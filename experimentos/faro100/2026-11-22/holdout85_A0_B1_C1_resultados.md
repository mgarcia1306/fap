# FARO-100 — Prueba fuera del piloto: 85 compras × 8 perfiles

**Fecha de ejecución:** 2026-11-25. **Estado:** predicciones exploratorias congeladas, sin verdad humana para las 85 compras. **Rama:** `experimento/faro-100-muestra-20261122`.

## Qué se hizo
- Se reutilizó el artefacto histórico del run [44987485178](https://github.com/mgarcia1306/fap/actions/runs/44987485178): 100 JSON de Compra Ágil más `resultado_descarga.json`. No hubo solicitudes nuevas a Mercado Público ni a Supabase.
- Se excluyeron exactamente las 15 compras usadas previamente para construir y probar las reglas, mediante las claves de `FARO100_B1_C1_resultados.csv`.
- Se ejecutaron **SIN ALTERACIONES** `faro100_metodo_A0_reproducir.py` (función `predict`) y `faro100_metodos_B1_C1.py` (función `guess_b`) sobre las 85 restantes. C1 conserva la etiqueta B1 y añade alerta de contradicción UNSPSC-texto.
- Se guardaron 680 predicciones con sus identificadores `codigo` + `perfil_id`, número de productos, códigos UNSPSC, etiqueta A0, etiqueta B1/C1, razón B1 y alerta C1.
- No se leyeron ni se inventaron etiquetas humanas para estas 85 compras. La columna de evaluación humana del CSV está vacía.
- Se verificaron 680 pares únicos (85 × 8), con una sola predicción por método y por par; C1 coincide con B1 en todos.

## Resultados congelados

| Salida | A0 solo códigos | B1 texto | C1 |
|---|---:|---:|---:|
| `coincidencia_confirmada` | 0 | 17 | 17 |
| `coincidencia_posible` | 2 | 13 | 13 |
| `informacion_insuficiente` | 0 | 64 | 64 |
| `no_relevante` | 614 | 586 | 586 |
| `abstencion` | 64 | 0 | 0 |
| Total | 680 | 680 | 680 |

- **C1:** 28 pares con `conflicto_posible` (23 compras únicas), 588 sin conflicto detectado, 64 `sin_codigos`.
- **Cobertura estructurada:** 8/85 compras no tenían productos estructurados, equivalentes a 64 pares sin códigos.
- **B1:** 17 coincidencias confirmadas y 13 posibles distribuidas en 24 compras únicas; el resto son descartes o insuficientes.
- **NO existen etiquetas humanas para holdout, por lo tanto NO calcular:** accuracy, sensibilidad, precisión, falsos negativos o falsos positivos.
- El aumento de coincidencias semánticas respecto de A0 no significa automáticamente mejora de calidad.

## Alertas de calidad (sin alterar reglas)

Estas son **posibles sobreclasificaciones**, a revisar con detalle antes de aceptar o anunciar oportunidades:

1. `2923-933-COT26` / `TEXTIL`: B1 clasificó `coincidencia_confirmada` una compra denominada *DIDECO--COFFE BREACK*. Puede deberse a menciones incidentales de artículos como manteles en una prestación alimentaria.
2. `2138-401-COT26` / `OFICINA`: B1 clasificó `coincidencia_confirmada` una mantención preventiva de intercambiadores de placas de hospital. Probable efecto de expresiones incidentales como formulario y no pertinencia directa al perfil.
3. `4364-558-COT26` / `ALIMENTOS`: B1 clasificó `coincidencia_confirmada` un servicio de producción de evento. Revisar si hay suministro alimentario independiente o catering/evento integral.
4. `1079659-480-COT26` / `MANTENCION`: B1 clasificó como confirmada una compra de *herramientas para mantenimiento*. No confundir propósito del comprador con el producto o servicio contratado.
5. `5097-2-COT26` / `MANTENCION`: instalación y puesta en marcha de CCTV. Posible especialización no incluida en servicios menores del perfil.

**Estos hallazgos NO son errores demostrados sin revisión humana**. No se utilizan para reajustar B1/C1, ya que hacerlo sobre el holdout destruiría su independencia.

## Límites metodológicos
- Los códigos del A0 proceden del diccionario exploratorio del piloto y no abarcan la taxonomía oficial UNSPSC. El descarte por códigos no mapeados puede producir numerosos negativos falsos.
- B1 y C1 son reglas léxicas, no un modelo de IA ni comprensión semántica profunda.
- Los métodos B1/C1 fueron ajustados con conocimiento de los **15 casos de diseño**. Los 85 restantes son fuera de esos 15, pero el muestreo total de 100 sigue siendo una selección específica; no inferir desempeño poblacional.
- La clasificación de **oportunidad afín / secundaria NO ESTÁ IMPLEMENTADA**. La salida `coincidencia_posible` solo refleja las reglas de texto, no un estimador del interés comercial real de clientes generalistas.
- La ejecución de D (adjuntos) y un método de IA genuino siguen pendientes.

## Evidencia y reproducción
- Archivos locales entregados al usuario en la conversación:
  - `FARO100_holdout85_A0_B1_C1_predicciones.csv`
  - `FARO100_holdout85_resumen.json`
  - `faro100_holdout85_ejecutar.py`
- Fuentes congeladas: `faro100-detalles.zip`, `FARO100_B1_C1_resultados.csv`, `faro100_metodo_A0_reproducir.py`, `faro100_metodos_B1_C1.py`.
- Hash SHA-256 del CSV de 680 pares: `d3d12b49b95616cce4d2839eb6b56e405eaacf300276b99eb4168e9884f9e58c`.
- El script de holdout invoca los módulos de A0/B1 existentes sin reescribir sus funciones; no requiere acceso de red.
- **Siguiente hito:** etiquetado humano independiente de una selección de casos de alta información (confirmadas, posibles, discordancias y controles negativos), sin usar las predicciones como pistas; medir el efecto de afinidad comercial en dimensión separada.

**Protección:** no hay cambios en `main`, Supabase, servicios activos ni automatizaciones FARO; las predicciones no se han enviado a clientes.
