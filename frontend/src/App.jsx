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

const CAMPUS_DEMAND_PREFIX = "uja.jaen.energia.consumo.edificio_";
const CAMPUS_VHE_RT_ID = "uja.jaen.energia.consumo.carga_vhe.p_kw";
const CAMPUS_PV_RT_ID = "uja.jaen.fv.auto.edificio_a0.p_kw";

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
  { label: "C4", rtId: "uja.jaen.energia.consumo.um_c4.p_kw", x: 45, y: 78 },
  { label: "C5", rtId: "uja.jaen.energia.consumo.edificio_c5.p_kw", x: 36, y: 79 },
  { label: "C6", rtId: "uja.jaen.energia.consumo.edificio_c6.p_kw", x: 27, y: 85 },
  { label: "D1", rtId: "uja.jaen.energia.consumo.edificio_d1.p_kw", x: 90, y: 54 },
  { label: "D2", rtId: "uja.jaen.energia.consumo.edificio_d2.p_kw", x: 69, y: 67 },
  { label: "D3", rtId: "uja.jaen.energia.consumo.edificio_d3.p_kw", x: 56, y: 74 },
  { label: "D4", rtId: "uja.jaen.energia.consumo.edificio_d4.p_kw", x: 31, y: 95 },
  { label: "Carga VHE", rtId: CAMPUS_VHE_RT_ID, x: 26, y: 67 },
  { label: "Apartamentos", rtId: "uja.jaen.energia.consumo.apartamentos_universitarios.p_kw", x: 38, y: 6 },
  { label: "Residencia", rtId: "uja.jaen.energia.consumo.residencia_domingo_savio.p_kw", x: 62, y: 6 },
  { label: "Polideportivo", rtId: "uja.jaen.energia.consumo.polideportivo.p_kw", x: 48, y: 15 },
  { label: "Magisterio", rtId: "uja.jaen.energia.consumo.ae_magisterio.p_kw", x: 60, y: 95 },
];

const calcTotals = (items) => {
  let demand = 0;
  let pv = 0;

  items.forEach((item) => {
    const value = Number(item.value) || 0;
    if (
      item.rt_id?.startsWith(CAMPUS_DEMAND_PREFIX) ||
      item.rt_id === CAMPUS_VHE_RT_ID
    ) {
      demand += value;
    }
    if (item.rt_id === CAMPUS_PV_RT_ID) {
      pv += value;
    }
  });

  return {
    demand,
    pv,
    grid: demand - pv,
  };
};

const AreaChart = ({ series }) => {
  const chartSeries = useMemo(() => {
    const sorted = [...series].sort((a, b) => a.ts - b.ts);
    if (sorted.length >= 2) return sorted;
    const now = Math.floor(Date.now() / 1000);
    const seed = sorted[0] || { ts: now, demand: 0, pv: 0 };
    return [
      { ...seed, ts: now - 86400 },
      { ...seed, ts: now },
    ];
  }, [series]);

  const maxValue = Math.max(
    1,
    ...chartSeries.map((item) => Math.max(item.demand, item.pv))
  );
  const now = Math.max(
    Math.floor(Date.now() / 1000),
    chartSeries[chartSeries.length - 1]?.ts || 0
  );
  const start = now - 86400;
  const range = 86400;
  const height = 60;

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
    <svg className="area-chart" viewBox="0 0 100 60" role="img">
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

function App() {
  const [realtime, setRealtime] = useState({
    status: "idle",
    data: null,
    error: null,
  });
  const [series24h, setSeries24h] = useState({
    status: "idle",
    data: null,
    error: null,
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
      const payload = await fetchWithFallback(
        "/realtime?campus=jaen&domain=energia"
      );
      setRealtime({ status: "ready", data: payload, error: null });
    } catch (error) {
      setRealtime({ status: "error", data: null, error: error.message });
    }
  };

  const fetchSeries24h = async () => {
    try {
      setSeries24h((prev) => ({ ...prev, status: "loading", error: null }));
      const payload = await fetchWithFallback("/series/24h?campus=jaen");
      setSeries24h({ status: "ready", data: payload, error: null });
    } catch (error) {
      setSeries24h({ status: "error", data: null, error: error.message });
    }
  };

  useEffect(() => {
    fetchRealtime();
    const interval = setInterval(fetchRealtime, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchSeries24h();
    const interval = setInterval(fetchSeries24h, 300000);
    return () => clearInterval(interval);
  }, []);

  const realtimeItems = realtime.data?.items || [];
  const { demand, pv, grid } = useMemo(
    () => calcTotals(realtimeItems),
    [realtimeItems]
  );

  const chartSeries = useMemo(() => {
    const fromApi = series24h.data?.series || [];
    if (fromApi.length) return fromApi;
    const now = Math.floor(Date.now() / 1000);
    return [
      { ts: now - 86400, demand, pv },
      { ts: now, demand, pv },
    ];
  }, [series24h.data, demand, pv]);

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

  return (
    <div className="app">
      <main>
        <section className="section">
          <div className="container">
            <h1 className="section-title">Balance de energia en tiempo real</h1>
            <div className="balance-grid">
              <div className="infographic">
                <div className="metric-card demand">
                  <div className="metric-icon">
                    <IconDemand />
                  </div>
                  <div className="metric-label">Demanda campus</div>
                  <div className="metric-value">
                    {number.format(demand)} kW
                  </div>
                </div>
                <div className="metric-card pv">
                  <div className="metric-icon">
                    <IconSolar />
                  </div>
                  <div className="metric-label">FV campus</div>
                  <div className="metric-value">
                    {number.format(pv)} kW
                  </div>
                </div>
                <div className="metric-card grid">
                  <div className="metric-icon">
                    <IconGrid />
                  </div>
                  <div className="metric-label">Red</div>
                  <div className="metric-value">
                    {number.format(grid)} kW
                  </div>
                </div>
              </div>
              <div className="chart-card">
                <div className="chart-legend">
                  <span className="legend-item demand">Demanda campus</span>
                  <span className="legend-item pv">FV campus</span>
                  <span className="legend-item">24h</span>
                </div>
                <AreaChart series={chartSeries} />
              </div>
            </div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <h2 className="section-title">Mapa del campus</h2>
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
      </main>
    </div>
  );
}

export default App;
