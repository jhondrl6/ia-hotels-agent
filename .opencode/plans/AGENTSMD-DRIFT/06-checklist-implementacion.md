# Checklist Maestro de Implementación — AGENTSMD-DRIFT

**Última actualización:** 2026-05-26
**Estado general:** ⏳ En ejecución (A-01a ✅, A-01b ✅, A-01c ✅, RELEASE pendiente)

---

## FASE-A-01a: Corrección one-shot AGENTS.md

**Prompt:** `05-prompt-inicio-sesion-fase-A-01a.md`
**Estado:** ✅ Completada 2026-05-26
**Depende de:** —
**Iteraciones máx:** 60

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Investigar secciones drift en AGENTS.md (L123, L168, L198, L365, L380, L418, L457, L438-456) | ✅ |
| T2 | Aplicar los 9 pasos de corrección editorial | ✅ |
| T3 | Verificar con pytest conteo real + parse de publication_gates.py | ✅ |
| T4 | log_phase_completion.py + docs cascade | ✅ |

---

## FASE-A-01b: validate_agents_md.py + integración

**Prompt:** `05-prompt-inicio-sesion-fase-A-01b.md`
**Estado:** ✅ Completada 2026-05-26
**Depende de:** FASE-A-01a ✅
**Iteraciones:** ~25 usadas de 60

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Investigar publication_gates.py estructura de gates + estructura AGENTS.md | ✅ |
| T2 | Crear scripts/validate_agents_md.py con 6 checks | ✅ |
| T3 | Test manual + verificar drift detection y tolerancia ±5% | ✅ |
| T4 | Integrar en docs/CONTRIBUTING.md §Post-Fase + log_phase_completion.py + 09-docs | ✅ |

**Nota:** 2/6 checks FAIL por drift residual en AGENTS.md (paths stale: schema_validator_v2, pain_ledger, dashboard, calibration). El script funciona correctamente — el drift debe corregirse en fase posterior.

---

## FASE-A-01c: v4complete Hotel Castilla Real

**Prompt:** `05-prompt-inicio-sesion-fase-A-01c.md`
**Estado:** ✅ Completada 2026-05-23
**Depende de:** FASE-A-01b ✅
**⚠️ CONTIENE COMANDO LARGO (v4complete ~5-10 min)**

|| # | Tarea | Estado |
|---|-------|--------|
| T1 | Ejecutar v4complete para https://www.hotelcastillareal.com/ | ✅ |
| T2 | Verificar output: coherence ≥0.80, coverage PASS, tier_c_onboarding PASS | ✅ |
| T3 | Guardar evidencia + log_phase_completion.py + análisis de ejecución | ✅ |

**Métricas obtenidas:**
- Coherence: 0.83 (≥0.80 ✅)
- Publication Gates: 9/11 PASS
- Pain Ledger: 11 entries (≥7 ✅)
- Assets: 12 generados
- Human checklist: 5 items (≤10 ✅)
- G8 WARNING: 2 assets below confidence threshold (no-bloqueante)

---

## FASE-RELEASE-4.49.0: Cierre documental

**Prompt:** `05-prompt-inicio-sesion-fase-RELEASE.md`
**Estado:** ⬜ Pendiente
**Depende de:** FASE-A-01a ✅, FASE-A-01b ✅, FASE-A-01c ✅

| # | Tarea | Estado |
|---|-------|--------|
| T1 | Diagnóstico inicial + sync_versions (VERSION → 6 archivos) | ⬜ |
| T2 | CHANGELOG.md + docs/GUIA_TECNICA.md | ⬜ |
| T3 | Skills/workflows + SYSTEM_STATUS.md | ⬜ |
| T4 | DOMAIN_PRIMER + symlink + run_all_validations.py --quick + commit | ⬜ |
