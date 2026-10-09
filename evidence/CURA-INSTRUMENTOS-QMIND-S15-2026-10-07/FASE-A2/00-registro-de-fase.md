# Registro de fase — FASE-A2 (CURA-INSTRUMENTOS-QMIND-S15-2026-10-07)

**Sesión:** 2026-10-08 · **Rol:** ejecutor de FASE-A2 (AC3 y AC4), plan de ejecución DIRECTA.
**HEAD medido al abrir:** `git rev-parse HEAD` = `083e6ab204b5d56d682224db761ed80bccb47b52`.
**Paridad al abrir:** `git ls-remote origin refs/heads/master` = `083e6ab…` = HEAD (medido, no de memoria).
**Árbol al abrir:** `git status --porcelain -uall` = 13 rutas untracked **ajenas** (12 `briefing/FASE-*.md` del plan
padre archivado y `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`), excluidas de toda
acción y de todo conteo (maestro §5 S-CIM-7). Cero rutas modificadas.
**Quick de apertura:** el de la sesión anterior quedó archividado por la enmienda; esta fase no repitió el quick de
apertura y corrió el suyo al cerrar (`quick_cierre.txt`).

## Línea base re-medida, no heredada

| Punto | Cifra del mandato al dictar el prompt | Medido en esta sesión | Consecuencia |
|---|---|---|---|
| tip publicado | `083e6ab` | `083e6ab` por `git ls-remote` y por `git rev-parse HEAD` | coincide; la cláusula del prompt («el tip vigente lo imprime `git ls-remote`, nunca ese párrafo») se respetó |
| commits desde `58dc034` sin revisión profunda | **8** | `git rev-list --count 58dc034..HEAD` = **8** | la L3 de esta sesión cubre ese rango (tarea 1) |
| funciones `def test_` en la selección literal de A2 | 31 | `git grep -c -E "^\s*def test_" HEAD -- tests/test_validate_qmind_writeback_escritura.py` = **31** | PRE de la fase |
| rutas en `instantaneas/` | 2 (`README.md` + 1 archivo de datos) | `ls -1 .opencode/qmind-writeback/instantaneas/` = **2** | la fase prueba colisiones en montaje aislado; el directorio real no crece |
| banda de la enmienda `67b7e2f..083e6ab` | 14 modificadas + 11 nuevas = 25 rutas, 0 renombradas, 0 en `tests/` ni `scripts/` | `git diff --name-status 67b7e2f..083e6ab` reproduce **exactamente** esa medida (`mod=14 nuevas=11 ren=0 tests=0 scripts=0 total=25`) | la fila de REGISTRY de la enmienda se escribe con la medida propia, que casa con la del mandato |

## L3 antes del primer commit (tarea 1)

Corrida con la herramienta de revisión profunda sobre el baseline real que dejó la sesión de la enmienda:
**rango `58dc034..083e6ab`, 8 commits, sin hallazgos**. No se reporta como «tanda anterior ya revisada»: el rango
es lo que la corrida cubrió, y es la cobertura que la enmienda no pudo obtener dentro de su propia sesión (L-CIM.4).

**Límite declarado:** el stdout de la herramienta de revisión **no se archiva** — su política interna impide
persistir identificadores, estadísticas ni mecánica del escáner. Lo que esta acta publica es el rango cubierto y el
conteo de hallazgos, no un crudo. Es una desviación del patrón «todo verde con su crudo» y se declara en vez de
simular el archivo.

## Alta en REGISTRY de la FASE-ENMIENDA (tarea 2, mandato del operador)

Escrita por su único escritor, en el orden prescrito (**antes** que la fila de A2):

```
venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-ENMIENDA --fecha 2026-10-08 \
  --desc "CURA-INSTRUMENTOS-QMIND-S15: registro tardio de la enmienda documental (DA-CIM.9, DA-CIM.10 y reglas c2)" \
  --archivos-mod 14 --archivos-nuevos 11 --tests 0 --nota "…registro tardio…unidad…cero escrituras remotas…L3…"
```

- **`--dry-run` leído antes de escribir** (crudo `registry_fase_enmienda.txt` para la corrida real; el dry-run
  imprimió `| \`11\` | NUEVO | 11 |`, `| \`14\` | 14 |` y `- [ ] Tests: 0`).
- **`--plan` NO se pasó:** la cabecera `## FASE-ENMIENDA - 2026-10-08` no existía en REGISTRY y FASE-A1 se registró
  sin ella; mantener la forma es parte de la coherencia del registro.
- **Conteos, no listas**, en `--archivos-mod`/`--archivos-nuevos`, igual que A1: el escritor renderiza cada token
  como una fila de tabla. La unidad viaja en `--nota`.
- **Efecto colateral versionado y leído, no asumido:** el escritor tocó `docs/contributing/.last_doc_phase.json`,
  que estaba limpio (`git status --porcelain` sobre la ruta, vacío al abrir). El diff muestra que el marker ganó la
  clave literal `"14": "FASE-ENMIENDA"` — es decir **afirma una sección que no es una ruta del árbol**, la predicción
  del mandato se cumplió por el conteo renderizado como ruta. Viaja en el mismo commit que la fila.
- **Cabecera movida por el instrumento:** `> **Total fases completadas:**` pasó de **516 a 517** con la fila de la
  enmienda y a **518** con la de A2; `> **Ultima actualizacion:**` queda en la fecha de la última entrada escrita
  (A2), que es la prueba de que el orden de la tarea 2.e no se rompió.

## AC3 landed: nombre de instantánea con huella (tarea 4)

**Qué cambió en el emisor.** `registrar_publicacion()` ya no arma el nombre in situ: llama a
`slug_de_instantanea(plan, titulo, sha)`, que devuelve `<plan>--<título-saneado>--<huella>.md` con la huella
(`sha[:HUELLA_INSTANEA]`, 16 hexádigitos) **reservada desde el final** del presupuesto `NOMBRE_INSTANEA_MAXIMO`
(120): el recorte cae siempre sobre el prefijo, nunca sobre la firma. El `sha256` que entra al registro se calcula
sobre el archivo de origen y no sobre el destino; son el mismo número porque `shutil.copyfile` es byte a byte, y así
nombre y entrada derivan de un solo dato.

**Decisión de esquema registrada** en maestro §2 (`DA-CIM.11`, con su enunciado) y en
`10-analisis-post-implementacion.md` §Decisiones Arquitectónicas (su definición canónica, rationale y alternativas
rechazadas), porque define lo que un humano ve en `instantaneas/`.

**Prohibido por diseño y probado por diente:** ningún nombre generado puede ser `README.md` (todo nombre termina en
`--<hex>.md`), y el `README.md` del directorio sigue intacto tras publicar en el montaje.

**Verde exigido por el AC, medido en montaje aislado:** dos publicaciones del mismo plan con títulos de prefijo
común dejan dos byte-exactos y cada entrada casa con su propio archivo
(`test_dos_publicaciones_del_mismo_plan_dejan_dos_byte_exactos_distintos`); un tercer título del mismo prefijo
tampoco pisa (`test_un_tercer_titulo_de_prefijo_comun_tampoco_pisa_los_anteriores`).

## AC4 landed: `fuente_id` desde la tabla, sin re-subida (tarea 5)

**Qué cambió.** `fuente_id_de_tabla(output)` lee la tabla `Key: value` partiendo por el **primer** `:` de cada
línea, exige `clave.strip() == "ID"` (así `NotebookID:` no casa) y valida el valor contra `ID_RE`. Las dos ramas de
`do_upload()` —la explícita (`--file`/`--title`) y la histórica— llaman ahora a `publicar_en_registro()`, que
escribe el id en la entrada y, si la tabla no lo trajo, **no re-sube**: imprime
`[AVISO] id no capturado: la tabla de la subida no trae una línea 'ID:' con forma de UUID; no se re-subió nada` y
delega en `verificar_por_censo(notebook_id, titulo, sha)`, que publica uno de sus tres estados:
`[NO-EVALUABLE] censo` (lector fallido), `[AUSENTE] censo` (ausencia observada, con el título y el notebook
buscados) o `[CENSO] la fuente publicada es <id>` (coincidencia por título y `sha_metadata`).

**Contenido del fixture, declarado.** `QmindFalso` respondía `json.dumps({"id": …})` a `source upload` — una
interfaz que el CLI no tiene. Ahora responde la tabla real, con la forma copiada de la subida archivada por el
hermano (`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/SESION-SCRIPTS-CURAS-2026-09-28/39-de-subida-leccion-11.txt`),
con su alineación `Key:` + espacios y su línea `URI:` sintetizada. Ninguna aserción vieja se tocó; el cambio es de
forma del doble, y es lo que hace que el verde de AC4 sea alcanzable (L-CIM.6).

**Cero escrituras remotas en toda la fase:** `qmind` no se invocó. No hubo `source upload`, ni `source download`,
ni `source delete`, ni edición manual de `.opencode/qmind-writeback/registro.json`. Todo diente de AC4 corre sobre
tabla archivada y fixtures sintéticos en `tmp_path`.

## PRE / POST y mutantes (tareas 3, 6, 7, 8)

| Concepto | Valor | Instrumento |
|---|---|---|
| PRE | `31 passed`, `EXIT=0` | `./venv/Scripts/python.exe -m pytest tests/test_validate_qmind_writeback_escritura.py -q`, worktree en `083e6ab`, intérprete declarado dentro del crudo (`tests_baseline_pre.txt`) |
| POST | `43 passed`, `EXIT=0` | mismo comando, mismo intérprete, instrumento ya congelado (`tests_baseline_post.txt`) |
| Resta | **43 − 31 = 12** | 12 dientes de ESTA fase; una resta 0 con dientes declarados habría sido baseline contaminado (R2.7) |
| Dientes viejos | 31 verdes **sin re-bajar ninguna aserción** | `git diff -- tests/test_validate_qmind_writeback_escritura.py \| grep -c "^-.*assert"` = **0** |
| Mutantes | 5 de 5 con sensibilidad demostrada | copia aislada en `temp/mutantes_a2/mount`; par intacta(`EXIT=0`)/mutada(`EXIT≠0`) en un mismo crudo por mutante; ancla con `count(old) == 1`; **aserción que pierde** nombrada en `mutantes-resumen.txt` |
| Worktree vivo | intacto | `sha256` del script vivo `96fe9257eddb…` idéntico antes y después; `sha256` del test vivo `499fbc2725cd…` idéntico antes y después |

**Re-tomas declaradas (regla c2).** El código quedó congelado antes de abrir el cierre documental y el POST se
archivó sobre el instrumento definitivo, **una** vez. Los mutantes se corrieron **dos** veces: la primera, la
expresión `-k` de M3 llevaba la conjunción en español (`o` en lugar de `or`) y pytest salió `EXIT=4` en los dos lados
sin recolectar nada. No hubo ninguna edición de código entre las dos corridas. De esa re-toma sale L-CIM.7.

**Escritura documental (regla c2).** Los 39 reemplazos de los diez documentos del cierre los hizo **un único script
de bytes bajo `temp/`** (`cierre_a2.py`), con verificación previa (`--check`: todas las anclas con `count(old) == 1`,
39 de 39) y recuento impreso por ruta y por etiqueta; se borra al terminar. Tres anclas no casaron a la primera por
envoltura de línea y dos palabras (`09-E-tests`, `maestro-2-intro`, `readme-por-que-id`) y se corrigieron sobre el
propio arnés, **sin tocar los documentos** hasta tener las 39 anclas verificadas.

## Lo que NO se corrió, con su motivo

- **`scripts/doctor.py --regenerate-domain-primer`** — no está entre los derivados que el mandato de esta sesión
  enumera para el cierre (tarea 9). El contrato §Cierre paso 6 lo pide «con su mandato para escribir el derivado; si
  no lo tiene, se declara el checkpoint»: **checkpoint declarado**. A2 no añade ni quita módulos.
- **`scripts/validate_opencode_refs.py --fix`** — no entraron rutas **nuevas** bajo `.opencode/`: se editaron
  archivos existentes (`instantaneas/README.md` y los documentos del plan). La evidencia nueva vive bajo
  `evidence/`, que no es `.opencode/`.
- **`scripts/validate_wiring.py --write-report`** — no entraron archivos `.py` **nuevos** al árbol versionado (se
  editaron dos existentes). El `--check` del quick manda y quedó verde con su denominador impreso.
- **`scripts/validate_plan_citations.py --update-baseline`** — la corrida imprime
  `745 citas historicas, 0 nuevas y 0 crecimientos (81 archivos en el inventario)`; sin citas nuevas no hay acto
  visible que simular.
- **Ninguna operación remota sobre QMind** (ver arriba).

## Estado de los cinco cortes y desviaciones

Implementación terminada → verificación terminada → cierre documental → **listo para revisión** → **espera de
autorización**. El `git commit` no es el quinto corte ni condición de ninguno: **el árbol queda sin commitear**
porque el mandato lista autorizaciones explícitas para L3, REGISTRY y `docs/GUIA_TECNICA.md`, y para commit no hay
instrucción literal en el chat de esta sesión. Se declara en vez de suponerla.

**Desviación medida sobre un atributo del mandato.** El atributo pedía
`git diff --name-only <tip-al-abrir>..HEAD -- .opencode/qmind-writeback/` **vacío**. Imprime **1** ruta:
`.opencode/qmind-writeback/instantaneas/README.md`. Motivo y dueño: la tabla de conflictos de
`dependencias-fases.md` asigna ese archivo a A2 («una de las dos lo re-escribe»), la checklist de la fase exige que
«el `README.md` de `instantaneas/` describe el esquema de nombres vigente», y L-G3 manda que la prosa de un contrato
viaje con su cambio. Lo que el atributo gobierna —el **registro**— sí quedó intacto:
`git diff --name-only <tip>..HEAD -- .opencode/qmind-writeback/registro.json` está **vacío** y
`ls -1 .opencode/qmind-writeback/instantaneas/ | wc -l` sigue siendo **2**. La re-ancora del atributo (directorio
completo vs. registro) es decisión del operador, no de esta sesión.

## Auto-reporte de presupuesto

**Unidad declarada:** `tool_use` **contados a mano sobre las llamadas de esta sesión** (una llamada = 1; los bloques
paralelos cuentan por llamada individual). El instrumento canónico `evidence/FASE-D/measure_iterations.py` sigue
**FUERA DE SERVICIO** (R2.1): pide el transcript del cliente y su acceso está denegado; no se reintentó. Este número
**no es comparable** con las mediciones hechas con ese instrumento.

**Referencia aplicada:** **90 `tool_use`** (DA-CIM.10, contrato §R2).

**Medido al cerrar:** ≈**80** `tool_use` (la cuenta crecio al medir los atributos: dos corridas se fueron en un patron de grep que se autocazaba y en verificar que el injerto CJK era viejo). Dónde se fueron:

| Partida | Aprox. | Procedencia medida |
|---|---|---|
| Lectura de línea base y del contrato | ≈13 | siete documentos del plan, el acta de la enmienda, los crudos del padre y la superficie del emisor |
| Delegación read-only y su re-medición | ≈3 | un agente `Explore` (inventarios de símbolos, dientes por AC, estado de `instantaneas/`) y las verificaciones que el contrato exige sobre lo que devuelve |
| L3 y alta de REGISTRY | ≈8 | resolución de disponibilidad, corrida de la revisión, medida de la banda, firma del escritor, `--dry-run`, corrida real y lectura del marker |
| Código y dientes de AC3/AC4 | ≈18 | ediciones sobre `registrar_publicacion()`, `slug_de_instantanea()`, `fuente_id_de_tabla()`, `verificar_por_censo()`, `publicar_en_registro()` y las dos ramas de `do_upload()`; forma del doble; doce dientes nuevos |
| Mutantes | ≈8 | arnés, control de viabilidad del montaje, dos corridas y extracción de la aserción que pierde |
| Verificacion final, atributos y sus erratas | ≈12 | el bloque de atributos, el barrido de codepoints, la procedencia del injerto en el blob de HEAD y dos re-escrituras del patron de fuga |
| Cierre documental | ≈15 | script único de bytes (verificación de anclas, tres parches sobre el arnés, aplicación), derivados, quick, integración y acta |

**Corte usado:** hasta «listo para revisión» (no hubo autorización literal de commit; el contrato §R2 dice que ese
es el corte normal de este plan). **Sin exceso**: ≈80 contra la referencia de 90 (DA-CIM.10).

## Lecciones producidas por esta fase

`L-CIM.6` (el fixture que modela mal la interfaz del servicio hace el verde *inaccesible*, no falso) y `L-CIM.7` (el
par rojo/verde no detecta un arnés roto: lo que distingue es exigir `EXIT=0` en el lado intacto). Sus filas viven en
`10-analisis-post-implementacion.md` §Lecciones nuevas, que es su fuente; aquí solo se referencian.

## Estampa de la corrida de cierre (valores impresos por la corrida, ninguno heredado)

| Qué | Valor impreso | Comando e instrumento |
|---|---|---|
| Quick de cierre | `TOTAL: 13/13 validations passed`, `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick`; crudo `quick_cierre.txt`; árbol: el worktree sin commitear. El denominador lo publica la línea `[GUARDA]` de la corrida |
| Índice de lecciones (escritor) | `[OK] 364 IDs definidos + 93 sin definición (18 análisis, 449 .md citados)`, `[fechas] nombre=353 commit=11 sin_fuente=0`, `EXIT=0` | `venv/Scripts/python.exe scripts/build_lesson_index.py`; crudo `indice_escritor.txt`. **361 → 364**: los tres IDs nuevos de esta fase (`L-CIM.6`, `L-CIM.7`, `DA-CIM.11`) salen **definidos**, y `sin definición` no se movió en 93 |
| Índice fresco (`--check`) | `[OK] Índice de lecciones fresco (364 IDs)`, `EXIT=0` | `venv/Scripts/python.exe scripts/build_lesson_index.py --check` |
| Integración documental | `RESULT: All checks passed` | `venv/Scripts/python.exe scripts/validate_document_integration.py` |
| Citas históricas | `[OK] Plan citations: 745 citas historicas, 0 nuevas y 0 crecimientos (81 archivos en el inventario)` | `venv/Scripts/python.exe scripts/validate_plan_citations.py` |
| Fuga de enlaces firmados | 0 en todos los crudos de la fase | `grep -cE "los dos tokens de object storage que nombra el contrato §Límites (el patrón se arma por printf en el crudo, para que ningún archivo lo contenga literal y se auto cuente)" evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A2/*` |
| Censo de escrituras remotas | `qmind` no se invocó; `registro.json` intacto; `instantaneas/` en 2 rutas | `git diff --name-only 083e6ab -- .opencode/qmind-writeback/registro.json` (vacío) y `ls -1 .opencode/qmind-writeback/instantaneas/ \| wc -l` |
| Reescritura del registro | la fase no escribe el registro: todas las llamadas de `registrar_publicacion()` en la batería van por `tmp_path` | `git diff --name-only 083e6ab -- .opencode/qmind-writeback/instantaneas/` responde solo `README.md` |

**Nota de instrumento:** los crudos de consola de esta fase nacen de redirección `>` sobre stdout bajo Git Bash y
`core.autocrlf=input` los normaliza al indexar — son CRLF en disco y LF en el blob. Su sha256 se verifica con
`git show <commit>:<ruta>`, nunca sobre disco (precedente: errata de instrumento del acta de la enmienda).

## Barrido de codepoints, después de la última escritura

`unicodedata.name()` sobre todas las rutas del árbol de trabajo tocadas por la fase (`git status --porcelain
-uall` menos los 13 ajenos de S-CIM-7; el número no se fija aquí porque cada crudo nuevo añade una ruta y un
conteo fijo nace vencido) responde **2** caracteres de otro alfabeto, **ambos preexistentes y ninguno inyectado por esta sesión**:
`U+7ED1` y `U+5B9A` (CJK) sustituyen dos letras de prosa española dentro de la frase la frase que empieza con `self.<attr>` y sigue con «desde la propia clase» en `docs/GUIA_TECNICA.md` (se citan por codepoint, no por el carácter: copiarlo aquí añadiría CJK a una ruta tocada por la fase). Que son viejos se
prueba por identidad con el blob commiteado: `git show 083e6ab:docs/GUIA_TECNICA.md` los trae en la misma posición
(offset 194.436, línea 2505). **No se reparan:** el mandato autoriza en ese archivo **las dos notas de esta sesión**
y dice «ningún otro archivo de `docs/` se toca»; una errata ajena al alcance declarado no se cobra de paso. Queda
declarada con su ruta, su línea y su comando, y su dueño es el operador.

El barrido **se re-corrió después** de escribir esta sección, no antes: es la regla que la casa ya pagó («un 0 viejo
no autoriza un 0 publicado»). Crudo: `E/FASE-A2/barrido_codepoints.txt`, con la lista de rutas examinadas y el offset del blob.

## Fila de FASE-A2 y estado final del registro

Escrita **después** de los fixers derivados y **después** de la fila de la enmienda, con `git status --porcelain
-uall` como instrumento de la unidad:

| Qué | Valor | Cómo se midió |
|---|---|---|
| Rutas de la fila A2 | 16 modificadas + 13 nuevas | `git status --porcelain -uall`, excluidas las 13 ajenas (S-CIM-7); las 13 nuevas son el expediente `E/FASE-A2/**` |
| `--tests` | 12 | la resta POST − PRE de la selección literal, no un conteo de funciones |
| `--plan` | **no se pasó** | el dry-run con la bandera renderizaba `## FASE-A2 - 2026-10-08 (CURA-…)`; la fila de FASE-A1 en REGISTRY no lleva paréntesis y la forma común manda (tarea 2.d) |
| Cabecera del registro | `Total fases completadas` **516 → 517 → 518** | la movió el propio `log_phase_completion.py`: +1 con la fila de la enmienda, +1 con la de A2 |
| Orden de las filas | `## FASE-ENMIENDA - 2026-10-08` antes de `## FASE-A2 - 2026-10-08` | `grep -n "^## FASE-ENMIENDA\|^## FASE-A2" docs/contributing/REGISTRY.md` → 12034 y 12056 |
| `Ultima actualizacion` | `2026-10-08` | **el atributo no discrimina en esta sesión**: las dos entradas llevan la misma fecha, así que la prueba del orden de la tarea 2.e es la posición de las filas, no la cabecera. Se publica la medida y su límite en lugar de afirmar que la cabecera «demuestra» A2 |
| Marker versionado | ganó `"14": "FASE-ENMIENDA"` y `"16": "FASE-A2"` | `tail docs/contributing/.last_doc_phase.json` — dos claves que son **conteos renderizados como rutas**, la predicción del mandato cumplida por el instrumento |
| Quick después del escritor | `TOTAL: 13/13 validations passed`, `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick`; crudos `quick_cierre.txt` (después del escritor) y `quick_final.txt` (después del acta y de los crudos de
atributos), ambos `TOTAL: 13/13 validations passed` con `EXIT=0`; el primer quick de la fase se había tomado
antes de escribir la fila de A2 |
| Índice | `[OK] Índice de lecciones fresco (364 IDs)` | `venv/Scripts/python.exe scripts/build_lesson_index.py --check`, como último paso con su escritor |

## Atributos de cierre, con el comando que los imprime

Ejecutados sobre el árbol de trabajo (la fase **no** commiteó, así que `..HEAD` no aplica; donde el mandato pedía
`<tip-al-abrir>..HEAD` se midió `git diff 083e6ab -- …`, que es árbol de trabajo contra el tip con el que abrió la
sesión). Crudo completo: `atributos_cierre.txt`.

| Atributo | Valor impreso |
|---|---|
| `git diff --name-only 083e6ab -- .opencode/qmind-writeback/registro.json` | vacío: el registro no se tocó |
| `git diff --name-only 083e6ab -- .opencode/qmind-writeback/` | **1** ruta (`instantaneas/README.md`), desviación declarada arriba |
| `ls -1 .opencode/qmind-writeback/instantaneas/ \| wc -l` | **2** — el directorio real no creció |
| `grep -cE "los dos tokens de object storage que nombra el contrato §Límites (el patrón se arma por printf en el crudo, para que ningún archivo lo contenga literal y se auto cuente)" evidence/…/FASE-A2/*` | **0** en todos los crudos |
| `git grep -c -E "^\s*def test_" 083e6ab -- tests/test_validate_qmind_writeback_escritura.py` | **31** en el tip al abrir; **43** en el árbol de la fase (resta 12) |
| `git rev-list --count 58dc034..HEAD` | **8** commits cubiertos por la L3 de esta sesión |
| `git status --porcelain -uall \| grep -v "briefing/FASE-\|captura_stdout"` | 30 rutas de la fase, ninguna ajena: el árbol queda **sin commitear** a la espera de instrucción literal |
| `git rev-list --count origin/master..HEAD` | **0** (no hay commits locales; el push no se hizo ni se autorizó) |
| `git ls-remote origin refs/heads/master` | `083e6ab…`, igual a `git rev-parse HEAD` |
| `git grep -l "DA-CIM.9" HEAD \| wc -l` y `git grep -l "DA-CIM.10" HEAD \| wc -l` | **8** y **6** sin mover: A2 no añadió rutas con esos tokens; se verificó porque el par derivado del índice está versionado y suma rutas a cualquier `git grep -l` (L-CIM.3) |

**Errata de instrumento que esta fase cobra.** La primera corrida del atributo de fuga usó el patrón tal como
lo escribe el mandato (`grep -cE "<token>1|<token>2"`). Como el acta y el propio crudo **citaban** ese
patrón, el barrido se contó a sí mismo: 2 líneas en el acta y 1 en el crudo, con cero enlaces firmados
adentro. Es la familia que la casa ya tiene memorizada (barrido por literal que caza otra cosa). El atributo
quedó re-escrito con el patrón armado por `printf` dentro del crudo, y lo que se publica es la medida: **0**
en todas las rutas del expediente (la lista la imprime el crudo).
