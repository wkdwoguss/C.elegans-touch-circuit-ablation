import re
import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Usage: python make_v1_anatomical_c2.py <ABLATED_NAME> <MISSING_CELL1> [MISSING_CELL2 ...]

ABL_NAME = sys.argv[1]
MISSING_CELLS = set(sys.argv[2:])

BASE = "/home/tako/wkdwoguss/openworm/day2_c2_check"
WT_NML = f"{BASE}/WT/c302_C2_TouchTW_WT.net.nml"
WT_DAT = f"{BASE}/WT/c302_C2_TouchTW_WT.dat"
ABL_NML = f"{BASE}/{ABL_NAME}/c302_C2_TouchTW_{ABL_NAME}.net.nml"
ABL_DAT = f"{BASE}/{ABL_NAME}/c302_C2_TouchTW_{ABL_NAME}.dat"


def get_positions(path):
    text = open(path).read()
    pattern = re.compile(
        r'<population id="(\w+)"[^>]*>.*?<location x="([-\d.]+)" y="([-\d.]+)" z="([-\d.]+)"',
        re.S,
    )
    out = {}
    for m in pattern.finditer(text):
        name = m.group(1)
        if re.match(r"^M[DV][LR]\d+$", name):
            continue  # skip muscles, neurons only
        out[name] = (float(m.group(2)), float(m.group(3)), float(m.group(4)))
    return out


wt_pos = get_positions(WT_NML)
abl_pos = get_positions(ABL_NML)

WT_CELLS = sorted(wt_pos.keys())
ABL_CELLS = sorted(abl_pos.keys())
wt_idx = {name: i + 1 for i, name in enumerate(WT_CELLS)}
abl_idx = {name: i + 1 for i, name in enumerate(ABL_CELLS)}

wt_data = np.loadtxt(WT_DAT)
abl_data = np.loadtxt(ABL_DAT)

t_ms = wt_data[:, 0] * 1000
assert np.allclose(t_ms, abl_data[:, 0] * 1000)

step = 100
frame_idx = np.arange(0, len(t_ms), step)
t_frames = t_ms[frame_idx]

VMIN, VMAX = -65.0, -30.0  # C2 spike threshold is -55mV (not -20mV like C) -- rescaled to actual dynamic range


def project(pos):
    px = pos[1]
    py = pos[2] + pos[0] * 0.15
    return px, py


wt_xy = {c: project(p) for c, p in wt_pos.items()}
abl_xy = {c: project(p) for c, p in abl_pos.items()}

all_x = [p[0] for p in wt_xy.values()]
all_y = [p[1] for p in wt_xy.values()]
XLIM = (min(all_x) - 40, max(all_x) + 40)
YLIM = (min(all_y) - 40, max(all_y) + 40)

GRID_W, GRID_H = 420, 140
gx = np.linspace(*XLIM, GRID_W)
gy = np.linspace(*YLIM, GRID_H)
GX, GY = np.meshgrid(gx, gy)

SIGMA = 8.0
BASELINE_GLOW = 0.04


def render_grid(data, idx, xy, current_row, missing_cells):
    grid = np.zeros_like(GX)
    for name, (px, py) in xy.items():
        if name in missing_cells:
            continue
        v = data[current_row, idx[name]] * 1000
        norm = np.clip((v - VMIN) / (VMAX - VMIN), 0, 1)
        amp = BASELINE_GLOW + (1 - BASELINE_GLOW) * norm
        blob = amp * np.exp(-((GX - px) ** 2 + (GY - py) ** 2) / (2 * SIGMA ** 2))
        np.maximum(grid, blob, out=grid)
    return grid


fig, (ax_wt, ax_abl) = plt.subplots(1, 2, figsize=(13, 5.5), facecolor="black")
for ax in (ax_wt, ax_abl):
    ax.set_facecolor("black")
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.axis("off")

im_wt = ax_wt.imshow(render_grid(wt_data, wt_idx, wt_xy, 0, set()),
                      extent=[*XLIM, *YLIM], origin="lower", cmap="inferno",
                      vmin=0, vmax=1, aspect="auto")
im_abl = ax_abl.imshow(render_grid(abl_data, abl_idx, abl_xy, 0, MISSING_CELLS),
                        extent=[*XLIM, *YLIM], origin="lower", cmap="inferno",
                        vmin=0, vmax=1, aspect="auto")

ax_wt.set_title("Wild type (C2)", color="white", fontsize=13, fontweight="bold")
ax_abl.set_title(f"{ABL_NAME} (C2)", color="white", fontsize=13, fontweight="bold")

for name in MISSING_CELLS:
    if name in wt_xy:
        px, py = wt_xy[name]
        ax_abl.scatter(px, py, s=260, facecolors="none", edgecolors="0.35",
                        linestyles="dashed", linewidths=1.2, zorder=3)

LANDMARKS = {"PLML": "PLM", "PVCL": "PVC", "AVBL": "AVB", "DB1": "DB1", "VA1": "VA1", "AVAL": "AVA"}
for ax, xy in ((ax_wt, wt_xy), (ax_abl, abl_xy)):
    for name, label in LANDMARKS.items():
        if name not in xy:
            continue
        px, py = xy[name]
        ax.annotate(label, (px, py), xytext=(0, 16), textcoords="offset points",
                    color="0.7", fontsize=8, ha="center")

time_text = fig.suptitle("", color="white", fontsize=12)
fig.subplots_adjust(left=0.02, right=0.98, top=0.86, bottom=0.04, wspace=0.03)


def frame(i):
    row = frame_idx[i]
    im_wt.set_data(render_grid(wt_data, wt_idx, wt_xy, row, set()))
    im_abl.set_data(render_grid(abl_data, abl_idx, abl_xy, row, MISSING_CELLS))
    time_text.set_text(f"Posterior touch (PLM stimulus, parameters_C2) — t = {t_frames[i]:.1f} ms")
    return [im_wt, im_abl]


anim = FuncAnimation(fig, frame, frames=len(frame_idx), interval=1000 / 30)
out = f"{BASE}/{ABL_NAME}/V1_anatomical_WT_vs_{ABL_NAME}_C2.mp4"
anim.save(out, fps=30, dpi=130, savefig_kwargs={"facecolor": "black"})
print("done:", out)
