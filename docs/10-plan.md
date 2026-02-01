# 10 — Plan por fases, tareas y entregables

## Fase 1 — Análisis y diseño técnico (1 semana)
Tareas:
- [COMPLETO] Revisión de gateways y payload
- [COMPLETO] Definición de topics
- [COMPLETO] Definición inventario variables (99 mapeadas + calculadas)
- [COMPLETO] Definición de tablas y modelo de datos
- [COMPLETO] Definición de API
- [COMPLETO] Mockups/estructura web

Entregables:
- `01-requirements.md`
- `02-gateway_topics.md`
- `03-payload_contract.md`
- `04-variables.md`
- `05-data_model.md`
- `06-aws_architecture.md`
- `07-api_spec.md`
- `08-frontend.md`
- `09-controls.md`

## Fase 2A — Backend MVP (solo gateway consumo energia Jaen) (1-2 semanas)
Tareas:
- [COMPLETO] Confirmar split `meter.name`/`data.var` del gateway `gw_jaen_energia`
- [COMPLETO] Crear IoT Rule para `uja/jaen/consumo/energia/gw_jaen_energia` (template listo)
- [COMPLETO] Crear Timestream db/table (`uja_monitoring`/`telemetry_rt`) (desplegado)
- [COMPLETO] Crear DynamoDB tables (`latest_readings`, `aggregates`, `kpis_realtime`, `gateway_variable_map`) (desplegado)
- [COMPLETO] Implementar `lambda_ingest_telemetry` con reglas A0/C4/Magisterio y A3/B4
- [COMPLETO] Cargar `gateway_variable_map` para `gw_jaen_energia`
- [COMPLETO] Prueba end-to-end con datos reales (incluye B3 cuando esté operativo)

Entregables (evidencia):
- Capturas/config summary de recursos creados
- Prueba end-to-end con datos reales (gateway Jaen energia)

## Fase 2B — Backend API + agregados (solo Jaen energia) (1 semana)
Tareas:
- [COMPLETO] Implementar jobs de agregacion (daily/monthly/yearly) (IaC + lambdas)
- [COMPLETO] Implementar endpoints `/v1/realtime` y `/v1/aggregates/*` (solo energia Jaen)
- [COMPLETO] Configurar API Gateway + WAF + throttling (IaC)
- [COMPLETO] Endpoint serie 24h (demanda + FV campus) para grafica de areas

Entregables (evidencia):
- API desplegada (URL) con datos reales de Jaen energia

## Fase 2C — Frontend MVP (solo Jaen energia) (1 semana)
Tareas:
- [COMPLETO] Redisenio MVP funcional (solo 2 secciones)
- [COMPLETO] Infografia balance (demanda/FV/red) desde `/realtime`
- [COMPLETO] Grafica de areas 24h desde `/series/24h`
- [COMPLETO] Mapa campus con `campus.png` + overlays por edificio (primeras coordenadas)
- [COMPLETO] SPA base (React + Vite)
- [COMPLETO] Despliegue inicial en Amplify

Entregables (evidencia):
- Web desplegada (URL) con consumo Jaen energia

## Fase 2D — CI/CD y testing (1 semana)
Tareas:
- [COMPLETO] Definir pipeline CI (software + IaC: lint + unit tests + checks CSV + validacion CFN)
- [COMPLETO] Anadir tests unitarios para `lambda_ingest_telemetry`
- [COMPLETO] Preparar pipeline CD infra (CloudFormation por entorno)
- [COMPLETO] Preparar pipeline CD backend (Lambda zip + carga mapping)
- [] Preparar pipeline CD frontend (Amplify o S3/CloudFront)
- [COMPLETO] Smoke test post-deploy (MQTT → `latest_readings`)

## Fase 3A — Backend ampliado (resto gateways) (2-3 semanas)
Tareas:
- [] Confirmar catálogo `meter.name`/`data.var` del resto de gateways
- [] Completar `gateway_variable_map` para agua, FV Endesa y FV autoconsumo
- [] Extender `lambda_ingest_telemetry` a nuevos gateways
- [] Habilitar reglas IoT para el resto de topics
- [] Validar agregados y KPIs para agua y FV

## Fase 3B — Frontend ampliado (resto secciones) (1-2 semanas)
Tareas:
- [] Añadir secciones agua, FV e indicadores
- [] Integración con endpoints adicionales
- [] Ajustes de UI/UX y performance

## Pendientes externos (bloqueantes suaves)
- [] Catálogo meter.name/data.var por gateway para cerrar mapeo al 100% (ver `03-payload_contract.md` y `04-variables.md`)
- [] Confirmación de conectividad/red del gateway (puertos salientes a AWS IoT)
