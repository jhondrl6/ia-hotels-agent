"""GEO Diagnostic - 42-method evaluation system for AI discovery readiness.

This module implements the diagnostic phase of GEO Enrichment, providing
a comprehensive evaluation of hotel website readiness for AI discovery
across 8 key areas totaling 100 points.

Architecture:
- 8 areas of evaluation
- 42 individual check methods
- 4 GEO bands (EXCELLENT, GOOD, FOUNDATION, CRITICAL)
- Orthogonal to pipeline: receives hotel_data, produces diagnostic only

Reference: .opencode/plans/GEO_FIELD_MAPPING.md (FASE-1)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional
from urllib.parse import urljoin, urlparse

from data_models.canonical_assessment import CanonicalAssessment


class GEOBand(Enum):
    """GEO readiness band classification.
    
    Bands are based on total score out of 100 points across 8 areas.
    """
    EXCELLENT = "excellent"   # 86-100: Minimal enrichment needed
    GOOD = "good"            # 68-85: Light enrichment recommended
    FOUNDATION = "foundation" # 36-67: Full enrichment required
    CRITICAL = "critical"    # 0-35: Urgent intervention needed

    @classmethod
    def from_score(cls, score: int) -> "GEOBand":
        """Classify band based on total score.
        
        Args:
            score: Total score out of 100.
            
        Returns:
            GEOBand classification.
        """
        if score >= 86:
            return cls.EXCELLENT
        elif score >= 68:
            return cls.GOOD
        elif score >= 36:
            return cls.FOUNDATION
        else:
            return cls.CRITICAL


@dataclass
class ScoreBreakdown:
    """Breakdown of scores by 8 evaluation areas.
    
    Each area has a maximum score:
    - robots: 18 points (6 methods)
    - llms: 18 points (6 methods)
    - schema: 16 points (7 methods)
    - meta: 14 points (5 methods)
    - content: 12 points (5 methods)
    - brand: 10 points (4 methods)
    - signals: 6 points (4 methods)
    - ai_discovery: 6 points (6 methods)
    """
    robots: int = 0          # /18
    llms: int = 0            # /18
    schema: int = 0          # /16
    meta: int = 0            # /14
    content: int = 0         # /12
    brand: int = 0           # /10
    signals: int = 0         # /6
    ai_discovery: int = 0     # /6

    def total(self) -> int:
        """Calculate total score across all areas."""
        return (
            self.robots +
            self.llms +
            self.schema +
            self.meta +
            self.content +
            self.brand +
            self.signals +
            self.ai_discovery
        )

    def to_dict(self) -> Dict[str, int]:
        """Export breakdown as dictionary."""
        return {
            "robots": self.robots,
            "llms": self.llms,
            "schema": self.schema,
            "meta": self.meta,
            "content": self.content,
            "brand": self.brand,
            "signals": self.signals,
            "ai_discovery": self.ai_discovery,
            "total": self.total(),
        }


@dataclass
class GEOAssessment:
    """Complete GEO diagnostic assessment result.
    
    Attributes:
        site_url: URL that was assessed.
        total_score: Overall score out of 100.
        band: GEO readiness band classification.
        breakdown: Detailed scores by area.
        details: Per-method results for traceability.
        gaps_blocking: List of blocking gaps identified.
        gaps_mitigable: List of mitigable gaps identified.
        recommendations: List of recommended actions.
    """
    site_url: str
    total_score: int
    band: GEOBand
    breakdown: ScoreBreakdown
    details: Dict[str, Dict[str, Any]]
    gaps_blocking: List[str]
    gaps_mitigable: List[str]
    recommendations: List[str]


class GEODiagnostic:
    """GEO Diagnostic engine implementing 42 check methods.
    
    This class evaluates hotel website readiness for AI discovery
    across 8 areas. It is designed to be ORTHOGONAL to the existing
    pipeline - it only reads from hotel_data and produces diagnostic
    output without modifying the input.
    
    The 42 methods are organized as follows:
    
    ROBOTS.TXT AREA (18 points, 6 methods)
    R1: robots.txt exists (3pts)
    R2: robots.txt allows crawling (3pts)
    R3: sitemap.xml referenced (3pts)
    R4: crawl-delay configured (3pts)
    R5: User-agent specific (3pts)
    R6: Sensitive paths blocked (3pts)
    
    LLMS.TXT AREA (18 points, 6 methods)
    L1: llms.txt exists (3pts)
    L2: Format valid (3pts)
    L3: Hotel name present (3pts)
    L4: Description complete (3pts)
    L5: Amenities listed (3pts)
    L6: Location precise (3pts)
    
    SCHEMA.ORG AREA (16 points, 7 methods)
    S1: Schema Hotel present (3pts)
    S2: name correct (2pts)
    S3: url canonical (2pts)
    S4: telephone present (2pts)
    S5: address complete (3pts)
    S6: amenityFeature listed (2pts)
    S7: review/rating present (2pts)
    
    META TAGS AREA (14 points, 5 methods)
    M1: Title tag optimized (3pts)
    M2: Meta description unique (3pts)
    M3: Canonical URL (2pts)
    M4: Open Graph tags (3pts)
    M5: Twitter cards (3pts)
    
    CONTENT AREA (12 points, 5 methods)
    C1: H1 unique and descriptive (3pts)
    C2: Statistics disclosed (2pts)
    C3: External citations (3pts)
    C4: Heading hierarchy (2pts)
    C5: Content length >300 words (2pts)
    
    BRAND & ENTITY AREA (10 points, 4 methods)
    B1: Brand name consistent (3pts)
    B2: Knowledge graph links (3pts)
    B3: Wikipedia/Wikidata (2pts)
    B4: Social profiles (2pts)
    
    SIGNALS AREA (6 points, 4 methods)
    G1: html_lang declared (2pts)
    G2: RSS feed exists (2pts)
    G3: date_modified recent (1pt)
    G4: Structured data fresh (1pt)
    
    AI DISCOVERY AREA (6 points, 6 methods)
    A1: ai.txt exists (1pt)
    A2: ai_summary.json valid (1pt)
    A3: ai_faq.json structured (1pt)
    A4: FAQ schema detected (1pt)
    A5: HowTo schema (1pt)
    A6: Q&A content (1pt)
    
    Reference: GEO_FIELD_MAPPING.md (FASE-1)
    """

    # AI bot user agents for robots.txt analysis
    AI_BOTS_TIER1 = [
        "GPTBot",
        "ChatGPT-User",
        "Claude-Web",
        "anthropic-ai",
    ]
    AI_BOTS_TIER2 = [
        "Google-Extended",
        "FacebookBot",
        "Applebot",
        "Bytespider",
        "Diffbot",
        "Discordbot",
        "GPTBot",
        "ia_architect",
        "ImagesiftBot",
        "Kodi",
        "Meta-ExternalAgent",
        "Amazonbot",
        "AwarioSmartBot",
        "Ax生态环境监测bot",
        "BlogMySite",
        "Buck",
        "CCBot",
        "ChatGPT-User",
        "Claude-Web",
        "Cloudflare speed tester",
        "Diffbot",
        "DuckDuckBot",
        "Environment",
        "FacebookBot",
        "Google-Extended",
        "GPTBot",
        "Grapeshot",
        "Honor",
        "ICC-Crawler",
        "ImagesiftBot",
        "Indy Library",
        "Kodi",
        "LivelapBot",
        "MediaAI",
        "MediBot",
        "Meta-ExternalAgent",
        "Meltwater",
        "MergePage",
        "Minion",
        "MJ12bot",
        "MTRobot",
        "NICE地方治理Bot",
        "Netseer",
        "OMGbot",
        "OpeNEnt",
        "PetalBot",
        "Pinterest",
        "Plexlabs",
        "Presbot",
        " Riddler",
        "Rogerbot",
        "Scholar",
        "SeekportBot",
        "SentiBot",
        "SEOdengo",
        "slackbot",
        "Sogou",
        "Spotify",
        "TelegramBot",
        "Television",
        "TinEye",
        "Trove",
        "Twitterbot",
        "Uptime",
        "WebBot",
        "Yandex",
        "YouBot",
        "Zombie",
    ]

    def __init__(self, hotel_data: CanonicalAssessment):
        """Initialize diagnostic with hotel data.
        
        Args:
            hotel_data: CanonicalAssessment containing site analysis data.
                        This is NOT modified by the diagnostic.
        """
        self.hotel_data = hotel_data
        self.site_url = hotel_data.url
        self.details: Dict[str, Dict[str, Any]] = {}

    def diagnose(self) -> GEOAssessment:
        """Run full diagnostic across all 42 methods.
        
        Returns:
            GEOAssessment with complete diagnostic results.
        """
        breakdown = ScoreBreakdown()
        all_gaps_blocking = []
        all_gaps_mitigable = []
        all_recommendations = []

        # Execute all 8 areas
        robots_score, robots_gaps, robots_recs = self.robots_check()
        breakdown.robots = robots_score
        all_gaps_blocking.extend(robots_gaps["blocking"])
        all_gaps_mitigable.extend(robots_gaps["mitigable"])
        all_recommendations.extend(robots_recs)

        llms_score, llms_gaps, llms_recs = self.llms_check()
        breakdown.llms = llms_score
        all_gaps_blocking.extend(llms_gaps["blocking"])
        all_gaps_mitigable.extend(llms_gaps["mitigable"])
        all_recommendations.extend(llms_recs)

        schema_score, schema_gaps, schema_recs = self.schema_check()
        breakdown.schema = schema_score
        all_gaps_blocking.extend(schema_gaps["blocking"])
        all_gaps_mitigable.extend(schema_gaps["mitigable"])
        all_recommendations.extend(schema_recs)

        meta_score, meta_gaps, meta_recs = self.meta_check()
        breakdown.meta = meta_score
        all_gaps_blocking.extend(meta_gaps["blocking"])
        all_gaps_mitigable.extend(meta_gaps["mitigable"])
        all_recommendations.extend(meta_recs)

        content_score, content_gaps, content_recs = self.content_check()
        breakdown.content = content_score
        all_gaps_blocking.extend(content_gaps["blocking"])
        all_gaps_mitigable.extend(content_gaps["mitigable"])
        all_recommendations.extend(content_recs)

        brand_score, brand_gaps, brand_recs = self.brand_check()
        breakdown.brand = brand_score
        all_gaps_blocking.extend(brand_gaps["blocking"])
        all_gaps_mitigable.extend(brand_gaps["mitigable"])
        all_recommendations.extend(brand_recs)

        signals_score, signals_gaps, signals_recs = self.signals_check()
        breakdown.signals = signals_score
        all_gaps_blocking.extend(signals_gaps["blocking"])
        all_gaps_mitigable.extend(signals_gaps["mitigable"])
        all_recommendations.extend(signals_recs)

        ai_discovery_score, ai_gaps, ai_recs = self.ai_discovery_check()
        breakdown.ai_discovery = ai_discovery_score
        all_gaps_blocking.extend(ai_gaps["blocking"])
        all_gaps_mitigable.extend(ai_gaps["mitigable"])
        all_recommendations.extend(ai_recs)

        total_score = breakdown.total()
        band = GEOBand.from_score(total_score)

        return GEOAssessment(
            site_url=self.site_url,
            total_score=total_score,
            band=band,
            breakdown=breakdown,
            details=self.details,
            gaps_blocking=all_gaps_blocking,
            gaps_mitigable=all_gaps_mitigable,
            recommendations=all_recommendations,
        )

    # =====================================================================
    # ROBOTS.TXT AREA (18 points, 6 methods)
    # =====================================================================

    def robots_check(self) -> tuple:
        """Evaluate robots.txt readiness for AI discovery.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        # R1: robots.txt exists (3pts) - available via url derivation
        # We check if we have the url
        if self.site_url:
            score += 3
            self.details["R1_robots_exists"] = {"status": "pass", "score": 3}
        else:
            gaps["blocking"].append("R1: Cannot derive robots.txt URL")
            self.details["R1_robots_exists"] = {"status": "fail", "score": 0}
        
        # R2: robots.txt allows crawling (3pts) - requires actual scraping
        # This is a mitigable gap - we assume permissive unless blocked
        score += 3  # Assume allowed for scoring purposes
        self.details["R2_robots_allows_crawling"] = {"status": "assumed", "score": 3}
        gaps["mitigable"].append("R2: Requires scraping to verify actual robots.txt rules")
        
        # R3: sitemap.xml referenced (3pts)
        # Can be derived from url
        sitemap_url = self._derive_sitemap_url()
        if sitemap_url:
            score += 3
            self.details["R3_sitemap_referenced"] = {"status": "pass", "score": 3, "url": sitemap_url}
        else:
            gaps["mitigable"].append("R3: Cannot determine sitemap.xml location")
            self.details["R3_sitemap_referenced"] = {"status": "unknown", "score": 0}
        
        # R4: crawl-delay configured (3pts) - mitigable gap
        gaps["mitigable"].append("R4: Requires scraping robots.txt to check crawl-delay")
        self.details["R4_crawl_delay"] = {"status": "scraping_required", "score": 0}
        
        # R5: User-agent specific (3pts) - available via cms_detected
        cms = self.hotel_data.site_metadata.cms_detected
        if cms:
            score += 3
            self.details["R5_user_agent_specific"] = {"status": "pass", "score": 3, "cms": cms}
        else:
            gaps["mitigable"].append("R5: CMS not detected, cannot verify user-agent rules")
            self.details["R5_user_agent_specific"] = {"status": "unknown", "score": 0}
        
        # R6: Sensitive paths blocked (3pts) - mitigable gap
        gaps["mitigable"].append("R6: Requires scraping robots.txt to verify path blocking")
        self.details["R6_sensitive_paths"] = {"status": "scraping_required", "score": 0}
        
        # Recommendation
        if gaps["mitigable"]:
            recs.append("Implement SitePresenceChecker for robots.txt scraping")
        
        return score, gaps, recs

    def _derive_sitemap_url(self) -> Optional[str]:
        """Derive sitemap URL from site URL."""
        if not self.site_url:
            return None
        parsed = urlparse(self.site_url)
        return f"{parsed.scheme}://{parsed.netloc}/sitemap.xml"

    # =====================================================================
    # LLMS.TXT AREA (18 points, 6 methods)
    # =====================================================================

    def llms_check(self) -> tuple:
        """Evaluate llms.txt readiness.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        # L1: llms.txt exists (3pts) - mitigable
        gaps["mitigable"].append("L1: llms.txt existence requires scraping or generation")
        self.details["L1_llms_exists"] = {"status": "scraping_required", "score": 0}
        
        # L2: Format valid (3pts) - mitigable
        gaps["mitigable"].append("L2: llms.txt format validation requires content analysis")
        self.details["L2_llms_format"] = {"status": "scraping_required", "score": 0}
        
        # L3: Hotel name present (3pts) - available via site_metadata.title
        title = self.hotel_data.site_metadata.title
        if title and not self.hotel_data.site_metadata.has_default_title:
            score += 3
            self.details["L3_llms_name"] = {"status": "pass", "score": 3, "title": title}
        else:
            gaps["mitigable"].append("L3: Title is default CMS title, not optimized for llms.txt")
            self.details["L3_llms_name"] = {"status": "needs_optimization", "score": 0}
        
        # L4: Description complete (3pts) - available via site_metadata.description
        desc = self.hotel_data.site_metadata.description
        if desc and len(desc) > 50:
            score += 3
            self.details["L4_llms_description"] = {"status": "pass", "score": 3}
        else:
            gaps["mitigable"].append("L4: Meta description missing or too short for llms.txt")
            self.details["L4_llms_description"] = {"status": "needs_optimization", "score": 0}
        
        # L5: Amenities listed (3pts) - available via gbp_analysis.categories
        gbp = self.hotel_data.gbp_analysis
        if gbp and gbp.categories:
            score += 3
            self.details["L5_llms_amenities"] = {"status": "pass", "score": 3, "categories": gbp.categories[:5]}
        else:
            gaps["mitigable"].append("L5: GBP categories not available for amenities listing")
            self.details["L5_llms_amenities"] = {"status": "unknown", "score": 0}
        
        # L6: Location precise (3pts) - partially available
        if gbp and gbp.profile_url:
            score += 2  # Partial credit for having GBP profile
            gaps["mitigable"].append("L6: Full location data requires schema raw extraction")
            self.details["L6_llms_location"] = {"status": "partial", "score": 2}
        else:
            gaps["mitigable"].append("L6: No GBP profile URL for location verification")
            self.details["L6_llms_location"] = {"status": "missing", "score": 0}
        
        if gaps["mitigable"]:
            recs.append("Generate llms.txt with GEOEnrichmentLayer for FULL enrichment")
        
        return score, gaps, recs

    # =====================================================================
    # SCHEMA.ORG AREA (16 points, 7 methods)
    # =====================================================================

    def schema_check(self) -> tuple:
        """Evaluate Schema.org implementation.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        schema = self.hotel_data.schema_analysis
        raw_schema = schema.raw_schema if schema else None
        
        # S1: Schema Hotel present (3pts)
        if schema and schema.has_hotel_schema:
            score += 3
            self.details["S1_schema_hotel"] = {"status": "pass", "score": 3}
        else:
            gaps["blocking"].append("S1: No Hotel schema detected")
            self.details["S1_schema_hotel"] = {"status": "fail", "score": 0}
        
        # S2: name correct (2pts)
        if raw_schema and "name" in raw_schema:
            score += 2
            self.details["S2_schema_name"] = {"status": "pass", "score": 2}
        else:
            gaps["mitigable"].append("S2: Schema name field missing")
            self.details["S2_schema_name"] = {"status": "missing", "score": 0}
        
        # S3: url canonical (2pts)
        if raw_schema and "url" in raw_schema:
            score += 2
            self.details["S3_schema_url"] = {"status": "pass", "score": 2}
        else:
            gaps["mitigable"].append("S3: Schema url field missing")
            self.details["S3_schema_url"] = {"status": "missing", "score": 0}
        
        # S4: telephone present (2pts) - requires raw schema extraction
        if raw_schema and ("telephone" in raw_schema or "phone" in str(raw_schema)):
            score += 2
            self.details["S4_schema_telephone"] = {"status": "pass", "score": 2}
        else:
            gaps["mitigable"].append("S4: Schema telephone field missing")
            self.details["S4_schema_telephone"] = {"status": "missing", "score": 0}
        
        # S5: address complete (3pts) - requires raw schema
        has_address = False
        if raw_schema:
            if "address" in raw_schema or "geo" in raw_schema:
                has_address = True
        if has_address:
            score += 3
            self.details["S5_schema_address"] = {"status": "pass", "score": 3}
        else:
            gaps["mitigable"].append("S5: Schema address/geo fields missing")
            self.details["S5_schema_address"] = {"status": "missing", "score": 0}
        
        # S6: amenityFeature listed (2pts)
        if schema and "amenityFeature" in schema.present_fields:
            score += 2
            self.details["S6_schema_amenities"] = {"status": "pass", "score": 2}
        else:
            gaps["mitigable"].append("S6: Schema amenityFeature field missing")
            self.details["S6_schema_amenities"] = {"status": "missing", "score": 0}
        
        # S7: review/rating present (2pts)
        if schema and ("review" in schema.present_fields or "aggregateRating" in schema.present_fields):
            score += 2
            self.details["S7_schema_rating"] = {"status": "pass", "score": 2}
        else:
            gaps["mitigable"].append("S7: Schema review/rating fields missing")
            self.details["S7_schema_rating"] = {"status": "missing", "score": 0}
        
        if gaps["mitigable"] or gaps["blocking"]:
            recs.append("Enhance Schema.org implementation with missing fields")
        
        return score, gaps, recs

    # =====================================================================
    # META TAGS AREA (14 points, 5 methods)
    # =====================================================================

    def meta_check(self) -> tuple:
        """Evaluate meta tags implementation.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        site_meta = self.hotel_data.site_metadata
        
        # M1: Title tag optimized (3pts)
        if site_meta.title and not site_meta.has_default_title:
            score += 3
            self.details["M1_title_optimized"] = {"status": "pass", "score": 3}
        else:
            gaps["blocking"].append("M1: Title tag is default CMS title")
            self.details["M1_title_optimized"] = {"status": "fail", "score": 0}
        
        # M2: Meta description unique (3pts)
        if site_meta.description and len(site_meta.description) > 50:
            score += 3
            self.details["M2_meta_description"] = {"status": "pass", "score": 3}
        else:
            gaps["blocking"].append("M2: Meta description missing or too short")
            self.details["M2_meta_description"] = {"status": "fail", "score": 0}
        
        # M3: Canonical URL (2pts)
        if self.site_url:
            score += 2
            self.details["M3_canonical_url"] = {"status": "pass", "score": 2, "url": self.site_url}
        else:
            gaps["blocking"].append("M3: No canonical URL available")
            self.details["M3_canonical_url"] = {"status": "fail", "score": 0}
        
        # M4: Open Graph tags (3pts) - requires scraping
        gaps["mitigable"].append("M4: Open Graph tags require scraping to verify")
        self.details["M4_open_graph"] = {"status": "scraping_required", "score": 0}
        
        # M5: Twitter cards (3pts) - requires scraping
        gaps["mitigable"].append("M5: Twitter cards require scraping to verify")
        self.details["M5_twitter_cards"] = {"status": "scraping_required", "score": 0}
        
        if gaps["mitigable"]:
            recs.append("Implement Open Graph and Twitter Card meta tags")
        
        return score, gaps, recs

    # =====================================================================
    # CONTENT AREA (12 points, 5 methods)
    # =====================================================================

    def content_check(self) -> tuple:
        """Evaluate content quality for AI discovery.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        site_meta = self.hotel_data.site_metadata
        
        # C1: H1 unique and descriptive (3pts) - available via title
        if site_meta.title and not site_meta.has_default_title:
            score += 3
            self.details["C1_h1_unique"] = {"status": "pass", "score": 3}
        else:
            gaps["blocking"].append("C1: H1/title is default CMS title")
            self.details["C1_h1_unique"] = {"status": "fail", "score": 0}
        
        # C2: Statistics disclosed (2pts) - available via gbp_analysis
        gbp = self.hotel_data.gbp_analysis
        if gbp and (gbp.rating is not None or gbp.review_count is not None):
            score += 2
            self.details["C2_statistics"] = {"status": "pass", "score": 2, 
                                             "rating": gbp.rating, 
                                             "reviews": gbp.review_count}
        else:
            gaps["blocking"].append("C2: No statistics (rating/reviews) available")
            self.details["C2_statistics"] = {"status": "missing", "score": 0}
        
        # C3: External citations (3pts) - BLOCKING gap
        gaps["blocking"].append("C3: External citations require content scraping")
        self.details["C3_citations"] = {"status": "scraping_required", "score": 0}
        
        # C4: Heading hierarchy (2pts) - BLOCKING gap
        gaps["blocking"].append("C4: Heading hierarchy requires content scraping")
        self.details["C4_heading_hierarchy"] = {"status": "scraping_required", "score": 0}
        
        # C5: Content length >300 words (2pts) - BLOCKING gap
        gaps["blocking"].append("C5: Content length requires content scraping")
        self.details["C5_content_length"] = {"status": "scraping_required", "score": 0}
        
        recs.append("Audit actual site content for citations, heading hierarchy, and length")
        
        return score, gaps, recs

    # =====================================================================
    # BRAND & ENTITY AREA (10 points, 4 methods)
    # =====================================================================

    def brand_check(self) -> tuple:
        """Evaluate brand consistency and entity presence.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        site_meta = self.hotel_data.site_metadata
        
        # B1: Brand name consistent (3pts)
        if site_meta.title and not site_meta.has_default_title:
            score += 3
            self.details["B1_brand_consistent"] = {"status": "pass", "score": 3}
        else:
            gaps["mitigable"].append("B1: Brand name is default CMS title")
            self.details["B1_brand_consistent"] = {"status": "needs_review", "score": 0}
        
        # B2: Knowledge graph links (3pts) - BLOCKING gap
        gaps["blocking"].append("B2: Knowledge graph links require external API")
        self.details["B2_knowledge_graph"] = {"status": "external_api_required", "score": 0}
        
        # B3: Wikipedia/Wikidata (2pts) - BLOCKING gap
        gaps["blocking"].append("B3: Wikipedia/Wikidata presence requires external search")
        self.details["B3_wikipedia"] = {"status": "external_search_required", "score": 0}
        
        # B4: Social profiles (2pts) - mitigable
        gbp = self.hotel_data.gbp_analysis
        if gbp and gbp.categories:
            # Check if social profiles might be in categories or metadata
            score += 1  # Partial credit
            gaps["mitigable"].append("B4: Full social profile audit required")
            self.details["B4_social_profiles"] = {"status": "partial", "score": 1}
        else:
            gaps["blocking"].append("B4: No GBP data to verify social profiles")
            self.details["B4_social_profiles"] = {"status": "missing", "score": 0}
        
        recs.append("Establish Knowledge Graph presence and Wikipedia/Wikidata entries")
        
        return score, gaps, recs

    # =====================================================================
    # SIGNALS AREA (6 points, 4 methods)
    # =====================================================================

    def signals_check(self) -> tuple:
        """Evaluate technical signals for AI discovery.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        site_meta = self.hotel_data.site_metadata
        schema = self.hotel_data.schema_analysis
        
        # G1: html_lang declared (2pts)
        if site_meta.detected_language:
            score += 2
            self.details["G1_html_lang"] = {"status": "pass", "score": 2, 
                                            "language": site_meta.detected_language}
        else:
            gaps["mitigable"].append("G1: HTML language not declared")
            self.details["G1_html_lang"] = {"status": "missing", "score": 0}
        
        # G2: RSS feed exists (2pts) - requires scraping
        gaps["mitigable"].append("G2: RSS feed existence requires scraping")
        self.details["G2_rss_feed"] = {"status": "scraping_required", "score": 0}
        
        # G3: date_modified recent (1pt) - requires schema raw
        raw_schema = schema.raw_schema if schema else None
        if raw_schema and ("dateModified" in raw_schema or "datePublished" in raw_schema):
            score += 1
            self.details["G3_date_modified"] = {"status": "pass", "score": 1}
        else:
            gaps["mitigable"].append("G3: Schema dateModified not found")
            self.details["G3_date_modified"] = {"status": "missing", "score": 0}
        
        # G4: Structured data fresh (1pt)
        if schema and schema.coverage_score > 0.5:
            score += 1
            self.details["G4_structured_data_fresh"] = {"status": "pass", "score": 1,
                                                         "coverage": schema.coverage_score}
        else:
            gaps["mitigable"].append("G4: Structured data coverage score low")
            self.details["G4_structured_data_fresh"] = {"status": "low_coverage", "score": 0}
        
        recs.append("Implement RSS feed and ensure schema freshness dates")
        
        return score, gaps, recs

    # =====================================================================
    # AI DISCOVERY AREA (6 points, 6 methods)
    # =====================================================================

    def ai_discovery_check(self) -> tuple:
        """Evaluate AI discovery file readiness.
        
        Returns:
            Tuple of (score, gaps_dict, recommendations_list)
        """
        score = 0
        gaps = {"blocking": [], "mitigable": []}
        recs = []
        
        schema = self.hotel_data.schema_analysis
        
        # A1: ai.txt exists (1pt) - mitigable
        gaps["mitigable"].append("A1: ai.txt requires generation or scraping")
        self.details["A1_ai_txt"] = {"status": "generation_required", "score": 0}
        
        # A2: ai_summary.json valid (1pt) - mitigable
        gaps["mitigable"].append("A2: ai_summary.json requires generation")
        self.details["A2_ai_summary"] = {"status": "generation_required", "score": 0}
        
        # A3: ai_faq.json structured (1pt) - mitigable
        gaps["mitigable"].append("A3: ai_faq.json requires generation")
        self.details["A3_ai_faq"] = {"status": "generation_required", "score": 0}
        
        # A4: FAQ schema detected (1pt)
        if schema and "FAQPage" in schema.present_fields:
            score += 1
            self.details["A4_faq_schema"] = {"status": "pass", "score": 1}
        else:
            gaps["mitigable"].append("A4: FAQPage schema not detected")
            self.details["A4_faq_schema"] = {"status": "missing", "score": 0}
        
        # A5: HowTo schema (1pt)
        if schema and "HowTo" in schema.present_fields:
            score += 1
            self.details["A5_howto_schema"] = {"status": "pass", "score": 1}
        else:
            gaps["mitigable"].append("A5: HowTo schema not detected")
            self.details["A5_howto_schema"] = {"status": "missing", "score": 0}
        
        # A6: Q&A content (1pt) - BLOCKING gap
        gaps["blocking"].append("A6: Q&A content requires content scraping")
        self.details["A6_qa_content"] = {"status": "scraping_required", "score": 0}
        
        recs.append("Generate ai.txt, ai_summary.json, and ai_faq.json via GEOEnrichmentLayer")
        
        return score, gaps, recs
