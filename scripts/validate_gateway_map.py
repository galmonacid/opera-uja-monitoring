import argparse
import csv
import sys


REQUIRED_COLUMNS = {"gateway_id", "source_key", "rt_id", "unit_expected", "enabled"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate gateway_variable_map CSV.")
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
            gateway_id = (row.get("gateway_id") or "").strip()
            source_key = (row.get("source_key") or "").strip()
            rt_id = (row.get("rt_id") or "").strip()
            if not gateway_id or not source_key or not rt_id:
                errors.append(f"row {idx}: gateway_id/source_key/rt_id cannot be empty")
                continue

            key = (gateway_id, source_key)
            if key in seen:
                errors.append(f"row {idx}: duplicate mapping for {gateway_id}::{source_key}")
            seen.add(key)

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: {args.csv_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
