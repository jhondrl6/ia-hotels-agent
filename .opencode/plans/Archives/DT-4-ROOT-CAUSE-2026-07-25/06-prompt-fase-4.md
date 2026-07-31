# Prompt de Inicio de Sesión: FASE-4 — Higiene Nombres Gates Duplicados

**Fase**: FASE-4 — FIX-PRIORITY-5: HALLAZGO-N1 Renombrar gates "coverage" duplicados
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: BAJA
**Ejecución**: **SUBAGENTE** ✅ — delegate_task viable (rename strings)
**Depende de**: — (independiente)
**Bloquea a**: FASE-RELEASE

---

## Objetivo

Renombrar los dos gates "coverage" que tienen el mismo nombre pero diferente contrato:
- Publication **G11 coverage** → `coverage_no_silent_drop` (evalúa pain_ledger coverage)
- Delivery quality **G7 coverage** → `coverage_failure_rate` (evalúa asset failure rate < 0.5)

---

## Contexto

HALLAZGO-N1: Dos sistemas independientes usan el mismo nombre "coverage" para cosas distintas:
- Publication G11 (`publication_gates.py:1188`): pain_ledger + diagnostic_pain_ids + proposal_pain_ids
- Delivery quality G7 (`delivery_quality_report.py:356-384`): failure_rate < 0.5 desde asset_generation_report

Mismo nombre, diferente contrato. Para Zi One: G7 PASS, G11 FAIL — pero el cliente solo ve "coverage".

---

## Tareas

### T1: Renombrar gates

**Archivos**: 
- `modules/quality_gates/publication_gates.py` — G11 `coverage` → `coverage_no_silent_drop`
- `modules/quality_gates/delivery_quality_report.py` — G7 `coverage_gate` → `coverage_failure_rate`

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Localizar los nombres actuales
grep -n '"coverage"' modules/quality_gates/publication_gates.py
grep -n '"coverage_gate"' modules/quality_gates/delivery_quality_report.py

# 2. Renombrar en publication_gates.py: "coverage" → "coverage_no_silent_drop"
#    (solo donde sea el gate_id string, NO en comentarios o nombres de variables)

# 3. Renombrar en delivery_quality_report.py: "coverage_gate" → "coverage_failure_rate"

# 4. Verificar que no haya otras referencias que necesiten actualización:
grep -rn '"coverage"\|"coverage_gate"' modules/ tests/ --include="*.py"
```

### T2: Actualizar tests y verificar

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli

# 1. Buscar tests que referencien los nombres viejos
grep -rn '"coverage"\|coverage_gate' tests/ --include="*.py"

# 2. Actualizar aserciones con los nuevos nombres

# 3. Ejecutar tests
./venv/Scripts/python.exe -m pytest tests/ -v -k "coverage or gate"
./venv/Scripts/python.exe -m pytest -q
```

---

## Criterios de Completitud

- [ ] Publication G11 gate_id: `coverage` → `coverage_no_silent_drop`
- [ ] Delivery quality G7 gate_id: `coverage_gate` → `coverage_failure_rate`
- [ ] Tests actualizados con nuevos nombres
- [ ] 100 tests existentes siguen PASS
- [ ] `grep -rn '"coverage"' modules/quality_gates/` no retorna gate_id strings viejos
- [ ] git commit con mensaje: "refactor(N1): rename duplicate coverage gates (G11→coverage_no_silent_drop, G7→coverage_failure_rate)"

---

## delegate_task Prompt (para subagente)

```
Implement FASE-4 of DT-4 plan for iah-cli project at /mnt/c/Users/Jhond/Github/iah-cli.

GOAL: Rename duplicate "coverage" gates that have same name but different contracts (HALLAZGO-N1).

CONTEXT:
Two independent gate systems use "coverage" for different things:
- Publication G11 (publication_gates.py:1188): checks pain_ledger coverage
- Delivery quality G7 (delivery_quality_report.py:356): checks asset failure_rate < 0.5

For Zi One: G7 PASS, G11 FAIL — but the name collision makes diagnosis confusing.

TASKS:
1. grep -n '"coverage"' modules/quality_gates/publication_gates.py to find the gate_id string
2. Rename publication G11 gate_id: "coverage" → "coverage_no_silent_drop"
3. grep -n '"coverage_gate"' modules/quality_gates/delivery_quality_report.py
4. Rename delivery G7 gate_id: "coverage_gate" → "coverage_failure_rate"
5. grep -rn '"coverage"\|coverage_gate' tests/ --include="*.py" to find test references
6. Update test assertions with new gate names
7. Run: ./venv/Scripts/python.exe -m pytest -q
8. git add + commit: "refactor(N1): rename duplicate coverage gates"

RESTRICTIONS:
- Only change gate_id strings, NOT variable names or comments
- Do NOT modify gate logic
- Keep existing tests passing
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-4 --desc "N1_renombrar_gates_coverage_duplicados" --check-manual-docs
```

---

## Siguiente Sesión

**FASE-RELEASE** — v4complete Zi One Luxury + version bump + análisis post-implementación
