# Piloto FARO → Supabase (Compra Ágil v2)

Esta rama propone una **prueba manual**, sin enviar correos y sin reemplazar el monitor anterior.

- Origen: endpoint `/v2/compra-agil`, usando `cambio_desde`/`cambio_hasta`.
- Destino: proyecto Supabase **radar_faro** (no el proyecto FARO).
- Tablas: `oportunidades`, `cambios_oportunidad`, `sincronizaciones`.
- La primera ejecución toma una hora reciente (con superposición de 20 minutos).
- Se procesa **una ventana por ejecución** de forma conservadora. La sincronización
  guarda el cursor únicamente después de almacenar correctamente los registros.
- Los códigos repetidos se actualizan por `(fuente, codigo)`; los cambios
  se deduplican por `(oportunidad_id, huella_cambio)`.
- En una falla, el cursor no avanza y se puede reintentar la misma ventana.

## Preparación obligatoria

En los secrets de Actions del repositorio `fap`, configurar:
- `CHILECOMPRA_TICKET`: ticket oficial utilizado por el monitor anterior.
- `SUPABASE_SECRET_KEY`: clave **secreta de servidor** del proyecto
  `radar_faro` (se obtiene en Supabase → Project Settings → API Keys).
  Nunca usar la publishable ni pegar la clave en GitHub como variable pública.

El workflow usa la URL pública de la API del proyecto como variable de entorno.
No usa dependencias de pip ni requiere permiso para escribir en GitHub.

## Ejecución y validación

1. Abrir el PR y revisar los cambios.
2. Configurar `SUPABASE_SECRET_KEY`.
3. Tras integrar el PR, ir a GitHub Actions → **FARO - Piloto Supabase (manual)**
   → **Run workflow**. El trigger manual requiere que el workflow exista
   en la rama predeterminada.
4. Verificar los logs y en Supabase:
   `select fuente, count(*) from public.oportunidades group by fuente;`
   `select * from public.sincronizaciones;`
5. Ejecutar otra vez para verificar que no aparecen duplicados.

**Precauciones:** El workflow antiguo de `fap` sigue programado y escribe
`state.json`. Esta prueba es independiente; no lo modifica. La prueba no
garantiza cobertura histórica completa ni que las fechas del API siempre
sean consistentes. No habilitar una programación automática hasta validar
los datos de la primera ejecución.
