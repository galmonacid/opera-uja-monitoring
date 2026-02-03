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
