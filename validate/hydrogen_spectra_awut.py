#!/usr/bin/env python3
import argparse, json, math, csv
from pathlib import Path

def load_ref_csv(path):
    rows = []
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            rows.append({"series":r["series"], "n":int(r["n"]), "lambda_nm":float(r["lambda_nm"])})
    return rows

def rydberg_lambda(n, series="Lyman", R=10973731.568160):
    if series.lower()=="lyman":
        inv_m = R*(1.0 - 1.0/(n*n))
    elif series.lower()=="balmer":
        inv_m = R*((1.0/4.0) - 1.0/(n*n))
    else:
        inv_m = R*((1.0/9.0) - 1.0/(n*n))
    lam_m = 1.0/inv_m
    return lam_m*1e9

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/atomic/hydrogen_lines_ref.csv")
    ap.add_argument("--cfg", default="config.json")
    ap.add_argument("--out", default="results/hydrogen_lines.json")
    args = ap.parse_args()

    try:
        CFG = json.load(open(args.cfg)); R = CFG.get("atomic", {}).get("R_infinity_per_m", 10973731.568160)
    except Exception: R = 10973731.568160

    ref = load_ref_csv(args.data)
    results = {"status":"OK","R_infinity_per_m":R,"lines":[]}
    for r in ref:
        lam_pred = rydberg_lambda(r["n"], series=r["series"], R=R)
        lam_ref  = r["lambda_nm"]
        err = abs(lam_pred - lam_ref)/lam_ref
        results["lines"].append({"series":r["series"],"n":r["n"],"lambda_nm_ref":lam_ref,"lambda_nm_awut":lam_pred,"rel_error":err})
    if results["lines"]:
        errs = [x["rel_error"] for x in results["lines"]]
        results["summary"] = {"mean_rel_error": sum(errs)/len(errs), "max_rel_error": max(errs)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(results, open(args.out,"w"), indent=2)
    print("Wrote", args.out)

if __name__=="__main__":
    main()
