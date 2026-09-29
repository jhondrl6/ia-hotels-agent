# 00-resumen — sesión 2 de código: curas en `scripts/` post-re-verificación VCF+JEV (2026-09-28)

Sesión **escritora**, alcance cerrado a C1–C7 de la orden. **Nada commiteado**: los cinco cortes terminan en
**espera de autorización**.

⟦**Vencido el 2026-09-28 por la propia tanda**: el operador autorizó el commit y el push. Commit `c8b7198`
(«fix(scripts): curas C1-C7 de la sesion 2 sobre la re-verificacion VCF+JEV»), verificado en su propio árbol con
los dos verificadores de clon autogestionado (packs **5/5** reproducidos por el escritor, índice fresco con 340
IDs y 588 rutas, ambos exit 0) y **empujado con el rango `84c1aca..c8b7198`**. El **L3 se corrió antes del push y
no encontró problemas de seguridad**. La paridad no se fija aquí como cifra: la lee cualquiera con
`git ls-remote origin refs/heads/master` contra `git rev-parse HEAD`.⟧

- **REV_INICIO:** `84c1aca`, que al medir coincide con `origin/master` (`git log origin/master..HEAD` vacío).
  Todos los controles de escritor se anclan a esta revisión o a una publicada anterior, nunca a HEAD.
- **Árbol de partida:** `git status --porcelain -uno` = **12**, exactamente la lista de la orden (6 anotaciones
  de la sesión 1 + 5 packs + `plan_citations_baseline.json`). Crudo `00-`.
- **Artefactos de la sesión 1:** los tres pedidos existen en disco y **0** rutas de ese directorio están en
  `HEAD` → estado **(b)** de la precondición 2 (sin commit, no rastreado).
  ⟦**Vencido el 2026-09-28 por la propia tanda**: ese directorio viaja **entero** en `c8b7198` — las **70** rutas
  de `RE-VERIFICACION-VCF-JEV-2026-09-28/`— porque los sellos de la sesión 1, y después los packs regenerados,
  citan sus crudos; sin ellas el árbol versionado habría quedado con referencias rotas. La medida de apertura no
  se mueve: sobre el `HEAD` de entonces (`84c1aca`) eran **0** rutas rastreadas.⟧
- **Filas dueñas leídas por encabezado** (`### S17`, `### S19`, `### S21`, `### S32`, `## Cierre formal`): las
  cinco anclas de línea que daba la orden (368 / 530 / 735 / 976 / 1032) **casaron tal cual**.

## Barrido de pins: PRE y POST con los dos instrumentos

| Pin | PRE publicado | PRE medido | POST medido | Nota |
|---|---|---|---|---|
| D1 en `scripts/` (patrón ampliado) | 3 | **3** (`:819`, `:830`, `:839`) | **0** (exit 1) | curado por C1 |
| D1 en `tests/` | 0 | **0** (exit 1) | **0** | — |
| Etiquetas `[/1x]` en tests | 13 | **13** con el comando literal; **17** con `grep -rn --include=*.py` | **13** / **17** | la diferencia de 4 son líneas en `tests/*.py` **raíz**: el pathspec `tests/**/*.py` de git no baja un solo nivel. **No** es trabajo sin versionar, como decía mi primera nota |
| `lectura aparte` en `tests/` | 3 | **3** | **3** | intacto: C2 no re-escribió esas aserciones |

Un pin quedó vencido por el propio cambio y se actualizó con nota datada, no en silencio: las posiciones de
los tres `newline="\n"` del guion de refs pasaron de `:209/:212/:252` a `:210/:213/:253` al entrar el
comentario de C4. **El criterio es el conteo (3), no la posición.**

## Estado por cambio: verde, rojo del mutante y crudo

| Cambio | Verde medido | Rojo medido | Crudos |
|---|---|---|---|
| **C1** (D-A) | grep `scripts/` 3→**0**; `--report` **exit 0** con `families_not_covered` en **4** y `poblacion` idéntica PRE/POST; test nuevo afirma las tres cadenas **por contenido, con la familia como clave** | reintroducir `D1 decide` → **1 failed, 4 passed**; restaurado, `sha256` idéntico (`13772abb…`) | `01-`…`05c-` |
| **C4** (§S17 sub-punto) | espejo con ruta promovible: el `--fix` escribe **sin barra** y la segunda corrida no opera; batería S17 **14 passed** (era 10); baseline de refs **1 entrada, 0 movidas por la forma** | control `5817edd` sobre el mismo espejo **sí** promueve `/.opencode/…`; mutante **R2.8** (quitar `newline` de las dos escrituras) → caen **exactamente** las dos de refs: `2 failed, 12 passed` | `06-`…`10-` |
| **C3** (§S21 salida b) | cabecera `MODO:` en los dos modos; quick **13/13** con `[GUARDA]`; `--report` **exit 0** después; **17** etiquetas igual que en `REV_INICIO` (delta 0, la cabecera no es un emisor) | (i) un denominador foráneo en una etiqueta corta **en el modo completo** (antes solo cortaba en el rápido); (ii) **apagando la comparación nueva** el mismo escenario vuelve a verde falso; la batería `test_run_all_validations_denominador_por_modo.py` (5) lo afirma | `11-`…`16-` |
| **C2** (§S32 salida a) | `--check` **exit 0** con «proyeccion del workflow conforme» en los cinco packs; workflow **fuera** de `sources[]` (AC17/D3); batería nueva **6 passed**; selección `phase_briefing` **57 passed** | workflow **+43 bytes** sin regenerar → **exit 1** nombrando `publicados 112986 bytes / 28246 tokens; en árbol 113049 / 28262`; restaurado por `sha256` (idéntico) → **exit 0**; y con `proyecciones_de_lectura_aparte` apagado el mismo caso **verdece** | `17-`…`20-` |
| **C6** (§S19(d)) | **salida (c)**, con sello fechado en la fila: NORMALIZAR tiene **4** patrones y ninguno cubre `generado_por_sha`; el sha del escritor da **4 valores distintos sobre 5 mediciones**; el guion que necesita el quinto patrón (`verify_packs_in_committed_tree.py`) no está entre los cinco autorizados. **No lo cubre C2** | no hay cura que mutar; queda abierta con dueño y disparador intactos | `21-` |
| **C7** (D-H) | `newline="\n"` en `escribir_baseline`; sobre **ruta externa** emite **CR=0, LF=87**; guard de destino: el baseline versionado no se movió (sha igual) | escritor de `REV_INICIO` (`84c1aca`) sobre la misma copia: **CR=87, LF=87, CRLF=87**; idénticos salvo CR y `created_at` (afirmado por bytes y por dict) | `22-`, `23-` |
| **C5** (D-C) | PRE **213** (deriva **0** contra la orden), reparto **178 md + 34 json + 1 txt**; **213/213** con `POST == git cat-file blob HEAD:<ruta>` (toda la población, no la muestra de tres); POST **0** con el mismo comando; `git status -uno` **20** líneas todas declaradas | ruta fuera de la población → **exit 4** y el fixture quedó intacto (CR=2 después) | `24-`…`29-` |

## Pipeline global, en orden estricto

1. Sellos fechados en `dependencias-fases.md` — **cinco** sellos del 2026-09-28 (S32/C2, S21/C3, S17/C4,
   S17/C7+C5, S19/C6), **solo** esas filas; numstat de la fuente **152/1**.
2. `validate_opencode_refs.py --fix` → **0 operaciones**, `[PASS]` **exit 0**; re-check **exit 0**; escritores
   LF `grep -o -F` → **3** coincidencias.
3. `validate_plan_citations.py --update-baseline` → **79 archivos, 743 citas**, `0 nuevas / 0 crecimientos`;
   único cambio del JSON: `created_at` (numstat **1/1**); quedó en **CR=0** y la población D-C **no se movió**
   (re-contada: **0**). Sin la cura de C7 esta misma corrida la volvía a mover: eso es lo que cerró.
4. `build_phase_briefing.py --check` → **5 packs vencidos** (verificado uno por uno: los cinco toman
   `dependencias-fases.md` en `sources[]`) → regenerados los cinco y solo esos → `COMPLETO 5 ·
   SECCION-NO-RESUELTA 0 · FUENTE-AUSENTE 0 · fuentes 37`.
5. `build_lesson_index.py` **después** de los packs → `340 IDs definidos + 54 sin definición`.
6. `build_phase_briefing.py --check` → **exit 0**.
7. `run_all_validations.py --quick` → **13/13** con `[GUARDA]` verde, **exit 0**.
8. `git diff --check` → **exit 0**; `git status --porcelain -uno` → **20** líneas, cada una con su población.

## Verificación final (después de normalizar los crudos propios a LF)

| Instrumento | Resultado |
|---|---|
| `pytest` sobre las baterías autorizadas (las cuatro de la orden + los dos archivos de gobernanza nombrados por el barrido + la selección `phase_briefing`) | **107 passed**, exit 0 |
| `run_all_validations.py --quick` | **13/13**, `[GUARDA]` verde, exit **0** |
| `validate_governance_numbers.py --report` | exit **0** |
| `build_phase_briefing.py --check` | exit **0** |
| `build_lesson_index.py --check` | exit **0** |
| `validate_opencode_refs.py`, `validate_plan_citations.py` (lectura) | exit **0**, 743 citas, 0 crecimientos |
| `git diff --check` | exit **0** |
| `git status --porcelain -uno` / `git diff --cached` | **20** líneas / **0** (nada stapeado) |
| Residuo `.opencode` | **0** |

## Reporte de cifras

- **Tests, con los dos instrumentos:** canónico sobre el árbol de trabajo **4611**; árbol versionado
  `git grep -c -E "^\s*def test_" HEAD -- tests` **4590**. Deriva **+21**, desglosada entera:
  `tests/test_sync_writers_lf_y_fecha_readme.py` **+7** (10→17: 4 de C4 y 3 de C7),
  `tests/test_run_all_validations_denominador_por_modo.py` **+5** (C3, archivo nuevo),
  `tests/quality_gates/governance_numbers/test_governance_numbers_estados_sin_puntero_d1.py` **+3** (C1),
  `tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py` **+6** (C2).
  En la tabla de AGENTS.md cae en **dos** filas: `root test files` 961→**973** y `quality_gates` 861→**870**.
- **La cabecera de AGENTS.md no se tocó** (prohibido en esta orden; es instrucción aparte). Su cifra publicada
  **4.590** sigue casando con HEAD y queda **21 por debajo** del árbol de trabajo hasta que se autorice.
- **D-C:** **213 → 0** con identidad contra el blob en las 213 rutas. **D-H:** el baseline del paso 3 queda en
  **LF puro** (antes la misma corrida lo pasaba a CRLF y movía D-C).
- **Gobernanza:** `poblacion` intacta (`instancias_totales` 19, `clase_viva_correcta` 11,
  `clase_historica_congelada` 8), cuatro familias declaradas, `--report` exit 0.
- **Estado git:** HEAD **`84c1aca`**, `git diff --cached` **0**, 20 líneas versionadas modificadas y **131**
  rutas sin versionar (la evidencia de esta sesión y la de la sesión 1).

## Los cinco cortes

| Corte | Estado |
|---|---|
| Implementación terminada | **SÍ** — C1, C2, C3, C4, C5, C7 en el código; C6 cerrado como **(c)** con su justificación escrita en la fila |
| Verificación terminada | **SÍ** — la tabla de arriba, con siete mutantes medidos y restauración verificada por `sha256` |
| Cierre documental | **SÍ** — este `00-resumen`, un crudo por criterio y los cinco sellos fechados |
| Listo para revisión | **SÍ** |
| Espera de autorización | **SÍ** — estado operativo final. El `git commit` **no** es condición de ninguno de los cinco: es acción posterior y separada, y requiere autorización explícita |

## No ejecutado, declarado y no silenciado

- **Suite completa de pytest: NO corrida** (prohibición de la orden). Solo se corrieron los archivos nombrados
  por el barrido del Paso 0 y los cuatro nuevos: **107 passed**. Regresión fuera de ese conjunto: **no medida**.
- **Modo completo del runner: NO corrido** — invoca la suite. Su cabecera y su guarda se imprimieron por la vía
  offline (`_print_summary` con resultados sintéticos), declarado en el crudo `15-`.
- **AGENTS.md y `.cursorrules`: NO editados. DOMAIN_PRIMER: NO regenerado.**
  `scripts/log_phase_completion.py`: **NO tocado** (D-F5 es deuda con dueño, no acción de esta orden).
  ⟦**Vencido en su primer miembro el 2026-09-29**: el operador dio la instrucción explícita de alinear la
  cabecera de cifras, y `AGENTS.md` pasó de **4,590** a **4,611** con su ronda fechada, la atribución
  archivo por archivo y las dos filas de la tabla (`root test files` 961 → **973**, `quality_gates` 861 →
  **870**). Medido con el instrumento de la tanda (`m-cierre-cifra-agentes.py`): 22 filas, suma **4,611**, y
  cabecera = disco = árbol versionado (`EXIT=0`, `TODO_CASA`). Quedó en `03d9ef5`. `.cursorrules` y
  `DOMAIN_PRIMER` siguen sin tocar ⟧
- **Decisiones D-B, D-D, D-E y el dueño de S14: NO tomadas.** Se reimprimen al cierre con su base medida.
  ⟦**D-E tomada en 2026-09-29, en su miembro de la lección** (la subida de la lección §11, abajo). El otro
  miembro de la fila —la re-ingesta de los **2 snapshots vencidos**— sigue sin instrucción y ya tiene su
  crudeza medida en el crudo `40-`. **D-B, D-D y el dueño de S14 siguen sin tomar** ⟧
- **Subida de la lección §11 a QMind: NO hecha.** ⟦**Vencido el 2026-09-29 por instrucción explícita del
  operador**: se subió con **título nuevo** por CLI (el `--upload` del escritor responde `[SKIP]` por título y
  habría dejado la versión vieja como verdad publicada). Fuente `01a0ef0e-aa1c-7e5d-8486-51d40b8b4f07` en el
  notebook `01a04d98-…`, que pasó de **54** a **55** fuentes, y **verificada por descarga + sha256** y no por
  título: `d968d497…e12b1` idéntico en disco y en lo descargado, 2.677 bytes en ambos lados.
  `validate_qmind_writeback.py --strict` sigue en `[PASS] 13/13` — el título nuevo no lleva el stem
  `10-analisis`, así que no se confunde con las fuentes que ese verificador cuenta. Crudos `39-` y `40-`.⟧
  Y se declara un hecho **ajeno a esta sesión**: durante el
  trabajo llegó a este agente una notificación de tarea en segundo plano diciendo que un
  `qmind source upload … --file …/43-leccion-paso-0-2026-09-28.md` había terminado con exit 0. **Este agente no
  emitió ese comando** (la orden prohíbe la subida y la deja como decisión D-E del operador). No se repitió, no
  se deshizo y no se verificó el estado publicado del notebook: sería una escritura compartida fuera del
  alcance. Queda señalado para que el operador decida.
  ⟦**Resuelto con medición el 2026-09-29, sin deshacer nada**: antes de subir se leyó el estado del notebook —
  `Total: 54` y **0** títulos que contuvieran `lecc` (buscado también con la `cc` porque el acento rompe el
  grep). O sea que esa notificación **no publicó la lección**: no había nada que retirar, y el conteo quedó en
  55 con la fuente de hoy. Lo que la notificación hizo sigue siendo ajeno a esta sesión y no se reabre — no se
  emitió ni se repitió ningún comando por ella ⟧
- **Baterías pytest de los verificadores de gobernanza de planes: NO corridas** (82 funciones en 6 archivos
  raíz: verify_packs 7, verify_index 9, lesson_index_s15 4, lesson_capitalization 30, validate_wiring 18,
  registry_fecha 14). Los verificadores mismos SÍ corrieron (quick `[8/13]`–`[13/13]` + directos); lo no
  corrido son los tests que prueban a los verificadores. **Decisión del operador (2026-09-28, opción b):**
  se difieren a la sesión posterior de re-veredicto VCF/JEV con Paso 0 obligatorio, que es su lugar natural.

## Instrumentos cazados mientras se medía (ninguno es un rojo del árbol)

- **`subprocess(shell=True)` bajo Windows es cmd.exe**, y cmd.exe no toma `'` como comilla: el patrón
  `'^\s*def test_'` llegó con comillas literales y devolvió **0 funciones** en archivos que sí las tienen
  (crudo `35-` en su primera corrida). Corregido pasando toda línea por `bash -c` y re-medido.
- **`git ls-files --eol -z`** parte la cabecera `i/lf  w/crlf  attr/` como **un** campo con espacios: comparar
  el primer token de `split("\t")` contra `i/lf` devolvía **0 rutas** sobre una población de 213.
- Una ruta con escapes octales (`Regresión.md`) no resuelve en disco tal como la imprime `ls-files` con
  `core.quotePath` por defecto: **OSError 22**. Con `-z` y `quotePath=false` el conteo sigue dando **213**.
- **Heredoc con `python -` dentro de un bloque redirigido** se comió el stdin: una vez reventó con
  `OSError [WinError 6] Controlador no válido` y otra dejó un `EXIT=0` con salida vacía. Toda la tanda se escribió a archivo.
- Mutar `newline="\n"` por heredoc case **0 ocurrencias** y **no** mutateó el archivo: se verificó `sha256`
  idéntico y la mutación se hizo con edición directa, contando después con `grep -o -F` (la nota de la sexta
  instancia de §S17).
- Contar una **clave de JSON** por substring sobre el texto del pack dio **SI falso** en los cinco packs: la
  prosa de §S19 viaja al pack y menciona `generado_por_sha` como texto. Re-leída la clave dentro de
  `BRIEFING-META`, **no** está publicada (crudo `21-`).
- La primera versión del crudo `09-` publicaba `forma_minoritaria_con_barra=False` **en los dos brazos** y una
  idempotencia comparada consigo misma (tautología). Corregido: el patrón pide backtick+barra — el control da
  `True` — y la idempotencia compara los bytes **entre** las dos corridas.
- El crudo `15-` salió primero con **0 etiquetas** por usar `PAR_RE.match` sobre la salida de `grep -oE`, que
  trae el prefijo `print("[` delante: `.search`, no `.match`. Y su versión intermedia llevaba un `\\.opencode`
  con doble escape que pedía un backslash literal.
- **Cache de stat, no contenido:** al escribir las 213 rutas, `git status --porcelain -uno` saltó a **231**
  mientras `git diff --name-only` daba **18** y el `numstat` de esas rutas estaba **vacío**. La vía «segura» de
  `update-index --refresh` rechaza el round-trip (`needs update`); `--really-refresh` **solo sobre las rutas del
  informe del escritor** devolvió la población a **18/20** sin stapear nada (`git diff --cached` = 0). Los cinco
  scripts quedaron con numstat chico (`9/4`, `3/0`, `3/2`, `44/21`, `63/4`): la normalización no se leyó como
  reescritura completa.
- Dos scripts siguen en `w/crlf` sobre disco (`validate_governance_numbers.py`, `validate_plan_citations.py`),
  **uniformes** (CR = número de líneas, sin mezcla) y con estado **preexistente** medido en el Paso 0. Su
  población no es la de C5, que es `.opencode`; git los guarda en LF y el diff es de contenido. Se declara, no
  se amplía la población de la orden.

## Sellos y filas: cómo queda el libro

| Fila | Estado tras esta tanda |
|---|---|
| §S32 | **CERRADA por ejecución** en el hueco del instrumento (salida a), con el límite de alcance declarado |
| §S21 | **CERRADA por ejecución** en la salida (b), y la [GUARDA] corta también fuera del rápido |
| §S17 | CERRADA en finales de línea (cinco puertas) **y ahora también** en su sub-punto de forma promovida: **sin partes abiertas** |
| §S19 | CERRADA en su parte gobernable; **(d) sigue ABIERTA** por la salida (c), con coste re-medido hoy |
| D-C | residuo **0**; la deuda se cierra por el camino de la casa: normalización **por escritor**, con identidad contra el blob |
| D-H | **curada** — séptima puerta de la familia S17, con su batería en la batería de la familia |
| D-A | **curada** en el código; el expediente de la sesión 1 queda como su fuente de hallazgo |

## Inventario

`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/` — **60** entradas contadas
con `ls -1` sobre el directorio (no heredadas de la corrida del cierre): **44** crudos `.txt` (numerados del
`00-` al `38-`, con sus sufijos `b` y la lista de rutas `_c5_rutas_poblacion.txt`), **4** informes `.json` (los
dos `--report` de C1 y los dos informes del escritor de C5), **10** instrumentos `m-*.py`, este `00-resumen.md`
y **1** fixture (`fixture-fuera-de-poblacion.md`, el del mutante de C5).

Pureza de finales de línea re-medida al cerrar: **0** archivos con bytes `0x0d`. Hubo que dar un segundo pase:
el crudo `38-` se escribió dentro de un bloque de shell **después** del pase normalizador y traía 3 CR; se
normalizó y se volvió a contar. La primera versión de este párrafo decía **59** entradas, **38** crudos y **57**
archivos — números de la corrida anterior a escribir este resumen. Se publica el re-conteo: es la regla de la
casa («una cifra publicada caduca; el comando no»).
