# FASE-D — par pre/post, resta comprobada y presupuesto declarado

Plan: `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20` · Fase: **D** · Fecha: **2026-09-24**
Corte usado: **«hasta listo para revisión»**. El commit **no** estaba autorizado en esta sesión, así que
no se hizo ni se simuló; y según el contrato (executor, *Cinco cortes*) el commit es una acción posterior
y separada, no un corte ni condición de ninguno. Los cinco cortes de D se verificaron sobre el árbol de
trabajo.

## 1. AC16 — conteos de checks: delta **0**, con la resta

La composición del `--quick` y del hook **no** se tocó en esta fase. Los valores los imprimen los
comandos; este archivo los registra como **par**, no como cifra vigente del repo.

| Conteo | Comando (idéntico en los dos lados) | PRE (antes de la primera edición) | POST (árbol final verificado) | Resta |
|---|---|---|---|---|
| Etiquetas `[N/11]` en `scripts/run_all_validations.py` | `grep -cE '^\s*print\(f?"\[[0-9]+/11\]' scripts/run_all_validations.py` | **11** | **11** | **0** |
| Pasos `[N/7]` en `scripts/git_hooks/pre-commit` | `grep -cE '^#   \[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit` | **7** | **7** | **0** |
| `--quick` completo | `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **11/11, `exit 0`** (`faseD_quick_pre.txt`) | **11/11, `exit 0`** (`faseD_quick_post.txt`) | **0** |

Archivos del par: `faseD_baseline_pre.txt` / `faseD_baseline_post.txt`. El PRE se capturó **antes de la
primera edición de código**, con el HEAD de la sesión anotado dentro (`5817edd` en los dos lados: la fase
no commiteó, así que la cabecera no se movió).

## 2. AC17 — `.agents/`: la casilla literal no era evaluable y se reformuló **midiendo**

| Concepto | PRE | POST |
|---|---|---|
| Rutas sucias bajo `.agents/` | **3**, todas ajenas a la fase (`phased_project_executor.md`, `templates/lecciones-capitalizadas-template.md`, `templates/prompt-fase-template.md`, del bloque B de la orden de calidad) | **las mismas 3** |
| `sha256` de los cuatro `.md` de `.agents/` | cuatro valores en `faseD_baseline_pre.txt` | **los cuatro idénticos** (`diff` vacío, impreso al pie de `faseD_baseline_post.txt`) |

La fila de AC17 en A y B decía «`git status --porcelain .agents/` vacío». Sobre este árbol eso ya no
describe nada: un `git status` **lleno** tampoco probaría que la fase escribió. Lo que goberna AC17 es
**cero bytes aportados por la fase**, y se afirma con dos instrumentos: el `sha256` de arriba y el
observador de escrituras compartido (`tests/support_observador_escrituras.py`, alcance declarado:
proceso de pytest, no procesos hijos), que no registró ninguna escritura dentro de `.agents/` durante la
selección. Un test además busca una tajada de 600 bytes del workflow y exige que **no** aparezca en
ningún pack.

## 3. Lo que **sí** se movió en esta fase, declarado aparte y no maquillado

| Magnitud | PRE | POST | Quién lo mide y qué resta significa |
|---|---|---|---|
| Funciones de test en `tests/` (`grep -rE '^\s*def test_' tests --include=*.py \| wc -l`) | **4.508** (reconstruido: `--exclude-dir=phase_briefing`, que reproduce exacto el POST que publicó C) | **4.557** | Resta **+49** = la contribución propia, contada con su propio comando (`… tests/quality_gates/phase_briefing`). Crudo: `test_count_pre_post.txt`. **No es la resta total del árbol**: al abrir, el árbol traía 63 rutas de trabajo ajeno sin commitear |
| Archivos de la selección | 0 | **12** (10 de test + `conftest.py` + `__init__.py`), 1.287 líneas | Los 7 nombrados por el mandato + AC20 + AC23 + el del guard de red (añadido por medición, ver `criterios-de-completitud.md`) |
| Instrumento nuevo | 0 | `scripts/build_phase_briefing.py`, **1.062 líneas**, stdlib-only | Su superficie de imports está auditada por AST en `cero-red.txt` |
| Packs generados | 0 | **5** en `…/briefing/` (A, B, C, D, RELEASE) | Son corpus: **re-vencen el índice de lecciones** y fueron la causa del rojo de la corrida 1 de `regression_calidad.txt` (**L-VCF-17**) |
| Carga total de lectura de las cinco fases (AC20) | **1.648.109** bytes (`stat -c %s` sobre 33 rutas) | **1.431.388** bytes (`stat` sobre 11 rutas) + 808 de coste de generar | Delta **216.721 bytes** ≈ 54.180 tokens por divisor 4 declarado = **13,08 %**. Cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py`, `exit 0`. La fuente de estas cifras es `carga.json` / este archivo: **ningún `.md` del corpus las transcribe** (**L-VCF-19**) |
| Índice de lecciones (`build_lesson_index.py --check`) | **fresco** al abrir (335 IDs) | **fresco** al cerrar, **339 IDs** | La fase define cuatro lecciones nuevas (**L-VCF-16/17/18/19**) y el barrido de citas añade menciones. A6 reproduciéndose sobre la fila: escribir el cierre mueve la cifra del cierre, y por eso ningún artefacto de D la pinea |
| `docs/contributing/REGISTRY.md` | ya traía +45/−2 de trabajo ajeno | entrada de FASE-D **apilada por el propio writer** (`log_phase_completion.py`, una sola corrida) | El writer es aditivo y **declara, no aprueba**. No se hizo `checkout`/`restore`/`stash` sobre esa ruta |
| Los **prompts de fase** de este plan (`05-prompt-inicio-sesion-fase-*.md`) y los de los otros tres planes | **ya estaban modificados al abrir**: `git diff --numstat` sobre el de D da **+97/−26**, y los de C y RELEASE también figuran modificados | **sin cambio por la fase** | Es el bloque C de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22` (enmiendas ⟦2026-09-24⟧ autorizadas sobre los documentos de los cuatro planes). **D los leyó y no los editó** — el mandato lo prohíbe y el generador los consume como fuente; atribuírselos a D sería el defecto que **L-VCF-11** capitaliza (una resta ajena contada como propia) |

## 4. Presupuesto (R2.1) — instrumento, corte y **unidad declarada**

**El instrumento canónico NO corrió.** `find . -name "*.jsonl" -not -path "./venv/*" | wc -l` = **0** al
abrir y **0** al cerrar (re-medido, no copiado del prompt): es la **octava reproducción** de la
precondición que capitalizó **D-V2.1**, y `evidence/FASE-D/measure_iterations.py` pide el transcript del
cliente, que no existe en el workspace.

**Y en esta fase el auto-reporte tampoco es reconstruible.** FASE-D pasó por una **compactación de
contexto a mitad de sesión**, así que la cuenta de bloques `tool_use` propios ya no está disponible para
contarla a mano. Publicar un número «de memoria» sería exactamente el defecto que **L-VCF-18** capitaliza
en esta misma fase (una resta que cuadra sobre un minuendo que nadie midió). **La métrica se retira, no se
estima**, y se declara la unidad que sí es contable.

Unidad contable publicada, con su comando y su crudo:

| Unidad | Valor | Comando |
|---|---|---|
| Rutas propias de la fase, desglosadas (sin colapsar directorios) | **57** | `{ git ls-files --others --exclude-standard -- <rutas de D>; git diff --name-only -- <plan>; } \| sort -u \| wc -l` |
| Rutas sucias totales del árbol (para no atribuirse lo ajeno) | **80** | `git status --porcelain \| wc -l` |
| Líneas de instrumento | **1.062** | `wc -l < scripts/build_phase_briefing.py` |
| Líneas de la selección | **1.287** | `cat tests/quality_gates/phase_briefing/*.py \| wc -l` |
| Archivos de evidencia de FASE-D | **28** | `find evidence/…/FASE-D -type f \| wc -l` |
| Corridas de verificación consumidas | **7** regresiones `tests/quality_gates` — **3 rojas con su causa atribuida y conservadas** y 4 verdes, de las que la **sexta** es la de referencia del cierre (y la séptima la confirma) —; + 4 selecciones propias, 3 `r26`, 4 mutation checks, 6 regeneraciones de pack con su `--check`, 4 `--quick` y 5 `build_lesson_index` con su `--check` | registradas en `regression_calidad.txt` (que guarda el stdout literal de las cinco corridas resumidas en `instrumentos/corridas-crudas-2026-09-24.zip`), `run_tests.txt`, `r26.txt`, `mutation/resumen.txt`, `generacion_stderr.txt`, `check_final.txt`, `ac18-tres-verificadores.txt` y `faseD_quick_post.txt` |

**Límite declarado:** esta unidad **no es comparable** con las tres horas de FASE-B, ni con el
auto-reporte en `tool_use` de FASE-C, ni con ninguna otra. Sirve para responder «cuánto costó cerrar D» en
número de artefactos, no de iteraciones. **D-V2.1 sigue abierta** y su dueño sigue siendo el mismo:
mientras el workspace no tenga transcripts, la métrica de iteraciones no es medible con instrumento.

## 5. Comprobación aritmética del par

- Quick: 11 − 11 = **0** (delta esperado 0 por AC5/AC16) — cumplido.
- Hook: 7 − 7 = **0** — cumplido.
- Carga: 1.648.109 − 1.431.388 = **216.721**; y por construcción debe cuadrar
  `delta == omitido − andamiaje − coste` por fase. Las cinco `resta_comprobada` son `true` y el
  instrumento sale `exit 0` (`carga-pre-post.md`).
- Tests: 4.557 − 4.508 = **49** = contribución propia medida por separado. **No** se afirma que el árbol
  haya crecido solo lo de D: 63 rutas ajenas estaban sucias al abrir.

## 6. Lo que queda fuera por no commitear (deuda declarada, no silencio)

Sin autorización literal de commit, **no viaja** en ningún commit: los `.md` de este plan (`00`, `06`,
`09`, `10`, `README`, `dependencias-fases`), los 5 packs generados, el par
`.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json`, `docs/contributing/REGISTRY.md` y el
trabajo ajeno de BLOQUE-B/BLOQUE-C y de los otros tres planes. Consecuencia medida y ya capitalizada en
C (**L-VCF-15** / **S15**): un commit propio verificado en su propio árbol (`git archive HEAD` extraído y
corrida ahí) daría `[6/7]` **rojo** con el par sin regenerar, y regenerarlo allí **no** lo cura porque 9
entradas del par sellan su fecha en el `mtime`. Por eso la instrucción del operador de **no** «curar» el
`--check` commiteando el par sigue vigente y no se tocó.
