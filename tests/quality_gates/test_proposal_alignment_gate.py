"""Tests for proposal_asset_alignment_gate in publication_gates.

Validates Gate 9: Proposal-Asset Alignment Check.

FASE-SOL2-B: Updated to reflect 7 services including llms_txt.
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
        """Gate passes when all 7 promised services have assets (FASE-SOL2-B)."""
        # The 7 services are: optimization_guide, whatsapp_button, hotel_schema,
        # monthly_report, faq_page, open_graph, llms_txt
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "7/7" in result.message

    def test_gate_warns_when_alignment_above_50_pct(self, orchestrator):
        """Gate returns WARNING when alignment >= 50% (some missing but acceptable)."""
        # 4 out of 7 = 57% alignment, above 50% threshold → WARNING (not blocking)
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                # Missing: faq_page, open_graph, llms_txt
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING, not blocking
        assert result.status == GateStatus.WARNING
        assert "missing" in result.message.lower() or "Missing" in result.message

    def test_gate_detects_llms_txt_missing(self, orchestrator):
        """FASE-SOL2-B: Gate detects when llms_txt is missing (GAP-C closure)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
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

    def test_gate_blocks_when_alignment_below_50_pct(self, orchestrator):
        """Gate BLOCKS when alignment < 50% (below policy threshold)."""
        # 1 out of 7 = 14% alignment, below 50% threshold → BLOCKED
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED
        assert "below 50%" in result.suggestion.lower() or "below 50%" in result.message.lower()

    def test_gate_blocks_when_alignment_0_pct(self, orchestrator):
        """Gate BLOCKS when alignment = 0% (no assets at all)."""
        # 0 out of 7 = 0% alignment, below 50% threshold → BLOCKED
        assessment = {"generated_assets": []}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED

    def test_gate_blocks_when_no_assets_key(self, orchestrator):
        """Gate BLOCKS when generated_assets key is missing (0% alignment)."""
        # No assets at all = 0% alignment → BLOCKED
        assessment = {}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is False  # BLOCKED
        assert result.status == GateStatus.BLOCKED

    def test_gate_result_has_details(self, orchestrator):
        """Gate result must include alignment report details (FASE-SOL2-B: 7 services)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert "total_services" in result.details
        assert result.details["total_services"] == 7

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
                {"asset_type": "monthly_report", "confidence_score": 0.8},
                {"asset_type": "faq_page", "confidence_score": 0.8},
                {"asset_type": "open_graph", "confidence_score": 0.8},
                {"asset_type": "llms_txt", "confidence_score": 0.8},
            ],
        }
        results = orchestrator.run_all(assessment)
        gate_names = [r.gate_name for r in results]
        assert "proposal_asset_alignment" in gate_names
