# FARO · cohorte continua de publicaciones

**Inicio fijo:** 2026-11-20 18:51:00 America/Santiago (2026-11-20 21:51 UTC).

**Sin fecha de término.** FARO continúa recopilando Compras Ágiles nuevas en cada activación de Cloudflare.

## Política de ingesta

Solo ingresar compras cuya fecha de publicación corresponda a las 18:51 del 20-nov-2026 o una fecha posterior. Los procesos publicados antes de ese instante no entran a la cohorte aunque reciban cambios. Las compras de la cohorte sí se actualizan cuando cambian, conservando su historial.

La selección se realiza antes de escribir en Supabase, interpretando `fechas.fecha_publicacion` como hora de pared Chile conforme al comportamiento observado de la API v2. Se mantienen cursores en UTC y deduplicación por código.

**Frecuencia:** cada ~15 min por Cloudflare. Ventana retrospectiva de 90 min, recortada al inicio en la primera ejecución.

**Datos anteriores:** conservar intactos los registros históricos; distinguir la cohorte por su fecha de publicación. No se borra ninguna tabla ni fila.

## Capacidad y controles recomendados

Supabase Free incluye actualmente 500 MB para la base de datos PostgreSQL (contando índices y objetos de la BD); la capacidad debe vigilarse con `pg_database_size(current_database())`, `pg_total_relation_size('public.oportunidades')` y `pg_total_relation_size('public.cambios_oportunidad')`.

Umbrales operativos sugeridos: aviso al 70% (350 MB), revisión de compactación/archivado al 80% (400 MB), y evitar acercarse a 500 MB sin una política definida. No se activa borrado ni archivado automáticos en este PR.

La ventana retrospectiva de 90 minutos cubre interrupciones cortas pero no recupera cortes más largos. Para un servicio comercial habrá que agregar control de huecos y reconciliación incremental, además de pruebas con clientes ficticios.
