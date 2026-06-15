import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.inspection import permutation_importance
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    average_precision_score,
    f1_score,
    fbeta_score,
    precision_recall_curve,
    precision_score,
    recall_score,
    roc_auc_score,
    roc_curve,
)
from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier


RANDOM_STATE = 42
TARGET = "Churn"
ID_COL = "CustomerID"
DATA_PATH = Path("E Commerce Dataset.xlsx - E Comm.csv")
RESULT_PATH = Path("reports/final_modeling_results.json")
FIGURE_DIR = Path("reports/figures")
SUSPICIOUS_FEATURES = ["Complain", "DaySinceLastOrder"]
ENGINEERED_FEATURES = ["OrdersPerTenure", "CashbackPerOrder", "CouponsPerOrder"]
RF_PARAMS = {
    "n_estimators": 476,
    "max_depth": 16,
    "max_features": 0.5,
    "max_samples": 0.7,
    "min_samples_leaf": 4,
    "min_samples_split": 4,
    "class_weight": {0: 1, 1: 5},
    "random_state": RANDOM_STATE,
    "n_jobs": 1,
}


def normalize_categories(data):
    normalized = data.copy()
    normalized["PreferredLoginDevice"] = normalized["PreferredLoginDevice"].replace(
        {"Phone": "Mobile Phone"}
    )
    normalized["PreferredPaymentMode"] = normalized["PreferredPaymentMode"].replace(
        {"COD": "Cash on Delivery", "CC": "Credit Card"}
    )
    normalized["PreferedOrderCat"] = normalized["PreferedOrderCat"].replace(
        {"Mobile": "Mobile Phone"}
    )
    return normalized


def add_business_features(data):
    engineered = data.copy()
    engineered["OrdersPerTenure"] = engineered["OrderCount"] / (
        engineered["Tenure"] + 1
    )
    engineered["CashbackPerOrder"] = engineered["CashbackAmount"] / (
        engineered["OrderCount"] + 1
    )
    engineered["CouponsPerOrder"] = engineered["CouponUsed"] / (
        engineered["OrderCount"] + 1
    )
    return engineered


def prepare_features(data, dropped_features):
    prepared = add_business_features(normalize_categories(data))
    return prepared.drop(columns=dropped_features)


def build_preprocessor(data, scale_numeric):
    categorical = data.select_dtypes(include=["object", "string"]).columns.tolist()
    numeric = [column for column in data.columns if column not in categorical]
    median_features = [
        column for column in ["WarehouseToHome", "CouponUsed"] if column in numeric
    ]
    knn_features = [column for column in numeric if column not in median_features]

    knn_steps = [("imputer", KNNImputer(n_neighbors=5, weights="distance"))]
    median_steps = [("imputer", SimpleImputer(strategy="median"))]
    if scale_numeric:
        knn_steps.append(("scaler", StandardScaler()))
        median_steps.append(("scaler", StandardScaler()))

    return ColumnTransformer(
        [
            ("numeric_knn", Pipeline(knn_steps), knn_features),
            ("numeric_median", Pipeline(median_steps), median_features),
            (
                "categorical",
                Pipeline(
                    [
                        ("imputer", SimpleImputer(strategy="most_frequent")),
                        ("onehot", OneHotEncoder(handle_unknown="ignore")),
                    ]
                ),
                categorical,
            ),
        ]
    )


def build_models(data):
    return {
        "Dummy": Pipeline(
            [
                ("preprocessor", build_preprocessor(data, scale_numeric=False)),
                ("model", DummyClassifier(strategy="most_frequent")),
            ]
        ),
        "Regresion logistica": Pipeline(
            [
                ("preprocessor", build_preprocessor(data, scale_numeric=True)),
                (
                    "model",
                    LogisticRegression(
                        class_weight="balanced",
                        max_iter=2000,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Arbol de decision": Pipeline(
            [
                ("preprocessor", build_preprocessor(data, scale_numeric=False)),
                (
                    "model",
                    DecisionTreeClassifier(
                        class_weight="balanced",
                        max_depth=5,
                        min_samples_leaf=20,
                        random_state=RANDOM_STATE,
                    ),
                ),
            ]
        ),
        "Random Forest": Pipeline(
            [
                ("preprocessor", build_preprocessor(data, scale_numeric=False)),
                ("model", RandomForestClassifier(**RF_PARAMS)),
            ]
        ),
    }


def metrics_from_probabilities(y_true, probabilities, threshold):
    predictions = (probabilities >= threshold).astype(int)
    return {
        "threshold": float(threshold),
        "f2": float(fbeta_score(y_true, predictions, beta=2, zero_division=0)),
        "recall": float(recall_score(y_true, predictions, zero_division=0)),
        "precision": float(precision_score(y_true, predictions, zero_division=0)),
        "f1": float(f1_score(y_true, predictions, zero_division=0)),
        "pr_auc": float(average_precision_score(y_true, probabilities)),
        "roc_auc": float(roc_auc_score(y_true, probabilities)),
        "accuracy": float(accuracy_score(y_true, predictions)),
        "contacts": int(predictions.sum()),
        "tp": int(((predictions == 1) & (np.asarray(y_true) == 1)).sum()),
        "fp": int(((predictions == 1) & (np.asarray(y_true) == 0)).sum()),
        "fn": int(((predictions == 0) & (np.asarray(y_true) == 1)).sum()),
        "tn": int(((predictions == 0) & (np.asarray(y_true) == 0)).sum()),
    }


def choose_threshold(y_true, probabilities):
    rows = [
        metrics_from_probabilities(y_true, probabilities, threshold)
        for threshold in np.round(np.arange(0.10, 0.81, 0.01), 2)
    ]
    table = pd.DataFrame(rows)
    best = table.sort_values(
        ["f2", "precision", "threshold"], ascending=[False, False, False]
    ).iloc[0]

    operational = table.loc[table["recall"] >= 0.80].sort_values(
        ["contacts", "precision"], ascending=[True, False]
    )
    operational_row = operational.iloc[0] if not operational.empty else best
    return best.to_dict(), operational_row.to_dict(), table


def clean_feature_name(name):
    cleaned = name.split("__", 1)[-1]
    return cleaned.replace("_", " ")


def original_feature_name(transformed_name, original_columns):
    cleaned = transformed_name.split("__", 1)[-1]
    for column in sorted(original_columns, key=len, reverse=True):
        if cleaned == column or cleaned.startswith(f"{column}_"):
            return column
    return cleaned


def save_model_comparison_plot(comparison):
    plot_data = comparison.loc[comparison["model"] != "Dummy"].copy()
    x = np.arange(len(plot_data))
    width = 0.22
    fig, ax = plt.subplots(figsize=(10, 5.5))
    for offset, metric, label in [
        (-width, "f2", "F2"),
        (0, "recall", "Recall"),
        (width, "precision", "Precision"),
    ]:
        ax.bar(x + offset, plot_data[metric], width, label=label)
    ax.set_xticks(x)
    ax.set_xticklabels(plot_data["model"])
    ax.set_ylim(0, 1)
    ax.set_ylabel("Metrica fuera de fold")
    ax.set_title("Comparacion final de modelos sin variables temporalmente dudosas")
    ax.legend()
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "final_model_comparison_cv.png", dpi=180)
    plt.close(fig)


def save_temporal_plot(sensitivity):
    fig, ax = plt.subplots(figsize=(10, 5.5))
    x = np.arange(len(sensitivity))
    ax.bar(x, sensitivity["f2"], color="#4472C4")
    ax.set_xticks(x)
    ax.set_xticklabels(sensitivity["scenario"], rotation=15, ha="right")
    ax.set_ylim(0, 1)
    ax.set_ylabel("F2 fuera de fold")
    ax.set_title("Sensibilidad de Random Forest a variables temporales")
    ax.grid(axis="y", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "temporal_sensitivity_f2.png", dpi=180)
    plt.close(fig)


def save_roc_pr_plot(y_true, probabilities, metrics):
    fpr, tpr, _ = roc_curve(y_true, probabilities)
    precision, recall, _ = precision_recall_curve(y_true, probabilities)
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    axes[0].plot(fpr, tpr, label=f"ROC-AUC = {metrics['roc_auc']:.3f}")
    axes[0].plot([0, 1], [0, 1], linestyle="--", color="gray")
    axes[0].set(xlabel="Tasa de falsos positivos", ylabel="Recall", title="Curva ROC en test")
    axes[0].legend()
    axes[0].grid(alpha=0.25)

    axes[1].plot(recall, precision, label=f"PR-AUC = {metrics['pr_auc']:.3f}")
    axes[1].axhline(np.mean(y_true), linestyle="--", color="gray", label="Base churn")
    axes[1].set(xlabel="Recall", ylabel="Precision", title="Curva Precision-Recall en test")
    axes[1].legend()
    axes[1].grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "final_test_roc_pr.png", dpi=180)
    plt.close(fig)


def save_confusion_matrix(y_true, predictions):
    fig, ax = plt.subplots(figsize=(6, 5))
    ConfusionMatrixDisplay.from_predictions(
        y_true,
        predictions,
        display_labels=["Permanece", "Churn"],
        cmap="Blues",
        colorbar=False,
        ax=ax,
    )
    ax.set_title("Matriz de confusion final en test")
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "final_test_confusion_matrix.png", dpi=180)
    plt.close(fig)


def save_permutation_importance(model, X_test, y_test):
    result = permutation_importance(
        model,
        X_test,
        y_test,
        scoring=lambda estimator, X, y: fbeta_score(
            y,
            (estimator.predict_proba(X)[:, 1] >= 0.5).astype(int),
            beta=2,
            zero_division=0,
        ),
        n_repeats=10,
        random_state=RANDOM_STATE,
        n_jobs=1,
    )
    importance = (
        pd.DataFrame(
            {
                "feature": X_test.columns,
                "importance_mean": result.importances_mean,
                "importance_std": result.importances_std,
            }
        )
        .sort_values("importance_mean", ascending=False)
        .reset_index(drop=True)
    )
    top = importance.head(12).sort_values("importance_mean")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["feature"], top["importance_mean"], xerr=top["importance_std"])
    ax.set_xlabel("Caida media de F2 al permutar")
    ax.set_title("Importancia por permutacion en test")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "final_feature_importance.png", dpi=180)
    plt.close(fig)
    return importance


def save_shap_artifacts(model, X_test, probabilities, customer_ids):
    preprocessor = model.named_steps["preprocessor"]
    forest = model.named_steps["model"]
    transformed = preprocessor.transform(X_test)
    if hasattr(transformed, "toarray"):
        transformed = transformed.toarray()
    feature_names = preprocessor.get_feature_names_out()
    sample_size = min(500, transformed.shape[0])
    sample_positions = np.linspace(
        0, transformed.shape[0] - 1, sample_size, dtype=int
    )
    transformed_sample = transformed[sample_positions]

    if isinstance(forest, RandomForestClassifier):
        explainer = shap.TreeExplainer(forest)
        shap_values = explainer.shap_values(transformed_sample)
        if isinstance(shap_values, list):
            positive_values = np.asarray(shap_values[1])
            expected_value = np.asarray(explainer.expected_value)[1]
        elif np.asarray(shap_values).ndim == 3:
            positive_values = np.asarray(shap_values)[:, :, 1]
            expected_value = np.asarray(explainer.expected_value)[1]
        else:
            positive_values = np.asarray(shap_values)
            expected_value = np.asarray(explainer.expected_value).reshape(-1)[0]
    else:
        explainer = shap.LinearExplainer(forest, transformed_sample)
        sample_explanation = explainer(transformed_sample)
        positive_values = np.asarray(sample_explanation.values)
        expected_value = np.asarray(sample_explanation.base_values).reshape(-1)[0]

    original_columns = list(X_test.columns)
    groups = [
        original_feature_name(name, original_columns) for name in feature_names
    ]
    shap_global = (
        pd.DataFrame(
            {
                "feature": groups,
                "mean_abs_shap": np.abs(positive_values).mean(axis=0),
            }
        )
        .groupby("feature", as_index=False)["mean_abs_shap"]
        .sum()
        .sort_values("mean_abs_shap", ascending=False)
        .reset_index(drop=True)
    )

    top = shap_global.head(12).sort_values("mean_abs_shap")
    fig, ax = plt.subplots(figsize=(9, 6))
    ax.barh(top["feature"], top["mean_abs_shap"], color="#70AD47")
    ax.set_xlabel("Impacto SHAP medio absoluto")
    ax.set_title("SHAP global simplificado del modelo final")
    ax.grid(axis="x", alpha=0.25)
    fig.tight_layout()
    fig.savefig(FIGURE_DIR / "final_shap_global.png", dpi=180)
    plt.close(fig)

    local_positions = {
        "high_risk": int(np.argmax(probabilities)),
        "low_risk": int(np.argmin(probabilities)),
    }
    local_rows = []
    for label, position in local_positions.items():
        transformed_row = preprocessor.transform(X_test.iloc[[position]])
        if hasattr(transformed_row, "toarray"):
            transformed_row = transformed_row.toarray()
        if isinstance(forest, RandomForestClassifier):
            row_values = explainer.shap_values(transformed_row)
            if isinstance(row_values, list):
                positive_row = np.asarray(row_values[1])[0]
            elif np.asarray(row_values).ndim == 3:
                positive_row = np.asarray(row_values)[0, :, 1]
            else:
                positive_row = np.asarray(row_values)[0]
        else:
            positive_row = np.asarray(explainer(transformed_row).values)[0]

        explanation = shap.Explanation(
            values=positive_row,
            base_values=expected_value,
            data=np.asarray(transformed_row)[0],
            feature_names=[clean_feature_name(name) for name in feature_names],
        )
        shap.plots.waterfall(explanation, max_display=12, show=False)
        plt.title(
            f"SHAP local - cliente {int(customer_ids.iloc[position])} "
            f"(riesgo {probabilities[position]:.1%})"
        )
        plt.tight_layout()
        plt.savefig(FIGURE_DIR / f"final_shap_local_{label}.png", dpi=180)
        plt.close()
        local_rows.append(
            {
                "example": label,
                "customer_id": int(customer_ids.iloc[position]),
                "probability": float(probabilities[position]),
            }
        )
    return shap_global, local_rows


def profile_groups(data):
    normalized = data.astype(object).where(data.notna(), "__MISSING__").astype(str)
    return pd.util.hash_pandas_object(
        normalized,
        index=False,
    ).astype(str)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--force",
        action="store_true",
        help="Repite la evaluacion final de test y reemplaza los artefactos.",
    )
    args = parser.parse_args()
    if RESULT_PATH.exists() and not args.force:
        raise SystemExit(
            f"{RESULT_PATH} ya existe. No se vuelve a abrir test sin --force."
        )

    FIGURE_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    X = df.drop(columns=[ID_COL, TARGET])
    y = df[TARGET]
    customer_ids = df[ID_COL]
    all_groups = profile_groups(X)
    outer_split = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )
    train_positions, test_positions = next(
        outer_split.split(X, y, groups=all_groups)
    )
    X_train_raw = X.iloc[train_positions].copy()
    X_test_raw = X.iloc[test_positions].copy()
    y_train = y.iloc[train_positions].copy()
    y_test = y.iloc[test_positions].copy()
    train_groups = all_groups.iloc[train_positions].copy()
    test_groups = all_groups.iloc[test_positions].copy()
    test_customer_ids = customer_ids.iloc[test_positions].copy()
    if set(train_groups).intersection(set(test_groups)):
        raise RuntimeError("Hay perfiles duplicados compartidos entre train y test.")

    cv = StratifiedGroupKFold(
        n_splits=5,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    scenarios = {
        "Completo": [],
        "Sin Complain": ["Complain"],
        "Sin DaySinceLastOrder": ["DaySinceLastOrder"],
        "Conservador: sin ambas": SUSPICIOUS_FEATURES,
    }
    sensitivity_rows = []
    for scenario, dropped in scenarios.items():
        X_train = prepare_features(X_train_raw, dropped)
        rf_model = build_models(X_train)["Random Forest"]
        probabilities = cross_val_predict(
            rf_model,
            X_train,
            y_train,
            cv=cv,
            groups=train_groups,
            method="predict_proba",
            n_jobs=1,
        )[:, 1]
        row = metrics_from_probabilities(y_train, probabilities, 0.5)
        row["scenario"] = scenario
        row["dropped_features"] = dropped
        sensitivity_rows.append(row)

    sensitivity = pd.DataFrame(sensitivity_rows)
    conservative_drop = SUSPICIOUS_FEATURES
    X_train = prepare_features(X_train_raw, conservative_drop)
    X_test = prepare_features(X_test_raw, conservative_drop)
    models = build_models(X_train)
    comparison_rows = []
    oof_probabilities = {}
    for model_name, model in models.items():
        probabilities = cross_val_predict(
            model,
            X_train,
            y_train,
            cv=cv,
            groups=train_groups,
            method="predict_proba",
            n_jobs=1,
        )[:, 1]
        oof_probabilities[model_name] = probabilities
        row = metrics_from_probabilities(y_train, probabilities, 0.5)
        row["model"] = model_name
        comparison_rows.append(row)
    comparison = pd.DataFrame(comparison_rows)

    eligible = comparison.loc[comparison["model"] != "Dummy"].sort_values(
        ["f2", "pr_auc", "precision"], ascending=False
    )
    selected_model_name = eligible.iloc[0]["model"]
    selected_model = models[selected_model_name]
    selected_oof = oof_probabilities[selected_model_name]
    best_threshold, operational_threshold, threshold_table = choose_threshold(
        y_train, selected_oof
    )

    selected_model.fit(X_train, y_train)
    test_probabilities = selected_model.predict_proba(X_test)[:, 1]
    final_threshold = float(best_threshold["threshold"])
    test_metrics = metrics_from_probabilities(
        y_test, test_probabilities, final_threshold
    )
    test_predictions = (test_probabilities >= final_threshold).astype(int)

    save_model_comparison_plot(comparison)
    save_temporal_plot(sensitivity)
    save_roc_pr_plot(y_test, test_probabilities, test_metrics)
    save_confusion_matrix(y_test, test_predictions)
    permutation = save_permutation_importance(
        selected_model, X_test, y_test
    )
    shap_global, local_examples = save_shap_artifacts(
        selected_model,
        X_test,
        test_probabilities,
        test_customer_ids.reset_index(drop=True),
    )

    output = {
        "protocol": {
            "random_state": RANDOM_STATE,
            "split": (
                "80/20 estratificado por grupos de perfiles identicos; "
                "sin duplicados compartidos entre train y test"
            ),
            "cv": "StratifiedGroupKFold 5 folds",
            "selection_metric": "F2 beta=2",
            "test_used_for_selection": False,
            "test_evaluation_frozen": True,
            "temporal_policy": (
                "Se excluyen Complain y DaySinceLastOrder por falta de "
                "confirmacion temporal en los artefactos del proyecto."
            ),
        },
        "selected_model": selected_model_name,
        "selected_features_dropped": conservative_drop,
        "model_comparison_oof_threshold_050": comparison.to_dict(orient="records"),
        "temporal_sensitivity_rf_threshold_050": sensitivity.to_dict(
            orient="records"
        ),
        "selected_threshold_oof": best_threshold,
        "operational_threshold_oof_recall_at_least_080": operational_threshold,
        "final_test_metrics": test_metrics,
        "final_test_rows": int(len(y_test)),
        "final_test_churn": int(y_test.sum()),
        "train_rows": int(len(y_train)),
        "train_churn": int(y_train.sum()),
        "duplicate_feature_rows_detected": int(X.duplicated().sum()),
        "shared_profile_groups_train_test": 0,
        "permutation_importance": permutation.to_dict(orient="records"),
        "shap_global": shap_global.to_dict(orient="records"),
        "shap_local_examples": local_examples,
        "rf_params": RF_PARAMS,
        "figures": [
            "reports/figures/final_model_comparison_cv.png",
            "reports/figures/temporal_sensitivity_f2.png",
            "reports/figures/final_test_roc_pr.png",
            "reports/figures/final_test_confusion_matrix.png",
            "reports/figures/final_feature_importance.png",
            "reports/figures/final_shap_global.png",
            "reports/figures/final_shap_local_high_risk.png",
            "reports/figures/final_shap_local_low_risk.png",
        ],
        "threshold_table_oof": threshold_table.to_dict(orient="records"),
    }
    RESULT_PATH.write_text(json.dumps(output, indent=2), encoding="utf-8")
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
