# 00-parte — SELLOS-ESTADO-2026-10-01 (plan EVALUACION-JEV-TYPESAFE-2026-09-21)

**Fecha de la tanda:** 2026-10-01 (los sellos se rotulan con la fecha de la tanda; la ejecución y todas
las mediciones de este parte se hicieron el **2026-10-02**, y cada cifra lleva abajo su fecha de medición).

**HEAD inicial:** `21b552f`. Paridad con `origin/master` medida tras `git fetch origin --quiet`:
`git rev-list --left-right --count origin/master...HEAD` = **0 0**. Árbol inicial limpio:
`git status --porcelain` = **0 líneas**.

**Frescura PRE de los derivados (antes de cualquier escritura):**
- `build_phase_briefing.py --check --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` → **exit 0** (5 packs OK)
- `build_lesson_index.py --check` → **exit 0**, `Índice de lecciones fresco (340 IDs)`

**Qué es esta tanda:** mantenimiento documental post-cierre. La frase original se conserva; el sello se
añade a continuación, con el formato `⟦Sello 2026-10-01 — …⟧`. No es fase de ningún plan.

---

## 1. Tabla ancla → archivo → estado

| # | Ancla (texto literal buscado) | Archivo | Estado |
|---|---|---|---|
| 2a | `los instrumentos que los producirán. Todos siguen sin implementar.` | `README.md` (línea 12) | **aplicado** |
| 2b | `\| Fase propia \| Trabajo \| Entrada \| Estado al ajustar \|` | `01-plan-maestro.md` (sello como párrafo tras la última fila `FASE-RELEASE … PENDIENTE`) | **aplicado** |
| 2c | `\| \`scripts/decision_client.py\` \| B externa crea;` | `09-documentacion-post-proyecto.md` (celda «Resultado real» de esa fila) | **aplicado** |
| 2d | `\| FASE-B \| BLOQUEADA POR DEPENDENCIA \| Sin ejecución \|` | `10-analisis-post-implementacion.md` (celda de estado) | **aplicado** |
| 4-espejo | línea final de §Sello 2026-09-30 («con esta medición como insumo.») | `10-analisis-post-implementacion.md` | **aplicado** — espejo de una línea de la deuda nueva **S37**, apuntando a `dependencias-fases.md` del hermano como fuente única (el `dependencias-fases.md` de este plan está protegido y no se tocó) |

Desacuerdos en el plan JEV: **ninguno**. Las cuatro anclas aparecieron tal como las describe el mandato,
ninguna estaba sellada ya con `Sello 2026-10-01`, y el disco no contradice lo que los sellos afirman
(comprobaciones en §3).

**Recuento medido sobre el commit** (`git grep -o 'Sello 2026-10-01' HEAD -- .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21 | wc -l`)
= **4 sellos**, uno por ancla, y **1 espejo** (`Espejo 2026-10-01`, §1 fila 4-espejo). Este plan no aporta
prosa a los packs: los cinco que se regeneraron son del hermano.

---

## 2. Huellas sha256 PRE / POST

Comando: `sha256sum <ruta>` sobre el árbol de trabajo.

| Archivo (plan JEV) | PRE | POST |
|---|---|---|
| `README.md` | `58af3ea242bfb51449df00db800ea83f129770f6dce9d79e047f69171a45a811` | `2fcb9bac59f39c944015f786060bdd399ae28c574d50288bd0a54818ff5dcb90` |
| `01-plan-maestro.md` | `e56201afc72f7b6f73c3ea76dab4997aae208e676b3b9d4bc117f0474b9cb563` | `e74c71882b312513d3de890c1156a68198ad55cd02dd62246078a10f49507556` |
| `09-documentacion-post-proyecto.md` | `226fcb3b87b2b9e45fc3bdcb6bb337a1f6ffbec98a9d916d56b834063d679a85` | `7b9b84cf9245e8d4e46a5592edc12525180bd1dbfcc237bef6a1c4daa92b5d2f` |
| `10-analisis-post-implementacion.md` | `f668bdd774bfd6d7457fa88b4dc2954a070d8a0aba96faef286571872594657b` | `951059a5d1f5592f7e21140da2c919812741d9fd8dff070e1891c042c481d479` |

Los otros cinco ficheros de la tanda (plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20: `README.md`,
`06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`, `10-analisis-post-implementacion.md`,
`dependencias-fases.md`), con sus huellas PRE/POST y su numstat, están en §5 y §6 del parte hermano
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SELLOS-ESTADO-2026-10-01/00-parte.md` — completan los 9 de la
tanda; la fuente de esas cinco mediciones es ese archivo, no este.

**Expediente protegido (debe quedar idéntico):**
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/mutation/verde_baseline.txt`
- PRE = POST = `e29a5574d151505f5e999f747f41942463b717cae2972eb9cc7aec688f104c8e` → **idéntico** (no se tocó).

## 3. Numstat por fichero

`git diff --numstat` contra `21b552f` (medido 2026-10-02, antes del commit de esta tanda):

| Archivo | + | - |
|---|---|---|
| `README.md` | 1 | 1 |
| `01-plan-maestro.md` | 9 | 0 |
| `09-documentacion-post-proyecto.md` | 1 | 1 |
| `10-analisis-post-implementacion.md` | 6 | 1 |

## 4. Comprobaciones contra disco que sostienen los sellos

- `ls -l scripts/evaluate_jev_pilot.py scripts/decision_client.py scripts/triage_lesson_relevance.py` →
  10.880 / 69.503 / 42.378 bytes, los tres presentes.
- `evaluate_jev_pilot.py` — modos: `run` y `decide` se niegan por diseño (`_refuse(...)`, líneas 240-243 del
  script); `check` sin `--out` no escribe (única escritura bajo `if args.out`).
- **Ejecución de re-medida, read-only:** `./venv/Scripts/python.exe scripts/evaluate_jev_pilot.py check
  --muestra evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/muestra.json --etiquetas
  evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/etiquetas.json` → `check_status: OK`, **5 guards** en verde
  (`schema`, `content_sha`, `split_disjoint`, `labels_not_in_payload`, `unreviewed_not_frozen`),
  `muestra_status: BORRADOR`, `counts: total 4 (dev 2 / eval 2 / excluidos 1)`. **EXIT=0** y
  `git status --porcelain` siguió en **0 líneas** (no escribió).
- Autoría de `scripts/decision_client.py`: `git log --diff-filter=A -- scripts/decision_client.py` →
  **`647f436`** (2026-09-22, «cierra FASE-B» del hermano VERIFICADOR-CONTEXTO-DE-FASE). El sello 2c afirma
  que «este plan no lo tocó» y esa creación es del hermano.
- README propio: `## Pendientes priorizados (orden de ejecución)` existe (línea 46); **P1** publica muestra
  BORRADOR / 4 pares / etiquetas `sin_revisar` / umbrales nulos; **P3** publica el bloqueo por revisión
  humana, gap de contrato y mandato. El sello 2d cita P3 y el sello 2b cita la sección.
- Archivado: `git merge-base --is-ancestor 84282c1 HEAD` → **sí** (el `git mv` del 2026-09-27 está en la
  historia de HEAD), como afirma el sello 2b.

## 5. Lo que NO se re-midió en esta tanda (declarado)

- **`pytest` no se ejecutó** — prohibido por el mandato de la tanda. Las dos frases «en verde» de los sellos
  2a y 2b (`pytest tests/quality_gates/jev_pilot -q`) viajan como las registran ya `README.md` (AC10) y
  `09-documentacion-post-proyecto.md` (`test_jev_pilot_offline.py` 7/7), no como medición de esta sesión. El
  sello 2a publica el comando, que es lo que permite re-medirlo.
- Selección de tests del hermano `tests/quality_gates/decision_client/`: verificada **su existencia en
  disco**, no su corrida.

## 6. Paso 5 — derivados y checks (los cuatro, con su salida)

Los derivados que esta tanda mueve son del plan hermano (los 5 packs de `build_phase_briefing.py` y el par del
índice); el JEV no tiene pack propio. Crudo completo en §7 del parte hermano
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SELLOS-ESTADO-2026-10-01/00-parte.md`. Aquí viajan los cuatro
resultados, que son el gate de la tanda:

1. `build_phase_briefing.py --plan .opencode/plans/Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` → **EXIT=0**,
   `[denominador] 5 packs · COMPLETO 5 · SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0 · fuentes 37 · secciones
   pedidas 23, resueltas 23, declaradas no resueltas 0`.
2. `build_lesson_index.py` → **EXIT=0**, `[OK] 340 IDs definidos + 54 sin definición (16 análisis, 422 .md
   citados)`. El par **no cambió de bytes** (no aparece en `git status --porcelain`).
3. `build_phase_briefing.py --check --plan VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` → **EXIT=0**, cinco líneas
   `[OK] … 4 fuentes frescas y proyeccion del workflow conforme (procedencia distinta, no vence)` (RELEASE: 10 fuentes).
4. `build_lesson_index.py --check` → **EXIT=0**, `[OK] Índice de lecciones fresco (340 IDs)` /
   `[fechas] nombre=329 commit=11 sin_fuente=0`.
5. `python scripts/run_all_validations.py --quick` → **TOTAL: 13/13 validations passed**, `STATUS: ALL
   VALIDATIONS PASSED`, `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`, **EXIT=0**
   (medido 2026-10-02 11:43, intérprete `python` = Python 3.13.3, el mismo que resuelve el hook).

## 7. Prohibiciones cumplidas

Sin `pytest`, sin `--no-verify`, sin push, sin APIs, sin tocar baselines. No se escribió en `evidence/` fuera
de este subdirectorio, ni en `dependencias-fases.md` de este plan (protegido), ni en `.agents/**`, `scripts/**`,
`tests/**`, `tmp_test/**`, `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, `CHANGELOG.md`, `REGISTRY.md`.

