# Report_month - November 2026

Student: Varshita K (CS24BT007)
Project: Early Detection of Satellite Degradation and Failure in LEO Megaconstellations
Actual work date: 14 November 2026. Initial milestone submission; this does not claim a month of prior activity.

## Things tried and completed
- Organised the project folder and preserved the original proposal.
- Reviewed official CelesTrak GP/OMM, GFZ Kp and Space-Track documentation.
- Implemented cached Starlink/OneWeb snapshot and Kp download attempts with provenance manifests and error logging.
- Implemented orbital-field validation, satellite/epoch deduplication and CSV feature extraction.
- Implemented two-body mean-element altitude/perigee/apogee proxies and period calculation.
- Added an exploratory distribution plot step for when real orbital data is available.
- Ran two automated tests covering circular-orbit calculations, six-digit catalogue numbers and invalid inputs: both passed.
- Created documentation covering formulas, limitations, historical-data requirements and the next milestone.
- Initialised a local Git repository.

## Attempts that did not succeed
- Starlink and OneWeb downloads: connection timeouts.
- GFZ Kp download: local TLS certificate verification failure.
- Alternative PowerShell downloads: host resolution failures.
- GitHub authentication check: saved CLI token is invalid; repository has not been uploaded.

## Results and current status
Real observations acquired: 0. No data-derived plot, trend or detection result is claimed.
The working deliverable is an initial acquisition/feature-processing implementation with analytical tests; live-data end-to-end validation remains pending.
No failure labels, degradation model, storm correction or warning-lead-time evaluation has been completed.

## Next steps
1. Download the GP and Kp JSON files using `data/DOWNLOAD_INSTRUCTIONS.md`, then rerun the pipeline.
2. Obtain a small historical Starlink cohort from Space-Track and independently sourced status labels.
3. Inspect gaps/outliers and develop time-series trends before attempting anomaly detection.
4. Restore GitHub access and push this repository for the club submission.
