# FARO-100 · Diseño del clasificador v2: cobertura integral en Compra Ágil

**Estado:** especificación experimental, NO código desplegado. **Fecha:** 2026-11-25. **Rama:** `experimento/faro-100-muestra-20261122`.

## Contexto y trazabilidad
- Reutiliza `perfiles_proveedor.md`, `protocolo_etiquetado.md`, `piloto15_etiquetado.csv`, `holdout85_A0_B1_C1_resultados.md` y las auditorías locales de los 60 pares evaluados por Claude.
- Las etiquetas A0/B1/C1 y 120 juicios humanos permanecen intactos. Las 60 etiquetas de Claude son **segunda evaluación de IA**, no nuevas etiquetas humanas. Claude tuvo acceso a anexos que no están en el Excel y esta auditoría no los verificó de manera independiente.
- **Regla de negocio central:** para Compra Ágil se cotiza el requerimiento completo. La afinidad con solo un subconjunto de ítems NO habilita recomendarla como cotizable. *No interpretar el porcentaje de ítems coincidentes como posibilidad de oferta parcial.*
- Este diseño no presume inventarios ni capacidades reales de los ocho proveedores ficticios. Una capacidad no declarada es **desconocida**, salvo exclusión explícita del perfil.
- El objetivo de la nueva versión no es reetiquetar a posteriori los resultados históricos; es ensayar una dimensión adicional de decisión.

## Datos necesarios por compra
`codigo`, `tipo_compra=COMPRA_AGIL`, `titulo`, `descripcion`, `items[]`, `servicios[]`, `requisitos_transversales[]`, `anexos_revisados[]`, `fuentes[]`.

Cada elemento obligatorio incluye `id`, `descripcion`, `cantidad`, `unidad`, `es_obligatorio` (en Compra Ágil, todos los ítems del requerimiento son obligatorios a efectos de cotización), y cuando exista `especificaciones_tecnicas`. Un servicio puede incluir instalación, montaje, entrega o certificación; los insumos de un servicio no convierten el contrato en una mera venta de materiales.

Cuando los productos estructurados son insuficientes, reconstruir las prestaciones desde título, descripción y anexos. **No inferir que la lista estructurada está completa**.

## Datos necesarios por proveedor (perfil real)
- `catalogo_habitual[]` (bienes y servicios realmente ofrecidos), `abastecimiento_por_encargo` con alcance explícito, `capacidades_servicio[]`, `exclusiones[]`.
- `habilitaciones[]`, compatibilidad de marcas/equipos, `capacidad_logistica` (despacho, región, volumen y plazo) y `restricciones[]`.
- `ultima_confirmacion` y `fuente_capacidad`: declaración de cliente, documentación comercial, historial Mercado Público u otra. El historial público solo **sugiere** capacidad, no la acredita automáticamente; el cliente debe confirmar.
- Los perfiles ficticios FARO-100 no incluyen necesariamente estos campos; usar `desconocido` cuando no están definidos.

## Dos dimensiones INDEPENDIENTES
1. **Afinidad comercial del requerimiento:** `directa`, `adyacente`, `no_relacionada`, `indeterminada`. Describir por qué podría interesarle a ese proveedor, sin inferir viabilidad.
2. **Cobertura integral:** `confirmada`, `posible_por_verificar`, `desconocida`, `imposible`. Evaluar **todos** los ítems y condiciones obligatorias, no contar solo palabras coincidentes.

### Cobertura por ítem o prestación
`directa`: capacidad acreditada con la declaración vigente del cliente y evidencia del ítem.
`por_encargo_confirmada`: el cliente confirma capacidad de conseguir ese artículo concreto, cantidad y plazo; no basta habilitar una casilla genérica "todólogo".
`por_encargo_por_verificar`: canal plausible, falta confirmación concreta.
`desconocida`: sin antecedentes para resolver.
`no_cubierta`: exclusión expresa o incapacidad conocida para el elemento o condición.

Aplicar también condiciones transversales: certificaciones, instalación, servicio, marca compatible, cobertura geográfica, plazo, logística, cantidades, permisos. La evidencia de afinidad no sustituye estas verificaciones.

### Agregación integral obligatoria
- Si **cualquier** ítem o requisito obligatorio es `no_cubierta` ⇒ `cobertura_integral=imposible`.
- Si **todos** los elementos obligatorios son `directa` o `por_encargo_confirmada` y se verificaron requisitos ⇒ `confirmada`.
- Si ninguno es `no_cubierta` y **alguno** es `por_encargo_por_verificar`, con inventario suficiente del resto ⇒ `posible_por_verificar`.
- Si faltan elementos, adjuntos importantes o especificaciones necesarias, o se desconoce alguna capacidad esencial ⇒ `desconocida`; nunca forzar `no_relacionada`.
- Las palabras "confirmada" en el ensayo son solo respecto de datos del **perfil declarado**: no constituyen certificación independiente de existencias, precio u ofertas admisibles.

## Salida para alertas
| Afinidad | Cobertura | Resultado FARO v2 |
|---|---|---|
| directa/adyacente | confirmada | `recomendable` (distinguir directa o adyacente en explicación) |
| directa/adyacente | posible_por_verificar | `consultar_cliente` antes de presentar como cotizable |
| directa/adyacente | desconocida | `pendiente_informacion`, solicitar detalle/anexo o perfil |
| cualquiera | imposible | `descartar_no_cotizable`, registrar ítem/requisito bloqueante |
| no_relacionada | otra distinta de imposible | `no_priorizar`; evitar confundir desinterés con incapacidad |

Se recomienda una **alerta de oportunidad secundaria** solo si la cobertura integral es `confirmada` o `posible_por_verificar`, con etiqueta explícita de incertidumbre. Nunca presentar `posible_por_verificar` como compra lista para cotizar.

## Algoritmo conceptual (sin acceso a predicciones humanas)
1. Cargar detalle y adjuntos **una vez por código** cuando sean necesarios. Extraer lista integral de bienes y prestaciones, mantener fuente y confianza.
2. Cruzar cada elemento con capacidad y exclusiones del proveedor. No utilizar UNSPSC como verdad ni descarte automático.
3. Aplicar requisitos transversales a todo el contrato; una instalación requerida no puede confundirse con suministro de sus materiales.
4. Calcular cobertura integral mediante reglas anteriores; derivar afinidad en eje separado.
5. Emitir salida explicable con `items_bloqueantes[]`, `items_a_confirmar[]`, `evidencias[]`, `fuentes[]`, `version_reglas` y `requiere_revision`.

## Casos de aceptación obligatorios (sin convertir la segunda evaluación de Claude en verdad)
- **10 ítems, 9 cubiertos, uno expresamente excluido:** `imposible`, `descartar_no_cotizable`.
- **10 ítems, 9 cubiertos, uno conseguible por encargo no confirmado:** `posible_por_verificar`, `consultar_cliente`; no "90 % cotizable".
- **10 ítems, todos cubiertos, despacho/región/certificación incompatibles:** `imposible`, registrar barrera concreta.
- **Compra de instalación de redes con tuberías:** proveedor que solo vende tuberías ⇒ `imposible` si no ejecuta el servicio.
- **Compra con alimentos y catering:** proveedor ALIMENTOS v1 sin cocina/catering ⇒ `imposible` para el perfil congelado.
- **Compra dental mixta con anestésicos farmacológicos:** perfil SALUD v1 sin medicamentos ⇒ `imposible`.
- **Merchandising mixto con artículos no textiles:** TEXTIL v1 ⇒ `desconocida` si la comercialización fuera del catálogo no consta; `imposible` solo si hay exclusión/incapacidad documentada; no confirmada.
- **Ítems solo en adjunto no accesible:** `desconocida`, no declarar cobertura integral.
- **UNSPSC incompatible con descripción explícita:** prevalece evidencia de texto/documento; registrar conflicto.
- **Proveedor todólogo:** permitir venta multirrubro y por encargo **solo dentro de capacidades/alcances que el cliente declare o confirme**; sin permisividad general automática.

## Medición experimental y siguientes pasos
1. Crear prueba v2 con **capacidad declarada congelada** de los ocho perfiles y ficha integral de las compras; separar evidencia confirmada por el usuario de interpretación de anexos por otra IA.
2. Aplicar casos de aceptación sintéticos controlados antes de comparar la muestra real.
3. Evaluar en forma ciega y con revisión humana focalizada; etiquetar por separado `afinidad`, `cobertura_integral`, `barrera`. No mezclar las etiquetas históricas de pertinencia con nuevas etiquetas v2.
4. Informar tasa de falsos recomendables (compras con ítem bloqueante), tasa de abstenciones, posibles pérdidas y coste/latencia. No calcular precisión poblacional con las 60 filas seleccionadas deliberadamente.
5. Solo después integrar al formulario existente y planificar código en rama experimental. Sin cambios a `main`, Supabase ni automatizaciones de producción.

**Estado del archivo:** propuesta de arquitectura y criterios; aún NO se ha implementado ni ejecutado el clasificador v2.
