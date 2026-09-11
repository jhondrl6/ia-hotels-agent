# 06 — Checklist de Implementación: TRIBUNAL-OFFLINE-2026-09-09

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.

---

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 1 | FASE-T1 | ⚠️ Completada con reserva | 2026-09-10 | 2026-09-10 | ⚠️ sin medir | Juez + contrato de acta + integración main.py; auditada. Reserva: S-HF1 y R2.1 sin cerrar; D-T1.3 abierta |
| 2 | FASE-T2-A | ✅ Completada | 2026-09-10 | 2026-09-10 | ⚠️ sin medir | Bot 1: DiagnosisReviewer — 10 tests verdes, AC5+AC6 certificados |
| 3 | FASE-T2-B | ✅ Completada | 2026-09-10 | 2026-09-10 | ⚠️ sin medir | Bot 3: AssetReviewer — 12 tests verdes, AC7+AC8 certificados |
| 4 | FASE-T2-C | ✅ Completada | 2026-09-10 | 2026-09-10 | ⚠️ sin medir | Limpieza S-E2/S9 — NameError hoisted + presence_lookup corregido + fósil V3 cerrado |
| 5 | FASE-T4-A | ✅ Completada | 2026-09-11 | 2026-09-11 | ⚠️ sin medir | Bot 2: AlignmentReviewer — protocolo PromiseExtractor + extracción LLM + clasificación determinista + S-C4; 25 tests verdes |
| 6 | FASE-T4-B | ⬜ Pendiente | — | — | — | Bot 4: Honestidad NL |
| 7 | FASE-E2E | ⬜ Pendiente | — | — | — | v4complete Salento Real |
| 8 | FASE-VERIFY | ⬜ Pendiente | — | — | — | Certificación ACs |
| 9 | FASE-RELEASE-4.76.0 | ⬜ Pendiente | — | — | — | Cierre + archivado |

---

## Checklist por Fase

### FASE-T1 — Juez Certificador

- [x] `modules/quality_gates/tribunal/__init__.py` creado
- [x] `modules/quality_gates/tribunal/judge.py` implementado (clase `TribunalJudge`)
- [x] `modules/quality_gates/tribunal/acta_writer.py` implementado
- [x] `acta_revision.json` con clave `verdict` (AC1)
- [x] Regla de primer piso: Tier B/C → condicional (AC2)
- [x] `acta_revision.md` legible con 6 cláusulas P6 (AC3)
- [x] Integración en `main.py` junto a `delivery_quality_report` (AC4)
- [x] NO añade cuarta ruta de bloqueo (AC4)
- [x] Tests: `tests/quality_gates/tribunal/test_judge.py` verdes (13 T1 + 4 auditoría = 17; `3944 → 3961` colectados)
- [x] Tests: `tests/quality_gates/tribunal/test_acta_serialization.py` verdes
- [x] `run_all_validations.py --quick` TOTAL PASS (8/8)
- [x] Baseline pre/post en `evidence/FASE-T1/`
- [x] `log_phase_completion.py` ejecutado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `10-analisis-post-implementacion.md` actualizado (lecciones)
- [x] **D-T1.1**: `DEVOLVER-CORRECCIONES` bloquea el ZIP vía `blocks_delivery_zip` / `BLOCKING_VERDICTS`
- [x] **D-T1.2**: sin evidencia certificable no hay `APROBADO-PARA-ENTREGA` (`T1_CERTIFIABLE_CLAUSES`)
- [ ] **D-T1.3**: colisión de ID `P6.5` (primer piso del Juez vs honestidad de T4-B) — requiere decisión
- [ ] **S-HF1**: criterio de narración `total_services` decidido y documentado — ⚠️ los dos documentos de evidencia se contradicen (`alignment.promised_services_total` no existe en ningún artefacto real; el código y `baseline-pre-post.md` usan `summary.promised`) y `total_services` no aparece en ningún archivo del tribunal
- [ ] **R2.1**: corte en commit de código — `modules/quality_gates/tribunal/` y la integración en `main.py` siguen sin commitear

### FASE-T2-A — Revisor de Diagnóstico (Bot 1)

- [x] `modules/quality_gates/tribunal/diagnosis_reviewer.py` implementado
- [x] `revision_diagnostico.json` con `findings[]` (AC5)
- [x] Bot 1 marca recall vacuo (AC6, S-I1 — test-level; en corrida E2E el gate ya declara `details`, no dispara)
- [x] Tests: `tests/quality_gates/tribunal/test_diagnosis_reviewer.py` verdes (10 tests)
- [x] Test de serialización (R2.4)
- [x] `run_all_validations.py --quick` TOTAL PASS (8/8)
- [x] Baseline pre/post en `evidence/FASE-T2-A/`
- [x] `log_phase_completion.py` ejecutado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `10-analisis-post-implementacion.md` actualizado

### FASE-T2-B — Revisor de Assets (Bot 3)

- [x] `modules/quality_gates/tribunal/asset_reviewer.py` implementado
- [x] `revision_assets.json` con `coverage_by_service[]` (AC7)
- [x] Bot 3 señala `IMPLEMENTATION_ORDER.md` vacío (AC8)
- [x] Bot 3 detecta P12 (fuente catálogo estático en el `message`) como P6.3 no verificable — no por score
- [x] Tests: `tests/quality_gates/tribunal/test_asset_reviewer.py` verdes (12 tests)
- [x] Test de serialización (R2.4)
- [x] `run_all_validations.py --quick` TOTAL PASS (8/8)
- [x] Baseline pre/post en `evidence/FASE-T2-B/`
- [x] `log_phase_completion.py` ejecutado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `10-analisis-post-implementacion.md` actualizado

### FASE-T2-C — Limpieza de precondiciones heredadas (S-E2, S9)

- [x] S-E2: `site_presence_report` ya no lanza `NameError` con `generate_proposal=False` (AC15)
- [x] S-E2: bloques `presence_lookup` muertos + instanciación muerta retirados (o justificada su permanencia)
- [x] S9: test de contrato de `INVALID_MAPPINGS` verde (AC16)
- [x] S9: fósil V3 en `service_identity.py` verificado con `grep` (curado o declarado cerrado)
- [x] Tests: `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` verde (7 tests)
- [x] `run_all_validations.py --quick` TOTAL PASS
- [x] Baseline pre/post en `evidence/FASE-T2-C/`
- [x] `log_phase_completion.py` ejecutado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `10-analisis-post-implementacion.md` actualizado

### FASE-T4-A — Revisor de Alineación NL (Bot 2)

- [x] `modules/quality_gates/tribunal/llm_extractor.py` implementado (protocolo + mock)
- [x] `modules/quality_gates/tribunal/alignment_reviewer.py` implementado
- [x] `revision_alineacion.json` con `service_matrix[]` (AC9)
- [x] Promesa verbal sin matriz → `PROMESA-SIN-MATRIZ` (AC10)
- [x] S-C4: tabla assets técnicos detectada como tercera superficie
- [x] Tests con LLM mockeado verdes (25 tests: 15 llm_extractor + 10 alignment_reviewer)
- [x] Test de serialización (R2.4)
- [x] `run_all_validations.py --quick` TOTAL PASS (7/8 — Version Sync esperado, se resuelve en RELEASE)
- [x] Baseline pre/post en `evidence/FASE-T4-A/`
- [x] `log_phase_completion.py` ejecutado
- [x] `09-documentacion-post-proyecto.md` actualizado
- [x] `10-analisis-post-implementacion.md` actualizado (lecciones + DA-T4A)

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
- [ ] AC1-AC16 verificados contra output real (no solo tests)
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
- [ ] AC1-AC16 certificados en FASE-VERIFY
- [ ] NR1-NR5 sin violaciones
- [ ] Plan archivado en `Archives/` (R2.5: git mv + refs --fix + citas --update-baseline)
- [ ] `10-analisis-post-implementacion.md` completo (lecciones, decisiones, métricas)
- [ ] v4.76.0 publicada
