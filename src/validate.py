"""Independent checks of downloaded source, exported database and scoring."""
import gzip
import hashlib
import json
import math
import sqlite3
from collections import Counter
from .metrics import MAX_SLOTS
from .download import ROOT, RAW, read_json


def main():
    manifest = read_json(RAW/'manifest.json')
    for r in manifest['files']:
        path = ROOT/r['path']
        payload = path.read_bytes()
        if path.suffix == '.gz':
            payload = gzip.decompress(payload)
        assert hashlib.sha256(payload).hexdigest() == r['sha256'], f'Hash mismatch: {path}'
        assert len(payload) == r['bytes']
    print(f"Verified {len(manifest['files'])} source hashes", flush=True)
    db = sqlite3.connect(ROOT/'data/processed/football.sqlite')
    db.row_factory = sqlite3.Row
    assert db.execute('PRAGMA integrity_check').fetchone()[0] == 'ok'
    players = db.execute('SELECT * FROM players_season').fetchall()
    for row in db.execute('SELECT * FROM player_match'):
        assert row['key_passes']==row['key_passes_open_play']+row['key_passes_set_piece']
        assert math.isclose(row['xg_assisted'], row['xg_assisted_open_play']+row['xg_assisted_set_piece'],abs_tol=1e-10)
    for p in players:
        assert p['key_passes']==p['key_passes_open_play']+p['key_passes_set_piece']
        assert math.isclose(p['xg_assisted'],p['xg_assisted_open_play']+p['xg_assisted_set_piece'],abs_tol=1e-8)
        totals = db.execute('SELECT SUM(minutes), SUM(goals), SUM(shots), SUM(passes_completed), SUM(passes_attempted) FROM player_match WHERE player_id=?',(p['player_id'],)).fetchone()
        for actual, key in zip(totals,['minutes','goals','shots','passes_completed','passes_attempted']):
            assert math.isclose(actual,p[key],abs_tol=1e-7), (p['player_id'],key)
        assert 0 <= p['passes_completed'] <= p['passes_attempted']
        assert 0 <= p['dribbles_completed'] <= p['dribbles_attempted']
        assert 0 <= p['tackles_won'] <= p['tackles_attempted']
        if p['minutes'] > 0:
            assert math.isclose(p['shots_p90'],p['shots']*90/p['minutes'],abs_tol=1e-8)
        if p['passes_attempted'] > 0:
            assert math.isclose(p['pass_completion_pct'],100*p['passes_completed']/p['passes_attempted'],abs_tol=1e-8)
    ranks = db.execute('SELECT * FROM rankings').fetchall()
    from .build import prepare_rankings
    historical,_,_ = prepare_rankings([dict(p) for p in players], read_json(ROOT/'config/history/profiles_v1.json'))
    prior = {r['candidate_id']:r for r in historical}
    assert {r['candidate_id'] for r in ranks} == set(prior), 'Changed comparison cohort'
    for r in ranks:
        if r['profile_id']!='organizador':
            assert r['score_base']==prior[r['candidate_id']]['score_base']
            assert r['rank_base']==prior[r['candidate_id']]['rank_base']
    for r in ranks:
        weights = [r[f'weight_{i}'] for i in range(1, MAX_SLOTS + 1)]
        ps = [r[f'percentile_{i}'] for i in range(1, MAX_SLOTS + 1)]
        recomputed = round(sum(w*p for w,p in zip(weights,ps) if w>0)/sum(weights),8)
        assert abs(recomputed-r['score_base'])<1e-8
        assert 0 <= r['score_base'] <= 100
        contribution = db.execute('SELECT SUM(contribution_base) FROM ranking_detail WHERE candidate_id=?',(r['candidate_id'],)).fetchone()[0]
        assert abs(contribution-r['score_base'])<1e-7
    for profile in db.execute('SELECT * FROM profiles'):
        group = [r for r in ranks if r['profile_id']==profile['profile_id']]
        scores = sorted({r['score_base'] for r in group}, reverse=True)
        for r in group:
            assert r['minutes']>=profile['minimum_minutes'] and r['role_share']>=profile['minimum_role_share']
            assert r['rank_base']==scores.index(r['score_base'])+1
    # Five deterministic games throughout the season, direct formulas independent of event_counts.
    ids = [r[0] for r in db.execute('SELECT match_id FROM matches ORDER BY match_date,match_id')]
    for mid in [ids[i] for i in [0,94,189,284,379]]:
        events = read_json(RAW/f'data/events/{mid}.json.gz')
        passed = Counter(e['player']['id'] for e in events if e['type']['name']=='Pass' and 'outcome' not in e['pass'])
        shots = Counter(e['player']['id'] for e in events if e['type']['name']=='Shot')
        # Independently classify creation and its xG without calling production helper.
        shots_by_id={e['id']:e for e in events if e['type']['name']=='Shot'}
        creations=Counter(); expected_xg=Counter()
        for e in events:
            if e['type']['name']!='Pass' or not any(e['pass'].get(k) for k in ['shot_assist','goal_assist','assisted_shot_id']):
                continue
            dead = e['play_pattern']['name'] in ['From Corner','From Free Kick'] or e['pass'].get('type',{}).get('name') in ['Corner','Free Kick','Throw-in','Goal Kick','Kick Off']
            key=(e['player']['id'],'set_piece' if dead else 'open_play')
            creations[key]+=1
            expected_xg[key]+=shots_by_id[e['pass']['assisted_shot_id']]['shot']['statsbomb_xg']
        for r in db.execute('SELECT * FROM player_match WHERE match_id=?',(mid,)):
            for context in ['open_play','set_piece']:
                key=(r['player_id'],context)
                assert r['key_passes_'+context]==creations[key]
                assert math.isclose(r['xg_assisted_'+context],expected_xg[key],abs_tol=1e-10)
        for r in db.execute('SELECT player_id,passes_completed,shots FROM player_match WHERE match_id=?',(mid,)):
            assert r['passes_completed']==passed[r['player_id']]
            assert r['shots']==shots[r['player_id']]
    assert db.execute('SELECT COUNT(*) FROM matches WHERE goals_reconciled=1').fetchone()[0]==380
    db.close()
    result={'status':'passed','source_files_hashed':len(manifest['files']),
            'players_reconciled':len(players),'candidate_scores_verified':len(ranks),
            'direct_source_sample_matches':5,'creation_partition_verified':True,
            'unchanged_other_profiles':6,'powerbi_engine_tested':False}
    (ROOT/'outputs/verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    print(json.dumps(result),flush=True)


if __name__=='__main__':
    main()
