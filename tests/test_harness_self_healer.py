"""Tests for Agent Harness Self-Healer."""

import json
import tempfile
from pathlib import Path

import pytest

from agent_harness.self_healer import SelfHealer, ErrorMatch, RecoveryStrategy


class TestSelfHealer:
    """Tests for SelfHealer class."""
    
    @pytest.fixture
    def temp_catalog(self):
        """Create a temporary error catalog."""
        catalog = {
            "version": "1.0",
            "errors": [
                {
                    "id": "ERR-001",
                    "name": "Timeout Error",
                    "pattern": "TimeoutError|timed out",
                    "pattern_type": "regex",
                    "category": "network",
                    "severity": "transient",
                    "recovery": {
                        "strategy": "retry_with_params",
                        "message": "Timeout detected. Retrying with longer wait.",
                        "retry_allowed": True,
                        "param_adjustments": {"timeout": "multiply:2"},
                        "max_retries": 2,
                    },
                },
                {
                    "id": "ERR-002",
                    "name": "API Key Missing",
                    "pattern": "No LLM API key|API key not configured",
                    "pattern_type": "regex",
                    "category": "config",
                    "severity": "blocking",
                    "recovery": {
                        "strategy": "escalate",
                        "message": "Configure API key in .env file.",
                        "retry_allowed": False,
                    },
                },
            ],
        }
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(catalog, f)
            temp_path = Path(f.name)
        yield temp_path  # Yield AFTER file is closed to ensure content is flushed to disk
    
    @pytest.fixture
    def healer(self, temp_catalog):
        """Create a SelfHealer with temporary catalog."""
        return SelfHealer(catalog_path=temp_catalog, verbose=False)
    
    def test_match_error_finds_timeout(self, healer):
        """match_error should find timeout pattern."""
        error = TimeoutError("Connection timed out")
        
        match = healer.match_error(error)
        
        assert match.matched is True
        assert match.error_id == "ERR-001"
        assert match.category == "network"
        assert match.recovery.strategy == "retry_with_params"
    
    def test_match_error_finds_api_key_error(self, healer):
        """match_error should find API key pattern."""
        error = ValueError("No LLM API key configured")
        
        match = healer.match_error(error)
        
        assert match.matched is True
        assert match.error_id == "ERR-002"
        assert match.recovery.retry_allowed is False
    
    def test_match_error_returns_unmatched_for_unknown(self, healer):
        """match_error should return unmatched for unknown errors."""
        error = ValueError("Some random error")
        
        match = healer.match_error(error)
        
        assert match.matched is False
        assert match.error_id is None
    
    def test_should_retry_true_for_transient(self, healer):
        """should_retry should return True for transient errors."""
        error = TimeoutError("Connection timed out")
        match = healer.match_error(error)
        
        result = healer.should_retry(match, current_retries=0)
        
        assert result is True
    
    def test_should_retry_false_when_max_reached(self, healer):
        """should_retry should return False when max retries reached."""
        error = TimeoutError("Connection timed out")
        match = healer.match_error(error)
        
        result = healer.should_retry(match, current_retries=2)
        
        assert result is False
    
    def test_should_retry_false_for_blocking(self, healer):
        """should_retry should return False for blocking errors."""
        error = ValueError("No LLM API key configured")
        match = healer.match_error(error)
        
        result = healer.should_retry(match, current_retries=0)
        
        assert result is False
    
    def test_apply_param_adjustments_multiply(self, healer):
        """apply_param_adjustments should multiply values."""
        original = {"timeout": 10, "other": "value"}
        adjustments = {"timeout": "multiply:2"}
        
        result = healer.apply_param_adjustments(original, adjustments)
        
        assert result["timeout"] == 20
        assert result["other"] == "value"
    
    def test_apply_param_adjustments_add(self, healer):
        """apply_param_adjustments should add values."""
        original = {"wait_time": 5}
        adjustments = {"wait_time": "add:10"}
        
        result = healer.apply_param_adjustments(original, adjustments)
        
        assert result["wait_time"] == 15
    
    def test_execute_recovery_escalate(self, healer):
        """execute_recovery should not retry for escalate strategy."""
        error = ValueError("No LLM API key configured")
        match = healer.match_error(error)
        
        should_retry, payload, delay = healer.execute_recovery(match, {"url": "test"}, 0)
        
        assert should_retry is False
    
    def test_execute_recovery_retry_with_params(self, healer):
        """execute_recovery should return modified payload for retry."""
        error = TimeoutError("Connection timed out")
        match = healer.match_error(error)
        
        should_retry, payload, delay = healer.execute_recovery(
            match, {"url": "test", "timeout": 10}, 0
        )
        
        assert should_retry is True
        assert payload["timeout"] == 20


class TestWithMissingCatalog:
    """Tests for SelfHealer with missing catalog."""
    
    def test_init_with_missing_catalog(self):
        """SelfHealer should handle missing catalog gracefully."""
        healer = SelfHealer(
            catalog_path=Path("/nonexistent/path.json"),
            verbose=False,
        )
        
        error = TimeoutError("Test")
        match = healer.match_error(error)
        
        assert match.matched is False
