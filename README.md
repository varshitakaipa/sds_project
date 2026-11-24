# Satellite Degradation Study

Investigating whether public orbital histories can provide early warning of satellite degradation in LEO megaconstellations.

**Author:** Varshita K (CS24BT007), Space and Data Science Club.

**Status:** Initial data-processing and exploratory-analysis milestone. A degradation detector has not yet been validated.

## Project documents
- [Problem statement](problem_statement.md) (PS document): motivation, research question and scope.
- [Pipeline](pipeline.md): inputs, scripts, processing steps and limitations.
- [Initial progress](Report_month.md) and [Milestone 2](Report_month_2.md): completed work and next steps.
- [Detailed documentation](documentations.md): methods, provenance and work log.
- [Original proposal](Satellite_Degradation_Project_Proposal.pdf).

## Implemented so far
- Orbital-data validation, duplicate resolution, approximate feature calculation and coverage summaries.
- GFZ Kp analysis and alignment of historical orbital epochs with available space-weather observations.
- Catalogue matching, exploratory plots and reproducibility records.
- Twelve automated tests covering core validation and calculations.

![Initial GFZ Kp analysis](results/space_weather/kp_overview.png)

## Setup
Use Python 3.10 or newer. From the project folder on Windows:
```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python -m unittest discover -s tests -v
```

## Run the analyses
Acquire the local inputs listed in [pipeline.md](pipeline.md), then run:
```powershell
.\.venv\Scripts\python src/analyze_kp.py
.\.venv\Scripts\python src/analyze_history.py
```
A fresh clone contains code and selected outputs, but no raw datasets. Tests run without the datasets. The current scripts use fixed input filenames and an October-November 2026 analysis window, documented in pipeline.md.

Optional current-snapshot acquisition:
```powershell
.\.venv\Scripts\python src/pipeline.py --fetch
```
This requires internet access and may fail if providers are unavailable. It does not replace historical orbital data. Historical analysis runs offline after manual downloads; never commit account credentials.

## Repository structure
```text
src/                    Acquisition and analysis scripts
 tests/                 Automated checks using synthetic fixtures
 data/raw/              Local original downloads (ignored by Git)
 results/space_weather/ Published initial GFZ analysis
 results/orbital_local/ Local detailed orbital analysis (ignored by Git)
```

## Limits and next steps
The initial historical sample is a convenience cohort from one launch. Orbital features are approximate mean-element proxies, not precise propagated positions. No orbital change is labelled as a failure, and weather overlap does not establish causation. Next steps are independently corroborated labels, manoeuvre investigation, SGP4 propagation, density modelling and temporal evaluation.

## Sources and data access
See [pipeline.md](pipeline.md) for official source links and exact input requirements. Raw downloads and detailed Space-Track-derived outputs remain local pending source-sharing review. GFZ and GCAT attribution is recorded in the documentation and provenance files.

Project repository: https://github.com/varshitakaipa/sds_project

## Milestone 2: retrospective screening baseline
The new baseline compares daily orbital changes with earlier self-history and same-day peers. Earlier dates calibrate robust median/MAD references; later dates are screened with frozen parameters. Outputs are candidate review signals, not satellite-health classifications.

No real data is needed to run the synthetic checks:
```powershell
.\.venv\Scripts\python src/demo_baseline.py
.\.venv\Scripts\python -m unittest discover -s tests -v
```
For the local real-data experiment, first run the history pipeline, then:
```powershell
.\.venv\Scripts\python src/baseline.py
```
Real-data outputs remain in `results/orbital_local/milestone2/`. Clearly labelled artificial outputs are in `results/synthetic_baseline/`. See [Report_month_2.md](Report_month_2.md) for findings and limitations. Five new tests check constant references, gap exclusion, peer behaviour, future-data separation and invalid calibration input.
