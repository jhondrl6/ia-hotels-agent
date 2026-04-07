# Documentacion Post-Proyecto — Plan Unificado v2 (2026-04-06)

## A. Modulos Nuevos

### FASE-A: Canonical Metrics + Provider Registry + Permission Modes

| Modulo | Archivo | Descripcion |
|--------|---------|-------------|
| Canonical Metrics | `modules/utils/canonical_metrics.py` | Normaliza nombres de metricas entre fuentes |
| Provider Registry | `modules/utils/provider_registry.py` | Singleton que gestiona proveedores desde YAML |
| Permission Mode | `modules/utils/permission_mode.py` | Enum y funcion para modos de aprobacion |
| Provider Config | `config/provider_registry.yaml` | Config centralizada de 8+ proveedores (incluye gsc anticipado) |

### FASE-B: Document Quality Gate + Content Scrubber

| Modulo | Archivo | Descripcion |
|--------|---------|-------------|
| Document Quality Gate | `modules/postprocessors/document_quality_gate.py` | Gate de calidad para documentos comerciales |
| Content Scrubber | `modules/postprocessors/content_scrubber.py` | Limpieza de output LLM |

### FASE-C: Opportunity Scorer

| Modulo | Archivo | Descripcion |
|--------|---------|-------------|
| Opportunity Scorer | `modules/financial_engine/opportunity_scorer.py` | Modelo ponderado 3 factores |

### FASE-D: Google Search Console

| Modulo | Archivo | Descripcion |
|--------|---------|-------------|
| GSC Client | `modules/analytics/google_search_console_client.py` | Cliente Google Search Console API |
| Data Aggregator | `modules/analytics/data_aggregator.py` | Unifica GA4 + GSC |

### FASE-E: Micro-Content Local Generator

| Modulo | Archivo | Descripcion |
|--------|---------|-------------|
| Local Content Generator | `modules/asset_generation/local_content_generator.py` | Paginas contenido local (3-5) para hoteles boutique con keywords long-tail |
| Page Template | `modules/asset_generation/templates/local_content/page_template.md` | Template de prompt LLM para contenido local |
| Keyword Guide | `modules/asset_generation/templates/local_content/keyword_selection.md` | Guia de seleccion de keywords por tipo de hotel |
| Tests | `tests/asset_generation/test_local_content_generator.py` | 15 tests unitarios |

## B. Modulos Modificados

| Fase | Archivo | Cambio |
|------|---------|--------|
| FASE-A | `main.py` | Argumento `--mode` |
| FASE-B | `modules/quality_gates/publication_gates.py` | Gate #6 content_quality_gate |
| FASE-B | `modules/asset_generation/asset_content_validator.py` | Agregar "default" a PLACEHOLDER_PATTERNS |
| FASE-B | `main.py` | Inyectar scrub en v4complete |
| FASE-C | `data_models/canonical_assessment.py` | Campo `opportunity_scores` |
| FASE-C | `modules/commercial_documents/composer.py` | Inyectar scores en brechas |
| FASE-C | `modules/financial_engine/calculator_v2.py` | Pesos dinamicos |
| FASE-D | `modules/onboarding/onboarding_flow.py` | Paso GSC verification |
| FASE-D | `modules/commercial_documents/composer.py` | Inyectar datos GSC |
| FASE-D | `config/provider_registry.yaml` | Activar entrada gsc |
| FASE-E | `modules/asset_generation/asset_catalog.py` | Tipo `local_content_page` |

## C. Configurados por Fase

| Fase | Estado | Archivos Nuevos | Archivos Modificados | Tests Nuevos |
|------|--------|-----------------|---------------------|--------------|
| FASE-A | ⏳ Pendiente | 4 | 1 | 22 |
| FASE-B | ⏳ Pendiente | 3 | 2 | 22 |
| FASE-C | ⏳ Pendiente | 1 | 3 | 14 |
| FASE-D | ⏳ Pendiente | 2 | 3 | 18 |
| FASE-E | ✅ Completado | 4 | 1 | 15 |

## D. Metricas Acumulativas

| Metrica | A (est) | B (est) | C (est) | D (est) | E (real) | Total acumulado |
|---------|---------|---------|---------|---------|----------|-----------------|
| Tests nuevos | 22 | 22 | 14 | 18 | 15 | 91 |
| Archivos nuevos | 4 | 3 | 1 | 2 | 4 | 14 |
| Archivos modificados | 1 | 2 | 3 | 3 | 1 | 10 |

## E. Archivos Afiliados — Estado FASE-E

- [x] CHANGELOG.md — Entrada [4.25.0] agregada con detalle FASE-E
- [x] VERSION.yaml — Bump 4.24.0 -> 4.25.0, codename "FASE-E: Micro-Content Local Generator"
- [x] REGISTRY.md — Actualizado por log_phase_completion.py (2026-04-06)
- [x] docs/GUIA_TECNICA.md — Notas tecnicas v4.25.0 agregadas
- [ ] AGENTS.md — Agregar postprocessors a tabla de modulos + GSC a analytics
- [ ] docs/CONTRIBUTING.md — Verificar que referencia FASE-E en REGISTRY.md sea consistente
