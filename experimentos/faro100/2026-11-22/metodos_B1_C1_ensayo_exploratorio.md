# FARO-100 — Ensayo exploratorio B1/C1 (texto + alerta UNSPSC)
**Fecha:** 2026-11-25. **Rama:** `experimento/faro-100-muestra-20261122`. **Estado:** comparación exploratoria de reglas, NO se declara ejecución validada de B/C del protocolo ni desempeño de un modelo de IA.

## Estado previo reutilizado
- 15 compras con detalles reales obtenidos en el ZIP histórico del run GitHub Actions [44987485178](https://github.com/mgarcia1306/fap/actions/runs/44987485178).
- 120 pares con etiqueta humana ya registrados en `piloto15_etiquetado.csv`, sin modificaciones.
- Prueba A0 existente: `metodo_A0_ensayo_exploratorio.md`. En A0 hubo 24 abstenciones, un falso negativo confirmado y un falso positivo confirmado; estos son resultados de un diccionario provisional.
- Perfiles congelados en `perfiles_proveedor.md`; protocolo en `protocolo_etiquetado.md`.

## Métodos ensayados
- **B1:** clasificador programático de expresiones de productos y servicios. Lee `nombre`, `descripcion`, y descripciones de `productos_solicitados`. **No utiliza códigos UNSPSC ni etiquetas humanas para emitir predicciones.** Reglas transparentes por perfil y exclusiones técnicas. Las compras sin productos no quedan automáticamente descartadas: se atiende a la descripción de servicio o se emite `informacion_insuficiente` si corresponde.
- **C1:** conserva la predicción B1 y añade alerta `conflicto_posible` cuando la señal A0 de códigos contradice la interpretación B1; añade `sin_codigos` cuando A0 se abstiene. No deja que un código sospechoso anule la evidencia semántica.
- **Advertencia de diseño:** las expresiones y exclusiones se diseñaron conociendo ya los 15 casos del piloto. Se hizo además una **corrección de dos errores de expresiones regulares tras la inspección de los resultados**: «preparación» se confundía con «reparación» y los tornillos de montaje de un switch eran interpretados como un suministro de ferretería. Los resultados siguientes son **post-corrección y NO constituyen una evaluación ciega ni una generalización válida**. Esta versión B1/C1 debe congelarse antes de medir sobre compras nunca vistas.

## Resultados revisados y reproducidos en el entorno de análisis
| Variable | A0 (existente) | B1 | C1 |
|---|---:|---:|---:|
| Pares evaluados | 120 | 120 | 120 |
| Coincidencia exacta con etiqueta humana | 81 | **107** | **107** (por diseño) |
| Abstenciones por ausencia de códigos | 24 | — | — |
| Falsos negativos confirmados según protocolo | 1 | **0** | **0** |
| Falsos positivos confirmados según protocolo | 1 | **0** | **0** |
| Alertas por discordancia código/texto | — | — | **8** |
| Pares sin códigos registrados | 24 | — | **24** |

**Distribución B1/C1:** 112 `no_relevante`, 3 `coincidencia_confirmada`, 3 `coincidencia_posible`, 2 `informacion_insuficiente`.

**Matriz de B1 (fila humana, columna predicción):**

| Humana | Confirmada | Posible | Insuficiente | No relevante |
|---|---:|---:|---:|---:|
| `coincidencia_confirmada` | 2 | 2 | 0 | 0 |
| `coincidencia_posible` | 1 | 1 | 1 | 9 |
| `informacion_insuficiente` | 0 | 0 | 1 | 0 |
| `no_relevante` | 0 | 0 | 0 | 103 |

De cuatro coincidencias confirmadas humanas, B1 propone dos confirmadas y dos posibles; ninguna queda descartada. Las nueve posibles humanas descartadas reflejan el problema conceptual no resuelto: **el B1 evalúa el catálogo acotado y no cuenta con un campo separado para interés comercial adyacente**.

## Ocho alertas C1
1. `3145-615-COT26` / `CONSTRUCCION` — A0 posible, B1 descarte.
2. `3145-615-COT26` / `MANTENCION` — A0 descarte, B1 confirmada.
3. `1075337-2243-COT26` / `SALUD` — A0 posible, B1 descarte.
4. `1018-88-COT26` / `SALUD` — A0 posible, B1 descarte.
5. `1018-88-COT26` / `ASEO` — A0 posible, B1 descarte.
6. `1018-88-COT26` / `TEXTIL` — A0 posible, B1 descarte.
7. `1057498-2745-COT26` / `SALUD` — A0 descarte, B1 confirmada.
8. `1058045-625-COT26` / `SALUD` — A0 confirmada, B1 descarte.

Las alertas son **discordancias entre reglas**, no necesariamente errores UNSPSC certificados. El código real puede corresponder a una familia válida pero demasiado amplia. No afirmar que las ocho sean códigos incorrectos.

## Límites y pasos pendientes
- B1/C1 **no son un clasificador de IA**: son heurísticas transparentes, con fragilidad ante variaciones de lenguaje y descripciones nuevas.
- El contraste A0/B1 no es un benchmark neutral: diccionarios y heurísticas fueron ajustados con conocimiento de la muestra. Los 107 acuerdos no representan precisión ni rendimiento real de FARO.
- D (adjuntos) no se ha ejecutado; no equiparar el informe histórico de IA con B1/C1.
- Falta validar taxonomía oficial UNSPSC, realizar prueba fuera de muestra y separar `pertinencia_catalogo` de `interes_adyacente` manteniendo las etiquetas históricas intactas.
- No se modificaron `main`, monitor, Supabase, automatizaciones ni los 120 juicios humanos.

**Reproducción local:** `faro100_metodos_B1_C1.py` lee el artefacto ZIP original y el CSV de claves/etiquetas; depende de la versión A0 reproducible para la señal de códigos. Este script y su CSV de resultados están disponibles como artefactos de esta conversación, pero **no se han desplegado en producción**.
