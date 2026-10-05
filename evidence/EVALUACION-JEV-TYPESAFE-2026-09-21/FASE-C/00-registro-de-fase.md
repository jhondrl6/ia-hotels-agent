# 00 · Registro de fase — FASE-C «Comparación decidible» (EVALUACION-JEV-TYPESAFE-2026-09-21)

Sesión ejecutora del pre-registro, 2026-10-04. Mandato: la pegada de FASE-C.
Estado terminal declarado en §8: **INCOMPLETO**, `decision = null`, con cuatro cambios requeridos.

Cada cifra lleva el comando que la imprime. Ningún número de este archivo nace de lógica nueva sin
test (AC10): los que no salen de un instrumento testado salen del ledger crudo y están etiquetados
como lectura, no como métrica.

---

## 0. Arranque (§0 del mandato)

| Dato | Valor | Comando |
|---|---|---|
| HEAD local | `d3ab12a` | `git rev-parse --short HEAD` |
| Árbol | limpio (sin modificaciones previas de esta sesión) | `git status --porcelain` |
| `refs/heads/master` en el servidor | `d3ab12a70f5ee81a459706a33d98ae4ea20a6914` | `git ls-remote origin refs/heads/master` |
| Paridad | `0 / 0` (izquierda/derecha) | `git rev-list --left-right --count origin/master...HEAD` |

El HEAD coincide con el estado anclado del prompt: **el disco no desmintió al mandato al arrancar.**

### Vintage de los insumos, medido al arrancar

```
0107a386ae5750cdc0e89d75d51b4745415f450ebd3802973d390bfb358e42eb  muestra.json
4ffbb120ef94b982cdcdf0f2c8ae4470eaf6ff58ad8eb2f5502f2cd87bb29338  etiquetas.json
4a351582a96b451ed1ca19b3bf5086059de726b9d384dc54a25b4388e472e6c3  protocolo.json   (BORRADOR)
```

Comando: `cd evidence/EVALUACION-JEV-TYPESAFE-2026-09-21 && sha256sum muestra.json etiquetas.json protocolo.json`

Condiciones duras de entrada: **las tres casaron.**

- `muestra.json` `status: CONGELADA`, `review: {human_reviewed: true, reviewer: jhon, reviewed_at:
  2026-10-02}`, `counts: {total 4, dev 2, eval 2, excluidos 1}`.
- `etiquetas.json` `review_status: revisada`, 4 filas firmadas las cuatro por `jhon` el 2026-10-02.
- `protocolo.json` en `BORRADOR` con `tokens_in 1834`, `tokens_out 139`, `usd null`, `llamadas 12`,
  `timeout_s 30`, `max_retries 0`.

Intérprete de las baterías: `venv/Scripts/python.exe`. El rojo de intérprete ya registrado
(`test_jev_pilot_sdk_ac9.py`, `assert 14 > 14` con el `python` global) no se volvió a producir ni se
reportó como rojo de código.

### Línea base PRE, tomada antes de tocar nada

| Instrumento | PRE | Crudo |
|---|---|---|
| `run_all_validations.py --quick` | **13/13, EXIT 0** | `16-quick-gate-pre.txt` |
| `pytest tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py` | **24 passed, EXIT 0** | `03-bateria-protocolo-pre-congelado.txt` |
| `protocolo-check` sobre el BORRADOR | **OK, EXIT 0**, `k 8`, umbrales 8, `nulos [limites_gasto.usd]`, hallazgos `[]` | `01-protocolo-check-pre-borrador.txt` |
| `validate_wiring.py --check` | (se midió después: el rojo que produjo fue de este expediente, ver §5) | `17-...` |

---

## 1. Orden de la fase y por qué ese orden

El maestro exige: conectividad y ajuste solo en dev → congelar prompt y umbrales → **después** abrir
eval. 3.2 alimenta a 3.1, y el congelado precede a 3.4. Se respetó literalmente:

1. §3.2 techos resueltos **por antecedente citado** (sin enviar nada) →
2. §3.1 `protocolo.json` CONGELADA + gate `protocolo-check` EXIT 0 + hash nuevo →
3. §3.3 `usd` null, fuera de gobernanza, re-estampado en el congelado →
4. **recién entonces** se calculó la capa fría sobre `eval` y se abrieron los pares de eval.

Nada de eval se miró antes del congelado, ni siquiera la capa fría (que es determinista y gratis):
`leccion_target_en_candidatos` sobre los pares de eval es un resultado, y se computó después del hash.

---

## 2. §3.1 · El congelado

Edición a `evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json`, y nada más que esa edición:

- `"status": "BORRADOR"` → `"CONGELADA"`
- objeto nuevo: `"congelado": {"revisado_por": "jhon", "fecha": "2026-10-04"}`

La fecha es la real de la sesión medida al arrancar (`date -u` → `2026-10-04T23:43:16Z`; local
`2026-10-04T18:43:16-0500`). La autorización la constituye la pegada; su decisión operatoria de
referencia vive en `PREPARACION-DECISION-2026-10-02/` y no se duplicó aquí.

| Forma | sha256 / sha1 |
|---|---|
| disco (CRLF, 3790 B, CR 50 / LF 50) | `140577a06b2315b5e67a5af9da889347455088270885a9f4f1c5db0f6bae277d` |
| contenido normalizado a LF (3740 B) | `7caed9dc959c113569145ff3b082d8c817de7ae3238e90398a26eceb94df0728` |
| `git hash-object` (con filtro de clean) | `8758e8b20364e097ad36d39e065a63ac368214f9` |
| `git hash-object --no-filters` | `e0ea350adbdfa5573d3d18102b12f784b1ce84fd` |

Las cuatro formas se publican a propósito: el clon tiene `core.autocrlf` activo y el disco CRLF nunca
casa con el blob LF. Comando: `sha256sum protocolo.json`, `git hash-object <ruta>`,
`git hash-object --no-filters <ruta>` y el contraste de bytes/CR/LF con
`venv/Scripts/python.exe -c "b=open(...,'rb').read(); print(len(b), b.count(b'\r'), b.count(b'\n'))"`.

El archivo pasó de 11 a 12 claves de primer nivel y de 46 a 50 líneas: +4 líneas, ninguna otra forma
tocada (no hay re-codificación, el BOM sigue ausente y el UTF-8 se conserva).

**Gate mecánico: `protocolo-check` EXIT 0** sobre la forma congelada
(`02-protocolo-check-post-congelada.txt`): `check_status OK`, `protocolo_status CONGELADA`, `k 8`,
`umbrales_gobernados 8`, `nulos ["limites_gasto.usd"]`, `hallazgos []`.

```
venv/Scripts/python.exe scripts/evaluate_jev_pilot.py protocolo-check --protocolo evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json
```

Cualquier edición posterior de estos umbrales es **otro protocolo**, no este.

### El rojo que el congelado estaba anunciado a producir

`tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py:43` pasó de verde a rojo:

```
>       assert resultado["protocolo_status"] == "BORRADOR", (
            "el congelado del protocolo es FASE-C: si alguien lo congelo aqui, esto es el aviso")
E       AssertionError: el congelado del protocolo es FASE-C: si alguien lo congelo aqui, esto es el aviso
E       assert 'CONGELADA' == 'BORRADOR'
```

**24 passed → 1 failed, 23 passed**, un solo fallo y es este. No es regresión ni ruido: es la aserción
que la propia tanda del 2026-10-03 escribió para avisar de este acto. Se deja roja y se registra como
**CR-4**; esta fase tiene prohibido editar `tests/` (§5), y re-bajar la aserción sería exactamente lo
que el mandato veda. La batería completa de las familias tocadas cerró en **357 passed, 1 failed**
(`18-baterias-piloto-post.txt`), o sea ningún rojo colateral: ni el escaneo de aislamiento AC6, ni las
huellas S12 del hermano, ni el guard de aditividad.

---

## 3. §3.2 · Techos: citados, no medidos de nuevo

El mecanismo real está leído en el código (`scripts/evaluate_jev_pilot.py:271-299`):
`reservar_presupuesto` goberna **llamadas, reintentos y timeout**, y no compara tokens contra el techo.
El techo es la máxima observación estampada, no un veto. Por eso:

- **No se repitió el corredor dev.** Cada envío cuenta, y el mandato hace preferente citar el
  antecedente.
- Antecedente citado: `tokens_in 1834` / `tokens_out 139`, máximos observados por llamada en las 2
  llamadas del corredor k=8 del split dev del 2026-10-03
  (`venv/Scripts/python.exe temp/ola2-2026-10-03/correr_k8.py`, crudo transcrito en
  `FASE-B/corrida_k8_2026-10-03.txt`, y su comando ya vive dentro de `limites_gasto.motivo`).
- **No se subió ningún techo**: no hay instrucción literal del operador en esta pegada que lo mande, y
  la acopladura del instrumento lo recuerda — `test_jev_pilot_protocolo_check.py:51` exige que la
  cifra del techo y el comando que la midió viajen juntos en el `motivo`, o sea subir el número sin
  el comando cae rojo por si solo.

El techo **sí fue vencido por la observación en `tokens_out`**, y eso se publica como hallazgo H3, no
como edición: ver §6.

---

## 4. §3.3 · `usd`

Sigue `null`, **fuera de gobernanza**, con la declaración del operador del 2026-10-03 escrita en
`limites_gasto.motivo` — que es la condición que el guard `usd-sin-declaracion` exige
(`scripts/evaluate_jev_pilot.py:557-560`). `cost_calculated` y `cost_billed` van null con ese mismo
motivo en `informe_comparativa.json`. El presupuesto de la etapa se gobernó en **llamadas 12** y
**timeout 30 s**.

**Proveniencia de la cuenta de arranque** (declarada, no inferida): `consumo.json` de FASE-C arrancó
en ceros porque la cuenta es por `--out-dir`, o sea por etapa. Los envíos previos que agotaron saldo no
están en esta cuenta y sí en el registro: corredor dev **2 envíos Jev** del 2026-10-03 y sondas de la
deuda **6 envíos DeepSeek** del 2026-10-04 (de esos 6, los **4** que pidieron `deepseek-chat` echaron
`deepseek-flash`). Nada se re-infiere del estado de una cuenta: el saldo de DeepSeek (USD 4.94) y el de
Typesafe (USD 10.00 declarado por consola) se citaron en `preflight.json` como antecedentes con su
archivo, y **no se volvieron a consultar**.

---

## 5. Escritos, y lo que hubo que re-publicar

`git status --porcelain` al cierre:

```
 M evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/protocolo.json
?? evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C/
```

Además de esos dos caminos solo se tocó **un derivado**: `.opencode/wiring_report.json`, forzado por
§7 («re-publicando el derivado si tu expediente lo vence, sin rebajar aserciones»). El mecanismo:
copiar los 6 arneses `.py` al expediente movió la población que el escáner AST cuenta por rol.

```
[FAIL] Derivado: .opencode/wiring_report.json DIVERGE del calculo en memoria (digest 5552bc06da9e)
  - cobertura.archivos_excluidos_por_rol_versionado: publicado 134 | fresco 140
  - exclusiones_por_rol.evidence.cantidad_versionada: publicado 122 | fresco 128
```

EXIT 3 (que según la regla de la casa no es un rojo de cableado: es el derivado vencido). Se
re-publicó con `venv/Scripts/python.exe scripts/validate_wiring.py --write-report` y el diff completo
del artefacto es de **5 líneas**, todas explicadas por este expediente:

```
-    "archivos_excluidos_por_rol": 8478,                      +    "archivos_excluidos_por_rol": 8492,
-    "archivos_excluidos_por_rol_versionado": 134,             +    "archivos_excluidos_por_rol_versionado": 140,
-      "cantidad_versionada": 122,   (evidence)                +      "cantidad_versionada": 128,
-  "generado": "2026-10-04T21:49:08+00:00", "git_sha": "5ca6395"
+  "generado": "2026-10-05T00:03:48+00:00", "git_sha": "d3ab12a"
```

128 − 122 = 6, exactamente los 6 arneses `.py` de FASE-C. Después del `--write-report`:
`validate_wiring.py --check` **EXIT 0** («derivado conforme con el calculo en memoria»). sha256 del
report: `081d08c3…969a8b` antes → `ad81323e…55501e25` después. Ninguna aserción fue rebajada.

**Lo que NO se tocó:** `scripts/`, `modules/`, `tests/`, `requirements.txt` (en particular
`modules/providers/llm_provider.py`), `muestra.json`, `etiquetas.json`, el hermano
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/`, ningún plan archivado, ninguna configuración
central, Anthropic (sigue excluido) y QMind (sin write-back). Los arneses de medición viven en
`temp/fasec-2026-10-04/` y se copiaron al expediente como evidencia (`10-…` a `15-…`), que es lo que
autoriza §5; solo llaman a instrumentos existentes.

**Dos vetos que el mandato deja vencidos y no se corrigieron**: ~25 frases del repositorio afirman hoy
«`protocolo.json` sigue BORRADOR» (p. ej. `docs/cobertura-historia.md:65`,
`PREFLIGHT-FASE-C-2026-10-04/00-resumen.md:253`, `FASE-B/contract.txt:72`) y
`evidence/VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20/RE-VERIFICACION-VCF-JEV-2026-09-28/12-jev-ac3-muestra.txt:25`
censaba 11 claves de primer nivel en el protocolo, ahora son 12. Todas son **notas selladas de rondas
anteriores o del hermano protegido**: la regla de la casa dice que el cierre verifica y no re-registra,
y §2 prohíbe tocar al hermano. Se declaran aquí, con su ruta, y no se editaron.

---

## 6. §3.4 · La corrida: tres brazos, mismo conjunto elegible, split eval, k=8

### Cuenta de envíos (moneda 1 de 3: `usage_observed`)

| Concepto | Valor | Prueba |
|---|---|---|
| Envíos de inferencia autorizados y hechos | **4** = 2 pares × (Jev + DeepSeek) | `ledger.jsonl` (2) + `ledger-deepseek.jsonl` (2) |
| Envíos de conectividad | **0** | `preflight.json:envio_de_conectividad_de_la_sesion` |
| Capa fría | **0** (no llama proveedores) | `05-capa-fria-crudo.json` |
| Llamadas de la etapa | **4 de 12** | `consumo.json` (2, lo escribe el runner) + `registro_deepseek.json:cuenta_al_salir` (4) |
| `attempts` por fila | **1, 1, 1, 1** | columnas `attempts` de ambos ledgers |
| Reintentos ocultos | **0** | `max_retries 0` congelado; `reservar_presupuesto` niega cualquier otro valor |

### Modelo pedido vs devuelto (AC4)

| Brazo | pedido | devuelto por el servicio | request_id |
|---|---|---|---|
| Jev · D-AJUST.1 | `jev-1.13.0` | `null` (no hubo respuesta) | `null` |
| Jev · D-AJUST.4 | `jev-1.13.0` | `jev-1.13.0` | `req_01a10952459e7afa89006e00420e36a8` |
| DeepSeek · D-AJUST.1 | `deepseek-chat` | `deepseek-flash` | `fe14a140-7a64-4b56-9509-beacded8ab16` |
| DeepSeek · D-AJUST.4 | `deepseek-chat` | `deepseek-flash` | `f8a93413-e09c-47d3-a423-6cbd7cbfbac9` |

El eco `deepseek-flash` se publica como modelo efectivo y **no se cambió lo pedido** (D7).
`alias_movil: true` en las dos filas: impide presentar el comparador como versión fijada.

### Usage y techos (H3)

| Brazo · par | tokens_in | tokens_out | duración ms | estado |
|---|---|---|---|---|
| Jev · D-AJUST.1 | `null` | `null` | 48.478 | `no_intentada` — **FALLO** |
| Jev · D-AJUST.4 | 1778 | 145 | 395.794 | observado |
| DS · D-AJUST.1 | 1054 | 149 | 1392.648 | observado |
| DS · D-AJUST.4 | 932 | 158 | 1133.547 | observado |

- `tokens_in` máximo de la etapa **1778 < 1834** → el techo de entrada **no** fue vencido.
- `tokens_out` máximo de la etapa **158 > 139** → **H3: el techo congelado de salida fue vencido por la
  observación en la misma etapa en que se congeló** (145 por Jev, 158 por DeepSeek). Se publica como
  hallazgo y **NO se sube**: subirlo después de abrir eval sería protocolo nuevo (§3.2).
- La falla por conexión **no liberó la reserva como cero**: `usage_normalized.estado`
  `no_intentada`, `libera_reserva_como_cero: false`, y la cuenta sumó la llamada igual que suma
  cualquier intento (`run` lo hace en `:672-673`; aquí es lectura del ledger, no conteo propio).

### El fallo operativo, y por qué no se reintentó

```
{"pair_id": "REFACTOR-WHATSAPP-ENTREGA-2026-09-18::D-AJUST.1", "attempts": 1, "estado": "FALLO",
 "error_kind": "conexion", "clase": "TypeSafeAPIConnectionError", "duracion_ms": 48.478,
 "request_id": null, "usage_normalized": {"estado": "no_intentada", "libera_reserva_como_cero": false}}
```

`48 ms` es un fallo de transporte local, no una respuesta negativa: el antecedente de FASE-B ya midió
que esta máquina sale por proxy de sistema y que el DNS local no resuelve
(`FASE-B/preflight.json:transporte_salida`), o sea un tropiezo de ese tipo deja exactamente esta firma.
La llamada **no se repitió por cuenta propia**: §5 lo prohíbe, y §3.4 autoriza 4 envíos de inferencia,
no 5. Por AC12 la indisponibilidad **detiene o aplaza y no elimina el brazo**: la comparación queda
incompleta y declarada (H4), no se corrió «con dos» presentándola como completa.

### Capa fría: identidad con el antecedente, antes de confiar en ella

El arnés `10-arnes-capa-fria.py` solo llama a `recuperacion_fria` del instrumento versionado. Antes de
usarla sobre eval se verificó que reproduce el split dev del antecedente:

```
IDENTICO  VERIFICADOR-CONTEXTO-DE-FASE-2026-09-20::D-AJUST.2   | n=8
IDENTICO  VERIFICADOR-ESCRITURA-QMIND-2026-09-20::D-NC2        | n=8
CONTRASTE DEV: IDENTIDAD TOTAL
```

Las dos listas de 8 candidatos casan elemento por elemento con `candidatos_frios` del ledger transcrito
en `FASE-B/corrida_k8_2026-10-03.txt:32-33`. Población del índice: **340 lecciones**. Comando:
`venv/Scripts/python.exe temp/fasec-2026-10-04/capa_fria.py` + el contraste contra el crudo antecedente.

Sobre eval, la capa fría es la que decidió la fase:

| par | etiqueta · importancia | ¿target en los 8? |
|---|---|---|
| `REFACTOR-WHATSAPP-ENTREGA-2026-09-18::D-AJUST.1` | pertinente · **alta** | **NO** — sus 8: `D-V.3, DA-F1, L-NC8, L-P5.3, S-I1, D-T4B-A1, DA-G1, DA-G3` |
| `EVALUACION-JEV-TYPESAFE-2026-09-21::D-AJUST.4` | pertinente · media | SÍ, puesto 2 |

### Camino DeepSeek: primer ejercicio real del emparejado

La cura del id recortado del 2026-10-04 no se había vuelto a probar con tráfico (V5 negó el segundo
envío), así que el primer envío de eval era el primer ejercicio real de `_emparejar_respuestas`. **No se
rompió**: los dos servicios devolvieron el id completo `REFACTOR-…::D-AJUST.1` y
`EVALUACION-…::D-AJUST.4`, o sea casó por coincidencia exacta y la rama del recorte no intervino. Se
verificó además **sin gastar un envío**, con `_payload` inyectado (`13-arnes-ensayo-sin-red-deepseek.py`
→ `08-ensayo-sin-red-deepseek.json`): la proyección de `preguntas_para_par` al tipo `Pregunta` de la
puerta es aceptada por `validar_payload` y `a_respuestas_tipadas` cuando el payload del servicio es
correcto, y rechaza cuando no. Ese ensayo detectó dos rechazos que eran de mi payload falso y no de la
proyección (`eleccion no está entre las opciones` y `las probabilidades suman 0.7200, no 1`), y por eso
valió la pena: el primer envío real no se gastó en un defecto de armadura.

### El rojo operativo que sí apareció, y su causa exacta

Por la vía de CLI, el brazo Jev murió antes de enviar nada:

```
typesafe_sdk._core.errors.TypeSafeError: No API key was provided. Pass api_key or set the TYPESAFE_API_KEY environment variable.
```

en `decision_client.py:1344 → cliente_jev`, con `evaluate_jev_pilot.py:630` en la pila. Causa: `main()`
nunca carga `.env` y `run()` no propaga `etiquetas` (no existe la bandera `--etiquetas`), o sea por CLI
la corrida no autentica y, si autenticara, `run_resumen.json` saldría con `recuperacion: null`. **Cero
envíos y cero artefactos escritos en ese intento** (se comprobó: `ls FASE-C/` solo tenía
`preflight.json`). No se parcheó el código: se resolvió por la misma vía que usó el corredor
antecedente de FASE-B, un arnés in-process que carga `TYPESAFE_API_KEY` de `.env` por nombre y llama a
`run()` sin tocarlo (`11-arnes-correr-jev-eval.py`), y se registró como **CR-3**.

---

## 7. Los cuatro cocientes (lo que §1 pide) y los huecos

Publicados por brazo en `informe_comparativa.json`, con numerador y denominador separados, sobre el
mismo conjunto elegible, en eval, bajo el protocolo congelado:

| Brazo | recuperación | precisión entre propuestas | recall importante en candidatos | extremo a extremo |
|---|---|---|---|---|
| capa fría | **1/2 = 0.5** | n/a (no elige) | **NO ESTIMADO** | **NO ESTIMADO** |
| DeepSeek | **1/2 = 0.5** | **NO ESTIMADO** | **NO ESTIMADO** | **NO ESTIMADO** |
| Jev | **1/2 = 0.5** | **NO ESTIMADO** | **NO ESTIMADO** | **NO ESTIMADO** |

- La recuperación la imprime `recuperacion_medida` (`:700`), función testada. En el brazo Jev la imprimió
  el propio runner dentro de `run_resumen.json`; para las otras dos filas se le pasó su ledger persistido.
- **H1: los tres brazos dan el mismo número por construcción**, porque la recuperación mide la capa
  fría y la capa fría es común. La métrica que sí se midió no puede decidir entre brazos.
- **NO ESTIMADO** es literal: `{"value": null, "numerator": null, "denominator": null, "motivo":
  "instrumento_no_implementado"}`. No se rellenó a mano (AC10). Prueba de la ausencia, medida:
  `grep -rn "prec_num\|rec_num" scripts/ tests/` → el instrumento solo los **lee**
  (`evaluate_jev_pilot.py:191-192`) y el único sitio que los alimenta es un fixture
  (`test_jev_pilot_offline.py:113-115`). `metrics()` no tiene ningún productor en `scripts/`.
- Emisión mecánica tampoco hay: `decide` → **EXIT 2** con el mensaje de `_refuse`
  (`evaluate_jev_pilot.py:828`); `report` ni siquiera está en el parser — los modos medidos son
  `prepare, check, run, protocolo-check, decide`, y correr `report` da **EXIT 2** de argparse
  (medido **sin tubería**, porque con `| tail` el `$?` que se lee es el de `tail`: daba 0 falso).
  Crudo: `09-negacion-de-report-y-decide.txt`. → **CR-1 y CR-2**.
- Abstenciones en su denominador aparte, como lectura del registro y no como score: Jev 1 con elección /
  0 abstenciones / **1 sin elección por fallo**; DeepSeek 2 con elección / **1 abstención**
  (`ninguna-aplica` en `D-AJUST.1`, p 0.50, conf 0.55) / 0 fallos. La única abstención de la corrida es
  la respuesta correcta para un candidato set donde el target no estaba.

**H2** y **H6** son las dos colisiones que §3.5 manda publicar en vez de resolver re-leyendo el
criterio:

- **H2**: el par de importancia **ALTA** no tiene su lección entre los 8 candidatos, o sea
  `cobertura_min 0.95` no se alcanza con `0.5`. Ninguna elección de modelo puede arreglarlo.
- **H6**: `margen_vs_deepseek 0.25` sobre un denominador de eval de 2 resuelve en pasos de 0.5:
  cualquier diferencia no nula pasa el umbral y la única alternativa es 0.0. La nota congelada razonaba
  ese margen contra el denominador **4** de la muestra completa, no contra el **2** de eval.

---

## 8. §3.5 / §3.6 · Decisión, AC6 y AC7

**AC6** (`15-arnes-aditividad-ac6.py` → `aditividad.json`), sobre el guard real
`scripts/triage_lesson_relevance.py:guardar_filas_ancladas`, con las respuestas persistidas de esta
corrida y **cero inferencias nuevas** (no se llamó a `triar` ni a `construir_informe`, que sí enviarían):

```
anchored_before 25 · anchored_after 25 · removed [] · intentos_filtrados [25 ids] · orden_preservado true · duplicadas_en_el_regreso []
```

No es verde por vacío: el filtro habría vaciado §2 (las 25 filas estaban en `cuestionadas`) y el guard
las devolvió intactas. Se declara además lo que **no** afirma: los ids que esta corrida eligió
(`D-AJUST.4`, `ninguna-aplica`) no nombran ninguna de las 25 filas ancladas del hermano, así que la
intersección es vacía por construcción y `removed []` prueba la aditividad del guard, no la pertinencia
de esas 25 filas. `GUARD_ADITIVIDAD_ACTIVO is True` antes de medir.

**§3.5 decisión: `null`.** Literales aplicados tal cual están congelados:

| Literal | Estado | Base |
|---|---|---|
| ACTIVAR | **excluido por medición** | `cobertura_min` 0.95 vs `0.5` medido con el instrumento testado |
| RECHAZAR | **no lo emite esta sesión** | gobernaría el margen extremo_a_extremo, que es NO-EVALUABLE, y la pata Jev tuvo un fallo operativo; un fallo operativo nunca es RECHAZAR |
| MUESTRA-INSUFICIENTE | **ponible por el operador, con base** | `suficiencia_minima` 0.5 **se cumple** (2 de 4 pertinentes), pero el denominador efectivo de la comparación es **1 par** y no discrimina el margen |
| COSTE-NO-PAGADO | **bloqueado** | `usd` null, fuera de gobernanza |

**AC7, tres campos separados** (`decision.json`, `decision.md`):

- `jev_recommendation` = **NO ADOPTAR; MANTENER COMO BRAZO MEDIBLE**. Donde la red respondió, el brazo
  funcionó de punta a punta; acertó en el único par utilizable; 1 de 2 envíos perdido por transporte.
  Un par no es base de calidad, y la recomendación no cambia ningún default ni cierra ninguna deuda.
- `d6_eligibility` = **NO ELEGIBLE en esta fase**. Su disparador es pertinencia aceptable + candidatos
  nuevos, **no** que gane Jev. Pertinencia: NO CUMPLE (0.5 < 0.95). Candidatos nuevos: CUMPLE — **9**
  medidos con `candidatos_de_pertinencia` del triaje versionado sobre índice `FRESCO`, sin red:
  `D-B, D-D, DA-C3, L-D5, L-ENT.9, L-P6.3, L-SR3, L-SR4, L-T2B.1`.
- `transfer_status` = **PENDIENTE**. Sin instrucción literal que nombre archivos y alcance, la deuda del
  hermano no se mueve; ningún documento hermano fue editado.

**Tres monedas separadas**: `usage_observed` publicado por llamada con su `usage_raw` en el ledger;
`cost_calculated` null; `cost_billed` null; motivo `usd` fuera de gobernanza. Latencias y reintentos
arriba. El modo auto del wrapper no se usó ni como fuente de usage.

---

## 9. Tabla de cierre: cada fila del DoD con su comando y su valor medido

| # | Afirmación del §7 | Comando que la imprime | Valor medido |
|---|---|---|---|
| 1 | protocolo CONGELADA con dueño y fecha, `protocolo-check` EXIT 0, hash citado; techos re-anclados o antecedente citado **antes** del congelado | `venv/Scripts/python.exe scripts/evaluate_jev_pilot.py protocolo-check --protocolo evidence/…/protocolo.json` | `status CONGELADA`, `congelado {jhon, 2026-10-04}`, **EXIT 0**, sha disco `140577a0…277d` / LF `7caed9dc…0728`; techos por antecedente (1834/139), subidos **no** |
| 2 | `muestra.json` / `etiquetas.json` intactos al cierre | `sha256sum` al arrancar y al cerrar | muestra `0107a386…8e42eb` = igual; etiquetas `4ffbb120…bb29338` = igual; protocolo `4a351582…472e6c3` → `140577a0…277d` (el único cambio, y es el mandato 3.1) |
| 3 | Tres brazos sobre el mismo conjunto elegible (eval, k=8), ledger por llamada, pedido/devuelto publicado, `reservar_presupuesto` antes de cada envío, cuenta por etapa con proveniencia | `cat evidence/…/FASE-C/ledger*.jsonl`, `registro_deepseek.json:reserva_previa` | 2+2+0 envíos, k=8, 4 filas de ledger, `reservado true` con `llamadas_restantes 10` y `9` antes de cada envío DeepSeek, cuenta 4/12, modelos pedidos y devueltos en la tabla §6 |
| 4 | `respuestas.jsonl` e `informe_comparativa.json` regenerables sin red — **o** ausencia declarada con cambio requerido y **cero números a mano** | `venv/Scripts/python.exe temp/fasec-2026-10-04/proyectar_comparativa.py` | 6 filas y los 4 cocientes por brazo; 1 cociente medido con instrumento testado, 3 en null con `motivo: instrumento_no_implementado` y CR-1/CR-2 registrados; **0 números a mano** |
| 5 | AC6 `removed: []` sobre el guard real, con las respuestas de esta corrida, sin nuevas inferencias | `venv/Scripts/python.exe temp/fasec-2026-10-04/correr_aditividad_ac6.py` | `anchored_before 25`, `anchored_after 25`, `removed []`, `intentos_filtrados` 25, `orden_preservado true`, `duplicadas []` |
| 6 | AC5 literales: fallo operativo = FALLIDO + null; denominador cero = NO-EVALUABLE; COSTE-NO-PAGADO solo con `usd` en gobernanza; MUESTRA-INSUFICIENTE con base | `cat decision.json` | `run_status INCOMPLETO`, `decision null`; margen **NO-EVALUABLE** (no 0.0); COSTE-NO-PAGADO **bloqueado**; MUESTRA-INSUFICIENTE **ponible** con su base; el fallo de Jev **no** se convirtió en RECHAZAR |
| 7 | AC7 `jev_recommendation` y `d6_eligibility` separados; `transfer_status` PENDIENTE | `cat decision.json` | los tres campos presentes, separados, D6 evaluado por su propio disparador |
| 8 | Tres monedas separadas; abstenciones en denominador aparte; latencia y reintentos publicados | `informe_comparativa.json` | `usage_observed` por llamada; `cost_calculated` null; `cost_billed` null; abstenciones aparte; latencias 48.478 / 395.794 / 1392.648 / 1133.547 ms; `attempts` 1 en las 4 filas |
| 9 | Escrituras solo en su ruta; hermano y producción intactos; `--quick` y `--check` en verde re-publicando el derivado sin rebajar aserciones | `git status --porcelain`; `venv/Scripts/python.exe scripts/run_all_validations.py --quick`; `… validate_wiring.py --check` | `M protocolo.json` + `?? FASE-C/` + el derivado `.opencode/wiring_report.json` (diff de 5 líneas, todas atribuibles a los 6 arneses); quick **13/13 EXIT 0**; wiring **--check EXIT 0**; hermano sin un byte movido |
| 10 | Cada cifra del registro lleva el comando que la imprime | este archivo | cumplido; los crudos están en `01-…` a `18-…` y los arneses en `10-…` a `15-…` |

### Fila final (§9 del mandato)

Sin commit. Sin push. Sin revisión L3. Sin write-back en QMind. Sin tocar planes hermanos ni deuda
ajena. Sin ofrecer la fase siguiente. Los cinco cortes documentales de esta fase terminan en **espera
de autorización del operador**; el `git commit` es un acto posterior, separado y suyo.

---

## 10. Estado terminal

**`run_status = INCOMPLETO`, `decision = null`**, los registros publicados completos y cuatro cambios
requeridos abiertos: **CR-1** contador de clasificación y extremo a extremo como instrumento testado;
**CR-2** `report` y `decide`; **CR-3** `--etiquetas` y la credencial del SDK en el CLI; **CR-4**
re-anclar `test_jev_pilot_protocolo_check.py:43` al estado CONGELADA.

La condición de cierre no era «los tres brazos corrieron»: era que el operador pueda emitir uno de los
cuatro literales sin interpretar nada de lo que esta sesión produjo. Con `cobertura_min` medido hasta el
fondo, el margen declarado NO-EVALUABLE con su motivo, el coste bloqueado por `usd` null, y la muestra
y el denominador efectivo publicados, **esa emisión le corresponde al operador y no a esta sesión**.
La materia prima queda congelada en los ledgers: CR-1 y CR-2 pueden producir los tres cocientes que
faltan **sin re-abrir la corrida y sin enviar nada**.

---

## 11. Ronda final de verificación, medida DESPUÉS de escribir este registro

Las filas 1-3 de §9 se midieron antes de existir este archivo. Como escribir el expediente también es
mutar el árbol, la ronda se volvió a correr entera sobre el estado final:

| Control | Comando | Valor final | Crudo |
|---|---|---|---|
| Gate rápido | `venv/Scripts/python.exe scripts/run_all_validations.py --quick` | **13/13, EXIT 0** (`[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`) | `20-quick-gate-final.txt` |
| Derivado de cableado | `venv/Scripts/python.exe scripts/validate_wiring.py --check` | **EXIT 0**, «derivado conforme con el calculo en memoria (digest `5552bc06da9e`)», violaciones 0 | `21-wiring-check-final.txt` |
| Batería del protocolo | `venv/Scripts/python.exe -m pytest tests/quality_gates/jev_pilot/test_jev_pilot_protocolo_check.py -q` | **1 failed, 23 passed** — el único rojo es `:43`, el aviso del congelado (CR-4) | `22-bateria-protocolo-final.txt` |
| Escrituras | `git status --porcelain` | 3 entradas y solo esas: ` M .opencode/wiring_report.json`, ` M evidence/…/protocolo.json`, `?? evidence/…/FASE-C/` | arriba |
| Invariantes | `sha256sum evidence/…/{muestra,etiquetas,protocolo}.json` | muestra `0107a386…8e42eb` y etiquetas `4ffbb120…bb29338` **iguales al arrancar**; protocolo `140577a0…277d` = el congelado de §2 | arriba |

El diff del derivado quedó capturado con `git diff --numstat` en `5 5 .opencode/wiring_report.json`
(`17c-wiring-write-report-diff.txt`), o sea las 5 líneas que afirma §5, medidas por el instrumento y no
contadas a ojo.

**Cuentas del expediente**, medidas y no contadas a ojo
(`ls -1 evidence/EVALUACION-JEV-TYPESAFE-2026-09-21/FASE-C | wc -l`): **38 archivos** — 27 numerados
(crudos y arneses, del `00-` al `24-`, más los dos sufijos `17b`/`17c`) y 11 con el nombre que manda §6
(`preflight.json`, `ledger.jsonl`, `run_resumen.json`, `consumo.json`, `registro_deepseek.json`,
`ledger-deepseek.jsonl`, `respuestas.jsonl`, `informe_comparativa.json`, `aditividad.json`,
`decision.json`, `decision.md`). La cifra es posterior a §11: los stamps `23-` y `24-` se escribieron
porque hubo que volver a correr los gates despues de redactar este mismo registro. El unico archivo
fuera de esa ruta que cambio es el derivado que §7 obliga a re-publicar.

**Barrido de credenciales del expediente** (regla de la casa: presencia por nombre, jamas el valor, su
longitud ni un prefijo). Comando:
`grep -rlIE "(sk-[A-Za-z0-9]{8,}|API_KEY[[:space:]]*=[[:space:]]*[A-Za-z0-9]|Bearer [A-Za-z0-9]{10,})" FASE-C/ | wc -l`
→ **0 archivos con patron de valor**. Para las menciones por nombre se publica el censo **excluyendo
este registro**, porque un conteo que incluye el documento que lo estampa se mueve cada vez que se edita
el documento (medido tres veces en esta sesion: 12 → 14 → 12 sin que cambiara nada sustantivo). El
numero estable es **10 menciones en los otros 37 archivos**, todas por nombre de variable, que es la
forma autorizada. Una de esas 10 pide declaracion expresa:

- **`'SENTINELA-NO-REAL-para-el-ensayo'`** en el arnes `13-`: un valor **fabricado a proposito** para el
  ensayo sin red, para que `resolver_proveedor` reportara `presente: true` sin tocar `.env` y sin que
  ninguna credencial real entrara en ese proceso. No es una clave: no tiene la forma de ninguna, nunca
  salio de la maquina y el ensayo no abrio sockets. Se declara aqui en vez de dejarla como un residuo
  que el proximo barrido leeria como un valor.

---

## 12. Sello de cierre

Ultima corrida de verificacion, ya con este registro redactado del todo (`ls -1 FASE-C | wc -l` =
**38**): `--quick` **13/13 EXIT 0**, `validate_wiring.py --check` **EXIT 0**, bateria del protocolo
**1 failed / 23 passed** (el unico rojo es el aviso `:43` = CR-4), `sha256sum` de muestra y etiquetas
**identicos al arranque**, protocolo el del congelado, y `git status --porcelain` con las tres entradas
de §11 y ninguna otra.

Despues de este parrafo la sesion no volvio a escribir: volver a correr los gates despues de cada
parrafo del registro seria perseguir un denominador que mueve el propio texto que lo documenta, y el
mandato pide el verde **al cierre**, no ad infinitum. El sello `23-` y `24-` son los crudos de la
penultima corrida; esta seccion es la ultima.

**Un cambio pendiente de autorizacion, no ejecutado**: `tests/quality_gates/jev_pilot/` queda con ese
rojo por diseño. La decision de commitear, empujar y correr la revision L3 es del operador, y abrir
FASE-RELEASE no se ofrece desde aqui.


