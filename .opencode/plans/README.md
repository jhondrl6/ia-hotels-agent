# Plan: Brecha Architectural Fix

**Proyecto**: Eliminar gap entre detección de brechas (diagnóstico) y presentación (propuesta)
**Versión Base**: v4.25.3
**Versión Target**: v4.26.0
**Creado**: 2026-04-10
**Estado**: 🔲 PREPARACIÓN COMPLETA — Listo para implementación por fases

---

## Resumen del Problema

El diagnóstico detecta brechas reales con impactos específicos (0.30, 0.25, etc.) pero la propuesta usa una distribución fija 40/30/20/10. Esto produce:

1. **Phantom costs**: Brechas inexistentes con valores COP reales
2. **Costos no proporcionales**: No reflejan la severidad real de cada problema
3. **Dual source conflict**: Dos sistemas sobrescriben las mismas variables
4. **Performance**: _identify_brechas calculado 9 veces innecesariamente
5. **Deuda técnica**: Código duplicado en data_structures.py

---

## Estructura del Plan

```
.opencode/plans/
├── README.md                              ← ESTE ARCHIVO
├── dependencias-fases.md                  ← Diagrama y conflictos
├── 05-prompt-inicio-sesion-fase-F.md      ← Phantom Cost Fix
├── 05-prompt-inicio-sesion-fase-G.md      ← Dual Source Resolution
├── 05-prompt-inicio-sesion-fase-H.md      ← Cache + Cleanup
├── 05-prompt-inicio-sesion-fase-I.md      ← Deduplication
├── 05-prompt-inicio-sesion-fase-J.md      ← E2E Validation + Release
├── 06-checklist-implementacion.md         ← Checklist maestro
├── 09-documentacion-post-proyecto.md      ← Docs incrementales
└── context/
    └── gap-arquitectonico-propuesta-v6-brechas.md  ← Contexto original
```

---

## Fases

| # | ID | Descripción | Prioridad | Tests | Archivo |
|---|------|-------------|-----------|-------|---------|
| 1 | FASE-F | Phantom Cost Fix + Dead Code | CRÍTICA | 5 | `05-prompt-fase-F.md` |
| 2 | FASE-G | Dual Source Conflict + Impactos Reales | ALTA | 5 | `05-prompt-fase-G.md` |
| 3 | FASE-H | Cache Performance + Cleanup | MEDIA | 4 | `05-prompt-fase-H.md` |
| 4 | FASE-I | data_structures Deduplication | MEDIA | 4 | `05-prompt-fase-I.md` |
| 5 | FASE-J | E2E Validation + Release | ALTA | E2E | `05-prompt-fase-J.md` |

**Total**: 5 sesiones de implementación + 18 tests nuevos + 1 release

---

## Progreso

| Fase | Estado | Fecha | Commit |
|------|--------|-------|--------|
| FASE-F | 🔲 Pendiente | — | — |
| FASE-G | 🔲 Pendiente | — | — |
| FASE-H | 🔲 Pendiente | — | — |
| FASE-I | 🔲 Pendiente | — | — |
| FASE-J | 🔲 Pendiente | — | — |
| RELEASE-4.26.0 | 🔲 Pendiente | — | — |

---

## Archivos a Modificar (resumen)

| Archivo | Fases | Líneas Clave |
|---------|-------|-------------|
| `v4_proposal_generator.py` | F, G | 538-546 (F), _prepare_template_data (G) |
| `v4_diagnostic_generator.py` | G, H | 510-521 vs 586 (G), 1767-1923 (H) |
| `data_structures.py` | G, I | DiagnosticSummary (G), Scenario+funcs (I) |
| `templates/propuesta_v4_template.md` | F (si aplica) | — |

---

## Validación Final

Ejecución E2E con `v4complete --url https://amaziliahotel.com` al final de FASE-J para verificar que todas las correcciones funcionan integradas. Baseline previo: 6 brechas, coherence 0.84, READY.
