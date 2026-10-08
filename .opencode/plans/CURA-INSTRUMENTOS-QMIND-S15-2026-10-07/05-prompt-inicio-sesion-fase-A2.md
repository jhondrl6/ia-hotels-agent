# FASE-A2 — Slug sin colisión y `fuente_id` capturado de la tabla (AC3, AC4)

**ID:** CURA-INSTRUMENTOS-QMIND-S15 / FASE-A2
**Objetivo:** que cada publicación deje su propio byte-exacto en el repo y que el registro sepa **qué fuente del
notebook** publicó, sin que un parseo fallido se convierta en una segunda subida.
**Dependencias:** FASE-A1 cerrada (misma función, `registrar_publicacion()`; el orden no es opcional).
**Complejidad:** MEDIA-ALTA — toca el emisor, y su error no se ve hasta que alguien intenta casar una entrada
contra disco.
**Skill:** `.agents/workflows/phased_project_executor.md`.
**Modo:** DIRECTO. **R3:** 4 tareas, 0 comandos largos. **Comando remoto:** **ninguna subida real** en esta fase
(AC10 es de RELEASE); todo diente de AC4 se ejerce sobre la **tabla archivada** de una subida ya hecha y sobre
fixtures sintéticas, nunca re-subiendo.

## Contexto

Dos defectos medidos el 2026-10-07 y re-confirmados en la preparación:

- **Slug.** `registrar_publicacion()` nombra la instantánea con `re.sub(...)[:120] + ".md"`. Dos títulos con
  prefijo común de 120 caracteres producen el mismo archivo. En el plan padre: el registro tiene **dos** entradas
  con shas distintos (`0b02bb5084e3…` y `1f0ee6e52f00…`) y `instantaneas/` tiene **un** archivo de datos, cuyo sha
  medido es `1f0ee6e52f00…` — la segunda publicación sobrescribió los bytes de la primera. Los byte-exactos de la
  entrada `reemplazada` **están perdidos** y no se recuperan (deuda S-CIM-3 del maestro). Consecuencia adicional que
  esta fase debe respetar: en ese directorio ya vive un `README.md`; el nombre nuevo no puede producirlo.
- **`fuente_id`.** `do_upload()` pasa `""` en sus dos ramas porque `upload_source()` devuelve la salida cruda del
  CLI y nadie la parsea. Y la respuesta de `qmind source upload` **no es JSON**: es una tabla `Key: value`
  (`ID:`, `NotebookID:`, `Title:`, `Type:`, `Status:`, `URI:`, `UpdatedAt:`). Un parser que busque `{"…}` aborta
  con «sin id» **después** de que la subida ya tuvo éxito; si ante eso se re-corre el `upload`, se crea una fuente
  duplicada (la idempotencia es por título y el título nuevo nunca existió).

### Estado de fases anteriores

| Fase | Estado |
|---|---|
| Preparación | ✅ 2026-10-08 |
| FASE-A1 | ✅ **CERRADA, COMMITEADA Y EMPUJADA** 2026-10-08 — AC1 y AC2 landed (`sha_cuerpo` + schema 1.1 y puerta de vigencia cuerpo contra cuerpo, con el gate de registro y D2 conservados). Banda empujada completa: `d8a7d80..67b7e2f` — la cura `63b944a`, el sello `15f4fdd` y la addenda `67b7e2f`, con L3 **sin hallazgos** en las tres tandas. PRE 23 passed → POST 31 passed (resta 8), tres mutantes sobre copia aislada. Crudos y registro: `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/` |
| FASE-A3, B, C, RELEASE | ⬜ Pendientes |

**Línea base de esta fase:** el tip que imprima `git ls-remote origin refs/heads/master` **al abrir la sesión**, no la
cifra de la tabla de arriba — esa describe la banda de A1 y es histórica. La banda `d8a7d80..67b7e2f` quedó cerrada
con la enmienda del 2026-10-08; cualquier commit posterior la sigue moviendo hacia adelante, así que la paridad se
declara por comando (`ls-remote` == `rev-parse HEAD`) y por `git status --porcelain -uall`, nunca por memoria.

### Lecciones capitalizadas aplicables a esta fase

| ID | Lección | Qué cambia en ESTA fase |
|---|---|---|
| L-QW.2 | Publicar con título distinto resuelve el SKIP y *crea* el duplicado | AC4: el registro es la contabilidad que hace falta para que el duplicado no sea la vía fácil; AC3: un slug que pisa el archivo anterior miente sobre el reemplazo |
| L-QW.3 | Un verde por ausencia del instrumento es un rojo disfrazado | AC4: si el parseo falla, el estado publicado es «id no capturado», y se verifica por censo, no se calla |
| L-PF6 | Ausencia observada y lector fallido no son equivalentes | AC4 y AC5: «el censo no respondió» se nombra como lector fallido con motivo; «no hay fuente con ese id» como ausencia con la ruta buscada |
| L-ENT.14 | Una prueba de NO-existencia recortada por un `head` no prueba nada | El censo de `fetch_sources()` y el inventario de `instantaneas/` se publican con el comando completo y sin corte |
| L-T4A.5 | Un verde puede no alcanzar la rama que dice certificar | El diente de AC4 se ejercita sobre la tabla real archivada y sobre el `do_upload()` versionado, no sobre un dict fabricado en el test |
| L-V2.1 | Un test que solo mira qué check disparó queda verde por la rama equivocada | El mutante de AC3 ancla la **aserción que pierde**: la comparación de los dos byte-exactos, no la existencia del archivo |
| L-G3 | Cambiar un contrato reescribe sus tests y su prosa en el mismo commit | El `README.md` de `instantaneas/` describe el esquema de nombres y viaja con esta fase si A1 no lo actualizó ya |

## Tareas

### Reglas de ejecución adoptadas (vía c2 de la decisión de presupuesto, 2026-10-08)

Las dos reglas entran **antes** de las tareas porque redistribuyen el presupuesto de la fase. Su base es la medición
de FASE-A1 (`evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/00-registro-de-fase.md`): ≈25 `tool_use` se fueron
en el cierre documental y ≈15 en verificaciones y re-tomas, y las re-tomas nacían de editar código cuando el cierre
ya estaba abierto.

1. **Congelar el código antes de abrir el cierre documental.** Cuando terminan las tareas 2 a 4 —el `slug`, el
   `fuente_id` y sus dientes— el código y los tests quedan **congelados**. A partir de ahí el POST de la selección y
   la corrida de mutantes se re-toman **UNA sola vez, al final**, sobre el instrumento ya definitivo, y se archivan.
   Si algo obliga a re-abrir el código, se declara la re-toma y su motivo en el registro de fase; no se encadena una
   segunda ni una tercera.
2. **Los reemplazos documentales del cierre se ejecutan con un solo script de bytes bajo `temp/`, con
   `count(old) == 1` por ancla, y se borra al terminar.** Es la misma receta canónica del saneado (contrato
   §Límites: sustitución a nivel de bytes con `assert count(old) == N` y prueba de sha inversa), aplicada a las
   ediciones de documentación que el cierre acumula. El script es de un solo uso, vive bajo `temp/` (excluido por
   declaración de Git), imprime el ancla que casó y el recuento por archivo, y se elimina al terminar; lo que
   produce queda en el diff del árbol, no en el scratch. **Ningún `.py` se escribe bajo `evidence/`** (contrato
   §Límites).

### Tarea 1 — PRE y lectura de la interfaz real

Re-medir HEAD/status/quick; PRE de `tests/test_validate_qmind_writeback_escritura.py` con intérprete declarado.
Leer la firma del CLI (`qmind source upload --help`, solo lectura de ayuda) y **no** subir nada. Localizar la
tabla de una subida real ya archivada (el padre dejó su crudo en `evidence/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/
FASE-RELEASE/crudos/`): se **lee** como referencia de forma, no se re-ejecuta ni se copia material del cliente.
Redactar antes de persistir cualquier salida: `URI:` y enlaces firmados fuera.

### Tarea 2 — AC3: slug único y legible

El nombre incluye el sha de la instantánea (o un correlativo verificable), conserva el prefijo legible
`<plan>--<titulo-saneado>` y no puede colisionar con `README.md` ni entre dos publicaciones del mismo plan. La
decisión de esquema se registra como decisión del plan (maestro §2) porque define lo que el lector humano va a
ver en `instantaneas/`.

**Criterios:** dos publicaciones seguidas del mismo plan → dos archivos, dos byte-exactos, cada entrada casa con
el suyo; un tercero con título de prefijo común tampoco pisa.

### Tarea 3 — AC4: `fuente_id` parseado de la tabla, sin re-subida

Parsear la respuesta de `upload_source()` por líneas `Key: value` y escribir el id en la entrada de
`registrar_publicacion()` en **las dos ramas** de `do_upload()`. Si el parseo falla: **no re-subir**, verificar
por censo de `fetch_sources()` (comparando título y `sha_metadata`) y publicar el estado «id no capturado» con su
motivo. El contador de subidas de la corrida es 1: un diente lo afirma.

**Criterios:** con la tabla archivada, el id extraído casa con una fuente real del censo; con una tabla degenerada
(sin la línea `ID:`), el diente declara «no capturado» y **no** se invoca una segunda subida.

### Tarea 4 — Dientes y cierre

Mutantes exigidos (cada uno con restauración por sha256, sobre el instrumento versionado):
1. Devolver el slug al prefijo truncado → la segunda publicación pisa la primera y cae el diente de byte-exactos.
2. Quitar el sha del nombre → colisión recuperable y el diente lo prueba con dos títulos de prefijo común.
3. Parsear la salida como JSON → id vacío, y el diente afirma «id no capturado» en vez de silencio.
4. Re-subir ante parseo fallido → el contador de subidas pasa de 1 y el diente de contención cae.
5. Escribir `fuente_id` en una sola rama de `do_upload()` → el diente que recorre las dos ramas cae.

Cierre incremental del contrato paso 1 al 8, con la regla de que el registro **no** se edita a mano: toda
entrada nueva sale del escritor.

## Tests Obligatorios

| Superficie | Criterio |
|---|---|
| `tests/test_validate_qmind_writeback_escritura.py` | 23 viejos + los de A1 + los de A2, sin aserción rebajada |
| Dientes AC3/AC4 | con su par rojo/verde archivado y restauración por sha |
| `run_all_validations.py --quick` | todos sus checks |
| Censo remoto | **no** se ejecuta en esta fase; se declara que AC4 cerró sobre tabla archivada y que la verificación por censo queda pendiente de la corrida de A3/RELEASE |

## Post-ejecución (OBLIGATORIO)

Identica a la de A1 (contrato §cierre), con el comando del escritor y sin `--release`:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-A2 --fecha 2026-10-08 \
    --desc "CURA-INSTRUMENTOS-QMIND-S15: slug sin colision y fuente_id capturado de la tabla" \
    --archivos-mod "$ARCHIVOS_MOD_MEDIDOS" --tests "$TESTS_NUEVOS_MEDIDOS" --check-manual-docs
```

## Criterios de Completitud (CHECKLIST)

- [ ] AC3 legible en disco: `instantaneas/` muestra dos archivos distintos para dos publicaciones y el `README.md` sigue intacto
- [ ] AC4 legible en `registro.json`: `fuente_id` poblado en la entrada nueva, con su diente de parseo fallido y su no-re-subida
- [ ] Los 23 + los dientes de A1 siguen verdes; delta explicado solo por adiciones de ESTA fase
- [ ] Ninguna subida real ejecutada; ningún material del cliente propagado; ninguna salida firmada persistida
- [ ] PRE/POST con resta comprobada; post-ejecución completo; quick verde; derivados regenerados
- [ ] El `README.md` de `instantaneas/` describe el esquema de nombres vigente
- [ ] Reglas c2 cumplidas y verificables en la evidencia: el código quedó **congelado** antes de abrir el cierre
  documental, el POST y los mutantes se re-tomaron **una** sola vez al final (si hubo más de una re-toma, cada una
  está declarada con su motivo), y los reemplazos documentales los hizo **un único script de bytes bajo `temp/`**
  con `count(old) == 1` por ancla, impreso con su recuento por archivo y borrado al terminar

## Restricciones

- Depende duramente de A1: sin `sha_cuerpo` landed, esta fase se detiene y declara INCOMPLETA con checkpoint.
- Prohibido re-subir ante un parseo fallido. Prohibido `qmind source delete`. Prohibido editar el registro a mano.
- No tocar `AGENTS.md`, `.cursorrules`, `VERSION.yaml`, el workflow ni los hooks; no liberar versión.
- No iniciar FASE-A3. Presupuesto **90 `tool_use`** al corte autorizado (la referencia por fase y su base medida
  viven en `04-contrato-ejecucion.md` §R2); auto-reporte con unidad declarada (R2.1).

## Prompt de ejecución

```
Actua como ejecutor de fases del repo C:\Users\Jhond\Github\iah-cli (rama master), en espanol y sin acentos en
el mensaje de commit.

Lee 01-plan-maestro.md §1 y §4, 04-contrato-ejecucion.md, 00-lecciones-capitalizadas.md §2 y §4, dependencias-fases.md, 05-prompt-inicio-sesion-fase-A2.md y el workflow canónico.

Ejecuta SOLO FASE-A2 del plan .opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07, y solo si FASE-A1 cerro.

OBJETIVO: que cada publicacion deje su propio byte-exacto y que el registro sepa que fuente publico, sin que un
parseo fallido provoque una segunda subida.

TAREAS: 1) PRE y lectura de la interfaz real sin subir nada. 2) AC3 slug unico y legible. 3) AC4 fuente_id desde
la tabla Key value con no-re-subida. 4) cinco mutantes con restauracion por sha y cierre.

REGLAS c2 (adoptadas con la decision de presupuesto del 2026-10-08): (i) congela el codigo antes de abrir el cierre
documental, y el POST y los mutantes se re-toman UNA sola vez al final; (ii) los reemplazos documentales del cierre
se ejecutan con un solo script de bytes bajo temp/, con count(old) == 1 por ancla, borrado al terminar. Presupuesto
90 tool_use al corte autorizado; la referencia y su base medida viven en 04-contrato-ejecucion.md §R2.

CRITERIOS: dos publicaciones del mismo plan dejan dos archivos que casan cada uno con su entrada, la tabla
archivada produce un id que casa con el censo, y ante tabla degenerada el estado es id no capturado con contador
de subidas igual a uno.

RESTRICCIONES: sin subida ni borrado remoto, sin editar el registro a mano, sin tocar el plan padre, sin AGENTS
ni VERSION, sin commit salvo instruccion literal, sin iniciar A3.

```
