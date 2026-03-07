import csv
import importlib.util
import json
from pathlib import Path


def load_lambda_module():
    module_path = Path("lambda/ingest_telemetry/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_ingest_telemetry", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_mapping(file_path):
    mapping = {}
    with open(file_path, "r", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            if row.get("enabled", "").strip().lower() != "true":
                continue
            mapping[row["source_key"]] = {
                "rt_id": row["rt_id"],
                "unit_expected": row.get("unit_expected") or "kW",
                "enabled": True,
            }
    return mapping


def test_ingest_applies_adjustments():
    module = load_lambda_module()
    mapping = load_mapping("seeds/gateway_variable_map_gw_jaen_energia.csv")

    with open("lambda/ingest_telemetry/test_event.json", "r", encoding="utf-8") as handle:
        event = json.load(handle)

    def fetch_mappings(_gateway_id, source_keys):
        return {sk: mapping[sk] for sk in source_keys if sk in mapping}

    captured = {}

    def write_latest_readings(records):
        captured["latest"] = records

    module.fetch_mappings = fetch_mappings
    module.write_latest_readings = write_latest_readings
    module.write_timestream_records = lambda _records: None

    result = module.handler(event, None)
    assert result["status"] == "ok"
    assert result["count"] == 11

    values = {item["rt_id"]: item["value"] for item in captured["latest"]}
    assert values["uja.jaen.energia.consumo.edificio_a0.p_kw"] == 135.5
    assert values["uja.jaen.energia.consumo.edificio_a3.p_kw"] == 70.0
    assert values["uja.jaen.energia.consumo.edificio_b4.p_kw"] == 60.0
    assert values["uja.jaen.energia.consumo.um_c4.p_kw"] == 45.0
    assert values["uja.jaen.energia.consumo.ae_magisterio.p_kw"] == 41.0


def test_ingest_autoconsumo_gateway_uses_topic_and_variants():
    module = load_lambda_module()
    mapping = load_mapping("seeds/gateway_variable_map_gw_autoconsumo_jaen.csv")

    with open(
        "lambda/ingest_telemetry/test_event_gw_autoconsumo_jaen.json",
        "r",
        encoding="utf-8",
    ) as handle:
        event = json.load(handle)

    def fetch_mappings(_gateway_id, source_keys):
        return {sk: mapping[sk] for sk in source_keys if sk in mapping}

    captured = {}

    def write_latest_readings(records):
        captured["latest"] = records

    module.fetch_mappings = fetch_mappings
    module.write_latest_readings = write_latest_readings
    module.write_timestream_records = lambda _records: None

    result = module.handler(event, None)
    assert result["status"] == "ok"
    assert result["count"] == 11

    values = {item["rt_id"]: item["value"] for item in captured["latest"]}
    gateways = {item["gateway_id"] for item in captured["latest"]}
    assert gateways == {"gw_autoconsumo_jaen"}
    assert values["uja.jaen.fv.auto.ct_total.p_kw"] == 72.8
    assert values["uja.jaen.fv.auto.pergola.p_ac_kw"] == 11.2
    assert values["uja.jaen.fv.auto.pergola_rad.g_wm2"] == 612.5
    assert values["uja.jaen.fv.auto.b5_rad.g_wm2"] == 598.3
    assert values["uja.jaen.fv.auto.fachada_rad.g_wm2"] == 601.2
