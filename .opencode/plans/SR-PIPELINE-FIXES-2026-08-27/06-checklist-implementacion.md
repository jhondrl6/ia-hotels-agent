# Checklist de Implementación — SR-PIPELINE-FIXES-2026-08-27

> Actualizar al cierre de CADA fase (plantilla del executor §3). Fuente de estado: `dependencias-fases.md` §2.

## Estado Global

| Fase | Estado | Fecha | Sesión | Iteraciones | delegate_task |
|------|--------|-------|--------|-------------|---------------|
| Preparación | ✅ COMPLETADA | 2026-08-27 | orquestación | ~20 | NO |
| FASE-SR-A | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 1) | ~30 | NO |
| FASE-SR-B | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 2) | ~35 | NO |
| FASE-SR-C | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 3) | ~45 | NO |
| FASE-SR-D | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 4) | ~40 | NO |
| FASE-SR-E | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 5) | ~45 | NO |
| FASE-SR-F | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 6) | ~55 | NO |
| FASE-SR-G | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 7) | ~45 | NO |
| FASE-SR-H | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 8) | ~20 | SÍ (v4complete) |
| FASE-SR-H2 | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 9) | ~25 | fix directo + corrida DELEGADA (D-PF7) |
| FASE-SR-VERIFY | ⏳ PENDIENTE | — | — | — | NO (§4.6) |
| FASE-RELEASE-4.73.0 | ⏳ PENDIENTE | — | — | — | opcional |

## Criterios por Fase (marcar ✅ al cerrar)

### FASE-SR-A — Helper compute_unresolved + guardián L-SR1
- [x] `AlignmentResult.compute_unresolved()` implementado y consumido por `publication_gates.py` y `delivery_quality_report.py`
- [x] Test estático AST guardián de `main.py` creado (logger = 0, py_compile OK)
- [x] Tests nuevos pasan (procesos aislados, salida a archivo); 0 regresiones en suites tocadas
- [x] `log_phase_completion.py --fase FASE-SR-A` ejecutado (SIN --release)
- [x] Documentación post-fase completa (09 + 10 + dependencias + README)

### FASE-SR-B — Unificación promesa/matriz/gate
- [x] Propuesta deriva servicios prometidos del pain_ledger + present_in_production
- [x] Gate excluye NO_BREACH del denominador de coverage_ratio (reutiliza `actionable`)
- [x] Taxonomía única de estados compartida (sin criterios paralelos — L-NC10)
- [x] Tests de contrato propuesta↔matriz↔gate pasan
- [x] Fix B7 respetado (sin promesas sin pain/presencia)
- [x] `log_phase_completion.py --fase FASE-SR-B` (SIN --release) + docs post-fase → REGISTRY.md actualizado, audit sin gaps, evidence/FASE-SR-B/ (103 tests passed = 57 gates + 46 RC1)

### FASE-SR-C — Self-healing CG-CLAIM-VS-EVIDENCE
- [x] Loop de regeneración con `suggestion` del gate + re-validación implementado (máx. 1 reintento) — `claim_self_healing.py` + closure única `_validate_diagnostic`
- [x] Persistencia → BLOCKED real (documentos retenidos) — flag `_claim_escalated` en main.py: GATE BLOCKING + BLOCKED_BY_GATES.md + ZIP abortado
- [x] Guard anti-bucle probado (MAX_REGENERATIONS=1; 2ª llamada no reescribe ni revalida — spy)
- [x] Tests del loop pasan — 20/20 nuevos + regresiones 79 (gates) / 27 (generator) / 57 (gate+guardián L-SR1), 0 fallos
- [x] `log_phase_completion.py --fase FASE-SR-C` (SIN --release) + docs post-fase → evidence/FASE-SR-C/ (quick 6/6)

### FASE-SR-D — Canonicalización target_id
- [x] URL canónica vía `_normalize_url()` como primer paso en v4complete + onboard + execute + validate-guarantee
- [x] `target_id` construido desde URL normalizada; URL original solo para scraping
- [x] `_detect_region_from_url` sigue funcionando con URL normalizada (test)
- [x] Tests anti-fragmentación (UTM ≡ limpia ≡ mismo id) pasan — 28/28 en `tests/test_target_id_canonicalization.py`
- [x] `log_phase_completion.py --fase FASE-SR-D` (SIN --release) + docs post-fase

### FASE-SR-E — Falso negativo schema + contabilización única (rediseñada 2026-08-28)
- [x] Bug del parser reproducido con test rojo: JSON-LD formato ARRAY → AttributeError tragado → 0 schemas falsos
- [x] `rich_results_client` soporta arrays JSON-LD; bloque corrupto no invalida los demás
- [x] `SchemaAuditResult` propaga `error_message` (distinguir ausencia verificada de detección fallida)
- [x] Fixture real Salento Real (3 bloques) → ≥ 2 schemas Hotel detectados; pain `no_hotel_schema` no generado
- [x] `exists_with_issues` cuenta como `present_in_production` en alignment (contabilización única)
- [x] Ausencia genuina sin GBP → sin invención (test) + fallback catálogo residual D-PF3
- [x] `log_phase_completion.py --fase FASE-SR-E` (SIN --release) + docs post-fase

### FASE-SR-F — Varianza + PageSpeed OPS
- [x] Hipótesis de varianza verificada contra pain_ledgers A vs C (7→5) — hipótesis del mapper FALSA; causa real: sondas robots/llms con query UTM medían homepage 200 (robots 1.0/robots_exists=True, llms_txt=100 falso; delta 22.222 reproducible con pesos)
- [x] Fix mínimo aplicado con test, O seguimiento documentado (decisión pre-registrada) — D-PF6=FIX: 3 sondas ancladas al origen (urlparse) en ai_crawler_auditor/v4_comprehensive/site_presence_checker; mapper verificado inocente; 15/15 tests nuevos + regresión 58, 0 fallos
- [x] Estado PageSpeed key verificado en config + instrucción OPS documentada (sin tocar secretos) — GOOGLE_PAGESPEED_API_KEY presente pero inválida/sin habilitar vs GOOGLE_MAPS_API_KEY funcional; rotación = decisión del usuario
- [x] `log_phase_completion.py --fase FASE-SR-F` (SIN --release) + docs post-fase

### FASE-SR-G — Display tier + jerga
- [x] CG-TIER-CONSISTENCY: texto deriva el tier de la fuente financiera (no hardcode) — extractor `_extract_text_tier` canónico (solo MAYÚSCULAS `[A-D][+]?` + lookahead de letra; `\b` eliminado por backtracking "B+"→"B"); fuente = `evidence_tier` del financial engine (desviación fundamentada: pricing.yaml es otra dimensión, intacto); gate intacto
- [x] CG-TECH-JARGON: lenguaje de negocio en vista gerencia — glosario único `tech_jargon_glossary.py` (detección+mapeo+patrón compartido, guardia "sin costo (fallback)"); `apply_glossary` post-render en ambos generadores (pre-validación/healing, L-SR3/L-NC10)
- [x] Tests pasan — 18 nuevos (14 glosario + 4 extractor), 147 PASSED aislados (70 gates -k + 24 docs -k + 27 diagnostic + 9 template_conditionals + 10 alignment + 7 proposal subset), 5 fallos PREEXISTENTES certificados en HEAD, 0 regresiones; greps residuos 0; quick 6/6
- [x] `log_phase_completion.py --fase FASE-SR-G` (SIN --release) + docs post-fase → evidence/FASE-SR-G/ (12 archivos: diff + logs + módulos nuevos), REGISTRY.md actualizado, documentation audit sin gaps, DOMAIN_PRIMER regenerado (25 módulos)

### FASE-SR-H — E2E v4complete Salento Real (ÚNICA corrida)
- [x] Baseline corrida C copiado a `evidence/FASE-SR-H/baseline/` ANTES de la corrida
- [x] Corrida ejecutada (delegate_task o terminal bg con notify) con `--output output/salentoreal_final_v4c` — exit 0, ~1m40s, URL canónica limpia
- [x] Evidencia proactiva copiada a `evidence/FASE-SR-H/` (OBLIGATORIO, antes de cualquier verificación) — `baseline/` + `final/` + `corrida.log` + `smoke_result.json`
- [x] Smoke 7 checks ejecutado: **5/7** — 2 fallas con causa única (`critical_recall` BLOCKED; bug latente expuesto por SR-E, post-mortem en `10-analisis` §Resumen E2E, decisión pre-VERIFY requerida)
- [x] `log_phase_completion.py --fase FASE-SR-H` (SIN --release) + docs post-fase

### FASE-SR-H2 — Hotfix critical_recall + corrida de verificación (pre-VERIFY)
- [x] T1: 4 tests de contrato escritos ANTES del fix — 2 ROJOS nuevos (extractor `test_extract_critical_recall_empty_with_audit_present` + gate `test_empty_critical_issues_with_audit_passes`, capturan el BLOCKED espurio) + 2 guards del comportamiento preservado (sin audit → None/BLOCKED, ya verdes contra código actual: pinnean el BLOCKED real, no es camino nuevo)
- [x] T2: fix `_extract_critical_recall` (lista vacía + `audit_schema` no vacío → 1.0 favorable con traza `recall_basis=audit_present_no_critical_issues` en details del gate PASSED; audit ausente → None → BLOCKED real, L-SR5) + 4 VERDES + regresión aislada 58+25+12 passed, 1 fallo PREEXISTENTE certificado contra HEAD con `git show` (`test_gate_presence_with_skipped_assets`, ejercita `_proposal_asset_alignment_gate`); grep residual: 0 consumidores de `_extract_critical_recall` fuera de publication_gates.py y sus tests
- [x] T3: corrida de verificación única D-PF7 delegada a subagente (`v4complete --url https://www.hotelsalentoreal.com/ --output output/salentoreal_final_v4c_h2`) — exit 0, ~1m50s, sin reintentos; evidencia copiada inmediatamente (`evidence/FASE-SR-H2/final/v4_complete` + `corrida.log`); smoke variante H2 (`temp/fase_sr_h2_smoke.py`, misma lógica/baseline, salida a `smoke_result_h2.json` para NO sobrescribir evidencia pre-fix de SR-H): **7/7** — READY_FOR_PUBLICATION, coherencia 0.88, unresolved 0=0, 01/02 presentes, ZIP, financiera idéntica al baseline; traza del fix en gate_report de producción (critical_recall PASSED 1.0 + `recall_basis`)
- [x] Docs post-fase (1-7) + D-PF7 registrada en `10-analisis` §Decisiones + `log_phase_completion` SIN --release (DOMAIN_PRIMER NO regenerado: es del RELEASE)

### FASE-SR-VERIFY — Certificación ACs
- [ ] AC1-AC13 verificados contra output real (matriz completa con Real/Status)
- [ ] Diff narrativo antes/después documentado (todas las zonas afectadas)
- [ ] Greps residuales = 0 matches
- [ ] ≥3 lecciones nuevas registradas en 10-analisis
- [ ] `log_phase_completion.py --fase FASE-SR-VERIFY` (SIN --release) + `run_all_validations.py --quick`

### FASE-RELEASE-4.73.0 — Cierre
- [ ] E1: version_consistency_checker + doctor sin errores
- [ ] E2: sync_versions.py ejecutado (6 archivos)
- [ ] E3: CHANGELOG `[4.73.0]` formato CONTRIBUTING (Objetivo/Cambios/Nuevos/Modificados/Tests)
- [ ] E4: GUIA_TECNICA "Notas de Cambios v4.73.0"
- [ ] E5: skills/workflows listados sin huérfanos
- [ ] E6: SYSTEM_STATUS.md regenerado
- [ ] E7: DOMAIN_PRIMER regenerado + `doctor.py --context`
- [ ] E8: symlink intacto + `run_all_validations.py --quick` TOTAL PASS
- [ ] E8b: README audit (test count vs `pytest --collect-only`, module count, fecha)
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.73.0` (marker release) + Version Sync Gate OK
