"""Read-only weight robustness analysis. Does not change profiles or rankings."""
import itertools
import json
import math
import random
import sqlite3
from collections import Counter
from datetime import datetime, timezone

from .download import ROOT, read_json


def main():
    config = read_json(ROOT/'config/profiles.json')
    profile = next(p for p in config['profiles'] if p['profile_id']=='organizador')
    keys = list(profile['weights'])
    base = list(profile['weights'].values())
    with sqlite3.connect(ROOT/'data/processed/football.sqlite') as db:
        db.row_factory = sqlite3.Row
        candidates = [dict(r) for r in db.execute("SELECT * FROM rankings WHERE profile_id='organizador' ORDER BY player_id")]
        details = [dict(r) for r in db.execute("SELECT * FROM ranking_detail WHERE profile_id='organizador'")]
    target = next(r for r in candidates if r['player']=='André Gomes')
    rivals = [next(r for r in candidates if r['player']==name) for name in ['Toni Kroos','Roberto Trashorras']]
    values = {r['player_id']: [r[f'percentile_{i+1}'] for i in range(len(keys))] for r in candidates}
    for r in candidates:
        assert [r[f'metric_{i+1}'] for i in range(len(keys))] == keys
        assert [r[f'weight_{i+1}'] for i in range(len(keys))] == base

    def evaluate(weights):
        scores={pid:round(sum(w*v for w,v in zip(weights,ps))/sum(weights),8) for pid,ps in values.items()}
        ordered=sorted(set(scores.values()),reverse=True)
        ranks={pid:ordered.index(s)+1 for pid,s in scores.items()}
        return scores,ranks

    baseline,_=evaluate(base)
    for r in candidates:
        assert math.isclose(baseline[r['player_id']],r['score_base'],abs_tol=1e-8)

    def summarize(weight_sets):
        counts=Counter(); beat=Counter(); ties=Counter(); outrank=Counter()
        for ws in weight_sets:
            scores,ranks=evaluate(ws)
            counts[ranks[target['player_id']]]+=1
            for r in candidates:
                if scores[r['player_id']]>scores[target['player_id']]:outrank[r['player']]+=1
            for r in rivals:
                delta=scores[target['player_id']]-scores[r['player_id']]
                beat[r['player']]+=int(delta>0)
                ties[r['player']]+=int(delta==0)
        n=sum(counts.values())
        return {'scenarios':n,'rank_counts':dict(sorted(counts.items())),
                'beats_rival_counts':dict(beat),'ties_rival_counts':dict(ties),
                'outranked_by_counts':dict(outrank)}

    single=[]
    single_detail=[]
    for i,k in enumerate(keys):
        for factor in [.8,1.2]:
            ws=base.copy();ws[i]*=factor;single.append(ws)
            scores,ranks=evaluate(ws)
            single_detail.append({'metric':k,'factor':factor,'normalized_weight_pct':100*ws[i]/sum(ws),
                                  'andre_rank':ranks[target['player_id']],
                                  'andre_score':scores[target['player_id']]})
    corners=[[w*f for w,f in zip(base,fs)] for fs in itertools.product([.8,1.2],repeat=len(base))]
    rng=random.Random(20261017)
    random_weights=[[w*rng.uniform(.8,1.2) for w in base] for _ in range(10000)]

    # Pairwise break-even: transfer t percentage points from one metric to another.
    thresholds=[]
    margins=[]
    for rival in rivals:
        delta=[a-b for a,b in zip(values[target['player_id']],values[rival['player_id']])]
        numerator=sum(w*d for w,d in zip(base,delta))
        margins.append({'rival':rival['player'],'baseline_margin_points':numerator/sum(base),
                        'metric_contributions':[{'metric':k,'weight':w,'difference_points':w*d/sum(base)} for k,w,d in zip(keys,base,delta)],
                        'min_numerator_box':sum(w*(.8 if d>0 else 1.2)*d for w,d in zip(base,delta)),
                        'max_numerator_box':sum(w*(1.2 if d>0 else .8)*d for w,d in zip(base,delta))})
        for donor in range(len(base)):
            for receiver in range(len(base)):
                slope=delta[receiver]-delta[donor]
                if slope>=0:continue
                t=-numerator/slope
                if 0<t<=base[donor]:
                    ws=base.copy();ws[donor]-=t;ws[receiver]+=t
                    at=sum(w*d for w,d in zip(ws,delta))
                    assert abs(at)<1e-8
                    thresholds.append({'rival':rival['player'],'from':keys[donor],'to':keys[receiver],
                                       'transfer_percentage_points':t})
    # Conservative rank bounds for every point in the weight box, not just samples.
    always_above=[];possibly_above=[]
    for r in candidates:
        if r['player_id']==target['player_id']:continue
        delta=[a-b for a,b in zip(values[r['player_id']],values[target['player_id']])]
        low=sum(w*(.8 if d>0 else 1.2)*d for w,d in zip(base,delta))
        high=sum(w*(1.2 if d>0 else .8)*d for w,d in zip(base,delta))
        if low>1e-8:always_above.append(r['player'])
        if high>1e-8:possibly_above.append(r['player'])
    # Rank for this robustness bound counts people strictly ahead (competition rank).
    # Dense rank may be lower at exact ties among other candidates.

    scenarios=[('Base',{})]
    def transfer(label,donor,receiver,amount):
        scenarios.append((label,{donor:-amount,receiver:amount}))
    transfer('2 puntos de regate a progresión','dribbles_completed_p90','progressive_passes_p90',2)
    transfer('5 puntos de regate a progresión','dribbles_completed_p90','progressive_passes_p90',5)
    transfer('5 puntos de xG abierto a progresión','xg_assisted_open_play_p90','progressive_passes_p90',5)
    transfer('5 puntos de regate a precisión','dribbles_completed_p90','pass_completion_pct',5)
    transfer('10 puntos de xG abierto a pases de tiro abiertos','xg_assisted_open_play_p90','key_passes_open_play_p90',10)
    transfer('5 puntos de progresión a xG abierto','progressive_passes_p90','xg_assisted_open_play_p90',5)
    named=[]
    for label,changes in scenarios:
        ws=[w+changes.get(k,0) for k,w in zip(keys,base)]
        assert sum(ws)==sum(base) and min(ws)>=0
        scores,ranks=evaluate(ws)
        named.append({'scenario':label,'weights':dict(zip(keys,ws)),
                      'players':[{'player':r['player'],'rank':ranks[r['player_id']],'score':scores[r['player_id']]} for r in [target,*rivals]]})
    result={'created_utc':datetime.now(timezone.utc).isoformat(),'cohort_size':len(candidates),
            'weights':dict(zip(keys,base)), 'baseline':[r for r in candidates if r['player_id'] in [target['player_id'],*(x['player_id'] for x in rivals)]],
            'breakdown':[d for d in details if d['player_id'] in [target['player_id'],*(x['player_id'] for x in rivals)]],
            'pairwise_margins':margins,'one_at_a_time':summarize(single),'one_at_a_time_detail':single_detail,
            'all_corners_20pct':summarize(corners),'random_20pct':summarize(random_weights),
            'random_seed':20261017,'sampling_definition':'Independent Uniform(0.8,1.2) multipliers on each base weight, then normalize. Not a probability model of player quality.',
            'always_above_in_box':always_above,'possibly_above_in_box':possibly_above,
            'conservative_max_number_ahead':len(possibly_above),
            'transfer_thresholds':sorted(thresholds,key=lambda x:x['transfer_percentage_points']),
            'named_scenarios':named,
            'limitations':['Fixed cohort and percentiles; measures weight sensitivity only.',
                           'No sampling uncertainty in match observations or corrections for role, possession or team context.',
                           'Creation counts and assisted xG are correlated.']}
    path=ROOT/'outputs/organizador_robustez.json'
    path.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    summary={k:result[k] for k in ['pairwise_margins','one_at_a_time','one_at_a_time_detail','all_corners_20pct','random_20pct','always_above_in_box','possibly_above_in_box','named_scenarios']}
    summary['smallest_transfers']=result['transfer_thresholds'][:12]
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=='__main__':
    main()
