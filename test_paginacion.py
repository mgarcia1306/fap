"""Pruebas sin red de la paginación adaptativa y sus garantías."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

from monitor_supabase import (
    fetch_changes, _fetch_pages, TooManyPagesError, MAX_PAGES,
    synchronize_window,
)

UTC = timezone.utc
START = datetime(2026, 11, 16, 9, 0, tzinfo=UTC)
END = START + timedelta(hours=1)


class PaginationTests(unittest.TestCase):
    def test_36_paginas_dispara_subdivision_y_preserva_ambas_mitades(self):
        calls = []
        boundary = {"codigo": "B", "fechas": {"fecha_ultimo_cambio": "2026-11-16T09:30:00Z"}}
        a = {"codigo": "A"}
        c = {"codigo": "C"}

        def pages(ticket, since, until):
            calls.append((since, until))
            if until - since > timedelta(minutes=40):
                raise TooManyPagesError("ChileCompra anuncia 36 páginas")
            return [a, boundary] if since == START else [boundary, c]

        with patch("monitor_supabase._fetch_pages", side_effect=pages):
            items = fetch_changes("ticket", START, END)
        self.assertEqual([v["codigo"] for v in items], ["A", "B", "C"])
        self.assertEqual(calls, [
            (START, END),
            (START, START + timedelta(minutes=30)),
            (START + timedelta(minutes=30), END),
        ])

    def test_paginas_completas_se_descargan_sin_subdivision(self):
        def response(url, headers):
            page = int(parse_qs(urlsplit(url).query)["numero_pagina"][0])
            return {"success": "OK", "payload": {
                "items": [{"codigo": str(page)}],
                "paginacion": {"total_paginas": 3},
            }}
        with patch("monitor_supabase.http_json", side_effect=response) as http:
            items = _fetch_pages("ticket", START, END)
        self.assertEqual([x["codigo"] for x in items], ["1", "2", "3"])
        self.assertEqual(http.call_count, 3)

    def test_limite_detectado_antes_de_pedir_pagina_31(self):
        def response(url, headers):
            return {"success": "OK", "payload": {
                "items": [{"codigo": "A"}],
                "paginacion": {"total_paginas": MAX_PAGES + 6},
            }}
        with patch("monitor_supabase.http_json", side_effect=response) as http:
            with self.assertRaises(TooManyPagesError):
                _fetch_pages("ticket", START, END)
        self.assertEqual(http.call_count, 1)

    def test_intervalo_irreducible_falla_sin_datos_parciales(self):
        with patch("monitor_supabase._fetch_pages",
                   side_effect=TooManyPagesError("36 páginas")):
            with self.assertRaisesRegex(RuntimeError, "no se avanza cursor"):
                fetch_changes("ticket", START, START + timedelta(minutes=2))

    def test_error_api_real_no_se_oculta_al_subdividir(self):
        with patch("monitor_supabase._fetch_pages", side_effect=RuntimeError("HTTP 504")) as pages:
            with self.assertRaisesRegex(RuntimeError, "HTTP 504"):
                fetch_changes("ticket", START, END)
        pages.assert_called_once()

    def test_error_en_segunda_mitad_no_guarda_cursor(self):
        class DB:
            def __init__(self):
                self.saved = False
            def save_cursor(self, *args, **kwargs):
                self.saved = True
        db = DB()
        def pages(ticket, since, until):
            if until - since > timedelta(minutes=40):
                raise TooManyPagesError("36")
            if since == START:
                return []
            raise RuntimeError("API falló en segunda mitad")
        with patch("monitor_supabase._fetch_pages", side_effect=pages):
            with self.assertRaisesRegex(RuntimeError, "segunda mitad"):
                synchronize_window(db, "ticket", START, END)
        self.assertFalse(db.saved)


if __name__ == "__main__":
    unittest.main()
