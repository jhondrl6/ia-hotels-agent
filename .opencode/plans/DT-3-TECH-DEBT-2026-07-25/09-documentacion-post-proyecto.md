# Documentación Post-Proyecto — DT-3 TECH DEBT

> **Plan**: DT-3-TECH-DEBT-2026-07-25
> **Target**: v4.64.0
> **Iniciado**: 2026-07-25

---

## FASE-0 — Fix sistémico rutas flat → per-hotel (BUG-1)

- **Estado**: ✅ COMPLETADO (subagente)
- **Archivos modificados**: main.py
- **Cambios**: _get_pipeline_path() helper + 3 rutas flat → per-hotel (L2650, L2571, L2572)
- **Verificación**: grep _get_pipeline_path → 4 ocurrencias (1 definición + 3 usos)

---

## FASE-1 — Fix G9 dual-list + status-based eval (BUG-2, BUG-3)

- **Estado**: ✅ COMPLETADO (directa)
- **Archivos modificados**: modules/quality_gates/delivery_quality_report.py
- **Cambios**:
  - `BLOCKING_GATE_NAMES` constante (L269): fuente única de verdad para blocking_gates + warning_gates
  - `_is_service_aligned()` helper: evalúa status (LINKED/NO_BREACH=True, resto=False)
  - `actionable_services`: excluye NO_BREACH del denominador
  - `passed` condition: `aligned_services == actionable_services` (no total_services)
- **BUG-2 fix**: warning_gates ahora usa `name not in BLOCKING_GATE_NAMES` (antes omitía "proposal_asset_alignment")
- **BUG-3 fix**: `_is_service_aligned()` distingue NO_BREACH (legítimo) de MISSING_ASSET (fallo real)
- **Verificación**: grep "proposal_asset_alignment" → 4 ocurrencias legítimas (gate_results ×2, BLOCKING_GATE_NAMES ×1, return ×1), cero en list comprehensions
