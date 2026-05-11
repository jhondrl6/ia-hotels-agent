"""Tests for proposal_asset_alignment_gate in publication_gates.

Validates Gate 9: Proposal-Asset Alignment Check.

FASE-2: Updated to reflect 8 services (7 base + AEO).
"""

import pytest
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


class TestProposalAssetAlignmentGate:
    """Test Gate 9: proposal_asset_alignment."""

    @pytest.fixture
    def orchestrator(self):
        """Orchestrator with default config."""
        return PublicationGatesOrchestrator(PublicationGateConfig())

    def test_gate_exists_in_orchestrator(self, orchestrator):
        """Gate 'proposal_asset_alignment' must be registered."""
        assert "proposal_asset_alignment" in orchestrator.gates

    def test_gate_passes_when_all_assets_present(self, orchestrator):
        """Gate passes when all 8 promised services have assets (FASE-2)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "8/8" in result.message

    def test_gate_warns_when_alignment_above_80_pct(self, orchestrator):
        """FASE-2: Gate returns WARNING when alignment >= 80% (some missing but acceptable)."""
        # 7 out of 8 = 87.5% alignment, above 80% threshold → WARNING (not blocking)
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                # Missing: llms_txt
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING, not blocking
        assert result.status == GateStatus.WARNING
        assert "missing" in result.message.lower() or "Missing" in result.message

    def test_gate_detects_llms_txt_missing(self, orchestrator):
        """FASE-2: Gate detects when llms_txt is missing."""
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                # llms_txt MISSING
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING, not blocking
        assert result.status == GateStatus.WARNING
        assert "Optimización para IA Generativa" in result.message

    def test_gate_blocks_when_alignment_below_80_pct(self, orchestrator):
        """FASE-2: Gate BLOCKS when alignment < 80% (below policy threshold)."""
        # 6 out of 8 = 75% alignment, below 80% threshold → BLOCKED
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                # Missing: open_graph, llms_txt
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED
        assert "below 80%" in result.suggestion.lower() or "below 80%" in result.message.lower()

    def test_gate_passes_with_present_in_production(self, orchestrator):
        """FASE-2: Gate PASSES when aligned + present_in_production >= 80%."""
        from unittest.mock import MagicMock
        # 5 aligned + 2 present_in_production out of 8 = 87.5% → PASSES (WARNING)
        mock_result = MagicMock()
        mock_result.status.value = "exists"
        mock_report = MagicMock()
        mock_report.results = {
            "faq_page": mock_result,
            "open_graph": mock_result,
        }

        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                # Missing: faq_page, open_graph, llms_txt
            ],
            "site_presence_report": mock_report,
            "hotel_url": "https://example.com",
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.WARNING  # 87.5% aligned, 1 missing → WARNING
        assert result.value >= 0.8

    def test_gate_blocks_when_alignment_0_pct(self, orchestrator):
        """Gate BLOCKS when alignment = 0% (no assets at all)."""
        assessment = {"generated_assets": []}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED

    def test_gate_blocks_when_no_assets_key(self, orchestrator):
        """Gate BLOCKS when generated_assets key is missing (0% alignment)."""
        assessment = {}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED

    def test_gate_result_has_details(self, orchestrator):
        """Gate result must include alignment report details (FASE-2: 8 services)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert "total_services" in result.details
        assert result.details["total_services"] == 8

    def test_full_run_all_includes_alignment_gate(self, orchestrator):
        """run_all() must include the proposal_asset_alignment gate."""
        assessment = {
            "coherence_score": 0.85,
            "evidence_coverage": 0.96,
            "hard_contradictions": [],
            "critical_recall": 0.95,
            "financial_data": {"occupancy_rate": 75.0, "direct_channel_percentage": 30.0, "adr_cop": 250000},
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "org_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ],
        }
        results = orchestrator.run_all(assessment)
        gate_names = [r.gate_name for r in results]
        assert "proposal_asset_alignment" in gate_names
