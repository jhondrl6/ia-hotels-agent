# Acta de Revisión — Tribunal de Certificación

**Hotel**: donalfonsohotel
**Fecha**: 2026-10-24T15:51:13.728352
**Veredicto**: ⚠️ APROBADO-CONDICIONAL
**Evidence Tier**: B+
**Cláusulas evaluadas**: 6

**Causa del condicional**: `ANALYTICS_CEILING` — techo de analytics — onboarding verificado; faltan datos de analítica para tier A

## Regla de Primer Piso

**Aplicada**: Sí
**Artefacto fuente**: `financial_scenarios_20261024_155101.json → breakdown.evidence_tier`
**Razón**: evidence_tier B+ → máximo condicional

## Cláusulas P6 Evaluadas

### P6.1: Critical Recall (Diagnóstico)

- **Status**: ✅ PASS
- **Artefacto fuente**: `gate_report_*.json`
- **Finding**: critical_recall OK: Critical recall at 100.0% (threshold: 90%)

### P6.2: Alineación de Promesas (NL)

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `revision_alineacion.json`
- **Finding**: Bot 2 (alignment_reviewer) está implementado y su report se publica en revision_alineacion.json; la cláusula no se certifica en T1 por decisión de contrato (fuera de T1_CERTIFIABLE_CLAUSES), no por ausencia del revisor

### P6.3: Completitud de Assets

- **Status**: ✅ PASS
- **Artefacto fuente**: `asset_generation_report.json`
- **Finding**: 12/12 assets generados exitosamente

### P6.4: Cobertura Propuesta→Asset

- **Status**: ✅ PASS
- **Artefacto fuente**: `proposal_asset_matrix.json`
- **Finding**: delivery_ready=true: 6 servicios prometidos, 6 linked, 0 en producción

### P6.5: Honestidad Comercial (NL) — reservada Bot 4

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `None`
- **Finding**: Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a

### P6.6: Coherencia + Contradicciones

- **Status**: ✅ PASS
- **Artefacto fuente**: `gate_report_*.json`
- **Finding**: coherence=PASS (0.926969696969697); hard_contradictions=PASS (0)

## Reportes de Revisores

| Bot | Estado | Hallazgos | CRITICAL | Recomendación | Informe |
|-----|--------|-----------|----------|---------------|---------|
| diagnosis_reviewer | ✅ sin hallazgos | 0 | 0 | APROBADO | revision_diagnostico.json |
| asset_reviewer | ⚠️ con hallazgos | 1 | 0 | APROBADO | revision_assets.json |
| alignment_reviewer | ⬜ insumo no evaluable | 1 | 0 | DEVOLVER-PRUEBAS | revision_alineacion.json |
| honesty_reviewer | ⬜ insumo no evaluable | 1 | 0 | DEVOLVER-PRUEBAS | revision_honestidad.json |

## Acciones correctivas

Ninguna: el acta no declaró hallazgos bloqueantes.

## Enforcement

- **Knob**: `GATE_BLOCKING_ENABLED`
- **Bloqueo activo**: Sí
- **Suprimido por el operador**: No

---

*Generado por TribunalJudge v4.81.1 — 2026-10-24 15:51*