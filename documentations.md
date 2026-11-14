# documentations

## Project and milestone
Research question: can public orbital histories reveal signs before operational degradation or failure?
Milestone 1 implements acquisition and exploratory analysis. All work in this initial submission was done on 14 November 2026; no earlier activity is claimed.

## Source review
- CelesTrak GP format documentation: https://celestrak.org/NORAD/documentation/gp-data-formats.php
  JSON uses OMM keywords and accommodates catalogue numbers above 99999. Current group snapshots do not supply historical trajectories.
- CelesTrak usage policy: https://celestrak.org/usage-policy.php
  Downloader caches per UTC day. Read provider terms before reuse or redistribution; raw data stays out of Git.
- GFZ Kp data and API: https://kp.gfz.de/en/data
  Attempted Kp interval: 1 October to 13 November 2026. Values may include provisional data. Raw JSON is retained; weather alignment is pending.
- Space-Track documentation: https://www.space-track.org/documentation
  `gp_history` is a historical-data route requiring an account and compliance with query limits.
- GCAT (candidate label source, not downloaded/validated): https://planet4589.org/space/gcat/

## Pipeline
1. Fetch Starlink and OneWeb GP JSON and GFZ Kp; log failures independently.
2. Keep original bytes plus retrieval UTC, URL, size and SHA256 in a manifest.
3. Require finite positive mean motion, eccentricity in [0,1), inclination in [0,180], parseable epoch and catalogue ID.
4. Deduplicate by catalogue ID and epoch; preserve different epochs.
5. Derive period and approximate mean-element altitude, perigee and apogee; export CSV, summary, rejection log and histogram.

## Physics and interpretation
For mean motion n in revolutions/day: angular frequency = 2*pi*n/86400 radians/s; a = (mu/angular_frequency^2)^(1/3), mu = 398600.4418 km^3/s^2. Altitude proxy = a - 6378.137 km. Perigee/apogee proxies = a*(1-/+e) - 6378.137 km. These are two-body conversions from SGP4 mean elements, not precise osculating altitudes. SGP4 propagation is future work.

## Quality and limitations
Tests check a circular reference orbit, six-digit catalogue IDs and invalid/nonfinite elements. Synthetic values in tests are software fixtures, never experimental observations.
Current snapshots are biased towards objects in the provider group and cannot establish failure, decay rate, manoeuvre frequency or warning lead time. Low altitude can reflect deployment or planned disposal. No labels, detector, ballistic coefficient, density model or survival result has been implemented. Kp has not yet been joined to orbit epochs. No healthy-versus-failed claim is made.

## Historical-data plan
Create a free Space-Track account at https://www.space-track.org/auth/createAccount and log in yourself. Select a small documented Starlink cohort and request 60-90 days of GP history in JSON. A query pattern after authentication is `/basicspacedata/query/class/gp_history/NORAD_CAT_ID/<comma-separated-IDs>/EPOCH/<start>--<end>/orderby/NORAD_CAT_ID,EPOCH/format/json` (replace placeholders and consult current docs). Keep raw exports locally and record retrieval provenance. An imported historical file can be placed in `data/raw/starlink_history.json` for the existing feature extractor; temporal analysis still needs implementation.

## Next milestone
1. Acquire historical cohort and independently sourced status-event labels; record uncertain labels and event intervals.
2. Quantify gaps, stale epochs and outliers; calculate per-satellite finite-difference altitude trends with gap limits.
3. Propagate with SGP4 and compare estimates; identify planned manoeuvre confounding.
4. Align three-hour UTC Kp bins, then add F10.7/density inputs before estimating drag.
5. Evaluate a baseline anomaly method with temporal splits, false alarms per satellite-day and event lead times. Treat healthy status as censored, not guaranteed negative.

## Reproducibility
Run commands in README. Outputs and actual counts are recorded in `results/summary.json` and `Report_month.md`. Python environment and test output are in `results/verification.txt`. Fetch timestamps may differ from the requested month and are never backdated.
