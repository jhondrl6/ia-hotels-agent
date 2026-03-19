"""Feature Flags for Financial Engine v4.1.0 Rollout.

Provides safe rollout mechanism for new financial calculations
with shadow mode support and fallback capabilities.
"""

import os
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class RolloutMode(Enum):
    """Rollout modes for feature activation."""
    SHADOW = "shadow"      # Calculate both, return old, log new
    CANARY = "canary"      # Calculate both, return new if valid, log both
    ACTIVE = "active"      # Return new, fallback to old on error
    FORCE_LEGACY = "legacy"  # Always return old (emergency rollback)


@dataclass(frozen=True)
class FinancialFeatureFlags:
    """Feature flags for financial engine v4.1.0.
    
    All flags default to SAFE values for production.
    Override via environment variables for gradual rollout.
    """
    
    # Feature toggles
    regional_adr_enabled: bool = False
    pricing_hybrid_enabled: bool = False
    financial_v410_enabled: bool = False
    
    # Rollout modes
    regional_adr_mode: RolloutMode = RolloutMode.SHADOW
    pricing_hybrid_mode: RolloutMode = RolloutMode.SHADOW
    
    # Safety limits
    max_adr_deviation_pct: float = 40.0  # Conflict threshold
    min_price_pain_ratio: float = 0.03   # 3%
    max_price_pain_ratio: float = 0.06   # 6%
    
    # Shadow logging
    shadow_logging_enabled: bool = True
    shadow_log_path: str = ".agent/shadow_logs"
    
    @classmethod
    def from_env(cls) -> "FinancialFeatureFlags":
        """Load flags from environment variables."""
        return cls(
            regional_adr_enabled=_env_bool("FINANCIAL_REGIONAL_ADR_ENABLED", False),
            pricing_hybrid_enabled=_env_bool("FINANCIAL_PRICING_HYBRID_ENABLED", False),
            financial_v410_enabled=_env_bool("FINANCIAL_V410_ENABLED", False),
            regional_adr_mode=RolloutMode(
                os.getenv("FINANCIAL_REGIONAL_ADR_MODE", "shadow")
            ),
            pricing_hybrid_mode=RolloutMode(
                os.getenv("FINANCIAL_PRICING_HYBRID_MODE", "shadow")
            ),
            max_adr_deviation_pct=float(
                os.getenv("FINANCIAL_MAX_ADR_DEVIATION", "40.0")
            ),
            min_price_pain_ratio=float(
                os.getenv("FINANCIAL_MIN_PRICE_PAIN_RATIO", "0.03")
            ),
            max_price_pain_ratio=float(
                os.getenv("FINANCIAL_MAX_PRICE_PAIN_RATIO", "0.06")
            ),
            shadow_logging_enabled=_env_bool(
                "FINANCIAL_SHADOW_LOGGING_ENABLED", True
            ),
            shadow_log_path=os.getenv(
                "FINANCIAL_SHADOW_LOG_PATH", ".agent/shadow_logs"
            ),
        )
    
    @classmethod
    def production_safe(cls) -> "FinancialFeatureFlags":
        """Return production-safe defaults (all features off)."""
        return cls(
            regional_adr_enabled=False,
            pricing_hybrid_enabled=False,
            financial_v410_enabled=False,
            regional_adr_mode=RolloutMode.SHADOW,
            pricing_hybrid_mode=RolloutMode.SHADOW,
        )
    
    @classmethod
    def full_enabled(cls) -> "FinancialFeatureFlags":
        """Return all features enabled (for testing only)."""
        return cls(
            regional_adr_enabled=True,
            pricing_hybrid_enabled=True,
            financial_v410_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
    
    def should_use_regional_adr(self) -> bool:
        """Check if regional ADR should be used."""
        return self.regional_adr_enabled and \
               self.regional_adr_mode != RolloutMode.FORCE_LEGACY
    
    def should_use_hybrid_pricing(self) -> bool:
        """Check if hybrid pricing should be used."""
        return self.pricing_hybrid_enabled and \
               self.pricing_hybrid_mode != RolloutMode.FORCE_LEGACY
    
    def should_calculate_shadow(self) -> bool:
        """Check if shadow calculations should run."""
        return (
            self.regional_adr_mode in (RolloutMode.SHADOW, RolloutMode.CANARY) or
            self.pricing_hybrid_mode in (RolloutMode.SHADOW, RolloutMode.CANARY)
        ) and self.shadow_logging_enabled

    def should_use_harness_delegation(self) -> bool:
        """Check if Agent Harness should be used for financial calculations.

        Requires:
        - financial_v410_enabled = True
        - regional_adr_mode or pricing_hybrid_mode in [CANARY, ACTIVE]
        """
        if not self.financial_v410_enabled:
            return False

        harness_modes = (RolloutMode.CANARY, RolloutMode.ACTIVE)
        return (
            self.regional_adr_mode in harness_modes or
            self.pricing_hybrid_mode in harness_modes
        )


def _env_bool(name: str, default: bool) -> bool:
    """Parse boolean from environment variable."""
    value = os.getenv(name, str(default).lower())
    return value.lower() in ("true", "1", "yes", "on")


# Global instance (lazy-loaded)
_flags: Optional[FinancialFeatureFlags] = None


def get_flags() -> FinancialFeatureFlags:
    """Get current feature flags (cached)."""
    global _flags
    if _flags is None:
        _flags = FinancialFeatureFlags.from_env()
    return _flags


def reset_flags() -> None:
    """Reset flags (useful for testing)."""
    global _flags
    _flags = None


def is_v410_active() -> bool:
    """Quick check if v4.1.0 is fully active."""
    flags = get_flags()
    return flags.financial_v410_enabled and \
           flags.regional_adr_mode == RolloutMode.ACTIVE and \
           flags.pricing_hybrid_mode == RolloutMode.ACTIVE
