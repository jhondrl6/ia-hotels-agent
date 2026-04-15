"""Tests for new asset types in conditional generator."""
import pytest
import json
from pathlib import Path
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestNewAssetTypes:
    """Test generation of new asset types."""

    def setup_method(self):
        self.generator = ConditionalGenerator(output_dir="/tmp/test_output")

    def test_generate_geo_playbook(self):
        """Test geo_playbook generation."""
        result = self.generator._generate_geo_playbook(
            {"geo_score": 50}, "Hotel Test"
        )

        assert "Geo Playbook" in result
        assert "Hotel Test" in result
        assert "Google Business Profile" in result
        assert "Checklist" in result or "Acciones" in result

    def test_generate_review_plan(self):
        """Test review_plan generation."""
        result = self.generator._generate_review_plan(
            {"reviews": 10}, "Hotel Test"
        )

        assert "Plan de Reviews" in result or "Reviews" in result
        assert "Hotel Test" in result
        assert "Estrategia" in result or "Objetivos" in result

    def test_generate_review_widget(self):
        """Test review_widget generation."""
        result = self.generator._generate_review_widget(
            {"rating": 4.5}, "Hotel Test"
        )

        assert "<div" in result  # HTML content
        assert "review-widget" in result or "widget" in result.lower()
        assert "Hotel Test" in result

    def test_generate_org_schema(self):
        """Test org_schema generation."""
        result = self.generator._generate_org_schema(
            {"website": "https://test.com", "phone": "+57 123"},
            "Hotel Test"
        )

        # Should be valid JSON
        schema = json.loads(result)
        assert schema["@type"] == "Organization"
        assert schema["name"] == "Hotel Test"
        assert "https://schema.org" in schema["@context"]

    def test_generate_voice_assistant_guide(self):
        """Test voice_assistant_guide generation (FASE-C)."""
        import tempfile
        import shutil
        
        # Setup with temp output dir
        temp_dir = tempfile.mkdtemp()
        try:
            generator = ConditionalGenerator(output_dir=temp_dir)
            
            hotel_data = {
                "nombre": "Hotel Test",
                "ubicacion": "Pereira, Colombia",
                "hotel_id": "hotel_test_001"
            }
            
            # Test generation
            result = generator._generate_voice_assistant_guide(hotel_data)
            
            # Verify the index file content
            assert "Voice Assistant Integration Package" in result
            assert "Hotel Test" in result
            assert "google_assistant_checklist.md" in result
            assert "apple_business_connect_guide.md" in result
            assert "alexa_skill_blueprint.md" in result
            
            # Verify subdocuments are stored
            assert hasattr(generator, '_voice_guide_subdocuments')
            guides = generator._voice_guide_subdocuments["hotel_test_001"]
            assert "google_assistant_checklist" in guides
            assert "apple_business_connect_guide" in guides
            assert "alexa_skill_blueprint" in guides
            
            # Verify each guide has substantial content
            assert len(guides["google_assistant_checklist"]) > 500
            assert len(guides["apple_business_connect_guide"]) > 500
            assert len(guides["alexa_skill_blueprint"]) > 500
            
            # Verify Google Assistant guide mentions key terms
            assert "Google Business Profile" in guides["google_assistant_checklist"]
            assert "D-U-N-S" in guides["apple_business_connect_guide"] or "D-U-N-S" in guides["google_assistant_checklist"]
            assert "Alexa" in guides["alexa_skill_blueprint"]
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

    def test_voice_guide_assets_in_catalog(self):
        """Test voice_assistant_guide is in ASSET_CATALOG."""
        from modules.asset_generation.asset_catalog import ASSET_CATALOG
        
        assert "voice_assistant_guide" in ASSET_CATALOG
        entry = ASSET_CATALOG["voice_assistant_guide"]
        assert entry.status.value == "implemented"
        assert entry.required_confidence == 0.4
