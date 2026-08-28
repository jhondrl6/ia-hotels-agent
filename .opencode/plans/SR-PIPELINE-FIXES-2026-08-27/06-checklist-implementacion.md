# Checklist de Implementación — SR-PIPELINE-FIXES-2026-08-27

> Actualizar al cierre de CADA fase (plantilla del executor §3). Fuente de estado: `dependencias-fases.md` §2.

## Estado Global

| Fase | Estado | Fecha | Sesión | Iteraciones | delegate_task |
|------|--------|-------|--------|-------------|---------------|
| Preparación | ✅ COMPLETADA | 2026-08-27 | orquestación | ~20 | NO |
| FASE-SR-A | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 1) | ~30 | NO |
| FASE-SR-B | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 2) | ~35 | NO |
| FASE-SR-C | ✅ COMPLETADA | 2026-08-28 | agente (Sesión 3) | ~45 | NO |
| FASE-SR-D | ⏳ PENDIENTE | — | — | — | NO |
| FASE-SR-E | ⏳ PENDIENTE | — | — | — | NO |
| FASE-SR-F | ⏳ PENDIENTE | — | — | — | NO |
| FASE-SR-G | ⏳ PENDIENTE | — | — | — | NO |
| FASE-SR-H | ⏳ PENDIENTE | — | — | — | SÍ (v4complete) |
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
- [ ] URL canónica vía `_normalize_url()` como primer paso en v4complete + onboard + execute + validate-guarantee
- [ ] `target_id` construido desde URL normalizada; URL original solo para scraping
- [ ] `_detect_region_from_url` sigue funcionando con URL normalizada (test)
- [ ] Tests anti-fragmentación (UTM ≡ limpia ≡ mismo id) pasan
- [ ] `log_phase_completion.py --fase FASE-SR-D` (SIN --release) + docs post-fase

### FASE-SR-E — Falso negativo schema + contabilización única (rediseñada 2026-08-28)
- [ ] Bug del parser reproducido con test rojo: JSON-LD formato ARRAY → AttributeError tragado → 0 schemas falsos
- [ ] `rich_results_client` soporta arrays JSON-LD; bloque corrupto no invalida los demás
- [ ] `SchemaAuditResult` propaga `error_message` (distinguir ausencia verificada de detección fallida)
- [ ] Fixture real Salento Real (3 bloques) → ≥ 2 schemas Hotel detectados; pain `no_hotel_schema` no generado
- [ ] `exists_with_issues` cuenta como `present_in_production` en alignment (contabilización única)
- [ ] Ausencia genuina sin GBP → sin invención (test) + fallback catálogo residual D-PF3
- [ ] `log_phase_completion.py --fase FASE-SR-E` (SIN --release) + docs post-fase

### FASE-SR-F — Varianza + PageSpeed OPS
- [ ] Hipótesis de varianza verificada contra pain_ledgers A vs C (7→5)
- [ ] Fix mínimo aplicado con test, O seguimiento documentado (decisión pre-registrada)
- [ ] Estado PageSpeed key verificado en config + instrucción OPS documentada (sin tocar secretos)
- [ ] `log_phase_completion.py --fase FASE-SR-F` (SIN --release) + docs post-fase

### FASE-SR-G — Display tier + jerga
- [ ] CG-TIER-CONSISTENCY: texto deriva el tier de la fuente financiera (no hardcode)
- [ ] CG-TECH-JARGON: lenguaje de negocio en vista gerencia
- [ ] Tests pasan
- [ ] `log_phase_completion.py --fase FASE-SR-G` (SIN --release) + docs post-fase

### FASE-SR-H — E2E v4complete Salento Real (ÚNICA corrida)
- [ ] Baseline corrida C copiado a `evidence/FASE-SR-H/baseline/` ANTES de la corrida
- [ ] Corrida ejecutada (delegate_task o terminal bg con notify) con `--output output/salentoreal_final_v4c`
- [ ] Evidencia proactiva copiada a `evidence/FASE-SR-H/` (OBLIGATORIO, antes de cualquier verificación)
- [ ] Smoke 7/7 checks OK (readiness, gate PASSED, coherencia, hotel_schema cubierto por presencia, target_id, 01/02, G9)
- [ ] `log_phase_completion.py --fase FASE-SR-H` (SIN --release) + docs post-fase

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
