# Documentación Post-Proyecto — ROICRII

**Plan**: ROICRII
**Target**: v4.56.0
**Creado**: 2026-05-27

---

## Acumulador de Documentación por Fase

### FASE-1: Unificar ROI
**Fecha ejecución**: 2026-05-27
**Archivos modificados**: `modules/financial_engine/roi_formatter.py` (+roi_cap param, :.1f→:.2f), `modules/commercial_documents/v4_proposal_generator.py` (−2 inline methods, +4 unified calls)
**Tests nuevos**: `tests/test_roi_unification.py` (11 tests: 3 inline-deleted, 3 precision, 3 cap, 1 CastillaReal, 1 single-motor)
**Hallazgos resueltos**: CRIT-01 (tres sistemas ROI paralelos → uno solo), IMP-02 (formato :.1f → :.2f)
**Notas**: roi_formatter ahora acepta roi_cap opcional (preserva cap 5.0X de commercial.yaml). 6 referencias activas a roi_formatter en v4_proposal_generator (1 import + 5 calls).

---

### FASE-2: Coherencia Financiera
**Fecha ejecución**: 2026-05-27
**Archivos modificados**: `modules/commercial_documents/v4_proposal_generator.py` (L377: total_investment→total_investment_opex, ROI sin CAPEX), `modules/financial_engine/pricing_resolution_wrapper.py` (L143: pasa expected_recovery_cop al calculator, activa pipeline 3 pasos)
**Tests nuevos**: `tests/test_financial_coherence.py` (TestGateOpexOnly + TestWrapperActivatesPipeline — pytest no disponible en entorno WSL, pendiente ejecución)
**Hallazgos resueltos**: NEW-03 (gate L377 usaba CAPEX en denominador → opex-only), CRIT-02 (wrapper L143 no pasaba expected_recovery_cop → calculado y pasado: pain_ratio=0.05, recovery_factor=0.35)
**Notas**: pipeline 3 pasos ahora se activa desde wrapper.resolve() → calculator.calculate(expected_recovery_cop=...) → _calculate_with_pipeline(). Gate ROI usa price_monthly*6 como denominador (CAPEX=activo del cliente, no inversión en servicio).

---

### FASE-3: Semántica + Floor + Gate
**Fecha ejecución**: 2026-05-27
**Archivos modificados**:
- `modules/commercial_documents/v4_proposal_generator.py` (pain_ratio_note clarificado con "addressable" + "zona addressable por IAO"; CommercialGateBlockedError añadida como clase L36 y raise L418)
- `modules/financial_engine/pricing_calculator.py` (L245: fallback operational_floor unificado a 400_000)
- `tests/test_semantics_floor_gate.py` — creado (5 tests)
**Tests nuevos**: `tests/test_semantics_floor_gate.py` — 5 passed (CommercialGateBlockedError: defined, stores_gate_ids, message_format, default_message, can_be_caught)
**Hallazgos resueltos**: IMP-01 (pain_ratio_note ahora diferencia addressable vs fee/loss), NEW-05 (operational_floor fallback = 400K en ambos caminos — 4 matches 400_000), NEW-02 (gate externo ahora lanza CommercialGateBlockedError, no solo warning)
**Notas**: "addressable" aparece 3 matches en v4_proposal_generator.py; CommercialGateBlockedError 2 matches (class + raise); pytest tests/test_semantics_floor_gate.py 5 passed, quality_gates 27 passed.

---

### FASE-4: CAPEX + Renombrar
**Fecha ejecución**: (pendiente)
**Archivos modificados**: (pendiente)
**Tests nuevos**: (pendiente)
**Hallazgos resueltos**: IMP-03, NEW-04
**Notas**: (pendiente)

---

### FASE-5: v4complete + Análisis
**Fecha ejecución**: (pendiente)
**Output v4complete**: (pendiente — paths de archivos generados)
**Coherence score**: (pendiente)
**QA score**: (pendiente)
**Hallazgos verificados**: Todos
**Notas**: (pendiente)

---

## Métricas Comparativas Finales

| Métrica | Pre-ROICRII (v4.55.0) | Post-ROICRII (v4.56.0) |
|---------|----------------------|------------------------|
| ROI motor | 3 paralelos | roi_formatter único |
| ROI formato | :.1f (1 decimal) | :.2f (2 decimales) |
| Gate ROI | Con CAPEX | Opex-only |
| Pipeline 3 pasos | NUNCA activado | Activa desde wrapper |
| pain_ratio | 3 significados | 2 semánticas separadas |
| operational_floor | 2 fallbacks | 400K único |
| Gate externo | Solo warning | Exception bloqueante |
| CAPEX | Monolítico $2.5M | Desglosado |
| Coherence | 0.826 | (pendiente) |
| QA Score | 72% (18/25) | (pendiente — objetivo ≥90%) |

---

## Veredicto Final

(pendiente — completar tras FASE-5)

**La propuesta es APTA para envío al cliente**: ⬜ SÍ / ⬜ NO

Si NO: razón(es) y plan de remediación pendiente.
