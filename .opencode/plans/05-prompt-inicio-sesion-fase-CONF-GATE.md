---
description: FASE-CONF-GATE — Asset confidence gate en publication gates
version: 1.0.0
---

# FASE-CONF-GATE: Asset Confidence Gate en Publication

**ID**: FASE-CONF-GATE  
**Objetivo**: Crear gate que evalúa `confidence_score` de assets y bloquea o advierte en publication  
**Dependencias**: FASE-GEO-BRIDGE (usa el bridge para mejorar confidence)  
**Duración estimada**: 1-2 horas  
**Skill**: `iah-cli-phased-execution`

---

## Contexto

### Problema (D8 del AUDIT)

```
D8: TODOS los assets con confidence 0.50 pero marcados READY_FOR_PUBLICATION

El cliente recibe assets de baja calidad sin saberlo.
El gate `content_quality` pasa con 0.95 aunque haya WARNING en preflight.
No hay gate que evalúe `confidence_score` de assets.
```

**Estado actual en v4_complete_report.json**:
```json
"phase_4_publication_gates": {
  "status": "READY_FOR_PUBLICATION",
  "gate_results": [
    // 7 gates pasando...
  ],
  "blocking_issues": []
}
```

**Pero los assets**:
```json
"generated_assets": [
  {
    "asset_type": "hotel_schema",
    "preflight_status": "WARNING",
    "confidence_score": 0.5,  // <-- ¡BAJO!
    "can_use": true           // <-- ¡El cliente cree que puede usarlo!
  }
]
```

### Archivo a Modificar

```
modules/quality_gates/publication_gates.py   — donde están los 7 gates actuales
```

### Decisión de Diseño Requerida

El gate puede actuar de dos formas:

**Opción A (Conservative)**: `READY_FOR_PUBLICATION_WITH_WARNINGS`
- Si algún asset confidence < 0.7, el status cambia a `READY_FOR_PUBLICATION_WITH_WARNINGS`
- No bloquea, pero alerta al cliente
- Campo nuevo: `warnings` array con lista de assets problemáticos

**Opción B (Strict)**: Gate falla si confidence < 0.7
- `READY_FOR_PUBLICATION` solo si todos los assets >= 0.7
- Si alguno < 0.7 → status = `BLOCKED` con razón

**Recomendación del AUDIT**: Opción A (conservative) ya que los datos de geo_enriched mejorarán el confidence y el gate será más lenient temporalmente mientras se madura la calidad.

---

## Tareas

### Tarea 1: Diseñar e implementar `asset_confidence_gate`

**Ubicación**: `modules/quality_gates/publication_gates.py`

**Código a agregar** (junto a los 7 gates existentes):

```python
def asset_confidence_gate(
    generated_assets: List[Dict[str, Any]],
    threshold: float = 0.7
) -> PublicationGateResult:
    """
    Gate 8: Verifica que los assets tengan confidence score aceptable.
    
    Args:
        generated_assets: Lista de assets generados con confidence_score
        threshold: Minimum acceptable confidence (default 0.7)
    
    Returns:
        PublicationGateResult con status PASSED/FAILED/WARNING
    """
    low_confidence_assets = [
        a for a in generated_assets 
        if a.get("confidence_score", 0) < threshold
    ]
    
    if not low_confidence_assets:
        return PublicationGateResult(
            gate_name="asset_confidence",
            passed=True,
            status=GateStatus.PASSED,
            message=f"All {len(generated_assets)} assets meet confidence threshold ({threshold})",
            value=1.0,
            details={
                "total_assets": len(generated_assets),
                "above_threshold": len(generated_assets),
                "below_threshold": 0
            }
        )
    
    # Advertencia: hay assets con confidence bajo
    avg_confidence = sum(a.get("confidence_score", 0) for a in generated_assets) / len(generated_assets)
    
    return PublicationGateResult(
        gate_name="asset_confidence",
        passed=True,  # No bloquea, solo advierte
        status=GateStatus.WARNING,
        message=f"{len(low_confidence_assets)} asset(s) below confidence threshold",
        value=avg_confidence,
        suggestion="Run enrichment phase to improve asset quality",
        details={
            "total_assets": len(generated_assets),
            "above_threshold": len(generated_assets) - len(low_confidence_assets),
            "below_threshold": len(low_confidence_assets),
            "low_confidence_assets": [
                {"type": a["asset_type"], "score": a["confidence_score"]}
                for a in low_confidence_assets
            ]
        }
    )
```

---

### Tarea 2: Integrar gate en `run_publication_gates`

**Ubicación**: `modules/quality_gates/publication_gates.py` — función `run_publication_gates`

**Agregar como gate #8**:
```python
# Gate 8: Asset Confidence
if "generated_assets" in context:
    results.append(asset_confidence_gate(context["generated_assets"]))
```

---

### Tarea 3: Actualizar `PublicationGatesOrchestrator`

**Ubicación**: `modules/quality_gates/publication_gates.py`

**Campo nuevo en PublicationGatesResult**:
```python
@dataclass
class PublicationGatesResult:
    # ... campos existentes ...
    confidence_warnings: List[Dict[str, Any]] = field(default_factory=list)
```

---

### Tarea 4: Tests para el gate

**Archivo**: `tests/quality_gates/test_asset_confidence_gate.py`

**Casos**:
1. `test_gate_passes_when_all_above_threshold` — todos assets >= 0.7 → PASSED
2. `test_gate_warns_when_some_below_threshold` — algunos < 0.7 → WARNING (no bloquea)
3. `test_gate_calculates_avg_correctly` — avg de 3 assets con scores [0.5, 0.8, 0.9] = 0.73
4. `test_gate_empty_assets_list` — lista vacía → PASSED (no hay nada que evaluar)

---

## Restricciones

- NO modificar el cálculo financiero ni los gates existentes 1-7
- El gate debe ser backward compatible: si no hay `generated_assets` en context, skip gracefully
- Umbral 0.7 es configurable (para testing se puede bajar a 0.5)

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_gate_passes_when_all_above_threshold` | `tests/quality_gates/test_asset_confidence_gate.py` | PASA |
| `test_gate_warns_when_some_below_threshold` | `tests/quality_gates/test_asset_confidence_gate.py` | PASA |
| `test_gate_calculates_avg_correctly` | `tests/quality_gates/test_asset_confidence_gate.py` | PASA |
| `test_gate_empty_assets_list` | `tests/quality_gates/test_asset_confidence_gate.py` | PASA |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_asset_confidence_gate.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Criterios de Completitud (CHECKLIST)

- [ ] **Tests nuevos pasan**: Los 4 tests del gate ejecutan exitosamente
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: FASE-CONF-GATE marcada como ✅ Completada
- [ ] **Gate integrado**: Publication gates ahora incluye asset_confidence como gate #8
- [ ] **No hay regresión**: Gates 1-7 siguen funcionando igual

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**: Marcar FASE-CONF-GATE como ✅ Completada con fecha
2. **`06-checklist-implementacion.md`**: Marcar Tareas 1-4 como completadas
3. **`09-documentacion-post-proyecto.md`**:
   - Sección E: Agregar `modules/quality_gates/publication_gates.py` modificado
   - Sección D: Nueva métrica "Publication gates: 8 (incluye confidence)"
