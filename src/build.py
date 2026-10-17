"""Build local analytical database and Power BI exchange tables from pinned data."""
import csv
import copy
import hashlib
import json
import math
import sqlite3
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

from .metrics import MAX_SLOTS
from .download import ROOT, RAW, read_json
from .metrics import COUNTS, LABELS, NEGATIVE, ROLES, event_counts, percentile, rates, score, stint_minutes

OUT = ROOT / 'data/processed'
REPORTS = ROOT / 'outputs'


def write_table(name, rows):
    if not rows:
        raise ValueError(f'Empty table: {name}')
    columns = list(rows[0])
    with (OUT / (name + '.csv')).open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    return columns


def prepare_rankings(players, config):
    ranking, detail, profiles = [], [], []
    for profile in config['profiles']:
        weights = profile['weights']
        if not weights or len(weights) > MAX_SLOTS or any(w < 0 or not math.isfinite(w) for w in weights.values()) or sum(weights.values()) <= 0:
            raise ValueError(f'Invalid weights: {profile["profile_id"]}')
        if any(k not in players[0] for k in weights):
            raise ValueError('Unknown metric in profile')
        pool = [p for p in players if p['minutes'] >= config['minimum_minutes'] and
                sum(p['minutes_' + role] for role in profile['roles']) / p['minutes'] >= config['minimum_role_share']]
        populations = {k:[p[k] for p in pool if p[k] is not None] for k in weights}
        profiles.append({'profile_id':profile['profile_id'], 'profile':profile['label'],
                         'roles':','.join(profile['roles']), 'minimum_minutes':config['minimum_minutes'],
                         'minimum_role_share':config['minimum_role_share'], 'cohort_size':len(pool)})
        group = []
        for p in pool:
            ps = {k:percentile(p[k], populations[k], k in NEGATIVE) for k in weights}
            s = score(ps, weights)
            row = {'candidate_id': f"{profile['profile_id']}_{p['player_id']}",
                   'profile_id':profile['profile_id'], 'profile':profile['label'],
                   'player_id':p['player_id'], 'player':p['player'], 'teams':p['teams'],
                   'primary_role':p['primary_role'], 'minutes':p['minutes'],
                   'role_share':sum(p['minutes_' + role] for role in profile['roles']) / p['minutes'],
                   'matches':p['matches'], 'score_base':s, 'rank_base':None, 'cohort_size':len(pool)}
            for slot in range(1, MAX_SLOTS + 1):
                metric = list(weights)[slot-1] if slot <= len(weights) else None
                row[f'metric_{slot}'] = metric
                row[f'percentile_{slot}'] = ps[metric] if metric else None
                row[f'weight_{slot}'] = weights[metric] if metric else 0
            group.append(row)
            for slot, (k,w) in enumerate(weights.items(), 1):
                detail.append({'candidate_id':row['candidate_id'], 'profile_id':row['profile_id'],
                               'player_id':p['player_id'], 'slot':slot, 'metric_id':k,
                               'value':p[k], 'percentile':ps[k], 'weight_base':w,
                               'contribution_base':ps[k]*w/sum(weights.values()) if ps[k] is not None else None})
        group.sort(key=lambda x: (-(x['score_base'] if x['score_base'] is not None else -1), x['player_id']))
        ranked_scores = sorted({r['score_base'] for r in group if r['score_base'] is not None}, reverse=True)
        for row in group:
            row['rank_base'] = ranked_scores.index(row['score_base']) + 1 if row['score_base'] is not None else None
        ranking.extend(group)
    return ranking, detail, profiles


def sensitivity(rankings):
    result = []
    for profile_id in sorted({r['profile_id'] for r in rankings}):
        group = [r for r in rankings if r['profile_id'] == profile_id]
        experiments = defaultdict(list)
        first = group[0]
        for slot in range(1, MAX_SLOTS + 1):
            if first[f'metric_{slot}'] is None:
                continue
            for factor in [.8, 1.2]:
                weighted = []
                for r in group:
                    vals = {str(i):r[f'percentile_{i}'] for i in range(1, MAX_SLOTS + 1)}
                    ws = {str(i):r[f'weight_{i}'] * (factor if i == slot else 1) for i in range(1, MAX_SLOTS + 1)}
                    weighted.append((r['player_id'], score(vals, ws)))
                weighted.sort(key=lambda x: (-(x[1] if x[1] is not None else -1), x[0]))
                distinct = sorted({s for _,s in weighted if s is not None}, reverse=True)
                for pid, s in weighted:
                    if s is not None:
                        experiments[pid].append(distinct.index(s)+1)
        for r in group:
            ranks = experiments[r['player_id']]
            result.append({'profile_id':profile_id, 'player_id':r['player_id'], 'player':r['player'],
                           'rank_base':r['rank_base'], 'best_rank':min(ranks) if ranks else None,
                           'worst_rank':max(ranks) if ranks else None, 'scenarios':len(ranks),
                           'top10_fraction':sum(n<=10 for n in ranks)/len(ranks) if ranks else None})
    return result


def metric_dictionary():
    special = {
        'key_passes_open_play':'Pases que generan tiro fuera de fases From Corner/From Free Kick y que no son ejecución directa de un saque.',
        'key_passes_set_piece':'Pases que generan tiro en fases From Corner/From Free Kick o directamente desde Corner, Free Kick, Throw-in, Goal Kick o Kick Off.',
        'xg_assisted_open_play':'Suma del xG de tiros enlazados a pases de creación en juego abierto. Depende del volumen y calidad de tiros, no solo de calidad media.',
        'xg_assisted_set_piece':'Suma del xG de tiros enlazados a pases de creación a balón parado. Misma partición que los pases; incluye segundas jugadas etiquetadas como córner/falta.',
        'progressive_passes':'Pase completado en juego abierto, final en campo rival, reduce distancia a (120,40) al menos 10 unidades y 25%.',
        'progressive_carries':'Conducción con final en campo rival; reduce distancia a (120,40) al menos 10 unidades y 25%.',
        'final_third_passes':'Pase completado en juego abierto desde x<80 hasta x>=80.',
        'passes_attempted':'Pases excluyendo resultados Unknown e Injury Clearance; ausencia de outcome significa completado según esquema StatsBomb.',
        'key_passes':'Pase con shot_assist, goal_assist o assisted_shot_id válido. Incluye balón parado.',
        'xg_assisted':'Suma de statsbomb_xg de tiros enlazados mediante assisted_shot_id. No es un modelo xA independiente. Incluye balón parado.',
        'box_touches':'Proxy: recepciones completadas y tiros con x>=102 y 18<=y<=62. No cuenta todos los contactos.',
        'interceptions':'Interception con outcome Won, Success, Success In Play o Success Out.',
        'tackles_won':'Duel/Tackle con outcome Won, Success, Success In Play o Success Out.',
        'recoveries':'Ball Recovery sin recovery_failure=true.',
        'aerial_wins':'Un evento con aerial_won=true en uno de sus atributos; no es porcentaje de duelos aéreos.',
        'shots_on_target':'Shot con outcome Goal, Saved o Saved to Post.',
        'non_penalty_goals':'Goles de Shot excepto type Penalty. Excluye autogoles.',
        'npxg':'statsbomb_xg excepto Shot/type Penalty.',
        'dispossessed':'Eventos Dispossessed. No equivale a todas las pérdidas de balón.',
    }
    rows = [{'metric_id':k+'_p90','label':v+' /90','unit':'por 90 minutos',
             'direction':'lower' if k+'_p90' in NEGATIVE else 'higher',
             'definition':special.get(k, 'Conteo de eventos StatsBomb de esta categoría.') + ' Dividido por minutos reglamentarios y multiplicado por 90.'}
            for k,v in LABELS.items()]
    for k,label,definition in [('pass_completion_pct','Precisión de pase','100 × pases completados / pases evaluables.'),
                               ('dribble_success_pct','Éxito en regate','100 × regates completados / intentados.'),
                               ('tackle_success_pct','Éxito en entradas','100 × entradas ganadas / intentadas.')]:
        rows.append({'metric_id':k,'label':label,'unit':'porcentaje 0-100','direction':'higher',
                     'definition':definition+' Sin denominador: nulo, nunca cero.'})
    return rows


def save_database(tables):
    tmp = OUT / 'football.tmp.sqlite'
    if tmp.exists():
        tmp.unlink()
    with sqlite3.connect(tmp) as db:
        for name, rows in tables.items():
            columns = list(rows[0])
            types = {}
            for k in columns:
                vals = [r[k] for r in rows if r[k] is not None]
                types[k] = 'INTEGER' if vals and all(isinstance(v, int) for v in vals) else 'REAL' if vals and all(isinstance(v, (int,float)) for v in vals) else 'TEXT'
            db.execute(f'CREATE TABLE "{name}" ('+', '.join(f'"{k}" {types[k]}' for k in columns)+')')
            db.executemany(f'INSERT INTO "{name}" VALUES ('+','.join('?' for _ in columns)+')',
                           [[r[k] for k in columns] for r in rows])
        db.execute('CREATE UNIQUE INDEX ix_player ON players_season(player_id)')
        db.execute('CREATE UNIQUE INDEX ix_match_player ON player_match(match_id, player_id)')
        db.execute('CREATE UNIQUE INDEX ix_candidate ON rankings(candidate_id)')
        db.execute('CREATE UNIQUE INDEX ix_match ON matches(match_id)')
        assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    db.close()
    tmp.replace(OUT / 'football.sqlite')


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    config = read_json(ROOT / 'config/profiles.json')
    if config['minimum_minutes'] <= 0 or not 0 < config['minimum_role_share'] <= 1:
        raise ValueError('Minimum minutes must be positive and role share in (0,1]')
    if len({p['profile_id'] for p in config['profiles']}) != len(config['profiles']):
        raise ValueError('Duplicate profile identifiers')
    if any(not p['roles'] or not set(p['roles']) <= set(ROLES.values()) for p in config['profiles']):
        raise ValueError('Unknown or empty profile roles')
    manifest = read_json(RAW / 'manifest.json')
    matches = read_json(RAW / 'data/matches/11/27.json.gz')
    errors, warnings, player_match, match_rows, stints = [], [], [], [], []
    exclusions = []
    checks, coverage, event_types = [], Counter(), Counter()
    event_total = 0
    for i,m in enumerate(sorted(matches, key=lambda x:(x['match_date'], x['match_id']))):
        mid = m['match_id']
        events = read_json(RAW / f'data/events/{mid}.json.gz')
        lineups = read_json(RAW / f'data/lineups/{mid}.json.gz')
        event_total += len(events)
        event_types.update(e['type']['name'] for e in events)
        ids = [e['id'] for e in events]
        if len(ids) != len(set(ids)):
            errors.append(f'Duplicate event IDs in {mid}')
        if {e['period'] for e in events if e['type']['name'] == 'Half End'} != {1,2}:
            errors.append(f'Missing full time periods in {mid}')
        home, away = m['home_team']['home_team_id'], m['away_team']['away_team_id']
        coverage.update([home,away])
        per_player = {}
        for team in lineups:
            for p in team['lineup']:
                role_minutes = Counter()
                for j, stint in enumerate(p['positions']):
                    minutes = stint_minutes(stint)
                    role = ROLES[stint['position_id']]
                    role_minutes[role] += minutes
                    stints.append({'match_id':mid, 'player_id':p['player_id'], 'team_id':team['team_id'],
                                   'stint':j, 'position_id':stint['position_id'], 'role':role,
                                   'from_clock':stint['from'], 'to_clock':stint['to'],
                                   'from_period':stint['from_period'], 'to_period':stint['to_period'],
                                   'minutes':minutes, 'end_reason':stint['end_reason']})
                if not p['positions']:
                    continue
                minutes = sum(role_minutes.values())
                if minutes > 90.001 or minutes < 0:
                    errors.append(f'Invalid minutes {mid}/{p["player_id"]}: {minutes}')
                per_player[p['player_id']] = {
                    'match_id':mid, 'match_date':m['match_date'], 'match_week':m['match_week'],
                    'player_id':p['player_id'], 'player':p.get('player_nickname') or p['player_name'],
                    'full_name':p['player_name'], 'team_id':team['team_id'], 'team':team['team_name'],
                    'country':p.get('country',{}).get('name'), 'minutes':minutes,
                    'started':int(any(s['start_reason']=='Starting XI' for s in p['positions'])),
                    **{'minutes_'+role:role_minutes[role] for role in sorted(set(ROLES.values()))},
                    **{k:0 for k in COUNTS}}
        shots = {e['id']:e for e in events if e['type']['name'] == 'Shot'}
        goals = Counter()
        unknown_event_players = set()
        for e in events:
            kind = e['type']['name']
            if kind == 'Shot' and e['shot']['outcome']['name'] == 'Goal':
                goals[e['team']['id']] += 1
            if kind == 'Own Goal Against':
                goals[away if e['team']['id']==home else home] += 1
            if kind == 'Pass' and e['pass'].get('assisted_shot_id') and e['pass']['assisted_shot_id'] not in shots:
                errors.append(f'Unresolved assisted shot in match {mid}')
            pid = e.get('player',{}).get('id')
            if pid is None:
                continue
            if pid not in per_player:
                if kind == 'Bad Behaviour' and e.get('position', {}).get('id') == 0 and any(
                    p['player_id'] == pid for team in lineups for p in team['lineup']
                ):
                    exclusions.append({'match_id':mid,'event_id':e['id'],'player_id':pid,
                                       'reason':'Tarjeta a suplente sin participación: excluida de métricas deportivas'})
                    continue
                unknown_event_players.add(pid)
                continue
            c = event_counts(e, shots)
            for k,v in c.items():
                per_player[pid][k] += v
        if unknown_event_players:
            errors.append(f'Events without played lineup: {mid}/{sorted(unknown_event_players)}')
        goal_ok = goals[home] == m['home_score'] and goals[away] == m['away_score']
        if not goal_ok:
            errors.append(f'Goals do not reconcile in {mid}: {dict(goals)}')
        for r in per_player.values():
            if r['passes_completed'] > r['passes_attempted']:
                errors.append(f'Invalid passing counts: {mid}/{r["player_id"]}')
            r.update(rates(r, r['minutes']))
            player_match.append(r)
        match_rows.append({'match_id':mid, 'match_date':m['match_date'], 'match_week':m['match_week'],
                           'home_team_id':home,'home_team':m['home_team']['home_team_name'],
                           'away_team_id':away,'away_team':m['away_team']['away_team_name'],
                           'home_goals':m['home_score'],'away_goals':m['away_score'],
                           'events':len(events),'goals_reconciled':int(goal_ok)})
        if (i+1)%50 == 0:
            print(f'Processed {i+1}/{len(matches)} matches', flush=True)
    if len(matches)!=380 or len(coverage)!=20 or any(n!=38 for n in coverage.values()):
        errors.append('Incomplete league coverage')
    counts = Counter((m['home_team_id'],m['away_team_id']) for m in match_rows)
    if len(counts)!=380 or any(n!=1 for n in counts.values()):
        errors.append('Duplicate or missing home/away pairings')
    if errors:
        (REPORTS / 'build_errors.json').write_text(json.dumps(errors, indent=2), encoding='utf-8')
        raise ValueError(f'{len(errors)} audit failures; see outputs/build_errors.json; no rankings exported')
    error_path = REPORTS / 'build_errors.json'
    if error_path.exists():
        error_path.unlink()
    grouped = defaultdict(list)
    for r in player_match:
        grouped[r['player_id']].append(r)
    players = []
    for pid, rows in sorted(grouped.items()):
        roles = {role:sum(r['minutes_'+role] for r in rows) for role in sorted(set(ROLES.values()))}
        totals = {k:sum(r[k] for r in rows) for k in COUNTS}
        minutes = sum(r['minutes'] for r in rows)
        p = {'player_id':pid,'player':rows[-1]['player'],'full_name':rows[-1]['full_name'],
             'country':rows[-1]['country'],'teams':' / '.join(sorted({r['team'] for r in rows})),
             'matches':len(rows),'starts':sum(r['started'] for r in rows),'minutes':minutes,
             'primary_role':max(roles,key=roles.get), 'primary_role_share':max(roles.values())/minutes if minutes else 0,
             **{'minutes_'+k:v for k,v in roles.items()}, **totals, **rates(totals, minutes)}
        players.append(p)
    rankings, detail, profiles = prepare_rankings(players, config)
    # Fixed historical comparator, recomputed with the same source and cohort rules.
    history_config = read_json(ROOT/'config/history/profiles_v1.json')
    original, _, _ = prepare_rankings(players, history_config)
    creative_config = copy.deepcopy(history_config)
    creative_weights = next(p['weights'] for p in creative_config['profiles'] if p['profile_id']=='organizador')
    creative_weights.update(key_passes_p90=40, pass_completion_pct=5)
    creative, _, _ = prepare_rankings(players, creative_config)
    prior = {r['candidate_id']:r for r in original}
    scenario = {r['candidate_id']:r for r in creative}
    player_lookup = {p['player_id']:p for p in players}
    comparison = []
    for r in rankings:
        if r['profile_id'] != 'organizador':
            continue
        old, hypothetical = prior[r['candidate_id']], scenario[r['candidate_id']]
        p = player_lookup[r['player_id']]
        comparison.append({'candidate_id':r['candidate_id'],'player_id':r['player_id'],'player':r['player'],
                           'rank_v1':old['rank_base'],'score_v1':old['score_base'],
                           'rank_creation_40':hypothetical['rank_base'],'score_creation_40':hypothetical['score_base'],
                           'rank_v2':r['rank_base'],'score_v2':r['score_base'],
                           **{k:p[k] for k in ['key_passes_open_play_p90','key_passes_set_piece_p90',
                                              'xg_assisted_open_play_p90','xg_assisted_set_piece_p90']}})
    sens = sensitivity(rankings)
    weights = [{'profile_id':p['profile_id'],'slot':i,'metric_id':k,'weight':v}
               for p in config['profiles'] for i,(k,v) in enumerate(p['weights'].items(),1)]
    audit = {'source_commit':manifest['commit'], 'created_utc':datetime.now(timezone.utc).isoformat(),
             'matches':len(matches),'teams':len(coverage),'players':len(players),'events':event_total,
             'player_match_rows':len(player_match),'ranked_candidates':len(rankings),
             'goals':sum(m['home_goals']+m['away_goals'] for m in match_rows),
             'goals_reconciled_matches':sum(m['goals_reconciled'] for m in match_rows),
             'pass_outcomes_excluded':sum(p['passes_excluded'] for p in players),
             'bench_events_excluded':len(exclusions),
             'errors':errors,'warnings':warnings,'event_types':dict(event_types),
             'profiles':profiles,'config_sha256':hashlib.sha256((ROOT/'config/profiles.json').read_bytes()).hexdigest()}
    tables = {'players_season':players,'player_match':player_match,'matches':match_rows,
              'position_stints':stints,'rankings':rankings,'ranking_detail':detail,
              'profiles':profiles,'weights':weights,'metrics':metric_dictionary(),'sensitivity':sens,
              'event_exclusions':exclusions,'organizer_comparison':comparison}
    schemas = {}
    for name, rows in tables.items():
        write_table(name,rows)
        schemas[name] = {k:('Int64.Type' if all(isinstance(r[k],int) for r in rows if r[k] is not None)
                               and any(r[k] is not None for r in rows) else 'type number'
                               if all(isinstance(r[k],(int,float)) for r in rows if r[k] is not None)
                               and any(r[k] is not None for r in rows) else 'type text') for k in rows[0]}
    (OUT/'schemas.json').write_text(json.dumps(schemas,indent=2),encoding='utf-8')
    save_database(tables)
    (REPORTS/'audit.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),encoding='utf-8')
    (OUT/'review.json').write_text(json.dumps({'rankings':rankings,'detail':detail,'profiles':profiles,
                                             'metrics':metric_dictionary(),'sensitivity':sens},ensure_ascii=False),encoding='utf-8')
    from .report import write_reports
    write_reports(audit,tables,schemas)
    print(json.dumps({k:audit[k] for k in ['matches','teams','players','events','goals','ranked_candidates']}, ensure_ascii=False),flush=True)


if __name__ == '__main__':
    main()
