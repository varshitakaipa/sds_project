# Manual data download

Automatic downloads failed in the current environment. Open these URLs in your browser and save the original response (not an HTML error page).

- Starlink: https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=JSON
  Save as `data/raw/starlink_2026-11-14.json`.
- OneWeb: https://celestrak.org/NORAD/elements/gp.php?GROUP=oneweb&FORMAT=JSON
  Save as `data/raw/oneweb_2026-11-14.json`.
- Kp: https://kp.gfz.de/app/json/?start=2026-10-01T00:00:00Z&end=2026-11-13T23:59:59Z&index=Kp
  Save as `data/raw/kp_2026-11-14.json`.

Create `raw` inside `data` if necessary. Use the actual download date in filenames if later. Record the URL and UTC retrieval time for manual downloads; do not invent a retrieval timestamp. Then run `python src/pipeline.py` (without `--fetch`) from the project folder. The Kp file is stored for future weather alignment, not consumed by the current orbital feature step.

For historical data, see documentations.md. Current snapshots alone cannot support early-warning evaluation.
