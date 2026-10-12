# Acta de Revisión — Tribunal de Certificación

**Hotel**: donalfonsohotel
**Fecha**: 2026-10-12T16:57:06.335973
**Veredicto**: 🚫 BLOQUEADO
**Evidence Tier**: B+
**Cláusulas evaluadas**: 6

## Regla de Primer Piso

**Aplicada**: Sí
**Artefacto fuente**: `financial_scenarios_20261012_165654.json → breakdown.evidence_tier`
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
- **Finding**: 13/13 assets generados exitosamente

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
- **Finding**: coherence=PASS (0.9633333333333333); hard_contradictions=PASS (0)

## Reportes de Revisores

| Bot | Estado | Hallazgos | CRITICAL | Recomendación | Informe |
|-----|--------|-----------|----------|---------------|---------|
| diagnosis_reviewer | ✅ sin hallazgos | 0 | 0 | APROBADO | revision_diagnostico.json |
| asset_reviewer | ⚠️ con hallazgos | 1 | 0 | APROBADO | revision_assets.json |
| alignment_reviewer | ⚠️ con hallazgos | 33 | 0 | DEVOLVER-PRUEBAS | revision_alineacion.json |
| honesty_reviewer | ⚠️ con hallazgos | 3 | 2 | BLOQUEAR | revision_honestidad.json |

## Acciones correctivas

- **[CRITICAL] OVER_PRESENTATION** — dueño: `comercial`
  - Artefacto: `02_PROPUESTA_COMERCIAL.md`
  - Instrucción: La propuesta usa «total» (CUANTIFICADOR_ABSOLUTO) con evidence_tier=B+ (no A) en: ## 🛡️ GARANTÍAS: Protección total para usted
- **[CRITICAL] OVER_PRESENTATION** — dueño: `comercial`
  - Artefacto: `02_PROPUESTA_COMERCIAL.md`
  - Instrucción: La propuesta usa «total» (CUANTIFICADOR_ABSOLUTO) con evidence_tier=B+ (no A) en: ### 5. Transparencia total

## Enforcement

- **Knob**: `GATE_BLOCKING_ENABLED`
- **Bloqueo activo**: Sí
- **Suprimido por el operador**: No

## Evidencia del Paquete Suprimido

- **Ruta**: `C:\Users\Jhond\Github\iah-cli\output\v4_complete\deliveries\donalfonsohotel_20261012.zip.tmp`
- **SHA256**: `dc00cdb94130552bd8cfa8a3801ddfc4a1e521f1d6ffe79afdb92bb489fc9d12`
- **Miembros en el ZIP**: 56

---

*Generado por TribunalJudge v4.80.0 — 2026-10-12 16:57*