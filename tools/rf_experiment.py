import json
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import randint, uniform
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import KNNImputer, SimpleImputer
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    f1_score,
    fbeta_score,
    make_scorer,
    precision_score,
    recall_score,
)
from sklearn.model_selection import (
    RandomizedSearchCV,
    StratifiedKFold,
    cross_val_predict,
    cross_validate,
    train_test_split,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


RANDOM_STATE = 42
df = pd.read_csv("E Commerce Dataset.xlsx - E Comm.csv")
X = df.drop(columns=["CustomerID", "Churn"])
y = df["Churn"]
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=RANDOM_STATE,
    stratify=y,
)


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


X_train = normalize_categories(X_train)
categorical = X_train.select_dtypes(include=["object", "string"]).columns.tolist()
numeric = [column for column in X_train.columns if column not in categorical]
median_features = ["WarehouseToHome", "CouponUsed"]
knn_features = [column for column in numeric if column not in median_features]

preprocessor = ColumnTransformer(
    [
        (
            "numeric_knn",
            Pipeline(
                [
                    ("imputer", KNNImputer(n_neighbors=5, weights="distance")),
                ]
            ),
            knn_features,
        ),
        (
            "numeric_median",
            Pipeline([("imputer", SimpleImputer(strategy="median"))]),
            median_features,
        ),
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

pipeline = Pipeline(
    [
        ("preprocessor", preprocessor),
        (
            "model",
            RandomForestClassifier(
                random_state=RANDOM_STATE,
                n_jobs=1,
            ),
        ),
    ]
)

param_distributions = {
    "model__n_estimators": randint(250, 701),
    "model__max_depth": [5, 7, 9, 12, 16, None],
    "model__min_samples_split": randint(4, 31),
    "model__min_samples_leaf": randint(2, 21),
    "model__max_features": ["sqrt", "log2", 0.5, 0.75],
    "model__class_weight": [
        "balanced",
        "balanced_subsample",
        {0: 1, 1: 2},
        {0: 1, 1: 3},
        {0: 1, 1: 4},
        {0: 1, 1: 5},
    ],
    "model__max_samples": [None, 0.70, 0.85],
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
f2_scorer = make_scorer(fbeta_score, beta=2, zero_division=0)

search = RandomizedSearchCV(
    pipeline,
    param_distributions=param_distributions,
    n_iter=30,
    scoring=f2_scorer,
    cv=cv,
    random_state=RANDOM_STATE,
    n_jobs=1,
    return_train_score=True,
    verbose=1,
)
search.fit(X_train, y_train)

best_pipeline = search.best_estimator_
scoring = {
    "f2": f2_scorer,
    "recall": make_scorer(recall_score, zero_division=0),
    "precision": make_scorer(precision_score, zero_division=0),
    "f1": make_scorer(f1_score, zero_division=0),
    "pr_auc": "average_precision",
    "accuracy": "accuracy",
}
cv_result = cross_validate(
    best_pipeline,
    X_train,
    y_train,
    scoring=scoring,
    cv=cv,
    return_train_score=True,
    n_jobs=1,
)

probabilities = cross_val_predict(
    best_pipeline,
    X_train,
    y_train,
    cv=cv,
    method="predict_proba",
    n_jobs=1,
)[:, 1]

threshold_rows = []
for threshold in np.round(np.arange(0.15, 0.81, 0.01), 2):
    predictions = (probabilities >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_train, predictions).ravel()
    threshold_rows.append(
        {
            "threshold": float(threshold),
            "f2": fbeta_score(y_train, predictions, beta=2, zero_division=0),
            "recall": recall_score(y_train, predictions, zero_division=0),
            "precision": precision_score(y_train, predictions, zero_division=0),
            "f1": f1_score(y_train, predictions, zero_division=0),
            "pr_auc": average_precision_score(y_train, probabilities),
            "contacts": int(tp + fp),
            "tp": int(tp),
            "fp": int(fp),
            "fn": int(fn),
            "tn": int(tn),
        }
    )

threshold_table = pd.DataFrame(threshold_rows)
best_threshold = threshold_table.sort_values(
    ["f2", "precision", "threshold"], ascending=[False, False, False]
).iloc[0]

top_search = (
    pd.DataFrame(search.cv_results_)
    .sort_values("rank_test_score")
    .head(10)[
        [
            "rank_test_score",
            "mean_test_score",
            "std_test_score",
            "mean_train_score",
            "params",
        ]
    ]
)

output = {
    "best_params": search.best_params_,
    "search_best_f2": search.best_score_,
    "fixed_cv": {
        key: {
            "mean": float(values.mean()),
            "std": float(values.std()),
        }
        for key, values in cv_result.items()
        if key.startswith("test_") or key == "train_f2"
    },
    "best_threshold": best_threshold.to_dict(),
    "threshold_050": threshold_table.loc[
        threshold_table["threshold"] == 0.50
    ].iloc[0].to_dict(),
    "top_search": top_search.to_dict(orient="records"),
    "test_rows_reserved": len(X_test),
}

Path("reports/rf_experiment.json").write_text(
    json.dumps(output, indent=2),
    encoding="utf-8",
)
print(json.dumps(output, indent=2))
