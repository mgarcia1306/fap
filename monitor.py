
import json
import os
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


API_URL = "https://api2.mercadopublico.cl/v2/compra-agil"
STATE_PATH = Path(__file__).with_name("state.json")

CHUNK_SIZE = timedelta(hours=1)
OVERLAP = timedelta(minutes=20)

MAX_CHUNKS = 4
MAX_PAGES = 30
MAX_ATTEMPTS = 3


def iso(moment):
    return (
        moment.astimezone(timezone.utc)
        .isoformat(timespec="seconds")
        .replace("+00:00", "Z")
    )


def parse_iso(value):
    return datetime.fromisoformat(
        value.replace("Z", "+00:00")
    ).astimezone(timezone.utc)


def load_state():
    if not STATE_PATH.exists():
        return {
            "last_success": None,
            "items": {}
        }

    with STATE_PATH.open("r", encoding="utf-8") as file:
        state = json.load(file)

    if not isinstance(state.get("items"), dict):
        raise ValueError("Historial inválido")

    return state


def save_state(state):
    temporary = STATE_PATH.with_suffix(".json.tmp")

    with temporary.open("w", encoding="utf-8") as file:
        json.dump(
            state,
            file,
            ensure_ascii=False,
            indent=2
        )

    temporary.replace(STATE_PATH)


def request_page(ticket, params):
    url = API_URL + "?" + urlencode(params)

    request = Request(
        url,
        headers={
            "ticket": ticket,
            "Accept": "application/json"
        }
    )

    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            with urlopen(request, timeout=35) as response:
                return json.load(response)

        except HTTPError as error:
            if error.code in (401, 403, 429):
                raise RuntimeError(
                    f"Error HTTP {error.code}. "
                    "Se detiene la sincronización."
                ) from error

            if error.code not in (500, 502, 503, 504):
                raise

            print(
                f"Error HTTP {error.code}. "
                f"Intento {attempt}/{MAX_ATTEMPTS}",
                flush=True
            )

        except (URLError, TimeoutError) as error:
            print(
                f"Error de conexión: {error}. "
                f"Intento {attempt}/{MAX_ATTEMPTS}",
                flush=True
            )

        if attempt < MAX_ATTEMPTS:
            espera = 5 * (2 ** (attempt - 1))
            print(f"Reintentando en {espera} segundos...")
            time.sleep(espera)

    raise RuntimeError(
        "La API no respondió después de varios intentos."
    )


def fetch_changes(ticket, since, until):
    entries = []

    params = {
        "cambio_desde": iso(since),
        "cambio_hasta": iso(until),
        "tamano_pagina": 50,
        "ordenar_por": "FechaUltimaModificacion"
    }

    for page in range(1, MAX_PAGES + 1):
        params["numero_pagina"] = page

        body = request_page(ticket, params)

        if body.get("success") != "OK":
            raise RuntimeError(
                f"Respuesta inesperada de la API: "
                f"{body.get('errors')}"
            )

        payload = body.get("payload")

        if not isinstance(payload, dict):
            raise RuntimeError("Payload inválido")

        items = payload.get("items")
        pagination = payload.get("paginacion")

        if not isinstance(items, list):
            raise RuntimeError("Lista de resultados inválida")

        if not isinstance(pagination, dict):
            raise RuntimeError("Paginación inválida")

        total_pages = int(pagination["total_paginas"])

        if total_pages > MAX_PAGES:
            raise RuntimeError(
                f"Se necesitan {total_pages} páginas. "
                "Se supera el límite de seguridad."
            )

        entries.extend(items)

        if page >= total_pages:
            return entries, page

    raise RuntimeError("Límite de páginas alcanzado")


def apply_changes(state, entries, until):
    new_count = 0
    changed_count = 0
    repeated_count = 0

    history = state["items"]

    for item in entries:
        code = item["codigo"]

        current = {
            "changed_at": item["fechas"]["fecha_ultimo_cambio"],
            "status": item["estado"]["codigo"]
        }

        previous = history.get(code)

        if previous is None:
            new_count += 1
            print(f"NUEVA: {code}")

        elif previous != current:
            changed_count += 1
            print(f"MODIFICADA: {code}")

        else:
            repeated_count += 1

        history[code] = current

    # Conservamos únicamente registros recientes.
    cutoff = until - timedelta(days=7)

    state["items"] = {
        code: value
        for code, value in history.items()
        if parse_iso(value["changed_at"]) >= cutoff
    }

    state["last_success"] = iso(until)

    return new_count, changed_count, repeated_count


def main():
    ticket = os.environ.get("CHILECOMPRA_TICKET")

    if not ticket:
        raise SystemExit(
            "Falta configurar CHILECOMPRA_TICKET"
        )

    state = load_state()
    now = datetime.now(timezone.utc)

    if state.get("last_success"):
        cursor = parse_iso(state["last_success"])
    else:
        cursor = now - timedelta(hours=1)

    print("FARO - Sincronización incremental", flush=True)
    print(f"Última sincronización: {iso(cursor)}")
    print(f"Hora actual: {iso(now)}")

    processed = 0

    while cursor < now and processed < MAX_CHUNKS:
        since = cursor - OVERLAP
        until = min(cursor + CHUNK_SIZE, now)

        print(
            f"\nConsultando: {iso(since)} → {iso(until)}",
            flush=True
        )

        entries, pages = fetch_changes(
            ticket,
            since,
            until
        )

        new, changed, repeated = apply_changes(
            state,
            entries,
            until
        )

        # Guardamos solo después de completar
        # correctamente todas las páginas del tramo.
        save_state(state)

        print(
            f"OK: páginas={pages}; "
            f"registros={len(entries)}; "
            f"nuevas={new}; "
            f"modificadas={changed}; "
            f"repetidas={repeated}",
            flush=True
        )

        cursor = until
        processed += 1

    if cursor < now:
        print(
            "\nQuedan intervalos pendientes. "
            "Se recuperarán en próximas ejecuciones."
        )
    else:
        print("\nSincronización al día.")

    print(f"Última sincronización guardada: {iso(cursor)}")


if __name__ == "__main__":
    main()
