# Changelog - IA Hoteles Agent

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [4.5.4] - 2026-03-16

### 🎯 Objetivo
Actualizar el v4_regression_guardian según el plan de actualización v4_regression_guardian

### ✅ Completado

**Mejoras en el v4_regression_guardian:**
- Añadido flag `--full` para validación completa
- Añadido flag `--quiet` para modo CI
- Añadido flag `--workdir` para directorio alternativo
- Añadido flag `--retry-failed` para re-ejecutar pasos fallidos
- Integración con agent_harness para registrar resultados
- Validación de capability contracts
- Mejorado manejo de encoding para evitar errores Unicode

### 📁 Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| .agents/workflows/v4_regression_guardian.py | Actualización completa con nuevas funcionalidades |

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
