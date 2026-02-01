import os
import time
from datetime import datetime, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
CALC_VERSION = os.getenv("CALC_VERSION", "v1")

dynamodb = boto3.resource("dynamodb")
agg_table = dynamodb.Table(DDB_AGG_TABLE)


def handler(event, context):
    target_month = event.get("month") if isinstance(event, dict) else None
    if not target_month:
        now = datetime.now(timezone.utc)
        target_month = f"{now.year}-{now.month:02d}"

    campus = "jaen"
    pk_daily = f"{campus}#energia#consumo#daily"
    pk_monthly = f"{campus}#energia#consumo#monthly"

    totals = {}
    for item in query_pk(pk_daily):
        sk = item["sk"]
        if not sk.startswith(target_month):
            continue
        asset = sk.split("#", 1)[1]
        totals[asset] = totals.get(asset, 0.0) + float(item["value"])

    items = []
    for asset, value in totals.items():
        items.append(build_item(pk_monthly, f"{target_month}#{asset}", value))

    write_items(items)
    return {"status": "ok", "count": len(items)}


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


def build_item(pk, sk, value):
    return {
        "pk": pk,
        "sk": sk,
        "value": Decimal(f"{value:.6f}"),
        "unit": "kWh",
        "ts_calculated": int(time.time()),
        "calc_version": CALC_VERSION,
    }


def write_items(items):
    with agg_table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=item)
