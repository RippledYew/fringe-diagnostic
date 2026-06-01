"""
ecfm_runner.py — Orchestrator Interface for ECFM Engine
========================================================
Thin wrapper around Ecfm_Engine.py that exposes a standard
probe entry point for automated pipeline use.

The engine (Ecfm_Engine.py) remains frozen and untouched.

Calibrated against: ECFM Research Report v3.6 (engine v40.4)

To run a smoke test directly in Pydroid:
    python ecfm_runner.py

To run with a config (CLI / orchestrator):
    python ecfm_runner.py --inline '{"probe_id":"p001","N":28,"eta":0.75,"seed":0}'
    python ecfm_runner.py --config probe_config.json
    python ecfm_runner.py --batch batch.json
"""

import sys
import os

# Pydroid runs via exec() so __file__ resolves incorrectly.
# Hardcode emulated storage root where both files live.
sys.path.insert(0, "/home/ripple/python/ecfm/")

import json
import argparse
import datetime
import traceback
import numpy as np

import Ecfm_Engine as engine


# ==============================================================
# RESULTS DIRECTORY
# ==============================================================

def _default_results_dir():
    if os.path.exists("/sdcard"):
        return "/sdcard/ecfm_results"
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), "ecfm_results")

RESULTS_DIR = os.environ.get("ECFM_RESULTS_DIR", _default_results_dir())


# ==============================================================
# JSON SERIALIZER
# Handles numpy types that Python's json encoder can't handle.
# ==============================================================

def _json_safe(obj):
    """Convert numpy/non-serializable types to Python natives."""
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.bool_):
        return bool(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    raise TypeError(f"Not serializable: {type(obj)}")


# ==============================================================
# CALIBRATED INVARIANT TOLERANCES
# Source: ECFM Research Report v3.6, engine v40.4
#
# Protected invariant: CURV/SOC sector norm ratio (CV=0.011)
# NOT R×gamma — that drifts under d1_amp (CV=0.087)
# ==============================================================

STD_COS_THETA_LO  = 0.58    # Section X.1: +0.62 to +0.73 geometric regime
STD_COS_THETA_HI  = 0.92    # up to 0.912 post-bounded-divergence near FP
PERP_COS_THETA_LO = -0.10   # PERP FP measured at 0.034
PERP_COS_THETA_HI =  0.10
DEG_COS_THETA_LO  = -0.80   # DEG attractor: -0.67 to -0.71 with margin
DEG_COS_THETA_HI  = -0.55
CURV_SOC_LO       = 0.640   # Protected ratio locked 0.663-0.685 (CV=0.011)
CURV_SOC_HI       = 0.710
PERP_R_LO         = 0.285   # PERP adiabatic invariant R≈0.30 (CV=0.00223)
PERP_R_HI         = 0.315
TAU_STD_MIN       = 0.980   # STD attractor ~0.999 late-traj; margin for early runs
TAU_PERP_MIN      = 0.985
BETA_C            = engine.BETA_C_BASE


# ==============================================================
# REGIME CLASSIFIER
# Three attractors: STD / PERP / DEG
# Dominance hierarchy: DEG > PERP > STD (Section II.4)
# ==============================================================

def classify_regime(obs: dict) -> str:
    cos_t = obs.get("cos_theta")
    tau   = obs.get("tau")
    phase = obs.get("phase", "")

    if cos_t is None or tau is None:
        return "UNKNOWN"

    if phase == "DECOHERED" or tau < 0.70:
        return "DECOHERED"

    if DEG_COS_THETA_LO <= cos_t <= DEG_COS_THETA_HI:
        return "DEG"

    if PERP_COS_THETA_LO <= cos_t <= PERP_COS_THETA_HI and tau >= TAU_PERP_MIN:
        return "PERP"

    if STD_COS_THETA_LO <= cos_t <= STD_COS_THETA_HI and tau >= TAU_STD_MIN:
        return "STD"

    if 0.10 < cos_t < STD_COS_THETA_LO:
        return "BOUNDARY"

    return "UNKNOWN"


# ==============================================================
# CURV/SOC RATIO — the protected structural invariant
# ==============================================================

def curv_soc_ratio(A) -> float:
    sectors = engine.engine_sectors(A)
    norm_curv = float(np.linalg.norm(sectors["CURV"]))
    norm_soc  = float(np.linalg.norm(sectors["SOC"]))
    if norm_soc < 1e-12:
        return float("inf")
    return norm_curv / norm_soc


# ==============================================================
# INVARIANT CHECKER
# ==============================================================

def check_invariants(obs: dict, regime: str, A=None) -> dict:
    checks = {}
    flags  = []
    fails  = []

    cos_t  = obs.get("cos_theta")
    tau    = obs.get("tau")
    norm_F = obs.get("norm_F")
    phase  = obs.get("phase", "")
    R      = obs.get("R")

    # tau vs phase consistency
    if tau is not None:
        ok = (
            (tau > 0.95  and phase == "CONDENSATE") or
            (0.70 < tau <= 0.95 and phase == "CORE") or
            (tau <= 0.70 and phase == "DECOHERED")
        )
        checks["tau_phase_consistent"] = {"tau": float(tau), "phase": phase, "pass": bool(ok)}
        if not ok:
            fails.append(f"tau={tau:.4f} inconsistent with phase label '{phase}'")

    # cos_theta in expected range for regime
    if cos_t is not None:
        if regime == "STD":
            ok = STD_COS_THETA_LO <= cos_t <= STD_COS_THETA_HI
            checks["cos_theta_std_range"] = {
                "value": float(cos_t), "range": [STD_COS_THETA_LO, STD_COS_THETA_HI], "pass": bool(ok)
            }
            if not ok:
                flags.append(f"cos_theta={cos_t:.4f} outside STD range")

        elif regime == "PERP":
            ok = PERP_COS_THETA_LO <= cos_t <= PERP_COS_THETA_HI
            checks["cos_theta_perp_near_zero"] = {
                "value": float(cos_t), "range": [PERP_COS_THETA_LO, PERP_COS_THETA_HI], "pass": bool(ok)
            }
            if not ok:
                fails.append(f"PERP regime but cos_theta={cos_t:.4f} not near zero")

        elif regime == "DEG":
            ok = DEG_COS_THETA_LO <= cos_t <= DEG_COS_THETA_HI
            checks["cos_theta_deg_range"] = {
                "value": float(cos_t), "range": [DEG_COS_THETA_LO, DEG_COS_THETA_HI], "pass": bool(ok)
            }
            if not ok:
                flags.append(f"DEG regime but cos_theta={cos_t:.4f} outside DEG band")

    # PERP adiabatic invariant R ≈ 0.30
    if regime == "PERP" and R is not None:
        ok = PERP_R_LO <= R <= PERP_R_HI
        checks["perp_R_invariant"] = {
            "value": float(R), "expected": 0.300, "range": [PERP_R_LO, PERP_R_HI], "pass": bool(ok)
        }
        if not ok:
            flags.append(f"PERP regime but R={R:.4f} not locked near 0.30")

    # CURV/SOC protected ratio (STD phase, requires A)
    if regime == "STD" and A is not None:
        try:
            ratio = curv_soc_ratio(A)
            ok = CURV_SOC_LO <= ratio <= CURV_SOC_HI
            checks["curv_soc_ratio"] = {
                "value": float(ratio),
                "range": [CURV_SOC_LO, CURV_SOC_HI],
                "pass": bool(ok),
                "note": "Protected invariant — sector norm ratio, not R×gamma"
            }
            if not ok:
                flags.append(f"CURV/SOC={ratio:.4f} outside locked range")
        except Exception as e:
            checks["curv_soc_ratio"] = {"error": str(e), "pass": None}

    # norm_F sanity (DEG handled separately)
    if norm_F is not None:
        if regime == "DEG":
            sane = norm_F > 1e3
            checks["norm_F_deg_large"] = {
                "value": float(norm_F), "note": "DEG norm_F expected ~6.7e6", "pass": bool(sane)
            }
        else:
            sane = 1e-8 < norm_F < 1e4
            checks["norm_F_sane"] = {"value": float(norm_F), "pass": bool(sane)}
            if not sane:
                fails.append(f"norm_F={norm_F:.4e} out of sane range for regime={regime}")

    # beta margin from third boundary
    beta_current = float(engine.PARAMS["beta"])
    beta_margin  = float(BETA_C) - beta_current
    checks["beta_margin"] = {
        "beta": beta_current, "beta_c": float(BETA_C),
        "margin": float(beta_margin), "pass": bool(beta_margin > 0)
    }
    if beta_margin <= 0:
        fails.append(f"beta={beta_current} at or above beta_c={BETA_C}")

    status = "fail" if fails else ("flag" if flags else "pass")
    return {"status": status, "checks": checks, "flags": flags, "fails": fails}


# ==============================================================
# ESCALATION LOGIC
# ==============================================================

ESCALATION_TRIGGERS = [
    "not near zero",
    "out of sane range",
    "inconsistent with phase label",
    "at or above beta_c",
]

def should_escalate(invariant_report: dict, regime: str) -> tuple:
    reasons = []
    if invariant_report["status"] == "fail":
        reasons.extend(invariant_report["fails"])
    if regime == "UNKNOWN":
        reasons.append("Regime could not be classified — novel behavior or parameter edge")
    for flag in invariant_report.get("flags", []):
        for trigger in ESCALATION_TRIGGERS:
            if trigger.lower() in flag.lower():
                reasons.append(f"Escalation trigger: {flag}")
                break
    return (len(reasons) > 0, reasons)


# ==============================================================
# CORE PROBE RUNNER
# ==============================================================

def run_probe(config: dict) -> dict:
    """
    Execute a single ECFM probe from a config dict.

    Config keys:
        probe_id       (str)   — unique identifier
        probe_name     (str)   — probe family name for grouping
        N              (int)   — system size (default: 28)
        seed           (int)   — random seed (default: 0)
        eta            (float) — initialization amplitude (default: 0.75)
        steps          (int)   — integration steps (default: 400)
        fast           (bool)  — use observables_fast (default: False)
        check_curv_soc (bool)  — compute CURV/SOC ratio check (default: True)
        save           (bool)  — persist result to JSON (default: True)
        notes          (str)   — optional annotation
    """
    probe_id       = config.get("probe_id",       "unset")
    probe_name     = config.get("probe_name",     "default")
    N              = int(config.get("N",          28))
    seed           = int(config.get("seed",       0))
    eta            = float(config.get("eta",      0.75))
    steps          = int(config.get("steps",      400))
    fast           = bool(config.get("fast",      False))
    check_curv_soc = bool(config.get("check_curv_soc", True))
    save           = bool(config.get("save",      True))
    notes          = config.get("notes", "")

    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()

    result = {
        "probe_id":           probe_id,
        "probe_name":         probe_name,
        "engine_version":     engine.VERSION,
        "timestamp":          timestamp,
        "config":             {"N": N, "seed": seed, "eta": eta, "steps": steps, "fast": fast},
        "engine_params":      {k: float(v) if hasattr(v, '__float__') else v
                               for k, v in engine.PARAMS.items()},
        "observables":        None,
        "regime":             None,
        "invariant_check":    None,
        "escalate":           False,
        "escalation_reasons": [],
        "status":             "pending",
        "error":              None,
        "notes":              notes,
    }

    try:
        A, late_states, late_flows = engine.evolve(N, seed=seed, eta=eta, steps=steps)

        obs = engine.observables_fast(A) if fast else engine.observables(A)
        result["observables"] = {
            k: float(v) if isinstance(v, (float, np.floating)) else
               bool(v)  if isinstance(v, (bool, np.bool_))    else
               int(v)   if isinstance(v, (int, np.integer))   else v
            for k, v in obs.items()
        }

        regime = classify_regime(obs)
        result["regime"] = regime

        A_for_check = A if check_curv_soc else None
        inv = check_invariants(obs, regime, A=A_for_check)
        result["invariant_check"] = inv

        escalate, reasons = should_escalate(inv, regime)
        result["escalate"]           = escalate
        result["escalation_reasons"] = reasons
        result["status"] = "complete"

    except Exception as exc:
        result["status"] = "error"
        result["error"]  = traceback.format_exc()
        result["escalate"] = True
        result["escalation_reasons"] = [f"Runtime exception: {str(exc)}"]

    if save:
        os.makedirs(RESULTS_DIR, exist_ok=True)
        path = os.path.join(RESULTS_DIR, f"{probe_name}.json")
        with open(path, "a") as f:
            json.dump(result, f, default=_json_safe)
            f.write("\n")

    return result


# ==============================================================
# BATCH RUNNER
# ==============================================================

def run_batch(configs: list, stop_on_escalate: bool = False) -> list:
    results = []
    for cfg in configs:
        r = run_probe(cfg)
        results.append(r)
        if stop_on_escalate and r.get("escalate"):
            print(f"[ESCALATE] Batch halted at probe_id={r['probe_id']}")
            for reason in r["escalation_reasons"]:
                print(f"  - {reason}")
            break
    return results


# ==============================================================
# RESULT SUMMARY
# ==============================================================

def summarize(result: dict) -> str:
    pid    = result.get("probe_id", "?")
    status = result.get("status",   "?")
    regime = result.get("regime",   "?")
    obs    = result.get("observables") or {}
    inv    = result.get("invariant_check") or {}
    esc    = result.get("escalate", False)

    tau   = obs.get("tau",       float("nan"))
    cos_t = obs.get("cos_theta", float("nan"))
    phase = obs.get("phase",     "?")
    inv_status = inv.get("status", "?")
    esc_marker = " *** ESCALATE ***" if esc else ""

    cs_check = inv.get("checks", {}).get("curv_soc_ratio", {})
    cs_str = ""
    if cs_check and cs_check.get("value") is not None:
        cs_str = f" | CURV/SOC={cs_check['value']:.3f}"

    return (
        f"[{pid}] {status} | regime={regime} | phase={phase} | "
        f"tau={tau:.4f} | cos_theta={cos_t:+.4f}{cs_str} | "
        f"inv={inv_status}{esc_marker}"
    )


# ==============================================================
# ENTRY POINT
# Run directly in Pydroid → smoke test
# Run with args → CLI mode
# ==============================================================

def _cli():
    parser = argparse.ArgumentParser(description="ECFM Probe Runner")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--config", help="Path to JSON config file")
    group.add_argument("--batch",  help="Path to JSON array of configs")
    group.add_argument("--inline", help="Inline JSON config string")
    parser.add_argument("--stop-on-escalate", action="store_true")
    args = parser.parse_args()

    if args.config:
        with open(args.config) as f:
            config = json.load(f)
        result = run_probe(config)
        print(summarize(result))
        if result.get("escalate"):
            for r in result["escalation_reasons"]:
                print(f"  - {r}")

    elif args.batch:
        with open(args.batch) as f:
            configs = json.load(f)
        results = run_batch(configs, stop_on_escalate=args.stop_on_escalate)
        for r in results:
            print(summarize(r))

    elif args.inline:
        config = json.loads(args.inline)
        result = run_probe(config)
        print(json.dumps(result, indent=2))


def _smoke_test():
    print("Running smoke test: N=28, eta=0.75, seed=0, steps=400")
    r = run_probe({"probe_id": "smoke_01", "probe_name": "smoke", "N": 28,
                   "eta": 0.75, "seed": 0, "steps": 400})
    print(summarize(r))
    if r.get("escalate"):
        print("Escalation reasons:")
        for reason in r["escalation_reasons"]:
            print(f"  - {reason}")


if __name__ == "__main__":
    # No args = smoke test (Pydroid direct run)
    # Args present = CLI mode (orchestrator)
    if len(sys.argv) > 1:
        _cli()
    else:
        _smoke_test()
