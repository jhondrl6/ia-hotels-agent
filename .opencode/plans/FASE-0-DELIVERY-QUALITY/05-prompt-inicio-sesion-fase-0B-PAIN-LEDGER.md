# FASE-0B: Pain Ledger — Fuente de Verdad de Brechas

> **Fase:** 0B  
> **Tipo:** Código + tests  
> **Comando largo:** No  
> **Dependencias:** 0A  
> **Máximo iteraciones:** 60  
> **Restricción:** TDD obligatorio. No ejecutar v4complete.

---

## Contexto

Lee primero:
1. `FASE-0-CONTEXTO-IMPLEMENTACION-ROADMAP.md` §5.4, §8 GAP-H2
2. `modules/commercial_documents/pain_solution_mapper.py` (estructura `Pain`, `detect_pains`)
3. `modules/asset_generation/v4_asset_orchestrator.py` (uso de `pain_ids_resolved`)
4. Este prompt

---

## Tareas

### Tarea 1: Diseñar PainLedger facade

Definir en un nuevo archivo `modules/asset_generation/pain_ledger.py`:

```python
@dataclass
class PainLedgerEntry:
    pain_id: str
    source_module: str
    source_file: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    confidence: float
    status: str    # DETECTED | DIAGNOSED | MAPPED_TO_SERVICE | ASSET_GENERATED | JUSTIFIED_SKIP | BLOCKED
    human_label: str
    evidence_refs: List[str]

class PainLedger:
    def from_pains(self, pains: List[Pain], source_module: str) -> List[PainLedgerEntry]
    def to_dict(self) -> dict
    def save(self, path: Path)
    def load(self, path: Path) -> List[PainLedgerEntry]
```

Reglas:
- Normalizar `pain_id` desde detecciones existentes.
- Conservar backward compat con `pain_ids_resolved`.
- Serializar JSON reproducible.

### Tarea 2: Implementar con TDD

**Step 1 (RED):** Escribir test en `tests/asset_generation/test_pain_ledger.py`:
- `test_ledger_normalizes_pain_ids()`
- `test_ledger_serializes_reproducibly()`
- `test_ledger_backward_compat_with_pain_ids_resolved()`

Ejecutar: `pytest tests/asset_generation/test_pain_ledger.py -v` → esperar FAIL.

**Step 2 (GREEN):** Implementar mínimo en `pain_ledger.py`.

**Step 3:** Ejecutar tests → PASS.

**Step 4 (REFACTOR):** Limpiar si aplica.

### Tarea 3: Integrar en v4_asset_orchestrator

Modificar `modules/asset_generation/v4_asset_orchestrator.py`:
- Después de `detect_pains()`, instanciar `PainLedger`.
- Guardar `pain_ledger.json` en `output/v4_complete/<hotel>/v4_audit/pain_ledger.json`.

Verificar con fixture/mock (no requiere v4complete):
```python
# Test de integración ligero
python -c "from modules.asset_generation.pain_ledger import PainLedger; ..."
```

### Tarea 4: Regresión focalizada

Ejecutar:
```bash
pytest tests/asset_generation/ -v -k "pain_ledger or v4_asset_orchestrator"
pytest tests/commercial_documents/test_pain_solution_mapper.py -v
```

Verificar que tests existentes no se rompen.

---

## Criterios de Completitud

- [ ] `modules/asset_generation/pain_ledger.py` existe y pasa lint
- [ ] `tests/asset_generation/test_pain_ledger.py` existe, >= 3 tests, todos PASS
- [ ] `v4_asset_orchestrator.py` escribe `pain_ledger.json` en path correcto
- [ ] Tests de regresión pasan

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0B-PAIN-LEDGER \
    --desc "Crear PainLedger facade sobre PainSolutionMapper" \
    --archivos-nuevos "modules/asset_generation/pain_ledger.py,tests/asset_generation/test_pain_ledger.py" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py" \
    --tests "3" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0B-1..0B-4 como ✅.
