"""Tests for FIN-4B: Financial Engine Pipeline Integration.

8 tests covering GAP-1 through GAP-4 fixes:
GAP-1: Case-insensitive region matching for regional ADR
GAP-2: opportunity_scores in v4_complete_report.json
GAP-3: channel_context in v4_complete_report.json
GAP-4: precision_tier in financial_scenarios.json
"""

import os
import sys
import pytest

_PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "..")
)
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)


# ---------------------------------------------------------------------------
# GAP-1: Case-insensitive regional ADR
# ---------------------------------------------------------------------------

class TestGAP1RegionalADRCaseInsensitive:
    """GAP-1: ADR regional usa feature flags y es case-insensitive."""

    def test_should_use_regional_for_title_case(self):
        """\"Eje Cafetero\" debe matchear contra validated_regions \"eje_cafetero\"."""
        from modules.financial_engine.feature_flags import FinancialFeatureFlags
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            validated_regions=("eje_cafetero", "antioquia", "caribe"),
        )
        # Title case (como viene del DOM)
        assert flags.should_use_regional_for("Eje Cafetero") is True
        # Lowercase
        assert flags.should_use_regional_for("eje_cafetero") is True
        # Antiguo bug: espacio vs underscore
        assert flags.should_use_regional_for("Eje  Cafetero") is False

    def test_adr_not_300k_legacy_with_flags_and_title_case(self):
        """Con FINANCIAL_REGIONAL_ADR_ENABLED=true, title case region usa ADR regional."""
        os.environ["FINANCIAL_REGIONAL_ADR_ENABLED"] = "true"
        os.environ["FINANCIAL_REGIONAL_ADR_MODE"] = "active"
        try:
            from modules.financial_engine.adr_resolution_wrapper import ADRResolutionWrapper
            from modules.financial_engine.feature_flags import FinancialFeatureFlags

            flags = FinancialFeatureFlags.from_env()
            wrapper = ADRResolutionWrapper(feature_flags=flags)

            result = wrapper.resolve(region="Eje Cafetero")
            # Bug original: source=legacy_hardcode, ADR=300000
            # Fix: source=regional_v410
            assert result.source == "regional_v410", (
                f"Expected regional_v410, got {result.source}"
            )
        finally:
            os.environ.pop("FINANCIAL_REGIONAL_ADR_ENABLED", None)
            os.environ.pop("FINANCIAL_REGIONAL_ADR_MODE", None)


# ---------------------------------------------------------------------------
# GAP-2: opportunity_scores en v4_complete_report.json
# ---------------------------------------------------------------------------

class TestGAP2OpportunityScoresInReport:
    """GAP-2: v4_complete_report acepta e incluye opportunity_scores."""

    def test_compute_opportunity_scores_returns_list_or_none(self):
        """_compute_opportunity_scores es accesible y retorna lista o None."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        gen = V4DiagnosticGenerator()
        assert hasattr(gen, "_compute_opportunity_scores")
        # Sin audit_result -> retorna None
        result = gen._compute_opportunity_scores(None, None)
        assert result is None

    def test_opportunity_scores_have_channel_multiplier_field(self):
        """Cada opportunity_score incluye channel_multiplier y channel_reason."""
        from modules.financial_engine.opportunity_scorer import OpportunityScorer

        scorer = OpportunityScorer()
        brechas = [{"id": "whatsapp_conflict", "type": "whatsapp_conflict", "name": "WhatsApp conflict"}]
        channel_context = {
            "dominant_channel": "whatsapp",
            "confidence": "medium",
            "channel_weights": {"whatsapp": 1.5, "gbp_local": 1.0, "iao_schema": 1.0,
                               "direct_conversion": 1.0, "seo_content": 1.0,
                               "performance_mobile": 1.0},
        }
        scores = scorer.score_brechas(brechas, channel_context=channel_context)
        assert len(scores) == 1
        s = scores[0]
        assert hasattr(s, "channel_multiplier")
        assert hasattr(s, "channel_reason")
        assert s.channel_multiplier == 1.5
        assert isinstance(s.channel_reason, str)


# ---------------------------------------------------------------------------
# GAP-3: channel_context en v4_complete_report.json
# ---------------------------------------------------------------------------

class TestGAP3ChannelContextInReport:
    """GAP-3: v4_complete_report acepta e incluye channel_context."""

    def test_resolve_channel_context_returns_dict_or_none(self):
        """_resolve_channel_context es accesible y retorna dict o None."""
        from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
        gen = V4DiagnosticGenerator()
        assert hasattr(gen, "_resolve_channel_context")
        # Sin audit_result -> retorna dict con valores por defecto (unknown/low)
        result = gen._resolve_channel_context(None, [])
        assert result is not None
        assert "dominant_channel" in result
        assert "confidence" in result
        assert "channel_weights" in result

    def test_channel_context_has_required_fields(self):
        """channel_context incluye dominant_channel, confidence, channel_weights."""
        from modules.financial_engine.channel_evidence_resolver import ChannelEvidenceResolver

        resolver = ChannelEvidenceResolver()
        evidence = resolver.resolve(
            onboarding_data=None,
            web_evidence={"whatsapp_visible": True},
            gbp_data={"review_count": 50, "score": 4.0},
            diagnostic_pains=["whatsapp_conflict"],
        )
        ctx = {
            "dominant_channel": evidence.dominant_channel.value
            if hasattr(evidence.dominant_channel, "value")
            else str(evidence.dominant_channel),
            "confidence": evidence.confidence.value
            if hasattr(evidence.confidence, "value")
            else str(evidence.confidence),
            "channel_weights": evidence.channel_weights,
        }
        assert "dominant_channel" in ctx
        assert "confidence" in ctx
        assert "channel_weights" in ctx
        assert ctx["dominant_channel"] in ("whatsapp", "direct", "social", "unknown", "gbp")
        assert ctx["confidence"] in ("high", "medium", "low")
        assert isinstance(ctx["channel_weights"], dict)


# ---------------------------------------------------------------------------
# GAP-4: precision_tier en financial_scenarios.json
# ---------------------------------------------------------------------------

class TestGAP4PrecisionTierInScenarios:
    """GAP-4: financial_scenarios.json incluye precision_tier."""

    def test_precision_validator_returns_tier_and_can_show_exact(self):
        """PrecisionValidator.validate() retorna precision_tier y can_show_exact_money."""
        from modules.financial_engine.precision_validator import PrecisionValidator

        result = PrecisionValidator.validate(
            adr_cop=300000.0,
            adr_source="regional_v410",
            occupancy_rate=0.65,
            occupancy_source="onboarding",
            direct_channel_pct=0.20,
            channel_source="onboarding",
        )
        assert result.precision_tier in ("A", "B", "C")
        assert isinstance(result.can_show_exact_money, bool)

    def test_financial_evidence_to_dict_includes_precision_fields(self):
        """FinancialEvidence.to_dict() incluye financial_precision_tier y can_show_exact_money."""
        from modules.financial_engine.financial_evidence import build_financial_evidence

        evidence = build_financial_evidence(
            adr_cop=300000.0,
            adr_source="regional_v410",
            occupancy_rate=0.65,
            occupancy_source="web_scraping",
            direct_channel_pct=0.20,
            channel_source="onboarding",
        )
        d = evidence.to_dict()
        assert "financial_precision_tier" in d
        assert "can_show_exact_money" in d
        assert d["financial_precision_tier"] in ("A", "B", "C")
        assert isinstance(d["can_show_exact_money"], bool)
