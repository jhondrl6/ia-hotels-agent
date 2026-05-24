# Checklist Maestro de Implementación — NUEVO-8 AssessmentBuilder

> **Plan:** `.opencode/plans/NUEVO-8-ASSESSMENT-BUILDER/`
> **Target:** v4.50.0
> **Última actualización:** 2026-05-30T18:47

---

## FASE N8-A: Auditoría + Diseño AssessmentPayload + Tests dataclass

|| ID | Tarea | Estado |
|----|-------|--------|
|| T1 | Verificar todos los claims del contexto contra código vivo (grep + lectura) | ⬜ |
|| T2 | Diseñar `AssessmentPayload` dataclass con campos confirmados (sin metrics, sin coherence_report) | ⬜ |
|| T3 | Escribir tests unitarios para validación de schema del dataclass | ⬜ |
|| T4 | Ejecutar tests y verificar que pasan (12+ tests) + log_phase | ⬜ |

**Estado:** ⬜ Pendiente
**Depende de:** —
**Bloquea a:** N8-B

---

## FASE N8-B: AssessmentBuilder + Migración main.py + Tests

|| ID | Tarea | Estado |
|----|-------|--------|
|| T1 | Implementar `AssessmentBuilder` con métodos fluid (with_core, with_validation, etc.) | ⬜ |
|| T2 | Migrar `main.py:2663-2754` al builder (~87 líneas → ~15 líneas) | ⬜ |
|| T3 | Escribir tests unitarios para AssessmentBuilder (construcción + validación) | ⬜ |
|| T4 | Ejecutar tests (18+ tests) + verificar que main.py compila + log_phase | ⬜ |

**Estado:** ⬜ Pendiente
**Depende de:** N8-A ✅

---

## FASE N8-C: Simplificar extractores + Eliminar campos muertos + Tests

|| ID | Tarea | Estado |
|----|-------|--------|
|| T1 | Simplificar 5 extractores multi-path a acceso directo (~129 → ~30 líneas) | ✅ |
|| T2 | Eliminar campos muertos/zombie: quality_gate_* ×3, coherence_checks/errors/warnings, critical_issues_detected, consistency_report L2838, metrics, coherence_report + simplificar hotel_url or url | ✅ |
|| T3 | Actualizar tests de integration para extractores simplificados | ✅ |
|| T4 | Ejecutar test suite completa (sin regresiones) + log_phase | ✅ |

**Estado:** ✅ Completada 2026-05-30T18:47
**Depende de:** N8-B ✅
**Tests:** 232 passed, 2 failed (pre-existentes)
**Archivos nuevos:** `tests/quality_gates/test_extractors_simplified.py` (24 tests)

---

## FASE N8-D: E2E v4complete Hotel Castilla Real

|| ID | Tarea | Estado |
|----|-------|--------|
|| T1 | Ejecutar v4complete para `https://www.hotelcastillareal.com/` (subagente, timeout=900s) | ⬜ |
|| T2 | Verificar output: coherence ≥ 0.80, 9+/11 gates, sin regresiones vs baseline | ⬜ |
|| T3 | Guardar evidencia en `evidence/N8-D/` + log_phase | ⬜ |

**Estado:** ⬜ Pendiente
**Depende de:** N8-C ✅
**⚠️ CONTIENE COMANDO LARGO (v4complete)**

---

## FASE N8-RELEASE: Documentación + Version Bump

|| ID | Tarea | Estado |
|----|-------|--------|
|| T1 | Diagnosticar estado + sync_versions.py (VERSION.yaml → AGENTS.md, README.md, etc.) | ⬜ |
|| T2 | Actualizar CHANGELOG.md + GUIA_TECNICA.md con cambios de N8-A a N8-D | ⬜ |
|| T3 | Actualizar skills/workflows afectados + SYSTEM_STATUS.md | ⬜ |
|| T4 | DOMAIN_PRIMER.md + validación final (run_all_validations.py --quick) + commit | ⬜ |

**Estado:** ⬜ Pendiente
**Depende de:** N8-D ✅

---

## Resumen

| Fase | Tareas | Comando Largo | Estado |
|------|--------|---------------|--------|
| N8-A | 4 | 0 | ⬜ Pendiente |
| N8-B | 4 | 0 | ⬜ Pendiente |
| N8-C | 4 | 0 | ✅ Completada 2026-05-30T18:47 |
| N8-D | 3 | 1 (v4complete) | ⬜ Pendiente |
| N8-RELEASE | 4 | 0 | ⬜ Pendiente |