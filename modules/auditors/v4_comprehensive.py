"""v4.0 Comprehensive Audit with API validation.

Integrates:
- Google Places API for GBP data validation
- Rich Results Test API for schema validation
- PageSpeed API for performance metrics
- Cross-validation between web scraping, APIs, and benchmarks

Usage:
    from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor
    
    auditor = V4ComprehensiveAuditor()
    result = auditor.audit("https://hotelvisperas.com")
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from modules.data_validation import CrossValidator, ConfidenceLevel
from modules.data_validation.external_apis import (
    RichResultsTestClient,
    PageSpeedClient,
)
from modules.scrapers.google_places_client import GooglePlacesClient, PlaceData
from modules.scrapers.google_travel_scraper import GoogleTravelScraper
from modules.scrapers.serpapi_client import SerpAPIClient
from modules.analyzers.competitor_analyzer import CompetitorAnalyzer
from data_validation.metadata_validator import MetadataValidator
from modules.utils.http_client import HttpClient
from modules.auditors.ai_crawler_auditor import AICrawlerAuditor
from modules.auditors.citability_scorer import CitabilityScorer, CitabilityScore
from modules.auditors.ia_readiness_calculator import IAReadinessCalculator, IAReadinessReport
from modules.auditors.seo_elements_detector import SEOElementsDetector, SEOElementsResult
from modules.auditors.aeo_snippet_tracker import AEOSnippetReport, AEOSnippetTracker


logger = logging.getLogger(__name__)


@dataclass
class SchemaAuditResult:
    """Result of schema validation audit."""
    hotel_schema_detected: bool
    hotel_schema_valid: bool
    hotel_confidence: str
    faq_schema_detected: bool
    faq_schema_valid: bool
    faq_confidence: str
    org_schema_detected: bool
    total_schemas: int
    errors: List[Dict] = field(default_factory=list)
    warnings: List[Dict] = field(default_factory=list)
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class GBPApiResult:
    """Result from Google Places API validation."""
    place_found: bool
    place_id: Optional[str]
    name: str
    rating: float
    reviews: int
    photos: int
    phone: Optional[str]
    website: Optional[str]
    address: str
    geo_score: int
    geo_score_breakdown: Dict[str, float]
    confidence: str
    data_source: str = "places_api"
    error_type: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class PerformanceResult:
    """Result from PageSpeed API."""
    has_field_data: bool
    mobile_score: Optional[int]
    desktop_score: Optional[int]
    lcp: Optional[float]
    fid: Optional[int]
    cls: Optional[float]
    status: str
    message: str


@dataclass
class CrossValidationResult:
    """Result of cross-validation between sources."""
    whatsapp_status: str
    phone_web: Optional[str]
    phone_gbp: Optional[str]
    adr_status: str
    adr_web: Optional[float]
    adr_benchmark: Optional[float]
    conflicts: List[Dict] = field(default_factory=list)
    validated_fields: Dict[str, Any] = field(default_factory=dict)
    whatsapp_html_detected: bool = False  # True si scraper detecto boton WhatsApp en HTML

    # NUEVOS CAMPOS (GAP-IAO-01-02-B):
    address_status: str = "unknown"
    email_status: str = "unknown"
    address_web: Optional[str] = None
    address_gbp: Optional[str] = None


@dataclass
class MetadataAuditResult:
    """Result of metadata validation audit."""
    cms_detected: str
    has_default_title: bool
    title: str
    has_default_description: bool
    description: str
    has_issues: bool
    issues: List[Dict] = field(default_factory=list)
    confidence: str = "estimated"


@dataclass
class AICrawlerAuditResult:
    """Result of AI crawler access audit."""
    robots_exists: bool
    overall_score: float
    allowed_crawlers: List[str] = field(default_factory=list)
    blocked_crawlers: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


@dataclass
class CitabilityResult:
    """Result of citability audit - ADVISORY, not used for gates."""
    overall_score: float
    blocks_analyzed: int
    high_citability_blocks: int
    recommendations: List[str]
    confidence: str = "ADVISORY"


@dataclass
class V4AuditResult:
    """Complete v4.0 audit result."""
    url: str
    hotel_name: str
    timestamp: str
    
    # Schema audit
    schema: SchemaAuditResult
    
    # GBP data (required)
    gbp: GBPApiResult
    
    # Performance
    performance: PerformanceResult
    
    # Cross-validation
    validation: CrossValidationResult
    
    # Overall assessment
    overall_confidence: str
    critical_issues: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)
    competitors: List[Dict] = field(default_factory=list)
    
    # Metadata audit (optional, after required fields)
    metadata: Optional[MetadataAuditResult] = None
    
    # AI Crawler audit (optional, advisory)
    ai_crawlers: Optional[AICrawlerAuditResult] = None
    
    # Citability audit (optional, advisory)
    citability: Optional[CitabilityResult] = None
    
    # IA Readiness (optional, advisory)
    ia_readiness: Optional[IAReadinessReport] = None
    
    # SEO Elements (GAP-IAO-01-02-B)
    seo_elements: Optional[SEOElementsResult] = None

    # AEO Snippet Tracker (FASE-B): featured snippet measurement via SerpAPI
    aeo_snippets: Optional[AEOSnippetReport] = None
    
    # Execution trace
    executed_validators: List[str] = field(default_factory=list)
    skipped_validators: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        result = {
            "url": self.url,
            "hotel_name": self.hotel_name,
            "timestamp": self.timestamp,
            "schema": {
                "hotel_schema_detected": self.schema.hotel_schema_detected,
                "hotel_schema_valid": self.schema.hotel_schema_valid,
                "hotel_confidence": self.schema.hotel_confidence,
                "faq_schema_detected": self.schema.faq_schema_detected,
                "faq_schema_valid": self.schema.faq_schema_valid,
                "faq_confidence": self.schema.faq_confidence,
                "org_schema_detected": self.schema.org_schema_detected,
                "total_schemas": self.schema.total_schemas,
                "errors": self.schema.errors,
                "warnings": self.schema.warnings,
                "properties": self.schema.properties,
            },
            "gbp": {
                "place_found": self.gbp.place_found,
                "place_id": self.gbp.place_id,
                "name": self.gbp.name,
                "rating": self.gbp.rating,
                "reviews": self.gbp.reviews,
                "photos": self.gbp.photos,
                "phone": self.gbp.phone,
                "website": self.gbp.website,
                "address": self.gbp.address,
                "geo_score": self.gbp.geo_score,
                "geo_score_breakdown": self.gbp.geo_score_breakdown,
                "confidence": self.gbp.confidence,
                "error_type": self.gbp.error_type,
                "error_message": self.gbp.error_message,
            },
            "performance": {
                "has_field_data": self.performance.has_field_data,
                "mobile_score": self.performance.mobile_score,
                "desktop_score": self.performance.desktop_score,
                "lcp": self.performance.lcp,
                "fid": self.performance.fid,
                "cls": self.performance.cls,
                "status": self.performance.status,
                "message": self.performance.message,
            },
            "validation": {
                "whatsapp_status": self.validation.whatsapp_status,
                "phone_web": self.validation.phone_web,
                "phone_gbp": self.validation.phone_gbp,
                "adr_status": self.validation.adr_status,
                "conflicts": self.validation.conflicts,
            },
            "overall": {
                "confidence": self.overall_confidence,
                "critical_issues": self.critical_issues,
                "recommendations": self.recommendations,
            },
            "competitors": self.competitors,
            "execution_trace": {
                "executed": self.executed_validators,
                "skipped": self.skipped_validators,
            },
        }
        
        if self.metadata:
            result["metadata"] = {
                "cms_detected": self.metadata.cms_detected,
                "has_default_title": self.metadata.has_default_title,
                "title": self.metadata.title,
                "has_default_description": self.metadata.has_default_description,
                "description": self.metadata.description,
                "has_issues": self.metadata.has_issues,
                "issues": self.metadata.issues,
                "confidence": self.metadata.confidence,
            }
        
        if self.ai_crawlers:
            result["ai_crawlers"] = {
                "robots_exists": self.ai_crawlers.robots_exists,
                "overall_score": self.ai_crawlers.overall_score,
                "allowed_crawlers": self.ai_crawlers.allowed_crawlers,
                "blocked_crawlers": self.ai_crawlers.blocked_crawlers,
                "recommendations": self.ai_crawlers.recommendations,
            }
        
        if self.citability:
            result["citability"] = {
                "overall_score": self.citability.overall_score,
                "blocks_analyzed": self.citability.blocks_analyzed,
                "high_citability_blocks": self.citability.high_citability_blocks,
                "recommendations": self.citability.recommendations,
                "confidence": self.citability.confidence,
            }
        
        if self.ia_readiness:
            result["ia_readiness"] = {
                "overall_score": self.ia_readiness.overall_score,
                "components": self.ia_readiness.components,
                "status": self.ia_readiness.status,
                "actionable_items": self.ia_readiness.actionable_items,
            }
        
        if self.seo_elements:
            result["seo_elements"] = {
                "open_graph": self.seo_elements.open_graph,
                "imagenes_alt": self.seo_elements.imagenes_alt,
                "redes_activas": self.seo_elements.redes_activas,
                "confidence": self.seo_elements.confidence,
                "notes": self.seo_elements.notes,
                "open_graph_tags": self.seo_elements.open_graph_tags,
                "images_without_alt": self.seo_elements.images_without_alt,
                "social_links_found": self.seo_elements.social_links_found,
            }

        if self.aeo_snippets:
            result["aeo_snippets"] = {
                "queries_tested": self.aeo_snippets.queries_tested,
                "snippets_captured": self.aeo_snippets.snippets_captured,
                "snippets_competitor": self.aeo_snippets.snippets_competitor,
                "paa_presence": self.aeo_snippets.paa_presence,
                "snippet_score": self.aeo_snippets.snippet_score,
                "source": self.aeo_snippets.source,
                "timestamp": self.aeo_snippets.timestamp,
            }

        return result


class V4ComprehensiveAuditor:
    """v4.0 Comprehensive Auditor with API integrations.
    
    Performs:
    1. Schema validation via Rich Results Test API
    2. GBP data retrieval via Google Places API
    3. Performance metrics via PageSpeed API
    4. Cross-validation between all sources
    
    Example:
        auditor = V4ComprehensiveAuditor()
        result = auditor.audit("https://hotelvisperas.com")
        print(f"Hotel: {result.hotel_name}")
        print(f"GBP Geo Score: {result.gbp.geo_score}/100")
        print(f"Schema Confidence: {result.schema.hotel_confidence}")
    """
    
    def __init__(
        self,
        places_client: Optional[GooglePlacesClient] = None,
        rich_results_client: Optional[RichResultsTestClient] = None,
        pagespeed_client: Optional[PageSpeedClient] = None,
    ):
        """Initialize the v4.0 comprehensive auditor.
        
        Args:
            places_client: Google Places API client (auto-created if None)
            rich_results_client: Rich Results Test client (auto-created if None)
            pagespeed_client: PageSpeed API client (auto-created if None)
        """
        self.places = places_client or GooglePlacesClient()
        self.rich_results = rich_results_client or RichResultsTestClient()
        self.pagespeed = pagespeed_client
        self.cross_validator = CrossValidator()
        self.competitor_analyzer = CompetitorAnalyzer()
    
    def _validate_html_integrity(self, html: str, url: str) -> bool:
        """
        Valida que el HTML sea legible y no basura binaria/comprimida.

        Detecta: Brotli sin decodificar, binario crudo, paginas de error,
        respuestas vacias, JavaScript-only shells sin contenido.

        Returns:
            True si el HTML es valido para analisis, False si es ilegible.
        """
        if not html or len(html) < 200:
            logger.warning(f"HTML too short or empty for {url} ({len(html) if html else 0} chars)")
            return False

        html_lower = html.lower()

        # Check 1: Debe tener estructura HTML basica
        has_structure = any(tag in html_lower for tag in ['<html', '<head', '<body', '<!doctype', '<div'])
        if not has_structure:
            logger.error(
                f"HTML integrity failed for {url}: no HTML structure found. "
                f"First 100 chars: {repr(html[:100])}"
            )
            return False

        # Check 2: No debe tener alto ratio de caracteres no imprimibles (binario)
        sample = html[:2000]
        non_printable = sum(1 for c in sample if ord(c) < 32 and c not in '\n\r\t')
        if len(sample) > 0 and non_printable / len(sample) > 0.15:
            logger.error(
                f"HTML integrity failed for {url}: {non_printable} non-printable chars in first 2000 "
                f"({non_printable/len(sample)*100:.1f}%). Likely binary/compressed data."
            )
            return False

        return True

    def audit(self, url: str, hotel_name: Optional[str] = None) -> V4AuditResult:
        """Run comprehensive v4.0 audit on a URL.
        
        Args:
            url: Hotel website URL
            hotel_name: Optional hotel name for Places API search
            
        Returns:
            V4AuditResult with all audit data
        """
        print(f"\n{'='*60}")
        print(f"V4.0 COMPREHENSIVE AUDIT")
        print(f"{'='*60}")
        print(f"URL: {url}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Step 1: Schema validation
        print("[1/5] Validating structured data schemas...")
        schema_result = self._audit_schemas(url)
        print(f"      Found {schema_result.total_schemas} schemas")
        print(f"      Hotel: {schema_result.hotel_confidence}")
        print(f"      FAQ: {schema_result.faq_confidence}")
        
        # Fetch HTML ONCE for metadata, citability, and SEO elements
        # (avoids redundant HTTP requests that may return different HTML for SPA sites)
        http_client = HttpClient()
        html_response, _ = http_client.get(url)
        page_html = html_response.text if html_response and html_response.text else ""
        if page_html and not self._validate_html_integrity(page_html, url):
            logger.error(f"HTML response for {url} is corrupted/unreadable — falling back to empty")
            page_html = ""
        elif not page_html:
            logger.warning(f"Empty HTML response for {url}")
        
        # Step 1.5: Metadata validation
        print("\n[1.5/5] Validating metadata (CMS defaults)...")
        metadata_result = self._audit_metadata(url, html_content=page_html)
        if metadata_result:
            print(f"      CMS Detected: {metadata_result.cms_detected}")
            print(f"      Default Title: {metadata_result.has_default_title}")
            print(f"      Default Description: {metadata_result.has_default_description}")
            if metadata_result.has_issues:
                print(f"      ⚠️  {len(metadata_result.issues)} metadata issues")
        else:
            print("      Metadata not available")
        
        # Step 2: GBP data via Places API
        print("\n[2/5] Retrieving GBP data via Places API...")
        gbp_result = self._audit_gbp(url, hotel_name, schema_result.properties)
        if gbp_result.place_found:
            print(f"      Found: {gbp_result.name}")
            print(f"      Rating: {gbp_result.rating}/5 ({gbp_result.reviews} reviews)")
            print(f"      Geo Score: {gbp_result.geo_score}/100")
        else:
            print("      Place not found in Google Places")
        
        # Step 2.5: Competitor analysis
        print("\n[2.5/5] Analyzing nearby competitors...")
        competitors = self._audit_competitors(gbp_result)
        if competitors:
            print(f"      Found {len(competitors)} competitors")
        
        # Step 2.7: AI Crawler access (ADVISORY)
        print("\n[2.7/5] Auditing AI crawler access...")
        ai_crawler_result = self._audit_ai_crawlers(url)
        print(f"      Score: {ai_crawler_result.overall_score:.2f}/1.00")
        print(f"      Robots.txt: {'Found' if ai_crawler_result.robots_exists else 'Not found'}")
        if ai_crawler_result.blocked_crawlers:
            print(f"      Blocked: {len(ai_crawler_result.blocked_crawlers)} crawlers")
        
        # Step 2.8: Citability audit (ADVISORY)
        print("\n[2.8/5] Analyzing content citability...")
        citability_result = None
        if page_html:
            citability_result = self._audit_citability(url, page_html)
            print(f"      Score: {citability_result.overall_score:.1f}/100")
            print(f"      [ADVISORY] Blocks analyzed: {citability_result.blocks_analyzed}")
        else:
            print("      HTML content not available")
        
        # Step 2.9: SEO Elements detection (GAP-IAO-01-02-B)
        print("\n[2.9/5] Detecting SEO elements...")
        seo_elements = self._run_seo_elements_audit(page_html, url)
        print(f"      Open Graph: {seo_elements.open_graph}")
        print(f"      Images with Alt: {seo_elements.imagenes_alt}")
        print(f"      Active Social: {seo_elements.redes_activas}")
        
        # Defensive logging: diagnose OG false negatives
        if seo_elements and not seo_elements.open_graph:
            html_snippet = page_html[:500] if page_html else "EMPTY"
            logger.warning(f"OG not detected for {url}. HTML snippet: {html_snippet}")

        # Step 2.10: AEO Snippet Tracker via SerpAPI (FASE-B)
        # Nota: 5 queries por hotel, free tier 100/mes
        print("\n[2.10/5] Checking featured snippets (AEO)... [ADVISORY]")
        aeo_snippet_report = None
        try:
            snippet_tracker = AEOSnippetTracker()
            aeo_snippet_report = snippet_tracker.check_snippets(
                hotel_name=final_hotel_name,
                hotel_url=url,
                location=gbp_result.address if gbp_result.place_found else "",
                landmark="",
            )
            print(f"      Source: {aeo_snippet_report.source}")
            if aeo_snippet_report.source == "serpapi":
                print(f"      Snippets captured: {aeo_snippet_report.snippets_captured}/{aeo_snippet_report.queries_tested}")
                print(f"      PAA presence: {aeo_snippet_report.paa_presence}")
                print(f"      Snippet score: {aeo_snippet_report.snippet_score}/100")
            else:
                print(f"      [STUB] Sin API key SerpAPI - medicion no disponible")
        except Exception as e:
            logger.warning(f"AEO Snippet Tracker failed: {e}")
            print(f"      [ADVISORY] Snippet tracker no disponible: {e}")
        
        # Step 3: Performance metrics
        print("\n[3/5] Checking performance metrics...")
        perf_result = self._audit_performance(url)
        if perf_result.has_field_data:
            print(f"      Mobile Score: {perf_result.mobile_score}/100")
            print(f"      Desktop Score: {perf_result.desktop_score}/100")
        else:
            print(f"      Status: {perf_result.status}")
            print(f"      {perf_result.message}")
        
        # Step 4: Cross-validation
        print("\n[4/5] Running cross-validation...")
        whatsapp_html_detected = self._detect_whatsapp_from_html(page_html)
        if whatsapp_html_detected:
            print("      WhatsApp button detected in HTML")
        validation_result = self._run_cross_validation(url, schema_result, gbp_result, whatsapp_html_detected)
        print(f"      WhatsApp: {validation_result.whatsapp_status}")
        print(f"      ADR: {validation_result.adr_status}")
        if validation_result.conflicts:
            print(f"      ⚠️  {len(validation_result.conflicts)} conflicts detected")
        
        # Step 5: Overall assessment
        print("\n[5/5] Calculating overall assessment...")
        overall_confidence = self._calculate_overall_confidence(
            schema_result, gbp_result, validation_result
        )
        critical_issues = self._identify_critical_issues(
            schema_result, gbp_result, perf_result, validation_result
        )
        
        # Add metadata issues AFTER critical issues are identified
        if metadata_result and metadata_result.has_issues:
            for issue in metadata_result.issues:
                critical_issues.append(f"Metadata: {issue.get('message', 'Issue detected')}")
        
        recommendations = self._generate_recommendations(
            schema_result, gbp_result, perf_result, validation_result
        )
        
        # Determine hotel name
        final_hotel_name = (
            hotel_name or 
            gbp_result.name or 
            schema_result.properties.get("name") or 
            "Unknown Hotel"
        )
        
        executed_validators = [
            "schema_validation",
            "metadata_validation",
            "gbp_api",
            "competitor_analysis",
            "ai_crawler_audit",
            "citability_audit",
            "seo_elements_detection",
            "pagespeed_api",
            "cross_validation",
            "aeo_snippet_tracker",
        ]

        skipped_validators = []

        if not metadata_result:
            skipped_validators.append("metadata_validation")
        
        if not gbp_result.place_found:
            skipped_validators.append("gbp_api")
        
        if not perf_result.has_field_data:
            skipped_validators.append("pagespeed_api")
        
        # Calculate IA Readiness (ADVISORY)
        ia_readiness_result = None
        if citability_result:
            ia_readiness_result = self._calculate_ia_readiness(
                schema_result, ai_crawler_result, citability_result, url
            )
            print(f"\n[IA Readiness] Status: {ia_readiness_result.status}")
        
        result = V4AuditResult(
            url=url,
            hotel_name=final_hotel_name,
            timestamp=datetime.now().isoformat(),
            schema=schema_result,
            metadata=metadata_result,
            gbp=gbp_result,
            performance=perf_result,
            validation=validation_result,
            overall_confidence=overall_confidence,
            critical_issues=critical_issues,
            recommendations=recommendations,
            competitors=competitors,
            ai_crawlers=ai_crawler_result,
            citability=citability_result,
            ia_readiness=ia_readiness_result,
            seo_elements=seo_elements,
            aeo_snippets=aeo_snippet_report,
            executed_validators=executed_validators,
            skipped_validators=skipped_validators,
        )
        
        print(f"\n{'='*60}")
        print(f"AUDIT COMPLETE - Overall Confidence: {overall_confidence}")
        print(f"{'='*60}")
        
        return result
    
    def _audit_schemas(self, url: str) -> SchemaAuditResult:
        """Audit structured data schemas on the page."""
        report = self.rich_results.get_hotel_schema_report(url)
        faq_report = self.rich_results.get_faq_schema_report(url)
        
        return SchemaAuditResult(
            hotel_schema_detected=report["has_hotel_schema"],
            hotel_schema_valid=report["schema_valid"],
            hotel_confidence=report["confidence"],
            faq_schema_detected=faq_report["has_faq_schema"],
            faq_schema_valid=faq_report["schema_valid"],
            faq_confidence=faq_report["confidence"],
            org_schema_detected="Organization" in report.get("all_schemas", []),
            total_schemas=len(report.get("all_schemas", [])),
            errors=report.get("errors", []),
            warnings=report.get("warnings", []),
            properties=report.get("properties", {}),
        )
    
    def _audit_metadata(self, url: str, html_content: Optional[str] = None) -> Optional[MetadataAuditResult]:
        """Audit HTML metadata for default CMS values.
        
        Args:
            url: Hotel website URL
            html_content: Pre-fetched HTML (avoids redundant HTTP request).
                         If None, fetches internally (legacy behavior).
        """
        try:
            if html_content is None:
                http_client = HttpClient()
                response, _ = http_client.get(url)
                
                if not response or not response.text:
                    return None
                
                html_content = response.text
            validator = MetadataValidator()
            
            cms_detected = validator.detect_cms(html_content)
            claims = validator.analyze(html_content, url)
            
            title_claim = validator.validate_title(validator._extract_title(
                __import__('bs4').BeautifulSoup(html_content, "html.parser")
            ))
            description_claim = validator.validate_description(validator._extract_description(
                __import__('bs4').BeautifulSoup(html_content, "html.parser")
            ))
            
            title = ""
            description = ""
            if title_claim:
                title = title_claim.evidence_excerpt
            if description_claim:
                description = description_claim.evidence_excerpt
            
            issues = []
            has_default_title = False
            has_default_description = False
            
            if title_claim and title_claim.severity.value in ["critical", "high"]:
                has_default_title = True
                issues.append({
                    "type": "default_title",
                    "severity": title_claim.severity.value,
                    "message": title_claim.message
                })
            
            if description_claim:
                has_default_description = True
                issues.append({
                    "type": "default_description",
                    "severity": description_claim.severity.value,
                    "message": description_claim.message
                })
            
            return MetadataAuditResult(
                cms_detected=cms_detected,
                has_default_title=has_default_title,
                title=title,
                has_default_description=has_default_description,
                description=description,
                has_issues=len(issues) > 0,
                issues=issues,
                confidence="estimated"
            )
        except Exception as e:
            return None
    
    def _audit_gbp(
        self, 
        url: str, 
        hotel_name: Optional[str],
        schema_props: Dict[str, Any]
    ) -> GBPApiResult:
        """Audit GBP data via Google Places API with fallback chain.
        
        FASE 11 Extension: Fallback chain: Places API (New) -> Google Travel -> SerpAPI -> schema_data
        """
        # Preferir schema_props name ya que es el nombre real del hotel desde el website
        search_name = schema_props.get("name") or hotel_name
        location = schema_props.get("address", "") or "Colombia"
        
        # FASE 11 Extension: Try Places API (New) first - tiene 200M+ places
        try:
            places_result = self._search_places_new(search_name, location)
            if places_result and places_result.place_found:
                logger.info(f"Places API (New) found: {search_name}")
                return GBPApiResult(
                    place_found=True,
                    place_id=places_result.place_id,
                    name=places_result.name,
                    rating=places_result.rating,
                    reviews=places_result.reviews,
                    photos=places_result.photos,
                    phone=places_result.phone,
                    website=places_result.website_url,
                    address=places_result.address,
                    geo_score=places_result.geo_score,
                    geo_score_breakdown=places_result.geo_score_formula,
                    confidence=ConfidenceLevel.VERIFIED.value,
                    data_source="places_api_new",
                    error_type=None,
                    error_message=None,
                )
        except Exception as e:
            logger.warning(f"Places API (New) failed: {e}")
        
        # Try Google Travel second
        try:
            travel_scraper = GoogleTravelScraper(timeout=15)
            travel_result = travel_scraper.scrape_hotel(search_name, location)
            
            if travel_result.get('found', False):
                travel_data = travel_result
                logger.info(f"Google Travel found: {search_name}")
                return GBPApiResult(
                    place_found=True,
                    place_id=travel_data.get('place_id'),
                    name=travel_data.get('name', search_name),
                    rating=float(travel_data.get('rating', 0.0)),
                    reviews=int(travel_data.get('reviews', 0)),
                    photos=int(travel_data.get('photos', 0)),
                    phone=travel_data.get('phone'),
                    website=travel_data.get('website', url),
                    address=travel_data.get('address', schema_props.get("address", "")),
                    geo_score=0,
                    geo_score_breakdown={},
                    confidence=ConfidenceLevel.VERIFIED.value,
                    data_source="google_travel",
                    error_type=None,
                    error_message=None,
                )
        except Exception as e:
            logger.warning(f"Google Travel fallback failed: {e}")
        
        # Try SerpAPI as third fallback
        try:
            serp_client = SerpAPIClient(timeout=20)
            if serp_client.is_available:
                serp_result = serp_client.search_hotel(search_name, location)
                
                if serp_result.get('found', False):
                    serp_data = serp_result
                    serp_stats = serp_client.get_usage_stats()
                    logger.info(f"SerpAPI found: {search_name} (used: {serp_stats['queries_used']}/{serp_stats['monthly_limit']})")
                    return GBPApiResult(
                        place_found=True,
                        place_id=serp_data.get('place_id'),
                        name=serp_data.get('name', search_name),
                        rating=float(serp_data.get('rating', 0.0)),
                        reviews=int(serp_data.get('reviews', 0)),
                        photos=int(serp_data.get('photos', 0)),
                        phone=serp_data.get('phone'),
                        website=serp_data.get('website', url),
                        address=serp_data.get('address', schema_props.get("address", "")),
                        geo_score=0,
                        geo_score_breakdown={},
                        confidence=ConfidenceLevel.VERIFIED.value,
                        data_source="serpapi",
                        error_type=None,
                        error_message=None,
                    )
                else:
                    logger.info(f"SerpAPI: {serp_result.get('error_message', 'Hotel not found')}")
            else:
                logger.info("SerpAPI not available (no API key)")
        except Exception as e:
            logger.warning(f"SerpAPI fallback failed: {e}")
        
        # Final fallback: schema data
        logger.info(f"Falling back to schema data for: {search_name}")
        return GBPApiResult(
            place_found=False,
            place_id=None,
            name=search_name or "Unknown",
            rating=0.0,
            reviews=0,
            photos=0,
            phone=schema_props.get("telephone"),
            website=url,
            address=schema_props.get("address", ""),
            geo_score=0,
            geo_score_breakdown={},
            confidence=ConfidenceLevel.ESTIMATED.value,
            data_source="schema_data",
            error_type="NO_PLACE_FOUND",
            error_message="Hotel not found in Places, Travel, or SerpAPI",
        )
    
    def _search_places_new(self, hotel_name: str, location: str) -> Optional['PlaceData']:
        """Busca hotel usando Google Places API (New).
        
        Args:
            hotel_name: Nombre del hotel
            location: Ubicacion
            
        Returns:
            PlaceData si se encuentra, None si no
        """
        if not self.places.is_available:
            logger.info("Places API (New) not available")
            return None
        
        try:
            import requests
            
            api_key = self.places.api_key
            url = "https://places.googleapis.com/v1/places:searchText"
            
            headers = {
                'Content-Type': 'application/json',
                'X-Goog-Api-Key': api_key,
                'X-Goog-FieldMask': 'places.id,places.displayName,places.rating,places.userRatingCount,places.formattedAddress,places.nationalPhoneNumber,places.websiteUri,places.photos'
            }
            
            query = f"{hotel_name}, {location}"
            data = {'textQuery': query}
            
            response = requests.post(url, headers=headers, json=data, timeout=20)
            
            if response.status_code != 200:
                logger.warning(f"Places API (New) returned {response.status_code}")
                return None
            
            result = response.json()
            places = result.get('places', [])
            
            if not places:
                return None
            
            # Tomar el primer resultado
            place = places[0]
            
            # Parsear datos
            name = place.get('displayName', {}).get('text', hotel_name)
            rating = place.get('rating', 0.0) or 0.0
            reviews = place.get('userRatingCount', 0) or 0
            address = place.get('formattedAddress', location)
            phone = place.get('nationalPhoneNumber')
            website = place.get('websiteUri')
            place_id = place.get('id')
            
            # Fotos
            photos = len(place.get('photos', [])) if place.get('photos') else 0
            
            # Calcular geo_score
            geo_breakdown = self.places.calculate_geo_score(
                rating=rating,
                reviews=reviews,
                photos=photos,
                has_hours=True,  # Asumimos que tiene horarios
                has_website=bool(website)
            )
            
            place_data = PlaceData(
                place_id=place_id,
                name=name,
                rating=rating,
                reviews=reviews,
                photos=photos,
                has_hours=True,
                has_website=bool(website),
                website_url=website,
                phone=phone,
                address=address,
                city="",
                lat=0.0,
                lng=0.0,
                geo_score=geo_breakdown.total,
                geo_score_formula={
                    'rating_score': geo_breakdown.rating_score,
                    'reviews_score': geo_breakdown.reviews_score,
                    'photos_score': geo_breakdown.photos_score,
                    'hours_score': geo_breakdown.hours_score,
                    'website_score': geo_breakdown.website_score,
                },
                data_source="places_api_new",
                fetched_at="",
                place_found=True
            )
            
            return place_data
            
        except Exception as e:
            logger.warning(f"Places API (New) search failed: {e}")
            return None

    def _audit_competitors(self, gbp_result: GBPApiResult) -> List[Dict]:
        """Analyze nearby competitors using CompetitorAnalyzer."""
        if not gbp_result.place_found or not gbp_result.geo_score:
            return []
        
        # We need coordinates to search - try to extract from address or use default
        # For now, return empty but structure is in place
        return self.competitor_analyzer.get_nearby_competitors(
            hotel_name=gbp_result.name,
            lat=0.0,  # TODO: Get from geocoding
            lng=0.0,  # TODO: Get from geocoding
            radius_km=15
        )
    
    def _audit_ai_crawlers(self, url: str) -> AICrawlerAuditResult:
        """Audit AI crawler access via robots.txt analysis.
        
        This is an ADVISORY check - does not block the audit.
        """
        try:
            auditor = AICrawlerAuditor()
            report = auditor.audit_robots_txt(url)
            
            return AICrawlerAuditResult(
                robots_exists=report.robots_exists,
                overall_score=report.overall_score,
                allowed_crawlers=[r.crawler_name for r in report.crawler_results if r.allowed],
                blocked_crawlers=[r.crawler_name for r in report.crawler_results if not r.allowed],
                recommendations=[r.recommendation for r in report.crawler_results if r.recommendation]
            )
        except Exception as e:
            return AICrawlerAuditResult(
                robots_exists=False,
                overall_score=0.0,
                allowed_crawlers=[],
                blocked_crawlers=[],
                recommendations=[f"AI crawler audit failed: {str(e)}"]
            )
    
    def _audit_citability(self, url: str, html_content: str) -> CitabilityResult:
        """Audit content citability - ADVISORY check."""
        try:
            scorer = CitabilityScorer()
            score = scorer.score_content(html_content, url)
            
            return CitabilityResult(
                overall_score=score.overall_score,
                blocks_analyzed=score.blocks_analyzed,
                high_citability_blocks=score.high_citability_blocks,
                recommendations=score.recommendations,
                confidence="ADVISORY"
            )
        except Exception as e:
            return CitabilityResult(
                overall_score=0.0,
                blocks_analyzed=0,
                high_citability_blocks=0,
                recommendations=[f"Citability audit failed: {str(e)}"],
                confidence="ADVISORY"
            )
    
    def _calculate_ia_readiness(
        self,
        schema_result: SchemaAuditResult,
        ai_crawler_result: AICrawlerAuditResult,
        citability_result: CitabilityResult,
        url: str,
    ) -> IAReadinessReport:
        """Calculate IA readiness report - ADVISORY check."""
        try:
            calculator = IAReadinessCalculator()
            
            schema_coverage = schema_result.total_schemas / max(1, 5)
            crawler_score = ai_crawler_result.overall_score * 100
            citability_score = citability_result.overall_score
            
            http_client = HttpClient()
            has_llmstxt = False
            try:
                llms_txt_response, _ = http_client.get(f"{url.rstrip('/')}/llms.txt")
                has_llmstxt = llms_txt_response and llms_txt_response.status_code == 200
            except:
                pass
            
            brand_score = 50.0
            
            return calculator.calculate(
                schema_coverage=schema_coverage,
                crawler_score=crawler_score,
                citability_score=citability_score,
                has_llmstxt=has_llmstxt,
                brand_score=brand_score
            )
        except Exception as e:
            return IAReadinessReport(
                overall_score=0.0,
                components={},
                status="Error",
                actionable_items=[f"IA readiness calculation failed: {str(e)}"]
            )

    def _run_seo_elements_audit(self, html: str, url: str) -> SEOElementsResult:
        """Run SEO elements detection."""
        detector = SEOElementsDetector()
        return detector.detect(html, url)

    def _check_ssl(self, url: str) -> bool:
        """
        SSL detection is trivial - just check URL scheme.

        Returns:
            True if URL uses https://, False otherwise.
        """
        return url.startswith("https://") if url else False

    def _es_nap_consistente(self, audit_result: 'V4AuditResult') -> bool:
        """NAP es consistente si WhatsApp Y dirección Y email están verificados."""
        validation = audit_result.validation

        # WhatsApp verificado
        whatsapp_ok = (
            getattr(validation, 'whatsapp_status', None) == ConfidenceLevel.VERIFIED.value
        )

        # Dirección verificada (si existe el campo)
        address_status = getattr(validation, 'address_status', 'unknown')
        address_ok = address_status == ConfidenceLevel.VERIFIED.value

        # Email verificado (si existe el campo)
        email_status = getattr(validation, 'email_status', 'unknown')
        email_ok = email_status in [ConfidenceLevel.VERIFIED.value, ConfidenceLevel.ESTIMATED.value]

        # NAP completo = WhatsApp + Address (email es bonus)
        return whatsapp_ok and address_ok

    def _audit_performance(self, url: str) -> PerformanceResult:
        """Audit performance via PageSpeed API."""
        if not self.pagespeed:
            # Try to initialize from environment
            try:
                self.pagespeed = PageSpeedClient()
            except ValueError:
                # No API key configured
                return PerformanceResult(
                    has_field_data=False,
                    mobile_score=None,
                    desktop_score=None,
                    lcp=None,
                    fid=None,
                    cls=None,
                    status="API_NOT_CONFIGURED",
                    message="PageSpeed API key not configured",
                )
        
        try:
            mobile_result = self.pagespeed.analyze_url(url, device="mobile")
            desktop_result = self.pagespeed.analyze_url(url, device="desktop")
            
            return PerformanceResult(
                has_field_data=mobile_result.has_field_data,
                mobile_score=mobile_result.performance_score,
                desktop_score=desktop_result.performance_score,
                lcp=mobile_result.lcp,
                fid=mobile_result.fid,
                cls=mobile_result.cls,
                status=mobile_result.status,
                message=mobile_result.message,
            )
        except Exception as e:
            return PerformanceResult(
                has_field_data=False,
                mobile_score=None,
                desktop_score=None,
                lcp=None,
                fid=None,
                cls=None,
                status="ERROR",
                message=str(e),
            )
    
    def _detect_whatsapp_from_html(self, html: str) -> bool:
        """Detect WhatsApp button/link presence in raw HTML.

        Searches for common WhatsApp patterns: wa.me, api.whatsapp.com,
        web.whatsapp.com, whatsapp:// protocol, and floating button classes.

        Args:
            html: Raw HTML content of the page.

        Returns:
            True if WhatsApp link/button detected in HTML.
        """
        if not html:
            return False
        import re
        whatsapp_patterns = [
            # Direct WhatsApp links
            r'wa\.me/',
            r'api\.whatsapp\.com',
            r'web\.whatsapp\.com',
            r'whatsapp://',
            r'whatsapp\.com/send',
            r'class="[^"]*whatsapp[^"]*"',  # CSS classes like "whatsapp-button"
            r'id="[^"]*whatsapp[^"]*"',      # IDs like "whatsapp-float"
            # WordPress WhatsApp plugins (top 3: 1M+ combined installs)
            r'joinchat',                      # Joinchat/creame-whatsapp-me (500K+)
            r'creame-whatsapp-me',           # Plugin path variant
            r'ht-ctc',                        # Click to Chat for WhatsApp (200K+)
            r'click-to-chat',                 # Click to Chat variant
            r'wa-chat',                       # WA Chat widgets
            r'data-settings.*telephone',      # Joinchat stores number in data-settings JSON
        ]
        html_lower = html.lower()
        for pattern in whatsapp_patterns:
            if re.search(pattern, html_lower):
                return True
        return False

    def _run_cross_validation(
        self,
        url: str,
        schema: SchemaAuditResult,
        gbp: GBPApiResult,
        whatsapp_html_detected: bool = False,
    ) -> CrossValidationResult:
        """Run cross-validation between data sources."""
        # Validate WhatsApp/phone
        web_phone = schema.properties.get("telephone")
        gbp_phone = gbp.phone
        
        whatsapp_dp = self.cross_validator.validate_whatsapp(
            web_value=web_phone,
            gbp_value=gbp_phone,
        )
        
        # Validate ADR (if available)
        adr_web = None
        price_range = schema.properties.get("priceRange")
        if price_range:
            # Try to extract numeric value from price range
            try:
                # Handle formats like "$100-200" or "COP 400000"
                import re
                numbers = re.findall(r'\d+', str(price_range))
                if numbers:
                    adr_web = float(numbers[0])
            except (ValueError, TypeError):
                pass
        
        adr_dp = self.cross_validator.validate_adr(
            scraped_price=str(adr_web) if adr_web else None,
        )
        
        # Get conflicts
        conflicts = self.cross_validator.get_conflict_report()

        # NUEVO: Validate address
        web_address = schema.properties.get("address")
        gbp_address = gbp.address
        address_dp = self.cross_validator.validate_address(web_address, gbp_address)

        # NUEVO: Validate email
        web_email = schema.properties.get("email")
        gbp_email = None  # GBP no typically provides email
        email_dp = self.cross_validator.validate_email(web_email, gbp_email)

        return CrossValidationResult(
            whatsapp_status=whatsapp_dp.confidence.value if whatsapp_dp else ConfidenceLevel.UNKNOWN.value,
            phone_web=web_phone,
            phone_gbp=gbp_phone,
            adr_status=adr_dp.confidence.value if adr_dp else ConfidenceLevel.UNKNOWN.value,
            adr_web=adr_web,
            adr_benchmark=None,
            conflicts=conflicts,
            validated_fields={
                "whatsapp": whatsapp_dp.to_dict() if whatsapp_dp else None,
                "adr": adr_dp.to_dict() if adr_dp else None,
                "address": address_dp.to_dict() if address_dp else None,
                "email": email_dp.to_dict() if email_dp else None,
            },
            # NUEVOS CAMPOS:
            address_status=address_dp.confidence.value if address_dp else "unknown",
            email_status=email_dp.confidence.value if email_dp else "unknown",
            address_web=web_address,
            address_gbp=gbp_address,
            whatsapp_html_detected=whatsapp_html_detected,
        )
    
    def _calculate_overall_confidence(
        self,
        schema: SchemaAuditResult,
        gbp: GBPApiResult,
        validation: CrossValidationResult,
    ) -> str:
        """Calculate overall confidence level."""
        scores = []
        
        # Schema confidence
        if schema.hotel_confidence == ConfidenceLevel.VERIFIED.value:
            scores.append(1.0)
        elif schema.hotel_confidence == ConfidenceLevel.ESTIMATED.value:
            scores.append(0.6)
        else:
            scores.append(0.2)
        
        # GBP confidence
        if gbp.confidence == ConfidenceLevel.VERIFIED.value:
            scores.append(1.0)
        elif gbp.confidence == ConfidenceLevel.ESTIMATED.value:
            scores.append(0.6)
        else:
            scores.append(0.2)
        
        # Validation confidence
        if validation.whatsapp_status == ConfidenceLevel.VERIFIED.value:
            scores.append(1.0)
        elif validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
            scores.append(0.3)
        else:
            scores.append(0.5)
        
        avg_score = sum(scores) / len(scores)
        
        if avg_score >= 0.8:
            return ConfidenceLevel.VERIFIED.value
        elif avg_score >= 0.5:
            return ConfidenceLevel.ESTIMATED.value
        else:
            return ConfidenceLevel.UNKNOWN.value
    
    def _identify_critical_issues(
        self,
        schema: SchemaAuditResult,
        gbp: GBPApiResult,
        perf: PerformanceResult,
        validation: CrossValidationResult,
    ) -> List[str]:
        """Identify critical issues from audit."""
        issues = []
        
        if not schema.hotel_schema_detected:
            issues.append("No Hotel schema detected - critical for SEO")
        
        if schema.hotel_schema_detected and not schema.hotel_schema_valid:
            issues.append("Hotel schema has validation errors")
        
        if validation.whatsapp_status == ConfidenceLevel.CONFLICT.value:
            issues.append("WhatsApp number conflict between sources")
        
        if gbp.geo_score < 50:
            issues.append(f"Low GBP geo_score ({gbp.geo_score}/100) - optimization needed")
        
        if perf.has_field_data and perf.mobile_score and perf.mobile_score < 50:
            issues.append(f"Poor mobile performance ({perf.mobile_score}/100)")
        
        return issues
    
    def _generate_recommendations(
        self,
        schema: SchemaAuditResult,
        gbp: GBPApiResult,
        perf: PerformanceResult,
        validation: CrossValidationResult,
    ) -> List[str]:
        """Generate recommendations based on audit."""
        recs = []
        
        if not schema.hotel_schema_detected:
            recs.append("Implement Hotel schema markup for better search visibility")
        elif schema.warnings:
            recs.append(f"Fix {len(schema.warnings)} schema warnings")
        
        if not schema.faq_schema_detected:
            recs.append("Add FAQPage schema to capture rich snippets")
        
        if gbp.photos < 20:
            recs.append(f"Add more photos to GBP (current: {gbp.photos}, target: 40+)")
        
        if gbp.reviews < 50:
            recs.append(f"Encourage more reviews (current: {gbp.reviews}, target: 100+)")
        
        if not perf.has_field_data:
            recs.append("No Core Web Vitals data - site may be new or low traffic")
        elif perf.mobile_score and perf.mobile_score < 70:
            recs.append("Optimize mobile performance for better rankings")
        
        return recs
    
    def save_report(self, result: V4AuditResult, output_path: Path) -> None:
        """Save audit report to JSON file.
        
        Args:
            result: Audit result to save
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result.to_dict(), f, indent=2, ensure_ascii=False)
        
        print(f"\nReport saved to: {output_path}")


# Singleton instance for reuse
_auditor_instance: Optional[V4ComprehensiveAuditor] = None


def get_v4_auditor() -> V4ComprehensiveAuditor:
    """Get singleton instance of v4.0 comprehensive auditor."""
    global _auditor_instance
    if _auditor_instance is None:
        _auditor_instance = V4ComprehensiveAuditor()
    return _auditor_instance
