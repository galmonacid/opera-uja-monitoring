import { cleanup, render, screen, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";

import App from "./App";

const buildFetchPayload = (url) => {
  const requestUrl = new URL(url);
  const path = requestUrl.pathname;
  const params = requestUrl.searchParams;
  const metric = params.get("metric");
  const period = params.get("period");

  if (path.endsWith("/realtime")) {
    return { ts: 0, items: [] };
  }

  if (path.endsWith("/kpis")) {
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
    expect(within(jaenCard).getByText("Puntos de lectura")).toBeInTheDocument();
    expect(within(jaenCard).getByText("Consumo diario")).toBeInTheDocument();
    expect(within(jaenCard).getByText("Consumo mensual")).toBeInTheDocument();

    const metrics = within(jaenCard).getByTestId("water-metrics-jaen");
    const chart = within(jaenCard).getByTestId("water-chart-jaen");
    const table = within(jaenCard).getByTestId("water-table-jaen");
    expect(metrics.compareDocumentPosition(chart) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
    expect(chart.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy();
  });

  it("keeps the map view without layer and water-reading selectors", () => {
    window.location.hash = "#/mapa";

    render(<App />);

    expect(screen.queryByRole("combobox", { name: /capa/i })).not.toBeInTheDocument();
    expect(screen.queryByRole("combobox", { name: /lectura agua/i })).not.toBeInTheDocument();
  });
});
