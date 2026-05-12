"""Tests for FASE-2-DEFAULT: Eliminate cross-hotel hardcoded defaults.

Tests that open_graph_generator.py:
1. Rejects missing hotel_name
2. Rejects missing website_url
3. Produces output without "Amazilia" for valid data
4. Uses 'name' field when 'hotel_name' is missing
"""

import pytest
from modules.asset_generation.open_graph_generator import OpenGraphGenerator


class TestHotelNameValidation:
    """T4.1: Test that missing hotel_name raises ValueError."""

    def test_rejects_missing_hotel_name_empty_string(self):
        """hotel_data={'name': ''} raises ValueError."""
        generator = OpenGraphGenerator()
        hotel_data = {'name': ''}
        with pytest.raises(ValueError, match="hotel_name"):
            generator._extract_og_data(hotel_data)

    def test_rejects_missing_hotel_name_none(self):
        """hotel_data={} raises ValueError."""
        generator = OpenGraphGenerator()
        hotel_data = {}
        with pytest.raises(ValueError, match="hotel_name"):
            generator._extract_og_data(hotel_data)

    def test_rejects_missing_hotel_name_whitespace_only(self):
        """hotel_data={'hotel_name': '   '} raises ValueError."""
        generator = OpenGraphGenerator()
        hotel_data = {'hotel_name': '   '}
        with pytest.raises(ValueError, match="hotel_name"):
            generator._extract_og_data(hotel_data)


class TestWebsiteUrlValidation:
    """T4.2: Test that missing website_url raises ValueError."""

    def test_rejects_missing_website_url(self):
        """hotel_data={'hotel_name': 'X'} (no website_url) raises ValueError."""
        generator = OpenGraphGenerator()
        hotel_data = {'hotel_name': 'Test Hotel'}
        with pytest.raises(ValueError, match="website_url"):
            generator._extract_og_data(hotel_data)

    def test_rejects_empty_website_url(self):
        """hotel_data with website_url='' raises ValueError."""
        generator = OpenGraphGenerator()
        hotel_data = {'hotel_name': 'Test Hotel', 'website_url': ''}
        with pytest.raises(ValueError, match="website_url"):
            generator._extract_og_data(hotel_data)


class TestValidDataOutput:
    """T4.3: Test that valid data produces output without 'Amazilia'."""

    def test_accepts_valid_data_no_amazilia(self):
        """Valid data produces HTML without 'Amazilia'."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'hotel_name': 'Hotel test',
            'website_url': 'https://test-hotel.com',
            'description': 'Test description',
            'rating': 4.0,
            'review_count': 50,
            'address': 'Calle 123, Armenia, Quindio',
            'phone': '+57 300 1234567',
        }
        og_data = generator._extract_og_data(hotel_data)
        html = generator._generate_html(og_data)
        assert 'Amazilia' not in html
        assert 'amaziliahotel' not in html

    def test_accepts_valid_data_with_name_field(self):
        """hotel_data with 'name' (not 'hotel_name') works correctly."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'name': 'Hotel test',
            'website_url': 'https://test-hotel.com',
        }
        og_data = generator._extract_og_data(hotel_data)
        assert og_data.hotel_name == 'Hotel test'
        html = generator._generate_html(og_data)
        assert 'Hotel test' in html
        assert 'Amazilia' not in html


class TestNameFieldFallback:
    """T4.4: Test that 'name' field is used when 'hotel_name' is missing."""

    def test_uses_name_when_hotel_name_missing(self):
        """hotel_data={'name': 'Hotel X'} → output contains 'Hotel X'."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'name': 'Hotel X',
            'website_url': 'https://hotel-x.com',
        }
        og_data = generator._extract_og_data(hotel_data)
        html = generator._generate_html(og_data)
        assert 'Hotel X' in html
        assert '<!-- Open Graph Meta Tags for Hotel X -->' in html

    def test_hotel_name_takes_precedence_over_name(self):
        """Both hotel_name and name present → hotel_name wins."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'hotel_name': 'Correct Name',
            'name': 'Wrong Name',
            'website_url': 'https://test.com',
        }
        og_data = generator._extract_og_data(hotel_data)
        assert og_data.hotel_name == 'Correct Name'


class TestGenerateContentPublicAPI:
    """Test the public generate_content() API used by conditional_generator."""

    def test_generate_content_returns_string(self):
        """generate_content() returns HTML string, not Path."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'hotel_name': 'Test Hotel',
            'website_url': 'https://test.com',
            'description': 'Test desc',
            'rating': 4.0,
            'review_count': 10,
        }
        result = generator.generate_content(hotel_data)
        assert isinstance(result, str)
        assert '<meta property="og:title"' in result

    def test_generate_content_no_amazilia(self):
        """generate_content() output has no 'Amazilia'."""
        generator = OpenGraphGenerator()
        hotel_data = {
            'hotel_name': 'Mi Hotel',
            'website_url': 'https://mi-hotel.com',
        }
        result = generator.generate_content(hotel_data)
        assert 'Amazilia' not in result
        assert 'amaziliahotel' not in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])