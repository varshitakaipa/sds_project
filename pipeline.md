# Data and analysis pipeline

## Implemented workflow
```mermaid
flowchart TD
    A[Manual source downloads] --> B[Local raw files and input hashes]
    B --> C[Validate orbital fields and epochs]
    C --> D[Filter time window and resolve duplicate epochs]
    D --> E[Orbital features and coverage checks]
    B --> F[Validate weather and read catalogues]
    E --> G[Join catalogue IDs and UTC weather bins]
    F --> G
    G --> H[Local feature CSV, summaries and plots]
```

## Entry points
| Script | Purpose | Outputs |
|---|---|---|
| `src/pipeline.py` | Fetch cached current Starlink/OneWeb GP snapshots and Kp; extract approximate orbital features | `results/summary.json`, optional feature CSV and altitude histogram |
| `src/analyze_kp.py` | Validate and analyse the saved GFZ Kp JSON offline | `results/space_weather/` |
| `src/analyze_history.py` | Process saved GP histories, catalogue matches, coverage and weather joins offline | `results/orbital_local/` (ignored by Git) |

## Required local inputs
Place these in `data/raw/` using the current script filenames:
- `starlink_history.json`: Space-Track GP_HISTORY JSON.
- `gcat_satcat.tsv` and `gcat_satcat100k.tsv`: standard and extended GCAT catalogues.
- `kp_2026-11-14.json`: GFZ three-hour Kp JSON with datetime and status arrays.
- `gfz_indices_20261001_20261113.txt`: 28-column GFZ combined solar/geomagnetic indices.
- `omni_dst_20261001_20261029.txt`: six-column NASA OMNI export (year, day of year, hour, magnetic field, proton density, Dst).
- Retain the accompanying OMNI format file to document column meanings.

The historical script currently uses the fixed UTC interval [2026-10-01, 2026-11-14). Adapt its configuration and input filenames deliberately for a new interval. A fresh clone does not contain raw inputs and cannot run the data analyses until these are supplied. Automated tests use synthetic fixtures and need no downloads.

## Validation and transformations
- Require valid finite orbital elements, UTC time system and SGP4 mean-element theory.
- Keep the latest CREATION_DATE for repeated satellite-ID/epoch pairs.
- Derive period, semi-major axis and approximate altitude/perigee/apogee using two-body formulas; these are exploratory mean-element proxies.
- Sort each satellite history, summarise gaps and calculate finite-difference altitude rates only for positive intervals of at most 48 hours.
- Join catalogue records by NORAD ID; preserve status as an uninterpreted field.
- Validate Kp array lengths, values, statuses and unique three-hour UTC timestamps.
- Join Kp/ap by containing three-hour UTC bin, solar indices by UTC date and Dst by containing UTC hour. Dst fill value 99999 and missing coverage remain missing.
- Record original-file SHA256 hashes and analysis timestamps; unknown manual retrieval times remain unknown.

## Run and verify
```powershell
python src/analyze_kp.py
python src/analyze_history.py
python -m unittest discover -s tests -v
```
Run these after installing dependencies as described in README.md. Only `python src/pipeline.py --fetch` requests network data; it is optional and is not needed for the offline historical workflow.

## Interpretation and remaining work
The weather joins describe retrospective context. Predictive features will need availability-aware lags to prevent leakage. Large orbital changes may reflect manoeuvres, deployment or element-fit noise; they are not failure detections. Plotted overlap with weather does not establish causation. Next work includes independently corroborated labels, broader cohorts, SGP4 propagation, manoeuvre analysis, density modelling and temporal evaluation.

## Data sources and sharing
- [Space-Track documentation](https://www.space-track.org/documentation)
- [GCAT, Jonathan McDowell](https://planet4589.org/space/gcat/)
- [GFZ indices](https://kp.gfz.de/en/data)
- [NASA OMNIWeb](https://omniweb.gsfc.nasa.gov/form/dx1.html)
- [CelesTrak GP formats](https://celestrak.org/NORAD/documentation/gp-data-formats.php)

Raw downloads and detailed Space-Track-derived outputs remain local and excluded from Git pending source-sharing review. Public repository contents include software, documentation, progress summaries and the initial GFZ weather analysis. Preserve source attribution and review provider terms before redistributing additional data or results.
