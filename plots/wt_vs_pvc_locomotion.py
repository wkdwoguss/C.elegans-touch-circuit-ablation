import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DIR = "/home/tako/wkdwoguss/openworm/v2_sibernetic"
WT_LOG = f"{DIR}/worm_motion_log_WT.txt"
PVC_LOG = f"{DIR}/worm_motion_log_PVCablated.txt"


def parse(path):
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


t_wt, X_wt, Y_wt, Z_wt = parse(WT_LOG)
t_pvc, X_pvc, Y_pvc, Z_pvc = parse(PVC_LOG)

# Body long axis is X (spans ~0.1-1.25 = body length laid out along world X).
# Net locomotion = translation of the body centroid along X over time.
cx_wt, cx_pvc = X_wt.mean(axis=1), X_pvc.mean(axis=1)
net_wt = cx_wt[-1] - cx_wt[0]
net_pvc = cx_pvc[-1] - cx_pvc[0]

# head/tail-specific tracking (point 0 vs point 98)
head_wt, tail_wt = X_wt[:, 0], X_wt[:, -1]
head_pvc, tail_pvc = X_pvc[:, 0], X_pvc[:, -1]

print("=== Net centroid displacement along body axis (X) ===")
print(f"WT:          {net_wt:+.5f}  (t=0 -> {cx_wt[0]:.4f}, t=end -> {cx_wt[-1]:.4f})")
print(f"PVC-ablated: {net_pvc:+.5f}  (t=0 -> {cx_pvc[0]:.4f}, t=end -> {cx_pvc[-1]:.4f})")
print()
print("=== Net displacement, each end of the body ===")
print(f"WT   point0(one end): {head_wt[-1]-head_wt[0]:+.5f}   point98(other end): {tail_wt[-1]-tail_wt[0]:+.5f}")
print(f"PVC  point0(one end): {head_pvc[-1]-head_pvc[0]:+.5f}   point98(other end): {tail_pvc[-1]-tail_pvc[0]:+.5f}")

# Path length (total distance traveled by centroid, not just net displacement)
path_wt = np.sum(np.abs(np.diff(cx_wt)))
path_pvc = np.sum(np.abs(np.diff(cx_pvc)))
print()
print(f"Centroid path length (sum|dx|): WT={path_wt:.5f}  PVC={path_pvc:.5f}")

# Bending amplitude: lateral deviation from the straight-line body axis (Y,Z combined)
lat_wt = np.sqrt(Y_wt.var(axis=1) + Z_wt.var(axis=1))
lat_pvc = np.sqrt(Y_pvc.var(axis=1) + Z_pvc.var(axis=1))
print(f"Mean lateral bending amplitude (std across body): WT={lat_wt.mean():.6f}  PVC={lat_pvc.mean():.6f}")

# ---- Figure 1: centroid + end-point displacement over time ----
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
ax = axes[0]
ax.plot(t_wt * 1000, (cx_wt - cx_wt[0]) * 1000, color="#2E5EAA", lw=2, label="WT")
ax.plot(t_pvc * 1000, (cx_pvc - cx_pvc[0]) * 1000, color="#D9720B", lw=2, label="PVC ablated")
ax.axvline(50, color="0.6", lw=1, linestyle=":", label="PLM stimulus onset")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Centroid displacement along body axis (mm, x1e-3 units)")
ax.set_title("Net body translation (posterior touch stimulus)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")

ax = axes[1]
ax.plot(t_wt * 1000, lat_wt, color="#2E5EAA", lw=2, label="WT")
ax.plot(t_pvc * 1000, lat_pvc, color="#D9720B", lw=2, label="PVC ablated")
ax.axvline(50, color="0.6", lw=1, linestyle=":")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Lateral bending amplitude (std of Y,Z across body)")
ax.set_title("Undulation / bending amplitude")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")

fig.tight_layout()
fig.savefig(f"{DIR}/../plots/wt_vs_pvc_displacement.png", dpi=150)

# ---- Figure 2: kymograph of lateral bending along body vs time (traveling-wave direction) ----
# curvature proxy: deviation of each point's lateral position (Y) from the straight-line
# fit through the body at that timestep, plotted as (body index, time) heatmap.
def kymograph(Y):
    n_t, n_pts = Y.shape
    idx = np.arange(n_pts)
    resid = np.zeros_like(Y)
    for i in range(n_t):
        p = np.polyfit(idx, Y[i], 1)
        resid[i] = Y[i] - np.polyval(p, idx)
    return resid

kymo_wt = kymograph(Y_wt)
kymo_pvc = kymograph(Y_pvc)
vmax = max(np.abs(kymo_wt).max(), np.abs(kymo_pvc).max())

fig, axes = plt.subplots(1, 2, figsize=(11, 5.5), sharey=True)
im0 = axes[0].imshow(kymo_wt, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                      extent=[0, 98, t_wt[-1] * 1000, 0])
axes[0].set_title("WT")
axes[0].set_xlabel("Body point index (0=one end, 98=other end)")
axes[0].set_ylabel("Time (ms)")

im1 = axes[1].imshow(kymo_pvc, aspect="auto", cmap="RdBu_r", vmin=-vmax, vmax=vmax,
                      extent=[0, 98, t_pvc[-1] * 1000, 0])
axes[1].set_title("PVC ablated")
axes[1].set_xlabel("Body point index (0=one end, 98=other end)")

fig.suptitle("Body-bending kymograph (diagonal banding = traveling wave = active crawling)")
cbar = fig.colorbar(im1, ax=axes, shrink=0.8, label="Lateral deviation from straight body axis")
fig.savefig(f"{DIR}/../plots/wt_vs_pvc_kymograph.png", dpi=150)

print("\nSaved: plots/wt_vs_pvc_displacement.png, plots/wt_vs_pvc_kymograph.png")

# ---- Figure 3: total muscle activation over time (direct motor-drive readout) ----
M_wt = np.loadtxt(f"{DIR}/muscles_activity_buffer_WT.txt")
M_pvc = np.loadtxt(f"{DIR}/muscles_activity_buffer_PVCablated.txt")
tot_wt = M_wt.sum(axis=1)
tot_pvc = M_pvc.sum(axis=1)

print("\n=== Total muscle activation (sum over 96 muscles) ===")
print(f"WT   @50ms idx~: peak={tot_wt.max():.4f} at t={t_wt[np.argmax(tot_wt)]*1000:.0f}ms, "
      f"end(500ms)={tot_wt[-1]:.4f}")
print(f"PVC  peak={tot_pvc.max():.4f} at t={t_pvc[np.argmax(tot_pvc)]*1000:.0f}ms, "
      f"end(500ms)={tot_pvc[-1]:.4f}")
# activation in the post-stimulus window (stimulus is 50-350ms)
post_wt = tot_wt[t_wt > 0.35]
post_pvc = tot_pvc[t_pvc > 0.35]
print(f"Post-stimulus (>350ms) mean activation: WT={post_wt.mean():.4f}  PVC={post_pvc.mean():.4f}")
print(f"Post-stimulus (>350ms) activation trend (last-first): WT={post_wt[-1]-post_wt[0]:+.4f}  PVC={post_pvc[-1]-post_pvc[0]:+.4f}")

fig, ax = plt.subplots(figsize=(8, 5))
ax.plot(t_wt * 1000, tot_wt, color="#2E5EAA", lw=2, label="WT")
ax.plot(t_pvc * 1000, tot_pvc, color="#D9720B", lw=2, label="PVC ablated")
ax.axvspan(50, 350, color="0.9", zorder=0, label="PLM stimulus window")
ax.set_xlabel("Time (ms)")
ax.set_ylabel("Total muscle activation (sum, 96 body-wall muscles)")
ax.set_title("Motor drive over time — does it persist after the touch stimulus ends?")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
ax.grid(True, axis="y", color="0.9", lw=0.8)
ax.legend(frameon=False, loc="best")
fig.tight_layout()
fig.savefig(f"{DIR}/../plots/wt_vs_pvc_muscle_activation.png", dpi=150)
print("Saved: plots/wt_vs_pvc_muscle_activation.png")
