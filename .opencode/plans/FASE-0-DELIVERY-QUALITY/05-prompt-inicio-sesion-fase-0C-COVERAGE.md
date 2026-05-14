# FASE-0C: Coverage Gate — No Silent Drop

> **Fase:** 0C  
> **Tipo:** Código + tests  
> **Comando largo:** No  
> **Dependencias:** 0B  
> **Máximo iteraciones:** 60  
> **Restricción:** TDD obligatorio. No ejecutar v4complete.

---

## Contexto

Lee primero:
1. `modules/quality_gates/publication_gates.py` (estructura de gates, `GateStatus`, `check_publication_readiness`)
2. `modules/commercial_documents/pain_solution_mapper.py` (`detect_pains`, `Pain`)
3. Este prompt

---

## Tareas

### Tarea 1: Implementar CoverageGate

En `modules/quality_gates/publication_gates.py`, agregar método:

```python
def _coverage_gate(self, pain_ledger: List[PainLedgerEntry], diagnostic_pain_ids: Set[str], proposal_pain_ids: Set[str]) -> PublicationGateResult
```

Regla:
```
brechas_en_diagnostico + brechas_justificadas == brechas_detectadas
```

- `passed=True` si todo pain_id en ledger aparece en diagnóstico, propuesta, o tiene `status` en (`JUSTIFIED_SKIP`, `BLOCKED`, `MAPPED_TO_SERVICE`).
- `passed=False` si algún pain_id detectado no aparece ni está justificado.
- `status=GateStatus.PASSED` / `FAILED`.

### Tarea 2: TDD — Tests de CoverageGate

Crear `tests/quality_gates/test_coverage_gate.py`:

**RED:**
- `test_fails_when_pain_detected_not_in_diagnostic_nor_justified()`
- `test_passes_when_pain_grouped_with_explicit_justification()`
- `test_passes_with_fixture_representative()`

Ejecutar → FAIL.

**GREEN:** Implementar mínimo.

**REFACTOR:** Limpiar.

### Tarea 3: Integrar en run_publication_gates

Agregar `_coverage_gate()` a `run_publication_gates()` con parámetros correctos.

Asegurar que el resultado aparezca en `gate_report_*.json`.

### Tarea 4: Regresión focalizada

```bash
pytest tests/quality_gates/ -v -k "coverage or publication"
pytest tests/ -v -k "gate" --timeout=60
```

Verificar que gates existentes no se rompen.

---

## Criterios de Completitud

- [ ] `_coverage_gate()` existe en `publication_gates.py`
- [ ] `tests/quality_gates/test_coverage_gate.py` existe, >= 3 tests, todos PASS
- [ ] `gate_report_*.json` incluye resultado de coverage gate
- [ ] Regresión: tests existentes de quality_gates pasan

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0C-COVERAGE \
    --desc "Coverage gate: ninguna brecha desaparece sin explicacion" \
    --archivos-mod "modules/quality_gates/publication_gates.py" \
    --archivos-nuevos "tests/quality_gates/test_coverage_gate.py" \
    --tests "3" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0C-1..0C-4 como ✅.
