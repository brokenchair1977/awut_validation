# AWUT — Paint‑By‑Numbers Starter (6 real checks)

Run from repo root:

```bash
python3 validate/run_all.py
```

**What it does (no tuning):**
- Leptons mass ratios (e, μ, τ) from AWUT constants in `config.json`
- Galaxy rotation curves using your NGC `*_rotmod.dat` files
- Hydrogen spectra (Lyman/Balmer lines)
- CMB low‑ℓ suppression (sample CSV structure)
- Lensing vs v_flat correlation (CSV structure)
- Black‑hole entropy 1/4 coefficient

Edit just once: `config.json` — set:
```json
{
  "awut_constants": {"K_s": ..., "C_kappa": ..., "C_L": ..., "g": ..., "lambda0": ..., "xi0": ...},
  "rotation_curves": {"V0_global": 120.0},
  "atomic": {"R_infinity_per_m": 10973731.568160},
  "cmb": {"Lc_lowell": 8.0}
}
```

Data locations:
- `data/galaxies/` — your uploaded NGC files (already included if you provided them)
- `data/atomic/hydrogen_lines_ref.csv`
- `data/cmb/planck_lowell_tt.csv`
- `data/lensing/pairs.csv`
