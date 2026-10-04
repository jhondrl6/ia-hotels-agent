# Cobertura por Modulo - historial de rondas

> **Procedencia**: las notas fechadas de `AGENTS.md` §Cobertura por Modulo, trasladadas **verbatim** el 2026-10-01
> para sacar ese archivo de los umbrales de tamano del contexto del agente (45,138 chars / 46,883 bytes contra
> 40,000 chars y 32,768 bytes). No se borro ni se reescribio ninguna linea: son las mismas, en el mismo orden.

> **Regla de aparcado**: la ronda que cierra escribe aqui su nota, arriba del todo (orden cronologico descendente,
> como estaba en AGENTS.md). En `AGENTS.md` solo se mueve la cifra de la cabecera
> `### Cobertura por Modulo (N funciones totales)` y la fila de la tabla que le corresponde. La cifra corriente, el
> metodo canonico (`grep -rE "^\s*def test_" tests --include=*.py`) y el retrato por modulo siguen viviendo alla.

> **Instrumentos que leen `AGENTS.md` y no este archivo**: `scripts/validate_agents_md.py::check_2_test_count`
> toma la **primera** ocurrencia de `N funciones`; el instrumento de cierre de ronda suma la tercera columna de la
> tabla desde la cabecera. Por eso cabecera y tabla no se mudan.

---

> **Ronda del 2026-10-03 — OLA 2 (CONTINUACION 2) DEL PILOTO JEV (la cifra sube a 4,776).** Medido con el
> metodo canonico sobre el arbol de trabajo (`grep -rE "^\s*def test_" tests --include=*.py` = **4,776**) y
> contrastado con el arbol versionado (`git grep -c -E "^\s*def test_" HEAD -- tests` sumado = **4,717**):
> el delta de **59** es trabajo de esta tanda todavia **sin commitear**, o sea las dos cifras no se
> contradicen -midieron arboles distintos- y la commiteada subira a 4,776 cuando este rango entre.
> Antecedente: **4,717** (mas arriba en esta misma pagina, la pata (b) del ledger, tandas de OLA 1 y de la
> continuacion 1 del mismo dia).
>
> Atribucion por archivo, medida por directorio y no derivada de la fila anterior: **+54** en
> `tests/quality_gates/` — 14 en `jev_pilot/test_jev_pilot_sdk_ac9.py`, 15 en
> `jev_pilot/test_jev_pilot_run_guards.py`, 10 en `jev_pilot/test_jev_pilot_deepseek_brazo.py`, 14 en
> `jev_pilot/test_jev_pilot_protocolo_check.py` (13 del paso 6 mas el diente del elegible sin fila, que
> nacio de la corrida k=8) y 1 en `decision_client/test_decision_client_aislamiento_imports.py` (el
> contrafactual de la excepcion de cero red que autorizo el operador) — y **+5** en la pata de raiz: las 5
> funciones del nuevo `test_validate_wiring_diente_mudanza_1_3.py` (la mudanza (a) de la fila 18 del
> `33-registro-unificado`). Aritmetica de la tabla: quality_gates 888 → **942**, root 1058 → **1063**,
> cabecera 4,717 → **4,776**.
>
> La cuenta se declaro mal una vez dentro de la misma ronda y se re-midio: el primer estampado fue
> 4,775 / 940 / 1064, y estaba mal sumado porque el contrafactual del hermano -que vive en
> `tests/quality_gates/decision_client/`- se conto en la fila de raiz. Ninguna de las dos versiones se
> commiteo, asi que no hay errata que abrir; lo que queda registrado es el metodo: cada fila se mide por
> su directorio (`grep -rE ... tests/quality_gates | wc -l`, y lo mismo sobre `tests/*.py`), no restando
> deltas a la cifra anterior.
>
> Instrumento y dos notas de instrumento, porque la ronda dejo medidas y no supuestas:
> (a) el par de mutacion se corri6 sobre los archivos reales con restauracion por sha256 en `finally`
> (`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/mutation.json`: 10 mutantes, 10 caen por la causa
> nombrada, 0 restauraciones fallidas). Dos de sus caidas son hallazgos sobre el propio test, no sobre el
> codigo: `test_error_kind_clasifica_subclases_por_su_antecesor` estaba verde **sin diente** (su subclase
> ya estaba nombrada en la tabla, o sea apagar la caminata del MRO no la movia) y el ancla de
> `request_id` era prefijo de una linea mas larga, con lo que mutaba la entrada ajena y daba verde con el
> defecto puesto. Ambos se corrigieron aqui.
> (b) cuatro de los diez mutantes salieron primero NO-APLICADO por comparar literales con `\n` contra un
> arbol checkado en CRLF: un mutante que no casa no es un verde, es un cero que hay que publicar. El arnes
> traduce el literal al EOL real y emite `ocurrencias_del_literal` por mutante.
>
> Lo que esta ronda **no** suma y se declara: la bateria completa no se corro (no se pidio), el diente de
> aditividad sobre `triage_lesson_relevance.py` (AC6 del prompt de FASE-B) sigue NO-EJERCITADO por no estar
> esa ruta en el mandato, y P4 cayo en 401 del servicio, con lo que la corrida de recuperacion k=8 no se
> corri6 y los techos `tokens_in`/`tokens_out` del protocolo siguen en null. Nada de eso entra en la cifra.

> **Ronda del 2026-10-03 — OLA 2 DEL PILOTO JEV (la cifra sube a 4,717).** Medido con el metodo canonico de la
> casa (`grep -rE "^\s*def test_" tests --include=*.py` = **4,717**) y contrastado con el arbol versionado
> (`git grep -c -E "^[[:space:]]*def test_" HEAD -- tests` sumado con awk sobre el commit que lleva la pata (b)
> = **4,717**): **las dos cifras cuadran**. Antecedente: **4,706** (ronda del 2026-10-02, medida sobre `4621049`).
> El delta (+11) se atribuye por archivo, sin mas sumandos: **+11** en
> `tests/quality_gates/jev_pilot/test_jev_pilot_ledger_fase_b.py` (0 → **11**), la pata (b) del ledger del runner
> - `attempts`, `error_kind` y `usage_normalized` - que nace en `scripts/evaluate_jev_pilot.py` porque la costura
> declara que no le pertenecen. Su diente no es decorativo: `reservar_presupuesto` niega `max_reintentos` distinto
> de 0 porque el default medido del SDK 0.7.0 (`RetryPolicy(max_retries=2)`) produce **3 intentos** facturables
> ante un 429, y `normalizar_usage` trata el uso desconocido como estado y no como cero (medido: `Usage()`
> resuelve `(None, None)`). El control negativo se ejecuto sobre el instrumento versionado: `git show HEAD:` del
> guard viejo deja pasar `typesafe_sdk`, que es el nombre real del modulo - la lista prohibida nombraba `typesafe`,
> un modulo que no existe y por eso nunca mordo.
>
> Nota de instrumento, declarada porque el error fue mio y dos veces: la primera medicion de fines de linea uso
> `grep -c $'\r'` con el patron vacio, o sea conto **todas** las lineas y fabrico un CRLF generalizado que no
> estaba (los numeros salian iguales al conteo de lineas); el segundo intento en Python conto `b[13:14]`, que es
> el byte en la posicion 13 del archivo y no el CR. Medido por bytes con `bytes([13])` salio la verdad: cuatro
> archivos en LF y **dos** crudos de sesion si venian en CRLF, por ser redireccion de stdout de Python/pytest
> bajo Windows; normalizados con asercion de lineas intactas (31 y 14, menos 31 y menos 14 bytes). La unidad
> viaja con la cifra, que es la regla de la casa.

> **Poda del 2026-10-02 — D-2 = (c), decidida por el operador: la prosa fechada que sobrevivia en `AGENTS.md` se
> corta y su texto se rescata aqui, verbatim en sus palabras.** Medido antes de cortar con **dos** instrumentos y
> no con uno: el que enumera literales (`python temp/chequea_duplicado.py`) dio **12 de 12 presentes** y dejo
> pasar el corte; el que enumera **frases** (`python temp/prueba_perdida_frases.py`, sobre el bloque leido de
> `git show HEAD:AGENTS.md` y no del arbol que se estaba editando) dio **0 de 6 copiadas**. La diferencia es el
> hallazgo y vale como nota de instrumento: la trasladacion del 2026-10-01 trajo a este archivo la *informacion*
> de esas rondas, reescrita y mas completa -la nota de la tanda ADOPCION-Y-CIERRE-DEUDA y la del CIERRE-DEUDA
> dicen lo mismo con otras palabras y con mas dientes-, pero no sus **frases**, y entre las seis perdidas estaba
> la regla normativa «La unidad viaja con la cifra, que es la regla de la casa». Un conteo de literales no cazó un
> texto que se iba. Por eso el bloque no se borra: se traslada, y queda abajo.
>
> Y una nota sobre el instrumento de frases: su primera version comparaba los dos lados con normalizacion
> distinta -dejaba los `>` de la cita en el historial y se los quitaba al bloque-, asi que despues del rescate
> seguia dando 5 de 6 faltantes con el texto ya puesto. Nivelada la comparacion dio **6 de 6 presentes y el bloque
> completo verbatim**. El cero de antes del corte era cierto (el texto no estaba); el rojo de despues era del
> instrumento. Se declara porque es la misma trampa de delimitadores que la casa ya registro.
>
> Lo que no se toco, verificado con `grep -c` despues de cortar: la cabecera `### Cobertura por Modulo (4,706
> funciones totales)` = 1 y la fila `| quality_gates | 877 |` = 1. El diff es **1/14** (una linea reescrita,
> catorce menos; 551 lineas pasan a 538). La razon de la poda no es estetica: mientras la cifra de una ronda este
> escrita en `AGENTS.md`, el primer commit ajeno la vuelve a vencer -que es exactamente lo que hizo `4621049` al
> subir el arbol a 4.706 sin llevar el archivo-. Hasta hoy este archivo era la fuente unica de la cifra; desde hoy
> lo es tambien de la prosa.
>
> Residuo declarado y **no** corregido, porque el mandato pedía conservar el parrafo intacto: la cabecera del
> parrafo siguiente sigue diciendo «las notas medidas entre 2026-09-11 y 2026-10-01», y en este archivo hay notas
> del 2026-10-02. Su cota alta esta vencida por un dia, y es el mismo tipo de literal que se acabo de podar, así
> que queda registrado como candidato a la misma cura. Dueno: el operador.
>
> **Ese residuo quedo cerrado el 2026-10-02, en el acto siguiente y por su letra (b), decidida por el operador.**
> El parrafo de `AGENTS.md` ya no lleva rango de fechas: apunta al archivo y describe el orden. No se re-ancló la
> cota a 2026-10-02, que es la via (a) y habria vuelto a vencer al commit siguiente; se retiro el literal, que es
> la cura estructural. Medido despues del cambio: `grep -c "2026-09-11 y 2026-10-01" AGENTS.md` = 0, y la unica
> mencion versionada que queda del rango es la de esta nota, que lo cita para declararlo cerrado. La cabecera del
> parrafo de arriba («no corregido») se deja intacta a proposito: describe el estado que esa nota registro, y su
> cierre vive aqui, como nota fechada anadida sobre evidencia publicada.
>
> **Texto rescatado** (las palabras exactas que estaban en `e507193`; re-empaquetada solo la longitud de linea,
> 1.267 caracteres): «En el commit que lleva esta nota **los dos comandos dan 4,699** (medido 2026-10-01 sobre
> `9181197`, tanda ADOPCION-Y-CIERRE-DEUDA): el +1 contra la segunda ronda de la manana sale de un archivo y se
> atribuye en `docs/cobertura-historia.md` — `tests/test_diagnostic_geo_metrics.py` (5 → 6, el diente de
> delimitadores de la fila 17 del registro 33-). La unidad viaja con la cifra, que es la regla de la casa. La
> ronda anterior subio `4,688 → 4,698` (medida sobre `c4d0ffe`, segunda ronda del dia): el +10 contra la ronda de
> la manana salia de tres archivos y se atribuyo archivo por archivo en `docs/cobertura-historia.md` —
> `tests/test_registry_fecha_documental.py` (20 → 25), `tests/financial_engine/test_pricing_resolution_wrapper.py`
> (36 → 39) y `tests/test_diagnostic_geo_metrics.py` (3 → 5). Las diez viajaron con la cifra, que es la regla de la
> casa. La nota anterior de hoy subio `4,584 → 4,688` sobre `ed3670e` y ya dejo escrita la razon: la afirmacion de
> `4,584` estaba vencida en los dos sentidos — ni el arbol ni HEAD daban ese numero. Eso es el estado de **ese
> commit**, no un invariante: en cuanto una edicion deje funciones test fuera del arbol versionado, las dos cifras
> vuelven a separarse — y asi paso los dias 25 y 26 de este mes, dos veces cada uno.»

> **Ronda del 2026-10-02 — CIERRE DE UMBRALES Y CIFRA (la cifra subio a 4,706).** Medido con el metodo canonico
> de la casa (`grep -rE "^\s*def test_" tests --include=*.py` = **4,706**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests` sumado por awk sobre `4621049` = **4,706**): **las dos cifras
> cuadran**. Antecedente: **4,699** (tanda ADOPCION-Y-CIERRE-DEUDA del 2026-10-01, medida sobre `9181197`). El
> delta (+7) se atribuye por archivo, sin mas sumandos: **+7** en
> `tests/quality_gates/decision_client/test_decision_client_campos_pedido_y_tiempo.py` (0 → **7**, la mitad (a)
> del gap: los tres campos nuevos del pedido viajando en el dict publicado, `provider_requested` saliendo del
> entorno que nombro el llamador, `model_requested` fijado al pin declarado y no a lo que reporta el proveedor,
> `elapsed_ms` en null cuando no hubo llamada y cronometrando la llamada real, y el control de que los siete
> campos viejos no cambiaron de nombre ni de valor). Distribucion por filas: +7 a `quality_gates` (870 →
> **877**); las otras 21 filas no se movieron y la suma de las 22 de la tercera columna da **4,706**, verificada
> con un instrumento que enumera los sumandos y no de memoria.
>
> Lo que esta ronda deja declarado, que es lo que la hace necesaria: **la unidad no viajó con la cifra**. Los
> siete tests se commitearon el 2026-10-02 en `4621049`, y ese commit no llevo `AGENTS.md` entre sus rutas, asi
> que la cabecera siguio diciendo 4,699 mientras el arbol y HEAD daban 4,706 desde ese mismo commit. La sesion
> que estampa la cifra hoy no escribio ningun test ni toco `tests/`: es la ronda de la costura anterior, aqui
> queda solo el sello. Y como su alcance fijo que en `AGENTS.md` solo cambian la cabecera y la fila, la prosa de
> la nota de `§Cobertura por Modulo` sigue afirmando que "en el commit que lleva esta nota los dos comandos dan
> 4,699": esa clausula queda vencida por esta nota y se declara aqui, no se re-escribe alla. Mide lo mismo que
> midio: `9181197`, que es su commit, no el que lleva la cabecera a 4,706.
>

> **Tanda ADOPCION-Y-CIERRE-DEUDA del 2026-10-01 (la cifra subio a 4,699).** Medido con el metodo canonico de
> la casa (`grep -rE "^\s*def test_" tests --include=*.py` = **4,699**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests` sumado por awk en `9181197` = **4,699**): **las dos cifras
> cuadran** con el delta ya commiteado. El delta contra la segunda ronda de la manana (4,698) es **+1** y se
> atribuye por archivo, sin mas sumandos: **+1** en `tests/test_diagnostic_geo_metrics.py` (5 → 6: el diente
> de DELIMITADORES de la fila 17 del registro 33-, `test_geo_table_header_and_separator_pipes_are_paired`,
> que renderiza el diagnostico end-to-end, ubica la tabla por el dato como el diente de la fila 14 y afirma
> paridad de pipes y de columnas entre cabecera y separador; rojo antes con la cabecera en 7 pipes contra el
> separador en 5, mutante con ancla unica verificada por conteo y `ast.parse`, control de renombre puro
> VERDE — el diente mide delimitadores, no el literal — y control negativo con `git show 7fa8d5c` del
> generador pre-cura, ejecutado). Distribucion por filas: +1 a `root test files` (1.057 → **1.058**); las
> otras 21 filas no se movieron y la suma de las 22 de la tercera columna da **4,699** (verificada con un
> instrumento que enumera los sumandos, `awk -F'|'` sobre las filas numericas de la tabla). La letra 1 de la
> misma tanda no sumo funciones-test: fue adopcion de trabajo suspendido (la cura faq del provider aislado y
> la cura wiring del derivado versionado, schema 1.2), no test nuevo.
>

> **Segunda ronda del 2026-10-01 — CIERRE-DEUDA (la cifra subio a 4,698).** Medido con el metodo canonico de la
> casa (`grep -rE "^\s*def test_" tests --include=*.py` = **4,698**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests` sumado por awk en `c4d0ffe` = **4,698**): **las dos cifras
> cuadran**, y esta vez porque las diez funciones nuevas se commitearon **antes** de medir — la regla de la casa
> al reves de lo que paso los dias 25 y 26. El delta contra la ronda de la manana (4,688) es **+10** y se
> atribuyo **por comparacion de arboles, no de memoria**: `git grep -c` en `321a0cf` y en `HEAD`, restados por
> archivo, da exactamente tres sumandos y ninguno mas —
> **+5** en `tests/test_registry_fecha_documental.py` (20 → 25: los dientes de la guarda `--plan` de la fila 15,
> que son rechazo medido por operaciones observadas, desambiguacion que no re-escribe la primera entrada, plan
> declinado que tambien se niega, caracterizacion de que las dos colisiones publicadas siguen en el expediente, y
> el control negativo que ejecuta el escritor versionado en `bb1be59`);
> **+3** en `tests/financial_engine/test_pricing_resolution_wrapper.py` (36 → 39: el diente de tres piezas del
> aislamiento de flags de la fila 13, envenenar-con-el-mecanismo-real / sin-guarda-da-437.500 / con-guarda-da
> 2.500.000);
> **+2** en `tests/test_diagnostic_geo_metrics.py` (3 → 5: el diente de PERDIDA de seccion de la fila 14, que
> ubica la tabla por el dato y no por el titulo, mas el test que declara el anclaje vigente).
> Distribucion por filas: +3 a `financial_engine` (549 → **552**) y +7 a `root test files` (1.050 → **1.057**);
> las otras 20 filas no se movieron y la suma de las 22 de la tercera columna da **4,698** (verificado sumando
> los sumandos con un instrumento que los enumera, no de memoria).
>
> **Nota de instrumento, porque esta ronda si tuvo uno nuevo**: el bisect de la fila 13 (`temp/
> cierre-deuda-2026-10-01_fila13_matriz.py`, 29 selecciones sobre 117 unidades de coleccion) corrio pytest una
> vez por seleccion y **no conto funciones-test por archivo**: la cifra que publica esta nota sale de los dos
> instrumentos canonicos de arriba, no de la matriz. Lo que aporto la matriz es el veredicto de rama — 11
> bloques rojos, no un contaminador — y por eso la cura fue aislamiento en el lector y no restaurar en el que
> ensucia.
>
> **Lo que esta ronda NO sumo**: `scripts/log_phase_completion.py` gano bandera y guarda pero es codigo de
> produccion, no test; y el rojo que la matriz delató en `tests/delivery`
> (`test_faq_generator_output_is_jsonld`, que llama a `api.deepseek.com` y revienta por read timeout) tampoco:
> cae en aislado, no por orden, y no se curo aqui.
>
> **Ronda del 2026-10-01 (la cifra subio a 4,688).** Medido con el metodo canonico de la casa
> (`grep -rE "^\s*def test_" tests --include=*.py` = **4,688**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests` = **4,688** en `ed3670e`): **las dos cifras cuadran**. La nota
> que esta ronda corrige decia «en el commit que lleva esta nota los dos comandos dan 4,584» y estaba vencida
> **en los dos sentidos**: ni el arbol de trabajo ni HEAD daban ese numero — daban 4,688 los dos. El delta contra
> la ronda anterior (4,682) es **+6** y cae **entero** en la fila `root test files` (1.044 → **1.050**): las 6
> funciones del nuevo `tests/test_hook_precommit_packs_check.py` (0 → 6), la bateria del `[8/8]` del hook
> pre-commit que entró en `0ff9f25`. Atribucion cerrada por comparacion de arboles, no de memoria: entre
> `fbfdc57` y `HEAD` el unico archivo de tests que cambia de presencia bajo el metodo grep es ese (medido con
> `git grep -l -E "^\s*def test_"` en las dos revisiones). Las otras 21 filas no se movieron y la suma de las 22
> da exactamente **4,688** (verificado sumando la tercera columna de la tabla, no de memoria).
>
> **Segunda ronda del 2026-09-30 (la cifra subio a 4,682).** Medido con el metodo canonico de la casa
> (`grep -rE "^\s*def test_" tests --include=*.py` = **4,682**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests` = **4,682** en `fbfdc57`, y vuelve a dar 4.682 en el commit
> que lleva esta nota, porque esta edicion no anade ni quita ninguna funcion-test): **las dos cifras cuadran**,
> segunda ronda seguida sin tocar el arbol para medirlas. El delta contra la ronda anterior (4.651, publicada
> **ese mismo dia** mas abajo) es **+31** y cae **entero** en la fila `root test files` (1.013 → **1.044**), en
> tres baterias que se nombran con su dueno porque no son tres de la misma tanda: **+12** en el nuevo
> `tests/test_validate_wiring_alcance_por_declaracion_git.py` — el paso 1 del wiring (salida (c), alcance por
> declaracion de Git), trabajo de la sesion anterior publicado en `abd181c`, que esta nota incorpora porque la
> nota de 4.651 se escribio cuando esas doce todavia no estaban en el arbol; y los dos pasos de esta tanda,
> **+8** en el nuevo `tests/test_validate_wiring_criterio_en_el_exit.py` (paso 2: el criterio de la clausula de
> produccion codificado en el EXIT, con su control negativo ejecutando el instrumento de `abd181c`) y **+11** en
> el nuevo `tests/test_validate_wiring_check_derivado_versionado.py` (paso 3: `--check` sobre el derivado
> versionado, con los tres estados del lector, dos mutantes y la traduccion del codigo nuevo en la cola). Las
> otras 21 filas no se movieron y la suma de las 22 vuelve a dar exactamente **4,682** (verificado por
> directorio con el mismo metodo grep y por `tests/*.py` para la fila de raiz, no sumando la columna de memoria).
>
> **Ronda del 2026-09-30 (la cifra subio a 4,651).** Medido con el metodo canonico de la casa
(`grep -rE "^\s*def test_" tests --include=*.py` = **4,651**) y contrastado con el arbol versionado
(`git grep -c -E "^\s*def test_" HEAD -- tests` = **4,611** en `7737347`): la diferencia es **+40**, y son
cuatro funciones-test que todavia no estan commiteadas, no deuda. El delta se atribuye archivo por archivo:
**+6** en `tests/test_registry_fecha_documental.py` (14 → **20**: los dos rechazos de D-F5, las siete formas
ISO mal escritas que caen en una funcion parametrizada, la fecha declarada contra el reloj, el control
negativo con el escritor de `7737347` y la nota), **+5** en el nuevo
`tests/test_verify_packs_quinto_patron_generado_por_sha.py` (S19(d) salida (c)), **+17** en el nuevo
`tests/test_verify_qmind_context_freshness.py` (S34) y **+12** en el nuevo
`tests/test_validate_lesson_capitalization_c9_descripcion_alcance.py` (el sub-punto de S29). Todo cae en la
fila `root test files` (**973 → 1.013**); `quality_gates` y las otras 20 filas no se movieron, y la suma de
las 22 filas vuelve a dar exactamente **4,651** (verificado sumando la tercera columna). Las cuatro pruebas
**viajan con su cifra**: la dependencia declarada es que los cuatro archivos esten commiteados antes o con
esta cabecera, no despues, para que los dos comandos cuadren en el commit que lleva la nota. Antecedente tal
como se publico: **4,611** (ronda del 2026-09-28, publicado en la tanda de `0e9cdd5`).

> **Ronda del 2026-09-28 (la cifra subio a 4,611).** Medido con el metodo canonico de la casa
> (`grep -rE "^\s*def test_" tests --include=*.py`, **4,611**) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests`, **4,611** en `0e9cdd5`): **las dos cifras cuadran**, y por
> primera vez sin mover el arbol para medirlas — la dependencia de la tanda ya estaba cumplida, porque las
> veintiuna funciones viajaron **antes** que esta nota, en `c8b7198`. El delta contra la ronda anterior
> (4,590, publicada en `e7c722b`) es **+21**, todo de la segunda sesion de codigo sobre `scripts/` (orden
> post-re-verificacion VCF+JEV), y se atribuye archivo por archivo: **+7** en
> `tests/test_sync_writers_lf_y_fecha_readme.py` (10 → 17: los cuatro controles de la forma que promueve
> `--fix`, el delta EOL contrastado contra la forma citada, la cuenta de escritores LF y el ancla del control
> C7 a su revision fija), **+5** en el nuevo `tests/test_run_all_validations_denominador_por_modo.py` (S21:
> un denominador por modo y la [GUARDA] cortando fuera del rapido), **+6** en el nuevo
> `tests/quality_gates/phase_briefing/test_briefing_proyeccion_workflow_gobernada.py` (S32: la proyeccion del
> workflow gobernada por `--check`, con su control de verde falso) y **+3** en el nuevo
> `tests/quality_gates/governance_numbers/test_governance_numbers_estados_sin_puntero_d1.py` (D-A: los estados
> que dejaron de delegarse en D1). O sea `root test files` 961 → **973** y `quality_gates` 861 → **870**; la
> suma de las 22 filas de la tabla da exactamente **4,611** (verificado sumando la tercera columna). Queda
> advertido el lector de la nota de arriba: su «En el commit que lleva esta nota los dos comandos dan 4,584»
> describia al commit que la escribio, no a este, y desde entonces dos rondas la han dejado como antecedente
> en vez de reescribirla.
>
> **Segunda ronda del 2026-09-27 (la cifra subio a 4,590).** Medido con el metodo canonico de la casa
> (`grep -rE "^\s*def test_" tests --include=*.py`, 4,590) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests`, 4,585 en `505cd44`): la diferencia es **+5**, cinco funciones
> nuevas de la sesion de curas fuera de plans. Dos paquetes, en dos filas de la tabla: **+3** en
> `tests/test_sync_writers_lf_y_fecha_readme.py` (la cura de S17 sobre el quinto escritor: su `--fix`, su
> `--write-baseline` y el guard de destino por operaciones observadas) y **+2** en
> `tests/quality_gates/phase_briefing/test_arneses_resuelven_plan_por_el_escritor.py` (la cura de S31: los dientes
> anclados a la revision fija `44f53c2` y el control anti-literal). O sea `root test files` 958 → **961** y
> `quality_gates` 859 → **861**; la suma de las 22 filas de la tabla da exactamente **4,590** (verificado sumando
> la tercera columna con `awk -F'|'`).
>
> Desvio declarado contra la instruccion que pidio esta edicion: esa nota preveia que la bateria LF cayera en
> `root test files` y que **nada** cayera en `quality_gates`. Cayeron dos, porque el control de S31 vive en una
> seleccion debajo de `tests/quality_gates/`. Se alinea su fila por la misma regla que la cabecera: la tabla es un
> retrato del arbol, no una prediccion del mandato.
>
> **Dependencia declarada, no asumida**: para que los dos comandos cuadren en el commit que lleva esta nota hace
> falta que las cinco funciones viajen **antes** — la tanda las pone en los commits de S17 y de S31, y esta
> cabecera se alinea en el ultimo. Antecedente tal como se publico: **4,585** (primera ronda del 2026-09-27,
> publicado en la tanda de `84282c1`/`505cd44`), y antes **4,584** (medido 2026-09-27, publicado en `5d80cd7`).
>
> Nota para no volver a confundir instrumentos: `scripts/validate_agents_md.py::check_2_test_count` **no** usa el
> metodo grep sino `pytest --collect-only -q` sobre items, con tolerancia **±5 %**. Los items y las funciones no
> son la misma poblacion — la suite de esta ronda recolecto **+6** items con **+5** funciones, y el item extra es
> un caso parametrizado (`test_triage_sobre_plan_archivado_real[EVALUACION-JEV-TYPESAFE-2026-09-21]`) que metio el
> archivado de JEV, no esta sesion. La cifra publicada es la del metodo canonico.
>
> **Ronda del 2026-09-27 (la cifra subio a 4,585).** Medido con el metodo canonico de la casa
> (`grep -rE "^\s*def test_" tests --include=*.py`, 4,585) y contrastado con el arbol versionado
> (`git grep -c -E "^\s*def test_" HEAD -- tests`, 4,584 en `1e4cb52`): la diferencia es **+1**, una funcion nueva
> en `tests/test_validate_lesson_capitalization.py` (`test_el_plan_archivado_posterior_al_corte_entra_en_alcance_sobre_revision_fija`,
> anclada a la revision fija `9c4a001`). El otro test tocado en la ronda se **renombo**, no se agrego, asi que sigue
> siendo una funcion. La +1 cae toda en la fila `root test files` (957 → **958**) y la suma de las 22 filas da
> exactamente 4,585. **Dependencia declarada, no asumida**: para que en el commit que lleva esta nota cuadren los
> dos comandos hace falta que la funcion nueva viaje **antes** — el orden de la tanda la pone en el commit S29, y
> esta cabecera se alinea en el ultimo. Antecedente tal como se publico: **4,584** (medido 2026-09-27, publicado en
> `5d80cd7`), y antes **4,582** (2026-09-26).
>
> Como se abrio y como se cerro la brecha de esta ronda, para no repetir el procedimiento: al comitear la
> orden las dos cifras estaban en 4,582 y cuadraban. Los dos controles nuevos entraron despues, el arbol
> subio a 4,584 y la cabecera se quedo dos por debajo. No se adivino el numero: se midio, se declaro la
> desviacion en el crudo `evidence/…/CIERRE-ORDEN-2026-09-25/D-C-D8-D9/06-…txt` **en vez de editar la
> cabecera a mano**, y se actualizo aqui solo cuando llego la instruccion explicita de hacerlo (AGENTS.md es
> config central). Y el gate que goberna esta cifra tampoco corto el paso: su tolerancia es del **±5 %**, asi
> que dos funciones de desviacion quedan muy dentro — ver el parrafo del instrumento, mas abajo. Lo que si la
> cazó fue la resta de la tabla contra el comando canonico, que es una comprobacion aparte y no un gate.
>
> Antecedente, vigente hasta el 2026-09-25: las dos cifras eran distintas (4,470 en HEAD `5817edd` contra
> 4,564 en el arbol de trabajo) y la diferencia (+94) era trabajo sin commitear, no deuda ni error. Lo que
> ese episodio deja como regla: una cifra publicada esta casada con las rutas que viajan con ella, y cuando
> no lo estan se corrige el grupo de rutas, no el numero.
>
> Medido 2026-09-27 con el metodo canonico del proyecto: `grep -rE "^\s*def test_" tests --include=*.py`
> (no `pytest --collect-only`; las filas suman el total). Nota de instrumento para no volver a confundirlas:
> `scripts/validate_agents_md.py::check_2_test_count` **no** usa el metodo grep sino
> `pytest --collect-only -q` sobre items (**4,658** al medir el 2026-09-27, +2 con los dos controles nuevos)
> con tolerancia **±5 %** — con **4,584** publicado la desviacion es **1,6 %** y el check pasa (exit 0). Lo
> mismo con **4,582** publicado daba 1,7 % y tampoco cortaba: de ahi que la desviacion se declarara en el
> crudo y no se confiara en el gate para cazarla.
> Antecedente: el 2026-09-25 medía
> 4,638 items y daba el mismo 1,6 % con 4,564 publicado; con el 4,246 anterior la desviacion llegaba a 8,5 %
> y el check fallaba. No hay que "arreglar"
> esta cifra hacia el numero de items: son dos instrumentos distintos y el publicado es el del metodo
> canonico.
> Cifra anterior: **4,582** (medido 2026-09-26, misma orden). La diferencia (+2) cae otra vez en la fila
> `root test files` (955 → **957**) y son los dos controles anclados a **revisiones publicadas fijas** que
> exige `tests/test_verify_packs_in_committed_tree.py` desde la ronda de D-c. Uno es
> `test_el_plan_archivado_sigue_siendo_evaluable` (anclado a `3c2e6a3`, la revision que archivó el plan) y el
> otro es `test_ambas_rutas_de_plan_resuelven_en_ambas_revisiones` (anclado a `44f53c2` antes y a `3c2e6a3`
> despues). Los dos nombres van enteros en una misma línea: partidos, dejan de ser símbolos localizables.
> Lo que estos dos prueban, ademas del fix: que el verificador de packs montaba la ruta a pelo como
> `plans/<PLAN>` y al archivarse el plan dejo de verlo — informaba `AUSENTE-EN-VERSIONADO` sobre cinco packs
> correctos, o sea un rapido rojo causado por el instrumento. La cura es reutilizar `resolver_plan()` del
> propio escritor. Cada control afirma una forma distinta de la ruta, asi que ninguno pasa por accidente, y
> se verifico que tienen dientes **quitando la cura**: mutado, caen exactamente esos dos y los otros cinco
> pasan igual. Previa, del 2026-09-26: **4,573** (dos sesiones antes). La diferencia (+9) vuelve a
> ser dos baterias y vuelve a caer en la fila `root test files` (946 → **955**): 4 funciones de
> `tests/test_verify_index_in_committed_tree.py` (la cura de **S20**: el clon del verificador heredaba el
> `core.autocrlf` del ambito system y su `--check` de packs cortaba rojo falso sobre un commit correcto) y 5
> de `tests/test_verify_packs_in_committed_tree.py` (la cura **(b) de S19**: regenera los packs en scratch
> dentro del arbol del commit y compara por sha normalizado; su control negativo muta el literal que el
> escritor copia al pack y exige a la vez que este verificador pierda y que `build_phase_briefing --check`
> siga dando verde). Previa, del mismo dia: **4,564 → 4,573** (+4 de `test_build_lesson_index_s15_fecha_versionada.py`
> y +5 de la primera bateria de `test_verify_index_in_committed_tree.py`). Suma comprobada al medir: las 22
> filas de la tabla dan exactamente **4,584**.
> Previa: 4,246 (v4.77.3, medido 2026-09-19). La diferencia (+318) se desglosa por fila de la
> tabla: `quality_gates` +229 (decision_client y su arnes de mutacion del bloque A/B de la orden de calidad,
> `lesson_relevance` del piloto FASE-C, `phase_briefing` de FASE-D y su cura AC23, y los gates tocados en
> RELEASE), `root test files` +75 (entre ellas las 7 de
> `tests/test_sync_writers_lf_y_fecha_readme.py` de la cura S17/S18), `commercial_documents` +12 y
> `asset_generation` +2. Previa: 4,245 (v4.77.2). La diferencia (+1) es el test de regresion del contrato
> no-medible (`test_check_mentions_all_providers_fail_is_not_measured`) en
> `tests/auditors/test_llm_mention_checker.py`. Previa: 4,240 (v4.77.1), +5 por
> `TestGeminiCostAccounting`. Previa: 4,233 (v4.77.0), +7 por
> `TestGeminiModelFromRegistry`.
> Previa: 4,063 (v4.76.0). La diferencia (+170) corresponde a los tests del plan
> TRIBUNAL-ENFORCEMENT-OBS-2026-09-11 (P3-A +21, P3-B +17, P2 +28, P5 +21, P6 +20, P6-R +7 funciones
> propias) y a entradas ajenas al plan medidas en el intervalo.
