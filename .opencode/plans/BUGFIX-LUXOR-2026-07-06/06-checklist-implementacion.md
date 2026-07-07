# Checklist Maestro de Implementación — BUGFIX-LUXOR-2026-07-06

## Estado de Fases

| Fase | Título | Estado | Sesión | Tests | log_phase |
|------|--------|--------|---------|-------|-----------|
| FASE-1 | BUG-2 + BUG-1: Quick Wins | ✅ COMPLETADA | 2026-07-06 | 39/39 (4 nuevos) | ✅ |
| FASE-2 | BUG-4a: Resiliencia LLM | ✅ COMPLETADA | 2026-07-06 | 4/4 (4 nuevos) | ✅ |
| FASE-3 | BUG-5: Higiene Scrubber | ✅ COMPLETADA | 2026-07-06 | 24/24 (0 nuevos) | ✅ |
| FASE-4 | BUG-6: SPA Rendering | ✅ COMPLETADA | 2026-07-06 | 16/16 (7 nuevos) | ✅ |
| FASE-5 | Verificación E2E | ✅ COMPLETADA | 2026-07-06 | - | ✅ |
| FASE-RELEASE | Cierre v4.60.1 | 🔒 BLOQUEADA | - | - | - |

## Dependencias

- FASE-1 a FASE-4: Independientes (cualquier orden)
- FASE-5: Requiere FASE-1 a FASE-4 ✅
- FASE-RELEASE: Requiere FASE-5 ✅

## Bugs Cubiertos

| Bug | Fase | Estado |
|-----|------|--------|
| BUG-1 (lat/lng 0.0) | FASE-1 | ✅ |
| BUG-2 (calc_result) | FASE-1 | ✅ |
| BUG-4a (openrouter 404) | FASE-2 | ✅ |
| BUG-4b (gemini 403) | FUERA DE PLAN | N/A (acción usuario) |
| BUG-5 (scrubber SKIP) | FASE-3 | ✅ |
| BUG-6 (SPA OG tags) | FASE-4 | ✅ |

## Métricas Acumulativas

| Métrica | Valor Base (v4.60.0) | Valor Post-Fix | Fase |
|---------|---------------------|----------------|------|
| Coherence score | 0.83 (Castilla Real) | [pendiente] | FASE-5 |
| Publication Gates | 9/11 | [pendiente] | FASE-5 |
| Tests nuevos | 0 | 4 | FASE-2 |
| Regresiones | 0 | [pendiente] | FASE-5 |

## Leyenda

- ⬜ NO INICIADA
- 🔄 EN CURSO
- ✅ COMPLETADA
- ⏳ INCOMPLETA (agotamiento)
- 🔒 BLOQUEADA
- ❌ CANCELADA
