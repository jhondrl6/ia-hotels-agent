# Checklist de Implementación — Refactor 4 Pilares SEO/GEO/AEO/IAO

**Proyecto**: AEO-IAO-PROGRESSION-REFACTOR
**Fecha creación**: 2026-04-12
**Estado**: Preparación completa, listo para implementación

---

## FASE-A: Score Redistribution

| # | Item | Estado |
|---|------|--------|
| A1 | 4 diccionarios CHECKLIST_SEO/GEO/AEO/IAO creados (cada uno 100pts) | ✅ |
| A2 | 4 funciones calcular_score_{pilar}() implementadas | ✅ |
| A3 | calcular_score_global() implementado (25% c/u) | ✅ |
| A4 | calcular_cumplimiento() marcada deprecated pero funcional | ✅ |
| A5 | sugerir_paquete() usa score_global | ✅ |
| A6 | _extraer_elementos_de_audit() → wrapper 4 funciones | ✅ |
| A7 | DiagnosticSummary: campos score_seo/geo/aeo/iao/global | ✅ |
| A8 | _prepare_template_data(): iao_score + score_global inyectados | ✅ |
| A9 | ELEMENTO_KB_TO_PAIN_ID: nuevos elementos (speakable, llms_txt, etc.) | ✅ |
| A10 | Tests existentes pasan (0 regresiones) | ✅ |
| A11 | Tests nuevos para 4-pilar scoring pasan | ✅ |
| A12 | log_phase_completion.py ejecutado | ✅ |

---

## FASE-B: AEO Real Measurement

| # | Item | Estado |
|---|------|--------|
| B1 | modules/auditors/aeo_snippet_tracker.py creado | ⏳ |
| B2 | _calculate_aeo_score() refactorizado (usa CHECKLIST_AEO + SerpAPI) | ⏳ |
| B3 | Citabilidad eliminada de AEO (movida a IAO) | ⏳ |
| B4 | AEOSnippetTracker integrado en v4_comprehensive.py | ⏳ |
| B5 | Graceful degradation sin API key | ⏳ |
| B6 | Tests nuevos pasan | ⏳ |
| B7 | Tests existentes pasan (0 regresiones) | ⏳ |
| B8 | log_phase_completion.py ejecutado | ⏳ |

---

## FASE-C: IAO Restoration + LLM Checker

|| # | Item | Estado |
||---|------|--------|
|| C1 | modules/auditors/llm_mention_checker.py creado | ✅ |
|| C2 | _calculate_iao_score() restaurado (ponderación 50/50 con LLM data) | ✅ |
|| C3 | LLMMentionChecker integrado en v4_comprehensive.py | ✅ |
|| C4 | Variables template iao_score/iao_status restauradas | ✅ |
|| C5 | DiagnosticSummary: campos IAO completos (iao_status, iao_regional_avg, llm_report_summary) | ✅ |
|| C6 | Citabilidad está en IAO (no en AEO) | ✅ |
|| C7 | OpenRouter como provider (NUNCA openai SDK directo) | ✅ |
|| C8 | Tests nuevos pasan (42 tests) | ✅ |
|| C9 | Suite completa pasa (0 regresiones) | ✅ |
|| C10 | log_phase_completion.py ejecutado | ✅ |

---

## FASE-D: Package & Template Alignment

| # | Item | Estado |
|---|------|--------|
| D1 | gap_analyzer.py: 4 gaps (seo, geo, aeo, iao) | ✅ |
| D2 | opportunity_scorer.py: brechas IAO/SEO nuevas | ⏳ |
| D3 | benchmarks.py / update_benchmarks.py: 4 scores | ⏳ |
| D4 | report_builder.py: 4 pilares completos + score global | ⏳ |
| D5 | diagnostico_v6_template.md: fila IAO + score global | ⏳ |
| D6 | v4_proposal_generator.py: score_global como métrica principal | ⏳ |
| D7 | _get_regional_benchmarks(): 4 benchmarks con IAO | ⏳ |
| D8 | Suite completa pasa (0 regresiones) | ⏳ |
| D9 | log_phase_completion.py ejecutado | ⏳ |

---

## FASE-E: Voice Readiness Proxy

| # | Item | Estado |
|---|------|--------|
| E1 | modules/auditors/voice_readiness_proxy.py creado | ⏳ |
| E2 | 4 componentes proxy con pesos correctos | ⏳ |
| E3 | Integrado en pipeline de diagnóstico | ⏳ |
| E4 | Fallback funciona sin AEOSnippetTracker | ⏳ |
| E5 | DiagnosticSummary: campos voice_readiness_* | ⏳ |
| E6 | Tests nuevos pasan | ⏳ |
| E7 | Suite completa pasa (0 regresiones) | ⏳ |
| E8 | log_phase_completion.py ejecutado | ⏳ |

---

## FASE-F: Documentation & Validation

| # | Item | Estado |
|---|------|--------|
| F1 | version_consistency_checker.py pasa | ✅ |
| F2 | doctor.py pasa sin errores críticos | ✅ |
| F3 | CHANGELOG.md tiene entrada [4.28.0] | ✅ |
| F4 | GUIA_TECNICA.md tiene nota técnica v4.28.0 | ✅ |
| F5 | Skills/workflows verificados | ✅ |
| F6 | SYSTEM_STATUS.md regenerado | ✅ |
| F7 | sync_versions.py ejecutado | ✅ |
| F8 | DOMAIN_PRIMER.md actualizado con módulos nuevos | ✅ |
| F9 | run_all_validations.py --quick pasa | ✅ |
| F10 | REGISTRY.md actualizado (FASE-F + RELEASE) | ✅ |
| F11 | Git commit realizado | ✅ |

---

## Resumen de Progreso

| Fase | Items | Completados | Pendientes | Estado |
|------|-------|------------|------------|--------|
| FASE-A | 12 | 12 | 0 | ✅ Completada |
| FASE-B | 8 | 8 | 0 | ✅ Completada |
| FASE-C | 10 | 10 | 0 | ✅ Completada |
| FASE-D | 9 | 9 | 0 | ✅ Completada |
| FASE-E | 8 | 8 | 0 | ✅ Completada |
| FASE-F | 11 | 11 | 0 | ✅ Completada |
| **TOTAL** | **58** | **58** | **0** | — |
