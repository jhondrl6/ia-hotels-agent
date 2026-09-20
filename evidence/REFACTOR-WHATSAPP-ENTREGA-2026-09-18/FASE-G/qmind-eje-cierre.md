# FASE-G — Reintento de QMind por el eje de CIERRE (no por el síntoma)

**Nota:** nb `01a04d98-b7bd-778c-8441-26fdc7e35f45` · **Fecha:** 2026-09-20 · **Herramienta:** `mcp__plugin_qoder-qmind_qoder-qmind__retrieve`

## Consulta ejecutada (eje de la superficie, formulada como manda `00` §1ter)

> Eje declarado por el mandato: AST, kwargs, callers, firma, discover, verificador.
> **No** las palabras del síntoma («WhatsApp», «promesa», «botón»), que fue el eje de Q3/Q4 y
> produjo tres resultados que no tocaban el cierre.

```
mcp__plugin_qoder-qmind_qoder-qmind__retrieve
  notebookId = 01a04d98-b7bd-778c-8441-26fdc7e35f45
  query      = "verificador AST descubrimiento de poblacion de callers sin lista fija
               kwargs obligatorios firma de funcion discover check en run_all_validations
               falsos verdes allowlist de archivos"
  maxResults = 6
```

**Resultado: PERMITIDA Y RESPONDIDA** (operationId `0da622f4-14e6-4455-a048-336e09e6fdc0`,
6 chunks, score 0,38–0,51). La denegación de la revisión 2 (Q9) **no se repitió**, tal como
anunciaba la fila Q11 de FASE-A: *una denegación de permiso es un estado de la sesión, no del
sistema*. Segundo dato del mismo eje: **el eje cambia lo que aparece** — Q11 buscó
presencia/cuarentena y trajo 6 aportes distintos de estos; esta consulta trajo 6 filas del
mismo corpus que ninguna consulta previa había traído.

## Aportes recibidos y qué cambiaron en esta fase

| # | Fila traída (fuente) | Qué dice | Efecto medible en G |
|---|---|---|---|
| G1 | `L-V2.1` (PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12 §2) | Un test que solo mira **qué check** disparó puede quedar verde por otra rama del mismo check; anclar la aserción al **mensaje** | Los rojos de AC7/AC16 no asertan «hubo violación»: asertan `tipo` **y** el texto del detalle (`"whatsapp_html_detected" in detalle`, `"AssertionError: []"` en M6). Sin esto, M2/M3/M6 podían quedar verdes por otra rama |
| G2 | `L-V2.2` (mismo §2) | Un verificador no debe apoyar su conclusión en un artefacto generado por **otro** gate; calcular en memoria y fallar con nombre propio (`LECTOR-FALLIDO`) | El check del quick **recalcula el árbol en memoria** en cada corrida; lee el JSON publicado solo como salida para humanos, nunca como insumo. Y `exit 2` se reporta como `READ_ERROR` explícito, no como verde ni como 0 hallazgos (`test_los_tres_estados_del_lector_de_reporte`) |
| G3 | `L-V2.3` (mismo §2) | Antes de cambiar un artefacto, ir a los tests que asertan **sobre ese artefacto**; si uno pina una etiqueta de numeración, atarlo a la coherencia interna y no al valor literal | **Evitó un rojo silencioso.** `tests/test_validate_lesson_capitalization.py` pineaba `[10/10]`; añadir el check 11 lo habría roto sin relación con el guard, y el precedente de esa trampa (`test_registrado_como_check_5_en_el_hook`, rojo dos commits sin declarar) está en la propia fila. G reescribió ese test a coherencia estructural derivada de `run_all` (ver §5 de `resultados-y-observaciones.md`) |
| G4 | `L-V3.1` (mismo §2) | Documentar un gate que no corre enseña a no verificarlo: el hook versionado **no** invoca `run_all_validations.py` | Límite declarado en el reporte y en CHANGELOG: conectar el check a `--quick` **no** lo pone en el pre-commit. G no tocó hooks (prohibido por el contrato de fases intermedias); lo que el verificador gobierna es la corrida de validaciones, no cada commit |
| G5 | `L-V3.2` (mismo §2) | Un gate que compara contra «hoy» no informa nada | Ya resuelto por A en `d7ff932` (ancla `date` en `VERSION.yaml`); G lo confirmó midiendo 10/10 al abrir sin tocar el check |
| G6 | `L-VUP-7` (VALIDADOR-URL-PROPIA §lecciones) | Un `raise` dentro de `main.py` puede ser tragado por sus `except Exception` (patrón never-block) | Relevante para AC20, no para G: el verificador corre como proceso hijo del runner de validaciones, no dentro del pipeline, así que ningún `except` de `main.py` puede silenciarlo. Registrado como **no aplicable a esta fase** para no inflar la fila |

## Qué NO trajo la consulta (límite, para que la fila siguiente no lo dé por cubierto)

Ninguna fila del corpus remoto define un verificador AST preexistente ni una convención de
`wiring_report.json`: los seis aportes son de **disciplina de verificadores** (a qué asertar,
dónde no apoyarse, qué declarar), no de mecanismo. El mecanismo se escribió en esta fase desde
cero. Consecuencia: el diseño del AST y la política de señales son **responsabilidad de G**, sin
antecedente que citar, y VERIFY debe juzgarlos por su cobertura medida (población, huecos
publicados), no por conformidad con una práctica previa del repo.

## Registro de la denegación, por si acaso

No hubo denegación que registrar en esta sesión. Si una próxima sesión la recibe, la lectura de
`00` §4 sigue vigente: reintentar en la sesión siguiente, no dar el corpus por agotado.
