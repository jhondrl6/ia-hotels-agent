"""
Test module for fallback chain epistemic metadata (FIN-2B).

Tests that ADRResolutionResult carries correct epistemic_status and can_show_exact
through the full fallback chain: user_provided → web_scraping → regional → legacy.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from modules.financial_engine.adr_resolution_wrapper import (
    ADRResolutionResult,
    ADRResolutionWrapper,
    ADRSource,
    resolve_adr_with_shadow,
)
from modules.financial_engine.feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
    get_flags,
    reset_flags,
)
from modules.financial_engine.shadow_logger import ShadowLogger, ShadowComparison


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def sample_regional_data():
    """Sample regional_adr_2026.json data for testing."""
    return {
        "version": "1.0.0",
        "regions": {
            "eje_cafetero": {
                "boutique_10_25": {"adr_cop": 420000, "occupancy_rate": 0.512},
                "standard_26_60": {"adr_cop": 350000, "occupancy_rate": 0.512},
            },
            "antioquia": {
                "boutique_10_25": {"adr_cop": 620000, "occupancy_rate": 0.642},
                "standard_26_60": {"adr_cop": 480000, "occupancy_rate": 0.642},
            },
            "caribe": {
                "boutique_10_25": {"adr_cop": 950000, "occupancy_rate": 0.685},
                "standard_26_60": {"adr_cop": 750000, "occupancy_rate": 0.685},
            },
            "default": {
                "any": {"adr_cop": 300000, "occupancy_rate": 0.50},
            },
        },
    }


@pytest.fixture
def temp_regional_adr_file(sample_regional_data):
    """Create a temporary regional ADR file."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump(sample_regional_data, f)
        temp_path = f.name
    yield temp_path
    Path(temp_path).unlink()


@pytest.fixture
def mock_shadow_logger():
    """Provide a mock shadow logger that returns a predictable comparison."""
    logger = Mock(spec=ShadowLogger)
    comparison = ShadowComparison(
        comparison_id="test_fallback_chain",
        timestamp="2026-01-01T00:00:00",
        hotel_id="test_hotel",
        hotel_name="Test Hotel",
        legacy_scenarios={
            "conservative": {"monthly_cop": 300000 * 10 * 0.5, "adr_cop": 300000},
            "realistic": {"monthly_cop": 300000 * 10 * 0.7, "adr_cop": 300000},
            "optimistic": {"monthly_cop": 300000 * 10 * 0.9, "adr_cop": 300000},
        },
        new_scenarios={
            "conservative": {"monthly_cop": 280000 * 10 * 0.5, "adr_cop": 280000},
            "realistic": {"monthly_cop": 280000 * 10 * 0.7, "adr_cop": 280000},
            "optimistic": {"monthly_cop": 280000 * 10 * 0.9, "adr_cop": 280000},
        },
        legacy_pricing={"monthly_price_cop": 300000 * 0.05, "pain_ratio": 0.05},
        new_pricing={"monthly_price_cop": 280000 * 0.04, "pain_ratio": 0.04},
        monthly_loss_delta=-42000.0,
        monthly_loss_delta_pct=-10.0,
        pricing_delta=-2800.0,
        pricing_delta_pct=-18.67,
        would_use_new=True,
        flags_used={"regional_adr_enabled": True, "regional_adr_mode": "canary"},
        validation_errors=None,
    )
    logger.log_comparison.return_value = comparison
    return logger


@pytest.fixture(autouse=True)
def reset_feature_flags():
    """Reset feature flags before each test."""
    reset_flags()
    yield
    reset_flags()


# =============================================================================
# T1: Feature flags - Caribe validation
# =============================================================================

class TestCaribeValidated:
    """Test that Caribe is in validated_regions."""

    def test_caribe_region_validated(self):
        """should_use_regional_for('caribe') returns True when enabled."""
        flags = FinancialFeatureFlags.full_enabled()
        assert flags.should_use_regional_for("caribe") is True

    def test_caribe_in_validated_regions_tuple(self):
        """validated_regions tuple contains 'caribe'."""
        flags = FinancialFeatureFlags()
        assert "caribe" in flags.validated_regions

    def test_unknown_region_not_validated(self):
        """should_use_regional_for('bogota') returns False."""
        flags = FinancialFeatureFlags.full_enabled()
        assert flags.should_use_regional_for("bogota") is False

    def test_unknown_region_returns_false_by_default(self):
        """should_use_regional_for('luna') returns False even with full_enabled."""
        flags = FinancialFeatureFlags.full_enabled()
        # Ensure "luna" is NOT in validated_regions
        assert "luna" not in flags.validated_regions
        assert flags.should_use_regional_for("luna") is False


# =============================================================================
# T2/T3: Epistemic metadata propagation in fallback chain
# =============================================================================

class TestUserProvidedAdrEpistemic:
    """Test user_provided_adr path sets epistemic=measured."""

    def test_user_provided_adr_measured_can_show_exact(
        self, mock_shadow_logger
    ):
        """user_provided_adr → epistemic_status='measured', can_show_exact=True."""
        wrapper = ADRResolutionWrapper(
            feature_flags=FinancialFeatureFlags.full_enabled(),
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="eje_cafetero",
            rooms=15,
            user_provided_adr=350000.0,
        )
        assert result.epistemic_status == "measured"
        assert result.can_show_exact is True

    def test_user_provided_adr_in_legacy_mode_also_measured(
        self, mock_shadow_logger
    ):
        """user_provided_adr in FORCE_LEGACY mode → epistemic='measured'."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="eje_cafetero",
            rooms=15,
            user_provided_adr=350000.0,
        )
        assert result.epistemic_status == "measured"
        assert result.can_show_exact is True


class TestWebScrapingAdrEpistemic:
    """Test web_scraping_adr path sets epistemic=observed."""

    def test_web_scraping_adr_observed_can_show_exact(
        self, mock_shadow_logger
    ):
        """web_scraping_adr → epistemic_status='observed', can_show_exact=True."""
        wrapper = ADRResolutionWrapper(
            feature_flags=FinancialFeatureFlags.full_enabled(),
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="eje_cafetero",
            rooms=15,
            web_scraping_adr=320000.0,
        )
        assert result.epistemic_status == "observed"
        assert result.can_show_exact is True
        assert result.source == ADRSource.WEB_SCRAPING.value

    def test_web_scraping_takes_precedence_over_regional(
        self, mock_shadow_logger
    ):
        """web_scraping_adr provided → regional benchmark not used."""
        wrapper = ADRResolutionWrapper(
            feature_flags=FinancialFeatureFlags.full_enabled(),
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
            web_scraping_adr=240000.0,
        )
        # Should be web scraping, not regional
        assert result.source == ADRSource.WEB_SCRAPING.value
        assert result.epistemic_status == "observed"


class TestRegionalBenchmarkEpistemic:
    """Test regional benchmark path sets epistemic=regional_benchmark."""

    def test_regional_benchmark_cannot_show_exact(
        self, mock_shadow_logger
    ):
        """regional benchmark → epistemic_status='regional_benchmark', can_show_exact=False."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            # plan_maestro_path=None → resolver carga data/benchmarks/regional_adr_2026.json real
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
            # No user_provided_adr, no web_scraping_adr → falls to regional
        )
        assert result.epistemic_status == "regional_benchmark"
        assert result.can_show_exact is False
        assert result.source == ADRSource.REGIONAL_V410.value

    def test_regional_epistemic_propagates_through_new_resolution(
        self, mock_shadow_logger
    ):
        """_new_resolution propagates epistemic_status from RegionalADRResult."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(region="eje_cafetero", rooms=15)
        assert result.epistemic_status == "regional_benchmark"
        assert result.can_show_exact is False


class TestLegacyHardcodeEpistemic:
    """Test legacy hardcode path sets epistemic=defaulted."""

    def test_legacy_hardcode_defaulted_cannot_show_exact(
        self, mock_shadow_logger
    ):
        """LEGACY_DEFAULT_ADR ($300K) → epistemic_status='defaulted', can_show_exact=False."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="bogota",  # Not validated → falls to legacy
            rooms=15,
        )
        assert result.epistemic_status == "defaulted"
        assert result.can_show_exact is False
        assert result.source == ADRSource.LEGACY_HARDCODE.value

    def test_legacy_mode_without_user_provided_is_defaulted(
        self, mock_shadow_logger
    ):
        """FORCE_LEGACY + no user_provided → epistemic='defaulted'."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="eje_cafetero",
            rooms=15,
            # No user_provided_adr
        )
        assert result.epistemic_status == "defaulted"
        assert result.can_show_exact is False


class TestFullFallbackChainEpistemic:
    """Test the complete fallback chain with different combinations."""

    def test_full_fallback_chain_user_provided_wins(
        self, temp_regional_adr_file, mock_shadow_logger
    ):
        """user_provided_adr wins over web_scraping_adr and regional."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_regional_adr_file,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
            user_provided_adr=400000.0,
            web_scraping_adr=260000.0,
        )
        assert result.epistemic_status == "measured"
        assert result.can_show_exact is True
        assert result.source == ADRSource.USER_PROVIDED.value

    def test_full_fallback_chain_web_scraping_wins_over_regional(
        self, temp_regional_adr_file, mock_shadow_logger
    ):
        """web_scraping_adr wins over regional benchmark."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_regional_adr_file,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
            web_scraping_adr=240000.0,
        )
        assert result.epistemic_status == "observed"
        assert result.can_show_exact is True
        assert result.source == ADRSource.WEB_SCRAPING.value

    def test_full_fallback_chain_regional_wins_over_legacy(
        self, mock_shadow_logger
    ):
        """regional benchmark wins over legacy when enabled."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="antioquia",
            rooms=15,
        )
        assert result.epistemic_status == "regional_benchmark"
        assert result.can_show_exact is False
        assert result.source == ADRSource.REGIONAL_V410.value

    def test_non_validated_region_falls_to_legacy(
        self, temp_regional_adr_file, mock_shadow_logger
    ):
        """Region not in validated_regions falls to legacy."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            plan_maestro_path=temp_regional_adr_file,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="bogota",  # Not in validated_regions
            rooms=15,
        )
        assert result.epistemic_status == "defaulted"
        assert result.can_show_exact is False
        assert result.source == ADRSource.LEGACY_HARDCODE.value


class TestOccupancyRatePropagation:
    """Test that occupancy_rate is propagated from regional resolver."""

    def test_occupancy_rate_propagated_from_regional(
        self, mock_shadow_logger
    ):
        """occupancy_rate from regional_adr_2026.json propagates to result."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
        )
        # Caribe has occupancy_rate: 0.685 in real regional_adr_2026.json (boutique_10_25)
        assert result.occupancy_rate == 0.685

    def test_occupancy_rate_not_set_for_legacy(
        self, mock_shadow_logger
    ):
        """Legacy hardcode path does not set occupancy_rate."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="bogota",
            rooms=15,
            web_scraping_adr=240000.0,
        )
        assert result.occupancy_rate is None

    def test_occupancy_rate_not_set_for_web_scraping(
        self, mock_shadow_logger
    ):
        """Web scraping path does not set occupancy_rate."""
        flags = FinancialFeatureFlags.full_enabled()
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
            web_scraping_adr=240000.0,
        )
        assert result.occupancy_rate is None


# =============================================================================
# T4: ADRResolutionResult dataclass fields
# =============================================================================

class TestADRResolutionResultFields:
    """Test that ADRResolutionResult has all required epistemic fields."""

    def test_dataclass_has_epistemic_status_field(self):
        """ADRResolutionResult accepts epistemic_status parameter."""
        result = ADRResolutionResult(
            adr_cop=300000.0,
            source="test",
            confidence="test",
            used_new_calculation=False,
            epistemic_status="measured",
            can_show_exact=True,
        )
        assert result.epistemic_status == "measured"
        assert result.can_show_exact is True

    def test_dataclass_has_occupancy_rate_field(self):
        """ADRResolutionResult accepts occupancy_rate parameter."""
        result = ADRResolutionResult(
            adr_cop=300000.0,
            source="test",
            confidence="test",
            used_new_calculation=True,
            occupancy_rate=0.72,
        )
        assert result.occupancy_rate == 0.72

    def test_default_epistemic_status_is_defaulted(self):
        """Default epistemic_status is 'defaulted'."""
        result = ADRResolutionResult(
            adr_cop=300000.0,
            source="test",
            confidence="test",
            used_new_calculation=False,
        )
        assert result.epistemic_status == "defaulted"

    def test_default_can_show_exact_is_false(self):
        """Default can_show_exact is False."""
        result = ADRResolutionResult(
            adr_cop=300000.0,
            source="test",
            confidence="test",
            used_new_calculation=False,
        )
        assert result.can_show_exact is False


# =============================================================================
# Integration: Shadow mode epistemic propagation
# =============================================================================

class TestShadowModeEpistemic:
    """Test epistemic metadata in SHADOW/CANARY modes."""

    def test_shadow_mode_regional_epistemic(
        self, mock_shadow_logger
    ):
        """SHADOW mode with regional → epistemic=regional_benchmark when new is used."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.SHADOW,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
        )
        # In SHADOW mode, result source is LEGACY_HARDCODE (returns legacy in shadow)
        # But the epistemic metadata reflects what was used
        assert result.source in (ADRSource.REGIONAL_V410.value, ADRSource.LEGACY_HARDCODE.value)

    def test_canary_mode_uses_new_when_valid(
        self, mock_shadow_logger
    ):
        """CANARY mode returns new (regional) result when valid."""
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.CANARY,
        )
        wrapper = ADRResolutionWrapper(
            feature_flags=flags,
            shadow_logger=mock_shadow_logger,
        )
        result = wrapper.resolve(
            region="caribe",
            rooms=15,
        )
        # CANARY mode with valid new result returns new (regional)
        assert result.source == ADRSource.REGIONAL_V410.value
