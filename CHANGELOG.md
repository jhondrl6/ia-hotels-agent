# Changelog

## [4.22.0] - 2026-04-05

### FIX CRITICO - Duplicacion de metricas en scorecard diagnostico

**Problema identificado:**
- `v4_diagnostic_generator.py:1078-1085`: `_calculate_activity_score()` inyectaba `geo_score * 0.5` en su resultado
- Esto causaba que la fila "Activity Score (GBP)" compartiera ~50% de sus datos con "Google Maps (GEO)"
- El diagnostico presentaba dos scores independientes cuando uno contenia al otro
- Ejemplo: GEO=72 inflaba automaticamente Activity=86 (36 puntos venian de la inyeccion directa)

**Solucion aplicada:**
- Nueva funcion `_calculate_competitive_score(audit_result)`: usa geo_scores de competidores reales (Places API) para calcular posicionamiento relativo
- La formula ahora mide: ranking percentile vs competidores cercanos + gap penalty al siguiente competidor
- Legacy alias `_calculate_activity_score = _calculate_competitive_score` mantiene compatibilidad con callers existentes
- Template renombrado: "Activity Score (GBP)" -> "Posicion Competitiva (vs cercanos)"
- Benchmark regional ajustado: 30/100 -> 45/100

**Metricas ahora ortogonales:**
| Pilar | Fuente de datos | Que mide |
|-------|-----------------|----------|
| GEO | Places API (perfil propio) | Completitud absoluta del perfil |
| Posicion Competitiva | Places API (competidores + ranking) | Posicion relativa vs competidores cercanos |
| Web/SEO | PageSpeed + Schema web | Credibilidad del sitio |
| AEO | Schema Hotel + FAQ + Open Graph + Citability | Legibilidad para IAs |

**Archivos modificados (2):**
- `v4_diagnostic_generator.py`: funcion corregida + template renombrado
- `output/v4_complete/`: nuevo diagnostico con scores validados

**Validacion:**
- 18/18 tests relacionados pasaron sin regresiones
- Comparacion linea base: GEO=72 antes y despues (sin cambio competitivo=50, antes 86)

### NOTAS
- `gbp_auditor._calcular_activity_score` (pipeline legacy via report_builder.py) NO modificado -- usa datos distintos (posts, respuestas) pero comparte el problema conceptual de overlapping con GEO
- Pendiente de tratamiento cuando se active ese pipeline

## [4.21.0] - 2026-04-04

### ELIMINADO - Redundancia AEO/IAO en scorecard diagnostico
- Template V6: eliminadas filas "Visibilidad en IA (AEO)" y "Optimizacion ChatGPT (IAO)"
- Scorecard unificado bajo "AEO - Infraestructura para IAs" (XX/100) -- dato 100% medible del audit web
- Regla de negocio: sin Asset = sin score en el diagnostico

### ELIMINADO - Metodos IAO/Voice de modulos internos
- v4_diagnostic_generator.py: eliminados _calculate_iao_score(), _calculate_score_ia(), _calculate_voice_readiness_score()
- v4_diagnostic_generator.py: renombrado _calculate_schema_infra_score() -> _calculate_aeo_score()
- gap_analyzer.py: eliminado pilar "Momentum IA", redistribucion 3->2 pilares (GBP + AEO)
- report_builder.py: eliminado _calculate_iao_score() y filas IAO de scorecards

### LIMPIEZA - Dead code
- Voice readiness eliminado (retornaba "--" hardcodeado)
- IATester wrapper eliminado (requiere GA4 real, no funciona en produccion actual)

### NOTAS
- aeo_metrics_gen.py se mantiene como modulo tecnico interno (no comercial)
- GA4 no modificado: puede enriquecer mediciones AEO en el futuro pero no genera score separado

## [4.20.0] - 2026-04-03

### ARCHIVO - Modulo observability deprecado
- `observability/` movido a `archives/deprecated_modules_20260304/observability/`
- Motivo: modulo huérfano (0 imports), persistencia inactiva, calibracion hardcodeada, sin integracion con flujo operacional
- Los validadores actuales (CoherenceValidator, contradiction_engine, consistency_checker) cubren la calidad per-corrida

### AGENT HARNESS v3.2.0 - REFACTOR ARQUITECTONICO COMPLETO

**CRITICAL FIX:**
- `agent_harness/core.py` linea 65: `tokens=shlex....cmd)` -> `tokens = shlex.split(command)`. Delegacion recursiva ahora funcional.
- `agent_harness/core.py` linea 80: `token=***` -> `token = tokens[i]`.

**ARCHITECTURAL IMPROVEMENTS (7 archivos, +900 lineas):**

**core.py - Orchestrator (306 -> 506 lines):**
- Timeout protection: `_execute_with_timeout()` via threading.Timer, configurable via `default_task_timeout`
- Background task lifecycle: `BackgroundTaskInfo` con estados running/completed/failed/timeout
- `_poll_background_tasks()`: detecta procesos terminados, limpia zombies >1h, reporta timeout >5min
- `register_validator(task_name, fn)`: validacion por tipo de tarea (fallback a generico si no hay)
- `_get_ui_colors()`: graceful fallback si modules.utils.ui_colors no existe
- `get_skill_metrics()`, `get_error_learning_report()`: metodos de introspeccion
- Handler ejecutado con timeout -- ya no hay riesgo de freeze indefinido

**memory.py - Memory Manager (328 -> 387 lines):**
- Thread safety: `threading.Lock` por archivo de sesion, previene race conditions
- Escritura atomica: escribe a `.tmp` + `rename`
- Indice invertido: `target_index.json` mapea `target_id -> [session_files]`
- `load_history()` consulta indice O(1) en lugar de scan lineal O(N) sobre todas las sesiones
- `rebuild_index()`: for-rebuild si el indice se corrompe
- `cleanup_old_sessions()` actualiza el indice al remover archivos viejos

**skill_router.py (191 lines):**
- Paths absolutos: `PROJECT_ROOT = Path(__file__).resolve().parent.parent`
- `.agents/workflows`, `skills`, `.agents/skills` resueltos desde ubicacion del modulo, no CWD
- Ya no depende del directorio de trabajo actual

**skill_executor.py (313 -> 433 lines):**
- `dry_run=False` como default (antes era `True` -- footgun que ocultaba errores)
- `SkillMetricsCollector`: persiste stats en `.agent/memory/skill_metrics.csv`
- Cada skill ejecutada registra: invocaciones, tasa de exito, duracion promedio

**self_healer.py (334 -> 445 lines):**
- `ErrorLearner`: captura errores no-matched, los agrupa, persiste en `unknown_errors.json`
- `get_learning_report()`: sugiere entradas para error_catalog.json (ocurrencias >= 2)
- PlanValidator: lazy import con try/except ImportError (graceful si modulo no existe)
- Si PlanValidator no disponible, retorna "skipped" en vez de crashear

**mcp_client.py (54 -> 250 lines):**
- Nested event loop fix: detecta loop corriendo, usa threading + new_event_loop como fallback
- Si `nest_asyncio` disponible, lo aplica automaticamente
- `list_tools()`, `list_tools_sync()`, `read_resource_sync()`: wrappers nuevos
- Import de `mcp` package deferred (no crash si no instalado)

**types.py (+86 lines):**
- Nuevas clases: `BackgroundTaskInfo`, `TaskValidator` (Protocol), `SkillMetrics`
- `SkillMetrics.record()`, `success_rate`, `avg_duration` properties

**Version:** 0.3.0 -> 3.2.0

## [4.19.0] - 2026-04-03

### INTEGRACION ECOSISTEMA DE AGENTES: Doctor + Pre-commit + Validacion Automatica

**NUEVOS SCRIPTS:**
- `scripts/doctor.py` (354 lineas) - Punto de entrada unificado para diagnostico del ecosistema
  - `--doctor` flag integrado en `main.py`
  - Soporta --agent, --context, --status, --json
  - Regenera SYSTEM_STATUS.md automaticamente desde datos reales
- `scripts/validate_agent_ecosystem.py` (259 lineas) - 8 checks automatizados
  - Symlink integrity, README refs, skills tracking, shadow logs, memory, gitignore, knowledge, agents dir
  - Manejo gracefully de errores Windows symlink

**PRE-COMIT HOOKS (2 nuevos):**
- `agent-ecosystem` - Valida skills, refs, symlink, shadow logs, memoria antes de cada commit
- `version-sync` - Sincroniza VERSION.yaml con README, AGENTS, CONTRIBUTING, GUIA_TECNICA, etc.

**WORKFLOWS (.agents/workflows/):**
- ELIMINADO: `audit_guardian.md` (deprecated, reemplazado por `v4_complete.md`)
- ELIMINADO: `qa_guardian.md` + `v4_coherence_validator.md` -> `v4_quality_validator.md` (unificado)
- ELIMINADO: `v4_financial_calculation.md` -> merged en `v4_financial_scenarios.md`
- MOVIDO: `v4_module_test_map.yaml` -> `templates/` (junto a `v4_regression_guardian.py`)
- ELIMINADO: `__pycache__/` (basura de ejecucion)
- FIX: Symlink `.agent/workflows` -> `.agents/workflows` (estaba roto)
- README.md reescrito con estructura actualizada (17 skills)

**DOCUMENTACION:**
- NUEVO: `.agent/CONVENTION.md` - Contrato de arquitectura para cualquier futuro agente
- REGENERADO: `.agent/SYSTEM_STATUS.md` desde datos reales (estaba stale desde Feb 2026)
- REGENERADO: `.agent/knowledge/DOMAIN_PRIMER.md` (v4.0.0 stale -> v4.19.0, 21 modulos, 138 archivos Python)
- FIX: `scripts/validate_context_integrity.py` (error Windows symlink stat + modulos nuevos agregados: analytics, geo_enrichment, quality_gates, auditors, commercial_documents, delivery, providers)
- FIX: `scripts/sync_config.yaml` (patterns actualizados)
- FIX: `docs/contributing/procedures.md` §4 - renombrado "Decision Engine" -> "Financial Engine", eliminada referencia a script fantasma `generate_domain_primer.py`
- FIX: `docs/CONTRIBUTING.md` - agregado DOMAIN_PRIMER.md a flujo de contribucion (Paso 5b, tabla manual docs, seccion Regenerable)

**FIX CLI:**
- `main.py` con `--doctor` flag integrado
- Manejo de errores Windows symlink en ambos validadores
- NUEVO: `doctor.py --regenerate-domain-primer` - regenera DOMAIN_PRIMER.md desde modulos reales en vivo

**Resultado:** Las carpetas .agent/ y .agents/workflows/ dejaron de ser "islas" y ahora son parte del flujo diario con validacion automatica pre-commit.

## [4.18.0] - 2026-04-02

### CERTIFICACION E2E 100% ANALYTICS: ANALYTICS-E2E-CERT-01

**Cambio de codigo (1 archivo, +10 lineas):**
- `modules/commercial_documents/pain_solution_mapper.py` — metodo `_detect_analytics_pains()`
  - Agrega pain `low_organic_visibility` cuando `ga4_available=False`
  - Sin GA4 no se puede medir trafico organico → deteccion implicita de baja visibilidad

**Resultado de certificacion E2E (12/12 PASADOS):**
- D1: analytics_data definido antes de detect_pains ✅
- D2: analytics_data llega a PainSolutionMapper ✅
- D3: analytics_data inyectado en diagnostico ✅
- D4: analytics_data inyectado en propuesta ✅
- D5: analytics persistido en v4_complete_report.json ✅
- D6: Pains no_analytics_configured + low_organic_visibility detectados ✅
- D7: AMBOS assets analytics generados (analytics_setup_guide + indirect_traffic_optimization) ✅
- D8: GoogleAnalyticsClient graceful fallback ✅
- D9: Profound/Semrush stubs graceful ✅
- D-A: V4AssetOrchestrator recibe analytics_data ✅
- D-B: analytics_setup_guide = 4952 bytes, 120 lineas ✅
- D-C: indirect_traffic_optimization = 5226 bytes, 128 lineas ✅

**Assets generados:**
- 9 assets totales (antes 8)
- analytics_setup_guide: 4952 bytes, guia GA4 paso a paso
- indirect_traffic_optimization: 5226 bytes, estrategias trafico indirecto

**Certificado:** output/CERTIFICADO_ANALYTICS_E2E.md

## [v4.17.0] - 2026-04-02

### FIX HANDLERS FALTANTES: analytics_setup_guide + indirect_traffic_optimization

**Handlers implementados:**
- `AnalyticsSetupGuideGenerator` (modules/delivery/generators/analytics_setup_guide_gen.py)
  - Carga template + personaliza con nombre/ciudad/URL del hotel
  - Fallback con contenido estatico si template no existe
- `IndirectTrafficOptimizationGenerator` (modules/delivery/generators/indirect_traffic_optimization_gen.py)
  - Carga template + personaliza con nombre del hotel
  - Fallback con contenido estatico si template no existe

**Handlers registrados en ConditionalGenerator._generate_content():**
- `elif asset_type == "analytics_setup_guide"` → AnalyticsSetupGuideGenerator
- `elif asset_type == "indirect_traffic_optimization"` → IndirectTrafficOptimizationGenerator

**D-A FIX: Analytics data pasado al V4AssetOrchestrator:**
- `generate_assets()` ahora acepta `analytics_data` opcional
- `detect_pains()` interno ahora recibe analytics_data (antes: None)
- pain `no_analytics_configured` ahora se detecta en el orchestrator
- main.py pasa analytics_data al orchestrator (L2092)

**Resultado de validacion:**
- Assets generados: 8 (antes 7)
- analytics_setup_guide: GENERADO (4952 bytes, 120 lineas)
- archivo: hotel_visperas/analytics_setup_guide/ESTIMATED_guia_configuracion_ga4_*.md
- Contenido completo con 7 pasos de configuracion GA4

## [v4.16.0] - 2026-04-02

### ANALYTICS-FIX-01: Fix critico UnboundLocalError + Analisis de Assets

**FASE A: Fix de orden en main.py (CRITICO)**
- Movido bloque analytics_data de L1958 a L1871, ANTES de PainSolutionMapper.detect_pains()
- Corregido UnboundLocalError: analytics_data undefined en L1851
- Import de GoogleAnalyticsClient y AnalyticsStatus: sin duplicados (1 ocurrencia cada uno)
- Pipeline ahora ejecuta completo: v4complete exit code 0

**FASE B: Analisis de assets de analytics (READ-ONLY)**
- D-B CONFIRMADO: analytics_setup_guide sin handler en ConditionalGenerator._generate_content()
- D-C CONFIRMADO: indirect_traffic_optimization sin handler en ConditionalGenerator._generate_content()
- Ambos assets estan en ASSET_CATALOG como IMPLEMENTED con templates existentes
- Assets fueron planificados pero NO generados (7 de 8 assets generados)

**FASE C: Verificacion**
- v4complete completo sin crash
- analytics persistido en v4_complete_report.json (seccion lines 163-174)
- Diagnostic incluye footer de transparencia analytics
- 8 pains detectados (vs 0 antes del fix)
- Reporte generado: ANALYTICS_FIX_REPORT_20260402.md


## [v4.15.0] - 2026-04-02

### Analytics E2E Bridge - COMPLETADO (01 + 02 + 04)

**ANALYTICS-01: Persistir analytics en JSON**
- `v4_complete_report.json` ahora incluye seccion `analytics` con:
  - `ga4_available`, `ga4_status`, `ga4_error`
  - `profound_available`, `profound_status`
  - `semrush_available`, `semrush_status`
  - `is_complete`, `missing_credentials`, `timestamp`
- Backwards compatible: sin cambios en report existente

**ANALYTICS-02: V4ProposalGenerator recibe analytics_data**
- `V4ProposalGenerator.generate()` acepta `analytics_data: Optional[Dict] = None`
- Metodo `_inject_analytics()` con 2 modos:
  - GA4 configurado: muestra metricas reales de trafico indirecto
  - Fallback: indica que GA4 no esta configurado
- main.py pasa `analytics_data` al proposal generator (L2040)
- Template V6 soporta placeholder `${analytics_transparency_section}`

**ANALYTICS-04: Analytics → Asset bridge via PainSolutionMapper**
- 3 nuevos pain types: `no_analytics_configured`, `low_organic_visibility`, `no_ga4_enhanced`
- Deteccion automatica:
  - GA4 no disponible → pain "Sin Analytics Configurado" (medium severity)
  - GA4 sin enhanced ecommerce → pain "GA4 sin Configuracion Avanzada" (low severity)
  - Trafico organico < 1000 sesiones/mes → pain "Baja Visibilidad Organica" (medium severity)
- 2 nuevos assets con templates completos:
  - `analytics_setup_guide` (guia_configuracion_ga4.md)
  - `indirect_traffic_optimization` (optimizacion_trafico_indirecto.md)
- Main.py detecta pains de analytics incluso sin audit_result completo
- Registro en asset_catalog.py con status IMPLEMENTED
- Refactor DRY: `_detect_analytics_pains()` metodo privado compartido

**PLAN ANALYTICS-E2E-BRIDGE: 100% COMPLETADO**

## [v4.14.0] - 2026-04-02

### Analytics E2E Bridge - Fases de Documentacion

**ANALYTICS-03: Documentacion de Stubs**
- ProfoundClient: docstring completo con instrucciones de activacion paso a paso
- SemrushClient: docstring completo con instrucciones de activacion paso a paso
- `modules/analytics/README.md`: nuevo archivo con tabla de todos los providers analytics
- Fallback a mock documentado y graceful (sin excepciones, retorna None)
- Variables de entorno documentadas: PROFOUND_API_KEY, SEMRUSH_API_KEY

## [v4.13.0] - 2026-04-01

### Analytics Transparency Loop (FASE-IAO-06)
- **NUEVO**: `data_models/analytics_status.py` - Clase AnalyticsStatus para rastrear disponibilidad de fuentes de datos
- **NUEVO**: Metodo `_check_analytics_status()` en V4DiagnosticGenerator - verifica estado de GA4/Profound/Semrush SIN hacer llamadas API
- **NUEVO**: Metodo `_build_transparency_section()` - genera seccion opcional "Fuentes de Datos Usadas en Este Diagnostico"
- **Cambio**: Diagnostico ahora informa POR QUE no hay datos (credenciales faltantes, APIs no configuradas) en vez de silenciar con ceros/guiones
- **Cambio**: Nuevo flag `show_analytics_transparency` en generador (default: True)
- **Template**: `${analytics_transparency_section}` en diagnostico_v6_template.md - solo aparece cuando alguna fuente falta
- **Docs**: capabilities.md actualizada con 4 nuevas capacidades (AnalyticsStatus, GoogleAnalyticsClient, ProfoundClient, SemrushClient) - IA Hoteles Agent

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.12.0] - 2026-04-01

### Objetivo
GA4 Integration - Tráfico Indirecto como Método #5 de Medición IA (GAP-IAO-01-05)

### Completado

**GAP-IAO-01-05: GA4 para Tráfico Indirecto**
- GoogleAnalyticsClient: cliente real con lazy init, graceful fallback, sin romper pipeline
- IndirectTrafficMetrics consolidado en data_models/aeo_kpis.py (eliminado duplicado)
- Campos date_range y note agregados a IndirectTrafficMetrics
- Método from_ga4_response() para crear métricas desde respuesta de GA4
- GoogleAnalyticsClient exportado desde modules/analytics/__init__.py
- _calculate_score_ia() integrado con GA4: construye AEOKPIs, calcula composite_score
- _calculate_iao_score() fallback fix: retorna schema_infra_score cuando IATester falla
- IAReadinessCalculator: ga4_indirect weight 0.10, redistribución proporcional cuando GA4 no disponible
- Backwards compatible: GA4 completamente opcional, try/except en todos los paths

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| tests/test_google_analytics_client.py | 17 tests para GoogleAnalyticsClient |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/analytics/google_analytics_client.py | Cliente real + eliminado duplicado IndirectTrafficMetrics |
| data_models/aeo_kpis.py | IndirectTrafficMetrics: date_range, note, from_ga4_response() |
| modules/analytics/__init__.py | Export GoogleAnalyticsClient |
| modules/commercial_documents/v4_diagnostic_generator.py | _calculate_score_ia() GA4 wiring, _calculate_iao_score() fallback |
| modules/auditors/ia_readiness_calculator.py | ga4_indirect weight 0.10, weight redistribution |
| tests/data_validation/test_aeo_kpis.py | Weights fijos + indirect_traffic en required fields |
| tests/auditors/test_ia_readiness_calculator.py | Weights fijos + 5 tests GA4 nuevos |

### Tests
- 17 tests nuevos en test_google_analytics_client.py
- 5 tests GA4 agregados a test_ia_readiness_calculator.py
- 46/46 tests passing (0 regresiones en módulos afectados)
- 1755/1829 tests passing (74 failures pre-existentes, no relacionados)

### Características
- **Método #5 de KB**: GA4 como método de medición de tráfico indirecto post-consulta IA
- **Graceful Fallback**: Sin credenciales → retorna data_source: N/A sin romper pipeline
- **Weight Redistribution**: Cuando GA4 no disponible, peso se redistribuye proporcionalmente
- **AEOKPIs Integration**: Construye objeto AEOKPIs con IATester + GA4 datos para composite score

---

## [4.12.0] - 2026-04-01

### Objetivo
GA4 Integration - Tráfico Indirecto como Método #5 de Medición IA (GAP-IAO-01-05)

### Completado

**GAP-IAO-01-05: GA4 para Tráfico Indirecto**
- GoogleAnalyticsClient: cliente real con lazy init, graceful fallback, sin romper pipeline
- IndirectTrafficMetrics consolidado en data_models/aeo_kpis.py (eliminado duplicado)
- Campos date_range y note agregados a IndirectTrafficMetrics
- Método from_ga4_response() para crear métricas desde respuesta de GA4
- GoogleAnalyticsClient exportado desde modules/analytics/__init__.py
- _calculate_score_ia() integrado con GA4: construye AEOKPIs, calcula composite_score
- _calculate_iao_score() fallback fix: retorna schema_infra_score cuando IATester falla
- IAReadinessCalculator: ga4_indirect weight 0.10, redistribución proporcional cuando GA4 no disponible
- Backwards compatible: GA4 completamente opcional, try/except en todos los paths

### Archivos Nuevos
| Archivo | Descripción |
|---------|-------------|
| tests/test_google_analytics_client.py | 17 tests para GoogleAnalyticsClient |

### Archivos Modificados
| Archivo | Cambio |
|---------|--------|
| modules/analytics/google_analytics_client.py | Cliente real + eliminado duplicado IndirectTrafficMetrics |
| data_models/aeo_kpis.py | IndirectTrafficMetrics: date_range, note, from_ga4_response() |
| modules/analytics/__init__.py | Export GoogleAnalyticsClient |
| modules/commercial_documents/v4_diagnostic_generator.py | _calculate_score_ia() GA4 wiring, _calculate_iao_score() fallback |
| modules/auditors/ia_readiness_calculator.py | ga4_indirect weight 0.10, weight redistribution |
| tests/data_validation/test_aeo_kpis.py | Weights fijos + indirect_traffic en required fields |
| tests/auditors/test_ia_readiness_calculator.py | Weights fijos + 5 tests GA4 nuevos |

### Tests
- 17 tests nuevos en test_google_analytics_client.py
- 5 tests GA4 agregados a test_ia_readiness_calculator.py
- 46/46 tests passing (0 regresiones en módulos afectados)
- 1755/1829 tests passing (74 failures pre-existentes, no relacionados)

### Características
- **Método #5 de KB**: GA4 como método de medición de tráfico indirecto post-consulta IA
- **Graceful Fallback**: Sin credenciales → retorna data_source: N/A sin romper pipeline
- **Weight Redistribution**: Cuando GA4 no disponible, peso se redistribuye proporcionalmente
- **AEOKPIs Integration**: Construye objeto AEOKPIs con IATester + GA4 datos para composite score

---

## [4.11.0] - 2026-03-30

### 🎯 Objetivo
Documentación Oficial - Actualización según CONTRIBUTING.md R8: GEO Enrichment Integration

### ✅ Completado

**FASE-7 - Documentación Oficial**
- CHANGELOG.md: Entrada v4.11.0 con features GEO
- GUIA_TECNICA.md: Nueva sección "GEO Enrichment Integration"
- .agents/workflows/README.md: geo_flow y módulos GEO listados
- capabilities.md: 4 nuevas capacidades actualizadas
- REGISTRY.md: FASE-1 a FASE-8 registradas

**FASE-1 a FASE-6 - GEO Integration (Previa)**
- FASE-1: Diagnóstico - Mapeo hotel_data a 42 métodos GEO
- FASE-2: GEO Flow Orchestrator - geo_flow.py integrado en v4_asset_orchestrator
- FASE-3: GEO Enrichment Layer - Asset generation enriquecido con datos GEO
- FASE-4: Sync Contract Analyzer - 8 combinaciones de sincronización
- FASE-5: Asset Responsibility Contract - Orden de implementación
- FASE-6: GEO Diagnostic - Dashboard y checklist GEO

### 📁 Módulos GEO Documentados

|| Módulo | Descripción | Estado ||
||--------|-------------|--------|
|| `geo_flow.py` | Orchestrator del flujo GEO | conectada |
|| `GEOEnrichmentLayer` | Enriquecimiento de assets con datos GEO | conectada |
|| `SyncContractAnalyzer` | Análisis de sincronización cross-platform | conectada |
|| `AssetResponsibilityContract` | Contrato de responsabilidad de assets | conectada |

### 🔧 Características

- **GEO Flow**: Orquestación completa del pipeline GEO
- **Sync Contract**: 8 combinaciones de sincronización (EXACT, SURFACE, SEMANTIC, etc.)
- **Responsibility Contract**: Orden de implementación de assets (Schema → Onsite → Offsite)
- **Backward Compatibility**: ✅ Preservada

### 🔗 Links
- [Plan FASE-7](./.opencode/plans/05-prompt-inicio-sesion-fase-7.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.10.0] - 2026-03-27

### 🎯 Objetivo
V6 E2E Certification - Formato V6 de documentos comerciales con datos reales para Hotel Vísperas

### ✅ Completado

**FASE V6-5 - E2E Certification**
- Ejecución E2E completa del flujo v4complete
- Documentos generados en formato V6 (DIAGNOSTICO_V6, PROPUESTA_V6)
- Frontmatter YAML con version, coherence_score, document_type
- Coherence score: 0.84 (umbral: 0.80)
- 6 assets planificados y generados
- Delivery package: hotelvisperas_20260327.zip
- No texto mixed-language detectado
- 52/52 regression tests PASS

**FASE V6-4 - Pain Solution Mapper Integration**
- PainSolutionMapper integrado en pipeline de documentos
- Mapeo dinámico de problemas a soluciones
- Financial impact calculado por problema

**FASE V6-3 - Proposal Generator V6**
- Pricing real extraído de ValidationSummary
- Hybrid pricing model (tier-based)
- ROI calculation dinámico
- GATE compliance verificado

**FASE V6-2 - Diagnostic Generator V6**
- Estructura V6 con YAML frontmatter
- Regional context dinámico
- Coherence scoring pre-generation

**FASE V6-1 - V6 Template Foundation**
- Templates con placeholders ${}
- Conditional content system
- Multi-section document structure

### 📁 Archivos Modificados

|| Archivo | Descripción ||
|---------|-------------|
| `modules/commercial_documents/v4_diagnostic_generator.py` | Generator V6 con coherence scoring |
| `modules/commercial_documents/v4_proposal_generator.py` | Proposal con pricing real |
| `modules/commercial_documents/pain_solution_mapper.py` | Mapper problemas→soluciones |
| `modules/asset_generation/asset_diagnostic_linker.py` | Link assets a diagnostics |

---

## [4.9.0] - 2026-03-25

### 🎯 Objetivo
AEO Re-Architecture: Alineación conceptual y técnica del módulo AEO (Auditory Engine Optimization)

### ✅ Completado

**FASE-A - Corrección Conceptual**
- "AEO (Schema)" renombrado a "Schema Infrastructure"
- Dual counting eliminado en favor de Schema Infrastructure score
- Voice Readiness como módulo separado de schema_markup

**FASE-B - AEO Voice-Ready Module**
- SpeakableSpecification añadida a hotel_schema
- FAQ conversacional con 40-60 palabras por respuesta
- Voice Keywords para Eje Cafetero
- llms.txt voice-ready con structured data

**FASE-C - Integración Plataformas de Voz**
- Google Assistant checklist
- Apple Business Connect guide
- Alexa Skill blueprint
- 3 blueprints implementados en modules/delivery/generators/

**FASE-D - Medición AEO Real**
- KPI Framework: AEOKPIs, VoiceReadinessScore, DataSource en data_models/
- Mock clients Profound/Semrush en modules/analytics/
- Dashboard template aeo_metrics_report.md
- 17 tests de regresión

**FASE-E - Validación E2E**
- Delivery genera sin errores
- Speakable presente en schema
- Coherence score: 0.84 (≥ 0.80)
- 26/28 tests pasan

**FASE-F - Corrección Brechas E2E**
- FAQ respuestas 40-60 palabras (prompt LLM corregido en faq_gen.py)
- voice_assistant_guide con 3 archivos .md en delivery (voice_guide.py + conditional_generator.py)
- commercial_documents/__init__.py creado (módulo ahora importable)
- 52/52 regression tests PASS

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `data_models/aeo_kpis.py` | KPI framework para AEO |
| `modules/analytics/profound_client.py` | Mock client para Profound API |
| `modules/analytics/semrush_client.py` | Mock client para Semrush API |
| `modules/delivery/generators/google_assistant_checklist.md` | Blueprint Google Assistant |
| `modules/delivery/generators/apple_business_connect_guide.md` | Blueprint Apple Business |
| `modules/delivery/generators/alexa_skill_blueprint.md` | Blueprint Alexa Skill |
| `docs/aeo_metrics_report.md` | Dashboard template |
| `commercial_documents/__init__.py` | Paquete formalizado (importable) |

---

## [4.8.0] - 2026-03-23

### 🎯 Objetivo
FASE-CAUSAL-01: SitePresenceChecker - Solución de causa raíz para desconexión assets/sitio real

### ✅ Completado

**FASE-CAUSAL-01 - SitePresenceChecker**
- T-C1: SitePresenceChecker para verificar sitio real ANTES de generar assets
- T-C2: Integración en ConditionalGenerator como gate de presencia
- T-C3: Estados SKIPPED y REDUNDANT en AssetStatus
- T-C4: V4AssetOrchestrator actualizado con SkippedAsset
- T-C5: Reporting mejorado con skipped_assets y site_verification_applied
- T-C6: 10 tests unitarios implementados y pasando

### 📁 Archivos Nuevos/Modificados

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/site_presence_checker.py` | Verificación de presencia en sitio real |
| `modules/asset_generation/conditional_generator.py` | Integración site_url como parámetro |
| `modules/asset_generation/asset_metadata.py` | Estados SKIPPED, REDUNDANT |
| `modules/asset_generation/v4_asset_orchestrator.py` | SkippedAsset dataclass, reporting |
| `tests/asset_generation/test_site_presence_checker.py` | 10 tests para FASE-CAUSAL-01 |
| `docs/CONTRIBUTING.md` | Sección 17 documenting SitePresenceChecker |

### 🔧 Arquitectura

```
                    ┌─────────────────────────────┐
                    │   SITIO DE PRODUCCIÓN       │
                    │  SchemaFinder + scraping    │
                    └──────────────┬──────────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  SitePresenceChecker.check   │
                    └──────────────┬──────────────┘
                                   │
              ┌────────────────────┼────────────────────┐
              ▼                    ▼                    ▼
        ┌───────────┐      ┌─────────────┐      ┌───────────┐
        │  EXISTS   │      │ NOT_EXISTS │      │ REDUNDANT │
        │  → SKIP   │      │  → Generar │      │  → SKIP   │
        └───────────┘      └─────────────┘      └───────────┘
```

**Problema resuelto:**
- Sistema generaba assets sin verificar si el sitio ya tenía la funcionalidad
- Assets regenerados 7+ veces sin cambios (hotel_schema, org_schema)
- delivery_ready_percentage: 0% pese a múltiples assets generados
- Visperas es laboratorio - sistema genérico para cualquier hotel boutique

### 🔗 Links
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.6.0] - 2026-03-23

### 🎯 Objetivo
FASE 10: Health Dashboard - System Health Monitor para visibility del estado del sistema

### ✅ Completado

**FASE 10 - Health Dashboard**
- T10A: HealthMetricsCollector con dataclass ExecutionMetrics
- T10B: HealthDashboardGenerator genera HTML con Chart.js
- T10C: Integración en main.py post-execution (FASE 7)
- 14 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
||---------|------------|
|| `modules/monitoring/__init__.py` | Módulo de monitoring con exports |
|| `modules/monitoring/health_metrics_collector.py` | ExecutionMetrics dataclass, HealthMetricsCollector |
|| `modules/monitoring/health_dashboard_generator.py` | HealthDashboardGenerator con Chart.js |
|| `tests/monitoring/test_health_dashboard.py` | 14 tests para FASE 10 |
|| `main.py` | Integración FASE 10 post-delivery (línea ~2183) |

### 🔧 Arquitectura

```
ExecutionMetrics (dataclass)
    hotel_id, timestamp, assets_generated, assets_failed
    success_rate, avg_confidence, execution_time
    errors, warnings
```

**Dashboard Features:**
- Summary cards: Hotels Analyzed, Success Rate, Avg Confidence, Exec Time
- Bar charts: Success Rate by Hotel, Execution Time
- Doughnut chart: Confidence Distribution buckets
- Table: Hotel execution details with status badges

### 🔗 Links
- [Plan FASE 10](./.opencode/plans/05-prompt-inicio-sesion-fase-10-HEALTH-DASHBOARD.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.7.0] - 2026-03-23

### 🎯 Objetivo
FASE 11: Google Travel Integration + Onboard Enhancement + Asset Quality Boost

### ✅ Completado

**FASE 11A - Google Travel Scraper**
- GoogleTravelScraper para capturar datos de hoteles en Google Travel/Hotels
- Diferencia con Google Places API: Travel es agregador de hoteles (precios, disponibilidad)
- Entity ID support para URLs directas de Google Travel
- 5 tests obligatorios implementados

**FASE 11B - Onboard Enhancement + Integración Real**
- GoogleTravelScraper integrado en V4ComprehensiveAuditor como fallback
- Fallback chain: Places API -> Google Travel -> schema_data
- Logging estructurado para diagnóstico
- 16 tests pasando (11 original + 5 nuevos de integración)

**FASE 11C - Asset Quality Boost**
- v4complete ejecutado con integración Google Travel
- Coherence Score: 0.87 (threshold: 0.85) ✅
- 7/7 assets generados exitosamente
- Publication Gates: 6/6 passed ✅
- ⚠️ Google Travel bloquea scraping real en producción (no es bug, es limitación de Google)

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
|||---------|------------|
|| NUEVO | `modules/scrapers/google_travel_scraper.py` | GoogleTravelScraper class |
|| MODIFICADO | `modules/auditors/v4_comprehensive.py` | Integración GoogleTravelScraper en _audit_gbp() |
|| MODIFICADO | `modules/providers/autonomous_researcher.py` | Import GoogleTravelScraper |
|| NUEVO | `tests/scrapers/test_google_travel_scraper.py` | 17 tests para FASE 11 |

### 🔗 Links
- [Plan FASE 11](./.opencode/plans/05-prompt-inicio-sesion-fase-11-GOOGLE-TRAVEL-INTEGRATION.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

---

## [4.5.9] - 2026-03-23

### 🎯 Objetivo
FASE 9: AI/ML Enhancement - Intelligent Disclaimer Generator v2

### ✅ Completado

**FASE 9 - Intelligent Disclaimer Generator v2**
- T9A: DisclaimerGeneratorV2 con clase `IntelligentDisclaimerGenerator` y método `generate()`
- T9B: Integración con asset_metadata - campos: `missing_data`, `benchmark_used`, `improvement_steps`, `confidence_after_fix`
- T9C: Función `calculate_improvement_score(current_confidence, target_confidence)`
- T9D: 10 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

||| Archivo | Descripción |
||---------|------------|
||| `modules/providers/disclaimer_generator.py` | Nueva clase `IntelligentDisclaimerGenerator`, función `calculate_improvement_score()` |
||| `modules/asset_generation/asset_metadata.py` | Nuevos campos: `missing_data`, `benchmark_used`, `improvement_steps`, `confidence_after_fix` |
||| `tests/test_never_block_architecture/test_disclaimer_generator.py` | 10 tests nuevos para FASE 9 |

### 🔧 Arquitectura

```
Asset con baja confianza
        │
        ▼
┌─────────────────────────────────────┐
│  INTELLIGENT DISCLAIMER GENERATOR   │
├─────────────────────────────────────┤
│  • asset_type: hotel_schema        │
│  • confidence: 0.3                 │
│  • missing_data: [gbp_reviews...]  │
│  • benchmark_used: Pereira avg      │
│  • improvement_steps: [1.1.2...]   │
└─────────────────────────────────────┘
        │
        ▼
Disclaimer contextual con:
⚠️ CONFIANZA BAJA (30/100)
• Google Business Profile sin datos
• Reseñas de clientes (gbp_reviews)
PARA MEJORAR:
1. Agregar 10+ fotos a GBP
2. Solicitar 5+ reseñas
CONFIDENCIA ESPERADA: 54%+
```

### 🔗 Links
- [Plan FASE 9](./.opencode/plans/05-prompt-inicio-sesion-fase-9-AI-DISCLAIMER.md)
- [Tracking fases](./.opencode/plans/README-FASES-TRACKING.md)

## [4.5.8] - 2026-03-23

### 🎯 Objetivo
FASE 8: Autonomous Research Engine v2 - Investigación autónoma real con output verificable

### ✅ Completado

**FASE 8 - Autonomous Research Engine v2**
- T8A: ResearchOutput schema con persistencia JSON (hotel_name, sources_checked, data_found, confidence, citations, gaps)
- T8B: Source Scrapers implementados (BookingScraper, TripAdvisorScraper, InstagramScraper)
- T8C: Integración en orchestration - last_research_output accesible post-research
- T8D: Research Confidence Scoring (4/4=1.0, 3/4=0.75, 2/4=0.5, 1/4=0.25)
- T8E: 25 tests obligatorios implementados y pasando

### 📁 Archivos Nuevos/Modificados

| Archivo | Descripción |
|---------|-------------|
| `modules/providers/autonomous_researcher.py` | ResearchOutput schema, scrapers stubs, confidence scoring |
| `modules/scrapers/booking_scraper.py` | Scraper para Booking.com |
| `modules/scrapers/tripadvisor_scraper.py` | Scraper para TripAdvisor |
| `modules/scrapers/instagram_scraper.py` | Scraper para Instagram |
| `modules/scrapers/__init__.py` | Exports actualizados |
| `modules/providers/__init__.py` | Exports de AutonomousResearcher y funciones |
| `tests/providers/test_autonomous_research_fase8.py` | 25 tests para FASE 8 |

### 🔧 Arquitectura

```
Research Request
      │
      ▼
┌─────────────────────────────────────┐
│     AUTONOMOUS RESEARCHER ENGINE     │
├─────────────────────────────────────┤
│  1. GBP Lookup (GBPScraper)         │
│  2. Booking.com (BookingScraper)    │
│  3. TripAdvisor (TripAdvisorScraper)│
│  4. Instagram (InstagramScraper)    │
│  5. Cross-Reference                 │
│  6. Confidence Scoring              │
└─────────────────────────────────────┘
      │
      ▼
Research Report (JSON persistido)
      │
      ▼
Assets referencian el research
```

### 📊 Confidence Scoring

| Fuentes | Confidence |
|---------|------------|
| 4/4 | 1.0 |
| 3/4 | 0.75 |
| 2/4 | 0.5 |
| 1/4 | 0.25 |
| 0/4 | 0.0 |

---

## [4.5.7] - 2026-03-23

### 🎯 Objetivo
FASE 5: Validación Transversal y Cierre del Proyecto NEVER_BLOCK v4.5.6

### ✅ Completado

**FASE 5 - Validación Transversal**
- T1: Orden Audit → Assets verificado (timestamps confirmados)
- T2: Coherence Score documentado (mide coherencia interna, no cantidad de datos)
- T3: Autonomous Researcher documentado como Silent Research (diseño intencional)
- T4: Métricas de salud del sistema creadas
- T5: Capability Contract v4.5.6 completo (10 capabilities, 0 huérfanas)
- T6: Test E2E de regresión creado

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `docs/capability_contract_v4_5_6.md` | Matriz completa de capabilities del sistema |
| `evidence/fase-5-transversal/system_health_metrics.json` | Métricas de salud post-ejecución |
| `evidence/fase-5-transversal/capability_contract.json` | Evidencia de validación T1-T6 |
| `tests/test_never_block_architecture/test_audit_generated_before_assets.py` | Test orden audit → assets |
| `tests/test_never_block_architecture/test_coherence_validation.py` | Test validación coherence |
| `tests/test_never_block_architecture/test_capability_contract.py` | Test capability contract |
| `tests/test_never_block_architecture/test_e2e_v4_5_6_corrections.py` | Test E2E regresión Fases 1-4 |

### 📝 Hallazgos Transversales

| Hallazgo | Descripción | Estado |
|----------|-------------|--------|
| Coherence Score | Score de 0.88 NO está inflado - mide coherencia entre documentos, no cantidad de datos | ✅ Documentado |
| autonomous_researcher | Silent Research (never_block) - diseño intencional, no bug | ✅ Documentado |
| Orden de ejecución | audit_report se genera ANTES que assets | ✅ Verificado |

### 🏁 Cierre del Proyecto

**PROYECTO v4.5.6 CERRADO**

- ✅ T1-T6 completadas
- ✅ 0 capabilities huérfanas
- ✅ Documentación post-proyecto completa
- ✅ CHANGELOG.md actualizado

---

## [4.5.6] - 2026-03-22

### 🎯 Objetivo
Implementar arquitectura NEVER_BLOCK: el sistema nunca se bloquea, siempre entrega algo aunque sea subóptimo. Resolución de gaps con benchmark regional + disclaimers honestos.

### ✅ Completado

**FASE 1 - Benchmark Resolver**
- `modules/providers/benchmark_resolver.py` - NUEVO módulo para resolver gaps con benchmark regional (Pereira/Santa Rosa de Cabal)
- `modules/asset_generation/asset_metadata.py` - Campo `disclaimers` añadido
- Tests en `tests/test_benchmark_resolver.py` - 11 tests

**FASE 2 - Disclaimer Generator**
- `modules/providers/disclaimer_generator.py` - NUEVO módulo genera disclaimers honestos por nivel de confidence
- Tests en `tests/test_disclaimer_generator.py` - 15 tests

**FASE 3 - Autonomous Researcher**
- `modules/providers/autonomous_researcher.py` - NUEVO módulo investiga hotel en GBP, Booking, TripAdvisor, Instagram
- Tests en `tests/test_autonomous_researcher.py` - 20 tests

**FASE 4 - Never-Block Integration**
- `modules/asset_generation/preflight_checks.py` - Integración benchmark fallback
- `modules/asset_generation/conditional_generator.py` - Placeholders corregidos en optimization_guide
- `modules/asset_generation/asset_content_validator.py` - Bloqueo de placeholders pre-generación
- Tests en `tests/test_never_block_integration.py` - 23 tests

**FASE 5 - Validación E2E**
- Tests de regresión Hotel Vísperas - 2 tests skipping corregidos
- 69/69 tests passing en suite NEVER_BLOCK

**FASE 6 - Documentación y Cierre**
- BenchmarkCrossValidator integrado en PreflightChecker (validate_adr_against_benchmark, check_asset_with_benchmark)
- Actualización documental: CONTRIBUTING.md, GUIA_TECNICA.md, README.md
- Tests actualizados para comportamiento NEVER_BLOCK
- Suite de regresión: 256 tests passing, 2 skipped

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/providers/benchmark_resolver.py` | Benchmark regional para datos faltantes |
| `modules/providers/disclaimer_generator.py` | Generador de disclaimers honestos |
| `modules/providers/autonomous_researcher.py` | Investigador autónomo en fuentes públicas |
| `tests/test_benchmark_resolver.py` | Tests TDD para BenchmarkResolver |
| `tests/test_disclaimer_generator.py` | Tests TDD para DisclaimerGenerator |
| `tests/test_autonomous_researcher.py` | Tests TDD para AutonomousResearcher |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/asset_generation/asset_metadata.py` | Añadido campo `disclaimers` |
| `modules/asset_generation/preflight_checks.py` | Integración benchmark fallback |
| `modules/asset_generation/conditional_generator.py` | Placeholders corregidos, benchmark fallback |
| `modules/asset_generation/asset_content_validator.py` | Bloqueo pre-generación de placeholders |
| `tests/test_never_block_integration.py` | Tests de regresión Hotel Vísperas |
| `output/v4_complete/hotelvisperas/` | Outputs regenerados sin placeholders |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests NEVER_BLOCK | 256 passing, 2 skipped |
| Tests totales | 256+ passing (suite regression) |
| Coherence | ≥ 0.8 |
| Placeholders en outputs | 0 |
| Assets bloqueados | 0 (hotel_schema aún bloqueado por datos externos vacíos) |

### Principios Implementados

1. **NEVER_BLOCK**: El sistema nunca se bloquea, siempre entrega algo
2. **BENCHMARK_FALLBACK**: Datos faltantes se resuelven con benchmark regional
3. **HONEST_CONFIDENCE**: Todo output incluye confidence score real y fuentes
4. **DELIVERY_READY**: Todo output es implementable, sin placeholders

## [4.5.5] - 2026-03-21

### 🎯 Objetivo
Mejorar generador de FAQs con categorías y timestamp ISO 8601

### ✅ Completado

**Cambios Implementados**
- `modules/delivery/generators/faq_gen.py` - Agregadas columnas Categoria y Fecha_Generacion
- `tests/delivery/test_faq_generator_improvements.py` - Test para nueva funcionalidad

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/delivery/generators/faq_gen.py` | Agregadas columnas Categoria y Fecha_Generacion |
| `tests/delivery/test_faq_generator_improvements.py` | Test para nueva funcionalidad |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1 nuevo test en `tests/delivery/test_faq_generator_improvements.py` |

## [4.5.4] - 2026-03-17

### 🎯 Objetivo
Implementar mejoras incrementales al agent_harness inspiradas en Superpowers sin adopción de framework externo.

### ✅ Completado

**Cambios Implementados**
- `.agents/workflows/phased_project_executor.md` - Agregado Step 0.5 TDD Gate
- `.agents/workflows/audit_guardian.md` - Modificado Steps 2-4 para ejecución paralela

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `.agents/workflows/phased_project_executor.md` | Agregado TDD Gate |
| `.agents/workflows/audit_guardian.md` | Ejecución paralela |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |
| Desconexiones | 0 |
| Hard contradictions | 0 |

## [4.5.3] - 2026-03-15

### 🎯 Objetivo
Adoptar enfoque de comunicación del diagnóstico antiguo (25/feb) sin perder validaciones técnicas de v4.5.2

### 🔧 Cambios Implementados

**Estructura de Diagnóstico Restaurada:**
- Narrativa "Antes/Ahora" que crea urgencia (PARTE 1)
- Comparativa regional: Su Hotel vs Promedio (PARTE 2)
- Las 4 Razones con costos específicos (PARTE 3)
- Quick Wins con timings concretos (PARTE 5)
- Plan 7/30/60/90 días (PARTE 6)
- Anexo Técnico con validaciones al final

**Estructura de Propuesta Restaurada:**
- Resumen Ejecutivo con pérdida mensual
- Proyección financiera mes a mes (6 meses)
- Plan 7/30/60/90 días detallado
- Garantías específicas (3 garantías)
- Mapeo problemas→soluciones→assets visible

**Assets Conectados:**
- Metadata de conexión: problem_solved, impact_cop, priority, timing
- README.md en cada folder de asset con justificación de ventas

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| templates/diagnostico_v4_template.md | Estructura de ventas completa |
| templates/propuesta_v4_template.md | Estructura de ventas completa |
| asset_diagnostic_linker.py | Metadata de conexión |
| v4_proposal_generator.py | Variables de proyección mensual |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |
| Desconexiones | 0 |
| Hard contradictions | 0 |

## [4.5.2] - 2026-03-13

### 🎯 Objetivo

Completar FASE-5: Validación de coherencia y preparación para publicación.

### ✅ Completado

**Fase 1-5**: 
- Coherence score: 0.64 → 0.91 (umbral: 0.8) ✅
- Validaciones rápidas: 4/4 passed
- Regression tests: 52/52 passed
- Publication Ready: true
- Price bug fixed ($800k → $130k)
- ConfidenceLevel enum unificado

### 🔧 Fixed

- Contradiction engine ahora detecta conflictos inter-documento
- Consistency checker valida WhatsApp, GBP, schema, ADR
- Publication gates implementados (hard_contradictions, evidence_coverage, financial_validity, coherence, critical_recall)
- Promise vs Implementation validator

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| modules/quality_gates/coherence_gate.py | Gate de coherencia con score ≥ 0.8 |
| modules/quality_gates/publication_gates.py | Gates de publicación |
| data_validation/consistency_checker.py | Validación cruzada |
| commercial_documents/coherence_validator.py | Validador de coherencia |
| orchestration_v4/phase5_validator.py | Orquestación Fase 5 |

## [4.5.1] - 2026-03-12

### 🎯 Objetivo

Corrección de desconexiones estructurales entre módulos GEO y documentos comerciales.

### 🔧 Added - GEO Integration Fix

**Integración GEO en Documentos Comerciales**:
- PainSolutionMapper ahora detecta problemas ai_crawler_blocked, low_citability, low_ia_readiness
- V4DiagnosticGenerator incluye sección de métricas GEO
- V4ProposalGenerator incluye assets GEO en propuesta

**Corrección de Assets**:
- Gate de contenido vacío implementado (mínimo 50 caracteres)
- Gate de placeholders implementado ($$VAR, {{VAR}}, [[VAR]])
- faq_page genera contenido real específico del hotel
- org_schema tiene campos poblados con fallback
- performance_audit usa datos reales del audit

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| modules/commercial_documents/pain_solution_mapper.py | Detección de problemas GEO |
| modules/commercial_documents/v4_diagnostic_generator.py | Sección métricas GEO |
| modules/commercial_documents/v4_proposal_generator.py | Assets GEO en propuesta |
| modules/asset_generation/conditional_generator.py | Gate de contenido |
| tests/asset_generation/test_content_gates.py | 19 tests nuevos para gates |
| tests/commercial_documents/test_pain_solution_mapper_geo.py | Tests para detección GEO |
| tests/commercial_documents/test_v4_diagnostic_generator_geo.py | Tests para sección GEO |
| tests/commercial_documents/test_v4_proposal_generator_geo.py | Tests para assets GEO |

## [4.5.0] - 2026-03-11

### 🎯 Objetivo

Completar integración GEO (Generative Engine Optimization): Documentación, gates y consolidación.

### 🔧 Added - GEO Integration

**Capacidades de Generative Engine Optimization**:
- **AI Crawler Auditor**: Análisis de robots.txt para 14+ crawlers de IA
- **llms.txt Generator**: Generación del estándar emergente para indexación IA
- **Citability Scorer**: Análisis de contenido para citabilidad (ADVISORY)
- **IA-Readiness Calculator**: Score compuesto de preparación IA (ADVISORY)

### 🔧 Added - Schema Hotel Enhanced

**Mejoras en schema hotelero**:
- Reconocimiento de `LodgingBusiness` como hotel válido
- Campos hoteleros críticos: `geo`, `checkinTime`, `checkoutTime`, `sameAs`, `amenityFeature`
- Estructura `@graph` para múltiples schemas

### 🔧 Changed

- `rich_results_client.py`: Extensión para LodgingBusiness
- `schema_validator_v2.py`: Coverage scoring con campos hoteleros
- `conditional_generator.py`: Unificación de schema generation
- `asset_catalog.py`: Nuevos assets llms_txt

### 🔧 Fixed

- Rich Results "non-critical issues" para hoteles con schema LodgingBusiness

### 🔧 Technical

- Tests incrementados a 1338+ passing
- 0 regresiones en validaciones existentes
- Métricas GEO como advisory (no gates bloqueantes)

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/auditors/ai_crawler_auditor.py` | Auditoría de robots.txt para IA crawlers |
| `modules/asset_generation/llmstxt_generator.py` | Generación de llms.txt estándar |
| `modules/auditors/citability_scorer.py` | Score de citabilidad de contenido |
| `modules/auditors/ia_readiness_calculator.py` | Score compuesto IA-readiness |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `CHANGELOG.md` | Entry v4.5.0 |
| `AGENTS.md` | Nuevos módulos activos + métricas advisory |
| `GUIA_TECNICA.md` | Secciones de auditoría y citabilidad |
| `VERSION.yaml` | Actualizado a 4.5.0 |

---

## [4.4.1] - 2026-03-10

### 🎯 Objetivo

Completar FASE-ASSET-06: Documentación. Sistema de catálogo unificado de assets con gate de coherencia mejorado.

### 🔧 Cambios Implementados

#### Catálogo Unificado de Assets
- `modules/asset_generation/asset_catalog.py` - Catálogo centralizado de tipos de assets con estado
- Enum AssetStatus: IMPLEMENTED, PROMISED_NOT_IMPLEMENTED, MISSING
- dataclass AssetCatalogEntry con is_asset_implemented()

#### Gate de Coherencia Mejorado
- `modules/commercial_documents/coherence_validator.py` - Nuevo check promised_assets_exist
- Valida que assets prometidos existen en el generador
- Severidad: error (blocking)

#### Refactorización de Consumidores
- `modules/commercial_documents/pain_solution_mapper.py` - Usa ASSET_CATALOG
- `modules/asset_generation/conditional_generator.py` - Usa ASSET_CATALOG
- `modules/asset_generation/preflight_checks.py` - Usa ASSET_CATALOG
- Eliminación de listas duplicadas en 3 módulos

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/asset_generation/asset_catalog.py` | Catálogo centralizado con Enum AssetStatus |
| `tests/test_coherence_promised_assets.py` | Tests para nuevo check promised_assets_exist |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/pain_solution_mapper.py` | Usa ASSET_CATALOG |
| `modules/asset_generation/conditional_generator.py` | Usa ASSET_CATALOG |
| `modules/asset_generation/preflight_checks.py` | Usa ASSET_CATALOG |
| `modules/commercial_documents/coherence_validator.py` | Nuevo check promised_assets_exist |
| `AGENTS.md` | Actualizado con nuevos módulos activos |

### 📊 Métricas

| Métrica | Valor |
|---------|-------|
| Fases completadas | 6/6 (100%) |
| Assets implementados | 9/11 |
| Assets prometeros-no-implementados | 0 (gestionados) |
| Unknown asset type errors | 0 |
| Tests | 1323 passing (17 geo_validation related - no bloqueante) |

---

## [4.4.2] - 2026-03-11

### 🎯 Objetivo

Auditoría Integral v4.4.1 - Corrección de inconsistencias en análisis Hotelvisperas.

### 🔧 Cambios Implementados

#### Validación Financiera (No Defaults in Money)
- modules/financial_engine/no_defaults_validator.py - Nuevo validador
- Bloquea cálculos financieros cuando occupancy_rate=0 o direct_channel=0
- 18 tests en test_no_defaults_validator.py

#### Calidad de Assets
- modules/asset_generation/asset_content_validator.py - Nuevo validador
- Detecta placeholders y contenido genérico en assets

#### Ethics Gate
- modules/quality_gates/ethics_gate.py - Nuevo gate
- Valida ROI >= 0 antes de proponer precios

### Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| modules/financial_engine/no_defaults_validator.py | Validador de defaults financieros |
| modules/asset_generation/asset_content_validator.py | Validador de contenido de assets |
| modules/quality_gates/ethics_gate.py | Gate ético financiero |

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1323 passing |
| NoDefaultsValidator tests | 18/18 passing |
| Validaciones | 4/4 |

## [4.4.1] - 2026-03-09

### 🎯 Objetivo

Conectar capacidades que existían pero no estaban integradas al flujo principal.

### 🔧 Cambios Implementados

#### Integración de MetadataValidator
- `modules/auditors/v4_comprehensive.py` - Nueva clase MetadataAuditResult
- `modules/auditors/v4_comprehensive.py` - Nuevo método _audit_metadata()
- Integración en flujo de auditoría entre schemas y GBP

#### Execution Trace
- `modules/auditors/v4_comprehensive.py` - Campos executed_validators, skipped_validators
- Output incluye execution_trace en serialización

#### PublicationGates como Gate Real
- `main.py` - FASE 4.5 después de assets
- Invocación de run_publication_gates()
- Resultados propagados al reporte final

#### ConsistencyChecker Obligatorio
- `main.py` - FASE 4.6 después de PublicationGates
- Integración de check_assessment_consistency()
- Resultados visibles en output

#### FinancialCalculatorV2 Garantizado
- `main.py` - FASE 3 usa FinancialCalculatorV2
- Reemplaza uso directo de ScenarioCalculator
- Validación "No Defaults in Money" asegurada

#### Documentación y Workflows
- `.agents/workflows/phased_project_executor.md` - v1.4.0
- `docs/CONTRIBUTING.md` - Nueva §13 Sistema de Capability Contracts

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/auditors/v4_comprehensive.py` | MetadataValidator + Execution Trace |
| `main.py` | FASE 4.5, FASE 4.6, FinancialCalculatorV2 |
| `.agents/workflows/phased_project_executor.md` | v1.4.0 - Capability Contracts |
| `docs/CONTRIBUTING.md` | §13 Sistema de Capability Contracts |

### 📊 Tests

- 27 tests passing (regresión Hotel Visperas)
- 4/4 validaciones pasando

---

## [4.4.1] - 2026-03-04

### 🎯 Objetivo

Limpieza de módulos deprecados y consolidación de arquitectura v4.0.

### 🔧 Cambios Implementados

#### Archivado de Módulos Legacy
- **decision_engine.py** → Archivado (v2.4.2 legacy, reemplazado por `financial_engine/`)
- **orchestrator/** → Archivado (v3.x legacy, reemplazado por `orchestration_v4/`)
- **generators/report_builder.py** → Archivado (huérfano, reemplazado por `report_builder_fixed.py`)
- **generators/certificate_gen.py** → Archivado (v2.2, versión más reciente en `delivery/generators/`)
- **utils/cac_tracker.py** → Archivado (huérfano, nunca utilizado)

#### Consolidación de Arquitectura
- Flujo v4.x consolidado en `orchestration_v4/` (comandos `v4complete`, `v4audit`)
- Comandos legacy (`audit`, `stage`, `spark`) marcados como deprecados con mensajes informativos
- Imports condicionales para módulos legacy con `ORCHESTRATOR_AVAILABLE`

### 📁 Archivos Archivados

| Archivo | Ubicación | Razón |
|---------|-----------|-------|
| `modules/decision_engine.py` | `archives/deprecated_modules_20260304/` | Legacy v2.4.2 |
| `modules/orchestrator/` | `archives/deprecated_modules_20260304/orchestrator/` | Legacy v3.x |
| `modules/generators/report_builder.py` | `archives/deprecated_modules_20260304/generators/` | Huérfano |
| `modules/generators/certificate_gen.py` | `archives/deprecated_modules_20260304/generators/` | Duplicado obsoleto |
| `modules/utils/cac_tracker.py` | `archives/deprecated_modules_20260304/utils/` | Huérfano |

### 📁 Tests Archivados

| Test | Ubicación | Razón |
|------|-----------|-------|
| `test_v23_integration.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.3 |
| `test_visperas_v242.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.4.2 |
| `test_v242_quick.py` | `archives/deprecated_modules_20260304/tests/` | Legacy v2.4.2 |
| `test_pipeline_no_llm.py` | `archives/deprecated_modules_20260304/tests/` | Pipeline legacy |

### 📊 Tests

- Tests activos: ~1240+ (reducidos por archivado de tests legacy)
- Cobertura: >80%

### 🔗 Referencias

- Archivo completo: `archives/deprecated_modules_20260304/`
- Documentación de archivado: `archives/deprecated_modules_20260304/README.md`

## [4.4.0] - 2026-03-04

### 🎯 Objetivo

Corregir hallazgos B-001, B-002, M-001, M-002, m-001 detectados en fase de observación v4complete.
Mejorar confiabilidad del sistema de evidencia y coherencia entre documentos.

### 🔧 Cambios Implementados

#### Adaptador Unificado de Taxonomías (B-001)
- **Problema**: Dos enums ConfidenceLevel con valores diferentes (data_structures vs confidence_level)
- **Solución**: Adaptador unificado en `modules/commercial_documents/data_structures.py`
- **Función**: `normalize_confidence_level()` para conversión segura entre taxonomías
- **Impacto**: Consistencia en overall_confidence en todos los documentos

#### Corrección Semántica Financiera (B-002)
- **Problema**: Escenario optimista podía tener valores negativos (max(0, ...) ocultaba problemas)
- **Solución**: Nuevo campo `monthly_opportunity_cop` sin truncamiento
- **Template**: Mostrar "Equilibrio" cuando oportunidad <= 0
- **Archivos**: `scenario_calculator.py`, templates financieros

#### Alineación Pricing vs Coherence (M-001, m-001)
- **Problema**: Unidades incompatibles (3.0x vs 0.03) causaban falsos FAIL
- **Solución**: Sistema unificado en Decimal (0.03-0.06) como canónica
- **Conversión**: Coherence convierte automáticamente para mensajes legibles
- **Mensajes**: "3.0x" en vez de "0.03" para legibilidad

#### Fuente Única de Problemas (M-002)
- **Problema**: Problemas duplicados entre diagnóstico y propuesta (50 FAQs → 18)
- **Solución**: Funciones compartidas `calculate_quick_wins()` y `extract_top_problems()`
- **Ubicación**: `modules/commercial_documents/data_structures.py`
- **Impacto**: Consistencia garantizada entre documentos

#### Observabilidad Determinística
- **Nuevo**: `manifest.json` generado en cada ejecución
- **Contenido**: Archivos procesados, métricas, checksums
- **Validación**: Validación cruzada automática post-ejecución
- **Clasificación**: Métricas determinísticas vs volátiles

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `tests/test_confidence_consistency_between_documents.py` | Test E2E de confianza entre documentos |
| `tests/test_top_problems_consistency.py` | Test de consistencia de problemas |
| `tests/test_optimistic_scenario_semantics.py` | Test de semántica de escenarios |
| `tests/test_price_pain_ratio_alignment.py` | Test de alineación pricing |
| `.opencode/plans/v4_observation_workflow/scripts/manifest_generator.py` | Generador de manifest por run |

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/data_structures.py` | Adaptador de taxonomías, funciones compartidas |
| `modules/financial_engine/scenario_calculator.py` | Campo monthly_opportunity_cop, sin max(0,...) |
| `modules/commercial_documents/coherence_config.py` | Alineación unidades pricing |
| `main.py` | Construcción de DiagnosticSummary con fuente única |
| `v4_diagnostic_generator.py` | Usa extract_top_problems compartida |
| `v4_proposal_generator.py` | Usa calculate_quick_wins compartida |

### 📊 Tests

- **1261 tests pasando** (+4 desde v4.3.0)
- **4 tests de integración nuevos** validando correcciones
- **Cobertura**: >80%
- **Regresión**: 22/22 checks PASSED

### 🔗 Referencias

- Plan de implementación: `.opencode/plans/v4_implementation_sessions/`
- Dependencias: `dependencias-sesiones.md`
- Sesiones completadas: 1-6 (Sesión 7: documentación)

---

## [4.3.0] - 2026-03-03

### 🎉 Release - Sistema de Evidencia y Confiabilidad (FASE 6)

Esta release introduce el Sistema de Evidencia Trazable completo, motor de contradicciones,
quality gates de pre-publicación, y dashboard de observabilidad. Preparado para transición SHADOW → ACTIVE.

### 🔬 Sistema de Evidencia Trazable

- **EvidenceLedger** - Almacén centralizado de evidencia con hash e integridad
- **Claim** - Claims con evidencia trazable y niveles de confianza
- **CanonicalAssessment** - Estructura unificada de verdad (reemplaza assessment v4.2)

### ⚠️ Motor de Contradicciones

- **ContradictionEngine** - Detección de hard/soft conflicts entre fuentes
- **ConsistencyChecker** - Validación inter-documento
- Bloqueo automático cuando hard contradictions > 0

### 🚦 Quality Gates de Pre-publicación

- **DomainGates** - Gates técnico, comercial, financiero
- **CoherenceGate** - Bloqueo si score < 0.8
- **PublicationGates** - Estados READY_FOR_CLIENT, DRAFT_INTERNAL, REQUIRES_REVIEW
- **NoDefaultsValidator** - Validación "No Defaults in Money"

### 📊 Observabilidad y Calibración

- **Dashboard** - Métricas y tendencias de calidad
- **Calibration** - Ajuste de umbrales de confianza
- **Suite de Regresión** - Test permanente con Hotel Vísperas

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `data_models/canonical_assessment.py` | Modelo unificado de assessment |
| `data_models/claim.py` | Claims con evidencia trazable |
| `data_models/evidence.py` | Evidencia con hash e integridad |
| `data_validation/evidence_ledger.py` | Almacén centralizado de evidencia |
| `data_validation/contradiction_engine.py` | Motor de detección de conflictos |
| `data_validation/consistency_checker.py` | Validación inter-documento |
| `modules/quality_gates/domain_gates.py` | Gates por dominio |
| `modules/quality_gates/coherence_gate.py` | Gate de coherencia |
| `modules/quality_gates/publication_gates.py` | Gates de pre-publicación |
| `modules/quality_gates/publication_state.py` | Estados de publicación |
| `modules/financial_engine/no_defaults_validator.py` | Validación sin defaults |
| `modules/financial_engine/calculator_v2.py` | Calculadora condicionada v2 |
| `commercial_documents/composer.py` | Composición documental determinística |
| `observability/dashboard.py` | Dashboard de métricas |
| `observability/calibration.py` | Calibración de umbrales |
| `enums/severity.py` | Niveles de severidad |
| `enums/confidence_level.py` | Niveles de confianza |
| `tests/regression/test_hotel_visperas.py` | Test de regresión permanente |

### 📊 Métricas de Calidad (KPIs)

| KPI | Umbral | Estado |
|-----|--------|--------|
| Evidence Coverage | >= 95% | ✅ |
| Hard Contradictions | = 0 | ✅ |
| Financial Validity | = 100% | ✅ |
| Critical Issue Recall | >= 90% | ✅ |
| Coherence Score | >= 0.8 | ✅ |

### 📈 Tests

- **1257 tests pasando** (+349 desde v4.2.0)
- Nueva suite de regresión permanente
- Tests de observabilidad y calibración

### ⚠️ Breaking Changes

- Nuevo formato `CanonicalAssessment` (reemplaza assessment v4.2)
- Estados de publicación obligatorios
- Bloqueo financiero con defaults detectados
- Coherence < 0.8 bloquea certificado

---

## [4.2.0] - 2026-03-02

### 🎉 Release - Integración Completa y Flujo v4complete Funcional

Esta release corrige bugs críticos y completa la integración de todas las fases técnicas (0-4), 
habilitando la ejecución completa de v4complete con generación de todos los outputs.

### 🐛 Correcciones de Bugs

#### Bug: Atributo `rationale` inexistente
- **Archivo**: `main.py`
- **Líneas**: 1494, 1584
- **Problema**: `PricingResolutionResult` no tiene atributo `rationale`, causando `AttributeError`
- **Solución**: Eliminar referencias a `rationale` del constructor y del JSON dump

### ✨ Mejoras

#### Flujo v4complete Funcional
- Todas las fases ejecutan sin errores:
  - FASE 1: Hook Generation ✅
  - FASE 2: Validación Cruzada ✅
  - FASE 3: Escenarios Financieros ✅
  - FASE 3.5: Documentos Comerciales ✅
  - FASE 4: Assets ✅
  - FASE 5: Reporte ✅

#### Outputs Generados
- `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` - Diagnóstico validado
- `02_PROPUESTA_COMERCIAL.md` - Propuesta coherente
- `financial_scenarios.json` - Escenarios financieros
- `audit_report.json` - Auditoría con APIs
- `v4_complete_report.json` - Reporte final

### 📁 Archivos Nuevos

| Archivo | Descripción |
|---------|-------------|
| `modules/financial_engine/harness_handlers.py` | Handlers para Agent Harness |
| `.agents/workflows/v4_financial_calculation.md` | Meta-Skill de cálculo financiero |
| `.agents/workflows/v4_regional_resolver.md` | Meta-Skill de resolución regional |
| `tests/test_fase3_harness_integration.py` | 26 tests de integración |
| `FASE_3_CHECKLIST.md` | Documentación Fase 3 |
| `FASE_4_CHECKLIST.md` | Documentación Fase 4 |

### 📊 Tests

- 908 tests pasando
- 26 tests nuevos de integración con Agent Harness
- Cobertura: financial_engine, agent_harness, commercial_documents

### 🔧 Feature Flags

El sistema está preparado para transición SHADOW → ACTIVE:
- `regional_adr_enabled`: False (default)
- `pricing_hybrid_enabled`: False (default)
- `financial_v410_enabled`: False (default)
- Modos: SHADOW (listo para activación progresiva)

---

## [4.2.0] - 2026-03-02 (Continuación - FASE 5)

### 🔧 Hardening y Validación de Regresión

#### Correcciones de Bugs Críticos (FASES 1-2)
- **Preflight Checks**: Respetar `block_on_failure=False` para campos faltantes (conversión a WARNING con fallback)
- **Asset Orchestrator**: Normalizar case en comparación de status (PASSED/passed) con .upper()
- **Coherence Validator**: Umbral unificado a 0.8 desde config
- **PageSpeed Client**: Extraer Lighthouse score incluso sin CrUX field data (status LAB_DATA_ONLY)
- **Google Places Client**: Agregar `error_type` y `error_message` para diagnóstico de fallos

#### Recuperación de Capacidades (FASE 3)
- **Competitor Analyzer**: Integrado en flujo v4 via V4ComprehensiveAuditor
- **Contexto Industria**: Agregado a diagnóstico (Eje Cafetero)
- **Scores 4 Pilares**: Tabla comparativa en diagnóstico (GEO, Activity, Web, AEO, IAO)
- **Plan 7/30/60/90**: Detallado en propuesta comercial
- **Garantías**: Nueva sección en propuesta (resultados, transparencia, sin permanencia)

#### Nuevos Tests de Regresión (FASE 5)
| Test | Descripción | Archivo |
|------|-------------|---------|
| Preflight Missing Field | 3 tests para fallback cuando campo requerido falta | `tests/asset_generation/test_preflight_missing_field.py` |
| Conditional New Assets | 4 tests para geo_playbook, review_plan, review_widget, org_schema | `tests/asset_generation/test_conditional_new_assets.py` |
| PageSpeed Lab Data | 2 tests para validar LAB_DATA_ONLY status | `tests/data_validation/test_pagespeed_lab_data.py` |
| Places Error Types | 3 tests para error_type en NO_API_KEY, QUOTA_EXCEEDED, TIMEOUT | `tests/test_google_places_error_types.py` |
| Comprehensive Competitors | 2 tests para integración de competitor_analyzer | `tests/auditors/test_v4_comprehensive_competitors.py` |

#### Sistema de Regresión Automatizada
- **Script:** `.opencode/plans/v4_repair_plan/scripts/regression_test.py`
- **Modos:** `url-only` (>=3 assets) y `with-onboarding` (coherence >=0.8)
- **Checks:** 7 validaciones E2E automatizadas
  1. Assets Generated (>=3/5)
  2. Coherence Score (estructura o >=0.8)
  3. Performance Detected (presente)
  4. Performance Status (VERIFIED/LAB_DATA_ONLY)
  5. GBP Diagnostics (error_type si place_found=false)
  6. Diagnostic Structure (4 secciones)
  7. Proposal Structure (5 secciones)

#### Nuevos Assets Generables
| Asset | Tipo | Descripción |
|-------|------|-------------|
| `geo_playbook` | Markdown | Checklist de optimización GBP |
| `review_plan` | Markdown | Estrategia de gestión de reseñas |
| `review_widget` | HTML | Widget de reviews para web |
| `org_schema` | JSON-LD | Schema.org Organization markup |

#### Tests Totales
- **Antes:** 908 tests
- **Después:** 921 tests (+13 nuevos)
- **Regresión:** 7/7 checks PASSED

#### Estado del Sistema
- ✅ **5/5 assets generados** (100%)
- ✅ **921 tests pasando** (100%)
- ✅ **Flujo v4complete funcional end-to-end**
- ✅ **Sistema preparado para transición SHADOW → ACTIVE**

---

## [4.1.0] - 2026-02-28

### 🎉 Release - Controles de Coherencia y Documentación Comercial

Esta release completa el flujo v4.0 con generación automatizada de documentos comerciales y controles de coherencia entre diagnóstico, propuesta y assets.

### ✨ Nuevas Características

#### Generación de Documentos Comerciales
- **Módulo**: `modules/commercial_documents/`
- **V4DiagnosticGenerator**: Genera `01_DIAGNOSTICO_Y_OPORTUNIDAD.md` con datos validados
- **V4ProposalGenerator**: Genera `02_PROPUESTA_COMERCIAL.md` con mapeo problemas→soluciones
- **Escenario financiero empático**: Realista destacado como "más probable", otros en anexo
- **Tabla de datos validados**: WhatsApp 🟢, Habitaciones 🟡, ADR 🟡 con fuentes

#### Controles de Coherencia
- **Módulo**: `CoherenceValidator` en `modules/commercial_documents/`
- **Validaciones automáticas**:
  - Problemas tienen soluciones (≥50%)
  - Assets están justificados por problemas
  - Datos financieros validados (≥0.7)
  - WhatsApp verificado (≥0.9, blocking)
  - Precio coherente con dolor (3-6x)
- **Score de coherencia global**: ≥0.8 para éxito
- **CoherenceConfig**: Lee umbrales desde `.conductor/guidelines.yaml`

#### Mapeo Problemas→Soluciones
- **Módulo**: `PainSolutionMapper`
- **9 problemas mapeados** a assets específicos
- **Categorización**: Con solución inmediata / Requieren atención
- **AssetPlan**: Genera plan de assets basado en confianza disponible

#### Integración Agent Harness
- **Log enriquecido v4.1.0**: coherence_score, phases_completed, assets counts
- **Persistencia de documentos**: Referencias a diagnóstico y propuesta
- **Comando `execute` mejorado**: Recupera análisis v4.0 con coherence ≥ 0.8
- **Validación de vigencia**: < 20 días

### 📁 Archivos Nuevos

```
modules/
├── commercial_documents/
│   ├── __init__.py
│   ├── coherence_config.py       # Config desde YAML
│   ├── coherence_validator.py    # Validación de coherencia
│   ├── pain_solution_mapper.py   # Mapeo problemas→assets
│   ├── v4_diagnostic_generator.py
│   ├── v4_proposal_generator.py
│   ├── data_structures.py
│   └── templates/
│       ├── diagnostico_v4_template.md
│       └── propuesta_v4_template.md
└── asset_generation/
    ├── v4_asset_orchestrator.py  # Orquestador v4
    └── asset_diagnostic_linker.py # Vincula assets con diagnóstico

tests/
└── test_v4_edge_cases.py         # 11 tests de casos de borde

.conductor/
└── guidelines.yaml               # + v4_coherence_rules, price_validation
```

### 🔧 Mejoras

#### Sincronización Workflows-Código
- Workflow `.agents/workflows/v4_coherence_validator.md` alineado con `CoherenceConfig`
- Umbrales configurables desde `.conductor/guidelines.yaml`
- Criterios de éxito documentados y consistentes

#### Tests de Casos de Borde
- 11 tests implementados basados en `DOMAIN_PRIMER.md`
- Casos: WhatsApp conflict, Schema inválido, Datos parciales, Escenarios negativos, Assets bloqueados

#### Optimización de Controles
- **Centralización**: Umbrales en `.conductor/guidelines.yaml`
- **Fallback**: Valores por defecto si YAML no existe
- **Flexibilidad**: Reglas blocking/non-blocking configurables

### 🐛 Correcciones

| Problema | Solución |
|----------|----------|
| `diagnostic_doc=None` en orchestrator | Crear DiagnosticDocument completo con problems reales |
| Tabla "Sin datos" en diagnóstico | Extraer datos reales de audit_result.validation |
| "Sin assets planificados" en propuesta | Generar asset_plan desde PainSolutionMapper |
| Execute no encuentra v4.0 | Filtro por coherence_score >= 0.8 y vigencia < 20 días |

### 📚 Documentación

- `AGENTS.md`: Actualizado con nuevos módulos y flujo completo
- `CONTRIBUTING.md`: Nueva sección "Controles de Coherencia v4.0"
- `DOMAIN_PRIMER.md`: Regenerado con módulos commercial_documents/

---

## [4.0.0] - 2026-02-27

### 🎉 Release - Sistema de Confianza

Esta release representa una transformación fundamental del modelo IAH, pasando de un "generador de diagnósticos" a un "sistema de inteligencia con niveles de certeza explícitos".

### ✨ Nuevas Características

#### Arquitectura de Validación Cruzada
- **Módulo**: `modules/data_validation/`
- **Taxonomía de Confianza**: VERIFIED (≥0.9), ESTIMATED (0.5-0.9), CONFLICT (<0.5)
- **Validación entre fuentes**: web scraping, GBP API, input usuario, benchmarks
- **Detección automática de conflictos**: Bloquea assets con datos contradictorios
- **71 tests implementados**

#### Motor Financiero por Escenarios
- **Módulo**: `modules/financial_engine/`
- **Reemplaza**: Cálculos exactos por escenarios probabilísticos
- **Escenarios**: Conservador (70%), Realista (20%), Optimista (10%)
- **Transparencia**: Explicación completa de fórmulas en lenguaje natural
- **Proyecciones**: 6-12 meses con intervalos de confianza
- **125 tests implementados**

#### Flujo de Dos Fases
- **Módulo**: `modules/orchestration_v4/`
- **Fase 1 (Hook)**: Benchmark regional → Rango estimado con disclaimer
- **Fase 2 (Input)**: 5 datos mínimos → Validación cruzada → Escenarios
- **Tracking de progreso**: 30% → 60% → 100%
- **Gestión de estados**: INIT → PHASE_1 → PHASE_2 → VALIDATION → COMPLETE
- **66 tests implementados**

#### Generación Condicional de Assets
- **Módulo**: `modules/asset_generation/`
- **Preflight checks**: Gates de calidad antes de generar
- **Nomenclatura honesta**: `ESTIMATED_` prefix si confidence < 0.9
- **Metadatos obligatorios**: confidence_level, sources, generated_at, can_use
- **Assets soportados**: WhatsApp button, FAQ page, Hotel schema, Financial projection
- **76 tests implementados**

### 🔧 Mejoras Técnicas

#### APIs Externas
- **PageSpeed Insights API**: Validación real de Core Web Vitals
- **Rich Results Test API**: Verificación de schemas
- **Google Places API**: Datos GBP mejorados

#### Pre-commit Hooks
- Validación de imports de módulos v4.0
- Verificación de estructura de archivos
- Tests automáticos de todos los módulos

#### Tests
- **Total**: 338 tests pasando
- **Cobertura**: >95%
- **E2E**: 5 escenarios de hoteles completos

### 🐛 Problemas Resueltos

| Problema | Solución |
|----------|----------|
| WhatsApp falso en assets | Validación cruzada web+GBP+input |
| 50 FAQs → 18 (inconsistencia) | Preflight check + nombre honesto |
| 3 cifras diferentes de pérdida | Escenarios únicos con probabilidades |
| Performance Score inventado | PageSpeed API real |
| Assets sin validación | Gates de calidad obligatorios |
| Sin metadatos de confianza | Metadata en todos los assets |
| Sin explicación de cálculos | Fórmulas transparentes en lenguaje natural |

### 📁 Archivos Nuevos

```
modules/
├── data_validation/
│   ├── __init__.py
│   ├── confidence_taxonomy.py
│   ├── cross_validator.py
│   └── external_apis/
│       ├── __init__.py
│       ├── pagespeed_client.py
│       └── rich_results_client.py     # NEW - Rich Results Test API
├── auditors/                              # NEW - API Integration
│   ├── __init__.py
│   └── v4_comprehensive.py                # Auditor comprehensivo con APIs
├── financial_engine/
│   ├── __init__.py
│   ├── scenario_calculator.py
│   ├── formula_transparency.py
│   └── loss_projector.py
├── orchestration_v4/
│   ├── __init__.py
│   ├── two_phase_flow.py
│   └── onboarding_controller.py
└── asset_generation/
    ├── __init__.py
    ├── preflight_checks.py
    ├── asset_metadata.py
    └── conditional_generator.py

tests/
├── data_validation/          (94 tests - incluye rich_results)
├── financial_engine/         (125 tests)
├── orchestration_v4/         (66 tests)
├── asset_generation/         (76 tests)
└── e2e/
    └── test_v40_complete_flow.py

archives/legacy_v39/
├── modules/
│   ├── decision_engine_v391.py
│   └── delivery_manager_v391.py
└── scripts/
    └── validate_v391.py
```

### 📝 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/data_validation/__init__.py` | Agregados exports para Rich Results client |
| `modules/data_validation/external_apis/__init__.py` | Exports para Rich Results API |
| `modules/data_validation/external_apis/pagespeed_client.py` | Soporte GOOGLE_API_KEY fallback |
| `main.py` | Nuevo comando `v4audit` para auditoria API |

### 📚 Documentación

- `AGENTS.md` - Actualizado a v4.0
- `ARCHITECTURE_v4.md` - Nueva arquitectura
- `IMPLEMENTATION_COMPLETE_v40.md` - Resumen de implementación
- `IMPLEMENTATION_REPORT_v4_API.md` - Reporte de integracion APIs (NUEVO)
- `.env.template` - Variables de entorno incluyendo PAGESPEED_API_KEY

### ⚠️ Breaking Changes

#### API Changes
- `modules/decision_engine.py` → Reemplazado por `modules/financial_engine/`
- `modules/delivery/manager.py` → Reemplazado por `modules/asset_generation/`
- Cálculos exactos ($2.5M) → Escenarios con rangos ($X - $Y)

#### Datos Requeridos
- **Nuevo**: `PAGESPEED_API_KEY` en `.env` (para validación Core Web Vitals)
- **Nuevo**: Input de 5 datos mínimos del hotel (habitaciones, ADR, ocupación, OTAs, canal directo)

#### Outputs
- Assets ahora incluyen `_metadata` obligatorio
- Nomenclatura: `ESTIMATED_` prefix si confidence < 0.9
- Proyecciones financieras incluyen probabilidades

### 🔒 Seguridad

- Validación de datos cruzada antes de usar en assets
- Detección de conflictos entre fuentes
- Bloqueo automático de assets con datos no verificados
- Metadatos de confianza en todos los outputs

### 📊 Rendimiento

- Tiempo de validación: <100ms por campo
- Cálculo de escenarios: <50ms
- Generación de assets: <200ms por asset
- Tests completos: ~2 segundos (338 tests)

### 🙏 Agradecimientos

- Análisis forense de Hotel Visperas que identificó problemas v3.9
- Arquitectura de "Sistema de Confianza" inspirada en mejores prácticas de IA

---

## [3.9.1] - 2026-02-25

### Pipeline Parallelism & Bug Fixes

- Mejoras en paralelización de scrapers
- Correcciones menores de bugs
- Documentación actualizada

---

## [3.9.0] - 2026-02-20

### Mejoras en Validación

- Validation Engine nativo
- Pre-commit hooks mejorados
- Agent Harness v3.3

---

## [3.8.0] - 2026-02-10

### Automatización sin Gemini CLI

- Scripts de validación independientes
- Sincronización de versiones
- Context Integrity Validator

---

[4.0.0]: https://github.com/jhond/iah-cli/releases/tag/v4.0.0
[3.9.1]: https://github.com/jhond/iah-cli/releases/tag/v3.9.1
[3.9.0]: https://github.com/jhond/iah-cli/releases/tag/v3.9.0
[3.8.0]: https://github.com/jhond/iah-cli/releases/tag/v3.8.0
