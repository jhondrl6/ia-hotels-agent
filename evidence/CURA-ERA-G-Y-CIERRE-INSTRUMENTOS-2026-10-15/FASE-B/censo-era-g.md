# Censo de la deuda era-G y decisión por fuente — FASE-B

> **Plan**: CURA-ERA-G-Y-CIERRE-INSTRUMENTOS-2026-10-15 · **Fase**: FASE-B · **Fecha de cierre**: 2026-10-22
> **Naturaleza**: fase de medición y decisión. **No cura nada, no borra nada, no toca código** (AC3 y AC4 son este documento; AC5 se cierra en FASE-C con el par rojo-antes/verde-después).
> **Población medida con**: el propio instrumento `scripts/validate_qmind_writeback.py` (corrida de esta sesión, crudo `01-writeback-rojo-antes.txt`) + el listado del notebook `iah-cli-lecciones` (`qmind source list --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 --all --format json`, crudo `02-notebook-source-list.json`; 68 fuentes) + `.opencode/qmind-writeback/registro.json` (schema 1.1, 9 entradas) leído en vivo.

## 1. El rojo-antes (AC5 insumo)

- Corrida del 2026-10-22 en esta sesión con el intérprete canónico (`venv/Scripts/python.exe`): **`EXIT 1`**, `5` líneas `[DUPLICADO-VIGENTE]` y `[CONTADOR] 8 vigente(s) … 5 fuente(s) huesped(s) sin contabilidad`. Crudo completo: `01-writeback-rojo-antes.txt`.
- **Intentos de corrida: 1** (declarado por el aviso de la fase: la corrida exige red). La corrida trajo 3 `[AVISO]` de descarga fallida (`01a12247…`, `01a1239b…`, `01a125a0…`, `error: QMind network request failed`), que dejaron 3 entradas `[NO-EVALUABLE] … su metadata casa no bajaron`. Esas abstenciones **no tocan las dos poblaciones de este censo**: los 5 `[DUPLICADO-VIGENTE]` y el `[CONTADOR]` salieron completos y sus datos (id, título, sha de metadata) provienen del listado del notebook, no de descargas. El rojo-antes queda publicado con sus abstenciones, no re-corrido hasta un verde de conveniencia.

## 2. Censo por fuente (AC3)

Predicados usados (declarados por D-QW-2: **no** se usó `scan_context_declarations()` como población gobernada; se replicaron los predicados del propio instrumento sobre el listado del notebook): `_fuente_nombral` (el título contiene `10-analisis` y nombra al plan o a su stem sin fecha final) y la contabilidad de `_huespedes_sin_contabilidad` (el título aparece en **cualquier** entrada del plan en el registro, incluida la `reemplazada`).

| # | id (completo) | Título completo | `sha_metadata` | Fecha (`createdAt` del listado, America/Bogota) | Atadura del título | Contabilidad en el registro | Respaldo byte-exacto medido |
|---|---------------|-----------------|----------------|--------------------------------|--------------------|-----------------------------|-----------------------------|
| 1 | `01a0bfc9-5f5a-783e-9492-16367bbff596` | `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (lecciones aprendidas y decisiones)` | `87b9b6664f945ac6279f1efaf9aa7682cac8a1c952e633bfc4ff55ce67a49274` | 2026-09-20 12:07:20 | plan (`_fuente_nombral`) | **no contable**: no existe entrada en el registro con ese título — las 2 entradas del plan son «…(cierre 4.79.0, lecciones finales 2026-10-07)» (`reemplazada`) y «…(cierre 4.79.0, lecciones finales 2026-10-07, rutas archivadas)» (`vigente`) | **NINGUNO** (ni instantánea ni blob histórico en el conjunto medido) |
| 2 | `01a10ec9-8113-7875-a806-2eec6521d37a` | `10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre FASE-RELEASE, etiqueta AC5 dictada 2026-10-05)` | `ee40f5ee52ffd6a27ccce262509b235495cbf4feedc03e676cd968c7ace67755` | 2026-10-05 20:17:29 | plan (`_fuente_nombral`) | **no contable**: no existe entrada con ese título (la entrada vigente del plan es «…(cura B2-1, B2-1c, B2-1d, B2-1e y sello documental 2026-10-09)») | blob histórico `bb1eacd63f501c93512ffb7a5af6724d2dff1c9e` (sha256 idéntico) |
| 3 | `01a10e39-1625-71b1-8ca6-73cbdb1c6a94` | `10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre FASE-RELEASE, checkpoint documental 2026-10-05)` | `d1b8ff00b51144ad092d633fc0122d4b7c0fd5b91e6b3eabbc2879ff5ed0fc48` | 2026-10-05 17:39:44 | plan (`_fuente_nombral`) | **no contable**: ídem (título sin entrada) | blob histórico `9895a6ae21ec26542cf34940a09950553af36caf` (sha256 idéntico) |
| 4 | `01a10853-6da2-7820-b2a3-fa1cb5ccb4ba` | `10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre FASE-B, lecciones finales 2026-10-04)` | `424b5828e34145fbaff7e72bf117d4b25a777c8f4f9e30156229aaa0ace81f90` | 2026-10-04 14:10:47 | plan (`_fuente_nombral`) | **no contable**: ídem (título sin entrada) | blob histórico `5d2ade22e30b556150578f4c46eb834972107eb4` (sha256 idéntico) |
| 5 | `01a0e4d9-b252-7ca0-bf4c-9a9ecc7448f5` | `10-analisis: EVALUACION-JEV-TYPESAFE-2026-09-21 (cierre offline, lecciones finales 2026-09-27)` | `34e2a95195b2ddb44c6770d9c76cfca4bced6349320c37c48353411b9484d9b9` | 2026-09-27 16:51:07 | plan (`_fuente_nombral`) | **no contable**: ídem (título sin entrada) | **NINGUNO** (ni instantánea ni blob histórico en el conjunto medido) |

Causa de falta de contabilidad **leída del registro, no supuesta**: en los 5 casos es «no existe entrada en el registro con su título» (el registro solo admite como contable un título que figure en alguna entrada del plan). Ninguna es el caso «entrada `1.0` sin `sha_cuerpo`» (ese es el estado de las 2 entradas de REFACTOR-WHATSAPP, que sí son contables por título) ni «entrada existente con estado no vigente».

**Nota de fecha**: el listado no da fecha de publicación como tal; la columna declara `createdAt` del listado del notebook (la fuente y su metadata nacen juntas en la subida).

## 3. Cruce entre las dos poblaciones

**Medido, no creído**: las dos poblaciones son **la misma** — `5/5` ids idénticos. Los 5 ids truncados de las líneas `[DUPLICADO-VIGENTE]` del crudo (`01a0bfc9-5f5a`, `01a10ec9-8113`, `01a10e39-1625`, `01a10853-6da2`, `01a0e4d9-b252`) casan uno a uno con los 5 huéspedes recalculados desde el listado del notebook + el registro. **Solapamiento 5/5 (100%); 0 fuentes exclusivas de una lista.**

Por qué coincide, medido en el código: las líneas `[DUPLICADO-VIGENTE]` del rojo las emite `_lineas_huesped`, que es exactamente el reportero de `_huespedes_sin_contabilidad` (mismo bloque, misma población). El «rojo de duplicado» y el «contador de huéspedes» son dos etiquetas de la misma lista, no dos deudas distintas. Consecuencia para FASE-C: **una cura por fuente cierra ambas cuentas a la vez**.

## 4. Huéspedes `CONTEXT:` (D-QW-1)

- **0 de las 5 huéspedes es una fuente `CONTEXT:`** — verificado por títulos sobre el listado (0 títulos que empiecen por `CONTEXT:` entre las 5), no por creencia. Todas las 5 se atan a su plan por título.
- `scan_context_declarations()` medido **en vivo el 2026-10-22**: `0` resultados (coincide con la medición del 2026-10-15 citada por la fase). Es la copia estrecha del writer (D-QW-2): mira solo `CONTEXT-*.md` de `.opencode/context/` con marcador de autodeclaración; **no es la población gobernada** y este censo no la usó como tal.
- **Límite estructural declarado** (D-QW-1, primera cláusula de la lección): `_fuente_nombral` exige `10-analisis` en el título, así que **por construcción ninguna fuente `CONTEXT:` puede aparecer jamás en el rojo ni en el contador de huéspedes**. El notebook tiene 43 fuentes con `CONTEXT` en el título de las cuales 41 no tienen entrada en el registro; si alguna fue publicada por la rama por defecto de `--upload` (D-QW-1, sin registrar), este instrumento no la señala y este censo no puede clasificarlas. Esa población queda fuera del alcance de AC3/AC4 y sigue gobernada por la deuda diferida `D-QW-1`/`D-QW-2` (dueño Operador, §5 del maestro). No se afirma nada sobre su origen sin medirlo.

## 5. Tabla de decisión del Operador (AC4)

Respuesta del Operador registrada **en la sesión** el **2026-10-22** (intercambio de decisión por fuente de esta sesión de FASE-B; texto suyo: «(a) Marcar como reemplazada en el registro» en las 5 filas). Ninguna fila queda pendiente.

| # | Fuente (id corto) | Decisión | Fecha | Mecanismo especificado (con coste medido) |
|---|-------------------|----------|-------|-------------------------------------------|
| 1 | `01a0bfc9-5f5a…` (REFACTOR-WHATSAPP) | **(a) marcar como reemplazada** | 2026-10-22 | Ver §5.1 — primitivo nuevo `registrar_historica()` |
| 2 | `01a10ec9-8113…` (JEV FASE-RELEASE) | **(a) marcar como reemplazada** | 2026-10-22 | Ver §5.1 — ídem |
| 3 | `01a10e39-1625…` (JEV checkpoint) | **(a) marcar como reemplazada** | 2026-10-22 | Ver §5.1 — ídem |
| 4 | `01a10853-6da2…` (JEV FASE-B) | **(a) marcar como reemplazada** | 2026-10-22 | Ver §5.1 — ídem |
| 5 | `01a0e4d9-b252…` (JEV offline) | **(a) marcar como reemplazada** | 2026-10-22 | Ver §5.1 — ídem |

### 5.1 Mecanismo de la opción (a) — «marcar como reemplazada»

**Dónde se marca** (L-QW.2: la marca va en el registro, no se borra del notebook): `.opencode/qmind-writeback/registro.json`. Cada fuente gana una entrada con su **título exacto**, `estado: "reemplazada"`, `reemplazada_por` = título de la entrada vigente del mismo documento (fila 1 → «…(cierre 4.79.0, lecciones finales 2026-10-07, rutas archivadas)»; filas 2-5 → «…(cura B2-1, B2-1c, B2-1d, B2-1e y sello documental 2026-10-09)»), más `fuente_id` y el `sha_metadata` del censo como evidencia de qué se marcó.

**Evidencia de la marca**: el par título + `fuente_id` + `sha_metadata` de este censo (§2), y el par rojo-antes (`01-writeback-rojo-antes.txt`) / verde-después (crudo de FASE-C) que AC5 exige.

**Coste medido (L-CST-6: nada prometido sin medir)**:

- `registrar_publicacion()` **no puede** hacerlo tal cual: su firma es `registrar_publicacion(datos, ruta_registro, plan, titulo, archivo, fuente_id, fecha, cuerpo)`, exige `archivo` (hace `shutil.copyfile` de la instantánea) y fija la entrada como `vigente`, que metería las 5 fuentes históricas en el bucle de `verificar_contenido` (que solo recorre vigentes y exigiría `sha_cuerpo` e instantánea). Medido sobre el símbolo, no supuesto.
- Hace falta un **primitivo nuevo** en `scripts/validate_qmind_writeback.py`. **Firma propuesta** (FASE-C la escribe y corrige si el código lo pide):
  `registrar_historica(datos: dict, ruta_registro: Path, plan: str, titulo: str, fuente_id: str, sha_metadata: str, fecha: str, reemplazada_por: str) -> dict`
  — appenda una entrada con `estado: "reemplazada"` (sin `instanea`, sin `sha_cuerpo`, sin `sha256` local), que **no** entra al bucle de vigencia pero **sí** satisface el predicado de contabilidad de `_huespedes_sin_contabilidad` (medido: acepta cualquier título del plan en cualquier entrada, incluida `reemplazada`).
- **Coste en líneas y dientes** (estimado, FASE-C lo mide al escribir): ~25-40 líneas de escritura (primitivo + su CLI, p. ej. un flag `--mark-historic` del writer) + ~40-60 líneas de dientes en `tests/test_validate_qmind_writeback_escritura.py`. Dientes mínimos exigidos: (i) la entrada registrada hace contable su título — el huésped desaparece del censo; (ii) la entrada `reemplazada` **no** exige instantánea ni `sha_cuerpo` (no entra al dictamen de vigencia); (iii) idempotencia: re-mcar la misma fuente no duplica entrada.
- Alternativas descartadas y por qué (medidas): edición a mano del JSON del registro — el mecanismo queda fuera del writer y sin dientes (la fase de cura solo puede editar el registro **por el writer**, tabla de conflictos del plan); política de excepción en archivo aparte — exige código nuevo en `_huespedes_sin_contabilidad`, que hoy no tiene ningún canal de excepción.

### 5.2 Opciones no elegidas (dejadas medidas por si el Operador cambia de criterio en FASE-C)

- **(b) Borrar del notebook**: `qmind source delete --nb <id> <source_id>` existe en el CLI (medido en `qmind source --help`). Irreversible sobre contenido publicado. Respaldo medido (crudo `03-respaldos-byte-exactos.txt`): las filas **1 y 5 no tienen copia byte-exacta** ni en `.opencode/qmind-writeback/instantaneas/`, ni en el árbol de trabajo de `plans/` + `Archives/` (880 `.md` escaneados), ni entre los 43 blobs históricos de `10-analisis-post-implementacion.md` de los dos planes (`git rev-list --all --objects`) — borrarlas pierde el contenido publicado sin respaldo medido. Las filas 2, 3 y 4 sí tienen blob histórico con sha256 idéntico. **Cero código.**
- **(c) Dejar con motivo declarado**: dos mecanismos medidos — (i) la excepción vive **en el registro** (entrada con el título exacto y estado no vigente): el predicado actual de `_huespedes_sin_contabilidad` ya la cuenta como contable → el mismo primitivo de §5.1 con otro estado, cero código de predicado nuevo; (ii) la excepción vive en un archivo de política aparte: exige código nuevo en `_huespedes_sin_contabilidad` (hoy el predicado no lee ninguna política; ~15-25 líneas + dientes) y habría que declarar ruta y lector.

## 6. Cinco cortes declarados (sin commit)

1. Implementación terminada: ✅ (censo + decisiones; cero código, tal como exige la fase).
2. Verificación terminada: ✅ (`run_all_validations.py --quick` con venv canónico: **13/13 ALL VALIDATIONS PASSED**, crudo `04-quick-cierre.txt`).
3. Cierre documental: ✅ (este informe + post-ejecución 1-7).
4. Listo para revisión: ✅ (a partir de este documento).
5. Espera de autorización: ⏳ — ningún commit sin la letra del Operador y pathspec explícito (maestro §4).

## 7. Crudos de la fase

`01-writeback-rojo-antes.txt` (rojo-antes, EXIT 1, intento 1 de 1), `02-notebook-source-list.json` + `02-notebook-source-list.err` (censo del notebook, 68 fuentes), `03-respaldos-byte-exactos.txt` (medición de respaldos y blobs históricos + `scan_context_declarations()` = 0), `04-quick-cierre.txt` (quick 13/13 de cierre).
