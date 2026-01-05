# UJA — Monitorización Energía/Agua/FV (AWS) — Índice de documentación

## Objetivo
Documentación mínima pero suficiente para construir y mantener una solución de monitorización (web pública) de:
- Consumo eléctrico
- Consumo de agua
- Producción FV (Endesa + Autoconsumo)
en Campus de Jaén y Campus de Linares.

## Documentos
1. `01_requirements.md` — Requerimientos y alcance
2. `02_gateways_topics.md` — Gateways y topics MQTT en AWS IoT
3. `03_payload_contract.md` — Contrato de payload y parsing
4. `04_variables_inventory_and_formulas.md` — Inventario completo de variables + fórmulas
5. `05_data_model_tables.md` — Modelo de datos y tablas (Timestream + DynamoDB)
6. `06_aws_architecture.md` — Arquitectura AWS y flujo de datos
7. `07_api_spec.md` — API pública (endpoints y payloads)
8. `08_frontend_spa_amplify.md` — Frontend SPA + Amplify (decisión)
9. `09_security_cost_controls.md` — Seguridad y control de costes/abuso
10. `10_plan_fase1_fase2.md` — Plan de fases y entregables

## Estado de completitud
- Variables mapeadas: ✅ 96 definidas (con placeholders donde falta meter.name exacto)
- Variables calculadas: ✅ definidas con fórmula exacta
- Tablas Timestream/DynamoDB: ✅ definidas y justificadas
- Arquitectura AWS: ✅ definida (IoT Core + Timestream + Lambda + DynamoDB + API GW + Amplify + WAF)
- Frontend: ✅ decisión SPA (React+Vite) + Amplify
- Pendientes externos: ✅ listado de datos a confirmar con operador de gateways (ver 03 y 04)
