"""Tests for CommercialGateBlockedError — ROICR FASE-3.

Tests that CommercialGateBlockedError is properly defined and raised
when commercial gates block proposal generation for external clients.
"""

import pytest
from unittest.mock import MagicMock, patch
from modules.commercial_documents.v4_proposal_generator import (
    CommercialGateBlockedError,
)


class TestCommercialGateBlockedError:
    """CommercialGateBlockedError exception behavior."""

    def test_error_defined_in_module(self):
        """CommercialGateBlockedError must be importable from v4_proposal_generator."""
        assert CommercialGateBlockedError is not None
        assert issubclass(CommercialGateBlockedError, Exception)

    def test_error_stores_gate_ids(self):
        """Error must store the list of gate_ids that blocked."""
        gate_ids = ["CG-SCENARIO-NEGATIVE", "CG-ROI-NEGATIVE"]
        error = CommercialGateBlockedError(gate_ids)
        assert error.gate_ids == gate_ids
        assert "CG-SCENARIO-NEGATIVE" in error.gate_ids
        assert "CG-ROI-NEGATIVE" in error.gate_ids

    def test_error_message_format(self):
        """Error message should include gate_ids."""
        gate_ids = ["CG-SCENARIO-NEGATIVE"]
        error = CommercialGateBlockedError(gate_ids, "Proposal commercial gates BLOCKING")
        assert "CG-SCENARIO-NEGATIVE" in str(error)
        assert "Proposal commercial gates BLOCKING" in str(error)

    def test_error_default_message(self):
        """Error should have a sensible default message."""
        error = CommercialGateBlockedError(["CG-TEST"])
        assert "CG-TEST" in str(error)
        assert "Commercial gates blocking" in str(error)

    def test_error_can_be_caught(self):
        """Error must be catchable with standard exception handling."""
        gate_ids = ["CG-SCENARIO-NEGATIVE"]
        with pytest.raises(CommercialGateBlockedError) as exc_info:
            raise CommercialGateBlockedError(gate_ids, "Test block")
        assert exc_info.value.gate_ids == gate_ids
