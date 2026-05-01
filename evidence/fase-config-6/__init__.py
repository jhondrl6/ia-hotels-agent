"""
Analytics module for AEO metrics and KPI tracking.

ESTADO: PARCIALMENTE DEPRECADO
Solo se exportan clientes activos usados en v4complete:
  - GoogleAnalyticsClient (GA4)
  - GoogleSearchConsoleClient (GSC)

Los siguientes están deprecados (se eliminarán en v5.0.0):
  - ProfoundClient
  - SemrushClient
  - AnalyticsAggregator
  - UnifiedAnalyticsData
  - ConfidenceLevel
"""

# Solo clientes activos usados en v4complete
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
from modules.analytics.google_search_console_client import (
    GoogleSearchConsoleClient,
    GSCQueryData,
    GSCPageData,
    GSCReport,
)

__all__ = [
    # Activos
    "GoogleAnalyticsClient",
    "GoogleSearchConsoleClient",
    "GSCQueryData",
    "GSCPageData",
    "GSCReport",
]
