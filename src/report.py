import html
import json
from pathlib import Path
from .metrics import MAX_SLOTS
from .download import ROOT


def write_reports(audit, tables, schemas):
    output = ROOT / 'outputs'
    lines = ['# Revisión inicial · LaLiga 2015/16', '',
             'Fuente: StatsBomb Open Data. Análisis histórico exploratorio para uso local.', '',
             f"{audit['matches']} partidos, {audit['teams']} equipos, {audit['players']} jugadores con participación y {audit['events']:,} eventos.",
             f"Marcadores reconciliados: {audit['goals_reconciled_matches']}/380; {audit['goals']} goles, incluidos autogoles.", '',
             '## Cómo interpretar los resultados', '',
             'Pesos iniciales propuestos, todavía no validados por criterio futbolístico ni por predicción futura. '
             'Puntuación = media ponderada de percentiles dentro de cada perfil. '
             'Mínimo 900 minutos reglamentarios y 50% del tiempo en los roles del perfil. '
             'Los eventos y las tasas incluyen toda la participación del jugador, no solo sus minutos en el rol. '
             'Los percentiles de referencia permanecen fijos al filtrar candidatos.', '',
             'El rango de sensibilidad cambia un peso cada vez un ±20%, normalizando el total. '
             'Es una prueba de dependencia de los pesos, no un intervalo de confianza.', '']
    sens = {(r['profile_id'],r['player_id']):r for r in tables['sensitivity']}
    for profile in tables['profiles']:
        pid = profile['profile_id']
        lines += [f"## {profile['profile']} ({profile['cohort_size']} candidatos)", '',
                  '| Puesto | Jugador | Equipo(s) | Minutos | Tiempo en roles | Puntuación | Rango ±20% |',
                  '|---:|---|---|---:|---:|---:|---:|']
        for r in [r for r in tables['rankings'] if r['profile_id']==pid][:10]:
            s = sens[(pid,r['player_id'])]
            lines.append(f"| {r['rank_base']} | {r['player']} | {r['teams']} | {r['minutes']:.0f} | {r['role_share']:.0%} | {r['score_base']:.2f} | {s['best_rank']}–{s['worst_rank']} |")
        lines.append('')
    lines += ['## Límites que revisar', '',
              '- No se han corregido las métricas por posesión, fuerza del equipo o rival.',
              '- Se compara rendimiento observado en 2015/16. No se estima rendimiento actual, futuro ni valor de mercado.',
              '- La posición viene de las alineaciones de StatsBomb. Los roles amplios pueden mezclar funciones tácticas distintas.',
              '- Recuperaciones, entradas y presiones pueden favorecer equipos que defienden más.',
              '- La precisión de pase no ajusta dificultad; debe interpretarse junto con progresión y creación.',
              '- Algunas métricas están correlacionadas. xG, goles y tiros pueden reforzar una misma dimensión.',
              '- Los eventos incluyen descuento; el denominador por 90 usa minutos reglamentarios, como convención explícita.',
              '- Datos económicos, salarios y disponibilidad de fichaje no están incluidos.', '',
              f"Commit de origen: `{audit['source_commit']}`. Definiciones en `docs/METODOLOGIA.md`."]
    (output/'VALIDACION.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    comparison = tables['organizer_comparison']
    text = ['# Organizador: comparación v1, escenario 40/5 y v2', '',
            'Misma cohorte de 66 jugadores. V1: creación total 25%, precisión 20%. '
            '40/5: simulación anterior con creación total 40%, precisión 5%. '
            'V2: creación abierta 35% (pases 15%, xG 20%) y balón parado 5% (pases 2%, xG 3%). '
            'En los tres: progresión 30%, recuperaciones 15%, regates 10%. V2 mantiene precisión 5%.', '',
            'Balón parado: fases StatsBomb From Corner/From Free Kick, además de saques directos que generan un tiro. '
            'Las secuencias de saque de banda/puerta/centro se consideran abiertas tras el saque. '
            'La separación es una aproximación basada en etiquetas del proveedor, sin ventana temporal adicional.', '',
            '| Jugador | Puesto v1 | Puesto 40/5 | Puesto v2 | Puntos v2 | Pases tiro abiertos /90 | xG asistido abierto /90 | Pases tiro balón parado /90 | xG asistido balón parado /90 |',
            '|---|---:|---:|---:|---:|---:|---:|---:|---:|']
    for r in comparison:
        text.append(f"| {r['player']} | {r['rank_v1']} | {r['rank_creation_40']} | {r['rank_v2']} | {r['score_v2']:.2f} | {r['key_passes_open_play_p90']:.2f} | {r['xg_assisted_open_play_p90']:.3f} | {r['key_passes_set_piece_p90']:.2f} | {r['xg_assisted_set_piece_p90']:.3f} |")
    text += ['', 'El xG asistido combina volumen y calidad de los tiros. No es xG medio por ocasión. '
             'Los pesos v2 son preferencias de scouting revisadas mediante sensibilidad; no son un modelo predictivo entrenado.']
    (output/'ORGANIZADOR_V2.md').write_text('\n'.join(text)+'\n',encoding='utf-8')
    payload = {k:tables[k] for k in ['rankings','ranking_detail','profiles','metrics','sensitivity']}
    payload['max_slots'] = MAX_SLOTS
    payload['organizer_comparison'] = comparison
    payload['audit'] = {k:audit[k] for k in ['matches','teams','players','events','source_commit']}
    template = (ROOT/'src/review.html').read_text(encoding='utf-8')
    encoded = json.dumps(payload,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    template = template.replace('__LOGO__', '../docs/assets/statsbomb-logo.png')
    template = template.replace('__MINIMUM__',str(tables['profiles'][0]['minimum_minutes']))
    template = template.replace('__ROLE_PERCENT__',str(round(100*tables['profiles'][0]['minimum_role_share'])))
    (output/'revisar_rankings.html').write_text(template.replace('__DATA__',encoded),encoding='utf-8')
    powerbi = ROOT/'powerbi'
    powerbi.mkdir(exist_ok=True)
    m = ['// Crear consulta en blanco llamada Fuente y pegar en Editor avanzado.',
         'let', f'    Carpeta = "{(ROOT/"data/processed").as_posix()}",',
         '    Leer = (nombre as text, tipos as list) as table =>',
         '        let',
         '            Csv = Csv.Document(File.Contents(Carpeta & "/" & nombre & ".csv"), [Delimiter=",", Encoding=65001, QuoteStyle=QuoteStyle.Csv]),',
         '            Cabecera = Table.PromoteHeaders(Csv, [PromoteAllScalars=true]),',
         '            Nulos = Table.ReplaceValue(Cabecera, "", null, Replacer.ReplaceValue, Table.ColumnNames(Cabecera)),',
         '            Tipos = Table.TransformColumnTypes(Nulos, tipos, "en-US")',
         '        in Tipos,', '    Tablas = [']
    entries = []
    for name, schema in schemas.items():
        pairs = ', '.join('{"'+k+'", '+v+'}' for k,v in schema.items())
        entries.append('        '+name+' = Leer("'+name+'", {'+pairs+'})')
    m += [',\n'.join(entries), '    ]', 'in', '    Tablas']
    (powerbi/'Fuente.pq').write_text('\n'.join(m)+'\n',encoding='utf-8')
    dax = ['// Crear cada tabla por separado con Modelado > Nueva tabla.']
    for i in range(1, MAX_SLOTS + 1):
        dax += [f'Peso{i} = GENERATESERIES(0, 100, 1)', '']
    dax += ['// Crear las siguientes medidas en rankings. Separadores DAX estándar (coma).',
            'Puntuacion interactiva =', 'VAR UnCandidato = HASONEVALUE(rankings[candidate_id])']
    for i in range(1, MAX_SLOTS + 1):
        dax += [f'VAR W{i} = IF(ISBLANK(SELECTEDVALUE(rankings[metric_{i}])), 0, SELECTEDVALUE(Peso{i}[Value], SELECTEDVALUE(rankings[weight_{i}])))',
                f'VAR P{i} = SELECTEDVALUE(rankings[percentile_{i}])']
    dax += ['VAR Faltan = '+ ' || '.join(f'(W{i} > 0 && ISBLANK(P{i}))' for i in range(1, MAX_SLOTS + 1)),
            'VAR TotalPeso = '+ ' + '.join(f'W{i}' for i in range(1, MAX_SLOTS + 1)),
            'RETURN IF(UnCandidato && NOT(Faltan) && TotalPeso > 0,',
            '    ROUND(DIVIDE('+ ' + '.join(f'W{i} * P{i}' for i in range(1, MAX_SLOTS + 1))+', TotalPeso), 8), BLANK())', '',
            'Ranking interactivo =',
            'VAR Actual = [Puntuacion interactiva]',
            'VAR Perfil = SELECTEDVALUE(rankings[profile_id])',
            'VAR Candidatos = FILTER(ALLSELECTED(rankings), rankings[profile_id] = Perfil)',
            'RETURN IF(HASONEVALUE(rankings[candidate_id]) && NOT(ISBLANK(Actual)),',
            '    RANKX(Candidatos, [Puntuacion interactiva], Actual, DESC, DENSE), BLANK())', '',
            'Cambio de puntuacion = IF(NOT ISBLANK([Puntuacion interactiva]), [Puntuacion interactiva] - SELECTEDVALUE(rankings[score_base]))', '']
    for i in range(1, MAX_SLOTS + 1):
        dax += [f'Etiqueta peso {i} =', f'VAR Perfil = SELECTEDVALUE(profiles[profile_id])',
                f'VAR Metrica = LOOKUPVALUE(weights[metric_id], weights[profile_id], Perfil, weights[slot], {i})',
                'RETURN LOOKUPVALUE(metrics[label], metrics[metric_id], Metrica)', '']
    (powerbi/'Medidas.dax').write_text('\n'.join(dax),encoding='utf-8')
