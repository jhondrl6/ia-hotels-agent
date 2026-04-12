# Checklist de Implementación — Rediseño Motor Financiero (Opción C)

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha inicio**: 2026-04-10
**Contexto**: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md`

---

## Progreso General

| Fase | Nombre | Estado | Archivos | Tests nuevos | Sesion |
|------|--------|--------|----------|-------------|--------|
| A | Data Structures + FinancialBreakdown | ✅ Completada | `data_structures.py` | 9 | 2026-04-10 |
| B | ScenarioCalculator por capas | ✅ Completada | `scenario_calculator.py` | 5 | 2026-04-11 |
| C | Pesos normalizados + DynamicImpact | ✅ Completada | `v4_diagnostic_generator.py` | 7 | 2026-04-11 |
| D | Scraper→ADR conexión | ✅ Completada | `adr_resolution_wrapper.py`, `main.py` | 5 | 2026-04-11 |
| E | Consumidores (proposal, coherence, asset) | ✅ Completada | 3 archivos | 4 | 2026-04-11 |
| F | Template + Evidence Tiers | ✅ Completada | `diagnostico_v6_template.md`, `v4_diagnostic_generator.py` | 9 | 2026-04-11 |
| G | Integración main.py + E2E | ✅ Completada | `main.py` | E2E | 2026-04-11 |
| H | RegionalADRResolver SHADOW | ✅ Completada | `feature_flags.py`, `regional_adr_resolver.py` | 0 | 2026-04-11 |
|| I | Activar RegionalADRResolver por regiones | ✅ 2026-04-11 | `feature_flags.py`, `harness_handlers.py`, `main.py` | 4 | 2026-04-11 |
|| J | Validator source-aware + template | ✅ 2026-04-11 | `no_defaults_validator.py`, `template`, `generator` | 8 | 2026-04-11 |
|| K | Unificar camino dual + fix optimista | ✅ Completada | `main.py`, `harness_handlers.py`, `scenario_calculator.py` | 5 | 2026-04-11 |

**Total Ciclo 1**: 8 fases, ~27 tests nuevos + E2E
**Total Ciclo 2**: 3 fases, ~16 tests nuevos + E2E final

---

## Dependencias

### Ciclo 1 (COMPLETADO):
```
A → B → E → F → G
A → C → E
A → D → G
H (validacion, no activado)
```

### Ciclo 2 (PENDIENTE):
```
I + J (paralelo) → K → v4complete validacion
```

**Paralelismo**: FASE-I y FASE-J son 100% independientes → subagentes en paralelo.
**Restriccion**: Una fase por sesion (regla del workflow). K requiere I+J.

---

## Notas por Fase

### FASE-A (Fundación)
- Crea FinancialBreakdown, EvidenceTier, Scenario.monthly_loss_central
- Backward compatible: todo es Optional/default
- **Gate**: Si esta falla, las demás no pueden avanzar

### FASE-B (Motor de cálculo)
- Agrega calculate_breakdown() SIN eliminar calculate_scenarios()
- Comisión OTA = dato verificable principal
- Supuestos documentados con fuente

### FASE-C (Pesos)
- _normalize_weights() garantiza suma = 100%
- DynamicImpactCalculator como fuente alternativa
- Resuelve GAP del 45% "sin explicar"

### FASE-D (ADR)
- Scraper precio → ADR source
- Cadena: onboarding > scraping > benchmark > hardcode
- **Verificar GAP A**: scope de hotel_data en main.py

### FASE-E (Consumidores)
- 22 puntos de monthly_loss_max → central
- proposal_generator, coherence_validator, asset_linker
- Siempre con fallback a max (backward compat)

### FASE-F (Template)
- Narrativa: "Comisión OTA verificable" → escenarios
- Evidence tier en YAML header
- Disclaimer honesto por tier

### FASE-G (Integración + E2E)
- [x] main.py orquesta FinancialBreakdown + monthly_loss_central + paso a generadores
- [x] Prueba con Amaziliahotel — exit code 0
- [x] 4 criterios de éxito verificados (breakdown poblado, evidence tier C, $2.610.000 central, data_sources)
- [x] 453 tests pasados, 0 failures
- [x] Git commit final

### FASE-H (Validacion RegionalADRResolver)
- [x] RegionalADRResolver funciona en SHADOW
- [x] Caribe muestra 36.7% diff → NO promovido a ACTIVE
- [x] eje_cafetero y antioquia coherentes
- [x] resolve_occupancy() implementado
- [x] NO promovido a ACTIVE (pendiente whitelist por region)

### FASE-I (Activar RegionalADRResolver por regiones validadas)
- [x] Feature flag con whitelist de regiones (eje_cafetero, antioquia)
- [x] Caribe protegido (no usa regional)
- [x] harness_handlers usa occupancy regional
- [x] adr_resolution_wrapper usa should_use_regional_for()
- [x] 4 tests nuevos pasan + 16 tests wrapper fix (validated_regions)
- [x] REGISTRY.md actualizado via log_phase_completion.py

### FASE-J (NoDefaultsValidator source-aware + template honesto)
- [x] Validator genera warnings para fuentes sospechosas (no blocks)
- [x] source_reliability populated en calc_result metadata
- [x] Template condicional: ${financial_title_label} (verificable vs estimada)
- [x] Asterisco de estimacion + nota condicional
- [x] 8 tests nuevos pasan (backward compatible)
- [x] REGISTRY.md actualizado via log_phase_completion.py

### FASE-K (Unificar camino dual + fix optimista negativo)
- [x] Camino unico en main.py (no segundo ScenarioCalculator)
- [x] Harness handler usa FinancialCalculatorV2
- [x] Optimista negativo muestra "ganancia neta"
- [x] display_label funciona para positivo y negativo
- [x] 5 tests nuevos pasan
- [x] E2E validacion final (con I+J completos)

---

## Criterios de Éxito Globales

| # | Criterio | Cómo verificar |
|---|----------|---------------|
| 1 | Rastreable a fuente | `financial_scenarios.json` tiene `breakdown.data_sources` |
| 2 | Proporcional | Pesos de brechas suman ~100% en documento |
| 3 | Etiquetado VERIFIED/ESTIMATED | Evidence tier en YAML header del diagnóstico |
| 4 | Basado en hecho verificable | Comisión OTA ($5.4M) como dato principal |
| 5 | Promesa README línea 63 | Costo en COP rastreable + validación cruzada |

---

## Historial de Sesiones

| Sesión | Fase | Fecha | Resultado |
|--------|------|-------|-----------|
|| 1 | FASE-A | 2026-04-10 | ✅ Completada — 9/9 tests pasan, 418 tests suite intacta |
|| 7 | FASE-G | 2026-04-11 | ✅ Completada — 453 tests, E2E Amaziliahotel exit code 0, breakdown poblado |
|| 8 | FASE-I+J | 2026-04-11 | ✅ Paralelo — I: whitelist regional ADR, J: validator source-aware. 12 tests nuevos, 0 regresiones |
|| 9 | FASE-K | 2026-04-11 | ✅ Completada — Camino unico + fix optimista negativo. 5 tests nuevos, 390 total, E2E exit 0 |
