# Alcance y cierre de Powerbi-scouting

## Propósito

Proyecto personal para practicar la preparación y el análisis de datos con Python y construir un informe interactivo en Power BI. El caso práctico es comparar jugadores según el tipo de futbolista que se busca.

Se utiliza LaLiga 2015/16 de StatsBomb Open Data. El análisis histórico terminó el 17/10/2026. El proyecto se cierra el 21/10/2026 con la publicación de la demo y la actualización del seguimiento. Evaluar proveedores actuales y adaptar nuevas fuentes son posibles ampliaciones, fuera de este cierre.

## Resultado entregado

| Parte | Resultado |
|---|---|
| Datos | Descarga con versión de origen fijada, reglas de limpieza y tablas SQLite/CSV. |
| Análisis | Siete perfiles, percentiles, pesos editables y detalle de contribuciones en el visor HTML. |
| Power BI | Informe con perfiles, filtro de equipo, ocho controles de peso y página de validación. |
| Demo pública | Siete perfiles, pesos editables, filtro de minutos y contribuciones en el navegador, sin instalar nada. |
| Comprobaciones | Pruebas de datos y fórmulas; revisión de pesos, minutos, partidos y contexto. |
| Documentación | Explicación sencilla, método, reproducción, análisis y capturas. |
| Seguimiento | Tareas y criterios en Jira, decisiones en Confluence e historial en GitHub. |

La fuente contiene 380 partidos, 20 equipos, 539 jugadores y 1.295.354 eventos. Los perfiles generan 387 candidaturas jugador-perfil de 311 personas distintas; una persona puede entrar en varios perfiles. Se exigen 900 minutos y un 50 % de tiempo en los roles admitidos. Las estadísticas corresponden a toda la temporada del jugador, no solo a sus minutos en ese rol.

## Decisiones de preparación

Las tablas se relacionan por identificadores, evitando depender de los nombres. Los pases de resultado desconocido o Injury Clearance quedan fuera del porcentaje evaluable. Los porcentajes se calculan a partir de totales y permanecen nulos cuando no tienen denominador.

Los minutos se limitan al tiempo reglamentario y los eventos del descuento se conservan. Si un pase creador carece del tiro enlazado, el cálculo se detiene. Los controles revisan duplicados, referencias, marcadores y conservación de totales. No se descartan valores extremos solo porque un jugador destaque.

Estas reglas comprueban la coherencia del procesamiento con la fuente. No equivalen a revisar manualmente cada acción del proveedor. [Metodología completa](METODOLOGIA.md).

## Qué está comprobado

| Comprobación | Resultado y alcance |
|---|---|
| Archivos y datos | 764 hashes de origen, 539 jugadores y 387 puntuaciones reconciliadas en la validación general. |
| Python y Power BI | 1.359 comparaciones en seis escenarios, sin diferencias de puntuación, puesto o grupo. Incluye pruebas representativas de filtros y pesos en Desktop. |
| Revisión de perfiles | Siete perfiles con atributos, sensibilidad y decisiones documentadas. |
| Partidos y contexto | 387 puntuaciones base y 6.842 totales contrastados; 2.000 muestras de partidos y 2.000 de jornadas. |
| Pruebas automatizadas | 18 pruebas con NumPy instalado. Sin NumPy se omiten las cuatro del análisis de estabilidad. |
| Demo web | 387 puntuaciones y puestos base comprobados al exportar. Siete perfiles, 387 puntuaciones visibles y controles revisados en la web publicada. |

Los registros conservan las pruebas de cada entrega: [Power BI](evidencias/powerbi-validacion.json), [pivote y delantero](evidencias/revision-perfiles.json), [cuatro perfiles restantes](evidencias/revision-cuatro-perfiles.json) y [partidos y contexto](evidencias/estabilidad-partidos.json).

Las revisiones posteriores de pesos y contexto se ejecutaron en Python. Las 1.359 comparaciones de Desktop corresponden a los seis escenarios documentados, no a todos los análisis posteriores.

## Interpretación de los resultados

El ranking responde a las preferencias elegidas. André Gomes cambia de tercero a quinto como organizador al aumentar el peso del pase progresivo y reducir el del regate. Yoda y Burgui muestran más variación por su muestra pequeña de minutos. Estos casos permiten entender qué mide el informe y dónde tiene límites.

La puntuación combina posiciones relativas dentro de un grupo; no representa una probabilidad de éxito ni permite comparar perfiles distintos directamente. No se ha probado capacidad predictiva, valoración económica ni una estimación de calidad individual aislada del equipo.

## Desarrollo y organización

El autor ha definido el objetivo y solicitado revisiones de métricas, pesos y resultados. La IA ha apoyado código, documentación y comprobaciones. El ranking es una fórmula explícita y el xG procede de StatsBomb; no se ha entrenado un modelo de aprendizaje automático.

El proyecto se cierra con once tareas terminadas: las diez entregas del análisis histórico y SCOUT-12/PUB-03, la demo pública y el cierre. No quedan tareas por ejecutar dentro de esta entrega. SCOUT-11/DAT-03 se conserva como propuesta futura de evaluación de datos actuales, aplazada y fuera del alcance cerrado. No se marca como trabajo realizado. [Organización e historial](gestion/FORMA_DE_TRABAJO.md).

## Presentación pública

La [demo](https://jjrn87.github.io/Powerbi-scouting/) permite probar los perfiles sin cuenta ni descarga. Es una presentación HTML del análisis; el informe nativo de Power BI forma parte del proyecto por separado. Los percentiles de referencia son fijos y los cambios de cada visitante solo afectan a su sesión. [Alcance y validación de la demo](DEMO.md).

GitHub reúne el código, la documentación, el backlog y las capturas de seguimiento. Jira y Confluence requieren acceso al sitio: no hace falta entrar en ellos para consultar los resultados ni el cierre. [Registro de publicación](evidencias/cierre-publicacion.json).

## Reproducción y ampliación

GitHub incluye el código, la configuración, el proyecto PBIP y la documentación. Los datos originales, los CSV completos, la base y el PBIX cargado se generan o conservan localmente. [Pasos para reproducir](REPRODUCIR.md).

La estructura separa entrada, cálculo y presentación, pero varios archivos contienen supuestos de LaLiga 2015/16. Adaptar otra fuente exige revisar esos supuestos y repetir la validación. [Propuesta de ampliación](FUTURO.md).

La atribución y la licencia de los datos se conservan por separado del código propio. El repositorio no declara una licencia de reutilización para el código propio; la licencia de StatsBomb no se extiende automáticamente a él.
