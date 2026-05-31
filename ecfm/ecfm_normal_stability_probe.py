"""
probe_normal_stability.py
=========================================================
ECFM — NORMAL STABILITY / CANCELLATION PROBE

Tests whether the extracted kernel behaves like:

1. attracting slow manifold
2. dynamically stabilized cancellation manifold
3. projective attractor

Requires:
    ecfm_engine.py
=========================================================
"""

import numpy as np
import sys

sys.path.insert(0, '/storage/emulated/0/')

from Ecfm_Engine import (
    evolve,
    extract_basis,
    engine_flow,
    safe_sym,
    safe_clip,
    EPS,
    DT
)

# =========================================================
# PARAMETERS
# =========================================================

N       = 28
ETA     = 0.75
SEED    = 0
STEPS   = 400

K_DIM   = 12

PERT    = 1e-2
EVOLVE2 = 200

# =========================================================
# HELPERS
# =========================================================

def orthoproject(v, basis):
    """
    Remove kernel components from vector v.
    """
    out = v.copy()

    for b in basis:
        out -= np.dot(out, b) * b

    return out


def evolve_state(A0, steps):
    """
    Evolve arbitrary state.
    """
    A = A0.copy()

    traj = []

    for _ in range(steps):
        F = engine_flow(A)
        A = safe_sym(A + DT * F)
        A = safe_clip(A)

        traj.append(A.copy())

    return traj


def distance_from_kernel(A, basis):
    """
    Distance of state from kernel subspace.
    """
    v = A.flatten()

    proj = np.zeros_like(v)

    for b in basis:
        proj += np.dot(v, b) * b

    perp = v - proj

    return np.linalg.norm(perp)


# =========================================================
# MAIN
# =========================================================

print("\n" + "="*65)
print("🌌 ECFM — NORMAL STABILITY PROBE")
print("="*65)

# ---------------------------------------------------------
# Converged state
# ---------------------------------------------------------

A_conv, late_states, late_flows = evolve(
    N,
    SEED,
    ETA,
    steps=STEPS
)

basis = extract_basis(late_flows, k=K_DIM)

basis = basis / (
    np.linalg.norm(basis, axis=1, keepdims=True) + EPS
)

print("\nExtracted kernel basis.")

# ---------------------------------------------------------
# Build perturbations
# ---------------------------------------------------------

dim = N * N

rand_vec = np.random.randn(dim)

# tangent perturbation
v_tan = np.zeros(dim)

for b in basis:
    v_tan += np.dot(rand_vec, b) * b

v_tan /= np.linalg.norm(v_tan) + EPS

# orthogonal perturbation
v_orth = orthoproject(rand_vec, basis)
v_orth /= np.linalg.norm(v_orth) + EPS

# reshape
dA_tan  = PERT * v_tan.reshape(N, N)
dA_orth = PERT * v_orth.reshape(N, N)

# symmetric
dA_tan  = safe_sym(dA_tan)
dA_orth = safe_sym(dA_orth)

print(f"\nPerturbation amplitude = {PERT}")

# ---------------------------------------------------------
# Perturbed trajectories
# ---------------------------------------------------------

traj_tan  = evolve_state(A_conv + dA_tan,  EVOLVE2)
traj_orth = evolve_state(A_conv + dA_orth, EVOLVE2)

# ---------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------

print("\n" + "="*65)
print("🌌 DISTANCE FROM KERNEL")
print("="*65)

print(f"""
   step | tangent_pert | orthogonal_pert
------------------------------------------------
""")

checkpoints = [0, 5, 10, 20, 50, 100, 150, 199]

for t in checkpoints:

    d_tan = distance_from_kernel(traj_tan[t], basis)
    d_orth = distance_from_kernel(traj_orth[t], basis)

    print(
        f"{t:7d} | "
        f"{d_tan:14.6f} | "
        f"{d_orth:16.6f}"
    )

# ---------------------------------------------------------
# Decay rates
# ---------------------------------------------------------

orth_dist = np.array([
    distance_from_kernel(A, basis)
    for A in traj_orth
])

times = np.arange(len(orth_dist))

mask = orth_dist > EPS

if np.sum(mask) > 5:

    slope, intercept = np.polyfit(
        times[mask],
        np.log(orth_dist[mask]),
        1
    )

    print("\n" + "="*65)
    print("🌌 NORMAL STABILITY VERDICT")
    print("="*65)

    print(f"""
Orthogonal decay slope = {slope:.6f}

Interpretation:

slope << 0
    strong attracting manifold

slope ~ 0
    no attraction
    possible cancellation manifold

positive slope
    unstable normal directions
""")

    if slope < -1e-2:
        print("✔ Strong normal attraction")
    elif slope < -1e-4:
        print("⚡ Weak normal attraction")
    elif abs(slope) <= 1e-4:
        print("🌌 Neutral/cancellation regime")
    else:
        print("✖ Orthogonal instability")

print("\n[Program finished]")