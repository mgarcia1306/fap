# FARO · Monitor reciente: publicaciones y modificaciones

El workflow `actualidad.yml`, activado mediante Cloudflare, consulta la API v2 de Compra Ágil cada ~15 minutos (según el programador externo).

## Dos consultas, dos objetivos

En cada ejecución, dentro de una ventana retrospectiva de 90 minutos:

1. **Publicaciones recientes:** `publicado_desde`, `publicado_hasta`, `ordenar_por=FechaPublicacion`. Detecta compras incorporadas a Mercado Público.
2. **Modificaciones recientes:** `cambio_desde`, `cambio_hasta`, `ordenar_por=FechaUltimaModificacion`. Detecta actualizaciones en compras ya publicadas.

Ambas utilizan `tamano_pagina=50`, descargan todas las páginas y subdividen automáticamente un intervalo demasiado voluminoso. Se combinan por `codigo` y prevalece la versión con mayor `fecha_ultimo_cambio`. Supabase realiza la persistencia idempotente e impide que una versión anterior sobrescriba una posterior.

El cursor independiente `compra_agil_v2_reciente` **solo avanza cuando ambas consultas y todas las escrituras terminan con éxito**. No se toca el cursor histórico `compra_agil_v2`.

## Logs y validación

La ejecución informa `publicaciones_en_ventana`, `cambios_en_ventana`, `oportunidades_distintas` y `publicadas_hoy_en_ventana`.

```bash
python -m unittest -v test_actualidad.py test_paginacion.py test_horario_faro.py
```

Una ejecución exitosa con cero resultados en ambos filtros significa que la API respondió cero para esas ventanas; no es prueba independiente de ausencia de publicaciones en el portal. Si persiste, se debe realizar un diagnóstico comparativo con una búsqueda por fecha de publicación directamente en la API y comprobar zona horaria, frecuencia de actualización y límites del servicio.

No se envían alertas ni se filtran oportunidades durante la ingesta. La elegibilidad comercial se calcula por la vista `oportunidades_clasificadas`.
