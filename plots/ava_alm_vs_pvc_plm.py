import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/v2_sibernetic"


def parse_motion(path):
    times, Xs, Ys, Zs = [], [], [], []
    with open(path) as f:
        for line in f:
            parts = [p for p in line.rstrip("\n").split("\t") if p != ""]
            if not parts:
                continue
            xi, yi, zi = parts.index("X:"), parts.index("Y:"), parts.index("Z:")
            times.append(float(parts[0]))
            Xs.append(np.array(parts[xi + 1:yi], dtype=float))
            Ys.append(np.array(parts[yi + 1:zi], dtype=float))
            Zs.append(np.array(parts[zi + 1:], dtype=float))
    return np.array(times), np.array(Xs), np.array(Ys), np.array(Zs)


CONDITIONS = {
    "WT":               dict(label="WT (PLM stim)",             color="#2E5EAA", ls="-"),
    "PVCablated":       dict(label="PVC ablated (PLM stim)",     color="#D9720B", ls="-"),
    "AVAablated":       dict(label="AVA ablated (PLM stim)",     color="#A6376A", ls="--"),
    "WT_ALMstim":       dict(label="WT (ALM stim)",              color="#2E5EAA", ls=":"),
    "AVAablated_ALMstim": dict(label="AVA ablated (ALM stim)",   color="#A6376A", ls="-"),
}

import os

def motion_path(key):
    per_folder = f"{DIR}/{key}/worm_motion_log.txt"
    return per_folder if os.path.exists(per_folder) else f"{DIR}/worm_motion_log_{key}.txt"

def muscle_path(key):
    per_folder = f"{DIR}/{key}/muscles_activity_buffer.txt"
    return per_folder if os.path.exists(per_folder) else f"{DIR}/muscles_activity_buffer_{key}.txt"

data = {}
for key in CONDITIONS:
    t, X, Y, Z = parse_motion(motion_path(key))
    M = np.loadtxt(muscle_path(key))
    data[key] = dict(t=t, X=X, Y=Y, Z=Z, M=M)

# ---- Figure 1: muscle activation over time, all 5 ----
fig, ax = plt.subplots(figsize=(9.5, 6))
for key, cfg in CONDITIONS.items():
    d = data[key]
    tot = d["M"].sum(axis=1)
    lw = 2.6 if key in ("WT", "PVCablated") else 2.0
    ax.plot(d["t"] * 1000, tot, color=cfg["color"], lw=lw, linestyle=cfg["ls"], label=cfg["label"])
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (a.u.)")
ax.set_title("Same cell (AVA), opposite direction depending on which pathway is tested")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best", fontsize=9)
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/ava_alm_vs_pvc_plm_muscle_activation.png", dpi=150)

# ---- Figure 2: centroid displacement over time, all 5 ----
fig, ax = plt.subplots(figsize=(9.5, 6))
for key, cfg in CONDITIONS.items():
    d = data[key]
    cx = d["X"].mean(axis=1)
    lw = 2.6 if key in ("WT", "PVCablated") else 2.0
    ax.plot(d["t"] * 1000, (cx - cx[0]) * 1000, color=cfg["color"], lw=lw, linestyle=cfg["ls"], label=cfg["label"])
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Centroid displacement along body axis (x1e-3 units)")
ax.set_title("Body displacement — PLM-stim family vs ALM-stim family")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best", fontsize=9)
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/ava_alm_vs_pvc_plm_displacement.png", dpi=150)

# ---- Figure 3: ALM-only pair, clean two-line comparison ----
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for key in ["WT_ALMstim", "AVAablated_ALMstim"]:
    d = data[key]
    cfg = CONDITIONS[key]
    tot = d["M"].sum(axis=1)
    axes[0].plot(d["t"] * 1000, tot, color=cfg["color"], lw=2.4,
                 linestyle="-" if "ablated" not in key.lower() else "-",
                 label=cfg["label"])
    cx = d["X"].mean(axis=1)
    axes[1].plot(d["t"] * 1000, (cx - cx[0]) * 1000, color=cfg["color"], lw=2.4, label=cfg["label"])
axes[0].set_title("Muscle activation (ALM stimulus)")
axes[0].set_xlabel("Time (ms)")
axes[0].set_ylabel("Total muscle activation (a.u.)")
axes[1].set_title("Body displacement (ALM stimulus)")
axes[1].set_xlabel("Time (ms)")
axes[1].set_ylabel("Centroid displacement (x1e-3 units)")
for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color="0.9", lw=0.8)
    ax.legend(frameon=False, loc="best", fontsize=9)
fig.suptitle("AVA ablation tested on its own pathway (ALM/anterior touch) — the correct positive control")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/ava_almstim_wt_vs_ablated.png", dpi=150)

print("done")
