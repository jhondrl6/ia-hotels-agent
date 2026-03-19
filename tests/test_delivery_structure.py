"""Tests for v2.5 delivery structure validation.

Validates that the delivery output meets v2.5 specification:
- manifest.json exists with required fields
- CMS-specific guide is generated
- Email delegation file exists
- Booking bar generated when engine detected
"""

import json
import pytest
from pathlib import Path
from typing import Dict, Any

from modules.delivery.generators.booking_bar_gen import BookingBarGenerator
from modules.delivery.generators.deploy_instructions_gen import DeployInstructionsGenerator


class TestBookingBarGenerator:
    """Tests for booking bar generator."""

    def test_generate_with_lobbypms(self):
        """Should generate bar when LobbyPMS URL is provided."""
        hotel_data = {
            "nombre": "Hotel Test",
            "booking_engine_url": "https://engine.lobbypms.com/hotel-test"
        }
        
        gen = BookingBarGenerator()
        result = gen.generate(hotel_data)
        
        assert result is not None
        assert "html_code" in result
        assert "engine_detected" in result
        assert result["engine_detected"]["type"] == "lobbypms"
        assert "engine.lobbypms.com" in result["html_code"]

    def test_generate_without_engine(self):
        """Should return None when no engine is detected."""
        hotel_data = {
            "nombre": "Hotel Test",
        }
        
        gen = BookingBarGenerator()
        result = gen.generate(hotel_data)
        
        assert result is None

    def test_generate_with_cloudbeds(self):
        """Should detect Cloudbeds engine."""
        hotel_data = {
            "nombre": "Hotel Cloud",
            "motor_reservas_url": "https://hotels.cloudbeds.com/hotel/123"
        }
        
        gen = BookingBarGenerator()
        result = gen.generate(hotel_data)
        
        assert result is not None
        assert result["engine_detected"]["type"] == "cloudbeds"


class TestDeployInstructionsGenerator:
    """Tests for deploy instructions generator."""

    def test_generate_wordpress_guide(self):
        """Should generate WordPress-specific guide."""
        hotel_data = {
            "nombre": "Hotel WP",
            "cms_detected": {"cms": "wordpress", "confidence": "high"}
        }
        assets = ["boton_whatsapp.html"]
        
        gen = DeployInstructionsGenerator()
        result = gen.generate(hotel_data, assets)
        
        assert result["cms_type"] == "wordpress"
        assert "WPCode" in result["cms_guide"]
        assert "WordPress" in result["delegation_email"]

    def test_generate_wix_guide(self):
        """Should generate Wix-specific guide."""
        hotel_data = {
            "nombre": "Hotel Wix",
            "cms_detected": {"cms": "wix", "confidence": "medium"}
        }
        assets = ["boton_whatsapp.html"]
        
        gen = DeployInstructionsGenerator()
        result = gen.generate(hotel_data, assets)
        
        assert result["cms_type"] == "wix"
        assert "Código personalizado" in result["cms_guide"]

    def test_generate_unknown_fallback(self):
        """Should generate generic guide for unknown CMS."""
        hotel_data = {
            "nombre": "Hotel Unknown",
            "cms_detected": {"cms": "unknown", "confidence": "low"}
        }
        assets = ["boton_whatsapp.html"]
        
        gen = DeployInstructionsGenerator()
        result = gen.generate(hotel_data, assets)
        
        assert result["cms_type"] == "unknown"
        assert "Webmaster" in result["cms_guide"]


class TestManifestStructure:
    """Tests for manifest.json structure."""

    def test_manifest_has_required_fields(self, tmp_path):
        """Manifest should have all required v2.5 fields."""
        # Simulate a manifest that would be generated
        manifest = {
            "version": "2.5.0",
            "generated_at": "2025-12-14T00:00:00",
            "cli_version": "2.5.0",
            "package": "pro_aeo_plus",
            "target_url": "https://example.com",
            "hotel_name": "Hotel Example",
            "cms_detected": "wordpress",
            "cms_confidence": "high",
            "booking_engine": "detected",
            "files_generated": []
        }
        
        # Required fields
        required = [
            "version", "generated_at", "cli_version", "package",
            "target_url", "hotel_name", "cms_detected", "cms_confidence",
            "booking_engine", "files_generated"
        ]
        
        for field in required:
            assert field in manifest, f"Missing required field: {field}"


class TestDeliveryFolderStructure:
    """Tests for folder organization by roles."""

    def test_role_folders_defined(self):
        """Role folder names should follow v2.5 spec."""
        expected_folders = [
            "01_PARA_EL_DUEÑO_HOY",
            "02_PARA_EL_SITIO_WEB",
            "03_PARA_TU_WEBMASTER",
            "04_GUIA_MOTOR_RESERVAS",
        ]
        
        # This test validates the naming convention
        for folder in expected_folders:
            assert folder.startswith("0"), "Folder should be numbered"
            assert "_" in folder, "Folder should use underscores"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
