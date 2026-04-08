"""Orchestration v4.0 for IA Hoteles Agent.

Manages two-phase user flow: Hook -> Input -> Validation -> Assets
"""

from .two_phase_flow import (
    Phase1Result,
    Phase2Result,
    HotelInputs,
    TwoPhaseOrchestrator,
)

from .onboarding_controller import (
    OnboardingPhase,
    OnboardingStatus,
    OnboardingState,
    OnboardingController,
)

# Re-export permission mode for convenience
from ..utils.permission_mode import (
    PermissionMode,
    OperationPermission,
    check_permission,
)

__all__ = [
    # Two Phase Flow
    "Phase1Result",
    "Phase2Result",
    "HotelInputs",
    "TwoPhaseOrchestrator",
    # Onboarding Controller
    "OnboardingPhase",
    "OnboardingStatus",
    "OnboardingState",
    "OnboardingController",
    # Permission Mode
    "PermissionMode",
    "OperationPermission",
    "check_permission",
]
