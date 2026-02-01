import argparse
import csv
from typing import Dict

import boto3


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Load gateway_variable_map from CSV.")
    parser.add_argument(
        "--file",
        required=True,
        help="CSV file path (e.g. seeds/gateway_variable_map_gw_jaen_energia.csv)",
    )
    parser.add_argument(
        "--table",
        default="gateway_variable_map",
        help="DynamoDB table name (default: gateway_variable_map)",
    )
    parser.add_argument(
        "--region",
        default=None,
        help="AWS region (optional; uses default if omitted)",
    )
    return parser.parse_args()


def to_bool(value: str) -> bool:
    return str(value).strip().lower() in {"true", "1", "yes", "y"}


def build_item(row: Dict[str, str]) -> Dict[str, object]:
    item = {
        "gateway_id": row["gateway_id"].strip(),
        "source_key": row["source_key"].strip(),
        "rt_id": row["rt_id"].strip(),
        "unit_expected": row.get("unit_expected", "").strip() or None,
        "enabled": to_bool(row.get("enabled", "true")),
    }
    notes = row.get("notes", "").strip()
    if notes:
        item["notes"] = notes
    return item


def main() -> None:
    args = parse_args()
    session = boto3.session.Session(region_name=args.region)
    dynamodb = session.resource("dynamodb")
    table = dynamodb.Table(args.table)

    count = 0
    with open(args.file, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        with table.batch_writer() as batch:
            for row in reader:
                item = build_item(row)
                batch.put_item(Item=item)
                count += 1

    print(f"loaded {count} rows into {args.table}")


if __name__ == "__main__":
    main()
