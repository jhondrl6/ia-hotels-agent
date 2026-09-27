# Lecciones Capitalizadas — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> **Creado**: 2026-09-20, antes de `01-plan-maestro.md`. **Actualizado**: al cierre de cada fase.
> **Plan**: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 · **Objetivo**: cerrar la mitad que
> `validate_lesson_capitalization.py` declara fuera de alcance (la **pertinencia**), la coherencia
> numérica entre el workflow canónico, sus templates y el código que ejecutan, y la **carga de
> lectura** que cada sesión de fase arrastra antes de tocar código.

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado medido |
|---|------|------------------|------------------|
| Q1 | Índice generado (capa fría) | `for id in L-R.1 L-R.3 L-R.4 L-NC10 L-PF6 L-PF10 L-D3 L-V2.3 L-T4A.5 L-VUP-5; do grep -oE "\\| \\\`${id}\\\`.*" .opencode/LECCIONES-INDEX.md; done` | **10 de 10** devuelven fila con dueño y conteo de citas |
| Q2 | Índice generado — corpus **completo** por síntoma | `grep -icE "numer" .opencode/LECCIONES-INDEX.md` · `… "fosiliz"` · `… "renumer"` · `… "denominador"` · `… "cobertura medida"` · `… "falso verde"` | 20 · 7 · 1 · 1 · 2 · 2 |
| Q3 | Índice generado — término buscado, **cero coincidencias** | `grep -icE "verificador mec" .opencode/LECCIONES-INDEX.md` | **0** — medido en vivo, ver §3-descarte D5 y AC15 |
| Q4 | Población del índice (denominador) | `head -18 .opencode/LECCIONES-INDEX.md` | **Re-medido tras cada regeneración**: 15 análisis + 36 `CONTEXT-*.md` como definiciones; **320** IDs con definición detectada; **50** citados sin definición; **402** `.md` como corpus de citas. La fila decía 14 / 49 / 389 al concebirla, pasó a 15 / 50 / 401 al entrarse el plan y a **402** al escribirse el prompt de FASE-D — tres valores en una sesión; ver maestro §1, medición **A6** |
| Q5 | Fuente de verdad dinámica de los conteos | `grep -nE 'print\("\[[0-9]+/[0-9]+\]' scripts/run_all_validations.py` | 11 etiquetas `[N/11]` (quick) y 4 `[N/15]` (full). **La lectura útil es la asociación etiqueta ↔ `def _check_*`, no la lista**: `[12/15]` es `def _check_dependencies` y `[15/15]` es `def _check_qmind_writeback`. Omitir ese emparejamiento produjo la medición vencida de A3 (ver maestro §1, rectificación de A3 y medición A8) |
| Q6 | Memoria de proyecto (capa caliente) | `MEMORY.md` → entradas *verificador-medido*, *no-implementar-aun*, *quien-produce-el-dato-publicado* | 3 entradas leídas; la tercera fija que la cura de una aserción vencida es un **writer o un verificador**, no el edit |
| Q7 | Notebook QMind `iah-cli-lecciones` | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "…" --format agent --non-interactive` | **Concebida como NO EJECUTADA** («el CLI no está disponible en esta sesión»); **ejecutada el 2026-09-20 en la auditoría de la concepción**, con el CLI disponible y autenticado (v3.3.0, 49 fuentes en el notebook). Cuatro consultas: conteos desfasados, carga de lectura por fase, pertinencia del Paso 0, presupuesto de iteraciones. **El comando original con el nombre (`--nb iah-cli-lecciones`) devuelve `error: Bad request`: `--nb` exige el ID** (medido con las dos formas). Resultados capitalizados abajo como L-V2.1, L-V2.2 y D-V2.1; deuda **D8** re-escrita |
| Q10 | Re-medición de la premisa al abrir **FASE-B** (2026-09-21) — el prompt de FASE-A dejaba la herencia y B no la asumió | `git rev-parse --short HEAD` · `git status --porcelain` · `grep -cE 'print\(f?"\[[0-9]+/11\]'` sobre `run_all_validations.py` · `grep -cE '^#   \[[0-9]+/[0-9]+\]'` sobre el hook · `git ls-files '*.py' \| wc -l` · `git grep -cE '^\s*(import\|from)\s+(typesafe\|jev\|httpx2)' -- '*.py'` · `python -c "import importlib.util as u; print([u.find_spec(m) is not None for m in ('typesafe','jev','httpx2','tenacity')])"` bajo el venv del producto · `find . -name '*.jsonl' \| wc -l` · `stat -c %s` sobre los siete documentos de A7 | HEAD ya no era `e3c4573` sino **`74d8ff5`** (dos commits de barrido documental de FASE-A encima), árbol con **dos rutas ajenas** preexistentes y ninguna creada por B; quick **11**, hook **7**; **0** imports del SDK en los 678 `.py` rastreados (692 en el árbol de trabajo al cerrar; 690 en el primer escaneo) y el SDK **AUSENTE** del venv del producto — pero **presente en el disco** bajo `tmp_test/venv-jev-sdk`, exclusión publicada con su conteo; `*.jsonl` = **0** (D-V2.1 reproducida de nuevo, el instrumento de presupuesto otra vez fuera de servicio); A7 **263.973 bytes ≈ 65.993 tokens**, sin cambio |
| Q11 | **Re-medición tras el commit de FASE-B (2026-09-22)** — el barrido de citas que ese mismo commit venció | `git rev-parse --short HEAD` · `git status --porcelain` · `git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git show --numstat --format="" 647f436 \| grep -cE '\\.py$'` · `git ls-files '*.py' \| wc -l` · `python scripts/decision_client.py --scan-imports` · `grep -cE 'print\\(f?"\\[[0-9]+/11\\]'` sobre `run_all_validations.py` · `grep -cE '^#   \\[[0-9]+/[0-9]+\\]'` sobre el hook · `find . -name '*.jsonl' -not -path './venv/*' \| wc -l` | HEAD **`647f436`** (el commit de B: 46 archivos, +4.412/−97, **13** de ellos `.py`) sobre `eecf246`, que **sigue sin empujar** — el remoto está en `74d8ff5`, paridad **`0/2`** a esa hora (`0/3` al cerrar el barrido que escribe esta fila: cada commit documental suma uno), con el push todavía sin autorizar a esa hora — **quedó hecho el mismo día: `origin/master` en `b764e8d`, paridad `0/0` re-medida tras `git fetch`, y el push publicó de paso el commit ajeno `eecf246`**; **una** ruta ajena sucia. El denominador que la fase publicó quedó refutado por su propio commit: `git ls-files '*.py'` **678 → 691**, mientras el escáner sigue viendo **692** y el numerador **no se mueve** (`SIN-HALLAZGOS`, 0 imports, 0 cargas dinámicas, 21 menciones). El residuo de 1 se **descompuso** con `comm` contra el `rglob` y es `.venv-wsl/bin/activate_this.py` → **S11** / **L-VCF-11**. Quick **11**, hook **7** (sin cambio), `*.jsonl` = **0** (sexta reproducción de D-V2.1, el instrumento de presupuesto sigue fuera de servicio); índice regenerado tras el barrido: **332** IDs definidos + 51 sin definición, **16** análisis y **416** `.md` citados (330 antes del barrido; el +2 son L-VCF-11 y L-VCF-12, y los análisis/.md se mueven por el plan hermano `EVALUACION-JEV-TYPESAFE-2026-09-21`, entrado al corpus en `2c966f6` con 12 `.md`). **Y el propio re-muestreo pisó la evidencia cerrada de FASE-A** (`--report` con destino hardcodeado), medido y revertido → **L-VCF-12** / **S12** |
| Q13 | **Re-medición de la premisa al abrir FASE-D (2026-09-24) — la herencia de D no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `git status --porcelain .agents/` · los dos `grep -cE` del quick (11) y del hook (7) · `python scripts/run_all_validations.py --quick` · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `stat -c %s .agents/workflows/phased_project_executor.md` · `python scripts/build_phase_briefing.py --listar-declarado --plan <este plan>` · recuento de prompts que declaran lectura: `Glob .opencode/plans/Archives/*/05-prompt-inicio-sesion-fase-*.md` filtrado por el parser · `python scripts/build_lesson_index.py --check` sobre un arbol extraido con `git archive HEAD` | HEAD **ya no era el `da382b1` que registro C: es `5817edd`** — el commit y el push del propio cierre de C movieron la cabecera despues de que C escribiera su evidencia (A6 sobre la fase anterior, medida al abrir la siguiente); paridad **`0 0`** verificada con `fetch` + `ls-remote`, no inferida. Arbol con **63 rutas sucias ajenas** al medir (ninguna creada por esta sesion al abrir) y **3 de ellas bajo `.agents/`** (executor y dos templates, del bloque B de la orden de calidad) — lo que hace **no verificable la casilla literal** «`git status .agents/` vacio al cerrar», reformulada como «cero bytes aportados por la fase» y afirmada con el observador de escrituras. Quick **11/11 `exit 0`** como par PRE y hook **7**. `*.jsonl` = **0** → **octava reproduccion** de la precondicion de **D-V2.1**, metrica retirada y auto-reporte con unidad declarada. **A7 vencida en su propio dato de entrada**: el workflow canónico pesa hoy **108.017 bytes**, no los **98.694** que publica el maestro §1 (+9.323 desde 2026-09-20, por las ediciones del bloque B), y la carga declarada de **este** plan es **5 fases · 34 fuentes**, con su total en `FASE-D/carga.json` (el número **no se copia aquí**: ver **L-VCF-19** — este `.md` entra en el pack que ese `stat` mide, y de hecho la corrida del cierre lo movió **dos veces**, una por cada barrido documental que se escribió después de medirlo). **Y la convencion que parsea el generador resulto minoritaria**: de **121** prompts archivados, **0** declaran su lectura con la cadena `Lee …`; los unicos **5** del repo estan en este plan → deuda **S16**. El `--check` del indice dio **FAIL** (`exit 1`) tambien sobre un arbol limpio extraido de `5817edd` con `git archive`; **regenerado en ese mismo arbol** paso a `exit 0` con **335** IDs — que es la firma de **S15**: 9 entradas con `fuente_fecha = mtime`, de modo que cada extraccion las vuelve a vencer y commitear el par desde otro arbol no lo cura. Nada del antecedente del prompt se copio como valor vigente |
| Q12 | **Re-medición de la premisa al abrir FASE-C (2026-09-24) — la herencia de C no se asumió** | `git rev-parse --short HEAD` · `git status --porcelain \| wc -l` · `git fetch origin --quiet && git rev-list --left-right --count origin/master...HEAD` · `git ls-remote origin refs/heads/master` · `python scripts/build_lesson_index.py --check` · `python scripts/run_all_validations.py --quick` · los dos `grep -cE` del quick (11) y del hook (7) · `find . -name "*.jsonl" -not -path "./venv/*" \| wc -l` · `python scripts/decision_client.py --scan-imports` · `ls .opencode/plans/Archives/ \| wc -l` y `ls .opencode/plans/Archives/*/00-lecciones-capitalizadas.md` | HEAD **sin cambio** respecto del antecedente publicado y **paridad verificada contra el remoto** (`fetch` + `ls-remote` + `0 0`), no inferida de la frase del README; árbol con **62 rutas sucias de trabajo ajeno** (las del bloque B, del bloque C de la orden y de `EVALUACION-JEV`), ninguna creada por esta sesión al medir; índice **fresco** con su cifra leída del comando (no pineada en ningún artefacto de C); quick **11/11 `exit 0`** como par PRE de AC16 y hook **7**; `*.jsonl` = **0** → **séptima reproducción** de la precondición de **D-V2.1**, el instrumento de presupuesto sigue fuera de servicio y C declara auto-reporte con unidad propia; AC6 `SIN-HALLAZGOS` / `exit 0` **antes** de escribir C. **Y la premisa de AC13 resultó vencida en su ruta**: el prompt decía `Archives/`, el `archives/` de raíz **no contiene planes**, y el corpus efectivo es `.opencode/plans/Archives/` con **27** archivados de los que **2** tienen `00-` que triar. Nada del antecedente del prompt se copió como valor vigente |
| Q9 | **Re-medición de la premisa al abrir FASE-A (2026-09-21)** — el prompt ordenaba no asumir el árbol | `git rev-parse --short HEAD` · `git status --porcelain | wc -l` · `git ls-remote origin refs/heads/master` · `grep -nE '^[[:space:]]*(def _check|print.f?"\[[0-9]+/[0-9]+\])' scripts/run_all_validations.py` · `grep -nE '^#[[:space:]]+\[[0-9]+/[0-9]+\]' scripts/git_hooks/pre-commit` · `stat -c %s` sobre los siete documentos de A7 · `grep -rhoE '\[[0-9]+/[0-9]+\]' <los dos documentos> | wc -l` | HEAD ya **no** era `2c9d0c1`: es `2deddee`, con once commits de `EVALUACION-JEV-TYPESAFE-2026-09-21` encima; árbol **limpio** y paridad `0/0` con `origin/master` **conservadas**. El emparejamiento etiqueta ↔ `def _check_*` reproduce A1–A3 (`validate_plan_citations` 9/11, `validate_lesson_capitalization` 10/11, `validate_qmind_writeback` **15/15** solo en el modo completo); el hook sigue en **7** pasos; A7 sigue en **263.973 bytes** y la población A8 se reprodujo **exacta**: 22 instancias con corchete en 17 líneas + 2 formas «check N». **Ninguna premisa del plan caducó en la ventana de A salvo el HEAD anunciado**, que es justo lo que el prompt ordenaba medir |
| Q8 | Carga de lectura de una sesión de fase (medición A7) | `for f en los 7 documentos sumados (más 1 de evidencia excluido) que declara leer 05-prompt-inicio-sesion-fase-B.md del plan en vuelo; do stat -c %s "$f"; done` y sumar | Al concebir: **254.010 bytes ≈ 63.502 tokens**. **Re-medido el 2026-09-20: 263.973 bytes ≈ 65.993 tokens** (+9.963; crecieron `06-checklist`, `00-lecciones`, `dependencias-fases` y el propio `05-…-fase-B.md` al cerrarse FASE-G y FASE-B del plan medido). Divisor 4 declarado. El workflow canónico aporta 98.694 bytes, de los cuales ~20 KB son plantillas de cierre |

**Regla**: la consulta debe ser copy-pasteable. Q1–Q6 y Q8 se re-ejecutan tal cual; **Q7 solo con el
ID del notebook** (la forma con el nombre que aparece en el workflow canónico devuelve `Bad request`,
medido el 2026-09-20). **Toda cifra de Q4
y Q8 caduca al escribir cualquier `.md` del corpus** — ver maestro §1, mediciones A6 y A7.

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-R.1 | Una regla que vive solo en el workflow y no en el artefacto que la fase rellena, se cumple por coincidencia | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | El plan existe porque las aserciones numéricas del workflow y de su template **no las sostiene ningún check**: se cumplen por coincidencia y hoy están vencidas | AC1 · FASE-A Tarea 1  · **aplicada el 2026-09-21 en FASE-A:** el verificador ahora contrasta contra la etiqueta impresa por el `def _check_*` que la ejecuta; las cuatro aserciones siguen vencidas sin que ningún gate las sostenga, y el guard existe (reporta, no reescribe) |
| L-R.3 | Un `[OK]` sin denominador no informa: el verificador publica la población que miró | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Ninguna salida del lint o del triaje puede decir «sin hallazgos» sin imprimir cuántas aserciones/IDs miró y quiénes quedaron exentos | AC2 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `coverage_basis` es obligatoria y el favorable está bloqueado sin ella (prueba `test_la_salida_favorable_no_existe_sin_denominador`); con denominador impreso: 24 miradas / 11 correctas / 8 congeladas / 0 no resueltas · **aplicada el 2026-09-21 en FASE-B (AC6/AC9):** el `0` de imports se publica con **dos** poblaciones (678 rastreados por `git grep` / 692 del árbol que ve el AST), los 4.379 nodos de import vistos, las 21 menciones-no-import aparte y los excluidos por directorio con su conteo; y el `1` de `files_changed_to_add_provider` sale de sha256 sobre la frontera copiada, no de una afirmación (L-VCF-8) · **aplicada el 2026-09-24 en FASE-D:** `coverage_basis` del informe imprime 5 packs por estado, 34 fuentes, 23 secciones pedidas / 23 resueltas y las cinco familias no cubiertas; y el corpus real se publica con su denominador de convencion (**0 de 121** prompts archivados declaran lectura) en lugar de un `[OK]` a secas |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Las tres reglas que este plan no cierra (promoción al quick, rebanado del workflow, arreglo de `.agents/`) se publican con dueño y disparador, no se callan | AC17 · `dependencias-fases.md` §Deuda  · **aplicada el 2026-09-21 en FASE-B:** la comparación de proveedores se declaró **fuera de alcance** en `extensibilidad.txt` con su porqué (D7) y la decisión de geometría que este plan **no** tomó salió con dueño y disparador nuevos: **S10** (L-VCF-9) |
| L-NC10 | Fosilización narrativa como clase de bug: templates con texto estático que ignoran la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22` | Mismo defecto, otro artefacto: el template fija «`[10/10]` de `--quick»` cuando el código emite `[10/11]`. La cura es comparar contra la fuente, no reescribir la frase | AC1 · AC4  · **aplicada el 2026-09-21 en FASE-A:** la lista de aserciones se **descubrió** escaneando los dos documentos (24 instancias: 22 con corchete + 2 formas «check N»), no hardcodeada; A1 apareció en dos sitios que el patrón nunca había visto juntos · **aplicada el 2026-09-24 en FASE-D:** el generador no recibe ninguna lista de lecturas por configuracion: parsea la que el propio prompt declara. El test confronta `parsear_lista_lectura(prompt)` contra las fuentes del pack emitido, y `no_incluye[]` publica los bytes que quedaron fuera de lo declarado |
| L-PF6 | Un lector roto leído como ausencia real produjo un pain falso HIGH con cifra económica | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El triaje lee `lecciones_index.json` y el lint lee `.agents/`: ambos publican los tres estados, y un parser que revienta jamás devuelve «sin candidatos» | AC3 · AC11  · **aplicada el 2026-09-21 en FASE-A:** cuatro caminos de `LECTOR-FALLIDO` con motivo propio (fuente sin etiquetas, hook sin pasos, documento sin patrones, sujeto ambiguo por alias); ninguno devuelve «sin hallazgos» · **aplicada el 2026-09-21 en FASE-B (AC7):** la prohibición del default es el eje del módulo — `evaluar()` sin proveedor **falla** con 5 `motivo_clase` que no colapsan, y el mutante `M-AC7-proveedor-por-defecto` muestra que ceder un default sí fabricaría una decisión. Coste propio descubierto al medir: la regla «nadie más importa el SDK» aplicada sin graduar producía **16 hallazgos ajenos** (L-VCF-7) · **aplicada el 2026-09-24 en FASE-D:** el lector de la lista declarada falla ruidoso y por causas separadas — `--plan` inexistente = exit 2 con sus tres rutas intentadas; fuente ausente = el pack **no se emite** (exit 1) con la ruta buscada; meta sin sha = `FUENTE-ILEGIBLE`, que no colapsa con `FUENTE-AUSENTE` ni con `SHA-DISTINTO` |
| L-PF10 | Vacío ≠ ausente: la lista quedó vacía **porque el fix funcionó**, y el extractor devolvía `None` igual que cuando el dato no existe | `Archives/SR-PIPELINE-FIXES-2026-08-27` | El estado `SIN-HALLAZGOS` del lint es un resultado positivo y debe decir sobre qué midió; `AUSENTE` debe imprimir la ruta buscada y el comando de regeneración | AC3 · AC11 · AC15  · **aplicada el 2026-09-21 en FASE-A:** `SIN-HALLAZGOS` imprime sobre qué midió y `AUSENTE` la ruta buscada; un documento no vacío con 0 instancias es fallo de lectura, no «limpio» · **aplicada el 2026-09-21 en FASE-B:** `respuestas: []` es `ILEGIBLE` con causa `respuesta-vacia:list` (no «cero decisiones favorables»), `usage=None` **no** es consumo cero, y `noul.confidence` es `None` **con su motivo escrito**, no un 0.0 que FASE-C leería como certeza · **aplicada el 2026-09-24 en FASE-D:** al trío de AC22 hubo que sumarle un cuarto estado, `SIN-DECLARACION` (pack emitido con cero fuentes gobernadas), y el `--check` lo imprime como `SIN-FUENTES` en lugar de `OK` — con test que prohíbe la palabra OK en esa salida. Motivo medido: 121 prompts archivados no declaran lectura, y llamarlos «completos» era el verde vacio de L-HF1 |
| L-D3 | Un baseline numérico hace que cumplir el plan cuente como violación | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El invariante «el quick sigue en 11 checks» se formula como **delta** con par `*_baseline_pre/post.txt`, no como número absoluto | AC5 · AC16 · AC20  · **aplicada el 2026-09-21 en FASE-A:** los conteos se publicaron como delta con par pre/post y la resta (quick 0, hook 0, población A8 0); la métrica que sí se movió (tests, +23) se declaró aparte en lugar de maquillarla · **aplicada el 2026-09-21 en FASE-B:** quick 11→11, completo 4→4, hook 7→7, `.agents/` 98.694/6.123 idénticos y población AC6 678 sin mover y 690→**692** en el árbol (+2 por los instrumentos de la propia fase: nota 3 en `FASE-B/baseline-pre-post.md`) — con **+48 funciones / 53 casos** de tests publicados por separado. Y una elección de unidad: no se publicó un `tool_use` aproximado, porque no era medible (R2.1) · **aplicada el 2026-09-24 en FASE-D:** la carga de lectura se goberno como delta con par `faseD_carga_pre/post.txt` (`stat -c %s`) y resta **entre cargas totales**; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (exit 0) y quick 11→11 / hook 7→7. Y un test planta una fuente diminuta para exigir que un delta **negativo** se publique con la misma identidad, no que se esconda |
| L-V2.3 | Renumerar el hook sin medir quién afirma el número de checks deja contrato huérfano | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Este plan **no renumera** nada: su AC5 y AC16 exigen medir la población que afirma los conteos antes de tocarla, y no pinear literales | AC5 · AC16 · AC8  · **aplicada el 2026-09-21 en FASE-A:** el barrido de `tests/` mostró que **esta fase añadió 4 pins del denominador 11** al fijar el contrato AC1 (L-VCF-5), declarados con dueño D1/D2 en vez de limar la aserción · **aplicada el 2026-09-21 en FASE-B (AC8):** el contract test afirma la **forma** y compara el modelo contra lo que el proveedor falso **declara**, nunca contra una cadena; el pin `jev-1.13.0` vive en `PIN_MODELO_DECLARADO` con `usado_por_el_codigo: false` y un test lo comprueba por AST (aparece una sola vez: su definición). FASE-B **no añadió** pins del 11 ni del 7 (4→4, medido) · **aplicada el 2026-09-24 en FASE-D:** AC21 se prueba **escribiendo la fuente en disco** y re-midiendo contra ese disco (y al revertir, verde); y AC23 se anclo con una cadena exclusiva del generador, porque «rutas intentadas» y «seccion pedida» ya vivian dentro de los documentos que el pack copia — un mutante anclado ahi daba rojo sin serlo |
| L-V2.1 | Un test que solo mira **qué check** disparó puede quedar verde por una rama distinta de la que pretendía observar | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | Cada mutante de AC4 y AC14 se afirma sobre el `assertion_id`/la detección que dice atacar, no sobre «el script devolvió un hallazgo»: el rojo tiene que nombrar la aserción mutada | AC4 · AC14 |
| L-V2.2 | Un verificador no debe apoyar su conclusión en el artefacto generado por **otro** gate | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` | FASE-C lee `lecciones_index.json`, que produce `[6/7]`; la cura ya implementada por ese plan es **calcular el índice en memoria** con `build_lesson_index.build()` (0,30 s medidos). ⟦**Ruta CERRADA el 2026-09-23, contrato E2**: FASE-C consume el JSON **tras ejecutar él mismo** la comprobación de frescura, de modo que `VENCIDO` sea estado producido por su propio check y no por un `--check` ajeno; la ruta (a) queda descartada porque **borraría** el estado que AC11 exige, y sigue prohibida la tercera vía (leer el JSON confiando en que otro paso lo regeneró). Coste publicado: C es responsable de su suelo y hace dos lecturas del JSON por corrida⟧ | AC11 · AC15 |
| D-V2.1 | El instrumento canónico de R2.1 no alcanza el transcript de sesión bajo el cliente actual; la medición se publica como auto-reporte con **unidad declarada** | `Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` (definida allí; **reproducida en cuatro fases seguidas** por `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`) | El `04-contrato-ejecucion.md` de este plan ya aplica el patrón (instrumento, corte, y si no corre: unidad declarada, «no comparable», o métrica retirada — nunca estimada). Verificado el 2026-09-20: `find . -name "*.jsonl"` devuelve **0** dentro del workspace, la misma precondición del incidente | **AC5** · **AC16** (par pre/post por fase) · `04-contrato-ejecucion.md` §Corte de presupuesto |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | Todo AC de detección del plan se cierra con mutation check sobre el símbolo real del guard, con las dos salidas en evidencia | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** seis mutantes sobre los símbolos reales del guard, con verde y rojo en disco — y el primer intento de anclaje (id posicional) **no** observaba la rama que decía certificar: ver L-VCF-1 · **aplicada el 2026-09-24 en FASE-D:** mutation check con las dos salidas en disco — apagado `GUARD_NO_TRUNCAMIENTO_ACTIVO` el pack conserva el estado `SECCION-NO-RESUELTA` pero **pierde la declaracion del recorte** y se achica en silencio (los dos tamaños y su diferencia viven en `FASE-D/mutation/resumen.txt`; **no se transcriben aquí**: este `.md` entra en el pack que lo mide → **L-VCF-19**). Un test aparte exige que el mutante NO cambie el estado: si lo cambiara, el rojo vendria de otra rama (L-V2.1) |
| L-VUP-5 | Una fase de extensión que no produce ni un rojo es un falso verde potencial | `Archives/VALIDADOR-URL-PROPIA-2026-08-30` | El verde de la primera corrida del lint se reporta **sospechoso** y se explica, nunca como éxito | AC4 · AC14  · **aplicada el 2026-09-21 en FASE-A:** el verde de la primera corrida **fue sospechoso y lo era**: la regla de población se rectificó dos veces y el mutation check nombraba a la aserción equivocada · **aplicada el 2026-09-21 en FASE-B:** la primera corrida de la selección dio **30 fallos** (f-string mal cerrado, `score` cayendo en `opciones` por argumento posicional, 8 aserciones mal apuntadas) y el primer mutante de forma apagaba la lista **entera**, que no aislaba a ningún guard (L-VCF-6). Rojos propios además de los buscados: AC8 guarda su `exit 1` en `contract.txt` |
| L-HF1 | Un candado con la cobertura equivocada pasa en verde mientras el artefacto miente | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El lint declara las familias de aserción que **no** cubre, una por una y medidas: prosa de conteo sin patrón, conteos fuera de los documentos de gobierno (`AGENTS.md`, `docs/GUIA_TECNICA.md`, `docs/contributing/REGISTRY.md`), pins de conteo en `tests/` y toda fuente dinámica que no sea etiqueta impresa. Ese límite es AC, no nota al pie | AC2 · AC17  · **aplicada el 2026-09-21 en FASE-A:** `families_not_covered[]` salió de la AC y del script: las cuatro familias medidas en el informe (3 / 245 / 4 archivos / 4.330 funciones en disk), y `git status --porcelain .agents/` quedó vacío · **aplicada el 2026-09-21 en FASE-B:** el escáner publica sus cuatro límites medidos (carga no literal → 16 sitios contados y no callados; dependencias declaradas → no miradas, es D7; menciones en prosa → aparte; exclusiones → con su conteo) y `git status --porcelain .agents/` volvió a quedar vacío con 98.694/6.123 bytes idénticos · **aplicada el 2026-09-24 en FASE-D:** `no_incluye[]` no vacio es exigido por test fase por fase, y del medir salio una regla nueva: lo que vive **fuera** de `.opencode/` se declara lectura aparte y no se copia, porque copiarlo dentro del plan ampliaba la poblacion que escanea `validate_opencode_refs.py` y un artefacto derivado le devolvio rojo al quick ([8/11]) por referencias ajenas |

Dueños distintos representados: **6** — TRIBUNAL-OFFLINE, REFACTOR-COHERENCIA-NARRATIVA, SR-PIPELINE-FIXES, ESTABILIZACION-PRE-TRIBUNAL, PASO0-VERIFICADOR-CAPITALIZACION y VALIDADOR-URL-PROPIA. Satisface C8 (≥2) con holgura y no repite solo al predecesor. **Doble corrección del 2026-09-20**: la fila decía **7** cuando las once originales ya tenían **6** dueños nombrables (L-R.3 aplicado a este propio archivo: el conteo se re-mide, no se copia), y las tres lecciones nuevas de la capa tibia **no suman dueño** — `D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12`, no en `TRIBUNAL-ENFORCEMENT-OBS`, que es donde la **reproducen** cuatro fases seguidas. Lo detectó `validate_lesson_capitalization.py` con su checks `C7` (atribución contra el índice), no una lectura humana: es el verificador de forma de este mismo plan funcionando sobre su propio `00-`.

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-A6, L-V4, L-H4 | Son la familia «la cita de línea cadura». Este plan no introduce citas de línea en ACs ni prompts y **no reescribe** las ajenas: `validate_plan_citations.py` ya las gobierna con alcance hacia delante + delta, y su política está recogida como restricción en `04-contrato-ejecucion.md`, no como trabajo nuevo |
| DA-HF3 | Misma política de alcance (hacia delante + delta, reporta sin reescribir). Ya está implementada en el verificador de citas; este plan la **hereda** como diseño de AC16, no la reconstruye |
| L-SR3, L-SR5 | Fuente única de verdad del estado de un servicio y gate bloqueante que no solo loggea: son del dominio de producto (promesas/métricas del pipeline v4). Ninguna fase de este plan toca el pipeline ni sus gates |
| L-VUP-1 | La baseline «13 rojos» que midió 14 por un test orden-dependiente del audit: este plan no ejecuta el audit ni hereda esa selección de tests |
| **D5** (no es ID: medición propia) | `grep -icE "verificador mec"` devolvió **0** sobre el índice, y sí existen verificadores nombrados en el corpus. Un cero de grep **no distingue** «no existe» de «busqué la palabra equivocada» — es la variante léxica de L-PF6. Se descarta el grep como única puerta de pertinencia y se registra como la evidencia que justifica FASE-C (AC15 obliga a publicar la población y el término usado) |

## 4. Cobertura declarada de este documento

- **Qué sí deja evidencia**: **catorce** consultas re-ejecutables (Q9 al abrir FASE-A; Q10 al abrir FASE-B; Q11 tras commitear B; Q12 al abrir FASE-C; **Q13 al abrir FASE-D, que es la que re-mide el workflow, la población de la convención `Lee …` y el índice sobre un árbol extraído con `git archive`**) — al concebir (Q9 el 2026-09-21 al abrir FASE-A; **Q10
  el 2026-09-21 al abrir FASE-B**, que es la que comprueba que la herencia de B no se asumió; **Q11 el
  2026-09-22 tras commitear B**, que desglosa la brecha entre las dos poblaciones de AC6) — al concebir
  eran ocho consultas re-ejecutables con su resultado medido, **catorce** lecciones con ID, dueño y un
  «qué cambia» que nombra un AC concreto (once al concebir + L-V2.1, L-V2.2 y D-V2.1, que trajo la capa
  tibia el 2026-09-20), cinco descartes con motivo y una medición propia (D5) que refuta el atajo obvio.
  **Al cerrar FASE-B se añaden cinco lecciones nuevas propias (L-VCF-6 a L-VCF-10, definidas con su
  medición en `10-analisis-post-implementacion.md`), dos más que escribieron el commit de la fase y su
  barrido (**L-VCF-11**: el denominador refutado al commitear; **L-VCF-12**: el verificador que pisó la
  evidencia de FASE-A por tener su destino hardcodeado), y deudas con dueño y disparador nuevos —
  **S10** (la geometría del `import` del SDK cuando D7 se active), **S11** (la exclusión no declarada del
  denominador) y **S12** (el default de `--report` sobre un registro cerrado; con guarda publicada en el
  README para que FASE-C no la re-pise, **guarda sin efecto desde el 2026-09-23** — ver la fila
  siguiente).**
- **Qué NO verifica el check mecánico**: la **pertinencia**. `validate_lesson_capitalization.py` comprueba forma y trazabilidad (C1–C8: consultas corpus-wide, ≥3 descartes, AC nombrado que existe, dueño publicado por el índice, ≥2 fuentes) y **ninguno de sus checks puede saber si la lección que debía capitalizarse era otra**. Un `[OK]` suyo significa «la forma exigida está». Ese límite declarado es exactamente el hueco que abre este plan.
- [x] **FASE-D cerró el 2026-09-24 con `build_phase_briefing.py` y sus 5 packs** dentro del plan
  (`…/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/briefing/`). Estado medido: **COMPLETO 4 ·
  SECCION-NO-RESUELTA 1 · FUENTE-AUSENTE 0** sobre 34 fuentes declaradas y 23 secciones pedidas
  (23 resueltas). La carga total de las cinco fases **bajó**, y el delta queda **muy por debajo del
  tercio** que el plan esperaba porque **el workflow canónico sigue entrando en los dos lados**: los
  dos totales, la resta y su comprobación los imprimen `FASE-D/carga.json` y `FASE-D/carga-pre-post.md`
  y su lectura métrica vive en `09` §D. **Aquí no se transcribe ninguna de esas cifras y eso es parte
  del hallazgo**: este documento entra en el pack que ese comando mide, así que copiar la carga en él
  la vence en el mismo gesto (**L-VCF-19**).
  Herencia de C aceptada sin reabrirla: la parte mecánica del triaje se exhibe en el pack, y su
  tramo semántico sigue `NO-EJERCITADO`, con **D6 dormida** (contrato E4). No se re-negoció E1–E5.
- [x] **La convención que parsea el generador es minoritaria y eso se midió, no se supuso**: de
  **121** prompts bajo `.opencode/plans/Archives/`, **0** declaran su lectura con la cadena
  `Lee …`; los únicos **5** del repo son los de este plan. Un test contra corpus real por eso
  afirma hoy el **corte** (el pack sale `SIN-DECLARACION` y su check `SIN-FUENTES`, no `OK`) y la
  escritura de la convención en `prompt-fase-template.md` quedó como deuda **S16**, con dueño y
  disparador, porque tocar `.agents/` es AC17/D1 y no compete a esta fase.
- [x] **El plan se auto-trió al cerrar FASE-C (2026-09-24), y el resultado NO se aplicó a sí mismo.**
  `scripts/triage_lesson_relevance.py` corrió sobre este propio `00-` con el **proveedor falso
  determinista** de la selección (el informe publica `coste.emisor = {nombre: falso-pertinencia,
  falso: true, credencial_env: null}`). Conteos del auto-triaje, con su artefacto:
  **propuestas aceptadas para §2: 0 · rechazadas: 0 · pendientes de revisión humana: 5**
  (`informe.json` → `buckets.propuesto`; 16 candidatos más quedaron en `a-revisar-humano` por
  `confidence` debajo del umbral o por rechazo confidente del emisor), y **11 de las 14 filas ancladas
  fueron juzgadas `no-pertinente` por el emisor y ninguna se borró** (`ac10_delta.json` →
  `removed: []`, `filas_cuestionadas_sin_borrar`). **Este §2 sigue teniendo las mismas catorce filas
  que tenía al cerrar FASE-B**, y esa invariancia es AC10, no olvido. Por qué cero aplicadas: una
  propuesta de un falso prueba la mecánica del camino, no la pertinencia (contrato **E3**), y aplicarla
  habría escrito aquí una fila cuya evidencia es sintética — lo que AC15 declara `NO-EJERCITADO`. Si
  alguna se revisa, entra con dueño, «qué cambia» real y la revisión que la avala registrada con quién
  decidió; si se rechaza, **se publica el rechazo con su motivo y la fila no desaparece**.
- [x] **Las cinco propuestas del piloto quedan declaradas PENDIENTES con su dueño (2026-09-25, cierre de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22`).** `L-VCF-10`, `L-VCF-11`, `L-VCF-12`, `L-VCF-13` y
  `L-VCF-14` son las cinco que publica `informe.json` → `revision_humana.propuestas_pendientes`
  (`n_pendientes: 5`, `registros: []`), definidas cada una con su medición en
  `10-analisis-post-implementacion.md`. **Dueño: el operador**, a través de la revisión humana que fija el
  contrato **E3** — no es una fase ni un script: `seccion_dos_editada_por_este_script: false` sigue siendo
  cierto después de esta sesión. **Ninguna se aceptó, se rechazó ni se copió a §2**, que conserva sus
  catorce filas (**AC10**). Lo que cada una necesita para entrar: un «qué cambia» real que nombre un AC de
  este plan, la revisión que la avala registrada con quién decidió, y una evidencia que no sea la de un
  emisor falso mientras **D7** esté inactiva — por eso se declaran pendientes en lugar de cerrarse.
- [x] **El hueco que este archivo declaraba fuera de alcance ya tiene instrumento**: la limitación del
  párrafo anterior («Qué NO verifica el check mecánico: la pertinencia») sigue siendo cierta de
  `validate_lesson_capitalization.py` — su `[OK]` jamás significó «capitalicé bien» —, pero desde el
  2026-09-24 existe la otra mitad: `triage_lesson_relevance.py` pregunta por pertinencia, publica su
  denominador con sus ceros y **propone sin filtrar**. Lo que **no** cierra: el juicio semántico real,
  que espera proveedor (deuda **D7**), y por eso **D6** sigue dormida.
- [x] Este archivo es verificado por `scripts/validate_lesson_capitalization.py` (`[7/7]` del hook versionado en `scripts/git_hooks/pre-commit`) y por `scripts/build_lesson_index.py --check` (`[6/7]` del mismo hook).
- [x] **Limitación del Paso 0 registrada y SUPERADA el 2026-09-20**: la capa tibia (QMind `iah-cli-lecciones`) **no se consultó** en la concepción porque el CLI no estaba disponible en esa sesión; se aplicó el fallback del executor (memoria de proyecto + índice generado) y quedó registrado aquí y en `dependencias-fases.md`. En la auditoría de la concepción del mismo 2026-09-20 el CLI **sí** estuvo disponible y autenticado: se ejecutó Q7 con cuatro consultas y sus resultados se capitalizaron arriba (L-V2.1, L-V2.2, D-V2.1). **El comando con el nombre de notebook no es re-ejecutable**: `--nb iah-cli-lecciones` devuelve `error: Bad request`; el identificador válido es `01a04d98-b7bd-778c-8441-26fdc7e35f45`. Queda como verificación de **D8** re-corrida antes de RELEASE por si el corpus cambió. ⟦**Re-fechada el 2026-09-25, al cerrar FASE-RELEASE**: la re-corrida **no** se hizo. D8 es operación de red y el mandato del cierre la dejó explícitamente fuera (checkpoint C1, `PENDIENTE-AUTORIZACION`). Lo que se declara es que **la premisa «el corpus del notebook cambió desde el 2026-09-20» quedó no comprobada**, que no es lo mismo que «no cambió», y que la capitalización de §2 sigue apoyada en la consulta de aquella auditoría. La limitación del comando con nombre sigue vigente: no es re-ejecutable tal cual⟧.
- [x] **Actualizado al cierre de FASE-A (2026-09-21)** con el balance de §5, la consulta Q9 re-ejecutable y las cinco lecciones nuevas de esa fase.
- [x] **Actualizado al cierre de FASE-B (2026-09-21)** con el balance de §6, la consulta Q10 re-ejecutable, las cinco lecciones nuevas de B (L-VCF-6 a L-VCF-10) y la deuda **S10**. Ocho de las diez lecciones filtradas por su prompt se ejercitaron y las dos restantes quedaron asignadas y declaradas (L-V2.1 y L-V2.2: la primera se volvió a caer, la segunda es de FASE-C). Sigue **sin** cerrarse el plan: faltan C, D y RELEASE, y el write-back de QMind se ejecuta **antes** del `git mv` a `Archives/` en esa última sesión (orden R2.5 / R2.10, con la interfaz del writer re-leída por D10).
- [x] **Actualizado el 2026-09-22, al commitear FASE-B** (`647f436`): la consulta **Q11** re-ejecutable,
  la lección **L-VCF-11** y la deuda **S11**, las tres nacidas del propio commit — que refutó una cifra
  que la fase acababa de publicar (678 → **691** `.py` rastreados) y dejó ver, al desglosar la
  brecha con el escáner, una exclusión no declarada en el denominador. Es A6 golpeando otra vez, ahora
  sobre el instrumento de la fase: **un cero medido sobre una población que nadie definió del todo**.
- [x] **Conciliada el 2026-09-23 (solo lectura, sin nueva instrumentación).** Las dos lecciones que
  escribió el commit de B — **L-VCF-11** y **L-VCF-12** — tenían su deuda asociada (**S11**, **S12**)
  corregida en código **por otro trabajo**: el bloque A de
  `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`, commit **`fdd397f`**, que declaró explícitamente que lo
  suyo era *corrección técnica, no cierre contractual* porque la enmienda correspondía a este plan. **Esa
  enmienda es la que se registra ahora** en `dependencias-fases.md` §Conciliación, con las tres capas
  separadas: cierre original (`647f436`) / corrección (`fdd397f`, ajena) / aceptación (2026-09-23). Las
  lecciones **no caducan**: L-VCF-11 sigue siendo la regla de desglosar una brecha entre dos poblaciones
  archivo por archivo (hoy verificada por medición: 696 escaneados vs 691 rastreados → residuo 0) y
  L-VCF-12 sigue siendo la regla de mirar el default de escritura de un verificador antes de correrlo.
  Lo que sí se retira es su aplicación concreta: la guarda del README sobre `--report` sin destino, que
  S12 dejó sin objeto. Y **ninguna de las dos correcciones toca el rojo contractual**: A1–A4 siguen
  vencidas en `.agents/` (`exit 1` re-medido) porque ese es **D1**, con instrucción literal del operador.
  ⟦**Vencido ese cierre el 2026-09-25, con atribución**: el `exit 1` de A1–A4 describía el árbol antes de
  que el **bloque B** de la orden recibiera su autorización para editar `.agents/`. Re-medido en el cierre de
  FASE-RELEASE con el mismo instrumento y su modo de solo lectura
  (`validate_governance_numbers.py --report`, sin destino): **`status: SIN-HALLAZGOS`, `exit 0`**. El veredicto
  de **D1** no lo da esta línea ni ese número: lo da la **matriz §13** de la fuente única de B, donde aparece
  **CERRADA en su alcance**. Lo que la lección conserva intacta es su regla de procedimiento: **leer** el
  verificador no es **reparar** `.agents/`, y eso fue lo único que hizo este cierre⟧.
- [x] **Actualizado al cierre de FASE-RELEASE (2026-09-25, parte offline).** El plan cerró sus cinco fases:
  release **4.78.0** en la fuente única, cinco cabeceras por su writer, `DOMAIN_PRIMER.md` regenerado con el
  suyo, `[4.78.0]` en `CHANGELOG.md` y registro en `REGISTRY.md` por su **único** escritor. Sobre este
  archivo, lo que el cierre **no** tocó y lo que sí: **no** se aceptó ni se rechazó ninguna de las cinco
  propuestas de revisión humana (L-VCF-10…14 siguen `pendientes`, §2 conserva sus catorce filas — AC10 y
  contrato **E3**), y **no** se capitalizó por cuota. Lo que se re-fechó es la limitación de Q7/D8 (arriba)
  y la lectura de D1. El cierre deja dos defectos de instrumento declarados y sin cura en esta fase: los
  writers de texto que reescriben sin `newline="\n"` (CRLF sobre archivos `i/lf`) y la regla
  `readme_version_header`, que no goberna la fecha legible del `README.md`.
  ⟦**Ese «sin cura en esta fase» se cumplió y luego venció el mismo 2026-09-25**: el cierre no los curó
  (no tenía mandato de código) y quedaron registrados como **S17** y **S18**; una sesión posterior, con
  mandato de código del operador, los curo — tres escrituras con `newline="\n"` (la de `run_status`
  apareció al curar) y la regla de la fecha legible goberna y escribe por su escritor. Estado vigente:
  §S17/§S18 de `dependencias-fases.md`; prueba en
  `tests/test_sync_writers_lf_y_fecha_readme.py`. Ninguna de las dos fue una lección nueva de este
  archivo: no se capitalizó por cuota. Las reglas generales que las produjeron ya estaban escritas —
  mirar el default de escritura de un verificador antes de correrlo (**L-VCF-12**) y arreglar un dato
  en su escritor, no con un tercero que lo reescriba a mano⟧.

## 5. Balance de FASE-A (2026-09-21): qué se aplicó de verdad, lección por lección

Diez lecciones de §2 estaban filtradas como pertinentes a FASE-A en su prompt. Contrastadas una a una
contra lo que la fase produjo (ninguna quedó «citada sin aplicar», y ninguna se borró):

| ID | Estado al cerrar A | Evidencia o motivo |
|---|---|---|
| L-R.1 | **aplicada** | La regla vivía solo en el workflow; ahora vive en `scripts/validate_governance_numbers.py` con su prueba sobre el árbol real |
| L-NC10 | **aplicada** | Población descubierta por escaneo (24 instancias), no hardcodeada en las cuatro medidas |
| L-R.3 | **aplicada** | `coverage_basis` obligatoria; el favorable sin denominador está cortado por guard |
| L-PF6 | **aplicada** | Cuatro caminos de `LECTOR-FALLIDO` con motivo propio; ninguno devuelve «sin hallazgos» |
| L-PF10 | **aplicada** | Tres archivos de estado, uno por estado; documento no vacío con 0 instancias = fallo de lectura |
| L-T4A.5 | **aplicada, y descubrió un defecto propio** | El primer mutation check apagaba el guard de A1 y nombraba a A4: anclar en un id posicional no prueba nada → `assertion_key` invariante (L-VCF-1) |
| L-VUP-5 | **aplicada** | El verde de la primera corrida se declaró sospechoso **y lo era**: la regla de población se rectificó dos veces antes de reproducir A1–A4 |
| L-D3 | **aplicada** | Conteos como delta con resta comprobada; la métrica que sí se movió (+23 tests) publicada aparte |
| L-V2.3 | **aplicada con costo propio** | El barrido de `tests/` mostró que la fase añadió pins del 11 (L-VCF-5), declarados con dueño |
| L-HF1 | **aplicada** | Familias no cubiertas medidas y publicadas; exclusión histórica con su conteo y su frase de amparo |

De las tres lecciones del §2 que el prompt de FASE-A no filtraba: **L-V2.1 sí se ejercitó** (es la que
gobierna el anclaje del mutante, y fue la que cayó — L-VCF-1); **D-V2.1 se reprodujo** (el instrumento de
presupuesto no corre: `find . -name "*.jsonl"` = 0 en el workspace, métrica retirada y unidad contable
declarada en `evidence/…/FASE-A/ac17-y-presupuesto.md`); **L-V2.2** corresponde a FASE-C y sigue
pendiente de ejercitarse.

Cinco lecciones nuevas salen de esta fase (**L-VCF-1** a **L-VCF-5**), definidas con su medición en
`10-analisis-post-implementacion.md`; dos afectan a las fases que siguen: el disparador de D1 era
circular (L-VCF-4, ya re-escrito en `dependencias-fases.md`) y **la salida de un verificador también es
contrato** (L-VCF-3), cosa que FASE-B, C y D pueden repetir si imprimen estados con acentos.


---


## 6. Balance de FASE-B (2026-09-21): qué se aplicó de verdad, lección por lección

Siete lecciones de §2 venían filtradas por el prompt de FASE-B, más la herencia explícita de A. Ninguna
se citó «de adorno»: cada fila dice contra qué artefacto se confrontó.

| ID | Estado al cerrar B | Evidencia o motivo |
|---|---|---|
| L-PF6 | **aplicada, y con costo propio** | La prohibición del default es el eje del módulo (5 `motivo_clase` sin colapsar + mutante del proveedor por defecto). Costo: la primera regla de aislamiento leía «todo `import_module`» como contrabando y producía **16 hallazgos ajenos** → L-VCF-7 |
| L-PF10 | **aplicada** | `respuesta-vacia:list` con causa propia; `usage=None` ≠ consumo cero; `noul.confidence = None` **con** `confidence_motivo`, nunca `0.0` |
| L-R.3 | **aplicada** | El `0` de AC6 con dos poblaciones (678 / 692), 4.379 nodos vistos, 21 menciones aparte y exclusiones con su conteo; el `1` de AC9 medido por sha256 |
| L-R.4 | **aplicada** | La comparación de proveedores declarada fuera de alcance con su porqué (D7), y S10 registrada con dueño y disparador en vez de decideda en silencio |
| L-D3 | **aplicada** | Todo conteo gobernado como delta con resta (quick 0, completo 0, hook 0, `.agents/` 0/0, AC6 0); los +48 de tests publicados aparte |
| L-V2.3 | **aplicada** | Contract test de forma sin literales del proveedor; pin declarado y probado no-usado por AST; **0** pins nuevos del 11 o del 7 añadidos por B |
| L-VUP-5 | **aplicada y confirmada** | La primera corrida dio **30 fallos** y el primer mutante de forma no aislaba ningún guard (L-VCF-6). El rojo de AC8 (`exit 1`) quedó capturado en `contract.txt` |
| L-T4A.5 / L-V2.1 | **aplicadas** | Nueve mutantes sobre símbolos reales, cada uno con verde y rojo, y un test que exige que dos mutantes no compartan símbolo. L-V2.1 volvió a caer: la unidad de mutación de una **lista** de guards es su entrada, no la lista (L-VCF-6) |
| L-HF1 | **aplicada** | Cuatro límites del escáner medidos y publicados (cargas no resueltas 14, dependencias declaradas no miradas, menciones aparte, exclusiones con conteo); `.agents/` intacto y verificado |
| L-V2.2 | **no ejercitada todavía** | Es de FASE-C (el suelo determinista del índice). Queda pendiente de ejercitarse allí, no se borra |

De las dos lecciones del §2 que el prompt de FASE-B no filtraba: **L-V2.1 sí volvió a caer** (es la que
rige el anclaje del mutante, y el primer mutante de forma no aislaba nada → L-VCF-6) y **D-V2.1 se
reprodujo otra vez** (`find . -name "*.jsonl"` = 0: el instrumento de presupuesto sigue sin correr,
métrica retirada y unidad contable declarada en `evidence/…/FASE-B/baseline-pre-post.md`).


---


## 7. Balance de FASE-D (2026-09-24): qué se aplicó de verdad, lección por lección

Ocho lecciones venían filtradas por el prompt de la fase. Ninguna se citó de adorno: cada fila dice
contra qué artefacto se confrontó, y la que no se ejercitó queda escrita como tal.

| ID | Estado al cerrar D | Evidencia o motivo |
|---|---|---|
| L-D3 | **aplicada** | Delta con par `stat -c %s` y resta entre cargas totales; cinco identidades comprobadas por `instrumentos/comprobar_resta_carga.py` (`exit 0`) y un test que obliga a publicar un delta **negativo** |
| L-PF10 | **aplicada, y amplió el contrato** | Al trío de AC22 se sumó `SIN-DECLARACION` y el check imprime `SIN-FUENTES` en lugar de `OK`; sin esa cuarta salida, los 121 prompts archivados habrían dado 121 verdes vacíos |
| L-PF6 | **aplicada** | `exit 2` con tres rutas intentadas para un plan inexistente; fuente ausente = pack **no emitido**; meta sin sha = `FUENTE-ILEGIBLE`, causa distinta de `AUSENTE` y de `SHA-DISTINTO` |
| L-NC10 | **aplicada** | Cero configuración a mano: `parsear_lista_lectura(prompt)` se confronta contra las fuentes del pack emitido, fase por fase |
| L-V2.3 | **aplicada con costo propio** | AC21 se prueba escribiendo la fuente **en disco**; y el anclaje de AC23 hubo que re-hacerlo: «rutas intentadas» y «sección pedida» ya vivían en los documentos copiados (ver L-VCF-16) |
| L-R.3 | **aplicada** | `coverage_basis` con 5 packs por estado, 34 fuentes, 23 secciones pedidas/resueltas, cinco familias no cubiertas y el denominador de la convención (0 de 121) |
| L-HF1 | **aplicada y produjo una regla nueva** | `no_incluye[]` no vacío por test; y lo que vive fuera de `.opencode/` se declara lectura aparte: copiarlo dentro reabrió `[8/11] validate_opencode_refs.py` (medido: 2 referencias rotas por el pack, `docs/CONTRIBUTING.md`) |
| L-T4A.5 | **aplicada** | Verde y rojo del guard real en `FASE-D/mutation/`, con test de que el mutante no cambia el estado, solo la declaración. El par de tamaños **no** se copia en esta fila: vive en `mutation/resumen.txt` y este documento está dentro del pack medido (**L-VCF-19**) |

De las lecciones del §2 que el prompt **no** filtraba: **L-V2.1 volvió a caer** (el primer anclaje
del mutante miraba una frase que existía en el corpus copiado: un rojo que no observaba la rama que
decía observar → **L-VCF-16**) y **D-V2.1 se reprodujo por octava vez** (`find . -name "*.jsonl"` =
0 dentro del workspace: el instrumento de presupuesto sigue fuera de servicio; el corte de esta fase
fue «hasta listo para revisión»). **Y en D el auto-reporte tampoco se publicó**: la sesión pasó por una
compactación de contexto a mitad de fase, la cuenta de `tool_use` propios ya no era reconstruible, y
publicar un número de memoria habría sido el defecto que **L-VCF-18** capitaliza en esta misma fase. La
métrica se retiró y se sustituyó por **unidad contable en disco** con su comando —rutas propias,
líneas de instrumento y de selección, archivos de evidencia y corridas listadas—, declarada
**no comparable** con las corridas que sí usaron el instrumento. Los números están en
`baseline-pre-post.md` §4 y **no se re-transcriben aquí**: esta fila es fuente de uno de los packs que
la fase mide, y copiar un conteo de la propia evidencia lo vuelve a mover (**L-VCF-19**).)

Dos cosas que D **no** hizo y se declaran: no rebanó el workflow (deuda **D3**, dueño «plan propio,
posterior»), y no aceptó candidatos de pertinencia ni tocó el §2 del `00-` — heredó de C su parte
mecánica medida y su `NO-EJERCITADO`, y **D6 sigue dormida** con su causa escrita
(`dependencias-fases.md` §Deuda).

**Y una cosa que D midió sobre su propio cierre**: la primera corrida de la regresión
`tests/quality_gates` salió **roja (14 failed, 26 errors, `SueloNoLeible: VENCIDO`)** por el índice
vencido **por los packs y los `.md` de cierre que la propia fase escribió** (**L-VCF-17**, y en la
selección de C, no en la de D), y la tercera volvió a salir roja porque **esta sesión editó corpus
mientras corría la selección**. Las dos se conservan con su cifra y su atribución en
`evidence/…/FASE-D/regression_calidad.txt`, que también guarda la **cuarta** corrida —la de referencia
del cierre, verde, sobre el árbol ya asentado, con el par de índice regenerado después del último `.md`
y su `--check` en verde—. Su recuento **no se copia a este `.md`**: sería la quinta vez que una cifra
transcrita al corpus queda vencida por el propio acto de transcribirla (**L-VCF-19**).
