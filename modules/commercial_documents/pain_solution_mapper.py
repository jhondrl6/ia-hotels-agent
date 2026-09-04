"""
Pain to Solution Mapper for Commercial Documents v4.0.

Maps detected problems to specific assets/solutions based on
validation confidence and availability.
"""

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from .data_structures import (
    V4AuditResult,
    ValidationSummary,
    AssetSpec,
    ConfidenceLevel
)

logger = logging.getLogger(__name__)


@dataclass
class Pain:
    """Represents a detected problem/pain point."""
    id: str
    name: str
    description: str
    severity: str  # "critical", "high", "medium", "low"
    detected_by: str  # "schema", "gbp", "performance", "validation"
    confidence: float
    additional_data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Solution:
    """Maps a pain to a specific solution/asset."""
    pain_id: str
    asset_type: str
    asset_name: str
    description: str
    confidence_required: float
    validation_fields: List[str]
    estimated_impact: str  # "high", "medium", "low"
    priority: int = 2  # 1=P1, 2=P2, 3=P3
    # ROICR FASE-1: semantic validation result
    # IMPLEMENT = normal, AUDIT_ONLY = skipped_existing, BLOCKED = hallucination
    semantic_status: str = "IMPLEMENT"
    semantic_blocked_reason: Optional[str] = None
    migration_target: Optional[str] = None  # redirect asset for deprecated/llmstxt


class PainSolutionMapper:
    """
    Maps problems identified during audit to specific assets.
    
    Maintains a static mapping of common problems to their solutions,
    with confidence requirements for each.
    """
    
    PAIN_SOLUTION_MAP = {
        "no_whatsapp_visible": {
            "assets": ["whatsapp_button"],
            "confidence_required": 0.9,
            "priority": 1,
            "validation_fields": ["whatsapp_number"],
            "estimated_impact": "high",
            "name": "Sin WhatsApp Visible",
            "description": "No se detecta botón o enlace de WhatsApp en la web"
        },
        "whatsapp_conflict": {
            "assets": ["whatsapp_button", "whatsapp_conflict_guide"],
            "confidence_required": 0.5,
            "priority": 1,
            "validation_fields": ["whatsapp_number"],
            "estimated_impact": "high",
            "name": "Conflicto de WhatsApp",
            "description": "Número de WhatsApp diferente entre fuentes (web vs Google)"
        },
        "no_faq_schema": {
            "assets": ["faq_page"],
            "confidence_required": 0.7,
            "priority": 2,
            "validation_fields": ["common_questions", "faq_content"],
            "estimated_impact": "medium",
            "name": "Sin Schema FAQ",
            "description": "No se detecta markup de schema.org/FAQPage"
        },
        "low_gbp_score": {
            "assets": ["review_plan"],
            "confidence_required": 0.6,
            "priority": 1,
            "validation_fields": ["gbp_rating", "gbp_reviews"],
            "estimated_impact": "high",
            "name": "Bajo Score GBP",
            "description": "Google Business Profile con score bajo o poca optimización"
        },
        "no_motor_reservas": {
            "assets": ["barra_reserva_movil"],
            "confidence_required": 0.8,
            "priority": 1,
            "validation_fields": ["booking_engine_detected"],
            "estimated_impact": "high",
            "name": "Sin Motor de Reservas",
            "description": "No se detecta motor de reservas propio visible"
        },
        "no_hotel_schema": {
            "assets": ["hotel_schema"],
            "confidence_required": 0.8,
            "priority": 1,
            "validation_fields": ["schema_hotel_detected"],
            "estimated_impact": "high",
            "name": "Sin Schema Hotel",
            "description": "No se detecta markup de schema.org/Hotel"
        },
        "poor_performance": {
            "assets": ["performance_audit", "optimization_guide"],
            "confidence_required": 0.6,
            "priority": 2,
            "validation_fields": ["core_web_vitals", "mobile_score"],
            "estimated_impact": "medium",
            "name": "Performance Deficiente",
            "description": "Core Web Vitals por debajo de los umbrales recomendados"
        },
        "no_org_schema": {
            "assets": ["org_schema"],
            "confidence_required": 0.7,
            "priority": 3,
            "validation_fields": ["schema_org_detected"],
            "estimated_impact": "low",
            "name": "Sin Schema Organization",
            "description": "No se detecta markup de schema.org/Organization"
        },
        "missing_reviews": {
            "assets": ["review_widget", "review_plan"],
            "confidence_required": 0.6,
            "priority": 2,
            "validation_fields": ["gbp_reviews", "trustpilot_reviews"],
            "estimated_impact": "medium",
            "name": "Falta de Reviews",
            "description": "Pocas o ninguna review visible en GBP o web"
        },
        "low_ota_divergence": {
            "assets": ["direct_booking_campaign"],
            "confidence_required": 0.7,
            "priority": 1,
            "validation_fields": ["ota_presence", "direct_channel_percentage"],
            "estimated_impact": "high",
            "name": "Alta Dependencia OTAs",
            "description": "Bajo porcentaje de reservas por canal directo"
        },
        "metadata_defaults": {
            "assets": ["optimization_guide"],
            "confidence_required": 0.8,
            "priority": 1,
            "validation_fields": ["default_title", "default_description"],
            "estimated_impact": "high",
            "name": "Metadatos por Defecto",
            "description": "Título y descripción usando valores por defecto del CMS"
        },
        "missing_llmstxt": {
            "assets": ["llms_txt"],
            "confidence_required": 0.5,
            "priority": 3,
            "validation_fields": ["llmstxt_exists"],
            "estimated_impact": "low",
            "name": "Sin llms.txt",
            "description": "No existe archivo /llms.txt para indexación IA"
        },
        # === ANALYTICS PAIN TYPES (ANALYTICS-04) ===
        "no_analytics_configured": {
            "assets": ["analytics_setup_guide"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["ga4_available"],
            "estimated_impact": "medium",
            "name": "Sin Analytics Configurado",
            "description": "No se detecto Google Analytics 4 ni fuentes de trafico indirecto"
        },
        "low_organic_visibility": {
            "assets": ["indirect_traffic_optimization"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["organic_traffic"],
            "estimated_impact": "medium",
            "name": "Baja Visibilidad Organica",
            "description": "Trafico organico por debajo del umbral esperado para el segmento hotelero"
        },
        # FASE-B: "no_ga4_enhanced" retirado de Capa 1 — su guardia de emisión era
        # insatisfacible (is_enhanced no existe en AnalyticsStatus). Ver
        # evidence/FASE-B/decision-pains-muertos.md §3.10.
        # === PROBLEMAS GEO (Fase 2) ===
        "ai_crawler_blocked": {
            "assets": ["llms_txt"],
            "confidence_required": 0.5,
            "priority": 2,
            "validation_fields": ["ai_crawler_score"],
            "estimated_impact": "medium",
            "name": "Crawlers IA Bloqueados",
            "description": "Robots.txt no permite crawlers de IA como GPTBot, ClaudeBot"
        },
        "low_citability": {
            "assets": ["optimization_guide"],
            "confidence_required": 0.4,
            "priority": 3,
            "validation_fields": ["citability_score"],
            "estimated_impact": "low",
            "name": "Contenido Poco Citable",
            "description": "El contenido es muy corto para ser citado por LLMs"
        },
        # FASE-D: Combinado HOTFIX-3 (local_content_page) con entrada original (hotel_schema, llms_txt)
        "low_ia_readiness": {
            "assets": ["hotel_schema", "llms_txt", "local_content_page"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["ia_readiness_score"],
            "estimated_impact": "high",
            "name": "Baja Preparación IA",
            "description": "El sitio no está optimizado para ser descubierto por IA"
        },
        # === ELEMENTOS KB CON DEFAULT (GAP-IAO-01-02) ===
        "no_schema_reviews": {
            "assets": ["hotel_schema"],
            "confidence_required": 0.7,
            "priority": 1,
            "validation_fields": ["aggregateRating_detected"],
            "estimated_impact": "high",
            "name": "Sin Schema de Reviews",
            "description": "No se detecta markup aggregateRating en el Schema Hotel"
        },
        "no_ssl": {
            "assets": ["ssl_guide"],
            "confidence_required": 0.0,
            "priority": 1,
            "validation_fields": ["ssl_detected"],
            "estimated_impact": "high",
            "name": "Sin SSL/HTTPS",
            "description": "El sitio no tiene certificado SSL o no fuerza HTTPS"
        },
        "no_og_tags": {
            "assets": ["og_tags_guide", "open_graph"],  # FASE-4: Added open_graph asset
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["og_tags_detected"],
            "estimated_impact": "medium",
            "name": "Sin Open Graph Tags",
            "description": "Faltan meta tags de Open Graph para redes sociales"
        },
        "missing_alt_text": {
            "assets": ["alt_text_guide"],
            "confidence_required": 0.0,
            "priority": 3,
            "validation_fields": ["alt_text_detected"],
            "estimated_impact": "medium",
            "name": "Imágenes sin Texto Alternativo",
            "description": "Las imágenes no tienen atributo alt descriptivo"
        },
        "no_monthly_report": {
            "assets": ["monthly_report"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["monthly_report_requested"],
            "estimated_impact": "low",
            "name": "Sin Informe Mensual",
            "description": "No se genera reporte mensual de metricas para el cliente"
        },
        "no_blog_content": {
            "assets": ["blog_strategy_guide"],
            "confidence_required": 0.0,
            "priority": 3,
            "validation_fields": ["blog_detected"],
            "estimated_impact": "low",
            "name": "Blog Inactivo",
            "description": "No se detecta blog activo en el sitio"
        },
        "no_social_links": {
            "assets": ["social_strategy_guide"],
            "confidence_required": 0.0,
            "priority": 3,
            "validation_fields": ["social_links_detected"],
            "estimated_impact": "low",
            "name": "Sin Presencia en Redes Sociales",
            "description": "No se detectan enlaces a redes sociales"
        },
        "low_content_length": {
            "assets": ["optimization_guide"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["content_length"],
            "estimated_impact": "medium",
            "name": "Contenido Muy Corto",
            "description": "El contenido es demasiado corto para ser citado por IA"
        },
        "low_seo_score": {
            "assets": ["optimization_guide"],
            "confidence_required": 0.0,
            "priority": 2,
            "validation_fields": ["web_score"],
            "estimated_impact": "high",
            "name": "SEO Local Bajo",
            "description": "El score de SEO Local (CHECKLIST_SEO) está significativamente bajo"
        },

    }
    
    ASSET_NAMES = {
        "whatsapp_button": "Botón WhatsApp",
        "faq_page": "Página de FAQ",
        "review_plan": "Plan de Gestión de Reviews",
        "barra_reserva_movil": "Barra de Reserva Móvil",
        "hotel_schema": "Schema Hotel Mejorado",
        "performance_audit": "Auditoría de Performance",
        "optimization_guide": "Guía de Optimización",
        "org_schema": "Schema Organization",
        "review_widget": "Widget de Reviews",
        "direct_booking_campaign": "Campaña de Reserva Directa",
        "llms_txt": "Archivo llms.txt",
        "analytics_setup_guide": "Guia de Configuracion GA4",
        "indirect_traffic_optimization": "Guia de Optimizacion de Trafico Indirecto",
        "open_graph": "Meta Tags Sociales (Open Graph)",
        "og_tags_guide": "Guía de Open Graph",
        "monthly_report": "Informe Mensual",
    }
    
    def __init__(self):
        self.pain_map = self.PAIN_SOLUTION_MAP
        self._manual_only_assets: List[str] = []
    
    @property
    def manual_only_assets(self) -> List[str]:
        """Get list of assets that require manual action."""
        return self._manual_only_assets.copy()
    
    def detect_pains(
        self, 
        audit_result: V4AuditResult,
        validation_summary: ValidationSummary,
        analytics_data: Optional[Dict[str, Any]] = None,
        whatsapp_html_detected: bool = False
    ) -> List[Pain]:
        """
        Analyze audit result and detect problems.
        
        Args:
            audit_result: Complete v4.0 audit result
            validation_summary: Validation summary with confidence data
            analytics_data: Optional dict with analytics_status and use_ga4
            
        Returns:
            List of detected Pain objects
        """
        pains = []
        
        # Check WhatsApp visibility
        whatsapp_field = validation_summary.get_field("whatsapp_number")
        if (not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT)) and not whatsapp_html_detected:
            pains.append(Pain(
                id="no_whatsapp_visible",
                name="Sin WhatsApp Visible",
                description="No se detecta botón o enlace de WhatsApp visible en la web",
                severity="high",
                detected_by="validation",
                confidence=0.5 if not whatsapp_field else self._confidence_to_float(whatsapp_field.confidence)
            ))
        
        # Check for WhatsApp conflict (different numbers in web vs GBP)
        if whatsapp_field and whatsapp_field.confidence == ConfidenceLevel.CONFLICT:
            pains.append(Pain(
                id="whatsapp_conflict",
                name="Conflicto de WhatsApp",
                description="Número de WhatsApp diferente entre fuentes",
                severity="high",
                detected_by="validation",
                confidence=0.5
            ))
        
        # Check FAQ schema
        if not audit_result.schema.faq_schema_detected:
            pains.append(Pain(
                id="no_faq_schema",
                name="Sin Schema FAQ",
                description="No se detecta markup de schema.org/FAQPage",
                severity="medium",
                detected_by="schema",
                confidence=1.0
            ))
        
        # Check Hotel schema
        if not audit_result.schema.hotel_schema_detected:
            pains.append(Pain(
                id="no_hotel_schema",
                name="Sin Schema Hotel",
                description="No se detecta markup de schema.org/Hotel",
                severity="high",
                detected_by="schema",
                confidence=1.0
            ))
        
        # Check GBP score
        if audit_result.gbp.geo_score < 70:
            pains.append(Pain(
                id="low_gbp_score",
                name="Bajo Score GBP",
                description=f"Google Business Profile con score de {audit_result.gbp.geo_score}/100",
                severity="high" if audit_result.gbp.geo_score < 50 else "medium",
                detected_by="gbp",
                confidence=self._confidence_str_to_float(audit_result.gbp.confidence)
            ))
        
        # Check performance
        if (audit_result.performance.mobile_score and 
            audit_result.performance.mobile_score < 50):
            pains.append(Pain(
                id="poor_performance",
                name="Performance Deficiente",
                description=f"Score móvil de {audit_result.performance.mobile_score}/100",
                severity="medium",
                detected_by="performance",
                confidence=0.9 if audit_result.performance.has_field_data else 0.6
            ))
        
        # Check Organization schema
        if not audit_result.schema.org_schema_detected:
            pains.append(Pain(
                id="no_org_schema",
                name="Sin Schema Organization",
                description="No se detecta markup de schema.org/Organization",
                severity="low",
                detected_by="schema",
                confidence=1.0
            ))
        
        # Check reviews
        if audit_result.gbp.reviews < 10:
            pains.append(Pain(
                id="missing_reviews",
                name="Falta de Reviews",
                description=f"Solo {audit_result.gbp.reviews} reviews en GBP",
                severity="medium",
                detected_by="gbp",
                confidence=self._confidence_str_to_float(audit_result.gbp.confidence)
            ))
        
        # Check OTA divergence (from validation)
        # FASE-H (V7): el guard historico `hasattr(direct_field.value, '__iter__')` era
        # insatisfacible para el valor canonico del pipeline — main.py:2306 registra
        # direct_channel_percentage como float en fraccion 0-1 (main.py:1865 hace
        # `canal_directo / 100`, default 0.20 en main.py:1890), de modo que el pain nunca
        # disparaba y el `isinstance(..., (int, float, str))` interno era codigo muerto.
        # Ahora: validacion numerica + normalizacion de unidades (0.2 == 20 == "0.2" == "20"
        # => 20%). `ota_field` tampoco se registra en el flujo real (main.py solo anade
        # adr_cop / occupancy_rate / direct_channel_percentage), por eso se usa como
        # ENRIQUECIMIENTO no bloqueante del description y nunca como guard: como guard el
        # pain volveria a ser codigo muerto.
        ota_field = validation_summary.get_field("ota_presence")
        direct_field = validation_summary.get_field("direct_channel_percentage")
        direct_pct = self._normalize_to_fraction(direct_field.value) if direct_field else None

        if direct_pct is not None and direct_pct < 0.3:
            description = f"Solo {round(direct_pct * 100)}% de reservas por canal directo"
            ota_evidence = self._describe_ota_presence(ota_field)
            if ota_evidence:
                description = f"{description}. OTAs confirmadas: {ota_evidence}"
            pains.append(Pain(
                id="low_ota_divergence",
                name="Alta Dependencia OTAs",
                description=description,
                severity="high",
                detected_by="validation",
                confidence=self._confidence_to_float(direct_field.confidence)
            ))
        
        # Check metadata defaults
        if audit_result.metadata and audit_result.metadata.has_issues:
            issue_messages = []
            if audit_result.metadata.has_default_title:
                issue_messages.append("título por defecto")
            if audit_result.metadata.has_default_description:
                issue_messages.append("descripción por defecto")
            
            if issue_messages:
                pains.append(Pain(
                    id="metadata_defaults",
                    name="Metadatos por Defecto",
                    description=f"Valores por defecto del CMS: {', '.join(issue_messages)}",
                    severity="high",
                    detected_by="metadata",
                    confidence=0.9
                ))
        

        # === ANALYTICS PAIN DETECTION (ANALYTICS-04) ===
        if analytics_data:
            pains.extend(self._detect_analytics_pains(analytics_data))

        # === FASE 2: DETECCIÓN DE PROBLEMAS GEO ===
        
        # Check AI Crawler access
        if hasattr(audit_result, 'ai_crawlers') and audit_result.ai_crawlers:
            if audit_result.ai_crawlers.overall_score < 0.7:
                blocked_count = len(audit_result.ai_crawlers.blocked_crawlers)
                pains.append(Pain(
                    id="ai_crawler_blocked",
                    name="Crawlers de IA Bloqueados",
                    description=f"Score de acceso IA: {audit_result.ai_crawlers.overall_score:.2f}/1.0 - {blocked_count} crawlers bloqueados",
                    severity="medium",
                    detected_by="ai_crawler_audit",
                    confidence=audit_result.ai_crawlers.overall_score
                ))
        
        # Check Citability
        if hasattr(audit_result, 'citability') and audit_result.citability:
            if audit_result.citability.overall_score < 50:
                pains.append(Pain(
                    id="low_citability",
                    name="Contenido Poco Citable",
                    description=f"Score citability: {audit_result.citability.overall_score:.1f}/100 - {audit_result.citability.blocks_analyzed} bloques analizados",
                    severity="medium",
                    detected_by="citability_audit",
                    confidence=audit_result.citability.overall_score / 100
                ))
        
        # Check IA-Readiness
        if hasattr(audit_result, 'ia_readiness') and audit_result.ia_readiness:
            if audit_result.ia_readiness.overall_score < 50:
                pains.append(Pain(
                    id="low_ia_readiness",
                    name="Baja Preparación para IA",
                    description=f"IA-Readiness: {audit_result.ia_readiness.overall_score:.1f}/100 - Estado: {audit_result.ia_readiness.status}",
                    severity="high",
                    detected_by="ia_readiness_calculator",
                    confidence=audit_result.ia_readiness.overall_score / 100
                ))
        
        # === FASE-C: Open Graph Tags Detection ===
        # Check seo_elements.open_graph from SEOElementsResult
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            if not audit_result.seo_elements.open_graph:
                logger.info("OG tags not detected → activating pain_id no_og_tags")
                pains.append(Pain(
                    id="no_og_tags",
                    name="Sin Open Graph Tags",
                    description="No se detectan meta tags de Open Graph para redes sociales",
                    severity="medium",
                    detected_by="seo_elements_detection",
                    confidence=0.9 if audit_result.seo_elements.confidence == "high" else 0.6
                ))
            elif self._og_tags_incomplete(audit_result.seo_elements):
                # ASSET-ALIGNMENT FASE-2: enhance_existing mode
                # Site HAS OG tags but they're incomplete → activate with medium confidence
                tag_count = len(audit_result.seo_elements.open_graph_tags or {})
                logger.info(f"OG tags present but incomplete ({tag_count} tags) → activating pain_id no_og_tags (enhance_existing)")
                pains.append(Pain(
                    id="no_og_tags",
                    name="Open Graph Tags Incompletos",
                    description=f"Se detectaron {tag_count} OG tags pero faltan tags importantes para redes sociales",
                    severity="medium",
                    detected_by="seo_elements_detection",
                    confidence=0.5
                ))

        # === ASSET-ALIGNMENT FASE-2: low_seo_score Detection ===
        web_score = self._compute_web_score(audit_result)
        if web_score is not None and web_score < 40:
            logger.info(f"Web/SEO score {web_score}/100 below threshold 40 → activating pain_id low_seo_score")
            pains.append(Pain(
                id="low_seo_score",
                name="SEO Local Bajo",
                description=f"Score SEO Local: {web_score}/100 — significativamente bajo",
                severity="high",
                detected_by="web_score",
                confidence=0.8
            ))
        
        # === FASE-B: emisiones de pains que estaban muertos en Capa 1 (V1) ===
        # Regla de B1: ninguna emisión sin señal de dato verificable Y sin evidencia
        # positiva de que la medición ocurrió. Un guard que confunda "no medido" con
        # "medido en False" produce pains que disparan en falso (el defecto de
        # ai_crawler_blocked, dossier §3).

        # missing_llmstxt — sonda HTTP real: v4_comprehensive hace GET {base}/llms.txt y
        # ia_readiness_calculator puebla components["llms_txt"] = 100 | 0. La presencia de
        # la clave es la prueba de que la sonda corrió; si ia_readiness es None, no se midió.
        if getattr(audit_result, 'ia_readiness', None):
            componentes = getattr(audit_result.ia_readiness, 'components', None)
            if isinstance(componentes, dict) and componentes.get("llms_txt") == 0:
                logger.info("llms.txt ausente (sonda HTTP) → activating pain_id missing_llmstxt")
                pains.append(Pain(
                    id="missing_llmstxt",
                    name="Sin llms.txt",
                    description="No existe archivo /llms.txt: los asistentes de IA no tienen mapa del sitio",
                    severity="low",
                    detected_by="ia_readiness_calculator",
                    confidence=0.9
                ))

        # El detector devuelve confidence="low" con todos los flags en False cuando lanza
        # excepción (seo_elements_detector.py:70-74); emitir sobre ese resultado sería un
        # falso positivo. Solo se emite con la medición realmente completada.
        seo_elements = getattr(audit_result, 'seo_elements', None)
        seo_medido = bool(seo_elements) and getattr(seo_elements, 'confidence', None) == "high"

        # missing_alt_text — exige recuento positivo: images_without_alt > 0 solo es posible
        # si el HTML se parseó y había imágenes sin alt. Sin imágenes el detector devuelve
        # imagenes_alt=True (seo_elements_detector.py:92), así que no dispara.
        if seo_medido and seo_elements.imagenes_alt is False \
                and getattr(seo_elements, 'images_without_alt', 0) > 0:
            logger.info(
                f"{seo_elements.images_without_alt} imágenes sin alt → "
                f"activating pain_id missing_alt_text"
            )
            pains.append(Pain(
                id="missing_alt_text",
                name="Imágenes sin Texto Alternativo",
                description=(
                    f"{seo_elements.images_without_alt} imágenes sin atributo alt descriptivo"
                ),
                severity="medium",
                detected_by="seo_elements_detection",
                confidence=0.9
            ))

        # no_social_links — redes_activas es len(found) > 0 sobre los <a href> del HTML
        # (seo_elements_detector.py:95-103). La ausencia solo es creíble si la medición
        # se completó, de ahí el guard seo_medido.
        if seo_medido and seo_elements.redes_activas is False:
            logger.info("Sin enlaces a redes sociales → activating pain_id no_social_links")
            pains.append(Pain(
                id="no_social_links",
                name="Sin Presencia en Redes Sociales",
                description="No se detectan enlaces a redes sociales en el sitio",
                severity="low",
                detected_by="seo_elements_detection",
                confidence=0.9
            ))

        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pains.sort(key=lambda p: severity_order.get(p.severity, 4))
        
        return pains
    
    # CHECKLIST_SEO weights — mirrors v4_diagnostic_generator:CHECKLIST_SEO
    # Used by _compute_web_score() to evaluate SEO health without importing
    # the diagnostic generator (avoids circular dependency)
    _CHECKLIST_SEO = {
        "ssl": 15,
        "schema_hotel": 20,
        "LCP_ok": 20,
        "CLS_ok": 10,
        "imagenes_alt": 15,
        "blog_activo": 10,
        "schema_reviews": 10,
    }

    def _compute_web_score(self, audit_result) -> int | None:
        """Compute Web/SEO score using CHECKLIST_SEO (same logic as diagnostic generator).

        Returns score 0-100, or None if audit_result is insufficient to compute.
        """
        if not audit_result:
            return None
        
        elementos = {}
        # SSL
        elementos["ssl"] = audit_result.url.startswith('https') if getattr(audit_result, 'url', None) else False
        # Schema hotel
        elementos["schema_hotel"] = bool(audit_result.schema.hotel_schema_detected) if getattr(audit_result, 'schema', None) else False
        # Performance
        elementos["LCP_ok"] = (
            getattr(audit_result, 'performance', None) is not None
            and hasattr(audit_result.performance, 'lcp')
            and audit_result.performance.lcp is not None
            and isinstance(audit_result.performance.lcp, (int, float))
            and audit_result.performance.lcp <= 2.5
        )
        elementos["CLS_ok"] = (
            getattr(audit_result, 'performance', None) is not None
            and hasattr(audit_result.performance, 'cls')
            and audit_result.performance.cls is not None
            and isinstance(audit_result.performance.cls, (int, float))
            and audit_result.performance.cls <= 0.1
        )
        # Imagenes alt
        if hasattr(audit_result, 'seo_elements') and audit_result.seo_elements:
            elementos["imagenes_alt"] = audit_result.seo_elements.imagenes_alt
        else:
            elementos["imagenes_alt"] = False
        # Blog activo
        elementos["blog_activo"] = "no_evaluado"
        # Schema reviews
        elementos["schema_reviews"] = bool(audit_result.gbp.rating) if getattr(audit_result, 'gbp', None) else False

        if not elementos:
            return None
        
        score = sum(self._CHECKLIST_SEO[k] for k, v in elementos.items() if v is True and k in self._CHECKLIST_SEO)
        return min(100, score)

    def _og_tags_incomplete(self, seo_elements) -> bool:
        """Check if existing OG tags are incomplete (fewer than 10 tags).

        Used by detect_pains() to trigger no_og_tags in enhance_existing mode
        when the site HAS OG tags but they're not comprehensive.
        """
        if not seo_elements:
            return False
        if not seo_elements.open_graph:
            return False  # Already handled by the primary detection branch
        og_tags = getattr(seo_elements, 'open_graph_tags', None) or {}
        return len(og_tags) < 10

    def detect_pains_for_analytics(
        self,
        analytics_data: Dict[str, Any]
    ) -> List[Pain]:
        """
        Detect analytics-specific pains when no audit_result is available.
        
        Used when the system runs without a full site audit but has
        analytics_data available (e.g., standalone analytics run).
        
        Args:
            analytics_data: Dict with analytics_status, use_ga4, organic_traffic
            
        Returns:
            List of detected analytics Pain objects
        """
        return self._detect_analytics_pains(analytics_data)
    
    def _detect_analytics_pains(
        self,
        analytics_data: Dict[str, Any]
    ) -> List[Pain]:
        """
        Internal method: detect analytics-related pains from analytics_data.
        
        Shared between detect_pains() and detect_pains_for_analytics().
        """
        pains = []
        status = analytics_data.get("analytics_status")
        ga4_available = analytics_data.get("use_ga4", False)

        organic = analytics_data.get("organic_traffic")
        organic_measured_low = (
            organic is not None
            and isinstance(organic, (int, float))
            and organic < 1000
        )

        if not ga4_available:
            error_text = ""
            if status and hasattr(status, "ga4_error") and status.ga4_error:
                error_text = f" - Error: {status.ga4_error}"
            elif status and hasattr(status, "ga4_status_text"):
                error_text = f" - Estado: {status.ga4_status_text}"

            pains.append(Pain(
                id="no_analytics_configured",
                name="Sin Analytics Configurado",
                description=f"Google Analytics 4 no configurado o sin credenciales.{error_text}",
                severity="medium",
                detected_by="analytics",
                confidence=0.9
            ))

        # FASE-H (V8): antes este id se anexaba desde DOS ramas (sin GA4 + trafico medido
        # bajo el umbral) y detect_pains recibia el pain duplicado, que se traduce en dos
        # brechas identicas con costo propio. Ahora hay UN solo punto de emision para
        # low_organic_visibility: se deciden primero las dos señales y se consolida la
        # construccion. Cuando ambas aplican, la emision unica conserva el dato medido
        # (sesiones/umbral) ADEMAS del motivo "sin analytics"; los nombres, severidades y
        # detected_by de cada caso quedan intactos.
        if not ga4_available or organic_measured_low:
            if not ga4_available:
                name = "Baja Visibilidad de Trafico Organico"
                description = (
                    "Sin analytics configurado, no se puede medir ni optimizar el trafico organico."
                )
                if organic_measured_low:
                    description = (
                        f"{description} Trafico organico estimado: {organic} sesiones/mes "
                        "(umbral hotelero: 1000)"
                    )
                confidence = 0.8
            else:
                name = "Baja Visibilidad Organica"
                description = (
                    f"Trafico organico estimado: {organic} sesiones/mes (umbral hotelero: 1000)"
                )
                confidence = 0.7

            pains.append(Pain(
                id="low_organic_visibility",
                name=name,
                description=description,
                severity="medium",
                detected_by="analytics",
                confidence=confidence
            ))

        return pains
    
    def map_to_solutions(
        self, 
        pains: List[Pain]
    ) -> List[Solution]:
        """
        Map detected pains to solutions.
        
        Args:
            pains: List of detected pains
            
        Returns:
            List of Solution objects
        """
        solutions = []
        self._manual_only_assets = []
        
        for pain in pains:
            if pain.id in self.pain_map:
                mapping = self.pain_map[pain.id]
                
                for asset_type in mapping["assets"]:
                    from modules.asset_generation.asset_catalog import is_asset_implemented, ASSET_CATALOG, AssetStatus
                    if not is_asset_implemented(asset_type):
                        if asset_type in ASSET_CATALOG:
                            entry = ASSET_CATALOG[asset_type]
                            if entry.status == AssetStatus.MANUAL_ONLY:
                                if asset_type not in self._manual_only_assets:
                                    self._manual_only_assets.append(asset_type)
                                import logging
                                logging.getLogger(__name__).warning(
                                    f"Asset {asset_type} is MANUAL_ONLY - requires manual implementation"
                                )
                                continue
                        import logging
                        logging.getLogger(__name__).warning(
                            f"Asset {asset_type} promised but not implemented - skipping"
                        )
                        continue
                        
                    # ROICR FASE-1: semantic validation of pain→asset mapping
                    from modules.asset_generation.asset_catalog import ASSET_CATALOG
                    entry = ASSET_CATALOG.get(asset_type)
                    asset_status = entry.status.value if entry else "unknown"
                    from modules.quality.asset_semantics_validator import validar_semantica_comercial
                    is_valid, status = validar_semantica_comercial(pain.id, asset_type, asset_status)
                    if not is_valid:
                        # Semantic hallucination: check for migration_target
                        if entry and entry.migration_target:
                            redirect_to = entry.migration_target
                            logger.info(
                                f"[AssetSemantics] Redirecting BLOCKED asset '{asset_type}' "
                                f"→ migration_target '{redirect_to}' for pain '{pain.id}'"
                            )
                            if redirect_to != asset_type and is_asset_implemented(redirect_to):
                                solutions.append(Solution(
                                    pain_id=pain.id,
                                    asset_type=redirect_to,
                                    asset_name=self.ASSET_NAMES.get(redirect_to, redirect_to),
                                    description=f"[REDIRECT] {mapping['description']}",
                                    confidence_required=mapping["confidence_required"],
                                    validation_fields=mapping["validation_fields"],
                                    estimated_impact=mapping["estimated_impact"],
                                    priority=mapping.get("priority", 2),
                                    semantic_status="IMPLEMENT",
                                    migration_target=redirect_to
                                ))
                        else:
                            logger.warning(
                                f"[AssetSemantics] BLOCKED '{asset_type}' for pain '{pain.id}' "
                                f"— no migration_target, marking UNRESOLVED"
                            )
                        continue

                    solutions.append(Solution(
                        pain_id=pain.id,
                        asset_type=asset_type,
                        asset_name=self.ASSET_NAMES.get(asset_type, asset_type),
                        description=mapping["description"],
                        confidence_required=mapping["confidence_required"],
                        validation_fields=mapping["validation_fields"],
                        estimated_impact=mapping["estimated_impact"],
                        priority=mapping.get("priority", 2),
                        semantic_status=status  # IMPLEMENT or AUDIT_ONLY
                    ))
        
        return solutions
    
    def get_assets_for_pain(
        self, 
        pain_id: str,
        available_confidence: Dict[str, float]
    ) -> List[AssetSpec]:
        """
        Get assets that can solve a specific pain, filtered by available confidence.
        
        Args:
            pain_id: The pain identifier
            available_confidence: Dict mapping field names to confidence scores
            
        Returns:
            List of AssetSpec objects that can be generated
        """
        if pain_id not in self.pain_map:
            return []
        
        mapping = self.pain_map[pain_id]
        assets = []
        
        for asset_type in mapping["assets"]:
            # Check if we have sufficient confidence for required fields
            required_fields = mapping["validation_fields"]
            min_confidence = mapping["confidence_required"]
            
            field_confidences = [
                available_confidence.get(field, 0.0) 
                for field in required_fields
            ]
            
            avg_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else 0.0
            
            # Special case: whatsapp_conflict always generates whatsapp_button
            # because the conflict itself justifies the asset as solution
            if pain_id == "whatsapp_conflict":
                can_generate = True  # El conflicto justifica generar el asset
                reason = f"Confidence {avg_confidence:.2f} vs required {min_confidence}"
            else:
                can_generate = avg_confidence >= min_confidence
                reason = (
                    f"Confidence {avg_confidence:.2f} vs required {min_confidence}"
                    if can_generate
                    else f"Insufficient confidence ({avg_confidence:.2f} < {min_confidence})"
                )
                # FASE-SR-E (D-PF3, L-SR4): para la brecha de AUSENCIA genuina
                # de schema, el contrato del catálogo manda — con fuentes
                # disponibles (GBP/web) el fallback ``generate_basic_schema``
                # (block_on_failure=False) permite generar la versión básica;
                # sin fuentes → bloqueo explícito con justified_skip. La
                # confianza de la brecha ("schema_hotel_detected") no mide las
                # fuentes para CONSTRUIR el asset (L-SR4).
                if not can_generate and pain_id == "no_hotel_schema":
                    from modules.asset_generation.asset_catalog import ASSET_CATALOG
                    catalog_entry = ASSET_CATALOG.get(asset_type)
                    has_sources = any(
                        score > 0 for score in available_confidence.values()
                    )
                    if (
                        catalog_entry is not None
                        and catalog_entry.fallback
                        and not catalog_entry.block_on_failure
                        and has_sources
                    ):
                        can_generate = True
                        reason = (
                            f"D-PF3 fallback '{catalog_entry.fallback}': ausencia "
                            f"genuina con fuentes disponibles (confianza media "
                            f"{avg_confidence:.2f} < {min_confidence} requerida "
                            f"por la brecha)"
                        )
                    elif not has_sources:
                        reason = (
                            f"Sin fuentes para generar el asset (confianza "
                            f"{avg_confidence:.2f}) — bloqueo con justified_skip "
                            f"(D-PF3)"
                        )
            
            # Determine confidence level
            if avg_confidence >= 0.9:
                conf_level = ConfidenceLevel.VERIFIED
            elif avg_confidence >= 0.7:
                conf_level = ConfidenceLevel.ESTIMATED
            elif avg_confidence >= 0.4:
                conf_level = ConfidenceLevel.CONFLICT
            else:
                conf_level = ConfidenceLevel.UNKNOWN
            
            # Get priority from mapping (default to 2 if not specified)
            priority = mapping.get("priority", 2)
            
            # ROICR FASE-1: semantic validation
            from modules.asset_generation.asset_catalog import ASSET_CATALOG
            entry = ASSET_CATALOG.get(asset_type)
            asset_status = entry.status.value if entry else "implemented"
            from modules.quality.asset_semantics_validator import validar_semantica_comercial
            _is_valid, semantic_status = validar_semantica_comercial(pain_id, asset_type, asset_status)
            if not _is_valid:
                # Semantic hallucination: skip this asset in asset_plan
                import logging
                logging.getLogger(__name__).debug(
                    f"[AssetSemantics] Skipping '{asset_type}' for pain '{pain_id}': "
                    f"{semantic_status}"
                )
                continue

            assets.append(AssetSpec(
                asset_type=asset_type,
                pain_ids=[pain_id],
                confidence_level=conf_level,
                confidence_required=min_confidence,
                can_generate=can_generate,
                priority=priority,  # FASE 2: Incluir prioridad del mapeo
                reason=reason,
                problem_solved=mapping["name"],
                description=mapping["description"],
                semantic_status=semantic_status  # ROICR FASE-1: AUDIT_ONLY or IMPLEMENT
            ))
        
        return assets
    
    def categorize_pains(
        self,
        pains: List[Pain],
        solutions: List[Solution]
    ) -> Tuple[List[Pain], List[Pain]]:
        """
        Separate pains into those with immediate solutions vs those requiring attention.
        
        Args:
            pains: List of all detected pains
            solutions: List of available solutions
            
        Returns:
            Tuple of (pains_with_solution, pains_requiring_attention)
        """
        # Get pain IDs that have solutions
        solvable_pain_ids = set(s.pain_id for s in solutions)
        
        with_solution = []
        requiring_attention = []
        
        for pain in pains:
            if pain.id in solvable_pain_ids:
                with_solution.append(pain)
            else:
                requiring_attention.append(pain)
        
        return with_solution, requiring_attention
    
    def generate_asset_plan(
        self,
        pains: List[Pain],
        validation_summary: ValidationSummary,
        extra_confidence: Optional[Dict[str, float]] = None,
        separate_manual: bool = False
    ) -> Any:
        """
        Generate a complete asset plan from detected pains.
        
        Args:
            pains: List of detected pains
            validation_summary: Validation summary with confidence data
            extra_confidence: Optional dict to override/add confidence scores
            separate_manual: If True, returns dict with 'automatic' and 'manual_only' keys.
                           If False (default), returns List[AssetSpec] for backward compatibility.
            
        Returns:
            If separate_manual is False: List[AssetSpec] (backward compatible)
            If separate_manual is True: Dict with 'automatic' and 'manual_only' lists
        """
        from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus, is_asset_implemented
        
        assets = []
        manual_only_asset_list = []
        
        self._manual_only_assets = []
        
        confidence_map = {}
        for field in validation_summary.fields:
            confidence_map[field.field_name] = self._confidence_to_score(field.confidence)
        
        if extra_confidence:
            confidence_map.update(extra_confidence)
        
        for pain in pains:
            if pain.id in self.pain_map:
                mapping = self.pain_map[pain.id]
                
                for asset_type in mapping["assets"]:
                    # ROICR FASE-1: semantic validation (same logic as get_assets_for_pain)
                    from modules.asset_generation.asset_catalog import ASSET_CATALOG
                    entry = ASSET_CATALOG.get(asset_type)
                    asset_status = entry.status.value if entry else "implemented"
                    from modules.quality.asset_semantics_validator import validar_semantica_comercial
                    _is_valid, semantic_status = validar_semantica_comercial(pain.id, asset_type, asset_status)
                    if not _is_valid:
                        import logging
                        logging.getLogger(__name__).debug(
                            f"[AssetSemantics] generate_asset_plan: skipping '{asset_type}' for pain '{pain.id}'"
                        )
                        continue

                    if is_asset_implemented(asset_type):
                        pain_assets = self.get_assets_for_pain(pain.id, confidence_map)
                        for pa in pain_assets:
                            pa.semantic_status = semantic_status
                        assets.extend(pain_assets)
                    elif asset_type in ASSET_CATALOG:
                        entry = ASSET_CATALOG[asset_type]
                        if entry.status == AssetStatus.MANUAL_ONLY:
                            if asset_type not in self._manual_only_assets:
                                self._manual_only_assets.append(asset_type)
                            
                            field_confidences = [
                                confidence_map.get(field, 0.0) 
                                for field in mapping["validation_fields"]
                            ]
                            avg_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else 0.0
                            
                            manual_only_asset_list.append(AssetSpec(
                                asset_type=asset_type,
                                pain_ids=[pain.id],
                                confidence_level=ConfidenceLevel.ESTIMATED,
                                confidence_required=mapping["confidence_required"],
                                can_generate=False,
                                priority=mapping.get("priority", 2),
                                reason="Asset is MANUAL_ONLY - requires manual implementation",
                                problem_solved=mapping["name"],
                                description=mapping["description"],
                                requires_manual_action=True
                            ))
        
        seen_types = set()
        unique_assets = []
        for asset in assets:
            if asset.asset_type not in seen_types:
                seen_types.add(asset.asset_type)
                unique_assets.append(asset)
        
        unique_assets.sort(key=lambda a: a.confidence_required, reverse=True)
        manual_only_asset_list.sort(key=lambda a: a.confidence_required, reverse=True)
        
        all_assets = unique_assets + manual_only_asset_list
        
        automatic_assets = unique_assets
        
        if separate_manual:
            return {
                "automatic": automatic_assets,
                "manual_only": manual_only_asset_list
            }
        
        return all_assets
    
    def get_manual_only_assets(
        self,
        pains: List[Pain],
        validation_summary: ValidationSummary,
        extra_confidence: Optional[Dict[str, float]] = None
    ) -> List[AssetSpec]:
        """
        Get assets that are MANUAL_ONLY but were requested.
        
        Args:
            pains: List of detected pains
            validation_summary: Validation summary with confidence data
            extra_confidence: Optional dict to override/add confidence scores
            
        Returns:
            List of AssetSpec that require manual action
        """
        from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus
        
        confidence_map = {}
        for field in validation_summary.fields:
            confidence_map[field.field_name] = self._confidence_to_score(field.confidence)
        
        if extra_confidence:
            confidence_map.update(extra_confidence)
        
        manual_assets = []
        
        for pain in pains:
            if pain.id in self.pain_map:
                mapping = self.pain_map[pain.id]
                
                for asset_type in mapping["assets"]:
                    if asset_type in ASSET_CATALOG:
                        entry = ASSET_CATALOG[asset_type]
                        if entry.status == AssetStatus.MANUAL_ONLY:
                            field_confidences = [
                                confidence_map.get(field, 0.0) 
                                for field in mapping["validation_fields"]
                            ]
                            avg_confidence = sum(field_confidences) / len(field_confidences) if field_confidences else 0.0
                            
                            manual_assets.append(AssetSpec(
                                asset_type=asset_type,
                                pain_ids=[pain.id],
                                confidence_level=ConfidenceLevel.ESTIMATED,
                                confidence_required=mapping["confidence_required"],
                                can_generate=False,
                                priority=mapping.get("priority", 2),
                                reason=f"Asset is MANUAL_ONLY - requires manual implementation",
                                problem_solved=mapping["name"],
                                description=mapping["description"],
                                requires_manual_action=True
                            ))
        
        seen_types = set()
        unique_manual = []
        for asset in manual_assets:
            if asset.asset_type not in seen_types:
                seen_types.add(asset.asset_type)
                unique_manual.append(asset)
        
        unique_manual.sort(key=lambda a: a.confidence_required, reverse=True)
        
        return unique_manual
    
    def _confidence_to_float(self, confidence: ConfidenceLevel) -> float:
        """Convert ConfidenceLevel to float."""
        mapping = {
            ConfidenceLevel.VERIFIED: 0.95,
            ConfidenceLevel.ESTIMATED: 0.7,
            ConfidenceLevel.CONFLICT: 0.3,
            ConfidenceLevel.UNKNOWN: 0.0
        }
        return mapping.get(confidence, 0.0)
    
    def _confidence_str_to_float(self, confidence: str) -> float:
        """Convert confidence string to float."""
        mapping = {
            "VERIFIED": 0.95,
            "ESTIMATED": 0.7,
            "CONFLICT": 0.3,
            "UNKNOWN": 0.0
        }
        return mapping.get(confidence.upper(), 0.5)
    
    def _confidence_to_score(self, confidence: ConfidenceLevel) -> float:
        """Convert ConfidenceLevel to numeric score."""
        return self._confidence_to_float(confidence)

    def _normalize_to_fraction(self, value: Any) -> Optional[float]:
        """Normalizar un valor de porcentaje a fraccion 0-1.

        FASE-H (V7): senal `direct_channel_percentage`. La unidad canonica del pipeline es
        la fraccion (main.py:1865 `canal_directo / 100`; default `0.20` en main.py:1890;
        calculator_v2.py:481 documenta "Porcentaje canal directo (0-1)"), pero un
        ValidatedField puede llegar en porcentaje o como string de input humano. Criterio de
        desempate: valor > 1 => porcentaje (se divide entre 100). Por eso `0.2`, `20`,
        `"0.2"`, `"20"` y `"20 %"` significan todos 20%.

        Devuelve None —y el caller no dispara el pain— para bool, negativo, NaN, inf, u
        otro tipo no convertible. Nunca lanza.
        """
        if value is None or isinstance(value, bool):
            return None

        if isinstance(value, str):
            text = value.strip().rstrip("%").strip()
            if not text:
                return None
            try:
                number = float(text)
            except ValueError:
                return None
        elif isinstance(value, (int, float)):
            number = float(value)
        else:
            return None

        if number != number or number in (float("inf"), float("-inf")):
            return None
        if number < 0:
            return None

        return number / 100 if number > 1 else number

    def _describe_ota_presence(self, ota_field: Any) -> str:
        """Render (tolerante) de la evidencia OTA para el description de un pain.

        Evidencia NO bloqueante: `ota_presence` es List[str] en el modelo del pipeline
        (inputs_contract.py:49) pero main.py nunca lo registra en el ValidationSummary, asi
        que devolver "" es el caso normal del flujo real y NUNCA debe condicionar la
        emision del pain. Acepta str / dict / secuencias por tolerancia; devuelve "" si no
        hay nada que nombrar.
        """
        value = getattr(ota_field, "value", None)

        if isinstance(value, str):
            nombres = [value]
        elif isinstance(value, dict):
            nombres = [str(clave) for clave in value.keys()]
        elif isinstance(value, (list, tuple, set)):
            nombres = [str(elemento) for elemento in value]
        else:
            nombres = []

        nombres = [n.strip() for n in nombres if isinstance(n, str) and n.strip()]
        if not nombres:
            return ""

        if len(nombres) > 3:
            return ", ".join(nombres[:3]) + f", +{len(nombres) - 3} mas"
        return ", ".join(nombres)
