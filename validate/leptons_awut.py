#!/usr/bin/env python3
import json, argparse, math, sys
from pathlib import Path

def E_of_R(R, Ks, Ck, CL, g, lam0, xi):
    # E(R) = Ks*Ck/R + CL*R + g*|xi|^2 / (2R - lam0)^2
    denom = (2.0*R - lam0)
    if denom == 0.0:
        return float("inf")
    return Ks*Ck/R + CL*R + g*(xi*xi)/(denom*denom)

def dE_dR(R, Ks, Ck, CL, g, lam0, xi):
    # dE/dR = -Ks*Ck/R^2 + CL - g * d/dR[ |xi|^2 / (2R - lam0)^2 ]
    # d/dR( (2R - lam0)^{-2} ) = -4 (2R - lam0)^{-3}
    denom = (2.0*R - lam0)
    if denom == 0.0:
        return float("inf")
    return -Ks*Ck/(R*R) + CL - g*((xi*xi)*(-4.0)/(denom**3))

def find_stationary_R(Ks, Ck, CL, g, lam0, xi, Rmin, Rmax, tol=1e-12, maxit=200):
    # Simple robust bracket+bisect on dE/dR = 0
    a, b = Rmin, Rmax
    fa = dE_dR(a, Ks, Ck, CL, g, lam0, xi)
    fb = dE_dR(b, Ks, Ck, CL, g, lam0, xi)
    if math.isnan(fa) or math.isnan(fb):
        return None
    # Expand bracket if same sign
    expand = 0
    while fa*fb > 0 and expand < 20:
        a = max(1e-18, a*0.5)
        b = b*1.5
        fa = dE_dR(a, Ks, Ck, CL, g, lam0, xi)
        fb = dE_dR(b, Ks, Ck, CL, g, lam0, xi)
        expand += 1
    if fa*fb > 0:
        return None
    for _ in range(maxit):
        m = 0.5*(a+b)
        fm = dE_dR(m, Ks, Ck, CL, g, lam0, xi)
        if abs(fm) < tol:
            return m
        if fa*fm <= 0:
            b, fb = m, fm
        else:
            a, fa = m, fm
    return 0.5*(a+b)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cfg", default=str(Path(__file__).resolve().parents[1]/"config.json"))
    p.add_argument("--out", default=str(Path(__file__).resolve().parents[1]/"results"/"lepton_ratios.json"))
    args = p.parse_args()

    CFG = json.load(open(args.cfg))
    const = CFG.get("awut_constants", {})
    Ks = const.get("K_s", None)
    Ck = const.get("C_kappa", None)
    CL = const.get("C_L", None)
    g  = const.get("g", None)
    lam0 = const.get("lambda0", None)
    xi0  = const.get("xi0", None)

    required = [Ks, Ck, CL, g, lam0, xi0]
    if any(v is None for v in required):
        print("[ERROR] Missing AWUT constants in config.json -> 'awut_constants' block.", file=sys.stderr)
        print("Please fill K_s, C_kappa, C_L, g, lambda0, xi0 from the paper and re-run.", file=sys.stderr)
        # Write a diagnostic JSON so scorecard can show SKIP instead of failing hard
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump({"status":"MISSING_CONSTANTS"}, f, indent=2)
        sys.exit(2)

    # Mode labels (can be adjusted if your selection rule differs)
    modes = {"e":1, "mu":2, "tau":3}
    results = {"status":"OK", "constants_used": const, "modes": modes, "stationary_points": {}, "ratios": {}}

    # Solve for stationary R for each mode, compute E(R_n), ratios relative to electron
    # We don't need absolute mass scale; ratios are E_n / E_e
    Rmin, Rmax = 1e-6, 1e6
    Es = {}
    for name, n in modes.items():
        xi = n*xi0
        Rstar = find_stationary_R(Ks, Ck, CL, g, lam0, xi, Rmin, Rmax)
        if Rstar is None or not math.isfinite(Rstar):
            results["status"] = "NO_STATIONARY"
            results["stationary_points"][name] = None
            Es[name] = None
            continue
        results["stationary_points"][name] = Rstar
        Es[name] = E_of_R(Rstar, Ks, Ck, CL, g, lam0, xi)

    if any(v is None for v in Es.values()):
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print("[WARN] Could not find stationary points for all modes. Wrote partial results.")
        sys.exit(1)

    Ee = Es["e"]
    results["ratios"]["mu_over_e"]  = Es["mu"]/Ee
    results["ratios"]["tau_over_e"] = Es["tau"]/Ee

    # Compare against targets (reporting only; no fitting)
    targets = CFG.get("targets", {})
    mu_ref = targets.get("mu_over_e", 206.7682830)
    tau_ref = targets.get("tau_over_e", 3477.48)

    mu_err = abs(results["ratios"]["mu_over_e"]-mu_ref)/mu_ref
    tau_err = abs(results["ratios"]["tau_over_e"]-tau_ref)

    results["compare"] = {
        "mu_over_e": {"awut": results["ratios"]["mu_over_e"], "ref": mu_ref, "rel_err": mu_err},
        "tau_over_e": {"awut": results["ratios"]["tau_over_e"], "ref": tau_ref, "rel_err": tau_err}
    }

    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        json.dump(results, f, indent=2)
    print("Wrote", args.out)

if __name__ == "__main__":
    main()
