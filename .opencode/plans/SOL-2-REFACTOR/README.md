---
description: Plan maestro SOL-2 Asset Alignment Refactor
version: 1.0.0
---

# SOL-2: Asset Alignment Refactor

## Contexto

Basado en el documento `.opencode/context/05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md`, este plan aborda las discrepancias entre `coherence_validator` y `proposal_asset_alignment_gate`, elimina componentes fantasma, y unifica la validación de assets.

## Estructura del Plan

```
.opencode/plans/SOL-2-REFACTOR/
├── README.md                              <- Este archivo
├── dependencias-fases.md                  <- Diagrama y conflictos
├── 06-checklist-implementacion.md         <- Checklist maestro
├── 09-documentacion-post-proyecto.md      <- Docs incremental
├── 05-prompt-inicio-sesion-fase-SOL2-A.md <- Ghost Ref Cleanup
├── 05-prompt-inicio-sesion-fase-SOL2-B.md <- Asset Alignment
├── 05-prompt-inicio-sesion-fase-SOL2-C.md <- v4complete E2E
├── 05-prompt-inicio-sesion-fase-SOL2-D.md <- Phantom Fields
└── 05-prompt-inicio-sesion-fase-SOL2-RELEASE.md <- Release
```

## Fases

| # | Fase | Descripción | Comando largo |
|---|------|-------------|---------------|
| 1 | FASE-SOL2-A | Ghost Ref & SitePresence Cleanup | No |
| 2 | FASE-SOL2-B | Asset Alignment & Gate Unification | No |
| 3 | FASE-SOL2-C | v4complete E2E Verification (Termales) | **SÍ** |
| 4 | FASE-SOL2-D | Phantom Fields & Coherence Consistency | No |
| 5 | FASE-SOL2-RELEASE | Documentación Cascade & Version Sync | No |

## Reglas del Workflow

- **1 fase por sesión** — sin excepciones
- **Máximo 60 iteraciones** por fase
- **FASE-SOL2-C** contiene el único comando largo (v4complete)
- **FASE-RELEASE** solo se ejecuta cuando A, B, C, D están ✅

## Estado Actual

| Fase | Estado |
|------|--------|
| Preparación (diseño plan) | ✅ Completada (esta sesión) |
| FASE-SOL2-A | ⏳ Pendiente |
| FASE-SOL2-B | ⏳ Pendiente |
| FASE-SOL2-C | ⏳ Pendiente |
| FASE-SOL2-D | ⏳ Pendiente |
| FASE-SOL2-RELEASE | ⏳ Pendiente |

## Evidencia de Ejecución v4complete

- **Ubicación**: `evidence/FASE-SOL2-C/`
- **Análisis**: `evidence/FASE-SOL2-C/analisis_ejecucion.md`
- **Resultado**: Coherence 0.89, 6/9 PASSED, 3 WARNING, missing_count=3 confirmado
