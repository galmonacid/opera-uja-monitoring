import importlib.util
from datetime import datetime, timezone
from pathlib import Path


def load_daily_module():
    module_path = Path("lambda/calc_daily/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_calc_daily", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.query_anomaly_timestamps = lambda rt_id, start, end: set()
    return module


def load_monthly_module():
    module_path = Path("lambda/calc_monthly/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_calc_monthly", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_yearly_module():
    module_path = Path("lambda/calc_yearly/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_calc_yearly", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
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


def test_daily_total_for_jaen_fv_auto_uses_counter_energy_delta():
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
    captured = {}

    daily.fetch_configs = lambda: [config]
    daily.fetch_rt_ids = lambda _config: ["uja.jaen.fv.auto.ct_total.e_kwh"]
    daily.calculate_counter_delta = lambda rt_id, _start, _end: 196.66 if rt_id.endswith(".e_kwh") else None
    daily.write_items = lambda items: captured.setdefault("items", []).extend(items)

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#total")
    assert float(total_item["value"]) == 196.66
    ct_total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#ct_total")
    assert float(ct_total_item["value"]) == 196.66


def test_daily_total_for_jaen_fv_endesa_uses_counter_energy_delta():
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
    captured = {}

    daily.fetch_configs = lambda: [config]
    daily.fetch_rt_ids = lambda _config: ["uja.jaen.fv.endesa.ct_total.e_kwh"]
    daily.calculate_counter_delta = lambda rt_id, _start, _end: 745.33 if rt_id.endswith(".e_kwh") else None
    daily.write_items = lambda items: captured.setdefault("items", []).extend(items)

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#total")
    assert float(total_item["value"]) == 745.33
    ct_total_item = next(item for item in captured["items"] if item["sk"] == "2026-03-06#ct_total")
    assert float(ct_total_item["value"]) == 745.33


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

    assert round(value, 6) == 3.2
    assert captured["events"] == []


def test_calculate_counter_delta_uses_start_and_end_samples():
    daily = load_daily_module()
    start_sample = (daily.parse_time("2026-03-07T00:00:00+00:00"), 291000.0)
    end_sample = (daily.parse_time("2026-03-07T23:59:00+00:00"), 291196.66)
    daily.query_latest_valid_sample = lambda _rt_id, boundary, operator="<=": (
        start_sample if operator == "<=" else end_sample
    )

    value = daily.calculate_counter_delta(
        "uja.jaen.fv.auto.ct_total.e_kwh",
        "2026-03-07T00:00:00+00:00",
        "2026-03-07T23:59:59+00:00",
    )

    assert round(value, 6) == 196.66


def test_closed_daily_window_uses_europe_madrid_boundaries():
    daily = load_daily_module()
    window = daily.closed_daily_window_utc(target_date="2026-04-09")

    assert window["key"] == "2026-04-09"
    assert window["start_utc"] == datetime(2026, 4, 8, 22, 0, tzinfo=timezone.utc)
    assert window["end_utc"] == datetime(2026, 4, 9, 22, 0, tzinfo=timezone.utc)


def test_last_closed_month_and_year_keys_use_local_calendar():
    monthly = load_monthly_module()
    yearly = load_yearly_module()
    reference_now = datetime(2026, 4, 11, 12, 0, tzinfo=timezone.utc)

    assert monthly.last_closed_month_key(now=reference_now) == "2026-03"
    assert yearly.last_closed_year_key(now=reference_now) == "2025"


def test_daily_handler_writes_per_config_and_returns_partial_on_error():
    daily = load_daily_module()
    energia_config = daily.normalize_config({
        "config_id": "jaen_energia",
        "gateway_id": "gw_jaen_energia",
        "rt_id_prefix": "uja.jaen.energia.consumo.",
        "campus": "jaen",
        "domain": "energia",
        "system": "consumo",
        "metric": "energia_consumo",
    })
    fv_config = daily.normalize_config({
        "config_id": "jaen_fv_endesa",
        "gateway_id": "gw_endesa_jaen",
        "rt_id_prefix": "uja.jaen.fv.endesa.",
        "campus": "jaen",
        "domain": "fv",
        "system": "endesa",
        "metric": "fv_endesa",
    })
    captured = []

    daily.fetch_configs = lambda: [energia_config, fv_config]
    daily.fetch_rt_ids = lambda config: (
        ["uja.jaen.energia.consumo.edificio_a0.p_kw"]
        if config["metric"] == "energia_consumo"
        else ["uja.jaen.fv.endesa.ct_total.e_kwh"]
    )

    def fake_calculate(config, rt_id, _start, _end):
        if config["metric"] == "energia_consumo":
            return 12.5
        raise RuntimeError(f"boom:{rt_id}")

    daily.calculate_daily_value = fake_calculate
    daily.write_items = lambda items: captured.append(list(items))

    result = daily.handler({"date": "2026-03-06"}, None)

    assert result["status"] == "partial"
    assert result["count"] == 2
    assert len(captured) == 1
    assert captured[0][0]["sk"] == "2026-03-06#edificio_a0"
    assert captured[0][1]["sk"] == "2026-03-06#total"


def test_monthly_handler_uses_last_closed_month_by_default():
    monthly = load_monthly_module()
    config = monthly.normalize_config({
        "config_id": "jaen_energia",
        "gateway_id": "gw_jaen_energia",
        "campus": "jaen",
        "domain": "energia",
        "system": "consumo",
        "metric": "energia_consumo",
    })
    captured = {}

    monthly.last_closed_month_key = lambda: "2026-03"
    monthly.fetch_configs = lambda: [config]
    monthly.query_pk = lambda _pk: [
        {"sk": "2026-03-01#total", "value": 5.0, "unit": "kWh"},
        {"sk": "2026-03-02#total", "value": 7.5, "unit": "kWh"},
        {"sk": "2026-04-01#total", "value": 99.0, "unit": "kWh"},
    ]
    monthly.write_items = lambda items: captured.setdefault("items", []).extend(items)

    result = monthly.handler({}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2026-03#total")
    assert float(total_item["value"]) == 12.5


def test_yearly_handler_uses_last_closed_year_by_default():
    yearly = load_yearly_module()
    config = yearly.normalize_config({
        "config_id": "jaen_energia",
        "gateway_id": "gw_jaen_energia",
        "campus": "jaen",
        "domain": "energia",
        "system": "consumo",
        "metric": "energia_consumo",
    })
    captured = {}

    yearly.last_closed_year_key = lambda: "2025"
    yearly.fetch_configs = lambda: [config]
    yearly.query_pk = lambda _pk: [
        {"sk": "2025-01#total", "value": 10.0, "unit": "kWh"},
        {"sk": "2025-02#total", "value": 11.5, "unit": "kWh"},
        {"sk": "2026-01#total", "value": 99.0, "unit": "kWh"},
    ]
    yearly.write_items = lambda items: captured.setdefault("items", []).extend(items)

    result = yearly.handler({}, None)

    assert result["status"] == "ok"
    total_item = next(item for item in captured["items"] if item["sk"] == "2025#total")
    assert float(total_item["value"]) == 21.5
