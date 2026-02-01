# 13 — Protocolo de desarrollo agéntico (UJA Monitoring)

## Objetivos
- Mantener cambios pequeños, revisables y reversibles.
- Aportar evidencia clara de tests y cambios de comportamiento.

## Alcance específico del proyecto
- Fuente de verdad: `docs/10-plan.md` y evidencias por gateway.
- IaC en `infra/` (CloudFormation). IoT Things/certificados se gestionan manualmente.
- Cada gateway requiere `seeds/gateway_variable_map_*.csv` + actualización de `docs/04-variables.md`.
- Backend “listo” significa: IoT Rule → `lambda_ingest_telemetry` → escritura en DynamoDB/Timestream + mapping cargado + smoke test registrado.

## Disciplina de cambios
- Preferir diffs pequeños y con alcance acotado.
- No mezclar refactors con nuevas features.
- Actualizar documentación junto con cambios de código/infra cuando aplique.
- Mantener IaC sin Things/certificados (gestion manual).

## Flujo por cambio (por tarea)
- Reconfirmar alcance y criterios de aceptación.
- Implementar el cambio mínimo viable.
- Añadir/actualizar tests cuando aplique.
- Registrar comandos de test y resultados.
- Resumir cambios de comportamiento y riesgos.
- Actualizar estado en `docs/10-plan.md` cuando cambie una tarea.

## Evidencia
- Reportar siempre comandos de test y resultados.
- Notar tests omitidos y el motivo.
- Para entregables del cliente, crear/actualizar `docs/12-evidencias-*.md`.
- Incluir outputs clave (stacks, smoke tests, carga de mapping).

## Safety checks
- Identificar cambios de riesgo (auth, API pública, costes).
- Añadir guardrails (validación, throttling, logging, WAF) cuando aplique.

## Rollback
- Para cambios que afecten prod, documentar pasos:
  - Qué revertir (stack/commit).
  - Configuración a restaurar.
  - Limpieza de datos si aplica (tablas/últimas lecturas).

## Datos + configuración
- No incluir secretos en el repo.
- Documentar configuración requerida en `docs/environments_secrets.md`.
- Preferir OIDC para CI/CD (sin claves largas).
- Usar stubs/mocks en unit tests cuando sea posible.
- Validar CSVs con `scripts/validate_gateway_map.py`.

## Plantilla de resumen de cambios
- Scope:
- Tests:
- Evidence:
- Risk/rollback:
- Plan updates:
