"""Tests para modules/financial_engine/no_defaults_validator precision tier (FIN-1B).

8 tests que validan classify_source(), determine_precision_tier() y PrecisionValidator.
"""

import pytest
from modules.financial_engine.no_defaults_validator import (
    classify_source,
    determine_precision_tier,
    NoDefaultsValidator,
    NoDefaultsValidationResult,
    SOURCE_EPISTEMIC_MAP,
    SUSPECT_SOURCES,
)
from modules.financial_engine.precision_validator import PrecisionValidator
from modules.financial_engine.financial_evidence import EpistemicStatus


class TestClassifySource:
    """Tests para classify_source()."""

    def test_classify_source_user_provided(self):
        """user_provided -> MEASURED."""
        assert classify_source("user_provided") == EpistemicStatus.MEASURED

    def test_classify_source_web_scraping(self):
        """web_scraping -> OBSERVED."""
        assert classify_source("web_scraping") == EpistemicStatus.OBSERVED

    def test_classify_source_regional_v410(self):
        """regional_v410 -> REGIONAL_BENCHMARK."""
        assert classify_source("regional_v410") == EpistemicStatus.REGIONAL_BENCHMARK

    def test_classify_source_legacy_hardcode(self):
        """legacy_hardcode -> DEFAULTED."""
        assert classify_source("legacy_hardcode") == EpistemicStatus.DEFAULTED


class TestDeterminePrecisionTier:
    """Tests para determine_precision_tier()."""

    def test_precision_tier_a_all_measured(self):
        """Todos MEASURED -> Tier A."""
        tier = determine_precision_tier(
            EpistemicStatus.MEASURED,
            EpistemicStatus.MEASURED,
            EpistemicStatus.MEASURED,
        )
        assert tier == "A"

    def test_precision_tier_c_with_defaulted(self):
        """Un DEFAULTED -> Tier C."""
        tier = determine_precision_tier(
            EpistemicStatus.MEASURED,
            EpistemicStatus.DEFAULTED,
            EpistemicStatus.MEASURED,
        )
        assert tier == "C"

    def test_precision_tier_b_with_regional(self):
        """REGIONAL_BENCHMARK sin DEFAULTED -> Tier B."""
        tier = determine_precision_tier(
            EpistemicStatus.MEASURED,
            EpistemicStatus.REGIONAL_BENCHMARK,
            EpistemicStatus.MEASURED,
        )
        assert tier == "B"

    def test_can_show_exact_true_all_measured(self):
        """Todos MEASURED/OBSERVED -> can_show_exact_money=True."""
        validator = NoDefaultsValidator()
        result = validator.validate(
            data={
                "adr_cop": 350000.0,
                "occupancy_rate": 0.75,
                "direct_channel_percentage": 0.40,
            },
            sources={
                "adr_cop": "user_provided",
                "occupancy_rate": "user_provided",
                "direct_channel_percentage": "user_provided",
            },
        )
        assert result.can_show_exact_money is True
        assert result.precision_tier == "A"


class TestPrecisionValidatorIntegration:
    """Integration tests para PrecisionValidator."""

    def test_precision_validator_all_user_provided(self):
        """Todos user_provided -> tier A, can_show_exact=True."""
        result = PrecisionValidator.validate(
            adr_cop=350000.0,
            adr_source="user_provided",
            occupancy_rate=0.75,
            occupancy_source="user_provided",
            direct_channel_pct=0.40,
            channel_source="user_provided",
        )
        assert result.can_calculate is True
        assert result.precision_tier == "A"
        assert result.can_show_exact_money is True
        assert result.field_epistemic["adr_cop"] == EpistemicStatus.MEASURED

    def test_precision_validator_with_defaulted(self):
        """Uno defaulted -> tier C, can_show_exact=False."""
        result = PrecisionValidator.validate(
            adr_cop=350000.0,
            adr_source="user_provided",
            occupancy_rate=0.75,
            occupancy_source="legacy_hardcode",
            direct_channel_pct=0.40,
            channel_source="user_provided",
        )
        assert result.precision_tier == "C"
        assert result.can_show_exact_money is False
        assert result.field_epistemic["occupancy_rate"] == EpistemicStatus.DEFAULTED

    def test_precision_validator_blocks_none_values(self):
        """Valor None genera ValidationBlock y can_calculate=False.

        Nota: precision_tier y can_show_exact_money se determinan por fuente,
        no por el valor. Un None con fuente MEASURED tiene tier A / can_show_exact=True
        (fuente confiable), pero can_calculate=False (valor ausente).
        """
        result = PrecisionValidator.validate(
            adr_cop=None,
            adr_source="user_provided",
            occupancy_rate=0.75,
            occupancy_source="user_provided",
            direct_channel_pct=0.40,
            channel_source="user_provided",
        )
        assert result.can_calculate is False
        assert len(result.blocks) > 0
        # Fuente es MEASURED -> tier A (calidad de fuente)
        assert result.precision_tier == "A"
