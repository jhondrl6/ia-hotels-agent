"""
Modelos de datos del sistema.
"""
# Lightweight dataclass models (no external deps)
from .analytics_status import AnalyticsStatus

# Pydantic models - canonical assessment
from .canonical_assessment import (
    CanonicalAssessment,
    Claim,
    SiteMetadata,
    SchemaAnalysis,
    PerformanceMetrics,
    PerformanceAnalysis,
    GBPAnalysis,
)

__all__ = [
    "AnalyticsStatus",
    "CanonicalAssessment",
    "Claim",
    "SiteMetadata",
    "SchemaAnalysis",
    "PerformanceMetrics",
    "PerformanceAnalysis",
    "GBPAnalysis",
]