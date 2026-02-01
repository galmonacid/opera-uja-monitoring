import json
import os

import boto3
from boto3.dynamodb.conditions import Attr, Key


DDB_LATEST_TABLE = os.getenv("DDB_LATEST_TABLE", "latest_readings")
DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")

dynamodb = boto3.resource("dynamodb")
latest_table = dynamodb.Table(DDB_LATEST_TABLE)
agg_table = dynamodb.Table(DDB_AGG_TABLE)


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
    response = dynamodb.batch_get_item(
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
        response = latest_table.scan(**kwargs)
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
        response = agg_table.query(**kwargs)
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
