# FARO: monitoreo de actualidad y recuperación histórica

**Dos procesos independientes**, una misma tabla de oportunidades.

- `python monitor_supabase.py --modo actualidad`: consulta la ventana de
  **90 minutos anteriores a la hora actual**, sin esperar al cursor histórico.
  Registra su propia sincronización con fuente `compra_agil_v2_reciente`.
- `python monitor_supabase.py --modo historico`: procesa desde el cursor
  histórico `compra_agil_v2`, hasta cuatro horas consecutivas por ejecución.

Ambos procesos usan el endpoint de cambios de Compra Ágil v2. No confundir
`fecha_ultimo_cambio` con `fecha_publicacion`: las oportunidades publicadas
hoy se identifican utilizando explícitamente su fecha de publicación.

## Protección de datos

La función SQL `public.faro_guardar_oportunidad(jsonb,text)`, instalada en
el proyecto Supabase `radar_faro` mediante la migración
`faro_ingesta_cronologica_segura`, ejecuta una transacción por oportunidad.
Rechaza sobrescribir una versión más reciente con una antigua; conserva ambas
huellas en `cambios_oportunidad`. Sólo `service_role` puede invocarla.
Los roles anónimos y autenticados no tienen acceso a la función.

## Ejecución y límites

Workflow nuevo: `.github/workflows/actualidad.yml`, con cron en los minutos
7, 22, 37 y 52 de cada hora. El código respeta el horario operativo de Chile
para ejecuciones programadas. Las ejecuciones manuales no tienen ese filtro.

GitHub Actions no garantiza puntualidad del cron: si hay una omisión mayor
a 90 minutos, el recuperador histórico debe cubrir el vacío más tarde.
El monitor de actualidad no sustituye el histórico ni implica cobertura total
de publicaciones de un día. Se requiere una futura verificación de cobertura.

## Testeo

`python -m unittest -v test_actualidad.py test_recuperacion_atrasos.py test_horario_faro.py`

Se verificó la función SQL con una compra temporal y sus versiones nueva y
antigua dentro de una transacción revertida (ROLLBACK), sin dejar datos de prueba.

El workflow no envía correos. Antes de activar alertas, validar consistencia
de campos y frecuencia real de ejecuciones.
