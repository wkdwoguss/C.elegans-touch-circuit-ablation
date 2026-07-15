import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/v2_sibernetic"

CONDITIONS = {
    "WT": "WT",
    "PVCablated": "PVC ablated",
    "AVBablated": "AVB ablated",
    "AVAablated": "AVA ablated",
}
COLORS = {
    "WT": "#2E5EAA",
    "PVCablated": "#D9720B",
    "AVBablated": "#3AA35C",
    "AVAablated": "#B23A6B",
}


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


data = {}
for key in CONDITIONS:
    t, X, Y, Z = parse_motion(f"{DIR}/worm_motion_log_{key}.txt")
    M = np.loadtxt(f"{DIR}/muscles_activity_buffer_{key}.txt")
    data[key] = dict(t=t, X=X, Y=Y, Z=Z, M=M)

print(f"{'condition':12s} {'net disp':>10s} {'path len':>10s} {'bend amp':>10s} {'muscle end':>11s} {'muscle post-stim trend':>22s}")
for key in CONDITIONS:
    d = data[key]
    cx = d["X"].mean(axis=1)
    net = cx[-1] - cx[0]
    path = np.sum(np.abs(np.diff(cx)))
    lat = np.sqrt(d["Y"].var(axis=1) + d["Z"].var(axis=1)).mean()
    tot_m = d["M"].sum(axis=1)
    post = tot_m[d["t"] > 0.35]
    trend = post[-1] - post[0] if len(post) > 1 else float("nan")
    print(f"{key:12s} {net:10.5f} {path:10.5f} {lat:10.6f} {tot_m[-1]:11.2f} {trend:22.2f}")

# ---- Figure: muscle activation over time, all 4 conditions ----
fig, ax = plt.subplots(figsize=(9, 5.5))
for key, label in CONDITIONS.items():
    d = data[key]
    tot_m = d["M"].sum(axis=1)
    ax.plot(d["t"] * 1000, tot_m, color=COLORS[key], lw=2, label=label)
ax.axvspan(50, 350, color="0.9", zorder=0, label="PLM stimulus window")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (sum, 96 body-wall muscles)")
ax.set_title("Motor drive over time — WT vs three single-neuron ablations")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/four_condition_muscle_activation.png", dpi=150)

# ---- Figure: centroid displacement, all 4 conditions ----
fig, ax = plt.subplots(figsize=(9, 5.5))
for key, label in CONDITIONS.items():
    d = data[key]
    cx = d["X"].mean(axis=1)
    ax.plot(d["t"] * 1000, (cx - cx[0]) * 1000, color=COLORS[key], lw=2, label=label)
ax.axvline(50, color="0.6", lw=1, linestyle=":")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Centroid displacement along body axis (x1e-3 units)")
ax.set_title("Net body translation — WT vs three single-neuron ablations")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/four_condition_displacement.png", dpi=150)

print("\nSaved: plots/four_condition_muscle_activation.png, plots/four_condition_displacement.png")
