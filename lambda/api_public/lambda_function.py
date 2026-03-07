import json
import os
from datetime import datetime, timezone

import boto3
from boto3.dynamodb.conditions import Attr, Key


DDB_LATEST_TABLE = os.getenv("DDB_LATEST_TABLE", "latest_readings")
DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
MAX_VALID_VALUE = float(os.getenv("MAX_VALID_VALUE", "1000000"))

_dynamodb = None
_latest_table = None
_agg_table = None
_ts_query = None

SERIES_INTERVAL_MINUTES = 5
METRIC_SERIES_CONFIG = {
    ("jaen", "energia_consumo"): {
        "rt_prefix": "uja.jaen.energia.consumo.",
        "rt_like_patterns": ["%.p_kw"],
    },
    ("linares", "energia_consumo"): {
        "rt_prefix": "uja.linares.energia.consumo.",
        "rt_like_patterns": ["%.p_kw"],
    },
    ("jaen", "fv_endesa"): {
        "rt_prefix": "uja.jaen.fv.endesa.",
        "rt_like_patterns": ["%.p_ac_kw"],
    },
    ("linares", "fv_endesa"): {
        "rt_ids": ["uja.linares.fv.endesa.ct_total.p_kw"],
    },
    ("jaen", "fv_auto"): {
        "rt_ids": ["uja.jaen.fv.auto.ct_total.p_kw"],
    },
}

BALANCE_SERIES_CONFIG = {
    "jaen": {
        "demand_metric": "energia_consumo",
        "pv_metrics": ["fv_endesa", "fv_auto"],
    },
    "linares": {
        "demand_metric": "energia_consumo",
        "pv_metrics": ["fv_endesa"],
    },
}


def handler(event, context):
    path = event.get("path", "")
    if path.startswith("/v1/"):
        path = path[len("/v1") :]
    params = event.get("queryStringParameters") or {}
    multi_params = event.get("multiValueQueryStringParameters") or {}

    if path.endswith("/realtime"):
        return response(get_realtime(params, multi_params))
    if path.endswith("/aggregates/daily"):
        return response(get_aggregates(params, "daily"))
    if path.endswith("/aggregates/monthly"):
        return response(get_aggregates(params, "monthly"))
    if path.endswith("/aggregates/yearly"):
        return response(get_aggregates(params, "yearly"))
    if path.endswith("/series/24h"):
        if params.get("metric"):
            return response(get_series_24h_by_metric(params))
        if params.get("rt_prefix"):
            return response(get_series_24h_by_prefix(params))
        return response(get_series_24h(params))

    return response({"error": "not_found"}, status=404)


def get_realtime(params, multi_params):
    rt_ids = multi_params.get("rt_id") or []
    if not rt_ids and params.get("rt_id"):
        rt_ids = [params["rt_id"]]
    gateway_id = params.get("gateway_id")

    if rt_ids:
        items = batch_get_latest(rt_ids, gateway_id)
        return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}

    prefix = build_prefix(params.get("campus"), params.get("domain"))
    if not prefix:
        return {"error": "missing_filters"}

    items = scan_latest(prefix, gateway_id)
    return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}


def batch_get_latest(rt_ids, gateway_id=None):
    keys = [{"rt_id": rt_id} for rt_id in rt_ids]
    response = get_dynamodb().batch_get_item(
        RequestItems={DDB_LATEST_TABLE: {"Keys": keys}}
    )
    items = response.get("Responses", {}).get(DDB_LATEST_TABLE, [])
    normalized = [normalize_item(i) for i in items]
    if gateway_id:
        normalized = [item for item in normalized if item.get("gateway_id") == gateway_id]
    return sorted(normalized, key=lambda x: x["rt_id"])


def scan_latest(prefix, gateway_id=None):
    items = []
    last_key = None
    filter_expression = Attr("rt_id").begins_with(prefix)
    if gateway_id:
        filter_expression = filter_expression & Attr("gateway_id").eq(gateway_id)
    while True:
        kwargs = {"FilterExpression": filter_expression}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_latest_table().scan(**kwargs)
        normalized = [normalize_item(i) for i in response.get("Items", [])]
        if gateway_id:
            normalized = [item for item in normalized if item.get("gateway_id") == gateway_id]
        items.extend(normalized)
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return sorted(items, key=lambda x: x["rt_id"])


def build_prefix(campus, domain):
    if not campus and not domain:
        return None
    if campus and domain:
        return f"uja.{campus}.{domain}."
    if campus:
        return f"uja.{campus}."
    return f"uja..{domain}."


def get_aggregates(params, period):
    campus = params.get("campus")
    metric = params.get("metric")
    asset = params.get("asset", "total")

    if not campus or not metric:
        return {"error": "missing_params"}

    domain, system = metric_to_scope(metric)
    if not domain:
        return {"error": "unsupported_metric"}

    pk = f"{campus}#{domain}#{system}#{period}"
    items = query_pk(pk)

    series = []
    for item in items:
        sk = item["sk"]
        if not sk.endswith(f"#{asset}"):
            continue
        date = sk.split("#", 1)[0]
        series.append({"date": date, "value": float(item["value"])})

    series.sort(key=lambda x: x["date"])
    unit = items[0].get("unit") if items else "kWh"
    return {
        "campus": campus,
        "metric": metric,
        "period": period,
        "unit": unit,
        "series": series,
    }


def metric_to_scope(metric):
    mapping = {
        "energia_consumo": ("energia", "consumo"),
        "agua_consumo": ("agua", "consumo"),
        "fv_energia": ("fv", "total"),
        "fv_endesa": ("fv", "endesa"),
        "fv_auto": ("fv", "auto"),
        "co2_evitar": ("co2", "evitar"),
    }
    return mapping.get(metric, (None, None))


def query_pk(pk):
    items = []
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("pk").eq(pk)}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_agg_table().query(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return items


def normalize_item(item):
    return {
        "rt_id": item["rt_id"],
        "value": float(item["value"]),
        "unit": item.get("unit"),
        "ts_event": int(item.get("ts_event", 0)),
        "gateway_id": item.get("gateway_id"),
    }


def get_series_24h(params):
    campus = params.get("campus", "jaen")
    config = BALANCE_SERIES_CONFIG.get(campus)
    if not config:
        return {"error": "unsupported_campus"}

    demand_series = get_metric_series(campus, config["demand_metric"])
    pv_series = sum_series_maps(
        [get_metric_series(campus, metric) for metric in config["pv_metrics"]]
    )

    all_ts = sorted(set(demand_series) | set(pv_series))
    series = [
        {
            "ts": ts,
            "demand": float(demand_series.get(ts, 0.0)),
            "pv": float(pv_series.get(ts, 0.0)),
        }
        for ts in all_ts
    ]

    return {
        "campus": campus,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": "kW",
        "series": series,
    }


def get_series_24h_by_metric(params):
    campus = params.get("campus")
    metric = params.get("metric")
    if not campus or not metric:
        return {"error": "missing_params"}

    series_map = get_metric_series(campus, metric)
    if series_map is None:
        return {"error": "unsupported_metric"}

    rows = [
        {"ts": ts, "value": float(value)}
        for ts, value in sorted(series_map.items())
    ]
    return {
        "campus": campus,
        "metric": metric,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": "kW",
        "series": rows,
    }


def get_series_24h_by_prefix(params):
    rt_prefix = params.get("rt_prefix")
    if not rt_prefix:
        return {"error": "missing_params"}

    series = query_timeseries_by_prefix(rt_prefix)
    rows = [
        {"ts": ts, "value": float(value)}
        for ts, value in sorted(series.items())
    ]

    return {
        "rt_prefix": rt_prefix,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": "kW",
        "series": rows,
    }


def get_metric_series(campus, metric):
    config = METRIC_SERIES_CONFIG.get((campus, metric))
    if not config:
        return None
    if config.get("rt_ids"):
        return query_timeseries(config["rt_ids"])
    return query_timeseries_by_select(
        rt_prefix=config["rt_prefix"],
        rt_like_patterns=config.get("rt_like_patterns"),
    )


def sum_series_maps(series_maps):
    result = {}
    for series_map in series_maps:
        if not series_map:
            continue
        for ts, value in series_map.items():
            result[ts] = result.get(ts, 0.0) + value
    return result


def query_timeseries(rt_ids):
    return query_timeseries_by_select(rt_ids=rt_ids)


def query_timeseries_by_prefix(rt_prefix):
    return query_timeseries_by_select(
        rt_prefix=rt_prefix,
        rt_like_patterns=["%.p_%"],
    )


def query_timeseries_by_select(rt_ids=None, rt_prefix=None, rt_like_patterns=None):
    where_clauses = [
        "time > ago(24h)",
        "measure_name = 'value'",
    ]
    if rt_ids:
        in_clause = ",".join([f"'{rt_id}'" for rt_id in rt_ids])
        where_clauses.append(f"rt_id IN ({in_clause})")
    elif rt_prefix:
        where_clauses.append(f"rt_id LIKE '{rt_prefix}%'")
    else:
        return {}

    if rt_like_patterns:
        patterns = " OR ".join([f"rt_id LIKE '{pattern}'" for pattern in rt_like_patterns])
        where_clauses.append(f"({patterns})")

    where_clauses.append(f"measure_value::double <= {MAX_VALID_VALUE}")
    where_clauses.append(f"measure_value::double >= {-MAX_VALID_VALUE}")
    query = f"""
SELECT ts, sum(value) AS value
FROM (
  SELECT
    bin(time, {SERIES_INTERVAL_MINUTES}m) AS ts,
    rt_id,
    max_by(measure_value::double, time) AS value
  FROM "{TS_DATABASE}"."{TS_TABLE}"
  WHERE {" AND ".join(where_clauses)}
  GROUP BY rt_id, bin(time, {SERIES_INTERVAL_MINUTES}m)
)
GROUP BY ts
ORDER BY ts
"""
    return rows_to_series_map(query_timestream(query))


def rows_to_series_map(rows):
    result = {}
    for row in rows:
        data = row.get("Data", [])
        if len(data) < 2:
            continue
        ts_value = data[0].get("ScalarValue")
        value = data[1].get("ScalarValue")
        if ts_value is None or value is None:
            continue
        ts_epoch = parse_ts(ts_value)
        if ts_epoch == 0:
            continue
        result[ts_epoch] = float(value)
    return result


def get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        if region:
            _dynamodb = boto3.resource("dynamodb", region_name=region)
        else:
            _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


def get_latest_table():
    global _latest_table
    if _latest_table is None:
        _latest_table = get_dynamodb().Table(DDB_LATEST_TABLE)
    return _latest_table


def get_agg_table():
    global _agg_table
    if _agg_table is None:
        _agg_table = get_dynamodb().Table(DDB_AGG_TABLE)
    return _agg_table


def query_timestream(query):
    client = get_ts_query_client()
    rows = []
    next_token = None
    while True:
        args = {"QueryString": query}
        if next_token:
            args["NextToken"] = next_token
        response = client.query(**args)
        rows.extend(response.get("Rows", []))
        next_token = response.get("NextToken")
        if not next_token:
            break
    return rows


def get_ts_query_client():
    global _ts_query
    if _ts_query is None:
        _ts_query = boto3.client("timestream-query")
    return _ts_query


def parse_ts(ts_value):
    if not ts_value:
        return 0
    ts_value = ts_value.replace("T", " ")
    base = ts_value.split(".")[0]
    try:
        parsed = datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return 0
    return int(parsed.replace(tzinfo=timezone.utc).timestamp())


def response(payload, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(payload),
    }
