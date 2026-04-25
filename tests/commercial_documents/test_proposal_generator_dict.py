"""
Tests for FASE-VALIDATE-RC: Regression test for _prepare_template_data() dict construction.

Verifies that:
1. _prepare_template_data() executes without TypeError (the bug this phase fixes)
2. V6 keys (plan_*_days) are present and non-empty
3. Legacy V4 keys (plan_*d) remain present (they ARE used by diagnostico_v4_template.md)
4. Both sets of plan keys return non-empty strings

Created by FASE-VALIDATE-RC to prevent future signature mismatches.
"""

import pytest
from unittest.mock import MagicMock
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.data_structures import AssetSpec


class TestPrepareTemplateDataRegression:
    """Regression suite for _prepare_template_data dict construction."""

    def setup_method(self):
        """Create generator instance with minimal mocks."""
        self.gen = V4ProposalGenerator()

    def _make_minimal_diagnostic(self):
        """Create a minimal DiagnosticSummary for testing."""
        diag = MagicMock()
        diag.hotel_name = "Amazilia Hotel Test"
        diag.hotel_url = "https://amaziliahotel.com/"
        diag.overall_confidence = MagicMock()
        diag.overall_confidence.value = "VERIFIED"
        diag.score_global = 65
        diag.score_tecnico = 65
        diag.coherence_score = 0.82
        diag.top_problems = []
        diag.gbp_data = None
        diag.web_data = None
        return diag

    def _make_minimal_financial(self):
        """Create a minimal FinancialScenarios for testing."""
        fin = MagicMock()
        fin.main_scenario = MagicMock()
        fin.main_scenario.monthly_loss = 4500000
        fin.main_scenario.monthly_investment = 1200000
        fin.main_scenario.projected_monthly_gain = 3800000
        fin.main_scenario.roi_6_months = "3.2X"
        fin.main_scenario.roi_12_months = "6.5X"
        fin.conservative = fin.main_scenario
        fin.optimistic = fin.main_scenario
        return fin

    def _make_minimal_asset_plan(self):
        """Create a minimal AssetSpec list for testing."""
        return [
            AssetSpec(
                asset_type="local_content",
                problem_solved="no_local_content",
                priority=2,
            )
        ]

    def test_prepare_template_data_no_typeerror(self):
        """Main regression: calling _prepare_template_data must not raise TypeError."""
        diag = self._make_minimal_diagnostic()
        fin = self._make_minimal_financial()
        assets = self._make_minimal_asset_plan()

        # This used to crash with:
        # TypeError: _build_60_day_plan() missing 1 required positional argument: 'asset_plan'
        result = self.gen._prepare_template_data(
            diagnostic_summary=diag,
            financial_scenarios=fin,
            asset_plan=assets,
            hotel_name="Amazilia Hotel Test",
            region="Pereira",
        )

        assert isinstance(result, dict), "Must return a dict"
        assert len(result) > 0, "Dict must not be empty"

    def test_v6_plan_keys_present_and_nonempty(self):
        """V6 keys (plan_*_days) must be present and non-empty after hotfix."""
        diag = self._make_minimal_diagnostic()
        fin = self._make_minimal_financial()
        assets = self._make_minimal_asset_plan()

        result = self.gen._prepare_template_data(
            diagnostic_summary=diag,
            financial_scenarios=fin,
            asset_plan=assets,
            hotel_name="Amazilia Hotel Test",
            region="Pereira",
        )

        v6_keys = ["plan_7_days", "plan_30_days", "plan_60_days", "plan_90_days"]
        for key in v6_keys:
            assert key in result, f"V6 key '{key}' must be in result dict"
            assert isinstance(result[key], str), f"V6 key '{key}' must be a string"
            assert len(result[key]) > 0, f"V6 key '{key}' must be non-empty"

    def test_legacy_v4_keys_present_and_nonempty(self):
        """Legacy V4 keys (plan_*d) must remain present (used by diagnostico_v4_template.md).

        Note: The original FASE-VALIDATE-RC plan assumed these were dead code, but
        grep revealed they ARE consumed by diagnostico_v4_template.md and
        propuesta_v4_template.md. Per the restriction 'If grep reveals legacy vars
        ARE used, do NOT remove', these must remain.
        """
        diag = self._make_minimal_diagnostic()
        fin = self._make_minimal_financial()
        assets = self._make_minimal_asset_plan()

        result = self.gen._prepare_template_data(
            diagnostic_summary=diag,
            financial_scenarios=fin,
            asset_plan=assets,
            hotel_name="Amazilia Hotel Test",
            region="Pereira",
        )

        v4_keys = ["plan_7d", "plan_30d", "plan_60d", "plan_90d"]
        for key in v4_keys:
            assert key in result, f"Legacy V4 key '{key}' must remain in result dict"
            assert isinstance(result[key], str), f"Legacy V4 key '{key}' must be a string"
            assert len(result[key]) > 0, f"Legacy V4 key '{key}' must be non-empty"

    def test_hotfix_applies_to_60_and_90_day_plans(self):
        """Explicitly verify plan_60d and plan_90d now receive asset_plan without TypeError.

        This is the direct regression test for the bug fixed in line 559-560:
        _build_60_day_plan() and _build_90_day_plan() were called without asset_plan,
        causing TypeError. After hotfix they receive asset_plan.
        """
        diag = self._make_minimal_diagnostic()
        fin = self._make_minimal_financial()
        assets = self._make_minimal_asset_plan()

        # If the hotfix is NOT applied, this will raise TypeError
        result = self.gen._prepare_template_data(
            diagnostic_summary=diag,
            financial_scenarios=fin,
            asset_plan=assets,
            hotel_name="Amazilia Hotel Test",
            region="Pereira",
        )

        # Verify the specific keys that were broken
        assert result["plan_60d"] is not None
        assert len(result["plan_60d"]) > 0
        assert result["plan_90d"] is not None
        assert len(result["plan_90d"]) > 0
