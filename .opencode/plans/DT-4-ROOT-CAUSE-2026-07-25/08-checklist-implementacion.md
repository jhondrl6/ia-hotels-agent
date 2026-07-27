# Checklist de Implementación — DT-4

> **Plan**: DT-4-ROOT-CAUSE-2026-07-25
> **Target**: v4.65.0
> **Hotel**: Zi One Luxury (https://zione.co/)

---

## Estado General

| Fase | Título | Estado | Sesión | Fecha | Iteraciones |
|------|--------|--------|--------|-------|-------------|
| FASE-0 | Reconciliador post-orchestrator | ✅ COMPLETADO | 2026-07-26 | 2026-07-26 | ~20 |
| FASE-1 | BUG-8: Optimista reinterpretación | ✅ COMPLETADO | 2026-07-26 | 2026-07-26 | delegate_task (21 calls, 464s) |
| FASE-2 | BUG-7: Commercial gates visibles | ✅ COMPLETADO | 2026-07-26 | 2026-07-26 | delegate_task + directa (recuperación) |
| FASE-3 | BUG-10: monthly_report alignment | ⬜ PENDIENTE | — | — | — |
| FASE-4 | N1: Renombrar gates coverage | ⬜ PENDIENTE | — | — | — |
| FASE-RELEASE | v4complete + version bump + análisis | ⬜ PENDIENTE | — | — | — |

---

## FASE-0 — Reconciliador Post-Orchestrator ✅ COMPLETADO

- [x] T1: `modules/orchestration/post_orchestrator_reconciler.py` creado
- [x] T2: `v4_asset_orchestrator.py` llama al reconciliador post-generación
- [x] T3a: `_JUSTIFIED_STATUSES` incluye `ASSET_GENERATED`
- [x] T3b: `_coverage_gate` lee `pain_ledger_resolved` con fallback
- [x] T4: `coherence_validator._check_whatsapp_verified()` consulta SitePresence
- [x] 140 tests existentes PASS (gates + coherence + orchestrator + reconciler)
- [x] git commit 73c0765

---

## FASE-1 — BUG-8: Optimista Reinterpretación ✅ COMPLETADO

- [x] T1: `_check_scenario_negative`: optimista < 0 + realista > 0 → WARNING
- [x] T2: `_check_scenario_order`: optimista < 0 < realista → PASS
- [x] T3: Tests nuevos (4 casos) + 29/29 tests PASS
- [x] git commit d93678c

---

## FASE-2 — BUG-7: Commercial Gates Visibles ✅ COMPLETADO

- [x] T1: `commercial_gates_report.json` persistido antes del raise
- [x] T2: `BLOCKED_BY_GATES.md` incluye sección commercial gates + cambia mensaje de acción
- [x] T3: Tests nuevos (5 tests: 2 persistencia + 3 BLOCKED_BY_GATES) + 34/34 commercial gate tests PASS
- [x] git commit 8794312

---

## FASE-3 — BUG-10: monthly_report Alignment ⬜ PENDIENTE

- [ ] T1: `monthly_report` removido de `PROPOSAL_SERVICE_TO_ASSET`
- [ ] T2: Tests actualizados con nuevo conteo + 100 tests existentes PASS
- [ ] git commit

---

## FASE-4 — N1: Renombrar Gates Coverage ⬜ PENDIENTE

- [ ] T1: Publication G11 `coverage` → `coverage_no_silent_drop`
- [ ] T1: Delivery G7 `coverage_gate` → `coverage_failure_rate`
- [ ] T2: Tests actualizados con nuevos nombres + 100 tests existentes PASS
- [ ] git commit

---

## FASE-RELEASE — v4complete + Version Bump + Análisis ⬜ PENDIENTE

- [ ] v4complete Zi One ejecutado (exit 0)
- [ ] `pain_ledger_resolved.json` existe en v4_audit
- [ ] `commercial_gates_report.json` existe en v4_audit
- [ ] `BLOCKED_BY_GATES.md` incluye commercial gates (si aplica)
- [ ] Coverage gate PASS (no_whatsapp_visible ya no es falso positivo)
- [ ] Matriz de verificación completada en `09-analisis-post-implementacion.md`
- [ ] VERSION.yaml: 4.65.0
- [ ] CHANGELOG.md: entrada [4.65.0]
- [ ] Pre-commit: version_consistency_checker.py PASS
- [ ] git tag v4.65.0
- [ ] `pytest --collect-only -q | tail -1` conteo real de tests
- [ ] README.md test count actualizado

---

## Criterios de Éxito Globales (DoD del Plan)

| # | Criterio | Estado |
|---|----------|--------|
| S-1 | Reconciliador creado y cableado | ✅ |
| S-2 | `ASSET_GENERATED` en `_JUSTIFIED_STATUSES` | ✅ |
| S-3 | Coverage gate lee `pain_ledger_resolved` | ✅ |
| S-4 | Coherence whatsapp_verified usa SitePresence | ✅ |
| S-5 | `pain_ledger_resolved.json` existe post-v4complete | ⬜ |
| S-6 | Optimista negativo → WARNING | ✅ |
| S-7 | `commercial_gates_report.json` existe | ✅ Código listo |
| S-8 | `BLOCKED_BY_GATES.md` menciona commercial gates | ✅ Código listo |
| S-9 | `monthly_report` excluido de alignment | ⬜ |
| S-10 | Gates renombrados sin regresión | ⬜ |
| S-11 | v4complete Zi One: coverage gate PASS | ⬜ |
| S-12 | 3104 tests totales (34 commercial gate + 5 nuevos FASE-2) | ✅ |
| S-13 | Pre-commit hooks limpios | ✅ |
