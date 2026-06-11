# Registro de Decisiones - Proyecto de Churn

**Proyecto:** Churn de clientes de e-commerce  
**Grupo:** Grupo 1  
**Ultima actualizacion:** 11/06/2026  
**Objetivo del documento:** registrar las decisiones importantes del proyecto, por que se tomaron, que alternativas se descartaron y que consecuencias tienen para el negocio.

---

## Como leer este documento

Este archivo funciona como memoria del proyecto y apoyo para la defensa oral. No registra solamente decisiones tecnicas: explica como cada eleccion ayuda o limita la decision que debe tomar el gerente comercial.

Estados utilizados:

- **Cerrada:** la decision ya fue implementada y validada.
- **Provisoria:** se adopta para avanzar, pero debe revisarse con nueva evidencia.
- **Pendiente:** todavia no existe evidencia suficiente para decidir.

---

## Decision 1 - Definir el problema como una priorizacion comercial

**Estado:** Cerrada

1. **Que decidimos:** usar el analisis para identificar y priorizar clientes con mayor riesgo de churn, con el fin de aplicar acciones de retencion antes de perderlos.
2. **Por que:** el valor para la empresa no esta en predecir por predecir, sino en decidir a quienes contactar, que problema resolver y donde asignar el presupuesto de retencion.
3. **Alternativas descartadas:**
   - Construir un modelo buscando solamente la mayor metrica posible.
   - Describir el churn general sin convertirlo en segmentos o acciones.
   - Tratar a todos los clientes con la misma campana.
4. **Consecuencias:** el resultado final debera generar una prioridad accionable, no solo una etiqueta. El gerente necesitara conocer el riesgo del cliente, las principales razones asociadas y la accion sugerida.
5. **Implicancia de negocio:** una campana focalizada permite concentrar beneficios y esfuerzo comercial donde existe mayor riesgo, evitando gastar el mismo monto en toda la base.

---

## Decision 2 - Priorizar la deteccion de clientes que realmente se van

**Estado:** Provisoria hasta comparar modelos y umbrales

1. **Que decidimos:** utilizar **F2**, un F-beta con `beta=2`, como metrica principal. F2 combina recall y precision, dando mas importancia al recall. Recall, precision, F1, PR-AUC y la matriz de confusion se reportan por separado para mantener visible el costo comercial.
2. **Por que:** el principal riesgo comercial es un falso negativo: un cliente que realmente se ira pero que el sistema no detecta. Ese cliente no recibe una accion de retencion y la empresa pierde su valor futuro.
3. **Alternativas descartadas:**
   - Usar accuracy como metrica principal.
   - Maximizar precision sin considerar cuantos clientes en riesgo quedan afuera.
   - Elegir un modelo por una unica metrica tecnica sin analizar costos comerciales.
4. **Consecuencias:** F2 evita maximizar recall sin limites. Un modelo recibe mejor valor si detecta churn, pero pierde calidad si genera demasiados falsos positivos.
5. **Implicancia de negocio:** el umbral final no debe elegirse solo desde Python. Debe relacionarse con el costo de una accion de retencion, el margen esperado del cliente, la capacidad del equipo comercial y el costo de perderlo.
6. **Evidencia actual:** solo 948 de 5.630 clientes presentan churn, un 16,8%. Un sistema que predijera siempre "no churn" tendria cerca de 83,2% de accuracy, pero detectaria cero clientes en riesgo.

---

## Decision 3 - Conservar una copia original e inalterada de los datos

**Estado:** Cerrada

1. **Que decidimos:** no modificar el archivo original. Las normalizaciones, imputaciones y exclusiones utilizadas en el EDA se realizan en memoria.
2. **Por que:** preservar el dato original permite auditar el trabajo, repetir el analisis y distinguir observaciones reales de transformaciones realizadas por el equipo.
3. **Alternativas descartadas:**
   - Sobrescribir el CSV con datos corregidos.
   - Reemplazar nulos o categorias directamente en la unica copia disponible.
4. **Consecuencias:** cada notebook debe aplicar explicitamente las transformaciones necesarias.
5. **Implicancia de negocio:** una recomendacion comercial debe poder rastrearse hasta datos verificables. Si el archivo original se altera, se pierde esa trazabilidad.
6. **Trazabilidad:** se conserva una copia inalterada en `data/raw/`. El archivo de la raiz se mantiene por compatibilidad con los notebooks actuales y ambas copias tienen el mismo contenido.

---

## Decision 4 - Excluir `CustomerID` como predictor

**Estado:** Cerrada

1. **Que decidimos:** mantener `CustomerID` para identificar clientes y validar que train y test no se superpongan, pero excluirlo de las variables predictoras.
2. **Por que:** es un identificador administrativo, no una caracteristica del comportamiento del cliente.
3. **Alternativas descartadas:**
   - Incluirlo porque es numerico.
   - Eliminarlo por completo y perder trazabilidad.
4. **Consecuencias:** el modelo no podra memorizar patrones artificiales asociados al numero de cliente, pero las predicciones futuras podran vincularse nuevamente con cada persona.
5. **Implicancia de negocio:** el gerente recibe una lista identificable de clientes sin convertir un codigo interno en una falsa explicacion del churn.

---

## Decision 5 - No eliminar todas las filas con valores faltantes

**Estado:** Cerrada

1. **Que decidimos:** conservar las filas con nulos y completar los valores mediante imputacion.
2. **Por que:** 1.856 clientes tienen al menos un valor faltante. Eliminarlos significaria perder cerca de un tercio de la base y podria cambiar artificialmente el perfil de los clientes analizados.
3. **Alternativas descartadas:**
   - Eliminar todas las filas incompletas.
   - Reemplazar todos los nulos con cero.
   - Aplicar una unica media global a todas las variables.
4. **Consecuencias:** los valores imputados son estimaciones y no deben interpretarse como observaciones reales. El proceso debe ajustarse solo con train.
5. **Implicancia de negocio:** conservar esos clientes permite que el sistema sea util aun cuando la informacion comercial no sea perfecta, una situacion habitual en operacion.

---

## Decision 6 - Usar una estrategia de imputacion diferenciada

**Estado:** Cerrada para la preparacion actual; debe integrarse al pipeline definitivo

1. **Que decidimos:**
   - Imputar `WarehouseToHome` y `CouponUsed` con la mediana calculada en train.
   - Comparar KNN y regresion iterativa para `Tenure`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`, `OrderCount` y `DaySinceLastOrder`.
   - Elegir el metodo con menor MAE simulado por variable.
2. **Por que:** no todas las variables representan lo mismo. La mediana es simple y robusta para distancia y cupones; para las demas se evaluaron relaciones multivariadas.
3. **Alternativas descartadas:**
   - Eliminar filas.
   - Usar un unico metodo para todas las columnas sin evaluarlo.
   - Elegir el metodo por comodidad y no por error observado.
4. **Consecuencias:** KNN resulto mejor que la regresion iterativa en las cinco variables comparadas. Como KNN utiliza distancias, las variables se estandarizan antes de imputar.
5. **Implicancia de negocio:** se conserva mas informacion, pero las decisiones sobre clientes no deben justificarse a partir de un valor imputado individual como si fuera cierto.
6. **Resultados de validacion:**

| Variable | Metodo elegido | MAE |
|---|---:|---:|
| `DaySinceLastOrder` | KNN k=5 | 1,618 |
| `HourSpendOnApp` | KNN k=5 | 0,427 |
| `OrderAmountHikeFromlastYear` | KNN k=5 | 2,090 |
| `OrderCount` | KNN k=5 | 0,846 |
| `Tenure` | KNN k=5 | 4,264 |

---

## Decision 7 - Separar train y test antes de preparar los datos

**Estado:** Cerrada

1. **Que decidimos:** realizar un split 80/20 antes de imputar, escalar o codificar variables.
2. **Por que:** test debe representar clientes que el proceso de entrenamiento nunca vio. Si se calculan transformaciones usando toda la base, se filtra informacion del examen final hacia el entrenamiento.
3. **Alternativas descartadas:**
   - Limpiar e imputar toda la base antes de dividirla.
   - Entrenar y evaluar sobre los mismos clientes.
4. **Consecuencias:** cualquier imputador, encoder, escalador o selector de variables debe ajustarse exclusivamente con train y luego aplicarse a test.
5. **Implicancia de negocio:** las metricas finales seran una estimacion mas honesta de lo que podria ocurrir con nuevos clientes.

---

## Decision 8 - Utilizar un split estratificado y reproducible

**Estado:** Cerrada

1. **Que decidimos:** usar `train_test_split` con `test_size=0.20`, `stratify=y` y `random_state=42`.
2. **Por que:** el churn es minoritario. La estratificacion evita que train y test tengan proporciones muy distintas por azar, y la semilla fija permite repetir exactamente el experimento.
3. **Alternativas descartadas:**
   - Split aleatorio sin estratificacion.
   - Cambiar la semilla en cada ejecucion.
   - Usar el conjunto de test para ajustar decisiones durante el desarrollo.
4. **Consecuencias:** train contiene 4.504 clientes y test 1.126. Las tasas de churn son 16,83% y 16,87%, respectivamente.
5. **Implicancia de negocio:** la comparacion de modelos se realiza sobre una distribucion consistente con la realidad observada y no sobre una division accidentalmente favorable.

---

## Decision 9 - Normalizar categorias semanticamente equivalentes

**Estado:** Cerrada para el EDA; pendiente de integrar al pipeline

1. **Que decidimos:** tratar como equivalentes las etiquetas que parecen representar la misma categoria:
   - `Phone` y `Mobile Phone`.
   - `COD` y `Cash on Delivery`.
   - `CC` y `Credit Card`.
   - `Mobile` y `Mobile Phone` en la categoria de orden.
2. **Por que:** mantener sinonimos separados fragmenta los segmentos y puede ocultar su tasa real de churn.
3. **Alternativas descartadas:**
   - Considerar cada texto como un segmento distinto.
   - Corregir manualmente el CSV original.
4. **Consecuencias:** la regla de normalizacion debe aplicarse igual en entrenamiento y produccion. Tambien debe validarse con el diccionario de datos o el responsable del sistema fuente.
5. **Implicancia de negocio:** el gerente no deberia recibir dos segmentos comerciales distintos cuando en la practica ambos significan "telefono movil" o "pago contra entrega".

---

## Decision 10 - Tratar los outliers con criterio y no eliminarlos automaticamente

**Estado:** Cerrada para el EDA; pendiente de definir para el modelo

1. **Que decidimos:** conservar los valores altos que pueden corresponder a clientes reales y excluir solo siete observaciones puntuales de ciertos graficos del EDA: dos extremos de `WarehouseToHome`, cuatro de `Tenure` y el maximo de `DaySinceLastOrder`.
2. **Por que:** un cliente con muchas ordenes, cupones o cashback puede ser comercialmente relevante y no un error.
3. **Alternativas descartadas:**
   - Eliminar todo valor fuera de 1,5 veces el rango intercuartil.
   - Recortar automaticamente todas las variables.
   - Modificar el archivo original.
4. **Consecuencias:** las exclusiones del EDA mejoran la lectura visual, pero no implican que esas filas deban borrarse del entrenamiento.
5. **Implicancia de negocio:** se evita perder clientes de alto valor o comportamientos extremos que podrian requerir una estrategia especifica.

---

## Decision 11 - Priorizar la retencion temprana

**Estado:** Cerrada como conclusion del EDA

1. **Que decidimos:** considerar `Tenure` una de las principales senales para segmentar acciones de retencion.
2. **Por que:** los clientes con churn tienen una antiguedad media de 3,57 meses y mediana de 1 mes, frente a 11,25 y 10 meses entre quienes permanecen. El efecto observado es alto.
3. **Alternativas descartadas:**
   - Tratar la antiguedad como una variable secundaria.
   - Esperar a que aparezca inactividad prolongada para intervenir.
4. **Consecuencias:** el futuro modelo debera evaluar seriamente esta variable y el reporte ejecutivo debera destacar el periodo inicial de la relacion.
5. **Implicancia de negocio:** conviene estudiar acciones de onboarding, seguimiento y beneficios iniciales durante los primeros meses.
6. **Cuidado:** la asociacion no prueba que una promocion temprana cause menor churn. La efectividad de una accion deberia validarse mediante una prueba controlada.

---

## Decision 12 - Usar `Complain` solo si su temporalidad es valida

**Estado:** Pendiente y critica antes de cerrar el modelo

1. **Que decidimos:** mantener `Complain` como variable candidata, pero no aprobar su uso definitivo hasta confirmar que el reclamo estaba disponible antes del momento de prediccion.
2. **Por que:** los clientes con reclamo presentan 31,7% de churn frente a 10,9% entre quienes no reclamaron. Es una senal fuerte y accionable, pero podria estar mirando el futuro.
3. **Alternativas consideradas:**
   - Incluirla sin revisar su origen.
   - Eliminarla inmediatamente y perder una senal posiblemente legitima.
   - Entrenar dos escenarios, con y sin `Complain`, para medir dependencia.
4. **Consecuencias:** si el reclamo fue registrado despues de la baja, incluirlo invalidaria la evaluacion. Si fue previo, puede ser una de las mejores alertas operativas.
5. **Implicancia de negocio:** independientemente del modelo, un reclamo previo deberia evaluar la activacion de un flujo de recuperacion. Pero una alerta basada en datos posteriores al abandono llegaria demasiado tarde.
6. **Accion requerida:** consultar el diccionario de datos o al responsable de la fuente y documentar fecha del reclamo, fecha de corte y definicion de churn.

---

## Decision 13 - No interpretar `DaySinceLastOrder` de forma intuitiva

**Estado:** Pendiente y critica antes de cerrar el modelo

1. **Que decidimos:** no comunicar que "mas dias sin comprar implican mayor churn" porque los datos observados muestran lo contrario.
2. **Por que:** los clientes con churn tienen menos dias desde la ultima orden en promedio: 3,37 dias frente a 4,86 dias.
3. **Alternativas descartadas:**
   - Forzar la narrativa esperada aunque los datos no la respalden.
   - Eliminar la variable solamente porque contradice la intuicion.
4. **Consecuencias:** antes de usarla se debe entender la fecha de medicion, la definicion de churn y si la ultima orden fue observada antes o despues de la ventana objetivo.
5. **Implicancia de negocio:** una campana de reactivacion basada en una interpretacion incorrecta podria contactar al segmento equivocado.
6. **Accion requerida:** comparar el rendimiento del futuro modelo con y sin esta variable y solicitar documentacion temporal.

---

## Decision 14 - No convertir asociaciones en afirmaciones causales

**Estado:** Cerrada

1. **Que decidimos:** describir los hallazgos como asociaciones y no como causas demostradas.
2. **Por que:** el dataset es observacional. Por ejemplo, quienes churnean reciben menos cashback, pero eso no demuestra que aumentar cashback evite el abandono.
3. **Alternativas descartadas:**
   - Recomendar beneficios masivos asumiendo causalidad.
   - Presentar segmentos demograficos como causa del churn.
4. **Consecuencias:** las recomendaciones deben formularse como hipotesis comerciales a probar.
5. **Implicancia de negocio:** antes de escalar descuentos o cashback, conviene hacer una prueba A/B o piloto que mida retencion incremental y rentabilidad.

---

## Decision 15 - Usar segmentos para orientar acciones, no para etiquetar personas

**Estado:** Cerrada como criterio de negocio

1. **Que decidimos:** usar categoria de compra, estado civil, medio de pago, ciudad y dispositivo como contexto de segmentacion, combinados con senales de comportamiento.
2. **Por que:** algunos segmentos tienen mayor churn, pero sus efectos son menores que el de variables como `Tenure`, y pertenecer a un grupo no implica que una persona vaya a abandonar.
3. **Alternativas descartadas:**
   - Crear reglas comerciales solo por genero o estado civil.
   - Tratar todos los segmentos como igualmente importantes.
4. **Consecuencias:** se priorizaran perfiles combinados, por ejemplo cliente nuevo con reclamo y categoria mobile, antes que una unica caracteristica aislada.
5. **Implicancia de negocio:** las acciones pueden ser mas relevantes y menos invasivas. Tambien reduce el riesgo de tomar decisiones injustas basadas solamente en datos demograficos.

---

## Decision 16 - Interpretar `SatisfactionScore` con cautela

**Estado:** Provisoria

1. **Que decidimos:** conservar la variable para explorar interacciones, pero no asumir que un puntaje alto significa automaticamente menor churn.
2. **Por que:** el score 5 presenta la mayor tasa observada de churn, 23,8%, mientras que los scores 1 y 2 presentan 11,6% y 12,6%.
3. **Alternativas descartadas:**
   - Usar el score como escala lineal sin validacion.
   - Eliminarlo por producir un resultado inesperado.
4. **Consecuencias:** se debera revisar la definicion de la escala, el momento de medicion y su relacion con `Complain`, `Tenure` y categoria de compra.
5. **Implicancia de negocio:** una lectura superficial podria llevar a enfocar acciones en clientes supuestamente insatisfechos y dejar afuera a un grupo que realmente presenta mayor abandono.

---

## Decision 17 - Comparar modelos simples antes del modelo potente

**Estado:** Provisoria; primera comparacion completada

1. **Que decidimos:** comparar primero Dummy, regresion logistica balanceada y arbol de decision balanceado mediante validacion cruzada estratificada. Random Forest queda como siguiente candidato potente.
2. **Por que:** el modelo simple establece un punto de comparacion y facilita la explicacion; el modelo potente permite evaluar si la complejidad agrega valor comercial real.
3. **Resultados actuales:**
   - Dummy: 83,2% de accuracy, pero 0% de recall.
   - Regresion logistica: F2 de 0,704, 81,4% de recall, 45,8% de precision y PR-AUC de 0,709.
   - Arbol de decision: F2 de 0,718, 80,5% de recall, 50,3% de precision y PR-AUC de 0,647.
4. **Alternativas pendientes:** Random Forest y escenarios sin `Complain` ni `DaySinceLastOrder`.
5. **Criterio de decision pendiente:** priorizar el mayor F2 promedio; desempatar con PR-AUC, precision, estabilidad, explicabilidad y utilidad operativa. No se elegira automaticamente el de mayor accuracy.
6. **Consecuencias:** la logistica detecta siete churns mas en las predicciones fuera de fold, pero requiere contactar 135 clientes adicionales. El arbol reduce falsas alertas y sigue detectando aproximadamente ocho de cada diez churns.
7. **Implicancia de negocio:** todavia no hay ganador. La eleccion depende de capacidad de contacto, costo de una alerta y valor de perder un cliente.

---

## Decision 18 - Reservar test para una unica evaluacion final

**Estado:** Cerrada como regla metodologica

1. **Que decidimos:** comparar alternativas y ajustar hiperparametros mediante validacion dentro de train. Test se utilizara una sola vez, cuando el proceso este cerrado.
2. **Por que:** consultar repetidamente test termina adaptando decisiones al conjunto que deberia simular datos nuevos.
3. **Alternativas descartadas:**
   - Elegir el modelo mirando repetidamente su resultado en test.
   - Ajustar el umbral hasta maximizar la metrica de test.
4. **Consecuencias:** los resultados intermedios deben provenir de validacion cruzada estratificada en train.
5. **Implicancia de negocio:** la estimacion final sera mas creible y reducira el riesgo de prometer un desempeno que no se sostenga al implementar el sistema.

---

## Decision 19 - Elegir el umbral segun capacidad y rentabilidad

**Estado:** Provisoria; analisis fuera de fold completado

1. **Que decidimos:** usar `0,51` como umbral F2 provisorio para el arbol. Mantener `0,60` como alternativa operativa si se necesita reducir contactos.
2. **Por que:** el modelo entregara probabilidades, pero el negocio debe decidir cuantos clientes puede contactar y cuanto puede invertir.
3. **Alternativas evaluadas:**
   - Logistica en `0,52`: mejora precision a 47,3%, evita 52 contactos y pierde cuatro churns detectados.
   - Arbol en `0,60`: mejora precision a 51,3%, evita 39 contactos y pierde siete churns detectados.
   - Mantener `0,50`: practicamente equivalente al maximo F2 del arbol.
4. **Consecuencias:** el ajuste de umbral mejora precision, pero no elimina el trade-off. Cada reduccion de falsas alertas puede dejar clientes con churn sin detectar.
5. **Implicancia de negocio:** `0,51` maximiza el criterio F2 actual. `0,60` puede ser preferible si el equipo no puede contactar 1.214 clientes. La decision final requiere capacidad, costo de contacto, margen y perdida esperada.

---

## Decision 20 - Exigir explicabilidad y una recomendacion accionable

**Estado:** Provisoria hasta elegir el modelo

1. **Que decidimos:** el resultado final debe explicar que factores elevan el riesgo general y, cuando sea posible, por que un cliente fue priorizado.
2. **Por que:** el gerente necesita convertir la prediccion en una accion y defender por que se usa presupuesto sobre determinado segmento.
3. **Alternativas descartadas:**
   - Entregar solamente una probabilidad sin contexto.
   - Elegir un modelo mas complejo si su mejora es marginal y no puede explicarse.
4. **Consecuencias:** se evaluaran coeficientes, importancia de variables y, si corresponde, explicaciones como SHAP. Estas explicaciones describiran el comportamiento del modelo, no causalidad.
5. **Implicancia de negocio:** la alerta deberia orientar una respuesta: onboarding para baja antiguedad, recuperacion ante reclamos o una prueba de beneficios para perfiles seleccionados.

---

## Pendientes obligatorios antes de cerrar la entrega de modelado

1. Confirmar la temporalidad de `Complain` y `DaySinceLastOrder`.
2. Integrar normalizacion, imputacion y encoding en pipelines ajustados solo con train.
3. Entrenar y comparar Random Forest como modelo potente.
4. Comparar el modelo potente con los tres modelos ya evaluados mediante la misma validacion cruzada estratificada.
5. Definir el costo aproximado de un falso positivo y un falso negativo.
6. Estimar capacidad semanal o mensual de contacto del equipo comercial.
7. Elegir modelo y umbral con metricas y criterio de negocio.
8. Evaluar test una sola vez y registrar el resultado final.
9. Traducir el modelo ganador a segmentos, acciones y limitaciones.
10. Actualizar este documento con la decision del modelo ganador y las alternativas descartadas.

---

## Resumen ejecutivo de decisiones actuales

- El proyecto busca priorizar clientes para retencion, no solamente predecir churn.
- F2 sera la metrica principal porque prioriza recall sin descuidar precision y capacidad operativa.
- El dataset original se conserva intacto y `CustomerID` no se utiliza como predictor.
- No se eliminan las 1.856 filas con datos faltantes; la imputacion se ajusta exclusivamente con train.
- El split es 80/20, estratificado y reproducible: 16,83% de churn en train y 16,87% en test.
- `Tenure` respalda una estrategia de retencion temprana.
- `Complain` es una senal comercial fuerte, pero no puede aprobarse para modelado sin verificar temporalidad.
- `DaySinceLastOrder` y `SatisfactionScore` contradicen lecturas intuitivas y requieren validacion adicional.
- Cashback y segmentos comerciales muestran asociaciones utiles, pero todavia no demuestran causalidad.
- La eleccion de modelo y umbral sigue pendiente y debera combinar desempeno, explicabilidad, presupuesto y capacidad de contacto.
