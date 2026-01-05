# 08 — Frontend (decisión SPA + React/Vite + Amplify)

## Decisión
Para Fase 1 se implementa una SPA (Single Page Application) desplegada en AWS Amplify.

Motivos:
- Caso de uso: dashboards + polling.
- No hay requerimiento explícito de SEO/SSR.
- Menor coste/operación y menor riesgo de gasto ante abuso.
- CI/CD simple.

## Stack
- React + Vite
- UI: Material UI (o similar)
- Charts: Recharts o Chart.js
- Consumo API: fetch/axios

## Secciones (5)
1. Visión general / mapa (campus)
2. Consumo energético
3. Consumo de agua
4. Producción FV
5. Indicadores (balance, CO2)

## Actualización de datos (recomendación)
- /realtime y /kpis: cada 60–120s
- agregados: al cargar vista o cada 5–10 min
