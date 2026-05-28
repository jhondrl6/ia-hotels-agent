"""
Tests for Asset Semantics Integration in v4_proposal_generator.

Covers: services_table blocks hallucination mappings, BREACH_BY_ASSET
corrected, WhatsApp narrative coherent.

ROICRIII FASE-3 (B1+B2+B6).
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "modules" / "quality"))
sys.path.insert(0, str(Path(__file__).parent.parent))
from modules.quality.asset_semantics_validator import (
    validar_semantica_comercial,
    INVALID_MAPPINGS,
)


class TestMonthlyReportSemanticBlocking:
    """B1: monthly_report must NOT appear in services table for no_faq_schema."""

    def test_monthly_report_no_resuelve_faq(self):
        """monthly_report → no_faq_schema is BLOCKED (hallucination)."""
        is_valid, status = validar_semantica_comercial(
            "no_faq_schema", "monthly_report", "IMPLEMENT"
        )
        assert is_valid is False
        assert "BLOCKED" in status

    def test_monthly_report_no_resuelve_hotel_schema(self):
        """monthly_report → no_hotel_schema is BLOCKED."""
        is_valid, status = validar_semantica_comercial(
            "no_hotel_schema", "monthly_report", "IMPLEMENT"
        )
        assert is_valid is False
        assert "BLOCKED" in status

    def test_monthly_report_no_resuelve_llmstxt(self):
        """monthly_report → missing_llmstxt is BLOCKED."""
        is_valid, status = validar_semantica_comercial(
            "missing_llmstxt", "monthly_report", "IMPLEMENT"
        )
        assert is_valid is False
        assert "BLOCKED" in status


class TestFaqPageSolvesFaq:
    """B1: faq_page correctly solves no_faq_schema."""

    def test_faq_page_si_resuelve_faq(self):
        """faq_page → no_faq_schema is VALID."""
        is_valid, status = validar_semantica_comercial(
            "no_faq_schema", "faq_page", "IMPLEMENT"
        )
        assert is_valid is True
        assert status == "IMPLEMENT"


class TestWhatsAppNarrative:
    """B6: WhatsApp conflict narrative is coherent."""

    def test_whatsapp_button_valid(self):
        """whatsapp_button → no_whatsapp_visible is VALID (buttons can fix gaps)."""
        is_valid, status = validar_semantica_comercial(
            "no_whatsapp_visible", "whatsapp_button", "IMPLEMENT"
        )
        assert is_valid is True
        assert status == "IMPLEMENT"

    def test_whatsapp_conflict_guide_blocked(self):
        """whatsapp_conflict_guide → no_whatsapp_visible is BLOCKED (advisory only)."""
        is_valid, status = validar_semantica_comercial(
            "no_whatsapp_visible", "whatsapp_conflict_guide", "IMPLEMENT"
        )
        assert is_valid is False
        assert "BLOCKED" in status


class TestInvalidMappingsComplete:
    """B1: INVALID_MAPPINGS uses correct pain_id keys (not asset_type keys)."""

    def test_keys_are_pain_ids(self):
        """All INVALID_MAPPINGS keys must be pain_ids (no_ prefix or missing_ prefix)."""
        for key in INVALID_MAPPINGS.keys():
            assert key.startswith("no_") or key.startswith("missing_"), (
                f"INVALID_MAPPINGS key '{key}' is not a pain_id"
            )

    def test_no_asset_type_keys(self):
        """INVALID_MAPPINGS must NOT have asset_type values as keys."""
        asset_types = {"monthly_report", "whatsapp_conflict_guide"}
        for key in INVALID_MAPPINGS.keys():
            assert key not in asset_types, (
                f"INVALID_MAPPINGS contains asset_type '{key}' instead of pain_id"
            )

    def test_mapeos_no_invertidos(self):
        """B1: Verify pain_ids are correct per INVALID_MAPPINGS."""
        # no_faq_schema blocks monthly_report
        assert "monthly_report" in INVALID_MAPPINGS["no_faq_schema"]
        # no_whatsapp_visible blocks whatsapp_conflict_guide
        assert "whatsapp_conflict_guide" in INVALID_MAPPINGS["no_whatsapp_visible"]