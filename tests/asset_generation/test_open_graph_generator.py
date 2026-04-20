"""Tests for OpenGraphGenerator — FASE-4: Asset B4 Open Graph."""

import logging
import tempfile
from pathlib import Path

import pytest

from modules.asset_generation.open_graph_generator import OpenGraphGenerator, HotelOGData


# Test data for Amazilia Hotel
HOTEL_DATA = {
    "hotel_name": "Amazilia Hotel Campestre",
    "rating": 4.5,
    "review_count": 202,
    "address": "Via Pereira a #Entrada 8 Cafelia, CERRITOS, Pereira, Risaralda",
    "phone": "+57 310 4019049",
    "website_url": "https://amaziliahotel.com/",
    "photos": [
        {"url": "https://example.com/photo1.jpg"}
    ]
}


class TestOpenGraphGenerator:
    """Test suite for OpenGraphGenerator."""
    
    def test_generate_creates_html_file(self):
        """Test that generator creates an HTML file with meta tags."""
        generator = OpenGraphGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            result_path = generator.generate(HOTEL_DATA, output_dir)
            
            # Check file exists
            assert result_path.exists()
            assert result_path.suffix == ".html"
            
            # Check content
            content = result_path.read_text(encoding='utf-8')
            assert "og:title" in content
            assert "og:description" in content
            assert "og:type" in content
            assert "og:locale" in content
            assert "es_CO" in content
    
    def test_generate_uses_real_data(self):
        """Test that generator uses real hotel data, not placeholders."""
        generator = OpenGraphGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            result_path = generator.generate(HOTEL_DATA, output_dir)
            
            content = result_path.read_text(encoding='utf-8')
            
            # Check real data is used
            assert "Amazilia Hotel Campestre" in content
            assert "4.5" in content
            assert "202" in content
            assert "+57 310 4019049" in content
            
            # Check no placeholders
            assert "{{" not in content
            assert "}}" not in content
            assert "$$" not in content
            assert "[[" not in content
    
    def test_generate_includes_photo_url(self):
        """Test that generator includes photo URL when available."""
        generator = OpenGraphGenerator()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            result_path = generator.generate(HOTEL_DATA, output_dir)
            
            content = result_path.read_text(encoding='utf-8')
            
            # Check photo URL is included
            assert "og:image" in content
            assert "https://example.com/photo1.jpg" in content
    
    def test_generate_without_photo(self):
        """Test that generator works without photo URL."""
        generator = OpenGraphGenerator()
        data_without_photo = HOTEL_DATA.copy()
        data_without_photo.pop('photos', None)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_dir = Path(temp_dir)
            result_path = generator.generate(data_without_photo, output_dir)
            
            content = result_path.read_text(encoding='utf-8')
            
            # Should still generate valid HTML
            assert "og:title" in content
            assert "og:image" not in content  # No photo, no image tag
    
    def test_extract_og_data(self):
        """Test data extraction from hotel data."""
        generator = OpenGraphGenerator()
        og_data = generator._extract_og_data(HOTEL_DATA)
        
        assert isinstance(og_data, HotelOGData)
        assert og_data.hotel_name == "Amazilia Hotel Campestre"
        assert og_data.rating == 4.5
        assert og_data.review_count == 202
        assert og_data.phone == "+57 310 4019049"
        assert og_data.photo_url == "https://example.com/photo1.jpg"
    
    def test_generate_html_structure(self):
        """Test that generated HTML has proper structure."""
        generator = OpenGraphGenerator()
        og_data = generator._extract_og_data(HOTEL_DATA)
        html = generator._generate_html(og_data)
        
        # Check HTML structure
        assert "<!-- Open Graph Meta Tags" in html
        assert '<meta property="og:type" content="hotel" />' in html
        assert '<meta property="og:title" content="Amazilia Hotel Campestre" />' in html
        assert '<meta property="og:locale" content="es_CO" />' in html
        
        # Check Twitter Card tags
        assert '<meta name="twitter:card" content="summary_large_image" />' in html
        
        # Check structured data
        assert '<script type="application/ld+json">' in html
        assert '"@type": "Hotel"' in html
    
    def test_create_description(self):
        """Test description creation from hotel data."""
        generator = OpenGraphGenerator()
        
        # With address
        description = generator._create_description(HOTEL_DATA)
        # Description should include rating and review count
        assert "4.5" in description
        assert "202" in description
        assert "Hotel boutique" in description or "Eje Cafetero" in description
        
        # Without address
        data_no_address = HOTEL_DATA.copy()
        data_no_address.pop('address', None)
        description = generator._create_description(data_no_address)
        assert "Eje Cafetero" in description
    
    def test_extract_city(self):
        """Test city extraction from address."""
        generator = OpenGraphGenerator()
        
        # Test with Colombian address
        address = "Via Pereira a #Entrada 8 Cafelia, CERRITOS, Pereira, Risaralda"
        city = generator._extract_city(address)
        assert city in ["CERRITOS", "Pereira", "Risaralda"]
        
        # Test with empty address
        city = generator._extract_city("")
        assert city == "el Eje Cafetero"


def test_open_graph_generator():
    """Main test function for Open Graph generator."""
    generator = OpenGraphGenerator()
    
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        result_path = generator.generate(HOTEL_DATA, output_dir)
        
        # Verify file was created
        assert result_path.exists()
        
        # Verify content
        content = result_path.read_text(encoding='utf-8')
        assert len(content) > 100  # Not empty
        assert "og:title" in content
        assert "Amazilia Hotel Campestre" in content
        
        # Verify no placeholders
        assert "{{" not in content
        assert "}}" not in content
        
        print(f"✅ Open Graph generator test passed: {result_path}")
        return True


if __name__ == "__main__":
    test_open_graph_generator()