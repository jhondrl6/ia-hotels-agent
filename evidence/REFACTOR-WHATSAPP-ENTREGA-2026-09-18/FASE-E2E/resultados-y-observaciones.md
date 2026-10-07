# FASE-E2E — resultados y observaciones (corrida única ejecutada)

**Plan**: REFACTOR-WHATSAPP-ENTREGA-2026-09-18. **Fecha de la corrida**: 2026-10-07.
**Contador v4complete**: **1/1**, acreditado por `run_control.json` y no por la narración de la sesión (L-R.4).
**Meta de la fase** (maestro §4, AC18 re-anclado): ZIP publicado con veredicto no bloqueante y acta con causas
legibles. **Resultado observado: alcanzada.**

## 1. La corrida

| Campo | Valor medido |
|---|---|
| `estado` / `exit_code` del hijo | `FINALIZADO` / **0** |
| `attempts` | 1 |
| `pid` | 30576 |
| `creado_en` → `terminado_en` | 2026-10-07T14:32:13.721Z → 14:34:09.761Z (**116 s**) |
| `argv` | literal congelado, 11 piezas, con `--permission-mode auto` |
| `argv_sha256` | `b57488913134feb2…` |
| `source_hashes` | los 10, con el runner ya en `1efa6cd142b70e3e…` tras la re-emisión |
| Invocaciones del runner | **una** (`--spawn`); ningún lanzamiento manual del argv |

El envoltorio de shell devolvió **EXIT=1** por un `UnicodeEncodeError` del cp1252 al *imprimir* la captura en consola
(`main` de `run_once.py:1038-1040`), **después** de `preservar_resultado`. El exit code real del proceso hijo es 0 y
es el que está consignado; la diferencia es del eco de consola del runner, no de la corrida (deuda S-E2E-7).

## 2. Veredicto, gates y entrega

- `verdict`: **`APROBADO-CONDICIONAL-PENDING-ONBOARDING`** — el techo que el plan declaró certificable, y no está en
  `BLOCKING_VERDICTS`.
- `evidence_tier`: **`B+`**. La regla de primer piso se aplicó y lo capa: `first_floor_rule.reason` dice literalmente
  «evidence_tier B+ → máximo condicional», con `source_artifact` `financial_scenarios_20261007_093348.json`. El plan
  anticipó «B por defecto»; el valor medido es B+, que sigue sin ser el tier A que exigiría `APROBADO-PARA-ENTREGA`.
- `clauses_evaluated`: 6. `corrective_actions`: `[]`. `enforcement`: `enabled: true`,
  `suppressed_by_operator: false`.
- **13 gates: 11 PASSED + 2 WARNING, 0 fallidos, 0 bloqueantes.** Los dos WARNING son `asset_confidence` (2 assets
  bajo 0.7) y `pricing_compliance` (pain_ratio 0.1574 fuera del rango ideal, dentro del gate_max 0.32 del tier
  boutique). `readiness: READY_FOR_PUBLICATION`.
- `coherence_score`: **0.9172**.
- **Paquete publicado**: `v4_complete/deliveries/hotel_don_alfonso_20261007.zip`, 70.191 bytes, sha256
  `487f5800c1410b16…`, **57 entradas**. `package_evidence.suppressed: false`. No quedó cuarentena `.zip.tmp`.
- Inventario post-corrida: 70 archivos, `errores: []`, `faltantes_declarados: []` (los cinco artefactos esperados).

**El paquete se validó con instrumento, no por el conteo que declara el acta:** `zipfile.ZipFile.testzip()` devolvió
`None` (ningún miembro con error CRC), `len(namelist())` = **57** — igual que `package_evidence.member_count` —, y el
sha256 del archivo en disco (`487f5800c1410b16…`, 70.191 bytes) casa con el que publican el acta y el inventario.
**No quedó ningún `.zip.tmp` bajo `output/REFACTOR-WHATSAPP-ENTREGA-2026-09-18`**: la cuarentena de O1 se cerró en
publish y no hay paquete suprimido que reconstituir. Dentro del ZIP **no hay asset de WhatsApp**, coherente con que
la rama no se ejercitó.

**El contraste que valía la pena medir.** El baseline `output/TAREA7-2026-09-19/` mostró `READY_FOR_PUBLICATION` con
los 13 gates sin fallar **y ZIP suprimido** a la vez. Esta corrida muestra `READY_FOR_PUBLICATION` **y ZIP
publicado**. La diferencia no es del hotel ni de los gates: es la serialización de AC20.

## 3. AC20 ejercitado en flujo real (era lo que E2E certificaba)

FASE-0 cerró AC20 VERIFICADO OFFLINE sobre el acta archivada; E2E lo confirma sobre la corrida viva, en sus tres
puntos:

| Punto | Baseline 2026-09-19 | Esta corrida |
|---|---|---|
| (i) `critical_recall` en el camino fundado | `details: {}` → `VACUOUS_RECALL` CRITICAL | `value: 1.0` **y** `details: {"critical_issues_count": 3, "recall_basis": "all_critical_issues_detected"}` |
| (ii) `reviewer_reports[].findings` | conteos sin causa | los cuatro revisores con su reporte; 3 hallazgos con `description` legible |
| (iii) `package_evidence` en la rama publish | solo en supresión | presente con `suppressed: false`, `path`, `sha256` y `member_count: 57` |

## 4. Cuatro revisores

`diagnosis_reviewer` (P6.1) `OK_NO_FINDINGS`, 0 critical, recomienda APROBADO. `asset_reviewer` (P6.3/P6.4)
`OK_WITH_FINDINGS` con `P12_UNVERIFIABLE` (WARNING) y APROBADO. `alignment_reviewer` (P6.2) `OK_WITH_FINDINGS` con
`S_C4_TECHNICAL_ASSETS_TABLE` (INFO) y APROBADO. `honesty_reviewer` (P6.5) `OK_WITH_FINDINGS` con
`CG_WARNING_UNDISCLOSED` (WARNING, `cg_reference: CG-WHATSAPP-LEAD`) y recomienda **`DEVOLVER-PRUEBAS`**.

## 5. Lo que la corrida NO ejercitó (L-VUP-17, declarado sin promoverlo a SUPERADO)

- **Medición IAO del `LLMMentionChecker`: NO EJERCITADO.** La unidad crasheó y se degradó a advisory:
  `LLM Mention Checker failed: 'NoneType' object has no attribute 'lower'`. Consecuencia measurable: en el
  `audit_report` de hoy **no existe** `providers_used`, mientras que el del baseline **sí** lo tenía.
- **Rama WhatsApp: NO EJERCITADA, tal como predijo el maestro.** Registrado en stderr: `[RC1] whatsapp_button:
  ninguna brecha candidata ['whatsapp_conflict'] presente en opportunity_scores`. AC1/AC2/AC3/AC6 siguen con régimen
  OFFLINE y este intento no los toca.
- **Proveedor de LLM por unidad: no acreditable desde el artefacto.** La Tarea 3 pedía `providers_used` de cada
  unidad «no el agregado». Medido: ese campo **no es por revisor** — es un agregado que produce
  `LLMMentionChecker` (`modules/auditors/llm_mention_checker.py:49`) y se escribe una sola vez en el `audit_report`
  (`modules/auditors/v4_comprehensive.py:398`). Los cuatro `revision_*.json` nunca lo tuvieron, ni hoy ni en el
  baseline. Lo único que la evidencia muestra del proveedor es el stdout: DeepSeek como proveedor de LLM y su
  conectividad. **La premisa del prompt era falsa** (misma familia que L-V.3).

## 5b. Estado de las baterías de H después de consumir el intento (medido al cerrar)

El «**70 passed**» que se cita más arriba corresponde a la corrida **pre-spawn** (tras la re-emisión del preflight).
Re-ejecutadas **después** del spawn, las dos baterías dan **2 failed / 68 passed**, y los dos rojos son de la misma
familia: **guardas cuya premisa era «el intento todavía no está consumido»**, que el consumo legítimo de E2E acaba de
vencer.

| Test | Qué asertaba | Por qué es rojo ahora |
|---|---|---|
| `test_fase_h_intento_unico.py::test_ningun_test_de_esta_bateria_toco_el_control_productivo` | que `FASE-E2E/run_control.json` no existiera y que el directorio no tuviera `run_control*` | El control existe: lo creó el runner en el spawn autorizado |
| `test_fase_h_onboarding_procedencia.py::test_nada_de_esta_fase_creara_el_control_productivo` | `not CONTROL_PRODUCTIVO.exists()`, con el mensaje «el intento unico es de E2E: si run_control.json existe, H lo consumo» | Misma causa; el mensaje nombra la única condición que lo vuelve rojo |

**No se tocaron.** El plan prohíbe alterar aserciones para alcanzar verde, y la decisión de re-anclarlas o diferirlas
no es de esta fase sin mandato. **Propuesta de re-anclaje, sin afeitar la aserción** (precedente directo: b1 re-ancló
tres pinos cuando llegó el consentimiento): el invariante que estos tests protegen es «**esta batería no creó ni tocó
el control productivo**», y eso sigue siendo verificable sin depender de que el archivo no exista —

1. **Histórico, con revisión fija** (nunca HEAD): demostrar con `git cat-file` que en el commit de H (`6fd39c2`, o su
   padre `d571277`) la ruta `evidence/…/FASE-E2E/run_control.json` **no existía**, así que ningún commit de H pudo
   crearla.
2. **Caracterización del consumo legítimo**: si el control existe hoy, debe ser del runner — `schema
   "iah-run-control/1.0"`, `attempts == 1`, `estado` dentro del vocabulario de `run_once.ESTADOS`, y `argv_sha256`
   recomputado desde `run_once.COMANDO_CONGELADO` igual al que declara el archivo. Un control fabricado por una
   batería no pasaría esa caracterización.

**Re-anclaje EJECUTADO en esta sesión por autorización del operador** (precedente directo: b1 re-ancló tres pinos
cuando llegó el consentimiento). Las dos guardas quedaron en dos patas, con la revisión **fija** `6fd39c2` y no HEAD:

1. **Histórica:** `git cat-file -e 6fd39c2:evidence/…/FASE-E2E/run_control.json` debe **fallar** — prueba que en el
   árbol donde H cerró la reserva no existía, o sea que H no la creó. La ruta se declara por construcción
   (`RUTA_RESERVA_PRODUCTIVA`), no derivada de la constante, para que la pata siga mirando la reserva aunque el test
   caracterice una copia.
2. **Caracterización:** el control del árbol vivo debe ser del runner — `schema "iah-run-control/1.0"`,
   `attempts == 1`, `estado` dentro de `run_once.ESTADOS`, `argv == run_once.COMANDO_CONGELADO` y `argv_sha256`
   recomputado con `run_once.argv_sha256` casando con el publicado.

**Dientes medidos, no afirmados.** Se ejercitaron ambas guardas contra cinco mutantes del control y contra el control
real, **monkeypatcheando la ruta del módulo** (instrumento Scratch fuera del árbol, borrado tras la medición; su salida
queda en `dientes_reanclaje_guardas.txt`). Resultado: los dos positivos **verdes**, y **8 de 10 caen por su guarda**.
Los dos que no caen son `argv sin 'auto'` y `argv_sha roto` sobre la guarda ligera de
`test_fase_h_onboarding_procedencia.py`, que por diseño no lleva pata de argv — **cada mutante es atrapado por al
menos una de las dos guardas (5/5)**. Después de añadir el mensaje faltante a la aserción del schema, que fallaba muda.

Tras el re-anclaje: `tests/test_fase_h_intento_unico.py` + `tests/test_fase_h_onboarding_procedencia.py`
**70 passed / EXIT 0**, crudo en `tests_post_reanclaje.txt`. **0 funciones de test nuevas**: se re-escribieron 2
funciones existentes, así que la fila del registro publicada con `--tests 0` sigue siendo cierta.

**Error de mi instrumento, declarado:** la primera versión del medidor de dientes usaba `r or "*** NO CAE ***"` sobre
el string del `AssertionError`; una aserción sin mensaje produce `str(e) == ""`, que es falsy, y reportó un verde
donde sí había rojo. Corregido con una señal explícita `(cayo: bool, motivo)`. Sin esa corrección habría publicado
«schema ajeno no cae», que es falso.

## 6. El sitio vivo: la red no fue el riesgo, pero la DNS local sí es inestable

La sonda midió resolución intermitente (re-midiendo, 0/5 fetches al host `www.` resolvían) y aun así la corrida
obtuvo datos reales de la página: `site_presence_snapshot.json` registra `org_schema` con propiedades leídas del
ápice (`@id` `https://donalfonsohotel.com/#organization`), y el audit pasó por Places API con `geo_score real` y por
Booking (`HTTP 202`). Los checks de presencia de assets quedaron `site_verified: false`, `crawl: false`,
`nivel: raiz`, `presence_evidence_kind: "ninguna"`: la raiz se inspeccionó y FAQ/Hotel Schema/llms.txt efectivamente
**no existen** en el sitio. Overall confidence del audit: `estimated`.

## 7. Deuda y observaciones con dueño

| ID | Observación | Dueño |
|---|---|---|
| S-E2E-1 | El `LLMMentionChecker` cae con `'NoneType' object has no attribute 'lower'` en `llm_mention_checker.py:498`: `check_mentions` toma `result["text"]` (`:192`) sin guarda de None. Coste: se perdió la medición IAO en el **único** intento permitido | auditors / VERIFY |
| S-E2E-2 | La Tarea 3 del prompt de E2E pide `providers_used` por unidad; medido, el campo es un agregado de una sola unidad y nunca fue por revisor. Errata del texto del plan | RELEASE |
| S-E2E-3 | `honesty_reviewer` serializa sus hallazgos con clave `type`, pero la proyección del acta espera `finding_type`: el hallazgo llega al acta **sin tipo** (conserva descripción). AC20 (ii) se cumple en la causa, no en el tipo | tribunal / RELEASE |
| S-E2E-4 | El ZIP se publicó con un revisor recomendando `DEVOLVER-PRUEBAS`. No es un defecto de esta corrida: `DEVOLVER-PRUEBAS` no está en `BLOCKING_VERDICTS`. Se declara para que VERIFY lo juzgue, no se remedia | VERIFY |
| S-E2E-5 | `commercial_gates_report`: `total_cg_count` 12 contra `distinct_cg_count` 10, con `duplicate_gate_ids` `CG-OTA-NARRATIVE` y `CG-TECH-JARGON` | quality_gates |
| S-E2E-6 | ⟦**RESUELTO el 2026-10-07 por autorización del operador (opción A).** Medido: el material estaba en **un solo artefacto versionable** (`captura_stdout.txt`, 4 líneas) y en `logs/fase_e2e_v4complete.log`, gitignored por `*.log`. Se creó `captura_stdout_saneada.txt` con cabecera de procedencia (ruta, 16.931 bytes, sha `7dffa6f2…` del original, nº de reemplazos y motivo) y los 4 fragmentos sustituidos por una etiqueta descriptiva; **el diff contra el original es exactamente 4 líneas con 353/353 en ambos**. El crudo **no se tocó** —su sha sigue casando con `run_control.json`— y queda en disco **sin versionar**, como los packs `briefing/`. Queda abierto el hueco de fondo: ver S-E2E-11⟧ | cerrado en E2E; hueco de fondo a `redaction.py` |
| S-E2E-7 | El eco de consola del runner revienta con cp1252 y devuelve EXIT=1 con el hijo en 0. Cura: imprimir con codificación segura o `PYTHONIOENCODING`. La evidencia no se pierde, solo el eco | H / RELEASE |
| S-E2E-8 | `run_control.json` registra `preflight.sha256: null`: la ruta del preflight queda consignada, su integridad no | H / RELEASE |
| S-E2E-9 | Deuda heredada que esta corrida **materializó**: `cleanup_old_sessions(20)` borró las 8 sesiones declaradas en el snapshot. Quedan 2 sesiones de 2026-09-19 y 2 nuevas de hoy. El inventario con sha256 del preflight prueba que existieron; `.agent/memory/sessions/` está en `.gitignore:38`, así que el contenido **no es recuperable** (S-H6) | operador |
| S-E2E-10 | `llms.txt` se generó con marcadores PENDING: `region`, `city` y `usp`/`description` no estaban en `hotel_data` | asset_generation |
| S-E2E-11 | **El sumidero de F no cubre el material ya enmascarado:** `config_checker` imprime `valor[:4]...valor[-4:]` y esas formas **no** casan con ninguno de los patrones del verificador de secretos (medido: exigen 30+ y 20+ caracteres tras el prefijo), así que ni `redact_secrets` ni el gate las ven. Cura: redactar la forma `prefijo…sufijo` en `modules/utils/redaction.py`, o —mejor— que `config_checker` no imprima fragmentos del valor | `modules/utils/redaction.py` + `config_checker` |
| S-E2E-12 | ⟦**CERRADO el 2026-10-07 por autorización del operador:** las dos guardas se re-anclaron a revisión fija + caracterización del control, con dientes medidos (5/5 mutantes atrapados, 2 positivos verdes) y **70 passed** de nuevo. Sin funciones de test nuevas⟧ — ver §5b | cerrado en E2E |
| S-E2E-13 | `docs/GUIA_TECNICA.md:2505` (columna 557-558) lleva dos caracteres CJK `U+7ED1 U+5B9A` dentro de una frase en español. **Preexistente y ajeno a esta fase**, medido idéntico en HEAD con `git show`; no se corrigió aquí porque el asunto y el dueño son de otra sesión | RELEASE (erratas de docs) |
| S-E2E-14 | `10-analisis-post-implementacion.md` fila F-P4.5 publica un **fragmento de credencial real** (`AIzaSyDq…`, ocho caracteres). **Preexistente, idéntico en HEAD y por tanto ya publicado en el remoto**, ajeno a E2E. Medido: el patrón del gate (`AIzaSy` + 30 caracteres) **no lo caza**, así que pasa el hook sin ruido. No se editó texto de otra sesión; es hallazgo de **contenido**, no de forma — conviene reducirlo a «key Gemini local rotada» sin prefijo | operador / RELEASE |

## 8. Criterios de esta fase, declarados sin remediación

No se editó producto, umbrales, `BLOCKING_VERDICTS` ni datos para alcanzar la entrega. No se fecharon datos a hoy. No
se desactivó frescura ni se cayó a defaults. No se lanzó el argv manualmente ni dos veces. No se suprimió ni se
reconstituyó paquete. La revocación de claves sigue sin evidencia operativa (S-F6) y así constaba en el preflight.

**VERIFY no ocurre en esta sesión** y AC18 no se marca aquí: la certificación de la matriz AC1-AC20 queda para su
sesión, con esta corrida como única muestra.

## 9. Cierre documental ejecutado

Orden real y por qué se lo cuenta así:

- **Quick antes del spawn: 13/13 con EXIT 0** (medido al abrir la fase y tras la re-emisión del preflight).
- **`[9/13] Plan Citations` cayó durante el cierre** porque mis propias ediciones a los cinco documentos del plan
  introdujeron **8 citas por número de línea**. Se corrigió **convirtiendo cada cita a su símbolo**
  (`config_checker._check_env_variables`, `def _parse_mentions`, `def check_mentions`, `LLMReport.providers_used`,
  `V4AuditResult.to_dict`, `PageSpeedClient.__init__`), no con `--update-baseline`: esa bandera habría legitimado la
  violación en vez de gobernarla. Tras la conversión el verificador devolvió **EXIT 0 con `745 citas historicas, 0
  nuevas y 0 crecimientos`** y el inventario de 81 archivos quedó intacto.
- **Índice de lecciones regenerado con su escritor** (`build_lesson_index.py`): **344 IDs definidos + 82 sin
  definición**, y `--check` responde **fresco** (344 IDs).
- **`log_phase_completion.py --fase FASE-E2E --fecha 2026-10-07 --archivos-mod 18 --tests 0 --check-manual-docs`**
  ejecutado una sola vez (es aditivo: re-correrlo apilaría una fila duplicada). Respondió `Fase registrada
  exitosamente` y la auditoría documental **`No se detectaron gaps`**.
- **Desfase del conteo, declarado en lugar de escondido:** los **18** son las rutas versionables medidas con
  `git status --porcelain -uall` **antes** de invocar al escritor, excluyendo los 12 archivos de `briefing/` que este
  plan decide no versionar. **La cifra final de esta sesión es 26 versionables (38 con `briefing/`)**, construida así:
  18 al momento del registro → +2 del propio escritor (`REGISTRY.md` y su `.last_doc_phase.json`) → +1 de la captura
  saneada → +2 de los crudos del re-anclaje y de los dientes → +2 por las dos guardas editadas → +1 del sello de
  regresión. Es el mismo mecanismo que produj las erratas `--archivos-mod` de C, F y H; aquí
  se publica cada cifra con su comando y su momento. **La fila del registro quedó en `18` porque ese fue el dato
  declarado al escritor, y el escritor es aditivo: re-correrlo apilaría una fila duplicada. La corrección al 26 va al
  sello de RELEASE**, con el precedente de S-F7 y S-H11.
- **Para quien commitee:** excluir **explícitamente** `FASE-E2E/captura_stdout.txt` (el crudo con los 4 fragmentos) y
  versionar en su lugar `captura_stdout_saneada.txt`.
- **Baterías de H: 70 passed antes del spawn** (tras la re-emisión del preflight, mismo verde que antes con la misma
  selección de dos archivos) y **2 failed / 68 passed re-ejecutadas después del spawn**, con las dos guardas de
  §5b como únicos rojos: su premisa era «el intento no está consumido». **Fueron re-ancladas con autorización del
  operador y volvieron a 70 passed** — detalle y dientes medidos en §5b.
- **El quick NO cubre el `--check` del índice de lecciones.** Medido dos veces en esta sesión: tras editar los
  documentos del plan al cierre, `build_lesson_index.py --check` devolvió **EXIT 1 (`Índice de lecciones vencido`)**
  mientras `run_all_validations.py --quick` seguía respondiendo **13/13 con EXIT 0**. El check `[10/13]` es
  `validate_lesson_capitalization.py` (forma y trazabilidad del Paso 0), no la frescura del índice: la frescura la
  corta el **hook pre-commit**, no el quick. Se regeneró con su escritor y quedó **fresco (344 IDs, `--check` EXIT 0)**.
  Para quien commitee: si el hook corta, es este check, y el remedio es el escritor, no la edición a mano.
- **Quick final: 13/13 con EXIT 0** (y baterías de H **70 passed**, `--preflight` EXIT 0,
  `validate_document_integration.py` EXIT 0). El quick **no ejecuta pytest**: mientras las guardas seguían rojas, ese
  13/13 no las veía. Quien cierre el plan debe correr las baterías, no confiar en el quick.

**Dos acciones autorizadas al cerrar, ejecutadas y medidas.** (1) **Saneado de la captura (opción A, S-E2E-6):**
`captura_stdout_saneada.txt` con cabecera de procedencia, 4 fragmentos retirados, diff exacto de 4 líneas sobre 353
en ambos lados, crudo intacto (sha verificado) y sin versionar. (2) **Re-anclaje de las dos guardas (S-E2E-12):**
revisión fija + caracterización, **70 passed** de nuevo, dientes medidos contra cinco mutantes con 5/5 atrapados entre
las dos guardas (`dientes_reanclaje_guardas.txt`, `tests_post_reanclaje.txt`).

**Lo que esas autorizaciones NO cubren:** S-E2E-11 — redactar la forma `prefijo…sufijo` en el sumidero o dejar de
imprimir fragmentos en `config_checker` — es **código de producto**, y la fase declara «sin edición de código de
producto». **Sigue abierto con dueño** en vez de amplificar el alcance en silencio.

**Publicación:** esta fase se commitea y se empuja en la tanda que el operador ordenó el 2026-10-07 con la instrucción
literal «Commit + L3 + Push con esa exclusión», donde la exclusión es `captura_stdout.txt`. **El sha del commit y el
rango empujado no se estampan aquí**: viajan al sello de RELEASE, con los precedentes de C, D, E, F y H (un sello que
documenta una acción git es a su vez una acción git, y esa recursividad se aplazó por decisión del operador).
**Sigue sin autorización y sin hacer:** tag, write-back a QMind, regeneración de `DOMAIN_PRIMER` y rotación de
credenciales. **AC18 no se marca en esta fase**: certifica VERIFY en su sesión, con esta corrida como única muestra.

⟦**Sello añadido después del push, 2026-10-07.** La frase de arriba prometía que el sha y el rango no se estampaban
aquí; el propio operador pidió sellarlos en una tanda posterior, así que quedan consignados y esa promesa se da por
cumplida en otro documento, no aquí. **Commit `b05e620`** (25 archivos, +2.431/−49, 8/8 checks del pre-commit sin
saltar, `git commit -F`). **L3 sobre el commit sin revisar: sin hallazgos.** **Push `6fd39c2..b05e620`**, remoto
verificado en `b05e6201c751386c…` con `git ls-remote` y paridad **0/0** en las dos direcciones. La verificación de la
exclusión se hizo contra **el árbol del commit** (`git ls-tree -r b05e620`): `captura_stdout.txt` count **0**,
`captura_stdout_saneada.txt` count **1**, y `git ls-files` confirma que el crudo no se trackea — el primer intento de
probarlo con `git show --name-only` contó la mención del propio mensaje del commit, no la lista de archivos. Este sello
no reabre recursividad porque estampa hechos ya publicados⟧.

## 10. Sello de regresión completa (por haber tocado dos archivos de test)

**1 failed / 5.134 passed / 41 skipped / 4 xfailed en 392,32 s (EXIT 1)** — crudo en
`tests_postfull_regresion.txt`, con su línea `EXIT=` escrita **dentro** del comando: la notificación del segundo plano
informa el código de la cadena shell, no el de pytest, y sin esa línea el verde sería una suposición.

El único rojo es **el ajeno y dependiente del orden** de siempre:
`test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic`, que
**pasa 15/15 aislado con EXIT 0** — el mismo comportamiento que documentaron C, D, F y H, con dueño en el piloto JEV y
sin relación con esta fase. **Nada de lo que esta sesión tocó aparece en la lista de rojos**, incluidas las dos
guardas re-ancladas, que pasaron **dentro del suite completo** y no solo aisladas.

**Reconciliación de denominadores, porque el relato previo del plan mezclaba unidades.** Con el método canónico
(`grep -rE "^\s*def test_" tests --include=*.py`): **5.040 en `1c20695` → 5.045 en `d571277` → 5.049 en `6fd39c2`** y
también 5.049 en el árbol vivo. Desde el cierre de H son **+9 funciones, no +12**: b1 añadió **5 funciones que producen
8 casos** (un `@pytest.mark.parametrize` aporta 3) y b1-bis **4 funciones / 4 casos**. Las baterías de H son hoy
**67 funciones / 70 casos** — `test_fase_h_intento_unico.py` 38 funciones y 41 casos,
`test_fase_h_onboarding_procedencia.py` 29 y 29 —, así que el «**70 passed**» que se cita en esta fase es **conteo de
casos**; la cifra de funciones es 67. El re-anclaje no cambió ninguna de las dos: transformó 2 funciones existentes.

## 11. Estado final entregado a VERIFY

- **Contador 1/1 consumido**, acreditado por `run_control.json`; no hay segunda corrida posible.
- **Entrega**: `hotel_don_alfonso_20261007.zip`, 70.191 bytes, sha `487f5800…`, 57 miembros, `testzip()` sin errores.
- **Evidencia de la fase**: **11 archivos en `FASE-E2E/`**, de los cuales **10 son versionables** — el undécimo es
  `captura_stdout.txt`, el crudo con los 4 fragmentos, que queda en disco **sin versionar** por S-E2E-6. Son: informe,
  preflight verificado, `run_control.json`, inventario post-corrida, `captura_stderr.txt`,
  `captura_stdout_saneada.txt`, `spawn_crudo.txt`, `tests_post_reanclaje.txt`, `dientes_reanclaje_guardas.txt` y el
  sello de regresión.
- **Un hallazgo preexistente, ajeno a esta fase, declarado en vez de corregido en silencio:** `docs/GUIA_TECNICA.md`
  línea 2505 lleva dos caracteres CJK (`U+7ED1 U+5B9A`) incrustados en una frase sobre el gobierno por tipo. Medido con
  `git show HEAD:…`: **idénticos en HEAD**, así que no los produjo E2E y **no se editan aquí** (son de otro asunto y
  otro dueño). Se registra como S-E2E-13 para el sello de RELEASE.
- **Abierto con dueño**: S-E2E-1 (el crash del `LLMMentionChecker`, que costó la medición IAO del único intento),
  S-E2E-2 a S-E2E-5, **S-E2E-11** (el sumidero no ve los valores ya enmascarados — es código de producto y no estaba
  autorizado aquí) y la errata de conteo **18 → 26** para el sello de RELEASE.
- **Sin hacer por falta de autorización**: tag, QMind write-back, `DOMAIN_PRIMER` y rotación de credenciales.
  **Commit, L3 y push sí están en la orden literal del operador del 2026-10-07**, con `captura_stdout.txt` excluido del
  versionado y el sha/rango al sello de RELEASE.
