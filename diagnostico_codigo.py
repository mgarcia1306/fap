"""Diagnóstico de lectura: Compra Ágil 4030-244-COT26 (sin Supabase)."""
import json
import os
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

URL = "https://api2.mercadopublico.cl/v2/compra-agil"
TARGET = "4030-244-COT26"
ticket = os.environ["CHILECOMPRA_TICKET"]
scenarios = [
    ("cambio_00_02_utc", {"cambio_desde": "2026-11-15T00:00:00Z", "cambio_hasta": "2026-11-15T02:00:00Z"}),
]

for label, filters in scenarios:
    print(f"=== {label} ===", flush=True)
    found = False
    for page in range(1, 31):
        params = {**filters, "tamano_pagina": 50, "numero_pagina": page}
        url = URL + "?" + urlencode(params)
        req = Request(url, headers={"ticket": ticket, "Accept": "application/json"})
        try:
            with urlopen(req, timeout=40) as res:
                body = json.load(res)
        except (HTTPError, URLError, TimeoutError) as exc:
            print(f"Consulta fallida en pagina {page}: {type(exc).__name__}; HTTP {getattr(exc, 'code', '?')}", flush=True)
            raise
        payload = body.get("payload") or {}
        items = payload.get("items") or []
        paging = payload.get("paginacion") or {}
        total_pages = paging.get("total_paginas", 1)
        print(f"pagina={page} items={len(items)} total_paginas={total_pages} status={body.get('success')}", flush=True)
        if page == 1 and items:
            sample = items[0]
            print("muestra:", sample.get("codigo"), "fechas:", json.dumps(sample.get("fechas"), ensure_ascii=False), flush=True)
        for item in items:
            if item.get("codigo") == TARGET:
                found = True
                print("ENCONTRADA:", json.dumps(item, ensure_ascii=False, default=str)[:5000], flush=True)
        if page >= int(total_pages) or not items:
            break
    print(f"RESULTADO {label}: {'ENCONTRADA' if found else 'NO ENCONTRADA EN PAGINAS CONSULTADAS'}", flush=True)
