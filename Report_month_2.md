# Second progress report - Milestone 2

Student: Varshita K (CS24BT007)
Project: Early Detection of Satellite Degradation and Failure in LEO Megaconstellations
Work date: 24 November 2026. This is the second progress checkpoint, using the existing October-November dataset; it does not represent a second elapsed calendar month or newly collected orbital data.

## Main work completed
- Added daily median altitude-proxy features and daily change rates, excluding differences across missing days.
- Implemented a robust statistical screening baseline comparing each satellite with its earlier behaviour and same-day peers.
- Used an earlier calibration period and a later held-out period; kept calibration parameters frozen during screening.
- Compared screening thresholds and generated candidate-review tables and a plot to examine review burden.
- Added a reproducible synthetic demo and five new tests for gap handling, peer comparison, calibration separation and invalid inputs; all twelve project tests pass.

## Initial results
Calibration uses dates before 22 October 2026; held-out dates run from 22 October through 13 November. There are 422 eligible held-out satellite-days and 19 ineligible satellite-days. The default exploratory settings produce 10 candidate days across 7 satellites (2.37 candidates per 100 eligible satellite-days). Increasing both score thresholds from 3.5 to 5 and 7 reduces the count to 5 and 4 respectively, keeping the minimum peer residual at 0.1 km/day.

In deliberately simple synthetic checks, stable data and a shared step produce zero candidate days; an isolated one-day excursion produces two (drop and recovery), while isolated sustained drift produces nineteen. These checks test expected software behaviour, not real-world satellite-failure detection performance.

## Limitations and next work
Candidates mean unusual daily orbital changes, not confirmed degradation, failures or manoeuvres. No health labels exist, so precision, recall, false-alarm rate and warning lead time cannot be measured. Same-day peer data and daily medians make this a retrospective experiment; actual element publication times and weather availability are not modelled. The noise floor and thresholds are unvalidated engineering settings. The cohort remains small and from one launch.

Next: review candidates against independent operational records; separate deployment/manoeuvre behaviour; test broader cohorts and gap/threshold settings; add propagation and density context before interpreting physical causes. No survival or failure-prediction model is claimed.

## Evidence
- `src/baseline.py`: daily features, frozen robust reference models, screening and sensitivity analysis.
- `src/demo_baseline.py`: deterministic synthetic scenarios requiring no raw downloads.
- `tests/test_baseline.py`: five new tests.
- `results/synthetic_baseline/`: clearly labelled synthetic outputs suitable for reproducing the software checks.
- `results/orbital_local/milestone2/`: local real-data scores, candidates, calibration parameters, provenance, sensitivity table and plot; excluded from Git.

Statistical reference: NIST, Detection of Outliers, https://itl.nist.gov/div898/handbook/eda/section3/eda35h.htm . The baseline adapts the median/MAD score with a scale floor and an absolute-change gate; NIST's general threshold is not satellite-specific validation.
