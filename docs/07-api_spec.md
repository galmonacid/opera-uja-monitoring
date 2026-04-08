# 07 — API pública (especificación)

## 1) Principios
- API pública, read-only.
- Datos ya procesados (no heavy compute por request).
- Respuesta JSON.
- CORS permitido para dominio Amplify.

## 2) Endpoints (v1)

### GET /v1/realtime
Devuelve valores actuales (latest) para un conjunto de RT_ID o por campus/dominio.

Query params (opcionales):
- campus=jaen|linares
- domain=energia|agua|fv
- gateway_id=gw_jaen_energia|gw_jaen_agua|gw_linares_mix|gw_endesa_jaen|gw_endesa_linares|gw_autoconsumo_jaen
- rt_id=... (repetible)

Respuesta (ejemplo):
{
  "ts": 173...,
  "items": [
    {"rt_id":"uja.jaen.energia.consumo.edificio_a1.p_kw","value":123.4,"unit":"kW","ts_event":...,"gateway_id":"gw_jaen_energia"},
    ...
  ]
}

### GET /v1/kpis
KPIs de balance para los paneles del dashboard principal.

Query params:
- scope=las_lagunillas|ctl_linares

Respuesta:
{
  "scope":"las_lagunillas",
  "campus":"jaen",
  "label":"Campus Las Lagunillas",
  "status":"complete",
  "missing_sources":[],
  "ts_event":...,
  "kpis":[
    {"kpi":"demanda_kw","value":...,"unit":"kW"},
    {"kpi":"fv_kw","value":...,"unit":"kW"},
    {"kpi":"red_kw","value":...,"unit":"kW"},
    {"kpi":"autoconsumo_kw","value":...,"unit":"kW"},
    {"kpi":"autoconsumo_pct","value":...,"unit":"%"}
  ]
}

### GET /v1/aggregates/daily
### GET /v1/aggregates/monthly
### GET /v1/aggregates/yearly
Query params:
- campus
- metric (energia_consumo, agua_consumo, fv_energia, fv_endesa, fv_auto, co2_evitar, etc.)
- asset=total|edificio_a1|inv01|...|all
- assets=edificio_a1,edificio_a2,inv01,... (lista separada por comas; se puede combinar con `asset`)

Respuesta:
{
  "campus":"jaen",
  "metric":"energia_consumo",
  "period":"daily",
  "unit":"kWh",
  "series":[
    {"date":"2025-09-30","value":...},
    ...
  ]
}

Respuesta (multi-asset con `asset=all` o `assets=...`):
{
  "campus":"jaen",
  "metric":"agua_consumo",
  "period":"monthly",
  "unit":"m3",
  "assets":["deposito_principal","edificio_a1","total"],
  "series":[
    {
      "date":"2026-03",
      "assets":{
        "deposito_principal":...,
        "edificio_a1":...,
        "total":...
      }
    }
  ],
  "asset_values":{
    "deposito_principal":...,
    "edificio_a1":...,
    "total":...
  },
  "asset_values_date":"2026-03"
}

### GET /v1/series/24h
Serie temporal (24h) para grafica de balance energetico.

Query params:
- scope=las_lagunillas|ctl_linares (opcional, modo dashboard)
- campus=jaen|linares
- metric=energia_consumo|agua_consumo|fv_endesa|fv_auto (opcional)
- rt_id=... (repetible, opcional)
- aggregation=sum|avg|max (solo cuando se usa `rt_id` repetible)
- interval_minutes=5|15 (opcional)
- rt_prefix=uja.... (opcional, modo tecnico)

Respuesta por scope (modo dashboard principal):
{
  "scope":"las_lagunillas",
  "campus":"jaen",
  "label":"Campus Las Lagunillas",
  "status":"complete",
  "missing_sources":[],
  "interval_minutes":15,
  "unit":"kW",
  "series":[
    {"ts":173...,"demand":123.4,"pv":45.6},
    ...
  ]
}

Respuesta por defecto (sin `metric` ni `scope`, balance campus):
{
  "campus":"jaen",
  "interval_minutes":15,
  "unit":"kW",
  "series":[
    {"ts":173...,"demand":123.4,"pv":45.6},
    ...
  ]
}

Respuesta con `metric`:
{
  "campus":"jaen",
  "metric":"fv_auto",
  "interval_minutes":15,
  "unit":"kW",
  "series":[
    {"ts":173...,"value":72.8},
    ...
  ]
}

Respuesta con `rt_id` repetible:
{
  "rt_ids":["uja.jaen.fv.endesa.rad01.g_wm2","uja.jaen.fv.endesa.rad02.g_wm2"],
  "aggregation":"avg",
  "interval_minutes":15,
  "unit":"W/m²",
  "series":[
    {"ts":173...,"value":512.4},
    ...
  ]
}

Notas:
- En ingestión, las anomalías se registran en `validation_anomalies`. Solo los RT con normalización explícita, como `uja.jaen.fv.auto.ct_total.p_kw`, se persisten ajustados a `0`; el resto no se escribe en `latest` ni en histórico.
- `gateway_id` permite aislar gateways que comparten prefijo de RT_ID, como `gw_jaen_energia` y `gw_autoconsumo_jaen`.
- En Jaén, el balance por defecto usa demanda total campus, FV Endesa por `abs(ct_total)` y FV autoconsumo por `ct_total + edificio_a0`.
- En modo `scope`, `las_lagunillas` usa solo A0-A4, B1-B5, C1-C3/C5/C6, D1-D4 y `carga_vhe`; excluye `um_c4`, `ae_magisterio`, `apartamentos_universitarios`, `residencia_domingo_savio` y `polideportivo`.
- En modo `scope`, la FV de `las_lagunillas` = `abs(uja.jaen.fv.endesa.ct_total.p_kw)` + `uja.jaen.fv.auto.ct_total.p_kw` + `uja.jaen.fv.auto.edificio_a0.p_kw`.
- `uja.jaen.fv.endesa.ct_total.p_kw` puede llegar en raw con signo negativo; en `scope` se publica con magnitud positiva para mantener la convención visual del portal.
- `metric=fv_endesa` y sus agregados diarios/mensuales en Jaén siguen calculándose por suma de inversores, no por `ct_total`.
- En modo `scope`, `ctl_linares` usa `lab_sg_t1`, `lab_sg_t2`, `urbanizacion`, `aulario_departamental`, `polideportivo` y FV desde `uja.linares.fv.endesa.ct_total.p_kw`.
- `status` puede ser `complete`, `partial` o `empty`. Si faltan fuentes obligatorias, `missing_sources` lista los identificadores afectados y la serie agregada se devuelve vacía.
- En potencia e irradiancia, cada bin devuelve la media de las muestras válidas dentro del intervalo solicitado.
- Para `agua_consumo`, la serie 24h devuelve consumo por intervalo a partir de contadores acumulados (unidad `m3`).
- Para `agua_consumo`, el bin usa el último contador válido del intervalo y la API transforma la serie a consumo incremental entre bins consecutivos.
- Las vistas visuales del portal consumen `interval_minutes=15` como granularidad estándar.
- Si `monthly` no está materializado todavía en DynamoDB, la API puede reconstruirlo a partir de `daily`.
- Compatibilidad: `asset=total` mantiene el contrato anterior (`series` con `{date, value}` sin bloque `assets`).
- Para mapa de agua, usar `metric=agua_consumo` + `period=monthly|yearly` + `asset=all` (o `assets=...`); `asset_values` devuelve directamente el mapa `asset -> value` de la fecha más reciente disponible.

### GET /v1/anomalies
Registro técnico reciente de anomalías detectadas durante ingestión o backfill.

Query params (opcionales):
- campus=jaen|linares
- domain=energia|agua|fv
- gateway_id=gw_jaen_energia|gw_jaen_agua|gw_linares_mix|gw_endesa_jaen|gw_endesa_linares|gw_autoconsumo_jaen
- lookback_hours=72 (default)
- limit=200 (default)

Respuesta:
{
  "items":[
    {
      "gateway_id":"gw_jaen_energia",
      "campus":"jaen",
      "domain":"energia",
      "rt_id":"uja.jaen.energia.consumo.edificio_a3.p_kw",
      "unit":"kW",
      "raw_value":"-106.63",
      "applied_value":null,
      "anomaly_type":"negative_not_allowed",
      "reason":"Valor negativo no permitido para este punto.",
      "threshold":"0",
      "ts_event":1735733400,
      "detected_by":"backfill"
    }
  ],
  "count":1,
  "lookback_hours":72
}

Notas:
- `Validación` usa este endpoint para la tabla global `Anomalías detectadas`.
- La analítica pública excluye o corrige estas muestras antes de construir KPIs/series operativas.
- `realtime` sigue siendo la vista técnica de latest; el registro de anomalías aporta la trazabilidad del raw y del valor aplicado.

## 3) Limits (desde API Gateway/WAF)
- Rate limit por IP.
- Burst limit.
- WAF rule: rate-based.
