"""Tests for canonical_metrics.py"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.utils.canonical_metrics import (
    CANONICAL_METRICS,
    CanonicalMetric,
    resolve_metric,
    get_all_names,
    metric_exists,
    list_sources,
)


class TestCanonicalMetric:
    def test_canonical_metric_creation(self):
        metric = CanonicalMetric(
            canonical_name="test_metric",
            description="Test metric",
            unit="count",
            aliases={"source1": "metric_v1"}
        )
        assert metric.canonical_name == "test_metric"
        assert metric.unit == "count"
        assert metric.aliases["source1"] == "metric_v1"

    def test_canonical_metric_default_aliases(self):
        metric = CanonicalMetric(
            canonical_name="bare",
            description="No aliases",
            unit="count",
        )
        assert metric.aliases == {}


class TestCanonicalMetricsRegistry:
    def test_organic_traffic_defined(self):
        assert "organic_traffic" in CANONICAL_METRICS
        m = CANONICAL_METRICS["organic_traffic"]
        assert m.unit == "clicks"
        assert "ga4" in m.aliases
        assert "profound" in m.aliases

    def test_total_metrics_count(self):
        assert len(CANONICAL_METRICS) >= 7


class TestResolveMetric:
    def test_resolve_ga4_organic(self):
        assert resolve_metric("ga4", "organic_total") == "organic_traffic"

    def test_resolve_profound_organic(self):
        assert resolve_metric("profound", "organic_clicks") == "organic_traffic"

    def test_resolve_serpapi_organic(self):
        assert resolve_metric("serpapi", "organicClicks") == "organic_traffic"

    def test_resolve_semrush_organic(self):
        assert resolve_metric("semrush", "Organic Traffic") == "organic_traffic"

    def test_resolve_places_rating(self):
        assert resolve_metric("places_api", "rating") == "review_rating"

    def test_resolve_gbp_reviews(self):
        assert resolve_metric("gbp_auditor", "reviews") == "review_count"

    def test_resolve_places_user_rating_count(self):
        assert resolve_metric("places_api", "user_rating_count") == "review_count"

    def test_resolve_unknown_source(self):
        assert resolve_metric("unknown_source", "some_metric") is None

    def test_resolve_unknown_metric(self):
        assert resolve_metric("ga4", "nonexistent_metric") is None

    def test_resolve_ga4_new(self):
        assert resolve_metric("ga4_new", "organic_new") == "organic_traffic"


class TestGetAllNames:
    def test_geo_score_sources(self):
        names = get_all_names("geo_score")
        assert names is not None
        assert "places_api" in names
        assert "gbp_auditor" in names

    def test_organic_traffic_sources(self):
        names = get_all_names("organic_traffic")
        assert names is not None
        assert "ga4" in names
        assert "profound" in names
        assert "serpapi" in names
        assert "semrush" in names

    def test_nonexistent_metric(self):
        assert get_all_names("nonexistent_metric") is None


class TestMetricExists:
    def test_existing_metric(self):
        assert metric_exists("organic_traffic")
        assert metric_exists("geo_score")
        assert metric_exists("adr")

    def test_nonexistent_metric(self):
        assert not metric_exists("fake_metric")


class TestListSources:
    def test_sources_include_core_apis(self):
        sources = list_sources()
        for expected in ["ga4", "places_api", "gbp_auditor", "serpapi", "profound", "semrush"]:
            assert expected in sources, f"Source {expected} not in {sources}"

    def test_sources_returns_sorted_list(self):
        sources = list_sources()
        assert sources == sorted(sources)

    def test_sources_has_multiple(self):
        assert len(list_sources()) >= 6
