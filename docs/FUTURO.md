# Posibles ampliaciones

La versión de LaLiga 2015/16 está finalizada. Las ideas siguientes quedan fuera de su alcance y no tienen ejecución ni contratación previstas.

## Otra temporada o fuente de fútbol

El enfoque se puede repetir: preparar datos, definir grupos comparables, calcular atributos, elegir pesos y revisar resultados. La implementación actual solo se ha comprobado con StatsBomb LaLiga 2015/16.

| Parte | Qué se puede reutilizar | Qué habría que adaptar |
|---|---|---|
| Entrada | Descarga con procedencia y comprobaciones de integridad. | Acceso, formatos, identificadores y permiso de uso de la nueva fuente. |
| Métricas | Cálculo de tasas, percentiles y medias ponderadas. | Definición de cada evento, coordenadas, minutos, posiciones y significado de los nulos. |
| Modelo de datos | Separación de jugadores, partidos, perfiles y resultados. | Claves de proveedor, competición y temporada para evitar mezclar registros. |
| Power BI | Filtros, controles de peso, medidas y estructura del informe. | Tablas de entrada, etiquetas, relaciones y referencias de validación. |
| Validación | Pruebas de reglas, agregados y concordancia Python–DAX. | Cobertura esperada, casos de prueba y resultados de referencia de la nueva muestra. |

Hoy existen rutas y comprobaciones específicas: `11/27` en la descarga, 380 partidos, 20 equipos y 38 jornadas en distintas partes del proceso. El informe y algunos análisis también contienen etiquetas, perfiles y candidatos de esta temporada. Modificar solo `source-lock.json` o sustituir un CSV no adapta el proyecto.

Un adaptador futuro convertiría la nueva fuente a tablas comunes de partidos, jugadores, minutos por posición y métricas por jugador-partido. Conservaría los identificadores y la procedencia de cada dato. Una métrica no disponible quedaría identificada como ausente: cero significaría que se ha observado y no ocurrió la acción.

Los datos agregados por temporada permitirían un ranking si incluyen las métricas y los minutos necesarios, pero no bastarían para repetir las pruebas por partidos. Sin alineaciones o minutos por rol tampoco se podría aplicar el filtro de posiciones actual de la misma forma.

Cada competición y temporada tendría su grupo de referencia. Los percentiles de ligas distintas no demuestran una equivalencia de nivel entre ellas.

## Pasos de una futura adaptación

1. Elegir una fuente y comprobar cobertura, definiciones, actualización, coste y condiciones de uso.
2. Preparar un mapeo de campos: qué representa cada dato y con qué métrica del proyecto se corresponde.
3. Adaptar un conjunto pequeño de partidos y contrastarlo con la fuente.
4. Parametrizar las referencias a competición y temporada y construir la nueva base.
5. Recalcular los grupos, revisar los pesos y generar nuevas referencias para Power BI.
6. Repetir las pruebas de datos, ranking, filtros y estabilidad; documentar los cambios y límites.

SCOUT-11/DAT-03 conserva la idea de evaluar datos actuales. Está aplazada y fuera de la versión cerrada; no representa una comparativa ya realizada ni una decisión de compra.

## Mejoras de análisis

- Extender la separación entre juego abierto y balón parado a mediapunta y extremo. Su efecto se exploró, pero no se incorporó al modelo oficial.
- Estudiar el contexto con posesión medida en tiempo, marcador y rival, si la fuente lo permite.
- Evaluar rendimiento en una temporada posterior, separando los datos usados para diseñar el modelo de los utilizados para comprobarlo.
- Añadir datos económicos si el objetivo futuro incluye comparar coste y rendimiento.

## Aplicar la idea a otro ámbito

La lógica de comparar opciones con criterios y pesos puede servir en otros proyectos. Por ejemplo, comparar productos por precio, prestaciones y fiabilidad. Se reutilizaría el planteamiento analítico, pero las tablas, métricas, reglas de negocio y pruebas serían nuevas. La versión actual no es un importador universal de bases de datos.
