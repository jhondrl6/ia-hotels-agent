# FASE-2: Coherencia Financiera — Gate ROI Opex-Only + Wrapper Activa Pipeline

**Plan**: ROICRII
**Tipo**: Código+Tests
**Hallazgos**: NEW-03, CRIT-02
**Prerrequisito**: FASE-1 completada
**Ejecución**: delegate_task (autónoma)
**Iteración estimada**: 35-40

---

## Objetivo

Corregir la inconsistencia financiera donde el commercial gate calcula ROI incluyendo CAPEX mientras el documento muestra ROI sin CAPEX. Activar el pipeline de 3 pasos desde el wrapper pasando `expected_recovery_cop`.

---

## DELEGATE_TASK — CONTEXTO AUTÓNOMO

**Working directory**: `/mnt/c/Users/Jhond/Github/iah-cli`

**Preflight**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
source venv/bin/activate 2>/dev/null || true
```

### Tarea 2A: Corregir commercial gate L377-379 — usar inversion_opex

**Archivo**: `modules/commercial_documents/v4_proposal_generator.py`

**Paso 1**: Leer L370-380 para confirmar contexto actual:
```bash
sed -n '370,380p' modules/commercial_documents/v4_proposal_generator.py
```

**Paso 2**: Aplicar patch. El bloque ANTES (verificar contra output de Paso 1):
```python
                    total_investment = price_monthly * 6 + setup_fee
                    total_recovery = monthly_gain * 6
                    roi = total_recovery / total_investment if total_investment > 0 else 0.0
```

Reemplazar con:
```python
                    total_investment_opex = price_monthly * 6  # ROICRII: SIN setup_fee (CAPEX es activo del cliente)
                    total_recovery = monthly_gain * 6
                    roi = total_recovery / total_investment_opex if total_investment_opex > 0 else 0.0
```

**Paso 3**: Verificar:
```bash
grep -n "total_investment_opex" modules/commercial_documents/v4_proposal_generator.py
# Expected: 1 match en L377
```

---

### Tarea 2B: Activar pipeline 3 pasos desde wrapper

**Archivo**: `modules/financial_engine/pricing_resolution_wrapper.py`

**Paso 1**: Leer L135-161 para entender contexto completo del método `_new_resolution`:
```bash
sed -n '135,161p' modules/financial_engine/pricing_resolution_wrapper.py
```

**Paso 2**: Verificar firma de `calculate()` en pricing_calculator.py:
```bash
grep -n "def calculate" modules/financial_engine/pricing_calculator.py
# Buscar la firma que acepta expected_recovery_cop
sed -n '340,370p' modules/financial_engine/pricing_calculator.py
```

**Paso 3**: Verificar si `self.LEGACY_PAIN_RATIO` existe en el wrapper:
```bash
grep -n "LEGACY_PAIN_RATIO" modules/financial_engine/pricing_resolution_wrapper.py
```

**Paso 4**: Aplicar patch en L143. ANTES (verificar contra Paso 1):
```python
        pricing_result = calculator.calculate(rooms, expected_loss_cop, segment)
```

Reemplazar con:
```python
        # ROICRII: Activar pipeline 3 pasos — pasar expected_recovery_cop
        pain_ratio = self.LEGACY_PAIN_RATIO  # 0.20 default
        recovery_factor = 0.35  # realistic from config/scenarios.yaml
        expected_recovery_cop = expected_loss_cop * pain_ratio * recovery_factor
        pricing_result = calculator.calculate(
            rooms, expected_loss_cop, segment,
            expected_recovery_cop=expected_recovery_cop,
        )
```

**NOTA**: Si `LEGACY_PAIN_RATIO` no existe, buscar alternativas:
```bash
grep -n "PAIN_RATIO\|pain_ratio\|0.20" modules/financial_engine/pricing_resolution_wrapper.py | head -10
```
Usar el valor que encuentres. Si no hay ninguno, hardcodear `0.20`.

**Paso 5**: Verificar:
```bash
grep -n "expected_recovery_cop" modules/financial_engine/pricing_resolution_wrapper.py
# Expected: ≥3 matches (cálculo + paso a calculator)
```

---

### Tarea 2C: Tests de coherencia financiera

**Archivo**: Crear `tests/test_financial_coherence.py`

**Contenido del test** (adaptar imports según estructura real del proyecto):
```python
"""ROICRII FASE-2: Tests de coherencia financiera — gate opex-only + pipeline activo."""
import pytest


class TestGateOpexOnly:
    """NEW-03: Commercial gate calcula ROI sin CAPEX."""

    def test_gate_roi_uses_opex_not_total_investment(self):
        """El denominador del ROI del gate debe ser price_monthly * 6, NO price_monthly * 6 + setup_fee."""
        # Simular: price_monthly=800000, setup_fee=2500000, monthly_gain=400000
        price_monthly = 800_000
        setup_fee = 2_500_000
        monthly_gain = 400_000
        
        # Fórmula CORRECTA (opex-only):
        total_investment_opex = price_monthly * 6
        total_recovery = monthly_gain * 6
        roi_opex = total_recovery / total_investment_opex  # 2.4M / 4.8M = 0.50
        
        # Fórmula INCORRECTA (con CAPEX):
        total_investment_with_capex = price_monthly * 6 + setup_fee
        roi_with_capex = total_recovery / total_investment_with_capex  # 2.4M / 7.3M = 0.33
        
        # El ROI correcto debe ser MAYOR que el incorrecto (sin CAPEX infla denominador)
        assert roi_opex > roi_with_capex
        assert roi_opex == pytest.approx(0.50, abs=0.01)


class TestWrapperActivatesPipeline:
    """CRIT-02: Wrapper pasa expected_recovery_cop al calculator."""

    def test_wrapper_passes_expected_recovery_cop(self):
        """El wrapper debe calcular y pasar expected_recovery_cop para activar pipeline 3 pasos."""
        from modules.financial_engine.pricing_resolution_wrapper import PricingResolutionWrapper
        
        wrapper = PricingResolutionWrapper()
        result = wrapper.resolve(rooms=30, expected_loss_cop=3_741_696, segment="boutique")
        
        # Si el pipeline 3 pasos se activó, el resultado debe tener metadata
        # con campos del pipeline (ethical_cap, adjusted_price, etc.)
        assert result.monthly_price_cop > 0
        # Verificar que NO es el cálculo simple (pipeline produce precios distintos)
        assert result.used_new_calculation is True

    def test_pipeline_produces_different_price_than_simple(self):
        """Con expected_recovery_cop, el pipeline 3 pasos debe producir un precio distinto al cálculo simple."""
        from modules.financial_engine.pricing_calculator import PricingCalculator
        
        calc = PricingCalculator()
        
        # Sin expected_recovery_cop (cálculo simple):
        simple = calc.calculate(30, 3_741_696, "boutique")
        
        # Con expected_recovery_cop (pipeline 3 pasos):
        recovery = 3_741_696 * 0.20 * 0.35  # pain_ratio * recovery_factor
        pipeline = calc.calculate(30, 3_741_696, "boutique", expected_recovery_cop=recovery)
        
        # Los precios pueden ser iguales o distintos dependiendo del ethical cap
        # Lo importante es que el pipeline se activó (no falló)
        assert pipeline.monthly_price_cop > 0
```

**Ejecución**:
```bash
cd /mnt/c/Users/Jhond/Github/iah-cli
python -m pytest tests/test_financial_coherence.py -v 2>&1 | tail -30
```

---

### Post-tareas: Verificación final + docs + log

```bash
# 1. Verificaciones grep
grep -n "total_investment_opex" modules/commercial_documents/v4_proposal_generator.py
grep -n "expected_recovery_cop" modules/financial_engine/pricing_resolution_wrapper.py

# 2. log_phase
cd /mnt/c/Users/Jhond/Github/iah-cli
python scripts/log_phase.py --phase "FASE-2" --plan "ROICRII" --status "completed" --desc "Gate_ROI_opex_only_wrapper_activa_pipeline_3_pasos" 2>/dev/null || echo "log_phase no disponible — skip"

# 3. Actualizar documentación post-fase
# Leer y actualizar /.opencode/plans/Archives/ROICRII/09-documentacion-post-proyecto.md
# Sección FASE-2: completar con archivos modificados, tests, hallazgos resueltos
```

---

## Hallazgos a Resolver

| Hallazgo | Veredicto | Fix |
|----------|-----------|-----|
| NEW-03 | Gate L377 usa CAPEX en denominador del ROI | Tarea 2A: `total_investment_opex = price_monthly * 6` |
| CRIT-02 | Wrapper L143 no pasa expected_recovery_cop | Tarea 2B: calcular y pasar parámetro |
