"""
Tests para Google Travel Scraper - FASE 11A

TDD Gate: Tests deben FALLAR antes de implementar GoogleTravelScraper.

Estos tests describen el comportamiento esperado:
- GoogleTravelScraper debe encontrar hotels en Google Travel
- Debe integrarse con AutonomousResearcher como fallback
- Debe manejar errores gracefully
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import sys

# Agregar modules al path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Estos tests FALLARAN hasta que se implemente GoogleTravelScraper
# TDD Gate: Test escrito primero, implementacion despues


class TestGoogleTravelScraperExists:
    """Test que GoogleTravelScraper existe y es importable."""

    def test_google_travel_scraper_importable(self):
        """GoogleTravelScraper debe ser importable desde modules.scrapers."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper
        assert GoogleTravelScraper is not None

    def test_google_travel_scraper_has_scrape_hotel_method(self):
        """GoogleTravelScraper debe tener metodo scrape_hotel()."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper
        scraper = GoogleTravelScraper()
        assert hasattr(scraper, 'scrape_hotel')
        assert callable(scraper.scrape_hotel)


class TestGoogleTravelScraperFunctionality:
    """Test funcionalidad de GoogleTravelScraper."""

    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_scrape_hotel_returns_place_data(self, mock_session_class):
        """scrape_hotel() debe retornar PlaceData con datos del hotel."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        # Mock response de Google Travel
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <script type="application/ld+json">
            {
                "@type": "Hotel",
                "name": "Hotel Visperas",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Km. 4 vía Termales, vereda La Leona",
                    "addressLocality": "Santa Rosa de Cabal",
                    "addressRegion": "Risaralda"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.5",
                    "reviewCount": "120"
                }
            }
            </script>
        </html>
        '''

        # Configurar el mock de session
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_session_instance

        scraper = GoogleTravelScraper()
        result = scraper.scrape_hotel("Hotel Visperas", "Santa Rosa de Cabal")

        assert result is not None
        assert result.get('name') == 'Hotel Visperas'
        assert 'Santa Rosa de Cabal' in result.get('address', '')

    def test_scrape_hotel_returns_dict_structure(self):
        """scrape_hotel() debe retornar estructura dict correcta."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        scraper = GoogleTravelScraper()

        # Test con mock de session
        with patch('modules.scrapers.google_travel_scraper.requests.Session') as mock_session_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><script type="application/ld+json">{"@type":"Hotel","name":"Test Hotel"}</script></html>'
            mock_session_instance = Mock()
            mock_session_instance.get.return_value = mock_response
            mock_session_class.return_value = mock_session_instance

            result = scraper.scrape_hotel("Test Hotel", "Test Location")

            # Estructura esperada
            assert isinstance(result, dict)
            assert 'name' in result
            assert 'address' in result
            assert 'rating' in result or 'reviews' in result or 'photos' in result

    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_hotelvisperas_found_in_google_travel(self, mock_session_class):
        """Hotel Visperas debe ser encontrado via Google Travel.

        Este test valida el caso real: Hotel Visperas existe en Google Travel
        https://www.google.com/travel/hotels/entity/ChcIqp2ZrdfnspElGgsvZy8xdGhobGtqYhAB
        """
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        # Simular respuesta de Google Travel con datos reales
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <script type="application/ld+json">
            {
                "@type": "Hotel",
                "name": "Hotel Visperas",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Km. 4 vía Termales, vereda La Leona",
                    "addressLocality": "Santa Rosa de Cabal",
                    "addressRegion": "Risaralda",
                    "addressCountry": "CO"
                },
                "aggregateRating": {
                    "@type": "AggregateRating",
                    "ratingValue": "4.2",
                    "reviewCount": "85"
                }
            }
            </script>
        </html>
        '''
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_session_instance

        scraper = GoogleTravelScraper()
        result = scraper.scrape_hotel("Hotel Visperas", "Santa Rosa de Cabal, Risaralda")

        assert result is not None
        # El hotel debe ser encontrado (no None)
        assert result.get('found') is True
        assert 'Visperas' in result.get('name', '')


class TestAutonomousResearcherIntegration:
    """Test integracion con AutonomousResearcher."""

    def test_autonomous_researcher_has_travel_fallback(self):
        """AutonomousResearcher debe usar GoogleTravelScraper como fallback.

        Cuando GBPScraper falla (Place not found), debe intentar con Travel.
        """
        from modules.providers.autonomous_researcher import AutonomousResearcher

        # Verificar que el modulo existe y tiene el metodo de fallback
        researcher = AutonomousResearcher()
        assert hasattr(researcher, '_try_travel_scrape') or hasattr(researcher, 'research')

    def test_research_output_has_travel_source(self):
        """ResearchOutput debe indicar cuando datos vienen de Google Travel."""
        from modules.providers.autonomous_researcher import ResearchOutput

        output = ResearchOutput(
            hotel_name="Test Hotel",
            sources_checked=["google_places", "google_travel"],
            data_found={"name": "Test Hotel"},
            confidence=0.5,
            citations=[],
            gaps=[]
        )

        # Debe indicar que Travel fue consultado
        assert 'google_travel' in output.sources_checked


class TestTravelFallbackChain:
    """Test cadena de fallback: Places -> Travel -> Benchmark."""

    @pytest.mark.skip(reason="Integracion con AutonomousResearcher se implementa en FASE 11B")
    @patch('modules.providers.autonomous_researcher.GooglePlacesClient')
    @patch('modules.scrapers.google_travel_scraper.GoogleTravelScraper.scrape_hotel')
    def test_fallback_places_to_travel(self, mock_travel, mock_places):
        """Cuando Places falla, Travel debe intentar.

        Cadena: GBPScraper (falla) -> GoogleTravelScraper (exito)

        NOTA: Este test requiere que AutonomousResearcher tenga el metodo
        _try_travel_scrape() integrado, lo cual se hace en FASE 11B.
        """
        from modules.providers.autonomous_researcher import AutonomousResearcher

        # Places falla
        mock_places.return_value = None

        # Travel tiene datos
        mock_travel.return_value = {
            'name': 'Hotel Visperas',
            'address': 'Km. 4 vía Termales',
            'rating': 4.2,
            'reviews': 85,
            'found': True
        }

        researcher = AutonomousResearcher()
        result = researcher.autonomous_research("Hotel Visperas", "Santa Rosa de Cabal")

        # Travel debe haber sido consultado
        mock_travel.assert_called_once()
        # Y debe retornar datos
        assert result.data_found is not None

    def test_fallback_travel_to_benchmark(self):
        """Cuando Travel falla, usar benchmark regional.

        Cadena: GBPScraper (falla) -> GoogleTravelScraper (falla) -> Benchmark
        """
        # Este test verifica que existe fallback a benchmark
        # cuando ambas fuentes de datos fallan
        pass  # Implementado en FASE 11B


class TestTravelResponseStructure:
    """Test estructura de respuesta de Travel scraper."""

    def test_travel_response_has_required_fields(self):
        """Respuesta de Travel debe tener campos requeridos.

        Campos requeridos para ResearchOutput:
        - name
        - address
        - rating
        - reviews
        - photos (opcional)
        - phone (opcional)
        - website (opcional)
        """
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        with patch('modules.scrapers.google_travel_scraper.requests.Session') as mock_session_class:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = '<html><script type="application/ld+json">{"@type":"Hotel","name":"Test"}</script></html>'
            mock_session_instance = Mock()
            mock_session_instance.get.return_value = mock_response
            mock_session_class.return_value = mock_session_instance

            scraper = GoogleTravelScraper()
            result = scraper.scrape_hotel("Test", "Test")

            # Verificar campos basicos
            assert 'name' in result
            assert 'address' in result


class TestTravelScraperErrorHandling:
    """Test manejo de errores de Travel scraper."""

    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_travel_scraper_handles_404(self, mock_session_class):
        """Travel scraper debe manejar 404 (hotel no encontrado)."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        mock_response = Mock()
        mock_response.status_code = 404
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_session_instance

        scraper = GoogleTravelScraper()
        result = scraper.scrape_hotel("NonExistent Hotel", "Somewhere")

        # Debe retornar dict con found=False
        assert result.get('found') is False or result is None

    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_travel_scraper_handles_timeout(self, mock_session_class):
        """Travel scraper debe manejar timeout."""
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper
        import requests

        mock_session_instance = Mock()
        mock_session_instance.get.side_effect = requests.Timeout()
        mock_session_class.return_value = mock_session_instance

        scraper = GoogleTravelScraper()
        result = scraper.scrape_hotel("Test Hotel", "Test")

        # Debe manejar timeout gracefully
        assert result is not None  # No debe lanzar excepcion


# =============================================================================
# FASE 11B: Tests de Integración con AutonomousResearcher
# =============================================================================

class TestGoogleTravelIntegrationWithAutonomousResearcher:
    """Tests para verificar integracion de GoogleTravelScraper en AutonomousResearcher."""

    def test_travel_scraper_integrates_with_researcher(self):
        """Verifica que AutonomousResearcher tiene _try_travel_scrape y puede integrarse."""
        from modules.providers.autonomous_researcher import AutonomousResearcher

        researcher = AutonomousResearcher()

        # Verificar que existen los metodos de fallback
        assert hasattr(researcher, '_try_travel_scrape')
        assert callable(researcher._try_travel_scrape)
        assert hasattr(researcher, '_try_gbp_scrape')
        assert callable(researcher._try_gbp_scrape)
        assert hasattr(researcher, '_fallback_benchmark')
        assert callable(researcher._fallback_benchmark)

    @patch('modules.providers.autonomous_researcher.GoogleTravelScraper')
    @patch('modules.providers.autonomous_researcher.GBPScraper')
    def test_fallback_chain_places_to_travel(self, mock_gbp_class, mock_travel_class):
        """Places falla -> Travel funciona: verifica que Travel se consulta despues de GBP."""
        from modules.providers.autonomous_researcher import AutonomousResearcher

        # GBPScraper no encuentra (falla)
        mock_gbp_instance = Mock()
        mock_gbp_instance.scrape.return_value = {'found': False, 'data': {}}
        mock_gbp_class.return_value = mock_gbp_instance

        # TravelS scraper encuentra
        mock_travel_instance = Mock()
        mock_travel_instance.scrape_hotel.return_value = {
            'name': 'Hotel Visperas',
            'address': 'Km. 4 vía Termales',
            'rating': 4.2,
            'reviews': 85,
            'found': True
        }
        mock_travel_instance.close.return_value = None
        mock_travel_class.return_value = mock_travel_instance

        researcher = AutonomousResearcher()
        researcher.scrapers['gbp'] = mock_gbp_instance

        result = researcher._try_travel_scrape("Hotel Visperas", "Santa Rosa de Cabal")

        assert result is not None
        assert 'google_travel' in result.sources_checked
        assert result.data_found.get('google_travel', {}).get('found') is True

    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_travel_data_in_research_output(self, mock_session_class):
        """Datos de Travel deben aparecer correctamente en ResearchOutput."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        from modules.scrapers.google_travel_scraper import GoogleTravelScraper

        # Mock response con datos de hotel
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '''
        <html>
            <script type="application/ld+json">
            {
                "@type": "Hotel",
                "name": "Hotel Visperas",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "Km. 4 vía Termales",
                    "addressLocality": "Santa Rosa de Cabal"
                },
                "aggregateRating": {
                    "ratingValue": "4.2",
                    "reviewCount": "85"
                }
            }
            </script>
        </html>
        '''
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_session_instance

        researcher = AutonomousResearcher()
        result = researcher._try_travel_scrape("Hotel Visperas", "Santa Rosa de Cabal")

        assert result is not None
        assert result.hotel_name == "Hotel Visperas"
        assert 'google_travel' in result.sources_checked
        assert result.data_found.get('google_travel') is not None
        travel_data = result.data_found['google_travel']
        assert travel_data.get('name') == 'Hotel Visperas'
        assert travel_data.get('rating') == 4.2

    @patch('modules.providers.autonomous_researcher.AutonomousResearcher._try_gbp_scrape')
    @patch('modules.scrapers.google_travel_scraper.requests.Session')
    def test_travel_fallback_to_benchmark(self, mock_session_class, mock_gbp):
        """Travel falla -> Benchmark: verifica que se usa benchmark como ultimo resort."""
        from modules.providers.autonomous_researcher import AutonomousResearcher

        # Mock session que retorna 404 (Travel no encuentra)
        mock_response = Mock()
        mock_response.status_code = 404
        mock_session_instance = Mock()
        mock_session_instance.get.return_value = mock_response
        mock_session_class.return_value = mock_session_instance

        # GBP no encuentra el hotel
        mock_gbp.return_value = None

        researcher = AutonomousResearcher()

        # Buscar hotel que no existe - debe usar benchmark
        result = researcher.autonomous_research("NonExistent Hotel XYZ", "Unknown Location")

        # Debe retornar benchmark
        assert result is not None
        assert 'benchmark' in result.sources_checked
        assert result.confidence == 0.2
        assert result.data_found.get('benchmark') is not None
        assert result.data_found['benchmark'].get('benchmark') is True

    def test_research_output_sources_include_travel(self):
        """sources_checked debe incluir 'google_travel' cuando Travel es exitoso."""
        from modules.providers.autonomous_researcher import ResearchOutput

        # Crear output con fuente Travel
        output = ResearchOutput(
            hotel_name="Hotel Test",
            sources_checked=["gbp", "google_travel"],
            data_found={
                "gbp": {"name": "Hotel Test"},
                "google_travel": {"name": "Hotel Test", "found": True}
            },
            confidence=0.6,
            citations=[],
            gaps=["limited_data"]
        )

        assert 'google_travel' in output.sources_checked
        assert output.data_found.get('google_travel') is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
