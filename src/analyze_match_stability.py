"""Match resampling and team-context diagnostics; production data stays unchanged.

Requires NumPy (requirements-analysis.txt). Run: python -m src.analyze_match_stability
"""
import argparse
import hashlib
import json
import sqlite3
from collections import defaultdict

import numpy as np

from .download import ROOT
from .metrics import NEGATIVE

SEED = 20261018
DEFENSIVE = {'tackles_won', 'interceptions', 'recoveries', 'dribbled_past'}
UNCHANGED = {'minutes', 'passes_attempted', 'passes_completed', 'aerial_wins'}


def percentiles(values, negative=False):
    """Midrank ECDF, last axis = candidates; deterministic handling of equal rates."""
    values = np.round(np.asarray(values, dtype=float), 12)
    if not np.isfinite(values).all():
        raise ValueError('Missing or non-finite rate in a fixed candidate cohort')
    out = 100*((values[..., :, None] > values[..., None, :]).sum(axis=-1)
               + .5*(values[..., :, None] == values[..., None, :]).sum(axis=-1))/values.shape[-1]
    return 100-out if negative else out


def dense_ranks(scores):
    scores = np.atleast_2d(np.round(scores, 8))
    return np.array([np.unique(-s, return_inverse=True)[1]+1 for s in scores])


def profile_score(totals, profile, fields):
    """totals: samples x candidates x fields; percentages are ratios of totals."""
    ix = {k:i for i,k in enumerate(fields)}
    minutes = totals[:, :, ix['minutes']]
    if np.any(minutes <= 0):
        raise ValueError('A candidate has no minutes in this replicate')
    out = np.zeros(minutes.shape)
    for metric, weight in profile['weights'].items():
        if metric == 'pass_completion_pct':
            denominator = totals[:, :, ix['passes_attempted']]
            if np.any(denominator <= 0): raise ValueError('No pass attempts in replicate')
            rate = 100*totals[:, :, ix['passes_completed']]/denominator
        else:
            rate = 90*totals[:, :, ix[metric.removesuffix('_p90')]]/minutes
        out += weight*percentiles(rate, metric in NEGATIVE)
    return np.round(out/sum(profile['weights'].values()), 8)


def context_factor(share, metric, strength=1, defense_only=False):
    if not 0 < share < 1: raise ValueError('Pass share must be strictly between zero and one')
    if metric in UNCHANGED: return 1.0
    if metric in DEFENSIVE: return (.5/(1-share))**strength
    return 1.0 if defense_only else (.5/share)**strength


def rank_summary(ranks):
    lo, med, hi = np.quantile(ranks, [.025,.5,.975], method='inverted_cdf')
    return {'q025':int(lo),'median':int(med),'q975':int(hi),
            'minimum':int(ranks.min()),'maximum':int(ranks.max()),
            'top1_pct':float(100*np.mean(ranks <= 1)),
            'top3_pct':float(100*np.mean(ranks <= 3)),
            'top10_pct':float(100*np.mean(ranks <= 10))}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--samples',type=int,default=2000)
    args=parser.parse_args()
    if args.samples < 100: raise ValueError('At least 100 replicates required')
    source_paths=['config/profiles.json','data/processed/football.sqlite','data/processed/rankings.csv']
    hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths}
    config=json.loads((ROOT/'config/profiles.json').read_text(encoding='utf-8'))
    with sqlite3.connect((ROOT/'data/processed/football.sqlite').as_uri()+'?mode=ro',uri=True) as db:
        db.row_factory=sqlite3.Row
        matches=[dict(r) for r in db.execute('SELECT * FROM matches ORDER BY match_id')]
        pm=[dict(r) for r in db.execute('SELECT * FROM player_match ORDER BY player_id,match_id')]
        season={r['player_id']:dict(r) for r in db.execute('SELECT * FROM players_season')}
        rankings=[dict(r) for r in db.execute('SELECT * FROM rankings ORDER BY profile_id,player_id')]
    players=sorted({r['player_id'] for r in rankings}); pidx={p:i for i,p in enumerate(players)}
    midx={m['match_id']:i for i,m in enumerate(matches)}
    fields=sorted({'minutes','passes_attempted','passes_completed'} |
                  {k.removesuffix('_p90') for p in config['profiles'] for k in p['weights'] if k.endswith('_p90')})
    cube=np.zeros((len(matches),len(players),len(fields)))
    team_passes=defaultdict(float)
    for r in pm: team_passes[r['match_id'],r['team_id']]+=r['passes_attempted']
    shares={}
    points=defaultdict(int)
    for m in matches:
        h,a=m['home_team_id'],m['away_team_id']; mid=m['match_id']
        total=team_passes[mid,h]+team_passes[mid,a]
        assert total>0
        shares[mid,h]=team_passes[mid,h]/total; shares[mid,a]=team_passes[mid,a]/total
        assert abs(shares[mid,h]+shares[mid,a]-1)<1e-12
        if m['home_goals']==m['away_goals']: points[h]+=1; points[a]+=1
        else: points[h if m['home_goals']>m['away_goals'] else a]+=3
    # Points threshold avoids inventing official tie-break rules.
    sixth_points=sorted(points.values(),reverse=True)[5]
    top_opponents={t for t,v in points.items() if v>=sixth_points}
    match_by_id={m['match_id']:m for m in matches}
    player_rows=defaultdict(list)
    for r in pm:
        if r['player_id'] not in pidx: continue
        cube[midx[r['match_id']],pidx[r['player_id']]] += [r[k] for k in fields]
        player_rows[r['player_id']].append(r)
    total=cube.sum(axis=0)
    for pid,i in pidx.items():
        for j,k in enumerate(fields):
            assert abs(total[i,j]-season[pid][k]) < 1e-7,(pid,k)
    # Shared fixture multiplicities retain covariance within each match.
    rng=np.random.default_rng(SEED)
    fixture_weights=rng.multinomial(len(matches),np.full(len(matches),1/len(matches)),size=args.samples)
    weeks=sorted({m['match_week'] for m in matches})
    assert len(matches)==380 and len(weeks)==38
    week_draws=rng.multinomial(len(weeks),np.full(len(weeks),1/len(weeks)),size=args.samples)
    week_weights=week_draws[:,[weeks.index(m['match_week']) for m in matches]]
    totals_by_scheme={}
    for label,weights in [('matches',fixture_weights),('matchweeks',week_weights)]:
        sampled=np.empty((args.samples,len(players),len(fields)))
        for p in range(len(players)):
            active=np.flatnonzero(np.any(cube[:,p,:]!=0,axis=1))
            sampled[:,p,:]=weights[:,active] @ cube[active,p,:]
        totals_by_scheme[label]=sampled
    context_totals={}
    for label,strength,defonly in [('defense_only',1,True),('all_half',.5,False),('all_full',1,False)]:
        adjusted=np.zeros_like(total)
        for pid,rows in player_rows.items():
            for r in rows:
                share=shares[r['match_id'],r['team_id']]
                adjusted[pidx[pid]] += [r[k]*context_factor(share,k,strength,defonly) for k in fields]
        context_totals[label]=adjusted
    results=[]
    for profile in config['profiles']:
        rows=[r for r in rankings if r['profile_id']==profile['profile_id']]
        ix=[pidx[r['player_id']] for r in rows]
        base=profile_score(total[None,ix,:],profile,fields)[0]
        br=dense_ranks(base)[0]
        assert np.allclose(base,[r['score_base'] for r in rows],rtol=0,atol=1e-8)
        assert np.array_equal(br,[r['rank_base'] for r in rows])
        distributions={}
        for label,sampled in totals_by_scheme.items():
            # Remove an invalid replicate for the entire profile, never impute a player.
            valid=(sampled[:,ix,fields.index('minutes')]>0).all(axis=1)
            if 'pass_completion_pct' in profile['weights']:
                valid &= (sampled[:,ix,fields.index('passes_attempted')]>0).all(axis=1)
            scores=profile_score(sampled[valid][:,ix,:],profile,fields)
            distributions[label]=(dense_ranks(scores),int((~valid).sum()))
        leaveout=profile_score(total[None,ix,:]-cube[:,ix,:],profile,fields)
        lr=dense_ranks(leaveout)
        contexts={}
        for label,adjusted in context_totals.items():
            sc=profile_score(adjusted[None,ix,:],profile,fields)[0]
            contexts[label]=(sc,dense_ranks(sc)[0])
        summaries=[]
        for j,r in enumerate(rows):
            pid=r['player_id']; prs=player_rows[pid]; minutes=r['minutes']
            played=[p for p in prs if p['minutes']>0]
            pass_share=sum(p['minutes']*shares[p['match_id'],p['team_id']] for p in prs)/minutes
            top_minutes=0
            for p in prs:
                m=match_by_id[p['match_id']]
                opp=m['away_team_id'] if p['team_id']==m['home_team_id'] else m['home_team_id']
                if opp in top_opponents: top_minutes+=p['minutes']
            summary={k:r[k] for k in ['player_id','player','teams','minutes','role_share','rank_base','score_base']}
            summary.update({'positive_minute_matches':len(played),'starts':sum(p['started'] for p in prs),
                            'appearances_at_most_30_min':sum(p['minutes']<=30 for p in played),
                            'minute_weighted_team_pass_share':pass_share,
                            'minutes_against_top_points_teams_pct':100*top_minutes/minutes,
                            'bootstrap':{label:rank_summary(rs[:,j]) for label,(rs,_) in distributions.items()},
                            'leave_one_match_out':{'best':int(lr[:,j].min()),'worst':int(lr[:,j].max())},
                            'context':{label:{'rank':int(ranks[j]),'score':float(sc[j])} for label,(sc,ranks) in contexts.items()}})
            if r['player'] in {'Abdoul Karim Yoda','Burgui'}:
                details=[]
                for p in prs:
                    m=match_by_id[p['match_id']]; mi=midx[p['match_id']]
                    details.append({'date':m['match_date'],'match':m['home_team']+' - '+m['away_team'],
                                    'minutes':p['minutes'],'key_passes':p['key_passes'],'xg_assisted':p['xg_assisted'],
                                    'progressive_carries':p['progressive_carries'],'dribbles_completed':p['dribbles_completed'],
                                    'rank_without_match':int(lr[mi,j]),'score_without_match':float(leaveout[mi,j])})
                summary['match_details']=details
                summary['maximum_single_match_xg_assisted_share']=max(p['xg_assisted'] for p in prs)/season[pid]['xg_assisted']
            summaries.append(summary)
        baseline_top={r['player_id'] for r in rows if r['rank_base']<=10}
        comparisons={}
        for label,(_,ranks) in contexts.items():
            top={r['player_id'] for r,k in zip(rows,ranks) if k<=10}
            comparisons[label]={'spearman':float(np.corrcoef(percentiles(base),percentiles(-ranks))[0,1]),
                                'base_top10_size':len(baseline_top),'scenario_top10_size':len(top),
                                'retained_top10':len(baseline_top & top)}
        results.append({'profile_id':profile['profile_id'],'cohort_size':len(rows),
                        'invalid_replicates':{label:n for label,(_,n) in distributions.items()},
                        'context_comparison':comparisons,'players':sorted(summaries,key=lambda p:(p['rank_base'],p['player_id']))})
    assert hashes=={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in source_paths}
    result={'seed':SEED,'samples_per_scheme':args.samples,'numpy_version':np.__version__,
            'input_sha256':hashes,'production_unchanged':True,'baseline_comparisons':len(rankings),
            'aggregated_values_checked':len(players)*len(fields),'source_matches':380,'source_matchweeks':38,
            'pass_share_range':[min(shares.values()),max(shares.values())],
            'method':'Shared fixture bootstrap and shared matchweek bootstrap. Original eligible cohorts and weights fixed; rates and within-profile percentiles rebuilt each draw. Rank intervals are descriptive 2.5/97.5 percentiles, not future performance confidence bounds.',
            'context_method':'Team share of evaluated pass attempts per fixture, not time possession. Counts scaled by (0.5/share)^strength for attacking metrics and (0.5/(1-share))^strength for defensive metrics; unchanged minutes, pass accuracy and aerial wins. Diagnostic only.',
            'profiles':results}
    out=ROOT/'outputs/match-stability.json'
    out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print('Saved',out,'baseline',len(rankings),'numpy',np.__version__)
    for p in results:
        print(p['profile_id'],'invalid',p['invalid_replicates'],'context',p['context_comparison'])
        for r in p['players'][:5]: print(r['player'],r['rank_base'],r['bootstrap'],r['context'])


if __name__=='__main__': main()
