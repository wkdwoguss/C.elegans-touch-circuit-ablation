# In Silico Ablation of Key Interneurons in the *C. elegans* Touch Circuit

**A three-day computational study using the OpenWorm stack (c302 / Sibernetic)**

---

## 1. Research Question

How does the removal of key interneurons in the *C. elegans* mechanosensory circuit affect the transmission of behavioural information from touch receptor neurons to motor output?

We ablate command interneurons in silico, measure whether a simulated touch signal still propagates to the motor layer, and produce two video outputs: an animation of signal propagation through the circuit, and a locomotion comparison of the intact vs. ablated worm.

---

## 2. Critical Reframing (please read before the methods)

The OpenWorm model **contains no environment and no contact physics.** Sensory neurons in the c302 network receive no input by default: if we simply run the model and delete a neuron, the touch neurons will sit silent and nothing will happen.

This is not a reason to abandon the question — it is a reason to operationalise it correctly:

> **We simulate "touch" as direct current injection into the touch receptor neurons, and we measure whether that injected signal propagates through the interneuron layer to the motor neurons.**

c302 supports this via its `-cellstostimulate` argument. Current injection is the **stimulus** (standing in for the physical touch we cannot deliver); it is not the experimental manipulation.

**The manipulation is the ablation itself.** Because the circuit relies heavily on gap junctions (e.g. AVA–AVD), ablation **cannot** be implemented by setting synaptic weights to zero — gap junctions are bidirectional and would leave the "ablated" cell acting as an electrical conduit and current sink. We instead **regenerate the network with the target cell excluded**, using c302's `-cells` whitelist. The cell then does not exist in the generated NeuroML at all: no populations, no chemical synapses, no gap junctions, no neuromuscular junctions.

Each condition is therefore: **same stimulus, different network.** The comparison between them is the experiment.

---

## 3. Circuit Under Study

The classical *C. elegans* touch circuit (Chalfie et al.):

| Layer | Cells | Pathway |
|---|---|---|
| Sensory | ALML/R, AVM | Anterior touch |
| Sensory | PLML/R | Posterior touch |
| Command interneuron | **AVD, AVA** | Drives reversal |
| Command interneuron | **PVC, AVB** | Drives forward locomotion |
| Motor | DA, VA | Backward |
| Motor | DB, VB | Forward |

- **Anterior touch:** ALM/AVM → AVD → AVA → A-type motor neurons → reversal
- **Posterior touch:** PLM → PVC → AVB → B-type motor neurons → forward acceleration

**Ablation targets: PVC, AVD, AVA, AVB.**

---

## 4. Methods

### 4.1 Tooling

- **c302** — NeuroML-based model of the 302 neurons and body wall muscles. Primary instrument. Runs in seconds to minutes, allowing a wide condition sweep. Source of all membrane potential traces.
- **Sibernetic** — 3D SPH body/fluid model. Slow (hours per run), driven **one-way** by c302 output. Used to generate the locomotion videos; launched in the background on Day 1.
- **NetworkX** — graph-theoretic connectome analysis (contingency track, §6).
- **matplotlib (FuncAnimation) + ffmpeg** — production of the propagation animation.

Environment: Python 3.10 virtual environment (owmeta does not support newer versions). Docker for Sibernetic.

### 4.2 Subnetwork Construction

We do **not** simulate all 302 neurons. We build a ~30-cell subnetwork of the touch circuit:

```
ALML, ALMR, AVM, PLML, PLMR, PVM,
AVAL, AVAR, AVBL, AVBR, AVDL, AVDR, PVCL, PVCR,
DA1–DA9, VA1–VA12, DB1–DB7, VB1–VB11
```

Each run then takes seconds, which is what makes a real condition sweep possible in three days.

### 4.3 Stimulation Protocol

```bash
c302 TouchWT parameters_C \
     -cells   [<subnetwork cell list>] \
     -cellstostimulate ["PLML","PLMR"] \
     -paramoverride {"unphysiological_offset_current":"2.9pA"} \
     -duration 500
```

Anterior touch: `-cellstostimulate ["ALML","ALMR","AVM"]`.

### 4.4 Ablation Protocol

```python
keep = [c for c in subnetwork_cells if c not in TARGETS]
# pass `keep` to c302 as the -cells argument
```

### 4.5 Readouts

From the membrane potential traces:

1. Does the downstream interneuron depolarise after sensory stimulation? (peak ΔV, latency)
2. Does the signal reach the command interneuron layer?
3. Does it reach the motor neurons?
4. Dose–response: vary injected current amplitude.

Primary metric: **presence and magnitude of signal propagation to the motor layer**, wild type vs. each ablation.

### 4.6 Video Outputs

Two video products, serving different purposes.

**V1 — Circuit propagation animation (primary result).**

c302 writes membrane potential traces to a `.dat` file (columns = cells, rows = timesteps). We map these to a schematic of the touch circuit and animate:

- Nodes laid out as PLM → PVC → AVB → DB/VB
- Node colour = membrane potential at that timestep (blue = resting, red = depolarised)
- Playback shows the signal travelling along the circuit
- **Wild type and ablated condition rendered side by side, time-synchronised**

In the wild type the activation should sweep to the motor layer; in the PVC-ablated condition it should stall at the missing node. This single video answers the research question visually.

Parameter set B is preferred for this: it exposes a 0–1 "activity" measure alongside membrane potential, which maps cleanly onto colour.

```python
import numpy as np, matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

data = np.loadtxt("c302_B.dat")          # [time, cell1, cell2, ...]
t, V = data[:, 0], data[:, 1:]
norm = (V - V.min()) / (V.max() - V.min())

pos = {"PLML": (0, 0), "PVCL": (1, 0), "AVBL": (2, 0),
       "DB1": (3, 0.5), "VB1": (3, -0.5)}

def frame(i):
    ax.clear()
    for name, (x, y) in pos.items():
        ax.scatter(x, y, s=1200, c=[plt.cm.RdYlBu_r(norm[i, idx[name]])])
        ax.text(x, y, name, ha="center", va="center")

anim = FuncAnimation(fig, frame, frames=len(t), interval=20)
anim.save("propagation_wt.mp4", fps=30)
```

**V2 — Locomotion comparison (supplementary).**

The OpenWorm Docker pipeline records the Sibernetic body simulation to mp4 automatically (via Xvfb + ffmpeg inside `master_openworm.py`). We run two containers — wild type and PVC-ablated — with `-d 5000`, and place the resulting clips side by side.

**We state up front that this video may show little or no difference between conditions.** The neural-to-body coupling is one-way and there is no proprioceptive feedback, so a disrupted sensory circuit is not expected to produce a dramatic behavioural change in this model. If the two clips look the same, that is itself a reportable finding about the model's current limits — and V1 remains the substantive result. We will not overstate V2.

---

## 5. Three-Day Schedule (7 h/day)

### Day 1 — Environment, connectome verification, wild-type baseline

| Time | Task |
|---|---|
| 0:00–1:30 | Docker image pull **in background**; install c302 in a Python 3.10 venv; smoke-test with `LEMS_c302_A_IClamp.xml` |
| 1:30–2:30 | **Connectome verification** (see below — do not skip) |
| 2:30–4:00 | Build the touch-circuit subnetwork; confirm generation and execution |
| 4:00–6:00 | **Wild-type propagation baseline**: stimulate PLM, record PVC → AVB → DB/VB. Repeat for anterior touch. Dose–response sweep |
| 6:00–7:00 | **Trace export check** — confirm the `.dat` file is written and establish which column maps to which cell |

Also launch, first thing in the morning: **two Sibernetic containers in the background** (wild type; PVC-ablated), `-d 5000`. These run for the remainder of the study.

**Connectome verification (1:30–2:30) is the highest-risk hour of the project.** Confirm that the connections our hypothesis assumes actually exist in c302's connectome data:

- Are all target cells present in the cell list?
- Does PLM → PVC exist? What is the synapse count / weight?
- Does PVC → AVB exist? AVB → DB/VB?
- Which connections are chemical and which are gap junctions?

Discovering on Day 3 that a required edge is absent from the model would end the project.

**The trace export check (6:00–7:00) is not optional either.** The entire V1 animation depends on having per-cell voltage traces on disk with a known column mapping. Discovering on Day 3 that traces were never saved would cost us the primary deliverable.

**Day 1 exit criterion:** a trace showing PLM stimulation producing a PVC response, saved to disk. If we do not have this by end of Day 1, we switch to the contingency track (§6) — the decision must be made before Day 1 ends.

### Day 2 — Positive controls and ablation sweep

| Time | Task |
|---|---|
| 0:00–2:30 | **Positive controls:** ablate AVB, AVA individually. Known experimental phenotypes (AVB loss → forward locomotion deficit; AVA loss → reversal deficit) should appear as loss of propagation to the corresponding motor class |
| 2:30–4:00 | **Main ablations:** PVC, AVD, and combinations (PVC+AVB; AVD+AVA) |
| 4:00–5:00 | **Bypass control:** inject current directly into AVB. If the motor layer responds here but not when PLM is stimulated in the PVC-ablated network, the break is localised precisely to PVC |
| 5:00–6:00 | Unilateral ablation (e.g. PVCL only) — test bilateral redundancy |
| 6:00–7:00 | **Parameter-set robustness:** repeat key conditions under parameter sets B and C |

The bypass control is what turns "the signal didn't arrive" into "the signal didn't arrive *because PVC is missing*." It rules out the alternative explanation that the downstream network simply cannot respond at all.

The final block matters: this model is parameter-sensitive. If the direction of an effect flips between parameter sets, that effect is an artefact of the parameters, not a finding.

### Day 3 — Recovery, animation, quantification, write-up

| Time | Task |
|---|---|
| 0:00–1:00 | **Recover Sibernetic output before running `stop.sh`** — `stop.sh` deletes the container and all data |
| 1:00–2:00 | Quantify traces: peak ΔV, latency, propagation index (motor-layer response relative to wild type) |
| 2:00–4:30 | **Produce V1: side-by-side propagation animation** (wild type vs. PVC-ablated) |
| 4:30–5:00 | **Produce V2:** trim and stitch the two Sibernetic clips side by side |
| 5:00–6:00 | Comparison figures: propagation heatmap across conditions |
| 6:00–7:00 | Write-up and limitations document |

Sibernetic data recovery:

```bash
docker cp openworm:/home/ow/sibernetic/simulations/[TIMESTAMPED_DIR]/worm_motion_log.txt ./wt_motion.txt
```

---

## 6. Contingency Track (Graph-Theoretic Analysis)

There is a meaningful chance that signal propagation is weak or absent in the dynamical model. We therefore run a parallel analysis that **cannot fail**.

Treat the connectome as a directed graph and compute, for each ablation:

- Number of paths from touch receptor neurons to motor neurons
- Shortest path length
- How many paths are severed by removing PVC / AVD / AVA / AVB
- Whether alternative routes exist (circuit redundancy)
- **Betweenness centrality** — which interneuron is the true bottleneck for touch information?

Roughly 2–3 hours in NetworkX. It answers our research question ("effect on information transmission") directly and independently of whether the biophysical simulation cooperates. It also yields a static figure that pairs naturally with V1.

---

## 7. Deliverables

1. **V1 — Circuit propagation animation (mp4).** Wild type vs. ablated, side by side, time-synchronised. Primary visual result.
2. **V2 — Locomotion comparison (mp4).** Sibernetic body simulation, intact vs. ablated. Supplementary; see the caveat in §4.6.
3. Membrane potential traces: wild type vs. each ablation, anterior and posterior touch.
4. **Positive control table** — does the model reproduce known ablation phenotypes? (pass / fail)
5. Bypass control result — is the break localised to the ablated cell?
6. Propagation heatmap across all conditions and both parameter sets.
7. Graph-theoretic bottleneck analysis of the touch circuit.
8. Limitations document (§8).

---

## 8. Known Limitations (to be stated explicitly in all outputs)

- **No sensory feedback loop.** Information flows one way from the neural model to the body model; proprioceptive feedback, essential to real *C. elegans* undulation, is absent. We therefore do not expect and do not claim behavioural phenotypes such as reversal. This is the reason V2 is supplementary rather than primary.
- **"Touch" is current injection**, not mechanotransduction. We model the propagation of an imposed signal, not the transduction of a physical stimulus.
- **Sparse electrophysiological constraints.** Patch-clamp data exist for only a small subset of ion channels; many parameters are inferred by homology from other organisms.
- **Parameter sensitivity.** Results are reported only where they hold across parameter sets.
- **A 2D neuromechanical model with closed proprioceptive feedback exists (`CE_locomotion`), but it contains only the motor circuit — the mechanosensory neurons and command interneurons we ablate are not represented in it.** It therefore cannot be used for this study. Coupling the two models is left as future work.
- **If the positive controls fail**, the honest finding is *"the current OpenWorm model does not reproduce known touch-circuit ablation phenotypes"* — and we report that, rather than over-interpreting null results on novel targets.

---

## 9. Summary

Three days is enough to answer a focused question about **signal propagation through the touch circuit**, and to produce a video that shows it, provided we:

(a) inject current rather than wait for a touch that will never come
(b) ablate by removing cells, not by zeroing weights
(c) verify the connectome before building on it
(d) confirm on Day 1 that traces are being saved — the animation depends on it
(e) validate against known ablation phenotypes before trusting any novel result
