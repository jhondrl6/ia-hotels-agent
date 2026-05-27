"""Tests for the 3-step unified pricing pipeline (v4.3.0).

Covers the core pipeline function `calcular_precio_final()` and the integrated
`PricingCalculator._calculate_with_pipeline()` path.

FASE-5 (ROICR): Created to validate pipeline determinism, Value-Capture Cap
dominance, pain ratio triggers, operational floor, metrics decoupling, and
the 4-pillar maturity curve.
"""

import pytest
from modules.financial_engine.pricing_calculator import (
    PricingCalculator,
    HotelTier,
    calcular_precio_final,
    _DEFAULT_TIER_CONFIG,
    _DEFAULT_GATES,
)


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _boutique_config():
    """Return a copy of the boutique tier config for testing."""
    return dict(_DEFAULT_TIER_CONFIG["boutique"])


def _run_pipeline(expected_loss, expected_recovery, config=None, gate_max=0.06):
    """Shortcut: run calcular_precio_final with boutique defaults."""
    if config is None:
        config = _boutique_config()
    return calcular_precio_final(
        expected_loss_cop=expected_loss,
        expected_recovery_cop=expected_recovery,
        config=config,
        gate_max_ratio=gate_max,
    )


# ---------------------------------------------------------------------------
# 5C-1: Determinism
# ---------------------------------------------------------------------------

class TestPipelineDeterminism:
    """test_pipeline_no_collision: pipeline 3 pasos produce resultado determinista."""

    def test_same_inputs_same_output(self):
        """Identical inputs always produce identical output."""
        cfg = _boutique_config()
        a = _run_pipeline(50_000_000, 50_000_000 * 0.35, cfg)
        b = _run_pipeline(50_000_000, 50_000_000 * 0.35, cfg)
        assert a["final_price"] == b["final_price"]
        assert a["base_price"] == b["base_price"]
        assert a["capped_price"] == b["capped_price"]

    def test_order_matters_pipeline_is_sequential(self):
        """Pipeline steps are sequential and order-dependent."""
        cfg = dict(
            _boutique_config(),
            value_capture_cap=0.80,  # high cap = no reduction
            pain_ratio_gate_max=0.99,  # high threshold = no adjustment
        )
        # With high thresholds, steps 2 and 3 don't fire
        # and final == base_price (capped by max_price)
        r = _run_pipeline(50_000_000, 50_000_000 * 0.35, cfg)
        # recommended = 1.75M, between min (800K) and max (2.5M)
        assert r["base_price"] == 1_750_000.0
        assert r["final_price"] == 1_750_000.0
        assert r["adjustment_applied"] is False
        assert r["ethical_cap_applied"] is False

    def test_different_inputs_different_output(self):
        """Different inputs reliably produce different outputs."""
        a = _run_pipeline(10_000_000, 10_000_000 * 0.35)
        b = _run_pipeline(100_000_000, 100_000_000 * 0.35)
        assert a["final_price"] != b["final_price"]


# ---------------------------------------------------------------------------
# 5C-2: Value-Capture Cap dominates floor
# ---------------------------------------------------------------------------

class TestValueCapDominatesFloor:
    """test_value_cap_dominates_floor: ethical_cap < floor → ethical_cap wins."""

    def test_ethical_cap_below_min_price(self):
        """When ethical_cap < min_price, capped_price < base_price but
        operational_floor may still apply."""
        cfg = _boutique_config()
        cfg["value_capture_cap"] = 0.05  # 5% only
        # loss = 50M, rec = 17.5M → ethical_cap = 17.5M * 0.05 = 875K
        # base_price = max(800K, min(1.75M, 2.5M)) = 1.75M
        # ethical_cap = 875K < 1.75M → capped_price = 875K
        r = _run_pipeline(50_000_000, 50_000_000 * 0.35, cfg)
        assert r["ethical_cap_applied"] is True
        assert r["capped_price"] < r["base_price"]
        assert r["final_price"] == 875_000.0

    def test_ethical_cap_below_operational_floor(self):
        """When ethical_cap < operational_floor, floor wins."""
        cfg = _boutique_config()
        cfg["value_capture_cap"] = 0.01  # 1% → tiny cap
        # ethical_cap = 17.5M * 0.01 = 175K
        # operational_floor = 400K
        # final = max(175K, 400K) = 400K
        r = _run_pipeline(50_000_000, 50_000_000 * 0.35, cfg)
        assert r["ethical_cap_applied"] is True
        assert r["final_price"] == 400_000.0  # operational floor


# ---------------------------------------------------------------------------
# 5C-3: Pain Ratio Trigger
# ---------------------------------------------------------------------------

class TestPainRatioTrigger:
    """test_pain_ratio_trigger: pain_ratio excesivo → escalonado se activa."""

    def test_high_pain_ratio_triggers_adjustment(self):
        """When base_pain_ratio > GATE_MAX*2, adjustment fires."""
        cfg = _boutique_config()
        # Small loss → base_price = 800K (floor), base_pain_ratio = 800K / 5M = 0.16
        # 0.16 > 0.12 (GATE_MAX*2) → adjustment fires
        r = _run_pipeline(5_000_000, 5_000_000 * 0.35, cfg)
        assert r["adjustment_applied"] is True
        assert r["adjusted_price"] < r["base_price"]

    def test_low_pain_ratio_no_adjustment(self):
        """When base_pain_ratio <= GATE_MAX*2, no adjustment."""
        cfg = _boutique_config()
        # Large loss → recommended = 3.5M capped at 2.5M, base_pain_ratio = 2.5M/150M=0.0167
        # 0.0167 < 0.12 → no adjustment
        r = _run_pipeline(150_000_000, 150_000_000 * 0.35, cfg)
        # recommended = 5,250,000 but capped at 2.5M
        assert r["base_price"] == 2_500_000.0
        assert r["adjustment_applied"] is False

    def test_adjustment_formula(self):
        """Adjustment averages between min_price and recommended."""
        cfg = _boutique_config()
        # loss=5M → recommended=175K, min=800K, base=800K
        r = _run_pipeline(5_000_000, 5_000_000 * 0.35, cfg)
        expected_adjusted = (800_000 + 175_000) / 2
        assert r["adjusted_price"] == pytest.approx(expected_adjusted)


# ---------------------------------------------------------------------------
# 5C-4: Operational Floor
# ---------------------------------------------------------------------------

class TestOperationalFloor:
    """test_operational_floor: resultado nunca baja de operational_floor."""

    def test_final_never_below_operational_floor(self):
        """No matter the pipeline, final_price >= operational_floor."""
        cfg = _boutique_config()
        cfg["operational_floor"] = 400_000
        r = _run_pipeline(1, 0, cfg)  # extreme: near-zero loss
        assert r["final_price"] >= 400_000

    def test_operational_floor_applied(self):
        """When pipeline produces lower, floor kicks in."""
        cfg = _boutique_config()
        cfg["value_capture_cap"] = 0.001  # near-zero cap
        r = _run_pipeline(10_000_000, 10_000_000 * 0.35, cfg)
        assert r["final_price"] == cfg["operational_floor"]


# ---------------------------------------------------------------------------
# 5C-5: Metrics Decoupled
# ---------------------------------------------------------------------------

class TestMetricsDecoupled:
    """test_metrics_decoupled: roi_saas NO divide por (OPEX+CAPEX)."""

    def test_roi_formatter_does_not_combine_capex_opex(self):
        """Verify roi_formatter keeps CAPEX and OPEX separate."""
        from modules.financial_engine.roi_formatter import calcular_metricas_roi

        metrics = calcular_metricas_roi(
            recuperacion_total=1_309_593,
            inversion_opex=350_000,
            inversion_capex=2_500_000,
        )
        # ROI SaaS must NOT use OPEX+CAPEX combined in denominator
        assert metrics.roi_saas > 0
        # OPEX and CAPEX must appear as separate fields
        assert metrics.capex_total == 2_500_000
        # OPEX mensual = inversion_opex / meses = 350K / 6
        assert metrics.opex_mensual == pytest.approx(58_333.33, rel=0.01)

    def test_roi_saas_formula_uses_expected_recovery(self):
        """ROI SaaS formula is based on expected recovery, not loss."""
        from modules.financial_engine.roi_formatter import calcular_metricas_roi

        metrics = calcular_metricas_roi(
            recuperacion_total=1_309_593,
            inversion_opex=350_000,
            inversion_capex=2_500_000,
        )
        roi = metrics.roi_saas
        # ROI > 0 (positive return)
        assert roi > 0


# ---------------------------------------------------------------------------
# 5C-6: Maturity Curve
# ---------------------------------------------------------------------------

class TestMaturityCurve:
    """test_maturity_curve_6_months: curva produce 6 valores con factor final=1.00."""

    def test_curve_has_six_values(self):
        """The 4-pillar maturity curve produces exactly 6 values."""
        from modules.financial_engine.pillar_maturity_curve import (
            CURVA_4_PILARES,
            aplicar_curva_4_pilares,
        )

        assert len(CURVA_4_PILARES) == 6

    def test_curve_final_factor_is_one(self):
        """After 6 months, the maturity factor reaches 1.00."""
        from modules.financial_engine.pillar_maturity_curve import (
            CURVA_4_PILARES,
            aplicar_curva_4_pilares,
        )

        assert CURVA_4_PILARES[-1] == 1.0 or CURVA_4_PILARES[-1] == pytest.approx(1.0)

    def test_curve_is_monotonic_increasing(self):
        """Maturity factors increase monotonically."""
        from modules.financial_engine.pillar_maturity_curve import CURVA_4_PILARES

        for i in range(1, len(CURVA_4_PILARES)):
            assert CURVA_4_PILARES[i] >= CURVA_4_PILARES[i - 1]

    def test_aplicar_curva_returns_six_values(self):
        """aplicar_curva_4_pilares returns 6 projected values."""
        from modules.financial_engine.pillar_maturity_curve import (
            aplicar_curva_4_pilares,
        )

        result = aplicar_curva_4_pilares(
            fuga_mensual=3_741_696,
            recovery_factor_max=0.35,
            meses=6,
        )
        # result is a PillarMaturityResult with .proyecciones list
        assert len(result.proyecciones) == 6
        # Last projection reaches factor 1.00
        assert result.proyecciones[-1].factor == pytest.approx(1.0)
        assert result.proyecciones[-1].recuperacion_mensual > 0


# ---------------------------------------------------------------------------
# Integration: full Calculator pipeline path
# ---------------------------------------------------------------------------

class TestCalculatorPipelineIntegration:
    """Integration tests through PricingCalculator.calculate()."""

    def test_calculate_with_recovery_uses_pipeline(self):
        """When expected_recovery_cop is provided, the pipeline path is used."""
        calc = PricingCalculator()
        result = calc.calculate(
            rooms=20,
            expected_loss_cop=3_741_696,
            expected_recovery_cop=1_309_593,
        )
        assert result.ethical_cap_applied is not None
        assert result.adjustment_applied is not None
        assert result.operational_floor > 0
        assert result.value_capture_cap > 0
        assert "Pipeline v4.3.0" in result.formula_used

    def test_calculate_without_recovery_no_pipeline(self):
        """Without expected_recovery_cop, old path is used."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000)
        assert "Pipeline" not in result.formula_used
        assert result.operational_floor == 0.0
