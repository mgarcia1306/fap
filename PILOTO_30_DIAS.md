# FARO · piloto de cohorte de publicaciones (30 días calendario)

**Inicio:** 2026-11-20 18:51:00 America/Santiago (2026-11-20 21:51 UTC).

**Final:** 2026-12-20 00:00:00 America/Santiago (exclusivo). El último día completo es 19 de diciembre.

**Política:** Solo ingresar Compras Ágiles publicadas durante este intervalo. Una compra anterior no ingresa por el simple hecho de recibir una modificación. Compras de la cohorte sí pueden actualizarse y registrar cambios en futuras rondas durante el piloto. Este filtro se ejecuta **antes** de escribir en Supabase.

**Frecuencia:** sin cambios en Cloudflare (cuatro activaciones cada hora, minutos 07/22/37/52); GitHub ejecuta el workflow de actualidad en cada activación. En cada ronda consulta publicaciones nuevas y últimas modificaciones dentro de una ventana retrospectiva de 90 minutos. En la primera ronda la ventana se recorta al inicio del piloto.

**Zona horaria:** el endpoint v2 observado interpreta sus filtros como hora de pared de Chile expresada en formato Z; por ello el monitor mantiene esa compatibilidad para consultar. Los campos `fechas.fecha_publicacion` se interpretan como fecha y hora local de Chile exclusivamente a los efectos de decidir si pertenecen a la cohorte.

**Datos previos:** no borrar ni alterar los 7.994 registros anteriores. El piloto convive en `public.oportunidades`, distinguible por la fecha de publicación. Las escrituras se realizan mediante la RPC idempotente existente.

**Al concluir:** se detiene la ingesta automática de actualidad dentro del programa (Cloudflare puede seguir despertando al workflow; optimización posterior), pero no se eliminan datos. Las compras no se recolectan después del límite sin una decisión explícita.

**Limitación conocida:** la ventana retrospectiva de 90 minutos cubre interrupciones cortas, pero no recupera automáticamente cortes más largos. Antes de ofrecer el servicio comercial deberán implementarse controles de huecos, verificación de integridad y horario óptimo, y revisar la semántica de fechas de la API.
