# Checklist de Implementación — Brecha Architectural Fix

**Proyecto**: Eliminar gap entre diagnóstico y propuesta V6
**Versión Target**: v4.26.0
**Creado**: 2026-04-10

---

## Progreso General

| Fase | Descripción | Estado | Tests | Dependencias |
|------|-------------|--------|-------|--------------|
|| FASE-F | Phantom Cost Fix + Dead Code | ✅ Completada | 5/5 pasan | Ninguna |
||| FASE-G | Dual Source Conflict Resolution | ✅ Completada | 5/5 pasan | FASE-F ||
|| FASE-H | Performance Cache + Cleanup | ✅ Completada | 4/4 pasan | FASE-G ||
|| FASE-I | data_structures Deduplication | ✅ Completada | 4/4 pasan | FASE-H |
| FASE-J | E2E Validation + Release | 🔲 Pendiente | E2E test | FASE-F/G/H/I |

**Total tests nuevos esperados**: 18
**Release**: FASE-RELEASE-4.26.0 (al completar FASE-J)

---

## FASE-F: Phantom Cost Fix + Dead Code Removal ✅ COMPLETADA (2026-04-10)

- [x] Tarea 1: Distribución fija 40/30/20/10 eliminada del proposal generator
  - [x] Líneas 538-546 reemplazadas con lógica dinámica (`_build_brecha_data`)
  - [x] Guard contra top_problems=None implementado (`or []`)
- [x] Tarea 2: Tests de regresión
  - [x] test_no_phantom_costs_with_one_problem — PASSED
  - [x] test_no_phantom_costs_with_zero_problems — PASSED
  - [x] test_no_phantom_costs_with_none_problems — PASSED
  - [x] test_costs_distributed_when_4_problems — PASSED
  - [x] test_empty_name_for_missing_brechas — PASSED
- [x] Tarea 3: Validación
  - [x] run_all_validations.py --quick: 3/4 pasan (version sync preexistente)
  - [x] 0 regresiones en tests existentes
- [x] Post-ejecución: dependencias, docs, log_phase_completion.py

---

## FASE-G: Dual Source Conflict Resolution ✅ COMPLETADA (2026-04-10)

- [x] Tarea 1: _inject_brecha_scores NO sobrescribe nombre/costo/detalle
  - [x] Líneas 2013-2015 reemplazadas (ya no setean _costo, _nombre, _detalle)
  - [x] Score vars (_score, _severity, _effort, _priority) sí se actualizan
- [x] Tarea 2: Conectar impactos reales al proposal generator
  - [x] brechas_reales agregado a DiagnosticSummary (data_structures.py)
  - [x] Diagnostic generator popula brechas_reales via _identify_brechas() (main.py)
  - [x] Proposal generator consume brechas_reales.impacto en _build_brecha_data()
  - [x] Fallback a top_problems cuando brechas_reales=None
- [x] Tarea 3: Tests
  - [x] test_brecha_scores_dont_overwrite_nombre — PASSED
  - [x] test_brecha_scores_dont_overwrite_costo — PASSED
  - [x] test_diagnostic_summary_includes_brechas_reales — PASSED
  - [x] test_proposal_uses_real_impact_weights — PASSED
  - [x] test_backward_compatible_without_brechas_reales — PASSED
- [x] Post-ejecución: dependencias, docs, log_phase_completion.py

---

## FASE-H: Performance Cache + Cleanup ✅ COMPLETADA (2026-04-10)

- [x] Tarea 1: Caché para _identify_brechas
  - [x] Caché implementado (instance-level _cached_brechas)
  - [x] Reset en generate() para evitar stale data
  - [x] _identify_brechas ejecuta 1x, no 9x
- [x] Tarea 2: pain_to_type cleanup
  - [x] low_ia_readiness removido de pain_to_type
- [x] Tarea 3: Loop normalization
  - [x] _build_brechas_section y _build_brechas_resumen_section usan misma convención (enumerate 1-based + i-1)
- [x] Tarea 4: Tests
  - [x] test_identify_brechas_cached_once
  - [x] test_cache_cleared_between_generates
  - [x] test_no_low_ia_readiness_in_pain_to_type
  - [x] test_loop_conventions_consistent
- [x] Post-ejecución: dependencias, docs, log_phase_completion.py

---

## FASE-I: data_structures.py Deduplication ✅ COMPLETADA (2026-04-10)

- [x] Tarea 1: Análisis de duplicados
  - [x] Scenario: versión viva identificada vs muerta (idénticas)
  - [x] calculate_quick_wins: versión viva identificada vs muerta (idénticas)
  - [x] extract_top_problems: versión viva identificada vs muerta (idénticas)
- [x] Tarea 2: Eliminación de definiciones muertas
  - [x] Scenario sin campos duplicados (12 líneas eliminadas)
  - [x] calculate_quick_wins con 1 sola definición (40 líneas eliminadas)
  - [x] extract_top_problems con 1 sola definición (55 líneas eliminadas)
  - [x] Import limpio funciona
- [x] Tarea 3: brechas_reales en DiagnosticSummary verificado
- [x] Tarea 4: Tests
  - [x] test_scenario_no_duplicate_fields — PASSED
  - [x] test_calculate_quick_wins_single_definition — PASSED
  - [x] test_extract_top_problems_single_definition — PASSED
  - [x] test_diagnostic_summary_has_brechas_reales — PASSED
- [x] Post-ejecución: dependencias, docs, log_phase_completion.py

---

## FASE-J: E2E Validation + Release

- [ ] Tarea 1: Pre-flight checks
  - [ ] Imports limpios
  - [ ] Tests FASE-F/G/H/I pasan
  - [ ] run_all_validations.py --quick pasa
- [ ] Tarea 2: v4complete ejecutado para amaziliahotel.com
  - [ ] Exit code 0
  - [ ] Coherence >= 0.80
  - [ ] Assets generados
- [ ] Tarea 3: Verificación de resultados
  - [ ] 0 phantom costs en propuesta
  - [ ] Costos reflejan impactos reales
  - [ ] Nombres consistentes entre diagnóstico y propuesta
  - [ ] Sin errores de import
- [ ] Tarea 4: Veredicto emitido
  - [ ] Template de veredicto completado
  - [ ] Documentado: EXITOSO / PERSISTENCIA PARCIAL / FALLIDO
- [ ] Tarea 5: Release v4.26.0 (solo si EXITOSO)
  - [ ] VERSION.yaml actualizado a 4.26.0
  - [ ] CHANGELOG.md con entrada completa
  - [ ] log_phase_completion.py --fase FASE-RELEASE-4.26.0
  - [ ] sync_versions.py ejecutado
  - [ ] version_consistency_checker.py pasa
  - [ ] GUIA_TECNICA.md actualizado
  - [ ] SYSTEM_STATUS.md regenerado
  - [ ] Git commit + tag

---

## Métricas Acumuladas

| Métrica | Antes | Después F | Después G | Después H | Después I | Final |
|---------|-------|-----------|-----------|-----------|-----------|-------|
| Tests nuevos | 0 | 5 | 10 | 14 | 18 | 18 |
| Regresiones | — | 0 | 0 | 0 | 0 | 0 |
| Phantom costs | Sí | No | No | No | No | No |
| Impactos reales | No | No | Sí | Sí | Sí | Sí |
| _identify_brechas calls | 9x | 9x | 9x | 1x | 1x | 1x |
| Duplicados DS | 3 | 3 | 3 | 3 | 0 | 0 |
