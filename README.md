# FARO · prueba de API Compra Ágil v2

Prueba de bajo consumo: consulta cada 15 minutos y compara `codigo`, `fecha_ultimo_cambio` y `estado` con el historial anterior. **No envía correos ni recolecta datos privados**.

## Preparación en GitHub

1. Crea un repositorio de prueba **privado** (recomendado) y sube **el contenido de esta carpeta a la raíz** del repositorio, incluida `.github/workflows/monitor.yml`.
2. Solicita o utiliza tu ticket personal oficial de ChileCompra: <https://www.chilecompra.cl/api/>.
3. En GitHub: **Settings → Secrets and variables → Actions → New repository secret**. Nombre: `CHILECOMPRA_TICKET`. Valor: tu ticket. Nunca lo pegues en el código ni en una conversación.
4. En **Settings → Actions → General → Workflow permissions**, habilita **Read and write permissions** (si esa opción está disponible). El workflow necesita escribir `state.json`. Comprueba que la rama principal no bloquee los commits del bot.
5. Abre **Actions → FARO - API Compra Agil (prueba) → Run workflow**. Luego revisa el log de `Consultar cambios`.
6. Vuelve a ejecutarlo manualmente después de unos minutos. La segunda ejecución debería registrar repetidas, nuevas o modificadas; el archivo `state.json` conserva el historial.

## Qué demuestra

- La API responde (o informa un rechazo) desde la red de GitHub.
- La tarea programada se ejecuta automáticamente cada 15 minutos **cuando GitHub la despacha**; GitHub advierte que los cron pueden retrasarse u omitirse.
- La sincronización usa `cambio_desde`/`cambio_hasta`, no vuelve a descargar todo el catálogo histórico.
- Recorre páginas de 50 hasta un máximo deliberado de 30 solicitudes por ejecución (2.880 solicitudes diarias como máximo teórico, sin reintentos ni ejecuciones manuales).
- Si hay error, exceso de páginas o respuesta incompleta, sale con error y **no avanza** el historial.
- El historial guarda códigos y marcas de cambios de los últimos 7 días. **No es aún una base histórica completa**.

## Limitaciones de esta prueba

- La primera ejecución revisa la última hora, y cada ejecución posterior vuelve a revisar 20 minutos superpuestos para tolerar retrasos. Si hay una caída prolongada, el historial conserva la última sincronización exitosa, pero una ventana muy extensa puede exceder el límite de páginas y necesitar un proceso de recuperación por tramos.
- La primera vez que ve una compra, la clasifica como «nueva en nuestro historial», aunque haya sido publicada antes.
- No busca detalles, productos ni perfiles de clientes. No prueba todavía que todas las Compras Ágiles nacionales se hayan recuperado sin omisiones.
- No hay garantía de ejecución puntual cada 15 minutos ni de disponibilidad de API.
- Si el proyecto está en repositorio público, cualquiera podrá ver el historial y los logs de identificación de compras (no el ticket); por eso se recomienda privado.
- En GitHub Actions, el límite de minutos gratuitos depende del tipo de repositorio/plan.

**Documentación oficial:** <https://www.chilecompra.cl/wp-content/uploads/2026/05/Documentacion_API_Compra_Agil.pdf>
