# Plan: Rediseño Motor Financiero (Opción C)

**Proyecto**: iah-cli — Motor de Cuantificación Financiera v2
**Fecha**: 2026-04-10
**Estado**: Preparación completa — listo para ejecución por fases

---

## Resumen

Rediseño completo del motor financiero para que cada costo en COP sea:
1. Rastreable a una fuente
2. Proporcional (pesos que suman 100%)
3. Honestamente etiquetado (VERIFIED vs ESTIMATED)
4. Basado en un hecho verificable cuando sea posible

## Contexto

- Investigación completa: `.opencode/plans/context/diagnostico_3132_cop_investigacion.md` (766 líneas)
- Decisión: Opción C — Rediseño completo (3 capas: presentación + pesos + conceptual)
- Justificación: "Las soluciones a medias no son soluciones, es aplazar el problema."
- Promesa del producto (README línea 63): "asigna un costo en COP a cada brecha detectada"

## Fases

### Ciclo 1: Rediseño Motor Financiero (COMPLETADO)

| Fase | Archivo prompt | Descripcion |
|------|---------------|-------------|
| A | `05-prompt-inicio-sesion-fase-A.md` | Data Structures + FinancialBreakdown |
| B | `05-prompt-inicio-sesion-fase-B.md` | ScenarioCalculator narrativa por capas |
| C | `05-prompt-inicio-sesion-fase-C.md` | Pesos normalizados + DynamicImpact |
| D | `05-prompt-inicio-sesion-fase-D.md` | Scraper→ADR conexion |
| E | `05-prompt-inicio-sesion-fase-E.md` | Consumidores (proposal, coherence, asset) |
| F | `05-prompt-inicio-sesion-fase-F.md` | Template + Evidence Tiers |
| G | `05-prompt-inicio-sesion-fase-G.md` | Integracion main.py + E2E |
| H | `05-prompt-inicio-sesion-fase-H.md` | RegionalADRResolver SHADOW |

### Ciclo 2: Causa Raiz — Datos No Verificables (PENDIENTE)

| Fase | Archivo prompt | Descripcion | Paralelizable |
|------|---------------|-------------|---------------|
| I | `05-prompt-inicio-sesion-fase-I.md` | Activar RegionalADRResolver por regiones validadas | SI (con J) |
| J | `05-prompt-inicio-sesion-fase-J.md` | NoDefaultsValidator source-aware + template honesto | SI (con I) |
| K | `05-prompt-inicio-sesion-fase-K.md` | Unificar camino dual + fix optimista negativo | NO (req I+J) |

## Archivos de Soporte

| Archivo | Descripción |
|---------|-------------|
| `dependencias-fases.md` | Diagrama de dependencias y conflictos |
| `06-checklist-implementacion.md` | Estado de cada fase |
| `09-documentacion-post-proyecto.md` | Documentación incremental |

## Progreso

### Ciclo 1 (COMPLETADO):
```
[A] ✅ → [B] ✅ → [E] ✅ → [F] ✅ → [G] ✅
               ↗                ↑
       [C] ✅ ──────────────┘
       [D] ✅ ─────────────────────→ [G]
[H] ✅ (SHADOW, NO promovido a ACTIVE)
```

### Ciclo 2 (PENDIENTE):
```
[I] ⬜ ──┐
         ├──→ [K] ⬜ → v4complete validacion final
[J] ⬜ ──┘

⬜ = Pendiente
🔄 = En progreso
✅ = Completada

FASE-I + FASE-J → paralelizables via subagentes (delegate_task)
FASE-K → requiere I + J completadas
```
