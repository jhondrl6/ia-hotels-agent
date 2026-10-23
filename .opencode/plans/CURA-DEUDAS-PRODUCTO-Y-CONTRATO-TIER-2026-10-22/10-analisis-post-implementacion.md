# Análisis Post-Implementación — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> **Estado por fase**: no se declara en este encabezado; su dueño único es `06-checklist-implementacion.md` (cada ✅ exige el checklist del prompt y la entrada de esa fase en `docs/contributing/REGISTRY.md`). La frase «Preparación corregida — ninguna fase ejecutada» quedó retirada de este archivo al vencerse en el cierre de FASE-A (2026-10-22).
> **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22`
> **Versión objetivo**: 4.82.0

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | Subagente | Notas |
|------|--------|--------|-------------|-----------|-------|
| Preparación | 2026-10-22 | ✅ | _(auto-reporte en unidad `tool_use`)_ | no | Correcciones al contexto de deudas aplicadas; estrategia corregida y 12 prompts regenerados |
| FASE-A | 2026-10-22 | ✅ | _(auto-reporte unidad `tool_use`, **no comparable**: `measure_iterations.py` es legado y no se probó contra este runtime)_ | no | `spark` retirado (centinela exit 0; `D19` cerrada por retiro), `gap_analyzer` reparado (reparar, no retirar), guardián por existencia (`N7`) con par rojo/verde, barrido `R4c` sin huérfanos vivos |

## Matriz de Verificación de Hallazgos (llenar en FASE-VERIFY; los «Expected» ya están medidos)

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| AC1 | Propuesta y diagnóstico con tier B+ | `summary.over_presentations == 0`; 2 claims neutralizados; labels financieros conservados | | |
| AC2 | Veredicto condicional | `verdict` + `conditional_reason` de 3 causas; 0 literal viejo en la población declarada; `P6.5` intacta | | |
| AC3 | Contrato GBP en dos caminos | `get_detected_issues` 0 brechas con `_base_profile`; `PainSolutionMapper` sin schema→abandono; 0 COP falsos | | |
| AC4 | `BenchmarkLoader` | Getters leen JSON; cinco tablas derivadas/retiradas; sync con valores y parseo | | |
| AC5 | `spark` retirado | Sin `AttributeError`; comando informa retiro; guardián caza atributo inexistente; `gap_analyzer` sin lector roto | | |
| AC6 | Umbrales/factores | Umbrales por semántica; `D25-bis` una fuente; `D27` con nombres semánticos | | |
| AC7 | Corrida Don Alfonso | ZIP real (`suppressed:false`); 0 `OVER_PRESENTATION`; pérdida 3.511.200 o re-medida; 11 brechas re-medidas | | |
| AC8 | `D16`/`D24`/`D18`/`D22`/`D23`/`D20` | Score `/90`; stub retirado; config limpia; docstring honesto; docs con fuente | | |

## Lecciones Aprendidas (llenar; «sin lecciones nuevas» es un resultado válido)

### Lecciones capitalizadas de planes anteriores (espejo de `00-lecciones-capitalizadas.md` §2)

| # | Lección | Aplicación en este plan |
|---|---------|-------------------------|
<!-- Espejo: se copia de 00 §2 y se anota qué pasó realmente en cada fase. El ID NUNCA ocupa la primera celda (columna # primero): _extract_definition trata la primera celda-ID como definición, y estas son citas. -->
| # | _(fila al cierre de la primera fase que las ejercite)_ | |
| 1 | `L-SR1` | FASE-A: el retiro de `spark` no cierra sin test de la ruta retirada y sin guardián |
| 2 | `L-V2` | FASE-A: barrido de los lectores del refactor `1501dd8`; FASE-D: dos caminos GBP |
| 3 | `D-T4B-A1` | FASE-D: el diente usa la forma real de `_base_profile` y de `PainSolutionMapper`, no un fixture del detector |
| 4 | `L-SR3` | FASE-E: una matriz de benchmarks; FASE-F: un umbral por semántica |
| 5 | `L-QW.1` | FASE-E: el check cableado compara valores, no solo parseo |
| 6 | `L-ENT.9` | FASE-E: `report_builder` deja de instanciar dos lectores; FASE-D: dos detectores reales |
| 7 | `L-NC10` | FASE-E: `DEFAULT_DATA` deja de ser maestro de facto sin declaración |
| 8 | `L-CIM.12` | FASE-A: el guardián se prueba contra un atributo inexistente; FASE-E: no confundir check verde con datos leídos |
| 9 | `L-P3A.2` | FASE-C: el nombre se prueba en el parser/acta real; FASE-F: nombres de umbral por semántica |
| 10 | `L-T4A.5` | AC1/AC3/AC5: mutation check sobre el símbolo real |
| 11 | `L-R.4` | Los huecos sin verificador (resta R2.7, par R2.8) se declaran |
| 12 | `D-PF5` | FASE-A: el guardián deja de ser solo una lista de nombres |
| 13 | `L-PF10` | FASE-E2E-PRE: distinguir “0 brechas porque está curado” de “0 porque el lector falló” |

### Lecciones nuevas de este plan

_(Al cierre de cada fase: qué pasó / por qué / qué lo previene + pertinencia INCLUIR/EXCLUIR. E2E-PRE y E2E nutren esta sección.)_

| ID | Qué pasó / por qué | Qué lo previene | Pertinencia |
|----|--------------------|-----------------|-------------|
| L20 | FASE-A añadió archivos de tests y evidencia y `run_all_validations.py --quick` falló 12/13: el artefacto publicado `.opencode/wiring_report.json` quedó vencido por el propio cambio de la fase («no falta un caller, falta publicar»). Reparación: `validate_wiring.py --write-report` → 13/13 | En el cierre de fase: re-publicar el artefacto de Wiring tras añadir archivos versionados y antes de `--quick` | INCLUIR — cambia el cierre de las 11 fases restantes del plan, todas añaden archivos |

Las lecciones citadas (`L-SR1`, `L-V2`, `L-CIM.12`, `D-PF5`, `L-R.4`, `L-T4A.5`)
se anotan con su desenlace real en `00-lecciones-capitalizadas.md` §5.

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| `D19`/`N1` (ruta `spark`) | **Cerrada por retiro** el 2026-10-22 (DA-PLAN-4) | Sin acción futura: no se promete cifra nueva; `spark` queda como centinela que informa su retiro y sale 0 |
| Lectores del refactor `1501dd8` en `temp/` (backups `fase_d_backup`, `fase_f_recovery_backup`) | Detectados en el barrido `R4c`; fuera de las rutas del producto | Dueño Operador: decidir la depuración de `temp/`; no se expande alcance sin decisión |
| Fósil textual: el docstring de clase de `FinancialFactors` nombra `SUPERPOSITION_FACTOR` como atributo | Detectado en el barrido `R4c` | Dueño FASE-H2 (honestidad de texto) |
| `AGENTS.md` §Comandos CLI: `spark` aún figuraba como «Deprecado» | **Aplicada** la escritura el 2026-10-22 con autorización expresa del Operador (opción (a)): la fila de `spark` pasa a «🚫 Retirado» con el centinela y `D19` cerrada por retiro, y la fila de `modules/generators/` se re-escribió tras medir sus consumidores reales (solo tests y `scripts/validate_structure.py`; `outreach_gen` sin referencias). Medido: `git diff --numstat AGENTS.md` = 2/2, EOL intacto | Ninguna: el hecho documental está cerrado. Queda la brecha de instrumento, con dueño FASE-H2: `validate_agents_md.py` no mira la tabla §Comandos CLI (PASS y EXIT 0 con la fila vencida) y `run_all_validations.py` no lo invoca, así que este tipo de deriva no la corta nadie |
| `D21`/`P6.5` | Fuera de alcance; dueño Operador | No absorber sin letra expresa; conservar `T1_CERTIFIABLE_CLAUSES` |
| `D26` (fórmula pretendida del precio) | Diferida sin enunciado original | Operador aporta enunciado → fase propia |
| Alias conformes para `D16`–`D28`/`N1`–`N7` | Decisión del Operador | Si se acuñan: celda de definición propia, nunca alias suelto |
| Publicación QMind de `CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` | Pendiente | Obligatoria en el mismo ciclo que la cura de la segunda vía del verificador |
| R2.7/R2.8 sin verificador mecánico | Con dueño (`L-R.4`) | Declarado en cada cierre; instrumentar queda como deuda escrita |
| `measure_iterations.py` legado | No comparable hasta probar compatibilidad | Usar auto-reporte `tool_use` o adaptar el instrumento al transcript del runtime |
| `D28` en `v4audit` | Resuelto en FASE-D, no en E2E | Mantener el diente de frontera; el E2E no lo ejercita |
| Onboarding de Don Alfonso | YAML versionado en evidencia; `output/clientes` gitignorado | E2E-PRE lo materializa; el Operador confirma el dominio antes de la corrida |
| `D20`/`Benchmarking.md` | FASE-H2 | La fuente es el JSON maestro; la doc se alinea o se marca |

## Métricas de Ejecución (al cierre: referencia a `09-documentacion-post-proyecto.md` §D y a los informes de `evidence/`, no copia del número)

Ver `09-documentacion-post-proyecto.md` §D (fuente única del número por fase) y `evidence/CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22/FASE-A/` (par pre/post con resta, par rojo/verde del guardián y crudos del barrido `R4c`).

## Decisiones Arquitectónicas

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| DA-PLAN-1 | Un solo plan para A y C, sin absorber `D21` | A y C comparten la superficie comercial, pero `D21` tiene dueño y no hay letra; absorberlo convertiría una deuda ajena en cambio no autorizado | Dos planes paralelos sobre `judge.py`/`acta_writer.py`; absorber `D21` sin letra | Preparación |
| DA-PLAN-2 | Ítem A por render condicionado, limitado a los **2** claims del revisor | El verde de Bot 4 pasa a ser estructural sobre los hallazgos reales; no se reescriben labels financieros legítimos | Re-copy de las 7 líneas del grep; poda manual de palabras | FASE-B |
| DA-PLAN-3 | Ítem C con `APROBADO-CONDICIONAL` + `conditional_reason` | Un veredicto puede ser condicional por tres causas; codificarlas en el nombre produce combinaciones y deja fuera la causa de tier A no certificable | Dos nombres largos sin tercera causa; mantener el literal viejo | FASE-C |
| DA-PLAN-4 | Retirar `spark`; `D19` se cierra por retiro | `spark` está deprecado y su ruta no recibe `hotel_data` ni `_pv_result`; repararla exigiría inventar un contrato que el producto no usa | Reparar `D19` y crear una ruta de estimación paralela | FASE-A |
| DA-PLAN-5 | `D16` publica `/90` y elimina la rama API muerta | `_places_api_lookup` no está implementada; la única varilla viva es la estimación; publicar `/100` con máximo 90 es un sesgo sistemático | Renormalizar a 100 sin declararlo; mantener dos varillas | FASE-H1 |
| DA-PLAN-6 | `D24` declara muerto el stub y no toca el scraper real | El producto usa `autonomous_researcher.BookingScraper`; el stub solo lo consumen tests y no debe presentarse como dato | Corregir el stub y mantenerlo como fuente; tocar el scraper real | FASE-H1 |
| DA-PLAN-7 | E2E-PRE determinista antes de la corrida pagada | La corrida es única y no se parchea en E2E; el ensayo valida onboarding, render, revisor y juez sin inferencia | Confiar en los tests unitarios y descubrir el fallo en la corrida | FASE-E2E-PRE |
| DA-PLAN-8 | `D25-ter` obliga a retirar/derivar las cinco tablas | Reparar `BenchmarkLoader` sin eliminar las copias deja la causa raíz viva | Declarar fuentes y conservar las copias | FASE-E |

## Checklist de Cierre (llenar en FASE-RELEASE)

_(vacío hasta FASE-RELEASE)_
