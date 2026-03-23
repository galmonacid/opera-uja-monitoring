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
   - Dos paneles: `Campus Las Lagunillas` y `Campus CTL Linares`
   - KPIs por panel desde `/kpis?scope=...`
   - Grafica de areas 24h por panel desde `/series/24h?scope=...`
2. Mapa del campus
   - `campus.png` con overlays por edificio
   - Valores instantaneos desde `/realtime` segun `gateway_variable_map_gw_jaen_energia`
   - Labels de valor colocados a la derecha del identificador de edificio en la imagen

## Estado actual implementado
- Dashboard principal por scope:
  - `las_lagunillas`:
    - Demanda = A0-A4, B1-B5, C1-C3/C5/C6, D1-D4 y `carga_vhe`
    - FV = `abs(uja.jaen.fv.endesa.ct_total.p_kw)` + `uja.jaen.fv.auto.ct_total.p_kw` + `uja.jaen.fv.auto.edificio_a0.p_kw`
  - `ctl_linares`:
    - Demanda = `lab_sg_t1 + lab_sg_t2 + urbanizacion + aulario_departamental + polideportivo`
    - FV = `uja.linares.fv.endesa.ct_total.p_kw`
  - Cada panel muestra `demanda`, `FV`, `red` y `autoconsumo %`
  - Si backend marca `partial`, el panel muestra aviso visible y placeholders en lugar de curva agregada
- Mapa principal:
  - mantiene el `campus.png`
  - se usa como vista operativa de Las Lagunillas
- Pantalla `#/validacion`:
  - 6 tarjetas, una por gateway requerido
  - `realtime` por `campus/domain/gateway_id`
  - series 24h por `campus + metric` para evitar mezclar `ct_total` con inversores
  - agua muestra consumo por intervalo (`m3`) a partir de contadores
  - monthly puede mostrarse reconstruido desde `daily` si aún no existe agregado materializado
- Convención visual:
  - el balance de campus y las vistas analíticas muestran FV/autoconsumo en positivo
  - `uja.jaen.fv.endesa.ct_total.p_kw` se recibe en raw con signo técnico y solo se transforma a magnitud positiva en esas vistas
  - `Validación` conserva el dato técnico original con su signo raw
  - la vista de `FV Endesa Jaén` usa `ct_total` como KPI instantánea y mantiene la suma de inversores como referencia secundaria

## Actualizacion de datos (MVP)
- `/realtime`: cada 60s
- `/kpis?scope=...`: cada 60s
- `/series/24h?scope=...`: cada 5 min

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
