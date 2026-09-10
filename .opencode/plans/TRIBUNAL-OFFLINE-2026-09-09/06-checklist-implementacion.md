# 06 — Checklist de Implementación: TRIBUNAL-OFFLINE-2026-09-09

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.

---

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 1 | FASE-T1 | ⬜ Pendiente | — | — | — | Juez + contrato de acta |
| 2 | FASE-T2-A | ⬜ Pendiente | — | — | — | Bot 1: Diagnóstico |
| 3 | FASE-T2-B | ⬜ Pendiente | — | — | — | Bot 3: Assets |
| 4 | FASE-T4-A | ⬜ Pendiente | — | — | — | Bot 2: Alineación NL |
| 5 | FASE-T4-B | ⬜ Pendiente | — | — | — | Bot 4: Honestidad NL |
| 6 | FASE-E2E | ⬜ Pendiente | — | — | — | v4complete Salento Real |
| 7 | FASE-VERIFY | ⬜ Pendiente | — | — | — | Certificación ACs |
| 8 | FASE-RELEASE-4.76.0 | ⬜ Pendiente | — | — | — | Cierre + archivado |

---

## Checklist por Fase

### FASE-T1 — Juez Certificador

- [ ] `modules/quality_gates/tribunal/__init__.py` creado
- [ ] `modules/quality_gates/tribunal/judge.py` implementado (clase `TribunalJudge`)
- [ ] `modules/quality_gates/tribunal/acta_writer.py` implementado
- [ ] `acta_revision.json` con clave `verdict` (AC1)
- [ ] Regla de primer piso: Tier B/C → condicional (AC2)
- [ ] `acta_revision.md` legible con 6 cláusulas P6 (AC3)
- [ ] Integración en `main.py` junto a `delivery_quality_report` (AC4)
- [ ] NO añade cuarta ruta de bloqueo (AC4)
- [ ] Tests: `tests/quality_gates/tribunal/test_judge.py` verdes
- [ ] Tests: `tests/quality_gates/tribunal/test_acta_serialization.py` verdes
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post en `evidence/FASE-T1/`
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado (lecciones)
- [ ] S-HF1: criterio de narración `total_services` decidido y documentado

### FASE-T2-A — Revisor de Diagnóstico (Bot 1)

- [ ] `modules/quality_gates/tribunal/diagnosis_reviewer.py` implementado
- [ ] `revision_diagnostico.json` con `findings[]` (AC5)
- [ ] Bot 1 marca recall vacuo (AC6, S-I1 — test-level; en corrida E2E el gate ya declara `details`, no dispara)
- [ ] Tests: `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` verdes
- [ ] Test de serialización (R2.4)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post en `evidence/FASE-T2-A/`
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado

### FASE-T2-B — Revisor de Assets (Bot 3)

- [ ] `modules/quality_gates/tribunal/asset_reviewer.py` implementado
- [ ] `revision_assets.json` con `coverage_by_service[]` (AC7)
- [ ] Bot 3 señala `IMPLEMENTATION_ORDER.md` vacío (AC8)
- [ ] Bot 3 detecta P12 (fuente catálogo estático en el `message`) como P6.3 no verificable — no por score
- [ ] Tests: `tests/quality_gates/tribunal/test_asset_reviewer.py` verdes
- [ ] Test de serialización (R2.4)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post en `evidence/FASE-T2-B/`
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado

### FASE-T4-A — Revisor de Alineación NL (Bot 2)

- [ ] `modules/quality_gates/tribunal/llm_extractor.py` implementado (protocolo + mock)
- [ ] `modules/quality_gates/tribunal/alignment_reviewer.py` implementado
- [ ] `revision_alineacion.json` con `service_matrix[]` (AC9)
- [ ] Promesa verbal sin matriz → `PROMESA-SIN-MATRIZ` (AC10)
- [ ] S-C4: tabla assets técnicos detectada como tercera superficie
- [ ] Tests con LLM mockeado verdes
- [ ] Test de serialización (R2.4)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post en `evidence/FASE-T4-A/`
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado

### FASE-T4-B — Revisor de Honestidad NL (Bot 4)

- [ ] `modules/quality_gates/tribunal/honesty_reviewer.py` implementado
- [ ] `revision_honestidad.json` con `findings[]` (AC11)
- [ ] Bot 4 detecta CG-WHATSAPP-LEAD del archivo diagnóstico (AC12)
- [ ] Lee AMBOS archivos comerciales (canónico + diagnóstico)
- [ ] Tests con LLM mockeado verdes
- [ ] Test de serialización (R2.4)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] Baseline pre/post en `evidence/FASE-T4-B/`
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado

### FASE-E2E — v4complete Hotel Salento Real

- [ ] `v4complete --url https://www.hotelsalentoreal.com/` ejecutado (subagente, timeout=900)
- [ ] Protocolo de Evidencia Proactiva: artefactos copiados a `evidence/FASE-E2E/` (incluye `deliveries/`: MANIFEST, IMPLEMENTATION_ORDER, ASSETS)
- [ ] `acta_revision.json` presente en output con 6 cláusulas (AC13)
- [ ] `acta_revision.md` presente y legible
- [ ] 4 reportes de revisión presentes en `v4_audit/` (AC14)
- [ ] Veredicto coherente con tier (Tier B → condicional)
- [ ] Delta vs baseline FASE-D documentado (R2.3)
- [ ] Coherence ≥ 0.80 (NR5)
- [ ] `log_phase_completion.py` ejecutado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `10-analisis-post-implementacion.md` actualizado

### FASE-VERIFY — Certificación Formal

- [ ] Output E2E leído (`evidence/FASE-E2E/`)
- [ ] Baseline leído (`output/FASE-D_salentoreal_post_guard/`)
- [ ] AC1-AC14 verificados contra output real (no solo tests)
- [ ] Matriz de verificación completada en `10-analisis-post-implementacion.md`
- [ ] Diff antes/después documentado
- [ ] Greps residuales (strings que debieron desaparecer): 0 matches
- [ ] Mínimo 3 lecciones aprendidas registradas
- [ ] `log_phase_completion.py` ejecutado (SIN `--release`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] NO modificó código fuente

### FASE-RELEASE-4.76.0 — Cierre

- [ ] VERSION.yaml → 4.76.0
- [ ] `sync_versions.py` ejecutado (6 archivos sincronizados)
- [ ] `version_consistency_checker.py` pasa
- [ ] CHANGELOG.md entrada `[4.76.0]` con formato CONTRIBUTING
- [ ] GUIA_TECNICA.md nota técnica "Notas de Cambios v4.76.0"
- [ ] `doctor.py --status` → SYSTEM_STATUS.md regenerado
- [ ] `doctor.py --regenerate-domain-primer` ejecutado
- [ ] `doctor.py --context` ejecutado (solo RELEASE)
- [ ] Symlink `.agent/workflows` → `.agents/workflows` intacto
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] E8b: README.md audit (test count + module count + fecha)
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.76.0` ejecutado
- [ ] R2.5: Plan archivado en `Archives/` (git mv + refs --fix + citas --update-baseline + --quick)
- [ ] Commit único cierra RELEASE + archivado

---

## Cierre del plan

- [ ] Todas las fases ✅
- [ ] AC1-AC14 certificados en FASE-VERIFY
- [ ] NR1-NR5 sin violaciones
- [ ] Plan archivado en `Archives/` (R2.5: git mv + refs --fix + citas --update-baseline)
- [ ] `10-analisis-post-implementacion.md` completo (lecciones, decisiones, métricas)
- [ ] v4.76.0 publicada
