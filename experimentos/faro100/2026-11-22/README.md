# FARO-100: muestra multirrubro v1

**100 compras ágiles reales de Supabase; selección congelada el 22-11-2026. No se modificó producción.**

## Archivos
- `muestra_faro100.csv`: manifiesto de 100 registros distintos y metadatos del listado, exportado en UTF-8 con BOM para Excel.
- `seleccion_faro100.sql`: consulta de solo lectura para reproducir el método de selección.

## Procedencia
- Tabla `public.oportunidades`, fuente `compra_agil_v2`; población de 8.954 registros al corte.
- Universo fijado con `id <= 12649` y `detectada_at <= 2026-11-22T04:32:41.815282Z`.
- Semilla fija `FARO100-20261122-v1` y ordenación por hash `md5` del código. No se usa `random()`.
- 30 `titulo_extenso`: título >=75 caracteres, fuera de la regla de títulos genéricos.
- 40 `titulo_breve_o_generico`: título <=42 caracteres o título que coincide con la expresión genérica exacta del SQL.
- 30 `aleatorio`: seleccionados del universo restante, sin repetir los anteriores.

**Importante:** largo de título es un proxy de muestreo, no una clasificación semántica. Títulos breves pueden ser perfectamente claros y títulos largos pueden ser vagos. Los porcentajes 30/40/30 son deliberados y NO representan prevalencias del mercado. La variedad de rubros debe validarse al etiquetar.

## Reproducibilidad
La membresía **exacta** está congelada por `oportunidad_id` y `codigo` en el CSV. El SQL reproduce el algoritmo, pero en una base viva la actualización posterior de títulos podría cambiar la selección. Para recuperar las mismas compras, consultar por los 100 ID del CSV.

En la selección original solo se exportaron datos del listado; posteriormente se recuperaron exitosamente los 100 detalles el 22-11-2026 en la ejecución de GitHub Actions #44987485178. Los adjuntos todavía no se han descargado. `documentos_en_listado` es el tamaño del arreglo JSON `documentos`, no un análisis de los archivos. No se asignaron etiquetas de relevancia ni rubros definitivos.

## Próxima fase
1. Definir perfiles de proveedores multirrubro para evaluar relevancia.
2. Etiquetar manualmente con evidencia independiente de la predicción.
3. Comparar A: UNSPSC; B: título+detalle+productos; C: B más conflicto UNSPSC; D: C más adjuntos.
4. Medir falsos negativos, falsos positivos, incertidumbre, necesidad de adjuntos y costos/latencias.

Regla central: **no descartar una oportunidad solo por UNSPSC o título**.


## Descarga de detalle (100/100 completados el 22-11-2026)
- `descargar_detalles.py` lee exactamente los 100 códigos del manifiesto y hace **GET** a `/v2/compra-agil/{codigo}`, sin conectar con Supabase.
- Reintentos para 429/500/502/503/504/522; cada código se guarda en `salida_detalles/<codigo>.json` con respuesta íntegra y hora de descarga.
- Reanudable: no vuelve a consultar archivos existentes y válidos; registra fallos en `salida_detalles/resultado_descarga.json`. No descarga adjuntos.
- `test_descargar_detalles.py` valida manifiesto, simulación, caché, continuidad tras fallos y validación de código sin red.
- El workflow `test_faro100.yml` solo corre pruebas **sin ticket ni conexión** en la rama experimental.

### Ejecución segura local
Desde la carpeta `experimentos/faro100/2026-11-22`:

```powershell
python descargar_detalles.py --dry-run --limit 3
# Configurar CHILECOMPRA_TICKET en una variable de entorno de sesión, no en el repositorio.
python descargar_detalles.py --limit 3
# Si las primeras tres respuestas son correctas, continuar:
python descargar_detalles.py --limit 100
```

**No pegar el ticket en capturas, commits, logs o mensajes.** Si se ejecuta sin `CHILECOMPRA_TICKET`, el programa falla antes de solicitar la API. Los archivos `salida_detalles/` están ignorados por Git para evitar publicar respuestas sin revisión.

La ejecución de los 100 detalles ya fue completada (100 descargados, 0 fallidos) y el artefacto histórico se encuentra en https://github.com/mgarcia1306/fap/actions/runs/44987485178. El workflow de CI no usa secretos.


### Prueba manual de adjuntos del caso 4 en GitHub Actions

Se adaptó el archivo local `test_descarga_adjuntos.py` como `descargar_adjuntos_faro100.py`. La prueba consulta **únicamente** los adjuntos de `3904-1092-COT26`, usando los endpoints públicos `/listar/{codigo}` y `/descargar/{uuid}`. No necesita ticket ni Supabase.

1. Abrir **Actions → FARO - Diagnostico API → Run workflow**.
2. En **Use workflow from**, seleccionar exactamente `experimento/faro-100-muestra-20261122` (no `main`).
3. Ejecutar. Se instalan dependencias, corren pruebas sin red y se descargan los adjuntos de la compra de Bulnes.
4. Descargar el artefacto `faro100-adjuntos-3904-1092-<run_id>` del resumen de ejecución; retención de 7 días.

**Importante:** el workflow de `main` sigue siendo el diagnóstico habitual. Esta variante de `diagnostico.yml` reemplaza temporalmente la descarga de detalles **solo en la rama experimental**; el script `descargar_detalles.py` se conserva. No se modifican monitores ni Supabase. Los PDF se excluyen de Git mediante `.gitignore`.

El script limita la descarga a 20 archivos de 25 MiB como máximo cada uno, valida cabeceras PDF, registra errores y evita nombres peligrosos o duplicados. Se probaron sus funciones sin red antes de incorporarlo a GitHub.
