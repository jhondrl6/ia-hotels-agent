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
| Benchmark maestro único | config, data/benchmarks | Una fuente ADR por región incl. Bogotá | FASE-P1-A |
| Verdad del sitio vivo | data_validation, asset_generation | Mapeo sedes + propagación site_verification | FASE-P1-D |
| Trazabilidad del rango Hook→Express | orchestration_v4 | Cap de plausibilidad + cierre del rango | FASE-P1-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base al inicio del plan | 3,233 funciones / 261 archivos (v4.71.0) | Preparación |
| Línea base de fallos preexistentes (suites tocadas) | 22 fallos: 12 commercial_documents + 10 financial_engine — evidence/BASELINE-TESTS-v4.71.0.txt | FASE-P0-A |
| Tests nuevos acumulados | 21 (3 P0-A + 18 P0-B) | FASE-P0-B |
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
