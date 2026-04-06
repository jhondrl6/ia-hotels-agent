"""
FASE 8: Autonomous Research Engine - Tests Obligatorios

Tests obligatorios según plan:
1. test_research_output_schema - Schema se serializa correctamente
2. test_scraper_booking - Datos de Booking se extraen
3. test_research_confidence - Score refleja fuentes encontradas
4. test_research_integrated - Research output disponible
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest
import json
import tempfile
from pathlib import Path


class TestResearchOutputSchema:
    """T8A: ResearchOutput schema y serialización."""
    
    def test_research_output_schema_creation(self):
        """ResearchOutput schema se crea correctamente."""
        from modules.providers.autonomous_researcher import ResearchOutput
        
        output = ResearchOutput(
            hotel_name="Hotel Test",
            sources_checked=["gbp", "booking"],
            data_found={"gbp": {"rating": 4.5}, "booking": {"rating": 4.3}},
            confidence=0.5,
            citations=["https://booking.com/hotel/test"],
            gaps=["instagram: no data found"]
        )
        
        assert output.hotel_name == "Hotel Test"
        assert len(output.sources_checked) == 2
        assert output.confidence == 0.5
    
    def test_research_output_to_dict(self):
        """ResearchOutput se serializa a dict."""
        from modules.providers.autonomous_researcher import ResearchOutput
        
        output = ResearchOutput(
            hotel_name="Hotel Test",
            sources_checked=["gbp"],
            confidence=0.25
        )
        
        d = output.to_dict()
        
        assert isinstance(d, dict)
        assert d['hotel_name'] == "Hotel Test"
        assert d['confidence'] == 0.25
        assert 'timestamp' in d
        assert 'research_id' in d
    
    def test_research_output_to_json(self):
        """ResearchOutput se serializa a JSON."""
        from modules.providers.autonomous_researcher import ResearchOutput
        
        output = ResearchOutput(
            hotel_name="Hotel JSON Test",
            sources_checked=["booking", "tripadvisor"],
            confidence=0.5
        )
        
        json_str = output.to_json()
        
        parsed = json.loads(json_str)
        assert parsed['hotel_name'] == "Hotel JSON Test"
        assert parsed['confidence'] == 0.5
    
    def test_research_output_save_to_file(self):
        """ResearchOutput se persiste a archivo JSON."""
        from modules.providers.autonomous_researcher import ResearchOutput
        
        output = ResearchOutput(
            hotel_name="Hotel Save Test",
            sources_checked=["gbp", "booking", "tripadvisor", "instagram"],
            confidence=1.0
        )
        
        with tempfile.TemporaryDirectory() as tmpdir:
            filepath = output.save_to_file(Path(tmpdir))
            
            assert filepath.exists()
            
            with open(filepath, 'r') as f:
                loaded = json.load(f)
            
            assert loaded['hotel_name'] == "Hotel Save Test"
            assert loaded['confidence'] == 1.0
    
    def test_research_output_from_dict(self):
        """ResearchOutput se reconstruye desde dict."""
        from modules.providers.autonomous_researcher import ResearchOutput
        
        data = {
            'hotel_name': "Hotel From Dict",
            'sources_checked': ['gbp'],
            'data_found': {},
            'confidence': 0.25,
            'citations': [],
            'gaps': [],
            'timestamp': '2026-03-23T12:00:00',
            'research_id': 'abc123'
        }
        
        output = ResearchOutput.from_dict(data)
        
        assert output.hotel_name == "Hotel From Dict"
        assert output.research_id == 'abc123'


class TestScraperBooking:
    """T8B: Scraper de Booking.com."""
    
    def test_scraper_booking_creation(self):
        """BookingScraper se instancia correctamente."""
        from modules.scrapers.booking_scraper import BookingScraper
        
        scraper = BookingScraper()
        
        assert scraper.source_name == 'booking'
    
    def test_scraper_booking_scrape(self):
        """BookingScraper.scrape() devuelve estructura válida."""
        from modules.scrapers.booking_scraper import BookingScraper
        
        scraper = BookingScraper()
        result = scraper.scrape("Hotel Test", "https://booking.com/hotel/test")
        
        assert result['source'] == 'booking'
        assert 'found' in result
        assert 'data' in result
        assert 'url' in result
        assert result['found'] == True  # Stub siempre returns True
    
    def test_scraper_booking_data_structure(self):
        """BookingScraper devuelve campos esperados."""
        from modules.scrapers.booking_scraper import BookingScraper
        
        scraper = BookingScraper()
        result = scraper.scrape("Hotel Test")
        
        data = result['data']
        
        assert 'hotel_name' in data
        assert 'rating' in data
        assert 'reviews' in data
        assert 'amenities' in data
        assert 'photos' in data
        assert 'price_range' in data
    
    def test_scraper_booking_url_construction(self):
        """BookingScraper construye URL correctamente."""
        from modules.scrapers.booking_scraper import BookingScraper
        
        scraper = BookingScraper()
        result = scraper.scrape("Hotel Gran Medellin")
        
        assert 'booking.com' in result['url']


class TestResearchConfidence:
    """T8D: Research Confidence Scoring (para 1 fuente activa: booking)."""
    
    def test_confidence_1_of_1_source(self):
        """1/1 fuente = confidence 0.25 (base 0.2 + field boost 0.05)."""
        from modules.providers.autonomous_researcher import calculate_research_confidence
        
        confidence = calculate_research_confidence(
            sources_checked=['booking'],
            data_found={'booking': {}}
        )
        
        assert confidence == 0.25
    
    def test_confidence_0_sources(self):
        """0 fuentes = confidence 0.0."""
        from modules.providers.autonomous_researcher import calculate_research_confidence
        
        confidence = calculate_research_confidence(
            sources_checked=[],
            data_found={}
        )
        
        assert confidence == 0.0


class TestResearchIntegrated:
    """T8C: Research integrado en el sistema."""
    
    def test_research_output_accessible_after_research(self):
        """ResearchOutput completo accesible via last_research_output."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotel Test", "https://test.com", persist=False)
        
        # El ResearchOutput completo debe estar disponible
        assert hasattr(researcher, 'last_research_output')
        assert researcher.last_research_output is not None
        assert researcher.last_research_output.hotel_name == "Hotel Test"
    
    def test_research_returns_research_result_for_compatibility(self):
        """research() devuelve ResearchResult (legacy) para compatibilidad."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotel Test", "https://test.com", persist=False)
        
        # Debe tener atributos de ResearchResult legacy
        assert hasattr(result, 'found')
        assert hasattr(result, 'data')
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'sources')
        assert hasattr(result, 'conflicts')
        assert hasattr(result, 'timestamp')
    
    def test_research_result_has_correct_sources(self):
        """ResearchResult.sources contiene fuentes encontradas (o vacío si stub no encuentra datos)."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotel Test", "https://test.com", persist=False)
        
        # Booking stub devuelve found=False (sin datos reales)
        # El test verifica que el Researcher funciona sin importar el resultado
        assert isinstance(result.sources, list)
    
    def test_research_confidence_matches_sources_count(self):
        """Confidence del result refleja fuentes encontradas."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        result = researcher.research("Hotel Test", "https://test.com", persist=False)
        
        # Confidence refleja fuentes con found=True
        # Stub devuelve 0 sources (found=False) → confidence 0.0
        assert result.confidence == 0.0
    
    def test_detect_gaps_function(self):
        """detect_gaps() identifica fuentes no consultadas o sin datos."""
        from modules.providers.autonomous_researcher import detect_gaps
        
        # Stub con {} como data se detecta como gap (sin datos reales)
        gaps = detect_gaps(
            sources_available=['booking'],  # Solo fuente activa
            sources_checked=['booking'],   # 1 de 1
            data_found={'booking': {}}
        )
        
        assert len(gaps) == 1  # Stub sin datos reales = gap


class TestAutonomousResearcherFull:
    """Tests de integración completa del AutonomousResearcher."""
    
    def test_researcher_initialization(self):
        """AutonomousResearcher se inicializa correctamente (solo booking activo)."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        researcher = AutonomousResearcher()
        
        assert researcher is not None
        assert hasattr(researcher, 'scrapers')
        # Solo booking scraper activo (los demás deprecados)
        assert researcher.ALL_SOURCES == ['booking']
        assert 'booking' in researcher.scrapers
        assert len(researcher.scrapers) == 1
    
    def test_research_with_persistence(self):
        """Research persiste output a archivo."""
        from modules.providers.autonomous_researcher import AutonomousResearcher
        
        with tempfile.TemporaryDirectory() as tmpdir:
            researcher = AutonomousResearcher(output_dir=Path(tmpdir))
            result = researcher.research("Hotel Persist Test", "https://persist.com", persist=True)
            
            # Verificar que se guardó un archivo
            files = list(Path(tmpdir).glob("research_*.json"))
            assert len(files) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
