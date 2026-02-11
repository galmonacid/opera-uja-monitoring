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
