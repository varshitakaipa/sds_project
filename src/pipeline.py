"""Download genuine GP snapshots and derive exploratory mean-element features."""
import argparse, csv, hashlib, json, math, statistics
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
MU = 398600.4418  # km^3/s^2
EARTH_RADIUS = 6378.137  # equatorial radius, km

def download(url, target):
    if target.exists():
        return target.read_bytes()
    with urlopen(Request(url, headers={'User-Agent': 'sds-project-research/0.1'}), timeout=90) as response:
        payload = response.read()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes(payload)
    return payload

def features(row):
    n, e = float(row['MEAN_MOTION']), float(row['ECCENTRICITY'])
    inc = float(row['INCLINATION'])
    if not all(math.isfinite(x) for x in (n, e, inc)) or n <= 0 or not 0 <= e < 1 or not 0 <= inc <= 180:
        raise ValueError('Invalid orbital elements')
    epoch = datetime.fromisoformat(row['EPOCH'].replace('Z', '+00:00'))
    a = (MU / (n * 2 * math.pi / 86400)**2)**(1/3)
    return dict(norad_id=int(row['NORAD_CAT_ID']), name=row['OBJECT_NAME'], epoch=epoch.isoformat(),
                mean_motion_rev_day=n, inclination_deg=inc, eccentricity=e,
                semi_major_axis_km=a, mean_altitude_proxy_km=a-EARTH_RADIUS,
                perigee_proxy_km=a*(1-e)-EARTH_RADIUS, apogee_proxy_km=a*(1+e)-EARTH_RADIUS,
                period_minutes=1440/n)

def run(fetch=False):
    day = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    manifest_path = ROOT/'data/manifest.json'
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else []
    failures = []
    if fetch:
        urls = {f'{g}_{day}.json': f'https://celestrak.org/NORAD/elements/gp.php?GROUP={g}&FORMAT=JSON' for g in ('starlink', 'oneweb')}
        urls[f'kp_{day}.json'] = 'https://kp.gfz.de/app/json/?start=2026-10-01T00:00:00Z&end=2026-11-13T23:59:59Z&index=Kp'
        for filename, url in urls.items():
            target = ROOT/'data/raw'/filename
            try:
                payload = download(url, target)
                parsed = json.loads(payload)
                if not parsed or (filename.startswith('kp_') and not parsed.get('datetime')):
                    raise ValueError('Empty or unexpected response')
                if not any(m['file'] == filename for m in manifest):
                    manifest.append(dict(file=filename, url=url, retrieved_utc=datetime.now(timezone.utc).isoformat(), sha256=hashlib.sha256(payload).hexdigest(), bytes=len(payload)))
            except Exception as exc:
                failures.append(dict(url=url, error=str(exc)))
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, indent=2))
        (ROOT/'data/download_errors.json').write_text(json.dumps(failures, indent=2))
    rows, rejected, seen = [], [], set()
    for path in sorted((ROOT/'data/raw').glob('*.json')):
        if path.name.startswith('kp_'):
            continue
        for row in json.loads(path.read_text()):
            try:
                f = features(row)
                key = (f['norad_id'], f['epoch'])
                if key in seen:
                    continue
                seen.add(key)
                f['constellation'] = path.name.split('_')[0]
                rows.append(f)
            except (KeyError, ValueError, TypeError, OverflowError) as exc:
                rejected.append(dict(source=path.name, error=str(exc)))
    out = ROOT/'results'
    out.mkdir(exist_ok=True)
    if rows:
        with (out/'orbital_features.csv').open('w', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
            writer.writeheader(); writer.writerows(rows)
    summary = {'observations': len(rows), 'satellites': len({r['norad_id'] for r in rows}), 'rejected': len(rejected), 'groups': {}, 'limitations': 'Snapshot EDA only. Mean-element altitude proxies are not SGP4 positions or failure labels.'}
    for group in sorted({r['constellation'] for r in rows}):
        values = [r['mean_altitude_proxy_km'] for r in rows if r['constellation']==group]
        summary['groups'][group] = dict(observations=len(values), minimum_altitude_proxy_km=min(values), median_altitude_proxy_km=statistics.median(values), maximum_altitude_proxy_km=max(values))
    (out/'summary.json').write_text(json.dumps(summary, indent=2))
    (out/'rejected.json').write_text(json.dumps(rejected, indent=2))
    if rows:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt
        fig, ax = plt.subplots(figsize=(9,5))
        for group in summary['groups']:
            ax.hist([r['mean_altitude_proxy_km'] for r in rows if r['constellation']==group], bins=50, alpha=.6, label=group)
        ax.set(xlabel='Mean-element altitude proxy (km)', ylabel='Observation count', title='Initial orbital snapshot: exploratory distribution')
        ax.legend(); fig.tight_layout(); fig.savefig(out/'altitude_distribution.png', dpi=160); plt.close(fig)
    print(json.dumps({'summary': summary, 'download_errors': failures}, indent=2))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--fetch', action='store_true', help='Download one cached snapshot per group per UTC day')
    run(parser.parse_args().fetch)
