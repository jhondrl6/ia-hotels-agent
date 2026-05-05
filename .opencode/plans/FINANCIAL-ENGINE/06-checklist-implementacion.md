# Checklist Maestro de Implementación — Financial Evidence Engine

**Plan**: FINANCIAL-ENGINE v1.2.0  
**Hotel E2E**: Hotel Castilla Real (hotelcastillareal.com)  
**v4complete**: 1 ejecución (FIN-4 combinado)

---

## Estado Global

|| Total fases | Completadas | Pendientes | v4complete | Workflow |
||:-----------:|:-----------:|:----------:|:----------:|:--------:|
|| 11 | 9 | 2 | 1/1 ejecutado ✅ | v2.10.0 |

---

## Fases

### FIN-1A — Epistemic Metadata Model

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Crear `FinancialEvidence` dataclass en `financial_evidence.py` | ✅ |
| T2 | Crear `build_financial_evidence()` helper | ✅ |
| T3 | Integrar en `FinancialScenario` y `ScenarioCalculator` | ✅ |
| T4 | 8 tests en `test_financial_evidence.py` | ✅ |

**Depende de**: — | **Archivos nuevos**: `financial_evidence.py`, `test_financial_evidence.py`

### FIN-1B — NoDefaultsValidator Ampliado + Precision Tier

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Investigar `NoDefaultsValidator` actual | ✅ |
| T2 | Ampliar con `SOURCE_EPISTEMIC_MAP` | ✅ |
| T3 | Crear `PrecisionValidator` | ✅ |
| T4 | 8 tests en `test_no_defaults_precision.py` | ✅ |

**Depende de**: FIN-1A | **Archivos nuevos**: `precision_validator.py`, `test_no_defaults_precision.py`

### FIN-2A — Regional Benchmark Structured Data

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Crear `regional_adr_2026.json` | ✅ |
| T2 | Modificar `RegionalADRResolver` con metadata epistémica | ✅ |
| T3 | Actualizar nota en `plan_maestro_data.json` (si aplica) | ✅ |
| T4 | 8 tests en `test_regional_adr_2026.py` | ✅ |

**Depende de**: FIN-1B | **Archivos nuevos**: `regional_adr_2026.json`, `test_regional_adr_2026.py`

### FIN-2B — Feature Flags + Fallback Chain

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Agregar Caribe a `validated_regions` | ✅ |
| T2 | Extender `ADRResolutionResult` con campos epistémicos | ✅ |
| T3 | Propagar metadata en cadena de fallback | ✅ |
| T4 | 8 tests en `test_fallback_chain_honesto.py` | ✅ |

**Depende de**: FIN-2A | **Archivos nuevos**: `test_fallback_chain_honesto.py`
**Ejecutada**: 2026-05-04 | **Tests**: 25 nuevos + 3 regresiones corregidas

### FIN-3 — Rendering: Rangos + Advertencias + CTA ✅

| ID | Tarea | Estado |
||----|-------|--------|
| T1 | Investigar flujo de render financiero actual | ✅ |
| T2 | Modificar `v4_diagnostic_generator.py` | ✅ |
| T3 | Actualizar templates | ✅ |
| T4 | 12 tests en `test_precision_rendering.py` | ✅ |

**Depende de**: FIN-2B | **Archivos nuevos**: `test_precision_rendering.py`
**Ejecutada**: 2026-05-04 | **Tests**: 12 nuevos + 0 regresiones

### CHAN-1 — Channel Evidence Resolver ✅
**Modo**: DIRECTO (código puro, 3 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Diseñar e implementar `ChannelEvidenceResolver` | ✅ |
| T2 | Implementar lógica de inferencia (3 niveles) | ✅ |
| T3 | 8 tests en `test_channel_evidence_resolver.py` | ✅ |

**Depende de**: FIN-3 | **Archivos nuevos**: `channel_evidence_resolver.py`, `test_channel_evidence_resolver.py`
**Ejecutada**: 2026-05-04 | **Tests**: 8 nuevos + 0 regresiones

### CHAN-2 — OpportunityScorer Integration
**Modo**: DIRECTO (código puro, 4 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Extender `OpportunityScore` con metadata de canal | ⏳ |
| T2 | Agregar `channel_context` a `score_brechas()` | ⏳ |
| T3 | Integrar en `v4_diagnostic_generator` | ⏳ |
| T4 | 8 tests en `test_opportunity_scorer_channels.py` | ⏳ |

**Depende de**: CHAN-1 | **Archivos nuevos**: `test_opportunity_scorer_channels.py`

### FIN-4 — E2E Combinado (Financiero + Comercial) ⚡ ✅
**Modo**: Regla v4complete (3 tareas + 1 cmd largo — workflow v2.10.0 §Regla de Decisión v4complete)
**Ejecutado**: 2026-05-04 | Hotel Castilla Real

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Copiar evidencia pre-v4complete + ejecutar v4complete (COMANDO LARGO) | ✅ |
| T2 | Verificar criterios financieros (ADR, rangos, advertencia, CTA, sin centavos) | ✅ |
| T3 | Verificar criterios de canal (channel_context, multipliers, ranking, no-WhatsApp-hardcode) | ✅ |
| T4 | Reportar hallazgos (4 issues → FASE-FIX) | ✅ |

**Hotel**: Hotel Castilla Real — https://www.hotelcastillareal.com/  
**Depende de**: CHAN-2 | **Comando largo**: v4complete (1) ✅  
**Issues**: 4 GAPs documentados en `evidence/FIN-4/validation_report.md` → corregidos en FIN-4A/FIN-4B

### FIN-4A — PATCH: Investigación de Gaps
**Modo**: DIRECTO (código puro, 4 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

| ID | Tarea | Estado |
||----|-------|--------|
| T1 | Trazar GAP-1: ADR $300K legacy → file:line exacto | ✅ |
| T2 | Trazar GAP-2: opportunity_scores en report.json → builder location | ✅ |
| T3 | Trazar GAP-3: channel_context flow → persistence gap | ✅ |
| T4 | Trazar GAP-4: precision_tier en financial_scenarios.json | ✅ |

**Depende de**: FIN-4 | **Archivos nuevos**: `evidence/FIN-4A/gap_analysis.md`
**Ejecutada**: 2026-05-04 | **Tests**: 0 (investigación pura)

### FIN-4B — PATCH: Implementación de Integración
**Modo**: DIRECTO (código puro, 4 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

|| ID | Tarea | Estado |
||----|-------|--------|
|| T1 | Fix GAP-1: ADR regional vía feature flags | ✅ |
|| T2 | Fix GAP-2: opportunity_scores en report.json builder | ✅ |
|| T3 | Fix GAP-3: channel_context en report.json builder | ✅ |
|| T4 | Fix GAP-4: precision_tier en financial_scenarios.json builder | ✅ |

**Depende de**: FIN-4A | **Archivos nuevos**: `tests/financial_engine/test_financial_4b_integration.py`  
**Tests**: 8 nuevos | **Regresiones**: 0 | **Ejecutada**: 2026-05-04

### RELEASE — Documentación Final
**Modo**: DIRECTO (documentación pura, 5 tareas, 0 cmd largo — workflow v2.10.0 §Regla código+tests)

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Registrar 10 fases en REGISTRY.md | ⏳ |
| T2 | Version bump + sync (v4.39.0 → v4.40.0) | ⏳ |
| T3 | Actualizar CHANGELOG.md | ⏳ |
| T4 | Actualizar GUIA_TECNICA.md | ⏳ |
| T5 | Validaciones finales (run_all_validations, doctor, tests) | ⏳ |

**Depende de**: FIN-4B

---

## Métricas Acumulativas

| Métrica | Esperado |
|---------|:--------:|
| Tests nuevos | 62 (54 original + 8 FIN-4B) |
| Archivos nuevos | 13 (11 original + 2: gap_analysis.md + test_financial_4b_integration.py) |
| Archivos modificados | 7-11 (depende de hallazgos FIN-4A) |
| Fases código | 7 |
| Fase E2E | 1 |
| Fases PATCH | 2 |
| Fase documentación | 1 |
| Ejecuciones v4complete | 1 |
| Hotel E2E | Hotel Castilla Real |
