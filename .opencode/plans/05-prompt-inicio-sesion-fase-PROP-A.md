# FASE-PROP-A: Unificacion de Coherence Score

**Plan:** PROPOSAL-COMERCIAL-FIX v1.0.0
**Workflow:** `.agents/workflows/phased_project_executor.md` v2.10.0
**Presupuesto:** 60 iteraciones max | **Estimado esta fase:** ~50 iteraciones
**Dependencias:** Ninguna
**Fase siguiente:** FASE-PROP-B

## Contexto

El pipeline v4complete tiene **3 fuentes de verdad** para `coherence_score`:

1. **Fallback del diagnostico** (`v4_diagnostic_generator.py:1178-1204` `_calculate_coherence_score()`): VERIFIED→100, ESTIMATED→70, CONFLICT→30 → promedio. Produce 0.74 para Hotelcastillareal.
2. **CoherenceValidator** (`coherence_validator.py` → `coherence_validation.json`): lógica propia (problems_have_solutions, assets_are_justified, etc.). Produce 0.72.
3. **Asset coherence report** (`main.py:2637` `asset_result.coherence_report.overall_score`): leído DESPUÉS de que el diagnóstico ya fue escrito. El gate lo usa en L2679.

**Problema**: el diagnóstico se genera PRIMERO con su propio fallback (0.74). La propuesta lee ese 0.74 × 100 = "74%". El gate lee el valor del asset (0.72) y compara contra 0.80 → FAILED. Ninguno se comunica con los otros.

**Causa raíz**: orden del pipeline en `main.py` (L2615-2722) es: diagnóstico → propuesta → assets → gates. Los gates corren al final y su resultado no retroalimenta nada.

**Objetivo**: UN solo cómputo de coherence_score (el CoherenceValidator), usado por diagnóstico, propuesta y gates.

## Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| Ninguna | — |

## Base Técnica Disponible

- `main.py` (L2615-2722): pipeline v4complete — assessment + gates
- `modules/commercial_documents/v4_diagnostic_generator.py` (L428, L1178-1204): `_calculate_coherence_score()` fallback
- `modules/quality_gates/coherence_gate.py` (377 líneas): CoherenceValidator
- `modules/commercial_documents/templates/diagnostico_v6_template.md`: template V6
- `coherence_validation.json` en `output/v4_complete/hotelcastillareal/v4_audit/`: overall_score=0.72

## Tareas Específicas

### Tarea 1: Investigar pipeline timing en main.py
**Objetivo**: Entender el orden exacto de ejecución y dónde se puede insertar CoherenceValidator.

**Archivos afectados**:
- `main.py` (L2615-2722)

**Criterios de aceptación**:
- [ ] Identificar la función/linea donde se invoca `diagnostic_gen.generate()`
- [ ] Identificar la función/linea donde se invoca `CoherenceValidator`
- [ ] Confirmar que `coherence_validation.json` ya existe (output de ejecución anterior) o entender cómo se genera en runtime
- [ ] Documentar el flujo de datos actual en comentarios

### Tarea 2: Mover CoherenceValidator antes del diagnóstico
**Objetivo**: Ejecutar CoherenceValidator (o leer su resultado) ANTES de `diagnostic_gen.generate()`.

**Archivos afectados**:
- `main.py`

**Criterios de aceptación**:
- [ ] CoherenceValidator corre (o su resultado se lee) antes de la llamada a `diagnostic_gen.generate()`
- [ ] El `coherence_score` obtenido se guarda en una variable local accesible
- [ ] No se rompe el orden de los demás pasos (propuesta, assets, gates)

### Tarea 3: Pasar coherence_score al diagnostic generator
**Objetivo**: El diagnóstico use el valor del CoherenceValidator en lugar del fallback.

**Archivos afectados**:
- `main.py` (pasar parámetro)
- `modules/commercial_documents/v4_diagnostic_generator.py` (L428: `coherence_score: Optional[float] = None`)

**Criterios de aceptación**:
- [ ] `diagnostic_gen.generate(coherence_score=coherence_validator_score)` se invoca con el valor real
- [ ] Si `coherence_score` se recibe y es > 0, se usa directamente (no se llama a `_calculate_coherence_score()`)
- [ ] Si `coherence_score` es None/0, mostrar "PENDIENTE" en el YAML header en lugar de un número inventado

### Tarea 4: Agregar gate_status al template de diagnóstico
**Objetivo**: El diagnóstico muestre si el coherence gate PASSED o FAILED.

**Archivos afectados**:
- `modules/commercial_documents/templates/diagnostico_v6_template.md`
- `modules/commercial_documents/v4_diagnostic_generator.py` (pasar `gate_status` al template data)

**Criterios de aceptación**:
- [ ] Variable `${gate_status}` disponible en el template
- [ ] Renderiza "Coherence Gate: PASSED" o "Coherence Gate: FAILED" según umbral 0.80
- [ ] Si no hay gate aún (porque los gates corren después), mostrar "Coherence Gate: PENDIENTE"

### Tarea 5: Eliminar o degradar fallback `_calculate_coherence_score()`
**Objetivo**: El fallback ya no debe producir valores ficticios.

**Archivos afectados**:
- `modules/commercial_documents/v4_diagnostic_generator.py` (L1178-1204)

**Criterios de aceptación**:
- [ ] El método `_calculate_coherence_score()` queda como "legacy fallback" con docstring DEPRECADO, o se elimina completamente
- [ ] Si se mantiene, NUNCA se invoca automáticamente — solo si se llama explícitamente
- [ ] El YAML header del diagnóstico NO muestra un número inventado cuando no hay coherence_score real

## Tests Obligatorios

| Test | Archivo | Criterio de Éxito |
|------|---------|-------------------|
| Test de pipeline timing | (nuevo o existente) | `main.py` ejecuta CoherenceValidator antes de diagnostic_gen sin errores |
| Test de fallback eliminado | `tests/commercial_documents/test_diagnostic_generator.py` | Cuando coherence_score=0.72 se pasa, el YAML header muestra 72% (no 74%) |
| Test de gate_status | `tests/commercial_documents/test_diagnostic_generator.py` | Template data incluye gate_status con valor esperado |

**Comando de validación**:
```bash
venv/Scripts/python.exe -m pytest tests/commercial_documents/test_diagnostic_generator.py -v -k coherence
venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

## Archivos Involucrados

| Archivo | Tipo de Cambio | Líneas Aprox. |
|---------|---------------|--------------|
| `main.py` | Modificación | L2615-2722 (pipeline timing) |
| `modules/commercial_documents/v4_diagnostic_generator.py` | Modificación | L428 (signature), L1178-1204 (fallback) |
| `modules/commercial_documents/templates/diagnostico_v6_template.md` | Modificación | Agregar bloque gate_status |
| `modules/quality_gates/coherence_gate.py` | Referencia (lectura) | Confirmar API del validator |

## Criterios de Completitud (CHECKLIST)

- [x] **Pipeline reordenado**: CoherenceValidator/resultado disponible antes del diagnóstico
- [x] **Diagnóstico usa valor real**: no inventa coherence_score
- [x] **Template muestra gate_status**: PASSED/FAILED/PENDIENTE visible
- [x] **Fallback degradado**: `_calculate_coherence_score()` no produce valores ficticios automáticamente
- [x] **Tests pasan**: 7 tests nuevos pasan
- [x] **Validaciones del proyecto**: `run_all_validations.py --quick` pasa 4/4
- [x] **Documentación afiliada**: cambios reflejados en notas de fase
- [x] **Evidencia preservada**: Documentación creada en `dependencias-fases.md`, `06-checklist-implementacion.md`, `09-documentacion-post-proyecto.md`

## Restricciones

- **NO modificar** la lógica interna de `CoherenceValidator` — solo su momento de ejecución
- **NO eliminar** los gates del final del pipeline — solo cambiar el flujo de datos
- **Máximo 60 iteraciones** (R2). Si se agota en iteración >50, marcar como ⏳ INCOMPLETA y documentar checkpoint

## Post-Ejecución (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

1. **`dependencias-fases.md`**
   - Marcar FASE-PROP-A como ✅ Completada
   - Agregar notas de ejecución (si hubo split, documentar)

2. **`06-checklist-implementacion.md`**
   - Marcar todas las tareas de FASE-PROP-A como completadas
   - Actualizar estado general

3. **`09-documentacion-post-proyecto.md`**
   - Sección B: agregar cambios en main.py y v4_diagnostic_generator.py
   - Sección C: documentar cambio arquitectónico (pipeline timing)

4. **Evidencia** (si se ejecutó v4complete):
   ```bash
   mkdir -p evidence/FASE-PROP-A
   cp output/v4_complete/01_DIAGNOSTICO_*.md evidence/FASE-PROP-A/ 2>/dev/null || true
   cp output/v4_complete/02_PROPUESTA_*.md evidence/FASE-PROP-A/ 2>/dev/null || true
   ```

5. **log_phase_completion.py**:
   ```bash
   cd /mnt/c/Users/Jhond/Github/iah-cli
   venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase FASE-PROP-A \
       --desc "Unificacion de Coherence Score: pipeline timing + fallback eliminado" \
       --archivos-mod "main.py,modules/commercial_documents/v4_diagnostic_generator.py,modules/commercial_documents/templates/diagnostico_v6_template.md" \
       --tests "3" \
       --check-manual-docs
   ```

**Siguiente fase:**
```
Carga y ejecuta .opencode/plans/05-prompt-inicio-sesion-fase-PROP-B.md siguiendo .agents/workflows/phased_project_executor.md
```
