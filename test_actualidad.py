"""El monitor de actualidad no avanza el cursor del recuperador histórico."""
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import patch
from monitor_supabase import (monitor_actualidad, RECENT_CURSOR,
    api_wallclock_chile_as_utc, pertenece_piloto, PILOT_START, normalize)

NOW = datetime(2026, 11, 20, 22, 30, tzinfo=timezone.utc)

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
    def test_estado_glosa_api_real(self):
        item = compra("GLS-1-COT26", "2026-11-20T19:30:00Z",
                      "2026-11-20 19:00")
        item["estado"] = {"glosa": "Publicada", "codigo": "publicada", "id_estado": 2}
        record, digest = normalize(item)
        self.assertEqual(record["estado_nombre"], "Publicada")
        self.assertEqual(record["estado_codigo"], "publicada")
        self.assertEqual(record["datos_originales"]["estado"]["id_estado"], 2)
        self.assertEqual(len(digest), 64)

    def test_estado_nombre_compatibilidad(self):
        item = compra("LEG-1-COT26", "2026-11-20T19:30:00Z",
                      "2026-11-20 19:00")
        self.assertEqual(normalize(item)[0]["estado_nombre"], "Publicada")
        item["estado"] = {"codigo": 3, "descripcion": "Cerrada"}
        self.assertEqual(normalize(item)[0]["estado_nombre"], "Cerrada")

    def test_estado_glosa_prioridad(self):
        item = compra("PRI-1-COT26", "2026-11-20T19:30:00Z",
                      "2026-11-20 19:00")
        item["estado"] = {"codigo": "publicada", "glosa": "Publicada",
                          "nombre": "Valor anterior"}
        self.assertEqual(normalize(item)[0]["estado_nombre"], "Publicada")

    def test_conversion_reloj_chile_verano_y_invierno(self):
        verano = datetime(2026, 11, 20, 21, 30, tzinfo=timezone.utc)
        invierno = datetime(2026, 7, 20, 21, 30, tzinfo=timezone.utc)
        self.assertEqual(api_wallclock_chile_as_utc(verano).isoformat(),
                         "2026-11-20T18:30:00+00:00")
        self.assertEqual(api_wallclock_chile_as_utc(invierno).isoformat(),
                         "2026-07-20T17:30:00+00:00")

    def test_piloto_filtra_inicio_en_chile_y_sigue_indefinidamente(self):
        anterior = compra("ANT-1-COT26", "2026-11-20T19:00:00Z",
                          "2026-11-20 18:50")
        inicio = compra("NUE-1-COT26", "2026-11-20T19:00:00Z",
                        "2026-11-20 18:51")
        al_final = compra("FIN-1-COT26", "2026-12-20T00:00:00Z",
                          "2026-12-20 00:00")
        self.assertFalse(pertenece_piloto(anterior))
        self.assertTrue(pertenece_piloto(inicio))
        self.assertTrue(pertenece_piloto(al_final))

    def test_cambio_de_compra_anterior_no_se_ingresa(self):
        db = FakeDB()
        antigua = compra("ANT-1-COT26", "2026-11-20T19:30:00Z",
                         "2026-11-20 18:50")
        nueva = compra("NUE-1-COT26", "2026-11-20T19:30:00Z",
                       "2026-11-20 19:00")
        with patch("monitor_supabase.fetch_publications", return_value=[nueva]), \
             patch("monitor_supabase.fetch_changes", return_value=[antigua, nueva]):
            n = monitor_actualidad(db, "ticket", NOW)
        self.assertEqual(n, 1)
        self.assertEqual(len(db.ingest), 1)
        self.assertEqual(db.ingest[0]["p_registro"]["codigo"], "NUE-1-COT26")

    def test_antes_de_inicio_no_consulta(self):
        for momento in (PILOT_START.astimezone(timezone.utc)-timedelta(seconds=1),):
            db = FakeDB()
            with patch("monitor_supabase.fetch_publications") as pubs, \
                 patch("monitor_supabase.fetch_changes") as changes:
                self.assertEqual(monitor_actualidad(db,"ticket",momento), 0)
            pubs.assert_not_called()
            changes.assert_not_called()
            self.assertEqual(db.cursors, [])

    def test_ventana_actual_y_cursor_independiente(self):
        db=FakeDB()
        data=[compra("AAA-1-COT26","2026-11-20T19:20:00Z","2026-11-20T19:15:00Z")]
        with patch("monitor_supabase.fetch_publications",return_value=[]) as publications, \
             patch("monitor_supabase.fetch_changes",return_value=data) as fetch:
            n=monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(n,1)
        self.assertEqual(fetch.call_args.args[1],api_wallclock_chile_as_utc(PILOT_START.astimezone(timezone.utc)))
        self.assertEqual(fetch.call_args.args[2],api_wallclock_chile_as_utc(NOW))
        self.assertEqual(db.cursors,[(NOW,1,RECENT_CURSOR)])

    def test_conserva_la_modificacion_mas_reciente(self):
        db=FakeDB()
        old=compra("AAA-1-COT26","2026-11-20T19:00:00Z","2026-11-20T18:55:00Z")
        new=compra("AAA-1-COT26","2026-11-20T19:30:00Z","2026-11-20T18:55:00Z")
        with patch("monitor_supabase.fetch_publications",return_value=[]), \
             patch("monitor_supabase.fetch_changes",return_value=[new,old]):
            n=monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(n,1)
        self.assertEqual(db.ingest[0]["p_registro"]["fecha_ultimo_cambio"],"2026-11-20T19:30:00Z")

    def test_error_no_mueve_cursor(self):
        db=FakeDB()
        with patch("monitor_supabase.fetch_publications",return_value=[]), \
             patch("monitor_supabase.fetch_changes",side_effect=RuntimeError("504")):
            with self.assertRaises(RuntimeError):
                monitor_actualidad(db,"ticket",NOW)
        self.assertEqual(db.cursors,[])


    def test_publicacion_nueva_sin_cambio_se_guarda(self):
        db = FakeDB()
        item = compra("NUEVA-1-COT26",
                      "2026-11-20T19:30:00Z", "2026-11-20T19:30:00Z")
        with patch("monitor_supabase.fetch_publications", return_value=[item]) as pubs, \
             patch("monitor_supabase.fetch_changes", return_value=[]) as changes:
            n = monitor_actualidad(db, "ticket", NOW)
        self.assertEqual(n, 1)
        self.assertEqual(db.ingest[0]["p_registro"]["codigo"], "NUEVA-1-COT26")
        self.assertEqual(db.cursors, [(NOW, 1, RECENT_CURSOR)])
        pubs.assert_called_once_with("ticket", api_wallclock_chile_as_utc(PILOT_START.astimezone(timezone.utc)), api_wallclock_chile_as_utc(NOW))
        changes.assert_called_once_with("ticket", api_wallclock_chile_as_utc(PILOT_START.astimezone(timezone.utc)), api_wallclock_chile_as_utc(NOW))

    def test_ambas_fuentes_deduplicadas_y_prevalece_cambio_reciente(self):
        db = FakeDB()
        pub = compra("A-1-COT26",
                     "2026-11-20T19:00:00Z", "2026-11-20T19:00:00Z")
        mod = compra("A-1-COT26",
                     "2026-11-20T19:30:00Z", "2026-11-20T19:00:00Z")
        other = compra("B-1-COT26",
                       "2026-11-20T19:31:00Z", "2026-11-20T19:31:00Z")
        with patch("monitor_supabase.fetch_publications", return_value=[pub, other]), \
             patch("monitor_supabase.fetch_changes", return_value=[mod]):
            n = monitor_actualidad(db, "ticket", NOW)
        self.assertEqual(n, 2)
        self.assertEqual(len(db.ingest), 2)
        self.assertEqual(db.ingest[0]["p_registro"]["fecha_ultimo_cambio"],
                         "2026-11-20T19:30:00Z")

    def test_error_publicaciones_no_guarda_cursor_ni_llama_cambios(self):
        db = FakeDB()
        with patch("monitor_supabase.fetch_publications",
                   side_effect=RuntimeError("publicaciones 504")), \
             patch("monitor_supabase.fetch_changes") as changes:
            with self.assertRaisesRegex(RuntimeError, "publicaciones 504"):
                monitor_actualidad(db, "ticket", NOW)
        self.assertEqual(db.cursors, [])
        changes.assert_not_called()

    def test_error_modificaciones_no_guarda_publicaciones_ni_cursor(self):
        db = FakeDB()
        item = compra("NUEVA-1-COT26",
                      "2026-11-20T19:30:00Z", "2026-11-20T19:30:00Z")
        with patch("monitor_supabase.fetch_publications", return_value=[item]), \
             patch("monitor_supabase.fetch_changes",
                   side_effect=RuntimeError("cambios 504")):
            with self.assertRaisesRegex(RuntimeError, "cambios 504"):
                monitor_actualidad(db, "ticket", NOW)
        self.assertEqual(db.cursors, [])
        self.assertEqual(db.ingest, [])



class PersistenciaRetryTests(unittest.TestCase):
    """Pruebas aisladas: no consultan ChileCompra ni escriben en Supabase."""

    @staticmethod
    def error_http(code):
        from io import BytesIO
        from urllib.error import HTTPError
        return HTTPError("https://ejemplo.test/rest/v1/rpc/faro_guardar_oportunidad",
                         code, "simulado", {}, BytesIO(b"error simulado"))

    def test_http_522_reintenta_y_recupera(self):
        from unittest.mock import MagicMock
        from monitor_supabase import http_json
        respuesta = MagicMock()
        respuesta.__enter__.return_value.read.return_value = b"123"
        with patch("monitor_supabase.urlopen",
                   side_effect=[self.error_http(522), respuesta]) as abrir, \
             patch("monitor_supabase.time.sleep") as esperar:
            self.assertEqual(http_json("https://ejemplo.test"), 123)
        self.assertEqual(abrir.call_count, 2)
        esperar.assert_called_once()

    def test_http_522_agota_reintentos(self):
        from monitor_supabase import http_json, MAX_ATTEMPTS
        with patch("monitor_supabase.urlopen",
                   side_effect=[self.error_http(522) for _ in range(MAX_ATTEMPTS)]) as abrir, \
             patch("monitor_supabase.time.sleep") as esperar:
            with self.assertRaisesRegex(RuntimeError, "HTTP 522"):
                http_json("https://ejemplo.test")
        self.assertEqual(abrir.call_count, MAX_ATTEMPTS)
        self.assertEqual(esperar.call_count, MAX_ATTEMPTS - 1)

    def test_http_400_no_reintenta(self):
        from monitor_supabase import http_json
        with patch("monitor_supabase.urlopen",
                   side_effect=self.error_http(400)) as abrir, \
             patch("monitor_supabase.time.sleep") as esperar:
            with self.assertRaisesRegex(RuntimeError, "HTTP 400"):
                http_json("https://ejemplo.test")
        abrir.assert_called_once()
        esperar.assert_not_called()

    def test_error_de_guardado_identifica_codigo_y_no_avanza_cursor(self):
        class FallaSegundaCompra(FakeDB):
            def request(self, table, method="GET", data=None):
                if data["p_registro"]["codigo"] == "FALLA-2-COT26":
                    raise RuntimeError("HTTP 522 simulado")
                return super().request(table, method=method, data=data)

        db = FallaSegundaCompra()
        items = [
            compra("OK-1-COT26", "2026-11-20T19:30:00Z", "2026-11-20 19:00"),
            compra("FALLA-2-COT26", "2026-11-20T19:31:00Z", "2026-11-20 19:00"),
            compra("PEND-3-COT26", "2026-11-20T19:32:00Z", "2026-11-20 19:00"),
        ]
        with patch("monitor_supabase.fetch_publications", return_value=items), \
             patch("monitor_supabase.fetch_changes", return_value=[]):
            with self.assertRaisesRegex(RuntimeError, "FALLA-2-COT26.*HTTP 522"):
                monitor_actualidad(db, "ticket", NOW)
        self.assertEqual([x["p_registro"]["codigo"] for x in db.ingest],
                         ["OK-1-COT26"])
        self.assertEqual(db.cursors, [])


if __name__=="__main__":
    unittest.main()
