const RAW_MONITORING_SOURCE_KEYS = {
  "uja.jaen.agua.consumo.ae_magisterio.v_m3": "UJA-Agua-Opera--m3.Edif_Magisterio::m3",
  "uja.jaen.agua.consumo.c_futbol.v_m3": "UJA-Agua-Opera--m3.Edif_Campo_Futbol::m3",
  "uja.jaen.agua.consumo.d1_caf.v_m3": "UJA-Agua-Opera--m3.Edif_D1_Cafeteria::m3",
  "uja.jaen.agua.consumo.edificio_a0.v_m3": "UJA-Agua-Opera--m3.Edif_A0::m3",
  "uja.jaen.agua.consumo.edificio_a1.v_m3": "UJA-Agua-Opera--m3.Edif_A1::m3",
  "uja.jaen.agua.consumo.edificio_a2.v_m3": "UJA-Agua-Opera--m3.Edif_A2::m3",
  "uja.jaen.agua.consumo.edificio_a3.v_m3": "UJA-Agua-Opera--m3.Edif_A3::m3",
  "uja.jaen.agua.consumo.edificio_a4.v_m3": "UJA-Agua-Opera--m3.Edif_A4::m3",
  "uja.jaen.agua.consumo.edificio_b1.v_m3": "UJA-Agua-Opera--m3.Edif_B1::m3",
  "uja.jaen.agua.consumo.edificio_b2.v_m3": "UJA-Agua-Opera--m3.Edif_B2::m3",
  "uja.jaen.agua.consumo.edificio_b3.v_m3": "UJA-Agua-Opera--m3.Edif_B3::m3",
  "uja.jaen.agua.consumo.edificio_b4.v_m3": "UJA-Agua-Opera--m3.Edif_B4::m3",
  "uja.jaen.agua.consumo.edificio_b5.v_m3": "UJA-Agua-Opera--m3.Edif_B5::m3",
  "uja.jaen.agua.consumo.edificio_c1.v_m3": "UJA-Agua-Opera--m3.Edif_C1::m3",
  "uja.jaen.agua.consumo.edificio_c1_garaje.v_m3": "UJA-Agua-Opera--m3.Edif_C1_Garaje::m3",
  "uja.jaen.agua.consumo.edificio_c2.v_m3": "UJA-Agua-Opera--m3.Edif_C2::m3",
  "uja.jaen.agua.consumo.edificio_c3.v_m3": "UJA-Agua-Opera--m3.Edif_C3::m3",
  "uja.jaen.agua.consumo.edificio_c5.v_m3": "UJA-Agua-Opera--m3.Edif_C5::m3",
  "uja.jaen.agua.consumo.edificio_c6.v_m3": "UJA-Agua-Opera--m3.Edif_C6::m3",
  "uja.jaen.agua.consumo.edificio_d1.v_m3": "UJA-Agua-Opera--m3.Edif_D1::m3",
  "uja.jaen.agua.consumo.edificio_d2.v_m3": "UJA-Agua-Opera--m3.Edif_D2::m3",
  "uja.jaen.agua.consumo.edificio_d3.v_m3": "UJA-Agua-Opera--m3.Edif_D3::m3",
  "uja.jaen.agua.consumo.edificio_d4.v_m3": "UJA-Agua-Opera--m3.Edif_D4::m3",
  "uja.jaen.agua.consumo.plaz_pueblos.v_m3": "UJA-Agua-Opera--m3.Edif_Plaza_pueblos::m3",
  "uja.jaen.agua.consumo.polideportivo.v_m3": "UJA-Agua-Opera--m3.Edif_Polideportivo::m3",
  "uja.jaen.agua.consumo.um_c4.v_m3": "UJA-Agua-Opera--m3.Edif_C4::m3",
  "uja.jaen.energia.consumo.ae_magisterio.p_kw": "Consumo_Edif_Resto::Magisterio_KW sys",
  "uja.jaen.energia.consumo.apartamentos_universitarios.p_kw": "Consumo_Edif_Resto::Apartamentos_KW sys",
  "uja.jaen.energia.consumo.carga_vhe.p_kw": "Consumo_Edif_Lagunillas::Carga_VHE_KW sys",
  "uja.jaen.energia.consumo.edificio_a0.p_kw": "Consumo_Edif_Lagunillas::A0_KW sys",
  "uja.jaen.energia.consumo.edificio_a1.p_kw": "Consumo_Edif_Lagunillas::A1_KW sys",
  "uja.jaen.energia.consumo.edificio_a2.p_kw": "Consumo_Edif_Lagunillas::A2_KW sys",
  "uja.jaen.energia.consumo.edificio_a3.p_kw": "Consumo_Edif_Lagunillas::A3_KW sys",
  "uja.jaen.energia.consumo.edificio_a4.p_kw": "Consumo_Edif_Lagunillas::A4_KW sys",
  "uja.jaen.energia.consumo.edificio_b1.p_kw": "Consumo_Edif_Lagunillas::B1_KW sys",
  "uja.jaen.energia.consumo.edificio_b2.p_kw": "Consumo_Edif_Lagunillas::B2_KW sys",
  "uja.jaen.energia.consumo.edificio_b3.p_kw": "Consumo_Edif_Lagunillas::B3_KW sys",
  "uja.jaen.energia.consumo.edificio_b4.p_kw": "Consumo_Edif_Lagunillas::B4_KW sys",
  "uja.jaen.energia.consumo.edificio_b5.p_kw": "Consumo_Edif_Lagunillas::B5_KW sys",
  "uja.jaen.energia.consumo.edificio_c1.p_kw": "Consumo_Edif_Lagunillas::C1_KW sys",
  "uja.jaen.energia.consumo.edificio_c2.p_kw": "Consumo_Edif_Lagunillas::C2_KW sys",
  "uja.jaen.energia.consumo.edificio_c3.p_kw": "Consumo_Edif_Lagunillas::C3_KW sys",
  "uja.jaen.energia.consumo.edificio_c5.p_kw": "Consumo_Edif_Lagunillas::C5_KW sys",
  "uja.jaen.energia.consumo.edificio_c6.p_kw": "Consumo_Edif_Lagunillas::C6_KW sys",
  "uja.jaen.energia.consumo.edificio_d1.p_kw": "Consumo_Edif_Lagunillas::D1_KW sys",
  "uja.jaen.energia.consumo.edificio_d2.p_kw": "Consumo_Edif_Lagunillas::D2_KW sys",
  "uja.jaen.energia.consumo.edificio_d3.p_kw": "Consumo_Edif_Lagunillas::D3_KW sys",
  "uja.jaen.energia.consumo.edificio_d4.p_kw": "Consumo_Edif_Lagunillas::D4_KW sys",
  "uja.jaen.energia.consumo.polideportivo.p_kw": "Consumo_Edif_Resto::Polideportivo_KW sys",
  "uja.jaen.energia.consumo.residencia_domingo_savio.p_kw": "Consumo_Edif_Resto::Residencia_KW sys",
  "uja.jaen.energia.consumo.um_c4.p_kw": "Consumo_Edif_Resto::C4_KW sys",
  "uja.jaen.fv.auto.b5_inv1.p_ac_kw": "OPERA-UNIVER--Autocon--FV.UJA::B5_Inv1_KW sys",
  "uja.jaen.fv.auto.b5_inv2.p_ac_kw": "OPERA-UNIVER--Autocon--FV.UJA::B5_Inv2_KW sys",
  "uja.jaen.fv.auto.b5_rad.g_wm2": "OPERA-UNIVER--Autocon--FV.UJA::B5_Radiación",
  "uja.jaen.fv.auto.ct_total.e_kwh": "OPERA-UNIVER--Autocon--FV.UJA::Tot_FV_kWh",
  "uja.jaen.fv.auto.ct_total.p_kw": "OPERA-UNIVER--Autocon--FV.UJA::Tot_FV_KW sys",
  "uja.jaen.fv.auto.edificio_a0.p_kw": "Autoconsumo_FV_Edif::FV_A0_KW sys",
  "uja.jaen.fv.auto.edificio_c4.p_kw": "Autoconsumo_FV_Edif::FV_C4_KW sys",
  "uja.jaen.fv.auto.fachada.p_ac_kw": "OPERA-UNIVER--Autocon--FV.UJA::Fachada_KW sys",
  "uja.jaen.fv.auto.fachada_rad.g_wm2": "OPERA-UNIVER--Autocon--FV.UJA::Fachada_Radiación",
  "uja.jaen.fv.auto.magisterio.p_kw": "Autoconsumo_FV_Edif::FV_Magisterio_KW sys",
  "uja.jaen.fv.auto.parking_p4.p_ac_kw": "OPERA-UNIVER--Autocon--FV.UJA::Parking_KW sys",
  "uja.jaen.fv.auto.pergola.p_ac_kw": "OPERA-UNIVER--Autocon--FV.UJA::Pérgola_KW sys",
  "uja.jaen.fv.auto.pergola_rad.g_wm2": "OPERA-UNIVER--Autocon--FV.UJA::Perg_Radiación",
  "uja.jaen.fv.auto.temp01.t_c": "OPERA-UNIVER--Autocon--FV.UJA::Temperatura",
  "uja.jaen.fv.endesa.ct_total.e_kwh": "Jaén-OPERA-Endesa--FV.UJA::Tot_FV_kWh",
  "uja.jaen.fv.endesa.ct_total.p_kw": "Jaén-OPERA-Endesa--FV.UJA::Tot_FV_KW sys",
  "uja.jaen.fv.endesa.inv01.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P3_Inv1_KW sys",
  "uja.jaen.fv.endesa.inv02.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P3_Inv2_KW sys",
  "uja.jaen.fv.endesa.inv03.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P3_Inv3_KW sys",
  "uja.jaen.fv.endesa.inv04.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P3_Inv4_KW sys",
  "uja.jaen.fv.endesa.inv05.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P4_Inv5_KW sys",
  "uja.jaen.fv.endesa.inv06.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::P4_Inv6_KW sys",
  "uja.jaen.fv.endesa.inv07.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::B4_Inv7_KW sys",
  "uja.jaen.fv.endesa.inv08.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::B4_Inv8_KW sys",
  "uja.jaen.fv.endesa.inv09.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::C3_Inv9_KW sys",
  "uja.jaen.fv.endesa.inv10.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::D3_Inv10_KW sys",
  "uja.jaen.fv.endesa.inv11.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::D3_Inv11_KW sys",
  "uja.jaen.fv.endesa.inv12.p_ac_kw": "Jaén-OPERA-Endesa--FV.UJA::D3_Inv12_KW sys",
  "uja.jaen.fv.endesa.rad01.g_wm2": "Jaén-OPERA-Endesa--FV.UJA::P3_Radiación",
  "uja.jaen.fv.endesa.rad02.g_wm2": "Jaén-OPERA-Endesa--FV.UJA::P4_Radiación",
  "uja.jaen.fv.endesa.rad03.g_wm2": "Jaén-OPERA-Endesa--FV.UJA::B4_Radiación",
  "uja.jaen.fv.endesa.rad04.g_wm2": "Jaén-OPERA-Endesa--FV.UJA::C3_Radiación",
  "uja.jaen.fv.endesa.rad05.g_wm2": "Jaén-OPERA-Endesa--FV.UJA::D3_Radiación",
  "uja.jaen.fv.endesa.temp01.t_c": "Jaén-OPERA-Endesa--FV.UJA::Temperatura",
  "uja.linares.agua.consumo.cafeteria.v_m3": "CCTL-TOTAL.Cons_Agua_Cafeteria::m3",
  "uja.linares.agua.consumo.comedor.v_m3": "CCTL-TOTAL.Cons_Agua_Comedor::m3",
  "uja.linares.agua.consumo.departamental.v_m3": "CCTL-TOTAL.Cons_Agua_Departamental::m3",
  "uja.linares.agua.consumo.laboratorios.v_m3": "CCTL-TOTAL.Cons_Agua_Laboratorios::m3",
  "uja.linares.agua.consumo.pabellon_polideportivo.v_m3": "CCTL-TOTAL.Cons_Agua_Polideportivo::m3",
  "uja.linares.agua.consumo.reciclada_lluvia.v_m3": "CCTL-TOTAL.Cons_Agua_Reciclada::m3",
  "uja.linares.agua.consumo.riego_aulario.v_m3": "CCTL-TOTAL.Cons_Agua_Riego_Aulario::m3",
  "uja.linares.agua.consumo.servicios_generales.v_m3": "CCTL-TOTAL.Cons_Agua_S_Generales::m3",
  "uja.linares.energia.consumo.aulario_departamental.p_kw": "CCTL-TOTAL.Cons_Elec_Aulario::KW sys",
  "uja.linares.energia.consumo.lab_sg_t1.p_kw": "CCTL-TOTAL.Cons_Elec_Lab_SG_T1::KW sys",
  "uja.linares.energia.consumo.lab_sg_t2.p_kw": "CCTL-TOTAL.Cons_Elec_Lab_SG_T2::KW sys",
  "uja.linares.energia.consumo.polideportivo.p_kw": "CCTL-TOTAL.Cons_Elec_Polideportivo::KW sys",
  "uja.linares.energia.consumo.urbanizacion.p_kw": "CCTL-TOTAL.Cons_Elec_Urbanización::KW sys",
  "uja.linares.fv.endesa.ct_total.e_kwh": "LIN_OPERA_FV.Lin::FV_kWh",
  "uja.linares.fv.endesa.ct_total.p_kw": "LIN_OPERA_FV.Lin::FV_KW sys",
  "uja.linares.fv.endesa.rad01.g_wm2": "LIN_OPERA_FV.Lin::Radiación",
  "uja.linares.fv.endesa.temp01.t_c": "LIN_OPERA_FV.Lin::Temperatura",
};

const CURATED_POINT_META = {
  "uja.jaen.agua.consumo.c_futbol.v_m3": { label: "Campo de fútbol", shortLabel: "Campo fútbol" },
  "uja.jaen.agua.consumo.edificio_c1_garaje.v_m3": {
    label: "Edificio C1 garaje",
    shortLabel: "C1 garaje",
  },
  "uja.jaen.agua.consumo.d1_caf.v_m3": { label: "Edificio D1 cafetería", shortLabel: "D1 cafetería" },
  "uja.jaen.agua.consumo.plaz_pueblos.v_m3": {
    label: "Plaza de los Pueblos",
    shortLabel: "Plaza Pueblos",
  },
  "uja.jaen.agua.consumo.um_c4.v_m3": { label: "Edificio C4", shortLabel: "C4" },
  "uja.jaen.energia.consumo.ae_magisterio.p_kw": { label: "Magisterio", shortLabel: "Magisterio" },
  "uja.jaen.energia.consumo.apartamentos_universitarios.p_kw": {
    label: "Apartamentos universitarios",
    shortLabel: "Apartamentos",
  },
  "uja.jaen.energia.consumo.carga_vhe.p_kw": { label: "Carga VHE", shortLabel: "Carga VHE" },
  "uja.jaen.energia.consumo.residencia_domingo_savio.p_kw": {
    label: "Residencia Domingo Savio",
    shortLabel: "Residencia",
  },
  "uja.jaen.energia.consumo.um_c4.p_kw": { label: "Edificio C4", shortLabel: "C4" },
  "uja.jaen.fv.auto.parking_p4.p_ac_kw": { label: "Parking P4", shortLabel: "Parking P4" },
  "uja.jaen.fv.auto.pergola.p_ac_kw": { label: "Pérgola", shortLabel: "Pérgola" },
  "uja.jaen.fv.auto.pergola_rad.g_wm2": {
    label: "Radiación pérgola",
    shortLabel: "Rad. pérgola",
  },
};

const stripDiacritics = (value) =>
  value.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

const normalizeLookupKey = (value) =>
  stripDiacritics(value)
    .replace(/[^A-Za-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "")
    .toUpperCase();

const ASSET_LABEL_OVERRIDES = {
  A0: "Edificio A0",
  A1: "Edificio A1",
  A2: "Edificio A2",
  A3: "Edificio A3",
  A4: "Edificio A4",
  B1: "Edificio B1",
  B2: "Edificio B2",
  B3: "Edificio B3",
  B4: "Edificio B4",
  B5: "Edificio B5",
  C1: "Edificio C1",
  C1_GARAJE: "Edificio C1 garaje",
  C2: "Edificio C2",
  C3: "Edificio C3",
  C4: "Edificio C4",
  C5: "Edificio C5",
  C6: "Edificio C6",
  D1: "Edificio D1",
  D1_CAFETERIA: "Edificio D1 cafetería",
  D2: "Edificio D2",
  D3: "Edificio D3",
  D4: "Edificio D4",
  APARTAMENTOS: "Apartamentos universitarios",
  AULARIO: "Aulario departamental",
  CAFETERIA: "Cafetería",
  CAMPO_FUTBOL: "Campo de fútbol",
  COMEDOR: "Comedor",
  DEPARTAMENTAL: "Edificio departamental",
  FACHADA: "Fachada",
  LAB_SG_T1: "Laboratorios SG T1",
  LAB_SG_T2: "Laboratorios SG T2",
  LABORATORIOS: "Laboratorios",
  MAGISTERIO: "Magisterio",
  PARKING: "Parking P4",
  PABELLON_POLIDEPORTIVO: "Pabellón polideportivo",
  PLAZA_PUEBLOS: "Plaza de los Pueblos",
  POLIDEPORTIVO: "Polideportivo",
  RECICLADA: "Agua reciclada y lluvia",
  RESIDENCIA: "Residencia Domingo Savio",
  RIEGO_AULARIO: "Riego aulario",
  S_GENERALES: "Servicios generales",
  SERVICIOS_GENERALES: "Servicios generales",
  TEMPERATURA: "Temperatura",
  TOTAL_FV: "Total FV",
  URBANIZACION: "Urbanización",
};

const deriveCampus = (rtId) => {
  if (rtId.includes(".jaen.")) return "jaen";
  if (rtId.includes(".linares.")) return "linares";
  return null;
};

const deriveDomain = (rtId) => {
  if (rtId.includes(".agua.")) return "agua";
  if (rtId.includes(".fv.")) return "fv";
  if (rtId.includes(".energia.")) return "energy";
  return null;
};

const extractTailFromSourceKey = (sourceKey) => {
  if (!sourceKey) return "";
  const fragments = sourceKey.split("::");
  const tail = fragments[fragments.length - 1] || sourceKey;
  if (/^(?:KW sys|kWh|m3)$/i.test(tail) && fragments.length > 1) {
    const previousFragment = fragments[fragments.length - 2];
    const dottedSegments = previousFragment.split(".");
    return dottedSegments[dottedSegments.length - 1] || previousFragment;
  }
  return tail;
};

const titleCaseWords = (value) =>
  value
    .split(" ")
    .filter(Boolean)
    .map((word) => {
      if (/^[A-Z]\d$/i.test(word) || /^P\d$/i.test(word) || /^T\d$/i.test(word) || word === "SG") {
        return word.toUpperCase();
      }
      if (word === "FV" || word === "VHE") return word;
      if (/^\d+$/.test(word)) return word;
      return word.charAt(0).toUpperCase() + word.slice(1).toLowerCase();
    })
    .join(" ");

const humanizeGenericAsset = (asset) => {
  const normalizedKey = normalizeLookupKey(asset);
  if (ASSET_LABEL_OVERRIDES[normalizedKey]) {
    return ASSET_LABEL_OVERRIDES[normalizedKey];
  }

  const compact = normalizedKey.replace(/_/g, "");
  if (/^[A-D]\d$/.test(compact)) {
    return `Edificio ${compact}`;
  }

  return titleCaseWords(
    asset
      .replace(/_/g, " ")
      .replace(/\bsg\b/gi, "SG")
      .replace(/\bfv\b/gi, "FV")
      .replace(/\bvhe\b/gi, "VHE")
  );
};

const deriveLabelFromRtId = (rtId) => {
  const energyMatch = rtId.match(/\.energia\.consumo\.([a-z0-9_]+)\./i);
  if (energyMatch) {
    const asset = energyMatch[1];
    if (asset.startsWith("edificio_")) {
      return humanizeGenericAsset(asset.slice("edificio_".length));
    }
    return humanizeGenericAsset(asset);
  }

  const waterMatch = rtId.match(/\.agua\.consumo\.([a-z0-9_]+)\./i);
  if (waterMatch) {
    const asset = waterMatch[1];
    if (asset.startsWith("edificio_")) {
      return humanizeGenericAsset(asset.slice("edificio_".length));
    }
    return humanizeGenericAsset(asset);
  }

  const fvMatch = rtId.match(/\.fv\.(?:auto|endesa)\.([a-z0-9_]+)\./i);
  if (fvMatch) {
    return humanizeGenericAsset(fvMatch[1]);
  }

  return rtId;
};

const deriveLabelFromSourceKey = (sourceKey, rtId) => {
  const tail = extractTailFromSourceKey(sourceKey);
  if (!tail) return deriveLabelFromRtId(rtId);

  const cleanedTail = tail.replace(/_(?:KW sys|kWh|m3)$/i, "");

  if (/^Edif_/i.test(cleanedTail)) {
    return humanizeGenericAsset(cleanedTail.slice(5));
  }

  if (/^Tot_FV/i.test(cleanedTail) || /^FV$/i.test(cleanedTail)) {
    return "Total FV";
  }

  const inverterMatch = cleanedTail.match(/^([A-Za-z0-9]+)_Inv(\d+)$/i);
  if (inverterMatch) {
    return `${humanizeGenericAsset(inverterMatch[1])} inversor ${Number(inverterMatch[2])}`;
  }

  const radiationMatch = cleanedTail.match(/^([A-Za-z0-9]+)_Radiaci[oó]n$/i);
  if (radiationMatch) {
    return `Radiación ${humanizeGenericAsset(radiationMatch[1]).replace(/^Edificio /, "")}`;
  }

  if (/^Perg_Radiaci[oó]n$/i.test(cleanedTail)) {
    return "Radiación pérgola";
  }

  if (/^Fachada_Radiaci[oó]n$/i.test(cleanedTail)) {
    return "Radiación fachada";
  }

  if (/^FV_/i.test(cleanedTail)) {
    return humanizeGenericAsset(cleanedTail.slice(3));
  }

  const consumoMatch = cleanedTail.match(/^Cons_(?:Agua|Elec)_(.+)$/i);
  if (consumoMatch) {
    return humanizeGenericAsset(consumoMatch[1]);
  }

  if (/^[A-D]\d$/i.test(cleanedTail)) {
    return `Edificio ${cleanedTail.toUpperCase()}`;
  }

  return humanizeGenericAsset(cleanedTail);
};

const deriveShortLabel = (label, rtId) => {
  const buildingMatch = rtId.match(/(?:edificio_|um_)([a-z]\d)/i);
  if (buildingMatch) return buildingMatch[1].toUpperCase();

  if (label.startsWith("Edificio ")) {
    return label.replace("Edificio ", "");
  }

  if (label === "Apartamentos universitarios") return "Apartamentos";
  if (label === "Residencia Domingo Savio") return "Residencia";
  if (label === "Plaza de los Pueblos") return "Plaza Pueblos";
  if (label === "Agua reciclada y lluvia") return "Reciclada";

  return label;
};

export const MONITORING_POINTS = Object.entries(RAW_MONITORING_SOURCE_KEYS).reduce(
  (accumulator, [rtId, sourceKey]) => {
    const curatedMeta = CURATED_POINT_META[rtId] || {};
    const label = curatedMeta.label || deriveLabelFromSourceKey(sourceKey, rtId) || deriveLabelFromRtId(rtId);
    accumulator[rtId] = {
      rtId,
      sourceKey,
      campus: curatedMeta.campus || deriveCampus(rtId),
      domain: curatedMeta.domain || deriveDomain(rtId),
      label,
      shortLabel: curatedMeta.shortLabel || deriveShortLabel(label, rtId),
    };
    return accumulator;
  },
  {}
);

export const getMonitoringPointMeta = (rtId) => {
  if (MONITORING_POINTS[rtId]) {
    return MONITORING_POINTS[rtId];
  }

  const fallbackLabel = deriveLabelFromRtId(rtId);
  return {
    rtId,
    sourceKey: null,
    campus: deriveCampus(rtId),
    domain: deriveDomain(rtId),
    label: fallbackLabel,
    shortLabel: deriveShortLabel(fallbackLabel, rtId),
  };
};

export const getMonitoringPointLabel = (rtId) => getMonitoringPointMeta(rtId).label;
export const getMonitoringPointShortLabel = (rtId) => getMonitoringPointMeta(rtId).shortLabel;
