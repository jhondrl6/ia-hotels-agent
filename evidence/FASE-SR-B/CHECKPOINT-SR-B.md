# Checkpoint FASE-SR-B — Unificación Promesa/Matriz/Gate (D-PF1)

**Fecha**: 2026-08-28 · **Plan**: SR-PIPELINE-FIXES-2026-08-27 · **Sesión 2** (~35/60 iteraciones) · **Estado**: ✅ COMPLETADA

## Decisión implementada (D-PF1)

La propuesta deriva sus servicios prometidos de la **fuente única** `pain_ledger + present_in_production`
(RC1 ↔ matriz ↔ gate). El gate excluye NO_BREACH del denominador de `coverage_ratio` (reutiliza la
taxonomía `actionable`; sin conteos paralelos — L-NC10). Sin pain ni presencia → footnote
"disponibles sin compromiso (fuera del coverage)" — fix B7 intacto.

## Conteo corrida C (verificado)

- 7 servicios del catálogo → no_breach=3 (SEO Local, WhatsApp, Open Graph), actionable=4
  (Schema Organization, Página de FAQ, Optimización para IA Generativa, Schema Hotel)
- coverage = 3/4 = 0.75 (estado intermedio hasta SR-E, donde presencia `exists_with_issues`
  re-clasifica hotel_schema → coverage=4/4=1.0)
- AEO no se renderiza bajo D-PF1: el servicio "Optimización para IA Generativa" ES el asset
  `llms_txt` del catálogo principal (dedup del mismo asset; registrado en 09 §Notas)
- Rama legacy (sin pain_ledger) intacta: catálogo estático ALL_PROMISED_SERVICES, filtro B7 previo

## Archivos modificados

| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/alignment_result.py` | `_DerivedEntry` (con `service_name`), `_from_entries` canónico, `actionable_total`, ruta legacy repara el NameError; 4 docstrings |
| `modules/quality_gates/publication_gates.py` | Gate `_proposal_asset_alignment_gate`: derivación D-PF1 antes de verify, trivial-pass (actionable=0 → 1.0), fallback ALL_PROMISED_SERVICES, `value=coverage_ratio` |
| `modules/asset_generation/proposal_asset_alignment.py` | (contexto) `_presence_exists`, `committed_services_from_entries`, `AssetAlignmentMatrix.committed_services()`, `derive_committed_services` |
| `modules/commercial_documents/v4_proposal_generator.py` | `_derive_committed_services()` (never-block), tabla dinámica con `committed_services`, AEO skip, footnote con suffix, logs |
| `tests/quality_gates/test_alignment_result.py` | corrida C actualizada a D-PF1 (3/4, actionable_total=4) |
| `tests/quality_gates/test_alignment_contract.py` | **NUEVO** — 10 tests de contrato 3 capas contra corrida C real |

## Resultados de test

- Suite gates `-k "alignment or proposal"`: **57 passed, 0 failed** (incluye 10 nuevos de contrato) → `tests_quality_gates_alignment.txt`
- Suites RC1 (test_proposal_dynamic + test_proposal_breach_consistency + test_promised_assets_production): **46 passed** + 8 fallos **preexistentes certificados en HEAD** (0 regresiones SR-B) → `tests_commercial_documents_rc1.txt`
- Greps de residuos: 0 matches en `modules/` ("sin costo (fallback)", "effective_alignment", "aligned_plus_present", "total_services_with_presence")
- `run_all_validations.py --quick`: 5/6 (Version Sync FAIL preexistente, mismo checkpoint que SR-A → se resuelve en RELEASE E2)

## Evidencia

- `fase_sr_b_code_diff.patch` — diff completo de código
- `tests_quality_gates_alignment.txt` — suite gates (57 passed)
- `tests_commercial_documents_rc1.txt` — suites RC1 (46 passed + 8 preexistentes)
- Certificación de preexistencia: backups en `temp/srb_bak/` + restauración HEAD verificada
