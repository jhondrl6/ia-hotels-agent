"""
Test module for adr_resolution_wrapper.py

Comprehensive tests for the ADRResolutionWrapper class and ADRResolutionResult dataclass,
covering all rollout modes (LEGACY, ACTIVE, SHADOW, CANARY) and integration with
feature flags, regional ADR resolver, and shadow logger.
"""

import pytest
import json
import tempfile
from pathlib import Path
from dataclasses import asdict
from unittest.mock import Mock, MagicMock, patch

from modules.financial_engine.adr_resolution_wrapper import (
    ADRResolutionResult,
    ADRResolutionWrapper,
    ADRSource,
    resolve_adr_with_shadow,
)
from modules.financial_engine.feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
)
from modules.financial_engine.shadow_logger import ShadowLogger, ShadowComparison


@pytest.fixture
def sample_plan_maestro_data():
    """Provide sample plan maestro data with multiple regions."""
    return {
        "regiones": {
            "coffee_axis": {
                "name": "Eje Cafetero",
                "adr_cop": 280000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 250000.0},
                    "standard_26_60": {"adr_cop": 300000.0},
                }
            },
            "bogota": {
                "name": "Bogotá",
                "adr_cop": 350000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 320000.0},
                    "standard_26_60": {"adr_cop": 380000.0},
                }
            },
            "default": {
                "name": "Default",
                "adr_cop": 300000.0,
                "segments": {
                    "boutique_10_25": {"adr_cop": 280000.0},
                    "standard_26_60": {"adr_cop": 320000.0},
                }
            }
        }
    }


@pytest.fixture
def temp_plan_maestro_file(sample_plan_maestro_data):
    """Provide a temporary plan maestro file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_plan_maestro_data, f)
        temp_path = f.name

    yield temp_path

    Path(temp_path).unlink()


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


class TestADRSource:
    """Test cases for ADRSource enum."""

    def test_adr_source_values(self):
        """Test ADRSource enum has correct values."""
        assert ADRSource.REGIONAL_V410.value == "regional_v410"
        assert ADRSource.LEGACY_HARDCODE.value == "legacy_hardcode"
        assert ADRSource.USER_PROVIDED.value == "user_provided"
        assert ADRSource.WEB_SCRAPING.value == "web_scraping"


class TestADRResolutionResult:
    """Test cases for ADRResolutionResult dataclass."""

    def test_basic_creation(self):
        """Test creating ADRResolutionResult with required fields."""
        result = ADRResolutionResult(
            adr_cop=250000.0,
            source="regional_v410",
            confidence="VERIFIED",
            used_new_calculation=True,
        )

        assert result.adr_cop == 250000.0
        assert result.source == "regional_v410"
        assert result.confidence == "VERIFIED"
        assert result.used_new_calculation is True
        assert result.shadow_comparison is None
        assert result.metadata is None

    def test_creation_with_shadow_comparison(self, mock_shadow_logger):
        """Test creating ADRResolutionResult with shadow comparison."""
        comparison = mock_shadow_logger.log_comparison.return_value
        result = ADRResolutionResult(
            adr_cop=300000.0,
            source="legacy_hardcode",
            confidence="ESTIMATED",
            used_new_calculation=False,
            shadow_comparison=comparison,
            metadata={"test": "data"},
        )

        assert result.shadow_comparison == comparison
        assert result.metadata == {"test": "data"}

    def test_creation_with_user_provided_source(self):
        """Test creating result with user_provided source."""
        result = ADRResolutionResult(
            adr_cop=350000.0,
            source="user_provided",
            confidence="VERIFIED",
            used_new_calculation=False,
        )

        assert result.source == "user_provided"
        assert result.adr_cop == 350000.0


class TestADRResolutionWrapperInitialization:
    """Test cases for wrapper initialization."""

    def test_default_initialization(self):
        """Test wrapper initializes with default dependencies."""
        wrapper = ADRResolutionWrapper()

        assert wrapper.flags is not None
        assert wrapper.LEGACY_DEFAULT_ADR == 300000.0
        assert wrapper._resolver is None

    def test_initialization_with_custom_flags(self):
        """Test wrapper initializes with custom feature flags."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(feature_flags=flags)

        assert wrapper.flags == flags
        assert wrapper.flags.regional_adr_enabled is True

    def test_initialization_with_custom_plan_path(self, temp_plan_maestro_file):
        """Test wrapper initializes with custom plan maestro path."""
        wrapper = ADRResolutionWrapper(plan_maestro_path=temp_plan_maestro_file)

        assert wrapper.plan_maestro_path == temp_plan_maestro_file

    def test_initialization_with_custom_shadow_logger(self, mock_shadow_logger):
        """Test wrapper initializes with custom shadow logger."""
        wrapper = ADRResolutionWrapper(shadow_logger=mock_shadow_logger)

        assert wrapper.shadow_logger == mock_shadow_logger

    def test_lazy_resolver_initialization(self, temp_plan_maestro_file):
        """Test resolver is lazily initialized."""
        wrapper = ADRResolutionWrapper(plan_maestro_path=temp_plan_maestro_file)

        assert wrapper._resolver is None

        resolver = wrapper._get_resolver()
        assert resolver is not None
        assert wrapper._resolver == resolver


class TestLegacyMode:
    """Test LEGACY mode resolution."""

    def test_legacy_mode_returns_hardcoded_adr(self):
        """Test LEGACY mode returns hardcoded 300000."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve("coffee_axis", 20)

        assert result.adr_cop == 300000.0
        assert result.source == "legacy_hardcode"
        assert result.confidence == "ESTIMATED"
        assert result.used_new_calculation is False
        assert result.shadow_comparison is None

    def test_legacy_mode_with_user_provided_adr(self):
        """Test LEGACY mode uses user provided ADR."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=450000.0)

        assert result.adr_cop == 450000.0
        assert result.source == "user_provided"
        assert result.used_new_calculation is False

    def test_legacy_mode_metadata(self):
        """Test LEGACY mode includes correct metadata."""
        flags = FinancialFeatureFlags(
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(feature_flags=flags)

        result = wrapper.resolve("any_region", 25, user_provided_adr=400000.0)

        assert result.metadata["user_provided_adr"] == 400000.0
        assert result.metadata["fallback_to_legacy"] is True


class TestActiveMode:
    """Test ACTIVE mode resolution."""

    def test_active_mode_uses_regional_resolver(self, temp_plan_maestro_file):
        """"Test ACTIVE mode uses new regional resolver."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("coffee_axis", 20)

        assert result.adr_cop == 250000.0  # boutique segment
        assert result.source == "regional_v410"
        assert result.used_new_calculation is True
        assert result.shadow_comparison is None

    def test_active_mode_different_regions(self, temp_plan_maestro_file):
        """Test ACTIVE mode with different regions."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        # Coffee axis boutique
        result = wrapper.resolve("coffee_axis", 15)
        assert result.adr_cop == 250000.0
        assert result.confidence == "ESTIMATED"  # no user_adr provided

        # Bogota standard
        result = wrapper.resolve("bogota", 45)
        assert result.adr_cop == 380000.0

    def test_active_mode_with_user_provided_adr(self, temp_plan_maestro_file):
        """Test ACTIVE mode with user provided ADR for confidence."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=255000.0)

        assert result.adr_cop == 250000.0
        assert result.confidence == "VERIFIED"
        assert result.metadata["user_provided_adr"] == 255000.0

    def test_active_mode_metadata(self, temp_plan_maestro_file):
        """Test ACTIVE mode includes comprehensive metadata."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("coffee_axis", 30)

        assert result.metadata["region"] == "coffee_axis"
        assert result.metadata["segment"] == "standard"
        assert result.metadata["is_default"] is False
        assert result.metadata["regional_source"] == "plan_maestro_v2.5"


class TestShadowMode:
    """Test SHADOW mode resolution."""

    def test_shadow_mode_returns_legacy(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test SHADOW mode returns legacy value but calculates both."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20, hotel_id="hotel_123")

        # Should return legacy (hardcoded) value
        assert result.adr_cop == 300000.0
        assert result.source == "legacy_hardcode"
        assert result.used_new_calculation is False

    def test_shadow_mode_logs_comparison(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test SHADOW mode logs comparison between legacy and new."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve(
            "coffee_axis", 20,
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

    def test_shadow_mode_includes_comparison(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test SHADOW mode includes shadow comparison in result."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20)

        assert result.shadow_comparison is not None
        assert result.shadow_comparison.comparison_id == "test_123"
        assert result.shadow_comparison.would_use_new is True

    def test_shadow_mode_metadata(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test SHADOW mode includes shadow-specific metadata."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20)

        assert result.metadata["shadow_mode"] == "shadow"
        assert result.metadata["would_use_new"] is True

    def test_shadow_mode_with_user_provided_adr(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test SHADOW mode uses user provided ADR in legacy."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=400000.0)

        # Legacy uses user_provided_adr
        assert result.adr_cop == 400000.0
        assert result.source == "user_provided"


class TestCanaryMode:
    """Test CANARY mode resolution."""

    def test_canary_mode_uses_new_when_valid(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test CANARY mode uses new result when it passes validation."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.CANARY,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20)

        # would_use_new is True, so should use new result
        assert result.adr_cop == 250000.0  # new regional value
        assert result.source == "regional_v410"
        assert result.used_new_calculation is True

    def test_canary_mode_fallback_when_invalid(self, temp_plan_maestro_file):
        """Test CANARY mode falls back to legacy when new fails validation."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.CANARY,
            validated_regions=("coffee_axis", "bogota", "default"),
        )

        # Create a mock logger that rejects the new result
        mock_logger = Mock(spec=ShadowLogger)
        comparison = ShadowComparison(
            comparison_id="test_456",
            timestamp="2024-01-01T00:00:00",
            would_use_new=False,
            rejection_reason="Validation failed",
        )
        mock_logger.log_comparison.return_value = comparison

        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_logger,
        )

        result = wrapper.resolve("coffee_axis", 20)

        # would_use_new is False, so should use legacy
        assert result.adr_cop == 300000.0  # legacy value
        assert result.source == "legacy_hardcode"
        assert result.used_new_calculation is False

    def test_canary_mode_includes_comparison(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test CANARY mode includes comparison metadata."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.CANARY,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        result = wrapper.resolve("coffee_axis", 20)

        assert result.metadata["shadow_mode"] == "canary"
        assert result.metadata["would_use_new"] is True


class TestShadowLoggingData:
    """Test shadow logging data structure."""

    def test_legacy_data_structure(self):
        """Test legacy data structure for shadow logging."""
        wrapper = ADRResolutionWrapper()
        legacy_result = ADRResolutionResult(
            adr_cop=300000.0,
            source="legacy_hardcode",
            confidence="ESTIMATED",
            used_new_calculation=False,
        )

        data = wrapper._build_legacy_data(legacy_result, rooms=20)

        assert "scenarios" in data
        assert "pricing" in data
        assert "conservative" in data["scenarios"]
        assert "realistic" in data["scenarios"]
        assert "optimistic" in data["scenarios"]
        assert data["scenarios"]["conservative"]["adr_cop"] == 300000.0

    def test_new_data_structure(self, temp_plan_maestro_file):
        """Test new data structure for shadow logging."""
        wrapper = ADRResolutionWrapper(plan_maestro_path=temp_plan_maestro_file)
        new_result = ADRResolutionResult(
            adr_cop=250000.0,
            source="regional_v410",
            confidence="VERIFIED",
            used_new_calculation=True,
        )

        data = wrapper._build_new_data(new_result, region="coffee_axis", rooms=20)

        assert "scenarios" in data
        assert "pricing" in data
        assert data["scenarios"]["realistic"]["adr_cop"] == 250000.0
        assert "monthly_price_cop" in data["pricing"]

    def test_flags_to_dict(self):
        """Test feature flags conversion to dictionary."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            shadow_logging_enabled=True,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(feature_flags=flags)

        flags_dict = wrapper._flags_to_dict()

        assert flags_dict["regional_adr_enabled"] is True
        assert flags_dict["regional_adr_mode"] == "shadow"
        assert flags_dict["shadow_logging_enabled"] is True


class TestResolveADRWithShadowFunction:
    """Test the convenience function resolve_adr_with_shadow."""

    def test_function_returns_result(self, temp_plan_maestro_file):
        """Test convenience function returns ADRResolutionResult."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )

        result = resolve_adr_with_shadow(
            region="coffee_axis",
            rooms=20,
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        assert isinstance(result, ADRResolutionResult)
        assert result.adr_cop == 250000.0

    def test_function_passes_all_parameters(self, temp_plan_maestro_file, mock_shadow_logger):
        """Test function passes all parameters to wrapper."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
            validated_regions=("coffee_axis", "bogota", "default"),
        )

        result = resolve_adr_with_shadow(
            region="coffee_axis",
            rooms=20,
            user_provided_adr=260000.0,
            hotel_id="hotel_789",
            hotel_name="My Hotel",
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
            shadow_logger=mock_shadow_logger,
        )

        assert result.adr_cop == 260000.0  # user_provided in legacy mode
        assert mock_shadow_logger.log_comparison.called

    def test_function_default_flags(self, temp_plan_maestro_file):
        """Test function works with default flags (LEGACY mode)."""
        result = resolve_adr_with_shadow(
            region="coffee_axis",
            rooms=20,
            plan_maestro_path=temp_plan_maestro_file,
        )

        # Default is SHADOW mode, but legacy is returned
        assert isinstance(result, ADRResolutionResult)
        assert result.adr_cop == 300000.0  # legacy default


class TestEdgeCases:
    """Test edge cases and error handling."""

    def test_undefined_mode_in_match(self, temp_plan_maestro_file):
        """Test that undefined enum value is handled gracefully."""
        # Create a mock flags object with a mock mode that won't match any case
        mock_flags = Mock()
        mock_flags.regional_adr_mode = Mock()
        # Make the mode not match any of the enum values
        mock_flags.regional_adr_mode.__eq__ = lambda self, other: False
        mock_flags.shadow_logging_enabled = True

        wrapper = ADRResolutionWrapper(feature_flags=mock_flags)

        # Should fallback to legacy when no mode matches
        result = wrapper._legacy_resolution(None)
        assert result.adr_cop == 300000.0

    def test_zero_rooms(self, temp_plan_maestro_file):
        """Test resolution with 0 rooms."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("coffee_axis", 0)

        # 0 rooms is boutique segment (<= 25)
        assert result.metadata["segment"] == "boutique"
        assert result.adr_cop == 250000.0

    def test_large_rooms_count(self, temp_plan_maestro_file):
        """Test resolution with large room count."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("coffee_axis", 100)

        # 100 rooms is large segment (> 60)
        assert result.metadata["segment"] == "large"
        assert result.adr_cop == 280000.0  # region average

    def test_unknown_region(self, temp_plan_maestro_file):
        """"Test resolution with unknown region falls back to legacy."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        result = wrapper.resolve("unknown_region", 30)

        # Region not in validated_regions -> falls back to legacy
        assert result.adr_cop == 300000.0
        assert result.source == "legacy_hardcode"
        assert result.used_new_calculation is False

    def test_missing_plan_maestro_file(self):
        """Test resolution when plan maestro file is missing."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path="/nonexistent/file.json",
        )

        result = wrapper.resolve("coffee_axis", 20)

        # Should fall back to default 300000
        assert result.adr_cop == 300000.0
        assert result.confidence == "ESTIMATED"


class TestIntegration:
    """Integration tests with real dependencies."""

    def test_full_shadow_mode_flow(self, temp_plan_maestro_file):
        """Test full shadow mode flow with real logger."""
        import tempfile
        import json

        # Create a temp directory for shadow logs
        with tempfile.TemporaryDirectory() as log_dir:
            flags = FinancialFeatureFlags(
                regional_adr_enabled=True,
                regional_adr_mode=RolloutMode.SHADOW,
                shadow_logging_enabled=True,
                shadow_log_path=log_dir,
                validated_regions=("coffee_axis", "bogota", "default"),
            )

            real_logger = ShadowLogger(log_path=log_dir)
            wrapper = ADRResolutionWrapper(
                feature_flags=flags,
                plan_maestro_path=temp_plan_maestro_file,
                shadow_logger=real_logger,
            )

            result = wrapper.resolve(
                "coffee_axis",
                20,
                hotel_id="test_hotel",
                hotel_name="Test Hotel",
            )

            # Verify result structure
            assert result.adr_cop == 300000.0  # legacy value
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

    def test_confidence_levels_integration(self, temp_plan_maestro_file):
        """Test confidence levels in integration."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
            validated_regions=("coffee_axis", "bogota", "default"),
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_plan_maestro_file,
        )

        # VERIFIED: within 20%
        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=260000.0)
        assert result.confidence == "VERIFIED"

        # ESTIMATED: within 20-40%
        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=320000.0)
        assert result.confidence == "ESTIMATED"

        # CONFLICT: > 40%
        result = wrapper.resolve("coffee_axis", 20, user_provided_adr=450000.0)
        assert result.confidence == "CONFLICT"


class TestWebScrapingADR:
    """Test cases for web_scraping_adr parameter in ADR resolution."""

    def test_web_scraping_as_source(self):
        """Test WEB_SCRAPING as source when no user_provided."""
        wrapper = ADRResolutionWrapper()
        result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=280000)
        assert result.source == "web_scraping"
        assert result.confidence == "medium"
        assert result.adr_cop == 280000
        assert result.metadata["fallback_chain"] == "web_scraping"

    def test_user_provided_priority_over_scraping(self):
        """Test user_provided has priority over scraping."""
        wrapper = ADRResolutionWrapper()
        result = wrapper.resolve(
            region="eje_cafetero",
            user_provided_adr=300000,
            web_scraping_adr=280000,
        )
        assert result.source == "user_provided"
        assert result.adr_cop == 300000

    def test_full_fallback_chain(self):
        """Test fallback chain works without scraping or user."""
        wrapper = ADRResolutionWrapper()
        # Sin user_provided ni scraping → va a regional/legacy
        result = wrapper.resolve(region="eje_cafetero")
        assert result.source in ("regional_v410", "legacy_hardcode")
        assert result.adr_cop > 0

    def test_scraping_none_no_crash(self):
        """Test scraping=None does not crash."""
        wrapper = ADRResolutionWrapper()
        result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=None)
        # Debe caer a regional/legacy sin error
        assert result.adr_cop > 0
        assert result.source != "web_scraping"

    def test_scraping_zero_ignored(self):
        """Test scraping=0 is not used as source."""
        wrapper = ADRResolutionWrapper()
        result = wrapper.resolve(region="eje_cafetero", web_scraping_adr=0)
        assert result.source != "web_scraping"
        assert result.adr_cop > 0
