# Lecciones capitalizadas — VERIFICADOR-ESCRITURA-QMIND-2026-09-20

**Estado: Paso 0 ejecutado el 2026-09-20**, en la misma sesión que concibió el mini-plan. Las seis consultas
de §1 son reales, con su comando y su conteo; lo que aquí no hay es código, porque ninguna línea de este
plan se ha implementado.

## 1. Consultas ejecutadas

| # | Capa | Consulta literal | Resultado |
|---|---|---|---|
| Q1 | QMind, notebook `iah-cli-lecciones` — capa corpus-wide | `mcp__plugin_qoder-qmind_qoder-qmind__retrieve` nb `01a04d98-…`, consulta: «write-back QMind del 10-analisis al cerrar la fase: idempotencia por titulo, SKIP, verificador de ingesta, archivado», `maxResults 5` | 5 fragmentos. El de mayor puntaje (**0,95**) es el checklist de cierre de `TRIBUNAL-OFFLINE-2026-09-09`, que ya dice en el corpus: «el script **no tiene vía de actualización** (`source upload` no admite sobrescribir; `is_ingested` corta por título ⇒ `[SKIP]`) … el notebook queda con **dos versiones** de la misma fuente» |
| Q2 | Corpus de planes archivados | `grep -rn "título distinto" .opencode/plans/Archives/` | **1** coincidencia: el `10-analisis` de `TRIBUNAL-OFFLINE-2026-09-09`, sección del checklist de FASE-RELEASE |
| Q3 | Código + contratos | `grep -rln "is_ingested\\|no tiene vía de actualización\\|título distinto" scripts/ .agents/ .opencode/plans/` | **5** archivos: el validador, su contract test, el workflow y dos documentos de plan |
| Q4 | Índice generado | `grep -c "L-QW" .opencode/LECCIONES-INDEX.md` | **0** — la serie `L-QW.1` a `L-QW.4` está libre y se reserva en §3bis |
| Q5 | Notebook real, no manifest | `fetch_source_titles()` de `validate_qmind_writeback.py` (envuelve `qmind source list --nb … --all --format json`) | **49** fuentes; **2** corresponden a `TRIBUNAL-OFFLINE-2026-09-09` (una de 2026-09-10 tomada a mitad de plan y la de cierre del 2026-09-11) |
| Q6 | Índice en memoria, no el JSON de salida | `build_lesson_index.build(pathlib.Path('.opencode/plans'))` y lectura de `plan`, `archivo` y `seccion` de cada ID | Dueños reales de las seis filas de §2, usados para escribir «Definida en» con ruta y sección, no de memoria |

## 2. Lecciones capitalizadas

| ID | Enunciado | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|---|---|---|---|---|
| L-D5 | Un instrumento de medición sin verificar devolvió 0 y casi lo reporto como resultado. | `.opencode/plans/Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03/10-analisis-post-implementacion.md` §8 | **AC3**: la ausencia del CLI `qmind` no puede seguir produciendo PASS; el modo completo tiene que distinguir «medido en verde» de «no medible» | `_check_qmind_writeback()` y el resumen de `run_all_validations.py` |
| L-V3.1 | El pre-commit no invoca `run_all_validations.py`, así que un guard declarado «conectado» puede no correr nunca en el ciclo real. | `.opencode/plans/Archives/PASO0-VERIFICADOR-CAPITALIZACION-2026-09-12/10-analisis-post-implementacion.md` §2 | **AC2** y **AC3**: este verificador vive solo en el modo completo; el plan debe decir dónde corre y qué lo invoca, no solo que existe | la cola de `run()`, rama `if not self.quick:` |
| L-ENT.9 | Un proveedor configurado no es un proveedor ejercitado: la métrica agregada verde oculta qué rama corrió. | `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md`, «Lecciones nuevas de este plan» | **AC2**: el verde agregado «hay fuente con ese título» oculta qué contenido se ingirió; la verificación pasa a por contenido | `is_ingested()` → comparación de contenido |
| L-ENT.12 | El verde del verificador no probaba su propia cobertura: el hueco estaba en su resolutor, y lo delató una cuenta que no cuadra. | `.opencode/plans/REFACTOR-WHATSAPP-ENTREGA-2026-09-18/10-analisis-post-implementacion.md`, «Lecciones nuevas de este plan» | **AC5**: los tres rojos nuevos se demuestran por mutación del guard, no por un test que confirme lo que ya pasaba | `mutation_report.json` del mini-plan |
| L-AJUST.1 | Un plan citaba como viva una verdad que un rebase y un push posteriores invalidaron; las citas de estado se escribieron en presente y nadie las contra-verifica. | `.opencode/plans/Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11/10-analisis-post-implementacion.md`, «Lecciones Aprendidas» | **AC4** y **AC6**: el «título pre-acordado» es un estado en prosa que caduca; tiene que vivir en el writer y en el check, no en un párrafo que RELEASE memorice | prompt de FASE-RELEASE del plan padre |
| L-R.4 | Una regla sin verificador declara expresamente su límite. | `.opencode/plans/Archives/TRIBUNAL-OFFLINE-2026-09-09/10-analisis-post-implementacion.md`, FASE-RELEASE-4.76.0 | §4 de este archivo y el límite de alcance del AC4 (borrar contenido publicado es irreversible y queda fuera sin decisión del operador) | Cobertura declarada |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO se capitaliza como tarea de este plan |
|---|---|
| L-ENT.14 | Nace y muere en el plan padre: es una regla de **cómo medir ausencias** (el `head` que recortó la prueba), no de escritura a QMind. Se cita como origen del mini-plan, no como alcance. |
| L-H2 | Dos actores reescribiendo el mismo archivo es una condición de carrera. Este plan es de una sesión sin delegación paralela: no hay reparto que gobernar. |
| L-B4 | Dos planes pueden compartir nombre de carpeta de evidencia. **Descartada** porque este mini-plan aún no genera evidencia; si la genera, su aislamiento por nombre de plan ya está resuelto en el repo. |
| L-B3 | Un presupuesto sin instrumento no restringe nada, y un instrumento sin corte definido mide una foto. **Descartada como tarea de este plan**: su superficie es el presupuesto de fases, y aquí no se redefine R2 ni su corte; se hereda tal como está en el contrato del plan padre. |
| L-PF11 | Reutilización de análisis previo por `canonical_url`. Mismo sabor de caché que caduca, pero su superficie es el cacheo de corridas en `main.py`, no la ingesta de documentos. |

## 3bis. Lecciones definidas por este plan

Serie reservada con Q4 (0 coincidencias en el índice al momento de la reserva). Se definen aquí y quedarán
redactadas en el `10-analisis-post-implementacion.md` de este plan al cerrar su fase, que es donde el índice
las cuenta como definición.

| ID | Enunciado provisional | Qué previene |
|---|---|---|
| L-QW.1 | Un verificador que comprueba la **clave** de una operación no puede detectar que el contenido detrás de esa clave es viejo: idempotencia y frescura son dos propiedades, y aquí solo está implementada la primera. | AC2 |
| L-QW.2 | Publicar con título distinto resuelve el SKIP y **crea** el duplicado: el notebook conserva la versión obsoleta y el retrieve la devuelve puntuada por parecido, no por vigencia (medido: 2 de 49 fuentes para un mismo plan). | AC4 |
| L-QW.3 | Un verde producido por la ausencia del instrumento es un rojo disfrazado. | AC3 |
| L-QW.4 | Un límite **conocido y escrito** no se cierra solo: esta restricción está documentada en el corpus desde 2026-09-11 y se redescubrió desde cero el 2026-09-20, porque ningún AC la reclamaba y ningún check la violaba. | el disparador y AC6 |

## 4. Cobertura declarada y límites

Se capitalizan **seis** lecciones preexistentes con dueño real y ruta (cinco planes distintos, exigencia de
dos fuentes mínima satisfecha) y **cinco** candidatos descartados con motivo, sobre tres capas corpus-wide:
QMind con `retrieve` (Q1), índice generado (Q4), índice en memoria (Q6), más los planes archivados y el
código vivo (Q2, Q3). La consulta Q1 se formuló por el **eje de escritura/ingesta**, no por el síntoma del
plan padre: eso es lo que trajo el antecedente de 2026-09-11 que la formulación por síntoma no había traído.

**Límite, que nombra a su verificador:** `validate_lesson_capitalization.py` comprueba forma y trazabilidad
—estructura §1–§4, una consulta corpus-wide con su comando, un AC existente nombrado en §2, descartes con
motivo, atribución real de cada ID y ≥2 fuentes— y **no verifica pertinencia**: no puede saber si L-D5 era
la lección que había que capitalizar, ni si el efecto asignado en «qué cambia» es verdadero. Un `[OK]` aquí
significa «la forma exigida está», nunca «capitalicé bien». La frescura del par
`.opencode/LECCIONES-INDEX.md` + `lecciones_index.json` la cubre `build_lesson_index.py --check`, que tampoco
mide calidad del diseño.
