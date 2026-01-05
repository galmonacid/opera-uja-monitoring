# 02 — Gateways y topics MQTT (AWS IoT Core)

## 1) Número de gateways
Total: 6 gateways (según requerimiento).

## 2) Convención de topics
Prefijo corporativo: `uja`

Formato:
- `uja/<campus>/<dominio>/<tipo>/<gateway_id>`

## 3) Topics definitivos (1 por gateway)

| Gateway (funcional) | Campus | Datos | gateway_id | Topic |
|---|---|---|---|---|
| Consumo energía edificios | Jaén | Potencia por edificio | gw_jaen_energia | `uja/jaen/consumo/energia/gw_jaen_energia` |
| Consumo agua edificios | Jaén | m³ por edificio | gw_jaen_agua | `uja/jaen/consumo/agua/gw_jaen_agua` |
| Consumo mixto | Linares | agua + energía | gw_linares_mix | `uja/linares/consumo/mix/gw_linares_mix` |
| FV Endesa | Jaén | inversores + CT + radiación | gw_endesa_jaen | `uja/jaen/produccion/fv_endesa/gw_endesa_jaen` |
| FV Endesa | Linares | inversores + CT + radiación | gw_endesa_linares | `uja/linares/produccion/fv_endesa/gw_endesa_linares` |
| FV Autoconsumo | Jaén | inversores + CT + radiación | gw_autoconsumo_jaen | `uja/jaen/produccion/fv_autoconsumo/gw_autoconsumo_jaen` |

## 4) Notas
- El nombre de variables en el payload lo define el gateway (no se cambia).
- El mapeo a RT_ID se realiza en backend mediante tabla `gateway_variable_map` (ver `05_data_model_tables.md`).
