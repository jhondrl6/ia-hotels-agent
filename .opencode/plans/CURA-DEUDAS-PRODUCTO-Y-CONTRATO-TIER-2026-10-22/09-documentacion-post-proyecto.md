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
