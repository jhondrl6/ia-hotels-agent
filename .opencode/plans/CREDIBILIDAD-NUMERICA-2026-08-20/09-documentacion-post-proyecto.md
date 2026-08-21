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
| Gate pricing_compliance | quality_gates | Bloqueo cuando is_compliant=false | FASE-P0-B |
| Benchmark maestro único | config, data/benchmarks | Una fuente ADR por región incl. Bogotá | FASE-P1-A |
| Verdad del sitio vivo | data_validation, asset_generation | Mapeo sedes + propagación site_verification | FASE-P1-D |
| Trazabilidad del rango Hook→Express | orchestration_v4 | Cap de plausibilidad + cierre del rango | FASE-P1-C |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests base al inicio del plan | 3,233 funciones / 261 archivos (v4.71.0) | Preparación |
| Línea base de fallos preexistentes (suites tocadas) | 22 fallos: 12 commercial_documents + 10 financial_engine — evidence/BASELINE-TESTS-v4.71.0.txt | FASE-P0-A |
| Tests nuevos acumulados | 3 (TestPricingContractF1: hook_pricing_matches_yaml, no_hardcoded_in_hook, no_hardcoded_in_proposal) | FASE-P0-A |
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
