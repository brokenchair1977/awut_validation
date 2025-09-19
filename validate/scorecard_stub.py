#!/usr/bin/env python3
import json, csv, argparse
from pathlib import Path
p = argparse.ArgumentParser()
p.add_argument("--cfg", required=True)
a = p.parse_args()
CFG = json.load(open(a.cfg))

rows = []
# Leptons
lep = Path(CFG["outputs"]["leptons_json"])
if lep.exists():
    L = json.load(open(lep))
    rmu = L["rmu_over_re"]["mean"]; rtau = L["rtau_over_re"]["mean"]
    mu_ref = 206.7682830; tau_ref = 3477.15
    mu_err = abs(rmu-mu_ref)/mu_ref; tau_err = abs(rtau-tau_ref)/tau_ref
    rows += [["Particle","μ/e mass ratio",f"{rmu:.6f}",mu_ref,mu_err,"PASS" if mu_err<=CFG["thresholds"]["lepton_ratio_relerr_strict"] else "FAIL"],
             ["Particle","τ/e mass ratio",f"{rtau:.2f}",tau_ref,tau_err,"PASS" if tau_err<=CFG["thresholds"]["lepton_ratio_relerr_strict"] else "FAIL"]]
else:
    rows += [["Particle","μ/e mass ratio","—","206.7682830","—","SKIP"],
             ["Particle","τ/e mass ratio","—","3477.15","—","SKIP"]]

# SPARC
sparc = Path(CFG["outputs"]["sparc_json"])
if sparc.exists():
    S = json.load(open(sparc))
    r2s = [g["R2"] for g in S.get("galaxies",[]) if "R2" in g]
    R2_mean = sum(r2s)/len(r2s) if r2s else float("nan")
    rows.append(["Cosmology","SPARC mean R²", f"{R2_mean:.3f}","≥0.90","PASS" if R2_mean>=CFG["thresholds"]["sparc_r2_mean_pass"] else "FAIL"])
else:
    rows.append(["Cosmology","SPARC mean R²","—","≥0.90","SKIP"])

# CMB
cmb = Path(CFG["outputs"]["cmb_json"])
if cmb.exists():
    C = json.load(open(cmb))
    dchi2 = C.get("delta_chi2_vs_zero", None)
    rows.append(["Cosmology","CMB low-ℓ Δχ²", f"{dchi2:.2f}","≤ -6.0","PASS" if dchi2 is not None and dchi2<=CFG["thresholds"]["cmb_dchi2_pass"] else "FAIL"])
else:
    rows.append(["Cosmology","CMB low-ℓ Δχ²","—","≤ -6.0","SKIP"])

# BH
bh = Path(CFG["outputs"]["bh_json"])
if bh.exists():
    B = json.load(open(bh))
    c_mean = B.get("c_mean", None)
    lo = CFG["thresholds"]["bh_c_target"]-CFG["thresholds"]["bh_c_tol"]
    hi = CFG["thresholds"]["bh_c_target"]+CFG["thresholds"]["bh_c_tol"]
    rows.append(["GR","BH entropy coeff c", f"{c_mean:.4f}","0.25±0.02","PASS" if (c_mean is not None and lo<=c_mean<=hi) else "FAIL"])
else:
    rows.append(["GR","BH entropy coeff c","—","0.25±0.02","SKIP"])

out = Path(CFG["outputs"]["scorecard_csv"])
out.parent.mkdir(exist_ok=True, parents=True)
with open(out, "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Domain","Test","AWUT","Target","Result"])
    for r in rows: w.writerow(r)
print("Wrote", out)
