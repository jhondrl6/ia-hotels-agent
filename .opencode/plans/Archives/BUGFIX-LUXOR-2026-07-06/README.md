# Plan: BUGFIX-LUXOR-2026-07-06 v4.60.1

## Resumen

Corrección de 5 bugs detectados en ejecución v4complete de Luxorhotel (motor v4.60.0), no relacionados con onboarding. Los bugs se agrupan por complejidad y riesgo en 5 fases + 1 release.

## Bugs Cubiertos

| Bug | Descripción | Prioridad | Fase | ¿En plan? |
|-----|-------------|-----------|------|-----------|
| BUG-1 | lat:0.0, lng:0.0 en `_audit_competitors` | P1 Alta | FASE-1 | SÍ |
| BUG-2 | `calc_result` UnboundLocalError en FASE-K | P3 Baja | FASE-1 | SÍ |
| BUG-4a | openrouter 404 — modelo hardcoded | P2 Media | FASE-2 | SÍ |
| BUG-4b | gemini 403 — API key ausente | P2 Media | — | NO (acción usuario) |
| BUG-5 | Content Scrubber bypass en FASE 3.6 | P3 Baja | FASE-3 | SÍ |
| BUG-6 | OG no detectado — sitio es SPA | P2 Media | FASE-4 | SÍ |

## Estructura de Fases

| Fase | Título | Bugs | Complejidad | Sesión |
|------|--------|------|-------------|--------|
| FASE-1 | Quick Wins (BUG-2 + BUG-1) | BUG-2, BUG-1 | ⭐ Baja | Nueva |
| FASE-2 | Resiliencia LLM (openrouter) | BUG-4a | ⭐⭐ Media | Nueva |
| FASE-3 | Higiene Content Scrubber | BUG-5 | ⭐⭐ Media | Nueva |
| FASE-4 | SPA Rendering con Playwright | BUG-6 | ⭐⭐⭐ Alta | Nueva |
| FASE-5 | Verificación E2E v4complete | Todos | ⭐⭐ Media | Nueva |
| FASE-RELEASE | Cierre y Documentación v4.60.1 | — | ⭐ Baja | Nueva |

## Archivos del Plan

- `01-plan-maestro.md` — Plan maestro con matriz de dependencias y métricas
- `dependencias-fases.md` — Diagrama de dependencias y conflictos de archivos
- `05-prompt-inicio-sesion-fase-1.md` — Prompt FASE-1 (BUG-2 + BUG-1 quick wins)
- `05-prompt-inicio-sesion-fase-2.md` — Prompt FASE-2 (BUG-4a openrouter)
- `05-prompt-inicio-sesion-fase-3.md` — Prompt FASE-3 (BUG-5 scrubber)
- `05-prompt-inicio-sesion-fase-4.md` — Prompt FASE-4 (BUG-6 SPA rendering)
- `05-prompt-inicio-sesion-fase-5.md` — Prompt FASE-5 (verificación E2E)
- `05-prompt-inicio-sesion-fase-RELEASE.md` — Prompt FASE-RELEASE (cierre v4.60.1)
- `06-checklist-implementacion.md` — Checklist maestro de estado de fases
- `09-documentacion-post-proyecto.md` — Acumulador de datos para FASE-RELEASE

## Orden de Ejecución

1. FASE-1 (quick wins — bajo riesgo)
2. FASE-2 (resiliencia LLM)
3. FASE-3 (higiene pipeline)
4. FASE-4 (SPA rendering — mayor complejidad)
5. FASE-5 (verificación E2E con v4complete)
6. FASE-RELEASE (cierre y documentación)

## Reglas del Workflow

- **R1**: 1 fase por sesión
- **R2**: Max 60 iteraciones por fase
- **R3**: Max 4 tareas o 3+1 comando largo por fase
- Cada fase ejecuta `log_phase_completion.py` al completar
- FASE-RELEASE NO registra fases anteriores (solo sync)
- Protocolo de evidencia proactiva obligatorio post-v4complete (FASE-5)
