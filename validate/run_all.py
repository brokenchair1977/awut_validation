#!/usr/bin/env python3
import json, sys, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CFG = json.load(open(ROOT/"config.json"))

def run(py, *args):
    cmd = [sys.executable, str(py)] + list(args)
    print(">>", " ".join(cmd))
    return subprocess.call(cmd)

def main():
    (ROOT/"results").mkdir(exist_ok=True)
    (ROOT/"figs").mkdir(exist_ok=True)

    run(Path(__file__).parent/"leptons_stub.py",
        "--out", str((ROOT/CFG["outputs"]["leptons_json"]).resolve()))

    sparc = ROOT/CFG["datasets"]["sparc_csv"]
    if sparc.exists():
        run(Path(__file__).parent/"sparc_stub.py",
            "--sparc_csv", str(sparc.resolve()),
            "--out", str((ROOT/CFG["outputs"]["sparc_json"]).resolve()))
    else:
        print("[WARN] Missing SPARC CSV, skipping rotation curves.")

    cmb = ROOT/CFG["datasets"]["planck_lowell_csv"]
    if cmb.exists():
        run(Path(__file__).parent/"cmb_stub.py",
            "--planck_lowell_csv", str(cmb.resolve()),
            "--out", str((ROOT/CFG["outputs"]["cmb_json"]).resolve()))
    else:
        print("[WARN] Missing Planck low-ℓ TT CSV, skipping CMB.")

    run(Path(__file__).parent/"bh_entropy_stub.py",
        "--out", str((ROOT/CFG["outputs"]["bh_json"]).resolve()))

    run(Path(__file__).parent/"scorecard_stub.py",
        "--cfg", str((ROOT/"config.json").resolve()))

if __name__ == "__main__":
    main()
