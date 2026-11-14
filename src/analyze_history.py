"""Local-only exploratory GP history analysis; no health classification."""
import csv
import hashlib
import json
import statistics
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from pipeline import features
from analyze_kp import validate, write_csv

ROOT = Path(__file__).resolve().parents[1]
START = datetime(2026, 10, 1, tzinfo=timezone.utc)
END = datetime(2026, 11, 14, tzinfo=timezone.utc)


def utc(value):
    t = datetime.fromisoformat(value.replace('Z', '+00:00'))
    return t.replace(tzinfo=timezone.utc) if t.tzinfo is None else t.astimezone(timezone.utc)


def bin_start(t, hours):
    return t.replace(hour=t.hour//hours*hours, minute=0, second=0, microsecond=0)


def rate(previous, current, max_gap_hours=48):
    hours = (utc(current['epoch'])-utc(previous['epoch'])).total_seconds()/3600
    if not 0 < hours <= max_gap_hours:
        return None
    return (current['mean_altitude_proxy_km']-previous['mean_altitude_proxy_km'])/(hours/24)


def catalogs():
    result = {}
    for filename in ('gcat_satcat.tsv', 'gcat_satcat100k.tsv'):
        with (ROOT/'data/raw'/filename).open(encoding='utf-8') as stream:
            header = next(stream)
            for r in csv.DictReader([header]+[l for l in stream if not l.startswith('#')], delimiter='\t'):
                key = r['Satcat'].strip()
                if key.isdigit():
                    result[int(key)] = {k:v.strip() for k,v in r.items()}
    return result


def weather():
    raw = ROOT/'data/raw'
    kp_rows = validate(json.loads((raw/'kp_2026-11-14.json').read_text()))
    kp = {r['time']:r for r in kp_rows}
    gfz = {}
    for line in (raw/'gfz_indices_20261001_20261113.txt').read_text().splitlines():
        if not line.strip() or line.startswith('#'):
            continue
        c = line.split()
        if len(c)!=28:
            raise ValueError('Expected 28 GFZ combined-index columns')
        day = datetime(*map(int,c[:3]),tzinfo=timezone.utc)
        gfz[day.date()] = dict(ap=[float(x) for x in c[15:23]], daily_Ap=float(c[23]),
                              f107_observed=float(c[25]), f107_adjusted=float(c[26]), definitive=int(c[27]))
    dst = {}
    # Companion format file states YEAR, DOY, HOUR, B, DENSITY, DST.
    for line in (raw/'omni_dst_20261001_20261029.txt').read_text().splitlines():
        c = line.split()
        if not c:
            continue
        if len(c)!=6:
            raise ValueError('Expected six OMNI columns; inspect supplied format file')
        t = datetime(int(c[0]),1,1,tzinfo=timezone.utc)+timedelta(days=int(c[1])-1,hours=int(c[2]))
        if t in dst:
            raise ValueError('Duplicate OMNI timestamp')
        value = int(c[5])
        dst[t] = None if value==99999 else value
    return kp,gfz,dst


def run():
    raw = ROOT/'data/raw'
    out = ROOT/'results/orbital_local'
    out.mkdir(parents=True, exist_ok=True)
    inputs = json.loads((raw/'starlink_history.json').read_text())
    kp,gfz,dst = weather()
    catalog = catalogs()
    keyed, rejected, duplicates, excluded = {}, [], 0, 0
    for index,r in enumerate(inputs):
        try:
            if r.get('TIME_SYSTEM')!='UTC' or r.get('MEAN_ELEMENT_THEORY')!='SGP4':
                raise ValueError('Expected UTC SGP4 mean elements')
            f = features(r)
            t = utc(f['epoch'])
            if not START<=t<END:
                excluded+=1
                continue
            f['epoch']=t.isoformat()
            key = f['norad_id'],t
            # Keep the most recently created element set at a duplicate epoch.
            if key in keyed:
                duplicates+=1
                if r.get('CREATION_DATE','') <= keyed[key][1]:
                    continue
            keyed[key]=(f,r.get('CREATION_DATE',''))
        except (ValueError,KeyError,TypeError,OverflowError) as exc:
            rejected.append(dict(input_index=index,error=str(exc)))
    rows = sorted([v[0] for v in keyed.values()],key=lambda r:(r['norad_id'],r['epoch']))
    if not rows:
        raise ValueError('No valid orbital observations')
    groups=defaultdict(list)
    for r in rows:
        groups[r['norad_id']].append(r)
    coverage=[]
    for ident,rs in groups.items():
        gaps=[(utc(b['epoch'])-utc(a['epoch'])).total_seconds()/3600 for a,b in zip(rs,rs[1:])]
        gc=catalog.get(ident,{})
        coverage.append(dict(norad_id=ident,name=rs[0]['name'],observations=len(rs),
                             first_epoch=rs[0]['epoch'],last_epoch=rs[-1]['epoch'],
                             days_observed=len({utc(r['epoch']).date() for r in rs}),
                             median_gap_hours=statistics.median(gaps) if gaps else '',
                             maximum_gap_hours=max(gaps) if gaps else '',gaps_over_48h=sum(g>48 for g in gaps),
                             net_altitude_proxy_change_km=rs[-1]['mean_altitude_proxy_km']-rs[0]['mean_altitude_proxy_km'],
                             gcat_name=gc.get('Name',''),gcat_launch_date=gc.get('LDate',''),
                             gcat_status_raw=gc.get('Status','')))
        for i,r in enumerate(rs):
            t=utc(r['epoch']); k=kp.get(bin_start(t,3)); g=gfz.get(t.date()); d=dst.get(bin_start(t,1))
            r.update(kp=k['kp'] if k else None,kp_status=k['status'] if k else None,
                     storm_context=int(k['kp']>=5) if k else None,
                     ap=g['ap'][t.hour//3] if g else None,daily_Ap=g['daily_Ap'] if g else None,
                     f107_observed=g['f107_observed'] if g and g['f107_observed']>=0 else None,
                     gfz_definitive=g['definitive'] if g else None,dst_nt=d,
                     altitude_proxy_rate_km_day=rate(rs[i-1],r) if i else None)
    write_csv(out/'orbit_weather_features.csv',list(rows[0]),rows)
    write_csv(out/'satellite_coverage.csv',list(coverage[0]),coverage)
    summary=dict(input_records=len(inputs),retained_records=len(rows),satellites=len(groups),
                 rejected_records=len(rejected),duplicate_epochs=duplicates,outside_window=excluded,
                 window_start_utc=START.isoformat(),window_end_exclusive_utc=END.isoformat(),
                 catalog_matches=sum(bool(c['gcat_name']) for c in coverage),
                 kp_matched_records=sum(r['kp'] is not None for r in rows),
                 dst_matched_records=sum(r['dst_nt'] is not None for r in rows),
                 gfz_matched_records=sum(r['ap'] is not None for r in rows),
                 valid_rate_records=sum(r['altitude_proxy_rate_km_day'] is not None for r in rows),
                 gaps_over_48h=sum(c['gaps_over_48h'] for c in coverage),
                 dst_first_utc=min(dst).isoformat(),dst_last_utc=max(dst).isoformat(),
                 warning='Exploratory single-launch cohort, no health labels or causal conclusions')
    (out/'summary.json').write_text(json.dumps(summary,indent=2))
    (out/'rejected.json').write_text(json.dumps(rejected,indent=2))
    (out/'provenance.json').write_text(json.dumps(dict(analyzed_utc=datetime.now(timezone.utc).isoformat(),
        retrieval_utc=None,method='Manual downloads by user; exact retrieval times unknown',
        inputs=[dict(file=p.name,bytes=p.stat().st_size,sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for p in sorted(raw.iterdir()) if p.is_file()]),indent=2))
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    fig,axes=plt.subplots(3,1,figsize=(12,10),layout='constrained',sharex=True)
    for ident,rs in groups.items():
        axes[0].plot([utc(r['epoch']) for r in rs],[r['mean_altitude_proxy_km'] for r in rs],lw=.9,alpha=.7)
    axes[0].set(title=f'Exploratory mean-element orbit histories: {len(groups)} Starlink satellites',ylabel='Altitude proxy (km)')
    for r in kp.values():
        if r['kp']>=5:
            for ax in axes:
                ax.axvspan(r['time'],r['time']+timedelta(hours=3),color='#e6a23c',alpha=.16)
    axes[1].step(list(kp),[r['kp'] for r in kp.values()],where='post',color='#176b93')
    axes[1].axhline(5,ls='--',color='brown',lw=.8)
    axes[1].set(ylabel='Kp',title='Geomagnetic context; shading marks Kp >= 5')
    axes[2].plot(list(dst),[float('nan') if v is None else v for v in dst.values()],color='#6654a3',lw=.9)
    axes[2].set(ylabel='Dst (nT)',xlabel='UTC date',title='NASA OMNI Dst: later dates unavailable, not filled')
    for ax in axes:
        ax.grid(alpha=.2); ax.set_xlim(START,END)
    fig.savefig(out/'orbit_weather_overview.png',dpi=150); plt.close(fig)
    (out/'findings.md').write_text('''# Local exploratory orbital analysis

See summary.json and satellite_coverage.csv for measured counts and coverage. Histories are converted to approximate two-body mean-element altitude proxies, not SGP4 propagated positions. Finite-difference rates are only calculated for positive gaps of at most 48 hours; no interpolation is performed. Large changes can reflect deployment, manoeuvres, orbit-fit updates or noise, not degradation.

Kp/ap join: containing three-hour UTC bin. Daily F10.7/Ap join: UTC date. Dst join: containing UTC hour; missing coverage and the 99999 fill value remain missing. These concurrent weather joins are for retrospective EDA; daily weather and within-bin aggregates must not be treated as information available at the start of a predictive interval. GFZ definitive/provisional information is retained.

The sample comprises the first 20 Starlink entries selected from the downloaded extended GCAT catalogue, a convenience cohort from one launch. Catalogue status is retained as an uninterpreted raw field; it is not a failure label. No manoeuvre detector, density model, ballistic coefficient, anomaly model or early-warning result is claimed. Visual overlap with space weather does not establish causation.

Source documentation: Space-Track https://www.space-track.org/documentation ; GFZ https://kp.gfz.de/en/data ; NASA OMNI https://omniweb.gsfc.nasa.gov/form/dx1.html ; GCAT (J. McDowell) https://planet4589.org/space/gcat/ . Inputs and Space-Track-derived results remain local pending sharing-permission review.
''',encoding='utf-8')
    print(json.dumps(summary,indent=2))


if __name__=='__main__':
    run()
