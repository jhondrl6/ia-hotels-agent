# Checklist de Implementación — BUGS-ONBOARDING-ADR-2026-07-22

> **Convención**: 1 fase = 1 sesión. Marcar [x] al completar.

## FASE-1: Root Cause — ADR + Occupancy Propagation ✅ COMPLETADA

- [x] 1.1 Agregar `user_provided_adr` al payload del AgentTask financiero en main.py
- [x] 1.2 Agregar `occupancy_source` al payload + guard en harness_handlers.py
- [x] 1.3 Arreglar `main.py:1861` adr_source placeholder "handler" → `adr_resolution.source`
- [x] 1.4 Verificación: handler test con user_provided_adr=330000
- [x] 1.5 Commit: `fix(BUG-1+NEW-1): propagate ADR+occupancy from onboarding to harness payload` (d0747ce)
- [x] 1.6 Regresión: 700 tests preexistentes pasan

## FASE-2: Cascade — Proposal Generator (H1) + ValidationSummary (H3) ⬜ PENDIENTE

- [ ] 2.1 Fix H1: Proposal generator recibe ADR del onboarding (no resolver paralelo con None)
- [ ] 2.2 Fix H3: ValidationSummary confidence/sources de adr_source real (no flag existencia)
- [ ] 2.3 Verificación de invariantes: grep checks
- [ ] 2.4 Regresión: tests commercial_documents + financial_engine
- [ ] 2.5 Commit: `fix(H1+H3): proposal ADR from onboarding + validation summary real source`

## FASE-3: Taxonomy Unification (H2) + CTA Fix (BUG-2, Opción C) ⬜ PENDIENTE

- [ ] 3.1 Fix H2: Discriminador del diagnóstico matchea vocabulario correcto
- [ ] 3.2 Fix BUG-2 (Opción C): Crear función centralizada _build_onboarding_cta + dict _ONBOARDING_CTA_MESSAGES
- [ ] 3.3 Fix BUG-2: Refactorizar los 7 CTAs para usar _build_onboarding_cta
- [ ] 3.4 Verificación: grep centralización + no bloques if dispersos
- [ ] 3.5 Regresión: tests commercial_documents + financial_engine
- [ ] 3.6 Commit: `fix(H2+BUG-2): unify source taxonomy + centralized onboarding CTA function`

## FASE-4: E2E Tests (H4) + v4complete Don Alfonso + Análisis ⬜ PENDIENTE

- [ ] 4.1 Tests e2e: tests/e2e/test_onboarding_to_harness_pipeline.py (6 tests)
- [ ] 4.2 v4complete: `python3 main.py v4complete https://www.donalfonsohotel.com/`
- [ ] 4.3 Análisis: verificar adr_cop=330000, occupancy=0.4242, adr_source!="handler"
- [ ] 4.4 Análisis: CTA "Complete el onboarding" NO aparece en diagnóstico
- [ ] 4.5 Análisis: ADR consistente entre diagnóstico y propuesta
- [ ] 4.6 Llenar 08-analisis-post-implementacion.md
- [ ] 4.7 Commit: `test(H4): e2e onboarding pipeline + v4complete Don Alfonso verification`

## FASE-5: RELEASE ⬜ PENDIENTE

- [ ] 5.1 Version bump en VERSION.yaml
- [ ] 5.2 CHANGELOG.md con todos los fixes
- [ ] 5.3 Docs cascade (GUIA_TECNICA.md, AGENTS.md si aplica)
- [ ] 5.4 Pre-commit validation
- [ ] 5.5 Commit: `release: BUGS-ONBOARDING-ADR fixes v<version>`

## DoD Global

- [ ] ADR=$330,000 COP en diagnóstico, propuesta y JSON
- [ ] Occupancy=0.4242 en JSON
- [ ] adr_source != "handler" en JSON
- [ ] ValidationSummary.confidence consistente con fuente real
- [ ] CTA "Complete el onboarding" no aparece con onboarding cargado (centralizado en _build_onboarding_cta)
- [ ] ADR consistente entre diagnóstico y propuesta
- [ ] Tests e2e pasando
- [ ] v4complete Don Alfonso verificado
- [ ] 700 tests preexistentes sin regresión
- [ ] RELEASE completado
