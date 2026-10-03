# Sello de publicacion de la tanda PASO-2-3-4-WIRING — medido 2026-09-30

Cierra lo que `04-reinvestigacion-alerta-wiring-2026-09-30.md` declaro **independiente** de la eleccion
de alcance (secciones 4 y 5), la letra de gobernanza que ese mismo parte dejo abierta y el pendiente que
la tanda del 09-30 heredo de la cura D-F5:

| Abierto por | Que quedaba | Donde cierra |
|---|---|---|
| `04-` §4 | el verificador sale EXIT 0 con su clausula de produccion rota | letra 1 — `5145173` |
| `04-` §5 | `.opencode/wiring_report.json` versionado, sin `--check` y sin nadie que lo contra-verifique | letra 2 — `fbfdc57` |
| `06-` punto 1 | `AGENTS.md` publicaba 4.651 contra 4.663 versionados | letra 3 — `d5b4059` |
| `CURAS-SCRIPTS-Y-CONTEXT-2026-09-30/00-resumen.md` fila 8 y `REINGESTA-CONTEXT-JEV-2026-09-29/33-registro-unificado-de-pendientes-2026-09-29.md` fila 4 | `--fecha` obligatoria (D-F5) dejo vencidas las lineas de uso del escritor de fases | letra 4 — `6d32abc` |

La orden fue una sola pegada con cuatro letras y un orden explícito. No se re-evaluo la prescripcion: se
executo, y este documento registra que cada accion tuvo su letra y cada cifra su comando.

## Lo que viajo, en cinco commits

| Commit | Contenido | Rutas | +/- | Hook |
|---|---|---|---|---|
| `5145173` | fix(scripts): la clausula de produccion del wiring se codifica en el EXIT (paso 2) | 2 | 457+/21- | 7/7 |
| `fbfdc57` | feat(scripts): el derivado versionado del wiring se contra-verifica con `--check` (paso 3) | 4 | 849+/97- | 7/7 |
| `d5b4059` | docs(AGENTS): la cifra de Cobertura por Modulo sube a 4.682 | 1 | 19+/2- | 7/7 |
| `6d32abc` | docs(workflow): las lineas de uso del escritor llevan `--fecha` y `--nota` | 7 | 111+/76- | 7/7 |
| `d37928c` | test(wiring): se retiran tres lineas muertas que esta tanda introdujo | 2 | 0+/4- | 7/7 |

Orden con motivo: el codigo de las letras 1 y 2 viajo **antes** que las cifras que publica, y el derivado
(`wiring_report.json`) viajo con el emisor que lo produce, no despues. El quinto commit es desviacion
declarada del mandato «commit y push solo por letra»: su contenido es unicamente codigo de esta sesion
que no hacia nada (ver «Defectos propios»).

## Letra 1 — el criterio, en el EXIT

Medido **antes** de tocar nada (`temp/p2-pre-wiring.txt`): el arbol ya tenia la cura de alcance del paso 1,
asi que `--quiet` salia 0 **por contenido** — que es el defecto, no su prueba: el codigo no afirmaba nada.
La bateria nueva contra el script **sin curar** dio `5 failed, 3 passed` (`temp/p2-01-rojo-antes.txt`);
contra el curado, `8 passed` (`temp/p2-03-verde-cura.txt`).

El criterio, definido antes que en el codigo y publicado en el docstring del script:

- **Rojo**: un `RECEPTOR_NO_RESUELTO` **fuera** de `tests/` (alla es donde una senal se esconde) y
  `gobernadas_resueltas == 0` (la otra mitad del mismo diente: sin un caller resuelto, «cero huecos» no
  afirma nada).
- **Registro, no rojo**: `TEST_EXENTO_DE_SENAL` y el `RECEPTOR_NO_RESUELTO` **bajo** `tests/`. Los dos
  siguen publicados en `poblacion` y contados en `cobertura`.
- El contrato **0/1/2 no se mueve**: lo que cambia es **que** entra en «hallazgos». Los del criterio no son
  amparables por `EXCEPCIONES`: una excepcion tipada cubre una omision concreta, no apaga la clausula que
  mide si el verificador todavia esta mirando.

Esos tres verdes que sobreviven al rojo son la mitad negativa del criterio (registro, no rojo) y el
contrato de codigos: existen para que la cura no se pase de lista cerrando los ojos.

Dientes y control: el mutante tiene ancla **unica** sobre la unica llamada del criterio
(`abiertas.extend(_hallazgos_del_criterio(cobertura, datos["poblacion"]))`), se pre-chequea con
`ast.parse` y **se ejecuta**: apagado, el CLI vuelve al 0 falso sobre el mismo arbol. El control negativo
lee `abd181c` con `git show` y lo ejecuta; la premissa se corta en su fuente (esa revision **si** consulta
la declaracion de Git y **no** conoce los dos tipos nuevos), y sobre el arbol sintetico sale **0** con
`receptores no resueltos 1` impreso.

## Letra 2 — `--check` sobre el derivado versionado

El artefacto que encontre publicado (`temp/p3-02-check-con-derivado-vencido.txt`): `schema_version` **1.0**,
`git_sha` **d7ff932** (2026-09-20), 611 archivos, 169 llamadas, 70 gobernadas resueltas y la clave
`excluidos_por_declaracion_git` **ausente**. La primera corrida de `--check` lo corto con doce divergencias
**nombradas con su ruta punteada** (`cobertura.archivos_en_alcance: publicado 611 | fresco 687`,
`excluidos_por_declaracion_git: SOLO EN EL CALCULO FRESCO`, `excepciones_aplicadas: lista de 3 elementos
publicados contra 0 calculados`, …) y EXIT 3.

Regenerado con el emisor actual y verificado con su propio `--check`, en una corrida **aparte**
(`temp/p3-05-write-report.txt`, `temp/p3-06-check-post-regenerado.txt`):

    [OK] Wiring: 174 llamadas descubiertas en 687 archivos | gobernadas 75 (conformes 21, omisiones 0)
    | amparadas por excepcion 0 | violaciones 0 | 684 excluidos por declaracion de Git
    | receptores no resueltos 25
           derivado: .opencode/wiring_report.json conforme con el calculo en memoria (digest 56a547f2ec31)

Antecedentes **medidos, no pineados**: alcance 687 · llamadas 174 · no resueltos 25 · en produccion 0 ·
excluidos por declaracion de Git 684 · gobernadas resueltas 75. La orden citaba 685 de alcance: los dos
archivos de test que anadieron las letras 1 y 2 son la diferencia, y esa es la razon por la que el derivado
se regenero despues de escribir el codigo y no antes.

Codigos: 0 conforme · 1 hallazgos · 2 error de uso o lector fallido (arbol ausente, artefacto **AUSENTE** o
**ILEGIBLE**, tres estados y no dos con un default) · 3 **DIVERGE**. El 3 va separado del 1 porque la cola
traduce cada codigo con un diagnostico: mezclar «falta una senal en un caller» con «el artefacto esta
vencido» mandaria a quien repara a buscar un caller que no existe. `run_all_validations.py` invoca ahora
con `--check` y reporta el 3 como «el artefacto publicado esta vencido (no falta un caller, falta
publicar)». La clausula **manda sobre el check**: con violaciones en el codigo, el derivado no opina.

Verificacion: `11 failed` antes de la cura, `11 passed` despues (`temp/p3-01`, `temp/p3-08`). Dos mutantes
con caida nombrada: apagar la normalizacion de los campos de procedencia vuelve el check un rojo
permanente; apagar el calculo de divergencias lo devuelve verde sin mirar. Control negativo leyendo **y
ejecutando** `5145173`: ese instrumento sale 2 por `unrecognized arguments` de la bandera.

Un defecto propio del arnes, corregido aqui porque es la leccion: la primera version del mutante de
normalizacion dio CONFORME, porque el artefacto publicado y el calculo fresco cayeron en el **mismo
segundo** y no havia fecha que normalizar. El diente se anclo entonces a un artefacto con la fecha corrida
(`2001-01-01T00:00:00+00:00`): un diente que muerde a veces no es un diente.

## Letra 3 — la cifra de gobernanza (AGENTS.md, config central, autorizada por la pegada)

Unicamente la cifra que este archivo tiene autorizada llevar: tres hunks, 19+/2-, y «nada mas de ese
archivo».

| Instrumento | Mando | Valor |
|---|---|---|
| metodo canonico | `grep -rE "^\s*def test_" tests --include=*.py` | **4.682** |
| arbol versionado | `git grep -c -E "^[[:space:]]*def test_" HEAD -- tests`, sumado con `$NF` | **4.682** |

Cuadran, y cuadran tambien en el commit que lleva la nota porque la edicion no anade ni quita ninguna
funcion-test (re-medido en `6d32abc` y en `d37928c`: sigue 4.682). Delta **+31** contra los 4.651 publicados
el mismo dia, **entero** en la fila `root test files` (1.013 → 1.044) y atribuido bateria por bateria:
**+12** del paso 1 (`test_validate_wiring_alcance_por_declaracion_git.py`, trabajo de la tanda anterior,
que la nota de 4.651 no podia incorporar porque todavia no estaba en el arbol), **+8** del paso 2 y **+11**
del paso 3. La suma de las 22 filas se verifico **recorriendo los 21 directorios y `tests/*.py` la fila de
raiz**, no sumando la columna de memoria: 21 filas sin movimiento y la de raiz arriba, y la suma vuelve a
dar 4.682 exactos.

Gate: `python scripts/validate_agents_md.py` con **EXIT 0 leido sin tuberia** y cero ocurrencias de `FAIL`
en su salida (`temp/p4-01-gate-agents.txt`).

## Letra 4 — documentar el CLI del escritor

La sintaxis se lee del `argparse` de `scripts/log_phase_completion.py`, medido sobre su propia fuente:
**quince banderas y tres obligatorias** (`--fase`, `--desc`, `--fecha`). Los dos «antes» de la tabla se
midieron contra la revision commiteada (`git show d5b4059:<ruta>`), no contra el recuerdo.

| Magnitud | Workflow (antes → despues) | CONTRIBUTING (antes → despues) |
|---|---|---|
| lineas que citan al escritor (nombre corto) | 20 → **21** | 5 → **5** |
| lineas que citan la **ruta** `scripts/log_phase_completion.py` | 8 → **9** | 2 → **2** |
| invocaciones | 7 → 7, **las 7 con `--fecha`** | 2 → 2, **las 2 con `--fecha`** |
| `--fecha` | 0 → **11** | 0 → **5** |
| `--nota` | 0 → **7** | 0 → **3** |
| `AAAA-MM-DD` | 0 → 0 | 0 → 0 |

Que CONTRIBUTING se quede en 5 menciones y 2 invocaciones es correcto: la letra ensancho las que ya estaban,
no agrego citas nuevas. Y «las 7 con `--fecha`» se verifico **invocacion por invocacion** (`grep -n` de la
ruta y lectura de sus lineas de continuacion), no con un conteo global: un `awk` de ventana que probe
primero conto 8 porque el propio `getline` se comia lineas del barrido, y ademas contaba como invocacion dos
menciones en prosa (la mia nueva, en §«COMO: Comandos Exactos», y la del changelog v2.25.0 en la linea 1476).

Fechas reales, con su procedencia: `2026-03-25` (FASE-12) y `2026-04-13` (FASE-GEO-BRIDGE), ambas con entrada
en `docs/contributing/REGISTRY.md`; `2026-09-21` —el caso documentado de la FASE-A de JEV, linea 11557 del
registro— donde el ejemplo es generico. Dos lecturas propias, declaradas: (i) `--nota` se paso en los
ejemplos donde el texto es justamente lo que la bandera governa (registro tardio, release marker, skip con
razon) y **no** en el «Caso 1 minimo», rotulado asi para mostrar las tres obligatorias sin nota; (ii) ademas
de la bandera, la fila 51 de CONTRIBUTING afirmaba «estampa con la fecha de HOY», que D-F5 dejo falso, y el
ejemplo de release carecia de `--desc`, que tambien es obligatorio: las dos invocaciones de CONTRIBUTING
habrian fallado antes de llegar al `--release`. Se corrigieron porque son lineas de uso del mismo CLI.

Protegido, y verificado como protegido: el parrafo `- **Alcance hacia delante**` (linea 728 del workflow) no
aparece en el diff de la letra (`git diff | grep -c "Alcance hacia delante"` = **0**), todos los hunks caen
en lineas ≥788, y el check **C9** sigue en verde: `descripcion del alcance: regla=cutoff en 2 texto(s)
gobernado(s)`, EXIT 0 leido sin tuberia (`temp/p5-06-check-c9.txt`).

**La cola de writers, porque el workflow es fuente proyectada de los packs.** Antes de regenerar,
`packs --check` corto los cinco con `PROYECCION-VENCIDA`: publicados 112986 bytes / 28246 tokens, en arbol
115175 / 28793, **EXIT 1** — o sea el guard de S32 si mira al workflow. Regenerados los cinco: `packs` 0,
`indice` 0, `packs --check` 0, `indice --check` 0 y `quick` **13/13** (`temp/p5-03-cola-writers-intento2.txt`).

Declaracion de captura: el crudo `p5-02` perdio el **stderr** (use `tee` sin `2>&1`, y el escritor emite sus
incidencias por stderr), o sea el archivo no prueba el rojo que si se veo. Se re-midio con stderr incluido
en `p5-07`, que ademas corre la bateria versionada que goberna ese mismo caso
(`tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py`, **6 passed**). Y el
primer intento de cola salio mal de verdad: invoque `build_phase_briefing.py` **sin `--plan`** y dio `[2]
hace falta --plan` (los `PIPELINE_EXIT=0` de ese crudo son el exit del ultimo `echo` del bloque, no el del
escritor).

**El par del parte 19-, re-medido con el metodo del crudo 05-t2** (`m-01-par-parte-19.py`, solo lectura,
sobre los packs ya regenerados): numerador **53**, denominador **13.819**, ratio **0,38 %**, lineas que
normalizan los CUATRO patrones **58** y los CINCO **63**, y `generado_por_sha` ya **SI** en el bloque meta de
los cinco packs (el crudo `01-` de la mañana decia NO en los cinco, porque los packs no se habian
regenerado desde S19(d)). Publicado medido, **no pineado**. El denominador **no** lo movio esta letra: el
`git show` de los cinco packs en HEAD daba 13.819 antes de regenerar y 13.819 despues — la regeneracion
cambio 64 lineas de valores proyectados, no el conteo de lineas. El 13.544 del antecedente es de `7737347`,
antes de las dos tandas del dia; el salto hasta 13.819 viene de esas tandas, no de esta.

## Delegacion (dos censos de solo lectura) y su re-verificacion

Ambos sub-agentes fueron de **solo lectura**: sin escritura, sin mutantes, sin medicion final y sin git de
cambio de estado. Todo eso quedo en esta sesion.

- **Censo 1, quien lee el derivado**: reporto **cero lectores** en todo el arbol (53 lineas / 56 ocurrencias
  de `wiring_report`, ninguna `json.load`/`read_text` sobre la ruta versionada; el unico consumidor,
  `run_all_validations.py:698`, invocaba sin `--write-report`). Re-verificado en disco con mi propio
  `git grep -n "wiring_report" -- "*.py"`: el unico lector hoy es `comparar_derivado`
  (`validate_wiring.py:1094`), que es la cura de la letra 2.
- **Censo 2, las lineas de uso del escritor**: reporto 20 lineas en el workflow y 5 en CONTRIBUTING,
  `--fecha` cero en los dos, y que las invocaciones del workflow estan en forma
  `./venv/Scripts/python.exe` (7) mientras las de CONTRIBUTING estan en forma `python` (2). Re-medido en
  disco con `grep -c` **y** `grep -n` antes de editar: mismo resultado. Del censo salio un dato que la orden
  no pedia y si uso: el escritor **imprime** dos invocaciones sin `--fecha` en su propia ayuda (lineas 691 y
  771).

## Verificacion, con el instrumento que la midio

- **TDD en orden, las dos letras de codigo**: letra 1 `5 failed, 3 passed` → `8 passed`; letra 2
  `11 failed` → `11 passed`.
- **Cuatro baterias del verificador juntas, sobre el arbol final**: `49 passed` (18 + 12 + 8 + 11) en
  `temp/p7-02`.
- **Suite completa, dos veces, sobre los dos arboles que importan**:
  - en `6d32abc`: `2 failed, 4720 passed, 41 skipped, 4 xfailed, 230 warnings in 647,37 s`, `EXIT=1`;
  - en `d37928c`, con `git status --porcelain -uno` en **0 rutas**:
    `2 failed, 4720 passed, 41 skipped, 4 xfailed, 230 warnings in 590,41 s (0:09:50)`, `EXIT=1`.

  Conteo identico en los dos arboles: la limpieza del quinto commit movio 4 lineas, no funciones. Los dos
  unicos rojos son los del baseline, atribuidos por su nombre
  (`tests/financial_engine/test_pricing_resolution_wrapper.py::TestCalculatePriceWithShadowFunction::test_function_default_flags`
  y `tests/test_diagnostic_geo_metrics.py::TestDiagnosticGEOMetrics::test_diagnostic_includes_geo_metrics`);
  **cero rojos nuevos**. Contra los `4701 passed` del sello `06-` (medido en `abd181c`) la diferencia es
  **+19**, que es exactamente el numero de funciones-test de las letras 1 y 2. Nota de instrumento: las
  duraciones (590 y 647 s) no son comparables con los 344-356 s de los antecedentes porque estas dos
  corridas compartieron CPU con las mediciones de la tanda; lo que se compara son los conteos.
- **Cola**: `run_all_validations.py --quick` → **13/13**, medida tres veces (tras la letra 2, antes del
  commit de la letra 4 y en el arbol limpio de `6d32abc`), con la `[GUARDA]` de denominador aprobando y el
  check 11 levando el denominador poblado en su mensaje.
- **Derivado**: `--check` en EXIT 0 con digest `56a547f2ec31` tras regenerar, **y otra vez** tras el commit
  `d37928c` con el **mismo digest** — o sea ninguna linea de la poblacion se movio, que es lo que el digest
  existe para poder afirmar.
- **Cifra de gobernanza**: 4.682 por los dos comandos, re-leida en `6d32abc`.

## Pre-vuelo y forma del empuje

- Paridad leida **antes y despues** de cada empuje: `0 0` contra `origin/master` en los cuatro casos.
- Cuatro fast-forwards puros: `6582a2c..5145173`, `5145173..fbfdc57`, `fbfdc57..d5b4059`,
  `d5b4059..6d32abc`. El quinto commit (`d37928c`) se empuja con el sello.
- Barrido de credenciales sobre **los blobs del rango** (`git grep -I -c` de cinco patrones: AKIA, ghp_,
  xox[baprs]-, PRIVATE KEY, JWT) sobre `origin/master..HEAD`: **cero coincidencias** en los cinco patrones;
  solo conteos, nunca se imprimio el contenido de una linea. Nota de instrumento: el `EXIT` de ese bucle no
  es el de `git grep` (se lo come el `echo` final), asi que la senal son los conteos por patron.
- **L3**: la orden dice que se pregunta al empujar. Se pregunto con tres alcances posibles y el operador
  eligio **empujar sin escaneo L3** para toda la tanda; queda registrado aqui en vez de barrido. El
  antecedente del paso 1 corrio L3 sobre sus commits y dio `findings_count: 0`.

## Defectos propios de esta sesion, declarados

1. **Tres lineas muertas que yo introduje** y que la tanda retiro en `d37928c`, medidas con pyflakes sobre
   los dos archivos nuevos: la constante `ARTEFACTO` (ruta que el archivo nunca leyo; el check toma la ruta
   por argumento del CLI), el local `leido = json.loads(intacto)` dentro del mutante 1, y un
   `import pytest` en un archivo que no define fixtures. Es un quinto commit, y por eso es desviacion
   declarada del «commit por letra».
2. **Dos capturas malas**: el crudo `p5-02` sin stderr y el primer intento de cola sin `--plan`. Ambos se
   re-midieron y su re-medicion esta nombrada arriba; los archivos malos se quedan en `temp/` como estan,
   porque borrar la evidencia de un error propio es peor que conservarla.
3. Lo que pyflakes tambien imprime en `scripts/run_all_validations.py` (f-string sin placeholders en :75,
   `_MAX_SCAN_BYTES` sin `self.` en :312, `status` sin uso en :1096) es **preexistente** y queda fuera de
   esta orden: no lo toque y no lo declaro curado.

## Lo que este sello NO cierra, declarado en vez de barrido

1. **Dos registros ajenos siguen narrando su pendiente como abierta.** La fila 4 del
   `REINGESTA-CONTEXT-JEV-2026-09-29/33-registro-unificado-de-pendientes-2026-09-29.md` y la fila 8 del
   `CURAS-SCRIPTS-Y-CONTEXT-2026-09-30/00-resumen.md` describen la desviacion que la letra 4 ejecuto. La
   orden prohibe editar registros ajenos, asi que el cierre se afirma aqui y la firma de esas dos filas
   sigue siendo acto del operador.
2. **El propio escritor imprime dos invocaciones sin `--fecha`**: `scripts/log_phase_completion.py:691` y
   `:771`, dentro de sus mensajes de ayuda. El mandato cubria las lineas de uso del workflow y de
   CONTRIBUTING; tocar el texto interno del script es otra letra.
3. **La copia congelada del workflow en `tests/quality_gates/governance_numbers/fixtures/` conserva ocho
   invocaciones sin `--fecha`**, y CONTRIBUTING tiene ademas tres menciones del escritor en prosa que no son
   invocacion (lineas 107, 169 y 292) y siguen correctas. La orden protegio expresamente esa copia, y no hay
   writer que la sincronice — ya lo declara la entrada v2.27.0 del propio workflow.
4. **Consecuencia de cablear el check**: `.opencode/wiring_report.json` paso a ser un gate. Cualquier `.py`
   nuevo —un test, un crudo de evidencia en Python, un scratch que mueva los conteos por rol— hace cortar el
   check 11 hasta que alguien regenere con `--write-report`. Su direccion de fallo es la correcta (corta, no
   se calla), pero el coste es real y la casa ya vive con el mismo regimen en packs e indice.
5. **La ruta roja del criterio no la ejercita el arbol vivo**: hoy `receptores_no_resueltos_en_produccion`
   es 0, asi que el EXIT 1 del quick [11/13] por esa clausula solo se prueba con arboles sinteticos y con el
   control versionado de `abd181c`. No hay diente que impida que alguien reintroduzca un hueco **y** regenere
   el derivado en el mismo commit.
6. **Los crudos de sesion no viajaron**: las corridas de suite, quick, packs, C9, pyflakes y los dos censos
   quedaron bajo `temp/`, que `.gitignore` excluye. Este documento los transcribe y los nombra por archivo.
7. **Este sello no puede nombrarse a si mismo dentro del rango que sella**: se escribio despues de `d37928c`
   y de su empuje, asi que su propio commit queda fuera de la cuenta de arriba.

---

## Addendum 2026-10-01 (CIERRE-DEUDA) — tres citas de este sello vencieron, y se estampan aqui

Este texto es **aditivo**: ninguna de las lineas de arriba se re-escribe. Lo que pasa es que tres de sus
afirmaciones, publicadas como pendientes, dejaron de ser ciertas, y un sello que no estampa lo que caduco
de el empieza a narrar un estado que ya no existe. Medido el 2026-10-01 sobre el arbol de `c4d0ffe`.

### (1) Las dos filas ajenas que este sello dejo sin firmar: ya estan firmadas

§«Lo que este sello NO cierra», punto 1. La letra B de la orden del 2026-10-01 las estampo: **`32792b6`**
— «docs(registros): las filas 4 y 8 estampan el cierre que la letra 4 ya ejecuto». Cae sobre la fila 4 de
`REINGESTA-CONTEXT-JEV-2026-09-29/33-registro-unificado-de-pendientes-2026-09-29.md` y la fila 8 de
`CURAS-SCRIPTS-Y-CONTEXT-2026-09-30/00-resumen.md`, con anotador nuevo y texto original intacto, que es la
forma en que el cierre de un registro ajeno puede darse sin re-escribirlo. El punto 1 de arriba queda
vencido y asi se declara, no se borra.

### (2) Las dos invocaciones sin `--fecha` del escritor: cerradas, y su ancla se volvio a mover dos veces

§«Lo que este sello NO cierra», punto 2, las citaba en `:691` y `:771`. **`bb1be59`** las cerró y este
addendum estampa el re-anclaje que esa tanda publico: `:692` y `:772` (verificado con
`git show bb1be59:scripts/log_phase_completion.py`, que es lectura de una revision fija, no del arbol).

Pero la linea literal **volvio a moverse en la misma sesion que escribe esta nota**: la guarda `--plan` de
la fila 15 (**`c4d0ffe`**) metio veinte lineas delante del primer print. Medido hoy, las dos invocaciones
impresas del escritor estan en **`:772`** y **`:864`**, y el rechazo nuevo añadio una tercera en **`:263`**.
Lo que si se verifico, porque es la clausula que importa y no el numero: las **tres** llevan `--fecha` en
su propio texto, asi que el contador de la doctrina sigue en 0. Se publica la condicion («toda invocacion
impresa por el escritor declara su `--fecha`») y no solo la coordenada, porque la coordenada es exactamente
lo que un commit posterior mueve.

### (3) La L3 retroactiva del rango que este sello sella: corrida, con `findings_count=0`

§«Lo que este sello NO cierra» no la nombraba: la L3 era el pendiente que la propia orden dejo abierto
(linea 231: «queda registrado aqui en vez de barrido», con el operador eligiendo empujar sin escaneo). La
correida retroactiva cubrio **`6582a2c..8c29c7e`** — es decir, el rango completo que este sello sella, los
cuatro fast-forwards de la linea 225 mas `8c29c7e` — y dio **`findings_count=0`**.

Procedencia, declarada: esa corrida es de la **sesion anterior** y no se re-ejecuto aqui, asi que se
estampa como registro ajeno verificado en su coherencia (el rango casa con los cuatro shas que este mismo
sello enumera) y no como medicion propia.

### (4) Lo que este addendum tampoco cierra, en la misma forma

El commit que lleve esta seccion es **posterior** a la corrida del punto (3), asi que por la logica de
baseline que usa el propio instrumento **queda fuera del rango que sella**. No es una excepcion de este
sello: es la regla que ya anoto la fila 16 del `33-` el 2026-10-01 («el commit que estampa el cierre queda
sin revision L3, y la proxima L3 lo barre a el y a lo que siga»). Se declara aqui en vez de barrerse, que
es lo que hace este documento cuando algo suyo sigue abierto.

Y una cuarta, nueva, medida en esta tanda: el punto 4 de arriba predijo exactamente el coste que se cobro.
Los ocho scripts decratch que `CIERRE-DEUDA` escribio en `temp/` —un directorio que ni siquiera se
versiona— vencieron `.opencode/wiring_report.json` (`exclusiones_por_rol.temp.cantidad`: 72 → 80) y
cortaron el quick [11/13]. Se republico con `--write-report`. El veredicto de cableado no se movio ni una
unidad (174 llamadas, 75 gobernadas, 0 violaciones antes y despues); lo que se movio fue la fotografia de
un directorio transitorio. Vale la pena que quien revise el gate se pregunte si un conteo de `temp/` debe
ser parte de un artefacto versionado, porque hoy obliga a re-publicar cada vez que alguien tira un scratch.

---

## Addendum 2026-10-03 (OLA-1) — la cuarta del addendum del 10-01 tiene letra, y su premisa ya estaba curada

Este texto es **aditivo**: ninguna linea de arriba se re-escribe, incluida la pregunta que cierra el punto
(4). Lo que pasa es que el operador la contesto el 2026-10-03 y que la economia que la preguntaba ya no es
la que el punto (4) describia.

### (1) La letra llego: decision (d1), dictada por el operador el 2026-10-03

Su texto, en las palabras de la pegada que lo autorizo: sacar el conteo de `temp/` del artefacto versionado
—`exclusiones_por_rol.temp` deja de pinarse en `.opencode/wiring_report.json`— y que siga publicandose en la
salida del verificador. Motivo declarado por quien la dicta: la fotografia de un directorio ignorado no es
una decision de cableado. La decision se registro como **fila 18** del
`REINGESTA-CONTEXT-JEV-2026-09-29/33-registro-unificado-de-pendientes-2026-09-29.md`, que es donde vive
ahora el registro de pendientes; su **ejecucion** toca `scripts/` y viaja con la OLA 2 (mandato
`scripts/` + `tests/` + `config/`). Nada de codigo se movio en esta tanda.

### (2) La premisa economica de esa pregunta esta VENCIDA, y el contrafactual lo dio la misma sesion que estampa

El punto (4) decia «hoy obliga a re-publicar cada vez que alguien tira un scratch». Eso lo levanto el schema
**1.2** del propio derivado, publicado el 2026-10-01 en la tanda de adopcion: `scripts/validate_wiring.py:1090-1096`
eleva a PROCEDENCIA `exclusiones_por_rol.<rol>.cantidad` y `.ejemplo` **para todo rol presente en cualquiera
de los dos objetos comparados** —no solo los del arbol fresco, para que un rol que desaparece no se ponga
rojo por ausencia—, y `_neutralizar_procedencia` (`:1100-1112`) los sustituye por la sentinela
`PROCEDENCIA-NO-GOBERNADA` antes de serializar. Lo gobernable es la contraparte versionada: hoy el artefacto
publica para `temp` una `cantidad` bruta de **90** con `cantidad_versionada` de **0**, y el digester
compara el 0.

El contrafactual no se construyo, se aprovecho: **esta tanda escribio 14 archivos bajo
`temp/ola1-2026-10-03/`** y, con ellos puestos, `python -X utf8 scripts/validate_wiring.py --check` devolvio
`[OK] Wiring: 174 llamadas descubiertas en 689 archivos ... derivado: .opencode/wiring_report.json conforme
con el calculo en memoria (digest f915bdd4943c)`, **EXIT 0** (crudo `temp/ola1-2026-10-03/15-check-con-temp.txt`),
y `run_all_validations.py --quick` dio **13/13** dos veces en el mismo arbol. O sea: el impuesto que el punto
(4) describia ya no se cobra, y se midio con el scratch puesto en vez de con memoria.

### (3) Lo que la (d1) si cambia, dicho con precision para que la Ola 2 no de un paso de mas

Hoy el conteo bruto esta **dentro del artefacto versionado** y **fuera de la salida impresa**: la linea
`[OK] Wiring: ...` no nombra `exclusiones_por_rol` en ningun caso (buscado en el crudo `15-`, cero
coincidencias). La decision pide la inversa —fuera del JSON, dentro de la salida—, de modo que ejecutarla
literal es una **mudanza**, no un retiro, y el retiro a secas dejaria al verificador mudo justo en el dato
que el operador quiere seguir viendo. Dos cosas que la Ola 2 tiene que medir antes de tocar, declaradas
aqui en vez de resueltas: quien aserta hoy `exclusiones_por_rol.*.cantidad` en la bateria (hay tests del
paso 3 que gobiernan el derivado y sus rutas), y que `--check` sigue necesitando una forma estable de
comparar roles que aparecen o desaparecen entre los dos objetos. Si al final resulta que el operador queria
solo la gobernanza (que el scratch no caduque el artefacto), **eso ya esta hecho** y no hay ejecucion.

### (4) Lo que este addendum tampoco cierra, en la misma forma que los anteriores

El commit que lleve esta seccion es **posterior** a la revision L3 corrida el 2026-10-03 —que respondio **sin
hallazgos** y, medido hoy, **no imprime su baseline ni el corte de commits**, asi que su cobertura no se
afirma desde el arbol—, ni de las ediciones del `33-`, que siguen **sin commitear** y por tanto fuera de
alcance de cualquier revision de commits. Es la regla que ya anotaron la fila 16 del `33-` y el punto (4) de
arriba: la proxima L3 barre esto y lo que siga.
