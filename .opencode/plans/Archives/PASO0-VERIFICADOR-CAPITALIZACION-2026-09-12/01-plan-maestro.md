# 01 — Plan Maestro: PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12

> **Estado**: EN CURSO · **Creado**: 2026-09-12, **después** de `00-lecciones-capitalizadas.md` (orden del
> executor v2.23.1, y el punto de este plan: es la primera vez que el Paso 0 se ejecuta en la concepción).
> **Objetivo**: un verificador mecánico que impida publicar un plan sin capitalización efectiva del corpus.
> **Predecesor**: `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` (vivo) — este plan toma su ítem **(i)** de
> §Deuda de proceso: «Deuda que queda (pertinencia) → verificador propio
> (`validate_lesson_capitalization.py`), con su cobertura declarada. Dueño sugerido: nuevo tramo con AC».
> **Versión**: sin bump (decisión Q5, §2.4). `4.77.0` sigue reservado por el predecesor.
> **Sin push**: ningún commit de este plan se empuja.

---

## 1. Origen medido (no supuesto)

| Hecho | Medición (2026-09-12, comandos en `00-lecciones-capitalizadas.md` §1) |
|-------|------------------------------------------------------------------------|
| Cobertura actual de la regla del Paso 0 | **1** archivo `00-lecciones-capitalizadas.md` sobre **26** planes del repo = **3,8 %** (Q6) |
| Planes archivados **sin** `00-` | **25** de 25 — ninguno lo tuvo nunca; el artefacto nace con v2.22.0 (2026-09-12) |
| Archivados que caerían en un check «todos los planes» | **25** fallos permanentes = ruido que se aprende a ignorar (L-HF1) |
| Enforcement real hoy | `scripts/git_hooks/pre-commit` con **6** checks, byte a byte idéntico al instalado en `.git/hooks/` |
| `.pre-commit-config.yaml` | **13** hooks declarados, **0** enforcement (así lo declara `CONTEXT-DECISION-PRE-COMMIT-FRAMEWORK-2026-08-29`; la decisión del usuario mantiene vigente el hook custom) |
| Precedente de cableado | `validate_plan_closure.py` y `build_lesson_index.py --check`: **hook-only** (0 apariciones en `run_all_validations.py`). `validate_plan_citations.py` y `validate_opencode_refs.py`: **doble** |
| Coste de calcular el índice en memoria | **0,30 s** para 346 `.md` / 246 IDs definidos (Q8) |
| Factibilidad de los checks propuestos | Sobre el único `00-` real: **18** filas §2, **18/18** atribuciones coinciden con el índice, **0** huérfanas, **6** dueños distintos (Q7) |

## 2. Decisiones fijadas ANTES de implementar

Cada decisión tiene su AC en §6 y su evidencia en `evidence/FASE-V1/decision-verificador.md`.

### 2.1 Q1 — Alcance: **hacia delante por fecha, con Archives fuera**

Un plan está en alcance si su **nombre de directorio** lleva fecha `≥ 2026-09-12` (fecha de executor
v2.22.0, que introdujo el artefacto) **y** no vive bajo `Archives/`. Constante `CUTOFF_DATE` en el script,
sobreescribible con `--cutoff` para poder medir contra el corpus histórico sin cambiar el código.

- Sin fecha parseable en el nombre ⇒ **exento y reportado** (6 archivados son así: `ROICRII`, `DT4-RESIDUAL-FIXES`, …).
- `Archives/` ⇒ fuera: ya pasó por el check mientras estaba vivo, y un archivo congelado no se reescribe
  (misma política de `validate_plan_closure.py`).
- **Medido**: con este alcance entran **0** planes históricos y **1** plan real (este) ⇒ el gate nace sin
  deuda y sin ruido.

### 2.2 Q2 — Qué puede verificar un script sin juicio semántico: **ocho checks, todos de forma o trazabilidad**

Se descartó deliberadamente cualquier check de *calidad* del texto: sería L-HF1 al revés (un candado de
forma que pasa en verde mientras el artefacto miente). La forma del contrato está en §3.

### 2.3 Q3 — Dónde vive: **doble cableado**, hook `[7/7]` + check `[9/9]` de `--quick`

El hook es lo único que bloquea un commit; `--quick` es lo único que corre en un clon donde nadie ejecutó
`install_git_hooks.py` (el límite de R2.6 medido: una regla cuyo insumo no está en el repo es
inejecutable fuera de esta máquina). Coste asumido y medido: renumerar `[n/6]`→`[n/7]` en el hook,
`[n/8]`→`[n/9]` en el modo rápido y `[9/11]`→`[10/13]` etc. en el completo, y actualizar **3** referencias
**normativas** del executor al `[6/6]`; las referencias **históricas** (`[6/6]` bloqueó ese commit, en R2.10
y en el changelog v2.23.x) **no se reescriben**: son medición, no puntero (L-NC10 no autoriza falsificar el
registro, y `validate_plan_citations.py` documenta el mismo principio).

### 2.4 Q4 — Qué declara no poder verificar, y Q5 — cierre sin bump

El límite es la **pertinencia**: qué lección debía capitalizarse y si el efecto alegado es real. Se publica
en tres sitios (cabecera del script, línea final de su salida, §4 de cada `00-`) porque L-R.4 solo vale si
quien lee el artefacto lo ve. Cierre: subsection en `CHANGELOG.md` bajo la regla de validación-only del
executor; no se toca `VERSION.yaml` ni se renumera el release del predecesor.

## 3. Contrato del verificador (`scripts/validate_lesson_capitalization.py`)

Entrada: directorio de planes. Salida: violaciones + **población mirada** (C0). Exit code `0/1/2` como los
dos verificadores de la familia. **Sin `--fix`**: reporta, no reescribe.

El script es él mismo un lector de artefactos, así que aplica **R2.9 (NR8)** a su propia lectura. Tres
estados, claves distintas en la salida, y **ningún verde desde el tercero**:

| Estado | Cuándo | Qué imprime |
|--------|--------|-------------|
| `SIN-HALLAZGOS` | el `00-` existe, se parseó y no hay violación | `OK` + conteo de planes mirados |
| `AUSENTE` | no hay `00-`, o no hay `01-plan-maestro.md` en un plan en alcance | violación con la ruta buscada |
| `LECTOR-FALLIDO` | el archivo no se puede leer, o la tabla §2/§1 no tiene el número de columnas que la convención exige | violación con el **motivo**; **nunca** `OK` |

| # | Check | Forma mecánica (sin juicio semántico) | Estado si no se puede evaluar |
|---|-------|--------------------------------------|--------------------------------|
| C0 | Cobertura publicada | Toda corrida imprime: planes totales, en alcance, exentos por `Archives`, exentos por fecha anterior al corte, exentos **sin fecha parseable** (con sus nombres) | — |
| C1 | Presencia | `00-lecciones-capitalizadas.md` existe y se lee | `AUSENTE` / `LECTOR-FALLIDO` |
| C2 | Estructura | Encabezados `## 1.`, `## 2.`, `## 3.`, `## 4.` presentes | `SIN-HALLAZGOS`, y los checks que dependen de la sección ausente reportan `LECTOR-FALLIDO` |
| C3 | Consulta al corpus completo | ≥1 fila de §1 cuya celda **Capa** nombre una capa corpus-wide (`Índice`, `LECCIONES-INDEX`, `QMind`, `Memoria`, `Repo`) **y** cuya celda **Consulta literal** contenga un comando entre backticks | `SIN-HALLAZGOS` (violación) |
| C4 | Anti-ceremonia sobre ACs | ≥1 fila de §2 cuya celda **Qué cambia** o **Dónde se aplica** nombre un AC (`AC-F1` **o** `AC8`: las dos convenciones vivas del repo, porque un candado de forma que castiga al que escribe bien es L-B1) que **existe** en la tabla de ACs de `01-plan-maestro.md` | `LECTOR-FALLIDO` si el maestro no tiene tabla parseable (no puede dar OK) |
| C5 | Descartes | ≥3 filas de datos en §3 (umbral medido en Q7 sobre el único artefacto real: 18 filas en §2, 6 descartes, 5 dueños) | `SIN-HALLAZGOS` (violación) |
| C6 | Declaración de cobertura | §4 contiene el nombre del verificador (`validate_lesson_capitalization.py`) **y** una frase de límite (`no verific`, `no comprueba`, `no garantiza`) | `SIN-HALLAZGOS` (violación) |
| C7 | Atribución real de §2 | Para cada ID `L-*`/`DA-*`/`D-*`/`S-*` de la primera celda de §2: (a) está **definido** en el índice calculado en memoria, y (b) el **dueño** que publica el índice aparece literalmente en la celda **Definida en** | `LECTOR-FALLIDO` si el índice no puede calcularse |
| C8 | Diversidad anti-predecesor | Los dueños resueltos en C7 cubren **≥2** planes/CONTEXTs distintos | `SIN-HALLAZGOS` (violación) |

**Fuente de verdad de C7/C8**: `build_lesson_index.build()` **en memoria**, no `.opencode/lecciones_index.json`.
Motivo medido en Q8 (0,30 s) y en Q9 (el JSON es salida de otro check): un verificador no confía su
conclusión al artefacto generado que otro gate mantiene fresco, porque si ese gate no corrió el verde es
prestado.

## 4. Cobertura y límites de ESTE plan

- **Cubre**: la forma y la trazabilidad del artefacto del Paso 0 de los planes nacidos desde v2.22.0.
- **No cubre**: (1) la pertinencia semántica — qué lección debía capitalizarse y si el efecto alegado es
  real; (2) los 25 planes archivados, que no tendrán nunca `00-`; (3) que los prompts de fase copien las
  filas de §2 que les corresponden (el executor lo exige en prosa, queda sin check); (4) que un plan nuevo
  se conciba **después** de escribir el `00-` — el script no puede ver el orden, solo el estado final
  (mismo límite declarado de R2.10); (5) los planes cuyo nombre no lleve fecha.
- Cada límite se publica en la salida del script y en §4 del `00-` de cada plan.

## 5. Fases

| Fase | Qué | Sesión |
|------|-----|--------|
| FASE-V1 | Decisiones fijadas con evidencia + contrato C0–C8 + plan maestro y prompts | esta |
| FASE-V2 | `scripts/validate_lesson_capitalization.py` + `tests/test_validate_lesson_capitalization.py` + NR7 por check + cableado (hook `[7/7]`, check `[9/9]`) | esta (commit propio) |
| FASE-V3 | Cierre documental: template y executor dejan de declarar que el verificador no existe, transferencia de deuda registrada en el predecesor, CHANGELOG sin bump, write-back + índice + `git mv` en orden R2.10 | esta (commit propio) |

## 6. Criterios de aceptación

Cada AC declara **artefacto** y **clave legible** (R2.4). Ninguno se certifica ✅ sin su lectura en el artefacto.

| AC | Fase | Criterio | Artefacto y clave donde se lee |
|----|------|----------|--------------------------------|
| AC-A1 | V1 | Q1 decidida con la población medida: cuántos planes entran y cuántos quedan exentos, y por qué | `evidence/FASE-V1/decision-verificador.md` → sección `## Q1` con la tabla de exención (Archives / fecha anterior / sin fecha) |
| AC-A2 | V1 | Q2 decidida: los ocho checks están escritos con su forma mecánica y su estado de no-evaluación | `01-plan-maestro.md` §3 (tabla C0–C8, columnas «Forma mecánica» y «Estado si no se puede evaluar» sin celdas vacías) |
| AC-A3 | V1 | Q3 decidida contra el dato de enforcement real, no contra la convención declarativa | `evidence/FASE-V1/decision-verificador.md` → sección `## Q3` con el resultado de `diff .git/hooks/pre-commit scripts/git_hooks/pre-commit` y el conteo de referencias normativas vs históricas al `[6/6]` |
| AC-A4 | V1 | Q4 decidida: el límite está escrito en los tres sitios exigidos | `01-plan-maestro.md` §4 + plantilla del docstring del script (Tarea 2 de V2) + §4 de `00-lecciones-capitalizadas.md` |
| AC-A5 | V1 | Q5 decidida: el cierre no toca `VERSION.yaml` ni renumera el release del predecesor | `evidence/FASE-V1/decision-verificador.md` → sección `## Q5`; verificación en V3 con `git diff` vacío sobre `VERSION.yaml` |
| AC-B1 | V2 | El script existe, **reporta sin reescribir** y sale `0/1/2` | `python scripts/validate_lesson_capitalization.py --help` → sin `--fix`; `git diff --name-only` tras una corrida con violaciones no lista ningún `.md` |
| AC-B2 | V2 | Cada check C1–C8 tiene ≥1 test que lo nombra por su causa, y los tres estados de R2.9 tienen test propio | `tests/test_validate_lesson_capitalization.py` → nombres `test_c4_...`, `test_estado_ausente_...`, `test_lector_fallido_...` |
| AC-B3 | V2 | **NR7 por check**: con el guard de ese check desactivado en el archivo versionado, su test cae en rojo | `evidence/FASE-V2/nr7-C<n>-rojo.txt` y `-verde.txt` por cada C1…C8 (dos salidas por check) |
| AC-B4 | V2 | Cableado activo en los dos puntos: el hook bloquea un commit real y el check aparece en `--quick` | `evidence/FASE-V2/hook-bloquea.txt` (exit code ≠ 0 de `scripts/git_hooks/pre-commit` sobre un árbol con `00-` defectuoso) + salida de `run_all_validations.py --quick` con `[9/9] Lesson Capitalization` |
| AC-B5 | V2 | Ningún `[OK]` sin denominador: la salida publica la población mirada | salida del script → línea `cobertura:` con los 5 conteos de C0 |
| AC-C1 | V3 | Las declaraciones «no existe verificador» del template y del executor se actualizan; las mediciones históricas no se reescriben | `git diff` de FASE-V3 sobre `.agents/workflows/templates/lecciones-capitalizadas-template.md` y `.agents/workflows/phased_project_executor.md` |
| AC-C2 | V3 | La deuda (i) del predecesor queda cerrada **con dueño y fecha** y el plan se archiva en el orden de R2.10 | `.opencode/plans/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/06-checklist-implementacion.md` §Deuda + `git log` del `git mv` con el índice regenerado en el mismo commit |

## 7. No-regresiones aplicables

- **NR1/R2.3/R2.7**: par pre/post del conteo canónico `grep -rE "^\s*def test_" tests --include=*.py`, con
  `--ignore` del archivo de tests nuevo en la corrida `pre` (L-T4B.5) y los flaky conocidos nombrados
  (L-VUP-1: `test_function_default_flags`). La resta debe dar exactamente los tests nuevos de V2.
- **R2.8 / NR7 por AC de detección**: AC-B1…AC-B5 son de detección → todos con reversión y rojo (AC-B3).
- **R2.9 / tri-estado**: exigido **sobre el verificador mismo** (§3) y cubierto por AC-B2.
- **R2.2**: ningún archivo de este plan cita `archivo:123`; se citan símbolos (`CUTOFF_DATE`,
  `build_lesson_index.build()`, `_check_c4_ac_existente()`).
- **R2.4**: cada AC de §6 declara artefacto y clave. Un AC no legible en el artefacto se cierra ⚠️.
- **L-R.3 (cobertura medida)**: el verde del verificador se publica con su población; queda prohibido
  reportar «el check pasa» sin el denominador.
- **L-D3**: los umbrales (≥3, ≥2, ≥1) vienen de Q7 sobre el único artefacto real, no de un deseo: un
  artefacto humano correcto ya los cumple, así que cumplir no cuenta como violación.

## 8. Riesgos y mitigación

| Riesgo | Mitigación |
|--------|-----------|
| Un check nuevo bloquea commits por un motivo espurio y se aprende a usar `--no-verify` | Alcance hacia delante (0 planes históricos), tri-estado (el lector fallido no da OK pero tampoco culpa a un artefacto legible) y umbrales medidos en Q7 |
| Ceremonia: la gente escribe ACs vacíos para satisfacer C4 | C4 comprueba que el AC **existe en el maestro**, no que la frase sea larga; C7/C8 exigen dueño real y ≥2 dueños. El límite semántico queda declarado, no disfrazado |
| Doble cableado diverge (hook y `--quick` con criterios distintos) | Ambos invocan el **mismo** script con los mismos argumentos por defecto; ningún criterio vive en el shell ni en `run_all_validations.py` |
| Renumarar checks deja referencias falsas en el executor | AC-C1 obliga a separar referencias normativas (se actualizan) de mediciones históricas (se conservan), con el diff como evidencia |

## 9. Trazabilidad con el Paso 0

Las 18 filas de `00-lecciones-capitalizadas.md` §2 se aplican así: L-HF1→AC-A2/AC-B5 · L-R.3→AC-B5 ·
L-R.4→AC-A4/AC-C1 · DA-HF3→AC-A1/AC-B1 · L-D3→AC-A2 · L-B1→AC-B2 · L-VUP-5 y L-T2C.4→AC-B3 ·
L-T4B.5 y L-VUP-1→§7 · L-PF10→AC-A2/AC-B2 · L-NC10→AC-C1 · L-V.4→§8 · L-V.2→AC-A3 · L-VUP-9→AC-B4 ·
S-H17→AC-B4 · L-I1→§3.b del `00-` · L-C2→AC-A3/AC-B4.
