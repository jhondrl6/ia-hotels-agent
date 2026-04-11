# Checklist de Implementación — Rediseño Motor Financiero (Opción C)

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha inicio**: 2026-04-10
**Contexto**: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md`

---

## Progreso General

| Fase | Nombre | Estado | Archivos | Tests nuevos | Sesión |
|------|--------|--------|----------|-------------|--------|
| A | Data Structures + FinancialBreakdown | ✅ Completada | `data_structures.py` | 9 | 2026-04-10 |
| B | ScenarioCalculator por capas | ✅ Completada | `scenario_calculator.py` | 5 | 2026-04-11 |
| C | Pesos normalizados + DynamicImpact | ✅ Completada | `v4_diagnostic_generator.py` | 7 | 2026-04-11 |
| D | Scraper→ADR conexión | ✅ Completada | `adr_resolution_wrapper.py`, `main.py` | 5 | 2026-04-11 |
| E | Consumidores (proposal, coherence, asset) | ✅ Completada | 3 archivos | 4 | 2026-04-11 |
| F | Template + Evidence Tiers | ✅ Completada | `diagnostico_v6_template.md`, `v4_diagnostic_generator.py` | 9 | 2026-04-11 |
| G | Integración main.py + E2E | ⬜ Pendiente | `main.py` | E2E | — |

**Total**: 7 fases, ~27 tests nuevos + E2E

---

## Dependencias

```
A → B → E → F → G
A → C → E
A → D → G
```

**Paralelismo lógico**: B, C, D pueden ejecutarse en paralelo (no compiten por archivos).
**Restricción**: Una fase por sesión (regla del workflow).

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
- main.py orquesta todo
- Prueba con Amaziliahotel
- Verificar 4 criterios de éxito
- Git commit final

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
| 1 | FASE-A | 2026-04-10 | ✅ Completada — 9/9 tests pasan, 418 tests suite intacta |
