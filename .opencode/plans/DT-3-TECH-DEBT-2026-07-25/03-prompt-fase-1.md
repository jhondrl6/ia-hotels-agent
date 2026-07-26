# FASE-1: Fix G9 Dual-List + Status-Based Evaluation (BUG-2, BUG-3)

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAJENTE (delegate_task viable — fixes pequeños, un solo archivo, sin imports del proyecto)
> **Complejidad**: BAJA
> **Iteraciones máx**: 60
> **Depende de**: FASE-0 ✅ (BUG-1 corregido — pain_ledger se carga correctamente)
> **Bloquea a**: FASE-2, FASE-3

---

## Objetivo

Corregir dos bugs en G9 (`delivery_quality_report.py`):

1. **BUG-2 (dual-list)**: G9 aparece simultáneamente en `blocking_gates` Y `warning_gates` en `delivery_quality_report.json`. Causa: la tupla de exclusión en L257 no incluye `"proposal_asset_alignment"` porque se escribió cuando G9 NO era blocking.

2. **BUG-3 (status-based eval)**: G9 evalúa `asset_path is not None` en vez de `status`. Esto no distingue `NO_BREACH` (dolor no existe → legítimo) de `MISSING_ASSET` (dolor existe pero asset no generado → fallo real).

---

## Contexto de Fases Anteriores

**FASE-0 completada**: BUG-1 corregido. `_get_pipeline_path()` existe en main.py. Las 3 rutas flat (L2571, L2572, L2650) ahora usan paths per-hotel. Con este fix, `pain_ledger_entries` ya no estará vacío para Zi One.

**Estado actual del archivo**:
- `delivery_quality_report.py`: 456 líneas
- G9 gate: L193-219
- Blocking/warning gates: L251-258
- aligned_services: L201-204 (evalúa `asset_path`, no `status`)

---

## Tareas

### T1: Fix BUG-2 — Unificar BLOCKING_GATE_NAMES constante

Crear UNA constante y usarla en ambos lugares (inclusión L253 y exclusión L257):

```python
# Al inicio del método (antes de L251), agregar:
BLOCKING_GATE_NAMES = ("coherence", "coverage", "evidence", "proposal_asset_alignment")

# L251-254: usar la constante
blocking_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name in BLOCKING_GATE_NAMES
]

# L255-258: usar la misma constante para exclusión
warning_gates = [
    name for name, result in gate_results.items()
    if not result["passed"] and name not in BLOCKING_GATE_NAMES
]
```

Esto elimina la divergencia de 2 líneas que debieron actualizarse juntas.

### T2: Fix BUG-3 — G9 evalúa status, no asset_path

Cambiar L201-204 para evaluar `status` del entry en vez de `asset_path`:

```python
# ANTES (L201-204):
aligned_services = sum(
    1 for e in entries
    if e.get("asset_path") is not None and e.get("asset_path") != ""
)

# DESPUÉS:
def _is_service_aligned(entry: dict) -> bool:
    """Determina si un servicio está alineado evaluando su status.
    
    - LINKED: asset existe → PASS
    - MISSING_ASSET: dolor existe pero asset falta → FAIL
    - NO_BREACH: dolor no existe → SKIP (no cuenta como fallo)
    - GENERIC_DRAFT: placeholder genérico → FAIL
    """
    status = entry.get("status", "")
    if status == "LINKED":
        return True
    elif status == "NO_BREACH":
        return True  # No es fallo de delivery — el dolor no aplica
    else:
        return False

aligned_services = sum(1 for e in entries if _is_service_aligned(e))
```

La clave semántica: `NO_BREACH` = "este servicio no debería estar en la propuesta porque el dolor no existe" → NO es un fallo de delivery.

### T3: Actualizar passed condition para reflejar nueva semántica

```python
# ANTES (L205):
passed = aligned_services == total_services if total_services > 0 else True

# DESPUÉS:
# Contar solo servicios que DEBERÍAN tener asset (excluyendo NO_BREACH)
actionable_services = sum(
    1 for e in entries
    if e.get("status") != "NO_BREACH"
)
passed = aligned_services == actionable_services if actionable_services > 0 else True
```

Esto evita que `NO_BREACH` bloquee el delivery: si 8 servicios tienen 6 LINKED + 2 NO_BREACH, `aligned_services=8`, `actionable_services=6`, `passed=True`.

---

## Criterios de Completitud

- [ ] `BLOCKING_GATE_NAMES` constante definida y usada en L253 y L257
- [ ] `_is_service_aligned()` helper implementado
- [ ] `aligned_services` calculado con status, no asset_path
- [ ] `actionable_services` excluye NO_BREACH
- [ ] `grep "proposal_asset_alignment" delivery_quality_report.py` muestra la constante + su uso en blocking_gates y warning_gates (misma fuente)
- [ ] Sin errores de sintaxis

---

## Restricciones

- **NO modificar** main.py (eso fue FASE-0)
- **NO modificar** proposal_asset_alignment.py (eso es FASE-2)
- **NO ejecutar v4complete** (eso es FASE-3)
- **NO ejecutar tests** (requiere Windows venv; se verifican en FASE-3)

---

## delegate_task Prompt (para subagente)

```
GOAL: Fix BUG-2 and BUG-3 in iah-cli delivery_quality_report.py — G9 dual-list and status-based evaluation.

CONTEXT:
Project: /mnt/c/Users/Jhond/Github/iah-cli
File to modify: modules/quality_gates/delivery_quality_report.py (456 lines)

BUG-2: G9 appears in BOTH blocking_gates AND warning_gates because the exclusion tuple
at ~L257 was written when proposal_asset_alignment was NOT blocking. When it was promoted
to blocking in DT-2, only the inclusion tuple (~L253) was updated.

BUG-3: G9 evaluates asset_path is not None (~L201-204) instead of entry status.
NO_BREACH entries have asset_path=null but are LEGITIMATE (pain doesn't exist for this hotel).
MISSING_ASSET entries also have asset_path=null but are REAL failures (pain exists, asset missing).
The current code treats them identically → false positive blocking.

TASKS:
1. Add constant BLOCKING_GATE_NAMES = ("coherence", "coverage", "evidence", "proposal_asset_alignment")
   before the blocking_gates list comprehension. Use it in BOTH blocking_gates (L253) AND
   warning_gates exclusion (L257).

2. Add helper _is_service_aligned(entry) that returns True for LINKED and NO_BREACH,
   False for MISSING_ASSET and GENERIC_DRAFT. Replace the aligned_services count at L201-204.

3. Add actionable_services count that excludes NO_BREACH entries. Change the 'passed'
   condition to compare aligned_services == actionable_services instead of total_services.

4. Verify with grep that "proposal_asset_alignment" appears only in BLOCKING_GATE_NAMES
   constant definition, not hardcoded in the list comprehensions.

RESTRICTIONS:
- Do NOT modify any other files
- Do NOT run tests
- Do NOT run v4complete
- Use patch() for edits

VERIFICATION: After fixes, grep for "proposal_asset_alignment" in the file should show
it ONLY in the BLOCKING_GATE_NAMES constant and in the gate_results key assignment (~L206, ~L214).
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-1 --plan DT-3-TECH-DEBT-2026-07-25 --desc BUG2_BUG3_G9_fixes"
```

---

## Próxima Sesión

**FASE-2**: Unificar ProposalAssetMatrix + AlignmentReport (BUG-4 / P-04). **Fase de mayor complejidad técnica.**
