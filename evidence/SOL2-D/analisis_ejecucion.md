# Evidencia FASE-SOL2-D: Phantom Fields & Coherence Consistency

**Fecha**: 2026-05-07 15:46
**Iteraciones usadas**: ~15
**Resultado**: ✅ COMPLETADA

---

## Tarea 1: Auditoría de Campos Fantasma

### Hallazgo
Los campos `site_verification_applied` y `delivery_ready_percentage` **SÍ existen** en el código:

**Archivo**: `modules/asset_generation/v4_asset_orchestrator.py` (líneas 144-145)
```python
"delivery_ready_percentage": round(delivery_ready_pct, 2),
"site_verification_applied": len(self.skipped_assets) > 0  # FASE-CAUSAL-01
```

- `delivery_ready_pct` se calcula como `(can_use / total) * 100`
- `site_verification_applied` es `True` si hay assets skipeados

### Veredicto
**GAP-G es FALSO POSITIVO.** Los campos son calculados dinámicamente, no hardcodeados. No hay campos fantasma en el pipeline.

### Búsqueda adicional
- `site_verification_applied` → Solo en `v4_asset_orchestrator.py` (1 match)
- `delivery_ready_percentage` → Solo en `v4_asset_orchestrator.py` (1 match)
- `67.0` hardcodeado → No encontrado en módulos de reporte
- No hay campos fantasma en `publication_gates.py` ni `v4_orchestrator.py`

---

## Tarea 2: Unificación de Coherence Score

### Hallazgo
La fuente de verdad es **CoherenceValidator.validate()** que calcula un promedio ponderado de 6 checks:

| Check | Peso |
|-------|------|
| problems_have_solutions | 1.5 |
| assets_are_justified | 1.0 |
| financial_data_validated | 1.5 |
| whatsapp_verified | 0.5 |
| price_matches_pain | 1.0 |
| promised_assets_exist | 2.0 |

### Flujo del score
1. `CoherenceValidator.validate()` → calcula `overall_score` (weighted avg)
2. Se guarda en `coherence_validation.json` como `round(overall_score, 4)` → 0.89
3. El orchestrator pasa el score al assessment dict
4. `PublicationGatesOrchestrator._extract_coherence_score()` extrae el valor del assessment
5. El gate lo muestra en `gate_report.json` → 0.891 (mismo dato, menos redondeo)

### Diferencia 0.89 vs 0.891
Es solo redondeo. No son cálculos independientes.

### Documentación agregada
- Docstring de `_coherence_gate()` en `publication_gates.py` ahora documenta "SOURCE OF TRUTH"
- Docstring de `_extract_coherence_score()` documenta prioridad de lookup
- AGENTS.md ya usa `≥0.8` (range notation) — no requiere cambios

---

## Tarea 3: Corrección de Line Range

### Cambio
- **Antes**: `publication_gates.py (lineas 755-850)` → claim #4 marcado como ⚠️ PARCIAL
- **Después**: `publication_gates.py (lineas 755-865)` → claim #4 ahora ✅ CONFIRMADO

### Archivo modificado
`.opencode/context/05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md`

---

## Tarea 4: Validación

```
[+] Residual Files: No residual files found
[+] Plan Maestro Sync: Plan Maestro vv2.5.0 loaded correctly
[+] Version Sync: All versions synchronized
[+] Secrets Check: No hardcoded secrets found
TOTAL: 4/4 validations passed
STATUS: ALL VALIDATIONS PASSED
```

---

## Archivos Modificados

| Archivo | Cambio |
|---------|--------|
| `modules/quality_gates/publication_gates.py` | Docstrings de source-of-truth en `_coherence_gate` y `_extract_coherence_score` |
| `.opencode/context/05_SOL-2_ASSET_ALIGNMENT_DISCREPANCY_20260507.md` | GAP-G corregida (falso positivo), GAP-D documentada, line range corregido, resumen actualizado |
| `.opencode/plans/SOL-2-REFACTOR/06-checklist-implementacion.md` | FASE-SOL2-D ✅, GAP-D ✅, GAP-G ✅ |
| `.opencode/plans/SOL-2-REFACTOR/dependencias-fases.md` | FASE-SOL2-D ✅ |
| `.opencode/plans/SOL-2-REFACTOR/09-documentacion-post-proyecto.md` | Sección E actualizada |

---

## Criterios de Completitud

- [x] Campos fantasma auditados → NO son fantasma (calculados dinámicamente)
- [x] Coherence score tiene fuente única → CoherenceValidator.validate()
- [x] Line ranges corregidos → 755-865
- [x] Validaciones pasan → 4/4
- [x] Máximo 60 iteraciones → ~15 usadas
