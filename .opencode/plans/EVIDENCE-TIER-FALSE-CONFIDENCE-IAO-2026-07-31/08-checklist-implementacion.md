# Checklist de Implementacion: EVIDENCE-TIER-FALSE-CONFIDENCE-IAO-2026-07-31

> **Version objetivo**: v4.68.0 | **Sesiones**: 6 | **Estado**: PLAN CORREGIDO tras auditoria 2026-07-31
> **Auditoria**: 12 hallazgos originales + 8 nuevos (NP1-NP8) detectados contra codigo vivo

---

## FASE-1 — Root Cause + Downstream Consumers Limpios ⬜ PENDIENTE

### Pre-requisito (T0/T0b): Limpiar consumers downstream ANTES de introducir B_PLUS

- [ ] **T0.1 NP1**: `hook_pdf_generator.py:509` → `valid_tiers = {"A", "B+", "B", "C"}`
- [ ] **T0.2 NP2**: `publication_gates.py:399` → `tier_message` dinamico (sin condicional falso)
- [ ] **T0.3 NP4**: `v4_diagnostic_generator.py:1043` → default `evidence_tier = "C"` (no "A")
- [ ] **T0b.1 NP3**: `tests/test_financial_breakdown.py` → assertions para `B_PLUS.disclaimer` y `B_PLUS.value`

### Tareas principales (T1-T4)

- [ ] **T1**: Agregar `B_PLUS = "B+"` al enum `EvidenceTier` + disclaimer honesto
- [ ] **T2**: Agregar `ga4_enabled`/`gsc_enabled` a `HotelFinancialData`
- [ ] **T3**: Refactorizar `_determine_evidence_tier()` + `calculate_breakdown()`
- [ ] **T4**: Wire `ga4_enabled`/`gsc_enabled` desde `main.py`
- [ ] Verificacion: Grep de `EvidenceTier` consumers no rotos
- [ ] Verificacion: Tests existentes (incluyendo test_financial_breakdown.py actualizado) pasan

## FASE-2 — Proposal + Template Honesty + PricingResolution Fix ⬜ PENDIENTE

### Pre-requisito (T0): Eliminar fallback silencioso de has_onboarding (NP5)

- [ ] **T0.1 NP5**: Eliminar `getattr(pricing_result, 'is_onboarding', False)` en `v4_proposal_generator.py:583-586`
- [ ] **T0.2 NP5**: Agregar param `has_onboarding: bool = False` a `generate()` en `v4_proposal_generator.py`
- [ ] **T0.3 NP5**: Pasar `has_onboarding=onboarding_data is not None` en `main.py:2712-2727`
- [ ] **T0.4 NP5**: Verificar NO hay otros usos de `pricing_result.is_onboarding` en codebase

### Tareas principales (T1-T4)

- [ ] **T1**: Fix `has_onboarding` hardcodeado → usa param pasado por main.py
- [ ] **T2**: Disclaimer condicional en propuesta segun tier
- [ ] **T3**: Fix relationship text hardcodeado en main.py:2099
- [ ] **T4**: Exponer `precision_tier` + actualizar leyenda Tiers (incluir B+)
- [ ] Verificacion: Propuesta no miente sobre tiers
- [ ] Verificacion: Tests existentes pasan

## FASE-3 — Quality Gate (per-hotel) + Delivery Enrichment ⬜ PENDIENTE

- [ ] **T1 NP7**: Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` con params per-hotel (`ga4_available`, `gsc_available`) — NO `os.getenv`
- [ ] **T1 NP7**: Gate agregado a `BLOCKING_GATE_IDS`
- [ ] **T2**: Integrar en `delivery_quality.py`
- [ ] **T2 NP7**: Caller en main.py pasa flags per-hotel al gate
- [ ] **T3 NP6**: Enriquecer MANIFEST.json en `modules/delivery/delivery_packager.py` (NO main.py:3038)
- [ ] Verificacion: Gate bloquea Tier A + !GA4 con params per-hotel
- [ ] Verificacion: Tests existentes pasan

## FASE-4 — Tests + Update Existing Tests ⬜ PENDIENTE

### Pre-requisito (T0): Validar tests pre-existentes compatibles con B_PLUS (NP3)

- [ ] **T0.1 NP3**: Ejecutar 5+ tests pre-existentes, documentar resultados
- [ ] **T0.2 NP3**: Aplicar fixes minimos si hay failures
- [ ] **T0.3 NP3**: Documentar cambios de semantica

### Tareas principales (T1-T4)

- [ ] **T1**: Unit tests `_determine_evidence_tier()` (6+ cases incluyendo B_PLUS con solo GA4 o solo GSC)
- [ ] **T2**: Integration test tier piping
- [ ] **T3**: Gate test `CG-EVIDENCE-TIER-CONSISTENCY` (4+ cases con params per-hotel, NO monkeypatch env vars)
- [ ] **T4**: Regression suite completa verde
- [ ] Verificacion: `pytest --collect-only` muestra nuevos tests
- [ ] Verificacion: Todos los tests pasan

## FASE-5 — v4complete Zi One + Control Sin Onboarding + Post-Implementation ⬜ PENDIENTE

### Pre-requisito (T0): Control de regresion sin onboarding (NP8)

- [ ] **T0 NP8**: delegate_task v4complete hotel_test_001 (timeout=900) — verificar Tier C sin regresion
- [ ] **T0.b NP8**: Confirmar no-regresion en default Tier C

### Tareas principales (T1-T4)

- [ ] **T1**: delegate_task v4complete Zi One Luxury (timeout=900)
- [ ] **T2**: Copiar evidencia a `evidence/FASE-5/` (Zi One + control)
- [ ] **T3**: Verificar matriz de 20 hallazgos (12 originales + 8 nuevos NP1-NP8)
- [ ] **T4**: Completar `09-analisis-post-implementacion.md`
- [ ] Verificacion: Zi One: evidence_tier = "B+" (no "A")
- [ ] Verificacion: Control hotel_test_001: evidence_tier = "C" (no regresion)
- [ ] Verificacion: 20/20 hallazgos resueltos

## FASE-RELEASE — v4.68.0 + Docs Cascade ⬜ PENDIENTE

- [ ] **T1**: VERSION.yaml → 4.68.0
- [ ] **T2**: CHANGELOG consolidado (incluir hallazgos NP1-NP8)
- [ ] **T3**: AGENTS.md + GUIA_TECNICA.md + README.md
- [ ] **T4**: Pre-commit + sync_versions + log_phase + tag v4.68.0
- [ ] Verificacion: Tag apunta al commit correcto
- [ ] Verificacion: README counts actualizados

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
| — | — | — | — | — |
