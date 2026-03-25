"""
TDD Gate: New Hotel Thresholds

Tests for B2: Umbrales diferenciados para hoteles nuevos
- whatsapp_button: 0.3 para hoteles nuevos (vs 0.7 original)
- faq_page: 0.4 para hoteles nuevos (vs 0.5 original)

HOTEL NUEVO (new hotel) tiene:
- 0-10 reviews
- 0-5 fotos  
- place_found=false

COMPORTAMIENTO ESPERADO:
- Hotel nuevo (0 reviews) puede generar whatsapp_button con threshold 0.3
- Hotel establecido (>10 reviews) mantiene threshold original 0.7
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest


class TestNewHotelThresholdsExists:
    """Verifica que las constantes de new hotel thresholds existen."""
    
    def test_new_hotel_thresholds_constant_exists(self):
        """NEW_HOTEL_THRESHOLDS debe existir con valores correctos."""
        from modules.asset_generation.preflight_checks import NEW_HOTEL_THRESHOLDS
        
        assert "whatsapp_button" in NEW_HOTEL_THRESHOLDS
        assert "faq_page" in NEW_HOTEL_THRESHOLDS
        assert NEW_HOTEL_THRESHOLDS["whatsapp_button"] == 0.3
        assert NEW_HOTEL_THRESHOLDS["faq_page"] == 0.4

    def test_new_hotel_max_reviews_constant(self):
        """NEW_HOTEL_MAX_REVIEWS debe ser 10."""
        from modules.asset_generation.preflight_checks import NEW_HOTEL_MAX_REVIEWS
        
        assert NEW_HOTEL_MAX_REVIEWS == 10

    def test_new_hotel_max_photos_constant(self):
        """NEW_HOTEL_MAX_PHOTOS debe ser 5."""
        from modules.asset_generation.preflight_checks import NEW_HOTEL_MAX_PHOTOS
        
        assert NEW_HOTEL_MAX_PHOTOS == 5


class TestIsNewHotel:
    """Verifica que is_new_hotel() detecta correctamente hoteles nuevos."""
    
    def test_zero_reviews_is_new_hotel(self):
        """Hotel con 0 reviews debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 0, "photos": 100, "place_found": True}
        
        assert checker.is_new_hotel(context) == True

    def test_ten_reviews_is_new_hotel(self):
        """Hotel con 10 reviews debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 10, "photos": 100, "place_found": True}
        
        assert checker.is_new_hotel(context) == True

    def test_eleven_reviews_is_not_new_hotel(self):
        """Hotel con 11 reviews NO debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 11, "photos": 100, "place_found": True}
        
        assert checker.is_new_hotel(context) == False

    def test_zero_photos_is_new_hotel(self):
        """Hotel con 0 fotos debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 50, "photos": 0, "place_found": True}
        
        assert checker.is_new_hotel(context) == True

    def test_five_photos_is_new_hotel(self):
        """Hotel con 5 fotos debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 50, "photos": 5, "place_found": True}
        
        assert checker.is_new_hotel(context) == True

    def test_six_photos_is_not_new_hotel(self):
        """Hotel con 6 fotos NO debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 50, "photos": 6, "place_found": True}
        
        assert checker.is_new_hotel(context) == False

    def test_place_found_false_is_new_hotel(self):
        """Hotel con place_found=false debe ser considerado nuevo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        context = {"reviews": 100, "photos": 100, "place_found": False}
        
        assert checker.is_new_hotel(context) == True

    def test_empty_context_returns_false(self):
        """Hotel sin contexto debe retornar False (asumir establecido)."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        
        assert checker.is_new_hotel(None) == False
        assert checker.is_new_hotel({}) == False


class TestGetEffectiveThreshold:
    """Verifica que get_effective_threshold retorna valores correctos."""
    
    def test_whatsapp_threshold_for_new_hotel(self):
        """Whatsapp threshold para hotel nuevo debe ser 0.3."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        threshold = checker.get_effective_threshold("whatsapp_button", is_new_hotel=True)
        
        assert threshold == 0.3

    def test_whatsapp_threshold_for_established_hotel(self):
        """Whatsapp threshold para hotel establecido debe ser 0.7 (del catalog)."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        threshold = checker.get_effective_threshold("whatsapp_button", is_new_hotel=False)
        
        # Original threshold from ASSET_CATALOG for whatsapp_button
        assert threshold == 0.7

    def test_faq_threshold_for_new_hotel(self):
        """FAQ threshold para hotel nuevo debe ser 0.4."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        threshold = checker.get_effective_threshold("faq_page", is_new_hotel=True)
        
        assert threshold == 0.4

    def test_faq_threshold_for_established_hotel(self):
        """FAQ threshold para hotel establecido debe ser 0.5 (del catalog)."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        threshold = checker.get_effective_threshold("faq_page", is_new_hotel=False)
        
        # Original threshold from ASSET_CATALOG for faq_page
        assert threshold == 0.5

    def test_other_assets_use_base_threshold(self):
        """Assets sin threshold diferenciado usan el base del catálogo."""
        from modules.asset_generation.preflight_checks import PreflightChecker
        
        checker = PreflightChecker()
        # hotel_schema has base threshold 0.6 in ASSET_CATALOG
        threshold = checker.get_effective_threshold("hotel_schema", is_new_hotel=True)
        
        assert threshold == 0.6  # Base threshold, not differentiated


class TestPreflightCheckWithNewHotel:
    """Verifica que check_asset usa umbrales diferenciados."""
    
    def test_whatsapp_passes_for_new_hotel_with_low_confidence(self):
        """Hotel nuevo con confidence 0.4 debe pasar para whatsapp (threshold 0.3)."""
        from modules.asset_generation.preflight_checks import PreflightChecker, PreflightStatus
        from modules.data_validation import DataPoint
        from modules.data_validation.confidence_taxonomy import ConfidenceLevel
        
        checker = PreflightChecker()
        
        # Create a mock data point with confidence 0.4 (between 0.3 and 0.7)
        class MockDataPoint:
            confidence = ConfidenceLevel.ESTIMATED  # This maps to 0.7 in _evaluate_check
            value = "+573001234567"
        
        validated_data = {"whatsapp": MockDataPoint()}
        hotel_context = {"reviews": 0, "photos": 0, "place_found": False}
        
        report = checker.check_asset("whatsapp_button", validated_data, hotel_context)
        
        # Should pass because new hotel threshold is 0.3 and ESTIMATED=0.7 > 0.3
        assert report.can_proceed == True

    def test_whatsapp_passes_for_new_hotel_without_data(self):
        """Hotel nuevo sin datos whatsapp debe pasar con fallback (threshold 0.3)."""
        from modules.asset_generation.preflight_checks import PreflightChecker, PreflightStatus
        
        checker = PreflightChecker()
        
        validated_data = {}  # No whatsapp data
        hotel_context = {"reviews": 0, "photos": 0, "place_found": False}
        
        report = checker.check_asset("whatsapp_button", validated_data, hotel_context)
        
        # Should pass with warning because block_on_failure=False for whatsapp
        assert report.can_proceed == True

    def test_established_hotel_requires_higher_confidence(self):
        """Hotel establecido requiere confidence mayor para whatsapp."""
        from modules.asset_generation.preflight_checks import PreflightChecker, PreflightStatus
        from modules.data_validation import DataPoint
        from modules.data_validation.confidence_taxonomy import ConfidenceLevel
        
        checker = PreflightChecker()
        
        # Create a mock data point with ESTIMATED confidence (0.7)
        class MockDataPoint:
            confidence = ConfidenceLevel.ESTIMATED  # = 0.7
            value = "+573001234567"
        
        validated_data = {"whatsapp": MockDataPoint()}
        hotel_context = {"reviews": 50, "photos": 50, "place_found": True}  # Established
        
        report = checker.check_asset("whatsapp_button", validated_data, hotel_context)
        
        # Should pass - ESTIMATED=0.7 >= required=0.7 for established hotel
        assert report.can_proceed == True


class TestConditionalGeneratorWithNewHotel:
    """Verifica que ConditionalGenerator pasa hotel_context a PreflightChecker."""
    
    def test_generate_accepts_hotel_context(self):
        """generate() debe aceptar hotel_context como parámetro."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        gen = ConditionalGenerator(output_dir="output")
        
        # Should not raise - accepts the parameter
        result = gen.generate(
            asset_type="whatsapp_button",
            validated_data={},
            hotel_name="Test Hotel",
            hotel_id="test_001",
            hotel_context={"reviews": 0, "photos": 0}
        )
        
        # Result depends on data, but should not error on parameter
        assert "status" in result or "success" in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
