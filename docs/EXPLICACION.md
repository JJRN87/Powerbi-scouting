# Explicar Powerbi-scouting

## Qué problema resuelve

Permite comparar candidatos que encajan en un perfil futbolístico y justificar el orden con atributos medibles. Hace explícita la preferencia del analista: un organizador que progresa con pases puede diferir de otro que regatea y crea ocasiones. No calcula por sí solo quién es el mejor futbolista ni quién está infravalorado económicamente.

## Por qué hay limpieza aunque los datos ya sean estructurados

Un JSON válido puede contener valores no evaluables, ratios sin denominador o eventos de personas sin minutos. El proceso define cómo tratarlos y deja evidencia. Por ejemplo, un pase Unknown no se convierte en fallado y un porcentaje sin intentos permanece nulo.

## Cómo se calcula una puntuación

Se seleccionan jugadores con minutos y roles suficientes. Se transforma cada métrica en un percentil dentro del perfil. Después se calcula la media ponderada de los percentiles. Ejemplo ficticio: percentiles 80 y 50 con pesos 60 y 40 producen `(80 × 60 + 50 × 40) / 100 = 68`. Cambiar pesos cambia la preferencia, sin cambiar los datos observados.

## Por qué usar tasas por 90 y percentiles

Las tasas facilitan comparar volúmenes con distinta participación. Los percentiles permiten combinar métricas con escalas diferentes. Se pierde información sobre la distancia absoluta entre jugadores; un puesto alto no dice cuánto mejor es una acción ni cuánto vale un fichaje. Las muestras pequeñas y el contexto siguen importando.

## Por qué separar creación abierta y balón parado

Los lanzadores de faltas y córners pueden acumular ocasiones por una función específica. La separación permite que el perfil priorice esa función o la creación abierta. El xG asistido suma el xG de los tiros resultantes: combina cantidad y calidad, y está relacionado con el número de pases que generan tiro.

## Qué enseñó revisar a André Gomes

La sorpresa en el ranking llevó a descomponer sus contribuciones y probar otros pesos. La ventaja puede depender de regates y recuperaciones aunque el perfil se llame organizador. El nombre del perfil no sustituye revisar su definición. `python -m src.analyze_organizer` permite reproducir el análisis manteniendo fija la cohorte.

## Qué está validado y qué falta

Se han comprobado integridad de archivos, cobertura, marcadores, agregaciones y fórmulas. El contraste independiente de eventos incluye una muestra de cinco partidos. El informe se ha ejecutado en Power BI Desktop: seis escenarios y 1.359 comparaciones con Python sin diferencias, además de pruebas de filtros y cambios de pesos en la interfaz. Falta revisar futbolísticamente los pesos y evaluar estabilidad por partidos. No hay validación predictiva ni ajustes por posesión o nivel del rival.

## Cómo describir la contribución y la IA

Una formulación coherente con el trabajo realizado es: «Proyecto de scouting histórico desarrollado con asistencia de IA. Definí el objetivo y participé en la revisión de métricas y sensibilidad de los rankings. El proceso incorpora limpieza documentada, controles reproducibles y un informe interactivo en Power BI Desktop con pesos ajustables y rankings contrastados con Python».

Antes de usarlo en una entrevista, conviene poder reproducir un cálculo, explicar una exclusión y justificar un cambio de pesos. La documentación sirve para practicar estas explicaciones; no sustituye la comprensión del autor.
