# Checklist de Implementación — ROICR

**Plan**: ROICR
**Target**: v4.55.0
**Origen**: ROICR.md (2026-05-27)
**Actualizado**: 2026-05-27

---

## FASE-1: Semántica de Activos [Problemas #1, #3]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 1A | Crear `modules/quality/asset_semantics_validator.py` con `INVALID_MAPPINGS` + `validar_semantica_comercial()` | ✅ | Archivo existe, función ejecutable |
| 1B | Agregar `migration_target` a entries DEPRECATED/IMPLEMENTED en `modules/asset_generation/asset_catalog.py` | ✅ | `grep migration_target asset_catalog.py` retorna matches |
| 1C | Integrar validator en `PainSolutionMapper` — redirigir DEPRECATED con migration_target | ✅ | Mapper redirige sin UnmappedPainError; `semantic_status` en Solution+AssetSpec |
| 1D | Implementar narrativas dinámicas: IMPLEMENT vs AUDIT_ONLY | ✅ | Propuesta dice "Auditar y Optimizar:" para `skipped_existing` |
| 1E | Tests: `tests/test_asset_semantics_validator.py` | ✅ | 15 tests pasando (BLOCKED/IMPLEMENT/AUDIT_ONLY) |

---

## FASE-2: Gate Hardening [Problema #4]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 2A | Elevar `proposal_asset_alignment` a BLOCKING para P1 en `modules/quality/publication_gates.py` | ⬜ | Gate bloquea si P1 asset NOT_READY |
| 2B | Integrar narrativa AUDIT_ONLY del FASE-1 validator en Gate evaluation | ⬜ | WhatsApp skipped → AUDIT_ONLY, no BLOCK |
| 2C | Tests: `tests/test_proposal_asset_alignment.py` | ⬜ | `pytest tests/test_proposal_asset_alignment.py -v` |

---

## FASE-3: Pipeline Unificado + CAPEX/OPEX + Curva [Problema #2]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 3A | Actualizar `config/pricing.yaml`: value_capture_cap, operational_floor | ⬜ | YAML tiene nuevos campos |
| 3B | Refactorizar `pricing_calculator.py`: pipeline 3 pasos (Base→PainRatio→EthicalCap) | ⬜ | `calcular_precio_final()` con 3 pasos |
| 3C | Crear `modules/financial_engine/roi_formatter.py`: métricas desacopladas | ⬜ | Retorna roi_saas + valorizacion_activo_digital |
| 3D | Crear `modules/financial_engine/pillar_maturity_curve.py` | ⬜ | Curva `[0.15, 0.35, 0.60, 0.80, 0.95, 1.00]` |
| 3E | Integrar en `v4_proposal_generator.py`: tablas CAPEX/OPEX separadas | ⬜ | Propuesta tiene 2 tablas |
| 3F | Actualizar `config/scenarios.yaml` con recovery 35% | ⬜ | scenarios.yaml tiene 0.35 |
| 3G | Actualizar narrativa comercial: Pitch + 4-Pillar Maturity textos | ⬜ | Templates con Value-Capture Cap, CAPEX/OPEX, Garantía Día 55, Curva |

---

## FASE-4: Arbitraje Ético + Garantía Día 55 [Problema #5]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 4A | Crear `modules/quality/financial_coherence_validator.py` con arbitraje check | ⬜ | `fee > recovery * 0.60` → BLOCK |
| 4B | Crear `modules/analytics/guarantee_validator.py` | ⬜ | Función `validar_garantia_dia55()` ejecutable |
| 4C | Agregar comando `validate-guarantee` a `main.py` | ⬜ | `python main.py validate-guarantee --help` funciona |
| 4D | Tests: `tests/test_financial_coherence_validator.py` + `tests/test_guarantee_validator.py` | ⬜ | `pytest tests/test_guarantee_validator.py -v` |

---

## FASE-5: Fixtures + Regression Guardian + Tests [Problema #6]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 5A | Actualizar `tests/fixtures/financial_scenarios.json` con nuevos valores pipeline | ⬜ | Fixtures reflejan pipeline 3 pasos |
| 5B | Re-calibrar `v4_regression_guardian` umbrales | ⬜ | Guardian acepta nuevos rangos |
| 5C | Crear `tests/test_pricing_pipeline.py` con casos borde | ⬜ | `pytest tests/test_pricing_pipeline.py -v` |
| 5D | Ejecutar `pytest` completo — sin regresiones | ⬜ | `pytest` 100% green |

---

## FASE-7: RELEASE v4.55.0

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 7A | VERSION.yaml → 4.55.0 | ⬜ | `grep version VERSION.yaml` |
| 7B | CHANGELOG.md entrada v4.55.0 | ⬜ | Entrada existe |
| 7C | REGISTRY.md actualizado | ⬜ | Última fase = FASE-RELEASE |
| 7D | Domain primer regeneration | ⬜ | `doctor.py --regenerate-domain-primer` |
| 7E | Pre-commit pasa | ⬜ | `pre-commit run --all-files` |
| 7F | log_phase de fases 1-6 | ⬜ | REGISTRY muestra todas |
| 7G | Veredicto final en 09-documentacion | ⬜ | Documento cerrado |

---

## FASE-6: v4complete + Análisis Post-Implementación

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 6A | Ejecutar v4complete Hotel Castilla Real | ⬜ | Output files generados |
| 6B | Verificar 6 niveles de éxito | ⬜ | Todos los niveles superados |
| 6C | Análisis comparativo pre/post ROICR | ⬜ | Documentado en 09-documentacion |
| 6D | Documentar métricas finales | ⬜ | Checklist actualizado |

---

## Métricas Finales (post FASE-6)

| Métrica | Pre-ROICR | Post-ROICR |
|---------|-----------|------------|
| Pricing Castilla Real | $1,200,000 | $654,796 ⬜ |
| ROI SaaS (6m) | 0.3X | 1.28X ⬜ |
| CAPEX/OPEX | Mezclados | Desacoplados ⬜ |
| Mapper semántico | Sin validación | Validator activo ⬜ |
| Gate P1 | ADVISORY | BLOCKING ⬜ |
| Garantía Día 55 | Solo pitch | Ejecutable ⬜ |
| Tests | +2,743 | +2,743+ sin regresiones ⬜ |
