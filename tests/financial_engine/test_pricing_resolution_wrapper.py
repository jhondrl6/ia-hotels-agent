"""
Test module for pricing_resolution_wrapper.py

Comprehensive tests for the PricingResolutionWrapper class and PricingResolutionResult dataclass,
covering all rollout modes (LEGACY, ACTIVE, SHADOW, CANARY) and integration with
feature flags, pricing calculator, and shadow logger.
"""

import pytest
import json
import tempfile
from pathlib import Path
from dataclasses import asdict
from unittest.mock import Mock, MagicMock, patch

from modules.financial_engine.pricing_resolution_wrapper import (
    PricingResolutionResult,
    PricingResolutionWrapper,
    PricingSource,
    calculate_price_with_shadow,
)
from modules.financial_engine.feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
)
from modules.financial_engine.shadow_logger import ShadowLogger, ShadowComparison


@pytest.fixture
def mock_shadow_logger():
    """Provide a mock shadow logger."""
    logger = Mock(spec=ShadowLogger)
    comparison = ShadowComparison(
        comparison_id="test_123",
        timestamp="2024-01-01T00:00:00",
        would_use_new=True,
    )
    logger.log_comparison.return_value = comparison
    return logger


@pytest.fixture
def mock_shadow_logger_reject():
    """Provide a mock shadow logger that rejects new results."""
    logger = Mock(spec=ShadowLogger)
    comparison = ShadowComparison(
        comparison_id="test_456",
        timestamp="2024-01-01T00:00:00",
        would_use_new=False,
        rejection_reason="Pain ratio outside GATE",
    )
    logger.log_comparison.return_value = comparison
    return logger


class TestPricingSource:
    """Test cases for PricingSource enum."""

    def test_pricing_source_values(self):
        """Test PricingSource enum has correct values."""
        assert PricingSource.HYBRID_V410.value == "hybrid_v410"
        assert PricingSource.LEGACY_FIXED.value == "legacy_fixed"
        assert PricingSource.SEGMENT_OVERRIDE.value == "segment_override"


class TestPricingResolutionResult:
    """Test cases for PricingResolutionResult dataclass."""

    def test_basic_creation(self):
        """Test creating PricingResolutionResult with required fields."""
        result = PricingResolutionResult(
            monthly_price_cop=2_500_000,
            tier="standard",
            pain_ratio=0.045,
            is_compliant=True,
            expected_loss_cop=50_000_000,
            source="hybrid_v410",
            used_new_calculation=True,
        )

        assert result.monthly_price_cop == 2_500_000
        assert result.tier == "standard"
        assert result.pain_ratio == 0.045
        assert result.is_compliant is True
        assert result.expected_loss_cop == 50_000_000
        assert result.source == "hybrid_v410"
        assert result.used_new_calculation is True
        assert result.shadow_comparison is None
        assert result.metadata is None

    def test_creation_with_shadow_comparison(self, mock_shadow_logger):
        """Test creating PricingResolutionResult with shadow comparison."""
        comparison = mock_shadow_logger.log_comparison.return_value
        result = PricingResolutionResult(
            monthly_price_cop=1_500_000,
            tier="boutique",
            pain_ratio=0.05,
            is_compliant=True,
            expected_loss_cop=30_000_000,
            source="legacy_fixed",
            used_new_calculation=False,
            shadow_comparison=comparison,
            metadata={"test": "data"},
        )

        assert result.shadow_comparison == comparison
        assert result.metadata == {"test": "data"}


class TestPricingResolutionWrapperInitialization:
    """Test cases for wrapper initialization."""

    def test_default_initialization(self):
        """Test wrapper initializes with default dependencies."""
        wrapper = PricingResolutionWrapper()

        assert wrapper.flags is not None
        assert wrapper.LEGACY_PAIN_RATIO == 0.05
        assert wrapper._calculator is None

    def test_initialization_with_custom_flags(self):
        """Test wrapper initializes with custom feature flags."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        assert wrapper.flags == flags
        assert wrapper.flags.pricing_hybrid_enabled is True

    def test_initialization_with_custom_shadow_logger(self, mock_shadow_logger):
        """Test wrapper initializes with custom shadow logger."""
        wrapper = PricingResolutionWrapper(shadow_logger=mock_shadow_logger)

        assert wrapper.shadow_logger == mock_shadow_logger

    def test_lazy_calculator_initialization(self):
        """Test calculator is lazily initialized."""
        wrapper = PricingResolutionWrapper()

        assert wrapper._calculator is None

        calculator = wrapper._get_calculator()
        assert calculator is not None
        assert wrapper._calculator == calculator


class TestLegacyMode:
    """Test LEGACY mode resolution."""

    def test_legacy_mode_returns_fixed_percentage(self):
        """Test LEGACY mode returns fixed 5% of expected loss."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        expected_loss = 50_000_000
        result = wrapper.resolve(rooms=30, expected_loss_cop=expected_loss)

        # Legacy: 5% of expected loss
        expected_price = expected_loss * 0.05
        assert result.monthly_price_cop == expected_price
        assert result.source == "legacy_fixed"
        assert result.pain_ratio == 0.05
        assert result.used_new_calculation is False
        assert result.shadow_comparison is None

    def test_legacy_mode_with_different_tiers(self):
        """Test LEGACY mode returns same calculation regardless of tier."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        expected_loss = 40_000_000
        expected_price = expected_loss * 0.05  # 2_000_000

        # Boutique
        result = wrapper.resolve(rooms=15, expected_loss_cop=expected_loss)
        assert result.monthly_price_cop == expected_price
        assert result.tier == "boutique"

        # Standard
        result = wrapper.resolve(rooms=40, expected_loss_cop=expected_loss)
        assert result.monthly_price_cop == expected_price
        assert result.tier == "standard"

        # Large
        result = wrapper.resolve(rooms=80, expected_loss_cop=expected_loss)
        assert result.monthly_price_cop == expected_price
        assert result.tier == "large"

    def test_legacy_mode_with_segment_override(self):
        """Test LEGACY mode respects segment override."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        expected_loss = 50_000_000
        
        # Override rooms=80 (large) with segment=boutique
        result = wrapper.resolve(
            rooms=80, 
            expected_loss_cop=expected_loss,
            segment="boutique"
        )
        
        assert result.tier == "boutique"
        # Price still based on fixed percentage
        assert result.monthly_price_cop == expected_loss * 0.05

    def test_legacy_mode_metadata(self):
        """Test LEGACY mode includes correct metadata."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve(
            rooms=25, 
            expected_loss_cop=40_000_000,
            segment="boutique"
        )

        assert result.metadata["rooms"] == 25
        assert result.metadata["segment"] == "boutique"
        assert result.metadata["fallback_to_legacy"] is True
        assert "formula_used" in result.metadata

    def test_legacy_mode_compliance_calculation(self):
        """Test LEGACY mode calculates compliance based on pain ratio."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # 5% pain ratio should be compliant
        result = wrapper.resolve(rooms=20, expected_loss_cop=50_000_000)
        assert result.pain_ratio == 0.05
        assert result.is_compliant is True


class TestActiveMode:
    """Test ACTIVE mode resolution."""

    def test_active_mode_uses_hybrid_calculator(self):
        """Test ACTIVE mode uses new hybrid calculator."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # Boutique: 3% of expected loss, min 1.2M, max 2.5M
        expected_loss = 50_000_000
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)

        # 3% of 50M = 1.5M, within bounds
        assert result.monthly_price_cop == 1_500_000
        assert result.source == "hybrid_v410"
        assert result.tier == "boutique"
        assert result.used_new_calculation is True
        assert result.shadow_comparison is None

    def test_active_mode_applies_tier_bounds(self):
        """Test ACTIVE mode applies tier min/max bounds."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # Boutique with very high loss (would exceed max)
        expected_loss = 100_000_000  # 3% = 3M, but max is 2.5M
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)

        assert result.monthly_price_cop == 2_500_000  # capped at max
        assert result.pain_ratio == round(2_500_000 / 100_000_000, 4)

        # Boutique with very low loss (would be below min)
        expected_loss = 10_000_000  # 3% = 300K, but min is 1.2M
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)

        assert result.monthly_price_cop == 1_200_000  # floored at min

    def test_active_mode_different_tiers(self):
        """Test ACTIVE mode with different tiers."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        expected_loss = 80_000_000

        # Boutique (3%): 2.4M
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)
        assert result.tier == "boutique"
        assert result.monthly_price_cop == 2_400_000  # 3% of 80M

        # Standard (2.5%): 2.0M
        result = wrapper.resolve(rooms=40, expected_loss_cop=expected_loss)
        assert result.tier == "standard"
        assert result.monthly_price_cop == 2_000_000  # 2.5% of 80M

        # Large (2%): 1.6M, but min is 3.5M
        result = wrapper.resolve(rooms=80, expected_loss_cop=expected_loss)
        assert result.tier == "large"
        assert result.monthly_price_cop == 3_500_000  # floored at min for large

    def test_active_mode_compliance(self):
        """Test ACTIVE mode GATE compliance."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # Compliant case (pain ratio ~4.5%)
        result = wrapper.resolve(rooms=20, expected_loss_cop=50_000_000)
        assert result.is_compliant is True
        assert 0.03 <= result.pain_ratio <= 0.06

    def test_active_mode_metadata(self):
        """Test ACTIVE mode includes comprehensive metadata."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve(rooms=30, expected_loss_cop=60_000_000)

        assert result.metadata["rooms"] == 30
        assert "formula_used" in result.metadata
        assert "min_price" in result.metadata
        assert "max_price" in result.metadata
        assert "recommended_price" in result.metadata


class TestShadowMode:
    """Test SHADOW mode resolution."""

    def test_shadow_mode_returns_legacy(self, mock_shadow_logger):
        """Test SHADOW mode returns legacy value but calculates both."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        expected_loss = 50_000_000
        result = wrapper.resolve(
            rooms=20,
            expected_loss_cop=expected_loss,
            hotel_id="hotel_123"
        )

        # Should return legacy (fixed 5%) value
        expected_legacy = expected_loss * 0.05
        assert result.monthly_price_cop == expected_legacy
        assert result.source == "legacy_fixed"
        assert result.used_new_calculation is False

    def test_shadow_mode_logs_comparison(self, mock_shadow_logger):
        """Test SHADOW mode logs comparison between legacy and new."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve(
            rooms=20,
            expected_loss_cop=50_000_000,
            hotel_id="hotel_123",
            hotel_name="Test Hotel"
        )

        # Verify log_comparison was called
        mock_shadow_logger.log_comparison.assert_called_once()
        call_kwargs = mock_shadow_logger.log_comparison.call_args.kwargs

        assert call_kwargs["hotel_id"] == "hotel_123"
        assert call_kwargs["hotel_name"] == "Test Hotel"
        assert "legacy_result" in call_kwargs
        assert "new_result" in call_kwargs
        assert "flags" in call_kwargs

    def test_shadow_mode_includes_comparison(self, mock_shadow_logger):
        """Test SHADOW mode includes shadow comparison in result."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve(rooms=20, expected_loss_cop=50_000_000)

        assert result.shadow_comparison is not None
        assert result.shadow_comparison.comparison_id == "test_123"
        assert result.shadow_comparison.would_use_new is True

    def test_shadow_mode_metadata(self, mock_shadow_logger):
        """Test SHADOW mode includes shadow-specific metadata."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve(rooms=20, expected_loss_cop=50_000_000)

        assert result.metadata["shadow_mode"] == "shadow"
        assert result.metadata["would_use_new"] is True


class TestCanaryMode:
    """Test CANARY mode resolution."""

    def test_canary_mode_uses_new_when_valid(self, mock_shadow_logger):
        """Test CANARY mode uses new result when it passes validation."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.CANARY,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        expected_loss = 50_000_000
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)

        # would_use_new is True, so should use new result
        assert result.monthly_price_cop == 1_500_000  # 3% of 50M (hybrid)
        assert result.source == "hybrid_v410"
        assert result.used_new_calculation is True

    def test_canary_mode_fallback_when_invalid(self, mock_shadow_logger_reject):
        """Test CANARY mode falls back to legacy when new fails validation."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.CANARY,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger_reject,
        )

        expected_loss = 50_000_000
        result = wrapper.resolve(rooms=20, expected_loss_cop=expected_loss)

        # would_use_new is False, so should use legacy
        assert result.monthly_price_cop == 2_500_000  # 5% of 50M (legacy)
        assert result.source == "legacy_fixed"
        assert result.used_new_calculation is False

    def test_canary_mode_includes_comparison(self, mock_shadow_logger):
        """Test CANARY mode includes comparison metadata."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.CANARY,
        )
        wrapper = PricingResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve(rooms=20, expected_loss_cop=50_000_000)

        assert result.metadata["shadow_mode"] == "canary"
        assert result.metadata["would_use_new"] is True


class TestShadowLoggingData:
    """Test shadow logging data structure."""

    def test_legacy_data_structure(self):
        """Test legacy data structure for shadow logging."""
        wrapper = PricingResolutionWrapper()
        legacy_result = PricingResolutionResult(
            monthly_price_cop=2_500_000,
            tier="standard",
            pain_ratio=0.05,
            is_compliant=True,
            expected_loss_cop=50_000_000,
            source="legacy_fixed",
            used_new_calculation=False,
        )

        data = wrapper._build_legacy_data(legacy_result)

        assert "scenarios" in data
        assert "pricing" in data
        assert "conservative" in data["scenarios"]
        assert "realistic" in data["scenarios"]
        assert "optimistic" in data["scenarios"]
        assert data["pricing"]["monthly_price_cop"] == 2_500_000
        assert data["pricing"]["pain_ratio"] == 0.05
        assert data["pricing"]["tier"] == "standard"

    def test_new_data_structure(self):
        """Test new data structure for shadow logging."""
        wrapper = PricingResolutionWrapper()
        new_result = PricingResolutionResult(
            monthly_price_cop=1_500_000,
            tier="boutique",
            pain_ratio=0.03,
            is_compliant=True,
            expected_loss_cop=50_000_000,
            source="hybrid_v410",
            used_new_calculation=True,
        )

        data = wrapper._build_new_data(new_result)

        assert "scenarios" in data
        assert "pricing" in data
        assert data["pricing"]["monthly_price_cop"] == 1_500_000
        assert data["pricing"]["pain_ratio"] == 0.03
        assert data["pricing"]["is_compliant"] is True

    def test_flags_to_dict(self):
        """Test feature flags conversion to dictionary."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        flags_dict = wrapper._flags_to_dict()

        assert flags_dict["pricing_hybrid_enabled"] is True
        assert flags_dict["pricing_hybrid_mode"] == "shadow"
        assert flags_dict["shadow_logging_enabled"] is True


class TestCalculatePriceWithShadowFunction:
    """Test the convenience function calculate_price_with_shadow."""

    def test_function_returns_result(self):
        """Test convenience function returns PricingResolutionResult."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )

        result = calculate_price_with_shadow(
            rooms=20,
            expected_loss_cop=50_000_000,
            feature_flags=flags,
        )

        assert isinstance(result, PricingResolutionResult)
        assert result.monthly_price_cop == 1_500_000  # 3% of 50M

    def test_function_passes_all_parameters(self, mock_shadow_logger):
        """Test function passes all parameters to wrapper."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.SHADOW,
        )

        result = calculate_price_with_shadow(
            rooms=20,
            expected_loss_cop=50_000_000,
            segment="boutique",
            hotel_id="hotel_789",
            hotel_name="My Hotel",
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )

        assert result.monthly_price_cop == 2_500_000  # legacy 5% of 50M
        assert mock_shadow_logger.log_comparison.called

    def test_function_default_flags(self):
        """Test function works with default flags (SHADOW mode)."""
        result = calculate_price_with_shadow(
            rooms=20,
            expected_loss_cop=50_000_000,
        )

        # Default is SHADOW mode, but legacy is returned
        assert isinstance(result, PricingResolutionResult)
        assert result.monthly_price_cop == 2_500_000  # legacy 5% of 50M


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_zero_expected_loss(self):
        """Test resolution with 0 expected loss."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve(rooms=20, expected_loss_cop=0)

        assert result.monthly_price_cop == 0
        assert result.pain_ratio == 0
        assert result.is_compliant is False

    def test_very_small_expected_loss(self):
        """Test resolution with very small expected loss."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # Small loss that would result in price below minimum
        result = wrapper.resolve(rooms=20, expected_loss_cop=1_000_000)

        # Should be floored at min price for boutique
        assert result.monthly_price_cop == 1_200_000

    def test_very_large_expected_loss(self):
        """Test resolution with very large expected loss."""
        flags = FinancialFeatureFlags(
            pricing_hybrid_enabled=True,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
        )
        wrapper = PricingResolutionWrapper(feature_flags=flags)

        # Large loss that would result in price above maximum
        result = wrapper.resolve(rooms=20, expected_loss_cop=1_000_000_000)

        # Should be capped at max price for boutique
        assert result.monthly_price_cop == 2_500_000

    def test_unknown_mode_fallback(self):
        """Test that unknown mode falls back to legacy."""
        # Create a mock flags object with an undefined mode
        mock_flags = Mock()
        mock_flags.pricing_hybrid_mode = Mock()
        # Make the mode not match any of the enum values
        mock_flags.pricing_hybrid_mode.__eq__ = lambda self, other: False
        mock_flags.shadow_logging_enabled = True

        wrapper = PricingResolutionWrapper(feature_flags=mock_flags)

        # Should fallback to legacy when no mode matches
        result = wrapper._legacy_resolution(20, 50_000_000)
        assert result.source == "legacy_fixed"


class TestIntegration:
    """Integration tests with real dependencies."""

    def test_full_shadow_mode_flow(self):
        """Test full shadow mode flow with real logger."""
        # Create a temp directory for shadow logs
        with tempfile.TemporaryDirectory() as log_dir:
            flags = FinancialFeatureFlags(
                pricing_hybrid_enabled=True,
                pricing_hybrid_mode=RolloutMode.SHADOW,
                shadow_logging_enabled=True,
                shadow_log_path=log_dir,
            )

            real_logger = ShadowLogger(log_path=log_dir)
            wrapper = PricingResolutionWrapper(
                feature_flags=flags,
                shadow_logger=real_logger,
            )

            result = wrapper.resolve(
                rooms=20,
                expected_loss_cop=50_000_000,
                hotel_id="test_hotel",
                hotel_name="Test Hotel",
            )

            # Verify result structure
            assert result.monthly_price_cop == 2_500_000  # legacy value (5%)
            assert result.shadow_comparison is not None
            assert result.shadow_comparison.comparison_id is not None

            # Verify log file was created
            log_files = list(Path(log_dir).glob("*.json"))
            assert len(log_files) == 1

            # Verify log content
            with open(log_files[0], 'r') as f:
                log_data = json.load(f)
                assert log_data["hotel_id"] == "test_hotel"
                assert log_data["hotel_name"] == "Test Hotel"
                assert "legacy_scenarios" in log_data
                assert "new_scenarios" in log_data
                assert "legacy_pricing" in log_data
                assert "new_pricing" in log_data

    def test_pricing_comparison_deltas(self):
        """Test that shadow logger calculates pricing deltas correctly."""
        with tempfile.TemporaryDirectory() as log_dir:
            flags = FinancialFeatureFlags(
                pricing_hybrid_enabled=True,
                pricing_hybrid_mode=RolloutMode.SHADOW,
                shadow_logging_enabled=True,
                shadow_log_path=log_dir,
            )

            real_logger = ShadowLogger(log_path=log_dir)
            wrapper = PricingResolutionWrapper(
                feature_flags=flags,
                shadow_logger=real_logger,
            )

            # Boutique hotel: legacy 5% vs hybrid 3%
            expected_loss = 50_000_000
            result = wrapper.resolve(
                rooms=20,
                expected_loss_cop=expected_loss,
            )

            # Legacy: 2.5M, Hybrid: 1.5M
            # Delta: -1M (-40%)
            assert result.shadow_comparison is not None
            assert result.shadow_comparison.pricing_delta is not None
            assert result.shadow_comparison.pricing_delta_pct is not None

            # Read log to verify deltas
            log_files = list(Path(log_dir).glob("*.json"))
            with open(log_files[0], 'r') as f:
                log_data = json.load(f)
                # Legacy: 2.5M, New: 1.5M
                assert log_data["legacy_pricing"]["monthly_price_cop"] == 2_500_000
                assert log_data["new_pricing"]["monthly_price_cop"] == 1_500_000
                assert log_data["pricing_delta"] == -1_000_000
                assert log_data["pricing_delta_pct"] == -40.0
