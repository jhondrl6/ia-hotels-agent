"""External API clients for data validation.

Provides integrations with:
- Google PageSpeed Insights API
- Google Rich Results Test API (NEW v4.0)
- Google Places API (via modules.scrapers.google_places_client)
"""

from .pagespeed_client import (
    PageSpeedClient,
    PageSpeedResult,
)
from .rich_results_client import (
    RichResultsTestClient,
    RichResultsTestResult,
    SchemaValidationResult,
    SchemaType,
)

__all__ = [
    "PageSpeedClient",
    "PageSpeedResult",
    "RichResultsTestClient",
    "RichResultsTestResult",
    "SchemaValidationResult",
    "SchemaType",
]
