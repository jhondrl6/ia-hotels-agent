"""
Módulo de auditors externos.
"""
from .pagespeed_auditor_v2 import PageSpeedAuditorV2, PageSpeedMetrics, PERFORMANCE_THRESHOLDS

__all__ = ["PageSpeedAuditorV2", "PageSpeedMetrics", "PERFORMANCE_THRESHOLDS"]