# Gap de contrato del piloto JEV: las dos salidas, con su coste medido (2026-09-30)

Documento de decision. **No se eligio ninguna salida y no se escribio codigo de produccion.** Lo que sigue
esta medido contra `scripts/decision_client.py` y `scripts/evaluate_jev_pilot.py` en la revision
`7737347e1572b52cb50e527086d7df8cc3950b71` (arbol de trabajo sin mutaciones de esta sesion sobre esos dos
archivos).

## 0. El contrato pedido, tal como esta escrito

`01-plan-maestro.md` Interfaz exige **once** campos por llamada: `provider_requested`,
`provider_effective`, `model_requested`, `model_effective`, `answers`, `usage_raw`, `usage_normalized`,
`elapsed_ms`, `attempts`, `error_kind`, y `request_id` cuando lo ofrezca el proveedor; <<ausente se conserva
como null con motivo>>.

## 1. Lo que la costura expone hoy (leido del codigo, no del docstring)

`ResultadoEvaluacion` (`decision_client.py:291-318`) tiene `__slots__` de siete campos
(`provider_status`, `proveedor`, `modelo`, `respuestas`, `usage`, `request_id`, `credencial`) y su `to_dict()`
publica esos siete. La construccion esta en `decision_client.py:699-715`.

Contraste con los once pedidos:

| Campo pedido | Estado medido hoy | Dato de la lectura |
|---|---|---|
| `provider_effective` | **expuesto** como `proveedor` | sale de `prov["nombre"]` (`resolver_proveedor`, `:596-627`) |
| `model_effective` | **expuesto** como `modelo` | sale de `payload["modelo"]`, o sea lo que el proveedor reporta (`:711`) |
| `answers` | **expuesto** como `respuestas` | `a_respuestas_tipadas(payload)` |
| `usage_raw` | **expuesto** como `usage` | `payload.get("usage")`, con guard de claves `input_tokens`/`output_tokens` (`:504-515`) |
| `request_id` | **expuesto** | `payload.get("request_id")`, ya puede ser None |
| `provider_requested` | **no expuesto**, y hoy es **degenerate**: `resolver_proveedor` solo devuelve el modulo cuyo `PROVEEDOR["nombre"]` coincide con el nombre pedido por `IAH_DECISION_PROVIDER`; no hay camino de fallback, asi que pedido = efectivo por construccion. La pareja vuelve a tener informacion exactamente cuando exista un segundo proveedor con eleccion (la fila D7+S10 del registro) |
| `model_requested` | **no expuesto**, pero **ya esta a mano**: el resolucion devuelve `declara` (`:628-631`), que contiene el pin `modelo` de AC8 (`:112-121`, `jev-1.13.0`). Exponerlo no requiere plomeria nueva, si no un campo en el contrato |
| `usage_normalized` | **no expuesto ni derivable dentro de la costura**: ella no conoce precios; en este repo el calculo de coste vive en `modules/providers/` y en la contabilidad del hermano, y el plan pide <<separar tokens observados, coste calculado y cargo facturado>> (`05-prompt-fase-B` item 6) |
| `elapsed_ms` | **no expuesto**: la costura no abre ningun temporizador alrededor de `prov["modulo"].evaluar(...)` (`:700`) |
| `attempts` | **no expuesto, y lo estructural es mas fuerte**: la costura hace **una** llamada y no tiene bucle de reintentos. Un contador suyo solo podria decir `1`. El plan med que los defaults del SDK dan `max_retries=2` o sea **3 intentos ante un 429** (`01-plan-maestro:68`, `04-contrato-ejecucion:44`), y esos intentos ocurren **dentro del cliente que arma el modulo proveedor**, no dentro de la costura |
| `error_kind` | **no expuesto**: la costura solo traduce `RespuestaIlegible` (`:702-706`); un 429/timeout del SDK se materializa dentro del proveedor, donde la costura no lo ve tipado |

Comprobacion de que esto no es opinion: `python scripts/decision_client.py --provider-status` responde hoy
`NO-CONFIGURADO` con `motivo_clase = env-de-proveedor-sin-definir` y EXIT 1 (crudo `04-` de esta tanda), y la
seleccion `tests/quality_gates/decision_client/` esta en **87 passed** (EXIT 0). O sea: **el gap no es un rojo
de suite, es una ausencia de superficie**. Un verde de 87 no prueba que los campos existan - es la familia de
<<un [OK] no prueba ausencia>>.

## 2. Salida (a): extender la costura del hermano, de forma aditiva y compatible

Que habria que tocar, medido:

- La clase: `__slots__`, `__init__` y `to_dict()` (tres sitios en `:291-318`). Anadir claves al **resultado**
  no rompe al guard `desconocidos = set(payload) - {"modelo","respuestas","usage","request_id"}` (`:382-384`),
  que gobierna el **payload del proveedor**. Si en cambio algn campo se pidiera *al* proveedor (p. ej. que el
  modulo reporte sus intentos), habria que ensanchar ese guard y entonces **si** se tocan consumidores: hay
  **7 afirmaciones** repartidas en 2 archivos de la seleccion que prueban exactamente esa frase
  (`test_decision_client_remediacion_bloque_a.py`, `test_decision_client_respuesta_ilegible.py`), y el
  contrato <<un archivo por segundo proveedor>> tiene su propia bateria (5 funciones en
  `test_decision_client_segundo_proveedor_un_archivo.py`) cuyo fixture es la plantilla
  `PLANTILLA_SEGUNDO_PROVEEDOR` (`:941-966`), que emite `{"modelo","respuestas","usage","request_id"}`: anadir
  claves al payload obliga a anadirlas tambien a la plantilla que se autogenera.
- Consumidores del resultado dentro del propio guion: `:1028` (`costura_funciona_con_ambos`), `:1073`
  (`out["RESUELTO"]` del informe `--json`), `:1107` (la salida de excepcion). Son tres, y son aditivos.
- Techo real de la salida (a), declarado en vez de maquillado: aunque se anadan los seis campos, **`attempts`
  y `error_kind` quedan mintiendo** para el camino del SDK, porque la costura no observa los reintentos que
  ocurren dentro del cliente que arma el proveedor. Publicar `attempts = 1` desde la costura sera un dato
  verdadero sobre *la costura* y falso sobre *la llamada facturable*. Eso choca de frente con la clausula del
  plan <<el SDK no puede reintentar por debajo de la contabilidad del runner>> (`04-contrato-ejecucion:44`) y con
  `test_sdk_retries_disabled_and_attempts_counted` (AC8, `05-prompt-fase-B:42`), que es la prueba que tiene que
  poder caer.
- Lo que la salida (a) **si** resuelve bien y barato: `provider_requested` (hoy degenerate, ver tabla),
  `model_requested` (el pin ya viaja en `declara`), `elapsed_ms` (temporizador alrededor de la unica llamada,
  y mide el tiempo real del proveedor including sus reintentos internos).

Coste resumido: 3 sitios de la clase + 3 consumidores + (solo si se pide al proveedor) 1 guard con sus 7
afirmaciones y 1 plantilla con sus 5 pruebas. Riesgo: convertir a la costura del hermano en duena de una
contabilidad que no puede ver.

## 3. Salida (b): producir los campos en el runner propio de JEV

Que habria que tocar, medido:

- `scripts/evaluate_jev_pilot.py` son **249 lineas** y hoy **no importa a `decision_client`** (sus imports son
  `argparse`, `hashlib`, `json`, `sys`, `pathlib`). Sus modos son `prepare` / `check` / metricas, y los modos
  de B/C se niegan con `_refuse(...)` -> EXIT 2 (<<el modo offline no construye clientes ni abre red>>,
  `:189-194`). Por lo tanto la salida (b) **no es barata**: para llevar el ledger al runner hay que que el
  runner llame al proveedor, y eso abre una de estas dos, ninguna gratuita:
  1. que el runner **importe a la costura** (dependencia nueva, inversa a la que existe hoy, y con ella el
     runner pasa a heredar el contrato de once campos que la costura no cumple: el gap no desaparece, se
     muda de casa); o
  2. que el runner **arme su propio cliente**, que es exactamente la *segunda costura* prohibida por el plan
     y por esta orden. Prohibido y no hecho.
- Lo que la salida (b) haria bien, si se resuelve como (b.1): `attempts`, `elapsed_ms` y `error_kind` por
  intento, que son los campos cuyo due natural es quien invoca con `RetryPolicy(max_retries=0)`.
- El plan ya tiene asignada esta pata: `01-plan-maestro:42` y la tarea 5 de FASE-B ponen el ledger y la
  contabilidad en `evaluate_jev_pilot.py`, no en la puerta. O sea (b) no es una idea nueva de esta sesion: es
  la decision ya escrita, y lo que falta es el permiso de FASE-B.

## 4. Lo que decide el operador, en una linea por opcion

- **(a) extender la costura** -> cubre `provider_requested`, `model_requested`, `elapsed_ms` de raiz; deja
  `attempts`/`error_kind` sin observacion real y `usage_normalized` fuera de su competencia. Coste acotado y
  aditivo **solo si ningn campo nuevo se pide al payload del proveedor**.
- **(b) mover el ledger al runner** -> cubre `attempts`, `error_kind`, `elapsed_ms` donde de verdad ocurren;
  exige que el runner llame (importar la costura o, prohibido, armar cliente propio) y depende del permiso de
  FASE-B, que esta bloqueado por P1 y por la decision de credenciales/presupuesto.
- **Leida de la combinacion que el gap sugiere y que NO se aplic**: `(a) para el trio pedido/efectivo +
  `elapsed_ms`, y `(b) para `attempts`/`error_kind` cuando abra FASE-B`. Esa particion es la nica que deja los
  seis campos con un productor que realmente los observa, pero toca dos archivos y por eso es decision del operador con mandato, no una cura de esta sesion.

Lo prohibido que se respet: ninguna segunda costura, `decision_client.py` no se duplicar, AC1/AC2 del piloto no
se recortaron, y no se escribi codigo de produccion en esta preparacin.
