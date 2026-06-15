import json
from pathlib import Path

import nbformat


NOTEBOOK_PATH = Path("Modelo.ipynb")
RESULT_PATH = Path("reports/final_modeling_results.json")


def set_source(cell, text):
    cell["source"] = text.strip() + "\n"


notebook = nbformat.read(NOTEBOOK_PATH, as_version=4)
notebook.cells = notebook.cells[:36]
results = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
test = results["final_test_metrics"]
threshold = results["selected_threshold_oof"]

set_source(
    notebook.cells[0],
    """
# Modelado de churn - Cierre final

Este notebook documenta la construccion de baselines, el arbol obligatorio y el cierre del modelo final.

El protocolo final incorpora dos correcciones conservadoras:

- perfiles con variables explicativas identicas se mantienen en el mismo grupo para que no aparezcan simultaneamente en train y test;
- `Complain` y `DaySinceLastOrder` se excluyen del modelo final porque no existe evidencia suficiente sobre su disponibilidad antes del churn.

La metrica principal es F2 (`beta=2`), complementada con recall, precision, PR-AUC, ROC-AUC y volumen de contactos.
""",
)

cell_1 = notebook.cells[1]["source"]
cell_1 = cell_1.replace(
    "from sklearn.model_selection import train_test_split",
    "from sklearn.model_selection import StratifiedGroupKFold",
)
set_source(notebook.cells[1], cell_1)

set_source(
    notebook.cells[4],
    """
## 2. Split train/test estratificado por perfiles

La auditoria detecto 556 filas con variables explicativas exactamente duplicadas. Un split aleatorio dejaba perfiles identicos en train y test, lo que podia inflar las metricas.

Para evitarlo se utiliza `StratifiedGroupKFold`: conserva aproximadamente la proporcion de churn y obliga a que todas las copias de un mismo perfil queden del mismo lado. El primer fold se reserva como test final y los cuatro restantes forman train.
""",
)

set_source(
    notebook.cells[5],
    """
def profile_groups(data):
    normalized = data.astype(object).where(data.notna(), "__MISSING__").astype(str)
    return pd.util.hash_pandas_object(normalized, index=False).astype(str)


profile_group = profile_groups(X)
outer_split = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)
train_positions, test_positions = next(
    outer_split.split(X, y, groups=profile_group)
)

X_train = X.iloc[train_positions].copy()
X_test = X.iloc[test_positions].copy()
y_train = y.iloc[train_positions].copy()
y_test = y.iloc[test_positions].copy()
train_groups = profile_group.iloc[train_positions].copy()
test_groups = profile_group.iloc[test_positions].copy()

split_summary = pd.DataFrame({
    "dataset": ["total", "train", "test"],
    "filas": [len(y), len(y_train), len(y_test)],
    "clientes_churn": [int(y.sum()), int(y_train.sum()), int(y_test.sum())],
    "clientes_no_churn": [
        int((y == 0).sum()),
        int((y_train == 0).sum()),
        int((y_test == 0).sum()),
    ],
    "tasa_churn_%": [
        round(y.mean() * 100, 2),
        round(y_train.mean() * 100, 2),
        round(y_test.mean() * 100, 2),
    ],
})

split_summary
""",
)

set_source(
    notebook.cells[6],
    """
## 3. Validaciones del split

Estas validaciones confirman que no se perdieron filas, que los identificadores no se superponen y, especialmente, que ningun perfil duplicado aparece simultaneamente en train y test.
""",
)

set_source(
    notebook.cells[7],
    """
train_ids = set(df_raw.loc[X_train.index, ID_COL])
test_ids = set(df_raw.loc[X_test.index, ID_COL])
shared_profiles = set(train_groups).intersection(set(test_groups))

assert len(X_train) + len(X_test) == len(df_raw)
assert len(train_ids.intersection(test_ids)) == 0
assert X_train.index.intersection(X_test.index).empty
assert y_train.sum() + y_test.sum() == y.sum()
assert len(shared_profiles) == 0

print("Validaciones OK")
print(f"Filas duplicadas por features detectadas: {X.duplicated().sum():,}")
print(f"Filas train: {len(X_train):,}")
print(f"Filas test: {len(X_test):,}")
print(f"Churn train: {y_train.mean() * 100:.2f}%")
print(f"Churn test: {y_test.mean() * 100:.2f}%")
print(f"Perfiles compartidos train/test: {len(shared_profiles)}")
""",
)

cell_14 = notebook.cells[14]["source"]
cell_14 = cell_14.replace(
    "validacion cruzada estratificada de 5 folds dentro de train",
    "validacion cruzada estratificada por grupos de 5 folds dentro de train",
)
cell_14 = cell_14.replace(
    "`Complain` y `DaySinceLastOrder` se mantienen como candidatas para esta primera comparacion",
    "`Complain` y `DaySinceLastOrder` se mantienen solo en esta comparacion inicial",
)
set_source(notebook.cells[14], cell_14)

cell_16 = notebook.cells[16]["source"]
cell_16 = cell_16.replace(
    "from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_validate",
    "from sklearn.model_selection import StratifiedGroupKFold, cross_val_predict, cross_validate",
)
set_source(notebook.cells[16], cell_16)

cell_17 = notebook.cells[17]["source"]
cell_17 = cell_17.replace(
    "cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)",
    "cv = StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)",
)
set_source(notebook.cells[17], cell_17)

cell_19 = notebook.cells[19]["source"]
cell_19 = cell_19.replace(
    "            y_train,\n            cv=cv,",
    "            y_train,\n            groups=train_groups,\n            cv=cv,",
)
set_source(notebook.cells[19], cell_19)

cell_22 = notebook.cells[22]["source"]
cell_22 = cell_22.replace(
    "        y_train,\n        cv=cv,",
    "        y_train,\n        groups=train_groups,\n        cv=cv,",
)
set_source(notebook.cells[22], cell_22)

set_source(
    notebook.cells[33],
    """
### Resultado intermedio del ajuste

Este bloque corresponde a la comparacion inicial de regresion logistica y arbol con las variables disponibles. Sirvio para entender el trade-off entre recall, precision y cantidad de contactos.

No representa la decision final porque posteriormente se:

1. detectaron perfiles duplicados;
2. cambio la validacion a grupos;
3. incorporo Random Forest;
4. excluyeron `Complain` y `DaySinceLastOrder` por temporalidad no confirmada;
5. selecciono el umbral definitivo antes de abrir test.

La decision final se presenta en las secciones siguientes.
""",
)

set_source(
    notebook.cells[34],
    f"""
## 13. Conclusion final

La **regresion logistica balanceada** fue elegida como modelo final bajo el escenario conservador sin `Complain` ni `DaySinceLastOrder`.

### Seleccion dentro de train

- Validacion: `StratifiedGroupKFold` con 5 folds.
- Metrica principal: F2 con `beta=2`.
- Umbral elegido fuera de fold: `{threshold['threshold']:.2f}`.
- F2 fuera de fold: `{threshold['f2']:.3f}`.
- Recall fuera de fold: `{threshold['recall']:.1%}`.
- Precision fuera de fold: `{threshold['precision']:.1%}`.

### Evaluacion final en test

- F2: `{test['f2']:.3f}`.
- Recall: `{test['recall']:.1%}`.
- Precision: `{test['precision']:.1%}`.
- PR-AUC: `{test['pr_auc']:.3f}`.
- ROC-AUC: `{test['roc_auc']:.3f}`.
- Churn detectado: `{test['tp']}` de `{test['tp'] + test['fn']}`.
- Falsas alertas: `{test['fp']}`.
- Clientes priorizados: `{test['contacts']}` de `{results['final_test_rows']}`.

La diferencia entre validacion y test es razonable y no cambia la conclusion. El modelo detecta aproximadamente 8 de cada 10 churns, pero solo 36,5% de las alertas son correctas. El costo operativo de esas falsas alertas debe discutirse con el equipo comercial.

Las explicaciones SHAP e importancias describen como decide el modelo; no prueban causalidad.
""",
)

set_source(
    notebook.cells[35],
    """
from pathlib import Path
import json

FINAL_RESULTS_PATH = Path("reports/final_modeling_results.json")
assert FINAL_RESULTS_PATH.exists()

final_results = json.loads(FINAL_RESULTS_PATH.read_text(encoding="utf-8"))
assert final_results["shared_profile_groups_train_test"] == 0
assert final_results["selected_model"] == "Regresion logistica"
assert final_results["protocol"]["selection_metric"] == "F2 beta=2"
assert final_results["protocol"]["test_used_for_selection"] is False
assert final_results["protocol"]["test_evaluation_frozen"] is True

print("Validaciones finales OK")
print("Modelo final:", final_results["selected_model"])
print("Umbral final:", final_results["selected_threshold_oof"]["threshold"])
print("Test congelado:", final_results["final_test_rows"], "clientes")
""",
)

notebook.cells.extend(
    [
        nbformat.v4.new_markdown_cell(
            """
## 14. Comparacion final y sensibilidad temporal

Los resultados siguientes se cargan desde `reports/final_modeling_results.json`, generado por `tools/finalize_modeling.py`. El script tiene una proteccion para no reabrir test accidentalmente.
"""
        ),
        nbformat.v4.new_code_cell(
            """
from IPython.display import Image, display

model_comparison = pd.DataFrame(
    final_results["model_comparison_oof_threshold_050"]
)[["model", "f2", "recall", "precision", "pr_auc", "roc_auc", "contacts"]]

temporal_sensitivity = pd.DataFrame(
    final_results["temporal_sensitivity_rf_threshold_050"]
)[["scenario", "f2", "recall", "precision", "pr_auc", "roc_auc"]]

display(model_comparison.round(3))
display(Image(filename="reports/figures/final_model_comparison_cv.png"))
display(temporal_sensitivity.round(3))
display(Image(filename="reports/figures/temporal_sensitivity_f2.png"))
"""
        ),
        nbformat.v4.new_markdown_cell(
            """
## 15. Evaluacion final en test

El umbral se eligio exclusivamente con probabilidades fuera de fold de train. Despues de congelar modelo, variables y umbral, test se utilizo para una unica evaluacion final.
"""
        ),
        nbformat.v4.new_code_cell(
            """
test_metrics = pd.DataFrame([final_results["final_test_metrics"]])
display(test_metrics.round(3))
display(Image(filename="reports/figures/final_test_roc_pr.png"))
display(Image(filename="reports/figures/final_test_confusion_matrix.png"))
"""
        ),
        nbformat.v4.new_markdown_cell(
            """
## 16. Interpretabilidad: importancia y SHAP

- La importancia por permutacion mide cuanto cae F2 cuando se desordena una variable.
- SHAP global resume que variables modifican mas las predicciones.
- SHAP local explica por que dos clientes concretos recibieron riesgo alto o bajo.

Estas tecnicas explican el comportamiento del modelo, no relaciones causales.
"""
        ),
        nbformat.v4.new_code_cell(
            """
display(Image(filename="reports/figures/final_feature_importance.png"))
display(Image(filename="reports/figures/final_shap_global.png"))
display(Image(filename="reports/figures/final_shap_local_high_risk.png"))
display(Image(filename="reports/figures/final_shap_local_low_risk.png"))
"""
        ),
    ]
)

nbformat.write(notebook, NOTEBOOK_PATH)
print(f"Actualizado: {NOTEBOOK_PATH}")
