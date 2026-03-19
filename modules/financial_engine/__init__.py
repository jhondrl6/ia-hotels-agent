"""Financial Engine v4.1.0 - Robust Financial Calculations.

This module provides:
- Scenario-based financial projections
- Regional ADR resolution
- Hybrid pricing calculations
- Shadow mode for safe rollout
"""

from .scenario_calculator import (
    ScenarioCalculator,
    HotelFinancialData,
    ScenarioType,
    FinancialScenario,
)
from .loss_projector import LossProjector, MonthlyProjection
from .formula_transparency import FormulaTransparency
from .feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
    get_flags,
    is_v410_active,
)
from .inputs_contract import (
    FinancialInputsContract,
    ValidationResult,
    ValidationSeverity,
)
from .shadow_logger import ShadowLogger, ShadowComparison
from .regional_adr_resolver import (
    RegionalADRResolver,
    RegionalADRResult,
    resolve_regional_adr,
)
from .adr_resolution_wrapper import (
    ADRResolutionWrapper,
    ADRResolutionResult,
    ADRSource,
    resolve_adr_with_shadow,
)
from .pricing_resolution_wrapper import (
    PricingResolutionWrapper,
    PricingResolutionResult,
    PricingSource,
    calculate_price_with_shadow,
)

__all__ = [
    # Core calculations
    "ScenarioCalculator",
    "HotelFinancialData", 
    "ScenarioType",
    "FinancialScenario",
    "LossProjector",
    "MonthlyProjection",
    "FormulaTransparency",
    # Feature flags
    "FinancialFeatureFlags",
    "RolloutMode",
    "get_flags",
    "is_v410_active",
    # Input validation
    "FinancialInputsContract",
    "ValidationResult",
    "ValidationSeverity",
    # Shadow logging
    "ShadowLogger",
    "ShadowComparison",
    # Regional ADR resolution
    "RegionalADRResolver",
    "RegionalADRResult",
    "resolve_regional_adr",
    # ADR resolution wrapper
    "ADRResolutionWrapper",
    "ADRResolutionResult",
    "ADRSource",
    "resolve_adr_with_shadow",
    # Pricing resolution wrapper
    "PricingResolutionWrapper",
    "PricingResolutionResult",
    "PricingSource",
    "calculate_price_with_shadow",
]

__version__ = "4.1.0"
