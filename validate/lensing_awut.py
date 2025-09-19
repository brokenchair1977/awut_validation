#!/usr/bin/env python3
import argparse, csv, json, math
from pathlib import Path

def load_pairs(path):
    names, v, a = [], [], []
    with open(path, newline="") as f:
        rdr = csv.DictReader(f)
        for r in rdr:
            names.append(r["name"]); v.append(float(r["v_flat_kms"])); a.append(float(r["alpha_arcsec"]))
    return names, v, a

def pearson(x, y):
    n = len(x)
    if n<2: return None
    mx = sum(x)/n; my = sum(y)/n
    sx = math.sqrt(sum((xi-mx)**2 for xi in x)/n)
    sy = math.sqrt(sum((yi-my)**2 for yi in y)/n)
    if sx==0 or sy==0: return None
    return sum((xi-mx)*(yi-my) for xi,yi in zip(x,y))/ (n*sx*sy)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default="data/lensing/pairs.csv")
    ap.add_argument("--cfg", default="config.json")
    ap.add_argument("--out", default="results/lensing.json")
    args = ap.parse_args()

    names, v, a = load_pairs(args.data)
    r = pearson(v, a)
    out = {"status":"OK","pearson_r":r,"n":len(v)}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    json.dump(out, open(args.out,"w"), indent=2)
    print("Wrote", args.out)

if __name__=="__main__":
    main()
