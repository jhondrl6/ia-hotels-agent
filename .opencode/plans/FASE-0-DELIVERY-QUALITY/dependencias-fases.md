# Dependencias de Fases — FASE-0-DELIVERY-QUALITY

```
FASE-0A (Baseline)
    |
    v
FASE-0B (Pain Ledger) --------> FASE-0C (Coverage Gate)
    |                                |
    |                                v
    |                           FASE-0D (Proposal-Asset Matrix)
    |                                |
    |                                v
    |                           FASE-0E (Delivery Quality Report)
    |                                |
    |                                v
    |                           FASE-0F (Human Checklist)
    |                                |
    +--------------------------------+
    |
    v
FASE-0G (E2E Controlado)
    |
    v
FASE-0H (G8 Root-Cause Hardening)
    |
    v
FASE-RELEASE (Docs Cascade)
```

---

## Tabla de dependencias

| Fase | Requiere | Archivos en común | Conflictos potenciales |
|------|----------|-------------------|------------------------|
| 0A | Ninguna | Ninguno | Ninguno |
| 0B | 0A | `modules/commercial_documents/pain_solution_mapper.py` | Ninguno (solo lectura en 0A) |
| 0C | 0B | `modules/quality_gates/` | Ninguno |
| 0D | 0C | `modules/asset_generation/proposal_asset_alignment.py`, `modules/commercial_documents/v4_proposal_generator.py` | 0D modifica proposal generator; 0C no lo toca |
| 0E | 0D | `modules/quality_gates/publication_gates.py`, `main.py` | 0E modifica `main.py` para integrar reporte antes de ZIP; 0D no toca main.py |
| 0F | 0E | `modules/quality_gates/` | 0F crea generator separado; no conflictos |
| 0G | 0A-0F | `output/v4_complete/` | 0G es ejecución; no modifica código fuente |
| 0H | 0G | `modules/asset_generation/`, `modules/quality_gates/` | 0H modifica orquestador + preflight + scoring; depende del fixture de 0G |
| RELEASE | 0A-0H | `docs/`, `CHANGELOG.md`, `VERSION.yaml` | RELEASE solo documenta; no modifica código productivo |

---

## Paralelismo

- **Ninguna fase puede ejecutarse en paralelo.** Cada fase depende de la anterior.
- RELEASE es estrictamente secuencial después de 0G.

---

## Archivos a modificar por fase (resumen)

### 0A — Baseline
- Ninguno (solo lectura/auditoría).
- Crea: `.opencode/context/FASE-0-BASELINE-DELIVERY-QUALITY.md` (evidencia).

### 0B — Pain Ledger
- `modules/commercial_documents/pain_solution_mapper.py` (extender)
- `modules/asset_generation/v4_asset_orchestrator.py` (inyectar ledger)
- Crea: `modules/asset_generation/pain_ledger.py`, `tests/asset_generation/test_pain_ledger.py`

### 0C — Coverage Gate
- `modules/quality_gates/publication_gates.py` (agregar gate)
- Crea: `tests/quality_gates/test_coverage_gate.py`

### 0D — Proposal-Asset Matrix
- `modules/asset_generation/proposal_asset_alignment.py` (extender)
- `modules/commercial_documents/v4_proposal_generator.py` (inyectar matriz)
- Crea: `tests/asset_generation/test_proposal_asset_matrix.py`

### 0E — Delivery Quality Report
- `modules/quality_gates/publication_gates.py` (integrar reporte)
- `main.py` (llamar reporte antes de ZIP)
- Crea: `modules/quality_gates/delivery_quality_report.py`, `tests/quality_gates/test_delivery_quality_report.py`

### 0F — Human Checklist
- Crea: `modules/quality_gates/human_checklist_generator.py`, `tests/quality_gates/test_human_checklist_generator.py`

### 0G — E2E
- Ninguno (ejecución + verificación).
- **Estado:** ✅ COMPLETADA — 2026-05-13
- **Resultado:** G0=WARNING, G6=PASS(0.81), G7=PASS(0 UNTRACKED), G8=FAIL(8/12 low conf)
- **Evidencia:** `evidence/FASE-0G-E2E/`

### 0H — G8 Root-Cause Hardening
- `modules/asset_generation/data_derivation_layer.py` (crear)
- `modules/asset_generation/v4_asset_orchestrator.py` (inyectar derivación)
- `modules/asset_generation/conditional_generator.py` (contrato REQUIRED/RECOMMENDED + scoring)
- Crea: `tests/asset_generation/test_data_derivation_layer.py`, `tests/fixtures/audit_report_hotelcastillareal.json`

### RELEASE
- `docs/CONTRIBUTING.md` (si aplica)
- `CHANGELOG.md`
- `docs/GUIA_TECNICA.md`
- `VERSION.yaml` → `sync_versions.py`
- `docs/contributing/REGISTRY.md` → `log_phase_completion.py`
