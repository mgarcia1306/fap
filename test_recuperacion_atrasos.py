"""Pruebas del avance por tramos sin acceder a servicios externos."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from monitor_supabase import recover_backlog, WINDOW, OVERLAP

UTC = timezone.utc
NOW = datetime(2026, 11, 16, 12, 0, tzinfo=UTC)


class FakeStore:
    def __init__(self, cursor):
        self._cursor = cursor

    def cursor(self):
        return self._cursor


class RecuperacionAtrasosTest(unittest.TestCase):
    def test_recupera_cuatro_horas_y_mantiene_solapamiento(self):
        db = FakeStore(NOW - timedelta(hours=10))
        called = []

        def fake_sync(store, ticket, since, until):
            called.append((since, until))
            db._cursor = until
            return 12, 10

        with patch("monitor_supabase.synchronize_window", side_effect=fake_sync):
            processed, cursor = recover_backlog(db, "ticket", NOW, max_chunks=4)
        self.assertEqual(processed, 4)
        self.assertEqual(cursor, NOW - timedelta(hours=6))
        self.assertEqual(len(called), 4)
        for i, (since, until) in enumerate(called):
            self.assertEqual(until - since, WINDOW + OVERLAP)
            if i:
                self.assertEqual(since, called[i-1][1] - OVERLAP)

    def test_corta_al_llegar_al_presente(self):
        db = FakeStore(NOW - timedelta(minutes=30))
        with patch("monitor_supabase.synchronize_window", return_value=(2, 2)) as sync:
            processed, cursor = recover_backlog(db, "ticket", NOW)
        self.assertEqual(processed, 1)
        self.assertEqual(cursor, NOW)
        sync.assert_called_once()

    def test_error_no_salta_el_intervalo(self):
        starting = NOW - timedelta(hours=5)
        db = FakeStore(starting)
        with patch("monitor_supabase.synchronize_window",
                   side_effect=RuntimeError("API caída")):
            with self.assertRaisesRegex(RuntimeError, "API caída"):
                recover_backlog(db, "ticket", NOW)
        self.assertEqual(db.cursor(), starting)

    def test_presupuesto_de_tiempo_evitar_iniciar_tramo(self):
        db = FakeStore(NOW - timedelta(hours=5))
        with patch("monitor_supabase.time.monotonic", return_value=1000.0):
            with patch("monitor_supabase.synchronize_window") as sync:
                processed, cursor = recover_backlog(db, "ticket", NOW,
                                                    deadline=1050.0)
        self.assertEqual(processed, 0)
        self.assertEqual(cursor, NOW - timedelta(hours=5))
        sync.assert_not_called()


if __name__ == "__main__":
    unittest.main()
