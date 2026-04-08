import importlib.util
from pathlib import Path


def load_daily_module():
    module_path = Path("lambda/calc_daily/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_calc_daily", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.query_anomaly_timestamps = lambda rt_id, start, end: set()
    return module


def test_build_pk_from_config():
    daily = load_daily_module()
    config = {
        "campus": "jaen",
        "domain": "energia",
        "system": "consumo",
    }
    pk = daily.build_pk(config, "daily")
    assert pk == "jaen#energia#consumo#daily"


def test_normalize_config_defaults():
    daily = load_daily_module()
    config = daily.normalize_config({
        "config_id": "cfg1",
        "gateway_id": "gw_jaen_energia",
        "rt_id_prefix": "uja.jaen.energia.consumo.",
        "campus": "jaen",
        "domain": "energia",
        "system": "consumo",
        "metric": "energia_consumo",
    })
    assert config["unit"] == "kWh"
    assert config["gateway_id"] == "gw_jaen_energia"


def test_daily_total_for_jaen_fv_auto_uses_only_ct_total():
    daily = load_daily_module()
    config = daily.normalize_config({
        "config_id": "jaen_fv_auto",
        "gateway_id": "gw_autoconsumo_jaen",
        "rt_id_prefix": "uja.jaen.fv.auto.",
        "campus": "jaen",
        "domain": "fv",
        "system": "auto",
        "metric": "fv_auto",
    })
    values = {
        "uja.jaen.fv.auto.ct_total.p_kw": 100.0,
        "uja.jaen.fv.auto.pergola.p_ac_kw": 10.0,
        "uja.jaen.fv.auto.parking_p4.p_ac_kw": 8.0,
    }
    captured = {}

    daily.fetch_configs = lambda: [config]
    daily.fetch_rt_ids = lambda _config: list(values)
    daily.integrate_energy = lambda rt_id, _start, _end: values[rt_id]
    daily.write_items = lambda items: captured.setdefault("items", items)

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#total")
    assert float(total_item["value"]) == 100.0


def test_daily_total_for_jaen_fv_endesa_uses_only_inverters():
    daily = load_daily_module()
    config = daily.normalize_config({
        "config_id": "jaen_fv_endesa",
        "gateway_id": "gw_endesa_jaen",
        "rt_id_prefix": "uja.jaen.fv.endesa.",
        "campus": "jaen",
        "domain": "fv",
        "system": "endesa",
        "metric": "fv_endesa",
    })
    values = {
        "uja.jaen.fv.endesa.ct_total.p_kw": 130.0,
        "uja.jaen.fv.endesa.inv01.p_ac_kw": 60.0,
        "uja.jaen.fv.endesa.inv02.p_ac_kw": 55.0,
    }
    captured = {}

    daily.fetch_configs = lambda: [config]
    daily.fetch_rt_ids = lambda _config: list(values)
    daily.integrate_energy = lambda rt_id, _start, _end: values[rt_id]
    daily.write_items = lambda items: captured.setdefault("items", items)

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#total")
    assert float(total_item["value"]) == 115.0


def test_daily_water_uses_counter_delta():
    daily = load_daily_module()
    config = daily.normalize_config({
        "config_id": "jaen_agua_consumo",
        "gateway_id": "gw_jaen_agua",
        "rt_id_prefix": "uja.jaen.agua.consumo.",
        "campus": "jaen",
        "domain": "agua",
        "system": "consumo",
        "metric": "agua_consumo",
        "unit": "m3",
    })
    values = {
        "uja.jaen.agua.consumo.edificio_a0.v_m3": 5.5,
        "uja.jaen.agua.consumo.edificio_a1.v_m3": 1.25,
    }
    captured = {}

    daily.fetch_configs = lambda: [config]
    daily.fetch_rt_ids = lambda _config: list(values)
    daily.calculate_daily_value = lambda _config, rt_id, _start, _end: values[rt_id]
    daily.write_items = lambda items: captured.setdefault("items", items)

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#total")
    assert float(total_item["value"]) == 6.75


def test_query_timestream_clamps_negative_ct_total_to_zero():
    daily = load_daily_module()
    
    class FakeQuery:
        def query(self, **_kwargs):
            return {
                "Rows": [
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 10:00:00.000000000"},
                            {"ScalarValue": "-0.34"},
                        ]
                    },
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 11:00:00.000000000"},
                            {"ScalarValue": "-0.20"},
                        ]
                    },
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 12:00:00.000000000"},
                            {"ScalarValue": "1.2"},
                        ]
                    },
                ]
            }

    daily.get_ts_query = lambda: FakeQuery()
    result = daily.query_timestream(
        "uja.jaen.fv.auto.ct_total.p_kw",
        "2026-03-06T10:00:00+00:00",
        "2026-03-06T12:00:00+00:00",
    )

    assert [value for _, value in result] == [0.0, 0.0, 1.2]


def test_query_timestream_skips_negative_demand_anomaly():
    daily = load_daily_module()

    class FakeQuery:
        def query(self, **_kwargs):
            return {
                "Rows": [
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 10:00:00.000000000"},
                            {"ScalarValue": "219.09"},
                        ]
                    },
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 11:00:00.000000000"},
                            {"ScalarValue": "-106.63"},
                        ]
                    },
                    {
                        "Data": [
                            {"ScalarValue": "2026-03-06 12:00:00.000000000"},
                            {"ScalarValue": "324.58"},
                        ]
                    },
                ]
            }

    daily.get_ts_query = lambda: FakeQuery()
    result = daily.query_timestream(
        "uja.jaen.energia.consumo.edificio_a3.p_kw",
        "2026-03-06T10:00:00+00:00",
        "2026-03-06T12:00:00+00:00",
    )

    assert [value for _, value in result] == [219.09, 324.58]


def test_calculate_counter_consumption_sums_only_positive_deltas():
    daily = load_daily_module()
    daily.query_timestream = lambda _rt_id, _start, _end: [
        (daily.parse_time("2026-03-06T00:00:00+00:00"), 100.0),
        (daily.parse_time("2026-03-06T01:00:00+00:00"), 102.0),
        (daily.parse_time("2026-03-06T02:00:00+00:00"), 99.0),
        (daily.parse_time("2026-03-06T03:00:00+00:00"), 105.5),
    ]
    captured = {}
    daily.write_validation_anomalies = lambda events: captured.setdefault("events", events)
    daily.COUNTER_RESET_NEGATIVE_THRESHOLD = 0.0

    value = daily.calculate_counter_consumption(
        {"gateway_id": "gw_jaen_agua"},
        "uja.jaen.agua.consumo.edificio_a0.v_m3",
        "2026-03-06T00:00:00+00:00",
        "2026-03-06T23:59:59+00:00",
    )

    assert value == 8.5
    assert len(captured["events"]) == 1
    assert captured["events"][0]["anomaly_type"] == "counter_reset_detected"


def test_calculate_counter_consumption_respects_negative_threshold_for_anomaly_log():
    daily = load_daily_module()
    daily.query_timestream = lambda _rt_id, _start, _end: [
        (daily.parse_time("2026-03-06T00:00:00+00:00"), 100.0),
        (daily.parse_time("2026-03-06T01:00:00+00:00"), 99.8),
        (daily.parse_time("2026-03-06T02:00:00+00:00"), 103.0),
    ]
    captured = {}
    daily.write_validation_anomalies = lambda events: captured.setdefault("events", events)
    daily.COUNTER_RESET_NEGATIVE_THRESHOLD = 1.0

    value = daily.calculate_counter_consumption(
        {"gateway_id": "gw_jaen_agua"},
        "uja.jaen.agua.consumo.edificio_a1.v_m3",
        "2026-03-06T00:00:00+00:00",
        "2026-03-06T23:59:59+00:00",
    )

    assert value == 3.2
    assert captured["events"] == []
