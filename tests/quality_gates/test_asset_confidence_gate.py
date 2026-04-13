"""Tests for the asset_confidence_gate (Gate #8)."""
import pytest

from modules.quality_gates.publication_gates import (
    GateStatus,
    PublicationGatesOrchestrator,
    PublicationGateResult,
)


class TestAssetConfidenceGate:
    """Gate 8: Asset confidence validation."""

    def _run_gate(self, assessment: dict) -> PublicationGateResult:
        """Run the asset_confidence gate via orchestrator."""
        orch = PublicationGatesOrchestrator()
        results = orch.run_all(assessment)
        return next(r for r in results if r.gate_name == "asset_confidence")

    def test_gate_passes_when_all_above_threshold(self):
        """All assets >= 0.7 → PASSED."""
        assessment = {
            "generated_assets": [
                {"asset_type": "hotel_schema", "confidence_score": 0.85},
                {"asset_type": "geo_playbook", "confidence_score": 0.90},
                {"asset_type": "optimization_guide", "confidence_score": 0.75},
            ]
        }
        result = self._run_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "All 3 assets meet confidence threshold" in result.message

    def test_gate_warns_when_some_below_threshold(self):
        """Some assets < 0.7 → WARNING (does NOT block)."""
        assessment = {
            "generated_assets": [
                {"asset_type": "hotel_schema", "confidence_score": 0.50},
                {"asset_type": "geo_playbook", "confidence_score": 0.90},
            ]
        }
        result = self._run_gate(assessment)
        assert result.passed is True  # Conservative: warns but passes
        assert result.status == GateStatus.WARNING
        assert "1 asset(s) below confidence threshold" in result.message
        assert result.details["below_threshold"] == 1

    def test_gate_calculates_avg_correctly(self):
        """Average of [0.5, 0.8, 0.9] = 0.73."""
        assessment = {
            "generated_assets": [
                {"asset_type": "a", "confidence_score": 0.5},
                {"asset_type": "b", "confidence_score": 0.8},
                {"asset_type": "c", "confidence_score": 0.9},
            ]
        }
        result = self._run_gate(assessment)
        assert result.value == pytest.approx(0.733333, abs=0.01)

    def test_gate_empty_assets_list(self):
        """Empty assets list → PASSED (nothing to evaluate)."""
        assessment = {"generated_assets": []}
        result = self._run_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "No generated assets" in result.message

    def test_gate_no_assets_key_in_assessment(self):
        """Missing 'generated_assets' key → PASSED (backward compat)."""
        assessment = {"some_other_data": True}
        result = self._run_gate(assessment)
        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_gate_lists_low_confidence_assets_in_details(self):
        """Low confidence assets are detailed with type and score."""
        assessment = {
            "generated_assets": [
                {"asset_type": "hotel_schema", "confidence_score": 0.50},
                {"asset_type": "llms_txt", "confidence_score": 0.45},
                {"asset_type": "geo_playbook", "confidence_score": 0.85},
            ]
        }
        result = self._run_gate(assessment)
        low = result.details["low_confidence_assets"]
        assert len(low) == 2
        types = {a["type"] for a in low}
        assert types == {"hotel_schema", "llms_txt"}
