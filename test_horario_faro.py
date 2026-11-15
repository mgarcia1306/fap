"""Pruebas de fronteras del horario operativo FARO."""
import unittest
from datetime import datetime
from zoneinfo import ZoneInfo
from monitor_supabase import horario_operativo

TZ = ZoneInfo("America/Santiago")


def chile(year, month, day, hour, minute=0):
    return datetime(year, month, day, hour, minute, tzinfo=TZ)


class HorarioFaroTest(unittest.TestCase):
    def test_lunes_temprano_fuera(self):
        self.assertFalse(horario_operativo(chile(2026, 11, 16, 1, 59)))

    def test_lunes_ocho_dentro(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 16, 8, 0)))

    def test_martes_una_dentro(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 17, 1, 59)))

    def test_martes_dos_fuera(self):
        self.assertFalse(horario_operativo(chile(2026, 11, 17, 2, 0)))

    def test_viernes_medianoche(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 20, 23, 59)))

    def test_sabado_una_por_viernes(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 21, 1, 59)))

    def test_sabado_dos_fuera(self):
        self.assertFalse(horario_operativo(chile(2026, 11, 21, 2, 0)))

    def test_sabado_ocho_dentro(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 21, 8, 0)))

    def test_domingo_madrugada_fuera(self):
        self.assertFalse(horario_operativo(chile(2026, 11, 22, 1, 0)))

    def test_domingo_dia_dentro(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 22, 12, 0)))

    def test_domingo_fin(self):
        self.assertTrue(horario_operativo(chile(2026, 11, 22, 23, 59)))
        self.assertFalse(horario_operativo(chile(2026, 11, 23, 0, 0)))


if __name__ == "__main__":
    unittest.main()
