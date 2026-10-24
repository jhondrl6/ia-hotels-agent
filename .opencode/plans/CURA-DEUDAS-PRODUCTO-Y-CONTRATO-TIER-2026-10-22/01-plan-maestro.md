# PLAN MAESTRO — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> **Fecha**: 2026-10-22 · **Versión objetivo**: 4.82.0 (minor: cambia comportamiento de producto — render comercial, contrato del veredicto, denominador del score GBP, retiro de una ruta deprecada) · **Estado por fase**: no se declara en esta cabecera; su dueño único es `06-checklist-implementacion.md` (con la entrada por fase de `docs/contributing/REGISTRY.md`). La frase «PREPARACIÓN CORREGIDA (prompts generados; ninguna fase ejecutada)» quedó retirada de este archivo al vencerse en el cierre de FASE-A (2026-10-22).
> **Origen**: absorción consciente de dos contextos — `.opencode/context/CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` (14 deudas `D16`–`D28`, 7 hallazgos `N1`–`N7`, causas raíz `R1`–`R6`) y `.opencode/context/CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` (ítems A y C). El primero se cita de **solo lectura** y no está publicado en QMind; el segundo está publicado, congelado y su copia recuperada del notebook coincide con la local.
> **Corrección de estrategia (sesión de preparación, 2026-10-22)**: el Operador aprobó las correcciones medidas contra el árbol vivo. Las decisiones aplicadas son: **`spark` se retira** (no se repara), **`D16` publica `/90` y elimina la rama API muerta**, **`D24` declara muerto el stub y no toca el scraper real**, **`D21`/`P6.5` no se absorben** y **`D26` sigue diferida**. En esa sesión no se escribió código ni se ejecutó `v4complete`.

## §0. Veredicto en una línea

La cura se ancla en el **camino real del producto** y no en las filas de una tabla: **8 fases de implementación** (A, B, C, D, E, F, H1, H2), un **ensayo determinista previo** (E2E-PRE), **una corrida real** (E2E), **VERIFY** y **RELEASE**. `N1`/`D19` se cierran retirando la ruta `spark`; `D21` y `D26` quedan fuera; `D16` y `D24` se resuelven con las decisiones aprobadas. La corrida de Don Alfonso prueba el paquete de un hotel tier B+ con veredicto honesto y ZIP real, no un reproductor sintético.

## §1. Criterios de Aceptación (verificación al cierre de cada fase; certificación formal en FASE-VERIFY)

Cada AC declara **el artefacto y la clave exacta donde se lee su valor** (R2.4). Si la corrida no ejercita el camino, se declara.

| AC | Criterio | Artefacto y clave | Fases |
|----|----------|-------------------|-------|
| AC1 | La propuesta **y el diagnóstico** renderizados con tier B+ emiten **0** `OVER_PRESENTATION` (`summary.over_presentations == 0`), usando el revisor real; con tier A se emite la variante respaldada por evidencia y el escáner sigue apagado por diseño. Los labels financieros “Fuga total”/“Total recuperación” se conservan. | `revision_honestidad.json` → `summary.over_presentations`, `findings[]`; par rojo/verde de FASE-B en `evidence/…/FASE-B/` | FASE-B, FASE-E2E |
| AC2 | El veredicto condicional publica con `conditional_reason` que distingue `ANALYTICS_CEILING`, `ONBOARDING_INCOMPLETE` y `UNCERTIFIABLE_CLAUSES`; 0 ocurrencias vivas del literal `APROBADO-CONDICIONAL-PENDING-ONBOARDING` en la población declarada de código y tests. `P6.5` **no** entra a este AC: queda con su dueño. | `acta_revision.json` → `verdict`, `conditional_reason`; grep de la población declarada; evidencia FASE-C | FASE-C, FASE-E2E |
| AC3 | El contrato GBP se cumple en **ambos** caminos: `get_detected_issues` devuelve 0 brechas con la forma real de `_base_profile()` y `PainSolutionMapper`/`_map_brecha_to_issue_type` no convierte “sin schema” en `PERFIL_ABANDONADO`. Un perfil completo produce 0 brechas y 0 COP por brechas inexistentes. | Test de frontera de FASE-D; `pain_ledger.json` → `brechas_en_ledger`; par rojo/verde en evidencia | FASE-D |
| AC4 | `BenchmarkLoader` lee el JSON publicado en todos sus getters; las cinco tablas regionales quedan derivadas o retiradas; la sincronización compara valores y conserva el chequeo de parseo/versión. | Salida del check de sincronización en `run_all_validations.py` + test de getters y paridad; evidencia FASE-E | FASE-E |
| AC5 | `spark` deja de ser una ruta de estimación rota: el comando informa su retiro y sale sin `AttributeError`; `_map_audit_to_spark_data` desaparece o deja de referenciar `FinancialFactors.SUPERPOSITION_FACTOR`; el lector latente de `gap_analyzer` se corrige y el guardián detecta atributos inexistentes. | stdout/exit del test CLI `spark`; par rojo/verde del guardián en `evidence/…/FASE-A/` | FASE-A |
| AC6 | Los umbrales de fotos se declaran por semántica (mínimo, oportunidad, banda de rúbrica, objetivo), no como un valor único; cada uno vive en un sitio; `D25-bis` tiene una sola fuente y `D27` nombres por semántica tras FASE-D. | Config/test de coherencia; grep por símbolo (no por literal global); evidencia FASE-F | FASE-F |
| AC7 | La corrida `v4complete` de Don Alfonso **publica un ZIP real** en `deliveries/` (`suppressed:false`, sha y tamaño), con 0 `OVER_PRESENTATION`, pérdida del escenario financiero honesta (3.511.200 COP/mes del baseline o la re-medida), 11 brechas de `PainSolutionMapper` re-medidas y onboarding cargado desde una fuente que casa por URL. | `v4_complete_report.json`, `acta_revision.json`, `summary.over_presentations`, `pain_ledger.json`, ZIP real y su inventario; evidencia FASE-E2E | FASE-E2E |
| AC8 | `D16` publica el score GBP sobre `/90` y retira la rama API muerta; `D24` marca el stub como retirado (`found=False`, `data_status=STUB_RETIRADO`) sin tocar `autonomous_researcher.BookingScraper`; `D18`, `D22`, `D23` y `D20` se cierran o se declaran diferidas con dueño. | Salida GBP con `/90`; test del stub; `settings.yaml` sin claves muertas; docstring y comportamiento de `_check_claim_vs_evidence`; `Benchmarking.md` con fuente declarada | FASE-H1, FASE-H2 |

**Mutation checks (R2.8)**: AC1, AC3 y AC5 no se cierran con el test verde; guardan su par rojo/verde en `evidence/` (condición del render desactivada; claves inglesas restauradas; atributo inexistente). AC2 guarda el rojo del literal viejo y AC8 el rojo del score `/100` o del stub `found=True`.

## §2. Alcance: absorción y vallas

**Se absorben**: ítem A (contrato plantilla↔tier), ítem C (nombre y causa del veredicto condicional), y las deudas `D16`, `D18`, `D20`, `D22`, `D23`, `D24`, `D25`, `D25-bis`, `D25-ter`, `D27`, `D28` con sus hallazgos `N2`–`N7`.

**Se cierran por retiro, no por reparación**: `N1`/`D19` (ruta `spark`). El Operador decidió retirar la ruta; el lector latente de `gap_analyzer` se corrige como higiene de contrato y el guardián se conserva.

**Vallas que este plan NO disuelve**:
- **Ítem B fuera**: no se busca una ruta a tier A sin analytics.
- **`S-CST-1` fuera**: el gate blocking `hard_contradictions` no puede fallar en producción; dueño Operador.
- **`D21`/`P6.5` fuera**: no se absorben sin letra expresa del Operador. La fila `P6.5` y `T1_CERTIFIABLE_CLAUSES` no se tocan. Dirección (b) de `P6.5` y la evaluabilidad de `P6.2` siguen diferidas.
- **`D26` diferida**: falta el enunciado original de la fórmula; no se improvisa.
- **Alias de IDs**: los tokens `D16`–`D28`, `N1`–`N7` se conservan; ningún prompt los escribe en grafía conforme sin celda de definición.

**Regla de camino**: ninguna fase puede declarar curada una deuda sin nombrar el **productor**, el **consumidor** y el **artefacto** que la leen. La matriz de camino de §8 es obligatoria antes de FASE-A.

## §3. Fases, complejidad y modo de ejecución

| Fase | Alcance | Complejidad | Modo |
|------|---------|-------------|------|
| FASE-A | `N1`/`N7`/`R4`: retiro de `spark`, higiene del lector latente de `gap_analyzer`, guardián por existencia y barrido de lectores huérfanos de `1501dd8` | MEDIA-ALTA | Directo (imports); barrido delegable con `Agent` |
| FASE-B | Ítem A: render condicionado al tier para los **2** claims del revisor, en propuesta y diagnóstico, con diente | ALTA | Directo (revisor real; copy comercial) |
| FASE-C | Ítem C: veredicto con `conditional_reason` y `has_onboarding`; `P6.5` intacta | MEDIA | Directo (contrato cross-module) |
| FASE-D | `R1`: contrato GBP en `get_detected_issues` y `PainSolutionMapper`; tri-estado de schema; `N2`/`N3` | ALTA | Directo (decisión arquitectónica) |
| FASE-E | `R2`: un solo lector de benchmarks, cinco tablas derivadas/retiradas y verificador real cableado | ALTA | Directo; verificación de getters delegable con `Agent` |
| FASE-F | `R3`: umbrales por semántica, `D25-bis` y `D27` post-D | MEDIA | Directo; barrido mecánico delegable con `Agent` |
| FASE-H1 | `D16` (`/90`, rama API muerta) y `D24` (stub retirado) con AC8 | MEDIA | Directo (decisiones registradas) |
| FASE-H2 | `D18`, `D22`, `D23`, `D20`: limpieza y honestidad de texto; `D26` fuera | BAJA | Directo; `D20` documental delegable con `Agent` |
| FASE-E2E-PRE | Ensayo determinista del baseline: onboarding, render B+, revisor real, juez real y ensamblaje de paquete; **sin inferencia pagada** | MEDIA | Directo, no delegable |
| FASE-E2E | Corrida única de `v4complete` de Don Alfonso + evidencia + análisis | MEDIA | Directo con `Bash` en segundo plano; `Agent` solo para el comando |
| FASE-VERIFY | Certificación AC1–AC8 contra artefactos reales (sin código, sin `v4complete`) | MEDIA | Directo, no delegable |
| FASE-RELEASE-4.82.0 | Cierre documental, write-back QMind y archivado por R2.10 | BAJA | Directo o `Agent` (solo YAML/MD/scripts) |

**Una fase = una sesión.** Cada fase registra su cierre con `log_phase_completion.py`; RELEASE solo verifica el registro.

## §4. Restricciones globales

1. **R2.2**: citas por **símbolos**; nunca `archivo:línea` en ACs, prompts o evidencia.
2. **R2.3/R2.7**: todo conteo es delta con par `*_baseline_pre.txt`/`*_baseline_post.txt`; la resta se publica en `baseline-pre-post.md`. El verificador mecánico de la resta no existe: se declara (`L-R.4`).
3. **R2.8**: mutation check por AC de detección, sobre el símbolo real del guard.
4. **Congelados de solo lectura**: `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md`, `CONTEXT-JEV-COSTURA-V4COMPLETE-2026-10-10.md` y el `10-analisis` de `CURA-COSTURA-TRIBUNAL-2026-10-11`. `CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` es insumo medido: se cita, no se edita desde las fases. `P6.5`/`D21` no se tocan.
5. **Gobernanza declarada**: el plan cita el contexto de deudas desde documentos de plan; ese contexto no está publicado. Si se ejecuta la cura de la segunda vía del verificador de frescura, su publicación va en el mismo ciclo. El contexto de CONTRATO sí está publicado y su copia recuperada del notebook coincide con la local.
6. **Commits**: ningún prompt autoriza commit; cada commit requiere letra del Operador con pathspec explícito.
7. **Presupuesto**: tope 60 `tool_use` por sesión; corte “listo para revisión”. `evidence/FASE-D/measure_iterations.py` es un instrumento legado que lee transcripts tipo Claude; **no se declara canónico** hasta comprobar que el transcript del runtime actual es compatible. Si no lo es: auto-reporte en unidad `tool_use`, marcado **no comparable**.
8. **Sin cuota de lecciones**: “sin lecciones nuevas” es resultado válido.
9. **Rutas medidas**: ningún prompt usa `modules/…`, `tests/…` ni rutas inventadas. Las rutas corregidas son: `modules/analyzers/gap_analyzer.py`, `modules/utils/dynamic_impact.py`, `modules/generators/report_builder.py`, `modules/auditors/v4_comprehensive.py`, `modules/commercial_documents/data_structures.py`, `modules/commercial_documents/v4_diagnostic_generator.py`, `modules/financial_engine/opportunity_scorer.py`, `modules/scrapers/booking_scraper.py` (método `scrape`, no `scrape_hotel`) y `modules/providers/autonomous_researcher.py` (scraper real del producto).
10. **Poblaciones de AC**: (a) atributos de código: AST, no grep de menciones; (b) literales: rutas de código y tests declaradas, con allowlist de históricos (`VERSION.yaml`, `CHANGELOG.md`, `context/`, `Archives/`, `evidence/`, `qmind-writeback/`) y motivo; (c) umbrales y valores: por símbolo con nombre, no por literal global; (d) publicación: ZIP real, nunca “registro” como sustituto.

## §5. Decisiones registradas

| Decisión | Fase | Estado |
|----------|------|--------|
| `spark` se retira; no se repara la estimación | FASE-A | **Aprobada por el Operador en esta corrección** |
| `D16`: publicar score GBP sobre `/90` y eliminar la rama API muerta (`_places_api_lookup` no implementada) | FASE-H1 | **Aprobada por el Operador en esta corrección** |
| `D24`: declarar muerto el stub de `modules/scrapers/booking_scraper.py`; no tocar `autonomous_researcher.BookingScraper` | FASE-H1 | **Aprobada por el Operador en esta corrección** |
| `D21`/`P6.5`: no absorber; queda con su dueño hasta letra expresa | fuera de alcance | **Aprobada por el Operador en esta corrección** |
| `D26`: diferida sin enunciado original | fuera de alcance | Aprobada |
| Cinco bloques sin dato en el JSON: `DEFAULT_DATA` se declara maestro por escrito con assert de coherencia | FASE-E | Default del plan; se escribe antes de tocar el lector |
| `gbp_leak_detector`: sustitución, no borrado; su lógica de vocabulario español sobrevive como implementación del contrato y la copia muerta se retira tras el relevo | FASE-D | Default del plan; se confirma al abrir la fase |
| `P6.5` y `T1_CERTIFIABLE_CLAUSES` no se tocan | fuera de alcance | Aprobada |

## §6. Pertinencia de la corrida `v4complete` (evaluada, no supuesta)

**PERTINENTE para A, C y el revpar regional de E; NO pertinente para `D28`, `D19` ni `D24`.** Razones medidas:

1. La corrida ejercita la propuesta renderizada, el acta del tribunal y los escenarios financieros que consumen el `revpar` regional. No ejercita `get_detected_issues` (ruta `v4audit`), ni `spark` (retirado), ni `BookingScraper` (research).
2. Baseline congelado: la corrida del 2026-10-12 para Don Alfonso (`evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/`) salió `BLOQUEADO` con 2 `OVER_PRESENTATION` CRITICAL, 3.511.200 COP/mes de pérdida realista y 11 brechas de `PainSolutionMapper`. El 39.600.000 COP/mes del contexto de deudas es un **reproductor sintético** de `get_detected_issues` sobre perfil perfecto, no la cifra del baseline.
3. Éxito de AC7: ZIP real en `deliveries/`, `suppressed:false`, sha y tamaño, 0 `summary.over_presentations`, pérdida del escenario financiero y 11 brechas re-medidas. Un “registro” sin ZIP no satisface AC7.
4. Coste: una corrida con extracción pagada (recibos `deepseek`). El ensayo E2E-PRE no gasta inferencia y debe pasar antes de la corrida.
5. Onboarding: el baseline usó `output/clientes/hotel_don_alfonso_onboarding.yaml`, que está **gitignorado**; la copia versionada vive en `evidence/…/hotel_don_alfonso_onboarding.yaml`. El `observations.json` tiene a Don Alfonso con website `hoteldonalfonso.com`, que **no casa** por host con `www.donalfonsohotel.com`. El preflight materializa el YAML versionado y afirma que `_load_latest_onboarding_data()` lo devuelve; el Operador confirma el dominio antes de la corrida.
6. El análisis post-implementación se nutre de la corrida y de E2E-PRE; la pertinencia de cada lección se decide al cierre (INCLUIR/EXCLUIR, sin cuota).

## §7. Insumos

- `.opencode/context/CONTEXT-DEUDAS-PRODUCTO-VERIFICADAS-2026-10-21.md` — definiciones `D16`–`D28`, hallazgos `N1`–`N7`, causas raíz `R1`–`R6`. Solo lectura.
- `.opencode/context/CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12.md` — ítems A y C, mecanismo del tier/veredicto, inventario y `P6.5` medido. Congelado y publicado.
- Baseline E2E: `evidence/CURA-COSTURA-TRIBUNAL-2026-10-11/FASE-E2E/` (acta, `revision_honestidad.json`, `01_DIAGNOSTICO`, `02_PROPUESTA`, `financial_scenarios`, `pain_ledger`, recibos y `hotel_don_alfonso_onboarding.yaml`).
- Knowledge Center: `CONTEXT-CONTRATO-PLANTILLA-TIER-2026-10-12` publicado (score 0.978 en la consulta de recuperación). No hay fuente QMind para `get_detected_issues`/`BenchmarkLoader`: esas deudas son mediciones locales del contexto de deudas y del árbol.
- Flujo canónico: `.agents/workflows/phased_project_executor.md` + `docs/CONTRIBUTING.md`.

## §8. Matriz de camino y trazabilidad de la corrección

| Deuda/hallazgo | Productor real | Consumidor real | Artefacto | Fase |
|---|---|---|---|---|
| `D28`, `N2`, `N3` | `get_detected_issues` (v4audit) y `PainSolutionMapper` (v4complete) | `gbp_auditor._detectar_fugas` y `V4DiagnosticGenerator` | `v4_audit` / `01_DIAGNOSTICO` | D |
| `D25-ter`, `N4`, `N5`, `N6` | `BenchmarkLoader` | `FinancialFactors`, `package_recommender`, `dynamic_impact` | escenarios/propuesta | E |
| `D25`, `D25-bis`, `D27` | umbrales y factores | `dynamic_impact`, `gbp_auditor`, `opportunity_scorer`, `v4_proposal_generator` | diagnóstico/propuesta | F |
| `N1`, `D19`, `N7` | `_map_audit_to_spark_data` + `gap_analyzer` | `spark` (retirado) + guardián | `spark_report` / tests | A |
| `D16` | `_calculate_gbp_score` / `get_competitor_score` | reporte GBP | puntaje `/90` | H1 |
| `D24` | `modules/scrapers/booking_scraper.py` (stub) | tests; el producto usa `autonomous_researcher.BookingScraper` | research.json | H1 |
| `D18`, `D22`, `D23`, `D20` | config/docstring/docs | tests y documentación | config/reportes | H2 |
| Ítem A | plantillas y generadores | `HonestyReviewer` | propuesta y diagnóstico | B |
| Ítem C | `TribunalJudge` | acta y `main.py` | `acta_revision.json` | C |

**Correcciones aplicadas respecto de la preparación anterior**: (1) rutas inexistentes corregidas; (2) `spark` retirado y `D19` cerrado por retiro; (3) `D28` separado por pipeline; (4) `D21`/`P6.5` fuera; (5) `D16` y `D24` con decisiones registradas; (6) AC1 lee `summary.over_presentations`, no `critical_count`; (7) AC7 exige ZIP real; (8) E2E-PRE determinista antes de gastar la corrida; (9) onboarding materializado y dominio declarado; (10) `D25-ter` obliga a retirar/derivar las cinco tablas; (11) umbrales por semántica; (12) FASE-H partida en H1/H2; (13) poblaciones de grep declaradas; (14) herramientas del runtime corregidas (`Agent`, no `delegate_task`).
