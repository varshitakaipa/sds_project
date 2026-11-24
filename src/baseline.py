"""Retrospective daily orbital-change screening, not failure prediction."""
import argparse
import csv
import hashlib
import json
import math
import statistics as st
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def fit(values, floor=0.02):
    """Robust centre/scale, with a configurable engineering noise floor."""
    if len(values)<10 or any(not math.isfinite(v) for v in values):
        raise ValueError('Need at least ten finite calibration values')
    centre=st.median(values)
    return dict(centre=centre, scale=max(st.median(abs(v-centre) for v in values)/0.6745,floor), n=len(values))


def score(value, model):
    return (value-model['centre'])/model['scale']


def daily_rows(records):
    grouped=defaultdict(list)
    for r in records:
        t=datetime.fromisoformat(r['epoch'])
        if t.tzinfo is None or t.utcoffset()!=timedelta(0):
            raise ValueError('Expected explicit UTC epochs')
        value=float(r['mean_altitude_proxy_km'])
        if not math.isfinite(value):
            raise ValueError('Nonfinite altitude')
        grouped[(int(r['norad_id']),t.date())].append((value,r))
    rows=[]
    for (ident,day),items in sorted(grouped.items()):
        kps=[float(r['kp']) for _,r in items if r.get('kp') not in ('',None)]
        rows.append(dict(norad_id=ident,day=day.isoformat(),n_observations=len(items),
                         altitude_km=st.median(v for v,_ in items),
                         kp_max_at_observations=max(kps) if kps else None))
    previous={}
    for r in rows:
        p=previous.get(r['norad_id'])
        # Exclude missing-day differences rather than bridging gaps.
        r['rate_km_day']=r['altitude_km']-p['altitude_km'] if p and (date.fromisoformat(r['day'])-date.fromisoformat(p['day'])).days==1 else None
        previous[r['norad_id']]=r
    byday=defaultdict(list)
    for r in rows:
        if r['rate_km_day'] is not None:
            byday[r['day']].append(r)
    for r in rows:
        peers=[p['rate_km_day'] for p in byday[r['day']] if p['norad_id']!=r['norad_id']]
        r['peer_count']=len(peers)
        r['peer_residual_km_day']=r['rate_km_day']-st.median(peers) if r['rate_km_day'] is not None and len(peers)>=5 else None
    return rows


def calibrate(rows, split, floor):
    buckets=defaultdict(list)
    for r in rows:
        if r['day']<split:
            for field in ('rate_km_day','peer_residual_km_day'):
                if r[field] is not None:
                    buckets[(r['norad_id'],field)].append(r[field])
    return {key:fit(values,floor) for key,values in buckets.items() if len(values)>=10}


def screen(rows, models, split, threshold=3.5, min_change=.1):
    result=[]
    for r in rows:
        if r['day']<split:
            continue
        q=dict(r)
        for field,label in (('rate_km_day','self'),('peer_residual_km_day','peer')):
            model=models.get((r['norad_id'],field))
            q[label+'_score']=score(r[field],model) if model and r[field] is not None else None
        q['eligible']=q['self_score'] is not None and q['peer_score'] is not None
        q['candidate']=bool(q['eligible'] and abs(q['self_score'])>threshold and abs(q['peer_score'])>threshold and abs(q['peer_residual_km_day'])>=min_change)
        result.append(q)
    return result


def csv_out(path,rows):
    if not rows:
        raise ValueError('No output records')
    with path.open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)


def run(input_path, output, split='2026-10-22', floor=.02):
    date.fromisoformat(split)
    if floor<=0 or not math.isfinite(floor):
        raise ValueError('Scale floor must be finite and positive')
    with input_path.open(newline='',encoding='utf-8') as f:
        rows=daily_rows(list(csv.DictReader(f)))
    models=calibrate(rows,split,floor)
    held=screen(rows,models,split)
    eligible=[r for r in held if r['eligible']]
    if not eligible:
        raise ValueError('No eligible held-out satellite-days; inspect dates and calibration coverage')
    output.mkdir(parents=True,exist_ok=True)
    csv_out(output/'daily_features.csv',rows)
    csv_out(output/'screened_days.csv',held)
    candidates=[r for r in held if r['candidate']]
    # Always write a header, even when there are no candidates.
    with (output/'candidate_days.csv').open('w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=list(held[0]));w.writeheader();w.writerows(candidates)
    sensitivity=[]
    for threshold in (3.5,5.,7.):
        for minimum in (.05,.1,.2):
            test=screen(rows,models,split,threshold,minimum)
            n=sum(r['candidate'] for r in test)
            sensitivity.append(dict(score_threshold=threshold,min_peer_change_km_day=minimum,
                                    eligible_satellite_days=len(eligible),candidate_days=n,
                                    candidates_per_100_satellite_days=100*n/len(eligible)))
    csv_out(output/'threshold_sensitivity.csv',sensitivity)
    serial_models=[dict(norad_id=k[0],feature=k[1],**v) for k,v in sorted(models.items())]
    (output/'calibration.json').write_text(json.dumps(serial_models,indent=2))
    summary=dict(work_date='2026-11-24',calibration_end_exclusive=split,
        heldout_start=split,first_day=min(r['day'] for r in rows),last_day=max(r['day'] for r in rows),
        satellites=len({r['norad_id'] for r in rows}),daily_observations=len(rows),
        calibration_satellite_days=sum(r['day']<split for r in rows),heldout_satellite_days=len(held),
        eligible_heldout_satellite_days=len(eligible),ineligible_heldout_satellite_days=len(held)-len(eligible),
        calibration_models=len(models),candidate_days=len(candidates),
        candidate_satellites=len({r['norad_id'] for r in candidates}),
        candidate_days_per_100_eligible_satellite_days=100*len(candidates)/len(eligible),
        scale_floor_km_day=floor,score_threshold=3.5,min_peer_change_km_day=.1,
        no_labels='Candidate burden only: no precision, recall, false-alarm rate or failure lead time can be measured.')
    (output/'summary.json').write_text(json.dumps(summary,indent=2))
    (output/'provenance.json').write_text(json.dumps(dict(input_file=input_path.name,
        input_sha256=hashlib.sha256(input_path.read_bytes()).hexdigest(),
        analyzed_utc=datetime.now(timezone.utc).isoformat(),
        parameters=dict(split=split,floor=floor,min_training_points=10,min_peers=5),
        approach='Frozen robust calibration; retrospective same-day peer comparison; no new raw data downloaded'),indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(2,1,figsize=(11,7),layout='constrained')
    ids=sorted({r['norad_id'] for r in held})
    for r in eligible:
        axes[0].scatter(date.fromisoformat(r['day']),ids.index(r['norad_id']),
            c='#bd4237' if r['candidate'] else '#c4d8df',s=30 if r['candidate'] else 10)
    axes[0].set(yticks=range(len(ids)),yticklabels=ids,ylabel='NORAD ID',title='Held-out daily screening: red = candidate, pale = eligible unflagged')
    main=[r for r in sensitivity if r['min_peer_change_km_day']==.1]
    axes[1].bar([str(r['score_threshold']) for r in main],[r['candidate_days'] for r in main],color='#176b93')
    axes[1].set(xlabel='Robust score threshold (both self and peer)',ylabel='Candidate satellite-days',title='Threshold sensitivity; minimum peer residual = 0.1 km/day')
    fig.savefig(output/'baseline_overview.png',dpi=160);plt.close(fig)
    (output/'interpretation.txt').write_text('Retrospective candidate screening only. Calibration fits use days strictly before the split; models stay frozen during evaluation. Daily medians and same-day peer medians are available only after those days, and element CREATION_DATE availability is not modelled. This is not an operational early-warning experiment. Candidates are unusual daily altitude-proxy changes; manoeuvres, deployment and element-fit noise remain plausible. Same-launch peers are not guaranteed healthy. Weather maxima cover observed epochs only and are context, not storm correction. Rates skip missing days. The scale floor and minimum-change gate are unvalidated engineering settings. Threshold sensitivity is descriptive, not performance optimisation. No ground-truth health labels or prediction metrics exist. Outputs remain local under results/orbital_local/.')
    print(json.dumps(summary,indent=2))
    return summary


if __name__=='__main__':
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,default=ROOT/'results/orbital_local/orbit_weather_features.csv')
    p.add_argument('--output',type=Path,default=ROOT/'results/orbital_local/milestone2')
    p.add_argument('--split',default='2026-10-22')
    p.add_argument('--scale-floor',type=float,default=.02)
    a=p.parse_args();run(a.input,a.output,a.split,a.scale_floor)
