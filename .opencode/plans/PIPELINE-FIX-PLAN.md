# Plan: Pipeline Assessment Bridge Fix (PIPELINE-FIX)

**Creado:** 2026-05-23
**Contexto:** `.opencode/context/auditoria-hotelcastillareal-fase0-pipeline-fixes.md`
**Dictamen:** Assessment dict en main.py no inyecta artefactos intermedios (pain_ledger, financial_evidence_tier, pain_ids) → 2 gates BLOCKED falsos + métrica delivery_ready distorsionada
**Causa raíz única:** `main.py:2652-2694` construye assessment manualmente sin cargar artefactos que YA existen en disco/memoria
**Versión objetivo:** 4.48.0
**Código:** `PIPELINE-FIX`

---

## Arquitectura del Plan

```
FASE-PF-1 ──→ FASE-PF-2 ──→ FASE-PF-3 ──→ FASE-PF-4
 (root cause)   (complementary)  (v4c+verify)    (release/docs)
```

| Fase | Propósito | Hallazgos que resuelve | Sesión | Comando largo |
|------|-----------|----------------------|--------|---------------|
| FASE-PF-1 | Fix assessment dict (cargar + inyectar artefactos huérfanos) | CRÍTICO-1, NUEVO-5, NUEVO-6, ALTO-4 | 1 | No |
| FASE-PF-2 | Fix delivery_ready_percentage (fórmula correcta) | NUEVO-7 | 1 | No |
| FASE-PF-3 | v4complete Hotel Castilla Real + verificación de gates | Verificación E2E | 1 | Sí (v4complete) |
| FASE-PF-4 | Documentación ROADMAP + CHANGELOG + VERSION sync | ALTO-3, NUEVO-9 | 1 | No |

**Total: 4 sesiones**

---

## Hallazgos → Fases (Mapping)

| ID | Severidad | Hallazgo | Fase | Fix |
|----|-----------|----------|------|-----|
| CRÍTICO-1 | 🔴 | PainLedger no llega al CoverageGate | PF-1 | Cargar pain_ledger.json + inyectar al assessment |
| ALTO-4 | 🟡 | proposal_asset_matrix.json no se serializa | PF-1 | Pasar pain_ledger a proposal_gen.generate() |
| NUEVO-5 | 🔴 | financial_evidence_tier nunca llega al assessment | PF-1 | Inyectar desde financial_breakdown.evidence_tier |
| NUEVO-6 | 🟡 | diagnostic_pain_ids y proposal_pain_ids ausentes | PF-1 | Extraer de diagnostic_summary + asset_plan |
| NUEVO-7 | 🟡 | delivery_ready_percentage usa fórmula equivocada | PF-2 | Cambiar preflight_status → confidence_score ≥0.65 |
| ALTO-3 | 🟡 | tier_c_onboarding_required no documentado en ROADMAP | PF-4 | Agregar a ROADMAP |
| NUEVO-9 | 🔵 | ROADMAP documenta 4 gates, código tiene 11 | PF-4 | Tabla mapping ROADMAP ↔ código |
| NUEVO-8 | 🟡 | Assessment dict frágil y manual | **FUERA DE SCOPE** | AssessmentBuilder (sesión futura dedicada) |

---

## Dependencias

```
PF-1 (root cause) ──── PF-2 (independiente de PF-1 pero secuencial)
      │                       │
      └───────┬───────────────┘
              ▼
        PF-3 (v4complete — necesita ambos fixes aplicados)
              │
              ▼
        PF-4 (docs — necesita resultados de PF-3)
```

---

## Resultado esperado post-fix (Hotel Castilla Real)

| Gate | Estado actual | Estado esperado |
|------|---------------|-----------------|
| `coverage` | BLOCKED (falso — sin pain_ledger) | PASS (0 UNTRACKED) |
| `tier_c_onboarding_required` | BLOCKED (falso — default "C") | Depende de datos reales |
| `asset_confidence` (G8) | WARNING (optimization_guide 0.50) | Sin cambios (data-dependent) |
| `financial_validity` | WARNING (default tier) | Depende de datos reales |
| `delivery_ready_percentage` | 50.0% (fórmula rota) | ~91.7% (11/12 ≥0.65) |
| `proposal_asset_matrix.json` | No generado | ✅ Generado |

---

## Archivos del plan

| Archivo | Descripción |
|---------|-------------|
| `PIPELINE-FIX-PLAN.md` | Este archivo — plan maestro |
| `05-prompt-inicio-sesion-fase-PF-1.md` | Prompt FASE-PF-1 (root cause) |
| `05-prompt-inicio-sesion-fase-PF-2.md` | Prompt FASE-PF-2 (delivery_ready) |
| `05-prompt-inicio-sesion-fase-PF-3.md` | Prompt FASE-PF-3 (v4complete + verificación) |
| `05-prompt-inicio-sesion-fase-PF-4.md` | Prompt FASE-PF-4 (release docs) |
| `06-checklist-pipeline-fix.md` | Checklist maestro de implementación |

---

## Archivos de código modificados

| Archivo | Fases | Qué se modifica |
|---------|-------|----------------|
| `main.py:2652-2694` | PF-1 | Agregar 4 campos al assessment dict |
| `main.py:2601-2614` | PF-1 | Pasar pain_ledger a proposal_gen.generate() |
| `modules/asset_generation/v4_asset_orchestrator.py:125-132` | PF-2 | Cambiar fórmula delivery_ready_pct |
| `ROADMAP.md:296-332` | PF-4 | Documentar gates y métrica |

## Archivos de código NO modificados (solo lectura/verificación)

| Archivo | Por qué |
|---------|---------|
| `modules/quality_gates/publication_gates.py` | Los gates ya están bien implementados; el bug es que no reciben datos |
| `modules/asset_generation/pain_ledger.py` | Ya genera y persiste correctamente |
| `modules/asset_generation/v4_proposal_generator.py` | Ya tiene la lógica de save(); solo falta recibir pain_ledger |
