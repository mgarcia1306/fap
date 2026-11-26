"""Pruebas sin red del diagnóstico AG y del mapeo explícito a COT."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch
import revisar_anexos_oc as m

class TestAnexosOC(unittest.TestCase):
    def test_sin_red_pendiente(self):
        with tempfile.TemporaryDirectory() as tmp:
            session = Mock()
            result = m.revisar(session, list(m.PENDIENTES), {}, Path(tmp))
            session.get.assert_not_called()
            self.assertEqual(len(result["resultados"]), 3)
            self.assertTrue(all(r["estado"] == "pendiente_consulta" for r in result["resultados"]))

    def test_ag_no_se_descarga_sin_mapeo(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Mock()
            with patch.object(m.base, "listar", return_value=[{"id":"0","nombreArchivo":"prueba.pdf"}]) as listar, patch.object(m.base,"descargar_uno") as bajar:
                r = m.revisar(s, ["3143-144-AG26"], {}, Path(tmp), consultar=True, descargar=True)
                self.assertEqual(r["resultados"][0]["estado"],"listado_ag_sin_vinculo_cot_verificado")
                listar.assert_called_once_with(s,"3143-144-AG26")
                bajar.assert_not_called()

    def test_solo_cot_mapeado_permite_descarga(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Mock()
            map = {"3143-144-AG26": {"codigo_cot":"3143-78-COT26","fuente_vinculo":"Documento hipotético de prueba"}}
            with patch.object(m.base,"listar", return_value=[{"id":"0","nombreArchivo":"a.pdf"}]) as listar, patch.object(m.base,"descargar_uno",return_value={"archivo":"a.pdf","bytes":5}) as bajar:
                r = m.revisar(s, ["3143-144-AG26"], map, Path(tmp), consultar=True, descargar=True)
                self.assertEqual(r["resultados"][0]["descargados"], 1)
                listar.assert_called_once_with(s,"3143-78-COT26")
                bajar.assert_called_once()

    def test_mapeo_necesita_fuente(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/"m.csv"
            p.write_text("codigo_oc,codigo_cot,fuente_vinculo\n3143-144-AG26,3143-78-COT26,\n",encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "fuente"):
                m.leer_mapeo(p)

    def test_errores_no_impiden_otros_codigos(self):
        with tempfile.TemporaryDirectory() as tmp:
            s=Mock()
            with patch.object(m.base,"listar",side_effect=[ValueError("sin adjuntos"),[{"nombreArchivo":"b.pdf"}]]) as listar:
                r=m.revisar(s, ["3143-144-AG26","1755-407-AG26"],{},Path(tmp),consultar=True)
                self.assertEqual(r["resultados"][0]["estado"],"listado_no_verificado")
                self.assertEqual(r["resultados"][1]["estado"],"listado_ag_sin_vinculo_cot_verificado")
                self.assertEqual(listar.call_count,2)

    def test_ag_no_comparte_codigo_con_cot(self):
        with self.assertRaisesRegex(ValueError, "OC inválida"):
            m.revisar(Mock(), ["3904-1092-COT26"], {}, Path("."))

if __name__=="__main__":
    unittest.main()
