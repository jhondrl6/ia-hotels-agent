"""Hybrid Pricing Calculator v4.1.0.

Calculates pricing based on hotel segment with tiered formulas.
Ensures price/pain ratio stays within GATE (3%-6%).

Segment formulas:
- Boutique (10-25 rooms): 3% of expected loss, min $1.2M, max $2.5M
- Standard (26-60 rooms): 2.5% of expected loss, min $1.8M, max $3.8M
- Large (60+ rooms): 2% of expected loss, min $3.5M, max $7.5M
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any
from enum import Enum


class HotelTier(Enum):
    BOUTIQUE = "boutique"
    STANDARD = "standard"
    LARGE = "large"


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


class PricingCalculator:
    """Calculates hybrid pricing based on hotel tier.
    
    GATE (Goal-Aligned Tiered Economics):
    - Pain ratio must be in [3%, 6%]
    - Price proportional to hotel value/loss
    """
    
    # Tier configuration
    TIER_CONFIG = {
        HotelTier.BOUTIQUE: {
            "room_min": 10,
            "room_max": 25,
            "percentage": 0.03,  # 3%
            "min_price": 1_200_000,
            "max_price": 2_500_000,
        },
        HotelTier.STANDARD: {
            "room_min": 26,
            "room_max": 60,
            "percentage": 0.025,  # 2.5%
            "min_price": 1_800_000,
            "max_price": 3_800_000,
        },
        HotelTier.LARGE: {
            "room_min": 61,
            "room_max": None,  # No upper limit
            "percentage": 0.02,  # 2%
            "min_price": 3_500_000,
            "max_price": 7_500_000,
        },
    }
    
    # GATE limits
    GATE_MIN_RATIO = 0.03  # 3%
    GATE_MAX_RATIO = 0.06  # 6%
    GATE_IDEAL_RATIO = 0.045  # 4.5%
    
    def calculate(
        self,
        rooms: int,
        expected_loss_cop: float,
        segment: Optional[str] = None
    ) -> PricingResult:
        """Calculate pricing for a hotel.
        
        Args:
            rooms: Number of rooms
            expected_loss_cop: Expected monthly loss in COP
            segment: Optional segment override (boutique/standard/large)
            
        Returns:
            PricingResult with price and compliance info
        """
        # Determine tier
        tier = self._determine_tier(rooms, segment)
        config = self.TIER_CONFIG[tier]
        
        # Calculate recommended price (percentage of loss)
        recommended = expected_loss_cop * config["percentage"]
        
        # Apply min/max bounds
        price = max(config["min_price"], min(recommended, config["max_price"]))
        
        # Calculate pain ratio
        pain_ratio = price / expected_loss_cop if expected_loss_cop > 0 else 0
        
        # Check GATE compliance
        is_compliant = self.GATE_MIN_RATIO <= pain_ratio <= self.GATE_MAX_RATIO
        
        return PricingResult(
            monthly_price_cop=round(price, 2),
            tier=tier.value,
            pain_ratio=round(pain_ratio, 4),
            is_compliant=is_compliant,
            expected_loss_cop=round(expected_loss_cop, 2),
            formula_used=f"{config['percentage']*100}% of expected loss",
            min_price=config["min_price"],
            max_price=config["max_price"],
            recommended_price=round(recommended, 2),
            metadata={
                "rooms": rooms,
                "tier_config": config,
                "gate_min": self.GATE_MIN_RATIO,
                "gate_max": self.GATE_MAX_RATIO,
            }
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
    segment: Optional[str] = None
) -> PricingResult:
    """Convenience function to calculate hybrid pricing."""
    calc = PricingCalculator()
    return calc.calculate(rooms, expected_loss_cop, segment)
