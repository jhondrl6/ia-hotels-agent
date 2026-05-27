# FASE-5: Fixtures Financieros + Regression Guardian + Tests del Pipeline

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (tests + fixtures)
> **Plan**: ROICR
> **Prerrequisito**: FASE-4 completada (arbitraje + garantía implementados)

## Contexto previo

FASE-1 a FASE-4 implementaron el código. Ahora el repo tiene +2,743 tests con fixtures que asumen el pipeline viejo (floor $1.2M, sin Value-Capture Cap, sin métricas desacoplados). Los tests financieros van a fallar masivamente. Esta fase actualiza fixtures, recalibra el guardian, y agrega tests específicos del nuevo pipeline.

## Objetivo de esta fase

Hacer que `pytest` pase al 100% con el nuevo motor financiero v3.0.

### Tareas

- [ ] **5A**: Actualizar `tests/fixtures/financial_scenarios.json`
  - Recalcular TODOS los valores esperados con el pipeline unificado de 3 pasos
  - Caso Castilla Real: expected_loss=3,741,696, recovery_factor=0.35
    - Paso 1: recommended=130,959, base_price=800,000 (floor)
    - Paso 2: pain_ratio=800K/3.74M=0.21 < 0.64, no se dispara escalonado
    - Paso 3: ethical_cap=1,309,593*0.50=654,796. final=min(800K, 654,796)=654,796
  - Verificar CADA fixture contra el pipeline real — no asumir valores del ROICR.md

- [ ] **5B**: Re-calibrar `v4_regression_guardian`
  - Los umbrales de tolerancia deben ajustarse a la nueva normalidad
  - El Value-Capture Cap produce precios más bajos → los rangos aceptables cambian
  - Buscar el guardian en el codebase (puede ser un script, un módulo, o un CI check)
  - Actualizar thresholds

- [ ] **5C**: Crear `tests/test_pricing_pipeline.py`
  - `test_pipeline_no_collision()`: pipeline 3 pasos produce resultado determinista
  - `test_value_cap_dominates_floor()`: ethical_cap < floor → ethical_cap wins
  - `test_pain_ratio_trigger()`: pain_ratio excesivo → escalonado se activa
  - `test_operational_floor()`: resultado nunca baja de operational_floor
  - `test_metrics_decoupled()`: roi_saas NO divide por (OPEX+CAPEX)
  - `test_maturity_curve_6_months()`: curva produce 6 valores con factor final=1.00

- [ ] **5D**: Ejecutar `pytest` completo
  - `cd /mnt/c/Users/Jhond/Github/iah-cli && python -m pytest --timeout=120 -x`
  - Si hay fallos: diagnosticar si son regresiones nuevas o pre-existentes
  - Fix regresiones nuevas. Documentar pre-existentes conocidas.
  - **Objetivo**: 0 regresiones nuevas

### Restricciones

- NO modificar código de FASE-1 a FASE-4 — solo fixtures y tests
- Si un fixture falla por cambio de formato (no de valor), investigar ANTES de parchear
- Los tests pre-existentes que fallan por razones NO relacionadas con este plan → documentar, NO fixear

### Criterios de completitud

- [ ] `financial_scenarios.json` actualizado con valores del pipeline v3.0
- [ ] `v4_regression_guardian` recalibrado (o documentado como pre-existente)
- [ ] `tests/test_pricing_pipeline.py` existe y pasa
- [ ] `pytest` completo sin regresiones nuevas
- [ ] Documentar resultado en `09-documentacion-post-proyecto.md` §FASE-5

### Próxima sesión

FASE-6: Ejecución de v4complete para Hotel Castilla Real + análisis post-implementación de los 6 niveles de éxito. ÚNICA ejecución de v4complete en todo el plan.
