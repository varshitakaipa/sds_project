"""Reproducible synthetic stress checks; no real satellite data required."""
import json
import math
from datetime import date,timedelta
from pathlib import Path
from baseline import daily_rows,calibrate,screen,csv_out

ROOT=Path(__file__).resolve().parents[1]


def scenario(kind):
    records=[]
    for ident in range(7):
        for i in range(44):
            day=date(2026,10,1)+timedelta(days=i)
            altitude=500+ident*.01+.003*math.sin(i+ident)
            if kind=='shared_step' and i>=25:
                altitude+=1
            if kind=='isolated_excursion' and ident==0 and i==25:
                altitude-=1
            if kind=='isolated_drift' and ident==0 and i>=25:
                altitude-=.2*(i-24)
            records.append(dict(norad_id=str(ident),epoch=day.isoformat()+'T12:00:00+00:00',mean_altitude_proxy_km=str(altitude)))
    return daily_rows(records)


def run():
    out=ROOT/'results/synthetic_baseline'
    out.mkdir(parents=True,exist_ok=True)
    results=[]
    for kind in ('stable','shared_step','isolated_excursion','isolated_drift'):
        rows=scenario(kind)
        models=calibrate(rows,'2026-10-22',.02)
        scored=screen(rows,models,'2026-10-22')
        flags=[r for r in scored if r['candidate']]
        results.append(dict(scenario=kind,synthetic=True,eligible_days=sum(r['eligible'] for r in scored),
                            candidate_days=len(flags),candidate_satellites=len({r['norad_id'] for r in flags})))
        csv_out(out/(kind+'.csv'),scored)
    # Behavioural checks are specified before observing the real data.
    expected=[0,0,2,19]
    if [r['candidate_days'] for r in results]!=expected:
        raise AssertionError('Synthetic stress-check behaviour changed')
    (out/'summary.json').write_text(json.dumps(dict(synthetic_only=True,checks_passed=True,
        caveat='Artificial scenarios test software behaviour, not real failure-detection accuracy.',results=results),indent=2))
    (out/'README.md').write_text('''# Synthetic baseline checks

Generated entirely by src/demo_baseline.py; no Space-Track data is included. Seven fictional IDs, 44 days, deterministic low-amplitude sinusoidal altitude-proxy noise. Calibration uses days before October 22 and a 0.02 km/day scale floor. Scenarios add no change, a +1 km common step to all objects, a one-day -1 km excursion for ID 0, or sustained -0.2 km/day drift for ID 0. The excursion produces two changed daily rates (drop and recovery); the drift produces 19 changed rates. Expected counts are asserted in code.

These deliberately simple examples validate arithmetic and peer filtering. They do not establish robustness to real storms, manoeuvres, model errors or failure signatures. They provide no real-world precision, recall or lead-time evidence.
''',encoding='utf-8')
    print(json.dumps(results,indent=2))


if __name__=='__main__':run()
