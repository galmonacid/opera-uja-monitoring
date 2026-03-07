# 15 — Evidencias backend/frontend (gateway FV autoconsumo Jaen)

## Alcance
Gateway: `gw_autoconsumo_jaen`  
Topic: `uja/jaen/produccion/fv_autoconsumo/gw_autoconsumo_jaen`  
Region: `eu-west-1`

## Resumen de configuracion
- IoT Rule: `uja_ingest_gw_autoconsumo_jaen` (stack `uja-iot-rule-gw-autoconsumo-jaen`)
- Lambda ingest: `lambda_ingest_telemetry`
- Mapping cargable: `seeds/gateway_variable_map_gw_autoconsumo_jaen.csv` (15 filas, 11 RT_ID lógicos)
- Aggregation config: `jaen_fv_auto` en `seeds/aggregation_configs.csv`
- API:
  - `GET /v1/realtime?campus=jaen&domain=fv&gateway_id=gw_autoconsumo_jaen`
  - `GET /v1/series/24h?campus=jaen&metric=fv_auto`
  - `GET /v1/aggregates/daily?campus=jaen&metric=fv_auto&asset=total`
- Frontend:
  - tarjeta dedicada en `#/validacion`
  - balance principal de Jaén incorpora `uja.jaen.fv.auto.ct_total.p_kw`

## Cobertura implementada en repo
- Fixture dedicado: `lambda/ingest_telemetry/test_event_gw_autoconsumo_jaen.json`
- Unit test de ingestión:
  - resolución de `gateway_id` desde `topic`
  - variantes acentuadas/no acentuadas
  - normalización `kW sys` → `KW sys`
- Validación técnica:
  - separación por `gateway_id` para no mezclar RT_ID con `gw_jaen_energia`
  - serie 24h por métrica `fv_auto`
- Agregación diaria:
  - total calculado solo desde `uja.jaen.fv.auto.ct_total.p_kw`
  - activos individuales mantenidos como detalle técnico

## Evidencias a capturar tras despliegue
1. IoT Rule `uja_ingest_gw_autoconsumo_jaen` con SQL y acción Lambda
2. Ejemplo de mensaje real publicado en el topic del gateway
3. Registros en `latest_readings` filtrando `gateway_id = gw_autoconsumo_jaen`
4. Serie 24h `fv_auto` devolviendo puntos en la API pública
5. Agregados daily/monthly para `metric=fv_auto`
6. Captura de la sexta tarjeta en la pantalla de validación

## Notas
- IoT Things, certificados y policy del dispositivo siguen fuera de IaC.
- La validación con datos reales queda pendiente hasta confirmar escritura estable en DynamoDB/Timestream.
