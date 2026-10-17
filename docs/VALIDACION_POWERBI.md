# Power BI: qué está terminado y qué falta

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

## Qué queda pendiente

El seguimiento queda en ocho tareas terminadas y tres pendientes:

1. Revisar futbolísticamente los siete perfiles: justificar atributos y pesos y revisar resultados inesperados sin ajustar el modelo para que salgan nombres concretos.
2. Estudiar la estabilidad por partidos y el contexto de equipo. Cambiar pesos mide nuestras preferencias; todavía falta medir cuánto depende el resultado de la muestra de partidos.
3. Comparar proveedores de datos actuales y decidir si merece la pena pagar, una vez revisado el caso histórico.

No hay validación predictiva, ajustes por posesión o rival, ni salarios o precios de fichaje. Por ahora el proyecto ayuda a localizar candidatos y explicar por qué aparecen arriba.

## Cómo se ha hecho

He preparado este proyecto con ayuda de IA y quiero dejarlo claro. Mi parte ha sido definir lo que quería buscar, pedir revisiones de métricas y cuestionar resultados como el de André Gomes. La IA ha ayudado con la implementación, la documentación y las comprobaciones. El objetivo es poder explicar de dónde salen los datos, qué limpieza se aplica y por qué un cambio de pesos mueve el ranking.
