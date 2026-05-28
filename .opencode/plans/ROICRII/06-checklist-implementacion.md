# Checklist de Implementación — ROICRII

**Plan**: ROICRII
**Target**: v4.56.0
**Origen**: ROICRII.md (reporte QA v3, 2026-05-27)
**Creado**: 2026-05-27

---

## FASE-1: Unificar ROI [CRIT-01, IMP-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 1A | Cambiar `:.1f` → `:.2f` en roi_formatter.py L81 | ✅ | `grep ":\.2f" roi_formatter.py` = 1 match |
| 1B | Reemplazar llamadas `_calculate_roi()` L710,810,814 y `_calculate_roi_saas()` L854 por roi_formatter | ✅ | `grep "calcular_metricas_roi"` = 6 hits en generator |
| 1C | Eliminar métodos inline `_calculate_roi()` y `_calculate_roi_saas()` | ✅ | `grep -c "def _calculate_roi"` = 0 |
| 1D | Tests: test_roi_unification.py (formato .2f, 0 inline, roi > 0) | ✅ | 11 passed, 0 failed |

---

## FASE-2: Coherencia Financiera [NEW-03, CRIT-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 2A | Gate L377: `total_investment_opex = price_monthly * 6` (sin CAPEX) | ⬜ | `grep total_investment_opex` = 1 match |
| 2B | Wrapper L143: pasar `expected_recovery_cop` al calculator | ⬜ | `grep expected_recovery_cop wrapper.py` ≥1 |
| 2C | Tests: test_financial_coherence.py (gate opex-only, pipeline activo) | ⬜ | pytest pasando |

---

## FASE-3: Semántica + Floor + Gate [IMP-01, NEW-05, NEW-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 3A | pain_ratio_note: "addressable" + fee/loss separados | ⬜ | Copy contiene "addressable" |
| 3B | operational_floor fallback = 400K en L245 | ⬜ | 2 caminos = mismo fallback |
| 3C | CommercialGateBlockedError para audiencia externa | ⬜ | Exception se lanza |
| 3D | Tests: test_semantics_floor_gate.py | ⬜ | pytest pasando |

---

## FASE-4: CAPEX + Renombrar [IMP-03, NEW-04]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 4A | CAPEX breakdown: config + dataclass + template | ⬜ | ≥3 componentes en tabla |
| 4B | Renombrar pain_ratio → addressable_pain_ratio (alias + comentario) | ⬜ | grep ≥2 matches |
| 4C | Tests: test_capex_rename.py | ⬜ | pytest pasando |

---

## FASE-5: v4complete + Análisis

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 5A | pytest completo sin regresiones | ⬜ | 517+ passed, 0 failed |
| 5B | v4complete Hotel Castilla Real | ⬜ | Archivos generados OK |
| 5C | Nivel 1 — ROI unificado (.2f, 0 inline) | ⬜ | Verificado |
| 5C | Nivel 2 — Coherencia financiera (gate opex, pipeline activo) | ⬜ | Verificado |
| 5C | Nivel 3 — Gobernanza semántica (addressable, floor 400K) | ⬜ | Verificado |
| 5C | Nivel 4 — Gate estricto (exception, CAPEX desglose) | ⬜ | Verificado |
| 5C | Nivel 5 — CI/CD (coherence ≥0.80, 0 failed) | ⬜ | Verificado |
| 5D | Documentar métricas finales en 09-documentacion | ⬜ | Tabla completa |

---

## QA Score Tracking
---

## FASE-6: RELEASE v4.56.0

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 6A | VERSION.yaml → 4.56.0 | ⬜ | `grep "4.56.0" VERSION.yaml` |
| 6B | CHANGELOG.md entrada v4.56.0 | ⬜ | Entrada ROICRII agregada |
| 6C | REGISTRY.md actualizado | ⬜ | ROICRII registrado |
| 6D | Domain primer regeneration | ⬜ | DOMAIN_PRIMER.md actualizado |
| 6E | log_phase de fases 1-5 | ⬜ | 5 entradas en log |
| 6F | Pre-commit o run_all_validations.py | ⬜ | 5/5 PASSED |
| 6G | Veredicto final en 09-documentacion | ⬜ | Plan cerrado |

| Checkpoint | Pre-ROICRII | Post-ROICRII |
|------------|-------------|--------------|
| Score total | 72% (18/25) | ⬜ |
| CRIT-01 resuelto | ❌ | ⬜ |
| CRIT-02 resuelto | ❌ | ⬜ |
| NEW-02 resuelto | ❌ | ⬜ |
| NEW-03 resuelto | ❌ | ⬜ |
| IMP-01 resuelto | ❌ | ⬜ |
| IMP-02 resuelto | ❌ | ⬜ |
| IMP-03 resuelto | ❌ | ⬜ |
| NEW-04 resuelto | ❌ | ⬜ |
| NEW-05 resuelto | ❌ | ⬜ |
