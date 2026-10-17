# El proyecto explicado de forma sencilla

## La idea

Quería unir el fútbol con la práctica de análisis de datos y Power BI. La pregunta es sencilla: **si busco un tipo de jugador, ¿qué candidatos destacan en las cualidades que me interesan?**

Un organizador, por ejemplo, puede destacar por dar pases que hacen avanzar al equipo o por crear ocasiones. El informe permite decidir qué pesa más y ver cómo cambia la lista.

La temporada elegida es LaLiga 2015/16. Sirve como ejemplo histórico para construir y comprobar el proyecto, no como recomendación de fichajes actuales.

## De un partido al informe

StatsBomb registra acciones de los partidos, como pases, tiros y entradas. Python lee esos registros, los relaciona con jugadores y alineaciones y calcula las estadísticas. SQLite guarda las tablas y los CSV permiten importarlas en Power BI.

La limpieza aplica reglas concretas. Un pase cuyo resultado es desconocido no se cuenta como fallado. Un porcentaje sin intentos queda vacío, porque no disponer de datos es distinto de tener un resultado de cero.

Power BI presenta los candidatos, permite filtrar y recalcula el ranking cuando cambian los pesos. Python se utiliza también para comprobar que las cuentas coinciden.

## Cómo se comparan los jugadores

Primero se forma un grupo para cada perfil. Un jugador necesita al menos 900 minutos y haber pasado la mitad de su tiempo en las posiciones admitidas. Puede entrar en más de un grupo.

Los recuentos se expresan por 90 minutos. Por ejemplo, 10 acciones en 450 minutos equivalen a 2 por 90. Esto facilita la comparación, aunque unos pocos partidos siguen aportando menos información que una temporada completa.

Después se calcula un **percentil**: la posición relativa de cada valor dentro del grupo. Así se pueden combinar atributos con escalas distintas, como pases y tiros. En atributos negativos, como las veces que un jugador pierde el balón por una desposesión, un valor menor recibe una valoración mayor.

Por último, cada atributo recibe un **peso**, es decir, una importancia. La puntuación es la media ponderada de los percentiles.

Ejemplo simplificado e inventado:

| Jugador | Percentil de pase progresivo | Percentil de creación |
|---|---:|---:|
| A | 80 | 50 |
| B | 50 | 80 |

Con un 60 % de peso al pase y un 40 % a la creación, A suma `80 × 0,6 + 50 × 0,4 = 68` y B suma 62. Si se invierten los pesos, B obtiene 68 y A, 62. Los datos no cambian: cambia la preferencia.

Una puntuación de 80 no significa un 80 % de probabilidad de éxito. Tampoco permite comparar directamente un 80 de delantero con un 80 de central, porque se calculan con grupos y criterios diferentes.

## Qué significa crear ocasiones

Un pase que termina en tiro cuenta como creación. El **xG**, o goles esperados, es una estimación de la probabilidad de gol de un tiro, calculada por el proveedor. En el xG asistido se suma el xG de los tiros que siguen a los pases del jugador.

Dos jugadores pueden generar el mismo número de tiros y que los de uno sean de mayor peligro. Por eso se revisan tanto la cantidad de tiros generados como su xG.

El organizador distingue juego abierto y balón parado mediante etiquetas del proveedor. Los demás perfiles conservan creación total. La definición exacta, que incluye algunas segundas jugadas, está en la [metodología](METODOLOGIA.md).

## Qué se aprendió al revisar los resultados

André Gomes aparece tercero como organizador con los pesos base. Al priorizar el pase progresivo y reducir el regate, baja al quinto. Su posición responde al perfil elegido.

Yoda y Burgui destacan con pocos minutos. Al repetir el cálculo con distintas muestras de partidos, conservan el top 10 en el 77 % y el 65,7 % de las muestras. Es una señal de interés con incertidumbre, no un puesto definitivo.

El contexto del equipo también afecta a las estadísticas. Se ha explorado por separado con la proporción de pases de cada equipo; esa aproximación no equivale a medir la posesión en tiempo ni se incorpora al ranking de Power BI.

## El papel de la IA y el cierre

La IA ha apoyado la escritura de código, documentación y pruebas. Las preguntas, las revisiones solicitadas y las decisiones sobre el alcance han guiado el desarrollo. El cálculo final usa reglas visibles en Python y DAX, sin un modelo de IA que seleccione futbolistas.

Esta versión personal está finalizada: prepara datos históricos, ofrece un informe interactivo y documenta sus comprobaciones. No calcula precios de fichaje ni predice temporadas futuras. Usar otros datos queda como una [posible ampliación](FUTURO.md).
