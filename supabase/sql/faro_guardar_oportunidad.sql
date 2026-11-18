CREATE OR REPLACE FUNCTION public.faro_guardar_oportunidad(p_registro jsonb, p_huella text)
 RETURNS bigint
 LANGUAGE plpgsql
 SET search_path TO ''
AS $function$
declare
  v_id bigint;
  v_codigo text;
  v_fuente text;
  v_cambio timestamptz;
begin
  v_codigo := nullif(btrim(p_registro->>'codigo'), '');
  v_fuente := p_registro->>'fuente';
  v_cambio := (p_registro->>'fecha_ultimo_cambio')::timestamptz;
  if v_codigo is null or v_fuente <> 'compra_agil_v2'
     or v_cambio is null or nullif(btrim(p_huella), '') is null
     or jsonb_typeof(p_registro->'datos_originales') <> 'object' then
    raise exception 'Registro FARO inválido';
  end if;
  insert into public.oportunidades (
    fuente,codigo,titulo,descripcion,organismo,estado_codigo,estado_nombre,
    monto,fecha_publicacion,fecha_cierre,fecha_ultimo_cambio,datos_originales,actualizada_at
  )
  values (
    v_fuente,v_codigo,p_registro->>'titulo',p_registro->>'descripcion',
    p_registro->>'organismo',p_registro->>'estado_codigo',p_registro->>'estado_nombre',
    (p_registro->>'monto')::numeric,
    (p_registro->>'fecha_publicacion')::timestamptz,
    (p_registro->>'fecha_cierre')::timestamptz,
    v_cambio, p_registro->'datos_originales',now()
  )
  on conflict (fuente,codigo) do update set
    titulo=excluded.titulo,
    descripcion=excluded.descripcion,
    organismo=excluded.organismo,
    estado_codigo=excluded.estado_codigo,
    estado_nombre=excluded.estado_nombre,
    monto=excluded.monto,
    fecha_publicacion=excluded.fecha_publicacion,
    fecha_cierre=excluded.fecha_cierre,
    fecha_ultimo_cambio=excluded.fecha_ultimo_cambio,
    datos_originales=excluded.datos_originales,
    actualizada_at=now()
  where public.oportunidades.fecha_ultimo_cambio is null
     or excluded.fecha_ultimo_cambio >= public.oportunidades.fecha_ultimo_cambio
  returning id into v_id;
  if v_id is null then
    select id into v_id from public.oportunidades
      where fuente=v_fuente and codigo=v_codigo;
  end if;
  if v_id is null then
    raise exception 'No se pudo guardar oportunidad';
  end if;
  insert into public.cambios_oportunidad
    (oportunidad_id,fecha_cambio_fuente,estado_nuevo,huella_cambio,datos_cambio)
  values
    (v_id,v_cambio,p_registro->>'estado_codigo',p_huella,p_registro->'datos_originales')
  on conflict (oportunidad_id,huella_cambio) do nothing;
  return v_id;
end
$function$

revoke all on function public.faro_guardar_oportunidad(jsonb,text) from public, anon, authenticated;
grant execute on function public.faro_guardar_oportunidad(jsonb,text) to service_role;
