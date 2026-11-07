
import os
import json
import time
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode

API_URL = "https://api2.mercadopublico.cl/v2/compra-agil"

ticket = os.environ.get("CHILECOMPRA_TICKET")

if not ticket:
    raise SystemExit("ERROR: Falta CHILECOMPRA_TICKET")

params = {
    "ttl_cambio_ms": 300000,
    "tamano_pagina": 10,
    "numero_pagina": 1
}

url = API_URL + "?" + urlencode(params)

request = Request(
    url,
    headers={
        "ticket": ticket,
        "Accept": "application/json"
    }
)

print("=== DIAGNÓSTICO FARO ===", flush=True)
print("Consultando cambios de los últimos 5 minutos...")
print("Máximo: 10 registros")
print("Realizando una única solicitud...")

inicio = time.monotonic()

try:
    with urlopen(request, timeout=45) as response:
        duracion = time.monotonic() - inicio
        data = json.load(response)

        print(f"\nHTTP: {response.status}")
        print(f"Tiempo de respuesta: {duracion:.2f} segundos")
        print(f"Resultado API: {data.get('success')}")

        payload = data.get("payload") or {}
        items = payload.get("items", [])
        paginacion = payload.get("paginacion") or {}

        print(f"Registros en esta página: {len(items)}")
        print(
            "Total de resultados:",
            paginacion.get("total_resultados", "No informado")
        )

        for item in items:
            print(
                item.get("codigo"),
                "-",
                item.get("nombre")
            )

except HTTPError as error:
    duracion = time.monotonic() - inicio

    print(f"\nHTTP ERROR: {error.code}")
    print(f"Tiempo transcurrido: {duracion:.2f} segundos")
    print(f"Motivo: {error.reason}")

except (URLError, TimeoutError) as error:
    duracion = time.monotonic() - inicio

    print("\nERROR DE CONEXIÓN")
    print(f"Tiempo transcurrido: {duracion:.2f} segundos")
    print(str(error))

print("\n=== FIN DEL DIAGNÓSTICO ===")
