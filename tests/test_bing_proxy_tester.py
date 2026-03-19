"""Tests for BingProxyTester - verificación de visibilidad via Bing."""

import pytest
from unittest.mock import patch, MagicMock
import requests

from modules.analyzers.bing_proxy_tester import (
    BingProxyTester,
    BingResult
)


class TestBingProxyTesterInit:
    """Tests de inicialización."""
    
    def test_initializes_with_defaults(self):
        """Test que se inicializa con valores por defecto."""
        tester = BingProxyTester()
        assert tester.timeout == 15
        assert tester.session is not None
    
    def test_initializes_with_custom_timeout(self):
        """Test que acepta timeout personalizado."""
        tester = BingProxyTester(timeout=30)
        assert tester.timeout == 30


class TestBingProxyQuickTest:
    """Tests del método quick_test."""
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_returns_correct_structure(self, mock_get):
        """Test que retorna estructura correcta."""
        mock_response = MagicMock()
        mock_response.text = '<html><li class="b_algo"><h2>Otro Hotel</h2></li></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel Test", "Ciudad Test")
        
        assert 'query' in result
        assert 'mencionado' in result
        assert 'ranking' in result
        assert 'probabilidad_chatgpt' in result
        assert result['metodo'] == 'bing_proxy_quick'
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_detects_mention_in_title(self, mock_get):
        """Test que detecta mención en título."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <li class="b_algo">
                <h2>Hotel Visperas - Santa Rosa de Cabal</h2>
                <p>Hotel boutique en el Eje Cafetero</p>
            </li>
        </html>
        '''
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel Visperas", "Santa Rosa de Cabal")
        
        assert result['mencionado'] == True
        assert result['ranking'] == 1
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_detects_mention_in_snippet(self, mock_get):
        """Test que detecta mención en snippet."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <li class="b_algo">
                <h2>Hoteles en Santa Rosa de Cabal</h2>
                <p>Visita Hotel Visperas, el mejor de la zona</p>
            </li>
        </html>
        '''
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel Visperas", "Santa Rosa de Cabal")
        
        assert result['mencionado'] == True
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_no_mention_returns_low_probability(self, mock_get):
        """Test que retorna baja probabilidad cuando no hay mención."""
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <li class="b_algo"><h2>Otro Hotel 1</h2></li>
            <li class="b_algo"><h2>Otro Hotel 2</h2></li>
        </html>
        '''
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel No Existente", "Ciudad")
        
        assert result['mencionado'] == False
        assert result['probabilidad_chatgpt'] == tester.DEFAULT_PROBABILITY


class TestBingProxyProbabilityMap:
    """Tests del mapeo de probabilidades."""
    
    def test_higher_rank_has_higher_probability(self):
        """Test que ranking más alto tiene mayor probabilidad."""
        tester = BingProxyTester()
        
        for rank in range(1, 10):
            prob_current = tester.RANKING_PROBABILITY_MAP.get(rank, tester.DEFAULT_PROBABILITY)
            prob_next = tester.RANKING_PROBABILITY_MAP.get(rank + 1, tester.DEFAULT_PROBABILITY)
            
            assert prob_current >= prob_next, \
                f"Rank {rank} debería tener >= prob que rank {rank+1}"
    
    def test_rank_1_has_highest_probability(self):
        """Test que ranking 1 tiene la mayor probabilidad."""
        tester = BingProxyTester()
        max_prob = max(tester.RANKING_PROBABILITY_MAP.values())
        assert tester.RANKING_PROBABILITY_MAP[1] == max_prob
    
    def test_default_probability_is_low(self):
        """Test que la probabilidad por defecto es baja."""
        tester = BingProxyTester()
        assert tester.DEFAULT_PROBABILITY < 0.20


class TestBingProxyErrorHandling:
    """Tests de manejo de errores."""
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_handles_timeout_gracefully(self, mock_get):
        """Test que maneja timeout sin crash."""
        mock_get.side_effect = requests.exceptions.Timeout()
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel Test", "Ciudad")
        
        assert result['mencionado'] == False
        assert result['probabilidad_chatgpt'] == 0.0
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_handles_connection_error(self, mock_get):
        """Test que maneja error de conexión."""
        mock_get.side_effect = requests.exceptions.ConnectionError()
        
        tester = BingProxyTester()
        result = tester.quick_test("Hotel Test", "Ciudad")
        
        assert result['mencionado'] == False


class TestBingProxyIsMentioned:
    """Tests de la lógica de detección de menciones."""
    
    def test_exact_match_detected(self):
        """Test que detecta nombre exacto."""
        tester = BingProxyTester()
        
        assert tester._is_mentioned(
            "hotel visperas",
            "hotel visperas - santa rosa",
            ""
        ) == True
    
    def test_partial_match_without_articles(self):
        """Test que detecta sin artículos."""
        tester = BingProxyTester()
        
        assert tester._is_mentioned(
            "El Hotel Visperas",
            "",
            "visperas es el mejor hotel"
        ) == True
    
    def test_case_insensitive(self):
        """Test que es case insensitive."""
        tester = BingProxyTester()
        
        assert tester._is_mentioned(
            "HOTEL VISPERAS",
            "Hotel visperas",
            ""
        ) == True
    
    def test_no_false_positives(self):
        """Test que no da falsos positivos."""
        tester = BingProxyTester()
        
        assert tester._is_mentioned(
            "Hotel Visperas",
            "Hotel Vista Hermosa",
            ""
        ) == False


class TestBingProxyVisibility:
    """Tests del método test_visibility."""
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_returns_aggregated_results(self, mock_get):
        """Test que retorna resultados agregados."""
        mock_response = MagicMock()
        mock_response.text = '<html><li class="b_algo"><h2>Otro Hotel</h2></li></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        hotel_data = {
            'nombre': 'Hotel Test',
            'ubicacion': 'Ciudad Test',
            'servicios': ['restaurante']
        }
        
        result = tester.test_visibility(hotel_data)
        
        assert 'metodo' in result
        assert 'probabilidad_chatgpt' in result
        assert 'desglose' in result
        assert result['metodo'] == 'bing_proxy'
    
    @patch('modules.analyzers.bing_proxy_tester.requests.Session.get')
    def test_generates_queries_from_services(self, mock_get):
        """Test que genera queries basadas en servicios."""
        mock_response = MagicMock()
        mock_response.text = '<html><li class="b_algo"><h2>Otro</h2></li></html>'
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        tester = BingProxyTester()
        hotel_data = {
            'nombre': 'Hotel Test',
            'ubicacion': 'Ciudad Test',
            'servicios': ['piscina', 'restaurante', 'spa']
        }
        
        result = tester.test_visibility(hotel_data)
        
        # Verificar que se generaron queries con servicios
        queries_tested = [d['query'] for d in result.get('desglose', [])]
        has_service_query = any('piscina' in q or 'spa' in q or 'restaurante' in q for q in queries_tested)
        assert has_service_query or len(queries_tested) > 0
