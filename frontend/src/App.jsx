import { useEffect, useMemo, useState } from "react";
import "./App.css";

import section1 from "./assets/sections/section-1.png";
import section2 from "./assets/sections/section-2.png";
import section3 from "./assets/sections/section-3.png";
import section4 from "./assets/sections/section-4.png";
import section5 from "./assets/sections/section-5.png";
import campus from "./assets/sections/campus.png";

const API_BASE =
  import.meta.env.VITE_API_BASE ||
  "https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1";

const number = new Intl.NumberFormat("es-ES", {
  maximumFractionDigits: 2,
});

const shortRt = (rtId = "") => {
  const parts = rtId.split(".");
  return parts.slice(-2).join(" ").replace(/_/g, " ");
};

const Sparkline = ({ series }) => {
  if (!series.length) {
    return (
      <svg className="sparkline" viewBox="0 0 100 100" role="img">
        <polyline
          points="0,70 25,68 50,72 75,67 100,70"
          fill="none"
          stroke="rgba(23,22,20,0.18)"
          strokeWidth="3"
        />
      </svg>
    );
  }

  const values = series.map((item) => item.value);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const range = max - min || 1;

  const points = series.map((item, index) => {
    const x = (index / (series.length - 1 || 1)) * 100;
    const y = 100 - ((item.value - min) / range) * 80 - 10;
    return `${x.toFixed(2)},${y.toFixed(2)}`;
  });

  return (
    <svg className="sparkline" viewBox="0 0 100 100" role="img">
      <polyline
        points={points.join(" ")}
        fill="none"
        stroke="#d44f2a"
        strokeWidth="3"
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
  );
};

function App() {
  const [viewMode, setViewMode] = useState("functional");
  const [realtime, setRealtime] = useState({
    status: "idle",
    data: null,
    error: null,
  });
  const [daily, setDaily] = useState({ status: "idle", data: null, error: null });

  const fetchRealtime = async () => {
    try {
      setRealtime((prev) => ({ ...prev, status: "loading", error: null }));
      const response = await fetch(
        `${API_BASE}/realtime?campus=jaen&domain=energia`
      );
      const payload = await response.json();
      if (!response.ok || payload.error) {
        throw new Error(payload.error || "realtime_error");
      }
      setRealtime({ status: "ready", data: payload, error: null });
    } catch (error) {
      setRealtime({ status: "error", data: null, error: error.message });
    }
  };

  const fetchDaily = async () => {
    try {
      setDaily((prev) => ({ ...prev, status: "loading", error: null }));
      const response = await fetch(
        `${API_BASE}/aggregates/daily?campus=jaen&metric=energia_consumo&asset=total`
      );
      const payload = await response.json();
      if (!response.ok || payload.error) {
        throw new Error(payload.error || "daily_error");
      }
      setDaily({ status: "ready", data: payload, error: null });
    } catch (error) {
      setDaily({ status: "error", data: null, error: error.message });
    }
  };

  useEffect(() => {
    fetchRealtime();
    const interval = setInterval(fetchRealtime, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchDaily();
  }, []);

  const realtimeItems = realtime.data?.items || [];
  const dailySeries = daily.data?.series || [];
  const trimmedSeries = dailySeries.slice(-7);

  const totalToday = useMemo(() => {
    if (!trimmedSeries.length) return null;
    return trimmedSeries[trimmedSeries.length - 1].value;
  }, [trimmedSeries]);

  const lastUpdate = realtime.data?.ts
    ? new Date(realtime.data.ts * 1000).toLocaleTimeString("es-ES")
    : "-";

  return (
    <div className="app">
      <header className="navbar">
        <div className="container navbar-inner">
          <div className="brand">
            <span className="brand-mark" />
            <div>
              <div>UJA Monitoring</div>
              <small>Energia · Agua · FV</small>
            </div>
          </div>
          <nav className="nav-links">
            <a href="#energia">Energia</a>
            <a href="#mapa">Mapa</a>
            <a href="#agua">Agua</a>
            <a href="#fv">FV</a>
            <a href="#indicadores">Indicadores</a>
          </nav>
          <div className="view-toggle">
            <button
              type="button"
              className={viewMode === "functional" ? "active" : ""}
              onClick={() => setViewMode("functional")}
            >
              Funcional
            </button>
            <button
              type="button"
              className={viewMode === "pixel" ? "active" : ""}
              onClick={() => setViewMode("pixel")}
            >
              Pixel match
            </button>
          </div>
        </div>
      </header>

      {viewMode === "pixel" ? (
        <main className="pixel">
          <section id="energia" className="pm-section">
            <div className="container">
              <div className="pm-header">
                <div className="eyebrow">Pagina 1</div>
                <h2>Consumo energetico</h2>
                <p>Pixel-match del layout original.</p>
              </div>
              <div className="pm-frame">
                <img src={section1} alt="Pagina 1 energia" />
              </div>
            </div>
          </section>

          <section id="mapa" className="pm-section">
            <div className="container">
              <div className="pm-header">
                <div className="eyebrow">Pagina 2</div>
                <h2>Mapa campus</h2>
                <p>Campus como base grafica con overlay de seccion.</p>
              </div>
              <div className="pm-campus">
                <img
                  className="pm-campus-base"
                  src={campus}
                  alt="Campus base"
                />
                <img
                  className="pm-campus-overlay"
                  src={section2}
                  alt="Pagina 2 overlay"
                />
              </div>
            </div>
          </section>

          <section id="agua" className="pm-section">
            <div className="container">
              <div className="pm-header">
                <div className="eyebrow">Pagina 3</div>
                <h2>Consumo de agua</h2>
              </div>
              <div className="pm-frame">
                <img src={section3} alt="Pagina 3 agua" />
              </div>
            </div>
          </section>

          <section id="fv" className="pm-section">
            <div className="container">
              <div className="pm-header">
                <div className="eyebrow">Pagina 4</div>
                <h2>Produccion FV</h2>
              </div>
              <div className="pm-frame">
                <img src={section4} alt="Pagina 4 FV" />
              </div>
            </div>
          </section>

          <section id="indicadores" className="pm-section">
            <div className="container">
              <div className="pm-header">
                <div className="eyebrow">Pagina 5</div>
                <h2>Indicadores</h2>
              </div>
              <div className="pm-frame">
                <img src={section5} alt="Pagina 5 indicadores" />
              </div>
            </div>
          </section>
        </main>
      ) : (
        <main className="functional">
          <section id="energia" className="section hero">
            <div className="container hero-grid">
              <div>
                <div className="eyebrow">Jaen · Campus Lagunillas</div>
                <h1>Consumo energetico en tiempo casi real.</h1>
                <p>
                  Lecturas directas del gateway, ajustes de autoconsumo y
                  agregados diarios listos para reporting.
                </p>
                <div className="cta-row">
                  <button className="button primary">Exportar datos</button>
                  <button className="button secondary">Configuracion</button>
                </div>
                <div style={{ marginTop: "2rem" }} className="card">
                  <div className="status-pill">
                    Estado API: {realtime.status === "ready" ? "activo" : "sin datos"}
                  </div>
                  <div className="metrics" style={{ marginTop: "1rem" }}>
                    <div className="metric">
                      <div>Lecturas activas</div>
                      <span>{realtimeItems.length}</span>
                    </div>
                    <div className="metric">
                      <div>Ultima actualizacion</div>
                      <span>{lastUpdate}</span>
                    </div>
                    <div className="metric">
                      <div>Total diario (kWh)</div>
                      <span>{totalToday ? number.format(totalToday) : "-"}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="media-frame">
                <span className="badge">Seccion 1</span>
                <img src={section1} alt="Referencia seccion energia" />
              </div>
            </div>
          </section>

          <section id="mapa" className="section">
            <div className="container section-grid">
              <div className="media-frame">
                <span className="badge">Mapa campus</span>
                <img src={campus} alt="Mapa campus Jaen" />
              </div>
              <div className="card">
                <h3>Resumen operativo</h3>
                <p>
                  Filtros por edificio, autoconsumo y anillo energetico con
                  comparativas por area.
                </p>
                <div style={{ marginTop: "1rem" }} className="metrics">
                  <div className="metric">
                    <div>Edificios monitorizados</div>
                    <span>20</span>
                  </div>
                  <div className="metric">
                    <div>PV autoconsumo</div>
                    <span>A0, C4, Magisterio</span>
                  </div>
                  <div className="metric">
                    <div>Gateway activo</div>
                    <span>gw_jaen_energia</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section className="section">
            <div className="container section-grid">
              <div className="card">
                <h3>Realtime (top lecturas)</h3>
                <p>Lecturas recientes del campus Jaen.</p>
                <div className="metrics" style={{ marginTop: "1rem" }}>
                  {realtimeItems.slice(0, 6).map((item) => (
                    <div key={item.rt_id} className="metric">
                      <div>{shortRt(item.rt_id)}</div>
                      <span>
                        {number.format(item.value)} {item.unit}
                      </span>
                    </div>
                  ))}
                  {!realtimeItems.length && <div>Sin datos todavia.</div>}
                </div>
              </div>
              <div className="card">
                <h3>Agregado diario (total)</h3>
                <p>Ultimos 7 dias de energia consumida.</p>
                <Sparkline series={trimmedSeries} />
                <div className="metrics">
                  {trimmedSeries.map((item) => (
                    <div key={item.date} className="metric">
                      <div>{item.date}</div>
                      <span>{number.format(item.value)} kWh</span>
                    </div>
                  ))}
                  {!trimmedSeries.length && <div>Sin datos diarios.</div>}
                </div>
              </div>
            </div>
          </section>

          <section id="agua" className="section">
            <div className="container section-grid">
              <div className="media-frame">
                <span className="badge">Seccion 3</span>
                <img src={section3} alt="Referencia consumo agua" />
              </div>
              <div className="card">
                <h3>Consumo de agua</h3>
                <p>
                  Seccion preparada para integracion de gateways de agua cuando
                  el catalogo este completo.
                </p>
                <div className="status-pill" style={{ marginTop: "1rem" }}>
                  En espera de datos
                </div>
              </div>
            </div>
          </section>

          <section id="fv" className="section">
            <div className="container section-grid">
              <div className="media-frame">
                <span className="badge">Seccion 4</span>
                <img src={section4} alt="Referencia produccion FV" />
              </div>
              <div className="card">
                <h3>Produccion FV</h3>
                <p>
                  Balance entre demanda y generacion para autoconsumo y FV
                  Endesa.
                </p>
                <div className="metrics" style={{ marginTop: "1rem" }}>
                  <div className="metric">
                    <div>Autoconsumo activo</div>
                    <span>A0 · C4 · Magisterio</span>
                  </div>
                  <div className="metric">
                    <div>Estado</div>
                    <span>Esperando datos</span>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <section id="indicadores" className="section">
            <div className="container section-grid">
              <div className="card">
                <h3>Indicadores y balance</h3>
                <p>
                  Indicadores clave para reportes publicos: CO2 evitado, balance
                  mensual y comparativa presupuestaria.
                </p>
                <div className="metrics" style={{ marginTop: "1rem" }}>
                  <div className="metric">
                    <div>CO2 evitado</div>
                    <span>--</span>
                  </div>
                  <div className="metric">
                    <div>Balance mensual</div>
                    <span>--</span>
                  </div>
                </div>
              </div>
              <div className="media-frame">
                <span className="badge">Seccion 5</span>
                <img src={section5} alt="Referencia indicadores" />
              </div>
            </div>
          </section>
        </main>
      )}

      <footer className="footer">
        <div className="container">API base: {API_BASE}</div>
      </footer>
    </div>
  );
}

export default App;
