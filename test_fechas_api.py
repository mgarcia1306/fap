import unittest
from datetime import datetime, timezone
from monitor_supabase import api_clock, api_local_to_utc, normalize

class CompraAgilRealTest(unittest.TestCase):
    def test_reloj_filtro_chile(self):
        self.assertEqual(api_clock(datetime(2026,11,15,4,31,tzinfo=timezone.utc)), "2026-11-15T01:31:00Z")

    def test_fecha_publicacion_chile(self):
        self.assertEqual(api_local_to_utc("2026-11-15 01:31"), "2026-11-15T04:31:00Z")
        self.assertEqual(api_local_to_utc("2026-11-15T01:35:00.503Z"), "2026-11-15T04:35:00Z")

    def test_payload_real(self):
        item={
            "codigo":"4030-244-COT26",
            "nombre":"ADQUISICION DE SERVICIO DE INTERNET SATELITAL STARLINK",
            "estado":{"id_estado":2,"codigo":"publicada","glosa":"Publicada"},
            "fechas":{"fecha_publicacion":"2026-11-15 01:31","fecha_cierre":"2026-11-16 18:00","fecha_ultimo_cambio":"2026-11-15T01:35:00.503Z"},
            "montos":{"moneda":"CLP","monto_disponible":1200000},
            "institucion":{"organismo_comprador":"ILUSTRE MUNICIPALIDAD DE CAMINA","region":1},
        }
        record, digest = normalize(item)
        self.assertEqual(record["monto"],1200000)
        self.assertEqual(record["region_codigo"],1)
        self.assertEqual(record["moneda"],"CLP")
        self.assertEqual(record["organismo"],"ILUSTRE MUNICIPALIDAD DE CAMINA")
        self.assertEqual(record["estado_nombre"],"Publicada")
        self.assertEqual(record["fecha_publicacion"],"2026-11-15T04:31:00Z")
        self.assertEqual(record["fecha_ultimo_cambio"],"2026-11-15T04:35:00Z")
        self.assertEqual(len(digest),64)

if __name__ == "__main__":
    unittest.main()
