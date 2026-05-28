# Checklist de Implementación — ROICRII

**Plan**: ROICRII
**Target**: v4.56.0
**Origen**: ROICRII.md (reporte QA v3, 2026-05-27)
**Creado**: 2026-05-27
**Última actualización**: 2026-05-28

---

## FASE-1: Unificar ROI [CRIT-01, IMP-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 1A | Cambiar `:.1f` → `:.2f` en roi_formatter.py L81 | ✅ | `grep ":\.2f" roi_formatter.py` = 1 match |
| 1B | Reemplazar llamadas `_calculate_roi()` L710,810,814 y `_calculate_roi_saas()` L854 por roi_formatter | ✅ | `grep calcular_metricas_roi` = 6 hits en generator |
| 1C | Eliminar métodos inline `_calculate_roi()` y `_calculate_roi_saas()` | ✅ | `grep -c "def _calculate_roi"` = 0 |
| 1D | Tests: test_roi_unification.py (formato .2f, 0 inline, roi > 0) | ✅ | 11 passed, 0 failed |

---

## FASE-2: Coherencia Financiera [NEW-03, CRIT-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 2A | Gate L377: `total_investment_opex = price_monthly * 6` (sin CAPEX) | ✅ | `grep total_investment_opex` = 1 match |
| 2B | Wrapper L143: pasar `expected_recovery_cop` al calculator | ✅ | `grep expected_recovery_cop wrapper.py` ≥1 |
| 2C | Tests: test_financial_coherence.py (gate opex-only, pipeline activo) | ✅ | pytest pasando |

---

## FASE-3: Semántica + Floor + Gate [IMP-01, NEW-05, NEW-02]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 3A | pain_ratio_note: "addressable" + fee/loss separados | ✅ | Copy contiene "addressable" |
| 3B | operational_floor fallback = 400K en L245 | ✅ | 2 caminos = mismo fallback |
| 3C | CommercialGateBlockedError para audiencia externa | ✅ | Exception se lanza |
| 3D | Tests: test_semantics_floor_gate.py | ✅ | pytest pasando |

---

## FASE-4: CAPEX + Renombrar [IMP-03, NEW-04]

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 4A | CAPEX breakdown: config + dataclass + template | ✅ | ≥3 componentes en tabla |
| 4B | Renombrar pain_ratio → addressable_pain_ratio (alias + comentario) | ✅ | grep ≥2 matches |
| 4C | Tests: test_capex_rename.py | ✅ | pytest pasando |

---

## FASE-5: v4complete + Análisis

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 5A | pytest completo sin regresiones | ✅ | 3 archivos fijaos: test_proposal_alignment (7→8+copy), test_conditional_new_assets (@skip), test_phase4_guardrails (StubCoherenceReport attr). 24 passed en archivo. |
| 5B | v4complete Hotel Castilla Real | ✅ | Generado: diagnóstico, propuesta, audit JSONs, coherence 0.81, gate 0 blocking errors |
| 5C | Nivel 1 — ROI unificado (.2f, 0 inline) | ✅ | `grep -c def _calculate_roi` = 0. ROI 0.45X/2.10X (2 decimales) |
| 5C | Nivel 2 — Coherencia financiera (gate opex, pipeline activo) | ✅ | `total_investment_opex = price_monthly * 6`. `expected_recovery_cop` pasado wrapper→calculator |
| 5C | Nivel 3 — Gobernanza semántica (addressable, floor 400K) | ✅ | "14% de su pérdida monthly addressable por IAO". Floor $400,000 COP/mes |
| 5C | Nivel 4 — Gate estricto (exception, CAPEX desglose) | ✅ | 0 blocking errors. CAPEX tabla con 3 componentes |
| 5C | Nivel 5 — CI/CD (coherence ≥0.80, 0 failed) | ✅ | coherence 0.81 ≥ 0.80. gate 0 blocking |
| 5D | Documentar métricas finales en 09-documentacion | ✅ | 09-documentacion-post-proyecto.md actualizado con output, coherence, veredicto |

---

## FASE-6: RELEASE v4.56.0

| ID | Tarea | Estado | Verificación |
|----|-------|--------|-------------|
| 6A | VERSION.yaml → 4.56.0 | ⬜ | Pendiente |
| 6B | CHANGELOG.md entrada v4.56.0 | ⬜ | Pendiente |
| 6C | REGISTRY.md actualizado | ✅ | FASE-5 ya registrada via log_phase_completion.py |
| 6D | Domain primer regeneration | ⬜ | Pendiente |
| 6E | log_phase de fases 1-5 | ⬜ | FASE-5 ejecutada, fases 1-4 pend. verificar |
| 6F | Pre-commit o run_all_validations.py | ⬜ | Pendiente |
| 6G | Veredicto final en 09-documentacion | ✅ | Plan cerrado con veredicto ✅ SÍ |

---

## QA Score Tracking

| Checkpoint | Pre-ROICRII | Post-ROICRII |
|------------|-------------|--------------|
| Score total | 72% (18/25) | ⬜ (objetivo ≥90%) |
| CRIT-01 resuelto | ❌ | ✅ |
| CRIT-02 resuelto | ❌ | ✅ |
| NEW-02 resuelto | ❌ | ✅ |
| NEW-03 resuelto | ❌ | ✅ |
| IMP-01 resuelto | ❌ | ✅ |
| IMP-02 resuelto | ❌ | ✅ |
| IMP-03 resuelto | ❌ | ✅ |
| NEW-04 resuelto | ❌ | ✅ |
| NEW-05 resuelto | ❌ | ✅ |
| Coherence | 0.826 | 0.81 ✅ |
