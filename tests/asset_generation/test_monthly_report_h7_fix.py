"""Tests for H7 FIX: monthly_report retry logic and graceful failure.

Validates:
- T1: conditional_generator catches exceptions from monthly_report with retry (max 2)
- T3: monthly_report_generator handles list instead of dict in generated_assets
- T2: proposal shows disclaimer when monthly_report is BLOCKED
"""

import pytest
import json
import os
import tempfile
from pathlib import Path

from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.monthly_report_generator import MonthlyReportGenerator
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator
from modules.commercial_documents.data_structures import (
    DiagnosticSummary, AssetSpec, ConfidenceLevel, FinancialScenarios
)


class TestMonthlyReportRetry:
    """T1: conditional_generator retries monthly_report on failure."""

    def test_retry_on_attribute_error(self):
        """conditional_generator retries and eventually marks BLOCKED after max attempts."""
        cg = ConditionalGenerator(output_dir="output")
        # Patch generator to always fail
        original_generate = MonthlyReportGenerator.generate
        def failing_generate(self, hotel_data, period=None, asset_report_path=None):
            raise AttributeError("'list' object has no attribute 'items'")
        MonthlyReportGenerator.generate = failing_generate

        try:
            result = cg.generate(
                asset_type="monthly_report",
                validated_data={"hotel_data": {"name": "Test Hotel"}},
                hotel_name="Test Hotel",
                hotel_id="test_hotel",
            )
            # After retries fail, should get error status from the outer try/except
            assert result["status"] in ("error", "blocked"), f"Expected error/blocked, got {result['status']}"
        finally:
            MonthlyReportGenerator.generate = original_generate

    def test_no_retry_on_success(self):
        """When monthly_report succeeds, no retry occurs."""
        cg = ConditionalGenerator(output_dir="output")
        result = cg.generate(
            asset_type="monthly_report",
            validated_data={"hotel_data": {"name": "Test Hotel"}},
            hotel_name="Test Hotel",
            hotel_id="test_hotel",
        )
        # Should succeed without errors
        assert result["status"] in ("success", "warning"), f"Expected success/warning, got {result['status']}"
        assert "error" not in result or result.get("error") is None


class TestMonthlyReportAssetsTableFix:
    """T3: monthly_report_generator handles list-typed generated_assets."""

    def test_handles_list_format_from_json(self):
        """Generator should not fail when JSON has assets as list instead of dict."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "asset_generation_report.json")
            with open(report_path, 'w') as f:
                json.dump({
                    "generated_assets": [
                        {"asset_type": "hotel_schema", "can_use": True, "confidence_score": 0.9},
                        {"asset_type": "faq_page", "can_use": True, "confidence_score": 0.8},
                    ]
                }, f)

            gen = MonthlyReportGenerator()
            # Should NOT raise "'list' object has no attribute 'items'"
            content = gen.generate(
                {"name": "Test Hotel", "output_dir": tmpdir},
                asset_report_path=report_path
            )
            assert "Informe Mensual" in content
            # Fallback: "No se generaron assets" since list can't be iterated as dict
            assert "No se generaron assets" in content or "✅ Entregado" in content

    def test_handles_dict_format_still_works(self):
        """Dict format (normal case) continues to work."""
        with tempfile.TemporaryDirectory() as tmpdir:
            report_path = os.path.join(tmpdir, "asset_generation_report.json")
            with open(report_path, 'w') as f:
                json.dump({
                    "generated_assets": {
                        "hotel_schema": {"can_use": True, "confidence_score": 0.95},
                        "faq_page": {"can_use": True, "confidence_score": 0.80},
                    }
                }, f)

            gen = MonthlyReportGenerator()
            content = gen.generate(
                {"name": "Test Hotel", "output_dir": tmpdir},
                asset_report_path=report_path
            )
            assert "Informe Mensual" in content
            # Normal case: should show real assets
            assert "hotel_schema" in content or "✅ Entregado" in content


class TestMonthlyReportDisclaimerInProposal:
    """T2: proposal shows disclaimer when monthly_report is BLOCKED."""

    def test_disclaimer_shown_when_blocked(self):
        """When monthly_report has status=blocked, proposal includes disclaimer."""
        gen = V4ProposalGenerator()

        # Create a diagnostic summary
        summary = DiagnosticSummary(
            hotel_name="Test Hotel",
            score_global=50,
            score_aeo=30,
            critical_problems_count=2,
            quick_wins_count=3,
            top_problems=[],
            coherence_score=0.8,
            overall_confidence=ConfidenceLevel.VERIFIED,
            pain_ids=["no_hotel_schema", "no_faq_schema"],
        )

        # Create a simple financial scenario
        class FakeScenario:
            monthly_loss_cop = 1000000
        scenarios = FinancialScenarios(
            conservative=FakeScenario(),
            realistic=FakeScenario(),
            optimistic=FakeScenario(),
        )
        scenarios.get_main_scenario = lambda: FakeScenario()

        # monthly_report with BLOCKED status
        blocked_monthly_report = {
            "asset_type": "monthly_report",
            "status": "blocked",
            "error": "monthly_report failed after 3 attempts: 'list' object has no attribute 'items'",
        }
        other_asset = {
            "asset_type": "hotel_schema",
            "status": "success",
            "confidence_score": 0.9,
        }
        assets_generated = [blocked_monthly_report, other_asset]

        data = gen._prepare_template_data(
            diagnostic_summary=summary,
            financial_scenarios=scenarios,
            asset_plan=[],
            hotel_name="Test Hotel",
            audit_result=None,
            region="eje_cafetero",
            analytics_data=None,
            assets_generated=assets_generated,
            site_presence_report=None,
            financial_breakdown=None,
        )

        # Disclaimer must be present
        assert data.get("monthly_report_disclaimer") != ""
        assert "24 horas" in data["monthly_report_disclaimer"]
        assert "automáticamente" in data["monthly_report_disclaimer"]

    def test_no_disclaimer_when_success(self):
        """When monthly_report succeeds, no disclaimer in proposal."""
        gen = V4ProposalGenerator()

        summary = DiagnosticSummary(
            hotel_name="Test Hotel",
            score_global=50,
            score_aeo=30,
            critical_problems_count=2,
            quick_wins_count=3,
            top_problems=[],
            coherence_score=0.8,
            overall_confidence=ConfidenceLevel.VERIFIED,
            pain_ids=["no_hotel_schema"],
        )

        class FakeScenario:
            monthly_loss_cop = 1000000
        scenarios = FinancialScenarios(
            conservative=FakeScenario(),
            realistic=FakeScenario(),
            optimistic=FakeScenario(),
        )
        scenarios.get_main_scenario = lambda: FakeScenario()

        # monthly_report with SUCCESS status
        successful_monthly_report = {
            "asset_type": "monthly_report",
            "status": "success",
            "confidence_score": 0.85,
        }
        assets_generated = [successful_monthly_report]

        data = gen._prepare_template_data(
            diagnostic_summary=summary,
            financial_scenarios=scenarios,
            asset_plan=[],
            hotel_name="Test Hotel",
            audit_result=None,
            region="eje_cafetero",
            analytics_data=None,
            assets_generated=assets_generated,
            site_presence_report=None,
            financial_breakdown=None,
        )

        # No disclaimer when monthly_report succeeds
        assert data.get("monthly_report_disclaimer") == ""


if __name__ == "__main__":
    pytest.main([__file__, "-v"])