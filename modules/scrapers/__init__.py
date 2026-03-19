
from modules.scrapers.web_scraper import WebScraper
from modules.scrapers.scraper_fallback import ScraperFallback
from modules.scrapers.schema_finder import SchemaFinder
from modules.scrapers.gbp_photo_auditor import integrate_photo_auditor

try:
    from modules.scrapers.gbp_auditor import GBPAuditor
except Exception:
    GBPAuditor = None  # type: ignore

try:
    from modules.scrapers.gbp_auditor_playwright import GBPAuditorPlaywright
except ImportError:
    GBPAuditorPlaywright = None  # type: ignore

try:
    from modules.scrapers.gbp_photo_auditor_playwright import GBPPhotoAuditorPlaywright
except ImportError:
    GBPPhotoAuditorPlaywright = None  # type: ignore

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
    "GBPAuditorPlaywright",
    "GBPPhotoAuditorPlaywright",
    "integrate_photo_auditor",
    "integrate_posts_auditor",
    "get_gbp_auditor",
    "GBPAuditorAuto",
]
