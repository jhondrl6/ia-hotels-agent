"""Pricing Resolution Wrapper v4.1.0.

Provides a wrapper around pricing calculations with shadow mode support,
feature flag integration, and safe rollout capabilities.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

from modules.financial_engine.feature_flags import (
    get_flags,
    RolloutMode,
    FinancialFeatureFlags,
)
from modules.financial_engine.pricing_calculator import (
    PricingCalculator,
    PricingResult,
)
from modules.financial_engine.shadow_logger import ShadowLogger, ShadowComparison


class PricingSource(Enum):
    """Source of the pricing value."""
    HYBRID_V410 = "hybrid_v410"
    LEGACY_FIXED = "legacy_fixed"
    SEGMENT_OVERRIDE = "segment_override"


@dataclass
class PricingResolutionResult:
    """Result of pricing resolution with metadata."""
    monthly_price_cop: float
    tier: str
    pain_ratio: float
    is_compliant: bool
    expected_loss_cop: float
    source: str  # "hybrid_v410", "legacy_fixed", "segment_override"
    used_new_calculation: bool
    shadow_comparison: Optional[ShadowComparison] = None
    metadata: Optional[Dict[str, Any]] = None


class PricingResolutionWrapper:
    """Wrapper for pricing calculations with shadow mode support."""

    # Legacy fixed 5% pain ratio
    LEGACY_PAIN_RATIO = 0.05

    def __init__(
        self,
        feature_flags: Optional[FinancialFeatureFlags] = None,
        shadow_logger: Optional[ShadowLogger] = None,
    ):
        self.flags = feature_flags or get_flags()
        self.shadow_logger = shadow_logger or ShadowLogger()
        self._calculator: Optional[PricingCalculator] = None

    def _get_calculator(self) -> PricingCalculator:
        """Lazy initialization of the calculator."""
        if self._calculator is None:
            self._calculator = PricingCalculator()
        return self._calculator

    def resolve(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None,
        hotel_id: Optional[str] = None,
        hotel_name: Optional[str] = None,
    ) -> PricingResolutionResult:
        """Resolve pricing with shadow mode support.

        Args:
            rooms: Number of rooms
            expected_loss_cop: Expected monthly loss in COP
            segment: Optional segment override (boutique/standard/large)
            hotel_id: Optional hotel identifier for logging
            hotel_name: Optional hotel name for logging

        Returns:
            PricingResolutionResult with price and metadata
        """
        mode = self.flags.pricing_hybrid_mode

        # Determine which calculation path to use
        if mode == RolloutMode.FORCE_LEGACY:
            return self._legacy_resolution(rooms, expected_loss_cop, segment)

        elif mode == RolloutMode.ACTIVE:
            return self._new_resolution(rooms, expected_loss_cop, segment)

        elif mode in (RolloutMode.SHADOW, RolloutMode.CANARY):
            return self._shadow_resolution(
                rooms, expected_loss_cop, segment, hotel_id, hotel_name
            )

        # Fallback to legacy for unknown modes
        return self._legacy_resolution(rooms, expected_loss_cop, segment)

    def _legacy_resolution(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None,
    ) -> PricingResolutionResult:
        """Use legacy fixed 5% pricing resolution."""
        # Determine tier based on rooms or segment
        tier = self._determine_tier(rooms, segment)
        
        # Legacy: fixed 5% of expected loss
        price = expected_loss_cop * self.LEGACY_PAIN_RATIO

        # Calculate legacy pain ratio (always 0.05 unless zero loss)
        pain_ratio = self.LEGACY_PAIN_RATIO if expected_loss_cop > 0 else 0
        is_compliant = 0.03 <= pain_ratio <= 0.06

        return PricingResolutionResult(
            monthly_price_cop=round(price, 2),
            tier=tier,
            pain_ratio=round(pain_ratio, 4),
            is_compliant=is_compliant,
            expected_loss_cop=expected_loss_cop,
            source=PricingSource.LEGACY_FIXED.value,
            used_new_calculation=False,
            metadata={
                "rooms": rooms,
                "segment": segment,
                "fallback_to_legacy": True,
                "formula_used": f"{self.LEGACY_PAIN_RATIO * 100}% of expected loss",
            },
        )

    def _new_resolution(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None,
    ) -> PricingResolutionResult:
        """Use new hybrid pricing resolution."""
        calculator = self._get_calculator()
        pricing_result = calculator.calculate(rooms, expected_loss_cop, segment)

        return PricingResolutionResult(
            monthly_price_cop=pricing_result.monthly_price_cop,
            tier=pricing_result.tier,
            pain_ratio=pricing_result.pain_ratio,
            is_compliant=pricing_result.is_compliant,
            expected_loss_cop=expected_loss_cop,
            source=PricingSource.HYBRID_V410.value,
            used_new_calculation=True,
            metadata={
                "rooms": rooms,
                "formula_used": pricing_result.formula_used,
                "min_price": pricing_result.min_price,
                "max_price": pricing_result.max_price,
                "recommended_price": pricing_result.recommended_price,
                "tier_config": pricing_result.metadata.get("tier_config", {}),
            },
        )

    def _shadow_resolution(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None,
        hotel_id: Optional[str] = None,
        hotel_name: Optional[str] = None,
    ) -> PricingResolutionResult:
        """Calculate both legacy and new, log comparison, return appropriate result."""
        # Calculate both values
        legacy_result = self._legacy_resolution(rooms, expected_loss_cop, segment)
        new_result = self._new_resolution(rooms, expected_loss_cop, segment)

        # Build comparison data for shadow logger
        legacy_data = self._build_legacy_data(legacy_result)
        new_data = self._build_new_data(new_result)

        # Log the comparison
        comparison = self.shadow_logger.log_comparison(
            legacy_result=legacy_data,
            new_result=new_data,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            flags=self._flags_to_dict(),
        )

        # Determine which result to return based on mode
        if self.flags.pricing_hybrid_mode == RolloutMode.CANARY:
            # In CANARY mode, use new if it passes validation
            if comparison.would_use_new:
                result = new_result
            else:
                result = legacy_result
        else:
            # In SHADOW mode, always return legacy but include comparison
            result = legacy_result

        # Attach shadow comparison to result
        result.shadow_comparison = comparison
        if result.metadata is None:
            result.metadata = {}
        result.metadata["shadow_mode"] = self.flags.pricing_hybrid_mode.value
        result.metadata["would_use_new"] = comparison.would_use_new

        return result

    def _determine_tier(self, rooms: int, segment: Optional[str]) -> str:
        """Determine hotel tier based on rooms or segment."""
        if segment:
            segment_lower = segment.lower()
            if segment_lower in ("boutique", "standard", "large"):
                return segment_lower

        if rooms <= 25:
            return "boutique"
        elif rooms <= 60:
            return "standard"
        else:
            return "large"

    def _build_legacy_data(
        self,
        legacy_result: PricingResolutionResult,
    ) -> Dict[str, Any]:
        """Build legacy result data structure for shadow logging."""
        price = legacy_result.monthly_price_cop
        expected_loss = legacy_result.expected_loss_cop
        return {
            "scenarios": {
                "conservative": {
                    "monthly_cop": expected_loss * 0.5,
                },
                "realistic": {
                    "monthly_cop": expected_loss * 0.7,
                },
                "optimistic": {
                    "monthly_cop": expected_loss * 0.9,
                },
            },
            "pricing": {
                "monthly_price_cop": price,
                "pain_ratio": legacy_result.pain_ratio,
                "tier": legacy_result.tier,
            },
        }

    def _build_new_data(
        self,
        new_result: PricingResolutionResult,
    ) -> Dict[str, Any]:
        """Build new result data structure for shadow logging."""
        price = new_result.monthly_price_cop
        expected_loss = new_result.expected_loss_cop
        return {
            "scenarios": {
                "conservative": {
                    "monthly_cop": expected_loss * 0.5,
                },
                "realistic": {
                    "monthly_cop": expected_loss * 0.7,
                },
                "optimistic": {
                    "monthly_cop": expected_loss * 0.9,
                },
            },
            "pricing": {
                "monthly_price_cop": price,
                "pain_ratio": new_result.pain_ratio,
                "tier": new_result.tier,
                "is_compliant": new_result.is_compliant,
            },
        }

    def _flags_to_dict(self) -> Dict[str, Any]:
        """Convert feature flags to dictionary for logging."""
        return {
            "pricing_hybrid_enabled": self.flags.pricing_hybrid_enabled,
            "pricing_hybrid_mode": self.flags.pricing_hybrid_mode.value,
            "shadow_logging_enabled": self.flags.shadow_logging_enabled,
        }


def calculate_price_with_shadow(
    rooms: int,
    expected_loss_cop: float,
    segment: Optional[str] = None,
    hotel_id: Optional[str] = None,
    hotel_name: Optional[str] = None,
    feature_flags: Optional[FinancialFeatureFlags] = None,
    shadow_logger: Optional[ShadowLogger] = None,
) -> PricingResolutionResult:
    """Convenience function to calculate pricing with shadow mode support.

    Args:
        rooms: Number of rooms
        expected_loss_cop: Expected monthly loss in COP
        segment: Optional segment override (boutique/standard/large)
        hotel_id: Optional hotel identifier for logging
        hotel_name: Optional hotel name for logging
        feature_flags: Optional feature flags override
        shadow_logger: Optional shadow logger instance

    Returns:
        PricingResolutionResult with price and metadata
    """
    wrapper = PricingResolutionWrapper(
        feature_flags=feature_flags,
        shadow_logger=shadow_logger,
    )
    return wrapper.resolve(rooms, expected_loss_cop, segment, hotel_id, hotel_name)
