# Plan: Corrección de Issues v4.5.6 - NEVER_BLOCK

**Versión**: 1.0.0
**Fecha**: 2026-03-23
**Proyecto**: IA Hoteles CLI - Corrección de Bugs v4.5.6
**Estado**: 🚧 EN PLANIFICACIÓN

---

## Resumen Ejecutivo

Este plan documenta las intervenciones necesarias para corregir los issues identificados durante la evaluación del informe V4COMPLETE para Hotel Visperas. Las correcciones abarcan desde bugs críticos de regresión hasta mejoras de calidad en la arquitectura NEVER_BLOCK.

---

## Dependencias entre Fases

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        FLUJO DE FASES                                       │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                 │
│  │   FASE 1    │────▶│   FASE 2    │────▶│   FASE 3    │                 │
│  │   COP COP   │     │   ASSETS    │     │   QUALITY   │                 │
│  │   + TESTS   │     │   BUGS      │     │  IMPROVMT   │                 │
│  └─────────────┘     └─────────────┘     └─────────────┘                 │
│        │                   │                   │                          │
│        │                   │                   │                          │
│        ▼                   ▼                   ▼                          │
│  ┌─────────────────────────────────────────────────────┐                   │
│  │                    FASE 4                            │                   │
│  │              FEATURE ENHANCEMENTS                     │                   │
│  │         (Depende de Fases 1, 2, 3 completas)         │                   │
│  └─────────────────────────────────────────────────────┘                   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Matriz de Conflictos Potenciales

| Fase | Archivos Principales | Archivos Secundarios | Overlap Potencial |
|------|---------------------|---------------------|-------------------|
| **Fase 1** | `modules/providers/benchmark_resolver.py`, `templates/*.md` | `tests/test_cop_cop_regression.py` | Ninguno |
| **Fase 2** | `modules/asset_generation/conditional_generator.py`, `modules/asset_generation/asset_content_validator.py` | `modules/asset_generation/asset_metadata.py` | asset_metadata.py (lectura) |
| **Fase 3** | `modules/asset_generation/asset_content_validator.py` | `modules/providers/autonomous_researcher.py` | asset_content_validator.py (modificación) |
| **Fase 4** | `modules/asset_generation/preflight_checks.py`, `modules/asset_generation/conditional_generator.py` | `modules/providers/benchmark_resolver.py` | benchmark_resolver.py (lectura) |

---

## Tabla de Recomendaciones por Prioridad

### 🔴 CRÍTICA (Fase 1 -Obligatorio)

| ID | Recomendación | Severidad | Tipo |
|----|---------------|-----------|------|
| C1 | Bug "COP COP" - Regresión en diagnósticos | ~~CRITICAL~~ → ✅ FIXED | Bug Fix |
| C2 | Test de regresión para detectar "COP COP" | ~~CRITICAL~~ → ✅ FIXED | Testing |

### 🔴 ALTA (Fase 2)

| ID | Recomendación | Severidad | Tipo |
|----|---------------|-----------|------|
| A1 | optimization_guide se escribe aunque falla validación | HIGH | Bug Fix |
| A2 | confidence_score es siempre 0.5 en asset_generation_report | HIGH | Bug Fix |

### 🟡 MEDIA (Fase 3)

| ID | Recomendación | Severidad | Tipo |
|----|---------------|-----------|------|
| M1 | Mejorar detección de frases genéricas (falsos positivos) | MEDIUM | Quality |
| M2 | Clarificar semántica can_use vs status | MEDIUM | Documentation |
| M3 | Documentar output de autonomous_researcher | MEDIUM | Documentation |

### 🟠 BAJA (Fase 4)

| ID | Recomendación | Severidad | Tipo |
|----|---------------|-----------|------|
| B1 | Cross-validación benchmark vs datos reales | LOW | Feature |
| B2 | Reducir umbrales para hoteles nuevos | LOW | Feature |
| B3 | Corregir "Refinando" → "refinado" | LOW | Bug Fix |

---

## Criterios de Aceptación por Fase

### Fase 1: COP COP + Tests
- [x] `grep -rn "COP COP" output/` retorna 0 resultados
- [x] `grep -rn "COP COP" modules/` retorna 0 resultados
- [x] Test `test_cop_cop_regression.py` existe y pasa
- [x] Validación: `pytest tests/test_cop_cop_regression.py -v` PASS

### Fase 2: Asset Generation Bugs
- [ ] optimization_guide NO se escribe cuando validation falla
- [ ] confidence_score en asset_generation_report coincide con metadata.json
- [ ] Validación: `pytest tests/test_never_block_integration.py -v` PASS

### Fase 3: Quality Improvements
- [ ] "verificar", "revisar", "no configurado" NO son marcados como generic_phrase
- [ ] Documentación clarifica can_use vs status
- [ ] autonomous_researcher tiene output documentado o evidencia de no-op

### Fase 4: Feature Enhancements
- [ ] Benchmark validation alerta cuando datos reales se desvían >20% del benchmark
- [ ] whatsapp_button y faq_page tienen umbrales diferenciados para hoteles nuevos
- [ ] "Refinando" corregido a "refinado" en benchmark_descriptions

---

## Orden de Ejecución Recomendado

| Orden | Fase | Justificación |
|-------|------|---------------|
| 1 | **Fase 1** | Bugs críticos de regresión - afecta credibilidad del sistema |
| 2 | **Fase 2** | Bugs que causan inconsistencias entre estado reportado y real |
| 3 | **Fase 3** | Mejoras de calidad que no bloquean otras fases |
| 4 | **Fase 4** | Features que pueden implementarse con confianza |

---

## Métricas Objetivo

| Métrica | Valor Actual | Valor Target |
|---------|--------------|--------------|
| Tests passing | 1434+ | 1440+ (6 nuevos) |
| Bugs críticos | 2 | 0 |
| Inconsistencias de metadata | 6 | 0 |
|COP COP occurrences | 15+ | 0 |

---

## Archivos de Evidencia Generados

- `evidence/fase-1-cop-cop/`
- `evidence/fase-2-asset-bugs/`
- `evidence/fase-3-quality/`
- `evidence/fase-4-enhancements/`

---

**Siguiente paso**: Ejecutar FASE 1 (primera sesión) según `05-prompt-inicio-sesion-fase-1-COP-COP.md`

---

## Prompts de Fase Creados

| Fase | Archivo | Estado |
|------|---------|--------|
| FASE 1 | `05-prompt-inicio-sesion-fase-1-COP-COP.md` | ✅ Listo |
| FASE 2 | `05-prompt-inicio-sesion-fase-2-ASSET-BUGS.md` | ✅ Listo |
| FASE 3 | `05-prompt-inicio-sesion-fase-3-QUALITY.md` | ✅ Listo |
| FASE 4 | `05-prompt-inicio-sesion-fase-4-FEATURES.md` | ✅ Listo |

---

## Resumen de la Planificación

```
┌──────────────────────────────────────────────────────────────────────┐
│                    EJECUCIÓN POR SESIONES                            │
├──────────────────────────────────────────────────────────────────────┤
│                                                                      │
│  SESIÓN 1 (FASE 1): COP COP Regression                              │
│  ├── TDD: Crear test que falla (COP COP existe)                     │
│  ├── Encontrar fuente del bug en modules/                           │
│  ├── Corregir "COP COP" → "COP" en generador                       │
│  └── Validar: grep -rn "COP COP" modules/ = 0                      │
│                                                                      │
│  SESIÓN 2 (FASE 2): Asset Generation Bugs                          │
│  ├── Investigar orden: write vs validation                          │
│  ├── Bug A: prevention of write on validation failure                │
│  ├── Bug B: confidence_score consistency                            │
│  └── Validar: 2 nuevos tests pasan                                   │
│                                                                      │
│  SESIÓN 3 (FASE 3): Quality Improvements                            │
│  ├── M1: Calibrar detector de frases genéricas                      │
│  ├── M2: Documentar can_use vs status semantics                     │
│  ├── M3: Documentar autonomous_researcher behavior                   │
│  └── Validar: optimization_guide pasa validación                     │
│                                                                      │
│  SESIÓN 4 (FASE 4): Feature Enhancements                            │
│  ├── B1: Implementar benchmark cross-validation                      │
│  ├── B2: Umbrales diferenciados para hoteles nuevos                  │
│  ├── B3: Corregir "Refinando" → "refinado"                          │
│  └── Validar: Tests de feature pasan                                 │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

---

## Métricas Esperadas Después de Completar

| Métrica | Antes | Después |
|---------|-------|---------|
| Tests passing | 1434 | 1446 (+12) |
| Bugs críticos | 2 | 0 |
| Inconsistencias metadata | 6 | 0 |
| COP COP occurrences | 15+ | 0 |
| Falsos positivos validation | >0 | 0 |

---

## Recomendaciones Transversales (FASE 5)

⚠️ **Estas recomendaciones NO fueron cubiertas en las Fases 1-4** porque son transversales al sistema completo.

### 🔴 CRÍTICAS - No cubiertass

| ID | Recomendación | Razón no cubierta | Prioridad |
|----|---------------|------------------|-----------|
| T1 | **Audit debe ejecutarse ANTES de asset generation** | Orden de dependencias no enforced | CRITICAL |
| T2 | **Validar coherence score con datos del sistema** | Coherence 0.88 nunca fue verificado | HIGH |
| T3 | **autonomous_researcher: output o no-op documentado** | Módulo se ejecuta pero no hay evidencia | HIGH |

### 🟡 MEDIA - No cubiertas

| ID | Recomendación | Razón no cubierta | Prioridad |
|----|---------------|------------------|-----------|
| T4 | **Métricas de salud del sistema** post-ejecución | No hay tracking de salud | MEDIUM |
| T5 | **Capability contract** de v4.5.6 | No hay matriz de capabilities | MEDIUM |
| T6 | **Regresión testing** para todas las fases | Tests son de fase, no E2E | MEDIUM |

---

## FASE 5: Validación Transversal y Cierre

**ID**: FASE-5-VALIDATION-CLOSURE
**Objetivo**: Ejecutar validaciones transversales y cerrar proyecto correctamente
**Dependencias**: Fases 1, 2, 3, 4 completadas
**Duración estimada**: 45-60 minutos
**Skill**: systematic-debugging, test-driven-development

### Tareas de FASE 5

#### Tarea T1: Verificar y corregir orden de dependencias Audit → Assets
**Problema**: Los timestamps sugieren que optimization_guide se generó antes del audit completo
```
audit_report.json: timestamp 07:32:13
optimization_guide.md: timestamp 07:32:14

Pero el contenido de optimization_guide depende de datos del audit.
```

**Validación**:
```bash
# Verificar orden real de generación
grep -n "timestamp" output/v4_complete/v4_complete_report.json
grep -n "generated_at" output/v4_complete/hotel_vísperas/*/*_metadata.json
```

**Criterio**: El audit_report.json debe generarse ANTES que cualquier asset.

#### Tarea T2: Validar coherence score con datos reales
**Problema**: Coherence 0.88 declarado pero no hay evidencia de cálculo
```
v4_complete_report.json: "coherence_score": 0.8828571428571428
audit_report.json: geo_score=0, 0 reviews, 0 photos

¿Cómo se calcula coherence con datos tan limitados?
```

**Validación**:
- Identificar fórmula de coherence en el código
- Verificar con datos del Hotel Visperas
- Documentar qué pasa cuando coherence < 0.8

#### Tarea T3: Capability Contract de autonomous_researcher
**Problema**: El módulo se menciona en el informe pero no produce output
```
Informe dice: "Autonomous Researcher: El sistema intentó investigar..."
Pero no hay archivo de evidencia, ni logs, ni metadata referenciándolo.
```

**Opciones**:
1. Es no-op intencional → documentar como tal
2. Debe generar evidencia → implementar output mínimo

#### Tarea T4: Métricas de salud post-ejecución
**Crear dashboard/métricas**:
- Time to generate assets
- Success rate de generation
- Percentage de assets con can_use=true
- Confidence score promedio

#### Tarea T5: Tests de regresión E2E
**Crear test que verifica todas las correcciones de Fases 1-4**:
```python
def test_e2e_corrections_v4_5_6():
    # FASE 1: No COP COP en outputs
    # FASE 2: confidence_score consistency
    # FASE 3: validator no false positives
    # FASE 4: benchmark validation works
    pass
```

---

### Tests Obligatorios FASE 5

| Test | Criterio |
|------|----------|
| `test_audit_runs_before_assets` | Timestamp audit < timestamp assets |
| `test_coherence_calculation_validated` | Coherence score es calculable con datos reales |
| `test_capability_contract_fulfilled` | autonomous_researcher tiene output o no-op documentado |
| `test_e2e_regression_all_phases` | Todos los bugs de Fases 1-4 no regresan |

---

### Criterios de Completitud FASE 5

- [ ] T1: Orden audit → assets verificado y documentado
- [ ] T2: Coherence calculation entendida y documentada
- [ ] T3: autonomous_researcher con comportamiento explícito
- [ ] T4: Métricas de salud disponibles
- [ ] T5: Test E2E pasa
- [ ] **Proyecto marcado como CERRADO**

---

## CIERRE DEL PROYECTO

### Checklist de Cierre

| Item | Estado |
|------|--------|
| Todas las 5 fases completadas | ⬜ |
| CHANGELOG.md actualizado (v4.5.7 o siguiente) | ⬜ |
| Métricas finales documentadas | ⬜ |
| Evidence directories con contenido | ⬜ |
| README del plan actualizado | ⬜ |
| Capabilities verificadas | ⬜ |

### Entregables Finales

| Entregable | Ubicación |
|-----------|-----------|
| Plan completo | `.opencode/plans/08-plan-correccion-v4-issues.md` |
| Dependencias | `.opencode/plans/dependencias-fases.md` |
| Prompts de fase (4) | `.opencode/plans/05-prompt-inicio-sesion-fase-*.md` |
| Documentación post-proyecto | `.opencode/plans/09-documentacion-post-proyecto.md` |
| Evidence (5 carpetas) | `evidence/fase-{1-4}-*/` + fase-5 |

---

## Resumen Final: TODAS las Recomendaciones Cubiertas

### De Evaluación del Informe (8 issues)
| ID | Recomendación | Fase |
|----|---------------|------|
| C1 | COP COP bug | FASE 1 |
| C2 | Test regresión COP COP | FASE 1 |
| A1 | optimization_guide write order | FASE 2 |
| A2 | confidence_score consistency | FASE 2 |
| M1 | Detección frases genéricas | FASE 3 |
| M2 | can_use vs status docs | FASE 3 |
| M3 | autonomous_researcher docs | FASE 3 |
| B1/B2/B3 | Features (benchmark, thresholds, typo) | FASE 4 |

### De Recomendaciones Adicionales (6 issues)
| ID | Recomendación | Fase |
|----|---------------|------|
| Adic-1 | COP COP como regresión | FASE 1 |
| Adic-2 | Test detección automática | FASE 1 |
| Adic-3 | Order validation vs write | FASE 2 |
| Adic-4 | Confidence score propagation | FASE 2 |
| Adic-5 | Benchmark vs real data | FASE 4 |
| Adic-6 | "Refinando" typo | FASE 4 |

### Transversales (6 issues) - FASE 5
| ID | Recomendación | Status |
|----|---------------|--------|
| T1 | Audit → assets order | FASE 5 |
| T2 | Coherence validation | FASE 5 |
| T3 | autonomous_researcher output | FASE 5 |
| T4 | Métricas de salud | FASE 5 |
| T5 | Capability contract | FASE 5 |
| T6 | E2E regression tests | FASE 5 |

---

---

## PARTE 2: EVOLUCIÓN REAL (FASES 6-10)

⚠️ **NOTA**: Las fases 1-5 son **REMEDIACIÓN** (corrigen lo que está mal).
Las fases 6-10 son **EVOLUCIÓN** (hacen que el sistema sea mejor).

### Gap Analysis: Estado Actual vs Necesidad

| Área | Estado Actual | Necesidad de Evolución |
|------|-------------|----------------------|
| **Orchestration** | Pipeline lineal secuencial | Validación temprana, branching inteligente |
| **Quality Gates** | Coherence verificado pero no mejorado | Gates adaptativos basados en contexto |
| **Delivery** | Assets en folders, sin packaging | Pipeline de delivery automatizado |
| **UX/Outputs** | MD/JSON/HTML dispersos | Dashboard unificado, outputs consistentes |
| **Autonomous Research** | Módulo existe pero no produce output | Investigación real con resultados |
| **AI/ML** | Disclaimer generator básico | Contexto LLM, generación sofisticada |
| **Benchmark** | Solo fallback regional | Benchmark inteligente con ML |
| **Preflight** | Checks básicos | Sistema de credit score para datos |

---

## FASE 6: Arquitectura de Orchestration v2

**ID**: FASE-6-ORCHESTRATION-V2
**Objetivo**: Refactorizar orchestration con validación temprana y branching inteligente
**Dependencias**: FASE 5 completada
**Duración estimada**: 2-3 horas
**Skill**: code-architecture, systematic-debugging

### Problema Actual
```
Flujo actual (lineal):
Audit → Validation → Asset Generation → Report

Problema:
- Validation ocurre DESPUÉS de generación ( Assets se escriben antes de validar)
- No hay branching: todos los assets se intentan generar
- Errores en paso 3 no se detectan hasta el reporte final
```

### Solución: Validación Temprana + Branching
```
                    ┌──────────────┐
                    │   AUDIT      │
                    │  (collect)   │
                    └──────┬───────┘
                           │
                           ▼
                    ┌──────────────┐
                    │  ASSESSMENT  │
                    │ (score data) │
                    └──────┬───────┘
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ LOW DATA │ │ MED DATA  │ │HIGH DATA │
        │ Branch A │ │ Branch B  │ │ Branch C │
        └──────────┘ └──────────┘ └──────────┘
              │            │            │
              ▼            ▼            ▼
        ┌──────────┐ ┌──────────┐ ┌──────────┐
        │ Fast Gen │ │ Standard │ │ Full Gen │
        │ 3 assets│ │ 5 assets │ │ 9 assets │
        └──────────┘ └──────────┘ └──────────┘
```

### Tasks FASE 6

#### T6A: Implementar Data Assessment婚前
**Objetivo**: Clasificar hotel según calidad de datos antes de generar

**Métricas a evaluar**:
- GBP data completeness (reviews, photos, score)
- Web scraping success rate
- SEO data availability
- Schema markup presence

**Clasificaciones**:
```
LOW:   < 30% data available  → Fast Path (3-4 assets críticos)
MED:   30-70% data available → Standard Path (6-7 assets)
HIGH:  > 70% data available → Full Path (9+ assets)
```

#### T6B: Implementar Validation Before Generation
**Objetivo**: Validar datos ANTES de generar assets

**Flujo corregido**:
```
1. Collect data
2. Validate data quality → SI FAIL → no generation, error inmediato
3. Assess data classification
4. Branch to appropriate generation path
5. Generate assets (validación ya pasó)
```

#### T6C: Refactorizar conditional_generator para branching
**Objetivo**: Soportar múltiples paths de generación

**Cambios**:
- Agregar método `assess_data_quality(data) → Classification`
- Modificar `generate()` para usar branching
- Crear generators por path (fast, standard, full)

### Tests FASE 6
| Test | Criterio |
|------|----------|
| `test_data_assessment_low` | Clasifica correctamente hotels con <30% datos |
| `test_data_assessment_high` | Clasifica correctamente hotels con >70% datos |
| `test_validation_before_generation` | No genera si datos inválidos |
| `test_branching_paths` | 3 paths diferentes ejecutan correctamente |

---

## FASE 7: Pipeline de Delivery v2

**ID**: FASE-7-DELIVERY-V2
**Objetivo**: Implementar pipeline de delivery automatizado con packaging
**Dependencias**: FASE 6 completada
**Duración estimada**: 1-2 horas
**Skill**: delivery-pipeline, automation

### Problema Actual
```
Estado actual:
- Assets se generan en folders dispersos
- No hay packaging automatizado
- No hay zip/tarball por hotel
- Entrega manual requiere copy-paste
```

### Solución: Delivery Pipeline
```
Generation → Validation → Packaging → Manifest → Delivery

├── output/v4_complete/hotel_visperas/
│   ├── 01_DIAGNOSTICO.md
│   ├── 02_PROPUESTA.md
│   └── hotel_visperas/
│       ├── geo_playbook/
│       ├── hotel_schema/
│       └── ...
│
└── deliveries/
    └── hotel_visperas_20260323.zip
        ├── DIAGNOSTICO.md
        ├── PROPUESTA_COMERCIAL.md
        ├── ASSETS/
        │   ├── geo_playbook.md
        │   ├── hotel_schema.json
        │   └── ...
        ├── MANIFEST.json
        └── README_DELIVERY.md
```

### Tasks FASE 7

#### T7A: Crear DeliveryPackager class
**Objetivo**: Automatizar packaging de deliverables

```python
class DeliveryPackager:
    def package(hotel_id: str, output_dir: str) -> str:
        """Crea ZIP con todos los assets"""
        
    def create_manifest(hotel_id: str, assets: list) -> dict:
        """Genera manifest.json con metadata"""
        
    def create_readme(delivery_dir: str) -> None:
        """Genera README con instrucciones de implementación"""
```

#### T7B: Agregar delivery al orchestration
**Objetivo**: Integrar packaging en pipeline

```python
# En orchestration_v4
def execute_full_pipeline(hotel_id):
    # ... generación ...
    
    # NEW: Delivery step
    packager = DeliveryPackager()
    delivery_path = packager.package(hotel_id, output_dir)
    
    return {"output_dir": output_dir, "delivery_path": delivery_path}
```

#### T7C: Crear template de README para delivery
**Objetivo**: Guía de implementación para el cliente

**Secciones**:
- Overview de deliverables
- Instrucciones de implementación por asset
- Timeline sugerido
- Checklist de implementación

### Tests FASE 7
| Test | Criterio |
|------|----------|
| `test_package_creates_zip` | ZIP se crea con todos los assets |
| `test_manifest_complete` | Manifest incluye todos los assets |
| `test_readme_generated` | README con instrucciones existe |

---

## FASE 8: Autonomous Research Engine

**ID**: FASE-8-AUTONOMOUS-RESEARCH
**Objetivo**: Implementar investigación autónoma real con output verificable
**Dependencias**: FASE 5 completada
**Duración estimada**: 2-3 horas
**Skill**: autonomous-ai-agents, web-research

### Problema Actual
```
Informe dice: "Autonomous Researcher intentó investigar..."
Pero no hay evidencia. El módulo es no-op o su output se pierde.

El sistema no está usando datos de Booking, TripAdvisor, Instagram.
```

### Solución: Research Engine con Evidence
```
Research Request
      │
      ▼
┌─────────────────────────────────────┐
│     AUTONOMOUS RESEARCHER ENGINE    │
├─────────────────────────────────────┤
│  1. GBP Lookup                      │
│  2. Booking.com Scrape              │
│  3. TripAdvisor Scrape              │
│  4. Instagram Lookup               │
│  5. Cross-Reference                 │
│  6. Confidence Scoring             │
└─────────────────────────────────────┘
      │
      ▼
Research Report (JSON)
      │
      ▼
Assets que referencian el research
```

### Tasks FASE 8

#### T8A: Implementar research_output_schema
**Objetivo**: Definir schema de output del research

```python
@dataclass
class ResearchOutput:
    hotel_name: str
    sources_checked: List[str]
    data_found: Dict[str, Any]
    confidence: float
    citations: List[str]  # URLs de donde viene la info
    gaps: List[str]       # Qué NO se encontró
```

#### T8B: Implementar source scrapers
**Objetivo**: Extraer datos de Booking, TripAdvisor, Instagram

**Scrapers**:
- `scrapers/booking_scraper.py` - Reviews, ratings, photos
- `scrapers/tripadvisor_scraper.py` - Reviews, rankings
- `scrapers/instagram_scraper.py` - Photos, engagement

#### T8C: Integrar research en orchestration
**Objetivo**: Research ocurre después de audit, antes de generation

**Flujo**:
```
Audit → Research → Assessment → Generation → Report
```

**Beneficio**: Assets generation usa datos de múltiples fuentes, no solo GBP.

#### T8D: Research confidence scoring
**Objetivo**: Score que indica calidad del research

```python
def calculate_research_confidence(sources: List[str], data: Dict) -> float:
    """
    sources_checked: 4/4 → 1.0
    sources_checked: 2/4 → 0.5
    sources_checked: 1/4 → 0.25
    """
```

### Tests FASE 8
| Test | Criterio |
|------|----------|
| `test_research_output_schema` | Schema se serializa correctamente |
| `test_scraper_booking` | Datos de Booking se extraen |
| `test_research_confidence` | Score refleja fuentes encontradas |
| `test_research_integrated` | Research output disponible para assets |

---

## FASE 9: AI/ML Enhancement - Intelligent Disclaimer Generator

**ID**: FASE-9-AI-DISCLAIMER
**Objetivo**: Evolucionar disclaimer generator con contexto LLM
**Dependencias**: FASE 8 completada
**Duración estimada**: 2-3 horas
**Skill**: llm-integration, prompt-engineering

### Problema Actual
```
Disclaimer actual:
"Este asset fue generado con datos estimados..."

El disclaimer NO dice:
- Qué datos específica faltan
- Qué benchmark se usó
- Cómo afecta la calidad del asset
- Qué hacer para mejorar
```

### Solución: Contextual AI Disclaimers
```
Tipo de Asset: hotel_schema
Confidence: 0.3
Datos faltantes: GBP reviews, photos, ratings
Benchmark usado: Pereira boutique avg

Disclaimer INTELIGENTE:
"""
⚠️ ASSET CON BAJA CONFIANZA (0.3/1.0)

Este schema fue generado usando benchmark regional porque:
• Google Business Profile no tiene datos (0 reviews, 0 fotos)
• Sistema usó promedio de hotels boutique en Pereira como referencia

PARA MEJORAR ESTE ASSET:
1. Completar perfil de Google Business Profile
2. Agregar al menos 10 fotos de alta calidad
3. Solicitar 5+ reseñas a clientes reales

CONFIDENCE ESPERADO DESPUÉS: 0.8+
"""
```

### Tasks FASE 9

#### T9A: Implementar DisclaimerGeneratorV2
**Objetivo**: Generador con contexto LLM

```python
class IntelligentDisclaimerGenerator:
    def generate(
        asset_type: str,
        confidence: float,
        missing_data: List[str],
        benchmark_used: str,
        improvement_steps: List[str]
    ) -> str:
        """Genera disclaimer contextual con recomendaciones"""
```

#### T9B: Integrar con asset_metadata
**Objetivo**: Todos los assets incluyen disclaimers accionables

**Metadato mejorado**:
```json
{
  "disclaimer": "...",
  "missing_data": ["gbp_reviews", "photos"],
  "benchmark_used": "pereira_boutique_avg",
  "improvement_steps": [
    "Agregar 10+ fotos a GBP",
    "Solicitar 5+ reseñas"
  ],
  "confidence_after_fix": 0.85
}
```

#### T9C: Agregar improvement_score a assets
**Objetivo**: Score que indica potencial de mejora

```python
def calculate_improvement_score(asset: dict) -> float:
    """
    Compara confidence actual con confidence posible
    después de seguir improvement steps
    
    current: 0.3, after: 0.85 → improvement_score: 0.55
    """
```

### Tests FASE 9
| Test | Criterio |
|------|----------|
| `test_intelligent_disclaimer_content` | Disclaimer menciona datos específicos |
| `test_disclaimer_includes_steps` | Incluye improvement steps |
| `test_improvement_score` | Score se calcula correctamente |

---

## FASE 10: UX/Dashboard - System Health Monitor

**ID**: FASE-10-DASHBOARD
**Objetivo**: Implementar dashboard unificado de métricas de salud
**Dependencias**: FASE 7 completada
**Duración estimada**: 1-2 horas
**Skill**: reporting, metrics, dashboard

### Problema Actual
```
No hay visibility del estado del sistema:
- Cuántos assets se generan por hotel
- Success rate
- Confidence promedio
- Tiempo de ejecución
- Errors/warnings por categoría
```

### Solución: Health Dashboard
```
┌─────────────────────────────────────────────────────────────┐
│              IA HOTELES - SYSTEM HEALTH DASHBOARD           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │    156      │  │    89%      │  │   0.72      │        │
│  │  Hotels     │  │  Success    │  │  Avg Conf   │        │
│  │  Analyzed   │  │  Rate       │  │  Score      │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│                                                             │
│  ┌─────────────────────────────────────────────┐            │
│  │          Confidence Distribution             │            │
│  │  ██████████████████░░░░ 0.9+ (65)          │            │
│  │  ████████████░░░░░░░░░░░ 0.7-0.9 (45)     │            │
│  │  ██████░░░░░░░░░░░░░░░░░ 0.5-0.7 (30)     │            │
│  │  ████░░░░░░░░░░░░░░░░░░░ <0.5 (16)        │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
│  ┌─────────────────────────────────────────────┐            │
│  │          Assets by Type                     │            │
│  │  geo_playbook:     142 ████████████████████│            │
│  │  hotel_schema:     138 ███████████████████ │            │
│  │  review_widget:    130 █████████████████   │            │
│  │  optimization_guide: 89 ███████████        │            │
│  └─────────────────────────────────────────────┘            │
│                                                             │
│  Last Updated: 2026-03-23 08:30:00                         │
└─────────────────────────────────────────────────────────────┘
```

### Tasks FASE 10

#### T10A: Crear HealthMetricsCollector
**Objetivo**: Recolectar métricas en cada ejecución

```python
@dataclass
class ExecutionMetrics:
    hotel_id: str
    timestamp: datetime
    assets_generated: int
    assets_failed: int
    success_rate: float
    avg_confidence: float
    execution_time: float
    errors: List[str]
    warnings: List[str]
```

#### T10B: Implementar HealthDashboardGenerator
**Objetivo**: Generar dashboard HTML

```python
class HealthDashboardGenerator:
    def generate_html(metrics: List[ExecutionMetrics]) -> str:
        """Genera dashboard HTML con Chart.js"""
        
    def generate_json_summary(metrics: List[ExecutionMetrics]) -> dict:
        """Genera summary para integración"""
```

#### T10C: Integrar en orchestration
**Objetivo**: Dashboard se genera después de cada ejecución

```python
# En main.py o orchestration
def post_execution():
    metrics = collector.collect()
    dashboard = generator.generate_html(all_metrics)
    save("output/health_dashboard.html", dashboard)
```

### Tests FASE 10
| Test | Criterio |
|------|----------|
| `test_metrics_collector` | Métricas se recolectan correctamente |
| `test_dashboard_html_generated` | HTML con gráficos se genera |
| `test_dashboard_integrated` | Dashboard disponible post-ejecución |

---

## Resumen: Fases de Evolución (6-10)

| Fase | Objetivo | Duración | Impacto |
|------|----------|----------|---------|
| **FASE 6** | Orchestration v2 (branching) | 2-3h | CRITICAL |
| **FASE 7** | Delivery Pipeline v2 | 1-2h | HIGH |
| **FASE 8** | Autonomous Research | 2-3h | CRITICAL |
| **FASE 9** | AI Disclaimer | 2-3h | MEDIUM |
| **FASE 10** | Health Dashboard | 1-2h | MEDIUM |

**Total Evolución**: ~10 horas de desarrollo

---

## Métricas: Antes vs Después de Evolución

| Métrica | Antes (v4.5.6) | Después (v4.6) |
|---------|---------------|-----------------|
| **Delivery** | Manual, disperso | Automatizado, packaged |
| **Research** | No-op o limitada | Full multi-source |
| **Disclaimer** | Genérico | Contextual + actionable |
| **Orchestration** | Lineal, sin branching | Intelligent branching |
| **Health Visibility** | Ninguna | Real-time dashboard |
| **Asset Quality** | Variable | Improvement score |
| **Tests** | ~1446 | ~1470 (+24) |

---

## Roadmap Completo: Remediation + Evolution

```
┌─────────────────────────────────────────────────────────────────┐
│                    ROADMAP COMPLETO v4.6                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ══════════════════════════════════════════════════════════════  │
│  ║  REMEDIATION (Fix what's broken) - Fases 1-5                ║
│  ══════════════════════════════════════════════════════════════  │
│  FASE 1: COP COP Regression          [C1, C2]                   │
│  FASE 2: Asset Generation Bugs       [A1, A2]                   │
│  FASE 3: Quality Improvements       [M1, M2, M3]                │
│  FASE 4: Feature Enhancements       [B1, B2, B3]               │
│  FASE 5: Validation & Closure        [T1-T6]                    │
│                                                                  │
│  ══════════════════════════════════════════════════════════════  │
│  ║  EVOLUTION (Make it better) - Fases 6-10                    ║
│  ══════════════════════════════════════════════════════════════  │
│  FASE 6: Orchestration v2          [Branching + Early Val]       │
│  FASE 7: Delivery Pipeline v2       [Automated Packaging]        │
│  FASE 8: Autonomous Research       [Multi-source Research]      │
│  FASE 9: AI Disclaimer             [Contextual + Actionable]     │
│  FASE 10: Health Dashboard         [Visibility]                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

TOTAL: 10 FASES → ~15 horas de desarrollo → v4.6.0
```

---

## Nueva Versión: v4.6.0

| Componente | Cambio | Breaking |
|-----------|--------|----------|
| **Orchestration** | v2 con branching | ⚠️ Sí |
| **Delivery** | v2 automatizado | ⚠️ Sí |
| **Research** | v2 full autonomous | No |
| **Disclaimer** | v2 intelligent | No |
| **Dashboard** | v1 new | No |
| **Tests** | +24 nuevos | No |

**CHANGELOG v4.6.0**:
```markdown
## [4.6.0] - 2026-03-XX

### 🚀 EVOLUCION MAJOR

**Orchestration v2**
- Intelligent branching based on data quality
- Early validation prevents waste
- 3 generation paths: Fast/Standard/Full

**Delivery Pipeline v2**
- Automated ZIP packaging
- Manifest generation
- README delivery template

**Autonomous Research v2**
- Multi-source research (GBP, Booking, TripAdvisor, Instagram)
- Research output schema with citations
- Research confidence scoring

**AI Disclaimer v2**
- Contextual disclaimers with missing data details
- Improvement steps included
- Expected confidence after fixes

**Health Dashboard v1**
- Real-time system metrics
- Success rate tracking
- Confidence distribution charts

### 🐛 Bug Fixes
- [Todos los bugs de Fases 1-5]
```

---

**Estado**: 🟡 PLANIFICADO - 5 fases remediation + 5 fases evolution
