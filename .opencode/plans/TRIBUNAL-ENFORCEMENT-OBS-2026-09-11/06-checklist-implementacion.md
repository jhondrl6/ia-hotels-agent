# 06 — Checklist de Implementación: TRIBUNAL-ENFORCEMENT-OBS-2026-09-11

> **Regla**: Una fase se marca ✅ solo cuando TODOS sus criterios de completitud pasan.
> **Fuente de estado**: este archivo + `dependencias-fases.md`.
> **Regla nueva (cura de L-R.1 aplicada a este plan, 2026-09-12)**: la celda `Iteraciones` es **bloqueante del ✅**. Debe llevar la unidad medida — `ids` + `tool_use` con corte en el commit de código. Un `—` o un `⚠️ sin medir` impide cerrar la fase; el instrumento ya existe y funciona (`evidence/FASE-D/measure_iterations.py`).

## Estado Global

| # | Fase | Estado | Fecha inicio | Fecha cierre | Iteraciones (ids + tool_use, corte = commit) | Notas |
|---|------|--------|-------------|-------------|-------------|-------|
| 0 | Precondición: FASE-RELEASE-4.76.0 (predecesor) | ✅ Completada | 2026-09-11 | 2026-09-11 | n/a (predecesor, sin medición) | v4.76.0 publicada (en `origin/master` como `3bdc14e`; `bd2bf57` es su duplicado pre-rebase) + archivado R2.5 — puerta de P1 abierta. Tag `v4.76.0` creado y empujado a origin 2026-09-14 |
| 1 | FASE-P1 | ⬜ Pendiente | — | — | — | Decisión Q1–Q6 + contrato (consecuencia del bloqueo + tri-estado) + ACs finales + cierre FASE-VERIFY + prompt P2 si Q1=sí |
| 2 | FASE-P2 | ⬜ Pendiente | — | — | — | Refactor de ordenamiento (solo si Q1=sí; opción O1/O2/O3). Prompt se crea en P1 |
| 3a | FASE-P3-A | ⬜ Pendiente | — | — | — | Detección y fidelidad: AC8 + tier acta + AC-F4 (`B_PLUS`) |
| 3b | FASE-P3-B | ⬜ Pendiente | — | — | — | Cableado y test: barreda D-V.1 + versión acta + AC-F5 solo si Q5=a |
| 4 | FASE-P4 | ⬜ Pendiente | — | — | — | Corrida observación + informe (T3a datos + T3b analítica; techo de tier según Q5) — **opcional**: véase cierre válido sin P4 en `dependencias-fases.md` |
| — | FASE-VERIFY | ⬜ Condicionada | — | — | — | Solo si los 3 criterios §4.6 se cumplen al cerrar P1; si no, la sustituye AC-V1 de RELEASE |
| 5 | FASE-RELEASE-4.77.0 | ⬜ Pendiente | — | — | — | Cierre + tag + archivado R2.5 |

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

### FASE-P1 — Decisión y contrato

- [ ] `evidence/FASE-P1/research-estado.md` con mapa confirmado símbolo-por-símbolo (R2.2)
- [ ] §2.1 del plan maestro **confirmado o refutado con evidencia** (cadena `_compute_verdict` → `_determine_evidence_tier` → banderas del bloque FASE-K); si se refuta, corregir §2.1 y §9 en el mismo commit
- [ ] Q1 (¿enforcement?), Q1b (consecuencia aguas abajo del bloqueo) decididas con el usuario
- [ ] Q2 (opción O1/O2/O3) y Q2b (remediación AC8) decididas — o O4 documentado
- [ ] Q3 (secuenciación) y Q4 (hotel + datos **T3a**) decididas
- [ ] Q5 (Tier A inalcanzable: propagar banderas / correr en `B_PLUS` / diferer P4) y Q6 (esquema de tri-estado) decididas
- [ ] `evidence/FASE-P1/decision-enforcement.md` con contrato + rationale (formato DA-*), incluidas las secciones **"Consecuencia del bloqueo"** y **"Tri-estado de revisores"** (AC-D1)
- [ ] ACs finales con artefacto + clave (R2.4) fijados en `01-plan-maestro.md` §6, y ningún AC de detección/bloqueo sin su verificación NR7 escrita
- [ ] Decisión de §Deuda de proceso: qué ítems entran al alcance de este plan y cuáles quedan como límite declarado
- [ ] **Decisión FASE-VERIFY cerrada** en `dependencias-fases.md` (§4.6: los 3 criterios sobre las fases que resulten de Q1/Q4/Q5; si no activa, AC-V1 queda como sustituto declarado)
- [ ] Si Q1=sí: **creado `05-prompt-inicio-sesion-fase-P2.md`** con la opción elegida (el diferimiento del prompt está declarado en `dependencias-fases.md` §Estado de la Etapa 1; P1 lo levanta)
- [ ] Si Q5=(c) **o T3a no se cierra por Q4**: P4 diferida con la mecánica de §Cierre válido sin P4 (`dependencias-fases.md`) — README a 5 sesiones, decisión registrada, nada en espera
- [ ] `06-checklist` + `dependencias-fases` actualizados con lo decidido
- [x] `10-analisis-post-implementacion.md` y `09-documentacion-post-proyecto.md` creados — **la estructura la creó la sesión de ajuste 2026-09-14** (eran deudores de la Etapa 1); P1 los rellena en su Post-Ejecución
- [ ] `log_phase_completion.py --fase FASE-P1` ejecutado (SIN `--release`)
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] **Iteraciones de P1 medidas y escritas** (`ids` + `tool_use`, corte = commit) — bloquea el ✅ (L-R.1)
- [ ] NO modificó código de producción
- [ ] Commit de cierre de fase

### FASE-P2 — Refactor de ordenamiento (solo si Q1=sí)

- [ ] Opción elegida implementada (O1/O2/O3) manteniendo never-block
- [ ] Camino de bloqueo ejercitado: recomendación BLOQUEAR de revisor → ZIP no emitido (AC-E2)
- [ ] **NR7**: AC-E2 cerrado con mutation check — `_compute_verdict` sin el consumo de `reviewer_reports` y el test en rojo; el par de salidas queda en `evidence/FASE-P2/`
- [ ] `acta_revision.json` → `reviewer_reports` no vacío con los 4 revisores (AC-E1)
- [ ] **NR8**: tres tests nombrados por causa (sin hallazgos / artefacto ausente / lector fallido) y el Juez actuando distinto en cada uno (AC-E0)
- [ ] Consecuencia del bloqueo implementada según el contrato (sección "Consecuencia del bloqueo" de AC-D1) — no solo el veredicto
- [ ] Never-block: fallo de un revisor no rompe la corrida (AC-E3)
- [ ] NR3: una sola ruta de bloqueo (grep en `main.py`)
- [ ] NR2: tribunal no reimplementa gates (grep en `tribunal/*.py`)
- [ ] Tests retro sobre `output/` vivo + corrida E2E del predecesor
- [ ] **Baseline NR1 sin contaminar**: snapshot `pre` con `--ignore` del archivo de tests de la fase (L-T4B.5) y resta R2.7 verificada (`suma_post − suma_pre == tests_nuevos`; 0 = baseline contaminado, no se declara el criterio)
- [ ] **Iteraciones de P2 medidas y escritas** — bloquea el ✅ (L-R.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P3-A — Detección y fidelidad del acta

- [ ] AC8: `EMPTY_DELIVERY_TEMPLATE` dispara en régimen ZIP-only real (AC-F1, sonda re-ejecutable)
- [ ] **NR7 sobre AC-F1**: fix desactivado → el test contra el layout ZIP-only se pone rojo (evidencia con el par de salidas)
- [ ] `evidence_tier` del acta == MANIFEST en corrida real (AC-F2)
- [ ] `first_floor_rule.reason` coherente con el veredicto en `B_PLUS` (AC-F4)
- [ ] **Iteraciones de P3-A medidas y escritas** — bloquea el ✅ (L-R.1)
- [ ] `run_all_validations.py --quick` TOTAL PASS

### FASE-P3-B — Cableado y test

- [ ] Whitelist barreda test-only (AC-F3, D-V.1)
- [ ] `acta_writer.py` lee versión de `VERSION.yaml`
- [ ] Si Q5=(a): banderas de analítica propagadas al `HotelFinancialData` del bloque FASE-K, con hoist verificado y test propio del tier con y sin analítica (AC-F5; advertencia L-T2C.2 sobre `except` anchos en `main.py`)
- [ ] Si Q5≠(a): AC-F5 **no** se ejecuta — queda registrado en esta sección con la decisión de Q5 como causa (no se borra la línea: es el rastro del condicional)
- [ ] **Iteraciones de P3-B medidas y escritas** — bloquea el ✅ (L-R.1)
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
