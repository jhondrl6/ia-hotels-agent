"""
Modelos de datos del sistema.
"""
# Legacy models (dataclass)
from .assessment import (
    Claim as LegacyClaim,
    Evidence as LegacyEvidence,
    CanonicalAssessment as LegacyCanonicalAssessment,
)

# Sprint 1, Fase 0 - Pydantic models
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
    # Legacy
    "LegacyClaim",
    "LegacyEvidence",
    "LegacyCanonicalAssessment",
    # Pydantic (nuevo)
    "CanonicalAssessment",
    "Claim",
    "SiteMetadata",
    "SchemaAnalysis",
    "PerformanceMetrics",
    "PerformanceAnalysis",
    "GBPAnalysis",
]