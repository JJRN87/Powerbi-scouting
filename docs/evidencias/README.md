# Capturas y comprobaciones

Imágenes del informe y capturas de Jira y Confluence del 17/10/2026, con enlaces a código, análisis y comprobaciones.

## Power BI Desktop

Fuente de los análisis: [StatsBomb Open Data](https://github.com/statsbomb/open-data), LaLiga 2015/16. Análisis propio con asistencia de IA; sin afiliación ni respaldo de StatsBomb.

<img src="../assets/statsbomb-logo.png" width="230" alt="StatsBomb">

Las dos imágenes proceden de una exportación real de Power BI a PDF, renderizada sin el aviso superior de la aplicación. No se han modificado los datos ni los elementos del informe. La primera muestra el organizador con la configuración base; los escenarios de las revisiones posteriores de los otros seis perfiles se han probado en Python.

![Informe de Power BI con pesos ajustables](capturas/powerbi-ranking-base.png)

La página de validación compara DAX con Python en seis escenarios: 1.359 comparaciones, cero diferencias. [Detalle de las pruebas](../VALIDACION_POWERBI.md).

![Validación de Power BI frente a Python](capturas/powerbi-validacion.png)

## Jira

Tablero después del análisis por partidos y contexto: diez tareas terminadas y una pendiente, la evaluación de datos actuales.

![Seguimiento del proyecto en Jira](capturas/jira-tablero.png)

## Confluence

La página recoge el objetivo, la limpieza, la validación y los siguientes pasos. El contenido esencial también está en este repositorio para que se pueda leer sin una cuenta de Atlassian.

![Documentación del proyecto en Confluence](capturas/confluence-proyecto.png)

## Registros reproducibles

- [Validación de Desktop](powerbi-validacion.json): registro de la sesión, escenarios y hashes de los archivos probados.
- [Revisión de perfiles](revision-perfiles.json): método de sensibilidad, contraste base, recuento directo y límites.
- [Revisión de los cuatro perfiles restantes](revision-cuatro-perfiles.json): 80.000 simulaciones, 213 candidatos, 196 comprobaciones de métricas y 70 de minutos. Incluye la excepción Filipe–Marcelo que no apareció en el muestreo aleatorio.
- [Estabilidad por partidos y contexto](estabilidad-partidos.json): muestras, reconciliación de totales, resultados y límites.
- [Origen de las imágenes de Power BI](imagenes-powerbi.json): exportación, renderizado y hashes.
- [Metodología](../METODOLOGIA.md) y [forma de trabajo](../gestion/FORMA_DE_TRABAJO.md).

Las imágenes documentan el informe y las herramientas de seguimiento. No se publican los eventos originales, la base, los CSV completos, la caché ni el PBIX cargado. Las marcas pertenecen a sus titulares.
