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

# ============================================================================
# FASE-3-CONTENT: Test evidence_tier consistency between JSON and YAML paths
# ============================================================================

def test_evidence_tier_consistent_from_breakdown():
    """El evidence_tier del FinancialBreakdown se propaga correctamente.
    
    Verifica que _determine_evidence_tier produce un tier consistente basado
    en las fuentes de datos reales, y que el tier es propagable.
    """
    from modules.financial_engine.scenario_calculator import (
        ScenarioCalculator,
        HotelFinancialData,
    )

    # Caso 1: Todas las fuentes son low_quality -> Tier C
    hotel_low = HotelFinancialData(
        adr_cop=300000.0,
        rooms=10,
        occupancy_rate=0.45,
        ota_commission_rate=0.15,
        adr_source="legacy_hardcode",
        occupancy_source="default",
        channel_source="unknown",
    )
    calc = ScenarioCalculator()
    breakdown = calc.calculate_breakdown(hotel_low)
    tier = breakdown.evidence_tier
    assert tier == "C", f"Expected Tier C for low quality sources, got {tier}"

    # Caso 2: Fuentes verificadas sin GA4/GSC → Tier B+ (FASE-1: honesto)
    hotel_verified = HotelFinancialData(
        adr_cop=350000.0,
        rooms=12,
        occupancy_rate=0.55,
        ota_commission_rate=0.15,
        adr_source="onboarding",
        occupancy_source="verified",
        channel_source="verified",
        ga4_enabled=False,
        gsc_enabled=False,
    )
    breakdown = calc.calculate_breakdown(hotel_verified)
    tier = breakdown.evidence_tier
    assert tier == "B+", f"Expected Tier B+ for verified sources without GA4/GSC, got {tier}"

    # Caso 2b: Fuentes verificadas CON GA4+GSC → Tier A (FASE-1)
    hotel_verified_with_ga4 = HotelFinancialData(
        adr_cop=350000.0,
        rooms=12,
        occupancy_rate=0.55,
        ota_commission_rate=0.15,
        adr_source="onboarding",
        occupancy_source="verified",
        channel_source="verified",
        ga4_enabled=True,
        gsc_enabled=True,
    )
    breakdown = calc.calculate_breakdown(hotel_verified_with_ga4)
    tier = breakdown.evidence_tier
    assert tier == "A", f"Expected Tier A for verified sources with GA4+GSC, got {tier}"

    # Caso 3: Fuentes mixtas (1 verified, 2 low) → Tier B+ (FASE-1: has_verified_data tiene prioridad)
    hotel_mixed = HotelFinancialData(
        adr_cop=320000.0,
        rooms=10,
        occupancy_rate=0.50,
        ota_commission_rate=0.15,
        adr_source="onboarding",
        occupancy_source="default",
        channel_source="unknown",
    )
    breakdown = calc.calculate_breakdown(hotel_mixed)
    tier = breakdown.evidence_tier
    # Con 1 verified + 2 low_quality → B+ (has_verified_data sin GA4/GSC)
    assert tier == "B+", f"Expected Tier B+ for mixed sources (1 verified + 2 low) without GA4/GSC, got {tier}"

    # Caso 4: Fuentes mixtas balanceadas (1 verified, 1 low, 1 other) → Tier B+ (FASE-1: has_verified_data)
    hotel_mixed2 = HotelFinancialData(
        adr_cop=320000.0,
        rooms=10,
        occupancy_rate=0.50,
        ota_commission_rate=0.15,
        adr_source="onboarding",
        occupancy_source="default",
        channel_source="industry_standard_15pct",
    )
    breakdown = calc.calculate_breakdown(hotel_mixed2)
    tier = breakdown.evidence_tier
    assert tier == "B+", f"Expected Tier B+ for balanced mixed sources without GA4/GSC, got {tier}"


def test_diagnostic_generator_uses_breakdown_tier():
    """El diagnostic generator usa el tier del FinancialBreakdown cuando esta disponible."""
    from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
    from modules.commercial_documents.data_structures import (
        FinancialScenarios,
        FinancialBreakdown,
        Scenario,
    )

    gen = V4DiagnosticGenerator()

    # Crear un breakdown con tier especifico
    breakdown = FinancialBreakdown(
        monthly_ota_commission_cop=500000.0,
        ota_commission_basis="test",
        ota_commission_source="test",
        shift_savings_cop=50000.0,
        shift_percentage=0.10,
        shift_source="test",
        ia_revenue_cop=25000.0,
        ia_boost_percentage=0.05,
        ia_source="test",
        evidence_tier="A",
        disclaimer="Test disclaimer",
        hotel_data_sources={},
    )

    # Crear scenarios minimos (Scenario requiere probability)
    scenarios = FinancialScenarios(
        conservative=Scenario(
            description="Conservative scenario",
            monthly_loss_min=300000,
            monthly_loss_max=400000,
            probability=0.70,
        ),
        realistic=Scenario(
            description="Realistic scenario",
            monthly_loss_min=400000,
            monthly_loss_central=500000,
            monthly_loss_max=600000,
            probability=0.20,
        ),
        optimistic=Scenario(
            description="Optimistic scenario",
            monthly_loss_min=600000,
            monthly_loss_max=700000,
            probability=0.10,
        ),
    )

    # Llamar a _build_financial_placeholders con el breakdown
    placeholders = gen._build_financial_placeholders(
        scenarios,
        analytics_data=None,
        source_reliability="unverified",
        financial_breakdown=breakdown,
    )

    assert placeholders["evidence_tier"] == "A", \
        f"Expected tier 'A' from breakdown, got '{placeholders['evidence_tier']}'"


def test_diagnostic_generator_fallback_tier_no_breakdown():
    """Sin breakdown, el diagnostic generator usa GA4 para determinar tier (fallback)."""
    from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
    from modules.commercial_documents.data_structures import (
        FinancialScenarios,
        Scenario,
    )

    gen = V4DiagnosticGenerator()

    scenarios = FinancialScenarios(
        conservative=Scenario(
            description="Conservative scenario",
            monthly_loss_min=300000,
            monthly_loss_max=400000,
            probability=0.70,
        ),
        realistic=Scenario(
            description="Realistic scenario",
            monthly_loss_min=400000,
            monthly_loss_central=500000,
            monthly_loss_max=600000,
            probability=0.20,
        ),
        optimistic=Scenario(
            description="Optimistic scenario",
            monthly_loss_min=600000,
            monthly_loss_max=700000,
            probability=0.10,
        ),
    )

    # Sin breakdown, sin GA4 -> tier C
    placeholders = gen._build_financial_placeholders(
        scenarios,
        analytics_data=None,
        source_reliability="unverified",
        financial_breakdown=None,
    )
    assert placeholders["evidence_tier"] == "C", \
        f"Expected fallback tier 'C' without GA4, got '{placeholders['evidence_tier']}'"

    # Sin breakdown, con GA4 -> tier A
    placeholders = gen._build_financial_placeholders(
        scenarios,
        analytics_data={"use_ga4": True},
        source_reliability="verified",
        financial_breakdown=None,
    )
    assert placeholders["evidence_tier"] == "A", \
        f"Expected fallback tier 'A' with GA4, got '{placeholders['evidence_tier']}'"
