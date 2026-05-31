"""
ecfm_sector_recombination_probe.py
============================================================
🌌 ECFM — SECTOR RECOMBINATION MAP

Purpose:
    Measure emergent structure from PAIRWISE sector interactions.

We evolve:
    F_ij = F_i + F_j

and compare against baseline dynamics:
    Δtau, Δr, stability shift

This probes:
    - constructive interference
    - destructive cancellation
    - nonlinear amplification channels
"""

import numpy as np

from Ecfm_Engine import (
    evolve,
    engine_sectors,
    engine_flow,
    tau_dom,
    r_ratio,
    safe_sym,
    DT,
)

# ==============================================================
# CONFIG
# ==============================================================

N     = 28
ETA   = 0.75
SEED  = 0
STEPS = 250

SECTORS = ["RG", "SOC", "CURV", "SPEC", "BACK", "closure"]


# ==============================================================
# BASELINE
# ==============================================================

print("\n" + "="*65)
print("🌌 ECFM — SECTOR RECOMBINATION MAP")
print("="*65)

A0, _, _ = evolve(N, SEED, ETA, STEPS)

tau_base = tau_dom(A0)
r_base   = r_ratio(A0)
F_base   = np.linalg.norm(engine_flow(A0))

print("\nBASELINE")
print("--------")
print(f"tau   = {tau_base:.5f}")
print(f"r     = {r_base:.5f}")
print(f"||F|| = {F_base:.5f}")


# ==============================================================
# SECTOR FLOW EXTRACTION
# ==============================================================

def sector_flow(A, i, j):
    """
    Recombined flow from two sectors only.
    """
    sectors = engine_sectors(A)

    F = sectors[i] + sectors[j]
    return F


def evolve_pair(i, j):
    """
    Evolve system using only sector pair (i, j).
    """
    A = A0.copy()

    tau_trace = []
    r_trace   = []

    for t in range(STEPS):

        F = sector_flow(A, i, j)

        A = safe_sym(A + DT * F)

        tau_trace.append(tau_dom(A))
        r_trace.append(r_ratio(A))

    return np.array(tau_trace), np.array(r_trace)


# ==============================================================
# PAIRWISE MAP
# ==============================================================

print("\n" + "="*65)
print("🌌 PAIRWISE INTERACTION MAP")
print("="*65)

results_tau = {}
results_r   = {}

for i in SECTORS:
    for j in SECTORS:

        if i >= j:
            continue

        print(f"\n--- {i} + {j} ---")

        tau_t, r_t = evolve_pair(i, j)

        d_tau = tau_t[-1] - tau_base
        d_r   = r_t[-1] - r_base

        results_tau[(i, j)] = d_tau
        results_r[(i, j)]   = d_r

        print(f"Δtau = {d_tau:+.6f}")
        print(f"Δr   = {d_r:+.6f}")


# ==============================================================
# INTERACTION CLASSIFICATION
# ==============================================================

print("\n" + "="*65)
print("🌌 INTERACTION REGIME CLASSIFICATION")
print("="*65)

for (i, j), dt in results_tau.items():

    dr = results_r[(i, j)]

    # classify regime
    if dt > 0.005 and dr < 0:
        regime = "🟢 CONSTRUCTIVE ALIGNMENT"
    elif dt < -0.005:
        regime = "🔴 DESTRUCTIVE INTERFERENCE"
    elif abs(dt) < 0.003 and abs(dr) < 0.003:
        regime = "🟡 NEUTRAL SUPERPOSITION"
    else:
        regime = "⚫ NONLINEAR AMPLIFICATION"

    print(f"{i:6s} + {j:6s} → {regime}")


# ==============================================================
# SUMMARY STRUCTURE
# ==============================================================

print("\n" + "="*65)
print("🌌 EMERGENT STRUCTURE SUMMARY")
print("="*65)

constructive = 0
destructive  = 0
neutral      = 0
nonlinear    = 0

for (i, j), dt in results_tau.items():

    dr = results_r[(i, j)]

    if dt > 0.005 and dr < 0:
        constructive += 1
    elif dt < -0.005:
        destructive += 1
    elif abs(dt) < 0.003 and abs(dr) < 0.003:
        neutral += 1
    else:
        nonlinear += 1


print(f"""
Constructive pairs : {constructive}
Destructive pairs  : {destructive}
Neutral pairs       : {neutral}
Nonlinear pairs     : {nonlinear}
""")

# interpretation
if nonlinear > constructive + destructive:
    print("⚡ INTERACTION-DOMINATED SYSTEM")
    print("   → structure emerges from pairwise geometry")
    print("   → NOT reducible to single sectors")
elif constructive > destructive:
    print("✔ ALIGNMENT-DOMINATED SYSTEM")
    print("   → CURV-like reinforcement structure likely")
else:
    print("⚠ FRUSTRATION-DOMINATED SYSTEM")
    print("   → cancellation manifold / competing flows")

print("\n[Program finished]")