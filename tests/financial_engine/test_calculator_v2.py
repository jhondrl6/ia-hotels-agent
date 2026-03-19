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
