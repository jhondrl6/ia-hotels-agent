# Documentación Post-Proyecto — Refactor 4 Pilares SEO/GEO/AEO/IAO

**Proyecto**: AEO-IAO-PROGRESSION-REFACTOR
**Fecha creación**: 2026-04-12
**Estado**: Estructura base, se actualiza incrementalmente por fase

---

## Sección A: Módulos Nuevos

*(Se actualiza después de cada fase que crea módulos)*

### FASE-B
| Módulo | Ruta | Función |
|--------|------|---------|
| AEOSnippetTracker | `modules/auditors/aeo_snippet_tracker.py` | Verificación de featured snippets via SerpAPI |

### FASE-C
| Módulo | Ruta | Función |
|--------|------|---------|
| LLMMentionChecker | `modules/auditors/llm_mention_checker.py` | Detección de menciones en LLMs via OpenRouter/Gemini/Perplexity |

### FASE-E
| Módulo | Ruta | Función |
|--------|------|---------|
| VoiceReadinessProxy | `modules/auditors/voice_readiness_proxy.py` | Score proxy de readiness para voz |

---

## Sección B: Módulos Modificados

| Fase | Módulo | Cambio Principal |
|------|--------|-----------------|
| A | `v4_diagnostic_generator.py` | CHECKLIST redistribution, 4 scores, deprecated calcular_cumplimiento |
| A | `data_structures.py` | DiagnosticSummary ampliado con 4 pilares |
| B | `v4_diagnostic_generator.py` | _calculate_aeo_score refactorizado |
| B | `v4_comprehensive.py` | AEOSnippetTracker integrado |
| C | `v4_diagnostic_generator.py` | _calculate_iao_score restaurado |
| C | `v4_comprehensive.py` | LLMMentionChecker integrado |
| C | `data_structures.py` | Campos IAO en DiagnosticSummary |
| D | `gap_analyzer.py` | 4 gaps |
| D | `opportunity_scorer.py` | Brechas IAO/SEO |
| D | `report_builder.py` | 4 pilares completos |
| D | `benchmarks.py` | 4 benchmarks |
| D | `update_benchmarks.py` | calculate_iao_score |
| D | `v4_proposal_generator.py` | score_global |
| D | `diagnostico_v6_template.md` | Fila IAO |
| E | `v4_diagnostic_generator.py` | voice_readiness_score |
| E | `data_structures.py` | voice_readiness fields |

---

## Sección C: Decisiones de Diseño

| Decisión | Opción elegida | Razón | Contexto |
|----------|---------------|-------|----------|
| Modelo de score | OPCION A: independientes con advertencia | Cliente necesita ver todos los scores | §6.2 del contexto |
| AEO scoring | 60% checklist + 40% resultado real | Infraestructura es necesaria pero no suficiente | §6.1 del contexto |
| IAO scoring | 50% checklist + 50% resultado real | LLM mentions son la prueba definitiva de IAO | §6.1 del contexto |
| Voice measurement | PROXY (inputs), no directo (Siri/Alexa) | No existe API para consultar respuestas de voz | §5C del contexto |
| OpenAI provider | SIEMPRE via OpenRouter | Regla del proyecto, nunca SDK directo | §5D del contexto |
| CHECKLIST_IAO | REEMPLAZAR por 4 checklists | Unifica sistema dual | §6.3 del contexto |

---

## Sección D: Métricas Acumulativas

| Métrica | Pre-refactor | Post-FASE-A | Post-FASE-B | Post-FASE-C | Post-FASE-D | Post-FASE-E | Post-FASE-F |
|---------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|
| Tests totales | ~385 | ~430 | — | — | — | — | — |
| Regresiones | 0 | 0 | — | — | — | — | — |
| Módulos nuevos | 0 | 0 | 1 | 1 | 0 | 1 | 0 |
| Pilares scoring | 3 (GEO/AEO/SEO) | 4 | 4 | 4 | 4 | 4 | 4 |
| Benchmarks | 3 | 4 | 4 | 4 | 4 | 4 | 4 |
| APIs externas | 3 (Places/PageSpeed/RichResults) | 3 | 4 (+SerpAPI) | 4-7 (+OpenRouter/Gemini/Perplexity) | 4-7 | 4-7 | 4-7 |
| Costo API/hotel | $0 | $0 | $0-0.05 | $0.05-0.30 | $0.05-0.30 | $0.05-0.30 | $0.05-0.30 |

*(Llenar "—" después de completar cada fase)*

---

## Sección E: Archivos Afiliados Actualizados

| Archivo | FASE-A | FASE-B | FASE-C | FASE-D | FASE-E | FASE-F |
|---------|--------|--------|--------|--------|--------|--------|
| CHANGELOG.md | — | — | — | — | — | ✅ |
| GUIA_TECNICA.md | — | — | — | — | — | ✅ |
| REGISTRY.md | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| VERSION.yaml | — | — | — | — | — | ✅ |
| AGENTS.md | — | — | — | — | — | ✅ |
| README.md | — | — | — | — | — | ✅ |
| CONTRIBUTING.md | — | — | — | — | — | ✅ |
| DOMAIN_PRIMER.md | — | — | — | — | — | ✅ |
| SYSTEM_STATUS.md | ✅ | — | — | — | — | ✅ |

---

## Sección F: Lecciones Aprendidas

*(Se documenta durante la implementación)*

### FASE-A
- Las funciones de pilar (seo/geo/aeo/iao) son independientes y cada una retorna 0-100.
- El wrapper _extraer_elementos_de_audit() mantiene backward compat con los 12 elementos originales.
- ELEMENTO_KB_TO_PAIN_ID creció de 12 a 18 elementos (6 nuevos con default False).
- calcular_cumplimiento() deprecada pero funcional: sugerir_paquete() acepta score_global.

### FASE-B
-

### FASE-C
-

### FASE-D
-

### FASE-E
-

### General
-
