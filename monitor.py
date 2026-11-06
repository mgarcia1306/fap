"""Prueba mínima de sincronización incremental de Compra Ágil v2.

No envía correos ni descarga detalles de compras. Requiere CHILECOMPRA_TICKET.
"""

import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api2.mercadopublico.cl/v2/compra-agil"
STATE_PATH = Path(__file__).with_name("state.json")
OVERLAP = timedelta(minutes=20)
FIRST_LOOKBACK = timedelta(hours=1)
PAGE_LIMIT = 30  # Límite deliberado de seguridad: 30 solicitudes por ejecución.


def iso(moment):
    return moment.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_iso(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_state():
    if not STATE_PATH.exists():
        return {"last_success": None, "items": {}}
    data = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    if not isinstance(data.get("items"), dict):
        raise ValueError("Historial inválido: falta items")
    return data


def request_page(ticket, params):
    url = API_URL + "?" + urlencode(params)
    request = Request(url, headers={"ticket": ticket, "Accept": "application/json"})
    try:
        with urlopen(request, timeout=35) as response:
            return json.load(response)
    except HTTPError as exc:
        if exc.code in (401, 403, 429):
            raise RuntimeError(f"API respondió HTTP {exc.code}; no se actualizará el historial") from None
        raise


def fetch_changes(ticket, since, until, fetch_page=None):
    get_page = fetch_page or request_page
    params = {
        "cambio_desde": iso(since),
        "cambio_hasta": iso(until),
        "tamano_pagina": 50,
        "ordenar_por": "FechaUltimaModificacion",
    }
    collected = []
    for page in range(1, PAGE_LIMIT + 1):
        body = get_page(ticket, {**params, "numero_pagina": page})
        if body.get("success") != "OK" or not isinstance(body.get("payload"), dict):
            raise RuntimeError("Respuesta no exitosa o estructura inesperada; no se actualizará el historial")
        payload = body["payload"]
        entries = payload.get("items")
        pagination = payload.get("paginacion")
        if not isinstance(entries, list) or not isinstance(pagination, dict):
            raise RuntimeError("Falta paginación o lista de resultados")
        total_pages = int(pagination["total_paginas"])
        if total_pages > PAGE_LIMIT:
            raise RuntimeError(f"La ventana requiere {total_pages} páginas (> {PAGE_LIMIT}); historial intacto")
        collected.extend(entries)
        if page >= total_pages:
            return collected, page
    raise RuntimeError("Se alcanzó el límite de páginas; historial intacto")


def apply_changes(state, entries, queried_until):
    current = dict(state["items"])
    new_count = changed_count = unchanged_count = 0
    samples = []
    for item in entries:
        code = item["codigo"]
        changed_at = item["fechas"]["fecha_ultimo_cambio"]
        status = item["estado"]["codigo"]
        new_value = {"changed_at": changed_at, "status": status}
        previous = current.get(code)
        if previous is None:
            new_count += 1
            samples.append(("NUEVA", code, item.get("nombre", "")))
        elif previous != new_value:
            changed_count += 1
            samples.append(("CAMBIO", code, item.get("nombre", "")))
        else:
            unchanged_count += 1
        current[code] = new_value

    # Historial acotado; conserva las compras vistas recientemente, sin guardar datos personales.
    cutoff = queried_until - timedelta(days=7)
    current = {code: value for code, value in current.items()
               if parse_iso(value["changed_at"]) >= cutoff}
    return {"last_success": iso(queried_until), "items": current}, (new_count, changed_count, unchanged_count, samples)


def main():
    ticket = os.environ.get("CHILECOMPRA_TICKET")
    if not ticket:
        raise SystemExit("Falta el secreto CHILECOMPRA_TICKET")
    state = load_state()
    now = datetime.now(timezone.utc)
    since = (parse_iso(state["last_success"]) - OVERLAP
             if state.get("last_success") else now - FIRST_LOOKBACK)
    print(f"Consulta de cambios: {iso(since)} a {iso(now)} (UTC)")
    entries, pages = fetch_changes(ticket, since, now)
    updated, (news, changes, unchanged, examples) = apply_changes(state, entries, now)

    # Escritura atómica tras completar TODAS las páginas.
    temp = STATE_PATH.with_suffix(".json.tmp")
    temp.write_text(json.dumps(updated, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(STATE_PATH)
    print(f"OK: páginas={pages}; registros={len(entries)}; nuevas={news}; modificadas={changes}; repetidas={unchanged}")
    for kind, code, name in examples[:10]:
        print(f"  {kind}: {code} · {name[:90]}")


if __name__ == "__main__":
    main()
