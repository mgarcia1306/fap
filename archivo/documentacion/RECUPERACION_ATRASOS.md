# Recuperación de atrasos de FARO

## Objetivo

El monitor actual consulta solo una hora pendiente por ejecución. Ahora procesa
hasta **4 tramos consecutivos de una hora**, cada uno con 20 minutos de solapamiento.

## Salvaguardas

- Solo avanza el cursor tras guardar por completo el tramo en Supabase.
- Si ChileCompra o Supabase falla, deja de procesar y no salta el intervalo fallido.
- Nunca procesa más allá de la hora UTC al inicio de la ejecución.
- Presupuesto general: 8 minutos. Si restan menos de 60 segundos, no
  inicia otro intervalo. GitHub Actions tiene un timeout independiente de 12 min.
- Mantiene el mismo filtro de horario para ejecuciones programadas.
- Mantiene el mismo esquema de base de datos y los mismos secretos.
- No modifica el antiguo monitor `monitor.py` ni el histórico `state.json`.

## Comprobaciones

```bash
python -m py_compile monitor_supabase.py
python -m unittest -v test_horario_faro.py test_recuperacion_atrasos.py
```

En GitHub Actions, revisar el log `Sincronizar una ventana de Compra Agil`:
ahora debe aparecer `Tramo 1/4`, `Tramo 2/4`, etc. y una línea `Resumen`.

## Limitaciones y próximos ajustes

- Una hora puede contener muchos registros y consumir varios minutos.
- Aún se hacen escrituras individuales por oportunidad y por cambio, que
  conviene agrupar para reducir llamadas a Supabase.
- El cursor actual puede estar muchas horas atrasado: recuperará progreso
  en cada ejecución, sujeto al horario operativo y los límites de la API.
- Seguimos necesitando mejorar la protección frente a eventos desordenados
  en las ventanas superpuestas para evitar sobrescribir un estado más reciente.
