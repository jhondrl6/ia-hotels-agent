"""
tests/quality_gates/test_pricing_compliance_gate.py

FASE-P0-B: Tests for the pricing_compliance gate (BLOCKING floor-aware D1).

Test cases:
    1. pain_ratio > tier gate_max → BLOCKED
    2. pain_ratio 0.0724 (Zione) with floor applied → PASSED + WARNING (D1)
    3. pain_ratio within ideal range → PASSED (no warning)
    4. pain_ratio at exact gate_max boundary → PASSED (boundary inclusive)
    5. No pricing_data → PASSED (skipped)
    6. Missing pain_ratio → PASSED (skipped)
    7. Non-numeric pain_ratio → BLOCKED

Baseline: 322 passed, 0 failed (quality_gates suite, pre-P0-B).
"""

import pytest
from unittest.mock import patch, MagicMock
from typing import Any, Dict

from modules.quality_gates.publication_gates import (
    PublicationGatesOrchestrator,
    PublicationGateConfig,
    GateStatus,
    PublicationGateResult,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def orchestrator():
    """Orchestrator with default config."""
    return PublicationGatesOrchestrator(PublicationGateConfig())


@pytest.fixture
def pricing_config_boutique() -> Dict[str, Any]:
    """Pricing config matching config/pricing.yaml for boutique tier."""
    return {
        "tiers": {
            "boutique": {
                "pain_ratio_gate_max": 0.32,
                "operational_floor": 400_000,
            },
            "standard": {
                "pain_ratio_gate_max": 0.32,
                "operational_floor": 500_000,
            },
            "large": {
                "pain_ratio_gate_max": 0.32,
                "operational_floor": 800_000,
            },
        },
        "gates": {
            "min_ratio": 0.03,
            "max_ratio": 0.06,
            "ideal_ratio": 0.045,
        },
    }


def _make_assessment(pricing_data: Dict[str, Any]) -> Dict[str, Any]:
    """Build a minimal assessment with pricing_data."""
    return {"pricing_data": pricing_data}


# ---------------------------------------------------------------------------
# T3: Tests del gate pricing_compliance
# ---------------------------------------------------------------------------

class TestPricingComplianceGate:
    """Unit tests for _pricing_compliance_gate."""

    # --- Test 1: BLOCKING when pain_ratio > gate_max ---

    def test_blocks_when_ratio_exceeds_tier_gate_max(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.50 > boutique gate_max 0.32 → BLOCKED."""
        assessment = _make_assessment({
            "pain_ratio": 0.50,
            "tier": "boutique",
            "monthly_price_cop": 2_500_000,
            "expected_loss_cop": 5_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.gate_name == "pricing_compliance"
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.value == 0.50
        assert "0.32" in result.message or "gate_max" in result.message
        assert result.details["tier_gate_max"] == 0.32
        assert result.details["tier"] == "boutique"

    # --- Test 2: D1 contract — Zione ratio 0.0724 with floor → PASSED + WARNING ---

    def test_zione_floor_aware_warning(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.0724, floor applied (price=400K, loss~5.5M) → PASSED + WARNING."""
        # Zione scenario: price=400K (floor), loss=5.525M → ratio=0.0724
        assessment = _make_assessment({
            "pain_ratio": 0.0724,
            "tier": "boutique",
            "monthly_price_cop": 400_000,
            "expected_loss_cop": 5_525_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.gate_name == "pricing_compliance"
        assert result.passed is True
        assert result.status == GateStatus.WARNING
        assert "operational_floor" in result.message or "floor" in result.message.lower()
        assert result.details["floor_applied"] is True
        assert result.details["tier_gate_max"] == 0.32

    # --- Test 3: Ideal range → PASSED (no warning) ---

    def test_ideal_range_passes_clean(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.045 (ideal) with no floor → PASSED."""
        assessment = _make_assessment({
            "pain_ratio": 0.045,
            "tier": "boutique",
            "monthly_price_cop": 900_000,
            "expected_loss_cop": 20_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.gate_name == "pricing_compliance"
        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert result.details["floor_applied"] is False

    def test_inside_ideal_range_low_end(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.03 (ideal boundary low) → PASSED."""
        assessment = _make_assessment({
            "pain_ratio": 0.03,
            "tier": "boutique",
            "monthly_price_cop": 600_000,
            "expected_loss_cop": 20_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_inside_ideal_range_high_end(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.06 (ideal boundary high) → PASSED."""
        assessment = _make_assessment({
            "pain_ratio": 0.06,
            "tier": "boutique",
            "monthly_price_cop": 1_200_000,
            "expected_loss_cop": 20_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    # --- Test 4: Boundary — exact gate_max → PASSED (inclusive) ---

    def test_exact_gate_max_passes(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio exactly 0.32 (gate_max) → PASSED (boundary inclusive)."""
        assessment = _make_assessment({
            "pain_ratio": 0.32,
            "tier": "boutique",
            "monthly_price_cop": 1_600_000,
            "expected_loss_cop": 5_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        # ratio 0.32 > ideal_max (0.06) and floor NOT applied → still PASSED
        assert result.status in (GateStatus.PASSED, GateStatus.WARNING)

    def test_just_above_gate_max_blocks(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.3201 (just above gate_max) → BLOCKED."""
        assessment = _make_assessment({
            "pain_ratio": 0.3201,
            "tier": "boutique",
            "monthly_price_cop": 1_600_500,
            "expected_loss_cop": 5_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED

    # --- Test 5: No pricing_data → PASSED (skipped) ---

    def test_no_pricing_data_skips(self, orchestrator):
        """assessment without pricing_data → PASSED (skipped)."""
        result = orchestrator._pricing_compliance_gate({})

        assert result.passed is True
        assert result.status == GateStatus.PASSED
        assert "No pricing data" in result.message

    def test_none_pricing_data_skips(self, orchestrator):
        """pricing_data = None → PASSED (skipped)."""
        result = orchestrator._pricing_compliance_gate({"pricing_data": None})

        assert result.passed is True
        assert "No pricing data" in result.message

    # --- Test 6: Missing pain_ratio → PASSED (skipped) ---

    def test_missing_pain_ratio_skips(self, orchestrator):
        """pricing_data without pain_ratio → PASSED (skipped)."""
        assessment = _make_assessment({"tier": "boutique"})

        result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        assert "pain_ratio not found" in result.message

    # --- Test 7: Non-numeric pain_ratio → BLOCKED ---

    def test_non_numeric_pain_ratio_blocks(self, orchestrator):
        """pain_ratio = 'invalid' → BLOCKED."""
        assessment = _make_assessment({
            "pain_ratio": "invalid",
            "tier": "boutique",
        })

        result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert "not numeric" in result.message

    # --- Additional edge cases ---

    def test_outside_ideal_no_floor_passes(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.15, floor NOT applied → PASSED (below gate_max)."""
        assessment = _make_assessment({
            "pain_ratio": 0.15,
            "tier": "boutique",
            "monthly_price_cop": 1_500_000,
            "expected_loss_cop": 10_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_below_ideal_range_no_floor_passes(
        self, orchestrator, pricing_config_boutique
    ):
        """pain_ratio 0.01 (below ideal), floor NOT applied → PASSED."""
        assessment = _make_assessment({
            "pain_ratio": 0.01,
            "tier": "boutique",
            "monthly_price_cop": 500_000,
            "expected_loss_cop": 50_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.passed is True
        assert result.status == GateStatus.PASSED

    def test_standard_tier_uses_correct_gate_max(
        self, orchestrator, pricing_config_boutique
    ):
        """standard tier with its own gate_max → correct threshold applied."""
        pricing_config_boutique["tiers"]["standard"]["pain_ratio_gate_max"] = 0.25

        assessment = _make_assessment({
            "pain_ratio": 0.30,
            "tier": "standard",
            "monthly_price_cop": 3_000_000,
            "expected_loss_cop": 10_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        # 0.30 > 0.25 (standard gate_max) → BLOCKED
        assert result.passed is False
        assert result.status == GateStatus.BLOCKED
        assert result.details["tier_gate_max"] == 0.25

    def test_details_include_all_fields(
        self, orchestrator, pricing_config_boutique
    ):
        """Result details contain all required fields for traceability."""
        assessment = _make_assessment({
            "pain_ratio": 0.0724,
            "tier": "boutique",
            "monthly_price_cop": 400_000,
            "expected_loss_cop": 5_525_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        d = result.details
        assert "pain_ratio" in d
        assert "tier" in d
        assert "tier_gate_max" in d
        assert "operational_floor" in d
        assert "floor_applied" in d
        assert "ideal_range" in d
        assert "monthly_price_cop" in d
        assert "expected_loss_cop" in d

    def test_gate_registered_in_orchestrator(self, orchestrator):
        """pricing_compliance gate is registered in self.gates dict."""
        assert "pricing_compliance" in orchestrator.gates
        assert callable(orchestrator.gates["pricing_compliance"])

    def test_floor_detection_tolerance(
        self, orchestrator, pricing_config_boutique
    ):
        """price slightly below floor (within 1% tolerance) → floor detected."""
        assessment = _make_assessment({
            "pain_ratio": 0.08,
            "tier": "boutique",
            "monthly_price_cop": 399_000,  # just below 400K floor
            "expected_loss_cop": 4_987_500,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        # price <= floor * 1.01 → floor_applied = True
        assert result.details["floor_applied"] is True

    def test_no_floor_detection_when_price_above(
        self, orchestrator, pricing_config_boutique
    ):
        """price well above floor → floor_applied = False."""
        assessment = _make_assessment({
            "pain_ratio": 0.08,
            "tier": "boutique",
            "monthly_price_cop": 800_000,  # well above 400K floor
            "expected_loss_cop": 10_000_000,
        })

        with patch.object(
            orchestrator,
            "_load_pricing_thresholds",
            return_value=pricing_config_boutique,
        ):
            result = orchestrator._pricing_compliance_gate(assessment)

        assert result.details["floor_applied"] is False
        assert result.passed is True
        # Outside ideal but no floor → still PASSED (below gate_max)
        assert result.status == GateStatus.PASSED
