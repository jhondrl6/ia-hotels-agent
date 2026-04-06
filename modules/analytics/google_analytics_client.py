"""
Google Analytics Client para medir tráfico indirecto.

MÉTODO #5 de KB [SECTION:IA_VISIBILITY_MEASUREMENT]:
Tráfico indirecto post-consulta IA (Google Analytics).

FASE: GAP-IAO-01-05
Estado: IMPLEMENTADO (requiere GA4_PROPERTY_ID y GA4_CREDENTIALS_PATH)
"""

import os
from typing import Dict, Any, List, Optional
from datetime import datetime


class GoogleAnalyticsClient:
    """
    Client para GA4 Data API.
    
    Requiere:
    - GA4_PROPERTY_ID: ID de propiedad GA4 (ej: "123456789")
    - GA4_CREDENTIALS_PATH: Ruta al archivo JSON de service account
    
    Instalación: pip install google-analytics-data
    """
    
    def __init__(self, property_id: str = None, credentials_path: str = None):
        self.property_id = property_id or os.getenv("GA4_PROPERTY_ID")
        self.credentials_path = credentials_path or os.getenv("GA4_CREDENTIALS_PATH")
        self._client = None
        self._initialized = False
        self._init_error = None
    
    def _initialize(self) -> bool:
        """Inicializa el cliente de GA4 Data API."""
        if self._initialized:
            return self._client is not None
        
        self._initialized = True
        
        if not self.property_id:
            self._init_error = "GA4_PROPERTY_ID no configurado"
            return False
        
        if not self.credentials_path:
            self._init_error = "GA4_CREDENTIALS_PATH no configurado"
            return False
        
        if not os.path.exists(self.credentials_path):
            self._init_error = f"Archivo de credenciales no encontrado: {self.credentials_path}"
            return False
        
        try:
            from google.analytics.data import BetaAnalyticsDataClient
            from google.oauth2 import service_account
            
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/analytics.readonly"]
            )
            
            self._client = BetaAnalyticsDataClient(credentials=credentials)
            return True
            
        except ImportError as e:
            self._init_error = f" Librería no instalada: {e}. Ejecutar: pip install google-analytics-data"
            self._client = None
            return False
        except Exception as e:
            self._init_error = f"Error inicializando GA4: {str(e)}"
            self._client = None
            return False
    
    def is_available(self) -> bool:
        """Verifica si GA4 está configurado y disponible."""
        return self._initialize() and self._client is not None
    
    def get_indirect_traffic(self, date_range: str = "last_30_days") -> Dict[str, Any]:
        """
        Obtiene métricas de tráfico que sugiere consulta previa en IA.
        
        Args:
            date_range: "last_30_days" | "last_90_days"
        
        Returns:
            {
                "sessions_indirect": int,
                "sessions_direct": int,
                "sessions_referral": int,
                "top_sources": [{"source": str, "sessions": int}],
                "data_source": "GA4" | "N/A"
            }
        """
        if not self._initialize():
            return {
                "sessions_indirect": 0,
                "sessions_direct": 0,
                "sessions_referral": 0,
                "top_sources": [],
                "data_source": "N/A",
                "note": self._init_error or "GA4 no disponible"
            }
        
        try:
            date_ranges = {
                "last_30_days": (30, "last_30_days"),
                "last_90_days": (90, "last_90_days")
            }
            
            days, label = date_ranges.get(date_range, (30, "last_30_days"))
            
            from datetime import timedelta
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            from google.analytics.data import RunReportRequest, DateRange, Dimension, Metric
            
            request = RunReportRequest(
                property=f"properties/{self.property_id}",
                dimensions=[Dimension(name="sessionDefaultChannelGrouping")],
                metrics=[Metric(name="sessions"), Metric(name="totalUsers")],
                date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
                limit=10,
            )
            
            response = self._client.run_report(request=request)
            
            sessions_indirect = 0
            sessions_direct = 0
            sessions_referral = 0
            top_sources = []
            
            for row in response.rows:
                channel = row.dimension_values[0].value
                sessions = int(row.metric_values[0].value)
                
                source_entry = {"source": channel, "sessions": sessions}
                top_sources.append(source_entry)
                
                if channel in ["Direct", "(None)"]:
                    sessions_direct += sessions
                elif channel in ["Organic Search", "Natural Search"]:
                    sessions_indirect += sessions
                elif channel in ["Referral"]:
                    sessions_referral += sessions
                else:
                    sessions_indirect += sessions
            
            return {
                "sessions_indirect": sessions_indirect,
                "sessions_direct": sessions_direct,
                "sessions_referral": sessions_referral,
                "top_sources": top_sources[:5],
                "data_source": "GA4",
                "date_range": label,
                "note": None
            }
            
        except Exception as e:
            return {
                "sessions_indirect": 0,
                "sessions_direct": 0,
                "sessions_referral": 0,
                "top_sources": [],
                "data_source": "N/A",
                "note": f"Error GA4: {str(e)}"
            }


# IndirectTrafficMetrics canonically defined in data_models/aeo_kpis.py
# Use: from data_models.aeo_kpis import IndirectTrafficMetrics
