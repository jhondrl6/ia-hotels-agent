# Documentación Post-Proyecto — Rediseño Motor Financiero

**Proyecto**: Motor de Cuantificación Financiera v2
**Fecha inicio**: 2026-04-10
**Estado**: Actualizado FASE-I+J completadas

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
|| G | `main.py` | Modificado | Integración FinancialBreakdown + E2E |
|| H | `modules/financial_engine/feature_flags.py` | Modificado | regional_adr_enabled + RolloutMode + from_env() |
|| H | `modules/financial_engine/regional_adr_resolver.py` | Nuevo | resolve(), resolve_occupancy(), get_segment_adr_table() |
|| I | `modules/financial_engine/feature_flags.py` | Modificado | validated_regions whitelist + should_use_regional_for() |
|| I | `modules/financial_engine/adr_resolution_wrapper.py` | Modificado | Usa should_use_regional_for() antes de resolver regional |
|| I | `modules/financial_engine/harness_handlers.py` | Modificado | Occupancy regional si región validada |
|| I | `main.py` | Modificado | Fallback occupancy regional (~L1630) |
|| I | `.env` | Modificado | FINANCIAL_REGIONAL_ADR_ENABLED=True + VALIDATED_REGIONS |
|| I | `tests/financial_engine/test_feature_flags.py` | Modificado | 4 tests nuevos: whitelist, should_use, disabled, from_env |
|| I | `tests/financial_engine/test_adr_resolution_wrapper.py` | Modificado | 16 fixtures fix (validated_regions) |
|| J | `modules/financial_engine/no_defaults_validator.py` | Modificado | SUSPECT_SOURCES, ValidationWarning, source_reliability |
|| J | `modules/financial_engine/calculator_v2.py` | Modificado | data_sources param, metadata con source_reliability |
|| J | `modules/commercial_documents/templates/diagnostico_v6_template.md` | Modificado | Título condicional ${financial_title_label} + asterisco |
|| J | `modules/commercial_documents/v4_diagnostic_generator.py` | Modificado | _build_financial_title_label(), placeholders condicionales |
|| J | `tests/financial_engine/test_no_defaults_source_aware.py` | Nuevo | 8 tests: suspect sources, verified, mixed, backward compat |

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
|| F | 4 | +34 | 2 | 0 |
|| G | E2E | +E2E | 1 | 0 |
|| H | 0 | +34 | 2 | 1 |
|| I | 4+16fix | +38 | 7 | 0 |
|| J | 8 | +46 | 4 | 1 |
|| **Total** | **46+16fix+E2E** | — | **24** | **3** |

---

## Sección E: Archivos Afiliados Actualizados

*(Marcar [x] cuando se actualice cada archivo)*

- [x] `CHANGELOG.md` — Entrada pendiente (al final release Ciclo 2, no por fase)
- [x] `REGISTRY.md` — Vía log_phase_completion.py (FASE-A..J ✅ 2026-04-11)
- [x] `GUIA_TECNICA.md` — Notas Ciclo 2: RegionalADR + Validator Source-Aware (2026-04-11)
- [x] `CONTRIBUTING.md` — Sin cambios de convenciones (implementación interna)
- [x] `README.md` — Promesa línea 63 vigente (no alterada por I+J)
- [x] `SYSTEM_STATUS.md` — Vía doctor.py --status (regenerado 2026-04-11)
- [ ] `.agents/workflows/README.md` — Sin skills nuevas agregadas
- [x] `VERSION.yaml` — v4.26.0 (sin bump, no es release)

---

## Sección F: Lecciones Aprendidas

### FASE-I+J (2026-04-11) — Ejecución paralela
- **Paralelismo verificado**: FASE-I y FASE-J NO comparten archivos → delegate_task paralelo exitoso (451s I, 279s J)
- **Whitelist rompe tests existentes**: 16 tests de adr_resolution_wrapper fallaron porque usaban regiones no validadas. Fix: agregar `validated_regions=("coffee_axis", "bogota", "default")` a fixtures de tests.
- **Region detection vs whitelist**: Amazilia detectada como "nacional" (no "eje_cafetero") → ADR queda en $300K legacy. Para $330K se necesita detección basada en GBP address (pendiente).
- **Backward compat crítico**: NoDefaultsValidator.validate() sin `sources` param = comportamiento idéntico. Tests verifican explícitamente.
- **log_phase_completion.py**: Cada fase necesita ejecución separada (no batch).

### FASE-G (2026-04-11)
- **has_onboarding scope**: La variable se define tarde (L1801) pero el breakdown la necesita antes. Usar `onboarding_data is not None` directamente.
- **Flag desactualizado**: El plan decía `--full-audit` pero no existe. El comando correcto es `v4complete`.
- **Patch tool pipe count**: Al reemplazar líneas de tablas markdown, el patch puede duplicar el `|` inicial. Verificar siempre.
