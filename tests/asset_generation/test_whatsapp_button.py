"""Tests for whatsapp_button asset generation.

Validates that whatsapp_button:
- Is in the catalog as IMPLEMENTED
- Has promised_by including "always"
- Generates HTML even without WhatsApp data (fallback)
- Is in fast_assets and standard_assets lists
"""

import pytest
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestWhatsAppButtonCatalog:
    """Test whatsapp_button catalog entry."""

    def test_whatsapp_button_exists_in_catalog(self):
        """whatsapp_button must exist in the catalog."""
        assert "whatsapp_button" in ASSET_CATALOG

    def test_whatsapp_button_is_implemented(self):
        """whatsapp_button must be IMPLEMENTED."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.status == AssetStatus.IMPLEMENTED

    def test_whatsapp_button_has_promised_by_always(self):
        """whatsapp_button promised_by must include 'always'."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert "always" in entry.promised_by

    def test_whatsapp_button_not_blocking(self):
        """whatsapp_button must not block on failure (has fallback)."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.block_on_failure is False

    def test_whatsapp_button_has_fallback(self):
        """whatsapp_button must have a fallback action."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert entry.fallback is not None
        assert "generate_basic_whatsapp" in entry.fallback


class TestWhatsAppButtonGeneration:
    """Test whatsapp_button generation."""

    def test_whatsapp_in_fast_assets(self):
        """whatsapp_button must be in _fast_assets for LOW data quality."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen._fast_assets

    def test_whatsapp_in_standard_assets(self):
        """whatsapp_button must be in _standard_assets for MED data quality."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen._standard_assets

    def test_whatsapp_generates_with_data(self, tmp_path):
        """Test generation with WhatsApp phone data."""
        from modules.data_validation import DataPoint, DataSource
        from datetime import datetime

        gen = ConditionalGenerator(output_dir=str(tmp_path))
        dp = DataPoint("whatsapp")
        dp.add_source(DataSource("test", "+573001234567", datetime.now().isoformat()))
        validated_data = {"whatsapp": dp}

        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test_hotel",
        )
        assert result["success"] is True
        assert result["status"] in ("success", "warning")

    def test_whatsapp_generates_without_data(self, tmp_path):
        """whatsapp_button should generate even without WhatsApp data (fallback)."""
        gen = ConditionalGenerator(output_dir=str(tmp_path))
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={},
            hotel_name="Test Hotel",
            hotel_id="test_hotel",
        )
        # NEVER_BLOCK: should succeed with warning, not blocked
        assert result["success"] is True
        assert result["status"] in ("success", "warning")

    def test_whatsapp_in_generation_strategies(self):
        """whatsapp_button must be in GENERATION_STRATEGIES."""
        gen = ConditionalGenerator()
        assert "whatsapp_button" in gen.GENERATION_STRATEGIES
