# FASE-1: DT4-R1-CONTRACT — Fix pain_ledger_resolved injection

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA
> **Iteraciones máx**: 60
> **Depende de**: —
> **Bloquea a**: FASE-6 (E2E)

## ⚠️ HEchos Confirmados (NO re-verificar)

- `MAPPED_TO_SERVICE` **YA existe** en `_JUSTIFIED_STATUSES` (publication_gates.py:1186-1188). NO agregarlo.
- `publication_gates.py:1232-1238` YA espera `pain_ledger_resolved` en el assessment, pero el campo nunca se inyecta.
- `v4_asset_orchestrator.py:521-533` YA genera `pain_ledger_resolved.json` correctamente pero descarta el resultado.
- `AssessmentPayload` NO tiene campo `pain_ledger_resolved`.
- `AssessmentBuilder` NO tiene método para inyectarlo.
- `main.py` NO carga `pain_ledger_resolved.json`.

## Objetivo

Integrar el `pain_ledger_resolved` (generado por el reconciliador post-orchestrator) al `AssessmentPayload` y al flujo de `main.py` para que el coverage gate reciba el ledger reconciliado, no el original.

## Tareas

### T1: Agregar `pain_ledger_resolved` al contrato `AssessmentPayload`

- **Archivo**: `modules/assessment_builder.py`
- Agregar campo en `AssessmentPayload`:
  ```python
  pain_ledger_resolved: List[Dict] = field(default_factory=list)
  ```
- Agregar en `to_dict()` si no está ya incluido por `dataclasses.asdict()`.
- **Verificación**: `grep "pain_ledger_resolved" modules/assessment_builder.py` debe mostrar 2+ ocurrencias (campo + builder method después de T3).

### T2: Exponer resultado reconciliado desde `AssetGenerationResult` + cargar en `main.py`

- **Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`
  - El método `reconcile()` en L521-533 ya retorna el resultado. Modificar `AssetGenerationResult` (o el diccionario que se retorna) para incluir `pain_ledger_resolved_entries`.
  - Agregar campo `pain_ledger_resolved: Optional[List[Dict]] = None` en `AssetGenerationResult` si no existe.

- **Archivo**: `main.py`
  - Después de la ejecución del orchestrator (~L2657-2661 donde se carga `pain_ledger.json` original), agregar carga de `pain_ledger_resolved.json`:
    ```python
    pain_ledger_resolved_path = output_dir / "v4_audit" / "pain_ledger_resolved.json"
    pain_ledger_resolved_entries = None
    if pain_ledger_resolved_path.exists():
        pain_ledger_resolved_entries = PainLedger().load(pain_ledger_resolved_path)
    ```

### T3: Crear `AssessmentBuilder.with_resolved_pain_ledger()` + inyectar antes de gates + BLOCKED en ausencia

- **Archivo**: `modules/assessment_builder.py`
  - Agregar método:
    ```python
    def with_resolved_pain_ledger(self, entries: List[Dict]) -> "AssessmentBuilder":
        self._payload.pain_ledger_resolved = entries
        return self
    ```

- **Archivo**: `main.py`
  - En la cadena del builder (~L2764), agregar después de `with_pain_ledger()`:
    ```python
    if pain_ledger_resolved_entries:
        builder.with_resolved_pain_ledger(pain_ledger_resolved_entries)
    ```

- **Archivo**: `modules/quality_gates/publication_gates.py`
  - En `_coverage_gate()` (L1232-1238), modificar el fallback: si `pain_ledger_resolved` no existe pero el assessment tiene `pain_ledger` con entries DETECTED, emitir warning pero NO hacer fallback silencioso. El gate ya tiene la lógica de fallback; verificar que funcione correctamente ahora que el campo existe.
  - Si el reconciliador NO se ejecutó (no hay `pain_ledger_resolved`), el comportamiento actual (fallback a `pain_ledger`) es correcto. Pero si SÍ se ejecutó y el campo está vacío, es un error → BLOCKED.

### T4: Integration test — reconciler → builder → assessment → coverage gate

- **Archivo**: `tests/quality_gates/test_coverage_gate.py` (o nuevo archivo `test_coverage_gate_integration.py`)
- Test integrado que:
  1. Simula `pain_ledger.json` con `no_whatsapp_visible: DETECTED`
  2. Simula `asset_generation_report.json` con `whatsapp_button: exists`
  3. Ejecuta `PostOrchestratorReconciler.reconcile()`
  4. Construye `AssessmentPayload` con `pain_ledger_resolved`
  5. Pasa el assessment a `_coverage_gate()`
  6. Verifica: `result.passed is True`, `result.details["justified"] >= 1`, `no_whatsapp_visible` en `uncovered = []`
- Usar fixtures existentes de `test_coverage_gate.py` como base.
- **Verificación**: `./venv/Scripts/python.exe -m pytest tests/quality_gates/test_coverage_gate.py -q -k "resolved"`

## Criterios de Completitud

- [ ] `AssessmentPayload` tiene campo `pain_ledger_resolved: List[Dict]`
- [ ] `AssessmentBuilder.with_resolved_pain_ledger()` existe y funciona
- [ ] `main.py` carga `pain_ledger_resolved.json` si existe
- [ ] `main.py` inyecta el ledger reconciliado al builder
- [ ] Coverage gate recibe `pain_ledger_resolved` en el assessment (verificable con grep)
- [ ] Test de integración: reconciler → builder → gate PASS
- [ ] Tests existentes no rompen: `./venv/Scripts/python.exe -m pytest tests/quality_gates/test_coverage_gate.py tests/test_assessment_builder.py tests/test_post_orchestrator_reconciler.py -q`
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO modificar `_JUSTIFIED_STATUSES`** — ya contiene `MAPPED_TO_SERVICE`
- **NO modificar `PostOrchestratorReconciler`** — ya funciona correctamente
- **NO ejecutar v4complete**
- **NO modificar `publication_gates.py` excepto el fallback en `_coverage_gate()`**
- Máximo 60 iteraciones
- Si se alcanza el límite: marcar INCOMPLETA, documentar checkpoint, NO continuar

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1 \
    --desc "DT4-R1-CONTRACT: pain_ledger_resolved injection into AssessmentPayload + builder + main.py integration" \
    --archivos-mod "modules/assessment_builder.py,modules/quality_gates/publication_gates.py,modules/asset_generation/v4_asset_orchestrator.py,main.py" \
    --archivos-nuevos "tests/quality_gates/test_coverage_gate_integration.py" \
    --tests "1" \
    --check-manual-docs
```

## Próxima Sesión

FASE-2: DT4-R2-SITE-PRESENCE — Normalización canónica de SitePresence + wiring a CoherenceValidator (MAYOR COMPLEJIDAD TÉCNICA)
