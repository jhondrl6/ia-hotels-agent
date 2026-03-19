"""Tests for feature flags system."""

import os
import pytest
from modules.financial_engine.feature_flags import (
    FinancialFeatureFlags,
    RolloutMode,
    get_flags,
    reset_flags,
    is_v410_active,
)


class TestFeatureFlags:
    """Test suite for feature flags."""
    
    def test_default_production_safe(self):
        """Test that defaults are production-safe."""
        flags = FinancialFeatureFlags()
        
        assert flags.regional_adr_enabled is False
        assert flags.pricing_hybrid_enabled is False
        assert flags.financial_v410_enabled is False
        assert flags.regional_adr_mode == RolloutMode.SHADOW
    
    def test_from_env(self, monkeypatch):
        """Test loading from environment variables."""
        monkeypatch.setenv("FINANCIAL_REGIONAL_ADR_ENABLED", "true")
        monkeypatch.setenv("FINANCIAL_PRICING_HYBRID_MODE", "canary")
        monkeypatch.setenv("FINANCIAL_MAX_ADR_DEVIATION", "50.0")
        
        reset_flags()
        flags = FinancialFeatureFlags.from_env()
        
        assert flags.regional_adr_enabled is True
        assert flags.pricing_hybrid_mode == RolloutMode.CANARY
        assert flags.max_adr_deviation_pct == 50.0
    
    def test_should_use_regional_adr(self):
        """Test regional ADR usage decision."""
        # Disabled
        flags = FinancialFeatureFlags(regional_adr_enabled=False)
        assert flags.should_use_regional_adr() is False
        
        # Enabled but legacy mode
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.FORCE_LEGACY,
        )
        assert flags.should_use_regional_adr() is False
        
        # Enabled and active
        flags = FinancialFeatureFlags(
            regional_adr_enabled=True,
            regional_adr_mode=RolloutMode.ACTIVE,
        )
        assert flags.should_use_regional_adr() is True
    
    def test_should_calculate_shadow(self):
        """Test shadow calculation decision."""
        # Shadow mode enabled (default pricing_hybrid_mode is SHADOW)
        flags = FinancialFeatureFlags(
            regional_adr_mode=RolloutMode.ACTIVE,  # Not shadow
            shadow_logging_enabled=True,
        )
        # Pricing is still SHADOW, so should calculate shadow
        assert flags.should_calculate_shadow() is True
        
        # Both modes ACTIVE (no shadow)
        flags = FinancialFeatureFlags(
            regional_adr_mode=RolloutMode.ACTIVE,
            pricing_hybrid_mode=RolloutMode.ACTIVE,
            shadow_logging_enabled=True,
        )
        assert flags.should_calculate_shadow() is False
        
        # Shadow logging disabled
        flags = FinancialFeatureFlags(shadow_logging_enabled=False)
        assert flags.should_calculate_shadow() is False
    
    def test_production_safe_factory(self):
        """Test production-safe factory method."""
        flags = FinancialFeatureFlags.production_safe()
        
        assert flags.regional_adr_enabled is False
        assert flags.pricing_hybrid_enabled is False
    
    def test_full_enabled_factory(self):
        """Test full-enabled factory method."""
        flags = FinancialFeatureFlags.full_enabled()
        
        assert flags.regional_adr_enabled is True
        assert flags.pricing_hybrid_enabled is True
        assert flags.regional_adr_mode == RolloutMode.ACTIVE
    
    def test_is_v410_active(self, monkeypatch):
        """Test v4.1.0 active check."""
        # Not active by default
        reset_flags()
        monkeypatch.setattr(
            'modules.financial_engine.feature_flags._flags',
            FinancialFeatureFlags.production_safe()
        )
        assert is_v410_active() is False
        
        # Active when all conditions met
        reset_flags()
        monkeypatch.setattr(
            'modules.financial_engine.feature_flags._flags',
            FinancialFeatureFlags.full_enabled()
        )
        assert is_v410_active() is True
    
    def test_env_bool_parsing(self, monkeypatch):
        """Test boolean parsing from env."""
        test_cases = [
            ("true", True),
            ("TRUE", True),
            ("1", True),
            ("yes", True),
            ("on", True),
            ("false", False),
            ("FALSE", False),
            ("0", False),
            ("no", False),
        ]
        
        for value, expected in test_cases:
            monkeypatch.setenv("FINANCIAL_SHADOW_LOGGING_ENABLED", value)
            flags = FinancialFeatureFlags.from_env()
            if expected:
                assert flags.shadow_logging_enabled is True, f"Failed for {value}"
            else:
                assert flags.shadow_logging_enabled is False, f"Failed for {value}"
