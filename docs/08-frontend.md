# 08 — Frontend (SPA + React/Vite + Amplify)

## Decision
Para el MVP se implementa una SPA (Single Page Application) desplegada en AWS Amplify.

Motivos:
- Caso de uso: dashboards con polling.
- No hay requerimiento explicito de SEO/SSR.
- Menor coste/operacion y menor riesgo de gasto ante abuso.
- CI/CD simple.

## Stack
- React + Vite
- UI: CSS custom + SVG inline
- Charts: SVG propio (area chart MVP)
- Consumo API: fetch

## Estructura en repo
- App SPA en `frontend/`
- Assets: `frontend/src/assets/sections/campus.png`
- Config Amplify en `amplify.yml`
- Variables en `frontend/.env.example` (usar `VITE_API_BASE`)

## MVP (2 secciones)
1. Balance de energia en tiempo real
   - Infografia: demanda campus, FV campus, energia de red
   - Grafica de areas 24h desde `/series/24h`
2. Mapa del campus
   - `campus.png` con overlays por edificio
   - Valores instantaneos desde `/realtime` segun `gateway_variable_map_gw_jaen_energia`
   - Labels de valor colocados a la derecha del identificador de edificio en la imagen

## Estado actual implementado
- Dashboard principal Jaen:
  - Demanda = suma `uja.jaen.energia.consumo.*.p_kw`
  - FV = suma de inversores `uja.jaen.fv.endesa.*.p_ac_kw` + `uja.jaen.fv.auto.ct_total.p_kw`
  - Red = `max(demanda - fv, 0)`
- Pantalla `#/validacion`:
  - 6 tarjetas, una por gateway requerido
  - `realtime` por `campus/domain/gateway_id`
  - series 24h por `campus + metric` para evitar mezclar `ct_total` con inversores
  - agua muestra consumo por intervalo (`m3`) a partir de contadores
  - monthly puede mostrarse reconstruido desde `daily` si aún no existe agregado materializado

## Actualizacion de datos (MVP)
- `/realtime`: cada 60s
- `/series/24h`: cada 5 min

## Runbook rapido (local)
```bash
cd frontend
npm install
npm run dev
```

## Amplify (build)
```yaml
appRoot: frontend
```

## URL (Amplify)
- App ID: `dqb16efeyz8k3`
- URL: `https://main.dqb16efeyz8k3.amplifyapp.com`
