import pytest
import uuid
from modules.scrapers.scraper_fallback import ScraperFallback


def _unique_url():
    return f'https://test-{uuid.uuid4().hex[:8]}.com'


class TestScraperFallbackConfirmedData:
    
    def setup_method(self):
        self.fallback = ScraperFallback()
    
    def test_confirmed_data_has_priority_over_estimation(self):
        confirmed = {
            'datos_operativos': {
                'habitaciones': 25,
                'valor_reserva_cop': 450000,
                'canal_directo_pct': 35
            }
        }
        
        result = self.fallback.enrich_data(
            partial_data={'nombre': 'Hotel Test'},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert result['habitaciones'] == 25
        assert result['precio_promedio'] == 450000
        assert result['canal_directo'] == 35
        assert 'habitaciones' in result.get('campos_confirmados', [])
        assert 'precio_promedio' in result.get('campos_confirmados', [])
        assert 'habitaciones' not in result.get('campos_estimados', [])
    
    def test_confirmed_data_not_overwritten_by_benchmark(self):
        confirmed = {
            'habitaciones': 8
        }
        
        result = self.fallback.enrich_data(
            partial_data={'ubicacion': 'Medellin, Antioquia'},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert result['habitaciones'] == 8
        assert 'habitaciones' in result.get('campos_confirmados', [])
        assert 'habitaciones' not in result.get('campos_estimados', [])
        assert 'benchmark_regional_habitaciones' not in result.get('fallback_chain', [])
    
    def test_field_mapping_valor_reserva_to_precio_promedio(self):
        confirmed = {
            'datos_operativos': {
                'valor_reserva_cop': 350000
            }
        }
        
        result = self.fallback.enrich_data(
            partial_data={},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert result['precio_promedio'] == 350000
        assert 'precio_promedio' in result.get('campos_confirmados', [])
    
    def test_field_mapping_canal_directo_pct(self):
        confirmed = {
            'datos_operativos': {
                'canal_directo_pct': 42
            }
        }
        
        result = self.fallback.enrich_data(
            partial_data={},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert result['canal_directo'] == 42
        assert 'canal_directo' in result.get('campos_confirmados', [])
    
    def test_data_sources_metadata(self):
        confirmed = {
            'habitaciones': 15
        }
        
        result = self.fallback.enrich_data(
            partial_data={},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert 'data_sources' in result
        assert 'habitaciones' in result['data_sources']
        assert result['data_sources']['habitaciones']['source'] == 'onboarding_confirmed'
        assert result['data_sources']['habitaciones']['confidence'] == 1.0
    
    def test_metodo_obtencion_includes_onboarding(self):
        confirmed = {
            'habitaciones': 10
        }
        
        result = self.fallback.enrich_data(
            partial_data={},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert 'onboarding' in result['metodo_obtencion']
    
    def test_backward_compatibility_without_confirmed_data(self):
        result = self.fallback.enrich_data(
            partial_data={'nombre': 'Hotel Test'},
            url=_unique_url()
        )
        
        assert result is not None
        assert result['nombre'] == 'Hotel Test'
        assert 'habitaciones' in result
        assert 'precio_promedio' in result
    
    def test_none_confirmed_values_ignored(self):
        confirmed = {
            'habitaciones': None,
            'valor_reserva_cop': None
        }
        
        result = self.fallback.enrich_data(
            partial_data={'ubicacion': 'Cartagena'},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert 'habitaciones' not in result.get('campos_confirmados', [])
    
    def test_is_field_confirmed_helper(self):
        data = {
            'campos_confirmados': ['habitaciones', 'precio_promedio']
        }
        
        assert self.fallback.is_field_confirmed(data, 'habitaciones') is True
        assert self.fallback.is_field_confirmed(data, 'precio_promedio') is True
        assert self.fallback.is_field_confirmed(data, 'ocupacion') is False
    
    def test_is_field_confirmed_empty_data(self):
        assert self.fallback.is_field_confirmed({}, 'habitaciones') is False
        assert self.fallback.is_field_confirmed({'campos_confirmados': []}, 'habitaciones') is False
    
    def test_partial_confirmed_data_allows_other_estimations(self):
        confirmed = {
            'habitaciones': 20
        }
        
        result = self.fallback.enrich_data(
            partial_data={'ubicacion': 'Santa Marta'},
            url=_unique_url(),
            confirmed_data=confirmed
        )
        
        assert result['habitaciones'] == 20
        assert 'habitaciones' in result.get('campos_confirmados', [])
        
        if result.get('precio_promedio'):
            assert 'precio_promedio' in result.get('campos_estimados', []) or 'precio_promedio' in result.get('campos_confirmados', [])


class TestScraperFallbackIntegration:
    
    def setup_method(self):
        self.fallback = ScraperFallback()
    
    def test_full_enrichment_flow_with_confirmed_data(self):
        confirmed = {
            'datos_operativos': {
                'habitaciones': 12,
                'valor_reserva_cop': 300000,
                'canal_directo_pct': 40
            }
        }
        
        partial = {
            'nombre': 'Hotel Visperas',
            'ubicacion': 'Santa Rosa de Cabal, Risaralda'
        }
        
        result = self.fallback.enrich_data(
            partial_data=partial,
            url='https://hotelvisperas-unique-12345.com',
            confirmed_data=confirmed
        )
        
        assert result['nombre'] == 'Hotel Visperas'
        assert result['habitaciones'] == 12
        assert result['precio_promedio'] == 300000
        assert result['canal_directo'] == 40
        assert len(result.get('campos_confirmados', [])) == 3
        assert result['confidence'] == 'alta'
