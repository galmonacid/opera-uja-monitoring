import os
import time
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
DDB_CONFIG_TABLE = os.getenv("DDB_CONFIG_TABLE", "aggregation_configs")
CALC_VERSION = os.getenv("CALC_VERSION", "v1")

dynamodb = boto3.resource("dynamodb")
agg_table = dynamodb.Table(DDB_AGG_TABLE)
config_table = dynamodb.Table(DDB_CONFIG_TABLE)


def handler(event, context):
    target_year = event.get("year") if isinstance(event, dict) else None
    if not target_year:
        now = datetime.now(timezone.utc)
        target_year = f"{now.year}"

    totals = {}
    items = []
    configs = fetch_configs()
    if not configs:
        return {"status": "ignored", "reason": "no_configs"}

    for config in configs:
        totals.clear()
        pk_monthly = build_pk(config, "monthly")
        pk_yearly = build_pk(config, "yearly")
        for item in query_pk(pk_monthly):
            sk = item["sk"]
            if not sk.startswith(target_year):
                continue
            asset = sk.split("#", 1)[1]
            totals[asset] = totals.get(asset, 0.0) + float(item["value"])
        for asset, value in totals.items():
            items.append(build_item(pk_yearly, f"{target_year}#{asset}", value, config))

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
        response = config_table.scan(**kwargs)
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


def query_pk(pk):
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("pk").eq(pk)}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = agg_table.query(**kwargs)
        for item in response.get("Items", []):
            yield item
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break


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
    with agg_table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
