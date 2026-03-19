---
description: Execute financial calculations using v4.1.0 financial engine with Agent Harness delegation.
---

# Skill: V4 Financial Calculation

## Propósito
Ejecutar cálculos financieros (escenarios y pricing) usando el motor financiero v4.1.0 real a través del Agent Harness.

## Inputs Requeridos
- rooms: int - Número de habitaciones
- adr_cop: float - ADR en COP (o null para resolución regional)
- occupancy_rate: float - Porcentaje de ocupación (0-1)
- direct_channel_percentage: float - Porcentaje canal directo (0-1)
- region: str - Región para benchmarks (eje_cafetero, caribe, etc.)
- hotel_id: str - Identificador único del hotel (URL)
- hotel_name: str - Nombre del hotel

## Flujo de Ejecución

1. **ADR Resolution** (si no proporcionado):
   - Usar `modules.financial_engine.resolve_adr_with_shadow()`
   - Prioridad: user_provided > regional_benchmark > legacy_default
   - Feature flags controlan shadow/canary/active mode

2. **Scenario Calculation**:
   - Usar `modules.financial_engine.ScenarioCalculator`
   - Calcular Conservador (70%), Realista (20%), Optimista (10%)
   - Validar orden: Conservador >= Realista >= Optimista

3. **Pricing Calculation** (Hybrid Model):
   - Usar `modules.financial_engine.calculate_price_with_shadow()`
   - Aplicar GATE validation (3%-6% pain ratio)
   - Determinar tier según número de habitaciones

4. **Confidence Scoring**:
   - VERIFIED (>=0.9): 2+ fuentes coinciden
   - ESTIMATED (0.5-0.9): 1 fuente o benchmark
   - CONFLICT (<0.5): Fuentes contradicen

## Outputs
- scenarios: dict - Conservador, Realista, Optimista con probabilidades
- expected_monthly_cop: float - Valor esperado ponderado
- pricing: dict - Tier, precio mensual, pain ratio, compliance
- adr_resolution: dict - ADR usado, fuente, confianza

## Feature Flags
- FINANCIAL_REGIONAL_ADR_ENABLED: true/false
- FINANCIAL_PRICING_HYBRID_ENABLED: true/false
- FINANCIAL_REGIONAL_ADR_MODE: shadow/canary/active/legacy
- FINANCIAL_PRICING_HYBRID_MODE: shadow/canary/active/legacy

## Plan de Recuperación
- Si ADR resolution falla: usar default regional
- Si escenarios son inconsistentes: aplicar ajustes automáticos
- Si pricing no pasa GATE: documentar y usar fallback
