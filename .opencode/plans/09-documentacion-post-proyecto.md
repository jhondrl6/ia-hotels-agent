# Plan de Documentación Post-Proyecto — FEATURE-CONFIG-EXTRACTION

**Versión:** 1.0.0
**Proyecto:** FEATURE-CONFIG-EXTRACTION (v4.38.0)
**Fases:** 10 (FASE-CONFIG-1 a FASE-RELEASE-4.38.0)

---

## Estructura del Documento

Este plan se completa INCREMENTALMENTE después de cada fase:

- **Sección A:** Módulos nuevos (por fase)
- **Sección B:** Archivos modificados (por fase)
- **Sección C:** Tests acumulativos
- **Sección D:** Métricas acumulativas
- **Sección E:** Archivos afiliados actualizados

---

## Sección A: Módulos Nuevos

| Fase | Módulo/Archivo | Descripción |
|------|---------------|-------------|
| CONFIG-2 | `config/fallbacks.yaml` | Fallbacks de scores con flags estimated |
| CONFIG-3A | `config/pricing.yaml` | TIER_CONFIG, GATE ratios, floor_price unificado |
| CONFIG-3B | `config/scenarios.yaml` | Recovery factors, weights, degradation, OTA shifts, ia_boost |
| CONFIG-3B | `config/financial_defaults.yaml` | DEFAULTS financieros (12 valores) |
| CONFIG-4 | `config/commercial.yaml` | ROI cap, break_even, descuentos, garantías, planes |
| CONFIG-5 | `config/regional_benchmarks.yaml` | Pain narratives + umbrales scoring multi-región |
| CONFIG-7 | `evidence/fase-config-7/ANALISIS_HALLAZGOS.md` | Análisis de resolución post-v4complete |
| CONFIG-8 | `tests/config/test_config_pricing.py` | Tests de migración pricing |
| CONFIG-8 | `tests/config/test_config_scenarios.py` | Tests de migración scenarios |
| CONFIG-8 | `tests/config/test_config_fallbacks.py` | Tests de migración fallbacks |
| CONFIG-8 | `tests/config/test_config_commercial.py` | Tests de migración commercial |
| CONFIG-8 | `tests/config/test_config_benchmarks.py` | Tests de migración benchmarks |
| CONFIG-8 | `tests/config/test_config_fallback.py` | Tests de fallback (YAML ausente/corrupto) |
| CONFIG-8 | `tests/config/test_config_schema.py` | Tests de schema validation |
| CONFIG-8 | `tests/config/test_config_integration.py` | Tests de integración |

---

## Sección B: Archivos Modificados

| Fase | Archivo | Cambio |
|------|---------|--------|
| CONFIG-1 | `scripts/sync_config.yaml` | CR-1: Corrección doble escape L101-103 + consistencia "v" |
| CONFIG-1 | `scripts/sync_versions.py` | CR-2: Validación post-reemplazo L131-133 |
| CONFIG-2 | `modules/commercial_documents/v4_proposal_generator.py` | H-11/12/13: Fallbacks → YAML + flag estimated |
| CONFIG-2 | `modules/commercial_documents/v4_diagnostic_generator.py` | H-27: voice_readiness → YAML + flag estimated |
| CONFIG-3A | `modules/financial_engine/pricing_calculator.py` | H-19, N-12, H-18a: TIER_CONFIG + GATEs → YAML |
| CONFIG-3A | `modules/commercial_documents/v4_proposal_generator.py` | H-18b: floor_price unificado a 1.2M |
| CONFIG-3B | `modules/financial_engine/scenario_calculator.py` | H-21, H-22: OTA shifts + ia_boost → YAML |
| CONFIG-3B | `modules/financial_engine/loss_projector.py` | H-20: degradation_rate → YAML |
| CONFIG-3B | `modules/utils/financial_factors.py` | N-11, N-11b: DEFAULTS → YAML |
| CONFIG-3B | `modules/commercial_documents/v4_proposal_generator.py` | H-14, H-17, N-01: recovery + weights + pain_ratio → YAML |
| CONFIG-4 | `modules/commercial_documents/v4_proposal_generator.py` | CR-5: Eliminar _build_guarantees_section() + H-15/16 + N-04 → YAML |
| CONFIG-4 | `modules/commercial_documents/v4_diagnostic_generator.py` | H-26: Plan stubs → YAML |
| CONFIG-4 | `modules/commercial_documents/templates/propuesta_v6_template.md` | H-23/24/25: Variables comerciales + garantías unificadas |
| CONFIG-5 | `modules/commercial_documents/v4_diagnostic_generator.py` | N-03/05/06/07/08/09/10: Pain narratives + umbrales → YAML |
| CONFIG-5 | `modules/commercial_documents/v4_proposal_generator.py` | N-02: Confidence thresholds → YAML |
| CONFIG-6 | `config/settings.yaml` | Depurado de duplicados, header legacy |
| CONFIG-6 | `modules/analytics/profound_client.py` | DEPRECADO: DeprecationWarning + docstring |
| CONFIG-6 | `modules/analytics/semrush_client.py` | DEPRECADO: DeprecationWarning + docstring |
| CONFIG-6 | `modules/analytics/data_aggregator.py` | DEPRECADO: DeprecationWarning + docstring |
| CONFIG-6 | `modules/delivery/generators/aeo_metrics_gen.py` | DEPRECADO: DeprecationWarning + docstring |
| CONFIG-6 | `modules/analytics/__init__.py` | Limpiado: solo exporta GA4 + GSC |
| CONFIG-6 | `data_models/analytics_status.py` | Corregido: is_any_missing() solo GA4+GSC; campos deprecados |
| CONFIG-6 | `modules/commercial_documents/v4_diagnostic_generator.py` | Docstring _check_analytics_status() corregido |
| CONFIG-8 | `scripts/doctor.py` | Verificación de integridad de config files |

---

## Sección C: Tests Acumulativos

| Fase | Tests nuevos | Archivos de test | Total acumulado |
|------|-------------|-----------------|-----------------|
| CONFIG-1 | 3 | sync_versions tests | 3 |
| CONFIG-2 | 5 | test_config_fallbacks | 8 |
| CONFIG-3A | 5 | test_config_pricing | 13 |
| CONFIG-3B | 6 | test_config_scenarios, test_config_financial | 19 |
| CONFIG-4 | 5 | test_config_commercial | 24 |
| CONFIG-5 | 5 | test_config_benchmarks | 29 |
| CONFIG-6 | 10 | test_config_reconnect, test_deprecation, test_analytics_status | 39 |
| CONFIG-8 | 30+ | 8 archivos en tests/config/ | 59+ |

---

## Sección D: Métricas Acumulativas

| Métrica | Valor (post-CONFIG-7) |
|---------|----------------------|
| Hardcodes extraídos | 31/31 |
| Causas raíz corregidas | 7/7 |
| Módulos huérfanos deprecados | 4/4 (847 líneas) |
| Archivos YAML creados | 6 |
| Archivos Python modificados | 12 |
| Templates modificados | 1 |
| Scripts modificados | 2 |
| Tests nuevos | 69+ |
| Coherence (Amazilia) | [COMPLETAR post-CONFIG-7] |
| Publication status | [COMPLETAR post-CONFIG-7] |
| Regresiones | 0 |

---

## Sección E: Archivos Afiliados Actualizados

| Documento | Actualizado en | Acción |
|-----------|---------------|--------|
| `VERSION.yaml` | FASE-RELEASE-4.38.0 | 4.37.0 → 4.38.0 |
| `CHANGELOG.md` | FASE-RELEASE-4.38.0 | Entrada [4.38.0] |
| `docs/GUIA_TECNICA.md` | FASE-RELEASE-4.38.0 | Nota técnica v4.38.0 |
| `docs/CONTRIBUTING.md` | FASE-RELEASE-4.38.0 | Auto (sync) |
| `AGENTS.md` | FASE-RELEASE-4.38.0 | Auto (sync) |
| `README.md` | FASE-RELEASE-4.38.0 | Auto (sync) |
| `.cursorrules` | FASE-RELEASE-4.38.0 | Auto (sync) |
| `docs/contributing/REGISTRY.md` | Cada fase | log_phase_completion.py |
| `.agent/SYSTEM_STATUS.md` | FASE-RELEASE-4.38.0 | doctor.py --status |
| `DOMAIN_PRIMER.md` | FASE-RELEASE-4.38.0 | doctor.py --context |

---

## Checklist de Completitud del Plan de Documentación

Después de ejecutar TODAS las fases y FASE-RELEASE, verificar:

- [ ] Fases registradas en REGISTRY.md (10 entradas: CONFIG-1 a RELEASE)
- [ ] Versiones sincronizadas (sync_versions.py corregido)
- [ ] CHANGELOG formato correcto (secciones requeridas)
- [ ] GUIA_TECNICA actualizada (nota técnica por fase)
- [ ] Validaciones pasan (run_all_validations.py --quick: 4/4)
- [ ] Doctor sin errores (doctor.py --status)
- [ ] Evidencia guardada en evidence/fase-config-{1..8}/
- [ ] ANALISIS_HALLAZGOS.md con veredicto final
- [ ] git commit realizado
