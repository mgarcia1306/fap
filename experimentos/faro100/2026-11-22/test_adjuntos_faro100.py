"""Pruebas unitarias del descargador de adjuntos; sin solicitudes HTTP."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock
import descargar_adjuntos_faro100 as d

UUID = "43733C13-56F4-4AE6-A8D0-DD82149BA014"

class Respuesta:
    def __init__(self, data=b"%PDF-1.7\\nEjemplo", tipo="application/pdf"):
        self.data = data
        self.headers = {"Content-Type": tipo}
    def raise_for_status(self):
        pass
    def iter_content(self, chunk_size=65536):
        yield self.data
    def __enter__(self):
        return self
    def __exit__(self, *args):
        return False

class PruebasAdjuntos(unittest.TestCase):
    def test_nombre_seguro(self):
        self.assertEqual(d.nombre_seguro("../../archivo.pdf"), "archivo.pdf")
        self.assertEqual(d.nombre_seguro("C:\\carpeta\\archivo.pdf"), "archivo.pdf")
        with self.assertRaises(ValueError):
            d.nombre_seguro("..")

    def test_listado(self):
        r = Mock()
        r.json.return_value = {"success":"OK","payload":{"files":[{"id":UUID,"nombreArchivo":"OP26-1628.pdf"}]}}
        s = Mock()
        s.get.return_value = r
        self.assertEqual(len(d.listar(s)), 1)
        self.assertIn(d.CODIGO, s.get.call_args.args[0])

    def test_pdf_valido(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Mock()
            s.get.return_value = Respuesta()
            dato = d.descargar_uno(s, {"id":UUID,"nombreArchivo":"../OP26-1628.pdf"}, Path(tmp))
            self.assertTrue((Path(tmp) / dato["archivo"]).exists())
            self.assertGreater(dato["bytes"], 0)

    def test_rechaza_html(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Mock()
            s.get.return_value = Respuesta(b"<html>error</html>", "text/html")
            with self.assertRaises(ValueError):
                d.descargar_uno(s, {"id":UUID,"nombreArchivo":"OP26-1628.pdf"}, Path(tmp))
            self.assertEqual(list(Path(tmp).iterdir()), [])

    def test_rechaza_pdf_invalido(self):
        with tempfile.TemporaryDirectory() as tmp:
            s = Mock()
            s.get.return_value = Respuesta(b"No es PDF")
            with self.assertRaises(ValueError):
                d.descargar_uno(s, {"id":UUID,"nombreArchivo":"OP26-1628.pdf"}, Path(tmp))

if __name__ == "__main__":
    unittest.main()
