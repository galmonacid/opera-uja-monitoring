import os
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
DDB_MAPPING_TABLE = os.getenv("DDB_MAPPING_TABLE", "gateway_variable_map")
DDB_CONFIG_TABLE = os.getenv("DDB_CONFIG_TABLE", "aggregation_configs")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
CALC_VERSION = os.getenv("CALC_VERSION", "v1")

_dynamodb = None
_ts_query = None
_agg_table = None
_mapping_table = None
_config_table = None


def _get_region():
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")


def get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        region = _get_region()
        if region:
            _dynamodb = boto3.resource("dynamodb", region_name=region)
        else:
            _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


def get_ts_query():
    global _ts_query
    if _ts_query is None:
        region = _get_region()
        if region:
            _ts_query = boto3.client("timestream-query", region_name=region)
        else:
            _ts_query = boto3.client("timestream-query")
    return _ts_query


def get_agg_table():
    global _agg_table
    if _agg_table is None:
        _agg_table = get_dynamodb().Table(DDB_AGG_TABLE)
    return _agg_table


def get_mapping_table():
    global _mapping_table
    if _mapping_table is None:
        _mapping_table = get_dynamodb().Table(DDB_MAPPING_TABLE)
    return _mapping_table


def get_config_table():
    global _config_table
    if _config_table is None:
        _config_table = get_dynamodb().Table(DDB_CONFIG_TABLE)
    return _config_table


def handler(event, context):
    target_date = event.get("date") if isinstance(event, dict) else None
    if not target_date:
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    start = f"{target_date}T00:00:00Z"
    end = f"{target_date}T23:59:59Z"

    items = []
    configs = fetch_configs()
    if not configs:
        return {"status": "ignored", "reason": "no_configs"}

    for config in configs:
        rt_ids = fetch_rt_ids(config)
        if not rt_ids:
            continue
        pk = build_pk(config, "daily")
        total = 0.0
        for rt_id in rt_ids:
            energy_kwh = integrate_energy(rt_id, start, end)
            if energy_kwh is None:
                continue
            asset = get_asset_name(rt_id)
            items.append(build_item(pk, f"{target_date}#{asset}", energy_kwh, config))
            if should_include_in_total(config, rt_id):
                total += energy_kwh
        items.append(build_item(pk, f"{target_date}#total", total, config))

    if not items:
        return {"status": "ignored", "reason": "no_items"}

    write_items(items)
    return {"status": "ok", "count": len(items)}


def fetch_configs():
    items = []
    last_key = None
    while True:
        kwargs = {}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_config_table().scan(**kwargs)
        for item in response.get("Items", []):
            if item.get("enabled") is False:
                continue
            if item.get("enabled") is None:
                continue
            items.append(normalize_config(item))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return items


def normalize_config(item):
    return {
        "config_id": item.get("config_id"),
        "gateway_id": item.get("gateway_id"),
        "rt_id_prefix": item.get("rt_id_prefix"),
        "campus": item.get("campus"),
        "domain": item.get("domain"),
        "system": item.get("system"),
        "metric": item.get("metric"),
        "unit": item.get("unit", "kWh"),
    }


def build_pk(config, period):
    return f"{config['campus']}#{config['domain']}#{config['system']}#{period}"


def fetch_rt_ids(config):
    rt_ids = []
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("gateway_id").eq(config["gateway_id"])}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_mapping_table().query(**kwargs)
        for item in response.get("Items", []):
            rt_id = item.get("rt_id")
            if rt_id and rt_id.startswith(config["rt_id_prefix"]) and is_power_rt_id(rt_id):
                rt_ids.append(rt_id)
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return sorted(set(rt_ids))


def is_power_rt_id(rt_id: str) -> bool:
    return rt_id.endswith(".p_kw") or rt_id.endswith(".p_ac_kw")


def get_asset_name(rt_id: str) -> str:
    return rt_id.split(".")[4]


def should_include_in_total(config, rt_id: str) -> bool:
    metric = config.get("metric")
    campus = config.get("campus")
    if metric == "fv_auto" and campus == "jaen":
        return rt_id.endswith("ct_total.p_kw")
    if metric == "fv_endesa" and campus == "jaen":
        return rt_id.endswith(".p_ac_kw")
    if metric == "fv_endesa" and campus == "linares":
        return rt_id.endswith("ct_total.p_kw")
    return is_power_rt_id(rt_id)


def integrate_energy(rt_id, start, end):
    rows = query_timestream(rt_id, start, end)
    if len(rows) < 2:
        return None

    total_kwh = 0.0
    for prev, curr in zip(rows, rows[1:]):
        t0, v0 = prev
        t1, v1 = curr
        dt_hours = (t1 - t0).total_seconds() / 3600.0
        total_kwh += (v0 + v1) / 2.0 * dt_hours
    return total_kwh


def query_timestream(rt_id, start, end):
    query = (
        f"SELECT time, measure_value::double AS value "
        f"FROM \"{TS_DATABASE}\".\"{TS_TABLE}\" "
        f"WHERE \"rt_id\" = '{rt_id}' "
        f"AND time BETWEEN from_iso8601_timestamp('{start}') "
        f"AND from_iso8601_timestamp('{end}') "
        f"ORDER BY time ASC"
    )
    rows = []
    response = get_ts_query().query(QueryString=query)
    rows.extend(parse_rows(response))
    while "NextToken" in response:
        response = get_ts_query().query(QueryString=query, NextToken=response["NextToken"])
        rows.extend(parse_rows(response))
    return rows


def parse_rows(response):
    rows = []
    for row in response.get("Rows", []):
        data = row["Data"]
        ts = parse_time(data[0]["ScalarValue"])
        value = float(data[1]["ScalarValue"])
        rows.append((ts, value))
    return rows


def parse_time(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def build_item(pk, sk, value, config):
    return {
        "pk": pk,
        "sk": sk,
        "value": Decimal(f"{value:.6f}"),
        "unit": config.get("unit", "kWh"),
        "ts_calculated": int(time.time()),
        "calc_version": CALC_VERSION,
        "gateway_id": config.get("gateway_id"),
    }


def write_items(items):
    with get_agg_table().batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
