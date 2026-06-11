# Plan: completar el proyecto de churn con entregables verificables y orientados a negocio

**Fecha:** 11/06/2026  
**Alternativa elegida:** Hipotesis - modelo - decision  
**STATUS:** EN_EJECUCION

## Alternativas consideradas

1. **Entrega minima:** completar solo los nombres de archivo exigidos. Se descarta porque cumple formalmente, pero deja debil la defensa oral.
2. **Modelar inmediatamente:** entrenar todos los modelos antes de cerrar el EDA. Se descarta porque mezcla entregas y aumenta el riesgo de leakage.
3. **Hipotesis - modelo - decision:** cerrar primero evidencia y decisiones; despues construir y evaluar modelos. Elegida por equilibrio entre rigor, claridad y fechas.

## Objetivo

Construir una solucion que permita priorizar clientes con riesgo de churn, explicar por que fueron priorizados y traducir el resultado en acciones comerciales defendibles.

## No objetivos

- No buscar el modelo con mayor accuracy.
- No afirmar causalidad a partir de asociaciones observacionales.
- No usar test para ajustar modelos o umbrales.
- No recomendar campanas masivas sin estimar costo y capacidad operativa.

## Supuestos criticos

- El target `Churn` representa abandono observado.
- `Complain` y `DaySinceLastOrder` estaban disponibles antes del momento de prediccion.
- Las categorias equivalentes detectadas representan el mismo concepto.
- El equipo comercial puede definir costo de contacto y capacidad de intervencion.

---

## Fase 0 - Validar datos y supuestos

- **Objetivo:** confirmar estructura, target, nulos, duplicados y riesgos temporales.
- **Entregable:** EDA y decisiones de calidad documentadas.
- **Criterio de aceptacion:** shape, target, nulos y variables sospechosas estan verificados.
- **Esfuerzo:** 2 horas.
- **Dependencias:** ninguna.
- **Agente:** ds-explorer + ds-stats + humano.
- **Estado:** completada, excepto confirmacion externa de temporalidad.

## Fase 1 - Formular y validar cinco hipotesis

- **Objetivo:** transformar variables en preguntas comerciales verificables.
- **Entregable:** `reports/01_hipotesis.md` y `EDA.ipynb`.
- **Criterio de aceptacion:** cada hipotesis tiene logica, grafico, test, tamano de efecto e interpretacion.
- **Esfuerzo:** 4 horas.
- **Dependencias:** Fase 0.
- **Agente:** ds-explorer + ds-stats.
- **Estado:** completada.

## Fase 2 - Congelar el experimento

- **Objetivo:** separar datos y preparar transformaciones sin leakage.
- **Entregable:** split estratificado y estrategia de imputacion en `Modelo.ipynb`.
- **Criterio de aceptacion:** train/test no se superponen, conservan la tasa de churn y los transformadores se ajustan solo con train.
- **Esfuerzo:** 3 horas.
- **Dependencias:** Fase 1.
- **Agente:** ds-feature.
- **Estado:** completada.

## Punto de reevaluacion 1

Antes de modelar, confirmar temporalidad de `Complain` y `DaySinceLastOrder`. Si no puede confirmarse, entrenar escenarios con y sin esas variables y declarar la limitacion.

## Fase 3 - Entrenar baseline y arbol obligatorio

- **Objetivo:** establecer un piso y un modelo interpretable.
- **Entregable:** DummyClassifier, baseline interpretable y DecisionTreeClassifier dentro de pipelines.
- **Criterio de aceptacion:** existen resultados de StratifiedKFold k=5 para F2, recall, precision y PR-AUC.
- **Esfuerzo:** 4 horas.
- **Dependencias:** Fase 2 y reevaluacion 1.
- **Agente:** ds-model.
- **Estado:** completada. Dummy, regresion logistica y arbol fueron comparados con 5 folds; test permanece cerrado.

## Fase 4 - Evaluar un modelo potente

- **Objetivo:** medir si Random Forest agrega valor frente al arbol y al baseline.
- **Entregable:** tabla comparativa de modelos con media y variabilidad de metricas.
- **Criterio de aceptacion:** la eleccion del candidato se justifica principalmente por F2 y se complementa con recall, precision, PR-AUC, estabilidad y explicabilidad.
- **Esfuerzo:** 4 horas.
- **Dependencias:** Fase 3.
- **Agente:** ds-model.
- **Estado:** pendiente.

## Fase 5 - Definir modelo y umbral de negocio

- **Objetivo:** convertir probabilidades en una lista operable de clientes.
- **Entregable:** matrices de confusion y volumen de contactos para distintos umbrales.
- **Criterio de aceptacion:** el umbral elegido respeta capacidad y costo comercial, y queda registrado en `reports/decisions.md`.
- **Esfuerzo:** 3 horas.
- **Dependencias:** Fase 4 e informacion del negocio.
- **Agente:** ds-model + humano.
- **Estado:** analisis tecnico completado con predicciones fuera de fold. Decision comercial pendiente de capacidad y costos.

## Punto de reevaluacion 2

Si el modelo complejo mejora poco, elegir el mas simple. Si el recall alto produce demasiados falsos positivos, revisar umbral o priorizar un top de riesgo segun capacidad.

## Fase 6 - Interpretar y evaluar una sola vez en test

- **Objetivo:** obtener una estimacion final honesta y explicable.
- **Entregable:** metricas de test, feature importance y explicaciones SHAP globales y locales.
- **Criterio de aceptacion:** test se consulta una sola vez y cada grafico se traduce a lenguaje comercial.
- **Esfuerzo:** 4 horas.
- **Dependencias:** Fase 5.
- **Agente:** ds-model + ds-report.
- **Estado:** pendiente.

## Fase 7 - Comunicar al gerente

- **Objetivo:** presentar hallazgos, desempeno, acciones y limitaciones sin tecnicismos innecesarios.
- **Entregable:** PDF ejecutivo de 4-6 paginas y defensa oral de 15 minutos.
- **Criterio de aceptacion:** incluye pregunta, hallazgo, desempeno en terminos de negocio, SHAP simplificado, recomendaciones y limitaciones.
- **Esfuerzo:** 1 dia.
- **Dependencias:** Fase 6.
- **Agente:** ds-report + humano.
- **Estado:** pendiente.

---

## Cuatro mejoras concretas propuestas por el planificador

1. **Separar evidencia de causalidad:** convertir cashback y onboarding en pilotos medibles antes de recomendarlos a toda la base.
2. **Comparar escenarios de temporalidad:** entrenar con y sin `Complain` y `DaySinceLastOrder` si la fuente no confirma sus fechas.
3. **Elegir umbral con capacidad real:** traducir cada umbral a clientes contactados, churn detectado y costo esperado.
4. **Preferir simplicidad cuando el valor sea similar:** si Random Forest no mejora materialmente el resultado, usar el arbol o baseline mas explicable.

## Handoff

- **Proxima fase:** Fase 3.
- **Agente sugerido:** ds-model.
- **Dependencia previa:** resolver o documentar el riesgo temporal.
- **Archivo de decisiones:** `reports/decisions.md`.
