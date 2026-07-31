"""Tests for FASE-4: Evidence Tier, Gate Consistency, and Integration.

Covers:
- T1: Unit tests for _determine_evidence_tier() (all tier combinations)
- T2: Integration test for tier piping (pipeline completo)
- T3: Gate tests for CG-EVIDENCE-TIER-CONSISTENCY (per-hotel params)
"""

import pytest
from modules.commercial_documents.data_structures import EvidenceTier, FinancialBreakdown
from modules.financial_engine.scenario_calculator import (
    HotelFinancialData,
    ScenarioCalculator,
)
from modules.quality_gates.commercial_gate import (
    CommercialGateValidator,
    CommercialGateResult,
)


# ──────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────

def _make_hotel_data(
    adr_source="onboarding",
    channel_source="onboarding",
    occupancy_source="onboarding",
    ga4_enabled=False,
    gsc_enabled=False,
    rooms=20,
    adr_cop=300000.0,
    occupancy_rate=0.55,
    direct_channel_percentage=0.60,
    ota_commission_rate=0.15,
):
    """Factory para HotelFinancialData con defaults de onboarding verificado."""
    return HotelFinancialData(
        rooms=rooms,
        adr_cop=adr_cop,
        occupancy_rate=occupancy_rate,
        ota_commission_rate=ota_commission_rate,
        direct_channel_percentage=direct_channel_percentage,
        adr_source=adr_source,
        occupancy_source=occupancy_source,
        channel_source=channel_source,
        ga4_enabled=ga4_enabled,
        gsc_enabled=gsc_enabled,
    )


# ──────────────────────────────────────────────────────────────
# T1: Unit tests for _determine_evidence_tier()
# ──────────────────────────────────────────────────────────────

class TestDetermineEvidenceTier:
    """Tests para _determine_evidence_tier() con ga4_enabled/gsc_enabled."""

    def test_tier_a_with_ga4_and_gsc_verified(self):
        """GA4+GSC conectados + has_verified_data → Tier A."""
        hotel_data = _make_hotel_data(
            ga4_enabled=True,
            gsc_enabled=True,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.A

    def test_tier_b_plus_with_onboarding_no_ga4(self):
        """Onboarding verificado sin GA4 ni GSC → B+."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B_PLUS

    def test_tier_b_plus_with_ga4_but_no_gsc(self):
        """GA4 conectado pero GSC no → B+ (se requieren AMBOS)."""
        hotel_data = _make_hotel_data(
            ga4_enabled=True,
            gsc_enabled=False,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B_PLUS

    def test_tier_b_plus_with_gsc_but_no_ga4(self):
        """GSC conectado pero GA4 no → B+ (se requieren AMBOS)."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=True,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B_PLUS

    def test_tier_b_plus_with_user_provided_no_ga4(self):
        """user_provided source (sin GA4/GSC) → B+."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="user_provided",
            channel_source="user_provided",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B_PLUS

    def test_tier_c_with_low_quality_sources(self):
        """Fuentes de baja calidad (2+ scraping/default/unknown) → C."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="scraping",
            channel_source="default",
            occupancy_source="legacy_hardcode",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.C

    def test_tier_c_with_all_unknown_sources(self):
        """Todas las fuentes 'unknown' → C (low_quality >= 2)."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="unknown",
            channel_source="unknown",
            occupancy_source="unknown",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.C

    def test_tier_b_default_mixed_sources(self):
        """Sin verified ni low_quality suficiente → B (default)."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="scraping",          # low_quality count = 1
            channel_source="industry_standard",  # not verified, not low_quality
            occupancy_source="industry_standard", # not verified, not low_quality
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B

    def test_tier_b_plus_with_verified_channel_source(self):
        """channel_source='verified' (sin GA4/GSC) → B+."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="unknown",
            channel_source="verified",
        )
        calc = ScenarioCalculator()
        tier = calc._determine_evidence_tier(hotel_data)
        assert tier == EvidenceTier.B_PLUS


# ──────────────────────────────────────────────────────────────
# T2: Integration test — pipeline completo
# ──────────────────────────────────────────────────────────────

class TestEvidenceTierIntegration:
    """Integration tests: pipeline completo produce tier correcto."""

    def test_onboarding_without_ga4_produces_b_plus(self):
        """v4complete scenario: onboarding verificado sin GA4 → Tier B+."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="onboarding",
            channel_source="onboarding",
            rooms=21,
            adr_cop=320000.0,
            occupancy_rate=0.60,
            direct_channel_percentage=0.55,
        )
        calc = ScenarioCalculator()
        breakdown = calc.calculate_breakdown(hotel_data)

        assert breakdown.evidence_tier == "B+"
        assert "operativos" in breakdown.disclaimer
        assert breakdown.monthly_ota_commission_cop >= 0
        assert breakdown.shift_savings_cop >= 0
        assert breakdown.ia_revenue_cop >= 0

    def test_unknown_sources_produces_tier_c(self):
        """Sin onboarding ni GA4 → Tier C (low_quality sources)."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="unknown",
            channel_source="unknown",
            occupancy_source="unknown",
        )
        calc = ScenarioCalculator()
        breakdown = calc.calculate_breakdown(hotel_data)

        assert breakdown.evidence_tier == "C"
        assert "limitados" in breakdown.disclaimer

    def test_ga4_gsc_produces_tier_a(self):
        """GA4+GSC conectados + onboarding → Tier A."""
        hotel_data = _make_hotel_data(
            ga4_enabled=True,
            gsc_enabled=True,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        breakdown = calc.calculate_breakdown(hotel_data)

        assert breakdown.evidence_tier == "A"
        assert "Google Analytics" in breakdown.disclaimer

    def test_only_ga4_produces_b_plus(self):
        """Solo GA4 (sin GSC) + onboarding → B+."""
        hotel_data = _make_hotel_data(
            ga4_enabled=True,
            gsc_enabled=False,
            adr_source="onboarding",
            channel_source="onboarding",
        )
        calc = ScenarioCalculator()
        breakdown = calc.calculate_breakdown(hotel_data)

        assert breakdown.evidence_tier == "B+"

    def test_breakdown_preserves_hotel_data_sources(self):
        """calculate_breakdown preserva las fuentes de datos del hotel."""
        hotel_data = _make_hotel_data(
            ga4_enabled=False,
            gsc_enabled=False,
            adr_source="onboarding",
            channel_source="user_provided",
            occupancy_source="benchmark",
        )
        calc = ScenarioCalculator()
        breakdown = calc.calculate_breakdown(hotel_data)

        assert breakdown.hotel_data_sources["adr"] == "onboarding"
        assert breakdown.hotel_data_sources["direct_channel"] == "user_provided"
        assert breakdown.ota_commission_source == "industry_standard_15pct"


# ──────────────────────────────────────────────────────────────
# T3: Gate tests for CG-EVIDENCE-TIER-CONSISTENCY
# ──────────────────────────────────────────────────────────────

class TestEvidenceTierConsistencyGate:
    """Tests para CG-EVIDENCE-TIER-CONSISTENCY con params per-hotel."""

    def _make_financial_json(self, evidence_tier="B+"):
        """Factory para el financial_json que espera el gate."""
        return {
            "breakdown": {
                "evidence_tier": evidence_tier,
                "monthly_ota_commission_cop": 5400000,
            }
        }

    def _run_gate(self, evidence_tier="B+", ga4_available=False, gsc_available=False):
        """Helper: ejecuta el gate y devuelve el CommercialGateResult."""
        validator = CommercialGateValidator()
        financial_json = self._make_financial_json(evidence_tier)
        return validator._check_evidence_tier_consistency(
            financial_json=financial_json,
            ga4_available=ga4_available,
            gsc_available=gsc_available,
        )

    def test_blocks_when_tier_a_without_ga4(self):
        """Tier A sin ga4_available → BLOCKING."""
        result = self._run_gate(
            evidence_tier="A",
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"
        assert result.gate_id == "CG-EVIDENCE-TIER-CONSISTENCY"
        assert "GA4" in result.message

    def test_blocks_when_tier_a_without_gsc(self):
        """Tier A sin gsc_available → BLOCKING."""
        result = self._run_gate(
            evidence_tier="A",
            ga4_available=True,
            gsc_available=False,
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"
        assert "GSC" in result.message

    def test_blocks_when_tier_a_without_both(self):
        """Tier A sin GA4 ni GSC → BLOCKING, menciona ambos."""
        result = self._run_gate(
            evidence_tier="A",
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is False
        assert result.severity == "BLOCKING"
        assert "GA4" in result.message and "GSC" in result.message

    def test_passes_when_tier_b_plus(self):
        """Tier B+ no requiere verificación GA4/GSC → pasa."""
        result = self._run_gate(
            evidence_tier="B+",
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is True
        assert "no requiere" in result.message.lower()

    def test_passes_when_tier_b(self):
        """Tier B no requiere verificación GA4/GSC → pasa."""
        result = self._run_gate(
            evidence_tier="B",
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is True

    def test_passes_when_tier_c(self):
        """Tier C no requiere verificación GA4/GSC → pasa."""
        result = self._run_gate(
            evidence_tier="C",
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is True

    def test_passes_when_tier_a_with_ga4_and_gsc(self):
        """Tier A con ga4_available=True + gsc_available=True → pasa."""
        result = self._run_gate(
            evidence_tier="A",
            ga4_available=True,
            gsc_available=True,
        )
        assert result.passed is True
        assert "verificado" in result.message.lower()

    def test_handles_missing_financial_json(self):
        """financial_json=None → pasa gracefully (sin datos)."""
        validator = CommercialGateValidator()
        result = validator._check_evidence_tier_consistency(
            financial_json=None,
            ga4_available=False,
            gsc_available=False,
        )
        assert result.passed is True
        assert result.severity == "INFO"
