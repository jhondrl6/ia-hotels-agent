"""Tests for FASE-1-A FIX-1: Template conditionals pre-processor."""

import pytest
from string import Template
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


class TestPreprocessConditionals:
    """Tests for _preprocess_conditionals method."""

    @pytest.fixture
    def generator(self):
        """Create a V4ProposalGenerator instance."""
        return V4ProposalGenerator()

    def test_conditional_include_when_true(self, generator):
        """{{if var == "value"}} block included when condition matches."""
        template = "Start {{if financial_evidence_tier == \"C\"}}WARNING{{endif}} End"
        data = {'financial_evidence_tier': 'C'}
        result = generator._preprocess_conditionals(template, data)
        assert "WARNING" in result
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_conditional_exclude_when_false(self, generator):
        """{{if var == "value"}} block excluded when condition does not match."""
        template = "Start {{if financial_evidence_tier == \"C\"}}WARNING{{endif}} End"
        data = {'financial_evidence_tier': 'B'}
        result = generator._preprocess_conditionals(template, data)
        assert "WARNING" not in result
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_no_residue_in_output(self, generator):
        """Output must NOT contain {{if}} or {{endif}} tags."""
        template = "{{if financial_evidence_tier == \"C\"}}content{{endif}}"
        data = {'financial_evidence_tier': 'C'}
        result = generator._preprocess_conditionals(template, data)
        assert "{{if}}" not in result
        assert "{{endif}}" not in result

    def test_render_template_with_conditionals(self, generator):
        """_render_template processes conditionals before safe_substitute."""
        template = "Tier: {{if financial_evidence_tier == \"C\"}}BRONZE{{endif}}"
        data = {'financial_evidence_tier': 'C', 'financial_evidence_tier': 'C'}
        result = generator._render_template(template, data)
        assert "BRONZE" in result
        assert "{{if}}" not in result

    def test_conditional_with_missing_variable(self, generator):
        """Missing variable treated as empty string (no match)."""
        template = "{{if missing_var == \"value\"}}SHOULD_NOT_APPEAR{{endif}}"
        data = {}
        result = generator._preprocess_conditionals(template, data)
        assert "SHOULD_NOT_APPEAR" not in result

    def test_multiple_conditionals(self, generator):
        """Multiple {{if}} blocks processed independently."""
        template = "{{if tier == \"A\"}}HIGH{{endif}} middle {{if tier == \"B\"}}MED{{endif}}"
        data = {'tier': 'A'}
        result = generator._preprocess_conditionals(template, data)
        assert "HIGH" in result
        assert "MED" not in result
        assert "{{if}}" not in result