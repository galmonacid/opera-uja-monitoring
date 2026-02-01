# Infra

## IoT Core
IoT Things and certificates are managed manually and intentionally excluded from IaC.

## IoT Rule (gw_jaen_energia only)
Template: `infra/iot-rule-gw-jaen-energia.yaml`

### Deploy
```bash
aws cloudformation deploy \
  --stack-name uja-iot-rule-gw-jaen-energia \
  --template-file infra/iot-rule-gw-jaen-energia.yaml \
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
