"""Review pivote/striker weights without changing production profiles or rankings.

Run: python -m src.analyze_profiles. Outputs stay local; the public report is
an editorial summary, not a redistribution of the database.
"""
import hashlib
import itertools
import json
import math
import random
import sqlite3
from collections import Counter
from pathlib import Path
from statistics import correlation, median

from .download import ROOT
from .metrics import NEGATIVE, percentile, score

SEED = 20261017
SAMPLES = 10000
# Hypotheses specified by function, not optimized to put particular names first.
SCENARIOS = {
    'pivote': {
        'Base': [25, 25, 15, 20, 10, 5],
        'Mas salida de balon': [25, 20, 10, 25, 15, 5],
        'Recuperador': [30, 30, 20, 10, 5, 5],
        'Distribuidor': [15, 15, 10, 35, 20, 5],
    },
    'delantero': {
        'Base': [35, 20, 15, 15, 15],
        'Menos resultado y volumen': [45, 10, 10, 20, 15],
        'Finalizador': [45, 30, 10, 5, 10],
        'Asociativo': [35, 10, 10, 30, 15],
    },
}


def evaluate(matrix, weights):
    if not weights or any(not math.isfinite(w) or w < 0 for w in weights):
        raise ValueError('Finite, non-negative weights required')
    if sum(weights) == 0:
        return {pid: None for pid in matrix}, {pid: None for pid in matrix}
    scores = {pid: round(sum(w*v for w, v in zip(weights, values)) / sum(weights), 8)
              for pid, values in matrix.items()}
    dense = {s: i+1 for i, s in enumerate(sorted(set(scores.values()), reverse=True))}
    return scores, {pid: dense[s] for pid, s in scores.items()}


def summarize(matrix, weight_sets):
    histories = {pid: [] for pid in matrix}
    for weights in weight_sets:
        _, ranks = evaluate(matrix, weights)
        for pid, rank in ranks.items():
            histories[pid].append(rank)
    return {pid: {'n': len(rs), 'best': min(rs), 'worst': max(rs),
                  'median': median(rs),
                  'top1_pct': 100*sum(r <= 1 for r in rs)/len(rs),
                  'top3_pct': 100*sum(r <= 3 for r in rs)/len(rs),
                  'top10_pct': 100*sum(r <= 10 for r in rs)/len(rs)}
            for pid, rs in histories.items()}


def leader_certificate(matrix, weights, leader, spread):
    """Minimum *unrounded numerator* lead over every rival in the whole box.

    Pairwise scores have a common positive denominator. Linear numerators
    reach their minimum at a box vertex. Thus a positive lower bound above
    rounding tolerance proves the lead for all weights in this box.
    """
    margins = []
    for pid, vals in matrix.items():
        if pid == leader:
            continue
        delta = [a-b for a, b in zip(matrix[leader], vals)]
        low = sum(w*d*(1-spread if d >= 0 else 1+spread)
                  for w, d in zip(weights, delta))
        margins.append((low / (sum(weights)*(1+spread)), pid))
    bound, rival = min(margins)
    return {'spread': spread, 'strict_first_proven': bound > 1e-8,
            'conservative_score_margin_lower_bound': bound, 'rival_id': rival}


def review(db, profile, seasons):
    pid = profile['profile_id']
    keys = list(profile['weights'])
    base = list(profile['weights'].values())
    rows = [dict(r) for r in db.execute('SELECT * FROM rankings WHERE profile_id=? ORDER BY player_id', (pid,))]
    matrix = {r['player_id']: [r[f'percentile_{i+1}'] for i in range(len(keys))] for r in rows}
    scores, ranks = evaluate(matrix, base)
    assert base == SCENARIOS[pid]['Base']
    for r in rows:
        player_id = r['player_id']
        assert [r[f'metric_{i+1}'] for i in range(len(keys))] == keys
        assert [r[f'weight_{i+1}'] for i in range(len(keys))] == base
        assert scores[player_id] == r['score_base'] and ranks[player_id] == r['rank_base']
        # Independently recompute every percentile from season-level raw rates.
        rebuilt = {k: percentile(seasons[player_id][k],
                    [seasons[x['player_id']][k] for x in rows], k in NEGATIVE) for k in keys}
        assert all(abs(rebuilt[k]-matrix[player_id][i]) < 1e-9 for i, k in enumerate(keys))
        assert score(rebuilt, profile['weights']) == scores[player_id]
    one = []
    for i in range(len(base)):
        for f in [.8, 1.2]:
            ws = base.copy(); ws[i] *= f; one.append(ws)
    corners = [[w*f for w, f in zip(base, fs)] for fs in itertools.product([.8, 1.2], repeat=len(base))]
    stress = {}
    for spread in [.2, .5]:
        rng = random.Random(SEED)
        stress[str(spread)] = summarize(matrix, ([w*rng.uniform(1-spread, 1+spread) for w in base] for _ in range(SAMPLES)))
    one_summary, corner_summary = summarize(matrix, one), summarize(matrix, corners)
    named = []
    for label, weights in SCENARIOS[pid].items():
        assert len(weights) == len(keys) and sum(weights) == 100
        sc, rk = evaluate(matrix, weights)
        named.append({'label': label, 'weights': dict(zip(keys, weights)),
                      'ranking': [{'player': r['player'], 'player_id': r['player_id'],
                                   'rank': rk[r['player_id']], 'score': sc[r['player_id']]}
                                  for r in sorted(rows, key=lambda r: (-sc[r['player_id']], r['player_id']))]})
    ablations = []
    for i, key in enumerate(keys):
        ws = base.copy(); ws[i] = 0
        sc, rk = evaluate(matrix, ws)
        ablations.append({'removed': key, 'ranks': rk})
    ordered = sorted(rows, key=lambda r: (r['rank_base'], r['player_id']))
    player_summaries = []
    for r in ordered:
        player_id = r['player_id']; season = seasons[player_id]
        player_summaries.append({k: r[k] for k in ['player_id','player','teams','minutes','role_share','rank_base','score_base']} | {
            'dm_share': season['minutes_DM']/season['minutes'],
            'metrics': [{'metric': k, 'raw': season[k], 'percentile': matrix[player_id][i],
                         'weight': base[i], 'contribution': base[i]*matrix[player_id][i]/sum(base)} for i, k in enumerate(keys)],
            'one_at_a_time': one_summary[player_id], 'corners20': corner_summary[player_id],
            'random20': stress['0.2'][player_id], 'random50': stress['0.5'][player_id],
            'remove_one_rank_range': [min(a['ranks'][player_id] for a in ablations), max(a['ranks'][player_id] for a in ablations)]})
    correlations = []
    for a, b in itertools.combinations(range(len(keys)), 2):
        correlations.append({'a': keys[a], 'b': keys[b],
                             'spearman_oriented': correlation([v[a] for v in matrix.values()], [v[b] for v in matrix.values()])})
    filters = []
    for minimum in [1500, 1800]:
        chosen = {r['player_id']: matrix[r['player_id']] for r in rows if r['minutes'] >= minimum}
        sc, rk = evaluate(chosen, base)
        filters.append({'minimum_minutes': minimum, 'size': len(chosen),
                        'top10': [{'player':r['player'],'rank':rk[r['player_id']]} for r in ordered if r['player_id'] in chosen and rk[r['player_id']]<=10]})
    strict_dm = None
    if pid == 'pivote':
        strict = [r for r in rows if seasons[r['player_id']]['minutes_DM']/r['minutes'] >= .5]
        strict_dm = {'size':len(strict), 'removed_from_base_top10':[r['player'] for r in ordered if r['rank_base']<=10 and r not in strict]}
    exclusions = []
    for s in seasons.values():
        if s['player'] in ['Lionel Messi','Cristiano Ronaldo','Neymar','Sergio Busquets','Koke','Luka Modrić']:
            share = sum(s['minutes_'+role] for role in profile['roles'])/s['minutes'] if s['minutes'] else 0
            exclusions.append({'player':s['player'], 'minutes':s['minutes'], 'role_share':share,
                               'eligible':s['player_id'] in matrix, 'rank':ranks.get(s['player_id'])})
    return {'profile_id':pid, 'cohort_size':len(rows), 'base_weights':profile['weights'],
            'baseline_recomputed_ok':len(rows), 'players':player_summaries,
            'named_scenarios':named, 'ablations':ablations, 'correlations':correlations,
            'leader_certificates':[leader_certificate(matrix, base, ordered[0]['player_id'], s) for s in [.2,.5]],
            'minutes_filter_fixed_percentiles':filters, 'strict_dm_diagnostic':strict_dm, 'eligibility_examples':exclusions}


def main():
    config = json.loads((ROOT/'config/profiles.json').read_text(encoding='utf-8'))
    paths = ['config/profiles.json','data/processed/football.sqlite','data/processed/rankings.csv']
    before = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    with sqlite3.connect((ROOT/'data/processed/football.sqlite').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory = sqlite3.Row
        seasons = {r['player_id']:dict(r) for r in db.execute('SELECT * FROM players_season')}
        results = [review(db, p, seasons) for p in config['profiles'] if p['profile_id'] in SCENARIOS]
    assert before == {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}
    result = {'seed':SEED,'samples_per_random_box':SAMPLES,'input_sha256':before,
              'method':'Independent uniform multipliers on base weights, normalized implicitly; fixed cohort and percentiles. Dense ranks, including ties. Frequencies are scenario frequencies, not player-quality probabilities.',
              'production_unchanged':True,'profiles':results}
    (ROOT/'outputs/revision_pivote_delantero.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    for p in results:
        print(p['profile_id'], 'N=',p['cohort_size'], 'certificates=',p['leader_certificates'])
        for r in p['players'][:12]:
            print(r['player'],r['rank_base'],round(r['score_base'],2),'20%',r['random20'],'50%',r['random50'])
        for s in p['named_scenarios']:
            print(s['label'],[(r['player'],r['rank']) for r in s['ranking'][:6]])
        print('eligibility',p['eligibility_examples'],'DM',p['strict_dm_diagnostic'])


if __name__ == '__main__':
    main()
