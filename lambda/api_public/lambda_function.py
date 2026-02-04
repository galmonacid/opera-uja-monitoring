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

SERIES_INTERVAL_MINUTES = 15
SERIES_CONFIG = {
    "jaen": {
        "demand_rt_ids": [
            "uja.jaen.energia.consumo.edificio_a0.p_kw",
            "uja.jaen.energia.consumo.edificio_a1.p_kw",
            "uja.jaen.energia.consumo.edificio_a2.p_kw",
            "uja.jaen.energia.consumo.edificio_a3.p_kw",
            "uja.jaen.energia.consumo.edificio_a4.p_kw",
            "uja.jaen.energia.consumo.edificio_b1.p_kw",
            "uja.jaen.energia.consumo.edificio_b2.p_kw",
            "uja.jaen.energia.consumo.edificio_b3.p_kw",
            "uja.jaen.energia.consumo.edificio_b4.p_kw",
            "uja.jaen.energia.consumo.edificio_b5.p_kw",
            "uja.jaen.energia.consumo.edificio_c1.p_kw",
            "uja.jaen.energia.consumo.edificio_c2.p_kw",
            "uja.jaen.energia.consumo.edificio_c3.p_kw",
            "uja.jaen.energia.consumo.edificio_c5.p_kw",
            "uja.jaen.energia.consumo.edificio_c6.p_kw",
            "uja.jaen.energia.consumo.edificio_d1.p_kw",
            "uja.jaen.energia.consumo.edificio_d2.p_kw",
            "uja.jaen.energia.consumo.edificio_d3.p_kw",
            "uja.jaen.energia.consumo.edificio_d4.p_kw",
            "uja.jaen.energia.consumo.carga_vhe.p_kw",
        ],
        "pv_rt_ids": [
            "uja.jaen.fv.auto.edificio_a0.p_kw",
        ],
    }
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
        return response(get_series_24h(params))

    return response({"error": "not_found"}, status=404)


def get_realtime(params, multi_params):
    rt_ids = multi_params.get("rt_id") or []
    if not rt_ids and params.get("rt_id"):
        rt_ids = [params["rt_id"]]

    if rt_ids:
        items = batch_get_latest(rt_ids)
        return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}

    prefix = build_prefix(params.get("campus"), params.get("domain"))
    if not prefix:
        return {"error": "missing_filters"}

    items = scan_latest(prefix)
    return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}


def batch_get_latest(rt_ids):
    keys = [{"rt_id": rt_id} for rt_id in rt_ids]
    response = get_dynamodb().batch_get_item(
        RequestItems={DDB_LATEST_TABLE: {"Keys": keys}}
    )
    items = response.get("Responses", {}).get(DDB_LATEST_TABLE, [])
    return sorted([normalize_item(i) for i in items], key=lambda x: x["rt_id"])


def scan_latest(prefix):
    items = []
    last_key = None
    while True:
        kwargs = {"FilterExpression": Attr("rt_id").begins_with(prefix)}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_latest_table().scan(**kwargs)
        items.extend([normalize_item(i) for i in response.get("Items", [])])
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
    }


def get_series_24h(params):
    campus = params.get("campus", "jaen")
    config = SERIES_CONFIG.get(campus)
    if not config:
        return {"error": "unsupported_campus"}

    demand_series = query_timeseries(config["demand_rt_ids"])
    pv_series = query_timeseries(config["pv_rt_ids"])

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


def query_timeseries(rt_ids):
    if not rt_ids:
        return {}
    in_clause = ",".join([f"'{rt_id}'" for rt_id in rt_ids])
    query = f"""
SELECT bin(time, {SERIES_INTERVAL_MINUTES}m) AS ts,
       sum(measure_value::double) AS value
FROM "{TS_DATABASE}"."{TS_TABLE}"
WHERE time > ago(24h)
  AND measure_name = 'value'
  AND rt_id IN ({in_clause})
  AND measure_value::double <= {MAX_VALID_VALUE}
  AND measure_value::double >= {-MAX_VALID_VALUE}
GROUP BY bin(time, {SERIES_INTERVAL_MINUTES}m)
ORDER BY bin(time, {SERIES_INTERVAL_MINUTES}m)
"""
    rows = query_timestream(query)
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
