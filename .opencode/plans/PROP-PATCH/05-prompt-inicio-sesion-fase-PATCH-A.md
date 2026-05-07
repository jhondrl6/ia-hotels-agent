---
description: FASE-PATCH-A — Fixes de coherencia y precio (SOL-1 + SOL-4)
version: 1.0.0
plan: PROP-PATCH
---

# FASE-PATCH-A: Fixes de Coherencia y Precio

**ID**: PATCH-A  
**Objetivo**: Corregir divergencia del coherence score (SOL-1) y el calculo de price_matches_pain (SOL-4)  
**Dependencias**: Ninguna  
**Duracion estimada**: 1.5-2 horas  
**Skill**: phased_project_executor v2.10.0  
**Iteraciones max**: 60  

---

## Contexto

La validacion post-ejecucion de Termales (2026-05-06) detecto que el YAML header del diagnostico muestra un coherence_score PRE-assets (0.8067) mientras que los publication gates usan el score POST-assets (0.7844). Esto produce una contradiccion visible: YAML dice PASSED, gate dice FAILED.

Ademas, el check `price_matches_pain` tiene score 0.0 porque el precio propuesto es 32.1x mayor que el dolor financiero calculado para Tier C, siendo el principal contribuidor al fallo de coherencia.

### Estado de Fases Anteriores

| Fase | Estado |
|------|--------|
| PROP-A — G | ✅ Completadas (plan anterior) |
| PATCH-A | 🔵 En Progreso |
| PATCH-B | ⏳ Pendiente |
| PATCH-C | ⏳ Pendiente |
| PATCH-RELEASE | ⏳ Pendiente |

### Base Tecnica Disponible

- Archivos existentes: `main.py`, `modules/commercial_documents/coherence_validator.py`
- Tests base: 2491 funciones, 192 archivos
- Módulos disponibles: CoherenceValidator, diagnostic generator, quality gates

---

## Tareas

### T1: SOL-1 — Unificar coherence score en YAML header

> **Leccion de PROP-A**: No reordenar el pipeline. El problema no es el orden; es que el diagnostico usa el score PRE-assets (L2235) mientras los gates usan POST-assets (L2425). El fix es pasar el post-assets score al diagnostico, no mover el validator.

**Objetivo**: Hacer que el diagnostico YAML use el coherence score POST-assets en lugar del PRE-assets.

**Archivos afectados**:
- `main.py` (L2447 aprox)

**Pasos**:
1. Localizar en `main.py` la llamada a `diagnostic_gen.generate(...)` donde se pasa `coherence_score=pre_coherence_score`.
2. ANTES de modificar, verificar que `asset_result` esta definido y accesible en ese scope. Buscar donde se crea (L2380-2425 aprox).
3. Si `asset_result` esta disponible, reemplazar por:
   ```python
   coherence_score=(asset_result.coherence_report.overall_score
                    if asset_result and asset_result.coherence_report
                    else pre_coherence_score),
   ```
4. Si `asset_result` NO esta disponible en ese scope, buscar donde se evalua post-assets y pasar ese score a la funcion del diagnostico.

**Criterios de aceptacion**:
- [ ] `grep -n "coherence_score=" main.py` muestra la nueva logica
- [ ] No hay SyntaxError al importar main.py
- [ ] Fallback a `pre_coherence_score` preservado si `asset_result` es None
- [ ] **NO se modifica** `v4_diagnostic_generator.py` ni templates (leccion PROP-A: no tocar lo que no es necesario)

---

### T2: Verificacion SOL-1 — Sin regressions

**Objetivo**: Confirmar que el cambio no rompe flujos donde `asset_result` es None.

**Pasos**:
1. Buscar todos los usos de `pre_coherence_score` en `main.py` despues de L2447.
2. Confirmar que ninguno requiere cambio (el PRE-score sigue siendo valido para usos internos previos).
3. Ejecutar tests relacionados:
   ```bash
   ./venv/Scripts/python.exe -m pytest tests/ -k coherence -v --tb=short
   ```

**Criterios de aceptacion**:
- [ ] Tests de coherencia pasan
- [ ] `run_all_validations.py --quick` pasa 4/4

---

### T3: SOL-4 — Investigar calculo de price_matches_pain

**Objetivo**: Entender por que el ratio es 32.1x para Termales (Tier C).

**Archivos afectados**:
- `modules/commercial_documents/coherence_validator.py`
- Diagnostico YAML de Termales (financial_value_central, precio propuesto)

**Pasos**:
1. En `coherence_validator.py`, localizar el check `price_matches_pain` (aprox L100-150).
2. Identificar la formula exacta: `ratio = precio_propuesto / dolor_financiero`.
3. Verificar que `dolor_financiero` usa `financial_value_central` (3,741,696 COP para Termales).
4. Verificar si el precio propuesto es fijo ($1,200,000/mes x 6 = $7,200,000 total) o mensual.
5. Calcular: si dolor = 3,741,696/mes y precio = 1,200,000/mes, ratio = 0.32x (no 32.1x). Identificar la unidad real.

**Criterios de aceptacion**:
- [ ] Formula documentada en comentario
- [ ] Unidades identificadas (mensual vs anual vs total)
- [ ] Causa del 32.1x explicada

---

### T4: SOL-4 — Implementar ajuste

**Objetivo**: Corregir el calculo o el threshold para que `price_matches_pain` no sea 0.0.

**Opciones** (elegir la minima segun hallazgo de T3):
- **A**: Si el dolor es anual y precio mensual, normalizar unidades.
- **B**: Si el precio total de 6 meses se compara contra dolor mensual, usar precio mensual.
- **C**: Si Tier C requiere threshold diferente, hacerlo dinamico por tier.

**Archivos afectados**:
- `modules/commercial_documents/coherence_validator.py`

**Criterios de aceptacion**:
- [ ] Ratio calculado < 6.0x para Termales (o threshold ajustado justificado)
- [ ] Score del check >= 0.4
- [ ] Tests pasan

---

## Tests Obligatorios

| Test | Archivo | Criterio de Exito |
|------|---------|-------------------|
| Coherence tests | `tests/` (buscar `coherence` o `validator`) | Pasan sin regresiones |
| Validaciones | `scripts/run_all_validations.py --quick` | 4/4 checks pass |

**Comando de validacion**:
```bash
./venv/Scripts/python.exe scripts/run_all_validations.py --quick
```

---

## Post-Ejecucion (OBLIGATORIO)

⚠️ **NO OMITIR** ⚠️

Al finalizar esta fase, actualizar INMEDIATAMENTE (antes de cerrar la sesion):

1. **`dependencias-fases.md`** (`.opencode/plans/PROP-PATCH/dependencias-fases.md`)
   - Marcar PATCH-A como ✅ Completada
   - Actualizar fecha de finalizacion

2. **`06-checklist-implementacion.md`**
   - Marcar todas las tareas de PATCH-A como completadas

3. **`09-documentacion-post-proyecto.md`**
   - **Seccion B**: Confirmar archivos modificados
   - **Seccion C**: Documentar backwards compatibility de SOL-1 y SOL-4
   - **Seccion D**: Actualizar metricas

4. **Evidencia**: Si se genero algun diagnostico de prueba, copiar a `evidence/PATCH-A/`

5. **`log_phase_completion.py`**:
   ```bash
   ./venv/Scripts/python.exe scripts/log_phase_completion.py \
       --fase PATCH-A \
       --desc "Fixes de coherencia y precio: SOL-1 (unificar coherence score) + SOL-4 (ajustar price_matches_pain)" \
       --archivos-mod "main.py,modules/commercial_documents/coherence_validator.py" \
       --check-manual-docs
   ```

---

## Criterios de Completitud (CHECKLIST)

⚠️ **Verificar ANTES de marcar como ✅ COMPLETADA** ⚠️

- [ ] **Tests nuevos pasan**: Todos los tests de esta fase ejecutan exitosamente
- [ ] **Validaciones del proyecto**: `./venv/Scripts/python.exe scripts/run_all_validations.py --quick` pasa 4/4
- [ ] **`dependencias-fases.md` actualizado**: Estado de PATCH-A marcado
- [ ] **Metricas consistentes**: Conteo de tests, version, fechas coinciden
- [ ] **Documentacion afiliada**: GUIA_TECNICA.md (via log_phase_completion audit)
- [ ] **Post-ejecucion completada**: Todos los puntos de la seccion anterior realizados

**NO marcar la fase como completada si algun criterio falla.**

---

## Restricciones

- **Maximo 60 iteraciones**
- **NO reordenar el pipeline** (leccion PROP-A: el problema es timing, no orden)
- **NO modificar** `v4_diagnostic_generator.py` ni templates (leccion PROP-A: solo 1 linea en main.py)
- **NO modificar** `modules/asset_generation/`, `proposal_generator.py`, ni archivos de propuesta (reservado para PATCH-B)
- **NO ejecutar v4complete** en esta fase (reservado para PATCH-C)
- **NO modificar ROADMAP.md**
- Preservar backwards compatibility: si `asset_result` es None, fallback a `pre_coherence_score`
