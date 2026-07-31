# Plan Maestro: DT-4 Residual Fixes — Post-Release v4.65.0

> **Versión objetivo**: v4.66.0
> **Hotel de evidencia**: Zi One Luxury — https://zione.co/
> **Contexto fuente**: `.opencode/context/CONTEXT-DT4-RESIDUAL-FIXES.md`
> **Workflow**: `.agents/workflows/phased_project_executor.md` v2.13.0
> **Regla**: 1 fase por sesión. Máximo 60 iteraciones por fase.
> **Creado**: 2026-07-27

---

## 0. Resumen Ejecutivo

El contexto DT4-RESIDUAL-FIXES validó 7 hallazgos contra el código vivo de v4.65.0:

| Hallazgo | Severidad | Estado | Acción |
|----------|-----------|--------|--------|
| DT4-R1 (MAPPED_TO_SERVICE ausente) | — | **REFUTADO** | No implementar. Ya existe en `_JUSTIFIED_STATUSES` |
| **Causa real** (pain_ledger_resolved no inyectado) | **CRÍTICO** | **NUEVO** | Corregir contrato AssessmentPayload → coverage gate |
| DT4-R2 (SitePresence boost no cableado) | ALTA | CONFIRMADO | Normalizar + propagar a 3 call sites |
| DT4-N1 (Shapes incompatibles SitePresenceReport) | MEDIA | CONFIRMADO | Adaptador canónico dataclass↔dict↔enum |
| DT4-N2 (SitePresence calculado 4+ veces) | MEDIA | CONFIRMADO | Computar una vez, propagar snapshot |
| DT4-N3 (Gates mutan assessment, doble ejecución) | MEDIA | CONFIRMADO | Idempotencia: una ejecución, sin mutaciones |
| DT4-N4 (Coherence score sin fuente única) | MEDIA | CONFIRMADO | `final_coherence_report` como fuente canónica |
| DT4-N5 (Alignment inconsistente pub vs delivery) | BAJA | CONFIRMADO | DTO canónico compartido |
| DT4-N6 (CG-ROI-NEGATIVE bloquea Zi One) | — | CONFIRMADO | Decisión comercial separada, no técnica |
| DT4-N7 (Drift documental REGISTRY + DOMAIN_PRIMER) | BAJA | CONFIRMADO | Corregir en FASE-RELEASE |

## 1. Arquitectura del Plan

```
FASE-1 (DT4-R1-CONTRACT)          FASE-2 (DT4-R2-SITE-PRESENCE)  ★ MAYOR COMPLEJIDAD
├── AssessmentPayload.pain_ledger  ├── Canonical SitePresence dict
│   _resolved                     ├── Adapter dataclass↔dict↔enum
├── main.py carga resolved         ├── Wire 3 CoherenceValidator calls
├── Builder.with_resolved_...()    ├── Compute once, propagate snapshot
└── Integration test               └── Eliminate fake reconstructions
         │                                    │
         │                                    └──────────┐
         │                                               │
         ▼                                               ▼
FASE-5 (DT4-N3-GATE-IDEMPOTENCY)           FASE-3 (DT4-N4-COHERENCE)
├── Assessment completo antes gates        ├── final_coherence_report
├── Una ejecución, sin mutaciones          ├── Consumers unificados
├── Readiness derivada de resultados       ├── Verify weighted formula
└── Tests                                  └── Eliminate pre/post mixing
         │ (requiere FASE-2)                    │
         │        FASE-4 (DT4-N5-ALIGNMENT)   │
         │        ├── Canonical alignment DTO │
         │        ├── Shared pub+delivery     │
         │        └── Semantic equality test  │
         │                    │               │
         └────────────────────┼───────────────┘
                              │
                              ▼
                    FASE-6 (E2E-ZIONE)
                    ├── v4complete Zi One [SUBAGENTE]
                    ├── Verify 14 criterios
                    └── Post-implementation analysis
                              │
                              ▼
                    FASE-RELEASE-v4.66.0
                    ├── Version bump + sync
                    ├── CHANGELOG + GUIA_TECNICA
                    └── Validaciones finales
```

## 2. Complejidad Técnica por Fase

| Fase | Complejidad | Razón | Riesgos |
|------|-------------|-------|---------|
| FASE-1 | MEDIA | 4 archivos, contrato dataclass | Regresión en consumers de AssessmentPayload |
| **FASE-2** | **ALTA ★** | **Diseño arquitectónico + adapter pattern + 3 call sites + 4 redundancias** | **Shape resolution, timing pre/post, budget (estimado 67-95 iters en 60-max — riesgo de overflow)** |
| FASE-3 | MEDIA | Refactor score sources, 3 consumers | Score drift entre pre/post |
| FASE-4 | BAJA | DTO + 2 consumers | Diferencia semántica 5/7 vs 7/7 |
|| FASE-5 | MEDIA | Double-execution path, mutations | Orden de gates, idempotencia | ✅ COMPLETADA | 2026-07-27 |
| FASE-6 | MEDIA | v4complete + verificación 14 criterios | Timeout subagente, CG-ROI-NEGATIVE |
| RELEASE | BAJA | Docs + scripts, delegable | README.md stale counts |

### ★ FASE-2 es la de mayor complejidad técnica porque:

1. **Decisión arquitectónica**: diseñar una estructura canónica serializable que unifique dataclass `SitePresenceReport`, dict de `asdict()`, y evidencia de `skipped_assets`
2. **Adapter pattern**: un solo punto de entrada que acepte `SitePresenceReport | dict | None` y resuelva a dict canónico
3. **3 call sites en 2 módulos** con timing diferente (pre-diagnóstico, pre-generación, post-generación)
4. **Eliminar 4 rutas redundantes**: `ConditionalGenerator`, `main.py` re-check, `publication_gates.py` fake reconstruction, `publication_gates.py` re-check
5. **Cross-module**: `v4_asset_orchestrator.py`, `main.py`, `publication_gates.py`, `coherence_validator.py`

## 3. delegate_task Viability Matrix

| Fase | Tipo | ¿delegate_task? | Justificación |
|------|------|-----------------|---------------|
| FASE-1 | Código + tests | ❌ DIRECTA | Venv Windows → WSL import cascade |
| FASE-2 | Código + diseño | ❌ DIRECTA | Decisión arquitectónica cross-module NO delegable |
| FASE-3 | Código + tests | ❌ DIRECTA | Imports del proyecto (venv Windows) |
| FASE-4 | Código + tests | ❌ DIRECTA | Imports del proyecto |
| FASE-5 | Código + tests | ❌ DIRECTA | Imports del proyecto |
| FASE-6 | v4complete + análisis | ✅ MIXTO | v4complete → subagente; análisis → agente principal |
| RELEASE | Docs + scripts | ✅ SUBAGENTE | Solo YAML/MD + scripts, 0 imports de proyecto |

## 4. Versión Target y Dependencias

- **Versión actual**: v4.65.0 (HEAD: 0181b54)
- **Versión target**: v4.66.0
- **Dependencia crítica**: FASE-6 depende de FASE-1,2,3,4,5 completadas
- **FASE-RELEASE** depende de FASE-6 completada

## 5. Evidencia para v4complete (Zi One)

Los datos reales están en `output/clientes/v4_complete/zione/v4_audit/`:
- `pain_ledger_resolved.json` — reconciliación correcta (9 entries, 1 mapped_to_service)
- `gate_report_20260727_140459.json` — coverage FAILED (uncovered: no_whatsapp_visible)
- `coherence_validation.json` — whatsapp_verified.score = 0.30
- `asset_generation_report.json` — whatsapp_button site_verified=true
- `commercial_gates_report.json` — CG-ROI-NEGATIVE BLOCKING

## 6. No Objetivos (out of scope)

- ❌ Modificar `_JUSTIFIED_STATUSES` (ya contiene MAPPED_TO_SERVICE)
- ❌ Relajar CG-ROI-NEGATIVE (decisión comercial, no técnica)
- ❌ Cambiar `PAIN_SOLUTION_MAP` o `scenario_calculator.py`
- ❌ Modificar ROADMAP.md

## 7. Estado de Ejecución

| Fase | Estado | Fecha | Commit |
|------|--------|-------|--------|
| FASE-1 (Contract) | ✅ COMPLETED | 2026-07-27 | — |
| FASE-2 (SitePresence) | ✅ COMPLETED | 2026-07-27 | — |
| FASE-3 (Coherence Unify) | ✅ COMPLETED | 2026-07-27 | — |
| FASE-4 (Alignment Unify) | ✅ COMPLETED | 2026-07-28 | — |
| FASE-5 (Gate Idempotency) | ✅ COMPLETED | 2026-07-28 | — |
| FASE-6 (E2E Zi One) | ✅ COMPLETED | 2026-07-28 | — |
| FASE-6-A (DT4-N7) | ✅ COMPLETED | 2026-07-28 | — |
| FASE-6-B (DT4-N8) | ✅ COMPLETED | 2026-07-28 | — |
| **FASE-RELEASE v4.66.0** | ✅ COMPLETED | 2026-07-28 | **9b51fb0** |
