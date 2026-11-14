# Report_month - November 2026

Student: Varshita K (CS24BT007)
Project: Early Detection of Satellite Degradation and Failure in LEO Megaconstellations
Actual work date: 14 November 2026. This submission records work completed for the monthly check; it does not claim a month of earlier work.

## Things tried and completed
- Set up the project, preserved the proposal and created the dedicated private GitHub repository.
- Reviewed official orbital-data and space-weather sources; documented CelesTrak connection failures.
- Acquired Space-Track GP history, both GCAT catalogues, GFZ Kp/ap/Ap/F10.7 and NASA OMNI Dst through manual downloads.
- Implemented orbital-field validation and deterministic duplicate-epoch resolution using the latest creation timestamp.
- Matched satellite identifiers to GCAT and produced per-satellite coverage and gap summaries.
- Calculated approximate mean-element altitude/perigee/apogee and finite-difference altitude-proxy rates with a 48-hour gap limit.
- Joined orbit epochs to three-hour UTC Kp/ap, daily solar indices and available hourly Dst; retained missing values and provisional flags.
- Generated orbital-history and space-weather overview plots, clean feature CSV and provenance hashes.
- Ran seven automated tests: all passed.

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

Space-Track-derived inputs, outputs and this updated analysis report have not been uploaded in this update while sharing permissions remain unresolved. Existing GitHub content reflects the earlier Kp milestone. No other repository was accessed or changed.
