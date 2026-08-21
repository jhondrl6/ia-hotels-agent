# Documentación Post-Proyecto — CREDIBILIDAD-NUMERICA-2026-08-20

> **Propósito**: acumular datos por fase para que FASE-RELEASE-4.72.0 genere CHANGELOG y GUIA_TECNICA oficiales sin reproceso.
> **Regla**: cada fase completa su columna "Fase" al cerrar sesión (Post-Ejecución paso 3). FASE-RELEASE SOLO consume este archivo, no registra fases.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (pendiente) | | | |

## Sección B: Funcionalidades Nuevas/Afinadas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Fuente única de pricing (D6) | commercial_documents, financial_engine, config | pricing.yaml master con `express_price` nuevo; hook_pdf_generator y v4_proposal_generator consumen dinámicamente; constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE/MONTHLY_PACKAGE_PRICE` eliminadas | FASE-P0-A |
| Gate pricing_compliance (D1 floor-aware) | quality_gates | Gate BLOCKING floor-aware: BLOCKED si pain_ratio > pain_ratio_gate_max del tier (0.32 boutique); WARNING si fuera del rango ideal 0.03-0.06 con operational_floor aplicado. Consume pricing_data del AssessmentBuilder + umbrales de pricing.yaml vía _load_pricing_config() | FASE-P0-B |
| Encoding utf-8 global en writers (F7) | quality_gates, utils | Todos los writers de artefactos (write_text) usan encoding='utf-8' explícito; auditoría estática AST anti-regresión | FASE-P0-C |
| Benchmark maestro único (F2+F4) | config, data/benchmarks, financial_engine | regional_adr_2026.json como master ADR/occupancy; Bogotá agregada; valores calibrados vs 6 observaciones Tier A; plan_maestro_data.json sincronizado; script validate_benchmark_sync.py anti-divergencia; normalización de regiones (aliases + lowercase) en RegionalADRResolver | FASE-P1-A |
| Fallback región conservador (F3) | auditors | 'colombia' resuelve a default ($300K) en lugar de caribe ($450K); evita sobreestimación 2.3-3.2x en hook | FASE-P1-B |
| Comisión OTA parametrizada (F5) | financial_engine, orchestration_v4, utils, config | Comisión OTA leída desde config/financial_defaults.yaml (18-22%, base 20%) con fuente documentada; 5 sitios hardcodeados eliminados; FinancialFactors.get_comision_ota() como API centralizada | FASE-P1-B |
| Verdad del sitio vivo | data_validation, asset_generation | Mapeo sedes + propagación site_verification | FASE-P1-D |
| Trazabilidad del rango Hook→Express | orchestration_v4 | Cap de plausibilidad + cierre del rango | FASE-P1-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base al inicio del plan | 3,233 funciones / 261 archivos (v4.71.0) | Preparación |
| Línea base de fallos preexistentes (suites tocadas) | 22 fallos: 12 commercial_documents + 10 financial_engine — evidence/BASELINE-TESTS-v4.71.0.txt | FASE-P0-A |
| Tests nuevos acumulados | 68 (3 P0-A + 18 P0-B + 4 P0-C + 19 P1-A + 24 P1-B) | FASE-P1-B |
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
