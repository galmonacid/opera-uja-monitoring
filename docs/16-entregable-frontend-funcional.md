# 16 — Entregable funcional del frontend

## 1. Objeto del documento
Este documento describe, en lenguaje funcional, la versión entregada del portal web de monitorización de la Universidad de Jaén.

Su objetivo es explicar:
- qué resuelve cada sección del frontend,
- qué bloques contiene,
- qué información muestra al usuario,
- de qué fuentes de datos se alimenta,
- y cómo se calcula cada indicador principal.

## 2. Criterios generales de funcionamiento
- El portal es una SPA (Single Page Application) desarrollada en React y desplegada en AWS Amplify.
- Todas las horas y fechas visibles se presentan en la hora local del navegador del usuario.
- Las gráficas operativas del portal trabajan con bins de `15 minutos`.
- En potencia e irradiancia, cada bin representa la media de las muestras válidas recibidas dentro de ese intervalo.
- En agua, cada bin toma el último contador válido del intervalo y la gráfica representa el consumo incremental entre bins consecutivos.
- Las muestras anómalas o fuera de rango no deforman la analítica operativa: se excluyen de las series y quedan registradas en la sección `Validación`.

## 3. Sección `Balance`

### Objetivo
Ofrecer una visión ejecutiva y simultánea del estado energético de los dos ámbitos operativos principales:
- Campus Las Lagunillas
- Campus CTL Linares

### Contenido
- Una tarjeta por campus.
- Infografía de flujo energético con `Demanda`, `Energía FV`, `Red` y `Autoconsumo`.
- Curva resumida de las últimas 24 horas.
- Estado de calidad de dato (`OK`, parcial, error o sin datos).
- Accesos directos al resto de módulos del portal.

### Información que muestra
- Demanda instantánea del campus.
- Energía fotovoltaica instantánea considerada en balance.
- Energía tomada de la red.
- Porcentaje de autoconsumo.
- Última actualización de cada campus.
- Evolución de `Demanda` y `FV` durante las últimas 24 horas.

### Fuentes de datos
- `/v1/kpis?scope=las_lagunillas`
- `/v1/kpis?scope=ctl_linares`
- `/v1/series/24h?scope=las_lagunillas&interval_minutes=15`
- `/v1/series/24h?scope=ctl_linares&interval_minutes=15`

### Cálculo
#### Las Lagunillas
- Demanda:
  `A0 + A1 + A2 + A3 + A4 + B1 + B2 + B3 + B4 + B5 + C1 + C2 + C3 + C5 + C6 + D1 + D2 + D3 + D4 + Carga VHE`
- FV:
  `abs(uja.jaen.fv.endesa.ct_total.p_kw) + uja.jaen.fv.auto.ct_total.p_kw + uja.jaen.fv.auto.edificio_a0.p_kw`
- Red:
  `max(Demanda - FV, 0)`
- Autoconsumo:
  `min(Demanda, FV)`
- % Autoconsumo:
  `Autoconsumo / Demanda * 100`

#### CTL Linares
- Demanda:
  `lab_sg_t1 + lab_sg_t2 + urbanizacion + aulario_departamental + polideportivo`
- FV:
  `uja.linares.fv.endesa.ct_total.p_kw`
- Red:
  `max(Demanda - FV, 0)`
- Autoconsumo:
  `min(Demanda, FV)`
- % Autoconsumo:
  `Autoconsumo / Demanda * 100`

## 4. Sección `Energía`

### Objetivo
Permitir una explotación más operativa del balance energético por campus, combinando KPIs de lectura rápida con paneles analíticos.

### Contenido
- Banda superior de KPIs y acumulados por campus.
- Panel operativo por campus.
- Selector de campus: `Todos`, `Las Lagunillas`, `CTL Linares`.
- Selector de periodo: `Actual`, `Diario`, `Mensual`.

### Información que muestra
- En la banda superior:
  - Demanda actual o energía diaria/mensual, según el periodo seleccionado.
  - Porcentaje de autoconsumo del campus.
- En cada panel operativo:
  - Gráfica de `Demanda` y `Generación FV` de las últimas 24 horas.
  - Cuatro bloques: `Demanda`, `Generación FV`, `Red` y `Autoconsumo`.
  - Estado del campus y última actualización.

### Fuentes de datos
- KPIs y curvas:
  - `/v1/kpis?scope=...`
  - `/v1/series/24h?scope=...&interval_minutes=15`
- Acumulados energéticos:
  - `/v1/aggregates/daily?campus=...&metric=energia_consumo&asset=total`
  - `/v1/aggregates/monthly?campus=...&metric=energia_consumo&asset=total`

### Cálculo
- Los valores de `Demanda`, `FV`, `Red` y `Autoconsumo` usan exactamente las mismas reglas que en `Balance`.
- La energía diaria y mensual se obtiene a partir de agregados energéticos del campus.
- La gráfica de 24 horas representa la evolución de `Demanda` y `FV` con bins de `15 minutos`.

## 5. Sección `Mapa`

### Objetivo
Mostrar la distribución espacial de los puntos de demanda sobre el plano del campus y permitir una consulta rápida de cada punto.

### Contenido
- Imagen del plano general del campus.
- Puntos superpuestos sobre la imagen.
- Panel de detalle del punto seleccionado.

### Información que muestra
- Valor instantáneo del punto seleccionado.
- Nombre amigable del elemento.
- Capa activa.
- Última lectura.
- En móvil, el valor se consulta principalmente en el panel de detalle para preservar la legibilidad.

### Alcance de esta entrega
- En esta entrega solo está activa la capa `Demanda de energía`.
- Las capas de `Agua`, `Fotovoltaica` y `Autoconsumo` quedan deshabilitadas en el frontend.
- El modelo interno del mapa conserva la posibilidad de activarlas en una fase posterior, pero no se exponen al usuario final en esta versión.

### Fuentes de datos
- `/v1/realtime?campus=jaen`
- `/v1/realtime?campus=linares`

### Cálculo
- Cada punto muestra el último valor válido disponible para su RT.
- En la capa activa de demanda, los valores se presentan como lectura instantánea en `kW`.
- El mapa no recalcula balances; su función es localización y consulta puntual.

## 6. Sección `Agua`

### Objetivo
Ofrecer una lectura operativa del consumo de agua por campus, combinando tabla instantánea y tendencia temporal.

### Contenido
- Tarjetas de resumen por campus.
- Tabla operativa de puntos de agua.
- Gráfica de tendencia de 24 horas.
- Totales `Diario`, `Mensual` y `Anual`.
- Selector de campus.
- Selector de periodo.

### Información que muestra
- Número de puntos con lectura por campus.
- Consumo diario, mensual y anual.
- Tabla con:
  - Punto
  - Valor actual
  - Unidad
  - Última lectura
- Gráfica de consumo por intervalo.

### Fuentes de datos
- Lectura instantánea:
  - `/v1/realtime?gateway_id=gw_jaen_agua`
  - `/v1/realtime?gateway_id=gw_linares_mix`
- Tendencia:
  - `/v1/series/24h?campus=jaen&metric=agua_consumo&interval_minutes=15`
  - `/v1/series/24h?campus=linares&metric=agua_consumo&interval_minutes=15`
- Totales:
  - `/v1/aggregates/daily?...metric=agua_consumo...`
  - `/v1/aggregates/monthly?...metric=agua_consumo...`
  - el anual se obtiene sumando la serie mensual disponible

### Cálculo
- Los puntos de agua son contadores acumulados.
- El consumo del intervalo se calcula como:
  `contador del bin actual - contador del bin anterior`
- El diario, mensual y anual se construyen sumando esos consumos incrementales agregados.

## 7. Sección `Fotovoltaica`

### Objetivo
Agrupar en una única vista la explotación de generación fotovoltaica y autoconsumo, con una lectura homogénea por instalación.

### Contenido
- Tres bloques de instalación:
  - `FV Endesa Jaén`
  - `Autoconsumo Jaén`
  - `FV Endesa Linares`
- KPIs por instalación:
  - `Potencia instantánea`
  - `Producción diaria`
  - `Producción mensual`
  - `Acumulado anual`
- En `FV Endesa Jaén`, se añade además `Suma inversores` como referencia secundaria.
- Gráfica de doble eje:
  - potencia en eje izquierdo,
  - irradiancia en eje derecho.

### Información que muestra
- Producción actual de la instalación.
- Producción acumulada diaria, mensual y anual.
- Evolución temporal de la potencia.
- Irradiancia agregada media asociada a la instalación.

### Fuentes de datos
- Lectura instantánea:
  - `/v1/realtime?gateway_id=gw_endesa_jaen`
  - `/v1/realtime?gateway_id=gw_autoconsumo_jaen`
  - `/v1/realtime?gateway_id=gw_endesa_linares`
- Curvas de potencia:
  - `/v1/series/24h?campus=jaen&metric=fv_endesa&interval_minutes=15`
  - `/v1/series/24h?campus=jaen&metric=fv_auto&interval_minutes=15`
  - `/v1/series/24h?campus=linares&metric=fv_endesa&interval_minutes=15`
- Irradiancia:
  - `/v1/series/24h?rt_id=...&aggregation=avg&interval_minutes=15`
- Acumulados:
  - `/v1/aggregates/daily?...metric=fv_endesa|fv_auto...`
  - `/v1/aggregates/monthly?...metric=fv_endesa|fv_auto...`

### Cálculo
#### FV Endesa Jaén
- Potencia instantánea mostrada:
  `abs(uja.jaen.fv.endesa.ct_total.p_kw)`
- Métrica secundaria:
  `suma de inv01..inv12`
- Producción diaria/mensual/anual:
  basada en el agregado `fv_endesa`, calculado desde la suma de inversores.
- Irradiancia:
  media de `rad01..rad05`.

#### Autoconsumo Jaén
- Potencia instantánea:
  selección principal del gateway de autoconsumo, mostrada en positivo.
- Producción diaria/mensual/anual:
  agregados `fv_auto`.
- Irradiancia:
  media de `pergola_rad`, `b5_rad` y `fachada_rad`.

#### FV Endesa Linares
- Potencia instantánea:
  `uja.linares.fv.endesa.ct_total.p_kw`
- Producción diaria/mensual/anual:
  agregados `fv_endesa` de Linares.
- Irradiancia:
  `rad01`.

## 8. Sección `Validación`

### Objetivo
Proporcionar una vista técnica para revisar calidad de dato, disponibilidad y consistencia de cada gateway integrado en el sistema.

### Contenido
- Tarjetas resumen:
  - Gateways visibles
  - Anomalías recientes
  - Incidencias
  - Cargas en curso
  - Última sincronización
- Tabla global `Anomalías detectadas`
- Un bloque por gateway con pestañas:
  - `Último valor`
  - `24h`
  - `Diario`
  - `Mensual`

### Información que muestra
- Estado técnico por gateway.
- Últimas lecturas por punto.
- Serie de 24 horas.
- Agregados diarios y mensuales.
- Historial reciente de anomalías detectadas, incluyendo valor bruto y valor aplicado.

### Fuentes de datos
- `/v1/realtime`
- `/v1/series/24h`
- `/v1/aggregates/daily`
- `/v1/aggregates/monthly`
- `/v1/anomalies`

### Cálculo
- `Último valor` muestra el dato técnico más reciente disponible por RT.
- `24h` muestra la serie técnica correspondiente al gateway y dominio.
- `Diario` y `Mensual` muestran los agregados persistidos o reconstruidos por la API cuando aplica.
- `Anomalías detectadas` muestra el registro técnico de valores descartados, ajustados o fuera de rango, sin ocultar la evidencia del problema.

## 9. Resumen funcional de la entrega
- El portal queda organizado en `Balance`, `Energía`, `Mapa`, `Agua`, `Fotovoltaica` y `Validación`.
- `Autoconsumo` se integra dentro de `Fotovoltaica`.
- Todas las gráficas operativas trabajan con bins de `15 minutos`.
- Todas las horas se presentan en la hora local del usuario.
- El `Mapa` se entrega con una única capa visible: `Demanda de energía`.
