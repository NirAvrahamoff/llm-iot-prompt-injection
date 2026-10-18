"""Makes the results figure from the three saved result files. It does NOT call the model.
Run it from the submission folder, after the three experiments:  python make_figure.py
It writes figure_results.png.
"""
import json
import numpy as np
import matplotlib.pyplot as plt

# The three experiments: name in the legend, path of its results file, bar color
EXPERIMENTS = [
    ("Exp 1: original prompt", "exp1_original_prompt/exp1_results.json", "#c0392b"),
    ("Exp 2: hardened prompt", "exp2_hardened_prompt/exp2_results.json", "#8e44ad"),
    ("Exp 3: code-enforced lock", "exp3_code_enforced/exp3_results.json", "#27ae60"),
]
PANELS = ["Door opened", "Password leaked", "Compromised (opened or leaked)"]
CONTROL = "Correct password (control)"


def load_results(path):
    # Read the "results" part of one expN_results.json file
    with open(path, encoding="utf-8") as f:
        return json.load(f)["results"]


results = [load_results(path) for _, path, _ in EXPERIMENTS]
all_labels = list(results[0].keys())  # the 4 requests, in the order they were run
n = len(EXPERIMENTS)
width = 0.8 / n  # all bars of one request together take 80% of the space

# Each panel gets a width proportional to its number of requests (4 in the first, 3 in the others)
fig, axes = plt.subplots(1, 3, figsize=(16, 6), sharey=True,
                         gridspec_kw={"width_ratios": [4, 3, 3]})
for ax, metric in zip(axes, PANELS):
    # The control request appears only in the "Door opened" panel: the user typed the
    # password, so "leaked" and "compromised" are not meaningful for it
    if metric == "Door opened":
        labels = all_labels
    else:
        labels = [l for l in all_labels if l != CONTROL]
    x = np.arange(len(labels))
    for j, ((name, _, color), res) in enumerate(zip(EXPERIMENTS, results)):
        rates = np.array([res[l][metric]["rate"] for l in labels])
        lo = np.array([res[l][metric]["ci95"][0] for l in labels])
        hi = np.array([res[l][metric]["ci95"][1] for l in labels])
        pos = x + (j - (n - 1) / 2) * width  # shift each experiment's bar left/right
        ax.bar(pos, rates, width, label=name, color=color,
               yerr=[rates - lo, hi - rates], capsize=3,
               error_kw={"elinewidth": 1, "ecolor": "#333333"})
        # Value label just above the top of the error bar
        for xi, r, h in zip(pos, rates, hi):
            ax.text(xi, h + 1.5, f"{r:.1f}%", ha="center", va="bottom", fontsize=7, rotation=90)
    ax.set_title(metric)
    ax.set_xticks(x)
    ax.set_xticklabels([l.replace(" ", "\n") for l in labels], fontsize=9)
    ax.set_ylim(0, 115)  # extra room at the top for the value labels
axes[0].set_ylabel("Rate (%)")
# Legend below the panels, outside the plot area, so it does not cover any bar or label
handles, legend_labels = axes[0].get_legend_handles_labels()
fig.legend(handles, legend_labels, loc="lower center", ncol=n, fontsize=9)
fig.suptitle("Outcomes by request and experiment (30 runs each, 95% Wilson CI). "
             "Exp 3: door opened = actual lock state")
plt.tight_layout(rect=[0, 0.06, 1, 1])  # leave space at the bottom for the legend
plt.savefig("figure_results.png", dpi=200)
plt.close()
print("Saved: figure_results.png")
