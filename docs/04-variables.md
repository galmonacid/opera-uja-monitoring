# 04 — Inventario de variables (96 mapeadas) + variables calculadas y fórmulas

## 0) Convenciones

### 0.1 Identificadores de edificios (sin ceros a la izquierda)
Se usan tal cual en PowerPoint:
- A0, A1, A2, A3, A4
- B1, B2, B3, B4, B5
- C1, C2, C3, C5, C6
- D1, D2, D3, D4
y activos especiales:
- D1 Cafetería → d1_caf
- Plaz. Pueblos → plaz_pueblos
- Edificio U.M. C4 → um_c4
- P. Polideportivo → polideportivo
- C. futbol → c_futbol
- A.E. Magisterio → ae_magisterio
- Carga VHE → carga_vhe
- Residencia Domingo Savio → residencia_domingo_savio
- Apartamentos Universitarios → apartamentos_universitarios

### 0.2 Convención RT_ID
`uja.<campus>.<dominio>.<subdominio>.<asset>.<magnitud>_<unidad>`

Ejemplos:
- `uja.jaen.energia.consumo.edificio_a1.p_kw`
- `uja.jaen.agua.consumo.edificio_b3.v_m3`
- `uja.jaen.fv.endesa.inv01.p_ac_kw`
- `uja.jaen.fv.endesa.rad01.g_wm2`

### 0.3 Convención de mapeo desde gateway
`gateway_id | source_key = "<meter.name>::<data.var>"`

> Nota: en FV y radiación, el `meter.name` exacto se completa con el operador.  
> Aquí usamos placeholders `<...>` sin romper el modelo.
> Normalización en ingestión: si el gateway envía `meter.name` con prefijo `UJA-OPERA--Edif-.`, se elimina el prefijo.  
> También se normaliza `data.var` para aceptar `kW sys` y convertirlo a `KW sys`.

---

## 1) VARIABLES MAPEADAS (directas desde gateways) — TOTAL: 100

### 1.1 Jaén — Consumo energía (25)
Gateway: `gw_jaen_energia`
`data.var` esperado: `<asset>_KW sys`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 1 | uja.jaen.energia.consumo.edificio_a0.p_kw | kW | `Consumo_Edif_Lagunillas::A0_KW sys` |
| 2 | uja.jaen.energia.consumo.edificio_a1.p_kw | kW | `Consumo_Edif_Lagunillas::A1_KW sys` |
| 3 | uja.jaen.energia.consumo.edificio_a2.p_kw | kW | `Consumo_Edif_Lagunillas::A2_KW sys` |
| 4 | uja.jaen.energia.consumo.edificio_a3.p_kw | kW | `Consumo_Edif_Lagunillas::A3_KW sys` |
| 5 | uja.jaen.energia.consumo.edificio_a4.p_kw | kW | `Consumo_Edif_Lagunillas::A4_KW sys` |
| 6 | uja.jaen.energia.consumo.edificio_b1.p_kw | kW | `Consumo_Edif_Lagunillas::B1_KW sys` |
| 7 | uja.jaen.energia.consumo.edificio_b2.p_kw | kW | `Consumo_Edif_Lagunillas::B2_KW sys` |
| 8 | uja.jaen.energia.consumo.edificio_b3.p_kw | kW | `Consumo_Edif_Lagunillas::B3_KW sys` |
| 9 | uja.jaen.energia.consumo.edificio_b4.p_kw | kW | `Consumo_Edif_Lagunillas::B4_KW sys` |
| 10 | uja.jaen.energia.consumo.edificio_b5.p_kw | kW | `Consumo_Edif_Lagunillas::B5_KW sys` |
| 11 | uja.jaen.energia.consumo.edificio_c1.p_kw | kW | `Consumo_Edif_Lagunillas::C1_KW sys` |
| 12 | uja.jaen.energia.consumo.edificio_c2.p_kw | kW | `Consumo_Edif_Lagunillas::C2_KW sys` |
| 13 | uja.jaen.energia.consumo.edificio_c3.p_kw | kW | `Consumo_Edif_Lagunillas::C3_KW sys` |
| 14 | uja.jaen.energia.consumo.edificio_c5.p_kw | kW | `Consumo_Edif_Lagunillas::C5_KW sys` |
| 15 | uja.jaen.energia.consumo.edificio_c6.p_kw | kW | `Consumo_Edif_Lagunillas::C6_KW sys` |
| 16 | uja.jaen.energia.consumo.edificio_d1.p_kw | kW | `Consumo_Edif_Lagunillas::D1_KW sys` |
| 17 | uja.jaen.energia.consumo.edificio_d2.p_kw | kW | `Consumo_Edif_Lagunillas::D2_KW sys` |
| 18 | uja.jaen.energia.consumo.edificio_d3.p_kw | kW | `Consumo_Edif_Lagunillas::D3_KW sys` |
| 19 | uja.jaen.energia.consumo.edificio_d4.p_kw | kW | `Consumo_Edif_Lagunillas::D4_KW sys` |
| 20 | uja.jaen.energia.consumo.carga_vhe.p_kw | kW | `Consumo_Edif_Lagunillas::Carga_VHE_KW sys` |
| 21 | uja.jaen.energia.consumo.um_c4.p_kw | kW | `Consumo_Edif_Resto::C4_KW sys` |
| 22 | uja.jaen.energia.consumo.polideportivo.p_kw | kW | `Consumo_Edif_Resto::Polideportivo_KW sys` |
| 23 | uja.jaen.energia.consumo.ae_magisterio.p_kw | kW | `Consumo_Edif_Resto::Magisterio_KW sys` |
| 24 | uja.jaen.energia.consumo.residencia_domingo_savio.p_kw | kW | `Consumo_Edif_Resto::Residencia_KW sys` |
| 25 | uja.jaen.energia.consumo.apartamentos_universitarios.p_kw | kW | `Consumo_Edif_Resto::Apartamentos_KW sys` |

### 1.1.b Jaén — Autoconsumo FV en edificios (3)
Gateway: `gw_jaen_energia`
`data.var` esperado: `FV_<asset>_KW sys`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 26 | uja.jaen.fv.auto.edificio_a0.p_kw | kW | `Autoconsumo_FV_Edif::FV_A0_KW sys` |
| 27 | uja.jaen.fv.auto.edificio_c4.p_kw | kW | `Autoconsumo_FV_Edif::FV_C4_KW sys` |
| 28 | uja.jaen.fv.auto.magisterio.p_kw | kW | `Autoconsumo_FV_Edif::FV_Magisterio_KW sys` |

Notas (operador):
- Split confirmado:
  - `meter.name`: `Consumo_Edif_Lagunillas`, `Consumo_Edif_Resto`, `Autoconsumo_FV_Edif`
  - `data.var`: `<asset>_KW sys` o `FV_<asset>_KW sys`
- Demanda edificio (aplicar en backend antes de guardar RT_ID):
  - A0 = `Consumo_Edif_Lagunillas::A0_KW sys + Autoconsumo_FV_Edif::FV_A0_KW sys`
  - C4 = `Consumo_Edif_Resto::C4_KW sys + Autoconsumo_FV_Edif::FV_C4_KW sys`
  - Magisterio = `Consumo_Edif_Resto::Magisterio_KW sys + Autoconsumo_FV_Edif::FV_Magisterio_KW sys`
  - A3 = `Consumo_Edif_Lagunillas::A3_KW sys - Consumo_Edif_Lagunillas::A4_KW sys` (A4 aguas abajo)
  - B4 = `Consumo_Edif_Lagunillas::B4_KW sys - (Consumo_Edif_Lagunillas::B5_KW sys + Consumo_Edif_Lagunillas::D3_KW sys)` (B5 y D3 aguas abajo)
  - Si el resultado A0 es negativo, indica exportación a red.
- B3 sin datos hasta sustitución del medidor.

### 1.2 Jaén — Consumo agua (25)
Gateway: `gw_jaen_agua`
`data.var` esperado: `m3` (confirmar)

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 29 | uja.jaen.agua.consumo.edificio_a0.v_m3 | m³ | `Edificio A0::m3` |
| 30 | uja.jaen.agua.consumo.edificio_a1.v_m3 | m³ | `Edificio A1::m3` |
| 31 | uja.jaen.agua.consumo.edificio_a2.v_m3 | m³ | `Edificio A2::m3` |
| 32 | uja.jaen.agua.consumo.edificio_a3.v_m3 | m³ | `Edificio A3::m3` |
| 33 | uja.jaen.agua.consumo.edificio_a4.v_m3 | m³ | `Edificio A4::m3` |
| 34 | uja.jaen.agua.consumo.edificio_b1.v_m3 | m³ | `Edificio B1::m3` |
| 35 | uja.jaen.agua.consumo.edificio_b2.v_m3 | m³ | `Edificio B2::m3` |
| 36 | uja.jaen.agua.consumo.edificio_b3.v_m3 | m³ | `Edificio B3::m3` |
| 37 | uja.jaen.agua.consumo.edificio_b4.v_m3 | m³ | `Edificio B4::m3` |
| 38 | uja.jaen.agua.consumo.edificio_b5.v_m3 | m³ | `Edificio B5::m3` |
| 39 | uja.jaen.agua.consumo.edificio_c1.v_m3 | m³ | `Edificio C1::m3` |
| 40 | uja.jaen.agua.consumo.edificio_c2.v_m3 | m³ | `Edificio C2::m3` |
| 41 | uja.jaen.agua.consumo.edificio_c3.v_m3 | m³ | `Edificio C3::m3` |
| 42 | uja.jaen.agua.consumo.edificio_c5.v_m3 | m³ | `Edificio C5::m3` |
| 43 | uja.jaen.agua.consumo.edificio_c6.v_m3 | m³ | `Edificio C6::m3` |
| 44 | uja.jaen.agua.consumo.edificio_d1.v_m3 | m³ | `Edificio D1::m3` |
| 45 | uja.jaen.agua.consumo.d1_caf.v_m3 | m³ | `D1 Cafeteria::m3` |
| 46 | uja.jaen.agua.consumo.edificio_d2.v_m3 | m³ | `Edificio D2::m3` |
| 47 | uja.jaen.agua.consumo.edificio_d3.v_m3 | m³ | `Edificio D3::m3` |
| 48 | uja.jaen.agua.consumo.edificio_d4.v_m3 | m³ | `Edificio D4::m3` |
| 49 | uja.jaen.agua.consumo.plaz_pueblos.v_m3 | m³ | `Plaz. Pueblos::m3` |
| 50 | uja.jaen.agua.consumo.um_c4.v_m3 | m³ | `Edificio U.M. C4::m3` |
| 51 | uja.jaen.agua.consumo.polideportivo.v_m3 | m³ | `P. Polideportivo::m3` |
| 52 | uja.jaen.agua.consumo.c_futbol.v_m3 | m³ | `C.futbol::m3` |
| 53 | uja.jaen.agua.consumo.ae_magisterio.v_m3 | m³ | `A.E. Magisterio::m3` |

### 1.3 Linares — Agua (9) + Energía (4) = 13
Gateway: `gw_linares_mix`

Agua (9):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 54 | uja.linares.agua.consumo.pabellon_polideportivo.v_m3 | m³ | `Pabellon polideportivo::m3` |
| 55 | uja.linares.agua.consumo.servicios_generales.v_m3 | m³ | `Servicios Generales::m3` |
| 56 | uja.linares.agua.consumo.cafeteria.v_m3 | m³ | `Cafeteria::m3` |
| 57 | uja.linares.agua.consumo.cocina_comedor.v_m3 | m³ | `Cocina-Comedor::m3` |
| 58 | uja.linares.agua.consumo.laboratorios.v_m3 | m³ | `Laboratorios::m3` |
| 59 | uja.linares.agua.consumo.aularios.v_m3 | m³ | `Aularios::m3` |
| 60 | uja.linares.agua.consumo.departamental.v_m3 | m³ | `Departamental::m3` |
| 61 | uja.linares.agua.consumo.riego_aularios.v_m3 | m³ | `Riego Aularios::m3` |
| 62 | uja.linares.agua.consumo.reciclada_general.v_m3 | m³ | `Reciclada general::m3` |

Energía (4) — placeholders hasta confirmar meter.name:
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 63 | uja.linares.energia.consumo.linea_01.p_kw | kW | `<LINEA_01>::kW sys` |
| 64 | uja.linares.energia.consumo.linea_02.p_kw | kW | `<LINEA_02>::kW sys` |
| 65 | uja.linares.energia.consumo.linea_03.p_kw | kW | `<LINEA_03>::kW sys` |
| 66 | uja.linares.energia.consumo.linea_04.p_kw | kW | `<LINEA_04>::kW sys` |

### 1.4 FV Endesa Jaén (20)
Gateway: `gw_endesa_jaen`
- 12 inversores (kW AC)
- CT total (kW)
- Radiación en 5 ubicaciones (W/m²) — MAPEADA desde gateway

Inversores (12):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 67 | uja.jaen.fv.endesa.inv01.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P3_Inv1_KW sys` |
| 68 | uja.jaen.fv.endesa.inv02.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P3_Inv2_KW sys` |
| 69 | uja.jaen.fv.endesa.inv03.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P3_Inv3_KW sys` |
| 70 | uja.jaen.fv.endesa.inv04.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P3_Inv4_KW sys` |
| 71 | uja.jaen.fv.endesa.inv05.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P4_Inv5_KW sys` |
| 72 | uja.jaen.fv.endesa.inv06.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::P4_Inv6_KW sys` |
| 73 | uja.jaen.fv.endesa.inv07.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::B4_Inv7_KW sys` |
| 74 | uja.jaen.fv.endesa.inv08.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::B4_Inv8_KW sys` |
| 75 | uja.jaen.fv.endesa.inv09.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::C3_Inv9_KW sys` |
| 76 | uja.jaen.fv.endesa.inv10.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::D3_Inv10_KW sys` |
| 77 | uja.jaen.fv.endesa.inv11.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::D3_Inv11_KW sys` |
| 78 | uja.jaen.fv.endesa.inv12.p_ac_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::D3_Inv12_KW sys` |

CT total (1) + Energía (1) + Radiación (5) + Temperatura (1):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 79 | uja.jaen.fv.endesa.ct_total.p_kw | kW | `Jaén-OPERA-Endesa--FV.UJA::Tot_FV_KW sys` |
| 80 | uja.jaen.fv.endesa.ct_total.e_kwh | kWh | `Jaén-OPERA-Endesa--FV.UJA::Tot_FV_kWh` |
| 81 | uja.jaen.fv.endesa.rad01.g_wm2 | W/m² | `Jaén-OPERA-Endesa--FV.UJA::P3_Radiación` |
| 82 | uja.jaen.fv.endesa.rad02.g_wm2 | W/m² | `Jaén-OPERA-Endesa--FV.UJA::P4_Radiación` |
| 83 | uja.jaen.fv.endesa.rad03.g_wm2 | W/m² | `Jaén-OPERA-Endesa--FV.UJA::B4_Radiación` |
| 84 | uja.jaen.fv.endesa.rad04.g_wm2 | W/m² | `Jaén-OPERA-Endesa--FV.UJA::C3_Radiación` |
| 85 | uja.jaen.fv.endesa.rad05.g_wm2 | W/m² | `Jaén-OPERA-Endesa--FV.UJA::D3_Radiación` |
| 86 | uja.jaen.fv.endesa.temp01.t_c | °C | `Jaén-OPERA-Endesa--FV.UJA::Temperatura` |

### 1.5 FV Endesa Linares (4)
Gateway: `gw_endesa_linares`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 87 | uja.linares.fv.endesa.ct_total.p_kw | kW | `LIN_OPERA_FV.Lin::FV_KW sys` |
| 88 | uja.linares.fv.endesa.ct_total.e_kwh | kWh | `LIN_OPERA_FV.Lin::FV_kWh` |
| 89 | uja.linares.fv.endesa.rad01.g_wm2 | W/m² | `LIN_OPERA_FV.Lin::Radiación` |
| 90 | uja.linares.fv.endesa.temp01.t_c | °C | `LIN_OPERA_FV.Lin::Temperatura` |

### 1.6 FV Autoconsumo Jaén (10)
Gateway: `gw_autoconsumo_jaen`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 91 | uja.jaen.fv.auto.inv01.p_ac_kw | kW | `<INV01_METER>::kW sys` |
| 92 | uja.jaen.fv.auto.inv02.p_ac_kw | kW | `<INV02_METER>::kW sys` |
| 93 | uja.jaen.fv.auto.inv03.p_ac_kw | kW | `<INV03_METER>::kW sys` |
| 94 | uja.jaen.fv.auto.inv04.p_ac_kw | kW | `<INV04_METER>::kW sys` |
| 95 | uja.jaen.fv.auto.inv05.p_ac_kw | kW | `<INV05_METER>::kW sys` |
| 96 | uja.jaen.fv.auto.ct_total.p_kw | kW | `<CT_METER>::kW sys` |
| 97 | uja.jaen.fv.auto.rad01.g_wm2 | W/m² | `<RAD01_METER>::Irradiación transitoria` |
| 98 | uja.jaen.fv.auto.rad02.g_wm2 | W/m² | `<RAD02_METER>::Irradiación transitoria` |
| 99 | uja.jaen.fv.auto.rad03.g_wm2 | W/m² | `<RAD03_METER>::Irradiación transitoria` |
| 100 | uja.jaen.fv.auto.rad04.g_wm2 | W/m² | `<RAD04_METER>::Irradiación transitoria` |

---
## 2) VARIABLES CALCULADAS — definiciones y fórmulas exactas

### 2.1 Agregación de potencia (tiempo real)
| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.energia.consumo.total.p_kw | kW | Σ de las 25 potencias `uja.jaen.energia.consumo.*.p_kw` |
| uja.linares.energia.consumo.total.p_kw | kW | `linea_01 + linea_02 + linea_03 + linea_04` |
| uja.jaen.fv.endesa.total.p_kw | kW | Σ `uja.jaen.fv.endesa.inv01..inv12.p_ac_kw` |
| uja.linares.fv.endesa.total.p_kw | kW | Σ `uja.linares.fv.endesa.inv01..inv03.p_ac_kw` |
| uja.jaen.fv.auto.total.p_kw | kW | Σ `uja.jaen.fv.auto.inv01..inv05.p_ac_kw` + `uja.jaen.fv.auto.edificio_a0.p_kw` + `uja.jaen.fv.auto.edificio_c4.p_kw` + `uja.jaen.fv.auto.magisterio.p_kw` |
| uja.jaen.fv.total.p_kw | kW | `uja.jaen.fv.endesa.total.p_kw + uja.jaen.fv.auto.total.p_kw` |

### 2.2 Energía (kWh) por integración
Definición por intervalo i:
- `E_i(kWh) = P_i(kW) * Δt(s) / 3600`
- `E_dia = Σ_i E_i`
- `E_mes = Σ E_dia`
- `E_anio = Σ E_mes`

| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.energia.consumo.daily.e_kwh | kWh | `Σ (uja.jaen.energia.consumo.total.p_kw * Δt/3600)` |
| uja.jaen.energia.consumo.monthly.e_kwh | kWh | `Σ daily` |
| uja.jaen.energia.consumo.yearly.e_kwh | kWh | `Σ monthly` |
| uja.linares.energia.consumo.daily.e_kwh | kWh | `Σ (uja.linares.energia.consumo.total.p_kw * Δt/3600)` |
| uja.linares.energia.consumo.monthly.e_kwh | kWh | `Σ daily` |
| uja.linares.energia.consumo.yearly.e_kwh | kWh | `Σ monthly` |
| uja.jaen.fv.total.daily.e_kwh | kWh | `Σ (uja.jaen.fv.total.p_kw * Δt/3600)` |
| uja.jaen.fv.endesa.daily.e_kwh | kWh | `Σ (uja.jaen.fv.endesa.total.p_kw * Δt/3600)` |
| uja.jaen.fv.auto.daily.e_kwh | kWh | `Σ (uja.jaen.fv.auto.total.p_kw * Δt/3600)` |
| uja.linares.fv.endesa.daily.e_kwh | kWh | `Σ (uja.linares.fv.endesa.total.p_kw * Δt/3600)` |

### 2.3 Agua (m³): contador acumulado vs incremental
Caso esperado (contador):
- `Consumo_dia = V_fin_dia - V_ini_dia`
- `Consumo_mes = Σ Consumo_dia`
- `Consumo_anio = Σ Consumo_mes`

| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.agua.consumo.total.daily.v_m3 | m³ | Σ assets `(V_fin_dia - V_ini_dia)` |
| uja.jaen.agua.consumo.total.monthly.v_m3 | m³ | `Σ daily` |
| uja.jaen.agua.consumo.total.yearly.v_m3 | m³ | `Σ monthly` |
| uja.linares.agua.consumo.total.daily.v_m3 | m³ | Σ assets `(V_fin_dia - V_ini_dia)` |
| uja.linares.agua.consumo.total.monthly.v_m3 | m³ | `Σ daily` |
| uja.linares.agua.consumo.total.yearly.v_m3 | m³ | `Σ monthly` |

### 2.4 Balance energético (tiempo real)
Definiciones:
- `Autoconsumo_kw = min(Consumo_kw, Generacion_kw)`
- `Red_kw = max(Consumo_kw - Generacion_kw, 0)`
- `%Autoconsumo = Autoconsumo_kw / Consumo_kw * 100` (si Consumo_kw > 0)

| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.balance.autoconsumo.p_kw | kW | `min(uja.jaen.energia.consumo.total.p_kw, uja.jaen.fv.total.p_kw)` |
| uja.jaen.balance.red.p_kw | kW | `max(uja.jaen.energia.consumo.total.p_kw - uja.jaen.fv.total.p_kw, 0)` |
| uja.jaen.balance.autoconsumo.p_pct | % | `autoconsumo/consumo*100` (si consumo>0) |
| uja.linares.balance.autoconsumo.p_kw | kW | `min(uja.linares.energia.consumo.total.p_kw, uja.linares.fv.endesa.total.p_kw)` |
| uja.linares.balance.red.p_kw | kW | `max(uja.linares.energia.consumo.total.p_kw - uja.linares.fv.endesa.total.p_kw, 0)` |
| uja.linares.balance.autoconsumo.p_pct | % | `autoconsumo/consumo*100` (si consumo>0) |

### 2.5 CO₂ evitado
Factor de emisión configurable:
- `EF = 0.23 kgCO2/kWh` (valor ejemplo; fijar con UJA)

| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.co2.evitar.daily.kg | kg | `uja.jaen.fv.total.daily.e_kwh * EF` |
| uja.jaen.co2.evitar.monthly.kg | kg | `Σ daily` |
| uja.jaen.co2.evitar.yearly.kg | kg | `Σ monthly` |
| uja.linares.co2.evitar.daily.kg | kg | `uja.linares.fv.endesa.daily.e_kwh * EF` |
| uja.linares.co2.evitar.monthly.kg | kg | `Σ daily` |
| uja.linares.co2.evitar.yearly.kg | kg | `Σ monthly` |
