#!/usr/bin/env python3
import argparse, csv, json, math
from pathlib import Path

def load_lowell(path):
    L, C, S = [], [], []
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            L.append(int(r["ell"])); C.append(float(r["C_ell"])); S.append(float(r["sigma"]))
    return L, C, S

def awut_suppressed(C, L, Lc):
    # simple exponential damping vs ell/Lc (fixed one-parameter form)
    return [ c*math.exp(-ell/ Lc) for c,ell in zip(C,L) ]

def chi2(obs, mod, sig):
    return sum(((o-m)/s)**2 for o,m,s in zip(obs,mod,sig) if s>0)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/cmb/planck_lowell_tt.csv")
    ap.add_argument("--cfg", default="config.json")
    ap.add_argument("--out", default="results/cmb_lowell.json")
    args = ap.parse_args()

    L, C, S = load_lowell(args.data)
    try:
        CFG = json.load(open(args.cfg))
        Lc = CFG.get("cmb", {}).get("Lc_lowell", 8.0)
    except Exception:
        Lc = 8.0

    model = awut_suppressed(C, L, Lc)
    # baseline = no suppression (identity)
    baseline = C[:]

    chi2_model = chi2(C, model, S)
    chi2_base  = chi2(C, baseline, S)
    out = {"status":"OK","Lc":Lc,"chi2_model":chi2_model,"chi2_baseline":chi2_base,"delta_chi2":chi2_model - chi2_base}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.out,"w"), indent=2)
    print("Wrote", args.out)

if __name__=="__main__":
    main()
