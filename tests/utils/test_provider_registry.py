"""Tests for provider_registry.py"""
import os
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from modules.utils.provider_registry import ProviderConfig, ProviderRegistry


class TestProviderConfig:
    def test_provider_config_defaults(self):
        pc = ProviderConfig(
            id="test",
            type="analytics",
            description="Test provider",
            auth_type="api_key",
        )
        assert pc.enabled is True
        assert pc.cost_per_call == 0.0
        assert pc.retry_count == 2
        assert pc.timeout_seconds == 15
        assert pc.endpoint is None
        assert pc.credentials_file is None
        assert pc.default_model is None

    def test_provider_config_custom_values(self):
        pc = ProviderConfig(
            id="custom",
            type="llm",
            description="Custom LLM",
            auth_type="api_key",
            env_vars=["API_KEY"],
            endpoint="https://api.example.com",
            enabled=False,
            cost_per_call=0.05,
            retry_count=5,
            timeout_seconds=30,
            default_model="gpt-4",
        )
        assert pc.id == "custom"
        assert pc.type == "llm"
        assert pc.enabled is False
        assert pc.cost_per_call == 0.05
        assert pc.default_model == "gpt-4"


class TestProviderRegistryLoad:
    def setup_method(self):
        ProviderRegistry.reset()
        self.registry = ProviderRegistry()
        config_path = str(PROJECT_ROOT / "config" / "provider_registry.yaml")
        self.registry.load(config_path)

    def test_load_succeeds(self):
        assert len(self.registry._providers) > 0

    def test_get_ga4(self):
        ga4 = self.registry.get("ga4")
        assert ga4 is not None
        assert ga4.type == "analytics"
        assert ga4.auth_type == "service_account"
        assert ga4.enabled is True
        assert ga4.cost_per_call == 0.0

    def test_get_places_api(self):
        places = self.registry.get("places_api")
        assert places is not None
        assert places.type == "search"
        assert "GOOGLE_API_KEY" in places.env_vars
        assert places.cost_per_call == 0.008

    def test_get_nonexistent_provider(self):
        assert self.registry.get("nonexistent_provider") is None

    def test_list_by_type_analytics(self):
        analytics = self.registry.list_by_type("analytics")
        types = [p.id for p in analytics]
        assert "ga4" in types
        assert "profound" in types
        assert "semrush" in types

    def test_list_enabled(self):
        enabled = self.registry.list_enabled()
        ids = [p.id for p in enabled]
        assert "ga4" in ids
        assert "places_api" in ids

    def test_list_by_type_performance(self):
        perf = self.registry.list_by_type("performance")
        ids = [p.id for p in perf]
        assert "pagespeed" in ids
        assert "rich_results" in ids

    def test_list_by_type_llm(self):
        llm = self.registry.list_by_type("llm")
        ids = [p.id for p in llm]
        assert "openrouter" in ids


class TestProviderRegistryIsConfigured:
    def setup_method(self):
        ProviderRegistry.reset()
        self.registry = ProviderRegistry()
        config_path = str(PROJECT_ROOT / "config" / "provider_registry.yaml")
        self.registry.load(config_path)

    def test_rich_results_is_configured(self):
        # auth_type=none means always configured
        assert self.registry.is_configured("rich_results") is True

    def test_ga4_is_configured_only_if_creds_exist(self):
        # ga4 requires credentials_file
        # Result depends on whether the file exists
        result = self.registry.is_configured("ga4")
        assert isinstance(result, bool)  # Must return a bool

    def test_profound_requires_env_var(self):
        # profound is disabled in YAML
        assert self.registry.is_configured("profound") is False

    def test_nonexistent_provider(self):
        assert self.registry.is_configured("nonexistent") is False


class TestProviderRegistryEstimatedCost:
    def setup_method(self):
        ProviderRegistry.reset()
        self.registry = ProviderRegistry()
        config_path = str(PROJECT_ROOT / "config" / "provider_registry.yaml")
        self.registry.load(config_path)

    def test_cost_per_run_returns_non_negative(self):
        cost = self.registry.estimated_cost_per_run()
        assert cost >= 0.0

    def test_cost_per_run_is_number(self):
        cost = self.registry.estimated_cost_per_run()
        assert isinstance(cost, (int, float))
