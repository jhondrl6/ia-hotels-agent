# ROICRIII — Documentación Post-Proyecto

**Proyecto:** Financial Coherence & Asset Semantics Rescue
**Versión target:** 4.57.0

---

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| B1: asset_semantics_validator en services table | v4_proposal_generator.py | validar_semantica_comercial integrado en _generate_dynamic_services_table — bloquea mapeos hallucination | FASE-3 |
| B2: BREACH_BY_ASSET corregido | v4_proposal_generator.py | monthly_report ya no mapea a FAQ; faq_page sí resuelve no_faq_schema; deprecados eliminados (optimization_guide, local_content_page) | FASE-3 |
| B6: narrativa WhatsApp coherente | v4_proposal_generator.py | "⚠️ Requiere corrección" → "📋 Auditoría incluida"; "Guía de corrección" → "Auditoría y Optimización de Conversión" | FASE-3 |

## Sección C: Correcciones Críticas

| Issue ID | Descripción | Archivo | Fase |
|----------|-------------|---------|------|
| ROICRIII-F1 | total_recovered unificado de effective_monthly_gain*6 a _maturity_result.total_recuperacion_6m (doble motor → único origen) | v4_proposal_generator.py L968 | FASE-1 |
| ROICRIII-F1 | roi_6m unificado de effective_monthly_gain a total_recuperacion_6m/(investment*6) | v4_proposal_generator.py L938 | FASE-1 |
| ROICRIII-F1 | net_benefit unificado a _maturity_result.total_recuperacion_6m - (investment*6) | v4_proposal_generator.py L969 | FASE-1 |
| ROICRIII-F1 | Bullets "Total 6 meses" redundantes eliminados del template V6 | propuesta_v6_template.md | FASE-1 |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| ROIs en documento | 1 (antes 2) | FASE-1 |
| Tests nuevos | 6 (test_financial_coherence.py) | FASE-1 |
| Tests nuevos | 9 (test_asset_semantics_validator.py) | FASE-3 |
| Regresiones | 0 detectadas (smoke OK) | FASE-1 |
| 10 failed pre-existing in test_proposal_generator.py (post-FASE-1 baseline) | 10 | FASE-3 |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| tests/test_asset_semantics_validator.py | Reescrito (9 tests: B1/B2/B6 semantics) | FASE-3 |
| .opencode/plans/ROICRIII/dependencias-fases.md | FASE-3 marcada completada | FASE-3 |
| .opencode/plans/ROICRIII/06-checklist-implementacion.md | FASE-3 verificaciones marcadas | FASE-3 |
| tests/commercial_documents/test_financial_coherence.py | Creado (6 tests: curva, ROI, net_benefit) | FASE-1 |
