-- FARO-100: SELECT de selección estratificada y determinista; NO modifica tablas.
-- Universo: 8954 registros al 2026-11-22T04:32:41.815282Z, id máximo 12649.
-- Semilla: FARO100-20261122-v1. La membresía exacta está congelada en el CSV.
WITH universo AS (
 SELECT id,codigo,titulo,
 CASE WHEN length(btrim(coalesce(titulo,'')))<=42 OR btrim(coalesce(titulo,'')) ~* '^(compra|adquisici[oó]n|servicio|contrataci[oó]n|suministro|materiales|insumos|equipamiento|productos|varios|otros|requerimiento|solicitud|cotizaci[oó]n|implementos|art[ií]culos|repuestos)( de| para)?[[:space:].-]*$' THEN 'titulo_breve_o_generico'
 WHEN length(btrim(coalesce(titulo,'')))>=75 THEN 'titulo_extenso' ELSE 'intermedio' END AS perfil
 FROM public.oportunidades WHERE fuente='compra_agil_v2' AND id<=12649
 AND detectada_at<='2026-11-22T04:32:41.815282Z'::timestamptz AND codigo IS NOT NULL
), elegidos AS (
 (SELECT id,codigo,'titulo_extenso'::text AS grupo FROM universo WHERE perfil='titulo_extenso' ORDER BY md5('FARO100-20261122-v1|D|'||codigo),codigo LIMIT 30)
 UNION ALL
 (SELECT id,codigo,'titulo_breve_o_generico'::text AS grupo FROM universo WHERE perfil='titulo_breve_o_generico' ORDER BY md5('FARO100-20261122-v1|A|'||codigo),codigo LIMIT 40)
), resto AS (
 SELECT id,codigo,'aleatorio'::text AS grupo FROM universo u
 WHERE NOT EXISTS (SELECT 1 FROM elegidos e WHERE e.id=u.id)
 ORDER BY md5('FARO100-20261122-v1|R|'||codigo),codigo LIMIT 30
), muestra AS (SELECT * FROM elegidos UNION ALL SELECT * FROM resto)
SELECT row_number() OVER(ORDER BY CASE m.grupo WHEN 'titulo_extenso' THEN 1 WHEN 'titulo_breve_o_generico' THEN 2 ELSE 3 END,md5('FARO100-20261122-v1|O|'||m.codigo),m.codigo)::integer AS numero,
 m.grupo AS grupo_muestreo,o.id AS oportunidad_id,o.codigo,o.titulo,
 o.datos_originales->'institucion'->>'nombre_region' AS region_nombre,
 o.datos_originales->'institucion'->>'region' AS region_codigo_fuente,
 o.datos_originales->'institucion'->>'organismo_comprador' AS organismo,
 o.datos_originales->'montos'->>'monto_disponible' AS monto_disponible,
 o.datos_originales->'montos'->>'moneda' AS moneda,
 o.datos_originales->'fechas'->>'fecha_publicacion' AS fecha_publicacion_fuente,
 o.datos_originales->'fechas'->>'fecha_ultimo_cambio' AS fecha_ultimo_cambio_fuente,
 o.datos_originales->'estado'->>'glosa' AS estado,
 CASE WHEN jsonb_typeof(o.datos_originales->'documentos')='array' THEN jsonb_array_length(o.datos_originales->'documentos') ELSE 0 END AS documentos_en_listado,
 o.detectada_at AS primera_deteccion_faro
FROM muestra m JOIN public.oportunidades o ON o.id=m.id ORDER BY numero;