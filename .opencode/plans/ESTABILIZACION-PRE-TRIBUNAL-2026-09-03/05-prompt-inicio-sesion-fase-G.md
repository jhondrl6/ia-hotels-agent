# FASE-G — Ceguera de gates (Nivel 3.7)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-G
**Objetivo**: Que los gates vean lo que hoy no pueden ver. Cuatro defectos: `doc_audit_consistency` llegó
sin datos y pasó en verde; `critical_recall = 1.0` es vacuo; y el coverage gate tiene **dos escotillas**
(V5 `ASSET_GENERATED` sin mención en doc, V9 ledger vacío PASS vs BLOCKED).
**Dependencias**: FASE-F ✅ (el criterio de presencia ya es único; cerrar escotillas antes fijaría el criterio doble)
**Duración estimada**: 4-5 horas
**Complejidad técnica**: **MEDIA-ALTA**
**Modo de ejecución**: **DIRECTO** (no delegable — V5 lleva advertencia anti-reversión de un fix de 2026-07-25)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤50 iteraciones (R2 tope: 60)
**ACs que cierra**: NR1, NR2, NR3, NR4

---

## Contexto

El dossier §3 establece que **los gates no pueden ver** las 8 caídas silenciosas del §4. Esta fase es el
Nivel 3.7 de §12.5 — *"Ceguera de gates (completitud del diagnóstico, faseable)"*. Va después de las
precondiciones del tribunal porque **no es** precondición: es completitud.

### La tautología que G3/G4 NO pueden curar solas (entender antes de editar)

`coverage_no_silent_drop` compara `len(pain_ledger_resolved)` contra las brechas del documento, y
**ambos salen de la MISMA llamada `detect_pains`** (`v4_asset_orchestrator.py:280`;
`v4_diagnostic_generator.py:3178`, DEP-03). **Tautología extremo a extremo confirmada en código** — la
brecha que no entra al ledger es **invisible** por construcción.

⟹ La cura real es FASE-A/B/C (fuente única + biyección + propuesta dinámica). G3 y G4 cierran **las
escotillas que quedan** dentro de un gate cuya premisa ya fue reparada aguas arriba. **No intentar
hacer que el gate detecte brechas que el ledger no registró** — eso es re-construir la detección dentro
del gate, que es exactamente el anti-patrón de DT4-N2 (*"los gates deben validar, no descubrir ni
reconstruir la evidencia primaria"*).

### Los cuatro candados rotos (dossier §3)

| Candado | Defecto | Ubicación |
|---------|---------|-----------|
| `coverage_no_silent_drop` | Tautología extremo a extremo + **dos escotillas** | `publication_gates.py:1244-1373` (`_coverage_gate`), `:1237-1242` (`_JUSTIFIED_STATUSES`), `:1295-1304`, `:1336-1344` |
| `doc_audit_consistency` | Único gate doc-vs-audit; llegó **sin** `audit_data`/`diagnostico_text` → PASSED con `value=null` pese a que `audit_report` existía en disco | `publication_gates.py:1464-1514` |
| `critical_recall` | **1.0 vacuo**: `_identify_critical_issues` solo consulta schema/whatsapp/`geo_score<50`/perf con `field_data` | `v4_comprehensive.py:1789-1814`, gate en `publication_gates.py:528` |
| `hard_contradictions` | `= 0` fuera del alcance del motor | — **documentado como límite, no se aborda** |

### V5 — Segunda escotilla del coverage gate (verbatim, con su advertencia)

> `_JUSTIFIED_STATUSES` incluye `ASSET_GENERATED` (`publication_gates.py:1237-1242`): un pain con asset
> generado cuenta como justificado **aunque el doc jamás lo mencione**. La tautología tiene dos salidas,
> no una.
>
> **Origen histórico (QMind, DT-4 root cause, Zione 2026-07-25):** esa inclusión fue el **fix deliberado
> de BUG-6/N2** — en 2026-07-25 `_JUSTIFIED_STATUSES` NO tenía `ASSET_GENERATED` y el coverage gate
> bloqueaba Zione con el botón de WhatsApp existente en producción (**falso positivo CRÍTICO**). Quitar
> `ASSET_GENERATED` sin más **resucitaría BUG-6**: cerrar la escotilla exige **distinguir "asset generado
> y mencionado en doc" de "asset generado y silencioso"**, no revertir el status. Segundo péndulo de la
> familia D2→tautología (§5).

⚠️ **Esta es la restricción más delicada del plan.** Es el segundo péndulo de una familia que ya osciló
una vez. Un subagente sin este contexto re-introduce BUG-6 — por eso la fase es DIRECTA.

### V9 — Inconsistencia de ledger vacío (verbatim)

> `pain_ledger` (fallback) vacío = **PASS** (`publication_gates.py:1336-1344`);
> `pain_ledger_resolved` vacío = **BLOCKED** (`:1295-1304`).

**Interacción con FASE-C**: C1 definió el comportamiento de la propuesta dinámica ante ledger vacío. G4
debe ser **coherente con esa decisión**, no inventar una tercera.

### V10 — Confirmación que refuerza la decisión de FASE-D (no requiere acción)

> En `delivery_quality_report`, G8 «some below threshold» retorna `False` pero fuera de
> `BLOCKING_GATE_NAMES` → WARNING → el ZIP procede (`main.py:3194` solo aborta con FAIL). **Refuerza
> §8.2: `asset_confidence` de publicación es el único bloqueo duro**, tal como el dossier afirma.

⟹ Registrar en `10-analisis` como **confirmación** de la decisión D1/D2. No tocar.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A … FASE-E | ✅ Completadas |
| FASE-F — A4 + A1 + N11 | ✅ Completada (ver sus 4 Decisiones Arquitectónicas en `10-analisis`) |

⚠️ **FASE-F modificó `publication_gates.py`** (`_coherence_gate:458`). Re-verificar las líneas de
`_coverage_gate` y `_doc_audit_consistency_gate` antes de editar — pueden haberse desplazado.

### Base Técnica Disponible

- Criterio de presencia **único** (FASE-F)
- Severidad explícita 11+2 (FASE-D) — `_coverage_gate` y `doc_audit_consistency` son **blocking**
- Biyección triple mapa↔emisión↔narrativa (FASE-B) — el ledger ya solo contiene pains que realmente se emiten **y** tienen narrativa
- **Corpus de referencia**: `output/FASE-D_salentoreal_post_guard/v4_complete/hotelsalentoreal/v4_audit/audit_report_20260831_122803.json`
- **Baseline**: 848 passed / 2 skipped + delta A-F

---

## Tareas

### Tarea G1: Cablear `doc_audit_consistency`

**Objetivo**: Que el único gate doc-vs-audit reciba realmente los datos y pueda fallar.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:1464-1514` (`_doc_audit_consistency_gate`)
- El **caller** que construye el assessment: `modules/assessment_builder.py` y/o `main.py` (identificar
  por grep dónde se ensambla el assessment que recibe el gate)

**Criterios de aceptación**:
- [ ] `audit_data` y `diagnostico_text` **llegan** al gate (hoy llegan `None` y el gate pasa con `value=null`)
- [ ] El gate **falla** cuando el doc contradice el audit, y **pasa** cuando coinciden — testeado en ambas direcciones
- [ ] **Check 2 acepta `gbp.reviews` como `int`** (el audit trae `986`), no solo como dict `{"total": ...}`
- [ ] El comportamiento con datos ausentes deja de ser PASS silencioso: o es `NOT_EVALUATED` (estado
      introducido en FASE-F) o es BLOCKED — **decisión registrada**, coherente con A1
- [ ] Test con el `audit_report` real de SalenteReal como fixture

### Tarea G2: Ampliar `_identify_critical_issues`

**Objetivo**: Que `critical_recall` deje de ser 1.0 vacuo.

**Archivos afectados**:
- `modules/auditors/v4_comprehensive.py:1789-1814` (`_identify_critical_issues`, consumido en `:619`)
- `modules/quality_gates/publication_gates.py:528` (`_critical_recall_gate`), `:1864` (`_extract_critical_recall`)

**Criterios de aceptación**:
- [ ] PageSpeed `status=ERROR` **califica** como critical issue (hoy no: solo perf con `field_data`)
- [ ] Banda GEO `critical` (29/100 en SalenteReal, `geo_flow_result` con `sync_report` "CRISIS TÉCNICA")
      **califica** (hoy no: solo `geo_score < 50`)
- [ ] `critical_recall` resultante **< 1.0** en el fixture de SalenteReal (prueba de que dejó de ser vacuo)
- [ ] ⚠️ **Semántica «vacío ≠ ausente»** preservada (lección SR-H2 / FASE-SR-H2 hotfix): un recall
      calculado sobre cero issues críticos no es 1.0, es no-evaluado
- [ ] Los 4 criterios preexistentes (schema / whatsapp / `geo_score<50` / perf con `field_data`) siguen funcionando
- [ ] Test con fixture de SalenteReal + test de no-regresión de los 4 criterios viejos

### Tarea G3: Cerrar la escotilla V5 **sin revertir BUG-6**

**Objetivo**: Distinguir "asset generado **y mencionado** en doc" de "asset generado **y silencioso**".

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:1237-1242` (`_JUSTIFIED_STATUSES`)
- `modules/quality_gates/publication_gates.py:1244-1373` (`_coverage_gate`)

**Criterios de aceptación**:
- [ ] `ASSET_GENERATED` **sigue en `_JUSTIFIED_STATUSES`** (no se revierte el fix BUG-6/N2 de 2026-07-25)
- [ ] Un pain con asset generado **y mencionado** en el doc ⟹ justificado (comportamiento actual, correcto)
- [ ] Un pain con asset generado **y NO mencionado** en el doc ⟹ **deja de contar como justificado**
- [ ] **Test anti-reversión obligatorio**: reproduce el caso Zione 2026-07-25 (botón de WhatsApp
      existente en producción) y verifica que **NO** se bloquea. Si este test falla, G3 reintrodujo BUG-6
- [ ] Test del caso SalenteReal: los 2 assets huérfanos de B1 (`indirect_traffic_optimization`,
      `analytics_setup_guide`) — generados y **no prometidos** — ya no pasan como justificados por la
      escotilla (si FASE-C los trató, verificar coherencia con esa decisión)
- [ ] ⚠️ **El gate sigue sin reconstruir la detección**: valida contra el ledger y el doc, no re-detecta

### Tarea G4: Cerrar la escotilla V9 (ledger vacío)

**Objetivo**: Unificar el tratamiento del ledger vacío.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:1336-1344` (`pain_ledger` fallback vacío → PASS)
- `modules/quality_gates/publication_gates.py:1295-1304` (`pain_ledger_resolved` vacío → BLOCKED)

**Criterios de aceptación**:
- [ ] Las dos rutas tratan el ledger vacío de forma **coherente entre sí**
- [ ] **Coherente con la decisión C1** de FASE-C sobre propuesta dinámica con ledger vacío (no inventar
      una tercera semántica)
- [ ] Un ledger vacío **no** pasa como PASS cuando debería ser BLOCKED
- [ ] Distingue **vacío** de **ausente** (lección SR-H2): ledger ausente ≠ ledger con cero entradas
- [ ] Estado `NOT_EVALUATED` de FASE-F usado si corresponde, en vez de PASS silencioso
- [ ] Tests de las 4 combinaciones: {fallback, resolved} × {vacío, ausente}

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `doc_audit_consistency` con datos | `tests/quality_gates/test_publication_gates.py` | Falla ante contradicción doc-vs-audit; pasa ante coincidencia |
| `gbp.reviews` como int | ídem | Acepta `986` (int) y `{"total": 986}` (dict) |
| `critical_recall` no vacuo | ídem | < 1.0 en fixture SalenteReal |
| PageSpeed ERROR califica | `tests/auditors/test_v4_comprehensive.py` | Verde |
| Banda GEO critical califica | ídem | Verde |
| No-regresión de los 4 criterios viejos | ídem | Verde |
| **Anti-reversión BUG-6** | `tests/quality_gates/test_coverage_gate_v5.py` | Caso Zione 2026-07-25 **NO** se bloquea |
| Generado y silencioso | ídem | Deja de contar como justificado |
| Ledger vacío (4 combinaciones) | ídem | Coherente con C1 de FASE-C |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848/2 + delta A-F preservado |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_coverage_gate_v5.py -v > temp/faseG_v5.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py -q > temp/faseG_gates.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/auditors/test_v4_comprehensive.py -q > temp/faseG_critical.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseG_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

⚠️ **NUNCA** correr `tests/commercial_documents` completo (~8GB).

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-G ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso
3. **`06-checklist-implementacion.md`** — fila FASE-G, NR1-NR4, trazabilidad V5/V9/V10 y eje 2 (candados rotos)
4. **`09-documentacion-post-proyecto.md`** — Sección B, D, E
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-G
   - **Decisiones Arquitectónicas**: (a) `doc_audit_consistency` con datos ausentes → `NOT_EVALUATED` o
     BLOCKED; (b) semántica de ledger vacío elegida y su coherencia con C1
   - **Confirmaciones**: V10 refuerza que `asset_confidence` es el único bloqueo duro (valida la decisión de FASE-D)
   - Lecciones (obligatorio: el péndulo D2→tautología→V5 es una lección de forma) + Métricas + Seguimientos
6. **`evidence/FASE-G/`** — logs de tests + fixture del caso Zione anti-reversión

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-G --desc "Ceguera de gates: doc_audit_consistency cableado + critical_recall no vacuo + escotillas V5/V9" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**, incluido el **anti-reversión BUG-6** (obligatorio)
- [ ] **NR1 cerrado**: `doc_audit_consistency` recibe datos y acepta `gbp.reviews` int
- [ ] **NR2 cerrado**: PageSpeed ERROR y banda GEO critical califican; `critical_recall < 1.0` en SalenteReal
- [ ] **NR3 cerrado**: V5 cerrada **sin** revertir BUG-6 — `ASSET_GENERATED` sigue en `_JUSTIFIED_STATUSES`
- [ ] **NR4 cerrado**: V9 unificada y coherente con la decisión C1 de FASE-C
- [ ] **Los 4 criterios viejos de `_identify_critical_issues` siguen funcionando**
- [ ] **El gate no reconstruye la detección** (anti-patrón DT4-N2)
- [ ] **V10 registrado como confirmación** de la decisión de FASE-D
- [ ] **`hard_contradictions` documentado como límite fuera de alcance**
- [ ] **Baseline preservado**: 848/2 + delta A-F
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7
- [ ] **Los 5 archivos de plan actualizados**
- [ ] **Evidencia preservada**: `evidence/FASE-G/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-G

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO quitar `ASSET_GENERATED` de `_JUSTIFIED_STATUSES`** — resucita BUG-6 (falso positivo CRÍTICO
      de Zione 2026-07-25)
- ❌ **NO hacer que el coverage gate re-detecte brechas** — los gates validan, no descubren (DT4-N2)
- ❌ **NO abordar `hard_contradictions`** — fuera del alcance del motor, documentado como límite
- ❌ **NO tocar los quirúrgicos V6/V7/V8/V11/V12/V13** — FASE-H. En particular **no tocar
      `pain_solution_mapper.py`** (conflicto de archivo, `dependencias-fases.md` §3 fija el orden G→H)
- ❌ **NO tocar `_coherence_gate`** ni `is_coherent` — ya cerrado en FASE-F
- ❌ **NO tocar la severidad de los gates** — FASE-D
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE
- ❌ **NO ejecutar un `v4complete` completo** — la única corrida E2E es FASE-I

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- `publication_gates.py` fue modificado por FASE-D y FASE-F: **re-verificar líneas** antes de editar
- Semántica «vacío ≠ ausente» en todos los cambios de estado (lección SR-H2)

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Ceguera de gates (Nivel 3.7). Cuatro defectos: doc_audit_consistency llegó sin datos y pasó
en verde; critical_recall=1.0 es vacuo; y el coverage gate tiene dos escotillas (V5 ASSET_GENERATED sin
mención en doc, V9 ledger vacío PASS vs BLOCKED).

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §3 (candados rotos), §12.3 V5/V9/V10, §12.5 Nivel 3.7
- TAUTOLOGÍA DE FONDO: coverage_no_silent_drop compara el ledger contra las brechas del doc y AMBOS
  salen de la MISMA llamada detect_pains (v4_asset_orchestrator.py:280; v4_diagnostic_generator.py:3178,
  DEP-03). La cura real fue FASE-A/B/C. G3/G4 cierran las escotillas que quedan — NO intentar que el
  gate detecte brechas que el ledger no registró (anti-patrón DT4-N2: los gates validan, no reconstruyen).
- FASE-A…F ✅. FASE-F modificó publication_gates.py:458 → re-verificar líneas antes de editar.

TAREAS:
1. G1 Cablear doc_audit_consistency (publication_gates.py:1464-1514 + caller en assessment_builder.py
   y/o main.py): audit_data y diagnostico_text deben LLEGAR. Check 2 acepta gbp.reviews como int (986).
   Con datos ausentes: NOT_EVALUATED o BLOCKED (decisión registrada, coherente con A1 de FASE-F).
2. G2 Ampliar _identify_critical_issues (v4_comprehensive.py:1789-1814): PageSpeed status=ERROR y banda
   GEO critical (29/100) deben calificar. critical_recall < 1.0 en fixture SalenteReal. Preservar
   semántica vacío≠ausente (SR-H2) y los 4 criterios viejos.
3. G3 Cerrar V5 SIN revertir BUG-6: distinguir "generado y mencionado en doc" de "generado y silencioso".
   ASSET_GENERATED SIGUE en _JUSTIFIED_STATUSES (:1237-1242).
4. G4 Cerrar V9: pain_ledger fallback vacío=PASS (:1336-1344) vs pain_ledger_resolved vacío=BLOCKED
   (:1295-1304) → tratamiento coherente, alineado con la decisión C1 de FASE-C.

⚠️ RESTRICCIÓN CRÍTICA G3 (anti-reversión):
La inclusión de ASSET_GENERATED fue el FIX DELIBERADO de BUG-6/N2 (Zione 2026-07-25): sin él, el
coverage gate bloqueaba Zione con el botón de WhatsApp existente en producción (falso positivo CRÍTICO).
Quitarlo sin más RESUCITA BUG-6. Es el segundo péndulo de la familia D2→tautología.
→ Test anti-reversión OBLIGATORIO que reproduce el caso Zione y verifica que NO se bloquea.

CRITERIOS:
- NR1: gate recibe datos + acepta gbp.reviews int
- NR2: PageSpeed ERROR y banda GEO critical califican; critical_recall < 1.0 en SalenteReal
- NR3: V5 cerrada SIN revertir BUG-6 (test anti-reversión verde)
- NR4: V9 unificada y coherente con C1
- Baseline 848/2 + delta A-F preservado; run_all_validations.py --quick 7/7

RESTRICCIONES:
- NO quitar ASSET_GENERATED de _JUSTIFIED_STATUSES; NO hacer que el gate re-detecte brechas
- NO abordar hard_contradictions (fuera de alcance del motor — documentar como límite)
- NO tocar V6/V7/V8/V11/V12/V13 ni pain_solution_mapper.py → FASE-H (orden forzoso G→H)
- NO tocar _coherence_gate (FASE-F) ni la severidad (FASE-D); NO tocar VERSION.yaml
- NO ejecutar v4complete completo (la única corrida E2E es FASE-I)
- V10 (G8 fuera de BLOCKING_GATE_NAMES → WARNING → ZIP procede) NO requiere acción: registrarla como
  CONFIRMACIÓN de que asset_confidence es el único bloqueo duro (valida la decisión de FASE-D)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (B/D/E), 10-analisis-post-implementacion.md (Decisiones: datos
ausentes en doc_audit, semántica ledger vacío · Confirmaciones: V10 · Lecciones: el péndulo
D2→tautología→V5), evidence/FASE-G/ (incl. fixture anti-reversión).
Luego: log_phase_completion.py --fase FASE-G --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-G.
```
