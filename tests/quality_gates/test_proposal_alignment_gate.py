"""Tests for proposal_asset_alignment_gate in publication_gates.

Validates Gate 9: Proposal-Asset Alignment Check.
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
        """Gate passes when all 7 promised services have assets."""
        assessment = {
            "generated_assets": [
                {"asset_type": "geo_playbook", "confidence_score": 0.8},
                {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
                {"asset_type": "voice_assistant_guide", "confidence_score": 0.8},
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "7/7" in result.message

    def test_gate_warns_when_assets_missing(self, orchestrator):
        """Gate returns WARNING when assets are missing (not blocking)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "geo_playbook", "confidence_score": 0.8},
            ]
        }
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING, not blocking
        assert result.status == GateStatus.WARNING
        assert "missing" in result.message.lower() or "Missing" in result.message

    def test_gate_with_empty_assets(self, orchestrator):
        """Gate handles empty asset list."""
        assessment = {"generated_assets": []}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING mode
        assert result.status == GateStatus.WARNING

    def test_gate_with_no_assets_key(self, orchestrator):
        """Gate handles missing generated_assets key."""
        assessment = {}
        result = orchestrator._proposal_asset_alignment_gate(assessment)
        assert result.passed is True  # WARNING mode
        assert result.status == GateStatus.WARNING

    def test_gate_result_has_details(self, orchestrator):
        """Gate result must include alignment report details."""
        assessment = {
            "generated_assets": [
                {"asset_type": "geo_playbook", "confidence_score": 0.8},
                {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
                {"asset_type": "voice_assistant_guide", "confidence_score": 0.8},
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
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
                {"asset_type": "geo_playbook", "confidence_score": 0.8},
                {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
                {"asset_type": "voice_assistant_guide", "confidence_score": 0.8},
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
                {"asset_type": "whatsapp_button", "confidence_score": 0.8},
                {"asset_type": "hotel_schema", "confidence_score": 0.8},
                {"asset_type": "monthly_report", "confidence_score": 0.8},
            ],
        }
        results = orchestrator.run_all(assessment)
        gate_names = [r.gate_name for r in results]
        assert "proposal_asset_alignment" in gate_names
