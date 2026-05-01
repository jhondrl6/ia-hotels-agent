"""Hybrid Pricing Calculator v4.2.0.

Calculates pricing based on hotel segment with tiered formulas.
Ensures price/pain ratio stays within GATE (3%-6%).

Segment formulas:
- Boutique (10-25 rooms): 3.5% of expected loss, min $1.2M, max $2.5M
- Standard (26-60 rooms): 2.5% of expected loss, min $1.8M, max $3.8M
- Large (60+ rooms): 2% of expected loss, min $3.5M, max $7.5M

Configuration loaded from config/pricing.yaml (with hardcoded fallback for backwards compatibility).
"""

import os
import logging
from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum

import yaml

logger = logging.getLogger(__name__)


class HotelTier(Enum):
    BOUTIQUE = "boutique"
    STANDARD = "standard"
    LARGE = "large"


# ---------------------------------------------------------------------------
# Default tier config (fallback when YAML is unavailable)
# Keys are strings (avoids enum-in-dict circular-import issues)
# ---------------------------------------------------------------------------
_DEFAULT_TIER_CONFIG: Dict[str, Dict[str, Any]] = {
    "boutique": {
        "room_min": 10,
        "room_max": 25,
        "percentage": 0.035,
        "min_price": 1_200_000,
        "max_price": 2_500_000,
    },
    "standard": {
        "room_min": 26,
        "room_max": 60,
        "percentage": 0.025,
        "min_price": 1_800_000,
        "max_price": 3_800_000,
    },
    "large": {
        "room_min": 61,
        "room_max": None,
        "percentage": 0.02,
        "min_price": 3_500_000,
        "max_price": 7_500_000,
    },
}

_DEFAULT_GATES = {
    "min_ratio": 0.03,
    "max_ratio": 0.06,
    "ideal_ratio": 0.045,
}

# ---------------------------------------------------------------------------
# Module-level cache for loaded config
# ---------------------------------------------------------------------------
_CACHED_CONFIG: Optional[Dict[str, Any]] = None


@dataclass
class PricingResult:
    """Result of pricing calculation."""
    monthly_price_cop: float
    tier: str
    pain_ratio: float
    is_compliant: bool
    expected_loss_cop: float
    formula_used: str
    min_price: float
    max_price: float
    recommended_price: float
    metadata: Dict[str, Any]


def _load_pricing_config() -> Dict[str, Any]:
    """Load pricing configuration from config/pricing.yaml.

    Caches result at module level. Falls back to hardcoded defaults
    if YAML is missing or invalid, logging a warning.

    Returns:
        Dict with keys: 'tiers', 'gates', 'packages'
    """
    global _CACHED_CONFIG

    if _CACHED_CONFIG is not None:
        return _CACHED_CONFIG

    config_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "config", "pricing.yaml"
    )
    config_path = os.path.normpath(config_path)

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f)

        if not isinstance(raw, dict):
            raise ValueError("pricing.yaml must be a dict at root level")

        tiers = raw.get("tiers", {})
        gates = raw.get("gates", {})
        packages = raw.get("packages", {})

        # Schema validation: tiers (stored with string keys internally)
        tier_map: Dict[str, Dict[str, Any]] = {}
        for tier_key in ("boutique", "standard", "large"):
            t = tiers.get(tier_key, {})
            defaults = _DEFAULT_TIER_CONFIG[tier_key]
            tier_map[tier_key] = {
                "percentage": float(t.get("percentage", defaults["percentage"])),
                "min_price": float(t.get("min_price", defaults["min_price"])),
                "max_price": float(t.get("max_price", defaults["max_price"])),
                "room_min": defaults["room_min"],
                "room_max": defaults["room_max"],
            }

        # Schema validation: gates
        validated_gates = {
            "min_ratio": float(gates.get("min_ratio", _DEFAULT_GATES["min_ratio"])),
            "max_ratio": float(gates.get("max_ratio", _DEFAULT_GATES["max_ratio"])),
            "ideal_ratio": float(gates.get("ideal_ratio", _DEFAULT_GATES["ideal_ratio"])),
        }

        validated_packages = {
            "monthly_default": float(packages.get("monthly_default", 1_200_000)),
            "setup_fee_default": float(packages.get("setup_fee_default", 2_500_000)),
            "floor_price": float(packages.get("floor_price", 1_200_000)),
        }

        _CACHED_CONFIG = {
            "tiers": tier_map,
            "gates": validated_gates,
            "packages": validated_packages,
        }

        logger.info(
            f"Pricing config loaded from pricing.yaml "
            f"(gates: {validated_gates['min_ratio']}-{validated_gates['max_ratio']})"
        )

    except FileNotFoundError:
        logger.warning(
            "pricing.yaml not found at %s — using hardcoded defaults. "
            "Create config/pricing.yaml to make pricing configurable.",
            config_path,
        )
        _CACHED_CONFIG = {
            "tiers": _DEFAULT_TIER_CONFIG,
            "gates": _DEFAULT_GATES,
            "packages": {
                "monthly_default": 1_200_000,
                "setup_fee_default": 2_500_000,
                "floor_price": 1_200_000,
            },
        }
    except Exception as exc:
        logger.warning(
            "Failed to load pricing.yaml (%s) — using hardcoded defaults: %s",
            config_path,
            exc,
        )
        _CACHED_CONFIG = {
            "tiers": _DEFAULT_TIER_CONFIG,
            "gates": _DEFAULT_GATES,
            "packages": {
                "monthly_default": 1_200_000,
                "setup_fee_default": 2_500_000,
                "floor_price": 1_200_000,
            },
        }

    return _CACHED_CONFIG


def get_floor_price() -> float:
    """Return the configured floor_price from pricing.yaml (or default)."""
    return _load_pricing_config()["packages"]["floor_price"]


class PricingCalculator:
    """Calculates hybrid pricing based on hotel tier.

    GATE (Goal-Aligned Tiered Economics):
    - Pain ratio must be in [3%, 6%]
    - Price proportional to hotel value/loss

    Configuration is loaded from config/pricing.yaml.
    """

    def __init__(self):
        cfg = _load_pricing_config()

        # Build TIER_CONFIG from YAML (with room bounds baked in from defaults)
        self.TIER_CONFIG: Dict[HotelTier, Dict[str, Any]] = {}
        tier_str_to_enum = {
            "boutique": HotelTier.BOUTIQUE,
            "standard": HotelTier.STANDARD,
            "large": HotelTier.LARGE,
        }
        for tier_key, tier_enum in tier_str_to_enum.items():
            yaml_tier = cfg["tiers"].get(tier_key, {})
            defaults = _DEFAULT_TIER_CONFIG[tier_key]
            self.TIER_CONFIG[tier_enum] = {
                "room_min": defaults["room_min"],
                "room_max": defaults["room_max"],
                "percentage": yaml_tier.get(
                    "percentage", defaults["percentage"]
                ),
                "min_price": yaml_tier.get(
                    "min_price", defaults["min_price"]
                ),
                "max_price": yaml_tier.get(
                    "max_price", defaults["max_price"]
                ),
            }

        self.GATE_MIN_RATIO: float = cfg["gates"]["min_ratio"]
        self.GATE_MAX_RATIO: float = cfg["gates"]["max_ratio"]
        self.GATE_IDEAL_RATIO: float = cfg["gates"]["ideal_ratio"]

    def calculate(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None,
    ) -> PricingResult:
        """Calculate pricing for a hotel.

        Args:
            rooms: Number of rooms
            expected_loss_cop: Expected monthly loss in COP
            segment: Optional segment override (boutique/standard/large)

        Returns:
            PricingResult with price and compliance info
        """
        tier = self._determine_tier(rooms, segment)
        config = self.TIER_CONFIG[tier]

        recommended = expected_loss_cop * config["percentage"]
        price = max(config["min_price"], min(recommended, config["max_price"]))

        pain_ratio = price / expected_loss_cop if expected_loss_cop > 0 else 0
        is_compliant = self.GATE_MIN_RATIO <= pain_ratio <= self.GATE_MAX_RATIO

        return PricingResult(
            monthly_price_cop=round(price, 2),
            tier=tier.value,
            pain_ratio=round(pain_ratio, 4),
            is_compliant=is_compliant,
            expected_loss_cop=round(expected_loss_cop, 2),
            formula_used=f"{round(config['percentage'] * 100, 4)}% of expected loss",
            min_price=config["min_price"],
            max_price=config["max_price"],
            recommended_price=round(recommended, 2),
            metadata={
                "rooms": rooms,
                "tier_config": config,
                "gate_min": self.GATE_MIN_RATIO,
                "gate_max": self.GATE_MAX_RATIO,
            },
        )

    def _determine_tier(self, rooms: int, segment: Optional[str]) -> HotelTier:
        """Determine hotel tier based on rooms or segment."""
        if segment:
            try:
                return HotelTier(segment.lower())
            except ValueError:
                pass

        if rooms <= 25:
            return HotelTier.BOUTIQUE
        elif rooms <= 60:
            return HotelTier.STANDARD
        else:
            return HotelTier.LARGE

    def validate_gate(self, price: float, expected_loss: float) -> Dict[str, Any]:
        """Validate if price is within GATE."""
        if expected_loss <= 0:
            return {"valid": False, "reason": "Expected loss must be positive"}

        ratio = price / expected_loss

        return {
            "valid": self.GATE_MIN_RATIO <= ratio <= self.GATE_MAX_RATIO,
            "ratio": round(ratio, 4),
            "min_allowed": self.GATE_MIN_RATIO,
            "max_allowed": self.GATE_MAX_RATIO,
            "within_ideal": abs(ratio - self.GATE_IDEAL_RATIO) < 0.01,
        }


def calculate_hybrid_price(
    rooms: int,
    expected_loss_cop: float,
    segment: Optional[str] = None,
) -> PricingResult:
    """Convenience function to calculate hybrid pricing."""
    calc = PricingCalculator()
    return calc.calculate(rooms, expected_loss_cop, segment)
