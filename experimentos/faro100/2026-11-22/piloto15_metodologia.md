# FARO-100 · Piloto 15 compras, selección v1

**Estado: 120 propuestas de IA añadidas al CSV existente el 22-11-2026; 1 etiqueta humana guiada registrada (caso 1/6), 119 pendientes y todavía NO hay resultados de los métodos A–D.**

## Objetivo y alcance
- 15 compras **extraídas de la muestra congelada de 100**, sin nuevas consultas a Supabase.
- 5 del estrato `titulo_extenso`, 5 de `titulo_breve_o_generico` y 5 de `aleatorio`.
- 8 perfiles congelados en `perfiles_proveedor.md`; **120 pares compra-perfil**.
- Selección deliberada por utilidad diagnóstica, **no aleatoria ni representativa**. No usar tasas del piloto para estimar desempeño poblacional.
- `piloto15_seleccion.csv`: copia de las 15 filas originales, con sus identificadores y metadatos intactos.
- `piloto15_etiquetado.csv`: copia de los 120 pares de la plantilla original, con campos de juicio en blanco.
- Los detalles JSON ya descargados están en el artefacto del run https://github.com/mgarcia1306/fap/actions/runs/44987485178. No volver a solicitar los 100.
- El caso Bulnes tiene dos PDF recuperados en https://github.com/mgarcia1306/fap/actions/runs/44990431115.

## Casos y por qué se eligieron

| Nº original | Código | Estrato | Motivo diagnóstico |
|---:|---|---|---|
| 3 | 3904-1092-COT26 | titulo_extenso | Título sugiere indumentaria, pero productos y adjunto confirman protectores solares |
| 4 | 3145-615-COT26 | titulo_extenso | UNSPSC Cabañas frente a servicio de instalación de redes de agua |
| 9 | 1075337-2243-COT26 | titulo_extenso | Descalcificador EDTA clínico con código de hemacitometría; adjunto DOCX técnico |
| 10 | 2771-694-COT26 | titulo_extenso | Publicidad/difusión sin productos estructurados; especificaciones solo en adjuntos |
| 29 | 1211-117-COT26 | titulo_extenso | Compra mixta de baterías, periféricos y audio bajo rótulo tecnológico |
| 42 | 1018-88-COT26 | titulo_breve_o_generico | Ferretería general con nueve líneas y códigos de rubros diversos |
| 43 | 1057498-2745-COT26 | titulo_breve_o_generico | Paño clínico estéril codificado como delimitador de tiro con arco |
| 47 | 1662-1583-COT26 | titulo_breve_o_generico | Protector solar claro; caso de control frente a compra de Bulnes |
| 58 | 5052-498-COT26 | titulo_breve_o_generico | Compra mixta de pilas, vasos y cucharas; evitar asumir alimentos |
| 62 | 2859-1467-COT26 | titulo_breve_o_generico | Coffee break sin productos; distinguir abastecimiento de servicio preparado |
| 78 | 1058045-625-COT26 | aleatorio | Medicamento levosulpirida codificado como accesorio de administración |
| 81 | 5066-280-COT26 | aleatorio | Servicio de impresión; alcance real de proveedor de papelería requiere revisión |
| 88 | 2102-579-COT26 | aleatorio | Contenedores para central de alimentación, pero no alimentos |
| 93 | 525800-471-COT26 | aleatorio | Reparación de ascensores sin productos; habilitación técnica especializada |
| 98 | 5067-2842-COT26 | aleatorio | Switch administrable; caso de control para tecnología |

## Procedimiento: evitar contaminar la verdad de referencia
1. Leer `perfiles_proveedor.md` sin modificarlo.
2. Revisar cada título, descripción y lista de productos del detalle original. **No utilizar el código UNSPSC como criterio de verdad**.
3. Etiquetar cada uno de los 120 pares con una de las cuatro etiquetas del `protocolo_etiquetado.md`: `coincidencia_confirmada`, `coincidencia_posible`, `informacion_insuficiente` o `no_relevante`. Justificar con evidencia.
4. Revisar adjuntos **solo si pueden cambiar una etiqueta o aclarar una ambigüedad**. Registrar archivo y sección. Por ejemplo, Bulnes se confirmó mediante `OP26-1628.pdf`.
5. Registrar conflictos UNSPSC **después de fijar la etiqueta semántica**.
6. Ejecutar los métodos A, B, C y D **por separado y sin acceso a etiquetas humanas**. Guardar predicciones y versiones; comparar recién al final.
7. Medir falsos negativos, falsos positivos y abstenciones con denominadores claros. Separar casos posibles/insuficientes.

## Advertencias de interpretación
- Un insumo utilizado en un hospital **no es automáticamente relevante para SALUD**.
- Un recipiente para cocina **no equivale a un alimento para ALIMENTOS**.
- Un servicio de catering **no equivale a suministro de alimentos envasados**.
- Una obra que incluye materiales **no es una venta de materiales de ferretería**.
- Un proveedor de mantención general **no necesariamente puede reparar ascensores**.
- No confundir pertinencia semántica con elegibilidad comercial, plazo, región o certificaciones.

**Próximo hito:** revisar y auditar las 120 etiquetas; luego comparar A–D. No alterar la rama `main`, monitores ni Supabase.

## Avance comprobado: preevaluación de IA (22-11-2026)
- Se añadieron cinco columnas **al CSV existente** `piloto15_etiquetado.csv`: `propuesta_ia`, `fuente_propuesta_ia`, `fundamento_propuesta_ia`, `adjunto_pendiente_ia`, `estado_validacion_ia`.
- Balance preliminar de **120 pares**: 3 `coincidencia_confirmada`, 4 `coincidencia_posible`, 2 `informacion_insuficiente`, 111 `no_relevante`. Son **propuestas de IA**, no etiquetas humanas, ni desempeño de los métodos A–D.
- Las **120 celdas** `etiqueta_humana` se conservaron vacías, así como los campos originales de referencia humana y UNSPSC. No confundir una propuesta con verdad de referencia.
- Fuente analizada: 15 respuestas reales en el ZIP del run `44987485178` (título, descripción, productos); para `3904-1092-COT26` se reutilizó el PDF `OP26-1628.pdf` revisado anteriormente. **No se descargaron más adjuntos**.
- Revisar primero seis pares con etiquetas posibles/insuficientes: `3145-615-COT26`/MANTENCION; `1075337-2243-COT26`/SALUD; `2771-694-COT26`/OFICINA y TEXTIL; `1211-117-COT26`/TECNOLOGIA; `5066-280-COT26`/OFICINA.
- Validar también las tres confirmaciones: `1018-88-COT26`/CONSTRUCCION; `1057498-2745-COT26`/SALUD; `5067-2842-COT26`/TECNOLOGIA. Auditar una muestra de los 111 descartes, porque un error allí sería precisamente un falso negativo.
- **No calcular todavía porcentajes de falsos negativos ni precisión de FARO**: faltan etiquetas independientes y salidas de métodos A–D.

## Decisión conversacional 1/6 (22-11-2026)
- `3145-615-COT26` / `MANTENCION` = `coincidencia_posible` según la usuaria, con razonamiento plomería/instalación y límite de capacidades reales.
- Revisar el caso como **revisión guiada**: el control UI tenía preseleccionada esa misma etiqueta. Para una prueba verdaderamente ciega, la segunda revisión debería ocultar propuestas y etiquetas por defecto.
- Códigos reportados por la usuaria: `721511`, `721515`, `7215`; no se validaron aquí. Códigos del producto observado: `30201603` y `40101825`.

## Decisión conversacional 2/6 (22-11-2026)
- `1075337-2243-COT26` / `SALUD` = `coincidencia_posible`, elegida por usuaria en control sin opción preseleccionada.
- Razonamiento: descalcificador EDTA para muestras de laboratorio no equivale a insumo clínico básico (mascarillas, guantes o jeringas), aunque en términos generales se relaciona con salud.
- Ficha de especificaciones `592 DESCALCIFICADOR (1).docx` identificada, pero no revisada. El código UNSPSC observado `42181504` corresponde a Sets de hemacitometría y no define la relevancia.
- 2/120 etiquetas humanas registradas; 118 pendientes. Próximo par `2771-694-COT26` / `OFICINA`.

## Decisión conversacional 3/6 (22-11-2026)
- `2771-694-COT26` / `OFICINA` = `informacion_insuficiente`, decisión humana sin preselección.
- Motivo: rubro de insumos de oficina no confirma equipamiento de impresión para publicidad (pendones/gigantografías); faltan productos exactos en `ESPECIFICACIONES TÉCNICAS.pdf`. La tercerización podría habilitar este trabajo, pero no está definida como capacidad del perfil.
- Propuesta para futuro, **no implementar aún**: apartado de compras de interés potencial por rubros afines / servicios especializados y pregunta opcional sobre tercerización en la ficha del cliente. Evitar contaminar las capacidades congeladas del experimento.
- 3/120 etiquetas humanas registradas; siguiente `2771-694-COT26` / `TEXTIL`.

## Adjunto de Chiguayante leído después de decisiones iniciales (22-11-2026)
- Archivo externo aportado por la usuaria: `ESPECIFICACIONES TÉCNICAS.pdf`, 6 páginas, pp. 1-2 listado y p. 3 §3.2 integralidad.
- Comprobado: 2 manteles corporativos impresos, 1.600 bolsas TNT serigrafiadas y 100 morrales impresos, **más** 300 libretas, 1.200 imanes, 1.000 chapitas, 1 stand, 235 botellas deportivas y 5.000 dípticos.
- El requerimiento exige oferta total (100% de partidas) y se factura en tres lineamientos; esto no equivale a permitir postulación parcial.
- Preservar la `propuesta_ia` original, construida sin leer este documento, para medir el aporte de adjuntos sin fuga de información. Evidencia posterior separada en columnas de trazabilidad del CSV.
- No alterar sin revisión explícita de la usuaria las etiquetas humanas ya asignadas; `OFICINA` requiere posible reconsideración y `TEXTIL` permanece pendiente.
