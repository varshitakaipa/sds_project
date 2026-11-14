"""Offline GFZ Kp validation and exploratory space-weather analysis."""
import argparse
import csv
import hashlib
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def validate(data):
    times, values, statuses = data['datetime'], data['Kp'], data['status']
    if not times or not len(times) == len(values) == len(statuses):
        raise ValueError('Expected nonempty, equally sized datetime, Kp and status arrays')
    rows = []
    seen = set()
    for stamp, value, status in zip(times, values, statuses):
        time = datetime.fromisoformat(stamp.replace('Z', '+00:00'))
        if time.utcoffset() != timedelta(0) or time.minute or time.second or time.microsecond or time.hour % 3:
            raise ValueError('Timestamps must start three-hour UTC bins')
        if time in seen:
            raise ValueError('Duplicate timestamp')
        if isinstance(value, bool) or not isinstance(value, (float, int)) or not math.isfinite(value) or not 0 <= value <= 9:
            raise ValueError('Kp must be a finite number in [0,9]')
        if status not in ('def', 'pre', 'now'):
            raise ValueError('Unrecognised GFZ status: ' + str(status))
        seen.add(time)
        rows.append({'time': time, 'kp': value, 'status': status})
    return sorted(rows, key=lambda r: r['time'])


def events(rows):
    result = []
    for row in rows:
        if row['kp'] < 5:
            continue
        if not result or row['time'] != result[-1]['end']:
            result.append({'start': row['time'], 'end': row['time'], 'peak_kp': row['kp'], 'bins': 0})
        event = result[-1]
        event['end'] = row['time'] + timedelta(hours=3)
        event['peak_kp'] = max(event['peak_kp'], row['kp'])
        event['bins'] += 1
    return result


def write_csv(path, fields, rows):
    with path.open('w', newline='', encoding='utf-8') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def run(path):
    payload = path.read_bytes()
    data = json.loads(payload)
    rows = validate(data)
    out = ROOT/'results/space_weather'
    out.mkdir(parents=True, exist_ok=True)
    expected = int((rows[-1]['time']-rows[0]['time']).total_seconds()/10800)+1
    summary = dict(observations=len(rows), expected_bins_within_observed_span=expected,
                   missing_bins=expected-len(rows), start_utc=rows[0]['time'].isoformat(),
                   end_exclusive_utc=(rows[-1]['time']+timedelta(hours=3)).isoformat(),
                   minimum_kp=min(r['kp'] for r in rows), maximum_kp=max(r['kp'] for r in rows),
                   status_counts=dict(Counter(r['status'] for r in rows)),
                   storm_threshold_kp=5, storm_bins=sum(r['kp']>=5 for r in rows),
                   contiguous_storm_intervals=len(events(rows)))
    summary['storm_bin_fraction'] = summary['storm_bins']/len(rows)
    provenance = dict(source='GFZ Potsdam', source_page='https://kp.gfz.de/en/data',
                      file=path.name, sha256=hashlib.sha256(payload).hexdigest(),
                      bytes=len(payload), retrieval_method='Manual browser download by user',
                      retrieval_utc=None, retrieval_note='Exact retrieval time not recorded; analysis time is not retrieval time.',
                      analyzed_utc=datetime.now(timezone.utc).isoformat(), provider_metadata=data.get('meta'))
    (out/'summary.json').write_text(json.dumps(summary, indent=2))
    (out/'provenance.json').write_text(json.dumps(provenance, indent=2))
    write_csv(out/'kp_clean.csv', ['start_utc','end_utc','kp','status','storm_context'],
              [dict(start_utc=r['time'].isoformat(),end_utc=(r['time']+timedelta(hours=3)).isoformat(),
                    kp=r['kp'],status=r['status'],storm_context=int(r['kp']>=5)) for r in rows])
    daily = defaultdict(list)
    for r in rows:
        daily[r['time'].date()].append(r)
    write_csv(out/'daily_summary.csv', ['date_utc','bins','complete_day','maximum_kp','storm_bins'],
              [dict(date_utc=d.isoformat(),bins=len(rs),complete_day=int(len(rs)==8),
                    maximum_kp=max(r['kp'] for r in rs),storm_bins=sum(r['kp']>=5 for r in rs)) for d,rs in sorted(daily.items())])
    write_csv(out/'storm_intervals.csv', ['start_utc','end_exclusive_utc','bins','duration_hours','peak_kp'],
              [dict(start_utc=e['start'].isoformat(),end_exclusive_utc=e['end'].isoformat(),bins=e['bins'],
                    duration_hours=e['bins']*3,peak_kp=e['peak_kp']) for e in events(rows)])
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig, axes = plt.subplots(2, 1, figsize=(11,7), layout='constrained')
    for r in rows:
        axes[0].plot([r['time'], r['time']+timedelta(hours=3)], [r['kp']]*2,
                     color='#c45b27' if r['status']!='def' else '#176b93', linewidth=1.4)
    axes[0].axhline(5,color='#b33232',linestyle='--',label='Kp >= 5 context threshold')
    axes[0].set(title='GFZ three-hour Kp: 1 October - 13 November 2026',ylabel='Kp',ylim=(0,9))
    axes[0].legend(loc='upper left'); axes[0].grid(alpha=.2)
    axes[0].text(.01,-.23,'Blue: definitive | Orange: provisional/nowcast | Times: UTC',transform=axes[0].transAxes,fontsize=9)
    axes[1].hist([r['kp'] for r in rows],bins=[x-.1667 for x in range(11)],color='#176b93',edgecolor='white')
    axes[1].axvline(5,color='#b33232',linestyle='--')
    axes[1].set(xlabel='Kp',ylabel='Three-hour bins',title='Observed geomagnetic activity distribution',xlim=(-.2,9.4))
    fig.savefig(out/'kp_overview.png',dpi=160)
    plt.close(fig)
    (out/'findings.md').write_text(f'''# Initial space-weather findings

Validated {len(rows)} three-hour observations covering {summary['start_utc']} to {summary['end_exclusive_utc']} (exclusive). Missing bins within this span: {summary['missing_bins']}.

Maximum Kp: {summary['maximum_kp']}. Bins with Kp >= 5: {summary['storm_bins']} ({summary['storm_bin_fraction']:.1%}); contiguous above-threshold intervals: {summary['contiguous_storm_intervals']}. Status counts: {summary['status_counts']}.

Kp >= 5 is used as an exploratory geomagnetic-storm context flag, informed by NOAA's G1 threshold: https://www.spaceweather.gov/noaa-scales-explanation . These contiguous intervals are algorithmic groups, not independently validated storm events. A dip below threshold or a missing bin splits an interval. Boundary intervals may continue outside the downloaded window.

Source: GFZ Potsdam, https://kp.gfz.de/en/data ; provider metadata reports CC BY 4.0. Preserve attribution. Provisional values can change. Retrieval time was not recorded; file hash and analysis time are in provenance.json.

This is environmental context for future orbit analysis. Kp is a quasi-logarithmic planetary index, not a direct density or satellite-health measurement. No satellite failures, drag changes or predictive performance can be inferred from this dataset alone.
''',encoding='utf-8')
    print(json.dumps(summary,indent=2))
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=Path, default=ROOT/'data/raw/kp_2026-11-14.json')
    run(parser.parse_args().input)
