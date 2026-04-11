# Documentación Post-Proyecto — Rediseño Motor Financiero

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha inicio**: 2026-04-10
**Estado**: En preparación

---

## Sección A: Módulos Nuevos / Modificados

*(Completar después de cada fase)*

| Fase | Archivo | Tipo | Descripción |
|------|---------|------|-------------|
| A | `modules/commercial_documents/data_structures.py` | Modificado | Agregado FinancialBreakdown, EvidenceTier, Scenario.monthly_loss_central | 2026-04-10 |
| A | `tests/test_financial_breakdown.py` | Nuevo | Tests de nuevas estructuras | 2026-04-10 |
| B | `modules/financial_engine/scenario_calculator.py` | Modificado | Agregado calculate_breakdown(), HotelFinancialData con adr_source/occupancy_source/channel_source | 2026-04-11 |
| B | `tests/financial_engine/test_scenario_calculator.py` | Modificado | 5 tests nuevos: breakdown OTA, layers, tier, sources, backward compat | 2026-04-11 |
| C | `modules/commercial_documents/v4_diagnostic_generator.py` | Modificado | Pesos normalizados + DynamicImpactCalculator | 2026-04-11 |
| D | `modules/financial_engine/adr_resolution_wrapper.py` | Modificado | ADRSource.WEB_SCRAPING | 2026-04-11 |
| D | `main.py` | Modificado | hotel_data → adr_resolver (scraping fallback) | 2026-04-11 |
| E | `modules/commercial_documents/v4_proposal_generator.py` | Modificado | 22 puntos max→central |
| E | `modules/validation/coherence_validator.py` | Modificado | pain usa central |
| E | `modules/asset_generation/asset_diagnostic_linker.py` | Modificado | impacto usa central |
| F | `modules/commercial_documents/templates/diagnostico_v6_template.md` | Modificado | Narrativa Comisión OTA + evidence tiers |
| F | `modules/commercial_documents/v4_diagnostic_generator.py` | Modificado | Nuevos placeholders financieros |
| G | `main.py` | Modificado | Integración FinancialBreakdown + E2E |

---

## Sección B: Problema → Solución

| Problema | Severidad | Fase que resuelve | Solución |
|----------|-----------|-------------------|----------|
| Inflación x1.2 sistemática (techo como principal) | ALTA | A, G | Valor central separado del rango |
| Pesos sin base empírica (suma hasta 150%) | ALTA | C | Normalización (siempre 100%) |
| 45% de pérdida sin explicar | ALTA | C | Pesos normalizados cubren 100% |
| Fórmula mezcla hechos + supuestos | CRÍTICA | B | FinancialBreakdown separa capas |
| Comisión OTA nunca visible | CRÍTICA | B, F | Capa 1 = comisión OTA verificable |
| Scraper precio desconectado del ADR | MEDIA | D | WEB_SCRAPING como fuente intermedia |
| Sin trazabilidad del cálculo | ALTA | A, B | data_sources + EvidenceTier |
| 22 consumidores usan monthly_loss_max | MEDIA | E | Cambio a central con fallback |

---

## Sección C: Cambios Arquitectónicos

### Antes (modelo actual)
```
ScenarioCalculator
  → monthly_loss_cop (1 número)
    → FinancialScenarios
      → Scenario(monthly_loss_max)  ← consumido como principal
        → v4_diagnostic_generator (6 puntos)
        → v4_proposal_generator (22 puntos)
        → coherence_validator (1 punto)
        → asset_linker (3 puntos)
```

### Después (modelo rediseñado)
```
ScenarioCalculator
  ├── calculate_scenarios() → FinancialScenarios (EXISTENTE, no modificado)
  └── calculate_breakdown() → FinancialBreakdown (NUEVO)
        ├── Capa 1: Comisión OTA verificable + fuente
        ├── Capa 2A: Shift savings + fuente
        ├── Capa 2B: IA revenue + fuente
        └── META: evidence_tier + disclaimer + data_sources

FinancialScenarios
  └── Scenario(monthly_loss_central)  ← consumido como principal
        → v4_diagnostic_generator (usa central, NO max)
        → v4_proposal_generator (usa central, NO max)
        → coherence_validator (usa central, NO max)
        → asset_linker (usa central, NO max)
```

---

## Sección D: Métricas Acumulativas

| Fase | Tests nuevos | Tests totales | Archivos modificados | Archivos nuevos |
|------|-------------|---------------|---------------------|----------------|
| A | 9 | +9 | 1 | 1 |
| B | 5 | +14 | 1 | 0 |
| C | 7 | +21 | 1 | 1 |
| D | 5 | +26 | 2 | 0 |
| E | 4 | +30 | 3 | 0 |
| F | 4 | +34 | 2 | 0 |
| G | E2E | +E2E | 1 | 0 |
| **Total** | **30+E2E** | — | **11** | **1** |

---

## Sección E: Archivos Afiliados Actualizados

*(Marcar [x] cuando se actualice cada archivo)*

- [ ] `CHANGELOG.md` — Entrada para el rediseño del motor financiero
- [ ] `GUIA_TECNICA.md` — Notas técnicas del nuevo FinancialBreakdown
- [ ] `CONTRIBUTING.md` — Si hay cambios en convenciones
- [ ] `REGISTRY.md` — Vía log_phase_completion.py
- [ ] `README.md` — Si la promesa línea 63 necesita actualización
- [ ] `SYSTEM_STATUS.md` — Vía doctor.py --status
- [ ] `.agents/workflows/README.md` — Si se agrega skill nueva
- [ ] `VERSION.yaml` — Si hay bump de versión

---

## Sección F: Lecciones Aprendidas

*(Completar al final del proyecto)*
