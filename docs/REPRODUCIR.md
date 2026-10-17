# Reproducir el proyecto

## Requisitos

- Python 3.10 o posterior.
- Internet para descargar la fuente por primera vez.
- Power BI Desktop en Windows para abrir el informe nativo.
- NumPy para el análisis adicional de estabilidad por partidos.

El proceso básico de datos usa la biblioteca estándar de Python. Las pruebas de estabilidad se ejecutaron con NumPy 2.3.5. El visor HTML generado funciona sin conexión y no requiere Power BI.

Los comandos se ejecutan desde la raíz de una copia del repositorio. El historial conserva la versión de datos en `data/source-lock.json`. La fuente se descarga por separado; el repositorio no incluye eventos ni datos cargados.

## Construcción básica

```powershell
python -m src.download
python -m src.build
python -m src.validate
python -m src.build_powerbi
```

1. La descarga conserva los originales comprimidos y el manifiesto de hashes en `data/raw/`.
2. La construcción produce `data/processed/football.sqlite`, los CSV y `outputs/revisar_rankings.html`.
3. La validación contrasta archivos, relaciones, agregaciones y puntuaciones. Guarda su resultado en `outputs/verification.json`.
4. El generador prepara `powerbi/Powerbi-scouting/Powerbi-scouting.pbip` y la referencia de pruebas DAX.

La descarga reutiliza la caché existente. Los pasos siguientes funcionan sin conexión cuando la fuente está completa.

## Abrir Power BI

Abrir el PBIP generado y pulsar **Actualizar**. El parámetro `CarpetaDatos` apunta a la carpeta de CSV de esta copia. Al mover el proyecto, volver a generar el PBIP o actualizar ese parámetro.

La página **Validación con Python** debe mostrar seis escenarios sin errores de puntuación, puesto o grupo. La [guía del informe](../powerbi/LEEME.md) describe los controles y cómo volver a los pesos base.

El PBIX cargado solo existe en la copia local de trabajo; no se descarga desde GitHub. El generador reconstruye el diseño del PBIP, por lo que una copia con modificaciones visuales manuales se guarda aparte antes de regenerar.

## Repetir las pruebas y los análisis

Con la construcción básica terminada:

```powershell
python -m pip install -r requirements-analysis.txt
python -m unittest discover -s tests -v
python -m src.analyze_organizer
python -m src.analyze_profiles
python -m src.verify_review_players
python -m src.analyze_profiles --group cuatro_perfiles
python -m src.verify_remaining_players
python -m src.analyze_match_stability
```

Las 18 pruebas requieren NumPy. Sin él, las cuatro pruebas de estabilidad se omiten y el resto puede ejecutarse. Los análisis guardan resultados en `outputs/`; las cifras principales y las condiciones de cada ejecución están en [evidencias](evidencias/README.md). El remuestreo usa una semilla fija; reproducir exactamente sus muestras requiere la misma versión de NumPy.

## Archivos principales

| Ruta | Contenido |
|---|---|
| `src/download.py` | Descarga de la fuente fijada. |
| `src/metrics.py` | Definiciones de eventos, tasas y puntuación. |
| `src/build.py` | Preparación de tablas y rankings. |
| `config/profiles.json` | Roles admitidos, mínimos y pesos. |
| `src/build_powerbi.py` | Generador del proyecto Power BI. |
| `powerbi/Medidas.dax` | Medidas y parámetros de pesos. |
| `data/processed/metrics.csv` | Diccionario generado de métricas. |
| `outputs/` | Visor, informes y resultados de comprobaciones. |

## Cambiar la configuración

Los pesos del informe y del visor son temporales. Para modificar la base se edita `config/profiles.json`, se ejecutan `src.build` y `src.build_powerbi`, se reabre el PBIP y se actualiza. Cambiar mínimos o roles reconstruye también los grupos y sus percentiles.

Las cifras publicadas corresponden a la configuración cerrada. Un cambio de pesos, reglas o datos requiere nuevas referencias de validación; no hereda los resultados de la versión anterior.

Cambiar de proveedor o de temporada requiere además adaptar el procesamiento. Ese trabajo está descrito como [ampliación futura](FUTURO.md), no como una opción ya implementada.
