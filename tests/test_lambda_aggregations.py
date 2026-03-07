import importlib.util
from pathlib import Path


def load_daily_module():
    module_path = Path("lambda/calc_daily/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_calc_daily", module_path)
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
