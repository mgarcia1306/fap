import unittest
from datetime import datetime, timezone

import monitor


NOW = datetime(2026, 11, 6, 14, 0, tzinfo=timezone.utc)


def entry(code, changed, status="publicada"):
    return {"codigo": code, "nombre": "Compra de prueba", "fechas": {"fecha_ultimo_cambio": changed},
            "estado": {"codigo": status}}


def page(items, pages):
    return {"success": "OK", "payload": {"items": items, "paginacion": {"total_paginas": pages}}}


class FakeSession:
    def __init__(self, responses):
        self.responses = iter(responses)
        self.calls = []

    def __call__(self, ticket, params):
        self.calls.append(params["numero_pagina"])
        return next(self.responses)


class MonitorTests(unittest.TestCase):
    def test_pages_and_state_changes(self):
        first = entry("A", "2026-11-06T13:50:00Z")
        second = entry("B", "2026-11-06T13:55:00Z")
        fake = FakeSession([page([first], 2), page([second], 2)])
        items, pages = monitor.fetch_changes("fake", NOW, NOW, fetch_page=fake)
        self.assertEqual((pages, fake.calls), (2, [1, 2]))
        self.assertEqual(len(items), 2)
        state, report = monitor.apply_changes({"items": {}}, items, NOW)
        self.assertEqual(report[:3], (2, 0, 0))
        again, report2 = monitor.apply_changes(state, [first, entry("B", "2026-11-06T13:59:00Z")], NOW)
        self.assertEqual(report2[:3], (0, 1, 1))
        self.assertEqual(len(again["items"]), 2)

    def test_refuses_overlong_pagination(self):
        fake = FakeSession([page([], 31)])
        with self.assertRaisesRegex(RuntimeError, "31 páginas"):
            monitor.fetch_changes("fake", NOW, NOW, fetch_page=fake)

    def test_expired_records_are_removed(self):
        old = entry("OLD", "2026-10-20T14:00:00Z")
        state, report = monitor.apply_changes({"items": {}}, [old], NOW)
        self.assertEqual(report[0], 1)
        self.assertNotIn("OLD", state["items"])


if __name__ == "__main__":
    unittest.main()
