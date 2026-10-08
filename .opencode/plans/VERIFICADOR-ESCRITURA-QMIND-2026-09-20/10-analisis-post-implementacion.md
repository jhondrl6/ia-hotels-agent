# 10-análisis post-implementación — VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Fase:** FASE-UNICA (momento A — entrega offline). **Fecha de cierre:** 2026-10-07.
**Versión del repo al abrir:** HEAD `21ade6c`, quick 13/13 en verde, árbol ya sucio con el cierre
documental de FASE-VERIFY del plan `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (36 entradas ajenas al abrir
esta sesión; ninguna fue tocada por esta fase salvo el prompt de RELEASE del padre, que es el entregable
de AC6-entrega).

> Estado honesto de la fase: **entregada con un AC diferido por construcción**. AC6-aceptación no puede
> cerrarse aquí porque el evento que la produce (la ingesta de cierre del padre) es posterior al
> disparador de esta sesión. Eso es resultado parcial explícito, no fracaso ni éxito integral
> (maestro §6). Ninguna operación remota se ejecutó en esta sesión: cero `source list`, cero
> `fetch_source_titles()`, cero `source upload`.

## A. Dictamen por criterio de aceptación

| AC | Veredicto | Instrumento que lo dictamina |
|---|---|---|
| AC1 | **CUMPLE** | `tests/test_validate_qmind_writeback_escritura.py` (batería de esta fase) sobre `validate_qmind_writeback.py::main` y `::do_upload`: `--title` y `--file` explícitos, `--file` fuera del repo corta por `dentro_del_repo()` antes de invocar el CLI, y `--upload <PLAN>` sin banderas publica con el título histórico idéntico al de antes (`test_el_default_de_upload_sigue_publicando_con_el_titulo_historico`). El control negativo se ejercita sobre el blob versionado en `21ade6c`: su parser moría con `--title` (exit 2 de argparse). |
| AC2 | **CUMPLE en su parte offline; su parte remota queda en el momento B** | `verificar_contenido()` compara sha de la **instantánea versionada** contra sha del cuerpo del plan y, por la vía remota, contra `metadata.fileSha256` verificado por descarga. Título coincidente con contenido distinto corta `[VENCIDO]`. Mutación M1 roja por el guard. |
| AC3 | **CUMPLE** | `main()` ya no devuelve 0 cuando falta el CLI: sin `--strict` sale **2** con `[NO-EVALUABLE]`, con `--strict` sale **1** con `[FAIL]`. `_check_qmind_writeback()` del runner lo invoca con `--strict` y trata 2 como estado propio que **no** cuenta como PASS. Mutación M2 roja: al devolver 0, la prueba objetivo pierde (`assert 0 == 2`). |
| AC4 | **CUMPLE en su parte offline; su parte remota queda en el momento B** | El registro versionado es la contabilidad de qué título está vigente y cuál `reemplazada`. Toda fuente que nombra al plan y no está contable corta `[DUPLICADO-VIGENTE]` (`test_dos_fuentes_vigentes_sin_marca_de_reemplazo_cortan`, mutación M3). La comprobación de que el marcado **llegó** al notebook es aceptación remota. |
| AC5 | **CUMPLE** | `evidence/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/mutation_report.json`: 3/3 aplicadas, 3/3 rojas por el guard, 3/3 con la aserción esperada en el rojo, 0 invalidadas por sintaxis o import, `arbol_restaurado_sin_pendencias: true` (sha256 de pre-imagen `50d1a7f8…` re-casado tras cada mutación). Instrumento: `temp/mutaciones_writeback_fase_unica.py`. |
| AC6-entrega | **CUMPLE** | `evidence/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/ac6-entrega-diff-prompt-release.txt` (es `git diff` del prompt de FASE-RELEASE del padre): el texto ahora **manda el writer** con `--file`/`--title`, resuelve la decisión marcar-vs-borrar hacia **marcar**, y declara que `[17/18]` sale NO-EVALUABLE mientras el registro no tenga entradas. Incluye la errata de símbolo: el prompt citaba `run()` del runner, que no existe; vigente `run_all()`. |
| AC6-aceptación | **DIFERIDA con dueño y disparador** | Dueño: **FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`** (momento B del maestro §6). Disparador: su ingesta de cierre por el writer con `--title`. Verificación exigida: descarga byte a byte + sha256 contra la instantánea, nunca el título. Queda declarada pendiente, no omitida. |

## B. Qué se construyó

- `scripts/validate_qmind_writeback.py` — dos capas: la de ingesta por título (vigente desde el origen,
  sobre `Archives/`) y la nueva de **contenido y vigencia** sobre el registro. Nuevas fronteras:
  `fetch_sources()` (primera vía D2), `descargar_fuente()`, `verificar_contenido()`, `cuerpo_del_plan()`,
  `dentro_del_repo()`, `registrar_publicacion()` y las banderas `--title`/`--file`/`--registro`/`--plans-dir`.
  `collect_archived_analisis()` ahora resuelve la población **bajo `--plans-dir`**: si no, el verde saldría
  del árbol real y no del montaje de la prueba.
- `scripts/run_all_validations.py::_check_qmind_writeback()` — invoca con `--strict`, nombra el estado
  `NO-EVALUABLE` y publica `VENCIDO o duplicado` en el rojo. La etiqueta `[17/18]` y la barrera
  `if not self.quick:` no cambian: lo gobiernan `test_el_check_queda_cableado_al_modo_completo_y_no_al_rapido`
  y la guarda de denominadores del propio runner.
- `.opencode/qmind-writeback/registro.json` — el registro versionado. **Nace con cero entradas y esa es la
  decisión declarada, no un olvido**: el único escritor es `--upload`, y publicar exige red autorizada.
- `tests/test_validate_qmind_writeback_escritura.py` — 23 funciones, íntegramente offline, con el doble de
  `_run_qmind` que responde `notebook list`, `source list`, `source download` **y `source upload`** (el del
  hermano no subía nada) y cuenta las bajadas para que ningún verde salga de una fuente que nunca bajó.
- `evidence/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/` — `mutation_report.json`, `mutaciones-crudo.txt`,
  `tests_baseline_post.txt` y `ac6-entrega-diff-prompt-release.txt` (la evidencia de AC6-entrega es el `git diff`
  del prompt del padre). Las premediciones de la §C salieron de las corridas de esta sesión y están transcritas
  en su tabla, con el comando que las imprime.

## C. Mediciones de la corrida (las imprime el instrumento, no la memoria)

| Medición | Valor | Cómo se obtuvo |
|---|---|---|
| Quick al abrir | 13/13 en verde | `run_all_validations.py --quick`, crudo en el output de la sesión |
| Citas de plan al abrir | 745 históricas, 0 nuevas, 0 crecimientos | `validate_plan_citations.py` |
| Índice de lecciones al abrir | fresco, 344 IDs | `build_lesson_index.py --check` |
| Firma del writer al abrir | solo `--nb`, `--strict`, `--upload` | `validate_qmind_writeback.py --help` |
| Batería al cerrar | 64 passed (23 de esta fase + 36 del hermano de frescura + 5 del denominador por modo) | `pytest -q`, crudo en `tests_baseline_post.txt` |
| Mutaciones | 3 aplicadas / 3 rojas por el guard / 3 con la aserción esperada | `temp/mutaciones_writeback_fase_unica.py` |
| sha256 pre-imagen del archivo mutado | `50d1a7f870134d96e9ae6fcf1f094524bba2396a855c09301118ca015f7a43cf` | re-casado tras cada mutación. **Es el sha del archivo tal como estaba durante la corrida de mutación**: después se retiró la constante `ARCHIVES_DIR`, que quedó sin lector al resolver la población bajo `--plans-dir`, así que quien re-mida el archivo hoy obtendrá otro sha y no un discrepancy |

**Presupuesto: FUERA DE SERVICIO (R2.1, D-V2.1).** El instrumento del contrato
(`evidence/FASE-D/measure_iterations.py <transcript> <corte-ISO>`) no recibió insumo en esta sesión, así que la
referencia de 60 **no se compara y no se estima**: aquí no se publica ninguna cifra de `tool_use`, ni medida ni
aproximada. **Se retira la estimación («~62 invocaciones») que esta sesión declaró en su mensaje de cierre**: un
número aproximado dentro de un reporte que se declara fuera de servicio es una medición falsa, y R2.1 manda no
estimar. Corte usado para el recuento: **«listo para revisión»**, que es el que estaba autorizado cuando se
declaró; la orden de commit y push llegó después, y ese trabajo (hook, L3, pre-vuelo, empuje y el sello) queda
**fuera** del recuento de arriba.

Matiz para no agrandar la leyenda: en esta sesión el instrumento **no falló ni se le denegó el insumo — no se
intentó**. D-V2.1 queda **en observación**, no confirmada por esta fase (a diferencia de P3-A/P3-B, donde el
transcript sí estuvo alcanzable y la cifra se midió, y de P5/P6-R, donde el acceso fue rechazado).

Unidad contable declarada — las tres que nombra el prompt de esta fase, enumeradas para que se recuenten sin
volver a ejecutar nada (re-correr un validador para verificar su propio conteo lo invalida):

- **Rutas tocadas:** 13 (9 editadas a mano + 4 regeneradas por su escritor). El comando, con su lista completa
  de rutas, devuelve **7 líneas `M` + 4 entradas `??`** —11, no 13—, y esa diferencia es la trampa del recuento:
  `CHANGELOG.md` y `docs/GUIA_TECNICA.md` no viven bajo las rutas del plan y hay que pasarlos explícitos, y las
  6 restantes de las 9 ya figuraban sucias en el listado de apertura (los cuatro documentos de este plan,
  CHANGELOG y GUIA_TECNICA), así que `git status` por sí solo **no** las separa del trabajo ajeno: lo que las
  distingue es aquel listado de 36 entradas medido al abrir, transcrito arriba en esta misma sección.
  De las 9 editadas a mano, **3 son nuevas para el árbol** (el writer, su conexión en `run_all_validations.py` y
  el prompt de FASE-RELEASE del padre) y las 4 entradas `??` son el `10-analisis`, `.opencode/qmind-writeback/`
  con su registro y sus instantáneas, la evidencia de la fase y la batería de tests. Las 4 regeneradas
  (REGISTRY, wiring_report, LECCIONES-INDEX y lecciones_index) ya estaban sucias al abrir y su contenido lo
  reescribió su escritor, no esta sesión.
  Comando: `git status --porcelain -- scripts/validate_qmind_writeback.py scripts/run_all_validations.py
  CHANGELOG.md docs/GUIA_TECNICA.md .opencode/qmind-writeback tests/test_validate_qmind_writeback_escritura.py
  evidence/VERIFICADOR-ESCRITURA-QMIND-2026-09-20 .opencode/plans/VERIFICADOR-ESCRITURA-QMIND-2026-09-20
  ".opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/05-prompt-inicio-sesion-fase-RELEASE.md"`.
- **Corridas con crudo conservado:** la lista nominal, no una cifra suelta — quick de arranque y tres de cierre,
  cinco de pytest y dos del harness de mutación, más los validadores documentales. Los crudos quedan en `temp/`
  (no versionado) y dos versionados en el directorio de evidencia de esta fase (`tests_baseline_post.txt` y
  `quick-cierre.txt`).
- **Mutaciones:** 3 aplicadas, 3 rojas por el guard, 3 con la aserción esperada en el rojo, árbol restaurado con
  su sha256 re-casado (`mutation_report.json`).
- **Tests nuevos:** 23 funciones, con el método canónico del repo (`grep -cE "^\s*def test_"`).

El recuento de arriba corresponde al **corte declarado**. Las corridas de esta misma rectificación (regenerar el
par del índice de lecciones porque el párrafo añade una cita a `D-V2.1`, su `--check`, el validador de citas y
un quick final) van **fuera** de ese recuento y se declaran aquí para que nadie las sume dos veces.

**Dos deltas del registro, declarados juntos** (el instrumento `log_phase_completion.py` es aditivo: re-ejecutarlo
apila una entrada duplicada, así que la diferencia se publica en vez de re-escribirse): su tabla de nuevos lista
**7** y la entrega tiene **9** —faltan `instantaneas/README.md` y el crudo del quick de cierre, que nacieron
después de registrar—; y su tabla de modificados lista **8** y la entrega editó **9** —falta
`00-lecciones-capitalizadas.md`, que se anotó después—. El registro es la foto de su momento, no el inventario.

**Divergencia de estilo declarada, para que nadie lea una errata donde hay una decisión:** el corpus tiene
declaraciones de esta misma clase que **sí** publican una cifra aproximada como unidad propia —FASE-A y FASE-F de
`REFACTOR-WHATSAPP-ENTREGA-2026-09-18` declaran «~62 intervenciones»—. Aquí no se hace: el prompt de esta fase
dice `no estimar` y su unidad es contable en disco, así que la cifra aproximada se retira y se sustituye por lo
enumerable. Las dos formas conviven en el corpus; la de esta fase es la más estricta de las dos.

## D. Decisiones tomadas en voz alta

1. **Marcar, no borrar** (maestro §4 la dejaba abierta). `registrar_publicacion()` pasa la entrada vigente
   anterior a `reemplazada` con `reemplazada_por`, y `verificar_contenido()` exige que toda fuente que
   nombra al plan esté contable. Borrar con `qmind source delete` es irreversible sobre contenido ya
   publicado y sigue pidiendo decisión escrita aparte del operador.
2. **La capa de contenido no sustituye a la de título.** La de título sigue respondiendo «¿existe ingesta?»
   sobre `Archives/`; la nueva responde «¿es el contenido que publicamos y hay una sola fuente vigente?».
   Sustituirla habría dejado a los ~40 planes archivados sin instantánea — que es la limpieza retroactiva
   que el maestro §3 declara fuera de alcance.
3. **Registro vacío = NO-EVALUABLE, no verde.** Es la regla de la casa («un verde sin candidatos no es un
   verde») y su consecuencia se publica: **el modo completo corta `[17/18]` en rojo hasta que la primera
   publicación por `--upload` registre una entrada.** No es una regresión de esta fase: es el verde hueco
   que AC3 vino a cerrar, y se apaga solo en el momento B. Esta sesión certificó el quick (que no corre
   el check) y no corrió el modo completo, que incluye pytest de producto.
4. **`--strict` conserva dientes propios:** sin él la ausencia es abstención declarada (2), con él es
   fallo (1). En ambos casos deja de ser PASS. El parámetro `strict` que `do_upload()` recibía sin usar
   se retiró con la firma nueva.

## E. Lecciones definidas por este plan (serie L-QW, reservada con Q4 del Paso 0)

- **L-QW.1 — Un verificador que comprueba la *clave* de una operación no puede detectar que el contenido
  detrás de esa clave es viejo: idempotencia y frescura son dos propiedades y aquí solo estaba la primera.**
  `is_ingested()` respondía por título, así que una fuente publicada a mitad de plan satisfacía el check para
  siempre y el `[PASS]` convivía con un cuerpo obsoleto. La cura no es «acordar un título nuevo»: es que la
  verificación compare bytes contra una instantánea versionada. Se aplicó en AC2 con M1 roja.
- **L-QW.2 — Publicar con título distinto resuelve el SKIP y *crea* el duplicado: el notebook conserva la
  versión obsoleta y el retrieve la devuelve puntuada por parecido, no por vigencia.** El residuo medido en
  P5 (dos fuentes de `TRIBUNAL-OFFLINE-2026-09-09`) no era un accidente sino la única salida que el writer
  dejaba. Con `--title` explícito hace falta el registro que marque la anterior; sin esa contabilidad el
  duplicado vuelve a ser la vía fácil. Se aplicó en AC4 con M3 roja.
- **L-QW.3 — Un verde producido por la ausencia del instrumento es un rojo disfrazado.** El `exit 0` por CLI
  ausente se publicaba como PASS en `[17/18]`; el fallback del executor (:468) estaba diseñado para
  *registrar la limitación*, no para callarla con verde. AC3 lo cierra con estado propio y M2 lo demuestra.
- **L-QW.4 — Un límite conocido y escrito no se cierra solo: la restricción estaba documentada en el corpus
  desde 2026-09-11 y se redescubrió desde cero el 2026-09-20, porque ningún AC la reclamaba y ningún check la
  violaba.** Lo que cerró el hueco no fue la nota sino el desdoblamiento AC6-entrega / AC6-aceptación con
  dueño y disparador: una pendencia sin dueño se re-descubre; una pendencia con dueño se ejecuta.

## F. Deuda y seguimientos con dueño

| # | Hallazgo | Dueño | Disparador |
|---|---|---|---|
| S-1 | AC6-aceptación: `[17/18]` verde sobre el plan padre tras su ingesta de cierre, verificada por descarga + sha256 | FASE-RELEASE de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` (momento B) | su write-back por el writer con `--title` |
| S-2 | El mismo verde por ausencia que AC3 cazó en `[17/18]` sigue vivo en `[18/18]`: `_check_context_freshness()` invoca al hermano sin `--strict` | operador / siguiente mandato sobre los verificadores QMind (maestro §3 lo declara fuera de alcance) | una AC nueva con su propio disparador |
| S-3 | La errata de símbolo `run()` → `run_all()` vive también en el `10-analisis` del padre (fila L-ENT.14), archivo sucio por el cierre de VERIFY | FASE-RELEASE del padre al tocar su `10-analisis` | esa edición |
| S-4 | Limpieza retroactiva de las dos fuentes vigentes de `TRIBUNAL-OFFLINE-2026-09-09` en el notebook | operador (decisión escrita: tocar contenido publicado) | mandato expreso |
| S-5 | `04-contrato-ejecucion.md` del padre, paso 5, sigue diciendo «acordar título nuevo antes de subir»; con el writer actualizado el título se **pasa** por bandera, no se acuerda en prosa | FASE-RELEASE del padre | su edición del contrato |
| S-6 | `DOMAIN_PRIMER` no se regeneró: esta fase no aporta contenido del dominio hotelero y el mandato de cierre del mini-plan no lo lista | FASE-RELEASE (que lo **verifica** con `doctor.py --context`) | esa fase, con instrucción expresa si quiere regenerarlo |
| S-7 | Los packs de briefing se reproducen contra el árbol de **HEAD** y esta entrega no los toca: medido, el escritor de packs **no nombra** `run_all_validations.py`, y la fuente que sí proyecta —el workflow canónico— no se editó en esta fase. **CERRADO por medición en el commit `b66d6a1`: el hook `[8/8]` reprodujo 5/5 packs contra el árbol commiteado, sin regeneración preventiva** | — (se cerró al commitear) | cumplido 2026-10-07 |

## G. Estado git de la entrega (y lo que sigue pendiente)

**Ejecutado por orden literal del operador el 2026-10-07** («Git Commit con L3 + Push»):

- **Commit `b66d6a1`** — *feat(qmind): FASE-UNICA - write-back por contenido, no por titulo*: 21 archivos,
  1.710 inserciones y 232 borrados. Los ocho checks de `.git/hooks/pre-commit` pasaron, incluido `[8/8]` (packs
  5/5 reproducidos contra el árbol commiteado) y `[6/8]` (índice de lecciones al día). Comprobación:
  `git show --stat b66d6a1`.
- **Alcance aprobado = letra A**: instrumento, batería de tests, evidencia, `.opencode/qmind-writeback/`, los
  cinco documentos de este mini-plan, el prompt de FASE-RELEASE del padre, y los derivados reescritos por su
  propio escritor (REGISTRY, `.last_doc_phase.json`, LECCIONES-INDEX con su JSON, wiring_report) con frase de
  procedencia en el mensaje.
- **Excluido por decisión del operador:** `CHANGELOG.md` y `docs/GUIA_TECNICA.md`. La subsección y la nota
  técnica de esta fase existen en disco pero **no en HEAD**: el binomio CHANGELOG↔REGISTRY queda incompleto en
  el commit y se resuelve en el commit aparte que se ofrece abajo. Quedaron fuera también los 9 archivos de
  producto y 5 de tests de la recuperación AC6/AC10, los siete documentos del plan padre y sus directorios de
  evidencia y briefing, porque no son trabajo de esta sesión.
- **L3 corrida antes del push: sin hallazgos** (`findings_count: 0` sobre los commits desde su baseline, que
  eran exactamente `21ade6c..b66d6a1`).
- **Empujado `21ade6c..b66d6a1`** a `origin/master`. Pre-vuelo medido antes de empujar: upstream
  `origin/master`, fast-forward confirmado con `git merge-base --is-ancestor origin/master HEAD`, 35 objetos
  nuevos en el rango y `git push --dry-run` con esa misma línea. Paridad después: `git status -sb` sin
  adelantamiento ni retraso.

**Sigue pendiente, con la misma regla de pedirlo por separado y con autorización literal:** el **tag** —esta
fase no libera versión: `--release` es exclusivo del RELEASE del padre y `VERSION.yaml` no se tocó— y
**cualquier operación remota a QMind**, que es el momento B (maestro §6). Los cinco cortes se sostuvieron sin
commit durante toda la sesión y el commit llegó después, por orden: ninguno quedó «no consumado».

**Ofrecido, no ejecutado:** commit aparte de `CHANGELOG.md` y `docs/GUIA_TECNICA.md`, que cargan además la prosa
ya cerrada de FASE-VERIFY de otra sesión. Mientras ese commit no exista, la clausura documental de esta fase
está completa en disco e incompleta en el histórico.

La apertura de esta sesión ya encontraba el árbol sucio con **36 entradas ajenas** (el cierre documental de
FASE-VERIFY del padre y la recuperación AC6/AC10 en curso). Esa es la razón del recorte A: lo ajeno se describió
en el mensaje del commit y se quedó en el árbol, no se absorbió. Lo que sí viaja publicado es el contenido
ajeno que es **derivado de un escritor**: `REGISTRY.md` y `.last_doc_phase.json` traen entradas de FASE-VERIFY y
FASE-E2E, y el par del índice de lecciones más `wiring_report.json` re-cuentan el corpus completo —texto ajeno
incluido, todavía sin commitear—. No es una elección de estilo: un derivado partialmente regenerado dejaría al
commit con un estado que su propio verificador no reproduce.
