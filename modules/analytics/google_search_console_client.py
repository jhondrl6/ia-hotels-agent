"""
Google Search Console Client para datos de busqueda organica.

FASE: FASE-D (GAP-IAO-01-06)
Estado: IMPLEMENTADO (requiere GSC_SITE_URL y credenciales de service account)

Usa el mismo service account que GA4. GSC API es GRATIS.
"""

import os
import logging
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

SCOPES = ['https://www.googleapis.com/auth/webmasters.readonly']


@dataclass
class GSCQueryData:
    """Datos de una query individual de Search Console."""
    query: str
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0

    @property
    def opportunity_score(self) -> float:
        """Score de oportunidad: alta impresion + bajo CTR = alto score."""
        if self.impressions == 0:
            return 0.0
        # Queries con muchas impresiones y CTR bajo tienen mas potencial
        return self.impressions * (1.0 - min(self.ctr / 100.0, 1.0))


@dataclass
class GSCPageData:
    """Datos de una pagina individual de Search Console."""
    url: str
    clicks: int = 0
    impressions: int = 0
    ctr: float = 0.0
    position: float = 0.0


@dataclass
class GSCReport:
    """Reporte agregado de Google Search Console."""
    is_available: bool = False
    start_date: str = ""
    end_date: str = ""
    total_clicks: int = 0
    total_impressions: int = 0
    avg_ctr: float = 0.0
    avg_position: float = 0.0
    queries: List[GSCQueryData] = field(default_factory=list)
    pages: List[GSCPageData] = field(default_factory=list)
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convierte el reporte a dict para serializacion."""
        return {
            "is_available": self.is_available,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "total_clicks": self.total_clicks,
            "total_impressions": self.total_impressions,
            "avg_ctr": round(self.avg_ctr, 2),
            "avg_position": round(self.avg_position, 2),
            "query_count": len(self.queries),
            "page_count": len(self.pages),
            "error_message": self.error_message,
        }


class GoogleSearchConsoleClient:
    """
    Client para Google Search Console API (Webmasters v3).

    Requiere:
    - GSC_SITE_URL: URL del sitio en GSC (ej: "https://hotel.com" o "sc-domain:hotel.com")
    - Credenciales de service account (mismo archivo que GA4)

    El API de GSC es 100% gratuita.
    """

    def __init__(self, credentials_path: str = None, site_url: str = None):
        self.credentials_path = credentials_path or os.getenv("GSC_CREDENTIALS_PATH")
        if not self.credentials_path:
            # Fallback al service account de GA4 por defecto
            ga4_creds = os.getenv("GA4_CREDENTIALS_PATH")
            if ga4_creds:
                self.credentials_path = ga4_creds
        self.site_url = site_url or os.getenv("GSC_SITE_URL")
        self._client = None
        self._initialized = False
        self._init_error = None

    def _initialize(self) -> bool:
        """Inicializa el cliente de GSC API."""
        if self._initialized:
            return self._client is not None

        self._initialized = True

        if not self.credentials_path:
            self._init_error = "GSC_CREDENTIALS_PATH no configurado (ni GA4_CREDENTIALS_PATH)"
            return False

        if not self.site_url:
            self._init_error = "GSC_SITE_URL no configurado"
            return False

        if not os.path.exists(self.credentials_path):
            self._init_error = f"Archivo de credenciales no encontrado: {self.credentials_path}"
            return False

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=SCOPES
            )

            self._client = build('webmasters', 'v3', credentials=credentials)
            return True

        except ImportError as e:
            self._init_error = f"Libreria no instalada: {e}. Ejecutar: pip install google-api-python-client"
            self._client = None
            return False
        except Exception as e:
            self._init_error = f"Error inicializando GSC: {str(e)}"
            logger.error(f"GSC init error: {e}")
            self._client = None
            return False

    def is_configured(self) -> bool:
        """Verifica si GSC esta configurado y disponible."""
        has_creds = bool(self.credentials_path and os.path.exists(self.credentials_path))
        has_site = bool(self.site_url)
        return has_creds and has_site

    def get_search_analytics(
        self,
        start_date: str = None,
        end_date: str = None,
        dimensions: List[str] = None,
    ) -> GSCReport:
        """
        Obtiene datos de Search Analytics desde GSC.

        Args:
            start_date: Fecha inicio formato YYYY-MM-DD. Default: hace 30 dias.
            end_date: Fecha fin formato YYYY-MM-DD. Default: hoy.
            dimensions: Lista de dimensiones. Default: ["query"].
                Opciones: ["query", "page", "country", "device"]

        Returns:
            GSCReport con los datos de busqueda
        """
        if not self._initialize():
            return GSCReport(
                is_available=False,
                error_message=self._init_error or "GSC no disponible"
            )

        # Fechas por defecto
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        if dimensions is None:
            dimensions = ["query"]

        try:
            request_body = {
                'startDate': start_date,
                'endDate': end_date,
                'dimensions': dimensions,
                'rowLimit': 25000,
                'startRow': 0,
            }

            response = self._client.searchanalytics().query(
                siteUrl=self.site_url,
                body=request_body
            ).execute()

            rows = response.get('rows', [])

            queries = []
            total_clicks = 0
            total_impressions = 0
            total_ctr = 0.0
            total_position = 0.0

            for row in rows:
                clicks = row.get('clicks', 0)
                impressions = row.get('impressions', 0)
                ctr = row.get('ctr', 0.0) * 100.0  # GSC returns decimal, convert to %
                position = row.get('position', 0.0)

                total_clicks += clicks
                total_impressions += impressions
                total_ctr += ctr * impressions if impressions > 0 else 0.0
                total_position += position * impressions if impressions > 0 else 0.0

                if "query" in dimensions:
                    query_val = row.get('keys', [''])[0]
                    queries.append(GSCQueryData(
                        query=query_val,
                        clicks=clicks,
                        impressions=impressions,
                        ctr=round(ctr, 2),
                        position=round(position, 2),
                    ))
                elif "page" in dimensions:
                    page_val = row.get('keys', [''])[0]
                    # handled below
                    pass

            avg_ctr = (total_ctr / total_impressions) if total_impressions > 0 else 0.0
            avg_position = (total_position / total_impressions) if total_impressions > 0 else 0.0

            # Si se pidio dimension page, extraer paginas
            pages = []
            if "page" in dimensions:
                page_request_body = {
                    'startDate': start_date,
                    'endDate': end_date,
                    'dimensions': ['page'],
                    'rowLimit': 1000,
                    'startRow': 0,
                }
                page_response = self._client.searchanalytics().query(
                    siteUrl=self.site_url,
                    body=page_request_body
                ).execute()
                page_rows = page_response.get('rows', [])
                for row in page_rows:
                    page_val = row.get('keys', [''])[0]
                    pages.append(GSCPageData(
                        url=page_val,
                        clicks=row.get('clicks', 0),
                        impressions=row.get('impressions', 0),
                        ctr=round(row.get('ctr', 0.0) * 100.0, 2),
                        position=round(row.get('position', 0.0), 2),
                    ))

            return GSCReport(
                is_available=True,
                start_date=start_date,
                end_date=end_date,
                total_clicks=total_clicks,
                total_impressions=total_impressions,
                avg_ctr=round(avg_ctr, 2),
                avg_position=round(avg_position, 2),
                queries=queries,
                pages=pages,
            )

        except Exception as e:
            error_msg = f"Error consultando GSC Search Analytics: {str(e)}"
            logger.error(error_msg)
            return GSCReport(
                is_available=False,
                start_date=start_date,
                end_date=end_date,
                error_message=error_msg,
            )

    def get_top_opportunities(self, report: GSCReport, top_n: int = 10) -> List[GSCQueryData]:
        """
        Identifica queries con alta impresion y bajo CTR como oportunidades.

        Args:
            report: GSCReport con datos de Search Console
            top_n: Numero de oportunidades a retornar

        Returns:
            Lista de GSCQueryData ordenada por opportunity_score descendente
        """
        if not report.is_available or not report.queries:
            return []

        opportunities = sorted(
            report.queries,
            key=lambda q: q.opportunity_score,
            reverse=True
        )
        return opportunities[:top_n]
