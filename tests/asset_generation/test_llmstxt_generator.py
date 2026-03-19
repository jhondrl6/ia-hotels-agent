"""Tests para LLMSTXTGenerator.

Valida generación de archivos llms.txt siguiendo el estándar llmstxt.org.
"""
import sys
from pathlib import Path

# Add project root to Python path for pytest
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.asset_generation.llmstxt_generator import (
    LLMSTXTGenerator,
    get_llmstxt_generator,
)


@pytest.fixture
def generator():
    """Fixture que proporciona una instancia de LLMSTXTGenerator."""
    return LLMSTXTGenerator()


@pytest.fixture
def sample_hotel_data():
    """Sample hotel data for testing."""
    return {
        "name": "Hotel Example",
        "website": "https://hotelexample.com",
        "description": "A lovely hotel in the city center with stunning views",
        "amenities": ["Free WiFi", "Swimming Pool", "Restaurant", "Spa", "Gym"],
        "phone": "+1-555-123-4567",
        "email": "reservations@hotelexample.com",
        "address": "123 Main Street, Downtown, City 12345",
        "social_links": [
            "https://facebook.com/hotelexample",
            "https://instagram.com/hotelexample"
        ],
        "rooms_url": "https://hotelexample.com/rooms",
        "contact_url": "https://hotelexample.com/contact",
        "location_url": "https://hotelexample.com/location",
    }


class TestLLMSTXTGenerator:
    """Tests for LLMSTXTGenerator class."""
    
    def test_generate_basic_content(self, generator, sample_hotel_data):
        """Test basic content generation."""
        content = generator.generate(sample_hotel_data)
        
        assert isinstance(content, str)
        assert len(content) > 0
        assert "# Hotel Example" in content
        assert "https://hotelexample.com" in content
    
    def test_generate_includes_important_pages(self, generator, sample_hotel_data):
        """Test that Important Pages section is generated."""
        content = generator.generate(sample_hotel_data)
        
        assert "## Important Pages" in content
        assert "[Homepage]" in content
        assert "[Rooms]" in content
        assert "[Contact]" in content
        assert "[Location]" in content
    
    def test_generate_includes_services(self, generator, sample_hotel_data):
        """Test that Services section is generated."""
        content = generator.generate(sample_hotel_data)
        
        assert "## Services" in content
        assert "Free WiFi" in content
        assert "Swimming Pool" in content
        assert "Restaurant" in content
    
    def test_generate_includes_contact(self, generator, sample_hotel_data):
        """Test that Contact section is generated."""
        content = generator.generate(sample_hotel_data)
        
        assert "## Contact" in content
        assert "+1-555-123-4567" in content
        assert "reservations@hotelexample.com" in content
    
    def test_generate_includes_social(self, generator, sample_hotel_data):
        """Test that Social section is generated."""
        content = generator.generate(sample_hotel_data)
        
        assert "## Social" in content
        assert "facebook.com/hotelexample" in content
        assert "instagram.com/hotelexample" in content
    
    def test_generate_includes_policies(self, generator, sample_hotel_data):
        """Test that Policies section is generated."""
        content = generator.generate(sample_hotel_data)
        
        assert "## Policies" in content
        assert "Check-in" in content
        assert "Check-out" in content
    
    def test_generate_includes_generator_credit(self, generator, sample_hotel_data):
        """Test that generator credit is included."""
        content = generator.generate(sample_hotel_data)
        
        assert "IA Hoteles Agent" in content
        assert "---" in content
    
    def test_generate_with_minimal_data(self, generator):
        """Test generation with minimal hotel data."""
        minimal_data = {
            "name": "Minimal Hotel",
            "website": "https://minimal.com",
        }
        
        content = generator.generate(minimal_data)
        
        assert "# Minimal Hotel" in content
        assert "https://minimal.com" in content
        assert "N/A" in content
    
    def test_generate_with_empty_amenities(self, generator):
        """Test generation with empty amenities list."""
        data = {
            "name": "Hotel No Amenities",
            "website": "https://noamenities.com",
            "amenities": [],
        }
        
        content = generator.generate(data)
        
        assert "## Services" in content
        assert "not available" in content.lower()
    
    def test_generate_description_as_quote(self, generator, sample_hotel_data):
        """Test that description is formatted as quote."""
        content = generator.generate(sample_hotel_data)
        
        assert ">" in content
        assert "lovely hotel" in content.lower()
    
    def test_factory_function(self):
        """Test get_llmstxt_generator factory function."""
        gen = get_llmstxt_generator()
        assert isinstance(gen, LLMSTXTGenerator)
    
    def test_generate_amenities_limited_to_10(self, generator):
        """Test that amenities are limited to 10 items."""
        data = {
            "name": "Hotel Many Amenities",
            "website": "https://many.com",
            "amenities": [f"Amenity {i}" for i in range(20)],
        }
        
        content = generator.generate(data)
        
        count = content.count("Amenity ")
        assert count == 10
    
    def test_generate_from_assessment(self, generator):
        """Test generation from assessment data."""
        assessment = {
            "hotel_name": "Assessment Hotel",
            "url": "https://assessment.com",
            "description": "From assessment",
            "amenities": ["WiFi"],
            "phone": "+111",
            "email": "test@test.com",
            "address": "123 Test St",
            "social_links": [],
        }
        
        content = generator.generate_from_assessment(assessment)
        
        assert "Assessment Hotel" in content
        assert "From assessment" in content


class TestLLMSTXTFormat:
    """Tests for llms.txt format compliance."""
    
    def test_format_markdown_headers(self, generator):
        """Test that content uses markdown headers."""
        data = {"name": "Test", "website": "https://test.com"}
        content = generator.generate(data)
        
        assert "# " in content
        assert "## " in content
    
    def test_format_links(self, generator):
        """Test that links are properly formatted."""
        data = {"name": "Test", "website": "https://test.com"}
        content = generator.generate(data)
        
        assert "](" in content
    
    def test_format_list_items(self, generator):
        """Test that list items are properly formatted."""
        data = {"name": "Test", "website": "https://test.com", "amenities": ["WiFi"]}
        content = generator.generate(data)
        
        assert "\n- " in content
