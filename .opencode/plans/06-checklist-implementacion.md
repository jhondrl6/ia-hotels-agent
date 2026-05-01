# Checklist Maestro de Implementación — FEATURE-CONFIG-EXTRACTION

**Versión:** 1.1.0 | **Target:** v4.38.0 | **Última actualización:** 2026-05-01

---

## Estado Global

|| Fase | Estado | Sesión | Fecha | Iteraciones ||
||------|--------|--------|-------|-------------|
|| FASE-CONFIG-1 | ✅ COMPLETADA | 2 | 2026-04-30 | ~45 ||
|| FASE-CONFIG-2 | ✅ COMPLETADA | 3 | 2026-04-30 | ~38 ||
|| FASE-CONFIG-3A | ✅ COMPLETADA | 4 | 2026-04-30 | ~30 ||
|| FASE-CONFIG-3B | ✅ COMPLETADA | 5 | 2026-04-30 | ~35 ||
|| FASE-CONFIG-4 | ✅ COMPLETADA | 6 | 2026-04-30 | ~28 ||
|| FASE-CONFIG-5 | ✅ COMPLETADA | 7 | 2026-04-30 | ~32 ||
|| FASE-CONFIG-6 | ✅ COMPLETADA | 8 | 2026-04-30 | ~40 ||
|| FASE-CONFIG-7 | ✅ COMPLETADA | 9 | 2026-04-30 | ~42 ||
|| FASE-CONFIG-8 | ✅ COMPLETADA | 10 | 2026-04-30 | ~35 ||
|| FASE-RELEASE-4.38.0 | ✅ COMPLETADA | 11 | 2026-05-01 | ~25 ||

**Leyenda:** ⬜ PENDIENTE | 🔄 EN PROGRESO | ✅ COMPLETADA | ⏳ INCOMPLETA | ❌ BLOQUEADA

---

## FASE-CONFIG-1: sync_versions fix

**Prompt:** `05-prompt-inicio-sesion-fase-CONFIG-1.md`
**Objetivo:** Corregir CR-1, CR-2, CR-3 del bug sync_versions

- [x] CR-1: Corregir doble escape en sync_config.yaml L101-103
- [x] CR-3: Agregar `v?` al pattern y `v{version}` al template de GUIA_TECNICA
- [x] CR-2: Agregar validación post-reemplazo en sync_versions.py L131-133
- [x] Test: sync_versions.py --check reporta correctamente
- [x] log_phase_completion.py --fase FASE-CONFIG-1 ejecutado

---

## FASE-CONFIG-2: Fallbacks peligrosos

**Prompt:** `05-prompt-inicio-sesion-fase-CONFIG-2.md`
**Objetivo:** Corregir CR-3 (fallbacks) — H-11, H-12, H-13, H-27

- [x] Crear `config/fallbacks.yaml` con schema validado
- [x] H-11: benchmark_score → YAML
- [x] H-12: score_tecnico fallback → YAML
- [x] H-13: coherence_score fallback → YAML
- [x] H-27: voice_readiness fallback → YAML
- [x] Agregar flag "estimated" visible en template
- [x] Tests: 16/16 PASSED
- [x] log_phase_completion.py --fase FASE-CONFIG-2 ejecutado

---

## FASE-CONFIG-3A: Pricing extraction

- [x] Crear `config/pricing.yaml`
- [x] TIER_CONFIG + GATE ratios → YAML
- [x] floor_price unificado
- [x] Tests: pricing con YAML, sin YAML, con floor unificado
- [x] log_phase_completion.py --fase FASE-CONFIG-3A ejecutado

---

## FASE-CONFIG-3B: Scenarios + financial engine

- [x] Crear `config/scenarios.yaml` + `config/financial_defaults.yaml`
- [x] recovery_factors, weights, degradation, ia_boost → YAML
- [x] OTA shifts → YAML
- [x] SUPERPOSITION_FACTOR + DEFAULTS → YAML
- [x] Tests: módulos con YAML presente, ausente, corrupto
- [x] log_phase_completion.py --fase FASE-CONFIG-3B ejecutado

---

## FASE-CONFIG-4: Template + comerciales

- [x] Eliminar duplicación garantías (_build_guarantees_section)
- [x] Crear `config/commercial.yaml`
- [x] ROI cap, break_even, descuentos, cuotas → YAML
- [x] Template con variables comerciales
- [x] Tests: template rendering con YAML
- [x] log_phase_completion.py --fase FASE-CONFIG-4 ejecutado

---

## FASE-CONFIG-5: Umbrales + narrativas

- [x] Crear `config/regional_benchmarks.yaml`
- [x] 14 pain narrative impacts → YAML
- [x] Confidence thresholds, coherence multipliers → YAML
- [x] GBP, mobile, citability, IAO thresholds → YAML
- [x] Tests: benchmarks con YAML, sin YAML, por región
- [x] log_phase_completion.py --fase FASE-CONFIG-5 ejecutado

---

## FASE-CONFIG-6: Config reconnect + Deprecación módulos huérfanos

- [x] settings.yaml: header de deprecación + eliminar duplicados
- [x] Deprecar 4 módulos huérfanos (Profound, Semrush, data_aggregator, aeo_metrics_gen)
- [x] Corregir AnalyticsStatus.is_any_missing() (solo GA4 + GSC)
- [x] Limpiar modules/analytics/__init__.py
- [x] Tests: config reconnect + deprecation + AnalyticsStatus
- [x] log_phase_completion.py --fase FASE-CONFIG-6 ejecutado

---

## FASE-CONFIG-7: v4complete Amazilia + Análisis

- [x] v4complete ejecutado para Amazilia Hotel
- [x] Evidencia guardada en evidence/fase-config-7/
- [x] Hardcodes resueltos en output
- [x] Flags "estimated" visibles donde aplica
- [x] log_phase_completion.py --fase FASE-CONFIG-7 ejecutado

---

## FASE-CONFIG-8: Suite de tests de regresión

- [x] 60 tests de config (migración, fallback, schema, integración)
- [x] doctor.py --status: integridad config files verificada
- [x] run_all_validations.py --quick: 4/4 checks
- [x] log_phase_completion.py --fase FASE-CONFIG-8 ejecutado

---

## FASE-RELEASE-4.38.0: Documentación + Release

**Prompt:** `05-prompt-inicio-sesion-fase-RELEASE-4.38.0.md`
**Objetivo:** Cierre documental + version bump

- [x] E1: version_consistency_checker.py + doctor.py — ALL PASSED
- [x] E2: VERSION.yaml 4.37.0 → 4.38.0 + sync_versions.py — 6/6 sincronizados
- [x] E3: CHANGELOG.md entrada [4.38.0] formato CONTRIBUTING.md completo
- [x] E4: GUIA_TECNICA.md nota técnica v4.38.0 con módulos, problema, solución, backwards compatibility
- [x] E5: Skills/Workflows — 17 skills, README.md verificado
- [x] E6: SYSTEM_STATUS.md regenerado con v4.38.0
- [x] E7: DOMAIN_PRIMER.md — All validations passed
- [x] E8: Symlink intacto + run_all_validations 4/4 + git commit
- [x] log_phase_completion.py --fase FASE-RELEASE-4.38.0 ejecutado

---

## Progreso: 10/10 fases completadas ✅ PROYECTO COMPLETADO
