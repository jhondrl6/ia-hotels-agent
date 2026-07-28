"""Tests for FASE-2 (DT4-R2): Site Presence Adapter — normalize_site_presence."""

import dataclasses
import pytest
from datetime import datetime
from modules.asset_generation.site_presence_adapter import normalize_site_presence
from modules.asset_generation.site_presence_checker import (
    SitePresenceReport,
    PresenceCheckResult,
    PresenceStatus,
)
from modules.commercial_documents.coherence_validator import CoherenceValidator


class TestNormalizeSitePresence:
    """Tests for normalize_site_presence() with 3 input types."""

    def _make_report(self, whatsapp_status=PresenceStatus.EXISTS):
        """Helper: create a SitePresenceReport dataclass."""
        result = PresenceCheckResult(
            asset_type="whatsapp_button",
            status=whatsapp_status,
            verified_at=datetime(2026, 7, 27, 14, 4, 48),
            site_url="https://zione.co/",
            confidence=1.0,
        )
        return SitePresenceReport(
            site_url="https://zione.co/",
            checked_at=datetime(2026, 7, 27, 14, 4, 48),
            results={"whatsapp_button": result},
        )

    # ─── Test 1: From dataclass ───────────────────────────────────────────

    def test_normalize_from_dataclass(self):
        """SitePresenceReport → canonical dict with top-level keys."""
        report = self._make_report()
        result = normalize_site_presence(report)

        assert result["site_url"] == "https://zione.co/"
        assert result["checked_at"] == "2026-07-27T14:04:48"
        assert "results" in result
        assert result["results"]["whatsapp_button"]["status"] == "exists"
        assert result["results"]["whatsapp_button"]["site_verified"] is True
        assert result["results"]["whatsapp_button"]["confidence"] == 1.0
        # Top-level key for CoherenceValidator direct access
        assert result["whatsapp_button"]["status"] == "exists"

    # ─── Test 2: From dataclasses.asdict() ────────────────────────────────

    def test_normalize_from_asdict(self):
        """dataclasses.asdict(report) → canonical dict with string status."""
        report = self._make_report()
        asdict_result = dataclasses.asdict(report)
        # asdict() preserves enum values, not strings
        result = normalize_site_presence(asdict_result)

        assert result["results"]["whatsapp_button"]["status"] == "exists"
        assert result["results"]["whatsapp_button"]["site_verified"] is True
        assert result["whatsapp_button"]["status"] == "exists"

    # ─── Test 3: From None ────────────────────────────────────────────────

    def test_normalize_from_none(self):
        """None → {'results': {}} (empty, no asset keys)."""
        result = normalize_site_presence(None)

        assert result == {"results": {}}

    # ─── Test 4: Status enum → string ─────────────────────────────────────

    @pytest.mark.parametrize("enum_val,expected_str", [
        (PresenceStatus.EXISTS, "exists"),
        (PresenceStatus.EXISTS_WITH_ISSUES, "exists_with_issues"),
        (PresenceStatus.NOT_EXISTS, "not_exists"),
        (PresenceStatus.VERIFICATION_FAILED, "verification_failed"),
        (PresenceStatus.REDUNDANT, "redundant"),
    ])
    def test_normalize_status_enum_to_string(self, enum_val, expected_str):
        """All PresenceStatus enum values → lowercase strings."""
        report = self._make_report(whatsapp_status=enum_val)
        result = normalize_site_presence(report)

        assert result["results"]["whatsapp_button"]["status"] == expected_str
        assert result["whatsapp_button"]["status"] == expected_str

    # ─── Test 5: WhatsApp exists boost ─────────────────────────────────────

    def test_whatsapp_exists_boost(self):
        """CoherenceValidator receives site_whatsapp_exists=True when presence=exists."""
        from unittest.mock import MagicMock
        from modules.commercial_documents.data_structures import ValidationSummary

        validator = CoherenceValidator()

        # Build canonical site_presence with whatsapp_button = exists
        report = self._make_report(whatsapp_status=PresenceStatus.EXISTS)
        canonical = normalize_site_presence(report)

        # Mock assets list with a whatsapp_button asset
        mock_asset = MagicMock()
        mock_asset.asset_type = "whatsapp_button"
        assets = [mock_asset]

        # Mock validation_summary with low confidence whatsapp_number
        mock_field = MagicMock()
        mock_field.confidence = 0.25  # Very low — should be boosted
        mock_summary = MagicMock(spec=ValidationSummary)
        mock_summary.get_field.return_value = mock_field

        check = validator._check_whatsapp_verified(
            assets=assets,
            validation_summary=mock_summary,
            whatsapp_html_detected=False,
            site_presence_report=canonical,
        )

        # With site_presence boost, confidence_score should be >= 0.95
        # (the boost sets max(0.25, 0.95) = 0.95)
        assert check.score >= 0.95, (
            f"Expected score >= 0.95 with site_presence boost, "
            f"got {check.score:.2f}"
        )

    def test_whatsapp_not_exists_no_boost(self):
        """CoherenceValidator does NOT boost when presence=not_exists."""
        from unittest.mock import MagicMock
        from modules.commercial_documents.data_structures import ValidationSummary

        validator = CoherenceValidator()

        report = self._make_report(whatsapp_status=PresenceStatus.NOT_EXISTS)
        canonical = normalize_site_presence(report)

        mock_asset = MagicMock()
        mock_asset.asset_type = "whatsapp_button"
        assets = [mock_asset]

        mock_field = MagicMock()
        mock_field.confidence = 0.25  # Low confidence, no boost expected
        mock_summary = MagicMock(spec=ValidationSummary)
        mock_summary.get_field.return_value = mock_field

        check = validator._check_whatsapp_verified(
            assets=assets,
            validation_summary=mock_summary,
            whatsapp_html_detected=False,
            site_presence_report=canonical,
        )

        # Without boost, score stays at the confidence_level_to_score mapping
        # 0.25 confidence → score should be 0.25 (very low)
        assert check.score < 0.95, (
            f"Expected score < 0.95 WITHOUT site_presence boost, "
            f"got {check.score:.2f}"
        )
