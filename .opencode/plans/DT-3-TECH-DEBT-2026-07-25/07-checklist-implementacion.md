# Checklist de Implementación — DT-3

> **Plan**: DT-3-TECH-DEBT-2026-07-25
> **Target**: v4.64.0
> **Última actualización**: 2026-07-25 (plan creado)

---

## Estado General

| Fase | Título | Estado | Sesión | Fecha | Iteraciones | delegate_task |
|------|--------|--------|--------|-------|-------------|---------------|
| FASE-0 | Fix sistémico rutas flat → per-hotel (BUG-1) | ✅ COMPLETADO | 2026-07-25 | 2026-07-25 | 1 | ✅ SUBAJENTE |
| FASE-1 | Fix G9 dual-list + status-based eval (BUG-2, BUG-3) | ✅ COMPLETADO | 2026-07-25 | 2026-07-25 | 1 | ✅ SUBAJENTE |
| FASE-2 | Unificar ProposalAssetMatrix + AlignmentReport (P-04) | ✅ COMPLETADO | 2026-07-25 | 2026-07-25 | 1 | ❌ DIRECTA |
| FASE-3 | v4complete Zi One + verificación E2E post-fix | ✅ COMPLETADO | 2026-07-25 | 2026-07-25 | 1 | ⚠️ MIXTO |
| FASE-RELEASE | Documentación + version bump v4.64.0 | ⬜ PENDIENTE | — | — | — | ✅ SUBAJENTE |

---

## FASE-0 — Fix sistémico rutas flat → per-hotel (BUG-1)

- [x] T1: Crear helper `_get_pipeline_path()` en main.py (~L2560)
- [x] T2: Corregir pain_ledger.json path (L2650)
- [x] T3: Corregir coherence_validation paths (L2571-2572)
- [x] T4: Auditar TODOS los JSON reads en main.py (grep rutas flat residuales)
- [x] Post: log_phase_completion.py ejecutado
- [x] Evidencia: `git diff --stat` muestra solo main.py

---

## FASE-1 — Fix G9 dual-list + status-based eval (BUG-2, BUG-3)

- [x] T1: Crear BLOCKING_GATE_NAMES constante y usarla en L253 + L257
- [x] T2: Implementar _is_service_aligned() helper (LINKED/NO_BREACH=True, resto=False)
- [x] T3: actionable_services excluye NO_BREACH; passed condition actualizada
- [x] Post: log_phase_completion.py ejecutado
- [x] Evidencia: grep "proposal_asset_alignment" solo en BLOCKING_GATE_NAMES

---

## FASE-2 — Unificar ProposalAssetMatrix + AlignmentReport (P-04) ⚠️ MAYOR COMPLEJIDAD

- [x] T1: Diseñar AssetAlignmentMatrix con AlignmentStatus enum + taxonomía unificada
- [x] T2: Implementar build(delivery_context, pain_ledger) → AssetAlignmentMatrix
- [x] T3: Migrar consumidores (G9, main.py, publication_gates.py, v4_proposal_generator.py)
- [x] T4: Verificar 86 tests existentes PASS + agregar nuevos tests (14 nuevos, 86/86 PASS)
- [x] Post: log_phase_completion.py ejecutado
- [x] Evidencia: grep "AssetAlignmentMatrix" en delivery_quality_report.py confirmado; grep "ProposalAssetMatrix\|AlignmentReport" solo ProposalAssetMatrixEntry

---

## FASE-3 — v4complete Zi One + verificación E2E post-fix ⚠️ COMANDO LARGO

- [x] T1: Ejecutar v4complete para https://zione.co/ (timeout=900s, delegate_task) — Exit 0, ~2 min runtime
- [x] T2: Capturar evidencia (pain_ledger.json, proposal_asset_matrix.json, delivery_quality_report.json, coherence_validation.json)
- [x] T3: Verificar matriz de bugs: BUG-1 ✅ (9 entries), BUG-2 ✅ (solo blocking), BUG-3 ✅ (NO_BREACH no bloquea), BUG-4 ✅ (AssetAlignmentMatrix), P-06 ✅ (per-hotel). P-01/P-02 ⚠️ no verificables (ZIP no generado — delivery bloqueado por coverage gate). Hallazgo: discrepancia delivery_quality_report vs gate_report en G9 (documentada, no regresión DT-3)
- [x] Post: log_phase_completion.py ejecutado
- [x] Evidencia: 4 archivos copiados a evidence/; delivery bloqueado por coverage gate (no_whatsapp_visible uncovered) — legítimo, no falso positivo

---

## FASE-RELEASE — Documentación + version bump v4.64.0

- [ ] T1: VERSION.yaml → 4.64.0 + sync_versions.py
- [ ] T2: CHANGELOG.md [4.64.0] + GUIA_TECNICA.md nota
- [ ] T3: git commit + git tag -a v4.64.0
- [ ] T4: version_consistency_checker.py + run_all_validations.py --quick + README.md audit
- [ ] Post: log_phase_completion.py --force-skip-docs ejecutado
- [ ] Evidencia: tag created, pre-commit PASS

---

## DoD Cross-Cutting (Post-RELEASE)

- [ ] S-1: 3 rutas flat → per-hotel corregidas
- [ ] S-2: _get_pipeline_path() creado y usado
- [x] S-3: pain_ledger 9 entries para Zi One
- [x] S-4: G1 coherence sync funcional
- [x] S-5: G9 no en warning_gates si está en blocking_gates
- [x] S-6: G9 evalúa status (NO_BREACH=skip)
- [x] S-7: AssetAlignmentMatrix reemplaza ProposalAssetMatrix + AlignmentReport
- [x] S-8: G9 consume AssetAlignmentMatrix
- [x] S-9: 42 tests existentes PASS
- [x] S-10: Tests nuevos para contrato unificado
- [ ] S-11: ZIP generado para Zi One
- [ ] S-12: P-01, P-02, P-06 verificados en ZIP
- [x] S-13: v4complete post-fix: G9 PASS o WARNING legítimo
- [ ] S-14: VERSION.yaml 4.64.0, CHANGELOG, tag creado
