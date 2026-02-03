# lambda_ingest_telemetry

## Environment
- `DDB_LATEST_TABLE` (default: `latest_readings`)
- `DDB_MAPPING_TABLE` (default: `gateway_variable_map`)
- `TS_DATABASE` (default: `uja_monitoring`)
- `TS_TABLE` (default: `telemetry_rt`)
- `DEFAULT_GATEWAY_ID` (optional)
- `LOG_LEVEL` (default: `INFO`)

## Notes
- Expects `meter.name` / `data.var` split as confirmed for `gw_jaen_energia`.
- Applies A0/C4/Magisterio sum rules and A3/B4 downstream adjustments before write.

<!-- noop change to trigger cd-backend -->
