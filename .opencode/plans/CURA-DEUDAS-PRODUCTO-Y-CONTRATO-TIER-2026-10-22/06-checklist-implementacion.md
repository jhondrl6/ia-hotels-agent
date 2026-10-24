# Checklist de Implementación — CURA-DEUDAS-PRODUCTO-Y-CONTRATO-TIER-2026-10-22

> Estado maestro de fases. Cada fase se marca ✅ solo con su checklist de prompt completo (todos los criterios) y su entrada en `docs/contributing/REGISTRY.md` escrita por esa fase. Una fase = una sesión.

| # | Fase | Complejidad | Estado | Checklist del prompt | Registro REGISTRY |
|---|------|-------------|--------|---------------------|-------------------|
| 0 | Preparación + corrección de estrategia | — | ✅ 2026-10-22 | prompts + docs corregidos | (etapa de orquestación, sin registro) |
| 1 | FASE-A — retiro de `spark` + guardián (`N1`/`N7`/`R4`) | MEDIA-ALTA | ✅ 2026-10-22 | [x] checklist del prompt cerrado | [x] registrado con `log_phase_completion.py` |
| 2 | FASE-B — ítem A (2 claims, propuesta y diagnóstico) | ALTA | ✅ 2026-10-23 | [x] checklist del prompt cerrado | [x] registrado con `log_phase_completion.py` |
| 3 | FASE-C — ítem C (`conditional_reason`; `P6.5` intacta) | MEDIA | ✅ 2026-10-23 | [x] checklist del prompt cerrado | [x] registrado con `log_phase_completion.py` |
| 4 | FASE-D — contrato GBP en ambos caminos | ALTA | ✅ 2026-10-23 | [x] checklist del prompt cerrado | [x] registrado con `log_phase_completion.py` |
| 5 | FASE-E — lector único y cinco tablas | ALTA | ✅ 2026-10-23 | [x] checklist del prompt cerrado (AC4; M1/M2/M3 en evidencia; `--quick` 13/13; presupuesto excedido y declarado) | [x] registrado con `log_phase_completion.py` |
| 6 | FASE-F — umbrales por semántica | MEDIA | ⏳ | [ ] | [ ] |
| 7 | FASE-H1 — `D16` `/90` y `D24` stub retirado | MEDIA | ⏳ | [ ] | [ ] |
| 8 | FASE-H2 — `D18`/`D22`/`D23`/`D20` | BAJA | ⏳ | [ ] | [ ] |
| 9 | FASE-E2E-PRE — ensayo determinista | MEDIA | ⏳ | [ ] | [ ] |
| 10 | FASE-E2E — v4complete Don Alfonso | MEDIA | ⏳ | [ ] | [ ] |
| 11 | FASE-VERIFY — certificación AC1–AC8 | MEDIA | ⏳ | [ ] | [ ] |
| 12 | FASE-RELEASE-4.82.0 — cierre | BAJA | ⏳ | [ ] | [ ] |

**Regla de dependencia**: FASE-RELEASE solo se ejecuta con todas las fases previas (incluida FASE-VERIFY) en ✅. Si una fase cierra `⏳ INCOMPLETA`, se retoma desde su checkpoint en sesión nueva antes de abrir la siguiente.

**Reglas de la corrección**: `spark` retirado; `D21`/`P6.5` fuera; `D26` diferida; `D16` y `D24` con decisión registrada; E2E-PRE obligatorio antes de la corrida pagada.
