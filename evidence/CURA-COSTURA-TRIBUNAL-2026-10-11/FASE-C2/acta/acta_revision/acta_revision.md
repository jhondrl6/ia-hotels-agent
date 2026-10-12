# Acta de Revisión — Tribunal de Certificación

**Hotel**: hotelx
**Fecha**: 2026-10-12T14:12:56.134553
**Veredicto**: 🚫 BLOQUEADO
**Evidence Tier**: B
**Cláusulas evaluadas**: 6

## Regla de Primer Piso

**Aplicada**: Sí
**Artefacto fuente**: `financial_scenarios_20260904_120000.json → breakdown.evidence_tier`
**Razón**: evidence_tier B → máximo condicional

## Cláusulas P6 Evaluadas

### P6.1: Critical Recall (Diagnóstico)

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `gate_report_*.json`
- **Finding**: gate_report no disponible

### P6.2: Alineación de Promesas (NL)

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `revision_alineacion.json`
- **Finding**: Bot 2 (alignment_reviewer) está implementado y su report se publica en revision_alineacion.json; la cláusula no se certifica en T1 por decisión de contrato (fuera de T1_CERTIFIABLE_CLAUSES), no por ausencia del revisor

### P6.3: Completitud de Assets

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `asset_generation_report.json`
- **Finding**: asset_generation_report no disponible

### P6.4: Cobertura Propuesta→Asset

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `proposal_asset_matrix.json`
- **Finding**: Formato de proposal_asset_matrix no reconocido

### P6.5: Honestidad Comercial (NL) — reservada Bot 4

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `None`
- **Finding**: Reservada para Bot 4 (honestidad NL) — D-T1.3 opción a

### P6.6: Coherencia + Contradicciones

- **Status**: ⬜ NOT_EVALUABLE
- **Artefacto fuente**: `gate_report_*.json`
- **Finding**: gate_report no disponible

## Reportes de Revisores

| Bot | Estado | Hallazgos | CRITICAL | Recomendación | Informe |
|-----|--------|-----------|----------|---------------|---------|
| diagnosis_reviewer | 🚫 no corrió | 0 | 0 | N/A | — |
| asset_reviewer | 🚫 no corrió | 0 | 0 | N/A | — |
| alignment_reviewer | 🚫 no corrió | 0 | 0 | N/A | — |
| honesty_reviewer | ⬜ insumo no evaluable | 2 | 2 | BLOQUEAR | revision_honestidad.json |

## Acciones correctivas

- **[CRITICAL] OVER_PRESENTATION** — dueño: `comercial`
  - Artefacto: `02_PROPUESTA_COMERCIAL.md`
  - Instrucción: La propuesta usa «verificadas» (LENGUAJE_VERIFICACION) con evidence_tier=B (no A) en: Ofrecemos soluciones verificadas para su hotel.
- **[CRITICAL] OVER_PRESENTATION** — dueño: `comercial`
  - Artefacto: `02_PROPUESTA_COMERCIAL.md`
  - Instrucción: La propuesta usa «confirmados» (LENGUAJE_VERIFICACION) con evidence_tier=B (no A) en: Publicamos datos confirmados del mercado en su ficha.

## Enforcement

- **Knob**: `GATE_BLOCKING_ENABLED`
- **Bloqueo activo**: Sí
- **Suprimido por el operador**: No

---

*Generado por TribunalJudge v4.80.0 — 2026-10-12 14:12*