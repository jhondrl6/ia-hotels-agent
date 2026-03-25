# Dependencias de Fases - Corrección v4.5.6

**Proyecto**: IA Hoteles CLI - Corrección de Bugs NEVER_BLOCK v4.6.0
**Archivo**: `.opencode/plans/dependencias-fases.md`
**Versión**: 1.1.0
**Fecha creación**: 2026-03-23
**Última actualización**: 2026-03-23

---

## Diagrama de Dependencias

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FLUJO DE DEPENDENCIAS                             │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   ┌─────────────┐                                                          │
│   │   START     │                                                          │
│   └──────┬──────┘                                                          │
│          │                                                                  │
│          ▼                                                                  │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   FASE 1    │────▶│   FASE 2    │────▶│   FASE 3    │                  │
│   │   COP COP   │     │   ASSETS    │     │   QUALITY   │                  │
│   │   + TESTS   │     │   BUGS      │     │  IMPROVMT   │                  │
│   └─────────────┘     └─────────────┘     └─────────────┘                  │
│                                                        │                    │
│                                                        ▼                    │
│                                               ┌─────────────┐               │
│                                               │   FASE 4    │               │
│                                               │   FEATURE   │               │
│                                               │ ENHANCEMTS  │               │
│                                               └─────────────┘               │
│                                                                            │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐                  │
│   │   FASE 5    │────▶│   FASE 6    │────▶│   FASE 7    │                  │
│   │  TRANSVERSA │     │ ORCHESTRAT. │     │  DELIVERY   │                  │
│   └─────────────┘     │    V2       │     │    V2       │                  │
│                        └─────────────┘     └─────────────┘                  │
│                                │                   │                         │
│                                ▼                   ▼                         │
│                        ┌─────────────┐     ┌─────────────┐                  │
│                        │   FASE 8    │────▶│   FASE 9    │                  │
│                        │   AUTONOM.  │     │AI DISCLAIM. │                  │
│                        │   RESEARCH  │     │             │                  │
│                        └─────────────┘     └─────────────┘                  │
│                                │                                               │
│                                ▼                                               │
│                        ┌─────────────┐     ┌─────────────┐                  │
│                        │  FASE 10    │────▶│  FASE 11    │                  │
│                        │   HEALTH    │     │   GOOGLE    │                  │
│                        │  DASHBOARD  │     │   TRAVEL    │                  │
│                        └─────────────┘     └─────────────┘                  │
│                                                        │                    │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Estado de Fases

| Fase | ID | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|----|--------|-------------|-----------|-------|
| FASE 1 | COP-COP-REGRESSION | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Bug corregido, test de regresión creado |
| FASE 2 | ASSET-GENERATION-BUGS | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Asset bugs corregidos |
| FASE 3 | QUALITY-IMPROVEMENTS | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Quality gates mejorados |
| FASE 4 | FEATURE-ENHANCEMENTS | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Benchmark validation |
| FASE 5 | VALIDATION-CLOSURE | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Validación transversal y cierre de proyecto |
| FASE 6 | ORCHESTRATION-V2 | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Intelligent branching, early validation |
| FASE 7 | DELIVERY-V2 | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Packaging automatizado implementado |
| FASE 8 | AUTONOMOUS-RESEARCH | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | ResearchOutput schema, scrapers, confidence scoring |
| FASE 9 | AI-DISCLAIMER | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Intelligent Disclaimer Generator v2 con improvement steps |
| FASE 10 | HEALTH-DASHBOARD | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Dashboard con Chart.js, métricas por hotel |
| **FASE 11** | GOOGLE-TRAVEL-INTEGRATION | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Google Travel scraper + Onboard enhancement + Asset Quality |

---

## Sub-Fases FASE 11

| Sub-Fase | Descripcion | Estado | Dependencias |
|----------|-------------|--------|--------------|
| 11A | Google Travel Scraper | ✅ COMPLETADA | Ninguna |
| 11B | Onboard Enhancement | ✅ COMPLETADA | 11A |
| 11C | Asset Quality Boost | ✅ COMPLETADA | 2026-03-23 | FASE 11C ejecutada. Coherence 0.87. Google Travel bloqueado en produccion (limitacion de Google). Integracion de fallback implementada. |

---

## Conflictos Potenciales de Archivos

| Fase | Archivos Principales | Fase Conflictiva | Overlap |
|------|---------------------|------------------|---------|
| FASE 1 | `modules/providers/benchmark_resolver.py` | FASE 4 | Línea 59 (B3) |
| FASE 2 | `modules/asset_generation/conditional_generator.py` | FASE 3, FASE 4 | Método generate() |
| FASE 2 | `modules/asset_generation/asset_metadata.py` | FASE 3 | Campo confidence |
| FASE 3 | `modules/asset_generation/asset_content_validator.py` | Ninguna | Solo lectura |
| FASE 4 | `modules/asset_generation/preflight_checks.py` | Ninguna | Solo lectura |
| **FASE 11** | `modules/scrapers/google_travel_scraper.py` | Nueva | Ninguno |

---

## Orden de Ejecución

1. **FASE 1** - Ejecutar primero (bugs críticos)
2. **FASE 2** - Después de FASE 1 (corrige asset bugs)
3. **FASE 3** - Después de FASE 2 (quality improvements)
4. **FASE 4** - Después de FASE 3 (feature enhancements)
5. **FASE 5-10** - Completadas previamente
6. **FASE 11A** - Google Travel Integration ✅ COMPLETADA
7. **FASE 11B** - Onboard Enhancement ✅ COMPLETADA (integración GoogleTravelScraper en AutonomousResearcher)
8. **FASE 11C** - Asset Quality Boost

---

## Criterios de Avance

| Fase | Criterio para avanzar |
|------|----------------------|
| FASE 1 → FASE 2 | `grep -rn "COP COP" modules/` = 0 Y test de regresión pasa |
| FASE 2 → FASE 3 | Asset bugs corregidos Y 2 tests nuevos pasan |
| FASE 3 → FASE 4 | Validator calibrado Y documentación actualizada |
| FASE 4 → COMPLETO | Todos los tests pasan Y CHANGELOG.md actualizado |
|| FASE 11A → 11B | GoogleTravelScraper implementado Y 5 tests pasando |
| FASE 11B → 11C | Datos onboard persistidos Y v4complete carga automaticamente |
| FASE 11C → CIERRE | 7/7 assets generados, Coherence 0.87 ✅ |

---

## Regla de Sesión Única

⚠️ **REGLA MANDATORIA - Sin excepciones**

> Una fase por sesión. No se permite ejecutar múltiples fases en una misma sesión.

| Sesión | Fase a Ejecutar |
|--------|----------------|
| Sesión 1 | FASE 1 |
| Sesión 2 | FASE 2 |
| Sesión 3 | FASE 3 |
| Sesión 4 | FASE 4 |
| Sesión 5 | FASE 5-10 (completadas) |
| Sesión 6 | FASE 11A |
| Sesión 7 | FASE 11B |
| Sesión 8 | FASE 11C |

---

## Registro de Ejecución

| Sesión | Fase | Ejecutor | Fecha | Resultado |
|--------|------|----------|-------|-----------|
| 1 | FASE 1 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 2 | FASE 7 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 3 | FASE 5 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 4 | FASE 6 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 5 | FASE 8 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 6 | FASE 9 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 7 | FASE 10 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |
| 8 | FASE 11A | Hermes CLI | 2026-03-23 | ✅ COMPLETADA (11 passed, 1 skipped) |
| 9 | FASE 11B | Hermes CLI | 2026-03-23 | ✅ COMPLETADA (16 passed, 1 skipped) |
| 10 | FASE 11C | Hermes CLI | 2026-03-23 | ✅ COMPLETADA (Coherence 0.87, Travel bloqueado por Google) |

---

## Links a Prompts

- [FASE 1: COP COP](./05-prompt-inicio-sesion-fase-1-COP-COP.md)
- [FASE 2: Asset Bugs](./05-prompt-inicio-sesion-fase-2-ASSET-BUGS.md)
- [FASE 3: Quality](./05-prompt-inicio-sesion-fase-3-QUALITY.md)
- [FASE 4: Features](./05-prompt-inicio-sesion-fase-4-FEATURES.md)
- [FASE 5: Transversal](./05-prompt-inicio-sesion-fase-5-TRANSVERSAL.md)
- [FASE 6: Orchestration v2](./05-prompt-inicio-sesion-fase-6-ORCHESTRATION-V2.md)
- [FASE 7: Delivery v2](./05-prompt-inicio-sesion-fase-7-DELIVERY-V2.md)
- [FASE 8: Autonomous Research](./05-prompt-inicio-sesion-fase-8-AUTONOMOUS-RESEARCH.md)
- [FASE 9: AI Disclaimer](./05-prompt-inicio-sesion-fase-9-AI-DISCLAIMER.md)
- [FASE 10: Health Dashboard](./05-prompt-inicio-sesion-fase-10-HEALTH-DASHBOARD.md)
- [FASE 11: Google Travel](./05-prompt-inicio-sesion-fase-11-GOOGLE-TRAVEL-INTEGRATION.md)

---

## Problemas a Resolver en FASE 11

| # | Problema | Severidad | Causa Raiz | Solucion |
|---|----------|-----------|-------------|----------|
| 1 | `Place not found in Google Places` | 🔴 CRITICAL | Places API != Travel API | Agregar Google Travel scraper |
| 2 | `optimization_guide` fallido | 🟡 MEDIUM | Datos estimados | Ejecutar onboard con datos reales |
| 3 | Crawlers IA bloqueados | 🟡 MEDIUM | Robots.txt no existe | Generar robots.txt en assets |
| 4 | Metadata por defecto | 🟡 MEDIUM | CMS defaults | Validar y corregir metadata |

---

**Última actualización**: 2026-03-23