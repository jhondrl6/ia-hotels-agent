# Plan: Refactor 4 Pilares SEO/GEO/AEO/IAO

**Proyecto**: AEO-IAO-PROGRESSION-REFACTOR
**Fecha**: 2026-04-12
**Contexto**: `.opencode/plans/context/AEO-IAO-PROGRESSION-REFACTOR.md`
**Workflow**: `.agents/workflows/phased_project_executor.md`
**Estado**: PREPARACIÓN COMPLETA — Listo para implementación

---

## Resumen

Refactor de la arquitectura de scores de visibilidad del sistema iah-cli.
El código actual trata GEO, AEO, SEO e IAO como pilares paralelos independientes con sistema dual de scoring.
El refactor redistribuye CHECKLIST_IAO a 4 pilares coherentes con progresión SEO→AEO→IAO y GEO lateral.

**Arquitectura correcta:**
```
SEO (base) → AEO (construye sobre SEO) → IAO (construye sobre AEO)
  │              │                           │
  └──── GEO (lateral, complementario) ───────┘
```

---

## Archivos del Plan

| Archivo | Descripción |
|---------|-------------|
| `context/AEO-IAO-PROGRESSION-REFACTOR.md` | Contexto completo del refactor (problema, arquitectura, APIs, decisiones) |
| `05-prompt-FASE-A.md` | Score Redistribution (base, sin dependencias) |
| `05-prompt-FASE-B.md` | AEO Real Measurement + SerpAPI |
| `05-prompt-FASE-C.md` | IAO Restoration + LLM Mention Checker |
| `05-prompt-FASE-D.md` | Package & Template Alignment |
| `05-prompt-FASE-E.md` | Voice Readiness Proxy |
| `05-prompt-FASE-F.md` | Documentation & Validation |
| `06-checklist-implementacion.md` | Checklist maestro (58 items) |
| `09-documentacion-post-proyecto.md` | Documentación incremental |
| `dependencias-fases.md` | Diagrama dependencias + tabla conflictos |
| `README.md` | Este archivo |

---

## Progreso

| Fase | Nombre | Dependencias | Estado |
|------|--------|-------------|--------|
| FASE-A | Score Redistribution | — | ⏳ Pendiente |
| FASE-B | AEO Real Measurement | FASE-A | ⏳ Pendiente |
| FASE-C | IAO Restoration + LLM Checker | FASE-B | ⏳ Pendiente |
| FASE-D | Package & Template Alignment | FASE-C | ⏳ Pendiente |
| FASE-E | Voice Readiness Proxy | FASE-A | ⏳ Pendiente |
| FASE-F | Documentation & Validation | TODAS | ⏳ Pendiente |

---

## Reglas del Proyecto

1. **Una fase por sesión** — Sin excepciones
2. **Prompts son auto-contenidos** — Cada prompt tiene todo el contexto necesario
3. **Costo API explícito** — Cada componente declara su costo mensual
4. **No romper outputs existentes** — Backward compatibility obligatoria
5. **No medición directa de voz** — Proxy measurement únicamente
6. **OpenAI siempre via OpenRouter** — Nunca SDK directo
7. **Python: `./venv/Scripts/python.exe`** — No python3, no .venv

---

## Cómo Ejecutar

Para ejecutar una fase, iniciar una nueva sesión y cargar el prompt correspondiente:

```
Lee y ejecuta: .opencode/plans/05-prompt-FASE-A.md
```

Después de completar, iniciar nueva sesión para la siguiente fase:
```
Lee y ejecuta: .opencode/plans/05-prompt-FASE-B.md
```

---

## Métricas Objetivo

| Métrica | Antes | Después |
|---------|-------|---------|
| Pilares de scoring | 3 (GEO/AEO/SEO) | 4 (SEO/GEO/AEO/IAO) |
| Sistema de scoring | Dual (CHECKLIST + 4-Pilar) | Unificado (4 checklists) |
| AEO mide | Infraestructura (schema) | Resultado (snippets) |
| IAO | Eliminado | Restaurado con LLM Checker |
| Voice Readiness | No existe | Proxy score |
| Benchmarks regionales | 3 scores | 4 scores |
| Costo API/hotel/mes | $0 | $0.20-0.50 USD |
