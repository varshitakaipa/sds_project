# Early Detection of Satellite Degradation in LEO

Project repository: https://github.com/varshitakaipa/sds_project (public).
Monthly progress: [Report_month.md](Report_month.md). Methods and work log: [documentations.md](documentations.md).

![Initial GFZ Kp analysis](results/space_weather/kp_overview.png)

First milestone for Varshita K (CS24BT007), Space and Data Science Club.
Scope: reproducible public-data acquisition, quality checks and exploratory orbital features.
This is an initial data pipeline, not a validated degradation detector.

## Completed offline Kp analysis

Run `python -m pip install -r requirements.txt`, then `python src/analyze_kp.py` and `python -m unittest discover -s tests -v`.
See `results/space_weather/findings.md` and `kp_overview.png`. This analyses environmental context only. Historical orbital data has now been acquired; see the local analysis below.

## Run on Windows
```powershell
py -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements.txt
.\.venv\Scripts\python src/pipeline.py --fetch
.\.venv\Scripts\python -m unittest discover -s tests -v
```
Run without `--fetch` to analyse existing JSON downloads offline. Internet is required for acquisition.
Keep each dated snapshot to begin accumulating history. Do not repeatedly query the provider.

## Files
- `Satellite_Degradation_Project_Proposal.pdf`: original proposal.
- `documentations.md`: methods, provenance, limitations and next steps.
- `Report_month.md`: actual completed work and pending tasks.
- `src/pipeline.py`: downloader, validation, feature extraction and plot.
- `data/raw/`: local original downloads, excluded from Git pending redistribution review.
- `data/manifest.json`: local retrieval timestamps, URLs and SHA256 hashes.
- `results/`: derived CSV, summary and figure.
- `tests/`: analytical checks using explicitly synthetic test inputs.

No private credentials are needed for the current-snapshot pipeline. Historical Space-Track access needs a user account; never commit passwords or tokens.

## Local historical-orbit analysis
Run `python src/analyze_history.py`. Outputs are in `results/orbital_local/`, excluded from Git pending source-sharing review. See Report_month.md and documentations.md for this updated milestone. Raw downloads stay in data/raw. No additional network requests are needed.
