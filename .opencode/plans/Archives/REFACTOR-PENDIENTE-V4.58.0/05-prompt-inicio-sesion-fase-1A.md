# FASE-1A: IMP-03 (CAPEX Breakdown) + F7 (Gate Discrepancy)

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DELEGAR vía `delegate_task` con toolsets `['terminal', 'file']`

## Contexto previo

- **FASE-0 completada** ✅: Verificación contra código vivo confirmada.
- Gaps confirmados aún vigentes: IMP-03, F7, F5, MIN-01, MIN-02, MIN-03, dead code.
- Baseline de tests documentado.

## Objetivo de esta fase

Resolver 2 gaps de bajo esfuerzo:
1. **IMP-03**: CAPEX breakdown se produce en código pero el template no lo consume
2. **F7**: Dos gates evalúan evidence tier con lógicas diferentes, confundiendo al lector

---

### Tareas

- [ ] **T1: Añadir `${capex_breakdown_table}` en propuesta_v6_template.md**

  El método `_build_capex_breakdown_table()` ya produce el dato en `v4_proposal_generator.py`.
  El template `propuesta_v6_template.md` solo tiene `${capex_total}` — falta el desglose.

  **Acción:**
  1. Leer el template alrededor de L141 donde aparece `${capex_total}`
  2. Añadir `${capex_breakdown_table}` INMEDIATAMENTE DESPUÉS de `${capex_total}`
  3. Verificar que `_build_capex_breakdown_table()` ya existe en el generador:
     ```bash
     grep -n "_build_capex_breakdown_table" modules/commercial_documents/v4_proposal_generator.py
     ```
  4. Verificar que el data dict ya incluye la key `'capex_breakdown_table'`:
     ```bash
     grep -n "capex_breakdown_table" modules/commercial_documents/v4_proposal_generator.py
     ```

  **Nota:** También eliminar la referencia a `${capex_breakdown_table}` en el template EMBEBIDO
  (si existe en `v4_proposal_generator.py` L593) — pero NO eliminar el template embebido completo;
  eso va en FASE-5.

- [ ] **T2: Unificar lógica de `financial_validity` gate**

  **Problema:** `financial_validity` usa heurística de source-level (any default → Tier C warning)
  mientras `tier_c_onboarding_required` usa `_determine_evidence_tier()` formal.

  **Acción:**
  1. Leer la función `financial_validity` en `modules/quality_gates/publication_gates.py`
  2. Buscar dónde genera el mensaje "Tier C evidence"
  3. Reemplazar la heurística propia por lectura de `financial_breakdown.evidence_tier`
     (o `assessment['evidence_tier']` según la estructura disponible)
  4. Asegurar que AMBAS gates reporten el mismo tier cuando evalúan el mismo concepto
  5. Mantener el WARNING como tal (no convertir a FAIL), solo corregir el texto del tier

- [ ] **T3: Tests de regresión**
  ```bash
  cd /mnt/c/Users/Jhond/Github/iah-cli
  ./venv/Scripts/python.exe -m pytest tests/ --timeout=60 -x -q 2>&1 | tail -20
  ```
  Si algún test falla, investigar y corregir ANTES de cerrar la fase.

- [ ] **T4: Actualizar estado de fase**
  Marcar T1-T4 como completadas en `06-checklist-implementacion.md`.

### Restricciones

- **NO ejecutar v4complete** en esta fase
- **NO modificar código de `v4_proposal_generator.py`** excepto la key en data dict si falta
- **NO modificar `regional_benchmarks.yaml`** — eso va en FASE-2
- **NO eliminar el template embebido L575-605** — eso va en FASE-5
- Máximo 60 iteraciones (R2)
- Si `template_embebido` test existe, no romperlo

### Criterios de completitud

- [ ] `${capex_breakdown_table}` aparece en `propuesta_v6_template.md` después de `${capex_total}`
- [ ] `financial_validity` gate usa `evidence_tier` formal en vez de heurística de source-level
- [ ] Todos los tests existentes pasan
- [ ] Estado actualizado en checklist

### Archivos involucrados

| Archivo | Cambio |
|---------|--------|
| `modules/commercial_documents/templates/propuesta_v6_template.md` | Añadir placeholder |
| `modules/quality_gates/publication_gates.py` | Unificar lógica de tier |

### Próxima sesión

```
Carga y ejecuta /.opencode/plans/Archives/REFACTOR-PENDIENTE-V4.58.0/05-prompt-inicio-sesion-fase-1B.md
```

Esa fase resuelve el bug F5 (ADR checklist siempre [PENDING]).
