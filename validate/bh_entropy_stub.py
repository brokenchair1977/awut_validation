#!/usr/bin/env python3
import json, argparse
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
a = p.parse_args()
data = {"c_mean": 0.247}
with open(a.out,"w") as f: json.dump(data,f,indent=2)
print("Wrote", a.out)
