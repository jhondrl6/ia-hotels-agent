# Plan maestro — CURA-INSTRUMENTOS-QMIND-S15 (creado 2026-10-07, preparación ejecutada 2026-10-08)

**Estado: DISEÑADO, SIN IMPLEMENTAR.** Preparación cerrada el 2026-10-08 contra HEAD `98c190e`; punto de
reanudación **FASE-A1**. No libera versión en esta sesión: `VERSION.yaml` publica `4.79.0` (release del plan
padre, 2026-10-07) y la versión de este plan la decide su FASE-RELEASE con mandato del operador, invocándola
como `--release "$VERSION_AUTORIZADA"`.

**Objetivo:** dejar los dos instrumentos de lecciones del repo en condiciones de decir la verdad: el
verificador de write-back de QMind (`scripts/validate_qmind_writeback.py`) debe poder dictaminar vigencia de
un plan cuyo cuerpo publicado fue **saneado** —hoy es estructuralmente imposible— y el control S15 del índice
de lecciones (`tests/test_build_lesson_index_s15_fecha_versionada.py`) debe dejar de fallar según el entorno,
sin perder el diente que lo justifica. Ninguno de los dos es cosmético: el primero gobierna el check
`[17/18]` del modo completo y la entrega documental de cada cierre; el segundo gobierna `[6/8]` del hook
versionado, o sea **cada commit**.

**Fuente de partida:** el mandato del operador del 2026-10-07 (texto de sesión nueva) más el cierre del plan
padre: `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-RELEASE/00-registro-de-fase.md` (§4 rojos, §7
erratas) y su `qmind-writeback-RELEASE.md`. Workflow canónico:
`.agents/workflows/phased_project_executor.md`. Los identificadores AC1-AC6 del mandato quedan **congelados**
con su número y su contenido; este maestro los re-valida y no los re-numera.

## 1. Revalidación del estado que traía el mandato (medido 2026-10-08, no heredado)

Ninguna fila de esta tabla es cortesía del mandato: cada una se midió en esta sesión y dos la refutan.

| Punto | Qué decía el mandato | Qué se midió el 2026-10-08 | Consecuencia para el plan |
|---|---|---|---|
| **Refutado: el tip** | «`HEAD = 83a6dc2` … 2 commits locales sin empujar; `origin/master = 649114c`» | `git rev-parse HEAD` = `98c190e`, `git rev-parse origin/master` = `98c190e` y `git ls-remote origin refs/heads/master` = `98c190e`. Hay **cuatro** commits más de los que el mandato nombra: `086ce65`, `83a6dc2`, el sello `f42c201` y el crudo `98c190e`. Árbol limpio a `-uno`; sin tag | Toda cita de estado del mandato se re-ancla a `98c190e`. El aviso del propio mandato («el tip local puede haber cambiado cuando arranques») se cumplió. Las fases re-miden HEAD al abrir: la paridad se declara por `ls-remote` y por rango empujado, no por «HEAD = origin» de memoria |
| **Refutado: el corpus del control S15** | «con `.opencode/` idéntico entre `649114c` y `086ce65` (0 rutas de diferencia)» | Entre `086ce65` y `HEAD` hay **20 rutas** de diferencia bajo `.opencode/`, y son las que FASE-B escanea: los `git mv` que archivaron el plan del padre (`plans/REFACTOR-WHATSAPP-…` → `plans/Archives/REFACTOR-WHATSAPP-…`), la regeneración del par `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json`, y `context/ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md` y `context/Refuerzo.md` | La afirmación del mandato sigue siendo cierta para el par que midió, pero **ya no describe el árbol donde FASE-B va a correr**. El control S15 clona HEAD y recorre `plans/` + `context/`: su población de dueños cambió de ruta. FASE-B no puede citar la medición del 2026-10-07 como suya: reproduce contra `98c190e` (o el HEAD de su sesión) y publica la banda |
| **Confirmado: el hueco del slug, con su forma exacta** | «registro con 2 shas, 1 archivo» | `.opencode/qmind-writeback/instantaneas/` tiene **un** archivo de datos (125.198 B) más su `README.md`, y las dos entradas del registro (`0b02bb5084e3…` y `1f0ee6e52f00…`) declaran el **mismo** nombre `instanea`. Medido por sha: el archivo en disco casa con `1f0ee6e52f00…` — o sea la segunda publicación **sobrescribió** los bytes de la primera | AC3 cierra con evidencia real, no con la hipótesis. Consecuencia que el mandato no escribía y hay que declarar: los byte-exactos de la entrada `reemplazada` **están perdidos** y no se recuperan tocando el registro; la cura solo puede garantizar que no vuelva a pasar. Y el `README.md` del directorio compite por nombre: el slug nuevo no puede producir `README.md` |
| **Confirmado: la puerta que no puede dar verde** | «`verificar_contenido()` compara sha(instantánea) contra sha(cuerpo crudo)» | Leído el símbolo: el guard es `if sha_inst != sha256_de(cuerpo):` y su mensaje nombra «el cuerpo del repo». Medidos los dos shas: crudo `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e` (124.280 B) contra publicado `1f0ee6e52f00…` (125.198 B) | AC2 parte de aquí. La diferencia de **+918 bytes** se atribuyó midiendo: el crudo no se editó después de publicar (`git show 83a6dc2`, `f42c201` y `98c190e` sobre la ruta archivada dan los mismos 124.280 B y el mismo sha), así que el delta es de las propias sustituciones del saneado, que alargan el texto. **Esto es buena noticia y hay que conservarla como pregunta medida**: con `sha_cuerpo` registrado al publicar, la fila del padre sería vigente, no vencida |
| **Nuevo, medido: el rojo de la era G está detrás del rojo de vigencia** | «al curar AC2 cortará `[DUPLICADO-VIGENTE]`» | Confirmado por flujo de control: el bloque que emite `DUPLICADO-VIGENTE` está al final del bucle por entrada y **todos los caminos anteriores terminan en `continue`**. Mientras la comparación de cuerpo corte `VENCIDO`, la fila huésped no se evalúa. Hoy `[17/18]` cortaba VENCIDO y por eso nadie vio la era G | AC6 no se puede certificar antes de AC2: su diente **depende** de la cura de A1. Es la dependencia dura del grafo (ver `dependencias-fases.md`), no una preferencia de orden |
| **Nuevo, medido: la migración no puede rellenarse hacia atrás** | «las entradas sin `sha_cuerpo` se tratan como NO-EVALUABLE» | El crudo de la fila vigente lleva desde `83a6dc2` sin moverse, así que calcular `sha(cuerpo hoy)` y escribirlo en la entrada vieja daría verde **por construcción** en este caso, y mentira en cualquier otro (un cuerpo editado antes de la primera corrida del migrador quedaría borrado de la historia) | AC1 fija la regla de migración: **ausente ≠ calculable**. El verificador que escribe pisa el pasado. Las dos entradas del padre salen `NO-EVALUABLE por instrumento` con el motivo impreso |
| **Confirmado: los 23 dientes están verdes y el S15 cae 1/4** | «los 23 de `tests/test_validate_qmind_writeback_escritura.py` deben seguir verdes»; «`test_el_control_defectuoso…` falla 2/2 determinista» | Corrida real de esta sesión, selección literal de los dos archivos: **1 failed / 26 passed**, EXIT=1 (`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/pre_seleccion_apertura.txt`). El rojo es exactamente la aserción citada por el mandato, con el mensaje impreso `assert ('mtime' == 'mtime' … mtime and 'nombre' == 'mtime' … - mtime + nombre)` | PRE de referencia para FASE-A1 (23/23 verdes en su archivo) y para FASE-B (1/4). Interpréte declarado en el crudo: Python 3.13.3 del sistema, no el venv — la selección no importa módulos del proyecto; cada fase fija su intérprete y lo publica |
| **Confirmado: el quick de apertura** | «Quick: 13/13» | `python scripts/run_all_validations.py --quick` contra `98c190e` con árbol limpio: **13/13, EXIT=0** (`…/FASE-0/quick_apertura.txt`). La etiqueta y el denominador los imprime la corrida; no se fijan aquí | La línea base de la preparación. El modo completo de la sesión que cerró el padre quedó en 15/18 con tres rojos (`Tests`, `[17/18]`, `[18/18]`) y es medición **de esa sesión**, archivada en su registro: este plan la referencia, no la re-transcribe ni la re-carga como propia |
| **Rectificado por lectura: AC5 ya funciona a medias** | «`--upload <PLAN>` resuelve contra `.opencode/plans/` y falla tras el `git mv`; con el plan bajo `Archives/` hay que aceptar `--upload Archives/<PLAN>`» | Leído `main()`: una `--upload` relativa se compone como `args.plans_dir / <argv>` **sin** exigir que exista primero, así que `Archives/<PLAN>` **sí resuelve hoy**, y `plan_dir.name` sigue dando la clave correcta del registro. Lo que no existe es el **camino inverso**: `--upload <PLAN>` a secas, tras el `git mv`, corta `[FAIL] Upload: el directorio no existe`. Y `cuerpo_del_plan()` ya prueba las dos raíces | AC5 se re-escribe como lo que es medido: **gobernar y fijar por diente** una resolución que hoy funciona por composición, no construirla. Su rojo exigido es el de la ruta equivocada (`--upload <PLAN>` con el plan archivado) y su verde el de `Archives/<PLAN>` con clave de registro intacta |

**Lectura de superficie confirmada (anclas por símbolo, todas re-visadas en esta sesión).** El sha-gate y el
segundo gate (`e["sha256"] != sha_inst`) viven en `verificar_contenido()`; el slug y la construcción de la
entrada en `registrar_publicacion()`; la entrega de `fuente_id=""` en las dos ramas de `do_upload()`; la
respuesta del CLI la devuelve `upload_source()` como `(exit_code, output)` y **nadie la parsea**; la resolución
de `--upload` está en `main()`; las dos raíces de verificación están en `cuerpo_del_plan()`; el censo de fuentes
en `fetch_sources()` (claves `id`, `title`, `sha_metadata`, `tam_metadata`; clave del listado `sources`); el
huésped no contable se emite en el bloque `DUPLICADO-VIGENTE` de `verificar_contenido()`. El consumidor es
`scripts/run_all_validations.py::_check_qmind_writeback`, invocado con `--strict` dentro de
`run_all()` en la rama `if not self.quick:`.

## 2. Decisiones de diseño y alcance

**Fuente única de la serie:** las **ocho** decisiones de la preparación, con su rationale y sus alternativas
rechazadas, están estructuradas en `10-analisis-post-implementacion.md` §Decisiones Arquitectónicas como
`DA-CIM.1`…`DA-CIM.8`. Aquí se enuncian las que fijan alcance, con los mismos números. A esas ocho se sumaron el
2026-10-08 **dos decisiones del operador**, `DA-CIM.9` y `DA-CIM.10` (abajo, al final de este §2), y al cerrar FASE-A2 su **decisión de diseño propia**, `DA-CIM.11` (el esquema de nombres de la instantánea, que es lo que un humano ve en disco), y al cerrar FASE-A3 su **segunda decisión de diseño propia**, `DA-CIM.12` (la etiqueta del resumen enumera las causas que la corrida imprimió; la concurrence de dictámenes dentro de la misma entrada se difiere con diente de caracterización y deuda S-CIM-9): no son filas de
aquella tabla —la preparación no las dictó y el censo de la enmienda no la incluye— y por eso el índice del corpus
las publica como *citadas sin definición*, un estado explícito del escritor y no un rojo. Su fuente canónica es este
§2 más el contrato §R2 para el presupuesto y el prompt de A3 para el bloque huésped. La serie propia de seguimientos
y deudas es `S-CIM-n` (§5), elegida **namespaced a propósito**: los IDs `D-1`, `D-2`, `D-3` ya existían como citas del corpus
`DT-2` y una versión temprana de este documento los usó como etiquetas propias — al regenerar el índice del corpus,
el plan se había convertido en dueño de IDs ajenos. Medido y corregido en la misma preparación.

**DA-CIM.1 (dictada por el operador, no se reabre): se cura por separación de las dos preguntas.** La vigencia del
plan se responde comparando **cuerpo contra cuerpo** (`sha_cuerpo` publicado contra `sha` del cuerpo actual);
la fidelidad de lo publicado contra el servidor se sigue respondiendo con `metadata.fileSha256` y, si hubo
descarga, la descarga. **Rechazada:** `--sanear` en el writer. Motivo: el writer no conoce la política de
identidades de cada cliente, y un saneado automático en el emisor fabricaría una segunda verdad sobre qué se
podía publicar. El que sanea sigue siendo quien documenta, con la receta del padre (sustitución a nivel de
**bytes** con `assert count(old) == N` y prueba de sha inverso).

**DA-CIM.2: el registro pasa de `schema_version` `1.0` a `1.1`** con el campo `sha_cuerpo` en la entrada que escribe
`registrar_publicacion()`. Sin back-fill. Las entradas `1.0` se leen y se dictaminan `NO-EVALUABLE por
instrumento`, nunca VENCIDO ni verde (AC1, AC2). El `README.md` de `instantaneas/` describe la semántica que
AC2 retira («compara el sha de esta copia contra el cuerpo del plan»): viaja **en el mismo commit** de la cura,
porque es prosa que un lector futuro va a creer (L-G3).

**DA-CIM.3: AC4 no re-subre.** Si el parseo de la tabla de `qmind source upload` no encuentra id, el estado publicado
es «id no capturado» y la comprobación es un censo de `fetch_sources()` más la comparación por sha. Re-subir
duplica: la idempotencia es por título y un título nuevo nunca existió antes (L-QW.2, medido en la memoria de
referencia del proyecto).

**DA-CIM.4: AC6 se cierra declarando, no tocando el notebook.** `qmind source delete` es irreversible sobre contenido
publicado y exige decisión escrita aparte del operador. La opción elegida por el mandato si no hay autorización
literal —**dejar el rojo declarado con dueño**— es la que se diseña aquí, y la entrada `vigente-historica` queda
como alternativa documentada con su disparador, no como tarea. Consecuencia dura: con AC2 landed y sin decisión
sobre la era G, el modo completo va a cortar `[17/18]` en rojo **por un hallazgo verdadero**. El plan lo
prevé, lo nombra y no lo tapa: ver maestro §5, deuda S-CIM-2.

**DA-CIM.5: FASE-A se corta en A1/A2/A3 por parejas de acoplamiento real, no por tamaño arbitrario.** El mandato traía
seis ACs en una fase; R3 fija cuatro tareas de fix como techo y aquí cada AC aporta su mutante, su restauración y
su diente. **Rechazada:** dividir en seis fases (una por AC), que habría multiplicado los cierres documentales sin
separar superficies distintas.

**DA-CIM.6: FASE-B no toca `scripts/build_lesson_index.py` sin su propia fase.** Si el diagnóstico concluye que la
cura exige el generador —código de producto, con batería propia—, eso es FASE-C con su AC, su mutación y la
re-ejecución de `tests/test_build_lesson_index.py` (16 funciones) y `tests/test_verify_qmind_context_freshness.py`
(36 funciones). La alternativa —meter el cambio de generador dentro de FASE-B— quedó rechazada por R3 y por la
propia formulación del mandato.

**DA-CIM.7: el verde se audita con un instrumento que la cura no produce.** `[17/18]` curado no se certifica a sí
mismo: el modo completo se corre y su crudo se archiva (L-V2.2). Y el diente decisivo del plan es AC10:
**publicar el `10-analisis` de este propio plan con el writer ya curado**, que es el caso imposible de hoy
(cuerpo con identidades sustituidas) y solo consume una escritura remota autorizada.

**DA-CIM.8: FASE-VERIFY no se activa en este plan**, con los tres criterios de §4.6 medidos en el maestro §3. La
certificación cruzada la hacen AC10 en RELEASE y los dientes por AC.

**DA-CIM.9 (dictada por el operador el 2026-10-08, Caso A vía a1): FASE-A3 gobierna el bloque huésped también en el
camino de migración.** No re-abre AC6: le añade el diente sin el cual el rojo de la era G es inalcanzable mientras
el registro solo tenga entradas `1.0` (consecuencia 1 del registro de A1). Su especificación, sus tres dientes y su
mutante viven en `05-prompt-inicio-sesion-fase-A3.md` (subtarea 3b) y su fila en §4 con la errata que la estampa.
**Rechazadas:** a2 (re-publicar el `10-analisis` del padre como 1.1 — escritura remota sobre contenido publicado,
con autorización propia) y a3 (declarar y no tocar, que dejaría `[17/18]` en NO-EVALUABLE sin fecha). **Addenda de la
misma sesión, con el coste medido — a2 queda RECHAZADA también por daño, no solo por autorización:** con AC3 y AC4
sin landear, una segunda publicación del mismo plan comparte prefijo de 120 caracteres en el slug (la línea
`slug = re.sub(…)[:120] + ".md"` dentro de `registrar_publicacion()`, en
`scripts/validate_qmind_writeback.py`) y **pisaría la única instantánea que queda del padre** — que es
exactamente el mecanismo que perdió los byte-exactos de la entrada `reemplazada` (S-CIM-3); y la entrada nueva
nacería con `fuente_id` vacía, porque las dos ramas de `do_upload()` siguen pasando la cadena vacía al llamar a
`registrar_publicacion()`. Además, con título nuevo la idempotencia por título **crea la fuente duplicada** que mide
L-QW.2, y con el título vigente el crudo de 124.280 B no casa con lo publicado de 125.198 B, así que corta `[FAIL]`. No hace
falta para DA-CIM.9: el diente de A3 hace visible el rojo **sin** necesitar una entrada 1.1. El `1.1` llega con AC10
en RELEASE, con el writer ya curado por A2.

**DA-CIM.10 (dictada por el operador el 2026-10-08, Caso C vía c1): el presupuesto de referencia se fija por fase** —
90 `tool_use` para A2, A3 y B, 60 para RELEASE — sobre la base medida de A1. Su fuente canónica es el contrato §R2 y
la fila de §3 de este maestro; las dos reglas c2 que se adoptan con ella viven en el prompt de A2. **Rechazada c3**
(aceptar checkpoints: el número deja de ser señal). La cláusula «un exceso produce checkpoint y fase INCOMPLETA, no
una segunda fase» queda intacta, y **FASE-C no está nombrada** en la decisión: se queda con 60 hasta que el operador
la cite si B la abre.

**DA-CIM.11 (decisión de FASE-A2, 2026-10-08): el nombre de la instantánea es `<plan>--<título-saneado>--<huella>.md`**
y se arma en `slug_de_instantanea()`. Se enuncia aquí porque define lo que un humano ve en `instantaneas/`; su
rationale y sus alternativas rechazadas viven en `10-analisis-post-implementacion.md` §Decisiones Arquitectónicas.
La huella son los 16 primeros hexádigitos del `sha256` que la entrada declara y va **al final**, con el presupuesto
de `NOMBRE_INSTANEA_MAXIMO` (120) reservado desde ese extremo para que el recorte caiga siempre sobre el prefijo.
Consecuencias que el diseño busca y comprueba por diente: dos publicaciones del mismo plan dejan dos byte-exactos
distintos, un tercer título de prefijo común tampoco pisa, y ningún nombre generado puede ser `README.md`.

**Fuera de alcance, declarado:** `[18/18]` y su invocación sin `--strict` (deuda S-2 del hermano, maestro §5);
la limpieza retroactiva de las fuentes duplicadas de `TRIBUNAL-OFFLINE-2026-09-09` (S-4 del hermano); la edición
de cualquier documento del plan padre archivado; `AGENTS.md`, `.cursorrules`, `VERSION.yaml` en fases
intermedias; el pipeline `v4complete` (no corre en ninguna fase de este plan).

## 3. Fases, complejidad y R3

R3 aplicado al diseño, no de pasada: el mandato traía **seis ACs en una fase**. Seis ACs con su mutante, su
diente contrario y su restauración por sha son más de cuatro tareas de fix, así que FASE-A se corta en tres
sesiones por **parejas de_acoplamiento real**, no por tamaño arbitrario.

| # | Fase | Objetivo y sus cuatro tareas | ACs | Complejidad y razón | Comandos largos |
|---|---|---|---|---|---|
| 0 | Preparación (ESTA sesión, cerrada) | Paso 0 capitalizado; revalidación del estado medido; diseño de ACs y fases; prompts, checklist y acumulativos; derivados regenerados | AC10 preparada, no certificada | MEDIA: cero código, decisiones congeladas del mandato verificadas contra disco | 0 |
| 1 | **A1** | PRE; `sha_cuerpo` en `registrar_publicacion()` con schema 1.1 y migración NO-EVALUABLE; puerta de `verificar_contenido()` cuerpo-contra-cuerpo conservando el gate de registro; dientes + diente contrario + cuerpo-editado; cierre | AC1, AC2 | ALTA: es el cambio de contrato del que dependen AC6 y AC10 | 0 |
| 2 | **A2** | PRE; slug único y legible en `registrar_publicacion()`; parseo de la tabla de `upload_source()` en `do_upload()` con no-re-subida; dientes y mutantes; cierre | AC3, AC4 | MEDIA-ALTA: toca la misma función que A1, por eso va después | 0 |
| 3 | **A3** | PRE; resolución de rutas con plan archivado fijada por diente; censo de fuentes del notebook y dictamen de la era G con dueño escrito; contador publicado por el verificador; cierre | AC5, AC6 | MEDIA-ALTA: su verde depende de que A1 haya landed; la parte remota puede quedar NO-EVALUABLE por red | 0 |
| 4 | **B** | PRE; diagnóstico reproducido con medición de la clasificación (no con hipótesis); cura dentro del test gobernando la divergencia esperada; control negativo intacto contra `6b02532`; cierre | AC7, AC8 | ALTA: es un control anti-regresión cuya premisa de entorno ya cayó una vez | 0 |
| 5 | **C** (condicional) | Si B concluye que la cura exige el generador: cambio en `scripts/build_lesson_index.py` con su AC, su mutación y las baterías de hermanos re-corridas; si no, la fase **no se ejecuta** y se declara | AC9 | ALTA: código de producto con 16 + 36 funciones hermanas | 0 |
| 6 | **RELEASE** | Docs oficiales con el mandato de versión del operador; write-back del `10-analisis` de este plan **con el writer curado** (AC10); orden R2.10 y archivado; validaciones con crudo | AC10 | MEDIA: sincronización y orden del cierre; la subida remota exige autorización literal propia | 0 |

**FASE-VERIFY no se activa, con los tres criterios medidos** (executor §4.6): (1) fases de implementación ≥3 —
**sí**, cuatro o cinco; (2) existe una fase con ejecución E2E tipo `v4complete`/`v4audit` — **no**, cero comandos
largos en las siete filas de arriba; (3) ACs que cruzan múltiples fases — **sí** (AC6 y AC10 cruzan A1→A3→RELEASE).
Fallando el criterio 2, el workflow queda en tres etapas. La certificación cruzada la hacen AC10 en RELEASE y
los dientes por AC, no una sesión de verificación.

**Presupuesto (R2.1, referencia re-ancurada el 2026-10-08 por DA-CIM.10 — Caso C, vía c1):** **90 `tool_use` para
FASE-A2, FASE-A3 y FASE-B, y 60 para FASE-RELEASE**, siempre **al corte que la sesión tenga autorizado**. La base
es la medición de FASE-A1: ≈70 `tool_use` contados a mano en
`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/00-registro-de-fase.md` (≈30 código + tests + mutantes, ≈25
cierre documental, ≈15 verificaciones y re-tomas; el total lo imprime ese registro y la separación en partidas la
declaró el operador al dictar la decisión). Rechazada c3 (aceptar checkpoints: con un denominador que las fases
exceden a medias, el número deja de ser señal). La cláusula «un exceso produce checkpoint y fase INCOMPLETA, no una
segunda fase» del contrato §R2 queda **intacta**, y con ella la de las fases ya cerradas: A1 corrió contra la
referencia de 60 que estaba vigente y su exceso quedó declarado como checkpoint. El instrumento
canónico `evidence/FASE-D/measure_iterations.py` sigue **FUERA DE SERVICIO**: pide el transcript del cliente y su
acceso está denegado (medido el 2026-10-07, no reintentado aquí). Cada sesión cierra con auto-reporte en la
unidad usada y declarando que no es comparable con las que usaron el instrumento. **FASE-C no está nombrada en la
decisión** y se queda con los 60: si B la abre, la referencia la dicta el operador. ⟦**Addenda de la misma sesión,
decidida por el operador tras medir el precedente:** FASE-C pasa a **90**. La base es la misma medición: A1, también
de complejidad ALTA, consumió ≈70 con dos ACs y tres mutantes, y C trae mutación sobre `_plan_date` más la
re-ejecución de 4 + 16 + 36 funciones hermanas. El 60 de la fila de C era el denominador que A1 ya había reventado.⟧

## 4. Criterios de aceptación y pares de evidencia

E = `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07`. Todo artefacto indicado como nuevo es **salida futura**.
AC1-AC6 conservan el número y el contenido del mandato; AC7-AC10 las añade este diseño y se nombran con la fase.

| AC | Contrato, artefacto y clave legible | Verde / rojo exigido | Fase |
|---|---|---|---|
| AC1 | Cada entrada que escribe `registrar_publicacion()` guarda `sha_cuerpo` —sha del cuerpo del plan en el momento de publicar— además del `sha256` de la instantánea. `schema_version` pasa a `1.1`. **Artefacto y clave:** `.opencode/qmind-writeback/registro.json`, clave `sha_cuerpo` por entrada, legible por un humano que solo tenga el archivo | Verde: la entrada nueva lleva `sha_cuerpo` igual al sha del cuerpo **en disco al publicar**, no al de la copia saneada. Rojo con mutante: desactivar la escritura del campo hace caer el diente que lo lee. Rojo de migración: una entrada `1.0` sin el campo **no** produce VENCIDO ni verde; sale NO-EVALUABLE con motivo. **Prohibido** back-fill: calcular el sha de hoy y escribirlo en la entrada vieja | A1 |
| AC2 | `verificar_contenido()` dictamina VENCIDO solo cuando `sha(cuerpo actual del repo) != sha_cuerpo publicado`. La fidelidad remota sigue gobernada por `metadata.fileSha256` == sha(instantánea) y, si hubo descarga, la descarga casa o corta `PROMESA-ROTA`. Se conserva el contrato D2 heredado del hermano: sin observación NO-EVALUABLE, la abstención nunca se pinta de VENCIDO, el rojo manda sobre la abstención | Verde **contrario** (el diente que prueba que el hueco existía): subida de copia saneada con cuerpo crudo intacto → antes `[VENCIDO]`, ahora vigente por cuerpo. Verde real: cuerpo editado **después** de publicar → VENCIDO (esa es la vigencia). Verde conservado: instantánea editada sin re-subir → VENCIDO por el gate `e["sha256"] != sha_inst`, que no se toca. Rojo con mutantes: apagar la comparación cuerpo-cuerpo o apagar el gate de registro cada uno rompe su grupo | A1 |
| AC3 | El nombre de la instantánea en `registrar_publicacion()` incluye el sha de la instantánea (o un correlativo) y sigue siendo legible. Dos títulos con prefijo común de 120 caracteres no pueden pisar el mismo archivo | Verde: dos publicaciones consecutivas del mismo plan dejan **dos archivos** y dos byte-exactos distintos, cada entrada casa con su propio archivo. Rojo con mutante: devolver el slug al prefijo truncado hace que la segunda publicación pise la primera y el diente de sha cae. Rojo adicional: el nombre generado no puede ser `README.md` ni colisionar con él | A2 |
| AC4 | `do_upload()` captura `fuente_id` parseando la **tabla** que responde `qmind source upload` (líneas `Key: value`, no JSON) y la escribe en la entrada. Si el parseo falla, **NO re-sube**: verifica por censo de `fetch_sources()` y reporta el estado | Verde: la entrada nueva lleva un id que casa con una fuente real del censo (id + título + `sha_metadata`). Rojo con mutante: un parseo que asuma JSON deja el id vacío y el diente lo declara «id no capturado», no silencioso. Rojo de contención: ante parseo fallido el instrumento **no** invoca una segunda subida (el contador de subidas de la corrida es 1). Límite declarado: si el censo remoto no está accesible, AC4 se certifica sobre la tabla archivada de una subida real y se dice que el censo quedó NO-EVALUABLE | A2 |
| AC5 | Con el plan bajo `Archives/`, `--upload Archives/<PLAN>` publica y la clave del registro sigue siendo `plan_dir.name` (sin el prefijo). El modo verificación (`cuerpo_del_plan()`) resuelve el cuerpo en las dos raíces | Verde: ruta con prefijo → entrada registrada con `plan` = nombre del directorio; y el dictamen del verificador sobre ese mismo plan no sale NO-EVALUABLE por «no resuelve». Rojo: `--upload <PLAN>` a secas con el plan archivado corta `[FAIL]` **por ruta no encontrada nombrada**, no por red. Rojo de mutante: eliminar la segunda raíz de `cuerpo_del_plan()` convierte un NO-EVALUABLE honesto en VENCIDO falso. **Medido en preparación:** la composición de `main()` ya admite el prefijo; lo que aporta esta fase es el diente, no la construcción | A3 |
| AC6 | La fuente `01a0bfc9-…` (era G) nombra al plan padre y no está contable en el registro, así que al curar AC2 corta `[DUPLICADO-VIGENTE]`. **No se borra nada.** Se cierra de dos formas y solo una es elegible sin autorización literal: (a) registrarla como `vigente-historica` con su sha —requiere instrucción expresa para escribir el registro a mano por una fuente ajena— o (b) **dejar el rojo declarado con dueño y disparador** | Verde de (b): la corrida imprime el rojo con el id, el título truncado y la ruta del documento donde está el dueño. Rojo que no puede desaparecer: silenciar el bloque huésped, o marcar la era G como reemplazada sin su sha. Si se ejecuta (a), verde adicional: el censo de fuentes vigentes del plan pasa de 2 a 1 y el rojo se retira **por contabilidad, no por borrado**; la alternativa (a) queda sin ejecutar si falta la autorización | A3 |
| AC6 — **errata AÑADIDA 2026-10-08, despues de la fila original, que no se re-escribe** | **DA-CIM.9 (Caso A, vía a1): FASE-A3 pasa a gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9).** La fila de arriba sigue vigente tal como se dictó; esta errata le añade el requisito que el diseño no podía ver: con la guarda de migración terminando en `continue` —medido y declarado por A1 en `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/00-registro-de-fase.md`, consecuencia 1— las entradas `1.0` **nunca** llegan al bloque `[DUPLICADO-VIGENTE]`, así que mientras el registro solo tenga entradas viejas el dictamen de la era G es inalcanzable y `[17/18]` queda en NO-EVALUABLE sin fecha. Especificación, dientes y mutante viven en `05-prompt-inicio-sesion-fase-A3.md` (subtarea «AC6 por DA-CIM.9»). **Rechazadas:** a2 (re-publicar el `10-analisis` del padre como 1.1: es una escritura remota sobre contenido publicado y pide autorización propia, solo si el operador la pide aparte) y a3 (declarar y no tocar: dejaría `[17/18]` en NO-EVALUABLE indefinidamente) | Verde: una corrida con **solo entradas `1.0`** en el registro imprime el rojo huésped con su id, su título truncado legible y su sha del censo, **y** la abstención de migración en la misma corrida. Rojo con mutante: apagar la llamada huésped en la rama de migración. La capa D2 **no** se levanta para entradas `1.0`: siguen en abstención, nunca `[FRESCO]` sobre quien no tiene `sha_cuerpo` | A3 |
| AC7 | FASE-B produce un **diagnóstico con medición, no con hipótesis**: por cada `i` divergente, la tupla `fuente_fecha` de A y de B, el documento dueño que la produce, y la prueba de si la diferencia depende del reloj del sistema, de `MTO_A`/`MTO_B` contra mtimes reales, o de que en un clon la ruta no materialice. Artefacto: `E/FASE-B/diagnostico.md` + crudo de la corrida | Verde: el informe nombra la causa con la corrida delante y **reproduce** el rojo contra el HEAD de su sesión (no contra `649114c` a secas). Rojo de método: concluir «el fixture está mal» sin reproducir la clasificación, o citar la medición del 2026-10-07 como propia. Prohibido cerrar AC7 tocando código | B |
| AC8 | La clasificación queda gobernada de modo que la divergencia **esperada** del control sea solo la fecha de `mtime`, sin debilitar la aserción ni el control negativo anclado a la revisión fija (`REV_CONTROL_DEFECTUOSO`). El diente se ejecuta sobre el instrumento versionado | Verde: los cuatro dientes del archivo cierran, el control sigue perdiendo cuando el generador defectuoso está puesto, y `test_dos_checkouts_con_mtimos_distintos_publican_bytes_identicos` sigue verde sin tocar su aserción. Rojo exigido: apagar la gobernanza nueva **vuelve** el rojo; re-ancorar el control a HEAD se detecta por un diente que afirma la revisión fija literal. **Prohibido**: re-anclear a HEAD, re-fijar un baseline, o convertir la aserción en un `in {...}` que traga la mala clasificación | B |
| AC9 | **Condicional.** Si AC7 concluye que la cura está en `scripts/build_lesson_index.py`, el cambio va con su propio AC, su mutación sobre el símbolo real (`_plan_date` y su cascada `nombre`/`commit`/`SIN-FUENTE`) y la re-ejecución de la familia (`tests/test_build_lesson_index.py`, 16 funciones, y `tests/test_verify_qmind_context_freshness.py`, 36 funciones). Si AC7 no exige el generador, **esta fase no se ejecuta** y se declara en el checklist | Verde: la línea `[fechas]` del writer y del `--check` sigue imprimiendo los tres tiers en verde **y** en rojo, y ningún tier nuevo aparece sin su diente. Rojo: quitar la rama de orden publicada deja un `[OK]` sin denominador. Límite conservado de la cura del 2026-09-26, que no se cura aquí: el desempate por nombre si un `git mv` masivo de `Historico/` colapsa las fechas del tier `commit` | C |
| AC10 | **Dogfooding del contrato.** El cierre de este plan publica su propio `10-analisis` con el writer curado (`--upload`, `--file` copia saneada versionada, `--title` nuevo) y `[17/18]` dicta **vigente por cuerpo** sobre esa publicación. Es el caso que hoy es imposible | Verde: la entrada lleva `sha_cuerpo` y `fuente_id` poblados, hay dos byte-exactos en `instantaneas/` si hubo dos publicaciones, y el dictamen impreso dice cuerpo. Rojo estructural: si AC1 o AC2 no landed, esta AC **no puede** dar verde — es su prueba de que el plan cerró su propia meta. Condición de honestidad: la subida remota exige autorización literal propia de la fase; sin ella AC10 cierra en `PENDIENTE-AUTORIZACION` con el paquete offline completo (copia saneada, título, sha inverso) y **no** se declara Published | RELEASE |

**Regla transversal de dientes (mandato, sin excepciones):** cada mutante tiene su restauración verificada por
sha256, todos se ejecutan sobre el **instrumento versionado** y ninguno reimplementa el hueco dentro del test.
Los 23 dientes de `tests/test_validate_qmind_writeback_escritura.py` siguen verdes **sin re-bajar ninguna
aserción**, más un diente por AC nueva.

## 5. Deudas y seguimientos con dueño

| # | Tema | Estado | Dueño | Disparador |
|---|---|---|---|---|
| S-CIM-1 | `[18/18]` sigue invocado **sin** `--strict`: el verde por ausencia del instrumento que AC3 del hermano cerró en `[17/18]` vive ahí (deuda S-2 del `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`) | FUERA DE ALCANCE de este plan, nombrada para que no se re-descubra (L-QW.4) | operador / siguiente mandato sobre los verificadores QMind | una AC con su propio disparador; **no** se la añade a ninguna fase de este plan a espaldas del operador |
| S-CIM-2 | Rojo `[DUPLICADO-VIGENTE]` de la era G una vez landed AC2 | **DECIDIDA 2026-10-08 por el operador (Caso A, vía a1): gobernar el bloque huesped tambien en el camino de migracion (DA-CIM.9).** Sigue DECLARADA con dos salidas (maestro §2 DA-CIM.4); la elegida por diseño sigue siendo la de rojo con dueño, ahora con diente propio porque A1 midió que la guarda de migración la deja inalcanzable (maestro §4, fila AC6 con su errata) | operador (decisión escrita para tocar el registro por una fuente ajena; `source delete` queda fuera) y FASE-A3 para la gobernanza del bloque | la corrida del modo completo que la nombra; se presenta con opciones, no se tapa |
| S-CIM-3 | Byte-exacto perdido de la entrada `reemplazada` del padre (el `0b02bb5084e3…` ya no tiene archivo) | NO RECUPERABLE; se documenta como consecuencia de AC3 y como motivo por el que la migración no rellena nada | este plan (su RELEASE lo publica en CHANGELOG con la fila del registro) | la cura de AC3 |
| S-CIM-4 | Limpieza retroactiva de las dos fuentes vigentes de `TRIBUNAL-OFFLINE-2026-09-09` (S-4 del hermano) | FUERA DE ALCANCE | operador | mandato expreso sobre contenido publicado |
| S-CIM-5 | Packs de briefing (`briefing/` + `build_phase_briefing.py`) para los prompts de este plan | NO GENERADOS en la preparación, declarado: los prompts nuevos usan la forma canónica `Lee …` de §8 del template, la generación de packs pertenece a la fase que los consuma | la primera sesión que pida un pack de este plan | esa solicitud |
| S-CIM-6 | `README.md` de `instantaneas/` describe la semántica pre-AC2 | EN ALCANCE de A1 (viaja con su commit, L-G3); no es regenerable por escritor: es prosa humana | FASE-A1 | la edición del contrato |
| S-CIM-7 | Trabajo ajeno sin commitear encontrado al abrir: 12 `briefing/FASE-*.md` bajo el plan padre archivado y `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`, todos **untracked** | EXCLUIDO de toda acción y de todo conteo de esta sesión; preservado intacto | su autor (otra sesión) | si el operador pide commitearlo, se hace en commit propio y separado |
| S-CIM-8 | `run_all_validations.py` modo completo con los tres rojos del cierre del padre (`Tests`, `[17/18]`, `[18/18]`) | MEDICION DEL PADRE, archivada en su registro; este plan la referencia y la re-mide en su propio RELEASE | FASE-RELEASE de este plan | su corrida, con crudo archivado. **Re-medido al cerrar FASE-A3 (2026-10-09):** `[17/18]` ya no está en NO-EVALUABLE — corta rojo por contabilidad (era G) y su crudo vive en `E/FASE-A3/` |
| S-CIM-9 | Concurrence de dictámenes en la **misma** entrada: la puerta de vigencia termina en `continue` antes del bloque huésped, así que una entrada `1.1` VENCIDA no evalúa a sus huéspedes (una `1.0` en migración sí, desde DA-CIM.9) | DECLARADO 2026-10-09 por FASE-A3 con **diente de caracterización** que aserta el comportamiento vigente y se pone rojo cuando un AC lo gobierne. **No es un olvido: DA-CIM.9 recortó la cura a la rama de migración** | operador (una AC propia sobre la concurrence) | un mandato que gobierne los `continue` del bucle de `verificar_contenido()` |
| S-CIM-11 | El escritor `log_phase_completion.py` interpreta `--archivos-mod` como **lista de rutas separadas por comas** y fabrica la columna «Cambio» tomando el ultimo segmento en title case: pasarle prosa (una unidad de medicion declarada) convierte la fila en dos rutas inventadas, una de ellas con un nombre que el arbol no tiene | **MEDIDO 2026-10-09 en FASE-RELEASE**: la fila salio publicada asi y se re-escribio a mano con **errata visible dentro de la propia fila**, porque re-correr el escritor apilaria una entrada duplicada y la regla de cierre lo prohibe | operador / siguiente mandato sobre los escritores documentales | un AC que governe el formato de `--archivos-mod` (validar que cada segmento sea una ruta del arbol, o separar unidad y conteo en banderas propias) |
| S-CIM-10 | El modo completo aborta en esta máquina al decodificar la salida de un subprocess con cp1252 (`UnicodeDecodeError` en el reader thread), antes de imprimir la primera etiqueta | MEDIDO 2026-10-09; la corrida de la fase se re-tomó con `PYTHONUTF8=1`, variable declarada en cada crudo. No lo introdujo esta fase y no se cura aquí (tabla de conflictos: «preferencia: no tocar `run_all_validations.py`») | operador / siguiente mandato sobre el runner | un AC que fije la codificación del lector y su crudo |

## 6. Preparación, trazabilidad y permisos

Qué hizo esta sesión y qué no. **No tocó código fuente ni tests, no ejecutó `v4complete`, no subió ni borró nada
en el notebook, no editó `AGENTS.md`, `.cursorrules` ni `VERSION.yaml`, no commiteó ni empujó** (el mandato
reserva esas acciones a instrucción literal en el chat y aquí no vino). ⟦**Sello de la misma sesión:** esa cláusula
describe el árbol al cerrar el documento. Después del cierre documental llegó la instrucción literal «Git Commit +
L3 + Push», y commit, revisión L3 y push se ejecutaron; ver «Estado de los cinco cortes» abajo y el §7 del registro
de fase. No se reescribe la afirmación original porque es registro de la preparación.⟧ Consultó el corpus por tres
capas (Q1-Q10 de `00-lecciones-capitalizadas.md`), midió en disco el hueco del slug y sus dos shas, reprodujo el
rojo de S15 contra `98c190e`, y releyó los símbolos del writer antes de citar uno.

Escritura efectuada: los documentos de este directorio y el expediente `E/FASE-0/` (`quick_apertura.txt`,
`pre_seleccion_apertura.txt`, `00-registro-de-fase.md`). El par del índice del corpus se regenera con su escritor
como **último paso**, porque esta sesión añade `.md` que nombran IDs y eso vence el conteo de citas (R2.10).

Auto-reporte de presupuesto (unidad declarada, no comparable con el instrumento canónico): ver
`E/FASE-0/00-registro-de-fase.md`, sección de presupuesto. El corte usado es **«hasta listo para revisión»**,
porque el commit no estaba autorizado al momento del cierre documental; no se simuló un corte de código. ⟦**Sello 2026-10-08, misma sesión:** llegó la instrucción literal «Git Commit + L3 + Push». Commit `b536748` con los ocho checks del hook versionado pasados, revisión profunda L3 **sin hallazgos** y rango empujado `98c190e..b536748` (paridad verificada con `git ls-remote`). No se re-escribe la frase original: registra el estado del árbol al cerrar el documento.⟧

**Estado de los cinco cortes:** implementación terminada (no aplica: fase documental) → verificación terminada
→ cierre documental → listo para revisión → **espera de autorización**. ⟦**Sello (2026-10-08, misma sesión):** la
autorización llegó después del cierre documental, con la instrucción literal «Git Commit + L3 + Push». Commit
`b536748` con sus ocho checks de hook pasados, revisión profunda L3 **sin hallazgos**, rango empujado
`98c190e..b536748` y paridad verificada por `git ls-remote`. El registro de esta frase viaja en el commit
documental posterior, no en el propio: el sha de un sello no se estampa a sí mismo.⟧
