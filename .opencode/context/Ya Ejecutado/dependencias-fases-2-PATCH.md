# Dependencias de Fases — FASE-2-PATCH-TERMALES

```
FASE-2-PATCH-A ──→ FASE-2-PATCH-B ──→ FASE-2-PATCH-C
  (3 fixes code)     (3 fixes orch)     (v4complete + verify)
```

## Tabla de Conflictos

| Archivo | FASE-A | FASE-B | FASE-C | ¿Conflicto? |
|---------|--------|--------|--------|-------------|
| `modules/commercial_documents/v4_proposal_generator.py` | PATCH-1 | — | — | No |
| `modules/commercial_documents/coherence_validator.py` | PATCH-2 | — | — | No |
| `modules/postprocessors/content_scrubber.py` | PATCH-4 | PATCH-6 | — | ⚠️ ORDEN REQUERIDO |
| `modules/asset_generation/monthly_report_generator.py` | — | PATCH-3 | — | No |
| `modules/asset_generation/site_presence_checker.py` | — | PATCH-5 | — | No |
| `modules/quality_gates/publication_gates.py` | — | PATCH-5 | — | No |
| `main.py` (orquestador) | PATCH-2 | PATCH-3, PATCH-6 | — | ⚠️ ORDEN REQUERIDO |

**Regla de orden**: FASE-A modifica `coherence_validator.py` y `content_scrubber.py` ANTES de que FASE-B añada la regla PATCH-6 al scrubber. FASE-A toca el orquestador para PATCH-2 ANTES de que FASE-B haga PATCH-3 y PATCH-6.

## R3 Scope Evaluation

| Fase | Tareas | Comandos largos | R3 |
|------|--------|-----------------|-----|
| FASE-2-PATCH-A | 3 (PATCH-1 + PATCH-2 + PATCH-4) | 0 | ✓ (≤4) |
| FASE-2-PATCH-B | 3 (PATCH-3 + PATCH-5 + PATCH-6) | 0 | ✓ (≤4) |
| FASE-2-PATCH-C | 2 (v4complete + verify 7 metrics) | 1 (v4complete) | ✓ (≤3+1) |

## Iteration Budget por Fase

| Fase | Costo fijo | Trabajo específico | Total estimado | Presupuesto |
|------|-----------|-------------------|----------------|-------------|
| FASE-A | ~28 iter | ~20 iter (3 fixes) | ~48 | 60 ✓ |
| FASE-B | ~28 iter | ~25 iter (3 fixes + browser investigation) | ~53 | 60 ✓ |
| FASE-C | ~28 iter | ~15 iter (v4complete wait + verify) | ~43 | 60 ✓ |

## Ejecución Recomendada

1. **Sesión 1**: FASE-2-PATCH-A (prompt `05-prompt-inicio-sesion-fase-2-PATCH-A.md`)
2. **Sesión 2**: FASE-2-PATCH-B (prompt `05-prompt-inicio-sesion-fase-2-PATCH-B.md`)
3. **Sesión 3**: FASE-2-PATCH-C (prompt `05-prompt-inicio-sesion-fase-2-PATCH-C.md`)
