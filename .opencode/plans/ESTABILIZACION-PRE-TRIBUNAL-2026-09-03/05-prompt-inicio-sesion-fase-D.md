# FASE-D — Severidad explícita de publication gates (H10, 11 blocking + 2 advisory)

**ID**: ESTABILIZACION-PRE-TRIBUNAL-2026-09-03 / FASE-D
**Objetivo**: Que los 13 publication gates tengan severidad explícita. **11 blocking + 2 advisory**
(`content_quality`, `proposal_asset_alignment`). `asset_confidence` **conserva su bloqueo**. Las dos
mitades — conductual y documental — se implementan **en el mismo commit**.
**Dependencias**: FASE-A ✅ (la severidad clasifica gates cuyo insumo deriva del registro canónico)
**Duración estimada**: 2-3 horas
**Complejidad técnica**: **MEDIA**
**Modo de ejecución**: **MIXTO** — estructura de severidad DIRECTO; corrección documental + candado de regresión DELEGABLE
**Skill**: `phased_project_executor.md` v2.18.0
**Presupuesto**: ≤35 iteraciones (R2 tope: 60)
**ACs que cierra**: AC7, AC8

---

## Contexto

Hoy el código **nunca implementó** la distinción que sus propios docstrings prometen:

- `publication_gates.py:4` dice literalmente *"This module implements 13 publication gates (10 blocking + 3 advisory)"*
- `publication_gates.py:162` dice *"This class manages 10 blocking gates and 3 advisory gates"*
- `self.gates` (`publication_gates.py:181-195`) es un **dict plano de 13** sin estructura blocking/advisory
- `check_publication_readiness` (`:1919`) decide con `blocking_gates = [r for r in results if not r.passed]` (`:1967`) ⟹ **los 13 bloquean**
- `is_ready_for_publication` (`:227`) solo aparece en el docstring (`:169`) y en tests

`AGENTS.md` repite el error en la tabla Módulos Activos (fila `quality_gates/`) y en el bloque FASE 4.5.

### La decisión ya está medida y cerrada

Memoria de proyecto `decision-advisory-gates-2-no-3` + dossier §8.3: **advisory = 2**, no 3.

**Por qué `asset_confidence` NO se demote**: su hard-block es hoy el **único mecanismo** que vuelve
no-entregable un paquete Tier C. Relajar el código para coincidir con el docstring dejaría salir a
entrega el **14% del histórico** — 4 de 29 corridas (corpus real corregido por C2: **27 corridas**,
~10 al 100% ESTIMATED, **37%**), todas `hotel_visperas`/`hotel_vísperas`, 2026-03-25 → 2026-04-05 — con
**100% de assets ESTIMATED y `coherence_score_final = None`**. Exactamente lo que P6.5 y el primer piso
del Juez existen para impedir.

**Por qué `proposal_asset_alignment` SÍ puede ser advisory**: su bloqueo es **redundante**.
`coverage_ratio = effective/(effective+unresolved)` ⟹ `coverage == 1.0 ⟺ passed == True` (tautología),
medido en 10 configuraciones con `coverage_ratio = 1.000` y `unresolved = 0`.

> ⚠️ **Nota post-FASE-C**: si FASE-C disolvió la tautología (AC5), la justificación de
> `proposal_asset_alignment` como advisory **cambia de base** — ya no es "redundante porque es
> tautológico" sino "redundante porque el veredicto bloqueante vive en `unresolved`". **Verificar en D1
> que la justificación sigue sosteniéndose** tras el punto 8 y registrar la nueva formulación en
> `10-analisis` §Decisiones. Si ya NO se sostiene, escalar al usuario antes de demoter el gate.

### Restricción de orden (memoria `decision-advisory-gates-2-no-3`)

Esta deuda está registrada en ROADMAP v4.2 como **H10** (§13.2, registro de deuda de herramienta — **no
es una sub-fase de FASE T**) y tiene dos mitades que **no se pueden separar en el tiempo**:

- **Mitad conductual** — que 2 de los 13 dejen de bloquear en `check_publication_readiness`. Es **T0.1**,
  la primera precondición medida de FASE T (ROADMAP §7.2).
- **Mitad documental** — los docstrings `:4` y `:162` + `AGENTS.md`.

⟹ **Corregir solo los docstrings antes del comportamiento cambia una falsedad por otra**: hoy afirman
10+3 cuando el código bloquea con los 13; escribir 11+2 sin tocar `check_publication_readiness`
afirmaría 11+2 cuando siguen bloqueando los 13. **La corrección documental va montada en la conductual,
nunca por delante.** AC7 y AC8 se certifican juntas o ninguna.

### Estado de Fases Anteriores

> ⚠️ **Corregido 2026-09-03, en la ejecución de FASE-D.** Esta tabla afirmaba
> «FASE-B ✅ / FASE-C ✅» y era **falsa**: `06-checklist-implementacion.md` y
> `git log` registraban **solo FASE-A** completada. **La fuente única del estado es
> `06-checklist-implementacion.md`**, no esta tabla copiada en cada prompt (los prompts
> de C, E y F repiten el mismo error → seguimiento **S23** en `10-analisis`).

| Fase | Estado real al ejecutar D | Impacto en FASE-D |
|------|---------------------------|-------------------|
| FASE-A — Fuente única de identidad | ✅ Completada (2026-09-03) | Es la **única dependencia dura** de D |
| FASE-B — Biyección triple mapa↔emisión↔narrativa | 🟡 **Cerrada en paralelo** (otra sesión, 2026-09-03 16:45) | Ninguno en D, pero sí en el árbol compartido — ver riesgo abajo |
| FASE-C — Punto 8 propuesta dinámica | ⬜ Pendiente | **No re-verifica la nota post-C** — ver abajo |

⚠️ **Riesgo de concurrencia (hallazgo de esta sesión, L-D1 + S21)**: FASE-B y FASE-D se
ejecutaron **a la vez sobre el mismo working tree**, violando R1 del executor («una fase
por sesión»). No chocaron porque `dependencias-fases.md` §3 les asigna archivos disjuntos,
pero el commit de FASE-D tuvo que construirse con `git add` explícito de 15 rutas para no
arrastrar el trabajo en vuelo de B. **Dos sesiones commiteando a la vez sobre un árbol
limpio compartido es una condición de carrera**, no una coincidencia inocua.

**Por qué D pudo correr sin B ni C**: `dependencias-fases.md` §2 fija la dependencia dura
de D solo en A y declara «D y E están fuera del camino crítico y pueden ejecutarse en
cualquier hueco tras A y B respectivamente».

**Consecuencia sobre la nota post-FASE-C**: al no haber corrido C, la tautología de
`coverage_ratio` (§8.3 del dossier) **sigue intacta** ⟹ la justificación de
`proposal_asset_alignment` como advisory se sostiene hoy **en su base original**
(«redundante porque es tautológico»), no en la reformulada. Medido en
`evidence/FASE-D/faseD_contrafactual.py`: 0 flips de `ready` sobre la corrida real
disponible. **La re-verificación sigue pendiente para cuando C cierre AC5** → seguimiento
S24 en `10-analisis`.

### Base Técnica Disponible

- **Patrón a copiar** (el único lugar del repo donde la distinción ya existe):
  `modules/quality_gates/commercial_gate.py:99` `BLOCKING_GATE_IDS = [` y `:108` `WARNING_GATE_IDS = [`
- **Consumidor nombrado**: `modules/quality_gates/human_checklist_generator.py` (≤10 items derivados)
- **Baseline dossier §8.6**: 140 passed, 1 skipped, 8 warnings en ~1.23s sobre los 7 archivos de tests
  de alignment/gates (141 tests, **32 asserts de bloqueo**) — ⚠️ esos 32 asserts son los que esta fase
  va a cambiar de comportamiento
- **Costo esperado declarado**: ~6 tests específicos de alignment a actualizar
- **Candados existentes**: **0 tests** referencian `BLOCKING_GATE_NAMES` y ningún test de
  `tests/regression/` ni `tests/e2e/` fija la lista advisory

---

## Tareas

### Tarea D1: Estructura de severidad (DIRECTO)

**Objetivo**: Implementar la distinción blocking/advisory copiando el patrón de `commercial_gate.py:99-113`.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:181-195` (`self.gates`, dict plano de 13)
- `modules/quality_gates/publication_gates.py:1919` `check_publication_readiness`, específicamente `:1967-1968`
- `modules/quality_gates/publication_gates.py:239-249` `get_blocking_gates`
- `modules/quality_gates/publication_gates.py:227` `is_ready_for_publication` (hoy huérfano de producción: solo en docstring `:169` y tests) — decidir si se conecta o se elimina, y registrarlo

**Criterios de aceptación**:
- [ ] Estructura explícita `BLOCKING_GATE_NAMES` / `ADVISORY_GATE_NAMES` a nivel de módulo, copiando
      `commercial_gate.py:99-113`
- [ ] Las dos listas suman **13** y son disjuntas
- [ ] `ADVISORY_GATE_NAMES == {"content_quality", "proposal_asset_alignment"}`
- [ ] **`asset_confidence` está en `BLOCKING_GATE_NAMES`**
- [ ] `check_publication_readiness:1967-1968` filtra por **severidad**, no por `not r.passed` plano
- [ ] `get_blocking_gates:239-249` consume la misma estructura (no una segunda copia)
- [ ] Los advisory fallidos se reportan con estado **WARNING** pero no impiden `ready = True`
- [ ] Los 32 asserts de bloqueo del baseline quedan actualizados y el nuevo comportamiento testeado
- [ ] **Justificación de `proposal_asset_alignment` como advisory re-verificada post-FASE-C** (ver nota
      del Contexto) y registrada

### Tarea D2: Piso bajo advisory + consumidor nombrado (DIRECTO)

**Objetivo**: Cerrar los dos requisitos que el dossier §8.4 declara **inseparables** de D1 (riesgos B y C).

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:660` `_content_quality_gate`
- `modules/quality_gates/publication_gates.py:842` `_proposal_asset_alignment_gate`
- `modules/quality_gates/human_checklist_generator.py`
- `modules/quality_gates/delivery_quality_report.py` — cable del WARNING (ver criterio F7 abajo)

**Criterios de aceptación**:
- [ ] **Piso explícito (riesgo B)**: un advisory sin umbral mínimo deja pasar en silencio coberturas de
      **0.125** (medido, §9.2 B4). Definir un piso bajo el cual el advisory **degrada a blocking**, o
      justificar por escrito por qué no hace falta. La justificación va en `10-analisis` §Decisiones
- [ ] **Divulgación con consumidor nombrado (riesgo C)**: el WARNING debe aterrizar en
      `human_checklist_generator.py` (≤10 items). *"Un advisory que no entra en un artefacto que el
      humano lee es indistinguible de un advisory que no existe."*
- [ ] ⚠️ **Auditoría del plan (F7) — el cable no existe hoy**: `human_checklist_generator` consume
      `DeliveryQualityReport` (coverage/specificity/evidence/blocking) pero `content_quality` **no está
      expuesto** en ese reporte — el WARNING del gate `content_quality` no llega al checklist por
      ninguna ruta actual. Cablearlo (exponer advisory WARNING en `delivery_quality_report` o consumir
      los resultados del gate directo) es **parte de D2**, no un supuesto
- [ ] Test que verifica que un advisory fallido **aparece** en el checklist humano generado
- [ ] Test del piso: un advisory por debajo del piso degrada a blocking
- [ ] Nota: el `acta_revision.md` del Bot 5 (CONTEXT-BOTS §5) **aún no existe** — el consumidor mínimo
      hoy es `human_checklist_generator.py`. NO construir el acta en esta fase (es el tribunal, que va
      DESPUÉS de este plan)

### Tarea D3: Mitad documental MONTADA en D1 (DELEGABLE, mismo commit)

**Objetivo**: Corregir docstrings y `AGENTS.md` a "11 blocking + 2 advisory" **en el mismo commit que D1**.

**Archivos afectados**:
- `modules/quality_gates/publication_gates.py:4` — *"This module implements 13 publication gates (10 blocking + 3 advisory)"*
- `modules/quality_gates/publication_gates.py:162` — *"This class manages 10 blocking gates and 3 advisory gates"*
- `AGENTS.md` — tabla **Módulos Activos**, fila `quality_gates/` (hoy lista explícitamente *"blocking (10): ... advisory (3): content_quality, asset_confidence, proposal_asset_alignment"*)
- `AGENTS.md` — bloque **FASE 4.5: PUBLICATION GATES** del flujo v4

**Criterios de aceptación**:
- [ ] Ambos docstrings dicen **11 blocking + 2 advisory**
- [ ] La fila `quality_gates/` de `AGENTS.md` lista los 11 blocking por nombre y los 2 advisory por
      nombre, **sin `asset_confidence` entre los advisory**
- [ ] El bloque FASE 4.5 refleja la misma clasificación
- [ ] `python scripts/validate_agents_md.py` → **6 PASS / 0 FAIL** con `missing_roadmap` vacío
- [ ] ⚠️ **Verificación de commit**: `git show --stat HEAD` debe incluir `publication_gates.py` **y**
      `AGENTS.md` en el mismo commit. Si quedaron separados, la fase **no está completa**

**Delegable**: esta tarea replica una decisión ya tomada (no la diseña). El subagente recibe la lista
exacta de strings a corregir.

### Tarea D4: Candado de regresión sobre ambas listas (DELEGABLE)

**Objetivo**: Hoy hay **0 tests** que fijen la pertenencia. Sin candado, el cuarto régimen reaparece.

**Archivos afectados**:
- `tests/quality_gates/test_gate_severity_lists.py` (nuevo)

**Criterios de aceptación**:
- [ ] Test que falla si `asset_confidence` aparece en `ADVISORY_GATE_NAMES`
- [ ] Test que falla si las dos listas no suman exactamente 13 o no son disjuntas
- [ ] Test que falla si `check_publication_readiness` vuelve a decidir con `not r.passed` plano
      (verificación estructural — guardián AST, no regex)
- [ ] Test que falla si aparece una tercera lista de severidad en otro módulo de publicación
      (anti-cuarto-régimen)
- [ ] **NO fija los nombres de los 13 en un literal inmutable** — fija la **pertenencia de
      `asset_confidence` a blocking** y la **cardinalidad**, que es lo que la decisión medida establece

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Listas de severidad | `tests/quality_gates/test_gate_severity_lists.py` | Verde; falla si `asset_confidence` se demote |
| `check_publication_readiness` filtra por severidad | `tests/quality_gates/test_publication_gates.py` (existente) | Advisory fallido ⟹ `ready = True` + WARNING |
| Piso bajo advisory | ídem | Advisory bajo el piso ⟹ degrada a blocking |
| Consumidor nombrado | `tests/quality_gates/test_human_checklist_generator.py` | Advisory WARNING aparece en el checklist |
| Baseline alignment/gates | 7 archivos | 140 passed / 1 skipped → actualizado (~6 tests + 32 asserts) |
| Baseline dossier §8.6 | `tests/quality_gates` + `tests/asset_generation` | 848 passed / 2 skipped + delta A/B/C preservado |
| Validadores | `scripts/` | `run_all_validations.py --quick` 7/7 · `validate_agents_md.py` 6 PASS / 0 FAIL |

**Comando de validación**:
```bash
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_gate_severity_lists.py -v > temp/faseD_severity.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_publication_gates.py tests/quality_gates/test_human_checklist_generator.py -q > temp/faseD_gates.txt 2>&1
./venv/Scripts/python.exe -m pytest tests/quality_gates tests/asset_generation -q > temp/faseD_baseline.txt 2>&1
./venv/Scripts/python.exe scripts/validate_agents_md.py
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
grep -n "10 blocking\|3 advisory" modules/quality_gates/publication_gates.py AGENTS.md || echo "OK: 0 strings stale"
git show --stat HEAD   # debe incluir publication_gates.py Y AGENTS.md
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — marcar FASE-D ✅, fecha, notas
2. **`README.md` del plan** — tabla de progreso
3. **`06-checklist-implementacion.md`** — fila FASE-D, AC7/AC8, trazabilidad H10 + deuda ROADMAP §13.2
4. **`09-documentacion-post-proyecto.md`** — Sección B (severidad explícita), D (métricas),
   **E (archivos afiliados: `AGENTS.md` modificado)**
5. **`10-analisis-post-implementacion.md`**
   - Resumen de Ejecución: fila FASE-D
   - **Decisiones Arquitectónicas**: (a) piso bajo advisory o justificación de su ausencia;
     (b) `is_ready_for_publication` conectado o eliminado; (c) re-formulación de la justificación de
     `proposal_asset_alignment` como advisory post-FASE-C
   - Lecciones + Métricas + Seguimientos
6. **`evidence/FASE-D/`** — logs de tests + captura del `git show --stat` que prueba el commit único

**Cierre con script**:
```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-D --desc "Severidad explicita publication gates 11 blocking + 2 advisory (H10/T0.1)" --check-manual-docs
```
**SIN `--release`.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: listas de severidad, piso, consumidor nombrado
- [ ] **AC7 cerrado**: 11 blocking + 2 advisory en código; `asset_confidence` en blocking;
      `check_publication_readiness` filtra por severidad
- [ ] **AC8 cerrado**: docstrings `:4`/`:162` + `AGENTS.md` (2 lugares) corregidos
- [ ] **MISMO COMMIT**: `git show --stat HEAD` incluye `publication_gates.py` **Y** `AGENTS.md`
- [ ] **`grep "10 blocking\|3 advisory"`** → 0 resultados en `publication_gates.py` y `AGENTS.md`
- [ ] **Piso bajo advisory definido o justificado por escrito**
- [ ] **WARNING aterriza en `human_checklist_generator.py`** con test que lo verifica
- [ ] **Candado de regresión** existe (antes había 0 tests)
- [ ] **Baseline preservado**: 848/2 + delta A/B/C (los ~6 tests y 32 asserts actualizados están explicados)
- [ ] **Validaciones**: `run_all_validations.py --quick` 7/7 · `validate_agents_md.py` 6/0
- [ ] **Los 5 archivos de plan actualizados**
- [ ] **Evidencia preservada**: `evidence/FASE-D/`
- [ ] **`log_phase_completion.py` ejecutado SIN `--release`**
- [ ] **Commit hecho** referenciando FASE-D

---

## Restricciones

**Alcance — qué NO está en esta fase**:
- ❌ **NO demoter `asset_confidence`** (dossier §8.5 + memoria). Es el único mecanismo que vuelve
      no-entregable un paquete Tier C
- ❌ **NO tocar `delivery_quality_report.py:289` `BLOCKING_GATE_NAMES`** (§8.4 tarea 3). Ese tuple rige
      el ZIP (`main.py:3198` *"⛔ ZIP ABORTED"*) y pertenece a un régimen **distinto** — delivery, no
      publicación. Unificarlos es una decisión separada con su propio radio de impacto. FASE-F lo toca
      **solo** por A1 (`skipped ≠ passed`), no por severidad
- ❌ **NO implementar S2.3**
- ❌ **NO agregar el 8º servicio**
- ❌ **NO construir el `acta_revision.md` del Bot 5** — el tribunal va DESPUÉS de este plan
- ❌ **NO corregir los docstrings en un commit anterior al comportamiento** — la restricción de orden es
      el núcleo de esta fase
- ❌ **NO tocar `_coherence_gate`** (`:458`) — FASE-F (N11)
- ❌ **NO tocar `_coverage_gate`** (`:1244`) — FASE-G
- ❌ **NO tocar `_doc_audit_consistency_gate`** (`:1464`) — FASE-G
- ❌ **NO tocar `VERSION.yaml`** — FASE-RELEASE

**Restricciones técnicas**:
- Python del venv: `./venv/Scripts/python.exe`
- Pytest en lotes pequeños con salida a archivo; **nunca** `tests/commercial_documents` completo
- Al editar `publication_gates.py`, recordar que FASE-F y FASE-G también lo tocarán: confinar los
  cambios a `self.gates` / `check_publication_readiness` / `get_blocking_gates` / docstrings
  (`dependencias-fases.md` §3)

---

## Prompt de Ejecución

```
Actúa como ingeniero senior en el repo iah-cli (Python, Windows, ./venv/Scripts/python.exe).

OBJETIVO: Severidad explícita en los 13 publication gates → 11 blocking + 2 advisory.
Advisory = {content_quality, proposal_asset_alignment}. asset_confidence CONSERVA su bloqueo.
Mitad conductual + mitad documental en el MISMO COMMIT.

CONTEXTO:
- Plan: .opencode/plans/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/
- Dossier §8.3 (decisión), §8.4 (tareas), §8.5 (qué NO hacer)
- Memoria: decision-advisory-gates-2-no-3
- Estado actual: publication_gates.py:4 y :162 dicen "10 blocking + 3 advisory"; self.gates (:181-195)
  es dict plano de 13; check_publication_readiness (:1919) decide con
  `blocking_gates = [r for r in results if not r.passed]` (:1967) → los 13 bloquean hoy
- Patrón a copiar (único lugar del repo donde ya existe): commercial_gate.py:99 BLOCKING_GATE_IDS
  y :108 WARNING_GATE_IDS
- Consumidor nombrado: human_checklist_generator.py
- FASE-A/B/C ✅ completadas

TAREAS:
1. D1 (DIRECTO) Estructura BLOCKING_GATE_NAMES/ADVISORY_GATE_NAMES + consumo en
   check_publication_readiness:1967-1968 y get_blocking_gates:239-249. Advisory fallido → WARNING,
   no impide ready=True. Decidir sobre is_ready_for_publication (:227, hoy solo en docstring :169 y tests).
2. D2 (DIRECTO) Piso bajo advisory (riesgo B: sin piso pasa en silencio coverage 0.125) + divulgación
   en human_checklist_generator.py (riesgo C). Ambos INSEPARABLES de D1.
3. D3 (DELEGABLE) Corregir publication_gates.py:4, :162 y AGENTS.md (tabla Módulos Activos fila
   quality_gates/ + bloque FASE 4.5) a "11 blocking + 2 advisory". MISMO COMMIT que D1.
4. D4 (DELEGABLE) Candado de regresión: tests/quality_gates/test_gate_severity_lists.py. Hoy hay 0 tests.

CRITERIOS:
- AC7: 11 blocking + 2 advisory en código; asset_confidence EN BLOCKING; filtrado por severidad
- AC8: docstrings + AGENTS.md corregidos EN EL MISMO COMMIT (verificar con git show --stat HEAD)
- Baseline 848/2 + delta A/B/C preservado; validate_agents_md.py 6/0; run_all_validations.py --quick 7/7

RESTRICCIONES (críticas):
- NO demoter asset_confidence (dejaría salir el 37% del histórico con 100% assets ESTIMATED)
- NO tocar delivery_quality_report.py:289 BLOCKING_GATE_NAMES (rige el ZIP, régimen de DELIVERY)
- NO implementar S2.3; NO agregar el 8º servicio; NO construir el acta_revision.md del Bot 5
- NO tocar _coherence_gate (:458), _coverage_gate (:1244), _doc_audit_consistency_gate (:1464)
- NO tocar VERSION.yaml
- NO commitear los docstrings por separado del comportamiento
- Verificar que la justificación de proposal_asset_alignment como advisory SIGUE sosteniéndose tras
  FASE-C (antes era "tautología"; si el punto 8 la disolvió, reformular y registrar)
- Pytest en lotes pequeños con salida a archivo; NUNCA tests/commercial_documents completo (~8GB)

POST-EJECUCIÓN (obligatoria):
Actualizar dependencias-fases.md, README.md, 06-checklist-implementacion.md,
09-documentacion-post-proyecto.md (B/D/E — AGENTS.md es archivo afiliado),
10-analisis-post-implementacion.md (Decisiones: piso advisory, is_ready_for_publication,
re-formulación de la justificación), evidence/FASE-D/ (incl. captura de git show --stat).
Luego: log_phase_completion.py --fase FASE-D --desc "..." --check-manual-docs  (SIN --release).
Commit ÚNICO que incluya código + AGENTS.md, referenciando FASE-D.
```
