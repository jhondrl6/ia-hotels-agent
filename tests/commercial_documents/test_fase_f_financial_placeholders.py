"""
Tests FASE-F: Financial placeholders (Comisión OTA + Evidence Tiers).

Tests:
- test_financial_placeholders_filled: New placeholders are populated (not raw ${...})
- test_evidence_tier_default_c: Default tier is C when no GA4
- test_evidence_tier_a_with_ga4: Tier is A when GA4 is enabled
- test_scenario_table_rows_format: Scenario table has 3 rows with correct format
- test_backward_compat_loss_6_months: loss_6_months recalculated with central value
- test_disclaimer_present: Disclaimer is non-empty
"""
import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator
from modules.commercial_documents.data_structures import (
    FinancialScenarios,
    Scenario,
    format_cop,
)


def make_scenarios(
    central_cons=2_000_000,
    central_real=2_610_000,
    central_opt=3_100_000,
):
    """Helper: create FinancialScenarios with monthly_loss_central set."""
    return FinancialScenarios(
        conservative=Scenario(
            monthly_loss_min=1_500_000,
            monthly_loss_max=2_500_000,
            probability=0.7,
            description="Conservador",
            monthly_loss_central=central_cons,
        ),
        realistic=Scenario(
            monthly_loss_min=2_000_000,
            monthly_loss_max=3_132_000,
            probability=0.2,
            description="Realista",
            monthly_loss_central=central_real,
        ),
        optimistic=Scenario(
            monthly_loss_min=2_500_000,
            monthly_loss_max=3_700_000,
            probability=0.1,
            description="Optimista",
            monthly_loss_central=central_opt,
        ),
    )


class TestFinancialPlaceholders:
    """Test _build_financial_placeholders() method."""

    def test_placeholders_filled_no_ga4(self):
        """Without GA4, placeholders are populated with defaults (Tier C)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios, analytics_data=None)

        # All keys present
        for key in [
            'ota_commission_formatted',
            'ota_commission_basis',
            'ota_commission_source',
            'scenario_table_rows',
            'evidence_tier',
            'financial_disclaimer',
            'financial_source_ref',
            'financial_value_central',
            'financial_value_min',
            'financial_value_max',
            'financial_method',
            'loss_6_months',
        ]:
            assert key in result, f"Missing key: {key}"

        # No raw placeholders remain
        for key, val in result.items():
            assert '${' not in str(val), f"Key '{key}' has raw placeholder: {val}"

    def test_evidence_tier_default_c(self):
        """Default tier without GA4 is C."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios, analytics_data=None)

        assert result['evidence_tier'] == 'C'

    def test_evidence_tier_a_with_ga4(self):
        """With GA4 enabled, tier is A."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(
            scenarios,
            analytics_data={"use_ga4": True},
        )

        assert result['evidence_tier'] == 'A'

    def test_scenario_table_has_3_rows(self):
        """Scenario table must have 3 rows (Conservador/Realista/Optimista)."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        table = result['scenario_table_rows']

        rows = [r for r in table.strip().split('\n') if r.strip()]
        assert len(rows) == 3, f"Expected 3 rows, got {len(rows)}"

    def test_scenario_table_format(self):
        """Each row is a valid markdown table row with | separators."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)
        table = result['scenario_table_rows']

        for row in table.strip().split('\n'):
            parts = [p.strip() for p in row.split('|') if p.strip()]
            assert len(parts) == 3, f"Row should have 3 columns: {row}"
            # Column 0: scenario name
            assert parts[0] in ('Conservador', 'Realista', 'Optimista')
            # Column 1: formatted COP
            assert 'COP/mes' in parts[1]
            # Column 2: probability
            assert '%' in parts[2]

    def test_uses_central_value_not_max(self):
        """ota_commission_formatted uses central value, not monthly_loss_max."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        # Should use central (2,610,000), not max (3,132,000)
        # format_cop uses dots: $2.610.000 COP
        assert '2.610.000' in result['ota_commission_formatted']
        assert result['financial_value_central'] == '2610000'

    def test_loss_6_months_uses_central(self):
        """loss_6_months is calculated from central value * 6."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios(central_real=2_610_000)

        result = gen._build_financial_placeholders(scenarios)

        expected_6m = 2_610_000 * 6  # 15,660,000
        assert result['loss_6_months'] == format_cop(expected_6m)

    def test_disclaimer_non_empty(self):
        """Disclaimer must be a non-empty string."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)

        assert len(result['financial_disclaimer']) > 20
        assert 'estimaci' in result['financial_disclaimer'].lower() or \
               'datos' in result['financial_disclaimer'].lower()

    def test_financial_method_constant(self):
        """financial_method is always proportional_normalized."""
        gen = V4DiagnosticGenerator()
        scenarios = make_scenarios()

        result = gen._build_financial_placeholders(scenarios)

        assert result['financial_method'] == 'proportional_normalized'
