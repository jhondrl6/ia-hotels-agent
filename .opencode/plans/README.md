# PLAN MAESTRO: BRECHAS-DINAMICAS

**ID**: BRECHAS-DINAMICAS
**Fecha**: 2026-04-08
**Estado**: PREPARACION

## Objetivo

Eliminar el hardcode "LAS 4 BRECHAS" del pipeline de diagnóstico para que el documento muestre TODAS las brechas detectadas (0-10) dinámicamente, sin desconectar la cadena diagnóstico → propuesta comercial → assets → coherencia.

## Progreso

| Fase | Estado | Descripción |
|------|--------|-------------|
| FASE-A | ✅ Completada | Templates dinámicos (V4 + V6) |
| FASE-B | ⬜ Pendiente | Generator dinámico (`_prepare_template_data` + `_inject_brecha_scores`) |
| FASE-C | ⬜ Pendiente | OpportunityScorer — completar mappings faltantes |
| FASE-D | ⬜ Pendiente | PainSolutionMapper — fix duplicate + verificar cadena coherencia |
| FASE-E | ⬜ Pendiente | Validación v4complete amaziliahotel.com + análisis de resultados |

## Dependencias

```
FASE-A ──→ FASE-B ──→ FASE-C ──→ FASE-D ──→ FASE-E
(templates) (generator)  (scorer)   (mapper)    (validacion)
```

FASE-E requiere que A, B, C, D estén completas para ejecutar v4complete correctamente.

## Convención

- Una fase por sesión. Sin excepciones.
- Cada fase termina con `python scripts/log_phase_completion.py`.
- Documentación incremental en `09-documentacion-post-proyecto.md`.
