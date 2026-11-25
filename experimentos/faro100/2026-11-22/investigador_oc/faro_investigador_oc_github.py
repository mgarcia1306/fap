#!/usr/bin/env python3
"""FARO · Investigación experimental de OC. Sin red salvo --ejecutar."""
import argparse
import csv
import json
import os
import re
import sys
import time
import unicodedata
from datetime import datetime, timezone
from pathlib import Path
from decimal import Decimal, InvalidOperation
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

API_URL = "https://api.mercadopublico.cl/servicios/v1/publico/ordenesdecompra.json"
CODE = re.compile(r"^\d{3,9}-\d{1,8}-(?:AG|SE|CM|CC|TD|OC)\d{2}$")
COLUMNS = ["codigo_oc","rut","nombre_oc","estado_oc","evidencia_estado",
           "nombre_proveedor","items_en_detalle","fecha_consulta_utc","item_n",
           "correlativo","codigo_categoria","categoria","codigo_producto",
           "especificacion_comprador","especificacion_proveedor","cantidad",
           "moneda","precio_neto","total","fuente",
           "precio_neto_original","total_original","cantidad_original",
           "cantidad_de_servicios_en_texto","calidad_monto",
           "interpretacion_monto","requiere_revision_monetaria",
           "monto_oc_total_original","monto_oc_total_neto_original"]


def normalize_rut(value):
    return re.sub("[^0-9kK]", "", str(value or "")).upper()


def read_queue(path):
    with path.open(encoding="utf-8-sig", newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        raise ValueError("Cola vacía")
    if not {"rut_exportado", "codigo_oc", "fuente"}.issubset(rows[0]):
        raise ValueError("La cola no tiene las columnas obligatorias")
    seen = set()
    for r in rows:
        r["codigo_oc"] = r["codigo_oc"].strip().upper()
        key = (normalize_rut(r["rut_exportado"]), r["codigo_oc"])
        if not CODE.fullmatch(key[1]) or not key[0] or key in seen:
            raise ValueError("Código o RUT inválido o duplicado en la cola")
        seen.add(key)
    return rows


def get_order(code, ticket):
    query = urlencode({"codigo": code, "ticket": ticket})
    request = Request(API_URL + "?" + query,
                      headers={"User-Agent": "FARO-Investigacion-OC/experimental"})
    for attempt in range(3):
        try:
            with urlopen(request, timeout=30) as response:
                body = json.load(response)
                if not isinstance(body, dict):
                    raise ValueError("La API no devolvió un objeto JSON")
                return body
        except HTTPError as exc:
            if exc.code in (401, 403):
                raise PermissionError("Ticket API rechazado (401/403)") from exc
            if exc.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(2 ** attempt)
    raise RuntimeError("No se obtuvo respuesta")


def entry_list(obj):
    listing = obj.get("Listado", [])
    if isinstance(listing, dict):
        listing = [listing]
    return [x for x in listing if isinstance(x, dict)] if isinstance(listing, list) else []


def item_list(oc):
    value = oc.get("Items") or {}
    listing = value.get("Listado", []) if isinstance(value, dict) else value
    if isinstance(listing, dict):
        listing = [listing]
    return [x for x in listing if isinstance(x, dict)] if isinstance(listing, list) else []


def evidence_status(raw):
    text = "".join(c for c in unicodedata.normalize("NFD", str(raw or "").lower())
                   if unicodedata.category(c) != "Mn")
    if any(x in text for x in ("cancelada", "no aceptada", "enviada a proveedor",
                                "enviada al proveedor", "rechazada", "anulada")):
        return "no_demuestra_entrega"
    if any(x in text for x in ("recepcion conforme", "recepcionada")):
        return "recepcion_conforme"
    if any(x in text for x in ("aceptada", "aceptado")):
        return "aceptada_no_entrega_verificada"
    return "estado_sin_acreditar"



def number(value):
    """Valida valores sin inferir la unidad comercial de PrecioNeto."""
    if value is None or str(value).strip() == "":
        return None
    try:
        n = Decimal(str(value))
        return n if n.is_finite() else None
    except (InvalidOperation, ValueError):
        return None


def service_quantity_hint(description):
    """Pista textual únicamente; no sustituye la cantidad oficial."""
    description = str(description or "").upper()
    matches = list(re.finditer(r"\b(\d{1,6})\s+(SERVICIOS?|ALMUERZOS?|COLACIONES?|PERSONAS?)\b", description))
    return matches[-1].group(0) if matches else ""


def monetary_quality(item):
    """Señala incertidumbre: NO se calculan totales ni ingresos."""
    quantity = number(item.get("Cantidad"))
    price = number(item.get("PrecioNeto"))
    total = number(item.get("Total"))
    if price is None and total is None:
        return "sin_montos", True
    if total == 0 and price is not None and price > 0:
        return "total_cero_con_precio_neto", True
    if total is None:
        return "total_ausente", True
    if total < 0 or (quantity is not None and quantity <= 0):
        return "valor_atipico", True
    return "valores_informados_sin_validar", True

def normalize_order(body, code, expected_rut):
    matches = [oc for oc in entry_list(body)
               if str(oc.get("Codigo", "")).upper() == code]
    if len(matches) != 1:
        raise ValueError("La API no entregó una única OC con el código solicitado")
    oc = matches[0]
    provider = oc.get("Proveedor") or {}
    if not isinstance(provider, dict):
        raise ValueError("Proveedor no es objeto")
    received_rut = provider.get("RutSucursal")
    if not received_rut:
        raise ValueError("La API no entregó RutSucursal; verificar esquema antes de usar")
    if normalize_rut(received_rut) != normalize_rut(expected_rut):
        raise ValueError("RUT de OC no coincide con el proveedor investigado")
    items = item_list(oc)
    status = str(oc.get("Estado", "") or oc.get("EstadoProveedor", "")).strip()
    meta = {
        "codigo_oc": code, "rut": expected_rut, "nombre_oc": oc.get("Nombre", ""),
        "estado_oc": status, "evidencia_estado": evidence_status(status),
        "nombre_proveedor": provider.get("Nombre", ""),
        "items_en_detalle": len(items),
        "fecha_consulta_utc": datetime.now(timezone.utc).isoformat()
    }
    rows = []
    for n, item in enumerate(items, 1):
        calidad, revisar = monetary_quality(item)
        qhint = service_quantity_hint(item.get("EspecificacionComprador", ""))
        rows.append({
            **meta, "item_n": n, "correlativo": item.get("Correlativo", ""),
            "codigo_categoria": item.get("CodigoCategoria", ""),
            "categoria": item.get("Categoria", ""),
            "codigo_producto": item.get("CodigoProducto", ""),
            "especificacion_comprador": item.get("EspecificacionComprador", ""),
            "especificacion_proveedor": item.get("EspecificacionProveedor", ""),
            "cantidad": item.get("Cantidad", ""), "moneda": item.get("Moneda", ""),
            "precio_neto": item.get("PrecioNeto", ""), "total": item.get("Total", ""),
            "fuente": API_URL + "?codigo=" + code,
            "precio_neto_original": json.dumps(item.get("PrecioNeto"), ensure_ascii=False),
            "total_original": json.dumps(item.get("Total"), ensure_ascii=False),
            "cantidad_original": json.dumps(item.get("Cantidad"), ensure_ascii=False),
            "cantidad_de_servicios_en_texto": qhint,
            "calidad_monto": calidad,
            "interpretacion_monto": "NO_INFERIR_INGRESOS: valores originales; revisar unidad, impuestos y estado",
            "requiere_revision_monetaria": revisar,
            "monto_oc_total_original": json.dumps(oc.get("Total"), ensure_ascii=False),
            "monto_oc_total_neto_original": json.dumps(oc.get("TotalNeto"), ensure_ascii=False),
        })
    return meta, rows


def save_csv(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def run(queue, output, ticket, network=False):
    output.mkdir(parents=True, exist_ok=True)
    states, historical = [], []
    for index, entry in enumerate(queue, 1):
        code, rut = entry["codigo_oc"], entry["rut_exportado"]
        cache = output / "json" / rut / (code + ".json")
        try:
            if cache.exists():
                body = json.loads(cache.read_text(encoding="utf-8"))
                source = "cache"
            elif network:
                body = get_order(code, ticket)
                source = "api"
            else:
                states.append({"codigo_oc": code, "rut": rut, "estado_proceso": "pendiente_sin_consultar",
                               "detalle": "", "items_en_detalle": "", "fuente": entry["fuente"]})
                continue
            meta, items = normalize_order(body, code, rut)
            if source == "api":
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(body, ensure_ascii=False), encoding="utf-8")
            historical.extend(items)
            states.append({"codigo_oc": code, "rut": rut, "estado_proceso": "ok_" + source,
                           "detalle": meta["evidencia_estado"],
                           "items_en_detalle": len(items), "fuente": entry["fuente"]})
        except PermissionError:
            states.append({"codigo_oc": code, "rut": rut, "estado_proceso": "error_ticket",
                           "detalle": "Ticket no autorizado", "items_en_detalle": "",
                           "fuente": entry["fuente"]})
            break
        except HTTPError as exc:
            states.append({"codigo_oc": code, "rut": rut, "estado_proceso": "error_http",
                           "detalle": "HTTP " + str(exc.code), "items_en_detalle": "",
                           "fuente": entry["fuente"]})
        except Exception as exc:
            # Nunca escribir URL de error: contiene ticket en query string.
            safe = type(exc).__name__
            if isinstance(exc, ValueError):
                safe += ": " + str(exc).split("?")[0][:100]
            states.append({"codigo_oc": code, "rut": rut, "estado_proceso": "error",
                           "detalle": safe, "items_en_detalle": "", "fuente": entry["fuente"]})
        print(f"[{index}/{len(queue)}] {code}: {states[-1]['estado_proceso']}", flush=True)
        if network:
            time.sleep(0.75)

    save_csv(output / "estado_cola.csv", states,
             ["codigo_oc", "rut", "estado_proceso", "detalle", "items_en_detalle", "fuente"])
    save_csv(output / "items_historicos.csv", historical, COLUMNS)
    result = {
        "oc_seleccionadas": len(queue),
        "oc_ok": sum(x["estado_proceso"].startswith("ok_") for x in states),
        "oc_error": sum(x["estado_proceso"].startswith("error") for x in states),
        "items_extraidos": len(historical),
        "modo": "consulta_api" if network else "solo_previsualizacion",
        "nota": "Historial no acredita capacidad comercial actual ni cobertura integral"
    }
    (output / "resumen.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cola", type=Path, required=True)
    parser.add_argument("--salida", type=Path, default=Path("salida_oc"))
    parser.add_argument("--limite", type=int, default=1)
    parser.add_argument("--desde", type=int, default=1, help="Índice 1-based: usar 2 para omitir la primera OC ya descargada")
    parser.add_argument("--ejecutar", action="store_true")
    args = parser.parse_args()
    if args.limite < 1 or args.limite > 49 or args.desde < 1 or args.desde + args.limite - 1 > 49:
        parser.error("El tramo --desde/--limite debe estar dentro de las 49 OC congeladas")
    ticket = os.environ.get("MERCADOPUBLICO_TICKET", "").strip()
    if args.ejecutar and not ticket:
        parser.error("Falta variable MERCADOPUBLICO_TICKET")
    queue = read_queue(args.cola)[args.desde - 1:args.desde - 1 + args.limite]
    result = run(queue, args.salida, ticket, args.ejecutar)
    print(json.dumps(result, ensure_ascii=False))
    return 1 if args.ejecutar and result["oc_ok"] != len(queue) else 0


if __name__ == "__main__":
    sys.exit(main())
