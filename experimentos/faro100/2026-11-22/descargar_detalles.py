"""FARO-100: descarga aislada de detalles Compra Ágil v2.

Lee el CSV congelado de 100 oportunidades. Solo hace GET a ChileCompra.
NO importa Store, NO escribe en Supabase, NO modifica monitor, cursor ni state.json.
El ticket se lee de CHILECOMPRA_TICKET y nunca se registra en logs.
"""
from __future__ import annotations

import argparse
import csv
import json
import os
import random
import re
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

HERE = Path(__file__).resolve().parent
MANIFEST = HERE / "muestra_faro100.csv"
API_BASE = "https://api2.mercadopublico.cl/v2/compra-agil"
CODE_PATTERN = re.compile(r"^[0-9]+-[0-9]+-COT[0-9]{2}$", re.IGNORECASE)
RETRY_HTTP = {429, 500, 502, 503, 504, 522}
MAX_ATTEMPTS = 4


def read_manifest(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        rows = list(csv.DictReader(stream))
    if len(rows) != 100:
        raise ValueError(f"Se esperaban 100 compras congeladas, recibidas: {len(rows)}")
    codes = [row.get("codigo", "").strip() for row in rows]
    if len(set(codes)) != 100 or not all(CODE_PATTERN.fullmatch(c) for c in codes):
        raise ValueError("Códigos duplicados o inválidos en el manifiesto")
    if sorted(int(row["numero"]) for row in rows) != list(range(1, 101)):
        raise ValueError("Numeración de la muestra inconsistente")
    return rows


def get_detail(code: str, ticket: str) -> dict:
    if not CODE_PATTERN.fullmatch(code):
        raise ValueError("Código de Compra Ágil inválido")
    url = API_BASE + "/" + quote(code, safe="")
    for attempt in range(MAX_ATTEMPTS):
        request = Request(url, headers={"ticket": ticket, "Accept": "application/json"})
        try:
            with urlopen(request, timeout=35) as response:
                doc = json.load(response)
            if not isinstance(doc, dict) or doc.get("success") != "OK":
                raise ValueError("ChileCompra respondió sin success=OK")
            payload = doc.get("payload")
            if not isinstance(payload, dict):
                raise ValueError("Detalle sin objeto payload")
            # La API puede ampliar el esquema. Guardamos payload íntegro.
            # Verificamos código cuando lo informa el detalle.
            found = payload.get("codigo")
            if found is not None and str(found).strip().upper() != code.upper():
                raise ValueError(f"El detalle no corresponde al código solicitado: {code}")
            return doc
        except HTTPError as exc:
            if exc.code not in RETRY_HTTP or attempt == MAX_ATTEMPTS - 1:
                raise RuntimeError(f"HTTP {exc.code} consultando {code}") from exc
            retry = exc.headers.get("Retry-After", "")
            delay = int(retry) if retry.isdigit() else 2 ** attempt * 3
        except (URLError, TimeoutError) as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise RuntimeError(f"Sin conexión consultando {code}") from exc
            delay = 2 ** attempt * 3
        time.sleep(min(delay, 60) + random.random())
    raise RuntimeError(f"No fue posible recuperar {code}")


def valid_cached(path: Path, code: str) -> bool:
    try:
        with path.open("r", encoding="utf-8") as stream:
            data = json.load(stream)
        return (
            isinstance(data, dict)
            and data.get("codigo_solicitado") == code
            and isinstance(data.get("respuesta"), dict)
            and data["respuesta"].get("success") == "OK"
            and isinstance(data["respuesta"].get("payload"), dict)
        )
    except (OSError, ValueError, TypeError):
        return False


def atomic_json(path: Path, data: dict) -> None:
    temp = path.with_name(path.name + ".tmp")
    try:
        with temp.open("w", encoding="utf-8") as stream:
            json.dump(data, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()


def collect(rows: list[dict[str, str]], output: Path, ticket: str,
            limit: int = 100, dry_run: bool = False, pause: float = 0.5) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("El límite debe estar entre 1 y 100")
    if pause < 0:
        raise ValueError("La pausa no puede ser negativa")
    selected = rows[:limit]
    if not dry_run and not ticket:
        raise ValueError("Falta CHILECOMPRA_TICKET")
    if not dry_run:
        output.mkdir(parents=True, exist_ok=True)
    stats = {"seleccionadas": len(selected), "descargadas": 0, "en_cache": 0,
             "fallidas": 0, "modo": "simulacion" if dry_run else "descarga"}
    errors = []
    for index, row in enumerate(selected, 1):
        code = row["codigo"].strip()
        path = output / (code + ".json")
        if dry_run:
            print(f"[{index}/{len(selected)}] SIMULACIÓN {code}")
            continue
        if valid_cached(path, code):
            stats["en_cache"] += 1
            print(f"[{index}/{len(selected)}] EN CACHÉ {code}", flush=True)
            continue
        try:
            doc = get_detail(code, ticket)
            atomic_json(path, {"codigo_solicitado": code,
                               "recuperado_utc": datetime.now(timezone.utc).isoformat(),
                               "respuesta": doc})
            stats["descargadas"] += 1
            print(f"[{index}/{len(selected)}] OK {code}", flush=True)
        except (RuntimeError, ValueError, OSError) as exc:
            stats["fallidas"] += 1
            errors.append({"codigo": code, "error": str(exc)})
            print(f"[{index}/{len(selected)}] ERROR {code}: {exc}", flush=True)
        if index < len(selected) and pause:
            time.sleep(pause)
    if not dry_run:
        atomic_json(output / "resultado_descarga.json",
                    {"estadisticas": stats, "errores": errors,
                     "fecha_utc": datetime.now(timezone.utc).isoformat()})
    return stats


def main() -> int:
    parser = argparse.ArgumentParser(description="FARO-100: descargar detalles de solo lectura")
    parser.add_argument("--manifest", type=Path, default=MANIFEST)
    parser.add_argument("--output", type=Path, default=HERE / "salida_detalles")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--pause", type=float, default=0.5)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rows = read_manifest(args.manifest)
    result = collect(rows, args.output, os.environ.get("CHILECOMPRA_TICKET", ""),
                     limit=args.limit, dry_run=args.dry_run, pause=args.pause)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["fallidas"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
