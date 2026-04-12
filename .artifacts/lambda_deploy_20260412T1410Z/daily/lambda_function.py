import os
import sys
import time
import logging
from datetime import datetime, time as dt_time, timedelta, timezone
from decimal import Decimal
from pathlib import Path
from zoneinfo import ZoneInfo

import boto3
from boto3.dynamodb.conditions import Key
try:
    from anomaly_policy import (
        build_anomaly_event_key,
        derive_rt_metadata,
        format_anomaly_value,
        sanitize_for_analytics,
        should_exclude_anomalous_sample,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from anomaly_policy import (
        build_anomaly_event_key,
        derive_rt_metadata,
        format_anomaly_value,
        sanitize_for_analytics,
        should_exclude_anomalous_sample,
    )


DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
DDB_MAPPING_TABLE = os.getenv("DDB_MAPPING_TABLE", "gateway_variable_map")
DDB_CONFIG_TABLE = os.getenv("DDB_CONFIG_TABLE", "aggregation_configs")
DDB_ANOMALIES_TABLE = os.getenv("DDB_ANOMALIES_TABLE", "validation_anomalies")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
MAX_VALID_VALUE = float(os.getenv("MAX_VALID_VALUE", "1000000"))
MAX_VALID_VALUE_KWH = float(os.getenv("MAX_VALID_VALUE_KWH", "1000000000"))
CALC_VERSION = os.getenv("CALC_VERSION", "v1")
COUNTER_RESET_NEGATIVE_THRESHOLD = float(os.getenv("COUNTER_RESET_NEGATIVE_THRESHOLD", "0"))

_dynamodb = None
_ts_query = None
_agg_table = None
_mapping_table = None
_config_table = None
_anomalies_table = None
_logger = logging.getLogger(__name__)
LOCAL_TIMEZONE_NAME = os.getenv("LOCAL_TIMEZONE", "Europe/Madrid")
LOCAL_TIMEZONE = ZoneInfo(LOCAL_TIMEZONE_NAME)

FV_COUNTER_RT_IDS = {
    ("jaen", "fv_endesa"): "uja.jaen.fv.endesa.ct_total.e_kwh",
    ("linares", "fv_endesa"): "uja.linares.fv.endesa.ct_total.e_kwh",
    ("jaen", "fv_auto"): "uja.jaen.fv.auto.ct_total.e_kwh",
}


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


def get_anomalies_table():
    global _anomalies_table
    if _anomalies_table is None:
        _anomalies_table = get_dynamodb().Table(DDB_ANOMALIES_TABLE)
    return _anomalies_table


def handler(event, context):
    window = resolve_daily_window(event)
    target_date = window["key"]
    start = window["start_utc"].isoformat()
    end = window["end_utc"].isoformat()

    configs = fetch_configs()
    if not configs:
        return {"status": "ignored", "reason": "no_configs"}

    total_items = 0
    errors = []
    for config in configs:
        config_started_at = time.perf_counter()
        try:
            rt_ids = fetch_rt_ids(config)
            if not rt_ids:
                _logger.info(
                    "calc_daily skipped config_id=%s target_date=%s reason=no_rt_ids",
                    config.get("config_id"),
                    target_date,
                )
                continue
            pk = build_pk(config, "daily")
            items = []
            total = 0.0
            for rt_id in rt_ids:
                value = calculate_daily_value(config, rt_id, start, end)
                if value is None:
                    continue
                asset = get_asset_name(rt_id)
                items.append(build_item(pk, f"{target_date}#{asset}", value, config))
                if should_include_in_total(config, rt_id):
                    total += value
            if not items:
                _logger.info(
                    "calc_daily skipped config_id=%s target_date=%s reason=no_values",
                    config.get("config_id"),
                    target_date,
                )
                continue
            items.append(build_item(pk, f"{target_date}#total", total, config))
            write_items(items)
            total_items += len(items)
            _logger.info(
                "calc_daily wrote config_id=%s target_date=%s items=%s duration_ms=%s",
                config.get("config_id"),
                target_date,
                len(items),
                round((time.perf_counter() - config_started_at) * 1000),
            )
        except Exception as exc:
            _logger.exception(
                "calc_daily failed config_id=%s target_date=%s error=%s",
                config.get("config_id"),
                target_date,
                exc,
            )
            errors.append(
                {
                    "config_id": config.get("config_id"),
                    "error": str(exc),
                }
            )

    if not total_items:
        if errors:
            return {"status": "error", "count": 0, "errors": errors}
        return {"status": "ignored", "reason": "no_items"}

    return {
        "status": "partial" if errors else "ok",
        "count": total_items,
        "errors": errors,
    }


def resolve_daily_window(event):
    target_date = event.get("date") if isinstance(event, dict) else None
    return closed_daily_window_utc(target_date=target_date)


def closed_daily_window_utc(target_date=None, now=None):
    now_utc = ensure_utc_datetime(now)
    local_now = now_utc.astimezone(LOCAL_TIMEZONE)
    if target_date:
        resolved_date = datetime.fromisoformat(str(target_date)).date()
    else:
        resolved_date = local_now.date() - timedelta(days=1)
    start_local = datetime.combine(resolved_date, dt_time.min, tzinfo=LOCAL_TIMEZONE)
    end_local = start_local + timedelta(days=1)
    return {
        "period": "daily",
        "key": resolved_date.isoformat(),
        "start_utc": start_local.astimezone(timezone.utc),
        "end_utc": end_local.astimezone(timezone.utc),
        "timezone": LOCAL_TIMEZONE_NAME,
    }


def ensure_utc_datetime(value=None):
    if value is None:
        return datetime.now(timezone.utc)
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


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
        "aggregation_mode": item.get("aggregation_mode"),
        "counter_rt_id": item.get("counter_rt_id"),
        "timezone": item.get("timezone"),
    }


def build_pk(config, period):
    return f"{config['campus']}#{config['domain']}#{config['system']}#{period}"


def fetch_rt_ids(config):
    configured_counter_rt_id = resolve_counter_rt_id(config)
    if configured_counter_rt_id:
        return [configured_counter_rt_id]

    rt_ids = []
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("gateway_id").eq(config["gateway_id"])}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_mapping_table().query(**kwargs)
        for item in response.get("Items", []):
            rt_id = item.get("rt_id")
            if rt_id and rt_id.startswith(config["rt_id_prefix"]) and is_supported_rt_id(config, rt_id):
                rt_ids.append(rt_id)
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return sorted(set(rt_ids))


def is_power_rt_id(rt_id: str) -> bool:
    return rt_id.endswith(".p_kw") or rt_id.endswith(".p_ac_kw")


def is_water_rt_id(rt_id: str) -> bool:
    return rt_id.endswith(".v_m3")


def is_supported_rt_id(config, rt_id: str) -> bool:
    if config.get("metric") == "agua_consumo":
        return is_water_rt_id(rt_id)
    return is_power_rt_id(rt_id)


def resolve_counter_rt_id(config):
    explicit_rt_id = config.get("counter_rt_id")
    if explicit_rt_id:
        return explicit_rt_id
    if resolve_aggregation_mode(config) != "counter_delta":
        return None
    return FV_COUNTER_RT_IDS.get((config.get("campus"), config.get("metric")))


def resolve_aggregation_mode(config):
    if config.get("aggregation_mode"):
        return config["aggregation_mode"]
    if config.get("metric") == "agua_consumo":
        return "counter_delta"
    if (config.get("campus"), config.get("metric")) in FV_COUNTER_RT_IDS:
        return "counter_delta"
    return "power_integration"


def get_asset_name(rt_id: str) -> str:
    return rt_id.split(".")[4]


def should_include_in_total(config, rt_id: str) -> bool:
    metric = config.get("metric")
    campus = config.get("campus")
    if resolve_aggregation_mode(config) == "counter_delta":
        counter_rt_id = resolve_counter_rt_id(config)
        return counter_rt_id is None or rt_id == counter_rt_id
    if metric == "agua_consumo":
        return is_water_rt_id(rt_id)
    if metric == "fv_auto" and campus == "jaen":
        return rt_id.endswith("ct_total.p_kw")
    if metric == "fv_endesa" and campus == "jaen":
        return rt_id.endswith(".p_ac_kw")
    if metric == "fv_endesa" and campus == "linares":
        return rt_id.endswith("ct_total.p_kw")
    return is_power_rt_id(rt_id)


def calculate_daily_value(config, rt_id, start, end):
    if config.get("metric") == "agua_consumo":
        return calculate_counter_consumption(config, rt_id, start, end)
    if resolve_aggregation_mode(config) == "counter_delta":
        return calculate_counter_delta(rt_id, start, end)
    return integrate_energy(rt_id, start, end)


def calculate_counter_delta(rt_id, start, end):
    start_sample = query_latest_valid_sample(rt_id, start, operator="<=")
    end_sample = query_latest_valid_sample(rt_id, end, operator="<")
    if not start_sample or not end_sample:
        return None
    _start_ts, start_value = start_sample
    _end_ts, end_value = end_sample
    return max(end_value - start_value, 0.0)


def query_latest_valid_sample(rt_id, boundary, operator="<="):
    query = (
        f"SELECT time, measure_value::double AS value "
        f"FROM \"{TS_DATABASE}\".\"{TS_TABLE}\" "
        f"WHERE \"rt_id\" = '{rt_id}' "
        f"AND time {operator} from_iso8601_timestamp('{boundary}') "
        f"ORDER BY time DESC "
        f"LIMIT 25"
    )
    response = get_ts_query().query(QueryString=query)
    rows = parse_rows(response)
    while "NextToken" in response:
        response = get_ts_query().query(QueryString=query, NextToken=response["NextToken"])
        rows.extend(parse_rows(response))
    for ts, value in rows:
        valid, applied_value, _anomaly = sanitize_for_analytics(
            rt_id,
            value,
            unit=infer_rt_unit(rt_id),
            max_valid_value=MAX_VALID_VALUE,
            max_valid_value_kwh=MAX_VALID_VALUE_KWH,
        )
        if not valid:
            continue
        return (ts, applied_value)
    return None


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


def calculate_counter_consumption(config, rt_id, start, end):
    rows = query_timestream(rt_id, start, end)
    if len(rows) < 2:
        return None

    total_consumption = 0.0
    anomalies = []
    threshold = max(COUNTER_RESET_NEGATIVE_THRESHOLD, 0.0)

    for prev, curr in zip(rows, rows[1:]):
        prev_ts, prev_value = prev
        curr_ts, curr_value = curr
        delta = curr_value - prev_value
        if delta >= 0:
            total_consumption += delta
            continue
        if abs(delta) >= threshold:
            anomalies.append(
                build_counter_reset_anomaly_event(
                    config=config,
                    rt_id=rt_id,
                    ts_event=int(curr_ts.timestamp()),
                    previous_value=prev_value,
                    current_value=curr_value,
                    delta=delta,
                    threshold=threshold,
                )
            )

    write_validation_anomalies(anomalies)
    return total_consumption


def build_counter_reset_anomaly_event(
    config,
    rt_id,
    ts_event,
    previous_value,
    current_value,
    delta,
    threshold,
):
    metadata = derive_rt_metadata(rt_id)
    anomaly_type = "counter_reset_detected"
    return {
        "gateway_id": config.get("gateway_id"),
        "event_key": build_anomaly_event_key(ts_event, rt_id, anomaly_type),
        "campus_domain": f"{metadata['campus']}#{metadata['domain']}",
        "campus": metadata["campus"],
        "domain": metadata["domain"],
        "rt_id": rt_id,
        "unit": infer_rt_unit(rt_id) or "",
        "raw_value": format_anomaly_value(current_value),
        "applied_value": format_anomaly_value(previous_value),
        "anomaly_type": anomaly_type,
        "reason": (
            "negative_delta_detected_between_samples; "
            f"delta={delta:.6f}; threshold={threshold:.6f}"
        ),
        "threshold": format_anomaly_value(threshold),
        "ts_event": int(ts_event),
        "detected_by": "calc_daily",
        "updated_at": int(time.time()),
    }


def build_anomaly_event_key_prefix(ts_epoch):
    return f"{int(ts_epoch):013d}#"


def query_anomaly_timestamps(rt_id, start, end):
    metadata = derive_rt_metadata(rt_id)
    start_ts = int(parse_time(start).timestamp())
    end_ts = int(parse_time(end).timestamp())
    items = []
    last_key = None
    min_event_key = build_anomaly_event_key_prefix(start_ts)
    max_event_key = f"{build_anomaly_event_key_prefix(end_ts)}\uffff"
    while True:
        kwargs = {
            "IndexName": "campus_domain_event_key",
            "KeyConditionExpression": Key("campus_domain").eq(
                f"{metadata['campus']}#{metadata['domain']}"
            ) & Key("event_key").between(min_event_key, max_event_key),
        }
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_anomalies_table().query(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break

    timestamps = set()
    for item in items:
        if item.get("rt_id") != rt_id:
            continue
        if not should_exclude_anomalous_sample(rt_id, item.get("anomaly_type")):
            continue
        ts_event = int(item.get("ts_event", 0))
        if start_ts <= ts_event <= end_ts:
            timestamps.add(ts_event)
    return timestamps


def query_timestream(rt_id, start, end):
    anomaly_timestamps = query_anomaly_timestamps(rt_id, start, end)
    query = (
        f"SELECT time, measure_value::double AS value "
        f"FROM \"{TS_DATABASE}\".\"{TS_TABLE}\" "
        f"WHERE \"rt_id\" = '{rt_id}' "
        f"AND time >= from_iso8601_timestamp('{start}') "
        f"AND time < from_iso8601_timestamp('{end}') "
        f"ORDER BY time ASC"
    )
    rows = []
    response = get_ts_query().query(QueryString=query)
    rows.extend(parse_rows(response))
    while "NextToken" in response:
        response = get_ts_query().query(QueryString=query, NextToken=response["NextToken"])
        rows.extend(parse_rows(response))
    normalized_rows = []
    for ts, value in rows:
        if int(ts.timestamp()) in anomaly_timestamps:
            continue
        valid, applied_value, _anomaly = sanitize_for_analytics(
            rt_id,
            value,
            unit=infer_rt_unit(rt_id),
            max_valid_value=MAX_VALID_VALUE,
            max_valid_value_kwh=MAX_VALID_VALUE_KWH,
        )
        if not valid:
            continue
        normalized_rows.append((ts, applied_value))
    return normalized_rows


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


def infer_rt_unit(rt_id):
    if rt_id.endswith(".v_m3"):
        return "m3"
    if rt_id.endswith(".e_kwh"):
        return "kWh"
    if rt_id.endswith(".g_wm2"):
        return "W/m²"
    if rt_id.endswith(".t_c"):
        return "°C"
    return "kW"


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


def write_validation_anomalies(events):
    if not events:
        return

    seen = set()
    with get_anomalies_table().batch_writer() as batch:
        for event in events:
            dedupe_key = (event.get("gateway_id"), event.get("event_key"))
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            batch.put_item(Item=event)


def write_items(items):
    with get_agg_table().batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
