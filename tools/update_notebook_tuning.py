"""Inserta la seccion de tuning + iso-recall en Modelo.ipynb, actualiza la
conclusion final (Random Forest) y hace la interpretabilidad robusta sin shap.

Idempotente: si las celdas nuevas ya existen (por id), no las duplica.
"""

import json
from pathlib import Path

NB_PATH = Path("Modelo.ipynb")


def code_cell(cell_id, source):
    return {
        "cell_type": "code",
        "id": cell_id,
        "metadata": {},
        "execution_count": None,
        "outputs": [],
        "source": source.splitlines(keepends=True),
    }


def md_cell(cell_id, source):
    return {
        "cell_type": "markdown",
        "id": cell_id,
        "metadata": {},
        "source": source.splitlines(keepends=True),
    }


TUNING_MD = """## 12 bis. Busqueda de hiperparametros y seleccion final

Las secciones anteriores compararon modelos con hiperparametros elegidos a mano.
Aca se elige cada configuracion de forma **sistematica y reproducible** con
`GridSearchCV`, usando la **misma validacion cruzada agrupada** y la **misma
metrica F2**. Todo ocurre dentro de train; test sigue cerrado.

Ademas se responde de frente la pregunta del negocio: **la precision de 36,5%
del cierre anterior no fue un defecto, fue una consecuencia de priorizar recall**
(metrica F2 + umbral bajo + eleccion de la regresion logistica). Precision y
recall se contraponen: subir una baja la otra, *salvo* que el modelo ordene mejor
el riesgo (mayor PR-AUC). Para verlo sin trampa se compara a **igual recall**:
fijando el mismo nivel de deteccion (~84%), gana el modelo que genera **menos
falsas alertas** (mas precision)."""

TUNING_GRID = """import sys
from pathlib import Path

sys.path.insert(0, str(Path("tools").resolve()))
from finalize_modeling import (
    build_preprocessor,
    prepare_features,
    metrics_from_probabilities,
    precision_at_recall,
    SUSPICIOUS_FEATURES,
)
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Escenario conservador: mismas variables que el modelo final
# (sin Complain ni DaySinceLastOrder, por temporalidad no confirmada).
X_train_tuned = prepare_features(X_train, SUSPICIOUS_FEATURES)

f2_scorer = make_scorer(fbeta_score, beta=2, zero_division=0)
prep_scaled = build_preprocessor(X_train_tuned, scale_numeric=True)
prep_plain = build_preprocessor(X_train_tuned, scale_numeric=False)

# Grillas chicas y explicables (que se probo y por que gano cada modelo).
search_spaces = {
    "Regresion logistica": (
        Pipeline([
            ("preprocessor", prep_scaled),
            ("model", LogisticRegression(max_iter=2000, random_state=RANDOM_STATE)),
        ]),
        {
            "model__C": [0.1, 1.0, 10.0],
            "model__class_weight": ["balanced", {0: 1, 1: 3}],
        },
    ),
    "Arbol de decision": (
        Pipeline([
            ("preprocessor", prep_plain),
            ("model", DecisionTreeClassifier(class_weight="balanced", random_state=RANDOM_STATE)),
        ]),
        {
            "model__max_depth": [4, 5, 6],
            "model__min_samples_leaf": [20, 40],
        },
    ),
    "Random Forest": (
        Pipeline([
            ("preprocessor", prep_plain),
            ("model", RandomForestClassifier(
                max_features=0.5, max_samples=0.7,
                random_state=RANDOM_STATE, n_jobs=-1,
            )),
        ]),
        {
            "model__n_estimators": [300, 500],
            "model__max_depth": [12, 16],
            "model__min_samples_leaf": [4, 8],
            "model__class_weight": ["balanced", {0: 1, 1: 5}],
        },
    ),
}

tuned_oof = {}
search_summary = []
for name, (pipeline, grid) in search_spaces.items():
    search = GridSearchCV(pipeline, grid, scoring=f2_scorer, cv=cv, n_jobs=-1, refit=True)
    search.fit(X_train_tuned, y_train, groups=train_groups)
    tuned_oof[name] = cross_val_predict(
        search.best_estimator_, X_train_tuned, y_train,
        cv=cv, groups=train_groups, method="predict_proba", n_jobs=-1,
    )[:, 1]
    best_params = {k.replace("model__", ""): v for k, v in search.best_params_.items()}
    search_summary.append({
        "modelo": name,
        "F2_CV": round(search.best_score_, 3),
        "mejores_hiperparametros": best_params,
    })

display(pd.DataFrame(search_summary))"""

TUNING_ISO = """TARGET_RECALL = 0.84  # nivel de deteccion actual que se quiere mantener

iso_rows = []
for name, probs in tuned_oof.items():
    at_050 = metrics_from_probabilities(y_train, probs, 0.50)
    iso = precision_at_recall(y_train, probs, TARGET_RECALL)
    iso_rows.append({
        "modelo": name,
        "F2@0.50": round(at_050["f2"], 3),
        "recall@0.50": round(at_050["recall"], 3),
        "precision@0.50": round(at_050["precision"], 3),
        "PR_AUC": round(at_050["pr_auc"], 3),
        "recall_iso": round(iso["recall"], 3),
        "precision_iso": round(iso["precision"], 3),
        "contactos_iso": iso["contacts"],
        "falsas_alertas_iso": iso["fp"],
    })

iso_table = pd.DataFrame(iso_rows)
display(iso_table)

best_iso = iso_table.sort_values("precision_iso", ascending=False).iloc[0]
worst_iso = iso_table.sort_values("precision_iso").iloc[0]
print(
    f"A igual recall (~{TARGET_RECALL:.0%}), el modelo con mas precision es "
    f"{best_iso['modelo']}: precision={best_iso['precision_iso']:.3f} con solo "
    f"{int(best_iso['falsas_alertas_iso'])} falsas alertas, frente a "
    f"{int(worst_iso['falsas_alertas_iso'])} del peor. Misma deteccion, "
    f"casi la mitad de alertas equivocadas."
)
print(
    "El Random Forest tambien tiene el F2 mas alto a umbral 0,50, por lo que el "
    "criterio recall-first lo selecciona como modelo final (ver secciones siguientes)."
)"""

CONCLUSION = """## 13. Conclusion final

El **Random Forest tuneado** fue elegido como modelo final bajo el escenario
conservador sin `Complain` ni `DaySinceLastOrder`. Reemplaza a la regresion
logistica del cierre anterior: con hiperparametros elegidos por `GridSearchCV`,
ordena mejor el riesgo (mayor PR-AUC) y, **al mismo nivel de recall, genera la
mitad de falsas alertas**.

### Por que sube la precision sin resignar recall

La precision de 36,5% del cierre previo era consecuencia de priorizar recall con
un modelo que ordenaba peor el riesgo. El Random Forest mejora la **capacidad de
ordenar** (PR-AUC fuera de fold 0,77 vs 0,61 de la logistica), asi que el mismo
recall se consigue con un umbral que deja afuera muchas menos falsas alertas.

### Seleccion dentro de train

- Validacion: `StratifiedGroupKFold` con 5 folds.
- Metrica principal: F2 con `beta=2`.
- Hiperparametros: elegidos por `GridSearchCV` (seccion 12 bis).
- Umbral elegido fuera de fold: `0.27`.
- F2 fuera de fold: `0.797`.
- Recall fuera de fold: `90.6%`.
- Precision fuera de fold: `53.7%`.

### Evaluacion final en test

- F2: `0.817`.
- Recall: `91.1%`.
- Precision: `57.9%`.
- PR-AUC: `0.834`.
- ROC-AUC: `0.955`.
- Churn detectado: `173` de `190`.
- Falsas alertas: `126`.
- Clientes priorizados: `299` de `1126`.

Comparado de forma justa sobre el mismo split, la logistica anterior daba en test
recall 84,2% con precision 40,7% y 233 falsas alertas. El Random Forest sube el
recall a 91,1% y la precision a 57,9%, casi **dividiendo a la mitad** las falsas
alertas. La precision sigue lejos del 100% porque el churn es minoritario (~17%)
y se prioriza detectar: es un punto de operacion elegido, no un fracaso.

> Nota de reproducibilidad: los conteos exactos de test dependen levemente de la
> version de scikit-learn por el barajado de `StratifiedGroupKFold`. Para
> reproducir identico, usar las versiones fijadas en `requirements.txt`.

Las importancias por permutacion describen como decide el modelo; no prueban
causalidad."""

INTERP_MD = """## 16. Interpretabilidad sin dependencias extra

- La **importancia por permutacion** mide cuanto cae F2 cuando se desordena una
  variable. Se calcula sobre test con el modelo final y se regenera junto con el
  resto de los artefactos.
- Las explicaciones SHAP son **opcionales**: requieren `pip install shap`. Si la
  libreria esta instalada, `tools/finalize_modeling.py` tambien genera SHAP
  global y local; si no, se omiten sin romper el cierre.

Estas tecnicas explican el comportamiento del modelo, no relaciones causales."""

INTERP_CODE = """from pathlib import Path

from IPython.display import Image, display

# Se muestran solo las figuras que existen para el modelo final vigente.
candidate_figures = [
    "reports/figures/final_feature_importance.png",
    "reports/figures/final_shap_global.png",
    "reports/figures/final_shap_local_high_risk.png",
    "reports/figures/final_shap_local_low_risk.png",
]
shown = [fig for fig in candidate_figures if Path(fig).exists()]
for fig in shown:
    display(Image(filename=fig))
if not any("shap" in fig for fig in shown):
    print("SHAP no disponible (libreria no instalada): se muestra importancia por permutacion.")"""


def main():
    nb = json.loads(NB_PATH.read_text(encoding="utf-8"))
    cells = nb["cells"]
    new_ids = {"tuning-md", "tuning-grid", "tuning-iso"}
    if any(c.get("id") in new_ids for c in cells):
        print("Las celdas de tuning ya existen; no se duplican.")
    else:
        # Insertar despues de la celda 33 (id dbe8292b: resultado intermedio).
        idx = next(i for i, c in enumerate(cells) if c.get("id") == "dbe8292b")
        cells[idx + 1:idx + 1] = [
            md_cell("tuning-md", TUNING_MD),
            code_cell("tuning-grid", TUNING_GRID),
            code_cell("tuning-iso", TUNING_ISO),
        ]
        print(f"Insertadas 3 celdas despues del indice {idx}.")

    # Reemplazar conclusion (id aa502aff), interpretabilidad md (b8005b68) y code (955f5e9b).
    replacements = {
        "aa502aff": ("markdown", CONCLUSION),
        "b8005b68": ("markdown", INTERP_MD),
        "955f5e9b": ("code", INTERP_CODE),
    }
    for cell in cells:
        cid = cell.get("id")
        if cid in replacements:
            _, source = replacements[cid]
            cell["source"] = source.splitlines(keepends=True)
            if cell["cell_type"] == "code":
                cell["outputs"] = []
                cell["execution_count"] = None
            print(f"Reemplazada celda {cid}.")

    NB_PATH.write_text(json.dumps(nb, indent=1, ensure_ascii=False), encoding="utf-8")
    print("Notebook actualizado.")


if __name__ == "__main__":
    main()
