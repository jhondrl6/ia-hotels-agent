# FASE-5: DT4-N3-GATE-IDEMPOTENCY — Single Execution, No Mutations

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA
> **Iteraciones máx**: 60
> **Depende de**: —
> **Bloquea a**: FASE-6 (E2E)

## ⚠️ Hechos Confirmados

- `main.py:2775-2776` ejecuta `run_publication_gates(assessment, gate_config)` + `check_publication_readiness(assessment)`
- `check_publication_readiness()` llama internamente a `run_publication_gates()` → doble ejecución
- `publication_gates.py:861-890` puede mutar `assessment["site_presence_report"] = SimpleNamespace(...)`
- Consecuencias: resultado depende del orden de `self.gates`, segunda ejecución ve assessment mutado, reportes pueden variar sin cambio de input

## Objetivo

1. Construir el assessment completo antes de ejecutar gates
2. Ejecutar gates UNA sola vez
3. Derivar readiness desde los resultados ya calculados (sin re-ejecutar)
4. Eliminar todas las mutaciones de `assessment` dentro de gates

## Tareas

### T1: Investigar el double-execution path

- **Archivo**: `main.py`
  - Leer `check_publication_readiness()` (buscar definición)
  - Trazar qué hace internamente — ¿re-ejecuta `run_publication_gates()`?
  ```bash
  grep -n "def check_publication_readiness" main.py modules/
  grep -n "run_publication_gates" main.py modules/
  ```
- Documentar el flujo actual: assessment → gates → readiness → gates otra vez

### T2: Refactorizar `check_publication_readiness()` para derivar de resultados existentes

- **Archivo**: `modules/quality_gates/publication_gates.py` (o donde esté definida)
  - Modificar para que acepte `gate_results` ya calculados como parámetro:
    ```python
    def check_publication_readiness(assessment, gate_results: List[GateResult]) -> ReadinessReport:
        # Derivar readiness de gate_results, NO re-ejecutar run_publication_gates()
    ```
  - Si `gate_results` no se provee, ejecutar `run_publication_gates()` una vez (backward compat para otros callers)

- **Archivo**: `main.py`
  - Cambiar L2775-2776:
    ```python
    gate_results = run_publication_gates(assessment, gate_config)
    readiness_report = check_publication_readiness(assessment, gate_results)
    ```

### T3: Eliminar mutaciones de `assessment` dentro de gates

- **Archivo**: `modules/quality_gates/publication_gates.py`
  - Identificar TODAS las mutaciones con:
    ```bash
    grep -n "assessment\[" modules/quality_gates/publication_gates.py
    ```
  - Para cada mutación (ej. L861-890 `assessment["site_presence_report"] = ...`):
    - Si es un cómputo que ya debe estar en el assessment → eliminar la asignación, usar lo que ya viene
    - Si es necesario para el gate → usar variable local, no mutar el dict de entrada
  - **NOTA**: FASE-2 ya eliminó las reconstrucciones fake de SitePresence. Si FASE-2 se ejecutó primero, estas líneas ya fueron removidas. Verificar.

### T4: Tests de idempotencia

- **Archivo**: `tests/quality_gates/test_coverage_gate.py` (extender)
  - Test: ejecutar gates 2 veces con el mismo assessment → mismos resultados
  - Test: verificar que el assessment no fue mutado después de ejecutar gates (`assessment == deepcopy(original)`)
  - Test: verificar que `check_publication_readiness(assessment, gate_results)` no re-ejecuta gates
- **Verificación**: `./venv/Scripts/python.exe -m pytest tests/quality_gates/ -q -k "idempot"

## Criterios de Completitud

- [ ] `check_publication_readiness()` acepta `gate_results` pre-calculados
- [ ] `main.py` ejecuta gates UNA sola vez
- [ ] Cero mutaciones de `assessment` dentro de `publication_gates.py`
- [ ] Tests de idempotencia PASS (mismos resultados en 2 ejecuciones, assessment no mutado)
- [ ] Tests existentes no rompen: `./venv/Scripts/python.exe -m pytest tests/quality_gates/ tests/test_publication_gates_presence.py -q`
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO cambiar la interfaz pública de `run_publication_gates()`**
- **NO eliminar `check_publication_readiness()`** — otros callers pueden depender de ella
- **NO ejecutar v4complete**
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-5 \
    --desc "DT4-N3-GATE-IDEMPOTENCY: single gate execution, readiness derived from results, zero assessment mutations" \
    --archivos-mod "modules/quality_gates/publication_gates.py,main.py" \
    --tests "3" \
    --check-manual-docs
```

## Próxima Sesión

FASE-6: E2E-ZIONE — v4complete Zi One Luxury + verificación de los 14 criterios de éxito + análisis post-implementación
