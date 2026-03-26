"""
Mock client para Semrush API.

Semrush (https://www.semrush.com/) proporciona métricas de SEO y visibilidad
que pueden complementar datos de AEO.

NOTE: Este es un STUB/MOCK. La integración real requiere:
  - Cuenta activa de Semrush API
  - API key válida (env: SEMRUSH_API_KEY)
  - Plan de suscripción con acceso a API

Para integración real, implementar:
  POST /v2/reports
  GET /v1/domain_analytics/organic_research/{domain}
"""
import os
from typing import Optional


class SemrushClient:
    """
    Client mock para Semrush API.
    
    En producción real, este client se conectaría a la API de Semrush
    para obtener métricas de visibilidad y competencia.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Inicializa el client.
        
        Args:
            api_key: API key de Semrush. Si es None, usa SEMRUSH_API_KEY del env.
        """
        self.api_key = api_key or os.getenv("SEMRUSH_API_KEY")
        self.base_url = "https://api.semrush.com"
        self._is_mock = self.api_key is None

    @property
    def is_mock(self) -> bool:
        """Retorna True si está usando modo mock (sin API key)."""
        return self._is_mock

    def get_domain_organic(self, domain: str) -> dict:
        """
        Obtiene métricas de tráfico orgánico para un dominio.
        
        Args:
            domain: Dominio del hotel (e.g., 'hotelvisperas.com')
            
        Returns:
            dict con structure:
                {
                    "domain": str,
                    "organic_traffic": int,
                    "organic_keywords": int,
                    "data_source": "semrush_api" o "mock"
                }
        """
        if self._is_mock:
            return {
                "domain": domain,
                "organic_traffic": None,
                "organic_keywords": None,
                "data_source": "mock",
                "note": "Configure SEMRUSH_API_KEY for real data"
            }
        
        # TODO: Implementar llamada real a API de Semrush
        # POST /v2/reports con type="domain_organic"
        raise NotImplementedError("Real API integration pending")

    def get_competitor_analysis(self, domain: str) -> dict:
        """
        Obtiene análisis de competidores orgánicos.
        
        Args:
            domain: Dominio principal
            
        Returns:
            dict con structure:
                {
                    "domain": str,
                    "competitors": [{"domain": str, "overlap": float}],
                    "data_source": "semrush_api" o "mock"
                }
        """
        if self._is_mock:
            return {
                "domain": domain,
                "competitors": [],
                "data_source": "mock",
                "note": "Configure SEMRUSH_API_KEY for real data"
            }
        
        # TODO: Implementar llamada real a API de Semrush
        raise NotImplementedError("Real API integration pending")

    def get_keyword_difficulty(self, keywords: list[str]) -> dict:
        """
        Obtiene dificultad de palabras clave.
        
        Args:
            keywords: Lista de keywords a analizar
            
        Returns:
            dict con structure:
                {
                    "keywords": [{"keyword": str, "difficulty": float}],
                    "data_source": "semrush_api" o "mock"
                }
        """
        if self._is_mock:
            return {
                "keywords": [{"keyword": k, "difficulty": None} for k in keywords],
                "data_source": "mock",
                "note": "Configure SEMRUSH_API_KEY for real data"
            }
        
        # TODO: Implementar llamada real a API de Semrush
        raise NotImplementedError("Real API integration pending")
