"""Pruebas sintéticas + regresión basada en los campos CSV del primer artefacto real."""
import unittest
from unittest.mock import patch
from pathlib import Path
import csv
import tempfile

import faro_investigador_oc_github as investigator


def response():
    # Estructura mínima equivalente a la OC real 3334-547-AG26.
    return {"Listado": [{"Codigo": "3334-547-AG26", "Estado": "Aceptada",
        "Nombre": "OC servicios de alimentación",
        "Proveedor": {"RutSucursal": "15.326.117-2", "Nombre": "ROSA MARIELA RIOS VERA"},
        "Items": {"Listado": [
            {"Correlativo": 1, "CodigoProducto": "90101603",
             "EspecificacionComprador": "3 SERVICIOS DE COFFEE BREAK PARA 23 PERSONAS (69 SERVICIOS EN TOTAL)",
             "Cantidad": 1.0, "Moneda": "CLP", "PrecioNeto": 450000.0, "Total": 0.0},
            {"Correlativo": 2, "CodigoProducto": "90101603",
             "EspecificacionComprador": "4 ALMUERZOS PARA 23 PERSONAS (92 ALMUERZOS)",
             "Cantidad": 1.0, "Moneda": "CLP", "PrecioNeto": 779000.0, "Total": 0.0}
        ]}}]}


class OCTests(unittest.TestCase):
    def test_01_preserva_valores_originales_sin_suma(self):
        meta, items = investigator.normalize_order(response(), "3334-547-AG26", "15.326.117-2")
        self.assertEqual(meta["evidencia_estado"], "aceptada_no_entrega_verificada")
        self.assertEqual(len(items), 2)
        self.assertEqual([x["precio_neto"] for x in items], [450000.0, 779000.0])
        self.assertEqual([x["total"] for x in items], [0.0, 0.0])
        self.assertEqual(items[0]["cantidad"], 1.0)
        self.assertEqual(items[0]["cantidad_de_servicios_en_texto"], "69 SERVICIOS")
        self.assertEqual(items[1]["cantidad_de_servicios_en_texto"], "92 ALMUERZOS")
        self.assertTrue(all(x["calidad_monto"] == "total_cero_con_precio_neto" for x in items))
        self.assertTrue(all(x["requiere_revision_monetaria"] for x in items))
        self.assertEqual(items[0]["monto_oc_total_original"], "null")

    def test_02_rut_equivocado_bloquea(self):
        with self.assertRaisesRegex(ValueError, "RUT"):
            investigator.normalize_order(response(), "3334-547-AG26", "78.247.235-6")

    def test_03_orden_equivocada_bloquea(self):
        with self.assertRaisesRegex(ValueError, "única OC"):
            investigator.normalize_order(response(), "2940-190-AG26", "15.326.117-2")

    def test_04_monto_cero_sin_precio_no_suma(self):
        self.assertEqual(investigator.monetary_quality({"PrecioNeto": 0, "Total": 0})[0],
                         "valores_informados_sin_validar")
        self.assertEqual(investigator.monetary_quality({"PrecioNeto": 100, "Total": 0})[0],
                         "total_cero_con_precio_neto")
        self.assertEqual(investigator.monetary_quality({"PrecioNeto": None, "Total": None})[0],
                         "sin_montos")

    def test_05_primera_orden_omitida_en_tramo_restante(self):
        queue = [{"codigo_oc": "3334-547-AG26", "rut_exportado": "15.326.117-2", "fuente": "x"},
                 {"codigo_oc": "2940-190-AG26", "rut_exportado": "15.326.117-2", "fuente": "x"},
                 {"codigo_oc": "1114504-6-AG26", "rut_exportado": "78.247.235-6", "fuente": "y"}]
        selected = queue[1:1+2]
        self.assertEqual([x["codigo_oc"] for x in selected],
                         ["2940-190-AG26", "1114504-6-AG26"])
        with tempfile.TemporaryDirectory() as folder:
            with patch.object(investigator, "get_order", side_effect=AssertionError("No debe consultar API")):
                result = investigator.run(selected, Path(folder), ticket="", network=False)
                self.assertEqual(result["oc_seleccionadas"], 2)
                self.assertEqual(result["oc_ok"], 0)

    def test_06_csv_mantiene_campos_y_orden(self):
        _, items = investigator.normalize_order(response(), "3334-547-AG26", "15.326.117-2")
        with tempfile.TemporaryDirectory() as folder:
            target = Path(folder) / "items_historicos.csv"
            investigator.save_csv(target, items, investigator.COLUMNS)
            with target.open(encoding="utf-8-sig", newline="") as fh:
                rows = list(csv.DictReader(fh))
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["cantidad_original"], "1.0")
            self.assertEqual(rows[0]["precio_neto_original"], "450000.0")
            self.assertEqual(rows[0]["total_original"], "0.0")


if __name__ == "__main__":
    unittest.main()
