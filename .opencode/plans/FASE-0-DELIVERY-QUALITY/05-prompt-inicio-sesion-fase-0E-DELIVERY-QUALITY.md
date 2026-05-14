# FASE-0E: Delivery Quality Report Bloqueante

> **Fase:** 0E  
> **Tipo:** Código + tests  
> **Comando largo:** No  
> **Dependencias:** 0D  
> **Máximo iteraciones:** 60  
> **Restricción:** TDD obligatorio. No ejecutar v4complete.

---

## Contexto

Lee primero:
1. `modules/quality_gates/publication_gates.py` (`check_publication_readiness`, `GateStatus`)
2. `modules/asset_generation/v4_asset_orchestrator.py` (`AssetGenerationResult`)
3. Este prompt

---

## Tareas

### Tarea 1: Implementar DeliveryQualityReport

Crear `modules/quality_gates/delivery_quality_report.py`:

```python
@dataclass
class DeliveryQualityReport:
    status: str          # PASS | FAIL | WARNING
    blocking: bool
    coverage_gate: dict
    proposal_asset_gate: dict
    asset_specificity_gate: dict
    evidence_gate: dict
    human_review_items: List[str]
    summary: dict

class DeliveryQualityReportGenerator:
    def generate(self, hotel_id: str, v4_audit_path: Path) -> DeliveryQualityReport
    def save(self, report: DeliveryQualityReport, path: Path)
```

Reglas:
- FAIL bloquea ZIP/publicación.
- WARNING visible pero no bloqueante.
- PASS requiere G6/G7/G8 satisfechos (coherence >= 0.8, coverage PASS, asset specificity PASS).

### Tarea 2: TDD — Tests

Crear `tests/quality_gates/test_delivery_quality_report.py`:

**RED:**
- `test_fail_blocks_publication()`
- `test_warning_does_not_block()`
- `test_pass_requires_gates_satisfied()`

**GREEN:** Implementar.

**REFACTOR.**

### Tarea 3: Integrar en main.py antes de ZIP

Modificar `main.py`:
- Después de generar assets y antes de `create_delivery_package()`, llamar `DeliveryQualityReportGenerator.generate()`.
- Guardar en `output/v4_complete/<hotel>/v4_audit/delivery_quality_report.json`.
- Si `status == FAIL`, abortar ZIP y loguear motivo.

### Tarea 4: Regresión focalizada

```bash
pytest tests/quality_gates/test_delivery_quality_report.py -v
pytest tests/ -v -k "publication or gate" --timeout=60
```

Verificar que publicación actual no se rompe.

---

## Criterios de Completitud

- [ ] `modules/quality_gates/delivery_quality_report.py` existe
- [ ] `tests/quality_gates/test_delivery_quality_report.py` existe, >= 3 tests, todos PASS
- [ ] `main.py` genera reporte antes de ZIP y aborta si FAIL
- [ ] Regresión: tests existentes de publicación/gates pasan

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0E-DELIVERY-QUALITY \
    --desc "Delivery quality report bloqueante pre-ZIP" \
    --archivos-nuevos "modules/quality_gates/delivery_quality_report.py,tests/quality_gates/test_delivery_quality_report.py" \
    --archivos-mod "main.py" \
    --tests "3" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0E-1..0E-4 como ✅.
