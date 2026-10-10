# Lecciones capitalizadas — CURA-BLOQUE-HUESPED-QMIND-2026-10-10

**Estado: Paso 0 ejecutado el 2026-10-10**, en la misma sesión que concibió el plan y abrió FASE-1. Las siete
consultas de §1 son reales, con su comando y su resultado medido; lo que aquí no hay es código: ninguna línea de
este plan estaba implementada al escribir este archivo.

**Fuente de partida:** el mandato del operador del 2026-10-10 y el §7 del acta de diagnóstico
`evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/00-acta.md`, que dictaminó con medición el hueco y dejó su cura
como mandato de una fase futura. Ese acta llama al AC «AC-N.1»; este plan lo instancia como **AC-N1** porque el
token que reconoce el validador de capitalización no admite el punto (medido en §1, Q8).

## 1. Consultas ejecutadas

| # | Capa | Consulta literal | Resultado |
|---|---|---|---|
| Q1 | QMind, notebook `iah-cli-lecciones` — capa corpus-wide | `mcp__plugin_qoder-qmind_qoder-qmind__retrieve` con `notebookId` `01a04d98-b7bd-778c-8441-26fdc7e35f45`, consulta «bloque huésped DUPLICADO-VIGENTE sin contabilidad, continue del bucle de verificar_contenido, contador de fuentes huésped que varía según la descarga», `maxResults 5` | **Lector fallido, no ausencia**: respondió `knowledgeBaseAccountListFailed`. Un intento, sin reintentos (restricción de la sesión de diagnóstico heredada). Se publica el motivo y no un cero (R2.9). La capa QMind queda **sin observación** en este Paso 0 y se declara en §4 |
| Q2 | Índice de lecciones en memoria | `validate_lesson_capitalization.duenos_del_corpus(Path('.opencode/plans'), Path('.opencode/context'))` | **374** IDs con dueño real. `S-CIM-9` y `DA-CIM.9` están en `citados_sin_definicion` y **no** definidos: no son capitalizables en §2 (C7 los cortaría) y quedan como prosa del maestro §5 |
| Q3 | Índice generado (JSON) | `json.loads(Path('.opencode/lecciones_index.json').read_text())['lecciones']`, leyendo `plan`, `archivo` y `seccion` de cada ID | Dueño, ruta y sección de las cinco filas de §2 tomados de aquí, no de memoria (método Q6 del precedente `Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20`) |
| Q4 | Repo, código vivo | `re.findall` de `\[CONTADOR\]`, `fuente\(s\) huesped\(s\)` y `\d+\+\d+\+\d+==\d+` sobre los **466** `.py` de `tests/` y `scripts/` | El literal del contador vive en **2 archivos**: su productor `scripts/validate_qmind_writeback.py` (3 ocurrencias) y su familia de tests (8). **15** líneas de aserción o comparación. Esta es la medición que decide el coste de AC-N2 |
| Q5 | Corpus de planes archivados | `grep -rn "S-CIM-9" .opencode/plans/Archives/` | **4** coincidencias en 2 archivos de `Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07`: la fila de deuda de su maestro §5 y las filas H-5, H-8 y §Deuda de su análisis. **Ninguna nombra la rama de la bajada fallida** |
| Q6 | Evidencia de la sesión de diagnóstico | Lectura de `evidence/DIAGNOSTICO-HUESPEDES-JEV-2026-10-10/00-acta.md` con sus crudos `03-censo_solo_lectura.txt` y `04-repro_offline_2x2.txt` | Censo vivo en una sola llamada: 64 fuentes, 5 nombran al plan JEV. Matriz offline: con censo idéntico, la sola respuesta de `source download` mueve el contador de 5 a 1 huésped y el EXIT de 1 a 2 |
| Q7 | Repo, familia de tests | Conteo por función de `tests/test_validate_qmind_writeback_escritura.py` | **57** funciones; **12** ejercitan la huésped; **1** ejercita la bajada que falla; **intersección 0** |
| Q8 | Repo, contrato del validador | `grep -n "AC_TOKEN_RE" scripts/validate_lesson_capitalization.py` | `\bAC-?[A-Z]{0,2}\d+\b`: admite `AC-N1` y **no** admite `AC-N.1`. De ahí el renombrado declarado arriba |

## 2. Lecciones capitalizadas

| ID | Enunciado | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|---|---|---|---|---|
| L-QW.4 | Un límite conocido y escrito no se cierra solo: la restricción estaba documentada en el corpus y se redescubrió desde cero porque ningún AC la reclamaba y ningún check la violaba. | `.opencode/plans/Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/10-analisis-post-implementacion.md`, §E | **AC-N1**: la familia de los `continue` ya estaba declarada como deuda (`S-CIM-9`), pero solo su miembro `VENCIDO` por cuerpo tenía diente de caracterización; el miembro de la bajada fallida no lo reclamaba nadie y lo redescubrió un diagnóstico. Este plan es el AC que faltaba | `verificar_contenido()` y su familia de tests |
| L-QW.2 | Publicar con título distinto resuelve el SKIP y crea el duplicado: el notebook conserva la versión obsoleta y el retrieve la devuelve puntuada por parecido, no por vigencia. | `.opencode/plans/Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20/10-analisis-post-implementacion.md`, §E | **AC-N1**: las cuatro fuentes huésped del plan JEV son exactamente esos duplicados. Si el bloque que los cuenta no se recorre, el instrumento pierde de vista el efecto que su propio corpus documentó | `_huespedes_sin_contabilidad()` y `_lineas_huesped()` |
| DA-C3 | `vacío ≠ ausente` como contrato: un valor por defecto no puede servir a la vez para «resuelto, cero brechas» y para «sin fuente». | `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md`, §6 Decisiones Arquitectónicas | **AC-N2**: el `[CONTADOR]` publica hoy `0 fuente(s) huesped(s)` tanto cuando midió como cuando el flujo no llegó al bloque. El denominador de observación separa los dos estados (R2.9) | la línea `[CONTADOR]` que cierra `verificar_contenido()` |
| L-D5 | Un instrumento de medición sin verificar devolvió cero y casi se reporta como resultado. | `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md`, §8 Lecciones Aprendidas | **AC-N2**: el denominador no se imprime como constante ni se deriva de `len(vigentes)`; se cuenta en el sitio donde el bloque corre, para que un `continue` nuevo lo baje y un diente lo vea | el `contador` de `verificar_contenido()` |
| L-ENT.12 | El verde del verificador no probaba su propia cobertura: el hueco estaba en su resolutor y lo delató una cuenta que no cuadra. | `.opencode/plans/Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md`, §Lecciones nuevas de este plan | **AC-N1 y AC-N2**: ambos se cierran con mutation check (R2.8, dos salidas en evidencia) y con la cobertura medida (intersección 0 de 57), no con un test que confirme lo que ya pasaba | `evidence/CURA-BLOQUE-HUESPED-QMIND-2026-10-10/FASE-1/` |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO se capitaliza como tarea de este plan |
|---|---|
| L-PF6 | Es el origen histórico de R2.9 (un JSON-LD en ARRAY tragado como ERROR y publicado como «cero schemas»). Su superficie es el parser de schema del pipeline, no el flujo del bucle de un verificador documental. Se cita como antecedente del contrato que AC-N2 aplica, no como tarea |
| L-PF10 | Mismo contrato, otro sitio: `critical_recall` BLOCKED porque la lista estaba vacía tras un fix que funcionó. Descartada porque su superficie es el extractor de métricas del pipeline; aquí el equivalente ya está gobernado por AC-N2 |
| L-V3.1 | Documentar un gate que no corre enseña a no verificarlo. Descartada como tarea: este plan **no mueve** dónde corre el check (sigue en el modo completo de `run_all_validations.py`, rama de no-quick); solo declara en el maestro §4 dónde es observable |
| L-R.4 | Una regla sin verificador declara su límite. Se aplica como **política** de este Paso 0 (§4) y del maestro, pero no es tarea: los dos AC de este plan nacen con diente y mutante, así que no hay regla nueva sin verificador que declarar |
| L-QW.3 | Un verde producido por la ausencia del instrumento es un rojo disfrazado. Ya curado por el plan hermano (`Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20`, AC3): la ausencia del CLI corta FAIL con `--strict`. Re-abrirla aquí sería re-escribir una cura cerrada |

## 4. Cobertura declarada y límites

Se capitalizan **cinco** lecciones preexistentes con dueño real y ruta tomada del índice (Q3), procedentes de
**tres** planes distintos (`Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20`,
`Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03`, `Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18`), y se
descartan **cinco** candidatos con motivo, sobre siete consultas repartidas en cinco capas: QMind (Q1), índice en
memoria (Q2), índice generado (Q3), código vivo del repo (Q4, Q7, Q8), corpus archivado (Q5) y evidencia de la
sesión de diagnóstico (Q6).

**Límite de instrumento, declarado:** `scripts/validate_lesson_capitalization.py` **no verifica** la pertinencia de
lo capitalizado —no puede saber si una lección debía aplicarse ni si el efecto alegado es real—, solo la forma:
presencia, secciones, consulta al corpus con comando, AC existente en el maestro, número de descartes, límite
declarado, atribución y pluralidad de dueños. Este archivo cumple la forma y no reclama más.

**Límite de cobertura de este Paso 0:** la capa QMind quedó sin observación (Q1, lector fallido). Las lecciones de
§2 salen del corpus versionado y del índice, que sí respondieron; si una lección relevante viviera solo en el
notebook, este Paso 0 no la habría visto. Se declara en lugar de reintentar en bucle.
