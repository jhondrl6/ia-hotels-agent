"""
Tests for gate_presence - FASE-D: Site Presence Verification in gate_report.

Verifies that gate_report correctly identifies assets that exist in production
site (present_in_production) vs truly missing assets.

Run with:
    pytest tests/quality_gates/test_gate_presence.py -v
"""

import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
from dataclasses import dataclass

from modules.asset_generation.proposal_asset_alignment import (
    ServiceAlignment,
    AlignmentReport,
    verify_proposal_asset_alignment,
    ALL_PROMISED_SERVICES,
)
from modules.asset_generation.site_presence_checker import (
    SitePresenceChecker,
    SitePresenceReport,
    PresenceCheckResult,
    PresenceStatus,
)
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


class TestGatePresenceSitePresenceChecker:
    """Test SitePresenceChecker integration with alignment verification."""
    
    def test_asset_with_exists_status_not_marked_missing(self):
        """Asset with PresenceStatus.EXISTS should be marked present_in_production, not missing."""
        # Mock site presence report where whatsapp_button EXISTS
        presence_result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"whatsapp_button": presence_result}
        
        # No generated assets (would normally be "missing")
        generated_assets = []
        proposal_services = ["Botón de WhatsApp"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        # Should be present_in_production, NOT missing
        assert len(report.present_in_production) == 1
        assert len(report.missing) == 0
        assert report.present_in_production[0].service_name == "Botón de WhatsApp"
        assert report.present_in_production[0].presence_verified is True
        assert report.present_in_production[0].presence_status == "exists"
    
    def test_asset_with_not_exists_status_marked_missing(self):
        """Asset with PresenceStatus.NOT_EXISTS should be marked missing."""
        presence_result = PresenceCheckResult(
            asset_type="open_graph",
            status=PresenceStatus.NOT_EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"open_graph": presence_result}
        
        generated_assets = []
        proposal_services = ["Meta Tags Sociales (Open Graph)"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        assert len(report.missing) == 1
        assert len(report.present_in_production) == 0
        assert report.missing[0].service_name == "Meta Tags Sociales (Open Graph)"
        assert report.missing[0].presence_verified is True
        assert report.missing[0].presence_status == "not_exists"
    
    def test_asset_with_redundant_status_marked_redundant(self):
        """Asset with PresenceStatus.REDUNDANT should be marked redundant."""
        presence_result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.REDUNDANT,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"whatsapp_button": presence_result}
        
        generated_assets = []
        proposal_services = ["Botón de WhatsApp"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        assert len(report.redundant) == 1
        assert len(report.missing) == 0
        assert report.redundant[0].service_name == "Botón de WhatsApp"
        assert report.redundant[0].presence_status == "redundant"
    
    def test_asset_with_verification_failed_marked_missing(self):
        """Asset with PresenceStatus.VERIFICATION_FAILED should be marked missing."""
        presence_result = PresenceCheckResult(
            asset_type="open_graph",
            status=PresenceStatus.VERIFICATION_FAILED,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={"error": "Site unreachable"}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"open_graph": presence_result}
        
        generated_assets = []
        proposal_services = ["Meta Tags Sociales (Open Graph)"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        assert len(report.missing) == 1
        assert report.missing[0].presence_verified is True
        assert report.missing[0].presence_status == "verification_failed"


class TestAlignmentPercentageWithPresence:
    """Test alignment_percentage calculation with present_in_production assets."""
    
    def test_alignment_percentage_excludes_present_in_production(self):
        """alignment_percentage should exclude present_in_production from denominator."""
        presence_result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"whatsapp_button": presence_result}
        
        # Only faq_page is generated, whatsapp_button exists in production
        generated_assets = [
            {"asset_type": "faq_page", "confidence_score": 0.85}
        ]
        proposal_services = ["Botón de WhatsApp", "Página de FAQ"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        # total_services excludes present_in_production
        assert report.total_services == 1  # Only faq_page counts
        # alignment_percentage = aligned / total_services
        assert report.alignment_percentage == 1.0  # faq_page is aligned
        # But actually we have 2 effective services covered (1 generated + 1 present)
        assert len(report.present_in_production) == 1
    
    def test_effective_alignment_with_present_in_production(self):
        """When all services are either aligned or present_in_production, all_aligned is True."""
        presence_result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={}
        )
        
        mock_report = Mock(spec=SitePresenceReport)
        mock_report.results = {"whatsapp_button": presence_result}
        
        # faq_page generated with good confidence
        generated_assets = [
            {"asset_type": "faq_page", "confidence_score": 0.85}
        ]
        proposal_services = ["Botón de WhatsApp", "Página de FAQ"]
        
        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=mock_report,
        )
        
        # No missing = all aligned (in some form)
        assert report.all_aligned is True
        assert len(report.missing) == 0


class TestGateReportBackwardCompatibility:
    """Test that gate_report JSON output is backward compatible."""
    
    def test_to_dict_excludes_empty_categories(self):
        """Empty present_in_production and redundant should not appear in output."""
        report = AlignmentReport()
        report.aligned.append(ServiceAlignment(
            service_name="Página de FAQ",
            asset_type="faq_page",
            is_aligned=True,
            status="aligned",
            confidence_score=0.85
        ))
        
        d = report.to_dict()
        
        # Backward compatible fields must exist
        assert "total_services" in d
        assert "aligned_count" in d
        assert "missing_count" in d
        assert "low_quality_count" in d
        assert "alignment_percentage" in d
        assert "all_aligned" in d
        assert "aligned" in d
        assert "missing" in d
        assert "low_quality" in d
        
        # New categories only appear if non-empty
        assert "present_in_production" not in d or d["present_in_production"] == []
        assert "redundant" not in d or d["redundant"] == []
    
    def test_to_dict_includes_present_in_production_when_present(self):
        """present_in_production should appear in output when assets exist."""
        report = AlignmentReport()
        report.present_in_production.append(ServiceAlignment(
            service_name="Botón de WhatsApp",
            asset_type="whatsapp_button",
            is_aligned=True,
            status="present_in_production",
            presence_verified=True,
            presence_status="exists"
        ))
        
        d = report.to_dict()
        
        assert "present_in_production" in d
        assert len(d["present_in_production"]) == 1
        assert d["present_in_production"][0]["service"] == "Botón de WhatsApp"
        assert d["present_in_production"][0]["presence_status"] == "exists"
    
    def test_aligned_items_have_presence_verified_when_checked(self):
        """Aligned items should have presence_verified field when site was checked."""
        report = AlignmentReport()
        report.present_in_production.append(ServiceAlignment(
            service_name="Botón de WhatsApp",
            asset_type="whatsapp_button",
            is_aligned=True,
            status="present_in_production",
            presence_verified=True,
            presence_status="exists"
        ))
        
        d = report.to_dict()
        
        pip = d["present_in_production"][0]
        assert pip["presence_verified"] is True
        assert pip["presence_status"] == "exists"


class TestProposalAlignmentGateWithSitePresence:
    """Test the full gate with SitePresenceChecker integration."""
    
    @pytest.fixture
    def orchestrator(self):
        return PublicationGatesOrchestrator(PublicationGateConfig())
    
    def test_gate_with_site_presence_checker_integration(self, orchestrator):
        """FASE-3 (BUG-10): Gate uses SitePresenceChecker but alignment is low with only 2/7."""
        # Create a mock site presence report where whatsapp_button EXISTS
        mock_site_report = Mock()
        mock_site_report.results = {
            "whatsapp_button": PresenceCheckResult(
                asset_type="whatsapp_button",
                status=PresenceStatus.EXISTS,
                verified_at=datetime.now(),
                site_url="https://example.com",
                details={}
            )
        }
        
        assessment = {
            "hotel_url": "https://example.com",
            "site_presence_report": mock_site_report,  # Pre-built report
            "generated_assets": [
                {"asset_type": "faq_page", "confidence_score": 0.85}
            ]
        }
        
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        
        # BUG-10: With 7 services total, 2/7 = 28.5% < 80% → BLOCKED
        # (1 generated + 1 present_in_production = 2 covered, 5 missing)
        assert result.status == GateStatus.BLOCKED
        assert "already in production" in result.message or "production" in result.message
    
    def test_gate_message_shows_present_in_production(self, orchestrator):
        """Gate message should show both missing and present_in_production counts."""
        mock_site_report = Mock()
        mock_site_report.results = {
            "whatsapp_button": PresenceCheckResult(
                asset_type="whatsapp_button",
                status=PresenceStatus.EXISTS,
                verified_at=datetime.now(),
                site_url="https://example.com",
                details={}
            ),
            "open_graph": PresenceCheckResult(
                asset_type="open_graph",
                status=PresenceStatus.NOT_EXISTS,
                verified_at=datetime.now(),
                site_url="https://example.com",
                details={}
            )
        }
        
        assessment = {
            "hotel_url": "https://example.com",
            "site_presence_report": mock_site_report,
            "generated_assets": [
                {"asset_type": "faq_page", "confidence_score": 0.85}
            ]
        }
        
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        
        # Should show that whatsapp_button is already in production
        assert "Botón de WhatsApp" in result.message or "production" in result.message
        assert "missing" in result.message.lower() or "open_graph" in result.message
    
    def test_gate_result_details_include_presence_info(self, orchestrator):
        """result.details should include present_in_production list when applicable."""
        mock_site_report = Mock()
        mock_site_report.results = {
            "whatsapp_button": PresenceCheckResult(
                asset_type="whatsapp_button",
                status=PresenceStatus.EXISTS,
                verified_at=datetime.now(),
                site_url="https://example.com",
                details={}
            )
        }
        
        assessment = {
            "hotel_url": "https://example.com",
            "site_presence_report": mock_site_report,
            "generated_assets": [
                {"asset_type": "faq_page", "confidence_score": 0.85}
            ]
        }
        
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        
        # Details should contain present_in_production when site check finds EXISTS
        assert "present_in_production" in result.details
        # The presence_verified field should be included
        if result.details.get("present_in_production"):
            assert result.details["present_in_production"][0].get("presence_verified") is True
