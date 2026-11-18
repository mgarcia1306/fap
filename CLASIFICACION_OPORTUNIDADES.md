# FARO · Elegibilidad para alertas según plazo

La vista protegida `public.oportunidades_clasificadas`, creada en Supabase
`radar_faro`, **no elimina registros históricos**. Calcula al consultar:

- `vigente`: estado oficial `publicada` y más de 24 horas para el cierre.
- `por_cerrar`: estado `publicada` y plazo futuro de hasta 24 horas.
- `finalizada`: cierre vencido o estado `cerrada`, `cancelada`,
  `desierta` o `proveedor_seleccionado`.
- `por_revisar`: sin fecha o estado no reconocido.

`elegible_alerta` es verdadero únicamente para `vigente` y `por_cerrar`.
`horas_para_cierre` ayuda a priorizar las oportunidades. La vista opera
sobre fechas UTC de tipo `timestamptz`, por lo que el cálculo es independiente
del huso horario de presentación.

## Consultas de ejemplo (servidor)

```sql
select codigo, titulo, estado_codigo, fecha_cierre, horas_para_cierre
from public.oportunidades_clasificadas
where elegible_alerta
order by fecha_cierre asc, codigo asc;

select clasificacion, count(*)
from public.oportunidades_clasificadas
group by clasificacion;
```

## Seguridad y alcance

La vista usa `security_invoker=true`. Se revocó el acceso a `anon` y
`authenticated`; solamente el rol de servidor `service_role` tiene
`SELECT`. No hay correos ni alertas automáticas implementadas todavía.

**Importante:** la elegibilidad refleja el estado de la última versión
almacenada; si ChileCompra cambió la situación y el monitor aún no sincroniza,
puede estar desfasada. Confirmar el estado en origen antes de cotizar.
Las compras con fecha futura pero estado `cancelada` no se ofrecen.
