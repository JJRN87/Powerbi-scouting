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

## Primera revisión: pivote y delantero · 17/10/2026

Objetivo: comprobar pivote y delantero antes de cambiar pesos. Resultado: 108 puntuaciones base reconciliadas, 40.000 simulaciones de pesos y 48 recuentos directos de métricas sin diferencias. Augusto y Suárez conservan el liderato en el intervalo probado; los puestos siguientes dependen más de la función buscada, sobre todo en pivote.

Decisión de esa primera entrega: conservar la configuración publicada y documentar alternativas. La tarea de perfiles pasó a En curso porque faltaban cuatro perfiles. Ese estado queda superado por el cierre documentado a continuación.

## Cierre de la revisión de perfiles · 17/10/2026

Central, lateral, mediapunta y extremo añaden 80.000 simulaciones y 213 candidatos reconciliados. El recuento directo comprueba 196 métricas y 70 valores de minutos sin diferencias. La prueba de extremos detectó que Marcelo puede superar a Filipe incluso dentro del ±20%, aunque las 10.000 simulaciones aleatorias no lo mostraron: una comprobación útil para no exagerar la robustez.

La decisión es mantener las bases y conservar alternativas por función. Los siete perfiles ya tienen justificación, sensibilidad y límites; [MOD-03/SCOUT-7](https://jjrn87.atlassian.net/browse/SCOUT-7) pasa a Listo como revisión descriptiva. No equivale a validar rendimiento futuro ni a elegir una preferencia universal. El balance actual es nueve tareas terminadas y dos por hacer: estabilidad por partidos/contexto y evaluación de datos actuales. La separación de creación en mediapunta y extremo queda como mejora propuesta, con diagnóstico realizado pero sin implementación.

## Reflexión para la siguiente iteración

Ha sido útil cuestionar resultados que sorprenden y comprobarlos desde los eventos, en vez de ajustar pesos para que encajen nombres conocidos. El punto a mejorar es separar desde el principio tres preguntas: si el cálculo está bien, si el perfil representa la función buscada y si el resultado se sostiene en otra muestra. La siguiente iteración debe abordar esa última pregunta, especialmente para Yoda y Burgui por sus pocos minutos, y separar el efecto de muestra del efecto de pesos.

Esta reflexión se ha redactado con asistencia de IA a partir del trabajo realizado. No representa una reunión de retrospectiva de un equipo.

## Herramientas y capturas

- [Tablero Jira](https://jjrn87.atlassian.net/jira/software/projects/SCOUT/boards/3).
- [Documentación Confluence](https://jjrn87.atlassian.net/wiki/spaces/SCOUT/overview).
- [Galería pública de evidencias](../evidencias/README.md): permite ver el trabajo sin tener acceso a Atlassian.

Los enlaces de Atlassian pueden requerir acceso. Las capturas son una instantánea fechada, no una vista en directo.
