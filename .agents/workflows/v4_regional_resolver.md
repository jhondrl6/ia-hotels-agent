---
description: Resolve regional ADR and benchmarks using plan_maestro_data.json with Agent Harness.
---

# Skill: V4 Regional Resolver

## Propósito
Resolver benchmarks regionales (ADR, ocupación) usando `data/benchmarks/plan_maestro_data.json` con validación de confianza.

## Inputs Requeridos
- region: str - Código de región (eje_cafetero, caribe, antioquia, default)
- rooms: int - Número de habitaciones (para segmento)
- user_provided_adr: float|null - ADR proporcionado por usuario
- hotel_id: str - Identificador del hotel

## Regiones Soportadas
- eje_cafetero: ADR ~385k COP, Ocupación ~51%
- caribe: ADR ~880k COP, Ocupación ~68%
- antioquia: ADR ~560k COP, Ocupación ~64%
- default: Valores promedio nacionales

## Segmentos por Tamaño
- boutique_10_25: Hoteles boutique 10-25 hab
- standard_26_60: Estándar 26-60 hab
- large_60plus: Grandes 60+ hab

## Lógica de Resolución

1. **Si user_provided_adr existe**:
   - Confidence: VERIFIED (0.95)
   - Source: user_provided
   - No usar benchmark

2. **Si no hay user_provided_adr**:
   - Cargar plan_maestro_data.json
   - Buscar región (case-insensitive)
   - Si rooms <= 25: usar segmento boutique
   - Si rooms <= 60: usar segmento standard
   - Si rooms > 60: usar segmento large
   - Confidence: ESTIMATED (0.7)
   - Source: regional_v410

3. **Validación**:
   - ADR debe estar entre 100k y 5M COP
   - Ocupación entre 0.2 y 0.9
   - Si fuera de rango: marcar como CONFLICT

## Outputs
- adr_cop: float - ADR resuelto
- occupancy_rate: float - Ocupación típica regional
- region_detected: str - Región usada
- segment: str - Segmento por tamaño
- confidence: float - Nivel de confianza (0-1)
- source: str - Fuente del dato
- deviation_warning: bool - Si hay desviación significativa

## Integración con Shadow Mode
- En modo SHADOW: calcular ambos (legacy y nuevo), retornar legacy, loguear comparación
- En modo CANARY: calcular ambos, retornar nuevo si pasa validación
- En modo ACTIVE: retornar nuevo directamente
