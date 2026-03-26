"""
Analytics module for AEO metrics and KPI tracking.

Contains mock clients for external APIs (Profound, Semrush) that can be
implemented for real data retrieval in production environments.
"""
from modules.analytics.profound_client import ProfoundClient
from modules.analytics.semrush_client import SemrushClient

__all__ = ["ProfoundClient", "SemrushClient"]
