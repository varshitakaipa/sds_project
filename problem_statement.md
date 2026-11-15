# Problem statement

## Project
Early Detection of Satellite Degradation and Failure in LEO Megaconstellations

Author: Varshita K (CS24BT007), Space and Data Science Club.

## Problem and research question
Public orbital data records how satellites move, but operators rarely publish detailed spacecraft-health telemetry. This project investigates whether orbital histories contain measurable warning signs before operational degradation or failure, and whether these signals generalise across constellations.

Orbital changes also occur during deployment, planned manoeuvres, disposal and geomagnetic disturbances. A useful detector must distinguish these behaviours and report uncertainty rather than equating every anomaly with failure.

## Proposed approach
1. Collect historical GP orbital elements and independently corroborated satellite-status records.
2. Validate observations and derive orbital time-series features.
3. Incorporate geomagnetic and solar context and, later, atmospheric-density estimates.
4. Establish an anomaly-detection baseline; consider survival models only if suitable event labels exist.
5. Evaluate with temporal holdouts, precision/recall, false alarms per satellite-day and warning lead time.
6. Begin with Starlink; later test transfer to OneWeb and Qianfan.

## Current scope
The initial implementation cleans a small Starlink history sample, calculates approximate orbital features, checks coverage and aligns observations with space-weather indices. It includes exploratory plots and automated tests. The sample comes from one launch and is not representative of constellation-wide reliability.

## Expected outcome and limitations
The intended outcome is a reproducible study of possible degradation signatures and their warning-time/false-alarm tradeoff. Successful early prediction is a research question, not an established result. No validated failure detector, manoeuvre detector, density correction or predictive evaluation exists yet. Mean-element altitude proxies are not precise SGP4-propagated positions; catalogue status alone is not a failure label.

See [pipeline.md](pipeline.md) for the implemented workflow and [Report_month.md](Report_month.md) for completed work. The original proposal is included in this repository.
