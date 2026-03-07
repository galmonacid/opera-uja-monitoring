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
KPIs de balance (por campus).

Query params:
- campus=jaen|linares

Respuesta:
{
  "campus":"jaen",
  "ts_event":...,
  "kpis":[
    {"kpi":"autoconsumo_kw","value":...,"unit":"kW"},
    {"kpi":"red_kw","value":...,"unit":"kW"},
    {"kpi":"autoconsumo_pct","value":...,"unit":"%"}
  ]
}

### GET /v1/aggregates/daily
### GET /v1/aggregates/monthly
### GET /v1/aggregates/yearly
Query params:
- campus
- metric (energia_consumo, agua_consumo, fv_energia, fv_endesa, fv_auto, co2_evitar, etc.)
- asset=total|edificio_a1|inv01|...

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

### GET /v1/series/24h
Serie temporal (24h) para grafica de balance energetico.

Query params:
- campus=jaen|linares
- metric=energia_consumo|agua_consumo|fv_endesa|fv_auto (opcional)
- rt_prefix=uja.... (opcional, modo tecnico)

Respuesta por defecto (sin `metric`, balance campus):
{
  "campus":"jaen",
  "interval_minutes":5,
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
  "interval_minutes":5,
  "unit":"kW",
  "series":[
    {"ts":173...,"value":72.8},
    ...
  ]
}

Notas:
- Se filtran valores inválidos/sentinela en Timestream (por defecto `abs(value) > 1e6`).
- `gateway_id` permite aislar gateways que comparten prefijo de RT_ID, como `gw_jaen_energia` y `gw_autoconsumo_jaen`.
- En Jaén, el balance por defecto usa demanda total campus, FV Endesa por suma de inversores y FV autoconsumo por `ct_total`.
- Para `agua_consumo`, la serie 24h devuelve consumo por intervalo a partir de contadores acumulados (unidad `m3`).
- Si `monthly` no está materializado todavía en DynamoDB, la API puede reconstruirlo a partir de `daily`.

## 3) Limits (desde API Gateway/WAF)
- Rate limit por IP.
- Burst limit.
- WAF rule: rate-based.
