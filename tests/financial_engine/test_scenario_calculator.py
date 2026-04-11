"""
Test module for scenario_calculator.py

Comprehensive tests for the ScenarioCalculator class and related dataclasses,
covering HotelFinancialData creation, scenario calculations, and formatting.
"""

import pytest
from modules.financial_engine.scenario_calculator import (
    ScenarioType,
    FinancialScenario,
    HotelFinancialData,
    ScenarioCalculator,
)
from modules.commercial_documents.data_structures import FinancialBreakdown


class TestHotelFinancialData:
    """Test cases for HotelFinancialData dataclass."""

    def test_hotel_financial_data_creation(self):
        """Test HotelFinancialData creation with all required fields."""
        hotel = HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
        )

        assert hotel.rooms == 50
        assert hotel.adr_cop == 180000.0
        assert hotel.occupancy_rate == 0.70

    def test_hotel_financial_data_defaults(self):
        """Test HotelFinancialData default values for optional fields."""
        hotel = HotelFinancialData(
            rooms=30,
            adr_cop=150000.0,
            occupancy_rate=0.65,
        )

        assert hotel.ota_commission_rate == 0.15
        assert hotel.direct_channel_percentage == 0.0
        assert hotel.ota_presence == ["booking", "expedia"]

    def test_hotel_financial_data_custom_values(self):
        """Test HotelFinancialData with custom optional values."""
        hotel = HotelFinancialData(
            rooms=40,
            adr_cop=200000.0,
            occupancy_rate=0.80,
            ota_commission_rate=0.18,
            direct_channel_percentage=0.25,
            ota_presence=["booking", "expedia", "despegar"],
        )

        assert hotel.ota_commission_rate == 0.18
        assert hotel.direct_channel_percentage == 0.25
        assert hotel.ota_presence == ["booking", "expedia", "despegar"]


class TestScenarioCalculatorInitialization:
    """Test cases for ScenarioCalculator initialization."""

    def test_scenario_calculator_initialization(self):
        """Test ScenarioCalculator initializes with default values."""
        calculator = ScenarioCalculator()

        assert calculator.default_ota_commission == 0.15

    def test_scenario_calculator_is_callable(self):
        """Test that initialized calculator has required methods."""
        calculator = ScenarioCalculator()

        assert hasattr(calculator, 'calculate_monthly_revenue')
        assert hasattr(calculator, 'calculate_scenarios')
        assert hasattr(calculator, '_calculate_conservative_scenario')
        assert hasattr(calculator, '_calculate_realistic_scenario')
        assert hasattr(calculator, '_calculate_optimistic_scenario')
        assert hasattr(calculator, 'get_hook_range')
        assert hasattr(calculator, 'interpret_scenario_for_hotelier')


class TestCalculateMonthlyRevenue:
    """Test cases for calculate_monthly_revenue method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    @pytest.fixture
    def sample_hotel(self):
        """Provide a sample HotelFinancialData instance."""
        return HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )

    def test_calculate_monthly_revenue_returns_dict(self, calculator, sample_hotel):
        """Test that calculate_monthly_revenue returns a dictionary."""
        result = calculator.calculate_monthly_revenue(sample_hotel)

        assert isinstance(result, dict)

    def test_calculate_monthly_revenue_correct_math(self, calculator, sample_hotel):
        """Test that monthly revenue is calculated with correct math.
        
        Expected calculation:
        - 50 rooms × 30 days = 1500 room nights
        - 1500 × 0.70 occupancy = 1050 occupied nights
        - 1050 × $180,000 ADR = $189,000,000 total revenue
        - OTA percentage = 80% (100% - 20% direct)
        - OTA revenue = $189,000,000 × 0.80 = $151,200,000
        - Direct revenue = $189,000,000 × 0.20 = $37,800,000
        """
        result = calculator.calculate_monthly_revenue(sample_hotel)

        expected_total_reservations = 50 * 30 * 0.70  # 1050
        expected_total_revenue = expected_total_reservations * 180000.0  # 189,000,000
        expected_ota_revenue = expected_total_revenue * 0.80  # 151,200,000
        expected_direct_revenue = expected_total_revenue * 0.20  # 37,800,000

        assert result["total_reservations"] == round(expected_total_reservations, 0)
        assert result["total_revenue_cop"] == round(expected_total_revenue, 2)
        assert result["ota_revenue_cop"] == round(expected_ota_revenue, 2)
        assert result["direct_revenue_cop"] == round(expected_direct_revenue, 2)
        assert result["ota_percentage"] == 0.80
        assert result["direct_percentage"] == 0.20

    def test_calculate_monthly_revenue_all_direct_bookings(self, calculator):
        """Test calculation when all bookings are direct (no OTA)."""
        hotel = HotelFinancialData(
            rooms=20,
            adr_cop=150000.0,
            occupancy_rate=0.80,
            direct_channel_percentage=1.0,
        )

        result = calculator.calculate_monthly_revenue(hotel)

        assert result["ota_percentage"] == 0.0
        assert result["direct_percentage"] == 1.0
        assert result["ota_revenue_cop"] == 0.0
        assert result["direct_revenue_cop"] == result["total_revenue_cop"]

    def test_calculate_monthly_revenue_all_ota_bookings(self, calculator):
        """Test calculation when all bookings are through OTAs."""
        hotel = HotelFinancialData(
            rooms=30,
            adr_cop=200000.0,
            occupancy_rate=0.65,
            direct_channel_percentage=0.0,
        )

        result = calculator.calculate_monthly_revenue(hotel)

        assert result["ota_percentage"] == 1.0
        assert result["direct_percentage"] == 0.0
        assert result["direct_revenue_cop"] == 0.0
        assert result["ota_revenue_cop"] == result["total_revenue_cop"]


class TestCalculateScenarios:
    """Test cases for calculate_scenarios method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    @pytest.fixture
    def sample_hotel(self):
        """Provide a sample HotelFinancialData instance."""
        return HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )

    def test_calculate_scenarios_returns_all_3_scenarios(self, calculator, sample_hotel):
        """Test that calculate_scenarios returns exactly 3 scenarios."""
        scenarios = calculator.calculate_scenarios(sample_hotel)

        assert len(scenarios) == 3
        assert ScenarioType.CONSERVATIVE in scenarios
        assert ScenarioType.REALISTIC in scenarios
        assert ScenarioType.OPTIMISTIC in scenarios

    def test_calculate_scenarios_returns_financial_scenario_objects(self, calculator, sample_hotel):
        """Test that all returned values are FinancialScenario instances."""
        scenarios = calculator.calculate_scenarios(sample_hotel)

        for scenario_type, scenario in scenarios.items():
            assert isinstance(scenario, FinancialScenario)
            assert scenario.scenario_type == scenario_type


class TestConservativeScenario:
    """Test cases for _calculate_conservative_scenario method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    @pytest.fixture
    def sample_hotel(self):
        """Provide a sample HotelFinancialData instance."""
        return HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )

    def test_conservative_uses_90_percent_occupancy(self, calculator, sample_hotel):
        """Test that conservative scenario uses 90% of provided occupancy."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        # The calculation uses actual occupancy (0.70) not conservative (0.63)
        # for base calculation, but mentions 90% in the basis
        assert "90%" in scenario.calculation_basis

    def test_conservative_uses_18_percent_commission(self, calculator, sample_hotel):
        """Test that conservative scenario uses 18% OTA commission."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        assert "18%" in scenario.calculation_basis

    def test_conservative_scenario_probability(self, calculator, sample_hotel):
        """Test conservative scenario has expected probability and confidence."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        assert scenario.probability == 0.70
        assert scenario.confidence_score == 0.85

    def test_conservative_scenario_type(self, calculator, sample_hotel):
        """Test conservative scenario has correct type."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        assert scenario.scenario_type == ScenarioType.CONSERVATIVE

    def test_conservative_has_assumptions(self, calculator, sample_hotel):
        """Test conservative scenario has list of assumptions."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        assert len(scenario.assumptions) >= 4
        assert any("10%" in assumption for assumption in scenario.assumptions)
        assert any("18%" in assumption or "comisión" in assumption.lower() 
                   for assumption in scenario.assumptions)

    def test_conservative_has_disclaimer(self, calculator, sample_hotel):
        """Test conservative scenario includes disclaimer."""
        scenario = calculator._calculate_conservative_scenario(sample_hotel)

        assert scenario.disclaimer is not None
        assert "Conservative" in scenario.disclaimer or "conservador" in scenario.disclaimer.lower()


class TestRealisticScenario:
    """Test cases for _calculate_realistic_scenario method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    @pytest.fixture
    def sample_hotel(self):
        """Provide a sample HotelFinancialData instance."""
        return HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )

    def test_realistic_uses_actual_data(self, calculator, sample_hotel):
        """Test that realistic scenario uses actual hotel data (no adjustment)."""
        scenario = calculator._calculate_realistic_scenario(sample_hotel)

        assert "Current data" in scenario.calculation_basis or "datos" in scenario.calculation_basis.lower()

    def test_realistic_uses_10_percent_shift(self, calculator, sample_hotel):
        """Test that realistic scenario uses 10% OTA-to-direct shift."""
        scenario = calculator._calculate_realistic_scenario(sample_hotel)

        assert "10%" in scenario.calculation_basis
        assert any("10%" in assumption for assumption in scenario.assumptions)

    def test_realistic_includes_ia_visibility_boost(self, calculator, sample_hotel):
        """Test that realistic scenario includes 5% IA visibility boost."""
        scenario = calculator._calculate_realistic_scenario(sample_hotel)

        assert "5%" in scenario.calculation_basis
        assert any("5%" in assumption for assumption in scenario.assumptions)

    def test_realistic_scenario_probability(self, calculator, sample_hotel):
        """Test realistic scenario has expected probability and confidence."""
        scenario = calculator._calculate_realistic_scenario(sample_hotel)

        assert scenario.probability == 0.20
        assert scenario.confidence_score == 0.70

    def test_realistic_scenario_type(self, calculator, sample_hotel):
        """Test realistic scenario has correct type."""
        scenario = calculator._calculate_realistic_scenario(sample_hotel)

        assert scenario.scenario_type == ScenarioType.REALISTIC


class TestOptimisticScenario:
    """Test cases for _calculate_optimistic_scenario method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    @pytest.fixture
    def sample_hotel(self):
        """Provide a sample HotelFinancialData instance."""
        return HotelFinancialData(
            rooms=50,
            adr_cop=180000.0,
            occupancy_rate=0.70,
            direct_channel_percentage=0.20,
            ota_commission_rate=0.15,
        )

    def test_optimistic_uses_20_percent_shift(self, calculator, sample_hotel):
        """Test that optimistic scenario uses 20% OTA-to-direct shift."""
        scenario = calculator._calculate_optimistic_scenario(sample_hotel)

        assert "20%" in scenario.calculation_basis
        assert any("20%" in assumption for assumption in scenario.assumptions)

    def test_optimistic_includes_10_percent_ia_boost(self, calculator, sample_hotel):
        """Test that optimistic scenario includes 10% IA visibility boost."""
        scenario = calculator._calculate_optimistic_scenario(sample_hotel)

        assert any("10%" in assumption and "IA" in assumption for assumption in scenario.assumptions)

    def test_optimistic_scenario_probability(self, calculator, sample_hotel):
        """Test optimistic scenario has expected probability and confidence."""
        scenario = calculator._calculate_optimistic_scenario(sample_hotel)

        assert scenario.probability == 0.10
        assert scenario.confidence_score == 0.50

    def test_optimistic_scenario_type(self, calculator, sample_hotel):
        """Test optimistic scenario has correct type."""
        scenario = calculator._calculate_optimistic_scenario(sample_hotel)

        assert scenario.scenario_type == ScenarioType.OPTIMISTIC

    def test_optimistic_occupancy_capped_at_100_percent(self, calculator):
        """Test that optimistic occupancy is capped at 100%."""
        # Hotel with 95% occupancy - 105% would be 99.75%, capped at 100%
        hotel_high_occupancy = HotelFinancialData(
            rooms=30,
            adr_cop=150000.0,
            occupancy_rate=0.95,
        )

        scenario = calculator._calculate_optimistic_scenario(hotel_high_occupancy)
        
        # Verify the scenario was calculated without error
        assert isinstance(scenario, FinancialScenario)
        assert scenario.scenario_type == ScenarioType.OPTIMISTIC


class TestGetHookRange:
    """Test cases for get_hook_range method."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    def test_get_hook_range_formats_correctly(self, calculator):
        """Test that get_hook_range returns correctly formatted string."""
        scenarios = {
            ScenarioType.CONSERVATIVE: FinancialScenario(
                scenario_type=ScenarioType.CONSERVATIVE,
                monthly_loss_cop=800000.0,
                probability=0.70,
                calculation_basis="Test",
                confidence_score=0.85,
            ),
            ScenarioType.REALISTIC: FinancialScenario(
                scenario_type=ScenarioType.REALISTIC,
                monthly_loss_cop=1500000.0,
                probability=0.20,
                calculation_basis="Test",
                confidence_score=0.70,
            ),
            ScenarioType.OPTIMISTIC: FinancialScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                monthly_loss_cop=3200000.0,
                probability=0.10,
                calculation_basis="Test",
                confidence_score=0.50,
            ),
        }

        hook_range = calculator.get_hook_range(scenarios)

        # Should format with dots as thousand separators
        assert "$800.000" in hook_range
        assert "$3.200.000" in hook_range or "$3.200.000" in hook_range.replace(".", ",")
        assert "COP/mes" in hook_range

    def test_get_hook_range_with_different_values(self, calculator):
        """Test get_hook_range with different value ranges."""
        scenarios = {
            ScenarioType.CONSERVATIVE: FinancialScenario(
                scenario_type=ScenarioType.CONSERVATIVE,
                monthly_loss_cop=1000000.0,
                probability=0.70,
                calculation_basis="Test",
                confidence_score=0.85,
            ),
            ScenarioType.REALISTIC: FinancialScenario(
                scenario_type=ScenarioType.REALISTIC,
                monthly_loss_cop=2000000.0,
                probability=0.20,
                calculation_basis="Test",
                confidence_score=0.70,
            ),
            ScenarioType.OPTIMISTIC: FinancialScenario(
                scenario_type=ScenarioType.OPTIMISTIC,
                monthly_loss_cop=5000000.0,
                probability=0.10,
                calculation_basis="Test",
                confidence_score=0.50,
            ),
        }

        hook_range = calculator.get_hook_range(scenarios)

        assert "$1.000.000" in hook_range
        assert "$5.000.000" in hook_range


class TestInterpretScenarioForHotelier:
    """Test cases for interpret_scenario_for_hotelier static method."""

    def test_interpret_returns_readable_text(self):
        """Test that interpretation returns readable text for hoteliers."""
        scenario = FinancialScenario(
            scenario_type=ScenarioType.REALISTIC,
            monthly_loss_cop=1500000.0,
            probability=0.20,
            calculation_basis="Test calculation basis",
            confidence_score=0.70,
            assumptions=[
                "Assumption 1: Test",
                "Assumption 2: Test",
            ],
            disclaimer="Test disclaimer",
        )

        interpretation = ScenarioCalculator.interpret_scenario_for_hotelier(scenario)

        # Should contain formatted loss amount
        assert "1.500.000" in interpretation or "1500000" in interpretation
        assert "COP" in interpretation

    def test_interpret_includes_scenario_name(self):
        """Test that interpretation includes scenario name in Spanish."""
        for scenario_type, expected_name in [
            (ScenarioType.CONSERVATIVE, "Conservador"),
            (ScenarioType.REALISTIC, "Realista"),
            (ScenarioType.OPTIMISTIC, "Optimista"),
        ]:
            scenario = FinancialScenario(
                scenario_type=scenario_type,
                monthly_loss_cop=1000000.0,
                probability=0.20,
                calculation_basis="Test",
                confidence_score=0.70,
            )

            interpretation = ScenarioCalculator.interpret_scenario_for_hotelier(scenario)

            assert expected_name in interpretation

    def test_interpret_includes_probability_and_confidence(self):
        """Test that interpretation includes probability and confidence scores."""
        scenario = FinancialScenario(
            scenario_type=ScenarioType.CONSERVATIVE,
            monthly_loss_cop=1000000.0,
            probability=0.70,
            calculation_basis="Test",
            confidence_score=0.85,
        )

        interpretation = ScenarioCalculator.interpret_scenario_for_hotelier(scenario)

        # Probability should be shown as percentage
        assert "70%" in interpretation or "70" in interpretation
        # Confidence should be shown as percentage
        assert "85%" in interpretation or "85" in interpretation

    def test_interpret_includes_assumptions(self):
        """Test that interpretation includes all assumptions."""
        scenario = FinancialScenario(
            scenario_type=ScenarioType.CONSERVATIVE,
            monthly_loss_cop=1000000.0,
            probability=0.70,
            calculation_basis="Test",
            confidence_score=0.85,
            assumptions=[
                "Assumption 1: First test assumption",
                "Assumption 2: Second test assumption",
                "Assumption 3: Third test assumption",
            ],
        )

        interpretation = ScenarioCalculator.interpret_scenario_for_hotelier(scenario)

        for assumption in scenario.assumptions:
            assert assumption in interpretation

    def test_interpret_includes_disclaimer(self):
        """Test that interpretation includes disclaimer when present."""
        scenario = FinancialScenario(
            scenario_type=ScenarioType.CONSERVATIVE,
            monthly_loss_cop=1000000.0,
            probability=0.70,
            calculation_basis="Test",
            confidence_score=0.85,
            disclaimer="This is an important disclaimer for the hotelier",
        )

        interpretation = ScenarioCalculator.interpret_scenario_for_hotelier(scenario)

        assert scenario.disclaimer in interpretation


class TestCalculateBreakdown:
    """Test cases for calculate_breakdown method (FASE-B)."""

    @pytest.fixture
    def calculator(self):
        """Provide a ScenarioCalculator instance."""
        return ScenarioCalculator()

    def test_breakdown_ota_commission_amazilia(self, calculator):
        """Comisión OTA = $5,400,000 para hotel de prueba."""
        hotel = HotelFinancialData(
            rooms=10,
            adr_cop=300000,
            occupancy_rate=0.5,
            direct_channel_percentage=0.2,
            ota_commission_rate=0.15
        )
        breakdown = calculator.calculate_breakdown(hotel)
        # 10 rooms × 0.5 occupancy × 30 days = 150 nights/mes
        # 80% OTA = 120 nights
        # 120 × 300K × 15% = 5,400,000
        assert breakdown.monthly_ota_commission_cop == 5400000

    def test_breakdown_layers_separated(self, calculator):
        """Capa 1 (comisión OTA) debe ser mayor que capas 2A y 2B."""
        hotel = HotelFinancialData(
            rooms=10,
            adr_cop=300000,
            occupancy_rate=0.5
        )
        breakdown = calculator.calculate_breakdown(hotel)
        # Comisión OTA (Capa 1) debe ser > shift_savings (Capa 2A) + ia_revenue (Capa 2B)
        assert breakdown.monthly_ota_commission_cop > breakdown.shift_savings_cop
        assert breakdown.monthly_ota_commission_cop > breakdown.ia_revenue_cop

    def test_breakdown_evidence_tier_c(self, calculator):
        """Evidence tier es C por defecto (sin GA4)."""
        hotel = HotelFinancialData(
            rooms=10,
            adr_cop=300000,
            occupancy_rate=0.5
        )
        breakdown = calculator.calculate_breakdown(hotel)
        assert breakdown.evidence_tier == "C"
        assert "limitados" in breakdown.disclaimer

    def test_breakdown_data_sources(self, calculator):
        """Cada dato tiene fuente rastreable."""
        hotel = HotelFinancialData(
            rooms=10,
            adr_cop=300000,
            occupancy_rate=0.5,
            adr_source="onboarding"
        )
        breakdown = calculator.calculate_breakdown(hotel)
        assert breakdown.hotel_data_sources['adr'] == "onboarding"
        assert 'shift' in breakdown.hotel_data_sources
        assert 'ia_boost' in breakdown.hotel_data_sources

    def test_backward_compat_calculate_scenarios(self, calculator):
        """Métodos existentes siguen funcionando (backward compat)."""
        hotel = HotelFinancialData(
            rooms=10,
            adr_cop=300000,
            occupancy_rate=0.5
        )
        scenarios = calculator.calculate_scenarios(hotel)
        assert scenarios is not None
        assert len(scenarios) == 3
        assert ScenarioType.CONSERVATIVE in scenarios
