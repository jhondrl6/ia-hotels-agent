# Checklist de Implementacion — Plan Unificado v2 (2026-04-06)

## Nota de Reorganizacion

Los prompts originales A/B (Review Response Rate) fueron archivados en `archived/`.
Las fases se renumeran A-E. Las fases historicas A/B del CHANGELOG (ciclo AEO) no se tocan.

## Fases del Proyecto

| # | ID | Descripcion | Estado | Sesion |
|---|----|-------------|--------|--------|
| 1 | FASE-A | Canonical Metrics + Provider Registry + Permission Modes | ✅ Completada | Sesion unificada 2026-04-06 |
| 2 | FASE-B | Document Quality Gate + Content Scrubber | ✅ Completada | Sesion 2 (2026-04-06) |
| 3 | FASE-C | Priorizacion Ponderada con Impacto Estimado | ✅ Completada | Sesion unificada 2026-04-06 |
| 4 | FASE-D | Google Search Console Integration | ✅ Completada | Sesion unificada 2026-04-06 |
| 5 | FASE-E | Micro-Content Local Generator | ✅ Completada | Sesion unificada 2026-04-06 |

---

## FASE-A: Canonical Metrics + Provider Registry + Permission Modes

**Archivo prompt**: `.opencode/plans/05-prompt-inicio-sesion-fase-A.md`
**Dependencias**: Ninguna
**Prioridad**: Media (base para FASE-D)

### Checklist
- [x] `modules/utils/canonical_metrics.py` creado
- [x] `tests/utils/test_canonical_metrics.py` — 22/22 tests passing
- [x] `config/provider_registry.yaml` creado (8 proveedores configurados)
- [x] `modules/utils/provider_registry.py` creado
- [x] `tests/utils/test_provider_registry.py` — 13/13 tests passing
- [x] `modules/utils/permission_mode.py` creado
- [x] `tests/utils/test_permission_mode.py` — 22/22 tests passing
- [x] `main.py` modificado con argumento `--permission-mode`
- [x] `python main.py --help` muestra `--permission-mode`
- [x] Backward compatible
- [x] CHANGELOG.md actualizado retroactivamente (v4.23.0)
- [x] REGISTRY.md actualizado (stats table)

---

## FASE-B: Document Quality Gate + Content Scrubber

**Archivo prompt**: `.opencode/plans/05-prompt-inicio-sesion-fase-B.md`
**Dependencias**: Ninguna obligatoria (FASE-A es nice-to-have)
**Prioridad**: ALTA — Previene documentos con errores visibles al cliente
**Origen**: Analisis comparativo seomachine #1,#2

### Checklist
- [x] `modules/postprocessors/__init__.py` creado
- [x] `modules/postprocessors/document_quality_gate.py` creado (3 blocker + 2 warning checks)
- [x] `modules/postprocessors/content_scrubber.py` creado (5 reglas, idempotente)
- [x] `modules/quality_gates/publication_gates.py` modificado — gate #6
- [x] `modules/asset_generation/asset_content_validator.py` modificado — nuevos patterns
- [x] Integracion en flujo v4complete (scrub → validate → log → delivery)
- [x] `tests/postprocessors/test_document_quality_gate.py` — 12/12 passing
- [x] `tests/postprocessors/test_content_scrubber.py` — 10/10 passing
- [x] Diagnostico de prueba limpio (sin "default", "COP COP", portugues, "0% confianza")
- [x] `python scripts/run_all_validations.py --quick` pasa
- [x] `python scripts/log_phase_completion.py --check-manual-docs` ejecutado

---

## FASE-C: Priorizacion Ponderada con Impacto Estimado

**Archivo prompt**: `.opencode/plans/05-prompt-inicio-sesion-fase-C.md`
**Dependencias**: FASE-B ✅
**Prioridad**: Alta — Mejora argumento comercial
**Origen**: Analisis comparativo seomachine #3

### Checklist
- [x] `modules/financial_engine/opportunity_scorer.py` creado (modelo 3 factores: severidad 0-40 + esfuerzo 0-30 + impacto 0-30)
- [x] `data_models/canonical_assessment.py` modificado — campo `opportunity_scores`
- [x] `modules/commercial_documents/v4_diagnostic_generator.py` modificado — scores en brechas (reemplaza composer.py)
- [x] `modules/financial_engine/calculator_v2.py` modificado — pesos dinamicos con fallback a fijos
- [x] `tests/financial_engine/test_opportunity_scorer.py` — 18/18 passing (supera criterio de 14)
- [x] Backward compatible (sin scorer = pesos fijos)
- [x] `python scripts/run_all_validations.py --quick` pasa
- [x] `python scripts/log_phase_completion.py --check-manual-docs` ejecutado

---

## FASE-D: Google Search Console Integration

**Archivo prompt**: `.opencode/plans/05-prompt-inicio-sesion-fase-D.md`
**Dependencias**: FASE-A ✅ (provider_registry), FASE-C ✅ (opportunity_scorer)
**Prioridad**: Media-Alta — Datos reales vs estimaciones
**Origen**: Analisis comparativo seomachine #4

### Checklist
- [x] `modules/analytics/google_search_console_client.py` creado (10,275 bytes)
- [x] `modules/analytics/data_aggregator.py` creado — unifica GA4 + GSC (11,447 bytes)
- [x] `modules/onboarding/add_gsc_step.py` creado — paso GSC opcional (4,319 bytes)
- [x] `modules/commercial_documents/v4_diagnostic_generator.py` modificado — datos GSC en diagnostico
- [x] `data_models/analytics_status.py` modificado — campos gsc_available, gsc_error, gsc_status_text
- [x] `config/provider_registry.yaml` modificado — entrada gsc agregada
- [x] `tests/analytics/test_google_search_console_client.py` — 14/14 passing
- [x] `tests/analytics/test_data_aggregator.py` — 19/19 passing
- [x] Graceful degradation: sin GSC = flujo normal funciona
- [x] `python scripts/run_all_validations.py --quick` pasa
- [x] `python scripts/log_phase_completion.py --check-manual-docs` ejecutado

---

## FASE-E: Micro-Content Local Generator

**Archivo prompt**: `.opencode/plans/05-prompt-inicio-sesion-fase-E.md`
**Dependencias**: FASE-B ✅ (content pasa por quality gate)
**Prioridad**: Baja — Add-on comercial
**Origen**: Analisis comparativo seomachine #5

### Checklist
- [x] `modules/asset_generation/local_content_generator.py` creado
- [x] `modules/asset_generation/asset_catalog.py` modificado — tipo `local_content_page`
- [x] `templates/local_content/` creado
- [x] `tests/asset_generation/test_local_content_generator.py` — 15/15 passing
- [x] Genera 3-5 paginas de contenido local por hotel
- [x] Contenido pasa Content Scrubber
- [x] `python scripts/run_all_validations.py --quick` pasa
- [x] `python scripts/log_phase_completion.py --check-manual-docs` ejecutado
