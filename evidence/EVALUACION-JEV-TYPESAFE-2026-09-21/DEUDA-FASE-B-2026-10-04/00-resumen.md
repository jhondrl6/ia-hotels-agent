# DEUDA-FASE-B-2026-10-04 — ejecucion de la deuda declarada al cierre de FASE-B

Plan: `EVALUACION-JEV-TYPESAFE-2026-09-21`. FASE-B cerro documentalmente el 2026-10-04 con `6cdb430` y
declaro una deuda de cinco filas. Esta sesion ejecuta **solo** esa deuda, en el arbol de trabajo, y
termino en espera de autorizacion, y el operador la dio: **commit si, push no, L3 no**.

- Revision al arrancar: `6cdb430`. **Sello del cierre: la tanda se commiteo en `7899f0f` (rango `6cdb430..7899f0f`) el
  2026-10-04, sin `git push` y sin revision L3, por indicacion expresa del operador. Las frases «sin commit»
  que quedaron escritas en el material de esta sesion -aqui, en el `cierre_2026-10-04` de
  `preflight.json` y en el de `mutation.json`- describian el quinto corte, un estado anterior real, y este
  sello las vence sin borrarlas.
- **Sello del push (mismo 2026-10-04, marca 2026-10-04T20:39:47Z): la tanda se empujo a `origin/master` en el rango `6cdb430..594ebb5` (dos commits) el 2026-10-04, y la paridad se re-midio contra el servidor, no contra el ref local: `git ls-remote origin refs/heads/master` = `594ebb5f8417c4411ef4e5092f687f515b5b5d9a`, igual que `git rev-parse HEAD`, con `rev-list --left-right --count origin/master...HEAD` = 0/0. la revision L3 **no se corrio**: el operador indico «commit sin L3» y luego «git push». Queda como opcion suya sobre el rango ya empujado, no como deuda de esta sesion. precision que este sello se traga y no se calla: el commit que estampa el rango `6cdb430..594ebb5` viaja el siguiente (`594ebb5..` en cuanto se empuje), asi que el rango citado es el estado medido al estampar, no la afirmacion de que todo lo posterior este publicado.
- Cifra canonica de pruebas: `grep -rE "^\s*def test_" tests --include=*.py` = **4,795** sobre el arbol de
  trabajo; `git grep -c -E "^\s*def test_" HEAD -- tests` sumado = **4,776**. El delta de 19 es trabajo de
  esta sesion sin commitear. **Tras el sello `7899f0f` las dos convergen**: el mismo comando sobre HEAD da
  ahora **4.795** (antes, sobre `6cdb430`, 4.776), o sea la frase «median arboles distintos» describe el
  estado anterior al sello y no el vigente.
- Consumo de red de la sesion: **una** llamada Jev-style de preflight no se repitio; DeepSeek recibio **6 envios** en total (1 de la fila 2 autorizada en el mandato + 5 de la tanda (b)), todos con su request_id en los crudos.
- Gate: `python scripts/run_all_validations.py --quick` = **13/13** (crudo `07-quick-gate-post-docs.txt`). La suite
  completa no se corrio, por mandato.

## Tabla de las cinco filas, en su estado medido nuevo

| # | Fila | Estado medido nuevo | Evidencia (ruta, sha, comando que la imprime) |
|---|------|---------------------|-----------------------------------------------|
| 1 | AC6 — guard real del triaje | **CERRADA**: el test existe, corre sobre el script versionado y su mutante de clausula corta rojo por la causa nombrada | `tests/quality_gates/lesson_relevance/test_triage_guard_real_aditividad.py` (4 pruebas); bateria `python -m pytest tests/quality_gates/lesson_relevance/ -q` = **62 passed** (58 previos + 4); mutacion `scripts/triage_lesson_relevance.py` sha `8538cf89c246` → mutante `5691f0d126e5` → restaurado `8538cf89c246` (`restauracion_coincide: true`, `git status` limpio); rojo rc=1 con 11 filas removidas, verde rc=0. Crudos `03-ac6-mutacion-crudo.json` y `08a-arnes-mutacion-ac6.py`. Cierre: `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/mutation.json` → `ac6_aditividad_no_cubierta_en_esta_ronda.cierre_2026-10-04` |
| 2 | DeepSeek real (AC12 + AC4) | **EJERCITADA** con 6 envios (1 del mandato + 5 de la tanda (b)): autenticada (AC12), con modelo efectivo y usage (AC4). **Hallazgo y su resolucion**: el servicio firma `deepseek-flash` al pedir `deepseek-chat` (4 de 4), y la tanda midio que ese nombre si se puede pedir pero **no es equivalente** (modo razonamiento, `content` vacio) => no se cambia el pedido | `python temp/deuda-2026-10-04/p4_deepseek.py` (copia en `08b-arnes-deepseek-sonda.py`); request_id `3317ed3c-7afa-4a1e-9697-eb4baf3a6c34`; usage 138 in / 36 out; pedido `deepseek-chat`, **devuelto `deepseek-flash`**. Crudo `04-deepseek-crudo.json`. Cierre: `preflight.json` → `proveedores.deepseek.cierre_2026-10-04`. Tanda (b) autorizada despues: **5 envios mas** en dos sondas (6 en total en la sesion) (`09-deepseek-estabilidad-crudo.json`, `10-deepseek-flash-direccionable-crudo.json`) y addendum `proveedores.deepseek.cierre_b_2026-10-04_estabilidad_del_alias` La clave no se imprimio en ninguna salida (ni su valor ni su longitud: la regla de la casa es `preflight.json:29`) |
| 3 | Write-back del 10-analisis | **CERRADA**: fuente nueva publicada con titulo fechado 2026-10-04, anterior intacta (56 → 57), descarga + sha256 casando con el disco | Nueva fuente `01a10853-6da2-7820-b2a3-fa1cb5ccb4ba`, titulo `10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre FASE-B, lecciones finales 2026-10-04)`, `createdAt: 2026-10-04T19:10:47.714529Z`, `status: ready`. Anterior `01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5` intacta (15144 B, sha `34e2a95195b2ddb4…`). Descarga de la nueva: 21249 B, sha256 `424b5828e34145fbaff7e72bf117d4b25a777c8f4f9e30156229aaa0ace81f90` == sha256 del archivo en disco (crudo y normalizado: el archivo no trae CRLF). `python scripts/validate_qmind_writeback.py --strict` = `[PASS] 13/13` |
| 4 | Diente de frescura del 10-analisis | **CERRADA**: primera corrida roja por la causa prevista, verde tras republicar, poblacion declarada explicitamente y control negativo ejecutado sobre la version fija | `scripts/verify_qmind_context_freshness.py` (poblacion declarada + `poblacion_declorada()`); roja: `python scripts/verify_qmind_context_freshness.py` EXIT=1 con `[VENCIDO] 10-analisis-post-implementacion.md (Archives/EVALUACION-JEV-TYPESAFE-2026-09-21/…): sha_disco=424b5828e341…` (crudo `01-diente-primera-corrida-roja.txt`); verde tras el write-back: EXIT=0 con `[FRESCO] … (01a10853-6da2…coincide)` sin barrido completo (crudo `02-diente-tras-republicar-verde.txt`); bateria `python -m pytest tests/test_verify_qmind_context_freshness.py -q` = **28 passed** (17 + 11) |
| 5 | Rojo del clon limpio en la fila 230 | **CERRADA** con premisa condicional: verde en el arbol, salto motivado en clon limpio, aserciones intactas | `tests/test_validate_wiring_alcance_por_declaracion_git.py` (12 → 16): arbol `python -m pytest tests/test_validate_wiring_alcance_por_declaracion_git.py -q` = **16 passed**; clon limpio de `6cdb430` con la version versionada del archivo = **1 failed, 11 passed** (`assert publicado["cantidad"] > 0` con `{'cantidad': 0, 'estado': 'GIT_OK', …}`, crudo `06-fila-230-en-clon-versionado-head-rojo.txt`); el MISMO clon con el archivo curado = **15 passed, 1 skipped** con la razon citable (crudo `05-fila-230-en-clon-limpio-curado.txt`). Control anclado a la revision fija `4c113de`: las seis aserciones de la fila 230 son las mismas por AST |

## Como se ejercito cada cierre

### Fila 1 — el guard real, no el simbolo

El registro de FASE-B dejo escrito que faltaba «el diente de AC6 sobre el guard real del triaje ajeno».
Ejercitado asi:

- El test pide el script por ruta (`conftest.py::trl`) y **contrasta lo cargado contra el blob de HEAD**
  (`git show HEAD:scripts/triage_lesson_relevance.py`, sha256 `8538cf89c246…` por las dos vias): por eso la
  palabra «versionado» esta medida y no supuesta.
- Verde medido sobre el arbol vigente: `anchored_before = anchored_after = 25`, `removed = []`,
  `intentos_filtrados` = 11 ids (`L-R.1`, `L-R.3`, `L-R.4`, `L-NC10`, `L-PF6`, `L-PF10`, `L-V2.3`, `L-V2.1`,
  `L-V2.2`, `D-V2.1`, `L-HF1`) y `candidatos con eleccion = 46 de 46`. Es decir: el filtro tuvo once filas
  ancladas en la mano y el guard devolvio las once.
- El mutante corta el **texto** de la clausula de reinsercion. La diferencia con AC14 es real y declarada:
  apagar `GUARD_ADITIVIDAD_ACTIVO` ya lo hacen los dientes de la ronda anterior; aqui se prueba la otra
  mitad del guard, y con el simbolo activo.
- La secuencia sobre el disco (mutacion → rojo → restauracion → verde) se corrio con ancla unica y
  restauracion verificada por sha; `git status --porcelain -- scripts/triage_lesson_relevance.py` quedo
  vacio.

### Fila 2 — DeepSeek: autenticacion, modelo efectivo y la etiqueta que firma el servicio

**Como se pidio y como se cobro.** Via preferida: el brazo de la costura
(`scripts/proveedores/deepseek.py:evaluar`), que es invocable aislado. El unico campo del cuerpo que anadio
esta sesion es `max_tokens`, y lo anadio por la costura `transporte` del propio brazo antes de llamar a
`post_default`: el resto del payload y todo el parsing son del brazo. Cero reintentos del brazo en todos los
envios. **Consumo total de la fila: 6 envios** — 1 de la autorizacion original del mandato (19:13:59Z,
request_id `3317ed3c-7afa-4a1e-9697-eb4baf3a6c34`) y 5 de la tanda (b) que autorizo despues el operador. La
letra de (b) decia «sondas minimas (un par de envios)»; **el desborde a cinco esta declarado** en
`preflight.json` → `cierre_b_2026-10-04_estabilidad_del_alias.desborde_declarado`, con su motivo: el tercer
envio dio 200 con content vacio y con ese resultado no se decidia nada. Usage acumulado de los cinco envios
cuyo envelope se leyo: **716 prompt / 396 completion**, de los cuales **254 fueron `reasoning_tokens`**; el
sexto (`deepseek-flash` con tope 64) no expuso su usage porque el brazo revienta antes de devolverlo, y esa
laguna se declara como vacio, no como cero.

**AC12 (autenticacion): AUTENTICADA.** Cuatro envios con HTTP 200 y respuesta util, sin rechazos de
credencial.

**AC4 (modelo efectivo): el eco es estable y es una etiqueta de serving, no un nombre para pedir.**
- Pidiendo `deepseek-chat`, el servicio firma `model: "deepseek-flash"` en **4 de 4** envios exitosos (la
  sonda original, dos de la tanda de estabilidad —request_ids `31256bbb-…` y `180fc230-…`— y el control de
  la tanda de direccionabilidad). No fue un azar de una corrida.
- `deepseek-flash` **si se puede pedir**: HTTP 200 y se echo a si mismo. Pero **no es equivalente**: con tope
  64 y con tope 254 devolvio `content_len = 0` y `finish_reason = length`, con los 254 tokens de salida
  consumidos en razonamiento (`completion_tokens_details.reasoning_tokens = 254`). El control de la misma
  corrida, mismo cuerpo y mismo tope pidiendo `deepseek-chat`, dio 36 tokens, `finish_reason = stop` y 89
  caracteres de content.
- **Reading para la pregunta que abrio la tanda**: no se cambia el pedido a `deepseek-flash`. Lo que la tanda
  desmiente es la etiqueta del eco, no la ruta del pedido; pedir el nombre con el que el servicio firma
  activa otra forma de responder y el brazo, tal como esta, la rechaza por content vacio. El brazo ya
  declaraba `alias_movil: true` para `deepseek-chat`, y esa declaracion es la que goberna.
- **Lo que NO se afirma**: si `deepseek-flash` es una capa de routing del proveedor o un alias de producto.
  Con n = 1 por nombre no se decide el significado; queda en «lo que queda abierto», item 4.

**Causa medida del `respuestas` vacio** (la reserva que dejo el cierre anterior, ya supersedida). El servicio
contesto `{"respuestas": [{"pregunta_id": "1", "tipo": "probabilidad_si", "probabilidad_si": 1.0}]}` mientras
la sonda pregunto con el id `sonda:1`, y `_mapear_respuestas` casa por id **exacto** y descarta la respuesta:
el payload sale `respuestas: []` con un modelo que SI contesto. Reproducido en **3 de 3** envios con content,
todos con `finish_reason = stop` y 34-36 tokens de salida — o sea ni truncamiento ni transporte: es el id que
el modelo recorta. Importa fuera de esta fila porque el comparador y el triaje preguntan con ids prefijados
(`sonda:1`, `pert:L-R.1`): un emisor que recorta el prefijo **vacia el ledger sin ruido y sin devolver el
gasto**. No se curo aqui: no estaba en el mandato y tocar el brazo moveria sus diez tests sin esa
autorizacion; tiene duena sugerida en `preflight.json`.

**Lo que sigue sin tocar esta fila.** `cuota_o_saldo` continua `NO-EJERCITADO`: ninguna de las dos tandas
autorizo leer saldo. Y la muestra congelada y `protocolo.json` no se movieron: se midio el nombre con el que
el servicio firma, no se re-etiqueto el brazo.

**Credenciales.** Ni la clave ni el header Authorization ni el contenido de `.env` se imprimieron en ninguna
salida, y tampoco su longitud (la regla de la casa es `preflight.json:29`: presencia por nombre y resultado
de autenticar, jamas la clave ni su longitud ni un prefijo). Barrido sobre lo escrito: las 10 variables de
`.env` con nombre `*_KEY` / `*_PASSWORD` / `*_CREDENTIALS_PATH`, buscadas como subcadena en los 14 archivos
del expediente, en los dos cierres de `FASE-B`, en `AGENTS.md`, en `docs/cobertura-historia.md`, en
`.opencode/wiring_report.json` y en los tres archivos de prueba tocados → **SIN HALLAZGOS**. Un barrido
ingenuo que tome *cualquier* valor de `.env` de ocho caracteres o mas si da un falso positivo: casa el valor
de `LLM_PROVIDER` (`deepseek`), que es el nombre de un proveedor y no un secreto; se declara aqui para que
nadie lea ese ruido como una fuga.

### Fila 3 — write-back por las herramientas MCP del agente

- `list_sources` del notebook `01a04d98-b7bd-778c-8441-26fdc7e35f45`: **56** fuentes antes, **57** despues
  (`totalSize` leido del listado paginado, no contado a mano).
- **Rectificacion de una premisa del prompt**: la publicacion del 2026-09-30 00:52Z es la del **CONTEXT**
  (`CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21 (cierre 2026-09-29, plan archivado en Archives)`,
  id `01a0efcc-3297-…`, `createdAt: 2026-09-30T00:52:12Z`). La ultima ingesta del `10-analisis` era del
  **2026-09-27 21:51:07Z** (id `01a0e4d9-b252-…`). El rojo previsto no cambia de causa —el disco se movio
  el 2026-10-04 con `6cdb430` despues de ambas ingestas— pero la fecha que hay que citar era otra y se cita
  la medida.
- No existe `delete_source`, y no se borro nada: la fuente anterior sigue publicada y contada.
- Verificacion por contenido, no por titulo: descarga de la nueva fuente (21249 B) con sha256 igual al del
  archivo en disco, con CRLF normalizado a LF en ambos lados (de hecho el archivo y la bajada no traen
  CRLF, asi que crudo y normalizado coinciden).
- `--strict` del hermano sigue `[PASS]` porque su `is_ingested()` decide por titulo (:131-147) y el titulo
  nuevo conserva el prefijo. Que el hermano imprimiera `[SKIP]` en un hipotetico `--upload` (:201-203) es
  **esperado**: la frescura ya no la goberna el titulo sino el diente por bytes. No se corrio `--upload`.

### Fila 4 — la poblacion declarada entra por declaracion

- El gobernado nuevo no es un `CONTEXT-*` autodeclarado: `POBLACION_DECLARADA` nombra su ruta **bajo
  `--plans-dir`** (por eso la bateria puede montarlo en un tmp) y el prefijo de titulo con el que se recorta
  la bajada, con la identificacion del notebook en el texto. Las aserciones existentes de CONTEXT no se
  movieron: la linea `poblacion: N CONTEXT gobernado(s)` conserva su forma y su cuenta.
- El criterio es el mismo que el de S34: descarga + sha256 por bytes, y `metadata.fileSha256` solo
  corroboracion. El prefijo **recorta, no decide**: con una fuente de titulo irreconocible que casa por
  bytes el verificador sigue diciendo FRESCO tras el barrido completo, y hay una prueba que lo afirma.
- Un gobernado declarado cuyo directorio de plan existe pero cuyo archivo falta corta **NO-EVALUABLE (2)**,
  no silencio: un `git mv` del plan no puede convertir un gobernado en verde vacio.
- La etiqueta del estado paso a `frescura de CONTEXT/10-analisis declarados`, que conserva el token con el
  que filtra el runner (`run_all_validations.py:996`) y hay una prueba que lo goberna leyendo el filtro del
  runner en vez de pinearlo.
- **Limitacion de instrumento observada y declarada**: en la primera corrida tres descargas fallaron con
  `error: QMind network request failed`. Como la bajada se cachea por fuente y corrida, ese ruido convirtio
  un `CONTEXT` **fresco** en `[VENCIDO]` (medido por otra via: la fuente `01a0efcc-…` pesa 17272 B y su
  sha256 `5587f27ddd5a…` casa con el disco). Un `SIN-DESCARGA` es transporte, no veredicto de contenido. No
  se agrego reintento: no estaba en el mandato de esta fila y cambiar la degradacion de S34 habria movido
  semantica de las aserciones existentes.

### Fila 5 — el rojo era del arbol de la maquina, no del instrumento

- La fila 230 exige `excluidos_por_declaracion_git.cantidad > 0`, y esa poblacion vive en la maquina: en el
  arbol de trabajo son los **684** `.py` de `tmp_test/` (el aislado del piloto). Un clon limpio no lo lleva
  porque `.gitignore` lo declara fuera del control de versiones, y alli el instrumento responde
  `{'cantidad': 0, 'estado': 'GIT_OK'}` — que es un resultado **legitimo**, como lo declara su propio
  bloque `limites`.
- La guarda es condicional y esta **antes** de publicar el artefacto: con el insumo puesto la prueba corre
  entera (16 passed en el arbol); con el insumo ausente salta con la razon que se puede citar, y hay una
  prueba que ejerce los dos estados sobre el MISMO reporte sintetico.
- El predicado no se midio con la funcion que se prueba: usa el corte propio del arnes
  (`_declaracion_git`) y la tabla `EXCLUSIONES_POR_ROL` leida como datos.
- Ninguna asercion se aflojo, y eso no se afirma de memoria: el control anclado a la revision fija
  `4c113de` extrae la funcion de la version versionada y de la actual con AST y exige que las seis
  aserciones sean identicas.
- **Asignacion**: la cura se asigna a esta tanda por declaracion del cierre de FASE-B. El registro propio
  del hermano (`33-registro-unificado-de-pendientes-2026-09-29.md` del plan
  `VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20`) **no se movio**: no se le escribio un cierre que esa sesion no
  dio.

## Escrituras colaterales, con su motivo

- `.opencode/wiring_report.json` **re-publicado dos veces** con el mecanismo documentado del verificador
  (`python scripts/validate_wiring.py --write-report`). El derivado versionado quedo vencido por las
  escrituras de esta sesion en dos momentos distintos y por causas distintas: primero
  `cobertura.archivos_en_alcance` 697 → **698** (el archivo nuevo de `lesson_relevance`, que es codigo
  versionado del proyecto) y despues `exclusiones_por_rol.evidence.cantidad_versionada` 115 → **117** (los
  dos arneses de esta sesion que se guardaron dentro del expediente, en `08a-` y `08b-`). Estado final:
  `--check` = `derivado conforme, digest 1a6602b8491d`, EXIT 0, y gate rapido **13/13**. Sin re-publicar, el
  gate cortaba 12/13 con `[-] Wiring … falta publicar`. Se re-publico el artefacto, no se re-bajo la
  asercion del gate.
- Un clon anidado que esta sesion creo en `temp/clon-2026-10-04` para medir la fila 5 **rompia el gate por
  su cuenta**: Git no desciende a un repositorio anidado, asi que sus archivos no salian declarados
  ignorados y el verificador los contaba como exclusiones **versionadas** (`archives.cantidad_versionada`
  12 → 24). Retirado el clon, el unico delta restante era el legitimo. Se declara porque es una forma de
  falso rojo que cualquier scratch con `.git` dentro del arbol puede reproducir.
- `AGENTS.md`: cabecera `### Cobertura por Modulo` 4.776 → **4,795**, fila `quality_gates` 942 → **946** y
  fila `root test files` 1,063 → **1,078**. La nota de la ronda se aparco en `docs/cobertura-historia.md`
  arriba del todo, sin borrar las previas. Verificado: la suma de la tercera columna de la tabla casa con
  la cabecera (4,795), la tabla mantiene 3 celdas por fila, `python scripts/validate_agents_md.py` EXIT 0 y
  `python scripts/validate_governance_numbers.py` `SIN-HALLAZGOS`.
- Nada de `10-analisis` del plan, del protocolo de la muestra, de `muestra.json` ni de `REGISTRY.md` fue
  editado por esta sesion: el mandato lo prohibe y la fila 4 goberna ese archivo por lectura.

## Lo que queda abierto al terminar la sesion

1. **Push y L3**: la sesion esta commiteada en `7899f0f` y **no empujada**; el push y la revision L3 siguen siendo
   acto del operador (esta tanda se hizo «commit sin L3», por indicacion). Verificacion del commit en su propio
   arbol: clon limpio de `7899f0f` **fuera del repo** (`AppData/Local/Temp`, no bajo `temp/`: un clon
   anidado si rompe el gate del derivado), baterias tocadas = 90 passed y, en el archivo del wiring,
   15 passed / 1 skipped con la razon citable.
   **El push se dio**: la tanda se empujo a `origin/master` en el rango `6cdb430..594ebb5` (dos commits) el 2026-10-04, y la paridad se re-midio contra el servidor, no contra el ref local: `git ls-remote origin refs/heads/master` = `594ebb5f8417c4411ef4e5092f687f515b5b5d9a`, igual que `git rev-parse HEAD`, con `rev-list --left-right --count origin/master...HEAD` = 0/0. la revision L3 **no se corrio**: el operador indico «commit sin L3» y luego «git push». Queda como opcion suya sobre el rango ya empujado, no como deuda de esta sesion.
2. **`respuestas` vacias del brazo DeepSeek**: causa **medida** en la tanda (b) —el modelo devuelve el id
   recortado (`1` por `sonda:1`) y `_mapear_respuestas` descarta la respuesta—; **la cura no se autorizo**:
   es del brazo `scripts/proveedores/deepseek.py` y moveria sus diez tests.
3. **`cuota_o_saldo` del brazo DeepSeek**: NO-EJERCITADO; ninguna de las dos tandas lo autorizo.
4. **Si el `deepseek-flash` del eco es una capa de serving o un alias de producto**: medido que se puede
   pedir y que responde distinto, no medido que significa. Lo responde la documentacion del proveedor o una
   pregunta con dueno, no este arbol.
5. **El reintento de descarga del diente de frescura**: un `SIN-DESCARGA` transitorio puede pintar de
   `VENCIDO` a un gobernado fresco. Se declaro la limitacion; curarla merita letra propia porque cambia la
   degradacion de S34.
6. **`git clone` dentro del arbol** como patron de scratch que rompe el gate del derivado versionado.

## Manifiesto del expediente

| Archivo | Bytes | sha256 (16) |
|---|---|---|
| `01-diente-primera-corrida-roja.txt` | 5880 | `6fa43232a9a82b0b` |
| `02-diente-tras-republicar-verde.txt` | 4569 | `d2c4edcf093a137a` |
| `03-ac6-mutacion-crudo.json` | 1987 | `f6bb0d1452d6a25e` |
| `04-deepseek-crudo.json` | 1813 | `a9b97eb8e15cf1e5` |
| `05-fila-230-en-clon-limpio-curado.txt` | 882 | `5afb20b0affbf204` |
| `06-fila-230-en-clon-versionado-head-rojo.txt` | 2711 | `6405962d748ea333` |
| `07-quick-gate-post-docs.txt` | 3071 | `1165a28a1553d2ce` |
| `08a-arnes-mutacion-ac6.py` | 5367 | `983064878dd20cc1` |
| `08b-arnes-deepseek-sonda.py` | 7433 | `eb5b795a2980303d` |
| `08c-arnes-deepseek-estabilidad.py` | 8992 | `2b6f6c79db8e4ba6` |
| `08d-arnes-deepseek-direccionabilidad.py` | 6955 | `339688a86b571762` |
| `09-deepseek-estabilidad-crudo.json` | 3234 | `bb7b98cfde7a5845` |
| `10-deepseek-flash-direccionable-crudo.json` | 2463 | `3e18b0bc80918439` |

El sha del propio `00-resumen.md` no se lista: listarlo cambiaria lo que lista. Los bytes de
`07-quick-gate-post-docs.txt` son la corrida del gate rapido del **cierre de la sesion**, despues de todas las escrituras
documentales (13/13, EXIT 0); los arneses `08a-`/`08b-` son copia literal de los que corrieron en
`temp/deuda-2026-10-04/`, que `temp/` excluye por `.gitignore:21`.

