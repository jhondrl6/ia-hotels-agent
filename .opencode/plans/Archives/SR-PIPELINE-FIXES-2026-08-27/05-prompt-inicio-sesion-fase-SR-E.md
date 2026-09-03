# FASE-SR-E — Falso Negativo de Detección de Schema + Contabilización Única de `exists_with_issues`

**ID**: FASE-SR-E
**Objetivo**: Corregir la causa raíz REAL del bloqueo de `hotel_schema` (revisión causa-raíz 2026-08-28, ver §Base Técnica): (1) el audit reporta 0 schemas siendo FALSO — el sitio tiene 2 schemas Hotel (uno en formato JSON-LD ARRAY) y `rich_results_client` no soporta arrays → AttributeError tragado → falso pain `no_hotel_schema`; (2) doble contabilidad de `EXISTS_WITH_ISSUES`: bloquea la generación ("existe") pero NO cuenta como `present_in_production` en alignment ("no existe"). Mantener como hardening residual la semántica D-PF3 (fallback del catálogo para ausencia genuina).
**Dependencias**: FASE-SR-D ✅ (orden del plan; SR-E PRIMERO que SR-F — `pain_solution_mapper.py` en común).
**Complejidad**: Alta · **Delegación**: ❌ DIRECTO (fix cross-module: parser + audit + SitePresence + alignment)
**Duración estimada**: 60-90 min · **Presupuesto**: ~25 iteraciones trabajo + ~15 verificación/docs (R2: máx. 60)

## Reglas de Sesión (MANDATORIO)

- R1: Una fase por sesión. R2: máx. 60 iteraciones (checkpoint + evidencia si se agota). R3: 4 tareas + 0 comandos largos.
- Python: `./venv/Scripts/python.exe`.
- NO ejecutar `v4complete`/`v4audit` (la única corrida es SR-H). La verificación en vivo del parser se hace con tests con fixtures del HTML real, NO con corridas.

## Contexto

**Lectura previa obligatoria**: CONTEXT-SALENTOREAL §5 (H4), §9.5.2 N4, §8.2 L-SR4 + plan maestro §1 (H4 reclasificado + H7) y §8.

### Estado de Fases Anteriores
| Fase | Estado |
|------|--------|
| FASE-SR-A…SR-D | ✅ Completadas |

### Base Técnica Disponible (revisión causa-raíz 2026-08-28 — verificada contra código vivo y sitio vivo)

**La premisa original de esta fase (H4/N4: "el preflight de confianza bloqueó la generación") es FALSA. Evidencia:**

1. **El sitio SÍ tiene schemas** (verificado con fetch en vivo): `hotelsalentoreal.com` tiene 3 bloques `application/ld+json`: (a) `@graph` Yoast/WebPage, (b) **ARRAY** JSON `[{ "@type": "Hotel", ... }]`, (c) dict single `{ "@type": "Hotel", telephone: "+57 316 6296142", ... }`.
2. **El parser falla en el formato array**: `modules/data_validation/external_apis/rich_results_client.py` — `_validate_schema`/`_validate_single_schema` (~L198-220) manejan `@graph` y dict single, pero NO listas: `data.get("@type", ...)` sobre una list lanza `AttributeError: 'list' object has no attribute 'get'`. El `except` del bucle de parsing (~L128-196) solo captura `(json.JSONDecodeError, TypeError)`.
3. **El error se traga**: `test_url` (~L96-126) `except Exception → status="ERROR"`, y `get_hotel_schema_report` (~L497-547) con ERROR retorna `has_hotel_schema=False, all_schemas=[]`. Prueba empírica ejecutada: `status: ERROR, error: 'list' object has no attribute 'get', detected_items: 0`.
4. **El audit propaga el falso negativo en silencio**: `modules/auditors/v4_comprehensive.py:680-697` (`_audit_schemas`) consume `get_hotel_schema_report` → `SchemaAuditResult(total_schemas=0)`; el `error_message` del resultado ERROR NUNCA llega al `SchemaAuditResult`. Artefacto corrida C: `audit_report.total_schemas = 0` (falso).
5. **El pain `no_hotel_schema` es un FALSO POSITIVO**: `pain_solution_mapper.py` ~L393-399 genera el pain si `not audit_result.schema.hotel_schema_detected`. Score 85, HIGH, $1.06M COP/mes — cifra inventada sobre una detección rota.
6. **Lo que realmente detuvo la generación**: `conditional_generator.py:110-127` — gate de presencia (FASE-CAUSAL-01) ANTES del preflight: `SitePresenceChecker` (vía el detector `modules/scrapers/schema_finder.py`, que SÍ detectó el schema) retornó `EXISTS_WITH_ISSUES` ("Campos faltantes: ['priceRange', 'amenityFeature', 'image', 'url']") → `should_generate=False` → SKIPPED. El mensaje "Insufficient confidence (0.00 < 0.8)" de `pain_solution_mapper.py:889` solo afecta el DISPLAY del plan en `main.py:2411`; el orquestador regenera specs con `can_generate=True` (`v4_asset_orchestrator._solutions_to_asset_specs` ~L712-722).
7. **Doble contabilidad** (viola L-SR3): `EXISTS_WITH_ISSUES` bloquea la generación ("existe en producción") pero `site_presence_checker.should_generate` (~L76-82) NO lo cuenta como `present_in_production` en alignment → queda `unresolved`. El mismo hecho tratado como "existe" y "no existe" según el consumidor.
8. **Dos detectores contradictorios sin arbitraje**: `schema_finder.py` (scrapers, detectó el schema) vs `rich_results_client` (auditors, 0 schemas).

## Tareas

### T1: Confirmar la cadena de fallo con tests reproduciendo el bug
**Archivos**: `modules/data_validation/external_apis/rich_results_client.py`, `modules/auditors/v4_comprehensive.py` (L640-700), `modules/scrapers/schema_finder.py`, `modules/asset_generation/site_presence_checker.py`, `modules/asset_generation/conditional_generator.py` (L90-200), `modules/commercial_documents/pain_solution_mapper.py` (~L393-399).
**Criterios**:
- [ ] Test rojo que reproduce: bloque ld+json en formato ARRAY con `@type: Hotel` → `get_hotel_schema_report` hoy retorna `has_hotel_schema=False` (bug confirmado)
- [ ] Test rojo: `SchemaAuditResult` no expone el `error_message` del resultado ERROR (falso negativo silencioso)
- [ ] Mapa documentado: qué detector consume SitePresenceChecker vs qué detector consume el audit, y dónde se decide `present_in_production` en alignment

### T2: Fix de detección + contabilización única
**Criterios**:
- [ ] `rich_results_client` soporta JSON-LD en formato ARRAY (iterar elementos de la lista; cada elemento se valida como schema individual) y el bucle de parsing captura `AttributeError`/`Exception` por bloque (un bloque corrupto NO invalida los demás)
- [ ] Si TODOS los bloques fallan o el resultado es ERROR, el error se PROPAGA: `SchemaAuditResult` expone `error_message`/warnings (el audit nunca reporta "0 schemas" en silencio cuando hubo error de parsing — distinguir "ausencia verificada" de "detección fallida")
- [ ] Contabilización única (L-SR3): `EXISTS_WITH_ISSUES` cuenta como `present_in_production` en alignment/matrix (el asset existe en el sitio; sus campos faltantes van como mejora sugerida, no como brecha unresolved). Un solo criterio compartido con SR-B
- [ ] Con schema detectado por el audit (`hotel_schema_detected=True`), el pain `no_hotel_schema` NO se genera (elimina el falso positivo de raíz)
- [ ] Hardening residual D-PF3 (solo para ausencia GENUINA verificada): si el sitio realmente no tiene schema y hay GBP completo, el preflight respeta `fallback="generate_basic_schema"` + `block_on_failure=False` del catálogo; sin fuentes → bloqueo con `justified_skip`
- [ ] `generate_basic_schema` queda cableado a un consumidor real o se documenta su no-implementación como seguimiento explícito (grep: 0 declaraciones sin consumidor)

### T3: Tests (fixture real + casos opuestos)
**Criterios**:
- [ ] Fixture con los 3 bloques reales de hotelsalentoreal.com (`@graph` + ARRAY Hotel + dict Hotel) → `get_hotel_schema_report` detecta ≥ 2 schemas Hotel; `total_schemas ≥ 1`
- [ ] Con detección correcta: pain `no_hotel_schema` NO generado; `promised_assets_exist` sin "Assets no implementados: hotel_schema"
- [ ] `EXISTS_WITH_ISSUES` → `present_in_production` en alignment (cuenta como cubierto, no unresolved)
- [ ] Bloque corrupto aislado no invalida bloques válidos; resultado ERROR propaga `error_message` al audit
- [ ] Ausencia genuina (0 schemas + sin GBP) → sin generación, sin invención, `justified_skip`
- [ ] Regresión: suites de auditors y asset_generation tocadas (archivos específicos)

### T4: Greps + docs
**Criterios**:
- [ ] Grep: el criterio de presencia es UNO solo — 0 paths que traten `EXISTS_WITH_ISSUES` como "no presente" en alignment
- [ ] Grep: `get_hotel_schema_report` sin consumidores que ignoren su `error_message`/status ERROR
- [ ] Documentar en `10-analisis` la decisión sobre el arbitraje schema_finder vs rich_results (¿fuente única? ¿unión? — decidir y registrar, no dejar ambos sin contrato)

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| parser array JSON-LD (fixture real Salento) | `tests/data_validation/` (archivo existente de rich_results o nuevo específico) | ≥2 schemas Hotel detectados |
| propagación de error al audit | tests de `v4_comprehensive` (específicos) | ERROR → error_message visible, nunca 0 silencioso |
| contabilización única exists_with_issues | tests de alignment/site_presence | cuenta como present_in_production |
| ausencia genuina sin fuentes | tests de pain_solution_mapper (específicos) | bloqueo + justified_skip |

**Comandos** (procesos aislados, salida a archivo):
```bash
./venv/Scripts/python.exe -m pytest tests/data_validation -k "rich_results or schema" -v > temp/fase_sr_e_tests1.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/asset_generation -k "presence or alignment" -v > temp/fase_sr_e_tests2.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/auditors -k "comprehensive or schema" -v > temp/fase_sr_e_tests3.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Post-Ejecución (OBLIGATORIO — antes de cerrar la sesión)

1. `dependencias-fases.md` §2 → ✅. 2. `README.md` → ✅. 3. `06-checklist` → SR-E. 4. `09-documentacion` → B/D/E + Notas. 5. `10-analisis` → Resumen + D-PF3 ajustada (revisión causa-raíz 2026-08-28) + lecciones + decisión de arbitraje de detectores. 6. `evidence/FASE-SR-E/` → diff + tests + fixture del HTML real. 7. Registro (SIN `--release`):
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-SR-E --desc "Fix falso negativo schema (JSON-LD array en rich_results_client + propagacion de error al audit) + contabilizacion unica exists_with_issues como present_in_production + fallback catalogo residual (D-PF3)" --archivos-mod "modules/data_validation/external_apis/rich_results_client.py,modules/auditors/v4_comprehensive.py,modules/asset_generation/site_presence_checker.py,modules/quality_gates/publication_gates.py,modules/commercial_documents/pain_solution_mapper.py" --tests "<N reales>" --check-manual-docs
```
8. `./venv/Scripts/python.exe scripts/doctor.py --regenerate-domain-primer`

## Criterios de Completitud (CHECKLIST)

- [ ] Bug del parser reproducido con test rojo ANTES del fix
- [ ] Fixture real de Salento detecta ≥2 schemas Hotel; falso pain eliminado
- [ ] Contabilización única de `exists_with_issues` implementada y testeada
- [ ] `run_all_validations.py --quick` TOTAL PASS; regresiones = 0 en suites tocadas
- [ ] Docs post-fase completos (1-8)
- [ ] Evidencia en `evidence/FASE-SR-E/`

## Restricciones

- Máx. 60 iteraciones; NO ejecutar v4complete/v4audit.
- NO bajar el umbral global 0.8 (enmascara problemas semánticos).
- NO tocar la rama GEO existente (`geo_enriched/hotel_schema_rich.json`) — esta fase trata la detección y el asset del catálogo.
- NO silenciar errores de parsing (todo ERROR debe ser visible en el audit — L-SR5).
- NO delegar a subagente; NO usar `--release` en log_phase_completion.
- AC10: capa financiera intacta.
