# Conciliación 2026-09-23 — par pre/post del conteo (AC5/AC16) y lo que sí se movió

Plan: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` · Cierre de la conciliación de FASE-B con la remediación
del bloque A y de la preparación contractual de FASE-C.

**Qué es esta página.** El contrato (§«Cierres incrementales obligatorios», ítem 1) pide que todo cierre
de fase publique el par `*_baseline_pre.txt` / `*_baseline_post.txt` **y** un `baseline-pre-post.md` con
la **resta** comprobada. La corrida de esta sesión había publicado la resta dentro de
`instrumentos/POST_verificacion_cierre.md` sin el par nombrado; esta página lo subsana. Crudos:
`conciliacion_baseline_pre.txt` · `conciliacion_baseline_post.txt`.

**Qué no es.** No es una fase de implementación: no escribe código ni tests, y por eso su delta esperado
en los conteos de checks es 0. FASE-D añade aquí su propio par de carga de lectura (AC20) con signo
distinto de cero; esta sesión **sí** mueve carga de lectura, y se publica restada abajo.

## Instrumento (comandos idénticos en los dos lados)

```bash
# PRE = revision fdd397f;  POST = arbol de trabajo. Mismo grep, distinta corriente.
git show HEAD:scripts/run_all_validations.py | grep -cE '^\s*print\(f?"\[[0-9]+/11\]'   # quick
grep -cE '^\s*print\(f?"\[[0-9]+/11\]' scripts/run_all_validations.py
git show HEAD:scripts/run_all_validations.py | grep -cE '^\s*print\(f?"\[[0-9]+/15\]'   # solo-completo
git show HEAD:scripts/git_hooks/pre-commit | grep -cE '^#   \[[0-9]+/[0-9]+\]'          # hook
grep -rE '^\s*def test_' tests --include=*.py | wc -l                                    # canonico (arbol)
git grep -hE '^\s*def test_' HEAD -- tests | wc -l                                       # canonico (PRE)
git ls-files '*.py' | wc -l                                                             # poblacion AC6
git grep -cE '^\s*(import|from)\s+(typesafe|jev|httpx2)' -- '*.py' | wc -l               # AC6 imports
python -c "import json;print(json.load(open('.opencode/lecciones_index.json',encoding='utf-8'))['cobertura']['ids_con_definicion'])"
stat -c "%s %n" .agents/workflows/phased_project_executor.md \
  .agents/workflows/templates/lecciones-capitalizadas-template.md                        # AC17
# carga de lectura: bytes de blob por archivo (git ls-tree -l para PRE; disco menos CR para POST)
git rev-parse HEAD:scripts/git_hooks/pre-commit; git hash-object --path=... ...          # identidad de scripts
```

## La resta, por unidad

| Unidad | PRE (HEAD `fdd397f`) | POST (árbol) | Resta | Esperado | Estado |
|---|---|---|---|---|---|
| Checks del `--quick` (`[N/11]` impresas) | 11 | 11 | **0** | 0 (AC16) | ✅ |
| Etiquetas del modo completo (`[N/15]`) | 4 | 4 | **0** | 0 (AC16) | ✅ |
| Pasos del hook versionado | 7 | 7 | **0** | 0 (AC16) | ✅ |
| Composición del `--quick` | 11/11 verde | 11/11 verde | 0 | verde sin tocar composición | ✅ |
| Funciones de test canónicas (método grep, árbol) | 4.424 | 4.424 | **0** | 0 (esta sesión no escribe `tests/`) | ✅ |
| Funciones rastreadas por `git grep` (mismo grep, HEAD vs árbol) | 4.424 | 4.424 | **0** | ídem | ✅ |
| Selección `decision_client` (casos) | 87 | **87 passed, EXIT=0** | 0 | corrido en esta sesión | ✅ |
| Selección `governance_numbers` (funciones / casos) | 35 / 40 | **35 / 40 passed, EXIT=0** | 0 | corrido en esta sesión | ✅ |
| Regresiones de S12 (funciones en su archivo) | 6 | **6 passed, EXIT=0** | 0 | ídem | ✅ |
| Población AC6 rastreada por git (`.py`) | 696 | 696 | **0** | 0 (no se conmuta `.py`) | ✅ |
| Imports del SDK/adapter fuera de la puerta | 0 | 0 | **0** | 0 | ✅ |
| IDs definidos del índice (criterio del generador) | 332 | 332 | **0** | 0: la sesión no define IDs nuevos | ✅ |
| Referencias del índice a IDs citados | — | `.md` 4/4 · `.json` 7/5 | líneas, no IDs | regenerado **solo** por su writer | ✅ |
| Bytes de los dos documentos de gobierno (AC17) | 98.694 / 6.123 | 98.694 / 6.123 | **0 / 0** | 0 (`.agents/` intocado) | ✅ |
| `git status --porcelain .agents/` | — | **vacío** | 0 | ✅ |
| Hash de objeto de los cuatro scripts gobernados | b6d0ffa7e4a5 · 75e0f5eae93a · b844914eee89 · 23ee23ca17ea | **idéntico** | 0 | esta sesión no los escribe | ✅ |
| `git diff` de esos cuatro scripts | — | **vacío** | 0 | ídem | ✅ |
| sha256 de `evidence/…/FASE-A/informe.json` (S12) | `1111f9b2e1d32e98…de1037` | **idéntico** tras `--report` sin destino | 0 | el default ya no escribe | ✅ |
| **Carga de lectura de los 16 documentos gobernados** | 703.627 B (≈175.907 tok) | **757.999 B (≈189.500 tok)** | **+54.372 B (+13.593 tok)** | **distinto de 0: la sesión edita documentos** | ⚠️ declarado |

AC16 pide resta 0 en los conteos de checks (11, 4, 7) y está. **De las 19 unidades restadas, 17 dan 0**; las
dos que no lo son son las líneas del índice regenerado (que no suman IDs) y la carga de lectura, y ninguna
de las dos se maquilla: pretender «delta 0» en los bytes de los planes que esta sesión reescribió sería
falsificar la métrica que sí cambió (L-D3). Desglose por archivo, de
mayor a menor: `05-prompt-inicio-sesion-fase-C.md` +11.620 · `01-plan-maestro.md` +7.277 ·
`ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` +6.742 · `dependencias-fases.md` +6.167 ·
`10-analisis-post-implementacion.md` +5.473 · `04-contrato-ejecucion.md` +3.550 ·
`06-checklist-implementacion.md` +3.446 · `README.md` +2.940 · `09-documentacion-post-proyecto.md` +2.726 ·
`00-lecciones-capitalizadas.md` +1.734 · `05-prompt-inicio-sesion-fase-B.md` +1.566 · el par del índice +96.
Los tres prompts de fase que esta sesión **no** tocó (`A`, `D`, `RELEASE`) aportan **+0**, y la suma de las
13 partidas cierra exactamente en **+53.337**.

**Esta fila se midió cuatro veces y las tres primeras quedaron vencidas por su propia página** (familia A6):
+50.709, +52.160 y +53.337. Cada lectura fue correcta al tomarse y dejó de serlo por ediciones posteriores
de la misma sesión — las correcciones de cifra de S11/S12, el registro de **S13** y la enmienda del contrato
que esa deuda obligó a escribir. La que vale es **+54.372 B (≈189.500 tokens)**, medida tras la **última**
edición de fuentes del índice y con el par regenerado despues. Se conserva la constancia porque el fenómeno es el
hallazgo: cuatro corridas de un mismo instrumento, tres cifras refutadas por quien las escribió.

## Dos correcciones de instrumento que produce esta página

1. **`git show HEAD:<f> | sha256sum` contra `sha256sum <f>` no casa en este repo y no prueba nada.**
   El blob de `run_all_validations.py` tiene **36.499 bytes y 0 CR**; el archivo en disco **37.412 y 913
   CR**, porque `core.autocrlf=input` normaliza al commitear. Ese par de sha256 desiguales es un artefacto
   de EOL: aplicado sin más, denuncia como «tocaron el script de validaciones» un script intacto. El
   instrumento que decide es el **hash de objeto con el filtro limpio aplicado**
   (`git rev-parse HEAD:<f>` vs `git hash-object --path=<f> <f>`) y `git diff`, y ambos casan para los
   cuatro scripts gobernados. Mismo criterio validado en tres rutas intactas antes de usarlo para la
   carga de lectura (blob == disco − CR, exacto).
2. **El número de IDs del índice se toma del generador, no de un conteo propio.** Un
   `grep -cE '^\| `' sobre `LECCIONES-INDEX.md` da **387** y **no** es «IDs definidos»: cuenta otras filas
   de tabla. La cifra canónica es `cobertura.ids_con_definicion` del JSON, que vale **332** en HEAD y **332**
   en el árbol (familia L-R.3: un conteo con criterio ajeno al emisor informa otra cosa).

## Los siete pasos del hook, medidos por payload y no solo por etiqueta

El conteo `7` es una etiqueta impresa en el hook. Esta sesión además **ejecutó los payload en modo
lectura**, porque tres de los siete no los invoca ninguno de los 11 checks del `--quick` y por tanto un
11/11 verde no los cubre (esa cobertura se midió leyendo a qué script despacha cada check de
`run_all_validations.py`, no se supuso): el quick sí despacha `sync_versions.py` (`[3/11]`,
línea 199), `validate_opencode_refs.py` (`[8/11]`, 552), `validate_plan_citations.py` (`[9/11]`, 593) y
`validate_lesson_capitalization.py` (`[10/11]`, 635); **no** despacha `version_consistency_checker.py`
(`[1/7]`), `validate_plan_closure.py` (`[5/7]`) ni `build_lesson_index.py --check` (`[6/7]`). Los tres se
corrieron aparte:

| Paso | Payload | Corrido aquí | Salida | EXIT |
|---|---|---|---|---|
| `[1/7]` | `version_consistency_checker.py` (sin `--fix`) | ✅ esta sesión | CHANGELOG/VERSION 4.77.3 sincronizado · `REGISTRY OK` | **0** |
| `[2/7]` | `sync_versions.py --check` | ✅ esta sesión | `All files in sync` | **0** |
| `[3/7]` | `validate_opencode_refs.py` | ✅ (sin `--fix`) | `[PASS] todas las referencias existen` | **0** |
| `[4/7]` | `validate_plan_citations.py` | ✅ | `743 citas historicas, 0 nuevas y 0 crecimientos (79 archivos)` | **0** |
| `[5/7]` | `validate_plan_closure.py` | ✅ esta sesión | `[OK] ningún plan vivo declara cierre con filas pendientes` | **0** |
| `[6/7]` | `build_lesson_index.py --check` | ✅ | `[OK] Índice de lecciones fresco (332 IDs)` | **0** |
| `[7/7]` | `validate_lesson_capitalization.py` | ✅ | `[OK] … forma y trazabilidad verificadas` | **0** |

Crudos: `instrumentos/HOOK_1_7_*.txt`, `HOOK_2_7_*.txt`, `HOOK_5_7_*.txt` (los tres nacidos de esta
página) y `FINAL_*.txt` / `POST_lesson_index_check.txt` (los cuatro ya corridos al cerrar). En la columna
«corrido aquí» **✅ = la corrida existe en la evidencia de esta sesión**, sea como comando suelto o además
dentro del `--quick`; no significa que el verde del quick lo implique. **El hook como gate no se
ejecutó**:
`scripts/git_hooks/pre-commit` tiene `set -e`, su `[3/7]` corre con `--fix` (auto-arregla) y su `[6/7]`
regenera el índice — ejecutarlo habría escrito en el árbol y requeriría staged files, que esta sesión no
produce (commit no autorizado en ese momento). Lo que se afirma es lo que puede afirmarse sin eso: los
siete payload en modo lectura dan verde y el conteo de pasos no se movió.

**⟦Rectificada por el cierre de la misma sesión⟧ El hook SÍ llegó a ejecutarse como gate**: al commitear
(`cea8259`) corrió sus siete pasos y los siete dieron OK — `[1/7]` versión sincronizada, `[2/7]` las siete
reglas de sync `in sync`, `[3/7]` referencias `PASS`, `[4/7]` citas `PASS`, `[5/7]` cierre `PASS`, `[6/7]`
índice fresco con **332 IDs**, `[7/7]` capitalización `OK` → «All checks PASSED - Commit allowed». Con eso
queda observada la precondición que arriba se declaraba no ejecutable: el gate no encontró filas pendientes
en los planes que esta sesión reescribió, y **no** escribió en el árbol (`git status` después del commit
solo muestra la ruta ajena de JEV).

## Lo que esta par NO afirma

- ~~**No re-corre los mutation checks**~~ — **rectificado en la misma sesión:** sí se re-evidenciaron, mutante
  por mutante y por id, con `pytest -v` sobre los dos arneses. Crudos:
  `instrumentos/MUT_governance_numbers_por_asercion.txt` (**7 passed**: los 6 `M-A1/M-A4/M-A2/M-A3/M-POBLACION/M-SUJETO`
  más `test_las_dos_salidas_quedan_en_disco`) y `instrumentos/MUT_decision_client_guards.txt` (**13 passed**,
  con `M_AC6_token_prohibido`, `M_AC6_carga_dinamica`, `M_AC6_superficie_de_proveedores`,
  `M_AC7_proveedor_por_defecto` y los 6 guards de forma). Lo que **no** se hizo: editar código para
  fabricar un mutante nuevo — se usó el arnés existente, que es el que ya sabe mutar el guard real.
  **Ese arnés produjo además un hallazgo nuevo, registrado como S13** en `10-analisis`:
  `test_governance_numbers_mutation_por_asercion.py:29` tiene `EVIDENCE` apuntando a
  `evidence/…/FASE-A/mutation/`, así que correrlo **re-escribió 7 archivos cerrados de otra fase**. Sin daño
  medido (los 7 `git hash-object --path` casan con HEAD; `git status --porcelain evidence/` vacío), pero con
  los `mtime` movidos — que es el mecanismo por el que este patrón pasa desapercibido.
- **No afirma verde contractual**: `validate_governance_numbers.py` sigue emitiendo `HALLAZGOS` con
  A1–A4 y `exit 1` porque `.agents/` no se toca (AC17 → deuda D1). Ese rojo se conserva con su causa.
- **No toca el `--quick` ni el hook**: su composición no se reescribió, y eso está probado por hash de
  objeto, no por lectura del archivo.
