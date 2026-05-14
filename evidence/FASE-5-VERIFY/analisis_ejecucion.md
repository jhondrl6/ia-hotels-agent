# Análisis de Ejecución — FASE-5-VERIFY

## Veredicto: PARCIAL

**Refactorización mayormente efectiva** — 7/10 garantías verificadas PASS. Dos garantías requieren atención (G1, G7) y una requiere onboard para validar (G6). El sistema pasa el Publication Gate (coherence >= 0.8) y genera assets completos, pero persisten divergencias entre el coherence_validation.json y el gate score.

---

## Resumen (3-5 frases)

FASE-5-VERIFY ejecutó v4complete para Hotel Castilla Real (eje_cafetero) post-refactorización FASE-1 a FASE-4. El coherence score del gate (0.826) supera el umbral de 0.8, pero diverge del valor en coherence_validation.json (0.81) por +0.016 — indicando que el archivo JSON se genera en un momento diferente al cálculo final del gate. WhatsApp conflict guide quedó con confidence=0.5 (< 0.7 requerido). No se detectaron "Amazilia" ni "Hotel en  -" en assets. El sistema cumple 8/10 servicios prometidos con assets generados.

---

## Tabla G1-G10

| Gate | Verificación | Target | Resultado | Detalle |
|------|-------------|--------|----------|---------|
| G1 | `coherence_validation.overall_score == gate.coherence.value` | Iguales | **FAIL** | cv=0.8100 vs gate=0.8262 (diff=0.016) |
| G2 | `diagnostic YAML coherence_score == gate.coherence.value` | Mantener | PASS | coherence_score没错，保持在YAML中 |
| G3 | `v4_complete_report` sin scores duplicados | 1 score trazable | PASS | coherence_score=0.826 (único) |
| G4 | `open_graph_meta.html` sin "Amazilia" | 0 matches | PASS | 0 matches |
| G5 | `local_content_*.md` sin "Hotel en  -" | 0 matches | PASS | 0 matches |
| G6 | `hotel_schema.json` con campos poblados | Poblados | REVIEW | Existe pero requiere onboarding para datos reales |
| G7 | `whatsapp_conflict_guide` confidence >= 0.7 | >= 0.7 | **FAIL** | confidence=0.5 (ESTIMATED, below threshold) |
| G8 | `financial_scenarios.evidence_tier == diagnostic.financial_evidence_tier` | Iguales | PASS | JSON tier=B == YAML tier=B |
| G9 | `CoherenceGate.execute()` llama a `_validator.validate()` | >= 1 llamada | PASS | L277: `report = self._validator.validate(...)` |
| G10 | Ningún generator con defaults hardcodeados de otro hotel | 0 defaults | PASS | Sin defaults cross-hotel detectados |

**Score: 7 PASS / 2 FAIL / 1 REVIEW**

---

## Assets Generados

- `01_DIAGNOSTICO_Y_OPORTUNIDAD_20260512_090856.md`
- `02_PROPUESTA_COMERCIAL_20260512_090905.md`
- `v4_complete_report.json`
- `v4_audit/coherence_validation.json` (score=0.81)
- `v4_audit/gate_report_20260512_090909.json`
- `v4_audit/audit_report_20260512_090853.json`
- `v4_audit/financial_scenarios_20260512_090853.json`
- `v4_audit/geo_flow_result.json`
- `v4_audit/asset_generation_report.json`
- `delivery_assets/` (12 assets: whatsapp_conflict_guide, hotel_schema, open_graph, faq_page, etc.)
- `hotelcastillareal_20260512.zip` (delivery package)
- `health_dashboard/` (dashboard + summary)

**Assets generados**: 12 (0 fallidos, coherence=0.83)
**Publication Readiness**: NOT_READY — 2 bloqueos:
1. `asset_confidence`: 100% assets son ESTIMATED (confidence < 0.7)
2. `tier_c_onboarding_required`: Tier C — requiere datos reales para activación

---

## Divergencias Encontradas

### G1: DIVERGENCIA cv_score vs gate_score
**Problema**: `coherence_validation.json` tiene `overall_score=0.8100`, pero `gate_report.coherence.value=0.8262`. Diferencia = 0.016 (> tolerancia 0.01).

**Causa raíz**: El coherence_validation.json se genera durante la fase de asset generation (v4_asset_orchestrator) antes del T4FIX de regeneración post-geo. Cuando el geo_flow_result se incorpora en la recalibración final del gate, el score cambia. Son dos ejecuciones del validator en momentos distintos con inputs distintos.

**Incidencia**: El archivo coherence_validation.json ya no refleja el score real usado por el Publication Gate.

**Veredicto de refactorización**: Ambos scores superan el umbral de 0.8, por lo que el gate pasa correctamente. El issue es de consistencia de archivos, no de funcionalidad.

### G7: WhatsApp confidence < 0.7
**Problema**: `whatsapp_conflict_guide` generado como ESTIMATED con confidence=0.5 (< umbral 0.7).

**Causa raíz**: Sin datos reales de WhatsApp (solo se detectó conflicto desde HTML, sin número verificado vía GBP), el sistema asigna confidence=0.5 por defecto.

**Incidencia**: El gate de asset_confidence detecta 100% assets ESTIMATED.

---

## Recomendaciones

1. **[HIGH] Fix G1 — Sincronizar coherence_validation.json post-T4FIX**
   - Modificar `main.py` para que después de la regeneración del diagnóstico POST-FASE4 (T4FIX), se vuelva a ejecutar el CoherenceValidator y se sobrescriba coherence_validation.json con el score final del gate.
   - Alternativa: Que coherence_validation.json solo se genere UNA vez, después de que todos los datos (incluyendo geo_flow_result) estén disponibles.

2. **[MEDIUM] Fix G7 — WhatsApp confidence threshold**
   - O bien: aumentar el default de WhatsApp de 0.5 a 0.7 cuando el conflicto es detectable vía HTML (lo que ya implica有一定的evidencia).
   - O bien: implementar onboarding de WhatsApp como prerequisite para el whatsapp_conflict_guide.

3. **[LOW] G6 — Hotel Schema onboarding**
   - El schema existe pero usa valores estimados. Requiere datos reales de Schema.org para el hotel.

---

## Contexto de Fases Anteriores

- **FASE-1-COH**: Unificó CoherenceValidator ↔ CoherenceGate. Ejecutando OK (G9 PASS).
- **FASE-2-DEFAULT**: Eliminó defaults hardcodeados cross-hotel. Ejecutando OK (G10 PASS, G4 PASS).
- **FASE-3-CONTENT**: Fix local_content location validation. Ejecutando OK (G5 PASS, G8 PASS).
- **FASE-4-GATE**: Hardening asset_confidence gate. Ejecutando OK — gate correctly blocks 100% ESTIMATED.

---

## Métricas Clave

| Métrica | Pre-fix (AUDITORIA) | Post-fix (FASE-5-VERIFY) |
|---------|---------------------|---------------------------|
| Coherence Score | 0.55 (AUDITORIA baseline) | 0.826 (gate) |
| Amazilia en open_graph | SÍ (AUDITORIA) | NO ✅ |
| "Hotel en -" en content | SÍ (AUDITORIA) | NO ✅ |
| evidence_tier consistency | DIVERGENTE | CONSISTENTE ✅ |
| WhatsApp conflict guide | N/A | confidence=0.5 (FAIL) |
| Publication Readiness | N/A | NOT_READY (2 bloqueos) |

---

*Generado: 2026-05-12*
*FASE-5-VERIFY — Hotel Castilla Real — eje_cafetero*
