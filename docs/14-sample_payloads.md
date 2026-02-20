# 14 — Samples de payload (redactados)

Este documento guarda ejemplos **reales pero redactados** (sin IP/MAC/SN) para:
- Validar el parser de ingestión.
- Alinear el `gateway_variable_map` con el `source_key`.

## 14.1 Jaén — Consumo energía (gw_jaen_energia)

Notas observadas:
- `meter.name` llega con prefijo `UJA-OPERA--Edif-.` (se normaliza en la Lambda).
- `data.var` llega con `kW sys` en minúsculas (se normaliza a `KW sys`).
- Algunos valores son claramente inválidos (p. ej. `1.84467440737096e+15`), probablemente **sentinelas** del gateway.

### 14.1.1 Autoconsumo FV

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "UJA-OPERA--Edif-.Autoconsumo_FV_Edif",
      "time": 1770157620,
      "data": [
        { "var": "FV_A0_kW sys", "unit": "kW", "value": 0.0 },
        { "var": "FV_C4_kW sys", "unit": "kW", "value": 0.0 },
        { "var": "FV_Magisterio_kW sys", "unit": "kW", "value": 0.0 }
      ]
    }
  ]
}
```

### 14.1.2 Consumo Edif. Lagunillas

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "UJA-OPERA--Edif-.Consumo_Edif_Lagunillas",
      "time": 1770157620,
      "data": [
        { "var": "A0_kW sys", "unit": "kW", "value": 24.305001 },
        { "var": "A1_kW sys", "unit": "kW", "value": 1.84467440737096e+15 },
        { "var": "B3_kW sys", "unit": "kW", "value": 1.84467440737096e+15 },
        { "var": "Carga_VHE_kW sys", "unit": "kW", "value": 0.24 }
      ]
    }
  ]
}
```

### 14.1.3 Consumo Edif. Resto

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "UJA-OPERA--Edif-.Consumo_Edif_Resto",
      "time": 1770157620,
      "data": [
        { "var": "Apartamentos_kW sys", "unit": "kW", "value": 28.885636 },
        { "var": "C4_kW sys", "unit": "kW", "value": 13.671137 },
        { "var": "Magisterio_kW sys", "unit": "kW", "value": 19.812576 },
        { "var": "Polideportivo_kW sys", "unit": "kW", "value": 10.877773 },
        { "var": "Residencia_kW sys", "unit": "kW", "value": 33.032916 }
      ]
    }
  ]
}
```

### 14.2 FV Endesa Jaén (gw_endesa_jaen)

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "Jaén-OPERA-Endesa--FV.UJA",
      "time": 1771527600,
      "data": [
        { "var": "Temperatura", "unit": "°C", "value": 10.6 },
        { "var": "Tot_FV_kW sys", "unit": "kW", "value": 0.125242 },
        { "var": "Tot_FV_kWh", "unit": "kWh", "value": 6198112.73 },
        { "var": "P3_Radiación", "unit": "W", "value": 0.0 },
        { "var": "P3_Inv1_kW sys", "unit": "kW", "value": 0.0 }
      ]
    }
  ]
}
```

### 14.3 Linares consumo mixto (gw_linares_mix)

Notas observadas:
- `meter.name` llega como `CCTL-TOTAL.<...>`.
- `data.var` llega como `m3` (agua) y `kW sys` (energía, normalizado a `KW sys` en ingestión).
- Se observan sentinelas/valores corruptos en agua (ej. `8.33e+14`), descartados por el filtro (`abs(value) > 1e6`).

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "CCTL-TOTAL.Cons_Agua_S_Generales",
      "time": 1770351480,
      "data": [{ "var": "m3", "unit": "m3", "value": 1017.6 }]
    },
    {
      "name": "CCTL-TOTAL.Cons_Elec_Polideportivo",
      "time": 1770351480,
      "data": [{ "var": "kW sys", "unit": "kW", "value": 6.357821 }]
    }
  ]
}
```

### 14.4 Jaén consumo agua (gw_jaen_agua)

Notas observadas:
- `meter.name` llega como `UJA-Agua-Opera--m3.Edif_<asset>`.
- `data.var` llega como `m3`.
- Son contadores incremental totalizador (consumo diario por diferencia fin-inicio).

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "UJA-Agua-Opera--m3.Edif_A0",
      "time": 1770351480,
      "data": [{ "var": "m3", "unit": "m3", "value": 1234.5 }]
    },
    {
      "name": "UJA-Agua-Opera--m3.Edif_D1_Cafeteria",
      "time": 1770351480,
      "data": [{ "var": "m3", "unit": "m3", "value": 234.1 }]
    }
  ]
}
```

### 14.5 Jaén FV autoconsumo UNIVER (gw_autoconsumo_jaen)

Notas observadas:
- `meter.name` observado: `OPERA-UNIVER--Autocon--FV.UJA`.
- `data.var` observado incluye `UJA.Tot_FV_kW sys`, `UJA.Tot_FV_kWh`, `UJA.Pérgola_kW sys`, `UJA.B5_Radiación`, etc.
- La potencia en CT (`UJA.Tot_FV_kW sys`) no tiene por qué coincidir exactamente con la suma de inversores.

```json
{
  "ver": "3.0.1",
  "sn": "<REDACTED>",
  "mac": "<REDACTED>",
  "ip": "<REDACTED>",
  "tz": "Europe/Paris",
  "opt": "insert_data",
  "meter": [
    {
      "name": "OPERA-UNIVER--Autocon--FV.UJA",
      "time": 1770351480,
      "data": [
        { "var": "UJA.Temperatura", "unit": "°C", "value": 19.4 },
        { "var": "UJA.Tot_FV_kW sys", "unit": "kW", "value": 72.8 },
        { "var": "UJA.Tot_FV_kWh", "unit": "kWh", "value": 418922.4 },
        { "var": "UJA.Pérgola_kW sys", "unit": "kW", "value": 11.2 },
        { "var": "UJA.B5_Radiación", "unit": "W/m²", "value": 612.5 }
      ]
    }
  ]
}
```
