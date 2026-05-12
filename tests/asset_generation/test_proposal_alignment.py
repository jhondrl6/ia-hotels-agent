"""Tests for proposal_asset_alignment module.

Validates the mapping and verification logic between proposal services
and generated assets.

FASE-SOL2-B: Updated to reflect 7 services (6 base + 1 conditional AEO).
Google Maps Optimizado was removed in FASE-PROP-D.
"""

import pytest
from modules.asset_generation.proposal_asset_alignment import (
    PROPOSAL_SERVICE_TO_ASSET,
    ALL_PROMISED_SERVICES,
    ServiceAlignment,
    AlignmentReport,
    verify_proposal_asset_alignment,
    get_missing_services,
    get_alignment_summary,
)
from modules.asset_generation.site_presence_checker import (
    SitePresenceReport,
    PresenceCheckResult,
    PresenceStatus,
)
from datetime import datetime


class TestProposalAssetMapping:
    """Test the proposal service to asset mapping."""

    def test_all_7_services_mapped(self):
        """All 7 promised services must have a mapping (FASE-SOL2-B: +llms_txt)."""
        assert len(PROPOSAL_SERVICE_TO_ASSET) == 7

    def test_all_promised_services_count(self):
        """ALL_PROMISED_SERVICES must have 7 entries (FASE-SOL2-B)."""
        assert len(ALL_PROMISED_SERVICES) == 7

    def test_mapping_covers_all_services(self):
        """Every service in ALL_PROMISED_SERVICES must be in the mapping."""
        for service in ALL_PROMISED_SERVICES:
            assert service in PROPOSAL_SERVICE_TO_ASSET

    def test_each_service_maps_to_unique_asset(self):
        """Each service should map to a unique asset type."""
        asset_types = list(PROPOSAL_SERVICE_TO_ASSET.values())
        assert len(asset_types) == len(set(asset_types))

    def test_known_mappings(self):
        """Test specific known mappings (FASE-SOL2-B: llms_txt replaces geo_playbook)."""
        assert PROPOSAL_SERVICE_TO_ASSET["Optimización para IA Generativa"] == "llms_txt"
        assert PROPOSAL_SERVICE_TO_ASSET["Botón de WhatsApp"] == "whatsapp_button"
        assert PROPOSAL_SERVICE_TO_ASSET["Informe Mensual"] == "monthly_report"

    def test_llms_txt_in_mapping(self):
        """GAP-C closure: llms_txt must be in PROPOSAL_SERVICE_TO_ASSET."""
        assert "Optimización para IA Generativa" in PROPOSAL_SERVICE_TO_ASSET
        assert PROPOSAL_SERVICE_TO_ASSET["Optimización para IA Generativa"] == "llms_txt"

    def test_no_google_maps_in_mapping(self):
        """Google Maps Optimizado was removed in FASE-PROP-D."""
        assert "Google Maps Optimizado" not in PROPOSAL_SERVICE_TO_ASSET


class TestVerifyAlignment:
    """Test the alignment verification logic."""

    def test_all_aligned_when_all_assets_present(self):
        """All services aligned when all 7 assets are present (FASE-SOL2-B)."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
            {"asset_type": "llms_txt", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert report.all_aligned is True
        assert len(report.missing) == 0
        assert len(report.aligned) == 7

    def test_missing_assets_detected(self):
        """Missing assets must be detected (6 of 7 missing when only optimization_guide provided)."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert report.all_aligned is False
        assert len(report.missing) == 6
        assert len(report.aligned) == 1

    def test_low_quality_assets_detected(self):
        """Low confidence assets must be flagged (FASE-SOL2-B with 7 services)."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
            {"asset_type": "llms_txt", "confidence_score": 0.3},  # low
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert len(report.low_quality) == 1
        assert report.low_quality[0].service_name == "Optimización para IA Generativa"

    def test_empty_assets_all_missing(self):
        """With no assets, all 7 services should be missing (FASE-SOL2-B)."""
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
        )
        assert len(report.missing) == 7
        assert len(report.aligned) == 0
        assert report.alignment_percentage == 0.0

    def test_default_services_when_empty_list(self):
        """Empty proposal_services should default to ALL_PROMISED_SERVICES (7 services, FASE-SOL2-B)."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
            {"asset_type": "llms_txt", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=[],
            generated_assets=assets,
        )
        assert report.all_aligned is True
        assert report.total_services == 7


class TestAlignmentReport:
    """Test AlignmentReport dataclass."""

    def test_report_to_dict(self):
        """Report should serialize to dict correctly (FASE-SOL2-B with 7 services)."""
        assets = [
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        d = report.to_dict()
        assert "total_services" in d
        assert "aligned_count" in d
        assert "missing_count" in d
        assert d["total_services"] == 7


class TestHelpers:
    """Test helper functions."""

    def test_get_missing_services(self):
        """get_missing_services should return list of names (7 services missing when none provided)."""
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
        )
        missing = get_missing_services(report)
        assert len(missing) == 7
        assert "Botón de WhatsApp" in missing
        assert "Optimización para IA Generativa" in missing

    def test_get_alignment_summary(self):
        """get_alignment_summary should return readable string."""
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
        )
        summary = get_alignment_summary(report)
        assert "MISSING" in summary
        assert "NOT READY" in summary


class TestConfidenceToNivelSignificado:
    """FASE-D: Tests for _confidence_to_nivel_significado presence-verified path."""

    def test_verified_present_in_production_returns_verificado_en_sitio(self):
        """When presence_verified=True and present_in_production=True -> 'Verificado en sitio'."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        gen = V4ProposalGenerator()
        nivel, significado = gen._confidence_to_nivel_significado(
            confidence=0.5,
            assets_generated=None,
            present_in_production=True,
            presence_verified=True,
        )
        assert nivel == "✅ Verificado en sitio"
        assert significado == "Ya existe en su web - nosotros lo entregamos"

    def test_high_confidence_without_presence_not_falsely_complete(self):
        """High confidence (>=0.85) WITHOUT presence verification should NOT claim 'Completo'."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        gen = V4ProposalGenerator()
        nivel, significado = gen._confidence_to_nivel_significado(
            confidence=0.95,
            assets_generated=[],
            present_in_production=False,
            presence_verified=False,
        )
        assert nivel == "✅ Completo"
        assert significado == "Listo para implementar"

    def test_verified_but_not_in_production(self):
        """presence_verified=True but present_in_production=False -> not 'Verificado en sitio'."""
        from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator

        gen = V4ProposalGenerator()
        nivel, significado = gen._confidence_to_nivel_significado(
            confidence=0.85,
            assets_generated=[],
            present_in_production=False,
            presence_verified=True,
        )
        assert nivel != "✅ Verificado en sitio"
        assert nivel == "✅ Completo"


class TestDivergenceDetection:
    """FASE-12B: Tests for audit↔presence divergence detection."""

    def _make_presence_report(self, asset_type: str, status: PresenceStatus) -> SitePresenceReport:
        """Helper: create a SitePresenceReport with one result."""
        return SitePresenceReport(
            site_url="https://example.com",
            checked_at=datetime.now(),
            results={
                asset_type: PresenceCheckResult(
                    asset_type=asset_type,
                    status=status,
                    verified_at=datetime.now(),
                    site_url="https://example.com",
                )
            },
        )

    def test_divergence_hotel_schema_audit_false_presence_exists(self):
        """FASE-12B: audit says hotel_schema_detected=false, presence says EXISTS → divergent missing."""
        audit_schema = {
            "hotel_schema_detected": False,
            "hotel_schema_valid": False,
            "hotel_confidence": "unknown",
            "faq_schema_detected": False,
            "faq_schema_valid": False,
            "faq_confidence": "unknown",
        }
        site_report = self._make_presence_report("hotel_schema", PresenceStatus.EXISTS)

        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],  # No hotel_schema generated
            site_presence_report=site_report,
            hotel_url="https://example.com",
            audit_schema=audit_schema,
        )

        # Should be in missing (not present_in_production)
        assert len(report.missing) == 7, f"Expected 7 missing, got {len(report.missing)}"
        assert len(report.present_in_production) == 0
        assert report.all_aligned is False

        # Find the hotel_schema entry
        hotel_entry = next(
            (s for s in report.missing if s.asset_type == "hotel_schema"), None
        )
        assert hotel_entry is not None, "hotel_schema should be in missing"
        assert hotel_entry.presence_verified is True
        assert hotel_entry.presence_status == "divergent"
        assert "DIVERGENCIA" in hotel_entry.message
        assert "hotel_schema_detected=false" in hotel_entry.message

    def test_no_divergence_hotel_schema_audit_true_presence_exists(self):
        """FASE-12B: audit says hotel_schema_detected=true, presence says EXISTS → present_in_production (normal)."""
        audit_schema = {
            "hotel_schema_detected": True,
            "hotel_schema_valid": True,
            "hotel_confidence": "verified",
            "faq_schema_detected": False,
            "faq_schema_valid": False,
            "faq_confidence": "unknown",
        }
        site_report = self._make_presence_report("hotel_schema", PresenceStatus.EXISTS)

        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],  # No hotel_schema generated
            site_presence_report=site_report,
            hotel_url="https://example.com",
            audit_schema=audit_schema,
        )

        # hotel_schema should be in present_in_production (not missing)
        assert len(report.present_in_production) == 1
        hotel_entry = report.present_in_production[0]
        assert hotel_entry.asset_type == "hotel_schema"
        assert hotel_entry.presence_status == "exists"
        assert hotel_entry.status == "present_in_production"
        # Other 6 services still missing
        assert len(report.missing) == 6

    def test_no_audit_schema_backward_compat(self):
        """FASE-12B: Without audit_schema, presence EXISTS → present_in_production (backward compatible)."""
        site_report = self._make_presence_report("hotel_schema", PresenceStatus.EXISTS)

        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
            site_presence_report=site_report,
            hotel_url="https://example.com",
            # No audit_schema provided
        )

        # hotel_schema should be in present_in_production
        assert len(report.present_in_production) == 1
        assert report.present_in_production[0].asset_type == "hotel_schema"

    def test_divergence_appears_in_to_dict(self):
        """FASE-12B: Divergent entry should appear in to_dict() with presence_status='divergent'."""
        audit_schema = {"hotel_schema_detected": False}
        site_report = self._make_presence_report("hotel_schema", PresenceStatus.EXISTS)

        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
            site_presence_report=site_report,
            hotel_url="https://example.com",
            audit_schema=audit_schema,
        )
        d = report.to_dict()

        # Find hotel_schema in missing
        missing_items = d.get("missing", [])
        hotel_items = [m for m in missing_items if m.get("asset") == "hotel_schema"]
        assert len(hotel_items) == 1
        assert hotel_items[0]["presence_verified"] is True
        assert hotel_items[0]["presence_status"] == "divergent"

# ============================================================================
# FASE-3-CONTENT: Test for all_covered property + all_aligned deprecated alias
# ============================================================================

def test_all_covered_property_exists():
    """all_covered property existe y retorna igual que all_aligned (deprecated)."""
    report = AlignmentReport()
    # Con missing vacio, ambos deben ser True
    assert report.all_covered is True
    assert report.all_aligned is True

    # Agregar un missing -> ambos deben ser False
    report.missing.append(ServiceAlignment(
        service_name="Test Service",
        asset_type="test_asset",
        is_aligned=False,
        status="missing",
        message="Test missing",
    ))
    assert report.all_covered is False
    assert report.all_aligned is False, "all_aligned alias must match all_covered"


def test_all_covered_in_to_dict():
    """to_dict() incluye 'all_covered' y mantiene 'all_aligned' para backward compat."""
    report = AlignmentReport()
    d = report.to_dict()
    assert "all_covered" in d, f"all_covered missing from dict keys: {list(d.keys())}"
    assert "all_aligned" in d, f"all_aligned missing (backward compat): {list(d.keys())}"
    assert d["all_covered"] == d["all_aligned"], "all_covered and all_aligned must match"
