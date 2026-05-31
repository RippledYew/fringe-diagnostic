"""
ecfm_engine.py — ECFM Core Engine Module
=========================================
Gospel engine v40.4 as a clean, importable module.

All probe scripts should import from here. The engine
parameters are frozen — do not modify them.

Exports:
    engine_flow(A)          — full composite flow F(A)
    engine_sectors(A)       — six sectors separately
    tau_dom(A)              — dominant coherence mode
    cos_theta(A)            — causal alignment angle
    spectral_distribution(A)— normalized eigenvalue spectrum
    evolve(N, seed, eta, steps) — run to convergence
    r_ratio(A)              — ||F_perp|| / ||F_parallel||
    phase_label(tau)        — CONDENSATE / CORE / DECOHERED
    PARAMS                  — frozen parameter dict

─────────────────────────────────────────────────────────────
CHANGELOG
─────────────────────────────────────────────────────────────
v40.4  — beta adjusted 0.080 → 0.045.

    Motivation: systematic stability margin probe series
    (ecfm_stability_margin.py, ecfm_beta_confirmation.py,
    ecfm_beta_045_j12.py) established that base beta=0.080
    sat at or on the PERP boundary (beta_c ≈ 0.080) at
    N=24,27,30, giving zero attractor margin and eroding
    the J_12 stability margin to spec_abs ≈ −0.006.

    beta=0.045 confirmed across N=24–36:
      Basin census:  20/20 STD seeds at every N  (✓)
      J_12 margin:   spec_abs −0.016 to −0.018   (✓)
      Navigation:    beta_c margin +0.035 at N=27 (✓)
      cos_theta:     0.646–0.682  (causal alignment emergent)
      CURV/SOC:      ≈ 0.663  (within locked range)
      d1:            0.150 exactly  (invariant, unchanged)
      R × gamma:     ≈ 0.024  (self-regulation active)

    Push-pull navigation: raise beta to 0.080–0.085 to enter
    PERP attractor regime. All other parameters unchanged.

v40.3  — parameters frozen as gospel engine (prior baseline).
─────────────────────────────────────────────────────────────
"""

import numpy as np

# ==============================================================
# FROZEN PARAMETERS — v40.4 (do not modify)
# ==============================================================

PARAMS = {
    "alpha": 0.12,
    "beta":  0.045,    # adjusted from 0.080 — see changelog
    "gamma": 0.15,
    "delta": 0.04,
    "eta":   0.06,
    "kappa": 0.18,
    "DT":    0.01,
    "EPS":   1e-10,
    "CLIP":  6.0,
}

_a = PARAMS["alpha"]
_b = PARAMS["beta"]
_g = PARAMS["gamma"]
_d = PARAMS["delta"]
_e = PARAMS["eta"]
_k = PARAMS["kappa"]
DT  = PARAMS["DT"]
EPS = PARAMS["EPS"]

# finite difference step for gradient computations
_DELTA = 1e-4


# ==============================================================
# SAFE OPS
# ==============================================================

def safe_sym(A):
    """Enforce symmetry."""
    return 0.5 * (A + A.T)

def safe_clip(A, lim=None):
    """Clip entries and zero NaNs."""
    lim = lim or PARAMS["CLIP"]
    return np.nan_to_num(np.clip(A, -lim, lim))

def safe_eigh(A):
    """Stable symmetric eigendecomposition."""
    A = safe_sym(A)
    try:
        return np.linalg.eigh(A)
    except np.linalg.LinAlgError:
        return np.linalg.eigh(A + 1e-6 * np.eye(A.shape[0]))

def _eig_spectrum(M):
    """Clipped positive eigenvalues of a symmetric matrix."""
    return np.clip(np.linalg.eigvalsh(safe_sym(M)), EPS, None)


# ==============================================================
# STATE-DEPENDENT GEOMETRY
# ==============================================================

def _intrinsic_geometry(A):
    """
    Three scalar geometric features from log-spectral decomposition of g.
    Returns (curvature_variance, anisotropy, volume).
    """
    vals     = _eig_spectrum(A @ A.T)
    log_spec = np.log(vals + EPS)
    return (
        float(np.sum((log_spec - np.mean(log_spec))**2)),
        float(np.std(log_spec)),
        float(np.mean(log_spec)),
    )

def _effective_couplings(A):
    """
    State-dependent effective couplings.
    Returns (a, b, g, d, e, k) — all six sectors.
    """
    curv, aniso, vol = _intrinsic_geometry(A)
    d1 = 0.15 * np.tanh(0.1 * curv)
    d2 = 0.10 * np.tanh(aniso)
    d3 = 0.08 * np.tanh(vol)
    return (
        _a * (1.0 + d1),
        _b * (1.0 - d2),
        _g * (1.0 + d1),
        _d * (1.0 - d2),
        _e * (1.0 + d3),
        _k * (1.0 - 0.5 * d1),
    )

def curvature_R(A):
    """Scalar curvature R(A) = Tr(A^2) - Tr(A)^2/N."""
    return float(np.trace(A @ A) - (np.trace(A)**2) / A.shape[0])


# ==============================================================
# GOSPEL ENGINE — v40.4
# ==============================================================

def engine_sectors(A):
    """
    Returns all six flow sectors separately as a dict.
    Signs match their contribution to F_total.

    Keys: RG, SOC, CURV, SPEC, BACK, closure, F_total
    """
    A  = safe_sym(A)
    Nm = A.shape[0]
    a, b, g, d, e, k = _effective_couplings(A)

    gm   = np.eye(Nm) + A @ A.T
    R    = curvature_R(A)
    vals, vecs = safe_eigh(A)

    RG      = -a * (A @ A - np.eye(Nm) * np.trace(A @ A) / Nm)
    SOC     =  b * np.tanh(A)
    CURV    = -g * R * A
    SPEC    =  vecs @ np.diag(d * vals) @ vecs.T
    BACK    =  e * (gm - np.eye(Nm))
    closure =  k * np.tanh(A @ A)

    F_total = RG + SOC + CURV - SPEC - BACK + closure

    return {
        "RG":      RG,
        "SOC":     SOC,
        "CURV":    CURV,
        "SPEC":    -SPEC,     # signed contribution
        "BACK":    -BACK,     # signed contribution
        "closure": closure,
        "F_total": F_total,
    }

def engine_flow(A):
    """
    Full composite flow F(A).
    dA/dt = engine_flow(A)
    """
    return engine_sectors(A)["F_total"]


# ==============================================================
# TAU OBSERVABLE
# ==============================================================

def tau_dom(A):
    """
    Dominant coherence mode tau.
    tau = largest normalized eigenvalue of C = K K^T / Tr(K K^T)
    where K = stack([A^2, A, A, A, A, A]).

    Returns float in [0, 1].
    Phase: CONDENSATE (>0.95), CORE (0.70-0.95), DECOHERED (<0.70)
    """
    K    = np.stack([A @ A, A, A, A, A, A], axis=0)
    flat = K.reshape(K.shape[0], -1)
    C    = flat @ flat.T
    C    = C / (np.trace(C) + EPS)
    ev   = np.linalg.eigvalsh(C)
    ev   = np.sort(ev)[::-1]
    return float(ev[0] / (np.sum(np.abs(ev)) + EPS))

def phase_label(tau):
    """Phase classification from tau value."""
    if tau > 0.95:
        return "CONDENSATE"
    elif tau > 0.70:
        return "CORE"
    else:
        return "DECOHERED"


# ==============================================================
# TAU GRADIENT
# ==============================================================

def grad_tau(A):
    """
    Gradient of tau w.r.t. A as a flattened N^2 vector.
    Computed by finite difference.
    """
    N    = A.shape[0]
    tau0 = tau_dom(A)
    grad = np.zeros(N * N)

    for i in range(N):
        for j in range(i, N):
            Ap = A.copy()
            Ap[i, j] += _DELTA
            if i != j:
                Ap[j, i] += _DELTA
            dtau = (tau_dom(Ap) - tau0) / _DELTA
            w    = 1.0 if i == j else 2.0
            grad[i*N + j] += w * dtau
            if i != j:
                grad[j*N + i] += w * dtau

    return grad

def grad_tau_hat(A):
    """Unit vector in grad_tau direction."""
    g    = grad_tau(A)
    norm = np.linalg.norm(g)
    return g / (norm + EPS)


# ==============================================================
# CAUSAL ALIGNMENT
# ==============================================================

def cos_theta(A):
    """
    Causal alignment angle cos_theta = <F(A), grad_tau> / (||F|| ||grad_tau||).

    Stable at ~0.663–0.682 in the condensation band interior (v40.4).
    Phase boundary is where cos_theta = 0.
    """
    F    = engine_flow(A).flatten()
    g    = grad_tau(A)
    nF   = np.linalg.norm(F)
    ng   = np.linalg.norm(g)
    return float(np.dot(F, g)) / (nF * ng + EPS)

def r_ratio(A):
    """
    r = ||F_perp|| / ||F_parallel||
    where F_parallel is the component of F(A) along grad_tau.

    cos_theta = 1/sqrt(1+r^2) exactly.
    """
    F    = engine_flow(A).flatten()
    ehat = grad_tau_hat(A)
    proj = float(np.dot(F, ehat))
    F_par  = proj * ehat
    F_perp = F - F_par
    return float(np.linalg.norm(F_perp)) / (abs(proj) + EPS)


# ==============================================================
# SPECTRAL DISTRIBUTION
# ==============================================================

def spectral_distribution(A):
    """
    Normalized eigenvalue spectrum of A@A.T.
    p_i = lambda_i / sum(lambda), sorted descending.
    Defines a point on the probability simplex.
    """
    vals = _eig_spectrum(A @ A.T)
    vals = np.sort(vals)[::-1]
    return vals / (np.sum(vals) + EPS)

def shannon_entropy(A):
    """Shannon entropy of spectral distribution H(p)."""
    p = np.clip(spectral_distribution(A), EPS, None)
    return float(-np.sum(p * np.log(p)))

def d_eff(A):
    """
    Effective dimension d_eff = exp(H(p)).
    Adiabatic invariant in condensed phase.
    """
    return float(np.exp(shannon_entropy(A)))


# ==============================================================
# EVOLUTION
# ==============================================================

def evolve(N, seed, eta, steps=400, late_frac=0.80):
    """
    Evolve ECFM to convergence.

    Args:
        N:          system size
        seed:       random seed
        eta:        initialization amplitude
        steps:      number of integration steps
        late_frac:  fraction of trajectory counted as 'late'

    Returns:
        A_conv:     converged state
        late_states: list of A matrices from late trajectory
        late_flows:  corresponding flow snapshots (flattened)
    """
    np.random.seed(seed + int(N * 100 + eta * 1000))
    A = safe_sym(eta * np.random.randn(N, N))

    late_start  = int(late_frac * steps)
    late_states = []
    late_flows  = []

    for t in range(steps):
        F = engine_flow(A)
        A = safe_sym(A + DT * F)
        A = safe_clip(A)
        if t >= late_start:
            late_states.append(A.copy())
            late_flows.append(F.flatten())

    return A, late_states, late_flows


def extract_basis(late_flows, k=12):
    """
    Extract k-dimensional kernel basis from late flow snapshots.
    Returns (k, N^2) matrix of top-k right singular vectors.
    """
    snaps = np.array(late_flows)
    if len(snaps) < k:
        return None
    snaps = snaps - snaps.mean(axis=0)
    _, _, Vt = np.linalg.svd(snaps, full_matrices=False)
    return Vt[:k]


# ==============================================================
# OBSERVABLES BUNDLE
# ==============================================================

def observables(A):
    """
    Compute all primary observables at state A.
    Returns dict with tau, cos_theta, r, d_eff, entropy, phase.

    Note: cos_theta and r require grad_tau computation (O(N^2) calls).
    For fast scanning use tau and d_eff only.
    """
    tau   = tau_dom(A)
    deff  = d_eff(A)
    H     = shannon_entropy(A)

    F     = engine_flow(A).flatten()
    g     = grad_tau(A)
    nF    = np.linalg.norm(F)
    ng    = np.linalg.norm(g)
    cos_t = float(np.dot(F, g)) / (nF * ng + EPS)

    ehat  = g / (ng + EPS)
    proj  = float(np.dot(F, ehat))
    F_perp= F - proj * ehat
    r     = float(np.linalg.norm(F_perp)) / (abs(proj) + EPS)

    return {
        "tau":       tau,
        "phase":     phase_label(tau),
        "cos_theta": cos_t,
        "r":         r,
        "d_eff":     deff,
        "entropy":   H,
        "norm_F":    float(nF),
    }


def observables_fast(A):
    """
    Fast observable bundle — no grad_tau computation.
    Returns tau, d_eff, entropy, phase only.
    Use for parameter sweeps where speed matters.
    """
    tau  = tau_dom(A)
    deff = d_eff(A)
    H    = shannon_entropy(A)
    F    = engine_flow(A)
    return {
        "tau":     tau,
        "phase":   phase_label(tau),
        "d_eff":   deff,
        "entropy": H,
        "norm_F":  float(np.linalg.norm(F)),
    }


# ==============================================================
# RESULTS STORE
# Lightweight JSON persistence for probe outputs.
# Saves to /sdcard/ecfm_results/ — visible outside Pydroid.
# ==============================================================

import json
import os

RESULTS_DIR = "/sdcard/ecfm_results"

def save_result(probe_name, params, data):
    """
    Append one result to probe_name.json.
    Each line is one JSON record.

    Usage:
        save_result("phase_sweep",
                    {"N": 28, "eta": 0.75, "seed": 0},
                    {"tau": 0.985, "cos": 0.678})
    """
    os.makedirs(RESULTS_DIR, exist_ok=True)
    path = os.path.join(RESULTS_DIR, f"{probe_name}.json")
    with open(path, "a") as f:
        json.dump({"params": params, "data": data}, f)
        f.write("\n")


def load_results(probe_name):
    """
    Load all saved results for a probe.
    Returns list of {"params":..., "data":...} dicts.

    Usage:
        results = load_results("phase_sweep")
        taus = [r["data"]["tau"] for r in results]
    """
    path = os.path.join(RESULTS_DIR, f"{probe_name}.json")
    if not os.path.exists(path):
        print(f"No results found for '{probe_name}' at {path}")
        return []
    results = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    results.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return results


def list_probes():
    """List all probes with saved results and record counts."""
    if not os.path.exists(RESULTS_DIR):
        print(f"No results directory at {RESULTS_DIR}")
        return []
    probes = [f.replace(".json","") for f in os.listdir(RESULTS_DIR)
              if f.endswith(".json")]
    for name in sorted(probes):
        path = os.path.join(RESULTS_DIR, f"{name}.json")
        n    = sum(1 for line in open(path) if line.strip())
        print(f"  {name}: {n} records")
    return probes


def clear_probe(probe_name):
    """Delete saved results for a probe (asks confirmation)."""
    path = os.path.join(RESULTS_DIR, f"{probe_name}.json")
    if os.path.exists(path):
        confirm = input(f"Delete all results for '{probe_name}'? (yes/no): ")
        if confirm.strip().lower() == "yes":
            os.remove(path)
            print(f"Cleared.")
        else:
            print("Cancelled.")
    else:
        print(f"No file found for '{probe_name}'.")


# ==============================================================
# VERSION INFO
# ==============================================================

VERSION = "v40.4"
CONDENSATION_THRESHOLD_N = 24
ETA_C_SCALING = -0.86   # eta_c(N) ~ N^ETA_C_SCALING

# v40.4 confirmed operating invariants (beta=0.045, gamma=0.15)
STD_SPECABS      = -0.017   # J_12 spectral abscissa (mean across N=24-36)
STD_COS_THETA    =  0.663   # causal alignment (emergent)
STD_CURV_SOC     =  0.663   # sector balance ratio
STD_RGAMMA       =  0.024   # curvature self-regulation product
BETA_C_BASE      =  0.080   # PERP boundary at base gamma (N=24-30)
BETA_NAV_RANGE   = (0.045, 0.085)  # STD → PERP navigation corridor


if __name__ == "__main__":
    print(f"ECFM Engine Module {VERSION}")
    print(f"Condensation threshold: N >= {CONDENSATION_THRESHOLD_N}")
    print(f"Phase boundary scaling: eta_c ~ N^{ETA_C_SCALING}")
    print(f"Beta setpoint: {PARAMS['beta']}  (navigation ceiling: {BETA_C_BASE})")
    print()

    # smoke test
    print("Smoke test at N=28, eta=0.75, seed=0...")
    A, states, flows = evolve(28, seed=0, eta=0.75, steps=300)
    obs = observables_fast(A)
    print(f"  tau   = {obs['tau']:.5f}  [{obs['phase']}]")
    print(f"  d_eff = {obs['d_eff']:.4f}")
    print(f"  ||F|| = {obs['norm_F']:.5f}")
    print(f"  late states: {len(states)}")
    print()
    print("Full observables (includes grad_tau)...")
    obs_full = observables(A)
    print(f"  cos_theta = {obs_full['cos_theta']:+.5f}")
    print(f"  r         = {obs_full['r']:.5f}")
    print()
    print("Engine module OK.")
