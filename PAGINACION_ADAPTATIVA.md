# FARO · Paginación adaptativa

## Problema observado

El 18 de noviembre de 2026 el recuperador histórico recibió un intervalo
con **36 páginas**, superior al límite de **30 páginas por solicitud** de FARO.
El límite lo define nuestro código; la API respondió correctamente con el
total de páginas. El cursor no se adelantó para ese intervalo.

## Solución propuesta

- Se conserva el máximo local de 30 páginas por subconsulta.
- Si el servidor anuncia un resultado mayor, el intervalo se divide
  cronológicamente en dos mitades y se consultan ambas.
- Si una mitad sigue teniendo demasiadas páginas, vuelve a dividirse.
- Se conserva el instante divisorio en ambos extremos y se eliminan
  únicamente resultados completamente idénticos en el momento de unirlos.
- Profundidad máxima: 7 subdivisiones. Ancho mínimo: 2 minutos.
- **Si no puede completarse cualquier mitad**, la consulta termina en error
  sin almacenar ni marcar como completo el intervalo de esa hora.
- El monitor continúa escogiendo el cambio más reciente por código.
- Se aplica a los dos modos que comparten `fetch_changes`: actualidad e histórico.

## Seguridad

La división automática no elimina el límite de páginas. Tampoco elimina las
salvaguardas de tiempo, reintentos ni cursor. No implica una cuota oficial
de ChileCompra: este límite es nuestro.

## Pruebas sin red

```bash
python -m unittest -v test_paginacion.py test_actualidad.py \
    test_recuperacion_atrasos.py test_horario_faro.py
```

## Limitación pendiente

En intervalos de alta actividad pueden existir cientos o miles de códigos.
Aunque se divida la consulta correctamente, guardarlos individualmente puede
tardar varios minutos y agotar el tiempo de GitHub Actions. El cursor seguirá
sin marcar intervalos incompletos. La siguiente optimización es guardar
registros en lotes o confirmar progreso en subintervalos transaccionales.
