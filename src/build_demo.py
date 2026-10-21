"""Export the derived scouting analysis as a static GitHub Pages demo.

Run after src.build: python -m src.build_demo
Only allowlisted analysis fields are published; source events and raw metrics
are excluded. Uses the same HTML controls and percentiles as the local viewer.
"""
import hashlib
import json
import re

from .download import ROOT
from .metrics import MAX_SLOTS, score


def select_fields(rows, names):
    return [{name: row[name] for name in names} for row in rows]


def public_analysis(source):
    ranking_fields = ['candidate_id', 'profile_id', 'player_id', 'player', 'teams',
                      'minutes', 'role_share', 'score_base', 'rank_base']
    for slot in range(1, MAX_SLOTS + 1):
        ranking_fields += [f'{prefix}_{slot}' for prefix in ['metric', 'percentile', 'weight']]
    return {
        'public_demo': True,
        'max_slots': MAX_SLOTS,
        'audit': {k: source['audit'][k] for k in ['matches', 'teams', 'players', 'source_commit']},
        'profiles': select_fields(source['profiles'], ['profile_id', 'profile', 'cohort_size',
                                                       'minimum_minutes', 'minimum_role_share']),
        'rankings': select_fields(source['rankings'], ranking_fields),
        'ranking_detail': select_fields(source['ranking_detail'],
                                       ['candidate_id', 'slot', 'metric_id', 'percentile']),
        'metrics': select_fields(source['metrics'], ['metric_id', 'label', 'direction', 'definition']),
        'sensitivity': select_fields(source['sensitivity'],
                                     ['profile_id', 'player_id', 'best_rank', 'worst_rank']),
        'organizer_comparison': select_fields(source['organizer_comparison'],
                                              ['candidate_id', 'rank_v1', 'rank_creation_40', 'rank_v2']),
    }


def check_baseline(data):
    checked = 0
    for profile in data['profiles']:
        rows = [r for r in data['rankings'] if r['profile_id'] == profile['profile_id']]
        if len(rows) != profile['cohort_size']:
            raise ValueError('Candidate count does not match the reference cohort')
        scores = []
        for row in rows:
            result = score({str(i): row[f'percentile_{i}'] for i in range(1, MAX_SLOTS + 1)},
                           {str(i): row[f'weight_{i}'] for i in range(1, MAX_SLOTS + 1)})
            if result is None or abs(result - row['score_base']) > 1e-7:
                raise ValueError('Published score differs from local reference')
            scores.append(result)
        distinct = sorted(set(scores), reverse=True)
        for row, result in zip(rows, scores):
            if distinct.index(result) + 1 != row['rank_base']:
                raise ValueError('Published rank differs from local reference')
            checked += 1
    return checked


def main():
    source_html = (ROOT / 'outputs/revisar_rankings.html').read_text(encoding='utf-8')
    match = re.search(r'<script id="data" type="application/json">(.*?)</script>', source_html, re.S)
    if not match:
        raise ValueError('Build the local report first: python -m src.build')
    data = public_analysis(json.loads(match.group(1)))
    checked = check_baseline(data)
    template = (ROOT / 'src/review.html').read_text(encoding='utf-8')
    html = template.replace('__MINIMUM__', str(data['profiles'][0]['minimum_minutes']))
    html = html.replace('__ROLE_PERCENT__', str(round(100 * data['profiles'][0]['minimum_role_share'])))
    html = html.replace('__LOGO__', 'assets/statsbomb-logo.png')
    encoded = json.dumps(data, ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    html = html.replace('__DATA__', encoded)
    output = ROOT / 'docs/index.html'
    output.write_text(html, encoding='utf-8')
    (ROOT / 'docs/.nojekyll').write_text('', encoding='utf-8')
    evidence = {
        'baseline_comparisons': checked, 'baseline_errors': 0,
        'profiles': len(data['profiles']),
        'distinct_players': len({r['player_id'] for r in data['rankings']}),
        'source_commit': data['audit']['source_commit'],
        'source_report_sha256': hashlib.sha256((ROOT / 'outputs/revisar_rankings.html').read_bytes()).hexdigest(),
        'published_html_sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
        'published_bytes': output.stat().st_size,
        'published_content': 'Derived percentiles, ranks, contributions, participation summaries and labels.',
        'excluded': ['events', 'lineups', 'match tables', 'raw metric values', 'SQLite', 'full CSV tables', 'PBIX'],
        'hosting': 'GitHub Pages from main /docs; calculations run in the visitor browser.',
    }
    (ROOT / 'docs/evidencias/demo.json').write_text(
        json.dumps(evidence, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'baseline_comparisons': checked, 'bytes': output.stat().st_size}))


if __name__ == '__main__':
    main()
