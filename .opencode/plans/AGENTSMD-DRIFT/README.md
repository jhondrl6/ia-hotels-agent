# AGENTSMD-DRIFT — Plan de Refactorización

**Creado:** 2026-05-26
**Contexto:** `.opencode/context/AGENTSMD-DRIFT-CONTEXT.md` (v4, validada)
**ROADMAP:** FASE A-01 — "AGENTS.md auditado como contexto primario agente"
**Versión actual:** v4.48.0 (PIPELINE-FIX)
**Versión target:** v4.49.0

---

## Objetivo

Corregir el drift factual en `AGENTS.md` (4 secciones desactualizadas respecto al código vivo y ROADMAP.md), implementar un gate automatizado que prevenga drift futuro, e integrarlo al flujo post-fase. Todo culmina con una ejecución E2E de v4complete sobre Hotel Castilla Real.

## Arquitectura

```
Solución 1 (editorial)        Solución 2 (script)        Solución 4 (proceso)
─────────────────────        ──────────────────        ─────────────────────
AGENTS.md corregido    →    validate_agents_md.py  →   CONTRIBUTING.md
(9 pasos, ~6 edits)         (6 checks automáticos)      (post-phase hook)
                                     │
                                     └── pre-commit: agent-ecosystem
```

## Fases (R3-compliant: ≤4 tareas + 0 largos, o ≤3 + 1 largo)

| Fase | Descripción | Tareas | Largo | Depende |
|------|------------|--------|-------|---------|
| **A-01a** | Corrección one-shot AGENTS.md (Solución 1) | 4 | 0 | — |
| **A-01b** | validate_agents_md.py + integración (Solución 2+4) | 4 | 0 | A-01a ✅ |
| **A-01c** | v4complete Hotel Castilla Real | 3 | 1 | A-01b |
| **RELEASE** | Cierre documental v4.49.0 | 4 | 0 | A-01a+b+c |

## Archivos del plan

| Archivo | Contenido |
|---------|-----------|
| `README.md` | Este documento |
| `dependencias-fases.md` | Grafo de dependencias y conflictos |
| `06-checklist-implementacion.md` | Tracker maestro |
| `09-documentacion-post-proyecto.md` | Acumulador de docs |
| `05-prompt-inicio-sesion-fase-A-01a.md` | Prompt fase A-01a |
| `05-prompt-inicio-sesion-fase-A-01b.md` | Prompt fase A-01b |
| `05-prompt-inicio-sesion-fase-A-01c.md` | Prompt fase A-01c (contiene v4complete) |
| `05-prompt-inicio-sesion-fase-RELEASE.md` | Prompt fase RELEASE v4.49.0 |

## Reglas del plan

1. **1 fase por sesión** (R1). Cada prompt se ejecuta en una sesión fresca del agente.
2. **Máx 60 iteraciones por fase** (R2). El agotamiento se maneja con checkpoint + evidencia.
3. **Cada fase ejecuta `log_phase_completion.py`** al terminar (no delegar a RELEASE).
4. **RELEASE es doc-only**: no modifica código fuente.
5. **v4complete genera evidencia proactiva** antes de verificar output.
