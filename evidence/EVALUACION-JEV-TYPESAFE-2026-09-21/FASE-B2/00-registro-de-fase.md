# 00 · Registro de fase — SESION 3.5 «FASE-B.2: el instrumento que faltaba» (EVALUACION-JEV-TYPESAFE-2026-09-21)

Sesión dueña designada de **CR-1 a CR-4**, los cuatro cambios que FASE-C dejó abiertos y que su propio
registro remitía a «una sesión con mandato sobre `scripts/` y `tests/`». Esta sesión **implementa el
instrumento**: `report` y `decide` en `scripts/evaluate_jev_pilot.py`, el contador de clasificación y del
extremo a extremo, el CLI del `run` y el re-anclaje de CR-4. **Cero llamadas de red y cero inferencias**: la
re-apertura de C es otra sesión con otra autorización.

Mandato ejecutado: `scripts/`, `tests/`, `config/` y `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/`.
`config/` no se tocó: ninguna de las cuatro CR pedía configuración, y meterla habría sido inventar superficie.

---

## 0. Arranque, verificado y no copiado

| Aspecto | Medido al arrancar |
|---|---|
| Árbol base | `git rev-parse HEAD` = `40c2754cf8dd245c616a34ac333e996416c99727`; `git status --porcelain` = **vacío** |
| Bateria del piloto | `venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -q` → **1 failed, 89 passed**, EXIT=1 (crudo `01-`) |
| Bateria del protocolo | mismo instrumento sobre `test_jev_pilot_protocolo_check.py` → **1 failed, 23 passed**, EXIT=1 (crudo `02-`); el rojo es `:43`, el aviso del congelado = CR-4 |
| Quick gate | `run_all_validations.py --quick` → **13/13**, EXIT=0 (crudo `03-`) |
| Insumo real de C | `FASE-C/respuestas.jsonl` = **6 líneas** (3 brazos × 2 pares de `eval`), con las claves que el emisor necesita |

**El rojo previo queda declarado con su causa**: 1 failed / 23 passed no era un fallo del instrumento, era el
aviso que la propia aserción anunciaba («si alguien lo congeló aquí, esto es el aviso»). FASE-C congeló el
protocolo y no podía tocar `tests/` (su §5), así que lo estampó como CR-4.

### Correcciones al censo delegable (verificadas en disco antes de usarla)

El censo se delegó a `Explore` (solo lectura) y se re-verificó. Tres afirmaciones del mandato o del censo
no casaban con el árbol; se consignan porque de ellas dependía el diseño:

1. **«maestro:153 "prepare, check, run, report"»** → la línea de interfaces previstas del runner está en
   `01-plan-maestro.md:172`, no en 153. El contenido es el que se citó; la coordenada estaba desfasada.
2. **`report` no estaba «fuera del parser con EXIT 2» del runner**: era `invalid choice` de argparse, que
   también da 2 pero por otra ruta (el crudo `FASE-C/09-` lo muestra). Por eso el contrato de «negación con
   causa escrita» había que implementarlo, no heredarlo: `report`/`decide` se niegan ahora con un mensaje
   propio y `main()` devuelve 2 (`_refuse` re-escrita en `:320`).
3. **El censo encontró una rama duplicada e inalcanzable** en `main()`: el bloque `protocolo-check` estaba
   escrito dos veces (`:794-800` y `:801-807`). Se retiró la copia muerta al cablear los modos nuevos; se
   declara como cambio **fuera del alcance de los CR** (H11 abajo).

---

## 1. CR-1 — el contador de clasificación y el extremo a extremo, como instrumento testado

**Cerrado.** Definiciones aplicadas, leídas del maestro y no reinventadas (`01-plan-maestro.md:88-91`, y la
regla de publicación en `:93`):

| Cociente | Regla aplicada | Numerador / denominador |
|---|---|---|
| recuperación | pertinentes importantes presentes entre candidatos / importantes del conjunto humano elegible | `recuperacion_medida()` (FASE-B, testada) — no se recalcula |
| precisión entre propuestas | elecciones correctas / **elecciones efectivamente hechas** | abstenciones y fallos quedan fuera, en su columna propia |
| recall importante dentro de candidatos | correctas / importantes **cuyo target sí estaba entre los candidatos** | un par no recuperable no es una oportunidad del clasificador |
| extremo a extremo | correctas / **conjunto importante elegible despachado**, incluyendo omisiones de recuperación y fallos del camino | maestro `:90` y `:93`: el fallo no se excluye para mejorar el score |

Productores nuevos en `scripts/evaluate_jev_pilot.py`: `estado_de_propuesta`, `es_acierto`,
`poblacion_de_comparacion`, `conteos_por_brazo`, `cocientes_por_brazo`, `conteo_de_abstenciones`,
`latencias_por_brazo`, `fallos_de_contabilidad`. Nada rellena a mano (AC10): una fila cuyo par no está en el
conjunto elegible se publica en `contabilidad.fuera_del_conjunto_elegible` en vez de descartarse.

**Forma del dato, medida con el control `test_los_cuatro_denominadores_no_comparten_un_denominador_unico`
sobre insumos sintéticos:** recuperación 1/2, precisión 1/2, recall 1/1, e2e 1/2. La envoltura `metrics()`
de FASE-A comparte un solo `den` entre precisión y recall (`:191-192`), así que **no puede** expresar cuatro
denominadores separados; `report` emite cociente por cociente con `score()` —el otro contrato probado en
FASE-A— y `metrics()` queda intacto, seguido por su test y sin productor (H7).

---

## 2. CR-2 — `report` y `decide`, emisión mecánica sin red

**Cerrado.** `report` lee `respuestas.jsonl` + `etiquetas.json` + `muestra.json` + `protocolo.json`; no abre
transporte, no instancia clientes, no lee credenciales. `decide` aplica `criterios_adopcion` del protocolo
CONGELADA sobre el informe y emite `decision.json` + `decision.md` con el schema `jev-pilot-decision/v1`
(ese shape es el contrato: no se inventó otro).

Reglas del maestro implementadas como aserciones y provocadas cada una con protocolos sintéticos:

| Regla | Dónde | Diente que la hace perder |
|---|---|---|
| fallo operativo → `run_status=FALLIDO`, `decision=null`, **nunca RECHAZAR** | `estado_del_run` | `test_un_fallo_operativo_de_autenticacion_es_FALLIDO_y_nunca_RECHAZAR` |
| contabilidad rota (`attempts>1` con `max_retries=0`) es impedimento, no derrota | `fallos_de_contabilidad` | `test_la_contabilidad_rota_tambien_es_FALLIDO...` |
| indisponibilidad detiene o aplaza, **no elimina el brazo** (AC12) | `estado_del_run` / margen | `test_una_indisponibilidad_no_elimina_el_brazo` |
| `ACTIVAR` requiere `cobertura_min` medido; `ACTIVAR` y `RECHAZAR` requieren criterios evaluables | `regla_de_adopcion` | `test_activar_y_rechazar_se_provocan...` (parametrizado 2×) + `test_mutante_umbral_de_margen_voltea_la_etiqueta_emitida` |
| `COSTE-NO-PAGADO` describe la decisión de no ejecutar; con `usd` null queda bloqueada | `regla_de_adopcion` | `test_coste_no_pagado_solo_cuando...` y `test_coste_no_pagado_queda_bloqueado...` |
| MUESTRA-INSUFICIENTE con datos válidos pero potencia insuficiente | `regla_de_adopcion` | `test_suficiencia_bajo_el_umbral_emite_MUESTRA_INSUFICIENTE` |
| un cociente NO-EVALUABLE ⇒ el emisor no elige: emite estado y bases | `regla_de_adopcion` | `test_decide_no_elige_cuando_un_criterio_queda_no_evaluable` |
| denominador cero = NO-EVALUABLE con motivo, nunca 100 ni 0 | `score()` + `report` | `test_un_denominador_cero_es_no_evaluable_y_no_cien_ni_cero` |
| recomendación Jev separada de elegibilidad D6; `transfer_status: PENDIENTE` | `decide` | `test_decide_sobre_los_registros_reales...` |

**Códigos de salida del CLI, ahora cuatro y nombrados** (antes: 0/1/2; el 3 nace en esta sesión): `0` emitido
y con decisión · `1` insumo declarado ausente en disco, o informe que no produjo `report` · `2` argumentos
faltantes (la negación histórica) · `3` **emitido sin decisión** (`decision=null`), que es el estado de C y el
que devuelve hoy `decide` sobre sus registros.

**Sobre los registros reales de C** (crudos `04-` y `05-`, artefactos `informe_comparativa.json`,
`decision.json`, `decision.md`): `run_status=INCOMPLETO`, `decision=null`, `EXIT_DECIDE=3`.

---

## 3. CR-3 — el CLI del `run` y la credencial por el camino del contrato

**Cerrado.** Dos piezas, y es la única parte de la sesión que toca el camino que hace llamadas:

1. `--etiquetas` en el parser de `run` (`:1469`) y propagado a `run()` (`:1549`). H5 de FASE-C medía que por
   CLI `run_resumen.json` salía con `recuperacion: null`. Diente:
   `test_el_cli_del_run_propaga_etiquetas_y_publica_la_recuperacion` — sin la bandera, `recuperacion` sigue
   en `null` (el runner no la inventa); con ella, 1/1.
2. `credencial_del_sdk` (`:1197`): rellena `TYPESAFE_API_KEY` desde `.env` **por nombre**, solo si el entorno
   no la trae —la misma regla que los arneses de C (`FASE-C/11-arnes-correr-jev-eval.py:32-34`)— y devuelve
   un estado con tres claves: `nombre`, `fuente`, `accion`. **Ni el valor ni su longitud**: publicar la
   longitud es publicar la forma del secreto. El SDK sigue resolviendo la clave desde su entorno porque
   `decision_client.cliente_jev` mantiene `api_key=None` (`decision_client.py:1327-1344`), y hay un diente
   que lo corta si el runner empezara a pasarla.
   Solo se llama cuando `enviar is None`: la vía inyectada no la toca, medido con contador
   (`test_el_run_con_enviar_inyectado_nunca_toca_la_credencial`).

Prueba de la vía CLI de punta a punta sobre un ledger persistido, sin SDK ni red: `PuertaFalsa` inyectada por
`monkeypatch` sobre `_puerta`, con `run_resumen.json` escrito en `tmp_path`.

---

## 4. CR-4 — el aviso del congelado, re-anclado y no borrado

**Cerrado.** `test_jev_pilot_protocolo_check.py::test_el_protocolo_versionado_pasa_y_deja_un_solo_nulo_declarado`
ahora ancla `CONGELADA`, afirma `congelado == {jhon, 2026-10-04}` y **conserva el diente contrario**: una copia
del versionado devuelta a `BORRADOR` sigue leyéndose como `BORRADOR` por el mismo lector, y el lector sigue
tratando `BORRADOR` como forma válida. Un verde vacío no prueba el ancla, así que la segunda mitad del diente
está ejecutada, no escrita.

El rojo previo y su causa quedan en el docstring de la prueba (crudo de C `22-`), con la regla de la casa:
la cura re-ancla, no baja la aserción. Resultado: **24 passed** (antes 1 failed / 23 passed), y el piloto
completo **126 passed** (antes 1 failed / 89 passed).

---

## 5. Re-anclaje del test de FASE-A (punto 4 del mandato)

`test_jev_pilot_offline.py::test_prepare_and_check_do_not_construct_clients` conservó sus 7 funciones y su
guard de `FORBIDDEN_MODULES`. El contrato cambió y el cambio está escrito dentro del test: `decide` sin
insumos **sigue** negándose con 2, y con insumos offline **emite** —ambas mitades corren bajo el mismo guard
de imports, así que la emisión nueva queda probada sin SDK. Con la muestra sin revisar de `_prepare_write`,
el emisor publica NO-EVALUABLE (`denominador_cero`) y la regla congelada emite `MUESTRA-INSUFICIENTE`
(0 de 4 pertinentes), no un número inventado.

---

## 6. Dientes, mutantes y su restauración

35 funciones nuevas en `tests/quality_gates/jev_pilot/test_jev_pilot_report_decide_fase_b2.py` (36 casos con
la parametrización). Todos bajo el guard de sockets `autouse` del `conftest.py` de la selección.

El par de mutación está en `FASE-B2/mutation.json`, producido por `12-arnes-mutacion.py`: el módulo se carga
por `importlib` desde la ruta versionada, se parcha **en memoria**, y el árbol no se muta (sha256 de la
fuente idéntico antes y después, `41c3f5cb…`). Cinco mutantes, cinco caídas por la causa nombrada:

| Mutante | Qué se mueve | Por qué cae por esa causa |
|---|---|---|
| M1 `es_acierto` siempre falso | numeradores de precisión, recall y e2e a 0 | la recuperación **no** se mueve: la pone la función testada |
| M2 `ninguna-aplica` vuelto elección | la columna propia de abstenciones se vacía | el criterio congelado perdería su denominador aparte |
| M3 `error_kind` colapsado en `sin_fila` | el denominador del e2e baja de 2 a 1 | el score mejora **excluyendo el fallo**: lo que el maestro `:93` prohíbe |
| M4 la credencial publicada con `valor` y `longitud` | el centinela aparece en el estado | una credencial, o su forma, publicada es una fuga |
| M5 fallos operativos borrados del informe | margen pasa a evaluable, `run_status` a COMPLETO | AC12: medirle al modelo una indisponibilidad de la infraestructura |

---

## 7. Los criterios de cumplimiento del mandato, con su comando medido

| §5 del mandato | Comando | Valor medido | Crudo |
|---|---|---|---|
| Batería del piloto verde tras re-anclar CR-4, rojo previo declarado | `venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -q` | **126 passed**, EXIT=0; protocolo **24 passed**; antes 1 failed / 89 y 1 failed / 23 | `01-`, `02-`, `06-`, `07-` |
| Quick 13/13 con EXIT leído sin tubería | `venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **13/13**, EXIT=0 | `03-`, `13-`, `15-` |
| Cero red e inferencias; AC6 sin hallazgos | `venv/Scripts/python.exe scripts/decision_client.py --scan-imports` | **SIN-HALLAZGOS** — 0 imports prohibidos fuera de la puerta, 0 cargas dinámicas | `08-` |
| `llm_provider.py` sin un byte de cambio | `git diff -- modules/providers/llm_provider.py` | **vacío** | `09-` |
| FASE-C y las congeladas intactas | `git status --porcelain` | ningún `M` bajo `FASE-C/`, ni en `muestra.json` ni `protocolo.json` | `16-` |
| `report` reconstruye desde el `respuestas.jsonl` real y casa con lo que C midió | `... report --respuestas FASE-C/respuestas.jsonl ...` | recuperación **1/2 = 0.5** en los tres brazos (igual que C); latencia jev 395.794 ms y el fallo de 48.478 ms publicado aparte | `04-`, `10-` |
| `decide` reproduce el estado de la sesión 3 sin contradecirla | `... decide --informe ... --protocolo ...` | `run_status=INCOMPLETO`, `decision=null`, ACTIVAR EXCLUIDA, RECHAZAR NO EMITIDA, COSTE BLOQUEADO, MUESTRA-INSUFICIENTE no emitida por la regla, `transfer_status=PENDIENTE` | `05-` |
| Los cuatro CR estampados con su evidencia | este registro, §1-§4 | CR-1 · CR-2 · CR-3 · CR-4 cerrados cada uno con su diente nombrado | — |
| La canónica re-medida y estampada **solo si se movió** | `grep -rE "^\s*def test_" tests --include=*.py` | **4.835** (antes 4.800; +35, todos de esta ronda) → una edición en `AGENTS.md` (cabecera y fila `quality_gates` 951→986) y la nota en `docs/cobertura-historia.md` | `15-`, `16-` |
| El atributo verificable a terceros | doble corrida con fecha fija + `diff` | `informe`, `decision.json` y `decision.md` **idénticos byte a byte** (sha256 iguales); con otra fecha solo se mueve la línea `fecha` | `10-` |
| Negación sin insumos con EXIT nombrado | `... report` / `... decide` / insumo ausente | **2** con causa escrita · **2** · **1** nombrando las cuatro rutas | `11-` |

---

## 8. Hallazgos de esta sesión

- **H7 — `metrics()` no expresa AC10.** Comparte un único `den` entre precisión y recall (`:191-192`), así
  que un informe con cuatro denominadores separados no puede salir por esa envoltura. Se deja la función
  intacta y probada, `report` emite con `score()`, y un control afirma que los dos denominadores difieran.
  Dueño si se quiere cerrar: el contrato de salida de FASE-A, con su re-anclaje y su motivo.
- **H8 — el margen es ahora calculable y sigue sin ser evaluable, por otra causa.** C declaró
  `margen_vs_deepseek: NO-EVALUABLE` porque «la magnitud no la produce ningún instrumento existente». Hoy el
  instrumento existe y la magnitud es **0.0** (jev 0.5 vs deepseek 0.5). Sigue NO-EVALUABLE, pero por la razón
  que da AC12: la pata Jev perdió un par por un fallo de transporte. El informe publica las dos cosas —
  `diferencia_calculada: 0.0` y `estado: NO-EVALUABLE` con su motivo— para que el operador no tenga que
  elegir entre el número y la excusa.
- **H9 — diferencia de texto contra el registro, no de estado.** C escribía MUESTRA-INSUFICIENTE como
  «ponible por el operador». El emisor nuevo la escribe «EXCLUIDA por la regla congelada; ponible por el
  operador» y añade el **denominador efectivo** (pares con elección utilizable en los dos brazos) que ahora
  calcula el instrumento: **1**. El literal que gobierna la adopción no se emite en ninguna de las dos versiones.
- **H10 — nace el EXIT 3.** «Emitido sin decisión» no es un fallo (1) ni una negación (2). Se documentó en el
  docstring del módulo y en el §2 arriba.
- **H11 — rama duplicada retirada.** `main()` tenía el bloque `protocolo-check` escrito dos veces; la segunda
  era inalcanzable. Se borró al cablear los modos nuevos. Fuera del alcance de los CR, declarado aquí.
- **H12 — el informe nuevo no publica la comparación de `usage` contra los techos congelados.** C lo hacía a
  mano en su arnés (H3: `tokens_out` 139 vencido por 145 y 158). `report` publica `usage_por_fila` y el techo
  en `protocolo`, pero **no** el veredicto de exceso. Queda como deuda con dueño (§9), no como omisión silenciosa.

---

## 9. Deuda declarada con dueño (esta sesión no la absorbe)

| # | Deuda | Dueño | Criterio que la pide |
|---|---|---|---|
| B2-1 | `report` no compara `usage_normalized` contra `limites_gasto.tokens_in/tokens_out` ni publica `cost_calculated`/`cost_billed` | `scripts/evaluate_jev_pilot.py` (`report`) | AC4, «tokens y contabilidad de coste separada» |
| B2-2 | `metrics()` queda sin productor mientras `report` emita cociente por cociente | el contrato de salida de FASE-A | AC10 |
| B2-3 | La comparación del margen sigue apoyada en 1 par utilizable; el umbral 0.25 no discrimina con denominador 2 (H6 de C) | re-apertura de C, decisión del operador **antes** de correr | AC5 |
| B2-4 | Limitación del reintento de descarga en el diente de frescura (un `SIN-DESCARGA` transitorio pinta `VENCIDO` un gobernado fresco) | `scripts/verify_qmind_context_freshness.py`, instrumento del hermano | ya declarada por C |
| B2-5 | Transferencia D7/D6 al hermano | `transfer_status: PENDIENTE`; solo con instrucción literal que nombre archivos y alcance | AC7 |

El write-back del `10-analisis` no se re-dispara: esta sesión no editó ese archivo.

---

## 10. Lo que NO hizo esta sesión

**Cero envíos de inferencia y cero envíos de conectividad** — el camino del SDK no se instanció: `report` y
`decide` no lo importan (AC6: `SIN-HALLAZGOS`, 0 imports prohibidos), la batería corrió bajo el guard de
sockets del `conftest`, y la vía CLI del `run` se ejercitó con `PuertaFalsa`. Ninguna credencial —ni valor,
ni máscara, ni longitud— viajó a un documento ni a un sub-agente; el único valor que se manipuló es un
centinela sintético de `tmp_path`, y `mutation.json` registra sus **claves**, no su contenido.

Sin commit. Sin push. Sin revisión L3. Sin write-back en QMind. Sin editar el hermano, ni el plan archivado,
ni `FASE-C/`, ni `muestra.json`, ni `protocolo.json` (CONGELADAS). Sin ofrecer la fase siguiente. Los cinco
cortes terminan en **espera de autorización del operador**; el `git commit` es un acto posterior, separado
y suyo.

⟦Vencida en su primera mitad por el sello de §12: el operador autorizó **«Commit sin L3»** y el trabajo se
commiteo en `0a6c84c` (32 archivos, +4410/−39, hooks pre-commit en verde) y su reparación en el commit
siguiente. **Sin push y sin L3 sigue vigente**: la paridad medida es `0 1` contra `origin/master`, o sea un
commiteado y nada empujado. La frase se conserva porque describe el estado al cierre de la fase de
ejecución, que es lo que esta hoja registra.⟧

⟦Y vencida también en su segunda mitad, en la misma sesión: **«Git Push»** se autorizó y se ejecuto, asi que
de las tres cosas que la anotacion de arriba declaraba pendientes, dos quedaron hechas (los dos commits) y
una empujada. El detalle medido esta en §13, incluido lo que el segundo empujon deja sin describir y donde
vive esa descripcion.⟧

### Árbol al cerrar, medido

```
M .opencode/wiring_report.json        (re-publicado por su escritor: 6+/6-, dos contadores + generado + git_sha)
M AGENTS.md                            (2+/2-: la cifra condicional del §5, una vez)
M docs/cobertura-historia.md          (45+/0-: la nota de la ronda)
M scripts/evaluate_jev_pilot.py        (847+/22-)
M tests/quality_gates/jev_pilot/test_jev_pilot_offline.py          (57+/3-)
M tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py  (21+/6-)
?? tests/quality_gates/jev_pilot/test_jev_pilot_report_decide_fase_b2.py  (35 funciones)
?? evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/
```

El derivado `.opencode/wiring_report.json` quedó **vencido con verde** a mitad de sesión (12/13) y se reparó
por su propio escritor, no a mano: `validate_wiring.py --write-report` y luego `--check` EXIT=0. La línea
`generado`/`git_sha` del artefacto reconoce el árbol donde corrió (`40c2754`).

---

## 11. Comandos exactos

```bash
# report y decide sobre los registros reales de FASE-C (EXIT 3 = emitido sin decision)
venv/Scripts/python.exe scripts/evaluate_jev_pilot.py report \
  --respuestas evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C/respuestas.jsonl \
  --etiquetas  evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/etiquetas.json \
  --muestra    evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/muestra.json \
  --protocolo  evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json \
  --out evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/informe_comparativa.json --fecha 2026-10-04

venv/Scripts/python.exe scripts/evaluate_jev_pilot.py decide \
  --informe  evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/informe_comparativa.json \
  --protocolo evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json \
  --out-dir  evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2 --fecha 2026-10-04

# determinismo: dos corridas, mismos bytes; con otra fecha solo se mueve la linea fecha
# negacion sin insumos: EXIT 2 con causa escrita; insumo ausente en disco: EXIT 1
venv/Scripts/python.exe scripts/evaluate_jev_pilot.py report
venv/Scripts/python.exe scripts/evaluate_jev_pilot.py decide

# baterias, mutacion, gobernanza
venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot -q
venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py -q
venv/Scripts/python.exe evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-B2/12-arnes-mutacion.py
venv/Scripts/python.exe scripts/decision_client.py --scan-imports
venv/Scripts/python.exe scripts/run_all_validations.py --quick
venv/Scripts/python.exe scripts/validate_wiring.py --check
venv/Scripts/python.exe scripts/validate_agents_md.py
venv/Scripts/python.exe scripts/validate_governance_numbers.py
grep -rE "^\s*def test_" tests --include=*.py | wc -l
```

### Artefactos de la ronda

`01-` `02-` batería PRE · `03-` quick PRE · `04-` crudo de `report` · `05-` crudo de `decide` · `06-` batería
protocolo POST (24) · `07-` batería piloto POST (126) · `08-` scan AC6 · `09-` diff de `llm_provider` (vacío) ·
`10-` determinismo con shas · `11-` negaciones con EXIT · `12-` arnés de mutación y su crudo · `13-` quick POST ·
`14-` `wiring --check` · `15-` validadores post-documentación · `16-` mediciones de cierre · `17-` batería del
piloto tras escribir el registro (126 passed) · `18-` quick post-registro (13/13) · `19-` `wiring --check`
post-registro ·
`informe_comparativa.json` `decision.json` `decision.md` `mutation.json` (emitidos por el runner y por su
arnés, no escritos a mano).

---

## 12. Sello del commit `0a6c84c` y su verificación en el propio árbol

El operador autorizó **«Commit sin L3»**. Se stagearon por nombre las ocho rutas del trabajo (nada de
`git add -A`), se re-corrió el quick gate **con el índice ya poblado** —el Secrets Check escanea
«tracked + staged», así que la pasada previa no había mirado aún los 25 archivos de `FASE-B2/`— y el commit
se hizo con los hooks activos, sin `--no-verify`: **32 files, +4410/−39**, `COMMIT_EXIT=0`.

Verificación, medida y no afirmada (`20-`, `21-` y su arnés):

| Chequeo | Instrumento | Valor |
|---|---|---|
| Árbol de trabajo | `git status --porcelain` | limpio |
| Cifra canónica **commiteada** | `git grep -h -c -E "^\s*def test_" HEAD -- "tests/*.py"` sumado | **4.835**, convergiendo con la que publica `AGENTS.md` (ya no es un número de árbol sin commitear) |
| Paridad con el remoto | `git rev-list --left-right --count origin/master...HEAD` | **0 1** — commiteado, nada empujado |
| Clon limpio del commit | `git clone --no-checkout` + `core.longpaths` + `core.autocrlf=input` dentro del clon | `0a6c84c`, árbol limpio, batería **113 passed, 13 skipped**, EXIT 0 (los 13 saltos son el SDK ausente en el clon, con su causa nombrada por el fixture `sdk`) |
| El commiteado reproduce el artefacto | correr `report`/`decide` dentro del clon y comparar por sha normalizado | `informe_comparativa.json` `990d6d96…` **igual**, `decision.json` `494df60b…` **igual**, `decision.md` `30dd6726…` **igual** |

### Lo que la verificación encontró, y se repara en el commit siguiente

**El primer commit se llevó un artefacto una revisión detrás de su propio código.** El diferencial es uno
solo y está impreso en `21-`: a `informe_comparativa.json` le faltaban las tres claves
`por_brazo/*/contabilidad/fuera_del_conjunto_elegible`, que el instrumento ganó a las 20:45 mientras el
informe se había emitido a las 20:34. `decision.json` y `decision.md` no estaban vencidos: su contenido no
porta ese campo, y por eso casaban. La causa es mi secuencia, no del contrato: regenerar el derivado después
de tocar el emisor era parte del cierre y no lo hice hasta verificar el commit. Se re-emiten con el código
commiteado y se re-miden (`16-` con los dos shas por archivo: `317541b3…` en disco, `990d6d96…` normalizado).

**Límite declarado del atributo §8**: «dos corridas producen bytes idénticos salvo la fecha» vale para la
misma invocación. Corriendo `report` con rutas absolutas desde otra raíz, el bloque `insumos` cambia porque
publica las rutas tal como se le pasaron —`21-` mide que **solo** se mueve `insumos` y que
`sha256_de_los_insumos` y los cocientes quedan idénticos—. Es procedencia, no lógica, y se consigna en vez de
adornarlo: quien busque un sha estable entre máquinas debe comparar `sha256_de_los_insumos`, no el archivo.
Dueño si se quiere cerrar: `scripts/evaluate_jev_pilot.py` (`report`, campo `insumos`).

**Permisos después del sello**: commit ejecutado dos veces (`0a6c84c` trabajo + el de esta reparación).
**Push sin ejecutar. Revisión L3 sin ejecutar, por instrucción expresa.** Sin write-back en QMind. Ningún
documento del hermano ni plan archivado tocado. FASE-C, `muestra.json` y `protocolo.json` siguen intactos
(el `git diff` de estas rutas contra `40c2754` está vacío; medido en `16-`).

⟦Vencida en su primera frase por §13: el push se ejecuto y la paridad se re-midio contra el servidor.
La segunda frase sigue vigente: **la L3 no se corrio**, y es decision del operador registrada en la misma
tanda («No correr L3 ahora»). El asunto de la L3 sobre un tip que se mueve tambien esta en §13.⟧

---

## 13. Sello del push `40c2754..e85954a`

El operador autorizo **«Git Push»**. Antes de empujar se midio el alcance, no solo el tip:

| Chequeo | Comando | Valor |
|---|---|---|
| Que dice el servidor | `git ls-remote origin refs/heads/master` | `40c2754…` al arrancar (igual que el ref local: no habia nada que reconciliar) |
| Que se mueve | `git log --oneline origin/master..HEAD` | **2 commits** (`0a6c84c`, `e85954a`), fast-forward puro, sin divergencia y **sin force** |
| Objetos | `git rev-list --objects origin/master..HEAD \| wc -l` | 59 objetos |
| Carga | `git diff --shortstat origin/master..HEAD` | 37 archivos, +4677/−39 |

Empujado: `40c2754..e85954a  master -> master`, `PUSH_EXIT=0`. Paridad re-medida **contra el servidor**, no
contra el ref local (`24-`): `git ls-remote origin refs/heads/master` = `git rev-parse HEAD` =
`e85954ae8bd307644e44f37a89a18dc001be9f9d`, `git rev-list --left-right --count origin/master...HEAD` =
**0 0**, arbol limpio.

### Lo que este push vence, medido por asunto y no por literal

Dos lineas de este propio registro decian lo que el push acabo de hacer:

* `:240` («**Sin push y sin L3 sigue vigente**: la paridad medida es `0 1»`) y `:349` («**Push sin
  ejecutar**»). Ambas quedan como foto del momento en que se escribieron, con esta anotacion encima; no se
  reescribieron, porque describen el estado al estampar, que es lo que una hoja de fase registra.
* `docs/cobertura-historia.md:113`, `:126` y `:138` tambien contienen «sin push», y **no se barren**: esas
  tres frases hablan de otras rondas y de otros rangos (`origin/master` en `5ca6395`, y el rango
  `6cdb430..7899f0f`). Contar menciones del literal y barrerlas hubiera convertido una prohibicion ajena en
  rojo propio.

**Los dos mensajes de commit publicados quedan con una frase vencida** («Sin push», dos ocurrencias). No se
hace `reword`: reescribir un commiteado ya empujado obliga a `push --force` sobre una rama compartida, y esa
no es la via de la casa. La errata vive aqui, en el registro, y `git log` sigue siendo la autoridad de que los
mensajes dicen eso.

### La L3, y el gate que este mismo sello re-abre

El operador eligio **«No correr L3 ahora»**. Queda declarado, con fecha (2026-10-04) y motivo, para que nadie
lea el rango publicado como ya revisado. Y hay una consecuencia que este sello produce y por eso se enuncia
aqui: **el commit de sello es un commit nuevo sobre `e85954a`**, asi que si algun dia se corre la L3 sobre
esta tanda, su baseline ya no es el rango empujado en `40c2754..e85954a` sino el que incluya a este sello. El
`skip` anterior no se arrastra a un tip nuevo.

**Este sello, empujado, no se describe a si mismo**: la regla de la casa es que un segundo push deja
incompleto el sello del primero, y reescribirlo abriria el mismo hueco un nivel mas arriba. El rango de este
segundo empujon (`e85954a..HEAD-del-sello`) queda publicado y verificable con el mismo par de comandos de
arriba; su autoridad es `git log`, no una nota que persiga al puntero.

### Permisos al cerrar el sello

Commit: tres ejecuciones. Push: ejecutado, paridad `0 0` re-medida contra el servidor. **L3: sin correr, por
decision expresa del operador.** Sin write-back en QMind. Sin tocar el hermano, los planes archivados,
`FASE-C/`, `muestra.json` ni `protocolo.json`. Sin ofrecer la fase siguiente: la re-apertura de C es otra
sesion con otra autorizacion.

### Sello del push `4661b6e..10dee08` (SESION DE SELLO de las filas 16 y 18 del 33-registro)

**Que se empujo, medido contra el servidor (2026-10-05):** `git ls-remote origin refs/heads/master` =
`10dee08` = `git rev-parse HEAD`; `git rev-list --left-right --count origin/master...HEAD` = `0 0` al cerrar
este bruto. El rango empujado desde el tip remoto previo es **un solo commit**, medido con `git log --oneline
4661b6e..HEAD`: `10dee08 docs(jev): SESION DE SELLO - filas 16 y 18 del registro unico, re-ancladas al tip
4661b6e`. Sus brutos: `26-verificacion-del-push.txt` y `27-quick-gate-post-sello-push.txt`.

**Lo que este push vence, medido por asunto y no por literal:**
* El mensaje publicado de `10dee08` lleva 1 ocurrencia de «sin push» (`git log -1 --format=%B 10dee08 |
  grep -oiE 'sin push' | wc -l` = 1); queda vencida y **no se hace reword**: reescribir un commiteado ya
  empujado obliga a `push --force` sobre una rama compartida, y esa no es la via de la casa.
* La fila 16 del `33-registro-unificado` (linea 51, anotador «Estampado 2026-10-04») decia «las ediciones de
  esta fila quedan sin commitear ... hasta que se pidan» y «`0c79e9c..4661b6e` = 13 commits». Ambas quedan
  superadas: ya estan commiteadas y empujadas, y el rango con `10dee08` medido ahora es `0c79e9c..HEAD` =
  **14** (`git rev-list --count`). **No se re-escriben**: son foto del momento de estampar y la convencion
  del registro es aditiva.
* `docs/cobertura-historia.md:113`, `:126` y `:138` dicen «sin push» de **otros** rangos (`5ca6395`,
  `6cdb430..7899f0f`); **no se barren**, porque contener el literal y barrerlo convertira una mencion ajena
  en rojo propio.

**La L3 y el gate que este sello re-abre:** el operador eligio **no correr L3** ni en el push de `10dee08` ni
aqui; queda declarado con fecha para que nadie lea el rango publicado como ya revisado. Consecuencia
estructural que este sello produce: el commit de sello es un commit **nuevo sobre `10dee08`**, asi que
cualquier L3 futura tendra por baseline un rango que ya incluye a `10dee08` y a este sello, no el que estampo
la fila 16. El skip anterior no se arrastra a un tip nuevo.

**Este sello, empujado, no se describe a si mismo:** la regla de la casa es que un segundo push deja
incompleto el sello del primero, y reescribirlo abriria el mismo hueco un nivel mas arriba. El rango de este
segundo empujon (`10dee08..HEAD-del-sello`) queda publicado y verificable con el mismo par de comandos de
arriba; su autoridad es `git log`, no una nota que persiga al puntero.

**Permisos al cerrar este sello:** Commit de sello: una ejecucion (tres archivos: `26-`, `27-` y este
apendice). Push: ejecutado, paridad re-medida contra el servidor. **L3: sin correr, por decision expresa del
operador.** Sin write-back en QMind. Sin tocar `scripts/`, `tests/`, `config/`, `VERSION.yaml`, `AGENTS.md`,
`.opencode/` ni `decision.json`. Sin ofrecer la fase siguiente: la re-apertura de C y el RELEASE siguen
pidiendo otra sesion con otra autorizacion.


