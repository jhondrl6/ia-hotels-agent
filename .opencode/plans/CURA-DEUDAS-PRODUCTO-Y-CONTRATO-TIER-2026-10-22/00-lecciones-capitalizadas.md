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

## 5.2 Qué pasó con las lecciones citadas — FASE-C (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-P3A.2` | El nombre y la causa se validan contra el acta serializada, no contra el diccionario en memoria | ✅ Los tests de las 3 causas leen `acta_revision.json` escrito por el `ActaWriter` real (R2.4); un primer protocolo mal planteado (tier A + todo PASS + revisores leídos) salió `APROBADO-PARA-ENTREGA` y el assert del JSON lo delató, no el diccionario |
| `L-T4A.5` | El test lee el JSON del writer real y provoca las tres causas | ✅ Par rojo/verde con dos mutantes sobre el símbolo real: M1 (literal viejo restaurado) → 8 rojos; M2 (causa eliminada) → 6 rojos; restauración verificada con el verde final idéntico al inicial |
| `L-CST-7` | `P6.5` no se toca; la cura se limita al veredicto y su causa | ✅ `P6.5` (fila NOT_EVALUABLE reservada Bot 4) y `T1_CERTIFIABLE_CLAUSES` sin cambios — grep por símbolo en `evidence/…/FASE-C/p65-intacta.txt` |
| `L-R.4` | El grep del literal viejo se declara con su población | ✅ `baseline-pre-post.md` declara la población (`modules/`, `tests/`, `main.py`), la allowlist de históricos/scratch y que el verificador mecánico de la resta no existe |

## 5.3 Qué pasó con las lecciones citadas — FASE-D (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `D-T4B-A1` | El diente usa la forma real de `_base_profile` y la de `PainSolutionMapper`, no un fixture del detector | ✅ `tests/test_gbp_contrato_frontera.py` construye el perfil con `GBPAuditor._base_profile()` real y el audit con el `V4AuditResult` real de `v4_comprehensive` (la forma que `main.py` pasa a `detect_pains`) |
| `L-SR3` | Un vocabulario, dos caminos | ✅ `get_detected_issues` y `_map_brecha_to_issue_type` comparten el vocabulario del productor; los tres pains de web quedan sin etiqueta GBP |
| `DA-C3` | vacío ≠ ausente | ✅ Schema tri-estado (`None` no dispara; `{}`/`tiene_hotel_schema=False` = medido ausente → `SIN_FAQ`); `ultima_actividad_dias=None` no dispara `CERO_ACTIVIDAD_RECIENTE`; el llamador deja de pasar `{}` por defecto |
| `L-T4A.5` | Mutation check sobre el símbolo real | ✅ M1 (contrato viejo restaurado) reproduce el reproductor de `D28` — 6 brechas y 39.600.000 COP/mes — y cae en rojo; M2 y M3 caen sobre `_map_brecha_to_issue_type` y `tipo_map` |
| `L-V2` | Quien cambia un contrato barre sus consumidores | ✅ Barrido por grep en todo el repo de `get_detected_issues`, `gbp_leak_detector` y `_map_brecha_to_issue_type`: consumidores actualizados (llamador y `tipo_map` de `gbp_auditor`; comentario de `TARGET_GBP_PHOTOS` que citaba la copia muerta) |
| `L-ENT.9` | Dos detectores reales, no uno | ✅ El relevo corre contra el detector muerto REAL (importado con stubs de `webdriver_manager`), no contra un fixture: matriz perfil a perfil en `relevo-cruce.txt` |

## 5.4 Qué pasó con las lecciones citadas — FASE-E (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-NC10` | Decidir por escrito el destino de los bloques de `DEFAULT_DATA` antes de tocar el lector | ✅ Escrito en `10-analisis` DA-PLAN-8a/8b/8c **antes** del primer `Edit` de código, con assert de coherencia (`assert_coherencia_maestros`) y nota en el módulo. La decisión se escribió dos veces: la primera medición («ocho bloques sin contraparte publicada») la refutó el diente de la propia decisión, y quedó re-escrita en tres poblaciones con el horque divergente medido |
| `L-QW.1` | Cablear el verificador que compara valores sin perder el parseo | ✅ `[2/13]` invoca en proceso a `validate_benchmark_sync.py` y su verde dice «v2.5.0 parseado y 4 regiones con valores sincronizados (exenta: default…)»; M2 (`if divergencias:` → `if False and divergencias:`) deja **1 rojo** y prueba que el runner consume las divergencias, no solo que el script existe. Se añadió un rojo que la lección no pedía y es su consecuencia: `0 regiones comparadas` es rojo, porque un verde sin comparación vuelve a certificar nada |
| `L-ENT.9` | Un solo lector | ✅ `ScraperFallback._load_benchmarks` delega y pierde su dict de respaldo y su `benchmarks_path` relativa al cwd; `report_builder` lee regiones del loader y conserva `ScraperFallback` solo por `_detect_region`; el test de paridad compara las dos salidas **estructuralmente** (identidad de dicts), no por tres cifras de ejemplo |
| `L-P3A.2` | Usar `v25_config.regiones`, `precio_promedio`/`ocupacion`, no nombres supuestos | ✅ El puente toma las claves del parser del artefacto; la evidencia es que el JSON **sí** publica `umbrales_decision`/`paquetes_servicios_v23`/`addons_v242` bajo `v25_config` con otros nombres (`inversión_mensual_cop`) y el getter del contrato sigue leyendo el nivel superior — los dos vocabularios se midieron antes de decidir cuál manda |
| `L-SR3` | Las cinco tablas se derivan o se retiran | ✅ Maestro↔`v25_config`↔derivado casan región a región (los cuatro `revpar_cop` son `adr × occupancy` del maestro); `revpar_targets` y el respaldo de `ScraperFallback` quedan **retirados** (AST y literales ausentes); `Benchmarking.md` no se tocó (dueño FASE-H2) y quedó fijado por test con su divergencia medida |
| `L-T4A.5` | Mutation check sobre el símbolo real | ✅ M1 sobre `get_regional_data` (13 rojos) y M2 sobre la rama del runner (1 rojo), restauración verificada por sha256 y verde final idéntico al inicial; M3 de dato sobre una copia (`ADR DIVERGENCE [caribe]`) sin tocar el árbol |

## 5.5 Qué pasó con las lecciones citadas — FASE-F (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-SR3` | Un sitio por umbral nombrado, no un valor único | ✅ Cinco nombres publicados en `config/regional_benchmarks.yaml` con lector único (`modules/common/umbrales_fotos.py`) y la escalera verificada al importar; los 14 sitios vivos del producto leen el nombre y `D25-bis` quedó en un respaldo único (`modules/common/scenario_config.py`). El valor único forzado habría sido el defecto contrario: el colapso está cortado por test (`len(set(valores)) == 5`) |
| `L-NC10` | El default duplicado se elimina o se vuelve assert contra el YAML | ✅ El `.get('realistic', 0.20)` y el `.get('realistic', 0.35)` desaparecen (AST lo corta) y el respaldo `0.20` se corrigió a `0.35` = maestro, con cotejo que pone en rojo la divergencia — M1: **3 rojos** restaurando el 0.20. Hallazgo propio: `L27` (un umbral también fossiliza como default de `.get()`, no solo como literal de comparación) |
| `L-V2` | El rename de constantes barre los módulos y tests que sobrevivan | ✅ Tres renombrados (`PERDIDA_BASE_SIN_PERFIL`, `PERDIDA_BASE_CARIBE_CALIBRADA`, `PERDIDA_BASE_CALIBRACION_15_20_HAB`) con 0 usos del nombre genérico en `modules/`, `main.py`, `scripts/` y `tests/`; el barrido también movió consumidores del contrato de tier (`test_fase_f_financial_placeholders.py`, `test_financial_evidence.py`) y los conteos de usos quedaron pinchados, así que una huérfana que alguien consuma sin declarar cae en rojo |
| `L-T4A.5` | Test de coherencia que falla si el YAML y el default divergen | ✅ M1 (divergencia del respaldo) y M2 (literal `fotos >= 15` re-introducido) con par en `evidence/…/FASE-F/par-rojo-verde-mutantes.txt`, árbol intacto por sha256 y verde final idéntico. Además el diente de divergencia vive dentro de la suite (`test_mutante_de_divergencia_pone_en_rojo_el_cotejo`), y `test_bloque_incompleto_o_invertido_falla_fuerte` le da oportunidad de perder al lector |
| `L-P3A.2` | Los nombres de umbral se leen del config, no de la costumbre | ✅ El lector toma las claves del bloque publicado (`umbrales_fotos`) y falla fuerte si faltan; el nombre no lo dictó la costumbre en dos episodios: el ejemplo del plan proponía **cuatro** nombres para **cinco** valores y el árbol resultó tener separada la banda de rúbrica (15) de la brecha que declara el diagnóstico (20), así que el vocabulario se publicó con cinco nombres; y el conteo de sitios que heredaba el enunciado (`11`) se re-midió a 14 |

## 5.6 Qué pasó con las lecciones citadas — FASE-H1 (2026-10-23)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-SR3` | Un denominador (`/90`) y una varilla viva; el stub no compite con el scraper real | ✅ `modules/common/rubrica_gbp.py` es el único sitio donde vive un techo (`SCORE_GBP_MAXIMO`/`ESTIMACION_GBP_MAXIMO`); la rúbrica queda en `_calculate_gbp_score` y la llama `_scrape_maps_profile` (M3 pone en rojo la segunda copia); la rama API muerta se retira y el scraper real queda intacto por test y por su suite |
| `L-NC10` | El reporte publica el denominador del cálculo, no un `/100` heredado | ✅ El reporte del auditor, el log del analizador y el `geo_score` auditado leen el denominador del productor. La población se midió por productor, no por literal: de 22 `/100` de `report_builder`, 4 imprimen la rúbrica (quedan declarados: módulo DEPRECATED) y el `/100` del cliente Places es legítimo |
| `DA-C3` | El stub publica `data_status=STUB_RETIRADO`, no `found=True` vacío | ✅ `found=False` + `data={}` + `STUB_RETIRADO`; el molde con `rating`/`review_count`/`price_range` en `None` quedó retirado y M2 (restaurar `found=True`) produce **4 rojos** |
| `L-T4A.5` | El test del stub afirma el estado retirado; el de `D16` afirma `/90` y el techo 90 | ✅ Ambos afirman sobre el artefacto real (`generar_reporte_ejecutivo`, `get_competitor_score`, `scrape`). Diente adicional por la lección nueva `L30`: la ausencia del `score_source` «api» se verifica por literales del código **sin docstrings** — el primer intento cayó rojo contra la prosa del propio retiro |

## 5.7 Qué pasó con las lecciones citadas — FASE-H2 (2026-10-24)

| ID | Qué exigía en esta fase | Qué pasó realmente |
|----|-------------------------|--------------------|
| `L-CST-7` | `D23` tiene **dos** divergencias en el mismo docstring; se corrigen ambas | ✅ La prosa prometía una disyunción y una frontera exclusiva; la rama es conjunción inclusiva. El guard no acepta la corrección por buena voluntad: el docstring debe contener el `ast.unparse` de la condición, y el mutante **M3b** (`>=` → `>`) pone en rojo 3 tests, incluido el de frontera. La hermana del defecto apareció donde no se esperaba — en el test, no en el texto: `tests/test_audit_alignment.py` certificaba umbrales que nunca leyó (ver `L31`) |
| `L-NC10` | `Benchmarking.md` declara su fuente y no compite con el JSON | ✅ §0 nuevo declara las **cinco** tablas de `N5` con su rol (MASTER / PUBLICADA / DERIVADA / RETIRADA ×2) y el propio doc como **contexto histórico sin lector**. No se movió un número: la divergencia de ADR/RevPAR queda escrita con su motivo (re-valuar el maestro sería cambio de modelo sin dictado) y con el pin de FASE-E vivo, que es lo que impide que la declaración se vuelva memoria |
| `L-P3A.2` | El test de `D23` usa la frontera real (`rating == 4.0`) | ✅ La frontera la dictó el AST (`_condicion_de_disparo()` anclada por identidad, no por posición) y el test juzga 4.0 como el código: FAIL. `test_justo_debajo_de_la_frontera_no_dispara` (3.99) y `test_place_found_falso_no_dispara_aunque_el_rating_suba` (la segunda divergencia) completan la escalera. Ninguna variante tocó la lógica del gate |
| `L-R.4` | `D20` documental se declara sin mutante | ✅ El par de mutantes de H2 es M1 (re-introducir el bloque `thresholds`), M2 (restaurar el módulo muerto), M3a (restaurar la prosa vieja) y M3b (invertir la rama). `D20` no tiene mutante porque no hay predicado que romper: se declara y queda gobernado por el pin ajeno de FASE-E, como exige la regla. La resta y la ausencia de verificador mecánico se declaran en `baseline-pre-post.md` |
| `L-SR3` (la clase de `D18`) | Un umbral no puede vivir en dos sitios | ✅ Retirado el bloque `thresholds` de `settings.yaml` (4 claves, 0 lectores medidos por símbolo) con los sucesores nombrados en el propio archivo (`gbp_score_bajo` del `BenchmarkLoader`, `umbrales_fotos` de FASE-F). **Hallazgo de la fase**: en el mismo archivo queda un segundo bloque sin lector (`package_thresholds`, 4 regiones × 6 claves, 0 lectores de producción) que `D18` no nombra; declarado con dueño, no curado por la valla del horque |
| `L30` (lección de FASE-H1, se cita aquí con su desenlace) | El diente anti-literal no puede mirar la fuente como texto | ✅ Se aplicó contra mí en el primer intento del guard de `D18`: barría el nombre `min_reviews:` y caía rojo contra (a) `package_thresholds`, que legitima el mismo nombre en otro bloque, y (b) la prosa del propio test que documenta el retiro. El predicado correcto es de mecanismo: qué archivo abre `settings.yaml` y qué ruta de claves lee |

- [ ] Actualizado al cierre de la última fase, y el write-back de QMind se ejecutó **antes** de archivar el plan (`git mv` a `Archives/`, orden R2.10).
