# 06 — Checklist de Implementación: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.
> **Regla nueva (cura de L-R.1 aplicada a este plan, 2026-09-12)**: la celda `Iteraciones` es **bloqueante del ✅**. Debe llevar la unidad medida — `ids` + `tool_use` con corte en el commit de código. Un `—` o un `⚠️ sin medir` impide cerrar la fase; el instrumento ya existe y funciona (`evidence/FASE-D/measure_iterations.py`).

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones (ids + tool_use, corte = commit) | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 0 | Precondición: FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada | 2026-09-11 | 2026-09-11 | n/a (predecesor, sin medición) | v4.76.0 publicada (en `origin/master` como `3bdc14e`; `bd2bf57` es su duplicado pre-rebase) + archivado R2.5 — puerta de P1 abierta. Tag `v4.76.0` creado y empujado a origin 2026-09-14 |
| 1 | **FASE-P1** | ✅ **Cerrada** | 2026-09-14 | 2026-09-14 | **≈30 `ids` / ≈58 `tool_use`** — auto-reporte con unidad declarada (D-V2.1: el instrumento no alcanza el transcript bajo el cliente actual); corte = commit de cierre. **Presupuesto de 30 superado**; causa y cura en L-P1.4 de `10-analisis` | Q1=sí · Q1b=escalar (sin reintento) · Q2=O1-cuarentena · Q2b=ambas capas · Q3=P3→P2 · Q4=el hotel (T3a externa, con líneas rojas) · Q5=a (par con AC-F2) · Q6=**4** estados · Q7=hereda `GATE_BLOCKING_ENABLED` · **FASE-VERIFY no activa**. Contrato: `evidence/FASE-P1/decision-enforcement.md` |
| 3a | FASE-P3-A | ⬜ Pendiente — **primera fase de ejecución** (orden DA-P1.3) | — | — | — | Detección y fidelidad: AC-F1 (dos capas, ZIP-aware) + AC-F2 (fuente del tier) + AC-F4 (`B_PLUS`) |
| 3b | FASE-P3-B | ⬜ Pendiente | — | — | — | Cableado y test: **AC-F5 disparado por Q5=a** (toca `main.py`) + barreda D-V.1 + AC-F6 versión del acta. Presupuesto **25** |
| 2 | FASE-P2 | ⬜ Pendiente — **depende ahora de P3-A y P3-B** | — | — | — | O1-cuarentena (`package()` write→publish), AC-E0…AC-E5. **Prompt creado por P1**: `05-prompt-inicio-sesion-fase-P2.md` |
| 4 | FASE-P4 | ⬜ Pendiente (opcional) | — | — | — | Corrida observación + informe. T3a asignada a **el hotel, por contacto del operador** (Q4/DA-P1.9); techo de tier con dueño declarado (AC-O0). Si al iniciar no hay dato con fuente → §Cierre válido sin P4, **sin reabrir decisión** |
| — | FASE-VERIFY | ❌ **No activa** (decidido en P1) | — | — | n/a | Criterio §4.6-2 no garantizable desde la ingeniería. AC-V1 de RELEASE ejecuta el patrón contra artefactos de fase + pares NR7 |
| 5 | FASE-RELEASE-4.77.0 | ⬜ Pendiente | — | — | — | Cierre + tag + AC-V1 + archivado R2.5 |

---

## Checklist por Fase

### Precondición — FASE-RELEASE-4.76.0 del predecesor

- [x] VERSION.yaml = 4.76.0 y `version_consistency_checker.py` pasa (hook pre-commit `3bdc14e`, 5/5 en verde)
- [x] Plan TRIBUNAL-OFFLINE-2026-09-09 archivado en `Archives/` (R2.5, 12 renombres, `--quick` 8/8 post-archivado)
- [x] Endosos D-V.1 (whitelist barreda) y D-V.3 (executor) ejecutados o explícitamente reasignados a este plan
  - D-V.3 **ejecutado**: executor v2.20.0 → v2.21.0 con R2.6 y R2.7. Ninguna de las dos tiene verificador
    mecánico todavía → esa parte queda **reasignada a P1** (ver §Deuda de proceso).
  - D-V.1 **reasignado**: la whitelist del emisor barreda es FASE-P3-B; `test_barreda_un_solo_emisor_de_la_clave`
    sigue en rojo y v4.76.0 se publicó así, con la limitación declarada.

### FASE-P1 — Decisión y contrato ✅ (cerrada 2026-09-14)

- [x] `evidence/FASE-P1/research-estado.md` con mapa confirmado símbolo-por-símbolo (R2.2) — 14 símbolos, más tres hechos nuevos que el plan no tenía (§3.1 el acta lee un tier de un `MANIFEST.json` que aún no existe; §3.2 `if reviewer_reports:` borra la sección del MD; §3.3 los dos emisores de `asset_path`)
- [x] §2.1 del plan maestro **CONFIRMADO con evidencia** en los tres eslabones (`_compute_verdict` → `_determine_evidence_tier` → banderas del bloque FASE-K); no hubo que refutar, pero sí **agravar**: propagar banderas sin AC-F2 es invisible → DA-P1.8
- [x] Q1 (¿enforcement?) = **sí**; Q1b (consecuencia aguas abajo del bloqueo) = **escalar**: ZIP suprimido + `corrective_actions` + humano decide, **sin reintento automático y sin entrega parcial**
- [x] Q2 (ordenamiento) = **O1-cuarentena** (decisión en el *publish*, no en el *write*); Q2b (AC8) = **las dos capas**, con raíz común a AC-F2 reconocida (DA-P1.5)
- [x] Q3 (secuenciación) = **P3-A → P3-B → P2 → P4**; Q4 (hotel + T3a) = **el hotel por contacto directo del operador**, jerarquía Salento Real → Don Alfonso/Luxor → Zi-One, con tres líneas rojas (el agente jamás llena el YAML; nada de datos plausibles para destrabar; consentimiento y frescura)
- [x] Q5 = **(a) propagar banderas, como par inseparable con AC-F2**; Q6 = **cuatro estados** (`OK_NO_FINDINGS`/`ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN`), no tres — el tri-estado del plan omitía el que la corrida real ya exhibe
- [x] **Q7** (nace de la verificación pedida): el tribunal **no heredaba** `GATE_BLOCKING_ENABLED` (medido) → se decide **heredarlo** + el acta declara `enforcement.suppressed_by_operator` (escape honesto, no silencioso)
- [x] `evidence/FASE-P1/decision-enforcement.md` con contrato + rationale (formato DA-P1.1…DA-P1.9), incluidas las secciones **"Consecuencia del bloqueo"** (§3) y **"Cuatro estados de revisores"** (§4) → **AC-D1 cumplido**
- [x] ACs finales con artefacto + clave (R2.4) fijados en `01-plan-maestro.md` §6: nacen **AC-E4** (knob), **AC-E5** (consecuencia) y **AC-F6** (versión del acta); ningún AC de detección/bloqueo sin su verificación NR7 escrita
- [x] Decisión de §Deuda de proceso: **9 ítems quedan como límite declarado** (R2.6/R2.7 sin verificador, baseline R2.6 fuera del repo, `validate_plan_closure.py` 1/8, `Version actual` del REGISTRY, reescrito ciego de `--fix`, regex de `version_consistency_checker.py`, L-R.1 aplicada, normalización del flaky, cola de 78 adyacentes) y **1 cerrado por decisión**: Tier A inalcanzable → Q5=a. **El "verificador de conteos declarados en §4" se RETIRA con evidencia**: el `00-` de este plan declara 19 lecciones y tiene 19 filas; la premisa no se reproduce
- [x] **Decisión FASE-VERIFY cerrada** en `dependencias-fases.md`: **NO activa**; el criterio 2 (E2E) no es garantizable desde la ingeniería; AC-V1 de RELEASE ejecuta el patrón anclado al par NR7 por fase
- [x] **Creado `05-prompt-inicio-sesion-fase-P2.md`** con O1-cuarentena, la matriz vinculante y el "no re-decidir" de Q1b/Q2/Q5/Q6/Q7
- [x] Escenario Q5=(c) / T3a: **no disparó** (Q5=a). T3a queda **asignada con disparador pre-registrado**, no "en espera": si al iniciar P4 no hay dato con fuente, se aplica §Cierre válido sin P4 sin reabrir decisión
- [x] Resolución de §3.b de `00-lecciones-capitalizadas.md`: `D-T1.1` **vigente** (AC-D1 registra la causa de no observación, no define una política nueva); `L-SR3` **capitalizado** como causa estructural de AC-F2; `DA-C3` **subsumido** por Q6 con nombre; `L-B4` **curado** con snapshot en AC-O2; cola de 78 **fuera de alcance con razón**
- [x] `06-checklist` + `dependencias-fases` actualizados con lo decidido
- [x] `10-analisis-post-implementacion.md` y `09-documentacion-post-proyecto.md` creados — **la estructura la creó la sesión de ajuste 2026-09-14** (eran deudores de la Etapa 1); P1 los rellena en su Post-Ejecución
- [x] `log_phase_completion.py --fase FASE-P1 --desc "…" --check-manual-docs` ejecutado **sin `--release`** → `(R) Fase registrada exitosamente` en `docs/contributing/REGISTRY.md`. El recordatorio de `CHANGELOG`/`GUIA_TECNICA` queda para RELEASE **por diseño de este plan**: el acumulador es `09-documentacion-post-proyecto.md` §E, que ya lista los cinco puntos que 4.77.0 debe publicar
- [x] `run_all_validations.py --quick` → **9/9 TOTAL PASS** (2026-09-14 14:00). Incluidos los dos checks que esta sesión ponía a prueba: `[8/9] Plan Citations` (**743 citas históricas, 0 nuevas, 0 crecimientos** — P1 no introdujo números de línea) y `[9/9] Lesson Capitalization` (forma y trazabilidad del `00-` verificadas; **no** verifica pertinencia, declarado por el propio check)
- [x] **Iteraciones de P1 medidas y escritas** — auto-reporte con unidad declarada (D-V2.1), celda rellenada en Estado Global; la celda ya no está en `—`
- [x] **NO modificó código de producción** — verificado con `git status`: `NINGUN .py modificado`; los 10 caminos tocados son `.opencode/plans/<PLAN>/*` (7), `evidence/FASE-P1/` (2 nuevos) y `docs/contributing/REGISTRY.md`
- [x] Commit de cierre de fase → **`fd8e4f4`** (13 archivos, +1.045/−229; hooks 7/7). La higiene que este commit exigía — regenerar `.opencode/LECCIONES-INDEX.md` y `lecciones_index.json` tras editar los `.md` del plan — viaja en el commit siguiente, que es el que estás leyendo

### FASE-P3-A — Detección y fidelidad del acta **(primera fase de ejecución — orden DA-P1.3)**

- [ ] **AC-F1 capa 1**: `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only leyendo el miembro **desde el ZIP** (`zipfile`), sin resolver un directorio fantasma; si el miembro falta → `ARTIFACT_MISSING`, si el ZIP es ilegible → `READER_FAILED` (prohibido "vacío sin error")
- [ ] **AC-F1 capa 2**: `_is_template_stub()` con criterio **estructural** (≥1 sección declarada y todas con 0 líneas de contenido real, excluyendo `---` y el boilerplate Fecha/Score/footer; ó 0 bytes) en lugar del conteo `non_empty_lines <= 3`
- [ ] **NR7 sobre AC-F1 — dos mutaciones, una por capa**: desactivar la lectura del ZIP → rojo; volver al conteo de líneas sobre el stub real → rojo. Par de salidas en `evidence/FASE-P3-A/` (AC8 ya falló por un test que "pasaba" sin ejercitar el régimen real — L-V.1)
- [ ] **AC-F2**: `evidence_tier` del acta == el del pipeline, leído de `financial_scenarios_*.json → breakdown.evidence_tier` (fuente pre-packaging), con MANIFEST solo como fallback. Precedente: `_extract_evidence_tier`
- [ ] **AC-F2 y AC-F1 se implementan como un mismo cambio de resolutor** (raíz común: un lector escrito contra un layout descomprimido). `L-SR3`: una sola fuente de verdad para el hecho "tier"
- [ ] **AC-F4**: `first_floor_rule.reason` coherente con el veredicto en `B_PLUS`
- [ ] **Iteraciones de P3-A medidas y escritas** (unidad declarada, D-V2.1) — bloquea el ✅ (L-R.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P3-B — Cableado y test **(presupuesto 25: Q5=a disparó AC-F5)**

- [ ] **AC-F5**: hoist de `ga4_available`/`gsc_available` por encima del bloque FASE-K y propagación al `HotelFinancialData` — la regla FASE-1 de `_determine_evidence_tier` queda intacta; lo que cambia es que su input deja de ser falso
- [ ] **AC-F5 · cuatro tests**: tier `A` con analítica / `B_PLUS` sin ella / **sin `NameError` en régimen `generate_proposal=False`** (ampliar `tests/quality_gates/tribunal/test_s_e2_generate_proposal_false.py`, que ya cubre el hoist S-E2) / delta NR1 con par pre/post. L-T2C.2: el `except Exception` de FASE-K enmascara el fallo y degrada el tier en silencio
- [ ] **AC-F5 · CHANGELOG**: el cambio de tier en corridas reales es comportamiento visible → se declara, no entra en silencio
- [ ] **AC-F3**: whitelist barreda test-only, **justificada** por el contrato del emisor de `asset_path` (§5.1 de `decision-enforcement.md`), no como `xfail`
- [ ] **AC-F6**: `acta_writer.py` lee la versión de `VERSION.yaml` (hoy fija `TribunalJudge v4.76.0` en el footer)
- [ ] ~~Si Q5≠(a): AC-F5 no se ejecuta~~ — **no aplica**: Q5=(a), el condicional quedó disparado
- [ ] **Iteraciones de P3-B medidas y escritas** (unidad declarada) — bloquea el ✅
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P2 — Refactor de ordenamiento: **O1-cuarentena** (Q1=sí → la fase se ejecuta; su prompt existe)

- [ ] `package()` partido en **write** (escribe `.zip.tmp`) y **publish** (rename) / **suppress** (unlink); los revisores leen el `.tmp`; la decisión gatea el rename. Single-write ZIP-only intacto, sin serialización duplicada
- [ ] **Verificación antes de tocar**: comprobar si el ZIP empaqueta el acta. Si la contuviera, el acta publicada debe ser la enriquecida, nunca la pre-veredicto (anotar el resultado aunque no exija cambio)
- [ ] **AC-E2**: CRITICAL verificado o `BLOQUEAR` de revisor → ningún `*.zip` publicado (glob sobre `deliveries/`)
- [ ] **NR7 AC-E2**: `_compute_verdict` sin el consumo de `reviewer_reports` y el test de bloqueo en rojo; el par queda en `evidence/FASE-P2/`. Un acta emitida a mano **no** certifica el AC
- [ ] **AC-E1**: `reviewer_reports` de longitud 4 cuando los 4 corrieron, poblado desde el DTO
- [ ] **AC-E0 / NR8**: **cuatro** tests nombrados por causa (`OK_NO_FINDINGS` / `ARTIFACT_MISSING` / `READER_FAILED` / `NOT_RUN`) + uno que colapsa los estados y debe romperse. Vetado el fixture que solo puede producir un estado. La sección del MD se renderiza **siempre** (se quita el `if reviewer_reports:` de `acta_writer`)
- [ ] **Un fallo de lectura no bloquea**: `ARTIFACT_MISSING`/`READER_FAILED`/`NOT_RUN` → `NOT_EVALUABLE`, jamás `BLOQUEADO` ni `DEVOLVER-CORRECCIONES`
- [ ] **AC-E5 (Q1b)**: ZIP suprimido + `corrective_actions[]` con `owner` + stdout con la ruta del acta. **Sin reintento automático y sin entrega parcial**
- [ ] **AC-E4 (Q7)**: el bloqueo respeta `GATE_BLOCKING_ENABLED` y el acta declara `enforcement.{blocking_env,enabled,suppressed_by_operator}`; test con el knob forzado a `true` para que el `false` de CI no deje AC-E2 sin cobertura
- [ ] **AC-E3**: never-block — un revisor que revienta no rompe la corrida
- [ ] NR3: una sola ruta de bloqueo — `grep` de `blocks_delivery_zip` en `main.py` = **una** llamada; el packager no importa el acta
- [ ] NR2: tribunal no reimplementa gates (grep en `tribunal/*.py`)
- [ ] Tests retro sobre `output/` vivo + corrida E2E del predecesor, con **diff estructural JSON** (L-VUP-14)
- [ ] **Baseline NR1 sin contaminar**: snapshot `pre` con `--ignore` del archivo de tests de la fase (L-T4B.5) y resta R2.7 verificada (`suma_post − suma_pre == tests_nuevos`; 0 = baseline contaminado, no se declara el criterio). Combinación exacta de archivos + flaky conocidos declarados (`test_function_default_flags`)
- [ ] **Iteraciones de P2 medidas y escritas** (unidad declarada) — bloquea el ✅ (L-R.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P4 — Corrida de observación

> **Precondición abierta o fase diferida**: si T3a no llega a cerrarse con proveedor y fuente, P4 **no queda "en espera"** — aplica §Cierre válido sin P4 de `dependencias-fases.md` (diferimiento registrado, README a 5 sesiones, RELEASE ejecuta sin ella).

- [ ] Datos operativos reales recibidos con fuente declarada (T3a)
- [ ] Techo de tier de la corrida fijado por Q5: T3b cumplido (Tier A observable) **o** corrida declarada en `B_PLUS` con el límite escrito (AC-O0)
- [ ] `--help` de `onboard` y `v4complete` verificado **antes** de redactar el brief delegado (L-VUP-9)
- [ ] `ls output/clientes/` y log de onboarding revisados antes de la corrida; si cae a defaults, la condición de equivalencia queda declarada (L-VUP-13)
- [ ] Corrida v4complete + onboarding ejecutada (delegate_task, exit 0)
- [ ] **Evidencia copiada antes de analizar** y script de comparación versionado dentro de `evidence/FASE-P4/` (L-VUP-12)
- [ ] Delta vs corrida E2E del predecesor con **diff estructural JSON** (claves numeradas), parseo probado contra el baseline antes de la corrida (L-VUP-14, R2.3)
- [ ] Informe `evidence/FASE-P4/informe-observacion.md` con los 9 puntos del plan maestro §5 (AC-O2)
- [ ] En el informe: estado real de `reviewer_reports` con los tres estados distinguibles (punto 8) y banderas de analítica efectivas (punto 9)
- [ ] Provisionalidad de `APROBADO-PARA-ENTREGA` registrada si enforcement no cerrado
- [ ] **Iteraciones de P4 medidas y escritas** — bloquea el ✅ (L-R.1)
- [ ] NO se usó como entrega a cliente

### FASE-RELEASE-4.77.0 — Cierre

- [ ] ACs certificados contra artefacto real: **FASE-VERIFY propia si P1 la activó; si no, AC-V1 dentro de RELEASE** (patrón VERIFY, con NR7 cumplido en cada AC de detección/bloqueo) — qué vía se usó queda declarado aquí, con referencia a la decisión en `dependencias-fases.md`
- [ ] VERSION.yaml → 4.77.0 + `sync_versions.py` + CHANGELOG + GUIA_TECNICA
- [ ] **Tag anotado `v4.77.0` creado al cerrar** (el predecesor cerró 4.76.0 sin tag; ese déficit quedó saneado el 2026-09-14 — no repetir la omisión) y comprobar que `v4.76.0` esté también empujado junto con master
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] **Iteraciones de RELEASE medidas y escritas** — bloquea el ✅ (L-R.1)
- [ ] `log_phase_completion.py --fase FASE-RELEASE-4.77.0 --release 4.77.0`
- [ ] Write-back QMind ejecutado **antes** de archivar: `python scripts/validate_qmind_writeback.py --upload <PLAN>` (con título nuevo si el contenido del `10-analisis` cambió — la idempotencia es por título, no por contenido)
- [ ] Plan archivado en `Archives/` (R2.5) + commit único de cierre
- [ ] **Post-archivado**: `git diff` del `validate_opencode_refs.py --fix` revisado a mano — confirmar que no reescribió comandos dentro de bloques de código ni las auto-referencias de este plan

---

## Deuda de proceso — dueño: FASE-P1 (heredada del R2.5 del predecesor, medida 2026-09-11)

Ninguno de estos es código de producción. Son gates que dan ✅ sobre lo que no miden; P1 debe
decir cuáles entran al alcance de este plan y cuáles se documentan como límite declarado.

- [ ] **R2.6 y R2.7 sin verificador mecánico**: dos reglas obligatorias del executor v2.21.0 que hoy
  solo sostienen la disciplina de quien escribe. R2.7 es la que se puede instrumentar ya (la resta
  `suma_post − suma_pre == tests_nuevos` sobre dos conteos canónicos).
  - **Límite medido de R2.6 (2026-09-11)**: su baseline (`output/FASE-D_salentoreal_post_guard/`) está
    **fuera del repo** — la regla `output/*` de `.gitignore` lo excluye y `git ls-files` devuelve 0
    archivos. En un clon limpio el `skipif` de `test_honesty_reviewer_retro_reales.py` se cumple y el
    test **no corre**: la regla es inejecutable fuera de esta máquina. P1 debe decidir si se versiona
    un fixture mínimo (con hash y procedencia), si se documenta el requisito de entorno, o si R2.6 se
    publica como límite declarado.
- [ ] **`validate_plan_closure.py` cubre 1 de 8 planes (12,5 %)**: solo lee `10-analisis` de planes
  vivos y solo dispara si el encabezado dice `COMPLETADO`. La regla L-R.3 sigue siendo letra muerta.
- [ ] **Campo `Version actual` del REGISTRY lo escribe una persona**: `log_phase_completion.py` no lo
  toca (0 hits en `scripts/*.py`), así que la cura es un writer o un verificador, no el edit manual
  que se hizo en este release (L-R.2).
- [ ] **`validate_opencode_refs.py --fix` reescribe a ciegas**: hace `text.replace` sobre todo el
  archivo y destruye comandos históricos de planes ya archivados (en el predecesor convirtió el
  `git mv` del `05-prompt` en una ruta sin sentido y devolvió `[PASS]`). Workaround usado: escribir
  la ruta como plantilla `<PLAN>`. Arreglo propuesto: no reescribir dentro de bloques de código.
- [ ] **`version_consistency_checker.py` no lee encabezados `FASE-RELEASE-x.y.z`**: su regex excluye
  `.`, así que la fase recién registrada es invisible y reporta `FASE-T4-A`. Hoy es informativo
  (el check solo exige encontrar *alguna* fase), pero el hook muestra una fase equivocada.
- [ ] **L-R.1: la columna `Iteraciones` de este checklist no obligaba a medir**. En el predecesor 8 de 9
  fases cerraron con `⚠️ sin medir (R2.1)` y aun así con ✅ de fase; el instrumento
  (`evidence/FASE-D/measure_iterations.py`) funcionó sin obstáculo alguno cuando se usó (RELEASE:
  31 ids / 43 `tool_use` con corte en `6bbdba7`). La cura exigida por la lección es una casilla
  obligatoria "Iteraciones (ids + tool_use, corte = commit de código)" por fase, de modo que un `—`
  impida cerrar el ✅. **Estado 2026-09-12: aplicada a este plan** (regla en la cabecera + casilla
  por fase). Sigue siendo deuda contra el executor: ninguna validación falla si otro plan la omite.

### Deuda añadida por el Paso 0 horizontal (2026-09-12)

- [x] **El Paso 0 seguía sin verificador mecánico** (misma familia que R2.6/R2.7 y L-R.4). El executor
  lo declaraba obligatorio desde v2.17.0 y describía la pasada por memoria del proyecto + notebook
  `iah-cli-lecciones`, pero ningún check comprueba que se hizo. La señal medida en este plan: sus
  prompts citaban **solo** al predecesor, con 24 planes más en el corpus. Cura candidata: exigir en
  el prompt de fase una sección "Consultas ejecutadas al notebook" y que `validate_plan_closure.py`
  (o un check nuevo) verifique que al menos una fuente citada **no** sea el predecesor inmediato.
  - **Estado 2026-09-12 (implementado A + C, fuera del perímetro de este plan)**: el Paso 0 ahora
    produce un artefacto — `00-lecciones-capitalizadas.md`, con template propio
    (`.agents/workflows/templates/lecciones-capitalizadas-template.md`) y gate en §2.5 del executor
    (v2.22.0) — y consulta una **capa fría generada**: `.opencode/LECCIONES-INDEX.md`
    (`scripts/build_lesson_index.py`; su `--check` es el guard `[6/6]` del hook versionado en
    `scripts/git_hooks/pre-commit` — activo en la máquina tras `install_git_hooks.py`; el conteo
    vigente de IDs vive en el encabezado del propio índice, no aquí). Medido al generarlo: las
    lecciones más citadas del corpus (`L-SR3`, `L-SR5`) estaban definidas **solo**
    en un `CONTEXT-*.md` y ningún análisis — el índice las
    recuperó; sin esa capa, el Paso 0 seguiría ciego a lo más usado.
  - **Cerrada 2026-09-12 por `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`** (FASE-V2, commit
    `e02a688`): existe `scripts/validate_lesson_capitalization.py`, cableado como `[7/7]` del hook
    versionado y `[9/9]` de `run_all_validations.py --quick`, con ocho checks de forma y trazabilidad
    (C0 publica la población mirada), tres estados conforme a R2.9 y sin auto-fix. Cobertura medida el
    día del cierre: **1** plan en alcance sobre **27** directorios (25 archivados excluidos por regla),
    y `--cutoff 2026-09-11` lo arrojó sobre el `00-` de este plan con **una sola** violación — su §4
    declarando que el verificador no existía, que es justo lo que el check C6 caza. **Lo que sigue sin
    verificarse, declarado por el propio script**: la pertinencia. FASE-P1 de este plan ya no es dueña
    de este ítem; conserva §3.b y la cola de adyacentes que mide Q7.
  - **Deuda que queda (pertinencia)**: ningún check verifica que las filas del §2 sean lecciones
    reales aplicadas y no ceremonial, ni que una consulta haya mirado más allá del predecesor.
    Requiere lectura semántica → verificador propio (`validate_lesson_capitalization.py`), con su
    cobertura declarada. **Dueño sugerido**: nuevo tramo con AC, no FASE-P1 (que ya va justa).
  - **El plan ya tiene `00-lecciones-capitalizadas.md`** (instanciado el 2026-09-12, a posteriori:
    el plan se concibió un día antes de la regla). Contiene las 8 consultas del Paso 0 con su
    comando literal, 19 lecciones con dueño y efecto, 5 descartes y 4 hallazgos sin efecto
    aplicado. Lo que queda para FASE-P1 es resolver **§3.b** (`D-T1.1`, `L-SR3`, `DA-C3`, `L-B4`
    y la cola de adyacentes que mide Q7) y actualizar §2 al cierre de cada fase con lo que pasó.
- [ ] **El verificador de R2.7 debe normalizar el fallo orden-dependiente**: `test_function_default_flags`
  cambia entre órdenes de recolección (lección L-VUP-1, y hoy registrado en AGENTS.md como uno de los
  2 fallos ajenos al plan). Un verificador que compare sumas crudas va a inventar causas para un delta
  que es ruido de recolección. Requisito: el par pre/post se mide con la **combinación exacta de
  archivos** declarada, y los flaky conocidos se listan explícitamente en la evidencia.
- [ ] **Tier A inalcanzable en `v4complete` (defecto de producto, no de pruebas)**: `HotelFinancialData`
  del bloque FASE-K fija `ga4_enabled=False, gsc_enabled=False` mientras `ga4_client.is_available()`
  se calcula después en el mismo modo, así que `_determine_evidence_tier` no puede devolver `A` y
  `_compute_verdict` no puede emitir `APROBADO-PARA-ENTREGA`. Dueño: **Q5 de FASE-P1** (decidir si P3
  lo arregla con AC-F5, si P4 se corre en `B_PLUS` con límite declarado, o si se difiere a un plan de
  analítica). No se arregla en silencio: el hoist toca `main.py` y cambia el tier de corridas reales.

---

## Cierre del plan

- [ ] Todas las fases ✅ — P4 admitida como **diferida** solo con la decisión registrada según §Cierre válido sin P4 (`dependencias-fases.md`); "en espera" no cierra
- [ ] ACs finales certificados (vía FASE-VERIFY o AC-V1 en RELEASE, según la decisión de P1)
- [ ] NR1–NR8 sin violaciones (NR7 con el par de salidas verde/rojo en evidencia; NR8 con los tres tests por estado)
- [ ] Todas las fases cerradas con sus iteraciones medidas (ninguna celda en `—`)
- [ ] `10-analisis-post-implementacion.md` completo (lecciones, decisiones, métricas) con la tabla "Lecciones capitalizadas de planes anteriores" incluyendo el Paso 0 horizontal
- [ ] Write-back QMind ejecutado antes del archivado (`validate_qmind_writeback.py --upload <PLAN>`)
- [ ] Plan archivado (R2.5)
- [ ] v4.77.0 publicada
