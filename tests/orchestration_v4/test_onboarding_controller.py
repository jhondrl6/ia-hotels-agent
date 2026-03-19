"""
Tests for the onboarding_controller module.

This module tests the onboarding state machine implementation including:
- OnboardingPhase and OnboardingStatus enums
- OnboardingState dataclass
- OnboardingController initialization and methods
- Phase transitions and state management
- Conflict detection and progress tracking
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from dataclasses import fields
from datetime import datetime

from modules.orchestration_v4.onboarding_controller import (
    OnboardingPhase,
    OnboardingStatus,
    OnboardingState,
    OnboardingController,
)
from modules.orchestration_v4.two_phase_flow import Phase1Result, Phase2Result, HotelInputs


class TestOnboardingPhaseEnum:
    """Tests for OnboardingPhase enum values."""

    def test_onboarding_phase_enum_values(self):
        """Test that OnboardingPhase has all expected enum values."""
        assert OnboardingPhase.INIT.value == "inicio"
        assert OnboardingPhase.PHASE_1_HOOK.value == "fase_1_hook"
        assert OnboardingPhase.PHASE_2_INPUT.value == "fase_2_input"
        assert OnboardingPhase.VALIDATION.value == "validacion"
        assert OnboardingPhase.CALCULATION.value == "calculo"
        assert OnboardingPhase.COMPLETE.value == "completo"
        assert OnboardingPhase.ERROR.value == "error"

    def test_onboarding_phase_enum_members(self):
        """Test that OnboardingPhase has all expected members."""
        expected_members = {
            "INIT",
            "PHASE_1_HOOK",
            "PHASE_2_INPUT",
            "VALIDATION",
            "CALCULATION",
            "COMPLETE",
            "ERROR",
        }
        actual_members = {m.name for m in OnboardingPhase}
        assert actual_members == expected_members


class TestOnboardingStatusEnum:
    """Tests for OnboardingStatus enum values."""

    def test_onboarding_status_enum_values(self):
        """Test that OnboardingStatus has all expected enum values."""
        assert OnboardingStatus.PENDING.value == "pendiente"
        assert OnboardingStatus.IN_PROGRESS.value == "en_progreso"
        assert OnboardingStatus.COMPLETED.value == "completado"
        assert OnboardingStatus.BLOCKED.value == "bloqueado"
        assert OnboardingStatus.ERROR.value == "error"

    def test_onboarding_status_enum_members(self):
        """Test that OnboardingStatus has all expected members."""
        expected_members = {
            "PENDING",
            "IN_PROGRESS",
            "COMPLETED",
            "BLOCKED",
            "ERROR",
        }
        actual_members = {m.name for m in OnboardingStatus}
        assert actual_members == expected_members


class TestOnboardingStateCreation:
    """Tests for OnboardingState dataclass creation."""

    def test_onboarding_state_creation(self):
        """Test that OnboardingState can be created with required fields."""
        state = OnboardingState(
            hotel_id="hotel_test",
            hotel_url="https://www.test.com",
            current_phase=OnboardingPhase.INIT,
            status=OnboardingStatus.PENDING,
        )

        assert state.hotel_id == "hotel_test"
        assert state.hotel_url == "https://www.test.com"
        assert state.current_phase == OnboardingPhase.INIT
        assert state.status == OnboardingStatus.PENDING
        assert state.phase_1_result is None
        assert state.phase_2_result is None
        assert isinstance(state.created_at, datetime)
        assert isinstance(state.updated_at, datetime)
        assert state.errors == []
        assert state.metadata == {}

    def test_onboarding_state_fields(self):
        """Test that OnboardingState has all expected fields."""
        field_names = {f.name for f in fields(OnboardingState)}
        expected_fields = {
            "hotel_id",
            "hotel_url",
            "current_phase",
            "status",
            "phase_1_result",
            "phase_2_result",
            "created_at",
            "updated_at",
            "errors",
            "metadata",
            "progress_percentage",
        }
        assert field_names == expected_fields


class TestOnboardingControllerInitialization:
    """Tests for OnboardingController initialization."""

    def test_controller_initialization(self):
        """Test that OnboardingController initializes correctly."""
        controller = OnboardingController()

        assert controller._orchestrator is not None
        assert controller._states == {}


class TestStartOnboarding:
    """Tests for start_onboarding method."""

    def test_start_onboarding_creates_state_with_phase_1(self):
        """Test that start_onboarding creates state starting with phase 1."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            state = controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
            )

        assert isinstance(state, OnboardingState)
        assert state.hotel_url == "https://www.hoteltest.com"

    def test_start_onboarding_sets_correct_phase_and_status(self):
        """Test that start_onboarding sets correct phase and status."""
        controller = OnboardingController()
        mock_result = Mock(spec=Phase1Result)

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=mock_result
        ):
            state = controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
            )

        assert state.current_phase == OnboardingPhase.PHASE_2_INPUT
        assert state.status == OnboardingStatus.PENDING
        assert state.phase_1_result is not None

    def test_start_onboarding_handles_error(self):
        """Test that start_onboarding handles errors gracefully."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator,
            'phase_1_hook',
            side_effect=Exception("Test error"),
        ):
            state = controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
            )

        assert state.current_phase == OnboardingPhase.ERROR
        assert state.status == OnboardingStatus.ERROR
        assert len(state.errors) > 0
        assert "Phase 1 error" in state.errors[0]


class TestSubmitPhase2:
    """Tests for submit_phase_2 method."""

    def _create_controller_with_state(self):
        """Helper to create a controller with initial state."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
            )

        return controller

    def test_submit_phase_2_updates_state_with_phase_2(self):
        """Test that submit_phase_2 updates state with phase 2 result."""
        controller = self._create_controller_with_state()
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            state = controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        assert state.phase_2_result is not None
        assert state.current_phase == OnboardingPhase.CALCULATION

    def test_submit_phase_2_detects_conflicts(self):
        """Test that submit_phase_2 detects conflicts and blocks."""
        controller = self._create_controller_with_state()
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = ["whatsapp mismatch"]
        mock_phase2_result.has_conflicts = True

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            state = controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        assert state.status == OnboardingStatus.BLOCKED
        assert state.current_phase == OnboardingPhase.VALIDATION

    def test_submit_phase_2_raises_on_invalid_hotel_id(self):
        """Test that submit_phase_2 raises error for invalid hotel_id."""
        controller = self._create_controller_with_state()

        with pytest.raises(ValueError, match="Onboarding not found"):
            controller.submit_phase_2(
                hotel_id="invalid_id",
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

    def test_submit_phase_2_raises_on_wrong_phase(self):
        """Test that submit_phase_2 raises error when in wrong phase."""
        controller = self._create_controller_with_state()
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        # Manually change phase to INIT
        controller._states[hotel_id].current_phase = OnboardingPhase.INIT

        with pytest.raises(ValueError, match="Invalid phase transition"):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )


class TestGetState:
    """Tests for get_state method."""

    def test_get_state_returns_correct_state(self):
        """Test that get_state returns the correct state for a hotel_id."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
            )

        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")
        state = controller.get_state(hotel_id)

        assert state is not None
        assert state.hotel_id == hotel_id
        assert state.hotel_url == "https://www.hoteltest.com"

    def test_get_state_returns_none_for_invalid_id(self):
        """Test that get_state returns None for invalid hotel_id."""
        controller = OnboardingController()
        state = controller.get_state("invalid_id")

        assert state is None


class TestCanProceedToAssets:
    """Tests for can_proceed_to_assets method."""

    def _create_controller_at_phase_2(self):
        """Helper to create a controller at phase 2."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding("https://www.test.com")

        return controller

    def test_can_proceed_to_assets_returns_true_when_valid(self):
        """Test that can_proceed_to_assets returns True when state is valid."""
        controller = self._create_controller_at_phase_2()
        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        assert controller.can_proceed_to_assets(hotel_id) is True

    def test_can_proceed_to_assets_returns_false_when_conflicts(self):
        """Test that can_proceed_to_assets returns False when conflicts exist."""
        controller = self._create_controller_at_phase_2()
        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = ["whatsapp mismatch"]

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        assert controller.can_proceed_to_assets(hotel_id) is False

    def test_can_proceed_to_assets_returns_false_when_error(self):
        """Test that can_proceed_to_assets returns False when status is ERROR."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator,
            'phase_1_hook',
            side_effect=Exception("Test error"),
        ):
            controller.start_onboarding("https://www.test.com")

        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")
        assert controller.can_proceed_to_assets(hotel_id) is False

    def test_can_proceed_to_assets_returns_false_for_invalid_id(self):
        """Test that can_proceed_to_assets returns False for invalid hotel_id."""
        controller = OnboardingController()
        assert controller.can_proceed_to_assets("invalid_id") is False


class TestGetConflictSummary:
    """Tests for get_conflict_summary method."""

    def test_get_conflict_summary_returns_conflicts(self):
        """Test that get_conflict_summary returns list of conflicts."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding("https://www.test.com")

        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = ["whatsapp mismatch", "adr discrepancy"]

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        summary = controller.get_conflict_summary(hotel_id)

        assert isinstance(summary, list)
        assert len(summary) == 2
        assert any("whatsapp" in s for s in summary)
        assert any("adr" in s for s in summary)

    def test_get_conflict_summary_returns_empty_for_no_conflicts(self):
        """Test that get_conflict_summary returns empty list when no conflicts."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding("https://www.clean.com")

        hotel_id = OnboardingController.generate_hotel_id("https://www.clean.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = []

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        summary = controller.get_conflict_summary(hotel_id)
        assert summary == []


class TestGetProgressPercentage:
    """Tests for get_progress_percentage method."""

    def test_get_progress_percentage_returns_30_after_phase_1(self):
        """Test that progress is 30% after completing phase 1."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding("https://www.test.com")

        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")
        progress = controller.get_progress_percentage(hotel_id)
        assert progress == 30

    def test_get_progress_percentage_returns_60_at_calculation(self):
        """Test that progress is 60% at CALCULATION phase."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding("https://www.test.com")

        hotel_id = OnboardingController.generate_hotel_id("https://www.test.com")

        mock_phase2_result = Mock(spec=Phase2Result)
        mock_phase2_result.conflicts_report = []
        mock_phase2_result.has_conflicts = False

        with patch.object(
            controller._orchestrator, 'phase_2_input', return_value=mock_phase2_result
        ):
            controller.submit_phase_2(
                hotel_id=hotel_id,
                inputs=HotelInputs(rooms=20, adr_cop=250000.0),
            )

        progress = controller.get_progress_percentage(hotel_id)
        assert progress == 60

    def test_get_progress_percentage_returns_0_for_invalid_id(self):
        """Test that progress is 0% for invalid hotel_id."""
        controller = OnboardingController()
        progress = controller.get_progress_percentage("invalid_id")
        assert progress == 0


class TestResetOnboarding:
    """Tests for reset_onboarding method."""

    def test_reset_onboarding_resets_to_initial_state(self):
        """Test that reset_onboarding resets state to initial phase."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
                region="bogota",
            )

        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            new_state = controller.reset_onboarding(hotel_id)

        assert new_state.current_phase == OnboardingPhase.PHASE_2_INPUT
        assert new_state.status == OnboardingStatus.PENDING

    def test_reset_onboarding_preserves_metadata(self):
        """Test that reset_onboarding preserves hotel metadata."""
        controller = OnboardingController()

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            controller.start_onboarding(
                hotel_url="https://www.hoteltest.com",
                hotel_name="Hotel Test",
                region="bogota",
            )

        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        with patch.object(
            controller._orchestrator, 'phase_1_hook', return_value=Mock(spec=Phase1Result)
        ):
            new_state = controller.reset_onboarding(hotel_id)

        assert new_state.hotel_url == "https://www.hoteltest.com"
        assert new_state.metadata.get("hotel_name") == "Hotel Test"
        assert new_state.metadata.get("region") == "bogota"

    def test_reset_onboarding_raises_for_invalid_id(self):
        """Test that reset_onboarding raises error for invalid hotel_id."""
        controller = OnboardingController()

        with pytest.raises(ValueError, match="Onboarding not found"):
            controller.reset_onboarding("invalid_id")


class TestGenerateHotelId:
    """Tests for generate_hotel_id static method."""

    def test_generate_hotel_id_creates_valid_id_from_url(self):
        """Test that generate_hotel_id creates valid ID from URL."""
        hotel_id = OnboardingController.generate_hotel_id("https://www.hoteltest.com")

        assert hotel_id.startswith("hotel_")
        assert "hoteltest" in hotel_id

    def test_generate_hotel_id_removes_protocol(self):
        """Test that generate_hotel_id removes https:// and http://."""
        https_id = OnboardingController.generate_hotel_id("https://www.test.com")
        http_id = OnboardingController.generate_hotel_id("http://www.test.com")

        assert "https://" not in https_id
        assert "http://" not in http_id
        assert https_id == http_id

    def test_generate_hotel_id_removes_www(self):
        """Test that generate_hotel_id removes www."""
        hotel_id = OnboardingController.generate_hotel_id("https://www.hotel.com")

        assert "www." not in hotel_id
        assert hotel_id == "hotel_hotel.com"

    def test_generate_hotel_id_replaces_special_chars(self):
        """Test that generate_hotel_id replaces special characters with underscores."""
        hotel_id = OnboardingController.generate_hotel_id("https://www.hotel.com/path?a=1&b=2")

        assert "/" not in hotel_id
        assert "?" not in hotel_id
        assert "&" not in hotel_id
        assert "=" not in hotel_id


class TestFormatStatusReport:
    """Tests for format_status_report static method."""

    @pytest.fixture
    def sample_state(self):
        """Provide a sample OnboardingState."""
        return OnboardingState(
            hotel_id="hotel_test",
            hotel_url="https://www.test.com",
            current_phase=OnboardingPhase.PHASE_2_INPUT,
            status=OnboardingStatus.PENDING,
        )

    def test_format_status_report_includes_phase_and_status(self, sample_state):
        """Test that format_status_report includes phase and status."""
        report = OnboardingController.format_status_report(sample_state)

        assert "ONBOARDING STATUS REPORT" in report
        assert "hotel_test" in report
        assert "https://www.test.com" in report
        assert "fase_2_input" in report
        assert "pendiente" in report

    def test_format_status_report_includes_timestamps(self, sample_state):
        """Test that format_status_report includes created/updated timestamps."""
        report = OnboardingController.format_status_report(sample_state)

        assert "Created:" in report
        assert "Updated:" in report

    def test_format_status_report_shows_phase_status(self, sample_state):
        """Test that format_status_report shows phase 1 and phase 2 status."""
        report = OnboardingController.format_status_report(sample_state)

        assert "Phase 1:" in report
        assert "Phase 2:" in report

    def test_format_status_report_includes_next_action(self, sample_state):
        """Test that format_status_report includes next action."""
        report = OnboardingController.format_status_report(sample_state)

        assert "Next Action:" in report

    def test_format_status_report_includes_errors(self, sample_state):
        """Test that format_status_report includes errors when present."""
        sample_state.errors = ["Error 1", "Error 2"]
        report = OnboardingController.format_status_report(sample_state)

        assert "ERRORS:" in report
        assert "Error 1" in report
        assert "Error 2" in report
