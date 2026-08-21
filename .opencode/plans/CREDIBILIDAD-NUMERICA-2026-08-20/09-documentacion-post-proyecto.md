# Documentación Post-Proyecto — CREDIBILIDAD-NUMERICA-2026-08-20

> **Propósito**: acumular datos por fase para que FASE-RELEASE-4.72.0 genere CHANGELOG y GUIA_TECNICA oficiales sin reproceso.
> **Regla**: cada fase completa su columna "Fase" al cerrar sesión (Post-Ejecución paso 3). FASE-RELEASE SOLO consume este archivo, no registra fases.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (pendiente) | | | |
| scrapers (google_places_client) | modules/scrapers/google_places_client.py | +search_by_name(): búsqueda Places API (New) por texto (nombre+ciudad) con category filter lodging | FASE-P2-B |
| scripts (preload_prospects_gbp) | scripts/preload_prospects_gbp.py | Script reutilizable de pre-carga GBP batch con gate de completitud (teléfono+dirección+categoría); soporta YAML/CSV/builtin; dry-run; reporte MD + JSON | FASE-P2-B |

## Sección B: Funcionalidades Nuevas/Afinadas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Fuente única de pricing (D6) | commercial_documents, financial_engine, config | pricing.yaml master con `express_price` nuevo; hook_pdf_generator y v4_proposal_generator consumen dinámicamente; constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE/MONTHLY_PACKAGE_PRICE` eliminadas | FASE-P0-A |
| Pre-carga GBP batch con gate de completitud (F9) | scrapers, scripts | search_by_name en GooglePlacesClient (Places API New searchText); preload_prospects_gbp.py con 30 prospectos embebidos; gate VERIFIED/PARTIAL/MISSING; reporte MD y JSON; modo dry-run | FASE-P2-B |
| Higiene documental comercial (F10) | docs, evidence/Recomendaciones | PRECIOS_PAQUETES.md unificado con pricing.yaml (COP, no USD); PROPUESTA_EMPAQUETADO actualizada (ADR $420K→$280K, ZIP actual, pricing.yaml citado); PROMPT_INGRESOS y README con ADR calibrado | FASE-P2-B |
| Gate pricing_compliance (D1 floor-aware) | quality_gates | Gate BLOCKING floor-aware: BLOCKED si pain_ratio > pain_ratio_gate_max del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con operational_floor aplicado. Consume pricing_data del AssessmentBuilder + umbrales de pricing.yaml vía _load_pricing_config() | FASE-P0-B |
| Encoding utf-8 global en writers (F7) | quality_gates, utils | Todos los writers de artefactos (write_text) usan encoding='utf-8' explícito; auditoría estática AST anti-regresión | FASE-P0-C |
| Benchmark maestro único (F2+F4) | config, data/benchmarks, financial_engine | regional_adr_2026.json como master ADR/occupancy; Bogotá agregada; valores calibrados vs 6 observaciones Tier A; plan_maestro_data.json sincronizado; script validate_benchmark_sync.py anti-divergencia; normalización de regiones (aliases + lowercase) en RegionalADRResolver | FASE-P1-A |
| Fallback región conservador (F3) | auditors | 'colombia' resuelve a default ($300K) en lugar de caribe ($450K); evita sobreestimación 2.3-3.2x en hook | FASE-P1-B |
| Comisión OTA parametrizada (F5) | financial_engine, orchestration_v4, utils, config | Comisión OTA leída desde config/financial_defaults.yaml (18-22%, base 20%) con fuente documentada; 5 sitios hardcodeados eliminados; FinancialFactors.get_comision_ota() como API centralizada | FASE-P1-B |
| Verdad del sitio vivo (F12+F13, D8) | data_validation, auditors, asset_generation, orchestration, quality_gates, commercial_documents | F12: validate_whatsapp con mapeo número→sede (web_alternates + gbp_location, firma backwards-compatible); scanner extrae todos los candidatos wa.me/tel con label de sede; GBP coincide con algún número web → VERIFIED, multi-sede sin mapeo → ESTIMATED, conflicto real misma sede → CONFLICT. F13: status VERIFIED_IN_SITE de primera clase en pain_ledger (apply_site_verification); reconciler lo preserva; coverage gate lo justifica (_JUSTIFIED_STATUSES); diagnóstico filtra brechas verificadas en producción | FASE-P1-D |
| Cableado benchmark master al hook (F6 causa raíz, D4) | orchestration_v4 | OnboardingController carga el master P1-A (regional_adr_2026.json) y lo pasa a TwoPhaseOrchestrator; normalización de keys de región (aliases del resolver); región sin match cae al "default" del master | FASE-P1-C |
| Cap de plausibilidad del rango del hook (F6, D7) | orchestration_v4, config | Ratio fijo max/min configurable (hook_range_max_ratio: 5.0 en financial_defaults.yaml); se aplica en la generación del rango del hook, no en escenarios; el extremo optimista se trunca sobre el piso conservador | FASE-P1-C |
| Coherence acepta "verificado en producción" (F14) | commercial_documents | `_check_promised_assets_exist` acepta site_presence_report: assets con status "exists"/"redundant" + site_verified=True NO se cuentan como missing; nuevo helper `_extract_verified_in_production_types`; mensaje enriquecido con production_only_types; alineado con gate proposal_asset_alignment | FASE-P2-A |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base al inicio del plan | 3,233 funciones / 261 archivos (v4.71.0) | Preparación |
| Línea base de fallos preexistentes (suites tocadas) | 22 fallos: 12 commercial_documents + 10 financial_engine — evidence/BASELINE-TESTS-v4.71.0.txt | FASE-P0-A |
| Tests nuevos acumulados | 127 (3 P0-A + 18 P0-B + 4 P0-C + 19 P1-A + 24 P1-B + 27 P1-C + 21 P1-D + 11 P2-A) | FASE-P2-B |
| Coherence última corrida | 0.9237 (evidence/FASE-F, pre-plan) | Preparación |
| Coherence E2E Zi One (post-plan) | (pendiente) | FASE-E2E-ZIONE |
| Tiempo corrida con caches cálidos (C9) | (pendiente) | FASE-E2E-ZIONE |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `config/pricing.yaml` | +express_price: 120000 en packages | FASE-P0-A |
| `modules/financial_engine/pricing_calculator.py` | +express_price en validated_packages y fallback defaults | FASE-P0-A |
| `modules/commercial_documents/hook_pdf_generator.py` | Eliminado constantes PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE; nuevo método _get_pricing_packages() desde pricing.yaml | FASE-P0-A |
| `modules/commercial_documents/v4_proposal_generator.py` | Eliminado constantes MONTHLY_PACKAGE_PRICE/SETUP_FEE; nuevo método _get_pricing_packages(); 15 usoss migrados a pricing.yaml | FASE-P0-A |
| `tests/commercial_documents/test_hook_pdf_generator.py` | +TestPricingContractF1 (3 tests contrato F1); test_pricing_constants actualizado a pricing.yaml | FASE-P0-A |
| `modules/quality_gates/publication_gates.py` | +_pricing_compliance_gate (gate 13, BLOCKING floor-aware D1); _load_pricing_thresholds(); imports logging+os; docstring actualizado a 13 gates (10 blocking + 3 advisory) | FASE-P0-B |
| `modules/assessment_builder.py` | +pricing_data campo en AssessmentPayload; +with_pricing() método fluid para inyectar pain_ratio/tier/price desde PricingResult | FASE-P0-B |
| `main.py` | +builder.with_pricing(pricing_result) en flujo FASE 4.5 (L2851) | FASE-P0-B |
| `AGENTS.md` | Gate count 12→13 (blocking 9→10); pricing_compliance en §Módulos y FASE 4.5 | FASE-P0-B |
| `tests/quality_gates/test_pricing_compliance_gate.py` | NUEVO — 18 tests: BLOCKING ratio>gate_max, WARNING floor-aware (D1 contrato Zione 0.0724), PASSED ideal range, boundary exacto, skip sin datos, multi-tier | FASE-P0-B |
| `tests/quality_gates/test_publication_gates.py` | Actualizados 4 assertions de conteo 12→13 (test_all_gates_pass, test_run_publication_gates_function, test_check_publication_readiness_function, test_visperas_comprehensive_report) | FASE-P0-B |
| `modules/quality_gates/delivery_quality_report.py` | +encoding="utf-8" en save() write_text (F7 fix) | FASE-P0-C |
| `modules/utils/config_checker.py` | +encoding="utf-8" en 2 write_text de test de permisos | FASE-P0-C |
| `tests/test_encoding_artifacts.py` | NUEVO — 4 tests: save utf-8, no mojibake, roundtrip special chars, auditoría estática AST write_text sin encoding | FASE-P0-C |
| `data/benchmarks/regional_adr_2026.json` | MASTER ADR/occupancy: v1.1.0; Bogotá agregada; valores calibrados vs observaciones Tier A (eje_cafetero boutique $420K→$280K) | FASE-P1-A |
| `data/benchmarks/plan_maestro_data.json` | ADR/occupancy sincronizados con master; Bogotá agregada; antioquia/caribe actualizados | FASE-P1-A |
| `config/regional_benchmarks.yaml` | ADR/occupancy sincronizados con master (referencial); versión 1.1.0 | FASE-P1-A |
| `modules/financial_engine/regional_adr_resolver.py` | +_normalize_region(); Bogotá alias; occupancy normalizada; _get_known_regions unificado; _determine_confidence normalizado | FASE-P1-A |
| `scripts/validate_benchmark_sync.py` | NUEVO — valida sincronización master↔plan_maestro_data (ADR + occupancy por región) | FASE-P1-A |
| `tests/financial_engine/test_benchmark_master.py` | NUEVO — 19 tests: Bogotá cobertura, eje_cafetero consistencia, sync todas regiones, mecanismo sync, normalización occupancy, known regions | FASE-P1-A |
| `tests/financial_engine/test_regional_adr_resolver.py` | Actualizados 6 assertions: region normalizado de alias a canónico (coffee_axis→eje_cafetero, medellin→antioquia) | FASE-P1-A |
| `tests/financial_engine/test_adr_resolution_wrapper.py` | Actualizado 1 assertion: metadata region normalizada | FASE-P1-A |
| `modules/auditors/v4_comprehensive.py` | F3: 'colombia' mapeado a 'default' en lugar de 'caribe' (L1471) | FASE-P1-B |
| `config/financial_defaults.yaml` | F5: añadido source a comision_ota (rango 18-22%, base 20%) | FASE-P1-B |
| `modules/utils/financial_factors.py` | F5: comision_ota_source en FinancialFactorsConfig + get_comision_ota() API centralizada | FASE-P1-B |
| `modules/financial_engine/scenario_calculator.py` | F5: import FinancialFactors; defaults 0.15→0.20; _trace_data_sources usa fuente de config | FASE-P1-B |
| `modules/financial_engine/calculator_v2.py` | F5: import FinancialFactors; defaults 0.15→0.20 en _to_hotel_financial_data y calculate_financial_scenarios | FASE-P1-B |
| `modules/financial_engine/inputs_contract.py` | F5: import FinancialFactors; defaults 0.15→0.20 en dataclass, validate() y from_dict() | FASE-P1-B |
| `modules/financial_engine/financial_evidence.py` | F5: import FinancialFactors; defaults 0.15→0.20; source actualizado a config/financial_defaults.yaml | FASE-P1-B |
| `modules/orchestration_v4/two_phase_flow.py` | F5: import FinancialFactors; _estimate_monthly_loss y phase_2 usan comisión OTA de config | FASE-P1-B |
| `modules/utils/benchmarks.py` | F5: DEFAULT_DATA comision_ota_base 0.15→0.20 | FASE-P1-B |
| `tests/auditors/test_region_fallback.py` | NUEVO — 12 tests F3: colombia→default, ciudades específicas→región correcta, cache, sin dirección | FASE-P1-B |
| `tests/financial_engine/test_ota_commission.py` | NUEVO — 12 tests F5: rango 18-22%, source, defaults en todos los consumidores, trace_data_sources | FASE-P1-B |
| `tests/financial_engine/test_scenario_calculator.py` | F5: 2 assertions actualizados 0.15→0.20 (defaults) | FASE-P1-B |
| `tests/financial_engine/test_inputs_contract.py` | F5: 1 assertion actualizado 0.15→0.20 (default normalized) | FASE-P1-B |
| `tests/financial_engine/test_financial_evidence.py` | F5: 1 test actualizado: value 0.15→0.20, source→config/financial_defaults.yaml | FASE-P1-B |
| `evidence/BASELINE-TESTS-auditors-v4.71.0.txt` | NUEVO — baseline de auditors (148 passed, 1 skipped) previa a FASE-P1-B | FASE-P1-B |
| `modules/orchestration_v4/two_phase_flow.py` | F6+F11: cableado de keys normalizadas en _get_regional_benchmarks (fallback al "default" del master); cap de plausibilidad en _calculate_hook_range (_get_hook_range_max_ratio desde config); dataclass HookRangeTraceability + validate_hook_range_traceability() + format_traceability_section(); disclaimer declara rango falsable | FASE-P1-C |
| `modules/orchestration_v4/onboarding_controller.py` | F6 (D4): load_benchmark_master() + _convert_master_region() cargan/convierten regional_adr_2026.json; __init__ pasa plan_maestro_data al orquestador (parámetro opcional benchmark_master_path); +get_range_traceability() (cifra Express desde escenario realista o valor explícito) | FASE-P1-C |
| `modules/commercial_documents/hook_pdf_generator.py` | F11: check advisory #9 en validate_data — fuga_mensual dentro del corredor [fuga_minima, fuga_maxima] con tolerancia 10%; +helper _parse_cop_number() | FASE-P1-C |
| `config/financial_defaults.yaml` | F6 (D7): +hook_range_max_ratio: 5.0 con fuente documentada | FASE-P1-C |
| `tests/orchestration_v4/test_hook_plausibility_cap.py` | NUEVO — 14 tests: cableado master (valores determinísticos con comisión patcheada), defaults documentados sin master, aliases, región sin match sin 23x, conversión del master real, cap configurable/fallback/piso 1.0, hook message acotado | FASE-P1-C |
| `tests/orchestration_v4/test_hook_express_traceability.py` | NUEVO — 13 tests: dentro/debajo/encima del corredor, límites inclusivos, narrativa benchmark→dato real, sección markdown, integración full-flow via OnboardingController (escenario realista como cifra Express) | FASE-P1-C |
| `modules/data_validation/cross_validator.py` | F12: validate_whatsapp acepta web_alternates + gbp_location (firma backwards-compatible); +_reconcile_whatsapp_multisede: match GBP con cualquier sede → VERIFIED, multi-sede sin mapeo → ESTIMATED (WARNING), conflicto real misma sede → CONFLICT; matching por tokens (palabras ≥4 chars) | FASE-P1-D |
| `modules/auditors/v4_comprehensive.py` | F12: +_extract_all_whatsapp_candidates (wa.me/api.whatsapp/tel con dedup normalizado) + _extract_sede_label (ventana de contexto DOM); CrossValidationResult +web_whatsapp_alternates + gbp_location; _run_cross_validation enriquece validate_whatsapp | FASE-P1-D |
| `main.py` | F12: caller validate_whatsapp (L1735) enriquecido con web_alternates y gbp_location desde audit_result.validation | FASE-P1-D |
| `modules/asset_generation/pain_ledger.py` | F13 (D8): +STATUS_VERIFIED_IN_SITE; +apply_site_verification(entries, site_presence_report) — entradas DETECTED cuyo asset mapeado existe/redundant + site_verified → VERIFIED_IN_SITE, severity LOW, evidence_refs site_verification:{asset}:{status}; +PAIN_TO_PRESENCE_ASSET | FASE-P1-D |
| `modules/asset_generation/v4_asset_orchestrator.py` | F13: cableado apply_site_verification tras from_pains y antes de save (solo si site_presence_report presente) | FASE-P1-D |
| `modules/orchestration/post_orchestrator_reconciler.py` | F13: _resolve_status preserva VERIFIED_IN_SITE (no lo sobreescribe en pain_ledger_resolved) | FASE-P1-D |
| `modules/quality_gates/publication_gates.py` | F13: VERIFIED_IN_SITE agregado a _JUSTIFIED_STATUSES del coverage gate (cubiertas + justificadas == detectadas) | FASE-P1-D |
| `modules/commercial_documents/v4_diagnostic_generator.py` | F13: +_load_verified_in_site_pain_ids (pain_ledger_resolved.json con fallback pain_ledger.json); _identify_brechas filtra pains VERIFIED_IN_SITE; cache_key incluye verified_ids | FASE-P1-D |
| `tests/data_validation/test_whatsapp_multisede.py` | NUEVO — 11 tests F12: caso Zione VERIFIED sin conflicto, degrade a ESTIMATED, conflicto real misma sede, legacy mono-sede, scanner con labels (fixture ZIONE_FOOTER_HTML) | FASE-P1-D |
| `modules/commercial_documents/coherence_validator.py` | F14: +_extract_verified_in_production_types (helper site_presence_report→set); _check_promised_assets_exist acepta site_presence_report (assets exists/redundant + site_verified → no missing); validate() cablea site_presence_report al check; mensaje enriquecido con production_only_types | FASE-P2-A |
| `tests/commercial_documents/test_promised_assets_production.py` | NUEVO — 11 tests F14: C1 (verified→PASSED), C2 (missing→FAILED), C3 (mix→PASSED), C4 (legacy), C5 (coherence↔gate alignment), edge cases (empty/verification_failed/site_verified=False) | FASE-P2-A |
| `modules/scrapers/google_places_client.py` | +search_by_name(): POST a places:searchText con textQuery=name+city, includedType=lodging, maxResultCount=3; cachea resultado; manejo errores HTTP 429/403/404 | FASE-P2-B |
| `scripts/preload_prospects_gbp.py` | NUEVO — ~300 líneas: parse YAML/CSV, 30 prospectos builtin Eje Cafetero, preload_prospect() con gate completitud (phone+address+category), generate_report() MD, save_json_results(), --dry-run, --builtin, --json-output | FASE-P2-B |
| `docs/PRECIOS_PAQUETES.md` | Reescrito v4.72.0: precios USD→COP, tiers desde pricing.yaml, paquetes Express/Starter/Professional/Enterprise, política de coherencia FASE-P0-A, benchmarks de regional_adr_2026.json | FASE-P2-B |
| `evidence/Recomendaciones/PROPUESTA_EMPAQUETADO_NO_TECNICO.md` | ADR $420K→$280K (sección 2.8, benchmark master v1.1.0); Express $120K citado desde pricing.yaml (sección 2.5); nota ZIP actual con README_DELIVERY+MANIFEST+IMPLEMENTATION_ORDER (sección 1) | FASE-P2-B |
| `evidence/Recomendaciones/PROMPT_INGRESOS.md` | ADR $420K→$280K (bloque de contexto, línea 5); fuente citada: data/benchmarks/regional_adr_2026.json | FASE-P2-B |
| `evidence/Recomendaciones/PROMPT_INGRESOS_README.md` | ADR $420K→$280K (tabla de datos calibrados, línea 29); referencia master v1.1.0 FASE-P1-A | FASE-P2-B |
