# Revisión de pivote y delantero

Revisión del 17/10/2026. Datos de LaLiga 2015/16. Fuente: [StatsBomb Open Data](https://github.com/statsbomb/open-data).

<img src="../assets/statsbomb-logo.png" width="230" alt="StatsBomb">

## Objetivo de la revisión

La pregunta era si los jugadores de arriba tienen sentido para la función que buscamos y si siguen ahí cuando cambiamos los pesos. Se analizan las métricas que los favorecen, las exclusiones y la variación del orden.

La conclusión es distinta para cada perfil. **En pivote hay un líder muy sólido, Augusto Fernández, pero bastante movimiento detrás. En delantero el grupo Suárez–Benzema–Gameiro es mucho más estable.** Esto describe el modelo y la temporada analizada; no demuestra que sean los mejores fichajes ni predice la siguiente temporada.

Los pesos oficiales no se han cambiado. Se han conservado el PBIX y los rankings ya contrastados. Las alternativas de esta revisión son escenarios para discutir, no una nueva configuración aprobada.

## Pesos y criterio futbolístico

### Pivote: recuperación y salida de balón

| Atributo | Base | Más salida | Recuperador | Distribuidor |
|---|---:|---:|---:|---:|
| Intercepciones por 90 | 25 | 25 | 30 | 15 |
| Entradas ganadas por 90 | 25 | 20 | 30 | 15 |
| Recuperaciones por 90 | 15 | 10 | 20 | 10 |
| Pases progresivos por 90 | 20 | 25 | 10 | 35 |
| Porcentaje de pase acertado | 10 | 15 | 5 | 20 |
| Menos desposesiones por 90 | 5 | 5 | 5 | 5 |

La base dedica 65 puntos a recuperar, 30 al pase y 5 a evitar desposesiones. Tiene sentido como primera aproximación a un pivote recuperador con salida, pero es demasiado amplio llamarlo simplemente «mejor pivote». La cohorte admite DM y CM, y no mide colocación sin intervención, coberturas o capacidad de impedir que el rival progrese.

Se conserva la base como referencia de **pivote recuperador**. «Más salida» representa una mayor prioridad por iniciar ataques. La precisión mantiene un peso moderado porque puede favorecer pases seguros. El peso 5 de desposesiones es deliberadamente pequeño; ese evento no incluye todas las pérdidas y tampoco está ajustado a cuántas veces recibe el jugador.

### Delantero: amenaza, producción y asociación

| Atributo | Base | Menos resultado y volumen | Finalizador | Asociativo |
|---|---:|---:|---:|---:|
| xG sin penaltis por 90 | 35 | 45 | 45 | 35 |
| Goles sin penaltis por 90 | 20 | 10 | 30 | 10 |
| Tiros por 90 | 15 | 10 | 10 | 10 |
| xG de tiros asistidos por 90 | 15 | 20 | 5 | 30 |
| Recepciones y tiros en el área por 90 | 15 | 15 | 10 | 15 |

La base es útil para revisar producción ofensiva histórica. La alternativa **45/10/10/20/15** propone menos dependencia de goles y volumen de tiros y algo más de creación. No es un peso «óptimo» demostrado.

En los 42 candidatos, las correlaciones de rangos son 0,85 entre xG sin penaltis y goles, 0,74 entre xG y tiros, y 0,80 entre tiros y el indicador de área. Por tanto, varios atributos recompensan dimensiones parecidas. Subir xG no elimina esa redundancia, pero explicita que preferimos generación de ocasiones a resultados observados. El indicador de área cuenta recepciones y tiros, no todos los toques; el volumen de tiros incluye penaltis, aunque goles y xG los excluyen. La creación total incluye balón parado. Son decisiones a revisar si hacemos una versión nueva del perfil.

## Por qué aparecen arriba

**Augusto Fernández:** no gana por un único atributo. Está en percentil 97,7 en intercepciones, 93,2 en entradas, 81,1 en recuperaciones, 78,0 en progresión y 91,7 en precisión. Los tres componentes defensivos aportan 59,89 de sus 87,42 puntos. La puntuación agrega su temporada en Celta y Atlético; no debe atribuirse a un solo equipo. Sus 2.190 minutos superan con margen el mínimo.

**Camacho e Illarramendi:** salen arriba por intercepciones, entradas y recuperaciones. Camacho pierde mucho si damos más valor al pase acertado: tiene 74,36 % y percentil 5,3 dentro de esta cohorte. Illarramendi lidera las intercepciones, pero queda por detrás de Augusto en otras dimensiones. La diferencia base entre ambos es de solo 0,30 puntos; los puestos segundo y tercero están muy próximos.

**Casemiro:** destaca en entradas (percentil 99,2) e intercepciones (96,2), pero la progresión del pase queda en 20,5. Es coherente que suba en el escenario recuperador y que cambie bastante con otro reparto. Con 1.527 minutos, además, su muestra es menor que la de otros candidatos.

**Busquets, puesto 31:** es una advertencia sobre el modelo. Tiene percentil 97,7 en precisión y 82,6 en entradas, pero 9,8 en intercepciones y 17,4 en recuperaciones. Esos dos últimos atributos pesan 40 puntos. Los recuentos se han contrastado directamente con los eventos y coinciden. Eso no permite concluir que fuera un mal pivote. La exposición defensiva y el rol pueden afectar estos volúmenes; el [diagnóstico de contexto](ESTABILIDAD_PARTIDOS_CONTEXTO.md) muestra su sensibilidad, sin atribuir causalmente la posición al equipo. [StatsBomb explica por qué la oportunidad de defender importa al comparar acciones por 90](https://blogarchive.statsbomb.com/articles/soccer/introducing-possession-adjusted-player-stats/).

**Suárez y Benzema:** ambos sobresalen en todas las métricas de remate. Benzema tiene más xG sin penaltis por 90 (0,789 frente a 0,678) y goles sin penaltis por 90 (1,087 frente a 1,057). Suárez gana el ranking combinado por creación: 0,305 de xG asistido por 90 frente a 0,137, además de mayor presencia en área. No es una contradicción: el perfil también valora lo que genera para otros.

**Gameiro:** combina amenaza de remate, creación y presencia en área, con percentiles 89,3, 91,7 y 91,7 respectivamente. Esa combinación sostiene su tercer puesto aunque no sea tercero en goles por 90.

**Aduriz y Agirretxe:** empatan en la puntuación base y comparten puesto 4. Agirretxe tiene percentil 94 en xG, goles y tiros, pero solo 3,6 en creación. Con más peso de finalización sube; con asociación baja. Además, son 1.169 minutos frente a los 2.776 de Aduriz. La estabilidad ante pesos no resuelve esa diferencia de muestra.

**Griezmann, puesto 9:** tiene buen percentil de goles (89,3) y creación (84,5), pero menos volumen de tiros y presencia en área. Solo un 61 % de sus minutos entra en ST y usamos estadísticas de toda la temporada. El perfil no mide su trabajo defensivo ni todos sus movimientos sin balón.

## Qué cambia al variar los pesos

Se hicieron 10.000 simulaciones por perfil con cada peso entre el 80 % y el 120 % de su base, y otras 10.000 entre el 50 % y el 150 %. Se normaliza el total, manteniendo fija la cohorte y los percentiles. **±20 % es un cambio relativo, no ±20 puntos porcentuales.** También se probó cada peso por separado, todas las combinaciones extremas del intervalo ±20 % (64 en pivote y 32 en delantero), quitar cada atributo y los escenarios de las tablas.

Las frecuencias son proporciones de estos escenarios; no probabilidades de que un jugador sea mejor. Un intervalo observado en simulación no es una garantía sobre todas las ponderaciones posibles.

### Pivote

| Jugador | Base | Puntos | Rango observado ±20 % | Top 3 en ±20 % | Rango observado ±50 % |
|---|---:|---:|---:|---:|---:|
| Augusto Fernández | 1 | 87.42 | 1–1 | 100.00 % | 1–1 |
| Ignacio Camacho | 2 | 72.73 | 2–6 | 84.78 % | 2–12 |
| Asier Illarramendi | 3 | 72.42 | 2–7 | 81.22 % | 2–11 |
| Casemiro | 4 | 71.14 | 2–11 | 21.53 % | 2–26 |
| Rubén Pérez | 5 | 70.98 | 3–8 | 4.46 % | 2–13 |
| Toni Kroos | 6 | 69.85 | 2–9 | 7.39 % | 2–20 |
| Sebastián Cristóforo | 7 | 69.24 | 3–12 | 0.13 % | 2–19 |
| Gabi | 8 | 68.33 | 2–14 | 0.49 % | 2–23 |
| Gonzalo Escalante | 9 | 67.80 | 5–14 | 0.00 % | 2–27 |
| Tiago | 10 | 66.67 | 6–17 | 0.00 % | 3–21 |

### Delantero

| Jugador | Base | Puntos | Rango observado ±20 % | Top 3 en ±20 % | Rango observado ±50 % |
|---|---:|---:|---:|---:|---:|
| Luis Suárez | 1 | 97.14 | 1–1 | 100.00 % | 1–1 |
| Karim Benzema | 2 | 93.10 | 2–2 | 100.00 % | 2–3 |
| Kévin Gameiro | 3 | 86.79 | 3–3 | 100.00 % | 2–4 |
| Aritz Aduriz | 4 | 79.76 | 4–5 | 0.00 % | 4–6 |
| Imanol Agirretxe | 4 | 79.76 | 4–7 | 0.00 % | 3–12 |
| Miku Fedor | 5 | 75.36 | 6–9 | 0.00 % | 4–12 |
| Álvaro Negredo | 6 | 75.00 | 5–9 | 0.00 % | 4–11 |
| Borja Bastón | 7 | 74.64 | 6–10 | 0.00 % | 6–12 |
| Fernando Torres | 8 | 73.81 | 6–9 | 0.00 % | 4–11 |
| Antoine Griezmann | 9 | 70.83 | 9–12 | 0.00 % | 5–13 |


Los empates reciben puesto denso: con dos jugadores en el puesto 4, el siguiente tiene puesto 5. Por eso un jugador puede bajar un puesto cuando se rompe un empate ajeno, aunque nadie nuevo le haya adelantado. «Top 10» significa puesto denso ≤10 y puede incluir más de diez personas.

### Cambios concretos de función

- **Pivote con más salida:** Augusto 1; Kroos 2; Modrić y Tiago empatan en 3; Illarramendi 4; Casemiro 5. No es una corrección para favorecer a Kroos, sino una preferencia distinta por el pase.
- **Pivote recuperador:** Augusto 1, Camacho 2, Casemiro 3, Illarramendi 4 y Escalante 5.
- **Delantero 45/10/10/20/15:** se mantienen Suárez, Benzema y Gameiro en los tres primeros puestos.
- **Delantero finalizador:** Suárez y Benzema empatan en el puesto 1; Agirretxe pasa al 2 y Gameiro al 3. El reparto ya se sale del intervalo de variación ±50 % de algunos pesos.
- **Delantero asociativo:** Suárez 1, Gameiro 2 y Benzema 3.

Hay una comprobación más fuerte que las simulaciones: para Augusto y Suárez se minimizó su ventaja frente a cada rival sobre todo el intervalo de pesos. Ambos mantienen matemáticamente el primer puesto para cualquier combinación de multiplicadores entre 0,5 y 1,5, con estos datos y percentiles fijos. La cota conservadora de ventaja es 1,82 puntos para Augusto y 0,24 para Suárez. Esto no cubre ponderaciones fuera de ese intervalo ni incertidumbre de los datos.

## Cohorte y minutos: lo que el ranking no muestra por sí solo

Pivote reúne 66 candidatos. Exigir al menos 50 % de minutos específicamente DM, en vez de DM+CM, deja 52 y no elimina a ninguno del top 10 base. Este es un diagnóstico de elegibilidad, sin recalcular percentiles.

Delantero reúne 42. Cristiano registra 20,7 % de minutos ST y Messi 4,5 %: quedan fuera por el filtro del 50 %, no porque puntúen peor. Neymar tampoco entra. Esta comparación no es un ranking de todos los atacantes de LaLiga.

Al exigir 1.500 minutos, conservando la referencia original, salen Agirretxe y Negredo en delantero y Tiago y Cristóforo en pivote. Al exigir 1.800 también sale Casemiro. Los líderes se mantienen. Esto comprueba el efecto de un filtro, no sustituye un remuestreo por partidos ni recalcula una nueva cohorte de percentiles.

## Validación y decisión de esta entrega

Se recalcularon los percentiles desde las métricas de temporada y se contrastaron las 108 puntuaciones y puestos base de ambos perfiles. Además, un recuento independiente recorrió los 380 archivos de eventos y comprobó seis métricas para ocho jugadores destacados: 48 comparaciones, cero diferencias. Las 13 pruebas unitarias pasaron.

Reproducción: `python -m src.analyze_profiles`, `python -m src.verify_review_players` y `python -m unittest discover -s tests -v`. Los resultados completos se guardan en `outputs/revision_pivote_delantero.json` y `outputs/review-players-verification.json`. El [resumen de evidencia](../evidencias/revision-perfiles.json) conserva método, comprobaciones y hashes, sin publicar la base de datos.

**Decisión de esta entrega:** aceptar la coherencia del cálculo y usar estos rankings como primera lista de candidatos, con las reservas indicadas. Conservar los pesos actuales como referencia y guardar las alternativas. En ese momento la tarea quedó en curso porque faltaban cuatro perfiles. La [revisión posterior](CENTRAL_LATERAL_MEDIAPUNTA_EXTREMO.md) completa el análisis descriptivo y cierra la tarea con las bases conservadas; el [análisis posterior por partidos y contexto](ESTABILIDAD_PARTIDOS_CONTEXTO.md) amplía esa revisión. Ver [decisiones de los siete perfiles](DECISIONES_PERFILES.md).

El hash del resultado completo de esta primera revisión corresponde a la versión del código publicada en el commit `8fc96d5`. La ampliación posterior añade campos de diagnóstico al JSON; no cambia los rankings ni las conclusiones de pivote/delantero.

No se ha vuelto a validar DAX para estas alternativas: se han probado en Python y no se han cambiado los pesos oficiales ni el informe. La validación anterior de Desktop sigue documentada por separado.
