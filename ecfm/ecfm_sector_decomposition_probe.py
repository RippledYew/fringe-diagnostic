"""
ecfm_sector_probe.py
============================================================
🌌 ECFM — SECTOR DECOMPOSITION DYNAMICS PROBE

Goal:
    Determine whether each sector independently:
    - drives τ alignment
    - supports or destroys stability
    - contributes to slow manifold formation
"""

import numpy as np
from Ecfm_Engine import (
    evolve,
    engine_sectors,
    tau_dom,
    cos_theta,
    r_ratio,
    safe_sym,
    EPS,
    DT,
)

# ==============================================================
# CONFIG
# ==============================================================

N     = 28
ETA   = 0.75
SEED  = 0
STEPS = 200

SECTOR_KEYS = ["RG", "SOC", "CURV", "SPEC", "BACK", "closure"]


# ==============================================================
# SINGLE-SECTOR DYNAMICS
# ==============================================================

def evolve_sector(A0, sector_key, steps=200):
    """
    Evolves system using ONLY one sector active.
    All others are suppressed.
    """
    A = A0.copy()

    tau_trace = []
    r_trace   = []
    norm_trace = []

    for t in range(steps):

        sectors = engine_sectors(A)

        F = sectors[sector_key]

        A = safe_sym(A + DT * F)

        tau_trace.append(tau_dom(A))
        r_trace.append(r_ratio(A))
        norm_trace.append(np.linalg.norm(F))

    return np.array(tau_trace), np.array(r_trace), np.array(norm_trace)


# ==============================================================
# FULL SYSTEM BASELINE
# ==============================================================

print("\n" + "="*65)
print("🌌 ECFM — SECTOR DECOMPOSITION PROBE")
print("="*65)

A0, _, _ = evolve(N, SEED, ETA, STEPS)

baseline_tau = tau_dom(A0)
baseline_r   = r_ratio(A0)

print(f"\nBaseline:")
print(f"  tau = {baseline_tau:.5f}")
print(f"  r   = {baseline_r:.5f}")


# ==============================================================
# PER-SECTOR ANALYSIS
# ==============================================================

results = {}

print("\n" + "="*65)
print("🌌 SECTOR DYNAMICS")
print("="*65)

for key in SECTOR_KEYS:

    print(f"\n--- {key} ---")

    tau_t, r_t, F_t = evolve_sector(A0, key, steps=STEPS)

    d_tau = tau_t[-1] - tau_t[0]
    d_r   = r_t[-1] - r_t[0]

    mean_F = np.mean(F_t)

    results[key] = {
        "delta_tau": d_tau,
        "delta_r": d_r,
        "mean_force": mean_F,
    }

    print(f"Δtau = {d_tau:+.6f}")
    print(f"Δr   = {d_r:+.6f}")
    print(f"<||F||> = {mean_F:.6f}")


# ==============================================================
# ALIGNMENT SIGNATURES
# ==============================================================

print("\n" + "="*65)
print("🌌 SECTOR INTERPRETATION")
print("="*65)

for k, v in results.items():

    dτ = v["delta_tau"]
    dr = v["delta_r"]

    if dτ > 0 and dr < 0:
        role = "✔ τ-ALIGNING + STABILIZING"
    elif dτ > 0 and dr > 0:
        role = "⚡ τ-ALIGNING BUT DESTABILIZING"
    elif dτ < 0:
        role = "✖ τ-OPPOSING"
    else:
        role = "~ NEUTRAL / MIXED"

    print(f"{k:8s} → {role}")

# ==============================================================
# GLOBAL INTERPRETATION
# ==============================================================

print("\n" + "="*65)
print("🌌 EMERGENT STRUCTURE DIAGNOSIS")
print("="*65)

aligning = sum(1 for v in results.values() if v["delta_tau"] > 0)
opposing = sum(1 for v in results.values() if v["delta_tau"] < 0)

print(f"""
Aligning sectors : {aligning}
Opposing sectors : {opposing}

Interpretation:
----------------
If ONLY CURV/SPEC align → geometry-driven slow manifold

If SOC dominates opposition → cancellation-driven manifold

If all weak → neutral shell system (metastability only)

If mixed strong → interference manifold (your current hypothesis)
""")

print("\n[Program finished]")