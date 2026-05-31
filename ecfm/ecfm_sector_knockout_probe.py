"""
ecfm_sector_knockout_probe.py
============================================================
🌌 ECFM — SECTOR KNOCKOUT PROBE

Causal test:
    Does system stability depend on ALL sectors,
    or is there redundancy / dominance?

We compare:
    FULL system vs SINGLE-SECTOR REMOVALS

Outputs:
    - Δtau collapse/growth
    - Δr stability shift
    - norm_F stability
    - structural dependency classification
"""

import numpy as np

from Ecfm_Engine import (
    evolve,
    engine_sectors,
    engine_flow,
    tau_dom,
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
STEPS = 250

SECTORS = ["RG", "SOC", "CURV", "SPEC", "BACK", "closure"]


# ==============================================================
# BASELINE EVOLUTION
# ==============================================================

print("\n" + "="*65)
print("🌌 ECFM — SECTOR KNOCKOUT PROBE")
print("="*65)

A0, _, _ = evolve(N, SEED, ETA, STEPS)

tau_base = tau_dom(A0)
r_base   = r_ratio(A0)
F_base   = np.linalg.norm(engine_flow(A0))

print("\nBASELINE STATE")
print("----------------")
print(f"tau = {tau_base:.5f}")
print(f"r   = {r_base:.5f}")
print(f"||F|| = {F_base:.5f}")


# ==============================================================
# SECTOR REMOVAL FUNCTION
# ==============================================================

def flow_without_sector(A, remove_key):
    """
    Recompute flow with one sector removed.
    """
    sectors = engine_sectors(A)

    F = np.zeros_like(A)

    for k, v in sectors.items():
        if k == "F_total":
            continue
        if k == remove_key:
            continue
        F += v

    return F


def evolve_knockout(remove_key):
    """
    Evolve system with one sector removed.
    """
    A = A0.copy()

    tau_trace = []
    r_trace   = []

    for t in range(STEPS):

        F = flow_without_sector(A, remove_key)

        A = safe_sym(A + DT * F)

        tau_trace.append(tau_dom(A))
        r_trace.append(r_ratio(A))

    return np.array(tau_trace), np.array(r_trace)


# ==============================================================
# RUN KNOCKOUT TESTS
# ==============================================================

results = {}

print("\n" + "="*65)
print("🌌 SECTOR KNOCKOUT DYNAMICS")
print("="*65)

for sec in SECTORS:

    print(f"\n--- removing {sec} ---")

    tau_t, r_t = evolve_knockout(sec)

    d_tau = tau_t[-1] - tau_base
    d_r   = r_t[-1] - r_base

    results[sec] = (d_tau, d_r)

    print(f"Δtau = {d_tau:+.6f}")
    print(f"Δr   = {d_r:+.6f}")


# ==============================================================
# STRUCTURAL INTERPRETATION
# ==============================================================

print("\n" + "="*65)
print("🌌 CAUSAL STRUCTURE DIAGNOSIS")
print("="*65)

critical = []

for sec, (dt, dr) in results.items():

    if abs(dt) > 0.01 or abs(dr) > 0.05:
        critical.append(sec)

        print(f"{sec:8s} → ❗ CRITICAL (system depends on it)")
    else:
        print(f"{sec:8s} → ~ redundant / perturbative")

print("\nSUMMARY")
print("-------")

if len(critical) >= 3:
    print("⚡ HIGH INTERFERENCE SYSTEM")
    print("   → stability depends on sector balance")
    print("   → cancellation manifold confirmed candidate")
elif len(critical) == 1:
    print("⚠ DOMINANT SECTOR SYSTEM")
    print("   → likely reducible dynamics")
else:
    print("✔ REDUNDANT STRUCTURE")
    print("   → stable core independent of sector decomposition")


print("\n[Program finished]")