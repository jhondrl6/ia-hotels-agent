# Registro decision-ready: que significa el eco `deepseek-flash` (Cierre C, SESION 2.5 / FASE-B.1)

Plan: `EVALUACION-JEV-TYPESAFE-2026-09-21`. Sesion: preflight de FASE-C, expediente
`evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/PREFLIGHT-FASE-C-2026-10-04/`. Revision de arranque de esta
sesion: `5ca6395` (paridad con `origin/master` medida contra el servidor, no contra el ref local).

Este archivo **no congela nada** y **no elige** entre las dos salidas del §3. Por V4 la decision del
congelado es del operador y se toma en el paso 3.1 de FASE-C. Lo que entrega es lo que ese paso necesita
para no comprar una afirmacion no medida: MEDIDO y NO MEDIDO separados, cada linea MEDIDO con su corrida,
y las dos salidas legitimas enunciadas.

## 1. MEDIDO

Cada fila lleva su proveniencia citada del expediente de la deuda (`DEUDA-FASE-B-2026-10-04/`) o de este
expediente. Nada de esta seccion es inferencia.

| # | Afirmacion | Como se midio | Proveniencia |
|---|------------|---------------|--------------|
| M-1 | Pidiendo `deepseek-chat`, el servicio firma `model: "deepseek-flash"` en **4 de 4** envios exitosos | Sondas por el brazo (`scripts/proveedores/deepseek.py:evaluar`), cero reintentos, mismo cuerpo | `preflight.json` → `proveedores.deepseek.cierre_2026-10-04` (request_id `3317ed3c-7afa-4a1e-9697-eb4baf3a6c34`, usage 138/36) y `cierre_b_2026-10-04_estabilidad_del_alias.eco_del_pedido_de_casa` (request_ids `31256bbb-b232-4aa8-a2e3-e1290efd35bd`, `180fc230-8367-40f7-8a6a-c08ca73474c8`); crudos `04-deepseek-crudo.json`, `09-deepseek-estabilidad-crudo.json` del expediente de la deuda |
| M-2 | `deepseek-flash` **es direccionable**: HTTP 200 y el servicio se echo a si mismo con ese nombre | Sonda pidiendo el nombre del eco, con tope 254 | `cierre_b_2026-10-04_estabilidad_del_alias.direccionabilidad_de_deepseek_flash`; crudo `10-deepseek-flash-direccionable-crudo.json` |
| M-3 | **No es equivalente**: con ese pedido `content_len = 0`, `finish_reason = length` y los 254 tokens de salida consumidos en `reasoning_tokens`. El control de la misma corrida, mismo cuerpo y mismo tope pidiendo `deepseek-chat`, dio 36 tokens, `finish_reason = stop` y 89 caracteres de content | Par control/efecto en una sola corrida; la forma se repite con tope 64 (200, content vacio, `finish_reason = length`) | `cierre_b_2026-10-04_estabilidad_del_alias.direccionabilidad_de_deepseek_flash` y su `sonda_previa_al_tope_alto`; crudo `10-` |
| M-4 | La causa de `respuestas: []` **no es truncamiento ni transporte**: es el id recortado. El servicio contesto `pregunta_id: "1"` a una pregunta `sonda:1` y `_mapear_respuestas` casaba por id exacto | Reproducido en **3 de 3** envios con content, todos con `finish_reason = stop` y 34-36 tokens de salida (deuda). **Reproducido ademas de forma determinista en esta sesion sobre el blob versionado en `5ca6395`**, cargado con `git show` y sin tocar el arbol: 4 de 4 casos de recorte salen `respuestas: []` y la puerta responde `respuesta-vacia:list` | Deuda: `cierre_b_2026-10-04_estabilidad_del_alias.causa_medida_del_respuestas_vacio`. Esta sesion: `02-antecedente-id-recortado-en-5ca6395.json` (arnes `08a-`) |
| M-5 | Con la cura aplicada, el mismo arnes da **3 de 4 casos VALIDA** (noul, choice y score con id recortado) y el cuarto caso —el recorte ambiguo— sigue rechazado **por diseno**, no por fallo | Arbol de trabajo curado, transporte inyectado, cero red | `03-post-cura-id-recortado-en-el-arbol.json` (arnes `08a-`); bateria `05-post-bateria-brazo-15-tests.txt` = 15 passed, EXIT=0 |
| M-6 | Cada diente nuevo cae por la causa prevista: **seis mutantes**, seis rojos con su kill-set publicado, seis restauraciones con sha igual al baseline `289842457a5b`, y bateria verde (`15 passed`) despues de cada restauracion | Secuencia sobre disco: mutacion → rojo → restauracion por sha → verde, con ancla de ocurrencia unica verificada antes de mutar | `04-mutantes-cierre-a-crudo.json` (arnes `08b-`) |
| M-7 | El saldo del segundo brazo es una superficie **publicada por la API**: `GET https://api.deepseek.com/user/balance` responde 200 con `is_available: true` y `balance_infos` en USD (total 4.94, granted 0.00, topped_up 4.94) | Una (1) llamada autenticada de lectura, cero reintentos, autorizacion A2 del prompt | `07-saldo-crudo.json` (arnes `08c-`); estampado en `preflight.json` → `proveedores.deepseek.cuota_o_saldo` y `cierre_c_2026-10-04_cuota_o_saldo_medido` |

## 2. NO MEDIDO

Lo que este arbol **no** puede responder. Cada linea dice quien la responde.

| # | Pregunta abierta | Por que no esta medida aqui | Quien la responde |
|---|------------------|------------------------------|-------------------|
| N-1 | Si `deepseek-flash` es una **capa de serving/routing** del proveedor o un **alias de producto** | Ninguna de las mediciones de arriba toca la semantica del nombre: midieron que el eco es estable (4/4), que se puede pedir, y que responde distinto. Un nombre que el servicio usa para firmar no es, por si solo, una version fijada ni un producto anunciado | La documentacion del proveedor o una pregunta con duena al proveedor. **No este arbol** (V4) |
| N-2 | Si la etiqueta del eco cambia entre regiones, cuentas o momentos | n = 1 por nombre y una sola cuenta. Lo medido es estable **dentro de la muestra de la tanda**, no como propiedad del servicio | El proveedor, o una corrida con dos cuentas (no autorizada aqui) |
| N-3 | Si la cura del id recortado se sostiene con **trafico real** | Comprobarlo pidiendo `sonda:1` otra vez es un **segundo envio de chat**, y V5 lo niega (tope A2, ya gastado en la lectura de saldo). La cura esta medida con transporte inyectado y el defecto esta reproducido sobre el blob versionado; la confirmacion por red queda pendiente | FASE-C, en su corrida de comparacion real, con su propia autorizacion de envios |
| N-4 | Que **capa del proveedor** recorta el prefijo (¿el modelo, el parser del servicio, o la instructiva?) | El brazo manda los ids en el texto de la instructiva y el servicio devolvio la cola. No se midio que pasa con una instructiva que exija el id literal: pedia otro envio | El paso que decida tocar `_instrucciones` (la otra duena que nombraba la `duena_sugerida`), con mandato propio |
| N-5 | Si `4.94 USD` es el saldo **correcto** | La lectura es lo que publico el servicio por `GET /user/balance`; no hay segunda fuente (consola) con la que casarlo. La via se tomo de un espejo de documentacion porque el sitio oficial no resuelve desde esta maquina (medido: `curl` HTTP=000) | El operador en la consola del proveedor, si quiere una validacion cruzada del numero |

## 3. Las dos salidas legitimas del congelado (paso 3.1 de FASE-C; las elige el operador)

- **(a) Preguntar al proveedor y estampar**: el operador pregunta que es `deepseek-flash`, y el resultado
  se estampa con fuente y fecha. Con (a) el comparador puede afirmar reproduccibilidad del nombre pedido.
  Coste: una espera externa antes de congelar.
- **(b) Congelar con el caveat escrito**: se congela declarando «comparador = `deepseek-chat`; el servicio
  firma `deepseek-flash`; no se afirma que representa» y la comparacion carga ese caveat. Con (b) la tabla
  comparativa de C reporta el nombre pedido y el eco observado como cuerdas distintas — que es lo que ya
  hace el brazo, que publica `crudo.model` y declara `alias_movil: true`.

No vale congelar sin decirlo. Esta sesion no congelo nada: `protocolo.json` sigue BORRADOR y
`muestra.json` sigue CONGELADA con su muestra de 2026-10-01 (D4 y V2), y ninguna de las dos se toco aqui.

## 4. Consumo de red de la sesion (declarado)

- DeepSeek: **1 envio** (`GET /user/balance`, HTTP 200, cero reintentos). Cero envios de `chat/completions`
  en esta sesion: el tope de A2 es una llamada y se gasto en la lectura de saldo, que es lo que cerraba el
  cuarto estado de AC12.
- Pruebas del mapper y de la cura: con **cero red** (transporte inyectado y el guard `RedProhibida` del
  `conftest.py` de la seleccion, que es lo que hace afirmable el cero envios).
- Documentacion de la via de saldo: dos intentos de fetch al sitio oficial (`api-docs.deepseek.com`), ambos
  sin resolucion desde esta maquina (HTTP=000 medido con `curl`), y un fetch exitoso a un espejo de terceros
  (`raw.githubusercontent.com`, HTTP 200) del que se transcribio la via. Ninguno de los tres es un envio
  autenticado contra el proveedor.

## 5. Lo que este registro deja dicho para la apertura de FASE-C

El preflight del brazo DeepSeek tiene sus cuatro estados de AC12 completos (M-7 cierra el ultimo; el
antecedente esta en `preflight.json`). La condicion de entrada que se levanta es la del brazo roto: M-4
describia un comparador que podia devolver `respuestas: []` con el envio cobrado, y correr C sobre ese brazo
habria producido un `margen_vs_deepseek` que se leeria como resultado del comparador y no del instrumento.
Eso ya no es asi en el arbol (M-5, M-6), con la reserva declarada en N-3: la confirmacion con trafico real
llega con la corrida de C.
