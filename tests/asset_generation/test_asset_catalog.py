"""Tests for Asset Catalog — FASE-4: Open Graph + FASE-5: WhatsApp/Voice decisions."""

import pytest

from modules.asset_generation.asset_catalog import (
    ASSET_CATALOG,
    AssetStatus,
    is_asset_implemented,
    get_implemented_assets,
    get_asset_requirements,
    get_generation_strategy
)


class TestAssetCatalog:
    """Test suite for Asset Catalog."""
    
    def test_open_graph_in_catalog(self):
        """Test that Open Graph is in the asset catalog."""
        assert "open_graph" in ASSET_CATALOG
    
    def test_open_graph_is_implemented(self):
        """Test that Open Graph asset is marked as implemented."""
        assert is_asset_implemented("open_graph") is True
    
    def test_open_graph_catalog_entry(self):
        """Test Open Graph catalog entry has correct properties."""
        entry = ASSET_CATALOG["open_graph"]
        
        assert entry.asset_type == "open_graph"
        assert entry.status == AssetStatus.IMPLEMENTED
        assert entry.required_field == "hotel_data"
        assert entry.required_confidence == 0.5
        assert entry.block_on_failure is False
        assert "no_og_tags" in entry.promised_by
    
    def test_open_graph_in_implemented_assets(self):
        """Test that Open Graph appears in implemented assets list."""
        implemented = get_implemented_assets()
        assert "open_graph" in implemented
    
    def test_open_graph_requirements(self):
        """Test that Open Graph requirements can be retrieved."""
        requirements = get_asset_requirements("open_graph")
        
        assert requirements is not None
        assert requirements["required_field"] == "hotel_data"
        assert requirements["required_confidence"] == 0.5
        assert requirements["fallback"] is None
        assert requirements["block_on_failure"] is False
    
    def test_open_graph_generation_strategy(self):
        """Test that Open Graph generation strategy can be retrieved."""
        strategy = get_generation_strategy("open_graph")
        
        assert strategy is not None
        assert strategy["template"] == "open_graph_template.html"
        assert "{prefix}open_graph_meta{suffix}.html" in strategy["output_name"]
    
    def test_open_graph_not_missing(self):
        """Test that Open Graph is not in missing assets."""
        from modules.asset_generation.asset_catalog import get_missing_assets
        missing = get_missing_assets()
        assert "open_graph" not in missing
    
    def test_open_graph_promised_by(self):
        """Test that Open Graph is promised by no_og_tags pain."""
        entry = ASSET_CATALOG["open_graph"]
        assert "no_og_tags" in entry.promised_by


def test_open_graph_in_catalog():
    """Main test function for Open Graph in catalog."""
    # Test 1: Open Graph exists in catalog
    assert "open_graph" in ASSET_CATALOG, "Open Graph not found in asset catalog"
    
    # Test 2: Open Graph is implemented
    assert is_asset_implemented("open_graph"), "Open Graph not marked as implemented"
    
    # Test 3: Open Graph has correct properties
    entry = ASSET_CATALOG["open_graph"]
    assert entry.status == AssetStatus.IMPLEMENTED
    assert entry.required_field == "hotel_data"
    
    # Test 4: Open Graph appears in implemented assets list
    implemented = get_implemented_assets()
    assert "open_graph" in implemented
    
    print("✅ Open Graph catalog test passed")
    return True


# =============================================================================
# FASE-5 Tests: WhatsApp and Voice decisions
# =============================================================================

class TestFASE5WhatsAppDecision:
    """Test suite for FASE-5 WhatsApp elimination decision."""
    
    def test_no_whatsapp_always_promised(self):
        """Test that whatsapp_button promised_by does NOT contain 'always'."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert "always" not in entry.promised_by, \
            f"WhatsApp promised_by still contains 'always': {entry.promised_by}"
    
    def test_whatsapp_still_has_valid_promises(self):
        """Test that whatsapp_button still has valid promise tags."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert "no_whatsapp_visible" in entry.promised_by
        assert "whatsapp_conflict" in entry.promised_by
    
    def test_whatsapp_promised_by_has_exactly_two_tags(self):
        """Test that whatsapp_button has exactly 2 promise tags."""
        entry = ASSET_CATALOG["whatsapp_button"]
        assert len(entry.promised_by) == 2, \
            f"Expected 2 promises, got {len(entry.promised_by)}: {entry.promised_by}"


class TestFASE5VoiceDecision:
    """Test suite for FASE-5 Voice Assistant pipeline elimination decision."""
    
    def test_no_voice_always_aeo(self):
        """Test that voice_assistant_guide promised_by is empty []."""
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.promised_by == [], \
            f"Voice promised_by should be [], got: {entry.promised_by}"
    
    def test_voice_not_promised_asset(self):
        """Test that voice_assistant_guide does not appear in promised assets."""
        from modules.asset_generation.asset_catalog import get_promised_assets
        promised = get_promised_assets()
        assert "voice_assistant_guide" not in promised, \
            "voice_assistant_guide should not be in promised assets"


class TestFASE5NoAlwaysBug:
    """Test that no asset has 'always' or 'always_aeo' in promised_by."""
    
    def test_no_always_in_any_promised_by(self):
        """Test that 'always' is not in any asset's promised_by list."""
        for asset_type, entry in ASSET_CATALOG.items():
            if asset_type == "monthly_report":
                # monthly_report exception: intentionally always
                continue
            assert "always" not in entry.promised_by, \
                f"Asset '{asset_type}' has 'always' in promised_by: {entry.promised_by}"
    
    def test_no_always_aeo_in_any_promised_by(self):
        """Test that 'always_aeo' is not in any asset's promised_by list."""
        for asset_type, entry in ASSET_CATALOG.items():
            assert "always_aeo" not in entry.promised_by, \
                f"Asset '{asset_type}' has 'always_aeo' in promised_by: {entry.promised_by}"


# =============================================================================
# FASE-PROP-D Tests: Google Maps / geo_playbook deprecation
# =============================================================================

class TestFASEPROPDGeoPlaybookDecision:
    """Test suite for FASE-PROP-D: geo_playbook deprecated as redundant with delivery GEO."""
    
    def test_geo_playbook_is_deprecated(self):
        """geo_playbook must be DEPRECATED in asset catalog."""
        entry = ASSET_CATALOG["geo_playbook"]
        assert entry.status == AssetStatus.DEPRECATED, \
            f"geo_playbook status should be DEPRECATED, got {entry.status}"
    
    def test_geo_playbook_not_implemented(self):
        """is_asset_implemented must return False for geo_playbook."""
        assert is_asset_implemented("geo_playbook") is False, \
            "geo_playbook should not be considered implemented"
    
    def test_geo_playbook_not_in_implemented_list(self):
        """geo_playbook must not appear in get_implemented_assets()."""
        implemented = get_implemented_assets()
        assert "geo_playbook" not in implemented, \
            f"geo_playbook found in implemented assets: {implemented}"
    
    def test_geo_playbook_has_no_promises(self):
        """geo_playbook promised_by must be empty."""
        entry = ASSET_CATALOG["geo_playbook"]
        assert entry.promised_by == [], \
            f"geo_playbook promised_by should be [], got: {entry.promised_by}"
    
    def test_geo_playbook_no_generation_strategy(self):
        """get_generation_strategy must return None for deprecated geo_playbook."""
        strategy = get_generation_strategy("geo_playbook")
        assert strategy is None, \
            f"geo_playbook generation strategy should be None, got: {strategy}"


if __name__ == "__main__":
    test_open_graph_in_catalog()