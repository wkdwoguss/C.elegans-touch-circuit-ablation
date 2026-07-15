import numpy as np, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def cell_list(dat_path):
    nml_path = dat_path.replace(".dat", ".net.nml")
    text = open(nml_path).read()
    names = re.findall(r'<population id="(\w+)"', text)
    return sorted(n for n in names if not re.match(r"^M[DV][LR]\d+$", n))

BASE = "/home/tako/wkdwoguss/openworm/day2_c2_check"
WT_DAT = f"{BASE}/WT/c302_C2_TouchTW_WT.dat"
PVC_DAT = f"{BASE}/PVCablated/c302_C2_TouchTW_PVCablated.dat"
wt = np.loadtxt(WT_DAT); pvc = np.loadtxt(PVC_DAT)
wt_cells = cell_list(WT_DAT); pvc_cells = cell_list(PVC_DAT)
wt_idx = {c: i + 1 for i, c in enumerate(wt_cells)}
pvc_idx = {c: i + 1 for i, c in enumerate(pvc_cells)}
t = wt[:, 0] * 1000
late = t > 350

motor_classes = {"DA": range(1, 10), "VA": range(1, 13), "DB": range(1, 8),
                  "VB": range(1, 12), "DD": range(1, 7), "VD": range(1, 14)}

names, gaps = [], []
for cls, rng in motor_classes.items():
    for n in rng:
        c = f"{cls}{n}"
        if c not in pvc_idx:
            continue
        vwt = wt[:, wt_idx[c]] * 1000
        vpvc = pvc[:, pvc_idx[c]] * 1000
        gap = (vwt - vpvc)[late].mean()
        names.append(c)
        gaps.append(gap)

fig, ax = plt.subplots(figsize=(13, 5))
colors = ["#D9720B" if g > 0 else "#2E5EAA" for g in gaps]
ax.bar(range(len(names)), gaps, color=colors)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=90, fontsize=7)
ax.set_ylabel("WT - PVCablated, mean mV gap (post-stimulus, >350ms)")
ax.set_title("PVC ablation vs all 58 DA/VA/DB/VB/DD/VD motor neurons (parameters_C2)")
ax.axhline(0, color="0.3", lw=0.8)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig(f"{BASE}/../plots/pvc_full_motorneuron_scan.png", dpi=150)
print("mean gap across all cells:", np.mean(gaps), "min:", np.min(gaps), "max:", np.max(gaps))
print("done")
