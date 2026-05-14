# FASE-0D: Matriz Propuesta → Brecha → Asset

> **Fase:** 0D  
> **Tipo:** Código + tests  
> **Comando largo:** No  
> **Dependencias:** 0C  
> **Máximo iteraciones:** 60  
> **Restricción:** TDD obligatorio. No ejecutar v4complete.
> **Estado:** ✅ COMPLETADA — 2026-05-13
> **Sesión:** 20260513_fase0d_proposal_asset
> **Iteraciones usadas:** ~25

---

## Contexto

Lee primero:
1. `modules/asset_generation/proposal_asset_alignment.py` (`PROPOSAL_SERVICE_TO_ASSET`)
2. `modules/commercial_documents/v4_proposal_generator.py` (`_generate_dynamic_services_table`, `_generate_asset_quality_table`)
3. `modules/asset_generation/asset_diagnostic_linker.py` (`AssetDiagnosticLink`)
4. Este prompt

---

## Tareas

### Tarea 1: Extender ProposalAssetMatrix

En `modules/asset_generation/proposal_asset_alignment.py`, agregar clase:

```python
@dataclass
class ProposalAssetMatrixEntry:
    service_name: str
    pain_ids: List[str]
    asset_type: str
    asset_path: Optional[str]
    confidence: float
    status: str  # LINKED | MISSING_ASSET | NO_BREACH | GENERIC_DRAFT

class ProposalAssetMatrix:
    def build(self, proposal_services: List[str], pain_ledger: List[PainLedgerEntry], generated_assets: List[GeneratedAsset]) -> List[ProposalAssetMatrixEntry]
    def save(self, path: Path)
```

Reglas:
- Todo servicio vendido debe mapear a brecha real (pain_id en ledger).
- Todo servicio vendido debe tener asset específico o quedar marcado `MISSING_ASSET`.
- Asset existente debe resolver pain_id asociado.

### Tarea 2: TDD — Tests

Crear `tests/asset_generation/test_proposal_asset_matrix.py`:

**RED:**
- `test_fails_when_service_sold_without_real_breach()`
- `test_fails_when_service_sold_without_asset()`
- `test_passes_when_service_present_and_justified()`

**GREEN:** Implementar.

**REFACTOR.**

### Tarea 3: Integrar en v4_proposal_generator

Modificar `modules/commercial_documents/v4_proposal_generator.py`:
- Después de generar propuesta, construir `ProposalAssetMatrix`.
- Guardar `proposal_asset_matrix.json` en `v4_audit/`.

Asegurar backward compat con `PROPOSAL_SERVICE_TO_ASSET` estático.

### Tarea 4: Regresión focalizada

```bash
pytest tests/asset_generation/test_proposal_asset_matrix.py -v
pytest tests/commercial_documents/test_proposal_dynamic.py -v
pytest tests/commercial_documents/test_proposal_alignment.py -v
```

---

## Criterios de Completitud

- [ ] `ProposalAssetMatrix` existe en `proposal_asset_alignment.py`
- [ ] `tests/asset_generation/test_proposal_asset_matrix.py` existe, >= 3 tests, todos PASS
- [ ] `v4_proposal_generator.py` escribe `proposal_asset_matrix.json`
- [ ] Tests de propuesta existentes no se rompen

---

## Post-Ejecución

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-0D-PROPOSAL-ASSET \
    --desc "Matriz propuesta-brecha-asset con trazabilidad" \
    --archivos-mod "modules/asset_generation/proposal_asset_alignment.py,modules/commercial_documents/v4_proposal_generator.py" \
    --archivos-nuevos "tests/asset_generation/test_proposal_asset_matrix.py" \
    --tests "3" \
    --check-manual-docs
```

Actualizar `06-checklist-implementacion.md`: marcar 0D-1..0D-4 como ✅.
