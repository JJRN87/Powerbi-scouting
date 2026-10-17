"""Recount selected candidates directly from events and lineups, without build/metrics.

Run: python -m src.verify_remaining_players. This checks source reconciliation,
not the provider's annotations or predictive quality.
"""
import gzip
import json
import math
import sqlite3
from collections import Counter
from .download import ROOT

NAMES = {'Shkodran Mustafi','Diego Reyes','Gustavo Cabral','Filipe Luis','Marcelo',
         'Abdoul Karim Yoda','James Rodríguez','Isco','Éver Banega','Neymar',
         'Lionel Messi','Nolito','Burgui','Cristiano Ronaldo'}
KEYS = ['passes_attempted','passes_completed','progressive_passes','progressive_carries',
        'key_passes','xg_assisted','key_passes_open_play','xg_assisted_open_play',
        'dribbles_completed','npxg','tackles_won','interceptions','aerial_wins','dribbled_past']


def advances(start, end):
    if start is None or end is None: return False
    d0 = ((120-start[0])**2 + (40-start[1])**2)**.5
    d1 = ((120-end[0])**2 + (40-end[1])**2)**.5
    return end[0] >= 60 and d0-d1 >= 10 and d1 <= .75*d0


def minute(clock, period):
    mm, ss = map(float, clock.split(':'))
    start = 0 if period == 1 else 45
    return start + max(0, min(45, mm+ss/60-start))


def main():
    with sqlite3.connect((ROOT/'data/processed/football.sqlite').as_uri()+'?mode=ro', uri=True) as db:
        db.row_factory=sqlite3.Row
        players={r['player_id']:dict(r) for r in db.execute('SELECT * FROM players_season') if r['player'] in NAMES}
    assert len(players)==len(NAMES)
    counts={pid:Counter() for pid in players}
    paths=sorted((ROOT/'data/raw/data/events').glob('*.json.gz'))
    assert len(paths)==380
    successful={'Won','Success','Success In Play','Success Out'}
    restarts={'Corner','Free Kick','Throw-in','Kick Off','Goal Kick'}
    for path in paths:
        events=json.loads(gzip.decompress(path.read_bytes()))
        shots={e['id']:e for e in events if e['type']['name']=='Shot'}
        for e in events:
            pid=e.get('player',{}).get('id')
            if pid not in counts: continue
            c=counts[pid]; kind=e['type']['name']
            c['aerial_wins']+=any(isinstance(v,dict) and v.get('aerial_won') is True for v in e.values())
            if kind=='Pass':
                p=e['pass']; outcome=p.get('outcome',{}).get('name','Complete')
                c['passes_attempted']+=outcome not in {'Unknown','Injury Clearance'}
                c['passes_completed']+=outcome=='Complete'
                c['progressive_passes']+=outcome=='Complete' and p.get('type',{}).get('name') not in restarts and advances(e.get('location'),p.get('end_location'))
                shot=shots.get(p.get('assisted_shot_id'))
                kp=bool(shot or p.get('shot_assist') or p.get('goal_assist'))
                assert not kp or shot
                xg=shot['shot']['statsbomb_xg'] if shot else 0
                c['key_passes']+=kp; c['xg_assisted']+=xg
                set_piece=p.get('type',{}).get('name') in restarts or e.get('play_pattern',{}).get('name') in {'From Corner','From Free Kick'}
                if not set_piece:
                    c['key_passes_open_play']+=kp; c['xg_assisted_open_play']+=xg
            elif kind=='Carry': c['progressive_carries']+=advances(e.get('location'),e['carry'].get('end_location'))
            elif kind=='Dribble': c['dribbles_completed']+=e['dribble']['outcome']['name']=='Complete'
            elif kind=='Shot' and e['shot'].get('type',{}).get('name')!='Penalty': c['npxg']+=e['shot']['statsbomb_xg']
            elif kind=='Duel': c['tackles_won']+=e['duel'].get('type',{}).get('name')=='Tackle' and e['duel'].get('outcome',{}).get('name') in successful
            elif kind=='Interception': c['interceptions']+=e['interception']['outcome']['name'] in successful
            elif kind=='Dribbled Past': c['dribbled_past']+=1
    lineup_paths=sorted((ROOT/'data/raw/data/lineups').glob('*.json.gz'))
    assert len(lineup_paths)==380
    role_ids={'CB':{3,4,5},'FB':{2,6,7,8},'AM_CM':{13,14,15,18,19,20},'W':{12,16,17,21}}
    minutes={pid:Counter() for pid in players}
    for path in lineup_paths:
        for team in json.loads(gzip.decompress(path.read_bytes())):
            for player in team['lineup']:
                pid=player['player_id']
                if pid not in players: continue
                for stint in player['positions']:
                    duration=(minute(stint['to'],stint['to_period']) if stint['to'] else 90)-minute(stint['from'],stint['from_period'])
                    minutes[pid]['minutes']+=duration
                    for role, ids in role_ids.items():
                        if stint['position_id'] in ids: minutes[pid][role]+=duration
    checks=[]
    for pid, player in players.items():
        for k in KEYS:
            assert math.isclose(counts[pid][k],player[k],rel_tol=0,abs_tol=1e-8),(player['player'],k)
        for k in ['minutes',*role_ids]:
            reference=player['minutes'] if k=='minutes' else sum(player['minutes_'+r] for r in k.split('_'))
            assert math.isclose(minutes[pid][k],reference,rel_tol=0,abs_tol=1e-8),(player['player'],k)
        checks.append({'player':player['player'],'event_metrics':len(KEYS),'minute_checks':5,'passed':True})
    result={'event_files_scanned':380,'lineup_files_scanned':380,'players':checks,
            'event_comparisons':len(players)*len(KEYS),'minute_comparisons':len(players)*5,'errors':0,
            'scope':'Recuento independiente de 14 métricas y minutos totales/en roles para 14 candidatos. No audita las anotaciones del proveedor ni todas las métricas de todos los jugadores.'}
    (ROOT/'outputs/remaining-players-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
