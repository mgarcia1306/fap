"""Pruebas sintéticas del diseño FARO v2. Ejecutar: python -m unittest -v test_clasificador_v2.py"""
import unittest

from clasificador_v2 import ElementoObligatorio as E, SolicitudEvaluacion as S, evaluar


def item(i, estado="directa", motivo=""):
    return E(f"item-{i}", f"Elemento {i}", estado, "ficha_demo", motivo)


def solicitud(elementos=None, requisitos=(), afinidad="directa", **kwargs):
    return S(
        codigo="PRUEBA-COT26",
        afinidad=afinidad,
        elementos=tuple(elementos if elementos is not None else (item(1),)),
        requisitos=tuple(requisitos),
        detalle_completo=kwargs.pop("detalle_completo", True),
        anexos_necesarios_revisados=kwargs.pop("anexos_necesarios_revisados", True),
        **kwargs,
    )


class TestFaroV2(unittest.TestCase):
    def test_01_nueve_de_diez_y_uno_excluido(self):
        data = [item(i) for i in range(1, 10)] + [item(10, "no_cubierta", "Exclusión expresa")]
        r = evaluar(solicitud(data))
        self.assertEqual((r["cobertura_integral"], r["decision"]),
                         ("imposible", "descartar_no_cotizable"))
        self.assertEqual(len(r["items_bloqueantes"]), 1)

    def test_02_nueve_y_ultimo_encargo_no_confirmado(self):
        data = [item(i) for i in range(1, 10)] + [
            item(10, "por_encargo_por_verificar", "Proveedor todavía no confirma")
        ]
        r = evaluar(solicitud(data))
        self.assertEqual((r["cobertura_integral"], r["decision"]),
                         ("posible_por_verificar", "consultar_cliente"))
        self.assertEqual(len(r["items_a_confirmar"]), 1)

    def test_03_requisito_logistico_incompatible(self):
        r = evaluar(solicitud(
            [item(i) for i in range(1, 11)],
            requisitos=[E("logistica", "Despacho región solicitada", "no_cubierta",
                         "perfil_cliente", "Sin despacho a esa región")],
        ))
        self.assertEqual(r["decision"], "descartar_no_cotizable")

    def test_04_instalacion_no_es_venta_tuberias(self):
        r = evaluar(solicitud([
            E("tubos", "Material PPR", "directa", "perfil_cliente"),
            E("instalar", "Instalar y habilitar red", "no_cubierta",
              "perfil_cliente", "Solo comercializa materiales"),
        ]))
        self.assertEqual(r["cobertura_integral"], "imposible")

    def test_05_catering_excluido(self):
        r = evaluar(solicitud([
            item("alimentos"),
            E("catering", "Preparar y servir", "no_cubierta",
              "perfil_alimentos_v1", "Excluye servicios de catering"),
        ]))
        self.assertEqual(r["decision"], "descartar_no_cotizable")

    def test_06_farmacos_excluidos(self):
        r = evaluar(solicitud([
            item("insumos"),
            E("anestesico", "Anestésico farmacológico", "no_cubierta",
              "perfil_salud_v1", "Excluye medicamentos"),
        ]))
        self.assertEqual(r["cobertura_integral"], "imposible")

    def test_07_merchandising_extra_textil_desconocido(self):
        r = evaluar(solicitud([
            item("bolsas_textiles"),
            E("no_textil", "Producto promocional no textil", "desconocida",
              "perfil_textil_v1"),
        ]))
        self.assertEqual((r["cobertura_integral"], r["decision"]),
                         ("desconocida", "pendiente_informacion"))

    def test_08_anexo_no_revisado(self):
        r = evaluar(solicitud([item(1)], anexos_necesarios_revisados=False))
        self.assertEqual(r["cobertura_integral"], "desconocida")

    def test_09_conflicto_unspsc_no_invalida_texto(self):
        r = evaluar(solicitud(
            [item(1)], conflicto_unspsc=True,
            evidencia_afinidad="El texto indica suministro compatible",
        ))
        self.assertEqual(r["decision"], "recomendable")
        self.assertTrue(r["requiere_revision"])

    def test_10_todologo_solo_encargo_confirmado(self):
        r = evaluar(solicitud([
            item(1),
            E("adicional", "Artículo conseguido por encargo",
              "por_encargo_confirmada", "confirmacion_cliente",
              "Cliente confirma cantidad, plazo y artículo"),
        ], afinidad="adyacente"))
        self.assertEqual((r["cobertura_integral"], r["decision"]),
                         ("confirmada", "recomendable"))

    def test_11_generalista_sin_confirmar_no_automatico(self):
        r = evaluar(solicitud([
            item(1),
            E("adicional", "Artículo potencial", "desconocida", "perfil_cliente"),
        ], afinidad="adyacente"))
        self.assertEqual(r["decision"], "pendiente_informacion")

    def test_12_items_incompletos_no_confirmar(self):
        r = evaluar(solicitud([item(1)], detalle_completo=False))
        self.assertEqual(r["decision"], "pendiente_informacion")

    def test_13_sin_items_no_confirmar(self):
        r = evaluar(solicitud([]))
        self.assertEqual(r["decision"], "pendiente_informacion")

    def test_14_dudoso_no_supera_desconocido(self):
        r = evaluar(solicitud([
            item(1, "por_encargo_por_verificar", "Requiere consulta"),
            item(2, "desconocida"),
        ]))
        self.assertEqual(r["cobertura_integral"], "desconocida")

    def test_15_barrera_tiene_prioridad_aun_sin_anexos(self):
        r = evaluar(solicitud(
            [item(1, "no_cubierta", "Excluido")],
            detalle_completo=False, anexos_necesarios_revisados=False,
        ))
        self.assertEqual(r["decision"], "descartar_no_cotizable")

    def test_16_no_relacionada_pero_cobertura_posible(self):
        r = evaluar(solicitud(afinidad="no_relacionada"))
        self.assertEqual(r["decision"], "no_priorizar")

    def test_17_trazabilidad_obligatoria(self):
        with self.assertRaises(ValueError):
            evaluar(solicitud([
                E("fuera", "Suministro excluido", "no_cubierta", "perfil_cliente")
            ]))

    def test_18_ids_duplicados_invalidos(self):
        with self.assertRaises(ValueError):
            evaluar(solicitud([item(1), item(1)]))


if __name__ == "__main__":
    unittest.main()
