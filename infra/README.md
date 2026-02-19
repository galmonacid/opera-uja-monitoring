# Infra

## IoT Core
IoT Things and certificates are managed manually and intentionally excluded from IaC.

## IoT Rule
Templates:
- `infra/iot-rule-gw-jaen-energia.yaml`
- `infra/iot-rule-gw-endesa-linares.yaml`
- `infra/iot-rule-gw-endesa-jaen.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-iot-rule-gw-jaen-energia \
  --template-file infra/iot-rule-gw-jaen-energia.yaml \
  --parameter-overrides IngestLambdaName=lambda_ingest_telemetry

aws cloudformation deploy \
  --stack-name uja-iot-rule-gw-endesa-linares \
  --template-file infra/iot-rule-gw-endesa-linares.yaml \
  --parameter-overrides IngestLambdaName=lambda_ingest_telemetry

aws cloudformation deploy \
  --stack-name uja-iot-rule-gw-endesa-jaen \
  --template-file infra/iot-rule-gw-endesa-jaen.yaml \
  --parameter-overrides IngestLambdaName=lambda_ingest_telemetry
```

## Lambda ingest_telemetry
Template: `infra/lambda-ingest-telemetry.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-lambda-ingest-telemetry \
  --template-file infra/lambda-ingest-telemetry.yaml \
  --parameter-overrides \
    FunctionName=lambda_ingest_telemetry \
    CodeS3Bucket=<bucket> \
    CodeS3Key=<path/to/lambda.zip>
```

## Timestream
Template: `infra/timestream.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-timestream \
  --template-file infra/timestream.yaml \
  --parameter-overrides DatabaseName=uja_monitoring TableName=telemetry_rt
```

## DynamoDB
Template: `infra/dynamodb.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-dynamodb \
  --template-file infra/dynamodb.yaml
```

### Load gateway_variable_map
```bash
python3 scripts/load_gateway_map.py \
  --file seeds/gateway_variable_map_gw_jaen_energia.csv \
  --table gateway_variable_map
```

### Load aggregation_configs
```bash
python3 scripts/load_aggregation_configs.py \
  --file seeds/aggregation_configs.csv \
  --table aggregation_configs
```

## Aggregations (daily/monthly/yearly)
Template: `infra/lambda-aggregations.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-lambda-aggregations \
  --template-file infra/lambda-aggregations.yaml \
  --parameter-overrides \
    CodeS3Bucket=<bucket> \
    CodeS3KeyDaily=<path/to/lambda_calc_daily.zip> \
    CodeS3KeyMonthly=<path/to/lambda_calc_monthly.zip> \
    CodeS3KeyYearly=<path/to/lambda_calc_yearly.zip>
```

## API Lambda
Template: `infra/lambda-api.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-lambda-api \
  --template-file infra/lambda-api.yaml \
  --parameter-overrides \
    FunctionName=lambda_api_public \
    CodeS3Bucket=<bucket> \
    CodeS3Key=<path/to/lambda_api_public.zip> \
    TimestreamDatabase=uja_monitoring \
    TimestreamTable=telemetry_rt
```

## API Gateway + WAF
Template: `infra/api-gateway.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-api-gateway \
  --template-file infra/api-gateway.yaml \
  --parameter-overrides \
    ApiName=uja-public-api \
    StageName=v1 \
    LambdaName=lambda_api_public \
    DeploymentVersion=$(date +%s)
```
