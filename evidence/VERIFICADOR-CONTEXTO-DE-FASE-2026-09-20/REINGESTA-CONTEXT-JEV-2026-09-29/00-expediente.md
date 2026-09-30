# Expediente — cierre de la divergencia del `CONTEXT` de JEV (2026-09-29)

Sesion **unica y escritora**, alcance cerrado a **UNA tarea**: la divergencia del §4 del expediente
`RE-VEREDICTO-VCF-JEV-2026-09-29`. La pegada del operador fue la autorizacion, incluida la **unica escritura
del notebook** que la orden previa (fuente nueva con titulo nuevo, opcion (a) del parte). **El borrado nunca
entro en este alcance**: ninguna fuente se borro.

- Revision de partida: `f624e02881d7a4213378ab1b7ed3ce49a1c2607a`, leida con `git rev-parse HEAD`.
- Arbol de partida: `git status --porcelain` = **0** lineas **antes** de abrir esta carpeta; `-uno` = **0**.
  Medido de nuevo tras abrirla, el `--porcelain` da **1** linea que es **esta propia carpeta** colapsada como
  `??/`. Es la misma situacion que declaro la tanda anterior: el arbol versionado esta limpio.
- Paridad con el remoto: `git fetch` + `git log origin/master..HEAD` = **0** rutas; `HEAD` y `origin/master`
  son la misma revision.
- Lo que esta sesion **no** hizo: borrar ninguna fuente, re-ingestar otro snapshot aunque lo midiera vencido,
  editar `AGENTS.md`/`.cursorrules`/`VERSION.yaml`/`DOMAIN_PRIMER`, tocar `scripts/log_phase_completion.py`,
  tomar D-B/D-D ni asignar dueño de S14, inventar IDs de deuda, `git stash`, commitear ni empujar, ni delegar
  el Paso 0, la escritura, la verificacion, los sellos o los commits (**no** hubo subagentes).
- Crudos: todos los archivos de esta carpeta. Ningun crudo acaba en `.log` (ver §5, trampa medida).

---

## 1. PASO 0 — re-medido, y la hipotesis del parte caso caracter a caracter

| Precondicion | Comando | Medido | Estado |
|---|---|---|---|
| Arbol limpio | `git status --porcelain` / `-uno` | **0** / **0** lineas antes de abrir la carpeta | cumple |
| Revision | `git rev-parse HEAD` | `f624e02…c2607a` | cumple |
| Paridad con el remoto | `git fetch` + `git log origin/master..HEAD` | **0** rutas | cumple |
| Expediente leido **antes** de medir | §1 y §4 de `RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md`, mas §10 y su crudo `05-` | leidos enteros | cumple |
| Notebook | `qmind source list --nb 01a04d98-… --all` | **Total: 55** (y 55 items en el JSON) | cumple |
| Sin gemelo previo del stem | conteo por subcadena en el listado JSON | **1** coincidencia, **0** titulos repetidos | cumple |

Crudos `00-`, `02-`, `02f-`.

### La divergencia, re-medida HOY por descarga + sha256 (crudos `01-`, `01b-`)

    fuente 01a0e4d9-e442-7d1b-bde5-7e9b669a2701  'CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21'
    DESCARGA : bytes=17263 sha256=04242f49… CR=0 LF=125
    DISCO    : bytes=17272 sha256=5587f27d… CR=0 LF=125
    delta_bytes_disco_menos_descarga=9      shas_iguales=NO (sigue VENCIDA)
    diff     : una sola diferencia, 5c5      DIFF_EXIT=1

Las dos cifras y los dos shas **son los mismos que publico el parte**: no se movio ni un byte desde aquella
medicion, asi que nadie escribio entre las dos. La hipotesis del §4 caso integra: la linea 5 es la ruta del plan
derivado y el segmento `Archives/` es exactamente los 9 bytes de diferencia.

Corroboracion aparte del criterio (que es la descarga): el `metadata.fileSha256` que el servidor publica para la
fuente vieja tambien es `04242f49…`, o sea el servidor efectivamente tiene la version vencida.

---

## 2. T1 — la unica escritura, con titulo nuevo que conserva el stem

    qmind source upload --non-interactive --format json --nb 01a04d98-… \
      --file .opencode/context/CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21.md \
      --title 'CONTEXT: CONTEXT-JEV-TYPESAFE-CASOS-DE-USO-2026-09-21 (cierre 2026-09-29, plan archivado en Archives)'

`EXIT_UPLOAD=0` (crudo `03-`, stdout de 1.868 B; `03a-` lleva el sha local de partida). Fuente nueva
**`01a0efcc-3297-7782-9467-757fe81018fc`** (extracto por campos sin credencial en `04-`, id persistida en `04a-`),
`status: pending → ready` (crudo `05a-`: `intento=1 EXIT_GET=0 status=ready`). Todo por shell: `qmind` no
resuelve desde subprocess de Python en Windows.

Titulo **nuevo adrede, conservando el stem**: el `--upload` decide `is_ingested` por titulo y repetir el titulo
responderia `[SKIP]`, dejando la version vencida como unica verdad publicada.

### Verificacion por DESCARGA + sha256 contra el archivo local, nunca por titulo (crudo `05-`)

    DESCARGA : bytes=17272 sha256=5587f27d… CR=0 LF=125
    LOCAL    : bytes=17272 sha256=5587f27d… CR=0 LF=125
    delta_bytes=0    identico_crudo=True    DIFF_EXIT=0 (diff vacio)

Corroboracion aparte: `metadata.fileSha256=5587f27d…` y `metadata.fileSize=17272` que el servidor publica para la
fuente nueva.

### Estado del notebook despues de T1 (crudos `06-`, `06e-`, `06c-`)

    PRE (02) 55  ->  POST (06) 56        delta = +1        Total impreso por la tabla: Total: 56
    coincidencias_del_stem=2  (titulos DISTINTOS: original + cierre)
    titulos_repetidos=0                                   <- control anti-gemelo
    fuente_anterior_presente=True                          <- esta orden NO borra
    anterior.fileSha256=04242f49…   nueva.fileSha256=5587f27d…

Forma resultante: **original + cierre**, dos fuentes con dos titulos, la misma que ya publica
`TRIBUNAL-OFFLINE-2026-09-09` y la que dejo la tanda anterior para el plan VCF. El caso que hay que borrar es el
que **repite el titulo exacto**, y aqui no se repite.

Nota de instrumento: el JSON del listado trae `totalSize=0` cuando se pide con `--all` (el merge de paginas no lo
rellena). El **56** sale de contar los items y de la linea `Total: 56` que imprime la tabla, no de `totalSize`.

---

## 3. Redaccion de las URL firmadas de los JSON persistidos (crudos `07a-`, `07-`, `07b-`)

Cuatro JSON quedaron en la carpeta y los cuatro llevan `originUrl` con firma. El control casa con la **FORMA del
valor**, no con el nombre del token: `x-os`+`s-(signature|credential|date|expires)=`, construido por
concatenacion en el instrumento para que ni el marcador (`REDACTADA`) ni el propio instrumento contengan el token
buscado.

| JSON | forma antes | hojas con forma | marcadores | forma despues |
|---|---|---|---|---|
| `02-source-list-pre.json` | 220 | 55 | 55 | 0 |
| `03-t1-upload.json` | 4 | 1 | 1 | 0 |
| `05-get-01a0efcc-….json` | 4 | 1 | 1 | 0 |
| `06-source-list-post.json` | 224 | 56 | 56 | 0 |
| **TOTAL** | **452** | **113** | **113** | **0** |

Segundo barrido, mas ancho que la forma de la casa (`signature|expires|credential|security[-_]token|
access[-_]key|acl)=` en cualquier grafia, mas cualquier URL con query): **0 coincidencias** en los cuatro JSON y
**0 hojas de mas de 200 caracteres** que puedan ser una URL sin firmar. Se conservan `id`, `title`, `status`,
`uri` y `metadata.fileSha256`.

---

## 4. Los tres sellos fechados (crudos `08-`, `08b-`, `09-`, `10-`)

Nota datada con la forma de la casa (`⟦…⟧`), **texto original intacto**, apuntando a este expediente como fuente
del hecho y **sin re-transcribir cifras**.

| Sello | Archivo | Como se ubico | numstat | delta de marcadores |
|---|---|---|---|---|
| 1. §4, de «PARA, no curado» a ejecutada | `RE-VEREDICTO-VCF-JEV-2026-09-29/00-expediente.md` | por el cierre del parrafo de opciones | **12/0** (aditivo puro) | **+2/+2** |
| 2. Tercera nota de la fila D-E | `RE-VERIFICACION-VCF-JEV-2026-09-28/00-expediente.md` | por la cabecera de la fila `\| **D-E** \|` | **1/1** | **+1/+1** |
| 3. «Vivas al cerrar» del §10 | el mismo del sello 1, **por su cabecera** (el sello 1 edito por encima y le movio las lineas) | `**Vivas al cerrar…` | (va en los 12/0) | (cuenta en el +2/+2) |

Controles de los tres, medidos en disco contra `HEAD` (crudo `08b-`):

- **CR=0** en los dos archivos, en `HEAD` y en disco.
- **Marcadores pareados**: en crudo, E1 pasa de `2/2` a `4/4` (balance 0 en los dos lados) y E2 de `8/6` a `9/7`
  (balance **+2 intacto**, que es el que ya declaro la tanda anterior por las menciones literales del caracter).
  **Excluyendo codigo inline**: E1 `1/1 → 3/3` y E2 `5/5 → 6/6`. El delta de esta sesion esta pareado en los dos
  archivos y en los dos instrumentos.
- **CJK=0** en `HEAD` y en disco, en los dos archivos.
- **0 citas nuevas de cifras**: la resta de los conjuntos de cifras de la linea D-E entre `HEAD` y disco da
  **vacias** las dos direcciones (`1970 → 2625` caracteres, el `HEAD` es **prefijo literal** del disco en sus
  primeros 400 caracteres: la fila se alargo, no se reescribio). En E1 las cifras nuevas tambien son **0**.
- **Backticks**: los del texto anadido son **pares** (14 en E1, 38 en E2). Los archivos tienen lineas con backtick
  impar **preexistentes** (6 en E1, 11 en E2, iguales antes y despues de esta sesion): por eso el balance se midio
  en crudo **y** filtrando, y por eso no se fia solo el numero filtrado.
- **Ruta apuntada**: los tres sellos citan `evidence/…/REINGESTA-CONTEXT-JEV-2026-09-29/00-expediente.md`. Es la
  **unica** ruta nueva en todo el texto anadido, y resuelve (este archivo).

Lectura de «0 citas nuevas» que se declara, porque la instruccion lo pedia sin definir la unidad: se midio como
**rutas nuevas citadas por las lineas anadidas**. Sale exactamente el puntero a este expediente. Si en vez de eso
la intención fuera «ninguna cifra nueva», tambien cumple: el conteo de cifras nuevas es 0 en los dos archivos.

---

## 5. Fraudes de instrumento cazados mientras se media (declarados, no corregidos en el pasado)

1. **La clave del listado no es `items`**: el primer analisis post subio `KeyError: 'items'` y `PY_EXIT=1`. La clave
   real es `sources`. El JSON ya estaba persistido, la correccion fue del lector y el crudo del intento fallido
   queda en `06f-`. El conteo **56** no dependio del intento fallido: lo imprime tambien la tabla.
2. **`re` no admite `\u` en un patron** sin sus cuatro digitos hexadecimales: la sonda previa a la redaccion reventó
   con `PatternError: incomplete escape`. Se paso a conteo por subcadena literal.
3. **`.gitignore:20` excluye `*.log` en silencio** (la medida de la tanda anterior: 113 inventariados contra 95
   versionados). Esta sesion escribio **7** crudos con extension `.log` y los renombro a `.txt` **antes** de
   commitear; ademas se barrió la extension de los instrumentos para que un re-ejecutable no vuelva a escribirla.
   Quedan `LOG_restantes=0`.
4. **Un sello dentro de una fila de tabla no puede llevar saltos de linea**: la nota 2 se redacto envoluelta a
   ~110 caracteres y rompio la fila D-E (`numstat` 7/1, siete lineas fisicas donde debia haber una). Se colapsó con
   instrumento propio (`09-`) y se exigió identidad **salvo espacios** mas `numstat` **1/1** y **61 filas de tabla
   antes y despues**. Leccion: en una tabla, la nota nueva es **una linea larga**, no un parrafo envuelto.
5. **Fecha mal escrita en un sello**: el sello 3 salio con la cadena `2022-` + `09-29` en vez de la de hoy, y una
   disculpa dentro del texto. Se corrigio antes de publicar ninguna cifra con esa nota. Barrido del residuo
   (crudos `11-`, `16-`, `18-`, `19-`): **0** ocurrencias de esa cadena en los dos archivos sellados, **0** en
   todos los archivos de esta carpeta y **0** en `HEAD` (`git grep -c` con exit **1**, que es la forma de un cero
   verdadero). Para que el barrido no se autocontamine, aqui la cadena esta escrita partida. Y el `numstat` 12/0 de
   `08b-` ya es del archivo corregido.
6. **Un cero de instrumento roto, no de medida** (crudo `18-` contra `17-`): el cierre contaba los marcadores del
   expediente nuevo con `grep -o "$AP"`, donde `$AP` salia de un `python -c` que **imprime** el caracter. Bajo
   cp1252 ese print reventa, la variable queda vacia y el conteo publica **0/0**. Los dos ceros eran falsos: medido
   en UTF-8 dentro del propio Python, el expediente lleva **1 apertura y 1 cierre** (balance 0), los dos citando la
   forma de la casa dentro de codigo inline. Leccion de la casa, otra vez y en carne propia: **la salida de un
   instrumento que revienta no es una medida** — y el `EXIT_RUN=0` del envoltorio no lo aviso, porque el fallo fue
   dentro de una sustitucion de comando.

---

## 6. Leccion sistémica (la que pide la orden, escrita aqui)

**Un archivado vence tambien los `CONTEXT` ya publicados, no solo los `10-analisis`.** El `git mv` de D-c movio el
segmento `Archives/` dentro de una ruta que un `CONTEXT` citaba, y con eso dejó vencida una fuente que ningun
mandato de cierre miraba. Dos consecuencias operativas:

1. `validate_qmind_writeback.py` **no** audita los `CONTEXT`: su poblacion son los `10-analisis` archivados. Por
   eso el verde de `13/13` convivio nueve dias con un `CONTEXT` vencido sin decir nada. Un verificador que audita
   una familia de artefactos no audita la carpeta donde esa familia vive.
2. El disparador de la vencidez **no es una edicion del documento**, es una edicion de la **ruta** que el documento
   menciona. Mientras no exista un verificador que baje los `CONTEXT` y los contraste por descarga + sha256, la
   poblacion de «que esta vencido» solo se conoce midiendo, y medir es caro: aqui fueron dos escrituras externas
   (esta y la de la tanda anterior) para descubrirlo en la segunda.

Deuda que esto **no** toma (queda para quien la asigne): un verificador de frescura de `CONTEXT` por descarga +
sha256, con su propia poblacion. No se invento un ID de deuda aqui porque la orden lo prohibe sin censo previo.

---

## 7. Estado del notebook al cerrar, y lo que sigue vencido

- **56** fuentes. La anterior `01a0e4d9-…` sigue publicada y **sigue vencida** (`04242f49…`): esta orden no borra.
- La nueva `01a0efcc-…` casa con el disco (`5587f27d…`, delta 0).
- **No se busco ni curo ninguna otra divergencia**: la orden lo prohibe. El Paso 0 midio las cinco fuentes que
  nombro el parte anterior y nada mas; si hay otro snapshot vencido, no fue medido en esta tanda.

---

## 8. El pipeline de cierre, en el orden de la casa

| Paso | Comando | Resultado medido (crudo) |
|---|---|---|
| Write-back estricto | `python scripts/validate_qmind_writeback.py --strict` | **`EXIT=0`**, `[PASS] QMind Write-back: 13/13 10-analisis archivados ingested en 'iah-cli-lecciones'` (`12-`). El `CONTEXT` **no movio la cuenta**: sigue en 13 porque el verificador no lo mira (§6) |
| Packs | `python scripts/build_phase_briefing.py --plan Archives/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20 --check` | **`EXIT=0`**, cinco filas `[OK] … fuentes frescas y proyeccion del workflow conforme` (`13a-`). **No se regenero nada** |
| Indice de lecciones | `python scripts/build_lesson_index.py --check` | **`EXIT=0`**, `[OK] Índice de lecciones fresco (340 IDs)`, `[fechas] nombre=329 commit=11 sin_fuente=0` (`13b-`) |
| Validaciones rapidas | `python scripts/run_all_validations.py --quick` | **`EXIT_QUICK=0`**, `TOTAL: 13/13 validations passed`, `STATUS: ALL VALIDATIONS PASSED`, con la `[GUARDA]` del denominador por modo (`14a-`) |
| Coherencia documental | `python scripts/validate_document_integration.py` | **`EXIT_DOC=0`**, `RESULT: All checks passed`, version 4.78.0 alineada y seis archivos en `LF` con estado Git LIMPIO (`14b-`). Se compruebo **antes** de correrlo que solo abre un archivo en lectura (`:529`, sin modo `w`) |
| Gate del arbol | `git diff --check` | **`EXIT_DIFF_CHECK=0`**, salida **vacia** (`15a-`) |
| Reconfirmacion final, despues de escribir todo | `qmind source download 01a0efcc-… --nb 01a04d98-…` + `sha256sum` contra el disco | **`EXIT_DESCARGA=0`**, 17.272 B / `5587f27d…` en los dos lados y **`DIFF_EXIT=0`** (`17-`): la fuente publicada casa con el disco, o sea la divergence quedo **CERRADA** y sigue cerrada al ultimo instante de la tanda |
| Estado del arbol | `git status --porcelain` / `-uno` | **3** / **2** lineas (`15b-`, `15c-`): los dos expedientes sellados (`M`) y esta carpeta (`??/`) |

Dos cosas que el verde **no** avala, declaradas:

- El quick mide el arbol de `HEAD`, asi que su `13/13` no certifica lo que esta sesion escribio sin commitear. Lo
  que si certifica es que **no rompio nada de lo versionado**, y eso tambien es resultado.
- **Ninguna bateria pytest se corrio en esta tanda**: el pipeline que fija la orden nombra seis comandos y pytest
  no esta entre ellos, asi que no estaba autorizado. La regresion de `tests/` queda **no ejecutada**. Su
  antecedente vigente es el de la decimocuarta sesion, en otro expediente: `3 failed, 4642 passed, 41 skipped,
  4 xfailed` con los tres nombres del baseline (los crudos `19-t3-pytest-82.txt`, `22-t4-modo-completo.txt` y
  `24-t4b-suite-completa.txt` en `RE-VEREDICTO-VCF-JEV-2026-09-29/`). Esta tanda no toco codigo ni tests, solo
  evidencia y dos notas datadas, asi que no hay mecanismo por el que un rojo nuevo pueda venir de aqui; pero **no
  se midio**, y esa es la diferencia con haberlo comprobado.
- El `Secrets Check` del quick barre `1361 tracked files + staged`. Esta carpeta esta **sin versionar**, o sea que
  el gate de secretos de la casa todavia no la vio: por eso el barrido propio de credenciales se corrio con
  instrumento propio y no se delego en el verde. Medido sobre **todos** los archivos de la carpeta al cerrar
  (`m-15`, crudos `18-` y `19-`): forma **0**, control ancho **0**, CJK **0**, `.log` **0**. El denominador no se
  publica como cifra: era **69** con `18-` en disco y **70** con `19-`, y cada crudo que se añade suma uno. Lo que
  se afirma son los cuatro ceros, que son invariantes del contenido y no del conteo.

Los cinco cortes terminan en **espera de autorizacion**: implementacion terminada (T1 + tres sellos), verificacion
terminada (§1 a §5 y §8), cierre documental (§4, los sellos apuntando a este expediente), listo para revision
(arbol con **3** lineas y pipeline en verde) y **espera de autorizacion**. El `git commit` no es condicion de
ninguno de los cinco: es una accion posterior, separada y con autorizacion explicita. El push se pregunta aparte.

El `Plan Citations` del quick cerro con **`743 citas historicas, 0 nuevas y 0 crecimientos`**, que es el instrumento
de la casa para la cuarta letra del control de sellos («0 citas nuevas») y coincide con la resta propia de `10-`:
la unica ruta nueva que citan las tres notas es este expediente.

---

## 9. Lo que queda vivo al cerrar esta tanda

- La fuente anterior `01a0e4d9-…` **sigue publicada y sigue vencida**, por decision del operador (esta orden no
  borra). El notebook queda en **56** con la forma original + cierre.
- El verificador de frescura de `CONTEXT` por descarga + sha256 **no existe** (§6). Esta tanda lo mide a mano dos
  veces; la siguiente no tiene por que.
- `D-B`, `D-D`, `D-F5`, el dueño de `S14`, `D3`, `D6`, `D7`, `S10`, `S19(d)` y las fases `B`/`C`/`RELEASE` de JEV:
  **ninguna** fue tocada ni tomada por esta sesion.
- El `CONTEXT` de VCF y cualquier otro snapshot del notebook: **no medidos** en esta tanda (la orden lo prohibe sin
  instruccion nueva). Que no se midio no es que este fresco.

---

## 10. Indice de crudos, para quien tenga que reproducir una medida

El inventario completo lo imprime `ls` de esta carpeta; aqui va la **funcion** de cada tallo, agrupada. Los
stderr van en su propio tallo porque el `EXIT` se captura sin tuberia y la salida y el error no se mezclan.

| Tallo | Que guarda |
|---|---|
| `00-` | precondiciones de git (status, `rev-parse`, paridad) y la medida del archivo en disco |
| `01-`, `01b-` | re-medicion de la divergence por descarga + sha256, y la salida del `source download` |
| `02-`, `02b-`, `02c-`, `02d-`, `02e-` | listado PRE en JSON, sus dos stderr, la tabla (la linea `Total: 55`) y el resumen con los `EXIT` |
| `02f-` | control anti-gemelo PRE: **1** coincidencia del stem, **0** titulos repetidos |
| `03-`, `03a-`, `03b-` | el upload en si (stdout JSON), su pre con el sha local, y su stderr |
| `04-`, `04a-` | extraccion de la id nueva por campos sin credencial, y la id persistida para los pasos siguientes |
| `05-`, `05a-`, `05b-`, `05-get-…json` | espera a `ready` con su `EXIT_GET`, la verificacion por descarga, el stderr de la descarga y el `source get` |
| `06-`, `06b-`, `06c-`, `06d-`, `06e-`, `06f-` | listado POST en JSON, sus stderr, la tabla (`Total: 56`), el resumen y **el intento fallido** (`KeyError: 'items'`, §5.1) |
| `07-`, `07a-`, `07b-` | sonda previa de credenciales, la redaccion con sus conteos, y el control ancho post |
| `08-`, `08b-`, `09-`, `10-` | controles de los tres sellos (antes y despues del colapso), el colapso de la fila D-E, y la resta de cifras con la resolucion de la ruta apuntada |
| `11-`, `16-`, `18-`, `19-`, `21-` | barridos de residuo y fuga (fecha mala, CJK, `.log`, credenciales), repetidos a medida que la carpeta crecia; `17-` guarda el **cero falso** que `18-` rectifica |
| `12-`, `13-`, `13a-`, `13b-` | `--strict`, el resumen del paso 1-3 del pipeline, packs `--check` e indice `--check` |
| `14a-`, `14b-`, `15-`, `15a-`, `15b-`, `15c-` | el quick completo, la integracion documental, el resumen del paso 4-5, `git diff --check` y los dos `git status` |
| `17b-`, `17c-` | la reconfirmacion final de la fuente publicada y su stderr |
| `20-`, `22-`, `22a-`, `22b-`, `22c-` | re-pasadas de los controles de sellos y del cierre (numstat, `diff --check`, porcelain, `rev-parse HEAD`) |
| `23-`, `24-`, `25-`, `26-` | las pasadas del verificador de citas del propio expediente: `23-`/`24-` son el **predicado equivocado** (§11), `25-` es la version corregida con **0 citas rotas**, y `26-` re-mide el indice despues de escribirlo |
| `27-`, `27a-`…`27f-` | la pasada final de los cuatro controles juntos (barrido, citas, sellos y arbol), cada uno en su archivo para no mezclar stdout con stderr |

**Regla para lo que venga despues de esta fila**: cualquier tallo nuevo es una **re-pasada de un control ya
nombrado arriba**, no un control nuevo. El verificador de citas (`m-17`) lo mide y siempre queda un residuo de uno:
el crudo que esta corrida todavia no ha escrito. Es el precio de que el inventario se lea con el mismo instrumento
que lista, y por eso se declara en vez de esconderse.

El ultimo crudo de cada pasada **no puede nombrarse a si mismo antes de existir**: el renglon que lo menciona se
escribe sabiendo que ese archivo lo va a medir. `25-` no estaba en la tabla cuando `25-` se corrio, y `26-` no
estaba cuando `25-` la redacto. Es el unico auto-referente del expediente y esta declarado aqui en vez de fingir
que el inventario se vio entero.

---

## 11. Un predicado equivocado, cazado por su propio residuo

El primer verificador de citas (`23-`, re-corrido en `24-`) barraba **todo token entre backticks con forma
`NN-…`** y lo buscaba en la carpeta. Devolvio **7 «rutas que no resuelven»** que no eran citas rotas: un id de
fuente (`01a0efcc-3297-…`), un fragmento de fecha (`09-29`), la familia de nombre `10-analisis`, dos expedientes
hermanos y un plan archivado. **El hallazgo falso delataba el predicado, no el documento.**

La version corregida (`25-`) separa las dos unidades: (1) los prefijos de crudo **locales** se contrastan con los
tallos reales de la carpeta, y (2) las rutas **de afuera** se enumeran a mano porque son finitas y nombrables
(catorce, todas `OK`). Resultado: **`citados_sin_archivo=NINGUNO`** y **`citas_rotas=0`**.

El indice de §10 se escribio para cerrar el hueco que ese recuento abria: la primera pasada dejaba
**19 tallos sin nombrar** en la prosa (los stderr, los resumenes de envoltorio y las re-pasadas de un mismo
control). Agrupados por funcion quedan **0**, salvo el auto-referente de cada corrida, y eso es lo que mide `26-`:
`citados_sin_archivo=NINGUNO`, `citas_rotas=0` y `crudos_reales_sin_nombrar=['26']`. El inventario lo imprime `ls`,
no este texto; el texto dice que no falta ninguno.

---

## 12. Los crudos salieron en CRLF y se normalizaron antes de commitear (crudo `30-`)

`git add` del stageo avisa: **43 archivos** del expediente tienen `w/crlf` y «CRLF will be replaced by LF the next
time Git touches it». La causa no es el `Write` del cliente (eso ya se sabia y se barriera con `sed` sobre cada
instrumento): es que **el stdout de Python bajo Windows traduce `\n` a `\r\n`**, y el `>` del shell guarda tal cual
lo que imprime el proceso. O sea que todos los crudos generados por un `.py` salieron con retornos, y los generados
por un bloque `{ } > archivo` de bash salieron en LF. De ahi el **43 contra 62**.

Por que se arreglo y no se dejo pasar: si el blob queda en LF y el disco en CRLF, cualquier contraste futuro entre
`git show <rev>:<ruta>` y el archivo de trabajo mide un delta que no existe (es la trampa que ya persigue la casa).
Se normalizo **por bytes con guardas**, y **las tres descargas quedan fuera a proposito**: su sha ES la evidencia
(`04242f49…`, `5587f27d…`, `5587f27d…`), asi que se re-midio despues del barrido que **no se movieron ni un byte**.
Resultado: `con_CR_despues=0`, `sin_CR_despues=105`, `archivos_reducidos=43`.

Y el instrumento que lo hizo fallo la primera vez por una razon propia: calculaba la ruta de salida desde el raiz
del repo y hacia `cd` a la carpeta **antes** de abrir el redirect, asi que el bloque ni se ejecuto
(`No such file or directory`, exit 1). Se corrigio a ruta relativa y se re-corrio; el conteo «antes» de `30-`
(43/62) es el de la pasada que si corrio, no una memoria de la que fallo.
