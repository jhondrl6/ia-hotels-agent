"""ADR Resolution Wrapper v4.1.0.

Provides a wrapper around regional ADR resolution with shadow mode support,
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
from modules.financial_engine.regional_adr_resolver import (
    RegionalADRResolver,
    RegionalADRResult,
)
from modules.financial_engine.shadow_logger import ShadowLogger, ShadowComparison


class ADRSource(Enum):
    """Source of the ADR value."""
    REGIONAL_V410 = "regional_v410"
    LEGACY_HARDCODE = "legacy_hardcode"
    USER_PROVIDED = "user_provided"


@dataclass
class ADRResolutionResult:
    """Result of ADR resolution with metadata."""
    adr_cop: float
    source: str  # "regional_v410", "legacy_hardcode", "user_provided"
    confidence: str
    used_new_calculation: bool
    shadow_comparison: Optional[ShadowComparison] = None
    metadata: Optional[Dict[str, Any]] = None


class ADRResolutionWrapper:
    """Wrapper for regional ADR resolution with shadow mode support."""

    LEGACY_DEFAULT_ADR = 300000.0

    def __init__(
        self,
        feature_flags: Optional[FinancialFeatureFlags] = None,
        plan_maestro_path: Optional[str] = None,
        shadow_logger: Optional[ShadowLogger] = None,
    ):
        self.flags = feature_flags or get_flags()
        self.plan_maestro_path = plan_maestro_path
        self.shadow_logger = shadow_logger or ShadowLogger()
        self._resolver: Optional[RegionalADRResolver] = None

    def _get_resolver(self) -> RegionalADRResolver:
        """Lazy initialization of the resolver."""
        if self._resolver is None:
            self._resolver = RegionalADRResolver(self.plan_maestro_path)
        return self._resolver

    def resolve(
        self,
        region: str,
        rooms: int,
        user_provided_adr: Optional[float] = None,
        hotel_id: Optional[str] = None,
        hotel_name: Optional[str] = None,
    ) -> ADRResolutionResult:
        """Resolve ADR with shadow mode support.

        Args:
            region: Hotel region code
            rooms: Number of rooms
            user_provided_adr: Optional ADR provided by user
            hotel_id: Optional hotel identifier for logging
            hotel_name: Optional hotel name for logging

        Returns:
            ADRResolutionResult with ADR value and metadata
        """
        mode = self.flags.regional_adr_mode

        # Determine which calculation path to use
        if mode == RolloutMode.FORCE_LEGACY:
            return self._legacy_resolution(user_provided_adr)

        elif mode == RolloutMode.ACTIVE:
            return self._new_resolution(region, rooms, user_provided_adr)

        elif mode in (RolloutMode.SHADOW, RolloutMode.CANARY):
            return self._shadow_resolution(
                region, rooms, user_provided_adr, hotel_id, hotel_name
            )

        # Fallback to legacy for unknown modes
        return self._legacy_resolution(user_provided_adr)

    def _legacy_resolution(
        self, user_provided_adr: Optional[float] = None
    ) -> ADRResolutionResult:
        """Use legacy hardcoded ADR resolution."""
        adr = user_provided_adr if user_provided_adr is not None else self.LEGACY_DEFAULT_ADR

        return ADRResolutionResult(
            adr_cop=adr,
            source=ADRSource.USER_PROVIDED.value
            if user_provided_adr
            else ADRSource.LEGACY_HARDCODE.value,
            confidence="ESTIMATED",
            used_new_calculation=False,
            metadata={
                "user_provided_adr": user_provided_adr,
                "fallback_to_legacy": True,
            },
        )

    def _new_resolution(
        self,
        region: str,
        rooms: int,
        user_provided_adr: Optional[float] = None,
    ) -> ADRResolutionResult:
        """Use new regional ADR resolution."""
        resolver = self._get_resolver()
        regional_result = resolver.resolve(region, rooms, user_provided_adr)

        return ADRResolutionResult(
            adr_cop=regional_result.adr_cop,
            source=ADRSource.REGIONAL_V410.value,
            confidence=regional_result.confidence,
            used_new_calculation=True,
            metadata={
                "region": regional_result.region,
                "segment": regional_result.segment,
                "is_default": regional_result.is_default,
                "regional_source": regional_result.source,
                "user_provided_adr": user_provided_adr,
            },
        )

    def _shadow_resolution(
        self,
        region: str,
        rooms: int,
        user_provided_adr: Optional[float] = None,
        hotel_id: Optional[str] = None,
        hotel_name: Optional[str] = None,
    ) -> ADRResolutionResult:
        """Calculate both legacy and new, log comparison, return appropriate result."""
        # Calculate both values
        legacy_result = self._legacy_resolution(user_provided_adr)
        new_result = self._new_resolution(region, rooms, user_provided_adr)

        # Build comparison data for shadow logger
        legacy_data = self._build_legacy_data(legacy_result, rooms)
        new_data = self._build_new_data(new_result, region, rooms)

        # Log the comparison
        comparison = self.shadow_logger.log_comparison(
            legacy_result=legacy_data,
            new_result=new_data,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            flags=self._flags_to_dict(),
        )

        # Determine which result to return based on mode
        if self.flags.regional_adr_mode == RolloutMode.CANARY:
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
        result.metadata["shadow_mode"] = self.flags.regional_adr_mode.value
        result.metadata["would_use_new"] = comparison.would_use_new

        return result

    def _build_legacy_data(
        self, legacy_result: ADRResolutionResult, rooms: int
    ) -> Dict[str, Any]:
        """Build legacy result data structure for shadow logging."""
        return {
            "scenarios": {
                "conservative": {
                    "monthly_cop": legacy_result.adr_cop * rooms * 0.5,
                    "adr_cop": legacy_result.adr_cop,
                },
                "realistic": {
                    "monthly_cop": legacy_result.adr_cop * rooms * 0.7,
                    "adr_cop": legacy_result.adr_cop,
                },
                "optimistic": {
                    "monthly_cop": legacy_result.adr_cop * rooms * 0.9,
                    "adr_cop": legacy_result.adr_cop,
                },
            },
            "pricing": {
                "monthly_price_cop": legacy_result.adr_cop * 0.05,
                "pain_ratio": 0.05,
            },
        }

    def _build_new_data(
        self, new_result: ADRResolutionResult, region: str, rooms: int
    ) -> Dict[str, Any]:
        """Build new result data structure for shadow logging."""
        adr = new_result.adr_cop
        return {
            "scenarios": {
                "conservative": {
                    "monthly_cop": adr * rooms * 0.5,
                    "adr_cop": adr,
                },
                "realistic": {
                    "monthly_cop": adr * rooms * 0.7,
                    "adr_cop": adr,
                },
                "optimistic": {
                    "monthly_cop": adr * rooms * 0.9,
                    "adr_cop": adr,
                },
            },
            "pricing": {
                "monthly_price_cop": adr * 0.04,
                "pain_ratio": 0.04,
            },
        }

    def _flags_to_dict(self) -> Dict[str, Any]:
        """Convert feature flags to dictionary for logging."""
        return {
            "regional_adr_enabled": self.flags.regional_adr_enabled,
            "regional_adr_mode": self.flags.regional_adr_mode.value,
            "shadow_logging_enabled": self.flags.shadow_logging_enabled,
        }


def resolve_adr_with_shadow(
    region: str,
    rooms: int,
    user_provided_adr: Optional[float] = None,
    hotel_id: Optional[str] = None,
    hotel_name: Optional[str] = None,
    feature_flags: Optional[FinancialFeatureFlags] = None,
    plan_maestro_path: Optional[str] = None,
    shadow_logger: Optional[ShadowLogger] = None,
) -> ADRResolutionResult:
    """Convenience function to resolve ADR with shadow mode support.

    Args:
        region: Hotel region code
        rooms: Number of rooms
        user_provided_adr: Optional ADR provided by user
        hotel_id: Optional hotel identifier for logging
        hotel_name: Optional hotel name for logging
        feature_flags: Optional feature flags override
        plan_maestro_path: Optional path to plan maestro data
        shadow_logger: Optional shadow logger instance

    Returns:
        ADRResolutionResult with ADR value and metadata
    """
    wrapper = ADRResolutionWrapper(
        feature_flags=feature_flags,
        plan_maestro_path=plan_maestro_path,
        shadow_logger=shadow_logger,
    )
    return wrapper.resolve(region, rooms, user_provided_adr, hotel_id, hotel_name)
