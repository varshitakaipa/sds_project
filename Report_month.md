# Report_month - November 2026

Student: Varshita K (CS24BT007)
Actual work date: 14 November 2026. Initial milestone; no earlier month of work is claimed.

## Things tried and completed
- Organised the repository and preserved the proposal.
- Reviewed official CelesTrak, GFZ and Space-Track documentation.
- Implemented an orbital downloader and approximate feature extraction, pending real orbital data validation.
- Attempted orbital downloads; CelesTrak timed out, including user attempts on a hotspot.
- Acquired real GFZ Kp JSON by manual browser download.
- Implemented offline validation of lengths, finite values, UTC three-hour timestamps, duplicates and provider status.
- Recorded file hash, source and licence metadata; exact retrieval time remains unknown.
- Exported clean data, daily summaries and contiguous Kp >= 5 context intervals.
- Generated a time-series and distribution plot.
- Ran five automated tests covering orbital calculations and Kp validation/interval grouping: all passed.

## Initial findings
- 352 three-hour observations covering 1 October through 13 November 2026 (44 days).
- No missing bins within the observed span.
- 248 definitive and 104 provisional observations.
- Maximum Kp: 7.333.
- 9 bins (27 hours, 2.56%) meet Kp >= 5, grouped into 7 contiguous intervals.
- These are environmental context flags, not satellite failure detections or independently validated storm events.

## Evidence
See src/analyze_kp.py and results/space_weather/ for clean CSV, daily summaries, interval table, summary, provenance, findings and kp_overview.png. Test output is in results/verification.txt.

## Remaining work
1. Acquire historical orbital data and independently sourced status labels. Orbital observations acquired: 0.
2. Join orbital epochs to UTC weather intervals and inspect gaps, trends and manoeuvre confounding.
3. Add density/solar inputs before estimating drag.
4. Develop and temporally evaluate a baseline once history is available.
5. Restore GitHub authentication and upload; last checked CLI token was invalid.

No degradation detector, failure prediction or warning-lead-time result is claimed.
