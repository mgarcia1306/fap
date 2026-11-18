"""El monitor de actualidad no avanza el cursor del recuperador histórico."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from monitor_supabase import monitor_actualidad, RECENT_CURSOR

NOW = datetime(2026, 11, 18, 15, 30, tzinfo=timezone.utc)

def compra(codigo, cambio, publicada):
    return {"codigo": codigo, "nombre": "Prueba",
            "estado": {"codigo": 2, "nombre": "Publicada"},
            "fechas": {"fecha_ultimo_cambio": cambio, "fecha_publicacion": publicada,
                       "fecha_cierre": "2026-11-19T17:00:00Z"}}

class FakeDB:
    def __init__(self):
        self.ingest = []
        self.cursors = []
    def request(self, table, method="GET", data=None):
        assert table == "rpc/faro_guardar_oportunidad"
        self.ingest.append(data)
        return len(self.ingest)
    def save_cursor(self, dt, count, fuente=None):
        self.cursors.append((dt,count,fuente))

class ActualidadTest(unittest.TestCase):
    def test_ventana_actual_y_cursor_independiente(self):
        db=FakeDB()
        data=[compra("AAA-1-COT26","2026-11-18T14:30:00Z","2026-11-18T14:15:00Z")]
        with patch("monitor_supabase.fetch_changes",return_value=data) as fetch:
            n=monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(n,1)
        self.assertEqual(fetch.call_args.args[1],NOW-timedelta(minutes=90))
        self.assertEqual(fetch.call_args.args[2],NOW)
        self.assertEqual(db.cursors,[(NOW,1,RECENT_CURSOR)])

    def test_conserva_la_modificacion_mas_reciente(self):
        db=FakeDB()
        old=compra("AAA-1-COT26","2026-11-18T14:00:00Z","2026-11-18T12:00:00Z")
        new=compra("AAA-1-COT26","2026-11-18T15:00:00Z","2026-11-18T12:00:00Z")
        with patch("monitor_supabase.fetch_changes",return_value=[new,old]):
            n=monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(n,1)
        self.assertEqual(db.ingest[0]["p_registro"]["fecha_ultimo_cambio"],"2026-11-18T15:00:00Z")

    def test_error_no_mueve_cursor(self):
        db=FakeDB()
        with patch("monitor_supabase.fetch_changes",side_effect=RuntimeError("504")):
            with self.assertRaises(RuntimeError):
                monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(db.cursors,[])

if __name__=="__main__":
    unittest.main()
