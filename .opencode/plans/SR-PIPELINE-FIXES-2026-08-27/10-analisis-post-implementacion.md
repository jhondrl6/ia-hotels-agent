# Análisis Post-Implementación — SR-PIPELINE-FIXES-2026-08-27

> **Estado**: Preparación completada (2026-08-27) — 13 archivos del plan creados; 0 fases ejecutadas.
> **Plan**: SR-PIPELINE-FIXES-2026-08-27 (v4.72.2 → v4.73.0 "Alineación de Pipeline")
> **Causa raíz tratada**: capas desincronizadas que contabilizan distinto el mismo hecho (promesa/matriz/gate) + gates que detectan sin ciclar + identidad de memoria no canónica + preflight que castiga la evidencia del problema.
> **Regla**: este archivo se crea DESDE LA CONCEPCIÓN del plan (executor v2.15.0+) y se actualiza al cierre de CADA fase.

---

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-SR-A (helper unresolved) | Sesión 1 | ✅ | ~30 | NO (directo) | Helper único + bucket no_breach + guardián AST L-SR1; 148 tests (6 nuevos), 0 regresiones; N1 cerrado a nivel de CONTEO (decisión de bloqueo → SR-B) |
| FASE-SR-B (unificación) ⚠️ | Sesión 2 | ✅ | ~35 | NO (DT-3) | D-PF1: promesa derivada de pain_ledger + presencia (RC1↔matriz↔gate, fuente única); NO_BREACH fuera del coverage (3/4=0.75 corrida C, intermedio); 57 PASSED gates (10 contrato nuevos); 0 regresiones (8 preexistentes certificados en HEAD); greps residuos 0 |
| FASE-SR-C (self-healing) | Sesión 3 | ✅ | ~45 | NO (directo) | D-PF2: loop regenera con suggestion + re-valida (closure única), máx 1 reintento, persistencia → BLOCKED real; 20 tests nuevos (20/20), regresiones 79/27/57, 0 fallos; greps 0 caminos paralelos; quick 6/6 (Version Sync resuelto in-session) |
| FASE-SR-D (target_id) | Sesión 4 | ✅ | ~40 | NO (directo) | D-PF4: `canonical_url=_normalize_url(args.url)` en v4complete (3 call sites memoria + búsqueda), execute, validate-guarantee; onboard persiste URL sin query; `generate_hotel_id` normaliza via urlparse (log Phase 1 canónico); memory.py intacto; 28 tests nuevos (28/28) + regresión 108 en 7 suites, 0 fallos; greps 0; quick 6/6 |
| FASE-SR-E (schema detect + presencia) | Sesión 5 | ✅ | ~45 | NO (directo) | H7: parser JSON-LD ARRAY + parse_errors por bloque + error_message propagado al audit (L-SR5); criterio canónico `is_present_in_production` (6 consumidores); D-PF3 residual (fallback catálogo / justified_skip); 31 tests nuevos (31/31) + regresión 148, 0 fallos; greps 0 residuos; quick 6/6 |
| FASE-SR-F (varianza+OPS) | Sesión 6 | ✅ | ~55 | NO (directo) | H5: sondas robots/llms con query UTM medían homepage 200 → exclusión determinista de ai_crawler_blocked (0.5) y low_ia_readiness (0.34674) — 7→5 pains/assets; delta ia_readiness 22.222 reproducible con pesos; D-PF6=FIX en 3 sondas ancladas al origen (mapper inocente); 15 tests nuevos + regresión 58, 0 fallos; PageSpeed: keys distintas (GOOGLE_PAGESPEED_API_KEY inválida; rotación = usuario) |
| FASE-SR-G (display) | Sesión 7 | ✅ | ~45 | NO (directo) | H6.3: la hipótesis del plan era FALSA — el renderer era inocente; el EXTRACTOR `_extract_text_tier` fabricaba 'D' capturando la 'd' de "Nivel de evidencia"; fix = regex canónico solo MAYÚSCULAS + lookahead de letra (no `\b`: backtracking "B+"→"B"); gate intacto; desviación fundamentada: fuente = evidence_tier del financial engine, NO pricing.yaml (intacto). H6.4: glosario único `tech_jargon_glossary.py` (detección+mapeo+patrón compartido, guardia "sin costo (fallback)") consumido por gate y ambos generadores (apply_glossary post-render, L-SR3/L-NC10); 18 tests nuevos, 147 PASSED aislados, 5 preexistentes certificados en HEAD, 0 regresiones; greps 0; quick 6/6 |
| FASE-SR-H (E2E Salento Real) | Sesión 8 | ✅ | ~20 | SÍ (v4complete, subagente) | Corrida única OK (exit 0, ~1m40s); evidencia baseline+final capturada (Protocolo Proactivo); smoke 5/7 — 2 fallas con causa única: gate `critical_recall` BLOCKED ("metric not found") porque el fix de SR-E eliminó el único critical_issue (el falso negativo de schema del baseline); financiera IDÉNTICA al baseline (AC10 OK); veredicto NOT_READY → escalado a decisión pre-VERIFY (ver §Resumen E2E) |
| FASE-SR-H2 (hotfix critical_recall) | Sesión 9 | ✅ | ~25 | SÍ (v4complete, subagente) | Fix `_extract_critical_recall` (lista vacía+audit=1.0 con traza `recall_basis`; sin audit=BLOCKED real, L-SR5); 4 tests de contrato TDD (2 rojos nuevos + 2 guards del BLOCKED preservado); regresión aislada 58+25+12 + 1 preexistente certificado HEAD; corrida D-PF7 delegada única (exit 0, ~1m50s, output nuevo); smoke **7/7** → READY_FOR_PUBLICATION (AC11/AC12 observables); financiera idéntica (AC10) |
| FASE-SR-VERIFY (ACs) | Sesión 10 | ⏳ | — | NO (§4.6) | |
| FASE-RELEASE-4.73.0 | Sesión 11 | ⏳ | — | opcional | |

---

## Resumen E2E (FASE-SR-H — Observed real vs baseline, 2026-08-28)

**Corrida**: `v4complete --url https://www.hotelsalentoreal.com/ --output output/salentoreal_final_v4c` (canónica limpia, L-SR2) · exit 0 · ~1m40s · evidencia: `evidence/FASE-SR-H/{baseline,final}/` + `corrida.log` + `smoke_result.json`.

### Smoke 7 checks: 5/7 PASSED

| # | Check | Resultado | Detalle |
|---|-------|-----------|---------|
| 1 | Veredicto READY_FOR_PUBLICATION | ❌ FAIL | `readiness.status = NOT_READY`; único bloqueo: `critical_recall` BLOCKED |
| 2 | Coherence ≥ 0.8 | ✅ PASS | 0.88 (baseline 0.8644, +0.0156); post-gen 0.88, commercial gates 3/3 |
| 3 | promised_assets_exist + schema por PRESENCIA | ✅ PASS | gate PASS score 1.0 (7 servicios via PROPOSAL_SERVICE_TO_ASSET); audit `hotel_schema_detected=True, valid=True, confidence=verified`; `no_hotel_schema` AUSENTE de pain_ledger/matriz/coherence (AC6 observado) |
| 4 | Unresolved idéntico gate vs delivery | ✅ PASS | 0 == 0 (fin del 4-vs-1, AC3 observado) |
| 5 | 01_DIAGNOSTICO + 02_PROPUESTA presentes | ❌ FAIL | Derivada de #1: GATE BLOCKING ACTIVE eliminó los docs cliente y generó BLOCKED_BY_GATES.md (comportamiento correcto del mecanismo SR-C) |
| 6 | ZIP de entrega | ✅ PASS | `deliveries/hotelsalentoreal_20260828.zip` (Pre-ZIP Gate 5/5) |
| 7 | Financiera idéntica al baseline | ✅ PASS | $6,571,622.4 / $4,042,752.0 / $1,264,435.2 COP — idénticos (AC10 OK) |

### Post-mortem del bloqueo (causa raíz documentada)

**Síntoma**: `critical_recall` BLOCKED — "Critical recall metric not found in assessment".

**Cadena causal** (verificada contra evidencia baseline vs final):
1. Baseline C: `critical_issues = ["No Hotel schema detected - critical for SEO"]` — el único critical issue era el FALSO NEGATIVO de schema (bug H7 que SR-E corrigió).
2. SR-E funciona según diseño: la corrida final detecta los schemas reales del sitio (`hotel_schema_detected=True`) → `critical_issues = []` (resultado genuinamente bueno).
3. `_extract_critical_recall` (`modules/quality_gates/publication_gates.py:1850-1862`) trata lista VACÍA como "métrica ausente" (retorna `None` → BLOCKED), en vez de "0 issues críticos = nada que recordar".
4. El bloqueo dispara GATE BLOCKING ACTIVE: docs cliente eliminados + BLOCKED_BY_GATES.md (checks 1 y 5 del smoke).

**Clasificación**: bug LATENTE en el gate (ninguna fase SR-A…G lo introdujo; SR-E lo expuso al corregir el falso negativo que mantenía la lista no-vacía). **Fase responsable de exposición**: SR-E. **Fix pendiente**: `_extract_critical_recall` debe distinguir "dato ausente" de "resultado favorable" (lista vacía → recall 1.0 o camino N/A explícito) + test con `critical_issues=[]`. **Decisión requerida ANTES de FASE-SR-VERIFY** (AC11 no certificable mientras tanto): hotfix en sesión propia (fuera del scope de SR-H — fase de ejecución sin código, restricción respetada).

**Confirmado OK en la corrida**: AC3 (unresolved 0=0), AC5 implícito (hotel_id canónico `hotel_hotelsalentoreal.com`), AC6 (schema detectado, pain ausente, presencia contabilizada), AC10 (financiera idéntica), AC13 (guardián intacto). Pendientes de certificación formal en VERIFY: AC1, AC2, AC4, AC7, AC8, AC9, AC11, AC12.

---

## Matriz de Verificación de Hallazgos (llenar en FASE-SR-VERIFY; fuentes: `evidence/FASE-SR-H/baseline/` vs `output/salentoreal_final_v4c/`)

### Baseline de referencia (corrida C, 2026-08-27 18:30): NOT_READY — 12/13 PASSED, alignment 43% (3/7), coherence 0.8644, unresolved gate=4 vs delivery=1, hotel_schema DETECTED, target_id con UTM, claim falso publicado, tier 'B' vs 'D'.

| # | Hallazgo | Expected | Real | Status |
|---|----------|----------|------|--------|
| AC1 | Gate proposal_asset_alignment NO bloquea por NO_BREACH ("sin costo") | coverage_ratio ≥ 0.80; gate PASSED en corrida final | ⏳ | ⏳ |
| AC2 | Promesa derivada del pain_ledger + present_in_production | Propuesta no promete servicios sin pain ni presencia; estados coherentes propuesta↔matriz↔gate | ⏳ | ⏳ |
| AC3 | Unresolved idéntico en gate_report y delivery_quality_report | Mismo número `unresolved` en ambos reportes del MISMO run (fin del 4-vs-1) | ⏳ | ⏳ |
| AC4 | Claims vs evidencia ciclan | 0 claims "no aparece" contradiendo GBP publicados (o BLOCKED real) | ⏳ | ⏳ |
| AC5 | target_id canónico | target_id sin query string en log de corrida final; unit tests UTM≡limpia | ⏳ | ⏳ |
| AC6 | Detección schema correcta + contabilización única | Audit detecta schemas del sitio (fixture real ≥ 2 Hotel, incl. array JSON-LD); pain no_hotel_schema no generado; exists_with_issues = present_in_production | ⏳ | ⏳ |
| AC7 | Coherencia resuelta (revisión 2026-08-28) | coherence_validation sin "Assets no implementados: hotel_schema"; score ≥ 0.8; ausencia genuina cubierta por fallback catálogo (D-PF3) | ⏳ | ⏳ |
| AC8 | Varianza explicada | Informe con hipótesis verificada del 7→5 (o fix con test) | ⏳ | ⏳ |
| AC9 | Display sincronizado | 0 WARNING CG-TIER-CONSISTENCY; jerga reducida vs baseline | ⏳ | ⏳ |
| AC10 | 0 regresión financiera | Escenarios idénticos al baseline: $6.57M / $4.04M / $1.26M COP | ⏳ | ⏳ |
| AC11 | readiness READY_FOR_PUBLICATION | `readiness = READY_FOR_PUBLICATION` en v4_complete_report | ⏳ | ⏳ |
| AC12 | Entregables publicables | Sin BLOCKED_BY_GATES.md; 01/02 presentes; ZIP no abortado | ⏳ | ⏳ |
| AC13 | Guardián estático L-SR1 | Test AST pasa; `grep "logger\." main.py` = 0 | ⏳ | ⏳ |

---

## Lecciones Aprendidas

### Lecciones capitalizadas de planes anteriores (REFACTOR-COHERENCIA-NARRATIVA-2026-08-22 + CONTEXT Salento Real)

| Lección | ID original | Aplicación en este plan |
|---------|-------------|--------------------------|
| Ramas no ejercitadas acumulan defectos latentes; smoke E2E con `--output` alternativo + grep de símbolos sospechosos + test estático | L-SR1 | Guardián AST permanente (SR-A); corrida final con `--output` alternativo (SR-H) |
| La identidad de memoria debe derivarse de la URL canónica | L-SR2 | SR-D completo (canonicalización en caller) |
| Promesa, matriz y gate comparten UNA fuente de verdad del estado de un servicio | L-SR3 | SR-B completo (taxonomía única) |
| La confianza de un asset no se degrada por la evidencia del problema que resuelve | L-SR4 | SR-E completo (confianza desde fuentes para construir el asset) |
| Un gate BLOCKING que solo loggea no previene: debe ciclar o escalar | L-SR5 | SR-C completo (self-healing con escalado a BLOCKED real) |
| Fosilización narrativa/decisoria: la capa que no consume la fuente de verdad produce hallazgos recurrentes | L-NC10 | SR-B (promesa consume pain_ledger, no catálogo estático) |
| Verificación E2E > unit tests; variaciones de parámetros detonan ramas ocultas | L-NC11 | SR-H con `--output` alternativo; VERIFY certifica contra output real |
| Diff antes/después como evidencia formal obligatoria | L-NC12 | SR-VERIFY: diff corrida C vs corrida final en todas las zonas afectadas |
| Tras parametrizar, verificar strings de display contra la fuente | L30 | SR-G: extractor de tier alineado a la forma canónica (MAYÚSCULAS) del valor que renderiza el template; el gate compara tokens canónicos, nunca prosa |
| Citar fuente de verdad, no hardcodear | L27 | SR-B/SR-G: promesas desde pain_ledger; jerga→negocio desde glosario único (texto publicado = fuente interna × transformación compartida `apply_glossary`, sin texto duplicado) |
| El gap está en el caller: verificar si el helper ya existe | L16 | SR-D usa `_normalize_url()` existente (main.py:3542); SR-A reutiliza rutas de conteo existentes |
| Grep de residuos post-fix | L2 | Cierre de cada fase (0 matches) |
| Tests de contrato contra fuente dinámica, no valores fijos | L3 | SR-B: tests propuesta↔matriz↔gate contra pain_ledger real |
| Para contratos transversales, AST en vez de regex | L7 | SR-A: guardián AST para main.py |
| Símbolo no definido en rama no ejercitada (clase de bug H1/L-NC8/L-NC9) | L-NC8/9 | Guardián AST + smoke de ramas nuevas en cada fase |
| Ejecución segura de suites pytest (memoria 2026-08-03) | — | Archivos específicos, procesos aislados, salida a archivo, sin suite completa |
| log_phase_completion SIN --release en fases intermedias (memoria cierre de fase) | — | Todos los prompts de fase; solo RELEASE usa marker |

### Lecciones nuevas de este plan (L-PF1+ — registrar al cierre de cada fase; mínimo 3 totales)

> Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR de memoria).

| ID | Lección | Fase |
|----|---------|------|
| L-PF1 | QUÉ PASÓ: dos reportes del MISMO run reportaban unresolved distinto (4 vs 1). POR QUÉ: el DTO AlignmentResult tenía dos paths de construcción que re-derivaban "unresolved" con reglas distintas (len(report.missing) vs suma de estados) — el AlignmentReport pierde la taxonomía NO_BREACH. QUÉ LO PREVIENE: UN helper canónico (compute_unresolved) consumido por ambos reportes + el caller deriva la taxonomía con el MISMO builder que ya produce el artefacto (AssetAlignmentMatrix.build desde pain_ledger) + test de igualdad entre paths. Pertinencia: INCLUIR en memoria (patrón de unificación de conteo en DTOs multi-consumer). | SR-A |
| L-PF2 | QUÉ PASÓ: el gate bloqueaba con coverage 3/7 mientras la propuesta mostraba solo 3 filas y la matriz marcaba 3 servicios como "sin costo" — tres contabilizaciones del mismo hecho desde dos fuentes distintas (catálogo estático del tier vs pain_ledger). POR QUÉ: la promesa provenía de un catálogo estático fosilizado que nadie reconciliaba con el pain_ledger (L-SR3/L-NC10); el gate contaba como missing servicios que la propia propuesta no prometía. QUÉ LO PREVIENE: UNA función derivadora única (comprometido = pain mapeado OR presencia `exists`) consumida por propuesta, matriz y gate + coverage_ratio sobre actionable (NO_BREACH fuera del denominador) + test de contrato de 3 capas contra pain_ledger real + fallback explícito al catálogo cuando no hay pain_ledger. Pertinencia: INCLUIR en memoria (fuente única de la promesa comercial entre capas de documentos y gating). | SR-B |
| L-PF3 | QUÉ PASÓ: un gate BLOCKING detectaba el claim falso "no aparece en Google" y solo loggeaba "hidden from client" — el documento se publicaba igual con la contradicción ante el cliente. POR QUÉ: el gate no tenía ciclo de corrección y el caller no consumía el resultado del gate tras la regeneración T4FIX. QUÉ LO PREVIENE: self-healing con el `suggestion` del gate como restricción de regeneración + re-validación con LA MISMA closure de validación (0 caminos paralelos) + guard anti-bucle (máx 1 reintento) + escalada explícita a BLOCKED real (docs retenidos + ZIP abortado) vía DTO tipado (`ClaimHealingResult`), no por parsing de JSON. Pertinencia: INCLUIR en memoria (patrón detect→ciclar→escalar para gates de contenido). | SR-C |
| L-PF4 | QUÉ PASÓ: el plan original de canonicalización solo cubría `target_id` (los 3 call sites de main.py) — la revisión causa-raíz 2026-08-28 descubrió una SEGUNDA identidad derivada de la misma URL cruda (`generate_hotel_id` en onboarding_controller, origen del hotel_id contaminado del log Phase 1), y en ejecución apareció una tercera identidad menor (hotel['url'] persistida por onboard). POR QUÉ: un mismo dato fuente (la URL) alimenta varias identidades con formatos y consumidores distintos (target_id de memoria, hotel_id de onboarding, website de assets) — un fix de identidad no está completo sin inventariar TODAS las derivaciones. QUÉ LO PREVIENE: al canonicalizar una identidad, grep de TODAS las identidades derivadas de la misma fuente (no solo la que motivó el hallazgo) + decidir por consumidor qué conserva cada una (memoria→canónica pura; website de assets→navegable sin query). Pertinencia: INCLUIR en memoria (inventario multi-identidad antes de canonicalizar). | SR-D |
| L-PF5 | (llenar al cerrar VERIFY — la lección de SR-D ocupó L-PF4) | VERIFY |
| L-PF6 | QUÉ PASÓ: un JSON-LD válido en formato ARRAY detonaba `AttributeError: 'list' object has no attribute 'get'` en el parser; el caller lo tragaba como status ERROR y el audit lo publicaba como "0 schemas" en silencio → pain falso HIGH con cifra económica inventada. POR QUÉ: (a) el parser solo soportaba dict single y @graph; (b) un except genérico convierte cualquier bug interno en "ERROR sin schemas", indistinguible de una ausencia verificada; (c) el audit consumía el reporte sin exponer el error. QUÉ LO PREVIENE: parser polimórfico (dict/list/@graph) + parse_errors por bloque (corrupto no invalida) + ERROR solo si TODOS fallan + `error_message` propagado al DTO del audit con warning visible (ausencia verificada ≠ detección fallida, L-SR5) + criterio canónico único para la presencia del asset (L-SR3). Pertinencia: INCLUIR en memoria (patrón "ausencia verificada vs detección fallida" en detectores). | SR-E |
| L-PF7 | QUÉ PASÓ: el plan de assets varió entre corridas separadas por horas (7→5 brechas, faltaban ai_crawler_blocked y low_ia_readiness); la hipótesis vigente culpaba a un filtro del pain_solution_mapper o a caché, pero el diff forense de ledgers mostró al mapper determinista y a ai_crawler_blocked PRESENTE en la corrida A. POR QUÉ: las métricas upstream se medían con sondas URL malformadas — `f"{url}/robots.txt"` y `f"{url}/llms.txt"` con query UTM pedían `…/?utm=…/robots.txt`; el servidor respondía 200 con la homepage y el parser la interpretaba como robots "sin bloqueos" (score 1.0, robots_exists=True) y llms.txt presente (100) → exclusión determinista por FORMA de la URL, no por tiempo ni por caché. QUÉ LO PREVIENE: anclar TODA sonda URL derivada al origen del sitio (urlparse → scheme://netloc, patrón seo_accelerator_pro) + contrastar la hipótesis contra datos crudos (diff de ledgers/scores) antes de culpar a la capa intermedia + test de determinismo clean≡UTM. Pertinencia: INCLUIR en memoria (sondas derivadas ancladas al origen; medición corrupta ≠ decisión errática). | SR-F |
| L-PF8 | QUÉ PASÓ: el gate CG-TIER-CONSISTENCY comparaba frontmatter 'B' vs texto 'D'; la hipótesis del plan ("string de presentación vs valor crudo") era FALSA — el documento renderizaba el valor canónico correcto y era el EXTRACTOR `_extract_text_tier` quien fabricaba el 'D' espurio (regex `[A-Da-d]` capturaba la 'd' de "Nivel de evidencia", primera ocurrencia de "Nivel/Tier" del doc renderizado). El primer fix con `\b` introdujo un SEGUNDO bug: "Tier B+ para" → 'B' (tras '+' no hay boundary → backtracking trunca la captura). POR QUÉ: un extractor de tokens canónicos debe aceptar SOLO la forma canónica del dominio (A-D MAYÚSCULAS) y anclar con lookahead negativo de letra `(?![^\W\d_])`, nunca `\b` tras un grupo opcional que termina en '+'; y la hipótesis de un falso positivo debe verificarse contra el punto REAL de derivación (¿renderer o extractor?) antes de fijar el fix. QUÉ LO PREVIENE: regex de token = clase EXACTA de valores válidos del dominio + lookahead de letra + tests de regresión con el texto exacto del template renderizado Y casos de borde ('Tier B+ para', 'Tier Básico', 'Nivel de evidencia'). Pertinencia: INCLUIR en memoria (extractor canónico + anclaje de tokens con '+'). | SR-G |
| L-PF9 | QUÉ PASÓ: la jerga detectada al cliente (H6.4) requería dos comportamientos coordinados — el gate DETECTA términos prohibidos y los generadores TRADUCEN antes de publicar; duplicar la lista en el gate y los textos en los generadores recrearía dos criterios paralelos (L-NC10) y deriva a desincronización. POR QUÉ: detección y traducción son dos vistas de la MISMA fuente (el vocabulario prohibido) consumidas por capas distintas; el patrón de matching (\b condicionales para términos con paréntesis) también debía ser único. QUÉ LO PREVIENE: módulo glosario único con las DOS colecciones (detección + mapeo jerga→negocio) y el patrón compartido; contrato de COBERTURA (todo término traducible es detectable por ≥1 patrón) en vez de identidad de colecciones — los compuestos ("Schema Hotel") se detectan vía el término genérico ("Schema") y se traducen con regla más-largo-primero; `apply_glossary` en el punto ÚNICO post-render, ANTES de validación/healing (texto validado == texto publicado, L-SR3). Pertinencia: INCLUIR en memoria (vocabulario prohibido compartido gate↔generadores). | SR-G |
| L-PF10 | QUÉ PASÓ: la corrida E2E final bloqueó con `critical_recall` BLOCKED "metric not found" — el ÚNICO critical issue del baseline era el falso negativo de schema que SR-E corrigió; al quedar `critical_issues = []` (resultado genuinamente bueno), el gate interpretó "ausencia de dato" y bloqueó la publicación (pariente directo de L-PF6: ausencia verificada ≠ detección fallida, ahora en el CONSUMIDOR). POR QUÉ: `_extract_critical_recall` retorna None tanto si el dato no existe como si la lista está vacía — un extractor de métrica que colapsa "dato ausente" con "resultado favorable" convierte las mejoras upstream en regresiones de gating. QUÉ LO PREVIENE: distinguir explícitamente los dos estados (lista vacía → recall 1.0 / N-A con traza; key ausente → BLOCKED real) + test de contrato con `critical_issues=[]` + regla: tras fixear un falso negativo upstream, revisar TODOS los gates/métricas que consumían ese falso positivo como señal. Pertinencia: INCLUIR en memoria (estado "vacío" vs "ausente" en extractores de métricas; efecto dominó de fixear falsos negativos). **Confirmación SR-H2 (2026-08-28)**: fix confirmado en corrida H2 (D-PF7) — smoke 7/7, READY_FOR_PUBLICATION, traza `recall_basis=audit_present_no_critical_issues` en gate_report de producción. | SR-H |

---

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Bloqueo estructural proposal_asset_alignment (3ª manifestación) | ✅ RESUELTO (SR-B, 2026-08-28) | Fuente única D-PF1 (pain_ledger + presencia) en RC1/matriz/gate; coverage sobre actionable; test de contrato permanente `tests/quality_gates/test_alignment_contract.py` |
| Self-healing CG-CLAIM-VS-EVIDENCE | ✅ RESUELTO (SR-C, 2026-08-28) | Loop D-PF2: regenera con suggestion → re-valida (máx 1) → persiste → BLOCKED real (docs retenidos + ZIP abortado); traza `self_healing` en JSON de gates; test permanente `tests/quality_gates/test_claim_self_healing.py` (20) |
| target_id con query string / fragmentación memoria | ✅ RESUELTO (SR-D, 2026-08-28) | D-PF4: identidad canónica en caller (v4complete graba/busca + execute + validate-guarantee + `generate_hotel_id`); onboard persiste URL sin query; memory.py intacto (match exacto); test permanente `tests/test_target_id_canonicalization.py` (28) |
| Preflight hotel_schema paradoja + fallback ignorado (N4) | ✅ RESUELTO (SR-E, 2026-08-28) | Causa real H7 fixeada (parser array + propagación error al audit); `exists_with_issues` = `present_in_production` (criterio canónico, 6 consumidores); D-PF3 residual: fallback catálogo con fuentes / justified_skip sin fuentes; tests permanentes `test_fase_sr_e_schema_detection.py` (11) + `test_fase_sr_e_presence_accounting.py` (20) |
| Varianza plan de assets entre corridas (7→5) | ✅ RESUELTO (SR-F, 2026-08-28) | Causa real H5 (NO el mapper): sondas robots/llms con query UTM medían homepage 200 → robots 1.0/robots_exists=True y llms_txt=100 falsos → ai_crawler_blocked (0.5) + low_ia_readiness (0.34674) excluidos; fix en 3 sondas ancladas al origen (urlparse); test permanente `tests/auditors/test_fase_sr_f_probe_url_canonicalization.py` (15) |
| G9 divergente 4-vs-1 (N1) | ✅ RESUELTO (SR-A conteo + SR-B decisión, 2026-08-28) | Conteo unificado en `AlignmentResult.compute_unresolved` (gate + delivery); decisión de bloqueo unificada en SR-B (coverage sobre actionable desde el DTO canónico) |
| CG-TIER-CONSISTENCY + CG-TECH-JARGON | ✅ RESUELTO (SR-G, 2026-08-28) | Extractor de tier canónico (solo MAYÚSCULAS + lookahead de letra; gate intacto) + glosario único `tech_jargon_glossary.py` con `apply_glossary` post-render en ambos generadores; tests permanentes `tests/commercial_documents/test_tech_jargon_glossary.py` (14) + `TestExtractTextTier` (4 nuevos); AC9 se certifica en SR-H/VERIFY con la corrida E2E |
| PageSpeed API key inválida | ✅ VERIFICADO (SR-F, 2026-08-28) → ACCIÓN USUARIO (OPS) | Fallback chain `PAGESPEED_API_KEY → GOOGLE_PAGESPEED_API_KEY → GOOGLE_API_KEY`: .env resuelve GOOGLE_PAGESPEED_API_KEY (presente PERO inválida o sin PageSpeed Insights API habilitada — "API key not valid" en corrida C); GOOGLE_MAPS_API_KEY funcional (Places OK); PAGESPEED_API_KEY y GOOGLE_API_KEY ausentes; degradación sin bloqueo correcta (skipped_validators; 12/13 gates en corrida C). USUARIO: rotar la key o habilitar PageSpeed Insights API en Google Cloud Console (secretos NO tocados en el plan) |
| Gate de coherencia usa score agregado e ignora `is_coherent: false` del mismo archivo (CONTEXT §5) | 💡 FUERA DE ALCANCE | Evaluar en plan futuro; no bloquea este plan |
| Ubicación de DOMAIN_PRIMER: dualidad `.agent/` vs `.agents/` (knowledge en singular; workflows canónico en plural + symlink; `FALLBACK_PATH` defensivo en doctor.py) | 💡 FUERA DE ALCANCE (SR-A, 2026-08-28) | Consolidar bajo `.agents/` en mini-plan propio futuro; costo estimado: doctor.py, log_phase_completion, CONTRIBUTING §5b, README, AGENTS.md, validadores (25+ refs); no bloquea este plan |
| Fix H1 logger (main.py) | ✅ RESUELTO (d8e509d) | Guardián estático en SR-A cierra la clase |
| Gate `critical_recall` colapsa lista vacía con dato ausente (expuesto por SR-H) | ✅ RESUELTO (SR-H2, 2026-08-28) | Fix `_extract_critical_recall` (vacío+audit=1.0 favorable con traza `recall_basis=audit_present_no_critical_issues`; sin audit=BLOCKED real, L-SR5) + traza `details` en branch PASSED del gate; 4 tests de contrato permanentes; corrida de verificación D-PF7: smoke 7/7, READY_FOR_PUBLICATION, traza del fix en gate_report de producción (`evidence/FASE-SR-H2/`); VERIFY certifica AC11/AC12 contra `evidence/FASE-SR-H2/final/` |

---

## Métricas de Ejecución (llenar al cierre)

| Métrica | Baseline (corrida C) | Post-fix (corrida final) | Delta |
|---------|----------------------|--------------------------|-------|
| Tests totales | 3,379 | 3,379+ (SR-H no añade tests; smoke 7 checks) | — |
| Coherence E2E Salento Real | 0.8644 | 0.88 | +0.0156 |
| Gates de publicación | 12 PASSED + 1 BLOCKED (alignment 43%) | Corrida SR-H: 12 PASSED/WARNING + 1 BLOCKED (critical_recall; alignment ya no bloquea: WARNING con cobertura 3/3) → Corrida H2: 13/13 sin bloqueos (critical_recall PASSED 1.0 con traza `recall_basis`) | 0 bloqueos post-hotfix |
| Alineación propuesta-assets | 43% (3/7) | coverage_no_silent_drop PASSED (3/3 detectadas, 0 justificadas); alignment WARNING no bloqueante (2 schemas presentes en producción, 1 FAQ ya en producción) | fin del bloqueo por alignment |
| `no_hotel_schema` en pain_ledger | DETECTED (falso positivo H7) | AUSENTE (schema real detectado por audit) | resuelto por detección correcta |
| unresolved (gate vs delivery) | 4 vs 1 | 0 vs 0 | unificado (AC3) |
| Escenarios financieros | $6.57M / $4.04M / $1.26M | $6,571,622.4 / $4,042,752.0 / $1,264,435.2 (idénticos) | 0 (AC10) |
| readiness | NOT_READY | Corrida SR-H: NOT_READY (único bloqueo: critical_recall — bug latente expuesto por SR-E, ver §Resumen E2E) → Corrida H2: **READY_FOR_PUBLICATION** (`ready: true` en v4_complete_report) | bloqueo eliminado por hotfix (AC11) |
| Smoke E2E (7 checks) | — (baseline de referencia) | SR-H 5/7 (pre-fix) → H2 7/7 (post-hotfix) | +2 checks (veredicto READY + docs 01/02) |

---

## Decisiones Arquitectónicas (pre-registradas en preparación; confirmar implementación en cada fase)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|-------------------------|------|
| D-PF1 | UNA fuente de verdad del estado de servicio = pain_ledger + present_in_production (SitePresence); reutilizar el concepto `actionable` existente en `proposal_asset_alignment.py:783-789`; NO_BREACH fuera del denominador del gate Y de la tabla de compromiso de la propuesta | Nunca dos criterios en paralelo (L-NC10); el catálogo estático del tier ya demostró fosilización (L-SR3) | (a) Solo que el gate respete NO_BREACH sin tocar la propuesta — dejaría promesas vacías en el texto; (b) crear taxonomía nueva paralela — viola L-NC10 | SR-B ✅ CONFIRMADA (2026-08-28, implementada tal cual; matices registrados en 09 §Notas: AEO no se renderiza bajo D-PF1 — dedup del mismo asset llms_txt; legacy sin pain_ledger intacto) |
| D-PF2 | Self-healing CG-CLAIM-VS-EVIDENCE: máx. 1 regeneración con el `suggestion` del gate como restricción; si persiste → BLOCKED real (documentos retenidos, ZIP abortado) | Detectar sin ciclar deja pasar la erosión de credibilidad (L-SR5); el loop infinito es un anti-patrón de gates | (a) Regeneración ilimitada — riesgo de bucle; (b) solo WARNING — mantiene el statu quo | SR-C ✅ CONFIRMADA (2026-08-28, implementada tal cual; matices: reescritura por oración con 3 estrategias — condicional intacta / instrucción neutralizada / sujeto GBP→claim trazable del suggestion; traza en JSON de gates bajo `self_healing`) |
| D-PF3 | Para brechas de ausencia ("no existe X"), la confianza del asset se calcula desde las fuentes disponibles para construir X (GBP/web); el preflight respeta `fallback` + `block_on_failure=False` del catálogo (contrato del catálogo gana — nunca ambos criterios, N4) | Separa "confianza en datos de entrada" de "confianza en implementación del asset" (L-SR4); el catálogo YA declara capacidad de fallback | (a) Eliminar el fallback del catálogo — dejaría el pain #1 estructuralmente irresoluble; (b) bajar el umbral 0.8 — enmascara el problema semántico | SR-E ✅ CONFIRMADA (2026-08-28, hardening residual tras revisión causa-raíz: la causa real era el falso negativo del parser, NO el preflight; `get_assets_for_pain` aplica fallback del catálogo cuando hay fuentes para construir el asset (L-SR4) y `justified_skip` sin fuentes; el preflight ya derivaba `ASSET_REQUIREMENTS` de `ASSET_CATALOG`; `generate_basic_schema` queda como no-implementación documentada con seguimiento abierto) |
| D-PF4 | Canonicalizar la URL al inicio de cada comando con `--url` usando el helper EXISTENTE `_normalize_url()` (L16: el gap está en el caller); URL original solo para scraping | Reutilización sobre código nuevo; el helper ya ignora protocolo/www/path/query | (a) Crear normalizador nuevo; (b) normalizar solo en memory.py — dejaría los call sites inconsistentes | SR-D ✅ CONFIRMADA (2026-08-28, implementada tal cual en v4complete/execute/validate-guarantee; matices: `generate_hotel_id` replica la semántica via urlparse — import de main desde modules es dependencia inversa; onboard persiste hotel['url'] sin query en vez de canónica pura porque los assets lo consumen como website navegable; onboard no usa target_id de memoria — 0 call sites verificados por grep) |
| D-PF5 | Guardián estático L-SR1 como test AST extensible (lista de símbolos prohibidos, inicia con `logger`) sobre main.py | Prevención permanente de la clase "símbolo no definido en rama no ejercitada" (H1, L-NC8/9) | (a) Solo grep manual — no es verificable en CI/validaciones | SR-A |
| D-PF6 | SR-F con outcome condicional pre-decidido: si la causa de la varianza es un filtro determinista erróneo → fix mínimo + test; si requiere rediseño mayor → seguimiento documentado (sin agrandar la fase) | Respeta R3; la investigación no puede inflarse en una fase de fixes | Dejar el outcome abierto — decisión incompleta viola el principio decision-complete | SR-F ✅ CONFIRMADA (2026-08-28, outcome=FIX: la causa era determinista y errónea pero upstream en las sondas URL, NO en el mapper; fix mínimo en 3 sondas ancladas al origen + 15 tests; sin rediseño mayor) |
| D-PF7 | Corrida de verificación ÚNICA post-hotfix (desviación pre-registrada al §9 del plan maestro): si T2 del hotfix critical_recall está verde, UNA corrida v4complete adicional con output NUEVO (`output/salentoreal_final_v4c_h2`) para no pisar la evidencia pre-fix de SR-H | AC11/AC12 no son certificables con el output NOT_READY pre-fix; el smoke 7/7 contra el MISMO baseline aísla el efecto del hotfix | (a) Re-ejecutar sobre `output/salentoreal_final_v4c` — pisaría la evidencia de SR-H; (b) certificar AC11 solo con unit tests — viola L-NC11 (verificación E2E > unit tests) | SR-H2 ✅ CONFIRMADA (2026-08-28, corrida única exit 0 ~1m50s; smoke 7/7; evidencia `evidence/FASE-SR-H2/` con traza del fix en gate_report de producción) |

---

## Checklist de Cierre (FASE-RELEASE — llenar al cierre)

- [ ] Todas las fases ✅ en `06-checklist-implementacion.md` (SR-A a SR-H + VERIFY)
- [ ] Matriz de Verificación completa: 13/13 ACs con Real/Status
- [ ] Lecciones nuevas registradas (mínimo 3, formato qué pasó/por qué/qué lo previene)
- [ ] Métricas de Ejecución post-fix completadas
- [ ] VERSION.yaml == "4.73.0" + sync 6 archivos + Version Sync Gate OK
- [ ] CHANGELOG `[4.73.0]` + GUIA_TECNICA "Notas de Cambios v4.73.0"
- [ ] `run_all_validations.py --quick` TOTAL PASS
- [ ] README/AGENTS audit: test count verificado contra `pytest --collect-only`
- [ ] Seguimientos abiertos: ninguno o con plan asignado
- [ ] Commit de release ejecutado
