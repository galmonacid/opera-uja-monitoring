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
- Charts: SVG propio (área/línea y doble eje para FV)
- Consumo API: fetch

## Estructura en repo
- App SPA en `frontend/`
- Assets: `frontend/src/assets/sections/campus.png`
- Config Amplify en `amplify.yml`
- Variables en `frontend/.env.example` (usar `VITE_API_BASE`)

## Vistas operativas actuales
1. Balance
   - Dos paneles: `Campus Las Lagunillas` y `Campus Científico Tecnológico de Linares`
   - KPIs por panel desde `/kpis?scope=...`
   - Gráfica de áreas 24h por panel desde `/series/24h?scope=...&interval_minutes=15`
2. Mapa
   - `campus.png` con la capa operativa visible de `Demanda de energía`
   - Valores instantáneos desde `/realtime`
   - Panel inferior con detalle del punto seleccionado
3. Agua
   - Tabla operativa por campus
   - Tendencia 24h desde `/series/24h?campus=...&metric=agua_consumo&interval_minutes=15`
4. Fotovoltaica
   - Vista unificada de FV Endesa y autoconsumo
   - Producción desde `/series/24h?campus=...&metric=fv_*&interval_minutes=15`
   - Irradiancia agregada desde `/series/24h?rt_id=...&aggregation=avg&interval_minutes=15`
5. Validación
   - Gateways con pestañas y tabla global de anomalías

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
  - en esta entrega solo expone la capa `Demanda de energía`
  - mantiene un panel de detalle para el punto seleccionado
- Pantalla `#/validacion`:
  - 6 tarjetas, una por gateway requerido
  - bloque global `Anomalías detectadas` antes de los gateways
  - `realtime` por `campus/domain/gateway_id`
  - series 24h por `campus + metric` para evitar mezclar `ct_total` con inversores
  - agua muestra consumo por intervalo (`m3`) a partir de contadores
  - monthly puede mostrarse reconstruido desde `daily` si aún no existe agregado materializado
  - las anomalías se consultan vía `/v1/anomalies` con filtros reutilizando campus/dominio
- Convención visual:
  - el balance de campus y las vistas analíticas muestran FV/autoconsumo en positivo
  - `uja.jaen.fv.endesa.ct_total.p_kw` se recibe en raw con signo técnico y solo se transforma a magnitud positiva en esas vistas
  - `Validación` conserva el dato técnico original con su signo raw
  - la vista de `FV Endesa Jaén` usa `ct_total` como KPI instantánea y mantiene la suma de inversores como referencia secundaria
  - la vista `Fotovoltaica` integra también autoconsumo; `#/autoconsumo` queda como alias compatible hacia `#/fotovoltaica`

## Actualizacion de datos (MVP)
- `/realtime`: cada 60s
- `/kpis?scope=...`: cada 60s
- `/series/24h?...interval_minutes=15`: cada 5 min
- `/anomalies`: cada 60s cuando la vista `Validación` está activa

## Saneado analítico
- Las gráficas operativas (`Balance`, `Energía`, `Agua`, `Fotovoltaica`) consumen series analíticas que excluyen muestras anómalas.
- En potencia e irradiancia, cada bin visual de `15 min` usa la media de muestras válidas del intervalo.
- En agua, el bin usa el último contador válido del intervalo y la curva se expresa como consumo incremental entre bins consecutivos.
- En balance, si un contribuidor llega anómalo:
  - se trata como `missing`
  - se usa `last observation carried forward` dentro de la ventana de frescura
  - si no existe valor válido reciente, el scope pasa a `partial`
- `Validación` no oculta el problema:
  - latest técnico sigue visible
  - la tabla de anomalías muestra `raw_value`, `applied_value`, `tipo` y `motivo`
- En frontend, las líneas y áreas se segmentan para no unir huecos largos cuando faltan datos válidos.
- Todas las horas visibles del portal se muestran en la zona horaria local del navegador del usuario.

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
