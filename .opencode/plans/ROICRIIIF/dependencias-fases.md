# ROICRIIIF — Dependencias de Fases

**Proyecto:** Publication Readiness Fix (post-FASE-6 blockers)
**Versión target:** 4.57.0 → 4.58.0
**Contexto:** .opencode/context/ROICRIII-fase-6-resultado-y-faltantes.md
**Score publication readiness:** 62.5% → target ≥80%
**Fecha creación:** 2026-05-28

---

## Issues a Resolver

| Issue | Issue ID | Severidad | Bloquea publicación |
|-------|----------|-----------|---------------------|
| Gate no reconoce whatsapp existente | GATE-PRESENCE | 🔴 Bloqueante | SÍ |
| "13%" artifact de pricing en propuesta | SEMANTIC-13 | 🟡 Semántico | NO |
| Confidence bajo (faq_page/optimization_guide: 0.5) | CONFIDENCE-LOW | 🔴 Co-bloqueante | SÍ (con GATE-PRESENCE) |

---

## Diagrama de Dependencias

```
FASE-1A (Gate Presence DIAGNÓSTICO — lectura pura, RAM-friendly)
    │
    ├──→ FASE-1B (Gate Presence IMPLEMENTACIÓN — delegate_task con fix recipe)
    │        │
    │        └──→ FASE-2 (Asset Confidence Enrichment — CONFIDENCE-LOW)
    │                 │
    │                 └──→ FASE-3 (Proposal Semantic Cleanup — SEMANTIC-13) [delegate_task]
    │                          │
    │                          └──→ FASE-4 (v4complete Hotel Castilla Real) [delegate_task]
    │                                   │
    └───────────────────────────────────┴──→ FASE-RELEASE-4.58.0
```

**Reglas:**
- FASE-1A (diagnóstico) → FASE-1B (implementación): secuencial obligatorio (1B depende del recipe de 1A)
- FASE-1B y FASE-2 son co-bloqueantes (ambas necesarias para ≥80% alignment)
- 1 fase por sesión, regla estricta

---

## Tabla de Conflictos de Archivos

| Archivo | FASE-1A | FASE-1B | FASE-2 | FASE-3 | FASE-4 |
|---------|---------|---------|--------|--------|--------|
| `publication_gates.py` (L797-1097) | 📖 read | ✏️ patch | — | — | — |
| `proposal_asset_alignment.py` (L157-330) | 📖 read | ✏️ patch | — | — | — |
| `assessment_builder.py` (L228-232) | 📖 read | — | — | — | — |
| `main.py` (L2693-2700) | 📖 grep | — | — | — | — |
| `conditional_generator.py` | — | — | ✏️ patch | — | — |
| `asset_catalog.py` | — | — | ✏️ patch | — | — |
| DOM scraping modules | — | — | ✏️ patch | — | — |
| `propuesta_v6_template.md` | — | — | — | ✏️ patch | — |
| `v4_proposal_generator.py` | — | — | — | ✏️ patch | — |

**Riesgo:** Ningún archivo modificado en más de una fase de implementation. FASE-1A solo lee (📖), FASE-1B escribe (✏️).

---

## Estado de Fases

| Fase | Estado | Fecha | Notas |
|------|--------|-------|-------|
| FASE-1A (Diagnóstico Gate) | ⬜ Pendiente | — | Lectura pura + fix recipe |
| FASE-1B (Implementación Gate) | ✅ COMPLETED | 2026-05-28 | delegate_task con recipe. Patches: assessment_builder.py (+skipped_assets field/propagation), publication_gates.py (+FASE-1B skipped→site_presence_report bridge). Tests: 4/4 pass (test_publication_gates_presence.py). No-regression: 401 passed. run_all_validations --quick: 5/5. |
| FASE-2 (Asset Confidence) | ✅ COMPLETED | 2026-05-28 | Fix: preflight_checks.py L279-281 trata listas como ESTIMATED. 5 tests nuevos. alignment 62%→100% con datos completos. |
| FASE-3 (Semantic Cleanup) | ⬜ Pendiente | — | delegate_task |
| FASE-4 (v4complete) | ⬜ Pendiente | — | delegate_task |
| FASE-RELEASE-4.58.0 | ⬜ Pendiente | — | Version bump + docs |

---

## Matriz de Complejidad

| Fase | Complejidad Técnica | Riesgo | delegate_task | Iteraciones est. | RAM pressure |
|------|-------------------|--------|---------------|------------------|--------------|
| FASE-1A | 🟡 MEDIA | Lectura sin side-effects | No | ~25-35 | 🟢 BAJO |
| FASE-1B | 🟡 MEDIA (recipe applied) | Patch cross-module | ✅ Sí | ~20-30 parent | 🟢 BAJO (aislado) |
| FASE-2 | 🟡 MEDIA | DOM enrichment, scoring | No | ~35-45 | 🟡 MEDIO |
| FASE-3 | 🟢 BAJA | Template edit localizado | ✅ Sí | ~15-25 parent | 🟢 BAJO (aislado) |
| FASE-4 | 🟡 MEDIA | v4complete largo | ✅ Sí | ~25-35 parent | 🟢 BAJO (aislado) |
| RELEASE | 🟢 BAJA | Docs only | No | ~30-40 | 🟢 BAJO |

**⚠️ MAYOR COMPLEJIDAD (original): FASE-1, DIVIDIDA EN:**
- **FASE-1A (diagnóstico)**: riesgo bajo, solo lectura
- **FASE-1B (implementación)**: complejidad ahora mitigada por recipe + delegate_task

---

## Estrategia de delegate_task

| Fase | delegate_task | Razón |
|------|---------------|-------|
| FASE-1A | ❌ No | Diagnóstico iterativo, parent agent necesita controlar lecturas |
| FASE-1B | ✅ Sí | Fix recipe documentado; implementación mecánica + tests |
| FASE-2 | ❌ No | Análisis iterativo de DOM/scoring |
| FASE-3 | ✅ Sí | Cambio localizado, self-contained |
| FASE-4 | ✅ Sí | v4complete ~5-10min, timeout=900s |
| RELEASE | ❌ No | Docs cascade estándar |

---

## RAM-Friendly Design

Este plan fue diseñado post-división de FASE-1 para mitigar problemas de RAM del usuario:

1. **FASE-1A sin patches**: evita cargar archivos a contexto para edición
2. **FASE-1B delegada**: subagente maneja todo el contexto de implementación en RAM aislada
3. **FASE-3 y FASE-4 delegadas**: subagentes con contextos aislados (no contaminan parent)
4. **FASE-1A usa execute_code para batching**: 1 tool call en vez de 5+ greps
5. **FASE-1A usa offset/limit**: lee 60 líneas máximo a la vez
6. **6 sesiones totales** (no 5): divide el trabajo más uniformemente
