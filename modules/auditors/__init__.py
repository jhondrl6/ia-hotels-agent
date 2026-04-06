"""Auditors module for IA Hoteles Agent.

Provides comprehensive audit capabilities with API integrations.
"""

from .v4_comprehensive import (
    V4ComprehensiveAuditor,
    V4AuditResult,
    SchemaAuditResult,
    GBPApiResult,
    PerformanceResult,
    CrossValidationResult,
    MetadataAuditResult,
    AICrawlerAuditResult,
    get_v4_auditor,
)

from .ia_readiness_calculator import IAReadinessCalculator, IAReadinessReport

from .seo_elements_detector import SEOElementsDetector, SEOElementsResult

__all__ = [
    "V4ComprehensiveAuditor",
    "V4AuditResult",
    "SchemaAuditResult",
    "GBPApiResult",
    "PerformanceResult",
    "CrossValidationResult",
    "MetadataAuditResult",
    "AICrawlerAuditResult",
    "get_v4_auditor",
    "IAReadinessCalculator",
    "IAReadinessReport",
    "SEOElementsDetector",
    "SEOElementsResult",
]
