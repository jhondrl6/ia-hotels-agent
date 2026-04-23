"""Tests for proposal_asset_alignment module.

Validates the mapping and verification logic between proposal services
and generated assets.
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


class TestProposalAssetMapping:
    """Test the proposal service to asset mapping."""

    def test_all_7_services_mapped(self):
        """All 7 promised services must have a mapping (v4.34.0: +FAQ, +Open Graph)."""
        assert len(PROPOSAL_SERVICE_TO_ASSET) == 7

    def test_all_promised_services_count(self):
        """ALL_PROMISED_SERVICES must have 7 entries (v4.34.0)."""
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
        """Test specific known mappings."""
        assert PROPOSAL_SERVICE_TO_ASSET["Google Maps Optimizado"] == "geo_playbook"
        assert PROPOSAL_SERVICE_TO_ASSET["Boton de WhatsApp"] == "whatsapp_button"
        assert PROPOSAL_SERVICE_TO_ASSET["Informe Mensual"] == "monthly_report"


class TestVerifyAlignment:
    """Test the alignment verification logic."""

    def test_all_aligned_when_all_assets_present(self):
        """All services aligned when all 7 assets are present (v4.34.0)."""
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert report.all_aligned is True
        assert len(report.missing) == 0
        assert len(report.aligned) == 7

    def test_missing_assets_detected(self):
        """Missing assets must be detected (6 of 7 missing when only geo_playbook provided)."""
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
            # Missing: SEO Local, Boton de WhatsApp, Datos Estructurados, Informe Mensual, Pagina de FAQ, Meta Tags Sociales (6 of 7)
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert report.all_aligned is False
        assert len(report.missing) == 6
        assert len(report.aligned) == 1

    def test_low_quality_assets_detected(self):
        """Low confidence assets must be flagged (v4.34.0 with 7 services)."""
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.3},  # low
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
        ]
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=assets,
        )
        assert len(report.low_quality) == 1
        assert report.low_quality[0].service_name == "Google Maps Optimizado"

    def test_empty_assets_all_missing(self):
        """With no assets, all 7 services should be missing (v4.34.0)."""
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
        )
        assert len(report.missing) == 7
        assert len(report.aligned) == 0
        assert report.alignment_percentage == 0.0

    def test_default_services_when_empty_list(self):
        """Empty proposal_services should default to ALL_PROMISED_SERVICES (7 services, v4.34.0)."""
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
            {"asset_type": "hotel_schema", "confidence_score": 0.8},
            {"asset_type": "monthly_report", "confidence_score": 0.8},
            {"asset_type": "faq_page", "confidence_score": 0.8},
            {"asset_type": "open_graph", "confidence_score": 0.8},
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
        """Report should serialize to dict correctly (v4.34.0 with 7 services)."""
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
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
        assert "Boton de WhatsApp" in missing

    def test_get_alignment_summary(self):
        """get_alignment_summary should return readable string."""
        report = verify_proposal_asset_alignment(
            proposal_services=ALL_PROMISED_SERVICES,
            generated_assets=[],
        )
        summary = get_alignment_summary(report)
        assert "MISSING" in summary
        assert "NOT READY" in summary
