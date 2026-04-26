import importlib.util
from datetime import datetime, timezone
from pathlib import Path

import pytest


def load_lambda_module():
    module_path = Path("lambda/api_public/lambda_function.py")
    spec = importlib.util.spec_from_file_location("lambda_api_public", module_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.get_recent_anomaly_bucket_map = lambda rt_ids, min_ts, interval_minutes: {}
    module.get_recent_anomaly_exact_map = lambda rt_ids, min_ts: {}
    return module


def test_series_24h_merges_demand_and_pv():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "10"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "12"},
            ]
        },
    ]
    endesa_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "4"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "5"},
            ]
        },
    ]
    auto_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "3"},
            ]
        },
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
    assert second["pv"] == 8.0


def test_sum_aligned_series_maps_carries_forward_recent_source_values():
    api = load_lambda_module()
    api.current_balance_cutoff_ts = lambda: 2000

    result = api.sum_aligned_series_maps(
        [
            {1000: 800.0},
            {1300: 50.0},
            {1300: 10.0},
        ]
    )

    assert result == {
        1000: 800.0,
        1300: 860.0,
    }


def test_sum_aligned_series_maps_drops_points_newer_than_cutoff():
    api = load_lambda_module()
    api.current_balance_cutoff_ts = lambda: 1200

    result = api.sum_aligned_series_maps(
        [
            {1000: 800.0, 1300: 820.0},
            {1000: 50.0, 1300: 60.0},
        ]
    )

    assert result == {1000: 850.0}


def test_query_timeseries_analytics_carries_forward_after_negative_anomaly():
    api = load_lambda_module()
    api.current_balance_cutoff_ts = lambda: 2000000000
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a3.p_kw"},
                {"ScalarValue": "200"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a3.p_kw"},
                {"ScalarValue": "-106.63"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:10:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a3.p_kw"},
                {"ScalarValue": "220"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_b1.p_kw"},
                {"ScalarValue": "1000"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_b1.p_kw"},
                {"ScalarValue": "1020"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:10:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_b1.p_kw"},
                {"ScalarValue": "1010"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows

    result = api.query_timeseries(
        [
            "uja.jaen.energia.consumo.edificio_a3.p_kw",
            "uja.jaen.energia.consumo.edificio_b1.p_kw",
        ],
        analytics=True,
    )

    assert result == {
        1735689600: 1200.0,
        1735689900: 1220.0,
        1735690200: 1230.0,
    }


def test_get_recent_anomaly_maps_keeps_retained_negative_ct_total_out_of_exclusions():
    api = load_lambda_module()
    api.query_all_anomalies_by_campus_domain = lambda campus, domain, min_ts: [
        {
            "rt_id": "uja.jaen.fv.auto.ct_total.p_kw",
            "ts_event": 1735689600,
            "anomaly_type": "negative_not_allowed",
        },
        {
            "rt_id": "uja.jaen.energia.consumo.edificio_a3.p_kw",
            "ts_event": 1735689600,
            "anomaly_type": "negative_not_allowed",
        },
    ]

    exact, bucketed = api.get_recent_anomaly_maps(
        [
            "uja.jaen.fv.auto.ct_total.p_kw",
            "uja.jaen.energia.consumo.edificio_a3.p_kw",
        ],
        min_ts=1735689000,
        interval_minutes=15,
    )

    assert exact == {
        "uja.jaen.energia.consumo.edificio_a3.p_kw": {1735689600},
    }
    assert bucketed == {
        "uja.jaen.energia.consumo.edificio_a3.p_kw": {1735689600},
    }


def test_get_valid_latest_items_with_fallback_uses_recent_valid_sample():
    api = load_lambda_module()

    api.batch_get_latest = lambda rt_ids, gateway_id=None: [
        {
            "rt_id": rt_ids[0],
            "value": -106.63,
            "unit": "kW",
            "ts_event": 1735689900,
            "gateway_id": gateway_id,
        }
    ]
    api.query_timestream = lambda _query: [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "-106.63"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "219.09"},
            ]
        },
    ]

    result = api.get_valid_latest_items_with_fallback(
        ["uja.jaen.energia.consumo.edificio_a3.p_kw"],
        interval_minutes=5,
    )

    assert result == [
        {
            "rt_id": "uja.jaen.energia.consumo.edificio_a3.p_kw",
            "value": 219.09,
            "unit": "kW",
            "ts_event": 1735689600,
            "gateway_id": None,
        }
    ]


def test_series_24h_by_rt_ids_supports_avg_aggregation():
    api = load_lambda_module()
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.rad01.g_wm2"},
                {"ScalarValue": "400"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.rad02.g_wm2"},
                {"ScalarValue": "600"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.rad01.g_wm2"},
                {"ScalarValue": "500"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.rad02.g_wm2"},
                {"ScalarValue": "700"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows

    result = api.get_series_24h_by_rt_ids(
        {"aggregation": "avg", "interval_minutes": "15"},
        {"rt_id": ["uja.jaen.fv.endesa.rad01.g_wm2", "uja.jaen.fv.endesa.rad02.g_wm2"]},
    )

    assert result["aggregation"] == "avg"
    assert result["interval_minutes"] == 15
    assert result["unit"] == "W/m²"
    assert result["series"] == [
        {"ts": 1735689600, "value": 500.0},
        {"ts": 1735690500, "value": 600.0},
    ]


def test_query_timeseries_uses_mean_of_valid_samples_within_bin():
    api = load_lambda_module()
    api.current_balance_cutoff_ts = lambda: 2000000000
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:01:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "100"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:11:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "200"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:04:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv02.p_ac_kw"},
                {"ScalarValue": "50"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:13:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv02.p_ac_kw"},
                {"ScalarValue": "70"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows

    result = api.query_timeseries(
        [
            "uja.jaen.fv.endesa.inv01.p_ac_kw",
            "uja.jaen.fv.endesa.inv02.p_ac_kw",
        ],
        interval_minutes=15,
        analytics=True,
    )

    assert result == {
        1735689600: 210.0,
    }


def test_query_timeseries_drops_invalid_irradiance_samples_before_bin_average():
    api = load_lambda_module()
    api.current_balance_cutoff_ts = lambda: 2000000000
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:01:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.pergola_rad.g_wm2"},
                {"ScalarValue": "600"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:06:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.pergola_rad.g_wm2"},
                {"ScalarValue": "300000"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:11:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.b5_rad.g_wm2"},
                {"ScalarValue": "900"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows

    result = api.get_series_24h_by_rt_ids(
        {"aggregation": "avg", "interval_minutes": "15"},
        {"rt_id": ["uja.jaen.fv.auto.pergola_rad.g_wm2", "uja.jaen.fv.auto.b5_rad.g_wm2"]},
    )

    assert result["unit"] == "W/m²"
    assert result["series"] == [
        {"ts": 1735689600, "value": 750.0},
    ]


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


def test_handler_current_aggregate_route():
    api = load_lambda_module()
    api.get_current_aggregate = lambda params: {"ok": True, "params": params}

    event = {
        "path": "/v1/aggregates/current",
        "queryStringParameters": {"campus": "jaen", "metric": "fv_endesa", "period": "daily"},
        "multiValueQueryStringParameters": None,
    }
    response = api.handler(event, None)

    assert response["statusCode"] == 200
    assert "ok" in response["body"]


def test_series_24h_scope_accepts_interval_override():
    api = load_lambda_module()
    captured = {}

    def fake_scope_state(scope, include_series=False, interval_minutes=api.SERIES_INTERVAL_MINUTES):
        captured["scope"] = scope
        captured["include_series"] = include_series
        captured["interval_minutes"] = interval_minutes
        return {
            "campus": "jaen",
            "label": "Campus Las Lagunillas",
            "status": "complete",
            "missing_sources": [],
        }

    def fake_rows(_state, interval_minutes=api.SERIES_INTERVAL_MINUTES):
        captured["rows_interval_minutes"] = interval_minutes
        return [{"ts": 1000, "demand": 10.0, "pv": 5.0}]

    api.get_balance_scope_state = fake_scope_state
    api.build_scope_series_rows = fake_rows

    result = api.get_series_24h({"scope": "las_lagunillas", "interval_minutes": "15"})

    assert result["interval_minutes"] == 15
    assert captured == {
        "scope": "las_lagunillas",
        "include_series": True,
        "interval_minutes": 15,
        "rows_interval_minutes": 15,
    }


def test_series_24h_by_metric_accepts_interval_override_for_water():
    api = load_lambda_module()
    captured = {}

    def fake_query_counter_deltas(rt_prefix, rt_like_patterns, interval, lookback):
        captured["rt_prefix"] = rt_prefix
        captured["rt_like_patterns"] = rt_like_patterns
        captured["interval"] = interval
        captured["lookback"] = lookback
        return {1000: 3.5}

    api.query_counter_deltas = fake_query_counter_deltas

    result = api.get_series_24h_by_metric(
        {"campus": "jaen", "metric": "agua_consumo", "interval_minutes": "15"}
    )

    assert result["interval_minutes"] == 15
    assert result["series"] == [{"ts": 1000, "value": 3.5}]
    assert captured["interval"] == "15m"


def test_handler_kpis_route():
    api = load_lambda_module()

    def fake_kpis(params):
        return {"ok": True, "params": params}

    api.get_kpis = fake_kpis

    event = {
        "path": "/v1/kpis",
        "queryStringParameters": {"scope": "las_lagunillas"},
        "multiValueQueryStringParameters": None,
    }
    response = api.handler(event, None)
    assert response["statusCode"] == 200
    assert "ok" in response["body"]


def test_handler_anomalies_route():
    api = load_lambda_module()

    def fake_get_anomalies(params):
        return {"ok": True, "params": params}

    api.get_anomalies = fake_get_anomalies

    event = {
        "path": "/v1/anomalies",
        "queryStringParameters": {"campus": "jaen", "domain": "energia"},
        "multiValueQueryStringParameters": None,
    }
    response = api.handler(event, None)
    assert response["statusCode"] == 200
    assert "ok" in response["body"]


def test_get_anomalies_queries_by_campus_domain_index():
    api = load_lambda_module()

    class FakeTable:
        def query(self, **kwargs):
            assert kwargs["IndexName"] == "campus_domain_event_key"
            return {
                "Items": [
                    {
                        "gateway_id": "gw_jaen_energia",
                        "campus": "jaen",
                        "domain": "energia",
                        "rt_id": "uja.jaen.energia.consumo.edificio_a3.p_kw",
                        "unit": "kW",
                        "raw_value": "-106.63",
                        "applied_value": "-106.63",
                        "anomaly_type": "negative_not_allowed",
                        "reason": "Valor negativo no permitido para este punto.",
                        "threshold": "0",
                        "ts_event": 1735689900,
                        "detected_by": "backfill",
                    }
                ]
            }

    api.get_anomalies_table = lambda: FakeTable()

    result = api.get_anomalies({"campus": "jaen", "domain": "energia"})

    assert result["count"] == 1
    assert result["items"][0]["gateway_id"] == "gw_jaen_energia"
    assert result["items"][0]["anomaly_type"] == "negative_not_allowed"


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


def test_get_realtime_supports_gateway_only_filter():
    api = load_lambda_module()

    captured = {}

    def fake_scan_latest(prefix, gateway_id=None):
        captured["prefix"] = prefix
        captured["gateway_id"] = gateway_id
        return [
            {
                "rt_id": "uja.linares.fv.endesa.ct_total.p_kw",
                "value": 4.13,
                "unit": "kW",
                "ts_event": 1777045980,
                "gateway_id": "gw_endesa_linares",
            }
        ]

    api.scan_latest = fake_scan_latest

    result = api.get_realtime({"gateway_id": "gw_endesa_linares"}, {})

    assert captured == {"prefix": "", "gateway_id": "gw_endesa_linares"}
    assert result["ts"] == 1777045980
    assert len(result["items"]) == 1
    assert result["items"][0]["gateway_id"] == "gw_endesa_linares"
    assert result["items"][0]["rt_id"] == "uja.linares.fv.endesa.ct_total.p_kw"


def test_scan_latest_clamps_negative_ct_total_to_zero():
    api = load_lambda_module()

    class FakeTable:
        def scan(self, **_kwargs):
            return {
                "Items": [
                    {
                        "rt_id": "uja.jaen.fv.auto.ct_total.p_kw",
                        "value": -0.34,
                        "unit": "kW",
                        "ts_event": 1770351480,
                        "gateway_id": "gw_autoconsumo_jaen",
                    }
                ]
            }

    api.get_latest_table = lambda: FakeTable()

    result = api.scan_latest("uja.jaen.fv.auto.", gateway_id="gw_autoconsumo_jaen")

    assert result[0]["value"] == 0.0


def test_series_by_metric_returns_metric_shape():
    api = load_lambda_module()
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "72.8"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "70.2"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_metric({"campus": "jaen", "metric": "fv_auto"})

    assert result["campus"] == "jaen"
    assert result["metric"] == "fv_auto"
    assert result["unit"] == "kW"
    assert len(result["series"]) == 2
    assert result["series"][0]["value"] == 72.8


def test_series_by_metric_clamps_negative_ct_total_to_zero():
    api = load_lambda_module()
    rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "-0.34"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "1.2"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_metric({"campus": "jaen", "metric": "fv_auto"})

    assert [item["value"] for item in result["series"]] == [0.0, 1.2]


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


def test_get_current_aggregate_for_fv_uses_counter_delta():
    api = load_lambda_module()
    api.current_period_window_utc = lambda period: {
        "period": period,
        "key": "2026-04-09",
        "start_utc": datetime(2026, 4, 8, 22, 0, tzinfo=timezone.utc),
        "end_utc": datetime(2026, 4, 9, 9, 25, tzinfo=timezone.utc),
        "today_key": "2026-04-09",
        "month_key": "2026-04",
        "year_key": "2026",
        "timezone": "Europe/Madrid",
    }
    api.calculate_current_counter_aggregate = lambda campus, metric, config, period, window: (
        745.33,
        int(window["end_utc"].timestamp()),
    )

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "fv_endesa", "period": "daily"}
    )

    assert result == {
        "campus": "jaen",
        "metric": "fv_endesa",
        "period": "daily",
        "unit": "kWh",
        "timezone": "Europe/Madrid",
        "period_start_ts": int(datetime(2026, 4, 8, 22, 0, tzinfo=timezone.utc).timestamp()),
        "ts_event": int(datetime(2026, 4, 9, 9, 25, tzinfo=timezone.utc).timestamp()),
        "value": 745.33,
    }


def test_calculate_current_counter_delta_falls_back_to_first_sample_within_period():
    api = load_lambda_module()
    start_utc = datetime(2026, 1, 1, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 4, 12, 13, 0, tzinfo=timezone.utc)
    api.query_latest_valid_sample_at_or_before = lambda rt_id, boundary_utc, inclusive=True: (
        None if boundary_utc == start_utc else (int(end_utc.timestamp()), 6418196.41)
    )
    api.query_earliest_valid_sample_at_or_after = lambda rt_id, boundary_utc, end_boundary=None: (
        int(datetime(2026, 2, 19, 19, 53, tzinfo=timezone.utc).timestamp()),
        6290626.43,
    )

    value, ts_event = api.calculate_current_counter_delta(
        "uja.jaen.fv.endesa.ct_total.e_kwh",
        start_utc,
        end_utc,
    )

    assert value == pytest.approx(127569.98)
    assert ts_event == int(end_utc.timestamp())


def test_get_current_aggregate_for_energy_monthly_uses_closed_daily_plus_live_day():
    api = load_lambda_module()

    def fake_window(period, now=None):
        if period == "daily":
            return {
                "period": "daily",
                "key": "2026-04-11",
                "start_utc": datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
                "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
                "today_key": "2026-04-11",
                "month_key": "2026-04",
                "year_key": "2026",
                "timezone": "Europe/Madrid",
            }
        return {
            "period": "monthly",
            "key": "2026-04",
            "start_utc": datetime(2026, 3, 31, 22, 0, tzinfo=timezone.utc),
            "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
            "today_key": "2026-04-11",
            "month_key": "2026-04",
            "year_key": "2026",
            "timezone": "Europe/Madrid",
        }

    api.current_period_window_utc = fake_window
    api.query_pk_for_metric = lambda campus, metric, period: [
        {"date": "2026-04-01", "asset": "total", "value": 20.0, "unit": "kWh"},
        {"date": "2026-04-02", "asset": "total", "value": 30.0, "unit": "kWh"},
        {"date": "2026-04-11", "asset": "total", "value": 999.0, "unit": "kWh"},
    ]
    api.integrate_power_window = lambda **_kwargs: (12.5, 1770000000)

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "energia_consumo", "period": "monthly"}
    )

    assert result["value"] == 62.5
    assert result["unit"] == "kWh"
    assert result["timezone"] == "Europe/Madrid"
    assert result["ts_event"] == 1770000000


def test_get_current_aggregate_for_water_daily_total_uses_asset_deltas():
    api = load_lambda_module()
    api.current_period_window_utc = lambda period, now=None: {
        "period": period,
        "key": "2026-04-11",
        "start_utc": datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
        "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
        "today_key": "2026-04-11",
        "month_key": "2026-04",
        "year_key": "2026",
        "timezone": "Europe/Madrid",
    }
    api.calculate_current_counter_asset_aggregates = lambda campus, metric, config, period, window: (
        {"edificio_a0": 3.5, "edificio_b1": 2.0, "total": 5.5},
        1770000000,
    )

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "agua_consumo", "period": "daily"}
    )

    assert result == {
        "campus": "jaen",
        "metric": "agua_consumo",
        "period": "daily",
        "unit": "m3",
        "timezone": "Europe/Madrid",
        "period_start_ts": int(datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc).timestamp()),
        "ts_event": 1770000000,
        "asset": "total",
        "value": 5.5,
    }


def test_get_current_aggregate_for_water_monthly_asset_all_returns_values_by_point():
    api = load_lambda_module()

    def fake_window(period, now=None):
        if period == "daily":
            return {
                "period": "daily",
                "key": "2026-04-11",
                "start_utc": datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
                "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
                "today_key": "2026-04-11",
                "month_key": "2026-04",
                "year_key": "2026",
                "timezone": "Europe/Madrid",
            }
        return {
            "period": "monthly",
            "key": "2026-04",
            "start_utc": datetime(2026, 3, 31, 22, 0, tzinfo=timezone.utc),
            "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
            "today_key": "2026-04-11",
            "month_key": "2026-04",
            "year_key": "2026",
            "timezone": "Europe/Madrid",
        }

    api.current_period_window_utc = fake_window
    api.query_pk_for_metric = lambda campus, metric, period: [
        {"date": "2026-04-01", "asset": "edificio_a0", "value": 2.0, "unit": "m3"},
        {"date": "2026-04-01", "asset": "edificio_b1", "value": 3.0, "unit": "m3"},
        {"date": "2026-04-01", "asset": "total", "value": 5.0, "unit": "m3"},
        {"date": "2026-04-02", "asset": "edificio_a0", "value": 3.0, "unit": "m3"},
        {"date": "2026-04-02", "asset": "edificio_b1", "value": 4.0, "unit": "m3"},
        {"date": "2026-04-02", "asset": "total", "value": 7.0, "unit": "m3"},
        {"date": "2026-04-11", "asset": "total", "value": 999.0, "unit": "m3"},
    ]
    api.scan_latest = lambda prefix, gateway_id=None: [
        {"rt_id": "uja.jaen.agua.consumo.edificio_a0.v_m3", "value": 120.0, "unit": "m3", "ts_event": 1770000000},
        {"rt_id": "uja.jaen.agua.consumo.edificio_b1.v_m3", "value": 220.0, "unit": "m3", "ts_event": 1770000000},
    ]

    def fake_delta(rt_id, start_utc, end_utc):
        if rt_id == "uja.jaen.agua.consumo.edificio_a0.v_m3":
            return (1.5, 1770000000)
        if rt_id == "uja.jaen.agua.consumo.edificio_b1.v_m3":
            return (2.0, 1770000000)
        return (None, None)

    api.calculate_current_counter_delta = fake_delta

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "agua_consumo", "period": "monthly", "asset": "all"}
    )

    assert result["assets"] == ["edificio_a0", "edificio_b1", "total"]
    assert result["asset_values"] == {
        "edificio_a0": 6.5,
        "edificio_b1": 9.0,
        "total": 15.5,
    }
    assert result["unit"] == "m3"
    assert result["timezone"] == "Europe/Madrid"
    assert result["ts_event"] == 1770000000


def test_get_current_aggregate_for_water_single_asset_returns_only_requested_point():
    api = load_lambda_module()
    api.current_period_window_utc = lambda period, now=None: {
        "period": period,
        "key": "2026-04-11",
        "start_utc": datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
        "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
        "today_key": "2026-04-11",
        "month_key": "2026-04",
        "year_key": "2026",
        "timezone": "Europe/Madrid",
    }
    api.calculate_current_counter_asset_aggregates = lambda campus, metric, config, period, window: (
        {"edificio_a0": 3.5, "edificio_b1": 2.0, "total": 5.5},
        1770000000,
    )

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "agua_consumo", "period": "daily", "asset": "edificio_a0"}
    )

    assert result["asset"] == "edificio_a0"
    assert result["value"] == 3.5
    assert result["unit"] == "m3"


def test_get_current_aggregate_for_water_daily_falls_back_to_today_aggregate_when_live_delta_is_empty():
    api = load_lambda_module()
    api.current_period_window_utc = lambda period, now=None: {
        "period": period,
        "key": "2026-04-11",
        "start_utc": datetime(2026, 4, 10, 22, 0, tzinfo=timezone.utc),
        "end_utc": datetime(2026, 4, 11, 10, 0, tzinfo=timezone.utc),
        "today_key": "2026-04-11",
        "month_key": "2026-04",
        "year_key": "2026",
        "timezone": "Europe/Madrid",
    }
    api.calculate_current_counter_deltas_by_asset = lambda *_args, **_kwargs: ({}, None)
    api.query_pk_for_metric = lambda campus, metric, period: []
    api.build_aggregate_fallback_items = lambda campus, metric, period: [
        {"date": "2026-04-10", "asset": "edificio_a0", "value": 1.0, "unit": "m3"},
        {"date": "2026-04-10", "asset": "total", "value": 1.0, "unit": "m3"},
        {"date": "2026-04-11", "asset": "edificio_a0", "value": 2.25, "unit": "m3"},
        {"date": "2026-04-11", "asset": "edificio_b1", "value": 1.75, "unit": "m3"},
        {"date": "2026-04-11", "asset": "total", "value": 4.0, "unit": "m3"},
    ]

    result = api.get_current_aggregate(
        {"campus": "jaen", "metric": "agua_consumo", "period": "daily", "asset": "all"}
    )

    assert result["asset_values"] == {
        "edificio_a0": 2.25,
        "edificio_b1": 1.75,
        "total": 4.0,
    }
    assert result["assets"] == ["edificio_a0", "edificio_b1", "total"]
    assert result["ts_event"] is None


def test_calculate_current_counter_delta_skips_invalid_end_sample():
    api = load_lambda_module()
    start_utc = datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 4, 2, 0, 0, tzinfo=timezone.utc)

    def fake_query(query):
        if "time <= from_iso8601_timestamp('2026-04-01T00:00:00+00:00')" in query:
            return [
                {
                    "Data": [
                        {"ScalarValue": "2026-04-01 00:00:00.000000000"},
                        {"ScalarValue": "100.0"},
                    ]
                }
            ]
        if "time < from_iso8601_timestamp('2026-04-02T00:00:00+00:00')" in query:
            return [
                {
                    "Data": [
                        {"ScalarValue": "2026-04-01 23:55:00.000000000"},
                        {"ScalarValue": "-10.0"},
                    ]
                },
                {
                    "Data": [
                        {"ScalarValue": "2026-04-01 23:50:00.000000000"},
                        {"ScalarValue": "103.0"},
                    ]
                },
            ]
        return []

    api.query_timestream = fake_query

    value, ts_event = api.calculate_current_counter_delta(
        "uja.jaen.agua.consumo.edificio_a0.v_m3",
        start_utc,
        end_utc,
    )

    assert value == 3.0
    assert ts_event == int(datetime(2026, 4, 1, 23, 50, tzinfo=timezone.utc).timestamp())


def test_calculate_current_counter_deltas_by_asset_uses_bulk_boundary_queries():
    api = load_lambda_module()
    api.CURRENT_COUNTER_BULK_QUERY_THRESHOLD = 1
    start_utc = datetime(2026, 4, 1, 0, 0, tzinfo=timezone.utc)
    end_utc = datetime(2026, 4, 2, 0, 0, tzinfo=timezone.utc)
    api.scan_latest = lambda prefix: [
        {"rt_id": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
        {"rt_id": "uja.jaen.agua.consumo.edificio_b1.v_m3"},
    ]

    captured = []

    def fake_query(query):
        captured.append(query)
        if "time <= from_iso8601_timestamp('2026-04-01T00:00:00+00:00')" in query:
            return [
                {
                    "Data": [
                        {"ScalarValue": "uja.jaen.agua.consumo.edificio_b1.v_m3"},
                        {"ScalarValue": "2026-03-31 23:55:00.000000000"},
                        {"ScalarValue": "-1.0"},
                    ]
                }
            ]
        if (
            "time >= from_iso8601_timestamp('2026-04-01T00:00:00+00:00')" in query
            and "time < from_iso8601_timestamp('2026-04-02T00:00:00+00:00')" in query
        ):
            return [
                {
                    "Data": [
                        {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                        {"ScalarValue": "2026-04-01 00:05:00.000000000"},
                        {"ScalarValue": "100.0"},
                    ]
                },
                {
                    "Data": [
                        {"ScalarValue": "uja.jaen.agua.consumo.edificio_b1.v_m3"},
                        {"ScalarValue": "2026-04-01 00:10:00.000000000"},
                        {"ScalarValue": "200.0"},
                    ]
                },
            ]
        if "time < from_iso8601_timestamp('2026-04-02T00:00:00+00:00')" in query:
            return [
                {
                    "Data": [
                        {"ScalarValue": "uja.jaen.agua.consumo.edificio_a0.v_m3"},
                        {"ScalarValue": "2026-04-01 23:55:00.000000000"},
                        {"ScalarValue": "103.0"},
                    ]
                },
                {
                    "Data": [
                        {"ScalarValue": "uja.jaen.agua.consumo.edificio_b1.v_m3"},
                        {"ScalarValue": "2026-04-01 23:50:00.000000000"},
                        {"ScalarValue": "205.0"},
                    ]
                },
            ]
        return []

    api.query_timestream = fake_query

    values, ts_event = api.calculate_current_counter_deltas_by_asset(
        "uja.jaen.agua.consumo.",
        ["%.v_m3"],
        start_utc,
        end_utc,
    )

    assert values == {
        "edificio_a0": 3.0,
        "edificio_b1": 5.0,
        "total": 8.0,
    }
    assert ts_event == int(datetime(2026, 4, 1, 23, 55, tzinfo=timezone.utc).timestamp())
    assert len(captured) == 3


def test_query_timeseries_by_select_uses_kwh_limit_for_e_kwh_series():
    api = load_lambda_module()
    captured = {}

    def fake_query(query):
        captured["query"] = query
        return []

    api.query_timestream = fake_query
    api.query_timeseries_by_select(rt_ids=["uja.jaen.fv.endesa.ct_total.e_kwh"])

    assert f"measure_value::double <= {api.MAX_VALID_VALUE_KWH}" in captured["query"]
    assert f"measure_value::double >= {-api.MAX_VALID_VALUE_KWH}" in captured["query"]


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


def test_monthly_aggregates_complete_missing_months_from_daily_when_partial():
    api = load_lambda_module()

    def fake_query_pk(pk):
        if pk == "jaen#energia#consumo#monthly":
            return [
                {"sk": "2026-02#total", "value": 65.35875, "unit": "kWh"},
            ]
        if pk == "jaen#energia#consumo#daily":
            return [
                {"sk": "2026-02-20#total", "value": 10.0, "unit": "kWh"},
                {"sk": "2026-02-21#total", "value": 12.5, "unit": "kWh"},
                {"sk": "2026-03-01#total", "value": 7.0, "unit": "kWh"},
                {"sk": "2026-03-02#total", "value": 3.0, "unit": "kWh"},
            ]
        return []

    api.query_pk = fake_query_pk
    result = api.get_aggregates({"campus": "jaen", "metric": "energia_consumo", "asset": "total"}, "monthly")

    assert result["period"] == "monthly"
    assert result["unit"] == "kWh"
    assert result["series"] == [
        {"date": "2026-02", "value": 65.35875},
        {"date": "2026-03", "value": 10.0},
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
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "5"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:15:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.inv01.p_ac_kw"},
                {"ScalarValue": "7"},
            ]
        },
    ]

    api.query_timestream = lambda _query: rows
    result = api.get_series_24h_by_prefix({"rt_prefix": "uja.jaen.fv.endesa."})

    assert result["rt_prefix"] == "uja.jaen.fv.endesa."
    assert result["unit"] == "kW"
    assert len(result["series"]) == 2
    assert result["series"][0]["value"] == 5.0


def test_scope_series_for_las_lagunillas_is_complete_and_excludes_jaen_resto():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "10"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "12"},
            ]
        },
    ]
    endesa_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "-4"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "-5"},
            ]
        },
    ]
    univer_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "3"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "1"},
            ]
        },
    ]
    a0_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.edificio_a0.p_kw"},
                {"ScalarValue": "1"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.edificio_a0.p_kw"},
                {"ScalarValue": "2"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 1.0, "unit": "kW", "ts_event": 1000}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if key == set(api.JAEN_ENDESA_INVERTER_RT_IDS):
            raise AssertionError("scope de Las Lagunillas ya no debe usar inversores Endesa")
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -4.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 3.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 1.0, "unit": "kW", "ts_event": 1000}]
        return []

    def fake_query(query):
        assert "uja.jaen.energia.consumo.um_c4.p_kw" not in query
        assert "uja.jaen.energia.consumo.ae_magisterio.p_kw" not in query
        assert "uja.jaen.fv.auto.edificio_c4.p_kw" not in query
        assert "uja.jaen.fv.auto.magisterio.p_kw" not in query
        if "uja.jaen.fv.auto.ct_total.p_kw" in query:
            return univer_rows
        if "uja.jaen.fv.auto.edificio_a0.p_kw" in query:
            return a0_rows
        if "uja.jaen.fv.endesa.ct_total.p_kw" in query:
            return endesa_rows
        if "uja.jaen.energia.consumo.edificio_a0.p_kw" in query:
            return demand_rows
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "las_lagunillas"})

    assert result["scope"] == "las_lagunillas"
    assert result["status"] == "complete"
    assert result["missing_sources"] == []
    assert result["series"] == [
        {"ts": 1735689600, "demand": 10.0, "pv": 8.0},
        {"ts": 1735689900, "demand": 12.0, "pv": 8.0},
    ]


def test_scope_series_returns_partial_when_univer_is_missing():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "10"},
            ]
        },
    ]
    endesa_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "4"},
            ]
        },
    ]
    a0_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.edificio_a0.p_kw"},
                {"ScalarValue": "1"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 1.0, "unit": "kW", "ts_event": 1000}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if key == set(api.JAEN_ENDESA_INVERTER_RT_IDS):
            raise AssertionError("scope de Las Lagunillas ya no debe usar inversores Endesa")
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -4.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return []
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 1.0, "unit": "kW", "ts_event": 1000}]
        return []

    def fake_query(query):
        if "uja.jaen.fv.auto.edificio_a0.p_kw" in query:
            return a0_rows
        if "uja.jaen.fv.endesa.ct_total.p_kw" in query:
            return endesa_rows
        if "uja.jaen.energia.consumo.edificio_a0.p_kw" in query:
            return demand_rows
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "las_lagunillas"})

    assert result["status"] == "partial"
    assert result["missing_sources"] == ["jaen_fv_auto_univer"]
    assert result["series"] == [{"ts": 1735689600, "demand": 10.0, "pv": 5.0}]


def test_scope_series_keeps_demand_when_linares_pv_series_is_missing():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.linares.energia.consumo.lab_sg_t1.p_kw"},
                {"ScalarValue": "30"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.linares.energia.consumo.lab_sg_t1.p_kw"},
                {"ScalarValue": "28"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.CTL_LINARES_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 2.0, "unit": "kW", "ts_event": 1100}
                for rt_id in api.CTL_LINARES_DEMAND_RT_IDS
            ]
        if rt_ids == ["uja.linares.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 6.0, "unit": "kW", "ts_event": 1100}]
        return []

    def fake_query(query):
        if "uja.linares.energia.consumo.lab_sg_t1.p_kw" in query:
            return demand_rows
        if "uja.linares.fv.endesa.ct_total.p_kw" in query:
            return []
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "ctl_linares"})

    assert result["scope"] == "ctl_linares"
    assert result["status"] == "partial"
    assert result["missing_sources"] == ["linares_fv_endesa_total"]
    assert result["series"] == [
        {"ts": 1735689600, "demand": 30.0, "pv": None},
        {"ts": 1735689900, "demand": 28.0, "pv": None},
    ]


def test_scope_series_uses_locf_for_recent_balance_gap():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:35:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "10"},
            ]
        },
    ]
    endesa_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "-4"},
            ]
        },
    ]
    univer_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "3"},
            ]
        },
    ]
    a0_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.edificio_a0.p_kw"},
                {"ScalarValue": "1"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 1.0, "unit": "kW", "ts_event": 1000}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -4.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 3.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 1.0, "unit": "kW", "ts_event": 1000}]
        return []

    def fake_query(query):
        if "uja.jaen.fv.endesa.ct_total.p_kw" in query:
            return endesa_rows
        if "uja.jaen.fv.auto.ct_total.p_kw" in query:
            return univer_rows
        if "uja.jaen.fv.auto.edificio_a0.p_kw" in query:
            return a0_rows
        if "uja.jaen.energia.consumo.edificio_a0.p_kw" in query:
            return demand_rows
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "las_lagunillas"})

    assert result["series"] == [
        {"ts": 1735731300, "demand": 10.0, "pv": None},
        {"ts": 1735731600, "demand": 10.0, "pv": 8.0},
    ]


def test_scope_series_drops_stale_balance_points_beyond_freshness_limit():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:20:00.000000000"},
                {"ScalarValue": "uja.jaen.energia.consumo.edificio_a0.p_kw"},
                {"ScalarValue": "10"},
            ]
        },
    ]
    endesa_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "-4"},
            ]
        },
    ]
    univer_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.ct_total.p_kw"},
                {"ScalarValue": "3"},
            ]
        },
    ]
    a0_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 11:40:00.000000000"},
                {"ScalarValue": "uja.jaen.fv.auto.edificio_a0.p_kw"},
                {"ScalarValue": "1"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 1.0, "unit": "kW", "ts_event": 1000}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -4.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 3.0, "unit": "kW", "ts_event": 1000}]
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 1.0, "unit": "kW", "ts_event": 1000}]
        return []

    def fake_query(query):
        if "uja.jaen.fv.endesa.ct_total.p_kw" in query:
            return endesa_rows
        if "uja.jaen.fv.auto.ct_total.p_kw" in query:
            return univer_rows
        if "uja.jaen.fv.auto.edificio_a0.p_kw" in query:
            return a0_rows
        if "uja.jaen.energia.consumo.edificio_a0.p_kw" in query:
            return demand_rows
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "las_lagunillas"})

    assert result["series"] == [
        {"ts": 1735730400, "demand": 10.0, "pv": None},
        {"ts": 1735731600, "demand": None, "pv": 8.0},
    ]


def test_scope_kpis_for_las_lagunillas_uses_exact_functional_definition():
    api = load_lambda_module()

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 10.0, "unit": "kW", "ts_event": 1200}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if key == set(api.JAEN_ENDESA_INVERTER_RT_IDS):
            raise AssertionError("scope de Las Lagunillas ya no debe usar inversores Endesa")
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -200.0, "unit": "kW", "ts_event": 1200}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 40.0, "unit": "kW", "ts_event": 1200}]
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 15.0, "unit": "kW", "ts_event": 1200}]
        return []

    api.batch_get_latest = fake_batch_get

    result = api.get_kpis({"scope": "las_lagunillas"})
    values = {item["kpi"]: item["value"] for item in result["kpis"]}

    assert result["status"] == "complete"
    assert result["missing_sources"] == []
    assert values["demanda_kw"] == 200.0
    assert values["fv_kw"] == 255.0
    assert values["red_kw"] == 0.0
    assert values["autoconsumo_kw"] == 200.0
    assert values["autoconsumo_pct"] == pytest.approx(100.0)


def test_scope_kpis_return_partial_when_univer_is_missing():
    api = load_lambda_module()

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.LAS_LAGUNILLAS_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 10.0, "unit": "kW", "ts_event": 1200}
                for rt_id in api.LAS_LAGUNILLAS_DEMAND_RT_IDS
            ]
        if key == set(api.JAEN_ENDESA_INVERTER_RT_IDS):
            raise AssertionError("scope de Las Lagunillas ya no debe usar inversores Endesa")
        if rt_ids == ["uja.jaen.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": -200.0, "unit": "kW", "ts_event": 1200}]
        if rt_ids == ["uja.jaen.fv.auto.ct_total.p_kw"]:
            return []
        if rt_ids == ["uja.jaen.fv.auto.edificio_a0.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 15.0, "unit": "kW", "ts_event": 1200}]
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = lambda _query: []

    result = api.get_kpis({"scope": "las_lagunillas"})
    values = {item["kpi"]: item["value"] for item in result["kpis"]}

    assert result["status"] == "partial"
    assert result["missing_sources"] == ["jaen_fv_auto_univer"]
    assert values["demanda_kw"] is None
    assert values["fv_kw"] is None


def test_scope_series_for_ctl_linares_uses_ct_total_pv():
    api = load_lambda_module()
    demand_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.linares.energia.consumo.lab_sg_t1.p_kw"},
                {"ScalarValue": "30"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.linares.energia.consumo.lab_sg_t1.p_kw"},
                {"ScalarValue": "28"},
            ]
        },
    ]
    pv_rows = [
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:00:00.000000000"},
                {"ScalarValue": "uja.linares.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "6"},
            ]
        },
        {
            "Data": [
                {"ScalarValue": "2025-01-01 00:05:00.000000000"},
                {"ScalarValue": "uja.linares.fv.endesa.ct_total.p_kw"},
                {"ScalarValue": "7"},
            ]
        },
    ]

    def fake_batch_get(rt_ids, gateway_id=None):
        assert gateway_id is None
        key = set(rt_ids)
        if key == set(api.CTL_LINARES_DEMAND_RT_IDS):
            return [
                {"rt_id": rt_id, "value": 2.0, "unit": "kW", "ts_event": 1100}
                for rt_id in api.CTL_LINARES_DEMAND_RT_IDS
            ]
        if rt_ids == ["uja.linares.fv.endesa.ct_total.p_kw"]:
            return [{"rt_id": rt_ids[0], "value": 6.0, "unit": "kW", "ts_event": 1100}]
        return []

    def fake_query(query):
        if "uja.linares.fv.endesa.ct_total.p_kw" in query:
            return pv_rows
        if "uja.linares.energia.consumo.lab_sg_t1.p_kw" in query:
            return demand_rows
        return []

    api.batch_get_latest = fake_batch_get
    api.query_timestream = fake_query

    result = api.get_series_24h({"scope": "ctl_linares"})

    assert result["scope"] == "ctl_linares"
    assert result["status"] == "complete"
    assert result["series"] == [
        {"ts": 1735689600, "demand": 30.0, "pv": 6.0},
        {"ts": 1735689900, "demand": 28.0, "pv": 7.0},
    ]
