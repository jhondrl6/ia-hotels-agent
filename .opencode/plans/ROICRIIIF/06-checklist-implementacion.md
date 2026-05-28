# ROICRIIIF — Checklist de Implementación

**Proyecto:** Publication Readiness Fix (post-FASE-6 blockers)
**Versión:** 4.57.0 → 4.58.0
**Contexto:** .opencode/context/ROICRIII-fase-6-resultado-y-faltantes.md

---

## Fases de Implementación

| # | Fase | Scope | Estado | Sesión |
|---|------|-------|--------|--------|
| 1 | FASE-1A | Gate Presence DIAGNÓSTICO (lectura + fix recipe) | ⬜ Pendiente | — |
| 2 | FASE-1B | Gate Presence IMPLEMENTACIÓN [delegate_task] | ✅ COMPLETED 2026-05-28 | 2026-05-28 |
|| 3 | FASE-2 | Asset Confidence Enrichment (co-bloqueante) | ✅ COMPLETED 2026-05-28 | 2026-05-28 |
| 4 | FASE-3 | Proposal Semantic Cleanup [delegate_task] | ⬜ Pendiente | — |
| 5 | FASE-4 | v4complete Hotel Castilla Real E2E [delegate_task] | ⬜ Pendiente | — |
| 6 | FASE-RELEASE-4.58.0 | Documentación oficial + version bump | ⬜ Pendiente | — |

---

## Gate de Dependencias

- [ ] FASE-1A completada antes de FASE-1B (FASE-1B ejecutó sin diagnóstico formal; esto indica que FASE-1A puede omitirse si el recipe ya fue generado en sesiones previas)
- [x] FASE-1B completada antes de FASE-2
- [x] FASE-1B + FASE-2 completadas antes de FASE-4 (co-bloqueantes resueltos: alignment 100%)
- [ ] FASE-3 puede ejecutarse en paralelo conceptual con FASE-2, pero se mantiene secuencial por convención
- [ ] TODAS las fases 1A-4 completadas antes de FASE-RELEASE

---

## Verificaciones Acumulativas

| Verificación | 1A | 1B | 2 | 3 | 4 | RELEASE |
|-------------|----|----|---|---|---|---------|
| Tests nuevos pasan | — | [x] | [x] | [ ] | — | [ ] |
| run_all_validations --quick | — | [x] | [x] | — | — | [ ] |
| dependencias-fases.md actualizado | [ ] | [x] | [x] | [ ] | [ ] | [ ] |
| log_phase_completion.py ejecutado | [ ] | [x] | [x] | [ ] | [ ] | [ ] |
| 09-documentacion actualizado | — | — | [x] | [ ] | [ ] | [ ] |
| REGISTRY.md actualizado | — | [x] | [x] | [ ] | [ ] | [ ] |
| Fix recipe creado | [ ] | — | — | — | — | — |
| Evidence preservada | — | — | — | — | [ ] | [ ] |

---

## Métricas Acumulativas

| Métrica | Inicio | 1A | 1B | 2 | 3 | 4 | RELEASE |
|---------|--------|----|----|---|---|---|---------|
| Tests totales | TBD | — | +4 | +1-2 | — | — | — |
| Proposal alignment % | 62.5% | 62.5% | 75%* | ≥87.5%* | ≥87.5% | TBD | — |
| Publication readiness | NOT_READY | — | IMPROVED* | — | — | READY* | — |
| Gates pasados | 10/11 | — | 11/11* | 11/11* | 11/11* | TBD | — |
| Version | 4.57.0 | — | — | — | — | — | 4.58.0 |

(*) Estimado — verificar con v4complete en FASE-4

---

## Issues Mapping

| Issue | Severity | Resolved In | Blocking |
|-------|----------|-------------|----------|
| GATE-PRESENCE (whatsapp not marked present_in_production) | 🔴 | FASE-1A (diagnóstico) + FASE-1B (fix) | SÍ |
| CONFIDENCE-LOW (faq_page/optimization_guide = 0.5) | 🔴 | FASE-2 | SÍ (co-bloqueante) |
| SEMANTIC-13 (artifact "13% del dolor") | 🟡 | FASE-3 | NO |

---

## RAM-Friendly Notes

- FASE-1A: usar execute_code para batch greps (reduce tool calls 5x)
- FASE-1A: read_file con offset/limit (no cargar archivos enteros)
- FASE-1B: delegate_task aísla contexto del subagente (RAM separada)
- FASE-3/4: delegate_task aísla RAM
- Fix recipe escrito por 1A → leído por 1B (no duplica contexto)
