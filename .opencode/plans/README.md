# Plan: Brechas Dinámicas v2

## Objetivo

Hacer que el número de brechas en el diagnóstico sea dinámico (N, no siempre 4),
propagar ese número a propuesta comercial y assets, y validar con ejecución real.

## Fases

| Fase | Archivo Prompt | Estado | Descripción |
|------|---------------|--------|-------------|
| FASE-A | `05-prompt-inicio-sesion-fase-A.md` | ⬜ Pendiente | Core: _identify_brechas() dinámico |
| FASE-B | `05-prompt-inicio-sesion-fase-B.md` | ⬜ Pendiente | Templates V4+V6 dinámicos |
| FASE-C | `05-prompt-inicio-sesion-fase-C.md` | ⬜ Pendiente | Proposal Generator dinámico |
| FASE-D | `05-prompt-inicio-sesion-fase-D.md` | ⬜ Pendiente | Validación E2E |
| FASE-E | `05-prompt-inicio-sesion-fase-E.md` | ⬜ Pendiente | Ejecución real v4complete |
| FASE-F | `05-prompt-inicio-sesion-fase-F.md` | ⬜ Pendiente | Limpieza legacy |

## Dependencias

```
FASE-A → FASE-B → FASE-C → FASE-D → FASE-E
FASE-A ──────────────────────────────→ FASE-F (paralelo con B o C)
```

## Progreso

- [ ] FASE-A: Core dinámico
- [ ] FASE-B: Templates dinámicos
- [ ] FASE-C: Proposal dinámico
- [ ] FASE-D: Validación E2E
- [ ] FASE-E: Ejecución real
- [ ] FASE-F: Limpieza legacy

## Criterio de Éxito Global

1. `_identify_brechas()` retorna N brechas (0-10) sin defaults genéricos
2. Diagnóstico muestra exactamente las brechas detectadas (no siempre 4)
3. Propuesta comercial refleja las mismas N brechas con distribución proporcional
4. Assets generados cubren TODAS las brechas (no solo las top 4)
5. `v4complete` para hotelvisperas.com ejecuta sin errores con N brechas reales
6. Tests existentes pasan sin regresión
7. Cero hardcoded "4" en la cadena Diagnóstico → Propuesta → Assets
