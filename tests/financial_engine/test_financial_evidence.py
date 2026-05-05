"""Tests para modules.financial_engine.financial_evidence (FIN-1A).

8 tests que validan el modelo de metadata epistémica.
"""

import pytest
from modules.financial_engine.financial_evidence import (
    EpistemicStatus,
    PrecisionTier,
    FieldEvidence,
    FinancialEvidence,
    build_financial_evidence,
    SOURCE_TO_EPISTEMIC,
)


class TestFieldEvidence:
    """Tests para FieldEvidence dataclass."""

    def test_field_evidence_measured_can_show_exact(self):
        """MEASURED con can_show_exact=True."""
        fe = FieldEvidence(
            value=350000.0,
            source="user_provided",
            epistemic_status=EpistemicStatus.MEASURED,
            precision="exact",
            can_show_exact=True,
        )
        assert fe.value == 350000.0
        assert fe.epistemic_status == EpistemicStatus.MEASURED
        assert fe.can_show_exact is True
        assert fe.precision == "exact"

    def test_field_evidence_defaulted_cannot_show_exact(self):
        """DEFAULTED con can_show_exact=False."""
        fe = FieldEvidence(
            value=300000.0,
            source="legacy_hardcode",
            epistemic_status=EpistemicStatus.DEFAULTED,
            precision="range",
            can_show_exact=False,
        )
        assert fe.value == 300000.0
        assert fe.epistemic_status == EpistemicStatus.DEFAULTED
        assert fe.can_show_exact is False
        assert fe.precision == "range"

    def test_field_evidence_to_dict(self):
        """FieldEvidence serializa correctamente a dict."""
        fe = FieldEvidence(
            value=400000.0,
            source="benchmarking_2026:eje_cafetero:boutique_10_25",
            epistemic_status=EpistemicStatus.REGIONAL_BENCHMARK,
            precision="range",
            can_show_exact=False,
        )
        d = fe.to_dict()
        assert d["value"] == 400000.0
        assert d["source"] == "benchmarking_2026:eje_cafetero:boutique_10_25"
        assert d["epistemic_status"] == "regional_benchmark"
        assert d["precision"] == "range"
        assert d["can_show_exact"] is False


class TestPrecisionTier:
    """Tests para PrecisionTier determination."""

    def test_precision_tier_a_all_measured(self):
        """Tier A cuando todo es MEASURED."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="user_provided",
            occupancy_rate=0.75, occupancy_source="user_provided",
            direct_channel_pct=0.30, channel_source="user_provided",
        )
        assert fe.precision_tier == PrecisionTier.A

    def test_precision_tier_b_regional_benchmark(self):
        """Tier B con regional_benchmark presente."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="regional_v410",
            occupancy_rate=0.75, occupancy_source="user_provided",
            direct_channel_pct=0.30, channel_source="user_provided",
        )
        assert fe.precision_tier == PrecisionTier.B

    def test_precision_tier_c_has_defaulted(self):
        """Tier C cuando hay DEFAULTED."""
        fe = build_financial_evidence(
            adr_cop=300000.0, adr_source="legacy_hardcode",
            occupancy_rate=0.70, occupancy_source="web_scraping",
            direct_channel_pct=0.25, channel_source="user_provided",
        )
        assert fe.precision_tier == PrecisionTier.C

    def test_precision_tier_c_has_simulated(self):
        """Tier C cuando hay SIMULATED."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="user_provided",
            occupancy_rate=0.70, occupancy_source="user_provided",
            direct_channel_pct=0.25, channel_source="legacy_hardcode",
        )
        # legacy_hardcode -> DEFAULTED -> Tier C
        assert fe.precision_tier == PrecisionTier.C


class TestCanShowExactMoney:
    """Tests para can_show_exact_money property."""

    def test_can_show_exact_money_true(self):
        """True cuando todo es MEASURED u OBSERVED."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="user_provided",
            occupancy_rate=0.75, occupancy_source="web_scraping",
            direct_channel_pct=0.30, channel_source="user_provided",
        )
        assert fe.can_show_exact_money is True

    def test_can_show_exact_money_false_with_defaulted(self):
        """False con DEFAULTED presente."""
        fe = build_financial_evidence(
            adr_cop=300000.0, adr_source="legacy_hardcode",
            occupancy_rate=0.70, occupancy_source="user_provided",
            direct_channel_pct=0.25, channel_source="user_provided",
        )
        assert fe.can_show_exact_money is False

    def test_can_show_exact_money_false_with_simulated(self):
        """False con SIMULATED presente."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="user_provided",
            occupancy_rate=0.70, occupancy_source="user_provided",
            direct_channel_pct=0.25, channel_source="legacy_hardcode",
        )
        assert fe.can_show_exact_money is False


class TestBuildFinancialEvidence:
    """Tests para build_financial_evidence factory."""

    def test_build_financial_evidence_maps_sources_correctly(self):
        """Mapeo de source strings a EpistemicStatus correcto."""
        # user_provided -> MEASURED
        fe_up = build_financial_evidence(
            350000.0, "user_provided", 0.75, "user_provided", 0.30, "user_provided"
        )
        assert fe_up.adr_cop.epistemic_status == EpistemicStatus.MEASURED
        assert fe_up.occupancy_rate.epistemic_status == EpistemicStatus.MEASURED
        assert fe_up.direct_channel_percentage.epistemic_status == EpistemicStatus.MEASURED

        # web_scraping -> OBSERVED
        fe_ws = build_financial_evidence(
            350000.0, "web_scraping", 0.75, "web_scraping", 0.30, "web_scraping"
        )
        assert fe_ws.adr_cop.epistemic_status == EpistemicStatus.OBSERVED

        # regional_v410 -> REGIONAL_BENCHMARK
        fe_rb = build_financial_evidence(
            350000.0, "regional_v410", 0.75, "regional_v410", 0.30, "regional_v410"
        )
        assert fe_rb.adr_cop.epistemic_status == EpistemicStatus.REGIONAL_BENCHMARK

        # legacy_hardcode -> DEFAULTED
        fe_lh = build_financial_evidence(
            300000.0, "legacy_hardcode", 0.70, "legacy_hardcode", 0.25, "legacy_hardcode"
        )
        assert fe_lh.adr_cop.epistemic_status == EpistemicStatus.DEFAULTED

    def test_build_financial_evidence_unknown_defaults_to_defaulted(self):
        """Source 'unknown' mapea a DEFAULTED."""
        fe = build_financial_evidence(
            300000.0, "unknown", 0.70, "unknown", 0.25, "unknown"
        )
        assert fe.adr_cop.epistemic_status == EpistemicStatus.DEFAULTED
        assert fe.occupancy_rate.epistemic_status == EpistemicStatus.DEFAULTED

    def test_build_financial_evidence_ota_defaults_to_industry_standard(self):
        """OTA commission usa industry_standard por defecto."""
        fe = build_financial_evidence(
            350000.0, "user_provided", 0.75, "user_provided", 0.30, "user_provided"
        )
        assert fe.ota_commission_rate.value == 0.15
        assert fe.ota_commission_rate.source == "industry_standard"
        assert fe.ota_commission_rate.epistemic_status == EpistemicStatus.DEFAULTED
        assert fe.ota_commission_rate.can_show_exact is False

    def test_build_financial_evidence_to_dict_complete(self):
        """to_dict() incluye todos los campos."""
        fe = build_financial_evidence(
            adr_cop=350000.0, adr_source="user_provided",
            occupancy_rate=0.75, occupancy_source="user_provided",
            direct_channel_pct=0.30, channel_source="user_provided",
        )
        d = fe.to_dict()
        assert "adr_cop" in d
        assert "occupancy_rate" in d
        assert "direct_channel_percentage" in d
        assert "ota_commission_rate" in d
        assert "financial_precision_tier" in d
        assert "can_show_exact_money" in d
        assert d["financial_precision_tier"] == "A"
        assert d["can_show_exact_money"] is True
