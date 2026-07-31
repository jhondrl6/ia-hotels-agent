# Dependencies entre Fases — DT-4

> **Plan**: DT-4-ROOT-CAUSE-2026-07-25
> **Target**: v4.65.0

---

## Grafo de Dependencias

```
FASE-0 (Reconciliador — causa raíz)
  │
  ├──▶ FASE-1 (BUG-8: optimista) ── independiente de FASE-2/3/4
  │
  ├──▶ FASE-2 (BUG-7: commercial gates) ── requiere pain_ledger resuelto
  │
  ├──▶ FASE-3 (BUG-10: monthly_report) ── independiente de FASE-1/2/4
  │
  ├──▶ FASE-4 (N1: gate names) ── independiente de FASE-1/2/3
  │
  └──▶ FASE-RELEASE (v4complete + version bump) ── requiere TODAS
```

---

## Tabla de Dependencias

| Fase | Depende de | Bloquea a | Justificación |
|------|-----------|-----------|---------------|
| FASE-0 | — (root cause) | FASE-2, FASE-RELEASE | El reconciliador es la causa raíz transversal. FASE-2 requiere pain_ledger resuelto para que los commercial gates operen sobre datos correctos. FASE-1/3/4 son independientes del reconciliador pero FASE-RELEASE requiere que todo esté implementado |
| FASE-1 | — (independiente) | FASE-RELEASE | BUG-8 es reinterpretación comercial en commercial_gate.py. No depende del reconciliador — los commercial gates evalúan escenarios financieros, no pain_ledger |
| FASE-2 | FASE-0 | FASE-RELEASE | BUG-7 persiste commercial gates. Requiere FASE-0 para que el pain_ledger esté resuelto (los commercial gates dependen indirectamente del estado de pains vía escenarios financieros) |
| FASE-3 | — (independiente) | FASE-RELEASE | BUG-10 es 1 línea en proposal_asset_alignment.py. Sin dependencias técnicas |
| FASE-4 | — (independiente) | FASE-RELEASE | N1 es rename de strings. Sin dependencias técnicas |
| FASE-RELEASE | FASE-0, FASE-1, FASE-2, FASE-3, FASE-4 | — (final) | v4complete + análisis requieren todos los fixes implementados |

---

## Matriz de Conflictos de Archivos

| Archivo | FASE-0 | FASE-1 | FASE-2 | FASE-3 | FASE-4 | RELEASE | ¿Conflicto? |
|---------|--------|--------|--------|--------|--------|---------|-------------|
| `modules/orchestration/post_orchestrator_reconciler.py` | ✅ CREA | — | — | — | — | — | Sin conflicto |
| `modules/asset_generation/v4_asset_orchestrator.py` | ✅ MODIFICA | — | — | — | — | — | Sin conflicto |
| `modules/quality_gates/publication_gates.py` | ✅ MODIFICA (L1186, L1230) | — | — | — | ✅ MODIFICA (rename gate) | — | ⚠️ FASE-0 modifica _JUSTIFIED_STATUSES + _coverage_gate; FASE-4 renombra gate. Sin solapamiento si FASE-4 usa rename único del gate_name string |
| `modules/quality_gates/coherence_validator.py` | ✅ MODIFICA | — | — | — | — | — | Sin conflicto |
| `modules/asset_generation/proposal_asset_alignment.py` | — | — | — | ✅ MODIFICA | — | — | Sin conflicto |
| `modules/quality_gates/commercial_gate.py` | — | ✅ MODIFICA | — | — | — | — | Sin conflicto |
| `modules/quality_gates/delivery_quality_report.py` | — | — | — | — | ✅ MODIFICA (rename gate) | — | Sin conflicto |
| `modules/commercial_documents/v4_proposal_generator.py` | — | — | ✅ MODIFICA (L610) | — | — | — | Sin conflicto |
| `main.py` | — | — | ✅ MODIFICA (BLOCKED_BY_GATES) | — | — | — | Sin conflicto |
| `VERSION.yaml` | — | — | — | — | — | ✅ MODIFICA | Sin conflicto |
| `CHANGELOG.md` | — | — | — | — | — | ✅ MODIFICA | Sin conflicto |

**Regla**: El único solapamiento es FASE-0 + FASE-4 en publication_gates.py, pero tocan secciones distintas del archivo (L1186 vs rename de string). Sin riesgo de conflicto de merge real.

---

## Orden de Ejecución Recomendado

1. **FASE-0** — Nueva sesión. Reconciliador post-orchestrator. **MAYOR COMPLEJIDAD**. Sin dependencias previas.
2. **FASE-1** — Nueva sesión. BUG-8 reinterpretación optimista. Independiente; puede ejecutarse en cualquier orden post-FASE-0.
3. **FASE-2** — Nueva sesión. BUG-7 commercial gates. Requiere FASE-0 completada.
4. **FASE-3** — Nueva sesión. BUG-10 monthly_report. Independiente; ejecutar cuando convenga.
5. **FASE-4** — Nueva sesión. N1 gate names. Independiente; ejecutar cuando convenga.
6. **FASE-RELEASE** — Nueva sesión. v4complete + version bump + análisis. Requiere TODAS las fases anteriores.

**Paralelismo posible**: FASE-1, FASE-3 y FASE-4 son independientes entre sí y pueden ejecutarse en cualquier orden después de FASE-0. FASE-2 debe esperar a FASE-0.
