# 09 — Seguridad y control de costes (anti-abuso)

## Objetivo
Evitar “cost explosion” por abuso de API o tráfico inesperado.

## Controles
1) AWS WAF delante de API Gateway
- regla rate-based por IP

2) API Gateway throttling
- rate limit + burst (valores a definir)

3) Lambda reserved concurrency
- limita gasto máximo por invocaciones

4) CloudWatch Alarms + AWS Budgets
- alarmas por:
  - invocaciones lambda
  - errores 4xx/5xx
  - requests API
- budgets con alertas

5) Caching (opcional)
- si hay endpoints que se repiten (p.ej. aggregates), se puede cachear en API GW/CloudFront.

## Nota
El mayor riesgo de coste es la API, no el hosting SPA (estático).
