# Checklist: PIPELINE-FIX Implementation

**Plan:** `.opencode/plans/PIPELINE-FIX-PLAN.md`
**Creado:** 2026-05-23
**Versión objetivo:** 4.48.0

---

## FASE-PF-1: Fix Assessment Dict (Root Cause)

| # | Tarea | Estado | Archivo(s) |
|---|-------|--------|-----------|
| PF1-1 | Cargar pain_ledger.json antes del assessment builder | ⬜ | main.py (antes de L2652) |
| PF1-2 | Inyectar pain_ledger al assessment dict | ⬜ | main.py:2652-2694 |
| PF1-3 | Inyectar diagnostic_pain_ids al assessment dict | ⬜ | main.py:2652-2694 |
| PF1-4 | Inyectar proposal_pain_ids al assessment dict | ⬜ | main.py:2652-2694 |
| PF1-5 | Inyectar financial_evidence_tier al assessment dict | ⬜ | main.py:2652-2694 |
| PF1-6 | Pasar pain_ledger a proposal_gen.generate() | ⬜ | main.py:2601-2614 |
| PF1-7 | Tests: assessment dict con 4 campos nuevos | ⬜ | tests/test_pipeline_fix_assessment.py |
| PF1-8 | Tests: fallback cuando pain_ledger.json no existe | ⬜ | tests/test_pipeline_fix_assessment.py |
| PF1-9 | Tests: financial_evidence_tier no default "C" | ⬜ | tests/test_pipeline_fix_assessment.py |
| PF1-10 | run_all_validations.py --quick PASS | ⬜ | — |

## FASE-PF-2: Fix delivery_ready_percentage

| # | Tarea | Estado | Archivo(s) |
|---|-------|--------|-----------|
| PF2-1 | Cambiar fórmula a confidence_score ≥0.65 | ⬜ | v4_asset_orchestrator.py:125-132 |
| PF2-2 | Preservar campo "estimated" (backward compat) | ⬜ | v4_asset_orchestrator.py:145 |
| PF2-3 | Tests: boundary conditions (0.64, 0.65, 0.8+WARNING) | ⬜ | tests/test_pipeline_fix_delivery_ready.py |
| PF2-4 | Tests: edge case 0 assets → 0.0% | ⬜ | tests/test_pipeline_fix_delivery_ready.py |
| PF2-5 | Tests existentes de orchestrator siguen pasando | ⬜ | — |
| PF2-6 | run_all_validations.py --quick PASS | ⬜ | — |

## FASE-PF-3: v4complete Hotel Castilla Real

| # | Tarea | Estado | Resultado |
|---|-------|--------|-----------|
| PF3-1 | v4complete ejecutado (exit 0) | ⬜ | — |
| PF3-2 | Evidence copiada en evidence/FASE-PF-3-E2E/ | ⬜ | — |
| PF3-3 | V1: coverage gate = PASS | ⬜ | — |
| PF3-4 | V2: tier_c no default "C" | ⬜ | — |
| PF3-5 | V3: pain_ledger untracked = 0 | ⬜ | — |
| PF3-6 | V4: delivery_ready ≈ 91.7% | ⬜ | — |
| PF3-7 | V5: proposal_asset_matrix.json existe | ⬜ | — |
| PF3-8 | V6: coherence ≥ 0.80 | ⬜ | — |
| PF3-9 | V7: financial_evidence_tier real | ⬜ | — |
| PF3-10 | Análisis comparativo pre/post documentado | ⬜ | — |

## FASE-PF-4: Release Documentation

| # | Tarea | Estado | Archivo(s) |
|---|-------|--------|-----------|
| PF4-1 | ROADMAP: tier_c documentado | ⬜ | ROADMAP.md |
| PF4-2 | ROADMAP: tabla mapping 4→11 gates | ⬜ | ROADMAP.md |
| PF4-3 | ROADMAP: claims verificados vs PF-3 | ⬜ | ROADMAP.md |
| PF4-4 | log_phase_completion ejecutado | ⬜ | — |
| PF4-5 | CHANGELOG.md actualizado | ⬜ | CHANGELOG.md |
| PF4-6 | VERSION sync (6 archivos) | ⬜ | VERSION.yaml + 6 |
| PF4-7 | GUIA_TECNICA.md nota técnica | ⬜ | GUIA_TECNICA.md |
| PF4-8 | run_all_validations.py --quick 4/4 | ⬜ | — |
| PF4-9 | validate_document_integration PASS | ⬜ | — |
| PF4-10 | AGENTS.md versión 4.48.0 | ⬜ | AGENTS.md |

---

## Resumen

| Fase | Items | Completados |
|------|-------|-------------|
| PF-1 | 10 | 0 |
| PF-2 | 6 | 0 |
| PF-3 | 10 | 0 |
| PF-4 | 10 | 0 |
| **Total** | **36** | **0** |

**Fuera de scope (NUEVO-8):** AssessmentBuilder centralizado → sesión futura dedicada.
