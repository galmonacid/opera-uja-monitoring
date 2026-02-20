# 03 — Contrato de payload y parsing

## 1) Campos observados en payload (ejemplo real)
Campos:
- ver
- sn
- mac
- ip
- srcname
- srctype
- tz
- opt
- meter
- __dt

Donde:
- `meter` contiene una lista de entradas con:
  - `name` (equipo/medidor)
  - `idowner`
  - `time` (epoch seconds)
  - `data[]` con tuplas {var, type, unit, value}

## 2) Punto crítico: JSON válido
En los ejemplos, el payload aparece con formato tipo `[{name=..., data=[{var=...}]}]`
Acción:
- Confirmar con operador si llega como JSON estricto o como formato key=value.
- Si no es JSON, el backend implementa parser robusto (sin OCR).

## 3) Semántica temporal
- `meter.time`: epoch seconds (confirmar si UTC).
- `tz`: timezone del origen (ej: Europe/Paris).
- Regla: normalizar a UTC en backend.

## 4) Duplicados / orden / backlog
Confirmar:
- ¿Puede haber backlog si cae la conexión?
- ¿Puede llegar fuera de orden?
- ¿Puede haber duplicados de timestamp?
Backend debe:
- Deduplicar por (rt_id, ts_event) en histórico si aplica.
- Mantener “latest” por rt_id.
 - Si un mismo evento trae varias entradas `meter[]` con tiempos distintos, se almacenan todas en histórico.

## 5) Contrato mínimo para la solución
Requisitos del payload para que la solución funcione:
- `meter.time` presente.
- `data.var`, `data.unit`, `data.value` presentes.
- `meter.name` estable en el tiempo.
 - Valores inválidos (sentinelas) se descartan en ingestión.

### 5.1 Filtro de valores inválidos (sentinelas)
Se descartan valores no finitos o fuera de rango razonable (`abs(value) > 1e6` por defecto).
Este umbral es configurable vía `MAX_VALID_VALUE`.

## 6) Lista de datos a solicitar al operador (para cerrar mapeo)
- Catálogo por gateway:
  - meter.name
  - data.var
  - unit
  - Jaén agua observado: `meter.name = "UJA-Agua-Opera--m3.Edif_*"` y `data.var = "m3"`
  - Linares mix observado: `meter.name = "CCTL-TOTAL.<...>"`, `data.var = "m3"` y `data.var = "kW sys"` (normalizado a `KW sys`)
  - FV Endesa Jaén observado: `meter.name = "Jaén-OPERA-Endesa--FV.UJA"` (var `Tot_FV_kW sys`, `Tot_FV_kWh`, `P3_Inv1_kW sys`, `P3_Radiación`, etc.)
- Frecuencia de envío por gateway.
- Agua: contador acumulado vs incremental.
- Identificación exacta de:
  - inversores FV (Endesa/autoconsumo)
  - CT total
  - radiación por ubicación
