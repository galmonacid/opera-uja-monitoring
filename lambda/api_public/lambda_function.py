import json
import os
from datetime import datetime, timezone
from fnmatch import fnmatchcase

import boto3
from boto3.dynamodb.conditions import Attr, Key


DDB_LATEST_TABLE = os.getenv("DDB_LATEST_TABLE", "latest_readings")
DDB_AGG_TABLE = os.getenv("DDB_AGG_TABLE", "aggregates")
TS_DATABASE = os.getenv("TS_DATABASE", "uja_monitoring")
TS_TABLE = os.getenv("TS_TABLE", "telemetry_rt")
ALLOWED_ORIGIN = os.getenv("ALLOWED_ORIGIN", "*")
MAX_VALID_VALUE = float(os.getenv("MAX_VALID_VALUE", "1000000"))
NEGATIVE_TO_ZERO_RT_IDS = {"uja.jaen.fv.auto.ct_total.p_kw"}

_dynamodb = None
_latest_table = None
_agg_table = None
_ts_query = None

SERIES_INTERVAL_MINUTES = 5
LAS_LAGUNILLAS_DEMAND_RT_IDS = [
    "uja.jaen.energia.consumo.edificio_a0.p_kw",
    "uja.jaen.energia.consumo.edificio_a1.p_kw",
    "uja.jaen.energia.consumo.edificio_a2.p_kw",
    "uja.jaen.energia.consumo.edificio_a3.p_kw",
    "uja.jaen.energia.consumo.edificio_a4.p_kw",
    "uja.jaen.energia.consumo.edificio_b1.p_kw",
    "uja.jaen.energia.consumo.edificio_b2.p_kw",
    "uja.jaen.energia.consumo.edificio_b3.p_kw",
    "uja.jaen.energia.consumo.edificio_b4.p_kw",
    "uja.jaen.energia.consumo.edificio_b5.p_kw",
    "uja.jaen.energia.consumo.edificio_c1.p_kw",
    "uja.jaen.energia.consumo.edificio_c2.p_kw",
    "uja.jaen.energia.consumo.edificio_c3.p_kw",
    "uja.jaen.energia.consumo.edificio_c5.p_kw",
    "uja.jaen.energia.consumo.edificio_c6.p_kw",
    "uja.jaen.energia.consumo.edificio_d1.p_kw",
    "uja.jaen.energia.consumo.edificio_d2.p_kw",
    "uja.jaen.energia.consumo.edificio_d3.p_kw",
    "uja.jaen.energia.consumo.edificio_d4.p_kw",
    "uja.jaen.energia.consumo.carga_vhe.p_kw",
]
JAEN_ENDESA_INVERTER_RT_IDS = [
    f"uja.jaen.fv.endesa.inv{idx:02d}.p_ac_kw"
    for idx in range(1, 13)
]
CTL_LINARES_DEMAND_RT_IDS = [
    "uja.linares.energia.consumo.lab_sg_t1.p_kw",
    "uja.linares.energia.consumo.lab_sg_t2.p_kw",
    "uja.linares.energia.consumo.urbanizacion.p_kw",
    "uja.linares.energia.consumo.aulario_departamental.p_kw",
    "uja.linares.energia.consumo.polideportivo.p_kw",
]
METRIC_SERIES_CONFIG = {
    ("jaen", "energia_consumo"): {
        "type": "power",
        "rt_prefix": "uja.jaen.energia.consumo.",
        "rt_like_patterns": ["%.p_kw"],
    },
    ("linares", "energia_consumo"): {
        "type": "power",
        "rt_prefix": "uja.linares.energia.consumo.",
        "rt_like_patterns": ["%.p_kw"],
    },
    ("jaen", "agua_consumo"): {
        "type": "counter",
        "rt_prefix": "uja.jaen.agua.consumo.",
        "rt_like_patterns": ["%.v_m3"],
        "unit": "m3",
    },
    ("linares", "agua_consumo"): {
        "type": "counter",
        "rt_prefix": "uja.linares.agua.consumo.",
        "rt_like_patterns": ["%.v_m3"],
        "unit": "m3",
    },
    ("jaen", "fv_endesa"): {
        "type": "power",
        "rt_prefix": "uja.jaen.fv.endesa.",
        "rt_like_patterns": ["%.p_ac_kw"],
    },
    ("linares", "fv_endesa"): {
        "type": "power",
        "rt_ids": ["uja.linares.fv.endesa.ct_total.p_kw"],
    },
    ("jaen", "fv_auto"): {
        "type": "power",
        "rt_ids": ["uja.jaen.fv.auto.ct_total.p_kw"],
    },
}

BALANCE_SERIES_CONFIG = {
    "jaen": {
        "demand_metric": "energia_consumo",
        "pv_metrics": ["fv_endesa", "fv_auto"],
    },
    "linares": {
        "demand_metric": "energia_consumo",
        "pv_metrics": ["fv_endesa"],
    },
}
BALANCE_SCOPE_CONFIG = {
    "las_lagunillas": {
        "campus": "jaen",
        "label": "Campus Las Lagunillas",
        "demand_sources": [
            {
                "id": "las_lagunillas_demand",
                "label": "Demanda Las Lagunillas",
                "rt_ids": LAS_LAGUNILLAS_DEMAND_RT_IDS,
                "min_items": len(LAS_LAGUNILLAS_DEMAND_RT_IDS),
            },
        ],
        "pv_sources": [
            {
                "id": "jaen_fv_endesa_total",
                "label": "FV Endesa Jaen",
                "rt_ids": JAEN_ENDESA_INVERTER_RT_IDS,
                "min_items": len(JAEN_ENDESA_INVERTER_RT_IDS),
            },
            {
                "id": "jaen_fv_auto_univer",
                "label": "FV autoconsumo UNIVER",
                "rt_ids": ["uja.jaen.fv.auto.ct_total.p_kw"],
                "min_items": 1,
            },
            {
                "id": "jaen_fv_auto_a0",
                "label": "FV edificio A0",
                "rt_ids": ["uja.jaen.fv.auto.edificio_a0.p_kw"],
                "min_items": 1,
            },
        ],
    },
    "ctl_linares": {
        "campus": "linares",
        "label": "Campus CTL Linares",
        "demand_sources": [
            {
                "id": "ctl_linares_demand",
                "label": "Demanda CTL Linares",
                "rt_ids": CTL_LINARES_DEMAND_RT_IDS,
                "min_items": len(CTL_LINARES_DEMAND_RT_IDS),
            },
        ],
        "pv_sources": [
            {
                "id": "linares_fv_endesa_total",
                "label": "FV Endesa Linares",
                "rt_ids": ["uja.linares.fv.endesa.ct_total.p_kw"],
                "min_items": 1,
            },
        ],
    },
}


def handler(event, context):
    path = event.get("path", "")
    if path.startswith("/v1/"):
        path = path[len("/v1") :]
    params = event.get("queryStringParameters") or {}
    multi_params = event.get("multiValueQueryStringParameters") or {}

    if path.endswith("/realtime"):
        return response(get_realtime(params, multi_params))
    if path.endswith("/kpis"):
        return response(get_kpis(params))
    if path.endswith("/aggregates/daily"):
        return response(get_aggregates(params, "daily"))
    if path.endswith("/aggregates/monthly"):
        return response(get_aggregates(params, "monthly"))
    if path.endswith("/aggregates/yearly"):
        return response(get_aggregates(params, "yearly"))
    if path.endswith("/series/24h"):
        if params.get("metric"):
            return response(get_series_24h_by_metric(params))
        if params.get("rt_prefix"):
            return response(get_series_24h_by_prefix(params))
        return response(get_series_24h(params))

    return response({"error": "not_found"}, status=404)


def get_realtime(params, multi_params):
    rt_ids = multi_params.get("rt_id") or []
    if not rt_ids and params.get("rt_id"):
        rt_ids = [params["rt_id"]]
    gateway_id = params.get("gateway_id")

    if rt_ids:
        items = batch_get_latest(rt_ids, gateway_id)
        return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}

    prefix = build_prefix(params.get("campus"), params.get("domain"))
    if not prefix:
        return {"error": "missing_filters"}

    items = scan_latest(prefix, gateway_id)
    return {"ts": int(max([i.get("ts_event", 0) for i in items] or [0])), "items": items}


def batch_get_latest(rt_ids, gateway_id=None):
    keys = [{"rt_id": rt_id} for rt_id in rt_ids]
    response = get_dynamodb().batch_get_item(
        RequestItems={DDB_LATEST_TABLE: {"Keys": keys}}
    )
    items = response.get("Responses", {}).get(DDB_LATEST_TABLE, [])
    normalized = [normalize_item(i) for i in items]
    if gateway_id:
        normalized = [item for item in normalized if item.get("gateway_id") == gateway_id]
    return sorted(normalized, key=lambda x: x["rt_id"])


def scan_latest(prefix, gateway_id=None):
    items = []
    last_key = None
    filter_expression = Attr("rt_id").begins_with(prefix)
    if gateway_id:
        filter_expression = filter_expression & Attr("gateway_id").eq(gateway_id)
    while True:
        kwargs = {"FilterExpression": filter_expression}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_latest_table().scan(**kwargs)
        normalized = [normalize_item(i) for i in response.get("Items", [])]
        if gateway_id:
            normalized = [item for item in normalized if item.get("gateway_id") == gateway_id]
        items.extend(normalized)
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return sorted(items, key=lambda x: x["rt_id"])


def build_prefix(campus, domain):
    if not campus and not domain:
        return None
    if campus and domain:
        return f"uja.{campus}.{domain}."
    if campus:
        return f"uja.{campus}."
    return f"uja..{domain}."


def get_aggregates(params, period):
    campus = params.get("campus")
    metric = params.get("metric")
    asset = params.get("asset", "total")

    if not campus or not metric:
        return {"error": "missing_params"}

    domain, system = metric_to_scope(metric)
    if not domain:
        return {"error": "unsupported_metric"}

    pk = f"{campus}#{domain}#{system}#{period}"
    items = normalize_aggregate_items(query_pk(pk), metric)
    if period == "monthly":
        fallback_items = build_aggregate_fallback_items(campus, metric, period)
        if fallback_items:
            existing_keys = {(item["date"], item["asset"]) for item in items}
            items.extend(
                item
                for item in fallback_items
                if (item["date"], item["asset"]) not in existing_keys
            )
    elif not items:
        items = build_aggregate_fallback_items(campus, metric, period)

    series = []
    for item in items:
        if item.get("asset") != asset:
            continue
        series.append({"date": item["date"], "value": float(item["value"])})

    series.sort(key=lambda x: x["date"])
    unit = items[0].get("unit") if items else infer_aggregate_unit(metric)
    return {
        "campus": campus,
        "metric": metric,
        "period": period,
        "unit": unit,
        "series": series,
    }


def normalize_aggregate_items(items, metric):
    normalized = []
    for item in items or []:
        if "sk" in item:
            sk = item.get("sk", "")
            if "#" not in sk:
                continue
            date, asset = sk.split("#", 1)
            normalized.append(
                {
                    "date": date,
                    "asset": asset,
                    "value": float(item["value"]),
                    "unit": item.get("unit", infer_aggregate_unit(metric)),
                }
            )
            continue

        date = item.get("date")
        if not date:
            continue
        normalized.append(
            {
                "date": date,
                "asset": item.get("asset", "total"),
                "value": float(item["value"]),
                "unit": item.get("unit", infer_aggregate_unit(metric)),
            }
        )
    return normalized


def metric_to_scope(metric):
    mapping = {
        "energia_consumo": ("energia", "consumo"),
        "agua_consumo": ("agua", "consumo"),
        "fv_energia": ("fv", "total"),
        "fv_endesa": ("fv", "endesa"),
        "fv_auto": ("fv", "auto"),
        "co2_evitar": ("co2", "evitar"),
    }
    return mapping.get(metric, (None, None))


def query_pk(pk):
    items = []
    last_key = None
    while True:
        kwargs = {"KeyConditionExpression": Key("pk").eq(pk)}
        if last_key:
            kwargs["ExclusiveStartKey"] = last_key
        response = get_agg_table().query(**kwargs)
        items.extend(response.get("Items", []))
        last_key = response.get("LastEvaluatedKey")
        if not last_key:
            break
    return items


def normalize_item(item):
    value = normalize_rt_value(item["rt_id"], float(item["value"]))
    return {
        "rt_id": item["rt_id"],
        "value": value,
        "unit": item.get("unit"),
        "ts_event": int(item.get("ts_event", 0)),
        "gateway_id": item.get("gateway_id"),
    }


def get_kpis(params):
    scope = params.get("scope")
    if not scope:
        return {"error": "missing_params"}
    state = get_balance_scope_state(scope)
    if not state:
        return {"error": "unsupported_scope"}
    return {
        "scope": scope,
        "campus": state["campus"],
        "label": state["label"],
        "status": state["status"],
        "missing_sources": state["missing_sources"],
        "ts_event": state["ts_event"],
        "kpis": build_scope_kpis(state),
    }


def get_series_24h(params):
    scope = params.get("scope")
    if scope:
        state = get_balance_scope_state(scope, include_series=True)
        if not state:
            return {"error": "unsupported_scope"}
        return {
            "scope": scope,
            "campus": state["campus"],
            "label": state["label"],
            "status": state["status"],
            "missing_sources": state["missing_sources"],
            "interval_minutes": SERIES_INTERVAL_MINUTES,
            "unit": "kW",
            "series": build_scope_series_rows(state),
        }

    campus = params.get("campus", "jaen")
    config = BALANCE_SERIES_CONFIG.get(campus)
    if not config:
        return {"error": "unsupported_campus"}

    demand_series = get_metric_series(campus, config["demand_metric"])
    pv_series = sum_series_maps(
        [get_metric_series(campus, metric) for metric in config["pv_metrics"]]
    )

    all_ts = sorted(set(demand_series) | set(pv_series))
    series = [
        {
            "ts": ts,
            "demand": float(demand_series.get(ts, 0.0)),
            "pv": float(pv_series.get(ts, 0.0)),
        }
        for ts in all_ts
    ]

    return {
        "campus": campus,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": "kW",
        "series": series,
    }


def get_balance_scope_state(scope, include_series=False):
    config = BALANCE_SCOPE_CONFIG.get(scope)
    if not config:
        return None

    sources = []
    for source_type in ("demand_sources", "pv_sources"):
        for source in config.get(source_type, []):
            source_state = get_balance_source_state(source, include_series=include_series)
            source_state["type"] = source_type
            sources.append(source_state)

    missing_sources = [source["id"] for source in sources if not source["complete"]]
    available_sources = [source for source in sources if source["has_any_data"]]
    if not available_sources:
        status = "empty"
    elif missing_sources:
        status = "partial"
    else:
        status = "complete"

    demand_total = sum(
        source["latest_total"]
        for source in sources
        if source["type"] == "demand_sources" and source["complete"]
    )
    pv_total = sum(
        source["latest_total"]
        for source in sources
        if source["type"] == "pv_sources" and source["complete"]
    )
    ts_event = int(max([source["ts_event"] for source in sources] or [0]))

    return {
        "scope": scope,
        "campus": config["campus"],
        "label": config["label"],
        "status": status,
        "missing_sources": missing_sources,
        "ts_event": ts_event,
        "demand_total": demand_total,
        "pv_total": pv_total,
        "sources": sources,
    }


def build_scope_kpis(state):
    if state["status"] != "complete":
        return [
            {"kpi": "demanda_kw", "value": None, "unit": "kW"},
            {"kpi": "fv_kw", "value": None, "unit": "kW"},
            {"kpi": "red_kw", "value": None, "unit": "kW"},
            {"kpi": "autoconsumo_kw", "value": None, "unit": "kW"},
            {"kpi": "autoconsumo_pct", "value": None, "unit": "%"},
        ]

    demand = state["demand_total"]
    pv = state["pv_total"]
    grid = max(demand - pv, 0.0)
    autoconsumo_kw = min(demand, pv)
    autoconsumo_pct = (autoconsumo_kw / demand * 100.0) if demand > 0 else 0.0
    return [
        {"kpi": "demanda_kw", "value": demand, "unit": "kW"},
        {"kpi": "fv_kw", "value": pv, "unit": "kW"},
        {"kpi": "red_kw", "value": grid, "unit": "kW"},
        {"kpi": "autoconsumo_kw", "value": autoconsumo_kw, "unit": "kW"},
        {"kpi": "autoconsumo_pct", "value": autoconsumo_pct, "unit": "%"},
    ]


def build_scope_series_rows(state):
    if state["status"] != "complete":
        return []

    demand_series = sum_series_maps(
        [
            source["series_map"]
            for source in state["sources"]
            if source["type"] == "demand_sources"
        ]
    )
    pv_series = sum_series_maps(
        [
            source["series_map"]
            for source in state["sources"]
            if source["type"] == "pv_sources"
        ]
    )
    all_ts = sorted(set(demand_series) | set(pv_series))
    return [
        {
            "ts": ts,
            "demand": float(demand_series.get(ts, 0.0)),
            "pv": float(pv_series.get(ts, 0.0)),
        }
        for ts in all_ts
    ]


def get_balance_source_state(source, include_series=False):
    latest_items = get_balance_source_latest_items(source)
    min_items = source.get("min_items") or source.get("expected_count") or 1
    latest_complete = len(latest_items) >= min_items
    latest_total = sum(float(item["value"]) for item in latest_items)
    ts_event = int(max([item.get("ts_event", 0) for item in latest_items] or [0]))

    series_map = {}
    series_complete = True
    if include_series and latest_complete:
        series_map = get_balance_source_series_map(source)
        series_complete = bool(series_map)

    complete = latest_complete and series_complete
    return {
        "id": source["id"],
        "label": source["label"],
        "latest_total": latest_total,
        "ts_event": ts_event,
        "series_map": series_map,
        "complete": complete,
        "has_any_data": bool(latest_items) or bool(series_map),
    }


def get_balance_source_latest_items(source):
    if source.get("rt_ids"):
        return batch_get_latest(source["rt_ids"])
    if source.get("metric") and source.get("campus"):
        return get_metric_latest_items(source["campus"], source["metric"])
    rt_prefix = source.get("rt_prefix")
    if not rt_prefix:
        return []
    items = scan_latest(rt_prefix)
    return filter_items_by_patterns(items, source.get("rt_like_patterns"))


def get_balance_source_series_map(source):
    if source.get("rt_ids"):
        return query_timeseries(source["rt_ids"])
    if source.get("metric") and source.get("campus"):
        return get_metric_series(source["campus"], source["metric"]) or {}
    rt_prefix = source.get("rt_prefix")
    if not rt_prefix:
        return {}
    return query_timeseries_by_select(
        rt_prefix=rt_prefix,
        rt_like_patterns=source.get("rt_like_patterns"),
    )


def get_metric_latest_items(campus, metric):
    config = METRIC_SERIES_CONFIG.get((campus, metric))
    if not config:
        return []
    if config.get("rt_ids"):
        return batch_get_latest(config["rt_ids"])
    items = scan_latest(config["rt_prefix"])
    return filter_items_by_patterns(items, config.get("rt_like_patterns"))


def filter_items_by_patterns(items, rt_like_patterns):
    if not rt_like_patterns:
        return items
    return [
        item
        for item in items
        if any(matches_like_pattern(item.get("rt_id", ""), pattern) for pattern in rt_like_patterns)
    ]


def matches_like_pattern(value, pattern):
    translated = pattern.replace("%", "*").replace("_", "?")
    return fnmatchcase(value, translated)


def get_series_24h_by_metric(params):
    campus = params.get("campus")
    metric = params.get("metric")
    if not campus or not metric:
        return {"error": "missing_params"}

    series_map = get_metric_series(campus, metric)
    if series_map is None:
        return {"error": "unsupported_metric"}

    rows = [
        {"ts": ts, "value": float(value)}
        for ts, value in sorted(series_map.items())
    ]
    unit = get_metric_unit(campus, metric)
    return {
        "campus": campus,
        "metric": metric,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": unit,
        "series": rows,
    }


def get_series_24h_by_prefix(params):
    rt_prefix = params.get("rt_prefix")
    if not rt_prefix:
        return {"error": "missing_params"}

    series = query_timeseries_by_prefix(rt_prefix)
    rows = [
        {"ts": ts, "value": float(value)}
        for ts, value in sorted(series.items())
    ]

    return {
        "rt_prefix": rt_prefix,
        "interval_minutes": SERIES_INTERVAL_MINUTES,
        "unit": "kW",
        "series": rows,
    }


def get_metric_series(campus, metric):
    config = METRIC_SERIES_CONFIG.get((campus, metric))
    if not config:
        return None
    if config.get("type") == "counter":
        return query_counter_deltas(
            rt_prefix=config["rt_prefix"],
            rt_like_patterns=config.get("rt_like_patterns"),
            interval=f"{SERIES_INTERVAL_MINUTES}m",
            lookback="24h",
        )
    if config.get("rt_ids"):
        return query_timeseries(config["rt_ids"])
    return query_timeseries_by_select(
        rt_prefix=config["rt_prefix"],
        rt_like_patterns=config.get("rt_like_patterns"),
    )


def sum_series_maps(series_maps):
    result = {}
    for series_map in series_maps:
        if not series_map:
            continue
        for ts, value in series_map.items():
            result[ts] = result.get(ts, 0.0) + value
    return result


def get_metric_unit(campus, metric):
    config = METRIC_SERIES_CONFIG.get((campus, metric), {})
    return config.get("unit", "kW")


def query_timeseries(rt_ids):
    return query_timeseries_by_select(rt_ids=rt_ids)


def query_timeseries_by_prefix(rt_prefix):
    return query_timeseries_by_select(
        rt_prefix=rt_prefix,
        rt_like_patterns=["%.p_%"],
    )


def query_timeseries_by_select(rt_ids=None, rt_prefix=None, rt_like_patterns=None):
    where_clauses = [
        "time > ago(24h)",
        "measure_name = 'value'",
    ]
    if rt_ids:
        in_clause = ",".join([f"'{rt_id}'" for rt_id in rt_ids])
        where_clauses.append(f"rt_id IN ({in_clause})")
    elif rt_prefix:
        where_clauses.append(f"rt_id LIKE '{rt_prefix}%'")
    else:
        return {}

    if rt_like_patterns:
        patterns = " OR ".join([f"rt_id LIKE '{pattern}'" for pattern in rt_like_patterns])
        where_clauses.append(f"({patterns})")

    where_clauses.append(f"measure_value::double <= {MAX_VALID_VALUE}")
    where_clauses.append(f"measure_value::double >= {-MAX_VALID_VALUE}")
    query = f"""
SELECT
  bin(time, {SERIES_INTERVAL_MINUTES}m) AS ts,
  rt_id,
  max_by(measure_value::double, time) AS value
FROM "{TS_DATABASE}"."{TS_TABLE}"
WHERE {" AND ".join(where_clauses)}
GROUP BY rt_id, bin(time, {SERIES_INTERVAL_MINUTES}m)
ORDER BY ts, rt_id
"""
    return rows_to_timeseries_sum_map(query_timestream(query))


def query_counter_deltas(rt_prefix, rt_like_patterns, interval, lookback):
    rows = query_counter_bins(
        rt_prefix=rt_prefix,
        rt_like_patterns=rt_like_patterns,
        interval=interval,
        lookback=lookback,
    )
    by_rt = {}
    totals = {}
    for row in rows:
        data = row.get("Data", [])
        if len(data) < 3:
            continue
        ts_epoch = parse_ts(data[0].get("ScalarValue"))
        rt_id = data[1].get("ScalarValue")
        value_raw = data[2].get("ScalarValue")
        if ts_epoch == 0 or not rt_id or value_raw is None:
            continue
        value = float(value_raw)
        prev_value = by_rt.get(rt_id)
        by_rt[rt_id] = value
        if prev_value is None:
            continue
        delta = max(value - prev_value, 0.0)
        totals[ts_epoch] = totals.get(ts_epoch, 0.0) + delta
    return totals


def query_counter_bins(rt_prefix, rt_like_patterns, interval, lookback):
    where_clauses = [
        f"time > ago({lookback})",
        "measure_name = 'value'",
        f"rt_id LIKE '{rt_prefix}%'",
        f"measure_value::double <= {MAX_VALID_VALUE}",
        "measure_value::double >= 0",
    ]
    if rt_like_patterns:
        patterns = " OR ".join([f"rt_id LIKE '{pattern}'" for pattern in rt_like_patterns])
        where_clauses.append(f"({patterns})")
    query = f"""
SELECT
  bin(time, {interval}) AS ts,
  rt_id,
  max_by(measure_value::double, time) AS value
FROM "{TS_DATABASE}"."{TS_TABLE}"
WHERE {" AND ".join(where_clauses)}
GROUP BY rt_id, bin(time, {interval})
ORDER BY rt_id, ts
"""
    return query_timestream(query)


def build_aggregate_fallback_items(campus, metric, period):
    if period == "monthly":
        return build_monthly_fallback_items(campus, metric)
    if period == "daily" and metric == "agua_consumo":
        return build_daily_water_fallback_items(campus)
    return []


def build_monthly_fallback_items(campus, metric):
    daily_items = build_aggregate_fallback_items(campus, metric, "daily")
    if not daily_items:
        daily_items = query_pk_for_metric(campus, metric, "daily")
    if not daily_items:
        return []

    totals = {}
    for item in daily_items:
        date = item.get("date")
        if not date or len(date) < 7:
            continue
        month = date[:7]
        asset = item.get("asset", "total")
        key = (month, asset)
        totals[key] = totals.get(key, 0.0) + float(item["value"])

    return [
        {"date": month, "asset": asset, "value": value, "unit": infer_aggregate_unit(metric)}
        for (month, asset), value in sorted(totals.items())
    ]


def build_daily_water_fallback_items(campus):
    config = METRIC_SERIES_CONFIG.get((campus, "agua_consumo"))
    if not config:
        return []
    rows = query_daily_counter_consumption(
        rt_prefix=config["rt_prefix"],
        rt_like_patterns=config.get("rt_like_patterns"),
        lookback="45d",
    )
    totals = {}
    for row in rows:
        data = row.get("Data", [])
        if len(data) < 4:
            continue
        day = normalize_day_value(data[0].get("ScalarValue"))
        rt_id = data[1].get("ScalarValue")
        start_raw = data[2].get("ScalarValue")
        end_raw = data[3].get("ScalarValue")
        if not day or not rt_id or start_raw is None or end_raw is None:
            continue
        asset = extract_asset_from_rt_id(rt_id)
        delta = max(float(end_raw) - float(start_raw), 0.0)
        totals[(day, asset)] = totals.get((day, asset), 0.0) + delta
        totals[(day, "total")] = totals.get((day, "total"), 0.0) + delta

    return [
        {"date": day, "asset": asset, "value": value, "unit": "m3"}
        for (day, asset), value in sorted(totals.items())
    ]


def query_daily_counter_consumption(rt_prefix, rt_like_patterns, lookback):
    where_clauses = [
        f"time > ago({lookback})",
        "measure_name = 'value'",
        f"rt_id LIKE '{rt_prefix}%'",
        f"measure_value::double <= {MAX_VALID_VALUE}",
        "measure_value::double >= 0",
    ]
    if rt_like_patterns:
        patterns = " OR ".join([f"rt_id LIKE '{pattern}'" for pattern in rt_like_patterns])
        where_clauses.append(f"({patterns})")
    query = f"""
SELECT
  bin(time, 1d) AS day,
  rt_id,
  min_by(measure_value::double, time) AS start_value,
  max_by(measure_value::double, time) AS end_value
FROM "{TS_DATABASE}"."{TS_TABLE}"
WHERE {" AND ".join(where_clauses)}
GROUP BY rt_id, bin(time, 1d)
ORDER BY day, rt_id
"""
    return query_timestream(query)


def query_pk_for_metric(campus, metric, period):
    domain, system = metric_to_scope(metric)
    if not domain:
        return []
    pk = f"{campus}#{domain}#{system}#{period}"
    items = query_pk(pk)
    normalized = []
    for item in items:
        sk = item.get("sk", "")
        if "#" not in sk:
            continue
        date, asset = sk.split("#", 1)
        normalized.append(
            {
                "date": date,
                "asset": asset,
                "value": float(item["value"]),
                "unit": item.get("unit", infer_aggregate_unit(metric)),
            }
        )
    return normalized


def infer_aggregate_unit(metric):
    if metric == "agua_consumo":
        return "m3"
    return "kWh"


def normalize_day_value(value):
    ts_epoch = parse_ts(value)
    if ts_epoch == 0:
        return None
    return datetime.fromtimestamp(ts_epoch, tz=timezone.utc).strftime("%Y-%m-%d")


def extract_asset_from_rt_id(rt_id):
    parts = rt_id.split(".")
    if len(parts) < 5:
        return rt_id
    return parts[4]


def rows_to_series_map(rows):
    result = {}
    for row in rows:
        data = row.get("Data", [])
        if len(data) < 2:
            continue
        ts_value = data[0].get("ScalarValue")
        value = data[1].get("ScalarValue")
        if ts_value is None or value is None:
            continue
        ts_epoch = parse_ts(ts_value)
        if ts_epoch == 0:
            continue
        result[ts_epoch] = float(value)
    return result


def rows_to_timeseries_sum_map(rows):
    result = {}
    for row in rows:
        data = row.get("Data", [])
        if len(data) < 2:
            continue
        ts_value = data[0].get("ScalarValue")
        ts_epoch = parse_ts(ts_value)
        if ts_epoch == 0:
            continue
        if len(data) >= 3:
            rt_id = data[1].get("ScalarValue")
            value_raw = data[2].get("ScalarValue")
        else:
            rt_id = None
            value_raw = data[1].get("ScalarValue")
        if value_raw is None:
            continue
        value = float(value_raw)
        if rt_id:
            value = normalize_rt_value(rt_id, value)
        result[ts_epoch] = result.get(ts_epoch, 0.0) + value
    return result


def normalize_rt_value(rt_id, value):
    if rt_id in NEGATIVE_TO_ZERO_RT_IDS and value < 0:
        return 0.0
    return value


def get_dynamodb():
    global _dynamodb
    if _dynamodb is None:
        region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION")
        if region:
            _dynamodb = boto3.resource("dynamodb", region_name=region)
        else:
            _dynamodb = boto3.resource("dynamodb")
    return _dynamodb


def get_latest_table():
    global _latest_table
    if _latest_table is None:
        _latest_table = get_dynamodb().Table(DDB_LATEST_TABLE)
    return _latest_table


def get_agg_table():
    global _agg_table
    if _agg_table is None:
        _agg_table = get_dynamodb().Table(DDB_AGG_TABLE)
    return _agg_table


def query_timestream(query):
    client = get_ts_query_client()
    rows = []
    next_token = None
    while True:
        args = {"QueryString": query}
        if next_token:
            args["NextToken"] = next_token
        response = client.query(**args)
        rows.extend(response.get("Rows", []))
        next_token = response.get("NextToken")
        if not next_token:
            break
    return rows


def get_ts_query_client():
    global _ts_query
    if _ts_query is None:
        _ts_query = boto3.client("timestream-query")
    return _ts_query


def parse_ts(ts_value):
    if not ts_value:
        return 0
    ts_value = ts_value.replace("T", " ")
    base = ts_value.split(".")[0]
    try:
        parsed = datetime.strptime(base, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return 0
    return int(parsed.replace(tzinfo=timezone.utc).timestamp())


def response(payload, status=200):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": ALLOWED_ORIGIN,
            "Access-Control-Allow-Methods": "GET,OPTIONS",
        },
        "body": json.dumps(payload),
    }
