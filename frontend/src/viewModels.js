export const getAssetFromRtId = (rtId) => rtId?.split(".")[4] || null;

export const buildEnergyCampusCards = ({
  configs,
  dashboardOverview,
  currentAggregates,
  getEnvironmentalImpact,
}) =>
  configs.map((config) => {
    const scopeSummary = dashboardOverview[config.scopeId] || {};
    const aggregateSummary = currentAggregates[config.scopeId] || {};
    const environmentalImpact = getEnvironmentalImpact(aggregateSummary.yearlyValue ?? null);

    return {
      id: config.scopeId,
      campusLabel: scopeSummary.title || config.label,
      scopeId: config.scopeId,
      status: scopeSummary.status || { kind: "idle", label: "Sin datos" },
      chartSeries: scopeSummary.chartSeries || [],
      topMetrics: [
        {
          id: `${config.scopeId}:demand`,
          label: "Demanda actual",
          value: scopeSummary.demand ?? null,
          unit: "kW",
        },
        {
          id: `${config.scopeId}:autoconsumo`,
          label: "% autoconsumo",
          value: scopeSummary.autoconsumoPct ?? null,
          unit: "%",
        },
        {
          id: `${config.scopeId}:monthly`,
          label: "Energía mensual",
          value: aggregateSummary.monthlyValue ?? null,
          unit: aggregateSummary.monthlyUnit || "kWh",
        },
        {
          id: `${config.scopeId}:impact`,
          label: "Impacto medioambiental anual",
          value: environmentalImpact.avoidedCo2Ton,
          unit: "tn/CO2",
          secondaryValue: environmentalImpact.equivalentTrees,
          secondaryUnit: "árboles",
          inlineSecondary: true,
        },
      ],
      balanceMetrics: [
        {
          id: `${config.scopeId}:balance-demand`,
          label: "Demanda",
          value: scopeSummary.demand ?? null,
          unit: "kW",
        },
        {
          id: `${config.scopeId}:balance-pv`,
          label: "Generación FV",
          value: scopeSummary.pv ?? null,
          unit: "kW",
        },
        {
          id: `${config.scopeId}:balance-grid`,
          label: "Red",
          value: scopeSummary.grid ?? null,
          unit: "kW",
        },
        {
          id: `${config.scopeId}:balance-self`,
          label: "Autoconsumo",
          value: scopeSummary.autoconsumoPct ?? null,
          unit: "%",
        },
      ],
    };
  });

export const buildWaterCampusCards = ({ configs, waterOverview }) =>
  configs.map((config) => {
    const summary = waterOverview[config.id] || {};

    return {
      id: config.id,
      campusLabel: config.label,
      topMetrics: [
        {
          id: `${config.id}:points`,
          label: "Puntos de lectura",
          value: summary.readingPointsCount ?? 0,
          unit: null,
        },
        {
          id: `${config.id}:daily`,
          label: "Consumo diario",
          value: summary.dailyValue ?? null,
          unit: summary.dailyUnit || "m3",
        },
        {
          id: `${config.id}:monthly`,
          label: "Consumo mensual",
          value: summary.monthlyValue ?? null,
          unit: summary.monthlyUnit || "m3",
        },
      ],
    };
  });

export const buildWaterRows = ({
  latestItems,
  prefix,
  dailyAssetValues,
  getLabel,
  expectedRtIds = null,
}) => {
  const filteredLatestItems = (latestItems || []).filter((item) => item.rt_id?.startsWith(prefix));
  const latestByRtId = new Map(filteredLatestItems.map((item) => [item.rt_id, item]));
  const expectedIds = (expectedRtIds || []).filter((rtId) => rtId?.startsWith(prefix));
  const rtIds = expectedIds.length ? expectedIds : filteredLatestItems.map((item) => item.rt_id);

  return rtIds
    .map((rtId) => {
      const item = latestByRtId.get(rtId) || {};
      const asset = getAssetFromRtId(rtId);
      return {
        id: rtId,
        sortLabel: getLabel(rtId),
        pointLabel: getLabel(rtId),
        dailyValue:
          asset && Object.prototype.hasOwnProperty.call(dailyAssetValues || {}, asset)
            ? dailyAssetValues[asset]
            : null,
        unit: item.unit || "m3",
        tsEvent: item.ts_event || null,
      };
    })
    .sort((left, right) => left.sortLabel.localeCompare(right.sortLabel, "es"));
};
