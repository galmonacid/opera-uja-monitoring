import math


ALLOWED_NEGATIVE_RT_IDS = {
    "uja.jaen.fv.endesa.ct_total.p_kw",
}

NEGATIVE_TO_ZERO_RT_IDS = {
    "uja.jaen.fv.auto.ct_total.p_kw",
}


def derive_rt_metadata(rt_id):
    parts = str(rt_id or "").split(".")
    return {
        "campus": parts[1] if len(parts) > 1 else "unknown",
        "domain": parts[2] if len(parts) > 2 else "unknown",
        "system": parts[3] if len(parts) > 3 else "unknown",
        "asset": parts[4] if len(parts) > 4 else "unknown",
    }


def threshold_for_unit(unit, max_valid_value, max_valid_value_kwh):
    unit_value = str(unit or "").strip().lower()
    if unit_value == "kwh":
        return float(max_valid_value_kwh)
    return float(max_valid_value)


def is_negative_not_allowed(rt_id, unit=None):
    rt_id = str(rt_id or "")
    if rt_id in ALLOWED_NEGATIVE_RT_IDS:
        return False
    if ".energia.consumo." in rt_id:
        return True
    if ".agua.consumo." in rt_id:
        return True
    if ".fv." in rt_id and (rt_id.endswith(".p_kw") or rt_id.endswith(".p_ac_kw")):
        return True
    return False


def detect_anomaly(rt_id, value, unit=None, max_valid_value=1000000, max_valid_value_kwh=1000000000):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return {
            "anomaly_type": "non_finite",
            "reason": "Valor no numérico o ausente.",
            "threshold": None,
        }

    if not math.isfinite(numeric):
        return {
            "anomaly_type": "non_finite",
            "reason": "Valor no finito (NaN o infinito).",
            "threshold": None,
        }

    threshold = threshold_for_unit(unit, max_valid_value, max_valid_value_kwh)
    if abs(numeric) > threshold:
        return {
            "anomaly_type": "above_max_threshold",
            "reason": f"Valor fuera de umbral máximo ({threshold:g}).",
            "threshold": threshold,
        }

    if numeric < 0 and is_negative_not_allowed(rt_id, unit):
        return {
            "anomaly_type": "negative_not_allowed",
            "reason": "Valor negativo no permitido para este punto.",
            "threshold": 0.0,
        }

    return None


def normalize_sentinel_value(rt_id, value):
    numeric = float(value)
    if rt_id in NEGATIVE_TO_ZERO_RT_IDS and numeric < 0:
        return 0.0
    return numeric


def sanitize_for_analytics(rt_id, value, unit=None, max_valid_value=1000000, max_valid_value_kwh=1000000000):
    anomaly = detect_anomaly(
        rt_id,
        value,
        unit=unit,
        max_valid_value=max_valid_value,
        max_valid_value_kwh=max_valid_value_kwh,
    )
    if anomaly is None:
        return True, float(value), None

    if anomaly["anomaly_type"] == "negative_not_allowed" and rt_id in NEGATIVE_TO_ZERO_RT_IDS:
        return True, 0.0, anomaly

    return False, None, anomaly


def format_anomaly_value(value):
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None if value is None else str(value)
    if not math.isfinite(numeric):
        if math.isnan(numeric):
            return "NaN"
        return "Infinity" if numeric > 0 else "-Infinity"
    return f"{numeric:.6f}".rstrip("0").rstrip(".")


def build_anomaly_event_key(ts_event, rt_id, anomaly_type):
    return f"{int(ts_event):013d}#{rt_id}#{anomaly_type}"

