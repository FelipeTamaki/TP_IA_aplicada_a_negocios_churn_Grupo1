# Semana 1 - Setup y Entendimiento del Problema

**Dataset**: `E Commerce Dataset.xlsx - E Comm.csv`  
**Fecha**: 2026-06-03  
**Objetivo**: entender que clientes tienen mayor riesgo de churn y que senales puede usar el gerente comercial para priorizar acciones de retencion.

---

## Antes de Tocar los Datos

### Que es churn y por que le importa economicamente a la empresa?

Para nosotros, churn es perder un cliente: alguien que antes compraba en la plataforma y deja de hacerlo. En terminos comerciales, no es solo una fila con `Churn = 1`; es facturacion futura que se pierde, recompra que no ocurre y relacion comercial que se corta.

Le importa economicamente a la empresa porque un cliente retenido suele tener mas valor que una venta aislada. Si el cliente ya nos conoce, ya paso por el proceso de compra y ya confio en la marca al menos una vez, mantenerlo activo puede ser mucho mas rentable que salir a buscar otro desde cero.

### Que significa que adquirir un cliente nuevo cuesta 5-7 veces mas que retener uno?

Significa que la empresa no deberia mirar churn como un problema tecnico, sino como una fuga de margen. Conseguir un cliente nuevo implica pauta, descuentos de entrada, promociones, esfuerzo comercial y tiempo hasta que ese cliente confie. Retener uno existente normalmente requiere una accion mas focalizada: resolver un reclamo, ofrecer un beneficio, mejorar la experiencia o intervenir antes de que deje de comprar.

Por eso, en este caso nos va a importar mas el **recall** que la **precision** cuando pasemos a modelado. Si el objetivo es retener clientes, el mayor riesgo de negocio es no detectar a alguien que realmente se iba a ir. Un falso positivo puede significar ofrecer un beneficio de mas; un falso negativo puede significar perder al cliente completo. Preferimos que el radar capture la mayor cantidad posible de clientes en riesgo, aunque despues haya que filtrar comercialmente a quien conviene contactar.

### Que decision concreta va a tomar el gerente comercial con este analisis?

El gerente comercial necesita decidir a que clientes priorizar con acciones de retencion. No alcanza con decir "hay churn": tiene que saber donde actuar primero.

Con este analisis deberia poder decidir, por ejemplo:

- si conviene enfocar campanas en clientes nuevos con baja antiguedad;
- si los reclamos deben disparar automaticamente una accion de recuperacion;
- si ciertos segmentos, como mobile, solteros o determinados medios de pago, necesitan una estrategia especifica;
- si beneficios como cashback pueden usarse como herramienta de retencion;
- que variables son confiables para explicar churn y cuales necesitan cuidado por posible leakage o problemas de temporalidad.

La decision concreta no es "hacer un modelo porque si", sino construir un sistema de priorizacion comercial: detectar clientes con mayor riesgo, entender por que estan en riesgo y decidir que accion tomar antes de que se vayan.

---

## Contexto del Problema

El dataset contiene 5.630 clientes de e-commerce, con 20 columnas: 1 identificador, 1 target (`Churn`) y 18 variables explicativas. La variable objetivo indica:

- `Churn = 1`: el cliente se fue.
- `Churn = 0`: el cliente sigue activo.

La base esta desbalanceada: 948 clientes churnearon, equivalente a 16,8%. Esto importa porque un modelo que diga "nadie se va" tendria aproximadamente 83% de accuracy, pero no serviria para retencion.

Para el EDA se trabajo con imputacion en memoria y exclusiones puntuales de outliers no defendibles. El CSV original no se modifica.

---

## Calidad de Datos

- Hay 7 columnas con nulos: `Tenure`, `WarehouseToHome`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`, `CouponUsed`, `OrderCount` y `DaySinceLastOrder`.
- Los nulos no se pisan entre si: 1.856 filas tienen algun nulo, pero cada una tiene exactamente 1 valor faltante.
- Borrar esas filas eliminaria casi un tercio de la base, por eso no conviene.
- `WarehouseToHome` y `CouponUsed` se imputaron por mediana.
- Para el resto de variables con nulos se comparo KNN vs regresion iterativa con variables estandarizadas. KNN gano por menor MAE en las variables evaluadas.
- Se excluyeron del EDA 7 filas puntuales: 2 extremos de `WarehouseToHome`, 4 extremos de `Tenure` y el maximo de `DaySinceLastOrder`.

---

## H1: Clientes con menor antiguedad tienen mayor riesgo de churn

**Enunciado**: los clientes nuevos o con poca antiguedad tienen mayor riesgo de irse porque todavia no desarrollaron habito, confianza ni costo de cambio.

**Evidencia**:

| Grupo | Media Tenure | Mediana Tenure |
|-------|--------------|----------------|
| No churn | 11,25 meses | 10 meses |
| Churn | 3,57 meses | 1 mes |

**Test aplicado**: Mann-Whitney U, porque `Tenure` es numerica y no se asume normalidad.  
**Resultado**: p-valor < 0,001; rank-biserial = 0,61, efecto alto.

**Interpretacion de negocio**: la antiguedad es una de las senales mas fuertes del EDA. La retencion temprana parece critica.

**Recomendacion**: priorizar onboarding, beneficios de bienvenida y seguimiento en los primeros meses.

---

## H2: Clientes que hicieron reclamos churnean mas

**Enunciado**: un reclamo puede indicar una mala experiencia y anticipar abandono.

**Evidencia**:

| Reclamo | Clientes | Tasa de churn |
|---------|----------|---------------|
| Sin reclamo | 4.021 | 10,9% |
| Con reclamo | 1.602 | 31,7% |

**Test aplicado**: chi-cuadrado, porque `Complain` es categorica y `Churn` es binaria.  
**Resultado**: p-valor < 0,001; Cramer's V = 0,25, efecto medio.

**Interpretacion de negocio**: reclamar triplica aproximadamente la tasa de churn. Es una senal accionable para el equipo comercial y de customer experience.

**Riesgo metodologico**: `Complain` puede tener leakage temporal si el reclamo fue registrado despues de la baja. Hay que confirmar temporalidad antes de usarlo en modelado.

**Recomendacion**: activar un flujo de recuperacion despues de reclamos y documentar temporalidad de la variable.

---

## H3: Mas dias desde la ultima orden anticipan churn

**Enunciado**: se esperaba que mas dias sin comprar indicaran inactividad y mayor riesgo de abandono.

**Evidencia**:

| Grupo | Media DaySinceLastOrder | Mediana |
|-------|--------------------------|---------|
| No churn | 4,86 dias | 4 dias |
| Churn | 3,37 dias | 2 dias |

**Test aplicado**: Mann-Whitney U.  
**Resultado**: p-valor < 0,001; rank-biserial = 0,27, efecto medio.

**Interpretacion de negocio**: la evidencia contradice la intuicion inicial. Los clientes que churnearon no aparecen como mas inactivos; al contrario, tienen menos dias desde la ultima orden.

**Recomendacion**: no usar esta variable como argumento ejecutivo sin entender la ventana temporal. Puede estar medida cerca del evento de baja o con una definicion distinta a la intuicion.

---

## H4: Menor cashback o menor actividad transaccional se asocia a mayor churn

**Enunciado**: clientes con menor relacion economica o menos beneficios tienen menos incentivo para quedarse.

**Evidencia principal**:

| Variable | No churn | Churn | Lectura |
|----------|----------|-------|---------|
| `CashbackAmount` promedio | 180,61 | 160,32 | Churn recibe menos cashback |
| `OrderCount` promedio | 3,10 | 2,88 | Diferencia chica |
| `CouponUsed` promedio | 1,72 | 1,71 | Sin diferencia relevante |

**Tests aplicados**: Mann-Whitney U para variables numericas.  
**Resultados**:

- `CashbackAmount`: p-valor < 0,001; rank-biserial = 0,27, efecto medio.
- `OrderCount`: p-valor = 0,009; rank-biserial = 0,05, efecto bajo.
- `CouponUsed`: p-valor = 0,512; rank-biserial = 0,01, efecto bajo/no relevante.

**Interpretacion de negocio**: `CashbackAmount` tiene senal real. `OrderCount` y `CouponUsed` no parecen explicar churn con la misma fuerza.

**Recomendacion**: evaluar beneficios o cashback para segmentos de riesgo, pero evitar concluir causalidad sin experimento o analisis adicional.

---

## H5: Algunos segmentos tienen mayor churn

**Enunciado**: el churn no se distribuye igual entre categorias; algunos segmentos pueden requerir acciones especificas.

**Evidencia destacada**:

| Variable | Segmento de mayor churn | Tasa de churn |
|----------|--------------------------|---------------|
| `PreferedOrderCat` | Mobile Phone | 27,4% |
| `MaritalStatus` | Single | 26,7% |
| `PreferredPaymentMode` | Cash on Delivery | 24,9% |
| `CityTier` | Tier 3 | 21,4% |
| `PreferredLoginDevice` | Computer | 19,9% |

**Tests aplicados**: chi-cuadrado para asociacion categorica con churn.  
**Resultados**:

- `PreferedOrderCat`: Cramer's V = 0,23, efecto medio.
- `MaritalStatus`: Cramer's V = 0,18, efecto medio.
- `PreferredPaymentMode`: Cramer's V = 0,10, efecto bajo/medio.
- `CityTier`: Cramer's V = 0,09, efecto bajo.
- `Gender`: Cramer's V = 0,03, efecto bajo.

**Interpretacion de negocio**: hay segmentos con churn mas alto, pero no todos tienen igual peso. Categoria de compra y estado civil parecen mas informativos que genero.

**Recomendacion**: cruzar segmentos de alto churn con `Tenure` y `Complain` para detectar perfiles accionables, por ejemplo clientes nuevos + mobile + reclamo.

---

## Lectura Especifica: SatisfactionScore

`SatisfactionScore` no se comporta como una relacion lineal simple donde menor satisfaccion implique mayor churn.

| SatisfactionScore | Tasa de churn |
|-------------------|---------------|
| 1 | 11,6% |
| 2 | 12,6% |
| 3 | 17,2% |
| 4 | 17,1% |
| 5 | 23,8% |

**Test aplicado**: chi-cuadrado.  
**Resultado**: p-valor < 0,001; Cramer's V = 0,11, efecto bajo/medio.

**Interpretacion**: el score 5 tiene la tasa de churn mas alta, lo cual obliga a mirar la variable con cuidado. Puede haber un tema de escala, momento de medicion o relacion con otras variables.

**Recomendacion**: cruzar `SatisfactionScore` con `Complain`, `Tenure` y categoria de compra antes de usarlo como narrativa ejecutiva.

---

## Variables Secundarias Revisadas

Se revisaron tambien `WarehouseToHome`, `HourSpendOnApp`, `OrderAmountHikeFromlastYear`, `NumberOfDeviceRegistered` y `NumberOfAddress`.

Hallazgos:

- `WarehouseToHome`: churn tiene distancia promedio algo mayor; efecto bajo.
- `NumberOfDeviceRegistered`: churn registra mas dispositivos en promedio; efecto bajo/medio.
- `HourSpendOnApp`: no muestra senal relevante.
- `OrderAmountHikeFromlastYear`: no muestra senal fuerte.
- `NumberOfAddress`: diferencia chica; conviene analizar agrupada.

Estas variables pueden entrar al modelado, pero no deberian ser el centro del relato ejecutivo salvo que interactuen con variables mas fuertes.

---

## Cierre Ejecutivo

1. El churn base es 16,8%; el problema esta desbalanceado.
2. La senal mas fuerte es `Tenure`: clientes nuevos churnean mucho mas.
3. `Complain` es muy accionable, pero hay que validar temporalidad por posible leakage.
4. `CashbackAmount` tiene senal: clientes que churnean reciben menos cashback.
5. Los segmentos mobile, solteros y cash on delivery muestran churn superior.
6. `DaySinceLastOrder` y `SatisfactionScore` no se comportan como la intuicion esperada; requieren cuidado antes de explicarlos al gerente.
7. La proxima etapa deberia separar train/test de forma estratificada y mover imputacion/limpieza a un pipeline reproducible.
