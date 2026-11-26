"""Diagnóstico de anexos de OC AG y descarga segura SOLO con mapeo COT explícito.

Reutiliza descargar_adjuntos_faro100 (listar, descargar_uno, crear_sesion).
No equiparar un código AG (orden de compra) con COT (Compra Ágil).
El diagnóstico con AG es una prueba de compatibilidad del servicio, no
evidencia de relación contractual entre OC y sus adjuntos.
"""
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests
import descargar_adjuntos_faro100 as base

PENDIENTES = ("3143-144-AG26", "1057539-9739-AG26", "1755-407-AG26")
OC_RE = re.compile(r"^\d+-\d+-AG\d{2}$", re.I)
COT_RE = re.compile(r"^\d+-\d+-COT\d{2}$", re.I)


def leer_mapeo(path):
    """Archivo opcional: codigo_oc,codigo_cot,fuente_vinculo; no inventar relaciones."""
    if path is None:
        return {}
    result = {}
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if not {"codigo_oc", "codigo_cot", "fuente_vinculo"}.issubset(reader.fieldnames or []):
            raise ValueError("Mapeo debe incluir codigo_oc,codigo_cot,fuente_vinculo")
        for row in reader:
            oc = row["codigo_oc"].strip().upper()
            cot = row["codigo_cot"].strip().upper()
            source = row["fuente_vinculo"].strip()
            if not OC_RE.fullmatch(oc) or not COT_RE.fullmatch(cot) or not source:
                raise ValueError("Mapeo inválido; se exige fuente documental para cada relación")
            if oc in result and result[oc]["codigo_cot"] != cot:
                raise ValueError("OC asignada a dos compras COT distintas")
            result[oc] = {"codigo_cot": cot, "fuente_vinculo": source}
    return result


def revisar(sesion, codigos, mapeos, output, consultar=False, descargar=False):
    if descargar and not consultar:
        raise ValueError("--descargar requiere --consultar")
    output.mkdir(parents=True, exist_ok=True)
    registros = []
    for codigo in codigos:
        if not OC_RE.fullmatch(codigo):
            raise ValueError(f"OC inválida: {codigo}")
        mappeado = mapeos.get(codigo)
        cot = mappeado["codigo_cot"] if mappeado else ""
        resultado = {"codigo_oc": codigo, "codigo_cot": cot,
                     "fuente_vinculo": mappeado["fuente_vinculo"] if mappeado else "",
                     "estado": "pendiente_consulta" if not consultar else "sin_consultar",
                     "adjuntos_listados": 0, "descargados": 0, "errores": []}
        if not consultar:
            registros.append(resultado)
            continue
        codigo_busqueda = cot or codigo
        try:
            files = base.listar(sesion, codigo_busqueda)
            resultado["adjuntos_listados"] = len(files)
            if not cot:
                # Respuesta por AG no acredita identidad de la Compra Ágil.
                resultado["estado"] = "listado_ag_sin_vinculo_cot_verificado"
                resultado["nombres_listados"] = [str(f.get("nombreArchivo", ""))[:160] for f in files]
            elif not descargar:
                resultado["estado"] = "listado_cot_con_vinculo_documentado"
                resultado["nombres_listados"] = [str(f.get("nombreArchivo", ""))[:160] for f in files]
            else:
                destino = output / codigo / cot
                destino.mkdir(parents=True, exist_ok=True)
                correctos = []
                for item in files:
                    try:
                        correctos.append(base.descargar_uno(sesion, item, destino))
                    except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as exc:
                        resultado["errores"].append(type(exc).__name__)
                resultado["descargados"] = len(correctos)
                resultado["estado"] = "descarga_completa" if not resultado["errores"] else "descarga_parcial"
                resultado["archivos"] = correctos
        except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as exc:
            resultado["estado"] = "listado_no_verificado"
            resultado["errores"].append(type(exc).__name__)
        registros.append(resultado)
        print(f"{codigo}: {resultado['estado']} (COT={cot or 'no encontrado'})", flush=True)
    summary = {
        "consultado_utc": datetime.now(timezone.utc).isoformat(),
        "solo_diagnostico_ag_sin_descarga": not descargar,
        "nota": "AG es código de OC; no asumir relación con COT ni capacidad actual de proveedor",
        "resultados": registros
    }
    (output / "resultado_inspeccion.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--salida", type=Path, default=Path("salida_inspeccion_oc"))
    p.add_argument("--mapa", type=Path, help="CSV documentado codigo_oc,codigo_cot,fuente_vinculo")
    p.add_argument("--codigos", nargs="+", default=PENDIENTES, help="OC AG que se van a revisar; omite otras para evitar duplicar descargas")
    p.add_argument("--consultar", action="store_true", help="Realiza GET de listado, sin descargar por defecto")
    p.add_argument("--descargar", action="store_true", help="Descarga solo anexos con mapeo COT explícito")
    args = p.parse_args()
    mapeos = leer_mapeo(args.mapa)
    codigos = list(dict.fromkeys(x.strip().upper() for x in args.codigos))
    with base.crear_sesion() as sesion:
        summary = revisar(sesion, codigos, mapeos, args.salida,
                         consultar=args.consultar, descargar=args.descargar)
    print(json.dumps({r["codigo_oc"]: r["estado"] for r in summary["resultados"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
