"""Independent direct-event recount for notable candidates in this review."""
import gzip
import json
import math
import sqlite3
from collections import Counter
from .download import ROOT

NAMES = {'Augusto Fernández','Ignacio Camacho','Asier Illarramendi','Sergio Busquets',
         'Luis Suárez','Karim Benzema','Kévin Gameiro','Imanol Agirretxe'}


def main():
    with sqlite3.connect((ROOT/'data/processed/football.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        players={r['player_id']:dict(r) for r in db.execute('SELECT * FROM players_season') if r['player'] in NAMES}
    assert len(players)==len(NAMES)
    counts={pid:Counter() for pid in players}
    paths=sorted((ROOT/'data/raw/data/events').glob('*.json.gz'))
    assert len(paths)==380
    for path in paths:
        events=json.loads(gzip.decompress(path.read_bytes()))
        for e in events:
            pid=e.get('player',{}).get('id')
            if pid not in counts: continue
            c=counts[pid]; kind=e['type']['name']
            if kind=='Interception' and e['interception']['outcome']['name'] in {'Won','Success','Success In Play','Success Out'}: c['interceptions']+=1
            if kind=='Duel' and e['duel'].get('type',{}).get('name')=='Tackle' and e['duel'].get('outcome',{}).get('name') in {'Won','Success','Success In Play','Success Out'}: c['tackles_won']+=1
            if kind=='Ball Recovery' and not e.get('ball_recovery',{}).get('recovery_failure',False): c['recoveries']+=1
            if kind=='Shot':
                c['shots']+=1
                if e['shot']['type']['name']!='Penalty':
                    c['npxg']+=e['shot']['statsbomb_xg']
                    c['non_penalty_goals']+=e['shot']['outcome']['name']=='Goal'
    checks=[]
    for pid,c in counts.items():
        for k in ['interceptions','tackles_won','recoveries','shots','npxg','non_penalty_goals']:
            assert math.isclose(c[k],players[pid][k],rel_tol=0,abs_tol=1e-8),(pid,k,c[k],players[pid][k])
        checks.append({'player':players[pid]['player'],'metrics_checked':6,'passed':True})
    result={'event_files_scanned':len(paths),'players':checks,'comparisons':len(checks)*6,'errors':0,
            'scope':'Recuento directo de seis métricas para ocho jugadores, sin llamar al agregador del proyecto. No valida cada métrica ni el rendimiento futuro.'}
    (ROOT/'outputs/review-players-verification.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False))


if __name__=='__main__': main()
