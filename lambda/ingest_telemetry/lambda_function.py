import json
import logging
import math
import os
import sys
import time
from decimal import Decimal
from pathlib import Path

import boto3
from boto3.dynamodb.types import TypeDeserializer, TypeSerializer
from botocore.exceptions import ClientError
try:
    from anomaly_policy import (
        build_anomaly_event_key,
        derive_rt_metadata,
        detect_anomaly,
        format_anomaly_value,
        normalize_sentinel_value,
        threshold_for_unit,
    )
except ModuleNotFoundError:
    sys.path.append(str(Path(__file__).resolve().parents[2]))
    from anomaly_policy import (
        build_anomaly_event_key,
        derive_rt_metadata,
        detect_anomaly,
        format_anomaly_value,
        normalize_sentinel_value,
        threshold_for_unit,
    )

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

DDB_LATEST_TABLE = os.getenv("DDB_LATEST_TABLE", "latest_readings")
DDB_MAPPING_TABLE = os.getenv("DDB_MAPPING_TABLE", "gateway_variable_map")
DDB_ANOMALIES_TABLE = os.getenv("DDB_ANOMALIES_TABLE", "validation_anomalies")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
DEFAULT_GATEWAY_ID = os.getenv("DEFAULT_GATEWAY_ID")
LOG_SAMPLE_LIMIT = int(os.getenv("LOG_SAMPLE_LIMIT", "10"))
MAX_VALID_VALUE = float(os.getenv("MAX_VALID_VALUE", "1000000"))
MAX_VALID_VALUE_KWH = float(os.getenv("MAX_VALID_VALUE_KWH", "1000000000"))

serializer = TypeSerializer()
deserializer = TypeDeserializer()
_dynamodb = None
_ddb_client = None
_timestream = None
_latest_table = None
_anomalies_table = None


def _get_region():
    return os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")


def _get_dynamodb_resource():
    global _dynamodb
    if _dynamodb is None:
        region = _get_region()
        if region:
            _dynamodb = boto3.resource("dynamodb", region_name=region)
        else:
            _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


def _get_ddb_client():
    global _ddb_client
    if _ddb_client is None:
        region = _get_region()
        if region:
            _ddb_client = boto3.client("dynamodb", region_name=region)
        else:
            _ddb_client = boto3.client("dynamodb")
    return _ddb_client


def _get_timestream_client():
    global _timestream
    if _timestream is None:
        region = _get_region()
        if region:
            _timestream = boto3.client("timestream-write", region_name=region)
        else:
            _timestream = boto3.client("timestream-write")
    return _timestream


def _get_latest_table():
    global _latest_table
    if _latest_table is None:
        _latest_table = _get_dynamodb_resource().Table(DDB_LATEST_TABLE)
    return _latest_table


def _get_anomalies_table():
    global _anomalies_table
    if _anomalies_table is None:
        _anomalies_table = _get_dynamodb_resource().Table(DDB_ANOMALIES_TABLE)
    return _anomalies_table


def handler(event, context):
    payload = extract_payload(event)
    if not payload:
        logger.warning("payload missing or invalid")
        return {"status": "ignored", "reason": "invalid_payload"}

    gateway_id = get_gateway_id(event, payload)
    if not gateway_id:
        logger.error("gateway_id not found")
        return {"status": "ignored", "reason": "missing_gateway_id"}

    measurements, raw_values_by_ts = extract_measurements(payload)
    if not measurements:
        logger.warning("no measurements found")
        return {"status": "ignored", "reason": "no_measurements"}

    source_keys = sorted({m["source_key"] for m in measurements})
    mappings = fetch_mappings(gateway_id, source_keys)
    logger.info(
        "ingest metrics: gateway=%s measurements=%d unique_keys=%d mappings=%d",
        gateway_id,
        len(measurements),
        len(source_keys),
        len(mappings),
    )

    records_by_ts = {}
    for measurement in measurements:
        source_key = measurement["source_key"]
        mapping = mappings.get(source_key)
        if not mapping or not mapping.get("enabled", True):
            continue

        rt_id = mapping["rt_id"]
        unit = mapping.get("unit_expected") or measurement.get("unit") or "kW"
        ts_event = measurement["ts_event"]
        records_by_ts.setdefault(ts_event, {})
        records_by_ts[ts_event][rt_id] = {
            "rt_id": rt_id,
            "value": measurement["value"],
            "unit": unit,
            "ts_event": ts_event,
            "gateway_id": gateway_id,
            "source_key": source_key,
            "anomaly_events": [],
        }
        if measurement.get("extract_anomaly"):
            records_by_ts[ts_event][rt_id]["anomaly_events"].append(
                build_anomaly_event(
                    gateway_id=gateway_id,
                    rt_id=rt_id,
                    unit=unit,
                    ts_event=ts_event,
                    raw_value=measurement.get("raw_value"),
                    applied_value=measurement["value"],
                    anomaly=measurement["extract_anomaly"],
                    detected_by="ingest",
                )
            )

    for ts_event, records_by_rt_id in records_by_ts.items():
        raw_values = raw_values_by_ts.get(ts_event, {})
        apply_adjustments(records_by_rt_id, raw_values)
        apply_rt_value_controls(records_by_rt_id)
        annotate_runtime_anomalies(records_by_rt_id)

    all_records = []
    all_anomalies = []
    for records_by_rt_id in records_by_ts.values():
        all_records.extend(records_by_rt_id.values())
        for record in records_by_rt_id.values():
            all_anomalies.extend(record.get("anomaly_events", []))

    if not all_records:
        missing_keys = [k for k in source_keys if k not in mappings]
        sample_missing = missing_keys[:LOG_SAMPLE_LIMIT]
        if sample_missing:
            logger.warning(
                "no mapped records; sample missing mappings: %s",
                ", ".join(sample_missing),
            )
        logger.warning("no mapped records to write")
        return {"status": "ignored", "reason": "no_mapped_records"}

    write_latest_readings(all_records)
    write_timestream_records(all_records)
    write_validation_anomalies(all_anomalies)

    return {"status": "ok", "count": len(all_records)}


def extract_payload(event):
    if not isinstance(event, dict):
        return {}

    payload = event.get("payload", event)
    if isinstance(payload, (bytes, bytearray)):
        payload = payload.decode("utf-8", errors="replace")
    if isinstance(payload, str):
        try:
            payload = json.loads(payload)
        except json.JSONDecodeError:
            logger.error("payload is not JSON")
            return {}
    if not isinstance(payload, dict):
        return {}
    return payload


def get_gateway_id(event, payload):
    topic = event.get("topic") or payload.get("topic")
    if isinstance(topic, str) and "/" in topic:
        return topic.split("/")[-1]
    return payload.get("gateway_id") or payload.get("sn") or DEFAULT_GATEWAY_ID


def extract_measurements(payload):
    meters = payload.get("meter") or payload.get("meters") or []
    if isinstance(meters, str):
        try:
            meters = json.loads(meters)
        except json.JSONDecodeError:
            return [], {}
    if isinstance(meters, dict):
        meters = [meters]
    if not isinstance(meters, list):
        return [], {}

    measurements = []
    raw_values_by_ts = {}

    for meter in meters:
        if not isinstance(meter, dict):
            continue
        meter_name = normalize_meter_name(meter.get("name") or meter.get("meter"))
        data_list = meter.get("data") or meter.get("data[]") or []
        if isinstance(data_list, dict):
            data_list = [data_list]
        if not isinstance(data_list, list):
            continue

        ts_event = parse_ts(meter.get("time") or payload.get("__dt") or payload.get("time"))

        for data in data_list:
            if not isinstance(data, dict):
                continue
            var = normalize_var_name(data.get("var"))
            value = data.get("value")
            unit = data.get("unit")
            if meter_name is None or var is None or value is None:
                continue

            try:
                raw_value_f = float(value)
            except (TypeError, ValueError):
                continue
            source_key = f"{meter_name}::{var}"
            unit_norm = unit.lower() if isinstance(unit, str) else ""
            max_value = threshold_for_unit(unit_norm, MAX_VALID_VALUE, MAX_VALID_VALUE_KWH)
            extract_anomaly = None
            value_f = raw_value_f
            if not math.isfinite(raw_value_f) or abs(raw_value_f) > max_value:
                logger.warning(
                    "out-of-range measurement normalized to 0: source_key=%s value=%s unit=%s",
                    source_key,
                    value,
                    unit,
                )
                value_f = 0.0
                extract_anomaly = detect_anomaly(
                    "__source__",
                    raw_value_f,
                    unit=unit,
                    max_valid_value=MAX_VALID_VALUE,
                    max_valid_value_kwh=MAX_VALID_VALUE_KWH,
                )

            measurements.append(
                {
                    "source_key": source_key,
                    "value": value_f,
                    "raw_value": raw_value_f,
                    "unit": unit,
                    "ts_event": ts_event,
                    "extract_anomaly": extract_anomaly,
                }
            )
            raw_values_by_ts.setdefault(ts_event, {})
            raw_values_by_ts[ts_event][source_key] = raw_value_f

    return measurements, raw_values_by_ts


def normalize_meter_name(value):
    if not isinstance(value, str):
        return value
    if value.startswith("UJA-OPERA--Edif-."):
        return value.split(".", 1)[1]
    return value


def normalize_var_name(value):
    if not isinstance(value, str):
        return value
    value = value.strip()
    if value.startswith("UJA."):
        value = value.split("UJA.", 1)[1]
    if "kW sys" in value:
        value = value.replace("kW sys", "KW sys")
    return value


def parse_ts(value):
    if value is None:
        return int(time.time())
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        try:
            return int(float(value))
        except ValueError:
            return int(time.time())
    return int(time.time())


def fetch_mappings(gateway_id, source_keys):
    if not source_keys:
        return {}

    items = []
    keys = [{"gateway_id": gateway_id, "source_key": sk} for sk in source_keys]
    request = {DDB_MAPPING_TABLE: {"Keys": [serialize_item(k) for k in keys]}}

    while True:
        response = _get_ddb_client().batch_get_item(RequestItems=request)
        items.extend(response.get("Responses", {}).get(DDB_MAPPING_TABLE, []))
        unprocessed = response.get("UnprocessedKeys", {})
        if not unprocessed or DDB_MAPPING_TABLE not in unprocessed:
            break
        request = unprocessed

    result = {}
    for item in items:
        python_item = {k: deserializer.deserialize(v) for k, v in item.items()}
        result[python_item["source_key"]] = python_item
    return result


def serialize_item(item):
    return {k: serializer.serialize(v) for k, v in item.items()}


def apply_adjustments(records_by_rt_id, raw_values):
    adjustments = {
        "uja.jaen.energia.consumo.edificio_a0.p_kw": [
            ("Consumo_Edif_Lagunillas::A0_KW sys", 1),
            ("Autoconsumo_FV_Edif::FV_A0_KW sys", 1),
        ],
        "uja.jaen.energia.consumo.um_c4.p_kw": [
            ("Consumo_Edif_Resto::C4_KW sys", 1),
            ("Autoconsumo_FV_Edif::FV_C4_KW sys", 1),
        ],
        "uja.jaen.energia.consumo.ae_magisterio.p_kw": [
            ("Consumo_Edif_Resto::Magisterio_KW sys", 1),
            ("Autoconsumo_FV_Edif::FV_Magisterio_KW sys", 1),
        ],
        "uja.jaen.energia.consumo.edificio_a3.p_kw": [
            ("Consumo_Edif_Lagunillas::A3_KW sys", 1),
            ("Consumo_Edif_Lagunillas::A4_KW sys", -1),
        ],
        "uja.jaen.energia.consumo.edificio_b4.p_kw": [
            ("Consumo_Edif_Lagunillas::B4_KW sys", 1),
            ("Consumo_Edif_Lagunillas::B5_KW sys", -1),
            ("Consumo_Edif_Lagunillas::D3_KW sys", -1),
        ],
    }

    for rt_id, terms in adjustments.items():
        if rt_id not in records_by_rt_id:
            continue
        missing = [key for key, _ in terms if key not in raw_values]
        if missing:
            logger.warning("adjustment skipped for %s (missing: %s)", rt_id, ",".join(missing))
            continue
        value = sum(raw_values[key] * sign for key, sign in terms)
        records_by_rt_id[rt_id]["value"] = value
        records_by_rt_id[rt_id]["unit"] = "kW"


def normalize_rt_value(rt_id, value):
    normalized = normalize_sentinel_value(rt_id, value)
    if normalized != float(value):
        logger.info("negative value normalized to 0 for %s: %s", rt_id, value)
    return normalized


def apply_rt_value_controls(records_by_rt_id):
    for record in records_by_rt_id.values():
        original_value = float(record["value"])
        normalized_value = normalize_rt_value(record["rt_id"], record["value"])
        if normalized_value != original_value:
            anomaly = detect_anomaly(
                record["rt_id"],
                original_value,
                unit=record.get("unit"),
                max_valid_value=MAX_VALID_VALUE,
                max_valid_value_kwh=MAX_VALID_VALUE_KWH,
            )
            if anomaly:
                record.setdefault("anomaly_events", []).append(
                    build_anomaly_event(
                        gateway_id=record["gateway_id"],
                        rt_id=record["rt_id"],
                        unit=record.get("unit"),
                        ts_event=record["ts_event"],
                        raw_value=original_value,
                        applied_value=normalized_value,
                        anomaly=anomaly,
                        detected_by="ingest",
                    )
                )
        record["value"] = normalized_value


def annotate_runtime_anomalies(records_by_rt_id):
    for record in records_by_rt_id.values():
        anomaly = detect_anomaly(
            record["rt_id"],
            record["value"],
            unit=record.get("unit"),
            max_valid_value=MAX_VALID_VALUE,
            max_valid_value_kwh=MAX_VALID_VALUE_KWH,
        )
        if not anomaly:
            continue
        event = build_anomaly_event(
            gateway_id=record["gateway_id"],
            rt_id=record["rt_id"],
            unit=record.get("unit"),
            ts_event=record["ts_event"],
            raw_value=record["value"],
            applied_value=record["value"],
            anomaly=anomaly,
            detected_by="ingest",
        )
        existing = record.setdefault("anomaly_events", [])
        if not any(item["event_key"] == event["event_key"] for item in existing):
            existing.append(event)


def build_anomaly_event(
    gateway_id,
    rt_id,
    unit,
    ts_event,
    raw_value,
    applied_value,
    anomaly,
    detected_by,
):
    metadata = derive_rt_metadata(rt_id)
    return {
        "gateway_id": gateway_id,
        "event_key": build_anomaly_event_key(ts_event, rt_id, anomaly["anomaly_type"]),
        "campus_domain": f"{metadata['campus']}#{metadata['domain']}",
        "campus": metadata["campus"],
        "domain": metadata["domain"],
        "rt_id": rt_id,
        "unit": unit or "",
        "raw_value": format_anomaly_value(raw_value),
        "applied_value": format_anomaly_value(applied_value),
        "anomaly_type": anomaly["anomaly_type"],
        "reason": anomaly["reason"],
        "threshold": format_anomaly_value(anomaly.get("threshold")),
        "ts_event": int(ts_event),
        "detected_by": detected_by,
        "updated_at": int(time.time()),
    }


def write_latest_readings(records):
    latest_by_rt = {}
    for record in records:
        rt_id = record["rt_id"]
        if rt_id not in latest_by_rt or record["ts_event"] > latest_by_rt[rt_id]["ts_event"]:
            latest_by_rt[rt_id] = record

    now = int(time.time())
    with _get_latest_table().batch_writer() as batch:
        for record in latest_by_rt.values():
            try:
                batch.put_item(
                    Item={
                        "rt_id": record["rt_id"],
                        "value": Decimal(str(record["value"])),
                        "unit": record["unit"],
                        "ts_event": int(record["ts_event"]),
                        "gateway_id": record["gateway_id"],
                        "updated_at": now,
                    }
                )
            except ClientError as exc:
                logger.error("dynamodb write failed: %s", exc)


def write_timestream_records(records):
    ts_records = []
    for record in records:
        dimensions = build_dimensions(
            record["rt_id"],
            record["unit"],
            record["gateway_id"],
        )
        ts_records.append(
            {
                "Dimensions": dimensions,
                "MeasureName": "value",
                "MeasureValue": str(record["value"]),
                "MeasureValueType": "DOUBLE",
                "Time": str(int(record["ts_event"])),
                "TimeUnit": "SECONDS",
            }
        )

    for chunk in chunked(ts_records, 100):
        try:
            _get_timestream_client().write_records(
                DatabaseName=TS_DATABASE,
                TableName=TS_TABLE,
                Records=chunk,
            )
        except _get_timestream_client().exceptions.RejectedRecordsException as exc:
            rejected = []
            response = getattr(exc, "response", {})
            if isinstance(response, dict):
                rejected = response.get("RejectedRecords", [])
            logger.error("timestream rejected records: %s", exc)
            if rejected:
                logger.error("timestream rejected details: %s", rejected)
        except ClientError as exc:
            logger.error("timestream write failed: %s", exc)


def write_validation_anomalies(events):
    if not events:
        return

    seen = set()
    with _get_anomalies_table().batch_writer() as batch:
        for event in events:
            dedupe_key = (event["gateway_id"], event["event_key"])
            if dedupe_key in seen:
                continue
            seen.add(dedupe_key)
            try:
                batch.put_item(Item=event)
            except ClientError as exc:
                logger.error("anomaly write failed: %s", exc)


def build_dimensions(rt_id, unit, gateway_id):
    parts = rt_id.split(".")
    campus = parts[1] if len(parts) > 1 else "unknown"
    domain = parts[2] if len(parts) > 2 else "unknown"
    system = parts[3] if len(parts) > 3 else "unknown"
    asset = parts[4] if len(parts) > 4 else "unknown"
    if system == "auto":
        system = "autoconsumo"
    return [
        {"Name": "rt_id", "Value": rt_id},
        {"Name": "campus", "Value": campus},
        {"Name": "domain", "Value": domain},
        {"Name": "system", "Value": system},
        {"Name": "asset", "Value": asset},
        {"Name": "unit", "Value": unit},
        {"Name": "gateway_id", "Value": gateway_id},
    ]


def chunked(items, size):
    for i in range(0, len(items), size):
        yield items[i : i + size]
