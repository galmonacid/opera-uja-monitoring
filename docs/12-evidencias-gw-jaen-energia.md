# 12 — Evidencias backend (gateway consumo energia Jaen)

## Alcance
Gateway: `gw_jaen_energia`  
Topic: `uja/jaen/consumo/energia/gw_jaen_energia`  
Region: `eu-west-1`

## Resumen de configuracion (backend)
- IoT Rule: `uja_ingest_gw_jaen_energia` (stack `uja-iot-rule-gw-jaen-energia`)
- Lambda: `lambda_ingest_telemetry` (stack `uja-lambda-ingest-telemetry`)
- Timestream: DB `uja_monitoring`, tabla `telemetry_rt` (stack `uja-timestream`)
- DynamoDB: `latest_readings`, `aggregates`, `kpis_realtime`, `gateway_variable_map` (stack `uja-dynamodb`)
- Mapping cargado: 28 entradas en `gateway_variable_map` para `gw_jaen_energia`
- Aggregations: `lambda_calc_daily`, `lambda_calc_monthly`, `lambda_calc_yearly` (stack `uja-lambda-aggregations`)
- API Lambda: `lambda_api_public` (stack `uja-lambda-api`)
- API Gateway + WAF: `uja-api-gateway` con WAF `uja-api-waf`
- API URL: `https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1`

## Capturas / evidencias (para cliente)
Adjuntar capturas de:
1) IoT Rule `uja_ingest_gw_jaen_energia` (SQL y accion Lambda)
2) Lambda `lambda_ingest_telemetry` (configuracion + variables de entorno)
3) Timestream DB/tabla (retencion memoria 7 dias / magnetico 24 meses)
4) DynamoDB tablas (creadas y activas)
5) Ejemplo de `latest_readings` con un RT_ID del campus Jaen
6) EventBridge rules `uja-calc-daily`, `uja-calc-monthly`, `uja-calc-yearly`
7) API Gateway `uja-public-api` (stage `v1`) + WAF asociado

## Prueba end-to-end (Jaen energia)
Ejecucion realizada con payload de prueba (archivo `lambda/ingest_telemetry/test_event.json`):
- Resultado: `{"status":"ok","count":11}`
- Ajustes aplicados: A0, C4, Magisterio, A3 y B4 (sumas/restas segun reglas).

Para evidenciar con datos reales:
1) Enviar mensaje real desde el gateway al topic MQTT.
2) Verificar escritura en `latest_readings` para un RT_ID (ej: `uja.jaen.energia.consumo.edificio_a0.p_kw`).

Opcional (API):
- `GET https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1/realtime`
- `GET https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1/aggregates/daily`
  - Respuesta esperada sin filtros: `{"error":"missing_filters"}` (HTTP 200)

## Smoke tests agregados (2026-02-01)
- `lambda_ingest_telemetry` OK: `{"status":"ok","count":11}`
- `lambda_calc_daily` OK (misma fecha): `{"status":"ok","count":9}`
- `lambda_calc_monthly` OK: `{"status":"ok","count":9}`
- `lambda_calc_yearly` OK: `{"status":"ok","count":9}`

Nota: si el timestamp del payload es anterior a la ventana de memoria (7 dias), Timestream rechaza los registros. Para smoke tests usar timestamp actual.

## Notas
- IoT Things y certificados se gestionan manualmente (no IaC).
- El medidor B3 esta pendiente de sustitucion.
