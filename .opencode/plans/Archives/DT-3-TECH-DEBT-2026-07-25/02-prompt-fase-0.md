# FASE-0: Fix Sistémico de Rutas Flat → Per-Hotel (BUG-1)

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: SUBAJENTE (delegate_task viable — code-editing puro, sin imports del proyecto)
> **Complejidad**: MEDIA
> **Iteraciones máx**: 60
> **Depende de**: — (causa raíz, sin dependencias previas)
> **Bloquea a**: FASE-1, FASE-2, FASE-3

---

## Objetivo

Corregir BUG-1: la migración flat → per-hotel fue parcial. P-06 (DT-2) fixeó UN archivo (`proposal_asset_matrix.json`) pero 3 archivos más quedaron con ruta flat inexistente. Esto causa que ProposalAssetMatrix reciba `pain_ledger_entries = []` → 8/8 NO_BREACH → G9 FAIL → delivery bloqueado.

**Fix**: Cambiar 3 rutas flat → per-hotel + crear helper `_get_pipeline_path()` para prevenir recurrencia.

---

## Contexto de Fases Anteriores

Ninguna. Esta es la primera fase del plan DT-3.

**Estado inicial del repo**:
- VERSION.yaml: 4.63.2
- Tag: v4.63.2 (dd576a2)
- Tests: 42/42 PASS (test_delivery_contract.py)
- main.py: 3462 líneas
- Patrón per-hotel YA existe en el código (L2908: `output_dir / hotel_id / "v4_audit"`)

---

## Tareas

### T1: Crear helper `_get_pipeline_path()` en main.py

Crear una función helper que unifique la construcción de rutas per-hotel. Insertar cerca de L2560 (antes del bloque G1 sync).

```python
def _get_pipeline_path(output_dir: Path, hotel_id: str, filename: str) -> Path:
    """Construye ruta per-hotel para archivos JSON del pipeline.
    
    Centraliza el patrón output_dir / hotel_id / "v4_audit" / filename
    para evitar recurrencia de rutas flat (BUG-1, DT-3).
    """
    return output_dir / hotel_id / "v4_audit" / filename
```

### T2: Corregir pain_ledger.json path (L2650)

```diff
- pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"
+ pain_ledger_path = _get_pipeline_path(output_dir, hotel_id, "pain_ledger.json")
```

### T3: Corregir coherence_validation paths (L2571-2572)

```diff
- cv_post_path = output_dir / "v4_audit" / "coherence_validation_post_gen.json"
- cv_path = output_dir / "v4_audit" / "coherence_validation.json"
+ cv_post_path = _get_pipeline_path(output_dir, hotel_id, "coherence_validation_post_gen.json")
+ cv_path = _get_pipeline_path(output_dir, hotel_id, "coherence_validation.json")
```

### T4: Auditar TODOS los JSON reads en main.py para detectar rutas flat residuales

Ejecutar y verificar que NO queden otras rutas flat:

```bash
grep -n 'output_dir / "v4_audit"' main.py
```

Si aparecen resultados además de L3063 y L3228 (que usan `output_dir` sin `hotel_id` en contexto diferente — son paths de entrega, no de lectura), documentarlos. La meta es **0 rutas flat de lectura**.

---

## Criterios de Completitud

- [ ] Helper `_get_pipeline_path()` creado y funcional
- [ ] L2650: `pain_ledger_path` usa helper
- [ ] L2571: `cv_post_path` usa helper
- [ ] L2572: `cv_path` usa helper
- [ ] `grep -n 'output_dir / "v4_audit"' main.py` muestra solo L3063 y L3228 (paths de entrega, no de lectura)
- [ ] `git diff --stat` muestra solo main.py modificado
- [ ] No hay errores de sintaxis (el helper es standalone, no requiere imports nuevos)

---

## Restricciones

- **NO modificar** L3063 ni L3228 (son paths de entrega/output, no de lectura)
- **NO modificar** PAIN_SOLUTION_MAP (BUG-5 fue refutado)
- **NO modificar** delivery_quality_report.py (eso es FASE-1)
- **NO ejecutar v4complete** (eso es FASE-3)
- **NO ejecutar tests** (requiere Windows venv; se verifican en FASE-3)

---

## delegate_task Prompt (para subagente)

```
GOAL: Fix BUG-1 in iah-cli main.py — correct 3 flat JSON paths to per-hotel paths.

CONTEXT:
Project: /mnt/c/Users/Jhond/Github/iah-cli
File to modify: main.py (3462 lines)

The pipeline migrated from flat output structure to per-hotel, but 3 JSON reads
were left behind using flat paths that no longer exist. The per-hotel pattern
is already used elsewhere in the code (L2908: output_dir / hotel_id / "v4_audit").

TASKS:
1. Add helper function _get_pipeline_path(output_dir, hotel_id, filename) near L2560
   that returns: output_dir / hotel_id / "v4_audit" / filename

2. Fix L2650: pain_ledger_path = output_dir / "v4_audit" / "pain_ledger.json"
   → pain_ledger_path = _get_pipeline_path(output_dir, hotel_id, "pain_ledger.json")

3. Fix L2571: cv_post_path = output_dir / "v4_audit" / "coherence_validation_post_gen.json"
   → cv_post_path = _get_pipeline_path(output_dir, hotel_id, "coherence_validation_post_gen.json")

4. Fix L2572: cv_path = output_dir / "v4_audit" / "coherence_validation.json"
   → cv_path = _get_pipeline_path(output_dir, hotel_id, "coherence_validation.json")

5. Verify: grep -n 'output_dir / "v4_audit"' main.py should ONLY show L3063 and L3228
   (those are delivery output paths, not reads — do NOT modify them)

RESTRICTIONS:
- Do NOT modify L3063 or L3228
- Do NOT modify any other files
- Do NOT run tests (they require Windows venv)
- Do NOT run v4complete
- Use patch() for edits, not write_file (to avoid overwriting the 3462-line file)

VERIFICATION: After all patches, the 3 lines should use _get_pipeline_path() and
grep should confirm no flat read paths remain.
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cmd.exe /c "C:\Users\Jhond\Github\iah-cli\venv\Scripts\python.exe scripts\log_phase_completion.py --fase FASE-0 --plan DT-3-TECH-DEBT-2026-07-25 --desc BUG-1_systemic_path_fix"
```

---

## Próxima Sesión

**FASE-1**: Corregir BUG-2 (G9 dual-list) + BUG-3 (G9 status-based eval) en delivery_quality_report.py
