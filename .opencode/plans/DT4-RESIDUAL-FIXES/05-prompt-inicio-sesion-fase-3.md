# FASE-3: DT4-N4-COHERENCE — Unify Coherence Score Source

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA
> **Iteraciones máx**: 60
> **Depende de**: FASE-2 ✅ (SitePresence propagado)
> **Bloquea a**: FASE-6 (E2E)

## Contexto de Fases Anteriores

**FASE-2 completada**: SitePresence ya está normalizado (adapter `normalize_site_presence()`) y propagado a los 3 call sites de `CoherenceValidator`. El `site_presence_report` canónico existe en el assessment o se pasa como parámetro.

## ⚠️ Hechos Confirmados

- `AssetGenerationResult` conserva `coherence_report` (pre-gen) y `post_coherence_score` (número separado)
- `AssessmentBuilder.with_coherence()` usa `asset_result.coherence_report.overall_score` → score PRE-gen (L137-146)
- El asset report muestra `coherence_score_pre: 0.84`, `coherence_score_post: 0.82`, pero el gate report usa `0.8424...`
- No existe `final_coherence_report` como fuente única

## Objetivo

Definir `final_coherence_report` como única fuente canónica. Conservar pre/post como trazabilidad. Unificar consumidores (AssessmentBuilder, gate report, v4complete report).

## Tareas

### T1: Agregar `final_coherence_report` a `AssetGenerationResult`

- **Archivo**: `modules/asset_generation/v4_asset_orchestrator.py`
  - Después de la validación post-generación (L419-423), donde ya existe `post_coherence_report`:
    ```python
    # Asignar final_coherence_report
    if post_coherence_report:
        result.final_coherence_report = post_coherence_report
        result.final_coherence_score = post_coherence_report.overall_score
    else:
        result.final_coherence_report = pre_coherence_report
        result.final_coherence_score = pre_coherence_report.overall_score
    ```
  - Agregar campo `final_coherence_report` y `final_coherence_score` en `AssetGenerationResult` dataclass.

### T2: Modificar `AssessmentBuilder.with_coherence()` para usar score final

- **Archivo**: `modules/assessment_builder.py`
  - Cambiar `with_coherence()` (~L137-146) para aceptar y preferir `final_coherence_report`:
    ```python
    def with_coherence(self, asset_result) -> "AssessmentBuilder":
        if asset_result:
            # Preferir final_coherence_report si existe
            if hasattr(asset_result, 'final_coherence_report') and asset_result.final_coherence_report:
                self._payload.coherence_score = asset_result.final_coherence_report.overall_score
            elif hasattr(asset_result, 'coherence_report') and asset_result.coherence_report:
                self._payload.coherence_score = asset_result.coherence_report.overall_score
            else:
                self._payload.coherence_score = 0.0
        return self
    ```
  - Agregar campo `final_coherence_score` a `AssessmentPayload` si se quiere trazabilidad explícita.

### T3: Unificar consumidores del score

- **Archivo**: `main.py`
  - Donde se construye el `v4complete_report` o se usa el coherence score, usar `final_coherence_score` del `AssetGenerationResult`.
  - Verificar con `grep -n "coherence_score" main.py` que todos los puntos de consumo usen la misma fuente.

- **Archivo**: `modules/quality_gates/publication_gates.py` (si aplica)
  - El gate de coherencia debe leer `assessment.coherence_score` que ahora vendrá del `final_coherence_report`.

- **Archivo**: donde se genera `v4_complete_report.json`
  - Asegurar que el campo `coherence` use el score final.

### T4: Verificar fórmula ponderada + tests

- **Verificación manual** de la fórmula de weighted score en `CoherenceValidator`:
  ```bash
  grep -n "weighted_score\|overall_score\|_calculate" modules/commercial_documents/coherence_validator.py
  ```
  Confirmar que no hay bugs de ponderación.

- **Tests**:
  - Extender `tests/commercial_documents/test_financial_coherence.py`:
    - Test que verifica que `final_coherence_score` se asigna correctamente cuando post-gen existe
    - Test que verifica fallback a pre-gen cuando post-gen no existe
  - **Verificación**: `./venv/Scripts/python.exe -m pytest tests/commercial_documents/test_financial_coherence.py -q -k "final_coherence"`

## Criterios de Completitud

- [ ] `AssetGenerationResult` tiene campos `final_coherence_report` y `final_coherence_score`
- [ ] `AssessmentBuilder.with_coherence()` usa `final_coherence_report` cuando existe
- [ ] Todos los consumidores de coherence score usan la misma fuente
- [ ] `final_coherence_score` ≠ `coherence_score` en el reporte cuando hay diferencia pre/post
- [ ] Tests verifican asignación correcta y fallback
- [ ] Tests existentes no rompen: `./venv/Scripts/python.exe -m pytest tests/commercial_documents/ tests/test_assessment_builder.py -q`
- [ ] `log_phase_completion.py` ejecutado

## Restricciones

- **NO eliminar `coherence_report` (pre-gen) ni `post_coherence_score`** — conservar como trazabilidad
- **NO modificar la fórmula de weighted score** — solo verificar
- **NO ejecutar v4complete**
- Máximo 60 iteraciones

## Post-Ejecución (OBLIGATORIO)

```bash
./venv/Scripts/python.exe scripts/log_phase_completion.py \
    --fase FASE-3 \
    --desc "DT4-N4-COHERENCE: final_coherence_report as single source, AssessmentBuilder unificado, consumers migrated" \
    --archivos-mod "modules/asset_generation/v4_asset_orchestrator.py,modules/assessment_builder.py,main.py,modules/quality_gates/publication_gates.py" \
    --tests "2" \
    --check-manual-docs
```

## Próxima Sesión

FASE-4: DT4-N5-ALIGNMENT — Unify alignment reporting (publication gates ↔ delivery quality report)
