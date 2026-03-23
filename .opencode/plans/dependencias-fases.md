# Dependencias de Fases - Corrección v4.5.6

**Proyecto**: IA Hoteles CLI - Corrección de Bugs NEVER_BLOCK v4.5.6
**Archivo**: `.opencode/plans/dependencias-fases.md`
**Versión**: 1.0.0
**Fecha creación**: 2026-03-23

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
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Estado de Fases

| Fase | ID | Estado | Fecha Inicio | Fecha Fin | Notas |
|------|----|--------|-------------|-----------|-------|
| FASE 1 | COP-COP-REGRESSION | ✅ COMPLETADA | 2026-03-23 | 2026-03-23 | Bug corregido, test de regresión creado |
| FASE 2 | ASSET-GENERATION-BUGS | ⬜ PENDIENTE | - | - | Depende de FASE 1 |
| FASE 3 | QUALITY-IMPROVEMENTS | ⬜ PENDIENTE | - | - | Depende de FASE 2 |
| FASE 4 | FEATURE-ENHANCEMENTS | ⬜ PENDIENTE | - | - | Depende de FASE 3 |
| FASE 5 | VALIDATION-CLOSURE | ⬜ PENDIENTE | - | - | Depende de FASE 4 |
| **FASE 6** | ORCHESTRATION-V2 | ⬜ PENDIENTE | - | - | Depende de FASE 5 - EVOLUCIÓN |
| **FASE 7** | DELIVERY-V2 | ⬜ PENDIENTE | - | - | Depende de FASE 6 - EVOLUCIÓN |
| **FASE 8** | AUTONOMOUS-RESEARCH | ⬜ PENDIENTE | - | - | Depende de FASE 5 - EVOLUCIÓN |
| **FASE 9** | AI-DISCLAIMER | ⬜ PENDIENTE | - | - | Depende de FASE 8 - EVOLUCIÓN |
| **FASE 10** | HEALTH-DASHBOARD | ⬜ PENDIENTE | - | - | Depende de FASE 7 - EVOLUCIÓN |

---

## Conflictos Potenciales de Archivos

| Fase | Archivos Principales | Fase Conflictiva | Overlap |
|------|---------------------|------------------|---------|
| FASE 1 | `modules/providers/benchmark_resolver.py` | FASE 4 | Línea 59 (B3) |
| FASE 2 | `modules/asset_generation/conditional_generator.py` | FASE 3, FASE 4 | Método generate() |
| FASE 2 | `modules/asset_generation/asset_metadata.py` | FASE 3 | Campo confidence |
| FASE 3 | `modules/asset_generation/asset_content_validator.py` | Ninguna | Solo lectura |
| FASE 4 | `modules/asset_generation/preflight_checks.py` | Ninguna | Solo lectura |

---

## Orden de Ejecución

1. **FASE 1** - Ejecutar primero (bugs críticos)
2. **FASE 2** - Después de FASE 1 (corrige asset bugs)
3. **FASE 3** - Después de FASE 2 (quality improvements)
4. **FASE 4** - Después de FASE 3 (feature enhancements)

---

## Criterios de Avance

| Fase | Criterio para avanzar |
|------|----------------------|
| FASE 1 → FASE 2 | `grep -rn "COP COP" modules/` = 0 Y test de regresión pasa |
| FASE 2 → FASE 3 | Asset bugs corregidos Y 2 tests nuevos pasan |
| FASE 3 → FASE 4 | Validator calibrado Y documentación actualizada |
| FASE 4 → COMPLETO | Todos los tests pasan Y CHANGELOG.md actualizado |

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

---

## Registro de Ejecución

| Sesión | Fase | Ejecutor | Fecha | Resultado |
|--------|------|----------|-------|----------|
| Sesión 1 | FASE 1 | Hermes CLI | 2026-03-23 | ✅ COMPLETADA |

---

## Links a Prompts

- [FASE 1: COP COP](./05-prompt-inicio-sesion-fase-1-COP-COP.md)
- [FASE 2: Asset Bugs](./05-prompt-inicio-sesion-fase-2-ASSET-BUGS.md)
- [FASE 3: Quality](./05-prompt-inicio-sesion-fase-3-QUALITY.md)
- [FASE 4: Features](./05-prompt-inicio-sesion-fase-4-FEATURES.md)
- [FASE 5: Transversal](./05-prompt-inicio-sesion-fase-5-TRANSVERSAL.md)
- [FASE 6: Orchestration v2](./05-prompt-inicio-sesion-fase-6-ORCHESTRATION-V2.md) ← EVOLUCIÓN
- [FASE 7: Delivery v2](./05-prompt-inicio-sesion-fase-7-DELIVERY-V2.md) ← EVOLUCIÓN
- [FASE 8: Autonomous Research](./05-prompt-inicio-sesion-fase-8-AUTONOMOUS-RESEARCH.md) ← EVOLUCIÓN
- [FASE 9: AI Disclaimer](./05-prompt-inicio-sesion-fase-9-AI-DISCLAIMER.md) ← EVOLUCIÓN
- [FASE 10: Health Dashboard](./05-prompt-inicio-sesion-fase-10-HEALTH-DASHBOARD.md) ← EVOLUCIÓN

---

**Última actualización**: 2026-03-23
