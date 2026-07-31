# FASE-1: Reparar el bypass de seguridad — delivery_quality_report + GATE_BLOCKING_ENABLED

**ID**: ASSET-ALIGNMENT-FASE-1
**Objetivo**: Reparar las 2 capas críticas de bypass que permiten entregar el ZIP a pesar de que Gate 9 (proposal_asset_alignment) marca BLOCKED.
**Dependencias**: Ninguna (primera fase del plan)
**Duración estimada**: 1-2 horas
**Skill**: `iah-cli-phased-execution` + `iah-cli-execution-conventions`
**delegate_task**: ✅ SUBAGENTE — spec completa del contexto (§9.1, §9.2), 2 archivos, cambios localizados.

---

## Contexto

La auditoría contra código vivo (sección 9 del contexto) reveló que el sistema tiene 3 capas de control que DEBERÍAN bloquear la entrega cuando un servicio prometido no tiene asset, pero las 3 están bypassed:

1. **CAPA A** (publication_gates.py): Gate 9 detecta BLOCKED correctamente → PERO `GATE_BLOCKING_ENABLED=False` por default en main.py:2814, así que no bloquea.
2. **CAPA B** (delivery_quality_report.py): Hardcodea `proposal_asset_gate.passed=True` en L238 porque busca la key `"proposal_asset"` (que no existe) en vez de `"proposal_asset_alignment"`.
3. **CAPA C** (delivery_packager.py): Solo bloquea el ZIP si `delivery_quality_report.status == "FAIL"`, pero como el quality report siempre dice PASS, nunca bloquea.

Esta fase repara las CAPAS A y B. La CAPA C no requiere cambios — una vez que el quality report consuma el resultado real del Gate 9, el packager bloqueará correctamente.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| (sin fases previas — primera fase del plan) | — |

### Base Técnica Disponible

- Archivos a modificar:
  - `modules/quality_gates/delivery_quality_report.py` (L238)
  - `main.py` (L2814)
- Tests base: `tests/quality_gates/test_delivery_quality_report.py` (27 tests pasan)
- Tests base: `tests/quality_gates/test_publication_gates.py` (85 passed, 1 FAILED pre-existente)

---

## Tareas

### Tarea 1: Fix delivery_quality_report.py — consumir resultado real de Gate 9

**Objetivo**: Hacer que delivery_quality_report lea el resultado real de `proposal_asset_alignment` desde gate_results, en vez de hardcodear `passed=True`.

**Archivos afectados**:
- `modules/quality_gates/delivery_quality_report.py`

**Diagnóstico del bug (del contexto §9.1)**:

Línea 238 actual:
```python
proposal_asset_gate=gate_results.get("proposal_asset", {"passed": True, "gate": "G9"}),
```

El código busca la key `"proposal_asset"` que NUNCA se inserta en `gate_results`. El gate real se llama `"proposal_asset_alignment"`. Al no encontrarlo, usa el default `{"passed": True, ...}`.

**Fix requerido**:
```python
proposal_asset_gate=gate_results.get("proposal_asset_alignment", {"passed": True, "gate": "G9"}),
```

**Además**: Verificar que `proposal_asset_alignment` esté en la lista de blocking_gates del quality report. Según §9.1, los únicos gates considerados blocking son `coherence`, `coverage`, `evidence` — `proposal_asset_alignment` NUNCA bloquea. Añadirlo a la lista de blocking_gates.

**Criterios de aceptación**:
- [ ] La key buscada es `"proposal_asset_alignment"` (no `"proposal_asset"`)
- [ ] `proposal_asset_alignment` está en la lista de blocking_gates del quality report
- [ ] Cuando Gate 9 falla, `delivery_quality_report.status` puede ser "FAIL"
- [ ] Tests existentes (27) siguen pasando
- [ ] Nuevo test: cuando gate_results tiene `proposal_asset_alignment.passed=False`, el quality report propaga el fallo

### Tarea 2: Fix main.py — GATE_BLOCKING_ENABLED=True por default

**Objetivo**: Cambiar el default de `GATE_BLOCKING_ENABLED` de `False` a `True` para que los gates bloqueen la generación de documentos por defecto.

**Archivos afectados**:
- `main.py`

**Diagnóstico del bug (del contexto §9.2)**:

Línea 2814 actual:
```python
_gate_blocking_enabled = os.getenv("GATE_BLOCKING_ENABLED", "").lower() in ("1", "true", "yes")
```

Default = `""` → `.lower()` → `""` → not in `("1", "true", "yes")` → `False`.

**Fix requerido**:
```python
_gate_blocking_enabled = os.getenv("GATE_BLOCKING_ENABLED", "true").lower() in ("1", "true", "yes")
```

Cambiar el default de `""` a `"true"`. Esto hace que el blocking esté activado por defecto, pero permite desactivarlo con `GATE_BLOCKING_ENABLED=0` o `GATE_BLOCKING_ENABLED=false` para debugging.

**Criterios de aceptación**:
- [ ] El default de `GATE_BLOCKING_ENABLED` es `True` (env var default = "true")
- [ ] Se puede desactivar con `GATE_BLOCKING_ENABLED=false`
- [ ] Tests existentes siguen pasando (verificar si algún test depende del default False)
- [ ] Si algún test rompe por este cambio, ajustarlo con `os.environ["GATE_BLOCKING_ENABLED"] = "false"` en el setup del test

---

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| `test_delivery_quality_report.py` | `tests/quality_gates/test_delivery_quality_report.py` | 27/27 existentes + N nuevos pasan |
| `test_publication_gates.py` | `tests/quality_gates/test_publication_gates.py` | 85/86 (1 pre-existente) no regresa |
| `test_proposal_asset_alignment.py` | `tests/quality_gates/test_proposal_asset_alignment.py` | 24/24 pasan |

**Comando de validación**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
./venv/Scripts/python.exe -m pytest tests/quality_gates/test_delivery_quality_report.py tests/quality_gates/test_proposal_asset_alignment.py -v
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`**: Marcar FASE-1 como ✅ Completada con fecha.
2. **`README.md` del plan**: Actualizar tabla de progreso, marcar FASE-1 como completada.
3. **`09-documentacion-post-proyecto.md`**:
   - **Sección B**: Agregar funcionalidad nueva (Gate 9 bypass fix, GATE_BLOCKING_ENABLED default)
   - **Sección D**: Métricas (tests count, files modified)
   - **Sección E**: Archivos afiliados actualizados (delivery_quality_report.py, main.py)
4. **`evidence/fase-1/`**: Guardar diffs de los cambios.
5. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-1-ASSET-ALIGNMENT \
       --desc "Fix bypass de seguridad: delivery_quality_report consume Gate 9 real + GATE_BLOCKING_ENABLED default True" \
       --archivos-mod "modules/quality_gates/delivery_quality_report.py,main.py" \
       --tests "2" \
       --check-manual-docs
   ```
6. **CHANGELOG.md y GUIA_TECNICA.md**: Editar con cambios de esta fase.

**NO esperar a la siguiente sesión para documentar.**

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] delivery_quality_report.py L238 busca `"proposal_asset_alignment"` (no `"proposal_asset"`)
- [ ] `proposal_asset_alignment` en lista de blocking_gates del quality report
- [ ] main.py L2814 default = "true" (GATE_BLOCKING_ENABLED=True por default)
- [ ] Tests nuevos pasan (gate fail propagation + default True)
- [ ] Tests existentes (27+24+85) sin regresión
- [ ] `run_all_validations.py --quick` pasa
- [ ] `dependencias-fases.md` actualizado
- [ ] `09-documentacion-post-proyecto.md` actualizado
- [ ] `log_phase_completion.py` ejecutado
- [ ] CHANGELOG.md + GUIA_TECNICA.md editados
- [ ] `evidence/fase-1/` con diffs

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **Máximo 60 iteraciones del agente por fase** (R2 del phased_project_executor)
- **No modificar** `publication_gates.py` (Gate 9 funciona correctamente, el problema está en el consumidor)
- **No modificar** `delivery_packager.py` (funciona correctamente una vez que el quality report es honesto)
- **No ejecutar v4complete** (reservado para FASE-5)
- **No modificar ROADMAP.md**
- Si un test existente depende de `GATE_BLOCKING_ENABLED=False`, ajustarlo con env var override, no revertir el fix

---

## Prompt de Ejecución (delegate_task subagente)

```
Actúa como especialista en Python con conocimiento del proyecto iah-cli.

OBJETIVO: Reparar el bypass de seguridad en delivery_quality_report.py + main.py para que Gate 9 (proposal_asset_alignment) bloquee correctamente la entrega cuando falla.

CONTEXTO:
- Proyecto: /mnt/c/Users/Jhond/Github/iah-cli
- Python: ./venv/Scripts/python.exe (Windows venv accedido desde WSL)
- Versión actual: 4.62.0
- Bug 1 (delivery_quality_report.py:238): Busca key "proposal_asset" que no existe; la key real es "proposal_asset_alignment". Default fallback hardcodea passed=True.
- Bug 2 (main.py:2814): GATE_BLOCKING_ENABLED default es "" (falsy). Debe ser "true".
- Además: proposal_asset_alignment no está en la lista de blocking_gates del quality report (solo coherence, coverage, evidence lo están).

TAREAS:
1. En delivery_quality_report.py L238: cambiar "proposal_asset" → "proposal_asset_alignment"
2. En delivery_quality_report.py: añadir "proposal_asset_alignment" a la lista de blocking_gates
3. En main.py L2814: cambiar default de os.getenv("GATE_BLOCKING_ENABLED", "") a os.getenv("GATE_BLOCKING_ENABLED", "true")
4. Escribir 2 tests nuevos:
   - test: cuando gate_results tiene proposal_asset_alignment.passed=False, el quality report propaga el fallo (status puede ser FAIL)
   - test: GATE_BLOCKING_ENABLED default es True cuando no se setea la env var
5. Ejecutar tests: ./venv/Scripts/python.exe -m pytest tests/quality_gates/test_delivery_quality_report.py tests/quality_gates/test_proposal_asset_alignment.py -v
6. Ejecutar: ./venv/Scripts/python.exe scripts/run_all_validations.py --quick

CRITERIOS:
- delivery_quality_report.py busca "proposal_asset_alignment" en gate_results
- proposal_asset_alignment está en blocking_gates
- GATE_BLOCKING_ENABLED default = True
- 27+24 tests existentes pasan, 2 nuevos pasan
- run_all_validations.py --quick pasa 4/4 (o 5/5)

VALIDACIONES:
- grep "proposal_asset_alignment" modules/quality_gates/delivery_quality_report.py (debe mostrar la key corregida)
- grep "GATE_BLOCKING_ENABLED.*true" main.py (debe mostrar el nuevo default)
- pytest tests/quality_gates/ -v sin regresiones
```
