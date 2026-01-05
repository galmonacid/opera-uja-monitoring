# 05 — Modelo de datos y tablas (Timestream + DynamoDB)

## 1) Objetivo
Separar:
- histórico (series temporales) → Timestream
- último valor + agregados + KPIs + mapping → DynamoDB

Esto reduce coste y mejora performance de dashboards.

---

## 2) Timestream

### 2.1 Database
- `uja_monitoring`

### 2.2 Table
- `telemetry_rt`

### 2.3 Esquema lógico
- Time: `ts_event` (UTC)
- MeasureName: `measure` (opcional; si usamos single-measure, measure = "value")
- MeasureValue: `value` (DOUBLE)
- Dimensions:
  - `rt_id`
  - `campus`
  - `domain` (energia/agua/fv)
  - `system` (consumo/endesa/autoconsumo)
  - `asset` (edificio_a1, inv01, rad01…)
  - `unit`
  - `gateway_id`

### 2.4 Retención (propuesta)
- Memory store: 7 días
- Magnetic store: 24 meses

---

## 3) DynamoDB (tablas separadas — decisión)

### 3.1 Tabla: `latest_readings`
Propósito: servir datos “realtime” en 1 lectura por RT_ID.

- PK: `rt_id`
- Atributos:
  - `value` (number)
  - `unit` (string)
  - `ts_event` (number/timestamp)
  - `gateway_id` (string)
  - `quality` (string opcional)
  - `updated_at` (timestamp)

### 3.2 Tabla: `aggregates`
Propósito: guardar agregados por periodo (daily/monthly/yearly) sin recalcular en cada consulta.

- PK: `pk` (ej: `jaen#energia#consumo#daily`)
- SK: `sk` (ej: `2025-09-30#total` o `2025-09-30#edificio_a1`)
- Atributos:
  - `value`
  - `unit`
  - `ts_calculated`
  - `calc_version`

### 3.3 Tabla: `kpis_realtime`
Propósito: KPIs de balance en tiempo real por campus.

- PK: `campus` (jaen/linares)
- SK: `kpi` (autoconsumo_kw, red_kw, autoconsumo_pct, etc.)
- Atributos:
  - `value`
  - `unit`
  - `ts_event`
  - `updated_at`

### 3.4 Tabla: `gateway_variable_map`
Propósito: traducir `meter.name::data.var` → `rt_id`.

- PK: `gateway_id`
- SK: `source_key` (`<meter.name>::<data.var>`)
- Atributos:
  - `rt_id`
  - `unit_expected`
  - `enabled` (bool)
  - `notes`

---

## 4) Consideraciones
- No hay tráfico alto → DynamoDB on-demand.
- Separar tablas reduce riesgo de diseño prematuro y acelera delivery.
