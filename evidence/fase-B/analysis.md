# FASE-B Analysis: Advisory Warnings Verification

**Date**: 2026-05-16
**Hotel**: Hotel Castilla Real (https://www.hotelcastillareal.com/)
**v4complete runs**: 20260516_192715 (v1), 20260516 (v2 with fix)
**FASE-A status**: Implemented (code changes from 2026-05-16 18:54 session)
**Fix applied**: 2026-05-16 — `v4_comprehensive.py` `save_report()` now writes `ia_readiness_report.json`

---

## T1: v4complete Execution ✅

**Command**: `./venv/Scripts/python.exe main.py v4complete --url https://www.hotelcastillareal.com/ --debug`

**Result** (run v2 with fix):
- Exit: SUCCESS (no fatal errors)
- Coherence score: **0.83** (threshold 0.80 → PASSES gate)
- `is_coherent: false` due to WhatsApp confidence 0.30 (< 0.9 threshold)
- Status: WARNING (non-blocking, due to G8 asset_specificity failure)
- ZIP generated: `hotelcastillareal_20260516.zip` ✅

**Files generated**:
- `01_DIAGNOSTICO_Y_OPORTUNIDAD_*.md`
- `02_PROPUESTA_COMERCIAL_*.md`
- `delivery_quality_report.json`
- `coherence_validation.json`
- `ia_readiness_report.json` ✅ (fix result)

---

## T2: Advisory Warning in DIAGNOSTICO.md ✅

**Location**: Lines 86-92 of DIAGNOSTICO.md

**Métricas de Acceso para IA table**:
```
| Accesibilidad IA | 0.50/1.00 | 0 bloqueados | 🟡 |
| Citabilidad      | 57.0/100  | 5 bloques    | 🟢 |
| IA-Readiness     | 34.6/100  | Critical     | 🟡 |
```

**Alert blockquote present** (line 92):
```
> ⚠️ **Alerta IA-Readiness Critical**: este score no bloquea la entrega,
> pero indica que el objetivo comercial de ser citado/recomendado por IA
> está en riesgo hasta implementar las correcciones propuestas.
```

**Verification**:
- ✅ IA-Readiness score 34.6 < 50 → Critical state triggered
- ✅ Blockquote format (`> ⚠️`) correct
- ✅ Alert text matches FASE-A specification exactly
- ✅ Alert appears directly below the IA metrics table
- ✅ ZIP delivery NOT blocked

**Verdict**: T2 PASS ✅ — Advisory warning in DIAGNOSTICO.md functions correctly.

---

## T3: Advisory Warnings in delivery_quality_report.json ✅

**Location**: `output/v4_complete/hotelcastillareal/v4_audit/delivery_quality_report.json`

**Result after fix**:
```json
{
  "status": "WARNING",
  "blocking": false,
  "advisory_warnings": [
    {
      "code": "IA_READINESS_CRITICAL",
      "severity": "WARNING",
      "blocking": false,
      "message": "IA-Readiness Critical: objetivo de citación/recomendación por IA en riesgo sin acción correctiva"
    }
  ],
  ...
}
```

**Verification**:
- ✅ `advisory_warnings` is a list (not empty)
- ✅ Entry contains correct `code: "IA_READINESS_CRITICAL"`
- ✅ `severity: "WARNING"` correct
- ✅ `blocking: false` correct (non-blocking as designed)
- ✅ `message` matches specification
- ✅ `status` is WARNING (not FAIL) — advisory does not block

**Root cause of previous failure**: `v4_comprehensive.py` `save_report()` was not writing `ia_readiness_report.json`. Fixed by adding writing of IA-Readiness data alongside the main audit report.

**Verdict**: T3 PASS ✅ — `advisory_warnings` now correctly populated.

---

## T4: Analysis Summary

### What works:
1. **DIAGNOSTICO.md alert**: ✅ Blockquote appears when IA-Readiness < 50
2. **Code in v4_diagnostic_generator.py**: ✅ Logic correct (lines 1655-1661)
3. **Code in delivery_quality_report.py**: ✅ Logic correct (lines 190-200)
4. **Non-blocking behavior**: ✅ ZIP generates despite Critical score
5. **Coherence gate ≥ 0.80**: ✅ 0.83 score
6. **ia_readiness_report.json generation**: ✅ Fixed by adding writing in `save_report()`

### Fix applied (2026-05-16):
**File**: `modules/auditors/v4_comprehensive.py`
**Location**: `save_report()` method (after line 1598)
**Change**: After writing `audit_report_*.json`, also persist `ia_readiness_report.json` if `result.ia_readiness` is present.

```python
# FASE-A: Also persist IA-Readiness separately so delivery_quality_report
# can read it back without needing the in-memory V4AuditResult object.
if result.ia_readiness:
    ia_readiness_path = output_path.parent / "ia_readiness_report.json"
    ia_data = {
        "overall_score": result.ia_readiness.overall_score,
        "components": result.ia_readiness.components,
        "status": result.ia_readiness.status,
        "actionable_items": result.ia_readiness.actionable_items,
    }
    with open(ia_readiness_path, 'w', encoding='utf-8') as f:
        json.dump(ia_data, f, indent=2, ensure_ascii=False)
```

### ia_readiness_report.json content:
```json
{
  "overall_score": 34.57,
  "components": {
    "schema_quality": 0.0,
    "crawler_access": 50.0,
    "citability": 57.0,
    "llms_txt": 0,
    "brand_signals": 50.0
  },
  "status": "Critical",
  "actionable_items": [...]
}
```

---

## Checkpoint: All Advisory Warnings Functionality ✅

| Component | Status | Evidence |
|-----------|--------|----------|
| Alerta en diagnóstico (DIAGNOSTICO.md) | ✅ | Line 92 blockquote present |
| advisory_warnings en JSON | ✅ | `[IA_READINESS_CRITICAL]` populated |
| advisory_warnings code logic | ✅ | Lines 190-200 in delivery_quality_report.py |
| Non-blocking (ZIP no aborta) | ✅ | ZIP generated despite Critical |
| Coherence gate ≥ 0.80 | ✅ | 0.83 score |
| ia_readiness_report.json generation | ✅ | Written by save_report() fix |

**Conclusion**: FASE-A + FASE-B fully functional. Both advisory warning outputs (DIAGNOSTICO.md blockquote AND delivery_quality_report.json advisory_warnings) work correctly end-to-end.

---

## Evidence Files
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/01_DIAGNOSTICO_*.md`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/02_PROPUESTA_*.md`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/delivery_quality_report.json`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/coherence_validation.json`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/ejecucion.log`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/ejecucion_v2.log`
- `/mnt/c/Users/Jhond/Github/iah-cli/evidence/fase-B/ia_readiness_report.json` (new)