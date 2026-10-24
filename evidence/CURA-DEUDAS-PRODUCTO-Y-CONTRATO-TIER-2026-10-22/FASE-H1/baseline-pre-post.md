# FASE-H1 — baseline PRE/POST y población de consumidores (R2.3/R2.7)

**Unidad**: funciones de test contadas por el método canónico del repo
(`grep -rE "^\s*def test_" tests --include=*.py | wc -l`), medido sobre el árbol de trabajo.

| Momento | Funciones `def test_` | Cómo se midió |
|---|---|---|
| PRE (apertura de la sesión, árbol en `2d2b48c` limpio) | **5.455** | comando anterior, antes del primer `Edit` |
| POST (cierre de la fase) | **5.478** | mismo comando, después de los dos archivos nuevos |
| Delta | **+23** | 14 en `tests/scrapers/test_fase_h1_gbp_score_denominador.py` + 9 en `tests/scrapers/test_fase_h1_booking_stub_retirado.py` |

**Antecedente que la resta no cierra sola**: `09-documentacion-post-proyecto.md` §D publica 5.454 como
cierre de FASE-F y el commit posterior `2d2b48c` (el piquete del fallback del tier) añade una función.
La resta de esta fase se ancla a los **5.455 medidos al abrir**, no al número commiteado de la fase anterior.

**Tests re-escritos, no añadidos** (cuentan igual en PRE y POST): `tests/providers/test_autonomous_research_fase8.py`
— `test_scraper_booking_scrape` y `test_scraper_booking_data_structure` afirmaban el `found=True` del stub; hoy
afirman el estado retirado. Su verde anterior certificaba el defecto (`L-T4A.5`).

**Verificador mecánico de la resta**: no existe (`L-R.4`). La resta se declara y la evidencia es el par crudo
`pytest-seleccion-fase-h1.txt` + `par-rojo-verde-mutantes.md`.

## Población declarada de consumidores del denominador (Tarea 1: medir antes de cambiar)

Dos vocabularios distinto se leían como uno. La columna «destino» dice qué se corrigió en el código y qué queda
declarado con dueño.

### A. Rúbrica GBP — productor `_calculate_gbp_score`, techo `SCORE_GBP_MAXIMO` (90)

| Sitio (símbolo) | Forma medida antes | Destino |
|---|---|---|
| `GBPAuditor.generar_reporte_ejecutivo` | `Score actual GBP: {score}/100` | **CORREGIDO** → `/{SCORE_GBP_MAXIMO}` |
| `GBPAuditor._scrape_maps_profile` | segunda rúbrica inline (`20+15+15+15+10+10+5`) | **UNIFICADO** → llama al productor único. Corrección al contexto de deudas: ubicaba la rúbrica en `check_google_profile`; medido por AST, vive en `_scrape_maps_profile` |
| `GBPAuditor._calculate_gbp_score` | copia de la rúbrica con 0 llamadores | **PRODUCTOR ÚNICO** (lo llama `_scrape_maps_profile`) |
| `GBPAuditor._places_api_lookup` | `raise NotImplementedError` | **RETIRADO** — 0 llamadores medidos en `modules/`, `main.py`, `scripts/`, `tests/` |
| `GBPAuditor.get_competitor_score(use_api=…)` | rama API inalcanzable: `except Exception: pass` degradaba a la estimación y el `score_source="api"` no tenía productor | **RETIRADA la rama y el parámetro**; diente `test_score_source_api_es_inalcanzable_en_el_modulo` (literales de código, no prosa) |
| `GBPAuditor.get_competitor_score` (estimación) | `min(100, int((reviews/10)*rating*2))` con metodología de una línea | **DECLARADA escala propia**: `score_maximo=ESTIMACION_GBP_MAXIMO (100)`, `comparable_con_rubrica_gbp=False`, metodología que nombra el techo de la rúbrica |
| `GBPAuditor.audit_competitor_profile` | `geo_score` = valor de la rúbrica, sin denominador | **CORREGIDO**: publica `geo_score_maximo` en las dos ramas (cache y live_audit) |
| `CompetitorAnalyzer.audit_competitors_gbp` (log) | `GEO {geo_score}/100` sobre el valor auditado | **CORREGIDO** → usa el denominador que viaja del productor |

### B. Quedan declarados, con dueño (no son la superficie de `D16`)

| Sitio | Hecho medido | Dueño |
|---|---|---|
| `GooglePlacesClient.calculate_geo_score` → `v4_comprehensive.gbp.geo_score` → `main.py` y `v4_comprehensive` imprimen `/100` (2 + 3 sitios) | **correcto**: el cliente normaliza su fórmula cruda (techo 90) a 0-100 con `raw * 100/90`. No es la rúbrica del auditor y no se tocó | — (vocabulario legítimo, declarado) |
| `CompetitorAnalyzer` escribe en la **misma clave** `geo_score` tres escalas: Places normalizada (/100), el fallback `int(rating*20)` (0-100) y la rúbrica auditada (/90); `score_source` publica `places_api_real` / `cache` / `live_audit` / `gbp_audit` | la clave no distingue la escala; el consumidor compara `geo_score` del competidor contra `client_score` sin verificar denominador | **Operador / FASE-E2E**: renombrar la clave o sellar el denominador en el contrato de competidores (fuera de la superficie de score de H1) |
| `modules/generators/report_builder.py` — 4 sitios imprimen el valor de la rúbrica como `/100` (`Score GEO:`, la tabla «Su Hotel vs Promedio Regional», la fila «Usted» de la tabla de competidores y el bloque `[CHART]` del template por defecto) + 4 sitios del benchmark regional | el módulo se autodeclara `DEPRECATED` en su encabezado y quedó sin consumidores de producción con el retiro de `spark` (FASE-A); FASE-E ya lo dejó con un solo lector | **Declarado**: el texto fósil vive en una ruta retirada; su cura no cambia ningún artefacto publicado |
| `GBPLeakDetector.generar_reporte_ejecutivo` | mismo literal `/100`; es la copia que FASE-D marcó como muerta tras el relevo | **Declarado** (dueño FASE-D/oráculo retirado) |
| `config/regional_benchmarks.yaml` → `gbp_geo_score_threshold: 70` (4 regiones) | **0 lectores de producción** medidos (`grep` por símbolo en `modules/`, `main.py`, `scripts/`); solo lo citan `tests/config/test_config_benchmarks.py` y `tests/test_regional_benchmarks.py` | **FASE-H2** (`D18`: claves de config muertas) |

## Población del stub (`D24`)

| Sitio | Antes | Después |
|---|---|---|
| `modules/scrapers/booking_scraper.BookingScraper.scrape` | `found=True` + molde con `rating`/`review_count`/`price_range` en `None` y `photos=[]` | `found=False`, `data={}`, `data_status=STUB_RETIRADO` |
| `modules/scrapers/__init__.py` (export) | export silencioso del stub junto al resto de scrapers | marcado `LEGACY` + `STUB_RETIRADO` en el propio sitio del export; diente `test_el_export_se_declara_legacy_en_su_sitio` |
| `modules/providers/autonomous_researcher.BookingScraper` (scraper real del producto) | scraping httpx + BeautifulSoup con fallback verificado | **SIN CAMBIOS** — verificado por `test_scraper_real_intacto`/`test_la_retirada_no_se_filtra_al_scraper_real` y por la suite `tests/scrapers/test_booking_scraper.py` (verde) |
| `parse_review` / `extract_amenities` del stub | 0 consumidores en el repo (la única varilla homónima vive en `archives/deprecated_modules_20260304/tripadvisor_scraper.py`) | quedan: la fase retira la promesa de dato, no reescribe helpers muertos. **Declarado** |

## Estado del horque de benchmarks al abrir/cerrar la fase

Medido con `run_all_validations.py --quick` (ver crudo). El horque `v25_config.umbrales_decision` publicado y no
leído es deuda **declarada en FASE-E con decisión del Operador del 2026-10-23: reconciliarla después de la corrida
E2E**. FASE-H1 no tocó `data/benchmarks/*` ni `config/regional_benchmarks.yaml`; el `[2/13]` no cambia por esta fase.


## Consecuencia medida sobre un pin de FASE-H1 (re-declaración de población ajena)

`tests/config/test_umbrales_fotos_semantica.py` dejó pinchada la población de sitios de comparación de fotos
que FASE-F re-midió: **5 sitios en `modules/scrapers/gbp_auditor.py` y 14 en total**. Al unificar la rúbrica
(Tarea 1 de `D16`), la copia inline de `_scrape_maps_profile` desapareció y el pin cayó en rojo:

| Clave del pin | FASE-F publicó | Medido tras FASE-H1 | Destino |
|---|---|---|---|
| sitios en `modules/scrapers/gbp_auditor.py` | 5 | **3** | re-declarado a 3, con el motivo escrito junto a `POBLACION` |
| total de sitios en los 7 módulos vivos | 14 | **12** | re-declarado a 12 y el docstring del test dice qué fase movió la cuenta |
| nombres leídos (`FOTOS_RUBRICA_EXCELENTE`, `MIN_FOTOS_BRECHA`) | ambos | ambos | intacto: el assert `esperados <= leidos` sigue cortando si un nombre deja de leerse |

No se perdió umbral ni semántica: dos sitios eran la **segunda copia del mismo cálculo**, que es exactamente lo
que `D16` describe. El rojo del pin de FASE-F es, por tanto, un verde mal anclado a la duplicación, y su
mensaje («re-mide y re-declara la población») es el procedimiento que se siguió. `tests/config` queda en
24 passed.

## Atribución de los rojos de la suite completa (POST, `pytest tests/ -q`)

Crudo: `pytest-suite-completa-post.txt` — **5 failed, 5614 passed, 37 skipped, 4 xfailed in 548.54s**.
El aviso de la tarea en segundo plano reportó `exit code 0`: esa cifra es el exit del `echo` compuesto, no el de
pytest (lección del repo: el código de salida de un comando en segundo plano se lee del crudo).

| Rojo | Causa | Atribuición |
|---|---|---|
| `tests/config/test_umbrales_fotos_semantica.py::test_cada_sito_lee_su_umbral_nombrado[gbp_auditor]` | 5 → 3 sitios por la unificación de la rúbrica | **DE FASE-H1 — CURADO**: población re-declarada con el motivo en el test |
| `tests/config/test_umbrales_fotos_semantica.py::test_la_cuenta_total_de_sitios_es_la_re_medida_de_fase_f` | 14 → 12 sitios, misma causa | **DE FASE-H1 — CURADO**: idem |
| `tests/config/test_config_integration.py::test_all_config_files_have_description` | `config/secret_fragment_policy.yaml` no publica campo `description` | **PREEXISTENTE**: reprodujo FAILED en árbol `git archive HEAD` (crudo en la sección siguiente); esta fase no tocó `config/` |
| `tests/test_fase_h_onboarding_procedencia.py::test_el_preflight_recalculado_no_inventa_el_consentimiento` | «el documento del operador está en el árbol: negarlo también sería inventar» | **PREEXISTENTE**: reprodujo FAILED en el mismo árbol HEAD |
| `tests/quality_gates/jev_pilot/test_jev_pilot_deepseek_brazo.py::test_la_falta_de_deepseek_falla_antes_de_enviar_aunque_haya_clave_anthropic` | esperaba `CredencialAusente`, hubo `RedProhibida` («hubo un intento de envío») | **ACOPLAMIENTO DE ORDEN DE LA SUITE, no de esta fase**: en el árbol HEAD (sin `.env`) pasa solo y con `.env`copiado también pasa; en el árbol de trabajo pasa solo (15 passed) y pasa con la selección de FASE-H1 por delante (88 passed). Solo falla dentro de `pytest tests/` completo, por estado que deja un test anterior |

Crudo de la medicion en HEAD: `atribucion-head-rojos-especificos.txt`. Declaracion de instrumento: el arbol materializado con `git archive HEAD` **no es un baseline valido de la suite** — no tiene `.git` (los arneses `verify_packs`/`verify_index`/`lesson_relevance`/`registry` lo requieren), no tiene `.env` ni fixtures sin versionar y por eso imprime 74 failed / 63 errors. De esa corrida solo se leen los dos rojos que interesan, que alli reprodujeron FAILED. El tercero (`test_jev_pilot_deepseek_brazo`) pasa en HEAD, pasa en el arbol de trabajo aislado (15 passed) y pasa con la seleccion de esta fase por delante (88 passed): su rojo es de orden de coleccion dentro de `tests/` completo y queda con dueno **Operador/FASE-VERIFY** (no lo abrio este plan).

## Re-ejecucion despues de curar el pin (crudo en `crudo-quick.txt`)

`pytest tests/scrapers/test_fase_h1_* tests/providers/test_autonomous_research_fase8.py tests/scrapers/test_booking_scraper.py tests/config -q` → **1 failed, 135 passed, 1 skipped** (EXIT=1). El unico rojo es `test_config_integration.py::test_all_config_files_have_description` (preexistente, reproducido en HEAD): `config/secret_fragment_policy.yaml` no publica campo `description`. **Dueno: Operador** — ninguna fase de este plan escribe `config/secret_fragment_policy.yaml`; queda declarado, no curado aqui.

Gates de cierre, con el exit leido sin tubería y el crudo guardado: `run_all_validations.py --quick` **13/13 (EXIT=0)**, `build_lesson_index.py --check` **EXIT=0** (403 IDs), `validate_wiring.py --check` **EXIT=0**, `validate_document_integration.py` **EXIT=0**.
