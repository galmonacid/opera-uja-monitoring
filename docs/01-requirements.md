# 01 — Requerimientos y alcance

## 1) Contexto
Se requiere una solución básica, de bajo coste, para monitorizar y publicar (web pública) consumos y generación energética/agua en UJA.

La solución se implementará en AWS usando:
- AWS IoT Core
- Amazon Timestream
- AWS Lambda (Python y/o Node.js)
- Amazon DynamoDB
- API Gateway
- Frontend en AWS Amplify (SPA)

Acceso:
- Público, sin contraseña.
- Enlace desde la web de la Unidad Técnica.

## 2) Fuentes (gateways) y variables en tiempo real

### 2.1 Campus Jaén — Consumo eléctrico
- 1 gateway registra consumo eléctrico de edificios.
- Total variables requeridas (RT): 28 (25 consumo red + 3 autoconsumo FV en edificios A0/C4/Magisterio).

### 2.2 Campus Jaén — Consumo agua
- 1 gateway registra consumo de agua.
- Unidad: m³.
- Total variables requeridas (RT): 25.

### 2.3 Campus Linares — Consumo agua y energía
- 1 gateway registra consumo de agua (9 vars) y energía (4 vars).
- Total variables requeridas (RT): 13.

### 2.4 Campus Jaén — FV Endesa
- 1 gateway registra producción FV Endesa Jaén.
- 12 inversores: potencia AC (kW) por inversor.
- Potencia total que llega al CT (kW).
- Radiación (W/m²) en 5 ubicaciones.
- Total variables requeridas (RT): 18.

### 2.5 Campus Linares — FV Endesa
- 1 gateway registra FV Endesa Linares.
- 3 inversores: potencia AC (kW) por inversor.
- Potencia total al CT (kW).
- Radiación (W/m²) en 1 ubicación.
- Total variables requeridas (RT): 5.

### 2.6 Campus Jaén — FV Autoconsumo (nuevos)
- 1 gateway registra autoconsumo: Pérgola, parte del parking, fachada B5, cubierta B5.
- 5 inversores: potencia AC (kW) por inversor.
- Potencia total al CT (kW).
- Radiación (W/m²) en 4 ubicaciones.
- Total variables requeridas (RT): 10.

## 3) Variables calculadas requeridas
- Energía diaria, mensual y anual.
- Consumo de agua diario, mensual y anual.
- Índices/indicadores de balance energético (como en el PowerPoint).
- CO2 evitado (aparece en pantallas; se incorpora como variable calculada).

## 4) Web (5 secciones)
- 5 secciones similares al PowerPoint.
- Visualizaciones: tiempo real, últimas 24h, acumulados y KPIs.
- Fondo/identidad gráfica: se usará el material suministrado.

## 5) Restricciones / priorización
- Propuesta básica (bajo coste).
- Se evita sobre-ingeniería.
- Se diseña para ampliación en fase 2 (más páginas y funcionalidades).

## 6) Decisiones acordadas
- Tópico por gateway: ✅ 1 topic por gateway.
- Frontend: ✅ SPA (React + Vite) desplegada en AWS Amplify.
- Tablas separadas en DynamoDB (no single-table): ✅ aceptado.
- Control anti-abuso API: ✅ WAF + throttling + quotas + caching cuando aplique.
