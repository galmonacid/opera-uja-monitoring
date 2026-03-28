import { useId } from "react";

const number = new Intl.NumberFormat("es-ES", {
  maximumFractionDigits: 2,
});

const formatValue = (value, unit) => (value == null ? "--" : `${number.format(value)} ${unit}`);

const formatPercent = (value) => (value == null ? "--" : `${number.format(value)} %`);

const ValuePill = ({ x, y, width, heading, value, className = "" }) => (
  <g className={`energy-flow-pill ${className}`.trim()} transform={`translate(${x} ${y})`}>
    <rect width={width} height="64" rx="18" />
    <text className="energy-flow-pill-heading" x={width / 2} y="23" textAnchor="middle">
      {heading}
    </text>
    <text className="energy-flow-pill-value" x={width / 2} y="48" textAnchor="middle">
      {value}
    </text>
  </g>
);

const GridPowerIcon = () => (
  <g
    className="energy-flow-icon energy-flow-grid-icon"
    fill="none"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M36 10v92" strokeWidth="4" />
    <path d="M18 10h36L72 30H0L18 10Z" strokeWidth="4" />
    <path d="M12 30v14M60 30v14" strokeWidth="4" />
    <path d="M16 30h40" strokeWidth="4" />
    <path d="M28 10l16 20M44 10 28 30" strokeWidth="4" />
    <path d="M10 52h52L76 72H-4L10 52Z" strokeWidth="4" />
    <path d="M8 52v16M64 52v16" strokeWidth="4" />
    <path d="M18 52h36" strokeWidth="4" />
    <path d="M22 52l14 20M50 52 36 72" strokeWidth="4" />
    <path d="M18 72 8 118h56L54 72" strokeWidth="4" />
    <path d="M20 88 52 110M52 88 20 110" strokeWidth="4" />
    <path d="M8 118h56" strokeWidth="4" />
  </g>
);

const SolarPanelIcon = () => (
  <g
    className="energy-flow-icon energy-flow-solar-icon"
    fill="none"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <g stroke="currentColor" strokeWidth="4">
      <path d="M18 42h82l-10 42H8l10-42Z" />
      <path d="M34 42 24 84M56 42 46 84M78 42 68 84" />
      <path d="M14 56h82M10 70h82" />
      <path d="M48 84v18M34 102h28" />
    </g>
    <g className="energy-flow-solar-sun" strokeWidth="3">
      <circle cx="104" cy="26" r="10" />
      <path d="M104 8v-8M104 52v-8M86 26h-8M130 26h-8M91 13l-6-6M117 39l6 6M117 13l6-6M91 39l-6 6" />
    </g>
  </g>
);

const BuildingIcon = () => (
  <g
    className="energy-flow-icon energy-flow-building-icon"
    fill="none"
    stroke="currentColor"
    strokeLinecap="round"
    strokeLinejoin="round"
  >
    <path d="M18 18h62v102H18z" strokeWidth="4" />
    <path d="M38 92h22v28H38z" strokeWidth="4" />
    <path
      d="M32 34h8v10h-8zM58 34h8v10h-8zM32 54h8v10h-8zM58 54h8v10h-8zM32 74h8v10h-8zM58 74h8v10h-8z"
      strokeWidth="4"
    />
    <path d="M8 120h82" strokeWidth="4" />
  </g>
);

function EnergyFlowDiagram({
  campusLabel,
  gridPower,
  consumption,
  generation,
  autoconsumption,
}) {
  const markerId = useId().replace(/:/g, "");
  const gridValue = formatValue(gridPower, "kW");
  const demandValue = formatValue(consumption, "kW");
  const generationValue = formatValue(generation, "kW");
  const autoconsumptionValue = formatPercent(autoconsumption);

  return (
    <div className="energy-flow-diagram">
      <svg
        className="energy-flow-diagram-svg"
        viewBox="0 0 960 430"
        role="img"
        aria-label={`Diagrama de flujo energético de ${campusLabel}`}
      >
        <defs>
          <marker
            id={markerId}
            markerWidth="10"
            markerHeight="10"
            refX="8"
            refY="5"
            orient="auto"
            markerUnits="userSpaceOnUse"
          >
            <path d="M0 0 10 5 0 10Z" className="energy-flow-arrow-head" />
          </marker>
        </defs>

        <rect className="energy-flow-surface" x="4" y="4" width="952" height="422" rx="30" />

        <path
          className="energy-flow-arrow energy-flow-arrow-grid"
          d="M226 100 L 390 198"
          markerEnd={`url(#${markerId})`}
        />
        <path
          className="energy-flow-arrow energy-flow-arrow-demand"
          d="M610 200 H 780"
          markerEnd={`url(#${markerId})`}
        />
        <path
          className="energy-flow-arrow energy-flow-arrow-solar"
          d="M226 308 L 390 202"
          markerEnd={`url(#${markerId})`}
        />

        <g transform="translate(34 26)">
          <ValuePill x="150" y="0" width="188"
          heading="Potencia"
          value={gridValue} />
          <g transform="translate(40 0)">
            <GridPowerIcon />
          </g>
          <text className="energy-flow-group-label" x="80" y="150" textAnchor="middle">
            Energía de red
          </text>
        </g>


        <g transform="translate(34 230)">
            <g transform="translate(20 0 )">
            <SolarPanelIcon />
          </g>
          <text className="energy-flow-group-label" x="74" y="140" textAnchor="middle">
            Energía FV
          </text>
          <ValuePill
            x="150"
            y="100"
            width="194"
            heading="Generación"
            value={generationValue}
          />
        </g>

        <g className="energy-flow-node" transform="translate(392 150)">
          <rect width="216" height="90" rx="20" />
          {/* <text className="energy-flow-node-title" x="108" y="50" textAnchor="middle">
            Balance energético
          </text> */}
          <text className="energy-flow-node-label" x="108" y="30" textAnchor="middle">
            Autoconsumo
          </text>
          <text className="energy-flow-node-value" x="108" y="80" textAnchor="middle">
            {autoconsumptionValue}
          </text>
        </g>

        <g transform="translate(650 100)">
          <ValuePill x="0" y="0" width="170" heading="Consumo" value={demandValue} />
        </g>

        <g transform="translate(832 108)">
          <BuildingIcon />
          <text className="energy-flow-group-label" x="49" y="176" textAnchor="middle">
            Demanda
          </text>
        </g>
      </svg>
    </div>
  );
}

export default EnergyFlowDiagram;
