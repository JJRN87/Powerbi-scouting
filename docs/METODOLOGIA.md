# Metodología v2 · LaLiga 2015/16

## Unidad de análisis

Fuente única: StatsBomb Open Data. Se utilizan los 380 partidos de LaLiga 2015/16, sus eventos y alineaciones. El manifiesto conserva enlaces al commit exacto y hashes del contenido original. No se descargan datos 360.

La tabla `player_match` contiene una fila por jugador y partido con participación según alineación, incluso si solo participó en el descuento y sus minutos reglamentarios son cero. `players_season` agrega por identificador de jugador, sumando su participación en todos sus clubes de esta competición. Los porcentajes de temporada se calculan con los numeradores y denominadores sumados; nunca se promedian porcentajes de partidos.

Los nombres y nacionalidades proceden del proveedor. Se prioriza su apodo cuando existe; los identificadores, no el nombre, se utilizan para unir tablas. No se inventan edades ni datos económicos.

## Minutos y posiciones

Se suman intervalos de las alineaciones, respetando cambios tácticos, sustituciones y salidas temporales. Se limita cada parte a sus 45 minutos reglamentarios. Un intervalo abierto finaliza en 90. Un jugador que entra a los 91 minutos tiene cero minutos reglamentarios; sus eventos se conservan en totales y sus tasas en ese partido son nulas. Los eventos en el descuento sí forman parte de los totales de temporada. Esta es una convención por 90 explícita, no tiempo efectivo con balón en juego.

Las posiciones se agrupan así:

| Código | Grupo | IDs StatsBomb |
|---|---|---|
| GK | Portero | 1 |
| CB | Central | 3, 4, 5 |
| FB | Lateral / carrilero | 2, 6, 7, 8 |
| DM | Mediocentro defensivo | 9, 10, 11 |
| CM | Centrocampista central | 13, 14, 15 |
| W | Extremo / centrocampista de banda | 12, 16, 17, 21 |
| AM | Mediapunta | 18, 19, 20 |
| ST | Delantero / segundo delantero | 22, 23, 24, 25 |

Un candidato necesita ≥900 minutos totales y ≥50% de esos minutos en la suma de los roles admitidos por el perfil. Puede entrar en varios perfiles. Se muestra su porcentaje de minutos en roles para hacer visible la mezcla. **Las estadísticas valoradas son las de toda su temporada, no únicamente las de sus intervalos en ese rol.** No se puntúan porteros en esta versión.

## Métricas

El diccionario completo se genera en `data/processed/metrics.csv`. Se exportan 36 métricas: 33 tasas por 90 y 3 porcentajes. Los conteos originales y denominadores también se conservan.

- **Pase acertado:** Pass sin `outcome`, conforme a la codificación StatsBomb. Los pases `Unknown` e `Injury Clearance` se apartan del denominador evaluable y quedan contados en `passes_excluded`. No se transforman en fallos.
- **Progresión:** campo StatsBomb de 120 × 80 unidades, dirección ofensiva hacia x=120. La distancia euclídea al centro de la portería (120,40) debe reducirse al menos 10 unidades y un 25%, terminando con x≥60. En pases se exige completado y se excluyen corners, faltas, saques de banda, de centro y de puerta. Es una definición propia versionada; no se etiqueta como métrica oficial del proveedor.
- **Pases al último tercio:** completados en juego abierto, inicio x<80 y final x≥80.
- **Pases que generan tiro:** `shot_assist`, `goal_assist` o enlace válido `assisted_shot_id`. Incluyen balón parado.
- **xG de tiros asistidos:** suma del `statsbomb_xg` de los tiros enlazados a los pases. Es una medida de creación basada en los tiros resultantes, no un modelo xA propio. Incluye balón parado.
- **Tiros a puerta:** resultados Goal, Saved o Saved to Post. Los autogoles no se atribuyen como goles del atacante.
- **Goles y xG sin penaltis:** excluyen Shot/type Penalty.
- **Entradas ganadas e intercepciones exitosas:** resultados Won, Success, Success In Play o Success Out, según tipo de evento.
- **Recuperaciones:** Ball Recovery sin `recovery_failure=true`.
- **Duelos aéreos ganados:** presencia de `aerial_won=true` en un atributo del evento, como máximo una vez por evento. No equivale a porcentaje de éxito aéreo.
- **Recepciones y tiros en el área:** proxy que cuenta recepciones completadas y tiros en x≥102, 18≤y≤62. No cuenta todos los contactos con el balón.
- **Desposesiones sufridas:** eventos Dispossessed. No incluye automáticamente pases fallados o malos controles; no equivale a pérdidas totales.
- **Tarjetas a suplentes sin participación:** se conservan como exclusiones de auditoría y no crean minutos o rendimiento ficticio.

La ausencia de eventos de una categoría en un partido íntegro puede dar un conteo cero. Una ratio sin denominador es nula. Cualquier candidato con una métrica activa nula queda sin puntuación; no se redistribuye silenciosamente su peso. Las métricas negativas se orientan para que un percentil alto siempre sea favorable.

## Percentiles y puntuación

Para cada perfil y métrica se toma la cohorte elegible. El percentil es:

`100 × (cantidad de valores inferiores + 0,5 × cantidad de valores iguales) / N`

Los empates comparten percentil. Una cohorte constante obtiene 50. Para métricas donde menos es mejor, se usa `100 − percentil`. La referencia queda fijada al reconstruir los datos. Los filtros de presentación no recalculan esa referencia.

`Puntuación = suma(peso × percentil orientado) / suma(pesos activos)`

Pesos finitos y no negativos; si todos son cero, no hay puntuación. La puntuación está entre 0 y 100, pero no es probabilidad, nota absoluta ni valor económico. Los empates de puntuación comparten puesto con ranking denso; el ID de jugador proporciona un orden de presentación determinista. Las puntuaciones de perfiles diferentes no deben compararse directamente.

Los perfiles y pesos están en `config/profiles.json`. No se han ajustado para situar a jugadores concretos arriba. La ponderación de goles, tiros y xG del delantero expresa una preferencia inicial por producción ofensiva, e introduce correlación, documentada en la revisión del perfil.

## Validación

La construcción comprueba cobertura (20 equipos, 38 partidos por equipo y cada pareja local/visitante una vez), eventos únicos dentro de cada partido, las dos partes completas, referencias de tiros asistidos, jugadores de los eventos, minutos individuales entre 0 y 90 y goles contra marcador, incluyendo autogoles. Ante errores sin explicar se detiene antes de exportar nuevos rankings.

`src.validate` comprueba hashes, integridad de la base, unicidad, sumas partido/temporada, denominadores, coherencia de la puntuación y concordancia de un muestreo directo de pases y tiros con los JSON. Las pruebas unitarias cubren descuento, ausencias temporales, penaltis, balón parado, datos ausentes, empates y cambios de orden al cambiar pesos.

La sensibilidad varía un peso por vez a 80% y 120% de su valor, normaliza el total y mantiene la cohorte fija. Exporta mejor/peor puesto y frecuencia de top 10. No es incertidumbre estadística ni validación predictiva. Los siete perfiles tienen revisión de atributos, pesos y escenarios. Para validar predicción habría que separar temporalmente entrenamiento y evaluación, sin utilizar estadísticas futuras para elegir pesos o percentiles.

## Límites

El ranking oficial no ajusta posesión, ritmo, rival, fuerza de equipo o marcador. El análisis separado de contexto utiliza proporción de pases como aproximación, no posesión medida en tiempo. Las acciones defensivas pueden crecer por mayor exposición y los pases seguros pueden inflar la precisión. El mínimo de minutos reduce muestras pequeñas, pero no elimina la variabilidad. No se han aplicado correcciones por fiabilidad ni inferido potencial.

No se incluyen mercado, salarios, lesiones ni disponibilidad para fichar. No se obtiene una conclusión de jugador infravalorado a partir de este ranking por sí solo. La muestra es histórica y las posiciones son las registradas entonces.


## Organizador v2: creación por contexto

La creación se divide de manera exhaustiva y sin duplicados entre juego abierto y balón parado. Balón parado comprende las secuencias del pase etiquetadas por StatsBomb como `From Corner` o `From Free Kick`, más cualquier pase de ejecución directa tipo Corner, Free Kick, Throw-in, Goal Kick o Kick Off que genere un tiro. Las fases completas de saque de banda, puerta y centro no se consideran balón parado: tras el saque, sus pases ordinarios entran en juego abierto. Los demás pases creadores, incluidos los de patrón Other, quedan en juego abierto por esta definición operativa.

Esto es una aproximación dependiente de las etiquetas de origen de posesión del proveedor, sin una ventana temporal adicional. Incluye segundas jugadas de córner/falta que mantengan esa etiqueta. Incluye más acciones que un recuento limitado a córners y faltas directos, por lo que sus porcentajes no son intercambiables.

Se conservan las métricas totales para los demás perfiles. Para cada jugador-partido y jugador-temporada, la suma de las dos clases coincide con el total, tanto en número de pases que generan tiro como en xG de sus tiros asistidos. Un pase creador sin tiro enlazado detiene el cálculo; nunca se rellena su xG con cero. En esta muestra todos los pases creadores tienen enlace.

Pesos organizador v2: progresión 30%, pases que generan tiro en juego abierto 15%, xG asistido en juego abierto 20%, pases que generan tiro a balón parado 2%, xG asistido a balón parado 3%, precisión de pase 5%, recuperaciones 15%, regates 10%. La creación ocupa 40% en total: 35% abierto y 5% balón parado. Los pesos son una propuesta inicial, no el resultado de entrenar un predictor.

El xG asistido es una suma por 90: combina volumen y calidad de los tiros, no calidad media por ocasión. Está correlacionado con el número de pases que generan tiro; los dos se ponderan dentro de un presupuesto total de creación de 40%.

La comparación reproducible se publica en `outputs/ORGANIZADOR_V2.md` y `data/processed/organizer_comparison.csv`. Distingue el perfil original v1 (25/20), el escenario 40/5 con creación total sin separar y el nuevo v2. El archivo histórico `config/history/profiles_v1.json` conserva los pesos originales. La cohorte sigue teniendo 66 jugadores. Los otros seis perfiles conservan exactamente sus puntuaciones y puestos.

## Estabilidad por partidos y contexto de equipo

El [análisis específico](analisis/ESTABILIDAD_PARTIDOS_CONTEXTO.md) conserva candidatos y pesos, remuestrea partidos o jornadas completas y recalcula tasas, percentiles y puestos. Usa 2.000 muestras por método y resume los percentiles 2,5 y 97,5 de los puestos. También retira cada partido una vez. Los rangos son descriptivos de la muestra observada y no predicen otra temporada.

El contexto se explora mediante la proporción de pases de cada equipo en cada partido. Se comparan ajustes defensivos y ajustes de ataque/defensa de dos intensidades. No se considera una corrección causal ni se incorpora a Power BI. La muestra, los pesos y el contexto se estudian por separado.
