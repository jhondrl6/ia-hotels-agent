# Análisis Post-Implementación — RC1-RC2-ENTREGA-COHERENTE

> **Estado**: FASE-F completada (2026-08-05, 2 sesiones: ejecución + recuperación S5b) — RC1 + RC2 + S5 + S7 SUPERADOS con evidencia E2E; V1-V10 = 10/10 PASS.
> **Plan**: RC1-RC2-ENTREGA-COHERENTE-2026-08-04
> **Versión objetivo**: v4.71.0
> **Baseline auditado**: run 2026-08-04 12:44:43 (Zi One Luxury, coherence 0.9168, evidence_tier B+)
> **Run de verificación E2E**: FASE-F — `output/v4_verify_4.71.0` (run 20260805_154855/154910, coherence 0.9238, evidence_tier B+)
> **Plan anterior**: COHERENCIA-MODULO-ENTREGA-2026-08-03 (15 lecciones aprendidas capitalizadas)
>
> **Nota pre-bump (R3.3)**: los artefactos E2E del baseline llevan la versión del código
> que corrió (4.69.0 + fixes); el bump a 4.70.0 es posterior y no se re-ejecutó v4complete.
> Evidencia del run 123637 preservada en `evidence/N3-diff/` (14 JSON; diff de 97 líneas
> NO reproducible — los .md del run 1 fueron sobrescritos por el run 2).

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-A | 2026-08-05 | ✅ | 1 sesión (~30/60) | No (directo) | Cuarentena 3 archivos patológicos (40 tests). Tests collected: 3215 → 3175. Lista segura: 13 archivos PASS. 2 archivos con fallos preexistentes (no patológicos). `pytest.ini` con `--ignore` específicos (CR-8). Ver L16-L17. |
| FASE-B | 2026-08-05 | ✅ | 1 sesión (~20/60) | No (directo, no delegable — DT-3) | RC1: `_build_dynamic_breach_map` + cableado `opportunity_scores` en main.py. Eliminados `BREACH_BY_ASSET` (N10/N17) y hardcode L1250 (N18); org_schema condicional (N19). 9 tests nuevos PASS, lista segura 208 passed / 0 regresiones, verificación estática vs run 124443 PASS. Ver L18-L20, DEC-B1-B3. |
| FASE-C | 2026-08-05 | ✅ | 1 sesión (~15/60) | No (directo) | RC2-a: split oraciones + filtro condicionales CG-CLAIM-VS-EVIDENCE (N11) + cableado frontmatter_tier/text_tier en CG-TIER-CONSISTENCY (N15). 20 tests nuevos PASS, quality_gates 322 passed / 0 regresiones, preexistentes estables (12 failed). Ver L21-L23, DEC-C1. |
| FASE-D | 2026-08-05 | ✅ | 1 sesión (~15/60) | No (directo, 3 tracks serie) | RC2-b: `_is_excluded_from_zip` + `_get_latest_run_timestamp` (N16/N21) + fallback loader onboarding (S7) + occupancy label priority (S5). 23 tests nuevos PASS, delivery 69 passed, quality_gates 366 passed, preexistentes estables (12 failed). Ver L24-L26. |
| FASE-E | 2026-08-05 | ✅ | 1 sesión (~25/60) | Sí (solo docs, sin imports) | RC3: `--release 4.70.0` eliminado de 4 prompts + nota preventiva. `_check_prompts_no_release` en `run_all_validations.py` (6/6 TOTAL PASS). Conteos fuente viva: 205 .py, 391 clases, 27 dirs, 3,227 tests. Lista D3 completa (8 valores). Evidencia N3 preservada (14 JSON). Ver L27. |
| FASE-F | 2026-08-05 | ✅ | 2 sesiones (~25/60 + ~15/60) | Sí (v4complete vía subagente) | Sesión 1: run E2E único exitoso (exit 0, onboarding real, coherence 0.9238). V1-V10: 9/10 — V8 (S5) FAIL. Sesión 2 (recuperación S5b): fix en 2 sitios de main.py (bloque FASE-K + PrecisionValidator/GAP-4) + 6 tests nuevos + re-verificación V8 PASS en run acotado. Regresión 0. Ver L28-L32. |
| FASE-RELEASE | ⬜ Pendiente | — | — | Sí (delegate_task) | Desbloqueada (A-F ✅). |

### Evidencia v4complete FASE-F

| Hotel | Output | evidence_tier | coherence | ZIP sin históricos | Onboarding inyectado |
|-------|--------|---------------|-----------|:---:|:---:|
| Zi One Luxury | `output/v4_verify_4.71.0` (20260805_154910) | B+ | 0.9238 (≥ 0.8) ✅ | ✅ (53 archivos, 0 gate reports, 1 timestamp) | ✅ (4 campos confirmados, sin "Using defaults") |

#### Run acotado de re-verificación S5b (20260805_161042)

| Output | `data_sources.occupancy` | occupancy_rate | readiness |
|--------|:---:|:---:|:---:|
| `output/v4_verify_s5b` (evidencia: `evidence/FASE-F/s5b_rerun/`) | ✅ "onboarding" | 0.7843 (800/(34×30), intacto) | READY_FOR_PUBLICATION |

---

## Matriz de Verificación de Causas Raíz (llenar en FASE-F)

### RC1 — Fuente de verdad de costos aplicada a medias

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N10 | Costos hardcodeados en propuesta | Costos desde `opportunity_scores` del run | E2E (V1): 5 filas con costo vivo, todas == `opportunity_scores` (baseline tenía $1.005.768 hardcodeado factor 0.671×) | ✅ SUPERADO |
| N17 | Mapa inverso `asset_type → brecha_id` | Construido desde `pain_solution_mapper.PAIN_SOLUTION_MAP` | E2E (V2): fila SEO Local → #6 `low_seo_score` (baseline referenciaba "#1: Sin Schema Hotel") | ✅ SUPERADO |
| N18 | Hardcode L1250 (servicio fantasma) | Eliminado o parametrizado | E2E (V3): fila WhatsApp rank vivo 1 + label "Conflicto de WhatsApp" + costo $899.000; grep "Brecha #5: WhatsApp" = 0 (baseline: 1) | ✅ SUPERADO |
| N19 | `ASSET_TO_PAIN_ID` solo cubre 6/8 | Mapa inverso cubre 8/8 | E2E (V4): sin fila "Schema Organization" y asset `org_schema` ausente del run (condicional sin cifras funciona) | ✅ SUPERADO |

### RC2 — Gates comerciales con inputs no cableados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| N11 | CG-CLAIM-VS-EVIDENCE falso positivo | No dispara con texto condicional "si...no aparece" | Split oraciones + `_CONDITIONAL_MARKERS`. E2E (V5): passed=true "condicionales descartados" (baseline: BLOCKING fail "El documento dice 'no aparece' pero place_found=True") | ✅ SUPERADO |
| N15 | CG-TIER-CONSISTENCY pasa vacuo | Valida inputs reales o falla explícitamente | `_check_tier_consistency` falla con None; caller cablea `frontmatter_tier`+`text_tier`. E2E (V6): valida inputs reales — detectó inconsistencia REAL del doc ("Frontmatter dice tier 'B+' pero el texto dice tier 'D'", WARNING) (baseline: "Sin datos de tier para comparar") | ✅ SUPERADO |
| N16 | ZIP con `commercial_gates_report` BLOCKING | Sin reports BLOCKING junto a doc PASSED | `_is_excluded_from_zip()`. E2E (V7): 0 `commercial_gates_report*` en ZIP (baseline: 3 archivos, incluido 1 BLOCKING) | ✅ SUPERADO |
| N21 | ZIP con artefactos de runs anteriores | Solo artefactos del run actual | `_get_latest_run_timestamp()` cutoff por mtime v4_audit. E2E (V7): solo timestamps del run 20260805 (baseline: 5 timestamps distintos, 76 archivos) | ✅ SUPERADO |

### RC3 — Higiene documental sin enforcement

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| R3.1 | Prompts con `--release` en fases intermedias | Sin `--release` en A-F | Eliminados de 4 prompts + nota preventiva + enforcement `_check_prompts_no_release` (6/6 PASS) | ✅ |
| R3.2 | Conteos desactualizados | Conteos desde fuente viva (L8) | 205 .py, 391 clases, 27 dirs, 3,227 tests; lista D3 completa (8 valores) | ✅ |
| R3.3 | Citas driftadas | Referencias verificadas | Nota pre-bump añadida; evidencia N3 preservada (14 JSON en `evidence/N3-diff/`) | ✅ |
| R3.4 | Evidencia no preservada | `evidence/N3-diff/` completo | 14 JSON del run 123637 + README (diff 97 líneas no reproducible) | ✅ |

### Seguimientos heredados

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| S5 | Occupancy label "regional" residual | Label coherente con fuente real | Fix FASE-D cubrió `harness_handlers.py` y `financial_sources`; E2E (V8) reveló DOS sitios adicionales (`main.py`: bloque FASE-K + input `PrecisionValidator`/GAP-4) → cerrados en recuperación S5b (re-verificación V8 PASS, run acotado 20260805_161042) | ✅ SUPERADO |
| S7 | Loader onboarding sin fallback | Fallback a `output/clientes` con `--output` alternativo | Verificado en aislamiento ANTES del run (`temp/verify_s7_loader.py`, 3/3 PASS) + E2E: log "Onboarding data loaded: 4 campos confirmados", sin "Using defaults" | ✅ SUPERADO |

---

## Matriz de fixes superados en E2E (FASE-F, run 20260805_154910)

| Hallazgo | Fix (fase) | Evidencia E2E | Estado |
|----------|-----------|---------------|--------|
| N10 costos hardcodeados | `_build_dynamic_breach_map` + cableado `opportunity_scores` (B) | V1 PASS — 5/5 costos vivos == scores | ✅ SUPERADO |
| N17 mapeo invertido erróneo | Mapa inverso auditado desde `PAIN_SOLUTION_MAP` (B) | V2 PASS — SEO Local → `low_seo_score` | ✅ SUPERADO |
| N18 hardcode "Brecha #5: WhatsApp" | Rank/label/costo vivos (B) | V3 PASS — rank 1, costo $899.000, 0 hardcodes | ✅ SUPERADO |
| N19 servicio fantasma Schema Organization | Condicional sin cifras (B) | V4 PASS — 0 filas, asset ausente | ✅ SUPERADO |
| N11 falso positivo condicional | Split oraciones + `_CONDITIONAL_MARKERS` (C) | V5 PASS — condicionales descartados | ✅ SUPERADO |
| N15 gate vacuo | Cableado frontmatter/text tier (C) | V6 PASS — valida inputs reales | ✅ SUPERADO |
| N16 gate reports en ZIP | `_is_excluded_from_zip` (D) | V7 PASS — 0 gate reports | ✅ SUPERADO |
| N21 artefactos de runs previos | `_get_latest_run_timestamp` (D) | V7 PASS — 1 solo timestamp | ✅ SUPERADO |
| S5 occupancy label | Prioridad onboarding en handlers (D) + recuperación S5b: 2 sitios de main.py (bloque FASE-K + PrecisionValidator/GAP-4) | V8 PASS — run acotado 20260805_161042: `data_sources.occupancy == "onboarding"`, 0.7843 intacto | ✅ SUPERADO |
| S7 loader fallback | Fallback `output/clientes` (D) | Pre-run 3/3 + log run | ✅ SUPERADO |
| D10 check de cierre | — | V9 PASS — 5/5 costos idénticos diagnóstico↔propuesta | ✅ SUPERADO |
| Coherencia global | — | V10 PASS — READY_FOR_PUBLICATION, 0 blocking, coherence 0.9238 | ✅ SUPERADO |

**Resultado**: 12/12 SUPERADO (V8 cerrado en la sesión de recuperación S5b, misma fecha).

## Diff cualitativo vs run baseline 20260804_124443 (`output/v4_verify_4.70.0`)

| Aspecto | Baseline (20260804_124443) | Run E2E FASE-F (20260805_154910) |
|---------|---------------------------|----------------------------------|
| Tabla de servicios (propuesta) | SEO Local → "#1: Sin Schema Hotel ($1,005,768/mes)" (mapeo+costo estático); WhatsApp → "Brecha #5: WhatsApp no coincide" (hardcode, sin costo); fila "Optimización para IA Generativa" con brecha ajena | SEO Local → #6 `low_seo_score` ($899.000); WhatsApp → Brecha #1 ($899.000); Schema Hotel → #3 ($1.123.390); FAQ → #4 ($539.400); OG → #10 ($359.600). Todos vivos del run |
| Commercial gate diagnóstico | CG-CLAIM-VS-EVIDENCE **FAIL BLOCKING** (falso positivo "no aparece" vs place_found=True); CG-TIER-CONSISTENCY pass vacuo "Sin datos de tier" | CG-CLAIM-VS-EVIDENCE PASS (condicionales descartados); CG-TIER-CONSISTENCY WARNING con comparación real (B+ vs D) |
| ZIP de entrega | 76 archivos; 3 `commercial_gates_report*` (1 de run anterior BLOCKING); 5 timestamps (123620/123636/123637/124429/124443) | 53 archivos; 0 gate reports; solo timestamps del run (154855/154910) |
| Coherencia / readiness | coherence 0.9168, gate comercial BLOCKING interno | coherence 0.9238, READY_FOR_PUBLICATION, 0 blocking |
| Onboarding | Cargado vía `output/clientes` | Cargado con workaround L13 + fallback S7 verificado en aislamiento |

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

#### L27 (FASE-E) — Regex de enforcement debe distinguir comando real de documentación que cita el flag
- **Qué pasó**: el check `_check_prompts_no_release` con regex genérico `--release\s+\d` detectaba falsos positivos en el propio prompt de FASE-E que documenta el problema (ej: "Eliminar `--release 4.70.0` del comando `log_phase_completion.py`" o "NO usar `--release` en fases intermedias").
- **Por qué**: la regex no distinguía entre un comando real (`scripts/log_phase_completion.py --fase FASE-X ... --release 4.70.0`) y documentación que discute el flag en orden inverso o como referencia.
- **Qué lo previene**: usar una regex que solo matchea cuando `log_phase_completion.py` aparece ANTES de `--release\s+\d` en la misma línea (`log_phase_completion\.py.*--release\s+\d`). Esto captura solo invocaciones de comando reales, no citas documentales. El enforcement es así auto-aplicable: el plan que corrige la violación puede ser escaneado sin falsos positivos.
- **Pertinencia**: **INCLUIR** — cualquier check de enforcement basado en regex sobre archivos que también documentan la violación necesita anclaje contextual (orden de tokens, no solo presencia).

#### L28 (FASE-F) — Un fix de label/fuente debe cubrir TODOS los sitios de construcción, no solo el que motivó el hallazgo
- **Qué pasó**: el fix S5 (FASE-D) corrigió el label de occupancy en `harness_handlers.py` y en los dicts `financial_sources` de main.py, y sus tests unitarios pasaron. Pero `main.py` L2036 (bloque FASE-K) construye un `HotelFinancialData` SEPARADO —que es el que alimenta `breakdown.data_sources` del `financial_scenarios*.json`— con la condición vieja (`'regional' if should_use_regional...`). El E2E (V8) lo detectó: label `'regional'` con valor real de onboarding.
- **Por qué**: los tests unitarios de FASE-D validaron los sitios conocidos del fix, pero nadie grepeó todos los sitios donde se construye el dict de fuentes / `HotelFinancialData`. Es la misma familia que L19/L23 ("la mitad faltante del fix es el cableado"), aplicada a sitios de construcción múltiples.
- **Qué lo previene**: al cerrar un fix de trazabilidad (label que describe un valor), ejecutar `grep` de todos los sitios que construyen la estructura afectada (`HotelFinancialData(`, `data_sources`, `occupancy_source`) y auditar cada uno contra la regla del fix ANTES de marcarlo resuelto.
- **Pertinencia**: **INCLUIR** — generalización de L26: "el label debe reflejar el valor" + "verificar todos los sitios de construcción, no solo el del reporte original".

#### L29 (FASE-F) — Tests unitarios que mockean el camino completo no detectan sitios de integración omitidos; solo el E2E lo hace
- **Qué pasó**: FASE-D cerró S5 con 6 tests PASS; FASE-E cerró con 6/6 validaciones PASS. El defecto sobrevivió hasta el ÚNICO run E2E real de FASE-F.
- **Por qué**: los tests unitarios fijan los inputs (mock del payload, `HotelFinancialData` construido en el test) y por diseño no pueden descubrir que el orquestador construye el objeto en otro sitio con lógica distinta.
- **Qué lo previene**: mantener SIEMPRE una fase E2E de verificación con checks automatizados contra artefactos del run (V1-V10) antes de declarar fixes "superados"; nunca promover un fix a SUPERADO solo con tests unitarios cuando el defecto era de integración.
- **Pertinencia**: **INCLUIR** — criterio de cierre: fix de integración solo se certifica con evidencia E2E del artefacto afectado.

#### L30 (FASE-F) — La delegación del comando largo + protocolo evidencia-first funciona y ahorra presupuesto
- **Qué pasó**: `v4complete` (5-10 min) se delegó a un subagente con instrucción estricta de "ejecutar y reportar, no interpretar"; el agente principal usó sus iteraciones en verificación S7, scripting V1-V10 y documentación. La evidencia se copió INMEDIATAMENTE después del run, antes de cualquier análisis.
- **Por qué**: el protocolo del executor (subagente para comandos largos + evidencia proactiva) elimina el riesgo de perder artefactos si una verificación posterior modifica el output.
- **Qué lo previene**: ya está protocolizado; reforzar que la copia de evidencia incluye también `v4_complete_report.json` y el ZIP (no solo docs+JSON de audit), porque V1/V7/V9 los necesitan.
- **Pertinencia**: **INCLUIR** — refuerzo del protocolo existente (sin cambios).

#### L31 (FASE-F) — Numeración de brechas divergente entre diagnóstico y propuesta es por diseño, pero debe documentarse
- **Qué pasó**: V9 detectó que el diagnóstico numera brechas por orden de aparición (`[BRECHA 1..10]`: WhatsApp, Schema Hotel, GBP, SEO...) mientras la propuesta referencia por rank de `opportunity_scores` (`#3` = Schema Hotel). Los COSTOS y nombres son idénticos en ambos documentos (check D10 real), pero un lector que cruce "#3 propuesta" con "BRECHA 3 diagnóstico" encontraría brechas distintas.
- **Por qué**: el diagnóstico renderiza brechas en orden de detección/severidad del audit; la propuesta usa rank de oportunidad para priorizar comercialmente. Son dos órdenes legítimos pero no alineados visualmente.
- **Qué lo previene**: decisión pendiente (seguimiento S9): alinear numeración (usar rank en ambos) o añadir el rank explícito en el diagnóstico. No bloqueante: los costos —lo que ve el cliente como cifra— son consistentes.
- **Pertinencia**: **EVALUAR** en próximo release — mejora de claridad comercial, no defecto de datos.

#### L32 (FASE-F recuperación S5b) — El grep de sitios de construcción (L28) revela defectos hermanos que el análisis inicial no ve
- **Qué pasó**: el análisis inicial de V8 identificó UN sitio defectuoso (bloque FASE-K). Al aplicar el protocolo L28 en la sesión de recuperación (grep de TODOS los sitios que asignan `occupancy_source=` / `_occ_source`), apareció un SEGUNDO sitio con la misma condición divergente: el input de `PrecisionValidator` (GAP-4), que alimenta `precision_tier` del `financial_scenarios*.json`.
- **Por qué**: el análisis de causa raíz tiende a detenerse en el primer sitio que explica el síntoma observado; los defectos hermanos solo aparecen cuando se audita el patrón completo, no el síntoma individual.
- **Qué lo previene**: convertir el grep de sitios de construcción en paso OBLIGATORIO (no opcional) de toda sesión de fix; los tests estáticos anti-regresión (3 en `test_fase_f_recovery_s5b.py`) anclan el patrón para que ningún sitio futuro reintroduzca la condición divergente.
- **Pertinencia**: **INCLUIR** — extiende L28 con la comprobación empírica: en este caso el protocolo encontró exactamente el defecto hermano que faltaba.

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Tests patológicos propuesta/precios | ✅ Cuarentena (FASE-A) | 3 archivos aislados en `_archived_broken_tests/commercial_documents/`. Lista segura: 13 archivos PASS. FASE-B puede agregar tests nuevos sin riesgo. |
| `test_proposal_confidence_disclosure.py` | ⚠️ 5 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (área asset_quality_table, no tocada por RC1). Diagnosticar en release posterior. |
| `test_proposal_dynamic.py` | ⚠️ 7 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (lookups/asset_quality_table, no tocados por RC1). Diagnosticar en release posterior. |
| Backup forense RC1 | ⚠️ Conservar | `temp/rc1_backup/v4_proposal_generator.py` — NO eliminar hasta cierre de FASE-F. |
| Backup forense RC2-a | ⚠️ Conservar | `temp/rc2_backup/commercial_gate.py` + `v4_diagnostic_generator.py` — NO eliminar hasta cierre de FASE-F. |
| Prompts con `--release` en plantilla (L3/L9) | ✅ Resuelto (FASE-E) | `_check_prompts_no_release` en `run_all_validations.py` escanea `0[2-5]-prompt*.md` buscando `--release` en comandos `log_phase_completion.py`. 6/6 TOTAL PASS en `--quick`. Enforcement permanente anti-regresión. |
| S5: label `"occupancy": "regional"` residual | ✅ SUPERADO (FASE-F + recuperación S5b) | Fix FASE-D (handlers + `financial_sources`) + recuperación S5b: 2 sitios de `main.py` (bloque FASE-K + input `PrecisionValidator`/GAP-4) reutilizan `_occupancy_source`. V8 re-verificado PASS. Cerrado. |
| **S5b (NUEVO FASE-F)**: occupancy label en bloque FASE-K | ✅ Resuelto (2026-08-05) | Fix aplicado en misma fecha: `occupancy_source=_occupancy_source` (bloque FASE-K) + `_occ_source = _occupancy_source` (GAP-4). 6 tests nuevos (`tests/financial_engine/test_fase_f_recovery_s5b.py`, incluye contrato estático anti-regresión). Backup forense: `temp/fase_f_recovery_backup/main.py`. Re-verificación V8 PASS en run acotado 20260805_161042. |
| S7: loader de onboarding sin fallback | ✅ SUPERADO (FASE-F) | Verificado en aislamiento (3/3) + E2E con onboarding real inyectado. Cerrado. |
| **S8 (NUEVO FASE-F)**: tier inconsistente en diagnóstico generado | ⬜ Pendiente | CG-TIER-CONSISTENCY (ya cableado) detectó que el diagnóstico de Zione dice tier B+ en frontmatter y tier D en el texto (WARNING). Es defecto de CONTENIDO del generador de diagnóstico, no del gate. Investigar origen del tier D en texto (probablemente plantilla legacy). Severidad MEDIA (el cliente ve dos tiers). |
| **S9 (NUEVO FASE-F)**: numeración divergente diagnóstico↔propuesta | ⬜ Pendiente | Diagnóstico numera por aparición, propuesta por rank de oportunidad (L31). Evaluar alineación en próximo release. Severidad BAJA (estética/comercial). |
| Backup forense FASE-D | ⚠️ Conservar | `temp/fase_d_backup/` (3 archivos originales) — NO eliminar hasta FASE-RELEASE. |
| Backup forense recuperación S5b | ⚠️ Conservar | `temp/fase_f_recovery_backup/main.py` (pre-fix S5b) — NO eliminar hasta FASE-RELEASE. |
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
| Tests nuevos FASE-F (recuperación S5b) | 6 (`test_fase_f_recovery_s5b.py`: 3 contrato estático + 3 comportamiento, 2026-08-05) | FASE-F |
| Coherencia run E2E Zione | 0.9238 (≥ 0.8 exigido) ✅ | FASE-F |
| Gates publicación run E2E | 12 gates: 11 passed + 1 WARNING advisory (`asset_confidence`), 0 blocking, readiness READY_FOR_PUBLICATION | FASE-F |
| Fixes verificados E2E (V1-V10) | 10/10 PASS (V8 cerrado en recuperación S5b, run acotado 20260805_161042) | FASE-F |
| Fixes SUPERADOS | 12/12 (matriz de fixes: N10-N21, S5+S5b, S7, D10, coherencia global) | FASE-F |
| Regresión recuperación S5b | 0 — batch 78 tests + lista segura FASE-A 208 passed; validaciones 6/6 | FASE-F |
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

### Resultado forense recuperación S5b (2026-08-05)

- Backup: `temp/fase_f_recovery_backup/main.py` (previo a todo edit del fix S5b).
- Grep de sitios de construcción (L28/L32): 25 asignaciones `occupancy_source=` auditadas; 2 sitios divergentes en `main.py` (bloque FASE-K e input `PrecisionValidator`/GAP-4) corregidos; el resto son tests, handlers ya fixeados o lógica de resolución legítima (FASE 3, diagnostic_generator).
- Tests nuevos: 6 (`test_fase_f_recovery_s5b.py`) — 12/12 PASS junto a la suite S5 de FASE-D (`test_fase_d_occupancy_label.py`).
- Batch de regresión: 78 passed (S5b + occupancy label + loader + injection + evidence_tier + breakdown).
- Lista segura FASE-A: 208 passed / 0 regresiones.
- Run acotado de re-verificación: `output/v4_verify_s5b` (20260805_161042) — V8 PASS; evidencia preservada en `evidence/FASE-F/s5b_rerun/`.
- Validaciones: `run_all_validations.py --quick` 6/6 TOTAL PASS.

---

## Checklist de Cierre (llenar en FASE-RELEASE)

> **Estado FASE-F (2026-08-05)**: ✅ COMPLETA — V1-V10 = 10/10 PASS tras recuperación S5b.
> El análisis post-implementación de FASE-F (matriz de fixes 12/12, diff cualitativo, L28-L32,
> seguimientos S8/S9) quedó poblado en estas sesiones; consolidar al cierre definitivo.

- [x] Todas las causas raíz (RC1, RC2, RC3) verificadas en E2E — 10/10 V-checks PASS
- [x] Seguimientos S5 y S7 resueltos o documentados — S5 ✅ (con S5b), S7 ✅
- [x] `run_all_validations.py --quick` TOTAL PASS (6/6, 2026-08-05)
- [ ] `validate_agents_md.py` PASS (FASE-RELEASE)
- [ ] CHANGELOG.md actualizado con formato CONTRIBUTING.md (FASE-RELEASE)
- [ ] GUIA_TECNICA.md con notas técnicas por fase (FASE-RELEASE)
- [ ] VERSION.yaml sincronizado (sync_versions.py) (FASE-RELEASE)
- [x] Lecciones aprendidas L16+ capitalizadas en memoria del agente (L16-L32)
- [x] Análisis post-implementación completo
