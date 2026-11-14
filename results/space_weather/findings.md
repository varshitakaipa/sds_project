# Initial space-weather findings

Validated 352 three-hour observations covering 2026-10-01T00:00:00+00:00 to 2026-11-14T00:00:00+00:00 (exclusive). Missing bins within this span: 0.

Maximum Kp: 7.333. Bins with Kp >= 5: 9 (2.6%); contiguous above-threshold intervals: 7. Status counts: {'def': 248, 'pre': 104}.

Kp >= 5 is used as an exploratory geomagnetic-storm context flag, informed by NOAA's G1 threshold: https://www.spaceweather.gov/noaa-scales-explanation . These contiguous intervals are algorithmic groups, not independently validated storm events. A dip below threshold or a missing bin splits an interval. Boundary intervals may continue outside the downloaded window.

Source: GFZ Potsdam, https://kp.gfz.de/en/data ; provider metadata reports CC BY 4.0. Preserve attribution. Provisional values can change. Retrieval time was not recorded; file hash and analysis time are in provenance.json.

This is environmental context for future orbit analysis. Kp is a quasi-logarithmic planetary index, not a direct density or satellite-health measurement. No satellite failures, drag changes or predictive performance can be inferred from this dataset alone.
