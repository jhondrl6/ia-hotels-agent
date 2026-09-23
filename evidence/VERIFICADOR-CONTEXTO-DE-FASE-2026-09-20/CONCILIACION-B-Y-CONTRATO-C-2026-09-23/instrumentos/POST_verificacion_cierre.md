# Verificación del cierre (POST) — 2026-09-23

Comandos, resultados y **códigos reales**. Nada de aquí fija como expectativa un conteo visto en otra
sesión: cada cifra lleva su comando y su fecha, y quien reabra el plan re-mide.

Intérprete usado en toda la sesión: `./venv/Scripts/python.exe` (Python **3.13.3**), por la misma razón
que el contrato canónico: bajo Git Bash `python` a secas resuelve al intérprete sin dependencias del
proyecto.

## El generador, y solo él, tocó el índice

| Paso | Comando | Salida | EXIT |
|---|---|---|---|
| Regenerar | `./venv/Scripts/python.exe scripts/build_lesson_index.py` | `[OK] 332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` → `-> .opencode/LECCIONES-INDEX.md` `-> .opencode/lecciones_index.json` | **0** |
| Comprobar frescura | `./venv/Scripts/python.exe scripts/build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (332 IDs)` | **0** |

Regenerado **después de la última edición de sus fuentes**, como exige el contrato (§Cierres 5) y
`[6/7]` del hook. Los dos archivos **no** se editaron a mano.

`git diff --numstat` del par: **`4 4 .opencode/LECCIONES-INDEX.md`** y **`7 5 .opencode/lecciones_index.json`**.
El cambio es **solo de conteos de referencias**, no de IDs definidos — y es la medición A6 del maestro
golpeando a esta propia sesión: al escribir sobre **L-VCF-11** y **L-VCF-12** sus referencias suben
(12→13 y 7→14, y L-VCF-12 pasa a figurar también bajo `context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22`),
y L-V2.2/L-V2.3 suben 18→21 y 32→33. **Los 332 IDs definidos no se movieron**: no se capitalizó ninguna
lección nueva aquí (las propuestas del proveedor falso siguen sin existir, y E3 las impediría).

## Validaciones documentales

| Comando | Salida | EXIT |
|---|---|---|
| `validate_lesson_capitalization.py` | `[OK] Capitalización del Paso 0: forma y trazabilidad verificadas \| NO verifica pertinencia…` — cobertura: 4 planes en alcance, 27 archivados excluidos, **6 fuentes** para este plan | **0** |
| `validate_plan_citations.py` | `[OK] Plan citations: 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos en el inventario)` | **0** |
| `validate_document_integration.py` | `RESULT: All checks passed` | **0** |
| `validate_opencode_refs.py` | `[PASS] OpenCode References: todas las referencias existen` | **0** |

Ningún validador fue relajado ni re-baselinado (`--update-baseline` **no** se corrió: es paso de
FASE-RELEASE), y ningún hallazgo conocido se convirtió en PASS.

## AC16 — el conteo de checks, como delta

| Lado | `run_all_validations.py --quick --check` | `build_lesson_index.py --check` |
|---|---|---|
| **PRE** (antes de la primera edición) | **11/11** `ALL VALIDATIONS PASSED`, `EXIT=0` | `[OK] … (332 IDs)`, `EXIT=0` |
| **POST** (última corrida) | **11/11** `ALL VALIDATIONS PASSED`, `EXIT=0` | `[OK] … (332 IDs)`, `EXIT=0` |

**Resta 0** en los dos instrumentos (quick **11**, hook **7** — esta sesión no tocó su composición), y
ninguna cuenta de test cambió: no se escribió ni un `.py`. El número **11** es el valor medido hoy con
`--quick --check`, no un pin copiado de otra sesión; su comando está en el README del plan.

## Instrumentos de B vuelven a su estado: rojo contractual conservado

- `validate_governance_numbers.py --report` (sin destino) → **`EXIT=1`**, `HALLAZGOS` con
  `assertion_id ∈ {A1,A2,A3,A4}`, **stdout JSON puro** y aviso de no-escritura por stderr.
  crudo: `../reporte_gobernanza_stdout_2026-09-23.json` y `_stderr_2026-09-23.txt`.
- `evidence/…/FASE-A/informe.json` → `sha256` **idéntico** antes y después de la corrida
  (`1111f9b2e1d32e9803c50864183a92e6ebd0cc5830e4dcc8b8b5fda8b7de1037`) y `git status --porcelain
  evidence/` **vacío**: S12 verificada **sin pisar el pasado**, que es justo lo que la guarda del README
  ya no necesita exigir.
- `decision_client.py --scan-imports` → `[SIN-HALLAZGOS]`, **0** imports, población **696/9655**, `EXIT=0`
  (crudo: `../scan_imports_2026-09-23.txt`, con `git ls-files '*.py'` = **696** en su `.meta`).
- `decision_client.py --costura` → `EXIT=0`, `files_changed_to_add_provider = 1`, y su
  `alcance_de_ac9` impreso (crudo: `../costura_remedida_2026-09-23.json`).
- `decision_client.py --provider-status` → `EXIT=1`, `NO-CONFIGURADO` (crudo:
  `../provider_status_2026-09-23.json`).
- Selección `pytest tests/quality_gates/decision_client -q -p no:cacheprovider` → **87 passed**,
  `EXIT=0` (crudo: `../pytest_seleccion_decision_client_2026-09-23.txt`). **No se corrió la suite
  completa**: los `4.393 / 4.396 passed, 4 failed` de `REMEDIACION-BLOQUE-A-2026-09-22/` son de las
  sesiones 3 y 4 del bloque A, no de esta.

## Diff final: lo excluido quedó intacto

`git status --porcelain` al cerrar esta sesión (los archivos de evidencia de esta propia sesión ya están
contados):

- **Modificados (esta sesión): 12 rutas.** Los **diez** documentos del plan propietario — `README.md`,
  `dependencias-fases.md`, `01-plan-maestro.md`, `04-contrato-ejecucion.md`,
  `05-prompt-inicio-sesion-fase-B.md`, `05-prompt-inicio-sesion-fase-C.md`,
  `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`,
  `10-analisis-post-implementacion.md`, `00-lecciones-capitalizadas.md` — más la orden
  `.opencode/context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y el par generado
  `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` (12 + 1 = 13 `M` en total contando
  la ruta ajena del punto siguiente). **No** se tocaron `05-…-fase-A.md`, `05-…-fase-D.md` ni
  `05-…-fase-RELEASE.md`.
- **Nuevos (esta sesión):** el subdirectorio `evidence/…/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/` y su
  `instrumentos/`. No reemplazó ni sobrescribió evidencia anterior: `FASE-A/`, `FASE-B/` y
  `REMEDIACION-BLOQUE-A-2026-09-22/` conservan sus rutas y sus mtimes de origen.
- **Ajeno y preservado:** `.opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21/dependencias-fases.md`
  sigue modificado con las 18 líneas de otra sesión — **sin `git checkout`, sin commitear, sin tocar**.
- **Intactos por restricción:** `AGENTS.md`, `.cursorrules`, `.agents/**`, `scripts/git_hooks/**`,
  `scripts/run_all_validations.py`, `scripts/build_lesson_index.py`, `scripts/decision_client.py`,
  `scripts/validate_governance_numbers.py`, `tests/**`, `VERSION.yaml`, `CHANGELOG.md`,
  `docs/contributing/REGISTRY.md`, y los otros tres planes de la orden (`REFACTOR-WHATSAPP`,
  `EVALUACION-JEV`, `VERIFICADOR-ESCRITURA-QMIND`) con **D/RELEASE** de este plan.

La comprobación mecánica de ese párrafo es `git status --porcelain` + `git diff --numstat` sobre las
rutas gobernadas; el `EXIT=0` de `validate_document_integration.py` y el de
`validate_opencode_refs.py` respaldan que ninguna referencia documental quedó colgando.

## Barrida FINAL (la que vale) tras la última edición

Después de esta página se escribió **otra** edición de fuentes del índice (la fila «Herencia de forma
para C» del README), así que el generador se volvió a correr y toda la barrida se repitió sobre el árbol
final. **Estos son los resultados de esa pasada**, no los de la primera de arriba; la segunda pasada del
mismo día vuelve a barrer más abajo:

| Comando | Salida | EXIT | crudo |
|---|---|---|---|
| `build_lesson_index.py` | `[OK] 332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` | **0** | `FINAL_build_lesson_index.txt` |
| `build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (332 IDs)` | **0** | `FINAL_check_indice.txt` |
| `validate_lesson_capitalization.py` | `[OK] … forma y trazabilidad verificadas` | **0** | `FINAL_lecciones.txt` |
| `validate_plan_citations.py` | `[OK] Plan citations: 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos en el inventario)` | **0** | `FINAL_citas.txt` |
| `validate_document_integration.py` | `RESULT: All checks passed` | **0** | `FINAL_doc_integration.txt` |
| `validate_opencode_refs.py` | `[PASS] … todas las referencias existen` | **0** | `FINAL_refs.txt` |
| `run_all_validations.py --quick --check` | `TOTAL: 11/11 validations passed` · `STATUS: ALL VALIDATIONS PASSED` | **0** | `FINAL_quick_check.txt` |

`git diff --numstat` del par generado al cerrar: **`4 4 .opencode/LECCIONES-INDEX.md`** /
**`7 5 .opencode/lecciones_index.json`** — idéntico a la primera pasada, porque la última edición no
añadió referencias a IDs nuevos. Los dos `--check` dan el mismo verde con la misma cifra (**332**), y el
inventario de citas no creció (**0 nuevas, 0 crecimientos**): ninguna `archivo:número` entró al plan
(R2.2).

## Barrida de la segunda pasada (la authoritative al cerrar el par)

Después de esta página volvieron a editarse fuentes del índice (`10-analisis-post-implementacion.md` y
`dependencias-fases.md`, por las dos correcciones de cifra que produjo correr las pruebas) y se escribieron
el par `conciliacion_baseline_pre.txt` / `conciliacion_baseline_post.txt` con su `baseline-pre-post.md`. El
generador se volvió a correr y la barrida completa se repitió. **Estos son los resultados del cierre:**

| Comando | Salida | EXIT | crudo |
|---|---|---|---|
| `build_lesson_index.py` | `[OK] 332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` | **0** | `SEGUNDA_build_lesson_index.txt` |
| `build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (332 IDs)` | **0** | `SEGUNDA_check_indice.txt` |
| `validate_lesson_capitalization.py` | `[OK] … forma y trazabilidad verificadas` | **0** | `SEGUNDA_lecciones.txt` |
| `validate_plan_citations.py` | `[OK] … 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos)` | **0** | `SEGUNDA_citas.txt` |
| `validate_document_integration.py` | `RESULT: All checks passed` (ocho `[PASS]`) | **0** | `SEGUNDA_doc_integration.txt` |
| `validate_opencode_refs.py` | `[PASS] … todas las referencias existen` | **0** | `SEGUNDA_refs.txt` |
| `run_all_validations.py --quick --check` | `TOTAL: 11/11 validations passed` · `STATUS: ALL VALIDATIONS PASSED` | **0** | `SEGUNDA_quick_check.txt` |
| `version_consistency_checker.py` · `sync_versions.py --check` · `validate_plan_closure.py` | `REGISTRY OK` · `All files in sync` · `ningún plan vivo declara cierre con filas pendientes` | **0 / 0 / 0** | `HOOK_1_7_*.txt`, `HOOK_2_7_*.txt`, `HOOK_5_7_*.txt` |

El `git diff --numstat` del par regenerado quedó **idéntico** a la pasada anterior (`4 4` el `.md`,
`7 5` el `.json`): las correcciones de esta segunda pasada citan IDs ya inventariados y no añaden
referencias nuevas, y el inventario de citas sigue en **0 nuevas / 0 crecimientos** (R2.2). Los IDs
definidos no se movieron: **332 → 332**.

## Barrida de la tercera pasada (la del commit)

Motivo: al revisar el árbol antes de commitear aparecieron **dos defectos propios** — filas de tabla con
continuaciones físicas (`dependencias-fases.md` y `10-analisis`, 11 líneas absorbidas) y espacio sobrante al
final de una línea, que hacían `git diff --check` devolver **`EXIT=2`** — más la deuda que la segunda pasada
no había cerrado (re-evidenciar R2.8 mutante por mutante). Reparado y re-evidenciado, el árbol se volvió a
barrer entero:

| Comando | Salida | EXIT | crudo |
|---|---|---|---|
| `build_lesson_index.py` | `[OK] 332 IDs definidos + 51 sin definición (16 análisis, 417 .md citados)` | **0** | `FINAL2_build.txt` |
| `build_lesson_index.py --check` | `[OK] Índice de lecciones fresco (332 IDs)` | **0** | `FINAL2_check_indice.txt` |
| `validate_lesson_capitalization.py` | `[OK] … forma y trazabilidad verificadas` | **0** | `FINAL2_lecciones.txt` |
| `validate_plan_citations.py` | `[OK] … 743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos)` | **0** | `FINAL2_citas.txt` |
| `validate_document_integration.py` | `RESULT: All checks passed` | **0** | `FINAL2_doc_integration.txt` |
| `validate_opencode_refs.py` | `[PASS] … todas las referencias existen` | **0** | `FINAL2_refs.txt` |
| `validate_plan_closure.py` | `[OK] ningún plan vivo declara cierre con filas pendientes` | **0** | `FINAL2_closure.txt` |
| `version_consistency_checker.py` | 4.77.3 sincronizado · `REGISTRY OK` | **0** | `FINAL2_version.txt` |
| `sync_versions.py --check` | `All files in sync` | **0** | `FINAL2_sync.txt` |
| `run_all_validations.py --quick --check` | `TOTAL: 11/11 validations passed` | **0** | `FINAL2_quick_check.txt` |
| `pytest …test_governance_numbers_mutation_por_asercion.py -v` | `7 passed` (los 6 mutantes por id + el de salidas en disco) | **0** | `MUT_governance_numbers_por_asercion.txt` |
| `pytest …test_decision_client_mutation_guards.py -v` | `13 passed` (`M_AC6_*` ×3, `M_AC7_*`, 6 guards de forma) | **0** | `MUT_decision_client_guards.txt` |
| `git diff --check` | sin salida | **0** | — |

**Un rojo propio, conservado con su causa y no borrado con la re-corrida.** Al registrar S13 escribí una
cita `test_governance_numbers_mutation_por_asercion.py:29`, y `validate_plan_citations.py` la devolvió
**`EXIT=1`**: `[FAIL] … 1 violacion(es) (inventario actual: 744 citas)` — el inventario había crecido de 743
a 744 por **una cita numérica mía**, exactamente lo que prohíbe R2.2. El crudo del rojo quedó en
`HALLAZGO_citas_R2.2_rojo_con_S13.txt`; la corrección sustituye el número por el símbolo (`EVIDENCE`,
definida junto a `SCRIPT`), y la re-corrida devuelve los **743** de antes con `0 nuevas, 0 crecimientos`.

**Consecuencia medida del arnés de mutación (S13).** Correr `test_governance_numbers_mutation_por_asercion.py`
**re-escribió 7 archivos** de `evidence/…/FASE-A/mutation/` (`verde_baseline.txt` + los 6 mutantes): sus
`mtime` se movieron y su contenido no — los 7 `git hash-object --path` casan con HEAD y
`git status --porcelain evidence/` quedó solo con el directorio nuevo. Es el mismo patrón que S12 curó en los
dos verificadores, vivo en un test que aquella cura no miró; se registró en `10-analisis` con dueño y
disparador, **sin** editarlo (el mandato de esta sesión no autoriza tocar código ni tests).

## Barrida DEFINITIVA (la del árbol que va al commit)

Después de la tercera pasada quedaba **una edición de corpus pendiente**: la enmienda al contrato que obligó
a escribir S13 (C no puede heredar el destino de escritura hardcodeado del arnés). Con esa edición entra la
**cuarta** medición de la carga de lectura — **+54.372 B (≈189.500 tokens)**, que vence a +53.337 — y el
se volvió a barrer el árbol entero. Crudos `DEF_*`:

`build_lesson_index.py` · `--check` · `validate_lesson_capitalization.py` · `validate_plan_citations.py` ·
`validate_document_integration.py` · `validate_opencode_refs.py` · `validate_plan_closure.py` ·
`version_consistency_checker.py` · `sync_versions.py --check` · `run_all_validations.py --quick --check`
→ **los diez con `EXIT=0`**; el `--quick` en **11/11**, el índice **fresco con 332 IDs** y las citas en
**743 históricas, 0 nuevas, 0 crecimientos**. `git diff --check` sin salida. El par regenerado sigue en
**`4 4` / `7 5`**.

Estas son las cifras que valen; las de `FINAL2_*` y `SEGUNDA_*` quedan como constancia de sus pasadas.

## Lo que esta verificación NO afirma
- Que FASE-C esté ejecutada: **no** se escribió `triage_lesson_relevance.py` ni sus tests.
- Que el bloque A de la orden esté cerrado **contractualmente por completo**: lo que se cerró es su
  pendiente con CONTEXTO (S11/S12, README, AC9). Su bloque **B** (proceso común, fecha de `REGISTRY.md`)
  y su bloque **C** (los otros tres planes) siguen **sin autorización y sin aplicar**.
- ~~Que no quede nada por commitear~~ — **vencido por el propio cierre de esta sesión**: el commit
  `cea8259` registró las 13 rutas del plan y la evidencia (87 archivos, +2.794/−88), con el par del índice
  en el mismo commit (R2.10) y el trabajo ajeno de JEV excluido del stage. **Lo que sigue pendiente: el
  push** — **también vencido**: `fdd397f..d576368` empujado a `origin/master` y la paridad confirmada por
  `git ls-remote` (`ahead 0` / `behind 0`), no por el título del ref.
- ~~Que los mutantes se hayan re-evidenciado **uno por uno**~~ — **cerrado en la segunda pasada**: los dos
  arneses corrieron con `-v` y cada mutante aparece por su id (`MUT_governance_numbers_por_asercion.txt`,
  7 passed; `MUT_decision_client_guards.txt`, 13 passed). Lo que sigue sin afirmarse: que esta sesión haya
  añadido mutantes, que exigirían editar código **no autorizado**.
- Que el hook se haya corrido **como gate**: lo que hay es el conteo de sus siete pasos en HEAD y en
  árbol, más sus payload en modo lectura. `pre-commit` tiene `set -e`, su `[3/7]` auto-arregla con `--fix`
  y su `[6/7]` regenera el índice; ejecutarlo escribiría en el árbol y pide archivos staged que esta
  sesión no produce.
- Que las dos cifras que esta sesión corrigió fueran las únicas malas: se corrigieron **porque se
  midieron** («cinco tests» de S12 → **6**; la atribución de S11 a un test de población → tres funciones en
  `test_decision_client_aislamiento_imports.py`). Un conteo que no se corre no se sabe si está bien.
- Un detalle del propio instrumento, por si alguien re-pisa el mismo error: una edición de esta página
  **aplicada y reportada como exitosa no estaba en disco** minutos después; la segunda pasada la re-escribió
  y verificó con `grep` sobre el archivo. La regla «acción de la sesión invalida tu propio report» aplica
  también al «se aplicó con éxito» de una herramienta.
