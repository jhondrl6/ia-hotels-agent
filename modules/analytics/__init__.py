"""
Analytics module for AEO metrics and KPI tracking.

Contains mock clients for external APIs (Profound, Semrush) that can be
implemented for real data retrieval in production environments.
"""
from modules.analytics.profound_client import ProfoundClient
from modules.analytics.semrush_client import SemrushClient
from modules.analytics.google_analytics_client import GoogleAnalyticsClient
from modules.analytics.google_search_console_client import (
    GoogleSearchConsoleClient,
    GSCQueryData,
    GSCPageData,
    GSCReport,
)
from modules.analytics.data_aggregator import (
    AnalyticsAggregator,
    UnifiedAnalyticsData,
    ConfidenceLevel,
)

__all__ = [
    "ProfoundClient",
    "SemrushClient",
    "GoogleAnalyticsClient",
    "GoogleSearchConsoleClient",
    "GSCQueryData",
    "GSCPageData",
    "GSCReport",
    "AnalyticsAggregator",
    "UnifiedAnalyticsData",
    "ConfidenceLevel",
]
