# Informe interactivo en Power BI Desktop

El archivo local listo para abrir es `Powerbi-scouting/Powerbi-scouting.pbix`. Incluye datos cargados. La versión reproducible es el PBIP de la misma carpeta.

## Abrir y reproducir

1. Generar los datos siguiendo el README del proyecto.
2. Ejecutar `python -m src.build_powerbi` desde la raíz. Genera el PBIP, el modelo y `data/processed/qa_expected.csv`.
3. Abrir `powerbi/Powerbi-scouting/Powerbi-scouting.pbip` con Power BI Desktop.
4. Pulsar **Actualizar**. La primera apertura no contiene caché de datos.
5. Revisar **Validación con Python**: las seis filas deben tener cero errores en las tres columnas de errores y coincidir en candidatos reales y esperados.

El generador escribe la ruta local de los CSV en el parámetro Power Query `CarpetaDatos`. Tras mover o clonar el proyecto, volver a generar o editar ese parámetro. Ejecutar el generador reconstruye el diseño; guardar aparte los cambios visuales manuales que se quieran conservar.

## Usar el informe

- **Perfil / posición:** selección única entre siete perfiles. El informe abre en organizador.
- **Equipo:** restringe los candidatos visibles. Los percentiles de referencia y las puntuaciones permanecen fijos; el puesto interactivo se recalcula dentro de la selección.
- **Ocho pesos:** cada desplegable acepta un entero de 0 a 100. Sin selección (`Todas`) usa el peso base que indica el título. El valor seleccionado aparece en el desplegable. Cero elimina el atributo; todos los pesos cero dejan puntuación y puesto vacíos.
- **Cambio de perfil:** limpiar los pesos seleccionados con el icono de borrador del segmentador. Los controles numerados representan atributos distintos en cada perfil. Los controles «No aplica» se ignoran.
- **Tabla:** puesto actual, jugador, equipo, minutos, proporción de tiempo en el rol, puntuación, puesto base de la cohorte completa y cambio de puntuación. Orden inicial por puntuación descendente.

Las puntuaciones se redondean a ocho decimales antes de ordenar, aunque se muestran dos. Los empates reciben el mismo puesto denso. La cohorte exige 900 minutos y 50% de tiempo en los roles; cambiar esos umbrales exige reconstruir los datos, no solo filtrar el informe.

## Validación en el motor de Desktop

La página de validación ejecuta las mismas medidas de puntuación y ranking que el informe, con referencias calculadas en Python. Se comprueban 1.359 filas:

| Escenario | Candidatos |
|---|---:|
| Pesos base, siete perfiles | 387 |
| Todos los pesos cero | 387 |
| Solo el primer atributo a 100 | 387 |
| Organizador: progresión 32 y regate 8 | 66 |
| Organizador: progresión 35 y regate 5 | 66 |
| Organizador: progresión 25 y xG abierto 25 | 66 |

«Solo progresión» es la etiqueta técnica del escenario que deja únicamente el primer atributo de cada perfil; ese atributo no siempre es pase progresivo. La consulta completa está en `Scouting.SemanticModel/DAXQueries/Validacion.dax`. Los resultados de la página se recalculan al actualizar el modelo; no son una respuesta escrita a mano.

La prueba controla tamaño de cohorte, nulos, puntuaciones (tolerancia 1e-7) y puestos exactos. Usa `COUNTROWS(rankings)` como expresión de conservación de filas: una constante habría retenido candidatos de otros perfiles con resultados vacíos bajo la semántica de SUMMARIZECOLUMNS. La comprobación de datos general `python -m src.validate` sigue siendo una prueba Python; su campo `powerbi_engine_tested: false` describe esa ejecución, no sustituye la evidencia independiente de Desktop.

## Modelo y mantenimiento

Se importan rankings, perfiles, pesos, métricas, detalle y sensibilidad. Relaciones de una dirección: profiles → rankings → ranking_detail y metrics → ranking_detail. Las tablas Peso1…Peso8 están desconectadas; sus selecciones entran en las medidas. `qa_expected` contiene la referencia y `QA_resultados` es una tabla calculada por DAX.

Para modificar pesos base: editar `config/profiles.json`, ejecutar `python -m src.build` y `python -m src.build_powerbi`, cerrar y reabrir el PBIP y actualizar. Para explorar pesos temporalmente basta con los desplegables.

Las tasas del informe corresponden a la temporada completa, sin ajuste por posesión ni rival. El [análisis por partidos y contexto](../docs/analisis/ESTABILIDAD_PARTIDOS_CONTEXTO.md) se ejecuta aparte en Python. Los pesos son hipótesis de scouting. La validación técnica no demuestra calidad predictiva ni determina por sí sola la mejor posición de un jugador.

## Archivos y atribución

El PBIP/PBIR y el generador se pueden versionar. Los CSV, la caché y el PBIX con datos se conservan localmente. Fuente de datos: StatsBomb Open Data; consultar su licencia y atribución antes de compartir análisis. El tema base CY24SU02 procede de Microsoft/BCApps, bajo la licencia MIT incluida en `base-theme/LICENSE-Microsoft.txt`.

Comprobado en Desktop el 17/10/2026: seis escenarios y 1.359 filas, sin diferencias. Evidencia local en `outputs/powerbi-verification.json` y capturas asociadas.
