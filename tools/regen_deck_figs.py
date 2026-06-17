"""Regenera solo las dos figuras de barras (comparacion y sensibilidad)
con la paleta del deck, etiquetas de valor y margenes recortados.
Lee los datos ya calculados de reports/final_modeling_results.json:
no reentrena nada."""

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
DATA = json.loads((ROOT / "reports" / "final_modeling_results.json").read_text(encoding="utf-8"))

# Paleta alineada al deck
TEAL = "#0E7C86"
ORANGE = "#E8833A"
SLATE = "#6A7A82"
TEXT = "#1F2D34"
GRID = "#DCE6E9"

plt.rcParams.update({
    "font.size": 13,
    "axes.edgecolor": "#C7D2D6",
    "axes.labelcolor": TEXT,
    "text.color": TEXT,
    "xtick.color": TEXT,
    "ytick.color": TEXT,
})


def _save(fig, name):
    fig.savefig(FIG / name, dpi=200, bbox_inches="tight", pad_inches=0.12)
    plt.close(fig)
    print("WROTE", name)


def comparison():
    rows = [r for r in DATA["model_comparison_oof_threshold_050"] if r["model"] != "Dummy"]
    x = np.arange(len(rows))
    width = 0.26
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    series = [(-width, "f2", "F2", TEAL), (0.0, "recall", "Recall", ORANGE), (width, "precision", "Precision", SLATE)]
    for off, metric, label, color in series:
        vals = [r[metric] for r in rows]
        bars = ax.bar(x + off, vals, width, label=label, color=color)
        ax.bar_label(bars, fmt="%.2f", padding=2, fontsize=10, color=TEXT)
    ax.set_xticks(x)
    ax.set_xticklabels([r["model"] for r in rows], fontsize=12)
    ax.set_ylim(0, 1.05)
    ax.set_ylabel("Metrica fuera de fold")
    ax.set_title("Comparacion de modelos (OOF, umbral 0,50)", fontsize=14, fontweight="bold", pad=10)
    ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.10))
    ax.grid(axis="y", color=GRID, alpha=0.9)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    _save(fig, "final_model_comparison_cv.png")


def temporal():
    rows = DATA["temporal_sensitivity_rf_threshold_050"]
    label_map = {
        "Completo": "Completo",
        "Sin Complain": "Sin\nComplain",
        "Sin DaySinceLastOrder": "Sin\nDaySinceLastOrder",
        "Conservador: sin ambas": "Sin ambas\n(final)",
    }
    labels = [label_map.get(r["scenario"], r["scenario"]) for r in rows]
    vals = [r["f2"] for r in rows]
    x = np.arange(len(rows))
    colors = [TEAL] * (len(rows) - 1) + [ORANGE]
    fig, ax = plt.subplots(figsize=(8.4, 5.6))
    bars = ax.bar(x, vals, width=0.62, color=colors)
    ax.bar_label(bars, fmt="%.3f", padding=3, fontsize=11, color=TEXT, fontweight="bold")
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=12)
    ax.set_ylim(0, 0.85)
    ax.set_ylabel("F2 fuera de fold")
    ax.set_title("Sensibilidad de Random Forest a variables temporales", fontsize=14, fontweight="bold", pad=10)
    ax.grid(axis="y", color=GRID, alpha=0.9)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    _save(fig, "temporal_sensitivity_f2.png")


if __name__ == "__main__":
    comparison()
    temporal()
