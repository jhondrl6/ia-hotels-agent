# Plan Maestro — SR-PIPELINE-FIXES: Fixes del Pipeline v4complete tras E2E Salento Real

**ID del Plan**: SR-PIPELINE-FIXES-2026-08-27
**Fecha de concepción**: 2026-08-27
**Versión base**: v4.72.2 → **Versión objetivo**: v4.73.0 (minor — cambios funcionales en gates/propuesta/preflight)
**Fuente de contexto**: `.opencode/context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27.md` (6 hallazgos + N1–N4, re-validados 6/6 contra código vivo el 2026-08-27)
**Revisión causa-raíz**: 2026-08-28 — bucle de verificación contra código vivo, artefactos de corrida C y sitio vivo; H4/N4 RECLASIFICADOS (premisa original falsa), hallazgo H7 añadido, FASE-SR-E rediseñada (ver §1 y prompt SR-E)
**Lecciones fuente**: `.opencode/plans/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22/10-analisis-post-implementacion.md` (L-NC1–L-NC12) + lecciones nuevas L-SR1–L-SR5 del contexto
**Workflow rector**: `.agents/workflows/phased_project_executor.md` v2.16.0
**Reglas mandatorias**: R1 (1 fase por sesión) · R2 (máx. 60 iteraciones por fase) · R3 (scope de fase)

---

## 1. Problema

La prueba E2E de `v4complete` sobre Hotel Salento Real (https://www.hotelsalentoreal.com/, 2026-08-27) dejó el hotel en `NOT_READY`: 12/13 publication gates PASSED, coherencia 0.86 (≥ 0.8 ✅), WhatsApp VERIFIED — pero alineación propuesta-assets 43% (3/7) < 80%. Las causas raíz (verificadas contra código vivo):

| ID | Hallazgo | Ubicación código | Recomendación |
|----|----------|------------------|---------------|
| H1 ✅ | NameError `logger` en main.py (rama FASE-D S7) — YA CORREGIDO y comiteado (d8e509d) | main.py (~1777, ~2976) | — (solo guardián estático) |
| H2/N3 | `target_id` de memoria se construye desde URL raw → UTM fragmenta la memoria | main.py:3248/3394/3460, helper `_normalize_url()` en main.py:3542 | #3/#10 |
| H3 | Bloqueo estructural `proposal_asset_alignment` (3ª manifestación): propuesta promete del catálogo estático, matriz registra NO_BREACH, gate cuenta `missing` — 3 contabilizaciones del mismo hecho | `v4_proposal_generator.py` (L1248 "sin costo (fallback)"), `proposal_asset_alignment.py`, `publication_gates.py:862-903` | #1 |
| H4/N4 ⚠️ RECLASIFICADO (2026-08-28) | La "paradoja de confianza" (`pain_solution_mapper.py:889`, "0.00 < 0.8") solo afecta el DISPLAY del plan (`main.py:2411`); el orquestador regenera specs con `can_generate=True` (`v4_asset_orchestrator._solutions_to_asset_specs` ~L712-722). La generación fue detenida por el gate SitePresence (`exists_with_issues` → skip, `conditional_generator.py:110-127`), NO por el preflight. El mecanismo de la premisa original es falso → ver H7 | `conditional_generator.py`, `v4_asset_orchestrator.py` | #4/#11 (vía H7) |
| **H7** (causa raíz real de #4/#11) | **Falso negativo del audit + doble contabilidad**: el sitio SÍ tiene 2 schemas Hotel (uno en JSON-LD formato ARRAY); `rich_results_client` no soporta arrays → `AttributeError: 'list' object has no attribute 'get'` tragado por `test_url` → `total_schemas=0` (falso) → pain `no_hotel_schema` es FALSO POSITIVO. Además `EXISTS_WITH_ISSUES` bloquea generación ("existe") pero no cuenta como `present_in_production` en alignment ("no existe") — doble contabilidad (viola L-SR3) | `rich_results_client.py` (~L96-220, ~L497-547), `v4_comprehensive.py:680-697`, `site_presence_checker.py` (~L76-82), `conditional_generator.py:110-127`, `pain_solution_mapper.py` (~L393-399) | #4/#11 (SR-E rediseñada) |
| H5 | Varianza del plan de assets entre corridas (7→5 brechas; `low_ia_readiness` y `ai_crawler_blocked` ausentes en C de forma determinista, no por score de robots) | `pain_solution_mapper.py` (hipótesis), caches | #5 |
| H6 | PageSpeed API key inválida (OPS) + `CG-CLAIM-VS-EVIDENCE` BLOCKING sin ciclo de corrección + CG-TIER-CONSISTENCY ('B' vs 'D') + CG-TECH-JARGON | `commercial_gate.py:538-595, 665-709, 786-812`, config | #2/#6/#8 |
| N1 | G9 divergente en el MISMO run: `gate_report` unresolved=4 vs `delivery_quality_report` unresolved=1 (dos caminos: `alignment_result.py:86` `len(report.missing)` vs `alignment_result.py:134/139` `sum(...)`) | `alignment_result.py`, `delivery_quality_report.py:235` | #9 |

**Impacto comercial**: el bloqueo recurrente de `proposal_asset_alignment` (Zione jul-2026, Salento 18:03 y 18:30) impide publicar entregables válidos; los claims falsos se publican pese a ser detectados.

## 2. Objetivo

Resolver los seguimientos abiertos del CONTEXT (recomendaciones #1-#5, #8-#11) con una única ejecución de verificación `v4complete` al final del plan sobre **Hotel Salento Real** (https://www.hotelsalentoreal.com/), con análisis post-implementación que certifique que los fixes fueron superados y capture lecciones aprendidas.

**Criterio de éxito (CONTEXT §9)**: una corrida v4complete de Salento Real con `readiness: READY_FOR_PUBLICATION` y 0 falsos claim-fact gates, **sin tocar la capa financiera** (determinista, intacta).

**Alcance IN**: `modules/quality_gates/` (alignment_result, publication_gates, delivery_quality_report, commercial_gate), `modules/asset_generation/` (proposal_asset_alignment, site_presence_checker, conditional_generator, asset_catalog consumo), `modules/commercial_documents/` (v4_proposal_generator, pain_solution_mapper preflight), `modules/data_validation/external_apis/rich_results_client.py` (fix parser JSON-LD array — H7), `modules/auditors/v4_comprehensive.py` (propagación error_message — H7), `main.py` (target_id), `modules/orchestration_v4/onboarding_controller.py` (`generate_hotel_id` — contamina hotel_id del log Phase 1), tests, docs oficiales.
**Alcance OUT**: capa financiera (`modules/financial_engine/` — determinista, INTACTA), detección de pains, ROADMAP.md, outputs históricos en `output/` y `evidence/`, rotación de secretos (PageSpeed key = instrucción OPS documentada, no código).

## 3. Estructura de Fases

| Fase | Fixes | Contenido | Archivos principales | Modo de ejecución | Estimación |
|------|-------|-----------|----------------------|-------------------|------------|
| FASE-SR-A | N1/#9 | Helper único `AlignmentResult.compute_unresolved()` para gate_report + delivery_quality_report + test estático guardián L-SR1 | `alignment_result.py`, `publication_gates.py`, `delivery_quality_report.py` | DIRECTO | 45-60 min |
| **FASE-SR-B** ⚠️ | #1 | **Unificación promesa/matriz/gate**: propuesta deriva del pain_ledger + present_in_production; gate excluye NO_BREACH del denominador; taxonomía única de estados | `v4_proposal_generator.py`, `proposal_asset_alignment.py`, `publication_gates.py` | DIRECTO (decisión arquitectónica) | 60-90 min |
| FASE-SR-C | #2 | Self-healing loop para `CG-CLAIM-VS-EVIDENCE`: regenerar con `suggestion` del gate + re-validar; persistencia → BLOCKED real | `commercial_gate.py`, flujo de regeneración (orchestration) | DIRECTO | 60-90 min |
| FASE-SR-D | #3/#10 | Canonicalizar URL antes de construir `target_id` (helper `_normalize_url` existente — L16: el gap está en el caller) + `generate_hotel_id` de `onboarding_controller.py:339-350` (sanitiza URL cruda → hotel_id contaminado del log Phase 1) | `main.py`, `modules/orchestration_v4/onboarding_controller.py`, `agent_harness/memory.py` (solo lectura) | DIRECTO | 45-60 min |
| FASE-SR-E | #4/#11 (H7) | **Rediseñada 2026-08-28**: fix falso negativo schema (JSON-LD array en `rich_results_client` + propagación `error_message` al audit) + contabilización única `exists_with_issues` → `present_in_production` + fallback catálogo residual D-PF3 (ausencia genuina) | `rich_results_client.py`, `v4_comprehensive.py`, `site_presence_checker.py`, `publication_gates.py`/alignment, `pain_solution_mapper.py` | DIRECTO | 60-90 min |
| FASE-SR-F | #5/#6 | Investigación varianza plan de assets (7→5) con fix mínimo si procede + verificación config PageSpeed (OPS) | `pain_solution_mapper.py` (investigación), `config/` (lectura) | DIRECTO | 45-60 min |
| FASE-SR-G | #8 | Display: CG-TIER-CONSISTENCY (texto derivado de fuente financiera) + CG-TECH-JARGON (lenguaje de negocio en vista gerencia) | `commercial_gate.py`, generadores de display | DIRECTO | 30-45 min |
| FASE-SR-H | E2E | **ÚNICA ejecución v4complete Salento Real** + preservación baseline + evidencia + smoke 7 checks | `output/salentoreal_final_v4c/`, `evidence/FASE-SR-H/` | **DELEGATE_TASK** (subagente terminal) | 30 min + corrida 5-10 min |
| FASE-SR-VERIFY | Verificación | AC1-AC13 + diff antes/después + lecciones | `10-analisis-post-implementacion.md` | DIRECTO (no delegable, §4.6) | 45-60 min |
| FASE-RELEASE-4.73.0 | Docs | Version bump + CHANGELOG + GUIA_TECNICA + validaciones E1-E8b | `VERSION.yaml`, docs oficiales | **DELEGABLE** (subagente) | 45 min |

**Orden justificado**: SR-A precede a SR-B (mismo archivo `alignment_result.py`; el helper de conteo es insumo de la unificación). SR-C precede a SR-G (ambos tocan `commercial_gate.py`). SR-E precede a SR-F (ambos tocan `pain_solution_mapper.py`). SR-H depende de TODAS las anteriores. SR-VERIFY y RELEASE dependen de SR-H.

## 4. Fase de Mayor Complejidad Técnica: FASE-SR-B

**FASE-SR-B es la fase de mayor complejidad del plan (MÁXIMA).** Justificación:

1. **Decisión arquitectónica cross-module** (lección DT-3 del executor): unifica 4 consumidores con taxonomías parcialmente divergentes (`v4_proposal_generator.py`, `proposal_asset_alignment.py`, `publication_gates.py`, `delivery_quality_report.py`). Requiere entender el contexto completo de todas las implementaciones → NO delegable a subagente aunque sea puro código.
2. **Taxonomía de estados a unificar**: `LINKED | MISSING_ASSET | NO_BREACH | GENERIC_DRAFT | PRESENT_IN_PRODUCTION`. El concepto `actionable` ya existe en `proposal_asset_alignment.py:783-789` (excluye NO_BREACH) — la unificación debe REUTILIZARLO, no crear un tercer criterio (L-NC10: nunca dos criterios en paralelo).
3. **Debe respetar decisiones ya implementadas**: el fix B7 de REFACTOR-COHERENCIA (botón WhatsApp fuera de "Servicios adicionales" sin brecha, signal `breach_by_asset`) — la nueva fuente de promesa no debe regresar a prometer servicios sin pain ni presencia.
4. **Riesgo de regresión concentrado**: toca el gate que bloqueó 3 corridas E2E y el generador de la propuesta (documento comercial cliente).
5. **Soporta la mayoría de los ACs**: AC1, AC2 (+AC3 con el helper de SR-A, +AC11/AC12 en el E2E).

## 5. Cumplimiento R3 (Scope de Fase) y Presupuesto de Complejidad — Análisis por Fase

Escala: `Baja → Baja-Media → Media → Media-Alta → Alta → MÁXIMA` (misma del plan CREDIBILIDAD-NUMERICA §3 y REFACTOR-COHERENCIA-NARRATIVA §5).

| Fase | Tareas | Comandos largos | Complejidad | ¿Cumple R3? |
|------|--------|-----------------|-------------|-------------|
| SR-A | 4 (investigar, helper+integración, test estático AST, tests+greps+docs) | 0 | Media (unificar 2 caminos de conteo + guardián AST nuevo) | ✅ (máx. 4 + 0) |
| **SR-B** | 4 (investigar contratos, implementar 3 partes, tests de contrato, greps+docs) | 0 | **MÁXIMA** (ver §4: decisión cross-module, 4 consumidores, taxonomía única) | ✅ |
| SR-C | 4 (investigar flujo, implementar loop, tests, greps+docs) | 0 | Alta (nuevo mecanismo self-healing con re-validación, escalado y guard anti-bucle) | ✅ |
| SR-D | 4 (investigar callers incl. `generate_hotel_id`, implementar canonicalización, tests anti-fragmentación, docs) | 0 | Media (multi-caller con helper existente; riesgo en `_detect_region_from_url`) | ✅ |
| SR-E | 4 (reproducir cadena de fallo con tests rojos, fix parser+contabilización, tests con fixture real, greps+docs) | 0 | Alta (fix cross-module: parser + audit + SitePresence + alignment; revisar §4 del prompt SR-E) | ✅ |
| SR-F | 4 (investigar varianza, fix mínimo o seguimiento, PageSpeed OPS, docs) | 0 | Media (investigación forense entre corridas; outcome condicional pre-decidido) | ✅ |
| SR-G | 4 (fix tier, fix jerga, tests, docs) | 0 | Baja-Media (2 fixes display acotados, L30/L27 ya catalogadas) | ✅ |
| SR-H | 3 (baseline+corrida, evidencia+smoke, docs) | 1 (v4complete) | Media (ejecución: corrida irrepetible, disciplina de evidencia) | ✅ (máx. 3 + 1) |
| SR-VERIFY | 4 (ACs vs output, diff antes/después, matriz+lecciones, log+validaciones) | 0 | Media (juicio analítico sobre output real, sin cambios de código) | ✅ |
| RELEASE | 4 (bump+sync, CHANGELOG+GUIA, validaciones E1-E8b, log) | 0 | Baja (mecánica documental con scripts) | ✅ |

## 6. Mapa de Delegación (delegate_task)

| Fase | ¿Delegable? | Justificación (regla del executor) |
|------|-------------|-------------------------------------|
| SR-A | ❌ NO | Código+tests puro con venv → ejecución directa (§Regla-de-Decisión-código+tests) |
| SR-B | ❌ NO | Decisión arquitectónica cross-module (4 consumidores, taxonomías) → directa, PREVALECE sobre eficiencia (lección DT-3, §Regla-de-Decisión) |
| SR-C | ❌ NO | Diseño de mecanismo nuevo cross-module (gates + regeneración) + código+tests → directa |
| SR-D | ❌ NO | Código+tests con venv → directa (regla venv prevalece sobre paralelismo) |
| SR-E | ❌ NO | Fix cross-module con decisión de semántica (parser + contabilización única de presencia + arbitraje de detectores) → directa |
| SR-F | ❌ NO | Investigación forense con juicio sobre corridas reales → directa (análogo a VERIFY) |
| SR-G | ❌ NO | Código+tests → directa |
| SR-H | ✅ SÍ | v4complete vía subagente: `delegate_task(timeout=900, notify_on_complete=True, toolsets=["terminal"])` (§Protocolo-de-Subagente-para-v4complete). El parent preserva baseline, ejecuta el Protocolo de Evidencia Proactiva, verifica smoke y documenta |
| SR-VERIFY | ❌ NO | §4.6: "Modo de ejecución: DIRECTO (agente principal). No delegable — requiere juicio y contexto completo del plan" |
| RELEASE | ✅ SÍ | Solo edita YAML/MD + ejecuta scripts stdlib → delegable (TIP §Paso-7; confirmado en BUGS-ONBOARDING-ADR: 18 tool calls, ~4 min). El parent verifica resultados |

## 7. Criterios de Aceptación (AC1-AC13) — Mapeo a Fases

| AC | Criterio | Implementa | Verifica |
|----|----------|-----------|----------|
| AC1 | El gate `proposal_asset_alignment` NO bloquea por servicios "sin costo (fallback)": NO_BREACH queda fuera del denominador de `coverage_ratio`; en la corrida final coverage_ratio ≥ 0.80 | SR-B | SR-H/VERIFY |
| AC2 | La propuesta deriva sus servicios prometidos del pain_ledger + present_in_production (fuente única, L27/L-NC10/L-SR3); servicios sin pain ni presencia NO se prometen como comprometidos | SR-B | SR-H/VERIFY |
| AC3 | En el MISMO run, `gate_report` y `delivery_quality_report` reportan el mismo `unresolved` (helper único); mensaje G9 coherente con sus propios datos (corrección del 4-vs-1) | SR-A | SR-H/VERIFY |
| AC4 | Claims contradichos por evidencia se corrigen o bloquean: en la corrida final, 0 claims "no aparece" contradiendo GBP propio publicados (o BLOCKED real con documentos retenidos) | SR-C | SR-H/VERIFY |
| AC5 | `target_id` canónico: unit tests prueban URL con UTM ≡ URL limpia ≡ mismo target_id; el log de la corrida final muestra target_id sin query string | SR-D | SR-H/VERIFY |
| AC6 | Detección de schema correcta: el audit detecta los schemas Hotel del sitio (incl. JSON-LD formato ARRAY — fixture real Salento Real ≥ 2 schemas); el pain `no_hotel_schema` NO se genera (falso positivo eliminado de raíz); `exists_with_issues` cuenta como `present_in_production` (contabilización única) | SR-E | SR-H/VERIFY |
| AC7 | `coherence_validation` sin "Assets no implementados: hotel_schema"; coherence score ≥ 0.8; caso residual de ausencia GENUINA cubierto por fallback del catálogo (D-PF3) con `justified_skip` trazable | SR-E | SR-H/VERIFY |
| AC8 | Varianza documentada: informe con hipótesis verificada sobre por qué el plan de assets varió 7→5 entre corridas (o fix aplicado con test) | SR-F | VERIFY |
| AC9 | CG-TIER-CONSISTENCY: tier de frontmatter == tier del texto == fuente financiera en la corrida final (0 WARNING de tier); CG-TECH-JARGON reducido vs baseline | SR-G | SR-H/VERIFY |
| AC10 | 0 regresión financiera: escenarios idénticos al baseline corrida C ($6.57M / $4.04M / $1.26M COP) | — (restricción global) | SR-H/VERIFY |
| AC11 | `readiness = READY_FOR_PUBLICATION` en la corrida final (criterio de éxito CONTEXT §9) | todas | SR-H/VERIFY |
| AC12 | No se genera `BLOCKED_BY_GATES.md`; documentos cliente 01/02 presentes en el output final; ZIP no abortado por gates | todas | SR-H/VERIFY |
| AC13 | Guardián estático L-SR1 presente y pasando: main.py compila, `grep "logger\." main.py` = 0, AST no referencia símbolos prohibidos | SR-A | VERIFY |

## 8. Restricciones y Guardas

- **Capa financiera INTACTA**: NO modificar `modules/financial_engine/` ni constantes de precios; AC10 certifica igualdad de escenarios vs corrida C.
- **Outputs históricos** en `output/` y `evidence/` NO se modifican (registro de lo que el sistema produjo). El baseline de comparación (corrida C, 18:30) se COPIA a `evidence/FASE-SR-H/baseline/` antes de la corrida final.
- **Decisión B7 respetada**: la unificación de SR-B no debe volver a prometer el botón de WhatsApp (ni ningún servicio) sin pain ni señal de presencia (D-NC7 del plan anterior).
- **Fuente única de verdad**: toda promesa/estado/conteo deriva de pain_ledger + SitePresence; nunca de catálogos estáticos en paralelo (L-NC10/L-SR3/L27).
- **L-SR1 (ramas no ejercitadas)**: tras cada fase, grep de símbolos sospechosos en código nuevo (`logger\.`, imports no usados); smoke de ramas nuevas al menos una vez; el guardián estático AST (SR-A) queda como prevención permanente.
- **L2 (grep de residuos)**: cada fase termina con greps de strings/variables que debieron desaparecer (0 matches).
- **L3 (tests de contrato)**: tests contra fuente dinámica, no valores fijos.
- **`log_phase_completion.py` SIN `--release`** en fases intermedias (check "Prompts No Release" de `run_all_validations.py`). Solo FASE-RELEASE usa el marker `FASE-RELEASE-4.73.0`.
- **Suites pytest seguras** (memoria 2026-08-03): NUNCA `pytest tests/commercial_documents tests/data_validation` en un solo proceso; ejecutar archivos específicos en procesos aislados secuenciales con salida redirigida (`> temp\fase_sr_x_tests.txt 2>&1`); los pipes de PowerShell pueden colgar la captura.
- **Python path**: `./venv/Scripts/python.exe` (CONTRIBUTING §Reglas-Contractuales).
- **Nombre del helper**: para target_id usar `_normalize_url` (main.py:3542). `_normalize_url_for_matching` NO existe (grep = 0) — cualquier referencia a él es un error del contexto original ya corregido.

## 9. Ejecución Única de v4complete (FASE-SR-H)

- **URL**: https://www.hotelsalentoreal.com/ (limpia, sin UTM — la equivalencia con UTM queda certificada por los unit tests de SR-D).
- **Output**: `--output output/salentoreal_final_v4c` (dir aislado y alternativo → ejercita la rama FASE-D S7 corregida del fix H1; el hotel no tiene onboarding yaml → la rama fallback se ejecuta, verificando L-SR1 en vivo).
- **Baseline ANTES de la corrida**: copiar artefactos de la corrida C (`output/test_salentoreal_v4c/v4_complete/...`: gate_report, delivery_quality_report, proposal_asset_matrix, pain_ledger_resolved, coherence_validation, commercial_gates_report, 01/02 .md si existen) a `evidence/FASE-SR-H/baseline/`.
- **ÚNICA ejecución del plan**. Si falla: NO re-ejecutar; aplicar el Protocolo de Recuperación de Agotamiento del executor (evidencia primero, checkpoint, sesión fresca).
- Smoke 7 checks post-corrida: (1) `v4_complete_report.json` con readiness; (2) gate_report 13 gates con `proposal_asset_alignment` PASSED; (3) coherence ≥ 0.8; (4) `hotel_schema` cubierto por PRESENCIA (el sitio tiene schemas reales, incl. array JSON-LD — el audit detecta ≥ 1 schema Hotel, el pain `no_hotel_schema` no aparece o queda resuelto por presencia; NO se espera "asset generado", la generación es el comportamiento incorrecto aquí); (5) `target_id` sin UTM; (6) 01/02 presentes, sin BLOCKED_BY_GATES; (7) delivery_quality PASS con `unresolved` coherente gate↔delivery.

## 10. Entregables del Plan

1. Fixes #1, #2, #3/#10, #4/#11, #5 (o seguimiento documentado), #8, #9 implementados con tests (~+30 tests estimados, 0 regresiones).
2. Guardián estático L-SR1 permanente contra símbolos no definidos en ramas no ejercitadas.
3. Evidencia E2E en `evidence/FASE-SR-H/` (baseline corrida C + corrida final Salento Real).
4. Matriz AC1-AC13 completa + lecciones aprendidas (mínimo 3/fase) en `10-analisis-post-implementacion.md`.
5. Release v4.73.0 documentada (CHANGELOG + GUIA_TECNICA + VERSION.yaml + sync 6 archivos).

## 11. Cómo Retomar una Sesión

1. Leer `README.md` de este plan (tabla de progreso).
2. Leer `06-checklist-implementacion.md` (estado de cada fase).
3. Leer `dependencias-fases.md` (conflictos y checkpoint).
4. Ejecutar el prompt `05-prompt-inicio-sesion-fase-{X}.md` de la siguiente fase pendiente en UNA sesión nueva de agente.
