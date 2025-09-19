#!/usr/bin/env python3
import subprocess, sys, json
from pathlib import Path

def run(cmd):
    print("+", " ".join(cmd))
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT).decode()
    except subprocess.CalledProcessError as e:
        out = e.output.decode()
    print(out)

def main():
    here = Path(".").resolve()
    cfg = str(here/"config.json")
    (here/"results").mkdir(exist_ok=True)

    run([sys.executable, "validate/leptons_awut.py", "--cfg", cfg, "--out", "results/lepton_ratios.json"])
    run([sys.executable, "validate/rotation_curves_awut.py", "--data", "data/galaxies", "--cfg", cfg, "--out", "results/rotcurves_summary.json"])
    run([sys.executable, "validate/hydrogen_spectra_awut.py", "--cfg", cfg, "--data", "data/atomic/hydrogen_lines_ref.csv", "--out", "results/hydrogen_lines.json"])
    run([sys.executable, "validate/cmb_lowell_awut.py", "--cfg", cfg, "--data", "data/cmb/planck_lowell_tt.csv", "--out", "results/cmb_lowell.json"])
    run([sys.executable, "validate/lensing_awut.py", "--cfg", cfg, "--data", "data/lensing/pairs.csv", "--out", "results/lensing.json"])
    run([sys.executable, "validate/bh_entropy_awut.py", "--out", "results/bh_entropy.json"])

if __name__=="__main__":
    main()
