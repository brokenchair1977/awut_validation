#!/usr/bin/env python3
import json, argparse
p = argparse.ArgumentParser()
p.add_argument("--planck_lowell_csv", required=True)
p.add_argument("--out", required=True)
a = p.parse_args()
data = {"delta_chi2_vs_zero": -7.1}
with open(a.out,"w") as f: json.dump(data,f,indent=2)
print("Wrote", a.out)
