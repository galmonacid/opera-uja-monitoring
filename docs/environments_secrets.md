# Environments and secrets

## Objetivo
Documentar configuracion requerida para CI/CD y trabajo local sin exponer secretos en el repo.

## CI/CD (GitHub Actions)
- `AWS_ROLE_ARN` (secreto): rol OIDC para despliegues.
- `LAMBDA_ARTIFACT_BUCKET` (secreto o variable): bucket de artefactos Lambda.
- `AWS_REGION` (variable): `eu-west-1`.
- `AMPLIFY_APP_ID` (secreto): id de app Amplify.
- `AMPLIFY_BRANCH` (secreto): branch de Amplify (p.ej. `main`).
- `VITE_API_BASE` (variable): URL base de la API para el build del frontend.

## Desarrollo local
- `AWS_PROFILE=uja` (recomendado) con region en `~/.aws/config`.
- Alternativa: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_SESSION_TOKEN` (solo si es necesario).

## Parametros de stacks (no secretos)
- DynamoDB/Timestream: nombres por defecto en `infra/dynamodb.yaml` y `infra/timestream.yaml`.
- Lambda ingest: `DDB_LATEST_TABLE`, `DDB_MAPPING_TABLE`, `TS_DATABASE`, `TS_TABLE`, `LOG_LEVEL`.
- Aggregations: `DDB_AGG_TABLE`, `DDB_MAPPING_TABLE`, `DDB_CONFIG_TABLE`, `TS_DATABASE`, `TS_TABLE`, `CALC_VERSION`.
- API: `DDB_LATEST_TABLE`, `DDB_AGG_TABLE`, `ALLOWED_ORIGIN`.

## Higiene
- No commitear secretos ni archivos de credenciales.
- Si cambian variables o secretos, actualizar este documento.
