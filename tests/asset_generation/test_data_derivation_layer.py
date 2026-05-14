"""
Tests for DataDerivationLayer — FASE-0H-G8.

Validates that missing fields (og_tags_detected, org_data, ga4_available,
organic_traffic, metadata) are correctly derived from audit_report structures.
"""

import json
import pytest
from pathlib import Path

# Import the module under test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from modules.asset_generation.data_derivation_layer import (
    DataDerivationLayer,
    merge_derived_into_validated,
)


FIXTURE_DIR = Path(__file__).parent.parent / "fixtures"
FIXTURE_PATH = FIXTURE_DIR / "audit_report_hotelcastillareal.json"


def load_fixture():
    """Load the Hotel Castilla Real audit_report fixture."""
    if not FIXTURE_PATH.exists():
        pytest.skip(f"Fixture not found: {FIXTURE_PATH}")
    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


class TestDataDerivationLayer:
    """Unit tests for the DataDerivationLayer."""

    def setup_method(self):
        self.layer = DataDerivationLayer()

    # === og_tags_detected ===

    def test_derive_og_tags_detected_false_when_open_graph_false(self):
        """og_tags_detected=False when seo_elements.open_graph=False."""
        audit = {
            "seo_elements": {
                "open_graph": False,
                "open_graph_tags": {},
                "notes": "Detected 0 OG tags",
            }
        }
        derived = self.layer.derive(audit)
        assert "og_tags_detected" in derived
        assert derived["og_tags_detected"]["value"] is False
        assert derived["og_tags_detected"]["inferred"] is True
        assert derived["og_tags_detected"]["confidence"] == 0.85

    def test_derive_og_tags_detected_true_when_open_graph_true(self):
        """og_tags_detected=True when seo_elements.open_graph=True."""
        audit = {
            "seo_elements": {
                "open_graph": True,
                "open_graph_tags": {"og:title": "Hotel Test"},
            }
        }
        derived = self.layer.derive(audit)
        assert "og_tags_detected" in derived
        assert derived["og_tags_detected"]["value"] is True

    def test_derive_og_tags_detected_true_from_tags_dict(self):
        """og_tags_detected=True when open_graph_tags dict is non-empty."""
        audit = {
            "seo_elements": {
                "open_graph": False,
                "open_graph_tags": {"og:title": "Hotel", "og:image": "img.jpg"},
            }
        }
        derived = self.layer.derive(audit)
        assert "og_tags_detected" in derived
        assert derived["og_tags_detected"]["value"] is True

    def test_derive_og_tags_no_seo_elements(self):
        """Returns nothing when seo_elements is missing."""
        audit = {"schema": {}}
        derived = self.layer.derive(audit)
        assert "og_tags_detected" not in derived

    # === org_data ===

    def test_derive_org_data_from_schema_detected(self):
        """org_data derived when schema.org_schema_detected=True."""
        audit = {
            "schema": {
                "org_schema_detected": True,
                "properties": {"name": "Hotel Test", "url": "https://test.com"},
            },
            "hotel_name": "Hotel Test",
        }
        derived = self.layer.derive(audit)
        assert "org_data" in derived
        assert derived["org_data"]["value"]["name"] == "Hotel Test"
        assert derived["org_data"]["confidence"] == 0.8
        assert derived["org_data"]["inferred"] is True

    def test_derive_org_data_fallback_from_gbp(self):
        """org_data fallback from GBP when no schema detected."""
        audit = {
            "schema": {"org_schema_detected": False, "properties": {}},
            "hotel_name": "Hotel GBP",
            "gbp": {
                "website": "https://hotelgbp.com",
                "address": "Calle 123",
                "phone": "555-1234",
            },
        }
        derived = self.layer.derive(audit)
        assert "org_data" in derived
        assert derived["org_data"]["value"]["name"] == "Hotel GBP"
        assert derived["org_data"]["value"]["url"] == "https://hotelgbp.com"
        assert derived["org_data"]["confidence"] == 0.5

    def test_derive_org_data_empty_when_nothing_available(self):
        """org_data with low confidence when nothing is derivable."""
        audit = {"schema": {}, "hotel_name": ""}
        derived = self.layer.derive(audit)
        assert "org_data" in derived
        assert derived["org_data"]["value"] == {}
        assert derived["org_data"]["confidence"] == 0.3

    # === ga4_available ===

    def test_derive_ga4_not_found_returns_none(self):
        """ga4_available returns None (omitted) when no indicators found."""
        audit = {"ai_crawlers": {"allowed_crawlers": []}, "seo_elements": {"notes": ""}}
        derived = self.layer.derive(audit)
        assert "ga4_available" not in derived  # Nothing derivable

    def test_derive_ga4_from_crawler(self):
        """ga4_available=True when analytics crawler detected."""
        audit = {
            "ai_crawlers": {
                "allowed_crawlers": ["Googlebot", "google-analytics", "Bingbot"]
            }
        }
        derived = self.layer.derive(audit)
        assert "ga4_available" in derived
        assert derived["ga4_available"]["value"] is True
        assert derived["ga4_available"]["confidence"] == 0.7

    # === organic_traffic ===

    def test_derive_organic_traffic_returns_none_when_no_data(self):
        """organic_traffic omitted when no proxy data available."""
        audit = {"performance": {"has_field_data": False}}
        derived = self.layer.derive(audit)
        assert "organic_traffic" not in derived

    def test_derive_organic_traffic_from_proxies(self):
        """organic_traffic includes proxy metrics when available."""
        audit = {
            "performance": {"has_field_data": True, "mobile_score": 75},
            "llm_report": {"share_of_voice": 0.15},
        }
        derived = self.layer.derive(audit)
        assert "organic_traffic" in derived
        assert derived["organic_traffic"]["value"]["mobile_score"] == 75
        assert derived["organic_traffic"]["value"]["share_of_voice"] == 0.15
        assert derived["organic_traffic"]["confidence"] == 0.4

    # === metadata ===

    def test_derive_metadata_from_audit(self):
        """metadata derived from audit.metadata section."""
        audit = {
            "metadata": {
                "cms_detected": "wordpress",
                "title": "Hotel Test",
                "has_issues": True,
            }
        }
        derived = self.layer.derive(audit)
        assert "metadata" in derived
        assert derived["metadata"]["value"]["cms_detected"] == "wordpress"
        assert derived["metadata"]["confidence"] == 0.8

    def test_derive_metadata_none_when_empty(self):
        """metadata omitted when audit.metadata is empty or missing."""
        derived = self.layer.derive({"metadata": {}})
        assert "metadata" not in derived

    # === Hotel Castilla Real fixture test ===

    def test_hotelcastillareal_fixture_derives_fields(self):
        """Real fixture should derive og_tags_detected and metadata."""
        audit = load_fixture()
        derived = self.layer.derive(audit)

        # og_tags_detected should be derived (open_graph=False in fixture)
        assert "og_tags_detected" in derived
        assert derived["og_tags_detected"]["value"] is False

        # metadata should be derived (has 8 keys in fixture)
        assert "metadata" in derived
        assert derived["metadata"]["value"]["cms_detected"] == "wordpress"

        # org_data should be derived (fallback from GBP)
        assert "org_data" in derived
        # GBP has website, address, phone
        assert "name" in derived["org_data"]["value"]

        # ga4 and organic_traffic should NOT be derived (no data in this fixture)
        assert "ga4_available" not in derived
        assert "organic_traffic" not in derived


class TestMergeDerivedIntoValidated:
    """Tests for merge_derived_into_validated."""

    def test_merge_adds_new_fields(self):
        """New derived fields are added to validated_data."""
        validated = {"hotel_data": {"name": "Test"}}
        derived = {
            "og_tags_detected": {"value": True, "confidence": 0.85, "source": "test"},
        }
        result = merge_derived_into_validated(validated, derived)
        assert "og_tags_detected" in result

    def test_merge_does_not_overwrite_existing(self):
        """Existing fields are NOT overwritten by derived data."""
        validated = {"og_tags_detected": {"value": True, "confidence": 0.95}}
        derived = {
            "og_tags_detected": {"value": False, "confidence": 0.85},
        }
        result = merge_derived_into_validated(validated, derived)
        # Should keep original value (True, 0.95), not derived (False, 0.85)
        assert result["og_tags_detected"]["value"] is True
        assert result["og_tags_detected"]["confidence"] == 0.95

    def test_merge_empty_derived_noop(self):
        """Empty derived dict changes nothing."""
        validated = {"hotel_data": {"name": "Test"}}
        result = merge_derived_into_validated(validated.copy(), {})
        assert result == validated

    def test_merge_preserves_existing_keys(self):
        """Existing keys are untouched when merging."""
        validated = {"hotel_data": {"name": "Test"}, "whatsapp": "555"}
        derived = {
            "metadata": {"value": {"cms": "wp"}, "confidence": 0.8},
        }
        result = merge_derived_into_validated(validated, derived)
        assert "hotel_data" in result
        assert "whatsapp" in result
        assert "metadata" in result
