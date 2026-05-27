# FASE-4: Arbitraje Ético Gate + Garantía Día 55

## Instrucciones de la sesión

> **REGLA**: Una fase = una sesión. No ejecutar múltiples fases aquí.
> **Tipo de ejecución**: DIRECTA (código + tests)
> **Plan**: ROICR
> **Prerrequisito**: FASE-3 completada (pipeline unificado + roi_formatter + curva)

## Contexto previo

FASE-1: Validator semántico. FASE-2: Gate P1 BLOCKING. FASE-3: Pipeline pricing 3 pasos + CAPEX/OPEX desacoplado + curva 4 pilares. Ahora cerramos la capa de protección comercial: un arbitraje ético que impida propuestas donde el fee supera el recovery, y la garantía auditable del Día 55.

## Objetivo de esta fase

Implementar el arbitraje ético (gate que bloquea si fee > 60% del recovery) y la garantía del Día 55 con comando CLI ejecutable.

### Tareas

- [ ] **4A**: Crear `modules/quality/financial_coherence_validator.py`
  - Función `validar_arbitraje_etico(proposal_data) -> ValidationReport`
  - Si `monthly_fee > expected_monthly_recovery * 0.60`:
    - Retornar `ValidationReport(is_valid=False, errors=["ETHICS GATE: ..."])`
  - Caso contrario: `ValidationReport(is_valid=True)`
  - Integrar como gate en el pipeline de generación de propuestas (importar en el orchestrador)

- [ ] **4B**: Crear `modules/analytics/guarantee_validator.py`
  - Función `validar_garantia_dia55(hotel_url, hotel_id) -> GuaranteeResult`
  - Flujo:
    1. Cargar línea base del Día 0 desde onboarding (`load_baseline`)
    2. Consultar GSC actual (simular si no hay API key real)
    3. Comparar KPIs: impresiones, clics, posición promedio
    4. Si mejora < threshold → generar `CREDIT_NOTE.md` + `billing_adjustment.yaml`
  - Generar outputs en `outputs/{hotel_id}/guarantees/`
  - **NOTA**: Si no hay acceso a GSC API, implementar con stub/mock que acepte datos manuales

- [ ] **4C**: Agregar comando `validate-guarantee` a `main.py`
  - `python main.py validate-guarantee --url [hotel_url]`
  - Debe ejecutar `validar_garantia_dia55()` y mostrar resultado
  - **Verificar la estructura de main.py** — puede usar argparse, click, o typer

- [ ] **4D**: Tests
  - `tests/test_financial_coherence_validator.py`:
    - Test fee < 60% recovery → PASS
    - Test fee > 60% recovery → BLOCK
    - Test fee = 60% exacto → PASS (límite inclusivo)
  - `tests/test_guarantee_validator.py`:
    - Test KPIs mejorados → no trigger
    - Test KPIs sin mejora → trigger + CREDIT_NOTE generada
    - Test sin baseline → error controlado

### Restricciones

- NO modificar el pipeline de pricing (ya está en FASE-3)
- NO modificar publication_gates.py (ya está en FASE-2)
- La garantía debe funcionar incluso sin GSC API real (modo simulación/stub)
- El arbitraje ético usa 0.60 como threshold (60%), NO 0.50 (eso es el Value-Capture Cap del pricing)

### Criterios de completitud

- [ ] `financial_coherence_validator.py` existe con `validar_arbitraje_etico()`
- [ ] `guarantee_validator.py` existe con `validar_garantia_dia55()`
- [ ] `python main.py validate-guarantee --help` muestra ayuda
- [ ] `pytest tests/test_financial_coherence_validator.py tests/test_guarantee_validator.py -v` pasa
- [ ] Documentar resultado en `09-documentacion-post-proyecto.md` §FASE-4

### Próxima sesión

FASE-5: Actualizar fixtures financieros, re-calibrar regression guardian, crear tests del pipeline unificado. Ejecutar pytest completo.
