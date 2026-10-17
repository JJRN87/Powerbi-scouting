# Powerbi-scouting

## Objetivo y alcance

Construir una herramienta explicable de selección de candidatos por perfil, utilizando LaLiga 2015/16 como caso histórico. El usuario decide qué atributos prioriza y observa cómo cambia el ranking. El objetivo inicial es validar las métricas y las preferencias antes de invertir en datos actuales.

Los perfiles son central, lateral, pivote, organizador, mediapunta, extremo y delantero. Se exige un mínimo de 900 minutos y un 50% de tiempo en los roles admitidos. Las estadísticas son de toda la temporada del jugador. No se infiere automáticamente su posición óptima.

## Flujo de datos

1. `src.download` obtiene eventos, alineaciones y partidos de un commit fijo de StatsBomb. Conserva originales comprimidos y hashes SHA-256.
2. `src.build` relaciona entidades por identificadores, calcula intervalos de participación y agrega métricas por partido y temporada.
3. Las tablas SQLite y CSV alimentan el cálculo de percentiles por perfil y el ranking ponderado.
4. El visor HTML permite inspeccionar contribuciones y variar pesos. El informe nativo de Power BI usa Power Query y DAX para filtrar perfiles y equipos y recalcular rankings con pesos ajustables.
5. `src.validate` contrasta integridad, agregaciones y puntuaciones. `src.analyze_organizer` reproduce el análisis de sensibilidad del organizador.

## Limpieza y controles

| Decisión | Motivo y tratamiento |
|---|---|
| Identificadores estables | Unir por ID evita confundir nombres y permite agregar jugadores que cambian de club. |
| Pases no evaluables | Unknown e Injury Clearance se excluyen del denominador; quedan auditados, sin tratarlos como fallos. |
| Ratios sin denominador | Se mantienen nulas; no se sustituyen por cero. |
| Porcentajes de temporada | Se calculan desde numeradores y denominadores agregados. |
| Suplentes sin participación | Sus eventos excluidos quedan registrados; no se inventan minutos. |
| Descuento | Los minutos se limitan al tiempo reglamentario; los eventos del descuento se conservan. Esta convención afecta las tasas por 90. |
| Tiro asistido ausente | El cálculo de creación se detiene ante enlaces faltantes; no se asigna xG cero. |
| Duplicados y referencias | Se comprueba unicidad de eventos por partido e integridad de referencias; los errores detienen la construcción. |
| Juego abierto y balón parado | La partición debe conservar tanto el conteo total como el xG asistido. |

No se eliminan valores extremos porque un jugador sobresalga. Los controles verifican coherencia con la fuente; no certifican que todas las anotaciones del proveedor sean correctas.

## Evidencia de validación

El 17 de octubre de 2026 se repitieron con éxito las 10 pruebas unitarias y `src.validate`: 764 archivos fuente con hash verificado, 539 jugadores reconciliados y 387 puntuaciones de candidatos verificadas. La auditoría de construcción registra 380 partidos, 20 equipos, 1.295.354 eventos y reconciliación del marcador en los 380 partidos. El contraste independiente directo de pases, tiros y creación cubre cinco partidos distribuidos en la temporada.

El informe existente de pruebas del visor registra paridad de puntuaciones, pesos nulos, cambios de orden, detalle del jugador, filtros vacíos y anchura móvil. Power BI Desktop se ha ejecutado y guardado como PBIP y PBIX: seis escenarios, 1.359 comparaciones con Python y cero errores de puntuación, puesto o cohorte. Se han probado cambios de perfil, pesos y equipo en la interfaz. La evidencia de esta sesión está en `outputs/powerbi-verification.json` y sus capturas; la página de validación del informe permite repetir las comprobaciones DAX. No se distribuye el conjunto de datos en GitHub.

## Decisiones analíticas

Los percentiles comparan al jugador con su cohorte elegible; la puntuación es su media ponderada. Los pesos representan preferencias y no coeficientes aprendidos. Una puntuación de 80 no es una probabilidad de éxito y no se compara directamente entre perfiles.

El organizador v2 separa creación abierta y balón parado, e incorpora xG de tiros asistidos. El análisis de André Gomes, Kroos y Trashorras motivó comprobar la estabilidad del orden al variar pesos. Esta sensibilidad no representa incertidumbre estadística por partidos. Las definiciones y los pesos exactos están en [METODOLOGIA.md](METODOLOGIA.md) y `config/profiles.json`.

## Trabajo pendiente y criterio de cierre

La revisión descriptiva de los siete perfiles está cerrada: atributos, sensibilidad y decisión de conservar las bases con escenarios por función. Queda estudiar estabilidad por partidos y contexto de equipo. Una decisión sobre proveedores actuales requerirá comparar cobertura, definiciones y condiciones de uso. Extender la separación de creación a mediapunta y extremo es una mejora propuesta cuyo efecto se ha medido, todavía sin implementar en Power BI.

Una tarea se cierra cuando su criterio de aceptación tiene evidencia reproducible. Jira recoge las tareas con criterios y referencias; Confluence conserva alcance, metodología y decisiones. El [backlog público](backlog.json) conserva 11 tareas con identificadores locales. Estado actual: nueve terminadas y dos por hacer; BI-01 y MOD-03 cerrados. El detalle de la entrega está en [VALIDACION_POWERBI.md](VALIDACION_POWERBI.md). Se conserva el trabajo previo sin inventar sprints ni fechas de ejecución históricas.

## Uso de IA y presentación profesional

La IA participa en implementación, documentación y comprobaciones. El autor define la finalidad, plantea revisiones y contrasta el comportamiento del modelo durante el desarrollo. La comprensión se demuestra explicando las reglas, reproduciendo los cálculos y razonando sobre los límites, sin atribuirse una auditoría manual exhaustiva ni experiencia de producción que este prototipo no acredita.

## Publicación

El destino solicitado es un repositorio público llamado Powerbi-scouting. El contenido publicable comprende código, configuración, pruebas, instrucciones de reproducción y documentación. Los datos originales, la base, los CSV de resultados y el visor generado permanecen fuera de Git por las reglas del proyecto. La fuente y las condiciones de uso se documentan en el README y en la licencia descargada de StatsBomb. La licencia del código propio queda por decidir; no se atribuye la licencia de los datos al código.

## Revisión de pivote y delantero

La [revisión documentada](analisis/PIVOTE_Y_DELANTERO.md) incluye 40.000 simulaciones y comprobaciones directas de candidatos destacados. Conserva los pesos oficiales y distingue validación técnica, preferencia futbolística e incertidumbre por partidos. La [galería](evidencias/README.md) muestra Power BI, Jira y Confluence; la [forma de trabajo](gestion/FORMA_DE_TRABAJO.md) explica las prácticas ágiles realmente utilizadas.

## Revisión de los cuatro perfiles restantes

La [revisión de central, lateral, mediapunta y extremo](analisis/CENTRAL_LATERAL_MEDIAPUNTA_EXTREMO.md) añade 80.000 simulaciones, 213 candidatos reconciliados, 196 comprobaciones directas de métricas y 70 de minutos, sin diferencias. Las 14 pruebas unitarias actuales pasan. Mustafi y Neymar son sólidos en los intervalos documentados; Filipe–Marcelo y James–Isco cambian de orden según las preferencias. El [registro de decisiones](analisis/DECISIONES_PERFILES.md) cierra la revisión descriptiva conservando las bases. No se ha modificado Power BI ni se atribuyen nuevas pruebas Desktop a esta entrega.
