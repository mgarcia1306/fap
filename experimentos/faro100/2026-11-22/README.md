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

Solo se exportaron datos del listado: no se consultó detalle ni se descargaron adjuntos. `documentos_en_listado` es el tamaño del arreglo JSON `documentos`, no un análisis de los archivos. No se asignaron etiquetas de relevancia ni rubros definitivos.

## Próxima fase
1. Definir perfiles de proveedores multirrubro para evaluar relevancia.
2. Etiquetar manualmente con evidencia independiente de la predicción.
3. Comparar A: UNSPSC; B: título+detalle+productos; C: B más conflicto UNSPSC; D: C más adjuntos.
4. Medir falsos negativos, falsos positivos, incertidumbre, necesidad de adjuntos y costos/latencias.

Regla central: **no descartar una oportunidad solo por UNSPSC o título**.
