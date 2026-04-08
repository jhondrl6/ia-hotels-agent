"""
Onboarding Controller - State Machine for Hotel Onboarding Flow.

Controls the two-phase onboarding process with proper state management
and phase transitions.
"""

from enum import Enum
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from datetime import datetime
from .two_phase_flow import TwoPhaseOrchestrator, Phase1Result, Phase2Result, HotelInputs
from ..utils.permission_mode import PermissionMode, DEFAULT_MODE


class OnboardingPhase(Enum):
    INIT = "inicio"
    PHASE_1_HOOK = "fase_1_hook"
    PHASE_2_INPUT = "fase_2_input"
    VALIDATION = "validacion"
    CALCULATION = "calculo"
    COMPLETE = "completo"
    ERROR = "error"


class OnboardingStatus(Enum):
    PENDING = "pendiente"
    IN_PROGRESS = "en_progreso"
    COMPLETED = "completado"
    BLOCKED = "bloqueado"
    ERROR = "error"


@dataclass
class OnboardingState:
    hotel_id: str
    hotel_url: str
    current_phase: OnboardingPhase
    status: OnboardingStatus
    phase_1_result: Optional[Phase1Result] = None
    phase_2_result: Optional[Phase2Result] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    progress_percentage: int = field(default=0)  # NUEVO: Progreso del onboarding


class OnboardingController:

    def __init__(
        self,
        permission_mode: PermissionMode = DEFAULT_MODE,
        on_ask_permission: Optional[Callable] = None,
    ):
        self.permission_mode = permission_mode
        self.on_ask_permission = on_ask_permission
        self._orchestrator = TwoPhaseOrchestrator(
            permission_mode=permission_mode,
            on_ask_permission=on_ask_permission,
        )
        self._states: Dict[str, OnboardingState] = {}

    def start_onboarding(
        self,
        hotel_url: str,
        hotel_name: str = None,
        region: str = "default"
    ) -> OnboardingState:
        hotel_id = self.generate_hotel_id(hotel_url)

        state = OnboardingState(
            hotel_id=hotel_id,
            hotel_url=hotel_url,
            current_phase=OnboardingPhase.INIT,
            status=OnboardingStatus.PENDING,
            metadata={
                "hotel_name": hotel_name,
                "region": region
            }
        )

        self._states[hotel_id] = state

        state.current_phase = OnboardingPhase.PHASE_1_HOOK
        state.status = OnboardingStatus.IN_PROGRESS
        state.updated_at = datetime.now()

        try:
            phase1_result = self._orchestrator.phase_1_hook(
                hotel_url=hotel_url,
                hotel_name=hotel_name,
                region=region
            )
            state.phase_1_result = phase1_result
            state.current_phase = OnboardingPhase.PHASE_2_INPUT
            state.status = OnboardingStatus.PENDING
        except Exception as e:
            state.current_phase = OnboardingPhase.ERROR
            state.status = OnboardingStatus.ERROR
            state.errors.append(f"Phase 1 error: {str(e)}")

        state.updated_at = datetime.now()
        return state

    def submit_phase_2(
        self,
        hotel_id: str,
        inputs: HotelInputs,
        scraped_data: Dict = None,
        gbp_data: Dict = None
    ) -> OnboardingState:
        state = self.get_state(hotel_id)
        if not state:
            raise ValueError(f"Onboarding not found for hotel_id: {hotel_id}")

        if state.current_phase != OnboardingPhase.PHASE_2_INPUT:
            raise ValueError(
                f"Invalid phase transition. Current: {state.current_phase}, "
                f"expected: {OnboardingPhase.PHASE_2_INPUT}"
            )

        state.status = OnboardingStatus.IN_PROGRESS
        state.updated_at = datetime.now()

        try:
            phase2_result = self._orchestrator.phase_2_input(
                phase_1_result=state.phase_1_result,
                user_inputs=inputs,
                scraped_data=scraped_data,
                gbp_data=gbp_data
            )
            state.phase_2_result = phase2_result

            if phase2_result.has_conflicts:
                state.current_phase = OnboardingPhase.VALIDATION
                state.status = OnboardingStatus.BLOCKED
            else:
                state.current_phase = OnboardingPhase.CALCULATION
                state.status = OnboardingStatus.COMPLETED

        except Exception as e:
            state.current_phase = OnboardingPhase.ERROR
            state.status = OnboardingStatus.ERROR
            state.errors.append(f"Phase 2 error: {str(e)}")

        state.updated_at = datetime.now()
        return state

    def get_state(self, hotel_id: str) -> Optional[OnboardingState]:
        return self._states.get(hotel_id)

    def can_proceed_to_assets(self, hotel_id: str) -> bool:
        state = self.get_state(hotel_id)
        if not state or not state.phase_2_result:
            return False

        if state.status in (OnboardingStatus.ERROR, OnboardingStatus.BLOCKED):
            return False

        return not state.phase_2_result.has_conflicts

    def get_conflict_summary(self, hotel_id: str) -> List[str]:
        state = self.get_state(hotel_id)
        if not state or not state.phase_2_result:
            return []

        conflicts = state.phase_2_result.conflicts_report
        summary = []

        for conflict in conflicts:
            summary.append(f"[CONFLICT] {conflict}")

        return summary

    def get_progress_percentage(self, hotel_id: str) -> int:
        state = self.get_state(hotel_id)
        if not state:
            return 0

        phase_progress = {
            OnboardingPhase.INIT: 0,
            OnboardingPhase.PHASE_1_HOOK: 30,
            OnboardingPhase.PHASE_2_INPUT: 30,
            OnboardingPhase.VALIDATION: 60,
            OnboardingPhase.CALCULATION: 60,
            OnboardingPhase.COMPLETE: 100,
            OnboardingPhase.ERROR: 0
        }

        return phase_progress.get(state.current_phase, 0)

    def reset_onboarding(self, hotel_id: str) -> OnboardingState:
        state = self.get_state(hotel_id)
        if not state:
            raise ValueError(f"Onboarding not found for hotel_id: {hotel_id}")

        hotel_url = state.hotel_url
        hotel_name = state.metadata.get("hotel_name")
        region = state.metadata.get("region", "default")

        return self.start_onboarding(hotel_url, hotel_name, region)

    @staticmethod
    def generate_hotel_id(hotel_url: str) -> str:
        sanitized = (
            hotel_url.lower()
            .replace("https://", "")
            .replace("http://", "")
            .replace("www.", "")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
            .replace("=", "_")
        )
        return f"hotel_{sanitized}"

    @staticmethod
    def format_status_report(state: OnboardingState) -> str:
        lines = [
            "=" * 50,
            "ONBOARDING STATUS REPORT",
            "=" * 50,
            f"Hotel ID:    {state.hotel_id}",
            f"URL:         {state.hotel_url}",
            f"Phase:       {state.current_phase.value}",
            f"Status:      {state.status.value}",
            f"Created:     {state.created_at.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Updated:     {state.updated_at.strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 50,
        ]

        if state.phase_1_result:
            lines.append("Phase 1: COMPLETED")
        else:
            lines.append("Phase 1: PENDING")

        if state.phase_2_result:
            lines.append("Phase 2: COMPLETED")
            conflicts = state.phase_2_result.validation_conflicts
            if conflicts:
                lines.append(f"  Conflicts: {len(conflicts)} found")
        else:
            lines.append("Phase 2: PENDING")

        lines.append("-" * 50)

        if state.status == OnboardingStatus.COMPLETED:
            lines.append("Next Action: Ready for asset generation")
        elif state.status == OnboardingStatus.BLOCKED:
            lines.append("Next Action: Resolve validation conflicts")
        elif state.status == OnboardingStatus.ERROR:
            lines.append("Next Action: Review errors and reset")
        elif state.current_phase == OnboardingPhase.PHASE_2_INPUT:
            lines.append("Next Action: Submit Phase 2 inputs")
        else:
            lines.append("Next Action: Wait for current phase")

        if state.errors:
            lines.append("-" * 50)
            lines.append("ERRORS:")
            for error in state.errors:
                lines.append(f"  - {error}")

        lines.append("=" * 50)
        return "\n".join(lines)
    def _update_progress(self, state: OnboardingState) -> None:
        """Update progress percentage based on current phase."""
        progress_map = {
            OnboardingPhase.INIT: 0,
            OnboardingPhase.PHASE_1_HOOK: 30,
            OnboardingPhase.PHASE_2_INPUT: 50,
            OnboardingPhase.VALIDATION: 70,
            OnboardingPhase.CALCULATION: 85,
            OnboardingPhase.COMPLETE: 100,
            OnboardingPhase.ERROR: 0,
        }
        state.progress_percentage = progress_map.get(state.current_phase, 0)

    @property
    def get_progress(self) -> int:
        """Get current progress percentage."""
        if not self._states:
            return 0
        latest_state = list(self._states.values())[-1]
        return latest_state.progress_percentage
