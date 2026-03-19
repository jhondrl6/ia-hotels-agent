"""
Tests for the two_phase_flow module.

This module tests the two-phase user flow implementation including:
- Phase1Result and Phase2Result dataclasses
- HotelInputs dataclass with defaults
- TwoPhaseOrchestrator initialization and methods
- Form generation and display formatting
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import fields

from modules.orchestration_v4.two_phase_flow import (
    Phase1Result,
    Phase2Result,
    HotelInputs,
    TwoPhaseOrchestrator,
)
from modules.financial_engine.scenario_calculator import HotelFinancialData


class TestPhase1Result:
    """Tests for Phase1Result dataclass creation and fields."""

    def test_phase1_result_creation(self):
        """Test that Phase1Result can be created with all required fields."""
        result = Phase1Result(
            hotel_name="Hotel Test",
            hotel_url="https://www.hoteltest.com",
            region="default",
            hook_message="Test hook message",
            loss_range_min=500000.0,
            loss_range_max=2000000.0,
            next_step="complete_phase_2",
            confidence_level="low",
            disclaimer="Test disclaimer",
        )

        assert result.hotel_name == "Hotel Test"
        assert result.hotel_url == "https://www.hoteltest.com"
        assert result.region == "default"
        assert result.hook_message == "Test hook message"
        assert result.loss_range_min == 500000.0
        assert result.loss_range_max == 2000000.0
        assert result.next_step == "complete_phase_2"
        assert result.confidence_level == "low"
        assert result.disclaimer == "Test disclaimer"
        assert result.requires_user_input is True

    def test_phase1_result_fields(self):
        """Test that Phase1Result has all expected fields."""
        field_names = {f.name for f in fields(Phase1Result)}
        expected_fields = {
            "hotel_name",
            "hotel_url",
            "region",
            "hook_message",
            "loss_range_min",
            "loss_range_max",
            "next_step",
            "confidence_level",
            "disclaimer",
            "requires_user_input",
        }
        assert field_names == expected_fields


class TestPhase2Result:
    """Tests for Phase2Result dataclass creation and fields."""

    def test_phase2_result_creation(self):
        """Test that Phase2Result can be created with all required fields."""
        hotel_data = HotelFinancialData(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.65,
        )

        result = Phase2Result(
            hotel_data=hotel_data,
            validated_fields={"rooms": {"value": 20}},
            confidence_scores={"rooms": 0.95},
            has_conflicts=False,
            conflicts_report=[],
            can_proceed=True,
        )

        assert result.hotel_data == hotel_data
        assert result.validated_fields == {"rooms": {"value": 20}}
        assert result.confidence_scores == {"rooms": 0.95}
        assert result.has_conflicts is False
        assert result.conflicts_report == []
        assert result.can_proceed is True
        assert result.scenarios is None

    def test_phase2_result_with_scenarios(self):
        """Test Phase2Result with scenarios included."""
        hotel_data = HotelFinancialData(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.65,
        )

        scenarios = {
            "conservative": {
                "monthly_loss_cop": 1000000.0,
                "probability": 0.7,
            }
        }

        result = Phase2Result(
            hotel_data=hotel_data,
            validated_fields={},
            confidence_scores={},
            has_conflicts=False,
            conflicts_report=[],
            can_proceed=True,
            scenarios=scenarios,
        )

        assert result.scenarios == scenarios

    def test_phase2_result_fields(self):
        """Test that Phase2Result has all expected fields."""
        field_names = {f.name for f in fields(Phase2Result)}
        expected_fields = {
            "hotel_data",
            "validated_fields",
            "confidence_scores",
            "has_conflicts",
            "conflicts_report",
            "can_proceed",
            "scenarios",
        }
        assert field_names == expected_fields


class TestHotelInputs:
    """Tests for HotelInputs dataclass creation with defaults."""

    def test_hotel_inputs_creation_with_defaults(self):
        """Test that HotelInputs can be created with all None defaults."""
        inputs = HotelInputs()

        assert inputs.rooms is None
        assert inputs.adr_cop is None
        assert inputs.occupancy_rate is None
        assert inputs.ota_presence == []
        assert inputs.direct_channel_percentage is None
        assert inputs.whatsapp_number is None

    def test_hotel_inputs_creation_with_values(self):
        """Test that HotelInputs can be created with specific values."""
        inputs = HotelInputs(
            rooms=25,
            adr_cop=300000.0,
            occupancy_rate=0.70,
            ota_presence=["booking", "expedia"],
            direct_channel_percentage=0.20,
            whatsapp_number="+57 300 123 4567",
        )

        assert inputs.rooms == 25
        assert inputs.adr_cop == 300000.0
        assert inputs.occupancy_rate == 0.70
        assert inputs.ota_presence == ["booking", "expedia"]
        assert inputs.direct_channel_percentage == 0.20
        assert inputs.whatsapp_number == "+57 300 123 4567"

    def test_hotel_inputs_partial_values(self):
        """Test that HotelInputs can be created with partial values."""
        inputs = HotelInputs(rooms=30, adr_cop=200000.0)

        assert inputs.rooms == 30
        assert inputs.adr_cop == 200000.0
        assert inputs.occupancy_rate is None
        assert inputs.ota_presence == []


class TestTwoPhaseOrchestratorInitialization:
    """Tests for TwoPhaseOrchestrator initialization."""

    def test_orchestrator_initialization_default(self):
        """Test that orchestrator initializes with default values."""
        orchestrator = TwoPhaseOrchestrator()

        assert orchestrator.plan_maestro_data == {}
        assert orchestrator.scenario_calculator is not None
        assert orchestrator.cross_validator is not None

    def test_orchestrator_initialization_with_data(self):
        """Test that orchestrator initializes with provided plan maestro data."""
        plan_data = {"regions": {"default": {"avg_adr": 250000.0}}}
        orchestrator = TwoPhaseOrchestrator(plan_maestro_data=plan_data)

        assert orchestrator.plan_maestro_data == plan_data


class TestPhase1Hook:
    """Tests for phase_1_hook method."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a TwoPhaseOrchestrator instance."""
        return TwoPhaseOrchestrator()

    def test_phase_1_hook_returns_phase1_result(self, orchestrator):
        """Test that phase_1_hook returns a Phase1Result instance."""
        result = orchestrator.phase_1_hook(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="default",
        )

        assert isinstance(result, Phase1Result)

    def test_phase_1_hook_has_correct_confidence_level(self, orchestrator):
        """Test that phase_1_hook returns result with confidence level 'low'."""
        result = orchestrator.phase_1_hook(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="default",
        )

        assert result.confidence_level == "low"

    def test_phase_1_hook_includes_disclaimer(self, orchestrator):
        """Test that phase_1_hook returns result with disclaimer."""
        result = orchestrator.phase_1_hook(
            hotel_url="https://www.hoteltest.com",
            hotel_name="Hotel Test",
            region="default",
        )

        assert result.disclaimer is not None
        assert len(result.disclaimer) > 0
        assert "benchmarks" in result.disclaimer.lower()

    def test_phase_1_hook_extracts_name_from_url(self, orchestrator):
        """Test that phase_1_hook extracts hotel name from URL if not provided."""
        result = orchestrator.phase_1_hook(
            hotel_url="https://www.hotel-ejemplo.com",
        )

        assert result.hotel_name == "Hotel Ejemplo"

    def test_phase_1_hook_uses_provided_name(self, orchestrator):
        """Test that phase_1_hook uses provided hotel name."""
        result = orchestrator.phase_1_hook(
            hotel_url="https://www.hotel-ejemplo.com",
            hotel_name="Custom Hotel Name",
        )

        assert result.hotel_name == "Custom Hotel Name"


class TestCalculateHookRange:
    """Tests for _calculate_hook_range method."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a TwoPhaseOrchestrator instance."""
        return TwoPhaseOrchestrator()

    def test_calculate_hook_range_returns_tuple(self, orchestrator):
        """Test that _calculate_hook_range returns a tuple."""
        result = orchestrator._calculate_hook_range("default")

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_calculate_hook_range_returns_positive_values(self, orchestrator):
        """Test that _calculate_hook_range returns positive min and max."""
        loss_min, loss_max = orchestrator._calculate_hook_range("default")

        assert loss_min > 0
        assert loss_max > 0
        assert loss_min < loss_max


class TestPhase2Input:
    """Tests for phase_2_input method."""

    @pytest.fixture
    def phase1_result(self):
        """Provide a sample Phase1Result."""
        return Phase1Result(
            hotel_name="Hotel Test",
            hotel_url="https://www.hoteltest.com",
            region="default",
            hook_message="Test message",
            loss_range_min=500000.0,
            loss_range_max=2000000.0,
            next_step="complete_phase_2",
            confidence_level="low",
            disclaimer="Test disclaimer",
        )

    def test_phase_2_input_validates_inputs(self, phase1_result):
        """Test that phase_2_input validates user inputs."""
        # Create a fresh orchestrator to avoid cross-test state
        orchestrator = TwoPhaseOrchestrator()
        user_inputs = HotelInputs(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.65,
        )

        result = orchestrator.phase_2_input(phase1_result, user_inputs)

        assert isinstance(result, Phase2Result)
        assert "rooms" in result.validated_fields
        assert "adr" in result.validated_fields

    def test_phase_2_input_detects_conflicts(self, phase1_result):
        """Test that phase_2_input detects conflicts between sources."""
        # Create a fresh orchestrator to avoid cross-test state
        orchestrator = TwoPhaseOrchestrator()
        user_inputs = HotelInputs(
            rooms=20,
            adr_cop=250000.0,
            whatsapp_number="+57 300 123 4567",
        )

        scraped_data = {"whatsapp": "+57 300 999 8888"}
        gbp_data = {"phone": "+57 300 111 2222"}

        result = orchestrator.phase_2_input(
            phase1_result, user_inputs, scraped_data, gbp_data
        )

        assert result.has_conflicts is True
        assert len(result.conflicts_report) > 0

    def test_phase_2_input_calculates_scenarios_when_no_conflicts(self, phase1_result):
        """Test that phase_2_input calculates scenarios when no conflicts exist."""
        # Create a fresh orchestrator to avoid cross-test state
        orchestrator = TwoPhaseOrchestrator()
        user_inputs = HotelInputs(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.65,
        )

        result = orchestrator.phase_2_input(phase1_result, user_inputs)

        assert result.can_proceed is True
        assert result.scenarios is not None
        assert isinstance(result.scenarios, dict)

    def test_phase_2_input_cannot_proceed_without_required_fields(self, phase1_result):
        """Test that phase_2_input cannot proceed without rooms and ADR."""
        # Create a fresh orchestrator to avoid cross-test state
        orchestrator = TwoPhaseOrchestrator()
        user_inputs = HotelInputs(occupancy_rate=0.65)

        result = orchestrator.phase_2_input(phase1_result, user_inputs)

        assert result.can_proceed is False
        assert result.scenarios is None


class TestValidateAllInputs:
    """Tests for _validate_all_inputs method."""

    def test_validate_all_inputs_returns_validated_fields(self):
        """Test that _validate_all_inputs returns dictionary of validated fields."""
        orchestrator = TwoPhaseOrchestrator()
        user_inputs = HotelInputs(
            rooms=20,
            adr_cop=250000.0,
            occupancy_rate=0.65,
            direct_channel_percentage=0.20,
            whatsapp_number="+57 300 123 4567",
        )

        result = orchestrator._validate_all_inputs(user_inputs, {}, {})

        assert isinstance(result, dict)
        assert "rooms" in result
        assert "adr" in result
        assert "occupancy_rate" in result
        assert "direct_channel_percentage" in result
        assert "whatsapp" in result


class TestGetPhase1Form:
    """Tests for get_phase_1_form method."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a TwoPhaseOrchestrator instance."""
        return TwoPhaseOrchestrator()

    def test_get_phase_1_form_returns_url_field(self, orchestrator):
        """Test that get_phase_1_form returns form with URL field."""
        form = orchestrator.get_phase_1_form()

        assert isinstance(form, dict)
        assert "fields" in form

        url_field = next((f for f in form["fields"] if f["name"] == "hotel_url"), None)
        assert url_field is not None
        assert url_field["type"] == "url"
        assert url_field["required"] is True

    def test_get_phase_1_form_structure(self, orchestrator):
        """Test that get_phase_1_form returns properly structured form."""
        form = orchestrator.get_phase_1_form()

        assert form["form_id"] == "phase_1_hook"
        assert "title" in form
        assert "description" in form
        assert "submit_label" in form
        assert "privacy_note" in form


class TestGetPhase2Form:
    """Tests for get_phase_2_form method."""

    @pytest.fixture
    def orchestrator(self):
        """Provide a TwoPhaseOrchestrator instance."""
        return TwoPhaseOrchestrator()

    def test_get_phase_2_form_returns_all_hotel_data_fields(self, orchestrator):
        """Test that get_phase_2_form returns form with all hotel data fields."""
        form = orchestrator.get_phase_2_form()

        assert isinstance(form, dict)
        assert "fields" in form

        field_names = {f["name"] for f in form["fields"]}
        expected_fields = {
            "rooms",
            "adr_cop",
            "occupancy_rate",
            "ota_presence",
            "direct_channel_percentage",
            "whatsapp_number",
        }
        assert field_names == expected_fields

    def test_get_phase_2_form_field_types(self, orchestrator):
        """Test that get_phase_2_form fields have correct types."""
        form = orchestrator.get_phase_2_form()

        fields_by_name = {f["name"]: f for f in form["fields"]}

        assert fields_by_name["rooms"]["type"] == "number"
        assert fields_by_name["adr_cop"]["type"] == "currency"
        assert fields_by_name["occupancy_rate"]["type"] == "percentage"
        assert fields_by_name["ota_presence"]["type"] == "multiselect"
        assert fields_by_name["direct_channel_percentage"]["type"] == "percentage"
        assert fields_by_name["whatsapp_number"]["type"] == "tel"


class TestFormatHookForDisplay:
    """Tests for format_hook_for_display static method."""

    @pytest.fixture
    def sample_result(self):
        """Provide a sample Phase1Result."""
        return Phase1Result(
            hotel_name="Hotel Ejemplo",
            hotel_url="https://www.hotelejemplo.com",
            region="default",
            hook_message="Test hook message",
            loss_range_min=1000000.0,
            loss_range_max=5000000.0,
            next_step="complete_phase_2",
            confidence_level="low",
            disclaimer="Esta estimacion inicial se basa en benchmarks.",
        )

    def test_format_hook_for_display_returns_markdown(self, sample_result):
        """Test that format_hook_for_display returns markdown string."""
        markdown = TwoPhaseOrchestrator.format_hook_for_display(sample_result)

        assert isinstance(markdown, str)
        assert "## Hotel Ejemplo" in markdown
        assert "**Minimo" in markdown or "$1.000.000" in markdown

    def test_format_hook_includes_disclaimer(self, sample_result):
        """Test that formatted markdown includes disclaimer."""
        markdown = TwoPhaseOrchestrator.format_hook_for_display(sample_result)

        assert "Esta estimacion inicial se basa en benchmarks" in markdown

    def test_format_hook_includes_loss_range(self, sample_result):
        """Test that formatted markdown includes loss range."""
        markdown = TwoPhaseOrchestrator.format_hook_for_display(sample_result)

        assert "1.000.000" in markdown or "1000000" in markdown
        assert "5.000.000" in markdown or "5000000" in markdown
