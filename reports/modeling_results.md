# Resultados finales de modelado

> **ACTUALIZACION 17/06/2026 - mejora con tuning sistematico.**
> El modelo final pasa de la regresion logistica al **Random Forest tuneado por
> `GridSearchCV`**. A igual recall genera la mitad de falsas alertas y sube la
> precision de test de 36,5% a **57,9%** sin resignar recall (de hecho sube a
> 91,1%). Los numeros nuevos estan en la seccion ["Cierre actualizado"](#cierre-actualizado-17062026).
> Las tablas previas se conservan como historia del proceso.

**Fecha de cierre original:** 15/06/2026
**Target:** `Churn`
**Metrica principal:** F2 con `beta=2`
**Validacion:** `StratifiedGroupKFold` con 5 folds
**Modelo final (original):** regresion logistica balanceada
**Modelo final (actualizado):** Random Forest tuneado
**Umbral final (actualizado):** `0,27`

## Correccion metodologica: perfiles duplicados

La auditoria final detecto **556 filas con variables explicativas exactamente duplicadas**. El split aleatorio anterior dejaba 193 perfiles de test tambien representados en train, lo que podia inflar las metricas.

Se reemplazo ese protocolo por una separacion estratificada por grupos:

- train: 4.504 clientes y 758 churns;
- test: 1.126 clientes y 190 churns;
- perfiles identicos compartidos entre train y test: 0;
- la validacion cruzada interna tambien mantiene cada grupo en un unico fold.

Los resultados anteriores al cambio se consideran intermedios y no deben presentarse como evaluacion final.

## Politica de temporalidad

No se encontro documentacion suficiente para confirmar que `Complain` y `DaySinceLastOrder` estuvieran disponibles antes del momento de prediccion. Por criterio conservador, ambas variables se excluyeron del modelo final.

La sensibilidad de Random Forest a esta decision fue:

| Escenario | F2 | Recall | Precision | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Completo | 0,754 | 0,753 | 0,760 | 0,831 | 0,957 |
| Sin `Complain` | 0,700 | 0,698 | 0,711 | 0,787 | 0,944 |
| Sin `DaySinceLastOrder` | 0,742 | 0,738 | 0,758 | 0,816 | 0,953 |
| Sin ambas | 0,674 | 0,670 | 0,689 | 0,776 | 0,938 |

`Complain` aporta capacidad predictiva, pero no se conserva porque una mejora basada en informacion posiblemente posterior al churn no seria util en produccion.

## Comparacion final dentro de train

Todos los modelos usan el mismo split, los mismos folds agrupados, el mismo feature engineering y el escenario conservador.

| Modelo | F2 | Recall | Precision | PR-AUC | ROC-AUC | Contactos |
|---|---:|---:|---:|---:|---:|---:|
| Dummy | 0,000 | 0,000 | 0,000 | 0,169 | 0,500 | 0 |
| Regresion logistica | **0,689** | **0,802** | 0,441 | 0,636 | 0,873 | 1.391 |
| Arbol de decision | 0,658 | 0,775 | 0,411 | 0,569 | 0,854 | 1.441 |
| Random Forest | 0,674 | 0,670 | **0,689** | **0,776** | **0,938** | **743** |

Random Forest ordena mejor el riesgo y genera menos alertas, pero con umbral 0,50 deja sin detectar mas churns. La regresion logistica obtiene el mayor F2 y recall bajo la prioridad definida para el negocio, por eso queda seleccionada.

## Seleccion del umbral

El umbral se eligio exclusivamente con probabilidades fuera de fold de train.

| Escenario | Umbral | F2 | Recall | Precision | Contactos | Churn detectado | Falsas alertas |
|---|---:|---:|---:|---:|---:|---:|---:|
| Maximo F2 | **0,41** | **0,696** | **0,861** | 0,394 | 1.668 | 658 | 1.010 |
| Alternativa operativa | 0,50 | 0,689 | 0,802 | **0,441** | **1.391** | 613 | **778** |

El umbral `0,41` es la decision tecnica final porque maximiza F2. El umbral `0,50` queda documentado como alternativa si la capacidad comercial exige 277 contactos menos, aceptando perder 45 churns adicionales dentro de train.

## Evaluacion final en test

Test se utilizo despues de congelar variables, modelo y umbral.

| Metrica | Resultado |
|---|---:|
| F2 | **0,665** |
| Recall | **0,837** |
| Precision | 0,365 |
| F1 | 0,508 |
| PR-AUC | 0,577 |
| ROC-AUC | 0,857 |
| Accuracy | 0,733 |

### Traduccion a clientes

| Resultado | Clientes |
|---|---:|
| Churn detectado | 154 |
| Churn no detectado | 30 |
| Falsas alertas | 268 |
| Activos correctamente descartados | 664 |
| Total priorizado para contacto | 422 |

El modelo detecta aproximadamente **8 de cada 10 clientes que churnean**. Sin embargo, solo 36,5% de las alertas son correctas. Esta precision no invalida el modelo: hace visible que la campaña debe diseñarse con acciones de costo controlado o con una segunda priorizacion comercial.

## Interpretabilidad

Las importancias por permutacion destacan:

1. `Tenure`.
2. `CashbackAmount`.
3. `PreferedOrderCat`.
4. `OrdersPerTenure`.
5. `SatisfactionScore`.

SHAP global tambien destaca categoria preferida, antiguedad, cantidad de direcciones, cashback, estado civil y frecuencia de compra.

Estas explicaciones muestran como decide el modelo. No demuestran que modificar una variable cause menor churn.

## Artefactos generados

- `reports/final_modeling_results.json`
- `reports/figures/final_model_comparison_cv.png`
- `reports/figures/temporal_sensitivity_f2.png`
- `reports/figures/final_test_roc_pr.png`
- `reports/figures/final_test_confusion_matrix.png`
- `reports/figures/final_feature_importance.png`
- `reports/figures/final_shap_global.png`
- `reports/figures/final_shap_local_high_risk.png`
- `reports/figures/final_shap_local_low_risk.png`

## Limitaciones pendientes para negocio

1. Definir costo real de contacto y capacidad semanal o mensual.
2. Elegir entre el umbral F2 `0,41` y la alternativa operativa `0,50`.
3. Validar mediante pilotos si onboarding, recuperacion de reclamos o cashback reducen churn.
4. Monitorear precision, recall y estabilidad por subgrupos luego de implementar.

---

## Cierre actualizado (17/06/2026)

**Por que se actualiza.** El cierre anterior reportaba precision 36,5% y se leia como
"baja". No era un defecto del modelo: era la consecuencia de priorizar recall (F2 + umbral
bajo + eleccion de la regresion logistica). Precision y recall se contraponen; la unica forma
honesta de subir precision sin resignar recall es que el modelo **ordene mejor el riesgo**
(mayor PR-AUC). Por eso se hizo tuning sistematico y se dejo competir al Random Forest.

### Que cambio

1. **Hiperparametros por `GridSearchCV`** (scoring F2, misma CV agrupada) en los tres modelos,
   en vez de valores elegidos a mano. Mejores configuraciones:
   - Regresion logistica: `C=0.1`, `class_weight=balanced`.
   - Arbol de decision: `max_depth=6`, `min_samples_leaf=20`.
   - Random Forest: `n_estimators=300`, `max_depth=12`, `min_samples_leaf=4`,
     `max_features=0.5`, `max_samples=0.7`, `class_weight={0:1, 1:5}`.
2. **Seleccion del modelo final** bajo el mismo criterio recall-first: el Random Forest tuneado
   pasa a tener el F2 mas alto fuera de fold, asi que queda seleccionado automaticamente.

### Comparacion a igual recall (~84%) - fuera de fold en train

A mismo nivel de deteccion, el modelo que mejor ordena el riesgo genera menos falsas alertas.

| Modelo (tuneado) | Umbral | Recall | Precision | Contactos | Falsas alertas |
|---|---:|---:|---:|---:|---:|
| Regresion logistica | 0,45 | 0,842 | 0,400 | 1.596 | 958 |
| Arbol de decision | 0,29 | 0,854 | 0,351 | 1.844 | 1.197 |
| **Random Forest** | 0,35 | 0,843 | **0,573** | **1.116** | **477** |

### Evaluacion final en test (umbral F2 `0,27`)

| Metrica | Logistica anterior (mismo split) | **Random Forest (final)** |
|---|---:|---:|
| Recall | 0,842 | **0,911** |
| Precision | 0,407 | **0,579** |
| F2 | 0,694 | **0,817** |
| F1 | - | 0,708 |
| PR-AUC | 0,643 | **0,834** |
| ROC-AUC | - | **0,955** |
| Accuracy | - | 0,873 |
| Churn detectado | 160 de 190 | **173 de 190** |
| Falsas alertas | 233 | **126** |
| Clientes priorizados | 393 | 299 |

El Random Forest **mejora simultaneamente recall, precision y F2**: no hay sacrificio, es
mejora pura por mejor ordenamiento del riesgo. La precision no llega al 100% porque el churn
es minoritario (~17%) y se prioriza detectar; sigue siendo un punto de operacion elegido.

> **Reproducibilidad.** Los conteos exactos de test dependen levemente de la version de
> scikit-learn por el barajado de `StratifiedGroupKFold`. La comparacion logistica vs Random
> Forest de la tabla anterior se hizo sobre el **mismo split** para aislar el efecto del modelo.
> Para reproducir identico, usar las versiones de `requirements.txt`.

### Notas de implementacion

- Los parametros tuneados viven en `tools/finalize_modeling.py` (`RF_PARAMS`, `LOGISTIC_PARAMS`,
  `TREE_PARAMS`) y la busqueda que los justifica esta en `Modelo.ipynb` (seccion 12 bis) y en
  `tools/tune_models.py`.
- `shap` paso a ser **opcional**: si no esta instalado, `finalize_modeling.py` omite las figuras
  SHAP sin romper el cierre. La interpretabilidad principal es importancia por permutacion.
