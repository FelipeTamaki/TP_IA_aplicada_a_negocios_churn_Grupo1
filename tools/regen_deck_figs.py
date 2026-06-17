"""Regenera figuras slide-first para la presentacion tecnica.

Lee los datos ya calculados de reports/final_modeling_results.json y el CSV raw:
no reentrena nada.
"""

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
FIG = ROOT / "reports" / "figures"
DATA = json.loads((ROOT / "reports" / "final_modeling_results.json").read_text(encoding="utf-8"))
CSV = ROOT / "E Commerce Dataset.xlsx - E Comm.csv"

# Paleta alineada al deck
TEAL = "#0E7C86"
ORANGE = "#E8833A"
SLATE = "#6A7A82"
TEXT = "#1F2D34"
GRID = "#DCE6E9"

plt.rcParams.update({
    "font.size": 14,
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


def eda_tenure():
    import pandas as pd

    df = pd.read_csv(CSV)
    d = df[["Tenure", "Churn"]].dropna().copy()
    bins = [-0.1, 1, 3, 6, 12, 24, 999]
    labels = ["0-1", "2-3", "4-6", "7-12", "13-24", "25+"]
    d["tenure_group"] = pd.cut(d["Tenure"], bins=bins, labels=labels)
    agg = (
        d.groupby("tenure_group", observed=False)
        .agg(churn_rate=("Churn", "mean"), clientes=("Churn", "size"))
        .reset_index()
    )

    fig, ax = plt.subplots(figsize=(12.0, 3.6))
    colors = [ORANGE if i == 0 else TEAL for i in range(len(agg))]
    bars = ax.bar(agg["tenure_group"].astype(str), agg["churn_rate"] * 100, color=colors, width=0.72)
    ax.bar_label(bars, labels=[f"{v:.0f}%" for v in agg["churn_rate"] * 100], padding=3, fontsize=13, fontweight="bold")
    ax.set_title("Churn segun antiguedad del cliente", fontsize=17, fontweight="bold", pad=10)
    ax.set_xlabel("Meses como cliente")
    ax.set_ylabel("% churn")
    ax.set_ylim(0, max(agg["churn_rate"] * 100) * 1.22)
    ax.grid(axis="y", color=GRID, alpha=0.9)
    ax.set_axisbelow(True)
    for spine in ("top", "right"):
        ax.spines[spine].set_visible(False)
    ax.text(
        0.0,
        -0.26,
        "Lectura: el riesgo cae fuerte despues del primer tramo de antiguedad.",
        transform=ax.transAxes,
        fontsize=12.5,
        color=SLATE,
    )
    _save(fig, "h1_tenure.png")


def eda_complain():
    import pandas as pd

    df = pd.read_csv(CSV)
    d = df[["Complain", "Churn"]].dropna().copy()
    d["Complain"] = d["Complain"].map({0: "Sin reclamo", 1: "Con reclamo"}).fillna(d["Complain"].astype(str))
    order = ["Sin reclamo", "Con reclamo"]
    rates = d.groupby("Complain")["Churn"].mean().reindex(order) * 100
    counts = d.groupby("Complain")["Churn"].size().reindex(order)

    fig, ax = plt.subplots(figsize=(12.0, 3.6))
    y = np.arange(len(order))
    bars = ax.barh(y, rates, color=[TEAL, ORANGE], height=0.52)
    ax.bar_label(bars, labels=[f"{v:.1f}%" for v in rates], padding=6, fontsize=15, fontweight="bold")
    ax.set_yticks(y)
    ax.set_yticklabels([f"{label}\n(n={int(counts[label]):,})".replace(",", ".") for label in order], fontsize=13)
    ax.set_xlim(0, max(rates) * 1.25)
    ax.set_xlabel("% churn dentro del grupo")
    ax.set_title("El reclamo aparece fuertemente asociado al churn", fontsize=17, fontweight="bold", pad=10)
    ax.grid(axis="x", color=GRID, alpha=0.9)
    ax.set_axisbelow(True)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.tick_params(axis="y", length=0)
    ax.text(
        0.0,
        -0.26,
        "Lectura: la asociacion es clara, pero la temporalidad no queda demostrada en el dataset.",
        transform=ax.transAxes,
        fontsize=12.5,
        color=SLATE,
    )
    _save(fig, "h2_complain.png")


def interpretability_combo():
    import pandas as pd

    perm = pd.DataFrame(DATA["permutation_importance"]).head(7).sort_values("importance_mean")
    shap = pd.DataFrame(DATA["shap_global"]).head(7).sort_values("mean_abs_shap")

    fig, axes = plt.subplots(2, 1, figsize=(10.8, 6.0), gridspec_kw={"hspace": 0.52})

    axes[0].barh(perm["feature"], perm["importance_mean"], color=TEAL)
    axes[0].set_title("Importancia por permutacion", loc="left", fontsize=17, fontweight="bold", pad=8)
    axes[0].set_xlabel("Caida media al permutar")
    axes[0].bar_label(axes[0].containers[0], fmt="%.3f", padding=4, fontsize=11)

    axes[1].barh(shap["feature"], shap["mean_abs_shap"], color=ORANGE)
    axes[1].set_title("SHAP global", loc="left", fontsize=17, fontweight="bold", pad=8)
    axes[1].set_xlabel("Impacto absoluto medio")
    axes[1].bar_label(axes[1].containers[0], fmt="%.2f", padding=4, fontsize=11)

    for ax in axes:
        ax.grid(axis="x", color=GRID, alpha=0.9)
        ax.set_axisbelow(True)
        ax.tick_params(axis="y", labelsize=12)
        ax.tick_params(axis="x", labelsize=11)
        for spine in ("top", "right", "left"):
            ax.spines[spine].set_visible(False)
    _save(fig, "final_interpretability_combo.png")


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
    eda_tenure()
    eda_complain()
    comparison()
    temporal()
    interpretability_combo()
