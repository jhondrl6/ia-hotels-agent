# Análisis Post-Implementación — RC1-RC2-ENTREGA-COHERENTE

> **Estado**: FASE-D completada (2026-08-05) — RC1 + RC2-a + RC2-b resueltos a nivel código; RC3 (FASE-E) pendiente.
> **Plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04
> **Versión objetivo**: v4.71.0
> **Baseline auditado**: run 2026-08-04 12:44:43 (Zi One Luxury, coherence 0.9168, evidence_tier B+)
> **Run de verificación E2E**: FASE-F (pendiente) — `output/v4_verify_4.71.0`
> **Plan anterior**: COHERENCIA-MODULO-ENTREGA-2026-08-03 (15 lecciones aprendidas capitalizadas)

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-A | 2026-08-05 | ✅ | 1 sesión (~30/60) | No (directo) | Cuarentena 3 archivos patológicos (40 tests). Tests collected: 3215 → 3175. Lista segura: 13 archivos PASS. 2 archivos con fallos preexistentes (no patológicos). `pytest.ini` con `--ignore` específicos (CR-8). Ver L16-L17. |
| FASE-B | 2026-08-05 | ✅ | 1 sesión (~20/60) | No (directo, no delegable — DT-3) | RC1: `_build_dynamic_breach_map` + cableado `opportunity_scores` en main.py. Eliminados `BREACH_BY_ASSET` (N10/N17) y hardcode L1250 (N18); org_schema condicional (N19). 9 tests nuevos PASS, lista segura 208 passed / 0 regresiones, verificación estática vs run 124443 PASS. Ver L18-L20, DEC-B1-B3. |
| FASE-C | 2026-08-05 | ✅ | 1 sesión (~15/60) | No (directo) | RC2-a: split oraciones + filtro condicionales CG-CLAIM-VS-EVIDENCE (N11) + cableado frontmatter_tier/text_tier en CG-TIER-CONSISTENCY (N15). 20 tests nuevos PASS, quality_gates 322 passed / 0 regresiones, preexistentes estables (12 failed). Ver L21-L23, DEC-C1. |
| FASE-D | 2026-08-05 | ✅ | 1 sesión (~15/60) | No (directo, 3 tracks serie) | RC2-b: `_is_excluded_from_zip` + `_get_latest_run_timestamp` (N16/N21) + fallback loader onboarding (S7) + occupancy label priority (S5). 23 tests nuevos PASS, delivery 69 passed, quality_gates 366 passed, preexistentes estables (12 failed). Ver L24-L26. |
| FASE-E | ⬜ Pendiente | — | — | Sí (solo docs, sin imports) | |
| FASE-F | ⬜ Pendiente | — | — | Sí parcial (v4complete background) | |
| FASE-RELEASE | ⬜ Pendiente | — | — | Sí (delegate_task) | |

### Evidencia v4complete FASE-F (llenar)

| Hotel | Output | evidence_tier | coherence | ZIP sin históricos | Onboarding inyectado |
|-------|--------|---------------|-----------|:---:|:---:|
| Zi One Luxury | ⬜ | ⬜ | ⬜ (≥ 0.8) | ⬜ | ⬜ |

---

## Matriz de Verificación de Causas Raíz (llenar en FASE-F)

### RC1 — Fuente de verdad de costos aplicada a medias

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N10 | Costos hardcodeados en propuesta | Costos desde `opportunity_scores` del run | ⬜ | ⬜ |
| N17 | Mapa inverso `asset_type → brecha_id` | Construido desde `pain_solution_mapper.PAIN_SOLUTION_MAP` | ⬜ | ⬜ |
| N18 | Hardcode L1250 (servicio fantasma) | Eliminado o parametrizado | ⬜ | ⬜ |
| N19 | `ASSET_TO_PAIN_ID` solo cubre 6/8 | Mapa inverso cubre 8/8 | ⬜ | ⬜ |

### RC2 — Gates comerciales con inputs no cableados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N11 | CG-CLAIM-VS-EVIDENCE falso positivo | No dispara con texto condicional "si...no aparece" | Split oraciones + `_CONDITIONAL_MARKERS` — condicional→PASS, factual+good_gbp→FAIL | ✅ |
| N15 | CG-TIER-CONSISTENCY pasa vacuo | Valida inputs reales o falla explícitamente | `_check_tier_consistency` falla con None; caller cablea `frontmatter_tier`+`text_tier` vía `_extract_text_tier()` | ✅ |
| N16 | ZIP con `commercial_gates_report` BLOCKING | Sin reports BLOCKING junto a doc PASSED | `_is_excluded_from_zip()` excluye `commercial_gates_report*`; verificado en ZIP de test | ✅ |
| N21 | ZIP con artefactos de runs anteriores | Solo artefactos del run actual | `_get_latest_run_timestamp()` usa mtime más reciente de v4_audit (tolerancia 60s); verificado con 2 runs separados | ✅ |

### RC3 — Higiene documental sin enforcement

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| R3.1 | Prompts con `--release` en fases intermedias | Sin `--release` en A-F | ⬜ | ⬜ |
| R3.2 | Conteos desactualizados | Conteos desde fuente viva (L8) | ⬜ | ⬜ |
| R3.3 | Citas driftadas | Referencias verificadas | ⬜ | ⬜ |
| R3.4 | Evidencia no preservada | `evidence/FASE-F/` completo | ⬜ | ⬜ |

### Seguimientos heredados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| S5 | Occupancy label "regional" residual | Label coherente con fuente real | `data_sources.occupancy` prioriza `"onboarding"` > `"regional"` > `"default"`; verificado con HotelFinancialData + ScenarioCalculator._trace_data_sources | ✅ |
| S7 | Loader onboarding sin fallback | Fallback a `output/clientes` con `--output` alternativo | main.py: fallback a `output/clientes` si `{--output}/clientes` no tiene YAML; verificado con 7 tests | ✅ |

---

## Lecciones Aprendidas (llenar — mínimo 3 por fase completada)

Formato por lección: **qué pasó / por qué / qué lo previene** + evaluación de pertinencia para futuras releases.

### Lecciones capitalizadas del plan anterior (L1-L15)

Estas lecciones ya fueron aplicadas en el diseño de este plan:

| Lección | Aplicación en este plan |
|---------|------------------------|
| L1/L11: tests patológicos bloquean equipo | FASE-A: cuarentena; NUNCA suite completa de `commercial_documents`/`financial_engine` |
| L2: validaciones documentales ≠ fallos tests | Clasificar antes de re-ejecutar suites; Version Sync → `sync_versions.py` |
| L3/L9: `log_phase_completion` sin `--release` | Fases A-F: SIN `--release`; RELEASE: con `--release 4.71.0` |
| L4/L5: forense baseline + backup | Protocolo `Copy-Item` + `git checkout HEAD --` en FASE-B |
| L6: pytest → archivo, no pipe | Regla transversal en todos los prompts |
| L7: evidencia mixta dinámica+estática | FASE-B T3: verificación contra run 124443 |
| L8: conteo desde `git diff tests/` | Regla transversal (L8) |
| L10: `git diff` tras intervención usuario | Regla transversal (L10) |
| L12: tracks mismo archivo → integrar | FASE-D: 3 tracks tocan archivos distintos → delegable |
| L13/L14: loader + clasificar fallo antes retry | FASE-F T0: verificar S7 en aislamiento |
| L15: grep UTF-8 vs Select-String | Regla transversal (L15) |

---

### Lecciones nuevas de este plan (L16+)

#### L16 (FASE-A) — Cuarentena con `--ignore` específicos vs `norecursedirs` global (CR-8)
- **Qué pasó**: se necesitaba excluir 3 archivos patológicos de la colección sin afectar los 22 archivos que YA estaban en `_archived_broken_tests/`.
- **Por qué**: añadir `norecursedirs = _archived_broken_tests` en `pytest.ini` habría excluido TODOS los archivos del directorio (incluyendo los 22 que sí se recolectan), reduciendo el conteo collected mucho más de lo esperado y rompiendo tests legítimos.
- **Qué lo previene**: usar `--ignore` específicos para cada archivo patológico en `addopts` de `pytest.ini`. Esto excluye solo los 3 archivos objetivo, manteniendo la recolección del resto de `_archived_broken_tests/`. Verificación: diferencia collected = 40 tests exactos (32 + 4 + 4), no más.
- **Pertinencia**: **INCLUIR** — aplica a cualquier cuarentena futura donde coexistan archivos rotos y legítimos en el mismo directorio.

#### L17 (FASE-A) — Diagnóstico de patológicos sin ejecutarlos completos
- **Qué pasó**: se necesitaba confirmar la causa probable de cada archivo patológico sin ejecutarlos (habría bloqueado el equipo).
- **Por qué**: los síntomas (fuga ~8GB, cuelgue indefinido, fallos en cascada) ya estaban documentados en L1/L11 del plan anterior, pero se requería confirmar el patrón causante específico de cada archivo.
- **Qué lo previene**: (a) leer el código de cada test (grep/read) para identificar el patrón (fixtures que instancian el generador completo, generación combinatoria, bucles); (b) si se necesita ejecutar algo, SOLO tests individuales con timeout corto (`pytest archivo.py::test_x -x --timeout=60 > temp/fase_a_diag.txt 2>&1`); (c) NUNCA ejecutar el archivo completo sin timeout.
- **Pertinencia**: **INCLUIR** — protocolo estándar para diagnosticar tests patológicos sin bloquear el equipo.

#### L18 (FASE-B) — La inversión de un mapa pain→assets NO es un mapeo asset→pain seguro
- **Qué pasó**: la primera implementación invertía `PAIN_SOLUTION_MAP[bid]["assets"]` sin restricción y el test "llms_txt sin costo" falló: `ai_crawler_blocked` (brecha de otro dominio, rank 7 en el run) también lista `llms_txt` como asset, asignándole un costo de $899.000 que el plan esperaba ausente.
- **Por qué**: un asset puede ser solución legítima de varios pains en el catálogo, pero la tabla comercial solo debe atribuir al servicio la brecha que ese servicio resuelve de cara al cliente (mapeo auditado 1:N acotado), no cualquier brecha que lo mencione.
- **Qué lo previene**: definir candidatos auditados por servicio (lista explícita multi-brecha solo donde hay ambigüedad real: optimization_guide, whatsapp_button) y desempatar por presencia+rank en opportunity_scores; además una defensa de drift que warnea si un candidato deja de existir en `PAIN_SOLUTION_MAP`. Escribir el test de consistencia ANTES de verificar contra el run real fue lo que lo detectó en la iteración 1.
- **Pertinencia**: **INCLUIR** — cualquier mapeo inverso de un mapa 1:N necesita una capa de selección semántica auditada antes de usarse en documentos de cara al cliente.

#### L19 (FASE-B) — Parametrizar sin cablear el origen de datos deja el fix inerte
- **Qué pasó**: el generador de propuesta no tenía acceso a `opportunity_scores` en ningún punto de su signature (`generate()` → `_prepare_template_data()` → tabla); el fix requirió tocar 3 niveles de signature + `main.py` (FASE 3.5), no solo la tabla.
- **Por qué**: la fuente viva la produce `diagnostic_gen._compute_opportunity_scores()` en el orquestador; sin el cableado, la parametrización habría quedado con fallback permanente (tabla vacía de costos) y el bug visual persistiría.
- **Qué lo previene**: al parametrizar una cifra, trazar primero el camino completo de datos (productor → parámetros → punto de render) y verificar con el run real (T3) que la cifra renderizada coincide byte a byte con el JSON del pipeline.
- **Pertinencia**: **INCLUIR** — aplica a todo fix de "fuente de verdad aplicada a medias": la mitad faltante suele ser el cableado, no la fórmula.

#### L20 (FASE-B) — Comentarios que citan símbolos eliminados disparan gates de grep
- **Qué pasó**: tras eliminar `BREACH_BY_ASSET`, el comentario que explicaba el reemplazo mencionaba el nombre del dict eliminado y el criterio de aceptación (`grep BREACH_BY_ASSET → 0 hits`) falló falsamente.
- **Por qué**: los criterios de aceptación basados en grep no distinguen código de comentarios.
- **Qué lo previene**: al eliminar un símbolo, redactar los comentarios de reemplazo sin citar el literal (ej: "reemplaza el mapa estático hardcodeado"); correr el grep de aceptación inmediatamente después del edit, no al final.
- **Pertinencia**: **INCLUIR** — regla general para cualquier refactor con criterios de aceptación grep-based.

#### L21 (FASE-C) — Regex sobre texto completo sin parseo de oraciones genera falsos positivos estructurales
- **Qué pasó**: `CG-CLAIM-VS-EVIDENCE` aplicaba un regex (`[Nn]o\s+aparece|...`) sobre el texto COMPLETO del diagnóstico. El texto condicional "si su web no tiene los datos correctos, no aparece en la respuesta" matcheaba y disparaba un falso positivo BLOCKING, aunque la oración era condicional (no factual).
- **Por qué**: el regex no distinguía entre afirmaciones factuales ("El hotel no aparece en Google") y cláusulas condicionales ("si...no aparece"). El patrón condicional es común en diagnósticos (recomendaciones, advertencias).
- **Qué lo previene**: split por oraciones ANTES del regex + filtro de marcadores condicionales (`_CONDITIONAL_MARKERS`). Si todas las oraciones que matchean son condicionales → PASS. Si al menos una es factual → evaluar contra evidencia.
- **Pertinencia**: **INCLUIR** — cualquier gate que use regex sobre texto libre debe considerar la estructura oracional; de lo contrario, los falsos positivos crecen con cada nuevo diagnóstico.

#### L22 (FASE-C) — Gate que pasa vacuo con `passed=True` es un bug silencioso
- **Qué pasó**: `CG-TIER-CONSISTENCY` siempre retornaba `passed=True` cuando `frontmatter_tier` o `text_tier` eran None (que era SIEMPRE, porque el caller no los pasaba). El gate decía "Sin datos de tier para comparar" y pasaba — enmascarando la ausencia de cableado.
- **Por qué**: la semántica `passed=True + "sin datos"` es ambigua: parece "no hay problema" cuando en realidad es "no pude verificar". Este patrón se repite en gates que reciben opcionales.
- **Qué lo previene**: cuando un gate NO puede validar por falta de inputs, debe fallar explícitamente (`passed=False` con mensaje claro). El fix del caller (cablear los inputs) es la solución correcta, no relajar el gate.
- **Pertinencia**: **INCLUIR** — diseño de gates: `passed=True` solo cuando se validó exitosamente; nunca como default por falta de datos.

#### L23 (FASE-C) — El caller debe cablear los parámetros del gate, no el gate inventar defaults
- **Qué pasó**: `validate_diagnostic()` en `v4_diagnostic_generator.py` no pasaba `frontmatter_tier` ni `text_tier` a `validate_diagnostic()` del gate. El tier ya existía en `financial_breakdown.evidence_tier` (se pasaba dentro de `financial_json` para otro gate) pero no como parámetro directo.
- **Por qué**: el productor del dato (`v4_diagnostic_generator.py`) y el consumidor (`commercial_gate.py`) estaban desacoplados en sus interfaces. Agregar el parámetro al consumer sin cablear el producer es un fix incompleto (como L19 de FASE-B).
- **Qué lo previene**: al añadir un parámetro a un gate, trazar inmediatamente quién lo produce y cablearlo en el caller. Crear `_extract_text_tier()` como método del generador (no del gate) mantiene la responsabilidad de extracción en quien tiene el texto.
- **Pertinencia**: **INCLUIR** — extiende L19: "la mitad faltante del fix suele ser el cableado".

#### L24 (FASE-D) — Archivos internos en ZIP de cliente: filtrar por prefijo, no por lista fija
- **Qué pasó**: `commercial_gates_report.json` y `commercial_gates_report_diagnostic_*.json` viajaban en el ZIP de cliente, exponiendo evidencia interna BLOCKING contradictoria con el frontmatter PASSED del diagnóstico.
- **Por qué**: el packager incluía todos los archivos de `v4_audit/` sin distinguir entre artefactos de entrega y reports internos.
- **Qué lo previene**: `_is_excluded_from_zip()` con prefijos configurables (`_GATE_REPORT_PREFIXES`). Cualquier nuevo report interno debe agregarse a la lista de prefijos, no hardcodearse en la lógica de filtrado.
- **Pertinencia**: **INCLUIR** — cualquier sistema de empaquetado para cliente debe tener una lista de exclusión por prefijo mantenible.

#### L25 (FASE-D) — Cutoff de 24h es insuficiente cuando hay múltiples runs el mismo día
- **Qué pasó**: el ZIP incluía artefactos de AMBOS runs del mismo día (123637 y 124443) porque el umbral de 24h no distingue entre runs.
- **Por qué**: `datetime.now().timestamp() - 86400` acepta cualquier archivo de las últimas 24 horas, sin importar si pertenecen al run actual o a uno anterior del mismo día.
- **Qué lo previene**: `_get_latest_run_timestamp()` calcula el cutoff desde el mtime más reciente de `v4_audit` (con tolerancia de 60s para archivos escritos en el mismo run). Esto es auto-adaptativo: si solo hay un run, el cutoff es ese run; si hay varios, solo el más reciente pasa.
- **Pertinencia**: **INCLUIR** — cualquier filtro temporal en directorios con múltiples ejecuciones debe usar timestamps derivados del contenido, no umbrales fijos.

#### L26 (FASE-D) — Label de fuente debe seguir la misma lógica de prioridad que el valor
- **Qué pasó**: `data_sources.occupancy` siempre decía `"regional"` cuando `should_use_regional_for(region)=True`, incluso cuando el occupancy provenía de onboarding (porque la L96 respetaba la prioridad pero el label en L118 no).
- **Por qué**: la lógica de prioridad del valor (`onboarding > regional > default`) estaba implementada en L96 pero el label en L118 usaba una condición independiente (`"regional" if should_use_regional...`) que ignoraba el resultado de L96.
- **Qué lo previene**: al construir un dict de fuentes, reutilizar la variable ya resuelta (`occupancy_source`) en vez de recalcular la condición. El label debe ser un reflejo del valor, no una segunda decisión.
- **Pertinencia**: **INCLUIR** — aplica a cualquier sistema de trazabilidad donde el label de fuente se construye independientemente del valor que describe.

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Tests patológicos propuesta/precios | ✅ Cuarentena (FASE-A) | 3 archivos aislados en `_archived_broken_tests/commercial_documents/`. Lista segura: 13 archivos PASS. FASE-B puede agregar tests nuevos sin riesgo. |
| `test_proposal_confidence_disclosure.py` | ⚠️ 5 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (área asset_quality_table, no tocada por RC1). Diagnosticar en release posterior. |
| `test_proposal_dynamic.py` | ⚠️ 7 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (lookups/asset_quality_table, no tocados por RC1). Diagnosticar en release posterior. |
| Backup forense RC1 | ⚠️ Conservar | `temp/rc1_backup/v4_proposal_generator.py` — NO eliminar hasta cierre de FASE-F. |
| Backup forense RC2-a | ⚠️ Conservar | `temp/rc2_backup/commercial_gate.py` + `v4_diagnostic_generator.py` — NO eliminar hasta cierre de FASE-F. |
| Prompts con `--release` en plantilla (L3/L9) | ⬜ Pendiente | FASE-E: enforcement `_check_prompts_no_release` en `run_all_validations.py` |
| S5: label `"occupancy": "regional"` residual | ✅ Resuelto (FASE-D) | `data_sources.occupancy` prioriza `"onboarding"`. `HotelFinancialData` fallback recibe `occupancy_source`. Verificar en E2E FASE-F. |
| S7: loader de onboarding sin fallback | ✅ Resuelto (FASE-D) | Fallback a `output/clientes` si `{--output}/clientes` no tiene YAML. 7 tests cubren el patrón. Verificar en E2E FASE-F. |
| Backup forense FASE-D | ⚠️ Conservar | `temp/fase_d_backup/` (3 archivos originales) — NO eliminar hasta cierre de FASE-F. |
| (otros) | | |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests baseline (pre-plan) | 3,215 collected | — |
| Tests collected post-cuarentena | 3,175 collected (2026-08-05) | FASE-A |
| Tests nuevos FASE-B | 9 (git diff tests/, patrón `^\+\s*def test_`, 2026-08-05) | FASE-B |
| Tests nuevos FASE-C | 20 (git diff tests/, patrón `^\+\s*def test_`, 2026-08-05) | FASE-C |
| Tests nuevos FASE-D | 23 (10 delivery + 6 financial + 7 loader, 2026-08-05) | FASE-D |
| Coherencia run E2E Zione | ⬜ (≥ 0.8 exigido) | FASE-F |
| Gates publicación run E2E | ⬜ (conteo dinámico) | FASE-F |
| Tests collected final | ⬜ (registrar en RELEASE) | FASE-RELEASE |

---

## Decisiones Arquitectónicas (llenar en FASE-B)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|------------------------|------|
| DEC-B1 | Mapa dinámico `_build_dynamic_breach_map()` dentro del generador de propuesta, consumiendo `opportunity_scores` pasados por parámetro desde `main.py` (FASE 3.5) | El pipeline ya produce opportunity_scores con la misma base que el diagnóstico (D3, DEC-B1 del plan anterior); pasarlos por parámetro mantiene el generador puro/testeable y evita leer JSON del disco | Recomputar scores dentro del generador (duplicaría lógica del diagnostic_gen); leer `v4_complete_report.json` desde disco (acopla al generador con rutas de output y orden de escritura) | FASE-B |
| DEC-B2 | Candidatos de brecha por servicio restringidos a la lista auditada (`optimization_guide ← [low_seo_score, low_content_length]`, `whatsapp_button ← [whatsapp_conflict, no_whatsapp_visible]`, resto 1:1), con desempate por mejor rank presente | La inversión pura de `PAIN_SOLUTION_MAP` atribuiría brechas de otro dominio al servicio (ej: `ai_crawler_blocked → llms_txt` daría costo $899.000 al servicio de llms.txt aunque `missing_llmstxt` no esté en el run) — distorsionaría la cifra que ve el cliente; detectado por test que falló en la primera iteración | Inversión pura del mapa sin restricción (falló el caso "llms_txt sin costo" del plan); usar solo `ASSET_TO_PAIN_ID` (cubre 6/8 y su entrada whatsapp=`no_whatsapp_visible` no resuelve runs con conflicto) | FASE-B |
| DEC-B3 | Fallback explícito sin cifras: si el asset no resuelve brecha presente en scores (o no hay scores), la columna muestra "—" + warning log | Principio "No Defaults in Money" — nunca inventar cifras ante el cliente; org_schema (N19) se vuelve naturalmente condicional | Fallback con costos estimados de benchmark (reproduciría N10); ocultar la fila (perdería trazabilidad del servicio prometido) | FASE-B |
| DEC-C1 | Split por oraciones + filtro doble de condicionales (antes del match + en toda la oración) para CG-CLAIM-VS-EVIDENCE | El texto diagnóstico real mezcla oraciones factuales y condicionales; verificar condicional solo antes del match es insuficiente ("El hotel podría no aparecer si no corrige su Schema" — condicional después del match); el doble check cubre ambos patrones sin exigir sujeto explícito (evita falsos negativos como "la web no aparece en Google") | Exigir sujeto explícito "hotel" en la oración (frágil: "la web no aparece en Google" es factual pero sin "hotel"); NLP con spaCy para clasificar oraciones (overkill para un gate de copywriting; agregaría dependencia pesada) | FASE-C |

---

## Notas de Forense y Regresión (llenar en FASE-B)

### Protocolo de verificación de regresiones (L4/L5)

1. Backup: `Copy-Item` de archivos de la fase a `temp/<fase>_backup/`
2. Reset: `git checkout HEAD -- <archivos>`
3. Test: correr tests contra HEAD (con timeout)
4. Restaurar: `Copy-Item` desde backup
5. Verificar: `git status --short` muestra archivos modificados

### Evidencia estática para tests patológicos (L7)

Mientras los tests patológicos sigan en cuarentena, usar `git show HEAD:` para verificar que el código modificado no afecta las áreas de los patológicos.

### Resultado forense FASE-B (2026-08-05)

- Backup: `temp/rc1_backup/v4_proposal_generator.py` (previo a todo edit; working tree limpio al iniciar, commit base `7ec1232`).
- No fue necesario el ciclo reset/restaurar: la lista segura de FASE-A pasó completa (208 passed) y los fallos preexistentes se mantuvieron en el conteo exacto documentado (7 + 5), confirmando 0 regresiones sin tocar los archivos cuarentenados.
- Evidencia estática (L7): verificación contra el JSON del run 124443 (`evidence/FASE-B/verify_breach_consistency_static.py`) — PASS, sin re-ejecutar v4complete.

### Resultado forense FASE-C (2026-08-05)

- Backup: `temp/rc2_backup/commercial_gate.py` + `v4_diagnostic_generator.py` (previo a todo edit).
- Suite completa quality_gates: 322 passed / 1 skipped / 0 failed (0 regresiones).
- Lista segura FASE-A (commercial_documents): 145 passed / 0 regresiones.
- Tests de diagnóstico: 63 passed / 0 regresiones.
- Fallos preexistentes estables: test_proposal_dynamic (7) + test_proposal_confidence_disclosure (5) = 12 failed (áreas no tocadas).
- No fue necesario el ciclo reset/restaurar: los cambios son autocontenidos en `_check_claim_vs_evidence` y `_check_tier_consistency` + cableado en caller.

### Resultado forense FASE-D (2026-08-05)

- Backup: `temp/fase_d_backup/delivery_packager.py` + `main.py` + `harness_handlers.py` (previo a todo edit).
- Suite completa delivery: 69 passed / 0 failed (incluye 10 tests nuevos FASE-D + 56 existentes + 2 FAQ + 1 contract).
- Quality gates: 366 passed / 1 skipped / 0 failed (0 regresiones).
- Fallos preexistentes estables: test_proposal_dynamic (7) + test_proposal_confidence_disclosure (5) = 12 failed (áreas no tocadas).
- Validaciones: 5/5 TOTAL PASS (residual files, plan maestro, version sync, secrets, document integration).
- No fue necesario el ciclo reset/restaurar: los 3 archivos de FASE-D son independientes entre sí y de los archivos de fases anteriores.

---

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Todas las causas raíz (RC1, RC2, RC3) verificadas en E2E
- [ ] Seguimientos S5 y S7 resueltos o documentados
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] `validate_agents_md.py` PASS
- [ ] CHANGELOG.md actualizado con formato CONTRIBUTING.md
- [ ] GUIA_TECNICA.md con notas técnicas por fase
- [ ] VERSION.yaml sincronizado (sync_versions.py)
- [ ] Lecciones aprendidas L16+ capitalizadas en memoria del agente
- [ ] Análisis post-implementación completo
