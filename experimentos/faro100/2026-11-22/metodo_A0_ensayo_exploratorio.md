# FARO-100 · Método A0 exploratorio — únicamente códigos UNSPSC

**Fecha:** 2026-11-25. **Rama:** `experimento/faro-100-muestra-20261122`. **Alcance:** solo 15 compras del piloto y 8 perfiles hipotéticos (120 pares). **Estado:** diagnóstico preliminar, **NO constituye el método A–D validado**, NO apto para producción ni para extrapolar a 800 pares.

## Fuentes y condiciones
- Manifiesto y referencias: `piloto15_etiquetado.csv`, `perfiles_proveedor.md`, `protocolo_etiquetado.md` en la misma carpeta.
- Datos brutos recuperados, sin consultar nuevamente Mercado Público: artefacto histórico del workflow [44987485178](https://github.com/mgarcia1306/fap/actions/runs/44987485178), ZIP `faro100-detalles-44987485178`. Se extrajo SOLO `productos_solicitados[].codigo_producto` de los 15 JSON para generar predicciones; **no se lee título, descripción, nombre del producto ni etiquetas humanas** durante la predicción.
- Correspondencia de código a perfil **manual/provisional** establecida a partir de las denominaciones de códigos presentes en el detalle original y el alcance del perfil. **No se verificó con una taxonomía UNSPSC oficial ni con catálogos reales del proveedor.** Es exploratoria, definida una vez conocida la distribución y el contenido del piloto, por lo que no es evaluación ciega independiente.
- Exclusiones de perfiles que describen capacidades, no certificaciones. Regla simple: códigos directos para TODOS los códigos distintos de una compra → `coincidencia_confirmada`; si al menos un código es directo o débil y no todos directos → `coincidencia_posible`; si hay códigos y ninguno mapeado → `no_relevante`; **si no hay códigos → `abstencion`** (no descarte).
- La regla no tiene información de parcialidad de adjudicación ni capacidad efectiva; una coincidencia código-producto puede inducir falsos positivos porque el código original esté mal asignado. No usa reglas semánticas de nombres ni documentación adjunta.

## Diccionario A0 (no ajustado según la evaluación humana)
| Perfil | Códigos directos | Códigos débiles / ambiguos |
|---|---|---|
| CONSTRUCCION | 27112801, 31211501, 31211904, 31211906 | 40101825 |
| OFICINA | 82121507 | — |
| TECNOLOGIA | 32101622, 43211708, 43201549 | 26111704, 26121630, 52161512, 52161520 |
| SALUD | 42192604 | 42181504, 39101608 |
| ALIMENTOS | — | — |
| ASEO | 47121612 | — |
| TEXTIL | — | 53102504 |
| MANTENCION | — | — |

**Nota:** las palabras "directo" o "débil" califican la afinidad *de la denominación UNSPSC*, no garantizan que el objeto real o el proveedor encajen. Códigos no incluidos no se expandieron por sufijos, segmentos o jerarquías.

## Resultados del A0 (después de congelar predicciones)
- 120 pares = 15 compras × 8 perfiles; 26 códigos distintos en el subconjunto; 24 abstenciones (20%).
- Predicciones A0: `abstencion` 24; `coincidencia_confirmada` 3; `coincidencia_posible` 7; `no_relevante` 86.
- Coincidencias exactas con etiquetas humanas: 81/120, incluidas abstenciones como discordancia respecto de las cuatro etiquetas humanas (NO equivalente a accuracy ni precisión de clasificador).
- Referencia humana `coincidencia_confirmada`: 4 pares; 3 fueron detectados por A0 como directos o posibles, 1 fueron `no_relevante` (**falsos negativos confirmados bajo regla del protocolo**). 0 abstenciones entre confirmados.
- Falsos positivos confirmados (humanos `no_relevante` clasificados por A0 como `coincidencia_confirmada`): 1.
- Comparación exploratoria exacta sobre etiquetas con evidencia concluyente (`confirmada`/ `no_relevante`): 107 pares, sin atribuir equivalencia al resto.

### Matriz (filas = humana, columnas = A0)
| Humana | confirmada | posible | no_relevante | abstencion |
|---|---:|---:|---:|---:|
| coincidencia_confirmada | 1 | 2 | 1 | 0 |
| coincidencia_posible | 1 | 2 | 7 | 2 |
| informacion_insuficiente | 0 | 0 | 0 | 1 |
| no_relevante | 1 | 3 | 78 | 21 |

### Errores de interés
- Falsos negativos confirmados: 1057498-2745-COT26/SALUD.
- Falsos positivos confirmados: 1058045-625-COT26/SALUD.
- Pares discrepantes (incluyendo abstenciones): 39. **La abstención no es un descarte**; debe medirse por separado.

## Predicciones por par y comparación posterior
| Código | Perfil | Códigos observados | Predicción A0 | Humana |
|---|---|---|---|---|
| 3904-1092-COT26 | CONSTRUCCION | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | OFICINA | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | TECNOLOGIA | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | SALUD | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | ALIMENTOS | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | ASEO | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | TEXTIL | 53131609 | no_relevante | no_relevante |
| 3904-1092-COT26 | MANTENCION | 53131609 | no_relevante | no_relevante |
| 3145-615-COT26 | CONSTRUCCION | 30201603, 40101825 | coincidencia_posible | coincidencia_posible |
| 3145-615-COT26 | OFICINA | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | TECNOLOGIA | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | SALUD | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | ALIMENTOS | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | ASEO | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | TEXTIL | 30201603, 40101825 | no_relevante | no_relevante |
| 3145-615-COT26 | MANTENCION | 30201603, 40101825 | no_relevante | coincidencia_posible |
| 1075337-2243-COT26 | CONSTRUCCION | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | OFICINA | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | TECNOLOGIA | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | SALUD | 42181504 | coincidencia_posible | coincidencia_posible |
| 1075337-2243-COT26 | ALIMENTOS | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | ASEO | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | TEXTIL | 42181504 | no_relevante | no_relevante |
| 1075337-2243-COT26 | MANTENCION | 42181504 | no_relevante | no_relevante |
| 2771-694-COT26 | CONSTRUCCION | — | abstencion | no_relevante |
| 2771-694-COT26 | OFICINA | — | abstencion | informacion_insuficiente |
| 2771-694-COT26 | TECNOLOGIA | — | abstencion | no_relevante |
| 2771-694-COT26 | SALUD | — | abstencion | no_relevante |
| 2771-694-COT26 | ALIMENTOS | — | abstencion | no_relevante |
| 2771-694-COT26 | ASEO | — | abstencion | no_relevante |
| 2771-694-COT26 | TEXTIL | — | abstencion | coincidencia_posible |
| 2771-694-COT26 | MANTENCION | — | abstencion | no_relevante |
| 1211-117-COT26 | CONSTRUCCION | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1211-117-COT26 | OFICINA | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | coincidencia_posible |
| 1211-117-COT26 | TECNOLOGIA | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | coincidencia_posible | coincidencia_confirmada |
| 1211-117-COT26 | SALUD | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1211-117-COT26 | ALIMENTOS | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1211-117-COT26 | ASEO | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1211-117-COT26 | TEXTIL | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1211-117-COT26 | MANTENCION | 26111702, 26111704, 26121630, 32101622, 43211708, 52161512, 52161520, 60104906 | no_relevante | no_relevante |
| 1018-88-COT26 | CONSTRUCCION | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | coincidencia_posible | coincidencia_confirmada |
| 1018-88-COT26 | OFICINA | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | no_relevante | no_relevante |
| 1018-88-COT26 | TECNOLOGIA | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | no_relevante | no_relevante |
| 1018-88-COT26 | SALUD | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | coincidencia_posible | no_relevante |
| 1018-88-COT26 | ALIMENTOS | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | no_relevante | no_relevante |
| 1018-88-COT26 | ASEO | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | coincidencia_posible | no_relevante |
| 1018-88-COT26 | TEXTIL | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | coincidencia_posible | no_relevante |
| 1018-88-COT26 | MANTENCION | 26111702, 27112801, 31211501, 31211904, 31211906, 39101608, 47121612, 53102504 | no_relevante | coincidencia_posible |
| 1057498-2745-COT26 | CONSTRUCCION | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | OFICINA | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | TECNOLOGIA | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | SALUD | 49181612 | no_relevante | coincidencia_confirmada |
| 1057498-2745-COT26 | ALIMENTOS | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | ASEO | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | TEXTIL | 49181612 | no_relevante | no_relevante |
| 1057498-2745-COT26 | MANTENCION | 49181612 | no_relevante | no_relevante |
| 1662-1583-COT26 | CONSTRUCCION | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | OFICINA | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | TECNOLOGIA | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | SALUD | 53131609 | no_relevante | coincidencia_posible |
| 1662-1583-COT26 | ALIMENTOS | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | ASEO | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | TEXTIL | 53131609 | no_relevante | no_relevante |
| 1662-1583-COT26 | MANTENCION | 53131609 | no_relevante | no_relevante |
| 5052-498-COT26 | CONSTRUCCION | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 5052-498-COT26 | OFICINA | 26111702, 52151504, 52151704 | no_relevante | coincidencia_posible |
| 5052-498-COT26 | TECNOLOGIA | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 5052-498-COT26 | SALUD | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 5052-498-COT26 | ALIMENTOS | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 5052-498-COT26 | ASEO | 26111702, 52151504, 52151704 | no_relevante | coincidencia_posible |
| 5052-498-COT26 | TEXTIL | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 5052-498-COT26 | MANTENCION | 26111702, 52151504, 52151704 | no_relevante | no_relevante |
| 2859-1467-COT26 | CONSTRUCCION | — | abstencion | no_relevante |
| 2859-1467-COT26 | OFICINA | — | abstencion | no_relevante |
| 2859-1467-COT26 | TECNOLOGIA | — | abstencion | no_relevante |
| 2859-1467-COT26 | SALUD | — | abstencion | no_relevante |
| 2859-1467-COT26 | ALIMENTOS | — | abstencion | coincidencia_posible |
| 2859-1467-COT26 | ASEO | — | abstencion | no_relevante |
| 2859-1467-COT26 | TEXTIL | — | abstencion | no_relevante |
| 2859-1467-COT26 | MANTENCION | — | abstencion | no_relevante |
| 1058045-625-COT26 | CONSTRUCCION | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | OFICINA | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | TECNOLOGIA | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | SALUD | 42192604 | coincidencia_confirmada | no_relevante |
| 1058045-625-COT26 | ALIMENTOS | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | ASEO | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | TEXTIL | 42192604 | no_relevante | no_relevante |
| 1058045-625-COT26 | MANTENCION | 42192604 | no_relevante | no_relevante |
| 5066-280-COT26 | CONSTRUCCION | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | OFICINA | 82121507 | coincidencia_confirmada | coincidencia_posible |
| 5066-280-COT26 | TECNOLOGIA | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | SALUD | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | ALIMENTOS | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | ASEO | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | TEXTIL | 82121507 | no_relevante | no_relevante |
| 5066-280-COT26 | MANTENCION | 82121507 | no_relevante | no_relevante |
| 2102-579-COT26 | CONSTRUCCION | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | OFICINA | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | TECNOLOGIA | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | SALUD | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | ALIMENTOS | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | ASEO | 31261501 | no_relevante | coincidencia_posible |
| 2102-579-COT26 | TEXTIL | 31261501 | no_relevante | no_relevante |
| 2102-579-COT26 | MANTENCION | 31261501 | no_relevante | no_relevante |
| 525800-471-COT26 | CONSTRUCCION | — | abstencion | no_relevante |
| 525800-471-COT26 | OFICINA | — | abstencion | no_relevante |
| 525800-471-COT26 | TECNOLOGIA | — | abstencion | no_relevante |
| 525800-471-COT26 | SALUD | — | abstencion | no_relevante |
| 525800-471-COT26 | ALIMENTOS | — | abstencion | no_relevante |
| 525800-471-COT26 | ASEO | — | abstencion | no_relevante |
| 525800-471-COT26 | TEXTIL | — | abstencion | no_relevante |
| 525800-471-COT26 | MANTENCION | — | abstencion | no_relevante |
| 5067-2842-COT26 | CONSTRUCCION | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | OFICINA | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | TECNOLOGIA | 43201549 | coincidencia_confirmada | coincidencia_confirmada |
| 5067-2842-COT26 | SALUD | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | ALIMENTOS | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | ASEO | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | TEXTIL | 43201549 | no_relevante | no_relevante |
| 5067-2842-COT26 | MANTENCION | 43201549 | no_relevante | no_relevante |

## Próximo paso
1. Obtener/validar un catálogo oficial UNSPSC de categorías y equivalencias por perfil, **antes** de llamar a este diagnóstico "método A".
2. Generar predicciones B y C con versiones registradas y sin acceso a etiquetas humanas; **no reutilizar** la `propuesta_ia` histórica como si fuera salida independiente de B o C.
3. Separar pertinencia al catálogo y oportunidad comercial secundaria para una evaluación compatible con el objetivo del producto.
4. Ejecutar D solo para ambiguos que verdaderamente requieran adjuntos, con registro de coste y evidencias.

No hay cambios en `main`, monitores ni Supabase.