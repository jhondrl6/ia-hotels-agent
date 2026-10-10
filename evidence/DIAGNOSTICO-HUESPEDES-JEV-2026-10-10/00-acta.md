# 00-acta — DIAGNOSTICO-HUESPEDES-JEV-2026-10-10

Sesion unica de diagnostico. No es fase de ningun plan: `CURA-INSTRUMENTOS-QMIND-S15-2026-10-07` y
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20` quedan **cerrados y archivados, sin abrir**. Cero escrituras remotas,
cero ediciones de codigo, de tests, de `AGENTS.md`, `.cursorrules`, `VERSION.yaml` o documentos de planes
archivados. Citas por SIMBOLO (R2.2), nunca por numero de linea.

---

## 1. Estado re-medido al abrir (no citado)

| Concepto | Medido en esta sesion |
|----------|-----------------------|
| HEAD / rama | `4d35a42` / `master` |
| Paridad | `0 0` contra `origin/master`; tip remoto leido por `git ls-remote origin refs/heads/master` = `4d35a42091c3938da2c771addbf6241c71a880e2` |
| Tag | ninguno |
| Arbol | `git status -uall --porcelain=v1` = **13 rutas**, todas `A ` (staged) y **AJENAS**: 12 bajo `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/briefing/` (FASE-0, A, B, C, D, E, E2E, F, G, H, RELEASE, VERIFY) y 1 bajo `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/FASE-E2E/captura_stdout.txt`. Deuda S-CIM-7: no tocadas, no des-staged |
| Quick | `PYTHONUTF8=1 python scripts/run_all_validations.py --quick` → 13 etiquetas, `STATUS: ALL VALIDATIONS PASSED`, `[GUARDA] las 13 etiquetas impresas casan con el TOTAL dinamico`, **EXIT=0** (crudo `02-quick_pre.txt`) |
| Seleccion literal | `PYTHONUTF8=1 python -m pytest tests/test_validate_qmind_writeback_escritura.py tests/test_build_lesson_index_s15_fecha_versionada.py -q` → **65 passed in 46.69s, EXIT=0** (crudo `01-pre_seleccion_dos_familias.txt`). Casa con la referencia vigente (65 passed, EXIT=0, medida en `0f50ea4`) re-medida ahora en `4d35a42` |
| Interprete | Python 3.13.3 (`C:\Users\Jhond\AppData\Local\Programs\Python\Python313\python`), git 2.53.0.windows.1, CLI `C:\Users\Jhond\AppData\Roaming\npm\qmind.CMD` |
| Rojo vivo y deseado | `--strict` cierra **EXIT=1** por `[DUPLICADO-VIGENTE]` de la era G (`01a0bfc9-5f5a-783e-9492-16367bbff596`). Dueño: el operador (S-CIM-2, AC6 opcion b del plan CURA). **No se apago, no se toco el notebook** |

El `EXIT` de cada crudo queda escrito **dentro** del archivo; el `$` del verificador se leyo sin tuberia
(`echo "EXIT=$?"` sobre el propio comando, no sobre un pipe).

---

## 2. La varianza que se dictamina

Corrida archivada `.../ARCHIVADO-2026-10-10/01-upload_verificacion_y_dictamen.txt`: `[CONTADOR]` con
**5 fuente(s) huesped(s)** y 3 con fidelidad remota medida.
Corrida `.../04-strict_post_archivado.txt`: `[CONTADOR]` con **1 fuente(s) huesped(s)** y 2 con fidelidad remota
medida. Mismo repo, mismo registro, mismo commit base. Las 4 que desaparecen son las del plan JEV:

| id (medida hoy, crudo 03) | sha_metadata del crudo 01 | titulo |
|----------------------------|---------------------------|--------|
| `01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5` | `34e2a95195b2...` | 10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre offline, lecciones finales 2026-09-27) |
| `01a10853-6da2-7820-b2a3-fa1cb5ccb4ba` | `424b5828e341...` | ... (cierre FASE-B, lecciones finales 2026-10-04) |
| `01a10e39-1625-71b1-8ca6-73cbdb1c6a94` | `d1b8ff00b511...` | ... (cierre FASE-RELEASE, checkpoint documental 2026-10-05) |
| `01a10ec9-8113-7875-a806-2eec6521d37a` | `ee40f5ee52ff...` | ... (cierre FASE-RELEASE, etiqueta AC5 dictada 2026-10-05) |

La fuente contable del JEV es `01a12247-f791-7944-832e-13f5cad68f3e`, que es **exactamente** el id al que la
corrida 04 le imprime `[AVISO] descarga ... salió 1: error: QMind network request failed`.

---

## 3. Mapa de control de flujo de `verificar_contenido()`

El bucle `for e in vigentes` tiene **9 sentencias `continue`** (medido con `awk` sobre el rango del bucle, no de
lectura). Llamadas a `_huespedes_sin_contabilidad()`: **2** — una dentro de la rama de migracion, antes de su
`continue`, y la del final del bucle.

| # | Rama (simbolo que decide) | Estado que publica | ¿Recorre el bloque huesped? |
|---|---------------------------|--------------------|------------------------------|
| 1 | `resolver_instanea()` sin archivo | `[NO-EVALUABLE]` (local) | **NO** — `continue` |
| 2 | `cuerpo_del_plan()` devuelve `None` | `[NO-EVALUABLE]` (local) | **NO** — `continue` |
| 3 | entrada sin `sha_cuerpo` (migracion, DA-CIM.9) | `[NO-EVALUABLE]` por migracion | **SI** — evalua a la huesped y despues hace `continue` |
| 4 | `e["sha_cuerpo"] != sha_cuerpo_ahora` | `[VENCIDO]` por cuerpo | **NO** — `continue` (familia declarada S-CIM-9) |
| 5 | `e["sha256"] != sha_inst` | `[VENCIDO]` instantanea vs registro | **NO** — `continue` |
| 6 | `prometidas` con `rotas` | `[PROMESA-ROTA]` | **NO** — `continue` |
| 7 | `prometidas` sin `casadas` ni `rotas` (todo `sin_bajar`, es decir `_hash_bajado()` → `descargar_fuente()` fallo) | `[NO-EVALUABLE] ... no bajaron` | **NO** — `continue` ← **la rama de la varianza** |
| 8 | `candidatas` con `bajo is None` (camino por titulo, misma causa de red) | `[NO-EVALUABLE] ... no bajó` | **NO** — `continue` ← hermano simetrico de la 7 |
| 9 | `candidatas` con `bajo != sha_inst` | `[VENCIDO]` titulo coincidente | **NO** — `continue` |
| — | caida al bloque final (sin `continue`): `casadas` → `[FRESCO]` por metadata; `bajo == sha_inst` → `[FRESCO]` por descarga; `not candidatas` → `[VENCIDO]` por titulo ausente | — | **SI** — las 3 unicas rutas que llegan al bloque del final |

**Resumen del mapa: 4 de 12 rutas evaluan a la huesped, 8 no.** De las 8 que no, **dos (7 y 8) se toman por el
unico camino que depende de la red**: `_hash_bajado()` cachea `None` por `(nb, source_id)` en `_CACHE_BAJADAS`
cuando `descargar_fuente()` devuelve `False`. Lo que co-varia en las dos corridas archivadas es eso.

Dato estructural que cierra la pregunta por la poblacion: `fetch_sources()` se invoca **una sola vez por corrida**
en `main()` y esa misma lista `fuentes` se pasa entera a `verificar_contenido()` y a
`_huespedes_sin_contabilidad()`. No existen dos censos dentro de una corrida.

---

## 4. Reproduccion

### 4.1 Censo vivo, de solo lectura (crudo `03-censo_solo_lectura.txt`)
**1 llamada a `qmind source list`, 0 reintentos, sin bucle** (la racha va contada en el propio crudo):
`EXIT_LLAMADA=0`, `CENSO_TOTAL=64` (casa con el censo que lee el instrumento), `pageSize`/`totalSize` en
cabecera. **5 fuentes nombran al JEV con `10-analisis`**: las 4 huesped de la tabla 2 (con los mismos
`sha_metadata` que imprime el crudo 01) mas la contable `01a12247...` con `sha=b88e3e08a70da45f`, que es el
`sha256` y el `sha_cuerpo` que declara el registro para ese plan. Todas `status=ready`.
`originUrl` y `originalFileUri` **no se imprimieron ni se archivaron** (enlaces firmados).

### 4.2 Matriz offline 2x2 (crudo `04-repro_offline_2x2.txt`)
Instrumento: el mismo tipo de doble de `_run_qmind` que usa `tests/test_validate_qmind_writeback_escritura.py`
(`QmindFalso`), ejecutado por stdin (`python -`) **sin crear archivo** y **sin una sola llamada de red**.
Montaje en `tmp`: `--plans-dir` y `--registro` temporales con el plan JEV (`1.1`, cuerpo y instantanea
byte-exactos) y, cuando toca, una entrada `1.0` sin `sha_cuerpo` a la manera del padre (molde
`_entrada_1_0`). Censo fijo de 6 fuentes, identico en todas las configs; **lo unico que cambia es la respuesta
de `source download` para la fuente contable**.

| Config | descarga | huespedes impresas | ids | `[CONTADOR]` | EXIT |
|--------|----------|--------------------|-----|---------------|------|
| A solo JEV | RESPONDE | **4** | las 4 del JEV | `1+0+0==1; 4 fuente(s) huesped(s)` | **1** (`DUPLICADO-VIGENTE`) |
| B solo JEV | FALLA | **0** | NINGUNO | `1+0+0==1; 0 fuente(s) huesped(s)` | **2** (`NO-EVALUABLE`) |
| C JEV + era 1.0 | RESPONDE | **5** | `01a0bfc9`, `01a0e4d9`, `01a10853`, `01a10e39`, `01a10ec9` | `1+1+0==2; 5 fuente(s) huesped(s)` | 1 |
| D JEV + era 1.0 | FALLA | **1** | `01a0bfc9` | `1+1+0==2; 1 fuente(s) huesped(s)` | 1 |
| E JEV + era, cuerpo editado | (no se descarga: `descargas=0`) | **1** | `01a0bfc9` | `1+1+0==2; 1 fuente(s) huesped(s)` | 1 (`VENCIDO+DUPLICADO-VIGENTE`) |

- **C reproduce el crudo 01** (los mismos 5 ids) y **D reproduce el crudo 04** (el mismo 1 id, `01a0bfc9`) sobre
  un censo **identico**: la unica diferencia entre C y D es si la descarga respondio. Eso atribuye la varianza al
  flujo de control y no a la poblacion.
- **B es el corte decisivo**: sin la era que sostenga el rojo, la bajada fallida no solo deja de imprimir las
  huesped: **el dictamen entero pasa de `EXIT=1` a `EXIT=2`** y el `[CONTADOR]` publica
  `0 fuente(s) huesped(s)`. El rojo de contabilidad es **suprimible por la red**.
- **E** muestra que la rama `VENCIDO` por cuerpo pertenece a la misma familia (su huesped tampoco se evalua),
  que es justo lo que declara S-CIM-9.

### 4.3 Cobertura vigente de la interseccion (medida, no afirmada)
`tests/test_validate_qmind_writeback_escritura.py`: **57 funciones**. Las que ejercitan la huesped: **12**. Las
que ejercitan la bajada que falla (`_corrida(..., {})` o el literal de la linea): **1**
(`test_fuente_que_promete_y_no_baja_es_no_evaluable_nunca_vencido`). **Interseccion: 0** — no hay ningun diente
que pare la rama 7 con huesped en el censo. El metodo de conteo esta escrito en el acta para que sea re-ejecutable.

---

## 5. Hipotesis contrastadas

- **(a) "el bloque huesped solo es alcanzable tras un veredicto favorable por cuerpo (FRESCO)"**: **refutada tal
  como esta redactada, confirmada en su mitad**. Es alcanzable tambien desde la abstencion de migracion (rama 3,
  DA-CIM.9) y desde el `[VENCIDO]` por titulo ausente, segun el mapa de §3; pero si es cierto que **no** es
  alcanzable desde las ramas que cortan `continue` antes del bloque. La redaccion de (a) se queda corta en
  denominador: goberna 3 rutas de 12 y no 1 de 12.
- **(b) "las 4 fuentes del JEV siempre estuvieron en el censo y la corrida 04 simplemente no las imprimio"**:
  **CONFIRMADA**. Prueba directa: el censo vivo de hoy (1 llamada) las muestra con los mismos `sha_metadata` del
  crudo 01. Prueba interna a la corrida 04: esa corrida imprime `[NO-EVALUABLE] ... 1 fuente(s) cuyo metadata
  casa no bajaron`, y esa linea **solo existe si `fetch_sources()` respondio y casa por metadata**; ademas imprime
  la huesped de la era G, que sale del mismo `fuentes`. El censo no falto: lo que falto fue la bajada.
- **(c) "la poblacion del censo difiere entre corridas por la red"**: **REFUTADA**. `fetch_sources()` es una
  llamada unica por corrida (§3); si esa llamada fallara, `main()` entraria en `QmindUnavailable` y no habria
  `[FRESCO]` ni `[CONTADOR]` en absoluto. La variacion de red medida vive en `descargar_fuente()`
  (`source download`), que es una llamada **distinta** y por fuente, y cuyo resultado se cachea en
  `_CACHE_BAJADAS`.
- **(d) la del diagnostico**: la varianza es un **artefacto de control de flujo**, no de datos: el unico hallazgo
  que no necesita ninguna observacion de red (`_huespedes_sin_contabilidad()` lee `datos` y `fuentes`, y no
  baja) esta colocado detras de los `continue` que la observacion de red decide. Prueba: B y C/D del §4.2.

---

## 6. Dictamen

**Hay hueco.** No es el comportamiento gobernado.

- **Donde**: en `verificar_contenido()`, rama **7** — el `else` del bloque `if prometidas:` (todos los miembros
  acaban en `sin_bajar` porque `_hash_bajado()` devolvio `None`), cuyo `continue` se toma **antes** de la unica
  llamada al bloque huesped del final del bucle. Y su hermano simetrico, rama **8**: `bajo is None` dentro del
  `else` del camino por titulo.
- **Por que no esta gobernado**: la deuda **S-CIM-9** declara la familia de los `continue` pero nombra y dienta
  **solo el miembro `VENCIDO` por cuerpo** (`test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado`
  aserta el comportamiento vigente y se pondra rojo cuando un AC lo gobierne). Ningun documento del corpus nombra
  el miembro de la **bajada fallida**, y medido: **0 de 57** funciones cubren la interseccion. Su disparador
  ademas no es editorial (una decision sobre contenido publicado) sino **ambiental** (que el servidor contesto).
- **Por que es mas grave que el miembro declarado**: el miembro de S-CIM-9 deja de imprimir una linea y sigue
  cerrando `EXIT=1` por su propio `[VENCIDO]`. El miembro de bajada **cambia el estado del check**: con la misma
  poblacion pasa de `1` a `2` (§4.2 config B), de modo que un duplicado real puede quedar sin dictaminar y el
  resumen lo anuncia como abstencion. Y el `[CONTADOR]` publica `0 fuente(s) huesped(s)` —un `0` que se lee como
  dato del censo cuando el bloque nunca se ejecuto—, que es la colision que **R2.9** prohibe: *lector fallido
  nunca un favorable ni un `0`*.
- **Tres estados R2.9 en los lectores de esta sesion**: (i) *con hallazgos*, con denominador: crudo 03 dice
  `CENSO_TOTAL=64` y `FUENTES_QUE_NOMBRAN_AL_JEV=5`, y crudo 04 imprime `huespedes_impresas` por config;
  (ii) *ausente*, con la ruta buscada: la sonda nombra el filtro aplicado (titulo con `10-analisis` y
  `EVALUACION-JEV-TYPESAFE`); el lector gobernado es `fetch_sources()` y sus tres estados ya estan dientados por
  `test_censo_que_no_responde_es_estado_propio_y_no_re_subir` (lector fallido),
  `test_censo_que_no_la_ve_nombra_lo_buscado_sin_re_subir` (ausente con lo buscado) y
  `test_la_tabla_puebla_fuente_id_en_la_rama_explicita_y_casa_con_el_censo` (con hallazgos);
  (iii) *lector fallido*, con motivo: la sonda cierra `EXIT_LLAMADA` distincto y aborta con `sys.exit(3)` y la
  primera linea del error si el CLI responde distinto de 0 — en esta corrida respondio 0, asi que **ese camino no
  se ejercito y queda declarado como limite de la sonda**, no como verde.

---

## 7. Mandato para una fase futura (NO se abre aqui)

Frase literal:

> la cura esta en `verificar_contenido()` porque el bloque huesped depende de la red: medido en un montaje con
> censo identico, la unica variable `source download` movio el `[CONTADOR]` de `5 fuente(s) huesped(s)` a
> `1 fuente(s) huesped(s)` y el EXIT de `1` a `2` (crudo 04, configs B/C/D), cuando
> `_huespedes_sin_contabilidad()` lee solo `datos` y `fuentes` y no necesita ninguna bajada.

- **Proximo AC** (una fase propia, con dueño operador, disparador: gobernar los `continue` del bucle de
  `verificar_contenido()` — el mandato que la propia S-CIM-9 ya tiene en su columna de mandato): **AC-N.1** —
  el hallazgo de contabilidad se evalua en **todas** las rutas del bucle, incluidas las 8 que hoy cortan antes
  (ramas 1, 2, 4, 5, 6, 7, 8, 9), y el `[CONTADOR]` publica los huespedes con su **denominador de observacion**
  (cuantas entradas llegaron al bloque), de modo que `0 fuente(s) huesped(s)` solo pueda salir de una ruta que
  efectivamente lo recorrio.
- **Diente** (nombrado por su causa, familia `tests/test_validate_qmind_writeback_escritura.py`):
  `test_una_bajada_que_falla_no_suprime_a_su_huesped_de_contabilidad` — mismo montaje de §4.2 config B, se exige
  `[DUPLICADO-VIGENTE]` con las 4 ids y `EXIT=1` **a pesar** de la abstencion por bajada. Hermano que re-ancla la
  caracterizacion vigente: el dia de AC-N.1,
  `test_un_vencido_por_cuerpo_en_la_mesma_entrada_no_evalua_a_su_huesped_limite_declarado` **debe ponerse rojo**
  por diseño (eso es su contrato declarado) y se re-escribe como diente de la cure.
- **Mutante** (R2.8, dos salidas en el `evidence/` de esa fase): borrar el `continue` de la rama 7 y dejar que la
  evaluacion de huesped corra. Anclar **por clave**, no por id posicional. Se exige que el diente de AC-N.1 caiga
  **por la causa nombrada** (el contador de huespedes) y que el arbol intacto se verifique por sha.
- **No es cura de contenido**: no se toca el notebook, no se re-suben las 4 fuentes del JEV, no se borra la era G.
  La decision sobre las fuentes duplicadas del JEV (que son las 5 huesped reales) sigue siendo del operador.

---

## 8. Los cinco cortes, declarados y verificados sin commitear

| Corte | Estado |
|-------|--------|
| 1. Implementacion terminada | N/A por naturaleza: es diagnostico, no escribe codigo ni tests. Termina la medicion y el acta |
| 2. Verificacion terminada | ✅ crudo 01 (`65 passed`, `EXIT=0`), crudo 02 (quick **PRE** `13/13`, `EXIT=0`), crudos 03 y 04 reproducen el par archivado sobre censo identico, crudo 05 (quick **POST** con el acta y los crudos 01-04 ya en el arbol —el propio 05 se estaba escribiendo por redireccion—: `13/13`, `STATUS: ALL VALIDATIONS PASSED`, `EXIT=0` — el directorio nuevo de evidencia no mueve el gate `--check`) |
| 3. Cierre documental | ✅ este acta + crudos numerados. **No** se escribio `REGISTRY.md` (no es fase de plan) ni se regenero el indice de lecciones (no se edito ningun `.md` de `plans/` o `context/`) |
| 4. Listo para revision | ✅ arbol con solo `evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/` como trabajo nuevo; las 13 rutas staged AJENAS quedan como estaban |
| 5. Espera de autorizacion | ✅ **asi queda la sesion**: sin `git commit`, sin `git add`, sin `--amend`, sin L3, sin push. Commit, L3 y push solo con literal del operador |

---

## 9. Auto-reporte de presupuesto

- **Unidad declarada**: `tool_use` (invocaciones de herramienta de esta sesion), el mismo denominador del
  mandato (90, por analogia con A2/A3/B/C).
- **Medido**: **47** invocaciones al cerrar (enumeracion manual, bloque por bloque, de las herramientas de esta
  sesion; incluye la escritura bloqueada por el clasificador y **dos ediciones fallidas** por mala transcripcion
  del ancla, que tambien gastan). La cifra inicial del acta decia 42 y era un **subconteo**: se re-enumeró y se
  re-ancló aqui, no se delego al recordatorio. **No existe comando en el repo que imprima esta unidad**: el
  conteo es declarativo y su limite va escrito aqui, conforme a la politica de unidad reproducible. Proxy
  re-ejecutable de gasto: los 5 crudos archivados y sus `EXIT`.
- **Presupuesto**: 47 de 90 = **52 %**. Sin exceso, sin checkpoint, sin segunda sesion.

## 10. Restricciones cumplidas y limites

- Cero escrituras remotas: `qmind` se invoco **una vez** y con `source list` (solo lectura); `source download`
  **nunca contra el servicio** (solo el doble offline); `source upload` y `source delete`: **cero llamadas**.
- No se re-codifico ningun crudo de pytest: `01` se escribio por redireccion directa de la corrida.
- No se edito codigo ni tests. El scratch de reproduccion se ejecuto por `python -` desde stdin, **sin crear
  archivo** (el clasificador veto el scratch fuera del workspace y un `.py` dentro moveria los contadores del
  gate `--check` de `.opencode/wiring_report.json`, medido antes como deuda del hermano); el arnes queda
  descrito en §4.2 y es re-ejecutable con el bloque de esta acta.
- Limites de esta sesion: (i) **no se reproduce la corrida real** de `--strict` contra el notebook (solo lectura
  de censo, sin verificacion por descarga en vivo); (ii) el `sha_metadata` de las 4 huesped en la matriz usa el
  prefijo de 16 hex **medido** mas relleno `0`, porque el crudo 01 los recorta a 12 y la matriz no compara esos
  sha contra ninguna promesa; (iii) el titulo de la huesped de la era G esta copiado del crudo 01, que lo recorta
  a 60 caracteres por construccion del instrumento.
