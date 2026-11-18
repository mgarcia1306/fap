# FARO · Monitoreo de Compra Ágil

Proyecto experimental del radar FARO. Consulta la API v2 de Compra Ágil de
Mercado Público y almacena oportunidades y cambios en **Supabase (radar_faro)**.
No envía correos.

## Procesos vigentes

- **Actualidad:** `.github/workflows/actualidad.yml` ejecuta
  `python monitor_supabase.py --modo actualidad`; busca cambios de los
  últimos 90 minutos, independientemente del atraso histórico.
- **Recuperación histórica:** `.github/workflows/supabase_piloto.yml`
  ejecuta `python monitor_supabase.py --modo historico`; recupera hasta
  cuatro tramos de una hora por ejecución.
- **Diagnóstico manual:** `.github/workflows/diagnostico.yml`
  ejecuta `diagnostico.py`.

La programación de GitHub Actions es de mejor esfuerzo: puede retrasarse u
omitirse. Para ejecuciones automáticas se aplica el horario operativo definido
en `monitor_supabase.py`.

## Configuración

En GitHub → Settings → Secrets and variables → Actions:
- `CHILECOMPRA_TICKET`: credencial oficial de ChileCompra.
- `SUPABASE_SECRET_KEY`: clave de servidor del proyecto Supabase `radar_faro`.

Nunca introducir secretos en el repositorio. La URL del proyecto es pública,
pero la clave de servidor debe permanecer privada.

## Pruebas

```sh
python -m unittest -v test_actualidad.py test_horario_faro.py test_recuperacion_atrasos.py
```

## Referencias y código histórico

- `MONITOREO_ACTUALIDAD.md`: arquitectura y limitaciones actuales.
- `supabase/sql/faro_guardar_oportunidad.sql`: función de persistencia.
- `archivo/`: scripts, workflow y documentos de pruebas anteriores;
  consultar `archivo/README.md`.
- `state.json`: historial del monitor antiguo, conservado **sin cambios**;
  no se utiliza en los procesos de Supabase.

El sistema aún está en etapa piloto. Un check verde en GitHub Actions no
garantiza por sí solo cobertura completa de todas las oportunidades.
