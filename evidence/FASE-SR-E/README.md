# Evidencia FASE-SR-E — Falso Negativo de Detección de Schema + Contabilización Única

**Fecha**: 2026-08-28 · **Sesión**: agente (Sesión 5, DIRECTO, venv) · **Plan**: SR-PIPELINE-FIXES-2026-08-27

## Resultados

| Verificación | Resultado | Archivo |
|--------------|-----------|---------|
| Tests nuevos TDD (rojo pre-fix → verde post-fix) | 11/11 schema detection + 20/20 presence accounting | `fase_sr_e_fix1.txt`, `fase_sr_e_fix2.txt` |
| Regresión `tests/data_validation -k "rich_results or schema"` | 58 passed, 0 fallos | `fase_sr_e_tests1.txt` |
| Regresión `tests/asset_generation -k "presence or alignment"` | 81 passed, 0 fallos | `fase_sr_e_tests2.txt` |
| Regresión `tests/auditors -k "comprehensive or schema"` | 9 passed, 0 fallos | `fase_sr_e_tests3.txt` |
| `run_all_validations.py --quick` | 6/6 PASSED | `fase_sr_e_validations.txt` |

## Contenido

- `diff_sr_e.patch` — git diff de los 9 módulos tocados. NOTA: diff acumulado desde HEAD
  (fases SR-A..SR-D sin commit; los archivos exclusivos de SR-E —`rich_results_client.py`,
  `v4_comprehensive.py`, `site_presence_checker.py`— contienen SOLO cambios de esta fase).
- `test_fase_sr_e_schema_detection.py` — 11 tests: parser JSON-LD ARRAY (fixture real Salento,
  ≥2 schemas Hotel), parse_errors por bloque (corrupto no invalida), ERROR solo si todos
  fallan, propagación `error_message` a `SchemaAuditResult` con warning (L-SR5).
- `test_fase_sr_e_presence_accounting.py` — 20 tests: criterio canónico
  `is_present_in_production` (EXISTS + EXISTS_WITH_ISSUES), contabilización en
  alignment/matrix/generator/ledger/coherencia, D-PF3 (fallback catálogo con fuentes /
  `justified_skip` sin fuentes), contrato preflight↔catálogo.
- `salento_real_fixture.html` — los 3 bloques `application/ld+json` reales de
  hotelsalentoreal.com (verificación en vivo 2026-08-28).

## Greps de residuos (T4)

- `status == "exists"` en `modules/`: 1 match — `coherence_validator.py:385`
  (`site_whatsapp_exists`), exclusión DELIBERADA (el HTML check de WhatsApp nunca produce
  `exists_with_issues`).
- `get_hotel_schema_report` en `modules/`: único consumidor `v4_comprehensive.py:691`
  (`_audit_schemas`), que propaga `status`/`error_message` (0 consumidores que ignoren el error).

## Fixes aplicados (9 módulos)

1. `rich_results_client.py` — parser polimórfico (dict/list/@graph), `parse_errors` por
   bloque, ERROR solo si TODOS fallan, reportes exponen `status`/`error_message`/`parse_errors`.
2. `v4_comprehensive.py` — `SchemaAuditResult.error_message` + warning severity ERROR en
   `_audit_schemas` ("0 schemas NO es ausencia verificada") + `to_dict()`.
3. `site_presence_checker.py` — `PRODUCTION_PRESENT_STATUSES` + `is_present_in_production()`.
4-9. `alignment_result.py`, `proposal_asset_alignment.py`, `pain_ledger.py`,
   `coherence_validator.py`, `v4_proposal_generator.py` (×3), `pain_solution_mapper.py`
   (D-PF3: fallback catálogo con fuentes / `justified_skip` sin fuentes).

## Decisión de arbitraje de detectores

`rich_results_client` = detector canónico del AUDIT (propaga error); `schema_finder`
(scrapers) = detector de PRESENCIA (SitePresenceChecker), intacto (fuera de alcance —
matriz de conflictos no lo lista). Contrato común: taxonomía de presencia + criterio
canónico compartido (L-NC10). Para Salento ambos convergen (audit ≥2 Hotel; presencia
EXISTS_WITH_ISSUES → presente en producción).
