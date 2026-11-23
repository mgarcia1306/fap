# ESTADO DEL PROYECTO · FARO (repositorio fap)

**Última revisión documental:** 2026-11-22  
**Ámbito:** `mgarcia1306/fap`, rama `experimento/faro-100-muestra-20261122`.  
**Regla de seguridad:** no modificar `main`, monitores, automatizaciones ni Supabase sin autorización explícita. Este archivo describe estados **verificados** y distingue pendientes.

## 1. Operación del monitor (contexto, no intervenir)

- El repositorio `fap` es el monitor experimental de Compra Ágil v2 y persiste en Supabase `radar_faro`. El README del repositorio indica que **no envía correos**.
- Procesos descritos en `README.md`: `.github/workflows/actualidad.yml` (ventana de cambios), `.github/workflows/supabase_piloto.yml` (recuperación histórica) y diagnóstico manual. **Su presencia en el código no equivale a verificación de salud operativa en tiempo real**.
- `CLASIFICACION_OPORTUNIDADES.md` documenta una vista de elegibilidad por plazo y estado, distinta de la clasificación **semántica** por perfil comercial.
- `PILOTO_CONTINUO.md` documenta la cohorte iniciada el 2026-11-20 a las 18:51, hora de Chile, con ingesta prevista cada ~15 minutos. No se han ejecutado cambios de producción para preparar este estado.

## 2. Auditoría UNSPSC anterior (archivo de usuario; NO es la muestra nueva del repositorio)

**Archivos existentes:**
- `FARO-100-auditoria.xlsx`: auditoría de 301 líneas de productos, correspondientes a 88 compras con líneas; según el trabajo previo, 12 compras adicionales no tenían líneas de productos.
- `FARO-100-revision-adjuntos.csv`: resolución documental de las 12 líneas que quedaron inicialmente como evidencia insuficiente.

**Resultado inicial verificado directamente en el XLSX:**

| Evaluación UNSPSC | Líneas |
|---|---:|
| Compatible | 109 |
| Parcial o imprecisa | 111 |
| Discordancia clara | 69 |
| Evidencia insuficiente | 12 |
| **Total** | **301** |

**Revisión de las 12 líneas con adjuntos, verificada en CSV:** 1 compatible, 9 parciales o imprecisas, 2 discordancias claras. **Resultado consolidado:** 110 compatibles, 120 parciales o imprecisas, 71 discordancias claras, 0 insuficientes entre esas 301 líneas (71/301 = 23,6 %). La auditoría **mide calidad de correspondencia UNSPSC**, NO relevancia comercial ni falsos negativos de FARO.

**Ubicación:** estos dos archivos están disponibles como archivos previos de la conversación/proyecto; **no se comprobó que estén versionados dentro del repositorio**. No recrearlos ni sobrescribirlos por defecto.

## 3. Muestra nueva FARO-100 en GitHub (otro conjunto experimental)

**Carpeta:** `experimentos/faro100/2026-11-22/`

- `muestra_faro100.csv`: selección congelada de 100 compras reales desde Supabase; estratos 30 títulos extensos / 40 breves o genéricos / 30 restantes.
- `perfiles_proveedor.md`: 8 perfiles hipotéticos, de alcance específico (CONSTRUCCION, OFICINA, TECNOLOGIA, SALUD, ALIMENTOS, ASEO, TEXTIL, MANTENCION).
- `plantilla_etiquetado.csv`: 800 pares compra-perfil **sin etiquetas humanas**.
- `protocolo_etiquetado.md`: criterios para evaluar pertinencia y comparar métodos A–D.
- Detalles completos de **100/100** compras recuperados en [GitHub Actions #44987485178](https://github.com/mgarcia1306/fap/actions/runs/44987485178).
- Descarga y lectura de **2/2 PDF** del caso Bulnes `3904-1092-COT26` en [GitHub Actions #44990431115](https://github.com/mgarcia1306/fap/actions/runs/44990431115). El título parecía pedir indumentaria, pero los PDF especifican protectores solares faciales, corporales y labiales.
- `piloto15_seleccion.csv`, `piloto15_etiquetado.csv` y `piloto15_metodologia.md` ya existen en la rama experimental. La selección de 15 proviene de la muestra nueva. El 22-11-2026 se añadieron **120 propuestas de IA** en cinco columnas nuevas sin completar ninguna etiqueta humana en ese paso; **posteriormente, la usuaria asignó una etiqueta al caso 1/6**. **No abrir una tercera muestra ni duplicar planillas.**
- El `README.md` de la carpeta conserva algunas frases históricas sobre descargas pendientes: interpretarlas según los hitos de ejecución confirmados arriba.

**Cruce de códigos verificado el 2026-11-22:** los **88 códigos** con líneas de la auditoría original y los **100 códigos** de la muestra nueva tienen **0 coincidencias**. Los 12 casos originales sin líneas no están incluidos en el XLSX auditado; no se verificó su identidad aquí. No fusionar denominadores ni trasladar automáticamente etiquetas entre muestras.

## 4. Qué falta realmente

1. **Cruzar la auditoría previa con los 8 perfiles de proveedor**, sin confundir correspondencia UNSPSC con relevancia comercial. Partir por los casos de adjuntos ya resueltos; no volver a descargarlos.
2. **Validar** las 120 propuestas de pertinencia por par compra-perfil —registradas el 22-11-2026, aún **NO** son etiquetas humanas— usando evidencia, límites de catálogo y revisión de casos dudosos. No compararlas como referencia oficial antes de validar.
3. **Cruce parcial completado:** 0 coincidencias entre los 88 códigos auditados y los 100 de la nueva muestra. Si se recupera el manifiesto completo de la cohorte original (incluidos los 12 sin líneas), verificar también esos 12; no asumir identidad de cohortes.
4. Ejecutar métodos A (solo UNSPSC), B (texto y productos), C (B + detección de conflicto UNSPSC), D (C + adjuntos selectivos) **sin mirar las etiquetas humanas**.
5. Medir falsos negativos, falsos positivos, abstenciones, esfuerzo y oportunidades únicas afectadas. Los 301 productos auditados no equivalen a 301 oportunidades ni a 301 pares compra-perfil.
6. Validar métricas antes de conectar clasificación a alertas de clientes.

## 5. Primer cruce semántico: 10 compras, 12 líneas con adjuntos (preliminar)

Se revisaron los **10 códigos únicos** que aparecen en `FARO-100-revision-adjuntos.csv` (12 líneas) y se contrastaron con los ocho perfiles ya definidos. **Son candidatos de pertinencia, no etiquetas humanas finales ni métricas de falsos negativos**.

| Compra | Candidato(s) de perfil | Motivo / límite |
|---|---|---|
| `1175-502-COT26` | SALUD **por verificar** | Maletines de atención domiciliaria; el perfil cubre insumos/equipamiento clínico básico, pero no declara expresamente bolsos de transporte. |
| `1962-386-COT26` | Ninguno claro | Sillas de oficina; el perfil OFICINA actual incluye papelería y suministros, **no mobiliario**. |
| `2287-741-COT26` | OFICINA | Marcadores, papeles y útiles; también hay materiales de manualidades, por lo que debe verificarse cobertura del conjunto. |
| `2675-394-COT26` | Ninguno claro | Balizas y equipamiento para vehículos; no se definió proveedor de accesorios automotrices. |
| `3152-314-COT26` | CONSTRUCCION **posible** | Insumos para mantención, enchufes, cable y otros; mezcla con calzado de seguridad y artículos fuera de catálogo. |
| `3945-69-COT26` | ASEO **posible/parcial** | Jabón mecánico y paños de limpieza, junto con soldadura y acoples; no asumir suministro del paquete completo. |
| `4455-357-COT26` | TECNOLOGIA | Proyector, televisor, notebook y Office; parte del pedido incluye materiales de laboratorio fuera del perfil. |
| `5060-1131-COT26` | OFICINA **posible/parcial** | Carpetas, cuadernos y láminas, además de témperas y material de enseñanza. |
| `557639-3693-COT26` | OFICINA **posible/parcial** | Tijeras, cartulinas y pegamento; mezcla de material didáctico. |
| `736812-99-COT26` | Ninguno claro | Cantantes, grupos musicales y danza; no hay perfil de producción artística. |

**Balance descriptivo:** 7 compras con al menos un perfil candidato, **3 sin perfil claro**. Este balance no mide rendimiento del algoritmo: todavía no se aplicó la matriz completa de etiquetas por par.

## 6. Próxima acción concreta

**Hito confirmado:** el primer cruce de las 12 líneas auditadas con adjuntos ya figura arriba. **Hito del piloto nuevo:** 120 pares revisados preliminarmente por IA (111 no relevantes, 4 posibles, 2 insuficientes, 3 confirmados), con **4 etiquetas humanas registradas** (casos 1 a 4/6) y 116 restantes vacías. **Siguiente acción:** revisión humana independiente empezando por los 6 pares dudosos/insuficientes y 3 confirmados, y muestreo de descartes; consultar adjuntos que efectivamente podrían cambiar la decisión. Solo tras validación, comparar A–D. No crear una nueva plantilla.

---
**Principio de continuidad:** revisar primero, reutilizar lo existente, ejecutar después. Una ejecución exitosa de GitHub Actions no equivale por sí sola a cobertura completa ni a precisión de clasificación validada.

## 7. Validación conversacional guiada (22-11-2026)
- **Caso 1/6 revisado:** `3145-615-COT26` / perfil `MANTENCION` = `coincidencia_posible`, decisión explícita de la usuaria; documentada en `piloto15_etiquetado.csv`. Considera servicios de plomería/instalación y la posible interacción con sistemas eléctricos en termos.
- La usuaria citó rangos/familias UNSPSC `721511`, `721515` y `7215` a partir de su investigación (su correspondencia exacta **no fue verificada externamente** en este registro). Los códigos realmente presentes en el JSON fueron `30201603` (Cabañas) y `40101825` (Calentadores de agua de uso doméstico).
- **Cautela metodológica:** la pregunta original traía `coincidencia_posible` preseleccionada; por tanto, esta decisión es una **revisión guiada, no ciega**. No tratar las seis decisiones guiadas como referencia independiente perfecta al evaluar métodos A–D; exigir una segunda revisión independiente si se necesita evaluación ciega.
- **Caso 2/6 revisado:** `1075337-2243-COT26` / `SALUD` = `coincidencia_posible`, porque un producto especializado de laboratorio puede exceder el catálogo de insumos clínicos básicos. Ficha `592 DESCALCIFICADOR (1).docx` pendiente de revisar. Control de opción sin etiqueta preseleccionada.
- **Caso 3/6 revisado:** `2771-694-COT26` / `OFICINA` = `informacion_insuficiente`, decisión explícita de la usuaria: publicidad puede exigir impresión especializada (pendones, gigantografías) y el proveedor de insumos de oficina no necesariamente dispone de ella; podría tercerizar, capacidad no definida. Requerimientos en adjunto por revisar.
- **Idea de producto (NO implementada):** valorar un bloque secundario de alertas para rubros afines o servicios especializados y preguntar al cliente si puede/acepta subcontratar. Mantener perfiles y correos existentes sin cambios hasta definir alcance y probarlo.
- **Progreso histórico (antes de leer adjunto):** 3/120 etiquetas humanas rellenadas. La decisión de TEXTIL se registra en el hito posterior de la sección 9.

## 8. Adjunto incorporado al caso 4/6 (22-11-2026)
- **Archivo aportado:** `ESPECIFICACIONES TÉCNICAS.pdf`, seis páginas, compra `2771-694-COT26`; revisados listados de pp. 1 y 2 y cláusula de integridad de la oferta en p. 3.
- **Hallazgo semántico:** existen 2 manteles corporativos, 1.600 bolsas TNT en dos formatos y 100 mochilas tipo morral personalizadas, además de 300 libretas ecológicas, 1.200 imanes, 1.000 chapitas, 1 stand, 235 botellas y 5.000 dípticos. **Sí hay artículos de interés para TEXTIL y OFICINA, pero la compra es multirrubro.**
- **Condición esencial:** la cláusula 3.2 exige cotizar el **100 %** de las partidas mínimas; no basta con ofrecer solo textiles o solo impresos. No existe evidencia en este documento de que se acepten propuestas parciales. Facturas separadas por lineamiento no prueban adjudicación separada.
- **Registro:** evidencia añadida a `piloto15_etiquetado.csv` en columnas **posteriores**, preservando las 120 propuestas originales y las 3 decisiones humanas ya registradas. **Caso TEXTIL etiquetado posteriormente por la usuaria como `coincidencia_posible`**. Caso OFICINA conserva `informacion_insuficiente` hasta que la usuaria lo reconsidere con la nueva evidencia.
- **Siguiente pregunta:** revisar con la usuaria el caso 4/6 `2771-694-COT26`/`TEXTIL`, considerando pertinencia parcial frente a obligación de cobertura integral y posibilidad de tercerización no acreditada.

## 9. Decisión conversacional 4/6 (22-11-2026)
- **Compra:** `2771-694-COT26`, perfil `TEXTIL` = `coincidencia_posible`, elegida expresamente por la usuaria después de revisar el PDF de especificaciones.
- **Justificación:** manteles, 1.600 bolsas TNT y 100 mochilas morral personalizados tienen afinidad textil/promocional, pero libretas, chapitas, imanes, stand, botellas y dípticos podrían exceder el catálogo. La tercerización es una posibilidad comercial por verificar, no capacidad demostrada.
- **Limitación determinante:** §3.2, p.3, exige cotizar el 100% de las partidas de la compra; afinidad parcial **no** implica admisibilidad de una oferta parcial.
- Registrados evidencia, fundamento y referencia del adjunto en `piloto15_etiquetado.csv`, sin alterar la propuesta original de IA. **Progreso: 4/120 etiquetas humanas registradas, 116 pendientes**.
- **Siguiente caso 5/6:** `1211-117-COT26` / `TECNOLOGIA`. La revisión de `OFICINA` sobre la compra de Chiguayante continúa con etiqueta anterior hasta que la usuaria decida si la modifica.
