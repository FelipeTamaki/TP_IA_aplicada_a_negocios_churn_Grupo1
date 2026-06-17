# Guia para crear la presentacion tecnica

## Enfoque

- Duracion estimada: 12-15 minutos.
- Cantidad sugerida: 15 diapositivas.
- Audiencia: docente o evaluador interesado en metodologia, reproducibilidad y resultados.
- Evitar recomendaciones comerciales extensas: corresponden a la presentacion de negocios.
- Mostrar decisiones tecnicas, comparaciones y controles contra leakage.
- Utilizar exclusivamente las metricas finales obtenidas con validacion agrupada.

---

## Diapositiva 1 - Arquitectura del experimento

### Titulo

**Pipeline de clasificacion de churn**

### Contenido

Presentar el flujo completo:

```text
Dataset raw
   |
Auditoria de calidad y duplicados
   |
Split estratificado por grupos
   |
Feature engineering
   |
Preprocesamiento dentro del pipeline
   |
Validacion cruzada agrupada
   |
Comparacion y seleccion de modelos
   |
Ajuste de umbral con predicciones OOF
   |
Evaluacion final en test
   |
Interpretabilidad
```

### Mensaje tecnico

El diseño separa preparacion, seleccion y evaluacion final para reducir leakage y sobreajuste al conjunto de test.

---

## Diapositiva 2 - Dataset y variable objetivo

### Contenido

- 5.630 observaciones.
- 20 columnas:
  - 1 identificador;
  - 1 target;
  - 18 variables explicativas.
- Target binario: `Churn`.
- Distribucion:
  - `Churn = 1`: 948 clientes, 16,8%;
  - `Churn = 0`: 4.682 clientes, 83,2%.
- `CustomerID` se excluye de los predictores.

### Tipos de variables

- Numericas continuas.
- Numericas discretas u ordinales.
- Categoricas nominales.
- Variables binarias.

### Recurso visual

Grafico de distribucion del target y tabla breve con tipos de variables.

### Mensaje tecnico

El desbalance obliga a utilizar metricas sensibles a la clase positiva y estrategias de balanceo en los modelos.

---

## Diapositiva 3 - Auditoria de calidad

### Contenido

- Siete variables numericas contienen valores faltantes.
- 1.856 filas presentan algun nulo.
- Cada fila incompleta tiene exactamente un valor faltante.
- No hay duplicados de `CustomerID`.
- Existen 556 filas con features exactamente identicas.
- Se detectaron categorias semanticamente equivalentes:
  - `Phone` y `Mobile Phone`;
  - `COD` y `Cash on Delivery`;
  - `CC` y `Credit Card`;
  - `Mobile` y `Mobile Phone`.

### Recurso visual

- Grafico de nulos por columna.
- Recuadro con el hallazgo de perfiles duplicados.

### Mensaje tecnico

Los perfiles repetidos deben tratarse como grupos para impedir que una copia quede en train y otra en test.

---

## Diapositiva 4 - Estrategia de imputacion

### Contenido

| Variables | Metodo |
|---|---|
| `WarehouseToHome`, `CouponUsed` | Mediana |
| `Tenure`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`, `OrderCount`, `DaySinceLastOrder` | KNN Imputer |
| Categoricas | Moda |

Configuracion:

- `KNNImputer(n_neighbors=5, weights="distance")`.
- Estandarizacion previa para modelos sensibles a escala.
- Comparacion previa entre KNN e imputacion iterativa mediante MAE simulado.
- KNN obtuvo menor MAE en las cinco variables evaluadas.

### Detalle metodologico

La imputacion se ajusta dentro de cada fold. Los datos de validacion nunca participan del calculo de medianas, vecinos, moda o escalado.

### Mensaje tecnico

Imputar antes de dividir o fuera del pipeline produciria leakage de preprocesamiento.

---

## Diapositiva 5 - Analisis exploratorio utilizado para modelar

### Contenido

Mostrar unicamente hallazgos que influyeron en decisiones tecnicas:

- `Tenure`: mayor diferencia entre clases.
- `Complain`: fuerte asociacion con churn, pero temporalidad no confirmada.
- `DaySinceLastOrder`: relacion contraria a la intuicion, con riesgo temporal.
- `CashbackAmount`: asociacion relevante.
- Variables categoricas con diferencias entre segmentos.

### Metodos estadisticos

- Mann-Whitney U para variables numericas.
- Chi-cuadrado para variables categoricas.
- Rank-biserial y Cramer's V como tamaños de efecto.

### Recursos visuales

- `reports/figures/h1_tenure.png`
- `reports/figures/h2_complain.png`
- `reports/figures/h3_days_since_last_order.png`
- `reports/figures/h4_cashback.png`
- `reports/figures/h5_segments.png`

### Mensaje tecnico

El EDA se utilizo para formular variables y detectar riesgos metodologicos, no para seleccionar predictores por p-valor.

---

## Diapositiva 6 - Split agrupado

### Contenido

Metodo:

```python
StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)
```

Grupo:

- Hash construido con todas las variables explicativas.
- No incluye `CustomerID`.
- No incluye `Churn`.

Division final:

| Conjunto | Filas | Churn |
|---|---:|---:|
| Train | 4.514 | 764 |
| Test | 1.116 | 184 |

- Perfiles compartidos entre train y test: 0.
- Test no se utiliza para seleccionar modelo, features ni umbral.

### Mensaje tecnico

La estratificacion mantiene la clase; el agrupamiento evita evaluar sobre perfiles equivalentes a los entrenados.

---

## Diapositiva 7 - Feature engineering

### Contenido

```text
OrdersPerTenure  = OrderCount / (Tenure + 1)
CashbackPerOrder = CashbackAmount / (OrderCount + 1)
CouponsPerOrder  = CouponUsed / (OrderCount + 1)
```

Justificacion tecnica:

- Capturan intensidad y no solamente magnitud absoluta.
- El `+1` evita divisiones por cero.
- Son transformaciones deterministicas.
- No utilizan el target.
- Se generan por separado en train y test.
- Se incluyen antes del `ColumnTransformer`.

### Recurso visual

Tabla con variable original, denominador y variable resultante.

### Mensaje tecnico

`OrdersPerTenure` conserva importancia en el modelo final según permutacion y SHAP.

---

## Diapositiva 8 - Pipeline de preprocesamiento

### Contenido

Mostrar dos ramas:

```text
Numericas KNN
  -> KNNImputer
  -> StandardScaler solo para regresion

Numericas mediana
  -> SimpleImputer(strategy="median")
  -> StandardScaler solo para regresion

Categoricas
  -> SimpleImputer(strategy="most_frequent")
  -> OneHotEncoder(handle_unknown="ignore")
```

Todos los pasos se integran mediante:

- `ColumnTransformer`.
- `Pipeline`.

### Diferencias por modelo

- Regresion logistica: variables numericas escaladas.
- Arbol y Random Forest: sin escalado.
- Todos: imputacion y one-hot dentro del fold.

### Mensaje tecnico

El pipeline garantiza que cada fold aprenda sus propios parametros de transformacion.

---

## Diapositiva 9 - Modelos e hiperparametros

### Contenido

**Dummy**

```text
strategy = most_frequent
```

**Regresion logistica**

```text
class_weight = balanced
max_iter = 2000
random_state = 42
```

**Arbol de decision**

```text
class_weight = balanced
max_depth = 5
min_samples_leaf = 20
random_state = 42
```

**Random Forest**

```text
n_estimators = 476
max_depth = 16
max_features = 0.5
max_samples = 0.7
min_samples_leaf = 4
min_samples_split = 4
class_weight = {0: 1, 1: 5}
```

### Metodo de ajuste

Los hiperparametros de Random Forest se obtuvieron mediante `RandomizedSearchCV` sobre los mismos folds agrupados, optimizando F2. Esto explica valores no redondos como `n_estimators = 476`.

### Mensaje tecnico

El Dummy establece el piso; la regresion aporta linealidad e interpretabilidad; el arbol captura no linealidad; Random Forest reduce varianza mediante ensamble.

---

## Diapositiva 10 - Metricas de evaluacion

### Contenido

**Recall**

```text
TP / (TP + FN)
```

**Precision**

```text
TP / (TP + FP)
```

**F-beta**

```text
F_beta = (1 + beta²) * (precision * recall)
         / (beta² * precision + recall)
```

Con `beta=2`, recall recibe cuatro veces el peso de precision dentro de la formula.

Metricas complementarias:

- F1.
- PR-AUC.
- ROC-AUC.
- Matriz de confusion.
- Cantidad de alertas.

### Recurso visual

Diagrama que relacione TP, FP, FN y TN con cada metrica.

### Mensaje tecnico

PR-AUC es especialmente informativa debido al 16,8% de positivos; ROC-AUC se reporta como capacidad global de ranking.

---

## Diapositiva 11 - Sensibilidad temporal

### Contenido

La sensibilidad se midio sobre Random Forest por ser el modelo mas reactivo a estas dos variables; la decision de exclusion se aplica a todos los modelos, incluido el final.

Comparacion de Random Forest:

| Escenario | F2 | Recall | Precision | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Completo | 0,754 | 0,753 | 0,760 | 0,831 | 0,957 |
| Sin `Complain` | 0,700 | 0,698 | 0,711 | 0,787 | 0,944 |
| Sin `DaySinceLastOrder` | 0,742 | 0,738 | 0,758 | 0,816 | 0,953 |
| Sin ambas | 0,674 | 0,670 | 0,689 | 0,776 | 0,938 |

### Recurso visual

`reports/figures/temporal_sensitivity_f2.png`

### Decision tecnica

Excluir `Complain` y `DaySinceLastOrder` del modelo final porque no se puede garantizar que estuvieran disponibles antes del churn.

### Mensaje tecnico

Se acepta una reduccion de performance para evitar leakage temporal y mantener validez de produccion.

---

## Diapositiva 12 - Comparacion de modelos

### Contenido

Resultados fuera de fold con umbral `0,50` y escenario conservador:

| Modelo | F2 | Recall | Precision | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Dummy | 0,000 | 0,000 | 0,000 | 0,169 | 0,500 |
| Regresion logistica | **0,689** | **0,802** | 0,441 | 0,636 | 0,873 |
| Arbol de decision | 0,658 | 0,775 | 0,411 | 0,569 | 0,854 |
| Random Forest | 0,674 | 0,670 | **0,689** | **0,776** | **0,938** |

### Recurso visual

`reports/figures/final_model_comparison_cv.png`

### Seleccion

- Modelo final: regresion logistica balanceada.
- Criterio primario: mayor F2.
- Criterio secundario: mayor recall.
- Random Forest obtiene mejor precision y capacidad de ranking, pero menor recall.

### Mensaje tecnico

La seleccion responde al criterio definido antes de observar test.

---

## Diapositiva 13 - Ajuste de umbral y test final

### Ajuste fuera de fold

| Umbral | F2 | Recall | Precision | Contactos |
|---|---:|---:|---:|---:|
| **0,41** | **0,696** | **0,861** | 0,394 | 1.668 |
| 0,50 | 0,689 | 0,802 | **0,441** | **1.391** |

El umbral `0,41` se selecciona antes de evaluar test.

### Resultado final en test

| Metrica | Valor |
|---|---:|
| F2 | **0,665** |
| Recall | **0,837** |
| Precision | 0,365 |
| F1 | 0,508 |
| PR-AUC | 0,577 |
| ROC-AUC | 0,857 |
| Accuracy | 0,733 |

Matriz:

- TP: 154.
- FN: 30.
- FP: 268.
- TN: 664.

### Recursos visuales

- `reports/figures/final_test_roc_pr.png`
- `reports/figures/final_test_confusion_matrix.png`

### Mensaje tecnico

La diferencia entre validacion y test no cambia la seleccion: el modelo mantiene recall superior al 80%.

---

## Diapositiva 14 - Interpretabilidad y limitaciones

### Importancia por permutacion

Principales variables:

1. `Tenure`.
2. `CashbackAmount`.
3. `PreferedOrderCat`.
4. `OrdersPerTenure`.
5. `SatisfactionScore`.

### SHAP global

Variables destacadas:

- `PreferedOrderCat`.
- `Tenure`.
- `NumberOfAddress`.
- `CashbackAmount`.
- `MaritalStatus`.
- `OrdersPerTenure`.

### Recursos visuales

- `reports/figures/final_feature_importance.png`
- `reports/figures/final_shap_global.png`
- Opcional: `reports/figures/final_shap_local_high_risk.png` y `reports/figures/final_shap_local_low_risk.png` para contrastar un cliente de alto riesgo con uno de bajo riesgo.

### Limitaciones tecnicas

- Dataset observacional.
- Temporalidad incompleta.
- Perfiles duplicados en la fuente.
- Precision final de 36,5%.
- El modelo requiere monitoreo ante cambios de distribucion.
- SHAP e importancia no implican causalidad.

### Mensaje tecnico

El modelo final es reproducible y conservador, pero su desempeño debe monitorearse y recalibrarse en produccion.

---

## Diapositiva 15 - Conclusion

### Decisiones tecnicas clave

1. Split estratificado por grupos para neutralizar los 556 perfiles duplicados y evitar fuga entre train y test.
2. Preprocesamiento e imputacion dentro de cada fold, nunca sobre el conjunto completo.
3. Exclusion conservadora de `Complain` y `DaySinceLastOrder` por temporalidad no garantizada.
4. Seleccion de modelo y umbral definida antes de observar test, priorizando F2 y recall.

### Resultado final

Regresion logistica balanceada con umbral `0,41`: en test detecta el 83,7% de los churns (recall) con F2 de 0,665, manteniendo el desempeño visto en validacion.

### Mensaje de cierre

El pipeline es reproducible y honesto respecto de sus limitaciones; prioriza no perder clientes en riesgo y deja la calibracion economica para la presentacion de negocios.

---

## Archivos visuales para utilizar

| Archivo | Diapositiva |
|---|---:|
| `reports/figures/h1_tenure.png` | 5 |
| `reports/figures/h2_complain.png` | 5 |
| `reports/figures/h3_days_since_last_order.png` | 5 |
| `reports/figures/h4_cashback.png` | 5 |
| `reports/figures/h5_segments.png` | 5 |
| `reports/figures/temporal_sensitivity_f2.png` | 11 |
| `reports/figures/final_model_comparison_cv.png` | 12 |
| `reports/figures/final_test_roc_pr.png` | 13 |
| `reports/figures/final_test_confusion_matrix.png` | 13 |
| `reports/figures/final_feature_importance.png` | 14 |
| `reports/figures/final_shap_global.png` | 14 |
| `reports/figures/final_shap_local_high_risk.png` | 14, opcional |
| `reports/figures/final_shap_local_low_risk.png` | 14, opcional |

## Contenido reservado para la presentacion de negocios

No desarrollar en esta presentacion:

- acciones de onboarding;
- campañas de cashback;
- estrategias posteriores a reclamos;
- presupuesto de retencion;
- costo de adquisicion;
- recomendaciones por segmento;
- plan comercial de contacto.

Solo mencionar estos puntos cuando sean necesarios para justificar F2 o la seleccion del umbral.

