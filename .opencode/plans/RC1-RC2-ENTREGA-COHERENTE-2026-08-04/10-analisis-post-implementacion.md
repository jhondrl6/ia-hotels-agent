# Análisis Post-Implementación — RC1-RC2-ENTREGA-COHERENTE

> **Estado**: FASE-B completada (2026-08-05) — RC1 resuelto a nivel código; verificación E2E en FASE-F.
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
| FASE-C | ⬜ Pendiente | — | — | No (directo) | |
| FASE-D | ⬜ Pendiente | — | — | Sí (3 tracks independientes) | |
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
| N11 | CG-CLAIM-VS-EVIDENCE falso positivo | No dispara con texto condicional "si...no aparece" | ⬜ | ⬜ |
| N15 | CG-TIER-CONSISTENCY pasa vacuo | Valida inputs reales o falla explícitamente | ⬜ | ⬜ |
| N16 | ZIP con `commercial_gates_report` BLOCKING | Sin reports BLOCKING junto a doc PASSED | ⬜ | ⬜ |
| N21 | ZIP con artefactos de runs anteriores | Solo artefactos del run actual | ⬜ | ⬜ |

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
| S5 | Occupancy label "regional" residual | Label coherente con fuente real | ⬜ | ⬜ |
| S7 | Loader onboarding sin fallback | Fallback a `output/clientes` con `--output` alternativo | ⬜ | ⬜ |

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

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Tests patológicos propuesta/precios | ✅ Cuarentena (FASE-A) | 3 archivos aislados en `_archived_broken_tests/commercial_documents/`. Lista segura: 13 archivos PASS. FASE-B puede agregar tests nuevos sin riesgo. |
| `test_proposal_confidence_disclosure.py` | ⚠️ 5 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (área asset_quality_table, no tocada por RC1). Diagnosticar en release posterior. |
| `test_proposal_dynamic.py` | ⚠️ 7 fallos preexistentes | Fallos de aserción (no patológicos), reconfirmados estables en FASE-B (lookups/asset_quality_table, no tocados por RC1). Diagnosticar en release posterior. |
| Backup forense RC1 | ⚠️ Conservar | `temp/rc1_backup/v4_proposal_generator.py` — NO eliminar hasta cierre de FASE-F. |
| Prompts con `--release` en plantilla (L3/L9) | ⬜ Pendiente | FASE-E: enforcement `_check_prompts_no_release` en `run_all_validations.py` |
| S5: label `"occupancy": "regional"` residual | ⬜ Pendiente | FASE-D: `_occupancy_source` al bloque de fuentes del scenario calculator |
| S7: loader de onboarding sin fallback | ⬜ Pendiente | FASE-D: fallback a `output/clientes` con `--output` alternativo |
| (otros) | | |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor | Fase |
|---------|-------|------|
| Tests baseline (pre-plan) | 3,215 collected | — |
| Tests collected post-cuarentena | 3,175 collected (2026-08-05) | FASE-A |
| Tests nuevos FASE-B | 9 (git diff tests/, patrón `^\+\s*def test_`, 2026-08-05) | FASE-B |
| Tests nuevos FASE-C | ⬜ (desde `git diff tests/`) | FASE-C |
| Tests nuevos FASE-D | ⬜ (desde `git diff tests/`) | FASE-D |
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
