"""
Pain to Solution Mapper for Commercial Documents v4.0.

Maps detected problems to specific assets/solutions based on
validation confidence and availability.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any

from .data_structures import (
    V4AuditResult,
    ValidationSummary,
    AssetSpec,
    ConfidenceLevel
)


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
            "assets": ["geo_playbook", "review_plan"],
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
        "no_ga4_enhanced": {
            "assets": ["analytics_setup_guide"],
            "confidence_required": 0.0,
            "priority": 3,
            "validation_fields": ["ga4_enhanced"],
            "estimated_impact": "low",
            "name": "GA4 sin Configuracion Avanzada",
            "description": "GA4 existe pero sin eventos de conversion ni medicion de revenue mejorada"
        },
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
        "low_ia_readiness": {
            "assets": ["hotel_schema", "llms_txt"],
            "confidence_required": 0.5,
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
            "assets": ["og_tags_guide"],
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
    }
    
    ASSET_NAMES = {
        "whatsapp_button": "Botón WhatsApp",
        "faq_page": "Página de FAQ",
        "geo_playbook": "Playbook de Geolocalización",
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
        "indirect_traffic_optimization": "Guia de Optimizacion de Trafico Indirecto"
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
        analytics_data: Optional[Dict[str, Any]] = None
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
        if not whatsapp_field or whatsapp_field.confidence in (ConfidenceLevel.UNKNOWN, ConfidenceLevel.CONFLICT):
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
        ota_field = validation_summary.get_field("ota_presence")
        direct_field = validation_summary.get_field("direct_channel_percentage")
        
        if direct_field and hasattr(direct_field.value, '__iter__'):
            try:
                direct_pct = float(direct_field.value) if isinstance(direct_field.value, (int, float, str)) else 0.3
                if direct_pct < 0.3:
                    pains.append(Pain(
                        id="low_ota_divergence",
                        name="Alta Dependencia OTAs",
                        description=f"Solo {int(direct_pct * 100)}% de reservas por canal directo",
                        severity="high",
                        detected_by="validation",
                        confidence=self._confidence_to_float(direct_field.confidence)
                    ))
            except (ValueError, TypeError):
                pass
        
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
        # Sort by severity
        severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        pains.sort(key=lambda p: severity_order.get(p.severity, 4))
        
        return pains
    
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

            # Sin GA4 no se puede medir trafico organico → implicitamente baja visibilidad
            pains.append(Pain(
                id="low_organic_visibility",
                name="Baja Visibilidad de Trafico Organico",
                description="Sin analytics configurado, no se puede medir ni optimizar el trafico organico.",
                severity="medium",
                detected_by="analytics",
                confidence=0.8
            ))

        elif status and hasattr(status, "is_enhanced"):
            if not status.is_enhanced:
                pains.append(Pain(
                    id="no_ga4_enhanced",
                    name="GA4 sin Configuracion Avanzada",
                    description="GA4 detectado pero sin eventos de conversion ni enhanced ecommerce",
                    severity="low",
                    detected_by="analytics",
                    confidence=0.6
                ))

        organic = analytics_data.get("organic_traffic")
        if organic is not None and isinstance(organic, (int, float)) and organic < 1000:
            pains.append(Pain(
                id="low_organic_visibility",
                name="Baja Visibilidad Organica",
                description=f"Trafico organico estimado: {organic} sesiones/mes (umbral hotelero: 1000)",
                severity="medium",
                detected_by="analytics",
                confidence=0.7
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
                        
                    solutions.append(Solution(
                        pain_id=pain.id,
                        asset_type=asset_type,
                        asset_name=self.ASSET_NAMES.get(asset_type, asset_type),
                        description=mapping["description"],
                        confidence_required=mapping["confidence_required"],
                        validation_fields=mapping["validation_fields"],
                        estimated_impact=mapping["estimated_impact"],
                        priority=mapping.get("priority", 2)
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
            else:
                can_generate = avg_confidence >= min_confidence
            
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
            
            assets.append(AssetSpec(
                asset_type=asset_type,
                pain_ids=[pain_id],
                confidence_level=conf_level,
                confidence_required=min_confidence,
                can_generate=can_generate,
                priority=priority,  # FASE 2: Incluir prioridad del mapeo
                reason=f"Confidence {avg_confidence:.2f} vs required {min_confidence}" if can_generate else f"Insufficient confidence ({avg_confidence:.2f} < {min_confidence})",
                problem_solved=mapping["name"],
                description=mapping["description"]
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
                    if is_asset_implemented(asset_type):
                        pain_assets = self.get_assets_for_pain(pain.id, confidence_map)
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
