import { useEffect, useMemo, useRef, useState } from "react";
import "./App.css";

import campus from "./assets/sections/campus.png";
import EnergyFlowDiagram from "./components/EnergyFlowDiagram";
import {
  getMonitoringPointLabel,
} from "./data/monitoringPoints";

const DEFAULT_API_BASE = "https://lg0yl7xofl.execute-api.eu-west-1.amazonaws.com/v1";
const API_BASES = [
  import.meta.env.VITE_API_BASE,
  DEFAULT_API_BASE,
].filter(Boolean);
const WATER_MAP_SOURCE_OPTIONS = new Set(["backend_aggregate", "client_offset", "raw"]);
const DEFAULT_WATER_MAP_SOURCE = "backend_aggregate";
const configuredWaterMapSource = String(
  import.meta.env.VITE_WATER_MAP_SOURCE || DEFAULT_WATER_MAP_SOURCE
).toLowerCase();
const WATER_MAP_SOURCE = WATER_MAP_SOURCE_OPTIONS.has(configuredWaterMapSource)
  ? configuredWaterMapSource
  : DEFAULT_WATER_MAP_SOURCE;
const ANALYTICS_SERIES_INTERVAL_MINUTES = 15;
const ANOMALIES_LOOKBACK_HOURS = 72;
const ANOMALIES_LIMIT = 200;
const CO2_EMISSIONS_COEFFICIENT_TON_PER_KWH = 0.000331;
const CARBON_FOOTPRINT_COEFFICIENT_KWH_PER_TREE = 30;

const number = new Intl.NumberFormat("es-ES", {
  maximumFractionDigits: 2,
});
const NICE_TICK_FACTORS = [1, 2, 2.5, 5, 10];
const USER_TIME_ZONE = Intl.DateTimeFormat().resolvedOptions().timeZone || "UTC";
const DATE_TIME_FORMATTER = new Intl.DateTimeFormat("es-ES", {
  timeZone: USER_TIME_ZONE,
  dateStyle: "short",
  timeStyle: "medium",
});
const DATE_FORMATTER = new Intl.DateTimeFormat("es-ES", {
  timeZone: USER_TIME_ZONE,
  dateStyle: "short",
});
const MONTH_FORMATTER = new Intl.DateTimeFormat("es-ES", {
  timeZone: USER_TIME_ZONE,
  month: "2-digit",
  year: "numeric",
});
const HOUR_FORMATTER = new Intl.DateTimeFormat("es-ES", {
  timeZone: USER_TIME_ZONE,
  hour: "2-digit",
  minute: "2-digit",
  hourCycle: "h23",
});

const CAMPUS_VHE_RT_ID = "uja.jaen.energia.consumo.carga_vhe.p_kw";
const JAEN_ENDESA_CT_TOTAL_RT_ID = "uja.jaen.fv.endesa.ct_total.p_kw";
const JAEN_ENDESA_INVERTER_RT_PREFIX = "uja.jaen.fv.endesa.inv";

const MAP_LAYER_OFFSETS = {
  energy: { x: 0, y: 0 },
  water: { x: 1.2, y: 2 },
  solar: { x: 1.2, y: -2 },
  autoconsumo: { x: -1.2, y: 2 },
};

const createMapEntry = ({
  id,
  layer,
  campus,
  x,
  y,
  rtIds,
  aggregate = "single",
  label,
  detailLabel,
  icon,
}) => {
  const normalizedRtIds = Array.isArray(rtIds) ? rtIds : [rtIds];
  const fallbackLabel = normalizedRtIds.length === 1 ? getMonitoringPointLabel(normalizedRtIds[0]) : id;
  const resolvedLabel = label || fallbackLabel;
  return {
    id,
    layer,
    campus,
    x,
    y,
    rtIds: normalizedRtIds,
    aggregate,
    icon: icon || layer,
    label: resolvedLabel,
    detailLabel: detailLabel || resolvedLabel,
  };
};

const buildSingleMapEntries = (layer, campus, definitions) =>
  definitions.map(([rtId, x, y, label]) =>
    createMapEntry({
      id: `${layer}:${rtId}`,
      layer,
      campus,
      rtIds: rtId,
      x,
      y,
      label,
      detailLabel: label,
    })
  );

const MAP_ENTRIES = [
  ...buildSingleMapEntries("energy", "jaen", [
    ["uja.jaen.energia.consumo.edificio_a0.p_kw", 83, 15],
    ["uja.jaen.energia.consumo.edificio_a1.p_kw", 64, 32],
    ["uja.jaen.energia.consumo.edificio_a2.p_kw", 50, 40],
    ["uja.jaen.energia.consumo.edificio_a3.p_kw", 40, 44],
    ["uja.jaen.energia.consumo.edificio_a4.p_kw", 31, 55],
    ["uja.jaen.energia.consumo.edificio_b1.p_kw", 87, 30],
    ["uja.jaen.energia.consumo.edificio_b2.p_kw", 65, 43],
    ["uja.jaen.energia.consumo.edificio_b3.p_kw", 57, 50],
    ["uja.jaen.energia.consumo.edificio_b4.p_kw", 45, 60],
    ["uja.jaen.energia.consumo.edificio_b5.p_kw", 36, 67],
    ["uja.jaen.energia.consumo.edificio_c1.p_kw", 73, 49],
    ["uja.jaen.energia.consumo.edificio_c2.p_kw", 61, 60],
    ["uja.jaen.energia.consumo.edificio_c3.p_kw", 54, 67],
    ["uja.jaen.energia.consumo.edificio_c5.p_kw", 36, 86],
    ["uja.jaen.energia.consumo.edificio_c6.p_kw", 23, 90],
    ["uja.jaen.energia.consumo.edificio_d1.p_kw", 87, 51],
    ["uja.jaen.energia.consumo.edificio_d2.p_kw", 74, 62],
    ["uja.jaen.energia.consumo.edificio_d3.p_kw", 59, 72],
    ["uja.jaen.energia.consumo.edificio_d4.p_kw", 31, 97],
    [CAMPUS_VHE_RT_ID, 23, 65],
    ["uja.jaen.energia.consumo.um_c4.p_kw", 43, 76],
    ["uja.jaen.energia.consumo.ae_magisterio.p_kw", 65, 95],
    ["uja.jaen.energia.consumo.apartamentos_universitarios.p_kw", 40, 9],
    ["uja.jaen.energia.consumo.polideportivo.p_kw", 52, 18],
    ["uja.jaen.energia.consumo.residencia_domingo_savio.p_kw", 65, 9],
  ]),
  ...buildSingleMapEntries("energy", "linares", [
    ["uja.linares.energia.consumo.aulario_departamental.p_kw", 5, 29],
    ["uja.linares.energia.consumo.lab_sg_t1.p_kw", 3, 40],
    ["uja.linares.energia.consumo.lab_sg_t2.p_kw", 11, 40],
    ["uja.linares.energia.consumo.urbanizacion.p_kw", 15, 25],
    ["uja.linares.energia.consumo.polideportivo.p_kw", 14, 12],
  ]),
  ...buildSingleMapEntries("water", "jaen", [
    ["uja.jaen.agua.consumo.edificio_a0.v_m3", 83, 15],
    ["uja.jaen.agua.consumo.edificio_a1.v_m3", 64, 32],
    ["uja.jaen.agua.consumo.edificio_a2.v_m3", 50, 40],
    ["uja.jaen.agua.consumo.edificio_a3.v_m3", 40, 44],
    ["uja.jaen.agua.consumo.edificio_a4.v_m3", 31, 55],
    ["uja.jaen.agua.consumo.edificio_b1.v_m3", 87, 30],
    ["uja.jaen.agua.consumo.edificio_b2.v_m3", 64, 44],
    ["uja.jaen.agua.consumo.edificio_b3.v_m3", 57, 50],
    ["uja.jaen.agua.consumo.edificio_b4.v_m3", 45, 60],
    ["uja.jaen.agua.consumo.edificio_b5.v_m3", 36, 67],
    ["uja.jaen.agua.consumo.edificio_c1.v_m3", 73, 49],
    ["uja.jaen.agua.consumo.edificio_c2.v_m3", 61, 60],
    ["uja.jaen.agua.consumo.edificio_c3.v_m3", 54, 67],
    ["uja.jaen.agua.consumo.edificio_c5.v_m3", 36, 86],
    ["uja.jaen.agua.consumo.edificio_c6.v_m3", 23, 90],
    ["uja.jaen.agua.consumo.edificio_d1.v_m3", 87, 51],
    ["uja.jaen.agua.consumo.edificio_d2.v_m3", 74, 62],
    ["uja.jaen.agua.consumo.edificio_d3.v_m3", 59, 72],
    ["uja.jaen.agua.consumo.edificio_d4.v_m3", 31, 97],
    ["uja.jaen.agua.consumo.edificio_c1_garaje.v_m3", 70, 59],
    ["uja.jaen.agua.consumo.d1_caf.v_m3", 92, 58],
    ["uja.jaen.agua.consumo.c_futbol.v_m3", 82, 8],
    ["uja.jaen.agua.consumo.plaz_pueblos.v_m3", 58, 30],
    ["uja.jaen.agua.consumo.polideportivo.v_m3", 62, 10],
    ["uja.jaen.agua.consumo.um_c4.v_m3", 44, 87],
    ["uja.jaen.agua.consumo.ae_magisterio.v_m3", 76, 95],
  ]),
  ...buildSingleMapEntries("water", "linares", [
    ["uja.linares.agua.consumo.cafeteria.v_m3", 19, 16],
    ["uja.linares.agua.consumo.comedor.v_m3", 12, 21],
    ["uja.linares.agua.consumo.departamental.v_m3", 5, 25],
    ["uja.linares.agua.consumo.laboratorios.v_m3", 11, 29],
    ["uja.linares.agua.consumo.pabellon_polideportivo.v_m3", 23, 10],
    ["uja.linares.agua.consumo.reciclada_lluvia.v_m3", 4, 33],
    ["uja.linares.agua.consumo.riego_aulario.v_m3", 9, 14],
    ["uja.linares.agua.consumo.servicios_generales.v_m3", 16, 31],
  ]),
  createMapEntry({
    id: "solar:jaen:p3",
    layer: "solar",
    campus: "jaen",
    x: 42,
    y: 96,
    rtIds: [
      "uja.jaen.fv.endesa.inv01.p_ac_kw",
      "uja.jaen.fv.endesa.inv02.p_ac_kw",
      "uja.jaen.fv.endesa.inv03.p_ac_kw",
      "uja.jaen.fv.endesa.inv04.p_ac_kw",
    ],
    aggregate: "sum",
    label: "FV Endesa P3",
  }),
  createMapEntry({
    id: "solar:jaen:p4",
    layer: "solar",
    campus: "jaen",
    x: 86,
    y: 8,
    rtIds: ["uja.jaen.fv.endesa.inv05.p_ac_kw", "uja.jaen.fv.endesa.inv06.p_ac_kw"],
    aggregate: "sum",
    label: "FV Endesa P4",
  }),
  createMapEntry({
    id: "solar:jaen:b4",
    layer: "solar",
    campus: "jaen",
    x: 45,
    y: 60,
    rtIds: ["uja.jaen.fv.endesa.inv07.p_ac_kw", "uja.jaen.fv.endesa.inv08.p_ac_kw"],
    aggregate: "sum",
    label: "FV Endesa B4",
  }),
  createMapEntry({
    id: "solar:jaen:c3",
    layer: "solar",
    campus: "jaen",
    x: 49,
    y: 70,
    rtIds: ["uja.jaen.fv.endesa.inv09.p_ac_kw"],
    aggregate: "single",
    label: "FV Endesa C3",
  }),
  createMapEntry({
    id: "solar:jaen:d3",
    layer: "solar",
    campus: "jaen",
    x: 56,
    y: 74,
    rtIds: [
      "uja.jaen.fv.endesa.inv10.p_ac_kw",
      "uja.jaen.fv.endesa.inv11.p_ac_kw",
      "uja.jaen.fv.endesa.inv12.p_ac_kw",
    ],
    aggregate: "sum",
    label: "FV Endesa D3",
  }),
  createMapEntry({
    id: "solar:linares:endesa",
    layer: "solar",
    campus: "linares",
    x: 8,
    y: 6,
    rtIds: ["uja.linares.fv.endesa.ct_total.p_kw"],
    aggregate: "single",
    label: "FV Endesa Linares",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:b5",
    layer: "autoconsumo",
    campus: "jaen",
    x: 36,
    y: 67,
    rtIds: ["uja.jaen.fv.auto.b5_inv1.p_ac_kw", "uja.jaen.fv.auto.b5_inv2.p_ac_kw"],
    aggregate: "sum",
    label: "Autoconsumo B5",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:pergola",
    layer: "autoconsumo",
    campus: "jaen",
    x: 63,
    y: 45,
    rtIds: ["uja.jaen.fv.auto.pergola.p_ac_kw"],
    aggregate: "single",
    label: "Pérgola",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:parking",
    layer: "autoconsumo",
    campus: "jaen",
    x: 78,
    y: 8,
    rtIds: ["uja.jaen.fv.auto.parking_p4.p_ac_kw"],
    aggregate: "single",
    label: "Parking P4",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:fachada",
    layer: "autoconsumo",
    campus: "jaen",
    x: 53,
    y: 37,
    rtIds: ["uja.jaen.fv.auto.fachada.p_ac_kw"],
    aggregate: "single",
    label: "Fachada",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:a0",
    layer: "autoconsumo",
    campus: "jaen",
    x: 83,
    y: 15,
    rtIds: ["uja.jaen.fv.auto.edificio_a0.p_kw"],
    aggregate: "single",
    label: "Autoconsumo A0",
    detailLabel: "Autoconsumo edificio A0",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:c4",
    layer: "autoconsumo",
    campus: "jaen",
    x: 44,
    y: 87,
    rtIds: ["uja.jaen.fv.auto.edificio_c4.p_kw"],
    aggregate: "single",
    label: "Autoconsumo C4",
    detailLabel: "Autoconsumo edificio C4",
  }),
  createMapEntry({
    id: "autoconsumo:jaen:magisterio",
    layer: "autoconsumo",
    campus: "jaen",
    x: 76,
    y: 95,
    rtIds: ["uja.jaen.fv.auto.magisterio.p_kw"],
    aggregate: "single",
    label: "Autoconsumo Magisterio",
  }),
];
const DASHBOARD_SCOPES = [
  { id: "las_lagunillas", title: "Campus Las Lagunillas" },
  { id: "ctl_linares", title: "Campus Científico Tecnológico de Linares" },
];
const MISSING_SOURCE_LABELS = {
  las_lagunillas_demand: "demanda Las Lagunillas",
  jaen_fv_endesa_total: "FV Endesa Jaen",
  jaen_fv_auto_univer: "FV autoconsumo UNIVER",
  jaen_fv_auto_a0: "FV edificio A0",
  ctl_linares_demand: "demanda Campus Científico Tecnológico de Linares",
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

const PORTAL_ROUTES = [
  { id: "summary", hash: "#/", label: "Balance" },
  { id: "energy", hash: "#/energia", label: "Energía" },
  { id: "map", hash: "#/mapa", label: "Mapa" },
  { id: "water", hash: "#/agua", label: "Agua" },
  { id: "solar", hash: "#/fotovoltaica", label: "Fotovoltaica" },
  { id: "validation", hash: "#/validacion", label: "Validación" },
];

const ENERGY_VIEW_CONFIG = [
  {
    scopeId: "las_lagunillas",
    campus: "jaen",
    label: "Campus Las Lagunillas",
    gatewayId: "gw_jaen_energia",
  },
  {
    scopeId: "ctl_linares",
    campus: "linares",
    label: "Campus Científico Tecnológico de Linares",
    gatewayId: "gw_linares_mix",
  },
];

const WATER_VIEW_CONFIG = [
  {
    id: "jaen",
    campus: "jaen",
    label: "Las Lagunillas",
    gatewayId: "gw_jaen_agua",
    prefix: "uja.jaen.agua.",
  },
  {
    id: "linares",
    campus: "linares",
    label: "Campus Científico Tecnológico de Linares",
    gatewayId: "gw_linares_mix",
    prefix: "uja.linares.agua.",
  },
];

const SOLAR_VIEW_CONFIG = [
  {
    id: "endesa_jaen",
    campus: "jaen",
    label: "FV Endesa Jaén",
    gatewayId: "gw_endesa_jaen",
    kind: "Planta FV",
    description: "Generación principal de Endesa en Las Lagunillas.",
    irradianceRtIds: [
      "uja.jaen.fv.endesa.rad01.g_wm2",
      "uja.jaen.fv.endesa.rad02.g_wm2",
      "uja.jaen.fv.endesa.rad03.g_wm2",
      "uja.jaen.fv.endesa.rad04.g_wm2",
      "uja.jaen.fv.endesa.rad05.g_wm2",
    ],
  },
  {
    id: "autoconsumo_jaen",
    campus: "jaen",
    label: "Autoconsumo Jaén",
    gatewayId: "gw_autoconsumo_jaen",
    kind: "Proyecto autoconsumo",
    description: "Producción de autoconsumo de Jaén para explotación interna.",
    irradianceRtIds: [
      "uja.jaen.fv.auto.pergola_rad.g_wm2",
      "uja.jaen.fv.auto.b5_rad.g_wm2",
      "uja.jaen.fv.auto.fachada_rad.g_wm2",
    ],
  },
  {
    id: "endesa_linares",
    campus: "linares",
    label: "FV Endesa Linares",
    gatewayId: "gw_endesa_linares",
    kind: "Planta FV",
    description: "Generación principal de Campus Científico Tecnológico de Linares.",
    irradianceRtIds: ["uja.linares.fv.endesa.rad01.g_wm2"],
  },
];

const MAP_LAYER_OPTIONS = [
  // { value: "all", label: "Todas las capas" },
  { value: "energy", label: "Demanda de energía" },
  // { value: "water", label: "Agua" },
  // { value: "solar", label: "Fotovoltaica" },
  // { value: "autoconsumo", label: "Autoconsumo" },
];
const ACTIVE_MAP_ENTRY_COUNT = MAP_ENTRIES.filter((entry) =>
  MAP_LAYER_OPTIONS.some((option) => option.value === entry.layer)
).length;

const VALIDATION_TAB_OPTIONS = [
  { id: "latest", label: "Último valor" },
  { id: "series", label: "24h" },
  { id: "daily", label: "Diario" },
  { id: "monthly", label: "Mensual" },
];

const CAMPUS_OPTIONS = [
  { value: "all", label: "Todos los campus" },
  { value: "jaen", label: "Las Lagunillas" },
  { value: "linares", label: "Campus Científico Tecnológico de Linares" },
];

const PERIOD_OPTIONS = [
  { value: "actual", label: "Actual" },
  { value: "daily", label: "Diario" },
  { value: "monthly", label: "Mensual" },
];

const VALIDATION_DOMAIN_OPTIONS = [
  { value: "all", label: "Todos los dominios" },
  { value: "mixto", label: "Mixto" },
  { value: "agua", label: "Agua" },
  { value: "fv", label: "Fotovoltaica" },
];

const ANOMALY_TYPE_LABELS = {
  negative_not_allowed: "Negativo no permitido",
  above_max_threshold: "Fuera de rango",
  non_finite: "No finito",
};

const GATEWAY_LABELS = Object.fromEntries(GATEWAYS.map((gateway) => [gateway.id, gateway.label]));

const resolveRouteId = (hash) => {
  switch (hash) {
    case "#/balance":
    case "#/resumen":
    case "#/":
      return "summary";
    case "#/energia":
      return "energy";
    case "#/mapa":
      return "map";
    case "#/agua":
      return "water";
    case "#/fotovoltaica":
      return "solar";
    case "#/autoconsumo":
    case "#/proyectos":
      return "solar";
    case "#/validacion":
      return "validation";
    default:
      return "summary";
  }
};

const buildLocalDateFromParts = (year, month, day = 1) =>
  new Date(Number(year), Number(month) - 1, Number(day), 12, 0, 0);

const formatLocalHour = (ts) => {
  const value = Number(ts);
  if (!Number.isFinite(value)) return "--:--";
  return HOUR_FORMATTER.format(new Date(value * 1000));
};

const getNiceStep = (roughStep) => {
  if (!Number.isFinite(roughStep) || roughStep <= 0) return 1;
  const magnitude = 10 ** Math.floor(Math.log10(roughStep));
  const normalized = roughStep / magnitude;
  const factor = NICE_TICK_FACTORS.find((candidate) => normalized <= candidate) || 10;
  return factor * magnitude;
};

const buildYAxisScale = (values, ticksY) => {
  const maxDataValue = Math.max(0, ...values.map((value) => Number(value || 0)));
  if (maxDataValue <= 0) {
    return {
      axisMax: 1,
      tickValues: Array.from({ length: ticksY + 1 }, (_, idx) => ticksY - idx),
    };
  }

  const step = getNiceStep(maxDataValue / ticksY);
  const axisMax = step * ticksY;
  return {
    axisMax,
    tickValues: Array.from({ length: ticksY + 1 }, (_, idx) => axisMax - step * idx),
  };
};

const formatTs = (ts) => {
  if (!ts && ts !== 0) return "--";
  const value = Number(ts);
  if (!Number.isFinite(value)) return "--";
  return DATE_TIME_FORMATTER.format(new Date(value * 1000));
};

const formatDate = (value) => {
  if (!value) return "--";
  if (typeof value === "string") {
    const fullDateMatch = value.match(/^(\d{4})-(\d{2})-(\d{2})$/);
    if (fullDateMatch) {
      const [, year, month, day] = fullDateMatch;
      return DATE_FORMATTER.format(buildLocalDateFromParts(year, month, day));
    }
    const monthMatch = value.match(/^(\d{4})-(\d{2})$/);
    if (monthMatch) {
      const [, year, month] = monthMatch;
      return MONTH_FORMATTER.format(buildLocalDateFromParts(year, month));
    }
    const parsed = new Date(value);
    if (!Number.isNaN(parsed.getTime())) {
      return DATE_TIME_FORMATTER.format(parsed);
    }
    return value;
  }
  if (typeof value === "number") {
    return DATE_TIME_FORMATTER.format(new Date(value * 1000));
  }
  return value;
};

const formatScalar = (value) => {
  if (value == null || value === "") return "--";
  const numeric = Number(value);
  if (Number.isFinite(numeric)) {
    return number.format(numeric);
  }
  return String(value);
};

const formatDisplayUnit = (unit) => {
  if (!unit) return "";
  if (unit === "m3") return "m³";
  return unit;
};

const formatAxisTick = (value, unit) => {
  const suffix = formatDisplayUnit(unit);
  return suffix ? `${number.format(value)} ${suffix}` : number.format(value);
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

const buildTimeSegments = (series, intervalMinutes = ANALYTICS_SERIES_INTERVAL_MINUTES) => {
  if (!series.length) return [];
  const maxGapSeconds = intervalMinutes * 60 + 300;
  const segments = [];
  let current = [];
  let previousTs = null;

  series.forEach((item) => {
    if (previousTs != null && item.ts - previousTs > maxGapSeconds) {
      if (current.length) segments.push(current);
      current = [];
    }
    current.push(item);
    previousTs = item.ts;
  });

  if (current.length) segments.push(current);
  return segments;
};

const buildLinePoints = (segment, xForTs, yForValue, valueKey = "value") =>
  segment
    .map((item) => `${xForTs(item.ts).toFixed(2)},${yForValue(item[valueKey]).toFixed(2)}`)
    .join(" ");

const buildAreaPath = (segment, xForTs, yForValue, baselineY, valueKey = "value") => {
  if (!segment.length) return "";
  const linePoints = buildLinePoints(segment, xForTs, yForValue, valueKey);
  const firstX = xForTs(segment[0].ts).toFixed(2);
  const lastX = xForTs(segment[segment.length - 1].ts).toFixed(2);
  return `M ${firstX},${baselineY.toFixed(2)} L ${linePoints} L ${lastX},${baselineY.toFixed(
    2
  )} Z`;
};

const AreaChart = ({
  series,
  intervalMinutes = ANALYTICS_SERIES_INTERVAL_MINUTES,
  unit = "kW",
  density = "split",
}) => {
  const [renderNow] = useState(() => Math.floor(Date.now() / 1000));
  const chartSeries = useMemo(
    () =>
      [...(series || [])]
        .filter(
          (item) =>
            Number.isFinite(Number(item?.ts)) &&
            Number.isFinite(Number(item?.demand)) &&
            Number.isFinite(Number(item?.pv))
        )
        .map((item) => ({
          ts: Number(item.ts),
          demand: Number(item.demand),
          pv: Number(item.pv),
        }))
        .sort((a, b) => a.ts - b.ts),
    [series]
  );

  const chartDensity = density === "single" ? "single" : "split";
  const width = 120;
  const height = chartDensity === "single" ? 40 : 44;
  const paddingLeft = chartDensity === "single" ? 15 : 18;
  const paddingRight = 6;
  const paddingTop = 2;
  const paddingBottom = chartDensity === "single" ? 9 : 10;
  const plotHeight = height - paddingTop - paddingBottom;
  const plotWidth = width - paddingLeft - paddingRight;
  const ticksY = 4;
  const { axisMax, tickValues } = buildYAxisScale(
    chartSeries.flatMap((item) => [item.demand, item.pv]),
    ticksY
  );
  const now = Math.max(renderNow, chartSeries[chartSeries.length - 1]?.ts || 0);
  const start = now - 86400;
  const xForTs = (ts) => paddingLeft + ((ts - start) / 86400) * plotWidth;
  const yForValue = (value) => paddingTop + plotHeight - (value / axisMax) * plotHeight;
  const baselineY = paddingTop + plotHeight;
  const segments = buildTimeSegments(chartSeries, intervalMinutes);

  return (
    <svg
      className={`area-chart density-${chartDensity}`}
      viewBox={`0 0 ${width} ${height}`}
      role="img"
      aria-label="Curva de demanda y generación fotovoltaica de las últimas 24 horas"
    >
      <g className="axis axis-y">
        {tickValues.map((value, idx) => {
          const y = paddingTop + (plotHeight / ticksY) * idx;
          return (
            <g key={`y-${idx}`} transform={`translate(0, ${y})`}>
              <line className="axis-line" x1={paddingLeft} x2={width - paddingRight} y1="0" y2="0" />
              <text className="axis-label axis-label-y" x={paddingLeft - 1.5} y="-1">
                {formatAxisTick(value, unit)}
              </text>
            </g>
          );
        })}
      </g>
      <g className="axis axis-x">
        {[0, 6, 12, 18, 24].map((hours) => {
          const x = paddingLeft + (hours / 24) * plotWidth;
          const textAnchor = hours === 0 ? "start" : hours === 24 ? "end" : "middle";
          return (
            <g key={`x-${hours}`} transform={`translate(${x}, ${baselineY})`}>
              <line className="axis-tick" x1="0" x2="0" y1="0" y2="2" />
              <text className="axis-label axis-label-x" x="0" y="4.5" textAnchor={textAnchor}>
                {formatLocalHour(now - (24 - hours) * 3600)}
              </text>
            </g>
          );
        })}
      </g>
      {segments.map((segment, idx) => (
        <path key={`demand-area-${idx}`} className="area area-demand" d={buildAreaPath(segment, xForTs, yForValue, baselineY, "demand")} />
      ))}
      {segments.map((segment, idx) => (
        <path key={`pv-area-${idx}`} className="area area-pv" d={buildAreaPath(segment, xForTs, yForValue, baselineY, "pv")} />
      ))}
      {segments.map((segment, idx) => (
        <polyline
          key={`demand-line-${idx}`}
          className="line line-demand"
          points={buildLinePoints(segment, xForTs, yForValue, "demand")}
        />
      ))}
      {segments.map((segment, idx) => (
        <polyline
          key={`pv-line-${idx}`}
          className="line line-pv"
          points={buildLinePoints(segment, xForTs, yForValue, "pv")}
        />
      ))}
    </svg>
  );
};

const ValueChart = ({
  series,
  label,
  unit = "kW",
  intervalMinutes = ANALYTICS_SERIES_INTERVAL_MINUTES,
  density = "split",
}) => {
  const [renderNow] = useState(() => Math.floor(Date.now() / 1000));
  const chartSeries = useMemo(
    () =>
      (series || [])
        .filter((item) => Number.isFinite(Number(item?.ts)) && Number.isFinite(Number(item?.value)))
        .map((item) => ({ ts: Number(item.ts), value: Number(item.value) }))
        .sort((a, b) => a.ts - b.ts),
    [series]
  );
  const chartDensity = density === "single" ? "single" : "split";
  const width = 120;
  const height = chartDensity === "single" ? 52 : 64;
  const paddingLeft = chartDensity === "single" ? 15 : 18;
  const paddingRight = 6;
  const paddingTop = 2;
  const paddingBottom = chartDensity === "single" ? 10 : 11;
  const plotHeight = height - paddingTop - paddingBottom;
  const plotWidth = width - paddingLeft - paddingRight;
  const ticksY = 4;
  const { axisMax, tickValues } = buildYAxisScale(
    chartSeries.map((item) => item.value),
    ticksY
  );
  const now = Math.max(renderNow, chartSeries[chartSeries.length - 1]?.ts || 0);
  const start = now - 86400;
  const xForTs = (ts) => paddingLeft + ((ts - start) / 86400) * plotWidth;
  const yForValue = (value) => paddingTop + plotHeight - (value / axisMax) * plotHeight;
  const baselineY = paddingTop + plotHeight;
  const segments = buildTimeSegments(chartSeries, intervalMinutes);

  return (
    <svg className={`value-chart density-${chartDensity}`} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${label} últimas 24 horas`}>
      <g className="axis axis-y">
        {tickValues.map((value, idx) => {
          const y = paddingTop + (plotHeight / ticksY) * idx;
          return (
            <g key={`value-y-${idx}`} transform={`translate(0, ${y})`}>
              <line className="axis-line" x1={paddingLeft} x2={width - paddingRight} y1="0" y2="0" />
              <text className="axis-label axis-label-y" x={paddingLeft - 1.5} y="-1">
                {formatAxisTick(value, unit)}
              </text>
            </g>
          );
        })}
      </g>
      <g className="axis axis-x">
        {[0, 6, 12, 18, 24].map((hours) => {
          const x = paddingLeft + (hours / 24) * plotWidth;
          const textAnchor = hours === 0 ? "start" : hours === 24 ? "end" : "middle";
          return (
            <g key={`value-x-${hours}`} transform={`translate(${x}, ${baselineY})`}>
              <line className="axis-tick" x1="0" x2="0" y1="0" y2="2" />
              <text className="axis-label axis-label-x" x="0" y="4.5" textAnchor={textAnchor}>
                {formatLocalHour(now - (24 - hours) * 3600)}
              </text>
            </g>
          );
        })}
      </g>
      {segments.map((segment, idx) => (
        <path key={`value-area-${idx}`} className="value-area" d={buildAreaPath(segment, xForTs, yForValue, baselineY)} />
      ))}
      {segments.map((segment, idx) => (
        <polyline
          key={`value-line-${idx}`}
          className="value-line"
          points={buildLinePoints(segment, xForTs, yForValue)}
        />
      ))}
    </svg>
  );
};

const SolarDualAxisChart = ({
  powerSeries,
  irradianceSeries,
  label,
  intervalMinutes = ANALYTICS_SERIES_INTERVAL_MINUTES,
  density = "split",
}) => {
  const [renderNow] = useState(() => Math.floor(Date.now() / 1000));
  const normalizedPower = useMemo(
    () =>
      (powerSeries || [])
        .filter((item) => Number.isFinite(Number(item?.ts)) && Number.isFinite(Number(item?.value)))
        .map((item) => ({ ts: Number(item.ts), value: Number(item.value) }))
        .sort((a, b) => a.ts - b.ts),
    [powerSeries]
  );
  const normalizedIrradiance = useMemo(
    () =>
      (irradianceSeries || [])
        .filter((item) => Number.isFinite(Number(item?.ts)) && Number.isFinite(Number(item?.value)))
        .map((item) => ({ ts: Number(item.ts), value: Number(item.value) }))
        .sort((a, b) => a.ts - b.ts),
    [irradianceSeries]
  );
  const chartDensity = density === "single" ? "single" : "split";
  const width = 124;
  const height = chartDensity === "single" ? 40 : 44;
  const paddingLeft = chartDensity === "single" ? 15 : 18;
  const paddingRight = chartDensity === "single" ? 15 : 18;
  const paddingTop = 2;
  const paddingBottom = chartDensity === "single" ? 9 : 10;
  const plotHeight = height - paddingTop - paddingBottom;
  const plotWidth = width - paddingLeft - paddingRight;
  const ticksY = 4;
  const powerScale = buildYAxisScale(normalizedPower.map((item) => item.value), ticksY);
  const irradianceScale = buildYAxisScale(normalizedIrradiance.map((item) => item.value), ticksY);
  const hasIrradiance = normalizedIrradiance.length > 0;
  const now = Math.max(
    renderNow,
    normalizedPower[normalizedPower.length - 1]?.ts || 0,
    normalizedIrradiance[normalizedIrradiance.length - 1]?.ts || 0
  );
  const start = now - 86400;
  const xForTs = (ts) => paddingLeft + ((ts - start) / 86400) * plotWidth;
  const yForPower = (value) =>
    paddingTop + plotHeight - (value / powerScale.axisMax) * plotHeight;
  const yForIrradiance = (value) =>
    paddingTop + plotHeight - (value / irradianceScale.axisMax) * plotHeight;
  const baselineY = paddingTop + plotHeight;
  const powerSegments = buildTimeSegments(normalizedPower, intervalMinutes);
  const irradianceSegments = buildTimeSegments(normalizedIrradiance, intervalMinutes);

  return (
    <svg className={`solar-chart density-${chartDensity}`} viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`${label} potencia e irradiancia últimas 24 horas`}>
      <g className="axis axis-y">
        {powerScale.tickValues.map((value, idx) => {
          const y = paddingTop + (plotHeight / ticksY) * idx;
          return (
            <g key={`solar-y-left-${idx}`} transform={`translate(0, ${y})`}>
              <line className="axis-line" x1={paddingLeft} x2={width - paddingRight} y1="0" y2="0" />
              <text className="axis-label axis-label-y" x={paddingLeft - 1.5} y="-1">
                {formatAxisTick(value, "kW")}
              </text>
            </g>
          );
        })}
        {hasIrradiance
          ? irradianceScale.tickValues.map((value, idx) => {
              const y = paddingTop + (plotHeight / ticksY) * idx;
              return (
                <text
                  key={`solar-y-right-${idx}`}
                  className="axis-label axis-label-y-right"
                  x={width - paddingRight + 1.5}
                  y={y - 1}
                >
                  {formatAxisTick(value, "W/m²")}
                </text>
              );
            })
          : null}
      </g>
      <g className="axis axis-x">
        {[0, 6, 12, 18, 24].map((hours) => {
          const x = paddingLeft + (hours / 24) * plotWidth;
          const textAnchor = hours === 0 ? "start" : hours === 24 ? "end" : "middle";
          return (
            <g key={`solar-x-${hours}`} transform={`translate(${x}, ${baselineY})`}>
              <line className="axis-tick" x1="0" x2="0" y1="0" y2="2" />
              <text className="axis-label axis-label-x" x="0" y="4.5" textAnchor={textAnchor}>
                {formatLocalHour(now - (24 - hours) * 3600)}
              </text>
            </g>
          );
        })}
      </g>
      {powerSegments.map((segment, idx) => (
        <path key={`solar-area-${idx}`} className="value-area" d={buildAreaPath(segment, xForTs, yForPower, baselineY)} />
      ))}
      {powerSegments.map((segment, idx) => (
        <polyline
          key={`solar-line-power-${idx}`}
          className="value-line"
          points={buildLinePoints(segment, xForTs, yForPower)}
        />
      ))}
      {hasIrradiance
        ? irradianceSegments.map((segment, idx) => (
            <polyline
              key={`solar-line-irradiance-${idx}`}
              className="line line-irradiance"
              points={buildLinePoints(segment, xForTs, yForIrradiance)}
            />
          ))
        : null}
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

const IconWater = () => (
  <svg viewBox="0 0 24 24" aria-hidden="true">
    <path
      d="M12 3s-5 5.4-5 9.1A5 5 0 0 0 17 12c0-3.7-5-9-5-9Z"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.8"
      strokeLinejoin="round"
    />
    <path
      d="M10 15.5a2.6 2.6 0 0 0 4 0"
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

const renderMapLayerIcon = (layer) => {
  if (layer === "water") return <IconWater />;
  if (layer === "solar") return <IconSolar />;
  if (layer === "autoconsumo") return <IconAutoconsumo />;
  return <IconDemand />;
};

const getDefaultMapUnit = (layer) => (layer === "water" ? "m3" : "kW");

const clampPercent = (value) => Math.max(1, Math.min(97, value));

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
  const [routeHash, setRouteHash] = useState(() => window.location.hash || "#/");
  const [campusFilter, setCampusFilter] = useState("all");
  const [periodFilter, setPeriodFilter] = useState("actual");
  const [mapLayer, setMapLayer] = useState("energy");
  const [selectedMapPoint, setSelectedMapPoint] = useState(null);
  const [validationDomainFilter, setValidationDomainFilter] = useState("all");
  const [validationActiveTabs, setValidationActiveTabs] = useState(() =>
    Object.fromEntries(GATEWAYS.map((gateway) => [gateway.id, "latest"]))
  );
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
  const [anomalies, setAnomalies] = useState({
    status: "idle",
    data: { items: [], count: 0, lookback_hours: ANOMALIES_LOOKBACK_HOURS },
    error: null,
  });
  const [waterMetrics, setWaterMetrics] = useState(() => {
    const initial = {};
    WATER_VIEW_CONFIG.forEach((config) => {
      initial[config.id] = {
        series: { status: "idle", data: null, error: null },
        daily: { status: "idle", data: null, error: null },
        monthly: { status: "idle", data: null, error: null },
      };
    });
    return initial;
  });
  const [solarMetrics, setSolarMetrics] = useState(() => {
    const initial = {};
    SOLAR_VIEW_CONFIG.forEach((config) => {
      initial[config.id] = {
        irradiance: { status: "idle", data: null, error: null },
      };
    });
    return initial;
  });
  const waterClientOffsetsRef = useRef(new Map());

  const routeId = resolveRouteId(routeHash);

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
      const realtimeQuery = new URLSearchParams({ water_map_source: WATER_MAP_SOURCE });
      const [jaenPayload, linaresPayload] = await Promise.all([
        fetchWithFallback(`/realtime?campus=jaen&${realtimeQuery.toString()}`),
        fetchWithFallback(`/realtime?campus=linares&${realtimeQuery.toString()}`),
      ]);
      const mergedItems = new Map();
      [jaenPayload, linaresPayload].forEach((payload) => {
        (payload.items || []).forEach((item) => {
          const previous = mergedItems.get(item.rt_id);
          if (!previous || Number(item.ts_event || 0) >= Number(previous.ts_event || 0)) {
            mergedItems.set(item.rt_id, item);
          }
        });
      });
      setRealtime({
        status: "ready",
        data: {
          ts: Math.max(Number(jaenPayload.ts || 0), Number(linaresPayload.ts || 0)),
          items: Array.from(mergedItems.values()).sort((a, b) => a.rt_id.localeCompare(b.rt_id)),
        },
        error: null,
      });
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
      const payload = await fetchWithFallback(
        `/series/24h?scope=${scope.id}&interval_minutes=${ANALYTICS_SERIES_INTERVAL_MINUTES}`
      );
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
      const payload = await fetchWithFallback(`/realtime?${params.toString()}`);
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
      const params = new URLSearchParams({
        campus: gateway.campus,
        metric: gateway.seriesMetric,
      });
      params.set("interval_minutes", String(ANALYTICS_SERIES_INTERVAL_MINUTES));
      const payload = await fetchWithFallback(`/series/24h?${params.toString()}`);
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

  const fetchSolarIrradianceSeries = async (config) => {
    if (!config.irradianceRtIds?.length) {
      setSolarMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          irradiance: { status: "na", data: null, error: null },
        },
      }));
      return;
    }
    try {
      setSolarMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          irradiance: { ...prev[config.id].irradiance, status: "loading", error: null },
        },
      }));
      const params = new URLSearchParams({
        aggregation: "avg",
        interval_minutes: String(ANALYTICS_SERIES_INTERVAL_MINUTES),
      });
      config.irradianceRtIds.forEach((rtId) => params.append("rt_id", rtId));
      const payload = await fetchWithFallback(`/series/24h?${params.toString()}`);
      setSolarMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          irradiance: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setSolarMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          irradiance: { status: "error", data: null, error: error.message },
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

  const fetchAnomalies = async () => {
    try {
      setAnomalies((prev) => ({ ...prev, status: "loading", error: null }));
      const params = new URLSearchParams({
        lookback_hours: String(ANOMALIES_LOOKBACK_HOURS),
        limit: String(ANOMALIES_LIMIT),
      });
      if (campusFilter !== "all") {
        params.set("campus", campusFilter);
      }
      if (validationDomainFilter !== "all" && validationDomainFilter !== "mixto") {
        params.set("domain", validationDomainFilter);
      }
      const payload = await fetchWithFallback(`/anomalies?${params.toString()}`);
      let items = payload.items || [];
      if (validationDomainFilter === "mixto") {
        const mixedGatewayIds = new Set(
          GATEWAYS.filter(
            (gateway) =>
              gateway.domain == null && (campusFilter === "all" || gateway.campus === campusFilter)
          ).map((gateway) => gateway.id)
        );
        items = items.filter((item) => mixedGatewayIds.has(item.gateway_id));
      }
      setAnomalies({
        status: "ready",
        data: { ...payload, items, count: items.length },
        error: null,
      });
    } catch (error) {
      setAnomalies({
        status: "error",
        data: { items: [], count: 0, lookback_hours: ANOMALIES_LOOKBACK_HOURS },
        error: error.message,
      });
    }
  };

  const fetchWaterSeries = async (config) => {
    try {
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          series: { ...prev[config.id].series, status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(
        `/series/24h?campus=${config.campus}&metric=agua_consumo&interval_minutes=${ANALYTICS_SERIES_INTERVAL_MINUTES}`
      );
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          series: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          series: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const fetchWaterAggregates = async (config, period) => {
    try {
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          [period]: { ...prev[config.id][period], status: "loading", error: null },
        },
      }));
      const payload = await fetchWithFallback(
        `/aggregates/${period}?campus=${config.campus}&metric=agua_consumo&asset=total`
      );
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          [period]: { status: "ready", data: payload, error: null },
        },
      }));
    } catch (error) {
      setWaterMetrics((prev) => ({
        ...prev,
        [config.id]: {
          ...prev[config.id],
          [period]: { status: "error", data: null, error: error.message },
        },
      }));
    }
  };

  const refreshScopeData = (scope) => {
    fetchDashboardKpis(scope);
    fetchDashboardSeries(scope);
  };

  const refreshDashboard = () => {
    DASHBOARD_SCOPES.forEach((scope) => {
      refreshScopeData(scope);
    });
  };

  const refreshGatewayData = (gateway) => {
    fetchGatewayLatest(gateway);
    fetchGatewaySeries(gateway);
    fetchGatewayAggregates(gateway, "daily");
    fetchGatewayAggregates(gateway, "monthly");
  };

  const refreshOperationalLatest = () => {
    GATEWAYS.forEach((gateway) => {
      fetchGatewayLatest(gateway);
    });
  };

  const refreshOperationalHistory = () => {
    GATEWAYS.forEach((gateway) => {
      fetchGatewaySeries(gateway);
      fetchGatewayAggregates(gateway, "daily");
      fetchGatewayAggregates(gateway, "monthly");
    });
    SOLAR_VIEW_CONFIG.forEach((config) => {
      fetchSolarIrradianceSeries(config);
    });
  };

  const refreshWaterHistory = () => {
    WATER_VIEW_CONFIG.forEach((config) => {
      fetchWaterSeries(config);
      fetchWaterAggregates(config, "daily");
      fetchWaterAggregates(config, "monthly");
    });
  };

  const refreshWaterData = () => {
    refreshOperationalLatest();
    refreshWaterHistory();
  };

  const refreshOperationalData = () => {
    refreshOperationalLatest();
    refreshOperationalHistory();
  };

  const refreshValidationData = () => {
    refreshOperationalData();
    fetchAnomalies();
  };

  const refreshPortal = () => {
    fetchRealtime();
    refreshDashboard();
    refreshOperationalData();
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
    refreshOperationalLatest();
    const interval = setInterval(refreshOperationalLatest, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    refreshOperationalHistory();
    const interval = setInterval(refreshOperationalHistory, 300000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    refreshWaterHistory();
    const interval = setInterval(refreshWaterHistory, 300000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (routeId !== "validation") return undefined;
    fetchAnomalies();
    const interval = setInterval(fetchAnomalies, 60000);
    return () => clearInterval(interval);
  }, [routeId, campusFilter, validationDomainFilter]);

  useEffect(() => {
    const handleHash = () => setRouteHash(window.location.hash || "#/");
    window.addEventListener("hashchange", handleHash);
    return () => window.removeEventListener("hashchange", handleHash);
  }, []);

  const formatValue = (value, unit) => (value == null ? "--" : `${number.format(value)} ${unit}`);

  const getLastAggregateValue = (series) => {
    if (!series?.length) return null;
    return series[series.length - 1].value ?? null;
  };

  const getAnnualValue = (series) => {
    if (!series?.length) return null;
    return series.reduce((sum, item) => sum + Number(item.value || 0), 0);
  };

  const getEnvironmentalImpact = (annualKwh) => {
    if (annualKwh == null) {
      return { avoidedCo2Ton: null, equivalentTrees: null };
    }
    return {
      avoidedCo2Ton: annualKwh * CO2_EMISSIONS_COEFFICIENT_TON_PER_KWH,
      equivalentTrees: annualKwh / CARBON_FOOTPRINT_COEFFICIENT_KWH_PER_TREE,
    };
  };

  const getStatusKind = (status) => {
    if (status === "ready") return "complete";
    if (status === "loading") return "loading";
    if (status === "error") return "error";
    return "idle";
  };

  const isPowerItem = (item) => {
    const rtId = item.rt_id || "";
    const unit = (item.unit || "").toLowerCase();
    return (
      unit === "kw" ||
      rtId.endsWith(".p_kw") ||
      rtId.endsWith(".p_ac_kw") ||
      rtId.includes(".p_kw") ||
      rtId.includes(".p_ac_kw")
    );
  };

  const getPrimaryLatest = (items) => {
    if (!items.length) return { value: null, unit: "--", ts: null };

    const powerItems = items.filter(isPowerItem);
    const preferredItems = powerItems.length ? powerItems : items;
    const ctTotal = preferredItems.find(
      (item) => item.rt_id?.includes("ct_total") && isPowerItem(item)
    );
    if (ctTotal) {
      return {
        value: ctTotal.value,
        unit: ctTotal.unit || "kW",
        ts: ctTotal.ts_event || null,
        rtId: ctTotal.rt_id || null,
      };
    }
    if (preferredItems.length === 1) {
      return {
        value: preferredItems[0].value,
        unit: preferredItems[0].unit || "kW",
        ts: preferredItems[0].ts_event || null,
        rtId: preferredItems[0].rt_id || null,
      };
    }
    return {
      value: preferredItems.reduce((sum, item) => sum + Number(item.value || 0), 0),
      unit: preferredItems[0].unit || "kW",
      ts: preferredItems.reduce((maxTs, item) => Math.max(maxTs, Number(item.ts_event || 0)), 0),
      rtId: null,
    };
  };

  const getGatewayDisplayLatest = (gateway, items) => {
    const fallback = { primary: getPrimaryLatest(items), secondary: null };
    if (!items.length || gateway.domain !== "fv") return fallback;

    if (gateway.id === "gw_endesa_jaen") {
      const ctTotal = items.find(
        (item) => item.rt_id === JAEN_ENDESA_CT_TOTAL_RT_ID && isPowerItem(item)
      );
      const inverterItems = items.filter(
        (item) =>
          isPowerItem(item) && item.rt_id?.startsWith(JAEN_ENDESA_INVERTER_RT_PREFIX)
      );

      return {
        primary: ctTotal
          ? {
              value: Math.abs(Number(ctTotal.value || 0)),
              unit: ctTotal.unit || "kW",
              ts: ctTotal.ts_event || null,
              rtId: ctTotal.rt_id || null,
            }
          : fallback.primary,
        secondary: inverterItems.length
          ? {
              label: "Suma inversores",
              value: inverterItems.reduce(
                (sum, item) => sum + Math.abs(Number(item.value || 0)),
                0
              ),
              unit: inverterItems[0].unit || "kW",
              ts: inverterItems.reduce(
                (maxTs, item) => Math.max(maxTs, Number(item.ts_event || 0)),
                0
              ),
            }
          : null,
      };
    }

    if (fallback.primary.rtId?.includes("ct_total")) {
      return {
        primary: {
          ...fallback.primary,
          value:
            fallback.primary.value == null ? fallback.primary.value : Math.abs(fallback.primary.value),
        },
        secondary: null,
      };
    }

    return fallback;
  };

  const pickMetricSnapshot = ({
    currentLabel,
    currentValue,
    currentUnit,
    dailyLabel,
    dailyValue,
    dailyUnit,
    monthlyLabel,
    monthlyValue,
    monthlyUnit,
  }) => {
    if (periodFilter === "daily") {
      return { label: dailyLabel, value: dailyValue, unit: dailyUnit };
    }
    if (periodFilter === "monthly") {
      return { label: monthlyLabel, value: monthlyValue, unit: monthlyUnit };
    }
    return { label: currentLabel, value: currentValue, unit: currentUnit };
  };

  const realtimeItems = useMemo(() => realtime.data?.items || [], [realtime.data]);

  const realtimeMap = useMemo(() => {
    const map = new Map();
    realtimeItems.forEach((item) => map.set(item.rt_id, item));
    return map;
  }, [realtimeItems]);

  const getMapEntryReading = (entry) => {
    const items = entry.rtIds
      .map((rtId) => realtimeMap.get(rtId))
      .filter(Boolean);

    if (!items.length) {
      return {
        value: null,
        unit: getDefaultMapUnit(entry.layer),
        tsEvent: null,
        availableCount: 0,
        totalCount: entry.rtIds.length,
        isPartial: false,
      };
    }

    let value =
      entry.aggregate === "sum"
        ? items.reduce((sum, item) => sum + Number(item.value || 0), 0)
        : Number(items[0].value || 0);

    if (entry.layer === "water" && WATER_MAP_SOURCE === "client_offset") {
      const normalizedItems = items.map((item) => {
        const key = item.rt_id;
        const currentValue = Number(item.value || 0);
        if (!waterClientOffsetsRef.current.has(key)) {
          waterClientOffsetsRef.current.set(key, currentValue);
        }
        const baseline = Number(waterClientOffsetsRef.current.get(key) || 0);
        return Math.max(0, currentValue - baseline);
      });
      value =
        entry.aggregate === "sum"
          ? normalizedItems.reduce((sum, itemValue) => sum + itemValue, 0)
          : normalizedItems[0];
    }

    return {
      value,
      unit: items[0].unit || getDefaultMapUnit(entry.layer),
      tsEvent: Math.max(...items.map((item) => Number(item.ts_event || 0))),
      availableCount: items.length,
      totalCount: entry.rtIds.length,
      isPartial: items.length < entry.rtIds.length,
    };
  };

  const getMapEntryPosition = (entry) => {
    if (mapLayer !== "all") {
      return {
        left: `${clampPercent(entry.x)}%`,
        top: `${clampPercent(entry.y)}%`,
      };
    }

    const offset = MAP_LAYER_OFFSETS[entry.layer] || { x: 0, y: 0 };
    return {
      left: `${clampPercent(entry.x + offset.x)}%`,
      top: `${clampPercent(entry.y + offset.y)}%`,
    };
  };

  const dashboardOverview = useMemo(() => {
    const result = {};
    DASHBOARD_SCOPES.forEach((scope) => {
      const state = dashboard[scope.id] || {};
      const status = resolveDashboardStatus(state.kpis || {}, state.series || {});
      result[scope.id] = {
        scope,
        campus: scope.id === "las_lagunillas" ? "jaen" : "linares",
        status,
        title: state.kpis?.data?.label || state.series?.data?.label || scope.title,
        demand: readKpiValue(state.kpis?.data, "demanda_kw"),
        pv: readKpiValue(state.kpis?.data, "fv_kw"),
        grid: readKpiValue(state.kpis?.data, "red_kw"),
        autoconsumoPct: readKpiValue(state.kpis?.data, "autoconsumo_pct"),
        chartSeries: state.series?.data?.series || [],
        tsEvent: state.kpis?.data?.ts_event || null,
      };
    });
    return result;
  }, [dashboard]);

  const gatewayOverview = useMemo(() => {
    const result = {};
    GATEWAYS.forEach((gateway) => {
      const state = validation[gateway.id] || {};
      const latestItems = state.latest?.data?.items || [];
      const displayLatest = getGatewayDisplayLatest(gateway, latestItems);
      result[gateway.id] = {
        gateway,
        latestItems,
        seriesItems: state.series?.data?.series || [],
        seriesUnit: state.series?.data?.unit || "--",
        dailySeries: state.daily?.data?.series || [],
        monthlySeries: state.monthly?.data?.series || [],
        latestStatus: state.latest?.status || "idle",
        seriesStatus: state.series?.status || "idle",
        dailyStatus: state.daily?.status || "idle",
        monthlyStatus: state.monthly?.status || "idle",
        latestValue: displayLatest.primary.value,
        latestUnit: displayLatest.primary.unit,
        latestTs: displayLatest.primary.ts,
        secondaryLatestValue: displayLatest.secondary?.value ?? null,
        secondaryLatestUnit: displayLatest.secondary?.unit ?? "--",
        secondaryLatestLabel: displayLatest.secondary?.label ?? null,
        secondaryLatestTs: displayLatest.secondary?.ts ?? null,
        dailyValue: getLastAggregateValue(state.daily?.data?.series || []),
        dailyUnit: state.daily?.data?.unit || "--",
        monthlyValue: getLastAggregateValue(state.monthly?.data?.series || []),
        monthlyUnit: state.monthly?.data?.unit || state.daily?.data?.unit || "--",
        annualValue: getAnnualValue(state.monthly?.data?.series || []),
        annualUnit: state.monthly?.data?.unit || state.daily?.data?.unit || "--",
      };
    });
    return result;
  }, [validation]);

  const waterOverview = useMemo(() => {
    const result = {};
    WATER_VIEW_CONFIG.forEach((config) => {
      const latest = gatewayOverview[config.gatewayId] || {};
      const metrics = waterMetrics[config.id] || {};
      result[config.id] = {
        latestItems: latest.latestItems || [],
        latestStatus: latest.latestStatus || "idle",
        seriesItems: metrics.series?.data?.series || [],
        seriesUnit: metrics.series?.data?.unit || "--",
        seriesStatus: metrics.series?.status || "idle",
        dailyValue: getLastAggregateValue(metrics.daily?.data?.series || []),
        dailyUnit: metrics.daily?.data?.unit || "--",
        monthlyValue: getLastAggregateValue(metrics.monthly?.data?.series || []),
        monthlyUnit: metrics.monthly?.data?.unit || metrics.daily?.data?.unit || "--",
        annualValue: getAnnualValue(metrics.monthly?.data?.series || []),
        annualUnit: metrics.monthly?.data?.unit || metrics.daily?.data?.unit || "--",
      };
    });
    return result;
  }, [gatewayOverview, waterMetrics]);

  const validationSummary = useMemo(() => {
    let errors = 0;
    let loading = 0;
    let ready = 0;
    let lastSync = 0;

    GATEWAYS.forEach((gateway) => {
      const summary = gatewayOverview[gateway.id];
      const statuses = [
        summary?.latestStatus,
        summary?.seriesStatus,
        summary?.dailyStatus,
        summary?.monthlyStatus,
      ];
      if (statuses.includes("error")) {
        errors += 1;
      } else if (statuses.includes("loading")) {
        loading += 1;
      } else if (statuses.includes("ready")) {
        ready += 1;
      }
      lastSync = Math.max(lastSync, Number(summary?.latestTs || 0));
    });

    return {
      errors,
      loading,
      ready,
      lastSync,
    };
  }, [gatewayOverview]);

  const solarOverview = useMemo(() => {
    const result = {};
    SOLAR_VIEW_CONFIG.forEach((config) => {
      const summary = gatewayOverview[config.gatewayId] || {};
      const irradiance = solarMetrics[config.id]?.irradiance || {};
      result[config.id] = {
        ...summary,
        irradianceItems: irradiance.data?.series || [],
        irradianceUnit: irradiance.data?.unit || "W/m²",
        irradianceStatus: irradiance.status || "idle",
      };
    });
    return result;
  }, [gatewayOverview, solarMetrics]);

  const anomaliesRows = useMemo(() => {
    return (anomalies.data?.items || [])
      .map((item) => ({
        sortTs: Number(item.ts_event || 0),
        cells: [
          formatTs(item.ts_event),
          GATEWAY_LABELS[item.gateway_id] || item.gateway_id || "--",
          getMonitoringPointLabel(item.rt_id),
          item.rt_id || "--",
          formatScalar(item.raw_value),
          formatScalar(item.applied_value),
          item.unit || "--",
          ANOMALY_TYPE_LABELS[item.anomaly_type] || item.anomaly_type || "--",
          item.reason || "--",
        ],
      }))
      .sort((left, right) => right.sortTs - left.sortTs)
      .map((item) => item.cells);
  }, [anomalies.data]);

  const visibleMapEntries = useMemo(() => {
    if (mapLayer === "all") return MAP_ENTRIES;
    return MAP_ENTRIES.filter((entry) => entry.layer === mapLayer);
  }, [mapLayer]);

  useEffect(() => {
    if (routeId !== "map") return;
    if (!visibleMapEntries.length) {
      setSelectedMapPoint(null);
      return;
    }
    if (!visibleMapEntries.some((entry) => entry.id === selectedMapPoint)) {
      setSelectedMapPoint(visibleMapEntries[0].id);
    }
  }, [routeId, selectedMapPoint, visibleMapEntries]);

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
              {columns.map((col, colIdx) => (
                <th key={`${col}-${colIdx}`} scope="col">
                  {col}
                </th>
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
    const activeTab = validationActiveTabs[gateway.id] || "latest";
    const latestItems = state.latest?.data?.items || [];
    const latestRows = latestItems
      .map((item) => ({
        sortLabel: getMonitoringPointLabel(item.rt_id),
        cells: [
          getMonitoringPointLabel(item.rt_id),
          item.rt_id,
          number.format(item.value),
          item.unit || "kW",
          formatTs(item.ts_event),
        ],
      }))
      .sort((left, right) => left.sortLabel.localeCompare(right.sortLabel, "es"))
      .map((item) => item.cells);

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

    const tabPanels = {
      latest: {
        label: "Último valor",
        title: "Último valor disponible",
        status: state.latest || {},
        content: renderTable(
          ["Punto", "rt_id", "Valor", "Unidad", "Última lectura"],
          latestRows
        ),
      },
      series: {
        label: "24h",
        title: "Últimas 24 horas",
        status: state.series || {},
        content: renderTable(
          usesValueSeries
            ? ["Fecha/hora", "Valor", "Unidad"]
            : ["Fecha/hora", "Demanda", "Unidad", "FV", "Unidad"],
          seriesRowsLocal
        ),
      },
      daily: {
        label: "Diario",
        title: labels.daily,
        status: state.daily || {},
        content: renderTable(["Periodo", "Valor", "Unidad"], dailyRows),
      },
      monthly: {
        label: "Mensual",
        title: labels.monthly,
        status: state.monthly || {},
        content: renderTable(["Periodo", "Valor", "Unidad"], monthlyRows),
      },
    };

    const activePanel = tabPanels[activeTab] || tabPanels.latest;

    return (
      <article key={gateway.id} className="gateway-card">
        <div className="gateway-header">
          <div>
            <h3 className="gateway-title">{gateway.label}</h3>
            <div className="gateway-topic">{gateway.topic}</div>
          </div>
          <button
            className="action-button action-button-secondary action-button-compact"
            type="button"
            aria-label={`Actualizar ${gateway.label}`}
            onClick={() => refreshGatewayData(gateway)}
          >
            Actualizar
          </button>
        </div>
        <div className="gateway-tabs" role="tablist" aria-label={`Datos de ${gateway.label}`}>
          {VALIDATION_TAB_OPTIONS.map((tab) => {
            const tabState = tabPanels[tab.id]?.status || {};
            const isActive = tab.id === activeTab;
            return (
              <button
                key={tab.id}
                type="button"
                role="tab"
                id={`${gateway.id}-${tab.id}-tab`}
                aria-selected={isActive}
                aria-controls={`${gateway.id}-${tab.id}-panel`}
                className={`gateway-tab${isActive ? " is-active" : ""}`}
                onClick={() =>
                  setValidationActiveTabs((prev) => ({ ...prev, [gateway.id]: tab.id }))
                }
              >
                <span className="gateway-tab-label">{tab.label}</span>
                <span className={`gateway-tab-status status-${tabState.status || "idle"}`}>
                  {renderStatus(tabState)}
                </span>
              </button>
            );
          })}
        </div>
        <div
          className="gateway-panel api-card gateway-panel-card"
          role="tabpanel"
          id={`${gateway.id}-${activeTab}-panel`}
          aria-labelledby={`${gateway.id}-${activeTab}-tab`}
        >
          <div className="gateway-panel-header">
            <h4 className="api-card-title">{activePanel.title}</h4>
            <div className={`api-status status-${activePanel.status.status || "idle"}`}>
              {renderStatus(activePanel.status)}
            </div>
          </div>
          {activePanel.content}
        </div>
      </article>
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
    const chartDensity = filteredEnergyConfigs.length === 1 ? "single" : "split";

    return (
      <article key={scope.id} className={`dashboard-panel panel-${panelStatus.kind}`}>
        <div className="dashboard-panel-header">
          <div>
            <h3 className="dashboard-panel-title">{title}</h3>
            <div className={`dashboard-status status-${panelStatus.kind}`}>
              {panelStatus.label}
            </div>
          </div>
          <button
            className="action-button action-button-secondary action-button-compact"
            type="button"
            aria-label={`Actualizar ${title}`}
            onClick={() => refreshScopeData(scope)}
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
          <div className="chart-card">
            <div className="chart-legend">
              <span className="legend-item demand">Curva Demanda kW</span>
              <span className="legend-item pv">Curva Generación kW</span>
            </div>
            {isComplete && chartSeries.length ? (
              <AreaChart series={chartSeries} unit="kW" density={chartDensity} />
            ) : (
              <div className="chart-empty">{chartEmptyText}</div>
            )}
          </div>
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
        </div>
      </article>
    );
  };

  const buildSummaryCampusCard = (config) => {
    const scopeSummary = dashboardOverview[config.scopeId];
    const campusLabel = scopeSummary?.title || config.label;

    return (
      <article key={config.scopeId} className="summary-campus-card">
        <div className="summary-card-header">
          <div>
            <h3 className="summary-card-title">{campusLabel}</h3>
            <div className={`dashboard-status status-${scopeSummary?.status?.kind || "idle"}`}>
              {scopeSummary?.status?.label || "Sin datos"}
            </div>
          </div>
        </div>
        <div className="summary-diagram-shell">
          <EnergyFlowDiagram
            campusLabel={campusLabel}
            gridPower={scopeSummary?.grid}
            consumption={scopeSummary?.demand}
            generation={scopeSummary?.pv}
            autoconsumption={scopeSummary?.autoconsumoPct}
          />
        </div>
        <span className="summary-card-copy">Última actualización {formatTs(scopeSummary?.tsEvent)}</span>
        {scopeSummary?.chartSeries?.length ? (
          <div className="summary-chart">
            <div className="chart-legend">
              <span className="legend-item demand">Curva Demanda kW</span>
              <span className="legend-item pv">Curva Generación kW</span>
            </div>
            <AreaChart series={scopeSummary.chartSeries} unit="kW" />
          </div>
        ) : (
          <div className="chart-empty">Sin curva resumida disponible.</div>
        )}
      </article>
    );
  };

  const buildWaterRows = (latestItems, config) => {
    const rows = (latestItems || [])
      .filter((item) => item.rt_id?.startsWith(config.prefix))
      .map((item) => ({
        sortLabel: getMonitoringPointLabel(item.rt_id),
        cells: [
          getMonitoringPointLabel(item.rt_id),
          number.format(item.value),
          item.unit || "m3",
          formatTs(item.ts_event),
        ],
      }))
      .sort((left, right) => left.sortLabel.localeCompare(right.sortLabel, "es"))
      .map((item) => item.cells);
    return rows;
  };

  const pageMeta = {
    summary: {
      title: "Balance general",
      subtitle:
        "Estado general de energía y producción en Las Lagunillas y Campus Científico Tecnológico de Linares.",
      primaryLabel: "Actualizar balance",
      primaryAction: refreshPortal,
    },
    energy: {
      title: "Explotación energética",
      subtitle:
        "Vista operativa para demanda, red, generación y acumulados por campus.",
      primaryLabel: "Actualizar energía",
      primaryAction: refreshDashboard,
    },
    map: {
      title: "Mapa de campus",
      subtitle:
        "Vista cartográfica operativa con la capa de demanda de energía y detalle del punto seleccionado.",
      primaryLabel: "Actualizar mapa",
      primaryAction: fetchRealtime,
    },
    water: {
      title: "Monitorización de agua",
      subtitle:
        "Sección tabular y analítica para consumo de agua por campus y punto de medida.",
      primaryLabel: "Actualizar agua",
      primaryAction: refreshWaterData,
    },
    solar: {
      title: "Monitorización fotovoltaica",
      subtitle:
        "Explotación unificada de plantas FV y autoconsumo con KPIs, producción, irradiancia y curvas.",
      primaryLabel: "Actualizar FV",
      primaryAction: refreshOperationalData,
    },
    validation: {
      title: "Validación de datos",
      subtitle:
        "Módulo técnico para incidencias, datos faltantes, series y agregados por gateway.",
      primaryLabel: "Actualizar validación",
      primaryAction: refreshValidationData,
    },
  }[routeId];

  const filteredEnergyConfigs = ENERGY_VIEW_CONFIG.filter(
    (config) => campusFilter === "all" || config.campus === campusFilter
  );
  const summaryEnergyConfigs = ENERGY_VIEW_CONFIG;
  const filteredWaterConfigs = WATER_VIEW_CONFIG.filter(
    (config) => campusFilter === "all" || config.campus === campusFilter
  );
  const filteredSolarConfigs = SOLAR_VIEW_CONFIG.filter(
    (config) => campusFilter === "all" || config.campus === campusFilter
  );
  const filteredValidationGateways = GATEWAYS.filter((gateway) => {
    const domain = gateway.domain || "mixto";
    return (
      (campusFilter === "all" || gateway.campus === campusFilter) &&
      (validationDomainFilter === "all" || validationDomainFilter === domain)
    );
  });

  const selectedMapData = selectedMapPoint
    ? visibleMapEntries.find((entry) => entry.id === selectedMapPoint) || null
    : null;
  const selectedMapReading = selectedMapData ? getMapEntryReading(selectedMapData) : null;

  const renderToolbar = () => {
    const controls = [];
    const addCampusControl = !["summary", "map"].includes(routeId);
    const addPeriodControl = !["summary", "map", "validation"].includes(routeId);

    if (addCampusControl) {
      controls.push(
        <label key="campus" className="toolbar-field">
          <span className="toolbar-label">Campus</span>
          <select
            className="toolbar-select"
            value={campusFilter}
            onChange={(event) => setCampusFilter(event.target.value)}
          >
            {CAMPUS_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (addPeriodControl) {
      controls.push(
        <label key="period" className="toolbar-field">
          <span className="toolbar-label">Periodo</span>
          <select
            className="toolbar-select"
            value={periodFilter}
            onChange={(event) => setPeriodFilter(event.target.value)}
          >
            {PERIOD_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (routeId === "map") {
      controls.push(
        <label key="layer" className="toolbar-field">
          <span className="toolbar-label">Capa</span>
          <select
            className="toolbar-select"
            value={mapLayer}
            onChange={(event) => setMapLayer(event.target.value)}
          >
            {MAP_LAYER_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      );
    }

    if (routeId === "validation") {
      controls.push(
        <label key="domain" className="toolbar-field">
          <span className="toolbar-label">Dominio</span>
          <select
            className="toolbar-select"
            value={validationDomainFilter}
            onChange={(event) => setValidationDomainFilter(event.target.value)}
          >
            {VALIDATION_DOMAIN_OPTIONS.map((option) => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        </label>
      );
    }

    let note = "Vista operativa lista.";
    if (routeId === "map") {
      note = `${visibleMapEntries.length} puntos visibles en la capa actual.`;
    } else if (routeId === "validation") {
      note = `${filteredValidationGateways.length} gateways visibles en seguimiento.`;
    } else if (routeId === "solar") {
      note = `${filteredSolarConfigs.length} instalaciones FV visibles.`;
    } else if (routeId === "summary") {
      note = `${summaryEnergyConfigs.length} campus en seguimiento.`;
    }

    return (
      <div className="view-toolbar">
        <div className="container view-toolbar-inner">
          <div className="view-toolbar-controls">{controls}</div>
          <div className="view-toolbar-note">{note}</div>
        </div>
      </div>
    );
  };

  const renderSummaryView = () => {
    const shortcuts = [
      {
        href: "#/energia",
        title: "Energía",
        copy: "Balance operativo, curvas y acumulados por campus.",
        status: `${summaryEnergyConfigs.length} campus activos`,
      },
      {
        href: "#/mapa",
        title: "Mapa campus",
        copy: "Vista cartográfica operativa con la capa activa de demanda y detalle de puntos.",
        status: `${ACTIVE_MAP_ENTRY_COUNT} puntos cartográficos visibles`,
      },
      {
        href: "#/agua",
        title: "Agua",
        copy: "Tabla operativa, totales y seguimiento del consumo.",
        status: `${WATER_VIEW_CONFIG.length} áreas disponibles`,
      },
      {
        href: "#/fotovoltaica",
        title: "Fotovoltaica",
        copy: "Explotación unificada por instalación, incluyendo autoconsumo e irradiancia.",
        status: `${SOLAR_VIEW_CONFIG.length} instalaciones`,
      },
      {
        href: "#/validacion",
        title: "Validación",
        copy: "Gateway por gateway, con incidencias y series técnicas.",
        status: `${validationSummary.errors} incidencias abiertas`,
      },
    ];

    return (
      <>
        <section className="section">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Balance energético por campus</h2>
              <p className="section-subtitle">Seguimiento simultáneo de Las Lagunillas y Campus Científico Tecnológico de Linares.</p>
            </div>
            <div className="summary-campus-grid">
              {summaryEnergyConfigs.map((config) => buildSummaryCampusCard(config))}
            </div>
          </div>
        </section>

        <section className="section">
          <div className="container">
            <div className="section-header">
              <h2 className="section-title">Accesos operativos</h2>
              <p className="section-subtitle">Acceso directo a los módulos principales del portal.</p>
            </div>
            <div className="shortcut-grid">
              {shortcuts.map((shortcut) => (
                <a key={shortcut.href} className="shortcut-card" href={shortcut.href}>
                  <span className="shortcut-card-title">{shortcut.title}</span>
                  <span className="shortcut-card-copy">{shortcut.copy}</span>
                  <span className="shortcut-card-status">{shortcut.status}</span>
                </a>
              ))}
            </div>
          </div>
        </section>
      </>
    );
  };

  const renderEnergyView = () => (
    <>
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Banda de KPIs y acumulados</h2>
            <p className="section-subtitle">Balance actual y acumulados por campus.</p>
          </div>
          <div className="insight-grid">
            {filteredEnergyConfigs.map((config) => {
              const scopeSummary = dashboardOverview[config.scopeId];
              const energySummary = gatewayOverview[config.gatewayId];
              const environmentalImpact = getEnvironmentalImpact(energySummary?.annualValue);
              const highlighted = pickMetricSnapshot({
                currentLabel: "Demanda actual",
                currentValue: scopeSummary?.demand,
                currentUnit: "kW",
                dailyLabel: "Energía diaria",
                dailyValue: energySummary?.dailyValue,
                dailyUnit: energySummary?.dailyUnit,
                monthlyLabel: "Energía mensual",
                monthlyValue: energySummary?.monthlyValue,
                monthlyUnit: energySummary?.monthlyUnit,
              });
              return (
                <article key={config.scopeId} className="insight-card">
                  <span className="insight-label">{scopeSummary?.title || config.label}</span>
                  <strong className="insight-value">
                    {formatValue(highlighted.value, highlighted.unit)}
                  </strong>
                  <span className="insight-note">{highlighted.label}</span>
                  <span className="insight-note">
                    Autoconsumo {formatValue(scopeSummary?.autoconsumoPct, "%")}
                  </span>
                  <div className="insight-environment">
                    <span className="insight-environment-title">Impacto medioambiental</span>
                    <span className="insight-environment-note">
                      Emisiones evitadas acumuladas este año
                    </span>
                    <span className="insight-environment-value">
                      {formatValue(environmentalImpact.avoidedCo2Ton, "tn/CO2")} (
                      {formatValue(environmentalImpact.equivalentTrees, "árboles")})
                    </span>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Paneles operativos por campus</h2>
            <p className="section-subtitle">Curvas y métricas de operación por campus.</p>
          </div>
          <div className="dashboard-panels">
            {filteredEnergyConfigs.map((config) => {
              const scope = DASHBOARD_SCOPES.find((item) => item.id === config.scopeId);
              return scope ? buildDashboardPanel(scope) : null;
            })}
          </div>
        </div>
      </section>
    </>
  );

  const renderMapView = () => (
    <section className="section">
      <div className="container">
        <div className="section-header">
          <h2 className="section-title">Mapa operacional</h2>
          <p className="section-subtitle">
            Consulte el detalle del punto de demanda seleccionado debajo del plano.
          </p>
          {mapLayer === "water" || mapLayer === "all" ? (
            <p className="section-subtitle">
              Fuente agua activa: <strong>{WATER_MAP_SOURCE}</strong>.
            </p>
          ) : null}
        </div>
        <div className="map-layout">
          <div className="map-frame map-workspace">
            <div className="map-canvas">
              <img
                src={campus}
                alt="Plano del campus con puntos de lectura energética destacados"
              />
              {visibleMapEntries.map((entry) => {
                const reading = getMapEntryReading(entry);
                const valueText =
                  reading.value == null ? "--" : formatValue(reading.value, reading.unit);
                const isActive = entry.id === selectedMapPoint;
                return (
                  <button
                    key={entry.id}
                    className={`map-pin layer-${entry.layer} ${isActive ? "is-active" : ""}`}
                    style={getMapEntryPosition(entry)}
                    type="button"
                    onClick={() => setSelectedMapPoint(entry.id)}
                    aria-label={`${entry.detailLabel}: ${valueText}`}
                  >
                    <span className="map-pin-icon" aria-hidden="true">
                      {renderMapLayerIcon(entry.icon)}
                    </span>
                    <span className="map-pin-value">{valueText}</span>
                  </button>
                );
              })}
            </div>
          </div>
          <article className="api-card map-detail-card">
            <h3 className="api-card-title">Detalle del punto</h3>
            {selectedMapData ? (
              <div className="detail-stack">
                <div className="detail-row">
                  <span className="detail-key">Elemento</span>
                  <span className="detail-value">{selectedMapData.detailLabel}</span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Capa</span>
                  <span className="detail-value">
                    {MAP_LAYER_OPTIONS.find((option) => option.value === selectedMapData.layer)?.label}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Valor</span>
                  <span className="detail-value">
                    {selectedMapReading
                      ? selectedMapReading.value == null
                        ? "--"
                        : `${formatValue(selectedMapReading.value, selectedMapReading.unit)}${
                            selectedMapReading.isPartial ? " · parcial" : ""
                          }`
                      : "--"}
                  </span>
                </div>
                <div className="detail-row">
                  <span className="detail-key">Última lectura</span>
                  <span className="detail-value">{formatTs(selectedMapReading?.tsEvent)}</span>
                </div>
                {selectedMapData.rtIds.length > 1 ? (
                  <div className="detail-row">
                    <span className="detail-key">Variables incluidas</span>
                    <span className="detail-value">
                      {selectedMapData.rtIds.map((rtId) => getMonitoringPointLabel(rtId)).join(", ")}
                      {selectedMapReading?.availableCount != null
                        ? ` · ${selectedMapReading.availableCount}/${selectedMapReading.totalCount} disponibles`
                        : ""}
                    </span>
                  </div>
                ) : null}
              </div>
            ) : (
              <div className="chart-empty">
                No hay puntos visibles para la capa seleccionada.
              </div>
            )}
          </article>
        </div>
      </div>
    </section>
  );

  const renderWaterView = () => (
    <>
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Consumo y acumulados de agua</h2>
            <p className="section-subtitle">
              La tabla pasa a ser protagonista y se combina con totales por campus y curva
              cuando el backend ya la sirve.
            </p>
          </div>
          <div className="insight-grid">
            {filteredWaterConfigs.map((config) => {
              const summary = waterOverview[config.id];
              const rows = buildWaterRows(summary?.latestItems || [], config);
              const highlighted = pickMetricSnapshot({
                currentLabel: "Puntos con lectura",
                currentValue: rows.length,
                currentUnit: "",
                dailyLabel: "Consumo diario",
                dailyValue: summary?.dailyValue,
                dailyUnit: summary?.dailyUnit,
                monthlyLabel: "Consumo mensual",
                monthlyValue: summary?.monthlyValue,
                monthlyUnit: summary?.monthlyUnit,
              });
              return (
                <article key={config.id} className="insight-card">
                  <span className="insight-label">{config.label}</span>
                  <strong className="insight-value">
                    {highlighted.unit
                      ? formatValue(highlighted.value, highlighted.unit)
                      : number.format(highlighted.value || 0)}
                  </strong>
                  <span className="insight-note">{highlighted.label}</span>
                  <span className="insight-note">
                    Anual {formatValue(summary?.annualValue, summary?.annualUnit)}
                  </span>
                </article>
              );
            })}
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <div className="water-stack">
            {filteredWaterConfigs.map((config) => {
              const summary = waterOverview[config.id];
              const rows = buildWaterRows(summary?.latestItems || [], config);
              const canRenderTrend = Boolean(summary?.seriesItems?.length);
              return (
                <article key={config.id} className="gateway-card">
                  <div className="gateway-header">
                    <div>
                      <h3 className="gateway-title">Agua {config.label}</h3>
                      <div className="gateway-topic">
                        Lectura instantánea y acumulados por campus.
                      </div>
                    </div>
                    <div className={`dashboard-status status-${getStatusKind(summary?.latestStatus)}`}>
                      {renderStatus({ status: summary?.latestStatus })}
                    </div>
                  </div>
                  <div className="water-detail-grid">
                    <div className="api-card">
                      <h4 className="api-card-title">Tabla operativa</h4>
                      {renderTable(["Punto", "Actual", "Unidad", "Última lectura"], rows)}
                    </div>
                    <div className="api-card">
                      <h4 className="api-card-title">Tendencia y totales</h4>
                      {canRenderTrend ? (
                    <ValueChart
                      series={summary.seriesItems}
                      label={`Agua ${config.label}`}
                      unit={summary?.seriesUnit || "m3"}
                      intervalMinutes={ANALYTICS_SERIES_INTERVAL_MINUTES}
                      density="single"
                    />
                  ) : (
                        <div className="chart-empty">Sin serie operativa disponible todavía.</div>
                      )}
                      <div className="detail-stack compact-detail-stack">
                        <div className="detail-row">
                          <span className="detail-key">Diario</span>
                          <span className="detail-value">
                            {formatValue(summary?.dailyValue, summary?.dailyUnit)}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-key">Mensual</span>
                          <span className="detail-value">
                            {formatValue(summary?.monthlyValue, summary?.monthlyUnit)}
                          </span>
                        </div>
                        <div className="detail-row">
                          <span className="detail-key">Anual</span>
                          <span className="detail-value">
                            {formatValue(summary?.annualValue, summary?.annualUnit)}
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );

  const renderSolarView = () => (
    <>
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Instalaciones fotovoltaicas</h2>
            <p className="section-subtitle">
              El módulo integra producción FV y autoconsumo con KPIs unificados, curva de potencia
              e irradiancia agregada por instalación.
            </p>
          </div>
          <div className="solar-stack">
            {filteredSolarConfigs.map((config) => {
              const summary = solarOverview[config.id];
              const highlighted = pickMetricSnapshot({
                currentLabel: "Potencia instantánea",
                currentValue: summary?.latestValue,
                currentUnit: summary?.latestUnit,
                dailyLabel: "Producción diaria",
                dailyValue: summary?.dailyValue,
                dailyUnit: summary?.dailyUnit,
                monthlyLabel: "Producción mensual",
                monthlyValue: summary?.monthlyValue,
                monthlyUnit: summary?.monthlyUnit,
              });
              return (
                <article key={config.id} className="gateway-card">
                  <div className="gateway-header">
                    <div>
                      <h3 className="gateway-title">{config.label}</h3>
                      <div className="gateway-topic">{config.description}</div>
                    </div>
                    <div className={`dashboard-status status-${getStatusKind(summary?.latestStatus)}`}>
                      {renderStatus({ status: summary?.latestStatus })}
                    </div>
                  </div>
                  <div className="summary-metric-grid">
                    <div className="summary-metric">
                      <span className="summary-metric-label">{highlighted.label}</span>
                      <strong className="summary-metric-value">
                        {formatValue(highlighted.value, highlighted.unit)}
                      </strong>
                    </div>
                    {summary?.secondaryLatestLabel ? (
                      <div className="summary-metric">
                        <span className="summary-metric-label">{summary.secondaryLatestLabel}</span>
                        <strong className="summary-metric-value">
                          {formatValue(summary.secondaryLatestValue, summary.secondaryLatestUnit)}
                        </strong>
                      </div>
                    ) : null}
                    <div className="summary-metric">
                      <span className="summary-metric-label">Producción diaria</span>
                      <strong className="summary-metric-value">
                        {formatValue(summary?.dailyValue, summary?.dailyUnit)}
                      </strong>
                    </div>
                    <div className="summary-metric">
                      <span className="summary-metric-label">Producción mensual</span>
                      <strong className="summary-metric-value">
                        {formatValue(summary?.monthlyValue, summary?.monthlyUnit)}
                      </strong>
                    </div>
                    <div className="summary-metric">
                      <span className="summary-metric-label">Acumulado anual</span>
                      <strong className="summary-metric-value">
                        {formatValue(summary?.annualValue, summary?.annualUnit)}
                      </strong>
                    </div>
                  </div>
                  {summary?.seriesItems?.length ? (
                    <div className="chart-card chart-card-solar">
                      <div className="chart-legend">
                        <span className="legend-item demand">Potencia kW</span>
                        {summary?.irradianceItems?.length ? (
                          <span className="legend-item irradiance">Irradiancia W/m²</span>
                        ) : null}
                      </div>
                      <SolarDualAxisChart
                        powerSeries={summary.seriesItems}
                        irradianceSeries={summary.irradianceItems}
                        label={config.label}
                        intervalMinutes={ANALYTICS_SERIES_INTERVAL_MINUTES}
                        density="single"
                      />
                    </div>
                  ) : (
                    <div className="chart-empty">Sin curva de producción disponible.</div>
                  )}
                </article>
              );
            })}
          </div>
        </div>
      </section>
    </>
  );

  const renderValidationView = () => (
    <>
      <section className="section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Estado técnico por gateway</h2>
            <p className="section-subtitle">
              La validación se integra en el portal con filtros por campus y dominio, sin perder
              la profundidad técnica actual.
            </p>
          </div>
          <div className="insight-grid">
            <article className="insight-card">
              <span className="insight-label">Gateways visibles</span>
              <strong className="insight-value">{filteredValidationGateways.length}</strong>
              <span className="insight-note">Tras filtros activos</span>
            </article>
            <article className="insight-card">
              <span className="insight-label">Anomalías recientes</span>
              <strong className="insight-value">
                {anomalies.status === "ready" ? anomalies.data?.count || 0 : "--"}
              </strong>
              <span className="insight-note">
                {anomalies.status === "error"
                  ? "Error al consultar anomalías"
                  : `Últimas ${ANOMALIES_LOOKBACK_HOURS}h`}
              </span>
            </article>
            <article className="insight-card">
              <span className="insight-label">Incidencias</span>
              <strong className="insight-value">{validationSummary.errors}</strong>
              <span className="insight-note">Gateways con error</span>
            </article>
            <article className="insight-card">
              <span className="insight-label">Actualizando</span>
              <strong className="insight-value">{validationSummary.loading}</strong>
              <span className="insight-note">Carga en curso</span>
            </article>
            <article className="insight-card">
              <span className="insight-label">Última sincronización</span>
              <strong className="insight-value">{formatTs(validationSummary.lastSync)}</strong>
              <span className="insight-note">Referencia técnica</span>
            </article>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container">
          <article className="gateway-card anomaly-card">
            <div className="gateway-header">
              <div>
                <h3 className="gateway-title">Anomalías detectadas</h3>
                <div className="gateway-topic">
                  Registro técnico reciente de valores anómalos excluidos o ajustados en la analítica.
                </div>
              </div>
              <div className={`dashboard-status status-${getStatusKind(anomalies.status)}`}>
                {renderStatus({ status: anomalies.status, error: anomalies.error })}
              </div>
            </div>
            <div className="gateway-panel api-card gateway-panel-card">
              <div className="gateway-panel-header">
                <h4 className="api-card-title">Últimas anomalías</h4>
                <div className={`api-status status-${anomalies.status || "idle"}`}>
                  {renderStatus({ status: anomalies.status, error: anomalies.error })}
                </div>
              </div>
              {anomalies.status === "error" ? (
                <div className="api-empty">Error: {anomalies.error}</div>
              ) : (
                renderTable(
                  [
                    "Fecha/hora",
                    "Gateway",
                    "Punto",
                    "rt_id",
                    "Valor raw",
                    "Valor aplicado",
                    "Unidad",
                    "Tipo",
                    "Motivo",
                  ],
                  anomaliesRows
                )
              )}
            </div>
          </article>
          <div className="gateway-stack">
            {filteredValidationGateways.map((gateway) => buildGatewayTables(gateway))}
          </div>
        </div>
      </section>
    </>
  );

  const renderCurrentView = () => {
    if (routeId === "summary") return renderSummaryView();
    if (routeId === "energy") return renderEnergyView();
    if (routeId === "map") return renderMapView();
    if (routeId === "water") return renderWaterView();
    if (routeId === "solar") return renderSolarView();
    return renderValidationView();
  };

  return (
    <div className="app">
      <a className="skip-link" href="#main-content">
        Saltar al contenido principal
      </a>
      <header className="site-header">
        <div className="utility-bar">
          <div className="container utility-bar-inner">
            <p className="utility-bar-text">Universidad de Jaén</p>
            <p className="utility-bar-text">Portal de monitorización operativa</p>
          </div>
        </div>
        <div className="topbar">
          <div className="container topbar-inner">
            <div className="brand-lockup">
              <p className="brand-kicker">Universidad de Jaén</p>
              <p className="brand-title">Portal de monitorización de campus</p>
            </div>
            <nav className="topbar-nav portal-nav" aria-label="Navegación principal">
              {PORTAL_ROUTES.map((item) => (
                <a
                  key={item.id}
                  className={`topbar-link ${routeId === item.id ? "active" : ""}`}
                  href={item.hash}
                >
                  {item.label}
                </a>
              ))}
            </nav>
          </div>
        </div>
      </header>
      <main id="main-content">
        <section className="hero-section">
          <div className="container">
            <nav className="breadcrumb" aria-label="Ruta de navegación">
              <a className="breadcrumb-link" href="#/">
                Inicio
              </a>
              <span className="breadcrumb-separator" aria-hidden="true">
                /
              </span>
              <span className="breadcrumb-current">{pageMeta.title}</span>
            </nav>
            <div className="page-hero">
              <div className="page-intro">
                <p className="page-eyebrow">Supervisión institucional</p>
                <h1 className="page-title">{pageMeta.title}</h1>
                <p className="page-subtitle">{pageMeta.subtitle}</p>
              </div>
              <div className="page-actions">
                <button
                  className="action-button action-button-primary"
                  type="button"
                  onClick={pageMeta.primaryAction}
                >
                  {pageMeta.primaryLabel}
                </button>
              </div>
            </div>
          </div>
        </section>
        {renderToolbar()}
        {renderCurrentView()}
      </main>
      <footer className="site-footer">
        <div className="container site-footer-inner">
          <div>
            <p className="site-footer-title">Universidad de Jaén</p>
            <p className="site-footer-copy">
              Aplicación interna para seguimiento de consumos, producción fotovoltaica,
              cartografía operativa y validación de telemetría en los campus de Jaén y
              Linares.
            </p>
          </div>
          <div className="site-footer-links">
            {PORTAL_ROUTES.map((item) => (
              <a key={item.id} className="site-footer-link" href={item.hash}>
                {item.label}
              </a>
            ))}
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
