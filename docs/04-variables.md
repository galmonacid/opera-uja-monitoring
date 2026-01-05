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

---

## 1) VARIABLES MAPEADAS (directas desde gateways) — TOTAL: 96

### 1.1 Jaén — Consumo energía (25)
Gateway: `gw_jaen_energia`
`data.var` esperado: `kW sys` (confirmar)

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 1 | uja.jaen.energia.consumo.edificio_a0.p_kw | kW | `Edificio A0::kW sys` |
| 2 | uja.jaen.energia.consumo.edificio_a1.p_kw | kW | `Edificio A1::kW sys` |
| 3 | uja.jaen.energia.consumo.edificio_a2.p_kw | kW | `Edificio A2::kW sys` |
| 4 | uja.jaen.energia.consumo.edificio_a3.p_kw | kW | `Edificio A3::kW sys` |
| 5 | uja.jaen.energia.consumo.edificio_a4.p_kw | kW | `Edificio A4::kW sys` |
| 6 | uja.jaen.energia.consumo.edificio_b1.p_kw | kW | `Edificio B1::kW sys` |
| 7 | uja.jaen.energia.consumo.edificio_b2.p_kw | kW | `Edificio B2::kW sys` |
| 8 | uja.jaen.energia.consumo.edificio_b3.p_kw | kW | `Edificio B3::kW sys` |
| 9 | uja.jaen.energia.consumo.edificio_b4.p_kw | kW | `Edificio B4::kW sys` |
| 10 | uja.jaen.energia.consumo.edificio_b5.p_kw | kW | `Edificio B5::kW sys` |
| 11 | uja.jaen.energia.consumo.edificio_c1.p_kw | kW | `Edificio C1::kW sys` |
| 12 | uja.jaen.energia.consumo.edificio_c2.p_kw | kW | `Edificio C2::kW sys` |
| 13 | uja.jaen.energia.consumo.edificio_c3.p_kw | kW | `Edificio C3::kW sys` |
| 14 | uja.jaen.energia.consumo.edificio_c5.p_kw | kW | `Edificio C5::kW sys` |
| 15 | uja.jaen.energia.consumo.edificio_c6.p_kw | kW | `Edificio C6::kW sys` |
| 16 | uja.jaen.energia.consumo.edificio_d1.p_kw | kW | `Edificio D1::kW sys` |
| 17 | uja.jaen.energia.consumo.d1_caf.p_kw | kW | `D1 Cafeteria::kW sys` |
| 18 | uja.jaen.energia.consumo.edificio_d2.p_kw | kW | `Edificio D2::kW sys` |
| 19 | uja.jaen.energia.consumo.edificio_d3.p_kw | kW | `Edificio D3::kW sys` |
| 20 | uja.jaen.energia.consumo.edificio_d4.p_kw | kW | `Edificio D4::kW sys` |
| 21 | uja.jaen.energia.consumo.plaz_pueblos.p_kw | kW | `Plaz. Pueblos::kW sys` |
| 22 | uja.jaen.energia.consumo.um_c4.p_kw | kW | `Edificio U.M. C4::kW sys` |
| 23 | uja.jaen.energia.consumo.polideportivo.p_kw | kW | `P. Polideportivo::kW sys` |
| 24 | uja.jaen.energia.consumo.c_futbol.p_kw | kW | `C.futbol::kW sys` |
| 25 | uja.jaen.energia.consumo.ae_magisterio.p_kw | kW | `A.E. Magisterio::kW sys` |

### 1.2 Jaén — Consumo agua (25)
Gateway: `gw_jaen_agua`
`data.var` esperado: `m3` (confirmar)

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 26 | uja.jaen.agua.consumo.edificio_a0.v_m3 | m³ | `Edificio A0::m3` |
| 27 | uja.jaen.agua.consumo.edificio_a1.v_m3 | m³ | `Edificio A1::m3` |
| 28 | uja.jaen.agua.consumo.edificio_a2.v_m3 | m³ | `Edificio A2::m3` |
| 29 | uja.jaen.agua.consumo.edificio_a3.v_m3 | m³ | `Edificio A3::m3` |
| 30 | uja.jaen.agua.consumo.edificio_a4.v_m3 | m³ | `Edificio A4::m3` |
| 31 | uja.jaen.agua.consumo.edificio_b1.v_m3 | m³ | `Edificio B1::m3` |
| 32 | uja.jaen.agua.consumo.edificio_b2.v_m3 | m³ | `Edificio B2::m3` |
| 33 | uja.jaen.agua.consumo.edificio_b3.v_m3 | m³ | `Edificio B3::m3` |
| 34 | uja.jaen.agua.consumo.edificio_b4.v_m3 | m³ | `Edificio B4::m3` |
| 35 | uja.jaen.agua.consumo.edificio_b5.v_m3 | m³ | `Edificio B5::m3` |
| 36 | uja.jaen.agua.consumo.edificio_c1.v_m3 | m³ | `Edificio C1::m3` |
| 37 | uja.jaen.agua.consumo.edificio_c2.v_m3 | m³ | `Edificio C2::m3` |
| 38 | uja.jaen.agua.consumo.edificio_c3.v_m3 | m³ | `Edificio C3::m3` |
| 39 | uja.jaen.agua.consumo.edificio_c5.v_m3 | m³ | `Edificio C5::m3` |
| 40 | uja.jaen.agua.consumo.edificio_c6.v_m3 | m³ | `Edificio C6::m3` |
| 41 | uja.jaen.agua.consumo.edificio_d1.v_m3 | m³ | `Edificio D1::m3` |
| 42 | uja.jaen.agua.consumo.d1_caf.v_m3 | m³ | `D1 Cafeteria::m3` |
| 43 | uja.jaen.agua.consumo.edificio_d2.v_m3 | m³ | `Edificio D2::m3` |
| 44 | uja.jaen.agua.consumo.edificio_d3.v_m3 | m³ | `Edificio D3::m3` |
| 45 | uja.jaen.agua.consumo.edificio_d4.v_m3 | m³ | `Edificio D4::m3` |
| 46 | uja.jaen.agua.consumo.plaz_pueblos.v_m3 | m³ | `Plaz. Pueblos::m3` |
| 47 | uja.jaen.agua.consumo.um_c4.v_m3 | m³ | `Edificio U.M. C4::m3` |
| 48 | uja.jaen.agua.consumo.polideportivo.v_m3 | m³ | `P. Polideportivo::m3` |
| 49 | uja.jaen.agua.consumo.c_futbol.v_m3 | m³ | `C.futbol::m3` |
| 50 | uja.jaen.agua.consumo.ae_magisterio.v_m3 | m³ | `A.E. Magisterio::m3` |

### 1.3 Linares — Agua (9) + Energía (4) = 13
Gateway: `gw_linares_mix`

Agua (9):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 51 | uja.linares.agua.consumo.pabellon_polideportivo.v_m3 | m³ | `Pabellon polideportivo::m3` |
| 52 | uja.linares.agua.consumo.servicios_generales.v_m3 | m³ | `Servicios Generales::m3` |
| 53 | uja.linares.agua.consumo.cafeteria.v_m3 | m³ | `Cafeteria::m3` |
| 54 | uja.linares.agua.consumo.cocina_comedor.v_m3 | m³ | `Cocina-Comedor::m3` |
| 55 | uja.linares.agua.consumo.laboratorios.v_m3 | m³ | `Laboratorios::m3` |
| 56 | uja.linares.agua.consumo.aularios.v_m3 | m³ | `Aularios::m3` |
| 57 | uja.linares.agua.consumo.departamental.v_m3 | m³ | `Departamental::m3` |
| 58 | uja.linares.agua.consumo.riego_aularios.v_m3 | m³ | `Riego Aularios::m3` |
| 59 | uja.linares.agua.consumo.reciclada_general.v_m3 | m³ | `Reciclada general::m3` |

Energía (4) — placeholders hasta confirmar meter.name:
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 60 | uja.linares.energia.consumo.linea_01.p_kw | kW | `<LINEA_01>::kW sys` |
| 61 | uja.linares.energia.consumo.linea_02.p_kw | kW | `<LINEA_02>::kW sys` |
| 62 | uja.linares.energia.consumo.linea_03.p_kw | kW | `<LINEA_03>::kW sys` |
| 63 | uja.linares.energia.consumo.linea_04.p_kw | kW | `<LINEA_04>::kW sys` |

### 1.4 FV Endesa Jaén (18)
Gateway: `gw_endesa_jaen`
- 12 inversores (kW AC)
- CT total (kW)
- Radiación en 5 ubicaciones (W/m²) — MAPEADA desde gateway

Inversores (12):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 64 | uja.jaen.fv.endesa.inv01.p_ac_kw | kW | `<INV01_METER>::kW sys` |
| 65 | uja.jaen.fv.endesa.inv02.p_ac_kw | kW | `<INV02_METER>::kW sys` |
| 66 | uja.jaen.fv.endesa.inv03.p_ac_kw | kW | `<INV03_METER>::kW sys` |
| 67 | uja.jaen.fv.endesa.inv04.p_ac_kw | kW | `<INV04_METER>::kW sys` |
| 68 | uja.jaen.fv.endesa.inv05.p_ac_kw | kW | `<INV05_METER>::kW sys` |
| 69 | uja.jaen.fv.endesa.inv06.p_ac_kw | kW | `<INV06_METER>::kW sys` |
| 70 | uja.jaen.fv.endesa.inv07.p_ac_kw | kW | `<INV07_METER>::kW sys` |
| 71 | uja.jaen.fv.endesa.inv08.p_ac_kw | kW | `<INV08_METER>::kW sys` |
| 72 | uja.jaen.fv.endesa.inv09.p_ac_kw | kW | `<INV09_METER>::kW sys` |
| 73 | uja.jaen.fv.endesa.inv10.p_ac_kw | kW | `<INV10_METER>::kW sys` |
| 74 | uja.jaen.fv.endesa.inv11.p_ac_kw | kW | `<INV11_METER>::kW sys` |
| 75 | uja.jaen.fv.endesa.inv12.p_ac_kw | kW | `<INV12_METER>::kW sys` |

CT total (1) + Radiación (5):
| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 76 | uja.jaen.fv.endesa.ct_total.p_kw | kW | `<CT_METER>::kW sys` |
| 77 | uja.jaen.fv.endesa.rad01.g_wm2 | W/m² | `<RAD01_METER>::Irradiación transitoria` |
| 78 | uja.jaen.fv.endesa.rad02.g_wm2 | W/m² | `<RAD02_METER>::Irradiación transitoria` |
| 79 | uja.jaen.fv.endesa.rad03.g_wm2 | W/m² | `<RAD03_METER>::Irradiación transitoria` |
| 80 | uja.jaen.fv.endesa.rad04.g_wm2 | W/m² | `<RAD04_METER>::Irradiación transitoria` |
| 81 | uja.jaen.fv.endesa.rad05.g_wm2 | W/m² | `<RAD05_METER>::Irradiación transitoria` |

### 1.5 FV Endesa Linares (5)
Gateway: `gw_endesa_linares`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 82 | uja.linares.fv.endesa.inv01.p_ac_kw | kW | `<INV01_METER>::kW sys` |
| 83 | uja.linares.fv.endesa.inv02.p_ac_kw | kW | `<INV02_METER>::kW sys` |
| 84 | uja.linares.fv.endesa.inv03.p_ac_kw | kW | `<INV03_METER>::kW sys` |
| 85 | uja.linares.fv.endesa.ct_total.p_kw | kW | `<CT_METER>::kW sys` |
| 86 | uja.linares.fv.endesa.rad01.g_wm2 | W/m² | `<RAD01_METER>::Irradiación transitoria` |

### 1.6 FV Autoconsumo Jaén (10)
Gateway: `gw_autoconsumo_jaen`

| # | RT_ID | Unidad | Mapeo (source_key) |
|---:|---|---|---|
| 87 | uja.jaen.fv.auto.inv01.p_ac_kw | kW | `<INV01_METER>::kW sys` |
| 88 | uja.jaen.fv.auto.inv02.p_ac_kw | kW | `<INV02_METER>::kW sys` |
| 89 | uja.jaen.fv.auto.inv03.p_ac_kw | kW | `<INV03_METER>::kW sys` |
| 90 | uja.jaen.fv.auto.inv04.p_ac_kw | kW | `<INV04_METER>::kW sys` |
| 91 | uja.jaen.fv.auto.inv05.p_ac_kw | kW | `<INV05_METER>::kW sys` |
| 92 | uja.jaen.fv.auto.ct_total.p_kw | kW | `<CT_METER>::kW sys` |
| 93 | uja.jaen.fv.auto.rad01.g_wm2 | W/m² | `<RAD01_METER>::Irradiación transitoria` |
| 94 | uja.jaen.fv.auto.rad02.g_wm2 | W/m² | `<RAD02_METER>::Irradiación transitoria` |
| 95 | uja.jaen.fv.auto.rad03.g_wm2 | W/m² | `<RAD03_METER>::Irradiación transitoria` |
| 96 | uja.jaen.fv.auto.rad04.g_wm2 | W/m² | `<RAD04_METER>::Irradiación transitoria` |

---

## 2) VARIABLES CALCULADAS — definiciones y fórmulas exactas

### 2.1 Agregación de potencia (tiempo real)
| RT_ID | Unidad | Fórmula exacta |
|---|---|---|
| uja.jaen.energia.consumo.total.p_kw | kW | Σ de las 25 potencias `uja.jaen.energia.consumo.*.p_kw` |
| uja.linares.energia.consumo.total.p_kw | kW | `linea_01 + linea_02 + linea_03 + linea_04` |
| uja.jaen.fv.endesa.total.p_kw | kW | Σ `uja.jaen.fv.endesa.inv01..inv12.p_ac_kw` |
| uja.linares.fv.endesa.total.p_kw | kW | Σ `uja.linares.fv.endesa.inv01..inv03.p_ac_kw` |
| uja.jaen.fv.auto.total.p_kw | kW | Σ `uja.jaen.fv.auto.inv01..inv05.p_ac_kw` |
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
