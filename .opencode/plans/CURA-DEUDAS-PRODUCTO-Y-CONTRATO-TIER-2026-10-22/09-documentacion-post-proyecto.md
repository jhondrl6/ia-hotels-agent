# Documentación Post-Proyecto — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> Acumulativo. **Fuente canónica del número por fase** — lo consume FASE-RELEASE. Cada fase completa su columna «Fase» al cerrar. Los demás cierres referencian este archivo, no re-transcriben cifras.

## Sección A: Módulos Nuevos

| Módulo | Archivos | Descripción | Fase |
|--------|----------|-------------|------|
| _(ninguno previsto: todas las curas son sobre módulos existentes)_ | — | — | — |

## Sección B: Funcionalidades Nuevas

| Feature | Módulo | Descripción | Fase |
|---------|--------|-------------|------|
| Render condicionado al `evidence_tier` | `commercial_documents` | Los 2 claims de totalidad detectados por el revisor emiten variante honesta con tier no-A; la propuesta y el diagnóstico comparten el contrato | FASE-B |
| Veredicto condicional con causa estructurada | `quality_gates/tribunal` | `APROBADO-CONDICIONAL` + `conditional_reason`: techo de analytics, onboarding incompleto o cláusulas no certificables | FASE-C |
| Contrato GBP unificado en dos caminos | `scrapers` / `utils` / `commercial_documents` | `get_detected_issues` y `PainSolutionMapper` comparten vocabulario; “sin schema” no se convierte en abandono de perfil | FASE-D |
| Lector único de benchmarks regionales | `utils` | Puente de esquema; cinco tablas derivadas o retiradas; verificador real cableado | FASE-E |
| Umbrales por semántica | `config` / módulos consumidores | Mínimo, oportunidad, banda de rúbrica y objetivo con nombre propio, sin colapsarlos en un valor único | FASE-F |
| Guardián por existencia de atributo | `tests` (superficie pública) | Extiende el guardián estático de nombres a existencia sobre la clase importada | FASE-A |
| Retiro de la ruta `spark` | `main.py` | El comando informa su retiro y no muere por `AttributeError`; el lector latente de `gap_analyzer` se corrige | FASE-A |
| Score GBP honesto | `scrapers` | Publica sobre `/90` y retira la rama API no implementada | FASE-H1 |
| Stub de Booking retirado | `scrapers` | `found=False` con `data_status=STUB_RETIRADO`; el scraper real del producto no se toca | FASE-H1 |

## Sección D: Métricas Acumulativas

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests nuevos (delta, par pre/post por fase — R2.3/R2.7) | FASE-A: **+7** (5334 → 5341); resta publicada en `evidence/…/FASE-A/baseline-pre-post.md` | FASE-A |
| Mutation checks con par rojo/verde en evidencia (R2.8) | 1 de 5 al cierre de FASE-A (AC5: guardián de existencia; `evidence/…/FASE-A/guardian-existencia-par-rojo-verde.txt`) | FASE-A |
| Corridas `v4complete` de este plan | 0 / 1 prevista (después de E2E-PRE) | FASE-E2E |
| Ensayos E2E-PRE sin inferencia | 0 / 1 previsto | FASE-E2E-PRE |
| Presupuesto por fase (unidad `tool_use`, corte «listo para revisión») | FASE-A: auto-reporte en `10-analisis` §Resumen, unidad `tool_use`, **no comparable** (instrumento legado `measure_iterations.py` no probado contra este runtime) | FASE-A |
| Tests nuevos (delta, par pre/post por fase — R2.3/R2.7) | FASE-B: **+8**; par y resta publicados en `evidence/…/FASE-B/baseline-pre-post.md` | FASE-B |
| Mutation checks con par rojo/verde en evidencia (R2.8) | 2 de 5 al cierre de FASE-B (AC1: el par de los 2 claims — propuesta y diagnóstico — cuenta como el check de AC1; `evidence/…/FASE-B/par-rojo-verde-claims.txt`) | FASE-B |
| Presupuesto por fase (unidad `tool_use`, corte «listo para revisión») | FASE-B: auto-reporte en `10-analisis` §Resumen, unidad `tool_use`, **no comparable** (instrumento legado `measure_iterations.py` no probado contra este runtime) | FASE-B |
| Tests nuevos (delta, par pre/post por fase — R2.3/R2.7) | FASE-C: **+7** (`tests/quality_gates/tribunal/test_conditional_reason.py`); resta publicada en `evidence/…/FASE-C/baseline-pre-post.md` | FASE-C |
| Mutation checks con par rojo/verde en evidencia (R2.8) | 3 de 5 al cierre de FASE-C (AC2: M1 literal viejo restaurado → 8 rojos; M2 causa eliminada → 6 rojos; `evidence/…/FASE-C/par-rojo-verde.md`) | FASE-C |
| Presupuesto por fase (unidad `tool_use`, corte «listo para revisión») | FASE-C: **no reportado** (la sesión no publicó la cifra); tope 60 `tool_use` **no verificable**; `measure_iterations.py` es legado | FASE-C |

## Sección E: Archivos Afiliados Actualizados

| Archivo | Cambio | Fase |
|---------|--------|------|
| `main.py` | Ruta `spark` retirada: `run_spark_mode` queda como centinela (informa retiro, exit 0); se retiran `_map_audit_to_spark_data`, `_spark_handler`, `_run_spark_legacy` y los helpers de región sin consumidores | FASE-A |
| `modules/analyzers/gap_analyzer.py` | Lector latente corregido (`FinancialFactors.get_superposition_factor()`); docstring de `analyze_with_claude` deja de afirmar el consumidor falso `main.py` | FASE-A |
| `tests/test_main_static_guards.py` | Guardián extendido a existencia de atributo sobre la clase importada (AST + import), con mutante rojo | FASE-A |
| `tests/test_spark_retirement.py` | Nuevo: retiro con diente (exit 0 + mensaje + sin `AttributeError`; reintroducción del lector roto = rojo por AST) | FASE-A |
| `tests/test_gap_analyzer_superposition_reader.py` | Nuevo: la rama fallback de `_basic_analysis` se recorre sin `AttributeError` | FASE-A |
| `.opencode/wiring_report.json` | Re-publicado con `validate_wiring.py --write-report` (contadores frescos tras los archivos nuevos) | FASE-A |
| `AGENTS.md` | **Aplicado** el 2026-10-22 con autorización del Operador: la fila de `spark` pasa de «⚠️ Deprecado» a «🚫 Retirado» (centinela, exit 0, `D19` cerrada por retiro) y la fila de `modules/generators/` se re-escribe con sus consumidores medidos. 2/2 líneas, EOL intacto; ver `10-analisis` §Seguimientos | FASE-A |
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Los 2 claims de totalidad pasan a render condicionado por tier: `{{if financial_evidence_tier == "A"}}` emite «Protección total para usted» / «Transparencia total» y `{{if financial_evidence_tier != "A"}}` la variante honesta «Protección para usted» / «Transparencia en cada cifra» | FASE-B |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Interpola `${garantias_titulo}` y `${garantias_cuerpo}` (strings precomputados por el generador, `safe_substitute`) en lugar de literales fijos | FASE-B |
| `modules/commercial_documents/v4_proposal_generator.py` | `_preprocess_conditionals` acepta `==` y `!=` en las condiciones del template (antes solo comparaba igualdad) | FASE-B |
| `modules/commercial_documents/v4_diagnostic_generator.py` | `_build_financial_placeholders` precomputa `garantias_titulo`/`garantias_cuerpo` según el tier resuelto (variante A vs variante honesta) | FASE-B |
| `tests/commercial_documents/test_fase_b_claims_tier_render.py` | Nuevo: 8 tests (render A/B+ de los 2 claims en propuesta y diagnóstico, diente del mutante, labels financieros intactos) | FASE-B |
| `.opencode/wiring_report.json` | Re-publicado con `validate_wiring.py --write-report` tras los archivos nuevos de FASE-B (contadores frescos; `--check` limpio) | FASE-B |
| `.opencode/LECCIONES-INDEX.md` y `.opencode/lecciones_index.json` | Re-publicados con `build_lesson_index.py` con autorización del Operador: el propio cierre de FASE-B los dejó vencidos y el guard de `triage_lesson_relevance.py` tumbaba 50 nodos (23 failed + 27 errors). `--check` de `EXIT=1` a `EXIT=0`; la re-publicación no añadió definiciones (398→398), citas sin definición (113→113) ni redefiniciones (33→33). Ver `evidence/…/FASE-B/baseline-pre-post.md` §1b y §5 | FASE-B |
| `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-B/` | Artefactos de la fase: `inventario-candidatas.txt`, `inventario_runner.py`, `mutation_pair_runner.py`, `par-rojo-verde-claims.txt`, `baseline-pre-post.md` y los crudos del `--quick` post-reparación, de la atribución de los 3 rojos, de la re-ejecución del fixture AC11 (`12 passed`; prosa intacta, sin actualización con justificación), del pytest de los 8 tests nuevos (`8 passed`) y de la suite completa post-cierre | FASE-B |
| `modules/quality_gates/tribunal/judge.py` | `VERDICT_CONDITIONAL` vale `APROBADO-CONDICIONAL`; `_compute_verdict` retorna `(verdict, conditional_reason)` con las 3 causas y un quinto parámetro `has_onboarding` (tri-estado); `evaluate`/`enrich` publican la causa y `finalize` la deriva al DTO | FASE-C |
| `modules/quality_gates/tribunal/outcome.py` | Vocabulario de la causa (`REASON_ANALYTICS_CEILING` / `REASON_ONBOARDING_INCOMPLETE` / `REASON_UNCERTIFIABLE_CLAUSES`, `CONDITIONAL_REASONS`); `TribunalOutcome.conditional_reason` + `acta_fields()`; `build_outcome` la transporta | FASE-C |
| `modules/quality_gates/tribunal/acta_writer.py` | Etiqueta del veredicto renombrada; el MD publica `Causa del condicional` con etiqueta humana — el caso de techo de analytics NO dice «Pendiente de onboarding» | FASE-C |
| `modules/quality_gates/tribunal/review_inputs.py` | `capture_review_inputs` recibe `has_onboarding` y lo publica en `review_input_manifest.json`; `ReviewInputs.has_onboarding` tri-estado (None = no transportado, DA-C3) | FASE-C |
| `main.py` | `capture_review_inputs(..., has_onboarding=has_onboarding)` — el dato real de la corrida viaja al tribunal | FASE-C |
| `tests/quality_gates/tribunal/test_conditional_reason.py` | Nuevo: 7 tests — las 3 causas leídas del `acta_revision.json` del writer real (R2.4), causa nula en veredictos no condicionales y literal viejo ausente del acta serializada | FASE-C |
| `tests/quality_gates/tribunal/test_judge.py`, `tests/quality_gates/tribunal/test_acta_version_desde_yaml.py`, `tests/quality_gates/tribunal/test_acta_serialization.py`, `tests/test_fase_0_ac20_evidencia_veredicto.py`, `tests/test_ac_g4_g5_multi_hotel_matrix.py` | Literal viejo → `APROBADO-CONDICIONAL` (las 6 ocurrencias de tests: docstrings y datos de prueba) | FASE-C |
| `.opencode/wiring_report.json` | Re-publicado con `validate_wiring.py --write-report` tras los archivos nuevos de FASE-C (`--check` limpio, digest conforme) | FASE-C |
| `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-C/` | Artefactos: `baseline-pre-post.md`, `par-rojo-verde.md`, `grep-literal-viejo-baseline_{pre,post}.txt`, `p65-intacta.txt`, crudos 01–04 (verde, M1, M2, verde restaurado), **05 pre-reparación (12/13: Wiring 727 vs 728)**, 06 (Wiring re-publicado), 07–10 (índice de lecciones pre/re-publicado/post y `--check` de Wiring), **11 final (13/13, EXIT=0)** y 12–13 (colección post/pre: 5513 vs 5506, +7) | FASE-C |
