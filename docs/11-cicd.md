# 11 — Estrategia CI/CD, testing y despliegues

## Objetivo
Garantizar calidad, trazabilidad y despliegues repetibles para software (backend/frontend) e infraestructura (IaC), con mínimo riesgo y coste.

## Alcance
- Software: Lambdas, API, frontend.
- Infra: CloudFormation para IoT Rules, Lambda, datos, API y seguridad.
- Fuera de IaC: IoT Things y certificados (gestion manual para no romper keys actuales).
  - Nota: no se incluye plantilla `iot-core.yaml`.

## Repos y ramas
- `main`: producción.
- `feature/*`: trabajo diario; merge via PR.
- Versionado opcional por tags (`vX.Y.Z`) al cerrar entregas.

## Modelo recomendado para este proyecto
- Un solo repo (infra + backend + frontend).
- Workflows separados por dominio (CI, CD infra, CD backend, CD frontend).
- Triggers por rutas para limitar despliegues (solo cuando cambia lo relevante).

## CI (Pull Requests)
Checks automáticos:
- Lint/format (Python y frontend si aplica).
- Tests unitarios (lambda y utilidades).
- Validación de artefactos de datos (CSV de `gateway_variable_map`).
- Validación IaC (plantillas CloudFormation).

Workflow: `.github/workflows/ci.yml`

## Testing (capas)
1) Unitario
   - Parsing del payload, mapeo y reglas A0/C4/Magisterio + A3/B4.
   - Usar `lambda/ingest_telemetry/test_event.json`.
2) Integración (opcional)
   - LocalStack o entorno AWS dev.
   - Verificar escrituras en DynamoDB y Timestream.
3) E2E / Smoke
   - Publicar un mensaje MQTT de prueba al topic y confirmar `latest_readings`.

## CD (merge a main)
Infra (IaC):
- CloudFormation (stacks separados: IoT Rules, datos, lambda, API, seguridad).
- Deploy por entorno (`dev`/`prod`) con parámetros.

Software:
- Backend (Lambda): zip → S3 → update stack.
- Datos: carga de `gateway_variable_map` desde CSV (script en `scripts/load_gateway_map.py`).
- Frontend: Amplify conectado al repo (build y deploy automático).
- Alternativa frontend: build + deploy a S3/CloudFront (si se evita Amplify).

Workflows:
- Infra: `.github/workflows/cd-infra.yml` (paths: `infra/timestream.yaml`, `infra/dynamodb.yaml`)
- Backend: `.github/workflows/cd-backend.yml` (paths: `lambda/**`, `seeds/**`, `scripts/**`, `infra/lambda-ingest-telemetry.yaml`, `infra/lambda-aggregations.yaml`, `infra/lambda-api.yaml`, `infra/api-gateway.yaml`, `infra/iot-rule-gw-jaen-energia.yaml`)
- Frontend: despliegue gestionado por Amplify (sin workflow en repo)

## Variables y secretos
- `AWS_ROLE_ARN`: rol OIDC para deploy.
- `LAMBDA_ARTIFACT_BUCKET`: bucket de artefactos Lambda.
- Región por defecto: `eu-west-1`.

## Entornos
- `dev` / `prod` como mínimo.
- Prefijo de stack: `uja-dev-*`, `uja-prod-*`.
- Variables de entorno por stack (tablas, DB, etc.).

## Seguridad
- CI con OIDC (sin claves estáticas).
- Least privilege por pipeline (solo permisos de deploy).

## Observabilidad y rollback
- Smoke test post-deploy.
- CloudFormation rollback automático.
- Versionado de Lambda (alias `prod`) para rollback rápido.
