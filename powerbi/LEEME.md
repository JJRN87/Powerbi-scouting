# Preparar el informe en Power BI Desktop

Los datos están calculados y el visor local ya funciona. Esta carpeta contiene el importador, las medidas y el diseño sugerido. **No se ha ejecutado ni validado DAX/Power Query dentro de Power BI Desktop en esta entrega y no se ha creado un PBIX.**

## 1. Importar con tipos correctos

1. Abrir un informe nuevo. Obtener datos → Consulta en blanco → Editor avanzado.
2. Pegar el contenido de `Fuente.pq`. Llamar a la consulta **Fuente**. Si se mueve el proyecto, cambiar únicamente `Carpeta` al directorio de datos procesados.
3. Crear consultas en blanco con los siguientes nombres y expresiones:

| Nombre de consulta | Expresión |
|---|---|
| rankings | `= Fuente[rankings]` |
| profiles | `= Fuente[profiles]` |
| weights | `= Fuente[weights]` |
| metrics | `= Fuente[metrics]` |
| ranking_detail | `= Fuente[ranking_detail]` |
| sensitivity | `= Fuente[sensitivity]` |
| players_season | `= Fuente[players_season]` |
| player_match | `= Fuente[player_match]` |
| matches | `= Fuente[matches]` |

No cargar Fuente como tabla. `position_stints` y `event_exclusions` se pueden añadir de la misma forma para auditoría. Cerrar y aplicar. Los CSV tienen coma como separador, punto decimal y UTF-8 con BOM. El importador usa `en-US` para números y mantiene los vacíos como nulos; no confiar en la detección automática del formato regional español.

Convertir `match_date` a fecha con formato ISO si se utilizarán series temporales. El modelo v1 solo contiene esta temporada y competición.

## 2. Relaciones

Desactivar o revisar las relaciones detectadas automáticamente. Crear relaciones uno-a-muchos, filtro en una dirección:

- `profiles[profile_id]` → `rankings[profile_id]`.
- `rankings[candidate_id]` → `ranking_detail[candidate_id]`.
- `metrics[metric_id]` → `ranking_detail[metric_id]`.
- `players_season[player_id]` → `player_match[player_id]`.
- `matches[match_id]` → `player_match[match_id]`.

Dejar `weights` y `sensitivity` desconectadas para evitar rutas ambiguas. Las medidas de etiquetas consultan `weights` por perfil y slot. No relacionar las tablas Peso1…Peso8. Usar los campos de `rankings` en la página de ranking; esta página funciona sin relacionar `players_season` con `rankings`.

La página de detalle de partidos usa `players_season`, `matches` y `player_match`. Sus filtros de fecha no recalculan el ranking de temporada: no colocar un filtro de fecha en la página del ranking v1.

## 3. Pesos interactivos

1. En Modelado → Nueva tabla, crear cada una de las ocho tablas `Peso1`…`Peso8` copiando su expresión de `Medidas.dax` por separado.
2. Crear por separado cada medida del mismo fichero dentro de `rankings`.
3. Añadir un segmentador `profiles[profile]`, selección única.
4. Añadir ocho segmentadores de selección única, uno por `PesoN[Value]`. Usar lista desplegable (0–100); **no usar un intervalo «Entre»**, porque selecciona múltiples pesos.
5. Cuando un segmentador de peso esté sin selección, la medida utiliza el peso base del perfil. Una selección de cero elimina esa métrica. Si todos los pesos son cero, la puntuación queda en blanco.
6. Para el título dinámico de cada segmentador usar Formato → Título → fx → Valor de campo → `Etiqueta peso N`.

Cada slot representa una métrica diferente según el perfil. Al cambiar de perfil, limpiar las selecciones de pesos para usar los valores base del nuevo perfil. Se puede guardar un marcador con los ocho segmentadores sin selección y añadir un botón «Restablecer pesos» limitado a esos segmentadores. Los slots sin métrica se ignoran en los perfiles con menos de ocho atributos.

Las fórmulas usan separadores DAX estándar con coma. Si Desktop tiene activados separadores regionales, desactivar esa opción o adaptar separadores antes de pegar.

## 4. Página de ranking

- Encabezado: «LaLiga 2015/16 · Selección por perfil», atribución StatsBomb y nota «Pesos exploratorios».
- Izquierda: perfil, mínimo de minutos (usar `rankings[minutes]`, mayor o igual que 900), equipo y ocho pesos.
- Tabla: `candidate_id` (necesario para identificar la fila), jugador, equipos, minutos, `role_share`, `[Puntuacion interactiva]`, `[Ranking interactivo]`, `score_base`, `[Cambio de puntuacion]`.
- Ordenar por puntuación descendente. Formatear puntuación a 2 decimales, minutos a 0 y `role_share` como porcentaje.
- Desglose: al seleccionar un candidato, mostrar `metrics[label]`, `ranking_detail[value]`, `percentile` y `contribution_base`. **La contribución base es estática**: no presentarla como contribución de pesos personalizados.
- Sensibilidad: tabla independiente con perfil, jugador, puesto base, mejor/peor puesto. Corresponde exclusivamente a perturbaciones del perfil base.

Los percentiles no cambian al filtrar por equipo o minutos. El ranking interactivo se recalcula entre los candidatos visibles del perfil seleccionado. Una cohorte de 900 minutos impide incluir jugadores con menor muestra; cambiarla requiere reconstruir con otra configuración.

## 5. Comprobación en Desktop

Antes de dar por validado el informe:

1. Elegir organizador y limpiar los ocho pesos: la puntuación interactiva debe coincidir con `score_base` para cada candidato.
2. Dejar un único peso a 100 y los demás a cero: puntuación igual al percentil de esa métrica.
3. Poner todos los pesos a cero: puntuación y ranking vacíos.
4. Cambiar pesos: observar que orden y puntuaciones se actualizan.
5. Filtrar un equipo: los percentiles y puntuaciones no cambian; el puesto visible sí puede cambiar.
6. Comparar nombres y puntuaciones con `outputs/revisar_rankings.html` para los mismos pesos y minutos. No aplicar un filtro de equipo durante esa comparación.
7. Guardar el informe como PBIX una vez comprobado.

## Actualizar

Editar `config/profiles.json` → ejecutar `python -m src.build` → pulsar Actualizar en Power BI. El visor se regenera con los nuevos datos. No es necesario volver a descargar los partidos.

Mantener los datos y el informe en local para esta fase de investigación. Consultar `data/raw/LICENSE.pdf` antes de publicar o compartir.


## Actualización del organizador v2

Volver a pegar el importador `Fuente.pq` para incorporar las columnas nuevas. Actualizar las medidas de `Medidas.dax`, crear las nuevas tablas Peso7 y Peso8 y añadir sus segmentadores y etiquetas. Limpiar todos los pesos seleccionados: los slots del organizador ahora representan otros atributos. No basta con refrescar los CSV si el modelo mantiene las fórmulas antiguas de seis slots.

Añadir una consulta `organizer_comparison` con `= Fuente[organizer_comparison]` para comparar puestos v1, escenario conversado 40/5 y v2. Dejarla desconectada y usar sus campos en una tabla independiente. Las comparaciones históricas corresponden a la cohorte completa y no se recalculan al cambiar los pesos interactivos.

El organizador utiliza ocho métricas. La creación en juego abierto suma 35% y la de balón parado 5%. Las definiciones incluyen secuencias etiquetadas como procedentes de córner/falta; consultar la metodología v2. Las pruebas de los ocho controles se han realizado en el visor local. Power BI Desktop sigue pendiente de validación en su motor.
