# Checklist Maestro — ADVISORY-WARNINGS (v4.47.0)

**Plan:** IA-Readiness Advisory Warnings
**Creado:** 2026-05-16
**Versión objetivo:** 4.47.0

---

## Estado General

| Fase | Estado | Inicio | Fin | Iteraciones | Observaciones |
|------|--------|--------|-----|-------------|---------------|
| FASE-A | ✅ Completada | 2026-05-16 | 2026-05-16 | — | Implementar advisory warnings + tests |
| FASE-B | ✅ Completada | 2026-05-16 | 2026-05-16 | — | v4complete Hotel Castilla Real + verificación |
| FASE-RELEASE-4.47.0 | 🔒 Bloqueada | — | — | — | Requiere FASE-A ✅ + FASE-B ✅ |
| **TOTAL** | **0/3** | | | | |

---

## FASE-A: Implementar Advisory Warnings

| ID | Tarea | Estado |
|----|-------|--------|
| T1 | Investigar código existente (puntos de inserción) | ⬜ |
| T2 | Implementar Cambio 1: alerta en diagnóstico | ⬜ |
| T3 | Implementar Cambio 2: advisory_warnings en delivery_quality_report | ⬜ |
| T4 | Tests: 6 tests nuevos | ⬜ |
| — | `log_phase_completion.py --fase FASE-A` | ⬜ |
| — | `run_all_validations.py --quick` pasa 4/4 | ⬜ |
| — | Actualizar `09-documentacion-post-proyecto.md` | ⬜ |
| — | Actualizar `dependencias-fases.md` | ⬜ |

---

## FASE-B: v4complete + Verificación

|| ID | Tarea | Estado |
||----|-------|--------|
|| T1 | Ejecutar v4complete para Hotel Castilla Real | ✅ |
|| T2 | Verificar advisory warning en DIAGNOSTICO.md | ✅ |
|| T3 | Verificar advisory_warnings en delivery_quality_report.json | ✅ |
|| T4 | Análisis de ejecución en evidence/fase-B/analysis.md | ✅ |
|| — | Evidencia copiada a evidence/fase-B/ | ✅ |
|| — | `log_phase_completion.py --fase FASE-B` | ✅ |
|| — | Actualizar `09-documentacion-post-proyecto.md` | ✅ |
|| — | Actualizar `dependencias-fases.md` | ✅ |

---

## FASE-RELEASE-4.47.0: Cierre Documental

| ID | Tarea | Estado |
|----|-------|--------|
| E1 | Diagnóstico inicial (version_consistency + doctor) | ⬜ |
| E2 | sync_versions.py | ⬜ |
| E3 | CHANGELOG.md entrada [4.47.0] | ⬜ |
| E4 | GUIA_TECNICA.md nota técnica v4.47.0 | ⬜ |
| E5 | Skills/workflows verificados | ⬜ |
| E6 | SYSTEM_STATUS.md regenerado | ⬜ |
| E7 | DOMAIN_PRIMER.md regenerado + context check | ⬜ |
| E8 | Validación final 4/4 + git diff | ⬜ |
| — | `log_phase_completion.py --fase FASE-RELEASE-4.47.0` | ⬜ |
| — | Commit: `v4.47.0: ADVISORY-WARNINGS` | ⬜ |

---

## Métricas del Proyecto

| Métrica | Objetivo | Actual |
|---------|----------|--------|
| Tests nuevos | 6 | 0 |
| Tests totales (base: ~2491) | ~2497 | 2491 |
| Regresiones | 0 | — |
| Coherence score (FASE-B) | ≥ 0.80 | — |
| Archivos modificados | 3-4 | 0 |
| Archivos nuevos (tests) | 1-2 | 0 |

---

## Reglas

1. **Una fase por sesión** — no ejecutar múltiples fases en la misma sesión
2. **Máximo 60 iteraciones por fase** — si se agota, marcar INCOMPLETA y retomar
3. **FASE-RELEASE solo cuando FASE-A y FASE-B estén ✅**
4. **Cada fase ejecuta su propio `log_phase_completion.py`** — no delegar a RELEASE
