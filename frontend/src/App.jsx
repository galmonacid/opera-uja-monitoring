import { useEffect, useMemo, useState } from "react";
import "./App.css";

import campus from "./assets/sections/campus.png";

const DEFAULT_API_BASE = "https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1";
const API_BASES = [
  import.meta.env.VITE_API_BASE,
  DEFAULT_API_BASE,
].filter(Boolean);

const number = new Intl.NumberFormat("es-ES", {
  maximumFractionDigits: 2,
});

const CAMPUS_VHE_RT_ID = "uja.jaen.energia.consumo.carga_vhe.p_kw";

const MAP_POINTS = [
  { label: "A0", rtId: "uja.jaen.energia.consumo.edificio_a0.p_kw", x: 79, y: 15 },
  { label: "A1", rtId: "uja.jaen.energia.consumo.edificio_a1.p_kw", x: 54, y: 28 },
  { label: "A2", rtId: "uja.jaen.energia.consumo.edificio_a2.p_kw", x: 45, y: 35 },
  { label: "A3", rtId: "uja.jaen.energia.consumo.edificio_a3.p_kw", x: 38, y: 43 },
  { label: "A4", rtId: "uja.jaen.energia.consumo.edificio_a4.p_kw", x: 31, y: 55 },
  { label: "B1", rtId: "uja.jaen.energia.consumo.edificio_b1.p_kw", x: 83, y: 33 },
  { label: "B2", rtId: "uja.jaen.energia.consumo.edificio_b2.p_kw", x: 60, y: 45 },
  { label: "B3", rtId: "uja.jaen.energia.consumo.edificio_b3.p_kw", x: 51, y: 52 },
  { label: "B4", rtId: "uja.jaen.energia.consumo.edificio_b4.p_kw", x: 45, y: 56 },
  { label: "B5", rtId: "uja.jaen.energia.consumo.edificio_b5.p_kw", x: 40, y: 63 },
  { label: "C1", rtId: "uja.jaen.energia.consumo.edificio_c1.p_kw", x: 68, y: 55 },
  { label: "C2", rtId: "uja.jaen.energia.consumo.edificio_c2.p_kw", x: 61, y: 63 },
  { label: "C3", rtId: "uja.jaen.energia.consumo.edificio_c3.p_kw", x: 49, y: 70 },
  { label: "C5", rtId: "uja.jaen.energia.consumo.edificio_c5.p_kw", x: 36, y: 79 },
  { label: "C6", rtId: "uja.jaen.energia.consumo.edificio_c6.p_kw", x: 27, y: 85 },
  { label: "D1", rtId: "uja.jaen.energia.consumo.edificio_d1.p_kw", x: 90, y: 54 },
  { label: "D2", rtId: "uja.jaen.energia.consumo.edificio_d2.p_kw", x: 69, y: 67 },
  { label: "D3", rtId: "uja.jaen.energia.consumo.edificio_d3.p_kw", x: 56, y: 74 },
  { label: "D4", rtId: "uja.jaen.energia.consumo.edificio_d4.p_kw", x: 31, y: 95 },
  { label: "Carga VHE", rtId: CAMPUS_VHE_RT_ID, x: 26, y: 67 },
];
const DASHBOARD_SCOPES = [
  { id: "las_lagunillas", title: "Campus Las Lagunillas" },
  { id: "ctl_linares", title: "Campus CTL Linares" },
];
const MISSING_SOURCE_LABELS = {
  las_lagunillas_demand: "demanda Las Lagunillas",
  jaen_fv_endesa_total: "FV Endesa Jaen",
  jaen_fv_auto_univer: "FV autoconsumo UNIVER",
  jaen_fv_auto_a0: "FV edificio A0",
  ctl_linares_demand: "demanda CTL Linares",
  linares_fv_endesa_total: "FV Endesa Linares",
};

const GATEWAYS = [
  {
    id: "gw_jaen_energia",
    label: "gw_jaen_energia",
    topic: "uja/jaen/consumo/energia/gw_jaen_energia",
    gatewayId: "gw_jaen_energia",
    campus: "jaen",
    domain: null,
    rtPrefixes: ["uja.jaen.energia.", "uja.jaen.fv.auto."],
    seriesMetric: "energia_consumo",
    aggregateMetric: "energia_consumo",
  },
  {
    id: "gw_jaen_agua",
    label: "gw_jaen_agua",
    topic: "uja/jaen/consumo/agua/gw_jaen_agua",
    gatewayId: "gw_jaen_agua",
    campus: "jaen",
    domain: "agua",
    rtPrefixes: ["uja.jaen.agua."],
    seriesMetric: "agua_consumo",
    aggregateMetric: "agua_consumo",
  },
  {
    id: "gw_linares_mix",
    label: "gw_linares_mix",
    topic: "uja/linares/consumo/mix/gw_linares_mix",
    gatewayId: "gw_linares_mix",
    campus: "linares",
    domain: null,
    rtPrefixes: ["uja.linares.agua.", "uja.linares.energia."],
    seriesMetric: "energia_consumo",
    aggregateMetric: "energia_consumo",
  },
  {
    id: "gw_endesa_jaen",
    label: "gw_endesa_jaen",
    topic: "uja/jaen/produccion/fv_endesa/gw_endesa_jaen",
    gatewayId: "gw_endesa_jaen",
    campus: "jaen",
    domain: "fv",
    rtPrefixes: ["uja.jaen.fv.endesa."],
    seriesMetric: "fv_endesa",
    aggregateMetric: "fv_endesa",
  },
  {
    id: "gw_endesa_linares",
    label: "gw_endesa_linares",
    topic: "uja/linares/produccion/fv_endesa/gw_endesa_linares",
    gatewayId: "gw_endesa_linares",
    campus: "linares",
    domain: "fv",
    rtPrefixes: ["uja.linares.fv.endesa."],
    seriesMetric: "fv_endesa",
    aggregateMetric: "fv_endesa",
  },
  {
    id: "gw_autoconsumo_jaen",
    label: "gw_autoconsumo_jaen",
    topic: "uja/jaen/produccion/fv_autoconsumo/gw_autoconsumo_jaen",
    gatewayId: "gw_autoconsumo_jaen",
    campus: "jaen",
    domain: "fv",
    rtPrefixes: ["uja.jaen.fv.auto."],
    seriesMetric: "fv_auto",
    aggregateMetric: "fv_auto",
  },
];

const formatTs = (ts) => {
  if (!ts && ts !== 0) return "--";
  const value = Number(ts);
  if (!Number.isFinite(value)) return "--";
  return new Date(value * 1000).toLocaleString("es-ES");
};

const formatDate = (value) => {
  if (!value) return "--";
  if (typeof value === "string" && value.includes("-")) {
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) {
      return parsed.toLocaleDateString("es-ES");
    }
    return value;
  }
  if (typeof value === "number") {
    return new Date(value * 1000).toLocaleString("es-ES");
  }
  return value;
};

const filterByPrefixes = (items, prefixes) =>
  items.filter((item) =>
    prefixes.some((prefix) => item.rt_id?.startsWith(prefix))
  );

const aggregateLabels = (metric) => {
  if (metric === "agua_consumo") {
    return { daily: "Agua diaria", monthly: "Agua mensual" };
  }
  if (metric === "fv_endesa" || metric === "fv_auto") {
    return { daily: "Producción diaria", monthly: "Producción mensual" };
  }
  return { daily: "Energía diaria", monthly: "Energía mensual" };
};

const readKpiValue = (data, kpi) =>
  data?.kpis?.find((item) => item.kpi === kpi)?.value ?? null;

const uniq = (values) => Array.from(new Set(values));

const resolveDashboardStatus = (kpisState, seriesState) => {
  if (kpisState?.status === "error" || seriesState?.status === "error") {
    return { kind: "error", label: "Error" };
  }
  if (kpisState?.status === "loading" || seriesState?.status === "loading") {
    return { kind: "loading", label: "Cargando" };
  }
  const apiStatuses = [kpisState?.data?.status, seriesState?.data?.status].filter(Boolean);
  if (!apiStatuses.length) {
    return { kind: "idle", label: "Sin datos" };
  }
  if (apiStatuses.includes("partial")) {
    return { kind: "partial", label: "Datos parciales" };
  }
  if (apiStatuses.every((status) => status === "empty")) {
    return { kind: "empty", label: "Sin datos" };
  }
  if (apiStatuses.every((status) => status === "complete")) {
    return { kind: "complete", label: "Datos completos" };
  }
  return { kind: "idle", label: "Sin datos" };
};

const buildMissingSourcesText = (kpisState, seriesState) => {
  const ids = uniq([
    ...(kpisState?.data?.missing_sources || []),
    ...(seriesState?.data?.missing_sources || []),
  ]);
  if (!ids.length) return null;
  const labels = ids.map((id) => MISSING_SOURCE_LABELS[id] || id);
  return `Datos incompletos: faltan ${labels.join(", ")}.`;
};

const AreaChart = ({ series }) => {
  const [renderNow] = useState(() => Math.floor(Date.now() / 1000));
  const chartSeries = useMemo(() => {
    const sorted = [...series].sort((a, b) => a.ts - b.ts);
    if (sorted.length >= 2) return sorted;
    const seed = sorted[0] || { ts: renderNow, demand: 0, pv: 0 };
    return [
      { ...seed, ts: renderNow - 86400 },
      { ...seed, ts: renderNow },
    ];
  }, [renderNow, series]);

  const maxValue = Math.max(
    1,
    ...chartSeries.map((item) => Math.max(item.demand, item.pv))
  );
  const now = Math.max(
    renderNow,
    chartSeries[chartSeries.length - 1]?.ts || 0
  );
  const start = now - 86400;
  const range = 86400;
  const height = 60;
  const ticksY = 4;
  const ticksX = [0, 6, 12, 18, 24];

  const formatHour = (hoursAgo) => {
    const date = new Date((now - hoursAgo * 3600) * 1000);
    const hh = String(date.getHours()).padStart(2, "0");
    return `${hh}:00`;
  };

  const buildPath = (key) => {
    const points = chartSeries.map((item) => {
      const x = ((item.ts - start) / range) * 100;
      const y = height - (item[key] / maxValue) * height;
      return [x, y];
    });
    const line = points.map(([x, y]) => `${x.toFixed(2)},${y.toFixed(2)}`).join(" ");
    const area = `M ${line} L 100,${height} L 0,${height} Z`;
    return { line, area };
  };

  const demandPath = buildPath("demand");
  const pvPath = buildPath("pv");

  return (
    <svg className="area-chart" viewBox="-12 0 112 60" role="img">
      <g className="axis axis-y">
        {Array.from({ length: ticksY + 1 }).map((_, idx) => {
          const y = (height / ticksY) * idx;
          const value = maxValue - (maxValue / ticksY) * idx;
          return (
            <g key={`y-${idx}`} transform={`translate(0, ${y})`}>
              <line className="axis-line" x1="0" x2="100" y1="0" y2="0" />
              <text className="axis-label axis-label-y" x="-2" y="-1">
                {number.format(Math.round(value / 100) * 100)}
              </text>
            </g>
          );
        })}
      </g>
      <g className="axis axis-x">
        {ticksX.map((hours) => {
          const x = (hours / 24) * 100;
          return (
            <g key={`x-${hours}`} transform={`translate(${x}, ${height})`}>
              <line className="axis-tick" x1="0" x2="0" y1="0" y2="2" />
              <text className="axis-label" x="0" y="6">
                {formatHour(24 - hours)}
              </text>
            </g>
          );
        })}
      </g>
      <path className="area area-demand" d={demandPath.area} />
      <path className="area area-pv" d={pvPath.area} />
      <polyline className="line line-demand" points={demandPath.line} />
      <polyline className="line line-pv" points={pvPath.line} />
    </svg>
  );
};

const IconDemand = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M4 18h16M6 18V8l6-4 6 4v10"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
    <path
      d="M9 18v-4h6v4"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
      strokeLinejoin="round"
    />
  </svg>
);

const IconSolar = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <circle cx="12" cy="12" r="4" fill="none" stroke="currentColor" strokeWidth="1.8" />
    <path
      d="M12 2v3M12 19v3M2 12h3M19 12h3M4.5 4.5l2.2 2.2M17.3 17.3l2.2 2.2M4.5 19.5l2.2-2.2M17.3 6.7l2.2-2.2"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
    />
  </svg>
);

const IconGrid = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M7 22V4M17 22V4M4 8h16M4 14h16"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

const IconAutoconsumo = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M12 3a9 9 0 1 0 9 9"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
    <path
      d="M12 12l5-5"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinecap="round"
    />
  </svg>
);

function App() {
  const [route, setRoute] = useState(() => window.location.hash || "#/");
  const [realtime, setRealtime] = useState({
    status: "idle",
    data: null,
    error: null,
  });
  const [dashboard, setDashboard] = useState(() => {
    const initial = {};
    DASHBOARD_SCOPES.forEach((scope) => {
      initial[scope.id] = {
        kpis: { status: "idle", data: null, error: null },
        series: { status: "idle", data: null, error: null },
      };
    });
    return initial;
  });
  const [validation, setValidation] = useState(() => {
    const initial = {};
    GATEWAYS.forEach((gateway) => {
      initial[gateway.id] = {
        latest: { status: "idle", data: null, error: null },
        series: { status: "idle", data: null, error: null },
        daily: { status: "idle", data: null, error: null },
        monthly: { status: "idle", data: null, error: null },
      };
    });
    return initial;
  });

  const fetchWithFallback = async (path) => {
    let lastError = null;
    for (const base of API_BASES) {
      try {
        const response = await fetch(`${base}${path}`);
        const payload = await response.json();
        if (!response.ok || payload.error) {
          throw new Error(payload.error || "api_error");
        }
        return payload;
      } catch (error) {
        lastError = error;
      }
    }
    throw lastError || new Error("api_error");
  };

  const fetchRealtime = async () => {
    try {
      setRealtime((prev) => ({ ...prev, status: "loading", error: null }));
      const payload = await fetchWithFallback("/realtime?campus=jaen");
      setRealtime({ status: "ready", data: payload, error: null });
    } catch (error) {
      setRealtime({ status: "error", data: null, error: error.message });
    }
  };

  const fetchDashboardKpis = async (scope) => {
    try {
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          kpis: { ...prev[scope.id].kpis, status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(`/kpis?scope=${scope.id}`);
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          kpis: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          kpis: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const fetchDashboardSeries = async (scope) => {
    try {
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          series: { ...prev[scope.id].series, status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(`/series/24h?scope=${scope.id}`);
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          series: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setDashboard((prev) => ({
        ...prev,
        [scope.id]: {
          ...prev[scope.id],
          series: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const fetchGatewayLatest = async (gateway) => {
    try {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          latest: { ...prev[gateway.id].latest, status: "loading", error: null },
        },
      }));
      const params = new URLSearchParams({ campus: gateway.campus });
      if (gateway.domain) params.set("domain", gateway.domain);
      if (gateway.gatewayId) params.set("gateway_id", gateway.gatewayId);
      const query = `/realtime?${params.toString()}`;
      const payload = await fetchWithFallback(query);
      const items = filterByPrefixes(payload.items || [], gateway.rtPrefixes);
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          latest: {
            status: "ready",
            data: { ...payload, items },
            error: null,
          },
        },
      }));
    } catch (error) {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          latest: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const fetchGatewaySeries = async (gateway) => {
    if (!gateway.seriesMetric) {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          series: { status: "na", data: null, error: null },
        },
      }));
      return;
    }
    try {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          series: { ...prev[gateway.id].series, status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(
        `/series/24h?campus=${gateway.campus}&metric=${gateway.seriesMetric}`
      );
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          series: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          series: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const fetchGatewayAggregates = async (gateway, period) => {
    if (!gateway.aggregateMetric) {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          [period]: { status: "na", data: null, error: null },
        },
      }));
      return;
    }
    try {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          [period]: { ...prev[gateway.id][period], status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(
        `/aggregates/${period}?campus=${gateway.campus}&metric=${gateway.aggregateMetric}&asset=total`
      );
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          [period]: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setValidation((prev) => ({
        ...prev,
        [gateway.id]: {
          ...prev[gateway.id],
          [period]: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  useEffect(() => {
    fetchRealtime();
    const interval = setInterval(fetchRealtime, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    DASHBOARD_SCOPES.forEach((scope) => {
      fetchDashboardKpis(scope);
    });
    const interval = setInterval(() => {
      DASHBOARD_SCOPES.forEach((scope) => {
        fetchDashboardKpis(scope);
      });
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    DASHBOARD_SCOPES.forEach((scope) => {
      fetchDashboardSeries(scope);
    });
    const interval = setInterval(() => {
      DASHBOARD_SCOPES.forEach((scope) => {
        fetchDashboardSeries(scope);
      });
    }, 300000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    const handleHash = () => setRoute(window.location.hash || "#/");
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  useEffect(() => {
    if (route !== "#/validacion") return;
    GATEWAYS.forEach((gateway) => {
      fetchGatewayLatest(gateway);
      fetchGatewaySeries(gateway);
      fetchGatewayAggregates(gateway, "daily");
      fetchGatewayAggregates(gateway, "monthly");
    });
  }, [route]);

  const refreshDashboard = () => {
    DASHBOARD_SCOPES.forEach((scope) => {
      fetchDashboardKpis(scope);
      fetchDashboardSeries(scope);
    });
  };

  const refreshValidation = () => {
    GATEWAYS.forEach((gateway) => {
      fetchGatewayLatest(gateway);
      fetchGatewaySeries(gateway);
      fetchGatewayAggregates(gateway, "daily");
      fetchGatewayAggregates(gateway, "monthly");
    });
  };

  const realtimeItems = useMemo(() => realtime.data?.items || [], [realtime.data]);

  const realtimeMap = useMemo(() => {
    const map = new Map();
    realtimeItems.forEach((item) => map.set(item.rt_id, item));
    return map;
  }, [realtimeItems]);

  const readValue = (rtId) => {
    const item = realtimeMap.get(rtId);
    if (!item) return null;
    return { value: item.value, unit: item.unit || "kW" };
  };

  const renderStatus = (state) => {
    if (state.status === "na") return "No disponible";
    if (state.status === "loading") return "Cargando...";
    if (state.status === "error") return `Error: ${state.error}`;
    if (state.status === "ready") return "OK";
    return "Sin datos";
  };

  const renderTable = (columns, rows) => {
    if (!rows.length) {
      return <div className="api-empty">No hay registros</div>;
    }
    return (
      <div className="api-table">
        <table>
          <thead>
            <tr>
              {columns.map((col) => (
                <th key={col}>{col}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, idx) => (
              <tr key={`${row[0]}-${idx}`}>
                {row.map((cell, cellIdx) => (
                  <td key={`${idx}-${cellIdx}`}>{cell}</td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  };

  const buildGatewayTables = (gateway) => {
    const labels = aggregateLabels(gateway.aggregateMetric);
    const state = validation[gateway.id] || {};
    const latestItems = state.latest?.data?.items || [];
    const latestRows = latestItems.map((item) => [
      item.rt_id,
      number.format(item.value),
      item.unit || "kW",
      formatTs(item.ts_event),
    ]);

    const seriesItems = state.series?.data?.series || [];
    const usesValueSeries = Boolean(state.series?.data?.metric || state.series?.data?.rt_prefix);
    const seriesUnit = state.series?.data?.unit || "kW";
    const seriesRowsLocal = usesValueSeries
      ? seriesItems.map((item) => [
          formatTs(item.ts),
          number.format(item.value),
          seriesUnit,
        ])
      : seriesItems.map((item) => [
          formatTs(item.ts),
          number.format(item.demand),
          "kW",
          number.format(item.pv),
          "kW",
        ]);

    const dailyRows = (state.daily?.data?.series || []).map((item) => [
      formatDate(item.date || item.ts || "--"),
      number.format(item.value),
      state.daily?.data?.unit || "--",
    ]);

    const monthlyRows = (state.monthly?.data?.series || []).map((item) => [
      formatDate(item.date || item.ts || "--"),
      number.format(item.value),
      state.monthly?.data?.unit || "--",
    ]);

    return (
      <div key={gateway.id} className="gateway-card">
        <div className="gateway-header">
          <div>
            <h2 className="gateway-title">{gateway.label}</h2>
            <div className="gateway-topic">{gateway.topic}</div>
          </div>
          <button
            className="api-refresh"
            type="button"
            onClick={() => {
              fetchGatewayLatest(gateway);
              fetchGatewaySeries(gateway);
              fetchGatewayAggregates(gateway, "daily");
              fetchGatewayAggregates(gateway, "monthly");
            }}
          >
            Actualizar
          </button>
        </div>
        <div className="gateway-grid">
          <div className="api-card">
            <div className="api-card-title">Último valor disponible</div>
            <div className={`api-status status-${state.latest?.status}`}>
              {renderStatus(state.latest || {})}
            </div>
            {renderTable(["rt_id", "value", "unit", "ts_event"], latestRows)}
          </div>
          <div className="api-card">
            <div className="api-card-title">Últimas 24 horas</div>
            <div className={`api-status status-${state.series?.status}`}>
              {renderStatus(state.series || {})}
            </div>
            {renderTable(
              usesValueSeries
                ? ["ts", "value", "unit"]
                : ["ts", "demand", "unit", "pv", "unit"],
              seriesRowsLocal
            )}
          </div>
          <div className="api-card">
            <div className="api-card-title">{labels.daily}</div>
            <div className={`api-status status-${state.daily?.status}`}>
              {renderStatus(state.daily || {})}
            </div>
            {renderTable(["date", "value", "unit"], dailyRows)}
          </div>
          <div className="api-card">
            <div className="api-card-title">{labels.monthly}</div>
            <div className={`api-status status-${state.monthly?.status}`}>
              {renderStatus(state.monthly || {})}
            </div>
            {renderTable(["date", "value", "unit"], monthlyRows)}
          </div>
        </div>
      </div>
    );
  };

  const buildDashboardPanel = (scope) => {
    const state = dashboard[scope.id] || {};
    const panelStatus = resolveDashboardStatus(state.kpis || {}, state.series || {});
    const isComplete = panelStatus.kind === "complete";
    const warningText = buildMissingSourcesText(state.kpis || {}, state.series || {});
    const errorText = state.kpis?.error || state.series?.error || "api_error";
    const title = state.kpis?.data?.label || state.series?.data?.label || scope.title;
    const chartSeries = isComplete ? state.series?.data?.series || [] : [];
    const demand = isComplete ? readKpiValue(state.kpis?.data, "demanda_kw") : null;
    const pv = isComplete ? readKpiValue(state.kpis?.data, "fv_kw") : null;
    const grid = isComplete ? readKpiValue(state.kpis?.data, "red_kw") : null;
    const autoconsumoPct = isComplete
      ? readKpiValue(state.kpis?.data, "autoconsumo_pct")
      : null;

    let chartEmptyText = "Sin datos para las últimas 24 horas.";
    if (panelStatus.kind === "loading") {
      chartEmptyText = "Cargando serie de las últimas 24 horas...";
    } else if (panelStatus.kind === "partial") {
      chartEmptyText = warningText || "Faltan fuentes requeridas para reconstruir la curva.";
    } else if (panelStatus.kind === "error") {
      chartEmptyText = `Error: ${errorText}`;
    }

    const formatValue = (value, unit) =>
      value == null ? "--" : `${number.format(value)} ${unit}`;

    return (
      <article key={scope.id} className={`dashboard-panel panel-${panelStatus.kind}`}>
        <div className="dashboard-panel-header">
          <div>
            <h2 className="dashboard-panel-title">{title}</h2>
            <div className={`dashboard-status status-${panelStatus.kind}`}>
              {panelStatus.label}
            </div>
          </div>
          <button
            className="api-refresh"
            type="button"
            onClick={() => {
              fetchDashboardKpis(scope);
              fetchDashboardSeries(scope);
            }}
          >
            Actualizar
          </button>
        </div>
        {warningText && panelStatus.kind === "partial" ? (
          <div className="dashboard-warning">{warningText}</div>
        ) : null}
        {panelStatus.kind === "error" ? (
          <div className="dashboard-warning warning-error">Error: {errorText}</div>
        ) : null}
        <div className="balance-grid">
          <div className="infographic">
            <div className="metric-card demand">
              <div className="metric-icon">
                <IconDemand />
              </div>
              <div className="metric-label">Demanda</div>
              <div className="metric-value">{formatValue(demand, "kW")}</div>
            </div>
            <div className="metric-card pv">
              <div className="metric-icon">
                <IconSolar />
              </div>
              <div className="metric-label">Generación FV</div>
              <div className="metric-value">{formatValue(pv, "kW")}</div>
            </div>
            <div className="metric-card grid">
              <div className="metric-icon">
                <IconGrid />
              </div>
              <div className="metric-label">Red</div>
              <div className="metric-value">{formatValue(grid, "kW")}</div>
            </div>
            <div className="metric-card autoconsumo">
              <div className="metric-icon">
                <IconAutoconsumo />
              </div>
              <div className="metric-label">Autoconsumo</div>
              <div className="metric-value">{formatValue(autoconsumoPct, "%")}</div>
            </div>
          </div>
          <div className="chart-card">
            <div className="chart-legend">
              <span className="legend-item demand">Curva Demanda kW</span>
              <span className="legend-item pv">Curva Generación kW</span>
            </div>
            {isComplete && chartSeries.length ? (
              <AreaChart series={chartSeries} />
            ) : (
              <div className="chart-empty">{chartEmptyText}</div>
            )}
          </div>
        </div>
      </article>
    );
  };

  const isValidation = route === "#/validacion";

  return (
    <div className="app">
      <header className="topbar">
        <div className="container topbar-inner">
          <div className="topbar-brand">UJA Monitoring</div>
          <nav className="topbar-nav">
            <a
              className={`topbar-link ${!isValidation ? "active" : ""}`}
              href="#/"
            >
              Dashboard
            </a>
            <a
              className={`topbar-link ${isValidation ? "active" : ""}`}
              href="#/validacion"
            >
              Validación de datos
            </a>
          </nav>
        </div>
      </header>
      <main>
        {isValidation ? (
          <section className="section">
            <div className="container">
              <div className="api-header">
                <h1 className="section-title">Validación de datos</h1>
                <button
                  className="api-refresh"
                  type="button"
                  onClick={refreshValidation}
                >
                  Actualizar todo
                </button>
              </div>
              <p className="api-subtitle">
                Vista técnica por gateway para validar ingestión, series y agregados.
              </p>
              <div className="gateway-stack">
                {GATEWAYS.map((gateway) => buildGatewayTables(gateway))}
              </div>
            </div>
          </section>
        ) : (
          <>
            <section className="section">
              <div className="container">
                <div className="api-header">
                  <h1 className="section-title">Balance de energia en tiempo real</h1>
                  <button
                    className="api-refresh"
                    type="button"
                    onClick={refreshDashboard}
                  >
                    Actualizar paneles
                  </button>
                </div>
                <p className="api-subtitle">
                  Balance operativo separado para Las Lagunillas y CTL Linares.
                </p>
                <div className="dashboard-panels">
                  {DASHBOARD_SCOPES.map((scope) => buildDashboardPanel(scope))}
                </div>
              </div>
            </section>

            <section className="section">
              <div className="container">
                <h2 className="section-title">Mapa de Las Lagunillas</h2>
                <div className="map-frame">
                  <img src={campus} alt="Mapa campus" />
                  {MAP_POINTS.map((point) => {
                    const reading = readValue(point.rtId);
                    const valueText = reading
                      ? `${number.format(reading.value)} ${reading.unit}`
                      : "--";
                    return (
                      <div
                        key={point.label}
                        className="map-pin"
                        style={{ left: `${point.x}%`, top: `${point.y}%` }}
                        aria-label={`${point.label} ${valueText}`}
                      >
                        <div className="map-pin-label">{point.label}</div>
                        <div className="map-pin-value">{valueText}</div>
                      </div>
                    );
                  })}
                </div>
              </div>
            </section>
          </>
        )}
      </main>
    </div>
  );
}

export default App;
