-- Ejecutar SOLO tras aprobar el PR y revisar la previsualización.
-- No modifica fechas, cursores, datos originales ni historial.
-- Idempotente: solo completa valores NULL y exige glosa no vacía.
BEGIN;

WITH corregidas AS (
    UPDATE public.oportunidades
    SET estado_nombre = NULLIF(BTRIM(datos_originales->'estado'->>'glosa'), '')
    WHERE estado_nombre IS NULL
      AND NULLIF(BTRIM(datos_originales->'estado'->>'glosa'), '') IS NOT NULL
    RETURNING codigo
)
SELECT COUNT(*) AS filas_corregidas FROM corregidas;

-- Comprobación final de los campos sin nombre.
SELECT COUNT(*) AS sin_estado_nombre
FROM public.oportunidades
WHERE estado_nombre IS NULL;

COMMIT;
