# Documentación Post-Proyecto — SR-PIPELINE-FIXES-2026-08-27

> **Fuente de datos para FASE-RELEASE-4.73.0** (CHANGELOG + GUIA_TECNICA). Cada fase completa SUS filas al cerrar (executor §4, template §5.3).

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| (ninguno previsto — refactor de módulos existentes) | | | |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Helper único de conteo `unresolved` | `modules/quality_gates/alignment_result.py` | `AlignmentResult.compute_unresolved()` consumido por gate_report y delivery_quality_report (fin de la divergencia 4-vs-1) | SR-A |
| Guardián estático L-SR1 | `tests/test_main_static_guards.py` | Test AST que impide símbolos no definidos (`logger.`) en ramas no ejercitadas de main.py | SR-A |
| Promesa derivada de fuente única | `modules/commercial_documents/v4_proposal_generator.py` + `modules/asset_generation/proposal_asset_alignment.py` | Servicios prometidos derivados del pain_ledger + present_in_production; NO_BREACH fuera del coverage (fin del bloqueo estructural) | SR-B |
| Self-healing de claims | `modules/quality_gates/commercial_gate.py` + flujo de regeneración | CG-CLAIM-VS-EVIDENCE cicla: regenera con suggestion + re-valida; persistencia → BLOCKED real | SR-C |
| target_id canónico | `main.py` + `modules/orchestration_v4/onboarding_controller.py` | Identidad de memoria derivada de la URL canónica (`_normalize_url()`): v4complete graba/busca con `canonical_url`, execute y validate-guarantee derivan su id desde la canónica; `generate_hotel_id` normaliza via urlparse (fin de fragmentación por UTM/campaña — L-SR2/N3) | SR-D |
| Fix detección schema + contabilización única | `rich_results_client.py`, `v4_comprehensive.py`, `site_presence_checker.py`, `pain_solution_mapper.py` | JSON-LD array soportado; error_message propagado al audit; `exists_with_issues` = `present_in_production`; fallback catálogo residual (D-PF3) | SR-E |
| Determinismo del plan de assets | `pain_solution_mapper.py` (o cache) | Hipótesis de varianza 7→5 verificada/fixeada | SR-F |
| Display sincronizado con fuente | `modules/quality_gates/commercial_gate.py` | CG-TIER-CONSISTENCY deriva de fuente financiera; jerga reducida en vista gerencia | SR-G |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests totales (baseline) | 3,379 | — |
| Tests nuevos SR-A | 6 (3 corrida-C + 3 guardián AST); 148 ejecutados aislados, 0 regresiones | SR-A |
| Tests nuevos SR-B | 10 (TestContractProposalLayer 4 + TestAntiB7 2 + TestContractGateLayer 4 en `tests/quality_gates/test_alignment_contract.py`); gates 57 PASSED aislado; 0 regresiones (8 fallos preexistentes en test_proposal_dynamic certificados en HEAD) | SR-B |
| Tests nuevos SR-C | 20 (`test_claim_self_healing.py`, 6 clases); regresiones aisladas: 79 gates + 27 generator + 57 gate/guardián L-SR1, 0 fallos; quick 6/6 | SR-C |
| Tests nuevos SR-D | 28 (`tests/test_target_id_canonicalization.py`: 9 target_id + 8 generate_hotel_id + 5 región + 3 reutilización memoria + 3 guardián estático); regresión aislada 108 (guardián 3 + onboarding_controller 37 + hook_traceability 13 + fase_d_loader 13 + onboarding_injection 7 + evidence_paths 27 + harness_core 8), 0 fallos; quick 6/6 | SR-D |
| Tests nuevos SR-E | (contar al cerrar) | SR-E |
| Tests nuevos SR-F | (contar al cerrar) | SR-F |
| Tests nuevos SR-G | (contar al cerrar) | SR-G |
| Coherence corrida final | (llenar en SR-H) | SR-H |
| Gates PASSED corrida final | (llenar en SR-H) | SR-H |
| readiness corrida final | (llenar en SR-H) | SR-H |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `modules/quality_gates/alignment_result.py` | Helper compute_unresolved unificado | SR-A |
| `modules/quality_gates/publication_gates.py` | Consumo del helper; gate excluye NO_BREACH | SR-A/SR-B |
| `modules/quality_gates/delivery_quality_report.py` | G9 consume helper único | SR-A |
| `modules/commercial_documents/v4_proposal_generator.py` | Promesas derivadas del pain_ledger | SR-B |
| `modules/asset_generation/proposal_asset_alignment.py` | Taxonomía única / actionable como fuente | SR-B |
| `modules/quality_gates/commercial_gate.py` | Self-healing + tier display + jerga | SR-C/SR-G |
| `main.py` | Canonicalización target_id: `canonical_url` en v4complete (búsqueda + 2 append_log + save_analysis_reference), execute, validate-guarantee; onboard persiste hotel['url'] sin query | SR-D |
| `modules/orchestration_v4/onboarding_controller.py` | `generate_hotel_id` normaliza via urlparse antes de construir el id | SR-D |
| `tests/test_target_id_canonicalization.py` | 28 tests anti-fragmentación + guardián estático de call sites | SR-D |
| `modules/data_validation/external_apis/rich_results_client.py` + `modules/auditors/v4_comprehensive.py` + `modules/asset_generation/site_presence_checker.py` | Fix detección schema + contabilización única (H7) | SR-E |
| `modules/commercial_documents/pain_solution_mapper.py` | Falso pain eliminado + determinismo | SR-E/SR-F |

## Notas de Ejecución por Fase

### FASE-SR-A
- Sesión agente 2026-08-28 (DIRECTO, venv). Helper único `AlignmentResult.compute_unresolved()` + bucket `no_breach` → mensaje G9 aritméticamente coherente (3 cubiertos + 1 sin cubrir + 3 sin brecha = 7 en corrida C).
- Decisión: el gate deriva los estados semánticos con el MISMO builder que produce `proposal_asset_matrix.json` (`AssetAlignmentMatrix.build` desde el `pain_ledger` del assessment) — sin duplicar criterios (L-NC10); fallback narrow con `logger.warning` (never-block).
- La decisión de bloqueo del gate NO cambia (usa `effective_alignment`): SR-A unifica el CONTEO (N1); la unificación de decisión es SR-B.
- Desviación esperada: `run_all_validations --quick` = 5/6 — fallo Version Sync PREEXISTENTE (headers AGENTS/.cursorrules/GUIA_TECNICA; git confirma archivos intocados; `version_consistency_checker` OK). Resolución: E2 de FASE-RELEASE (`sync_versions.py`).
- Greps (L2): 0 conteos paralelos de unresolved G9; `logger.` en main.py = 0 (AC13). Evidencia: `evidence/FASE-SR-A/`.

### FASE-SR-B
- Sesión agente 2026-08-28 (DIRECTO, venv). D-PF1 implementada: `derive_committed_services` / `committed_services_from_entries` en `proposal_asset_alignment.py` — comprometido = pain mapeado OR presencia `exists` (dict normalizado, plano u objeto con .results).
- RC1 (`v4_proposal_generator.py`): `_derive_committed_services` conecta pain_ledger → tabla dinámica; filas = SOLO comprometidos (MISSING-con-pain se muestra ⏳ Pendiente, coherente con gate); no comprometidos → footnote "— disponibles sin compromiso (fuera del coverage)"; fila AEO omitida bajo D-PF1 (dedup del mismo asset llms_txt); filtro B7/D-NC7 intacto (WhatsApp sin brecha no se lista).
- Gate (`publication_gates.py`): derivación de semantic_entries reordenada ANTES de `verify_proposal_asset_alignment`; override `proposal_services = matrix.committed_services(...)`; PASS trivial con 0 comprometidos (never-block); `value = coverage_ratio` y `missing_count = unresolved` del DTO canónico — eliminados los conteos paralelos `pct` y `effective_alignment` (L-NC10).
- `AlignmentResult` (`alignment_result.py`): cálculo canónico `_from_entries` (ambos constructores delegan — AC3), propiedad `actionable_total`, mensaje "X/Y servicios comprometidos cubiertos … K sin brecha (no comprometidos, fuera del coverage)", dataclass `_DerivedEntry` (con service_name) para la ruta legacy sin pain_ledger.
- Greps (T4): 0 residuos de "sin costo (fallback)" / `effective_alignment` / `aligned_plus_present` en modules/. `run_all_validations --quick` 5/6 (Version Sync preexistente → RELEASE E2). Evidencia: `evidence/FASE-SR-B/`.
- Corrida C: coverage sobre actionable 3/4 = 0.75 (estado intermedio documentado) → tras SR-E 3/3 = 1.0. Suite gates: 57 PASSED (10 tests de contrato nuevos). `test_proposal_dynamic.py`: 8 fallos PREEXISTENTES certificados contra HEAD (git show baseline; catálogo 7 entradas vs test espera 8; B7 quita WhatsApp del footnote) — 0 regresiones SR-B.

### FASE-SR-C
- Sesión agente 2026-08-28 (DIRECTO, venv; continuada post-compactación). D-PF2 implementada: `ClaimSelfHealer` en `modules/quality_gates/claim_self_healing.py` (NUEVO, 404 líneas) — al fallo BLOCKING CG-CLAIM-VS-EVIDENCE: regeneración con el claim trazable textual del `suggestion` (restricción obligatoria) → re-validación con la MISMA closure `_validate_diagnostic` (0 caminos paralelos); máx 1 reintento (guard anti-bucle); persistencia → `escalated_to_blocked`.
- Estrategias por tipo de oración: condicional intacta; instrucción al lector/otro sujeto → neutralizada con sinónimo ("falta"); sujeto GBP → claim trazable del suggestion (preserva prefijo lista/etiqueta/tabla y puntuación).
- main.py: flag `_claim_escalated` → GATE BLOCKING extendido, BLOCKED_BY_GATES.md con causa, ZIP abortado. "hidden from client" intacto (solo cambió la consecuencia).
- Regexes del gate extraídas a constantes de módulo compartidas gate↔healer (L-NC10/L27); traza `self_healing` en `commercial_gates_report_diagnostic_*.json` (sin consumidores existentes).
- Sustitución documentada: `tests/commercial_documents/test_commercial_gates.py` del prompt NO existe → `tests/quality_gates/test_commercial_gate.py` (real, incluida en los conteos 79/57).
- Autorrevisión pre-tests corrigió 2 defectos: `_TRAILING_PUNCT` (hack de reversa con `$`) y `_LIST_PREFIX` con `\s*` que consumía énfasis markdown.
- Version Sync resuelto in-session (`sync_versions.py`: fecha de 3 headers 2026-08-24→2026-08-28; el patrón de versión no matchea el prefijo "v" y no se verifica) → quick 6/6 en SR-C (SR-A/B reportaron 5/6 por esto).
- Greps (T4): 0 caminos paralelos de regeneración; "hidden from client" persiste. Evidencia: `evidence/FASE-SR-C/` (20+79+27+57 passed).

### FASE-SR-D
- Sesión agente 2026-08-28 (DIRECTO, venv). D-PF4 CONFIRMADA: `canonical_url = _normalize_url(args.url)` como primer paso de `run_v4_complete_mode` (tras crear output_dir); target_id canónico en los 3 call sites de memoria (2 `append_log` + `save_analysis_reference`) y en la búsqueda `find_latest_analysis`; la URL ORIGINAL `args.url` se conserva para región/nombre/scraping/audit y como campo `url` de trazabilidad en los logs.
- Resto de comandos: execute construye `target_id = _normalize_url(args.url)` (nombre/input_data intactos); validate-guarantee deriva `hotel_id` desde la canónica (estable ante protocolo/www/UTM; `hotel_url` original conservada para la consulta GSC); onboard persiste `hotel['url']` SIN query string (`urlunparse(query='', fragment='')`) — esquema+path conservados porque los assets consumen ese campo como website navegable (booking_bar_gen, geo_playbook, optimization_guide, conditional_generator); el matching de onboarding ya era UTM-insensible (`_normalize_url` en ambos lados).
- `generate_hotel_id` (onboarding_controller): normaliza via urlparse con semántica idéntica a `_normalize_url` (no importable: main importa modules — dependencia inversa) → log "Phase 1 iniciada: hotel_hotelsalentoreal.com" sin UTM; compatibilidad total para URLs limpias (hotel_hoteltest.com, hotel_test.com).
- `agent_harness/memory.py` INTACTO (match exacto en `load_history`): la reutilización funciona sola al coincidir IDs — verificado end-to-end con MemoryManager(tmp_path): corrida grabada con UTM recuperada por URL limpia y viceversa; 2 corridas (A limpia + C UTM) = UNA identidad.
- Desviación de números de línea: el prompt citaba L3248/3394/3460 y L3542 — desplazados por el fix de SR-C; call sites reales en 3289/3435/3501 y helper en 3583 (mismo contenido, verificado 1:1 contra código vivo).
- Matiz de alcance: onboard NO usa target_id de memoria (0 call sites, verificado por grep); se aplicó higiene de la única identidad URL-side de onboard (URL persistida sin query) — los greps T4 quedan en 0 igualmente.
- Greps (T4): 0 `target_id=args.url` / `'target_id': args.url` en código (solo assertions del guardián estático); 0 `_normalize_url_for_matching` (solo patch documental de SR-B); 0 `replace()` sobre URL cruda dentro de `generate_hotel_id`. Evidencia: `evidence/FASE-SR-D/` (28 nuevos + 108 regresión passed, quick 6/6).

### FASE-SR-E
- (llenar al cerrar)

### FASE-SR-F
- (llenar al cerrar)

### FASE-SR-G
- (llenar al cerrar)

### FASE-SR-H
- (llenar al cerrar: corrida, smoke, evidencia)

### FASE-SR-VERIFY
- (llenar al cerrar: ACs, diff, lecciones)

### FASE-RELEASE-4.73.0
- (llenar al cerrar)
