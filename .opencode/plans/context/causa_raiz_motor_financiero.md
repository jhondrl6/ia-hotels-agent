# Investigacion: Causa Raiz — Motor Financiero Produce Datos No Verificables

**Fecha**: 2026-04-11
**Trigger**: Analisis del diagnostico generado para Amaziliahotel (01_DIAGNOSTICO_Y_OPORTUNIDAD_20260411_120128.md)
**Alcance**: 3 fallas interrelacionadas en el motor financiero

---

## Hallazgos Principales

### F1: NoDefaultsValidator tiene definicion insuficiente de "default"

**Archivo**: `modules/financial_engine/no_defaults_validator.py`

El validador solo detecta `valor == 0`, `valor == None`, `valor == ""` (lineas 173-191).
NO detecta valores fallback disfrazados como datos reales:
- ADR = $300,000 (viene de `regional_adr_resolver.py:98` fallback, no de datos del hotel)
- occupancy = 0.50 (hardcodeado en `harness_handlers.py:88`)
- direct_channel = 0.20 (hardcodeado en `harness_handlers.py:89`)

Todos pasan la validacion porque son != 0 y != None.

**Evidencia**: `financial_scenarios.json` muestra:
```json
"data_sources": {
  "adr": "legacy_hardcode",
  "occupancy": "default",
  "direct_channel": "default"
}
```
El sistema SABE que son defaults pero el validador no los detecta.

### F2: RegionalADRResolver existe pero esta DESACTIVADO

**Archivo**: `modules/financial_engine/feature_flags.py`

`regional_adr_enabled: bool = False` (linea 30).

FASE-H (completada) dejo el resolver en SHADOW por anomalia del Caribe (36.7% diff).
Pero eje_cafetero ($330K) y antioquia ($280K) SON coherentes con legacy $300K.

**Impacto**: Para Amazilia (eje_cafetero):
- ADR actual: $300,000 (legacy) vs $330,000 (regional) = 10% subestimado
- Occupancy actual: 50% (default) vs 52% (regional) = 4% subestimado
- Comision OTA real estimada: $5.94M (no $5.4M)

### F3: Camino dual — FinancialCalculatorV2 + ScenarioCalculator calculan lo mismo

**Archivo**: `main.py` lineas 1650-1733

Linea 1651: `FinancialCalculatorV2().calculate(financial_input)` — calcula escenarios CON validacion
Linea 1721-1733: `ScenarioCalculator().calculate_breakdown()` — recalcula breakdown SIN validacion

El breakdown de trazabilidad (evidence tier, data sources) viene del SEGUNDO camino que bypasa el validador.

**Consecuencia**: La capa de trazabilidad (FASE-A..G) funciona pero opera en paralelo al motor validado, no integrada a el.

### Bug adicional: Escenario Optimista negativo

**Archivo**: `modules/financial_engine/scenario_calculator.py` lineas 248-304

```
Optimista: OTA loss $6.75M - savings $1.35M - IA revenue $4.5M = -$189,000
```

El campo `monthly_loss_cop` con valor negativo indica GANANCIA, no perdida. El nombre es semanticamente incorrecto. La UI lo muestra como "-$189,000 COP/mes" en tabla de "Escenarios de Recuperacion", lo cual confunde.

---

## Cadena de Procedencia (verificada contra codigo)

```
main.py:1410  → _detect_region_from_url(args.url)  → "eje_cafetero"
main.py:1620  → resolve_adr_with_shadow(region, rooms) → $300,000 (legacy, NO regional)
main.py:1630  → occupancy_rate = 0.50 (hardcode, main.py obtiene de onboarding_data o default)
main.py:1651  → FinancialCalculatorV2().calculate({rooms:10, adr:300000, occ:0.50, direct:0.20})
main.py:1659  → calc_result = calc_v2.calculate(financial_input)
  → NoDefaultsValidator.validate() → PASA (todos != 0)
  → ScenarioCalculator.calculate_scenarios() → {conservador:$5.07M, realista:$2.61M, optimista:-$189K}
main.py:1721  → ScenarioCalculator().calculate_breakdown() → FinancialBreakdown con evidence_tier=C
```

---

## Plan de Accion (3 fases)

| Fase | Objetivo | Impacto | Esfuerzo | Risk |
|------|----------|---------|----------|------|
| FASE-I | Activar RegionalADRResolver por regiones validadas | ALTO | BAJO | BAJO |
| FASE-J | NoDefaultsValidator source-aware + template honesto | MEDIO | MEDIO | BAJO |
| FASE-K | Unificar camino dual + fix optimista negativo | MEDIO | MEDIO | MEDIO |

FASE-I y FASE-J son INDEPENDIENTES (no comparten archivos) → paralelizables via subagentes.
FASE-K depende de ambas (requiere que I y J esten completas).

---

## Diagrama de Dependencias

```
FASE-I ──────┐
             ├──→ FASE-K → v4complete validacion final
FASE-J ──────┘
```

---

## Conflictos de Archivos

| Archivo | FASE-I | FASE-J | FASE-K | Resolucion |
|---------|--------|--------|--------|------------|
| feature_flags.py | TOCA | - | - | Solo I |
| harness_handlers.py | TOCA (datos regionales) | - | TOCA (usar calc_v2) | K va despues de I |
| main.py (L1600-1650) | TOCA | - | - | Solo I |
| main.py (L1720-1733) | - | - | TOCA | Solo K |
| no_defaults_validator.py | - | TOCA | - | Solo J |
| calculator_v2.py | - | TOCA | - | Solo J |
| diagnostico_v6_template.md | - | TOCA | - | Solo J |
| v4_diagnostic_generator.py | - | TOCA | - | Solo J |
| scenario_calculator.py | - | - | TOCA | Solo K |
