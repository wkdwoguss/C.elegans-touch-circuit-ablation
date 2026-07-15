import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/day2_c2_check"
CONDITIONS = {"WT": ("WT", "#2E5EAA"), "PVCLablated": ("PVCL only (unilateral)", "#E0A03C"), "PVCablated": ("PVCL+PVCR (bilateral)", "#D9720B")}

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# left: time series
for key, (label, color) in CONDITIONS.items():
    d = np.loadtxt(f"{DIR}/{key}/c302_C2_TouchTW_{key}.muscles.activity.dat")
    t = d[:, 0] * 1000
    tot = d[:, 1:].sum(axis=1) * 1e6
    axes[0].plot(t, tot, color=color, lw=2.4, label=label)
axes[0].axvspan(50, 350, color="0.92", zorder=0)
axes[0].set_xlabel("Time (ms)")
axes[0].set_ylabel("Total muscle activation (a.u.)")
axes[0].set_title("PVC: bilateral vs unilateral ablation")
axes[0].legend(frameon=False, fontsize=9)

# right: bar summary at t=500ms, as % of WT
labels, vals, colors = [], [], []
wt_end = None
for key, (label, color) in CONDITIONS.items():
    d = np.loadtxt(f"{DIR}/{key}/c302_C2_TouchTW_{key}.muscles.activity.dat")
    end = d[:, 1:].sum(axis=1)[-1] * 1e6
    if key == "WT":
        wt_end = end
    labels.append(label)
    vals.append((end / wt_end - 1) * 100)
    colors.append(color)
axes[1].bar(labels, vals, color=colors)
axes[1].axhline(0, color="0.3", lw=0.8)
axes[1].set_ylabel("Muscle activation, % change from WT")
axes[1].set_title("At t=500ms, % of WT")
for i, v in enumerate(vals):
    axes[1].text(i, v - (3 if v < 0 else -1), f"{v:+.1f}%", ha="center", fontsize=10)
axes[1].tick_params(axis='x', labelrotation=12)

for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color="0.9", lw=0.8)

fig.tight_layout()
fig.savefig(f"{DIR}/../plots/pvc_unilateral_comparison.png", dpi=150)
print("done")
