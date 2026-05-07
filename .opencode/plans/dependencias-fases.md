# Dependencias de Fases

> Plan: PROPOSAL-COMERCIAL-FIX v1.0.0

```
FASE-PROP-A  -->  FASE-PROP-B  -->  FASE-PROP-C  -->  FASE-PROP-D  -->  FASE-PROP-E  -->  FASE-PROP-F  -->  FASE-PROP-G
     |                  |                |                |                |                |                |
   [DONE]            [DONE]          [DONE]           [DONE]           [DONE]          [DONE]           [DONE]

FASE-PROP-G  -->  FASE-RELEASE-4.41.0
     |                  |
   [DONE]            [DONE]
```

## Conflictos de Archivos

|||| Archivo | FASE-PROP-A | FASE-PROP-B | FASE-PROP-C | FASE-PROP-D | FASE-PROP-E | FASE-PROP-F | FASE-PROP-G | Conflicto |
||---------|-------------|-------------|-------------|-------------|-------------|-------------|-------------|-----------|
||| main.py | Modificación (pipeline timing) | — | — | — | — | — | — | No |
||| v4_diagnostic_generator.py | Modificación | — | — | — | — | — | — | No |
||| diagnostico_v6_template.md | Modificación | — | — | — | — | — | — | No |
||| v4_proposal_generator.py | — | Modificación | Modificación | — | — | Modificación | — | No (tareas diferentes) |
||| propuesta_v6_template.md | — | — | Modificación | — | — | Modificación | — | No |
||| pain_solution_mapper.py | — | — | — | Modificación | — | — | — | No |
||| asset_catalog.py | — | — | — | Modificación | — | — | — | No |
||| conditional_generator.py | — | — | — | Modificación | — | — | — | No |
||| asset_diagnostic_linker.py | — | — | — | Modificación | — | — | — | No |
||| site_presence_checker.py | — | — | — | Modificación | — | — | — | No |

## Estado

|||| Fase | Estado | Notas |
|||------|--------|-------|
|||| FASE-PROP-A | ✅ Completada | Unificación de Coherence Score — pipeline timing + fallback eliminado |
|||| FASE-PROP-B | ✅ Completada | WhatsApp Conflict Status en Propuesta |
|||| FASE-PROP-C | ✅ Completada | Proyecciones financieras transparentes — pain_ratio_note explica ambos descuentos |
|||| FASE-PROP-D | ✅ Completada | Google Maps asset: eliminar promesa falsa — geo_playbook deprecated, redundante con delivery GEO |
|||| FASE-PROP-E | ✅ Completada | SEO/AEO plan específico por score — priorización dinámica en planes 7/30 días |
||||| FASE-PROP-F | ✅ Completada | Tier C — Advertencia en Propuesta |
||||| FASE-PROP-G | ✅ Completada | Sobrescritura de evidencia: JSONs persisten por hotel+timestamp |
| FASE-RELEASE-4.41.0 | ✅ Completada | Documentación y version bump — CHANGELOG, GUIA_TECNICA, REGISTRY, VERSION sync |
