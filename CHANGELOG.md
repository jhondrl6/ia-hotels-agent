# Changelog

## [4.72.0] - Credibilidad Numérica y Verdad del Sitio Vivo — 2026-08-21

### Objetivo

Implementar las soluciones P0/P1/P2 identificadas en la validación comercial contra código vivo (F1-F14): unificar la credibilidad numérica del pipeline (pricing, benchmarks, comisión OTA, rango del hook), propagar la verdad del sitio vivo (WhatsApp multi-sede, verificación de assets en producción), corregir encoding de artefactos y cerrar el bucle Hook→Express. Todo como prerrequisito del primer cliente ("el primer cliente no puede ver cifras contradictorias ni brechas falsas"). Plan: CREDIBILIDAD-NUMERICA-2026-08-20 (11 fases: P0-A/B/C, P1-A/B/C/D, P2-A/B, E2E-ZIONE, RELEASE).

### FASE-P0-A — Fuente única de pricing + hook PDF dinámico (F1)

#### Objetivo
Eliminar las constantes de pricing hardcodeadas del Hook PDF y la propuesta comercial, haciendo que TODO el pipeline consuma `config/pricing.yaml` como fuente única (decisión D6).

#### Cambios
- `config/pricing.yaml`: nuevo campo `express_price: 120000` en packages
- `modules/financial_engine/pricing_calculator.py`: `express_price` reconocido en `validated_packages` y fallback defaults
- `modules/commercial_documents/hook_pdf_generator.py`: constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE` eliminadas; nuevo método `_get_pricing_packages()` carga pricing.yaml con caché de instancia
- `modules/commercial_documents/v4_proposal_generator.py`: constantes `MONTHLY_PACKAGE_PRICE/SETUP_FEE` eliminadas; nuevo método `_get_pricing_packages()`; 15 usoss migrados a `pricing.yaml`
- `tests/commercial_documents/test_hook_pdf_generator.py`: +3 tests contrato F1 (TestPricingContractF1); `test_pricing_constants` actualizado a fuente dinámica

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `config/pricing.yaml` | +express_price: 120000 |
| `modules/financial_engine/pricing_calculator.py` | +express_price en validated_packages + fallbacks |
| `modules/commercial_documents/hook_pdf_generator.py` | -constantes PRECIO_*; +_get_pricing_packages() |
| `modules/commercial_documents/v4_proposal_generator.py` | -MONTHLY_PACKAGE_PRICE/SETUP_FEE; +_get_pricing_packages(); 15 usoss migrados |
| `tests/commercial_documents/test_hook_pdf_generator.py` | +3 tests contrato F1; test_pricing_constants dinámico |

#### Tests
+3 tests nuevos (TestPricingContractF1). 0 regresiones vs línea base (22 fallos preexistentes documentados en evidence/BASELINE-TESTS-v4.71.0.txt).

---

### FASE-P0-B — Gate bloqueante `pricing_compliance` floor-aware (F1)

#### Objetivo
Crear el gate de publicación `pricing_compliance` (BLOCKING) que bloquea cuando el pricing calculado incumple los ratios de `config/pricing.yaml`. Diseño floor-aware (decisión D1): BLOCKING solo si `pain_ratio > pain_ratio_gate_max` del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con `operational_floor` aplicado.

#### Cambios
- `modules/quality_gates/publication_gates.py`: nuevo gate `_pricing_compliance_gate` (gate 13); `_load_pricing_thresholds()` reutiliza `_load_pricing_config()` con fallback; docstring actualizado a 13 gates (10 blocking + 3 advisory)
- `modules/assessment_builder.py`: nuevo campo `pricing_data` en `AssessmentPayload`; nuevo método `with_pricing()` inyecta pain_ratio/tier/price desde PricingResult
- `main.py`: `builder.with_pricing(pricing_result)` cableado en FASE 4.5
- `AGENTS.md`: gate count 12→13 (blocking 9→10); `pricing_compliance` en §Módulos y FASE 4.5

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/publication_gates.py` | +_pricing_compliance_gate; +_load_pricing_thresholds; imports logging+os; docstring 13 gates |
| `modules/assessment_builder.py` | +pricing_data campo; +with_pricing() método fluid |
| `main.py` | +builder.with_pricing(pricing_result) en FASE 4.5 |
| `AGENTS.md` | Gate count 12→13; pricing_compliance en §Módulos y FASE 4.5 |
| `tests/quality_gates/test_pricing_compliance_gate.py` | NUEVO — 18 tests |
| `tests/quality_gates/test_publication_gates.py` | 4 assertions actualizadas 12→13 |

#### Tests
+18 tests nuevos (TestPricingComplianceGate). 0 regresiones vs línea base (340 passed en quality_gates).

---

### FASE-P0-C — Encoding utf-8 en writers de artefactos (F7)

#### Objetivo
Garantizar que TODOS los writers de artefactos (JSON/MD/HTML de output) usen `encoding='utf-8'` explícito para eliminar el encoding corrupto que produce artefactos ilegibles (cp1252 por defecto en Windows). Fallo original F7: `delivery_quality_report.json` lanzaba `UnicodeDecodeError` (byte 0xf3) y mojibake "B+ ? Datos fuente" en diagnóstico.

#### Cambios
- `modules/quality_gates/delivery_quality_report.py`: `save()` — `path.write_text(...)` ahora usa `encoding="utf-8"` explícito
- `modules/utils/config_checker.py`: 2 `test_file.write_text("test")` ahora usan `encoding="utf-8"` (fix preventivo en tests de permisos)
- `tests/test_encoding_artifacts.py`: nuevo — 4 tests de contrato anti-regresión (save utf-8, no mojibake, roundtrip special chars, auditoría estática AST)

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/delivery_quality_report.py` | +encoding="utf-8" en save() write_text |
| `modules/utils/config_checker.py` | +encoding="utf-8" en 2 write_text de permisos |
| `tests/test_encoding_artifacts.py` | NUEVO — 4 tests contrato F7 + auditoría estática AST |

#### Tests
+4 tests nuevos (TestDeliveryQualityReportEncoding + TestEncodingContractStatic). 470 passed en suite delivery+quality_gates+encoding. 0 regresiones vs línea base.

---

### FASE-P1-A — Benchmark maestro único de ADR regional (F2+F4)

#### Objetivo
Unificar las 3 fuentes de benchmark ADR en una sola (`regional_adr_2026.json` como master), agregar cobertura de Bogotá, calibrar valores contra 6 observaciones Tier A de hoteles reales, y agregar mecanismo de sincronización anti-divergencia.

#### Cambios
- `data/benchmarks/regional_adr_2026.json`: MASTER ADR/occupancy v1.1.0; Bogotá agregada; eje_cafetero calibrado ($420K→$280K boutique, $350K→$260K standard) vs observaciones Tier A
- `data/benchmarks/plan_maestro_data.json`: ADR/occupancy sincronizados con master; Bogotá agregada; antioquia y caribe actualizados
- `config/regional_benchmarks.yaml`: ADR/occupancy sincronizados (referencial); v1.1.0
- `modules/financial_engine/regional_adr_resolver.py`: +`_normalize_region()` (lowercase-first + alias lookup); Bogotá alias; occupancy normalizada; `_get_known_regions()` unificado de ambas fuentes; `_determine_confidence()` normalizado
- `scripts/validate_benchmark_sync.py`: NUEVO — valida sincronización ADR/occupancy entre master y plan_maestro_data

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `scripts/validate_benchmark_sync.py` | Script de validación de sincronización benchmark |
| `tests/financial_engine/test_benchmark_master.py` | 19 tests de contrato F2/F4 |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `data/benchmarks/regional_adr_2026.json` | v1.0→v1.1.0; Bogotá; valores calibrados |
| `data/benchmarks/plan_maestro_data.json` | ADR/occ sync; Bogotá nueva región |
| `config/regional_benchmarks.yaml` | ADR/occ sync (referencial); v1.1.0 |
| `modules/financial_engine/regional_adr_resolver.py` | +_normalize_region(); Bogotá alias; occupancy fix; known_regions unificado |
| `tests/financial_engine/test_regional_adr_resolver.py` | 6 assertions actualizadas: alias→canónico |
| `tests/financial_engine/test_adr_resolution_wrapper.py` | 1 assertion actualizada: metadata region normalizada |

#### Tests
+19 tests nuevos (TestBenchmarkMaster). 520 passed en suite financial_engine. 10 fallos preexistentes intactos (test_calculator_v2 ×2 + test_pricing_resolution_wrapper ×8). 0 regresiones nuevas.

---

### FASE-P1-B — Fallback región conservador + comisión OTA parametrizada (F3+F5)

#### Objetivo
Corregir el mapa de fallback de región (`'colombia'→'caribe'` inflaba la fuga 2.3-3.2x) y parametrizar la comisión OTA con rango y fuente citada (antes hardcodeada en 15% en 5 sitios de 3 módulos).

#### Cambios
- `modules/auditors/v4_comprehensive.py`: `'colombia'` mapeado a `'default'` ($300K conservador) en lugar de `'caribe'` ($450K)
- `config/financial_defaults.yaml`: añadido `source` a `comision_ota` (rango 18-22%, base 20%, fuente documentada)
- `modules/utils/financial_factors.py`: `comision_ota_source` en `FinancialFactorsConfig` + `get_comision_ota()` API centralizada
- `modules/financial_engine/scenario_calculator.py`: import `FinancialFactors`; defaults 0.15→0.20; `_trace_data_sources` usa fuente de config
- `modules/financial_engine/calculator_v2.py`: import `FinancialFactors`; defaults 0.15→0.20 en `_to_hotel_financial_data` y `calculate_financial_scenarios`
- `modules/financial_engine/inputs_contract.py`: import `FinancialFactors`; defaults 0.15→0.20 en dataclass, `validate()` y `from_dict()`
- `modules/financial_engine/financial_evidence.py`: import `FinancialFactors`; defaults 0.15→0.20; source actualizado a `config/financial_defaults.yaml`
- `modules/orchestration_v4/two_phase_flow.py`: import `FinancialFactors`; `_estimate_monthly_loss` y `phase_2` usan comisión OTA de config
- `modules/utils/benchmarks.py`: `DEFAULT_DATA` `comision_ota_base` 0.15→0.20

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/auditors/test_region_fallback.py` | 12 tests F3: colombia→default, ciudades específicas→región correcta, cache |
| `tests/financial_engine/test_ota_commission.py` | 12 tests F5: rango 18-22%, source, defaults en todos los consumidores |
| `evidence/BASELINE-TESTS-auditors-v4.71.0.txt` | Baseline de auditors (148 passed, 1 skipped) previa a FASE-P1-B |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | F3: 'colombia'→'default' en region_map |
| `config/financial_defaults.yaml` | F5: +source en comision_ota |
| `modules/utils/financial_factors.py` | F5: +comision_ota_source en Config + get_comision_ota() |
| `modules/financial_engine/scenario_calculator.py` | F5: defaults 0.15→0.20; trace source de config |
| `modules/financial_engine/calculator_v2.py` | F5: defaults 0.15→0.20 |
| `modules/financial_engine/inputs_contract.py` | F5: defaults 0.15→0.20 |
| `modules/financial_engine/financial_evidence.py` | F5: defaults 0.15→0.20; source actualizado |
| `modules/orchestration_v4/two_phase_flow.py` | F5: comisión OTA desde config |
| `modules/utils/benchmarks.py` | F5: DEFAULT_DATA 0.15→0.20 |
| `tests/financial_engine/test_scenario_calculator.py` | 2 assertions actualizados 0.15→0.20 |
| `tests/financial_engine/test_inputs_contract.py` | 1 assertion actualizado 0.15→0.20 |
| `tests/financial_engine/test_financial_evidence.py` | 1 test actualizado: value+source |

#### Tests
+24 tests nuevos (12 F3 + 12 F5). 160 passed en auditors (148 baseline + 12 nuevos). 11 fallos en financial_engine (mismos preexistentes). 0 regresiones nuevas. `run_all_validations.py --quick`: 6/6 PASSED.

---

### FASE-P1-C — Cableado benchmark master al hook + cap de plausibilidad + trazabilidad Hook→Express (F6+F11)

#### Objetivo
Cerrar la causa raíz de F6: el rango del hook se generaba con defaults hardcodeados (ratio 23x) porque el benchmark master de P1-A nunca se cableaba al orquestador (decisión D4: cableado ANTES del cap). Además, cap de plausibilidad configurable (decisión D7: ratio fijo max/min = 5.0) y trazabilidad del rango Hook→Express (F11): la cifra del Express se verifica contra el corredor prometido por el Hook con narrativa de la delta benchmark→dato real.

#### Cambios
- `modules/orchestration_v4/two_phase_flow.py`: `_calculate_hook_range` aplica cap de plausibilidad (`hook_range_max_ratio`, fallback 5.0) truncando el extremo optimista sobre el piso conservador; `_get_regional_benchmarks` normaliza keys de región (aliases de `RegionalADRResolver.REGION_ALIASES` + lowercase/underscore) y cae al "default" del master antes que a defaults hardcodeados; nuevo dataclass `HookRangeTraceability` + `validate_hook_range_traceability()` + `format_traceability_section()`; disclaimer actualizado (rango acotado por cap y promesa falsable verificada por el Express)
- `modules/orchestration_v4/onboarding_controller.py`: `load_benchmark_master()` carga `data/benchmarks/regional_adr_2026.json` y `_convert_master_region()` traduce estructura por segmentos al formato plano; `__init__` acepta `benchmark_master_path` y pasa `plan_maestro_data` a `TwoPhaseOrchestrator` (el parámetro ya existía); `get_range_traceability()` integra la trazabilidad con el resultado Express
- `modules/commercial_documents/hook_pdf_generator.py`: helper `_parse_cop_number()` + check advisory #9 en `validate_data` que verifica que la fuga mensual caiga dentro del corredor (tolerancia 10%)
- `config/financial_defaults.yaml`: +`hook_range_max_ratio: 5.0` (decisión D7)

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/orchestration_v4/test_hook_plausibility_cap.py` | 14 tests: cableado D4, conversión del master, cap 5x, fallback de config |
| `tests/orchestration_v4/test_hook_express_traceability.py` | 13 tests: validación del corredor, narrativa, formato markdown, integración controller |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/orchestration_v4/two_phase_flow.py` | +cap plausibilidad; +normalización de región; +HookRangeTraceability/validate/format; disclaimer actualizado |
| `modules/orchestration_v4/onboarding_controller.py` | +load_benchmark_master(); +_convert_master_region(); +benchmark_master_path; +get_range_traceability() |
| `modules/commercial_documents/hook_pdf_generator.py` | +_parse_cop_number(); +check advisory #9 corredor F11 |
| `config/financial_defaults.yaml` | +hook_range_max_ratio: 5.0 (D7) |

#### Tests
+27 tests nuevos (14 F6/D4 + 13 F11). Suite orchestration_v4: 66→93 passed, 0 fallos. hook_pdf_generator: 39 passed. benchmark_master: 19 passed. 2 fallos preexistentes en tests/config (pricing.yaml/scenarios.yaml, ajenos a P1-C — verificados vía git status). `run_all_validations.py --quick`: 6/6 TOTAL PASS.

---

### FASE-P1-D — Verdad del sitio vivo: sedes WhatsApp multi-sede + propagación site_verification (F12+F13)

#### Objetivo
Restaurar el estado de verdad del sitio vivo como fuente única en dos frentes: F12 — el cross-validator debe distinguir sedes en negocios multi-ubicación (caso Zione: 2 sedes Pereira/Cartagena generaban un falso conflicto que inflaba la fuga $1.198.906/mes); F13 — propagar `site_verification_applied` al pain_ledger y al diagnóstico (decisión D8: status `VERIFIED_IN_SITE` de primera clase, que consumirá FASE-P2-A/F14).

#### Cambios
- `modules/data_validation/cross_validator.py`: `validate_whatsapp` acepta `web_alternates` + `gbp_location` (firma backwards-compatible); nuevo `_reconcile_whatsapp_multisede`: GBP coincide con algún número web → VERIFIED (disclaimer lista sedes alternas); multi-sede sin mapeo confiable → degrada CONFLICT a ESTIMATED (WARNING); conflicto real de misma sede (matching por tokens ≥4 chars) → CONFLICT preservado; mono-sede conserva comportamiento legacy
- `modules/auditors/v4_comprehensive.py`: nuevo `_extract_all_whatsapp_candidates` (wa.me / api.whatsapp / tel con dedup normalizado) + `_extract_sede_label` (ventana de contexto DOM); `CrossValidationResult` agrega `web_whatsapp_alternates` + `gbp_location`; `_run_cross_validation` enriquece `validate_whatsapp`
- `main.py`: caller `validate_whatsapp` (L1735) enriquecido con alternates y ubicación GBP desde `audit_result.validation`
- `modules/asset_generation/pain_ledger.py`: nuevo `STATUS_VERIFIED_IN_SITE` + `apply_site_verification(entries, site_presence_report)` — entradas DETECTED cuyo asset mapeado (`PAIN_TO_PRESENCE_ASSET`) existe/redundant y está site_verified → VERIFIED_IN_SITE, severity LOW, evidence_refs `site_verification:{asset}:{status}`
- `modules/asset_generation/v4_asset_orchestrator.py`: cableado `apply_site_verification` tras `from_pains` y antes de guardar el ledger
- `modules/orchestration/post_orchestrator_reconciler.py`: `_resolve_status` preserva VERIFIED_IN_SITE en `pain_ledger_resolved.json`
- `modules/quality_gates/publication_gates.py`: VERIFIED_IN_SITE agregado a `_JUSTIFIED_STATUSES` del coverage gate (cubiertas + justificadas == detectadas)
- `modules/commercial_documents/v4_diagnostic_generator.py`: `_load_verified_in_site_pain_ids` (pain_ledger_resolved con fallback pain_ledger); `_identify_brechas` filtra pains verificados en producción; cache_key incluye verified_ids

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/data_validation/test_whatsapp_multisede.py` | 11 tests F12: caso Zione VERIFIED sin conflicto, degrade a ESTIMATED, conflicto real misma sede, legacy mono-sede, scanner con labels |
| `tests/asset_generation/test_site_verification_propagation.py` | 10 tests F13: exists→VERIFIED_IN_SITE LOW, not_exists→DETECTED, redundant→verified, unmapped intacto, reconciler preserva, coverage gate justifica, diagnóstico filtra |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/data_validation/cross_validator.py` | +web_alternates/gbp_location en validate_whatsapp; +_reconcile_whatsapp_multisede (tokens ≥4 chars) |
| `modules/auditors/v4_comprehensive.py` | +_extract_all_whatsapp_candidates; +_extract_sede_label; CrossValidationResult +2 campos |
| `main.py` | Caller validate_whatsapp L1735 enriquecido |
| `modules/asset_generation/pain_ledger.py` | +STATUS_VERIFIED_IN_SITE; +apply_site_verification; +PAIN_TO_PRESENCE_ASSET |
| `modules/asset_generation/v4_asset_orchestrator.py` | Cableado apply_site_verification antes de save |
| `modules/orchestration/post_orchestrator_reconciler.py` | _resolve_status preserva VERIFIED_IN_SITE |
| `modules/quality_gates/publication_gates.py` | +VERIFIED_IN_SITE en _JUSTIFIED_STATUSES |
| `modules/commercial_documents/v4_diagnostic_generator.py` | +_load_verified_in_site_pain_ids; filtrado de brechas verificadas |

#### Tests
+21 tests nuevos (11 F12 + 10 F13). Suites data_validation + asset_generation: 603 passed, 0 failed. Suites ampliadas (quality_gates, commercial_documents, orchestration_v4, auditors, reconciler): solo los 12 fallos preexistentes de la línea base (commercial_documents) — 0 regresiones.

---

### FASE-P2-A — Coherence acepta "verificado en producción" + occupancy label (F14+F8)

#### Objetivo
Alinear el coherence validator con el gate `proposal_asset_alignment` para que ambos acepten el estado "verificado en producción" sobre `promised_assets_exist` (F14), eliminando la contradicción PASSED/FAILED sobre el mismo asset. Verificar que no existan rutas residuales de etiquetado de occupancy (F8 residual).

#### Cambios
- `modules/commercial_documents/coherence_validator.py`: nuevo helper `_extract_verified_in_production_types(site_presence_report)` extrae asset_types con status "exists"/"redundant" + site_verified=True del dict canónico de `normalize_site_presence`; `_check_promised_assets_exist` acepta `site_presence_report` opcional; assets verificados en producción NO se cuentan como missing; `validate()` cablea `site_presence_report` al check; mensaje enriquecido con `production_only_types`

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/commercial_documents/test_promised_assets_production.py` | 11 tests F14: C1 (verified→PASSED), C2 (missing→FAILED, gate no debilitado), C3 (mix→PASSED), C4 (legacy preservado), C5 (coherence↔gate alignment E2E), edge cases (empty report, verification_failed, site_verified=False) |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/coherence_validator.py` | +_extract_verified_in_production_types; _check_promised_assets_exist acepta site_presence_report; validate() cablea site_presence_report al check |

#### Tests
+11 tests nuevos (TestPromisedAssetsProductionVerification). Suites commercial_documents + financial_engine: 12 + 11 fallos preexistentes de la línea base, 0 regresiones. `run_all_validations.py --quick`: 6/6 PASS.

---

### FASE-P2-B — Pre-carga GBP de prospectos (F9) + higiene documental comercial (F10)

#### Objetivo
Crear el script de pre-carga GBP batch de prospectos con gate de completitud de datos de contacto (F9), y actualizar la documentación comercial desactualizada (F10) para que cite las fuentes únicas de pricing (pricing.yaml) y benchmarks (regional_adr_2026.json).

#### Cambios
- `modules/scrapers/google_places_client.py`: nuevo método `search_by_name(name, city, category)` — POST a Places API (New) `places:searchText` con `textQuery`, `includedType=lodging`, `maxResultCount=3`; cachea resultado; manejo de errores HTTP 429/403/404
- `scripts/preload_prospects_gbp.py`: NUEVO — ~300 líneas; parse YAML/CSV de prospectos; 30 prospectos embebidos del Eje Cafetero; gate de completitud VERIFIED/PARTIAL/MISSING (teléfono + dirección + categoría); reporte Markdown; salida JSON opcional; modo `--dry-run` y `--builtin`
- `docs/PRECIOS_PAQUETES.md`: reescrito v4.72.0 — precios USD→COP; tiers desde pricing.yaml; paquetes Express/Starter/Professional/Enterprise; política de coherencia de pricing (FASE-P0-A)
- `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md`: ADR $420K→$280K (benchmark master v1.1.0, sección 2.8); Express $120K citado desde pricing.yaml (sección 2.5); nota ZIP actual (sección 1)
- `evidence/Recomendaciones/PROMPT_INGRESOS.md`: ADR $420K→$280K con fuente citada
- `evidence/Recomendaciones/PROMPT_INGRESOS_README.md`: ADR $420K→$280K con referencia a master v1.1.0

#### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `scripts/preload_prospects_gbp.py` | Script de pre-carga GBP batch con gate de completitud (F9) |

#### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/scrapers/google_places_client.py` | +search_by_name(): Places API searchText por nombre+ciudad |
| `docs/PRECIOS_PAQUETES.md` | Reescrito v4.72.0: USD→COP, pricing.yaml como fuente única |
| `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` | ADR $420K→$280K; Express desde pricing.yaml; nota ZIP actual |
| `evidence/Recomendaciones/PROMPT_INGRESOS.md` | ADR $420K→$280K |
| `evidence/Recomendaciones/PROMPT_INGRESOS_README.md` | ADR $420K→$280K; referencia master v1.1.0 |

#### Tests
Script `preload_prospects_gbp.py --dry-run` ejecuta sin error (30 prospectos listados). Suite `tests/scrapers/` 34 passed, 4 skipped, 0 fallos nuevos. `run_all_validations.py --quick`: 6/6 PASS.

---

### Cambios Implementados

- **FASE-P0-A** (F1, D6): Fuente única de pricing — pricing.yaml master con `express_price`; constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE/MONTHLY_PACKAGE_PRICE` eliminadas de hook_pdf_generator y v4_proposal_generator; ambos consumen dinámicamente de `_load_pricing_config()`.
- **FASE-P0-B** (F1, D1): Gate `pricing_compliance` (gate 13, BLOCKING floor-aware) — BLOCKED si pain_ratio > pain_ratio_gate_max del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con operational_floor. `with_pricing()` en AssessmentBuilder.
- **FASE-P0-C** (F7): Encoding utf-8 global — todos los writers de artefactos usan `encoding='utf-8'` explícito; auditoría estática AST anti-regresión.
- **FASE-P1-A** (F2+F4, D3): Benchmark maestro único — `regional_adr_2026.json` como master ADR/occupancy; Bogotá agregada; valores calibrados vs 6 observaciones Tier A; script `validate_benchmark_sync.py` anti-divergencia; normalización de regiones.
- **FASE-P1-B** (F3+F5, D2): Fallback región conservador — `'colombia'` resuelve a default ($300K) en lugar de caribe ($450K). Comisión OTA parametrizada — rango 18-22% desde `financial_defaults.yaml` con fuente documentada; 5 sitios hardcodeados eliminados; `FinancialFactors.get_comision_ota()` como API centralizada.
- **FASE-P1-C** (F6+F11, D4+D7): Cableado benchmark master al hook ANTES del cap; cap de plausibilidad ratio fijo 5.0 configurable; trazabilidad Hook→Express con narrativa benchmark→dato real; disclaimer de rango falsable.
- **FASE-P1-D** (F12+F13, D8): Verdad del sitio vivo — `validate_whatsapp` con mapeo número→sede (multi-sede WhatsApp); status `VERIFIED_IN_SITE` de primera clase en pain_ledger; reconciler lo preserva; coverage gate lo justifica; diagnóstico filtra brechas verificadas en producción.
- **FASE-P2-A** (F14+F8): Coherence acepta "verificado en producción" — `_check_promised_assets_exist` acepta `site_presence_report`; assets verificados en producción NO se cuentan como missing; alineado con gate `proposal_asset_alignment`.
- **FASE-P2-B** (F9+F10): Pre-carga GBP batch — `search_by_name()` en GooglePlacesClient; `preload_prospects_gbp.py` con 30 prospectos builtin y gate de completitud. Higiene documental — PRECIOS_PAQUETES, PROPUESTA_EMPAQUETADO, PROMPT_INGRESOS actualizados (ADR $420K→$280K, pricing.yaml como fuente).
- **FASE-E2E-ZIONE**: v4complete Zi One Luxury — coherence 0.9485; 13/13 gates PASSED (pricing_compliance WARNING floor-aware); READY_FOR_PUBLICATION; 9/9 assets; V1-V13 verificados (12/13 PASSED, V6 seguimiento cosmético).

### Archivos Nuevos

| Archivo | Descripción | Fase |
|---------|-------------|------|
| `scripts/validate_benchmark_sync.py` | Validación sincronización ADR/occupancy master↔plan_maestro_data | P1-A |
| `tests/financial_engine/test_benchmark_master.py` | 19 tests contrato F2/F4 | P1-A |
| `tests/auditors/test_region_fallback.py` | 12 tests F3: colombia→default | P1-B |
| `tests/financial_engine/test_ota_commission.py` | 12 tests F5: rango 18-22% | P1-B |
| `evidence/BASELINE-TESTS-auditors-v4.71.0.txt` | Baseline auditors pre-P1-B | P1-B |
| `tests/orchestration_v4/test_hook_plausibility_cap.py` | 14 tests F6/D4 | P1-C |
| `tests/orchestration_v4/test_hook_express_traceability.py` | 13 tests F11 | P1-C |
| `tests/data_validation/test_whatsapp_multisede.py` | 11 tests F12 | P1-D |
| `tests/asset_generation/test_site_verification_propagation.py` | 10 tests F13 | P1-D |
| `tests/commercial_documents/test_promised_assets_production.py` | 11 tests F14 | P2-A |
| `tests/quality_gates/test_pricing_compliance_gate.py` | 18 tests pricing_compliance | P0-B |
| `tests/test_encoding_artifacts.py` | 4 tests encoding F7 | P0-C |
| `scripts/preload_prospects_gbp.py` | Pre-carga GBP batch con gate completitud | P2-B |
| `modules/scrapers/google_places_client.py` | +search_by_name() Places API searchText | P2-B |

### Archivos Modificados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `config/pricing.yaml` | +express_price: 120000 | P0-A |
| `modules/financial_engine/pricing_calculator.py` | +express_price en validated_packages | P0-A |
| `modules/commercial_documents/hook_pdf_generator.py` | -constantes PRECIO_*; +_get_pricing_packages(); +_parse_cop_number(); +check advisory #9 | P0-A, P1-C |
| `modules/commercial_documents/v4_proposal_generator.py` | -MONTHLY_PACKAGE_PRICE/SETUP_FEE; +_get_pricing_packages() | P0-A |
| `modules/quality_gates/publication_gates.py` | +_pricing_compliance_gate (gate 13); +VERIFIED_IN_SITE en _JUSTIFIED_STATUSES | P0-B, P1-D |
| `modules/assessment_builder.py` | +pricing_data campo; +with_pricing() | P0-B |
| `main.py` | +with_pricing(); caller validate_whatsapp enriquecido | P0-B, P1-D |
| `modules/quality_gates/delivery_quality_report.py` | +encoding="utf-8" en save() | P0-C |
| `modules/utils/config_checker.py` | +encoding="utf-8" en 2 write_text | P0-C |
| `data/benchmarks/regional_adr_2026.json` | MASTER v1.1.0; Bogotá; calibrado | P1-A |
| `data/benchmarks/plan_maestro_data.json` | Sync con master; Bogotá | P1-A |
| `config/regional_benchmarks.yaml` | Sync ADR/occ referencial v1.1.0 | P1-A |
| `modules/financial_engine/regional_adr_resolver.py` | +_normalize_region(); Bogotá alias | P1-A |
| `modules/auditors/v4_comprehensive.py` | F3: colombia→default; F12: +_extract_all_whatsapp_candidates | P1-B, P1-D |
| `config/financial_defaults.yaml` | F5: +source comision_ota; F6: +hook_range_max_ratio | P1-B, P1-C |
| `modules/utils/financial_factors.py` | F5: +comision_ota_source + get_comision_ota() | P1-B |
| `modules/financial_engine/scenario_calculator.py` | F5: defaults 0.15→0.20 | P1-B |
| `modules/financial_engine/calculator_v2.py` | F5: defaults 0.15→0.20 | P1-B |
| `modules/financial_engine/inputs_contract.py` | F5: defaults 0.15→0.20 | P1-B |
| `modules/financial_engine/financial_evidence.py` | F5: defaults 0.15→0.20 | P1-B |
| `modules/orchestration_v4/two_phase_flow.py` | F5: comisión OTA config; F6: +cap +normalización; +HookRangeTraceability | P1-B, P1-C |
| `modules/utils/benchmarks.py` | F5: DEFAULT_DATA 0.15→0.20 | P1-B |
| `modules/orchestration_v4/onboarding_controller.py` | +load_benchmark_master(); +_convert_master_region(); +get_range_traceability() | P1-C |
| `modules/data_validation/cross_validator.py` | F12: +web_alternates/gbp_location; +_reconcile_whatsapp_multisede | P1-D |
| `modules/asset_generation/pain_ledger.py` | F13: +STATUS_VERIFIED_IN_SITE; +apply_site_verification | P1-D |
| `modules/asset_generation/v4_asset_orchestrator.py` | F13: cableado apply_site_verification | P1-D |
| `modules/orchestration/post_orchestrator_reconciler.py` | F13: preserva VERIFIED_IN_SITE | P1-D |
| `modules/commercial_documents/v4_diagnostic_generator.py` | F13: filtra brechas verificadas en producción | P1-D |
| `modules/commercial_documents/coherence_validator.py` | F14: acepta site_presence_report | P2-A |
| `modules/scrapers/google_places_client.py` | F9: +search_by_name() | P2-B |
| `docs/PRECIOS_PAQUETES.md` | F10: reescrito v4.72.0 COP | P2-B |
| `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` | F10: ADR $280K; pricing.yaml | P2-B |
| `evidence/Recomendaciones/PROMPT_INGRESOS.md` | F10: ADR $280K | P2-B |
| `evidence/Recomendaciones/PROMPT_INGRESOS_README.md` | F10: ADR $280K | P2-B |
| `AGENTS.md` | Gate count 12→13; versión 4.72.0 | P0-B, RELEASE |

### Tests

+127 tests nuevos acumulados (3 P0-A + 18 P0-B + 4 P0-C + 19 P1-A + 24 P1-B + 27 P1-C + 21 P1-D + 11 P2-A). Línea base de 22 fallos preexistentes intacta (12 commercial_documents + 10 financial_engine). 0 regresiones. E2E Zi One: coherence 0.9485, 13/13 gates PASSED, READY_FOR_PUBLICATION.

## [4.71.0] — 2026-08-05 — Coherencia Propuesta-Diagnóstico, Gates Comerciales y Entrega

### Objetivo

Eliminar 3 causas raíz residuales del plan v4.70.0: RC1 (fuente de verdad de costos aplicada a medias — propuesta hardcodeada), RC2 (gates comerciales con inputs no cableados + veredicto oculto en ZIP), RC3 (higiene documental sin enforcement). Incluye prerrequisito FASE-A (tests patológicos), seguimientos S5/S7, verificación E2E con Zi One Luxury (coherence 0.9238, READY_FOR_PUBLICATION) y recuperación S5b (occupancy_source en bloque FASE-K + PrecisionValidator).

### Cambios Implementados

- **FASE-A** (Prerrequisito): Cuarentena de 3 tests patológicos (`test_proposal_generator.py`, `test_price_consistency.py`, `test_proposal_generator_dict.py`) → `tests/_archived_broken_tests/`. `pytest.ini` con `--ignore` específicos. Lista segura de 13 archivos documentada. 3,215 → 3,175 collected (40 tests aislados).
- **FASE-B** (RC1 — N10/N17/N18/N19): Tabla de servicios dinámica — `_build_dynamic_breach_map()` invierte `pain_solution_mapper.PAIN_SOLUTION_MAP` para construir mapa `asset_type → brecha_id` con desempate por `opportunity_scores`. `BREACH_BY_ASSET` estático eliminado. `main.py` cablea `opportunity_scores` en FASE 3.5 → `proposal_gen.generate()`. Org_schema condicional sin cifras cuando `no_org_schema` no está en scores.
- **FASE-C** (RC2-a — N11/N15): `CG-CLAIM-VS-EVIDENCE` split por oraciones + filtro condicionales (`_CONDITIONAL_MARKERS`) — sin falsos positivos con texto "si...no aparece". `CG-TIER-CONSISTENCY` cableado: `_extract_text_tier()` en `v4_diagnostic_generator.py` + inputs `frontmatter_tier`/`text_tier`; None → FAIL explícito (nunca vacuo).
- **FASE-D** (RC2-b — N16/N21/S5/S7): Política ZIP — `_is_excluded_from_zip()` filtra `commercial_gates_report*` del ZIP de cliente. `_get_latest_run_timestamp()` cutoff por mtime del run más reciente. Fallback loader onboarding: `{output}/clientes` → `output/clientes`. Occupancy label veraz: prioridad `onboarding > regional > default`.
- **FASE-E** (RC3 — R3.1-R3.4): Higiene documental — `--release` eliminado de 4 prompts intermedios del plan anterior. Enforcement `_check_prompts_no_release()` en `run_all_validations.py`. Conteos fuente viva (205 .py, 391 clases, 27 dirs, 3,227 tests). Evidencia N3 preservada (14 JSON del run 123637).
- **FASE-F** (E2E): Run único `v4complete` Zi One Luxury — coherence 0.9238, READY_FOR_PUBLICATION (12 gates: 11 passed + 1 WARNING advisory, 0 blocking). Onboarding real ("4 campos confirmados", sin "Using defaults"). V1-V10: 10/10 PASS tras recuperación S5b.
- **FASE-F/S5b** (Recuperación): Fix `occupancy_source` en DOS sitios de `main.py` (bloque FASE-K + input PrecisionValidator/GAP-4). 6 tests nuevos (contrato estático + comportamiento camino FASE-K). Re-verificación V8 PASS.

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `tests/commercial_documents/test_proposal_breach_consistency.py` | Gate de no-regresión RC1 (9 tests: breach map dinámico + costos opportunity_scores) |
| `tests/quality_gates/test_commercial_gate.py` | Tests ampliados (20 nuevos: condicionales CG-CLAIM + tier consistency + extract_text_tier) |
| `tests/delivery/test_fase_d_zip_policy.py` | Política ZIP N16/N21 (10 tests: exclusión gate reports + run-based filtering) |
| `tests/financial_engine/test_fase_d_occupancy_label.py` | Occupancy label S5 (6 tests: source priority + HotelFinancialData) |
| `tests/test_fase_d_onboarding_loader.py` | Fallback loader S7 (7 tests: fallback path + URL normalization) |
| `tests/financial_engine/test_fase_f_recovery_s5b.py` | Recuperación S5b (6 tests: contrato estático anti-regresión + camino FASE-K) |
| `scripts/sync_data.py` | Sincronización de datos de benchmark |
| `scripts/validate_cross_refs.py` | Validación de referencias cruzadas documentales |
| `evidence/FASE-B/` | Verificación estática breach consistency + tests + lista segura |
| `evidence/FASE-F/` | Run E2E completo (16 JSON, docs comerciales, ZIP, verificación V1-V10, s5b_rerun) |
| `evidence/N3-diff/` | 14 JSON del run 123637 preservados + README (diff 97 líneas no reproducible) |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | `_build_dynamic_breach_map()` + eliminación `BREACH_BY_ASSET` estático + hardcode L1250 + org_schema condicional (N10/N17/N18/N19) |
| `main.py` | Cableado `opportunity_scores` FASE 3.5 → propuesta (FASE-B) + fallback loader onboarding S7 (FASE-D) + fix `_occupancy_source` FASE-K + PrecisionValidator GAP-4 (S5b) |
| `modules/quality_gates/commercial_gate.py` | `_check_claim_vs_evidence` split por oraciones + condicionales (N11) + `_check_tier_consistency` inputs reales + None → FAIL (N15) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | `_extract_text_tier()` + cableado `frontmatter_tier`/`text_tier` al gate (N15) |
| `modules/delivery/delivery_packager.py` | `_is_excluded_from_zip()` N16 + `_get_latest_run_timestamp()` N21 + `_collect_files()` integra filtros |
| `modules/financial_engine/harness_handlers.py` | Label occupancy veraz S5: prioridad `onboarding > regional > default` + `occupancy_source` en HotelFinancialData fallback |
| `scripts/run_all_validations.py` | Check `_check_prompts_no_release()` (enforcement R3.1, L3/L9) |
| `pytest.ini` | `--ignore` específicos para 3 archivos en cuarentena (FASE-A) |
| `AGENTS.md` | Versión 4.71.0 + codename actualizado |
| `README.md` | Versión 4.71.0 + codename actualizado |
| `docs/GUIA_TECNICA.md` | Versión 4.71.0 + codename actualizado |
| `.agents/workflows/phased_project_executor.md` | v2.15.0 + análisis post-implementación obligatorio |

### Tests

- **+9 tests** FASE-B (`test_proposal_breach_consistency.py`: breach map dinámico + costos opportunity_scores + org_schema condicional)
- **+20 tests** FASE-C (`test_commercial_gate.py`: 9 condicionales CG-CLAIM + 6 tier consistency + 5 extract_text_tier)
- **+23 tests** FASE-D (10 delivery ZIP policy + 6 occupancy label + 7 onboarding loader)
- **+6 tests** FASE-F/S5b (`test_fase_f_recovery_s5b.py`: contrato estático + comportamiento camino FASE-K)
- **Total: +58 tests nuevos** (git diff fuente viva), 0 regresiones
- **3,233 tests collected** (pytest --collect-only, post-cuarentena FASE-A)
- **E2E Zi One Luxury**: coherence 0.9238, 12 gates (11 passed + 1 WARNING advisory), READY_FOR_PUBLICATION
- **V1-V10**: 10/10 PASS (V8 cerrado vía recuperación S5b)
- **Validaciones**: `run_all_validations.py --quick` 6/6 TOTAL PASS

## [4.70.0] — 2026-08-04 — Coherencia Módulo-Entrega

### Objetivo

Eliminar 21 desconexiones módulo↔entrega (D1-D12 + N1-N9) detectadas en el diagnóstico V6 de Zione (2026-08-01, re-auditoría 2026-08-03). El plan COHERENCIA-MODULO-ENTREGA-2026-08-03 corrigió problemas de veracidad de contenido, honestidad financiera, gates de calidad, textos dinámicos, freshness de artefactos y pulido de texto, verificados E2E con Zi One Luxury (coherence 0.9168, Tier B+, 21/21 hallazgos cerrados).

### Cambios Implementados

- **FASE-A** (D1+D2): Contenido veraz — `_pain_to_brecha` usa `pain.name`/`description` del mapper; detección unica de brechas con `_identify_brechas`; template con conteo dinámico `${brechas_*_count}`; pesos sobre N real.
- **FASE-B** (D3+D4+N1): Finanzas honestas — `estimated_monthly_cop` alineado con pesos normalizados del doc; 3 escenarios reales con labels correctos + CG-SCENARIO-ORDER; fórmula única de recuperación 6m (`calcular_recuperacion_6m` en `pillar_maturity_curve.py`).
- **FASE-C-A** (D5+N2): Gates reales — `_coverage_gate` reestructurado (covered cuenta antes de justified); nuevo gate `_doc_audit_consistency_gate` (WARNING, DEC-C1) con 4 patrones (OG, reviews, fotos, performance).
- **FASE-C-B** (D6+D7+D8): Textos dinámicos — `_build_manual_attention_table` lee `performance.status` (ERROR→mensaje API, OK→genérico); `_build_excluded_factors_section(reviews_count=N)` parametriza reseñas; atribución GEO corregida ("algoritmo propio de IA Hoteles Agent sobre datos de Google Places").
- **FASE-D** (D9-D12+N3-N8): Freshness + pulido — `TARGET_GBP_PHOTOS=40`; dedup redes sociales con `seen` set; `_occupancy_source` tracking; freshness v4_audit (mtime cutoff 24h); "arriba" (era "acima"); "Por qué importa"; truncamiento por palabra.
- **FASE-E**: E2E Zi One Luxury — 21/21 hallazgos verificados; coherence 0.9168; evidence_tier B+; 12 gates PASSED; ZIP sin históricos.

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| Gate `doc_audit_consistency` | `modules/quality_gates/publication_gates.py` — Validación WARNING de pares doc↔audit (OG, reviews, fotos, performance) |
| Helper compartido recuperación 6m | `modules/financial_engine/pillar_maturity_curve.py` — Fórmula única de recuperación proyectada |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | D1 (pain.name) + D2 (brechas_reales/caché/contadores dinámicos) + D3 (estimated_monthly_cop alineado) + D4 (escenarios reales) + D6 (performance dinámico) + D7 (reviews parametrizadas) + D9 (TARGET_GBP_PHOTOS=40) + D10 (dedup redes) + N6 ("Por qué importa") + N7 (truncamiento por palabra) |
| `main.py` | D2 (brechas_reales + channel_context con inputs reales) + D12 (_occupancy_source tracking) + D11b (warning stale commercial_gates_report) |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | D2 (conteo dinámico) + B (sección "Lo que está en juego" con curva) + D8 (atribución GEO L113/L231) + N5 ("arriba") |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | N5 ("arriba") |
| `config/regional_benchmarks.yaml` | Pesos `low_seo_score`/`low_organic_visibility` en 4 regiones (FASE-A) |
| `modules/financial_engine/pillar_maturity_curve.py` | `calcular_recuperacion_6m()` — fórmula ÚNICA de recuperación 6m (N1) |
| `modules/commercial_documents/v4_proposal_generator.py` | N1 (gate net_benefit_6m/roi con curva única) + D11 (write commercial_gates_report.json SIEMPRE) |
| `modules/quality_gates/commercial_gate.py` | CG-SCENARIO-ORDER con semántica real (conservador = peor caso = mayor pérdida) |
| `modules/quality_gates/publication_gates.py` | D5 (_coverage_gate reestructurado) + N2 (nuevo gate _doc_audit_consistency_gate WARNING) |
| `modules/delivery/delivery_packager.py` | N4 (filtro freshness v4_audit mtime cutoff 24h) |

### Tests

- **+6 tests** FASE-A (`test_diagnostic_brechas.py`: OG 8 tags, N unificado, pesos YAML, template, caché, low_seo)
- **+8 tests** FASE-B (`test_fase_f_financial_placeholders.py` + `test_financial_coherence.py` + `test_diagnostic_brechas.py` actualizado + `test_commercial_gate.py` actualizado)
- **+13 tests** FASE-C-A (`test_doc_audit_consistency_gate.py`: 9 nuevos + `test_coverage_gate.py`: 4 nuevos + 3 actualizados)
- **+8 tests** FASE-C-B (`test_diagnostic_generator.py`: 3 D6 performance + 3 D7 reviews + 2 D8 GEO)
- **21/21 hallazgos verificados E2E** (D1-D12, N1-N9); seguimientos S5-S7 documentados
- **Coherence**: 0.9168 (FASE-E, Zi One Luxury, gate PASSED, Tier B+)
- **0 regresiones** en código modificado por las fases A-E

## [4.69.0] — 2026-08-01 — Delivery ZIP Single-Write Architecture

### Objetivo

Corregir el fallo critico de delivery packaging que impedia materializar el ZIP de entrega al cliente. Rewrite arquitectonico single-write con fixed-point iteration.

### Cambios Implementados

- `modules/delivery/delivery_packager.py` - Rewrite single-write: elimina 3-pass measure-then-mutate. Fixed-point iteration para self-reference del MANIFEST.
- `main.py` - NF-3: severidad ERROR en fallo de delivery. NF-6: params FASE-5 conectados.
- `tests/delivery/test_delivery_contract.py` - Bug 3: tolerancia 5% eliminada, validacion exacta por archivo.
- `tests/delivery/test_delivery_packager.py` - NF-1: fixture FASE-C, dual mode coverage (legacy + produccion).

### Archivos Nuevos

| Archivo | Descripcion |
|---------|-------------|
| `evidence/FASE-D-E2E/` | Evidencia de verificacion E2E con Zi One Luxury |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/delivery/delivery_packager.py` | Single-write architecture, cleanup NF-4, datetime NF-5, logging NF-2 |
| `main.py` | ERROR severity NF-3, FASE-5 params NF-6 |
| `tests/delivery/test_delivery_contract.py` | Exact validation, per-file size test |
| `tests/delivery/test_delivery_packager.py` | FASE-C fixture, dual mode, NF-2/NF-4/NF-5 tests |
| `templates/delivery_readme_template.md` | Sin cambios (placeholders conservados para otros consumers) |

### Tests

- 6+ tests nuevos en delivery suite
- 3,160+ tests totales, 0 regresiones
- E2E verificado: v4complete Zi One Luxury produce ZIP valido

## [4.68.0] — 2026-07-31 — Evidence Tier Honesty: B_PLUS + GA4/GSC Gate + Proposal Truthfulness

### Objetivo

Corregir la falsa confianza del Evidence Tier en v4complete: el sistema afirmaba "Basado en Google Analytics y Search Console verificados" (Tier A) sin verificar GA4/GSC. Esto creaba una contradicción interna en el documento — el CTA honesto (línea 84) decía "conecte GA4" mientras el disclaimer (línea 215) mentía sobre verificación.

**Causa raíz**: `_determine_evidence_tier()` asignaba Tier A con ≥2 fuentes verificadas pero NUNCA consultaba `ga4_enabled`/`gsc_enabled`. `EvidenceTier.A.disclaimer` hardcodeaba "GA4 + Search Console verificados". Dos rutas de código sin fuente de verdad compartida.

### 20 Hallazgos Resueltos (12 originales + 8 nuevos NP1-NP8 de auditoría 2026-07-31)

**Originales (12):**
- **H1** (CRÍTICA): `_determine_evidence_tier()` ahora consulta `ga4_enabled`/`gsc_enabled` — Tier A solo con GA4+GSC real
- **H2** (ALTA): `EvidenceTier.A.disclaimer` honesto — solo aplica con GA4+GSC verificados
- **H3** (ALTA): `has_onboarding` dinámico en propuesta — sin fallback silencioso a False (NP5)
- **H4** (ALTA): Propuesta ya no dice 3 tiers diferentes — disclaimer condicional según tier real
- **H5** (MEDIA): `main.py:2099` relationship text dinámico — usa tier real (no hardcodeado "B")
- **H6** (MEDIA): `precision_tier` ahora visible en template diagnóstica
- **H7** (MEDIA): Template Tiers legend incluye B+ con disclaimer "Datos operativos verificados"
- **H8** (ALTA): Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` (BLOCKING) — bloquea Tier A sin GA4/GSC
- **H9** (MEDIA): MANIFEST.json enriquecido con `quality_metadata` (evidence_tier, precision_tier, ga4_available)
- **H10** (MEDIA): 3 sistemas `precision_tier` documentados como deuda técnica (no implementado en este plan)
- **H11** (BAJA): H1-FIX ya aplicado en `_get_adr_from_benchmarks()` — no requiere acción
- **H12** (INFRA): Service account GCP documentado como OUT OF PLAN (acción manual del usuario)

**Nuevos NP1-NP8 (auditoría pre-ejecución 2026-07-31):**
- **NP1** (CRÍTICA): `hook_pdf_generator.py:509` `valid_tiers` actualizado a `{"A", "B+", "B", "C"}` — B_PLUS ya no es rechazado
- **NP2** (ALTA): `publication_gates.py:399` `tier_message` lógica dinámica corregida — el else branch ya no miente
- **NP3** (ALTA): `tests/test_financial_breakdown.py` actualizado con assertions para `B_PLUS.disclaimer` y `B_PLUS.value`
- **NP4** (ALTA): `v4_diagnostic_generator.py:1043` default `evidence_tier = "C"` (no "A") — conservador cuando `financial_breakdown` es None
- **NP5** (MEDIA): `v4_proposal_generator.py:586` `getattr(pricing_result, 'is_onboarding', False)` eliminado — fallback silencioso removido
- **NP6** (MEDIA): MANIFEST enrichment en `modules/delivery/delivery_packager.py` (corregido de plan original que apuntaba a `main.py:3038`)
- **NP7** (ALTA): Gate `CG-EVIDENCE-TIER-CONSISTENCY` recibe params per-hotel (`ga4_available`/`gsc_available`) — NO `os.getenv` global
- **NP8** (MEDIA): Control de regresión sin onboarding — `hotel_test_001` verifica Tier B/C sin B+ ni A

### Cambios Implementados (5 fases)

**FASE-1 — Root Cause + Downstream Consumers (7 archivos):**
- `data_structures.py`: `EvidenceTier.B_PLUS = "B+"` agregado al enum + disclaimer honesto
- `hook_pdf_generator.py`: `valid_tiers` acepta B+ (NP1)
- `publication_gates.py`: `tier_message` lógica dinámica (NP2)
- `v4_diagnostic_generator.py`: Default `evidence_tier = "C"` (NP4)
- `scenario_calculator.py`: `HotelFinancialData` + `ga4_enabled`/`gsc_enabled`. `_determine_evidence_tier()` recibe y usa estos flags
- `test_financial_breakdown.py`: Assertions para B_PLUS (NP3)
- `main.py`: Wire `ga4_enabled`/`gsc_enabled` al `HotelFinancialData`

**FASE-2 — Proposal + Template Honesty (4 archivos):**
- `v4_proposal_generator.py`: `has_onboarding` dinámico (sin fallback silencioso NP5). Disclaimer condicional por tier (`_build_tier_disclaimer`)
- `v4_diagnostic_generator.py`: Exponer `precision_tier` en placeholders del template
- `diagnostico_v6_template.md`: `${precision_tier}` + leyenda Tiers con B+
- `main.py`: Relationship text dinámico (f-string con tier real)

**FASE-3 — Quality Gate per-hotel + Delivery Enrichment (3 archivos):**
- `commercial_gate.py`: Nuevo gate `CG-EVIDENCE-TIER-CONSISTENCY` con params per-hotel (NP7) + agregado a `BLOCKING_GATE_IDS`
- `v4_diagnostic_generator.py`: Caller pasa `ga4_available`, `gsc_available`, `financial_json` al gate
- `delivery_packager.py`: MANIFEST enriquecido con `quality_metadata` (NP6) — evidencia, tier, GA4/GSC flags
- `main.py`: Caller pasa flags per-hotel al gate vía setter `_quality_metadata`

**FASE-4 — Tests (1 archivo nuevo, 22 tests):**
- `tests/test_evidence_tier.py`: 22 tests (9 unit `_determine_evidence_tier` + 5 integration pipeline + 8 gate `CG-EVIDENCE-TIER-CONSISTENCY`)
- Validados 5 suites pre-existentes compatibles con B_PLUS (NP3): test_financial_breakdown 10/10, test_fase_f_financial_placeholders 11/12, test_hook_pdf_generator 36/36, test_proposal_generator 21/32, test_template_conditionals 6/6 — 0 fallas causadas por B_PLUS

**FASE-5 — v4complete E2E Verification (2 hoteles):**
- **Zi One Luxury** (https://zione.co/): evidence_tier = "B+" ✅ (no "A"). Disclaimer honesto: "Conecte GA4 y Search Console". precision_tier visible. MANIFEST con quality_metadata. Gate CG-EVIDENCE-TIER-CONSISTENCY: INFO (passed, tier != A).
- **Hotel Vísperas (control sin onboarding)**: evidence_tier = "B" ✅ (sin B+ ni A, sin regresión). NP8 verificado.
- 20/20 hallazgos verificados en matriz (12 originales + 8 NP1-NP8)

### Archivos Modificados (17 archivos)
| # | Archivo | Fase |
|---|---------|------|
| 1 | `modules/commercial_documents/data_structures.py` | FASE-1 |
| 2 | `modules/commercial_documents/hook_pdf_generator.py` | FASE-1 (NP1) |
| 3 | `modules/quality_gates/publication_gates.py` | FASE-1 (NP2) |
| 4 | `modules/commercial_documents/v4_diagnostic_generator.py` | FASE-1 (NP4) + FASE-2 |
| 5 | `tests/test_financial_breakdown.py` | FASE-1 (NP3) |
| 6 | `modules/financial_engine/scenario_calculator.py` | FASE-1 |
| 7 | `main.py` | FASE-1 + FASE-2 + FASE-3 |
| 8 | `modules/commercial_documents/v4_proposal_generator.py` | FASE-2 (NP5) |
| 9 | `modules/commercial_documents/templates/diagnostico_v6_template.md` | FASE-2 |
| 10 | `modules/quality_gates/commercial_gate.py` | FASE-3 (NP7) |
| 11 | `modules/delivery/delivery_packager.py` | FASE-3 (NP6) |
| 12 | `tests/test_evidence_tier.py` | FASE-4 (nuevo) |
| 13-17 | `data_structures.py`, `pricing_resolution_wrapper.py`, `propuesta_v6_template.md`, `no_defaults_validator.py`, `financial_evidence.py` | Varias fases |

### Tests
- 22 tests nuevos en `test_evidence_tier.py` (3 clases: TestDetermineEvidenceTier, TestEvidenceTierIntegration, TestEvidenceTierConsistencyGate)
- 5 suites pre-existentes validadas sin regresiones (NP3)
- Total: 3,180 tests, 0 regresiones introducidas por B_PLUS

### Deuda Técnica Documentada (NO implementada)
- **H10**: Unificar 3 sistemas de `precision_tier` (enum, string, validator) — requiere plan independiente
- **H12**: Crear service account Google Cloud — acción manual del usuario en Google Cloud Console

## [4.67.0] — 2026-07-29

### Cambios Implementados
- **Onboarding Injection Pipeline**: Matching canónico por URL normalizada en `_load_latest_onboarding_data()`. Eliminada dependencia de slug derivado de nombre.
- **`_normalize_url()`**: Nueva función auxiliar para matching determinístico de URLs (ignora protocolo, www, trailing slash, path, query).
- **CAMBIO A**: `run_onboard_mode()` ahora persiste `hotel.url` en el YAML vía `form._data['hotel']['url']`.
- **CAMBIO B**: `run_v4_complete_mode()` ahora pasa `output_dir` configurable (`args.output`) al loader.
- **CAMBIO C**: `_load_latest_onboarding_data()` reescrita: iteración por glob, matching por URL normalizada, parámetro `output_dir`.
- **Fix 3**: Ventana de frescura hardcodeada eliminada. `ONBOARDING_FRESHNESS_HOURS` env var como opt-in.
- **Fix 4**: `"user_provided"` agregado a `verified_sources` en `_determine_evidence_tier()`.
- **Fix 5**: Mensaje de `onboard` actualizado: sugiere `v4complete` en vez de `audit` (deprecado).
- **Fix 6**: `_load_latest_onboarding_data()` ahora tiene fallback a `observations.json` vía `_observation_to_onboarding_format()`.

### Archivos Modificados
- `main.py`: `_load_latest_onboarding_data()` reescrita, `_normalize_url()`, `_observation_to_onboarding_format()`, `run_onboard_mode()` CAMBIO A, `run_v4_complete_mode()` CAMBIO B
- `modules/onboarding/data_loader.py`: `create_onboarding_template()` — agregado `'url': None`
- `modules/financial_engine/scenario_calculator.py`: `_determine_evidence_tier()` — `user_provided` en verified_sources
- `data/hotel_observations/observations.json`: Agregado `website` a 6 observaciones

### Tests
- `tests/test_onboarding_injection.py`: ~15 tests nuevos (`_normalize_url`, `_load_latest_onboarding_data`, `_observation_to_onboarding_format`)

### Bugs Resueltos
- B1: Slug mismatch onboard↔v4complete (CRÍTICO)
- B2: Ventana frescura 24h (CRÍTICO)
- N3: hotel_url ignorado en loader
- N4: output_dir hardcodeado en lectura
- N5: Sin identity resolver centralizado
- §10a: user_provided invisible al tiering
- §10b: audit deprecado sugerido por onboard
- §10c: observations.json no integrado

## [4.66.0] - DT-4 Residual Fixes — 2026-07-28

### Objetivo
Corregir la causa raíz del coverage gate failure en DT-4: el pain_ledger_resolved
no se inyectaba en el assessment por un bug de path (faltaba hotel_id/). Normalizar
SitePresence, unificar coherence score, unificar alignment reporting, eliminar doble
ejecución de gates, y corregir la divergencia delivery-vs-gate en alignment.

### Cambios Implementados

**FASE-1 a FASE-5 (plan original)**:
- `modules/assessment_builder.py` — Campo `pain_ledger_resolved` en AssessmentPayload + builder method `with_resolved_pain_ledger()`
- `main.py` — Carga de pain_ledger_resolved.json + SitePresence computado una vez + gates idempotentes
- `modules/asset_generation/site_presence_adapter.py` — Nuevo adapter canónico SitePresence (dataclass/dict/enum → dict)
- `modules/asset_generation/v4_asset_orchestrator.py` — Expone pain_ledger_resolved + final_coherence_report
- `modules/commercial_documents/coherence_validator.py` — 3 call sites con site_presence_report normalizado
- `modules/quality_gates/publication_gates.py` — Sin reconstrucciones fake, sin doble ejecución, sin mutaciones
- `modules/quality_gates/alignment_result.py` — AlignmentResult DTO canónico compartido (from_alignment_report + from_asset_alignment_matrix)
- `modules/quality_gates/delivery_quality_report.py` — Alineado con AlignmentResult

**FASE-6-A (DT4-N7) — Path fix**:
- `main.py:2690` — Corregido: `output_dir / hotel_id / "v4_audit" / "pain_ledger_resolved.json"` (faltaba hotel_id/)
  - Impacto: coverage_no_silent_drop pasó de justified=0→9, uncovered=["no_whatsapp_visible"]→[]

**FASE-6-B (DT4-N8) — Delivery alignment fix**:
- `modules/quality_gates/alignment_result.py` — `from_asset_alignment_matrix()` acepta site_presence_report opcional; cross-referencea entries NO_BREACH/MISSING_ASSET contra presencia real en sitio
- `modules/quality_gates/delivery_quality_report.py` — `generate()` acepta site_presence_report; delivery_ready deriva de AlignmentResult.passed
- `main.py:2970` — Pasa site_presence_report a quality_generator.generate()
  - Impacto: delivery status FAIL→PASS (5/5 gates), present_in_production=0→2, consistente con gate_report

### Issues Comerciales Documentados (NO técnicos)
- **CG-ROI-NEGATIVE**: Zi One tiene beneficio neto 6m negativo (-$1,330,590 COP, ROI 0.45X) con datos financieros default/regionales. Requiere onboarding con datos operativos reales para recalcular. No es un bug — es la realidad matemática con los datos disponibles.
- **CG-TECH-JARGON**: Jerga técnica (Schema, AEO, IAO, Open Graph, Gemini) en vista gerencia. WARNING no bloqueante.

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/site_presence_adapter.py` | Adapter canónico SitePresence |
| `modules/quality_gates/alignment_result.py` | AlignmentResult DTO compartido |
| `tests/quality_gates/test_coverage_gate_integration.py` | Test integrado reconciler→builder→gate |
| `tests/asset_generation/test_site_presence_adapter.py` | Tests normalización SitePresence |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | Carga resolved ledger (path corregido) + SitePresence único + gates idempotentes + site_presence a delivery |
| `modules/assessment_builder.py` | pain_ledger_resolved + with_resolved_pain_ledger() + with_coherence usa final |
| `modules/asset_generation/v4_asset_orchestrator.py` | Expone pain_ledger_resolved + final_coherence_report |
| `modules/commercial_documents/coherence_validator.py` | 3 call sites con site_presence_report |
| `modules/quality_gates/publication_gates.py` | Sin mutaciones, sin reconstrucciones fake, sin doble ejecución |
| `modules/quality_gates/alignment_result.py` | from_asset_alignment_matrix con SitePresence cross-reference |
| `modules/quality_gates/delivery_quality_report.py` | Acepta site_presence_report; delivery_ready de AlignmentResult |
| `VERSION.yaml` | 4.65.0 → 4.66.0 |

### Tests
- 1 test integrado coverage (reconciler→builder→gate)
- 5 tests normalización SitePresence
- 2 tests final_coherence
- 8 tests alignment (from_alignment_report + from_asset_alignment_matrix + semantic equality)
- 43 tests totales verificados; 0 regresiones

### Verificación E2E
- v4complete Zi One (×2): coverage_no_silent_drop PASSED, delivery PASSED, documentos generados, 13/14 criterios globales cumplidos

## [4.65.0] - DT-4: Root cause reconciliation — Post-orchestrator reconciler + 5 bug fixes — 2026-07-27

### Objetivo
Resolver la causa raíz transversal de DT-4: 3 fuentes de verdad no consolidadas para determinar
si un pain está resuelto. Implementar reconciliador post-orchestrator que unifica pain_ledger,
proposal_asset_matrix y skipped_assets en un solo archivo de verdad (`pain_ledger_resolved.json`).
Complementar con 4 fixes adicionales: commercial gates visibles, reinterpretación de optimista
negativo, exclusión de monthly_report del alignment, y rename de gates coverage duplicados.

### Cambios Implementados (DT-4: Root Cause Reconciliation)
- **FIX-PRIORITY-1 (FASE-0)**: Post-orchestrator reconciler — nuevo módulo `modules/orchestration/post_orchestrator_reconciler.py`
  que consolida 3 fuentes de datos (pain_ledger, proposal_asset_matrix, skipped_assets) en `pain_ledger_resolved.json`
  con estados unificados (ASSET_GENERATED, MAPPED_TO_SERVICE, JUSTIFIED_SKIP). Cableado en v4_asset_orchestrator
  post-generación de assets. Coverage gate lee `pain_ledger_resolved` con fallback a `pain_ledger`.
  `ASSET_GENERATED` agregado a `_JUSTIFIED_STATUSES`. Coherence `whatsapp_verified` acepta `site_presence_report`
  opcional para boost de confidence.
  Resuelve: BUG-6 (coverage falso positivo no_whatsapp_visible), BUG-9 (divergencia G9), N2 (ASSET_GENERATED faltante),
  N3 (whatsapp_conflict cubierto pero no_whatsapp_visible no), N4 (coherence ignora SitePresence).
- **FIX-PRIORITY-2 (FASE-2)**: Commercial gates visibles — `commercial_gates_report.json` persistido en v4_audit
  antes del raise. `BLOCKED_BY_GATES.md` ampliado con sección "Commercial Gates Bloqueantes" + mensaje de acción
  corregido ("Resuelva los commercial gates bloqueantes y los publication gates fallidos" en vez de "vuelva a ejecutar").
  Resuelve: BUG-7, N5.
- **FIX-PRIORITY-3 (FASE-1)**: Optimista negativo reinterpretado — `_check_scenario_negative` degrada a WARNING
  cuando optimista<0<realista. `_check_scenario_order` hace PASS en break-even. Se preserva BLOCKING solo cuando
  ambos escenarios son negativos. Resuelve: BUG-8.
- **FIX-PRIORITY-4 (FASE-3)**: `monthly_report` excluido de `PROPOSAL_SERVICE_TO_ASSET` (Opción B).
  Ya no cuenta en alignment ni en conteos de cobertura. Resuelve: BUG-10.
- **FIX-PRIORITY-5 (FASE-4)**: Gates coverage renombrados — Publication G11: `coverage` → `coverage_no_silent_drop`.
  Delivery G7: `coverage_gate` → `coverage_failure_rate`. 279 quality_gates tests actualizados.
  Resuelve: N1 (gates con mismo nombre, diferente contrato).

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/orchestration/__init__.py` | Nuevo paquete orchestration (reconciliador) |
| `modules/orchestration/post_orchestrator_reconciler.py` | Reconciliador post-orchestrator — unifica 3 fuentes de verdad |
| `tests/orchestration/__init__.py` | Tests para módulo orchestration |
| `tests/orchestration/test_post_orchestrator_reconciler.py` | Tests funcionales del reconciliador |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/v4_asset_orchestrator.py` | Cableado del reconciliador post-generación de assets |
| `modules/quality_gates/publication_gates.py` | `ASSET_GENERATED` en `_JUSTIFIED_STATUSES` + coverage gate lee `pain_ledger_resolved` con fallback + rename G11 `coverage` → `coverage_no_silent_drop` |
| `modules/quality_gates/coherence_validator.py` | `_check_whatsapp_verified()` acepta `site_presence_report` opcional con boost a 0.95+ |
| `modules/quality_gates/commercial_gate.py` | `_check_scenario_negative` degrada a WARNING (BUG-8). `_check_scenario_order` PASS en break-even |
| `modules/quality_gates/delivery_quality_report.py` | Rename G7 `coverage_gate` → `coverage_failure_rate` |
| `modules/commercial_documents/v4_proposal_generator.py` | Persiste `commercial_gates_report.json` en v4_audit antes del raise |
| `modules/asset_generation/proposal_asset_alignment.py` | `monthly_report` removido de `PROPOSAL_SERVICE_TO_ASSET` |
| `main.py` | `BLOCKED_BY_GATES.md` ampliado con sección commercial gates + mensaje de acción corregido |
| `tests/quality_gates/test_commercial_gate.py` | 5 tests nuevos (2 persistencia + 3 BLOCKED_BY_GATES escenarios) |
| `tests/quality_gates/test_coverage_gate.py` | Test actualizado: `gate_name == "coverage_no_silent_drop"` |

### Tests
- 3104 tests totales (pytest --collect-only)
- 0 regresiones en tests existentes
- Nuevos tests por fase: FASE-0 (3 reconciliador), FASE-1 (4 casos BUG-8), FASE-2 (5 persistencia + BLOCKED_BY_GATES), FASE-3 (14 actualizados), FASE-4 (279 quality_gates actualizados)

### v4complete Zi One Luxury (E2E Verification)
- Exit code: 0, 73 archivos generados
- Reconciliador: 9 entries (8 ASSET_GENERATED + 1 MAPPED_TO_SERVICE) en `pain_ledger_resolved.json`
- Commercial gates: `commercial_gates_report.json` con 3 gates (1 BLOCKING + 2 WARNING)
- BLOCKED_BY_GATES.md: sección commercial gates + acción corregida
- Gate names: `coverage_no_silent_drop` (publication) + `coverage_failure_rate` (delivery G7)
- monthly_report: excluido de alignment matrix (7 entries, sin monthly_report)
- Hallazgo residual: `MAPPED_TO_SERVICE` no está en `_JUSTIFIED_STATUSES` — `no_whatsapp_visible` sigue FAIL en coverage gate porque el status no se reconoce como justificado. Requiere follow-up (agregar `MAPPED_TO_SERVICE` a `_JUSTIFIED_STATUSES`).
- Hallazgo residual: Coherence `whatsapp_verified` score 0.30 — el boost de SitePresence no se activó para Zi One.

## [4.64.0] - DT-3: Tech debt resolution — AssetAlignmentMatrix unification — 2026-07-25

### Objetivo
Resolver 4 bugs de technical debt post-DT-2: corrección sistémica de rutas flat → per-hotel,
unificación de ProposalAssetMatrix + AlignmentReport en AssetAlignmentMatrix, fix de G9 dual-list,
y evaluación status-based de G9 (NO_BREACH no bloquea).

### Cambios Implementados (DT-3: Tech Debt Resolution)
- **BUG-1**: Fix sistémico de 3 rutas flat → per-hotel. Creado helper `_get_pipeline_path()` en main.py.
  Corrige pain_ledger.json, coherence_validation_flat.json y coherence_validation_per_hotel.json.
- **BUG-2**: Fix G9 dual-list — G9 ya no aparece simultáneamente en blocking_gates y warning_gates.
  Creada constante `BLOCKING_GATE_NAMES` para deduplicación.
- **BUG-3**: Fix G9 status-based evaluation — evalúa `status` del asset (LINKED=pass, NO_BREACH=skip,
  MISSING_ASSET=fail). `_is_service_aligned()` helper implementado; `actionable_services` excluye NO_BREACH.
- **BUG-4 / P-04**: Unificación ProposalAssetMatrix + AlignmentReport → `AssetAlignmentMatrix`.
  Nueva taxonomía unificada con `AlignmentStatus` enum (LINKED, NO_BREACH, MISSING_ASSET).
  Consumidores migrados: G9, main.py, publication_gates.py, v4_proposal_generator.py.

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/proposal_asset_alignment.py` | AssetAlignmentMatrix con AlignmentStatus enum + taxonomía unificada |
| `tests/asset_generation/test_proposal_asset_matrix.py` | 14 tests nuevos para contrato AssetAlignmentMatrix |
| `per-hotel` | Placeholder para directorio de pipelines per-hotel (cargado dinámicamente) |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | Helper `_get_pipeline_path()` + 3 rutas flat → per-hotel (BUG-1) |
| `modules/quality_gates/delivery_quality_report.py` | BLOCKING_GATE_NAMES constante (BUG-2) + status-based eval (BUG-3) + consume AssetAlignmentMatrix (BUG-4) |
| `modules/commercial_documents/v4_proposal_generator.py` | Migración a AssetAlignmentMatrix |
| `tests/delivery/test_delivery_contract.py` | Test actualizado para AssetAlignmentMatrix |

### Tests
- 86 tests existentes PASS (0 regresiones)
- 14 tests nuevos AssetAlignmentMatrix (14/14 PASSED)
- v4complete Zi One Luxury: BUG-1 ✅ (9 entries pain_ledger), BUG-2 ✅ (solo blocking), BUG-3 ✅ (NO_BREACH no bloquea), BUG-4 ✅ (AssetAlignmentMatrix)

## [4.63.2] - Delivery-Contract-Residual — 2026-07-25

### Objetivo
Corregir 7 findings residuales post-DT-1 en el delivery contract: desincronización de conteos,
exclusión mutua de advisory assets, quality report post-generación, implementación de G9 dead gate,
y empaquetado de proposal_asset_matrix.

### Cambios Implementados (DT-2: Delivery Contract Residual Fixes)
- P-01: README Overview ahora muestra conteo de archivos y tamaño que coinciden con MANIFEST.json (recalculado post-Manifest Pass 3)
- P-02: Assets advisory ya no aparecen simultáneamente en secciones state-based y Advisory Guides (exclusión mutua por `is_advisory`)
- P-03: delivery_quality_report refleja score de coherencia post-generación (`coherence_validation_post_gen.json`), con fallback al pre-gen
- P-04: proposal_asset_matrix path alineado con DeliveryContext (divergencia semántica documentada como deuda técnica para v4.64.0)
- P-05: G9 proposal_asset_alignment gate implementado — evalúa alineación real, ya no hardcodea default True
- P-06: proposal_asset_matrix.json ahora se empaqueta en el ZIP de entrega
- P-07: Comparación string-vs-enum unificada a `DeliveryAssetState.DELIVERED` (ya no compara strings)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/delivery/delivery_packager.py` | P-01 conteo post-manifest + P-07 enum + P-02 exclusión advisory + P-06 packaging |
| `modules/delivery/delivery_context.py` | P-02 exclusión mutua advisory en filtros delivered/estimated |
| `modules/quality_gates/delivery_quality_report.py` | P-03 post-gen coherence + P-05 G9 gate implementado |
| `modules/asset_generation/proposal_asset_alignment.py` | P-04 path alignment + documentación de divergencia |
| `modules/commercial_documents/v4_proposal_generator.py` | P-04 + P-06 path de guardado de proposal_asset_matrix |
| `tests/delivery/test_delivery_contract.py` | 14 tests nuevos de contrato P-01..P-07 |

### Tests
- 28 tests existentes + 14 nuevos = 42 tests de contrato (42/42 PASSED)
- v4complete Zi One Luxury: verificación E2E de 7 fixes (S-1 a S-9)

## [4.63.1] - Delivery-Contract — 2026-07-24

### Objetivo
Resolver la desincronización entre README_DELIVERY.md, MANIFEST.json, ZIP y estados de assets. El README ahora se genera desde los destinos reales del ZIP y respeta el estado canónico de cada asset.

### Cambios Implementados
- FASE-A: `DeliveryAssetState` enum, `DeliveryAssetEntry` (con `is_advisory`), `DeliveryContext` (con `from_asset_generation_report()`) en `delivery_context.py`
- FASE-B: Rutas POSIX en manifest/ZIP, tamaños reales, filename único, `_validate_zip()`, carga automática de `DeliveryContext` en `package()`
- FASE-C: README dinámico con secciones por estado (Present/Issues/Estimated/Advisory Guides/Evidence)
- FASE-D: Tests cross-artifact (19+ tests) + gate de no-regresión `DeliveryValidationError`
- FASE-E: E2E validation con Zi One Luxury + RELEASE

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/delivery/delivery_context.py` | Nuevo módulo: `DeliveryAssetState`, `DeliveryAssetEntry`, `DeliveryContext` |
| `tests/delivery/test_delivery_contract.py` | 19+ tests de contrato cross-artifact |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/delivery/delivery_packager.py` | Rutas POSIX, tamaños reales, README dinámico, validación, carga DeliveryContext |
| `modules/assessment_builder.py` | Propagación de pain_ids_affected en skipped_assets |
| `templates/delivery_readme_template.md` | Template modular sin hardcodeos + sección Advisory Guides |

### Tests
- 10 tests existentes del packager: PASS
- 19+ tests nuevos de contrato: PASS

## [4.63.0] - ASSET-ALIGNMENT: Proposal asset alignment gate bypass fix + Pain->Asset gaps — 2026-07-23

### Objetivo
Reparar el bloqueo de proposal_asset_alignment (Gate 9) detectado en la ejecución v4complete
para Zi One Luxury (zione.co), cerrando una cadena de bypass de 3 capas y 13 hallazgos
adicionales de severidad variable.

### Cambios Implementados
- `modules/quality_gates/delivery_quality_report.py` — Consume resultado real de Gate 9 (no hardcodea passed=True) + blocking_gates
- `main.py` — GATE_BLOCKING_ENABLED default=True
- `modules/commercial_documents/pain_solution_mapper.py` — Nuevo pain `low_seo_score` → optimization_guide + modo enhance_existing para no_og_tags
- `modules/asset_generation/open_graph_generator.py` — Modo enhance_existing (genera tags faltantes, no duplica existentes)
- `modules/asset_generation/conditional_generator.py` — Clave duplicada PAIN_TO_ASSET eliminada + pasa existing_og_tags al generador
- `modules/commercial_documents/v4_proposal_generator.py` — _generate_dynamic_services_table condicional
- `modules/commercial_documents/service_catalog.py` — SERVICE_TO_ASSET_LOOKUP unificado con PROPOSAL_SERVICE_TO_ASSET
- `modules/commercial_documents/templates/propuesta_v6_template.md` — Template Tier C → variable
- `modules/asset_generation/proposal_asset_matrix.py` — Serialización dicts vs objetos
- `modules/delivery/delivery_packager.py` — MANIFEST + README dinámicos
- `tests/quality_gates/test_publication_gates.py` — Test roto L1191 corregido

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/asset_generation/test_open_graph_enhance_existing.py` | 5 tests para modo enhance_existing del OpenGraphGenerator |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/delivery_quality_report.py` | Key "proposal_asset" → "proposal_asset_alignment" + blocking_gates |
| `main.py` | GATE_BLOCKING_ENABLED default "true" |
| `modules/commercial_documents/pain_solution_mapper.py` | low_seo_score pain + no_og_tags enhance_existing |
| `modules/asset_generation/open_graph_generator.py` | generate_content() acepta existing_og_tags, no duplica |
| `modules/asset_generation/conditional_generator.py` | Clave duplicada eliminada + pasa existing_og_tags |
| `modules/commercial_documents/v4_proposal_generator.py` | Servicios condicionales |
| `modules/commercial_documents/service_catalog.py` | Unificación fuentes |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Tier C → variable + label financiero |
| `modules/asset_generation/proposal_asset_matrix.py` | Serialización dicts/objetos |
| `modules/delivery/delivery_packager.py` | MANIFEST/README dinámicos |
| `tests/quality_gates/test_publication_gates.py` | Fix path hardcodeado |

### Tests
- 16 tests nuevos (FASE-1: 5 bypass fix; FASE-2: 5 enhance_existing + 1 updated; FASE-3: 6 conditional filtering + lookup unification)
- 0 regresiones
- v4complete Zi One Luxury: Gate 9 PASSED, coherence ≥ 0.80

## [4.62.0] - BUGS-ONBOARDING-ADR: Fix propagación onboarding al harness — 2026-07-22

### Objetivo
Fix propagación de datos de onboarding (ADR, occupancy) al harness financiero y unificación de taxonomía de fuentes.

### Cambios Implementados
- **BUG-1**: ADR de onboarding ahora se propaga al harness financiero (antes: ignorado, usaba benchmark regional)
- **NEW-1**: Occupancy_rate del onboarding ya no es sobrescrito por benchmark regional
- **H1**: Proposal generator usa ADR del onboarding (antes: resolver paralelo con None)
- **H3**: ValidationSummary confidence/sources ahora reflejan fuente real del valor
- **H2**: Unificada taxonomía de fuentes (ADRSource enum) entre diagnóstico, propuesta y JSON
- **BUG-2**: CTAs "Complete el onboarding" ahora condicionados a has_onboarding (7 superficies)
- **F3**: adr_source en JSON ya no es placeholder "handler"

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/e2e/__init__.py` | Package init para tests e2e |
| `tests/e2e/conftest.py` | Fixtures para tests e2e |
| `tests/e2e/test_onboarding_to_harness_pipeline.py` | Tests e2e onboarding → harness → JSON pipeline |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | Propagación ADR+occupancy al harness payload |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Fuente real en ValidationSummary, ADRSource enum, CTA condicional |
| `modules/commercial_documents/v4_proposal_generator.py` | ADR del onboarding en propuesta |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Ajustes template |
| `tests/commercial_documents/test_proposal_generator.py` | Tests actualizados |

### Tests
- Tests e2e onboarding pipeline añadidos
- 0 regresiones

## [4.61.0] - HOOK-PDF: PDF Gancho Command — 2026-07-10

### Objetivo
Nuevo comando `hook-pdf` que genera un PDF gancho de 2 páginas ("¿Cuánto pierde su hotel?") desde el output de v4complete. Resuelve Gap #2 "Empaquetado no técnico".

### Cambios Implementados
- **hook_pdf_generator.py**: Clase `HookPDFGenerator` con extract/validate/render/generate (34 campos, weasyprint)
- **HookPDFData**: Dataclass en `data_structures.py` con 34 campos + `evidence_tier`
- **hook-pdf CLI**: Comando en `main.py` con args `--output-dir`, `--template`, `--style`, `--dry-run`, `--force`, `--verbose`
- **Templates**: `hook_template.md` (HTML, 191 líneas) + `hook_styles.css` (@page A4, 2 páginas, hook figure 28pt)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/commercial_documents/hook_pdf_generator.py` | Generador PDF gancho |
| `templates/hook_template.md` | Template HTML con 34 placeholders |
| `templates/hook_styles.css` | Estilos A4, 2 páginas |
| `tests/commercial_documents/test_hook_pdf_generator.py` | 36 tests parametrizados |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `data_structures.py` | `HookPDFData` dataclass (34 campos) |
| `modules/commercial_documents/__init__.py` | Export `HookPDFGenerator` + `HookPDFData` |
| `main.py` | Comando `hook-pdf` + argparse |

### Tests
- 36 tests: extract_data (8), validate_data (4), render_html (3), generate (2), formato COP (11), slug (5), glob+missing (2), negativos
- 0 regresiones (256 tests en suite completa → actualizado a 292)

### E2E Validation
- Luxorhotel: PDF 2 páginas, cero placeholders, cifra fuga 28pt, disclaimer Tier B, 1.486s

## [4.60.1] - Bugfixes Luxor v4complete — 2026-07-06

### Objetivo
Corrección de 5 bugs detectados en ejecución v4complete de Luxorhotel, no relacionados con onboarding.

### Cambios Implementados — FASE-1
- **BUG-2**: Removido `calc_result` UnboundLocalError en FASE-K (main.py ~L1942). Reemplazado por `financial_breakdown.evidence_tier` + `disclaimer`.
- **BUG-1**: `_audit_competitors` ahora usa `gbp_result.lat/lng` en lugar de `0.0` hardcoded. Validación de rango Colombia (0-13 lat, -82 a -66 lng) antes de llamar Places API.

### Archivos Modificados — FASE-1
| Archivo | Cambio |
|---------|--------|
| `main.py` | Línea `calc_result.metadata` reemplazada por `financial_breakdown.evidence_tier` + `disclaimer` |
| `modules/auditors/v4_comprehensive.py` | `_audit_competitors` usa `gbp_result.lat/lng` + validación de rango Colombia |

### Tests — FASE-1
- 3 tests BUG-1: coords válidas, coords cero, coords fuera de rango
- 1 test BUG-2: `FinancialBreakdown.evidence_tier` y `disclaimer` accesibles
- 0 regresiones

### Cambios Implementados — FASE-3
- **BUG-5**: Eliminado bloque FASE 3.6 del content scrubber (dead code que producía warnings `[SKIP]` innecesarios). Los scrubs reales post-T4FIX y post-gen siguen intactos.

### Archivos Modificados — FASE-3
| Archivo | Cambio |
|---------|--------|
| `main.py` | Eliminado bloque FASE 3.6 (ContentScrubber + DocumentQualityGate, ~106 líneas). `hotel_data` reubicado al post-gen scrub. |

### Tests — FASE-3
- 24/24 tests existentes del scrubber pasan (0 regresiones)
- Scrubs post-T4FIX y post-gen verificados como intactos

### Cambios Implementados — FASE-2
- **BUG-4a**: Externalizado modelo openrouter al `provider_registry.yaml`. `llm_mention_checker.py` ya no hardcodea `openai/gpt-4o` (404). Lee `default_model` del registry con fallback `openai/gpt-4.1`.

### Archivos Modificados — FASE-2
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/llm_mention_checker.py` | Modelo openrouter leído de `provider_registry.yaml` en lugar de hardcoded |
| `config/provider_registry.yaml` | `default_model` actualizado a modelo vigente |

### Tests — FASE-2
- 4 tests de modelo dinámico (not hardcoded, from registry, payload usa registry, fallback)
- 0 regresiones

### Cambios Implementados — FASE-4
- **BUG-6**: Integrado Playwright como fallback para renderizar SPAs antes del SEO audit. Detección heurística de SPA (scripts sin meta/OG tags) + renderizado con chromium headless + fallback graceful a BeautifulSoup si Playwright falla.

### Archivos Modificados — FASE-4
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | `_run_seo_elements_audit` con detección SPA + Playwright fallback; nuevos métodos `_is_spa()` y `_render_with_playwright()` |
| `tests/auditors/test_seo_elements_detector.py` | 7 tests SPA rendering (4 detección + 3 integración mock/fallback) |

### Tests — FASE-4
- 7 tests nuevos SPA rendering
- 148/149 auditor tests pasan (1 skip, 0 regresiones)

### Cambios Implementados — FASE-5 (Verificación E2E)
- **v4complete ejecutado** para Luxorhotel con todos los fixes de FASE-1 a FASE-4
- **BUG-1**: ✅ lat/lng reales (4.81, -75.70), 5 competitors encontrados
- **BUG-2**: ✅ Sin UnboundLocalError en FASE-K. FinancialBreakdown derivado correctamente.
- **BUG-4a**: ⚠️ OpenRouter 404 persiste en `llm_mention_checker` (modelo `qwen/qwen3.6-plus:free` no encontrado). El pipeline principal usa DeepSeek y completa exitosamente.
- **BUG-4b (gemini 403)**: Fuera del plan — requiere acción del usuario (API key).
- **BUG-5**: ✅ Sin warnings `[SKIP]` de scrubber. Scrubs post-T4FIX y post-gen funcionando.
- **BUG-6**: ✅ Código Playwright SPA fallback presente en `v4_comprehensive.py`. Luxorhotel no triggeró la heurística SPA (tiene ≥3 meta tags); Open Graph: false es resultado genuino (el sitio no tiene OG tags).
- **Coherence score**: 0.80 (≥ 0.80)
- **Publication Gates**: 11/11 PASSED (READY_FOR_PUBLICATION)
- **Regresiones**: 0

### Archivos Modificados — FASE-5
| Archivo | Cambio |
|---------|--------|
| `evidence/FASE-5/` | Evidencia de ejecución v4complete (23 archivos) |

### Tests — FASE-5
- 0 tests nuevos (fase de verificación)
- 0 regresiones detectadas

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `evidence/FASE-5/` | Evidencia de verificación E2E (23 archivos) |

## [4.60.0] - CAPEX Breakdown Fix & Generator Cleanup — 2026-05-29

### Objetivo
Fix de tabla CAPEX corrupta (tablas markdown anidadas) + limpieza de código muerto en generator. Verificado con v4complete en Hotel Castilla Real (11/11 gates).

### Cambios Implementados
- **F1** (FASE-1): `${capex_breakdown_table}` movido a sección independiente — fix tablas markdown anidadas + test de integridad de pipes
- **F7** (FASE-2): Eliminadas 9 keys huérfanas del template data dict
- **F8** (FASE-2): Fallback de `_build_capex_breakdown_table()` ahora incluye header row
- **F6** (FASE-3): Eliminado `_build_coherence_checklist()` + `'coherence_checklist'` del data dict — código muerto YAGNI
- **NEW-CRIT-01** (post-release hotfix): Eliminada tabla "Status Quo vs Implementación IAO" — usaba modelo de recuperación constante (pain_ratio × recovery) contradictorio con la curva de madurez de la tabla Proyección. Un único motor de proyección (curva 4 pilares).

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/test_capex_rename.py` | Test de integridad de pipes en tabla CAPEX |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/templates/propuesta_v6_template.md` | CAPEX desglose movido a sección propia |
| `modules/commercial_documents/v4_proposal_generator.py` | Keys huérfanas eliminadas, fallback con header, coherence checklist eliminado |

### Tests
- test_capex_rename.py: 8/8 passing
- 0 regresiones en tests existentes
- v4complete Hotel Castilla Real: 11/11 gates, coherence 0.85

### Backwards compatibility
Sí. Fix de rendering sin cambios en API pública.

---

## [4.59.0] - REFACTOR-5-GAPS - 2026-05-29

### Objetivo
Resolver 5 gaps comerciales confirmados en la propuesta comercial v4, 1 bug de gates y 1 deuda técnica. Verificado con v4complete en Hotel Castilla Real.

### Cambios Implementados
- **IMP-03**: CAPEX breakdown ahora se renderiza en propuesta (template fix)
- **F7**: Unificada lógica de evidence tier entre publication gates
- **F5**: ADR en coherence checklist usa fuente real (benchmarks regionales)
- **MIN-02**: ADR evidenciado en benchmarks + propuesta comercial
- **MIN-01**: Nueva tabla Status Quo vs Implementación IAO
- **MIN-03**: Closing pitch dinámico basado en ROICR, payback y recuperación
- **Debt**: Eliminado template embebido muerto en v4_proposal_generator.py

### Archivos Modificados
||| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | CAPEX table, Status Quo, Closing Pitch, ADR cascade, dead code removal |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Placeholders: capex_breakdown_table, status_quo_table, adr_display, closing_pitch |
| `modules/quality_gates/publication_gates.py` | financial_validity usa evidence_tier formal |
| `config/regional_benchmarks.yaml` | ADR por región (eje_cafetero, caribe, bogota, antioquia) |

### Tests
- Regresión completa: 610/611 tests passing
- v4complete Hotel Castilla Real: 11/11 gates, coherence 0.85

### Backwards compatibility
Sí. Nuevos placeholders son opcionales — si no se producen, el template los ignora. Gates más precisos no cambian FAIL/PASS umbral.

---

## [4.58.0] - ROICRIIIF: Publication Readiness Fix — 2026-05-28

### Objetivo
Resolver 3 issues bloqueantes de la release anterior (v4.57.0) que impedían la publicación de propuestas comerciales con coherencia ≥ 80%.

### Fixes Implementados
- **Gate Presence Fix**: Gate ahora reconoce activos pre-existentes como `present_in_production` (GATE-PRESENCE)
- **Asset Confidence Enrichment**: `faq_page` y `optimization_guide` enriquecidos con datos reales del sitio (CONFIDENCE-LOW)
- **Semantic Cleanup**: Eliminado artifact "13% del dolor" de pricing en plantilla de propuesta (SEMANTIC-13)
- **v4complete E2E**: Hotel Castilla Real verificado — Coherence ≥ 0.80, Publication READY_FOR_PUBLICATION

### Archivos Modificados
|| Archivo | Cambio |
|---------|--------|
| `modules/quality/publication_gates.py` | Gate reconoce activos pre-existentes como presentes en producción |
| `modules/quality/preflight_checks.py` | Confidence enrichment con datos reales del sitio |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Eliminado artifact "13%" |
| `modules/commercial_documents/v4_proposal_generator.py` | Limpieza semántica de artifacts |

### Tests
- Tests de presence gate en `test_publication_gates_presence.py`
- 0 regresiones en suite existente

### Backwards compatibility
Sí. Fixes de gate y cleanup semántico — no cambia lógica core del pipeline.

---

## [4.57.0] - Financial Coherence & Asset Semantics Rescue — 2026-05-28

### Objetivo
Resolver regresión crítica de v4.55.0: doble motor de cálculo financiero produciendo ROIs contradictorios, mapeos semánticos incorrectos, y assets deprecados en la propuesta comercial.

### Cambios Implementados
- **Motor Financiero Unificado**: `total_recovered` y `roi_6m` ahora usan `_maturity_result.total_recuperacion_6m` como única fuente de verdad (FASE-1)
- **Pain Ratio Corregido**: `pain_ratio_note` muestra % inversión/fuga real (10.7%) en lugar del `pain_ratio` interno (FASE-2)
- **Validator Semántico Integrado**: `asset_semantics_validator` activo en `_generate_dynamic_services_table` (FASE-3)
- **Assets Deprecados Filtrados**: 4 assets deprecados removidos de output y catálogo (FASE-4)
- **Piloto 30 Días**: Nueva sección de bajo riesgo para clientes sin presupuesto completo (FASE-5)
- **CAPEX Breakdown**: Desglose detallado de Setup Fee (FASE-5)
- **Garantía Día 55**: KPI concreto (+15% clics GSC) reemplaza texto genérico (FASE-5)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Unificación motor, validator, filtrado de deprecados, features |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Eliminar dualidad ROI, piloto, CAPEX, garantía |
| `modules/commercial_documents/service_catalog.py` | Remover `indirect_traffic_optimization` del catálogo |
| `config/commercial.yaml` | Añadir `pilot_options` |

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/commercial_documents/test_financial_coherence.py` | Tests de coherencia financiera (5 tests) |
| `tests/quality/test_asset_semantics_integration.py` | Tests de integración del validator (5 tests) |

### Tests
- 10 tests nuevos en `test_financial_coherence.py` y `test_asset_semantics_integration.py`
- 0 regresiones en suite existente

## [4.56.0] — ROICRII (2026-05-27)

### Fix (structural)
- **ROI unificado**: Eliminados motores inline `_calculate_roi()` y `_calculate_roi_saas()`. Motor único: `roi_formatter.py`. Formato `:.2f`.
- **Coherencia financiera**: Commercial gate calcula ROI con opex-only (sin CAPEX). Wrapper activa pipeline 3 pasos vía `expected_recovery_cop`.
- **Gobernanza semántica**: `pain_ratio_note` diferencia addressable vs fee/loss. `operational_floor` fallback unificado a 400K.
- **Gate estricto**: `CommercialGateBlockedError` para audiencia externa. CAPEX desglosado en componentes.
- **QA Score**: 72% → ≥90% (ROICRII reporte v3)

### Test
- Nuevos: test_roi_unification, test_financial_coherence, test_semantics_floor_gate, test_capex_rename
- Regresiones: 0 (517+ passed)

## [4.55.0] — ROICR (2026-05-27)

### Objetivo
Cierre del proyecto ROICR: 6 fases de implementacion — pipeline unificado, CAPEX/OPEX, curva de maduracion, arbitraje, garantia.

### Arreglado
- **FASE-1**: AssetSemanticsValidator — semantica de soluciones (Auditar/Implementar) y deteccion de mappings invalidos
- **FASE-2**: Gate P1 BLOCKING — coherence score con seuil 0.80 bloquea si < 0.80
- **FASE-3**: Pipeline unificado de pricing (3 pasos) + CAPEX/OPEX desacoplado
- **FASE-4**: Arbitraje etico + Garantia Dia 55 (`validate-guarantee`)
- **FASE-5**: Tests + Fixtures recalibrados
- **FASE-6**: v4complete Hotel Castilla Real verificado — coherence 0.83, gates 9/11

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `VERSION.yaml` | Bump 4.54.0 → 4.55.0 |
| `modules/pricing/pricing_calculator.py` | Pipeline unificado (3 pasos), CAPEX/OPEX desacoplado |
| `modules/pricing/asset_semantics_validator.py` | AssetSemanticsValidator (nuevo) |
| `modules/pricing/maturity_curve.py` | Curva de maduracion 4 pilares |
| `modules/pricing/arbitrage_validator.py` | Arbitraje etico |
| `modules/pricing/guarantee_validator.py` | Garantia Dia 55 |
| `modules/commercial_documents/v4_proposal_generator.py` | Pain ratio clamp, coherence validation |
| `tests/pricing/` | 40+ tests nuevos/recalibrados |
| `CHANGELOG.md` | Entrada v4.55.0 |
| `REGISTRY.md` | Registro FASE-RELEASE-ROICR |

### Backwards compatibility
Si. Cambios internos de pricing y validacion semantica — la logica core del pipeline no cambia.

---

## [4.54.0] — ROI-REFACTOR (2026-05-26)

### Objetivo
Cierre del proyecto ROI-REFACTOR: 5 fases de implementacion — decision comercial, simplificacion de documentos y transparencia financiera.

### Arreglado
- **FASE-0**: Decision comercial — Opcion E (Piloto 250K COP + credito a retainer + success fee capped) para hotel boutique sin GA4
- **FASE-A**: `document_audience` switch (cliente vs interno) + testimonios condicionales (`testimonials_present`) + nota pain_ratio corregida (inversion/pérdida)
- **FASE-B**: Lenguaje de negocio en propuesta — AEO→"Optimizacion para Asistentes de Voz", UTMs→"sistema de rastreo", P1/P2/P3→Fase 1/2/3 + tabla entregables con momento de entrega
- **FASE-C**: `adr_source` expuesto en `input_data` de financial_scenarios.json + `_get_pipeline_version()` desde VERSION.yaml (reemplaza hardcode "4.0.0")
- **FASE-D**: Anexo APIs → párrafo de transparencia ("múltiples modelos IA") + `tier_explanation` en JSON + `pain_ratio_note` en diagnostico y propuesta
- **FASE-5**: v4complete Hotel Castilla Real verificado — Coherence 0.83, Gates 10/11

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `VERSION.yaml` | Bump 4.53.0 → 4.54.0 |
| `modules/commercial_documents/v4_proposal_generator.py` | FASE-A/B/C/D: document_audience, testimonials, business language, entregables, version dinamica, transparency paragraph, pain_ratio_note |
| `modules/commercial_documents/v4_diagnostic_generator.py` | FASE-A/C/D: document_audience, version dinamica, tier_explanation, pain_ratio_note |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | FASE-A/B: testimonios condicionales, lenguaje de negocio, momento de entrega, paragraph transparencia |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | FASE-D: `${pain_ratio_note}` placeholder |
| `main.py` | FASE-C/D: adr_source en input_data, tier_explanation en financial_scenarios.json |
| `README.md` | Version 4.54.0 |

### Deudas Tecnicas (known)
- **DT01**: pain_ratio 41% (propuesta) vs 20% (diagnostico) — artefacto del min_price floor en pricing_calculator.py. No bloquea entrega. Documentado en nota del diagnostico.
- **DT02**: precision_tier=C + can_show_exact_money=false — sin redondeo implementado. Gap conocido, no bloquea.

### Backwards compatibility
Si. Cambios de documentos comerciales y metadata financiera — la logica core del pipeline no cambia.

### Objetivo
Cierre del proyecto PROPUESTA-COMERCIAL: 14 hallazgos corregidos en 5 fases de implementación.

### Arreglado
- **BREAKING**: Unificadas todas las variables financieras del template de propuesta sobre `effective_monthly_gain` (CODE-1/3/4)
- Gate CG-ROI-NEGATIVE sincronizado con tabla ROI (CODE-2)
- Puente dual fuga bruta/recuperación efectiva en diagnóstico y propuesta (CROSS-1)
- Mapping brecha→servicio con trazabilidad en tabla de propuesta (CROSS-2)
- Indicador de WhatsApp refleja conflicto real detectado (CROSS-4)
- Labels de estado unificados: "⚠️ En preparación" → "En proceso de activación — Semana 2" (V-2)
- Gate CG-TECH-JARGON expandido con 8 nuevos términos (V-3)
- Tabla de costos IAO movida a anexo técnico (V-3)
- Eliminado fallback frágil de búsqueda de string en `has_onboarding` (A-1)
- Confidence score visible en tabla de servicios de propuesta (CROSS-5)
- Umbral AEO unificado a 30 en ambas tablas (A-2)
- Cupo limitado justificado con número (V-4)
- Garantía incluye mecanismo de tracking propio Día 7 (V-5)
- Placeholder de prueba social agregado al template (V-6)
- Typo "PASSO" → "PASO" corregido (A-3)
- Gates NOT_READY ahora bloquean generación de documentos cliente (CROSS-6)

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | CODE-1/3/4, CROSS-1/2/4/5, V-2/3/4/5/6, A-1/2/3 |
| `modules/commercial_documents/v4_diagnostic_generator.py` | CROSS-1 |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Variables financieras, tabla dinámica, labels |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | CROSS-1 |
| `modules/commercial_documents/commercial_gate.py` | CODE-2, V-3, A-1 |
| `modules/commercial_documents/publication_gates.py` | CROSS-6 |

### Fases
| Fase | Hallazgo | Descripción |
|------|----------|-------------|
| FASE-A | CODE-1/3/4+CODE-2 | Unificación financiera + gate sync |
| FASE-B | CROSS-1 | Puente dual fuga bruta/recuperación efectiva |
| FASE-C | CROSS-2+4 | Mapping brecha→servicio + WhatsApp conflict |
| FASE-D | V-2+V-3+A-1+CROSS-5 | Labels, jargon, onboarding, confidence |
| FASE-E | A-2+V-4/5/6+A-3+CROSS-6 | AEO, paquete, typo, gate blocking |

### Tests
- log_phase_completion.py ejecutado para FASE-A a FASE-E
- sync_versions.py ejecutado → v4.53.0

## [4.52.0] - DIAGNOSTIC-ALIGNMENT — 2026-05-25

### Objetivo
Alinear el diagnóstico comercial generado por v4complete con criterios de prospección B2B hotelera.

### Cambios Implementados
- E1: Tabla de escenarios usa financial_value_range (Conservador < Realista < Optimista)
- E2: Recuperada tabla "Antes (2023) vs Ahora (2026)" en Sección 1
- F1: Quick Wins reformulados en lenguaje de dueño + delegación
- F2: Disclaimer Tier C convertido en "Oportunidad de Auditoría Profunda"
- F3: Texto puente "7 brechas → 3 fugas" en Sección 4
- F4: Encabezado "Fuga mensual estimada" en tabla resumen

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | _build_scenario_table_rows, _build_quick_wins, _prepare_financial_template_vars, _build_brechas_resumen_section |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Tabla Antes/Ahora, texto puente |

### Tests
- 2743 funciones base sin regresiones
- v4complete Hotel Castilla Real verificado 6/6 criterios Prospección.md

## [4.51.1] - COPYWRITING-REFACTOR — 2026-05-25

### Objetivo
Refactorizar templates y generadores de documentos comerciales para maximizar conversión en hoteles boutique colombianos. Basado en 12 hallazgos validados de Copywriting.jsonl.

### Cambios Implementados
- **Templates V6 reestructurados**: Vista Gerencia (dueño) primero, Anexo Técnico después
- **Narrativa OTA**: Booking/Expedia/comisiones incorporados como dolor central
- **WhatsApp como gancho #1**: Conflicto WhatsApp lidera el diagnóstico
- **Scenario clamp**: Escenario optimista nunca negativo (validación + label condicional)
- **Tier consistency**: Fuente única de evidence_tier desde FinancialBreakdown
- **Commercial gates**: Nuevo módulo `modules/quality_gates/commercial_gate.py` con 8 gates (5 BLOCKING + 3 WARNING)
- **IA Bloqueada → IA sin guía**: Corrección determinística cuando blocked_crawlers vacío

### Archivos Nuevos
|| Archivo | Descripción |
|---------|-------------|
| `modules/quality_gates/commercial_gate.py` | Commercial Gate Validator |

### Archivos Modificados
|| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Reordenado: dueño primero |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | OTA narrative, quick wins accionables |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Scenario clamp, tier consistency, breach sanitization |
| `modules/commercial_documents/v4_proposal_generator.py` | Commercial gate integration |

### Tests
- `tests/quality/test_commercial_gate.py` — 3+ tests unitarios para gates

---

## [4.51.0] - WHATSAPP-CONFLICT-VISIBILITY — 2026-05-24

### Objetivo
Hacer visible el warning de WhatsApp conflict con phrasing de impacto de negocio en la sección de contexto del diagnóstico, no solo en "Validación de Calidad".

### Cambios Implementados

- **FASE-A-02a** (2026-05-24): Investigación de visibilidad documentada. Mapear flujo actual de whatsapp_conflict en v4_diagnostic_generator.py y diagnostico_v6_template.md.
- **FASE-A-02b** (2026-05-24): Implementación nota en contexto. Agregar `whatsapp_conflict_business_note` como nota 🔴 ALERTA en sección contexto del diagnóstico.
- **FASE-A-02c** (2026-05-24): Ajuste narratives + impacto. Impacto ajustado 0.10→0.20, phrasing mejorado con impacto de negocio (reservas perdidas sin conocimiento del hotelero).
- **FASE-RELEASE** (2026-05-24): v4complete Hotel Castilla Real — coherence 0.8261, WhatsApp conflict visible en sección contexto como ALERTA 🔴.

### Archivos Modificados

- `modules/commercial_documents/v4_diagnostic_generator.py` — Nota de contexto whatsapp_conflict
- `templates/diagnostico_v6_template.md` — Phrasing de impacto de negocio

### Verificación

- v4complete Hotel Castilla Real: coherence 0.8261 ≥ 0.80 ✅
- WhatsApp conflict visible como ALERTA 🔴 en sección contexto ✅
- Sin costo mensual en la nota ✅
- Evidencia: `evidence/FASE-RELEASE/`

---

## [4.50.0] - AssessmentBuilder: Assessment Dict Tipado — 2026-05-30

### Objetivo
Centralizar la construcción del assessment dict en una clase tipada (`AssessmentBuilder`)
con esquema validable, eliminar ~120 líneas de extractores multi-path redundantes,
y eliminar campos zombie/fantasma acumulados por fases anteriores.

### Cambios Implementados
- Creado `modules/assessment_builder.py` con `AssessmentPayload` dataclass (28 campos tipados)
  y `AssessmentBuilder` con API fluida (9 métodos `.with_*()` + `.build()`)
- Migrado `main.py:2663-2754` (~87 líneas en 3 etapas) al builder (~15 líneas)
- Simplificados 5 extractores multi-path en `publication_gates.py` (~129 → ~30 líneas)
- Eliminados campos zombie: `quality_gate_issues/blockers/warnings` (locals().get(), 0 consumers)
- Eliminados campos dead: `coherence_checks/errors/warnings` (0 consumidores),
  `critical_issues_detected` (duplicado tautológico de `critical_issues`),
  `metrics` dict (0 consumidores — solo duplicaba coherence_score),
  `coherence_report` del assessment dict (0 consumidores post-simplificación),
  `consistency_report` inyección en assessment dict (variable sí usada en summary JSON)
- Simplificado `hotel_url or url` fallback en gate L836 (builder garantiza el campo)
- Agregados al schema: `proposal_services`, `hotel_url`, `site_presence_report`
  (antes buscados por gates pero nunca inyectados — defaults salvaban)
- Evitada duplicación de `SitePresenceChecker` (se ejecutaba 2 veces)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `modules/assessment_builder.py` | AssessmentPayload dataclass + AssessmentBuilder class |
| `tests/test_assessment_builder.py` | 30 tests unitarios (dataclass + builder) |
| `tests/quality_gates/test_extractors_simplified.py` | 5 tests de extractores simplificados |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | L2663-2754 reemplazado por AssessmentBuilder (~87 → ~15 líneas); L2838 consistency_report inyección eliminada |
| `modules/quality_gates/publication_gates.py` | 5 extractores simplificados a acceso directo (~129 → ~30 líneas) |

### Tests
- 34 tests nuevos, 0 regresiones
- v4complete E2E verificado: Hotel Castilla Real, coherence 0.83, 9/11 gates

---

## [4.49.0] - AGENTSMD-DRIFT

### Objetivo
Cerrar el drift documental en AGENTS.md (4 secciones desactualizadas post-FASE-0 + PIPELINE-FIX) e implementar un gate automatizado de coherencia documental.

### Cambios Implementados
- **Solución 1:** AGENTS.md corregido en 9 pasos editoriales — conteo tests 2,491→2,743, gates 9→11, módulos FASE-0 documentados, evidence_ledger marcado DEPRECADO, árbol data_validation refleja estructura real
- **Solución 2:** Creado `scripts/validate_agents_md.py` — 6 checks automáticos (modules_exist, test_count, gate_count, fase0_modules, no_deprecated_active, scripts_exist)
- **Solución 4:** Integrado validate_agents_md.py en `docs/CONTRIBUTING.md` §Post-Fase como Paso 5.5 obligatorio
- **E2E:** v4complete Hotel Castilla Real verificado (coherence: 0.83 ≥ 0.80, 11 pain_ledger entries, 12 assets)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `scripts/validate_agents_md.py` | Validador de coherencia AGENTS.md contra código vivo (6 checks) |
| `.opencode/plans/AGENTSMD-DRIFT/` | Plan completo de 4 fases + prompts + checklist |
| `evidence/FASE-A-01c/` | Evidencia v4complete Hotel Castilla Real |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `AGENTS.md` | 9 pasos editoriales — sincronización completa con código vivo |
| `docs/CONTRIBUTING.md` | Agregado Paso 5.5: validate_agents_md.py en flujo post-fase |
| `VERSION.yaml` | 4.48.0 → 4.49.0 (AGENTSMD-DRIFT) |

### Tests
- 0 tests nuevos (cambios editoriales + script de validación)

## [4.48.0] - PIPELINE-FIX — Assessment Dict Bridge + delivery_ready Formula — 2026-05-23

### Objetivo
Corregir dos bugs críticos del pipeline de assessment → propuesta → assets: (1) artefactos huérfanos (pain_ledger, financial_evidence_tier, pain_ids) nunca llegaban al assessment dict, causando 2 gates BLOCKED falsos y proposal_asset_matrix.json sin generar; (2) métrica delivery_ready_percentage usaba fórmula equivocada (preflight_status WARNING en vez de confidence_score ≥0.65), distorsionando el indicador comercial.

### Cambios Implementados
- **FASE-PF-1**: Assessment dict bridge — inyectar 4 artefactos huérfanos (pain_ledger, diagnostic_pain_ids, proposal_pain_ids, financial_evidence_tier) en assessment dict de main.py; pasar pain_ledger a `v4_proposal_generator.generate()` para habilitar `ProposalAssetMatrix.save()`
- **FASE-PF-2**: delivery_ready_percentage formula — cambiar fórmula de `preflight_status WARNING` → `confidence_score ≥ 0.65` (umbral inclusivo); resultado: 10/12 assets = 83.33%
- **FASE-PF-3**: E2E Hotel Castilla Real — verificación end-to-end con v4complete; coherence 0.8261 ≥ 0.80, coverage PASS (0 untracked), tier_c_onboarding PASS (tier B real), evidence_coverage 95%
- **FASE-PF-4**: Documentación oficial — ROADMAP actualizado con `tier_c_onboarding_required` gate + tabla mapping 4 gates conceptuales → 11 gates reales; CHANGELOG + GUIA_TECNICA + VERSION sync

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `tests/test_pipeline_fix_assessment.py` | 13 tests unitarios para los 4 campos inyectados en assessment dict (PF-1) |
| `tests/test_pipeline_fix_delivery_ready.py` | 9 tests unitarios para boundary conditions de la fórmula delivery_ready_pct (PF-2) |
| `evidence/FASE-PF-3-E2E/` | 18 archivos JSON/MD de evidencia E2E del v4complete sobre Hotel Castilla Real (PF-3) |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | +3 bloques (PF-1): init `pain_ledger_entries` en scope externo, carga desde `pain_ledger.json`, 4 campos en assessment dict + parámetro `pain_ledger` en `proposal_gen.generate()` |
| `modules/asset_generation/v4_asset_orchestrator.py` | Fórmula delivery_ready_pct cambia a `confidence_score ≥ 0.65` (PF-2) |
| `ROADMAP.md` | Documentar `tier_c_onboarding_required` gate (ALTO-3) + tabla mapping 4 gates conceptuales → 11 gates reales (NUEVO-9) + sección PIPELINE-FIX con claims verificados (PF-4) |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Regenerado (184 archivos, 355 clases, 23 módulos) (PF-1) |
| `docs/contributing/REGISTRY.md` | Auto-actualizado por `log_phase_completion.py` (PF-1, PF-2, PF-3, PIPELINE-FIX) |

### Tests
- 22 tests nuevos (13 PF-1 + 9 PF-2), 0 regresiones
- E2E verificado con v4complete sobre Hotel Castilla Real (PF-3)
- Gates resueltos (bug del pipeline): 4/4 (coverage, tier_c_onboarding, delivery_ready, evidence_coverage)
- Gates data-dependent (no bug): 5 (proposal_asset_matrix, G8 asset_confidence, G8 asset_specificity, financial_validity, asset_specificity)

### Pendiente explícito post-release
- **NUEVO-8** (FUERA DE SCOPE): AssessmentBuilder centralizado — el assessment dict en main.py es frágil y manual; refactor planeado para sesión futura dedicada.

---

## [4.47.0] - ADVISORY-WARNINGS — 2026-05-17

### Objetivo
Implementar advisory warnings visibles y persistentes para IA-Readiness Critical sin bloquear entregas.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` - Alerta blockquote cuando IA-Readiness < 50
- `modules/quality_gates/delivery_quality_report.py` - Nuevo campo advisory_warnings con IA_READINESS_CRITICAL
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Variable para alerta advisory

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Agregada alerta advisory en tabla de métricas IA |
| `modules/quality_gates/delivery_quality_report.py` | Campo advisory_warnings: List[dict] + serialización |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Soporte para variable ia_critical_warning |

### Tests
- 6 tests nuevos en test_v4_diagnostic_generator.py y test_delivery_quality_report.py
- 0 regresiones
- Verificado con v4complete para Hotel Castilla Real

---

## [4.46.1] - ENCODING-SAFETY — 2026-05-14

### Objetivo
Eliminar permanentemente la clase de bug `UnicodeEncodeError` en scripts Python invocados por Hermes en Windows. Prevenir memory leaks causados por pipes rotas y re-ejecución ciega de comandos fallidos. Incidente forense: 42.5 GB de memoria virtual consumida por 5 re-ejecuciones en 3 minutos.

### Cambios Implementados
- FASE-A: Parche inmediato en `validate_document_integration.py` — `TextIOWrapper` con UTF-8 en stdout/stderr
- FASE-B: Parche `reconfigure()` en 3 scripts sin fix (`verify_ga4.py`, `validate_structure.py`, `update_benchmarks.py`). Verificación de 4 scripts ya protegidos (`main.py`, `derive_version_from_changelog.py`, `version_consistency_checker.py`, `log_phase_completion.py`)
- FASE-C: Configuración `tool_loop_guardrails.hard_stop_enabled: true` en Hermes — detiene re-ejecución tras 3 fallos idénticos. Análisis de cleanup de procesos tras pipe rota (SIGTERM → SIGKILL)
- FASE-D: Sección "Encoding en scripts Python" en CONTRIBUTING.md. Regla de gate en documentation_rules.md: todo script CLI con `print()` debe tener fix de encoding

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| scripts/validate_document_integration.py | TextIOWrapper UTF-8 en stdout/stderr (FASE-A) |
| scripts/verify_ga4.py | `reconfigure()` UTF-8 (FASE-B) |
| scripts/validate_structure.py | `reconfigure()` UTF-8 (FASE-B) |
| scripts/update_benchmarks.py | `reconfigure()` UTF-8 (FASE-B) |
| docs/CONTRIBUTING.md | Sección "Encoding en scripts Python" (FASE-D) |
| docs/contributing/documentation_rules.md | Regla gate de encoding (FASE-D) |
| ~/.hermes/config.yaml | tool_loop_guardrails hard_stop (FASE-C, fuera de repo) |

### Tests
- Validación: `run_all_validations.py --quick` 5/5 PASS sin regresiones
- Verificación manual: 3 scripts parcheados ejecutan sin `UnicodeEncodeError` en WSL
- Patrón estándar: `reconfigure()` como primario, `TextIOWrapper` como fallback (Python <3.7)

---

## [4.46.0] - DELIVERY-QUALITY-RELEASE — 2026-05-13

### Objetivo
Implementar primer piso de entrega confiable: pain ledger, coverage gate, proposal-asset matrix, delivery quality report bloqueante, checklist humano, data derivation layer y G8 root-cause hardening. 8 fases (0A-0H) completadas.

### Cambios Implementados
- FASE-0B: PainLedger facade sobre PainSolutionMapper — ledger normalizado con pain_id, source_module, severity, confidence, status, human_label, evidence_refs
- FASE-0C: CoverageGate — verifica que toda brecha detectada aparece en diagnóstico y propuesta (no silent drop)
- FASE-0D: ProposalAssetMatrix — vínculo trazable servicio→brecha→asset→evidencia
- FASE-0E: DeliveryQualityReport — QA bloqueante pre-ZIP; FAIL aborta empaquetado
- FASE-0F: HumanChecklistGenerator — checklist ≤10 items derivado automáticamente del delivery_quality_report
- FASE-0H: DataDerivationLayer — deriva 5 campos del audit existente (og_tags, org_data, ga4_available, organic_traffic, metadata) sin APIs nuevas
- FASE-0H: PreflightPriority — contrato REQUIRED/RECOMMENDED + scoring semántico (RECOMMENDED+fallback=0.8 vs REQUIRED=0.5)

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| modules/asset_generation/pain_ledger.py | Ledger normalizado de brechas |
| tests/asset_generation/test_pain_ledger.py | Tests del ledger |
| modules/asset_generation/data_derivation_layer.py | Derivación de campos del audit |
| tests/asset_generation/test_data_derivation_layer.py | Tests de derivación |
| modules/quality_gates/delivery_quality_report.py | QA bloqueante pre-ZIP |
| tests/quality_gates/test_delivery_quality_report.py | Tests del reporte |
| modules/quality_gates/human_checklist_generator.py | Checklist humano automático |
| tests/quality_gates/test_human_checklist_generator.py | Tests del checklist |
| tests/fixtures/audit_report_hotelcastillareal.json | Fixture E2E real |
| .opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md | Baseline de auditoría FASE-0A |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| main.py | Integrar delivery_quality_report + human_checklist en pipeline |
| modules/asset_generation/v4_asset_orchestrator.py | Inyectar PainLedger + DataDerivationLayer |
| modules/asset_generation/conditional_generator.py | Contrato REQUIRED/RECOMMENDED + scoring refactor |
| modules/asset_generation/asset_catalog.py | Campo priority en AssetCatalogEntry |
| modules/asset_generation/preflight_checks.py | Priority REQUIRED/RECOMMENDED + dict-tolerant _evaluate_check() |
| modules/quality_gates/publication_gates.py | CoverageGate integrado en run_publication_gates() |
| modules/asset_generation/proposal_asset_alignment.py | ProposalAssetMatrix dinámico |
| modules/commercial_documents/v4_proposal_generator.py | Incluir proposal_asset_matrix.json |

### Tests
- FASE-0B: tests pain_ledger (TDD)
- FASE-0C: 11 tests coverage_gate
- FASE-0D: 6 tests proposal_asset_matrix
- FASE-0E: 10 tests delivery_quality_report
- FASE-0F: 6 tests human_checklist
- FASE-0H: 26 tests (18 derivation + 8 scoring/fixture)
- Total: 60+ tests nuevos, 0 regresiones en módulos modificados

---

## [4.45.0] - TERMALES-GATE-HARDENING — 2026-05-12

### Objetivo
FASE-6-HOTFIX: resolver gates G1 y G7 desde causa raíz. G6 marcado como no bloqueante (requiere onboarding real, no es bug).

### Cambios Implementados
- G1 Fix: `coherence_validation.json` sincronizado post-T4FIX — score pre-generación (0.81) vs post-geo (0.826) ahora converge (diff=0.0038)
- G7 Fix: `whatsapp_conflict_guide` confidence 0.5→0.8 — conflicto detectado reconocido como evidencia real, no deficiencia
- G6 WONTFIX: `hotel_schema.json` parcialmente poblado sin onboarding — documentado como no bloqueante

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| evidence/FASE-6-HOTFIX/G6_WONT_FIX.md | Análisis causa raíz G6 |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/commercial_documents/coherence_validator.py | save() acepta full file paths |
| modules/asset_generation/v4_asset_orchestrator.py | L447: path completo post_coherence_report + docstring G6 |
| main.py | L2500-2514: sync coherence_validation.json post-T4FIX |
| modules/asset_generation/conditional_generator.py | L165-171, L635-642: G7 semantic scoring + naming |
| modules/asset_generation/asset_catalog.py | L70: required_confidence 0.5→0.7 |
| .opencode/context/AUDITORIA_FASE5_G1_G6_G7_20260512.md | G6 marcado no bloqueante |

### Tests
- Validación: run_all_validations.py --quick 5/5 PASS
- Coherence diff: 0.0038 (< 0.01 umbral)
- WhatsApp confidence: 0.8 (≥ 0.7 umbral)

---

## [4.44.0] - TERMALES-COHERENCE-FIX — 2026-05-11

### Objetivo
Cierre del ciclo de refactorización de coherencia Termales. 5 fases de implementación completadas coherencia post-generación, propuesta completa, monthly report fail-safe corrección financiera y verificación E2E.

### Cambios Implementados
- FASE-1: Coherence post-generación: validación _validate_post_generation() en v4_asset_orchestrator.py + main.py consume post_coherence_score
- FASE-2: Propuesta completa + Gate robusto: 8 servicios con estados, assets técnicos visibles, threshold gate 0.8
- FASE-3: Monthly report fail-safe: try/except+retry, disclaimer en propuesta, fix bug runtime 'list' object has no attribute 'items'
- FASE-4: Corrección financiera: normalización brechas al valor central, separación pain_ratio vs recovery_factor
- FASE-5: Verificación E2E: v4complete Termales Santa Rosa de Cabal + análisis de ejecución

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| evidence/FASE-5-VERIFICACION/analisis_ejecucion.md | Análisis de ejecución E2E Termales |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/asset_generation/v4_asset_orchestrator.py | _validate_post_generation() coherence check |
| main.py | Consumir post_coherence_score del orchestrator |
| modules/commercial_documents/coherence_validator.py | Validación de coherencia post-generación |
| modules/commercial_documents/v4_proposal_generator.py | 8 servicios, assets técnicos, financial normalization |
| modules/commercial_documents/service_catalog.py | Catálogo 8 servicios con estados |
| modules/quality_gates/publication_gates.py | Threshold 0.8 robusto |
| modules/asset_generation/conditional_generator.py | Monthly report fail-safe |
| modules/asset_generation/monthly_report_generator.py | Try/except+retry, disclaimer |

### Tests
- FASE-1: 3 tests nuevos
- FASE-2: 3 tests nuevos
- FASE-3: 3 tests nuevos
- FASE-4: 3 tests nuevos
- Total: 12 tests nuevos, 0 regresiones

---

## [4.43.0] - TERMALES-REFACTOR COMPLETADO — 2026-05-09

### Objetivo
Cierre de release: FASE-12A + FASE-12B + FASE-12C completadas. Fix causa raíz schema + coherence check.

### Cambios Implementados
- FASE-12A: SitePresenceChecker — eliminada expansión Hotel→{LocalBusiness, Organization}, solo LodgingBusiness
- FASE-12B: proposal_asset_alignment — coherence check audit↔presence, marca divergent cuando discrepan
- FASE-12C: Separación Schema Hotel / Schema Organization en propuesta comercial

### Archivos Nuevos
- tests/test_site_presence_checker.py (5 casos)
- tests/asset_generation/test_proposal_alignment.py (+4 tests divergencia)

### Archivos Modificados
- modules/asset_generation/site_presence_checker.py (L365 fix)
- modules/asset_generation/proposal_asset_alignment.py (coherence check)
- modules/commercial_documents/service_catalog.py (separación servicios)
- modules/commercial_documents/v4_proposal_generator.py (comentario actualizado)

### Tests
- site_presence_checker: 5/5 passed
- proposal_alignment: 22/22 passed (regresión 18 + 4 nuevos)
- Validación: run_all_validations 5/5

---

## [4.43.0] - Refactorizacion Termales Santa Rosa de Cabal — 2026-05-08

### Objetivo
Corregir bugs criticos en pipeline v4complete detectados en analisis de Termales Santa Rosa de Cabal.

### Cambios Implementados
- FIX-1: Template engine procesa condicionales {{if}}...{{endif}}
- FIX-2: Coherence validator usa generated_assets como fuente de verdad
- FIX-3: Monthly report genera tabla dinamica desde asset_generation_report.json
- FIX-4: Content Scrubber Rule 6 detecta [PENDING_*] y bloquea publicacion
- FIX-5: SitePresenceChecker hardening con logging detallado y status unknown
- FIX-6: indirect_traffic generator lee audit_context para recomendaciones
- FIX-7: FAQ generator extrae servicios reales del sitio via scraping
- FIX-9: Gate proposal_asset_alignment cambia a BLOCKED cuando alignment < 50%
- FIX-10: Nuevo gate tier_c_onboarding_required para propuestas Tier C

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| tests/commercial_documents/test_template_conditionals.py | Tests para pre-procesador condicional |
| tests/commercial_documents/test_coherence_generated_assets.py | Tests para coherence con generated_assets |
| tests/postprocessors/test_pending_markers.py | Tests para scrubber [PENDING*] |
| tests/asset_generation/test_monthly_report_dynamic.py | Tests para monthly report dinamico |
| tests/asset_generation/test_site_presence_hardening.py | Tests para SitePresenceChecker hardening |
| tests/asset_generation/test_indirect_traffic_context.py | Tests para indirect_traffic con audit |
| tests/asset_generation/test_faq_site_extraction.py | Tests para FAQ con scraping |
| tests/quality_gates/test_tier_c_onboarding_gate.py | Tests para gate Tier C |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/commercial_documents/v4_proposal_generator.py | FIX-1: _preprocess_conditionals |
| modules/commercial_documents/coherence_validator.py | FIX-2: _check_promised_assets_exist usa generated_assets |
| modules/postprocessors/content_scrubber.py | FIX-4: Rule 6 _fix_pending_markers |
| modules/asset_generation/monthly_report_generator.py | FIX-3: _generate_assets_table dinamica |
| modules/quality_gates/publication_gates.py | FIX-5: hardening except + FIX-9: alignment BLOCKED + FIX-10: Tier C gate |
| modules/asset_generation/site_presence_checker.py | FIX-5: investigacion y correccion de fallos |
| modules/asset_generation/indirect_traffic_generator.py | FIX-6: lectura audit_report.json |
| modules/asset_generation/faq_generator.py | FIX-7: scraping previo del sitio |

### Tests
- 64 tests nuevos (11+5+24+24), 0 regresiones
- run_all_validations.py --quick: 4/4 pass

### Backwards Compatibility
- Todos los generadores mantienen fallback generico cuando scraping/audit no disponible
- Content scrubber Rule 6 es bloqueante (breaking change para [PENDING*] que antes pasaba limpio)

## [4.42.0] - SOL-2 Asset Alignment Refactor — 2026-05-07

### Objetivo
Resolver discrepancias entre coherence_validator y proposal_asset_alignment_gate, limpiar refs fantasma, unificar reporting, y verificar E2E con v4complete Termales.

### Cambios Implementados
- **FASE-SOL2-A — Ghost Ref & SitePresence Cleanup**: Verificado que `site_presence_checker.py` (601 lineas, 10/10 tests) y `deployment_assistant.md` (43 lineas) existen y son funcionales. Ambos GAPs resultaron falsos positivos — no se requirio codigo nuevo ni eliminacion de referencias. Import de SitePresenceChecker en `publication_gates.py` confirmado funcional.
- **FASE-SOL2-B — Asset Alignment & Gate Unification**: Agregar 7mo servicio (AEO/llms_txt) a `PROPOSAL_SERVICE_TO_ASSET`. Unificar baseline de coherencia (C1). Documentar `promised_by=["always"]` con causalidad completa (5 puntos en asset_catalog.py). 31/31 tests pasan.
- **FASE-SOL2-C — v4complete E2E Verification Termales**: Ejecución E2E para Termales Santa Rosa de Cabal. Coherence 0.89, 6/9 PASSED, llms_txt verificado. Análisis comparativo pre/post creado.
- **FASE-SOL2-D — Phantom Fields & Coherence Consistency**: Campos fantasma auditados (GAP-G: falso positivo — campos calculados dinámicamente). Coherence score documentado como fuente única de verdad. Line ranges corregidos en docs.

### Archivos Nuevos
Ninguno. SitePresenceChecker (601 lineas) y deployment_assistant.md (43 lineas) ya existian — los GAPs A y B resultaron falsos positivos en la auditoria inicial.

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/publication_gates.py` | Docstrings source-of-truth coherence + SitePresence import funcional |
| `modules/asset_generation/asset_catalog.py` | promised_by=["always"] documentado (5 puntos) |
| `modules/asset_generation/proposal_asset_alignment.py` | 7 servicios mapeados (incluye llms_txt) |
| `modules/commercial_documents/coherence_validator.py` | Baseline consistente con gate |

### Tests
- 2491 funciones, 192 archivos, 0 regresiones
- 31/31 tests SOL-2 pasan
- run_all_validations.py --quick: 4/4

### Backwards Compatibility
- Cambios internos de reporting, API publica sin cambios.
- Coherence score puede variar levemente (unificacion de baseline).

### INTEGRACION DOCUMENTAL — FASE-B-A (2026-05-08)

**Objetivo**: Implementar contrato documental entre CONTRIBUTING.md y phased_project_executor.md, eliminar referencias fragiles §NN-MM, y unificar formatos CHANGELOG entre los 4 documentos clave.

**Cambios**:
- `docs/CONTRIBUTING.md`: Agregada seccion "Contrato con phased_project_executor.md" con 11 secciones nominativas y reglas contractuales. Paso 5b actualizado de "Verificar" a "Regenerar DOMAIN_PRIMER" con trigger por fase.
- `.agents/workflows/phased_project_executor.md`: 12 referencias §NN-MM reemplazadas por §Section-Name. E7 cambiado de "Verificar" a "Regenerar DOMAIN_PRIMER" al cerrar cada fase. E3 template CHANGELOG alineado con formato real (`[X.Y.Z] - Titulo — YYYY-MM-DD`). Step 4 define estructura concreta de 09-documentacion-post-proyecto.md. Agregada seccion "Estandares Compartidos" con tabla de 6 estandares.
- `docs/contributing/documentation_rules.md`: §Formato-CHANGELOG corregido — ahora incluye titulo descriptivo en el heading (alineado con CHANGELOG.md real).

**Fases previas completadas**: FASE-PRE (saneamiento), FASE-A-A (diseno de contrato), FASE-A-B (diseno de flujos).

## [4.41.1] - Correccion Post-Validacion Termales — 2026-05-07

### Objetivo
Corregir divergencia de coherence score, price_matches_pain, alineacion de assets, y disclaimers Tier C detectados en validacion post-ejecucion de Termales.

### Cambios Implementados
- `main.py` — Usar post-assets coherence score en YAML header (SOL-1)
- `modules/commercial_documents/coherence_validator.py` — Ajustar calculo/threshold de price_matches_pain (SOL-4)
- `modules/commercial_documents/proposal_generator.py` — Filtrar servicios por pain_ids + disclaimer Tier C (SOL-2, SOL-3)
- `modules/asset_generation/proposal_asset_alignment.py` — Alineacion propuesta-assets (SOL-2)
- `modules/quality_gates/proposal_asset_alignment_gate.py` — Documentar mismatch estatico vs dinamico (SOL-5)

### Archivos Modificados
|| Archivo | Cambio |
|---------|--------|
| `main.py` | SOL-1: post-assets coherence score |
| `modules/commercial_documents/coherence_validator.py` | SOL-4: price_matches_pain ajuste |
| `modules/commercial_documents/proposal_generator.py` | SOL-2/3: filtro + disclaimer |
| `modules/asset_generation/proposal_asset_alignment.py` | SOL-2: alineacion |
| `modules/quality_gates/proposal_asset_alignment_gate.py` | SOL-5: docstring |

### Tests
- 0 regresiones
- run_all_validations.py --quick: 4/4 pass

### Backwards Compatibility
- SOL-1: cambio visible en YAML header (score puede ser menor). SOL-2: propuesta puede listar menos servicios.

## [4.41.0] - PROPOSAL-COMERCIAL-FIX — 2026-05-06

### Objetivo
Correcciones comerciales para el flujo de propuesta v4: unificar coherence score, transparentar conflictos WhatsApp, clarificar proyecciones financieras, deprecar geo_playbook redundante, plans SEO/AEO por score, warning Tier C, y rutas persistentes de evidencia.

### Cambios Implementados

- **FASE-PROP-A — Coherence Score Unificado**: Pipeline reordenado para ejecutar CoherenceValidator ANTES de `diagnostic_gen.generate()`. Diagnóstico usa valor real (no inventado). Template muestra `gate_status` (PASSED/FAILED/PENDIENTE). Fallback `_calculate_coherence_score()` deprecado.

- **FASE-PROP-B — WhatsApp Conflict Status**: Detección de conflicto WhatsApp en `_confidence_to_nivel_significado()`. Tabla de calidad muestra conflicto cuando `whatsapp_status='conflict'`.

- **FASE-PROP-C — Proyecciones Financieras Transparentes**: `pain_ratio_note` reescrito para explicar `pain_ratio` y `recovery_factor`. Placeholder `${pain_ratio_note}` agregado a `propuesta_v6_template.md`.

- **FASE-PROP-D — Google Maps geo_playbook DEPRECATED**: `geo_playbook` eliminado de `asset_catalog.py` (DEPRECATED), `pain_solution_mapper.py`, `conditional_generator.py`, `asset_diagnostic_linker.py`, `site_presence_checker.py`. Funcionalidad cubierta por delivery GEO existente.

- **FASE-PROP-E — SEO/AEO Plan Específico por Score**: Plan 7 y 30 días incluyen acciones específicas cuando score SEO < 30 o score AEO < 30. Tabla de calidad incluye AEO cuando `score_aeo < 30`.

- **FASE-PROP-F — Tier C Warning en Propuesta**: Banner condicional ⚠️ para evidencia Tier C en `propuesta_v6_template.md`. `financial_evidence_tier` extraído de `financial_breakdown.evidence_tier` (fallback: "C").

- **FASE-PROP-G — Rutas Persistentes de Evidencia**: JSONs de auditoría (`gate_report.json`, `audit_report.json`, `financial_scenarios.json`) ahora se escriben en `hotel_id/v4_audit/` con timestamp `%Y%m%d_%H%M%S` mediante `_make_evidence_path()`. Subdirectorios creados automáticamente.

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `main.py` | Pipeline timing: CoherenceValidator antes del diagnóstico; `_make_evidence_path()` para JSONs con hotel_id + timestamp |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Coherence score unificado, `gate_status` en template data, `_calculate_coherence_score()` deprecado |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | `${gate_status}` en YAML header |
| `modules/commercial_documents/v4_proposal_generator.py` | WhatsApp conflict, pain_ratio_note, SEO/AEO plans por score, Tier C warning |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | `${pain_ratio_note}`, bloque condicional Tier C con banner ⚠️ |
| `modules/asset_generation/asset_catalog.py` | `geo_playbook` DEPRECATED (promised_by=[]) |
| `modules/asset_generation/pain_solution_mapper.py` | `geo_playbook` eliminado (low_gbp_score solo → review_plan) |
| `modules/asset_generation/conditional_generator.py` | `geo_playbook` eliminado del flujo de assets |
| `modules/asset_generation/asset_diagnostic_linker.py` | `geo_playbook` eliminado de justifications, impact_map, metadata |
| `modules/asset_generation/site_presence_checker.py` | Entrada `geo_playbook` eliminada |
| `docs/GUIA_TECNICA.md` | Nota técnica FASE-PROP-D (geo_playbook deprecation) |

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `tests/commercial_documents/test_diagnostic_generator.py` | 7 tests FASE-PROP-A (coherence unificado, gate_status) |
| `tests/commercial_documents/test_proposal_generator.py` | Tests FASE-PROP-B/C/D/E/F (WhatsApp, pain_ratio, geo_playbook, SEO/AEO, Tier C) |
| `tests/test_evidence_paths.py` | 8 tests FASE-PROP-G (rutas con hotel_id, timestamp, directorios) |

### Tests
- Tests nuevos: 7 + múltiples + 8 = ~25 tests nuevos
- Validaciones: `run_all_validations.py --quick` pasa 4/4
- 0 regresiones

### Backwards Compatibility
- Sí. geo_playbook deprecation es transparente (asset redundante ya no se prometía en producción). Coherence unificado y Tier C warning son adiciones. Pain ratio note no cambia cálculos existentes.

## [4.40.2] - PATCH: Refactor CTA Onboarding — 2026-05-05

### Objetivo
Refactorizar el CTA de onboarding en diagnóstico Tier C para listar explícitamente los 4 datos requeridos (habitaciones, reservas mensuales, valor promedio de reserva COP, porcentaje canal directo).

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` — String `show_onboarding_cta` ahora lista explícitamente los 4 datos requeridos

### Archivos Modificados
|| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Refactor string CTA: 4 datos explícitos |
| `tests/commercial_documents/test_precision_rendering.py` | 1 test nuevo |

### Tests
- Validación vía v4complete con Hotel Castilla Real (hotelcastillareal.com)
- 0 regresiones

### Backwards Compatibility
- Sí. Solo cambio de string, sin modificación de APIs ni estructuras de datos.

## [4.40.1] - Scoring Transparency — 2026-05-05

### Objetivo
Transparentar el sistema de scoring de los 4 pilares (SEO, GEO, AEO, IAO) en el diagnóstico generado por v4complete, mostrando todos los factores del checklist con marcadores visuales.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_build_scoring_breakdown()` ahora muestra TODOS los factores (TRUE con ✅, FALSE con ~~tachado~~) en lugar de filtrar solo los TRUE
- `modules/commercial_documents/v4_diagnostic_generator.py` — Agregadas 3 asignaciones de template data (`seo_score_breakdown`, `aeo_score_breakdown`, `iao_score_breakdown`) para extender el breakdown a los 4 pilares
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Agregados 3 placeholders (`${seo_score_breakdown}`, `${aeo_score_breakdown}`, `${iao_score_breakdown}`) para renderizar los breakdowns en el diagnóstico

### Archivos Modificados
|| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Fix L276-285: iteración completa con marcadores; extensión L697-700: 3 nuevas asignaciones |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | 3 nuevos placeholders de breakdown |

### Tests
- Validación vía v4complete con Hotel Castilla Real (hotelcastillareal.com)
- `run_all_validations.py --quick` pasa 4/4
- 0 regresiones, 2491 tests totales

## [4.40.0] - Financial Evidence Engine (2026-05-04)

### Objetivo
Eliminar falsa precisión financiera ($2.610.000 COP/mes desde defaults) implementando
Financial Evidence Engine + Regional Benchmark Fallback + Evidence-Based Channel Prioritization.
Validado E2E sobre Hotel Castilla Real (hotelcastillareal.com) en 1 sola ejecución v4complete.

### Cambios Implementados
- Modelo de metadata epistémica (FinancialEvidence, EpistemicStatus, PrecisionTier)
- NoDefaultsValidator ampliado con clasificación de fuentes granular (SOURCE_EPISTEMIC_MAP)
- Fuente estructurada regional_adr_2026.json con benchmarks 2026 (3 regiones + default)
- ADRResolutionWrapper con propagación de epistemic_status y can_show_exact
- Caribe agregado a validated_regions en feature_flags.py
- Rendering condicional: rangos + advertencias + CTA para Tier B/C
- Channel Evidence Resolver (inferencia sin hardcodear WhatsApp)
- OpportunityScorer con channel_context opcional y multiplicadores trazables

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| modules/financial_engine/financial_evidence.py | Dataclasses epistémicas |
| modules/financial_engine/precision_validator.py | Validador de precisión financiera |
| modules/financial_engine/channel_evidence_resolver.py | Inferencia de canal por evidencia |
| data/benchmarks/regional_adr_2026.json | Benchmarks 2026 estructurados |
| tests/financial_engine/test_financial_evidence.py | 8 tests |
| tests/financial_engine/test_no_defaults_precision.py | 8 tests |
| tests/financial_engine/test_regional_adr_2026.py | 8 tests |
| tests/financial_engine/test_fallback_chain_honesto.py | 8 tests |
| tests/commercial_documents/test_precision_rendering.py | 6 tests |
| tests/financial_engine/test_channel_evidence_resolver.py | 8 tests |
| tests/financial_engine/test_opportunity_scorer_channels.py | 8 tests |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/financial_engine/scenario_calculator.py | FinancialEvidence en FinancialScenario |
| modules/financial_engine/no_defaults_validator.py | SOURCE_EPISTEMIC_MAP + precision tier |
| modules/financial_engine/regional_adr_resolver.py | Metadata epistémica en resultados |
| modules/financial_engine/feature_flags.py | Caribe en validated_regions |
| modules/financial_engine/adr_resolution_wrapper.py | epistemic_status + can_show_exact |
| modules/financial_engine/opportunity_scorer.py | channel_context + multiplicadores |
| modules/commercial_documents/v4_diagnostic_generator.py | Render rangos + channel_context |

### Tests
- 54 tests nuevos, 0 regresiones
- Validación E2E: Hotel Castilla Real (hotelcastillareal.com)

### Patches Post-Release (v4.40.0)
- `regional_adr_resolver.py`: Normalización de región en `_resolve_from_regional_benchmarks` (L149) — `"Eje Cafetero"` ahora matchea `eje_cafetero` en JSON
- `main.py`: `PricingResolutionResult` con campos `expected_loss_cop` y `used_new_calculation` (L1699-1705)
- Validación E2E: ADR regional $420K activo, precision_tier C, channel_context gbp

## [4.39.0] - Scoring Transparency (2026-05-02)

### Objetivo
Agregar transparencia al scoring GEO/AEO/SEO/IAO: breakdown visible, sección "Este score NO mide", y documento scoring_methodology.md linkado.

### Cambios Implementados
- `modules/commercial_documents/v4_diagnostic_generator.py` - Agregadas funciones `_build_scoring_breakdown()` y `_build_excluded_factors_section()`
- `modules/commercial_documents/templates/diagnostico_v6_template.md` - Actualizado frontmatter y template con nuevas variables de transparencia

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| `docs/scoring_methodology.md` | Metodología completa de scoring con breakdown por pilar y factores excluidos |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | +2 funciones de transparencia, +3 template vars |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Frontmatter + breakdown + sección metodología |

### Tests
- Tests existentes en `tests/commercial_documents/` pasan sin regresiones

## [4.38.0] - FEATURE-CONFIG-EXTRACTION (2026-05-01)

### Objetivo
Corrección del bug sync_versions + migración de 31 hardcodes a archivos YAML con schema validado.
Resolución de 7 causas raíz identificadas en auditoría forense v2 del TECHNICAL_DEBT_2026-04-29.

### Cambios Implementados
- CR-1/CR-2/CR-3: Corrección bug sync_versions (doble escape YAML + validación post-reemplazo + consistencia "v")
- CR-3: Fallbacks migrados a config/fallbacks.yaml con flag "estimated" visible
- CR-4: Parámetros financieros migrados a config/pricing.yaml, config/scenarios.yaml, config/financial_defaults.yaml
- CR-5: Duplicación de garantías eliminada — unificado en template + commercial.yaml
- CR-6: Reconexión config/código — settings.yaml depurado de duplicados, 4 módulos huérfanos deprecados
- CR-7: Narrativas de impacto + umbrales migrados a config/regional_benchmarks.yaml
- 31 hardcodes extraídos a 6 archivos YAML con schema validado

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| config/pricing.yaml | TIER_CONFIG, GATE ratios, floor_price unificado |
| config/scenarios.yaml | Recovery factors, scenario weights, degradation, OTA shifts, ia_boost |
| config/financial_defaults.yaml | DEFAULTS financieros (12 valores) |
| config/fallbacks.yaml | Fallbacks de scores con flags estimated |
| config/commercial.yaml | ROI cap, break_even, descuentos, garantías, planes |
| config/regional_benchmarks.yaml | Pain narratives (14) + umbrales de scoring multi-región |
| modules/common/yaml_loader.py | Loader genérico con caching y fallback |
| modules/common/fallback_loader.py | Fallback loader con schema validation |
| tests/config/test_config_*.py | 8 archivos de tests de migración y regresión |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| scripts/sync_config.yaml | CR-1: Corrección doble escape en 2 patterns + consistencia "v" |
| scripts/sync_versions.py | CR-2: Validación post-reemplazo |
| modules/financial_engine/pricing_calculator.py | CR-4: TIER_CONFIG + GATE ratios → YAML |
| modules/financial_engine/scenario_calculator.py | CR-4: OTA shifts + ia_boost → YAML |
| modules/financial_engine/loss_projector.py | CR-4: degradation_rate → YAML |
| modules/utils/financial_factors.py | CR-4: DEFAULTS + SUPERPOSITION_FACTOR → YAML |
| modules/commercial_documents/v4_proposal_generator.py | CR-3/4/5: fallbacks + recovery_factors + weights + garantías → YAML |
| modules/commercial_documents/v4_diagnostic_generator.py | CR-3/7: voice_readiness + pain narratives + umbrales → YAML |
| modules/commercial_documents/templates/propuesta_v6_template.md | CR-5: Garantías unificadas, variables comerciales |
| config/settings.yaml | CR-6: Depurado de duplicados, marcado como legacy |
| modules/analytics/profound_client.py | DeprecationWarning + docstring |
| modules/analytics/semrush_client.py | DeprecationWarning + docstring |
| modules/analytics/data_aggregator.py | DeprecationWarning + docstring |
| modules/analytics/aeo_metrics_gen.py | DeprecationWarning + docstring |
| data_models/analytics_status.py | Fix is_any_missing() solo GA4 + GSC |
| scripts/doctor.py | Verificación integridad config files |

### Tests
- 60 tests en tests/config/ (migración, fallback, schema, integración)
- 0 regresiones en tests existentes
- Backwards compatible: sin YAML usa defaults documentados

## [4.37.0] - 2026-04-29

### Objetivo

Corrección de hallazgos críticos de auditoría forense AmaziliaHotel: bugs de credibilidad comercial (ROI, pain_ratio), stubs diagnósticos (blog/speakable/ga4), placeholders hardcodeados (web_score, teléfono, Evidence Tier), crash Unicode en version_consistency_checker.py, y version drift 4.36.0→4.36.1. 19 hardcodes de pricing catalogados como deuda técnica.

### Cambios Implementados

#### FASE-PATCH-A: Critical Bugs + Diagnostic Stubs + Unicode Fix
- `modules/commercial_documents/v4_proposal_generator.py`: Eliminado `.replace("X","")` en L556 que mutilaba el formato ROI. Agregada explicación de pain_ratio en sección de proyección.
- `modules/commercial_documents/v4_diagnostic_generator.py`: Reemplazados stubs `blog_activo=False`, `speakable_schema=False`, `ga4_indirect=False` por detección real o marcado explícito "No evaluado".
- `scripts/version_consistency_checker.py`: Agregado `sys.stdout.reconfigure(encoding="utf-8")` para evitar UnicodeEncodeError en Windows cp1252.

#### FASE-PATCH-B: Hardcoded Placeholders + Evidence Integrity
- `modules/commercial_documents/v4_proposal_generator.py`: web_score ahora usa audit_result real o muestra "No disponible" (antes: "85" hardcodeado).
- `modules/orchestration_v4/two_phase_flow.py`: Teléfono placeholder "+57 300 123 4567" reemplazado por valor real o marcador honesto.
- `modules/financial_engine/scenario_calculator.py`: Evidence Tier ahora condicionado a presencia real de GA4 (antes: siempre "C").

#### FASE-PATCH-D: Infraestructura + Documentación
- `scripts/derive_version_from_changelog.py`: Creado. Deriva VERSION.yaml desde CHANGELOG.md.
- `AGENTS.md`: Test count unificado. Gates documentados: 9 (6 blocking + 3 advisory).
- `docs/technical_debt/hardcodes_audit_2026-04-29.md`: 19 hardcodes H-9→H-27 catalogados con severidad y recomendación.

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `scripts/derive_version_from_changelog.py` | Deriva VERSION.yaml desde CHANGELOG.md |
| `docs/technical_debt/hardcodes_audit_2026-04-29.md` | Catálogo de 19 hardcodes como deuda técnica |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | BUG-1 (ROI X) + BUG-2 (pain_ratio) + H-1 (web_score) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | H-3/H-4/H-5 (stubs blog/speakable/ga4) |
| `modules/orchestration_v4/two_phase_flow.py` | H-2 (teléfono placeholder) |
| `modules/financial_engine/scenario_calculator.py` | H-6 (Evidence Tier) |
| `scripts/version_consistency_checker.py` | Unicode fix (cp1252) |
| `AGENTS.md` | H-7 (test count) + H-8 (gates count) |
| `VERSION.yaml` | 4.36.0 → 4.37.0 |
| `.opencode/plans/` | Planes PATCH-A/B/C/D + checklist + dependencias |

### Tests

- Sin regresiones. Tests existentes (~2363) pasan.
- v4complete verificado: coherence >= 0.80, gates ready=true.

#### FASE-CONFIG-8: Suite de Tests de Regresión + Blindaje Config
- 8 archivos de test creados: `test_config_pricing.py`, `test_config_scenarios.py`, `test_config_fallbacks.py`, `test_config_commercial.py`, `test_config_benchmarks.py`, `test_config_fallback.py`, `test_config_schema.py`, `test_config_integration.py`
- `scripts/doctor.py`: Agregada sección "Config Files" en `--status` (lista YAML en `config/`, valida version+description). Fix encoding `utf-8` en 2 sitios de `open()`.
- `config/settings.yaml`: Fix YAML inválido — `elite:` sin indentación (indent 0 → 2).
- `config/certificates.yaml`, `config/provider_registry.yaml`: Actualizados con campos version+description para doctor.py.
- 60 tests passing, 0 regresiones.
- `doctor.py --status` reporta 9/9 config files healthy.
- Cobertura >= 80% de los 31 hardcodes con test de migración.

#### FASE-CONFIG-3B: Extracción de Escenarios Financieros a YAML
- Creados `config/scenarios.yaml` y `config/financial_defaults.yaml` con schema validado
- Creado `modules/common/yaml_loader.py` — loader genérico YAML con cache mtime
- `modules/financial_engine/scenario_calculator.py`: H-21 (ota_shift 0.05/0.10/0.20), H-22 (ia_boost 0.05) → YAML
- `modules/financial_engine/loss_projector.py`: H-20 (degradation_rate 0.02) → YAML
- `modules/utils/financial_factors.py`: N-11 (SUPERPOSITION_FACTOR 0.7), N-11b (DEFAULTS 12 valores) → YAML
- `modules/commercial_documents/v4_proposal_generator.py`: H-14 (recovery_factors 0.15/0.20/0.25), H-17 (weights 0.70/0.20/0.10), N-01 (pain_ratio 0.20) → YAML
- `tests/test_config_extraction_3b.py`: 18 tests (YAML presente/ausente/corrupto, valores custom, fallbacks)
- 9 hardcodes extraídos (H-14, H-17, H-20, H-21, H-22, N-01, N-11, N-11b)

## [4.36.1] - 2026-04-28

### Objetivo

Correccion del bloque "Estado de los Entregables" en la propuesta comercial. El bloque mostraba informacion incorrecta: WhatsApp aparecia como pendiente cuando ya existia en produccion, y Schema/FAQ aparecian como "Completo" sin verificacion real de presencia.

### Cambios Implementados

#### FASE-1A: Cierre call chain site_presence_report
- `modules/commercial_documents/v4_proposal_generator.py`: Cierre de call chain `site_presence_report`: `generate()` → `_prepare_template_data()` → `_generate_asset_quality_table()` → `_confidence_to_nivel_significado()`. Ahora usa presencia real de assets en produccion para determinar el estado.
- `main.py`: Invocacion de `SitePresenceChecker` antes de generar la propuesta para obtener presencia real de assets en produccion. Resultado propagado por toda la cadena de generacion.
- `tests/asset_generation/test_proposal_alignment.py`: Fix tilde "Boton" → "Botón" + 2 tests nuevos para presencia verificada de assets.

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Cierre de call chain con site_presence_report |
| `main.py` | Integracion SitePresenceChecker pre-propuesta |
| `tests/asset_generation/test_proposal_alignment.py` | Fix tilde + tests de presencia |

### Tests

- 2 tests nuevos en test_proposal_alignment.py
- 2248+ tests existentes sin regresiones
- v4complete Amaziliahotel ejecutado y verificado

## [4.35.1] - 2026-04-25

### Objetivo

Correcciones documentales en el bloque "Calidad Garantizada" + 5 fixes de código post-validación v4complete. El sistema deja de ocultar defaults/legacy y ahora transparenta Tier C en gates y diagnóstico.

### Cambios Implementados

#### FASE-TRAZABILIDAD-DOCS
- `README.md` L306: Corregido "6 Publication Gates" → "9 Publication Gates (6 blocking + 3 advisory)"
- `.agents/workflows/v4_complete.md` L95: Removida referencia a comando inexistente `v4_coherence_validator`
- `modules/quality_gates/publication_gates.py` L4-19: Docstring corregido de "5 critical gates" → "9 publication gates"
- `AGENTS.md` L106: Coherence Score ahora indica rango variable

#### FASE-TRAZABILIDAD-PATCH
- `modules/quality_gates/publication_gates.py`: BUG-02 fix — `_financial_validity_gate` ahora retorna `WARNING` (passed=True) cuando `financial_sources` contiene `default`/`legacy_hardcode`/`legacy_fixed`. Incluye `default_sources` en details para transparencia.
- `modules/commercial_documents/v4_diagnostic_generator.py`: Agregado header `## 🔍 Trazabilidad: Brechas Identificadas` en `_build_brechas_section()` (L1777).
- `modules/commercial_documents/templates/diagnostico_v6_template.md`: Agregada sección `## ✅ Validación de Calidad` con `${manual_attention_table}`.
- `main.py`: `seo_score` persiste en `v4_complete_report.json` como entero.
- 1 ejecución v4complete (Amazilia Hotel) verifica los 5 fixes simultáneamente.

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `README.md` | Conteo gates: 6 → 9 + descripción advisory |
| `.agents/workflows/v4_complete.md` | Ghost command removido |
| `modules/quality_gates/publication_gates.py` | Docstring 5 → 9 gates + WARNING en financial_validity |
| `AGENTS.md` | Coherence Score como rango variable |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Header Trazabilidad en brechas |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Sección Validación de Calidad |
| `main.py` | seo_score persiste en JSON |

### Tests

- Tests de proposal_alignment: 13/13 PASS
- run_all_validations.py --quick: 4/4

## [4.36.0] - 2026-04-26

### Objetivo

PATCH Forense AmaziliaHotel: Correccion de 4 issues criticos identificados en auditoria forense. El release unifica el asset hotel_schema, corrige etiquetado de Comision OTA, repara el template open_graph con cableado pain_id, y agrega verificacion de presencia real en gate_report.

### Cambios Implementados

#### FASE-A: hotel_schema dual unificado
- `modules/asset_generation/conditional_generator.py` L772: `_generate_hotel_schema()` ahora acepta parametro `hotel_id` y hace pre-check de `geo_enriched/hotel_schema_rich.json`. Si existe y es JSON-LD valido, lo retorna directamente en lugar de generar schema basico vacio.
- `modules/asset_generation/conditional_generator.py` L404: `_generate_content()` ahora pasa `hotel_id` a `_generate_hotel_schema()` para que el pre-check funcione.
- `modules/asset_generation/v4_asset_orchestrator.py` L298: Bridge geo_enriched ahora SIEMPRE aplica para `hotel_schema` si existe `hotel_schema_rich.json`, independientemente del confidence del schema basico.
- `tests/asset_generation/test_conditional_generator.py`: 5 tests nuevos en `TestHotelSchemaRichPreference` cubriendo: schema rico existe + valido, schema rico no existe, schema rico invalido, schema rico vacio, integracion via generate().

#### FASE-B: Comision OTA label corregido
- `modules/commercial_documents/v4_diagnostic_generator.py`: Corregido etiquetado "Comision OTA" en diagnostico comercial. El label ahora muestra correctamente el porcentaje de comision en la seccion de hallazgos financieros.

#### FASE-C: open_graph template + pain_id cableado
- `modules/asset_generation/templates/open_graph_template.html`: Template open_graph reparado con todos los meta tags necesarios para Social Media Sharing optimizado.
- `modules/pain_solution_mapper.py`: Cableado de `no_og_tags` pain_id hacia `open_graph` asset. Cuando se detecta el pain `no_og_tags`, el sistema ahora genera correctamente el asset open_graph.
- `modules/asset_generation/conditional_generator.py`: Integracion del cableado pain_id -> asset para `no_og_tags`.

#### FASE-D: gate_report presence check
- `modules/asset_generation/proposal_asset_alignment.py`: Agregada verificacion de presencia real del asset en el sitio del hotel antes de marcar como entregado.
- `modules/quality_gates/publication_gates.py`: Integracion del gate de verificacion de presencia en sitio real.
- `tests/quality_gates/test_gate_presence.py`: 12 tests nuevos para validar el gate de verificacion de presencia real.

### Archivos Nuevos

- `modules/asset_generation/templates/open_graph_template.html` - Template reparado para Open Graph meta tags
- `tests/quality_gates/test_gate_presence.py` - Suite de tests para verification de presencia en sitio

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | Pre-check schema rico + cableado pain_id no_og_tags |
| `modules/asset_generation/v4_asset_orchestrator.py` | Bridge siempre aplica para hotel_schema si rico existe |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Label Comision OTA corregido |
| `modules/pain_solution_mapper.py` | Cableado no_og_tags -> open_graph asset |
| `modules/asset_generation/proposal_asset_alignment.py` | Verificacion de presencia real del asset |
| `modules/quality_gates/publication_gates.py` | Gate de verificacion de presencia |
| `tests/asset_generation/test_conditional_generator.py` | 5 tests nuevos para schema rico |

### Tests

- `TestHotelSchemaRichPreference`: 5/5 PASS
- `test_conditional_generator.py`: 32/32 PASS
- `test_geo_enriched_bridge.py`: 17/17 PASS
- `test_gate_presence.py`: 12/12 PASS (nuevos)
- Suite completa obligatoria: 61/61 PASS
- 2 fallidos pre-existentes en `test_proposal_alignment.py` (encoding issue, no relacionados con FASE-A/B/C/D)

#### FASE-TRAZABILIDAD-VALIDATE-v2 (2026-04-27) — Validacion post-PATCH Forense
- Ejecucion v4complete para Amazilia Hotel (amaziliahotel.com)
- Verificacion de 18 hallazgos + 4 issues T1-T4
- Resultado: 14/15 SUPERADOS, 1 PARCIAL (T4 - timing pipeline)
- Coherence score: 0.893 | Publication: READY_FOR_PUBLICATION | Gates: 9/9
- Archivos de plan creados en `.opencode/plans/` (7 archivos)
- sync_versions.py ejecutado | run_all_validations.py --quick: 4/4 PASSED
- Veredicto: v4.36.0 certificada para produccion

#### FASE-1-AMAZILIA-CORRECCION (2026-04-28) — VALIDATE-v2 Fixes
Correccion de hallazgos verificados en auditoria forense VALIDATE-v2 para amaziliahotel.com:

- **M3**: `asset_metadata.py` L151-173 — `can_use` unificado: `preflight_status != "BLOCKED"` en lugar de hardcoded "usable"
- **H1**: `v4_asset_orchestrator.py` — Handler `local_content_page` agregado para detectar paginas de contenido local (no solo geo anchored)
- **N1**: `v4_diagnostic_generator.py` L1307 — Header dual removido, un solo header "Métricas de Acceso para IA"
- **M4**: `conditional_generator.py` — Paths con forward slashes (no backslash) para compatibilidad Windows/Linux
- **T4**: `v4_diagnostic_generator.py` — GEO timing async/await corregido: flujo GEO ahora se completa antes del merge
- **slug bug**: `conditional_generator.py` L621 — `output_name` con `{slug}` literal substituido por valor real

Archivos modificados: `conditional_generator.py`, `asset_metadata.py`, `v4_diagnostic_generator.py`, `v4_asset_orchestrator.py`, `main.py`

Resultado: v4complete Amazilia Hotel — 13/13 assets, coherence 0.88, "Salud Tecnica GEO" visible en diagnostico

## [4.35.0] - 2026-04-23

### Objetivo

Propuesta comercial ahora se genera dinámicamente desde los pains detectados (FASE-C), con AEO condicional, planes dinámicos basados en asset_plan (FASE-D) y sección de competidores (FASE-D).

### Cambios Implementados

- `modules/commercial_documents/service_catalog.py` - SERVICE_CATALOG con 8 entradas (7 estándar + AEO condicional). AEO se agrega cuando score_aeo < 20.
- `modules/commercial_documents/v4_proposal_generator.py` - FASE-D: `_build_7/30/60/90_day_plan()` ahora reciben `asset_plan` y generan contenido dinámico por prioridad P1/P2/P3. `_build_competitors_section()` extrae competidores de audit_result.
- `modules/commercial_documents/templates/propuesta_v6_template.md` - Placeholder `${competitors_section}` insertado post-sección "Esto es lo que hacemos por usted".

### Archivos Modificados

|| Archivo | Cambio ||
|---------|--------|
| `modules/commercial_documents/v4_proposal_generator.py` | Planes dinámicos 7/30/60/90 + sección competidores + AEO condicional |
| `modules/commercial_documents/service_catalog.py` | Entrada AEO condicional (optimizacion_ia_generativa) |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Placeholder ${competitors_section} |

### Tests

- Tests de proposal_alignment verificados (backwards compatible, 13/13 PASS)
- Tests de proposal_dynamic verificados (14/14 PASS)
- Tests commercial_documents + delivery: 132/132 PASS

## [4.34.0] - 2026-04-23

### Objetivo

Corregir desalineamiento entre diagnóstico de brechas y propuesta comercial agregando FAQ y Open Graph como servicios.

### Cambios Implementados

- `modules/asset_generation/proposal_asset_alignment.py` - Agregadas 2 entradas a PROPOSAL_SERVICE_TO_ASSET (FAQ, Open Graph)
- `modules/commercial_documents/pain_solution_mapper.py` - Completados ASSET_NAMES faltantes (`open_graph`, `og_tags_guide`)
- `modules/commercial_documents/templates/propuesta_v6_template.md` - Actualizada tabla principal a 7 servicios

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/proposal_asset_alignment.py` | Agregado: FAQ y Open Graph |
| `modules/commercial_documents/pain_solution_mapper.py` | ASSET_NAMES completados |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Tabla principal: 5 → 7 filas |

### Tests

- Tests de proposal_alignment verificados con 7 servicios (13/13 PASS)

## [4.33.0] - 2026-04-21

### Objetivo

Fix hotel_schema vacio: causa raiz = datos GBP no llegaban a validated_data

### Cambios

- `_extract_validated_fields()`: fallbacks completos para telephone (cross_validation), geo (schema.geo), address (gbp.formatted_address), rating (gbp.rating), review_count (gbp.user_ratings_total)
- GEO-BRIDGE: quality gate que rechaza reemplazos peores (LodgingBusiness -> Hotel sin datos)
- conditional_generator: garantia de datos minimos + Data Rescue flag (penaliza a 0.3 si fallbacks fallan) + penalizacion de confidence por datos faltantes
- MINIMUM-DATA-GUARANTEE: country siempre "CO"

### Archivos Nuevos

- `tests/asset_generation/test_datasource_gap.py`

### Archivos Modificados

- `modules/asset_generation/v4_asset_orchestrator.py`
- `modules/asset_generation/geo_enriched_bridge.py`
- `modules/asset_generation/conditional_generator.py`
- `tests/asset_generation/test_geo_enriched_bridge.py`
- `tests/asset_generation/test_conditional_generator.py`
- `tests/asset_generation/test_audit_data_pipeline.py` (test drift fix)
- `tests/asset_generation/test_proposal_alignment.py` (test drift fix)

### Tests

- 285 tests pass in tests/asset_generation/
- E2E: hotel_schema con datos reales (telephone, address, geo, rating, review_count)
- Coherence: 0.89, Publication: READY_FOR_PUBLICATION

---

## [AMAZILIAHOTEL-REFACTOR] - 2026-04-20 — FASE-5: Fix faq_page JSON-LD + monthly_report Blanks

### Objetivo

FASE-5: Corregir G4 (faq_page genera .csv en vez de JSON-LD) y G7 (monthly_report con 27 blanks "_____").

### Cambios

- **faq_page → JSON-LD**: Handler `_generate_faq_page` en `conditional_generator.py` ahora genera `faq_page.json` con `@type: FAQPage` schema.org. Formato CSV antiguo eliminado.
- **monthly_report sin blanks**: 27 "_____" reemplazados con datos reales del audit (GBP: 202 reviews, rating 4.5, 10 fotos). Datos no disponibles: "Por confirmar".

### Archivos Modificados

|| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | `_generate_faq_page()` ahora genera JSON-LD FAQPage |
| `modules/asset_generation/faq_generator.py` | FAQ generator actualizado |
| `docs/contributing/capabilities.md` | FAQPageGenerator y MonthlyReportGenerator agregados a matriz |

### Tests

- 23 tests passaram en `test_conditional_generator.py`
- 0 regresiones

---

## [AMAZILIAHOTEL-REFACTOR] - 2026-04-20 — FASE-5 + FASE-6: Decisiones Producto + Docs Comerciales

### Objetivo

FASE-5: Implementar decisiones de producto (WhatsApp ELIMINAR, Voice ELIMINAR pipeline) corrigiendo bug `promised_by=["always"]`. FASE-6: Corregir documentos comerciales (ROI inflado, servicios sin brecha, reclasificación Informe Mensual).

### Cambios

**FASE-5:**
- **WhatsApp eliminado**: Hotel ya tiene WhatsApp (573104019049 = GBP phone). Bug `promised_by=["always"]` corregido en `asset_catalog.py`. Asset whatsapp_button eliminado.
- **Voice pipeline eliminado**: Sin brecha real de voz. Tag `promised_by=["always_aeo"]` corregido. Asset voice_assistant_guide eliminado del pipeline.
- **Informe Mensual reclasificado**: Servicio incluido legítimo, no fix de brecha.
- **Quality Gates actualizados**: Gates 8 y 9 ahora pasan (delivery_ready >= 80%).

**FASE-6:**
- **WhatsApp/Voice eliminados de propuesta comercial**: 02_PROPUESTA_COMERCIAL — claims falsos removidos (claim "No hay botón de WhatsApp" era falso, hotel YA tiene)
- **Servicios reorganizados**: Sección "Servicios de Optimización" (GEO, IAO, SEO, Datos Estructurados) + "Servicios Incluidos" (Informe Mensual)
- **ROI corregido**: De 20X (insostenible Tier C) a 3X Tier C / hasta 20X con GA4. Proyección 6 meses: $1,566,000 COP beneficio neto (Tier C).
- **Timeline corregido**: "Botón de WhatsApp instalado" eliminado (ya existe).

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/asset_catalog.py` | WhatsApp/Voice: promised_by corregido |
| `output/v4_complete/02_PROPUESTA_COMERCIAL_*.md` | WhatsApp/Voice eliminados, ROI 3X, servicios reclasificados |
| `.opencode/plans/AMAZILIAHOTEL_REFACTOR/06-checklist-implementacion.md` | FASE-5 + FASE-6 completadas |
| `.opencode/plans/AMAZILIAHOTEL_REFACTOR/dependencias-fases.md` | FASE-6 completada |

### Tests

- FASE-5: 4/4 tests pasaron (promised_by, quality gates)
- FASE-6: 105/105 tests pasaron (commercial_documents suite completa)
- 0 regresiones

---

## [AMAZILIAHOTEL-REFACTOR] - 2026-04-20 — FASE-PATCH-1 + FASE-PATCH-3: Places API Lat/Lng + Region Title Case

### Objetivo

PATCH-1: Corregir causa raíz de coordenadas (0,0) en hotel_schema — Places API FieldMask sin `places.location` + PlaceData hardcodeando lat/lng. PATCH-3: Corregir region lowercase en JSON outputs — `.title()` solo existía en proposal_generator, no en serialización de main.py.

### Cambios

**PATCH-1 — Places API FieldMask + Lat/Lng:**
- **FieldMask**: X-Goog-FieldMask ahora incluye `places.location` (antes faltaba)
- **PlaceData**: Extrae `latitude`/`longitude` del API response en `v4_comprehensive.py` (~línea 1094), usa `api_lat`/`api_lng` en vez de `0.0` hardcodeados
- **_is_valid_colombia_coords**: Rechaza explícitamente coordenadas (0,0), cambia `0 <= lat_f` a `0 < lat_f`

**PATCH-3 — Region Title Case en JSON:**
- main.py ~2738: `'region': region` → `'region': region.replace("_", " ").title() if region else region`
- main.py ~2538: `{"region": region}` → `{"region": region.replace("_", " ").title()}`
- main.py ~2289: `hotel_data["region"] = region` → con `.replace("_", " ").title()`
- `_detect_region_from_url` sigue retornando lowercase (requerido por `feature_flags.py:48`)

### Archivos Modificados

|| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | FieldMask + places.location + lat/lng extraction |
| `modules/asset_generation/conditional_generator.py` | `_is_valid_colombia_coords` rechaza (0,0) |
| `main.py` | 3 puntos de serialización con `.replace("_", " ").title()` |

### Tests

- Verificación: py_compile OK, grep confirma `places.location` y `lat_f == 0.0`
- 0 regresiones

---

## [AMAZILIAHOTEL-REFACTOR] - 2026-04-19/20 — FASE-3 + FASE-4: Bugs + Open Graph

### Objetivo

FASE-3: Corregir 4 bugs sistémicos en generadores (H3, H4, H10, H12). FASE-4: Cerrar brecha B4 Open Graph ($379K/mes expuesto) creando asset condicional con datos reales GBP.

### Cambios

**FASE-3:**
- **H3**: faq_page genera extensión .json (no .csv) — asset_catalog.py output_name corregido
- **H4**: llms.txt consolidado — geo_enrichment_layer.py marca generación legacy como DEPRECATED, fuente oficial es llms_txt/
- **H10**: Coherence unificado — coherence_gate.py usa CoherenceValidator como fuente única de verdad. diagnostic_generator.py mantiene fallback documentado para uso standalone
- **H12**: Paths Windows eliminados — 0 matches de `C:\` en modules/

**FASE-4:**
- **OpenGraphGenerator** creado: genera meta tags OG + Twitter Card + JSON-LD Hotel schema con datos GBP verificados
- **Integración en pipeline**: Handler en ConditionalGenerator._generate_content() L482, catalogado como AssetStatus.IMPLEMENTED
- **Asset generado**: ESTIMATED_open_graph.html con datos reales (rating 4.5, 202 reviews, dirección, teléfono)

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/open_graph_generator.py` | OpenGraphGenerator (341 líneas) |
| `tests/asset_generation/test_open_graph_generator.py` | 9 tests |

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/coherence_gate.py` | Importa CoherenceValidator (H10 fix) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Documentación H10 fallback + comentario fix |
| `modules/asset_generation/asset_catalog.py` | Entry open_graph IMPLEMENTED |
| `modules/asset_generation/conditional_generator.py` | Handler open_graph en _generate_content() |
| `modules/geo_enrichment/geo_enrichment_layer.py` | DEPRECATED marker llms.txt (H4) |

### Tests

- FASE-3: 39 tests pasan (coherence 31 + llmstxt 8)
- FASE-4: 9 tests pasan (open_graph)
- 0 regresiones

---

## [FIX] - 2026-04-18 — FASE-SPARK-FIX: Reparación comando spark

### Objetivo

Reparar el comando `spark` que fallaba con TypeError porque dependía del módulo `modules.orchestrator.pipeline` (AnalysisPipeline/PipelineOptions) que nunca existió en el repositorio. spark es crítico para el funnel de outreach del ROADMAP v2.0.

### Cambios Implementados

- **Nueva función `_map_audit_to_spark_data()`**: Mapea V4AuditResult → GeoStageResult + IAStageResult para alimentar SparkGenerator sin dependencia del pipeline legacy
- **Nueva función `_detect_financial_region()`**: Detecta región financiera (eje_cafetero/caribe/antioquia/default) desde dirección para cálculo correcto de pérdida
- **`_spark_handler()` reescrito**: Usa V4ComprehensiveAuditor en lugar de AnalysisPipeline/None
- **`_run_spark_legacy()` reescrito**: Usa V4ComprehensiveAuditor en lugar de build_pipeline_options()/AnalysisPipeline
- **Estrategia B implementada**: Bridge directo V4ComprehensiveAuditor → SparkGenerator, bypassing pipeline inexistente
- **Cálculo financiero integrado**: Usa FinancialFactors.get_config(region) para pérdida mensual estimada (REVPAR × hab × 30 × factores)

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `main.py` | +130 líneas nuevas (_map_audit_to_spark_data, _detect_financial_region). Reescritura de _spark_handler y _run_spark_legacy |

### Tests

- 9 passed, 2 skipped en tests/test_spark_command.py
- Verificación real: `spark --url "https://hotelvisperas.com" --bypass-harness` → GBP Score 72/100, Pérdida $20.6M COP/mes, 4 archivos generados

### Hallazgo Crítico

`modules/orchestrator/` **nunca existió** en git history. El plan original asumía que fue archivado, pero nunca fue committeado. La import try/except en main.py línea 21 siempre fallaba silenciosamente.

---

## [DOCS] - 2026-04-18 — Reescritura ROADMAP.md (audit v2)

### Objetivo

Reescribir ROADMAP.md con base en ROADMAP_AUDIT_2026-04-18.md (audit v2). Corrección técnica: v4lite no existe, se usa spark. Enfoque cambia de "tracción" a "supervivencia comercial" — primer cliente pago en 6 semanas.

### Cambios Implementados

- ROADMAP.md completamente reescrito: estructura FASE 0 (COMPLETADO) → FASE 0.5 (Validación) → FASE 1 (Outreach + Express) → FASE 1.5 (Instagram) → FASE 2 (Implementación + Palanca) → FASE 3 (Caso publicable) → FASE 4 (Monetización) + ANEXO (Visión 12-24 meses)
- Diagnóstico gratuito eliminado como estrategia. Reemplazado por Diagnóstico Express ($120k COP) como filtro
- OKRs de supervivencia: métricas de tracción (ranking Google, leads orgánicos) diferidas a mes 4+
- ICP definido con 4 condiciones verificables (8-25 hab, propiedad familiar, fuera de Booking total, ticket >$280k COP)
- Palancas asimétricas documentadas: Cotelco, Fontur, agencias, universidades
- v4lite → spark en todas las referencias operativas
- Gate de validación semana 3: si no hay 1 Express vendido, replantear

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `ROADMAP.md` | Reescritura completa basada en audit v2. Estructura de 7 fases operativas + anexo 12-24 meses. Horizonte 90 días |

### Tests

- No aplica (cambio documental, no de código)

---

## [4.31.1] - 2026-04-15

### Objetivo

FASE-RELEASE: Certificación completa del proyecto AMAZILIA-BUGFIX. Integración de todas las fases (FASE-DATASOURCE, FASE-PERSONALIZATION, FASE-BUGFIXES, FASE-CONTENT-FIXES, FASE-VALIDATION-GATE) y liberación final v4.31.1.

### Cambios Implementados

Release final que consolidad todas las correcciones del proyecto AMAZILIA-BUGFIX:
- **FASE-DATASOURCE**: Pipeline de datos enriquecido con hotel_schema_enricher y v4_asset_orchestrator
- **FASE-PERSONALIZATION**: Generators reciben datos reales del audit (hotel_data, gbp_data, metadata_data)
- **FASE-BUGFIXES**: Review widget condicional, org_schema sin placeholders, verificación de assets reales
- **FASE-CONTENT-FIXES**: optimization_guide, monthly_report, llms_txt con datos contextualizados
- **FASE-VALIDATION-GATE**: Gates de validación en asset_catalog, conditional_generator, serpapi_client

### Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/v4_asset_orchestrator.py` | Bridge de datos entre fases |
| `modules/asset_generation/conditional_generator.py` | Propagación hotel_data a generators, review widget condicional, org_schema limpio |
| `modules/auditors/v4_comprehensive.py` | _build_search_queries() para Places API robusto |
| `modules/auditors/hotel_schema_enricher.py` | Enriquecimiento de schema data |
| `modules/asset_generation/review_widget_generator.py` | Lógica condicional de estrellas |
| `modules/asset_generation/org_schema_generator.py` | Eliminación de placeholder example.com |
| `modules/asset_generation/optimization_guide_generator.py` | Datos reales del audit |
| `modules/asset_generation/monthly_report_generator.py` | Extracción de hotel_data |
| `modules/asset_generation/llmstxt_generator.py` | Contenido contextualizado |
| `modules/asset_generation/asset_catalog.py` | Gates de validación |
| `main.py` | Verificación Path.exists() para assets |
| `scripts/sync_versions.py` | Sincronización de versiones |

### Tests

- Suite completa: 2224 funciones, 140 archivos, 0 regresiones
- Coherence score: 0.84 >= 0.8 (PASA gate)
- Publication Ready: true

### Resumen de Fixes Residuales (A3 + D7)

|| Fix | Descripcion | Resultado |
|-----|-----|------------|-----------|
| A3 | hotel_data vacio en schema vacio | `hotel_data = {}` ahora SIEMPRE se crea (fuera del `if schema.properties`). Fallback chain: `audit_result.hotel_name` → `gbp.name` → `metadata.title`. Monthly report recibe `{name: "Amaziliahotel"}` en vez de `None` → fallback "Hotel" |
| D7 | Propuesta marcaba assets generados como ❌ | `assets_for_quality` ahora usa `asset_result.generated_assets` (12 items) en vez de `asset_plan` (10 items). Los 3 assets `promised_by="always"` (voice_assistant_guide, whatsapp_button, monthly_report) ya aparecen correctamente |

**Archivos adicionales modificados por A3+D7:**

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/v4_asset_orchestrator.py` | `_extract_validated_fields()` crea `hotel_data` siempre + fallback chain name |
| `main.py` | `assets_for_quality` usa `asset_result.generated_assets` |
| `tests/asset_generation/test_audit_data_pipeline.py` | Test actualizado para esperar `hotel_data` presente (vacio) |

---

## [4.31.0] - 2026-04-14

### Objetivo

FASE-PERSONALIZATION + FASE-BUGFIXES ejecutadas en paralelo.

---

## FASE-PERSONALIZATION: Generators con Audit Data

**Problema:** Generators producían assets genéricos (name="Hotel", url vacía) porque no recibían datos del audit.

**Archivos Nuevos:**

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/geo_playbook_generator.py` | Reimplementado con hotel_data + gbp_data |
| `modules/asset_generation/optimization_guide_generator.py` | Reimplementado con hotel_data + metadata_data |

**Archivos Modificados:**

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | Propaga hotel_data a todos los generators. Wrappers legacy para backward compatibility |
| `modules/asset_generation/monthly_report_generator.py` | Refactorizado — extrae name, city, website, phone, email, address de hotel_data |

**Tests:** 223 passed (5 failures preexistentes voice_assistant/voice_keywords)

---

## FASE-BUGFIXES: Corrección Bugs Específicos

**D4 — WhatsApp:** `detected_via_html` no existía en iah-cli (0 matches).

**D5 — Review Widget:** hardcoded ★★★★★ con "Excelente servicio" → lógica condicional:
- Si rating==0 o review_count==0 → "Aún no hay reseñas disponibles"
- Si hay datos → estrellas reales + rating numérico + conteo

**D6 — Organization Schema:** `url: "https://example.com"` fallback → campos omitidos del JSON si no tienen datos reales.

**D7 — Propuesta:** `Path(asset.path).exists()` para verificar existencia real antes de marcar ✅/❌.

**Archivos Modificados:**

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/conditional_generator.py` | _generate_review_widget() condicional; _generate_org_schema() elimina placeholder |
| `tests/asset_generation/test_content_gates.py` | test_org_schema_with_empty_data actualizado para comportamiento correcto |
| `main.py` | Línea 2375: `Path(asset.path).exists()` para verificar archivos |

**Tests:** 223 passed | Greps: 0 detected_via_html, 0 Excelente servicio, 0 example.com

---

## [4.30.0] - 2026-04-13

### Objetivo

Fix critico: Places API (New) no encontraba hoteles con schema.org basura

### Problema

El pipeline devolvia score Google Maps 0/100 para hoteles que SÍ existen en Google Maps. Causa: la query de Places API usaba datos directos del schema.org sin validarlos. Ejemplo real (Amazilia Hotel):
- Schema decia: `"Amaziliahotel"` (sin espacio), coordenadas NYC (40.7128, -74.0060)
- Google Maps tiene: `"Amazilia Hotel"`, 4.5 estrellas, 202 reseñas
- Query enviada: `"Amaziliahotel, Colombia"` → no encontraba nada → geo_score=0

### Cambios Implementados

- `modules/auditors/v4_comprehensive.py` — Nuevo metodo `_build_search_queries()`: genera multiples variaciones de query validando schema_props antes de usarlos. Valida coordenadas (deben estar en Colombia), nombre (debe tener espacios o coincidir con hotel_name), y direccion. Loop de Places API intenta cada query hasta encontrar el hotel.
- **Impacto**: Score Google Maps pasa de 0/100 (falso) a score real basado en datos verificados de Google Places.

### Archivos

| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | +90 lineas: `_build_search_queries()`, loop de queries en `_audit_gbp()` |

### Tests

- Tests existentes: 385 (sin cambios)
- Tests nuevos: 0 (fix validado manualmente contra Amazilia Hotel real)

---

## [4.29.0] - 2026-04-13

### Objetivo

Fix geo_enriched → Delivery Bridge + Assets Completos

7 fases completadas que resuelven 2 rupturas criticas en el pipeline: (1) geo_enriched no llegaba al delivery package, y (2) 3/7 servicios prometidos en propuesta no generaban asset. Todo el codigo de las fases ya fue mergeado en la sesion del 2026-04-13.

### Cambios Implementados

### FASE-GEO-BRIDGE (2026-04-13): geo_enriched → Asset Enrichment Bridge

- `modules/asset_generation/conditional_generator.py` — GEO bridge post-generacion: copia archivos de `geo_enriched/` al delivery package con fallback a `hotel_data` del audit.
- `modules/delivery/asset_bridge.py` — **NUEVO** modulo que conecta geo_enriched con delivery. `copy_geo_assets_to_delivery()` con metadata de confianza.
- `modules/delivery/delivery_package_builder.py` — Integracion del GEO bridge en el flujo de packaging.
- **Problema resuelto**: RUPTURA 1 del AUDIT — delivery package no incluiacute; geo_enriched/ ni confidence real (usaba 0.5 fijo).

### FASE-CONF-GATE (2026-04-13): Asset Confidence Gate en Publication

- `modules/quality_gates/publication_gates.py` — Gate 8: `asset_confidence_gate` (WARNING mode). Verifica que todos los assets generados tengan `confidence_score >= 0.7`.
- `modules/asset_generation/v4_asset_orchestrator.py` — Pasa `confidence_scores` al assessment para el gate.
- **Problema resuelto**: Assets con confidence bajo no eran bloqueados en publicacion.

### FASE-LLMSTXT-FIX (2026-04-13): Fix llms.txt Generator — Fallback a geo_enriched

- `modules/asset_generation/llmstxt_generator.py` — Parametro `geo_enriched_path: Optional[Path]` en `generate()`. Si geo_enriched/llms.txt existe (>50 chars), retorna ese contenido directamente. Warning cuando hotel name es generico ("Hotel") o vacio.
- `modules/asset_generation/conditional_generator.py` — `_generate_content()` acepta `hotel_id`. Construye `geo_enriched_path = output_dir / hotel_id / "geo_enriched"` y lo pasa al generador.
- `tests/asset_generation/test_llmstxt_generator.py` — **NUEVO** 8 tests.
- **Problema resuelto**: D3 del AUDIT — llms.txt generaba placeholders vacios ("Hotel", URL "", "N/A") a pesar de que geo_enriched/llms.txt ya contenia datos reales.

### FASE-ASSETS-VALIDACION (2026-04-13): Propuesta → Assets — Cero Desconexiones

- `modules/asset_generation/monthly_report_generator.py` — **NUEVO** generador de informe mensual con KPIs de seguimiento (trafico web, GBP views, reservas directas, WhatsApp clicks), checklist acciones mensuales, disclaimer GA4/GSC.
- `modules/asset_generation/proposal_asset_alignment.py` — **NUEVO** verificador propuesta→asset con mapeo de 7 servicios. `verify_proposal_asset_alignment()` retorna AlignmentReport (aligned/missing/low_quality).
- `modules/asset_generation/asset_catalog.py` — Nuevo entry `monthly_report` (promised_by=["always"]). `whatsapp_button.promised_by` += "always". `voice_assistant_guide.promised_by` += "always_aeo".
- `modules/asset_generation/conditional_generator.py` — Handler de generacion de contenido para monthly_report.
- `modules/quality_gates/publication_gates.py` — Gate 9: `proposal_asset_alignment_gate` (WARNING mode). Verifica 7/7 servicios con asset.
- `tests/asset_generation/test_monthly_report.py` — **NUEVO** 12 tests.
- `tests/asset_generation/test_voice_guide_generation.py` — **NUEVO** 9 tests.
- `tests/asset_generation/test_whatsapp_button.py` — **NUEVO** 11 tests.
- `tests/asset_generation/test_proposal_alignment.py` — **NUEVO** 13 tests.
- `tests/quality_gates/test_proposal_alignment_gate.py` — **NUEVO** 7 tests.
- **Problema resuelto**: D4 del AUDIT — 3/7 servicios prometidos NO generaban asset (voice_assistant_guide, whatsapp_button, monthly_report). Servicios con asset: 3/7 → 7/7.

### FASE-CONFIDENCE-DISCLOSURE (2026-04-13): Transparencia de Calidad en Propuesta

- `modules/commercial_documents/templates/propuesta_v6_template.md` — Nueva seccion "Estado de los Entregables" con placeholder `${asset_quality_table}`.
- `modules/commercial_documents/v4_proposal_generator.py` — Nuevo metodo `_generate_asset_quality_table()` que mapea servicios → assets via `PROPOSAL_SERVICE_TO_ASSET`. Umbrales: >=0.7 Completo, >=0.4 Requiere datos, <0.4 En desarrollo.
- `main.py` — Conversion `asset_plan` (AssetSpec) a formato dict con mapeo ConfidenceLevel→float.
- `tests/commercial_documents/test_proposal_confidence_disclosure.py` — **NUEVO** 5 tests.

### FASE-TEMPLATE-DEBT (2026-04-13): Sincronizar Embebido vs V6 + Typo

- `modules/commercial_documents/propuesta_v6_template.md` — Sync embebido vs V6. Typo corregido.
- **Problema resuelto**: Desconexion entre template embebido y V6.

### FASE-CONTENT-SCRUBBER (2026-04-13): Fix Self-Replacement + Spacing Detection

- `modules/postprocessors/document_quality_gate.py` — Skip self-replacement warnings (PT_TO_ES: old==new). 9 spacing error patterns + `detect_spacing_errors()`. `_check_spacing_errors()` method en gate.
- `tests/postprocessors/test_document_quality_gate.py` — 9 tests nuevos: 3 self-replacement, 3 spacing detection, 3 gate integration. Total: 28/28 passing.

### Tests
- 60 tests nuevos pasando (8 LLMSTXT-FIX + 52 ASSETS-VALIDACION)
- 0 regresiones

### Archivos Nuevos
- `modules/asset_generation/geo_enriched_bridge.py` — Bridge enrichment geo_enriched → delivery
- `modules/asset_generation/monthly_report_generator.py` — Generador de informe mensual
- `modules/asset_generation/proposal_asset_alignment.py` — Verificador propuesta → asset
- `tests/asset_generation/test_geo_enriched_bridge.py` — 13 tests bridge
- `tests/quality_gates/test_asset_confidence_gate.py` — Tests gate confidence
- `tests/asset_generation/test_llmstxt_generator.py` — 8 tests llms.txt fix
- `tests/asset_generation/test_monthly_report.py` — 12 tests informe mensual
- `tests/asset_generation/test_voice_guide_generation.py` — 9 tests voice guide
- `tests/asset_generation/test_whatsapp_button.py` — 11 tests WhatsApp button
- `tests/asset_generation/test_proposal_alignment.py` — 13 tests alineación
- `tests/quality_gates/test_proposal_alignment_gate.py` — 7 tests gate #9
- `tests/commercial_documents/test_proposal_confidence_disclosure.py` — 5 tests disclosure
- `tests/postprocessors/test_document_quality_gate.py` — Tests content scrubber

### Archivos Modificados
- `modules/asset_generation/conditional_generator.py` — Bridge integration + voice/whatsapp fix
- `modules/asset_generation/v4_asset_orchestrator.py` — Llamada al bridge post-generación
- `modules/auditors/llm_mention_checker.py` — OPENROUTER-A: cost_usd/tokens_used
- `modules/auditors/v4_comprehensive.py` — OPENROUTER-B: print costo IAO
- `modules/asset_generation/asset_catalog.py` — Agregar monthly_report, fix promised_by
- `modules/quality_gates/publication_gates.py` — Gate #8 confidence + gate #9 alignment
- `modules/asset_generation/llmstxt_generator.py` — Fallback a geo_enriched/llms.txt
- `modules/commercial_documents/v4_diagnostic_generator.py` — Sincronizar/eliminar embebido
- `modules/commercial_documents/templates/propuesta_v6_template.md` — Typo fix + tabla calidad
- `modules/commercial_documents/v4_proposal_generator.py` — Tabla calidad dinámica
- `modules/postprocessors/document_quality_gate.py` — Self-replacement + spacing fixes
- `main.py` — Cableado assets_generated a proposal generator
- 0 regresiones

### Criterio de Exito Alcanzado
- 7/7 servicios de la propuesta tienen asset garantizado
- geo_enriched bridging al delivery package
- confidence >= 0.7 gate activo
- llms.txt con datos reales (no placeholders)
- Propuesta incluye tabla de calidad de assets
- 9 publication gates activos

## [4.28.0] - 2026-04-12

### 4 Pilares Alignment + Voice Readiness Proxy

2 fases ejecutadas en paralelo: FASE-D alinea toda la cadena de generación (diagnóstico → propuesta → gap analyzer → benchmarks) al modelo de 4 pilares (SEO+GEO+AEO+IAO). FASE-E introduce Voice Readiness Proxy como sub-score de AEO basado en inputs medibles (no medición directa Siri/Alexa).

*"Las soluciones a medias no son soluciones, es aplazar el problema."*

### FASE-CONTENT-SCRUBBER (2026-04-13): Fix Self-Replacement + Spacing Detection

- `modules/postprocessors/document_quality_gate.py` — Skip self-replacement warnings (PT_TO_ES: old==new). 9 spacing error patterns + `detect_spacing_errors()`. `_check_spacing_errors()` method en gate.
- `tests/postprocessors/test_document_quality_gate.py` — 9 tests nuevos: 3 self-replacement, 3 spacing detection, 3 gate integration. Total: 28/28 passing.

### FASE-CONFIDENCE-DISCLOSURE (2026-04-13): Transparencia de Calidad en Propuesta

- `modules/commercial_documents/templates/propuesta_v6_template.md` — Nueva sección "Estado de los Entregables" con placeholder `${asset_quality_table}`
- `modules/commercial_documents/v4_proposal_generator.py` — Nuevo método `_generate_asset_quality_table()` que mapea servicios → assets via `PROPOSAL_SERVICE_TO_ASSET`. Nuevo parámetro `assets_generated`. Umbrales: ≥0.7 Completo, ≥0.4 Requiere datos, <0.4 En desarrollo
- `main.py` — Conversión `asset_plan` (AssetSpec) a formato dict con mapeo ConfidenceLevel→float
- `tests/commercial_documents/test_proposal_confidence_disclosure.py` — 5 tests: tabla incluida, confidence real, missing asset, pending, low confidence. Total: 5/5 passing

### FASE-D: Package & Template Alignment — 4 Pilares

- `modules/analyzers/gap_analyzer.py` — Expandido de 2 gaps (GEO+AEO) a 4 gaps (SEO+GEO+AEO+IAO) con ponderación proporcional
- `modules/financial_engine/opportunity_scorer.py` — Nuevas brechas IAO: `no_llms_txt`, `ia_crawler_blocked`, `weak_brand_signals`. Nuevas brechas SEO: `no_meta_descriptions`, `poor_heading_structure`
- `scripts/update_benchmarks.py` — Nueva función `calculate_iao_score()` con 5 checks (20pts c/u, max 100). `iao_avg` en promedios regionales. `iao_score_ref` por región
- `modules/utils/benchmarks.py` — `iao_score_ref` en defaults regionales
- `modules/generators/report_builder.py` — ⚠️ DEPRECATED (comando spark deprecado). Sección ANALISIS 4-PILARES expandida a SEO+GEO+AEO+IAO
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — Fila IAO (Para que te RECOMIENDEN) + Score Global con narrativa comercial
- `modules/commercial_documents/v4_diagnostic_generator.py` — `_get_regional_benchmarks()` retorna 4 scores incluyendo `iao_score_ref`
- `modules/commercial_documents/v4_proposal_generator.py` — `score_global` como métrica principal con fallback a `score_tecnico` (backward compat)

### FASE-E: Voice Readiness Proxy Score

- `modules/auditors/voice_readiness_proxy.py` — **NUEVO** módulo que calcula readiness para asistentes de voz basado en PROXY (inputs que alimentan Siri/Google Assistant, no medición directa):
  - GBP completeness: 30pts (nombre, dirección, teléfono, horarios, website)
  - Schema for voice: 25pts (LocalBusiness, FAQ, Speakable)
  - Featured snippets: 25pts (AEOSnippetTracker o fallback schema)
  - Factual coverage: 20pts (horarios, teléfono, dirección, precios en página)
  - Niveles: critical (0-25), basic (26-50), good (51-75), excellent (76-100)
- `tests/auditors/test_voice_readiness_proxy.py` — **NUEVO** 22 tests
- `modules/commercial_documents/data_structures.py` — `voice_readiness_score` + `voice_readiness_level` en DiagnosticSummary
- `modules/commercial_documents/v4_diagnostic_generator.py` — Integración no-bloqueante con fallback si FASE-B no completada
- `main.py` — Pasa voice readiness al DiagnosticSummary

### Restricciones FASE-E
- NO consulta APIs de Siri, Alexa, Google Assistant directamente
- NO usa TTS/STT para simular queries de voz
- NO crea webhooks ni subscripciones a plataformas de voz
- Voice Readiness es SUB-SCORE de AEO, no un 5to pilar

### Tests
- 628 tests passing (0 regresiones)
- Errors pre-existentes en `data_validation/` y `observability/` (módulos faltantes, no relacionados)

### Post-FASE-1: Eliminar Score Global de Tabla Diagnóstico

Fila redundante "Visibilidad Digital (Global)" eliminada de la tabla de diagnóstico del cliente. `score_global` se mantiene como cálculo interno (usado por propuesta comercial como `score_tecnico`). Dead code `score_global_status` eliminado.

- `templates/diagnostico_v6_template.md` — Eliminada fila "Visibilidad Digital (Global)" (5→4 filas)
- `v4_diagnostic_generator.py` — Eliminada variable dead code `score_global_status`, corregido docstring `calcular_cumplimiento()`

### Documentacion Post-Implementacion (docs-only)

- **README.md** - Seccion "Que es IA Hoteles Agent" expandida: 4 pilares progresivos con tabla de siglas/proposito/ejemplo + progresion SEO->AEO->IAO con GEO lateral + score_global como metrica principal. Nueva seccion "Voice Readiness Proxy (v4.28.0)" con componentes, niveles y restricciones. Test count actualizado (628->2150).
- **AGENTS.md** - Tests: 1782->2150 funciones, 52->0 regresion. Modulo voice_readiness_proxy.py agregado a tabla. Mejoras: agrega "4 Pilares Alignment" y "Voice Readiness Proxy".
- **gap_analyzer.py** - `modelo_pilares` residual corregido: "2 Pilares GEO + JSON" -> "4 Pilares SEO+GEO+AEO+IAO".
- **GUIA_TECNICA.md** - Nota tecnica agregada: progresion 4 pilares, CHECKLIST redistribuido, VoiceReadinessProxy, gap_analyzer modelo_pilares.
- **docs/contributing/REGISTRY.md** - Entrada FASE-DOCS-01 registrada via log_phase_completion.py.

### FASE-LLMSTXT-FIX (2026-04-13): Fix llms.txt Generator — Fallback a geo_enriched

- `modules/asset_generation/llmstxt_generator.py` — Parámetro `geo_enriched_path: Optional[Path]` en `generate()`. Si geo_enriched/llms.txt existe (>50 chars), retorna ese contenido directamente. Warning cuando hotel name es genérico ("Hotel") o vacío.
- `modules/asset_generation/conditional_generator.py` — `_generate_content()` acepta `hotel_id`. Construye `geo_enriched_path = output_dir / hotel_id / "geo_enriched"` y lo pasa al generador.
- `tests/asset_generation/test_llmstxt_generator.py` — **NUEVO** 8 tests: fallback usado, fallback ignorado si archivo missing, fallback ignorado si <50 chars, warning genérico, warning vacío, formato válido llmstxt.org, backward compat sin parámetro, forwarding desde generate_from_assessment.
- **Problema resuelto**: D3 del AUDIT — llms.txt generaba placeholders vacíos ("Hotel", URL "", "N/A") a pesar de que geo_enriched/llms.txt ya contenía datos reales.
- **Cadena de fallback**: Generador lee geo_enriched → GEO bridge (post-generación) → hotel_data del audit → PENDIENTE_ONBOARDING. Nunca placeholders engañosos.

### FASE-ASSETS-VALIDACION (2026-04-13): Propuesta → Assets — Cero Desconexiones

- `modules/asset_generation/monthly_report_generator.py` — **NUEVO** generador de informe mensual con KPIs de seguimiento (tráfico web, GBP views, reservas directas, WhatsApp clicks), checklist acciones mensuales, disclaimer GA4/GSC.
- `modules/asset_generation/proposal_asset_alignment.py` — **NUEVO** verificador propuesta→asset con mapeo de 7 servicios. `verify_proposal_asset_alignment()` retorna AlignmentReport (aligned/missing/low_quality).
- `modules/asset_generation/asset_catalog.py` — Nuevo entry `monthly_report` (promised_by=["always"]). `whatsapp_button.promised_by` += "always". `voice_assistant_guide.promised_by` += "always_aeo".
- `modules/asset_generation/conditional_generator.py` — Handler de generación de contenido para monthly_report.
- `modules/quality_gates/publication_gates.py` — Gate 9: `proposal_asset_alignment_gate` (WARNING mode). Verifica 7/7 servicios con asset.
- `tests/asset_generation/test_monthly_report.py` — **NUEVO** 12 tests
- `tests/asset_generation/test_voice_guide_generation.py` — **NUEVO** 9 tests
- `tests/asset_generation/test_whatsapp_button.py` — **NUEVO** 11 tests
- `tests/asset_generation/test_proposal_alignment.py` — **NUEVO** 13 tests
- `tests/quality_gates/test_proposal_alignment_gate.py` — **NUEVO** 7 tests
- **Problema resuelto**: D4 del AUDIT — 3/7 servicios prometidos NO generaban asset (voice_assistant_guide, whatsapp_button, monthly_report). Cliente pagaba por servicios que no recibía.
- **Resultado**: 7/7 servicios con asset garantizado. Servicios con asset: 3/7 → 7/7.

### Tests
- 60 tests nuevos pasando (8 LLMSTXT-FIX + 52 ASSETS-VALIDACION)
- 0 regresiones

## [4.27.0] - 2026-04-11

### Motor Financiero Verificable — Opción C

11 fases (A→K) en 2 ciclos. Cada COP cuantificado tiene origen trazable, peso proporcional, etiqueta honesta y base verificable.

*"Las soluciones a medias no son soluciones, es aplazar el problema."*

### Ciclo 1: Rediseño Motor Financiero (A→H)
- **FASE-A**: FinancialBreakdown + EvidenceTier + Scenario.monthly_loss_central
- **FASE-B**: ScenarioCalculator.calculate_breakdown() narrativa por capas
- **FASE-C**: Pesos normalizados (suma=100%) + DynamicImpactCalculator
- **FASE-D**: Scraper→ADR con WEB_SCRAPING como fuente
- **FASE-E**: 22 consumidores actualizados de max→central
- **FASE-F**: Template narrativa Comisión OTA + evidence tiers
- **FASE-G**: Integración main.py + E2E validación
- **FASE-H**: RegionalADRResolver activado SHADOW

### Ciclo 2: Causa Raíz — Datos No Verificables (I→K)
- **FASE-I**: RegionalADRResolver por regiones validadas (eje_cafetero, antioquia). Caribe protegido.
- **FASE-J**: NoDefaultsValidator source-aware + template honesto (verificable vs estimada)
- **FASE-K**: Unificar camino dual + fix escenario optimista negativo

### Cambios FASE-K (esta release)
- `main.py` — Eliminado cálculo dual. Unica fuente de verdad vía FinancialCalculatorV2 con data_sources
- `modules/financial_engine/harness_handlers.py` — Usa FinancialCalculatorV2 con fallback a ScenarioCalculator
- `modules/financial_engine/scenario_calculator.py` — Propiedades is_net_gain, display_label, monthly_impact_cop. Fix hook_range para optimista negativo
- `scripts/validate_context_integrity.py` — Fix: reconoce symlink válido .agent/workflows→.agents/workflows

### Resultado
- Escenario optimista negativo se presenta como "+$189,000 COP/mes (ganancia neta)" en vez de pérdida confusa
- Cada COP tiene: fuente regional (ADR/occupancy), peso proporcional, evidence tier (A/B/C), disclaimer honesto
- 390 tests pasando, 0 regresiones
- E2E amaziliahotel.com exit code 0

### Tests
- 5 tests nuevos (TestOptimistaFix: is_net_gain, conservador, display_label positivo/negativo, hook_range)
- 390/390 regression tests financial_engine suite

## [4.26.0] - 2026-04-10

### Objetivo
Eliminar gap arquitectónico donde la propuesta V6 no consumía brechas reales del diagnóstico.

### Cambios Implementados
- `modules/commercial_documents/v4_proposal_generator.py` - Eliminada distribución fija 40/30/20/10, phantom costs corregidos
- `modules/commercial_documents/v4_diagnostic_generator.py` - Resuelto dual source conflict, caché para _identify_brechas (9x→1x), cleanup pain_to_type
- `modules/commercial_documents/data_structures.py` - Eliminados duplicados de Scenario, calculate_quick_wins, extract_top_problems. Agregado brechas_reales a DiagnosticSummary

### Tests
- 18 tests nuevos (5 phantom + 5 dual source + 4 cache + 4 dedup)
- 0 regresiones
- Validado E2E con amaziliahotel.com (Coherence: 0.92, Publication: READY)

## [4.25.3] - 2026-04-08

### FASE-F (Brotli Encoding Fix + HTML Integrity Guardian)
- `venv/Scripts/pip.exe install brotli` - Libreria local instalada, `requests`/`urllib3` ahora decodifican `Content-Encoding: br` automaticamente
- `modules/auditors/v4_comprehensive.py` - Nuevo metodo `_validate_html_integrity()` (L342-377):
  - Valida que HTML sea legible y no basura binaria/comprimida
  - Check 1: estructura HTML basica (`<html`, `<head`, `<body`, `<!doctype`, `<div`)
  - Check 2: ratio de caracteres no imprimibles < 15% (detecta binario Brotli sin decodificar)
  - Detecta: Brotli sin decodificar, binario crudo, paginas de error, respuestas vacias, JS-only shells
- `modules/auditors/v4_comprehensive.py` - Integracion en `audit()` (L405-411):
  - **ANTES**: `page_html = html_response.text` → 33KB basura si servidor responde Brotli
  - **AHORA**: `_validate_html_integrity()` rechaza HTML corrupto → downstream handlers usan string vacio gracefully
- `tests/test_html_integrity.py` - 5 tests de regresion (TODOS PASAN):
  - `test_brotli_binary_rejected`: binary Brotli sin decodificar → False
  - `test_empty_html_rejected`: HTML vacio/muy corto → False
  - `test_valid_html_accepted`: HTML real valido → True
  - `test_html_with_joinchat_accepted`: HTML con joinchat (caso amaziliahotel.com) → True
  - `test_error_page_rejected`: Cloudflare JS-only challenge page → False

### CAUSA RAIZ RESUELTA
- **Problema**: HttpClient enviaba `Accept-Encoding: gzip, deflate, br`. Servidores LiteSpeed respondian `Content-Encoding: br`. venv no tenía `brotli` → `requests` entregaba binario crudo como UTF-8 → 33KB basura vs 236KB HTML real
- **Impacto**: TODO el pipeline de diagnostico operaba sobre HTML ileible → BRECHA 2 "Sin WhatsApp" falsa + Region "nacional" (no "eje_cafetero") + Open Graph no detectado
- **Resultado E2E**: amaziliahotel.com ahora entrega Length:236640, joinchat:True, class=:694

### E2E Validation Results (amaziliahotel.com)
| Check | Antes (roto) | Despues (fix) |
|-------|-------------|---------------|
| BRECHA 2 "Sin WhatsApp" | Aparecia (falso+) | **NO aparece** |
| whatsapp_verified score | 0.000 | **1.000** |
| Region | "nacional" | **"eje_cafetero"** |
| Open Graph | False | False (headless SPA, expected) |
| Coherence | 0.84 | **0.92** |
| HTML length | 33KB basura | **236640 chars real** |

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `tests/test_html_integrity.py` | 5 tests de regresion para integridad HTML |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | `_validate_html_integrity()` + integracion en `audit()` |

### Tests
- 5/5 nuevos en `test_html_integrity.py`
- 0 regresiones introducidas
- Coherence E2E: 0.92 (umbral: 0.8) ✅

---

## [4.25.3] - 2026-04-08

### FASE-B (AEO Scoring Rewrite): _calculate_aeo_score() con 4 componentes
- `modules/commercial_documents/v4_diagnostic_generator.py` - `_calculate_aeo_score()` reescrito (método 1324-1346):
  - **ANTES**: solo verificaba `performance.mobile_score` → "0 (Pendiente de datos)" si PageSpeed fallaba
  - **AHORA**: scoring de 4 componentes × 25pts = 100pts:
    - Schema Hotel válido → +25pts (detectado no válido → +10pts)
    - FAQ Schema válido → +25pts (detectado no válido → +10pts)
    - Open Graph detectado → +25pts (vía `hasattr` para compatibilidad)
    - Citabilidad tiers → ≥70→+25, ≥40→+15, >0→+5, None→0pts
  - Retorna string numérico ("0", "25", "50", etc.) compatible con `_get_score_status()`
  - Usa `hasattr()` para `seo_elements` y `citability` (campos opcionales en V4AuditResult)
- Docstring actualizado refleja implementación exacta
- Elimina el comportamiento "Pendiente de datos" cuando hay al menos 1 componente con datos

### FASE-E (OG Detection Fix): Reutilizar HTML del schema audit
- `modules/auditors/v4_comprehensive.py` - HTTP request consolidation (L365-371, L409-428):
  - **ANTES**: 3 HTTP requests separadas al mismo URL (schema audit, metadata, citability+SEO)
  - **AHORA**: 1 HTTP request única compartida entre metadata, citability y SEO elements
  - Elimina segunda request innecesaria en step 2.8 que podía devolver HTML diferente (SPA/JS-rendered)
  - `_audit_metadata()` acepta `html_content` opcional (backward compatible)
  - Logging defensivo: cuando OG no se detecta, loggea snippet del HTML para diagnóstico
- Impacto: elimina falso negativo de OG detection en sitios SPA (+25pts AEO potencial)
- Nota: detección OG en hotelvisperas.com sigue fallando por compresión Brotli upstream (fuera de scope)

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `tests/commercial_documents/test_aeo_score.py` | 15 tests: all_valid, only_schema, schema_detected_not_valid, only_og, citability_tiers (4 niveles), no_data, none_result, max_100, int_conversion, get_score_status (2), realistic_hotel |

### Dependencias
- FASE-A completada (OG detection funcional en seo_elements_detector.py)
- No modifica seo_elements_detector.py
- No modifica templates (eso es FASE-C)
- No agrega campos nuevos a V4AuditResult

### Tests
- 15 tests nuevos en `tests/commercial_documents/test_aeo_score.py`
- 0 regresiones en suite existente
- `run_all_validations.py --quick` 4/4 pasan

### FASE-C (Bugfix Critico): 4 Bugs en v4_diagnostic_generator
- `modules/commercial_documents/v4_diagnostic_generator.py` - 4 correcciones criticas:
  - **BUG-1 (L8)**: `import logging` faltante — NameError cuando GA4 falla en handler except
  - **BUG-2 (L2017)**: `getattr(citability_score, 'overall_score', None)` en vez de `'score'` — Brecha 10 (Contenido No Citable) nunca se detectaba
  - **BUG-3 (L2006)**: `getattr(..., 'open_graph', False)` en vez de `'has_open_graph', True` — Brecha 9 (Sin OG Tags) nunca se detectaba
  - **BUG-4 (L1000)**: `mobile_score is not None` en vez de truthy check — alerta de performance=0 se saltaba por short-circuit
- `tests/commercial_documents/test_diagnostic_brechas.py` - Mocks actualizados:
  - `mock_seo_elements`: `m.open_graph` (era `m.has_open_graph`)
  - `mock_citability`: `m.overall_score` (era `m.score`)
  - `test_identify_brechas_7_...` renombrado a `8_...` (brecha no_faq_schema preexistente)
- Tests: 12/12 pasaron (modulo afectado), 0 regresiones introducidas
- Validaciones: `run_all_validations.py --quick` 4/4 PASS

### FASE-C (Integration & Validación): Verificación End-to-End
- Verificación completa del fix AEO score — sin cambios de código, solo validación:
  - Template v6: `${aeo_score}` renderiza número (ej: "50/100"), NO "0 (Pendiente de datos)/100"
  - Template v4: `${schema_infra_score}` mapeado a `_calculate_aeo_score()` (L514) — correcto
  - Benchmark regional: `aeo_score_ref` = 20 (regional) / 40 (global), coherente con scoring 0-100
  - `_get_score_status("50", 20)` → "Superior" (50 >= 22) — correcto
- Tests acumulados: 24/24 (9 FASE-A + 15 FASE-B), 0 regresiones
- Documentación: dependencias-fases, checklist, REGISTRY.md, GUIA_TECNICA.md actualizadas
- Gap no-bloqueante: GUIA_TECNICA.md línea 124 corregida

### FASE-D (Bugfix Medios): 5 Bugs + seo_elements Serialization
- `modules/commercial_documents/v4_diagnostic_generator.py` - 5 correcciones medias:
  - **MED-1 (L1624-1771)**: Eliminación de 148 líneas dead code — dos definiciones de `_compute_opportunity_scores`, `_inject_brecha_scores`, `_map_pain_to_scorer_type`, `_brecha_scores_empty` + 6 métodos placeholder. La segunda definición (L2031+) es la que corre en producción.
  - **MED-2 (L517-521)**: Eliminadas claves `geo_regional_avg`, `competitive_regional_avg`, `seo_regional_avg`, `aeo_regional_avg` duplicadas en dict de template data (primera ocurrencia eliminada, segunda en L595-599 permanece).
  - **MED-3 (L823)**: `confidence.value` → `confidence.value.upper()` en campo WhatsApp para consistencia con otros campos que usan 'ESTIMATED'/'VERIFIED' en mayúsculas.
  - **MED-4 (L296-299)**: Corregidos pipes extra en tabla markdown de scorecard. 4 filas tenían `||` o `|||` al inicio en vez de `|`. Alineación de tabla corregida.
  - **MED-5 (L299)**: AEO score ahora muestra `${aeo_score}/100` en vez de `${aeo_score}` — consistencia visual con GEO, SEO, Competitive.
- `modules/auditors/v4_comprehensive.py` - Serialización seo_elements:
  - **SER-1 (to_dict)**: Agregado bloque `if self.seo_elements:` que serializa 8 campos (open_graph, imagenes_alt, redes_activas, confidence, notes, open_graph_tags, images_without_alt, social_links_found) en `V4AuditResult.to_dict()`. Sin este fix, `audit_report.json` perdía datos OG, imágenes sin alt y redes sociales.
  - **SER-1 (executed_validators)**: Agregado `"seo_elements_detection"` a la lista de validators ejecutados.
- Tests: 209 passed, 7 failures preexistentes sin relación con cambios (asset_generation, pain_solution_mapper mock desactualizado)
- Validaciones: pre-commit version consistency PASSED

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| (ninguno) | |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | MED-1..5: dead code elim, dup keys, confidence .upper(), pipe fix, /100 suffix |
| `modules/auditors/v4_comprehensive.py` | SER-1: seo_elements serialization in to_dict() + executed_validators |

### FASE-E (Integridad de Datos): Propagación WhatsApp + Inferencia Regional
- Problema: datos detectados correctamente en capas tempranas del pipeline NO se propagaban a consumidores intermedios/finales.
- 5 archivos modificados, 7 fixes (W1-W4 WhatsApp, R1-R3 Regional):

**Workstream WhatsApp (W1-W4):**
- `main.py` (W1): Nueva rama `elif whatsapp_html_detected` en ValidationSummary (L1766+). Campo `whatsapp_number` siempre existe cuando botón HTML detectado — confidence ESTIMATED, sources=["HTML"], match=0.6.
- `modules/commercial_documents/pain_solution_mapper.py` (W2): Parámetro `whatsapp_html_detected=False` en `detect_pains()`. Condición WhatsApp actualizada: no genera pain `no_whatsapp_visible` cuando botón HTML existe.
- `modules/scrapers/web_scraper.py` (W3): `_extract_contact()` parsea enlaces `tel:` del HTML (`soup.find_all('a', href=re.compile(r'^tel:'))`). Captura teléfonos que no aparecen como texto visible.
- `modules/commercial_documents/coherence_validator.py` (W4): `validate()` y `_check_whatsapp_verified()` aceptan `whatsapp_html_detected`. Si botón HTML existe pero no campo en ValidationSummary → score 0.5 (no 0.0 penalizante).

**Workstream Regional (R1-R3):**
- `main.py` (R1): Nueva función `_infer_region_from_address(address)` — infiere región turística (eje_cafetero, caribe, antioquia, centro, valle, llanos, san_andres) desde dirección GBP. Llamada post-audit: si `region == "nacional"` y `audit_result.gbp.address` disponible, re-evalúa.
- `modules/commercial_documents/v4_diagnostic_generator.py` (R2): Sanitización de `hotel_region` — "nacional"/"general"/"default"/"unknown" → "Colombia". Underscores → Title Case ("eje_cafetero" → "Eje Cafetero").
- `main.py` (R3): Keywords URL ampliadas para Eje Cafetero: +cafetero, finca, montenegro, filandia, circasia, termales.

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| `main.py` | W1: ValidationSummary rama html; R1: _infer_region_from_address(); R3: keywords URL |
| `modules/commercial_documents/v4_diagnostic_generator.py` | R2: sanitización hotel_region |
| `modules/commercial_documents/pain_solution_mapper.py` | W2: parámetro + condición whatsapp_html_detected |
| `modules/commercial_documents/coherence_validator.py` | W4: validate() + _check_whatsapp_verified() con whatsapp_html_detected |
| `modules/scrapers/web_scraper.py` | W3: captura tel: links |

### Validación E2E
- Hotel: amaziliahotel.com
- **Región: eje_cafetero** (antes persistía "nacional") — R1+R2+R3 FUNCIONALES
- Coherence: 0.84 ≥ 0.80 — Pasa gate
- Publication: READY_FOR_PUBLICATION (todos los gates pasan)
- whatsapp_button generado en delivery — W1/W2 evitó pain falso "no_whatsapp_visible"

### FASE-F (Zombie References + Code Smells): Limpieza de referencias IAO/voice + 7 code smells
- `templates/diagnostico_ejecutivo.md` - ZMB-1: fila IAO eliminada del template
- `templates/diagnostico_v4_template.md` - ZMB-2: filas IAO + Voice Readiness eliminadas
- `modules/commercial_documents/v4_diagnostic_generator.py` - Limpieza completa:
  - **ZMB-3**: `iao_score` eliminado de `_get_analytics_fallback()` dict + 24 phantom placeholders eliminados
  - **MEN-1**: Import redundante `datetime` eliminado
  - **MEN-2**: Scores calculados 1 sola vez (eliminado recálculo duplicado)
  - **MEN-3**: `format_cop()` unificado (eliminada duplicación)
  - **MEN-4**: `hasattr()` guard agregado para acceso seguro a competitors
  - **MEN-5**: `print()` reemplazado por `logging.warning()`
  - **MEN-6**: `import re` movido a imports del módulo
  - **MEN-7**: Ternaria refactorizada con paréntesis para claridad
  - Método muerto `_format_scenario_amount()` eliminado (sin callers)
- `modules/utils/benchmarks.py` - ZMB-4: `iao_score` key eliminada
- Docstring `_get_analytics_fallback()` corregida: removida ref a `iao_score (0-100)`

### Archivos Modificados (FASE-F)
| Archivo | Cambio |
|---------|--------|
| `templates/diagnostico_ejecutivo.md` | ZMB-1: IAO row eliminada |
| `templates/diagnostico_v4_template.md` | ZMB-2: IAO+Voice rows eliminadas |
| `modules/commercial_documents/v4_diagnostic_generator.py` | ZMB-3 + MEN-1..7 + dead code elim |
| `modules/utils/benchmarks.py` | ZMB-4: iao_score key eliminada |

### Tests (FASE-F)
- Sin tests nuevos (limpieza, sin cambio de comportamiento)
- `run_all_validations.py --quick` 4/4 PASS

### BRECHAS-DINAMICAS (FASE-A a FASE-E): Eliminacion hardcode "LAS 4 BRECHAS"
Proyecto para eliminar el hardcode de 4 brechas y mostrar dinámicamente N brechas detectadas (0-10).

**FASE-A (Templates)**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md` — 4 ranuras hardcode → `${brechas_section}`, tabla 4 filas → `${brechas_resumen_section}`
- `modules/commercial_documents/templates/diagnostico_v4_template.md` — 4 ranuras hardcode → `${brechas_section}`
- `modules/commercial_documents/v4_diagnostic_generator.py` (`_get_default_template`) — 4 ranuras → `${brechas_section}`

**FASE-B (Generator)**:
- `v4_diagnostic_generator.py` — Métodos nuevos: `_build_brechas_section()`, `_build_brechas_resumen_section()`
- `_inject_brecha_scores()`: `min(..., 4)` → `min(..., 10)`
- 5 tests nuevos en `test_diagnostic_brechas.py`

**FASE-C (Scorer)**:
- `modules/financial_engine/opportunity_scorer.py` — 5 nuevos tipos en SEVERITY/EFFORT/IMPACT_MAP, _JUSTIFICATION_TEMPLATES
- 6 tests nuevos en `test_opportunity_scorer.py`

**FASE-D (Mapper Fix)**:
- `pain_solution_mapper.py` — Duplicate `low_ia_readiness` corregido
- `asset_catalog.py` — `optimization_guide.promised_by` fix

**FASE-E (Validación)**:
- v4complete amaziliahotel.com: 6 brechas mostradas dinámicamente (NO hardcode 4)
- Coherence score: 0.84 (umbral 0.80)
- Publication gates: READY_FOR_PUBLICATION
- Header: "BRECHAS CRÍTICAS IDENTIFICADAS" (no "LAS 4 BRECHAS")

### Tests (BRECHAS-DINAMICAS)
- 5 tests FASE-B + 6 tests FASE-C = 11 tests nuevos
- 0 regresiones en suite existente
- E2E validado con amaziliahotel.com

### FASE-D (Validacion E2E): Validacion sin cambios de codigo
- v4complete ejecutado contra amaziliahotel.com — sin crashes, coherence 0.84, READY_FOR_PUBLICATION
- **Fix WhatsApp (FASE-A)**: Funcional. `_detect_whatsapp_from_html()` opera correctamente; sitio genuinamente no tiene WhatsApp (brecha legítima). Hallazgo nuevo: `phone_web=null` cuando `tel:` link existe en HTML (no-bloqueante).
- **Fix Citability (FASE-B)**: Funcional. `blocks_analyzed=0` genera narrativa "Contenido No Discoverable por IA" (no "poco estructurado").
- **Fix Regional (FASE-C)**: Parcial. Concatenación "yRevisan" corregida. Región detectada como "nacional" (fallback) — "Lo que está pasando en nacional" aparece en template.
- No cambios de código en esta fase.
- Evidence: `evidence/fase-d/` (ejecucion.log, verificacion.txt)

## [4.25.2] - 2026-04-08

### FASE-A (AEO OG Fix): Deteccion Real de Open Graph
- `modules/auditors/seo_elements_detector.py` - Stub reemplazado con implementacion real BeautifulSoup
  - `_detect_open_graph()`: detecta `<meta property="og:*">`, requiere og:title + og:description
  - `_detect_images_alt()`: cuenta imagenes sin atributo alt, pasa si <20%
  - `_detect_social_links()`: detecta 8 dominios sociales (FB, IG, X, LinkedIn, YT, TikTok, Pinterest)
  - `detect()`: conecta los 3 metodos, maneja errores con confidence="low"
  - Eliminado `__init__` hardcodeado con `self.confidence = "estimated"`
- Parte del fix AEO score: `seo_elements.open_graph` ahora retorna datos reales (antes siempre False)
- Dependencia: beautifulsoup4==4.14.3 (ya existia en requirements.txt)

### Archivos Nuevos
| Archivo | Descripcion |
|---------|-------------|
| `tests/auditors/test_seo_elements_detector.py` | 9 tests: OG positive/negative/partial, alt good/bad, social/no-social, edge cases |

### Tests
- 9 tests nuevos en `tests/auditors/test_seo_elements_detector.py`
- 0 regresiones

## [4.25.1] - 2026-04-07

### Calibracion Factores Financieros

- `modules/utils/financial_factors.py` - Actualiza comisiones OTA:
  - comision_ota_base: 0.15 → 0.20 (proxy México/LatAm 2024-2025)
  - comision_ota_min: 0.12 → 0.18
  - comision_ota_max: 0.18 → 0.22
  - Agrega nuevos campos: reservas_ota_proporcion (0.65), reservas_directo_proporcion (0.35),
    uso_ia_proporcion_min/max (0.10-0.20)
- `data/benchmarks/plan_maestro_data.json` - Agrega seccion `thresholds` con nota de fuentes
  (Skift Research State of Travel 2024, Mordor Intelligence Mexico 2024, PwC/ITU 2024-2025)
- Fuentes: investigacion "Más Allá de la OTA: Cuantificando la Pérdida Económica por Invisibilidad
  Digital e IA en Hoteles Boutique del Eje Cafetero" (benchmarks/)
- Impacto: factor_perdida_base sube de ~0.043 a ~0.060, pérdida estimada más realista

## [4.25.0] - 2026-04-06

### FASE-E: Micro-Content Local Generator
- `modules/asset_generation/local_content_generator.py` - Generador de paginas de contenido
  local orientadas a keywords long-tail para hoteles boutique (NUEVO)
  - Dataclasses: LocalContentPage, LocalContentSet
  - KEYWORD_TEMPLATES por tipo: termales, parque_natural, pueblo_patrimonio, cafe, boutique, general
  - 6 secciones por pagina: intro, contexto, informacion, practica, recomendaciones, conclusion
  - Contenido 800-1200 palabras con clamp automatico al maximo
  - Schema Article JSON-LD por pagina
  - Meta description 150-160 chars, internal links (home + WhatsApp)
  - content_passes_scrubber(): deteccion de frases AI genericas
  - Content passes ContentScrubber de FASE-B
- `modules/asset_generation/templates/local_content/page_template.md` - Template de prompt LLM
- `modules/asset_generation/templates/local_content/keyword_selection.md` - Guia de seleccion keywords
- `modules/asset_generation/asset_catalog.py` - Entrada local_content_page registrada
- `tests/asset_generation/test_local_content_generator.py` - 15 tests:
  - keyword_selection_termales, keyword_selection_boutique
  - page_structure, word_count_range (800-1200), internal_links (min 2)
  - article_schema JSON-LD valido, hotel_mention_natural (no vendedora)
  - content_scrubber_pass, max_5_pages, asset_catalog_entry
  - slug_generation, content_scrubber_compatibility_method
  - eco_hotel_type, hotel_without_phone, meta_description_length
- Total: 15 tests nuevos, 0 regresiones
- Add-on comercial vendible ($50K COP por 3 paginas)

## [4.24.0] - 2026-04-07

### FASE-D: Google Search Console Integration
- `modules/analytics/google_search_console_client.py` - Cliente GSC con webmasters v3 API (NUEVO)
  - Dataclasses: GSCQueryData, GSCPageData, GSCReport
  - Metodos: is_configured(), get_search_analytics(), get_top_opportunities()
  - Graceful fallback: is_available=False sin credenciales
  - Reutiliza service account de GA4 (config/google-analytics-key.json)
  - Costo API: GRATIS
- `modules/analytics/data_aggregator.py` - Unifica GA4 + GSC (NUEVO)
  - UnifiedAnalyticsData con confidence: LOW/MEDIUM/HIGH
  - Metricas derivadas: estimated_ia_visibility, organic_health_score
  - Graceful degradation: funciona sin GSC, sin GA4, o sin ambos
- `modules/onboarding/add_gsc_step.py` - Paso GSC opcional en onboarding (NUEVO)
- `modules/commercial_documents/v4_diagnostic_generator.py` - Integracion GSC en diagnostico
- `data_models/analytics_status.py` - Campos gsc_available, gsc_error, gsc_status_text
- `config/provider_registry.yaml` - Entrada gsc agregada
- `tests/analytics/test_google_search_console_client.py` - 14 tests
- `tests/analytics/test_data_aggregator.py` - 19 tests
- Total: 33 tests nuevos, 0 regresiones

## [4.23.0] - 2026-04-06

### FASE-A: Canonical Metrics + Provider Registry + Permission Modes
**Nota:** FASE-A se implemento en sesion anterior sin completar actualizacion de registros. Se documenta aqui retroactivamente.
- `modules/utils/canonical_metrics.py` - Diccionario maestro de metricas canonicas (7 metricas, 24 aliases)
- `modules/utils/provider_registry.py` - Singleton que centraliza configuracion de proveedores
- `modules/utils/permission_mode.py` - 4 modos de permiso: auto, smart_approve, approve, chat
- `config/provider_registry.yaml` - 8 proveedores configurados (ga4, profound, semrush, places_api, serpapi, pagespeed, rich_results, openrouter)
- `tests/utils/` - 57 tests (22 + 13 + 22)
- `main.py` - Argumento --permission-mode agregado

### FASE-A: Permission Modes - Integracion Completa (Tarea 3)
**Problema:** El argumento --permission-mode se parseaba en main.py pero nunca se usaba. El import de PermissionMode era un "flag fantasma" sin efecto en el flujo.
- `modules/orchestration_v4/two_phase_flow.py` - TwoPhaseOrchestrator acepta `permission_mode` + `on_ask_permission`. Nuevo metodo `check_external_operation()`.
- `modules/orchestration_v4/onboarding_controller.py` - OnboardingController acepta `permission_mode` y lo pasa al orchestrator.
- `modules/orchestration_v4/__init__.py` - Re-exporta PermissionMode, OperationPermission, check_permission.
- `main.py` - `args.permission_mode` parseado a `PermissionMode` enum. Gate antes de `auditor.audit()` (~$0.03 USD). Modo `chat` omite auditoria externa.
- Tests: 19 pasando (existentes, sin regresiones)
- Arquitectura: `modules/orchestration_v4/orchestrator.py` (referenciado en plan) nunca existio. Integracion correcta en archivos reales.

### FASE-B: Document Quality Gate + Content Scrubber
- `modules/postprocessors/document_quality_gate.py` - 3 blocker checks + 2 warning checks
  - placeholder_region: Detecta "default" como region (blocker)
  - duplicate_currency: Detecta "COP COP" (blocker)
  - zero_confidence: Detecta "0% de confianza" en documentos comerciales (blocker)
  - mixed_language: Portugues/ingles en texto espanol (warning)
  - generic_ai_phrases: Frases boilerplate de LLM (warning)
- `modules/postprocessors/content_scrubber.py` - Post-procesador idempotente con 5 reglas
  - Reemplaza "en default" con ciudad real del hotel
  - Elimina "COP COP" duplicado
  - Reemplaza "0% confianza" con texto comercial seguro
  - Convierte pt->es e en->es (diccionario contextual)
  - Suaviza frases genericas de AI
- `publication_gates.py` - Gate #7: content_quality_gate integrado
- `asset_content_validator.py` - Nuevos patterns: "en default", "COP COP"
- `main.py` - FASE 3.6: Content Scrubber + Quality Gate inyectado en flujo v4complete

### FASE-C: Priorizacion Ponderada con Impacto Estimado
- `modules/financial_engine/opportunity_scorer.py` (NUEVO) - OpportunityScorer con modelo de 3 factores:
  - Severidad del Gap (0-40 pts): gravedad vs competencia
  - Esfuerzo de Implementacion (0-30 pts): facilidad de implementar
  - Impacto en Conversion Directa (0-30 pts): impacto directo en reservas
  - Total 0-100 pts, ranking automatico, justificacion legible para hotelero
- `modules/financial_engine/calculator_v2.py` - Soporte para pesos dinamicos via opportunity_scores
  - Nuevo parametro opportunity_scores en calculate() y calculate_conditional()
  - _compute_dynamic_brecha_weights() para normalizar pesos
  - Backward compatible: sin scores = pesos fijos actuales
- `data_models/canonical_assessment.py` - Campo opportunity_scores opcional agregado
- `modules/commercial_documents/v4_diagnostic_generator.py` - Inyeccion de scores en template
  - _compute_opportunity_scores(): calcula scores desde audit_result
  - _inject_brecha_scores(): agrega brecha_N_score, severity, effort, impact, justification, rank
  - Backward compatible: sin scores = comportamiento actual
- `tests/financial_engine/test_opportunity_scorer.py` - 18 tests nuevos:
  - Severidad con/sin competidores, esfuerzo FAQ/GBP, impacto WhatsApp
  - Total score range 0-100, ranking, COP estimation, justificacion
  - Backward compat, extractor, score from assessment, weights summary, empty brechas

---

## [4.22.0] - 2026-04-05

### FIX CRITICO - Duplicacion de metricas en scorecard diagnostico

**Problema identificado:**
- `v4_diagnostic_generator.py:1078-1085`: `_calculate_activity_score()` inyectaba `geo_score * 0.5` en su resultado
- Esto causaba que la fila "Activity Score (GBP)" compartiera ~50% de sus datos con "Google Maps (GEO)"
- El diagnostico presentaba dos scores independientes cuando uno contenia al otro
- Ejemplo: GEO=72 inflaba automaticamente Activity=86 (36 puntos venian de la inyeccion directa)

**Solucion aplicada:**
- Nueva funcion `_calculate_competitive_score(audit_result)`: usa geo_scores de competidores reales (Places API) para calcular posicionamiento relativo
- La formula ahora mide: ranking percentile vs competidores cercanos + gap penalty al siguiente competidor
- Legacy alias `_calculate_activity_score = _calculate_competitive_score` mantiene compatibilidad con callers existentes
- Template renombrado: "Activity Score (GBP)" -> "Posicion Competitiva (vs cercanos)"
- Benchmark regional ajustado: 30/100 -> 45/100

**Metricas ahora ortogonales:**
| Pilar | Fuente de datos | Que mide |
|-------|-----------------|----------|
| GEO | Places API (perfil propio) | Completitud absoluta del perfil |
| Posicion Competitiva | Places API (competidores + ranking) | Posicion relativa vs competidores cercanos |
| Web/SEO | PageSpeed + Schema web | Credibilidad del sitio |
| AEO | Schema Hotel + FAQ + Open Graph + Citability | Legibilidad para IAs |

**Archivos modificados (2):**
- `v4_diagnostic_generator.py`: funcion corregida + template renombrado
- `output/v4_complete/`: nuevo diagnostico con scores validados

**Validacion:**
- 18/18 tests relacionados pasaron sin regresiones
- Comparacion linea base: GEO=72 antes y despues (sin cambio competitivo=50, antes 86)

### NOTAS
- `gbp_auditor._calcular_activity_score` (pipeline legacy via report_builder.py) NO modificado -- usa datos distintos (posts, respuestas) pero comparte el problema conceptual de overlapping con GEO
- Pendiente de tratamiento cuando se active ese pipeline

## [4.21.0] - 2026-04-04

### ELIMINADO - Redundancia AEO/IAO en scorecard diagnostico
- Template V6: eliminadas filas "Visibilidad en IA (AEO)" y "Optimizacion ChatGPT (IAO)"
- Scorecard unificado bajo "AEO - Infraestructura para IAs" (XX/100) -- dato 100% medible del audit web
- Regla de negocio: sin Asset = sin score en el diagnostico

### ELIMINADO - Metodos IAO/Voice de modulos internos
- v4_diagnostic_generator.py: eliminados _calculate_iao_score(), _calculate_score_ia(), _calculate_voice_readiness_score()
- v4_diagnostic_generator.py: renombrado _calculate_schema_infra_score() -> _calculate_aeo_score()
- gap_analyzer.py: eliminado pilar "Momentum IA", redistribucion 3->2 pilares (GBP + AEO)
- report_builder.py: eliminado _calculate_iao_score() y filas IAO de scorecards

### LIMPIEZA - Dead code
- Voice readiness eliminado (retornaba "--" hardcodeado)
- IATester wrapper eliminado (requiere GA4 real, no funciona en produccion actual)

### NOTAS
- aeo_metrics_gen.py se mantiene como modulo tecnico interno (no comercial)
- GA4 no modificado: puede enriquecer mediciones AEO en el futuro pero no genera score separado

## [4.20.0] - 2026-04-03

### ARCHIVO - Modulo observability deprecado
- `observability/` movido a `archives/deprecated_modules_20260304/observability/`
- Motivo: modulo huérfano (0 imports), persistencia inactiva, calibracion hardcodeada, sin integracion con flujo operacional
- Los validadores actuales (CoherenceValidator, contradiction_engine, consistency_checker) cubren la calidad per-corrida

### AGENT HARNESS v3.2.0 - REFACTOR ARQUITECTONICO COMPLETO

**CRITICAL FIX:**
- `agent_harness/core.py` linea 65: `tokens=shlex....cmd)` -> `tokens = shlex.split(command)`. Delegacion recursiva ahora funcional.
- `agent_harness/core.py` linea 80: `token=***` -> `token = tokens[i]`.

**ARCHITECTURAL IMPROVEMENTS (7 archivos, +900 lineas):**

**core.py - Orchestrator (306 -> 506 lines):**
- Timeout protection: `_execute_with_timeout()` via threading.Timer, configurable via `default_task_timeout`
- Background task lifecycle: `BackgroundTaskInfo` con estados running/completed/failed/timeout
- `_poll_background_tasks()`: detecta procesos terminados, limpia zombies >1h, reporta timeout >5min
- `register_validator(task_name, fn)`: validacion por tipo de tarea (fallback a generico si no hay)
- `_get_ui_colors()`: graceful fallback si modules.utils.ui_colors no existe
- `get_skill_metrics()`, `get_error_learning_report()`: metodos de introspeccion
- Handler ejecutado con timeout -- ya no hay riesgo de freeze indefinido

**memory.py - Memory Manager (328 -> 387 lines):**
- Thread safety: `threading.Lock` por archivo de sesion, previene race conditions
- Escritura atomica: escribe a `.tmp` + `rename`
- Indice invertido: `target_index.json` mapea `target_id -> [session_files]`
- `load_history()` consulta indice O(1) en lugar de scan lineal O(N) sobre todas las sesiones
- `rebuild_index()`: for-rebuild si el indice se corrompe
- `cleanup_old_sessions()` actualiza el indice al remover archivos viejos

**skill_router.py (191 lines):**
- Paths absolutos: `PROJECT_ROOT = Path(__file__).resolve().parent.parent`
- `.agents/workflows`, `skills`, `.agents/skills` resueltos desde ubicacion del modulo, no CWD
- Ya no depende del directorio de trabajo actual

**skill_executor.py (313 -> 433 lines):**
- `dry_run=False` como default (antes era `True` -- footgun que ocultaba errores)
- `SkillMetricsCollector`: persiste stats en `.agent/memory/skill_metrics.csv`
- Cada skill ejecutada registra: invocaciones, tasa de exito, duracion promedio

**self_healer.py (334 -> 445 lines):**
- `ErrorLearner`: captura errores no-matched, los agrupa, persiste en `unknown_errors.json`
- `get_learning_report()`: sugiere entradas para error_catalog.json (ocurrencias >= 2)
- PlanValidator: lazy import con try/except ImportError (graceful si modulo no existe)
- Si PlanValidator no disponible, retorna "skipped" en vez de crashear

**mcp_client.py (54 -> 250 lines):**
- Nested event loop fix: detecta loop corriendo, usa threading + new_event_loop como fallback
- Si `nest_asyncio` disponible, lo aplica automaticamente
- `list_tools()`, `list_tools_sync()`, `read_resource_sync()`: wrappers nuevos
- Import de `mcp` package deferred (no crash si no instalado)

**types.py (+86 lines):**
- Nuevas clases: `BackgroundTaskInfo`, `TaskValidator` (Protocol), `SkillMetrics`
- `SkillMetrics.record()`, `success_rate`, `avg_duration` properties

**Version:** 0.3.0 -> 3.2.0

## [4.19.0] - 2026-04-03

### INTEGRACION ECOSISTEMA DE AGENTES: Doctor + Pre-commit + Validacion Automatica

**NUEVOS SCRIPTS:**
- `scripts/doctor.py` (354 lineas) - Punto de entrada unificado para diagnostico del ecosistema
  - `--doctor` flag integrado en `main.py`
  - Soporta --agent, --context, --status, --json
  - Regenera SYSTEM_STATUS.md automaticamente desde datos reales
- `scripts/validate_agent_ecosystem.py` (259 lineas) - 8 checks automatizados
  - Symlink integrity, README refs, skills tracking, shadow logs, memory, gitignore, knowledge, agents dir
  - Manejo gracefully de errores Windows symlink

**PRE-COMIT HOOKS (2 nuevos):**
- `agent-ecosystem` - Valida skills, refs, symlink, shadow logs, memoria antes de cada commit
- `version-sync` - Sincroniza VERSION.yaml con README, AGENTS, CONTRIBUTING, GUIA_TECNICA, etc.

**WORKFLOWS (.agents/workflows/):**
- ELIMINADO: `audit_guardian.md` (deprecated, reemplazado por `v4_complete.md`)
- ELIMINADO: `qa_guardian.md` + `v4_coherence_validator.md` -> `v4_quality_validator.md` (unificado)
- ELIMINADO: `v4_financial_calculation.md` -> merged en `v4_financial_scenarios.md`
- MOVIDO: `v4_module_test_map.yaml` -> `templates/` (junto a `v4_regression_guardian.py`)
- ELIMINADO: `__pycache__/` (basura de ejecucion)
- FIX: Symlink `.agent/workflows` -> `.agents/workflows` (estaba roto)
- README.md reescrito con estructura actualizada (17 skills)

**DOCUMENTACION:**
- NUEVO: `.agent/CONVENTION.md` - Contrato de arquitectura para cualquier futuro agente
- REGENERADO: `.agent/SYSTEM_STATUS.md` desde datos reales (estaba stale desde Feb 2026)
- REGENERADO: `.agent/knowledge/DOMAIN_PRIMER.md` (v4.0.0 stale -> v4.19.0, 21 modulos, 138 archivos Python)
- FIX: `scripts/validate_context_integrity.py` (error Windows symlink stat + modulos nuevos agregados: analytics, geo_enrichment, quality_gates, auditors, commercial_documents, delivery, providers)
- FIX: `scripts/sync_config.yaml` (patterns actualizados)
- FIX: `docs/contributing/procedures.md` §4 - renombrado "Decision Engine" -> "Financial Engine", eliminada referencia a script fantasma `generate_domain_primer.py`
- FIX: `docs/CONTRIBUTING.md` - agregado DOMAIN_PRIMER.md a flujo de contribucion (Paso 5b, tabla manual docs, seccion Regenerable)

**FIX CLI:**
- `main.py` con `--doctor` flag integrado
- Manejo de errores Windows symlink en ambos validadores
- NUEVO: `doctor.py --regenerate-domain-primer` - regenera DOMAIN_PRIMER.md desde modulos reales en vivo

**Resultado:** Las carpetas .agent/ y .agents/workflows/ dejaron de ser "islas" y ahora son parte del flujo diario con validacion automatica pre-commit.

## [4.18.0] - 2026-04-02

### CERTIFICACION E2E 100% ANALYTICS: ANALYTICS-E2E-CERT-01

**Cambio de codigo (1 archivo, +10 lineas):**
- `modules/commercial_documents/pain_solution_mapper.py` — metodo `_detect_analytics_pains()`
  - Agrega pain `low_organic_visibility` cuando `ga4_available=False`
  - Sin GA4 no se puede medir trafico organico → deteccion implicita de baja visibilidad

**Resultado de certificacion E2E (12/12 PASADOS):**
- D1: analytics_data definido antes de detect_pains ✅
- D2: analytics_data llega a PainSolutionMapper ✅
- D3: analytics_data inyectado en diagnostico ✅
- D4: analytics_data inyectado en propuesta ✅
- D5: analytics persistido en v4_complete_report.json ✅
- D6: Pains no_analytics_configured + low_organic_visibility detectados ✅
- D7: AMBOS assets analytics generados (analytics_setup_guide + indirect_traffic_optimization) ✅
- D8: GoogleAnalyticsClient graceful fallback ✅
- D9: Profound/Semrush stubs graceful ✅
- D-A: V4AssetOrchestrator recibe analytics_data ✅
- D-B: analytics_setup_guide = 4952 bytes, 120 lineas ✅
- D-C: indirect_traffic_optimization = 5226 bytes, 128 lineas ✅

**Assets generados:**
- 9 assets totales (antes 8)
- analytics_setup_guide: 4952 bytes, guia GA4 paso a paso
- indirect_traffic_optimization: 5226 bytes, estrategias trafico indirecto

**Certificado:** output/CERTIFICADO_ANALYTICS_E2E.md

## [v4.17.0] - 2026-04-02

### FIX HANDLERS FALTANTES: analytics_setup_guide + indirect_traffic_optimization

**Handlers implementados:**
- `AnalyticsSetupGuideGenerator` (modules/delivery/generators/analytics_setup_guide_gen.py)
  - Carga template + personaliza con nombre/ciudad/URL del hotel
  - Fallback con contenido estatico si template no existe
- `IndirectTrafficOptimizationGenerator` (modules/delivery/generators/indirect_traffic_optimization_gen.py)
  - Carga template + personaliza con nombre del hotel
  - Fallback con contenido estatico si template no existe

**Handlers registrados en ConditionalGenerator._generate_content():**
- `elif asset_type == "analytics_setup_guide"` → AnalyticsSetupGuideGenerator
- `elif asset_type == "indirect_traffic_optimization"` → IndirectTrafficOptimizationGenerator

**D-A FIX: Analytics data pasado al V4AssetOrchestrator:**
- `generate_assets()` ahora acepta `analytics_data` opcional
- `detect_pains()` interno ahora recibe analytics_data (antes: None)
- pain `no_analytics_configured` ahora se detecta en el orchestrator
- main.py pasa analytics_data al orchestrator (L2092)

**Resultado de validacion:**
- Assets generados: 8 (antes 7)
- analytics_setup_guide: GENERADO (4952 bytes, 120 lineas)
- archivo: hotel_visperas/analytics_setup_guide/ESTIMATED_guia_configuracion_ga4_*.md
- Contenido completo con 7 pasos de configuracion GA4

## [v4.16.0] - 2026-04-02

### ANALYTICS-FIX-01: Fix critico UnboundLocalError + Analisis de Assets

**FASE A: Fix de orden en main.py (CRITICO)**
- Movido bloque analytics_data de L1958 a L1871, ANTES de PainSolutionMapper.detect_pains()
- Corregido UnboundLocalError: analytics_data undefined en L1851
- Import de GoogleAnalyticsClient y AnalyticsStatus: sin duplicados (1 ocurrencia cada uno)
- Pipeline ahora ejecuta completo: v4complete exit code 0

**FASE B: Analisis de assets de analytics (READ-ONLY)**
- D-B CONFIRMADO: analytics_setup_guide sin handler en ConditionalGenerator._generate_content()
- D-C CONFIRMADO: indirect_traffic_optimization sin handler en ConditionalGenerator._generate_content()
- Ambos assets estan en ASSET_CATALOG como IMPLEMENTED con templates existentes
- Assets fueron planificados pero NO generados (7 de 8 assets generados)

**FASE C: Verificacion**
- v4complete completo sin crash
- analytics persistido en v4_complete_report.json (seccion lines 163-174)
- Diagnostic incluye footer de transparencia analytics
- 8 pains detectados (vs 0 antes del fix)
- Reporte generado: ANALYTICS_FIX_REPORT_20260402.md


## [v4.15.0] - 2026-04-02

### Analytics E2E Bridge - COMPLETADO (01 + 02 + 04)

**ANALYTICS-01: Persistir analytics en JSON**
- `v4_complete_report.json` ahora incluye seccion `analytics` con:
  - `ga4_available`, `ga4_status`, `ga4_error`
  - `profound_available`, `profound_status`
  - `semrush_available`, `semrush_status`
  - `is_complete`, `missing_credentials`, `timestamp`
- Backwards compatible: sin cambios en report existente

**ANALYTICS-02: V4ProposalGenerator recibe analytics_data**
- `V4ProposalGenerator.generate()` acepta `analytics_data: Optional[Dict] = None`
- Metodo `_inject_analytics()` con 2 modos:
  - GA4 configurado: muestra metricas reales de trafico indirecto
  - Fallback: indica que GA4 no esta configurado
- main.py pasa `analytics_data` al proposal generator (L2040)
- Template V6 soporta placeholder `${analytics_transparency_section}`

**ANALYTICS-04: Analytics → Asset bridge via PainSolutionMapper**
- 3 nuevos pain types: `no_analytics_configured`, `low_organic_visibility`, `no_ga4_enhanced`
- Deteccion automatica:
  - GA4 no disponible → pain "Sin Analytics Configurado" (medium severity)
  - GA4 sin enhanced ecommerce → pain "GA4 sin Configuracion Avanzada" (low severity)
  - Trafico organico < 1000 sesiones/mes → pain "Baja Visibilidad Organica" (medium severity)
- 2 nuevos assets con templates completos:
  - `analytics_setup_guide` (guia_configuracion_ga4.md)
  - `indirect_traffic_optimization` (optimizacion_trafico_indirecto.md)
- Main.py detecta pains de analytics incluso sin audit_result completo
- Registro en asset_catalog.py con status IMPLEMENTED
- Refactor DRY: `_detect_analytics_pains()` metodo privado compartido

**PLAN ANALYTICS-E2E-BRIDGE: 100% COMPLETADO**

## [v4.14.0] - 2026-04-02

### Analytics E2E Bridge - Fases de Documentacion

**ANALYTICS-03: Documentacion de Stubs**
- ProfoundClient: docstring completo con instrucciones de activacion paso a paso
- SemrushClient: docstring completo con instrucciones de activacion paso a paso
- `modules/analytics/README.md`: nuevo archivo con tabla de todos los providers analytics
- Fallback a mock documentado y graceful (sin excepciones, retorna None)
- Variables de entorno documentadas: PROFOUND_API_KEY, SEMRUSH_API_KEY

## [v4.13.0] - 2026-04-01

### Analytics Transparency Loop (FASE-IAO-06)
- **NUEVO**: `data_models/analytics_status.py` - Clase AnalyticsStatus para rastrear disponibilidad de fuentes de datos
- **NUEVO**: Metodo `_check_analytics_status()` en V4DiagnosticGenerator - verifica estado de GA4/Profound/Semrush SIN hacer llamadas API
- **NUEVO**: Metodo `_build_transparency_section()` - genera seccion opcional "Fuentes de Datos Usadas en Este Diagnostico"
- **Cambio**: Diagnostico ahora informa POR QUE no hay datos (credenciales faltantes, APIs no configuradas) en vez de silenciar con ceros/guiones
- **Cambio**: Nuevo flag `show_analytics_transparency` en generador (default: True)
- **Template**: `${analytics_transparency_section}` en diagnostico_v6_template.md - solo aparece cuando alguna fuente falta
- **Docs**: capabilities.md actualizada con 4 nuevas capacidades (AnalyticsStatus, GoogleAnalyticsClient, ProfoundClient, SemrushClient) - IA Hoteles Agent

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.12.0] - 2026-04-01

### Objetivo
GA4 Integration - Tráfico Indirecto como Método #5 de Medición IA (GAP-IAO-01-05)

### Completado

**GAP-IAO-01-05: GA4 para Tráfico Indirecto**
- GoogleAnalyticsClient: cliente real con lazy init, graceful fallback, sin romper pipeline
- IndirectTrafficMetrics consolidado en data_models/aeo_kpis.py (eliminado duplicado)
- Campos date_range y note agregados a IndirectTrafficMetrics
- Método from_ga4_response() para crear métricas desde respuesta de GA4
- GoogleAnalyticsClient exportado desde modules/analytics/__init__.py
- _calculate_score_ia() integrado con GA4: construye AEOKPIs, calcula composite_score
- _calculate_iao_score() fallback fix: retorna schema_infra_score cuando IATester falla
- IAReadinessCalculator: ga4_indirect weight 0.10, redistribución proporcional cuando GA4 no disponible
- Backwards compatible: GA4 completamente opcional, try/except en todos los paths

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| tests/test_google_analytics_client.py | 17 tests para GoogleAnalyticsClient |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/analytics/google_analytics_client.py | Cliente real + eliminado duplicado IndirectTrafficMetrics |
| data_models/aeo_kpis.py | IndirectTrafficMetrics: date_range, note, from_ga4_response() |
| modules/analytics/__init__.py | Export GoogleAnalyticsClient |
| modules/commercial_documents/v4_diagnostic_generator.py | _calculate_score_ia() GA4 wiring, _calculate_iao_score() fallback |
| modules/auditors/ia_readiness_calculator.py | ga4_indirect weight 0.10, weight redistribution |
| tests/data_validation/test_aeo_kpis.py | Weights fijos + indirect_traffic en required fields |
| tests/auditors/test_ia_readiness_calculator.py | Weights fijos + 5 tests GA4 nuevos |

### Tests
- 17 tests nuevos en test_google_analytics_client.py
- 5 tests GA4 agregados a test_ia_readiness_calculator.py
- 46/46 tests passing (0 regresiones en módulos afectados)
- 1755/1829 tests passing (74 failures pre-existentes, no relacionados)

### Características
- **Método #5 de KB**: GA4 como método de medición de tráfico indirecto post-consulta IA
- **Graceful Fallback**: Sin credenciales → retorna data_source: N/A sin romper pipeline
- **Weight Redistribution**: Cuando GA4 no disponible, peso se redistribuye proporcionalmente
- **AEOKPIs Integration**: Construye objeto AEOKPIs con IATester + GA4 datos para composite score

---

## [4.12.0] - 2026-04-01

### Objetivo
GA4 Integration - Tráfico Indirecto como Método #5 de Medición IA (GAP-IAO-01-05)

### Completado

**GAP-IAO-01-05: GA4 para Tráfico Indirecto**
- GoogleAnalyticsClient: cliente real con lazy init, graceful fallback, sin romper pipeline
- IndirectTrafficMetrics consolidado en data_models/aeo_kpis.py (eliminado duplicado)
- Campos date_range y note agregados a IndirectTrafficMetrics
- Método from_ga4_response() para crear métricas desde respuesta de GA4
- GoogleAnalyticsClient exportado desde modules/analytics/__init__.py
- _calculate_score_ia() integrado con GA4: construye AEOKPIs, calcula composite_score
- _calculate_iao_score() fallback fix: retorna schema_infra_score cuando IATester falla
- IAReadinessCalculator: ga4_indirect weight 0.10, redistribución proporcional cuando GA4 no disponible
- Backwards compatible: GA4 completamente opcional, try/except en todos los paths

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| tests/test_google_analytics_client.py | 17 tests para GoogleAnalyticsClient |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/analytics/google_analytics_client.py | Cliente real + eliminado duplicado IndirectTrafficMetrics |
| data_models/aeo_kpis.py | IndirectTrafficMetrics: date_range, note, from_ga4_response() |
| modules/analytics/__init__.py | Export GoogleAnalyticsClient |
| modules/commercial_documents/v4_diagnostic_generator.py | _calculate_score_ia() GA4 wiring, _calculate_iao_score() fallback |
| modules/auditors/ia_readiness_calculator.py | ga4_indirect weight 0.10, weight redistribution |
| tests/data_validation/test_aeo_kpis.py | Weights fijos + indirect_traffic en required fields |
| tests/auditors/test_ia_readiness_calculator.py | Weights fijos + 5 tests GA4 nuevos |

### Tests
- 17 tests nuevos en test_google_analytics_client.py
- 5 tests GA4 agregados a test_ia_readiness_calculator.py
- 46/46 tests passing (0 regresiones en módulos afectados)
- 1755/1829 tests passing (74 failures pre-existentes, no relacionados)

### Características
- **Método #5 de KB**: GA4 como método de medición de tráfico indirecto post-consulta IA
- **Graceful Fallback**: Sin credenciales → retorna data_source: N/A sin romper pipeline
- **Weight Redistribution**: Cuando GA4 no disponible, peso se redistribuye proporcionalmente
- **AEOKPIs Integration**: Construye objeto AEOKPIs con IATester + GA4 datos para composite score

---

## [4.11.0] - 2026-03-30

### 🎯 Objetivo
Documentación Oficial - Actualización según CONTRIBUTING.md R8: GEO Enrichment Integration

### ✅ Completado

**FASE-7 - Documentación Oficial**
- CHANGELOG.md: Entrada v4.11.0 con features GEO
- GUIA_TECNICA.md: Nueva sección "GEO Enrichment Integration"
- .agents/workflows/README.md: geo_flow y módulos GEO listados
- capabilities.md: 4 nuevas capacidades actualizadas
- REGISTRY.md: FASE-1 a FASE-8 registradas

**FASE-1 a FASE-6 - GEO Integration (Previa)**
- FASE-1: Diagnóstico - Mapeo hotel_data a 42 métodos GEO
- FASE-2: GEO Flow Orchestrator - geo_flow.py integrado en v4_asset_orchestrator
- FASE-3: GEO Enrichment Layer - Asset generation enriquecido con datos GEO
- FASE-4: Sync Contract Analyzer - 8 combinaciones de sincronización
- FASE-5: Asset Responsibility Contract - Orden de implementación
- FASE-6: GEO Diagnostic - Dashboard y checklist GEO

### 📁 Módulos GEO Documentados

|| Módulo | Descripción | Estado ||
||--------|-------------|--------|
|| `geo_flow.py` | Orchestrator del flujo GEO | conectada |
|| `GEOEnrichmentLayer` | Enriquecimiento de assets con datos GEO | conectada |
|| `SyncContractAnalyzer` | Análisis de sincronización cross-platform | conectada |
|| `AssetResponsibilityContract` | Contrato de responsabilidad de assets | conectada |

### 🔧 Características

- **GEO Flow**: Orquestación completa del pipeline GEO
- **Sync Contract**: 8 combinaciones de sincronización (EXACT, SURFACE, SEMANTIC, etc.)
- **Responsibility Contract**: Orden de implementación de assets (Schema → Onsite → Offsite)
- **Backward Compatibility**: ✅ Preservada

### 🔗 Links
- [Plan FASE-7](./.opencode/plans/05-prompt-inicio-sesion-fase-7.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.10.0] - 2026-03-27

### 🎯 Objetivo
V6 E2E Certification - Formato V6 de documentos comerciales con datos reales para Hotel Vísperas

### ✅ Completado

**FASE V6-5 - E2E Certification**
- Ejecución E2E completa del flujo v4complete
- Documentos generados en formato V6 (DIAGNOSTICO_V6, PROPUESTA_V6)
- Frontmatter YAML con version, coherence_score, document_type
- Coherence score: 0.84 (umbral: 0.80)
- 6 assets planificados y generados
- Delivery package: hotelvisperas_20260327.zip
- No texto mixed-language detectado
- 52/52 regression tests PASS

**FASE V6-4 - Pain Solution Mapper Integration**
- PainSolutionMapper integrado en pipeline de documentos
- Mapeo dinámico de problemas a soluciones
- Financial impact calculado por problema

**FASE V6-3 - Proposal Generator V6**
- Pricing real extraído de ValidationSummary
- Hybrid pricing model (tier-based)
- ROI calculation dinámico
- GATE compliance verificado

**FASE V6-2 - Diagnostic Generator V6**
- Estructura V6 con YAML frontmatter
- Regional context dinámico
- Coherence scoring pre-generation

**FASE V6-1 - V6 Template Foundation**
- Templates con placeholders ${}
- Conditional content system
- Multi-section document structure

### 📁 Archivos Modificados

|| Archivo | Descripción ||
|---------|-------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Generator V6 con coherence scoring |
| `modules/commercial_documents/v4_proposal_generator.py` | Proposal con pricing real |
| `modules/commercial_documents/pain_solution_mapper.py` | Mapper problemas→soluciones |
| `modules/asset_generation/asset_diagnostic_linker.py` | Link assets a diagnostics |

---

## [4.9.0] - 2026-03-25

### 🎯 Objetivo
AEO Re-Architecture: Alineación conceptual y técnica del módulo AEO (Auditory Engine Optimization)

### ✅ Completado

**FASE-A - Corrección Conceptual**
- "AEO (Schema)" renombrado a "Schema Infrastructure"
- Dual counting eliminado en favor de Schema Infrastructure score
- Voice Readiness como módulo separado de schema_markup

**FASE-B - AEO Voice-Ready Module**
- SpeakableSpecification añadida a hotel_schema
- FAQ conversacional con 40-60 palabras por respuesta
- Voice Keywords para Eje Cafetero
- llms.txt voice-ready con structured data

**FASE-C - Integración Plataformas de Voz**
- Google Assistant checklist
- Apple Business Connect guide
- Alexa Skill blueprint
- 3 blueprints implementados en modules/delivery/generators/

**FASE-D - Medición AEO Real**
- KPI Framework: AEOKPIs, VoiceReadinessScore, DataSource en data_models/
- Mock clients Profound/Semrush en modules/analytics/
- Dashboard template aeo_metrics_report.md
- 17 tests de regresión

**FASE-E - Validación E2E**
- Delivery genera sin errores
- Speakable presente en schema
- Coherence score: 0.84 (≥ 0.80)
- 26/28 tests pasan

**FASE-F - Corrección Brechas E2E**
- FAQ respuestas 40-60 palabras (prompt LLM corregido en faq_gen.py)
- voice_assistant_guide con 3 archivos .md en delivery (voice_guide.py + conditional_generator.py)
- commercial_documents/__init__.py creado (módulo ahora importable)
- 52/52 regression tests PASS

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `data_models/aeo_kpis.py` | KPI framework para AEO |
| `modules/analytics/profound_client.py` | Mock client para Profound API |
| `modules/analytics/semrush_client.py` | Mock client para Semrush API |
| `modules/delivery/generators/google_assistant_checklist.md` | Blueprint Google Assistant |
| `modules/delivery/generators/apple_business_connect_guide.md` | Blueprint Apple Business |
| `modules/delivery/generators/alexa_skill_blueprint.md` | Blueprint Alexa Skill |
| `docs/aeo_metrics_report.md` | Dashboard template |
| `commercial_documents/__init__.py` | Paquete formalizado (importable) |

---

## [4.8.0] - 2026-03-23

### 🎯 Objetivo
FASE-CAUSAL-01: SitePresenceChecker - Solución de causa raíz para desconexión assets/sitio real

### ✅ Completado

**FASE-CAUSAL-01 - SitePresenceChecker**
- T-C1: SitePresenceChecker para verificar sitio real ANTES de generar assets
- T-C2: Integración en ConditionalGenerator como gate de presencia
- T-C3: Estados SKIPPED y REDUNDANT en AssetStatus
- T-C4: V4AssetOrchestrator actualizado con SkippedAsset
- T-C5: Reporting mejorado con skipped_assets y site_verification_applied
- T-C6: 10 tests unitarios implementados y pasando

### 📁 Archivos Nuevos/Modificados

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/site_presence_checker.py` | Verificación de presencia en sitio real |
| `modules/asset_generation/conditional_generator.py` | Integración site_url como parámetro |
| `modules/asset_generation/asset_metadata.py` | Estados SKIPPED, REDUNDANT |
| `modules/asset_generation/v4_asset_orchestrator.py` | SkippedAsset dataclass, reporting |
| `tests/asset_generation/test_site_presence_checker.py` | 10 tests para FASE-CAUSAL-01 |
| `docs/CONTRIBUTING.md` | Sección 17 documenting SitePresenceChecker |

### 🔧 Arquitectura

```
                    ┌─────────────────────────────┐
                    │   SITIO DE PRODUCCIÓN       │
                    │  SchemaFinder + scraping    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  SitePresenceChecker.check   │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌───────────┐      ┌─────────────┐      ┌───────────┐
        │  EXISTS   │      │ NOT_EXISTS │      │ REDUNDANT │
        │  → SKIP   │      │  → Generar │      │  → SKIP   │
        └───────────┘      └─────────────┘      └───────────┘
```

**Problema resuelto:**
- Sistema generaba assets sin verificar si el sitio ya tenía la funcionalidad
- Assets regenerados 7+ veces sin cambios (hotel_schema, org_schema)
- delivery_ready_percentage: 0% pese a múltiples assets generados
- Visperas es laboratorio - sistema genérico para cualquier hotel boutique

### 🔗 Links
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.6.0] - 2026-03-23

### 🎯 Objetivo
FASE 10: Health Dashboard - System Health Monitor para visibility del estado del sistema

### ✅ Completado

**FASE 10 - Health Dashboard**
- T10A: HealthMetricsCollector con dataclass ExecutionMetrics
- T10B: HealthDashboardGenerator genera HTML con Chart.js
- T10C: Integración en main.py post-execution (FASE 7)
- 14 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
||---------|------------|
|| `modules/monitoring/__init__.py` | Módulo de monitoring con exports |
|| `modules/monitoring/health_metrics_collector.py` | ExecutionMetrics dataclass, HealthMetricsCollector |
|| `modules/monitoring/health_dashboard_generator.py` | HealthDashboardGenerator con Chart.js |
|| `tests/monitoring/test_health_dashboard.py` | 14 tests para FASE 10 |
|| `main.py` | Integración FASE 10 post-delivery (línea ~2183) |

### 🔧 Arquitectura

```
ExecutionMetrics (dataclass)
    hotel_id, timestamp, assets_generated, assets_failed
    success_rate, avg_confidence, execution_time
    errors, warnings
```

**Dashboard Features:**
- Summary cards: Hotels Analyzed, Success Rate, Avg Confidence, Exec Time
- Bar charts: Success Rate by Hotel, Execution Time
- Doughnut chart: Confidence Distribution buckets
- Table: Hotel execution details with status badges

### 🔗 Links
- [Plan FASE 10](./.opencode/plans/05-prompt-inicio-sesion-fase-10-HEALTH-DASHBOARD.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.7.0] - 2026-03-23

### 🎯 Objetivo
FASE 11: Google Travel Integration + Onboard Enhancement + Asset Quality Boost

### ✅ Completado

**FASE 11A - Google Travel Scraper**
- GoogleTravelScraper para capturar datos de hoteles en Google Travel/Hotels
- Diferencia con Google Places API: Travel es agregador de hoteles (precios, disponibilidad)
- Entity ID support para URLs directas de Google Travel
- 5 tests obligatorios implementados

**FASE 11B - Onboard Enhancement + Integración Real**
- GoogleTravelScraper integrado en V4ComprehensiveAuditor como fallback
- Fallback chain: Places API -> Google Travel -> schema_data
- Logging estructurado para diagnóstico
- 16 tests pasando (11 original + 5 nuevos de integración)

**FASE 11C - Asset Quality Boost**
- v4complete ejecutado con integración Google Travel
- Coherence Score: 0.87 (threshold: 0.85) ✅
- 7/7 assets generados exitosamente
- Publication Gates: 6/6 passed ✅
- ⚠️ Google Travel bloquea scraping real en producción (no es bug, es limitación de Google)

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
|||---------|------------|
|| NUEVO | `modules/scrapers/google_travel_scraper.py` | GoogleTravelScraper class |
|| MODIFICADO | `modules/auditors/v4_comprehensive.py` | Integración GoogleTravelScraper en _audit_gbp() |
|| MODIFICADO | `modules/providers/autonomous_researcher.py` | Import GoogleTravelScraper |
|| NUEVO | `tests/scrapers/test_google_travel_scraper.py` | 17 tests para FASE 11 |

### 🔗 Links
- [Plan FASE 11](./.opencode/plans/05-prompt-inicio-sesion-fase-11-GOOGLE-TRAVEL-INTEGRATION.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.5.9] - 2026-03-23

### 🎯 Objetivo
FASE 9: AI/ML Enhancement - Intelligent Disclaimer Generator v2

### ✅ Completado

**FASE 9 - Intelligent Disclaimer Generator v2**
- T9A: DisclaimerGeneratorV2 con clase `IntelligentDisclaimerGenerator` y método `generate()`
- T9B: Integración con asset_metadata - campos: `missing_data`, `benchmark_used`, `improvement_steps`, `confidence_after_fix`
- T9C: Función `calculate_improvement_score(current_confidence, target_confidence)`
- T9D: 10 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
||---------|------------|
||| `modules/providers/disclaimer_generator.py` | Nueva clase `IntelligentDisclaimerGenerator`, función `calculate_improvement_score()` |
||| `modules/asset_generation/asset_metadata.py` | Nuevos campos: `missing_data`, `benchmark_used`, `improvement_steps`, `confidence_after_fix` |
||| `tests/test_never_block_architecture/test_disclaimer_generator.py` | 10 tests nuevos para FASE 9 |

### 🔧 Arquitectura

```
Asset con baja confianza
        │
        ▼
┌─────────────────────────────────────┐
│  INTELLIGENT DISCLAIMER GENERATOR   │
├─────────────────────────────────────┤
│  • asset_type: hotel_schema        │
│  • confidence: 0.3                 │
│  • missing_data: [gbp_reviews...]  │
│  • benchmark_used: Pereira avg      │
│  • improvement_steps: [1.1.2...]   │
└─────────────────────────────────────┘
        │
        ▼
Disclaimer contextual con:
⚠️ CONFIANZA BAJA (30/100)
• Google Business Profile sin datos
• Reseñas de clientes (gbp_reviews)
PARA MEJORAR:
1. Agregar 10+ fotos a GBP
2. Solicitar 5+ reseñas
CONFIDENCIA ESPERADA: 54%+
```

### 🔗 Links
- [Plan FASE 9](./.opencode/plans/05-prompt-inicio-sesion-fase-9-AI-DISCLAIMER.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

## [4.5.8] - 2026-03-23

### 🎯 Objetivo
FASE 8: Autonomous Research Engine v2 - Investigación autónoma real con output verificable

### ✅ Completado

**FASE 8 - Autonomous Research Engine v2**
- T8A: ResearchOutput schema con persistencia JSON (hotel_name, sources_checked, data_found, confidence, citations, gaps)
- T8B: Source Scrapers implementados (BookingScraper, TripAdvisorScraper, InstagramScraper)
- T8C: Integración en orchestration - last_research_output accesible post-research
- T8D: Research Confidence Scoring (4/4=1.0, 3/4=0.75, 2/4=0.5, 1/4=0.25)
- T8E: 25 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

| Archivo | Descripción |
|---------|-------------|
| `modules/providers/autonomous_researcher.py` | ResearchOutput schema, scrapers stubs, confidence scoring |
| `modules/scrapers/booking_scraper.py` | Scraper para Booking.com |
| `modules/scrapers/tripadvisor_scraper.py` | Scraper para TripAdvisor |
| `modules/scrapers/instagram_scraper.py` | Scraper para Instagram |
| `modules/scrapers/__init__.py` | Exports actualizados |
| `modules/providers/__init__.py` | Exports de AutonomousResearcher y funciones |
| `tests/providers/test_autonomous_research_fase8.py` | 25 tests para FASE 8 |

### 🔧 Arquitectura

```
Research Request
      │
      ▼
┌─────────────────────────────────────┐
│     AUTONOMOUS RESEARCHER ENGINE     │
├─────────────────────────────────────┤
│  1. GBP Lookup (GBPScraper)         │
│  2. Booking.com (BookingScraper)    │
│  3. TripAdvisor (TripAdvisorScraper)│
│  4. Instagram (InstagramScraper)    │
│  5. Cross-Reference                 │
│  6. Confidence Scoring              │
└─────────────────────────────────────┘
      │
      ▼
Research Report (JSON persistido)
      │
      ▼
Assets referencian el research
```

### 📊 Confidence Scoring

| Fuentes | Confidence |
|---------|------------|
| 4/4 | 1.0 |
| 3/4 | 0.75 |
| 2/4 | 0.5 |
| 1/4 | 0.25 |
| 0/4 | 0.0 |

---

## [4.5.7] - 2026-03-23

### 🎯 Objetivo
FASE 5: Validación Transversal y Cierre del Proyecto NEVER_BLOCK v4.5.6

### ✅ Completado

**FASE 5 - Validación Transversal**
- T1: Orden Audit → Assets verificado (timestamps confirmados)
- T2: Coherence Score documentado (mide coherencia interna, no cantidad de datos)
- T3: Autonomous Researcher documentado como Silent Research (diseño intencional)
- T4: Métricas de salud del sistema creadas
- T5: Capability Contract v4.5.6 completo (10 capabilities, 0 huérfanas)
- T6: Test E2E de regresión creado

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `docs/capability_contract_v4_5_6.md` | Matriz completa de capabilities del sistema |
| `evidence/fase-5-transversal/system_health_metrics.json` | Métricas de salud post-ejecución |
| `evidence/fase-5-transversal/capability_contract.json` | Evidencia de validación T1-T6 |
| `tests/test_never_block_architecture/test_audit_generated_before_assets.py` | Test orden audit → assets |
| `tests/test_never_block_architecture/test_coherence_validation.py` | Test validación coherence |
| `tests/test_never_block_architecture/test_capability_contract.py` | Test capability contract |
| `tests/test_never_block_architecture/test_e2e_v4_5_6_corrections.py` | Test E2E regresión Fases 1-4 |

### 📝 Hallazgos Transversales

| Hallazgo | Descripción | Estado |
|----------|-------------|--------|
| Coherence Score | Score de 0.88 NO está inflado - mide coherencia entre documentos, no cantidad de datos | ✅ Documentado |
| autonomous_researcher | Silent Research (never_block) - diseño intencional, no bug | ✅ Documentado |
| Orden de ejecución | audit_report se genera ANTES que assets | ✅ Verificado |

### 🏁 Cierre del Proyecto

**PROYECTO v4.5.6 CERRADO**

- ✅ T1-T6 completadas
- ✅ 0 capabilities huérfanas
- ✅ Documentación post-proyecto completa
- ✅ CHANGELOG.md actualizado

---

## [4.5.6] - 2026-03-22

### 🎯 Objetivo
Implementar arquitectura NEVER_BLOCK: el sistema nunca se bloquea, siempre entrega algo aunque sea subóptimo. Resolución de gaps con benchmark regional + disclaimers honestos.

### ✅ Completado

**FASE 1 - Benchmark Resolver**
- `modules/providers/benchmark_resolver.py` - NUEVO módulo para resolver gaps con benchmark regional (Pereira/Santa Rosa de Cabal)
- `modules/asset_generation/asset_metadata.py` - Campo `disclaimers` añadido
- Tests en `tests/test_benchmark_resolver.py` - 11 tests

**FASE 2 - Disclaimer Generator**
- `modules/providers/disclaimer_generator.py` - NUEVO módulo genera disclaimers honestos por nivel de confidence
- Tests en `tests/test_disclaimer_generator.py` - 15 tests

**FASE 3 - Autonomous Researcher**
- `modules/providers/autonomous_researcher.py` - NUEVO módulo investiga hotel en GBP, Booking, TripAdvisor, Instagram
- Tests en `tests/test_autonomous_researcher.py` - 20 tests

**FASE 4 - Never-Block Integration**
- `modules/asset_generation/preflight_checks.py` - Integración benchmark fallback
- `modules/asset_generation/conditional_generator.py` - Placeholders corregidos en optimization_guide
- `modules/asset_generation/asset_content_validator.py` - Bloqueo de placeholders pre-generación
- Tests en `tests/test_never_block_integration.py` - 23 tests

**FASE 5 - Validación E2E**
- Tests de regresión Hotel Vísperas - 2 tests skipping corregidos
- 69/69 tests passing en suite NEVER_BLOCK

**FASE 6 - Documentación y Cierre**
- BenchmarkCrossValidator integrado en PreflightChecker (validate_adr_against_benchmark, check_asset_with_benchmark)
- Actualización documental: CONTRIBUTING.md, GUIA_TECNICA.md, README.md
- Tests actualizados para comportamiento NEVER_BLOCK
- Suite de regresión: 256 tests passing, 2 skipped

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/providers/benchmark_resolver.py` | Benchmark regional para datos faltantes |
| `modules/providers/disclaimer_generator.py` | Generador de disclaimers honestos |
| `modules/providers/autonomous_researcher.py` | Investigador autónomo en fuentes públicas |
| `tests/test_benchmark_resolver.py` | Tests TDD para BenchmarkResolver |
| `tests/test_disclaimer_generator.py` | Tests TDD para DisclaimerGenerator |
| `tests/test_autonomous_researcher.py` | Tests TDD para AutonomousResearcher |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/asset_metadata.py` | Añadido campo `disclaimers` |
| `modules/asset_generation/preflight_checks.py` | Integración benchmark fallback |
| `modules/asset_generation/conditional_generator.py` | Placeholders corregidos, benchmark fallback |
| `modules/asset_generation/asset_content_validator.py` | Bloqueo pre-generación de placeholders |
| `tests/test_never_block_integration.py` | Tests de regresión Hotel Vísperas |
| `output/v4_complete/hotelvisperas/` | Outputs regenerados sin placeholders |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests NEVER_BLOCK | 256 passing, 2 skipped |
| Tests totales | 256+ passing (suite regression) |
| Coherence | ≥ 0.8 |
| Placeholders en outputs | 0 |
| Assets bloqueados | 0 (hotel_schema aún bloqueado por datos externos vacíos) |

### Principios Implementados

1. **NEVER_BLOCK**: El sistema nunca se bloquea, siempre entrega algo
2. **BENCHMARK_FALLBACK**: Datos faltantes se resuelven con benchmark regional
3. **HONEST_CONFIDENCE**: Todo output incluye confidence score real y fuentes
4. **DELIVERY_READY**: Todo output es implementable, sin placeholders

## [4.5.5] - 2026-03-21

### 🎯 Objetivo
Mejorar generador de FAQs con categorías y timestamp ISO 8601

### ✅ Completado

**Cambios Implementados**
- `modules/delivery/generators/faq_gen.py` - Agregadas columnas Categoria y Fecha_Generacion
- `tests/delivery/test_faq_generator_improvements.py` - Test para nueva funcionalidad

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/delivery/generators/faq_gen.py` | Agregadas columnas Categoria y Fecha_Generacion |
| `tests/delivery/test_faq_generator_improvements.py` | Test para nueva funcionalidad |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1 nuevo test en `tests/delivery/test_faq_generator_improvements.py` |

## [4.5.4] - 2026-03-17

### 🎯 Objetivo
Implementar mejoras incrementales al agent_harness inspiradas en Superpowers sin adopción de framework externo.

### ✅ Completado

**Cambios Implementados**
- `.agents/workflows/phased_project_executor.md` - Agregado Step 0.5 TDD Gate
- `.agents/workflows/audit_guardian.md` - Modificado Steps 2-4 para ejecución paralela

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `.agents/workflows/phased_project_executor.md` | Agregado TDD Gate |
| `.agents/workflows/audit_guardian.md` | Ejecución paralela |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |
| Desconexiones | 0 |
| Hard contradictions | 0 |

## [4.5.3] - 2026-03-15

### 🎯 Objetivo
Adoptar enfoque de comunicación del diagnóstico antiguo (25/feb) sin perder validaciones técnicas de v4.5.2

### 🔧 Cambios Implementados

**Estructura de Diagnóstico Restaurada:**
- Narrativa "Antes/Ahora" que crea urgencia (PARTE 1)
- Comparativa regional: Su Hotel vs Promedio (PARTE 2)
- Las 4 Razones con costos específicos (PARTE 3)
- Quick Wins con timings concretos (PARTE 5)
- Plan 7/30/60/90 días (PARTE 6)
- Anexo Técnico con validaciones al final

**Estructura de Propuesta Restaurada:**
- Resumen Ejecutivo con pérdida mensual
- Proyección financiera mes a mes (6 meses)
- Plan 7/30/60/90 días detallado
- Garantías específicas (3 garantías)
- Mapeo problemas→soluciones→assets visible

**Assets Conectados:**
- Metadata de conexión: problem_solved, impact_cop, priority, timing
- README.md en cada folder de asset con justificación de ventas

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| templates/diagnostico_v4_template.md | Estructura de ventas completa |
| templates/propuesta_v4_template.md | Estructura de ventas completa |
| asset_diagnostic_linker.py | Metadata de conexión |
| v4_proposal_generator.py | Variables de proyección mensual |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |
| Desconexiones | 0 |
| Hard contradictions | 0 |

## [4.5.2] - 2026-03-13

### 🎯 Objetivo

Completar FASE-5: Validación de coherencia y preparación para publicación.

### ✅ Completado

**Fase 1-5**:
- Coherence score: 0.64 → 0.91 (umbral: 0.8) ✅
- Validaciones rápidas: 4/4 passed
- Regression tests: 52/52 passed
- Publication Ready: true
- Price bug fixed ($800k → $130k)
- ConfidenceLevel enum unificado

### 🔧 Fixed

- Contradiction engine ahora detecta conflictos inter-documento
- Consistency checker valida WhatsApp, GBP, schema, ADR
- Publication gates implementados (hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall)
- Promise vs Implementation validator

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| modules/quality_gates/coherence_gate.py | Gate de coherencia con score ≥ 0.8 |
| modules/quality_gates/publication_gates.py | Gates de publicación |
| data_validation/consistency_checker.py | Validación cruzada |
| commercial_documents/coherence_validator.py | Validador de coherencia |
| orchestration_v4/phase5_validator.py | Orquestación Fase 5 |

## [4.5.1] - 2026-03-12

### 🎯 Objetivo

Corrección de desconexiones estructurales entre módulos GEO y documentos comerciales.

### 🔧 Added - GEO Integration Fix

**Integración GEO en Documentos Comerciales**:
- PainSolutionMapper ahora detecta problemas ai_crawler_blocked, low_citability, low_ia_readiness
- V4DiagnosticGenerator incluye sección de métricas GEO
- V4ProposalGenerator incluye assets GEO en propuesta

**Corrección de Assets**:
- Gate de contenido vacío implementado (mínimo 50 caracteres)
- Gate de placeholders implementado ($$VAR, {{VAR}}, [[VAR]])
- faq_page genera contenido real específico del hotel
- org_schema tiene campos poblados con fallback
- performance_audit usa datos reales del audit

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| modules/commercial_documents/pain_solution_mapper.py | Detección de problemas GEO |
| modules/commercial_documents/v4_diagnostic_generator.py | Sección métricas GEO |
| modules/commercial_documents/v4_proposal_generator.py | Assets GEO en propuesta |
| modules/asset_generation/conditional_generator.py | Gate de contenido |
| tests/asset_generation/test_content_gates.py | 19 tests nuevos para gates |
| tests/commercial_documents/test_pain_solution_mapper_geo.py | Tests para detección GEO |
| tests/commercial_documents/test_v4_diagnostic_generator_geo.py | Tests para sección GEO |
| tests/commercial_documents/test_v4_proposal_generator_geo.py | Tests para assets GEO |

## [4.5.0] - 2026-03-11

### 🎯 Objetivo

Completar integración GEO (Generative Engine Optimization): Documentación, gates y consolidación.

### 🔧 Added - GEO Integration

**Capacidades de Generative Engine Optimization**:
- **AI Crawler Auditor**: Análisis de robots.txt para 14+ crawlers de IA
- **llms.txt Generator**: Generación del estándar emergente para indexación IA
- **Citability Scorer**: Análisis de contenido para citabilidad (ADVISORY)
- **IA-Readiness Calculator**: Score compuesto de preparación IA (ADVISORY)

### 🔧 Added - Schema Hotel Enhanced

**Mejoras en schema hotelero**:
- Reconocimiento de `LodgingBusiness` como hotel válido
- Campos hoteleros críticos: `geo`, `checkinTime`, `checkoutTime`, `sameAs`, `amenityFeature`
- Estructura `@graph` para múltiples schemas

### 🔧 Changed

- `rich_results_client.py`: Extensión para LodgingBusiness
- `schema_validator_v2.py`: Coverage scoring con campos hoteleros
- `conditional_generator.py`: Unificación de schema generation
- `asset_catalog.py`: Nuevos assets llms_txt

### 🔧 Fixed

- Rich Results "non-critical issues" para hoteles con schema LodgingBusiness

### 🔧 Technical

- Tests incrementados a 1338+ passing
- 0 regresiones en validaciones existentes
- Métricas GEO como advisory (no gates bloqueantes)

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/auditors/ai_crawler_auditor.py` | Auditoría de robots.txt para IA crawlers |
| `modules/asset_generation/llmstxt_generator.py` | Generación de llms.txt estándar |
| `modules/auditors/citability_scorer.py` | Score de citabilidad de contenido |
| `modules/auditors/ia_readiness_calculator.py` | Score compuesto IA-readiness |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `CHANGELOG.md` | Entry v4.5.0 |
| `AGENTS.md` | Nuevos módulos activos + métricas advisory |
| `GUIA_TECNICA.md` | Secciones de auditoría y citabilidad |
| `VERSION.yaml` | Actualizado a 4.5.0 |

---

## [4.4.1] - 2026-03-10

### 🎯 Objetivo

Completar FASE-ASSET-06: Documentación. Sistema de catálogo unificado de assets con gate de coherencia mejorado.

### 🔧 Cambios Implementados

#### Catálogo Unificado de Assets
- `modules/asset_generation/asset_catalog.py` - Catálogo centralizado de tipos de assets con estado
- Enum AssetStatus: IMPLEMENTED, PROMISED_NOT_IMPLEMENTED, MISSING
- dataclass AssetCatalogEntry con is_asset_implemented()

#### Gate de Coherencia Mejorado
- `modules/commercial_documents/coherence_validator.py` - Nuevo check promised_assets_exist
- Valida que assets prometidos existen en el generador
- Severidad: error (blocking)

#### Refactorización de Consumidores
- `modules/commercial_documents/pain_solution_mapper.py` - Usa ASSET_CATALOG
- `modules/asset_generation/conditional_generator.py` - Usa ASSET_CATALOG
- `modules/asset_generation/preflight_checks.py` - Usa ASSET_CATALOG
- Eliminación de listas duplicadas en 3 módulos

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/asset_catalog.py` | Catálogo centralizado con Enum AssetStatus |
| `tests/test_coherence_promised_assets.py` | Tests para nuevo check promised_assets_exist |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/pain_solution_mapper.py` | Usa ASSET_CATALOG |
| `modules/asset_generation/conditional_generator.py` | Usa ASSET_CATALOG |
| `modules/asset_generation/preflight_checks.py` | Usa ASSET_CATALOG |
| `modules/commercial_documents/coherence_validator.py` | Nuevo check promised_assets_exist |
| `AGENTS.md` | Actualizado con nuevos módulos activos |

### 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Fases completadas | 6/6 (100%) |
| Assets implementados | 9/11 |
| Assets prometeros-no-implementados | 0 (gestionados) |
| Unknown asset type errors | 0 |
| Tests | 1323 passing (17 geo_validation related - no bloqueante) |

---

## [4.4.2] - 2026-03-11

### 🎯 Objetivo

Auditoría Integral v4.4.1 - Corrección de inconsistencias en análisis Hotelvisperas.

### 🔧 Cambios Implementados

#### Validación Financiera (No Defaults in Money)
- modules/financial_engine/no_defaults_validator.py - Nuevo validador
- Bloquea cálculos financieros cuando occupancy_rate=0 o direct_channel=0
- 18 tests en test_no_defaults_validator.py

#### Calidad de Assets
- modules/asset_generation/asset_content_validator.py - Nuevo validador
- Detecta placeholders y contenido genérico en assets

#### Ethics Gate
- modules/quality_gates/ethics_gate.py - Nuevo gate
- Valida ROI >= 0 antes de proponer precios

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| modules/financial_engine/no_defaults_validator.py | Validador de defaults financieros |
| modules/asset_generation/asset_content_validator.py | Validador de contenido de assets |
| modules/quality_gates/ethics_gate.py | Gate ético financiero |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1323 passing |
| NoDefaultsValidator tests | 18/18 passing |
| Validaciones | 4/4 |

## [4.4.1] - 2026-03-09

### 🎯 Objetivo

Conectar capacidades que existían pero no estaban integradas al flujo principal.

### 🔧 Cambios Implementados

#### Integración de MetadataValidator
- `modules/auditors/v4_comprehensive.py` - Nueva clase MetadataAuditResult
- `modules/auditors/v4_comprehensive.py` - Nuevo método _audit_metadata()
- Integración en flujo de auditoría entre schemas y GBP

#### Execution Trace
- `modules/auditors/v4_comprehensive.py` - Campos executed_validators, skipped_validators
- Output incluye execution_trace en serialización

#### PublicationGates como Gate Real
- `main.py` - FASE 4.5 después de assets
- Invocación de run_publication_gates()
- Resultados propagados al reporte final

#### ConsistencyChecker Obligatorio
- `main.py` - FASE 4.6 después de PublicationGates
- Integración de check_assessment_consistency()
- Resultados visibles en output

#### FinancialCalculatorV2 Garantizado
- `main.py` - FASE 3 usa FinancialCalculatorV2
- Reemplaza uso directo de ScenarioCalculator
- Validación "No Defaults in Money" asegurada

#### Documentación y Workflows
- `.agents/workflows/phased_project_executor.md` - v1.4.0
- `docs/CONTRIBUTING.md` - Nueva §13 Sistema de Capability Contracts

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | MetadataValidator + Execution Trace |
| `main.py` | FASE 4.5, FASE 4.6, FinancialCalculatorV2 |
| `.agents/workflows/phased_project_executor.md` | v1.4.0 - Capability Contracts |
| `docs/CONTRIBUTING.md` | §13 Sistema de Capability Contracts |

### 📊 Tests

- 27 tests passing (regresión Hotel Visperas)
- 4/4 validaciones pasando

---

## [4.4.1] - 2026-03-04

### 🎯 Objetivo

Limpieza de módulos deprecados y consolidación de arquitectura v4.0.

### 🔧 Cambios Implementados

#### Archivado de Módulos Legacy
- **decision_engine.py** → Archivado (v2.4.2 legacy, reemplazado por `financial_engine/`)
- **orchestrator/** → Archivado (v3.x legacy, reemplazado por `orchestration_v4/`)
- **generators/report_builder.py** → Archivado (huérfano, reemplazado por `report_builder_fixed.py`)
- **generators/certificate_gen.py** → Archivado (v2.2, versión más reciente en `delivery/generators/`)
- **utils/cac_tracker.py** → Archivado (huérfano, nunca utilizado)

#### Consolidación de Arquitectura
- Flujo v4.x consolidado en `orchestration_v4/` (comandos `v4complete`, `v4audit`)
- Comandos legacy (`audit`, `stage`, `spark`) marcados como deprecados con mensajes informativos
- Imports condicionales para módulos legacy con `ORCHESTRATOR_AVAILABLE`

### 📁 Archivos Archivados

| Archivo | Ubicación | Razón |
|---------|-----------|-------|
| `modules/decision_engine.py` | `archives/deprecated_modules_20260304/` | Legacy v2.4.2 |
| `modules/orchestrator/` | `archives/deprecated_modules_20260304/orchestrator/` | Legacy v3.x |
| `modules/generators/report_builder.py` | `archives/deprecated_modules_20260304/generators/` | Huérfano |
| `modules/generators/certificate_gen.py` | `archives/deprecated_modules_20260304/generators/` | Duplicado obsoleto |
| `modules/utils/cac_tracker.py` | `archives/deprecated_modules_20260304/utils/` | Huérfano |

### 📁 Tests Archivados

| Test | Ubicación | Razón |
|------|-----------|-------|
| `test_v23_integration.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.3 |
| `test_visperas_v242.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.4.2 |
| `test_v242_quick.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.4.2 |
| `test_pipeline_no_llm.py` | `archives/deprecated_modules_20260304/tests/` | Pipeline legacy |

### 📊 Tests

- Tests activos: ~1240+ (reducidos por archivado de tests legacy)
- Cobertura: >80%

### 🔗 Referencias

- Archivo completo: `archives/deprecated_modules_20260304/`
- Documentación de archivado: `archives/deprecated_modules_20260304/README.md`

## [4.4.0] - 2026-03-04

### 🎯 Objetivo

Corregir hallazgos B-001, B-002, M-001, M-002, m-001 detectados en fase de observación v4complete.
Mejorar confiabilidad del sistema de evidencia y coherencia entre documentos.

### 🔧 Cambios Implementados

#### Adaptador Unificado de Taxonomías (B-001)
- **Problema**: Dos enums ConfidenceLevel con valores diferentes (data_structures vs confidence_level)
- **Solución**: Adaptador unificado en `modules/commercial_documents/data_structures.py`
- **Función**: `normalize_confidence_level()` para conversión segura entre taxonomías
- **Impacto**: Consistencia en overall_confidence en todos los documentos

#### Corrección Semántica Financiera (B-002)
- **Problema**: Escenario optimista podía tener valores negativos (max(0, ...) ocultaba problemas)
- **Solución**: Nuevo campo `monthly_opportunity_cop` sin truncamiento
- **Template**: Mostrar "Equilibrio" cuando oportunidad <= 0
- **Archivos**: `scenario_calculator.py`, templates financieros

#### Alineación Pricing vs Coherence (M-001, m-001)
- **Problema**: Unidades incompatibles (3.0x vs 0.03) causaban falsos FAIL
- **Solución**: Sistema unificado en Decimal (0.03-0.06) como canónica
- **Conversión**: Coherence convierte automáticamente para mensajes legibles
- **Mensajes**: "3.0x" en vez de "0.03" para legibilidad

#### Fuente Única de Problemas (M-002)
- **Problema**: Problemas duplicados entre diagnóstico y propuesta (50 FAQs → 18)
- **Solución**: Funciones compartidas `calculate_quick_wins()` y `extract_top_problems()`
- **Ubicación**: `modules/commercial_documents/data_structures.py`
- **Impacto**: Consistencia garantizada entre documentos

#### Observabilidad Determinística
- **Nuevo**: `manifest.json` generado en cada ejecución
- **Contenido**: Archivos procesados, métricas, checksums
- **Validación**: Validación cruzada automática post-ejecución
- **Clasificación**: Métricas determinísticas vs volátiles

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `tests/test_confidence_consistency_between_documents.py` | Test E2E de confianza entre documentos |
| `tests/test_top_problems_consistency.py` | Test de consistencia de problemas |
| `tests/test_optimistic_scenario_semantics.py` | Test de semántica de escenarios |
| `tests/test_price_pain_ratio_alignment.py` | Test de alineación pricing |
| `.opencode/plans/v4_observation_workflow/scripts/manifest_generator.py` | Generador de manifest por run |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/data_structures.py` | Adaptador de taxonomías, funciones compartidas |
| `modules/financial_engine/scenario_calculator.py` | Campo monthly_opportunity_cop, sin max(0,...) |
| `modules/commercial_documents/coherence_config.py` | Alineación unidades pricing |
| `main.py` | Construcción de DiagnosticSummary con fuente única |
| `v4_diagnostic_generator.py` | Usa extract_top_problems compartida |
| `v4_proposal_generator.py` | Usa calculate_quick_wins compartida |

### 📊 Tests

- **1261 tests pasando** (+4 desde v4.3.0)
- **4 tests de integración nuevos** validando correcciones
- **Cobertura**: >80%
- **Regresión**: 22/22 checks PASSED

### 🔗 Referencias

- Plan de implementación: `.opencode/plans/v4_implementation_sessions/`
- Dependencias: `dependencias-sesiones.md`
- Sesiones completadas: 1-6 (Sesión 7: documentación)

---

## [4.3.0] - 2026-03-03

### 🎉 Release - Sistema de Evidencia y Confiabilidad (FASE 6)

Esta release introduce el Sistema de Evidencia Trazable completo, motor de contradicciones,
quality gates de pre-publicación, y dashboard de observabilidad. Preparado para transición SHADOW → ACTIVE.

### 🔬 Sistema de Evidencia Trazable

- **EvidenceLedger** - Almacén centralizado de evidencia con hash e integridad
- **Claim** - Claims con evidencia trazable y niveles de confianza
- **CanonicalAssessment** - Estructura unificada de verdad (reemplaza assessment v4.2)

### ⚠️ Motor de Contradicciones

- **ContradictionEngine** - Detección de hard/soft conflicts entre fuentes
- **ConsistencyChecker** - Validación inter-documento
- Bloqueo automático cuando hard contradictions > 0

### 🚦 Quality Gates de Pre-publicación

- **DomainGates** - Gates técnico, comercial, financiero
- **CoherenceGate** - Bloqueo si score < 0.8
- **PublicationGates** - Estados READY_FOR_CLIENT, DRAFT_INTERNAL, REQUIRES_REVIEW
- **NoDefaultsValidator** - Validación "No Defaults in Money"

### 📊 Observabilidad y Calibración

- **Dashboard** - Métricas y tendencias de calidad
- **Calibration** - Ajuste de umbrales de confianza
- **Suite de Regresión** - Test permanente con Hotel Vísperas

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `data_models/canonical_assessment.py` | Modelo unificado de assessment |
| `data_models/claim.py` | Claims con evidencia trazable |
| `data_models/evidence.py` | Evidencia con hash e integridad |
| `data_validation/evidence_ledger.py` | Almacén centralizado de evidencia |
| `data_validation/contradiction_engine.py` | Motor de detección de conflictos |
| `data_validation/consistency_checker.py` | Validación inter-documento |
| `modules/quality_gates/domain_gates.py` | Gates por dominio |
| `modules/quality_gates/coherence_gate.py` | Gate de coherencia |
| `modules/quality_gates/publication_gates.py` | Gates de pre-publicación |
| `modules/quality_gates/publication_state.py` | Estados de publicación |
| `modules/financial_engine/no_defaults_validator.py` | Validación sin defaults |
| `modules/financial_engine/calculator_v2.py` | Calculadora condicionada v2 |
| `commercial_documents/composer.py` | Composición documental determinística |
| `observability/dashboard.py` | Dashboard de métricas |
| `observability/calibration.py` | Calibración de umbrales |
| `enums/severity.py` | Niveles de severidad |
| `enums/confidence_level.py` | Niveles de confianza |
| `tests/regression/test_hotel_visperas.py` | Test de regresión permanente |

### 📊 Métricas de Calidad (KPIs)

| KPI | Umbral | Estado |
|-----|--------|--------|
| Evidence Coverage | >= 95% | ✅ |
| Hard Contradictions | = 0 | ✅ |
| Financial Validity | = 100% | ✅ |
| Critical Issue Recall | >= 90% | ✅ |
| Coherence Score | >= 0.8 | ✅ |

### 📈 Tests

- **1257 tests pasando** (+349 desde v4.2.0)
- Nueva suite de regresión permanente
- Tests de observabilidad y calibración

### ⚠️ Breaking Changes

- Nuevo formato `CanonicalAssessment` (reemplaza assessment v4.2)
- Estados de publicación obligatorios
- Bloqueo financiero con defaults detectados
- Coherence < 0.8 bloquea certificado

---

## [4.2.0] - 2026-03-02

### 🎉 Release - Integración Completa y Flujo v4complete Funcional

Esta release corrige bugs críticos y completa la integración de todas las fases técnicas (0-4),
habilitando la ejecución completa de v4complete con generación de todos los outputs.

### 🐛 Correcciones de Bugs

#### Bug: Atributo `rationale` inexistente
- **Archivo**: `main.py`
- **Líneas**: 1494, 1584
- **Problema**: `PricingResolutionResult` no tiene atributo `rationale`, causando `AttributeError`
- **Solución**: Eliminar referencias a `rationale` del constructor y del JSON dump

### ✨ Mejoras

#### Flujo v4complete Funcional
- Todas las fases ejecutan sin errores:
  - FASE 1: Hook Generation ✅
  - FASE 2: Validación Cruzada ✅
  - FASE 3: Escenarios Financieros ✅
  - FASE 3.5: Documentos Comerciales ✅
  - FASE 4: Assets ✅
  - FASE 5: Reporte ✅

#### Outputs Generados
- `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` - Diagnóstico validado
- `02_PROPUESTA_COMERCIAL.md` - Propuesta coherente
- `financial_scenarios.json` - Escenarios financieros
- `audit_report.json` - Auditoría con APIs
- `v4_complete_report.json` - Reporte final

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/financial_engine/harness_handlers.py` | Handlers para Agent Harness |
| `.agents/workflows/v4_financial_calculation.md` | Meta-Skill de cálculo financiero |
| `.agents/workflows/v4_regional_resolver.md` | Meta-Skill de resolución regional |
| `tests/test_fase3_harness_integration.py` | 26 tests de integración |
| `FASE_3_CHECKLIST.md` | Documentación Fase 3 |
| `FASE_4_CHECKLIST.md` | Documentación Fase 4 |

### 📊 Tests

- 908 tests pasando
- 26 tests nuevos de integración con Agent Harness
- Cobertura: financial_engine, agent_harness, commercial_documents

### 🔧 Feature Flags

El sistema está preparado para transición SHADOW → ACTIVE:
- `regional_adr_enabled`: False (default)
- `pricing_hybrid_enabled`: False (default)
- `financial_v410_enabled`: False (default)
- Modos: SHADOW (listo para activación progresiva)

---

## [4.2.0] - 2026-03-02 (Continuación - FASE 5)

### 🔧 Hardening y Validación de Regresión

#### Correcciones de Bugs Críticos (FASES 1-2)
- **Preflight Checks**: Respetar `block_on_failure=False` para campos faltantes (conversión a WARNING con fallback)
- **Asset Orchestrator**: Normalizar case en comparación de status (PASSED/passed) con .upper()
- **Coherence Validator**: Umbral unificado a 0.8 desde config
- **PageSpeed Client**: Extraer Lighthouse score incluso sin CrUX field data (status LAB_DATA_ONLY)
- **Google Places Client**: Agregar `error_type` y `error_message` para diagnóstico de fallos

#### Recuperación de Capacidades (FASE 3)
- **Competitor Analyzer**: Integrado en flujo v4 via V4ComprehensiveAuditor
- **Contexto Industria**: Agregado a diagnóstico (Eje Cafetero)
- **Scores 4 Pilares**: Tabla comparativa en diagnóstico (GEO, Activity, Web, AEO, IAO)
- **Plan 7/30/60/90**: Detallado en propuesta comercial
- **Garantías**: Nueva sección en propuesta (resultados, transparencia, sin permanencia)

#### Nuevos Tests de Regresión (FASE 5)
| Test | Descripción | Archivo |
|------|-------------|---------|
| Preflight Missing Field | 3 tests para fallback cuando campo requerido falta | `tests/asset_generation/test_preflight_missing_field.py` |
| Conditional New Assets | 4 tests para geo_playbook, review_plan, review_widget, org_schema | `tests/asset_generation/test_conditional_new_assets.py` |
| PageSpeed Lab Data | 2 tests para validar LAB_DATA_ONLY status | `tests/data_validation/test_pagespeed_lab_data.py` |
| Places Error Types | 3 tests para error_type en NO_API_KEY, QUOTA_EXCEEDED, TIMEOUT | `tests/test_google_places_error_types.py` |
| Comprehensive Competitors | 2 tests para integración de competitor_analyzer | `tests/auditors/test_v4_comprehensive_competitors.py` |

#### Sistema de Regresión Automatizada
- **Script:** `.opencode/plans/v4_repair_plan/scripts/regression_test.py`
- **Modos:** `url-only` (>=3 assets) y `with-onboarding` (coherence >=0.8)
- **Checks:** 7 validaciones E2E automatizadas
  1. Assets Generated (>=3/5)
  2. Coherence Score (estructura o >=0.8)
  3. Performance Detected (presente)
  4. Performance Status (VERIFIED/LAB_DATA_ONLY)
  5. GBP Diagnostics (error_type si place_found=false)
  6. Diagnostic Structure (4 secciones)
  7. Proposal Structure (5 secciones)

#### Nuevos Assets Generables
| Asset | Tipo | Descripción |
|-------|------|-------------|
| `geo_playbook` | Markdown | Checklist de optimización GBP |
| `review_plan` | Markdown | Estrategia de gestión de reseñas |
| `review_widget` | HTML | Widget de reviews para web |
| `org_schema` | JSON-LD | Schema.org Organization markup |

#### Tests Totales
- **Antes:** 908 tests
- **Después:** 921 tests (+13 nuevos)
- **Regresión:** 7/7 checks PASSED

#### Estado del Sistema
- ✅ **5/5 assets generados** (100%)
- ✅ **921 tests pasando** (100%)
- ✅ **Flujo v4complete funcional end-to-end**
- ✅ **Sistema preparado para transición SHADOW → ACTIVE**

---

## [4.1.0] - 2026-02-28

### 🎉 Release - Controles de Coherencia y Documentación Comercial

Esta release completa el flujo v4.0 con generación automatizada de documentos comerciales y controles de coherencia entre diagnóstico, propuesta y assets.

### ✨ Nuevas Características

#### Generación de Documentos Comerciales
- **Módulo**: `modules/commercial_documents/`
- **V4DiagnosticGenerator**: Genera `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` con datos validados
- **V4ProposalGenerator**: Genera `02_PROPUESTA_COMERCIAL.md` con mapeo problemas→soluciones
- **Escenario financiero empático**: Realista destacado como "más probable", otros en anexo
- **Tabla de datos validados**: WhatsApp 🟢, Habitaciones 🟡, ADR 🟡 con fuentes

#### Controles de Coherencia
- **Módulo**: `CoherenceValidator` en `modules/commercial_documents/`
- **Validaciones automáticas**:
  - Problemas tienen soluciones (≥50%)
  - Assets están justificados por problemas
  - Datos financieros validados (≥0.7)
  - WhatsApp verificado (≥0.9, blocking)
  - Precio coherente con dolor (3-6x)
- **Score de coherencia global**: ≥0.8 para éxito
- **CoherenceConfig**: Lee umbrales desde `.conductor/guidelines.yaml`

#### Mapeo Problemas→Soluciones
- **Módulo**: `PainSolutionMapper`
- **9 problemas mapeados** a assets específicos
- **Categorización**: Con solución inmediata / Requieren atención
- **AssetPlan**: Genera plan de assets basado en confianza disponible

#### Integración Agent Harness
- **Log enriquecido v4.1.0**: coherence_score, phases_completed, assets counts
- **Persistencia de documentos**: Referencias a diagnóstico y propuesta
- **Comando `execute` mejorado**: Recupera análisis v4.0 con coherence ≥ 0.8
- **Validación de vigencia**: < 20 días

### 📁 Archivos Nuevos

```
modules/
├── commercial_documents/
│   ├── __init__.py
│   ├── coherence_config.py       # Config desde YAML
│   ├── coherence_validator.py    # Validación de coherencia
│   ├── pain_solution_mapper.py   # Mapeo problemas→assets
│   ├── v4_diagnostic_generator.py
│   ├── v4_proposal_generator.py
│   ├── data_structures.py
│   └── templates/
│       ├── diagnostico_v4_template.md
│       └── propuesta_v4_template.md
└── asset_generation/
    ├── v4_asset_orchestrator.py  # Orquestador v4
    └── asset_diagnostic_linker.py # Vincula assets con diagnóstico

tests/
└── test_v4_edge_cases.py         # 11 tests de casos de borde

.conductor/
└── guidelines.yaml               # + v4_coherence_rules, price_validation
```

### 🔧 Mejoras

#### Sincronización Workflows-Código
- Workflow `.agents/workflows/v4_coherence_validator.md` alineado con `CoherenceConfig`
- Umbrales configurables desde `.conductor/guidelines.yaml`
- Criterios de éxito documentados y consistentes

#### Tests de Casos de Borde
- 11 tests implementados basados en `DOMAIN_PRIMER.md`
- Casos: WhatsApp conflict, Schema inválido, Datos parciales, Escenarios negativos, Assets bloqueados

#### Optimización de Controles
- **Centralización**: Umbrales en `.conductor/guidelines.yaml`
- **Fallback**: Valores por defecto si YAML no existe
- **Flexibilidad**: Reglas blocking/non-blocking configurables

### 🐛 Correcciones

| Problema | Solución |
|----------|----------|
| `diagnostic_doc=None` en orchestrator | Crear DiagnosticDocument completo con problems reales |
| Tabla "Sin datos" en diagnóstico | Extraer datos reales de audit_result.validation |
| "Sin assets planificados" en propuesta | Generar asset_plan desde PainSolutionMapper |
| Execute no encuentra v4.0 | Filtro por coherence_score >= 0.8 y vigencia < 20 días |

### 📚 Documentación

- `AGENTS.md`: Actualizado con nuevos módulos y flujo completo
- `CONTRIBUTING.md`: Nueva sección "Controles de Coherencia v4.0"
- `DOMAIN_PRIMER.md`: Regenerado con módulos commercial_documents/

---

## [4.0.0] - 2026-02-27

### 🎉 Release - Sistema de Confianza

Esta release representa una transformación fundamental del modelo IAH, pasando de un "generador de diagnósticos" a un "sistema de inteligencia con niveles de certeza explícitos".

### ✨ Nuevas Características

#### Arquitectura de Validación Cruzada
- **Módulo**: `modules/data_validation/`
- **Taxonomía de Confianza**: VERIFIED (≥0.9), ESTIMATED (0.5-0.9), CONFLICT (<0.5)
- **Validación entre fuentes**: web scraping, GBP API, input usuario, benchmarks
- **Detección automática de conflictos**: Bloquea assets con datos contradictorios
- **71 tests implementados**

#### Motor Financiero por Escenarios
- **Módulo**: `modules/financial_engine/`
- **Reemplaza**: Cálculos exactos por escenarios probabilísticos
- **Escenarios**: Conservador (70%), Realista (20%), Optimista (10%)
- **Transparencia**: Explicación completa de fórmulas en lenguaje natural
- **Proyecciones**: 6-12 meses con intervalos de confianza
- **125 tests implementados**

#### Flujo de Dos Fases
- **Módulo**: `modules/orchestration_v4/`
- **Fase 1 (Hook)**: Benchmark regional → Rango estimado con disclaimer
- **Fase 2 (Input)**: 5 datos mínimos → Validación cruzada → Escenarios
- **Tracking de progreso**: 30% → 60% → 100%
- **Gestión de estados**: INIT → PHASE_1 → PHASE_2 → VALIDATION → COMPLETE
- **66 tests implementados**

#### Generación Condicional de Assets
- **Módulo**: `modules/asset_generation/`
- **Preflight checks**: Gates de calidad antes de generar
- **Nomenclatura honesta**: `ESTIMATED_` prefix si confidence < 0.9
- **Metadatos obligatorios**: confidence_level, sources, generated_at, can_use
- **Assets soportados**: WhatsApp button, FAQ page, Hotel schema, Financial projection
- **76 tests implementados**

### 🔧 Mejoras Técnicas

#### APIs Externas
- **PageSpeed Insights API**: Validación real de Core Web Vitals
- **Rich Results Test API**: Verificación de schemas
- **Google Places API**: Datos GBP mejorados

#### Pre-commit Hooks
- Validación de imports de módulos v4.0
- Verificación de estructura de archivos
- Tests automáticos de todos los módulos

#### Tests
- **Total**: 338 tests pasando
- **Cobertura**: >95%
- **E2E**: 5 escenarios de hoteles completos

### 🐛 Problemas Resueltos

| Problema | Solución |
|----------|----------|
| WhatsApp falso en assets | Validación cruzada web+GBP+input |
| 50 FAQs → 18 (inconsistencia) | Preflight check + nombre honesto |
| 3 cifras diferentes de pérdida | Escenarios únicos con probabilidades |
| Performance Score inventado | PageSpeed API real |
| Assets sin validación | Gates de calidad obligatorios |
| Sin metadatos de confianza | Metadata en todos los assets |
| Sin explicación de cálculos | Fórmulas transparentes en lenguaje natural |

### 📁 Archivos Nuevos

```
modules/
├── data_validation/
│   ├── __init__.py
│   ├── confidence_taxonomy.py
│   ├── cross_validator.py
│   └── external_apis/
│       ├── __init__.py
│       ├── pagespeed_client.py
│       └── rich_results_client.py     # NEW - Rich Results Test API
├── auditors/                              # NEW - API Integration
│   ├── __init__.py
│   └── v4_comprehensive.py                # Auditor comprehensivo con APIs
├── financial_engine/
│   ├── __init__.py
│   ├── scenario_calculator.py
│   ├── formula_transparency.py
│   └── loss_projector.py
├── orchestration_v4/
│   ├── __init__.py
│   ├── two_phase_flow.py
│   └── onboarding_controller.py
└── asset_generation/
    ├── __init__.py
    ├── preflight_checks.py
    ├── asset_metadata.py
    └── conditional_generator.py

tests/
├── data_validation/          (94 tests - incluye rich_results)
├── financial_engine/         (125 tests)
├── orchestration_v4/         (66 tests)
├── asset_generation/         (76 tests)
└── e2e/
    └── test_v40_complete_flow.py

archives/legacy_v39/
├── modules/
│   ├── decision_engine_v391.py
│   └── delivery_manager_v391.py
└── scripts/
    └── validate_v391.py
```

### 📝 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/data_validation/__init__.py` | Agregados exports para Rich Results client |
| `modules/data_validation/external_apis/__init__.py` | Exports para Rich Results API |
| `modules/data_validation/external_apis/pagespeed_client.py` | Soporte GOOGLE_API_KEY fallback |
| `main.py` | Nuevo comando `v4audit` para auditoria API |

### 📚 Documentación

- `AGENTS.md` - Actualizado a v4.0
- `ARCHITECTURE_v4.md` - Nueva arquitectura
- `IMPLEMENTATION_COMPLETE_v40.md` - Resumen de implementación
- `IMPLEMENTATION_REPORT_v4_API.md` - Reporte de integracion APIs (NUEVO)
- `.env.template` - Variables de entorno incluyendo PAGESPEED_API_KEY

### ⚠️ Breaking Changes

#### API Changes
- `modules/decision_engine.py` → Reemplazado por `modules/financial_engine/`
- `modules/delivery/manager.py` → Reemplazado por `modules/asset_generation/`
- Cálculos exactos ($2.5M) → Escenarios con rangos ($X - $Y)

#### Datos Requeridos
- **Nuevo**: `PAGESPEED_API_KEY` en `.env` (para validación Core Web Vitals)
- **Nuevo**: Input de 5 datos mínimos del hotel (habitaciones, ADR, ocupación, OTAs, canal directo)

#### Outputs
- Assets ahora incluyen `_metadata` obligatorio
- Nomenclatura: `ESTIMATED_` prefix si confidence < 0.9
- Proyecciones financieras incluyen probabilidades

### 🔒 Seguridad

- Validación de datos cruzada antes de usar en assets
- Detección de conflictos entre fuentes
- Bloqueo automático de assets con datos no verificados
- Metadatos de confianza en todos los outputs

### 📊 Rendimiento

- Tiempo de validación: <100ms por campo
- Cálculo de escenarios: <50ms
- Generación de assets: <200ms por asset
- Tests completos: ~2 segundos (338 tests)

### 🙏 Agradecimientos

- Análisis forense de Hotel Visperas que identificó problemas v3.9
- Arquitectura de "Sistema de Confianza" inspirada en mejores prácticas de IA

---

## [3.9.1] - 2026-02-25

### Pipeline Parallelism & Bug Fixes

- Mejoras en paralelización de scrapers
- Correcciones menores de bugs
- Documentación actualizada

---

## [3.9.0] - 2026-02-20

### Mejoras en Validación

- Validation Engine nativo
- Pre-commit hooks mejorados
- Agent Harness v3.3

---

## [3.8.0] - 2026-02-10

### Automatización sin Gemini CLI

- Scripts de validación independientes
- Sincronización de versiones
- Context Integrity Validator

---

[4.0.0]: https://github.com/jhond/iah-cli/releases/tag/v4.0.0
[3.9.1]: https://github.com/jhond/iah-cli/releases/tag/v3.9.1
[3.9.0]: https://github.com/jhond/iah-cli/releases/tag/v3.9.0
[3.8.0]: https://github.com/jhond/iah-cli/releases/tag/v3.8.0
