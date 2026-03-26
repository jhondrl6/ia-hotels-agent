"""
Tests for price consistency between financial_scenarios.json and proposal document.
FASE 13: Price Unification fix verification.
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import List

from modules.commercial_documents.data_structures import (
    DiagnosticSummary, FinancialScenarios, Scenario, AssetSpec, ConfidenceLevel,
)
from modules.data_validation.confidence_taxonomy import ConfidenceLevel as DVConfidence
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.financial_engine.pricing_resolution_wrapper import PricingResolutionResult


def make_scenarios(conservative_max, realistic_max, optimistic_max):
    conservative = Scenario(monthly_loss_min=0, monthly_loss_max=conservative_max, probability=0.70, description="Conservative")
    realistic = Scenario(monthly_loss_min=0, monthly_loss_max=realistic_max, probability=0.20, description="Realistic")
    optimistic = Scenario(monthly_loss_min=0, monthly_loss_max=optimistic_max, probability=0.10, description="Optimistic")
    return FinancialScenarios(conservative=conservative, realistic=realistic, optimistic=optimistic)


def make_summary(hotel_name="Hotel Test"):
    return DiagnosticSummary(
        hotel_name=hotel_name,
        critical_problems_count=1,
        quick_wins_count=0,
        overall_confidence=DVConfidence.VERIFIED,
        top_problems=[],
        validated_data_summary={}
    )


def run_generate(generator, pricing_result=None):
    fs = make_scenarios(2000000, 2610000, 3500000)
    summary = make_summary("Hotel Visperas")
    with patch.object(generator, '_load_template', return_value=""), \
         patch.object(generator, '_prepare_template_data', return_value={}), \
         patch.object(generator, '_render_template', return_value="Test"), \
         patch('pathlib.Path.mkdir', return_value=True), \
         patch('builtins.open', MagicMock()):
        return generator.generate(
            diagnostic_summary=summary,
            financial_scenarios=fs,
            asset_plan=[],
            hotel_name="Hotel Visperas",
            output_dir="/tmp/test_proposal",
            pricing_result=pricing_result
        )


class TestPriceConsistency:
    """FASE 13: Price consistency tests."""

    def test_price_uses_pricing_result_when_provided(self):
        """pricing_result.monthly_price_cop should be used directly."""
        pricing_result = PricingResolutionResult(
            monthly_price_cop=130500, tier="boutique", pain_ratio=0.05,
            is_compliant=True, expected_loss_cop=2610000, source="legacy_fixed",
            used_new_calculation=False
        )
        generator = V4ProposalGenerator()
        run_generate(generator, pricing_result=pricing_result)
        assert generator._current_price_monthly == 130500, \
            f"Expected 130500, got {generator._current_price_monthly}"

    def test_price_uses_legacy_formula_when_no_pricing_result(self):
        """Without pricing_result, legacy formula applies (min 800k)."""
        generator = V4ProposalGenerator()
        run_generate(generator, pricing_result=None)
        # expected_monthly = 2000000*0.7 + 2610000*0.2 + 3500000*0.1 = 2407000
        # price = 2407000 * 0.02 = 48140, bounded to min 800000
        assert generator._current_price_monthly == 800000, \
            f"Expected 800000 (min bound), got {generator._current_price_monthly}"

    def test_pricing_result_takes_precedence_over_price_monthly(self):
        """When both are provided, pricing_result takes precedence."""
        pricing_result = PricingResolutionResult(
            monthly_price_cop=130500, tier="boutique", pain_ratio=0.05,
            is_compliant=True, expected_loss_cop=2610000, source="legacy_fixed",
            used_new_calculation=False
        )
        generator = V4ProposalGenerator()
        fs = make_scenarios(2000000, 2610000, 3500000)
        summary = make_summary("Hotel Visperas")
        with patch.object(generator, '_load_template', return_value=""), \
             patch.object(generator, '_prepare_template_data', return_value={}), \
             patch.object(generator, '_render_template', return_value="Test"), \
             patch('pathlib.Path.mkdir', return_value=True), \
             patch('builtins.open', MagicMock()):
            generator.generate(
                diagnostic_summary=summary,
                financial_scenarios=fs,
                asset_plan=[],
                hotel_name="Hotel Visperas",
                output_dir="/tmp/test_proposal",
                price_monthly=999999,
                pricing_result=pricing_result
            )
        assert generator._current_price_monthly == 130500, \
            "pricing_result should take precedence"

    def test_proposal_price_matches_financial_scenarios(self):
        """End-to-end: price in proposal matches financial_scenarios calculation."""
        expected_monthly_loss = 2610000
        pain_ratio = 0.05
        calculated_price = int(expected_monthly_loss * pain_ratio)
        pricing_result = PricingResolutionResult(
            monthly_price_cop=calculated_price, tier="boutique", pain_ratio=pain_ratio,
            is_compliant=True, expected_loss_cop=expected_monthly_loss, source="legacy_fixed",
            used_new_calculation=False
        )
        generator = V4ProposalGenerator()
        run_generate(generator, pricing_result=pricing_result)
        assert generator._current_price_monthly == calculated_price
        assert generator._current_price_monthly != 800000  # Bug is fixed


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
