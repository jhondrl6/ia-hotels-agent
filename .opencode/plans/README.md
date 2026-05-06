# Planes de Intervencion — iah-cli

## Indice de Planes Activos

| Plan | Estado | Fases | Descripcion |
|------|--------|-------|-------------|
| REFACTOR-ONBOARDING-CTA | 🟡 Preparacion | 3 (A, B, C) | Refactoriza el CTA de onboarding en diagnostico Tier C para listar explicitamente los 4 datos requeridos. Verificado con v4complete en Hotel Castilla Real. |

## Convenciones

- `05-prompt-inicio-sesion-fase-*.md` — Prompt completo para una sesion de agente (1 fase = 1 sesion)
- `06-checklist-implementacion.md` — Checklist maestro con estado de todas las fases
- `dependencias-fases.md` — Diagrama de dependencias y tabla de conflictos
- `09-documentacion-post-proyecto.md` — Plan de documentacion incremental

## Reglas de Ejecucion

1. **Una fase por sesion** (R1). Sin excepciones.
2. **Maximo 60 iteraciones** por fase (R2).
3. **Maximo 4 tareas + 0 comandos largos** por fase (R3).
4. Al completar una fase: ejecutar `log_phase_completion.py` inmediatamente.
