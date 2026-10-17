# Decisiones de los siete perfiles

Revisión descriptiva cerrada el 17/10/2026. Se conservan los pesos de `config/profiles.json`; los escenarios alternativos no se promueven a configuración oficial. Son preferencias de búsqueda, no parámetros aprendidos ni una validación predictiva.

| Perfil | Decisión y lectura del resultado | Limitación prioritaria |
|---|---|---|
| Central | Mantener base general; Mustafi lidera todo el intervalo ±20%. Comparar salida y defensa según necesidad. | Exposición defensiva y regates sufridos; puestos siguientes sensibles. |
| Lateral/carrilero | Mantener base ofensiva; comparar escenario defensivo. Filipe–Marcelo destacan, el orden cambia. | Yoda con pocos minutos; conducción y regate correlacionados. |
| Pivote | Mantener referencia recuperadora; mostrar más salida como alternativa. Augusto lidera todo el intervalo ±50%. | No equivale a pivote posicional; Busquets penalizado por volumen de acciones. |
| Organizador | Mantener v2 con creación abierta/parada y xG asistido; interpretar el puesto de André Gomes con su sensibilidad. | No confundir tercer puesto base con una superioridad independiente de pesos. |
| Mediapunta/interior | Mantener referencia; James e Isco como elección por función, Banega tercero con variación moderada. | Cohorte pequeña, roles mixtos y creación a balón parado. |
| Extremo | Mantener perfil de desborde/creación; escenario de gol para otra función. Neymar lidera todo el intervalo ±50%. | No es ranking de calidad global; Burgui con pocos minutos y efecto del balón parado. |
| Delantero | Mantener base; alternativa 45/10/10/20/15 para reducir énfasis en goles y volumen. Suárez lidera todo el intervalo ±50%. | Correlación entre xG, tiros y goles; exclusión de atacantes sin suficiente tiempo ST. |

“Todo el intervalo” se refiere a multiplicadores independientes sobre los pesos base, normalización por su suma, cohorte y percentiles fijos. No es una garantía ante cualquier ponderación.

Evidencia: [central, lateral, mediapunta y extremo](CENTRAL_LATERAL_MEDIAPUNTA_EXTREMO.md), [pivote y delantero](PIVOTE_Y_DELANTERO.md), [metodología y organizador v2](../METODOLOGIA.md), `src/analyze_organizer.py` y su salida local `outputs/organizador_robustez.json`.

SCOUT-7/MOD-03 se cierra como revisión de atributos, sensibilidad y decisiones. No implica que el usuario haya elegido una preferencia universal ni que se haya comprobado rendimiento futuro. Cambiar una base o una definición exigirá versionarla y repetir las pruebas correspondientes.

Siguen abiertas SCOUT-8/MOD-04 (estabilidad por partidos y contexto) y SCOUT-11/DAT-03 (evaluación de datos actuales). Se propone como mejora futura extender la separación de creación a mediapunta y extremo; su diagnóstico ya está documentado, su implementación no está hecha.
