# FASE-1-COH: Unificar CoherenceValidator ↔ CoherenceGate

**ID**: FASE-1-COH
**Objetivo**: Eliminar el facade H10 FIX e integrar realmente CoherenceValidator en CoherenceGate para producir un único coherence_score trazable.
**Dependencias**: Ninguna (primera fase del proyecto)
**Duración estimada**: 2-3 horas
**Skill**: `phased-workflow-self-improvement` (reglas de ejecución directa)
**Modo de ejecución**: DIRECTO — código puro, sin comandos externos ni subagentes.

---

## Contexto

El pipeline v4complete produce **5 valores distintos de coherence_score** para el mismo delivery porque `CoherenceGate._validator` está instanciado (L158) pero **jamás llamado** en `execute()` (L160-203). El gate recibe un `coherence_score` float externo y solo compara contra umbral, ignorando por completo los errores detallados del validator.

**Causa raíz**: R1 — `CoherenceGate.execute()` ignora `_validator`. Validator corre 2× (pre/post). `v4_complete_report` introduce 2 scores adicionales.

**Archivos clave** (verificados en contexto AUDITORIA_COHERENCIA_HOTELCASTILLAREAL_20260511):
- `modules/quality_gates/coherence_gate.py` — L158 instancia `_validator`, L160-203 `execute()` nunca lo llama
- `main.py` — L2228 validator pre-gen, L2414 orchestrator pre-gen, L2653 gate assessment, L2955-2960 v4_complete_report

---

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| — | — |

---

## Base Técnica Disponible

- `modules/quality_gates/coherence_gate.py` — CoherenceGate con H10 FIX facade
- `modules/quality_gates/coherence_validator.py` — CoherenceValidator con validate()
- `main.py` — pipeline v4complete, L2225-2250, L2653, L2955-2960
- Tests existentes en `tests/quality_gates/`

---

## Tareas

### T1: Investigar flujo actual de coherence_score en main.py
**Objetivo**: Trazar el flujo completo de coherence_score desde el validator hasta el gate y v4_complete_report.

**Pasos**:
1. Leer `main.py` alrededor de L2225-2250 (pre_coherence_score), L2414 (orchestrator coherence_report), L2653 (assessment coherence_score), L2955-2960 (v4_complete_report).
2. Confirmar que `pre_coherence_score` (~0.8053) se asigna en L2236 y nunca se reasigna hasta L2955.
3. Documentar en notas internas: ¿por qué v4_complete_report muestra 0.8467 si pre_coherence_score es 0.8053?

**Criterios de aceptación**:
- [ ] Trazado completo documentado con números de línea
- [ ] Anomalía 0.8467 explicada o marcada para investigación

### T2: Refactor coherence_gate.py para integrar validator
**Objetivo**: Eliminar facade H10 FIX. Hacer que `execute()` use `_validator.validate()` como fuente única de verdad.

**Cambios requeridos**:
1. Modificar `coherence_gate.py`: en `execute()`, llamar `self._validator.validate(diagnostic, proposal, assets, validation_summary, generated_assets=generated_assets)` en vez de comparar solo `coherence_score >= threshold`.
2. O bien crear `execute_from_validator()` si modificar `execute()` rompe la firma pública. Evaluar backwards compatibility.
3. Asegurar que el resultado del gate incluya: `coherence_score=report.overall_score`, `passed=report.is_coherent`, `errors=report.errors`, `checks=report.checks`.

**Criterios de aceptación**:
- [ ] `CoherenceGate.execute()` invoca `self._validator.validate()` al menos 1 vez
- [ ] Gate ya no depende de `coherence_score` float externo — consume el reporte completo del validator
- [ ] Backwards compatibility: si alguien llama `execute(score)` con firma antigua, manejar graceful

### T3: Refactor main.py para unificar fuente de coherence_score
**Objetivo**: Que el diagnóstico YAML, gate_report y v4_complete_report lean del mismo source: el CoherenceValidator.

**Cambios requeridos**:
1. Modificar `main.py` L2653: pasar datos completos al gate (diagnostic, proposal, assets, validation_summary, generated_assets) en vez de solo `coherence_score` float.
2. Modificar `main.py` L2955-2960: `v4_complete_report` debe usar un único score del validator, no `pre_coherence_score` + `post_coherence_score` duplicados.
3. Eliminar `asset_result.coherence_report.overall_score` como fuente del gate — usar solo el validator.

**Criterios de aceptación**:
- [ ] Diagnostic YAML coherence_score == gate_report coherence.value
- [ ] v4_complete_report tiene exactamente 1 campo coherence_score (trazable al validator)
- [ ] No hay scores "fantasma" (0.8467 no trazable)

### T4: Tests de integración gate ↔ validator
**Objetivo**: Verificar que gate y validator producen el mismo score cuando se conectan.

**Tests**:
1. `test_gate_uses_validator`: mock de validator.validate() retorna score=0.81, is_coherent=false; gate.execute() debe retornar passed=false, score=0.81.
2. `test_gate_no_longer_uses_external_score`: gate.execute() ignorará parámetro `coherence_score` externo si se le pasa el reporte del validator.
3. `test_main_passes_validator_data_to_gate`: verificar que main.py construye los argumentos correctos para el gate.
4. `test_v4_complete_report_single_score`: verificar que report JSON solo tiene 1 campo coherence_score.

**Criterios de aceptación**:
- [ ] 4+ tests nuevos pasan
- [ ] 0 regresiones en tests existentes de quality_gates/
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesión):

1. **`dependencias-fases.md`** — Marcar FASE-1-COH como ✅ Completada con fecha y notas.
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-1-COH como ✅.
3. **`09-documentacion-post-proyecto.md`** — Sección E: agregar archivos modificados (`coherence_gate.py`, `main.py`). Sección D: actualizar métrica "Tests nuevos".
4. **Evidencia**: si hay outputs de tests o logs relevantes, copiar a `evidence/FASE-1-COH/`.
5. **`log_phase_completion.py`**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-1-COH \
    --desc "Unificar CoherenceValidator en CoherenceGate: eliminar facade H10 FIX, integrar validate() en execute(), unificar fuente de coherence_score en main.py" \
    --archivos-mod "modules/quality_gates/coherence_gate.py,main.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [x] **T1 completo**: Trazado documentado con líneas exactas
- [x] **T2 completo**: `execute()` llama a `_validator.validate()` ≥ 1 vez
- [x] **T3 completo**: main.py pasa datos completos al gate, v4_complete_report tiene 1 solo score
- [x] **T4 completo**: ≥ 4 tests nuevos pasan, 0 regresiones
- [x] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 5/5
- [x] **`dependencias-fases.md` actualizado**: Estado de FASE-1-COH marcado ✅
- [x] **Documentación afiliada**: `09-documentacion-post-proyecto.md` actualizado
- [x] **log_phase_completion.py ejecutado**: REGISTRY.md tiene entrada FASE-1-COH

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO ejecutar v4complete** en esta fase. Es implementación pura.
- **NO modificar ROADMAP.md** — solo en FASE-RELEASE.
- **Máximo 60 iteraciones** — si se alcanza el límite, marcar como ⏳ INCOMPLETA con checkpoint.
- **Presupuesto estimado**: ~30-40 iteraciones trabajo + ~20 docs/verificación.
- Si `asset_confidence` gate vive en `coherence_gate.py` (mismo archivo), reportar inmediatamente para evaluar fusión con FASE-4-GATE.
