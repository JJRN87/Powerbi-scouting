# Cómo estoy organizando el proyecto

Quiero que el portfolio muestre el proceso completo: plantear una pregunta, preparar los datos, revisar el resultado y dejar constancia de lo que falta. Jira sirve para seguir el trabajo; Confluence, para explicar las decisiones; GitHub, para conservar el código y la documentación que puede consultar cualquiera.

## Qué prácticas están en uso

| Práctica | Evidencia |
|---|---|
| Objetivo de producto | Comparar candidatos por función y pesos antes de invertir en datos actuales. |
| Backlog con criterios de aceptación | [Backlog público](../backlog.json), reflejado en Jira. |
| Trabajo incremental | Datos y limpieza → rankings y visor → Power BI → revisión de perfiles. |
| Revisión del resultado | El caso de André Gomes y la [revisión de pivote y delantero](../analisis/PIVOTE_Y_DELANTERO.md). |
| Cierre basado en evidencia | Power BI se cerró después de ejecutar Desktop y contrastar 1.359 resultados. |
| Decisiones y límites documentados | [Metodología](../METODOLOGIA.md), Confluence y registros de validación. |
| Trazabilidad | La tarea referencia el análisis y el código; el repositorio conserva los cambios mediante commits. |

## Jira, Confluence y Scrum: qué puedo afirmar

El tablero actual tiene Por hacer, En curso y Listo. La forma de trabajo es iterativa y utiliza backlog, criterios de aceptación, revisión y adaptación, prácticas compatibles con Scrum. **No hay evidencia de sprints formalizados, Daily Scrums, un Scrum Master o un equipo Scrum.** Tener Jira y Confluence no demuestra por sí solo que se haya aplicado Scrum completo.

La [Scrum Guide](https://scrumguides.org/scrum-guide.html) define responsabilidades, eventos y artefactos que van más allá del tablero. No voy a añadir ceremonias o fechas retrospectivas para que el proyecto parezca algo distinto. En el CV lo describiría así: «Proyecto personal de análisis de datos, con seguimiento en Jira, documentación en Confluence y entregas iterativas con criterios de aceptación y validación reproducible».

Para una próxima iteración se puede practicar una adaptación individual: fijar un objetivo y un plazo antes de empezar, seleccionar trabajo del backlog, revisar el incremento al terminar y registrar una retrospectiva. Eso sería una práctica futura, no experiencia de Scrum en un equipo que ya haya sucedido.

## Criterio de terminado

Una entrega técnica está terminada cuando se puede reproducir, sus cálculos coinciden con las referencias, se han probado los casos relevantes, sus límites están documentados y el código y la evidencia están enlazados. Una decisión futbolística requiere además explicar los atributos, revisar resultados inesperados y dejar registrada la preferencia elegida. Una prueba de pesos no cierra por sí sola la estabilidad por partidos ni la validación predictiva.

## Revisión de esta entrega · 17/10/2026

Objetivo: comprobar pivote y delantero antes de cambiar pesos. Resultado: 108 puntuaciones base reconciliadas, 40.000 simulaciones de pesos y 48 recuentos directos de métricas sin diferencias. Augusto y Suárez conservan el liderato en el intervalo probado; los puestos siguientes dependen más de la función buscada, sobre todo en pivote.

Decisión: conservar la configuración publicada y documentar alternativas. La tarea de perfiles pasa a En curso, porque todavía faltan central, lateral, mediapunta y extremo y confirmar las preferencias finales. Las tareas de estabilidad por partidos y proveedores siguen Por hacer. El balance es ocho terminadas, una en curso y dos por hacer.

## Reflexión para la siguiente iteración

Ha sido útil cuestionar resultados que sorprenden y comprobarlos desde los eventos, en vez de ajustar pesos para que encajen nombres conocidos. El punto a mejorar es separar desde el principio tres preguntas: si el cálculo está bien, si el perfil representa la función buscada y si el resultado se sostiene en otra muestra. La próxima revisión debería aplicar esa separación a los cuatro perfiles restantes.

Esta reflexión se ha redactado con asistencia de IA a partir del trabajo realizado. No representa una reunión de retrospectiva de un equipo.

## Herramientas y capturas

- [Tablero Jira](https://jjrn87.atlassian.net/jira/software/projects/SCOUT/boards/3).
- [Documentación Confluence](https://jjrn87.atlassian.net/wiki/spaces/SCOUT/overview).
- [Galería pública de evidencias](../evidencias/README.md): permite ver el trabajo sin tener acceso a Atlassian.

Los enlaces de Atlassian pueden requerir acceso. Las capturas son una instantánea fechada, no una vista en directo.
