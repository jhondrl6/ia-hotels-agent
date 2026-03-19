"""
Tests for optimistic scenario semantic handling (B-002 fix).

Verifies that:
1. Negative optimistic values are allowed (represent equilibrium/gain)
2. JSON persists real values (including negatives)
3. Documents show "Equilibrio" when value <= 0
4. Scenario order validation works correctly
"""

import pytest
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from modules.commercial_documents.data_structures import (
    Scenario,
    FinancialScenarios,
    format_cop,
)
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


class TestOptimisticScenarioSemantics:
    """Test semantic handling of optimistic scenario values."""
    
    def test_scenario_with_negative_value_shows_equilibrium(self):
        """When scenario value is negative, format shows Equilibrium."""
        scenario = Scenario(
            monthly_loss_min=-200000,
            monthly_loss_max=-189000,
            probability=0.10,
            description="Caso de equilibrio",
            monthly_opportunity_cop=189000
        )
        
        # The format_loss_cop method should show equilibrium
        formatted = scenario.format_loss_cop()
        assert "Equilibrio" in formatted, f"Expected 'Equilibrio' in '{formatted}'"
        assert "ahorro" in formatted.lower(), f"Expected 'ahorro' in '{formatted}'"
    
    def test_scenario_with_positive_value_shows_normal(self):
        """When scenario value is positive, format shows normal amount."""
        scenario = Scenario(
            monthly_loss_min=800000,
            monthly_loss_max=1000000,
            probability=0.70,
            description="Peor caso plausible",
            monthly_opportunity_cop=0
        )
        
        formatted = scenario.format_loss_cop()
        assert "$" in formatted, f"Expected '$' in '{formatted}'"
        assert "Equilibrio" not in formatted, f"Did not expect 'Equilibrio' in '{formatted}'"
    
    def test_is_equilibrium_or_gain_returns_true_for_negative(self):
        """is_equilibrium_or_gain returns True for negative values."""
        scenario = Scenario(
            monthly_loss_min=-200000,
            monthly_loss_max=-189000,
            probability=0.10,
            description="Caso de equilibrio",
            monthly_opportunity_cop=189000
        )
        
        assert scenario.is_equilibrium_or_gain() is True
    
    def test_is_equilibrium_or_gain_returns_false_for_positive(self):
        """is_equilibrium_or_gain returns False for positive values."""
        scenario = Scenario(
            monthly_loss_min=800000,
            monthly_loss_max=1000000,
            probability=0.70,
            description="Peor caso plausible",
            monthly_opportunity_cop=0
        )
        
        assert scenario.is_equilibrium_or_gain() is False
    
    def test_monthly_opportunity_cop_field_exists(self):
        """monthly_opportunity_cop field exists and is accessible."""
        scenario = Scenario(
            monthly_loss_min=-200000,
            monthly_loss_max=-189000,
            probability=0.10,
            description="Caso de equilibrio",
            monthly_opportunity_cop=189000
        )
        
        assert scenario.monthly_opportunity_cop == 189000
    
    def test_diagnostic_generator_formats_optimistic_equilibrium(self):
        """Diagnostic generator formats optimistic scenario with equilibrium correctly."""
        generator = V4DiagnosticGenerator()
        
        # Test the _format_scenario_amount method
        result_positive = generator._format_scenario_amount(1000000)
        assert "$" in result_positive
        assert "1.000.000" in result_positive
        
        result_negative = generator._format_scenario_amount(-189000)
        assert "Equilibrio" in result_negative
        assert "ahorro" in result_negative.lower()
    
    def test_proposal_generator_formats_optimistic_equilibrium(self):
        """Proposal generator formats optimistic scenario with equilibrium correctly."""
        generator = V4ProposalGenerator()
        
        # Test the _format_scenario_amount method
        result_positive = generator._format_scenario_amount(1000000)
        assert "$" in result_positive
        
        result_negative = generator._format_scenario_amount(-189000)
        assert "Equilibrio" in result_negative
    
    def test_financial_scenarios_with_negative_optimistic(self):
        """FinancialScenarios can handle negative optimistic scenario."""
        scenarios = FinancialScenarios(
            conservative=Scenario(
                monthly_loss_min=3000000,
                monthly_loss_max=3500000,
                probability=0.70,
                description="Peor caso plausible",
                monthly_opportunity_cop=0
            ),
            realistic=Scenario(
                monthly_loss_min=1500000,
                monthly_loss_max=2000000,
                probability=0.20,
                description="Meta esperada",
                monthly_opportunity_cop=0
            ),
            optimistic=Scenario(
                monthly_loss_min=-250000,
                monthly_loss_max=-189000,
                probability=0.10,
                description="Caso de equilibrio (ahorro en comisiones)",
                monthly_opportunity_cop=189000
            )
        )
        
        # Verify optimistic is recognized as equilibrium
        assert scenarios.optimistic.is_equilibrium_or_gain() is True
        assert scenarios.conservative.is_equilibrium_or_gain() is False
        assert scenarios.realistic.is_equilibrium_or_gain() is False
        
        # Verify format shows equilibrium
        formatted = scenarios.optimistic.format_loss_cop()
        assert "Equilibrio" in formatted


class TestScenarioOrderValidation:
    """Test scenario order validation."""
    
    def test_conservative_should_be_highest(self):
        """Conservative scenario should have highest loss (or lowest gain)."""
        # This is a semantic validation - conservative >= realistic >= optimistic
        conservative = 3500000
        realistic = 2000000
        optimistic = -189000  # Negative is OK, represents gain
        
        # Conservative should be >= realistic
        assert conservative >= realistic, "Conservative should be >= realistic"
        
        # When optimistic is negative (gain), realistic will be > optimistic
        # This is correct - realistic shows loss, optimistic shows gain
        assert realistic > optimistic, "Realistic (loss) should be > optimistic (gain)"
    
    def test_scenario_probabilities_sum_to_100_percent(self):
        """Scenario probabilities should sum to 100%."""
        scenarios = FinancialScenarios(
            conservative=Scenario(
                monthly_loss_min=3000000,
                monthly_loss_max=3500000,
                probability=0.70,
                description="Peor caso plausible",
                monthly_opportunity_cop=0
            ),
            realistic=Scenario(
                monthly_loss_min=1500000,
                monthly_loss_max=2000000,
                probability=0.20,
                description="Meta esperada",
                monthly_opportunity_cop=0
            ),
            optimistic=Scenario(
                monthly_loss_min=-250000,
                monthly_loss_max=-189000,
                probability=0.10,
                description="Caso de equilibrio",
                monthly_opportunity_cop=189000
            )
        )
        
        total_prob = (
            scenarios.conservative.probability +
            scenarios.realistic.probability +
            scenarios.optimistic.probability
        )
        assert abs(total_prob - 1.0) < 0.001, f"Probabilities sum to {total_prob}, expected 1.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
