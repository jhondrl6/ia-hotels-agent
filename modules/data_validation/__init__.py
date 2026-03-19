"""Data Validation module for IA Hoteles Agent v4.0.

Provides cross-validation between data sources and confidence taxonomy.
Includes external API integrations for data verification.
"""

from .confidence_taxonomy import (
    ConfidenceLevel,
    ConfidenceTaxonomy,
    DataPoint,
    DataSource,
    ValidationResult,
)

from .cross_validator import (
    CrossValidator,
    normalize_phone_number,
)

from .external_apis import (
    PageSpeedClient,
    PageSpeedResult,
    RichResultsTestClient,
    RichResultsTestResult,
    SchemaValidationResult,
    SchemaType,
)

__all__ = [
    # Core validation
    "ConfidenceLevel",
    "ConfidenceTaxonomy",
    "DataPoint",
    "DataSource",
    "ValidationResult",
    "CrossValidator",
    "normalize_phone_number",
    # External APIs
    "PageSpeedClient",
    "PageSpeedResult",
    "RichResultsTestClient",
    "RichResultsTestResult",
    "SchemaValidationResult",
    "SchemaType",
]
