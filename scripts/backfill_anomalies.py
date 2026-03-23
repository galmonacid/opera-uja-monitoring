import argparse

import boto3

from anomaly_policy import (
    build_anomaly_event_key,
    derive_rt_metadata,
    format_anomaly_value,
    sanitize_for_analytics,
)


def parse_args():
    parser = argparse.ArgumentParser(description="Backfill anomaly log from recent Timestream data.")
    parser.add_argument("--table", default="validation_anomalies", help="DynamoDB anomalies table.")
    parser.add_argument("--database", default="uja_monitoring", help="Timestream database.")
    parser.add_argument("--ts-table", default="telemetry_rt", help="Timestream table.")
    parser.add_argument("--lookback-hours", type=int, default=72, help="Hours to inspect.")
    parser.add_argument("--region", default=None, help="AWS region.")
    parser.add_argument("--limit", type=int, default=5000, help="Maximum rows to backfill.")
    return parser.parse_args()


def build_query(database, table, lookback_hours, limit):
    return f"""
SELECT
  time,
  rt_id,
  gateway_id,
  campus,
  domain,
  unit,
  measure_value::double AS value
FROM "{database}"."{table}"
WHERE measure_name = 'value'
  AND time > ago({lookback_hours}h)
  AND (measure_value::double < 0 OR measure_value::double > 1000000 OR measure_value::double < -1000000)
ORDER BY time DESC
LIMIT {int(limit)}
"""
def parse_row(row):
    data = row.get("Data", [])
    if len(data) < 7:
        return None
    return {
        "time": data[0].get("ScalarValue"),
        "rt_id": data[1].get("ScalarValue"),
        "gateway_id": data[2].get("ScalarValue"),
        "campus": data[3].get("ScalarValue"),
        "domain": data[4].get("ScalarValue"),
        "unit": data[5].get("ScalarValue"),
        "value": data[6].get("ScalarValue"),
    }


def parse_epoch_seconds(value):
    if not value:
        return 0
    normalized = value.replace("Z", "+00:00")
    from datetime import datetime

    return int(datetime.fromisoformat(normalized).timestamp())


def query_timestream(client, query):
    rows = []
    response = client.query(QueryString=query)
    rows.extend(response.get("Rows", []))
    while "NextToken" in response:
        response = client.query(QueryString=query, NextToken=response["NextToken"])
        rows.extend(response.get("Rows", []))
    return rows


def main():
    args = parse_args()
    session = boto3.session.Session(region_name=args.region)
    dynamodb = session.resource("dynamodb")
    ts_query = session.client("timestream-query")
    table = dynamodb.Table(args.table)

    query = build_query(args.database, args.ts_table, args.lookback_hours, args.limit)
    rows = query_timestream(ts_query, query)

    count = 0
    with table.batch_writer() as batch:
        for row in rows:
            parsed = parse_row(row)
            if not parsed or not parsed["rt_id"] or not parsed["gateway_id"]:
                continue
            valid, applied_value, anomaly = sanitize_for_analytics(
                parsed["rt_id"],
                parsed["value"],
                unit=parsed["unit"],
            )
            if not anomaly:
                continue
            metadata = derive_rt_metadata(parsed["rt_id"])
            ts_event = parse_epoch_seconds(parsed["time"])
            batch.put_item(
                Item={
                    "gateway_id": parsed["gateway_id"],
                    "event_key": build_anomaly_event_key(ts_event, parsed["rt_id"], anomaly["anomaly_type"]),
                    "campus_domain": f"{metadata['campus']}#{metadata['domain']}",
                    "campus": metadata["campus"],
                    "domain": metadata["domain"],
                    "rt_id": parsed["rt_id"],
                    "unit": parsed["unit"] or "",
                    "raw_value": format_anomaly_value(parsed["value"]),
                    "applied_value": format_anomaly_value(applied_value),
                    "anomaly_type": anomaly["anomaly_type"],
                    "reason": anomaly["reason"],
                    "threshold": format_anomaly_value(anomaly.get("threshold")),
                    "ts_event": ts_event,
                    "detected_by": "backfill",
                }
            )
            count += 1

    print(f"backfilled {count} anomalies into {args.table}")


if __name__ == "__main__":
    main()
