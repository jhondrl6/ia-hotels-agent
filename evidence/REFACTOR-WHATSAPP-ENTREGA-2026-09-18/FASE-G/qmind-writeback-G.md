# Write-back de QMind — FASE-G (ejecutado y verificado el 2026-09-20)

**Autorización:** textual y separada del operador, el 2026-09-20: «Ejecuta el punto 1 y también el
write-back de G». No se heredó de la consulta Q12 de esta misma fase: la consulta nunca concede
subida (`04-contrato-ejecucion.md` §1, `dependencias-fases.md` fila QMind/write-back).

## Blast radius medido ANTES de subir

| Qué | Cómo se midió | Resultado |
|---|---|---|
| Fuentes ya ingesta en el notebook | `fetch_source_titles()` del propio validador (`qmind source list --all --format json`) | 48 títulos; **0** correspondientes a este plan (el más reciente era 2026-09-15, `TRIBUNAL-ENFORCEMENT-OBS-2026-09-11`) |
| `CONTEXT-*.md` que `--upload` habría subido también | `scan_context_declarations()` importado del validador | **0 candidatos**. Existe 1 archivo en `.opencode/context/` (`CONTEXT-BUG-WHATSAPP-VERIFIED-BLOQUEO-ENTREGA-2026-09-17.md`) pero no autodeclara lección durable, así que no entra |
| ¿El plan está en raíz (requisito R2.10)? | `Path('.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18').is_dir()` | Sí — el upload tenía que correr aquí y no después del `git mv` de RELEASE |

Consecuencia: el write-back de G afecta a **un solo archivo**, el `10-analisis` del plan.

## Saneamiento aplicado (exigido por el contrato de este plan)

`04-contrato-ejecucion.md` y la tarea 3 de RELEASE ordenan revisar **qué** sube: «sin material del
hotel ni secretos». El `10-analisis` sí contenía identidad del cliente. Medido con
`re.findall('Alfonso', t, re.I)` → **5 ocurrencias en 4 líneas**; número de teléfono, `wa.me` con
destino, precios y credenciales → **0** (las dos coincidencias de `wa.me` son la mención del patrón
en prosa sobre qué detecta el lector, sin destino).

| # | Original | Saneado |
|---|---|---|
| 1 | `https://www.donalfonsohotel.com/` | `[URL-DEL-CLIENTE-OMITIDA]` |
| 2 | `deuda §6 "Procedencia del dato Don Alfonso"` | `… dato [CLIENTE]` |
| 3 | `evidence/FASE-P4/consentimiento-donalfonso.md` | `evidence/FASE-P4/consentimiento-[CLIENTE].md` |
| 4 | `hotel_name == "Hotel Don Alfonso"` | `hotel_name == "[HOTEL-CLIENTE-OMITIDO]"` |
| 5 | `3 artefactos de memoria de Don Alfonso` | `… memoria de [CLIENTE]` |

Prueba de fidelidad, no promesa: cada sustitución se aplicó con `assert count(old) == 1` sobre
**bytes**; al final se invirtieron las cinco sobre la copia y el resultado reprodujo el sha256 del
original (`7077f3ac10fe9489a9eaa4a9befe729b1b50b76a82e27d95a642ff12032bb478`, 38.803 B). La copia
saneada quedó en `qmind-upload-10-analisis-saneado.md` (39.422 B, sha256
`87b9b6664f945ac6279f1efaf9aa7682cac8a1c952e633bfc4ff55ce67a49274`) con una cabecera que declara que
no es el documento canónico. Tras el saneamiento, `Alfonso` → 0 coincidencias en el archivo subido.

## Desviación del comando canónico, y por qué

Se ejecutó **`upload_source()` del validador con la copia saneada** en lugar de
`validate_qmind_writeback.py --upload REFACTOR-WHATSAPP-ENTREGA-2026-09-18`. Motivo medido en el
código: `do_upload()` resuelve `plan_dir / 10-analisis…` y `upload_source()` lanza
`qmind source upload --nb … --file … --title …` **sin ningún reescritor** — es decir, el comando
canónico habría publicado las 5 identidades que el contrato de este plan prohíbe subir. Se conservó
el mismo canal, las mismas banderas verificadas (L-VUP-9) y **exactamente el mismo título** que
`do_upload()` habría generado, para no romper `is_ingested()`:

```
10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (lecciones aprendidas y decisiones)
```

Queda registrado como límite del writer, con dueño RELEASE/operador: `--upload` no sanea, así que en
este repo su uso directo sobre un `10-analisis` de plan con cliente nombrado sube identidad.

## Resultado y verificación

| Campo | Valor medido |
|---|---|
| Source ID | `01a0bfc9-5f5a-783e-9492-16367bbff596` |
| Notebook | `01a04d98-b7bd-778c-8441-26fdc7e35f45` (`iah-cli-lecciones`) |
| Estado | `ready` (creado 2026-09-20T17:07:20.538537Z, actualizado 17:07:25.38724Z) |
| Títulos tras la subida | 48 → **49** |
| `is_ingested(plan, titles)` | **True** |
| **Verificación por contenido, no por título** | `qmind source download <id> --nb <nb>` devolvió **39.422 B idénticos** y sha256 `87b9b666…49274` **igual** al de la copia local; el archivo temporal de comprobación se borró y `git status` no quedó con restos |

La verificación por descarga es la que vale: `SKIP por título` solo prueba que *un* título existe, no
que el contenido publicado sea el de esta fase — y en el notebook ya conviven dos fuentes del mismo
plan TRIBUNAL-OFFLINE con contenidos distintos.

## Límite: nada de esto está gateado

> **Esta sección estaba mal y se rectifica el mismo día.** La medición que la originó fue
> `grep -rln "validate_qmind_writeback" … | head -20`, y el `head` se comió el resultado: `scripts/`
> aparece después de `.agents/` y `.opencode/` en el orden del grep. Re-medido sin corte, el
> validador **sí** está invocado: `scripts/run_all_validations.py:97` lo corre como check **[15/15]**.

Los límites reales, leídos en el código de los dos archivos:

- **[15/15] solo existe en el modo completo.** Dentro de `if not self.quick:`, así que la validación
  rápida de todas las fases intermedias nunca lo ve. Tampoco está en `scripts/git_hooks/pre-commit`.
- **Escanea solo `.opencode/plans/Archives/`** (`collect_archived_analisis()`): con el plan en raíz no
  hay verde ni rojo, como sucedió durante toda esta sesión.
- **Degrada a exit 0 si el CLI `qmind` no está disponible**, porque el check lo invoca sin `--strict`
  (`run_all_validations.py:827`). Es un verde producido por la ausencia del instrumento.
- **Decide por título** (`is_ingested()`): la fuente de la era G satisface el check para siempre, de
  modo que un contenido obsoleto pasa por cierre publicado.

Consecuencia: el hueco no es «no hay verificador», es «el verificador comprueba la clave y no el
contenido, y solo en un modo que nadie corre a mitad de plan». Eso es lo que el mini-plan
`VERIFICADOR-ESCRITURA-QMIND-2026-09-20` ataca.

## Precedente observado, registrado y no corregido aquí

El notebook contiene desde antes fuentes con nombres de otros clientes (`SalenteReal`, `Luxor`,
`Zione`, en títulos `CONTEXT: …` de 2026-08-29 y 2026-09-03/04). El saneamiento de G no altera eso.
Es exposición preexistente con dueño operador; sacarla del notebook es una decisión aparte, no parte
de FASE-G.

## Lo que RELEASE debe hacer distinto (pre-acordado aquí)

1. Subir con **título nuevo**, porque el de G ya existe y `--upload` respondería SKIP dejando el
   contenido de la era G publicado como si fuera el cierre:
   `10-analisis: REFACTOR-WHATSAPP-ENTREGA-2026-09-18 (cierre <versión final>, lecciones finales <fecha>)`.
2. Correr el write-back **con el plan aún en raíz**, antes de `build_lesson_index.py` y del `git mv`
   (orden fijo R2.10).
3. Volver a sanear (el `10-analisis` habrá cambiado) y volver a verificar por descarga + sha.

## Límite del writer, medido en su propio `main()`

`validate_qmind_writeback.py` **no expone `--title` ni `--file`**: el título se construye fijo como
`10-analisis: <PLAN> (lecciones aprendidas y decisiones)` y la ruta se deriva de `plan_dir`. Como
`is_ingested()` decide **por título**, la ingesta de RELEASE respondería `SKIP` y dejaría visible en
el notebook el contenido de la era G como si fuera el cierre. La idempotencia que protege contra
duplicados es exactamente la que produce la obsolescencia silenciosa, y el único check que podría
verla —[15/15] de la validación completa— decide por título, así que también la da por buena. Su
modo verificación, además, solo mira `Archives/`.

- **Esquive usado por G:** subir por el mismo canal (`upload_source()` del validador) una copia
  saneada y con el título canónico, de modo que `is_ingested()` siga siendo verdadero.
- **Cura de fondo, con dueño (productor del writer / operador):** `--title`, `--file` o `--sanear` y
  verificación por descarga en lugar de por título.
- **Consecuencia registrada en el plan:** fila nueva en «Seguimientos abiertos» del `10-analisis` y
  condición 1 del prompt de RELEASE.

## Deriva conocida entre la instantánea subida y el documento canónico

La subida corresponde al `10-analisis` en su estado de cierre de G (sha256
`7077f3ac10fe9489a9eaa4a9befe729b1b50b76a82e27d95a642ff12032bb478`). Después de la ingesta se le
añadió **una fila** en «Seguimientos abiertos» (el límite del writer), que llevó el sha del canónico
de `7077f3ac…` a `7cb88b51e7df05f5cf7e038509ea112b94dcf8b9fab2476b60952388c569533d`. No se re-subió:
`--upload` habría respondido SKIP por el título existente, y re-ingerir ahora exigiría negociar el
título de RELEASE antes de tiempo. La regla queda escrita para que la ingesta final cubra la deriva.

## Alcance de este propio registro

Las cinco cadenas originales aparecen **literalmente** en la tabla de arriba. Es deliberado: este
archivo vive en `evidence/` y no es un insumo del writer —`do_upload()` solo toma el `10-analisis` y
los `CONTEXT-*.md` autodeclarados—, de modo que nombrarlas aquí no las publica. Si algún día este
directorio se convirtiera en material de subida, esta tabla sería el primer sitio que hay que sanear.
