# TP IA Aplicada a Negocios - Churn

Proyecto de analisis y prediccion de churn sobre 5.630 clientes de e-commerce.

## Entregables

- `EDA.ipynb`: calidad de datos, exploracion e hipotesis de negocio.
- `Modelo.ipynb`: split estratificado y preparacion posterior al split.
- `reports/01_hipotesis.md`: cinco hipotesis con evidencia visual y estadistica.
- `reports/decisions.md`: decisiones, alternativas y consecuencias comerciales.
- `reports/modeling_results.md`: primera comparacion de Dummy, regresion logistica y arbol.
- `plans/PLAN_2026-06-11_entrega-churn.md`: plan de trabajo y mejoras propuestas.

## Ejecucion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

Luego abrir y ejecutar `EDA.ipynb` y `Modelo.ipynb` en ese orden. El dataset original se conserva en `data/raw/` y no debe modificarse.

## Estado

La entrega de EDA, preparacion del experimento, Dummy, regresion logistica y arbol obligatorio esta completa. Random Forest, seleccion final, SHAP y reporte ejecutivo corresponden a la siguiente etapa.
