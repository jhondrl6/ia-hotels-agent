# CONTEXT — Deudas del write-back de QMind: la rama que sube y no registra

**Fecha:** 2026-10-15. **Sesión:** tanda `CURA-SEGUNDA-VIA-QMIND` (cura de la segunda vía de gobernación + cura del
reemplazo por documento; commits `2e048e6` y `1f95e84`, empujados sobre `5341e15`). **Sin plan dueño:** el hallazgo no
pertenece al alcance de `CURA-COSTURA-TRIBUNAL-2026-10-11` (costura del Tribunal), así que las deudas se definen aquí,
en el corpus de definiciones que `scripts/build_lesson_index.py` reconoce para `.opencode/context/`. La medición completa
y su crudeza están en `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/14-deuda-writer-context-sin-registro.txt`.

> **Qué es este archivo.** Dos deudas de instrumento sobre `scripts/validate_qmind_writeback.py`, cada una con su
> medición, su disparador y su coste. No es un plan, no abre fase y no declara ACs.
>
> **No autodeclara lección durable.** La entrada a la población de write-back de QMind depende de tres grafías al inicio
> de línea real —las dos «…de forma» y «…durable», y la de lecciones capitalizadas—, no del nombre del archivo. Este
> documento no escribe ninguna de las tres al inicio de línea, así que
> `scripts/verify_qmind_context_freshness.py` debe publicarlo como `[EXCLUIDO]` con la razón de no-declaración: la
> política del write-back es por aporte declarado, no por existencia.
>
> **Acuña dos IDs nuevos**, `D-QW-1` y `D-QW-2`, ambos definidos aquí y ninguno citado desde los tres documentos que
> gobernan los contextos (`10-analisis`, `00-lecciones`, `dependencias-fases`) de ningún plan archivado. Contadores al
> escribir: **387 IDs** definidos y `110` citados sin definición, antes de regenerar el par.

---

## 0. Veredicto en una línea

El writer tiene dos caminos para publicar y solo uno de ellos deja contabilidad: la rama explícita (`--file` / `--title`)
registra, la rama por defecto sube los contextos declarados y se queda en un `[OK] Subido:` que ningún verificador vuelve
a mirar. Mientras el detector de esa rama devuelva 0 declaraciones el hueco es latente, no rojo — y el mismo archivo
revela por qué puede dejar de serlo: las dos copias del detector no son el mismo conjunto.

---

## 1. `D-QW-1` — La rama por defecto de `--upload` sube CONTEXT y no los registra

`do_upload()` resuelve primero el `10-analisis` del plan y lo registra con `publicar_en_registro()`. Después, en la rama
sin `--file`/`--title`, recorre `scan_context_declarations()` y por cada elemento llama a `upload_source()`, imprime
`[OK] Subido: <archivo>` y **no** llama a `publicar_en_registro()` ni a `registrar_publicacion()`. Lo que no entra en
`registro.json` no existe para ninguna de las dos capas del propio instrumento:

- `verificar_contenido()` itera las entradas con estado vigente: sin entrada no hay instantánea que cotejar, no hay
  `sha_cuerpo`, y la fidelidad remota (metadata del servidor + descarga) no se mide.
- `_fuente_nombral()` exige que el título contenga `10-analisis`, y los títulos que emite esa rama son `CONTEXT: <stem>`:
  la fuente tampoco se contabiliza como huésped, o sea que sale del `[CONTADOR]` sin dejar rastro.
- El reemplazo no aplica, así que una segunda subida del mismo contexto con título nuevo queda como dos fuentes sin marca
  de reemplazada — la familia del rojo `DUPLICADO-VIGENTE` que la casa ya conoce por la era G.

**Medido el 2026-10-15:** `scan_context_declarations()` devuelve **0** sobre la raíz de `.opencode/context/`, así que hoy
el bucle no sube nada. Es una deuda latente: su coste no se paga hasta que alguien capitaliza un contexto con la grafía
que la rama sí ve.

---

## 2. `D-QW-2` — Dos copias del detector de autodeclaración, con conjuntos distintos

`CONTEXT_DECLARATION_MARKERS` (writer) ancla las tres grafías a inicio de línea exacto. `MARCA_DURABLE`
(`verify_qmind_context_freshness.py`) acepta además sangría y encabezado (`#` de nivel 1 a 6), y tolera espacio antes de
los dos puntos — esa fue la cura del 2026-09-27, cuando el contexto de JEV declaraba como encabezado y el detector
devolvía 0 sobre un archivo que sí declaraba.

La divergencia produce dos cortes opuestos, ambos medidos por comparación de los patrones (ningún archivo del árbol los
dispara hoy, porque las dos funciones devuelven 0 sobre la raíz):

- Un contexto que declara **como encabezado**: lo goberna el verificador de frescura (le exige fuente publicada byte a
  byte) y **no** lo sube la rama por defecto del writer.
- Un contexto que declara **a línea suelta**: lo sube el writer, y esa subida no deja registro (es `D-QW-1`).

La cura de fondo es una sola: que el writer consuma el mismo predicado que `declara_durable()` del hermano en lugar de
mantener una copia propia.

---

## 3. Tabla de definiciones

| ID | Enunciado | Definida en | Evidencia |
|---|---|---|---|
| `D-QW-1` | la rama por defecto de `--upload` sube los CONTEXT declarados y no los registra: sin entrada escapan de la capa de contenido y del bloque de huéspedes | este §1 | lectura de `do_upload()`, `publicar_en_registro()` y `_fuente_nombral()` en `scripts/validate_qmind_writeback.py`; `scan_context_declarations()` = 0 declarado el 2026-10-15; crudo `14-` de `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-RELEASE/` |
| `D-QW-2` | el writer y el verificador de frescura mantienen copias distintas del detector de autodeclaración, así que gobernar y subir pueden no ser el mismo conjunto | este §2 | comparación de `CONTEXT_DECLARATION_MARKERS` con `MARCA_DURABLE` en los dos guiones; antecedente de la divergencia: el contexto de JEV medido el 2026-09-27 |

---

## 4. Qué no sostiene este documento

- No afirma que exista hoy una fuente `CONTEXT:` publicada por la rama por defecto: midió 0 declaraciones y por eso
  nombra la deuda latente.
- No decide el contrato de la entrada: `sha_cuerpo` de una publicación de contexto graba hoy el sha del `10-analisis` del
  plan (medido en las dos publicaciones de esta tanda: `5c54f5ed3cb9…` en ambas, frente a `sha256` propios
  `f6e14e735e51…` y `3cebfeb58e48…`). Cambiarlo o añadir un campo propio es decisión del Operador, no de este escrito.
- No toca el rojo `DUPLICADO-VIGENTE` de la era G ni las 5 fuentes huéspedes sin contabilidad: deuda ya registrada con
  dueño desde la release 4.80.0.
- No cura nada: no cambia `scripts/`, no sube nada al notebook y no abre fase. Sus dos entradas necesitan dientes propios
  (una subida por la rama por defecto con corpus montado en `tmp`, y un control de paridad entre los dos patrones) antes
  de cualquier código.
