# Registro de fase — FASE-A3 (CURA-INSTRUMENTOS-QMIND-S15-2026-10-07)

**Sesión:** 2026-10-09 · **Rol:** ejecutor de FASE-A3 (AC5, AC6 y la subtarea 3b / DA-CIM.9), plan de ejecución
**DIRECTA**. **Complejidad declarada por el diseño:** MEDIA-ALTA.
**HEAD medido al abrir:** `git rev-parse HEAD` = `b32a5ad65c9520de0190b2dc15e97d30ae721380`.
**Paridad al abrir:** `git rev-parse origin/master` = `git ls-remote origin refs/heads/master` = HEAD (los tres
miden lo mismo; la paridad se declara por medida, no de memoria).
**Árbol al abrir:** `git status --porcelain -uall` trajo **13 rutas staged ajenas** (12
`Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/briefing/FASE-*.md` y
`evidence/REFACTOR-WHATSAPP-ENTREGA-2026-10-07/…/FASE-E2E/captura_stdout.txt` del hermano, deuda S-CIM-7 del
maestro). **No se comitearon, no se des-stagearon, no se tocaron.** La cláusula INDICE del mandato quedó aplicada
por su rama pasiva: como no hubo instrucción literal de commit, tampoco hizo falta el pre-vuelo de packs sobre el
árbol del pathspec. Una decimocuarta ruta era propia del plan y venía modificada de la sesión de preparación del
prompt de A3 (`05-prompt-inicio-sesion-fase-A3.md`, la nota de `$(date +%F)` y la cláusula INDICE): se respetó
intacta y viajó en el cierre de esta fase.
**Dependencia dura con A1 verificada antes de editar:** la puerta cuerpo-contra-cuerpo de A1 está landed (su
`[NO-EVALUABLE] ... no grabo sha_cuerpo` apareció en el dictamen real de esta sesión) y A2 está cerrada y empujada;
por eso AC6 era evaluable.

## Línea base re-medida, no heredada

| Punto | Qué decía el prompt de la fase | Qué se midió el 2026-10-09 | Consecuencia |
|---|---|---|---|
| Dientes de la familia | «los 23 + los de A1 + los de A2 + los de esta fase» | `git grep -c -E "^\s*def test_" b32a5ad -- tests/test_validate_qmind_writeback_escritura.py` = **43**; en el árbol de la fase `grep -cE` = **57** | PRE 43 / POST 57, resta **14** (R2.7) |
| Rojos verdaderos de `[17/18]` | «aquí aparecen los primeros rojos verdaderos del check» | Confirmado: `--strict` cortó `EXIT=1` con `contenido: DUPLICADO-VIGENTE` sobre la era G | AC6 cerrada por la opción (b), no tapada |
| Racha remota del listado | «si el listado falla, registrar la racha y cerrar AC6 en NO-EVALUABLE» | El listado respondió en el **intento 1** (`62 fuentes`); no hubo que invocarlo 3 veces | AC6 se cierra por dictamen, no por abstención |
| Mutante de `cuerpo_del_plan()` | «quitar la segunda raíz convierte una abstención honesta en `[VENCIDO]` falso» | **REFUTADO por medición:** la copia mutada imprimió **0** líneas `[VENCIDO]` y **40** caídas con una sola causa (`cuerpo is None`: abstención del verificador y `[FAIL]` del escritor) | El daño real es inverso (medición → abstención). El diente se ancla en la unidad del lector, no en el conteo de caídas; L-CIM.10 |
| `instantaneas/` | heredado de A2: «2 rutas» | `ls -1 .opencode/qmind-writeback/instantaneas/ \| wc -l` = **3**; la tercera es la publicación del hermano JEV (commit `d47953b`), no de esta fase | Se publica la medida; esta fase no añadió rutas ahí |
| Censo del padre | «tres fuentes del plan padre, la de la era G sin entrada» | Confirmado por el lector del instrumento: 3 nombran al padre, 2 contables, 1 huésped (`01a0bfc9-5f5a-783e-9492-16367bbff596`, `sha_metadata` `87b9b6664f945ac6…`, 39.422 B) | coincide con el mandato; la cota del censo es 62 fuentes |

## AC5 landed: la ruta del `--upload` fijada por diente (tarea 2)

**Qué cambió en el emisor.** `main()` compone la ruta con `ruta_del_upload(argv, plans_dir)` y **después** resuelve
el notebook: el rojo `[FAIL] Upload: el directorio no existe: <ruta buscada>` se dicta con el servicio caído. El
texto lo emite un solo sitio (`sin_directorio()`), que llaman `main()` y `do_upload()`; no hay dos mensajes que
puedan divergir. La composición con prefijo **no se construyó** — `--upload Archives/<PLAN>` ya resolvía y
`plan_dir.name` ya daba la clave—; lo que aporta la fase es el diente, como dictó la rectificación del maestro §1.

**Dientes (5, todos con `--plans-dir` y `--registro` montados en `tmp_path`, cero toque del registro real):**

- `test_upload_con_prefijo_y_desde_la_raiz_dejan_la_clave_del_directorio_sin_prefijo` — verde por `main()` en las
  dos raíces; la clave es `PLAN-A-2026-09-01`, nunca `Archives/…`.
- `test_upload_sin_prefijo_con_el_plan_archivado_corta_por_la_ruta_y_no_por_la_red` — rojo nombrado por su causa,
  con `llamadas == []` (cero salidas al servicio) **y** su control negativo ejecutado sobre el blob commiteado en
  `b32a5ad`, que sí preguntaba al notebook primero y respondía el motivo del lector. El doble lanza la excepción
  REAL del módulo gobernado, no una copia del defecto.
- `test_cuerpo_del_plan_resuelve_las_dos_raices_y_su_ausencia_no_es_ninguna` — el ancla del mutante M1.
- `test_el_plan_archivado_publicado_por_prefijo_no_abstiene_al_verificador_por_no_resolver` — el dictamen sobre el
  plan archivado sale medido (`[FRESCO]`, `1 dictaminada(s) por cuerpo`, `descargas == 1`), no en abstención.
- `test_upload_con_ruta_absoluta_bajo_archives_tampoco_escribe_el_prefijo_en_la_clave` — la otra rama de la
  composición, con un `--plans-dir` que no existe para probar que no interviene.

## DA-CIM.9 landed: el bloque huésped también en el camino de migración (subtarea 3b)

`_huespedes_sin_contabilidad(datos, fuentes, plan)` recibe las fuentes del censo y el nombre del plan y devuelve
las que nombran al plan sin título contable; `_lineas_huesped()` formatea el rojo. La llaman **los dos caminos**:
el de las entradas con `sha_cuerpo` (donde vivía) y el de la guarda de migración, **antes del `continue`**. La capa
D2 no se levantó para entradas `1.0`: esas siguen en abstención con su motivo impreso y nunca `[FRESCO]`.

Los tres dientes exigidos, con su población en `tmp_path` y cero escrituras remotas:

| Diente | Prueba | Lo que afirma |
|---|---|---|
| (i) | `test_la_huesped_sin_contabilidad_corta_rojo_sobre_una_entrada_1_0_sin_descargar_nada` | huésped **roja** sobre una entrada `1.0`, con `descargas == 0`, `EXIT=1` y el rojo impreso con id, título truncado legible y `sha_metadata` del censo; la abstención de migración sigue imprimiéndose y el registro queda byte a byte igual (declarar no es contabilizar) |
| (ii) | `test_el_rojo_huesped_de_una_entrada_1_1_convive_con_la_abstencion_de_migracion` | rojo + abstención en la misma corrida, `EXIT` del rojo, `[VENCIDO]` ausente: la abstención no tapa el hallazgo y el hallazgo no pinta de VENCIDO a la abstención |
| (iii) | `test_el_contador_sigue_cuadrando_con_la_huesped_fuera_de_la_suma` | `[CONTADOR]` con `1+1+1==3` y `2 fuente(s) huesped(s)` en cláusula propia: la huésped no entra en la suma de la partición |

Dos dientes más de contención: `test_la_fuente_del_titulo_reemplazado_no_es_huesped_en_el_camino_de_migracion`
(sobre un registro con las dos entradas `1.0` del padre —vigente y reemplazada— la corrida es `NO-EVALUABLE` con
`0 fuente(s) huesped(s)`: la contabilidad de AC3 no se re-bajó al extraer el bloque) y
`test_la_huesped_sin_promesa_de_sha_nombra_su_abstencion_del_dato` (fuente sin `metadata.fileSha256` →
`sin-sha-en-el-censo`, nunca un sha vacío).

## AC6 cerrada por la opción (b): rojo declarado, nada borrado (tarea 3)

**Dictado del censo** (`censo_qmind_racha.txt`, lectura por `fetch_sources()` del propio instrumento, sin
`originUrl` ni `URI`): 62 fuentes en el notebook `01a04d98-b7bd-778c-8441-26fdc7e35f45`; 3 nombran al plan padre;
2 contables; 1 huésped — `01a0bfc9-5f5a-783e-9492-16367bbff596`, `sha_metadata` `87b9b6664f945ac6279f1efa…`,
39.422 B. Racha: intento 1 = `EXIT 0`.

**Dictamen del verificador sobre el registro real** (`--strict`, dos tomas declaradas en los crudos):

```
[NO-EVALUABLE] REFACTOR-WHATSAPP-… :: la entrada no grabo sha_cuerpo (registro schema 1.1) … no es VENCIDO ni verde
[DUPLICADO-VIGENTE] REFACTOR-WHATSAPP-… :: la fuente 01a0bfc9-5f5a... (10-analisis: … (lecciones...) con
                sha_metadata 87b9b6664f94... nombra al plan y no esta marcada como reemplazada
[CONTADOR] 2 vigente(s): 1 dictaminada(s) por cuerpo, 0 con fidelidad remota medida, 1 NO-EVALUABLE por
           migracion, 0 sin observacion local; … 1+1+0==2; 1 fuente(s) huesped(s) sin contabilidad, …
[FAIL] qmind write-back: titulo OK | contenido: DUPLICADO-VIGENTE      EXIT=1
```

La vía (a) —registrar la era G como `vigente-historica` con su sha— **no se ejecutó**: el mandato no trajo
autorización literal para editar la contabilidad por una fuente ajena. **Dueño escrito: el operador**
(decisión sobre contenido publicado; `source delete` queda fuera de este plan), **disparador: la decisión de
contenido publicado**. El dueño vive en `dependencias-fases.md` (fila 3 del estado de seguimiento) y en
`10-analisis-post-implementacion.md` §Seguimientos, además de maestro §5 S-CIM-2. Ningún documento del plan describe
AC6 como resuelta: el rojo se sigue imprimiendo.

**Cero destructivos:** no se invocó `source upload`, ni `source delete`. Las únicas operaciones remotas fueron
`source list` (censo) y `source download` (verificación de promesa, por el propio `--strict`). `registro.json`
intacto después de las dos corridas (`git status --porcelain -uall -- .opencode/qmind-writeback/` vacío) y ninguna
firma de object storage persistida.

## Hallazgo de la propia corrida, curado en sesión: la etiqueta del resumen

La corrida real expuso que el resumen agregado fijaba `contenido: VENCIDO` para **cualquier** rojo, mientras la
corrida no había impreso una sola línea `[VENCIDO]`: con DA-CIM.9 landed el único rojo podía ser de contabilidad.
Es la misma familia que el plan persigue (el output tiene que codificar el criterio) y cae dentro del criterio
«el rojo nombrado por su causa», así que se curó aquí en vez de diferirlo: `causas_del_rojo()` lista las marcas que
salieron (`VENCIDO`, `PROMESA-ROTA`, `DUPLICADO-VIGENTE`; si no hay ninguna, `ROJO-SIN-CAUSA-IMPRESA`). Diente:
`test_el_resumen_lista_la_causa_del_rojo_y_no_inventa_un_vencido` (dos poblaciones: huésped única → la etiqueta
dice `DUPLICADO-VIGENTE`; dos entradas con dos causas → dice `VENCIDO+DUPLICADO-VIGENTE`). Mutante **M4** (devolver
la cadena fija) rompe **solo** ese diente. Lección definida: L-CIM.9.

**Límite declarado con diente de caracterización, no curado:** una entrada `1.1` cuyo cuerpo venció termina en
`continue` antes del bloque huésped, así que su huésped no se evalúa. La especificación del operador del 2026-10-08
recortó DA-CIM.9 a la rama de migración y no abrió los demás `continue`, y gobernar la concurrence es una decisión
de alcance que esta sesión no tomó. Nace `test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado`,
que aserta el comportamiento vigente y se pondrá rojo el día que un AC lo gobierne (deuda **S-CIM-9**, maestro §5,
dueño operador).

## PRE / POST y mutantes (tarea 4)

| Concepto | Valor | Instrumento |
|---|---|---|
| PRE | `43 passed`, `EXIT=0` | `venv/Scripts/python.exe -m pytest tests/test_validate_qmind_writeback_escritura.py -q`, worktree en `b32a5ad`, intérprete y comando estampados dentro del crudo |
| POST | `57 passed`, `EXIT=0` | mismo comando, mismo intérprete, instrumento **congelado** y con `PYTHONUTF8=1` declarado |
| Resta | **57 − 43 = 14** | 14 dientes de ESTA fase (5 de AC5, 7 de AC6/DA-CIM.9 y 2 de la etiqueta y su límite) |
| Dientes viejos | 43 verdes **sin re-bajar ninguna aserción** | `git diff -- tests/… \| grep -c "^-.*assert"` = **0** |
| Mutantes | 4 de 4 con sensibilidad demostrada | `temp/mutantes_a3/mount` (script, tests, `run_all_validations.py` —que dos dientes leen su fuente—, `tests/conftest.py` y `pytest.ini`); cada crudo con su par `[A] copia intacta` (`57 passed`, `EXIT=0`) / `[B] copia mutada` (`EXIT=1`), ancla con `count(old) == 1` y la aserción que pierde nombrada. M1 40 caídas (una causa), M2 5, **M3 1 (solo el diente (i))**, M4 1 |
| Worktree vivo | intacto | sha256 del script vivo `ffce48557fbc…` y del test vivo `895e64d92c2d…` idénticos antes y después de la tanda |

**Re-tomas declaradas (regla c2).** (1) El arnés de mutantes corrió **tres** tandas: la primera con tres mutantes y
el instrumento previo a la cura de la etiqueta; la segunda y la tercera, con M4 y el instrumento final. Entre la
segunda y la tercera se editó **un diente** (`test_el_resumen_…`) para que su población no dependiera de la rama de
migración y M3 pudiera afirmar «rompe solo el (i)» — la segunda tanda lo rompía también a él. (2) La primera corrida
del dictamen con `--strict` quedó archivada (`dictamen_17-18_strict.txt`) pero sus bytes salieron en cp1252; se
re-tomó con `PYTHONUTF8=1` y las dos tomas se conservan, con la racha declarada en el encabezado. Ninguna edición de
código hubo entre las dos tomas del dictamen.

## Modo completo: se archiva, no certifica su propio verde (L-V2.2)

`PYTHONUTF8=1 ./venv/Scripts/python.exe scripts/run_all_validations.py` sobre el árbol de la fase (crudo
`modo_completo_final.txt`): **15/18 validations passed, `EXIT=1`**, con `[GUARDA] las 18 etiquetas impresas casan
con el TOTAL dinámico`. Los tres rojos, con su atribución:

| Check | Estado | Dueño |
|---|---|---|
| `Tests` | rojo | **No lo introdujo esta fase.** La firma es la del control S15 (`test_el_control_defectuoso…`, `mtime` vs `nombre`), deuda registrada como roja preexistente en HEAD y gobernada por **FASE-B de este plan** (AC7/AC8). Re-medido en esta sesión: `PYTHONUTF8=1 pytest tests/test_build_lesson_index_s15_fecha_versionada.py` conserva el rojo con esa firma. **Límite declarado:** no se cotejó contra un clon limpio del tip `b32a5ad` |
| `[17/18]` QMind Write-back | rojo **verdadero por AC6** | `contenido: DUPLICADO-VIGENTE` — la era G; dueño operador (S-CIM-2). Es el hallazgo que el plan prevé y no tapa |
| `[18/18]` QMind CONTEXT Freshness | NO-EVALUABLE | la fuente `01a12247-…` no bajó (`error: QMind network request failed`); el `[18/18]` además se invoca **sin `--strict`** — deuda S-CIM-1 / S-2 del hermano, fuera de alcance |

Esta fase **no** auditó su verde con el check recién curado: el `[17/18]` curado no certifica el cierre; se corrió
el modo completo y su crudo está archivado con el estado de cada check. La certificación de contenido es AC10 en
FASE-RELEASE.

## Hallazgo de instrumento: la codificación del lector (deuda S-CIM-10)

La primera corrida del modo completo **no llegó a imprimir su primera etiqueta**: murió en un reader thread de
`subprocess` con `UnicodeDecodeError: 'charmap' codec can't decode byte 0x8d in position 31574` — decodificaba la
salida del hijo con la cp1252 de la consola. No es un rojo del árbol ni de la cura: es el lector. Se re-corrió con
`PYTHONUTF8=1` y esa variable queda estampada en el encabezado de cada crudo de cierre. **No se curó aquí:** la
tabla de conflictos del plan dice «preferencia: no tocar `run_all_validations.py`» y dos dientes leen su fuente
(L-V2.3). Dueño: operador / siguiente mandato sobre el runner; disparador: un AC que fije la codificación del
lector. Dos crudos de la fase conservan bytes cp1252 y se nombran aquí en vez de re-codificarlos a mano
(`quick_apertura.txt`, `dictamen_17-18_strict.txt`): re-codificar un artefacto de consola borra su evidencia.

## Lo que NO se corrió, con su motivo

- **`scripts/validate_opencode_refs.py --fix`** — no entraron rutas **nuevas** bajo `.opencode/`: se editaron
  archivos existentes; la evidencia nueva vive bajo `evidence/`.
- **`scripts/validate_wiring.py --write-report`** — no entraron `.py` **nuevos** al árbol versionado (se editaron
  dos; los arneses de `temp/` no se versionan y se borran). El `--check` del quick manda y quedó verde con su
  denominador impreso.
- **`scripts/validate_plan_citations.py --update-baseline`** — la corrida imprimió `745 citas historicas, 0 nuevas
  y 0 crecimientos (81 archivos en el inventario)`: sin citas nuevas no hay acto visible que simular.
- **`scripts/doctor.py --regenerate-domain-primer`** — **checkpoint declarado**: el contrato §Cierre.6 lo pide «con
  su mandato para escribir el derivado» y esta sesión no lo trae. La fase no añade ni quita módulos.
- **Ninguna subida, ningún borrado, ninguna edición manual del registro.**

## Estado de los cinco cortes

Implementación terminada (AC5, AC6 opción (b) y DA-CIM.9 landed, código congelado) → verificación terminada (POST
57, cuatro mutantes, dictamen real, modo completo archivado) → cierre documental (48 reemplazos en diez documentos
con un solo script de bytes bajo `temp/`, derivados regenerados con su escritor) → **listo para revisión** →
**espera de autorización**. El `git commit` no es el quinto corte ni condición de ninguno: **el árbol queda sin
commitear** porque el mandato dice «sin commit salvo instruccion literal» y esa instrucción no vino en esta sesión.
Tampoco se iniciará FASE-B.

## Estampa de la corrida de cierre (valores impresos por la corrida, ninguno heredado)

| Qué | Valor impreso | Comando e instrumento |
|---|---|---|
| Escritor del índice | `[OK] 371 IDs definidos + 95 sin definición (18 análisis, 450 .md citados)`, `[fechas] nombre=360 commit=11 sin_fuente=0`, `EXIT=0` | `PYTHONUTF8=1 venv/Scripts/python.exe scripts/build_lesson_index.py`; crudo `derivados_cierre.txt`. A2 cerró en 364 definidos / 93 sin definición: las tres lecciones nuevas (`L-CIM.9`, `L-CIM.10`, `L-CIM.11`) salen **definidas** (medido: `grep -cE "L-CIM\.9|L-CIM\.10|L-CIM\.11" .opencode/LECCIONES-INDEX.md` = 3) y los dos seguimientos nuevos del maestro (`S-CIM-9`, `S-CIM-10`) entran al estado explícito de **citados sin definición** que el propio escritor publica |
| Índice fresco (`--check`) | `[OK] Índice de lecciones fresco (371 IDs)`, `EXIT=0` | `build_lesson_index.py --check` |
| Integración documental | `RESULT: All checks passed`, `EXIT=0` | `validate_document_integration.py` |
| Citas históricas | `745 citas historicas, 0 nuevas y 0 crecimientos (81 archivos)` | `validate_plan_citations.py` |
| Modo completo | `TOTAL: 15/18 validations passed`, `STATUS: 3 VALIDATION(S) FAILED`, `EXIT=1` | `run_all_validations.py` con `PYTHONUTF8=1`; crudo `modo_completo_final.txt` |
| Censo remoto | `62` fuentes, `3` nombran al padre, `1` huésped | `fetch_sources()` del instrumento; crudo `censo_qmind_racha.txt` |
| Dictamen `--strict` | `EXIT=1`, `contenido: DUPLICADO-VIGENTE`, `[CONTADOR] 1+1+0==2; 1 fuente(s) huesped(s)` | `validate_qmind_writeback.py --strict`; crudo `dictamen_17-18_strict_toma2_utf8.txt` |
| Registro y instantáneas | `registro.json` intacto; `instantaneas/` en **3** rutas (la tercera es la publicación del hermano JEV en `d47953b`) | `git status --porcelain -uall -- .opencode/qmind-writeback/` (vacío) y `ls -1 … \| wc -l` |

**Nota de instrumento:** los crudos de consola de esta fase nacen de redirección `>` bajo Git Bash. Con
`PYTHONUTF8=1` nacen en UTF-8 y así lo lee el propio modo completo; los dos que se tomaron sin la variable conservan
bytes cp1252 y están nombrados arriba en vez de re-codificados. Su verificación por `git show` aplica solo después de
un commit, que esta fase no hizo.

## Auto-reporte de presupuesto

**Unidad declarada:** `tool_use` **contados a mano sobre las llamadas de esta sesión** (una llamada = 1; los bloques
paralelos cuentan por llamada individual). El instrumento canónico `evidence/FASE-D/measure_iterations.py` sigue
**FUERA DE SERVICIO** (R2.1): pide el transcript del cliente y su acceso está denegado; no se reintentó. Este número
**no es comparable** con las mediciones hechas con ese instrumento.

**Referencia aplicada:** **90 `tool_use`** (DA-CIM.10, contrato §R2).

**Medido al cerrar:** ≈**91** `tool_use`. La primera estampa de esta acta decía ≈84; se re-midió después de las tres
llamadas finales (la verificación de los sellos del registro, el quick final y la comprobación de que ningún arnés
de `temp/` quedó colgando), y el número publicado es el último medido. Dónde se fueron:

| Partida | Aprox. | Procedencia medida |
|---|---|---|
| Lectura de línea base, contrato, maestro, lecciones, dependencias y los tres actas hermanas | ≈12 | siete documentos del plan más el acta de A2 como modelo y los anclajes de los diez documentos de cierre |
| PRE, HEAD, paridad y quick de apertura | ≈3 | tres corridas con crudo |
| Código de AC5 y DA-CIM.9 | ≈8 | seis ediciones sobre `main()`, `do_upload()`, `cuerpo_del_plan()`, `_huespedes_sin_contabilidad()`, `_lineas_huesped()` y `[CONTADOR]` |
| Dientes nuevos y sus dos correcciones de montaje | ≈8 | doce dientes, más el KeyError del fixture `_fuente` y la excepción cruzada del control versionado |
| Censo, dictamen y su re-toma | ≈5 | racha, dos tomas del `--strict`, verificación de que el registro quedó intacto |
| Mutantes | ≈6 | arnés, dos tandas, atribución de la causa única de M1 y el diente re-ancorado para que M3 rompa solo el (i) |
| Cura de la etiqueta y su caracterización | ≈6 | hallazgo de la corrida, `causas_del_rojo()`, M4 y el límite S-CIM-9 |
| Modo completo (dos corridas, una muerta por cp1252) | ≈4 | dos lanzamientos en segundo plano y su lectura |
| Cierre documental | ≈5 | script único de bytes con `--check` (dos anclas rotas corregidas) y derivados |

**Corte usado:** hasta «listo para revisión» (sin autorización literal de commit). **Exceso declarado como
checkpoint** (contrato §R2: exceso → checkpoint y fase INCOMPLETA en esta partida, no una segunda fase): ≈91 contra
la referencia de 90 de DA-CIM.10. La causa medida: el modo completo hubo que correrlo **dos** veces porque la
primera murió decodificando un subprocess con cp1252 (deuda S-CIM-10), y el arnés de mutantes corrió una tanda extra
para re-ancalar el diente de la etiqueta y que M3 pudiera afirmar «rompe solo el (i)». Ninguna de las dos estaba
presupuestada por el mandato; ninguna mueve el alcance de la fase, que quedó completo.

## Lecciones producidas por esta fase

`L-CIM.9` (el resumen agregado de un verificador puede nombrar una causa que la corrida no imprimió), `L-CIM.10`
(un mutante que tumba casi toda la batería no ancla un AC: el ancla es la aserción unitaria del lector, y la
predicción del mandato se mide, no se cita) y `L-CIM.11` (una corrida de cierre puede morir por la codificación del
lector, no por el árbol). Sus filas viven en `10-analisis-post-implementacion.md` §Lecciones Aprendidas, que es su
fuente; aquí solo se referencian.

## Sello del registro y del quick de cierre (escritos después de esta acta)

Alta en `docs/contributing/REGISTRY.md` por su **único escritor**, corrida **después** de los fixers derivados
(índice regenerado) y **con rutas, no con conteos** —se pasó `--dry-run` antes y el render salió con las dos colas
de rutas—:

| Qué | Valor impreso |
|---|---|
| `EXIT_ESCRITOR` | `0` |
| Cabecera `> **Total fases completadas:**` | **518 → 519** (la movió el propio instrumento) |
| Cabecera `> **Ultima actualizacion:**` | `2026-10-09` (la fecha real de esta sesión; el prompt la auto-evaluaba con `$(date +%F)`) |
| Fila | `## FASE-A3 - 2026-10-09`, línea 12138 de REGISTRY |
| `--plan` | **no se pasó** (la forma común de A1 y A2 manda; no hay empate de fase homónima este día) |
| `--archivos-mod` / `--archivos-nuevos` / `--tests` | 16 rutas / 16 rutas / 14; la unidad y las exclusiones viajan en `--nota` |
| Marker `docs/contributing/.last_doc_phase.json` | **16 claves afirmando `FASE-A3`**, efecto colateral del escritor con `--archivos-mod`; viaja en el mismo commit que la fila |
| Quick de cierre (después del escritor) | `TOTAL: 13/13 validations passed`, `EXIT=0`, crudo `registry_fase_a3.txt` |

**Delta declarado, no corregido re-ejecutando el escritor.** La fila registró **16** rutas nuevas y el árbol cerró con
**18**: dos crudos nacieron **después** de la corrida del escritor y no podían estar en su medida —
`registry_fase_a3.txt` (el crudo de esa misma corrida) y `quick_final.txt` (el quick repetido después del acta y de
la limpieza de arneses: `TOTAL: 13/13 validations passed`, `EXIT=0`, y la selección literal repetida sobre el árbol
final: `57 passed`, `EXIT=0`). Es el mismo mecanismo de la 2ª instancia de FASE-A1: el escritor es aditivo y no tiene
bandera de enmienda, así que volver a correrlo apilaría una entrada duplicada (executor §4.5.1) y la diferencia se
declara aquí. La lista autoritativa de rutas la imprime `git status --porcelain -uall` menos las 13 ajenas, no esta
frase. Las 13 rutas staged ajenas (S-CIM-7) siguen excluidas de todo conteo y de toda acción, y **no** se
comitearon ni se des-stagearon.

**El sha de este sello no se estampa aquí:** la fase no commiteó, así que no hay árbol de commit que medir. Si el
operador da la instrucción literal, la verificación se repite sobre el árbol del commit (L-VCF-15) y el pre-vuelo de
packs (`[8/8]` del hook) se corre sobre el árbol del **pathspec** (HEAD + rutas propias), no sobre el índice
completo con las 13 ajenas — cláusula INDICE del mandato.

**Arneses de esta sesión, borrados al terminar:** `temp/censo_a3.py`, `temp/cierre_a3.py`, `temp/mutantes_a3/`
(y su `mount/`), `temp/a3_mod.txt` y `temp/a3_nuev.txt`. Ningún `.py` quedó bajo `evidence/` (contrato §Límites) y
ningún `.py` nuevo entró al árbol versionado, por eso no hizo falta `validate_wiring.py --write-report`.

## Segunda tanda documental, pedida después del cierre (2026-10-09)

El acta de arriba describía el cierre como «48 reemplazos en diez documentos». Falta una capa: al revisar el
contrato §Cierre 2 («actualizar `09` **Secciones A/B**/D/E») se midió que `09` §A y §B seguían con tres filas en
`⬜ A3 (futura)` y que la matriz de hallazgos de `10-analisis` tenía sus columnas **Real** y **Status** en blanco
para los dos hallazgos que esta fase governó. Se escribieron con su medida, no con su promesa:

| Qué se estampó | Valor |
|---|---|
| Reemplazos de la segunda tanda | **10** en 3 documentos (`temp/cierre_a3_tanda2.py`, anclas `count(old) == 1`, borrado al terminar) |
| `09` §B | tres filas `⬜ A3 (futura)` → **✅ A3 (2026-10-09)** (AC5, dictamen de la era G, bloque huésped) y una fila nueva: `causas_del_rojo()` |
| `09` §A | verificado y estampado: **ningún módulo nuevo** en A3 (añadió funciones al verificador existente) |
| `10-analisis` matriz | H-4 y H-5 con su **Real** medido y su **Status** ✅; nacen **H-7** (la etiqueta del resumen, refutada por la propia corrida y curada) e **H-8** (la concurrence, **no curada por decisión de alcance**, con diente de caracterización) |
| `10-analisis` decisiones + maestro §2 | **`DA-CIM.12`** definida (la etiqueta enumera las causas impresas; la concurrence se difiere) y anunciada en el índice de la serie del maestro, para que no nazca como cita sin definición |
| Escritor del índice, re-corrido como último paso | `371 → **372** IDs definidos` (`[fechas] nombre=361 commit=11 sin_fuente=0`), `--check` `[OK] Índice de lecciones fresco (372 IDs)` |
| Integración documental / citas históricas / quick | `All checks passed` · `745 citas historicas, 0 nuevas y 0 crecimientos` · **`TOTAL: 13/13 validations passed`, `EXIT=0`** (crudo `derivados_segunda_tanda.txt`) |

**Corrección del delta de rutas publicado arriba.** La fila de REGISTRY midió **16** rutas nuevas; el árbol, al
cerrar esta segunda tanda, tiene **19** (a `registry_fase_a3.txt` y `quick_final.txt` se sumó
`derivados_segunda_tanda.txt`, y las tres filas de documento editadas ya estaban contadas como modificadas:
**16 modificadas** no cambian). El escritor **no** se re-ejecutó: es aditivo y apilaría una entrada duplicada
(executor §4.5.1), así que la diferencia se declara aquí, que es donde manda la regla de la casa. La lista
autoritativa la imprime `git status --porcelain -uall` menos las 13 rutas ajenas de S-CIM-7.

**Límite de esta tanda, declarado:** la corrección llegó después del sello del registro porque el contrato §Cierre
2 no se re-verificó sección por sección al cerrar; lo detonó la petición del operador. No hay un instrumento del plan
que goberne que las secciones A/B/E de `09` se llenaron — los verificadores gobernaron forma del índice, integración
documental y citas, no esa checklist. Queda como observación para el RELEASE de este plan, no como deuda nueva con
fila propia (S-CIM-1…10 siguen siendo las del maestro §5).

