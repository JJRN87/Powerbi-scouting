"""Reproducible, resumable public StatsBomb download (Python standard library)."""
import argparse
import concurrent.futures
import gzip
import hashlib
import json
from pathlib import Path
import time
import urllib.request
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / 'data' / 'raw'
REPO = 'https://raw.githubusercontent.com/statsbomb/open-data'


def request(url):
    for attempt in range(5):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'LaLigaResearch/1.0'})
            with urllib.request.urlopen(req, timeout=90) as response:
                return response.read()
        except Exception:
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def read_json(path):
    if str(path).endswith('.gz'):
        with gzip.open(path, 'rt', encoding='utf-8') as f:
            return json.load(f)
    return json.loads(Path(path).read_text(encoding='utf-8'))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--workers', type=int, default=6)
    args = parser.parse_args()
    RAW.mkdir(parents=True, exist_ok=True)
    lock_path = ROOT / 'data' / 'source-lock.json'
    if lock_path.exists():
        lock = read_json(lock_path)
    else:
        commit = json.loads(request('https://api.github.com/repos/statsbomb/open-data/commits/master'))['sha']
        lock = {'provider': 'StatsBomb', 'repository': 'https://github.com/statsbomb/open-data',
                'commit': commit, 'competition_id': 11, 'season_id': 27,
                'created_utc': datetime.now(timezone.utc).isoformat()}
        lock_path.write_text(json.dumps(lock, indent=2), encoding='utf-8')
    base = f"{REPO}/{lock['commit']}"
    records = []

    def fetch(rel, compressed=True):
        dest = RAW / (rel + ('.gz' if compressed else ''))
        dest.parent.mkdir(parents=True, exist_ok=True)
        if dest.exists():
            payload = gzip.decompress(dest.read_bytes()) if compressed else dest.read_bytes()
            if rel.endswith('.json'):
                json.loads(payload)
        else:
            payload = request(f'{base}/{rel}')
            if rel.endswith('.json'):
                json.loads(payload)
            tmp = dest.with_suffix(dest.suffix + '.tmp')
            tmp.write_bytes(gzip.compress(payload, mtime=0) if compressed else payload)
            tmp.replace(dest)
        return {'path': dest.relative_to(ROOT).as_posix(), 'url': f'{base}/{rel}',
                'sha256': hashlib.sha256(payload).hexdigest(), 'bytes': len(payload)}

    for rel in ['data/competitions.json', 'data/matches/11/27.json']:
        records.append(fetch(rel))
    for rel in ['LICENSE.pdf', 'README.md']:
        records.append(fetch(rel, False))
    matches = read_json(RAW / 'data/matches/11/27.json.gz')
    ids = [m['match_id'] for m in matches]
    if len(ids) != len(set(ids)) or len(ids) != 380:
        raise ValueError(f'Expected 380 unique matches; found {len(ids)}')
    print(f"Source {lock['commit']}; {len(ids)} matches", flush=True)
    jobs = [f'data/{kind}/{mid}.json' for mid in ids for kind in ['events', 'lineups']]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(fetch, rel): rel for rel in jobs}
        for i, future in enumerate(concurrent.futures.as_completed(futures), 1):
            records.append(future.result())
            if i % 40 == 0 or i == len(jobs):
                print(f'{i}/{len(jobs)} event/lineup files ready', flush=True)
    manifest = {**lock, 'files': sorted(records, key=lambda r: r['path']),
                'downloaded_utc': datetime.now(timezone.utc).isoformat()}
    (RAW / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
    print('Download complete. Run python -m src.build', flush=True)


if __name__ == '__main__':
    main()
