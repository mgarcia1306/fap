# Archivo histórico de FARO

Esta carpeta conserva código y documentación de las primeras pruebas del monitor
Compra Ágil. **No es parte del sistema operativo actual.**

## Contenido

- `monitores_antiguos/monitor.py`: monitor original que usaba `state.json`.
- `monitores_antiguos/test_monitor.py`: pruebas antiguas del monitor original.
- `workflows/monitor.yml`: workflow manual antiguo que ejecutaba `monitor.py`
  y escribía `state.json`. Está **fuera de `.github/workflows/`**, por lo
  tanto GitHub Actions ya no lo reconoce como workflow activo.
- `documentacion/SUPABASE_PILOTO.md`: instrucciones iniciales del piloto.
- `documentacion/RECUPERACION_ATRASOS.md`: notas de la primera recuperación.

Cada archivo se trasladó conservando el contenido original.

## Importante

`state.json` continúa en la raíz sin modificaciones. Es un historial legado
que debe respaldarse o compararse con Supabase antes de decidir su destino.

Los monitores operativos están en `monitor_supabase.py` y se ejecutan mediante:
- `.github/workflows/actualidad.yml` (actualidad)
- `.github/workflows/supabase_piloto.yml` (recuperación histórica)

No ejecutar los scripts archivados directamente sin comprobar sus dependencias.
