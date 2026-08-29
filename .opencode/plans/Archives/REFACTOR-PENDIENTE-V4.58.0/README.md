# Plan de Refactorización — Pendiente v4.58.0

## Estado General

| Aspecto | Valor |
|---------|-------|
| Plan | ⚪ Preparación |
| Fases totales | 10 (0, 1A, 1B, 2, 3, 4, 5, 6, 7, RELEASE) |
| Fases completadas | 1/10 (FASE-6 ejecutada) |
| Hotel verificación | Hotel Castilla Real |
| v4complete único | FASE-6 |

## Índice de Fases

| Fase | ID | Título | Complejidad | Delegate | Sesión |
|------|-----|--------|-------------|----------|--------|
| 0 | FASE-0 | Verificación y Preparación | BAJA | ✅ | 1 |
| 1A | FASE-1A | IMP-03 (CAPEX) + F7 (Gate) | MEDIA | ✅ | 2 |
| 1B | FASE-1B | F5 (ADR checklist bug) | BAJA | ✅ | 3 |
| 2 | FASE-2 | MIN-02 (ADR evidenciado) | **ALTA** | ❌ | 4 |
| 3 | FASE-3 | MIN-01 (Status Quo) | MEDIA | ✅ | 5 |
| 4 | FASE-4 | MIN-03 (Closing pitch) | MEDIA | ✅ | 6 |
| 5 | FASE-5 | Limpieza dead code | BAJA | ✅ | 7 |
| 6 | FASE-6 | v4complete E2E | MEDIA | ✅ | 8 |
| 7 | FASE-7 | ADR audit status | BAJA | ❌ | 9 |
| — | RELEASE | Docs cascade | MEDIA | ❌ | 10 |

## Convenciones

- `05-prompt-inicio-sesion-fase-{ID}.md` — Prompt completo para una sesión (1 fase = 1 sesión)
- `06-checklist-implementacion.md` — Checklist maestro con estado de todas las fases
- `dependencias-fases.md` — Diagrama de dependencias y tabla de conflictos
- `09-documentacion-post-proyecto.md` — Plan de documentación incremental

## Reglas de Ejecución

1. **Una fase por sesión** (R1). Sin excepciones.
2. **Máximo 60 iteraciones** por fase (R2).
3. **Máximo 4 tareas + 0 comandos largos** por fase (R3).
4. Al completar una fase: actualizar `06-checklist-implementacion.md` inmediatamente.
5. **FASE-2 NO delegar** — complejidad alta requiere razonamiento iterativo.
6. **FASE-7 NO delegar** — investigación directa más eficiente que subagent overhead.
7. **v4complete único** en FASE-6 — no ejecutar en fases anteriores.

## Cómo Iniciar

Copiar y pegar en la siguiente sesión:

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-0.md
```

Cada prompt de fase incluye instrucciones para continuar con la siguiente.

## Baseline de Comparación

| Métrica | Valor Pre-Fix |
|---------|---------------|
| Coherence score | 0.83 |
| Publication Gates | 9/11 |
| Pain ledger entries | 11 |
| Assets generated | 12 |
| tier_c_onboarding | PASS |
| Blocking issues | None |

**Esperado post-fix:** 11/11 gates, coherence ≥0.85, todos los fixes visibles en output.
