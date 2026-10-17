# Capturas y comprobaciones

Capturas reales del 17/10/2026. Muestran el informe y el uso de Jira y Confluence; no son maquetas. El código, las decisiones y los registros se enlazan para poder comprobar qué hay detrás.

## Power BI Desktop

Fuente de los análisis: [StatsBomb Open Data](https://github.com/statsbomb/open-data), LaLiga 2015/16. Análisis propio con asistencia de IA; sin afiliación ni respaldo de StatsBomb.

<img src="../assets/statsbomb-logo.png" width="230" alt="StatsBomb">

El informe permite seleccionar perfil, equipo y pesos. Esta captura corresponde al organizador y a la configuración base validada; los escenarios nuevos de pivote y delantero se han revisado en Python.

![Informe de Power BI con pesos ajustables](capturas/powerbi-ranking-base.png)

La página de validación compara DAX con Python en seis escenarios: 1.359 comparaciones, cero diferencias. [Detalle de las pruebas](../VALIDACION_POWERBI.md).

![Validación de Power BI frente a Python](capturas/powerbi-validacion.png)

## Jira

Tablero después de iniciar la revisión de perfiles: ocho tareas terminadas, una en curso y dos por hacer. La revisión global permanece abierta.

![Seguimiento del proyecto en Jira](capturas/jira-tablero.png)

## Confluence

La página recoge el objetivo, la limpieza, la validación y los siguientes pasos. El contenido esencial también está en este repositorio para que se pueda leer sin una cuenta de Atlassian.

![Documentación del proyecto en Confluence](capturas/confluence-proyecto.png)

## Registros reproducibles

- [Validación de Desktop](powerbi-validacion.json): registro de la sesión, escenarios y hashes de los archivos probados.
- [Revisión de perfiles](revision-perfiles.json): método de sensibilidad, contraste base, recuento directo y límites.
- [Metodología](../METODOLOGIA.md) y [forma de trabajo](../gestion/FORMA_DE_TRABAJO.md).

Las capturas de herramientas documentan el proceso. No prueban por sí solas calidad predictiva ni aplicación de Scrum completo. No se publican los eventos originales, la base, los CSV completos, la caché ni el PBIX cargado. Las marcas pertenecen a sus titulares.
