# Report_month - November 2026

Student: Varshita K (CS24BT007)
Project: Early Detection of Satellite Degradation and Failure in LEO Megaconstellations
Actual work date: 14 November 2026. This submission records work completed for the monthly check; it does not claim a month of earlier work.

## Follow-up checkpoint - 24 November 2026

Completed a retrospective daily-change screening baseline, earlier/later split, peer comparison and synthetic checks. See [Report_month_2.md](Report_month_2.md) for the second progress checkpoint. The initial report below retains its original scope and date.

## Things tried and completed
- Collected historical Starlink orbital data, satellite catalogue records and space-weather data from Space-Track, GCAT, GFZ and NASA OMNI.
- Built a preprocessing pipeline to check orbital records, resolve duplicate epochs and identify gaps in each satellite's history.
- Calculated approximate orbital features, including altitude, perigee, apogee and altitude-change rates.
- Aligned orbital observations with available geomagnetic and solar indices to prepare for investigating space-weather effects.
- Produced initial orbital-history and space-weather plots, and documented the methods, findings and limitations in the project repository.

## Measured first-sample results (local)
- Downloaded 1,688 orbital records for 20 Starlink satellites from one launch.
- Resolved 58 duplicate satellite/epoch records, retaining 1,630 observations; no rejected input records.
- Matched all 20 satellite IDs to GCAT.
- Matched all 1,630 orbital epochs to Kp and GFZ context; 1,174 had available Dst.
- Calculated 1,609 finite-difference rates; one inter-observation gap exceeded 48 hours.
- GFZ coverage: 44 days, October 1 through November 13. Kp has 352 bins with no missing bins; 104 are provisional.
- NASA Dst has 696 hourly records through October 29; later dates remain unavailable.

## Interpretation and limits
The cohort is a convenience sample selected from one July 2026 launch, not a representative health/failure sample. Initial orbit-raising and other changes are visible in altitude proxies, but their operational causes are unverified. No change is labelled as degradation or failure. Plotted weather overlap is not evidence of causation.

No validated manoeuvre detector, density model, ballistic coefficient, anomaly detector, survival model or early-warning evaluation has been completed. Mean-element proxies are not precise propagated positions. Concurrent weather joins are retrospective and need availability-aware lagging for prediction.

## Evidence and next steps
Code: src/analyze_history.py. Local outputs: results/orbital_local/ (features, coverage, summary, provenance, findings and orbit_weather_overview.png). Weather-only outputs remain in results/space_weather/.

Next: review source permissions; expand the cohort with an explicit selection method and independently corroborated status labels; inspect element-fit noise and manoeuvres; add SGP4 propagation and density modelling; evaluate any baseline with temporal splits and false-alarm/lead-time metrics.

The code, documentation and monthly progress summary are published in the dedicated project repository. Raw downloads and detailed Space-Track-derived files in results/orbital_local/ remain excluded from Git pending source-sharing review. No other repository was accessed or changed.
