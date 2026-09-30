# Expediente — cierre de deudas + re-veredicto VCF/JEV (2026-09-29)

Sesión **única y escritora**, alcance cerrado a **T1–T5** de la orden pegada por el operador. La pegada
fue la autorización, incluidas las dos escrituras del notebook (re-ingesta y borrado del gemelo). Todo lo
demás quedó sin tocar.

- Revision de partida: `e5a654b` (leida con `git rev-parse HEAD`, y confirmada por `git log origin/master..HEAD`
  = **0** rutas tras `git fetch`).
- Arbol de partida: `git status --porcelain` = **1** linea, que es **esta propia carpeta de evidencia**
  colapsada como `??/`; `git status --porcelain -uno` = **0** lineas.
- Lo que esta sesion **no** hizo: commit, push, editar `AGENTS.md`/`.cursorrules`/`VERSION.yaml`/`DOMAIN_PRIMER`,
  tocar `scripts/log_phase_completion.py`, tomar D-B o D-D, asignar dueño de S14, inventar IDs de leccion,
  subir lecciones no pedidas, `git stash`, ni delegar el Paso 0, los veredictos, las escrituras o los commits.
- Convencion de esta casa aplicada aqui: **los veredictos nuevos se publican como seccion fechada de este
  expediente; las filas del expediente anterior no se reescriben, reciben nota datada** (secciones §2 a §4 abajo).

---

## 1. PASO 0 — re-medido, con dos precondiciones que la orden traia mal

La orden pedia fiar su contexto solo como hipotesis. Resultado de la re-medicion:

| Precondicion | Comando | Medido | Estado |
|---|---|---|---|
| Arbol limpio | `git status --porcelain -uno` | **0** lineas | cumple |
| Revision | `git rev-parse HEAD` | `e5a654bec1185eae2d11ad14718148e626a62d59` | cumple |
| Paridad con el remoto | `git fetch` + `git log origin/master..HEAD` | **0** rutas | cumple |
| Matriz vigente leida antes de medir | se abrio `BLOQUE-B-REMEDIACION-2026-09-23/00-resumen-cierre-B.md` por sus cabeceras y se leyó **§13** entero (lineas 52-140) | §13 es la unica matriz vigente; §1-§12 son antecedentes | cumple |
| Filas dueñas | `dependencias-fases.md` del plan VCF: encabezado, §S17 (cerrada por ejecucion en sus dos defectos), §S19 **(d) abierta por la salida (c)**, §S21 (cerrada por ejecucion en su salida b), §S32 (cerrada por ejecucion en el hueco del instrumento) y «Cierre formal» | leidas, no re-escritas | cumple |
| D-E y su §6 | fila D-E y §6 del expediente `RE-VERIFICACION-VCF-JEV-2026-09-28` | leidos; su ejecucion esta en §2 y §3 de este archivo | cumple |
| Notebook | `qmind source list --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45` | **Total: 55** (y 55 fuentes en el listado JSON) | cumple |

**Divergencia contra la orden, medida y declarada (no corregida en el pasado):** la orden describia la deuda
D-E(a) como «los **2** snapshots vencidos» y pedía re-ingestar los dos del plan VCF y del plan JEV. Medido por
**descarga + sha256** (crudo `03-comparacion-snapshots.txt`), la poblacion es **1**, no 2:

| Fuente | bytes publicados | sha256 publicado | bytes en disco | sha256 en disco | delta | CR en ambos lados | VEREDICTO |
|---|---|---|---|---|---|---|---|
| VCF `10-analisis` `01a0e464-3331-7684-9742-f64e009fb10b` | 106.284 | `e30a1cc3…bdd0b` | 110.891 | `0eb1d8fe…97d6aa` | **−4.607** | CR=0 los dos | **VENCIDA** |
| JEV `10-analisis` `01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5` | 15.144 | `34e2a951…84d9b9` | 15.144 | `34e2a951…84d9b9` | **+0** | CR=0 | **FRESCA** |
| Leccion §11 `01a0ef0e-aa1c-7e5d-8486-51d40b8b4f07` | 2.677 | `d968d497…41e12b1` | 2.677 | `d968d497…41e12b1` | **+0** | CR=0 | **FRESCA** |
| Gemelo VCF `01a0e0d3-92db-795b-ad7a-48a7c322e8e9` | 94.984 (chars 92.931) | `fd9829dc…b434e80` | — | — | −15.907 contra el disco | — | vencido, y **T2 lo borro** |

El JEV llego **fresco**, así que la regla de la orden («no re-ingestas nada que el Paso 0 mida fresco, la
poblacion la fija la medicion») corto la re-ingesta a una sola fuente. La hipotesis del parte sobre el VCF
(+4.607 B, shas `e30a1cc3`/`0eb1d8fe`, sin artefacto CRLF) **caso exactamente**: los dos lados tienen CR=0,
y normalizar el retorno de carro no mueve ni las medidas ni los shas.

Comandos de la medicion: `qmind source download <source_id> --nb <ID> -o <destino> --overwrite`,
`sha256sum` y lectura por bytes (`m-01-comparacion.py`). Crudos: `00-`, `01-`, `02-`, `03-`.

**Y una fuente que la orden no nombraba y que resulto medida VENCIDA: ver §4. No se re-ingesto.**

---

## 2. T1 — re-ingesta del unico snapshot medido VENCIDO

`qmind source upload --non-interactive --format json --nb 01a04d98-… --file <10-analisis VCF> --title "10-analisis: VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 (cierre formal 2026-09-27, lecciones finales 2026-09-29)"`
→ `EXIT_UPLOAD=0`, fuente nueva **`01a0ef39-b514-7b10-ae86-5ff435fee0a3`**, notebook de **55 a 56** fuentes,
`status: pending → processing → ready` (re-leido en dos listas).

Titulo **nuevo adrede**, conservando el stem: el `--upload` del escritor decide `is_ingested` por titulo y
responderia `[SKIP]` dejando la version vieja como unica verdad publicada. Verificacion **por descarga y
sha256 contra el archivo local**, nunca por titulo (crudo `12-t1-verificacion-por-descarga.txt`):

    DESCARGA : bytes=110891 sha256=0eb1d8feb18eb1a7400c2ec9a4436b92cd7d2bdb208c6471caa33807de97d6aa CR=0 LF=495
    DISCO    : bytes=110891 sha256=0eb1d8feb18eb1a7400c2ec9a4436b92cd7d2bdb208c6471caa33807de97d6aa CR=0 LF=495
    identico_crudo=True   delta=+0

Corroboracion aparte, no el criterio: `metadata.fileSha256` que el servidor publica para la fuente nueva
tambien casa con el sha del disco.

Que quede en el notebook despues de T1 y T2, para quien lea la fila D-E: **dos** fuentes del plan VCF, con
titulos **distintos** — la version original del plan (con su titulo «lecciones aprendidas y decisiones») y la
version de cierre. Esa es la forma que ya publica `TRIBUNAL-OFFLINE-2026-09-09` (dos fuentes, dos titulos). El
caso que hay que borrar es el que **repite el titulo exacto**, que era el gemelo.

Cierre con el verificador de la casa: `python scripts/validate_qmind_writeback.py --strict` →
**`[PASS] QMind Write-back: 13/13 10-analisis archivados ingested`**, `EXIT=0`. Se corrio **antes** (crudo `06-`)
y **despues** de las dos escrituras (crudo `18-`): el mismo verde en ambos lados, asi que la re-ingesta con
titulo nuevo no movio la cuenta del verificador.

---

## 3. T2 — borrado del gemelo (irreversible, autorizado por la pegada)

`qmind source delete 01a0e0d3-92db-795b-ad7a-48a7c322e8e9 --nb 01a04d98-… --force` → salida `deleted`,
`EXIT_DELETE=0`. Pre-estado leido antes de borrar (`qmind source get`, crudo `13-`): titulo identico al de
`01a0e464`, `status=ready`, `updatedAt` del 2026-09-27.

Verificacion por el listado, no por la respuesta del comando (crudo `17-cierre-notebook-post-t2.txt`):

    PRE (01) 55 -> POST T1 (09) 56 -> POST T2 (16) 55      delta T1 = +1 ; delta T2 = -1 ; neto = +0
    Total impreso por la tabla   : Total: 55
    id borrado presente en el JSON post : False
    id borrado presente en la tabla     : False
    titulos duplicados en el notebook   : 0

**Independencia declarada y respetada**: T1 y T2 no dependen el uno del otro; ambos se ejecutaron y cada uno
trae su propia verificacion.

---

## 4. Una divergence nueva que la orden no preveia: `CONTEXT` de JEV vencido por 9 bytes — **PARA, no curado**

Medida al pasar el Paso 0 sobre la quinta fuente del notebook (crudos `03-`, `04-`, `05-diff-context-jev-9b.txt`):

    fuente 01a0e4d9-e442-7d1b-bde5-7e9b669a2701  'CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21'
    DESCARGA 17.263 B / sha 04242f49…   vs   DISCO 17.272 B / sha 5587f27d…   delta = -9 bytes
    UN parrafo difiere, linea 5: la ruta del plan derivado
      publicado: .opencode/plans/EVALUACION-JEV-TYPESAFE-2026-09-21
      en disco : .opencode/plans/Archives/EVALUACION-JEV-TYPESAFE-2026-09-21

Los 9 bytes son exactamente el segmento `Archives/`: lo escribio el `git mv` de archivado (D-c), no una edicion
de contenido. **No se re-ingesto** por tres razones que se declaran juntas:

1. La pegada contaba **dos** escrituras del notebook («la re-ingesta y el borrado del gemelo»), y la poblacion
   de D-E(a) eran los `10-analisis`. Una tercera subida excede lo contado.
2. La regla de la orden ante una divergencia nueva es **PARAR y presentarla con opciones con letras**, no curarla.
3. La cura de la fila D-E no goberna esta fuente: `validate_qmind_writeback.py` audita los `10-analisis`
   archivados, no los `CONTEXT`.

Opciones para el operador (ninguna ejecutada): **(a)** re-ingestarla por CLI con titulo nuevo que conserve el
stem `CONTEXT:` y verificarla por descarga + sha256, mismo procedimiento de T1; **(b)** dejarla y registrarla
como deuda con dueño (seria la **segunda** instancia de «el archivado vence un snapshot ya publicado», familia
de la secuela que la fila D9 ya declara); **(c)** no tocar nada y dar por suficiente que el unico texto
diferido sea la ruta del propio plan. Coste de (a): una escritura externa irreversible mas; coste de (b): una
fila nueva en el libro de deuda ajena a este alcance.

---

## 5. T3 — las 82 funciones diferidas: 81 pasan y el unico rojo se atribuye en clon limpio

Poblacion fijada por medicion con el metodo canonico de la casa, archivo por archivo
(`grep -cE "^\s*def test_" <archivo>`): `test_verify_packs_in_committed_tree.py` **7** +
`test_verify_index_in_committed_tree.py` **9** + `test_build_lesson_index_s15_fecha_versionada.py` **4** +
`test_validate_lesson_capitalization.py` **30** + `test_validate_wiring.py` **18** +
**`test_registry_fecha_documental.py`** **14** = **82**. La orden decia «registry_fecha 14»; el archivo se
llama `test_registry_fecha_documental.py`.

Una sola corrida, con el exit del proceso en el crudo (sin tuberia):
`python -m pytest -q -ra <los seis archivos>` → **`1 failed, 81 passed in 107.19s`**, `EXIT_PYTEST=1`
(crudo `19-t3-pytest-82.txt`). Las 82 funciones entraron en la seleccion, asi que el denominador es el pedido.

Diagnostico **en aislado antes de atribuir**, como pedía la orden (crudos `20-`, `20d-`, `21-`):

| Paso | Resultado |
|---|---|
| El archivo solo (`test_validate_wiring.py`, 18 funciones) | `1 failed, 17 passed` (48,08 s) — el rojo no es contaminacion entre tests |
| El test solo | `1 failed` (15,87 s) |
| Poblacion leida del propio reporte (`validate_wiring.construir_reporte(raiz)`, la misma llamada del fixture) | `receptores_no_resueltos_en_produccion = 5`, **5 de 5 bajo `tmp_test/venv-jev-sdk/`**, **0 fuera de ese directorio** |
| Estado versionado de ese insumo | `git ls-files tmp_test` = **0** rutas; `git check-ignore -v tmp_test` responde `.gitignore:28:tmp_test/` |
| **Control en clon fiel de HEAD** (`git clone --no-checkout` + `core.longpaths` y `core.autocrlf=input` dentro del clon; HEAD identico `e5a654b`) | `1 passed` (10,89 s) y `receptores = 0`; poblacion del clon 680 en alcance / 101 excluidas, contra 1.364 / 8.386 en el arbol de trabajo |

Concluso: **no es regresion de esta sesion ni de las 82 funciones**. Es el rojo que la matriz §13 del bloque B
ya atribuye («5 receptores no resueltos y los cinco dentro de `tmp_test/venv-jev-sdk/…`, directorio existente
en disco, del trabajo ajeno de la evaluacion JEV»), y aqui se re-confirmo con el clon: en el arbol commiteado
el test pasa. No se borro `tmp_test/` (trabajo ajeno, y la orden no autoriza esa supresion).

---

## 6. T4 — modo completo: 16/17, y el rojo es `[16/17] Tests`

`python scripts/run_all_validations.py` (crudo `22-t4-modo-completo.txt`, `EXIT_T4_COMPLETO=1`):

- **16/17** pasan. La linea `[GUARDA] las 17 etiquetas impresas casan con el TOTAL dinamico` se imprime.
- El unico rojo es `[-] Tests`. **Seis checks verdes que vale la pena nombrar porque son los que la orden
  miraba**: `[8/13] OpenCode References: All .opencode references exist`, `[9/13] Plan Citations: 743 citas
  historicas, 0 nuevas y 0 crecimientos (79 archivos en el inventario)`, `[10/13] Lesson Capitalization [OK]`,
  `[12/13] Governance Numbers [SIN-HALLAZGOS]`, `[13/13] Briefing Packs in Commit Tree: 5/5 reproducidos,
  0 divergentes, 0 no evaluables`, y `[17/17] QMind Write-back [PASS] 13/13` — este ultimo **despues** de T1 y
  T2, que es lo que la orden pedia leer antes de tocar nada.
- Nota de instrumento: el runner **trunca** la salida de pytest (`... and 7 more`), asi que su crudo no sirve
  para atribuir nombres. La suite se re-corrio aparte (crudo `24-t4b-suite-completa.txt`, `EXIT_SUITE=1`):
  **`3 failed, 4642 passed, 41 skipped, 4 xfailed, 230 warnings in 304.39s`**.
- Los **3 rojos son los tres nombres del baseline de la casa**, con 0 nuevos:
  `tests/financial_engine/test_pricing_resolution_wrapper.py::…::test_function_default_flags`,
  `tests/test_diagnostic_geo_metrics.py::…::test_diagnostic_includes_geo_metrics`,
  `tests/test_validate_wiring.py::test_toda_la_poblacion_no_resuelta_queda_fuera_de_produccion` (el de §5).
- Los cuatro checks exclusivos del modo completo (`[14/17]`–`[17/17]`), que era deuda declarada de la tanda
  anterior, **corrieron y pasaron**: Dependencies, Module Imports, QMind Write-back; y Tests corto por los
  tres rojos preexistentes.
- Cifras de cobertura viva que el modo completo imprime y conviene tener medidas: `Wiring: 183 llamadas
  descubiertas en 1364 archivos | gobernadas 75 (conformes 21, omisiones 0) | violaciones 0 | receptores no
  resueltos 30`.
- **Lo que el quick no avala**: el `[13/13]` mira el arbol de `HEAD`, y esta sesion no commiteo, asi que su
  verde se cobra contra lo ya publicado, no contra lo que aqui se escriba.

---

## 7. T5 — re-veredicto VCF/JEV sobre la matriz §13 vigente

Re-midido cada veredicto que la orden de re-verificacion trajo como heredado, en su fuente y con su comando
(crudos `25-` a `35-`). Los instrumentos son los **versionados de la sesion anterior**, re-usados:
`barrido_parrafo.py`, `conteo_formas.py`, `m-f1.sh`, `m-f2.sh`, `m-f5.sh` — con su sha256 impreso en el crudo
`25-t5-identidad-del-arbol.txt` para que la re-medicion sea reproducible. El de AC3 se copio **por byte** y se
le movio solo la linea del destino (control `diff` en `33e-`: exactamente una linea, `3c3`), para no pisar el
crudo del 2026-09-28.

### 7.1 Veredictos por plan y AC

| Plan / item | Veredicto del 2026-09-28 | **Re-medido el 2026-09-29** | Que lo sostiene |
|---|---|---|---|
| VCF AC12 (fila ⟦E1⟧) | CUMPLIDO (no «PARCIAL», que era la orden) | **CUMPLIDO, sin cambio** | celda 2 de la fila en `evidence/…/FASE-C/criterios-de-completitud.md`, leida por `m-34-veredictos.py` (crudo `34-`) |
| VCF AC14 | CUMPLIDO — con rojo | **CUMPLIDO — con rojo, sin cambio** | mismo fila + los cuatro artefactos `mutation/` presentes en disco: `verde_baseline.json` con `removed` = **0 elementos** y `mutante_M-AC10-guard-aditividad.json` con `removed` = **11 elementos**, sobre el mismo simbolo mutado `triage_lesson_relevance.GUARD_ADITIVIDAD_ACTIVO` (el 14→14 y el 14→3 se leen de esos dos conteos) |
| VCF AC15 | PARCIAL por diseño, `acceptance = NO-EJERCITADO` | **Igual, sin cambio** | `coverage.json` → `aceptacion` re-impreso entero en el crudo `34-`, con `valor: null`, el motivo literal, `deuda_afectada` D6/D7 y el campo `prohibido` |
| JEV AC3 | REFUTADO, con medicion (0 shas casan) | **REFUTADO, re-midido** | `m-33-jev-ac3.py` (crudo `33-`): poblacion versionada **2.988 ficheros** (antes 2.852), **0 coincidencias sobre el blob de HEAD** y **0 sobre los bytes en disco**; muestra sigue `BORRADOR`, `human_reviewed=False`, `reviewer=None`, `reviewed_at=None`; y sigue sin existir fichero de candidatos versionado que lleve los `original_sha256` (3 rutas con `candidat`, todas de `evidence/FASE-P4`, otro asunto) |
| JEV regla 1.a | NO SATISFACTORIO por AC3 | **NO SATISFACTORIO, sin cambio** (es el corolario del renglon anterior) | idem |
| JEV regla 1.c / B / C / RELEASE | PENDIENTE-POR-DISEÑO | **PENDIENTE-POR-DISEÑO, sin cambio** | las tres filas del README del plan siguen `SIN AUTORIZACION PARA EJECUTARLA`, `BLOQUEADA POR DEPENDENCIA Y AUTORIZACION`, `PENDIENTE` |
| VCF regla 1.b | NO SATISFACTORIO (afirmaciones en presente vencidas, F2 y F3) | **SATISFACTORIA desde hoy, con la nota del 2026-09-28 ya commiteada como causa** | ver F2 y F3 en §7.2: los parrafos que no tenian nota la tienen, y el barrido por parrafo da **0 SIN-NOTA** en los dos alcances |

Un matiz que cambia de renglon y hay que leer con su instrumento: la busqueda literal del primer fragmento de
la muestra en HEAD paso de **1 archivo a 2**. El segundo no es un original versionado: es el crudo de la propia
sesion anterior (`13-jev-ac3-verificabilidad-sha.txt`), que **copia** el fragmento para medirlo. O sea que el
texto pre-saneado sigue sin estar guardado como original, y AC3 sigue refutado — pero la cifra «1 archivo» del
expediente anterior ya no reproduce, y su causa es la publicacion de ese expediente.

### 7.2 F1–F5, re-chequeados **por parrafo** (no por linea)

| Item | Medicion del 2026-09-28 | **Medicion del 2026-09-29** | Veredicto de esta sesion |
|---|---|---|---|
| **F1** archivado JEV | VIVO: 12 rutas bajo `Archives/`, 0 en raiz, 12 renombres (R100 ×10, R089 ×1, R099 ×1), `84282c1` si-ancestro | **Identicos los cuatro numeros** (crudo `26-`) | **CERRADO COMO HALLAZGO**: el hecho git no cambia y la nota datada que lo contradice ya esta publicada en el README del plan (su parrafo de estado) y en su contrato de ejecucion |
| **F2** piloto FASE-C VCF | VIVO, con la cifra corregida (23 rutas, no 20) | `git ls-files evidence/…/FASE-C/` = **23**; `7f2e9f9` y `5817edd` **SI-ANCESTRO** los dos; la nota «Rectificado el 2026-09-24» sigue viviendo solo en `dependencias-fases.md`, y las dos notas datadas del 2026-09-28 estan en maestro y contrato (crudo `27-`) | **CERRADO COMO HALLAZGO** (los dos parrafos que no tenian nota ya la tienen y viajaron en `c8b7198`) |
| **F3** «Única superviviente» | 11 parrafos afirman la clausula: **2 SIN nota**, 9 CON nota; criterio fuerte 5. Corpus completo (383 `.md`): 37 parrafos, 28 CON nota, **9 SIN nota** | Alcance **13 fuentes**: `TOTAL=11 CON-NOTA=11 SIN-NOTA=0 FUERTE=7`. Corpus completo (**383** `.md`): `TOTAL=37 CON-NOTA=37 SIN-NOTA=0 FUERTE=22` — los cuatro conteos leidos del **pie del propio instrumento** (crudos `28b-`, `29b-`), no de un `grep -c` sobre su salida (crudos `28-`, `29-`) | **CERRADO**: el punto de fondo del hallazgo («hay 2 supervivientes, no 1») ya no tiene supervivientes. El numero de parrafos no se movio: 11 y 37 en ambas mediciones. El criterio fuerte **subio** (5 → 7 y → 22) porque las notas que se anadieron caen despues de la negacion |
| **F4** par 518/66 de la fila S17 | El par no reproduce con ninguna ancla, en ningun instrumento, ni en la revision que lo escribio | **Sigue sin reproducir** (crudos `30-`, `30b-`, `31-`, `35-`): sobre HEAD `e5a654b`, lineas `git grep -c` **178 contra 36** (ancla del mandato) y **599 contra 81** (ancla ancha); ocurrencias `str.count` en el arbol de trabajo **179 contra 36** y **645 contra 81**; en `3c2e6a3`, la revision que firmo el 518/66, **147 contra 28** y **524 contra 72** — estos cuatro numeros **casan con la medicion anterior** de esa revision | **VIVO como cifra declarada, CERRADO como defecto de escritura**: la fila ya publica los tres pares con su poblacion e instrumento, y el `--fix` que promovia la forma minoritaria fue curado en `c8b7198` (sub-punto de S17). La proporcion de la casa hoy es **4,9 a 1** por lineas (178/36), no la «5,8 a 1» que anoto la tanda anterior: esa cifra caducaba con el arbol y aqui se re-mide |
| **F5** REGISTRY sin FASE-A de JEV | CADUCADO PARA LA ACCION / VIVO COMO DEUDA (D-F5) | **Sin cambio en los seis hechos** (crudo `32-`): menciones de `EVALUACION-JEV-TYPESAFE-2026-09-21` en REGISTRY = **0** en disco y **0** en HEAD; contraste VCF = 7 ocurrencias y su cabecera `## FASE-RELEASE … - 2026-09-25`; el escritor sigue con **13** `add_argument`, ninguno de fecha ni de nota, y la fecha de la cabecera sale de `datetime.now()`; `--dry-run` **no escribio** (sha256 de `docs/contributing/REGISTRY.md` identico antes y despues: `307f48df…0da4f45`; `git status --porcelain -uno` = **0** despues de todo) | **VIVO COMO DEUDA D-F5**, sin accion: la rama «usar el escritor» sigue cerrada por medicion. `scripts/log_phase_completion.py` **no se toco** (prohibido y dueño de D-F5) |

Las dos retracciones que la orden prohibia reabrir **no se reabrieron**: R-1 («12/16 vencido») sigue congelada, y
su medicion de denominadores vivos la confirmo esta sesion — el modo completo imprime `/13` y `/17` y su TOTAL
dinamico es **17** (crudo `22-`), exactamente lo que el crudo de censo del 2026-09-28 publico. R-2 («D1 con
dueño colgante») sigue refutada por §13, que declara **D1 CERRADA en su alcance**.

### 7.3 Cifras de la sesion, cada una con su comando

- Funciones test canonicas: **4.611** en disco **y 4.611** en el arbol versionado
  (`grep -rE "^\s*def test_" tests --include=*.py | wc -l` = 4.611;
  `git grep -c -E "^\s*def test_" HEAD -- tests | awk -F: '{t+=$NF} END {print t+0}'` = 4.611). **No se movieron**:
  esta sesion no escribio tests. La cabecera de `AGENTS.md` sigue diciendo 4.611 y **no se le toco** (ni se pudo:
  esta prohibida sin instruccion nueva).
- Items recolectados por `pytest --collect-only -q`: **4.689**. Instrumento distinto, poblacion distinta: no es
  la cifra publicada.
- Rutas versionadas: **2.988** (`git ls-files | wc -l`).

---

## 8. Fraudes de instrumento cazados mientras se medía (declarados, no corregidos en el pasado)

1. **El `Write` de este cliente emite CRLF, y un guion `.sh` con CRLF escribe en rutas con `\r` embebido.**
   Detectado con una prueba plantada a proposito: el archivo resultado salio con nombre corrupto dentro del
   propio expediente. Desde ese momento **todo instrumento se normaliza con `sed -i 's/\r$//'` antes de
   ejecutarlo** y se verifica su CR=0. El crudo afectado se borro (era mio y no era evidencia de nada).
2. **`qmind` no resuelve desde `subprocess` de Python en Windows** (`FileNotFoundError [WinError 2]`): el CLI es
   un shim `.cmd`. El primer intento de verificacion de T1 murio ahi; el crudo `10-t1-verificacion.txt` se
   conserva **con su traceback** porque muestra donde duele el instrumento mal elegido. La descarga se paso a la
   shell y el Python solo comparo bytes.
3. **Marcador autocontaminante**: la primera redaccion de las URLs firmadas sustituyo el valor por un texto que
   **contenia los propios tokens** que el contador buscaba, y el informe dio «448 supervivientes» sobre un
   archivo ya limpio. Re-marcado y re-medido: la pasada limpia cuenta **448 → 0** y el barrido del expediente
   da **0 supervivientes**. Quedan los dos numeros en el crudo `11-`, con su causa.
4. **La salida del CLI de QMind lleva credenciales**: `originUrl` y `metadata.originalFileUri` son URLs de
   objeto firmadas (`x-oss-credential`, `x-oss-signature`, `x-oss-date`, `x-oss-expires`). La regla de la casa es
   no persistirlas en evidencia, asi que se redactaron por instrumento (`11-`), conservando `id`, `title`,
   `status`, `uri` y `metadata.fileSha256`, que es lo que sostiene la medicion. El control aparte —la raiz del
   objeto firmado— da **0** ocurrencias en los tres objetos JSON.
5. **`git grep -c` cuenta lineas, no ocurrencias**, y la diferencia se ve en el propio F4 (178 vs 179 con la
   misma ancla). Se publican los dos numeros con su instrumento, como ya hizo la tanda anterior.
6. **Un `grep -c` sobre la salida de un barredor cuenta su propia leyenda.** Conté los parrafos del F3 con
   `grep -c "NOTA-DETAS-DE-LA-FRASE"` sobre el crudo y dio **8**; el pie del propio instrumento publica
   **7**. La diferencia es la linea de cabecera que define el criterio, que coincide con el patron. Lo publicado
   en §7.2 es el pie del instrumento, y la cifra mal leida queda aqui como antecedente. Misma familia: el
   marcador autocontaminante del punto 3.
7. **Los instrumentos que esta sesion dejo en `evidence/` entran a la poblacion del verificador de cableado**:
   `archivos_excluidos_por_rol` paso de **8.385** (leido en el repr del test durante T3) a **8.386** al crearse
   el siguiente guion `.py`. No es un rojo —es el numero de exclusiones de un verificador que recorre el arbol
   de trabajo y se cuenta a si mismo— pero se declara: cualquier cifra de cobertura de ese verificador es del
   arbol donde corrio.

---

## 9. Escrituras, inventario y los cinco cortes

**Escrituras efectivas de esta sesion:**

- **Notebook QMind** (fuera del repo): 1 subida (`01a0ef39-…`, titulo nuevo, verificada por descarga + sha256)
  y **1 borrado irreversible** (`01a0e0d3-…`). Poblacion neta: **55 → 55** (+1 por T1, −1 por T2).
- **Repo**: solo evidencia nueva en este directorio y las **notas datadas** del §10. Nada de codigo, nada de
  tests, nada de config central. Nada commiteado.

**Contenido de este expediente** (inventario final en el crudo `50-`, el ultimo que se escribe): **113**
archivos —**1** documento (este), **81** crudos numerados `00-` a `50-` con sus sufijos `b/c/d/e`, **6**
descargas del notebook (`descarga-<source_id>.md`) y **25** instrumentos `m-*`—. Aqui **no** se publica el
tamano en bytes: seria una cifra del propio corpus que esta edicion mueve (L-VCF-18 y la regla de no publicar
la metrica de un derivado dentro de el); el tamano y el desglose por archivo viven en `50-`, medidos en el
instante de ese inventario. Todos los instrumentos y todos los reportes que un instrumento escribe por su
cuenta estan en **LF (CR=0)**; **28** archivos conservan CRLF porque son **captura verbatim de la consola**
(`pytest`, `run_all_validations.py`, `python` con stdout redirigido, que bajo Windows emite CRLF y cp1252) y
estan listados uno a uno con su numero de retornos en el mismo `50-`. No se normalizo ninguno a mano:
normalizar un crudo seria re-escribir la evidencia.

| Corte | Estado |
|---|---|
| Implementacion terminada | **SI** — T1, T2, T3, T4 y T5 ejecutados en su alcance; la divergencia de §4 **no** se ejecuto, que es lo que la orden manda hacer con una divergencia nueva |
| Verificacion terminada | **SI** — T1 verificado por descarga + sha256; T2 por listado (Total 55, id ausente, 0 titulos duplicados); `--strict` en `[PASS] 13/13` antes y despues; modo completo 16/17 con el rojo atribuido en clon limpio; quick **13/13** con `[GUARDA]` y `git diff --check` en **exit 0** (crudos `39-`, `40-`) |
| Cierre documental | **SI** — este expediente con sus crudos, mas las tres notas datadas que vencen lo que esta ejecucion dejo atras (§10, crudos `41-`, `42-`) |
| Listo para revision | **SI** |
| Espera de autorizacion | **SI** — estado operativo final. El `git commit` no es condicion de ninguno de los cinco: es accion posterior y **pendiente de autorizacion explicita**, y el push se pregunta aparte |

---

## 10. Lo que esta ejecucion vencio y se anoto (nota datada, no reescritura)

**Cuatro** declaraciones publicadas decian que algo seguia pendiente y esta sesion lo ejecuto. Pasaron a
antecedentes con su nota datada, apuntando a este expediente como fuente del hecho (crudos `41-`, `42-`):

1. Fila **D-E** del §5 del expediente `RE-VERIFICACION-VCF-JEV-2026-09-28`: «Resta el otro miembro, la
   re-ingesta de los **2 snapshots vencidos**».
2. Nota datada del **§6** del mismo expediente: «Su ejecucion, y el borrado del gemelo `01a0e0d3-92db-…`, piden
   instrucion literal».
3. Nota del **§9** de `SESION-SCRIPTS-CURAS-2026-09-28/00-resumen.md`: «El otro miembro de la fila —la re-ingesta
   de los 2 snapshots vencidos— sigue sin instruccion».
4. Mismo §9, renglon siguiente: «**Baterias pytest … NO corridas** (82 funciones en 6 archivos …)» y la
   delegacion del modo completo a esta sesion.

Las cuatro se barraron con la forma de la casa (`⟦…⟧` datado, texto original intacto) y cada nota nombra el
detalle que la orden no preveia: **la poblacion de la re-ingesta era 1, no 2**, porque el `10-analisis` de JEV
esta fresco.

**Control de que anotar no borro nada** (crudo `42-`): sobre el diff `-U0`, la unica linea suprimida en todo el
conjunto es la celda D-E alargada; su cuerpo de **973 caracteres** reaparece **literal y completo** como prefijo
de la linea nueva (que mide 1.970, delta **+997**). `numstat` final: **9/1** en el expediente del 2026-09-28 y
**15/0** en el resumen de las curas.

**Balance de marcadores, con su instrumento correcto (crudos `41-`, `42-`, `44-`)**: contados en crudo, el
expediente del 2026-09-28 marcaba **6 aperturas contra 4 cierres** (+2) **ya en HEAD**, y parecia una pila rota.
No lo esta: al excluir el codigo inline quedan **3/3, balance 0** —los dos sobrantes son menciones literales del
caracter dentro de parrafos que **hablan** del marcador (la fila F3 y la seccion de fraudes de instrumento).
El delta de esta sesion esta pareado en los dos archivos: **+2 aperturas / +2 cierres** en cada uno, y el
resumen de las curas quedo en **9/9**. Queda publicado porque es la trampa contraria: un conteo sin filtro
acusa un hueco que no existe, y el propio filtro es frágil en un archivo con **11 lineas de backticks impares**
(bloques cercados y dos inline multineas).

**Un registro que esta sesion midio vencido y NO toco** (fuera de alcance, pide licencia): el titulo del §11
del expediente `RE-VERIFICACION-VCF-JEV-2026-09-28` sigue diciendo «La leccion del Paso 0, escrita y **pendiente
de autorizacion para subirla**» y su cuerpo «**No se subio a QMind**». Lo vencio la sesion anterior (la leccion
subio el 2026-09-29 como fuente `01a0ef0e-…`, y el Paso 0 de esta sesion la re-midio **FRESCA**), no esta. Se
declara en vez de editar: no es letra de este mandato.

**Vivas al cerrar, sin cambio y con su dueño** (esta sesion no las toco porque no le fueron asignadas):
D-B, D-D, D-F5, el dueño de S14, D3, D6 (dormida), D7, S10, S19(d), las fases B/C/RELEASE de JEV, y la
divergencia nueva de §4 con sus tres opciones.

---

## 11. El pipeline de cierre, en el orden de la casa

| Paso | Comando | Resultado (crudo) |
|---|---|---|
| Sellos fechados | cuatro notas datadas, editadas a mano por ser la forma de la casa para una nota de frescura | `numstat` **9/1** y **15/0**; CR=0 en los tres archivos tocados (`36-`, `45-`) |
| Packs | `python scripts/build_phase_briefing.py --plan Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check` | **`EXIT_PACKS_CHECK=0`**, cinco filas `[OK] … fuentes frescas y proyeccion del workflow conforme` (`38-`). **No se regenero nada**: esta sesion no edito ninguna fuente gobernada (solo evidencia), asi que el `--check` tenia que dar verde y lo dio |
| Indice de lecciones | `python scripts/build_lesson_index.py --check` | **`EXIT_INDICE_CHECK=0`**, `[OK] Índice de lecciones fresco (340 IDs)`, `[fechas] nombre=329 commit=11 sin_fuente=0` (`38-`) |
| `--check` de ambos | los dos renglones anteriores | en verde, sin escritura |
| Quick | `python scripts/run_all_validations.py --quick` | **13/13, `EXIT_QUICK=0`**, con `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`. Citas: «743 citas historicas, **0 nuevas y 0 crecimientos**» — las cuatro notas no anadieron ninguna cita numerica, deliberadamente. Se corrio **dos veces**: en el pipeline (`39-`) y **despues de la ultima anotacion** (`46-`, `EXIT_QUICK_FINAL=0`), que es la que vale |
| Integracion documental | `python scripts/validate_document_integration.py` | `RESULT: All checks passed`, `EXIT_INTEGRACION=0` (`37-`) |
| `git diff --check` | `git diff --check` | **`EXIT_DIFF_CHECK=0`** (`40-`, y re-confirmado en el cierre: `EXIT=0` otra vez) |
| Poblacion del arbol | `git status --porcelain` | **3 lineas**: 2 ` M` (los dos documentos anotados) + 1 `??` (este directorio de evidencia). Nada staged |
| Control de las cuatro escrituras | lectura UTF-8 de los tres documentos por su propio instrumento (`m-48`… en `48-`) | **CR=0, CJK=0** en los tres; marcadores pareados excluyendo codigo inline: **6/6**, **9/9** y **1/1** |
| Quick despues del control | `python scripts/run_all_validations.py --quick` | **13/13, `EXIT=0`** con `[GUARDA]` (`49-`) — la tercera corrida, la que cierra |

**Orden respetado y por que importa**: packs → indice → `--check` → quick. Como esta sesion no toco corpus
gobernado, el orden se verifico en lugar de ejercitarse; los dos `--check` en verde **son** la prueba de que
no habia derivados que regenerar. Y el `[13/13]` del quick mira el arbol de `HEAD`, asi que su verde se cobra
contra lo ya publicado, no contra lo que aqui se escribio: lo mismo que declaro la sesion anterior.
