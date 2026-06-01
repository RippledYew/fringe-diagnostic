# ECFM Research Notes - Acer Node

## Open Question 001 - CURV/SOC Invariant Discrepency
**Date:** 2026-06-01
**Engine:** v40.4
**Runner:** ecfm_runner.py (calibrated 3.6)

### Observation
Eta sweep prode (p001-p004, n=28, seed=0, steps=400) shows CURV/SOC
consistently reading ~3.08 across all eta values (0.58, 0.60, 0.75, 0.90).

Runner Tolerance Window: 0.640-0.710 (from v3.6 calibration)
Observed value: ~3.08 (stable, eta-independent)

### Platform Test (2026-06-01)
Ran smoke test run on Android/Pydroid3 (original platform)
Result: CURV?SOC=3.087 - identical to Acer/Linux result.
Platform hypothesis: ELIMINATED.
New hypothesis: 0.685 canonical value was measured during specific sector sweep probes, not smoke test defaults. 
The smoke test may not be the STD invariant sweet spot.

### Steps Sweep - probe_002 (n=28, eta=0.75, seed=0)
| steps | CURV/SOC | regime | cos_heta | inv |
|-------|----------|----------|----------|------|
| 400   | 3.087    | STD      | +0.7352  | flag |
| 1000  | 1.272    | STD      | +0.7278  | flag |
| 5000  | 0.294    | STD      | +0.6659  | flag |
| 10000 | n/a      | BOUNDARY | +0.4292  | pass |
| 50000 | 0.008    | STD      | +0.9125  | flag |

### Interpretation
CURV/SOC migrates across a wide range as trajectory deepens.
at 50k steps: tau=1.0000, cos_thet=0.9125 - near STD fixed point geometry.
CURV/SOC=0.008 at 50k undershoots the invariant window (0.640-0.710).
the 0.640-0.710 window may be a MID-TRAJECTORY property, not a
fixed point property. Invariant may be transiently locking during
approach to fixed point, not at the fixed point itself.

### Significance
Value is consistent and stable - hallmarks of a true invariant.
Absolute value differs from v3.6 clibration by ~4.5x.
Not a stability collapse - collapse signature would be millions, not ~3.

### Hypotheses
1. CURV/SOC window 0.640-0.710 is a mid-trajectory adiabatic property
2. Window was measured during approach phase, not at fixed point
3. need a probe targetting t=5k-20k range to find the lock window

### Next Steps
- Design probe sweeping steps=5000-20000 to find exact lock window
- Inspect engine_sectors() function in Ecfm_Engine.py
- Recalibrate tolerance window based on trajectory phase
- Run no-clip probe (v4.0 target) on Zion once live