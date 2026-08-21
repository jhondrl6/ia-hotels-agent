# Análisis Post-Implementación — CREDIBILIDAD-NUMERICA-2026-08-20

> **Estado**: 9/11 fases completadas (P0-A ✅, P0-B ✅, P0-C ✅, P1-A ✅, P1-B ✅, P1-C ✅, P1-D ✅, P2-A ✅, P2-B ✅) — 2 restantes
> **Plan**: CREDIBILIDAD-NUMERICA-2026-08-20
> **Versión objetivo**: v4.72.0
> **Creado DESDE LA CONCEPCIÓN** (phased_project_executor v2.15.0): cada fase agrega lecciones aquí al cerrar sesión.

## Resumen de Ejecución (llenar al cierre de cada fase)

| Fase | Sesión | Estado | Iteraciones | delegate_task | Notas |
|------|--------|--------|-------------|---------------|-------|
| FASE-P0-A | 2026-08-20 | ✅ | ~35 | No | 3 tests nuevos contrato F1; 0 regresiones; 22 fallos línea base intactos |
| FASE-P0-B | 2026-08-21 | ✅ | ~30 | No | 18 tests nuevos pricing_compliance; gate floor-aware D1; AGENTS.md 12→13 gates; 0 regresiones |
| FASE-P0-C | 2026-08-21 | ✅ | ~15 | No (DIRECTO) | 4 tests nuevos encoding; auditoría estática AST; fix en 3 writers (1 delivery_quality_report + 2 config_checker); 0 regresiones |
| FASE-P1-A | 2026-08-21 | ✅ | ~45 | No | 19 tests nuevos benchmark_master; normalización regiones; script sync; D3+D3b documentadas; 0 regresiones vs baseline (10 preexistentes) |
| FASE-P1-B | 2026-08-21 | ✅ | ~45 | No (DIRECTO) | 24 tests nuevos (12 F3 + 12 F5); comisión OTA parametrizada en 5 sitios + 3 archivos de tests actualizados; 0 regresiones vs baseline (148 auditors, 10 preexistentes financial_engine) |
| FASE-P1-C | 2026-08-21 | ✅ | ~30 | No | 27 tests nuevos (14 F6/D4 + 13 F11); benchmark master cableado al hook; cap plausibilidad 5x (D7); trazabilidad Hook→Express; suite orchestration_v4 66→93; validaciones --quick 6/6 PASS |
| FASE-P1-D | 2026-08-21 | ✅ | ~35 | No (DIRECTO) | 21 tests nuevos (11 F12 multi-sede + 10 F13 propagación); firma backwards-compatible en validate_whatsapp; D8 (VERIFIED_IN_SITE primera clase); suites data_validation+asset_generation 603 passed; suites ampliadas: solo los 12 fallos preexistentes de la línea base; 0 regresiones |
| FASE-P2-A | 2026-08-21 | ✅ | ~30 | No (DIRECTO) | 11 tests nuevos F14; coherence acepta site_presence_report; F8 auditoría sin rutas residuales; validaciones --quick 6/6 PASS; 0 regresiones |
| FASE-P2-B | 2026-08-21 | ✅ | ~30 | No (DIRECTO) | Script preload_prospects_gbp.py (dry-run OK, 30 prospectos builtin); search_by_name en GooglePlacesClient; 4 docs higienizadas (PRECIOS_PAQUETES, PROPUESTA_EMPAQUETADO, PROMPT_INGRESOS x2); ADR $420K→$280K; scrapers 34 passed 0 nuevos fallos; validaciones --quick 6/6 PASS |
| FASE-E2E-ZIONE | — | ⬜ | — | Sí (v4complete) | |
| FASE-RELEASE-4.72.0 | — | ⬜ | — | Opcional | |

## Matriz de Verificación de Fixes (llenar en FASE-E2E-ZIONE)

Matriz completa en `01-plan-maestro.md §4` (V1-V13). Resumen:

| # | Fix (fallo) | Expected | Real | Status |
|---|-------------|----------|------|--------|
| V1-V2 | F1 pricing único + gate | Un precio; gate PASSED (floor-aware D1) | | |
| V3 | F7 encoding | JSONs legibles utf-8 | | |
| V4-V5 | F2/F4/F3 benchmarks + fallback | Un ADR; fallback conservador | | |
| V6 | F5 comisión OTA | Rango + fuente | | |
| V7 | F6 cap rango hook | Ratio acotado | | |
| V8-V9 | F12/F13 verdad sitio vivo | Sin brechas falsas WhatsApp | | |
| V10 | F14 coherence vs gate | Ambos de acuerdo | | |
| V11 | F8 occupancy label | Etiqueta correcta | | |
| V12 | Regresión gates | Coherence ≥ 0.8; sin fallos NUEVOS vs línea base §6 | | |
| V13 | C9 corrida (caches cálidos) | Tiempo medido | | |

## Lecciones Aprendidas (mínimo 3 por fase completada)

Formato: **qué pasó / por qué / qué lo previene** + pertinencia (INCLUIR/EXCLUIR)

### Lecciones capitalizadas de planes anteriores (aplicadas al DISEÑO de este plan)

| Lección | Aplicación en este plan |
|---------|--------------------------|
| Nunca declarar bug sin leer el archivo completo (CONTEXT §1.3) | Los prompts ordenan INVESTIGAR antes de fijar; líneas citadas del contexto se marcan "verificar en ejecución" |
| Nunca declarar brecha HIGH sin verificación contra sitio vivo (CONTEXT §7.4) | FASE-E2E verifica V8/V9 contra https://zione.co/ |
| Post-implementación desde concepción (executor v2.15.0) | Este archivo creado en Preparación |
| Subagentes no comparten venv Windows (FASE-4 BUGS-ONBOARDING-ADR) | Advertencia venv en P1-B; v4complete delegado solo ejecuta terminal |
| Análisis de causa raíz de FASE-F (occupancy label) | F8 residual limitado a verificación de etiqueta, no re-fix del valor |

### Lecciones nuevas de este plan (llenar por fase)

#### FASE-P0-A

| # | Lección | Pertinencia |
|---|---------|-------------|
| L1 | `_load_pricing_config()` ya existía en `pricing_calculator.py` con caché module-level y fallback. Reutilizarla evita duplicar lógica de carga YAML y garantiza consistencia con el financial engine. | INCLUIR: futuros consumidores de pricing deben importar de pricing_calculator, no reimplementar |
| L2 | Al eliminar constantes de clase y reemplazarlas con método de instancia `_get_pricing_packages()`, los `getattr(self, '_current_*', self.CONSTANTE)` en 15 sitios del proposal generator requerían migración individual. Un grep global (`self.SETUP_FEE\|self.MONTHLY_PACKAGE_PRICE`) confirmó 0 residuales. | INCLUIR: tras refactor de constantes, SIEMPRE verificar con grep que no queden referencias |
| L3 | El test `test_pricing_constants` con valores hardcodeados (“120.000”, “400.000”) se rompió con el refactor. Reescribirlo para comparar contra `_load_pricing_config()` lo hace resiliente a cambios futuros en pricing.yaml. | INCLUIR: tests de contrato deben comparar contra fuente dinámica, no valores fijos |

#### FASE-P0-B

| # | Lección | Pertinencia |
|---|---------|-------------|
| L4 | El gate `pricing_compliance` necesita datos de pricing (pain_ratio, tier, monthly_price) en el assessment, pero `AssessmentBuilder` no los inyectaba. Agregar `with_pricing()` como método fluid y `pricing_data` como campo en `AssessmentPayload` resuelve el vacío sin tocar los 12 gates existentes. | INCLUIR: al agregar un gate nuevo, verificar SIEMPRE que el assessment builder propague los datos necesarios |
| L5 | La detección de `operational_floor` aplicado se implementa comparando `monthly_price <= operational_floor * 1.01` (tolerancia 1%). Sin tolerancia, precios exactos al floor fallan la detección por redondeo de punto flotante. | INCLUIR: comparaciones de precios con floor SIEMPRE deben incluir tolerancia (1% mínimo) |
| L6 | Los tests existentes (test_all_gates_pass, test_visperas_comprehensive_report) asumen un conteo FIJO de gates (12). Al agregar un gate nuevo, 4 tests se rompieron por assertions `len(results) == 12`. Actualizar a 13 fue trivial pero evitable con assertions dinámicas (`len(orchestrator.gates)`). | INCLUIR: assertions de conteo de gates deben usar `len(orchestrator.gates)` en vez de hardcoded — mejora resiliencia ante futuros gates |

#### FASE-P0-C

| # | Lección | Pertinencia |
|---|---------|-------------|
| L7 | La auditoría de writers sin encoding reveló que de ~60 writers en modules/, solo 3 carecían de encoding='utf-8'. El patrón dominante es que los writers YA estaban corregidos (probablemente por P0-A o convenciones previas). Un test estático con AST (ast.parse + walk) es más robusto que grep para detectar violaciones futuras porque entiende la estructura del código y no genera falsos positivos con comentarios o strings. | INCLUIR: para contratos de código transversales (encoding, imports prohibidos), usar AST en vez de regex/grep |
| L8 | `delivery_quality_report.py` era el writer crítico (F7 original: UnicodeDecodeError byte 0xf3). El fix fue trivial (1 línea) pero el impacto es alto: es el primer archivo que se lee al abrir el ZIP de entrega. Los writers de config_checker.py son archivos temporales de prueba de permisos — el fix es preventivo (evita fallo en sistemas con locale no-UTF-8). | INCLUIR: priorizar fixes de encoding por impacto en el usuario final, no por cantidad de writers |
| L9 | El test de contrato anti-regresión con caracteres Unicode (em-dash “–”, tildes “ó”, “é”) verifica el roundtrip save→load. Sin estos caracteres explícitos en el test, un futuro cambio podría reintroducir write_text sin encoding y el test pasaría porque ASCII no distingue cp1252 de utf-8. | INCLUIR: tests de encoding SIEMPRE deben incluir caracteres no-ASCII (tildes, ñ, em-dash) para ser efectivos |

#### FASE-P1-A

| # | Lección | Pertinencia |
|---|---------|-------------|
| L10 | El inventario T0 reveló **3 fuentes** de benchmarks (no 2 como asumía el plan original): regional_adr_2026.json, plan_maestro_data.json, regional_benchmarks.yaml. El YAML resultó NO consumirse en cálculos financieros (solo pain_narratives y thresholds). Un grep exhaustivo ANTES de decidir master evitó migrar consumidores irrelevantes. | INCLUIR: siempre verificar consumo real con grep antes de refactor multi-fuente |
| L11 | `_normalize_region()` debe aplicar lowercase ANTES del alias lookup, no después. Caso: “Bogotá” (mayúscula) no matchea alias “bogotá” (minúscula) si el lookup va primero. Orden correcto: lowercase → alias → lowercase final. | INCLUIR: normalización de strings con aliases SIEMPRE lowercase-first |
| L12 | `_get_known_regions()` retornaba keys crudas del data source, pero `_normalize_region()` retornaba nombres normalizados. Mismatch causaba que regiones conocidas se marcaran como `is_default=True` al consultarlas con alias (coffee_axis→eje_cafetero no matcheaba “coffee_axis” en known). Fix: normalizar keys en `_get_known_regions()`. | INCLUIR: cuando hay normalización de entrada, la comparación SIEMPRE debe usar la misma normalización en ambos lados |

#### FASE-P1-B

| # | Lección | Pertinencia |
|---|---------|-------------|
| L13 | La decisión D2 (usar campo existente `comision_ota` en lugar de crear `ota_commission` nuevo) demostró ser correcta: el flatten en `financial_factors.py` ya convertía `comision_ota.{min,base,max}` en `comision_ota_min/base/max`. Añadir `source` al YAML fue transparente porque el flatten lo convirtió automáticamente en `comision_ota_source`. | INCLUIR: cuando exista infraestructura de flatten/parse, aprovecharla para nuevos campos en lugar de crear rutas paralelas |
| L14 | Los defaults de parámetros en dataclasses y funciones no pueden cargar dinámicamente de config en tiempo de definición. La solución fue cambiar el default hardcoded de 0.15 a 0.20 (valor actual de config) y cargar dinámicamente solo en `__init__` y métodos que lo necesitan (ScenarioCalculator, _to_hotel_financial_data, _estimate_monthly_loss). | INCLUIR: para parametrizar defaults de parámetros, usar el valor actual de config como literal y cargar dinámicamente solo donde sea posible |
| L15 | Al cambiar defaults de 0.15 a 0.20, 4 tests existentes se rompieron (test_hotel_financial_data_defaults, test_scenario_calculator_initialization, test_all_optional_defaults, test_build_financial_evidence_ota_defaults). Los tests que usaban 0.15 como valor explícito pasado como parámetro NO se rompieron. Diferenciar entre “tests que verifican defaults” y “tests que usan valores explícitos” es crucial al cambiar constantes. | INCLUIR: tras cambiar defaults, ejecutar tests y actualizar solo las aserciones de default, no los valores explícitos |

#### FASE-P1-C

| # | Lección | Pertinencia |
|---|---------|-------------|
| L16 | El fix de cableado D4 fue en el caller (`OnboardingController`), no en el orquestador: el constructor de `TwoPhaseOrchestrator` ya aceptaba `plan_maestro_data`, solo nadie lo pasaba. Una capa conversora (`load_benchmark_master`/`_convert_master_region`) en el controller traduce la estructura por segmentos del master (boutique_10_25/standard_26_60) al formato plano que espera `_get_regional_benchmarks`, aislando al orquestador de la estructura del master. | INCLUIR: antes de modificar un constructor, verificar si el parámetro ya existe y el gap está en el caller; las conversiones de formato van en una capa adaptadora, no en el consumidor |
| L17 | Los tests existentes assertean conjuntos EXACTOS de campos de `Phase1Result`/`Phase2Result`. Añadir la trazabilidad como campos nuevos en el dataclass habría roto esos assertions. Se implementó como métodos separados (`validate_hook_range_traceability` en el orquestador, `get_range_traceability` en el controller), manteniendo los dataclasses intactos. | INCLUIR: antes de añadir campos a dataclasses con tests de contrato sobre sus campos, exponer la nueva información vía métodos/objetos separados |
| L18 | Reutilizar `RegionalADRResolver.REGION_ALIASES` para normalizar keys de región evita duplicar la tabla de aliases (coffee_axis→eje_cafetero, medellin→antioquia). Región sin match cae al "default" del master (conversado, ratio ~3.3x) antes que a los defaults hardcodeados (ratio 23x); estos últimos solo aplican si el master está ausente, comportamiento documentado explícitamente. | INCLUIR: reutilizar tablas de normalización existentes en vez de duplicarlas; documentar explícitamente el último nivel de fallback |

#### FASE-P1-D

| # | Lección | Pertinencia |
|---|---------|-------------|
| L19 | La deduplicación de candidatos WhatsApp por número normalizado descartaba el alterno COMPLETO, perdiendo su label de sede (test C3 falló: ESTIMATED en vez de CONFLICT real). Fix: cuando el número ya existe como candidato sin label, adoptar el label del duplicado. La metadata complementaria (label/tipo) nunca debe perderse al deduplicar por clave numérica. | INCLUIR: al deduplicar por clave normalizada, SIEMPRE fusionar metadata complementaria (labels, tipos) en la entrada existente en vez de descartar el duplicado completo |
| L20 | El matching label↔gbp_location por substring completo falla con direcciones reales: "Pereira Contact" no es substring de "Cra 13 # 5-20, Pereira, Risaralda". Matching por tokens (palabras ≥4 chars del label contenidas en gbp_location) resuelve sin falsos positivos de palabras cortas ("Sede", "Tel"). | INCLUIR: matching de ubicaciones entre texto libre y labels DOM SIEMPRE por tokens con longitud mínima, nunca substring completo |
| L21 | F13 se resolvió extendiendo la taxonomía de status (VERIFIED_IN_SITE) + agregándolo al whitelist de justificación del coverage gate (_JUSTIFIED_STATUSES), sin alterar la fórmula "cubiertas + justificadas == detectadas". El reconciler solo necesitó una línea de preservación. Extender estados existentes es más barato y auditable que crear lógica paralela de "brechas ignoradas". | INCLUIR: para nuevos estados de verdad, preferir extensión de taxonomía + whitelist de gates sobre lógica paralela; verificar SIEMPRE que los reconciliadores intermedios preserven el nuevo estado |
| L22 | La firma backwards-compatible (parámetros opcionales web_alternates/gbp_location) permitió que `two_phase_flow._validate_all_inputs` quedara intacto (no tiene DOM disponible) y solo se enriquecieran los callers con acceso al HTML (v4_comprehensive, main.py). Mono-sede conserva comportamiento legacy exacto. | INCLUIR: al cambiar firmas con múltiples callers, parámetros opcionales + enriquecer solo callers con datos disponibles preserva compatibilidad sin branch masivo |

#### FASE-P2-B

| # | Lección | Pertinencia |
|---|---------|-------------|
| L26 | `GooglePlacesClient` solo tenía `search_nearby_lodging` (requiere lat/lng). Para pre-carga de prospectos por nombre+ciudad se necesita `search_by_name` con Places API (New) `places:searchText`. El nuevo método usa `textQuery`, `includedType=lodging`, `maxResultCount=3` y cachea el resultado. | INCLUIR: nuevos scripts que busquen hoteles por nombre deben usar `search_by_name`, no construir queries HTTP ad-hoc |
| L27 | La higiene documental reveló que `PRECIOS_PAQUETES.md` tenía precios en USD ($299/$599/$999/$1499) completamente desconectados de `config/pricing.yaml` (COP). Los documentos comerciales son frecuentemente editados manualmente y se desincronizan del código. La solución es citar la fuente única (`config/pricing.yaml`) en vez de hardcodear cifras, y agregar una "Política de Coherencia de Pricing" visible en el documento. | INCLUIR: docs comerciales SIEMPRE deben citar la fuente de verdad (archivo YAML/JSON) en vez de repetir valores; incluir nota de política de coherencia |
| L28 | El benchmark ADR Eje Cafetero en `PROPUESTA_EMPAQUETADO` y `PROMPT_INGRESOS` aún citaba $420K (valor pre-calibración FASE-P1-A). Grep con `$420` y `420K` encontró 4 documentos activos con el valor obsoleto. Los archivos de evidencia histórica (outputs pasados de v4complete) NO se modifican — son registro de lo que el sistema produjo. | INCLUIR: tras recalibración de benchmarks, SIEMPRE buscar con grep en docs activos (evidence/Recomendaciones, docs/) y NO tocar archivos de evidencia histórica |

#### FASE-P2-A

| # | Lección | Pertinencia |
|---|---------|-------------|
| L23 | `_extract_verified_in_production_types` extrae asset_types del site_presence_report canónico (normalize_site_presence) iterando sobre "results" + top-level keys. El dict canónico tiene la data duplicada en ambos niveles, y algunos callers pasan solo uno. Iterar sobre ambos garantiza robustez. | INCLUIR: al consumir dicts canónicos de normalize_site_presence, SIEMPRE verificar ambos niveles (results + top-level keys) para no perder datos |
| L24 | El test C5 (coherence ↔ gate alignment) verifica el contrato end-to-end: mismo input → misma decisión en coherence_validator._check_promised_assets_exist y proposal_asset_alignment.verify_proposal_asset_alignment. Sin este test de integración, la alineación semántica entre ambos validadores sería frágil a cambios independientes. | INCLUIR: cuando dos validadores deben producir la misma señal sobre el mismo input, SIEMPRE escribir un test de alineación end-to-end |
| L25 | La auditoría F8 (occupancy provenance) reveló una discrepancia semántica menor en main.py L1854: el payload del harness usa `adr_from_onboarding > 0` para etiquetar occupancy_source, pero el valor real del occupancy_rate viene de `reservas_mes`. No es un bug porque el valor es correcto, pero el label en el payload no refleja la fuente real. El label canónico (`_occupancy_source`) usado en todas partes es correcto. | INCLUIR: al auditar provenance, verificar SIEMPRE que el label y el valor provengan de la misma condición; discrepancias semánticas pueden confundir debugging futuro |

**T0b: Desviación benchmark vs observaciones Tier A (Eje Cafetero)**

| Hotel | Categoría | ADR observado | Benchmark anterior | Desviación |
|-------|-----------|--------------|-------------------|------------|
| Don Alfonso | boutique | $330K | $420K | -21% |
| Castilla Real | boutique | $282K | $420K | -33% |
| Luxor (tránsito) | boutique | $200K | $420K | -52% |
| Zi One | standard | $290K | $350K | -17% |
| Luma Plaza (tránsito) | standard | $200K | $350K | -43% |
| Abadia Plaza (tránsito) | standard | $300K | $350K | -14% |

Decisión: benchmark $420K era desactualizado/aspiracional. Master calibrado a $280K boutique (promedio no-tránsito: $306K) y $260K standard (promedio: $263K). Hoteles de tránsito excluidos del benchmark por no ser competidores del nicho boutique-destino.

## Seguimientos abiertos (llenar conforme avancen las fases)

| Tema | Estado | Acción futura |
|------|--------|---------------|
| Ruta productora del pricing $500K no trazada a fondo (CONTEXT §4.2) | ✅ Cerrado | FASE-P0-A trazó la cadena: pricing.yaml → _load_pricing_config() → _calculate_dynamic_price() → pricing_result.monthly_price_cop |
| Comportamiento de scrapers con prospectos nuevos (CONTEXT §4.3) | Parcialmente cubierto | FASE-P2-B creó el script y el método search_by_name; ejecución batch real (30 prospectos) pendiente como tarea operativa post-plan |
| Ejecución batch operativa de pre-carga GBP sobre 30 prospectos | Abierto (post-plan) | Ejecutar `scripts/preload_prospects_gbp.py --builtin` con GOOGLE_MAPS_API_KEY configurada; revisar reporte; contactar prospectos VERIFIED |
| Widget Elementor `e-fab-whatsapp` (F12) | ✅ Cubierto sin cambio de código | `_check_html_element` de SitePresenceChecker ya lo detecta por substring 'whatsapp'; verificado en T1, sin acción pendiente |
| P3: deployer real, Express 5 páginas, monitoreo | Fuera de alcance | Solo tras primer Express pagado |

## Métricas de Ejecución (llenar al cierre)

| Métrica | Valor |
|---------|-------|
| Tests totales al cierre | (pendiente — se actualizará en RELEASE) |
| Coherence E2E Zi One | (pendiente) |
| Gates PASSED E2E | (pendiente) |
| Tiempo corrida con caches cálidos (C9) | (pendiente) |

## Decisiones Arquitectónicas (llenar cuando aplique)

| ID | Decisión | Rationale | Alternativas rechazadas | Fase |
|----|----------|-----------|--------------------------|------|
| D1 | Gate pricing_compliance floor-aware: BLOCKING solo si pain_ratio > pain_ratio_gate_max del tier (0.32 boutique); WARNING fuera de 0.03-0.06 con operational_floor aplicado | Con umbrales globales 0.03-0.06 como blocking, fuga < 6.67M/mes con floor 400K nunca cumple ratio ≤ 0.06 → V12 inalcanzable; precedente PATCH-A en coherence_validator (max_ratio 0.50) | Umbrales globales como blocking | FASE-P0-B |
| D2 | Comisión OTA: campo EXISTENTE `comision_ota` (0.18-0.22) + `source`; 5 sitios hardcodeados eliminados; FinancialFactors.get_comision_ota() como API centralizada; defaults 0.15→0.20 en dataclasses y funciones | Campo ya existente dentro de la narrativa 17-25%; consumidores activos (financial_factors.py, main.py L361); flatten automático convierte source en comision_ota_source | Crear campo nuevo `ota_commission` | FASE-P1-B ✅ |
| D3 | JSON (regional_adr_2026.json) como master ADR/occupancy por región. YAML es referencial (no consumido en cálculos). plan_maestro_data.json sincronizado via validate_benchmark_sync.py | Ya gana en runtime; estructura por categoría (boutique/standard) más granular que YAML plano; default_region alineado con nicho fundacional. Calibrado vs 6 observaciones Tier A | YAML como master (pierde categoría); crear un cuarto archivo consolidado (más complejidad sin beneficio) | FASE-P1-A ✅ |
| D3b | Retroalimentación benchmark←observations: diferida a P1-C o P2. Umbral: ≥3 hoteles VERIFIED por región+segmento para recalibrar. Strategy: calcular mediana de observaciones no-transit, comparar vs benchmark, actualizar si desviación >20% | Suficiente data hoy solo para eje_cafetero (6 hoteles, todos Eje Cafetero). Otras regiones sin observaciones Tier A. Implementar ahora sería prematuro | Implementar ahora (sin data suficiente fuera de Eje Cafetero); umbral ≥5 (retrasaría demasiado la retroalimentación) | FASE-P1-A ✅ |
| D4 | Rango del hook cableado al benchmark master ANTES del cap | El cap sobre defaults hardcodeados acota un rango fabricado | Cap directo sin cableado | FASE-P1-C |
| D5 | AGENTS.md gate count 12→13 actualizado en P0-B y validado con validate_agents_md.py | `--quick` no valida gate count; drift invisible si se pospone a RELEASE | Posponer actualización a RELEASE | FASE-P0-B |
| D6 | pricing.yaml como fuente única de pricing: constantes `PRECIO_EXPRESS/PRECIO_MENSUAL/SETUP_FEE` (hook_pdf) y `MONTHLY_PACKAGE_PRICE/SETUP_FEE` (proposal) eliminadas; ambos módulos consumen de `_load_pricing_config()["packages"]`; +express_price: 120000 agregado a pricing.yaml | Principio "una fuente de verdad por concepto": 3 fuentes Python no sincronizadas generaban riesgo de cifras contradictorias en output del cliente. La solución reutiliza infraestructura existente (pricing_calculator._load_pricing_config con caché) sin crear módulo nuevo | Crear pricing_service.py nuevo (más abstracción); mantener constantes con sync manual (más frágil) | FASE-P0-A ✅ |
| D7 | Cap de plausibilidad por ratio fijo max/min = 5.0 configurable (`hook_range_max_ratio` en `config/financial_defaults.yaml`, fallback hardcoded 5.0); aplicado en la GENERACIÓN del rango del hook (`_calculate_hook_range`), no en los escenarios financieros; el extremo optimista se trunca sobre el piso conservador (min × ratio) | Ratio fijo es simple, configurable y auditable; aplicar el cap en el hook preserva la verdad financiera de los escenarios (capear escenarios contaminaría el cálculo real con un artefacto de presentación); D4 exige cableado ANTES del cap (master real eje_cafetero: 6.46x → capado a 5x) | Cap por percentil P95 (requiere maquinaria de escenarios completa dentro del hook, complejidad sin beneficio); cap aplicado en escenarios (contamina la verdad financiera); ratio 8x (demasiado permisivo, sigue permitiendo rangos poco creíbles) | FASE-P1-C ✅ |
| D8 | Estado "verificado en producción" como primera clase: `STATUS_VERIFIED_IN_SITE` en pain_ledger (apply_site_verification antes de save); reconciler lo preserva; coverage gate lo justifica vía _JUSTIFIED_STATUSES; diagnóstico filtra brechas verificadas. FASE-P2-A/F14 consumirá este mismo estado en coherence_validator | Cierra F13 sin alterar la fórmula del coverage gate (cubiertas + justificadas == detectadas) y deja LISTO el estado para F14 (restricción explícita del prompt: no tocar coherence en P1-D); la trazabilidad pain_id → site_verification:{asset}:{status} queda en evidence_refs | Metadata sin estado propio (el diagnóstico seguiría reportando la brecha falsa); borrar la entrada del ledger (pierde trazabilidad y viola el gate de no-regresión documental del coverage) | FASE-P1-D ✅ |

> D1-D6 están pre-resueltas en `01-plan-maestro.md §7`; D7/D8 se deciden en su fase.

## Checklist de Cierre (llenar en FASE-RELEASE-4.72.0)

- [ ] Todos los fixes F1-F14 verificados en matriz V1-V13
- [ ] Corrida única v4complete Zi One Luxury en `evidence/E2E-ZIONE/`
- [ ] Lecciones aprendidas ≥ 3 por fase
- [ ] CHANGELOG + GUIA_TECNICA + VERSION.yaml = 4.72.0
- [ ] run_all_validations.py --quick TOTAL PASS
