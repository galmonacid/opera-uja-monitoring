# 06 — Arquitectura AWS y flujo de datos

## 1) Servicios AWS usados
- AWS IoT Core (MQTT ingestion)
- AWS IoT Rules (enrutado a Lambda)
- AWS Lambda (ingesta, normalización, cálculos)
- Amazon Timestream (histórico)
- DynamoDB (latest/agregados/kpis/mapeo)
- EventBridge (jobs programados de agregación)
- API Gateway (API pública)
- AWS Amplify (hosting SPA)
- AWS WAF (protección API)
- CloudWatch (logs/métricas/alarmas)

## 2) Flujo end-to-end (paso a paso)
1. Gateway publica a su topic `uja/.../gw_xxx`.
2. IoT Core recibe el mensaje.
3. IoT Rule invoca `lambda_ingest_telemetry`.
4. `lambda_ingest_telemetry`:
   - parsea payload (JSON o key=value)
   - extrae (meter.name, data.var, unit, value, time)
   - consulta `gateway_variable_map` para obtener `rt_id`
   - escribe:
     - Timestream: punto histórico (rt_id, ts_event, value, unit, dimensions)
     - DynamoDB `latest_readings`: último valor por rt_id
5. EventBridge dispara:
   - `lambda_calc_daily` (1 vez/día)
   - `lambda_calc_monthly` (1 vez/mes)
   - `lambda_calc_yearly` (1 vez/año)
   - (opcional) `lambda_calc_kpis_realtime` cada 1–5 min si se decide no calcular en consulta.
6. API Gateway expone endpoints que leen de DynamoDB (latest/agregados/kpis).
7. Frontend SPA (Amplify) consume API.

## 3) Razones del diseño
- Performance: web consulta DynamoDB (rápido).
- Histórico completo: Timestream para auditoría y cálculos.
- Coste controlado: cálculo programado + rate limit en API.
