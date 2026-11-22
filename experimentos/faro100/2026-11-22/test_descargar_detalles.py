"""Pruebas locales de la descarga FARO-100, sin red ni credenciales."""
import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import descargar_detalles as d


class FARO100DetailTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.rows = [{"numero": str(i), "codigo": f"123-{i}-COT26"} for i in range(1, 101)]

    def test_manifest_valido_y_sin_duplicados(self):
        p = self.root / "muestra.csv"
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["numero", "codigo"])
            w.writeheader()
            w.writerows(self.rows)
        self.assertEqual(len(d.read_manifest(p)), 100)
        self.rows[1]["codigo"] = self.rows[0]["codigo"]
        with p.open("w", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=["numero", "codigo"])
            w.writeheader()
            w.writerows(self.rows)
        with self.assertRaisesRegex(ValueError, "duplicados"):
            d.read_manifest(p)

    def test_dry_run_no_escribe_ni_consulta(self):
        out = self.root / "no_crear"
        with patch.object(d, "get_detail", side_effect=AssertionError("red")):
            result = d.collect(self.rows, out, "", limit=3, dry_run=True)
        self.assertEqual(result["seleccionadas"], 3)
        self.assertFalse(out.exists())

    def test_descarga_una_vez_y_reutiliza_cache(self):
        out = self.root / "detalles"
        fake = {"success": "OK", "payload": {"codigo": "123-1-COT26", "descripcion": "Ejemplo"}}
        with patch.object(d, "get_detail", return_value=fake) as fetch:
            result = d.collect(self.rows, out, "ticket-falso", limit=1, pause=0)
            self.assertEqual(result["descargadas"], 1)
            result2 = d.collect(self.rows, out, "ticket-falso", limit=1, pause=0)
            self.assertEqual(result2["en_cache"], 1)
            fetch.assert_called_once()
        self.assertEqual(json.loads((out / "123-1-COT26.json").read_text(encoding="utf-8"))["respuesta"], fake)

    def test_fallo_no_detiene_otros_codigos(self):
        def fake(code, ticket):
            if code.endswith("-1-COT26"):
                raise RuntimeError("HTTP 522 simulado")
            return {"success": "OK", "payload": {"codigo": code}}
        with patch.object(d, "get_detail", side_effect=fake):
            result = d.collect(self.rows, self.root / "detalles", "ticket-falso", limit=2, pause=0)
        self.assertEqual((result["fallidas"], result["descargadas"]), (1, 1))
        self.assertTrue((self.root / "detalles" / "123-2-COT26.json").exists())

    def test_no_acepta_codigo_arbitrario(self):
        with self.assertRaises(ValueError):
            d.get_detail("../admin", "ticket-falso")

    def test_no_acepta_detalle_de_otro_codigo(self):
        from io import BytesIO
        from contextlib import contextmanager
        @contextmanager
        def response():
            yield BytesIO(b'{"success":"OK","payload":{"codigo":"otro"}}')
        with patch.object(d, "urlopen", return_value=response()):
            with self.assertRaisesRegex(ValueError, "no corresponde"):
                d.get_detail("123-1-COT26", "ticket-falso")


if __name__ == "__main__":
    unittest.main()
