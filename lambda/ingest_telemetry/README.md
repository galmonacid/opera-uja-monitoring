# lambda_ingest_telemetry

## Environment
- `DDB_LATEST_TABLE` (default: `latest_readings`)
- `DDB_MAPPING_TABLE` (default: `gateway_variable_map`)
- `TS_DATABASE` (default: `uja_monitoring`)
- `TS_TABLE` (default: `telemetry_rt`)
- `DEFAULT_GATEWAY_ID` (optional)
- `LOG_LEVEL` (default: `INFO`)
- `MAX_VALID_VALUE` (default: `1000000`)
- `MAX_VALID_VALUE_KWH` (default: `1000000000`)

## Notes
- Expects `meter.name` / `data.var` split as confirmed for `gw_jaen_energia`.
- Applies A0/C4/Magisterio sum rules and A3/B4 downstream adjustments before write.
- If a payload includes multiple `meter[]` entries with different `time` values, all are written to Timestream and only the latest per `rt_id` is kept in DynamoDB.

<!-- noop change to trigger cd-backend -->
