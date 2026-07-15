import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/day2_c2_check"
CONDITIONS = {"WT": "WT", "PVCablated": "PVC ablated", "AVBablated": "AVB ablated", "AVAablated": "AVA ablated"}
COLORS = {"WT": "#2E5EAA", "PVCablated": "#D9720B", "AVBablated": "#2F8F5B", "AVAablated": "#A6376A"}

fig, ax = plt.subplots(figsize=(9, 5.5))
for key, label in CONDITIONS.items():
    d = np.loadtxt(f"{DIR}/{key}/c302_C2_TouchTW_{key}.muscles.activity.dat")
    t = d[:, 0] * 1000
    tot = d[:, 1:].sum(axis=1) * 1e6
    ax.plot(t, tot, color=COLORS[key], lw=2, label=label)
ax.axvspan(50, 350, color="0.9", zorder=0, label="stimulus window")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (a.u., NEURON muscle model, no Sibernetic)")
ax.set_title("c302+NEURON muscle activation (parameters_C2, matches Sibernetic model — no physics)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/c2_muscle_activation.png", dpi=150)
print("done")
