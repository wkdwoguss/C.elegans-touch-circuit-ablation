import pickle
import networkx as nx
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

G = pickle.load(open("/tmp/connectome_graph.pkl", "rb"))
bc = nx.betweenness_centrality(G, weight=None)
ranked = sorted(bc.items(), key=lambda x: -x[1])[:20]
names = [c for c, v in ranked]
vals = [v for c, v in ranked]
targets = {"PVCL","PVCR","AVBL","AVBR","AVDL","AVDR","AVAL","AVAR"}
colors = ["#D9720B" if n in targets else "#8CA0B3" for n in names]

fig, ax = plt.subplots(figsize=(10, 5.5))
ax.bar(range(len(names)), vals, color=colors)
ax.set_xticks(range(len(names)))
ax.set_xticklabels(names, rotation=45, ha="right")
ax.set_ylabel("Betweenness centrality")
ax.set_title("Betweenness centrality, top 20 of 299 C. elegans neurons\n(orange = our 4 ablation targets)")
ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)
fig.tight_layout()
fig.savefig("/home/tako/wkdwoguss/openworm/plots/networkx_betweenness.png", dpi=150)
print("done")
