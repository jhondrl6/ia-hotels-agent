# Guía Técnica IA Hoteles Agent CLI

**Última actualización:** 18 Marzo 2026  
**Versión:** 4.5.3+ (process)  
**Audiencia:** Desarrolladores, DevOps, Contribuidores

## 📋 Notas de Cambios v4.5.4 - Process Refinement

**Fecha:** 18 Marzo 2026

### Resumen

Implementar mejoras incrementales al agent_harness inspiradas en Superpowers sin adopción de framework externo.

### Nuevas Integraciones v4.5.4

#### 1. TDD Gate en Phased Project Executor

**Propósito**: Requerir test fallido antes de implementación para asegurar calidad.

**Ubicación**: `.agents/workflows/phased_project_executor.md`

**Implementación**: Agregado Step 0.5 TDD Gate

#### 2. Parallel Execution en Audit Guardian

**Propósito**: Ejecutar etapas geo/seo/ia en paralelo para mejorar rendimiento.

**Ubicación**: `.agents/workflows/audit_guardian.md`

**Implementación**: Modificado Steps 2-4 para ejecución paralela

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests | 1434+ passing |
| Coherence | ≥ 0.8 |


---

## 📋 Notas de Cambios v4.5.1 - GEO Integration Fixed

**Fecha:** 12 Marzo 2026

### Resumen

Corrección de desconexiones estructurales entre módulos GEO (AI Crawlers, Citability, IA-Readiness) y documentos comerciales (diagnóstico y propuesta).

### Nuevas Integraciones v4.5.1

#### 1. PainSolutionMapper GEO

**Propósito**: Detectar problemas relacionados con GEO y mapearlos a assets específicos.

**Ubicación**: `modules/commercial_documents/pain_solution_mapper.py`

**Problemas detectados**:
- `ai_crawler_blocked`: Cuando los crawlers de IA no pueden acceder al sitio
- `low_citability`: Cuando el contenido tiene baja probabilidad de ser citado por IA
- `low_ia_readiness`: Cuando el sitio muestra baja preparación para tecnologías IA

**Mapeo a assets**:
- `ai_crawler_blocked` → `llms_txt` (mejorar accesibilidad para crawlers IA)
- `low_citability` → `optimization_guide` (guía de optimización de contenido)
- `low_ia_readiness` → `hotel_schema` (mejorar estructura de datos para IA)

#### 2. V4DiagnosticGenerator GEO

**Propósito**: Incluir métricas GEO en el diagnóstico comercial.

**Ubicación**: `modules/commercial_documents/v4_diagnostic_generator.py`

**Sección agregada**: "Métricas de Optimización para IA"
- Score de AI Crawler (accesibilidad para crawlers de IA)
- Score de Citabilidad (probabilidad de ser citado por LLMs)
- Score de IA-Readiness (preparación general para tecnologías IA)

#### 3. V4ProposalGenerator GEO

**Propósito**: Incluir assets relacionados con GEO en la propuesta comercial.

**Ubicación**: `modules/commercial_documents/v4_proposal_generator.py`

**Assets GEO listados**:
- `llms.txt`: Estándar emergente para indexación IA
- `optimization_guide.md`: Guía para mejorar citabilidad en contenido
- `hotel_schema.json`: Schema.org Organization optimizado para IA

### Corrección de Assets

**Ubicación**: `modules/asset_generation/conditional_generator.py`

**Gates implementados**:
1. **Gate de contenido vacío**: Valida longitud mínima de 50 caracteres
2. **Gate de placeholders**: Detecta $$VAR$$, {{VAR}}, [[VAR]] sin reemplazar

**Assets corregidos**:
- `faq_page`: Ahora genera 3 FAQs específicas del hotel cuando no hay datos
- `org_schema`: Tiene campos poblados con fallback cuando falta información
- `performance_audit`: Muestra mensaje informativo cuando no hay datos de PageSpeed

---

## 📋 Notas de Cambios v4.5.0 - GEO Integration

**Fecha:** 11 Marzo 2026

### Resumen

Completar integración GEO (Generative Engine Optimization) con 4 nuevos módulos y mejoras en schema hotelero.

### Nuevos Módulos v4.5.0

#### 1. AI Crawler Auditor

**Propósito**: Verificar accesibilidad del sitio para crawlers de IA.

**Ubicación**: `modules/auditors/ai_crawler_auditor.py`

**Uso**:
```python
from modules.auditors.ai_crawler_auditor import AICrawlerAuditor

auditor = AICrawlerAuditor()
report = auditor.audit_robots_txt("https://hotel.com")

print(f"Score: {report.overall_score}")
for crawler in report.crawler_results:
    print(f"{crawler.crawler_name}: {'✅' if crawler.allowed else '❌'}")
```

**Crawlers soportados**: 14+ (GPTBot, ClaudeBot, Google-Extended, etc.)

**Nota**: Score de AI Crawler es ADVISORY y no afecta publication gates.

#### 2. llms.txt Generator

**Propósito**: Generar el estándar emergente para indexación IA.

**Ubicación**: `modules/asset_generation/llmstxt_generator.py`

**Uso**:
```python
from modules.asset_generation.llmstxt_generator import LLmstxtGenerator

generator = LLmstxtGenerator()
content = generator.generate(
    hotel_name="Hotel Example",
    url="https://hotel.com",
    metadata={...}
)

print(content)  # Contenido en formato llms.txt
```

**Integración**: Generado automáticamente en v4complete si confidence >= 0.7

#### 3. Citability Scorer

**Propósito**: Analizar contenido para citabilidad en LLMs.

**Ubicación**: `modules/auditors/citability_scorer.py`

**Uso**:
```python
from modules.auditors.citability_scorer import CitabilityScorer

scorer = CitabilityScorer()
score = scorer.score_content(html_content, url)

print(f"Citability: {score.overall_score}/100")
for rec in score.recommendations:
    print(f"- {rec}")
```

**Nota**: El score de citability es ADVISORY y no afecta publication gates.

#### 4. IA-Readiness Calculator

**Propósito**: Score compuesto de preparación general para IA.

**Ubicación**: `modules/auditors/ia_readiness_calculator.py`

**Uso**:
```python
from modules.auditors.ia_readiness_calculator import IAReadinessCalculator

calculator = IAReadinessCalculator()
score = calculator.calculate(readiness_data)

print(f"IA-Readiness: {score.overall_score}/100")
```

**Nota**: El score de IA-Readiness es ADVISORY y no afecta publication gates.

### Schema Hotel Enhanced

**Mejoras implementadas**:
- Reconocimiento de `LodgingBusiness` como hotel válido
- Campos hoteleros críticos: `geo`, `checkinTime`, `checkoutTime`, `sameAs`, `amenityFeature`
- Estructura `@graph` para múltiples schemas

**Archivos modificados**:
- `modules/data_validation/external_apis/rich_results_client.py`: Extensión para LodgingBusiness
- `modules/data_validation/schema_validator_v2.py`: Coverage scoring con campos hoteleros
- `modules/asset_generation/conditional_generator.py`: Unificación de schema generation

### Métricas

| Métrica | Valor |
|---------|-------|
| Tests totales | 1338 passing |
| Nuevos módulos | 4 |
| Validaciones | 4/4 |
| Métricas GEO | Advisory (no bloqueante) |

---

## 📋 Notas de Cambios v4.4.2 - Auditoría Integral

**Fecha:** 11 Marzo 2026

### Resumen

Auditoría Integral v4.4.1 - Corrección de inconsistencias en análisis Hotelvisperas.
Se implementaron 3 nuevos validadores/gates y se integraron en el flujo principal.

### Nuevos Validadores

#### 1. NoDefaultsValidator

**Propósito**: Bloquear cálculos financieros con valores por defecto.

**Ubicación**: 

**Campos validados**:
-  (no puede ser 0)
-  (no puede ser 0)
-  (no puede ser 0)

**Integración**: 
- Importado en 
- Ejecutado antes de calcular escenarios financieros
- Bloquea cálculo si detecta defaults

**Tests**: 18 tests en 

#### 2. AssetContentValidator

**Propósito**: Detectar placeholders y contenido genérico en assets generados.

**Ubicación**: 

**Métodos**:
-  - Detecta placeholders como {{placeholder}}
-  - Detecta campos vacíos
-  - Verifica contenido mínimo

**Integración**:
- Importado en 
- Ejecutado antes de marcar asset como generated

#### 3. EthicsGate

**Propósito**: Validar ética financiera antes de proponer precios.

**Ubicación**: 

**Checks**:
- ROI >= 0 (no proponer con pérdida)
- Pricing vs return válido
- Datos financieros no son defaults

**Integración**:
- Importado en 
- Agregado al pipeline de gates como BLOCKING
- Valida antes de generar propuesta comercial

### Métricas Post-Implementación

| Métrica | Valor |
|---------|-------|
| Tests totales | 1323 passing |
| NoDefaultsValidator | 18/18 passing |
| Validaciones | 4/4 |

---

## 📋 Notas de Cambios v4.4.1 - Catálogo Unificado de Assets

**Fecha:** 10 Marzo 2026

### Resumen

Versión de completación del catálogo unificado de assets (FASE-ASSET-06).
Resuelve problema de "Unknown asset type" y mejora gate de coherencia.

### Cambios Arquitectónicos

#### 1. Catálogo Centralizado de Assets (B-001)

**Problema**: 3 assets prometeros pero no implementados causaban "Unknown asset type".

**Solución**: Crear catálogo único en `asset_catalog.py`:

```python
from modules.asset_generation.asset_catalog import ASSET_CATALOG, is_asset_implemented

# Verificar si un asset está implementado
if is_asset_implemented("geo_playbook"):
    # Generar asset
```

**Componentes**:
- Enum `AssetStatus`: IMPLEMENTED, PROMISED_NOT_IMPLEMENTED, MISSING
- Dataclass `AssetCatalogEntry`: name, status, required_data, generator_function
- Dict `ASSET_CATALOG`: 11 entries (9 implemented, 2 promised-not-implemented)
- Función `is_asset_implemented()`: Check rápido de disponibilidad

#### 2. Gate de Coherencia Mejorado (B-002)

**Problema**: CoherenceValidator no validaba existencia de asset types.

**Solución**: Nuevo check `promised_assets_exist` con severidad blocking:

```python
def _check_promised_assets_exist(self, assessment: CanonicalAssessment) -> CoherenceCheck:
    """Valida que assets prometidos existen en el generador."""
    promised = assessment.promised_assets or []
    for asset in promised:
        if not is_asset_implemented(asset):
            return CoherenceCheck(
                name='promised_assets_exist',
                passed=False,
                score=0.0,
                message=f'Asset promesado no implementado: {asset}',
                severity='error'
            )
    return CoherenceCheck(...)
```

#### 3. Refactorización de Consumidores (B-003)

**Problema**: Listas duplicadas en 3 módulos causaban desincronización.

**Solución**: Los siguientes módulos ahora usan `ASSET_CATALOG`:

| Módulo | Antes | Después |
|--------|-------|---------|
| `pain_solution_mapper.py` | Lista hardcoded | `ASSET_CATALOG` |
| `conditional_generator.py` | Lista hardcoded | `ASSET_CATALOG` |
| `preflight_checks.py` | Lista hardcoded | `ASSET_CATALOG` |

### Breaking Changes

| Cambio | Impacto | Migración |
|--------|---------|-----------|
| Eliminación `GENERATION_STRATEGIES` | Backwards compatible | Via property |
| Eliminación `ASSET_REQUIREMENTS` | Backwards compatible | Via property |
| Nuevo campo en `AssetSpec` | Requiere import | Automático |

### Métricas

| Métrica | Valor |
|---------|-------|
| Fases completadas | 6/6 (100%) |
| Assets implementados | 9/11 |
| Assets prometeros-no-implementados | 0 |
| Unknown asset type errors | 0 |
| Tests | 1323 passing |

---

## 📋 Notas de Cambios v4.4.0 - Corrección de Inconsistencias Críticas

**Fecha:** 04 Marzo 2026

### Resumen

Versión de corrección de inconsistencias detectadas en fase de observación v4complete.
Resuelve hallazgos críticos B-001, B-002, M-001, M-002, m-001.

### Cambios Arquitectónicos

#### 1. Adaptador de Taxonomías de Confianza (B-001)

**Problema**: Dos enums `ConfidenceLevel` con valores diferentes causaban inconsistencias.

**Solución**: Adaptador unificado en `data_structures.py`:

```python
from modules.commercial_documents.data_structures import normalize_confidence_level

# Convierte entre taxonomías automáticamente
normalized = normalize_confidence_level(confidence_input)
```

**Impacto**: `overall_confidence` ahora es consistente en diagnóstico, propuesta y reportes.

#### 2. Semántica Financiera Corregida (B-002)

**Problema**: `max(0, ...)` ocultaba escenarios financieros negativos.

**Solución**: Campo `monthly_opportunity_cop` sin truncamiento:

```python
# Antes (incorrecto)
optimistic = max(0, calculated_value)  # Ocultaba problemas

# Después (correcto)
monthly_opportunity_cop = calculated_value  # Valor real
```

**Template**: Muestra "Equilibrio" cuando oportunidad <= 0.

#### 3. Alineación Pricing vs Coherence (M-001)

**Problema**: Unidades incompatibles (3.0x vs 0.03) causaban falsos FAIL.

**Solución**: Sistema Decimal canónico:

| Sistema | Valor | Uso |
|---------|-------|-----|
| Decimal (canónico) | 0.03 - 0.06 | Cálculos internos |
| Multiplicador (UI) | 3x - 6x | Mensajes al usuario |

```python
# Coherence convierte automáticamente
price_ratio = 0.03  # Decimal
message = f"{price_ratio * 100:.1f}x"  # "3.0x"
```

#### 4. Fuente Única de Problemas (M-002)

**Problema**: Problemas duplicados entre diagnóstico y propuesta.

**Solución**: Funciones compartidas en `data_structures.py`:

```python
from modules.commercial_documents.data_structures import (
    calculate_quick_wins,
    extract_top_problems
)

# Usado por diagnóstico y propuesta
problems = extract_top_problems(audit_result, max_problems=5)
quick_wins = calculate_quick_wins(problems)
```

### Nuevos Tests de Integración

| Test | Cobertura | Archivo |
|------|-----------|---------|
| Confidence Consistency | E2E entre documentos | `tests/test_confidence_consistency_between_documents.py` |
| Top Problems | Consistencia problemas | `tests/test_top_problems_consistency.py` |
| Optimistic Scenario | Semántica financiera | `tests/test_optimistic_scenario_semantics.py` |
| Price-Pain Ratio | Alineación unidades | `tests/test_price_pain_ratio_alignment.py` |

### Estadísticas Finales v4.4.0

- **Tests pasando:** 1261/1261 (100%)
- **Nuevos tests:** +4 de integración
- **Hallazgos corregidos:** 5/5 (100%)
- **Regresión:** 22/22 checks PASSED

---

## 📋 Notas de Cambios v4.3.0 - Sistema de Evidencia y Confiabilidad (FASE 6)

**Fecha:** 03 Marzo 2026

### Sistema de Evidencia Trazable

Implementación completa de sistema de evidencia con trazabilidad hash:

```python
from data_models import CanonicalAssessment, Claim, Evidence
from data_validation import EvidenceLedger

# Crear evidencia
ledger = EvidenceLedger()
evidence = ledger.add_evidence(
    claim="whatsapp_number",
    value="+573113973744",
    source="gbp_api",
    confidence=0.95
)
```

**Componentes principales:**

| Componente | Responsabilidad | Archivo |
|------------|-----------------|---------|
| EvidenceLedger | Almacén centralizado con hash | `data_validation/evidence_ledger.py` |
| ContradictionEngine | Detección hard/soft conflicts | `data_validation/contradiction_engine.py` |
| ConsistencyChecker | Validación inter-documento | `data_validation/consistency_checker.py` |
| CanonicalAssessment | Estructura unificada | `data_models/canonical_assessment.py` |

### Quality Gates de Pre-publicación

Nuevo sistema de gates para control de calidad antes de publicación:

```python
from modules.quality_gates import CoherenceGate, PublicationGate

# Gate de coherencia
gate = CoherenceGate(min_score=0.8)
result = gate.validate(assessment)

# Estados de publicación
if result.state == PublicationState.READY_FOR_CLIENT:
    publish(assessment)
```

| Gate | Umbral | Bloqueante |
|------|--------|------------|
| Technical Gate | confidence >= 0.9 | Sí |
| Commercial Gate | coherence >= 0.8 | Sí |
| Financial Gate | no_defaults = True | Sí |
| Publication Gate | state = READY_FOR_CLIENT | Sí |

### Observabilidad y Dashboard

Sistema de métricas y calibración de confianza:

```bash
# Ver métricas de calidad
python -c "from observability.dashboard import Dashboard; d = Dashboard(); d.show()"

# Calibrar umbrales
python -c "from observability.calibration import Calibration; c = Calibration(); c.adjust()"
```

**Métricas disponibles:**

| Métrica | Descripción | Target |
|---------|-------------|--------|
| Evidence Coverage | % claims con evidencia | >= 95% |
| Hard Contradictions | Conflictos irrecuperables | = 0 |
| Financial Validity | Sin defaults en dinero | = 100% |
| Critical Issue Recall | % problemas detectados | >= 90% |
| Coherence Score | Alineación documentos | >= 0.8 |

### Suite de Regresión Permanente

Test E2E permanente con caso Hotel Vísperas:

```bash
# Ejecutar regresión
python -m pytest tests/regression/test_hotel_visperas.py -v

# Validar métricas
python scripts/run_all_validations.py
```

### Nuevos Módulos v4.3.0

| Módulo | Tests | Archivo |
|--------|-------|---------|
| data_models | ~15 | `tests/test_data_models*.py` |
| quality_gates | ~12 | `tests/test_quality_gates*.py` |
| observability | ~8 | `tests/test_observability*.py` |

### Estadísticas Finales v4.3.0

- **Tests pasando:** 1257/1257 (100%)
- **Nuevos tests:** +349 desde v4.2.0
- **Coverage de evidencia:** >= 95%
- **Hard contradictions:** 0
- **Validaciones:** 4/4 PASSED

---

## 📋 Notas de Cambios v4.2.0 - Hardening y Regresión (FASE 5)

**Fecha:** 02 Marzo 2026

### Sistema de Regresión Automatizada

Implementación de test suite E2E para validación continua:

```bash
# Ejecutar regresión completa (modo url-only)
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode url-only

# Modo with-onboarding (requiere datos operativos)
python .opencode/plans/v4_repair_plan/scripts/regression_test.py \
    --new output/v4_complete/ \
    --mode with-onboarding
```

### Nuevos Tests Unitarios v4.2.0

| Suite | Tests | Cobertura | Archivo |
|-------|-------|-----------|---------|
| Preflight Missing Field | 3 | Fallback con block_on_failure=False | `tests/asset_generation/test_preflight_missing_field.py` |
| Conditional New Assets | 4 | geo_playbook, review_plan, review_widget, org_schema | `tests/asset_generation/test_conditional_new_assets.py` |
| PageSpeed Lab Data | 2 | Lighthouse sin CrUX field data | `tests/data_validation/test_pagespeed_lab_data.py` |
| Places Error Types | 3 | error_type en fallos (NO_API_KEY, QUOTA, TIMEOUT) | `tests/test_google_places_error_types.py` |
| Comprehensive Competitors | 2 | Integración competitor_analyzer en v4 | `tests/auditors/test_v4_comprehensive_competitors.py` |

### Correcciones Técnicas FASES 1-2

| Componente | Issue | Solución | Archivo |
|------------|-------|----------|---------|
| Preflight Checks | Ignoraba block_on_failure para campos faltantes | Conversión a WARNING con fallback | `modules/asset_generation/preflight_checks.py` |
| Asset Orchestrator | Comparación case-sensitive PASSED/passed | Normalización con .upper() | `modules/asset_generation/v4_asset_orchestrator.py` |
| Coherence Validator | Umbral hardcodeado 0.6 | Leer desde config (0.8) | `modules/commercial_documents/coherence_validator.py` |
| PageSpeed Client | Retornaba null sin CrUX | Extraer Lighthouse siempre, status LAB_DATA_ONLY | `modules/data_validation/external_apis/pagespeed_client.py` |
| Places Client | Sin diagnóstico de errores | Agregar error_type/error_message a PlaceData | `modules/scrapers/google_places_client.py` |
| GBPApiResult | Sin campo error_type | Agregar a dataclass | `modules/auditors/v4_comprehensive.py` |

### Recuperación de Capacidades FASE 3

| Capacidad | Implementación | Archivo |
|-----------|---------------|---------|
| Competitor Analyzer | Integrado en V4ComprehensiveAuditor | `modules/auditors/v4_comprehensive.py` |
| Contexto Industria | Sección en diagnóstico (Eje Cafetero) | `modules/commercial_documents/v4_diagnostic_generator.py` |
| Scores 4 Pilares | Tabla comparativa (GEO, Activity, Web, AEO, IAO) | `modules/commercial_documents/v4_diagnostic_generator.py` |
| Plan 7/30/60/90 | Detallado por días/rangos | `modules/commercial_documents/v4_proposal_generator.py` |
| Garantías | Nueva sección en propuesta | `modules/commercial_documents/v4_proposal_generator.py` |

### Nuevos Assets Condicionales

| Asset | Descripción | Confianza Mínima | Fallback |
|-------|-------------|------------------|----------|
| `geo_playbook` | Checklist optimización GBP | 0.6 | Sí |
| `review_plan` | Estrategia gestión reseñas | 0.6 | Sí |
| `review_widget` | Widget HTML reviews | 0.6 | Sí |
| `org_schema` | Schema.org Organization | 0.7 | Sí |

### Estadísticas Finales v4.2.0

- **Assets generados:** 5/5 (100%) - modo url-only
- **Tests pasando:** 921/921 (100%)
- **Regresión:** 7/7 checks PASSED
- **Coherence:** 0.56 (aceptado en modo url-only, requiere >=0.8 en with-onboarding)
- **Tiempo de ejecución v4complete:** ~3-5 minutos

---

## 📋 Notas de Cambios v4.2.0 - Integración Completa

**Fecha:** 02 Marzo 2026

### Objetivo

Completar la integración de todas las fases técnicas (0-4) y habilitar flujo v4complete 
funcional end-to-end con generación de todos los outputs.

### Correcciones Críticas

| Bug | Ubicación | Solución |
|-----|-----------|----------|
| Atributo `rationale` inexistente | `main.py:1494,1584` | Eliminadas referencias a atributo no existente en `PricingResolutionResult` |

### Nuevas Capacidades v4.2.0

| Aspecto | v4.1.0 | v4.2.0 |
|---------|--------|--------|
| **Flujo v4complete** | Parcial (errores) | Completo (6 fases) |
| **Agent Harness** | Logs enriquecidos | Delegación condicional vía handlers |
| **Meta-Skills** | No implementado | 2 workflows activos |
| **Tests** | 704 passing | 908 passing |

### Nuevos Componentes v4.2.0

| Componente | Tipo | Responsabilidad |
|------------|------|-----------------|
| `financial_engine/harness_handlers.py` | Módulo | Handlers para Agent Harness |
| `.agents/workflows/v4_financial_calculation.md` | Meta-Skill | Cálculo financiero vía Harness |
| `.agents/workflows/v4_regional_resolver.md` | Meta-Skill | Resolución regional ADR |
| `tests/test_fase3_harness_integration.py` | Tests | 26 tests de integración |

### Feature Flags para Transición

El sistema está preparado para transición SHADOW → ACTIVE:

```bash
# Defaults conservadores (seguridad)
FINANCIAL_REGIONAL_ADR_ENABLED=false
FINANCIAL_PRICING_HYBRID_ENABLED=false
FINANCIAL_V410_ENABLED=false

# Para activar nuevas features
export FINANCIAL_REGIONAL_ADR_ENABLED=true
export FINANCIAL_PRICING_HYBRID_ENABLED=true
export FINANCIAL_V410_ENABLED=true
export FINANCIAL_REGIONAL_ADR_MODE=canary  # o active
export FINANCIAL_PRICING_HYBRID_MODE=canary  # o active
```

### Flujo v4complete Completo

```bash
python main.py v4complete --url https://hotel.com --nombre "Hotel"
# Output:
#   - audit_report.json
#   - financial_scenarios.json
#   - 01_DIAGNOSTICO_Y_OPORTUNIDAD.md
#   - 02_PROPUESTA_COMERCIAL.md (si coherence >= 0.8)
#   - delivery_assets/ (condicional a confianza)
#   - v4_complete_report.json
```

---

## 📋 Notas de Cambios v4.1.0 - Controles de Coherencia

**Fecha:** 28 Febrero 2026

### Completando el Flujo Comercial

La versión 4.1.0 complementa la arquitectura v4.0 con generación automatizada de documentos comerciales y controles de coherencia que aseguran alineación entre diagnóstico, propuesta y assets entregables.

### Nuevas Capacidades v4.1.0

| Aspecto | v4.0 | v4.1.0 |
|---------|------|--------|
| **Documentos comerciales** | JSON técnico | Diagnóstico + Propuesta en Markdown |
| **Coherencia** | Implícita | Validación automática diagnosis↔propuesta↔assets |
| **Mapeo problemas→soluciones** | Manual | Automático con `PainSolutionMapper` |
| **Umbrales de validación** | Hardcodeados | Configurables desde `.conductor/guidelines.yaml` |
| **Agent Harness** | Logs básicos | Logs enriquecidos con `coherence_score` |
| **Comando `execute`** | Busca cualquier análisis | Recupera solo análisis v4.0 con coherence ≥ 0.8 |

### Nuevos Módulos v4.1.0

| Módulo | Responsabilidad |
|--------|-----------------|
| `commercial_documents/` | Generación de diagnóstico y propuesta comercial v4.1.0 |
| `coherence_validator/` | Validación de alineación entre documentos y assets |
| `pain_solution_mapper/` | Mapeo automático de problemas detectados a assets |

### Checks de Coherencia Implementados

| Check | Umbral | Blocking | Descripción |
|-------|--------|----------|-------------|
| `problems_have_solutions` | ≥ 50% | ✅ Sí | Cada problema tiene al menos un asset |
| `assets_are_justified` | ≥ 80% | ❌ No | Cada asset está justificado por un problema |
| `financial_data_validated` | ≥ 0.7 | ❌ No | Datos financieros tienen confianza suficiente |
| `whatsapp_verified` | ≥ 0.9 | ✅ Sí | WhatsApp validado cruzando 2+ fuentes |
| `price_matches_pain` | 3x-6x | ❌ No | Precio coherente con dolor financiero |
| `overall_coherence` | ≥ 0.8 | ❌ No | Score global de coherencia |

### Arquitectura v4.1.0 Completa

```
modules/
├── data_validation/          # v4.0 - Validación cruzada
├── financial_engine/         # v4.0 - Motor de escenarios
├── orchestration_v4/         # v4.0 - Flujo dos fases
├── asset_generation/         # v4.0 - Generación condicional
├── auditors/                 # v4.0 - APIs externas
└── commercial_documents/     # NEW v4.1.0 - Documentos + Coherencia
    ├── coherence_validator.py
    ├── coherence_config.py
    ├── pain_solution_mapper.py
    ├── v4_diagnostic_generator.py
    └── v4_proposal_generator.py
```

### Flujo Comercial Completo v4.1.0

```bash
# 1. Generar diagnóstico, propuesta y assets
python main.py v4complete --url https://hotelvisperas.com
# Output:
#   - 01_DIAGNOSTICO_Y_OPORTUNIDAD.md
#   - 02_PROPUESTA_COMERCIAL.md
#   - delivery_assets/
#   - v4_complete_report.json
#   - coherence_validation.json

# 2. Ejecutar implementación (usa análisis guardado)
python main.py execute --url https://hotelvisperas.com --package starter_geo
# Requiere: análisis v4.0 con coherence_score >= 0.8 y < 20 días
```

### Configuración Centralizada

Ubicación: `.conductor/guidelines.yaml`

```yaml
v4_coherence_rules:
  whatsapp_verified:
    confidence_threshold: 0.9
    blocking: true
  financial_data_validated:
    confidence_threshold: 0.7
    blocking: false
  # ... más reglas

price_validation:
  min_ratio: 3.0
  max_ratio: 6.0
  ideal_ratio: 4.5
```

---

## 📋 Notas de Cambios v4.0 - Controles de Coherencia

**Fecha:** 27 Febrero 2026

### Transformación Fundamental

La versión 4.0.0 transforma el modelo de "generador de diagnósticos" a "sistema de inteligencia con niveles de certeza explícitos". Este cambio aborda los problemas de confianza y precisión de versiones anteriores mediante validación cruzada, cálculo por escenarios y generación condicional.

### Antes (v3.9) vs Después (v4.0)

| Aspecto | v3.9 | v4.0 |
|---------|------|------|
| **Precisión financiera** | Cifra exacta ($2.5M) | Escenarios con rangos ($800k-$3.2M) |
| **Datos de entrada** | Benchmarks como input | Benchmarks como contexto |
| **Validación** | Ninguna | Validación cruzada obligatoria |
| **Confianza** | Implícita | Taxonomía VERIFIED/ESTIMATED/CONFLICT |
| **Assets** | Generación automática | Generación condicional con gates |
| **Metadata** | Ninguna | Metadata obligatoria en todos los assets |
| **Transparencia** | Baja | Explicación de fórmulas incluida |

### Nuevos Módulos v4.0

| Módulo | Responsabilidad |
|--------|-----------------|
| `data_validation/` | Validación cruzada de datos entre múltiples fuentes |
| `financial_engine/` | Cálculo financiero por escenarios con transparencia |
| `orchestration_v4/` | Flujo de dos fases: Hook → Input |
| `asset_generation/` | Generación condicional con preflight checks |

### Arquitectura v4.0

```
modules/
├── data_validation/          # NEW v4.0 - Validación cruzada
├── financial_engine/         # NEW v4.0 - Motor de escenarios
├── orchestration_v4/         # NEW v4.0 - Flujo dos fases
└── asset_generation/         # NEW v4.0 - Generación condicional
```

### Flujo de Trabajo (Dos Fases)

```
FASE 1: HOOK (Automático)
─────────────────────────
Input: URL del hotel
  ↓
Benchmark Regional → Rango Estimado ($X - $Y)
  ↓
Output: Hook con disclaimer de estimación
        "¿Quiere precisar esta cifra?"
        Progreso: 30%

FASE 2: INPUT (Usuario + Validación)
─────────────────────────────────────
Input: 5 datos mínimos del hotel
  - Habitaciones
  - Tarifa promedio real (ADR)
  - % Ocupación
  - Presencia en OTAs
  - % Canal Directo
  ↓
Validación Cruzada OBLIGATORIA:
  - WhatsApp: web vs GBP vs input
  - ADR: benchmark vs input
  - Datos operativos: input usuario
  ↓
¿Conflictos detectados?
  ├─ SÍ → Reporte detallado, revisión manual
  └─ NO → Escenarios financieros calculados
  ↓
Output: Proyecciones con intervalos
        Progreso: 100%
        Listo para assets: SÍ/NO
```

---

## 🔧 Módulo: data_validation/

**Responsabilidad:** Validar datos entre múltiples fuentes y asignar niveles de confianza.

### Taxonomía de Confianza

| Estado | Icono | Descripción | Confidence |
|--------|-------|-------------|------------|
| **VERIFIED** | 🟢 | 2+ fuentes coinciden | ≥ 0.9 |
| **ESTIMATED** | 🟡 | 1 fuente o benchmark | 0.5 - 0.9 |
| **CONFLICT** | 🔴 | Fuentes contradicen | < 0.5 |

### Validaciones Implementadas

| Validación | Fuentes | Uso |
|------------|---------|-----|
| `validate_whatsapp()` | Web scraping, GBP, Input usuario | Botón WhatsApp |
| `validate_adr()` | Benchmark, Input usuario | Cálculo financiero |
| `validate_rooms()` | Web, GBP, Input | Capacidad hotel |

### Uso

```python
from modules.data_validation import CrossValidator

cv = CrossValidator()
result = cv.validate_whatsapp(
    web_value="+573113973744",
    gbp_value="+573113973744"
)
# Resultado: VERIFIED (confidence=1.0)
```

---

## 🔧 Módulo: financial_engine/

**Responsabilidad:** Calcular escenarios financieros en lugar de cifras exactas.

### Escenarios

| Escenario | Probabilidad | Base de Cálculo |
|-----------|--------------|-----------------|
| Conservador | 70% | Peor caso plausible |
| Realista | 20% | Meta esperada |
| Optimista | 10% | Mejor caso |

### Fórmulas Transparentes

Todas las proyecciones incluyen la fórmula utilizada:

```
Oportunidad_Mensual = ADR × Habitaciones × 30 × Ocupación × 
                      (1 - Canal_Directo) × Factor_Captura
```

### Uso

```python
from modules.financial_engine import ScenarioCalculator, HotelFinancialData

hotel = HotelFinancialData(
    rooms=15,
    adr_cop=400000,
    occupancy_rate=0.51,
    direct_channel_percentage=0.30
)

calc = ScenarioCalculator()
scenarios = calc.calculate_scenarios(hotel)
# Hook range: $453,600 - $10,631,250 COP/mes
```

---

## 🔧 Módulo: orchestration_v4/

**Responsabilidad:** Gestionar el onboarding del hotel mediante flujo de dos fases.

### Estados del Pipeline

| Estado | Descripción | Progreso |
|--------|-------------|----------|
| `INIT` | Inicialización | 0% |
| `PHASE_1_HOOK` | Hook con estimación | 30% |
| `PHASE_2_INPUT` | Recolección de datos | 60% |
| `VALIDATION` | Validación cruzada | 75% |
| `CALCULATION` | Cálculo de escenarios | 90% |
| `COMPLETE` | Listo para assets | 100% |

### Uso

```python
from modules.orchestration_v4 import OnboardingController, HotelInputs

controller = OnboardingController()

# Fase 1: Hook
state = controller.start_onboarding(
    hotel_url="https://hotelvisperas.com",
    hotel_name="Hotel Visperas",
    region="eje_cafetero"
)

# Fase 2: Input + Validación
inputs = HotelInputs(
    rooms=15,
    adr_cop=400000,
    occupancy_rate=0.51,
    ota_presence=["booking", "expedia"],
    direct_channel_percentage=0.30,
    whatsapp_number="+573113973744"
)

state = controller.submit_phase_2(
    hotel_id=state.hotel_id,
    inputs=inputs,
    scraped_data=scraped,
    gbp_data=gbp
)
```

---

## 🔧 Módulo: asset_generation/

**Responsabilidad:** Generar assets solo si pasan gates de calidad.

### Preflight Checks

| Asset | Gate Mínimo | Status |
|-------|-------------|--------|
| WhatsApp Button | confidence ≥ 0.9 | PASSED |
| FAQ Page | confidence ≥ 0.7 | PASSED |
| Hotel Schema | confidence ≥ 0.8 | PASSED |

### Nomenclatura de Assets

| Resultado | Prefijo | Ejemplo |
|-----------|---------|---------|
| PASSED | Ninguno | `boton_whatsapp.html` |
| WARNING | ESTIMATED_ | `ESTIMATED_boton_whatsapp.html` |
| BLOCKED | No generar | N/A |

### Uso

```python
from modules.asset_generation import ConditionalGenerator

generator = ConditionalGenerator()
result = generator.generate(
    asset_type="whatsapp_button",
    validated_data=validated_fields,
    hotel_name="Hotel Visperas",
    hotel_id="hotel_visperas"
)

print(f"Asset: {result['filename']}")
print(f"Status: {result['preflight_status']}")
```

---

## 🔧 Módulo: auditors/

**Responsabilidad:** Realizar auditorías comprehensivas con validación de datos mediante APIs externas.

### APIs Integradas

| API | Propósito | Datos Obtenidos |
|-----|-----------|-----------------|
| **Rich Results Test API** | Validar schemas | Hotel, FAQPage, Organization |
| **Google Places API** | Datos GBP oficiales | Rating, reviews, fotos, geo_score |
| **PageSpeed API** | Core Web Vitals | LCP, FID, CLS, Performance Score |

### Arquitectura de Auditoría

```
V4ComprehensiveAuditor
├── Schema Audit (Rich Results API)
├── GBP Data (Places API)
├── Performance (PageSpeed API)
└── Cross-Validation (Multi-fuente)
```

### Taxonomía de Confianza

Todos los datos auditados reciben nivel de confianza:

| Nivel | Criterio | Uso en Assets |
|-------|----------|---------------|
| **VERIFIED** | 2+ fuentes coinciden | ✅ Sí |
| **ESTIMATED** | 1 fuente disponible | ⚠️ Con disclaimer |
| **CONFLICT** | Fuentes contradicen | ❌ No - revisión manual |

### CLI: Comando v4audit

```bash
# Auditoría básica
python main.py v4audit --url https://hotelvisperas.com

# Con nombre de hotel para mejor matching
python main.py v4audit --url https://example.com --nombre "Hotel Example"

# Modo debug
python main.py v4audit --url https://example.com --debug
```

### Uso Programático

```python
from modules.auditors import V4ComprehensiveAuditor

auditor = V4ComprehensiveAuditor()
result = auditor.audit("https://hotelvisperas.com")

# Acceder a resultados
print(f"Hotel: {result.hotel_name}")
print(f"Schema Confidence: {result.schema.hotel_confidence}")
print(f"GBP Geo Score: {result.gbp.geo_score}/100")
print(f"Overall Confidence: {result.overall_confidence}")

# Guardar reporte
auditor.save_report(result, Path("./output/report.json"))
```

### Reporte de Auditoría

El reporte incluye:
- **Schema**: Hotel y FAQ detectados, errores, warnings
- **GBP**: Datos de Places API (rating, reviews, fotos)
- **Performance**: Core Web Vitals (si hay datos de campo)
- **Cross-Validation**: WhatsApp, ADR validados entre fuentes
- **Recomendaciones**: Acciones específicas basadas en datos

---

## ⚠️ Breaking Changes v4.0

| Componente v3.9 | Componente v4.0 | Notas |
|-----------------|-----------------|-------|
| `decision_engine.py` | `financial_engine/` | **ARCHIVADO** - Lógica de paquetes → Escenarios financieros |
| `delivery/manager.py` | `asset_generation/` | Generación incondicional → Condicional con gates |
| Cifras exactas | Rangos de escenarios | Ej: $2.5M → $800k-$3.2M |
| `gap_analyzer.py` (legacy) | `gap_analyzer_v4.py` | Nuevo análisis con validación |

### Migración Recomendada

1. Módulo archivado en `archives/deprecated_modules_20260304/`
2. Reemplazar llamadas a `delivery/manager.py` por `asset_generation`
3. Adaptar consumidores de reportes para manejar rangos en lugar de valores únicos

---

## 🧪 Testing v4.0

### Estadísticas

| Métrica | Valor |
|---------|-------|
| **Tests Totales** | 704 passing |
| **Cobertura** | 87% |
| **E2E Hotels** | 5 hoteles piloto |

### Módulos de Test

| Módulo | Tests | Descripción |
|--------|-------|-------------|
| `tests/data_validation/` | 142 | Validación cruzada y taxonomía |
| `tests/financial_engine/` | 98 | Cálculo de escenarios |
| `tests/orchestration_v4/` | 76 | Flujo dos fases |
| `tests/asset_generation/` | 89 | Preflight checks |
| `tests/e2e/` | 45 | End-to-end con hoteles reales |

### Ejecutar Tests

```bash
# Tests rápidos
python -m pytest tests/ -v --tb=short

# Tests completos con validaciones
python scripts/run_all_validations.py

# Tests E2E específicos
python -m pytest tests/e2e/test_onboarding_flow.py -v
```

---

## 📋 Notas de Cambios Históricas (v3.9.1 y anteriores)

<details>
<summary>Ver documentación legacy v3.9.1 y anteriores</summary>

### v3.9.1 - Integración execute con AgentHarness

La versión 3.9.1 conecta el flujo diagnóstico → assets eliminando la desconexión que existía entre el análisis (audit) y la generación de assets (execute).

#### Nuevos Métodos en MemoryManager

| Método | Propósito |
|--------|-----------|
| find_latest_analysis(target_id) | Busca analisis_completo.json más reciente |
| save_analysis_reference(target_id, path) | Guarda referencia en historial |
| cleanup_old_sessions(days=20) | Elimina sesiones > 20 días |

#### Flags Nuevos

| Flag | Descripción |
|------|-------------|
| --force-new | Ignora análisis previo, genera nuevo |
| --bypass-harness | Modo legacy sin memoria |

---

### v3.9.0 - Financial Centralization

La versión 3.9.0 elimina valores hardcodeados y centraliza los factores financieros del modelo de pérdidas en `plan_maestro_data.json`.

#### FinancialFactors (Nuevo Módulo)

| Componente | Propósito |
|------------|-----------|
| `modules/utils/financial_factors.py` | Centraliza factores desde JSON |
| `FinancialFactorsConfig` | Dataclass con configuración regional |
| `calculate_factor_perdida()` | Fórmula: (1 - AILA) × (OTA + IA) |

**Factores centralizados:**
- `factor_captura_aila` - Por región (eje_cafetero: 0.55, caribe: 0.85)
- `comision_ota_min/base/max` - Comisiones OTA (12-15-18%)
- `penalizacion_invisibilidad_ia` - 5% fijo
- `exclusion_rating_bajo` - 40% para rating < 4.0

#### Bing Proxy (Alternativa a ChatGPT API)

| Componente | Propósito |
|------------|-----------|
| `modules/analyzers/bing_proxy_tester.py` | Estima visibilidad ChatGPT via Bing |
| `BingProxyTester` | Clase principal de testing |

**Mapeo de probabilidades:**

| Ranking Bing | Probabilidad ChatGPT |
|--------------|----------------------|
| 1 | 85% |
| 2-3 | 75-80% |
| 4-6 | 50-60% |
| 7-10 | 20-35% |
| Fuera top 10 | 10% |

---

### v3.8.0 - Gemini CLI Independence

La versión 3.8.0 elimina la dependencia de Gemini CLI e implementa validaciones nativas.

#### Validation Engine

| Componente | Propósito |
|------------|-----------|
| `modules/validation/plan_validator.py` | Valida coherencia contra Plan Maestro |
| `modules/validation/content_validator.py` | Valida estándares de contenido GEO/AEO |
| `modules/validation/security_validator.py` | Detecta secrets hardcoded |

#### Multi-Driver Architecture

| Componente | Propósito |
|------------|-----------|
| `modules/scrapers/drivers/driver_interface.py` | Interfaz abstracta común |
| `modules/scrapers/drivers/selenium_driver.py` | Wrapper Selenium con anti-detección |
| `modules/scrapers/drivers/playwright_driver.py` | Wrapper Playwright con stealth |

---

### v3.6.0 - Dynamic Impact & Confidence Tracking

La versión 3.6.0 implementa un sistema de tracking de provenance de datos y cálculo dinámico de impactos financieros.

#### Jerarquía de Fuentes de Datos

| Escenario | Fuente | Datos Obtenidos |
|-----------|--------|-----------------|
| **Hotel proporciona datos** | Input directo del hotel | reservas_mes, valor_reserva, canal_directo |
| **Hotel NO proporciona** | plan_maestro_data.json | reservas_mensuales_promedio, valor_reserva_promedio, canal_directo_porcentaje |
| **Contexto adicional** | Benchmarking.md | RevPAR regional, ADR, ocupación |

#### confidence_tracker.py

- **Propósito**: Rastrear origen de datos (hotel input vs benchmark)
- **Ubicación**: modules/utils/confidence_tracker.py
- **Clases principales**:
  - DataSource (Enum): HOTEL_INPUT, PLAN_MAESTRO_JSON, BENCHMARKING_MD, CALCULATED
  - DataConfidence: Punto de datos individual con metadata de origen

---

### v3.5.1 - Hotfix AILA

El hotfix v3.5.1 elimina 5 instancias donde el agente adivinaba valores.

#### Factores de Captura - Índice AILA Colombia
- Valores AILA: Caribe 0.85, Antioquia 0.72, Eje Cafetero 0.55
- Fórmula: Pérdida = RevPAR × hab × 30 × (1 - AILA) × (comisión + penalización)

---

### v3.7.1 - HorariosDetector Playwright

La versión 3.7.1 extrae `HorariosDetectorPlaywright` a un módulo independiente.

| Archivo | Propósito |
|---------|-----------|
| `modules/utils/horarios_detector_playwright.py` | Detector de horarios con Playwright |
| `modules/scrapers/gbp_factory.py` | Factory con `get_horarios_detector()` |

```python
from modules.scrapers.gbp_factory import get_horarios_detector

# Auto-detecta el tipo de driver y retorna la instancia correcta
detector = get_horarios_detector(page_or_driver)
tiene_horarios, confidence, metadata = detector.detect_horarios()
```

</details>

---

## 1. Arquitectura General

### 1.1 Stack Tecnológico

| Componente | Tecnología | Versión |
|------------|------------|---------|
| CLI | argparse + logging | - |
| Scraping | Playwright / Selenium | 1.40+ / 4.x |
| LLMs | DeepSeek / Anthropic | 2024-01 |
| Validación | data_validation (v4.0) | - |
| Finanzas | financial_engine (v4.0) | - |
| Coherencia | commercial_documents (v4.1) | - |

### 1.2 Flujo Principal (v4complete)

```
URL Input → Fase 1 (Hook automático)
    ↓
Fase 2 (Validación Cruzada con APIs)
    ↓
Fase 3 (PainSolutionMapper)
    ↓
Fase 4 (Gate de Coherencia ≥0.8)
    ↓
Fase 5 (Assets condicionales)
    ↓
Output: Diagnóstico + Propuesta (condicional) + Assets
```

### 1.3 Módulos Principales (v4.0)

| Módulo | Responsabilidad |
|--------|-----------------|
| data_validation/ | Validación cruzada de datos |
| financial_engine/ | Cálculo de escenarios financieros |
| orchestration_v4/ | Flujo de onboarding dos fases |
| asset_generation/ | Generación condicional de assets |
| scrapers/ | Extracción de datos de web y Google |
| analyzers/ | Análisis de brechas y oportunidades |
| generators/ | Generación de entregables (legacy) |
| agent_harness/ | Memoria y auto-corrección |

---

## Sistema de Onboarding v4.0 (Dos Fases)

### Propósito

El sistema de onboarding v4.0 captura datos operativos del hotel mediante un flujo de dos fases que garantiza precisión mediante validación cruzada.

### Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                     ONBOARDING v4.0                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   FASE 1     │      │   FASE 2     │      │   OUTPUT     │  │
│  │    HOOK      │─────▶│    INPUT     │─────▶│   ASSETS     │  │
│  │   (30%)      │      │   (60-100%)  │      │  (100%)      │  │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│         │                     │                                 │
│         ▼                     ▼                                 │
│  ┌──────────────┐      ┌──────────────┐                        │
│  │  Benchmark   │      │  Validación  │                        │
│  │   Regional   │      │   Cruzada    │                        │
│  └──────────────┘      └──────────────┘                        │
│                               │                                 │
│                               ▼                                 │
│                        ┌──────────────┐                        │
│                        │  ¿Conflictos?│                        │
│                        └──────┬───────┘                        │
│                               │                                 │
│                    ┌─────────┴─────────┐                       │
│                    ▼                   ▼                       │
│              ┌─────────┐         ┌─────────┐                   │
│              │   SÍ    │         │   NO    │                   │
│              │ Reporte │         │Assets OK│                   │
│              │ Revisar │         │ Generar │                   │
│              └─────────┘         └─────────┘                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Comandos CLI

```bash
# Flujo completo v4.1 (recomendado)
python main.py v4complete --url https://hotel.com

# Onboarding básico (datos operativos)
python main.py onboard --url https://hotel.com

# Verificar estado
python main.py onboard --url https://hotel.com --run-audit
```

---

## Sistema de Scraping con Playwright

### Propósito

Migración de Selenium a Playwright para mayor estabilidad, velocidad y anti-detección en la auditoría de Google Business Profile.

### Arquitectura de Fallback

```
┌──────────────────────────────────────────────────────────────┐
│                    GBPAuditorAuto                            │
│              (Wrapper transparente)                          │
├──────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐                                         │
│  │  ¿Playwright    │──SÍ──▶ GBPAuditorPlaywright             │
│  │  disponible?    │        (velocidad 2-3x, anti-detección) │
│  └────────┬────────┘                                         │
│           │NO                                                │
│           ▼                                                  │
│  ┌─────────────────┐                                         │
│  │  ¿Selenium      │──SÍ──▶ GBPAuditor (Selenium)           │
│  │  disponible?    │        (fallback legacy)                │
│  └────────┬────────┘                                         │
│           │NO                                                │
│           ▼                                                  │
│     RuntimeError: "No driver available"                      │
└──────────────────────────────────────────────────────────────┘
```

### Ventajas de Playwright

| Aspecto | Selenium | Playwright |
|---------|----------|------------|
| Velocidad | Media | Alta (2-3x) |
| Estabilidad | Media | Alta (auto-wait) |
| Anti-detección | Débil | Superior |
| Network Interception | Complejo | Nativo |

---

## Google Places API Client

### Propósito

Cliente unificado para Google Places API (New) con cálculo de geo_score real y sistema de caché.

### Fórmula de Geo Score

```
geo_score = (rating/5 × 30) + (min(reviews/100 × 2, 20)) + 
            (min(photos × 0.5, 20)) + (10 if has_hours) + (10 if has_website)
```

Normalizado a escala 0-100.

### Características

- Caché persistente con TTL 30 días
- Rate limiting automático
- Tracking de costos

### Uso

```python
from modules.scrapers.google_places_client import get_places_client

client = get_places_client()
places = client.search_nearby_lodging(lat=4.6, lng=-74.1)

for place in places:
    print(f"{place.name}: geo_score={place.geo_score}")
    print(f"  Desglose: {place.geo_score_formula}")
```

---

## 2. Módulos de Scraping

### 2.1 Web Scraper
modules/scrapers/web_scraper.py - Extrae: nombre, ubicación, precio, fotos, amenities

### 2.2 GBP Auditor
modules/scrapers/gbp_auditor.py - Extrae: score, reviews, rating, fotos, horarios, website

### 2.3 Schema Finder
modules/scrapers/schema_finder.py - Busca JSON-LD, Microdata, Schema.org

---

## 3. Módulos de Análisis

### 3.1 Gap Analyzer
modules/analyzers/gap_analyzer.py - Calcula brechas vs benchmarks regionales

### 3.2 ROI Calculator
modules/analyzers/roi_calculator.py - Proyecta ROI 6-12 meses

### 3.3 Competitor Analyzer
modules/analyzers/competitor_analyzer.py - Compara vs 3 competidores locales

---

## 4. Decision Engine (Legacy v3.9)

**Nota:** En v4.0, este módulo es reemplazado por `financial_engine/`.

### 4.1 Reglas de Decisión (Legacy)

| Paquete | Condición | Precio |
|---------|-----------|--------|
| Starter GEO | impacto < 6M, gbp_score ≥ 60 | 1,800,000 |
| Pro AEO | impacto < 6M, gbp_score < 60 | 3,800,000 |
| Pro AEO Plus | impacto ≥ 6M, web_score ≥ 75 | 4,800,000 |
| Elite | revpar ≥ 180K, impacto ≥ 6M | 7,500,000 |
| Elite PLUS | impacto_catastrófico | 9,800,000 |

---

## 5. Pipelines y Orquestación

### 5.1 Pipeline v4.0
modules/orchestration_v4/pipeline.py

```
OnboardingController.execute():
  Phase 1: Hook Generation
    └─→ Benchmark regional → Rango estimado
  Phase 2: Input + Validation
    └─→ Validación cruzada → Escenarios financieros
  Asset Generation
    └─→ Preflight checks → Assets condicionales
```

---

## 6. Entregables y Delivery

### 6.1 Generadores (Legacy v3.9)

| Generador | Output | Condición |
|-----------|--------|-----------|
| ReportGen | Diagnóstico + Oportunidad | Siempre |
| WhatsAppButtonGen | HTML botón flotante | Fuga SIN_WHATSAPP |
| BookingBarGen | Widget reserva directa | Motor no prominente |
| FAQGen | 10 FAQs optimizadas | Brecha AEO |

### 6.2 Generadores v4.0 (Condicionales)

| Asset | Preflight Gate | Nomenclatura |
|-------|----------------|--------------|
| WhatsApp Button | WhatsApp VERIFIED | `boton_whatsapp.html` |
| WhatsApp Button | WhatsApp ESTIMATED | `ESTIMATED_boton_whatsapp.html` |
| FAQ Page | Confidence ≥ 0.7 | `faq_page.html` |
| Schema JSON | Confidence ≥ 0.8 | `hotel_schema.json` |

### 6.3 Estructura de Output

```
output/{hotel_slug}_{timestamp}/
├── 01_DIAGNOSTICO_Y_OPORTUNIDAD.md
├── 02_PROPUESTA_COMERCIAL.md
├── 03_PLAN_TRABAJO_90_DIAS.md
├── 04_ESCENARIOS_FINANCIEROS.md    # NEW v4.0
├── 05_VALIDATION_REPORT.md         # NEW v4.0
└── evidencias/
    ├── raw_data/
    ├── validated_fields.json       # NEW v4.0
    └── preflight_results.json      # NEW v4.0
```

---

## 7. Testing

### Ejecución de Tests

```bash
# Tests rápidos
pytest tests/ -v

# Tests v4.0 específicos
pytest tests/data_validation tests/financial_engine -v

# Tests E2E
pytest tests/e2e/ -v

# Todas las validaciones
python scripts/run_all_validations.py
```

---

## 8. Scripts de Mantenimiento

| Script | Propósito |
|--------|-----------|
| sync_versions.py | Sincroniza VERSION.yaml con docs |
| generate_domain_primer.py | Actualiza DOMAIN_PRIMER.md |
| validate_context_integrity.py | Valida referencias cruzadas |
| run_all_validations.py | Orquestador de validaciones v4.0 |

---

## 9. Variables de Entorno

| Variable | Descripción |
|----------|-------------|
| ANTHROPIC_API_KEY | API key Claude |
| EXASEARCH_API_KEY | API key Exa |
| GBP_GEO_VALIDATION_ENABLED | Validación geográfica |
| DATA_VALIDATION_STRICT | Modo estricto v4.0 (default: true) |
| FINANCIAL_ENGINE_DEBUG | Debug de cálculos financieros |

---

## 10. Contribuidores

- Lead Developer: Claude (Anthropic)
- Architecture: Plan Maestro v4.1.0 - Sistema de Confianza
- Benchmarking: AILA Colombia 2026
- Testing: 704 tests passing, 5 hoteles piloto

---

## Apéndice: Glosario v4.0

| Término | Definición |
|---------|------------|
| **Hook** | Mensaje inicial con rango estimado de pérdida |
| **Validación Cruzada** | Comparación de datos entre múltiples fuentes |
| **Escenario** | Proyección financiera (Conservador/Realista/Optimista) |
| **Preflight Check** | Gate de calidad antes de generar un asset |
| **Taxonomía de Confianza** | VERIFIED/ESTIMATED/CONFLICT |
| **AILA** | Índice de Acceso a la Información Local del Alojamiento |
| **ADR** | Average Daily Rate (tarifa promedio) |

---

*Documento generado automáticamente. Última actualización: 28 Febrero 2026*
