# Resultados de Modelado - Primera Comparacion

**Fecha:** 11/06/2026  
**Target:** `Churn`  
**Base de comparacion:** 4.504 clientes de train  
**Evaluacion:** StratifiedKFold con 5 folds  
**Test:** reservado, sin evaluar

## Criterio definido antes de entrenar

La metrica principal es **F2**, un F-beta con `beta=2`. Combina recall y precision, pero da mas importancia al recall porque el error mas costoso es no detectar a un cliente que se va. Precision, F1 y PR-AUC se mantienen para medir el costo de generar alertas y la capacidad de ordenar clientes por riesgo.

## Resultados de validacion cruzada

| Modelo | F2 | Recall | Precision | F1 | PR-AUC | Accuracy |
|---|---:|---:|---:|---:|---:|---:|
| Dummy - clase mayoritaria | 0,000 | 0,000 | 0,000 | 0,000 | 0,168 | 0,832 |
| Regresion logistica balanceada | 0,704 | 0,814 | 0,458 | 0,585 | 0,709 | 0,806 |
| Arbol de decision balanceado | **0,718** | 0,805 | 0,503 | 0,619 | 0,647 | 0,833 |

## Traduccion a clientes

Las predicciones fuera de fold permiten comparar el costo operativo sin abrir test:

| Modelo | Churn detectado | Churn no detectado | Falsas alertas | Clientes contactados |
|---|---:|---:|---:|---:|
| Dummy | 0 | 758 | 0 | 0 |
| Regresion logistica | 617 | 141 | 732 | 1.349 |
| Arbol de decision | 610 | 148 | 604 | 1.214 |

## Lectura de negocio

- El Dummy demuestra que 83% de accuracy puede ser inutil: no detecta ningun churn.
- El arbol obtiene el mejor F2, 0,718, porque conserva recall alto y mejora precision.
- La logistica detecta aproximadamente 8 de cada 10 churns y obtiene la mejor PR-AUC, por lo que ordena mejor el riesgo.
- El arbol detecta siete churns menos, pero evita 128 falsas alertas y requiere contactar 135 clientes menos.
- El arbol tiene una brecha F2 train-CV cercana a 3 puntos porcentuales, sin una senal fuerte de sobreajuste con la configuracion actual.

## Decision provisoria

El **arbol queda como candidato provisorio** por obtener el mayor F2. No se declara ganador final hasta comparar Random Forest, revisar temporalidad y definir el umbral comercial. La logistica sigue siendo competitiva por su mayor recall y PR-AUC.

## Ajuste de umbral con predicciones fuera de fold

| Modelo | Umbral | F2 | Recall | Precision | Contactos | Churn detectado |
|---|---:|---:|---:|---:|---:|---:|
| Logistica estandar | 0,50 | 0,704 | 0,814 | 0,457 | 1.349 | 617 |
| Logistica ajustada | **0,52** | **0,708** | 0,809 | **0,473** | **1.297** | 613 |
| Arbol estandar | 0,50 | 0,718 | 0,805 | 0,502 | 1.214 | 610 |
| Arbol maximo F2 | 0,51 | 0,718 | 0,805 | 0,502 | 1.214 | 610 |
| Arbol alternativa operativa | 0,60 | 0,717 | 0,796 | **0,513** | **1.175** | 603 |

El ajuste mejora claramente la logistica: evita 52 contactos y sube 1,6 puntos porcentuales de precision, perdiendo cuatro churns detectados. En el arbol, el umbral estandar ya esta cerca del maximo F2. Subirlo a 0,60 reduce 39 contactos y mejora 1,1 puntos de precision, pero pierde siete churns adicionales.

**Umbral provisorio:** `0,51` para el arbol si se prioriza F2. El umbral `0,60` queda como alternativa si la capacidad comercial exige menos contactos.

## Siguientes pasos

1. Comparar Random Forest con los mismos folds.
2. Repetir escenarios sin variables temporalmente sospechosas.
3. Definir capacidad y costo de contacto.
4. Confirmar si el umbral F2 o la alternativa operativa se adapta a esa capacidad.
5. Evaluar test una sola vez al final.
