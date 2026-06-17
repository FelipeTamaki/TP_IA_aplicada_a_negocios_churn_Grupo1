"""Prototipo: tuning sistematico (GridSearchCV) + comparacion iso-recall.

Reutiliza las funciones del cierre final (finalize_modeling.py) para no duplicar
el preprocesamiento ni el protocolo de split agrupado. No abre test: todo el
trabajo es out-of-fold sobre train.
"""

import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import fbeta_score, make_scorer
from sklearn.model_selection import (
    GridSearchCV,
    StratifiedGroupKFold,
    cross_val_predict,
)
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier

sys.path.insert(0, str(Path(__file__).resolve().parent))
from finalize_modeling import (  # noqa: E402
    DATA_PATH,
    ID_COL,
    RANDOM_STATE,
    SUSPICIOUS_FEATURES,
    TARGET,
    build_preprocessor,
    metrics_from_probabilities,
    prepare_features,
    profile_groups,
)

F2_SCORER = make_scorer(fbeta_score, beta=2, zero_division=0)
TARGET_RECALL = 0.84  # nivel de deteccion actual que se quiere mantener


def load_train():
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=[ID_COL, TARGET])
    y = df[TARGET]
    groups = profile_groups(X)
    outer = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    train_idx, _ = next(outer.split(X, y, groups=groups))
    X_train = prepare_features(X.iloc[train_idx].copy(), SUSPICIOUS_FEATURES)
    y_train = y.iloc[train_idx].copy()
    g_train = groups.iloc[train_idx].copy()
    return X_train, y_train, g_train


def model_grids(preprocessor_scaled, preprocessor_plain):
    """Devuelve (pipeline, grid) por modelo. Grids chicos y explicables."""
    log = Pipeline([
        ("preprocessor", preprocessor_scaled),
        ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
    ])
    log_grid = {
        "model__C": [0.1, 1.0, 10.0],
        "model__class_weight": ["balanced", {0: 1, 1: 3}],
    }

    tree = Pipeline([
        ("preprocessor", preprocessor_plain),
        ("model", DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE)),
    ])
    tree_grid = {
        "model__max_depth": [4, 5, 6],
        "model__min_samples_leaf": [20, 40],
    }

    rf = Pipeline([
        ("preprocessor", preprocessor_plain),
        ("model", RandomForestClassifier(
            max_features=0.5, max_samples=0.7, random_state=RANDOM_STATE, n_jobs=1,
        )),
    ])
    rf_grid = {
        "model__n_estimators": [300, 500],
        "model__max_depth": [12, 16],
        "model__min_samples_leaf": [4, 8],
        "model__class_weight": ["balanced", {0: 1, 1: 5}],
    }
    return {
        "Regresion logistica": (log, log_grid),
        "Arbol de decision": (tree, tree_grid),
        "Random Forest": (rf, rf_grid),
    }


def precision_at_recall(y_true, probs, target_recall):
    """Umbral mas alto cuyo recall OOF >= target_recall, y sus metricas."""
    best = None
    for thr in np.round(np.arange(0.05, 0.96, 0.01), 2):
        m = metrics_from_probabilities(y_true, probs, thr)
        if m["recall"] >= target_recall:
            if best is None or thr > best["threshold"]:
                best = m
    if best is None:  # no se alcanza ese recall ni con umbral minimo
        best = metrics_from_probabilities(y_true, probs, 0.05)
    return best


def main():
    X_train, y_train, g_train = load_train()
    cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    preprocessor_scaled = build_preprocessor(X_train, scale_numeric=True)
    preprocessor_plain = build_preprocessor(X_train, scale_numeric=False)

    print(f"Train: {len(X_train)} filas, churn={int(y_train.sum())} "
          f"({y_train.mean():.1%})")

    results = {}
    for name, (pipe, grid) in model_grids(preprocessor_scaled, preprocessor_plain).items():
        search = GridSearchCV(
            pipe, grid, scoring=F2_SCORER, cv=cv, n_jobs=-1, refit=True,
        )
        search.fit(X_train, y_train, groups=g_train)
        best_pipe = search.best_estimator_
        oof = cross_val_predict(
            best_pipe, X_train, y_train, cv=cv, groups=g_train,
            method="predict_proba", n_jobs=-1,
        )[:, 1]
        at_050 = metrics_from_probabilities(y_train, oof, 0.5)
        iso = precision_at_recall(y_train, oof, TARGET_RECALL)
        results[name] = {
            "best_params": {k.replace("model__", ""): v for k, v in search.best_params_.items()},
            "best_cv_f2": float(search.best_score_),
            "oof_050": at_050,
            "iso_recall": iso,
        }
        print(f"\n=== {name} ===")
        print("  best_params:", results[name]["best_params"])
        print(f"  CV F2 (mejor grid): {search.best_score_:.3f}")
        print(f"  OOF @0.50  -> F2={at_050['f2']:.3f} recall={at_050['recall']:.3f} "
              f"prec={at_050['precision']:.3f} contactos={at_050['contacts']}")
        print(f"  OOF iso-recall (>= {TARGET_RECALL:.0%}) @thr={iso['threshold']:.2f} "
              f"-> recall={iso['recall']:.3f} prec={iso['precision']:.3f} "
              f"contactos={iso['contacts']} (TP={iso['tp']} FP={iso['fp']} FN={iso['fn']})")

    out = Path("reports/tuning_prototype.json")
    out.write_text(json.dumps(results, indent=2), encoding="utf-8")
    print(f"\nGuardado: {out}")


if __name__ == "__main__":
    main()
