# Synthetic baseline checks

Generated entirely by src/demo_baseline.py; no Space-Track data is included. Seven fictional IDs, 44 days, deterministic low-amplitude sinusoidal altitude-proxy noise. Calibration uses days before October 22 and a 0.02 km/day scale floor. Scenarios add no change, a +1 km common step to all objects, a one-day -1 km excursion for ID 0, or sustained -0.2 km/day drift for ID 0. The excursion produces two changed daily rates (drop and recovery); the drift produces 19 changed rates. Expected counts are asserted in code.

These deliberately simple examples validate arithmetic and peer filtering. They do not establish robustness to real storms, manoeuvres, model errors or failure signatures. They provide no real-world precision, recall or lead-time evidence.
