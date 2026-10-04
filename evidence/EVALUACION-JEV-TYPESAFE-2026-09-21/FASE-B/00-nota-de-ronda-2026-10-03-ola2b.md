# Nota de ronda - OLA 2 (continuacion 2) del piloto JEV, FASE-B, 2026-10-03

Rama `master`, arbol base **4c113de** (empujado y en paridad `0 0` con `origin/master`, medido al
abrir). Mandato: `scripts/`, `tests/`, `config/` y esta carpeta. Sin commitear al cerrar la tanda:
los cinco cortes terminan en espera de autorizacion.

> **Sello del quinto corte, en la misma sesion y despues de medir lo de arriba:** las mediciones >de esta nota son del 2026-10-03 y los commits cayeron ya pasada la medianoche, el 2026-10-04 >entre 10:09 y 10:13 (-0500). La autorizacion
> llego y la tanda se commiteo en cuatro commits tematicos y se empujo. Rango publicado
> `4c113de..4895d04`: `dccbb6a` feat(jev) el run y sus dos brazos, `f884ada` feat(wiring) la mudanza
> (a) de la fila 18 con su derivado, `bcd8d2a` docs(jev) los artefactos de FASE-B, y `4895d04`
> docs(AGENTS) la cifra. Paridad contra `origin/master` re-medida tras el push: `0 0`. El escaneo
> L3 deep se corrio **antes** de empujar, por decision del operador, y no devolvio hallazgos.
> La frase de arriba se conserva tal cual porque describia el estado al cerrar la implementacion,
> no una promesa.
>
> Dos cosas quedan explicitamente fuera de este sello. La fila 18 del
> `33-registro-unificado-de-pendientes-2026-09-29.md` **no se estampo aqui**: esa ruta esta
> prohibida para esta sesion, y la mudanza se ejecuto leyendola, no escribiendola -le toca a una
> sesion con esa ruta autorizada, como la propia fila ya venia diciendo para el sello `07-`. Y el
> cierre post-fase del plan (README, dependencias, checklist, 09 y 10) sigue pendiente: no era
> mandato de esta tanda.

## Que se ejecuto, con su evidencia

| Paso | Estado | Evidencia (ruta) |
|---|---|---|
| 1a cliente Jev en `run` | HECHO | `scripts/evaluate_jev_pilot.py` (`run`, `revisar_preflight`, `limites_desde_protocolo`, `recuperacion_fria`, `recuperacion_medida`); `scripts/decision_client.py` (`cargar_sdk`, `cliente_jev`, `preflight_jev`, `system_one_jev`, `cargar_transporte`); `metrics_tests.txt`, `integracion.json` |
| 1b AC9 con SDK real + `MockTransport` | HECHO | `tests/quality_gates/jev_pilot/test_jev_pilot_sdk_ac9.py` (14), `metrics_tests.txt` (84 passed), `mutation.json` |
| 1c brazo DeepSeek por la costura | HECHO | `scripts/proveedores/deepseek.py`, `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py` (10); `llm_provider.py` intacto: `git diff --numstat` vacio sobre esa ruta y control por AST |
| 1d seis artefactos del prompt 05 | HECHO | `contract.txt`, `modelos.json`, `integracion.json`, `import_scanner.txt`, `metrics_tests.txt`, `mutation.json` |
| 2 censo `exclusiones_por_rol.*.cantidad` | HECHO y re-verificado en disco | un solo lector-asercion en codigo versionado: `tests/test_validate_wiring_alcance_por_declaracion_git.py:287`; un solo emisor: `scripts/validate_wiring.py:783-806`; cero coincidencias en `modules/`, `config/`, `docs/`, `archives/`, `.agents/` |
| 3 P4, el porton | **ABIERTO el mismo dia, en dos llamadas** | `preflight.json`: intento 1 = 401 (credencial vencida, no plomeria); intento 2 = AUTENTICADA con la llave reemplazada por el operador. Contraste del pin: `jev-1.13.0` no esta listado por `Models.list()` y el servicio lo acepta y lo devuelve |
| 4 corrida k=8 y techos | **EJECUTADA una vez, split dev** | `corrida_k8_2026-10-03.txt`: 2 llamadas, `attempts` 1 cada una, usage observado, `modelo_efectivo` jev-1.13.0. Techos escritos en `protocolo.json`: tokens_in=1834, tokens_out=139 (maximo observado por llamada, sin margen, con su comando en el `motivo`). `usd` sigue null y `status` sigue BORRADOR |
| 5 mudanza (a) de la fila 18 | HECHA, siete pasos | `scripts/validate_wiring.py` (schema 1.3, emisor, salida, procedencia conservada, dos prosas), `tests/test_validate_wiring_alcance_por_declaracion_git.py` re-anclado, `tests/test_validate_wiring_diente_mudanza_1_3.py`, `.opencode/wiring_report.json` regenerado en el mismo cambio |
| 6 validador de `protocolo.json` | HECHO | `validar_protocolo()` + modo CLI `protocolo-check`; `tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py` (24 con sus parametrizaciones) |
| 7 P4 re-medida con la seleccion del hermano | HECHA | `temp/ola2-2026-10-03/45-p4-remeida-hermano-post-mudanza.txt`: **294 passed** (decision_client + lesson_relevance + phase_briefing + jev_pilot) sobre el arbol final, EXIT 0 |
| 8 disparo real de D3/S14 | MEDIDO, **no disparado** | ver el ultimo apartado de esta nota |

## La mudanza (a), medida y no narrada

- Criterio de cierre de la fila, verificado sobre el artefacto: **cero** ocurrencias de `"cantidad"`
  y de `"ejemplo"` dentro de `exclusiones_por_rol` del JSON publicado (26 lineas de bloque leidas con
  `json.dumps` del objeto, no de memoria). Cada rol queda con `cantidad_versionada` y `motivo`.
- `--check` conforme con digest publicado (`temp/ola2-2026-10-03/39-check-post-mudanza.txt`,
  EXIT 0) y la salida nombra el desglose:
  `exclusiones_por_rol: .venv-wsl bruto=582 versionada=0, archives bruto=12 versionada=12, build
  bruto=14 versionada=0, evidence bruto=115 versionada=115, temp bruto=114 versionada=0, venv
  bruto=7610 versionada=0`.
- Las rutas de procedencia viejas (`exclusiones_por_rol.<rol>.cantidad`/`.ejemplo`) **se conservaron**
  en el commit de transicion, como pedia el paso 3 de la fila: son no-op contra el calculo de hoy y
  son las que evitan que el `--check` lea como DIVERGE una clave que el publicado del commit previo
  todavia lleva.
- Efecto colateral medido, no ignorado: la poblacion del verificador subio con los archivos nuevos
  (`cobertura.archivos_en_alcance` 690 → 697) y ese numero **si** esta gobernado, asi que el derivado
  se re-publico. Es el unico numero que caduco con el trabajo de esta ronda: exactamente lo que la
  (d1) queria conseguir.
- El rojo de transicion aparecio tal cual lo anticipaba la fila: `--check` respondio
  `SOLO EN EL ARTEFACTO, el emisor ya no lo publica` por cada `cantidad`/`ejemplo` del 1.2 publicado,
  con EXIT 3. Se cierra publicando, no bajando la asercion.

## Decision del operador tomada en esta tanda (no reabrible sin otra linea suya)

1. **Excepcion nombrada en la denegatoria de cero red** del hermano
   (`test_la_puerta_y_sus_proveedores_no_importan_nada_que_pueda_hacer_red`): AC9 necesita un
   `MockTransport` de `httpx2` y la lista negra vetaba ese import dentro de la puerta. Se resolvio con
   una excepcion **escrita como triple** `(archivo, funcion, modulo)`, solo para
   `cargar_sdk`/`typesafe_sdk` y `cargar_transporte`/`httpx2`, y su contrafactual
   (`test_la_excepcion_de_cero_red_solo_cubre_la_funcion_que_la_declara`: un import a nivel de modulo,
   en otra funcion o en otro archivo sigue siendo rojo). De paso se cerro un agujero de la misma
   lista: nombraba `typesafe` (un modulo que no existe) y no nombraba `httpcore2` ni `typesafe_sdk`,
   el mismo defecto de nombre real que `be8ccec` corrigio en `FORBIDDEN_MODULES` del runner.
2. **Terminar lo offline y no escribir techos no medidos**: con P4 cerrado en 401, `protocolo.json`
   conservaba sus dos techos en null. La decision se tomo con el porton aun cerrado y siguio vigente
   hasta que el operador reemplazo la credencial: reabrido P4, la corrida k=8 se corro y los dos techos
   se escribieron **con la medida delante**, no antes. `usd` sigue null (fuera de gobernanza) y `status`
   sigue **BORRADOR** (su congelado es FASE-C).

## Dos defectos que la ronda encontro en su propio instrumento

- `test_error_kind_clasifica_subclases_por_su_antecesor` estaba **verde sin diente**: su subclase ya
  estaba nombrada en `CLASES_DE_ERROR`, o sea apagar la caminata del MRO no la movia. Se re-anclo a un
  nombre que la tabla no conoce y el mutante M9 lo confirmo.
- El ancla del mutante M5 era **prefijo de una linea mas larga**: `replace(..., 1)` mutaba la entrada
  de `preflight_jev` y dejaba intacta la de `system_one_jev`, con lo que el control daba verde con el
  defecto puesto. Se anclo a la linea de arriba, unica.
- Y uno de instrumento: cuatro mutantes salieron primero NO-APLICADO por comparar literales con `\n`
  contra un arbol checkado en CRLF. Un mutante que no casa no es un verde: es un cero que hay que
  publicar. El arnes (`temp/ola2-2026-10-03/mutacion.py`) traduce el literal al EOL real y emite
  `ocurrencias_del_literal` por mutante.

## Paso 8: el disparo de S14, medido tres veces

Fila 3 del `33-registro-unificado`: S14 es *corpus mixto si el triaje corre con `--plans-dir` sobre
copia*, dueno este plan, FASE-D/RELEASE, y su disparador es la primera llamada con `--plans-dir` sobre
un directorio que no sea el repo. Las tres llamadas se hicieron contra
`C:/Users/Jhond/Github/clone-jev-ola2/.opencode/plans` (el clon de verificacion de esta misma tanda,
en el commit `4c113de`, o sea una copia fiel y fuera del repo):

1. `temp/.../42-disparo-s14.txt` - `status: EMISOR-NO-CONFIGURADO`, EXIT 7, `index_status: FRESCO`,
   poblacion `ancladas 19 / pool 78`, `ruta_del_suelo` = el indice **del repo**.
2. `temp/.../43-control-s14-plan-dir-del-repo.txt` - la misma corrida con el `--plans-dir` por defecto:
   poblacion **identica** (19 / 78) y mismo suelo.
3. `temp/.../44-disparo-s14-copia-divergida.txt` - con un plan de marcador anadido solo a la copia:
   `SUELO-AUSENTE`, EXIT 2 (`resolver_plan` no acepto el directorio sintetico), y el marcador se borro
   del clon despues de medir.

**Veredicto: disparo NO confirmado, con dos causas medidas** (y sigue vigente despues de abrir P4: la
causa no era la credencial, era que `--plans-dir` no redirige el suelo). Primera: `--plans-dir` redirige la
resolucion del plan pero **no** redirige el suelo - con `index_status: FRESCO` la poblacion sale del
indice versionado del repo, y por eso el numero no se mueve entre las dos condiciones. Segunda: sin
emisor configurado el triaje no tria, o sea no hay corpus que se mezcle en un resultado.

Lo que si dejo la medicion, y es un hallazgo para el dueno de S14: en la condicion (1) el plan se
resolvio **en la copia** mientras el pool salio **del indice del repo**, y el informe no avisa en
ningun campo que las dos mitades vienen de arboles distintos. Eso es la forma latente del corpus
mixto, silenciosa en el JSON. Queda registrada aqui, con sus tres crudos, y la fila sigue ABIERTA con
su dueno: confirmar el disparo exige una llamada que si trie (emisor a parte) o un `--plans-dir` que
fuerce el rebuild del suelo.

## Cifra canonica de la ronda

Arbol de trabajo: **4,776** (`grep -rE "^\s*def test_" tests --include=*.py`). Commiteado en HEAD al
cerrar la tanda: **4,717**. El delta de 59 es trabajo sin commitear; la nota de ronda esta en
`docs/cobertura-historia.md` y la cabecera y las dos filas de la tabla de `AGENTS.md` ya la reflejan
(gate `python scripts/validate_agents_md.py`: PASS 11/11).

> **Re-medido tras el sello del quinto corte:** con el rango `4c113de..4895d04` ya empujado, la
> cifra commiteada es **4,776** -el mismo numero que el arbol de trabajo, porque el delta de 59
> entro con estos commits-. El parrafo de arriba se deja como estaba: media el arbol antes de
> commitear, y decir hoy "4,717 commiteado" seria citar un HEAD que ya no es el HEAD.
