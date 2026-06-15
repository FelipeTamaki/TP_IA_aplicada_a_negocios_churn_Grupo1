# TP IA Aplicada a Negocios - Churn

Proyecto de analisis y prediccion de churn sobre 5.630 clientes de e-commerce.

## Entregables

- `EDA.ipynb`: calidad de datos, exploracion e hipotesis de negocio.
- `Modelo.ipynb`: split estratificado y preparacion posterior al split.
- `reports/01_hipotesis.md`: cinco hipotesis con evidencia visual y estadistica.
- `reports/decisions.md`: decisiones, alternativas y consecuencias comerciales.
- `reports/modeling_results.md`: primera comparacion de Dummy, regresion logistica y arbol.
- `reports/final_modeling_results.json`: resultados congelados de seleccion, umbral y test final.
- `tools/finalize_modeling.py`: cierre reproducible con proteccion para no reabrir test.
- `guion_presentacion_tecncica.md`: estructura y guion oral de la presentacion tecnica.

`tools/rf_experiment.py` y `reports/rf_experiment.json` se conservan solo como evidencia historica del primer experimento. No representan el protocolo ni las metricas finales.
- `plans/PLAN_2026-06-11_entrega-churn.md`: plan de trabajo y mejoras propuestas.

## Ejecucion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Luego abrir y ejecutar `EDA.ipynb` y `Modelo.ipynb` en ese orden. El dataset original se conserva en `data/raw/` y no debe modificarse.

## Estado

El EDA y el modelado estan completos. La regresion logistica balanceada fue seleccionada como modelo final con umbral `0,41`, luego de:

- comparar Dummy, regresion logistica, arbol y Random Forest;
- bloquear perfiles duplicados entre train y test;
- excluir `Complain` y `DaySinceLastOrder` por temporalidad no confirmada;
- evaluar test una sola vez;
- generar ROC, Precision-Recall, matriz de confusion, importancia y SHAP.

Quedan pendientes el reporte ejecutivo y las presentaciones finales.
