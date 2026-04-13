"""
Tests for geo_enriched_bridge module.

Referencia: FASE-GEO-BRIDGE Tarea 4
"""

import json
import tempfile
from pathlib import Path

import pytest

from modules.asset_generation.geo_enriched_bridge import (
    try_enrich_from_geo_enriched,
    is_geo_enriched_available,
    get_enrichment_summary,
    ASSET_ENRICHMENT_MAP,
    FILENAME_HOTEL_SCHEMA_RICH,
    FILENAME_LLMS_TXT,
    FILENAME_FAQ_SCHEMA,
)


class TestTryEnrichFromGeoEnriched:
    """Tests for try_enrich_from_geo_enriched function."""

    def test_bridge_enriches_hotel_schema_from_geo_enriched(self):
        """
        Test that hotel_schema is enriched when geo_enriched version is available.
        Confidence should boost from 0.5 to 0.85.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Create hotel_schema_rich.json with real data
            hotel_schema_content = json.dumps({
                "@context": "https://schema.org",
                "@type": "Hotel",
                "name": "Amazili Hotel",
                "description": "A wonderful hotel in the coffee region",
                "url": "https://amaziliahotel.com",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Calle 10 #5-50",
                    "addressLocality": "Salento",
                    "addressRegion": "Quindio",
                    "postalCode": "631920",
                    "addressCountry": "CO"
                },
                "telephone": "+57 310 123 4567",
                "priceRange": "$$"
            }, indent=2)

            hotel_schema_path = geo_dir / FILENAME_HOTEL_SCHEMA_RICH
            hotel_schema_path.write_text(hotel_schema_content, encoding='utf-8')

            original_content = '{"@type": "Hotel", "name": "Hotel", "placeholder": true}'
            original_confidence = 0.5

            enriched_content, new_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert new_score == 0.85
            assert enriched_content == hotel_schema_content
            assert "Amazili Hotel" in enriched_content

    def test_bridge_skips_if_no_geo_enriched_dir(self):
        """
        Test that when geo_enriched/ does not exist, original content is returned.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "nonexistent_geo_enriched"

            original_content = '{"name": "Test Hotel"}'
            original_confidence = 0.5

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert result_content == original_content
            assert result_score == original_confidence

    def test_bridge_preserves_high_confidence_assets(self):
        """
        Test that assets with confidence >= 0.7 are NOT modified.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Even if geo_enriched exists, high confidence should be preserved
            (geo_dir / FILENAME_HOTEL_SCHEMA_RICH).write_text(
                '{"name": "Real Hotel"}', encoding='utf-8'
            )

            original_content = '{"name": "Already Good Hotel"}'
            high_confidence = 0.75

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",
                current_content=original_content,
                current_confidence=high_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert result_content == original_content
            assert result_score == high_confidence

    def test_bridge_handles_missing_files_gracefully(self):
        """
        Test that when geo_enriched/ exists but specific file is missing,
        original content is returned.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Create a different file, but not hotel_schema_rich.json
            (geo_dir / FILENAME_LLMS_TXT).write_text(
                "# Some other content", encoding='utf-8'
            )

            original_content = '{"name": "Test Hotel"}'
            original_confidence = 0.5

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",  # Asking for hotel_schema, but only llms.txt exists
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert result_content == original_content
            assert result_score == original_confidence

    def test_bridge_rejects_placeholder_hotel_schema(self):
        """
        Test that geo_enriched file with placeholder content ('Hotel') is NOT used.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Create a geo_enriched file with placeholder name
            placeholder_content = json.dumps({
                "@type": "Hotel",
                "name": "Hotel",  # This is a placeholder
                "url": "https://your-website.com"
            })
            (geo_dir / FILENAME_HOTEL_SCHEMA_RICH).write_text(
                placeholder_content, encoding='utf-8'
            )

            original_content = '{"name": "Original"}'
            original_confidence = 0.5

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            # Should NOT enrich because content is a placeholder
            assert result_content == original_content
            assert result_score == original_confidence

    def test_bridge_rejects_empty_geo_enriched_file(self):
        """
        Test that empty geo_enriched files are not used for enrichment.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Create empty file
            (geo_dir / FILENAME_HOTEL_SCHEMA_RICH).write_text("", encoding='utf-8')

            original_content = '{"name": "Original"}'
            original_confidence = 0.5

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="hotel_schema",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert result_content == original_content
            assert result_score == original_confidence

    def test_bridge_enriches_llms_txt(self):
        """
        Test that llms_txt asset type is enriched from geo_enriched/llms.txt.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            llms_content = """# Amazili Hotel

https://amaziliahotel.com

## Services
- Luxury accommodations
- Coffee tours
- Restaurant
"""
            (geo_dir / FILENAME_LLMS_TXT).write_text(llms_content, encoding='utf-8')

            original_content = "# Hotel\nhttps://example.com"
            original_confidence = 0.5

            enriched_content, new_score = try_enrich_from_geo_enriched(
                asset_type="llms_txt",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert new_score == 0.85
            assert "Amazili Hotel" in enriched_content
            assert "https://amaziliahotel.com" in enriched_content

    def test_bridge_enriches_faq_page(self):
        """
        Test that faq_page asset type is enriched from geo_enriched/faq_schema.json.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            faq_content = json.dumps({
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": "What time is check-in?",
                        "acceptedAnswer": {
                            "@type": "Answer",
                            "text": "Check-in is at 3:00 PM."
                        }
                    }
                ]
            }, indent=2)
            (geo_dir / FILENAME_FAQ_SCHEMA).write_text(faq_content, encoding='utf-8')

            original_content = '{"@type": "FAQPage"}'
            original_confidence = 0.5

            enriched_content, new_score = try_enrich_from_geo_enriched(
                asset_type="faq_page",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert new_score == 0.85
            assert "What time is check-in?" in enriched_content

    def test_bridge_ignores_unknown_asset_type(self):
        """
        Test that asset types not in ASSET_ENRICHMENT_MAP are returned unchanged.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            original_content = "<html>Some content</html>"
            original_confidence = 0.5

            result_content, result_score = try_enrich_from_geo_enriched(
                asset_type="some_unknown_asset",
                current_content=original_content,
                current_confidence=original_confidence,
                geo_enriched_dir=geo_dir,
                hotel_id="test_hotel"
            )

            assert result_content == original_content
            assert result_score == original_confidence


class TestIsGeoEnrichedAvailable:
    """Tests for is_geo_enriched_available function."""

    def test_returns_true_when_files_exist(self):
        """Test that True is returned when geo_enriched files exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            (geo_dir / FILENAME_HOTEL_SCHEMA_RICH).write_text(
                '{"name": "Test"}', encoding='utf-8'
            )

            assert is_geo_enriched_available(geo_dir) is True

    def test_returns_false_when_dir_does_not_exist(self):
        """Test that False is returned when geo_enriched directory doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "nonexistent"

            assert is_geo_enriched_available(geo_dir) is False

    def test_returns_false_when_no_matching_files(self):
        """Test that False is returned when directory exists but no enrichment files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Create unrelated file
            (geo_dir / "unrelated.txt").write_text("content", encoding='utf-8')

            assert is_geo_enriched_available(geo_dir) is False


class TestGetEnrichmentSummary:
    """Tests for get_enrichment_summary function."""

    def test_returns_summary_with_availability(self):
        """Test that summary correctly reports availability of each file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            geo_dir = Path(tmpdir) / "geo_enriched"
            geo_dir.mkdir()

            # Only hotel_schema_rich exists with real data
            hotel_schema_content = json.dumps({
                "@type": "Hotel",
                "name": "Real Hotel Name",
                "url": "https://real-hotel.com"
            })
            (geo_dir / FILENAME_HOTEL_SCHEMA_RICH).write_text(
                hotel_schema_content, encoding='utf-8'
            )

            summary = get_enrichment_summary(geo_dir)

            assert summary["hotel_schema"]["exists"] is True
            assert summary["hotel_schema"]["has_real_data"] is True
            assert summary["llms_txt"]["exists"] is False
            assert summary["faq_page"]["exists"] is False
