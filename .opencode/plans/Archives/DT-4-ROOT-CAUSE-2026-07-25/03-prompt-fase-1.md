# Prompt de Inicio de Sesión: FASE-1 — Reinterpretación Comercial del Optimista

**Fase**: FASE-1 — FIX-PRIORITY-3: BUG-8 Reinterpretación comercial del escenario optimista
**Plan**: DT-4-ROOT-CAUSE-2026-07-25
**Sesión**: Nueva (fresh)
**Iteraciones máx**: 60
**Complejidad**: BAJA
**Ejecución**: **SUBAGENTE** ✅ — delegate_task viable (2 funciones en 1 archivo)
**Depende de**: — (independiente)
**Bloquea a**: FASE-RELEASE

---

## Objetivo

Corregir la interpretación comercial del escenario financiero optimista cuando se vuelve negativo. El cálculo matemático es CORRECTO (cuando ahorros + revenue superan la pérdida OTA, el neto es negativo → "sin pérdida neta" = mejor escenario posible). El problema es que `_check_scenario_negative` y `_check_scenario_order` tratan el valor negativo como BLOCKING cuando debería ser un WARNING (el hotel está en una posición excelente).

---

## Contexto

El optimista se calcula como:
```
monthly_loss = current_ota_commission_loss - savings - ia_revenue
```

Para Zi One: $7.7M OTA loss - $774K savings - $3.2M IA revenue = **-$270K**
→ Matemáticamente correcto: "los ahorros + IA revenue SUPERAN la pérdida actual"

La solución es Opción B: reinterpretación comercial. NO se modifica la fórmula matemática (no requiere N≥5 observaciones).

---

## Tareas

### T1: Modificar `_check_scenario_negative` en commercial_gate.py

**Archivo**: `modules/quality_gates/commercial_gate.py`

Cambiar el check de BLOCKING a WARNING cuando `optimistic < 0 AND realistic > 0`:

```python
# En _check_scenario_negative (aprox L328-362):
# Buscar la línea donde optimistic_value < 0 dispara blocking:

# Antes (conceptual):
if optimistic_value < 0:
    return GateResult(
        gate_id="CG-SCENARIO-NEGATIVE",
        passed=False,
        blocking=True,
        message="Optimistic scenario is negative — cannot be presented as recovery",
    )

# Después:
if optimistic_value < 0:
    is_blocking = realistic_value <= 0  # Solo blocking si realista también es negativo
    severity = "BLOCKING" if is_blocking else "WARNING"
    return GateResult(
        gate_id="CG-SCENARIO-NEGATIVE",
        passed=not is_blocking,
        blocking=is_blocking,
        message=(
            "Optimistic scenario shows no net loss — excellent position (WARNING)"
            if not is_blocking
            else "Both optimistic and realistic scenarios are negative (BLOCKING)"
        ),
    )
```

### T2: Modificar `_check_scenario_order` en commercial_gate.py

**Archivo**: `modules/quality_gates/commercial_gate.py`

Cambiar el check de orden `optimistic >= realistic` para aceptar optimista < 0 como caso especial:

```python
# En _check_scenario_order (aprox L282-326):
# Aceptar que optimista < realista cuando optimista es negativo (sin pérdida neta)

# Antes (conceptual):
if optimistic_value < realistic_value:
    return GateResult(..., blocking=True, ...)

# Después:
if optimistic_value < realistic_value:
    # Si optimista < 0, es "break-even o mejor" — reinterpretar como éxito
    if optimistic_value < 0 and realistic_value > 0:
        return GateResult(
            gate_id="CG-SCENARIO-ORDER",
            passed=True,
            blocking=False,
            message="Optimistic scenario at break-even/better — ordering inverted due to net gain (WARNING)",
        )
    return GateResult(
        gate_id="CG-SCENARIO-ORDER",
        passed=False,
        blocking=True,
        message=f"Optimistic ({optimistic_value}) < Realistic ({realistic_value})",
    )
```

### T3: Test + verificación

1. Agregar test unitario en `tests/quality_gates/test_commercial_gate.py`:
   - Test: optimista negativo + realista positivo → WARNING, no BLOCKING
   - Test: ambos negativos → BLOCKING (no debe relajar este caso)
   - Test: optimista > realista (caso normal) → PASS

2. Ejecutar tests:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_commercial_gate.py -v
```

3. Verificar no regresión:
```bash
./venv/Scripts/python.exe -m pytest -q
```

---

## Criterios de Completitud

- [ ] `_check_scenario_negative`: optimista < 0 + realista > 0 → WARNING, no BLOCKING
- [ ] `_check_scenario_order`: optimista < 0 < realista → PASS (caso break-even)
- [ ] Ambos negativos → BLOCKING (sin cambio en este caso)
- [ ] Tests nuevos: 2-3 test cases cubriendo los escenarios
- [ ] 100 tests existentes siguen PASS
- [ ] git commit con mensaje descriptivo

---

## delegate_task Prompt (para subagente)

```
Implement FASE-1 of DT-4 plan for iah-cli project at /mnt/c/Users/Jhond/Github/iah-cli.

GOAL: Fix BUG-8 in commercial_gate.py — reinterpret optimistic scenario when it becomes negative.

CONTEXT:
The optimistic scenario calculation is mathematically CORRECT: monthly_loss = OTA_loss - savings - IA_revenue. When savings + IA_revenue exceed OTA_loss, the result is negative (no net loss = best possible outcome). But two gate checks treat this as BLOCKING:
1. _check_scenario_negative: optimistic < 0 → BLOCKING
2. _check_scenario_order: optimistic < realistic → BLOCKING

FIX (Opción B — reinterpretación comercial, NO modificar fórmula):
1. In _check_scenario_negative: when optimistic < 0 AND realistic > 0, emit WARNING instead of BLOCKING
2. In _check_scenario_order: when optimistic < 0 < realistic, pass (break-even case)

TASKS:
1. Read modules/quality_gates/commercial_gate.py — find _check_scenario_negative and _check_scenario_order
2. Modify _check_scenario_negative: optimistic < 0 + realistic > 0 → WARNING (not BLOCKING)
3. Modify _check_scenario_order: optimistic < 0 < realistic → PASS (not BLOCKING)
4. Add tests in tests/quality_gates/test_commercial_gate.py (create if not exists)
5. Run: ./venv/Scripts/python.exe -m pytest tests/quality_gates/test_commercial_gate.py -v
6. Run full suite: ./venv/Scripts/python.exe -m pytest -q
7. git add + commit with message: "fix(BUG-8): reinterpret optimistic scenario negative as WARNING not BLOCKING"

RESTRICTIONS:
- Do NOT modify modules/financial_engine/scenario_calculator.py
- Preserve blocking behavior when BOTH optimistic AND realistic are negative
- Keep existing test suite passing
```

---

## Post-Ejecución (OBLIGATORIO)

```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe scripts/log_phase_completion.py --fase FASE-1 --desc "BUG-8_optimista_negativo_WARNING_no_BLOCKING" --check-manual-docs
```

---

## Siguiente Sesión

**FASE-2** — BUG-7: Persistir commercial gates + expandir BLOCKED_BY_GATES.md
