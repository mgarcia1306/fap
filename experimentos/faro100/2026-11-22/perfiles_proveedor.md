# FARO-100 · Perfiles de proveedores v1 (hipotéticos)

Estos **ocho perfiles son casos de prueba**, no clientes reales ni rubros definitivos de FARO. Su alcance deliberadamente específico permite evaluar pertinencia y detectar falsos negativos; no se debe asumir que todos los proveedores de un rubro ofrecen lo mismo.

| ID | Perfil | Incluye (capacidad asumida) | No incluye o requiere verificación |
|---|---|---|---|
| CONSTRUCCION | Materiales de construcción y ferretería | Materiales de obra, fijaciones, herramientas y elementos de ferretería para abastecimiento. | Excluir obras integrales, ingeniería, instalación especializada y equipos industriales fuera del catálogo; una obra que incluya materiales no implica que un proveedor de materiales pueda ejecutarla. |
| OFICINA | Papelería, impresión y suministros de oficina | Papel, útiles de escritorio, tóner, tintas, artículos de archivo y material impreso simple. | Excluir equipos computacionales complejos, desarrollo de software y servicios publicitarios integrales; impresiones especializadas requieren validación. |
| TECNOLOGIA | Equipamiento informático y soporte TI | Computadores, periféricos, redes de datos, licencias comunes y soporte informático básico. | Excluir proyectos de IA, ciberseguridad, software a medida y servicios profesionales especializados salvo ampliación explícita del perfil. |
| SALUD | Insumos médicos y clínicos no farmacéuticos | Insumos clínicos desechables, curación y equipamiento clínico básico sujeto a compatibilidad y requisitos. | Excluir medicamentos, reactivos regulados y dispositivos de alta complejidad; exigir comprobación de registros y especificaciones cuando aplique. |
| ALIMENTOS | Alimentos y abastecimiento gastronómico | Alimentos envasados, bebidas no alcohólicas, materias primas y suministros alimentarios. | Excluir catering preparado, concesiones de alimentación y servicios con cocina o transporte especializado sin capacidad acreditada. |
| ASEO | Productos de aseo e higiene institucional | Detergentes, desinfectantes de uso permitido, bolsas, papel higiénico, toallas de papel y utensilios de limpieza. | Excluir contratos de personal de aseo, sanitización especializada y químicos que requieran autorizaciones no cubiertas. |
| TEXTIL | Vestuario, textiles y elementos promocionales | Ropa de trabajo, uniformes, textiles y productos promocionales textiles estándar. | Excluir equipos de protección certificados o textiles técnicos cuando el perfil no cubra normas específicas; fabricación a medida requiere validación. |
| MANTENCION | Mantención general y servicios menores | Reparaciones menores, mantención preventiva básica de infraestructura y servicios simples de instalación. | Excluir reparación vehicular especializada, obras mayores, electricidad certificada y mantenimiento clínico/industrial sin personal habilitado. |

## Condiciones transversales
- El juicio principal es **pertinencia técnica/comercial** para el perfil, no elegibilidad legal o logística. Región, cobertura, plazo, capacidad de suministro, presupuesto, experiencia, certificaciones y estado de convocatoria se registran aparte; no se mezclan con la etiqueta semántica.
- No inferir que un proveedor posee acreditaciones o capacidad de fabricar a medida. Si son necesarias y no están definidas, usar `coincidencia_posible` o `informacion_insuficiente`.
- Una oportunidad puede coincidir con varios perfiles. Las 100 compras originan **800 pares compra-perfil**; los 800 no son oportunidades independientes.
- Los códigos UNSPSC se comparan como una **señal**: nunca se usan para crear la verdad de referencia ni para descartar sin revisar evidencia.
- No ajustar estos perfiles después de ver resultados de los métodos A-D sin versionar el cambio; de lo contrario se contamina la evaluación.
