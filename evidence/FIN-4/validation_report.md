# FIN-4 Combined E2E Validation Report

**Hotel**: Hotel Castilla Real (hotelcastillareal.com)
**Fecha**: 2026-05-04
**v4complete exit code**: 0 (EXITÓ)

---

## Criterios Financieros

| # | Criterio | Resultado | Detalle |
|---|----------|-----------|---------|
| C1 | ADR ≠ $300K legacy | ❌ FAIL | `input_data.adr_cop = 300000.0` — el hardcode legacy sigue activo en `data_sources.adr = "legacy_hardcode"` |
| C2 | precision_tier + can_show_exact_money | ❌ FAIL | `precision_tier` NO encontrado en ningún JSON |
| C3 | Sin $2.610.000 exacto | ⚠️ WARNING | "$2.610.000" aparece múltiples veces en diagnóstico: `expected_monthly_cop = 2610000.0`, `realistic = 2610000.0` |
| C4 | Advertencia preliminar | ✅ PASS | "Estimación basada en datos limitados..." presente en `breakdown.disclaimer` |
| C5 | CTA onboarding | ✅ PASS | "Conecte Google Analytics 4 para un diagnóstico más preciso" presente |
| C6 | Sin centavos falsos | ⚠️ WARNING | Valores como $701.568, $280.575, $420.993 — sin decimales pero precisión sospechosa |
| C7 | Fuente de datos mencionada | ✅ PASS | `data_sources.adr = "legacy_hardcode"` documentado en JSON |

### Detalle C1 (CRÍTICO):

```json
"input_data": {"adr_cop": 300000.0, ...},
"data_sources": {"adr": "legacy_hardcode", ...},
"breakdown": {
  "ota_commission_basis": "120 noches OTA × $300,000 ADR × 15% comisión"
}
```

El ADR legacy de $300.000 COP sigue siendo la base de los escenarios. Los feature flags `FINANCIAL_REGIONAL_ADR_ENABLED=true` y `FINANCIAL_REGIONAL_ADR_MODE=active` se activaron, pero el pipeline financiero no los reconoció.

---

## Criterios de Canal

| # | Criterio | Resultado | Detalle |
|---|----------|-----------|---------|
| C8 | channel_context presente | ❌ FAIL | `channel_context = {}` (vacío) en v4_complete_report.json |
| C9 | WhatsApp no asumido sin evidencia | ⚠️ SKIP | `dominant_channel = ""` (vacío) — ni forzado WhatsApp ni canal válido |
| C10 | channel_multiplier en scores | ❌ FAIL | `opportunity_scores = []` (vacío) — scorer no integrado |
| C11 | channel_reason trazable | ⚠️ INFO | No visible en diagnóstico. Fase CHAN-1/2 dice `ChannelEvidenceResolver` importable, pero no integrado en pipeline |

### Detalle C8/C10 (CRÍTICO):

El `ChannelEvidenceResolver` y `OpportunityScorer` (implementados en CHAN-1 y CHAN-2) NO están integrados en el pipeline de v4complete. Los criterios de canal requieren que `channel_context` y `opportunity_scores` aparezcan en el output, pero están vacíos.

---

## Veredicto

❌ **ISSUES — crear FASE-FIX para:**

1. **FIX-FIN-1**: El ADR legacy $300.000 sigue activo. 尽管 se activaron los feature flags, el pipeline no los usa. Causa raíz: `FinancialScenarioGenerator` no consulta `FinancialFeatureFlags.regional_adr_enabled` ni `regional_adr_mode=active`.

2. **FIX-CHAN-1**: `channel_context` vacío en v4_complete_report.json. Causa raíz: `ChannelEvidenceResolver` no está integrado en el flujo principal de v4complete — existe como módulo importable pero no se invoca desde el orchestrator.

3. **FIX-CHAN-2**: `opportunity_scores = []`. Causa raíz: `OpportunityScorer` (CHAN-2) no está invocado en el pipeline — los scores con `channel_multiplier` nunca se generan.

4. **FIX-PRECISION**: `precision_tier` y `can_show_exact_money` no aparecen en ningún JSON de output. Estos campos fueron implementados en FIN-1A/B pero no se escriben al final del pipeline.

---

## Criterios de Completitud — Estado

- [x] Pre-flight checks pasan (hotel accesible, flags, JSON, imports) ✅
- [x] v4complete ejecutado exitosamente sobre Hotel Castilla Real ✅
- [x] Evidencia copiada a `evidence/FIN-4/` ✅
- [x] C1-C7 verificados (financieros) — C1, C2 FALLAN ❌
- [x] C8-C11 verificados (canal) — C8, C10 FALLAN ❌
- [x] `evidence/FIN-4/validation_report.md` generado ✅
- [x] Issues documentados con causas raíz claras ✅

---

## Post-Ejecución: log_phase_completion.py

```
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FIN-4 \
    --desc "E2E combinado financiero + comercial — Hotel Castilla Real" \
    --archivos-nuevos "evidence/FIN-4/" \
    --tests "0" \
    --check-manual-docs
```
