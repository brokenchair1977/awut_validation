#!/usr/bin/env python3
import argparse, json, os, math, csv, glob
from pathlib import Path

def read_rotmod_any(path):
    R, Vobs, Verr, Vgas, Vdisk, Vbulge = [], [], [], [], [], []
    with open(path, 'r', newline='') as f:
        first = f.readline()
        has_header = any(h in first.lower() for h in ["r", "v", "gas", "disk", "bulge", "obs"])
        f.seek(0)
        if has_header:
            rdr = csv.DictReader(f, delimiter=None, skipinitialspace=True)
            for row in rdr:
                def g(keys):
                    for k in keys:
                        if k in row and row[k]:
                            try: return float(row[k])
                            except: pass
                    return None
                r   = g(["R","R_kpc","radius","Radius","r"])
                vob = g(["Vobs","V_obs","Vobs_kms","Vobs(km/s)","Vobs[km/s]","V"])
                ver = g(["Verr","eVobs","Verr_kms","sigma","err","dV"])
                vga = g(["Vgas","V_gas","Vgas_kms"])
                vdi = g(["Vdisk","V_disk","Vdisk_kms"])
                vbu = g(["Vbul","V_bulge","Vbulge","Vbulge_kms"])
                if r is None: continue
                R.append(r); Vobs.append(vob if vob is not None else float("nan"))
                Verr.append(ver if ver is not None else float("nan"))
                if vga is not None: Vgas.append(vga)
                if vdi is not None: Vdisk.append(vdi)
                if vbu is not None: Vbulge.append(vbu)
        else:
            for line in f:
                if not line.strip() or line.strip().startswith("#"): continue
                parts = line.split()
                if len(parts) < 2: continue
                try:
                    r = float(parts[0]); R.append(r)
                    Vobs.append(float(parts[1]) if len(parts)>1 else float("nan"))
                    Verr.append(float(parts[2]) if len(parts)>2 else float("nan"))
                    if len(parts)>3: Vgas.append(float(parts[3]))
                    if len(parts)>4: Vdisk.append(float(parts[4]))
                    if len(parts)>5: Vbulge.append(float(parts[5]))
                except: pass
    n = len(R)
    def pad(a): return a + [0.0]*(n - len(a))
    Vgas, Vdisk, Vbulge = pad(Vgas), pad(Vdisk), pad(Vbulge)
    return {"R_kpc":R,"Vobs":Vobs,"Verr":Verr,"Vgas":Vgas,"Vdisk":Vdisk,"Vbulge":Vbulge}

def baryon_speed_sq(row):
    return row["Vgas"]*row["Vgas"] + row["Vdisk"]*row["Vdisk"] + row["Vbulge"]*row["Vbulge"]

def awut_purple_add_sq(R, V0):
    Rmax = max(R) if R else 1.0
    Rchar = 0.3*Rmax if Rmax>0 else 1.0
    return [ (V0*V0)*(1.0 - math.exp(-r/Rchar)) for r in R ]

def r2_rmse(vobs, vpred):
    xs, ys = [], []
    for o,p in zip(vobs,vpred):
        if (o is None) or (p is None): continue
        if (isinstance(o,float) and math.isnan(o)): continue
        xs.append(o); ys.append(p)
    if len(xs) < 2: return None, None
    ybar = sum(xs)/len(xs)
    ss_tot = sum((x - ybar)**2 for x in xs)
    ss_res = sum((x - y)**2 for x,y in zip(xs,ys))
    r2 = 1.0 - (ss_res/ss_tot if ss_tot>0 else float("inf"))
    rmse = math.sqrt(ss_res/len(xs))
    return r2, rmse

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--cfg", default="config.json")
    ap.add_argument("--out", default="results/rotcurves_summary.json")
    args = ap.parse_args()

    V0 = None
    if os.path.exists(args.cfg):
        try:
            cfg = json.load(open(args.cfg))
            V0 = cfg.get("rotation_curves", {}).get("V0_global", None)
        except: pass
    if V0 is None:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"status":"MISSING_V0_GLOBAL"}, open(args.out,"w"), indent=2)
        print("[ERROR] Set rotation_curves.V0_global (km/s) in config.json"); return

    files = sorted(glob.glob(os.path.join(args.data,"*_rotmod.*")))
    summary = {"status":"OK","V0_global":V0,"galaxies":[]}
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    for fpath in files:
        name = os.path.basename(fpath).split("_rotmod")[0]
        try:
            tab = read_rotmod_any(fpath)
            R = tab["R_kpc"]
            Vb2 = [baryon_speed_sq({k:tab[k][i] for k in ["Vgas","Vdisk","Vbulge"]}) for i in range(len(R))]
            Vadd2 = awut_purple_add_sq(R, V0)
            Vpred = [math.sqrt(max(0.0, vb2 + va2)) for vb2,va2 in zip(Vb2,Vadd2)]
            r2, rmse = r2_rmse(tab["Vobs"], Vpred)
            summary["galaxies"].append({"name":name,"n_points":len(R),"R2":r2,"RMSE_kms":rmse})
        except Exception as e:
            summary["galaxies"].append({"name":name,"error":str(e)})
    json.dump(summary, open(args.out,"w"), indent=2)
    print("Wrote", args.out)

if __name__=="__main__":
    main()
