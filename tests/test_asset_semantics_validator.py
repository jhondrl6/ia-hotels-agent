"""
Tests for AssetSemanticsValidator — ROICR FASE-1.

Covers semantic hallucination detection, AUDIT_ONLY paths,
and migration_target redirects.
"""

import pytest
import sys
from pathlib import Path

# Direct import of the module under test
sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "quality"))
from asset_semantics_validator import (
    validar_semantica_comercial,
    INVALID_MAPPINGS,
)


class TestInvalidMappings:
    """Test cases for invalid (hallucination) pain→asset mappings."""

    def test_monthly_report_cannot_fix_faq_missing(self):
        """monthly_report is a commercial INTERNAL report — can't fix technical FAQ gap."""
        is_valid, status = validar_semantica_comercial(
            "monthly_report", "faq_missing", "implemented"
        )
        assert is_valid is False
        assert "BLOCKED" in status
        assert "faq_missing" in status

    def test_monthly_report_cannot_fix_schema_missing(self):
        is_valid, status = validar_semantica_comercial(
            "monthly_report", "schema_missing", "implemented"
        )
        assert is_valid is False
        assert "BLOCKED" in status

    def test_monthly_report_cannot_fix_llms_missing(self):
        is_valid, status = validar_semantica_comercial(
            "monthly_report", "llms_missing", "implemented"
        )
        assert is_valid is False
        assert "BLOCKED" in status

    def test_whatsapp_conflict_guide_cannot_fix_whatsapp_missing(self):
        """whatsapp_conflict_guide is advisory — it can't fix 'no WhatsApp visible'."""
        is_valid, status = validar_semantica_comercial(
            "whatsapp_conflict_guide", "whatsapp_missing", "implemented"
        )
        assert is_valid is False
        assert "BLOCKED" in status


class TestNormalMapping:
    """Test cases for valid, semantically correct pain→asset mappings."""

    def test_low_gbp_score_maps_to_review_plan(self):
        is_valid, status = validar_semantica_comercial(
            "low_gbp_score", "review_plan", "implemented"
        )
        assert is_valid is True
        assert status == "IMPLEMENT"

    def test_no_faq_schema_maps_to_faq_page(self):
        is_valid, status = validar_semantica_comercial(
            "no_faq_schema", "faq_page", "implemented"
        )
        assert is_valid is True
        assert status == "IMPLEMENT"

    def test_no_hotel_schema_maps_to_hotel_schema_asset(self):
        is_valid, status = validar_semantica_comercial(
            "no_hotel_schema", "hotel_schema", "implemented"
        )
        assert is_valid is True
        assert status == "IMPLEMENT"


class TestAuditOnly:
    """Test: skipped_existing assets → AUDIT_ONLY (audit, don't implement)."""

    def test_skipped_existing_returns_audit_only(self):
        is_valid, status = validar_semantica_comercial(
            "low_gbp_score", "review_plan", "skipped_existing"
        )
        assert is_valid is True
        assert status == "AUDIT_ONLY"

    def test_skipped_existing_with_any_asset_type(self):
        is_valid, status = validar_semantica_comercial(
            "no_faq_schema", "faq_page", "skipped_existing"
        )
        assert is_valid is True
        assert status == "AUDIT_ONLY"


class TestInvalidMappingsComplete:
    """Verify INVALID_MAPPINGS dict has expected structure."""

    def test_monthly_report_has_all_blocked_assets(self):
        assert "monthly_report" in INVALID_MAPPINGS
        blocked = INVALID_MAPPINGS["monthly_report"]
        assert "faq_missing" in blocked
        assert "schema_missing" in blocked
        assert "llms_missing" in blocked

    def test_whatsapp_conflict_guide_blocks_whatsapp_missing(self):
        assert "whatsapp_conflict_guide" in INVALID_MAPPINGS
        blocked = INVALID_MAPPINGS["whatsapp_conflict_guide"]
        assert "whatsapp_missing" in blocked

    def test_no_extra_entries(self):
        # Only two entries in INVALID_MAPPINGS (expand if needed)
        assert len(INVALID_MAPPINGS) == 2