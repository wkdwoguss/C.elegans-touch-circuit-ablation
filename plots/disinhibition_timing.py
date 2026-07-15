import numpy as np, re
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def cell_list(dat_path):
    nml_path = dat_path.replace(".dat", ".net.nml")
    text = open(nml_path).read()
    names = re.findall(r'<population id="(\w+)"', text)
    return sorted(n for n in names if not re.match(r"^M[DV][LR]\d+$", n))

WT_DAT = "/home/tako/wkdwoguss/openworm/day2_c2_check/WT/c302_C2_TouchTW_WT.dat"
AVB_DAT = "/home/tako/wkdwoguss/openworm/day2_c2_check/AVBablated/c302_C2_TouchTW_AVBablated.dat"
wt = np.loadtxt(WT_DAT); avb = np.loadtxt(AVB_DAT)
wt_cells = cell_list(WT_DAT); avb_cells = cell_list(AVB_DAT)
wt_idx = {c:i+1 for i,c in enumerate(wt_cells)}
avb_idx = {c:i+1 for i,c in enumerate(avb_cells)}
t = wt[:,0]*1000

fig, axes = plt.subplots(2,2, figsize=(11,7), sharex=True)
for ax, c in zip(axes.flat, ["AVAL","DA5","VA2","AVDL"]):
    vwt = wt[:, wt_idx[c]]*1000
    vavb = avb[:, avb_idx[c]]*1000
    ax.plot(t, vwt, label="WT", color="#2E5EAA", lw=2)
    ax.plot(t, vavb, label="AVB removed", color="#2F8F5B", lw=2)
    ax.axvline(50, color="0.6", lw=1, linestyle=":")
    ax.set_title(c)
    ax.set_ylabel("mV")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.legend(fontsize=8)
axes[1,0].set_xlabel("Time (ms)")
axes[1,1].set_xlabel("Time (ms)")
fig.suptitle("Disinhibition only appears after the stimulus (dotted line = stimulus onset, t=50ms)")
fig.tight_layout()
fig.savefig("/home/tako/wkdwoguss/openworm/plots/disinhibition_timing.png", dpi=150)
print("done")
