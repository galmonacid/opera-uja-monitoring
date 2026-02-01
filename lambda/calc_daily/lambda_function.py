import os
import time
from datetime import datetime, timedelta, timezone
from decimal import Decimal

import boto3
from boto3.dynamodb.conditions import Key


DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
DDB_MAPPING_TABLE = os.getenv("DDB_MAPPING_TABLE", "gateway_variable_map")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
GATEWAY_ID = os.getenv("GATEWAY_ID", "gw_jaen_energia")
RT_ID_PREFIX = os.getenv("RT_ID_PREFIX", "uja.jaen.energia.consumo.")
CALC_VERSION = os.getenv("CALC_VERSION", "v1")

dynamodb = boto3.resource("dynamodb")
ts_query = boto3.client("timestream-query")

agg_table = dynamodb.Table(DDB_AGG_TABLE)
mapping_table = dynamodb.Table(DDB_MAPPING_TABLE)


def handler(event, context):
    target_date = event.get("date") if isinstance(event, dict) else None
    if not target_date:
        target_date = (datetime.now(timezone.utc) - timedelta(days=1)).strftime("%Y-%m-%d")

    start = f"{target_date}T00:00:00Z"
    end = f"{target_date}T23:59:59Z"

    rt_ids = fetch_rt_ids()
    if not rt_ids:
        return {"status": "ignored", "reason": "no_rt_ids"}

    campus = "jaen"
    pk = f"{campus}#energia#consumo#daily"
    items = []
    total = 0.0

    for rt_id in rt_ids:
        energy_kwh = integrate_energy(rt_id, start, end)
        if energy_kwh is None:
            continue
        asset = rt_id.split(".")[4]
        items.append(build_item(pk, f"{target_date}#{asset}", energy_kwh))
        total += energy_kwh

    items.append(build_item(pk, f"{target_date}#total", total))
    write_items(items)

    return {"status": "ok", "count": len(items)}


def fetch_rt_ids():
    rt_ids = []
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("gateway_id").eq(GATEWAY_ID)}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = mapping_table.query(**kwargs)
        for item in response.get("Items", []):
            rt_id = item.get("rt_id")
            if rt_id and rt_id.startswith(RT_ID_PREFIX):
                rt_ids.append(rt_id)
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return sorted(set(rt_ids))


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
    response = ts_query.query(QueryString=query)
    rows.extend(parse_rows(response))
    while "NextToken" in response:
        response = ts_query.query(QueryString=query, NextToken=response["NextToken"])
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
