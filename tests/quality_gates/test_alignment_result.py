"""Tests for AlignmentResult — DT4-N5-ALIGNMENT (FASE-4).

Validates that the canonical AlignmentResult DTO produces consistent
totals from both code paths:
1. from_alignment_report() — used by publication_gates.py
2. from_asset_alignment_matrix() — used by delivery_quality_report.py
"""

import pytest
from modules.quality_gates.alignment_result import AlignmentResult
from modules.asset_generation.proposal_asset_alignment import (
    AlignmentReport,
    ServiceAlignment,
    AssetAlignmentMatrix,
    ProposalAssetMatrixEntry,
    ALL_PROMISED_SERVICES,
)


class TestAlignmentResultFromReport:
    """Test AlignmentResult.from_alignment_report() — publication gates path."""

    def test_all_7_aligned_no_presence(self):
        """7 generated, 0 in production → coverage 7/7."""
        report = AlignmentReport(
            aligned=[
                ServiceAlignment("SEO Local", "optimization_guide", True, "aligned", 0.9),
                ServiceAlignment("Botón de WhatsApp", "whatsapp_button", True, "aligned", 0.8),
                ServiceAlignment("Schema Hotel", "hotel_schema", True, "aligned", 0.95),
                ServiceAlignment("Schema Organization", "org_schema", True, "aligned", 0.9),
                ServiceAlignment("Página de FAQ", "faq_page", True, "aligned", 0.85),
                ServiceAlignment("Open Graph", "open_graph", True, "aligned", 0.7),
                ServiceAlignment("LLMs.txt", "llms_txt", True, "aligned", 0.8),
            ],
            present_in_production=[],
        )
        result = AlignmentResult.from_alignment_report(report)

        assert result.promised_services_total == 7
        assert result.generated_aligned == 7
        assert result.present_in_production == 0
        assert result.unresolved == 0
        assert result.coverage_ratio == 1.0
        assert result.passed is True
        assert result.effective_total == 7
        assert "7/7" in result.message

    def test_5_aligned_2_in_production(self):
        """5 generated + 2 in production → coverage 7/7."""
        report = AlignmentReport(
            aligned=[
                ServiceAlignment("SEO Local", "optimization_guide", True, "aligned", 0.9),
                ServiceAlignment("Schema Hotel", "hotel_schema", True, "aligned", 0.95),
                ServiceAlignment("Schema Organization", "org_schema", True, "aligned", 0.9),
                ServiceAlignment("Página de FAQ", "faq_page", True, "aligned", 0.85),
                ServiceAlignment("LLMs.txt", "llms_txt", True, "aligned", 0.8),
            ],
            present_in_production=[
                ServiceAlignment("Botón de WhatsApp", "whatsapp_button", False,
                                 "present_in_production", presence_verified=True,
                                 presence_status="exists"),
                ServiceAlignment("Open Graph", "open_graph", False,
                                 "present_in_production", presence_verified=True,
                                 presence_status="exists"),
            ],
        )
        result = AlignmentResult.from_alignment_report(report)

        assert result.promised_services_total == 7  # 5 aligned + 2 present
        assert result.generated_aligned == 5
        assert result.present_in_production == 2
        assert result.unresolved == 0
        assert result.coverage_ratio == 1.0
        assert result.passed is True
        assert result.effective_total == 7
        assert "7/7" in result.message
        assert "5 generados" in result.message
        assert "2 ya en producción" in result.message
        assert "Botón de WhatsApp" in result.present_assets
        assert "Open Graph" in result.present_assets

    def test_5_aligned_0_presence_2_missing(self):
        """5 generated, 0 in production, 2 missing → coverage 5/7."""
        report = AlignmentReport(
            aligned=[
                ServiceAlignment("SEO Local", "optimization_guide", True, "aligned", 0.9),
                ServiceAlignment("Botón de WhatsApp", "whatsapp_button", True, "aligned", 0.8),
                ServiceAlignment("Schema Hotel", "hotel_schema", True, "aligned", 0.95),
                ServiceAlignment("Schema Organization", "org_schema", True, "aligned", 0.9),
                ServiceAlignment("Página de FAQ", "faq_page", True, "aligned", 0.85),
            ],
            missing=[
                ServiceAlignment("Open Graph", "open_graph", False, "missing"),
                ServiceAlignment("LLMs.txt", "llms_txt", False, "missing"),
            ],
            present_in_production=[],
        )
        result = AlignmentResult.from_alignment_report(report)

        assert result.promised_services_total == 7
        assert result.generated_aligned == 5
        assert result.present_in_production == 0
        assert result.unresolved == 2
        assert result.coverage_ratio == pytest.approx(5 / 7)
        assert result.passed is False
        assert "5/7" in result.message
        assert "2 sin cubrir" in result.message


class TestAlignmentResultFromMatrix:
    """Test AlignmentResult.from_asset_alignment_matrix() — delivery report path."""

    def test_all_linked_delivery_ready(self):
        """7 LINKED → delivery ready, coverage 7/7."""
        entries = [
            ProposalAssetMatrixEntry("SEO Local", ["pain_seo"], "optimization_guide",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Botón de WhatsApp", ["pain_whatsapp"], "whatsapp_button",
                                     None, 0.8, "LINKED"),
            ProposalAssetMatrixEntry("Schema Hotel", ["pain_schema"], "hotel_schema",
                                     None, 0.95, "LINKED"),
            ProposalAssetMatrixEntry("Schema Organization", ["pain_schema"], "org_schema",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Página de FAQ", ["pain_faq"], "faq_page",
                                     None, 0.85, "LINKED"),
            ProposalAssetMatrixEntry("Open Graph", ["pain_seo"], "open_graph",
                                     None, 0.7, "LINKED"),
            ProposalAssetMatrixEntry("LLMs.txt", ["pain_seo"], "llms_txt",
                                     None, 0.8, "LINKED"),
        ]
        matrix = AssetAlignmentMatrix(entries=entries)
        result = AlignmentResult.from_asset_alignment_matrix(matrix)

        assert result.promised_services_total == 7
        assert result.generated_aligned == 7
        assert result.present_in_production == 0
        assert result.unresolved == 0
        assert result.coverage_ratio == 1.0
        assert result.passed is True
        assert matrix.is_delivery_ready() == result.passed

    def test_5_linked_2_present_in_production(self):
        """5 LINKED + 2 PRESENT_IN_PRODUCTION → delivery ready, coverage 7/7."""
        entries = [
            ProposalAssetMatrixEntry("SEO Local", ["pain_seo"], "optimization_guide",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Botón de WhatsApp", ["pain_whatsapp"], "whatsapp_button",
                                     None, 0.0, "PRESENT_IN_PRODUCTION"),
            ProposalAssetMatrixEntry("Schema Hotel", ["pain_schema"], "hotel_schema",
                                     None, 0.95, "LINKED"),
            ProposalAssetMatrixEntry("Schema Organization", ["pain_schema"], "org_schema",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Página de FAQ", ["pain_faq"], "faq_page",
                                     None, 0.85, "LINKED"),
            ProposalAssetMatrixEntry("Open Graph", ["pain_seo"], "open_graph",
                                     None, 0.0, "PRESENT_IN_PRODUCTION"),
            ProposalAssetMatrixEntry("LLMs.txt", ["pain_seo"], "llms_txt",
                                     None, 0.8, "LINKED"),
        ]
        matrix = AssetAlignmentMatrix(entries=entries)
        result = AlignmentResult.from_asset_alignment_matrix(matrix)

        assert result.promised_services_total == 7
        assert result.generated_aligned == 5
        assert result.present_in_production == 2
        assert result.unresolved == 0
        assert result.coverage_ratio == 1.0
        assert result.passed is True
        assert "Botón de WhatsApp" in result.present_assets
        assert "Open Graph" in result.present_assets
        # Delivery ready and alignment passed should agree
        assert matrix.is_delivery_ready() == result.passed

    def test_missing_assets_not_delivery_ready(self):
        """MISSING_ASSET entries → not delivery ready, unresolved > 0."""
        entries = [
            ProposalAssetMatrixEntry("SEO Local", ["pain_seo"], "optimization_guide",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Botón de WhatsApp", ["pain_whatsapp"], "whatsapp_button",
                                     None, 0.0, "MISSING_ASSET"),
            ProposalAssetMatrixEntry("Schema Hotel", ["pain_schema"], "hotel_schema",
                                     None, 0.95, "LINKED"),
            ProposalAssetMatrixEntry("Schema Organization", ["pain_schema"], "org_schema",
                                     None, 0.0, "MISSING_ASSET"),
            ProposalAssetMatrixEntry("Página de FAQ", ["pain_faq"], "faq_page",
                                     None, 0.85, "LINKED"),
            ProposalAssetMatrixEntry("Open Graph", ["pain_seo"], "open_graph",
                                     None, 0.7, "LINKED"),
            ProposalAssetMatrixEntry("LLMs.txt", ["pain_seo"], "llms_txt",
                                     None, 0.8, "LINKED"),
        ]
        matrix = AssetAlignmentMatrix(entries=entries)
        result = AlignmentResult.from_asset_alignment_matrix(matrix)

        assert result.promised_services_total == 7
        assert result.generated_aligned == 5
        assert result.unresolved == 2
        assert result.coverage_ratio == pytest.approx(5 / 7)
        assert result.passed is False
        assert matrix.is_delivery_ready() == result.passed


class TestSemanticEquality:
    """Verify both paths produce the same canonical representation."""

    def test_same_totals_from_both_paths(self):
        """AlignmentReport and AssetAlignmentMatrix with same data → same totals."""
        # ── Path 1: AlignmentReport ──
        report = AlignmentReport(
            aligned=[
                ServiceAlignment("SEO Local", "optimization_guide", True, "aligned", 0.9),
                ServiceAlignment("Schema Hotel", "hotel_schema", True, "aligned", 0.95),
                ServiceAlignment("Schema Organization", "org_schema", True, "aligned", 0.9),
                ServiceAlignment("Página de FAQ", "faq_page", True, "aligned", 0.85),
                ServiceAlignment("LLMs.txt", "llms_txt", True, "aligned", 0.8),
            ],
            present_in_production=[
                ServiceAlignment("Botón de WhatsApp", "whatsapp_button", False,
                                 "present_in_production", presence_verified=True),
                ServiceAlignment("Open Graph", "open_graph", False,
                                 "present_in_production", presence_verified=True),
            ],
        )
        from_report = AlignmentResult.from_alignment_report(report)

        # ── Path 2: AssetAlignmentMatrix ──
        entries = [
            ProposalAssetMatrixEntry("SEO Local", ["pain_seo"], "optimization_guide",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Botón de WhatsApp", ["pain_whatsapp"], "whatsapp_button",
                                     None, 0.0, "PRESENT_IN_PRODUCTION"),
            ProposalAssetMatrixEntry("Schema Hotel", ["pain_schema"], "hotel_schema",
                                     None, 0.95, "LINKED"),
            ProposalAssetMatrixEntry("Schema Organization", ["pain_schema"], "org_schema",
                                     None, 0.9, "LINKED"),
            ProposalAssetMatrixEntry("Página de FAQ", ["pain_faq"], "faq_page",
                                     None, 0.85, "LINKED"),
            ProposalAssetMatrixEntry("Open Graph", ["pain_seo"], "open_graph",
                                     None, 0.0, "PRESENT_IN_PRODUCTION"),
            ProposalAssetMatrixEntry("LLMs.txt", ["pain_seo"], "llms_txt",
                                     None, 0.8, "LINKED"),
        ]
        matrix = AssetAlignmentMatrix(entries=entries)
        from_matrix = AlignmentResult.from_asset_alignment_matrix(matrix)

        # ── Semantic equality: same totals ──
        assert from_report.promised_services_total == from_matrix.promised_services_total == 7
        assert from_report.generated_aligned == from_matrix.generated_aligned == 5
        assert from_report.present_in_production == from_matrix.present_in_production == 2
        assert from_report.unresolved == from_matrix.unresolved == 0
        assert from_report.coverage_ratio == from_matrix.coverage_ratio == 1.0
        assert from_report.passed == from_matrix.passed is True
        assert from_report.effective_total == from_matrix.effective_total == 7

        # ── Both serialized forms are consistent ──
        report_dict = from_report.to_dict()
        matrix_dict = from_matrix.to_dict()

        for key in ("promised_services_total", "generated_aligned",
                     "present_in_production", "unresolved", "coverage_ratio"):
            assert report_dict[key] == matrix_dict[key], (
                f"Mismatch in '{key}': {report_dict[key]} != {matrix_dict[key]}"
            )

    def test_to_dict_contains_all_required_keys(self):
        """to_dict() produces the canonical contract fields."""
        result = AlignmentResult(
            promised_services_total=7,
            generated_aligned=5,
            present_in_production=2,
            unresolved=0,
            coverage_ratio=1.0,
            present_assets=["Botón de WhatsApp", "Open Graph"],
        )
        d = result.to_dict()

        assert d["promised_services_total"] == 7
        assert d["generated_aligned"] == 5
        assert d["present_in_production"] == 2
        assert d["unresolved"] == 0
        assert d["coverage_ratio"] == 1.0
        assert d["present_assets"] == ["Botón de WhatsApp", "Open Graph"]
        assert d["passed"] is True
        assert d["effective_total"] == 7
        assert "message" in d
        assert "7/7" in d["message"]
