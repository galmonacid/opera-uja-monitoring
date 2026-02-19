import importlib.util
from pathlib import Path


def load_lambda_module():
    module_path = Path("lambda/api_public/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_api_public", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_series_24h_merges_demand_and_pv():
    api = load_lambda_module()
    demand_rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "10"}]},
        {"Data": [{"ScalarValue": "2025-01-01 00:15:00.000000000"}, {"ScalarValue": "12"}]},
    ]
    pv_rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "3"}]},
    ]

    def fake_query(query):
        if "fv.auto" in query:
            return pv_rows
        return demand_rows

    api.query_timestream = fake_query

    result = api.get_series_24h({"campus": "jaen"})

    assert result["campus"] == "jaen"
    assert result["unit"] == "kW"
    assert result["interval_minutes"] == api.SERIES_INTERVAL_MINUTES
    assert len(result["series"]) == 2
    first = result["series"][0]
    second = result["series"][1]
    assert first["demand"] == 10.0
    assert first["pv"] == 3.0
    assert second["demand"] == 12.0
    assert second["pv"] == 0.0


def test_handler_series_24h_route():
    api = load_lambda_module()
    def fake_series(params):
        return {"ok": True, "params": params}

    api.get_series_24h = fake_series

    event = {
        "path": "/v1/series/24h",
        "queryStringParameters": {"campus": "jaen"},
        "multiValueQueryStringParameters": None,
    }
    response = api.handler(event, None)
    assert response["statusCode"] == 200
    assert "ok" in response["body"]


def test_metric_to_scope_supports_new_metrics():
    api = load_lambda_module()
    assert api.metric_to_scope("agua_consumo") == ("agua", "consumo")
    assert api.metric_to_scope("fv_endesa") == ("fv", "endesa")
    assert api.metric_to_scope("fv_auto") == ("fv", "auto")


def test_series_by_prefix():
    api = load_lambda_module()
    rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "5"}]},
        {"Data": [{"ScalarValue": "2025-01-01 00:15:00.000000000"}, {"ScalarValue": "7"}]},
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_prefix({"rt_prefix": "uja.jaen.fv.endesa."})

    assert result["rt_prefix"] == "uja.jaen.fv.endesa."
    assert result["unit"] == "kW"
    assert len(result["series"]) == 2
    assert result["series"][0]["value"] == 5.0
