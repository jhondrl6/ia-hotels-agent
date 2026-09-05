# FASE-F — A4 oráculo único de presencia + A1 `skipped ≠ passed` + N11/P9 respetar `is_coherent`

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-F
**Objetivo**: Cerrar tres defectos de **decisión** (no de presentación): que un mismo resultado de gate
afirme que un asset falta y a la vez lo liste como presente (A4), que un gate saltado cuente como
pasado (A1), y que el gate de coherencia ignore el veredicto `is_coherent` que sus propios artefactos
declaran (N11/P9 — **la deuda más grave abierta**).
**Dependencias**: FASE-C ✅ (`no_breach = 0` cambia el insumo del oráculo), FASE-E ✅ (snapshot persistido es el insumo del oráculo único)
**Duración estimada**: 4-5 horas
**Complejidad técnica**: **MEDIA-ALTA**
**Modo de ejecución**: **DIRECTO** (no delegable — N11 es decisión arquitectónica)
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤45 iteraciones (R2 tope: 60)
**ACs que cierra**: AC10, AC11, AC12 · **Deudas**: H8, H9 (parcial), P9, A1, A4 · **Precondición del tribunal**: §10 #4

---

## Contexto

Los tres defectos comparten una forma: **el sistema tiene dos fuentes de verdad para la misma decisión
y elige la que no compromete**. A4: dos oráculos de presencia (decide el permisivo, narra el estricto).
A1: dos defaults para la misma clave de gate. N11: dos veredictos de coherencia (`coherence_score` y
`is_coherent`) y el gate lee solo el que pasa.

### A4 — Doble oráculo de presencia (verbatim del dossier §9.1)

- **Qué**: un mismo resultado de gate puede afirmar que un asset falta y a la vez listarlo como presente
  en producción.
- **Evidencia**: reproducido con nombres reales sobre SalenteReal — el resultado dice que **Schema Hotel**
  está `missing` y simultáneamente lo incluye en `present_assets`. Mecanismo: el oráculo **permisivo**
  (`PRODUCTION_PRESENT_STATUSES = ("exists", "exists_with_issues")`, `site_presence_checker.py:73`,
  decisión FASE-SR-E H7/L-SR3) es el que **decide**; el **estricto** es el que **escribe el mensaje**.
- **Consecuencia**: el humano (y el Bot 3) lee una narrativa que no corresponde con la decisión tomada.
  Misma forma de defecto que R2 (`site_verification_applied`, CONTEXT-BOTS §13).
- **Requisito**: **un solo oráculo para decidir y para narrar, o narrativa derivada de la decisión.**

**V15 lo confirma como mecanismo, no como contradicción**: la matriz tiene **6 NO_BREACH** pero el gate
reporta **3** — `_presence_resolved` absorbió 3 NO_BREACH (Schema Hotel, Schema Organization, FAQ)
moviéndolos a `present` con el oráculo permisivo. Por eso `details` dice «2 missing» (oráculo estricto)
mientras la cuenta de la matriz dice otra cosa. **Son dos etapas del mismo pipeline**, no datos
inconsistentes — es la reproducción exacta de A4.

⚠️ **Nota post-FASE-C**: si el punto 8 hizo `no_breach = 0` por construcción, la absorción de V15 ya no
tiene 6 entradas que absorber. **El defecto estructural sigue vivo** (dos oráculos) aunque su síntoma se
haya atenuado. No cerrar A4 solo porque el síntoma desapareció — FASE-I lo verificaría sobre una corrida
distinta y el defecto reaparecería en otro hotel.

### A1 — G9 se salta en verde (verbatim)

- **Qué**: si no existe `proposal_asset_matrix.json`, el gate de alignment de delivery se marca como pasado.
- **Evidencia**: `delivery_quality_report.py:250-257` → `{"passed": True, "gate": "G9", "skipped": True, "reason": "proposal_asset_matrix.json not found"}`. El summary (`:310-319`) cuenta `passed_count` sobre `gate_results.values()` ⟹ **un gate saltado se cuenta como gate pasado**. Hay además un **segundo default independiente** en `:325` (`{"passed": True, "gate": "G9"}`) para cuando la clave no existe.
- **Consecuencia**: un paquete sin matriz pasa el gate de delivery de forma **vacuamente verde**. Dos
  defaults para la misma clave = dos fuentes de verdad.
- **Requisito**: `skipped` no debe contar como `passed`; debe ser **`NOT_EVALUATED`** y visible en el acta.
  Unificar los dos defaults.
- **Calificación**: **latente, no observado** — en SalenteReal la matriz sí existía. Eso no lo hace menos
  real: es la misma forma que el NameError silencioso del gate `tier_c` y que `precision_tier`
  defaulteando a `"C"` bajo `except` desnudo (deuda P11).

⚠️ **Límite explícito**: FASE-D **no** tocó `BLOCKING_GATE_NAMES` (`delivery_quality_report.py:289`)
porque rige el ZIP (`main.py:3198` *"⛔ ZIP ABORTED"*) y pertenece al régimen de **delivery**, no de
publicación. Esta fase lo toca **solo** para que `skipped` no cuente como `passed` — **NO** para
re-clasificar severidades. Unificar los dos regímenes sigue siendo una decisión separada con su propio
radio de impacto.

### N11/P9 — El gate de coherencia ignora `is_coherent` (verbatim)

- Los **cuatro** artefactos de la corrida SalenteReal dicen `is_coherent: false` (incluido
  `asset_generation_report.json` ×2 — **V16**), y el paquete salió `READY_FOR_PUBLICATION` con
  `hotelsalentoreal_20260831.zip` de **46.552 bytes / 37 archivos**.
- **Mecanismo**: `publication_gates._coherence_gate` (`:458`) decide con **solo**
  `coherence_score >= threshold`. El módulo que **sí** lee `is_coherent` (`coherence_gate.py`) está
  **huérfano** — sin importadores fuera de sí mismo.
- **Causa del `false`**: `assets_are_justified 3/4 = 0.75` (dossier §5, §9.4).
- **Consecuencia grave**: **agregar errores al reporte de coherence no bloquea nada**, y ningún acta
  futura que se alimente de ese reporte hereda el veredicto real.
- **Requisito (§10 #4)**: *"el pipeline debe respetar `is_coherent` antes de que Bot 1 lo certifique."*
- **Deuda ROADMAP**: **P9** — calificada como **la más grave abierta**. Relacionada: **H8**
  (`publication_state.py` huérfano, como `coherence_gate.py`: conectar o eliminar).

### Interacción con FASE-C (crítica, no ignorar)

FASE-C debía disolver el `is_coherent = false` **estructural** (AC6) por la vía del punto 8. Si lo logró,
esta fase encuentra `is_coherent = true` en los fixtures nuevos — pero el **defecto del gate sigue
vivo**: sigue sin consultar el campo. Un `is_coherent = false` legítimo (por una incoherencia real, no
estructural) volvería a pasar en verde.

⟹ **F3 no es redundante con AC6.** AC6 cura la *causa* del false; AC12 cura la *ceguera* del gate.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-A — Fuente única de identidad | ✅ |
| FASE-B — Biyección triple mapa↔emisión↔narrativa | ✅ |
| FASE-C — Punto 8 propuesta dinámica | ✅ |
| FASE-D — Severidad 11+2 | ✅ |
| FASE-E — A2 snapshot + A6 asset_path | ✅ (ver `evidence/FASE-E/consumidores-snapshot.md`: rutas de reconstrucción vivas) |

### Base Técnica Disponible

- **Snapshot de presencia persistido** (FASE-E) — insumo del oráculo único
- **Inventario de consumidores y rutas de reconstrucción**: `evidence/FASE-E/consumidores-snapshot.md`
- **Severidad explícita** (FASE-D) — F2 debe respetar las listas `BLOCKING_GATE_NAMES` / `ADVISORY_GATE_NAMES` de publicación
- **Corpus histórico**: 27 corridas reales en `output/` (C2: ~10 al 100% ESTIMATED, 37%)
- **Sensibilidad de coherence** (si F3 la toca): pesos `1.5/1.0/1.5/0.5/1.0/2.0` (total 7.5,
  `coherence_validator.py:101-108`) ⟹ 0.2667 por unidad; headroom 0.08; score mínimo por check para
  mantener overall ≥ 0.8 = **0.7000**

---

## Tareas

### Tarea F1: A4/V15 — Un oráculo de presencia para decidir **y** narrar

**Objetivo**: Que la narrativa se derive de la decisión, no de un segundo criterio.

**Archivos afectados**:
- `modules/asset_generation/site_presence_checker.py:73` (`PRODUCTION_PRESENT_STATUSES`, oráculo permisivo)
- `modules/quality_gates/alignment_result.py:62` (`_presence_resolved`)
- `modules/quality_gates/alignment_result.py:222-276` (`_from_entries`)
- El sitio donde se escribe el mensaje con `present_assets` / `missing` (identificar por grep a partir de la evidencia de A4)

**Criterios de aceptación**:
- [ ] **Un solo oráculo**: el que decide es el que narra, o la narrativa se **deriva** de la decisión tomada
- [ ] El caso reproducido del dossier queda imposible por test: un resultado **no puede** afirmar que
      Schema Hotel está `missing` y a la vez listarlo en `present_assets`
- [ ] `details.missing_count` y el conteo de la matriz **ya no divergen**
- [ ] Las rutas de reconstrucción identificadas en FASE-E quedan reducidas a **una** (insumo de E4)
- [ ] ⚠️ **NO modificar la decisión FASE-SR-E H7/L-SR3** (`exists_with_issues` cuenta como presencia
      única) sin registrar el cambio como decisión arquitectónica — fue un fix deliberado, no un descuido
- [ ] ⚠️ **NO tocar la fórmula de `coverage_ratio`**

### Tarea F2: A1 — `skipped ≠ passed` y unificar los dos defaults de G9

**Objetivo**: Un gate no evaluado no es un gate pasado.

**Archivos afectados**:
- `modules/quality_gates/delivery_quality_report.py:250-257` (primer default, `"skipped": True`)
- `modules/quality_gates/delivery_quality_report.py:310-319` (summary que cuenta `passed_count`)
- `modules/quality_gates/delivery_quality_report.py:325` (segundo default independiente)
- `modules/quality_gates/delivery_quality_report.py:289,292,296` (`BLOCKING_GATE_NAMES` — **solo** para que `skipped` no cuente como `passed`)

**Criterios de acceptance**:
- [ ] Estado **`NOT_EVALUATED`** introducido y distinto de `passed` y de `failed`
- [ ] El summary (`:310-319`) **no** cuenta `skipped` como `passed_count`
- [ ] Los **dos defaults unificados** en uno solo
- [ ] El estado `NOT_EVALUATED` es **visible** en el reporte (no silencioso) — misma familia de
      lecciones que «no colapsar vacío con ausente» (SR-H2)
- [ ] `BLOCKING_GATE_NAMES` decide con `not passed` sobre estados **evaluados**; un `NOT_EVALUATED`
      **no bloquea** pero **tampoco figura como pasado**
- [ ] ⚠️ **NO re-clasificar severidades** en este tuple (es régimen de delivery, no de publicación)

### Tarea F3: N11/P9 — El gate de coherencia respeta `is_coherent`

**Objetivo**: Cerrar la deuda **P9**, la más grave abierta.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:458` (`_coherence_gate`)
- `modules/quality_gates/publication_gates.py:1855` (`_extract_coherence_score`)
- `modules/quality_gates/coherence_gate.py` (huérfano — **conectar o eliminar**)
- `modules/quality_gates/publication_state.py` (huérfano — deuda **H8**: conectar o eliminar)
- `modules/commercial_documents/coherence_validator.py:185-188` (donde se computa `is_coherent = len(errors) == 0 and overall_score >= threshold`)

**Criterios de aceptación**:
- [ ] **Decisión arquitectónica explícita y registrada** entre las dos opciones del dossier §12.5 Nivel 2.6:
      **(a)** el gate **respeta** `is_coherent`, o **(b)** el campo se **elimina** a favor de sus checks.
      No dejar la doble fuente
- [ ] Si se elige (a): un paquete con `is_coherent: false` **no puede** salir `READY_FOR_PUBLICATION`
- [ ] Si se elige (b): el campo desaparece de los **cuatro** artefactos que hoy lo declaran, y sus
      checks subyacentes (`assets_are_justified` 3/4) pasan al gate de forma explícita
- [ ] `coherence_gate.py` **conectado o eliminado** — no huérfano
- [ ] `publication_state.py` (H8) **conectado o eliminado** — no huérfano
- [ ] Test de reproducción del caso SalenteReal: `coherence_score = 0.88` + `is_coherent: false` ⟹
      el nuevo comportamiento esperado
- [ ] ⚠️ **NO relajar el umbral de 0.8** para compensar

### Tarea F4: Medir el impacto sobre el corpus histórico

**Objetivo**: Saber cuántas corridas cambian de veredicto **antes** de cerrar la fase.

**Archivos afectados**: ninguno (medición) + salida nueva `evidence/FASE-F/impacto-corpus.md`

**Criterios de aceptación**:
- [ ] Las **27 corridas** reales de `output/` re-evaluadas bajo el nuevo comportamiento (F1+F2+F3)
- [ ] Tabla: corrida → veredicto antes → veredicto después → qué cambio lo movió (F1, F2 o F3)
- [ ] ⚠️ **Atención esperada**: las ~10 corridas (37%) con 100% de assets ESTIMATED y
      `coherence_score_final = None` (todas `hotel_visperas`/`hotel_vísperas`, 2026-03-25 → 2026-04-05)
      **deben** seguir bloqueadas — si alguna pasa, F3 se pasó de permisivo
- [ ] Si algún veredicto cambia de bloqueado a listo, **justificación explícita** en el informe
- [ ] Salida escrita en `evidence/FASE-F/impacto-corpus.md`

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Oráculo único (anti-A4) | `tests/quality_gates/test_alignment_result.py` | Falla si un resultado dice `missing` y lista en `present_assets` |
| Narrativa derivada de la decisión | ídem | `details.missing_count` == conteo de la matriz |
| `skipped ≠ passed` (anti-A1) | `tests/quality_gates/test_delivery_quality_report.py` | Gate saltado → `NOT_EVALUATED`, no cuenta en `passed_count` |
| Default único de G9 | ídem | Falla si reaparece un segundo default |
| Reproducción SalenteReal (anti-N11) | `tests/quality_gates/test_publication_gates.py` | `score 0.88` + `is_coherent: false` ⟹ comportamiento nuevo |
| Corpus de 27 corridas | `tests/` o script de medición | Las ESTIMATED siguen bloqueadas |
| Baseline | `tests/quality_gates` + `tests/asset_generation` | 848/2 + delta A/B/C/D/E preservado |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_alignment_result.py tests/quality_gates/test_delivery_quality_report.py -v > temp/faseF_oracle.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py -q > temp/faseF_coherence.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseF_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
grep -rn "import coherence_gate\|from.*coherence_gate" modules/ main.py   # huérfano antes; conectado o eliminado después
grep -rn "import publication_state\|from.*publication_state" modules/ main.py   # H8
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-F ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso
3. **`06-checklist-implementacion.md`** — fila FASE-F, AC10/AC11/AC12, trazabilidad A1/A4/V15/V16/N11 y deudas P9/H8/H9
4. **`09-documentacion-post-proyecto.md`** — Sección B, D, E
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-F
   - **Decisiones Arquitectónicas** (obligatorias en esta fase): (a) respetar vs eliminar `is_coherent`;
     (b) conectar vs eliminar `coherence_gate.py`; (c) conectar vs eliminar `publication_state.py` (H8);
     (d) si se modificó la decisión FASE-SR-E H7/L-SR3
   - Lecciones + Métricas + Seguimientos
6. **`evidence/FASE-F/`** — `impacto-corpus.md` + logs de tests

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-F --desc "Oraculo unico presencia (A4) + skipped!=passed (A1) + gate respeta is_coherent (N11/P9)" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: oráculo único, `skipped ≠ passed`, reproducción SalenteReal
- [ ] **AC10 cerrado**: un oráculo decide **y** narra; `missing_count` y matriz coinciden
- [ ] **AC11 cerrado**: `NOT_EVALUATED` existe, no cuenta como passed, es visible
- [ ] **AC12 cerrado**: decisión sobre `is_coherent` tomada, implementada y **registrada**
- [ ] **`coherence_gate.py` ya no es huérfano** (conectado o eliminado)
- [ ] **`publication_state.py` (H8) ya no es huérfano** (conectado o eliminado)
- [ ] **Impacto sobre las 27 corridas medido** en `evidence/FASE-F/impacto-corpus.md`
- [ ] **Las ~10 corridas ESTIMATED siguen bloqueadas**
- [ ] **Umbral de coherence 0.8 intacto**
- [ ] **Fórmula de `coverage_ratio` intacta**
- [ ] **Baseline preservado**: 848/2 + delta A/B/C/D/E
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7 · `validate_agents_md.py` 6/0
- [ ] **Los 5 archivos de plan actualizados** (con las 4 Decisiones Arquitectónicas)
- [ ] **Evidencia preservada**: `evidence/FASE-F/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-F

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO re-clasificar severidades en `delivery_quality_report.py:289`** — es régimen de delivery.
      Solo `skipped ≠ passed`
- ❌ **NO tocar la fórmula ni el denominador de `coverage_ratio`** — interruptor global, bloquea en
      10/10 configuraciones medidas
- ❌ **NO cerrar las escotillas V5/V9 del `_coverage_gate`** — FASE-G
- ❌ **NO cablear `doc_audit_consistency`** ni ampliar `_identify_critical_issues` — FASE-G
- ❌ **NO tocar `pain_solution_mapper.py`** — FASE-H (y conflicto de archivo con G)
- ❌ **NO relajar el umbral de coherence 0.8**
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE
- ❌ **NO ejecutar un `v4complete` completo** — la única corrida E2E es FASE-I. F4 re-evalúa
      **artefactos ya persistidos**, no corre el pipeline

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- F4 sobre 27 corridas: procesar artefactos en lote con script temporal en `temp/`, no a mano
- Verificar premisas contra salidas reales: el dossier fue validado el 2026-09-03, pero FASE-C/D/E ya
  movieron código — re-verificar línea por línea antes de editar

---

## Prompt de Ejecución

```
Actúa como arquitecto de software senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Cerrar tres defectos de DECISIÓN con doble fuente de verdad:
A4 (dos oráculos de presencia: decide el permisivo, narra el estricto), A1 (gate saltado cuenta como
pasado, con dos defaults independientes) y N11/P9 (el gate de coherencia ignora is_coherent — la deuda
más grave abierta).

CONTEXTO:
- Plan: /.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §9.1 A1/A4 (verbatim), §9.2 B5/N11, §12.3 V15/V16, §12.5 Nivel 2 (puntos 5 y 6), §10 #4
- N11: los CUATRO artefactos de SalenteReal dicen is_coherent:false (causa: assets_are_justified 3/4)
  y el paquete salió READY_FOR_PUBLICATION con ZIP de 46.552 B / 37 archivos. _coherence_gate
  (publication_gates.py:458) decide con SOLO coherence_score >= threshold; coherence_gate.py (que sí
  lee is_coherent) está HUÉRFANO.
- V15: la matriz tiene 6 NO_BREACH pero el gate reporta 3 — _presence_resolved absorbió 3
  (Schema Hotel, Schema Organization, FAQ) con el oráculo permisivo. Dos etapas del mismo pipeline.
- A1: delivery_quality_report.py:250-257 → {"passed":True,"gate":"G9","skipped":True,...}; summary
  :310-319 cuenta passed_count sobre gate_results.values(); segundo default independiente en :325.
- FASE-A/B/C/D/E ✅. Insumo de E4: evidence/FASE-E/consumidores-snapshot.md (rutas de reconstrucción vivas)
- Sensibilidad coherence: pesos 1.5/1.0/1.5/0.5/1.0/2.0 (total 7.5) → 0.2667/unidad; headroom 0.08

TAREAS:
1. F1 Oráculo único (A4/V15): site_presence_checker.py:73, alignment_result.py:62/:222-276 + el sitio
   que escribe present_assets/missing. Narrativa DERIVADA de la decisión. Test: imposible afirmar
   "Schema Hotel missing" y a la vez listarlo en present_assets.
2. F2 skipped≠passed (A1): delivery_quality_report.py:250-257/:310-319/:325 → estado NOT_EVALUATED
   distinto de passed y failed, visible, y los DOS defaults unificados en uno.
3. F3 N11/P9: DECIDIR (a) respetar is_coherent o (b) eliminarlo a favor de sus checks. Implementar.
   coherence_gate.py y publication_state.py (H8): conectar o eliminar, no huérfanos.
   Test de reproducción: score 0.88 + is_coherent:false.
4. F4 Medir impacto sobre las 27 corridas reales de output/. Salida: evidence/FASE-F/impacto-corpus.md

CRITERIOS:
- AC10: un oráculo decide y narra; details.missing_count == conteo de la matriz
- AC11: NOT_EVALUATED no cuenta como passed y es visible
- AC12: paquete con is_coherent:false NO puede salir READY_FOR_PUBLICATION (o el campo se elimina con
  sus checks explicitados en el gate)
- Las ~10 corridas (37%) con 100% assets ESTIMATED y coherence_score_final=None SIGUEN bloqueadas
- Baseline 848/2 + delta A/B/C/D/E preservado; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO re-clasificar severidades en delivery_quality_report.py:289 (régimen de DELIVERY, no publicación) —
  solo skipped≠passed
- NO tocar la fórmula ni el denominador de coverage_ratio (interruptor global, bloquea en 10/10 medidas)
- NO cerrar escotillas V5/V9 del _coverage_gate, NO cablear doc_audit_consistency, NO ampliar
  _identify_critical_issues → FASE-G
- NO tocar pain_solution_mapper.py → FASE-H
- NO relajar el umbral de coherence 0.8; NO tocar VERSION.yaml
- NO ejecutar un v4complete completo: F4 re-evalúa artefactos YA persistidos (script en temp/)
- NO modificar la decisión FASE-SR-E H7/L-SR3 (exists_with_issues como presencia única) sin registrarla
  como Decisión Arquitectónica
- Si AC6 de FASE-C ya hizo is_coherent=true en fixtures nuevos, F3 NO es redundante: el defecto del gate
  sigue vivo (sigue sin consultar el campo)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (B/D/E), 10-analisis-post-implementacion.md con las 4 Decisiones
Arquitectónicas OBLIGATORIAS (is_coherent respetar/eliminar · coherence_gate.py · publication_state.py ·
si se tocó FASE-SR-E), evidence/FASE-F/.
Luego: log_phase_completion.py --fase FASE-F --desc "..." --check-manual-docs  (SIN --release).
Commit referenciando FASE-F.
```
