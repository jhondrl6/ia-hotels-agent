# FASE-4-GATE: Gate asset_confidence hardening

**ID**: FASE-4-GATE
**Objetivo**: Modificar el gate `asset_confidence` para emitir BLOCKED (no WARNING) cuando 100% de los assets generados tienen confidence < 0.7 (ESTIMATED).
**Dependencias**: FASE-3-CONTENT (✅)
**Duración estimada**: 1.5-2 horas
**Skill**: `phased-workflow-self-improvement` (reglas de ejecución directa)
**Modo de ejecución**: DIRECTO — código puro, sin comandos externos ni subagentes.

---

## Contexto

En el delivery de Hotel Castilla Real, los 7 assets del `PROPOSAL_SERVICE_TO_ASSET` tienen confidence=0.5 (100% ESTIMATED). El gate `asset_confidence` emite **WARNING** pero no bloquea. El único bloqueo es `tier_c_onboarding_required`, que es fácil de bypass.

Esto significa que un delivery 100% placeholder (todos los assets son estimados) pasa como "con warnings" en vez de "bloqueado". La semántica del gate debe ser más estricta.

**Causa raíz**: R6 — Gate asset_confidence muy permisivo.

**Nota de conflicto**: Si `asset_confidence` vive en `coherence_gate.py` (mismo archivo que FASE-1-COH), el agente debe confirmar la ubicación real. Si está en `publication_gates.py` u otro archivo, proceder normalmente.

---

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| FASE-1-COH | ✅ Completada |
| FASE-2-DEFAULT | ✅ Completada |
| FASE-3-CONTENT | ✅ Completada |

---

## Base Técnica Disponible

- `modules/quality_gates/publication_gates.py` (o equivalente) — donde vive `asset_confidence`
- `modules/quality_gates/coherence_gate.py` — verificar si `asset_confidence` está aquí por conflicto
- `modules/asset_generation/` — cómo se calcula `confidence` en cada asset
- Tests existentes en `tests/quality_gates/`

---

## Tareas

### T1: Modificar asset_confidence gate para BLOCKED en 100% ESTIMATED
**Objetivo**: Hacer que el gate sea más estricto cuando todos los assets son de baja confianza.

**Cambios**:
1. Localizar el gate `asset_confidence` (buscar en `modules/quality_gates/`).
2. Modificar la lógica:
   - Si `all(asset.confidence < 0.7 for asset in generated_assets)` → estado BLOCKED (no WARNING).
   - Si `any(asset.confidence < 0.7)` pero no todos → estado WARNING (comportamiento actual).
   - Si todos >= 0.7 → PASSED.
3. Actualizar el mensaje del gate para que sea claro: "100% de assets son ESTIMATED (confidence < 0.7). Delivery bloqueado hasta onboarding o datos reales."

**Criterios de aceptación**:
- [ ] Gate emite BLOCKED cuando 100% assets tienen confidence < 0.7
- [ ] Gate mantiene WARNING cuando hay mix ESTIMATED/VERIFIED
- [ ] Gate emite PASSED cuando todos >= 0.7

### T2: Tests para nuevo comportamiento
**Objetivo**: Cubrir los 3 casos del gate.

**Tests**:
1. `test_all_estimated_blocked`: 3 assets con confidence 0.5 → BLOCKED
2. `test_mixed_estimated_warning`: 2 assets 0.5 + 1 asset 0.8 → WARNING
3. `test_all_verified_passed`: 3 assets con confidence 0.8 → PASSED
4. `test_empty_assets_neutral`: 0 assets → PASSED o WARNING según decisión de diseño (documentar)

**Criterios de aceptación**:
- [ ] 4 tests nuevos pasan
- [ ] 0 regresiones en tests existentes de quality_gates/

### T3: Verificar backwards compatibility
**Objetivo**: Asegurar que deliveries existentes con confianza mixta no se rompen.

**Pasos**:
1. Revisar tests existentes que usen `asset_confidence`. Si alguno asumía WARNING para 100% ESTIMATED, actualizarlo a BLOCKED.
2. Si hay fixtures de datos reales de hoteles anteriores, confirmar que no cambian de PASSED a BLOCKED inesperadamente.
3. Documentar en notas de la fase: ¿cuáles hoteles/deliveries se verificaron?

**Criterios de aceptación**:
- [ ] Tests existentes actualizados si esperaban WARNING para 100% ESTIMATED
- [ ] No hay regresiones en deliveries con assets VERIFIED
- [ ] `run_all_validations.py --quick` pasa 4/4

---

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`** — Marcar FASE-4-GATE como ✅ Completada.
2. **`06-checklist-implementacion.md`** — Marcar todos los items de FASE-4-GATE como ✅.
3. **`09-documentacion-post-proyecto.md`** — Sección E: agregar archivos modificados. Sección D: actualizar métricas.
4. **`log_phase_completion.py`**:

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-4-GATE \
    --desc "Hardening de gate asset_confidence: BLOCKED cuando 100% assets son ESTIMATED (confidence < 0.7)" \
    --archivos-mod "modules/quality_gates/publication_gates.py" \
    --tests "4" \
    --check-manual-docs
```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **T1 completo**: asset_confidence emite BLOCKED para 100% ESTIMATED
- [ ] **T2 completo**: 4 tests nuevos pasan, 0 regresiones
- [ ] **T3 completo**: Backwards compatibility verificada, tests existentes sanos
- [ ] **Validaciones del proyecto**: `python scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado de FASE-4-GATE marcado ✅
- [ ] **Documentación afiliada**: `09-documentacion-post-proyecto.md` actualizado
- [ ] **log_phase_completion.py ejecutado**: REGISTRY.md tiene entrada FASE-4-GATE

**NO marcar la fase como completada si algún criterio falla.**

---

## Restricciones

- **NO ejecutar v4complete** en esta fase.
- **NO modificar ROADMAP.md** — solo en FASE-RELEASE.
- **Máximo 60 iteraciones**.
- **Presupuesto estimado**: ~25-35 iteraciones trabajo + ~15 docs/verificación.
