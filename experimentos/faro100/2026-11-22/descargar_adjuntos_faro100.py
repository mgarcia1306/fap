"""Descarga controlada de adjuntos para 3904-1092-COT26, sin Supabase.

Adaptación del archivo local test_descarga_adjuntos.py.
"""
import argparse
import json
import os
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE = "https://servicios-compra-agil.mercadopublico.cl/v1/adjuntos-compra-agil"
CODIGO = "3904-1092-COT26"
HERE = Path(__file__).resolve().parent
MAX_BYTES = 25 * 1024 * 1024
MAX_FILES = 20


def nombre_seguro(nombre):
    nombre = str(nombre).replace("\\", "/").split("/")[-1].strip()
    nombre = re.sub(r'[<>:"|?*\x00-\x1f]', "_", nombre)
    if nombre in ("", ".", ".."):
        raise ValueError("Nombre de adjunto inválido")
    return nombre[:180]


def crear_sesion():
    sesion = requests.Session()
    reintentos = Retry(total=3, connect=3, read=3, backoff_factor=1.5,
                       status_forcelist=[429, 500, 502, 503, 504, 522],
                       allowed_methods=["GET"], respect_retry_after_header=True)
    sesion.mount("https://", HTTPAdapter(max_retries=reintentos))
    return sesion


def listar(sesion):
    respuesta = sesion.get(f"{BASE}/listar/{CODIGO}", timeout=(15, 45))
    respuesta.raise_for_status()
    datos = respuesta.json()
    if not isinstance(datos, dict) or datos.get("success") != "OK":
        raise ValueError("Listado de adjuntos sin success=OK")
    archivos = (datos.get("payload") or {}).get("files")
    if not isinstance(archivos, list) or not archivos:
        raise ValueError("Listado de adjuntos vacío o inválido")
    if len(archivos) > MAX_FILES:
        raise ValueError("Número inesperado de adjuntos")
    return archivos


def descargar_uno(sesion, archivo, carpeta):
    identificador = str(uuid.UUID(str(archivo["id"])))
    nombre = nombre_seguro(archivo["nombreArchivo"])
    destino = carpeta / f"{identificador[:8]}_{nombre}"
    temporal = destino.with_name(destino.name + ".part")
    bytes_recibidos = 0
    cabecera = b""
    try:
        with sesion.get(f"{BASE}/descargar/{identificador}", timeout=(15, 90),
                       stream=True) as respuesta:
            respuesta.raise_for_status()
            tipo = respuesta.headers.get("Content-Type", "").lower()
            if any(x in tipo for x in ("application/json", "text/html", "text/plain")):
                raise ValueError(f"Contenido inesperado: {tipo}")
            with temporal.open("wb") as salida:
                for fragmento in respuesta.iter_content(chunk_size=65536):
                    if not fragmento:
                        continue
                    bytes_recibidos += len(fragmento)
                    if bytes_recibidos > MAX_BYTES:
                        raise ValueError("Archivo supera el máximo de 25 MiB")
                    if len(cabecera) < 1024:
                        cabecera += fragmento[:1024-len(cabecera)]
                    salida.write(fragmento)
        if bytes_recibidos == 0:
            raise ValueError("Archivo vacío")
        if nombre.lower().endswith(".pdf") and b"%PDF-" not in cabecera:
            raise ValueError("El archivo no contiene cabecera PDF")
        os.replace(temporal, destino)
        return {"id": identificador, "nombre_original": archivo["nombreArchivo"],
                "archivo": destino.name, "bytes": bytes_recibidos}
    finally:
        temporal.unlink(missing_ok=True)


def ejecutar(carpeta, sesion):
    carpeta.mkdir(parents=True, exist_ok=True)
    archivos = listar(sesion)
    correctos, errores = [], []
    for indice, archivo in enumerate(archivos, 1):
        try:
            dato = descargar_uno(sesion, archivo, carpeta)
            correctos.append(dato)
            print(f"[{indice}/{len(archivos)}] OK {dato['archivo']} ({dato['bytes']} bytes)", flush=True)
        except (requests.RequestException, ValueError, KeyError, TypeError, OSError) as exc:
            errores.append({"id": str(archivo.get("id", "")), "error": str(exc)})
            print(f"[{indice}/{len(archivos)}] ERROR {type(exc).__name__}: {exc}", flush=True)
    resumen = {"codigo": CODIGO, "fecha_utc": datetime.now(timezone.utc).isoformat(),
               "adjuntos_listados": len(archivos), "descargados": len(correctos),
               "fallidos": len(errores), "archivos": correctos, "errores": errores}
    (carpeta / "resultado_adjuntos.json").write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return resumen


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=HERE / "salida_adjuntos" / CODIGO)
    args = parser.parse_args()
    with crear_sesion() as sesion:
        resumen = ejecutar(args.output, sesion)
    print(json.dumps({k: resumen[k] for k in ("codigo", "adjuntos_listados", "descargados", "fallidos")}))
    return 0 if resumen["fallidos"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
