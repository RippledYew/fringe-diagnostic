"""
ecfm_probe_normal_lyapunov.py
=============================================================
🌌 ECFM — NORMAL LYAPUNOV PROBE

Goal
----
Measure the NORMAL Lyapunov exponent of the extracted
12D kernel manifold.

Question:
    Do orthogonal perturbations decay exponentially?

If YES:
    manifold is genuinely normally attracting

If NO:
    manifold is only metastable / cancellation-balanced

This is the decisive follow-up to the normal stability probe.

Theory
------
We measure:

    λ_perp(t) = (1/t) log(||δ_perp(t)|| / ||δ0||)

Interpretation:

λ_perp < 0
    attracting normal bundle

λ_perp ≈ 0
    neutral slow shell / cancellation manifold

λ_perp > 0
    unstable manifold

Expected for ECFM:
    small negative λ_perp
"""

import numpy as np
import sys

# ==============================================================
# IMPORT ENGINE
# ==============================================================

sys.path.insert(0, '/storage/emulated/0/')

from Ecfm_Engine import (
    evolve,
    extract_basis,
    engine_flow,
    safe_sym,
    EPS,
    DT,
)

# ==============================================================
# CONFIG
# ==============================================================

N         = 28
ETA       = 0.75
SEED      = 0

STEPS_EQ  = 400
STEPS_RUN = 300

K_DIM     = 12
PERT_AMPL = 1e-2

PRINT_STEPS = [0, 1, 2, 5, 10, 20, 50, 100, 150, 200, 299]


# ==============================================================
# BASIS HELPERS
# ==============================================================

def flatten(A):
    return A.flatten()

def unflatten(v, N):
    return v.reshape(N, N)

def normalize(v):
    return v / (np.linalg.norm(v) + EPS)

def orthogonal_projector(basis):
    """
    basis: (k, N²)
    returns projector onto orthogonal complement
    """
    B = basis.T
    P = B @ B.T
    I = np.eye(P.shape[0])
    return I - P

def tangent_projector(basis):
    B = basis.T
    return B @ B.T


# ==============================================================
# BUILD KERNEL
# ==============================================================

print("\n" + "="*65)
print("🌌 ECFM — NORMAL LYAPUNOV PROBE")
print("="*65)

A_conv, late_states, late_flows = evolve(
    N=N,
    seed=SEED,
    eta=ETA,
    steps=STEPS_EQ,
)

basis = extract_basis(late_flows, k=K_DIM)

if basis is None:
    raise RuntimeError("Could not extract kernel basis.")

basis = basis / (
    np.linalg.norm(basis, axis=1, keepdims=True) + EPS
)

print("\nExtracted kernel basis.")
print(f"K_DIM = {K_DIM}")

# ==============================================================
# BUILD ORTHOGONAL PERTURBATION
# ==============================================================

rng = np.random.default_rng(1234)

v = rng.normal(size=N*N)
v = normalize(v)

P_perp = orthogonal_projector(basis)

v_perp = P_perp @ v
v_perp = normalize(v_perp)

delta0 = PERT_AMPL * v_perp

print(f"Perturbation amplitude = {PERT_AMPL}")

# ==============================================================
# EVOLVE REFERENCE + PERTURBED TRAJECTORIES
# ==============================================================

A_ref  = A_conv.copy()

A_pert = safe_sym(
    A_conv + unflatten(delta0, N)
)

# ==============================================================
# TRACK NORMAL DISTANCE
# ==============================================================

times      = []
distances  = []
lyap_est   = []

print("\n" + "="*65)
print("🌌 NORMAL SEPARATION EVOLUTION")
print("="*65)

print(f"""
{'step':>7} | {'||δ_perp||':>14} | {'λ_perp(t)':>14}
--------------------------------------------------------
""")

for t in range(STEPS_RUN):

    # evolve both systems
    F_ref  = engine_flow(A_ref)
    F_pert = engine_flow(A_pert)

    A_ref  = safe_sym(A_ref  + DT * F_ref)
    A_pert = safe_sym(A_pert + DT * F_pert)

    # difference vector
    delta = flatten(A_pert - A_ref)

    # project orthogonal to kernel
    delta_perp = P_perp @ delta

    d = np.linalg.norm(delta_perp)

    # finite-time Lyapunov estimate
    lam = np.log((d + EPS) / PERT_AMPL) / ((t + 1) * DT)

    times.append(t)
    distances.append(d)
    lyap_est.append(lam)

    if t in PRINT_STEPS:
        print(f"{t:7d} | {d:14.8f} | {lam:14.8f}")

# ==============================================================
# FIT ASYMPTOTIC EXPONENT
# ==============================================================

tail_start = int(0.5 * STEPS_RUN)

tail_t = np.array(times[tail_start:]) * DT
tail_d = np.array(distances[tail_start:])

# log-linear fit
coef = np.polyfit(tail_t, np.log(tail_d + EPS), 1)

lambda_fit = coef[0]

# ==============================================================
# SUMMARY
# ==============================================================

print("\n" + "="*65)
print("🌌 NORMAL LYAPUNOV VERDICT")
print("="*65)

print(f"""
Asymptotic λ_perp ≈ {lambda_fit:.8f}

Interpretation
--------------

λ_perp << 0
    strong normally attracting manifold

small negative λ_perp
    weak metastable attraction
    cancellation-induced slow manifold

λ_perp ≈ 0
    neutral shell
    no true normal attraction

λ_perp > 0
    unstable transverse dynamics
""")

if lambda_fit < -1e-2:
    print("✔ STRONG NORMAL ATTRACTION")
    print("  Fenichel-style slow manifold plausible")

elif lambda_fit < -1e-3:
    print("⚡ WEAK NORMAL ATTRACTION")
    print("  metastable slow manifold")
    print("  likely cancellation-supported")

elif lambda_fit < 1e-3:
    print("⚠ NEAR-NEUTRAL")
    print("  manifold behaves like coherence shell")
    print("  persistence without strong contraction")

else:
    print("✖ TRANSVERSE INSTABILITY")
    print("  kernel is not dynamically attracting")

print(f"""
Physical meaning
----------------
This probe measures whether trajectories are dynamically
pulled back toward the extracted kernel manifold.

A small negative exponent would strongly support:

    'slow meta-stable manifold generated by
     sector cancellation'

rather than a classical hyperbolic invariant manifold.
""")

print("\n[Program finished]")