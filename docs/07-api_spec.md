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
- rt_id=... (repetible)

Respuesta (ejemplo):
{
  "ts": 173...,
  "items": [
    {"rt_id":"uja.jaen.energia.consumo.edificio_a1.p_kw","value":123.4,"unit":"kW","ts_event":...},
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
- metric (energia_consumo, agua_consumo, fv_energia, co2_evitar, etc.)
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

## 3) Limits (desde API Gateway/WAF)
- Rate limit por IP.
- Burst limit.
- WAF rule: rate-based.
