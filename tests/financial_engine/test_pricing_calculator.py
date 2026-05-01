"""Tests for the Hybrid Pricing Calculator v4.2.0.

Extends v4.1.0 tests to cover YAML loading, backwards compatibility,
and the get_floor_price() function added in v4.2.0.
"""

import pytest
import os
import tempfile
import yaml
from unittest.mock import patch
from modules.financial_engine.pricing_calculator import (
    PricingCalculator,
    HotelTier,
    PricingResult,
    calculate_hybrid_price,
    get_floor_price,
    _CACHED_CONFIG,
)


class TestBoutiquePricing:
    """Test pricing calculations for boutique hotels (10-25 rooms)."""

    def test_boutique_basic_calculation(self):
        """Test boutique pricing with typical expected loss."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000)

        assert result.tier == "boutique"
        assert result.formula_used == "3.5% of expected loss"
        # 3.5% of 50M = 1.75M, which is above min (1.2M) and below max (2.5M)
        assert result.monthly_price_cop == 1_750_000.00
        assert result.recommended_price == 1_750_000.00

    def test_boutique_min_price_enforced(self):
        """Test that min price is enforced for boutique hotels."""
        calc = PricingCalculator()
        # Low expected loss would result in price below minimum
        result = calc.calculate(rooms=15, expected_loss_cop=10_000_000)

        # 3.5% of 10M = 350K, but min is 1.2M
        assert result.monthly_price_cop == 1_200_000.00
        assert result.recommended_price == 350_000.00

    def test_boutique_max_price_enforced(self):
        """Test that max price is enforced for boutique hotels."""
        calc = PricingCalculator()
        # High expected loss would result in price above maximum
        result = calc.calculate(rooms=25, expected_loss_cop=200_000_000)

        # 3.5% of 200M = 7M, but max is 2.5M
        assert result.monthly_price_cop == 2_500_000.00
        assert result.recommended_price == 7_000_000.00


class TestStandardPricing:
    """Test pricing calculations for standard hotels (26-60 rooms)."""

    def test_standard_basic_calculation(self):
        """Test standard pricing with typical expected loss."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=40, expected_loss_cop=80_000_000)

        assert result.tier == "standard"
        assert result.formula_used == "2.5% of expected loss"
        # 2.5% of 80M = 2M, which is above min (1.8M) and below max (3.8M)
        assert result.monthly_price_cop == 2_000_000.00

    def test_standard_min_price_enforced(self):
        """Test that min price is enforced for standard hotels."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=30, expected_loss_cop=50_000_000)

        # 2.5% of 50M = 1.25M, but min is 1.8M
        assert result.monthly_price_cop == 1_800_000.00

    def test_standard_max_price_enforced(self):
        """Test that max price is enforced for standard hotels."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=60, expected_loss_cop=200_000_000)

        # 2.5% of 200M = 5M, but max is 3.8M
        assert result.monthly_price_cop == 3_800_000.00


class TestLargeHotelPricing:
    """Test pricing calculations for large hotels (60+ rooms)."""

    def test_large_basic_calculation(self):
        """Test large hotel pricing with typical expected loss."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=80, expected_loss_cop=150_000_000)

        assert result.tier == "large"
        assert result.formula_used == "2.0% of expected loss"
        # 2% of 150M = 3M, which is below min (3.5M)
        assert result.monthly_price_cop == 3_500_000.00

    def test_large_min_price_enforced(self):
        """Test that min price is enforced for large hotels."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=100, expected_loss_cop=100_000_000)

        # 2% of 100M = 2M, but min is 3.5M
        assert result.monthly_price_cop == 3_500_000.00

    def test_large_max_price_enforced(self):
        """Test that max price is enforced for large hotels."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=200, expected_loss_cop=500_000_000)

        # 2% of 500M = 10M, but max is 7.5M
        assert result.monthly_price_cop == 7_500_000.00

    def test_large_no_upper_room_limit(self):
        """Test that large hotels have no upper room limit."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=500, expected_loss_cop=200_000_000)

        assert result.tier == "large"
        assert result.metadata["rooms"] == 500


class TestPainRatioCalculation:
    """Test pain ratio calculations."""

    def test_pain_ratio_calculation(self):
        """Test that pain ratio is calculated correctly."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000)

        # Price is 1.75M (3.5%), expected loss is 50M
        expected_ratio = 1_750_000 / 50_000_000
        assert result.pain_ratio == round(expected_ratio, 4)
        assert result.pain_ratio == 0.035

    def test_pain_ratio_within_gate(self):
        """Test pain ratio within GATE range."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000)

        # 3.5% is within GATE (3%-6%)
        assert result.is_compliant is True
        assert 0.03 <= result.pain_ratio <= 0.06


class TestGateComplianceValidation:
    """Test GATE compliance validation."""

    def test_gate_validation_valid(self):
        """Test GATE validation with compliant ratio."""
        calc = PricingCalculator()
        validation = calc.validate_gate(price=4_500_000, expected_loss=100_000_000)

        assert validation["valid"] is True
        assert validation["ratio"] == 0.045
        assert validation["within_ideal"] is True

    def test_gate_validation_below_min(self):
        """Test GATE validation below minimum ratio."""
        calc = PricingCalculator()
        validation = calc.validate_gate(price=2_000_000, expected_loss=100_000_000)

        assert validation["valid"] is False
        assert validation["ratio"] == 0.02

    def test_gate_validation_above_max(self):
        """Test GATE validation above maximum ratio."""
        calc = PricingCalculator()
        validation = calc.validate_gate(price=8_000_000, expected_loss=100_000_000)

        assert validation["valid"] is False
        assert validation["ratio"] == 0.08

    def test_gate_validation_zero_loss(self):
        """Test GATE validation with zero expected loss."""
        calc = PricingCalculator()
        validation = calc.validate_gate(price=1_000_000, expected_loss=0)

        assert validation["valid"] is False
        assert validation["reason"] == "Expected loss must be positive"


class TestSegmentOverride:
    """Test segment override functionality."""

    def test_segment_override_boutique(self):
        """Test forcing boutique tier via segment."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=100, expected_loss_cop=50_000_000, segment="boutique")

        assert result.tier == "boutique"
        assert result.formula_used == "3.5% of expected loss"

    def test_segment_override_standard(self):
        """Test forcing standard tier via segment."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=80_000_000, segment="standard")

        assert result.tier == "standard"
        assert result.formula_used == "2.5% of expected loss"

    def test_segment_override_large(self):
        """Test forcing large tier via segment."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=30, expected_loss_cop=200_000_000, segment="large")

        assert result.tier == "large"
        assert result.formula_used == "2.0% of expected loss"

    def test_invalid_segment_fallback_to_rooms(self):
        """Test that invalid segment falls back to room-based tier."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000, segment="invalid")

        # Falls back to boutique based on rooms
        assert result.tier == "boutique"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_zero_loss_results_in_zero_pain_ratio(self):
        """Test that zero expected loss results in zero pain ratio."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=0)

        assert result.pain_ratio == 0
        assert result.is_compliant is False

    def test_negative_loss(self):
        """Test behavior with negative expected loss."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=-10_000_000)

        assert result.pain_ratio == 0
        assert result.is_compliant is False

    def test_exact_tier_boundaries(self):
        """Test exact tier boundary values."""
        calc = PricingCalculator()

        result_25 = calc.calculate(rooms=25, expected_loss_cop=50_000_000)
        assert result_25.tier == "boutique"

        result_26 = calc.calculate(rooms=26, expected_loss_cop=50_000_000)
        assert result_26.tier == "standard"

        result_60 = calc.calculate(rooms=60, expected_loss_cop=50_000_000)
        assert result_60.tier == "standard"

        result_61 = calc.calculate(rooms=61, expected_loss_cop=50_000_000)
        assert result_61.tier == "large"

    def test_very_small_room_count(self):
        """Test with very small room count (below typical boutique)."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=5, expected_loss_cop=30_000_000)

        assert result.tier == "boutique"

    def test_convenience_function(self):
        """Test the calculate_hybrid_price convenience function."""
        result = calculate_hybrid_price(rooms=40, expected_loss_cop=80_000_000)

        assert isinstance(result, PricingResult)
        assert result.tier == "standard"

    def test_pricing_result_dataclass(self):
        """Test that PricingResult dataclass works correctly."""
        result = PricingResult(
            monthly_price_cop=1_500_000,
            tier="boutique",
            pain_ratio=0.03,
            is_compliant=True,
            expected_loss_cop=50_000_000,
            formula_used="3% of expected loss",
            min_price=1_200_000,
            max_price=2_500_000,
            recommended_price=1_500_000,
            metadata={},
        )

        assert result.monthly_price_cop == 1_500_000
        assert result.is_compliant is True


class TestTierConfig:
    """Test tier configuration loaded from YAML."""

    def test_boutique_config(self):
        """Test boutique tier configuration loaded from pricing.yaml."""
        calc = PricingCalculator()
        config = calc.TIER_CONFIG[HotelTier.BOUTIQUE]

        assert config["room_min"] == 10
        assert config["room_max"] == 25
        assert config["percentage"] == 0.035
        assert config["min_price"] == 1_200_000
        assert config["max_price"] == 2_500_000

    def test_standard_config(self):
        """Test standard tier configuration loaded from pricing.yaml."""
        calc = PricingCalculator()
        config = calc.TIER_CONFIG[HotelTier.STANDARD]

        assert config["room_min"] == 26
        assert config["room_max"] == 60
        assert config["percentage"] == 0.025
        assert config["min_price"] == 1_800_000
        assert config["max_price"] == 3_800_000

    def test_large_config(self):
        """Test large tier configuration loaded from pricing.yaml."""
        calc = PricingCalculator()
        config = calc.TIER_CONFIG[HotelTier.LARGE]

        assert config["room_min"] == 61
        assert config["room_max"] is None
        assert config["percentage"] == 0.02
        assert config["min_price"] == 3_500_000
        assert config["max_price"] == 7_500_000

    def test_gate_constants(self):
        """Test GATE constant values loaded from pricing.yaml."""
        calc = PricingCalculator()
        assert calc.GATE_MIN_RATIO == 0.03
        assert calc.GATE_MAX_RATIO == 0.06
        assert calc.GATE_IDEAL_RATIO == 0.045


class TestMetadata:
    """Test metadata in pricing results."""

    def test_metadata_contains_expected_keys(self):
        """Test that metadata contains expected information."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=40, expected_loss_cop=80_000_000)

        assert "rooms" in result.metadata
        assert "tier_config" in result.metadata
        assert "gate_min" in result.metadata
        assert "gate_max" in result.metadata
        assert result.metadata["rooms"] == 40

    def test_tier_config_in_metadata(self):
        """Test that tier config is included in metadata."""
        calc = PricingCalculator()
        result = calc.calculate(rooms=20, expected_loss_cop=50_000_000)

        tier_config = result.metadata["tier_config"]
        assert tier_config["percentage"] == 0.035
        assert tier_config["min_price"] == 1_200_000


class TestYAMLLoading:
    """Tests for YAML configuration loading (v4.2.0 new)."""

    def teardown_method(self):
        """Reset the module-level cache after each test."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

    def test_pricing_yaml_absent_uses_defaults(self):
        """When pricing.yaml is absent, hardcoded defaults are used."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        with patch("modules.financial_engine.pricing_calculator.open", side_effect=FileNotFoundError()):
            calc = PricingCalculator()

        # Should fall back to defaults
        assert calc.TIER_CONFIG[HotelTier.BOUTIQUE]["min_price"] == 1_200_000
        assert calc.GATE_MIN_RATIO == 0.03
        assert calc.GATE_MAX_RATIO == 0.06

    def test_pricing_yaml_corrupt_uses_defaults(self):
        """When pricing.yaml is corrupt/invalid, hardcoded defaults are used."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        with patch("modules.financial_engine.pricing_calculator.open", side_effect=yaml.YAMLError("invalid")):
            calc = PricingCalculator()

        # Should fall back to defaults
        assert calc.TIER_CONFIG[HotelTier.BOUTIQUE]["min_price"] == 1_200_000
        assert calc.GATE_MIN_RATIO == 0.03

    def test_pricing_yaml_loaded_successfully(self):
        """When pricing.yaml exists, values are loaded from it."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        calc = PricingCalculator()

        # Values from config/pricing.yaml
        assert calc.TIER_CONFIG[HotelTier.BOUTIQUE]["percentage"] == 0.035
        assert calc.TIER_CONFIG[HotelTier.BOUTIQUE]["min_price"] == 1_200_000
        assert calc.GATE_MIN_RATIO == 0.03
        assert calc.GATE_MAX_RATIO == 0.06

    def test_get_floor_price_returns_yaml_value(self):
        """get_floor_price() returns the configured value from pricing.yaml."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        floor = get_floor_price()
        assert floor == 1_200_000

    def test_get_floor_price_unified(self):
        """floor_price in YAML is unified — no more 800K vs 1.2M inconsistency."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        floor = get_floor_price()
        # H-18b: floor was 800K in v4_proposal_generator.py, 1.2M in TIER_CONFIG
        # After FASE-CONFIG-3A, both must use 1.2M from pricing.yaml
        assert floor == 1_200_000
        assert floor != 800_000

    def test_config_cached(self):
        """Configuration is cached at module level after first load."""
        global _CACHED_CONFIG
        _CACHED_CONFIG = None

        calc1 = PricingCalculator()
        calc2 = PricingCalculator()

        # Both should reference the same cached config
        assert calc1.GATE_MIN_RATIO == calc2.GATE_MIN_RATIO
        assert calc1.TIER_CONFIG[HotelTier.BOUTIQUE]["percentage"] == calc2.TIER_CONFIG[HotelTier.BOUTIQUE]["percentage"]
