# Write-back de cierre a QMind — FASE-RELEASE del plan REFACTOR-WHATSAPP-ENTREGA-2026-09-18

**Fecha:** 2026-10-07 · **Instrumento:** `scripts/validate_qmind_writeback.py` (writer con `--title`/`--file`,
entregado por la AC6-entrega del mini-plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20`) · **Notebook:** `iah-cli-lecciones`.

## Lo que se subió y con qué prueba de saneamiento

- **Cuerpo canónico:** `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md`,
  sha256 `3d2184fb2822f38d3b8fe97d55d565d10027373256fd63feb40fa226ee73d28e`, 124.280 B.
- **Copia saneada (la que se publica):** `qmind-upload-10-analisis-cierre-4.79.0-saneado.md` en esta carpeta.
  Siete tokens de identidad del cliente evaluados, **6 con coincidencia y sustituidos**, 3 con cero coincidencias:

  | Original | Saneado | Ocurrencias |
  |---|---|---|
  | `Hotel Don Alfonso` | `[HOTEL-CLIENTE-OMITIDO]` | 1 |
  | `Don Alfonso` | `[CLIENTE]` | 3 |
  | `https://www.donalfonsohotel.com/` | `[URL-DEL-CLIENTE-OMITIDA]` | 1 |
  | `consentimiento-donalfonso.md` | `consentimiento-[CLIENTE].md` | 1 |
  | `6063146139` | `[TELEFONO-DEL-CLIENTE-OMITIDO]` | 1 |
  | `donalfonsohotel.com` / `don_alfonso_20261007` / `Alfonso` (suelto) | — | 0 |

- **Prueba de fidelidad, no promesa:** se revirtieron las sustituciones sobre la copia (empezando por el token
  más largo, porque `[CLIENTE]` es subcadena de `[HOTEL-CLIENTE-OMITIDO]`) y el resultado reprodujo el sha256 del
  original: `3d2184fb2822…`, 124.280 B, **byte a byte**. Crudo: `crudos/saneado_post.txt` y
  `crudos/saneado_refijo.txt`.
- No hay secretos en la subida: el estado de la credencial viaja por su clave de estado, nunca por su valor
  (heredado de FASE-F), y el barrido de material de cliente del quick da `SIN_HALLAZGOS`.

## Las dos publicaciones y su estado en el registro

| # | Hora | Título | sha de la instantánea | Estado en `.opencode/qmind-writeback/registro.json` |
|---|---|---|---|---|
| 1 | 19:34 | `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (cierre 4.79.0, lecciones finales 2026-10-07)` | `0b02bb5084e3…` | `reemplazada` (con `reemplazada_por`) |
| 2 | 19:39 | `… (cierre 4.79.0, lecciones finales 2026-10-07, rutas archivadas)` | `1f0ee6e52f00…` | **vigente** |

**Segundo hallazgo del instrumento: las dos publicaciones compartieron archivo de instantánea, y la segunda
pisó a la primera.** `registrar_publicacion()` (scripts/validate_qmind_writeback.py:269) nombra la instantánea con
`re.sub(r"[^A-Za-z0-9._-]+", "_", f"{plan}--{titulo}")[:120] + ".md"`: el recorte a 120 caracteres deja **fuera** la
única diferencia entre los dos títulos (`", rutas archivadas"`), así que ambos títulos producen el mismo
`…_lecciones_finales_2.md` y `shutil.copyfile` sobrescribió la primera. Medido: el registro conserva dos entradas
con sha distintos (`0b02bb50…` y `1f0ee6e5…`) pero **un solo archivo en disco**, con `1f0ee6e5…`. Consecuencia: la
"instantánea versionada" de una publicación reemplazada no es durable: se pierde el byte-exacto que se publicó
bajo ese título. Hoy no produce rojo porque `verificar_contenido()` solo itera las entradas `vigentes`; lo haría en
cuanto alguien audite el historial. Dueño: la misma `registrar_publicacion` (el nombre debe llevar el sha o un
número de corrida). No se cura aquí: RELEASE no repara código.

**Tercer hueco menor, declarado:** la entrada vigente quedó con `fuente_id: ""` — el writer no captura el id que
devuelve `qmind source upload` (cuya respuesta es una **tabla**, no JSON), así que la verificación por descarga
depende de casar el `metadata.fileSha256` prometido por el índice, no de una identidad de fuente registrada.

La segunda se exigió porque la cabecera de la copia declaraba la ruta de raíz (`plans/<PLAN>/…`) y el `git mv`
de archivado la movió: la copia se regeneró con la ruta correcta y el writer marca la anterior como
reemplazada. **No se borró ninguna fuente**: `qmind source delete` sobre contenido publicado es irreversible y
pide decisión escrita aparte (decisión del mini-plan: marcar).

La primera invocación con `--upload REFACTOR-WHATSAPP-ENTREGA-2026-09-18` después del `git mv` falla por ruta
(`el directorio no existe`): el writer resuelve `--upload` contra `.opencode/plans/`, así que con el plan
archivado hay que pasar `--upload Archives/<PLAN>` — y `plan_dir.name` conserva la clave del plan, así que el
registro sigue indexado por `REFACTOR-WHATSAPP-ENTREGA-2026-09-18`.

## Hallazgo nuevo del instrumento: `[17/18]` es insatisfacible para un cuerpo con identidad de cliente

**Rojo medido** (crudo `crudos/writeback_check3.txt`):

```
[VENCIDO] REFACTOR-WHATSAPP-ENTREGA-2026-09-18 :: … : la instantanea publicada (0b02bb5084e3…)
          ya no casa con el cuerpo del repo (3d2184fb2822…): re-publicar con titulo nuevo
```

**Diagnóstico, con la atribución hecha midiendo y no suponiendo.** Primero se sospchó que el cuerpo había
cambiado después de publicar (el fixer `validate_opencode_refs.py --fix` imprimió una línea `10-analisis…`): **falso**.
El sha del cuerpo antes y después del fixer es el mismo (`3d2184fb2822…`) y la línea del fixer pertenecía al
`10-analisis` de otro plan, que referencia al nuestro. La causa es otra y es de diseño.

`verificar_contenido()` (scripts/validate_qmind_writeback.py:400) gobierna con:

```python
if sha_inst != sha256_de(cuerpo):   # sha(instantanea) vs sha(cuerpo del plan en el repo)
```

o sea, exige que el archivo publicado sea **byte a byte el cuerpo del repo**. Pero `--file` está documentado
para recibir la **copia saneada** («copia saneada y versionada») y el propio writer no sanea nada, así que para
cualquier plan cuyo `10-analisis` lleve identidad de cliente —el caso que este plan y FASE-G obligan a sanear—
el check **no puede dar verde sin publicar la identidad**.

**Contrafactual ejecutado** (`contrafactual_1718.py`, montaje en `tmp` que no toca el árbol, instrumento
versionado importado y llamado in-process):

| Caso | sha instantánea vs sha cuerpo | Código | Línea impresa |
|---|---|---|---|
| A — subida byte-identica al cuerpo | casan | 1 | pasa la puerta del sha y cae en la siguiente («ninguna fuente del notebook lleva el título registrado»), **no** en `VENCIDO` |
| B — subida saneada | no casan | 1 | `[VENCIDO] … la instantanea publicada (1f0ee6e52f00…) ya no casa con el cuerpo del repo (3d2184fb2822…)` |

A demuestra que la puerta es la comparada y que una subida idéntica al cuerpo la supera; B demuestra que la
subida obligatoria (saneada) la rompe. **El verde de `[17/18]` y la prohibición de subir identidades son
incompatibles tal como está escrito el check.**

**Dueño y disparador.** Dueño: el writer `verificar_contenido()` de `scripts/validate_qmind_writeback.py`
(plan `VERIFICADOR-ESCRITURA-QMIND-2026-09-20, FASE-UNICA`). Disparador: la próxima sesión que toque ese
escritor o que ejecute un cierre con identidad de cliente. Dos curas candidatas, **ninguna ejecutada aquí**
(RELEASE no repara código): (a) que el registro guarde aparte `sha_cuerpo` y `sha_publicado` y la puerta compare
lo publicado contra la *forma saneada* del cuerpo; (b) la cura de fondo que ya propuso FASE-G: un `--sanear` en
el writer, de modo que la copia sea derivada del cuerpo por el propio instrumento y el sha quede gobernable.

**Consecuencia publicada.** La corrida del modo completo que certifica este cierre sale roja en `[17/18]` por
esta causa, y FASE-RELEASE se cierra como **INCOMPLETA con el rojo listado**, no como TOTAL PASS. Lo publicado
en el notebook sí está verificado: la instantánea vigente es la copia saneada `1f0ee6e52f00…` y su contenido
casa byte a byte con el cuerpo una vez revertido el saneamiento.

## Verificación de la publicación: por metadata SÍ, por descarga NO (flake medido 3/3)

Censo del notebook `01a04d98-b7bd-778c-8441-26fdc7e35f45` con `fetch_sources()` del propio writer
(crudo `crudos/fuentes_plan_censo.txt`): **3 fuentes** nombran a este plan.

| Fuente id | Título | `metadata.fileSha256` | Tamaño |
|---|---|---|---|
| `01a118f3-ca9a-7cf8-beae-3723640007da` | … (cierre 4.79.0, lecciones finales 2026-10-07, **rutas archivadas**) | `1f0ee6e52f008e74…` | 125.198 B |
| `01a118ee-fa45-7aa1-be01-4ce7332323d4` | … (cierre 4.79.0, lecciones finales 2026-10-07) | `0b02bb5084e3a785…` | 125.072 B |
| `01a0bfc9-5f5a-783e-9492-16367bbff596` | … (lecciones aprendidas y decisiones) — era G | `87b9b6664f945ac6…` | 39.422 B |

- **Lo que se verificó:** la promesa del índice del servidor sobre la fuente vigente casa **con la instantánea
  versionada del repo** (`1f0ee6e52f00…`, 125.198 B) — es la primera vía del contrato D2.
- **Lo que no se pudo verificar:** la **descarga** del bytes. `qmind source download <id>` falló **3/3 intentos**
  con `error: QMind network request failed` (crudos `descarga_intento_*.txt`). Por el contrato D2 del hermano de
  frescura, la ausencia de observación es **NO-EVALUABLE**, nunca un veredicto: se declara aquí como límite de
  esta sesión y no como éxito de la verificación por descarga que pedía el mandato.
- **Consecuencia para el dueño del writer:** la fuente de la **era G** (`01a0bfc9…`) sigue vigente en el notebook y
  **no tiene entrada en `registro.json`** (G subió por `upload_source()` directo). El código de
  `verificar_contenido()` corta `[DUPLICADO-VIGENTE]` cuando una fuente que nombra al plan no está contable; hoy
  ese rojo no se ve porque la puerta del sha corta antes. Cuando se cure el hallazgo de arriba, esta fila será la
  que salte: hay que registrar o marcar la fuente de G con decisión escrita del operador.
