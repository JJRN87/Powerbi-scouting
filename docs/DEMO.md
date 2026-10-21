# Demo interactiva en GitHub Pages

[**Abrir Powerbi-scouting**](https://jjrn87.github.io/Powerbi-scouting/)

La demo permite explorar los siete perfiles, ajustar pesos, filtrar por minutos y seleccionar un jugador para ver sus percentiles y contribuciones. Funciona en el navegador, sin cuenta, instalación ni descarga del proyecto.

Es una presentación HTML del mismo análisis. El informe nativo de Power BI se conserva como parte del proyecto; la demo no ejecuta Power BI.

## Qué contiene

Se publican resultados derivados: percentiles, puestos, pesos, sensibilidad y resúmenes de participación. Los datos necesarios para estos cálculos viajan con la página y son públicos. Los cambios de un visitante solo afectan a su sesión; no modifican la configuración del proyecto.

La copia web omite los valores originales de las métricas en el detalle y las tablas de eventos, alineaciones y partidos. Se mantienen la fuente, el logotipo de StatsBomb y enlaces al método. Los eventos originales, la base SQLite, los CSV completos y el PBIX cargado no se publican.

Los percentiles y la población de referencia son los de la versión histórica. Cambiar el mínimo de minutos filtra la lista, sin recalcular esa referencia. La demo no incorpora los ajustes exploratorios de contexto de equipo.

## Publicación y mantenimiento

GitHub Pages publica la rama `main`, carpeta `/docs`. La entrada es `docs/index.html`; `docs/.nojekyll` permite servirla directamente como sitio estático.

Después de una reconstrucción de datos:

```powershell
python -m src.build
python -m src.build_demo
```

El segundo comando exporta únicamente los campos permitidos desde el visor generado, comprueba sus puntuaciones y puestos base y actualiza `docs/index.html` y [el registro de comprobación](evidencias/demo.json). También utiliza `src/review.html`, la misma plantilla del visor local.

Los cambios se publican al subirlos a `main`. Las pruebas de interacción y la revisión visual se realizan en el sitio desplegado. La versión histórica de análisis sigue siendo la cerrada el 17/10/2026; la demo se añade el 21/10/2026 para facilitar su consulta.

## Límites

Muestra histórica de LaLiga 2015/16, pesos elegidos y resultados relativos al perfil. La lista sirve para explorar candidatos; no predice rendimiento, precio o disponibilidad actual.

[Repositorio y código](https://github.com/JJRN87/Powerbi-scouting) · [Explicación sencilla](EXPLICACION.md) · [Reproducción completa](REPRODUCIR.md)

Configuración del alojamiento: [documentación oficial de GitHub Pages](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).
