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
    PROPOSAL_SERVICE_TO_ASSET,
    verify_proposal_asset_alignment,
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


class TestCorridaCSemantics:
    """FASE-SR-A (N1) + FASE-SR-B (D-PF1): ambos reportes producen el MISMO
    resultado para el escenario corrida C (Hotel Salento Real, 2026-08-27
    18:30).

    7 servicios prometidos: 2 LINKED (org_schema, faq_page), 1 MISSING con pain
    (hotel_schema), 3 NO_BREACH "no comprometidos, fuera del coverage"
    (SEO Local, WhatsApp, Open Graph) y llms_txt (NO_BREACH en matriz) resuelto
    por SitePresence (1 ya en producción). Semántica correcta: unresolved=1 —
    solo el MISSING con pain es "sin cubrir". Este test certifica el fin del
    4-vs-1 (AC3).

    FASE-SR-B (D-PF1): coverage_ratio se calcula sobre el conjunto actionable
    (total − NO_BREACH-no-presencia = 4) → 3/4 = 0.75. Estado intermedio
    documentado: 0.75 < 0.80 hasta SR-E (tras SR-E, el pain no_hotel_schema
    desaparece → actionable=3 → coverage 3/3 = 1.0).
    """

    # pain_ids REALES de PainSolutionMapper.PAIN_SOLUTION_MAP (fuente del
    # contrato — L3: tests contra fuente dinámica, no valores inventados):
    #   no_hotel_schema → hotel_schema · no_org_schema → org_schema ·
    #   no_faq_schema → faq_page
    PAIN_LEDGER = [
        {"pain_id": "no_hotel_schema"},
        {"pain_id": "no_org_schema"},
        {"pain_id": "no_faq_schema"},
    ]
    GENERATED_ASSETS = [
        {"asset_type": "org_schema", "confidence_score": 0.9},
        {"asset_type": "faq_page", "confidence_score": 0.85},
    ]
    # Snapshot canónico (misma forma que site_presence_adapter
    # .normalize_site_presence: clave "results" + claves planas por asset-type).
    SITE_PRESENCE = {
        "results": {"llms_txt": {"status": "exists"}},
        "llms_txt": {"status": "exists"},
    }

    def _semantic_entries(self):
        """Misma derivación que usa el gate (cableado FASE-SR-A en
        publication_gates): AssetAlignmentMatrix.build desde pain_ledger.

        FASE-C: con ``site_presence_report``, igual que el gate — la presencia
        también compromete (D-PF1) y ambas rutas deben ver el mismo conjunto.
        """
        from modules.delivery.delivery_context import DeliveryContext

        matrix = AssetAlignmentMatrix.build(
            delivery_context=DeliveryContext(),
            pain_ledger=self.PAIN_LEDGER,
            generated_assets=self.GENERATED_ASSETS,
            site_presence_report=self.SITE_PRESENCE,
        )
        return matrix.entries

    def _gate_report(self):
        """AlignmentReport real (mismo verify que consume el gate)."""
        return verify_proposal_asset_alignment(
            proposal_services=list(PROPOSAL_SERVICE_TO_ASSET.keys()),
            generated_assets=self.GENERATED_ASSETS,
            site_presence_report=self.SITE_PRESENCE,
        )

    def test_corrida_c_same_unresolved_both_paths(self):
        """from_alignment_report y matriz+SitePresence → MISMO unresolved."""
        from_report = AlignmentResult.from_alignment_report(
            self._gate_report(),
            semantic_entries=self._semantic_entries(),
            site_presence_report=self.SITE_PRESENCE,
        )
        matrix = AssetAlignmentMatrix(entries=self._semantic_entries())
        from_matrix = AlignmentResult.from_asset_alignment_matrix(
            matrix, self.SITE_PRESENCE
        )

        # Fin del 4-vs-1: mismo número en ambos reportes del MISMO run
        assert from_report.unresolved == from_matrix.unresolved == 1  # hotel_schema
        assert from_report.generated_aligned == from_matrix.generated_aligned == 2
        assert from_report.present_in_production == from_matrix.present_in_production == 1
        # FASE-C (AC5): la propuesta dinámica no promete servicios sin brecha,
        # así que NO_BREACH desaparece por construcción — no por resta.
        assert from_report.no_breach == from_matrix.no_breach == 0
        # Los denominadores convergen: total == actionable (se disuelve la
        # tautología coverage_ratio == 1.000 del dossier §9.2).
        assert from_report.promised_services_total == from_matrix.promised_services_total
        assert from_report.actionable_total == from_report.promised_services_total
        assert from_matrix.actionable_total == from_matrix.promised_services_total
        # 3 comprometidos por pain + 1 por presencia = 4; coverage 3/4 = 0.75
        assert from_report.actionable_total == 4
        assert from_report.coverage_ratio == pytest.approx(3 / 4)
        assert from_matrix.coverage_ratio == pytest.approx(3 / 4)
        assert from_report.passed is False
        assert from_matrix.passed is False
        # Mensaje G9 derivado del helper, coherente con unresolved y coverage (AC3)
        assert from_report.message == from_matrix.message
        assert "3/4" in from_report.message
        assert "1 sin cubrir" in from_report.message
        assert "sin brecha" not in from_report.message

    def test_no_breach_arithmetic_coherence(self):
        """El mensaje es coherente con sus propios datos:
        effective_total + unresolved + no_breach == promised_services_total."""
        result = AlignmentResult.from_alignment_report(
            self._gate_report(),
            semantic_entries=self._semantic_entries(),
            site_presence_report=self.SITE_PRESENCE,
        )
        assert (
            result.effective_total + result.unresolved + result.no_breach
            == result.promised_services_total
        )

    def test_legacy_path_without_semantic_entries_counts_missing(self):
        """Sin semantic_entries (pain_ledger ausente), el fallback cuenta
        report.missing vía el MISMO helper — sin conteos paralelos."""
        result = AlignmentResult.from_alignment_report(self._gate_report())
        # report.missing = SEO Local, WhatsApp, hotel_schema, Open Graph = 4
        assert result.unresolved == 4
        assert result.no_breach == 0  # taxonomía pain-driven no conocible aquí
