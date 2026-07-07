# Dependencias entre Fases — BUGFIX-LUXOR-2026-07-06

## Diagrama de Dependencias

```
FASE-1 (BUG-2 + BUG-1: quick wins)  ──────────┐
                                               │
FASE-2 (BUG-4a: openrouter)  ─────────────────┤  (independiente de FASE-1)
                                               │
FASE-3 (BUG-5: scrubber)  ────────────────────┤  (independiente de FASE-1 y FASE-2)
                                               │
FASE-4 (BUG-6: SPA rendering)  ───────────────┤  (independiente de FASE-1/2/3)
                                               │
FASE-5 (v4complete E2E + verificación)  ───────┤  (DEPENDIENTE de FASE-1 a FASE-4)
                                               │
FASE-RELEASE v4.60.1  ─────────────────────────┘  (DEPENDIENTE de FASE-5)
```

## Tabla de Conflictos Potenciales

| Archivo | Fases que lo modifican | Sección afectada | ¿Conflicto? | Resolución |
|---------|----------------------|------------------|-------------|------------|
| `main.py` | FASE-1 (BUG-2), FASE-3 (BUG-5) | L1942 vs L2372-2473 | NO | Secciones NO superpuestas |
| `modules/auditors/v4_comprehensive.py` | FASE-1 (BUG-1), FASE-4 (BUG-6) | L1159-1160 vs L505 | NO | Métodos distintos (`_audit_competitors` vs `_run_seo_elements_audit`) |
| `modules/auditors/llm_mention_checker.py` | FASE-2 | L239, L100 | NO | Una sola fase |
| `config/provider_registry.yaml` | FASE-2 | default_model | NO | Una sola fase |
| `modules/auditors/seo_elements_detector.py` | FASE-4 | L41-87 | NO | Una sola fase |

## Reglas de Dependencia

1. **FASE-1 a FASE-4**: Independientes entre sí. Pueden ejecutarse en cualquier orden.
2. **FASE-5**: Requiere que FASE-1 a FASE-4 estén completadas (✅). Ejecuta v4complete E2E para verificar todos los fixes.
3. **FASE-RELEASE**: Requiere que FASE-5 esté completada (✅). NO registra fases anteriores (solo sync de versiones y docs).

## Orden de Ejecución Sugerido

1. FASE-1 (quick wins — bajo riesgo, entrega valor inmediato)
2. FASE-2 (resiliencia LLM)
3. FASE-3 (higiene de pipeline)
4. FASE-4 (SPA rendering — mayor complejidad)
5. FASE-5 (verificación E2E con v4complete)
6. FASE-RELEASE (cierre y documentación)

## Estado de Fases

| Fase | Título | Estado | Cerrada | Pendiente |
|------|--------|--------|---------|-----------|
| FASE-1 | BUG-2 + BUG-1: Quick Wins | COMPLETADA | 2026-07-06 | Nada |
| FASE-2 | BUG-4a: Resiliencia LLM (openrouter) | COMPLETADA | 2026-07-06 | Nada |
| FASE-3 | BUG-5: Higiene Content Scrubber | COMPLETADA | 2026-07-06 | Nada |
| FASE-4 | BUG-6: SPA Rendering con Playwright | COMPLETADA | 2026-07-06 | Nada |
| FASE-5 | Verificación E2E v4complete | COMPLETADA | 2026-07-06 | Ninguna |
| FASE-RELEASE | Cierre y Documentación v4.60.1 | BLOQUEADA | - | Requiere FASE-5 |

## Log de Cierres de Sesión

(vacío — el agente completa al cerrar cada fase)
