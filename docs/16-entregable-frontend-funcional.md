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
  devuelve los KPIs instantáneos del scope `las_lagunillas`, calculados en backend sumando las fuentes de demanda y FV definidas para ese campus y derivando `red` y `autoconsumo`.
- `/v1/kpis?scope=ctl_linares`
  devuelve los KPIs instantáneos del scope `ctl_linares`, calculados con la suma de demanda de Linares y la FV instantánea de `ct_total`.
- `/v1/series/24h?scope=las_lagunillas&interval_minutes=15`
  devuelve la curva agregada de `Demanda` y `FV` de Las Lagunillas; cada punto representa un bin de 15 minutos y, en potencia, usa la media de muestras válidas del intervalo.
- `/v1/series/24h?scope=ctl_linares&interval_minutes=15`
  devuelve la curva agregada de `Demanda` y `FV` de CTL Linares con la misma lógica de agregación temporal.

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
    devuelve el estado instantáneo del campus calculado a partir del scope energético correspondiente.
  - `/v1/series/24h?scope=...&interval_minutes=15`
    devuelve la serie agregada de `Demanda` y `FV` del campus en bins de 15 minutos.
- Acumulados energéticos:
  - `/v1/aggregates/daily?campus=...&metric=energia_consumo&asset=total`
    devuelve la energía diaria total del campus, obtenida por integración temporal de la potencia y agregada por día.
  - `/v1/aggregates/monthly?campus=...&metric=energia_consumo&asset=total`
    devuelve la energía mensual total del campus, calculada como suma de los valores diarios o reconstruida desde ellos si es necesario.

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
  devuelve las últimas lecturas válidas disponibles del campus de Jaén para los RT incluidos en la respuesta.
- `/v1/realtime?campus=linares`
  devuelve las últimas lecturas válidas disponibles del campus de Linares.

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
    devuelve los últimos contadores válidos de agua asociados al gateway de Jaén.
  - `/v1/realtime?gateway_id=gw_linares_mix`
    devuelve los últimos contadores válidos de agua de Linares presentes en el gateway mixto.
- Tendencia:
  - `/v1/series/24h?campus=jaen&metric=agua_consumo&interval_minutes=15`
    devuelve el consumo de agua por intervalo en Jaén; cada punto se calcula como diferencia entre el último contador válido de un bin y el del bin anterior.
  - `/v1/series/24h?campus=linares&metric=agua_consumo&interval_minutes=15`
    devuelve el consumo de agua por intervalo en Linares con la misma lógica.
- Totales:
  - `/v1/aggregates/daily?...metric=agua_consumo...`
    devuelve el consumo total diario agregado a partir de los incrementos válidos de los contadores.
  - `/v1/aggregates/monthly?...metric=agua_consumo...`
    devuelve el consumo total mensual calculado como suma de los diarios.
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
    devuelve las últimas lecturas válidas del gateway Endesa de Jaén, incluyendo `ct_total`, inversores e irradiancias.
  - `/v1/realtime?gateway_id=gw_autoconsumo_jaen`
    devuelve las últimas lecturas válidas del gateway de autoconsumo de Jaén.
  - `/v1/realtime?gateway_id=gw_endesa_linares`
    devuelve las últimas lecturas válidas del gateway Endesa de Linares.
- Curvas de potencia:
  - `/v1/series/24h?campus=jaen&metric=fv_endesa&interval_minutes=15`
    devuelve la curva agregada de producción Endesa Jaén; en cada bin se usa la media de valores válidos y el agregado energético se basa en la producción definida para esa métrica.
  - `/v1/series/24h?campus=jaen&metric=fv_auto&interval_minutes=15`
    devuelve la curva agregada de autoconsumo Jaén con bins de 15 minutos.
  - `/v1/series/24h?campus=linares&metric=fv_endesa&interval_minutes=15`
    devuelve la curva agregada de FV Endesa Linares.
- Irradiancia:
  - `/v1/series/24h?rt_id=...&aggregation=avg&interval_minutes=15`
    devuelve la irradiancia agregada media de una o varias sondas, calculada promediando sus series válidas por bin.
- Acumulados:
  - `/v1/aggregates/daily?...metric=fv_endesa|fv_auto...`
    devuelve la producción diaria calculada por integración temporal de la potencia.
  - `/v1/aggregates/monthly?...metric=fv_endesa|fv_auto...`
    devuelve la producción mensual como suma de los valores diarios.

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
  devuelve el último valor técnico disponible de cada RT consultado.
- `/v1/series/24h`
  devuelve la serie técnica de las últimas 24 horas, ya sea por scope, métrica, prefijo o RT explícito, según el panel consultado.
- `/v1/aggregates/daily`
  devuelve la agregación diaria persistida o reconstruida de la métrica solicitada.
- `/v1/aggregates/monthly`
  devuelve la agregación mensual persistida o reconstruida de la métrica solicitada.
- `/v1/anomalies`
  devuelve el registro técnico de anomalías detectadas en ingestión o backfill, con valor bruto y valor aplicado.

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
