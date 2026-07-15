import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/day2_c2_check"
conds = ["WT", "PVCablated", "WT_AVBstim", "PVCablated_AVBstim"]
labels = ["WT\n(PLM stim)", "PVC ablated\n(PLM stim)", "WT\n(AVB direct stim)", "PVC ablated\n(AVB direct stim)"]
colors = ["#2E5EAA", "#D9720B", "#8FA8D6", "#F0B47A"]

fig, axes = plt.subplots(1, 2, figsize=(12, 5))

# left: time series, all 4
for c, lab, col in zip(conds, labels, colors):
    d = np.loadtxt(f"{DIR}/{c}/c302_C2_TouchTW_{c}.muscles.activity.dat")
    t = d[:, 0] * 1000
    tot = d[:, 1:].sum(axis=1) * 1e6
    axes[0].plot(t, tot, color=col, lw=2.2, label=lab.replace("\n", " "))
axes[0].axvspan(50, 350, color="0.92", zorder=0)
axes[0].set_xlabel("Time (ms)")
axes[0].set_ylabel("Total muscle activation (a.u.)")
axes[0].set_title("Bypass control: does the motor layer respond\nwhen AVB is stimulated directly?")
axes[0].legend(frameon=False, fontsize=8, loc="upper left")

# right: bar, end values
ends = []
for c in conds:
    d = np.loadtxt(f"{DIR}/{c}/c302_C2_TouchTW_{c}.muscles.activity.dat")
    ends.append(d[:, 1:].sum(axis=1)[-1] * 1e6)
axes[1].bar(labels, ends, color=colors)
axes[1].set_ylabel("Muscle activation at t=500ms")
axes[1].set_title("PLM-stim gap (-40%) mostly closes\nunder AVB direct stim (-20%)")
for i, v in enumerate(ends):
    axes[1].text(i, v + 0.3, f"{v:.1f}", ha="center", fontsize=10)
axes[1].tick_params(axis='x', labelrotation=8)

for ax in axes:
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.grid(True, axis="y", color="0.9", lw=0.8)

fig.tight_layout()
fig.savefig(f"{DIR}/../plots/bypass_control.png", dpi=150)
print("done")
