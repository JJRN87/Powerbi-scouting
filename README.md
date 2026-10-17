# Powerbi-scouting

Proyecto de portfolio para explorar qué jugadores encajan mejor en un perfil futbolístico según los atributos que se prioricen. Utiliza StatsBomb Open Data de LaLiga 2015/16, un proceso reproducible en Python, una base SQLite y tablas preparadas para Power BI.

La pregunta es: **¿cómo cambia la selección de candidatos cuando cambia lo que buscamos en una posición?** Se comparan siete perfiles mediante percentiles y pesos editables. Un jugador puede encajar en varios perfiles; la puntuación no determina por sí sola su mejor posición ni garantiza rendimiento futuro.

## Desarrollo asistido por IA

El proyecto se desarrolla con asistencia de IA para programar, documentar y ejecutar comprobaciones. La intervención del autor incluye definir el objetivo, revisar decisiones metodológicas, pedir la separación de creación en juego abierto y a balón parado e investigar la sensibilidad de resultados inesperados. El código generado se acompaña de pruebas y reglas explícitas para poder inspeccionarlo y reproducirlo.

El trabajo documenta las decisiones y sus límites. La revisión técnica automatizada no equivale a una auditoría manual de cada evento ni a una validación futbolística definitiva. La [guía de explicación](docs/EXPLICACION.md) recoge preguntas y respuestas que ayudan a comprender y defender el proyecto.

## Estado del proyecto

| Componente | Estado |
|---|---|
| Ingesta, transformación y controles de datos | Implementados y comprobados localmente |
| Rankings y visor HTML interactivo | Implementados; pesos en revisión |
| Tablas, Power Query y medidas DAX | Preparados |
| Informe ejecutado en Power BI Desktop | Pendiente; no se entrega PBIX |
| Validación predictiva y valoración económica | Fuera del alcance actual |

El proyecto cuenta con documentación en Confluence y seguimiento en Jira, ambos sujetos al acceso del sitio de Atlassian. La [metodología](docs/METODOLOGIA.md), el [resumen de proyecto](docs/PROYECTO.md), la [guía de explicación](docs/EXPLICACION.md) y una [instantánea del backlog](docs/backlog.json) están disponibles públicamente en este repositorio.

## Entorno

Base analítica local de StatsBomb Open Data para explorar perfiles de jugadores con pesos editables. Python 3.10+; el proceso de datos usa únicamente la biblioteca estándar, sin instalación de paquetes.

## Empezar

Si acabas de clonar este repositorio, ejecuta primero los comandos de **Reproducir**: los datos y los informes generados no están incluidos en GitHub. Después:

1. Abrir `outputs/revisar_rankings.html` en un navegador. Elegir perfil, ajustar pesos y pulsar un jugador para ver el desglose. Funciona sin conexión.
2. Leer `outputs/VALIDACION.md` para ver los diez primeros de cada perfil y su sensibilidad a cambios de pesos.
3. Seguir `powerbi/LEEME.md` para importar las tablas y activar las medidas interactivas.

**Esto prepara los datos, las consultas y las medidas para Power BI. No incluye un archivo PBIX ni un informe ya ejecutado en Power BI Desktop.** El visor local permite comenzar la revisión de los pesos inmediatamente.

## Reproducir

Desde esta carpeta, en PowerShell:

```powershell
python -m src.download
python -m src.build
python -m unittest discover -s tests -v
python -m src.validate
python -m src.analyze_organizer
```

La primera descarga necesita Internet. Las siguientes reutilizan archivos en caché. La reconstrucción y las validaciones funcionan sin conexión. La descarga fija un commit del repositorio en `data/source-lock.json`; no cambia de versión en cada ejecución. La descarga completa ocupa varios cientos de MB antes de comprimir; se conserva comprimida localmente.

Para cambiar pesos de forma permanente: editar `config/profiles.json`, ejecutar `python -m src.build` y actualizar Power BI. Los cambios del visor son temporales y no modifican el fichero de configuración. El mínimo de referencia inicial es 900 minutos y la fracción mínima de tiempo en los roles es 50%. Si se cambia esta configuración, se reconstruyen los percentiles y la cohorte.

## Archivos y resultados que se generan

| Ruta | Contenido |
|---|---|
| `data/raw/` | JSON originales comprimidos, licencia y manifiesto de procedencia con hashes SHA-256. |
| `data/processed/football.sqlite` | Base relacional local: jugadores, partidos, intervalos de posición, métricas, perfiles y rankings. |
| `data/processed/*.csv` | Tablas de intercambio UTF-8, separador coma y punto decimal. |
| `outputs/revisar_rankings.html` | Exploración interactiva local y desglose de puntuaciones. |
| `outputs/VALIDACION.md` | Ranking base y prueba de sensibilidad. |
| `outputs/audit.json` | Auditoría de cobertura y reconciliación de goles. |
| `powerbi/Fuente.pq` | Importador Power Query con tipos explícitos y lectura de nulos. |
| `powerbi/Medidas.dax` | Parámetros de peso, puntuación y ranking interactivos. |
| `docs/METODOLOGIA.md` | Definiciones, decisiones estadísticas y límites. |

## Revisión propuesta

Primero revisar el organizador, el pivote y el delantero. Para cada perfil, valorar los primeros diez jugadores, los atributos que los favorecen y los jugadores que sorprenden. Cambiar un peso cada vez, observar el orden y guardar los pesos acordados en la configuración. La familiaridad de los nombres no demuestra que el modelo sea correcto: revisar también minutos, rol y contexto del equipo.

Los pesos son hipótesis de scouting, no coeficientes aprendidos ni garantías de rendimiento. La validación técnica y la sensibilidad están automatizadas; la validación futbolística sigue pendiente. No se incluyen salarios, precios ni valoraciones económicas.

## Fuente y uso

Datos: [StatsBomb Open Data](https://github.com/statsbomb/open-data), competición 11, temporada 27. Consultar la copia exacta de `data/raw/LICENSE.pdf`. El proyecto está preparado para análisis local de investigación. La licencia del conjunto limita el uso comercial y la redistribución de datos; la publicación de análisis requiere la atribución y el logotipo indicados por StatsBomb. Los datos y resultados derivados están excluidos del control de versiones mediante `.gitignore`.

El motor de puntuación está separado del procesamiento de eventos. Incorporar otro proveedor requerirá un adaptador y comprobar equivalencias de métricas; no se deben mezclar automáticamente definiciones diferentes.


## Organizador actualizado (v2)

El organizador separa volumen y xG asistido en juego abierto y a balón parado, con ocho pesos editables. Consultar `outputs/ORGANIZADOR_V2.md` para comparar los 66 candidatos con el perfil original y con la simulación 40/5. Los otros perfiles se conservan. En Power BI es necesario actualizar el importador y las medidas, añadir Peso7/Peso8 y borrar las selecciones anteriores de pesos.
