import argparse
import csv
import os

import boto3


REQUIRED_COLUMNS = {
    "config_id",
    "gateway_id",
    "rt_id_prefix",
    "campus",
    "domain",
    "system",
    "metric",
    "unit",
    "enabled",
}
OPTIONAL_COLUMNS = {
    "aggregation_mode",
    "counter_rt_id",
    "timezone",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load aggregation configs from CSV.")
    parser.add_argument("--file", required=True, help="CSV file path.")
    parser.add_argument(
        "--table",
        default="aggregation_configs",
        help="DynamoDB table name (default: aggregation_configs)",
    )
    parser.add_argument("--region", default=os.getenv("AWS_REGION"))
    return parser.parse_args()


def parse_enabled(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes"}


def main() -> None:
    args = parse_args()
    session = boto3.session.Session(region_name=args.region)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(args.table)

    with open(args.file, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            raise SystemExit(f"missing columns: {', '.join(sorted(missing))}")

        count = 0
        with table.batch_writer() as batch:
            for row in reader:
                if not row.get("config_id"):
                    continue
                item = {
                    "config_id": row["config_id"].strip(),
                    "gateway_id": row["gateway_id"].strip(),
                    "rt_id_prefix": row["rt_id_prefix"].strip(),
                    "campus": row["campus"].strip(),
                    "domain": row["domain"].strip(),
                    "system": row["system"].strip(),
                    "metric": row["metric"].strip(),
                    "unit": row["unit"].strip(),
                    "enabled": parse_enabled(row.get("enabled", "")),
                }
                notes = (row.get("notes") or "").strip()
                if notes:
                    item["notes"] = notes
                for key in sorted(OPTIONAL_COLUMNS):
                    value = (row.get(key) or "").strip()
                    if value:
                        item[key] = value
                batch.put_item(Item=item)
                count += 1

    print(f"loaded {count} rows into {args.table}")


if __name__ == "__main__":
    main()
