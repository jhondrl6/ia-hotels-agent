# Análisis Post-Implementación — VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20

> Se crea **desde la concepción** del plan, no al final. Cada fase actualiza su fila, sus lecciones,
> sus métricas y sus seguimientos al cerrar. FASE-RELEASE consolida la matriz.

## Resumen de Ejecución

| Fase | Estado | Iteraciones medidas (unidad e instrumento) | Cortes autorizados | Notas |
|---|---|---|---|---|
| FASE-A | **VERIFICADO OFFLINE 2026-09-21** (AC1–AC5; AC16/AC17/AC18 en su parte de A) | Instrumento canónico **no corrió**: `find . -name "*.jsonl"` = 0 en el workspace (condición D-V2.1, re-medida el 2026-09-21). Se retira la métrica de iteraciones y se publica en unidad contable en disco: **14 rutas propias** en el árbol de trabajo, 933 líneas de instrumento, 23 funciones de test / 28 casos. **No comparable** con auto-reportes en `tool_use` de otros planes | Ninguno: la fase cerró su presupuesto documental y sus 3 tareas de código en la sesión (R3 permitía 4) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`: `informe.json`, `baseline-pre-post.md`, `ac17-y-presupuesto.md`, `mutation/` (verde + 6 rojos), par pre/post y las dos corridas del quick. **Commiteado el 2026-09-21 en `a7564ae`** con el par del índice de lecciones dentro (`[6/7]`) y con los dos archivos ajenos a la fase excluidos a propósito (instrucción literal del operador para el commit y, en una instrucción separada del mismo día, para el push: `a7564ae` y su barrido `e3c4573` ya están en `origin/master`, con el escaneo L3 ofrecido y saltado por el operador) |
| FASE-B | **VERIFICADO OFFLINE 2026-09-21** (AC6–AC9; AC16/AC17/AC18 en su parte de B) | Instrumento canónico **volvió a no correr**: `find . -name "*.jsonl"` = **0** en el workspace, medido hoy (precondición de D-V2.1). La métrica se **retira**, no se estima: no se publica un `tool_use` aproximado, porque contar bloques desde dentro de la sesión no es medible sin el transcript que falta. Unidad contable en disco, declarada no comparable: **11** archivos de código/tests (1 puerta + 2 proveedores falsos + 6 de tests + `conftest.py` + `__init__.py`) y **25** de evidencia (10 de ellos en `mutation/`, 2 en `instrumentos/`), ambos contados con su comando en `baseline-pre-post.md`, no estimados | Ninguno: 3 tareas de código y **0** comandos de larga duración (R3) | Evidencia en `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/`: `informe.json`, `import_scanner.txt`, `contract.txt` (verde `exit 0` + rojo `exit 1`), `costura.json`, `extensibilidad.txt`, `cero-red.txt`, `run_tests.txt` (53 casos), `baseline-pre-post.md` con la resta y `mutation/` (verde + 9 mutantes). **Commiteada el 2026-09-22 en `647f436`** (46 archivos, +4.412/−97) con instrucción literal del operador y con el par del índice **dentro**; los **7** checks del pre-commit pasaron. Dos cosas quedan declaradas y no cerradas: la ruta ajena `EVALUACION-JEV/dependencias-fases.md` **excluida** a propósito del commit, y el **push hecho el 2026-09-22** por instrucción literal: `74d8ff5..b764e8d`, cinco commits publicados —los cuatro de esta fase más el ajeno `eecf246`, que es su ancestro obligado— y paridad `0/0` re-medida tras `git fetch` (los antecedentes de paridad del día: `0/2` al commitear la fase, `0/3` tras `612efd0`, `0/5` tras `cf64faf`: cada commit documental suma uno, así que se re-mide) |
| FASE-C | PENDIENTE | — | — | — |
| FASE-D | PENDIENTE | — | — | — |
| FASE-RELEASE | PENDIENTE | — | — | — |

**FASE-VERIFY no aplica** (criterio 2 de §4.6 cae: no existe fase con ejecución E2E, y además este
plan no hace llamadas de red). Por tanto ningún AC de este plan puede alcanzar `SUPERADO EN E2E`.

## Matriz de Verificación de Hallazgos

| Hallazgo | Medición que lo sostiene | Qué lo previene ahora | ¿Verificable en el artefacto? |
|---|---|---|---|
| A1 — el workflow afirma que `validate_plan_citations.py` es el check 8 del quick | El método `def _check_plan_citations` imprime `[9/11]` | `validate_governance_numbers.py` (FASE-A) | Sí — `findings[]` |
| A2 — el workflow afirma `[9/9]` para la capitalización | `def _check_lesson_capitalization` imprime `[10/11]` | ídem | Sí |
| A3 — el workflow afirma `[12/12]` en el modo completo | **Rectificada el 2026-09-20**: la etiqueta real del write-back es `[15/15]` (la imprime `def _check_qmind_writeback`). La primera versión de esta fila decía `[12/15]`, que es la etiqueta de `def _check_dependencies` — el total (15) sí era correcto y el emisor no | ídem | Sí — y es el ejemplo vivo de por qué AC1 exige emparejar etiqueta ↔ método |
| A4 — el template de lecciones afirma `[10/10]` | La etiqueta real es `[10/11]`; su `[7/7]` del hook **sí** coincide | ídem | Sí |
| A5 — un grep de término devuelve 0 sobre un corpus que sí contiene lo buscado con otras palabras | `grep -icE "verificador mec"` devolvió 0 al concebir el plan | `triage_lesson_relevance.py` publica términos y ceros (AC15) | Sí — `coverage.json` |
| A6 — **las cifras del propio plan vencieron al crearse el plan**: decía 14 análisis / 49 IDs sin definición / 389 `.md` y el índice regenerado pasó a 15 / 50 / 401 | `build_lesson_index.py` contra `head -18 .opencode/LECCIONES-INDEX.md`, medido el 2026-09-20 al verificar este plan | Toda cifra copiada de una fuente dinámica se publica **con su comando y su fecha** y se re-mide al cerrar la fase; no se le cree a la salida de otro verificador | Sí — `00-…` Q4 y maestro §1 |
| A7 — una sesión de fase declara **263.973 bytes ≈ 65.993 tokens** de lectura antes de tocar código, en ocho lecturas, contra un presupuesto de 60 `tool_use` | `stat -c %s` sobre los **siete** documentos que suma la tabla (el octavo que declara leer la fase es un archivo de `evidence/` excluido de la suma), re-medido el 2026-09-20; al concebir dio 254.010 y creció +9.963 con los cierres del propio plan medido; tokens estimados por divisor 4 | `build_phase_briefing.py` (FASE-D) unifica las lecturas declaradas en un pack derivado; **AC20 mide el delta y lo publica aunque sea cero** | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-D/carga.json` |
| A8 — la población bajo el patrón de conteo es mayor que las cuatro aserciones: **22 instancias `[N/M]` en 17 líneas** más 2 formas «check N» en los documentos de gobierno | `grep -rnoE '\[[0-9]+/[0-9]+\]' .agents/` y `grep -rnoE 'check [0-9]+' .agents/`, medido el 2026-09-20; el propio workflow declara en su entrada `v2.24.0` que cuatro de esas menciones son históricas y «se conservan literales» | AC1 con regla de población (viva / histórica congelada publicada / vigente-correcta) y `findings[]` por aserción con `occurrences[]` | Sí — `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/informe.json` → `findings[]`, `historical_excluded[]` |

**Lo que A7 no afirma.** No dice que la lentitud sea solo de tokens: la cadena del otro plan es de
doce fases secuenciales de una sesión y cada fase re-mide once validaciones. Nada de eso lo toca este
plan, y decirlo aquí es parte del cierre honesto.

## Lecciones Aprendidas

Mínimo 3 por fase completada (regla del executor). Formato: **qué pasó / por qué / qué lo previene** +
pertinencia **INCLUIR** o **EXCLUIR** para el siguiente plan.

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

**Catorce filas** capitalizadas: once al concebir (L-R.1, L-R.3, L-R.4, L-NC10, L-PF6, L-PF10, L-D3,
L-V2.3, L-T4A.5, L-VUP-5, L-HF1) más tres que aportó la **capa tibia consultada en la auditoría del
2026-09-20** (L-V2.1, L-V2.2, D-V2.1), sobre **6 dueños distintos** con su efecto concreto nombrado en
la columna «Qué cambia» del propio §2 — no aquí. *(Doble corrección del 2026-09-20: la fila publicaba
**7** dueños cuando las once originales ya tenían **6**, y las tres nuevas no suman ninguno porque
`D-V2.1` está definida en `PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12` — `TRIBUNAL-ENFORCEMENT-OBS`
es donde la **reproducen**, en cuatro fases seguidas. Lo detectó
`validate_lesson_capitalization.py` por `C7`, es decir: el verificador de forma del corpus cazó la
atribución vencida del documento de este propio plan, y el conteo se corrigió re-midiéndolo.)*

### Lecciones nuevas de este plan (L-VCF-1+)

Cerradas en FASE-A (2026-09-21). Cada una con su medición, no con su impresión.

| ID | Qué pasó | Por qué | Qué lo previene | Pertinencia para el siguiente plan |
|---|---|---|---|---|
| **L-VCF-1** | El primer mutation check **falló nombrando a otra aserción**: al apagar el guard de A1 el rojo reportó «se perdió A4» | `assertion_id` se asigna por orden de aparición (así reproduce la tabla A1–A4 del maestro sin pinearla). Es **posicional**: en cuanto un hallazgo desaparece, los demás se re-numeran, y el rojo pasa a hablar de un tercero | `findings[]` publica además `assertion_key` (sujeto + afirmación + documento), que es invariante; todo anclaje de mutante, contract test o diff entre corridas mira la clave, nunca el id. Los seis archivos de `mutation/` muestran las dos columnas | **INCLUIR** — es L-V2.1 en una variante nueva y barata: «el anclaje del mutante no puede ser un entero de posición». Le aplica a cualquier verificador que numere hallazgos |
| **L-VCF-2** | Resolver el sujeto de cada mención por «el script más cercano» produjo un **hallazgo fantasma**: dentro del changelog, un `[6/7]` que *nombra el token* («las 5 referencias normativas al `[6/6]` se actualizan a `[6/7]»`) se atribuyó al verificador de capitalización y dio claimed 6 vs observed 7 | Una instancia puede ser **mención de sí misma** (metarreferencia) en vez de atribución, y la distancia textual no las distingue | Regla de dos partes publicada en el script: (a) una afirmación «del hook» se contrasta **solo por forma** (sus N pasos), sin sujeto; (b) las congeladas salen por H1 (denominador de otra época dentro de `## Versiones`) o H2 (cláusula de evento pasado). Prueba: el mutante `M-POBLACION` — apagar la regla convierte las 8 congeladas en **4 hallazgos extra** | **INCLUIR** — sirve a cualquier lector que empareje texto con código por proximidad |
| **L-VCF-3** | Dos defectos de la **salida**, encontrados al escribir la prueba de estados y no al leer el codigo: (1) la primera linea de la consola no era ASCII —el guion largo de la cabecera llegaba al lector convertido en caracter de reemplazo—; (2) la marca corta esta contenida en la larga, asi que buscar el veredicto con una prueba de subcadena **tambien** es verdad cuando el veredicto es el contrario | La salida legible por maquinas es parte del contrato del instrumento, y la consola de este entorno no es UTF-8 (leccion ya capitalizada: «evidencia de consola no es UTF-8») | `_estado_a_imprimir()` deja la marca en ASCII fija; `test_marca_de_estado_en_ascii` exige `isascii()` y el estado exacto, y los archivos de estado comparan la **primera linea**, no un `in` sobre todo el stdout | **INCLUIR** — para todo verificador cuyo verde se consume por grep o por log |
| **L-VCF-4** | El disparador de **D1** estaba redactado en círculo: «verificador verde y decisión escrita» — pero el verificador solo está verde *después* de la corrección que D1 pide, y esta fase, por diseño (AC17), no puede dar ese verde | Una condición de cierre que solo se cumple al ejecutar lo que condiciona no es un disparador: es una traba | Disparador re-escrito en `dependencias-fases.md` y en la matriz de deuda: *verificador operativo con su mutation check en disco* (cumplido el 2026-09-21) **+** decisión escrita del operador | **INCLUIR** — releer los disparadores de deuda «contra el árbol de la fase que los ejecuta», no solo contra la concepción |
| **L-VCF-6** | El primer mutation check de AC7 apagaba `VERIFICACIONES_DE_FORMA` **entera**, y con la lista vacía la puerta **seguía negándose** a decidir: la conversión a tipos se negó a rellenar la `confidence` ausente. El mutante no podía dar verde, así que no probaba nada sobre los seis guards | Un guard que es una **lista** de verificaciones no es un símbolo mutable atómico: apagarla entera borra seis guards a la vez y, si hay una segunda línea defensiva, el rojo deja de atribuirse a ninguno (L-V2.1 aplicado a una colección, no a un id posicional) | El mutante se re-escribió **uno por guard** (seis vueltas parametrizadas), cada una con un payload que **solo ese guard** ve, y con la aserción `disparados == {guard}` antes de apagar: si el verde no aísla, el test lo dice. Los otros tres mutantes (`M-AC6-token`, `M-AC6-carga-dinamica`, `M-AC6-superficie`) apuntan a símbolos distintos y un test final verifica que no comparten símbolo y que los seis siguen existiendo | **INCLUIR** — para cualquier guard implementado como registro de verificaciones: la unidad de mutación es la entrada, no la colección |
| **L-VCF-7** | La primera versión de la regla de aislamiento marcaba **cualquier** `import_module`/`exec_module` como sospechoso: sobre el árbol real eso producía **16 hallazgos ajenos** (fixtures de otros planes, cargadores de skills) y AC6 habría quedado rojo por diseño | Una regla pensada para un contrabando concreto, aplicada sin distinguir lo resoluble en estático de lo que no, convierte un candado en ruido; y el ruido invita a apagar el candado | Clasificación en dos: carga con argumento **literal** prohibido → hallazgo en cualquier archivo; carga con argumento **no literal** → límite publicado (`cargas_dinamicas_no_resueltas`) que solo escala a hallazgo dentro de la superficie `*proveedores*`, donde sí tiene sentido. Los 16 siguen publicados, con su conteo y sin contar como violación | **INCLUIR** — «un detector que marca todo lo que se parece al delito también marca la prueba del delito»: medir cuántos falsos produce antes de darlo por cerrado |
| **L-VCF-8** | El «0» de AC6 tiene **dos poblaciones** y no eran la misma: `git grep` ve **678** `.py` rastreados y el escáner AST ve **692** en el árbol de trabajo (los archivos de esta fase, aún sin commitear — **rectificado el 2026-09-22**: tras el commit git ve **691** y la diferencia no era toda de la fase, ver **L-VCF-11**). Y el SDK **sí está en el disco**: bajo `tmp_test/venv-jev-sdk`, donde lo aisló el plan hermano | Un «cero coincidencias» afirmado sobre una población que nadie definió se lee como «no existe», cuando lo medido es «nadie lo importa» | `import_scanner.txt` publica las dos cifras con su comando, los excluidos **por directorio con su conteo** (`venv` 7.618, `site-packages` 8.889, `tmp_test` 690, `temp` 65, `build` 14) y la diferencia entre rastreado y árbol; la ausencia del SDK del venv del producto se mide con `find_spec`, no se infiere del grep | **INCLUIR** — antes de afirmar «no hay», medir sobre qué universo y declarar qué exclusiones sostienen el cero |
| **L-VCF-9** | Apareció una contradicción **entre dos ACs del propio plan**, latente hasta que exista un proveedor real: AC6 dice «ningún archivo fuera de `decision_client.py` importa el SDK» y AC9 dice «añadir un proveedor es **un** archivo». Con el proveedor en su propio módulo, la primera obliga a que ese módulo no importe nada y la segunda prohíbe tocar la puerta | Los dos enunciados son ciertos hoy (0 imports, 1 archivo) pero no son compatibles en el único escenario para el que se escribió la costura: D7. Decidirlo aquí habría sido **reinterpretar una restricción del plan en silencio** | No se reinterpretó: quedó escrito (esta fila, el docstring de la puerta y **S10** en Seguimientos) con las dos salidas y su coste — (a) la puerta posee el `import` y el archivo nuevo solo **declara** el módulo, o (b) re-anclar AC6 a «puerta + su directorio de proveedores», que es edición de plan, no de código | **INCLUIR** — un par de ACs que hoy cuadran puede dejar de cuadrar en el caso que justificó el diseño; se detecta escribiéndolo, no esperándolo |
| **L-VCF-10** | «Cero llamadas de red» escrito como afirmación del informe no era verificable, y el primer intento de probarlo con `from conftest import RedProhibida` falló en colección: resolvía al `tests/conftest.py` **raíz**, no al de esta selección (1 test rojo antes de la corrección) | Un guard que no se ejecuta no existe; y en pytest `conftest` no es un importable único bajo colecciones anidadas (es la familia de «la cobertura del verificador se mide»: un ✅ no prueba ausencia) | El guard se expone **por fixture** y hay dos pruebas: que `socket.socket()` bajo el fixture produce `RedProhibida`, y que la costura llega a `RESUELTO` **con el guard armado**. Más la denegatoria AST de 19 módulos capaces de hacer red y el `find_spec` del SDK en el venv. Las tres, en `cero-red.txt` | **INCLUIR** — toda prohibición de proceso necesita un instrumento que falle si se viola; si su prueba depende de un import, que lo resuelva un fixture |
| **L-VCF-11** | Al commitear FASE-B, la resta que la propia fase había publicado **dejó de cerrar por un archivo**: git pasó de 678 a **691** `.py` (+13, los de la fase) pero el escáner seguía en **692**, así que la explicación escrita en `baseline-pre-post.md` («la diferencia son los archivos de esta fase, que aún no están commiteados») quedó refutada por el commit que debía reconciliarla | El denominador se construye excluyendo por **nombre de componente de ruta**, y `.venv-wsl` no está en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`: su `bin/activate_this.py` entra al universo. Y las exclusiones se **solapan** (`site-packages` está anidada dentro de `venv`/`tmp_test`, y el walker incrementa los dos marcadores por la misma ruta), de modo que la suma de las exclusiones no reproduce el universo y no sirve de comprobación aritmética | Descomponer la brecha entre dos poblaciones **archivo por archivo** (`comm` entre `git ls-files '*.py'` y el `rglob` con las mismas exclusiones) en lugar de atribuirla a la fase por defecto. El 0 de AC6 **no se mueve**, y se dice por medición (ese archivo no importa el SDK), no por suposición. Queda como **S11** con su disparador; no se arregló en el barrido porque editar la puerta obliga a re-ejecuciones de sus 53 casos y sus 9 mutantes | **INCLUIR** — dos poblaciones con cifras cercanas no son la misma población: la resta se desglosa o se publica como no desglosada |
| **L-VCF-12** | Al re-medir AC6/A1–A4 para escribir este barrido, `python scripts/validate_governance_numbers.py --report` **sobrescribió la evidencia commiteada de FASE-A**: la ruta de escritura está hardcodeada como default (`REPORT_DEFAULT` → `evidence/…/FASE-A/informe.json`) y el comando canónico que el propio plan publica no lleva destino. Cambió tres campos: `generated_at`, `medido_el` y `funciones_test_en_disk` (4.330 → **4.378**, que es una medición **verdadera** escrita sobre el registro de otra fase). Se revirtió con `git checkout -- <ese archivo>` y se re-midió con destino explícito (`--report temp/…`), que deja FASE-A limpia y da el mismo `HALLAZGOS` con `exit 1` | Un verificador que además es **writer** gobierna dos artefactos, y aquí el segundo es un registro fechado de otra sesión: cada corrida re-escribe el pasado. Es la familia de L-VCF-11 (el instrumento afectado por su propio uso) y la de «quién produce el dato publicado», en su variante peligrosa: **el verde se publica pisando una evidencia ajena** | Separar lector de writer: `--report` sin destino debe **imprimir y no escribir** (o exigir `--out` explícito), y la evidencia de cada fase se escribe con su ruta nombrada en el comando publicado. Registrado como **S12**; mientras tanto, todo re-muestreo de este verificador se hace con destino explícito y se declara | **INCLUIR** — antes de correr cualquier verificador del repo con `--report`/`--write`: mirar si su default toca evidencia commiteada |
| **L-VCF-5** | Al medir «quién afirma el 11» (AC5/AC16, barrido de `tests/` por L-V2.3) resultó que **esta misma fase añadió 4 pins nuevos del denominador 11** en `tests/`: la aserción `observed == 9/11` del contrato AC1 es, literalmente, un pin | Un test que fija el valor observado de una fuente dinámica *es* una de las fuentes estáticas que el plan denuncia; la familia no cubierta (iii) de AC2 no era teoría | Se declaró en `baseline-pre-post.md` con dueño (D1/D2: al corregir `.agents/` o renumerar el quick, el test se re-ancla con su nota datada) en lugar de debilitar la aserción para que la resta quedara limpia | **INCLUIR** — «medir a quién le duele la renumeración» incluye medirse a uno mismo |

## Seguimientos abiertos

| # | Tema | Dueño | Disparador |
|---|---|---|---|
| S1 | D1: corregir o retirar las aserciones A1–A4 en `.agents/` | FASE-RELEASE de este plan | **Disparador reformulado el 2026-09-21 (era circular, L-VCF-4):** verificador operativo con mutation check en disco (ya cumplido) **y** decisión escrita del operador sobre la forma de la corrección; configuración central |
| S8 | Los **4 pins del denominador 11** que FASE-A escribió en `tests/` al fijar el contrato AC1 (`test_governance_numbers_reproduce_A1_A4.py`) | D1/D2 de este plan | Al corregir `.agents/` (D1) o al promover el verificador a check 12 (D2): re-anclar el test con nota datada, **sin** limar la aserción (L-VCF-5) |
| S9 | El verificador **no está cableado** a ningún gate: corre suelto (`python scripts/validate_governance_numbers.py --report`, salida 1 con A1–A4 presentes). Promoverlo al `--quick` es exactamente **D2** y rompería la cifra que `REFACTOR-WHATSAPP` pinea en cuatro documentos | D2 | Sesión previa al `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S2 | D2/D3: promover el verificador al `--quick` y rebanar el workflow | Plan propio posterior | Sesión previa a `FASE-RELEASE` de `REFACTOR-WHATSAPP-ENTREGA-2026-09-18` |
| S3 | **D6: lint de contradicciones semánticas** (`validate_plan_semantics.py`) | Plan propio posterior; entra en **este** directorio si el disparador se cumple vigente este plan | El `acceptance` que publique AC15 en FASE-C. Si el triaje sale inaceptable, **no se activa** |
| S4 | **D7: activar el proveedor de decisiones ya habilitado** y correr la comparación | Plan propio posterior | Decisión del operador del 2026-09-20 de no entrar ahora; AC9 dejó la costura probada **el 2026-09-21** (`files_changed_to_add_provider = 1`). Al activarlo cae la decisión de **S10** |
| S10 | **Dónde vivirá el `import` del SDK cuando D7 se active**: la puerta (y el archivo nuevo solo declara) o re-anclar AC6 a «puerta + directorio de proveedores». Las dos son coherentes con AC9; solo una con la letra de AC6 | Quien ejecute **D7** — no este plan: decidirlo aquí habría sido reinterpretar una restricción en silencio (L-VCF-9) | Que un proveedor real vaya a quedar detrás de la costura. Está escrito en el docstring de `decision_client.py`, en `extensibilidad.txt` y en la lección L-VCF-9 |
| S11 | **✅ ACEPTADA el 2026-09-23 — corregida fuera de este plan.** **El denominador de AC6 admitía un archivo de entorno no declarado**: `.venv-wsl/bin/activate_this.py` entraba en los 692 `.py` que escanea `iterar_py()` porque `.venv-wsl` no estaba en `ARCHIVOS_EXCLUIDOS_DE_LA_POBLACION`. Y las exclusiones se solapan (`site-packages` anidada en `venv`/`tmp_test`), así que su suma no reproduce el universo. El numerador no se mueve: **0** imports prohibidos re-medido el 2026-09-22 | ~~Quien toque `decision_client.py`~~ → **bloque A de `ORDEN-CAMBIO-CALIDAD-PROCESO-2026-09-22.md`**, que la ejecutó en `fdd397f` con sus pruebas de exclusión y publicó el conteo ⟦**rectificado el 2026-09-23**: esta fila decía «con su test de población (2 funciones)». Medido con `git show fdd397f`, la cura de S11 vive en `tests/quality_gates/decision_client/test_decision_client_aislamiento_imports.py` (**+83/−11**, tres funciones: `test_un_directorio_de_venv_se_excluye_y_su_exclusion_se_publica_con_su_conteo`, `test_en_el_arbol_vigente_un_venv_presente_aparece_como_exclusion_publicada`, `test_exclusiones_solapadas_no_inflan_el_denominador`), **no** en `governance_numbers`⟧ | Cerrada por ese bloque con **corrección técnica**; el **cierre contractual** (la enmienda en este plan, que el propio resumen del bloque A §4 declaraba pendiente) quedó registrado el 2026-09-23 en `dependencias-fases.md` §Conciliación. **Re-validación offline de esta sesión:** población escaneada **696** vs `git ls-files '*.py'` **696** → **residuo 0**, `--scan-imports` con `exit 0` y `excluidos_por_directorio` publicando `.venv-wsl`: 582. **Sus pruebas también corrieron aquí:** selección `decision_client` → **87 casos, `EXIT=0`**, que es donde viven las tres funciones de exclusión de S11 |
| S12 | **✅ ACEPTADA el 2026-09-23 — corregida fuera de este plan.** **`validate_governance_numbers.py --report` escribía por default dentro de la evidencia commiteada de FASE-A** (`REPORT_DEFAULT`): cada corrida re-escribía `generated_at`, `medido_el` y el conteo inyectado, o sea **pisaba el registro fechado de otra fase**. Medido y revertido el 2026-09-22 (`git checkout --` sobre ese archivo; re-muestreo con destino explícito dejaba FASE-A limpia y el mismo `HALLAZGOS` con `exit 1`) | ~~FASE-RELEASE de este plan~~ → **bloque A de la orden de calidad**, que trasladó la ejecución a su §4.A (FASE-RELEASE tiene prohibido editar código) y la corrigió en `fdd397f` con **6 funciones** en `tests/quality_gates/governance_numbers/test_governance_numbers_s12_report_no_escribe.py` (**+97/0**, medido con `git show`) ⟦**rectificado el 2026-09-23**: esta celda decía «+ 5 tests»; la cuenta real es 6, y el directorio completo suma **35 funciones / 40 casos**⟧ | Cerrada por ese bloque con **corrección técnica**; el traslado contractual se aceptó el 2026-09-23. **Re-validación offline:** `--report` sin destino → `exit 1`, stdout JSON con A1–A4, stderr avisa que no escribió, y el `sha256` de `evidence/…/FASE-A/informe.json` queda **idéntico** antes y después con `git status --porcelain evidence/` vacío. **La guarda publicada en el README para FASE-C queda sin efecto** (rectificada el 2026-09-23); la lección **L-VCF-12** sigue vigente como regla general. **Sus pruebas sí corrieron en esta sesión** (era la deuda del cierre): las 6 regresiones por nombre → `6 passed, EXIT=0`, y la selección del directorio → `40 passed, EXIT=0` en `evidence/…/CONCILIACION-B-Y-CONTRATO-C-2026-09-23/pytest_{seleccion_governance_numbers,s12_report_no_escribe}_2026-09-23.txt` |
| S13 | **Nueva, hallada al re-evidenciar R2.8 el 2026-09-23: el arnés de mutación de FASE-A escribe por ruta hardcodeada en evidencia de otra fase.** `tests/quality_gates/governance_numbers/test_governance_numbers_mutation_por_asercion.py` (la constante `EVIDENCE`, definida junto a `SCRIPT` y sin parametro de destino) apunta a `evidence/…/FASE-A/mutation/`, así que correr el test **re-escribió 7 archivos cerrados de FASE-A** (`verde_baseline.txt` + los 6 mutantes). Esta vez sin daño: los 7 `git hash-object --path` casan con HEAD y `git status --porcelain evidence/` quedó vacío, o sea bytes idénticos con mtimes movidos — que es justo lo que hace invisible el patrón. Es la familia **S12 / L-VCF-12** sobreviviendo en un test que la cura del bloque A no cubrió (esa cura alcanzó a los dos verificadores, no al arnés) | Quien toque ese test — **no esta sesión**, que no edita código ni tests (AC17 y el mandato de la conciliación). Se registra con dueño, no se lima | Al promover `validate_governance_numbers.py` a check 12 (**D2**), o cuando FASE-C necesite su propio mutation check sobre `triage_*` (AC14) y tenga que elegir destino de escritura |
| S5 | D8: la consulta Q7 de QMind **sí se ejecutó** en la auditoría del 2026-09-20 (cuatro `retrieve`; el comando válido usa el ID del notebook, no su nombre) | FASE-RELEASE | Re-correr solo si el corpus del notebook cambió desde la auditoría, y verificar que las citas de L-V2.1/L-V2.2/D-V2.1 siguen en pie |
| S7 | **D10: re-leer la interfaz del write-back antes del cierre** — `VERIFICADOR-ESCRITURA-QMIND-2026-09-20` declara dentro de su alcance `validate_qmind_writeback.py` y su conexión en `run_all_validations.py`, y piensa añadir `--title`/`--file` | FASE-RELEASE de este plan | Al llegar el cierre: `--help` contra el árbol vigente y re-escribir el orden de `04-contrato-ejecucion.md` si la firma cambió |
| S6 | D4/D5: verificadores de la resta pre/post (R2.7) y del par verde/rojo (R2.8) | `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` §Deuda | Ya asignados antes que este plan; no se reasignan |

## Métricas de Ejecución

- [x] **FASE-A (2026-09-21), en la misma base de medición que su par pre/post** (R2.3): quick
  11→11 (resta 0), hook 7→7 (resta 0), población A8 22/17/2 → 22/17/2 (resta 0), selección de tests
  0→23 funciones (+23, **no** 0: la fase agrega tests y lo dice), canónicas del repo
  4.307→4.330 (resta +23, coherente con la fila anterior). Crudos en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-A/`.
- [x] **FASE-B (2026-09-21), misma base de medición que su par pre/post** (R2.3): quick 11→11
  (resta 0), etiquetas del modo completo 4→4 (resta 0), hook 7→7 (resta 0), `git diff` de los cuatro
  scripts gobernados **vacío**, bytes de `.agents/` 98.694/6.123 **idénticos** (AC17), población AC6
  678→678 rastreados y 690→692 en el árbol (**+2**, no 0: los dos instrumentos que la fase escribió para generar su propia evidencia; ver `FASE-B/baseline-pre-post.md` nota 3), imports prohibidos fuera de la puerta 0→0, pins
  del 11 en `tests/` 4→4 (esta fase **no** añadió ninguno, a diferencia de A). Lo que sí se movió y se
  declara aparte: selección de tests 0→**48 funciones / 53 casos**; canónicas del repo
  4.330→4.378 (resta +48, coherente con la fila anterior). Crudos en
  `evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/FASE-B/`. **Rectificación medida el 2026-09-22, al
  commitear la fase (`647f436`)**: los `.py` rastreados pasaron de 678 a **691** (+13 propios) y el
  numerador de AC6 **sigue en 0** re-medido con la puerta sobre los mismos 692 del árbol; la resta
  692−691 se desglosó y dio `.venv-wsl/bin/activate_this.py` → **L-VCF-11** / **S11** (ver nota 4 del
  par pre/post).
- [x] **AC9 medido, no afirmado**: `files_changed_to_add_provider = 1` (`costura.json`) con
  `agregados = [falsos_proveedores/falso_segundo.py]`, `modificados = []`, y despacho de los dos
  proveedores por la misma puerta con respuestas **distintas** (si contestaran igual, el 1 sería humo).
- [x] **Lo que se pospuso (D7) y qué cuesta posponerlo.** No entra ningún proveedor real, y eso tiene
  cuatro consecuencias escritas: (i) ningún AC de este plan mide calidad de decisiones de un modelo —
  miden forma, aislamiento y no-regresión; (ii) **D6** queda sin su consumidor natural, así que su
  disparador depende del `acceptance` de FASE-C y no de un proveedor ya probado; (iii) la pregunta de
  geometría de **S10** se paga entera en D7 y su coste real puede ser una edición de plan (re-anclar
  AC6) si se elige la ruta (b); (iv) el manifiesto de dependencias del SDK no lo mide AC9, porque
  medirlo exigiría activarlo. Lo que **no** cuesta: la costura ya está, con su contract test y su
  coste de extensión verificado, así que D7 no reabre FASE-B.
- [x] Coherencia del índice de lecciones al commitear: `build_lesson_index.py` regenerado el
  2026-09-21 tras escribir los `.md` de esta fase; el commit debe llevar los dos archivos dentro
  (`[6/7]` del hook lo corta). **Cumplido en los dos commits**: `a7564ae` (FASE-A) y `647f436`
  (FASE-B, el 2026-09-22, con `LECCIONES-INDEX.md` 24+/17− y `lecciones_index.json` 100+/14− dentro y
  los **7** checks del hook en verde).
- [ ] **Carga de lectura por fase, antes y después del pack (AC20)** — con su comando y su divisor.
- [ ] Aceptabilidad del triaje (AC15): propuestos pertinentes / total propuestos.

## Decisiones Arquitectónicas

- [ ] El pack se genera dentro del plan y **no** sustituye ninguna lectura canónica (alternativa
  descartada: rebanar `.agents/`, que es D3 y exige tocar configuración central en vuelo).
- [x] FASE-B deja un solo proveedor configurable y **no** compara (alternativa descartada: mantener
  el AC9 de comparación, que con un solo proveedor se cerraba declarando `NO-EJERCITADO` y certificaba
  humo). **Aplicado el 2026-09-21 y legible en el artefacto**: `extensibilidad.txt` declara que la
  comparación es D7 y `costura.json` certifica la geometría con `1`.
- [x] La resolución del proveedor es **por entorno y sin default** (aplicado el 2026-09-21).
  Alternativas descartadas con su coste: (a) *proveedor por defecto si el entorno falta* — es
  exactamente lo que L-PF6 castiga: una decisión que nadie pidió; (b) *un registro central de
  proveedores que la puerta importa* — cerraba AC9 en **2** archivos (el nuevo más el registro), que es
  el número que la medición rechazó; (c) *descubrimiento por `entry_points` o paquetes instalados* —
  habría obligado a instalar el SDK para probar la costura, rompiendo el cero red y el «sin
  credencial». Coste de la ruta elegida: el directorio de proveedores lo nombra el entorno y no hay
  ruta por defecto que descubrir, así que `NO-CONFIGURADO` imprime la ruta que buscó.
- [x] La `confidence` es **obligatoria** en `choice`/`score` y **prohibida** en `noul`, y la puerta no
  rellena la que falta (aplicado el 2026-09-21, con su mutante `M-AC7-forma-choice` y su prueba
  anti-default). Alternativa descartada: aceptar un `noul` con confidence rellenada a 1.0, que
  fabricaría el eje con el que FASE-C separa «actué» de «no estoy seguro» (AC12).
- [ ] El triaje es aditivo y no filtro, con el coste de esa elección medido en FASE-C.
- [x] **⟦Contrato de C cerrado el 2026-09-23; su EJECUCIÓN sigue pendiente⟧** La pregunta de
  pertinencia es **`choice` de dos opciones**, no `noul`. Alternativa descartada y cara: usar `noul` y
  leer `probabilidad_si` como si fuera confianza — la puerta **prohíbe** `confidence` en `noul`
  (`RespuestaNoul.confidence = None` con su `confidence_motivo`), así que ese umbral gobernaría otra
  cosa y cerraría AC12 con una métrica que el AC no describe. Coste de la ruta elegida: cada candidato
  carga dos números y hay que publicarlos separados.
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ AC11 toma la ruta (b):** C consume
  `lecciones_index.json` **tras ejecutar él mismo** la comprobación de frescura. Alternativas
  descartadas con su coste: (a) `build_lesson_index.build()` en memoria — un solo lector y sin verde
  heredado, pero **borra el estado `VENCIDO`**, y AC11 pide tres estados; (c) la tercera vía prohibida
  por L-V2.2 — leer el JSON confiando en que `[6/7]` del hook lo regeneró, que es heredar un verde de
  otro gate. Coste de (b): C es responsable de su suelo y hace dos lecturas del JSON por corrida.
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ Una propuesta del proveedor falso NO entra en §2 sin
  revisión humana.** Alternativa descartada, que era la instrucción original del paso 6 del prompt de
  C («aplica lo que proponga»): auto-escribir en el documento de lecciones una fila cuya única
  evidencia es la respuesta de un fixture determinista — fabricaría la pertinencia que AC15 declara
  `NO-EJERCITADO`, y es la familia `VACUOUS_RECALL` que la matriz §2 ya rechazó. Coste aceptado: C no
  puede cerrar «se auto-trió y aplicó» en una sola sesión; el rechazo se publica igual que la
  aceptación, porque una fila de §2 no desaparece (AC10).
- [x] **⟦Contrato de C cerrado el 2026-09-23⟧ C conserva el workflow canónico y el proceso común
  vigentes** (orden de calidad §4.C: sus bloques B y C quedan **diferidos, no aplicados ni cerrados**).
  Alternativa descartada: aprovechar la sesión piloto para «modernizar» el executor y `AGENTS.md` —
  colaría un cambio de gobierno por arrastre de una fase y rompería la comparabilidad de la medición
  D3/A7, que se hizo contra las reglas actuales. Coste: C vuelve a pagar la lectura de A7 sin alivio.
- [x] Forma de descubrir aserciones en los documentos: **patrón sobre la fuente, no lista fija**
  (decisión aplicada el 2026-09-21 en FASE-A). Alternativas descartadas, con su coste:
  (a) *hardcodear A1–A4* — cerraba AC1 en verde y dejaba el verificador ciego ante la aserción
  siguiente, que es el defecto L-NC10 que este plan denuncia;
  (b) *descubrir sin regla de clases* — producía 8+ hallazgos sobre menciones históricas que el
  propio workflow declara literales, es decir el rojo «por diseño, no por defecto» que A8 anticipó;
  (c) *excluir lo histórico sin publicarlo* — un candado que excluye en silencio (L-HF1).
  Coste de la ruta elegida: dos tablas de marcadores (`KIND_MARKERS`, `HISTORICAL_EVENT_MARKERS`)
  publicadas en el script y mutables: la exclusión es auditable y reversible, no magia.
- [x] FASE-A **no edita `.agents/`** ni toca la composición del `--quick` (AC17/AC16): el verificador
  reporta; la corrección de las cuatro aserciones es D1 con instrucción literal.
- [x] FASE-A **no se cablea** a ningún gate ni al hook: se promueve o no en D2, con la medición de
  quién afirma el 11 ya hecha (AC5/AC16).

## Checklist de Cierre (llenar en FASE-RELEASE)

- [ ] Los cuatro scripts en `scripts/`, con sus tests y su evidencia de mutation check.
- [ ] Ningún AC promocionado sin respaldo legible en el artefacto (R2.4).
- [ ] `--quick` en 11 checks y hook en 7, composición intacta (AC16).
- [ ] S1–S7 con dueño y disparador vigentes; **D6 resuelta con el número de FASE-C, no con opinión**.
- [ ] Write-back → índice → `git mv` → índice, en ese orden (R2.5, R2.10).
