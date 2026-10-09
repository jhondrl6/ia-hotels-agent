# Documentación post-proyecto — CURA-INSTRUMENTOS-QMIND-S15 (2026-10-07)

Acumulador canónico de métricas por fase. **Este archivo es la fuente del número**: README, `10-analisis` y el
CHANGELOG lo **referencian**, no lo re-transcriben (executor, proceso común del bloque B). Creado en la preparación
con estructura vacía; cada fase llena sus filas al cerrar, con lo que midió, no con lo que esperaba.

Unidades declaradas: «funciones `def test_`» se cuenta con el método canónico del repo
(`grep -cE "^\s*def test_" <archivo>`), «casos collectados» con pytest, y **no son comparables** entre sí.

## Sección A: Módulos nuevos

| Módulo | Archivos | Descripción | Fase |
|---|---|---|---|
| — (ningún módulo nuevo; el plan cura instrumentos existentes) | | | |

## Sección B: Funcionalidades nuevas

| Feature | Módulo | Descripción | Fase |
|---|---|---|---|
| Identidad de cuerpo en el registro de publicaciones (`sha_cuerpo`, schema 1.1) | `scripts/validate_qmind_writeback.py` | Separa «el plan cambió» de «lo publicado casa con el servidor»; migración sin back-fill | ✅ A1 (2026-10-08) |
| Puerta de vigencia cuerpo contra cuerpo | `scripts/validate_qmind_writeback.py` | `verificar_contenido()` dicta VENCIDO solo contra `sha_cuerpo`; conserva el gate de registro y el contrato D2 | ✅ A1 (2026-10-08) |
| [CONTADOR] de las dos preguntas en el resumen del verificador | `scripts/validate_qmind_writeback.py` | Publica cuántas entradas se dictaminaron por cuerpo, cuántas tuvieron fidelidad remota medida y cuántas quedaron NO-EVALUABLE, con su suma | ✅ A1 (2026-10-08) |
| Nombre de instantánea sin colisión | `scripts/validate_qmind_writeback.py` | `slug_de_instantanea()`: prefijo legible + huella `--<16 hex>.md` reservada al final del presupuesto de 120; dos publicaciones del mismo plan dejan dos byte-exactos y ningún nombre puede ser `README.md` | ✅ A2 (2026-10-08) |
| `fuente_id` capturado de la tabla del CLI | `scripts/validate_qmind_writeback.py` | `fuente_id_de_tabla()` (tabla `Key: value`, valor gobernado por `ID_RE`) llamado en **las dos** ramas por `publicar_en_registro()`; ante fallo, `verificar_por_censo()` con sus tres estados y **cero re-subidas** | ✅ A2 (2026-10-08) |
| Rutas con el plan archivado fijadas por diente | `scripts/validate_qmind_writeback.py` | `Archives/<PLAN>` publica con clave `plan_dir.name`; `cuerpo_del_plan()` resuelve dos raíces | ⬜ A3 (futura) |
| Dictamen de la fuente de la era G | notebook `iah-cli-lecciones` + registro | `[DUPLICADO-VIGENTE]` con id, título y sha, declarado con dueño; nada borrado | ⬜ A3 (futura) |
| Bloque huésped gobernado también en el camino de migración | `scripts/validate_qmind_writeback.py` | `_huespedes_sin_contabilidad(datos, fuentes, plan)` llamada antes del `continue` de la guarda de migración, sin levantar la capa D2 para entradas `1.0` (decisión del operador del 2026-10-08; especificación en el prompt de A3, subtarea 3b) | ⬜ A3 (futura) |
| Control S15 estabilizado con diente intacto | `tests/test_build_lesson_index_s15_fecha_versionada.py` | La divergencia esperada queda gobernada sin re-anclar el control ni debilitar la aserción | ⬜ B (futura) |
| Cura de clasificación en el generador (condicional) | `scripts/build_lesson_index.py` | Solo si AC7 la exige; con su mutación y sus baterías | ⬜ C (condicional) |

## Sección D: Métricas acumulativas — **aquí vive el número**

| Métrica | Valor | Unidad e instrumento | Fase |
|---|---|---|---|
| Funciones `def test_` en `tests/test_validate_qmind_writeback_escritura.py` | 23 → **31** → **43** | `grep -cE "^\s*def test_"` sobre el archivo — 23 **medido 2026-10-08 en la preparación** (línea base, no producto del plan), 31 al cerrar FASE-A1 y 43 al cerrar FASE-A2. La cifra **commiteada** se mide sin tocar el árbol con `git grep -c -E "^\s*def test_" HEAD -- tests/test_validate_qmind_writeback_escritura.py` | Preparación / ✅ A1 / ✅ A2 |
| Tests nuevos de cada fase | A1: **8** | resta comprobada sobre la **misma** selección y el mismo intérprete: POST `31 passed` − PRE `23 passed` = 8; crudos `E/FASE-A1/tests_baseline_pre.txt` (EXIT 0) y `tests_baseline_post.txt` (EXIT 0) | ✅ A1 |
| Regresión de la familia vecina al cerrar A1 | `90 passed`, `EXIT=0` | `venv/Scripts/python.exe -m pytest tests/test_verify_qmind_context_freshness.py tests/quality_gates/governance_numbers -q`; crudo `E/FASE-A1/hermanos_regresion.txt`, árbol: primero el worktree y repetido sobre el árbol del commit `63b944a` (L-VCF-15) | ✅ A1 |
| Tests nuevos de cada fase | A2: **12** | resta comprobada sobre la **misma** selección y el mismo intérprete: POST `43 passed` − PRE `31 passed` = 12; crudos `E/FASE-A2/tests_baseline_pre.txt` (EXIT 0) y `tests_baseline_post.txt` (EXIT 0). Los 31 dientes viejos siguen verdes y el diff no elimina ninguna línea `assert` (medido: `git diff -- tests/... | grep -c "^-.*assert"` = 0) | ✅ A2 |
| Mutantes de AC3/AC4 sobre copia aislada | 5 de 5 con sensibilidad demostrada | montaje `temp/mutantes_a2/mount` (copia del script, del archivo de tests y de `run_all_validations.py`, que dos dientes leen): cada uno con su par copia-intacta(EXIT 0)/mutada(EXIT ≠ 0) dentro del mismo crudo, la **aserción que pierde** nombrada y `count(old) == 1` en el ancla. El sha256 del script vivo (`96fe9257eddb…`) y del test vivo (`499fbc2725cd…`) es idéntico antes y después de la tanda: el worktree no se mutó. Crudos `E/FASE-A2/mutantes-*.txt` y `mutantes-resumen.txt`. **Re-toma declarada:** el arnés corrió dos veces porque la expresión `-k` de M3 llevaba la conjunción en español y pytest salió `EXIT=4` en los dos lados, sin ejecutar nada | ✅ A2 |
| Checks del quick al cerrar A2 | todos verdes, con `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick` sobre el worktree con la cura de AC3/AC4; el número lo imprime la corrida y no se copia aquí — crudo `E/FASE-A2/quick_cierre.txt`, repetido sobre el árbol del commit | ✅ A2 |
| Mutantes ejecutados sobre copia aislada | 3 de 3 con sensibilidad demostrada | montaje en `temp/mutantes_a1/mount` (el worktree vivo nunca se mutó): cada mutante con su par copia-intacta(verde) / mutada(roja) y el sha256 del script vivo idéntico antes y después; crudos `E/FASE-A1/mutante-*.txt` y `mutantes-resumen.txt` | ✅ A1 |
| Funciones `def test_` en `tests/test_build_lesson_index_s15_fecha_versionada.py` | 4 | idem — medido 2026-10-08 | Preparación |
| Funciones `def test_` en la familia del índice (16 + 36 hermanas) | 52 | idem sobre `tests/test_build_lesson_index.py` y `tests/test_verify_qmind_context_freshness.py` — medido 2026-10-08 | Preparación |
| Cases de la selección PRE de apertura | 1 failed / 26 passed (27 collectados) | pytest 9.0.2 con Python 3.13.3 del sistema; crudo en `E/FASE-0/pre_seleccion_apertura.txt`, EXIT=1 | Preparación |
| Checks del quick de apertura | todos verdes, con `EXIT=0` | `python scripts/run_all_validations.py --quick`; **el número lo imprime la corrida**, no se fija aquí — crudo `E/FASE-0/quick_apertura.txt` | Preparación |
| Checks del quick al cerrar A1 | todos verdes, con `EXIT=0` | `venv/Scripts/python.exe scripts/run_all_validations.py --quick` sobre el worktree con la cura; el número lo imprime la corrida y no se copia aquí — crudo de apertura `E/FASE-A1/quick_apertura.txt`, el del cierre en el registro de fase | ✅ A1 |
| IDs definidos en el índice del corpus | 348 | salida de `build_lesson_index.py --check`, medido 2026-10-08 | Preparación |
| Distribución de fuentes de fecha del índice | 337 `nombre` / 11 `commit` / 0 `SIN-FUENTE` | línea `[fechas]` del writer; la FASE-B/C la re-mide | Preparación |
| Tests nuevos de cada fase | A3, B, C: ⬜ pendiente (A1: 8 y A2: 12, filas arriba) | lo imprime su POST | A3, B, C |
| Checks del modo completo al cerrar | ⬜ pendiente | `run_all_validations.py` sin `--quick`, crudo archivado | RELEASE |
| Presupuesto `tool_use` por fase | A1: ≈70 contados a mano, **por encima de la referencia de 60 → checkpoint declarado** (no fase adicional, contrato §R2). **Referencia vigente desde la enmienda del 2026-10-08: 90 para A2/A3/B y 60 para RELEASE** (contrato §R2; la decisión y su base medida están allí) | **auto-reporte con unidad declarada** (instrumento canónico FUERA DE SERVICIO, R2.1); el desglose de en qué se fue, en `E/FASE-A1/00-registro-de-fase.md`; el total ≈70 lo imprime ese registro y las tres partidas (≈30 código+tests+mutantes / ≈25 cierre documental / ≈15 verificaciones y re-tomas) las declaró el operador al dictar la referencia, no las publica ningún instrumento. **Y la FASE-ENMIENDA del mismo 2026-10-08: ≈110 `tool_use`** contra la referencia de
~40 que proponía su propio mandato → exceso **declarado como checkpoint**, con el desglose de seis partidas y las
cuatro negaciones de instrumento en `E/FASE-ENMIENDA/00-registro-de-enmienda.md` (esa acta es la fuente del número;
esta fila lo referencia). **FASE-A2 del mismo 2026-10-08:** su auto-reporte con unidad declarada, corte usado y desglose vive en `E/FASE-A2/00-registro-de-fase.md`, que es la fuente del número; la referencia que le aplicaba es 90 `tool_use` (DA-CIM.10) | ✅ A1, ✅ Enmienda documental, ✅ A2 (A3, B, C pendientes) |

## Sección E: Archivos afiliados actualizados

| Archivo | Cambio | Fase |
|---|---|---|
| `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/**` | Catorce documentos del plan creados en la preparación: ocho de gestión (00, 01, 04, dependencias, 06, 09, 10, README) y seis prompts de fase | Preparación |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-0/**` | Crudos de apertura (quick y selección PRE) y registro de fase | Preparación |
| `.opencode/LECCIONES-INDEX.md` + `.opencode/lecciones_index.json` | Regenerados **con su escritor** como último paso de la preparación (esta sesión añadió `.md` que nombran IDs) | Preparación |
| `CHANGELOG.md` | Subsección de fase bajo `## [Sin publicar]` en cada fase; encabezado de versión solo en RELEASE | todas |
| `docs/GUIA_TECNICA.md` | Nota técnica por fase | todas |
| `docs/contributing/REGISTRY.md` + `docs/contributing/.last_doc_phase.json` | Una entrada por fase, escrita **por esa fase** con `log_phase_completion.py`. **FASE-A2 escribió dos**: el alta tardía de la FASE-ENMIENDA (mandato del operador; 25 rutas por `git diff --name-status 67b7e2f..083e6ab`, `--tests 0`, unidad en `--nota`, sin `--plan`) y su propia fila, **después**, para que `> **Ultima actualizacion:**` quede en la fecha de A2. El marker `.last_doc_phase.json` es efecto colateral del escritor con `--archivos-mod` y viaja en el mismo commit; medido: ganó la clave literal `"14": "FASE-ENMIENDA"`, o sea **afirma una sección que no es una ruta del árbol** | todas ✅ |
| `.agent/knowledge/DOMAIN_PRIMER.md` | Regenerado con `doctor.py --regenerate-domain-primer` al cerrar fases de implementación, si la fase tiene mandato para escribirlo; verificado con `--context` en RELEASE | A1 ✅ (el escritor corrió al cerrar y el derivado quedó **byte-idéntico** a HEAD, así que no aportó ruta al commit), A2, A3, B, C, RELEASE |
| `.opencode/qmind-writeback/instantaneas/README.md` | Prosa humana del directorio: A1 re-escribió «Qué sirve» con las tres comprobaciones (cuerpo / registro-vs-instantánea / servidor) y la regla de no-back-fill; **A2 añadió «Cómo se nombra una instantánea»** con el esquema `<plan>--<título-saneado>--<huella>.md` (resolución de la fila `instantaneas/README.md` de `dependencias-fases.md`) | A1 ✅, A2 ✅ (2026-10-08) |
| `scripts/validate_qmind_writeback.py` | El instrumento curado: A1 landed (`sha_cuerpo`, schema 1.1, puerta cuerpo-contra-cuerpo, `[CONTADOR]`, guard del escritor ante cuerpo no resoluble); **A2 landed** (`slug_de_instantanea()`, `fuente_id_de_tabla()`, `verificar_por_censo()`, `publicar_en_registro()` llamado en las dos ramas de `do_upload()`, y `registrar_publicacion()` calculando el `sha256` sobre el origen) | A1 ✅, A2 ✅, A3 |
| `tests/test_validate_qmind_writeback_escritura.py` | Dientes aditivos por AC: A1 sumó 8 (23 → 31) sin re-bajar aserciones; **A2 sumó 12 (31 → 43)** y cambió la forma con la que `QmindFalso` responde a `source upload` — pasó de JSON a la tabla `Key: value` real — sin tocar ninguna aserción vieja | A1 ✅, A2 ✅, A3 |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A1/**` | Doce crudos: quick de apertura, PRE/POST de la selección literal, regresión de hermanos, muestra offline del `[CONTADOR]`, tres mutantes con su par intacto/mutado y el resumen con la restauración por sha256 | A1 ✅ |
| `tests/test_build_lesson_index_s15_fecha_versionada.py` | Cura del control | B |
| `scripts/build_lesson_index.py` | Solo si AC9 lo exige | C |
| `VERSION.yaml` | **No** en fases intermedias | RELEASE con mandato |
| `.opencode/plans/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/**` (diez rutas) | **FASE-ENMIENDA, 2026-10-08:** maestro (errata en §4, estado en §5, enunciado de las dos decisiones del operador en §2 y presupuesto en §3), contrato (§R2 y el apartado nuevo de §Cierre sobre la unidad de los atributos verificables), prompts de A2/A3/B/C, `dependencias-fases.md`, `10-analisis` (seguimientos y sello de A1), `06-checklist`, `09` (esta sección, §B y §D) y `README.md` (punto de reanudación y Progreso) | Enmienda documental ✅ |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A2/**` | Acta de la fase (`00-registro-de-fase.md`), PRE/POST de la selección literal, control del montaje aislado, los cinco crudos de mutante con su par, `mutantes-resumen.txt`, el crudo del alta de la enmienda en REGISTRY y los crudos del quick. La lista la publica `ls -1 evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-A2/*`, no esta fila | A2 ✅ |
| `evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-ENMIENDA/**` | Acta de la enmienda (`00-registro-de-enmienda.md`) más los crudos del quick por tanda: apertura, cierre, sello, addenda, negación de la L3, el **par** rojo/verde de las citas numéricas. La lista la publica `ls -1 evidence/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07/FASE-ENMIENDA/*.txt`, no esta fila — cada tanda añade su crudo y un conteo fijo aquí nace vencido | Enmienda documental ✅ |
| `CHANGELOG.md` (nota de la enmienda) | Subsección bajo `## [Sin publicar]` con las cuatro decisiones del operador del 2026-10-08 y el rojo que la propia tanda fabricó, **sin** encabezado de versión | Enmienda documental ✅ |
| `docs/GUIA_TECNICA.md` | **Sin nota al cerrar la enmienda** (su lectura fue denegada por el clasificador y el contrato prohíbe reintentar un permiso negado; quedó declarada en el acta). **Escrita en FASE-A2 con autorización expresa del operador**: la nota técnica de la enmienda y la errata de estado de AC3/AC4 | Enmienda documental ✅ (tardío), A2 ✅ |
