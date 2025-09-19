#!/usr/bin/env python3
import json, argparse, math
from pathlib import Path

def E_of_R(R, Ks, Ck, CL, g, lam0, xi):
    denom = (2.0*R - lam0)
    if denom == 0.0:
        return float("inf")
    return Ks*Ck/R + CL*R + g*(xi*xi)/(denom*denom)

def dE_dR(R, Ks, Ck, CL, g, lam0, xi):
    denom = (2.0*R - lam0)
    if denom == 0.0:
        return float("inf")
    return -Ks*Ck/(R*R) + CL - g*((xi*xi)*(-4.0)/(denom**3))

def find_stationary_R(Ks, Ck, CL, g, lam0, xi, Rmin=1e-6, Rmax=1e6, tol=1e-12, maxit=200):
    a, b = Rmin, Rmax
    fa = dE_dR(a, Ks, Ck, CL, g, lam0, xi)
    fb = dE_dR(b, Ks, Ck, CL, g, lam0, xi)
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
    ap = argparse.ArgumentParser()
    ap.add_argument("--cfg", default="config.json")
    ap.add_argument("--out", default="results/lepton_ratios.json")
    args = ap.parse_args()

    CFG = json.load(open(args.cfg))
    const = CFG.get("awut_constants", {})
    Ks = const.get("K_s")
    Ck = const.get("C_kappa")
    CL = const.get("C_L")
    g  = const.get("g")
    lam0 = const.get("lambda0")
    xi0  = const.get("xi0")

    missing = [k for k,v in {"K_s":Ks,"C_kappa":Ck,"C_L":CL,"g":g,"lambda0":lam0,"xi0":xi0}.items() if v is None]
    if missing:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"status":"MISSING_CONSTANTS","missing":missing}, open(args.out,"w"), indent=2)
        print("[ERROR] Missing constants:", ",".join(missing)); return

    modes = {"e":1, "mu":2, "tau":3}
    Es, Rstar = {}, {}
    for name, n in modes.items():
        xi = n*xi0
        R_ = find_stationary_R(Ks, Ck, CL, g, lam0, xi)
        Rstar[name] = R_
        if R_ is None or not math.isfinite(R_):
            Es[name] = None
        else:
            Es[name] = E_of_R(R_, Ks, Ck, CL, g, lam0, xi)

    results = {"status":"OK", "Rstar":Rstar, "E":Es}
    if None in Es.values():
        results["status"]="FAIL_STATIONARY"
    else:
        Ee = Es["e"]
        results["ratios"] = {
            "mu_over_e": Es["mu"]/Ee,
            "tau_over_e": Es["tau"]/Ee
        }
    json.dump(results, open(args.out,"w"), indent=2)
    print("Wrote", args.out)

if __name__=="__main__":
    main()
