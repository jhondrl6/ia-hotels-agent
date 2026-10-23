# Lecciones Capitalizadas — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> **Creado**: 2026-10-22, antes de FASE-A. **Corregido**: 2026-10-22, al aplicar la estrategia revisada (spark retirado, D21 fuera, D16/D24 con decisión, H1/H2, E2E-PRE).
> **Plan**: `CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22` · **Objetivo**: curar las deudas de producto verificadas (`D16`–`D28`) con sus hallazgos (`N1`–`N7`), el contrato plantilla↔tier↔veredicto (ítems A y C), y certificarlo con un ensayo determinista y una corrida E2E de `v4complete` para Hotel Don Alfonso.

## 1. Consultas ejecutadas (literales, re-ejecutables)

| # | Capa | Consulta literal | Resultado (n / IDs devueltos) |
|---|------|------------------|-------------------------------|
| Q1 | Índice generado (`.opencode/LECCIONES-INDEX.md`, corpus-wide) | `grep -n "L-SR1\|L-V2\|D-T4B-A1\|L-CST-7\|L-SR3\|L-NC10\|L-CIM.12\|L-QW.1\|L-ENT.9\|L-P3A.2\|L-R.4\|L-VUP-5\|L-T4A.5\|DA-C3" .opencode/LECCIONES-INDEX.md` | 16 filas devueltas; 14 IDs con dueño y ruta legibles. Al regenerar el par tras esta corrección, `python scripts/build_lesson_index.py --check` reporta **398 IDs definidos** y **113 citados sin definición**, con `EXIT 0`; incluye `DA-PLAN-1`…`DA-PLAN-8` de este plan, sin redefiniciones atribuidas a él. |
| Q2 | Notebook QMind `iah-cli-lecciones` (corpus-wide) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "contrato roto atributo método lectores huérfanos ramas no ejercitadas" --format agent` | 5 fuentes; top: `CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27` |
| Q3 | Notebook QMind `iah-cli-lecciones` (corpus-wide) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "over-presentación plantilla comercial tier veredicto honestidad" --format agent` | 5 fuentes; top: `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12` (score 0.98). La copia recuperada coincide con la local; `10 → 6 → 2` es la medición del revisor. |
| Q4 | Notebook QMind `iah-cli-lecciones` (corpus-wide) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "get_detected_issues claves GBP inglés español pérdida falsa brechas incondicionales" --format agent` | **0 fuentes relevantes**. No hay conocimiento publicado para `D28`/`get_detected_issues`; la autoridad es el código vivo y el contexto de deudas local. |
| Q5 | Notebook QMind `iah-cli-lecciones` (corpus-wide) | `qmind retrieve --nb 01a04d98-b7bd-778c-8441-26fdc7e35f45 -q "BenchmarkLoader regiones DEFAULT_DATA lector benchmarks regionales" --format agent` | 1 fuente, score 0.62, no pertinente. No hay conocimiento publicado para `D25-ter`; la autoridad es el código vivo y el contexto de deudas local. |
| Q6 | Memoria de proyecto (`MEMORY.md`) | `grep -in "patch\|tabla\|commit\|fase" <memoria-de-proyecto>` | Convenciones de cierre de fase y de edición de tablas aplicadas como restricciones de los prompts |

**Frontera Knowledge Center / código local**: el contrato tier↔veredicto sí está publicado y se puede citar como conocimiento; `D28`, `D25-ter`, `D16`, `D24` y el resto de deudas son mediciones locales del árbol, no doctrina del notebook. El plan las etiqueta así.

## 2. Lecciones capitalizadas

| ID | Enunciado (una línea) | Definida en (ruta) | Qué cambia en ESTE plan | Dónde se aplica |
|----|----------------------|--------------------|-------------------------|-----------------|
| L-SR1 | Las ramas no ejercitadas por la corrida estándar acumulan defectos latentes hasta que una prueba las toca | `context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27` | `N1` es la clase: `spark` no la ejercitaba nadie. El retiro no cierra sin test de la ruta retirada y sin guardián | AC5 · FASE-A |
| L-V2 | Quien cambia un contrato barre sus consumidores en TODO el repo, no solo en el directorio de su fase | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | El refactor `1501dd8` dejó dos lectores; FASE-A barre los contratos atributo→método y FASE-D barre los dos caminos GBP | AC3 · AC5 · FASE-A, FASE-D |
| D-T4B-A1 | Una suite verde puede certificar sin ejercitar el contrato de lectura sobre artefactos reales | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | El diente de FASE-D usa la forma real de `_base_profile()` **y** la de `PainSolutionMapper`; no un fixture del detector | AC3 · FASE-D |
| L-CST-7 | Curar el texto de una cláusula no cura la forma del defecto en sus hermanas | `Archives/CURA-COSTURA-TRIBUNAL-2026-10-11` | `P6.5`/`D21` quedan fuera; la lección se aplica a `D23` (dos divergencias en el mismo docstring) y a la familia de textos comerciales | AC8 · FASE-H2 |
| L-SR3 | Promesa, matriz y gate deben compartir UNA fuente de verdad para el estado de un servicio | `context/CONTEXT-SALENTOREAL-V4COMPLETE-EJECUCION-2026-08-27` | Dos vocabularios GBP y cinco tablas regionales son la misma clase; FASE-D/E imponen la fuente única | AC3 · AC4 · FASE-D, FASE-E |
| L-QW.1 | Un verificador que comprueba la clave de una operación no detecta que el contenido no se verificó | `Archives/VERIFICADOR-ESCRITURA-QMIND-2026-09-20` | `N6`: el check “Plan Maestro Sync” comprueba que el JSON parsea, no que sincroniza; FASE-E cablea el verificador que compara valores sin perder el parseo | AC4 · FASE-E |
| L-ENT.9 | Un proveedor configurado no es un proveedor ejercitado: la métrica verde oculta qué rama corrió | `Archives/REFACTOR-WHATSAPP-ENTREGA-2026-09-18` | `N4`: `report_builder` instancia dos lectores; FASE-E deja uno. FASE-D verifica dos detectores reales, no uno | AC3 · AC4 · FASE-D, FASE-E |
| L-NC10 | Fosilización narrativa: texto estático que ignora la fuente dinámica de verdad | `Archives/REFACTOR-COHERENCIA-NARRATIVA-2026-08-22` | `DEFAULT_DATA` es maestro de facto de cinco bloques; FASE-E declara su destino antes de tocar el lector | AC4 · FASE-E |
| L-CIM.12 | Un control anti-regresión puede estar en verde y no medir la propiedad que nombra | `Archives/CURA-INSTRUMENTOS-QMIND-S15-2026-10-07` | `N7`: el guardián pasa sobre un `AttributeError`; FASE-A lo extiende a existencia. FASE-E no confunde check verde con dato leído | AC4 · AC5 · FASE-A, FASE-E |
| L-P3A.2 | La clave correcta la dicta el parser del lector, no la intención del autor | `Archives/TRIBUNAL-ENFORCEMENT-OBS-2026-09-11` | FASE-C valida el nombre contra el acta/parser real; FASE-F nombra umbrales por semántica, no por costumbre | AC2 · AC6 · FASE-C, FASE-F |
| L-T4A.5 | Un test puede pasar sin ejecutar la rama que dice certificar | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | AC1, AC3, AC5 y AC8 se cierran con mutation check sobre el símbolo real | AC1 · AC3 · AC5 · AC8 |
| L-R.4 | Una regla de proceso sin verificador es publicable solo si la regla lo declara | `Archives/TRIBUNAL-OFFLINE-2026-09-09` | R2.7/R2.8 se declaran; el instrumento de iteraciones legado se marca no comparable si no aplica | Restricción de todos los prompts · `10-analisis` §Seguimientos |
| DA-C3 | vacío ≠ ausente: un lector que no pudo mirar no publica el mismo resultado que «medí y no hay nada» | `Archives/ESTABILIZACION-PRE-TRIBUNAL-2026-09-03` | `D28` y `D24`: schema tri-estado y stub con `data_status`, no `found=True` vacío | AC3 · AC8 · FASE-D, FASE-H1 |
| D-PF5 | El guardián estático L-SR1 es una lista de nombres prohibidos sobre AST, extensible | `Archives/SR-PIPELINE-FIXES-2026-08-27` | FASE-A lo extiende a existencia del atributo sobre la clase importada | AC5 · FASE-A |
| L-PF10 | Vacío ≠ ausente: la lista vacía puede significar «el fix funcionó» | `Archives/SR-PIPELINE-FIXES-2026-08-27` | E2E-PRE distingue “0 brechas porque está curado” de “0 porque el lector falló” | AC7 · FASE-E2E-PRE |

## 3. Candidatos evaluados y descartados

| ID | Por qué NO aplica a este plan |
|----|-------------------------------|
| L-VCF-5 / L-VCF-10 / L-VCF-11 | Familia del instrumento de verificación de contexto de fase: miden denominadores de checks y red prohibida de un lint que este plan no toca |
| L-HF1 | Candados de cobertura sobre `.agents/`: superficie de gobernanza de artefactos, no de producto |
| DA-G4 | Extensión de DA-C3 al gate de cobertura: este plan no modifica el gate de cobertura ni el `pain_ledger` |
| L-V2.2 / L-V2.3 | Verificadores de capitalización y de denominadores del hook: pertenecen al instrumento del Paso 0, ya ejecutado y en verde para este artefacto |
| L-CST-6 | Ya se aplicó a la cura de la costura del tribunal; este plan no reabre el tribunal fuera del nombre del veredicto |

## 4. Cobertura declarada de este documento

- Qué **sí** deja evidencia: las consultas re-ejecutables de §1 (índice, QMind, memoria), las lecciones de §2 con dueño y ruta del corpus, y los descartes de §3 con motivo.
- Qué **no** verifica el check mecánico: la **pertinencia**. `scripts/validate_lesson_capitalization.py` comprueba forma y trazabilidad —consultas corpus-wide con comando en backticks, ≥3 descartes, AC nombrado que existe en `01-plan-maestro.md`, ID con el dueño que publica el índice y ≥2 fuentes distintas— pero **no verifica** que la lección que debía capitalizarse fuera esta ni que el efecto alegado sea real.
- Frontera de autoridad: las lecciones de `D28`/`D25-ter`/`D16`/`D24` son mediciones locales; las de A/C tienen respaldo publicado en el notebook. No se atribuye al Knowledge Center lo que no está en él.

## 5. Qué pasó con las lecciones citadas — FASE-A (2026-10-22)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-SR1` | El retiro no cierra sin test de la ruta retirada y sin guardián | ✅ `tests/test_spark_retirement.py` ejercita la ruta real (`main.py spark --url …` → exit 0 + mensaje de retiro) y el guardián cubre las dos superficies del contrato; la reintroducción del lector roto es rojo por AST |
| `L-V2` | Barrer los consumidores del contrato en TODO el repo (Tarea 4) | ✅ Barrido `R4c` publicado en `evidence/…/FASE-A/`: 2 huérfanos vivos del contrato (`main.py` retirado, `gap_analyzer` reparado), 0 restantes; hallazgos fuera de código vivo con dueño en `10-analisis` §Seguimientos |
| `L-CIM.12` | El guardián se convierte en comprobación de existencia, con mutante en rojo | ✅ Mutante con atributo inventado sobre la fuente real del defecto → rojo (violación detectada); árbol actual → verde; par en `guardian-existencia-par-rojo-verde.txt` |
| `D-PF5` | Extender el guardián de nombres a la clase importada | ✅ Extensión por AST + import (`hasattr` sobre la clase importada), no por más nombres prohibidos ni grep de menciones |
| `L-R.4` | El par rojo/verde y la resta se declaran sin verificador mecánico | ✅ Declarado en `baseline-pre-post.md` (resta) y en el par del guardián (R2.8) |
| `L-T4A.5` | El test del retiro afirma exit y mensaje, no solo «no lanzó» | ✅ El test afirma exit 0 **y** mensaje de retiro **y** ausencia de `AttributeError`; el test del lector recorre la rama fallback real de `_basic_analysis` |

## 5.1 Qué pasó con las lecciones citadas — FASE-B (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-P3A.2` | La sintaxis la dicta el parser del lector, no la intención del autor | ✅ El template pidió `==`/`!=` y `_preprocess_conditionals` solo comparaba igualdad: se extendió el parser (operador `==`/`!=`) antes de escribir el `{{if}}`; la regla la dictó el parser |
| `L-T4A.5` | Mutation check sobre el símbolo real, no sobre un fixture | ✅ El par de AC1 corre la función real del revisor sobre el render real: VERDE 0 → ROJO 2 con el mutante (condición desactivada / strings forzados a variante A); el rojo del mutante queda codificado como test |
| `L-VUP-5` | Una fase de extensión sin rojo es un falso verde potencial | ✅ La extensión de FASE-B sí produjo rojo: 2 hallazgos reales del revisor con el mutante; además el derivado de Wiring vencido hizo fallar `--quick` 12/13 hasta re-publicarlo. La extensión no es verde por no-ejecución |
| `L-R.4` | Los huecos sin verificador se declaran | ✅ `baseline-pre-post.md` declara que el verificador mecánico de la resta no existe, que el par pass/fail de la suite completa **no existe** (solo el punto medido), y la atribución de los 3 rojos de la suite por mecanismo |

- [ ] Actualizado al cierre de la última fase, y el write-back de QMind se ejecutó **antes** de archivar el plan (`git mv` a `Archives/`, orden R2.10).
