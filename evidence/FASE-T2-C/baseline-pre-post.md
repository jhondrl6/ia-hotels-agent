# Baseline FASE-T2-C — S-E2 y S9

**Fecha**: 2026-09-10
**Phase**: TRIBUNAL-OFFLINE-2026-09-09 / FASE-T2-C

## Pre-baseline (antes de cambios)

- Tests colectados: 3,983 (post T2-B)
- S-E2: `site_presence_report` asignado solo dentro de `if generate_proposal:` en `main.py`
- S-E2: 3 bloques `presence_lookup` en `v4_proposal_generator.py` con `hasattr(site_presence_report, 'results')` siempre False contra dict canónico
- S-E2: `self.site_checker = SitePresenceChecker()` en `v4_asset_orchestrator.py` instanciado pero nunca usado
- S9: `INVALID_MAPPINGS` con claves `pain_id` correctas (corregidas desde FASE-2), sin test de contrato propio (pero certificado por `test_invalid_mappings_valida_contra_capa1` en `test_service_identity_registry.py`)
- S9: Fósil V3 `ASSET_TO_PAIN_ID["monthly_report"] = "no_faq_schema"` — solo documentado en `service_identity.py:10`, no código vivo

## Cambios realizados

### S-E2 (NameError + código muerto)
1. `main.py`: Hoist de `site_presence_report = site_presence_snapshot` fuera del bloque `if generate_proposal:`
2. `v4_proposal_generator.py`: 3 bloques `presence_lookup` corregidos para manejar dict canónico Y dataclass `SitePresenceReport`
3. `v4_asset_orchestrator.py`: Import y instanciación de `SitePresenceChecker` retirados (muertos)

### S9 (Certificación INVALID_MAPPINGS)
1. Verificado con `grep`: fósil V3 solo existe como docstring en `service_identity.py` — cerrado
2. `ASSET_TO_PAIN_ID` en `v4_proposal_generator.py` ya es derivado del canónico (FASE-A)
3. Tests existentes certifican el contrato: `test_invalid_mappings_valida_contra_capa1` + `TestInvalidMappingsComplete`

## Post-baseline (después de cambios)

- Tests colectados: 3,990 (+7 nuevos)
- Tests nuevos: `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py` (7 tests)
- Tests afectados (no-regresión): 997 passed, 0 failed (commercial_documents + asset_generation + tribunal + S9)
- `run_all_validations.py --quick`: 8/8 PASS

## Criterios de completitud

- [x] AC15: S-E2 cerrado — `generate_proposal=False` sin NameError (test verde)
- [x] AC16: S9 certificado — test de contrato de `INVALID_MAPPINGS` verde
- [x] NR1: `3983 + 7 = 3990` (baseline pre/post verificado)
- [x] NR3: `run_all_validations.py --quick` TOTAL PASS (8/8)
- [x] NR4: No reimplementa gates (solo limpieza + fix de formato)
