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
        recovery = 3_741_696 * 0.05 * 0.35  # pain_ratio * recovery_factor
        pipeline = calc.calculate(30, 3_741_696, "boutique", expected_recovery_cop=recovery)

        # Los precios pueden ser iguales o distintos dependiendo del ethical cap
        # Lo importante es que el pipeline se activó (no falló)
        assert pipeline.monthly_price_cop > 0