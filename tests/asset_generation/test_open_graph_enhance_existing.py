"""
Tests for OpenGraphGenerator enhance_existing mode (ASSET-ALIGNMENT FASE-2).

Tests that the generator:
1. Does NOT duplicate OG tags already present on the site
2. Generates all tags when no existing tags are passed (backward compat)
"""
import pytest
from modules.asset_generation.open_graph_generator import OpenGraphGenerator


class TestOpenGraphEnhanceExisting:
    """Test suite for OpenGraphGenerator enhance_existing mode."""

    def test_generate_content_with_existing_tags_no_duplication(self):
        """Enhance mode: existing OG tags are NOT duplicated in output."""
        generator = OpenGraphGenerator()

        test_data = {
            "hotel_name": "Zi One Luxury",
            "description": "Hotel de lujo en Cartagena",
            "website_url": "https://zione.co/",
            "photo_url": "https://zione.co/img/hotel.jpg",
            "rating": 4.8,
            "review_count": 200,
            "phone": "+57 300 1234567",
            "address": "Carrera 3 #8-50, Centro Histórico, Cartagena",
        }

        # Simulate 3 OG tags already present on site
        existing_og_tags = ["og:type", "og:title", "og:url"]

        content = generator.generate_content(test_data, existing_og_tags=existing_og_tags)

        # Tags that are in existing SHOULD NOT appear
        assert 'property="og:type" content="hotel"' not in content, \
            "og:type should NOT be duplicated"
        assert 'property="og:title" content="Zi One Luxury"' not in content, \
            "og:title should NOT be duplicated"
        assert 'property="og:url" content="https://zione.co/"' not in content, \
            "og:url should NOT be duplicated"

        # Tags NOT in existing SHOULD appear
        assert 'property="og:description"' in content, \
            "og:description should be generated (not in existing)"
        assert 'property="og:site_name"' in content, \
            "og:site_name should be generated (not in existing)"
        assert 'property="og:locale"' in content, \
            "og:locale should be generated (not in existing)"

        # Enhance mode comment should be present
        assert "enhance_existing" in content, \
            "enhance_existing mode comment should be present"
        assert "3 OG tags already present" in content, \
            "should mention existing tag count"

    def test_generate_content_without_existing_tags_full_regression(self):
        """Regression: no existing tags → generates all tags from scratch."""
        generator = OpenGraphGenerator()

        test_data = {
            "hotel_name": "Hotel Test",
            "description": "Hotel de prueba",
            "website_url": "https://test.com/",
            "photo_url": "https://test.com/img.jpg",
            "rating": 4.0,
            "review_count": 50,
            "phone": "+57 300 1111111",
            "address": "Calle 1, Bogotá",
        }

        # No existing tags → full generation
        content = generator.generate_content(test_data, existing_og_tags=None)

        # All standard tags should be present
        assert 'property="og:type" content="hotel"' in content
        assert 'property="og:title" content="Hotel Test"' in content
        assert 'property="og:description"' in content
        assert 'property="og:url" content="https://test.com/"' in content
        assert 'property="og:site_name" content="Hotel Test"' in content
        assert 'property="og:locale" content="es_CO"' in content
        assert 'property="og:image"' in content

        # Twitter cards should be present
        assert 'name="twitter:card"' in content
        assert 'name="twitter:title"' in content

        # Full generation mode comment
        assert "full_generation" in content, \
            "full_generation mode comment should be present"

    def test_generate_content_with_empty_list_full_generation(self):
        """Empty list → same as None, full generation."""
        generator = OpenGraphGenerator()

        test_data = {
            "hotel_name": "Hotel Empty List",
            "description": "Test",
            "website_url": "https://empty.com/",
            "rating": 3.5,
            "review_count": 20,
        }

        content = generator.generate_content(test_data, existing_og_tags=[])

        # Empty list = full generation
        assert "full_generation" in content
        assert 'property="og:type" content="hotel"' in content
        assert "Hotel Empty List" in content

    def test_generate_content_all_tags_present_generates_only_note(self):
        """All important tags already present → minimal output with note."""
        generator = OpenGraphGenerator()

        test_data = {
            "hotel_name": "Complete Hotel",
            "description": "All tags present",
            "website_url": "https://complete.com/",
            "photo_url": "https://complete.com/img.jpg",
            "rating": 4.5,
            "review_count": 100,
            "phone": "+57 300 9999999",
            "address": "Calle 100, Medellín",
        }

        # All major OG tags already present
        all_tags = [
            "og:type", "og:title", "og:description", "og:url",
            "og:site_name", "og:locale", "og:image", "og:image:alt",
            "twitter:card", "twitter:title", "twitter:description",
            "twitter:image"
        ]

        content = generator.generate_content(test_data, existing_og_tags=all_tags)

        # Enhance mode
        assert "enhance_existing" in content

        # None of the OG tags should appear (all in existing)
        assert 'property="og:type" content="hotel"' not in content
        assert 'property="og:title" content="Complete Hotel"' not in content
        assert 'property="og:description"' not in content
        assert 'property="og:url" content="https://complete.com/"' not in content
        assert 'property="og:site_name" content="Complete Hotel"' not in content
        assert 'property="og:locale" content="es_CO"' not in content

        # Non-OG tags (name="description", rating, etc.) still generated
        assert 'name="description"' in content
        assert "Complete Hotel" in content

    def test_conditional_generator_extract_existing_og_tags(self):
        """Test _extract_existing_og_tags with various input shapes."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator

        # Empty validated_data
        result = ConditionalGenerator._extract_existing_og_tags({})
        assert result == []

        # seo_elements path
        validated = {
            "seo_elements": {
                "open_graph_tags": {"og:title": "...", "og:type": "..."}
            }
        }
        result = ConditionalGenerator._extract_existing_og_tags(validated)
        assert sorted(result) == ["og:title", "og:type"]

        # direct open_graph_tags path
        validated = {
            "open_graph_tags": {"og:locale": "es_CO"}
        }
        result = ConditionalGenerator._extract_existing_og_tags(validated)
        assert result == ["og:locale"]

        # No tags → empty
        result = ConditionalGenerator._extract_existing_og_tags({"other": "data"})
        assert result == []
