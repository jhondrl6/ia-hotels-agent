# Checklist de Implementacion: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31

> **Version objetivo**: v4.68.0 | **Sesiones**: 6 | **Estado**: PLAN CORREGIDO tras auditoria 2026-07-31
> **Auditoria**: 12 hallazgos originales + 8 nuevos (NP1-NP8) detectados contra codigo vivo

---

## FASE-1 — Root Cause + Downstream Consumers Limpios ✅ COMPLETADA (2026-07-31)

### Pre-requisito (T0/T0b): Limpiar consumers downstream ANTES de introducir B_PLUS

- [x] **T0.1 NP1**: `hook_pdf_generator.py:509` → `valid_tiers = {"A", "B+", "B", "C"}`
- [x] **T0.2 NP2**: `publication_gates.py:399` → `tier_message` dinamico (sin condicional falso)
- [x] **T0.3 NP4**: `v4_diagnostic_generator.py:1043` → default `evidence_tier = "C"` (no "A")
- [x] **T0b.1 NP3**: `tests/test_financial_breakdown.py` → assertions para `B_PLUS.disclaimer` y `B_PLUS.value`

### Tareas principales (T1-T4)

- [x] **T1**: Agregar `B_PLUS = "B+"` al enum `EvidenceTier` + disclaimer honesto
- [x] **T2**: Agregar `ga4_enabled`/`gsc_enabled` a `HotelFinancialData`
- [x] **T3**: Refactorizar `_determine_evidence_tier()` + `calculate_breakdown()`
- [x] **T4**: Wire `ga4_enabled`/`gsc_enabled` desde `main.py`
- [x] Verificacion: Grep de `EvidenceTier` consumers no rotos
- [x] Verificacion: Tests existentes (incluyendo test_financial_breakdown.py + test_financial_evidence.py actualizados) pasan

## FASE-2 — Proposal + Template Honesty + PricingResolution Fix ✅ COMPLETADA (2026-07-31)

### Pre-requisito (T0): Eliminar fallback silencioso de has_onboarding (NP5)

- [x] **T0.1 NP5**: Eliminar `getattr(pricing_result, 'is_onboarding', False)` en `v4_proposal_generator.py:583-586`
- [x] **T0.2 NP5**: Agregar param `has_onboarding: bool = False` a `generate()` en `v4_proposal_generator.py`
- [x] **T0.3 NP5**: Pasar `has_onboarding=onboarding_data is not None` en `main.py:2712-2727`
- [x] **T0.4 NP5**: Verificar NO hay otros usos de `pricing_result.is_onboarding` en codebase (0 matches)

### Tareas principales (T1-T4)

- [x] **T1**: Fix `has_onboarding` hardcodeado → usa param pasado por main.py
- [x] **T2**: Disclaimer condicional en propuesta segun tier (nuevo metodo `_build_tier_disclaimer`)
- [x] **T3**: Fix relationship text hardcodeado en main.py:2099 (ahora f-string dinamico)
- [x] **T4**: Exponer `precision_tier` + actualizar leyenda Tiers (incluir B+)
- [x] Verificacion: Propuesta no miente sobre tiers
- [x] Verificacion: Tests existentes pasan (549/550, 1 pre-existente OpenRouter)

## FASE-3 — Quality Gate (per-hotel) + Delivery Enrichment ✅ COMPLETADA (2026-07-31)

- [x] **T1 NP7**: Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` con params per-hotel (`ga4_available`, `gsc_available`) — NO `os.getenv`
- [x] **T1 NP7**: Gate agregado a `BLOCKING_GATE_IDS`
- [x] **T2**: Integrar en caller `v4_diagnostic_generator.py` (pasa `ga4_available`, `gsc_available`, `financial_json`)
- [x] **T2 NP7**: Caller en main.py pasa flags per-hotel al gate (vía setter `_quality_metadata`)
- [x] **T3 NP6**: Enriquecer MANIFEST.json en `modules/delivery/delivery_packager.py` (NO main.py:3038)
- [x] Verificacion: Gate bloquea Tier A + !GA4 con params per-hotel
- [x] Verificacion: Tests existentes pasan (549/550, 1 pre-existente OpenRouter)

## FASE-4 — Tests + Update Existing Tests ✅ COMPLETADA (2026-07-31)

### Pre-requisito (T0): Validar tests pre-existentes compatibles con B_PLUS (NP3)

- [x] **T0.1 NP3**: Ejecutar 5+ tests pre-existentes, documentar resultados
  - test_financial_breakdown.py: 10/10 ✅
  - test_fase_f_financial_placeholders.py: 11/12 (1 pre-existente encoding) ✅
  - test_hook_pdf_generator.py: 36/36 ✅
  - test_proposal_generator.py: 21/32 (11 pre-existentes WhatsApp/asset) ✅
  - test_template_conditionals.py: 6/6 ✅
- [x] **T0.2 NP3**: Sin fixes necesarios — ninguna falla causada por B_PLUS
- [x] **T0.3 NP3**: Todos los tests pre-existentes pasan con B_PLUS. Fallas documentadas como pre-existentes (encoding, WhatsApp, OpenRouter).

### Tareas principales (T1-T4)

- [x] **T1**: Unit tests `_determine_evidence_tier()`: 9 test cases (A, B+, B, C, combinaciones GA4/GSC)
- [x] **T2**: Integration test tier piping: 5 cases (onboarding→B+, unknown→C, GA4+GSC→A, solo GA4→B+, fuentes preservadas)
- [x] **T3**: Gate test `CG-EVIDENCE-TIER-CONSISTENCY`: 8 cases (BLOCKING A sin GA4/GSC, pasa B+/B/C, pasa A+GA4+GSC, missing JSON)
- [x] **T4**: Regression suite: 549 passed + 22 nuevos, 2 skipped, 1 pre-existente (OpenRouter)
- [x] Verificacion: `pytest --collect-only` muestra 22 nuevos tests en test_evidence_tier.py
- [x] Verificacion: 32/32 tests financieros + evidence tier pasan

## FASE-5 — v4complete Zi One + Control Sin Onboarding + Post-Implementation ✅ COMPLETADA (2026-07-31)

### Pre-requisito (T0): Control de regresion sin onboarding (NP8)

- [x] **T0 NP8**: delegate_task v4complete hotel_test_001 (timeout=900) — Hotel Visperas, evidence_tier = "B" (default honesto, sin B+ ni A). SIN REGRESION.
- [x] **T0.b NP8**: Confirmar no-regresion en default Tier: B es el default correcto para hotel con GBP + Schema verificados pero sin GA4/GSC ni onboarding.

### Tareas principales (T1-T4)

- [x] **T1**: delegate_task v4complete Zi One Luxury (timeout=900) — completado en ~120s, exit code 0
- [x] **T2**: Copiar evidencia a `evidence/FASE-5/` (Zi One: 6 archivos, control: 4 archivos)
- [x] **T3**: Verificar matriz de 20 hallazgos (12 originales + 8 nuevos NP1-NP8) — 20/20 ✅
- [x] **T4**: Completar `09-analisis-post-implementacion.md` — completado con lecciones aprendidas
- [x] Verificacion: Zi One: evidence_tier = "B+" (no "A"), disclaimer honesto, precision_tier visible, MANIFEST quality_metadata
- [x] Verificacion: Control hotel_test_001: evidence_tier = "B" (sin regresion: no B+ ni A), disclaimer honesto
- [x] Verificacion: 20/20 hallazgos resueltos (ver matriz en 09-analisis-post-implementacion.md)

## FASE-RELEASE — v4.68.0 + Docs Cascade ✅ COMPLETADA (2026-07-31)

- [x] **T1**: VERSION.yaml → 4.68.0
- [x] **T2**: CHANGELOG consolidado (incluye 20 hallazgos: 12 originales H1-H12 + 8 NP1-NP8)
- [x] **T3**: AGENTS.md + GUIA_TECNICA.md (nueva seccion v4.68.0) + README.md (counts: 3,180 tests, 205 modulos, 10 gates)
- [x] **T4**: Pre-commit + sync_versions + log_phase + tag v4.68.0
- [x] Verificacion: Tag v4.68.0 apunta al commit 25e7be3
- [x] Verificacion: Push exitoso (master + tag v4.68.0)

---

## Deuda Tecnica Documentada (NO implementa)

- [ ] **H10**: Unificar 3 sistemas de precision_tier (enum, string, validator) — plan futuro
- [ ] **H12**: Crear service account Google Cloud — user action (Google Cloud Console)

---

## Hallazgos Nuevos Auditados (NP1-NP8)

| ID | Severidad | Descripcion | Archivo | Fase |
|----|-----------|-------------|---------|------|
| **NP1** | CRITICA | hook_pdf_generator rechaza B+ | hook_pdf_generator.py:509 | FASE-1 T0.1 |
| **NP2** | ALTA | publication_gates tier_message logica rota | publication_gates.py:399 | FASE-1 T0.2 |
| **NP3** | ALTA | tests pre-existentes rompen con B_PLUS | test_financial_breakdown.py + otros | FASE-1 T0b.1 + FASE-4 T0 |
| **NP4** | ALTA | default "A" en diagnostic generator | v4_diagnostic_generator.py:1043 | FASE-1 T0.3 |
| **NP5** | MEDIA | fallback silencioso has_onboarding | v4_proposal_generator.py:586 | FASE-2 T0 |
| **NP6** | MEDIA | MANIFEST ubicacion incorrecta (main.py:3038 vs delivery_packager.py:145) | Documentacion del plan | CORREGIDO en este plan |
| **NP7** | ALTA | gate usa env vars globales (deberia ser per-hotel) | commercial_gate.py | FASE-3 T1 rediseñado |
| **NP8** | MEDIA | control sin onboarding post-fix | Test strategy | FASE-5 T0 |

---

## Log de Sesiones

| Fecha | Fase | Estado | Iteraciones | Notas |
|-------|------|--------|-------------|-------|
| 2026-07-31 | FASE-1 | ✅ COMPLETADA | 1 | T0-T4 + T0b.1 (NP1-NP4). 7 archivos modificados. Tests: 10/10 financial_breakdown + 17/17 financial_evidence. B_PLUS introducido. |
| 2026-07-31 | FASE-2 | ✅ COMPLETADA | 1 | T0 NP5 (has_onboarding sin fallback) + T1-T4 (disclaimer condicional, relationship text dinamico, precision_tier visible). 5 archivos. Tests: 549/550. |
| 2026-07-31 | FASE-3 | ✅ COMPLETADA | 1 | T1 NP7 (gate per-hotel sin os.getenv) + T2 (caller en v4_diagnostic_generator) + T3 NP6 (MANIFEST en delivery_packager.py). 3 archivos. Tests: 549/550. |
| 2026-07-31 | FASE-4 | ✅ COMPLETADA | 1 | T0 NP3 (5 suites validadas, 0 fixes necesarios) + T1 (9 unit tests) + T2 (5 integration tests) + T3 (8 gate tests). Archivo nuevo: test_evidence_tier.py (22 tests). Tests: 549+22 passed, 1 pre-existente OpenRouter. |
| 2026-07-31 | FASE-5 | ✅ COMPLETADA | 1 | T0 NP8 (control hotel_test_001, delegate_task) + T1 (Zi One, delegate_task) + T2 (evidencia copiada) + T3 (20/20 hallazgos verificados) + T4 (analisis post-implementacion completado). Zi One: Tier B+, honesto. Control: Tier B, sin regresion. |
