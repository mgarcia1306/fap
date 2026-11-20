"""Diagnóstico de solo lectura de API Compra Ágil v2; sin acceso a Supabase.

Ejecutar con CHILECOMPRA_TICKET en GitHub Actions. No imprime ticket ni
datos personales de procesos. Una petición por prueba, sin reintentos.
"""
import json
import os
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

ROOT = "https://api2.mercadopublico.cl/v2/compra-agil"
CODE = "3891-290-COT26"
NOW = datetime.now(timezone.utc).replace(microsecond=0)

def iso(dt):
    return dt.isoformat().replace("+00:00", "Z")

def probe(name, params=None, code=None):
    url = ROOT + ("/" + code if code else "")
    if params:
        url += "?" + urlencode(params)
    request = Request(url, headers={"ticket": os.environ["CHILECOMPRA_TICKET"],
                                    "Accept": "application/json", "User-Agent": "FARO-diagnostico/1.0"})
    t0 = time.monotonic()
    try:
        with urlopen(request, timeout=23) as response:
            payload = json.loads(response.read())
            status = response.status
        result = payload.get("payload", {}) if isinstance(payload, dict) else {}
        items = result.get("items", []) if isinstance(result, dict) else []
        pagination = result.get("paginacion", {}) if isinstance(result, dict) else {}
        if not isinstance(items, list):
            items = []
        if not isinstance(pagination, dict):
            pagination = {}
        if code and isinstance(result, dict):
            items = [result] if result.get("codigo") else []
        seen = [p.get("codigo") for p in items if isinstance(p, dict)]
        dates = [
            {"codigo": p.get("codigo"), "publicacion": (p.get("fechas") or {}).get("fecha_publicacion"),
             "cambio": (p.get("fechas") or {}).get("fecha_ultimo_cambio")}
            for p in items[:2] if isinstance(p, dict)
        ]
        print(json.dumps({"prueba": name, "http": status,
            "success": payload.get("success") if isinstance(payload, dict) else None,
            "total_resultados": pagination.get("total_resultados"),
            "paginas": pagination.get("total_paginas"),
            "items_pagina": len(items), "codigo_objetivo_presente": CODE in seen,
            "muestra_fechas": dates, "segundos": round(time.monotonic()-t0, 1)}, ensure_ascii=False), flush=True)
    except HTTPError as e:
        print(json.dumps({"prueba": name, "http": e.code, "segundos": round(time.monotonic()-t0, 1)}), flush=True)
    except (URLError, TimeoutError, ValueError, json.JSONDecodeError, OSError) as e:
        print(json.dumps({"prueba": name, "error_tipo": type(e).__name__,
            "segundos": round(time.monotonic()-t0, 1)}), flush=True)

def main():
    print("Diagnóstico FARO solo lectura, hora UTC", iso(NOW), flush=True)
    # Presupuesto acotado: 6 consultas; no reintentos ni escritura.
    probe("detalle_codigo", code=CODE)
    probe("listar_por_id", {"id": CODE, "tamano_pagina": 10, "numero_pagina": 1})
    probe("publicaciones_3h", {"publicado_desde": iso(NOW-timedelta(hours=3)),
        "publicado_hasta": iso(NOW), "tamano_pagina": 10, "numero_pagina": 1})
    probe("publicaciones_24h", {"publicado_desde": iso(NOW-timedelta(hours=24)),
        "publicado_hasta": iso(NOW), "tamano_pagina": 10, "numero_pagina": 1})
    probe("cambios_3h", {"cambio_desde": iso(NOW-timedelta(hours=3)),
        "cambio_hasta": iso(NOW), "tamano_pagina": 10, "numero_pagina": 1})
    probe("ttl_4h", {"ttl_cambio_ms": 14400000, "tamano_pagina": 10, "numero_pagina": 1})
    chile_now = NOW.astimezone(ZoneInfo("America/Santiago"))
    chile_since = chile_now - timedelta(minutes=90)
    # Detecta si backend interpreta ISO con Z como hora local pese a declarar UTC.
    local_z = lambda dt: dt.strftime("%Y-%m-%dT%H:%M:%SZ")
    probe("publicaciones_90m_hora_chile_como_Z", {"publicado_desde": local_z(chile_since),
        "publicado_hasta": local_z(chile_now), "tamano_pagina": 10, "numero_pagina": 1})
    probe("cambios_90m_hora_chile_como_Z", {"cambio_desde": local_z(chile_since),
        "cambio_hasta": local_z(chile_now), "tamano_pagina": 10, "numero_pagina": 1})
    probe("publicaciones_90m_offset_chile", {"publicado_desde": chile_since.isoformat(),
        "publicado_hasta": chile_now.isoformat(), "tamano_pagina": 10, "numero_pagina": 1})
    probe("cambios_90m_offset_chile", {"cambio_desde": chile_since.isoformat(),
        "cambio_hasta": chile_now.isoformat(), "tamano_pagina": 10, "numero_pagina": 1})
    probe("codigo_en_publicaciones_hora_chile", {"id": CODE,
        "publicado_desde": local_z(chile_since), "publicado_hasta": local_z(chile_now),
        "tamano_pagina": 10, "numero_pagina": 1})
    probe("codigo_en_publicaciones_utc", {"id": CODE,
        "publicado_desde": iso(NOW-timedelta(minutes=90)), "publicado_hasta": iso(NOW),
        "tamano_pagina": 10, "numero_pagina": 1})
    probe("codigo_en_cambios_hora_chile", {"id": CODE,
        "cambio_desde": local_z(chile_since), "cambio_hasta": local_z(chile_now),
        "tamano_pagina": 10, "numero_pagina": 1})
    probe("publicaciones_90m_chile_pagina50", {"publicado_desde": local_z(chile_since),
        "publicado_hasta": local_z(chile_now), "tamano_pagina": 50, "numero_pagina": 1})
    probe("cambios_90m_chile_pagina50", {"cambio_desde": local_z(chile_since),
        "cambio_hasta": local_z(chile_now), "tamano_pagina": 50, "numero_pagina": 1})
    print("Fin diagnóstico, sin escrituras.", flush=True)

if __name__ == "__main__":
    main()
