# FASE-PF-2: Fix delivery_ready_percentage — Fórmula Correcta

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código + tests, sin comandos largos)
> **Presupuesto**: ~25 iteraciones (2 tareas + tests)

## Contexto previo

**Plan:** PIPELINE-FIX (`.opencode/plans/PIPELINE-FIX-PLAN.md`)
**Fase anterior:** FASE-PF-1 completada — assessment dict ahora inyecta pain_ledger, pain_ids, y financial_evidence_tier.

### Hallazgo que resuelve

**NUEVO-7 (MEDIO):** `delivery_ready_percentage` en `asset_generation_report.json` usa fórmula incorrecta.

**Fórmula actual (INCORRECTA)** en `v4_asset_orchestrator.py:125-132`:
```python
estimated_count = sum(
    1 for a in self.generated_assets if a.preflight_status.upper() == "WARNING"
)
delivery_ready_pct = (
    ((generated_count - estimated_count) / generated_count) * 100
    if generated_count > 0
    else 0.0
)
```
→ Cuenta assets con preflight WARNING como "not ready". Pero un asset puede tener WARNING y confidence 0.8 (RECOMMENDED priority + fallback action = 0.8). Resultado: 50.0% cuando la realidad es 91.7%.

**Fórmula correcta (debe usar confidence_score):**
```python
CONFIDENCE_THRESHOLD = 0.65
ready_count = sum(
    1 for a in self.generated_assets 
    if a.confidence_score >= CONFIDENCE_THRESHOLD
)
delivery_ready_pct = (
    (ready_count / generated_count) * 100
    if generated_count > 0
    else 0.0
)
```
→ 11/12 = 91.7% para Hotel Castilla Real.

## Objetivo de esta fase

Cambiar la métrica `delivery_ready_percentage` para que refleje el contrato de negocio: assets con confidence_score ≥ 0.65 son "delivery ready".

### Tareas

#### T1: Cambiar fórmula en v4_asset_orchestrator.py

- **Dónde:** `modules/asset_generation/v4_asset_orchestrator.py:125-132` (método `to_dict()`)
- **Qué:** Reemplazar la lógica de `estimated_count` + `delivery_ready_pct`:
```python
CONFIDENCE_THRESHOLD = 0.65
ready_count = sum(
    1 for a in self.generated_assets
    if a.confidence_score >= CONFIDENCE_THRESHOLD
)
delivery_ready_pct = (
    (ready_count / generated_count) * 100
    if generated_count > 0
    else 0.0
)
```
- **Nota:** NO eliminar `estimated_count` si se usa en otras partes del dict (línea 145: `"estimated": estimated_count`). Verificar si `estimated` se usa como campo del summary — si sí, MANTENER la variable pero renombrar la semántica:
```python
# Mantener estimated_count para backward compat del campo "estimated"
estimated_count = sum(
    1 for a in self.generated_assets if a.preflight_status.upper() == "WARNING"
)
# PIPELINE-FIX: delivery_ready usa confidence_score, no preflight_status
CONFIDENCE_THRESHOLD = 0.65
ready_count = sum(
    1 for a in self.generated_assets
    if a.confidence_score >= CONFIDENCE_THRESHOLD
)
delivery_ready_pct = (
    (ready_count / generated_count) * 100
    if generated_count > 0
    else 0.0
)
```
- **Verificar:** El campo `"estimated"` en el summary sigue presente (backward compat). Solo `delivery_ready_percentage` cambia de fórmula.

#### T2: Tests unitarios

- **Qué:** Crear o extender tests que verifiquen:
  1. Asset con confidence_score=0.8 y preflight_status=WARNING → cuenta como "ready"
  2. Asset con confidence_score=0.5 → NO cuenta como "ready"
  3. Asset con confidence_score=0.65 → cuenta como "ready" (boundary)
  4. Asset con confidence_score=0.64 → NO cuenta como "ready" (boundary)
  5. Escenario completo: 11/12 ≥0.65 → 91.67%
  6. Edge case: 0 generated_assets → 0.0%
- **Dónde:** `tests/` — buscar tests existentes de `to_dict()` o crear `tests/test_pipeline_fix_delivery_ready.py`
- **Ejecutar:** `./venv/Scripts/python.exe -m pytest tests/test_pipeline_fix_delivery_ready.py -v`

### Restricciones

- NO modificar el campo `"estimated"` del summary (backward compat)
- NO ejecutar v4complete en esta fase (eso es FASE-PF-3)
- Verificar que `confidence_score` es un atributo disponible en `generated_assets` items
- Mantener el threshold 0.65 como constante nombrada (no magic number)

### Criterios de completitud

- [x] T1: Fórmula cambiada a `confidence_score >= 0.65`
- [x] T1: Campo `"estimated"` preservado en summary (backward compat)
- [x] T2: Tests pasan (9 tests cubriendo boundary conditions)
- [x] Tests existentes de v4_asset_orchestrator siguen pasando (tests/asset_generation/test_report_generator.py: 10/10 PASS)
- [x] `python scripts/run_all_validations.py --quick` → sin nuevos errores (solo pre-existentes)

### Próxima sesión

**FASE-PF-3**: Ejecución v4complete para Hotel Castilla Real + verificación de que los fixes producen los resultados esperados (coverage PASS, delivery_ready ~91.7%, proposal_asset_matrix.json generado).
