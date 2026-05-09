"""Tests para FIX-5: SitePresenceChecker hardening.

Verifica que:
1. Cuando SitePresenceChecker lanza excepción, el gate retorna presence_status: 'unknown'
2. El gate NO marca assets como missing cuando presence es unknown
3. Los assets no verificados se reportan como 'indeterminate'
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.asset_generation.proposal_asset_alignment import (
    verify_proposal_asset_alignment,
    AlignmentReport,
    ServiceAlignment,
    PROPOSAL_SERVICE_TO_ASSET,
)


class TestSitePresenceHardening:
    """FIX-5: SitePresenceChecker error handling and indeterminate status."""

    def test_unknown_presence_dict_marks_indeterminate(self):
        """When site_presence_report is a dict with presence_status='unknown',
        assets not in generated_assets should be marked as indeterminate, not missing."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local", "Página de FAQ"],
            generated_assets=[],  # No assets generated
            site_presence_report={
                'presence_status': 'unknown',
                'error': 'Connection timeout',
                'assets_checked': {'optimization_guide': 'unknown', 'faq_page': 'unknown'}
            },
        )

        # Should NOT be in missing
        assert len(report.missing) == 0, (
            f"Expected 0 missing, got {len(report.missing)}: "
            f"{[s.service_name for s in report.missing]}"
        )

        # Should be in indeterminate
        assert len(report.indeterminate) == 2, (
            f"Expected 2 indeterminate, got {len(report.indeterminate)}: "
            f"{[s.service_name for s in report.indeterminate]}"
        )

        indeterminate_services = {s.service_name for s in report.indeterminate}
        assert "SEO Local" in indeterminate_services
        assert "Página de FAQ" in indeterminate_services

        # all_aligned should be True (no missing, indeterminate doesn't count as missing)
        assert report.all_aligned is True

    def test_unknown_presence_status_field(self):
        """Indeterminate entries should have status='indeterminate'."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local"],
            generated_assets=[],
            site_presence_report={
                'presence_status': 'unknown',
                'error': 'SSL Error',
                'assets_checked': {}
            },
        )

        assert len(report.indeterminate) == 1
        entry = report.indeterminate[0]
        assert entry.status == "indeterminate"
        assert entry.is_aligned is False
        assert "could not be verified" in entry.message.lower()
        assert "SitePresenceChecker" in entry.message

    def test_unknown_presence_with_existing_generated_assets(self):
        """Generated assets should still be aligned even if presence is unknown."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local", "Página de FAQ"],
            generated_assets=[
                {"asset_type": "optimization_guide", "confidence_score": 0.9},
            ],
            site_presence_report={
                'presence_status': 'unknown',
                'error': 'Timeout',
                'assets_checked': {}
            },
        )

        # SEO Local has generated asset → aligned
        assert len(report.aligned) == 1
        assert report.aligned[0].service_name == "SEO Local"

        # Página de FAQ not generated + presence unknown → indeterminate
        assert len(report.indeterminate) == 1
        assert report.indeterminate[0].service_name == "Página de FAQ"

        # No missing
        assert len(report.missing) == 0

    def test_none_presence_report_still_works(self):
        """Backward compat: None site_presence_report should still mark as missing."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local"],
            generated_assets=[],
            site_presence_report=None,
        )

        assert len(report.missing) == 1
        assert len(report.indeterminate) == 0
        assert report.missing[0].service_name == "SEO Local"

    def test_normal_site_presence_report_still_works(self):
        """Normal SitePresenceReport object should still work for exists/missing."""
        from modules.asset_generation.site_presence_checker import (
            PresenceCheckResult,
            PresenceStatus,
        )

        # Mock a SitePresenceReport-like object
        from datetime import datetime
        mock_result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
        )
        mock_report = MagicMock()
        mock_report.results = {"whatsapp_button": mock_result}

        report = verify_proposal_asset_alignment(
            proposal_services=["Botón de WhatsApp"],
            generated_assets=[],
            site_presence_report=mock_report,
        )

        # Should be present_in_production, not indeterminate
        assert len(report.present_in_production) == 1
        assert len(report.indeterminate) == 0
        assert len(report.missing) == 0

    def test_to_dict_includes_indeterminate(self):
        """to_dict() should include indeterminate section when non-empty."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local"],
            generated_assets=[],
            site_presence_report={
                'presence_status': 'unknown',
                'error': 'Test error',
                'assets_checked': {}
            },
        )

        d = report.to_dict()
        assert "indeterminate" in d
        assert len(d["indeterminate"]) == 1
        assert d["indeterminate"][0]["service"] == "SEO Local"
        assert d["indeterminate"][0]["asset"] == "optimization_guide"

    def test_to_dict_empty_indeterminate_not_included(self):
        """to_dict() should have empty indeterminate list when no indeterminate entries."""
        report = verify_proposal_asset_alignment(
            proposal_services=["SEO Local"],
            generated_assets=[
                {"asset_type": "optimization_guide", "confidence_score": 0.9},
            ],
            site_presence_report=None,
        )

        d = report.to_dict()
        # indeterminate key should exist but be empty list
        assert "indeterminate" in d
        assert d["indeterminate"] == []
