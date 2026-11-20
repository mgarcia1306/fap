"""FARO: sincroniza publicaciones y cambios de Compra Ágil v2 hacia Supabase.
Solo usa librería estándar. No envía correos ni modifica state.json.
"""
import argparse
import hashlib
import json
import os
import random
import time
from datetime import datetime, timedelta, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

API_URL = "https://api2.mercadopublico.cl/v2/compra-agil"
SOURCE = "compra_agil_v2"
RECENT_CURSOR = "compra_agil_v2_reciente"
RECENT_LOOKBACK = timedelta(minutes=90)
OVERLAP = timedelta(minutes=20)
WINDOW = timedelta(hours=1)
MAX_PAGES = 30
MIN_SPLIT_WINDOW = timedelta(minutes=2)
MAX_SPLIT_DEPTH = 7
MAX_ATTEMPTS = 4
MAX_CHUNKS_PER_RUN = 4
MAX_RUNTIME_SECONDS = 8 * 60
MIN_REMAINING_SECONDS = 60
CHILE_TZ = ZoneInfo("America/Santiago")


def horario_operativo(moment):
    """08:00–00:00 todos los días; 00:00–02:00 si el día anterior fue hábil.

    Por ejemplo, sábado 01:00 sigue siendo la ventana del viernes.
    No supone que el domingo carezca de publicaciones.
    """
    local = moment.astimezone(CHILE_TZ)
    if local.hour >= 8:
        return True
    if local.hour < 2:
        ayer = (local.date() - timedelta(days=1)).weekday()
        return ayer < 5
    return False


def iso(dt):
    return dt.astimezone(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def parse_dt(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)


def http_json(url, method="GET", headers=None, body=None):
    payload = None if body is None else json.dumps(body, ensure_ascii=False).encode("utf-8")
    request = Request(url, data=payload, headers=headers or {}, method=method)
    for attempt in range(MAX_ATTEMPTS):
        try:
            with urlopen(request, timeout=35) as response:
                raw = response.read()
                return json.loads(raw) if raw else None
        except HTTPError as exc:
            if exc.code not in (429, 500, 502, 503, 504) or attempt == MAX_ATTEMPTS - 1:
                detail = exc.read(250).decode("utf-8", errors="replace")
                raise RuntimeError(f"HTTP {exc.code} en {url.split('?')[0]}: {detail}") from exc
            retry_after = exc.headers.get("Retry-After", "")
            delay = int(retry_after) if retry_after.isdigit() else 2 ** attempt * 5
        except (TimeoutError, URLError) as exc:
            if attempt == MAX_ATTEMPTS - 1:
                raise RuntimeError("Agotados reintentos de conexión") from exc
            delay = 2 ** attempt * 5
        time.sleep(min(delay, 90) + random.random())
    raise RuntimeError("Error de conexión inesperado")


class Store:
    def __init__(self):
        self.url = os.environ["SUPABASE_URL"].rstrip("/") + "/rest/v1"
        self.key = os.environ["SUPABASE_SECRET_KEY"]
        self.headers = {"apikey": self.key, "Content-Type": "application/json"}
        # Las claves nuevas sb_secret_ no son JWT y no deben usarse como Bearer.
        if not self.key.startswith("sb_secret_"):
            self.headers["Authorization"] = "Bearer " + self.key

    def request(self, table, method="GET", params=None, data=None, prefer=None):
        url = self.url + "/" + table
        if params:
            url += "?" + urlencode(params, safe="(),.*")
        headers = dict(self.headers)
        if prefer:
            headers["Prefer"] = prefer
        return http_json(url, method, headers, data)

    def cursor(self, fuente=SOURCE):
        rows = self.request("sincronizaciones", params={
            "select": "ultimo_cambio_procesado_at",
            "fuente": "eq." + fuente,
            "limit": 1,
        })
        return parse_dt(rows[0]["ultimo_cambio_procesado_at"]) if rows and rows[0]["ultimo_cambio_procesado_at"] else None

    def upsert(self, table, records, conflict):
        if not records:
            return []
        return self.request(table, "POST", {"on_conflict": conflict}, records,
                            "resolution=merge-duplicates,return=representation")

    def save_cursor(self, dt, count, fuente=SOURCE):
        self.upsert("sincronizaciones", [{
            "fuente": fuente, "ultimo_cambio_procesado_at": iso(dt),
            "ultima_ejecucion_at": iso(datetime.now(timezone.utc)),
            "ultimo_exito_at": iso(datetime.now(timezone.utc)),
            "estado": "correcto", "registros_procesados": count,
            "ultimo_error": None, "actualizado_at": iso(datetime.now(timezone.utc)),
        }], "fuente")


class TooManyPagesError(RuntimeError):
    """La API anuncia más páginas de las que aceptamos por solicitud."""


def _fetch_pages(ticket, since, until, filter_mode="cambios"):
    """Descarga todas las páginas de un subintervalo o falla sin datos parciales."""
    all_items = []
    if filter_mode == "cambios":
        period = {"cambio_desde": iso(since), "cambio_hasta": iso(until)}
        order = "FechaUltimaModificacion"
    elif filter_mode == "publicaciones":
        period = {"publicado_desde": iso(since), "publicado_hasta": iso(until)}
        order = "FechaPublicacion"
    else:
        raise ValueError(f"Filtro de consulta desconocido: {filter_mode}")
    params = {**period, "tamano_pagina": 50, "ordenar_por": order}
    for page in range(1, MAX_PAGES + 1):
        params["numero_pagina"] = page
        response = http_json(API_URL + "?" + urlencode(params),
                             headers={"ticket": ticket, "Accept": "application/json"})
        if not isinstance(response, dict) or response.get("success") != "OK":
            raise RuntimeError("Respuesta de ChileCompra inválida o sin éxito")
        payload = response.get("payload")
        if not isinstance(payload, dict):
            raise RuntimeError("Payload inválido")
        items, pagination = payload.get("items"), payload.get("paginacion")
        if not isinstance(items, list) or not isinstance(pagination, dict):
            raise RuntimeError("Estructura de paginación inesperada")
        pages = int(pagination["total_paginas"])
        if pages > MAX_PAGES:
            raise TooManyPagesError(f"ChileCompra anuncia {pages} páginas")
        all_items.extend(items)
        if page >= pages:
            return all_items
    raise RuntimeError("Paginación incompleta")


def fetch_changes(ticket, since, until, depth=0, filter_mode="cambios"):
    """Reduce intervalos saturados sin omitir páginas ni adelantar cursores.

    Ambos lados incluyen el punto medio para proteger eventos en el límite.
    Los resultados idénticos de esa frontera se deduplican por contenido.
    """
    try:
        if filter_mode == "cambios":
            return _fetch_pages(ticket, since, until)
        return _fetch_pages(ticket, since, until, filter_mode=filter_mode)
    except TooManyPagesError as exc:
        span = until - since
        if depth >= MAX_SPLIT_DEPTH or span <= MIN_SPLIT_WINDOW:
            raise RuntimeError(
                f"Intervalo {iso(since)} → {iso(until)} sigue saturado "
                f"tras {depth} divisiones; no se avanza cursor"
            ) from exc
        midpoint = since + span / 2
        # Los parámetros API se serializan en segundos: evitamos mitades
        # que colapsen en la misma marca temporal.
        midpoint = midpoint.replace(microsecond=0)
        if midpoint <= since or midpoint >= until:
            raise RuntimeError("Intervalo demasiado pequeño para subdividir") from exc
        print(f"Intervalo saturado ({exc}). Dividiendo "
              f"{iso(since)} → {iso(midpoint)} → {iso(until)}",
              flush=True)
        left = fetch_changes(ticket, since, midpoint, depth + 1, filter_mode)
        right = fetch_changes(ticket, midpoint, until, depth + 1, filter_mode)
        merged = []
        seen = set()
        for item in left + right:
            fingerprint = json.dumps(item, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":"))
            if fingerprint not in seen:
                seen.add(fingerprint)
                merged.append(item)
        return merged


def fetch_publications(ticket, since, until):
    """Consulta procesos por fecha de PUBLICACIÓN; no depende del último cambio."""
    return fetch_changes(ticket, since, until, filter_mode="publicaciones")


def as_text(value):
    if isinstance(value, dict):
        return str(value.get("nombre") or value.get("descripcion") or value.get("codigo") or "")
    return str(value) if value is not None else None


def normalize(item):
    code = item.get("codigo")
    if not isinstance(code, str) or not code.strip():
        raise ValueError("Compra Ágil sin código")
    dates = item.get("fechas") or {}
    if not isinstance(dates, dict) or not dates.get("fecha_ultimo_cambio"):
        raise ValueError(f"Compra Ágil {code} sin fecha_ultimo_cambio")
    state = item.get("estado") or {}
    if not isinstance(state, dict):
        raise ValueError(f"Compra Ágil {code} con estado inválido")
    buyer = item.get("organismo") or item.get("comprador")
    amount = item.get("monto_disponible")
    if isinstance(amount, dict):
        amount = amount.get("valor")
    record = {
        "fuente": SOURCE, "codigo": code.strip(),
        "titulo": item.get("nombre"), "descripcion": item.get("descripcion"),
        "organismo": as_text(buyer),
        "estado_codigo": as_text(state.get("codigo")),
        "estado_nombre": as_text(state.get("nombre") or state.get("descripcion")),
        "fecha_publicacion": dates.get("fecha_publicacion"),
        "fecha_cierre": dates.get("fecha_cierre"),
        "fecha_ultimo_cambio": dates["fecha_ultimo_cambio"],
        "datos_originales": item,
        "actualizada_at": iso(datetime.now(timezone.utc)),
    }
    if amount is not None and not isinstance(amount, (dict, list)):
        record["monto"] = amount
    signature = {key: record.get(key) for key in (
        "codigo", "titulo", "descripcion", "organismo", "estado_codigo",
        "fecha_publicacion", "fecha_cierre", "fecha_ultimo_cambio", "monto")}
    digest = hashlib.sha256(json.dumps(signature, sort_keys=True, ensure_ascii=False,
                                       default=str).encode("utf-8")).hexdigest()
    return record, digest


def synchronize_window(db, ticket, since, until):
    entries = fetch_changes(ticket, since, until)
    unique = {}
    for item in entries:
        record, digest = normalize(item)
        code = record["codigo"]
        previous = unique.get(code)
        if previous is None or parse_dt(record["fecha_ultimo_cambio"]) >= parse_dt(previous[0]["fecha_ultimo_cambio"]):
            unique[code] = (record, digest)
    for code, (record, digest) in unique.items():
        # Una única transacción PostgreSQL guarda la oportunidad y el historial.
        # Una versión antigua nunca reemplaza una modificación más reciente.
        result = db.request("rpc/faro_guardar_oportunidad", method="POST",
                            data={"p_registro": record, "p_huella": digest})
        if not isinstance(result, int) or result <= 0:
            raise RuntimeError(f"No se confirmó el guardado de {code}")
    db.save_cursor(until, len(unique))
    return len(entries), len(unique)


def recover_backlog(db, ticket, now, max_chunks=MAX_CHUNKS_PER_RUN,
                    deadline=None):
    """Procesa tramos consecutivos sin saltarse ni adelantar el cursor.

    El avance se confirma en Supabase dentro de synchronize_window, solo
    después de guardar todas las oportunidades y sus cambios.
    """
    cursor = db.cursor() or now - WINDOW
    if cursor > now:
        raise RuntimeError("Cursor de sincronización está en el futuro")
    processed = 0
    total_records = 0

    while cursor < now and processed < max_chunks:
        if deadline is not None and time.monotonic() + MIN_REMAINING_SECONDS >= deadline:
            print("Presupuesto de tiempo agotado: continuaremos en la siguiente ejecución.",
                  flush=True)
            break
        until = min(cursor + WINDOW, now)
        since = cursor - OVERLAP
        print(f"Tramo {processed + 1}/{max_chunks}: {iso(since)} → {iso(until)}",
              flush=True)
        total, unique = synchronize_window(db, ticket, since, until)
        cursor = until
        processed += 1
        total_records += total
        print(f"OK tramo: entradas={total}, códigos únicos={unique}, cursor={iso(cursor)}",
              flush=True)

    pending = max(timedelta(0), now - cursor)
    print(f"Resumen: tramos={processed}, registros={total_records}, "
          f"pendiente_horas={pending.total_seconds()/3600:.2f}",
          flush=True)
    if pending:
        print("Quedan intervalos pendientes; se recuperarán en próximas ejecuciones.",
              flush=True)
    else:
        print("Sincronización al día al inicio de esta ejecución.", flush=True)
    return processed, cursor


def monitor_actualidad(db, ticket, now):
    """Consulta tanto publicaciones recientes como modificaciones recientes.

    Ambos listados se unen por código, conservando la versión más actual.
    El cursor reciente solo avanza tras completar ambas consultas y la escritura.
    """
    desde = now - RECENT_LOOKBACK
    hasta = now
    print(f"FARO actualidad: {iso(desde)} → {iso(hasta)}", flush=True)
    # Consultas independientes: un proceso nuevo no siempre figura en
    # una búsqueda exclusivamente basada en fecha de última modificación.
    publicaciones = fetch_publications(ticket, desde, hasta)
    cambios = fetch_changes(ticket, desde, hasta)
    unique = {}
    for item in publicaciones + cambios:
        record, digest = normalize(item)
        code = record["codigo"]
        old = unique.get(code)
        if old is None or parse_dt(record["fecha_ultimo_cambio"]) >= parse_dt(old[0]["fecha_ultimo_cambio"]):
            unique[code] = (record, digest)
    for code, (record, digest) in unique.items():
        result = db.request("rpc/faro_guardar_oportunidad", method="POST",
                            data={"p_registro": record, "p_huella": digest})
        if not isinstance(result, int) or result <= 0:
            raise RuntimeError(f"Fallo persistencia de {code}")
    db.save_cursor(hasta, len(unique), fuente=RECENT_CURSOR)
    nuevas_hoy = sum(1 for record, _ in unique.values()
                    if record.get("fecha_publicacion")
                    and parse_dt(record["fecha_publicacion"]).astimezone(CHILE_TZ).date()
                    == now.astimezone(CHILE_TZ).date())
    print(f"Actualidad OK: publicaciones_en_ventana={len(publicaciones)}, "
          f"cambios_en_ventana={len(cambios)}, "
          f"oportunidades_distintas={len(unique)}, "
          f"publicadas_hoy_en_ventana={nuevas_hoy}", flush=True)
    return len(unique)


def main():
    parser = argparse.ArgumentParser(description="FARO Compra Ágil → Supabase")
    parser.add_argument("--modo", choices=("historico", "actualidad"),
                        default="historico")
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    if os.environ.get("GITHUB_EVENT_NAME") == "schedule" and not horario_operativo(now):
        print("Fuera de horario FARO (America/Santiago). Sin consultas.", flush=True)
        return
    ticket = os.environ["CHILECOMPRA_TICKET"]
    db = Store()
    if args.modo == "actualidad":
        monitor_actualidad(db, ticket, now)
    else:
        deadline = time.monotonic() + MAX_RUNTIME_SECONDS
        recover_backlog(db, ticket, now, deadline=deadline)


if __name__ == "__main__":
    main()
