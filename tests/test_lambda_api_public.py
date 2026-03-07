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
    endesa_rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "4"}]},
        {"Data": [{"ScalarValue": "2025-01-01 00:15:00.000000000"}, {"ScalarValue": "5"}]},
    ]
    auto_rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "3"}]},
    ]

    def fake_query(query):
        if "uja.jaen.energia.consumo." in query:
            return demand_rows
        if "uja.jaen.fv.auto.ct_total.p_kw" in query:
            return auto_rows
        if "uja.jaen.fv.endesa." in query:
            return endesa_rows
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
    assert first["pv"] == 7.0
    assert second["demand"] == 12.0
    assert second["pv"] == 5.0


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


def test_scan_latest_filters_by_gateway_id():
    api = load_lambda_module()

    class FakeTable:
        def scan(self, **_kwargs):
            return {
                "Items": [
                    {
                        "rt_id": "uja.jaen.fv.auto.ct_total.p_kw",
                        "value": 72.8,
                        "unit": "kW",
                        "ts_event": 1770351480,
                        "gateway_id": "gw_autoconsumo_jaen",
                    },
                    {
                        "rt_id": "uja.jaen.fv.auto.edificio_a0.p_kw",
                        "value": 15.0,
                        "unit": "kW",
                        "ts_event": 1770351480,
                        "gateway_id": "gw_jaen_energia",
                    },
                ]
            }

    api.get_latest_table = lambda: FakeTable()

    result = api.scan_latest("uja.jaen.fv.auto.", gateway_id="gw_autoconsumo_jaen")

    assert len(result) == 1
    assert result[0]["gateway_id"] == "gw_autoconsumo_jaen"
    assert result[0]["rt_id"] == "uja.jaen.fv.auto.ct_total.p_kw"


def test_series_by_metric_returns_metric_shape():
    api = load_lambda_module()
    rows = [
        {"Data": [{"ScalarValue": "2025-01-01 00:00:00.000000000"}, {"ScalarValue": "72.8"}]},
        {"Data": [{"ScalarValue": "2025-01-01 00:15:00.000000000"}, {"ScalarValue": "70.2"}]},
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_metric({"campus": "jaen", "metric": "fv_auto"})

    assert result["campus"] == "jaen"
    assert result["metric"] == "fv_auto"
    assert result["unit"] == "kW"
    assert len(result["series"]) == 2
    assert result["series"][0]["value"] == 72.8


def test_series_by_metric_water_uses_counter_deltas():
    api = load_lambda_module()
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                {"ScalarValue": "100.0"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                {"ScalarValue": "101.5"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:10:00.000000000"},
                {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                {"ScalarValue": "103.0"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_metric({"campus": "jaen", "metric": "agua_consumo"})

    assert result["campus"] == "jaen"
    assert result["metric"] == "agua_consumo"
    assert result["unit"] == "m3"
    assert [item["value"] for item in result["series"]] == [1.5, 1.5]


def test_monthly_aggregates_fallback_to_daily():
    api = load_lambda_module()

    def fake_query_pk(pk):
        if pk == "linares#energia#consumo#monthly":
            return []
        if pk == "linares#energia#consumo#daily":
            return [
                {"sk": "2026-02-20#total", "value": 10.0, "unit": "kWh"},
                {"sk": "2026-02-21#total", "value": 12.5, "unit": "kWh"},
                {"sk": "2026-03-01#total", "value": 7.0, "unit": "kWh"},
            ]
        return []

    api.query_pk = fake_query_pk
    result = api.get_aggregates({"campus": "linares", "metric": "energia_consumo", "asset": "total"}, "monthly")

    assert result["period"] == "monthly"
    assert result["unit"] == "kWh"
    assert result["series"] == [
        {"date": "2026-02", "value": 22.5},
        {"date": "2026-03", "value": 7.0},
    ]


def test_daily_water_aggregates_fallback_from_counters():
    api = load_lambda_module()
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-02-19 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                {"ScalarValue": "100.0"},
                {"ScalarValue": "105.5"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-02-20 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                {"ScalarValue": "105.5"},
                {"ScalarValue": "107.0"},
            ]
        },
    ]

    api.query_pk = lambda _pk: []
    api.query_timestream = lambda _query: rows
    result = api.get_aggregates({"campus": "jaen", "metric": "agua_consumo", "asset": "total"}, "daily")

    assert result["unit"] == "m3"
    assert result["series"] == [
        {"date": "2025-02-19", "value": 5.5},
        {"date": "2025-02-20", "value": 1.5},
    ]


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
