"""
Test module for formula_transparency.py

Comprehensive tests for the FormulaTransparency class and related dataclasses,
covering calculation explanations and formatting utilities.
"""

import pytest
from modules.financial_engine.formula_transparency import (
    CalculationStep,
    TransparentCalculation,
    FormulaTransparency,
    format_cop,
    format_percentage,
)


class TestCalculationStepDataclass:
    """Test cases for CalculationStep dataclass."""

    def test_calculation_step_creation(self):
        """Test CalculationStep dataclass creation with all fields."""
        step = CalculationStep(
            step_number=1,
            description="Test calculation step",
            formula="a + b = c",
            inputs={"a": 10, "b": 20},
            result=30,
            explanation="Adding two numbers",
        )

        assert step.step_number == 1
        assert step.description == "Test calculation step"
        assert step.formula == "a + b = c"
        assert step.inputs == {"a": 10, "b": 20}
        assert step.result == 30
        assert step.explanation == "Adding two numbers"

    def test_calculation_step_with_various_types(self):
        """Test CalculationStep with various input and result types."""
        step = CalculationStep(
            step_number=2,
            description="Complex calculation",
            formula="revenue * rate = commission",
            inputs={
                "revenue": 1000000.0,
                "rate": 0.15,
                "formatted_rate": "15%"
            },
            result=150000.0,
            explanation="Calculate commission",
        )

        assert isinstance(step.inputs["revenue"], float)
        assert isinstance(step.inputs["rate"], float)
        assert isinstance(step.result, float)


class TestTransparentCalculationDataclass:
    """Test cases for TransparentCalculation dataclass."""

    def test_transparent_calculation_creation(self):
        """Test TransparentCalculation dataclass creation."""
        steps = [
            CalculationStep(
                step_number=1,
                description="Step 1",
                formula="a + b",
                inputs={"a": 1, "b": 2},
                result=3,
                explanation="Add",
            )
        ]

        calc = TransparentCalculation(
            title="Test Calculation",
            steps=steps,
            final_result=100.0,
        )

        assert calc.title == "Test Calculation"
        assert len(calc.steps) == 1
        assert calc.final_result == 100.0
        assert calc.assumptions == []
        assert calc.limitations == []

    def test_transparent_calculation_with_assumptions_and_limitations(self):
        """Test TransparentCalculation with assumptions and limitations."""
        calc = TransparentCalculation(
            title="Revenue Calculation",
            steps=[],
            final_result=1000000.0,
            assumptions=[
                "30 days per month",
                "Constant occupancy",
            ],
            limitations=[
                "Seasonal variations not included",
                "External factors excluded",
            ],
        )

        assert len(calc.assumptions) == 2
        assert len(calc.limitations) == 2
        assert "30 days" in calc.assumptions[0]


class TestFormulaTransparencyInitialization:
    """Test cases for FormulaTransparency initialization."""

    def test_formula_transparency_initialization(self):
        """Test FormulaTransparency initializes correctly."""
        ft = FormulaTransparency()

        assert isinstance(ft, FormulaTransparency)

    def test_formula_transparency_has_required_methods(self):
        """Test that initialized FormulaTransparency has required methods."""
        ft = FormulaTransparency()

        assert hasattr(ft, 'explain_revenue_calculation')
        assert hasattr(ft, 'explain_ota_commission_loss')
        assert hasattr(ft, 'explain_direct_channel_savings')
        assert hasattr(ft, 'explain_invisibility_penalty')
        assert hasattr(ft, 'format_for_report')
        assert hasattr(ft, 'format_for_hotelier')


class TestExplainRevenueCalculation:
    """Test cases for explain_revenue_calculation method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    def test_explain_revenue_calculation_returns_transparent_calculation(self, formula_transparency):
        """Test that explain_revenue_calculation returns a TransparentCalculation."""
        result = formula_transparency.explain_revenue_calculation(
            rooms=50,
            adr=180000.0,
            occupancy=0.70,
        )

        assert isinstance(result, TransparentCalculation)

    def test_explain_revenue_calculation_has_correct_steps(self, formula_transparency):
        """Test that revenue calculation has correct number of steps."""
        result = formula_transparency.explain_revenue_calculation(
            rooms=50,
            adr=180000.0,
            occupancy=0.70,
        )

        assert len(result.steps) == 3

        # Step 1: Max daily revenue
        assert result.steps[0].step_number == 1
        assert "máximo" in result.steps[0].description.lower() or "max" in result.steps[0].description.lower()

        # Step 2: Apply occupancy
        assert result.steps[1].step_number == 2
        assert "ocupación" in result.steps[1].description.lower()

        # Step 3: Monthly projection
        assert result.steps[2].step_number == 3
        assert "mensual" in result.steps[2].description.lower()

    def test_explain_revenue_calculation_correct_math(self, formula_transparency):
        """Test that revenue calculation has correct math.
        
        50 rooms × $180,000 = $9,000,000 max daily
        $9,000,000 × 0.70 = $6,300,000 actual daily
        $6,300,000 × 30 = $189,000,000 monthly
        """
        result = formula_transparency.explain_revenue_calculation(
            rooms=50,
            adr=180000.0,
            occupancy=0.70,
        )

        # Step 1 result: 50 × 180000 = 9,000,000
        assert result.steps[0].result == 50 * 180000.0

        # Step 2 result: 9,000,000 × 0.70 = 6,300,000
        assert result.steps[1].result == 50 * 180000.0 * 0.70

        # Step 3 result: 6,300,000 × 30 = 189,000,000
        assert result.steps[2].result == 50 * 180000.0 * 0.70 * 30

        # Final result should match step 3
        assert result.final_result == 50 * 180000.0 * 0.70 * 30

    def test_explain_revenue_calculation_has_assumptions(self, formula_transparency):
        """Test that revenue calculation includes assumptions."""
        result = formula_transparency.explain_revenue_calculation(
            rooms=50,
            adr=180000.0,
            occupancy=0.70,
        )

        assert len(result.assumptions) >= 3
        assert any("30" in assumption for assumption in result.assumptions)

    def test_explain_revenue_calculation_has_limitations(self, formula_transparency):
        """Test that revenue calculation includes limitations."""
        result = formula_transparency.explain_revenue_calculation(
            rooms=50,
            adr=180000.0,
            occupancy=0.70,
        )

        assert len(result.limitations) >= 3


class TestExplainOtaCommissionLoss:
    """Test cases for explain_ota_commission_loss method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    def test_explain_ota_commission_loss_returns_transparent_calculation(self, formula_transparency):
        """Test that explain_ota_commission_loss returns a TransparentCalculation."""
        result = formula_transparency.explain_ota_commission_loss(
            monthly_revenue=100000000.0,
            ota_percentage=0.70,
            commission_rate=0.18,
        )

        assert isinstance(result, TransparentCalculation)

    def test_explain_ota_commission_loss_shows_correct_formula(self, formula_transparency):
        """Test that OTA commission loss shows correct formula."""
        result = formula_transparency.explain_ota_commission_loss(
            monthly_revenue=100000000.0,
            ota_percentage=0.70,
            commission_rate=0.18,
        )

        # Should have steps showing the formula progression
        assert len(result.steps) == 3

        # Step 1: OTA revenue calculation
        assert "ingreso_ota" in result.steps[0].formula or "ota" in result.steps[0].formula.lower()

        # Step 2: Commission calculation
        assert "comisión" in result.steps[1].formula.lower()

        # Step 3: Annual projection
        assert "12" in result.steps[2].formula or "anual" in result.steps[2].formula.lower()

    def test_explain_ota_commission_loss_correct_calculation(self, formula_transparency):
        """Test OTA commission loss calculation is correct.
        
        $100,000,000 × 0.70 = $70,000,000 OTA revenue
        $70,000,000 × 0.18 = $12,600,000 monthly commission
        $12,600,000 × 12 = $151,200,000 annual loss
        """
        result = formula_transparency.explain_ota_commission_loss(
            monthly_revenue=100000000.0,
            ota_percentage=0.70,
            commission_rate=0.18,
        )

        expected_ota_revenue = 100000000.0 * 0.70  # 70,000,000
        expected_monthly_commission = expected_ota_revenue * 0.18  # 12,600,000
        expected_annual_loss = expected_monthly_commission * 12  # 151,200,000

        assert result.steps[0].result == expected_ota_revenue
        assert result.steps[1].result == expected_monthly_commission
        assert result.steps[2].result == expected_annual_loss
        assert result.final_result == expected_annual_loss


class TestExplainDirectChannelSavings:
    """Test cases for explain_direct_channel_savings method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    def test_explain_direct_channel_savings_returns_transparent_calculation(self, formula_transparency):
        """Test that explain_direct_channel_savings returns a TransparentCalculation."""
        result = formula_transparency.explain_direct_channel_savings(
            monthly_revenue=100000000.0,
            current_direct_pct=0.30,
            target_direct_pct=0.50,
            commission_rate=0.18,
        )

        assert isinstance(result, TransparentCalculation)

    def test_explain_direct_channel_savings_calculates_correctly(self, formula_transparency):
        """Test direct channel savings calculation is correct.
        
        Current: 30% direct = 70% OTA
        Target: 50% direct = 50% OTA
        
        $100,000,000 × 0.70 = $70,000,000 current OTA revenue
        $100,000,000 × 0.50 = $50,000,000 target OTA revenue
        Reduction: $70,000,000 - $50,000,000 = $20,000,000
        Savings: $20,000,000 × 0.18 = $3,600,000 monthly
        Annual: $3,600,000 × 12 = $43,200,000
        """
        result = formula_transparency.explain_direct_channel_savings(
            monthly_revenue=100000000.0,
            current_direct_pct=0.30,
            target_direct_pct=0.50,
            commission_rate=0.18,
        )

        current_ota_pct = 1 - 0.30  # 0.70
        target_ota_pct = 1 - 0.50  # 0.50

        expected_current_ota_revenue = 100000000.0 * current_ota_pct  # 70,000,000
        expected_target_ota_revenue = 100000000.0 * target_ota_pct  # 50,000,000
        expected_reduction = expected_current_ota_revenue - expected_target_ota_revenue  # 20,000,000
        expected_monthly_savings = expected_reduction * 0.18  # 3,600,000
        expected_annual_savings = expected_monthly_savings * 12  # 43,200,000

        assert result.steps[0].result == expected_current_ota_revenue
        assert result.steps[1].result == expected_target_ota_revenue
        assert result.steps[2].result == expected_monthly_savings
        assert result.steps[3].result == expected_annual_savings
        assert result.final_result == expected_annual_savings

    def test_explain_direct_channel_savings_has_four_steps(self, formula_transparency):
        """Test that direct channel savings has 4 calculation steps."""
        result = formula_transparency.explain_direct_channel_savings(
            monthly_revenue=100000000.0,
            current_direct_pct=0.30,
            target_direct_pct=0.50,
            commission_rate=0.18,
        )

        assert len(result.steps) == 4


class TestExplainInvisibilityPenalty:
    """Test cases for explain_invisibility_penalty method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    def test_explain_invisibility_penalty_returns_transparent_calculation(self, formula_transparency):
        """Test that explain_invisibility_penalty returns a TransparentCalculation."""
        result = formula_transparency.explain_invisibility_penalty(
            monthly_revenue=100000000.0,
        )

        assert isinstance(result, TransparentCalculation)

    def test_explain_invisibility_penalty_uses_5_percent_default(self, formula_transparency):
        """Test that invisibility penalty uses 5% default when not specified."""
        result = formula_transparency.explain_invisibility_penalty(
            monthly_revenue=100000000.0,
        )

        # Check that 5% was used in calculation
        expected_monthly_penalty = 100000000.0 * 0.05  # 5,000,000
        expected_annual_penalty = expected_monthly_penalty * 12  # 60,000,000

        assert result.steps[0].result == expected_monthly_penalty
        assert result.steps[1].result == expected_annual_penalty
        assert result.final_result == expected_annual_penalty

    def test_explain_invisibility_penalty_accepts_custom_percentage(self, formula_transparency):
        """Test that invisibility penalty accepts custom percentage."""
        result = formula_transparency.explain_invisibility_penalty(
            monthly_revenue=100000000.0,
            estimated_penalty_pct=0.10,  # 10%
        )

        expected_monthly_penalty = 100000000.0 * 0.10  # 10,000,000
        expected_annual_penalty = expected_monthly_penalty * 12  # 120,000,000

        assert result.steps[0].result == expected_monthly_penalty
        assert result.steps[1].result == expected_annual_penalty
        assert result.final_result == expected_annual_penalty

    def test_explain_invisibility_penalty_has_three_steps(self, formula_transparency):
        """Test that invisibility penalty has 3 calculation steps."""
        result = formula_transparency.explain_invisibility_penalty(
            monthly_revenue=100000000.0,
        )

        assert len(result.steps) == 3


class TestFormatForReport:
    """Test cases for format_for_report method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    @pytest.fixture
    def sample_calculation(self):
        """Provide a sample TransparentCalculation."""
        steps = [
            CalculationStep(
                step_number=1,
                description="Test Step",
                formula="a × b = c",
                inputs={"a": 100, "b": 0.5},
                result=50,
                explanation="Test explanation",
            )
        ]
        return TransparentCalculation(
            title="Test Calculation",
            steps=steps,
            final_result=1000.0,
            assumptions=["Test assumption"],
            limitations=["Test limitation"],
        )

    def test_format_for_report_includes_all_steps(self, formula_transparency, sample_calculation):
        """Test that format_for_report includes all calculation steps."""
        formatted = formula_transparency.format_for_report(sample_calculation)

        assert "## Test Calculation" in formatted
        assert "### Desglose del Cálculo" in formatted
        assert "Paso 1" in formatted
        assert "Test Step" in formatted

    def test_format_for_report_includes_formulas(self, formula_transparency, sample_calculation):
        """Test that format_for_report includes formulas."""
        formatted = formula_transparency.format_for_report(sample_calculation)

        assert "Fórmula:" in formatted
        assert "a × b = c" in formatted

    def test_format_for_report_includes_result(self, formula_transparency, sample_calculation):
        """Test that format_for_report includes final result."""
        formatted = formula_transparency.format_for_report(sample_calculation)

        assert "### Resultado Final" in formatted
        assert "1000" in formatted

    def test_format_for_report_includes_assumptions(self, formula_transparency, sample_calculation):
        """Test that format_for_report includes assumptions."""
        formatted = formula_transparency.format_for_report(sample_calculation)

        assert "### Supuestos" in formatted
        assert "Test assumption" in formatted

    def test_format_for_report_includes_limitations(self, formula_transparency, sample_calculation):
        """Test that format_for_report includes limitations."""
        formatted = formula_transparency.format_for_report(sample_calculation)

        assert "### Limitaciones" in formatted
        assert "Test limitation" in formatted


class TestFormatForHotelier:
    """Test cases for format_for_hotelier method."""

    @pytest.fixture
    def formula_transparency(self):
        """Provide a FormulaTransparency instance."""
        return FormulaTransparency()

    @pytest.fixture
    def sample_calculation(self):
        """Provide a sample TransparentCalculation."""
        steps = [
            CalculationStep(
                step_number=1,
                description="Test Step",
                formula="a × b = c",
                inputs={"a": 100, "b": 0.5},
                result=50,
                explanation="Esta es la explicación en términos simples",
            )
        ]
        return TransparentCalculation(
            title="Cálculo de Prueba",
            steps=steps,
            final_result=1000.0,
            assumptions=[],
            limitations=["Limitación de prueba"],
        )

    def test_format_for_hotelier_uses_plain_language(self, formula_transparency, sample_calculation):
        """Test that format_for_hotelier uses plain language for hoteliers."""
        formatted = formula_transparency.format_for_hotelier(sample_calculation)

        assert "¿Qué significa esto para su hotel?" in formatted
        assert "términos simples" in formatted.lower() or "simples" in formatted

    def test_format_for_hotelier_includes_explanations(self, formula_transparency, sample_calculation):
        """Test that format_for_hotelier includes step explanations."""
        formatted = formula_transparency.format_for_hotelier(sample_calculation)

        assert "Esta es la explicación en términos simples" in formatted

    def test_format_for_hotelier_includes_final_result(self, formula_transparency, sample_calculation):
        """Test that format_for_hotelier emphasizes final result."""
        formatted = formula_transparency.format_for_hotelier(sample_calculation)

        assert "RESULTADO FINAL" in formatted
        assert "1000" in formatted

    def test_format_for_hotelier_has_context_aware_message(self, formula_transparency):
        """Test that format_for_hotelier provides context-aware message."""
        # Test with commission/loss calculation
        loss_calc = TransparentCalculation(
            title="Pérdida por Comisiones",
            steps=[],
            final_result=50000.0,
            limitations=["Test"],
        )
        formatted = formula_transparency.format_for_hotelier(loss_calc)

        assert "dinero que su hotel está dejando de ganar" in formatted.lower()

    def test_format_for_hotelier_includes_limitations(self, formula_transparency, sample_calculation):
        """Test that format_for_hotelier includes top limitations."""
        formatted = formula_transparency.format_for_hotelier(sample_calculation)

        assert "Puntos importantes a considerar:" in formatted
        assert "Limitación de prueba" in formatted


class TestFormatCop:
    """Test cases for format_cop function."""

    def test_format_cop_basic(self):
        """Test format_cop with basic amount."""
        assert format_cop(2100000) == "$2.100.000"

    def test_format_cop_with_thousands(self):
        """Test format_cop with amount in thousands."""
        assert format_cop(850500) == "$850.500"

    def test_format_cop_zero(self):
        """Test format_cop with zero."""
        assert format_cop(0) == "$0"

    def test_format_cop_none(self):
        """Test format_cop with None."""
        assert format_cop(None) == "$0"

    def test_format_cop_large_number(self):
        """Test format_cop with large number."""
        assert format_cop(100000000) == "$100.000.000"

    def test_format_cop_rounds_to_integer(self):
        """Test format_cop rounds to nearest integer."""
        assert format_cop(1500.7) == "$1.501"
        assert format_cop(1500.3) == "$1.500"


class TestFormatPercentage:
    """Test cases for format_percentage function."""

    def test_format_percentage_basic(self):
        """Test format_percentage with basic values."""
        assert format_percentage(0.15) == "15%"
        assert format_percentage(0.70) == "70%"

    def test_format_percentage_with_decimal(self):
        """Test format_percentage with decimal values."""
        assert format_percentage(0.185) == "18.5%"
        assert format_percentage(0.333) == "33.3%"

    def test_format_percentage_zero(self):
        """Test format_percentage with zero."""
        assert format_percentage(0) == "0%"

    def test_format_percentage_none(self):
        """Test format_percentage with None."""
        assert format_percentage(None) == "0%"

    def test_format_percentage_one_hundred(self):
        """Test format_percentage with 100%."""
        assert format_percentage(1.0) == "100%"

    def test_format_percentage_whole_number_no_decimal(self):
        """Test format_percentage doesn't show decimals for whole numbers."""
        assert format_percentage(0.5) == "50%"
        assert ".0%" not in format_percentage(0.5)
