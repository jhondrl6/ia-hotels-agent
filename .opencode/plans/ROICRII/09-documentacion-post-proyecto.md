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
**Fecha ejecución**: (pendiente)
**Archivos modificados**: (pendiente)
**Tests nuevos**: (pendiente)
**Hallazgos resueltos**: NEW-03, CRIT-02
**Notas**: (pendiente)

---

### FASE-3: Semántica + Floor + Gate
**Fecha ejecución**: (pendiente)
**Archivos modificados**: (pendiente)
**Tests nuevos**: (pendiente)
**Hallazgos resueltos**: IMP-01, NEW-05, NEW-02
**Notas**: (pendiente)

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
