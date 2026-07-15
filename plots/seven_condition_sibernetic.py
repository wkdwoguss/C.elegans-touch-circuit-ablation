import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

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

def mpath(c):
    p = f"{DIR}/{c}/worm_motion_log.txt"
    return p if os.path.exists(p) else f"{DIR}/worm_motion_log_{c}.txt"

def mupath(c):
    p = f"{DIR}/{c}/muscles_activity_buffer.txt"
    return p if os.path.exists(p) else f"{DIR}/muscles_activity_buffer_{c}.txt"

CONDITIONS = {
    "WT": ("WT", "#2E5EAA", "-"),
    "PVCablated": ("PVC removed", "#D9720B", "-"),
    "AVBablated": ("AVB removed", "#2F8F5B", "-"),
    "AVDablated": ("AVD removed", "#6B4FA0", "-"),
    "PVCAVBablated": ("PVC+AVB removed", "#B8860B", "--"),
    "AVDAVAablated": ("AVD+AVA removed", "#3AAFA9", "--"),
    "PVCLablated": ("PVCL only (unilateral)", "#E0A03C", ":"),
}

data = {}
for key in CONDITIONS:
    t, X, Y, Z = parse_motion(mpath(key))
    M = np.loadtxt(mupath(key))
    data[key] = dict(t=t, X=X, M=M)

fig, ax = plt.subplots(figsize=(10, 6))
for key, (label, color, ls) in CONDITIONS.items():
    d = data[key]
    tot = d["M"].sum(axis=1)
    lw = 2.6 if key in ("WT", "PVCablated") else 1.9
    ax.plot(d["t"] * 1000, tot, color=color, lw=lw, linestyle=ls, label=label)
ax.axvspan(50, 350, color="0.93", zorder=0, label="stimulus window")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (a.u.)")
ax.set_title("Body-level (Sibernetic) muscle activation, all 7 conditions")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, fontsize=9, loc="upper left")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/seven_condition_sibernetic_muscle.png", dpi=150)

# bar summary: path length as % of WT
fig, ax = plt.subplots(figsize=(10, 5.5))
labels, vals, colors = [], [], []
wt_path = None
for key, (label, color, ls) in CONDITIONS.items():
    d = data[key]
    cx = d["X"].mean(axis=1)
    path = np.sum(np.abs(np.diff(cx)))
    if key == "WT":
        wt_path = path
    labels.append(label)
    vals.append((path / wt_path - 1) * 100)
    colors.append(color)
bars = ax.bar(labels, vals, color=colors)
ax.axhline(0, color="0.3", lw=0.8)
ax.set_ylabel("Body displacement path length, % change from WT")
ax.set_title("How much the body actually moved (Sibernetic), vs WT")
for b, v in zip(bars, vals):
    ax.text(b.get_x() + b.get_width() / 2, v + (4 if v >= 0 else -8), f"{v:+.0f}%", ha="center", fontsize=10)
ax.tick_params(axis="x", labelrotation=20)
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/seven_condition_pathlength.png", dpi=150)
print("done")
