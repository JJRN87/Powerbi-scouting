# Estabilidad por partidos y contexto de equipo

LaLiga 2015/16 · StatsBomb Open Data · 17/10/2026.

<img src="../assets/statsbomb-logo.png" width="230" alt="StatsBomb">

Los primeros candidatos suelen mantenerse, pero el orden exacto cambia más al variar los partidos que al variar ligeramente los pesos. Yoda y Burgui son los casos más claros: su resultado justifica incluirlos en una lista de seguimiento, pero no considerar firmes sus puestos cuarto y quinto.

Se conservan los pesos y el ranking oficial. Este análisis se ejecuta aparte en Python; no modifica Power BI.

## Yoda y Burgui

| Medida | Yoda · lateral/carrilero | Burgui · extremo |
|---|---:|---:|
| Puesto base | 4 | 5 |
| Minutos reglamentarios | 975,6 | 979,4 |
| Partidos con minutos reglamentarios | 17 | 26 |
| Titularidades | 8 | 8 |
| Apariciones de hasta 30 minutos | 5 | 13 |
| Puesto mediano al remuestrear partidos | 5 | 8 |
| Rango central del 95% de las muestras | 2–22 | 3–27 |
| Presencia en top 10 | 77,0% | 65,7% |
| Presencia en top 3 | 31,9% | 5,8% |
| Rango central al remuestrear jornadas completas | 2–22 | 3–25 |
| Top 10 al remuestrear jornadas | 80,3% | 67,3% |

Los rangos contienen la parte central de los resultados simulados, no todos los casos posibles ni una predicción de rendimiento futuro. Las tasas se calculan sumando acciones y minutos, sin promediar los valores por 90 de cada aparición. Los partidos con cero minutos reglamentarios conservan sus eventos, según la regla general del proyecto.

### Cuánto pesa un solo partido

Al retirar un partido de la competición cada vez y recalcular el ranking, Yoda se mueve entre el 3 y el 8, y Burgui entre el 4 y el 9. El partido se elimina para todos sus participantes; también se recalculan los percentiles del grupo.

- **Yoda:** sin el Getafe–Celta del 27/02/2016 pasa del 4 al 8. En ese partido registra tres pases que generan tiro y seis conducciones progresivas.
- **Burgui:** sin el Las Palmas–Espanyol del 22/04/2016 pasa del 5 al 9. Sus tres pases que generan tiro suman 0,980 de xG asistido: el 32,2% de su total de temporada.

En esta prueba se mantiene la lista original de candidatos para medir el efecto del partido. Si se reaplicara el mínimo de 900 minutos tras retirar esos encuentros de 90 minutos, ambos quedarían fuera. No se interpreta ese ranking de diagnóstico como una nueva lista de elegibles.

**Conclusión:** los dos destacan en métricas concretas, pero tienen poca exposición y bastantes apariciones cortas. Burgui presenta más variación. El análisis por jornadas confirma la misma lectura; no depende solo de cómo se han agrupado los partidos.

## Qué ocurre en los siete perfiles

Resultados del remuestreo de partidos, con pesos constantes:

| Perfil | Líder base | Rango central del 95% | Frecuencia en el primer puesto |
|---|---|---:|---:|
| Central | Mustafi | 1–3 | 85,4% |
| Lateral | Filipe Luis | 1–2 | 63,4% |
| Pivote | Augusto Fernández | 1–3 | 91,1% |
| Organizador | Luka Modrić | 1–2 | 95,5% |
| Mediapunta | James Rodríguez | 1–3 | 44,0% |
| Extremo | Neymar | 1–2 | 83,7% |
| Delantero | Luis Suárez | 1–2 | 84,8% |

Mustafi, Augusto, Modrić, Neymar y Suárez conservan una posición destacada en la mayoría de las muestras. Esto es compatible con que pierdan el primer puesto en algunas de ellas: una garantía ante cambios de pesos no era una garantía ante cambios de partidos.

En lateral, Marcelo ocupa el primer puesto en el 36,5% de las muestras. En mediapunta, Isco lo ocupa en el 49,4% y Banega en el 9,6%; James no es un líder claro. Los porcentajes pueden sumar más del 100% porque se cuentan los empates en el primer puesto.

Detrás de los líderes hay más movimiento: André Gomes tiene un rango central de 2–23 como organizador, Nolito de 3–11 como extremo y Gameiro de 2–15 como delantero. La estabilidad al cambiar pesos no basta para asegurar sus puestos concretos.

## Contexto del equipo

Las oportunidades de atacar y defender dependen del equipo. Para explorar ese efecto se usa, en cada partido, la proporción de pases evaluables intentados por el equipo sobre el total de ambos equipos. **Es una aproximación al control del balón, no un porcentaje de posesión medido en tiempo.** No mide el contexto exacto durante los minutos de cada jugador ni separa marcador, rival o dificultad de las acciones.

Se comparan tres escenarios, recalculando métricas y percentiles pero conservando candidatos y pesos:

| Escenario | Tratamiento |
|---|---|
| Solo defensa | Ajusta entradas ganadas, intercepciones, recuperaciones y regates sufridos. |
| Ataque y defensa, moderado | Ajusta los volúmenes ofensivos y defensivos con la raíz cuadrada del factor completo. |
| Ataque y defensa, completo | Usa el factor completo en ambos grupos. |

Con `s = pases del equipo / pases de ambos equipos`, el factor ofensivo es `0,5 / s` y el defensivo `0,5 / (1 − s)`. Se multiplica cada conteo de cada jugador-partido por su factor, se suman los conteos ajustados y se dividen por los minutos totales para obtener la tasa por 90. El escenario moderado usa la raíz cuadrada de esos factores. No se ajustan minutos, precisión de pase ni duelos aéreos, porque estos últimos no distinguen aquí acciones ofensivas y defensivas. Los regates sufridos y las desposesiones mantienen su orientación negativa.

El escenario completo es una prueba exigente, no una corrección validada ni una fórmula oficial de StatsBomb. La proporción de pases por equipo-partido va del 22,3% al 77,7%; no hay divisiones por cero. Comparar intensidades muestra cuánto depende la conclusión del propio ajuste.

| Jugador y perfil | Base | Solo defensa | Moderado | Completo |
|---|---:|---:|---:|---:|
| Yoda · lateral | 4 | 9 | 4 | 4 |
| Burgui · extremo | 5 | 5 | 4 | 3 |
| Filipe Luis · lateral | 1 | 2 | 2 | 2 |
| Marcelo · lateral | 2 | 1 | 1 | 1 |
| Busquets · pivote | 31 | 13 | 23 | 15 |
| Luis Suárez · delantero | 1 | 1 | 1 | 2 |
| Benzema · delantero | 2 | 2 | 2 | 1 |

La proporción de pases de los equipos de Yoda y Burgui, ponderada por sus minutos, es del 46,3% y el 45,2%. El contexto no elimina sus buenas métricas: Burgui incluso sube al ajustar ataque. Pero ese ajuste **no añade partidos ni reduce la incertidumbre de su muestra**. Yoda baja al ajustar solo defensa y recupera su posición cuando también se ajusta ataque.

Busquets mejora al considerar oportunidades defensivas. Es un indicio de sensibilidad al contexto; no demuestra que el ajuste haya aislado su calidad individual ni que explique causalmente su puesto.

| Perfil | Candidatos del top 10 base que permanecen en top 10 con el ajuste completo |
|---|---:|
| Central | 8 de 10 |
| Lateral | 9 de 11 |
| Pivote | 8 de 10 |
| Organizador | 10 de 10 |
| Mediapunta | 8 de 10 |
| Extremo | 6 de 10 |
| Delantero | 8 de 11 |

El top 10 usa puesto denso ≤10 y puede contener más de diez personas por empates. Extremo es el perfil cuyo grupo de cabeza más cambia en este escenario; organizador conserva sus diez candidatos, aunque cambia parte del orden. En mediapunta James e Isco empatan primeros; en delantero Benzema supera a Suárez.

Como descripción adicional de los rivales, Yoda concentra el 39,5% de sus minutos ante los equipos del grupo de seis con más puntos de la temporada, frente al 21,6% de Burgui. Este dato no corrige la dificultad del rival ni permite atribuirle el resultado. Se calcula desde los marcadores de la propia temporada y no se utiliza para predecir.

## Método de remuestreo

1. Se fijan los 387 candidatos de los siete perfiles y sus pesos. El mínimo de minutos y los roles se aplican a la temporada observada, no a cada muestra.
2. Se generan 2.000 muestras de 380 partidos con reemplazo: un partido puede repetirse o no aparecer. Todos sus participantes reciben la misma multiplicidad, conservando la relación entre compañeros y rivales.
3. Se suman los conteos y minutos de cada jugador, se recalculan tasas y porcentajes, y después percentiles y puestos dentro del perfil. Las métricas de un partido permanecen juntas.
4. Como contraste, se generan otras 2.000 muestras de las 38 jornadas completas. Los partidos de cada jornada se mueven juntos, según la jornada registrada en la fuente.
5. Se resumen los percentiles 2,5 y 97,5 de los puestos y las frecuencias de top 1, top 3 y top 10. Los empates conservan ranking denso. La semilla es 20261018.

Son 4.000 muestras compartidas por los siete perfiles, no 28.000 muestras independientes. No hubo muestras sin minutos o denominadores válidos. También se recalculó el ranking retirando cada uno de los 380 partidos una vez.

El método describe la variación al reutilizar partidos observados. No crea situaciones nuevas, no recoge lesiones futuras y no modela toda la dependencia temporal entre encuentros. Los rangos son un resumen descriptivo, no intervalos calibrados de rendimiento futuro. No se combinan aquí cambios simultáneos de pesos, muestra y contexto.

## Validación y decisión

Se reconciliaron 6.842 totales jugador-métrica con la base y las 387 puntuaciones y puestos iniciales. Pasaron las 18 pruebas automatizadas, incluidas tasas desde totales, empates, dirección del ajuste y tratamiento de muestras sin minutos. Los hashes confirman que la base, los rankings y los pesos oficiales no cambiaron. [Registro de validación](../evidencias/estabilidad-partidos.json).

SCOUT-8/MOD-04 queda terminado como análisis exploratorio de estabilidad y contexto. Se conservan los rankings oficiales y se acompañan de estas limitaciones. Yoda y Burgui quedan identificados como candidatos de muestra reducida. No se incorporan automáticamente los ajustes de contexto al informe.

Queda pendiente evaluar proveedores de datos actuales. La predicción en otra temporada, el ajuste con posesión medida en tiempo y la separación por marcador o rival requieren estudios adicionales fuera del alcance de esta entrega.

## Reproducción

La construcción de datos usa la biblioteca estándar de Python. Este análisis añade NumPy; se ejecutó con la versión 2.3.5.

```powershell
python -m pip install -r requirements-analysis.txt
python -m src.analyze_match_stability
python -m unittest discover -s tests -v
```

El resultado completo se genera en `outputs/match-stability.json`, fuera de Git. La misma versión de NumPy y la semilla permiten reproducir el muestreo. Las pruebas de estabilidad se omiten si NumPy no está instalado; las restantes pruebas siguen disponibles.

Referencias: [remuestreo con reemplazo y muestras emparejadas, documentación de SciPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.bootstrap.html); [oportunidades defensivas y contexto, StatsBomb](https://blogarchive.statsbomb.com/articles/soccer/introducing-possession-adjusted-player-stats/). La implementación usa NumPy y una fórmula de contexto propia, no las funciones de SciPy ni el ajuste publicado por StatsBomb.
