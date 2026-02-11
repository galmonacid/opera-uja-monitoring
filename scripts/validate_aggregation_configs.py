import argparse
import csv
import sys


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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate aggregation configs CSV.")
    parser.add_argument("csv_path", help="Path to the CSV file to validate.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors = []
    seen = set()

    with open(args.csv_path, "r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = REQUIRED_COLUMNS - set(reader.fieldnames or [])
        if missing:
            errors.append(f"missing columns: {', '.join(sorted(missing))}")

        for idx, row in enumerate(reader, start=2):
            config_id = (row.get("config_id") or "").strip()
            gateway_id = (row.get("gateway_id") or "").strip()
            rt_id_prefix = (row.get("rt_id_prefix") or "").strip()
            campus = (row.get("campus") or "").strip()
            domain = (row.get("domain") or "").strip()
            system = (row.get("system") or "").strip()
            metric = (row.get("metric") or "").strip()
            unit = (row.get("unit") or "").strip()
            if not all([config_id, gateway_id, rt_id_prefix, campus, domain, system, metric, unit]):
                errors.append(f"row {idx}: missing required values")
                continue

            if config_id in seen:
                errors.append(f"row {idx}: duplicate config_id {config_id}")
            seen.add(config_id)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
