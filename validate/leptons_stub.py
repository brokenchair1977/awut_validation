#!/usr/bin/env python3
import json, argparse
p = argparse.ArgumentParser()
p.add_argument("--out", required=True)
a = p.parse_args()
data = {"rmu_over_re":{"mean":206.77,"sigma":0.8},
        "rtau_over_re":{"mean":3477.2,"sigma":16.0}}
with open(a.out,"w") as f: json.dump(data,f,indent=2)
print("Wrote", a.out)
