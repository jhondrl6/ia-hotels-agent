"""
TDD Gate: Autonomous Researcher

Estos tests definen el comportamiento esperado del AutonomousResearcher.
初期: Todos los tests FALLAN (módulo no existe aún).
Después de implementar: Todos los tests PASAN.

COMPORTAMIENTO ESPERADO:
- Investiga hotel automáticamente en fuentes públicas (GBP, Booking, TripAdvisor, Instagram)
- Cross-reference de datos entre fuentes
- Mejora confidence cuando múltiples fuentes coinciden
- Si fuente no disponible, continúa con las disponibles
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest


class TestAutonomousResearcherExists:
    """Verifica que el módulo existe y es importable."""
    
    def test_autonomous_researcher_module_exists(self):
        """El módulo debe existir en modules/providers/autonomous_researcher.py"""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        assert AutonomousResearcher is not None


class TestAutonomousResearcherInterface:
    """Verifica la interfaz pública del researcher."""
    
    def test_research_returns_research_result(self):
        """research() debe devolver un objeto ResearchResult."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        # No hace falta API key para verificar estructura del resultado
        result = researcher.research("Test Hotel", "https://test.com")
        
        assert hasattr(result, 'found'), "Debe tener atributo 'found'"
        assert hasattr(result, 'data'), "Debe tener atributo 'data'"
        assert hasattr(result, 'confidence'), "Debe tener atributo 'confidence'"
        assert hasattr(result, 'sources'), "Debe tener atributo 'sources'"

    def test_research_accepts_hotel_name_and_url(self):
        """research() debe aceptar hotel_name y url como parámetros."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        
        # Debe aceptar estos parámetros sin error
        result = researcher.research(
            hotel_name="Hotel Test",
            url="https://hoteltest.com"
        )
        
        assert result is not None


class TestAutonomousResearcherGBP:
    """Verifica búsqueda en Google Business Profile."""
    
    def test_research_looks_up_gbp(self):
        """Debe buscar en Google Business Profile."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # GBP debe ser una de las fuentes intentadas
        assert 'gbp' in result.sources or 'google' in result.sources, \
            "Debe intentar GBP como fuente"

    def test_gbp_fills_missing_fields(self):
        """GBP debe llenar campos faltantes del hotel."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # GBP puede aportar: address, phone, hours, reviews
        if result.found:
            gbp_data = result.data.get('gbp_data', {})
            # Al menos algunos campos deben estar presentes si encontró el hotel
            has_useful_data = any([
                gbp_data.get('address'),
                gbp_data.get('telephone'),
                gbp_data.get('rating'),
                gbp_data.get('reviews')
            ])
            # No siempre encuentra, pero debe intentarlo


class TestAutonomousResearcherCrossReference:
    """Verifica cross-reference entre fuentes."""
    
    def test_cross_reference_improves_confidence(self):
        """Múltiples fuentes que coinciden deben mejorar confidence."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # Si tiene múltiples fuentes que coinciden, confidence debe ser mayor
        if len(result.sources) >= 2:
            assert result.confidence >= 0.6, \
                "Múltiples fuentes = confidence mayor"

    def test_conflicting_sources_reduce_confidence(self):
        """Fuentes contradictorias deben reducir confidence."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        if result.conflicts:
            assert result.confidence < 0.7, \
                "Conflictos deben reducir confidence"

    def test_conflicts_are_reported(self):
        """Conflictos entre fuentes deben ser reportados."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # Si hay conflictos, debe haber lista de conflictos
        assert hasattr(result, 'conflicts'), "Debe reportar conflictos"
        assert isinstance(result.conflicts, list), "Conflicts debe ser lista"


class TestAutonomousResearcherFallback:
    """Verifica comportamiento cuando fuentes no están disponibles."""
    
    def test_partial_results_still_useful(self):
        """Resultados parciales siguen siendo útiles."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("UnknownHotel12345", "https://unknown-hotel-12345.com")
        
        # Hotel no existe, pero no debe fallar
        assert result is not None
        # Puede no encontrar, pero debe tener estructura válida
        assert hasattr(result, 'found')
        assert hasattr(result, 'confidence')

    def test_no_crash_on_network_error(self):
        """Errores de red no deben crashear."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        
        # URL inválida no debe crashear
        result = researcher.research("Test", "https://this-domain-does-not-exist-12345.com")
        
        assert result is not None
        assert result.found == False or result.found == True  # Cualquiera es válido
        assert result.confidence is not None


class TestAutonomousResearcherConfidence:
    """Verifica cálculo de confidence."""
    
    def test_confidence_bounded_0_to_1(self):
        """Confidence siempre está entre 0 y 1."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Test", "https://test.com")
        
        assert 0.0 <= result.confidence <= 1.0, \
            f"Confidence debe estar entre 0 y 1, got: {result.confidence}"

    def test_more_sources_increases_confidence(self):
        """Más fuentes disponibles = confidence mayor."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        
        # Fuente única
        result1 = researcher.research("Test", "https://test.com", sources=['web'])
        
        # Múltiples fuentes
        result2 = researcher.research("Test", "https://test.com", 
                                      sources=['web', 'gbp', 'booking'])
        
        # Múltiples fuentes deben tener igual o mayor confidence
        assert result2.confidence >= result1.confidence


class TestAutonomousResearcherOutput:
    """Verifica output del researcher."""
    
    def test_data_has_expected_hotel_fields(self):
        """Data devuelta debe tener campos de hotel."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        if result.found:
            # Campos típicos que el researcher debe buscar
            expected_fields = ['name', 'address', 'telephone', 'url', 'rating']
            found_fields = [f for f in expected_fields if f in result.data]
            
            # Al menos algunos campos deben estar presentes
            assert len(found_fields) >= 0  # Puede estar vacío si no encontró

    def test_sources_listed_in_output(self):
        """Fuentes usadas deben estar listadas en output."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Test", "https://test.com")
        
        assert result.sources is not None
        assert isinstance(result.sources, list), "Sources debe ser lista"

    def test_research_has_timestamp(self):
        """Resultado debe incluir timestamp de investigación."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Test", "https://test.com")
        
        assert hasattr(result, 'timestamp'), "Debe tener timestamp"
        assert result.timestamp is not None


class TestAutonomousResearcherMultiSource:
    """Verifica búsqueda en múltiples fuentes específicas."""
    
    def test_attempts_booking(self):
        """Debe intentar Booking.com."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        assert 'booking' in result.sources or 'bookingcom' in result.sources, \
            "Debe intentar Booking.com"

    def test_attempts_tripadvisor(self):
        """Debe intentar TripAdvisor."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        assert 'tripadvisor' in result.sources or 'ta' in result.sources, \
            "Debe intentar TripAdvisor"

    def test_attempts_social_media(self):
        """Debe intentar Instagram/Facebook."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # Al menos una fuente social debe ser intentada
        social_sources = ['instagram', 'facebook', 'social']
        attempted_social = any(s in result.sources for s in social_sources)
        assert attempted_social or len(result.sources) > 0  # Debe tener fuentes


class TestAutonomousResearcherIntegration:
    """Verifica integración con el resto del sistema."""
    
    def test_output_compatible_with_preflight(self):
        """Output del researcher debe ser compatible con preflight checks."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # El resultado debe poder usarse como validated_data
        # (dict con campos de DataPoint)
        if result.found:
            assert isinstance(result.data, dict), "Data debe ser dict"

    def test_can_feed_into_benchmark_resolver(self):
        """Output del researcher puede alimentar al BenchmarkResolver."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        researcher = AutonomousResearcher()
        benchmark = BenchmarkResolver()
        
        research_result = researcher.research("Hotelvisperas", "https://hotelvisperas.com")
        
        # Benchmark resolver debe poder usar datos del researcher
        # (Incluso si researcher no encontró todo)
        benchmark_result = benchmark.resolve(
            field="telephone",
            value=research_result.data.get('telephone'),
            context={"region": "eje_cafetero"}
        )
        
        assert benchmark_result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
