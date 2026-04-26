import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const BRAND_PORTAL_NAME = "Portal de monitorización UJA Sostenible";
const JAEN_WATER_REALTIME_ITEMS = [
  {
    rt_id: "uja.jaen.agua.consumo.edificio_a0.v_m3",
    value: 120,
    unit: "m3",
    ts_event: 1700000000,
  },
  {
    rt_id: "uja.jaen.agua.consumo.edificio_b1.v_m3",
    value: 220,
    unit: "m3",
    ts_event: 1700000300,
  },
];

const buildFetchPayload = (url) => {
  const requestUrl = new URL(url);
  const path = requestUrl.pathname;
  const params = requestUrl.searchParams;
  const metric = params.get("metric");
  const period = params.get("period");
  const gatewayId = params.get("gateway_id");

  if (path.endsWith("/realtime")) {
    if (gatewayId === "gw_jaen_agua") {
      return { ts: 1700000300, items: JAEN_WATER_REALTIME_ITEMS };
    }
    return { ts: 0, items: [] };
  }

  if (path.endsWith("/kpis")) {
    if (params.get("scope") === "ctl_linares") {
      return {
        scope: "ctl_linares",
        campus: "linares",
        label: "Campus Científico Tecnológico de Linares",
        status: "complete",
        missing_sources: [],
        ts_event: 1777230060,
        kpis: [
          { kpi: "demanda_kw", value: 83.41, unit: "kW" },
          { kpi: "fv_kw", value: 4.13, unit: "kW" },
          { kpi: "red_kw", value: 79.28, unit: "kW" },
          { kpi: "autoconsumo_pct", value: 4.95, unit: "%" },
        ],
      };
    }
    return {
      scope: params.get("scope"),
      campus: params.get("scope") === "ctl_linares" ? "linares" : "jaen",
      label: params.get("scope") === "ctl_linares" ? "Campus Científico Tecnológico de Linares" : "Campus Las Lagunillas",
      status: "empty",
      missing_sources: [],
      ts_event: null,
      kpis: [],
    };
  }

  if (path.endsWith("/series/24h")) {
    if (params.get("scope")) {
      if (params.get("scope") === "ctl_linares") {
        return {
          scope: "ctl_linares",
          campus: "linares",
          label: "Campus Científico Tecnológico de Linares",
          status: "partial",
          missing_sources: ["linares_fv_endesa_total"],
          interval_minutes: 15,
          unit: "kW",
          series: [
            { ts: 1777229100, demand: 79.1, pv: null },
            { ts: 1777230000, demand: 83.4, pv: null },
          ],
        };
      }
      return {
        scope: params.get("scope"),
        campus: params.get("scope") === "ctl_linares" ? "linares" : "jaen",
        label: params.get("scope") === "ctl_linares" ? "Campus Científico Tecnológico de Linares" : "Campus Las Lagunillas",
        status: "empty",
        missing_sources: [],
        interval_minutes: 15,
        unit: metric === "agua_consumo" ? "m3" : "kW",
        series: [],
      };
    }
    return {
      campus: params.get("campus") || "jaen",
      metric,
      interval_minutes: 15,
      unit: metric === "agua_consumo" ? "m3" : "kW",
      series: [],
    };
  }

  if (path.endsWith("/aggregates/current")) {
    if (metric === "agua_consumo") {
      return {
        campus: params.get("campus") || "jaen",
        metric,
        period,
        unit: "m3",
        timezone: "Europe/Madrid",
        period_start_ts: 0,
        ts_event: null,
        assets: ["total"],
        asset_values: { total: 0 },
      };
    }
    return {
      campus: params.get("campus") || "jaen",
      metric,
      period,
      unit: "kWh",
      timezone: "Europe/Madrid",
      period_start_ts: 0,
      ts_event: null,
      value: 0,
    };
  }

  if (path.includes("/aggregates/")) {
    return {
      campus: params.get("campus") || "jaen",
      metric,
      period: path.split("/").pop(),
      unit: metric === "agua_consumo" ? "m3" : "kWh",
      series: [],
    };
  }

  if (path.endsWith("/anomalies")) {
    return { items: [], count: 0, lookback_hours: 72 };
  }

  return {};
};

describe("App toolbar", () => {
  beforeEach(() => {
    vi.stubGlobal(
      "fetch",
      vi.fn(async (url) => ({
        ok: true,
        json: async () => buildFetchPayload(url),
      }))
    );
  });

  afterEach(() => {
    cleanup();
    window.location.hash = "#/";
    vi.unstubAllGlobals();
  });

  it("hides the period selector in the energy view", () => {
    window.location.hash = "#/energia";

    render(<App />);

    expect(screen.getByText("Campus")).toBeInTheDocument();
    expect(screen.queryByText("Periodo")).not.toBeInTheDocument();
    expect(screen.queryByText("Banda de KPIs y acumulados")).not.toBeInTheDocument();
    expect(screen.getByTestId("energy-card-las_lagunillas")).toBeInTheDocument();
    expect(screen.getByTestId("energy-card-ctl_linares")).toBeInTheDocument();
    expect(
      within(screen.getByTestId("energy-card-las_lagunillas")).getByText("Balance operativo")
    ).toBeInTheDocument();
  });

  it("hides the period selector in the water view", () => {
    window.location.hash = "#/agua";

    render(<App />);

    expect(screen.getByText("Campus")).toBeInTheDocument();
    expect(screen.queryByText("Periodo")).not.toBeInTheDocument();
    const jaenCard = screen.getByTestId("water-card-jaen");
    expect(jaenCard).toBeInTheDocument();
    const metrics = within(jaenCard).getByTestId("water-metrics-jaen");
    expect(within(metrics).getByText("Puntos de lectura")).toBeInTheDocument();
    expect(within(metrics).getByText("Consumo diario")).toBeInTheDocument();
    expect(within(metrics).getByText("Consumo mensual")).toBeInTheDocument();
    const chart = within(jaenCard).getByTestId("water-chart-jaen");
    const table = within(jaenCard).getByTestId("water-table-jaen");
    expect(metrics.compareDocumentPosition(chart) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(chart.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(within(jaenCard).getByRole("heading", { name: "Las Lagunillas" })).toBeInTheDocument();
    expect(within(jaenCard).queryByRole("heading", { name: "Agua Las Lagunillas" })).not.toBeInTheDocument();
  });

  it("keeps the map view without layer and water-reading selectors", () => {
    window.location.hash = "#/mapa";

    render(<App />);

    expect(screen.queryByRole("combobox", { name: /capa/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: /lectura agua/i })).not.toBeInTheDocument();
    expect(screen.getAllByText("Demanda energética").length).toBeGreaterThanOrEqual(2);
  });

  it("renders the demand chart for Linares even when FV series data is missing", async () => {
    render(<App />);

    const linaresCardTitle = await screen.findByText("Campus Científico Tecnológico de Linares");
    const summaryCard = linaresCardTitle.closest("article");
    expect(summaryCard).not.toBeNull();
    expect(within(summaryCard).getByText("Datos parciales")).toBeInTheDocument();
    expect(within(summaryCard).getByText("Curva Demanda kW")).toBeInTheDocument();
    expect(within(summaryCard).queryByText("Curva Generación kW")).not.toBeInTheDocument();
    expect(within(summaryCard).queryByText("Sin curva resumida disponible.")).not.toBeInTheDocument();
  });

  it("shows the updated portal branding and hides validation from visible navigation", () => {
    render(<App />);

    expect(screen.getAllByText(BRAND_PORTAL_NAME)).toHaveLength(2);
    expect(screen.queryByRole("link", { name: "Validación" })).not.toBeInTheDocument();
    expect(screen.queryByText("Gateway por gateway, con incidencias y series técnicas.")).not.toBeInTheDocument();
  });

  it("keeps the validation route reachable by direct hash without visible menu links", () => {
    window.location.hash = "#/validacion";

    render(<App />);

    expect(screen.getByRole("heading", { name: "Validación de datos" })).toBeInTheDocument();
    expect(screen.queryByRole("link", { name: "Validación" })).not.toBeInTheDocument();
  });

  it("shows the four missing Jaen water points in validation even without realtime values", async () => {
    window.location.hash = "#/validacion";

    render(<App />);

    const gatewayTitle = await screen.findByRole("heading", { name: "gw_jaen_agua" });
    const gatewayCard = gatewayTitle.closest("article");
    expect(gatewayCard).not.toBeNull();
    expect(within(gatewayCard).getByText("Plaza de los Pueblos")).toBeInTheDocument();
    expect(within(gatewayCard).getByText("Edificio C1 garaje")).toBeInTheDocument();
    expect(within(gatewayCard).getByText("Polideportivo")).toBeInTheDocument();
    expect(within(gatewayCard).getByText("Campo de fútbol")).toBeInTheDocument();
  });

  it("keeps 26 expected water points in Jaen and lists missing realtime points", async () => {
    window.location.hash = "#/agua";

    render(<App />);

    const jaenCard = screen.getByTestId("water-card-jaen");
    expect(await within(jaenCard).findByText("26")).toBeInTheDocument();
    expect(await within(jaenCard).findByText("Plaza de los Pueblos")).toBeInTheDocument();
    expect(await within(jaenCard).findByText("Edificio C1 garaje")).toBeInTheDocument();
    expect(await within(jaenCard).findByText("Polideportivo")).toBeInTheDocument();
    expect(await within(jaenCard).findByText("Campo de fútbol")).toBeInTheDocument();
  });
});
