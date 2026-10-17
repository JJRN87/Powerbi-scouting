# Power BI: validación de la versión finalizada

Actualizado el 17/10/2026.

La idea era llevar el análisis a Power BI y poder cambiar lo que buscamos en un jugador sin rehacer el ranking a mano. Esa parte ya está terminada. El informe se ha abierto, actualizado y probado en Power BI Desktop, y está guardado como PBIX local y como proyecto PBIP reproducible.

## Qué permite hacer

Elegir entre siete perfiles, filtrar por equipo y ajustar hasta ocho pesos. La tabla recalcula la puntuación y el puesto. También hay una página para comprobar los resultados de DAX contra una referencia calculada en Python.

El filtro de equipo conserva las puntuaciones y ordena los jugadores que quedan visibles. Al cambiar de perfil hay que borrar los pesos seleccionados para recuperar sus valores base: cada perfil puede usar atributos diferentes. Si todos los pesos son cero, el informe deja la puntuación y el puesto vacíos.

## Qué se ha comprobado

Las pruebas del motor de Power BI cubren 1.359 comparaciones en seis escenarios. No hubo diferencias en puntuaciones, puestos ni tamaño de la cohorte. La tolerancia de puntuación es 0,0000001; los puestos deben coincidir exactamente.

| Escenario | Comparaciones | Errores |
|---|---:|---:|
| Pesos base de los siete perfiles | 387 | 0 |
| Todos los pesos a cero | 387 | 0 |
| Solo el primer atributo de cada perfil | 387 | 0 |
| Organizador: progresión 32 y regate 8 | 66 | 0 |
| Organizador: progresión 35 y regate 5 | 66 | 0 |
| Organizador: progresión 25 y xG abierto 25 | 66 | 0 |

Son comparaciones de candidatos por escenario, no 1.359 jugadores distintos. En la interfaz también se probaron cambios de perfil, el filtro de Barcelona, cambios de pesos y la vuelta a los valores base. La prueba automática cubre los siete perfiles; la prueba manual de la interfaz usa casos representativos.

El ejemplo de André Gomes sirve para entender por qué había que comprobarlo. Con los pesos base queda tercero, por delante de Kroos y Trashorras. Al dar 35 a progresión y 5 a regate, Kroos pasa al tercer puesto, Trashorras al cuarto y André al quinto. Power BI reproduce el mismo resultado que Python. Su tercer puesto depende de lo que prioricemos en el perfil.

Antes de esta entrega también se comprobaron los datos: 10 pruebas unitarias, 764 archivos con hash verificado, 539 jugadores reconciliados y 387 puntuaciones base. La cobertura es de 380 partidos y 20 equipos. El contraste independiente de eventos se hizo sobre cinco partidos; no se ha revisado manualmente cada evento de la temporada.

## Dónde está el informe y cómo repetir la prueba

- [Proyecto Power BI](../powerbi/Powerbi-scouting/Powerbi-scouting.pbip) y [guía de uso](../powerbi/LEEME.md).
- [Generador](../src/build_powerbi.py): construye el informe y la referencia de Python.
- [Consulta de validación](../powerbi/Powerbi-scouting/Scouting.SemanticModel/DAXQueries/Validacion.dax).
- [Registro de esta validación](evidencias/powerbi-validacion.json): escenarios, resultados y hashes de los archivos comprobados.

Primero se reconstruyen los datos siguiendo el README. Después se ejecuta `python -m src.build_powerbi`, se abre el PBIP y se pulsa Actualizar. En la página «Validación con Python» deben aparecer seis filas con cero errores y el mismo número de candidatos reales y esperados.

El PBIX con los datos cargados se conserva localmente en `powerbi/Powerbi-scouting/Powerbi-scouting.pbix`. GitHub incluye el proyecto y el código para reproducirlo. Los datos, la caché y el PBIX no se publican. Las capturas de la sesión se conservan localmente en `outputs/`.

## Cierre y posibles ampliaciones

En el cierre de Desktop quedaron ocho tareas terminadas y tres pendientes. Posteriormente se completó la [revisión descriptiva de los siete perfiles](analisis/DECISIONES_PERFILES.md), conservando los pesos oficiales. El [análisis por partidos y contexto](analisis/ESTABILIDAD_PARTIDOS_CONTEXTO.md) también está terminado como diagnóstico separado. La versión histórica queda finalizada con diez tareas terminadas. Comparar proveedores actuales se aplaza como propuesta futura, fuera de este alcance. [Posibles ampliaciones](FUTURO.md).

El informe conserva las tasas originales. El diagnóstico de contexto usa proporción de pases, no posesión medida en tiempo. No hay validación predictiva, corrección por rival ni datos económicos. Por ahora el proyecto ayuda a localizar candidatos y explicar por qué aparecen arriba.

## Cómo se ha hecho

El desarrollo utiliza asistencia de IA en implementación, documentación y comprobaciones. Las revisiones de métricas y resultados, como el caso de André Gomes, forman parte de las decisiones documentadas del proyecto.
