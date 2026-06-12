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
| Regresion logistica balanceada | 0,724 | 0,830 | 0,481 | 0,609 | **0,712** | 0,821 |
| Arbol de decision balanceado | **0,730** | **0,838** | **0,484** | **0,613** | 0,641 | 0,822 |

## Traduccion a clientes

Las predicciones fuera de fold permiten comparar el costo operativo sin abrir test:

| Modelo | Churn detectado | Churn no detectado | Falsas alertas | Clientes contactados |
|---|---:|---:|---:|---:|
| Dummy | 0 | 758 | 0 | 0 |
| Regresion logistica | 629 | 129 | 679 | 1.308 |
| Arbol de decision | 635 | 123 | 678 | 1.313 |

## Lectura de negocio

- El Dummy demuestra que 83% de accuracy puede ser inutil: no detecta ningun churn.
- El arbol obtiene el mejor F2, 0,730, y detecta 83,8% de los churns.
- La logistica tambien mejora y obtiene la mejor PR-AUC, por lo que ordena mejor el riesgo.
- Con umbral 0,50, el arbol detecta seis churns mas que la logistica y genera una falsa alerta menos.
- El arbol tiene una brecha F2 train-CV de 2,3 puntos porcentuales, sin una senal fuerte de sobreajuste con la configuracion actual.

## Impacto del feature engineering

Se agregaron `OrdersPerTenure`, `CashbackPerOrder` y `CouponsPerOrder`.

| Modelo | F2 sin FE | F2 con FE | Delta F2 | Delta recall | Delta precision | Delta PR-AUC |
|---|---:|---:|---:|---:|---:|---:|
| Regresion logistica | 0,704 | 0,724 | +0,021 | +0,016 | +0,023 | +0,003 |
| Arbol de decision | 0,718 | 0,730 | +0,012 | +0,033 | -0,019 | -0,007 |

`OrdersPerTenure` quedo tercera en importancia del arbol. El feature engineering mejora el criterio F2 en ambos modelos, aunque en el arbol intercambia precision y capacidad de ordenamiento por mayor deteccion.

## Decision provisoria

El **arbol queda como candidato provisorio** por obtener el mayor F2. No se declara ganador final hasta comparar Random Forest, revisar temporalidad y definir el umbral comercial. La logistica sigue siendo competitiva por su mayor recall y PR-AUC.

## Ajuste de umbral con predicciones fuera de fold

| Modelo | Umbral | F2 | Recall | Precision | Contactos | Churn detectado |
|---|---:|---:|---:|---:|---:|---:|
| Logistica estandar | 0,50 | 0,725 | 0,830 | 0,481 | 1.308 | 629 |
| Logistica maximo F2 | **0,47** | **0,727** | **0,847** | 0,464 | 1.383 | **642** |
| Arbol estandar | 0,50 | 0,731 | 0,838 | 0,484 | 1.313 | 635 |
| Arbol maximo F2 | **0,52** | **0,731** | 0,838 | 0,484 | 1.313 | 635 |
| Arbol alternativa operativa | 0,60 | 0,716 | 0,792 | **0,519** | **1.156** | 600 |

El ajuste de la logistica a 0,47 detecta trece churns adicionales, pero requiere 75 contactos mas y reduce precision. En el arbol, el umbral estandar ya esta cerca del maximo F2. Subirlo a 0,60 reduce 157 contactos y mejora 3,5 puntos de precision, pero pierde 35 churns adicionales.

**Umbral provisorio:** `0,52` para el arbol si se prioriza F2. El umbral `0,60` queda como alternativa si la capacidad comercial exige menos contactos.

## Siguientes pasos

1. Comparar Random Forest con los mismos folds.
2. Repetir escenarios sin variables temporalmente sospechosas.
3. Definir capacidad y costo de contacto.
4. Confirmar si el umbral F2 o la alternativa operativa se adapta a esa capacidad.
5. Evaluar test una sola vez al final.
