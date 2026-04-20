import { describe, expect, it } from "vitest";

import {
  buildEnergyCampusCards,
  buildWaterCampusCards,
  buildWaterRows,
} from "./viewModels";

describe("viewModels", () => {
  it("buildEnergyCampusCards composes one unified campus card with ordered KPI groups", () => {
    const cards = buildEnergyCampusCards({
      configs: [{ scopeId: "las_lagunillas", label: "Las Lagunillas" }],
      dashboardOverview: {
        las_lagunillas: {
          title: "Campus Las Lagunillas",
          status: { kind: "complete", label: "Datos completos" },
          demand: 320,
          pv: 180,
          grid: 140,
          autoconsumoPct: 45,
          chartSeries: [{ ts: 1, demand: 1, pv: 2 }],
        },
      },
      currentAggregates: {
        las_lagunillas: {
          monthlyValue: 1200,
          monthlyUnit: "kWh",
          yearlyValue: 5400,
          yearlyUnit: "kWh",
        },
      },
      getEnvironmentalImpact: (annualKwh) => ({
        avoidedCo2Ton: annualKwh * 0.001,
        equivalentTrees: Math.round(annualKwh / 30),
      }),
    });

    expect(cards).toEqual([
      {
        id: "las_lagunillas",
        campusLabel: "Campus Las Lagunillas",
        scopeId: "las_lagunillas",
        status: { kind: "complete", label: "Datos completos" },
        chartSeries: [{ ts: 1, demand: 1, pv: 2 }],
        topMetrics: [
          {
            id: "las_lagunillas:demand",
            label: "Demanda actual",
            value: 320,
            unit: "kW",
          },
          {
            id: "las_lagunillas:autoconsumo",
            label: "% autoconsumo",
            value: 45,
            unit: "%",
          },
          {
            id: "las_lagunillas:monthly",
            label: "Energía mensual",
            value: 1200,
            unit: "kWh",
          },
          {
            id: "las_lagunillas:impact",
            label: "Impacto medioambiental anual",
            value: 5.4,
            unit: "tn/CO2",
            secondaryValue: 180,
            secondaryUnit: "árboles",
            inlineSecondary: true,
          },
        ],
        balanceMetrics: [
          {
            id: "las_lagunillas:balance-demand",
            label: "Demanda",
            value: 320,
            unit: "kW",
          },
          {
            id: "las_lagunillas:balance-pv",
            label: "Generación FV",
            value: 180,
            unit: "kW",
          },
          {
            id: "las_lagunillas:balance-grid",
            label: "Red",
            value: 140,
            unit: "kW",
          },
          {
            id: "las_lagunillas:balance-self",
            label: "Autoconsumo",
            value: 45,
            unit: "%",
          },
        ],
      },
    ]);
  });

  it("buildWaterCampusCards composes one unified campus card with ordered KPI rows", () => {
    const cards = buildWaterCampusCards({
      configs: [{ id: "jaen", label: "Las Lagunillas" }],
      waterOverview: {
        jaen: {
          readingPointsCount: 26,
          dailyValue: 12.5,
          dailyUnit: "m3",
          monthlyValue: 240.75,
          monthlyUnit: "m3",
        },
      },
    });

    expect(cards).toEqual([
      {
        id: "jaen",
        campusLabel: "Las Lagunillas",
        topMetrics: [
          {
            id: "jaen:points",
            label: "Puntos de lectura",
            value: 26,
            unit: null,
          },
          {
            id: "jaen:daily",
            label: "Consumo diario",
            value: 12.5,
            unit: "m3",
          },
          {
            id: "jaen:monthly",
            label: "Consumo mensual",
            value: 240.75,
            unit: "m3",
          },
        ],
      },
    ]);
  });

  it("buildWaterRows maps daily asset values onto realtime rows", () => {
    const rows = buildWaterRows({
      latestItems: [
        {
          rt_id: "uja.jaen.agua.consumo.edificio_b1.v_m3",
          unit: "m3",
          ts_event: 1700000200,
        },
        {
          rt_id: "uja.jaen.agua.consumo.edificio_a0.v_m3",
          unit: "m3",
          ts_event: 1700000100,
        },
      ],
      prefix: "uja.jaen.agua.",
      dailyAssetValues: {
        edificio_a0: 1.5,
        edificio_b1: 2.75,
      },
      getLabel: (rtId) =>
        ({
          "uja.jaen.agua.consumo.edificio_a0.v_m3": "Edificio A0",
          "uja.jaen.agua.consumo.edificio_b1.v_m3": "Edificio B1",
        })[rtId],
    });

    expect(rows).toEqual([
      {
        id: "uja.jaen.agua.consumo.edificio_a0.v_m3",
        sortLabel: "Edificio A0",
        pointLabel: "Edificio A0",
        dailyValue: 1.5,
        unit: "m3",
        tsEvent: 1700000100,
      },
      {
        id: "uja.jaen.agua.consumo.edificio_b1.v_m3",
        sortLabel: "Edificio B1",
        pointLabel: "Edificio B1",
        dailyValue: 2.75,
        unit: "m3",
        tsEvent: 1700000200,
      },
    ]);
  });
});
