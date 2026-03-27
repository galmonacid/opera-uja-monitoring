# 03 — Contrato de payload y parsing

## 1) Campos observados en payload (ejemplo real)
Campos:
- ver
- sn
- mac
- ip
- srcname
- srctype
- tz
- opt
- meter
- __dt

Donde:
- `meter` contiene una lista de entradas con:
  - `name` (equipo/medidor)
  - `idowner`
  - `time` (epoch seconds)
  - `data[]` con tuplas {var, type, unit, value}

## 2) Punto crítico: JSON válido
En los ejemplos, el payload aparece con formato tipo `[{name=..., data=[{var=...}]}]`
Acción:
- Confirmar con operador si llega como JSON estricto o como formato key=value.
- Si no es JSON, el backend implementa parser robusto (sin OCR).

## 3) Semántica temporal
- `meter.time`: epoch seconds (confirmar si UTC).
- `tz`: timezone del origen (ej: Europe/Paris).
- Regla: normalizar a UTC en backend.

## 4) Duplicados / orden / backlog
Confirmar:
- ¿Puede haber backlog si cae la conexión?
- ¿Puede llegar fuera de orden?
- ¿Puede haber duplicados de timestamp?
Backend debe:
- Deduplicar por (rt_id, ts_event) en histórico si aplica.
- Mantener “latest” por rt_id.
 - Si un mismo evento trae varias entradas `meter[]` con tiempos distintos, se almacenan todas en histórico.

## 5) Contrato mínimo para la solución
Requisitos del payload para que la solución funcione:
- `meter.time` presente.
- `data.var`, `data.unit`, `data.value` presentes.
- `meter.name` estable en el tiempo.
- Los valores inválidos se evalúan en ingestión según la política de anomalías.

### 5.1 Filtro de valores inválidos (sentinelas)
Los valores no finitos o fuera de rango razonable (`abs(value) > 1e6` por defecto) se registran como anomalía y no se persisten en `latest` ni en histórico analítico.
Este umbral es configurable vía `MAX_VALID_VALUE`.

### 5.2 Política de anomalías y trazabilidad
La solución distingue entre:
- `raw_validation`: valor técnico observado tal como llega o como puede reconstruirse desde histórico.
- `analytics`: valor utilizable para KPIs, balance y series operativas.

Reglas activas:
- `negative_not_allowed`: demanda de energía, agua y potencias FV/autoconsumo no deben ser negativas.
- `above_max_threshold`: `abs(value)` por encima del umbral configurado.
- `non_finite`: `NaN`, `Infinity` o valor no numérico.
- Excepción explícita: `uja.jaen.fv.endesa.ct_total.p_kw` puede llegar negativo en raw.

Comportamiento:
- Solo los RT con normalización explícita pactada, como `uja.jaen.fv.auto.ct_total.p_kw`, siguen transformándose a `0` en ingestión y además se registran en `validation_anomalies`.
- Las anomalías que no pertenecen a esos RT excepcionales no se fuerzan a `0` en ingestión; se registran y no se persisten en `latest_readings` ni en Timestream.
- La tabla `validation_anomalies` conserva `raw_value`, `applied_value`, `anomaly_type`, `reason` y `ts_event`.

Limitación:
- Si un valor histórico ya fue clamped en ingestión antes de existir este registro, puede no ser recuperable retrospectivamente salvo que siga visible en Timestream raw.

## 6) Lista de datos a solicitar al operador (para cerrar mapeo)
- Catálogo por gateway:
  - meter.name
  - data.var
  - unit
  - Jaén agua observado: `meter.name = "UJA-Agua-Opera--m3.Edif_*"` y `data.var = "m3"`
  - FV autoconsumo Jaén observado: `meter.name = "OPERA-UNIVER--Autocon--FV.UJA"` con vars `UJA.Tot_FV_kW sys`, `UJA.Pérgola_kW sys`, `UJA.B5_Radiación`, etc.
  - Linares mix observado: `meter.name = "CCTL-TOTAL.<...>"`, `data.var = "m3"` y `data.var = "kW sys"` (normalizado a `KW sys`)
  - FV Endesa Jaén observado: `meter.name = "Jaén-OPERA-Endesa--FV.UJA"` (var `Tot_FV_kW sys`, `Tot_FV_kWh`, `P3_Inv1_kW sys`, `P3_Radiación`, etc.)
- Frecuencia de envío por gateway.
- Agua: contador acumulado vs incremental.
- Identificación exacta de:
  - inversores FV (Endesa/autoconsumo)
  - CT total
  - radiación por ubicación
