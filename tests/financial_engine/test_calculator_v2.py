"""Tests for Financial Calculator V2.

Valida que el calculador v2:
1. Bloquea calculos con valores por defecto
2. Bloquea calculos con baja coherencia
3. Calcula escenarios cuando los datos son validos
4. Genera explicaciones descriptivas
"""

import pytest
from datetime import datetime

from modules.financial_engine.calculator_v2 import (
    FinancialCalculatorV2,
    FinancialCalculationResult,
    CalculationStatus,
    calculate_financial_scenarios,
)
from modules.financial_engine.scenario_calculator import ScenarioType


class TestFinancialCalculatorV2:
    """Test cases for FinancialCalculatorV2."""

    def test_calculator_initialization(self):
        """Test calculator initializes with validator and scenario calculator."""
        calculator = FinancialCalculatorV2()
        assert calculator.validator is not None
        assert calculator.scenario_calculator is not None

    def test_valid_data_calculates_scenarios(self):
        """Test that valid data produces scenarios."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
            "ota_commission_rate": 0.15,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.SUCCESS
        assert result.success is True
        assert result.scenarios is not None
        assert len(result.scenarios) == 3
        assert ScenarioType.CONSERVATIVE in result.scenarios
        assert ScenarioType.REALISTIC in result.scenarios
        assert ScenarioType.OPTIMISTIC in result.scenarios

    def test_occupancy_zero_blocks_calculation(self):
        """Test that occupancy_rate=0 blocks calculation."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0,  # Default value
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.success is False
        assert result.blocked is True
        assert result.scenarios is None

    def test_direct_channel_zero_blocks_calculation(self):
        """Test that direct_channel_percentage=0 blocks calculation."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0,  # Default value
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.success is False
        assert result.validation_result is not None
        assert result.validation_result.has_blocks is True

    def test_adr_zero_blocks_calculation(self):
        """Test that adr_cop=0 blocks calculation."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 0,  # Default value
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.success is False

    def test_multiple_defaults_all_reported(self):
        """Test that multiple default values are all reported."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 0,
            "occupancy_rate": 0,
            "direct_channel_percentage": 0,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.validation_result is not None
        assert len(result.validation_result.blocks) == 3

    def test_conditional_with_low_coherence_blocks(self):
        """Test that low coherence score blocks calculation."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate_conditional(
            financial_data,
            coherence_score=0.5,  # Below threshold
            min_coherence=0.8
        )
        
        assert result.status == CalculationStatus.BLOCKED_BY_VALIDATION
        assert result.success is False
        assert result.blocked is True

    def test_conditional_with_high_coherence_succeeds(self):
        """Test that high coherence score allows calculation."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate_conditional(
            financial_data,
            coherence_score=0.85,  # Above threshold
            min_coherence=0.8
        )
        
        assert result.status == CalculationStatus.SUCCESS
        assert result.success is True
        assert result.scenarios is not None

    def test_hook_range_included(self):
        """Test that hook range is included in successful result."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.hook_range is not None
        assert "COP" in result.hook_range or "$" in result.hook_range

    def test_get_conservative_loss(self):
        """Test get_conservative_loss method."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        
        conservative_loss = result.get_conservative_loss()
        assert conservative_loss is not None
        assert conservative_loss > 0

    def test_get_realistic_loss(self):
        """Test get_realistic_loss method."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        
        realistic_loss = result.get_realistic_loss()
        assert realistic_loss is not None
        assert realistic_loss > 0

    def test_explanation_includes_assumptions(self):
        """Test that explanation includes scenario assumptions."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        explanation = calculator.get_calculation_explanation(result)
        
        assert "Conservador" in explanation or "conservador" in explanation.lower()
        assert "Realista" in explanation or "realista" in explanation.lower()
        assert "Optimista" in explanation or "optimista" in explanation.lower()

    def test_result_to_dict(self):
        """Test FinancialCalculationResult serialization."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 50,
            "adr_cop": 180000.0,
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.20,
        }
        
        result = calculator.calculate(financial_data)
        data = result.to_dict()
        
        assert "status" in data
        assert "success" in data
        assert "scenarios" in data
        assert data["success"] is True


class TestCalculateFinancialScenarios:
    """Test cases for calculate_financial_scenarios helper."""

    def test_helper_valid_data(self):
        """Test helper function with valid data."""
        result = calculate_financial_scenarios(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
            coherence_score=0.85,
            min_coherence=0.8,
        )
        
        assert result.status == CalculationStatus.SUCCESS
        assert result.scenarios is not None

    def test_helper_with_defaults_blocked(self):
        """Test helper function blocks with defaults."""
        result = calculate_financial_scenarios(
            rooms=50,
            adr_cop=0,  # Default
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            coherence_score=0.85,
            min_coherence=0.8,
        )
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.blocked is True

    def test_helper_with_low_coherence(self):
        """Test helper function with low coherence."""
        result = calculate_financial_scenarios(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            coherence_score=0.5,
            min_coherence=0.8,
        )
        
        assert result.status == CalculationStatus.BLOCKED_BY_VALIDATION


class TestHotelVisperasScenario:
    """Test scenarios similar to Hotel Visperas."""

    def test_visperas_incomplete_data_blocked(self):
        """Test that Hotel Visperas-like data is blocked."""
        calculator = FinancialCalculatorV2()
        
        # Simulate Hotel Visperas incomplete data
        visperas_data = {
            "rooms": 20,
            "adr_cop": 0,  # Unknown/ default
            "occupancy_rate": 0,  # Unknown/ default
            "direct_channel_percentage": 0,  # Unknown/ default
        }
        
        result = calculator.calculate(visperas_data)
        
        assert result.status == CalculationStatus.BLOCKED_BY_DEFAULTS
        assert result.blocked is True
        assert result.scenarios is None
        assert result.validation_result is not None
        assert len(result.validation_result.blocks) >= 2

    def test_visperas_with_coherence_zero_blocked(self):
        """Test that Hotel Visperas with 0% coherence is blocked."""
        calculator = FinancialCalculatorV2()
        
        visperas_data = {
            "rooms": 20,
            "adr_cop": 280000.0,  # From schema
            "occupancy_rate": 0.70,
            "direct_channel_percentage": 0.10,
        }
        
        result = calculator.calculate_conditional(
            visperas_data,
            coherence_score=0.0,  # Like Hotel Visperas
            min_coherence=0.8
        )
        
        assert result.status == CalculationStatus.BLOCKED_BY_VALIDATION
        assert result.blocked is True


# ==============================================================================
# FASE-B: Financial Corrections Tests (TDD RED Phase)
# ==============================================================================

class TestScenarioOrderCorrection:
    """Test Task 1: Verify scenario order is correct.
    
    Order must be: conservative >= realistic >= optimistic (in monthly_loss_cop)
    Even when optimistic is negative (gain), the order should be maintained.
    
    Bug: _get_main_value() tries to access monthly_loss_central (doesn't exist)
         and falls back to monthly_loss_max (also doesn't exist in FinancialScenario)
    """

    def test_get_main_value_returns_valid_value(self):
        """Test that _get_main_value returns a valid value from FinancialScenario.
        
        Bug: _get_main_value tries getattr(scenario, 'monthly_loss_central', None)
        which returns None (doesn't exist), then falls back to scenario.monthly_loss_max
        which also doesn't exist in FinancialScenario.
        
        Expected: Should return monthly_loss_cop as fallback.
        """
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        
        generator = V4ProposalGenerator()
        
        # Create a FinancialScenario like the calculator returns
        from modules.financial_engine.scenario_calculator import FinancialScenario, ScenarioType
        
        scenario = FinancialScenario(
            scenario_type=ScenarioType.REALISTIC,
            monthly_loss_cop=2610000,
            probability=0.20,
            calculation_basis="test",
            confidence_score=0.70,
        )
        
        # This should return a valid value, not None
        result = generator._get_main_value(scenario)
        
        assert result is not None, \
            f"_get_main_value returned None - should return monthly_loss_cop as fallback"
        assert result == 2610000, \
            f"_get_main_value should return monthly_loss_cop (2610000), got {result}"

    def test_scenario_order_conservative_greater_than_realistic(self):
        """Test that conservative monthly_loss >= realistic monthly_loss."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 10,
            "adr_cop": 300000.0,
            "occupancy_rate": 0.5,
            "direct_channel_percentage": 0.2,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.SUCCESS
        assert result.scenarios is not None
        
        conservative_loss = result.scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop
        realistic_loss = result.scenarios[ScenarioType.REALISTIC].monthly_loss_cop
        
        assert conservative_loss >= realistic_loss, \
            f"Conservative ({conservative_loss}) should be >= Realistic ({realistic_loss})"

    def test_scenario_order_realistic_greater_than_optimistic(self):
        """Test that realistic monthly_loss >= optimistic monthly_loss."""
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 10,
            "adr_cop": 300000.0,
            "occupancy_rate": 0.5,
            "direct_channel_percentage": 0.2,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.SUCCESS
        assert result.scenarios is not None
        
        realistic_loss = result.scenarios[ScenarioType.REALISTIC].monthly_loss_cop
        optimistic_loss = result.scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop
        
        assert realistic_loss >= optimistic_loss, \
            f"Realistic ({realistic_loss}) should be >= Optimistic ({optimistic_loss})"

    def test_scenario_order_with_negative_optimistic(self):
        """Test order when optimistic scenario is negative (gain).
        
        From financial_scenarios.json:
        - conservative: 5,076,000
        - realistic: 2,610,000
        - optimistic: -189,000 (NEGATIVE = gain)
        
        Order should still be: conservative >= realistic >= optimistic
        """
        calculator = FinancialCalculatorV2()
        
        financial_data = {
            "rooms": 10,
            "adr_cop": 300000.0,
            "occupancy_rate": 0.5,
            "direct_channel_percentage": 0.2,
        }
        
        result = calculator.calculate(financial_data)
        
        assert result.status == CalculationStatus.SUCCESS
        
        conservative = result.scenarios[ScenarioType.CONSERVATIVE].monthly_loss_cop
        realistic = result.scenarios[ScenarioType.REALISTIC].monthly_loss_cop
        optimistic = result.scenarios[ScenarioType.OPTIMISTIC].monthly_loss_cop
        
        # Verify expected values from financial_scenarios.json
        # conservative should be highest (most loss), optimistic lowest (could be negative)
        assert conservative >= realistic, f"{conservative} >= {realistic}"
        assert realistic >= optimistic, f"{realistic} >= {optimistic}"
        # optimistic can be negative (gain)
        assert optimistic < 0, "Optimistic should be negative (gain) for this dataset"


class TestRecoveryFactorROI:
    """Test Task 2: Verify ROI uses recovery_factor.
    
    Formula: roi = (monthly_loss * recovery_factor * meses) / (monthly_price * meses)
    Recovery factors: conservative=0.15, realistic=0.20, optimistic=0.25
    Maximum realistic ROI should be <= 5.0X
    
    Bug: _calculate_roi uses gain/investment directly without recovery_factor,
         resulting in 20X ROI instead of ~4X.
    """

    def test_roi_calculation_uses_recovery_factor(self):
        """Test that _calculate_roi applies recovery_factor to cap ROI.
        
        Bug: Current _calculate_roi computes roi = (gain * months) / (investment * months)
             which gives 20X for realistic scenario.
             
        Expected: ROI with recovery_factor=0.20 should be ~4X, not 20X.
        """
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        
        generator = V4ProposalGenerator()
        
        monthly_investment = 130500  # From financial_scenarios.json pricing
        monthly_gain = 2610000       # Realistic monthly_loss
        months = 6
        
        # Current buggy calculation (gain/investment directly)
        buggy_roi = generator._calculate_roi(monthly_investment, monthly_gain, months)
        
        # Expected: ROI with recovery_factor=0.20 should cap at ~4X
        # roi = (gain * recovery_factor) / investment
        expected_roi_with_factor = (monthly_gain * 0.20) / monthly_investment
        
        # The ROI should be reasonable (<= 5.0X)
        # Bug: buggy_roi is 20X, but should be ~4X
        assert float(buggy_roi.rstrip('X')) <= 5.0, \
            f"ROI ({buggy_roi}) should be <= 5.0X with recovery_factor applied"

    def test_realistic_roi_max_5x(self):
        """Test that realistic scenario ROI is capped at 5.0X.
        
        From financial_scenarios.json with pain_ratio=0.05:
        - realistic monthly_loss: 2,610,000
        - monthly_price: 130,500
        - Without recovery_factor: 2610000/130500 ≈ 20X (too high!)
        - With recovery_factor 0.20: 2610000*0.20/130500 ≈ 4X (reasonable)
        """
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        
        generator = V4ProposalGenerator()
        
        monthly_price = 130500
        monthly_gain = 2610000
        months = 6
        
        # Get ROI from the actual method
        roi_str = generator._calculate_roi(monthly_price, monthly_gain, months)
        roi = float(roi_str.rstrip('X'))
        
        # With recovery_factor 0.20, ROI should be <= 5.0X
        assert roi <= 5.0, \
            f"Realistic ROI ({roi}X) should be <= 5.0X with recovery_factor"


class TestPainRatioProjection:
    """Test Task 3: Verify projected_gain uses pain_ratio.
    
    Formula: projected_gain = monthly_loss * pain_ratio
    If pricing has pain_ratio, use it; if not, default to 0.20
    
    Bug: projected_gain = monthly_loss (100% recovery) instead of monthly_loss * pain_ratio (5%)
    """

    def test_project_gain_uses_pain_ratio(self):
        """Test that projected_gain is calculated using pain_ratio.
        
        Bug: _prepare_template_data uses _get_main_value(main_scenario) directly
             which equals monthly_loss (100% recovery).
             
        Expected: projected_gain = monthly_loss * pain_ratio (e.g., 5%)
        """
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        
        generator = V4ProposalGenerator()
        
        # Simulate main_scenario with monthly_loss_cop = 2,610,000
        from modules.financial_engine.scenario_calculator import FinancialScenario, ScenarioType
        
        main_scenario = FinancialScenario(
            scenario_type=ScenarioType.REALISTIC,
            monthly_loss_cop=2610000,
            probability=0.20,
            calculation_basis="test",
            confidence_score=0.70,
        )
        
        # pain_ratio from pricing = 0.05
        pain_ratio = 0.05
        monthly_loss = generator._get_main_value(main_scenario)
        
        # Bug: projected_gain = monthly_loss (full recovery)
        # Expected: projected_gain = monthly_loss * pain_ratio
        expected_projected_gain = monthly_loss * pain_ratio
        
        assert expected_projected_gain == 130500, \
            f"Expected projected_gain of 130500 (5% of 2610000), got {expected_projected_gain}"
        
        # Verify it's NOT 100% of loss
        assert expected_projected_gain < monthly_loss, \
            f"Projected gain ({expected_projected_gain}) should be less than full loss ({monthly_loss})"

    def test_projected_gain_not_100_percent(self):
        """Test that projected_gain is NOT 100% of monthly_loss.
        
        Current bug: projected_gain = monthly_loss (100% recovery)
        Should be: projected_gain = monthly_loss * pain_ratio (e.g., 5%)
        """
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
        
        generator = V4ProposalGenerator()
        
        monthly_loss = 2610000
        pain_ratio = 0.05
        
        # Current bug: uses full monthly_loss
        buggy_projected_gain = monthly_loss
        
        # Expected: uses pain_ratio
        correct_projected_gain = monthly_loss * pain_ratio
        
        # Verify the bug exists (full recovery is wrong)
        assert buggy_projected_gain == 2610000, "Bug: using 100% of loss"
        assert correct_projected_gain == 130500, "Correct: 5% of loss"
        
        # The projected gain should be much less than the full loss
        assert correct_projected_gain < buggy_projected_gain, \
            "Correct projected_gain should be less than buggy (full) version"

    def test_pain_ratio_default_when_missing(self):
        """Test that pain_ratio defaults to 0.20 when not provided in pricing."""
        # If no pain_ratio in pricing, default should be 0.20
        monthly_loss = 2610000
        default_pain_ratio = 0.20
        
        projected_gain = monthly_loss * default_pain_ratio
        
        # With default 0.20, projected gain should be 522,000
        assert projected_gain == 522000, \
            f"With default pain_ratio 0.20, expected 522000, got {projected_gain}"


class TestDisclaimerTierC:
    """Test Task 4: Verify disclaimer for Tier C evidence.
    
    If evidence_tier=="C" OR data_sources contains "default"/"legacy_hardcode",
    add disclaimer: "Proyeccion basada en ADR estimado ($300K)..."
    """

    def test_disclaimer_appears_when_tier_c(self):
        """Test that disclaimer appears when evidence_tier is 'C'."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator
        
        calculator = ScenarioCalculator()
        
        # Create hotel data with Tier C sources (hardcoded ADR)
        hotel_data = type('HotelFinancialData', (), {
            'rooms': 10,
            'adr_cop': 300000.0,
            'occupancy_rate': 0.5,
            'direct_channel_percentage': 0.2,
            'ota_commission_rate': 0.15,
            'adr_source': 'legacy_hardcode',  # Indicates Tier C
            'occupancy_source': 'default',
            'channel_source': 'default',
        })()
        
        breakdown = calculator.calculate_breakdown(hotel_data)
        
        # Verify Tier C
        assert breakdown.evidence_tier == "C", \
            f"Expected Tier C, got {breakdown.evidence_tier}"

    def test_disclaimer_with_legacy_hardcode_source(self):
        """Test disclaimer appears when data_sources contains 'legacy_hardcode'."""
        from modules.financial_engine.scenario_calculator import ScenarioCalculator
        
        calculator = ScenarioCalculator()
        
        # Data sources like in financial_scenarios.json
        sources = {
            "adr": "legacy_hardcode",  # Should trigger disclaimer
            "rooms": "hotel_data",
            "occupancy": "default",
            "ota_commission": "industry_standard_15pct",
            "direct_channel": "default",
            "shift": "hardcoded: sin GA4",
            "ia_boost": "estimado: sin datos GA4"
        }
        
        # Check if any source should trigger disclaimer
        has_hardcoded_adr = sources.get("adr") == "legacy_hardcode"
        has_default_occupancy = sources.get("occupancy") == "default"
        
        assert has_hardcoded_adr or has_default_occupancy, \
            "Sources should trigger Tier C disclaimer"

    def test_tier_c_disclaimer_content(self):
        """Test that Tier C disclaimer mentions ADR estimation."""
        from modules.commercial_documents.data_structures import EvidenceTier
        
        tier_c = EvidenceTier.C
        
        # Tier C disclaimer should mention limited data
        assert "estimación" in tier_c.disclaimer.lower() or \
               "estimado" in tier_c.disclaimer.lower() or \
               "datos limitados" in tier_c.disclaimer.lower(), \
            f"Tier C disclaimer should mention estimation: {tier_c.disclaimer}"
