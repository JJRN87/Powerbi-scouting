# Revisión de central, lateral, mediapunta y extremo

17/10/2026 · LaLiga 2015/16 · StatsBomb Open Data · Análisis con asistencia de IA.

<img src="../assets/statsbomb-logo.png" width="230" alt="StatsBomb">

Quería comprobar si los jugadores de arriba salían por un equilibrio de atributos o porque un peso concreto los favorecía demasiado. La conclusión es distinta para cada perfil: Mustafi y Neymar tienen lideratos sólidos dentro de los límites probados; Filipe Luis y Marcelo forman una pareja destacada cuyo orden depende de lo que busquemos; James e Isco están prácticamente igualados.

Conservo los pesos publicados como referencia. Las alternativas de esta revisión son escenarios para comparar funciones, no una nueva configuración oficial. Se cierra la revisión descriptiva de los siete perfiles, pero sigue pendiente comprobar estabilidad por partidos y contexto. No se han cambiado los datos, el PBIX ni las medidas DAX.

## Qué se ha comprobado

- 213 candidatos: 62 centrales, 66 laterales, 18 mediapuntas/interiores y 67 extremos. Todos cumplen 900 minutos y al menos un 50% en los roles admitidos.
- Recálculo de todos sus percentiles, puntuaciones y puestos base: cero diferencias.
- 10.000 combinaciones aleatorias por perfil con cada peso entre el 80% y el 120% de su valor base, y otras 10.000 entre el 50% y el 150%. Total: **80.000 simulaciones**, semilla 20261017.
- Cambios de un peso cada vez, las 64 combinaciones extremas de ±20% en cada perfil de seis atributos y las 32 de extremo, eliminación de un atributo y tres escenarios por función en cada perfil.
- Recuento directo desde los 380 archivos de eventos y las 380 alineaciones: 14 métricas de 14 jugadores (196 comparaciones) y cinco comprobaciones de minutos por jugador (70). Cero diferencias. No se utiliza el agregador para ese recuento.
- 14 pruebas unitarias superadas. [Registro público de evidencia](../evidencias/revision-cuatro-perfiles.json).

Cada peso se multiplica de forma independiente y la puntuación se divide por la suma resultante. ±20% no significa sumar o restar 20 puntos porcentuales. Los percentiles y la cohorte se mantienen fijos en las pruebas de pesos. Se usan puestos densos: dos jugadores empatados pueden ocupar el 5 y el siguiente el 6. Los porcentajes indican frecuencia en los escenarios, no probabilidad de que un jugador sea mejor.

## Central: Mustafi destaca por varios atributos

| Atributo | Base | Defensa y juego aéreo | Salida de balón | Sin penalizar exposición al regate |
|---|---:|---:|---:|---:|
| Entradas ganadas /90 | 20 | 25 | 15 | 20 |
| Intercepciones /90 | 20 | 25 | 15 | 25 |
| Duelos aéreos ganados /90 | 20 | 30 | 15 | 25 |
| Pases progresivos /90 | 20 | 10 | 30 | 20 |
| Pases acertados % | 10 | 5 | 20 | 10 |
| Veces superado por regate /90, invertido | 10 | 5 | 5 | 0 |

La base dedica un 60% a acciones defensivas, un 30% al pase y un 10% a ser superado menos veces. Tiene sentido como perfil general de central activo, pero cuenta intervenciones, no la calidad de su colocación ni la dificultad de cada duelo.

| Jugador | Puesto base | Puntos | Rango aleatorio ±20% | Rango aleatorio ±50% |
|---|---:|---:|---:|---:|
| Shkodran Mustafi | 1 | 80,32 | 1–1 | 1–2 |
| Diego Reyes | 2 | 70,81 | 2–4 | 1–17 |
| Gustavo Cabral | 3 | 67,26 | 2–6 | 2–16 |
| Sergio Ramos | 4 | 65,65 | 3–7 | 2–18 |
| Zé Castro | 5 | 63,23 | 3–12 | 2–24 |
| Zouhair Feddal | 6 | 62,74 | 3–12 | 2–27 |
| Diego Godín | 7 | 62,10 | 4–13 | 3–26 |

Mustafi está en percentiles 99,2 en entradas, 83,1 en intercepciones, 96,0 en juego aéreo y 87,9 en pase progresivo. Esas cuatro métricas aportan 73,23 de sus 80,32 puntos. Su debilidad es ser superado por regate: percentil invertido 8,9. El primer puesto no procede de ocultar esa debilidad; las otras dimensiones compensan la penalización.

Reyes destaca en entradas e intercepciones, pero queda en percentil 23,4 en pase progresivo. Por eso es segundo en la base y quinto en «Salida de balón». Cabral combina entradas y buen pase, con una penalización fuerte por regates sufridos. Ramos pasa del cuarto al segundo, empatado con Cabral, cuando priorizamos la salida. Godín sube del séptimo al tercero con defensa y juego aéreo.

El liderato de Mustafi está demostrado para **todo** el intervalo de multiplicadores 0,8–1,2 mediante comparación lineal contra cada rival, con margen conservador mínimo de 3,17 puntos. Con ±50% gana el 99,16% de las simulaciones y Reyes el 0,84%: ahí ya no hay garantía. Los tres escenarios por función mantienen a Mustafi primero. Al exigir 1.800 minutos se conserva el primer cuarteto.

**Decisión:** mantener la base como perfil general y mostrar la alternativa de salida cuando esa sea la prioridad. No vender el orden de los puestos 2–7 como estable. El indicador de regates sufridos y los conteos defensivos necesitan estudiar exposición y posesión; menos intervenciones no demuestra mejor defensa. Los duelos aéreos son victorias por 90, no porcentaje de victorias.

## Lateral: la pareja es más sólida que el orden

| Atributo | Base | Prioridad defensiva | Profundidad y creación | Progresión con pase |
|---|---:|---:|---:|---:|
| Pases progresivos /90 | 20 | 15 | 20 | 35 |
| Conducciones progresivas /90 | 20 | 10 | 25 | 15 |
| Pases que generan tiro /90 | 15 | 10 | 25 | 15 |
| Regates completados /90 | 15 | 5 | 20 | 5 |
| Entradas ganadas /90 | 20 | 35 | 5 | 20 |
| Intercepciones /90 | 10 | 25 | 5 | 10 |

La base ya es bastante ofensiva: un 70% en progresión, creación y regate frente a un 30% defensivo. Por eso la etiqueta incluye lateral/carrilero. Conducciones y regates tienen correlación de Spearman 0,758: no son iguales, pero al sumar ambos pesos se refuerza una cualidad parecida.

| Jugador | Puesto base | Puntos | Rango aleatorio ±20% | Rango aleatorio ±50% |
|---|---:|---:|---:|---:|
| Filipe Luis | 1 | 93,48 | 1–1 | 1–2 |
| Marcelo | 2 | 91,36 | 2–2 | 1–2 |
| João Cancelo | 3 | 78,33 | 3–5 | 3–9 |
| Abdoul Karim Yoda | 4 | 78,11 | 3–6 | 3–11 |
| Dani Alves | 5 | 75,23 | 3–9 | 3–16 |
| Daniel Carvajal | 5 | 75,23 | 3–10 | 3–19 |

Filipe Luis tiene percentiles entre 87,1 y 97,7 en los seis atributos. Marcelo le supera en pase progresivo, conducciones y creación; Filipe tiene ventaja en entradas e intercepciones. En ±50%, Filipe lidera el 91,78% de los escenarios y Marcelo el 8,22%. El escenario ofensivo coloca a Marcelo primero y Carvajal tercero; el defensivo coloca a Filipe primero y Danilo tercero. Cancelo solo es tercero en el 55,56% de las simulaciones de ±20%.

**La excepción que la simulación no detectó:** con pesos `24/24/18/12/16/8`, todos dentro del ±20% relativo antes de normalizar, Marcelo puntúa 92,8550 y Filipe 92,8253. Las 10.000 simulaciones no encontraron ese pequeño rincón, pero la prueba de combinaciones extremas sí. Por tanto, no afirmo que Filipe sea primero en todo el intervalo.

Yoda merece atención: percentiles 99,2 en conducciones y regates, pero solo 975,5 minutos. La fuente asigna un 82,0% de su tiempo a roles FB, que incluyen carrileros, y ese dato se ha contrastado con las alineaciones. Las estadísticas usadas son de toda su temporada, no solo de esos minutos. Al subir el mínimo a 1.500 desaparece de la lista; Filipe, Marcelo y Cancelo mantienen los tres primeros puestos.

**Decisión:** mantener la base para lateral/carrilero con participación ofensiva. Para una búsqueda defensiva usar el escenario específico. La pareja Filipe–Marcelo es consistente en las pruebas realizadas; el primer puesto y el tercer candidato dependen de la función. Yoda queda como candidato a revisar por muestra, no como una conclusión firme.

## Mediapunta: James e Isco están casi empatados

| Atributo | Base | Creador de ocasiones | Llegada y desborde | Menos doble peso a creación |
|---|---:|---:|---:|---:|
| xG de tiros asistidos /90 | 25 | 40 | 15 | 30 |
| Pases que generan tiro /90 | 20 | 20 | 10 | 5 |
| Pases progresivos /90 | 20 | 15 | 10 | 25 |
| Conducciones progresivas /90 | 15 | 10 | 20 | 20 |
| Regates completados /90 | 10 | 5 | 15 | 10 |
| xG sin penaltis /90 | 10 | 10 | 30 | 10 |

La base combina un 45% de creación, un 35% de progresión, un 10% de regate y un 10% de amenaza propia. Creación por volumen y por xG correlacionan 0,783; conducciones y regates, 0,750. Los pesos representan énfasis, no seis señales independientes.

| Jugador | Puesto base | Puntos | Rango aleatorio ±20% | Rango aleatorio ±50% |
|---|---:|---:|---:|---:|
| James Rodríguez | 1 | 85,56 | 1–2 | 1–2 |
| Isco | 2 | 85,28 | 1–2 | 1–3 |
| Éver Banega | 3 | 80,00 | 3–3 | 2–3 |
| Luka Modrić | 4 | 71,67 | 4–4 | 4–6 |
| Andrés Iniesta | 5 | 67,50 | 5–5 | 4–6 |
| André Gomes | 6 | 60,00 | 6–7 | 4–7 |

James lidera creación y pase progresivo dentro de esta cohorte: percentil 97,2 en las tres métricas. Isco alcanza ese mismo percentil en conducciones y regates. La diferencia base es solo **0,28 puntos**. En ±20%, James sale primero el 60,48% de las veces e Isco el 39,52%. Banega conserva el tercero en esas simulaciones y en las 64 combinaciones extremas.

«Creador de ocasiones» mantiene James–Isco–Banega. «Llegada y desborde» y «Menos doble peso a creación» colocan a Isco primero. No sería razonable resolver esa preferencia con una etiqueta de mejor jugador absoluto.

También influye quién entra: James acumula 1.514,9 minutos y un 52,5% en AM/CM; Isco, 1.831,8 y un 59,1%. Si se exige un 60% en esos roles, ambos quedan fuera. Con 1.800 minutos, James y Banega dejan de ser elegibles. El perfil admite interiores creativos; no es una lista pura de mediapuntas. Koke no entra porque solo tiene un 28,3% en AM/CM según la fuente.

**Decisión:** mantener la referencia, tratar James–Isco como una elección por función y presentar Banega como parte de la terna estable ante cambios moderados de pesos. Antes de buscar un mediapunta puro habría que redefinir la cohorte y recalcular sus percentiles, no eliminar nombres a mano.

## Extremo: Neymar lidera, pero el perfil no busca solo gol

| Atributo | Base | Desborde y progresión | Creador | Amenaza de gol |
|---|---:|---:|---:|---:|
| Regates completados /90 | 25 | 40 | 15 | 15 |
| Conducciones progresivas /90 | 20 | 30 | 15 | 15 |
| xG sin penaltis /90 | 20 | 10 | 10 | 40 |
| xG de tiros asistidos /90 | 20 | 10 | 40 | 20 |
| Pases que generan tiro /90 | 15 | 10 | 20 | 10 |

La base prioriza desborde/progresión (45%) y creación (35%); la amenaza de gol pesa un 20%. Volumen y xG asistido correlacionan 0,814. Esto representa un extremo que participa con balón, no cualquier atacante situado en banda.

| Jugador | Puesto base | Puntos | Rango aleatorio ±20% | Rango aleatorio ±50% |
|---|---:|---:|---:|---:|
| Neymar | 1 | 97,76 | 1–1 | 1–1 |
| Lionel Messi | 2 | 95,75 | 2–2 | 2–2 |
| Nolito | 3 | 85,75 | 3–3 | 3–4 |
| Yevgen Konoplyanka | 4 | 79,93 | 4–9 | 3–10 |
| Burgui | 5 | 79,25 | 4–7 | 4–10 |
| Gareth Bale | 6 | 78,88 | 4–9 | 3–12 |

Neymar combina percentiles entre 94,8 y 99,3. Messi lo supera en regates y xG sin penaltis; Neymar suma más en conducciones y creación. Se demuestra el liderato de Neymar para todo el intervalo de multiplicadores **0,5–1,5**, con un margen conservador de 0,0249 puntos. Es una garantía del cálculo en ese intervalo, no una comparación definitiva entre sus carreras.

Nolito es tercero en todas las simulaciones de ±20% y en las 32 combinaciones extremas. En el escenario creador, Konoplyanka pasa al tercero y Nolito al cuarto. Burgui combina conducción y creación, pero sus 979,4 minutos hacen que desaparezca al exigir 1.500. El primer trío sí permanece al exigir 1.800 minutos.

Cristiano Ronaldo queda 25 pese a liderar el percentil de xG sin penaltis (99,3). Sus percentiles de regates (29,1) y pases que generan tiro (33,6) explican el resultado. Al duplicar el peso del xG propio al 40% sube al 13, pero eso sigue siendo un perfil con varias funciones. Koke queda 44: la creación le favorece, la conducción y el regate no. Los roles W incluyen jugadores de banda más retrasados. No interpreto estas posiciones como calidad global ni adapto los pesos para colocar nombres conocidos arriba.

**Decisión:** conservar la base como extremo de desborde y creación, y ofrecer el escenario de amenaza de gol para otra necesidad. Neymar–Messi es la pareja más estable en estas pruebas; el tercero depende más de la función y de la definición de creación.

## Juego abierto y balón parado: una prueba diferente

En estos perfiles la creación sigue siendo total. Como diagnóstico adicional, se han sustituido pases que generan tiro y xG asistido por sus versiones de juego abierto, con la misma cohorte y los mismos pesos, recalculando los percentiles de esas dos métricas. **Esto cambia la definición, no solo los pesos**, por lo que se presenta aparte.

| Perfil | Primeros cinco, creación total | Primeros cinco, solo juego abierto |
|---|---|---|
| Mediapunta | James, Isco, Banega, Modrić, Iniesta | Isco, James, Banega, Modrić, Iniesta |
| Extremo | Neymar, Messi, Nolito, Konoplyanka, Burgui | Neymar, Messi, Bruma, Correa, Nolito |

El 52,4% del xG asistido de Banega procede del balón parado; también el 52,4% del de Burgui y el 41,7% del de Konoplyanka. Se han comprobado los totales y la parte de juego abierto desde los eventos. Las participaciones no explican por sí solas el cambio: el ranking depende de los percentiles relativos de toda la cohorte. James conserva sus percentiles de creación, pero Isco mejora respecto al grupo al retirar el balón parado.

Recomiendo ofrecer la separación también para mediapunta y extremo en una futura versión del modelo. Esta entrega deja medido su efecto; no añade controles ni sustituye las métricas de Power BI. El organizador ya dispone de esa separación.

## Cierre y siguientes pasos

La revisión de pesos queda documentada para los siete perfiles. La decisión de esta entrega es **mantener las bases como hipótesis de referencia**, conservar escenarios por función y señalar candidatos sensibles a pesos, minutos o roles. No se han aprobado pesos universales ni se ha validado rendimiento futuro. [Registro de decisiones de los siete perfiles](DECISIONES_PERFILES.md).

SCOUT-7 puede cerrarse porque cada perfil tiene justificación, sensibilidad y decisión registrada. SCOUT-8 sigue pendiente: remuestreo por partidos, estabilidad de candidatos con pocos minutos y contexto de equipo/posesión. SCOUT-11 sigue pendiente: decidir si compensa obtener datos actuales. La separación de creación en más perfiles es una mejora propuesta, pendiente de una nueva versión y de repetir las pruebas DAX si se implementa.

Las pruebas de esta revisión se ejecutaron en Python. Las 1.359 comparaciones de Power BI corresponden a la entrega anterior; no se presentan como pruebas nuevas de estos escenarios. Las estadísticas son de toda la temporada y los minutos excluyen el descuento, aunque los eventos lo incluyen. No se corrige aquí posesión, dificultad del rival ni incertidumbre de observación.

## Reproducir

Después de descargar y construir la base siguiendo el README:

```powershell
python -m src.analyze_profiles --group cuatro_perfiles
python -m src.verify_remaining_players
python -m unittest discover -s tests -v
```

Los resultados completos quedan en `outputs/revision_cuatro_perfiles.json` y `outputs/remaining-players-verification.json`, fuera de Git. Los hashes y el resumen publicable están en [revision-cuatro-perfiles.json](../evidencias/revision-cuatro-perfiles.json). [Definiciones de métricas](../METODOLOGIA.md) · [Fuente](https://github.com/statsbomb/open-data) · [Atribución](../assets/ATRIBUCION.md).
