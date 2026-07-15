import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/day2_c2_check"
CONDITIONS = {
    "WT": "WT",
    "PVCablated": "PVC ablated",
    "AVBablated": "AVB ablated",
    "AVAablated": "AVA ablated",
    "AVDablated": "AVD ablated",
    "PVCAVBablated": "PVC+AVB ablated",
    "AVDAVAablated": "AVD+AVA ablated",
}
COLORS = {
    "WT": "#2E5EAA", "PVCablated": "#D9720B", "AVBablated": "#2F8F5B", "AVAablated": "#A6376A",
    "AVDablated": "#6B4FA0", "PVCAVBablated": "#B8860B", "AVDAVAablated": "#3AAFA9",
}
STYLES = {
    "WT": "-", "PVCablated": "-", "AVBablated": "-", "AVAablated": "-",
    "AVDablated": "-", "PVCAVBablated": "--", "AVDAVAablated": "--",
}

fig, ax = plt.subplots(figsize=(9.5, 6))
for key, label in CONDITIONS.items():
    d = np.loadtxt(f"{DIR}/{key}/c302_C2_TouchTW_{key}.muscles.activity.dat")
    t = d[:, 0] * 1000
    tot = d[:, 1:].sum(axis=1) * 1e6
    lw = 2.6 if key in ("WT", "PVCablated") else 1.8
    ax.plot(t, tot, color=COLORS[key], lw=lw, linestyle=STYLES[key], label=label)
ax.axvspan(50, 350, color="0.9", zorder=0, label="stimulus window")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (a.u., NEURON muscle model, no Sibernetic)")
ax.set_title("c302+NEURON muscle activation, all 7 conditions (parameters_C2)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best", fontsize=9)
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/c2_muscle_activation_all7.png", dpi=150)
print("done")
