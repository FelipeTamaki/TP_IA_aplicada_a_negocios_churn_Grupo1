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
| Train | 4.504 | 758 |
| Test | 1.126 | 190 |

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

**Regresion logistica** (tuneada)

```text
C = 0.1
class_weight = balanced
max_iter = 2000
random_state = 42
```

**Arbol de decision** (tuneado)

```text
class_weight = balanced
max_depth = 6
min_samples_leaf = 20
random_state = 42
```

**Random Forest** (tuneado - MODELO FINAL)

```text
n_estimators = 300
max_depth = 12
max_features = 0.5
max_samples = 0.7
min_samples_leaf = 4
class_weight = {0: 1, 1: 5}
random_state = 42
```

### Metodo de ajuste

Los hiperparametros de los tres modelos se eligieron con `GridSearchCV` sobre los mismos folds agrupados, optimizando F2. La busqueda esta documentada en `Modelo.ipynb` (seccion 12 bis) y en `tools/tune_models.py`.

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
| Completo | 0,763 | 0,768 | 0,743 | 0,830 | 0,957 |
| Sin `Complain` | 0,699 | 0,703 | 0,683 | 0,784 | 0,942 |
| Sin `DaySinceLastOrder` | 0,759 | 0,765 | 0,737 | 0,821 | 0,954 |
| Sin ambas (final) | 0,698 | 0,707 | 0,662 | 0,768 | 0,936 |

### Recurso visual

`reports/figures/temporal_sensitivity_f2.png`

### Decision tecnica

Excluir `Complain` y `DaySinceLastOrder` del modelo final porque no se puede garantizar que estuvieran disponibles antes del churn.

### Mensaje tecnico

Se acepta una reduccion de performance para evitar leakage temporal y mantener validez de produccion.

---

## Diapositiva 12 - Comparacion de modelos

### Contenido

Resultados fuera de fold con umbral `0,50`, modelos tuneados y escenario conservador:

| Modelo | F2 | Recall | Precision | PR-AUC | ROC-AUC |
|---|---:|---:|---:|---:|---:|
| Dummy | 0,000 | 0,000 | 0,000 | 0,168 | 0,500 |
| Regresion logistica | 0,688 | **0,809** | 0,431 | 0,609 | 0,868 |
| Arbol de decision | 0,669 | 0,780 | 0,427 | 0,579 | 0,855 |
| **Random Forest** | **0,698** | 0,707 | **0,662** | **0,768** | **0,936** |

### Comparacion a igual recall (~84%)

A mismo nivel de deteccion, el modelo que mejor ordena el riesgo genera menos falsas alertas:

| Modelo | Umbral | Recall | Precision | Falsas alertas |
|---|---:|---:|---:|---:|
| Regresion logistica | 0,45 | 0,842 | 0,400 | 958 |
| Arbol de decision | 0,29 | 0,854 | 0,351 | 1.197 |
| **Random Forest** | 0,35 | 0,843 | **0,573** | **477** |

### Recurso visual

`reports/figures/final_model_comparison_cv.png`

### Seleccion

- Modelo final: **Random Forest tuneado**.
- Criterio primario: mayor F2 (el Random Forest tiene el F2 mas alto fuera de fold).
- A igual recall genera la mitad de falsas alertas que la logistica (mejor PR-AUC).
- La regresion logistica queda como baseline interpretable.

### Mensaje tecnico

La seleccion responde al criterio recall-first definido antes de observar test. Tunear y dejar competir al Random Forest sube la precision sin resignar recall, porque ordena mejor el riesgo.

---

## Diapositiva 13 - Ajuste de umbral y test final

### Ajuste fuera de fold (Random Forest)

El umbral que maximiza F2 fuera de fold es `0,27`:

| Umbral | F2 | Recall | Precision | Contactos |
|---|---:|---:|---:|---:|
| **0,27** | **0,797** | **0,906** | 0,537 | 1.280 |

El umbral `0,27` se selecciona antes de evaluar test.

### Resultado final en test

| Metrica | Logistica anterior (mismo split) | **Random Forest (final)** |
|---|---:|---:|
| F2 | 0,694 | **0,817** |
| Recall | 0,842 | **0,911** |
| Precision | 0,407 | **0,579** |
| F1 | - | 0,708 |
| PR-AUC | 0,643 | **0,834** |
| ROC-AUC | - | **0,955** |
| Accuracy | - | 0,873 |

Matriz (Random Forest):

- TP: 173.
- FN: 17.
- FP: 126.
- TN: 810.

### Recursos visuales

- `reports/figures/final_test_roc_pr.png`
- `reports/figures/final_test_confusion_matrix.png`

### Mensaje tecnico

El Random Forest mejora recall, precision y F2 a la vez respecto de la logistica: no hay sacrificio, es mejor ordenamiento del riesgo. Reduce las falsas alertas casi a la mitad (268 -> 126) manteniendo recall superior al 90%.

---

## Diapositiva 14 - Interpretabilidad y limitaciones

### Importancia por permutacion (Random Forest)

Principales variables:

1. `Tenure`.
2. `OrdersPerTenure`.
3. `CashbackPerOrder`.
4. `CashbackAmount`.
5. `NumberOfAddress`.

### SHAP global

Variables destacadas:

- `Tenure`.
- `OrdersPerTenure`.
- `NumberOfAddress`.
- `PreferedOrderCat`.
- `CashbackAmount`.
- `MaritalStatus`.

Las variables derivadas (`OrdersPerTenure`, `CashbackPerOrder`) aparecen entre las mas
importantes en ambas tecnicas, lo que confirma que el feature engineering aporta señal real.

### Recursos visuales

- `reports/figures/final_feature_importance.png`
- `reports/figures/final_shap_global.png`
- Opcional: `reports/figures/final_shap_local_high_risk.png` y `reports/figures/final_shap_local_low_risk.png` para contrastar un cliente de alto riesgo con uno de bajo riesgo.

### Limitaciones tecnicas

- Dataset observacional.
- Temporalidad incompleta.
- Perfiles duplicados en la fuente.
- Precision final de 57,9%: cada alerta acierta mas de una de cada dos veces, pero el churn
  minoritario (~17%) impide acercarse al 100% sin perder recall.
- Random Forest es menos transparente que la logistica o el arbol; se explica con importancia
  por permutacion y SHAP.
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
4. Hiperparametros elegidos con `GridSearchCV` y seleccion de modelo/umbral definida antes de
   observar test, priorizando F2 y recall.

### Resultado final

Random Forest tuneado con umbral `0,27`: en test detecta el **91,1%** de los churns (recall) con
F2 de **0,817** y precision de **57,9%**, reduciendo casi a la mitad las falsas alertas frente a
la logistica del cierre anterior. Mejora recall, precision y F2 a la vez gracias a un mejor
ordenamiento del riesgo.

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

