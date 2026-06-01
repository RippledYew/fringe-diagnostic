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

###Report Cross-Reference (v3.6 Section V.4)
Canonical STD Invariant: CURV/SOC = 0.663-0.685 (CV=0.011)
Stability collapse signature: jumps to 4,238, 660 at N_c (not gradual)
Our reading of 3.087 is STABLE and eta-independent - not a collapse signature.
Hypothesis: platform-dependent numerical difference in sector norm computation.
Android/Pydroid3 vs Linux x86_64 floating point behavior.
Priority: inspect engine_sectors() on Zion once live.

### Significance
Value is consistent and stable - hallmarks of a true invariant.
Absolute value differs from v3.6 clibration by ~4.5x.
Not a stability collapse - collapse signature would be millions, not ~3.

### Hypotheses
1. engine_sectors() numerical behavior differs between Android and Linux x86_64
2. Tolerance window needs recalibration for Linux platform
3. Possible floating point accumulation difference across platforms

### Next Steps
- Inspect engine_sectors() function in Ecfm_Engine.py
- Compare with original probe results if available
- Recalibrate tolerance window on Zion once live
- Run no-clip (v4.0 target) to test invariant behavior in unbounded space

### Platform Test (2026-06-01)
Ran smoke test run on Android/Pydroid3 (original platform)
Result: CURV?SOC=3.087 - identical to Acer/Linux result.
Platform hypothesis: ELIMINATED.
New hypothesis: 0.685 canonical value was measured during specific sector sweep probes, not smoke test defaults. 
The smoke test may not be the STD invariant sweet spot.