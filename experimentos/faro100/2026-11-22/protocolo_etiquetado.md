# FARO-100 · Protocolo de etiquetado y evaluación v1

## Objetivo
Medir cómo distintos métodos de clasificación detectan compras relevantes para ocho perfiles hipotéticos. **El objetivo principal es minimizar falsos negativos** sin disparar falsos positivos. El experimento es multirrubro y la muestra es intencionalmente estratificada, por lo que no permite extrapolar directamente porcentajes al universo completo.

## Unidad de análisis
- 100 códigos únicos del manifiesto `muestra_faro100.csv`.
- 8 perfiles definidos en `perfiles_proveedor.md`.
- 800 pares (compra, perfil) en `plantilla_etiquetado.csv`.
- Evaluación de pertinencia técnica/comercial por separado de filtros de elegibilidad (región, plazo, estado, certificaciones, etc.).

## Etiquetas de referencia humana
- `coincidencia_confirmada`: evidencia explícita de que el objeto solicitado encaja con el catálogo/capacidad definida; no depende solo de UNSPSC.
- `coincidencia_posible`: encaje plausible, pero faltan especificaciones o se requiere confirmar capacidad del proveedor.
- `informacion_insuficiente`: no hay evidencia suficiente ni para afirmar pertinencia ni para descartarla con fundamento.
- `no_relevante`: evidencia positiva de que lo solicitado queda fuera del alcance definido; **ausencia de coincidencia UNSPSC no es evidencia suficiente**.

Las etiquetas se asignan por par compra-perfil. No se asignan por nombre de rubro solamente.

## Fuentes y orden de revisión
1. Título y metadatos originales de listado (sin leer predicciones A-D).
2. Descripción **real** del endpoint de detalle `/v2/compra-agil/{codigo}` y `productos_solicitados` (nombre, descripción, código, cantidad, unidad).
3. Documentos adjuntos cuando haya ambigüedad o contradicción que impida un juicio.
4. UNSPSC se registra **después** de la primera evaluación semántica; documentar conflictos sin usarlo como verdad.
5. Cada etiqueta debe incluir un resumen de evidencia y origen (listado, detalle, producto, adjunto). Si se usó adjunto, registrar nombre del archivo/página o sección.

**Importante:** en esta fase solo se creó la plantilla; no se ha descargado detalle ni adjuntos y ninguna fila ha sido etiquetada.

## Columnas de la plantilla
- `numero`, `grupo_muestreo`, `oportunidad_id`, `codigo`, `perfil_id`: claves congeladas.
- `etiqueta_humana`: una de las cuatro etiquetas anteriores.
- `fuente_evidencia`: `listado`, `detalle`, `producto`, `adjunto`, o combinación separada por `+`.
- `evidencia_resumen`, `razon_etiqueta`: trazabilidad y justificación breve.
- `requiere_adjunto`: `si`/`no`/`pendiente`; `adjunto_referencia`: archivo y ubicación.
- `conflicto_unspsc`: `si`/`no`/`no_disponible`/`pendiente`; `codigo_unspsc_observado`: código observado en detalle.
- `revisor`, `fecha_revision`: auditoría; `observaciones`: excepciones y dudas.
- Todos los campos de juicio están inicialmente vacíos, para evitar etiquetas inventadas.

## Comparación ciega de métodos
- **A**: UNSPSC de los productos, sin título ni descripción. Si falta código, registrar `abstencion`, no inferir `no_relevante`.
- **B**: título + descripción real + nombres y descripciones de productos, sin UNSPSC como regla decisoria.
- **C**: B + comparación/alerta de conflicto UNSPSC; no descartar automáticamente por conflicto.
- **D**: C + análisis de adjuntos solo en casos sin resolución, registrando consultas y esfuerzo.
- Ejecutar A-D sin acceso a las etiquetas humanas. Conservar predicción por par y versión de cada método.
- La evaluación humana idealmente es independiente de las predicciones; resolver discrepancias con revisión documentada.

## Métricas y cautelas
- **Falsos negativos confirmados**: pares con etiqueta `coincidencia_confirmada` que el método marca `no_relevante`.
- **Falsos positivos confirmados**: pares `no_relevante` que el método marca `coincidencia_confirmada`.
- **Posibles/insuficientes**: reportar aparte; no contarlos como negativos confirmados ni forzarlos a verdadero/falso.
- Medir cobertura (cuántos pares resuelve), abstenciones, precisión y sensibilidad solo sobre pares con verdad confirmada; acompañar de denominadores y matrices de confusión.
- Contar además oportunidades únicas afectadas, no solo pares, para evitar confundir 800 evaluaciones con 800 compras.
- Comparar latencia, solicitudes de detalle, adjuntos y coste operativo. El acceso a detalle se hace **una vez por compra**, reutilizable entre perfiles.
- Reportar resultados por estrato y globales de esta muestra; **no estimar prevalencia poblacional** a partir de proporciones 30/40/30.

## Criterio de avance
No entrenar reglas definitivas ni automatizar alertas a clientes hasta disponer de etiquetas humanas auditables, revisión de casos dudosos y medición de falsos negativos.
