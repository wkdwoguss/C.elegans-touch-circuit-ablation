import sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

# Usage: python make_v1_animation_c2.py <ABLATED_NAME> <MISSING_CELL1> [MISSING_CELL2 ...]
# e.g.:  python make_v1_animation_c2.py PVCablated PVCL PVCR

ABL_NAME = sys.argv[1]
MISSING_CELLS = set(sys.argv[2:])

BASE = "/home/tako/wkdwoguss/openworm/day2_c2_check"
WT_DAT = f"{BASE}/WT/c302_C2_TouchTW_WT.dat"
ABL_DAT = f"{BASE}/{ABL_NAME}/c302_C2_TouchTW_{ABL_NAME}.dat"


def cell_list_from_dat_header(dat_path):
    # c302 .dat columns are alphabetical-by-cell-name; recover names from the
    # sibling .net.nml population list (same trick used for the original v1_ablated scripts).
    import re
    nml_path = dat_path.replace(".dat", ".net.nml")
    text = open(nml_path).read()
    names = re.findall(r'<population id="(\w+)"', text)
    # drop muscle populations (MDL/MDR/MVL/MVR##), keep neurons only
    neurons = sorted(n for n in names if not re.match(r"^M[DV][LR]\d+$", n))
    return neurons


WT_CELLS = cell_list_from_dat_header(WT_DAT)
ABL_CELLS = cell_list_from_dat_header(ABL_DAT)

wt_idx = {name: i + 1 for i, name in enumerate(WT_CELLS)}
abl_idx = {name: i + 1 for i, name in enumerate(ABL_CELLS)}

wt_data = np.loadtxt(WT_DAT)
abl_data = np.loadtxt(ABL_DAT)

t_ms = wt_data[:, 0] * 1000
assert np.allclose(t_ms, abl_data[:, 0] * 1000), "time bases differ between runs"

step = 100
frame_idx = np.arange(0, len(t_ms), step)
t_frames = t_ms[frame_idx]

VMIN, VMAX = -65.0, -30.0  # C2 spike threshold is -55mV (not -20mV like C) -- rescaled to actual dynamic range

layout = {
    "PLML": (0, 0.6), "PLMR": (0, -0.6),
    "PVCL": (1.4, 0.6), "PVCR": (1.4, -0.6),
    "AVBL": (2.8, 0.6), "AVBR": (2.8, -0.6),
    "DB1": (4.2, 1.1), "VB1": (4.2, 0.1),
}
edges = [("PLML", "PVCL"), ("PLMR", "PVCR"),
         ("PVCL", "AVBL"), ("PVCR", "AVBR"),
         ("PVCL", "AVBR"), ("PVCR", "AVBL"),
         ("AVBL", "DB1"), ("AVBL", "VB1"),
         ("AVBR", "DB1"), ("AVBR", "VB1")]

cmap = plt.cm.RdYlBu_r


def mv(data, idx, name, frame_row):
    if name not in idx:
        return None
    return data[frame_row, idx[name]] * 1000


def draw_panel(ax, data, idx, title, missing_cells):
    ax.clear()
    ax.set_title(title, fontsize=13, fontweight="bold")
    ax.set_xlim(-0.8, 5.2)
    ax.set_ylim(-1.3, 1.7)
    ax.axis("off")

    for a, b in edges:
        if a in missing_cells or b in missing_cells:
            continue
        xa, ya = layout[a]
        xb, yb = layout[b]
        ax.plot([xa, xb], [ya, yb], color="0.75", lw=1.5, zorder=1)

    for name, (x, y) in layout.items():
        if name in missing_cells:
            ax.scatter(x, y, s=900, facecolors="none", edgecolors="0.6",
                       linestyles="dashed", linewidths=1.5, zorder=2)
            ax.text(x, y, "X", ha="center", va="center", fontsize=14, color="0.6")
            ax.text(x, y - 0.35, name, ha="center", va="center", fontsize=9, color="0.6")
            continue
        v = mv(data, idx, name, current_row[0])
        norm = np.clip((v - VMIN) / (VMAX - VMIN), 0, 1)
        ax.scatter(x, y, s=900, c=[cmap(norm)], edgecolors="black", linewidths=1, zorder=2)
        ax.text(x, y, name, ha="center", va="center", fontsize=9, fontweight="bold")
        ax.text(x, y - 0.35, f"{v:.0f}mV", ha="center", va="center", fontsize=8)


current_row = [0]

fig, (ax_wt, ax_abl) = plt.subplots(1, 2, figsize=(11, 5))
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=VMIN, vmax=VMAX))
cbar = fig.colorbar(sm, ax=[ax_wt, ax_abl], orientation="horizontal", fraction=0.05, pad=0.08)
cbar.set_label("Membrane potential (mV)")

time_text = fig.suptitle("", fontsize=12)


def frame(i):
    current_row[0] = frame_idx[i]
    draw_panel(ax_wt, wt_data, wt_idx, "Wild type (C2)", missing_cells=set())
    draw_panel(ax_abl, abl_data, abl_idx, f"{ABL_NAME} (C2)", missing_cells=MISSING_CELLS)
    time_text.set_text(f"Posterior touch (PLM stimulus, parameters_C2) — t = {t_frames[i]:.1f} ms")
    return []


anim = FuncAnimation(fig, frame, frames=len(frame_idx), interval=1000 / 30)
out = f"{BASE}/{ABL_NAME}/V1_propagation_WT_vs_{ABL_NAME}_C2.mp4"
anim.save(out, fps=30, dpi=120)
print("done:", out)
