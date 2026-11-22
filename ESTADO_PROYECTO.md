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
- `piloto15_seleccion.csv`, `piloto15_etiquetado.csv` y `piloto15_metodologia.md` ya fueron creados en la rama experimental. El piloto de 15 es **una selección derivada de esta muestra nueva**, no una repetición literal demostrada de las 100 compras auditadas anteriormente. Sus 120 etiquetas siguen vacías. **No abrir una tercera muestra ni duplicar planillas.**
- El `README.md` de la carpeta conserva algunas frases históricas sobre descargas pendientes: interpretarlas según los hitos de ejecución confirmados arriba.

**Precaución:** la auditoría anterior y la muestra nueva se originaron en selecciones diferentes; no fusionar sus denominadores ni trasladar automáticamente etiquetas entre compras. Si un código aparece en ambos conjuntos, reutilizar la evidencia por código y registrar procedencia.

## 4. Qué falta realmente

1. **Cruzar la auditoría previa con los 8 perfiles de proveedor**, sin confundir correspondencia UNSPSC con relevancia comercial. Partir por los casos de adjuntos ya resueltos; no volver a descargarlos.
2. Etiquetar la pertinencia **por par compra-perfil** usando evidencia del producto/servicio y límites de catálogo: `coincidencia_confirmada`, `coincidencia_posible`, `informacion_insuficiente`, `no_relevante`. Registrar fundamento y qué parte de un paquete mixto cubre cada perfil.
3. Verificar si las 100 compras de ambas selecciones se solapan por código y **reutilizar** las etiquetas documentales en las coincidentes; no asumir identidad de cohortes.
4. Ejecutar métodos A (solo UNSPSC), B (texto y productos), C (B + detección de conflicto UNSPSC), D (C + adjuntos selectivos) **sin mirar las etiquetas humanas**.
5. Medir falsos negativos, falsos positivos, abstenciones, esfuerzo y oportunidades únicas afectadas. Los 301 productos auditados no equivalen a 301 oportunidades ni a 301 pares compra-perfil.
6. Validar métricas antes de conectar clasificación a alertas de clientes.

## 5. Primer cruce semántico: observaciones preliminares, NO etiquetas finales

Basado en el CSV de adjuntos ya revisados:

- `2287-741-COT26`: marcadores, tijeras, papeles y cartulinas; **OFICINA** es candidato por útiles/papelería, pero verificar cobertura de todo el paquete.
- `4455-357-COT26`: proyector, audio, televisor, notebook y licencia de Office, además de elementos de laboratorio; **TECNOLOGIA** es candidato para parte del pedido; no asumir que provee insumos de laboratorio.
- `3152-314-COT26`: nylon para orilladora, calzado de seguridad, enchufes y cable eléctrico; posible cruce con **CONSTRUCCION**, sujeto a cobertura de todos los ítems.
- `736812-99-COT26`: artistas y danza; **no aparece un perfil de producción artística** entre los ocho, y no debe forzarse coincidencia.

Estas observaciones son hipótesis de pertinencia, **no etiquetas humanas auditadas**. Para etiquetar se deben leer los detalles de cada compra y aplicar el protocolo.

## 6. Próxima acción concreta

Reutilizar `FARO-100-auditoria.xlsx` y `FARO-100-revision-adjuntos.csv` como evidencia ya revisada. Empezar por las 12 líneas con adjuntos, identificar los pares compra-perfil candidatos y contrastar el alcance real de los ocho perfiles. Documentar decisiones justificadas antes de comparar A–D. No crear archivos nuevos si puede ampliarse un registro existente.

---
**Principio de continuidad:** revisar primero, reutilizar lo existente, ejecutar después. Una ejecución exitosa de GitHub Actions no equivale por sí sola a cobertura completa ni a precisión de clasificación validada.
