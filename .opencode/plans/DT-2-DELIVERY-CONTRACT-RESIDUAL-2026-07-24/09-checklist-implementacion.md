# Checklist de Implementación — DT-2

> **Plan**: DT-2-DELIVERY-CONTRACT-RESIDUAL-2026-07-24
> **Estado**: EN CURSO
> **Versión objetivo**: v4.63.2

---

## FASE-A — Conteo README + String-vs-Enum (P-01, P-07) ✅ COMPLETADA (2026-07-25)

- [x] A-1: Fix P-01 — Recalcular conteo post-manifest en README
- [x] A-2: Fix P-07 — Unificar comparación string vs enum (L618, L721, L755)
- [x] A-3: 28 tests existentes pasan (28/28 PASSED)
- [x] Commit: `fad2170` — `fix(delivery): P-01 README count post-manifest + P-07 enum comparison`
- [x] log_phase_completion.py ejecutado
- [x] Ejecución vía: delegate_task (SUBAGENTE)

## FASE-B — Exclusión Mutua Advisory Sections (P-02) ✅ COMPLETADA (2026-07-25)

- [x] B-1: Modificar delivered_assets y estimated_assets con exclusión `not is_advisory`
- [x] B-2: Modificar filtro L618 en delivery_packager.py con exclusión advisory
- [x] B-3: 28 tests existentes pasan (28/28 PASSED, 0.69s)
- [x] Commit: `95a29e9` — `fix(delivery): P-02 advisory assets mutual exclusion in README sections`
- [x] log_phase_completion.py ejecutado
- [x] Ejecución vía: directa (main agent)

## FASE-C — Quality Report Post-Gen + G9 Dead Gate (P-03, P-05) ✅ COMPLETADA (2026-07-25)

- [x] C-1: Fix P-03 — Leer coherence_validation_post_gen.json con fallback a pre-gen
- [x] C-2: Fix P-05 — Implementar G9 proposal_asset_alignment gate (Opción 1: implementado desde proposal_asset_matrix.json)
- [x] C-3: 28 tests existentes pasan (28/28 PASSED, 0.58s)
- [x] Commit: `c94001d` — `fix(delivery): P-03 post-gen coherence score + P-05 G9 gate implemented`
- [x] log_phase_completion.py ejecutado
- [x] Ejecución vía: directa (main agent) — decisión arquitectónica Opción 1 con lectura JSON sin dependencia circular

## FASE-D — proposal_asset_matrix Path + Packaging (P-04, P-06) ⬜ PENDIENTE

- [ ] D-1: Fix P-06 — Corregir path de guardado de proposal_asset_matrix
- [ ] D-2: Fix P-04 — Unificar modelo o documentar divergencia
- [ ] D-3: 28 tests existentes pasan
- [ ] Commit: `fix(delivery): P-04 P-06 proposal_asset_matrix path fix and packaging`
- [ ] log_phase_completion.py ejecutado

## FASE-E — Tests Nuevos P-01..P-07 ⬜ PENDIENTE

- [ ] E-1: Tests P-01 (conteo README == MANIFEST)
- [ ] E-2: Tests P-02 (exclusión mutua advisory, partición disjunta)
- [ ] E-3: Tests P-03 (post-gen coherence) + P-05 (G9 evaluado)
- [ ] E-4: Tests P-06 (matrix en ZIP) + P-07 (enum)
- [ ] Total: 28 existentes + 7+ nuevos = 35+ tests pasan
- [ ] Commit: `test(delivery): 7 new contract tests for P-01 to P-07`
- [ ] log_phase_completion.py ejecutado

## FASE-F — v4complete Zi One + Análisis Post-Implementación ⬜ PENDIENTE

- [ ] F-1: v4complete ejecutado para https://zione.co/ (SUBAGENTE, timeout 900s)
- [ ] F-2: Verificación de 7 fixes contra v4complete output (matriz de verificación)
- [ ] F-3: 10-analisis-post-implementacion.md completado
- [ ] S-1: README count == MANIFEST count ✅/❌
- [ ] S-2: 0 assets en múltiples secciones ✅/❌
- [ ] S-3: Post-gen coherence score usado ✅/❌
- [ ] S-4: Matrix alineada con DeliveryContext ✅/❌
- [ ] S-5: 28+ tests pasan ✅/❌
- [ ] S-6: 7+ tests nuevos ✅/❌
- [ ] S-7: ZIP cumple S-1 y S-2 ✅/❌
- [ ] S-8: G9 evaluado realmente ✅/❌
- [ ] S-9: Matrix en ZIP ✅/❌
- [ ] Commit: `verification: DT-2 v4complete Zi One 7 fixes verified`
- [ ] log_phase_completion.py ejecutado

## FASE-RELEASE — v4.63.2 ⬜ PENDIENTE

- [ ] R-1: VERSION.yaml → 4.63.2
- [ ] R-2: CHANGELOG.md entrada consolidada [4.63.2]
- [ ] R-3: sync_versions.py ejecutado
- [ ] GUIA_TECNICA.md actualizado
- [ ] Pre-commit hook pasa
- [ ] Git tag v4.63.2 creado
- [ ] log_phase_completion.py ejecutado

---

## Progreso General

| Fase | Estado | Sesión | Fecha |
|------|--------|--------|-------|
| A | ✅ COMPLETADA | 2026-07-25 | 2026-07-25 |
| B | ✅ COMPLETADA | 2026-07-25 | 2026-07-25 |
| C | ✅ COMPLETADA | 2026-07-25 | 2026-07-25 |
| D | ⬜ PENDIENTE | — | — |
| E | ⬜ PENDIENTE | — | — |
| F | ⬜ PENDIENTE | — | — |
| RELEASE | ⬜ PENDIENTE | — | — |
