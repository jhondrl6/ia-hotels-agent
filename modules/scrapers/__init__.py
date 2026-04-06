
from modules.scrapers.web_scraper import WebScraper
from modules.scrapers.scraper_fallback import ScraperFallback
from modules.scrapers.schema_finder import SchemaFinder
from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

# T8B: Source Scrapers for Autonomous Research
# NOTE: TripAdvisorScraper, InstagramScraper -> archives/deprecated_modules_20260304
# (OBSOLETE: datos capturados por Google Places API)
from modules.scrapers.booking_scraper import BookingScraper, create_booking_scraper

# FASE 11A: Google Travel Scraper
from modules.scrapers.google_travel_scraper import GoogleTravelScraper, TravelPlaceData

try:
    from modules.scrapers.gbp_auditor import GBPAuditor
except Exception:
    GBPAuditor = None  # type: ignore

try:
    from modules.scrapers.gbp_posts_auditor import integrate_posts_auditor
except Exception:
    integrate_posts_auditor = None  # type: ignore

from modules.scrapers.gbp_factory import get_gbp_auditor, GBPAuditorAuto

__all__ = [
    "WebScraper",
    "ScraperFallback",
    "SchemaFinder",
    "GBPAuditor",
    "integrate_photo_auditor",
    "integrate_posts_auditor",
    "get_gbp_auditor",
    "GBPAuditorAuto",
    # T8B: Source Scrapers
    "BookingScraper",
    "create_booking_scraper",
    # NOTE: TripAdvisorScraper, InstagramScraper -> archives/deprecated_modules_20260304
    # FASE 11A: Google Travel
    "GoogleTravelScraper",
    "TravelPlaceData",
]
