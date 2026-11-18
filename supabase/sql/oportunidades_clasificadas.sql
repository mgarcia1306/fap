-- Clasificación dinámica de Compras Ágiles para futuras alertas FARO.
-- Aplicada a Supabase radar_faro con migración:
-- faro_clasificacion_dinamica_cierre_compra_agil
-- La fecha de cierre y NOW() se evalúan al consultar la vista.
create or replace view public.oportunidades_clasificadas
with (security_invoker = true)
as
select clasificada.*,
       (clasificada.clasificacion in ('vigente','por_cerrar')) as elegible_alerta
from (
  select o.id, o.fuente, o.codigo, o.titulo, o.descripcion, o.organismo,
         o.region_codigo, o.estado_codigo, o.estado_nombre, o.monto, o.moneda,
         o.fecha_publicacion, o.fecha_cierre, o.fecha_ultimo_cambio,
         o.detectada_at, o.actualizada_at,
         case
           when lower(btrim(coalesce(o.estado_codigo,''))) in
             ('cerrada','cancelada','desierta','proveedor_seleccionado')
             then 'finalizada'
           when o.fecha_cierre is not null and o.fecha_cierre <= now()
             then 'finalizada'
           when o.fecha_cierre is null then 'por_revisar'
           when lower(btrim(coalesce(o.estado_codigo,''))) <> 'publicada'
             then 'por_revisar'
           when o.fecha_cierre <= now() + interval '24 hours'
             then 'por_cerrar'
           else 'vigente'
         end as clasificacion,
         case when o.fecha_cierre > now()
              then round((extract(epoch from (o.fecha_cierre - now())) / 3600)::numeric,2)
              else 0::numeric end as horas_para_cierre
  from public.oportunidades o
  where o.fuente = 'compra_agil_v2'
) clasificada;
revoke all on public.oportunidades_clasificadas from public, anon, authenticated;
grant select on public.oportunidades_clasificadas to service_role;
comment on view public.oportunidades_clasificadas is
 'Clasificación dinámica para FARO. Solo vigente/por_cerrar es elegible; la vista no elimina el histórico ni envía alertas.';
