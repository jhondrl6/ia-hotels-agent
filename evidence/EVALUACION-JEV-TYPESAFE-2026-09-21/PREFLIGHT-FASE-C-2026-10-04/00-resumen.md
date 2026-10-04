# PREFLIGHT-FASE-C-2026-10-04 — SESION 2.5 (FASE-B.1): cura del brazo DeepSeek y registro decision-ready

Plan: `EVALUACION-JEV-TYPESAFE-2026-09-21`. Antecedente inmediato: `DEUDA-FASE-B-2026-10-04/00-resumen.md`
(deuda de cinco filas, commiteada en `7899f0f` y empujada hasta `5ca6395`). Esta sesion ejecuta los items
abiertos **2** y **3** de esa deuda y produce el registro del **4**; los items **5** y **6** quedan fuera de
alcance y transferidos (prompt §10).

- **Revision de arranque**: `5ca63953b966b18f8e55a79c7669ca1196fc6f1e`. Paridad medida contra el servidor:
  `git ls-remote origin refs/heads/master` = `5ca6395…`, igual que `git rev-parse HEAD`; `git status` al
  arrancar estaba vacio (arbol limpio, sin trabajo ajeno). Esa revision fija es la ancla de los controles
  versionados: el antecedente se ejecuto sobre `git show 5ca6395:scripts/proveedores/deepseek.py`.
- **Cifra canonica de pruebas**: `grep -rE "^\s*def test_" tests --include=*.py` = **4,800** sobre el arbol de
  trabajo; `git grep -c -E "^\s*def test_" HEAD -- tests` sumado = **4,795** sobre `HEAD` = `5ca6395`. El delta
  de **5** es trabajo de esta sesion sin commitear. Las dos cifras no se contradicen: median arboles distintos
  en el momento de la medida.
- **Consumo de red de la sesion**: **1** envio autenticado (la lectura de saldo, `07-saldo-crudo.json`, cero
  reintentos). **Cero** envios de `chat/completions`: el tope de A2 es una llamada y se destino al saldo, asi
  que la cura del mapper no se re-confirmo con trafico real (reserva N-3 del registro). Afuera del proveedor:
  dos intentos de fetch al sitio de documentacion oficial (`api-docs.deepseek.com`, sin resolucion desde esta
  maquina) y un fetch a un espejo de terceros de donde se transcribio la via del endpoint.
- **Gate**: `python scripts/run_all_validations.py --quick` = **13/13**, EXIT=0. Se corrio tres veces sobre el
  mismo estado y se publican dos crudos: `10-` (antes del cierre documental), `15-` (tras las escrituras de
  docs y derivado) y `16-` (tras el manifiesto); la corrida que avala el estado final —ya con el parrafo de
  verificacion posterior escrito— esta estampada al pie de este archivo, en el unico documento excluido de su
  propio manifiesto. `python scripts/validate_wiring.py --check` = conforme, digest `b4705a4b5d38`, EXIT=0
  (`11-` y `14-`; el crudo de cuando todavia estaba vencido es `12-`).
- **Los cinco cortes estan declarados y verificados sin commitear** (D6). El `git commit` no es condicion de
  ninguno: queda en espera de autorizacion explicita del operador.

## Tabla de los tres cierres, en su estado medido

| # | Cierre | Estado medido | Evidencia (ruta dentro de este expediente, y comando que la imprime) |
|---|--------|---------------|------------------------------------------------------------------------|
| A | Cura del id recortado en `_mapear_respuestas` | **CERRADO**: la respuesta cuyo id llega recortado se devuelve mapeada con el id **preguntado**; el recorte ambiguo no se adivina; D5 intacto (lo que no vino sigue ausente). PRE 10 passed (crudo `01-`), POST **15 passed, EXIT=0** (`05-`). Antecedente reproducido sobre el blob de `5ca6395`: 4/4 casos `respuestas: []` (`02-`); arbol curado: 3/4 VALIDA y el ambiguo rechazado por diseno (`03-`). Seis mutantes, seis rojos por su causa, seis restauraciones con sha `289842457a5b` y bateria verde tras cada una (`04-`) | `venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py -q`; arneses `08a-` (antecedente/post) y `08b-` (mutantes). Cierre estampado en `preflight.json` → `proveedores.deepseek.cierre_d_2026-10-04_cura_del_id_recortado` |
| B | `cuota_o_saldo` del segundo brazo (cuarto estado de AC12) | **MEDIDO (camino (i))**: `GET https://api.deepseek.com/user/balance` → HTTP 200, `is_available: true`, USD total **4.94** (granted 0.00, topped_up 4.94). Un envio, cero reintentos. La clave `cuota_o_saldo` del preflight ya no dice `NO-EJERCITADO`; el valor anterior queda transcripto en el cierre, no borrado | `python temp/sesion25-2026-10-04/p3_saldo_deepseek.py` (copia `08c-`), crudo `07-saldo-crudo.json`. Estampado en `preflight.json` → `proveedores.deepseek.cuota_o_saldo` y `cierre_c_2026-10-04_cuota_o_saldo_medido` |
| C | Registro decision-ready de `deepseek-flash` | **ENTREGADO, sin congelar**: `09-registro-deepseek-flash.md` con MEDIDO (7 filas, cada una con su corrida o request_id citado) y NO MEDIDO (5 filas, cada una con quien la responde) separados, y las dos salidas legitimas del congelado —(a) preguntar al proveedor y estampar, (b) congelar con el caveat— enunciadas para el paso 3.1. Esta sesion no eligio ninguna | Lectura del archivo; cada fila MEDIDO cita `preflight.json` → `cierre_2026-10-04` / `cierre_b_2026-10-04_estabilidad_del_alias` del expediente de la deuda, o un crudo propio (`02-`, `03-`, `04-`, `05-`, `07-`) |

## Como se ejercito cada cierre

### Cierre A — el id recortado, y el ledger que se cobraba sin devolver

La cura no es cosmetica por una razon medida: el comparador y el triaje preguntan con ids prefijados
(`sonda:1`, `pert:L-R.1`), y un emisor que recorta el prefijo vaciaba el ledger **sin ruido y con el gasto
cobrado**. Correr FASE-C sobre ese brazo habria producido un `margen_vs_deepseek` que se leeria como resultado
del comparador y no como fallo del instrumento.

- **Que hace el codigo**: `_mapear_respuestas` ya no indexa solo por id exacto. Llama a
  `_emparejar_respuestas`, que hace dos vueltas: primero la coincidencia exacta (la que pide el contrato) y
  despues la forma recortada del id preguntado —el ultimo segmento despues de `:`—, y solo cuando ese recorte
  nombra a **una** pregunta y queda **una** respuesta libre con ese id. La fila se publica con el id
  **preguntado**, porque la cobertura la cuenta la puerta contra los ids del pedido.
- **Que NO hace**: no rellena. La cura cambia el emparejamiento, no la construccion de la fila: los campos que
  el servicio no trajo siguen ausentes y la puerta los marca `ILEGIBLE` (D5). Y no toca `_instrucciones`, que
  era la otra duena posible del defecto (queda como N-4 en el registro). Tampoco cambia el pedido
  (`deepseek-chat` sigue, D7) ni el techo de tokens del brazo.
- **El re-anclaje prometido resulto no-actado, y se declara**: las diez pruebas previas quedaron verdes tal
  cual. Medido prueba por prueba: ninguna asercion dependia del descarte. El prompt anunciaba "los 10 tests
  re-anclados"; la realidad medida es que no habia nada que re-anclar, y se escribe eso en vez de inventar un
  cambio para que la fila del prompt salga cumplida (V8 iba en la misma direccion).
- **Dientes**: cinco pruebas nuevas (10 → 15). Cada una con su mutante y su causa enunciada antes de correr:
  M1 el recorte vuelve a descartarse, M2 el recorte se toma del lado equivocado del delimitador, M3 se adivina
  el ambiguo, M4 el recorte le roba la respuesta a la exacta, M5 el mapper rellena el `confidence` que no vino,
  M6 la fila publica el id del servicio. Los seis cortaron, con kill-set publicado (no solo el nodo previsto:
  se corre la bateria entera por mutante para que un rojo inesperado se vea), y los seis se restauraron al sha
  `289842457a5b` con la bateria verde despues de cada restauracion. `git status` del archivo mutado dio lo mismo
  antes y despues de la ronda (`M`, por la cura autorizada en A1, no por los mutantes).
- **Dos mutantes que NO fueron dientes, declarados**: `split(SEP, 1)[1]` y `split(SEP)[1]` dieron VERDE. Son
  equivalentes: los ids del corpus llevan un solo `:`, y ahi `split` y `rsplit` coinciden. Un verde de mutante
  equivalente no prueba la rama, asi que se reportaron en el crudo y se sustituyeron por `split(SEP)[0]`, que
  toma el prefijo y si muerde.
- **Kill-set publicado, no solo el nodo previsto**: se corrio la bateria entera por mutante, y eso mostro que
  los dientes se solapan. M1 y M2 apagan tambien las pruebas que comparten la via del recorte, y M5 apaga
  **una prueba previa** (`test_deepseek_no_inventa_confidence_y_la_puerta_responde_ilegible`) por la misma
  causa: el `confidence` plantado vale para las dos vias, la exacta y la recortada. Los solapes se publican
  en la columna `cayo_algo_no_predicho` del crudo en vez de podarse, porque un kill-set recortado a lo
  previsto es la forma en que un mutante parece mas especifico de lo que es. M3, M4 y M6 cortaron exactamente
  su conjunto predicho, sin residuo.

### Cierre B — AC12 cuarto estado: MEDIDO por la API, no DECLARADO

El precedente del primer brazo era `DECLARADA-POR-CONSOLA $10.00` porque el SDK 0.7.0 no expone superficie de
saldo. DeepSeek si expone una, y el prompt preferia la via medida: se camino (i).

- **La via**: `GET https://api.deepseek.com/user/balance` con `Authorization: Bearer` y
  `Accept: application/json`. No la publicaba el brazo (su unico camino de red es el POST de
  `chat/completions`), y agregarle un GET de facturacion seria meterle al comparador una superficie que el
  protocolo no le pidio (D3), asi que el arnes habla con `urllib` a una sola mano.
- **El gasto**: un envio, cero reintentos (AC8). No hay segundo envio: la lectura salio 200 a la primera.
- **Lo que no cubrio**: el saldo no ejercita el mapper —es un GET de facturacion, no un chat—, asi que la
  ventana de "si su trafico sirve para observar el mapper con trafico real" no se abrio. El trafico real que
  ejercicio el mapper siguen siendo los 6 envios de la deuda.
- **La clave no sale**: entra por `.env` al entorno del proceso; el arnes afirma antes de escribir que el valor
  no esta en el crudo, y el barrido final (`13-`) lo vuelve a medir sobre los 22 archivos.

### Cierre C — el registro que no responde la pregunta

Que significa `deepseek-flash` no lo puede responder este arbol (V4), y el objetivo no era responderlo sino
dejarlo decision-ready. La forma esta en `09-`: siete filas MEDIDO con su proveniencia citada, cinco NO MEDIDO
con quien las responde, y las dos salidas del congelado enunciadas sin elegir una.

## Escrituras colaterales, con su motivo

- `.opencode/wiring_report.json` **re-publicado** con el mecanismo documentado
  (`python scripts/validate_wiring.py --write-report`). El derivado quedo vencido por los tres arneses `.py` que
  esta sesion guardo dentro de su expediente: `cobertura.archivos_excluidos_por_rol_versionado` 131 → **134** y
  `exclusiones_por_rol.evidence.cantidad_versionada` 119 → **122** (crudo de la divergencia: `12-`; crudo de la
  conformidad: `11-` y `14-`). No se rebajo la asercion del gate: se re-publico el artefacto. Mismo precedente y
  mismo signo que en la deuda (+2 alli por sus dos arneses).
- `AGENTS.md`: cabecera `### Cobertura por Modulo` 4,795 → **4,800** y fila `quality_gates` 946 → **951**. La
  nota de la ronda se aparco en `docs/cobertura-historia.md` arriba del todo, sin borrar las previas. Verificado
  con el instrumento de la casa: suma de la tercera columna = cabecera (**4,800 = 4,800**, 22 filas, 3 celdas por
  fila), `python scripts/validate_agents_md.py` EXIT=0 y `python scripts/validate_governance_numbers.py`
  `SIN-HALLAZGOS`.
- `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B/preflight.json`: dos cierres nuevos
  (`cierre_c_2026-10-04_cuota_o_saldo_medido`, `cierre_d_2026-10-04_cura_del_id_recortado`) y **una reescritura
  declarada**: la clave `cuota_o_saldo` pasa de `NO-EJERCITADO` al valor medido porque el criterio C4 de la
  sesion lo pide. Los cierres anteriores de este brazo prometian no tocar los campos originales; aqui esa
  promesa se rompe en UNA clave, se rompe porque el mandato la rompe, y el valor anterior queda transcripto
  dentro del cierre en vez de borrado. Los otros tres estados del brazo y todo el brazo `jev` (incluido su
  `DECLARADA-POR-CONSOLA $10.00`) no se movieron; `diff --numstat` del archivo: 43 inserciones, 1 borrado.
- **Vedas verificadas al cierre, no prometidas**: `muestra.json`, `protocolo.json`, el `10-analisis` del plan y
  `REGISTRY.md` no aparecen en `git status` (V2); `scripts/verify_qmind_context_freshness.py` y su test estan
  intactos (V1); ningun otro archivo de produccion se toco (V3, incluido `modules/providers/llm_provider.py`);
  no se corrio `git clone` dentro del arbol (V7) y el indice temporal que se us6 para medir los blobs se creen
  fuera, en `AppData/Local/Temp`.

## Nota de interprete: un rojo que no era del codigo

La bateria adyacente (`tests/quality_gates/jev_pilot/ + decision_client/ + lesson_relevance/`) dio
**1 failed, 246 passed** bajo el `python` global del sistema y **247 passed** bajo
`venv/Scripts/python.exe`, el interprete del piloto (crudos `06-` y `06b-`). El rojo es
`test_jev_pilot_sdk_ac9.py::test_cargar_sdk_anade_al_final_y_conserva_el_pydantic_del_product` con firma
`assert (14 > 14)`: con el interprete global la unica entrada de `sys.path` que casa con
`"venv" and "site-packages"` es el propio `tmp_test/venv-jev-sdk`, asi que la prueba se compara contra si misma.
No es regresion de esta tanda (ese archivo no mira el brazo ni importa el mapper), se registra con su dueno y
no se cura aqui porque V3 acota la escritura de produccion a `scripts/proveedores/deepseek.py`. Leccion para la
casa: las baterias del piloto se corren con `venv/Scripts/python.exe`, y un rojo de interprete no se reporta
como rojo de codigo.

## Los cinco cortes (declarados, sin commit)

1. **Implementacion terminada**: la cura en `scripts/proveedores/deepseek.py` y sus cinco pruebas nuevas.
2. **Verificacion terminada**: PRE 10 → POST 15 con EXIT=0, antecedente sobre el blob de `5ca6395`, seis
   mutantes con su causa y su restauracion por sha, bateria adyacente 247 verde con el interprete del piloto.
3. **Cierre documental**: `preflight.json` con los dos cierres, `AGENTS.md` y `docs/cobertura-historia.md` por
   su flujo, `wiring_report.json` re-publicado, `09-registro-deepseek-flash.md` y este resumen.
4. **Listo para revision**: los 20 archivos de este expediente con su manifiesto sha256, el gate 13/13 y el
   barrido de credenciales SIN HALLAZGOS.
5. **Espera de autorizacion**: nada de esto esta commiteado. `git commit`, `git push` y la revision L3 son acto
   del operador; la apertura de FASE-C tambien, y esta sesion no la ofrece.

## Lo que queda abierto al terminar la sesion

1. **Commit, push y L3**: a criterio del operador (los cinco cortes terminan en espera de autorizacion).
2. **Que significa `deepseek-flash`** (capa de serving o alias de producto): NO MEDIDO, y no lo responde este
   arbol. Sale con las dos salidas (a)/(b) del registro, para el paso 3.1 de FASE-C.
3. **Confirmar la cura con trafico real**: pidio un segundo envio de `chat/completions` y V5 lo niega (el tope
   de A2 se gasto en el saldo). Llega con la corrida de comparacion de C, con su propia autorizacion de envios.
4. **Item 5 de la deuda — el reintento de descarga del diente de frescura**: transferido, no ejecutado (V1).
   Dueno: `scripts/verify_qmind_context_freshness.py`. Va a la carta de transferencias entre planes con letra
   propia (paso 5 del plan maestro).
5. **Item 6 de la deuda — `git clone` dentro del arbol como patron que rompe el gate**: la regla escrita del
   executor se redacta en el paso 5; en esta sesion solo se aplico la practica (V7).
6. **El rojo de interprete** (`test_jev_pilot_sdk_ac9.py` bajo el `python` global): registrado con su dueno y su
   crudo; su cura no esta en el mandato de esta sesion.
7. **La otra duena posible del defecto del id**: exigir el id literal en `_instrucciones` en vez de tolerar el
   recorte en el mapper (N-4 del registro). Se eligio el mapper porque es lo que autoriza D3 y porque tolerar
   al emisor es el contrato de esta casa: conservar lo que el servicio trajo.
8. **Un borde no tocado del mapper, declarado y no curado**: si el servicio devolviera un `pregunta_id` **no
   hashable** (una lista o un dict), `_emparejar_respuestas` explota con `TypeError` al indexar. Es una via
   **previa** a esta sesion -el `por_id` del codigo versionado en `5ca6395` usaba la misma clave- y no se curo
   aqui porque el mandato no la nombra: se registra con su duena (`scripts/proveedores/deepseek.py`, el filtro
   de `trayidas`) para que entre con letra propia. No esta medido con trafico real: los seis envios de la deuda
   y la lectura de saldo de esta sesion nunca trajeron esa forma.

## Manifiesto del expediente

El sha del propio `00-resumen.md` no se lista: listarlo cambiaria lo que lista. `sha256 disco` es el del arbol
de trabajo; `sha256 en LF` es el del contenido que Git guardara (medido con indice temporal fuera del repo:
`git cat-file blob` de `04-` casa con su columna LF y `08b-`, que ya esta en LF, casa con las dos). Los archivos
con `EOL = MIXTO` son crudos de consola que traen lineas mixtas; `temp/` queda excluido por `.gitignore:21`, y
los arneses corrieron en `temp/sesion25-2026-10-04/`.

| Archivo | Bytes | sha256 disco (16) | sha256 en LF (16) | EOL |
|---|---|---|---|---|
| `01-pre-bateria-brazo-10-tests.txt` | 108 | `3edee28392016f60` | `65263fe0fa8debeb` | MIXTO(2) |
| `02-antecedente-id-recortado-en-5ca6395.json` | 1143 | `40450b2cb2593702` | `0325d66dcb4f207b` | CRLF |
| `03-post-cura-id-recortado-en-el-arbol.json` | 1491 | `cb7acb055933048d` | `f9bf103570e8fc1a` | CRLF |
| `04-mutantes-cierre-a-crudo.json` | 13456 | `861595f412b6a9ad` | `2f98f2518c1a072c` | CRLF |
| `05-post-bateria-brazo-15-tests.txt` | 108 | `e2e333f441453591` | `a780b8f2a4c64e5f` | MIXTO(2) |
| `06-post-bateria-adyacente-247.txt` | 1224 | `5f8b198a7ffe0a68` | `c89fc944f1daf065` | MIXTO(15) |
| `06b-rojo-de-instrumento-interprete-global.txt` | 4080 | `a15676f54f7a1b14` | `651008119a039b94` | MIXTO(38) |
| `07-saldo-crudo.json` | 1095 | `e084dea918dc1b21` | `4b8805624cd831a0` | CRLF |
| `08a-arnes-antecedente-id-recortado.py` | 4683 | `a7da7e3e014b0251` | `a7da7e3e014b0251` | LF |
| `08b-arnes-mutantes-cierre-a.py` | 11600 | `e64639b16607b9e1` | `e64639b16607b9e1` | LF |
| `08c-arnes-saldo.py` | 6072 | `538c43230b665612` | `538c43230b665612` | LF |
| `09-registro-deepseek-flash.md` | 9024 | `e97efc60cfb69f20` | `e97efc60cfb69f20` | LF |
| `10-quick-gate.txt` | 3112 | `2de97ec0d4e9d5d9` | `3c12a129cf42fe03` | CRLF |
| `11-wiring-check-conforme.txt` | 528 | `9a4afffb0a7c35a9` | `9be020d9f54109c9` | CRLF |
| `12-wiring-check-previo-divergente.txt` | 362 | `a5c51a36a07c1a78` | `1539bd21c52bca2d` | CRLF |
| `13-barrido-credenciales.txt` | 2582 | `93377f577dc42522` | `c5891624f171958b` | CRLF |
| `14-wiring-check-final.txt` | 528 | `9a4afffb0a7c35a9` | `9be020d9f54109c9` | CRLF |
| `15-quick-gate-final.txt` | 3112 | `fcdf122646ec8c00` | `6cda60fb2a755263` | CRLF |
| `16-quick-gate-post-resumen.txt` | 3124 | `7f27e7d38776b323` | `7319cb76d7be31d3` | MIXTO(43) |
| `17-quick-gate-de-certificacion.txt` | 3119 | `b7ccf5585feb1d22` | `69343a3ccb5dce8e` | MIXTO(43) |
| `18-verificacion-en-clon-del-commit.txt` | 2622 | `9ea3d629e70442e2` | `dfa476db68849bc6` | CRLF |


Total: **21 archivos**, 73173 bytes. Los tres arneses `.py` (`08a-`, `08b-`, `08c-`) son los que movieron
`evidence.cantidad_versionada` del derivado (+3: 119 → 122); el resto son crudos `.json`/`.txt` y dos `.md`.
El manifiesto se recalculo **despues** del barrido final (`13-`) y del crudo del gate (`16-`), que son
los ultimos archivos del expediente en cambiar de bytes. El sha del propio `00-resumen.md` no se lista
(listarlo cambiaria lo que lista), y por eso la verificacion posterior al manifiesto se estampa aqui, en el
archivo excluido, en vez de abrir un crudo nuevo que dejaria vencida esta tabla. El `16-` es la corrida del gate rapido despues de todas las escrituras documentales.

## Verificacion posterior al manifiesto (estampada en el archivo excluido de el)

Esta corrida se estampa aqui, y no en un crudo nuevo, porque abrir un archivo despues de la tabla dejaba
vencida la tabla que lo registraba. `00-resumen.md` es el unico archivo del expediente que cambia de bytes
despues del manifiesto, y es el unico que no esta en el.

- `python scripts/run_all_validations.py --quick` (arbol de trabajo, con los 20 archivos del expediente y las
  cinco escrituras de docs/derivado ya publicadas): **13/13**, EXIT=0. Es la cuarta corrida del gate en la
  sesion (`10-`, `15-`, `16-` y esta) y su crudo es `17-`. Las tres corridas anteriores valian sobre bytes que
  todavia iban a cambiar: esta es la unica que corre sobre el expediente completo; despues se anadieron `18-` (la verificacion en el arbol del commit) y este
  sello, y el manifiesto se recalculo con ellos dentro (el manifiesto se recalculo con ella dentro).
- `python scripts/validate_wiring.py --check`: conforme, digest `b4705a4b5d38`, EXIT=0.

## Etiqueta del arbol donde corrio cada verde

| Verde | Arbol | Interprete |
|---|---|---|
| PRE 10 passed (`01-`) | `5ca6395` limpio, sin la cura | `python` (global, 3.13.3) |
| Antecedente 4/4 `respuestas: []` (`02-`) | blob de `5ca6395` cargado con `git show`, arbol intacto | `python` |
| POST 15 passed (`05-`) | arbol de trabajo con la cura | `venv/Scripts/python.exe` |
| POST 3/4 VALIDA + ambiguo rechazado (`03-`) | arbol de trabajo con la cura | `python` |
| Restauraciones tras cada mutante (`04-`) | arbol de trabajo, archivo restaurado al sha `289842457a5b` | `python` |
| Adyacente 247 passed (`06-`) | arbol de trabajo con la cura | `venv/Scripts/python.exe` |
| Gate 13/13 (`15-`, `16-` y este parrafo) | arbol de trabajo con todas las escrituras | `python` |
| Saldo 200 (`07-`) | red real, un envio, cero reintentos | `python` |

## Lo que NO se corrio en esta sesion (declarado, no callado)

- La **suite completa** de pytest: no la pide el mandato de la sesion, y el rojo de interprete de
  `test_jev_pilot_sdk_ac9.py` (ver la nota arriba) muestra que correrla con el interprete equivocado produce
  rojos que no son del codigo. La regresion se mido en las tres baterias adyacentes al brazo (247 pruebas).
- La **verificacion del commit en clon externo**: no hay commit, porque no fue ordenado (D6). Queda pendiente
  para cuando el operador lo de, y se hara en `AppData/Local/Temp`, nunca dentro del arbol (V7).
- La **revision L3**: no se corrio; es opcion del operador sobre lo que se empuje.
- El **congelado del protocolo** (paso 3.1 de FASE-C) y la eleccion entre las salidas (a) y (b) del registro:
  `protocolo.json` sigue BORRADOR y `muestra.json` sigue CONGELADA, sin un byte movido (D4, V2).

## Sello del commit (mismo 2026-10-04)

Este sello **vence** las frases de esta sesion que decian «sin commit», «en espera de autorizacion» y «los
cinco cortes terminan sin commitear»: describian el quinto corte en el momento en que se escribieron y se
dejan, no se borran.

- **Revision al arrancar**: `5ca6395` (paridad contra el servidor medida arriba, en `§Arranque`).
- **Commit de la sesion**: `7547c1b` (rango `5ca6395..7547c1b`), 27 archivos, +1.694 / -15. Los hooks pasaron
  8/8 y la corrida individual de los seis checks sustantivos dio EXIT 0 antes de commitear
  (`version_consistency_checker`, `sync_versions --check`, `validate_plan_citations`,
  `build_lesson_index --check`, `validate_lesson_capitalization`, `verify_packs_in_committed_tree`).
- **No empujado**: `origin/master` sigue en `5ca6395`; `git rev-list --left-right --count origin/master...HEAD`
  = **0/1** (un commit local por delante). El push es acto del operador.
- **Revision L3**: **no se corrio**, por indicacion expresa («git commit sin L3»). Sigue siendo opcion suya
  sobre lo que se empuje, y no es deuda de esta sesion.
- **Verificacion en el arbol del commit** (clon limpio fuera del repo, V7): brazo **15 passed**, piloto
  77 passed / 13 skipped por SDK ausente, las tres baterias adyacentes **233 passed / 14 skipped**, y la cifra
  commiteada `git grep -c -E "^\s*def test_" HEAD -- tests` = **4.800**, que converge con la del arbol de
  trabajo. Crudo: `18-verificacion-en-clon-del-commit.txt`.
- **Un rojo del clon limpio que no es de este commit**:
  `test_el_derivado_versionado_del_repo_pasa_su_propio_check` corta EXIT 3 porque cuatro roles de
  `exclusiones_por_rol` (`.venv-wsl`, `build`, `temp`, `venv`) no existen en un clon y el emisor deja de
  publicarlos mientras el artefacto los lista. Se probo **en el mismo clon sobre `5ca6395`**: falla igual
  (1 failed, 10 passed). Preexistente y de estado de maquina, registrado con su duena en el crudo `18-` en
  vez de rebajar la asercion ni re-publicar el derivado desde el clon.
- **Precision que este sello se traga y no se calla**: el sello se escribe **despues** del commit que nombra,
  asi que vive en el commit siguiente (`7547c1b..` en cuanto se commitee este sello). Nada de lo posterior al
  rango citado esta afirmado como publicado.

