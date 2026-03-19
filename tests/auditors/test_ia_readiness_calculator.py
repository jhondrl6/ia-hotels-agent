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
        
        expected_overall = (
            expected_schema * 0.25 +
            expected_crawler * 0.25 +
            expected_citability * 0.25 +
            expected_llms * 0.10 +
            expected_brand * 0.15
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
            schema_coverage=0.60,
            crawler_score=60.0,
            citability_score=50.0,
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
            brand_score=90.0
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
