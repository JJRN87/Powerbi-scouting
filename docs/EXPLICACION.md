# Cómo funciona Powerbi-scouting

## Objetivo

Comparar jugadores que encajan en una función y explicar su posición mediante atributos medibles. Un organizador que avanza con pases puede diferir de otro que regatea y crea ocasiones. El ranking depende de esas preferencias; no calcula por sí solo el mejor futbolista ni el valor de un fichaje.

## Preparación de los datos

Los datos estructurados también necesitan reglas de limpieza. Un pase con resultado Unknown se excluye del porcentaje de acierto, sin contarlo como fallado. Un porcentaje sin intentos permanece nulo. Los eventos y las alineaciones se relacionan por identificadores y los totales de partido se contrastan con los de temporada.

## Cálculo de la puntuación

Se seleccionan jugadores con al menos 900 minutos y un 50% de tiempo en los roles del perfil. Cada métrica se transforma en un percentil dentro de ese grupo. La puntuación es la media ponderada de esos percentiles.

Ejemplo: percentiles 80 y 50 con pesos 60 y 40 producen `(80 × 60 + 50 × 40) / 100 = 68`. Cambiar los pesos modifica la preferencia, sin cambiar los datos observados.

Las tasas por 90 permiten comparar volúmenes con distinta participación. Los percentiles permiten combinar escalas diferentes, aunque no conservan la distancia absoluta entre los valores. Una puntuación de 80 no es una probabilidad de éxito.

## Creación de ocasiones

El organizador distingue juego abierto y balón parado. Así se separa la creación habitual de la función de lanzar faltas y córners. El xG asistido suma el xG de los tiros que siguen a los pases: combina cantidad y calidad de ocasiones. Los demás perfiles conservan creación total; la separación en mediapunta y extremo está analizada como alternativa.

## Resultados de las revisiones

André Gomes queda tercero como organizador con los pesos base y quinto al aumentar progresión a 35 y reducir regate a 5. El cambio se explica por las contribuciones de sus atributos. Los siete perfiles tienen escenarios que muestran ese tipo de sensibilidad.

Al variar la muestra de partidos, Yoda mantiene el top 10 en el 77% de las muestras y Burgui en el 65,7%. Sus pocos minutos hacen que sus puestos exactos sean más variables. El [análisis por partidos y contexto](analisis/ESTABILIDAD_PARTIDOS_CONTEXTO.md) distingue este efecto del cambio de pesos.

## Comprobaciones y alcance

Se han comprobado archivos, cobertura, marcadores, agregaciones y fórmulas. Power BI se ejecutó en Desktop: seis escenarios y 1.359 comparaciones con Python sin diferencias, además de pruebas de filtros y pesos en la interfaz. El análisis por partidos reconcilia las 387 puntuaciones base y utiliza 2.000 muestras de partidos y otras 2.000 de jornadas.

El contexto se explora mediante la proporción de pases de cada equipo, que no equivale a posesión medida en tiempo. Los ajustes son escenarios separados y no modifican Power BI. No hay validación predictiva, datos económicos ni una estimación de la calidad individual aislada del equipo.

## Desarrollo

El proyecto se ha desarrollado con asistencia de IA en código, documentación y comprobaciones. El objetivo, las revisiones solicitadas y las decisiones sobre los perfiles forman parte del proceso documentado en GitHub, Jira y Confluence.
