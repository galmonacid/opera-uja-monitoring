# 10 — Plan por fases, tareas y entregables

## Fase 1 — Análisis y diseño técnico (1 semana)
Tareas:
- Revisión de gateways y payload
- Definición de topics
- Definición inventario variables (96 mapeadas + calculadas)
- Definición de tablas y modelo de datos
- Definición de API
- Mockups/estructura web

Entregables:
- `01_requirements.md`
- `02_gateways_topics.md`
- `03_payload_contract.md`
- `04_variables_inventory_and_formulas.md`
- `05_data_model_tables.md`
- `06_aws_architecture.md`
- `07_api_spec.md`
- `08_frontend_spa_amplify.md`
- `09_security_cost_controls.md`

## Fase 2 — Configuración infraestructura AWS (2 semanas)
Tareas:
- Crear IoT Core + Rules + IAM
- Crear Timestream db/table
- Crear DynamoDB tables
- Lambdas (ingest + cálculos)
- API Gateway + WAF
- Amplify deploy inicial

Entregables (evidencia):
- Capturas/config summary de recursos creados
- API desplegada (URL)
- Web desplegada (URL)
- Prueba end-to-end con datos reales

## Pendientes externos (bloqueantes suaves)
- Catálogo meter.name/data.var por gateway para cerrar mapeo al 100% (ver `03` y `04`).
