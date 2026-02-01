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
