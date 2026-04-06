import pytest
from modules.auditors.ia_readiness_calculator import IAReadinessCalculator, IAReadinessReport


class TestIAReadinessCalculator:
    """Tests for IAReadinessCalculator module."""

    def test_ia_readiness_calculator(self):
        """Verify compound score calculation is correct."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=85.0,
            citability_score=75.0,
            has_llmstxt=True,
            brand_score=80.0
        )

        expected_schema = 80.0
        expected_crawler = 85.0
        expected_citability = 75.0
        expected_llms = 100.0
        expected_brand = 80.0
        
        # When ga4_indirect_score is None, weight is redistributed proportionally
        available_weights = {"schema_quality": 0.22, "crawler_access": 0.22, "citability": 0.23, "llms_txt": 0.09, "brand_signals": 0.14}
        total_w = sum(available_weights.values())
        expected_overall = (
            expected_schema * (available_weights["schema_quality"] / total_w) +
            expected_crawler * (available_weights["crawler_access"] / total_w) +
            expected_citability * (available_weights["citability"] / total_w) +
            expected_llms * (available_weights["llms_txt"] / total_w) +
            expected_brand * (available_weights["brand_signals"] / total_w)
        )

        assert report.overall_score == expected_overall
        assert report.components["schema_quality"] == expected_schema
        assert report.components["crawler_access"] == expected_crawler
        assert report.components["citability"] == expected_citability
        assert report.components["llms_txt"] == expected_llms
        assert report.components["brand_signals"] == expected_brand

    def test_ia_readiness_status_ready(self):
        """Status 'Ready' when score >= 70."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=80.0,
            citability_score=80.0,
            has_llmstxt=True,
            brand_score=80.0
        )

        assert report.status == "Ready"
        assert report.overall_score >= 70

    def test_ia_readiness_status_needs_work(self):
        """Status 'Needs Work' when score >= 50 and < 70."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.65,
            crawler_score=65.0,
            citability_score=55.0,
            has_llmstxt=False,
            brand_score=50.0
        )

        assert report.status == "Needs Work"
        assert 50 <= report.overall_score < 70

    def test_ia_readiness_status_critical(self):
        """Status 'Critical' when score < 50."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.30,
            crawler_score=40.0,
            citability_score=30.0,
            has_llmstxt=False,
            brand_score=20.0
        )

        assert report.status == "Critical"
        assert report.overall_score < 50

    def test_actionable_items_generated(self):
        """Verify actionable items are generated based on component scores."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.40,
            crawler_score=30.0,
            citability_score=20.0,
            has_llmstxt=False,
            brand_score=10.0
        )

        assert len(report.actionable_items) > 0
        assert isinstance(report.actionable_items, list)
        assert all(isinstance(item, str) for item in report.actionable_items)

    def test_actionable_items_none_when_all_pass(self):
        """No actionable items when all components pass."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.90,
            crawler_score=90.0,
            citability_score=90.0,
            has_llmstxt=True,
            brand_score=90.0,
            ga4_indirect_score=80.0
        )

        assert len(report.actionable_items) == 0

    def test_llms_txt_false_gives_zero(self):
        """llms_txt component is 0 when has_llmstxt is False."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.0,
            crawler_score=0.0,
            citability_score=0.0,
            has_llmstxt=False,
            brand_score=0.0
        )

        assert report.components["llms_txt"] == 0

    def test_llms_txt_true_gives_hundred(self):
        """llms_txt component is 100 when has_llmstxt is True."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.0,
            crawler_score=0.0,
            citability_score=0.0,
            has_llmstxt=True,
            brand_score=0.0
        )

        assert report.components["llms_txt"] == 100

    def test_schema_coverage_multiplied_by_100(self):
        """schema_coverage (0-1) is multiplied by 100."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.75,
            crawler_score=0.0,
            citability_score=0.0,
            has_llmstxt=False,
            brand_score=0.0
        )

        assert report.components["schema_quality"] == 75.0

    def test_weights_sum_to_one(self):
        """WEIGHTS values sum to 1.0."""
        calculator = IAReadinessCalculator()
        
        total = sum(calculator.WEIGHTS.values())
        
        assert total == 1.0


class TestIAReadinessCalculatorGA4:
    """Tests for GA4 integration in IA readiness calculator."""

    def test_ga4_score_included_in_components(self):
        """GA4 score is included in components when provided."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=80.0,
            citability_score=70.0,
            has_llmstxt=True,
            brand_score=60.0,
            ga4_indirect_score=50.0,
        )
        
        assert "ga4_indirect" in report.components
        assert report.components["ga4_indirect"] == 50.0

    def test_ga4_score_affects_overall(self):
        """GA4 score contributes to overall score when provided."""
        calculator = IAReadinessCalculator()
        
        report_with_ga4 = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=80.0,
            citability_score=70.0,
            has_llmstxt=True,
            brand_score=60.0,
            ga4_indirect_score=50.0,
        )
        report_without_ga4 = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=80.0,
            citability_score=70.0,
            has_llmstxt=True,
            brand_score=60.0,
        )
        
        # Scores should differ since GA4 adds a component
        assert report_with_ga4.overall_score != report_without_ga4.overall_score

    def test_ga4_unavailable_adds_actionable_item(self):
        """An actionable item is added when GA4 is not configured."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.90,
            crawler_score=90.0,
            citability_score=90.0,
            has_llmstxt=True,
            brand_score=90.0,
        )
        
        ga4_items = [item for item in report.actionable_items if "Google Analytics" in item]
        assert len(ga4_items) == 1

    def test_ga4_available_no_ga4_actionable_item(self):
        """No GA4 actionable item when GA4 score is provided."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.90,
            crawler_score=90.0,
            citability_score=90.0,
            has_llmstxt=True,
            brand_score=90.0,
            ga4_indirect_score=80.0,
        )
        
        ga4_items = [item for item in report.actionable_items if "Google Analytics" in item]
        assert len(ga4_items) == 0

    def test_ga4_zero_score(self):
        """GA4 score of 0 is treated as available (not None)."""
        calculator = IAReadinessCalculator()
        
        report = calculator.calculate(
            schema_coverage=0.80,
            crawler_score=80.0,
            citability_score=70.0,
            has_llmstxt=True,
            brand_score=60.0,
            ga4_indirect_score=0.0,
        )
        
        assert "ga4_indirect" in report.components
        assert report.components["ga4_indirect"] == 0.0
