# UJA — Monitorización Energía/Agua/FV (AWS) — Índice de documentación

## Objetivo
Documentación mínima pero suficiente para construir y mantener una solución de monitorización (web pública) de:
- Consumo eléctrico
- Consumo de agua
- Producción FV (Endesa + Autoconsumo)
en Campus de Jaén y Campus de Linares.

## Documentos
1. `01-requirements.md` — Requerimientos y alcance
2. `02-gateway_topics.md` — Gateways y topics MQTT en AWS IoT
3. `03-payload_contract.md` — Contrato de payload y parsing
4. `04-variables.md` — Inventario completo de variables + formulas
5. `05-data_model.md` — Modelo de datos y tablas (Timestream + DynamoDB)
6. `06-aws_architecture.md` — Arquitectura AWS y flujo de datos
7. `07-api_spec.md` — API publica (endpoints y payloads)
8. `08-frontend.md` — Frontend SPA + Amplify (decision)
9. `09-controls.md` — Seguridad y control de costes/abuso
10. `10-plan.md` — Plan de fases y entregables
11. `11-cicd.md` — Estrategia CI/CD, testing y despliegues
12. `12-evidencias-gw-jaen-energia.md` — Evidencias backend (gateway consumo energia Jaen)
13. `13-agentic-protocol.md` — Protocolo de desarrollo agentico
14. `environments_secrets.md` — Configuracion y secretos por entorno

## Estado de completitud
- Variables mapeadas: ✅ 99 definidas (con placeholders donde falta meter.name exacto)
- Variables calculadas: ✅ definidas con fórmula exacta
- Tablas Timestream/DynamoDB: ✅ definidas y justificadas
- Arquitectura AWS: ✅ definida (IoT Core + Timestream + Lambda + DynamoDB + API GW + Amplify + WAF)
- Frontend: ✅ decisión SPA (React+Vite) + Amplify
- CI/CD: ✅ estrategia definida
- Pendientes externos: ✅ listado de datos a confirmar con operador de gateways (ver 03 y 04)
