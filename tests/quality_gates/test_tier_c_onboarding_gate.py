"""Tests for tier_c_onboarding_gate (FASE-3 FIX-10).

Validates Gate: tier_c_onboarding_required blocks Tier C proposals
without real data onboarding.
"""

import pytest
from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
)


class TestTierCOnboardingGate:
    """Test FIX-10: Tier C onboarding gate."""

    @pytest.fixture
    def orchestrator(self):
        """Orchestrator with default config."""
        return PublicationGatesOrchestrator(PublicationGateConfig())

    def test_gate_exists_in_orchestrator(self, orchestrator):
        """Gate 'tier_c_onboarding_required' must be registered."""
        assert "tier_c_onboarding_required" in orchestrator.gates

    def test_tier_c_blocked(self, orchestrator):
        """Tier C assessment must be BLOCKED (not publishable without real data)."""
        assessment = {
            "financial_evidence_tier": "C",
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
            ],
        }
        result = orchestrator._tier_c_onboarding_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "Tier C" in result.message
        assert "onboarding" in result.message.lower() or "preliminar" in result.message.lower()

    def test_tier_b_passes(self, orchestrator):
        """Tier B assessment must PASS (has real data)."""
        assessment = {
            "financial_evidence_tier": "B",
        }
        result = orchestrator._tier_c_onboarding_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_tier_a_passes(self, orchestrator):
        """Tier A assessment must PASS (has verified data)."""
        assessment = {
            "financial_evidence_tier": "A",
        }
        result = orchestrator._tier_c_onboarding_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_default_to_c_when_missing(self, orchestrator):
        """Missing financial_evidence_tier defaults to C (most restrictive)."""
        assessment = {}
        result = orchestrator._tier_c_onboarding_gate(assessment)
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    def test_tier_c_in_run_all(self, orchestrator):
        """run_all() must include the tier_c_onboarding_required gate."""
        assessment = {
            "coherence_score": 0.85,
            "evidence_coverage": 0.96,
            "hard_contradictions": [],
            "critical_recall": 0.95,
            "financial_data": {
                "occupancy_rate": 75.0,
                "direct_channel_percentage": 30.0,
                "adr_cop": 250000,
            },
            "generated_assets": [
                {"asset_type": "optimization_guide", "confidence_score": 0.8},
            ],
            "financial_evidence_tier": "C",
        }
        results = orchestrator.run_all(assessment)
        gate_names = [r.gate_name for r in results]
        assert "tier_c_onboarding_required" in gate_names

        tier_gate = next(r for r in results if r.gate_name == "tier_c_onboarding_required")
        assert tier_gate.passed is False
        assert tier_gate.status == GateStatus.BLOCKED