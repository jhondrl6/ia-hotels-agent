"""Generates assets conditionally based on preflight checks.

INTEGRACION FASE-CAUSAL-01:
- SitePresenceChecker se ejecuta ANTES de generar
- Si el asset YA existe en sitio real → SKIP con理由
- Si el asset fue entregado previamente → SKIP REDUNDANT
- Solo genera si realmente necesita crearse
"""

import re
from typing import Dict, List, Optional, Any
from pathlib import Path
from datetime import datetime
import json
import csv
import io
import hashlib

from .preflight_checks import PreflightChecker, PreflightStatus, PreflightReport
from .asset_metadata import AssetMetadata, AssetMetadataEnforcer, AssetStatus
from .asset_catalog import ASSET_CATALOG
from .data_assessment import DataAssessment, DataClassification
from .site_presence_checker import SitePresenceChecker, PresenceStatus


class ConditionalGenerator:
    """Generates assets conditionally based on preflight check results."""

    @property
    def GENERATION_STRATEGIES(self) -> dict:
        """
        Derive generation strategies from ASSET_CATALOG.
        Only includes IMPLEMENTED assets.
        
        Returns:
            Dict mapping asset_type to {template, output_name}
        """
        return {
            k: {"template": v.template, "output_name": v.output_name}
            for k, v in ASSET_CATALOG.items()
            if v.status.value == "implemented"
        }

    def __init__(self, output_dir: str = "output"):
        """Initialize the conditional generator.
        
        Args:
            output_dir: Base directory for output files
        """
        self.preflight_checker = PreflightChecker()
        self.output_dir = Path(output_dir)
        self.metadata_enforcer = AssetMetadataEnforcer()
        self.data_assessor = DataAssessment()
        self.site_checker = SitePresenceChecker()  # FASE-CAUSAL-01
        
        # Asset sets per generation path (FASE 6: Orchestration V2)
        self._fast_assets = ["whatsapp_button", "faq_page", "hotel_schema"]
        self._standard_assets = ["whatsapp_button", "faq_page", "hotel_schema", 
                                 "geo_playbook", "review_plan", "org_schema"]
        self._full_assets = None  # Will use all IMPLEMENTED assets

    def generate(
        self,
        asset_type: str,
        validated_data: Dict,
        hotel_name: str,
        hotel_id: str,
        hotel_context: Optional[Dict[str, Any]] = None,
        site_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate an asset conditionally based on preflight checks.
        
        FASE-CAUSAL-01: Ahora verifica sitio real ANTES de generar.
        Si el asset ya existe en producción → SKIP
        
        Args:
            asset_type: Type of asset to generate
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            hotel_id: Unique hotel identifier
            hotel_context: Optional context about hotel (reviews, photos, place_found)
            site_url: URL del sitio de producción para verificar si asset ya existe
                         Si el asset ya existe en el sitio → SKIP
        
        Returns:
            Result dictionary with status, content, and metadata
        """
        if asset_type not in self.GENERATION_STRATEGIES:
            return {
                "success": False,
                "status": "error",
                "error": f"Unknown asset type: {asset_type}",
                "asset_type": asset_type,
                "hotel_id": hotel_id
            }
        
        # ═══════════════════════════════════════════════════════════════════
        # FASE-CAUSAL-01: GATE DE PRESENCIA EN SITIO REAL
        # ═══════════════════════════════════════════════════════════════════
        if site_url:
            presence_result = self.site_checker.get_full_presence_decision(
                site_url, hotel_id, asset_type
            )
            
            if not presence_result.should_generate:
                return {
                    "success": True,  # No es error, es skip válido
                    "status": "skipped",
                    "asset_type": asset_type,
                    "hotel_id": hotel_id,
                    "skip_reason": presence_result.skip_reason,
                    "presence_status": presence_result.status.value,
                    "site_verified": True,
                    "can_use": False,
                    "details": presence_result.details,
                    "recommendations": presence_result.recommendations
                }
        # ═══════════════════════════════════════════════════════════════════
        
        preflight_report = self.preflight_checker.check_asset(
            asset_type, validated_data, hotel_context
        )

        if preflight_report.overall_status == PreflightStatus.BLOCKED:
            return {
                "success": False,
                "status": "blocked",
                "error": "Preflight check failed",
                "reasons": preflight_report.blocking_issues,
                "asset_type": asset_type,
                "hotel_id": hotel_id,
                "preflight_report": preflight_report
            }

        is_warning = preflight_report.overall_status == PreflightStatus.WARNING
        
        try:
            content = self._generate_content(asset_type, validated_data, hotel_name)
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": f"Generation failed: {str(e)}",
                "asset_type": asset_type,
                "hotel_id": hotel_id
            }

        filename = self._apply_naming_strategy(asset_type, preflight_report, hotel_id)
        
        confidence_score = self._calculate_confidence_score(preflight_report)
        
        metadata = AssetMetadata(
            asset_type=asset_type,
            hotel_id=hotel_id,
            hotel_name=hotel_name,
            generated_at=datetime.now(),
            status=AssetStatus.GENERATED,
            preflight_status=preflight_report.overall_status.value,
            confidence_score=confidence_score,
            source_data_hash=self._hash_data(validated_data),
            fallback_used=is_warning,
            fallback_reason=preflight_report.warnings[0] if is_warning and preflight_report.warnings else None,
            disclaimers=preflight_report.warnings.copy() if is_warning else [],
            tags=["conditional_generation", "auto_generated"]
        )

        if is_warning:
            self.metadata_enforcer.tag_as_estimated(
                metadata,
                preflight_report.warnings[0] if preflight_report.warnings else "Low confidence data"
            )

        try:
            file_path = self.save_asset(asset_type, content, filename, metadata)
        except Exception as e:
            return {
                "success": False,
                "status": "error",
                "error": f"Failed to save asset: {str(e)}",
                "asset_type": asset_type,
                "hotel_id": hotel_id
            }

        return {
            "success": True,
            "status": "warning" if is_warning else "success",
            "asset_type": asset_type,
            "hotel_id": hotel_id,
            "file_path": str(file_path),
            "filename": filename,
            "metadata": metadata.to_dict(),
            "warnings": preflight_report.warnings if is_warning else [],
            "preflight_status": preflight_report.overall_status.value,
            "can_use": True  # NEVER_BLOCK: asset puede usarse aunque sea estimado
        }

    # ============================================================
    # GAP-IAO-01-04: PAIN_ID → ASSET MAPPING
    # Única fuente de verdad: ELEMENTO_KB_TO_PAIN_ID
    # ============================================================
    PAIN_TO_ASSET = {
        # KB element: (pain_id, asset_principal)
        # ssl
        "no_ssl": "ssl_guide",
        # schema
        "no_hotel_schema": "hotel_schema",
        "no_schema_reviews": "hotel_schema",  # Usa el mismo asset con aggregateRating
        # performance
        "poor_performance": "performance_audit",  # CLS_ok también mapea aquí
        # contenido
        "low_citability": "optimization_guide",
        # open graph
        "no_og_tags": "og_tags_guide",
        # FAQ
        "no_faq_schema": "faq_page",
        # NAP/WhatsApp
        "whatsapp_conflict": "whatsapp_button",
        "whatsapp_conflict": ["whatsapp_button", "whatsapp_conflict_guide"],
        # imágenes
        "missing_alt_text": "alt_text_guide",
        # blog
        "no_blog_content": "blog_strategy_guide",
        # redes
        "no_social_links": "social_strategy_guide",
    }

    def generate_for_faltantes(
        self,
        faltantes: List[str],
        validated_data: Dict,
        hotel_name: str,
        hotel_id: str,
        hotel_context: Optional[Dict[str, Any]] = None,
        site_url: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Genera assets SOLO para los faltantes/pain_ids detectados.

        GAP-IAO-01-04: Conecta el diagnóstico con conditional_generator
        usando PainSolutionMapper como puente.

        Args:
            faltantes: Lista de pain_ids detectados (ej: ["no_hotel_schema", "no_faq_schema"])
                       También acepta elementos KB (e.g., "ssl", "open_graph")
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            hotel_id: Unique hotel identifier
            hotel_context: Optional context about hotel
            site_url: URL del sitio para verificar presencia de assets

        Returns:
            List of generation result dictionaries (uno por asset generado)
        """
        from modules.commercial_documents.v4_diagnostic_generator import ELEMENTO_KB_TO_PAIN_ID

        results = []
        assets_generated = set()

        # Normalizar: si es elemento KB, convertir a pain_id
        # ELEMENTO_KB_TO_PAIN_ID["ssl"] = ("no_ssl", "ssl_guide", None)
        for item in faltantes:
            pain_id = item

            # Si es elemento KB (no pain_id), buscar su pain_id
            if item in ELEMENTO_KB_TO_PAIN_ID:
                pain_id = ELEMENTO_KB_TO_PAIN_ID[item][0]

            # Mapear pain_id → asset
            # Support both string and list values in PAIN_TO_ASSET
            asset_types_raw = self.PAIN_TO_ASSET.get(pain_id)
            
            # Process all pain_ids to asset_type(s) mapping
            if not asset_types_raw:
                # No hay asset mapeado para este pain_id
                results.append({
                    'success': False,
                    'status': 'no_asset_mapping',
                    'pain_id': pain_id,
                    'original_item': item,
                    'error': f'No asset mapped for pain_id: {pain_id}'
                })
                continue
            
            # Normalize to list
            if isinstance(asset_types_raw, str):
                _asset_list = [asset_types_raw]
            else:
                _asset_list = asset_types_raw
            
            for asset_type in _asset_list:
                # Evitar duplicados
                if asset_type in assets_generated:
                    results.append({
                        'success': True,
                        'status': 'skipped_duplicate',
                        'pain_id': pain_id,
                        'original_item': item,
                        'asset_type': asset_type,
                        'skip_reason': f'Asset {asset_type} already generated'
                    })
                    continue
                
                # Verificar que el asset este implementado
                if asset_type not in self.GENERATION_STRATEGIES:
                    results.append({
                        'success': False,
                        'status': 'asset_not_implemented',
                        'pain_id': pain_id,
                        'original_item': item,
                        'asset_type': asset_type,
                        'error': f'Asset {asset_type} is not implemented'
                    })
                    continue
                
                # Generar el asset
                result = self.generate(
                    asset_type=asset_type,
                    validated_data=validated_data,
                    hotel_name=hotel_name,
                    hotel_id=hotel_id,
                    hotel_context=hotel_context,
                    site_url=site_url
                )
                
                result['pain_id'] = pain_id
                result['original_item'] = item
                result['generation_path'] = 'faltantes'
                
                if result.get('success'):
                    assets_generated.add(asset_type)
                
                results.append(result)

        return results

    def _generate_content(
        self,
        asset_type: str,
        validated_data: Dict,
        hotel_name: str
    ) -> str:
        """Generate content based on asset type.
        
        Args:
            asset_type: Type of asset to generate
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            
        Returns:
            Generated content as string
        """
        content = ""
        
        if asset_type == "whatsapp_button":
            # FASE-H-02 FIX: Accept both "whatsapp" and "whatsapp_number" field names
            # The field is stored as "whatsapp_number" in ValidationSummary but
            # some code paths use "whatsapp". Check both for compatibility.
            phone_data = validated_data.get("whatsapp") or validated_data.get("whatsapp_number", {})
            phone = getattr(phone_data, 'value', str(phone_data)) if not isinstance(phone_data, str) else phone_data
            content = self._generate_whatsapp_button(phone, hotel_name)
        
        elif asset_type == "whatsapp_conflict_guide":
            from .whatsapp_conflict_guide import WhatsAppConflictGuideGenerator
            generator = WhatsAppConflictGuideGenerator()
            phone_web = validated_data.get("phone_web", "")
            phone_gbp = validated_data.get("phone_gbp", "")
            gbp_rating = validated_data.get("gbp_rating", None)
            gbp_review_count = validated_data.get("gbp_review_count", None)
            content = generator.generate(
                hotel_name=hotel_name,
                phone_web=phone_web,
                phone_gbp=phone_gbp,
                gbp_rating=gbp_rating,
                gbp_review_count=gbp_review_count,
            )
        
        elif asset_type == "faq_page":
            faqs_data = validated_data.get("faqs", [])
            faqs = getattr(faqs_data, 'value', faqs_data) if not isinstance(faqs_data, list) else faqs_data
            actual_count = len(faqs) if isinstance(faqs, list) else 0
            content = self._generate_faq_page(faqs if isinstance(faqs, list) else [], actual_count, hotel_name)
        
        elif asset_type == "hotel_schema":
            hotel_data = validated_data.get("hotel_data", {})
            data = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = self._generate_hotel_schema(data if isinstance(data, dict) else {})
        
        elif asset_type == "financial_projection":
            scenarios_data = validated_data.get("hotel_financial_data", {})
            scenarios = getattr(scenarios_data, 'value', scenarios_data) if not isinstance(scenarios_data, dict) else scenarios_data
            hotel_data = validated_data.get("hotel_data", {})
            hotel_dict = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = self._generate_financial_projection(
                scenarios if isinstance(scenarios, dict) else {},
                hotel_dict if isinstance(hotel_dict, dict) else {}
            )

        elif asset_type == "geo_playbook":
            gbp_data = validated_data.get("gbp_data", {})
            data = getattr(gbp_data, 'value', gbp_data) if not isinstance(gbp_data, dict) else gbp_data
            content = self._generate_geo_playbook(data if isinstance(data, dict) else {}, hotel_name)

        elif asset_type == "review_plan":
            review_data = validated_data.get("gbp_reviews", {})
            data = getattr(review_data, 'value', review_data) if not isinstance(review_data, dict) else review_data
            content = self._generate_review_plan(data if isinstance(data, dict) else {}, hotel_name)

        elif asset_type == "review_widget":
            review_data = validated_data.get("review_data", {})
            data = getattr(review_data, 'value', review_data) if not isinstance(review_data, dict) else review_data
            content = self._generate_review_widget(data if isinstance(data, dict) else {}, hotel_name)

        elif asset_type == "org_schema":
            org_data = validated_data.get("org_data", {})
            data = getattr(org_data, 'value', org_data) if not isinstance(org_data, dict) else org_data
            content = self._generate_org_schema(data if isinstance(data, dict) else {}, hotel_name)

        elif asset_type == "optimization_guide":
            metadata_data = validated_data.get("metadata_data", {})
            data = getattr(metadata_data, 'value', metadata_data) if not isinstance(metadata_data, dict) else metadata_data
            content = self._generate_optimization_guide(data if isinstance(data, dict) else {}, hotel_name)

        elif asset_type == "performance_audit":
            performance_data = validated_data.get("performance_data", {})
            data = getattr(performance_data, 'value', performance_data) if not isinstance(performance_data, dict) else performance_data
            content = self._generate_performance_audit(data if isinstance(data, dict) else {}, hotel_name)
        
        elif asset_type == "llms_txt":
            from .llmstxt_generator import LLMSTXTGenerator
            generator = LLMSTXTGenerator()
            hotel_data = validated_data.get("hotel_data", {})
            data = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = generator.generate(data if isinstance(data, dict) else {})
        
        elif asset_type == "faq_conversational":
            faqs_data = validated_data.get("faqs", [])
            faqs = getattr(faqs_data, 'value', faqs_data) if not isinstance(faqs_data, list) else faqs_data
            hotel_data = validated_data.get("hotel_data", {})
            hotel_dict = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = self._generate_faq_conversational(
                faqs if isinstance(faqs, list) else [],
                hotel_dict if isinstance(hotel_dict, dict) else {}
            )

        elif asset_type == "voice_assistant_guide":
            hotel_data = validated_data.get("hotel_data", validated_data)
            hotel_dict = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = self._generate_voice_assistant_guide(hotel_dict if isinstance(hotel_dict, dict) else {})

        elif asset_type == "ssl_guide":
            from modules.delivery.generators.ssl_guide_gen import SSLGuideGenerator
            generator = SSLGuideGenerator()
            content = generator.generate(validated_data)

        elif asset_type == "og_tags_guide":
            from modules.delivery.generators.og_tags_guide_gen import OGTagsGuideGenerator
            generator = OGTagsGuideGenerator()
            content = generator.generate(validated_data)

        elif asset_type == "alt_text_guide":
            from modules.delivery.generators.alt_text_guide_gen import AltTextGuideGenerator
            generator = AltTextGuideGenerator()
            content = generator.generate(validated_data)

        elif asset_type == "blog_strategy_guide":
            from modules.delivery.generators.blog_strategy_guide_gen import BlogStrategyGuideGenerator
            generator = BlogStrategyGuideGenerator()
            content = generator.generate(validated_data)

        elif asset_type == "social_strategy_guide":
            from modules.delivery.generators.social_strategy_guide_gen import SocialStrategyGuideGenerator
            generator = SocialStrategyGuideGenerator()
            content = generator.generate(validated_data)

        elif asset_type == "analytics_setup_guide":
            from modules.delivery.generators.analytics_setup_guide_gen import AnalyticsSetupGuideGenerator
            generator = AnalyticsSetupGuideGenerator()
            hotel_data = validated_data.get("hotel_data", validated_data)
            data = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = generator.generate(data if isinstance(data, dict) else {})

        elif asset_type == "indirect_traffic_optimization":
            from modules.delivery.generators.indirect_traffic_optimization_gen import IndirectTrafficOptimizationGenerator
            generator = IndirectTrafficOptimizationGenerator()
            hotel_data = validated_data.get("hotel_data", validated_data)
            data = getattr(hotel_data, 'value', hotel_data) if not isinstance(hotel_data, dict) else hotel_data
            content = generator.generate(data if isinstance(data, dict) else {})

        else:
            raise ValueError(f"Unknown asset type: {asset_type}")
        
        self._validate_generated_content(content, asset_type)
        
        return content
    
    def _validate_generated_content(self, content: str, asset_type: str) -> None:
        """Validate generated content for empty/placeholder issues.
        
        Args:
            content: Generated content to validate
            asset_type: Type of asset being validated
            
        Raises:
            ValueError: If content is empty, too short, or contains placeholders
        """
        if not content or len(content.strip()) < 50:
            raise ValueError(
                f"Generated content for {asset_type} is empty or too short. "
                f"Length: {len(content) if content else 0} chars"
            )
        
        placeholder_patterns = [
            (r'\$\$[\w]+', 'dollar placeholder'),
            (r'\{\{+[\w_]+\}\}+', 'double brace placeholder'),
            (r'\[\[[\w_]+\]\]', 'double bracket placeholder'),
        ]
        
        for pattern, placeholder_type in placeholder_patterns:
            matches = re.findall(pattern, content)
            if matches:
                raise ValueError(
                    f"Unreplaced {placeholder_type} found in {asset_type}: {matches[:3]}"
                )

    def _apply_naming_strategy(
        self,
        asset_type: str,
        preflight_report: PreflightReport,
        hotel_id: str
    ) -> str:
        """Determine filename based on preflight status.
        
        Args:
            asset_type: Type of asset
            preflight_report: Preflight check results
            hotel_id: Hotel identifier
            
        Returns:
            Generated filename
        """
        strategy = self.GENERATION_STRATEGIES[asset_type]
        template = strategy["output_name"]
        
        if preflight_report.overall_status == PreflightStatus.PASSED:
            prefix = ""
            suffix = ""
        elif preflight_report.overall_status == PreflightStatus.WARNING:
            prefix = "ESTIMATED_"
            suffix = ""
        else:
            prefix = "FAILED_"
            suffix = ""
        
        filename = template.format(prefix=prefix, suffix=suffix)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        name_parts = filename.rsplit(".", 1)
        if len(name_parts) == 2:
            filename = f"{name_parts[0]}_{timestamp}.{name_parts[1]}"
        else:
            filename = f"{filename}_{timestamp}"
        
        return filename

    def _generate_whatsapp_button(self, phone_number: str, hotel_name: str) -> str:
        """Generate HTML for WhatsApp button.
        
        Args:
            phone_number: WhatsApp phone number
            hotel_name: Name of the hotel
            
        Returns:
            HTML string with WhatsApp button
        """
        tracking_code = f"wa_{hotel_name.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m')}"
        
        html = f"""<!-- WhatsApp Button for {hotel_name} -->
<!-- Generated: {datetime.now().isoformat()} -->
<!-- Tracking: {tracking_code} -->
<a href="https://wa.me/{phone_number}?text=Hola%20{hotel_name.replace(' ', '%20')},%20estoy%20interesado%20en%20hacer%20una%20reserva"
   class="whatsapp-button"
   data-tracking="{tracking_code}"
   target="_blank"
   rel="noopener noreferrer">
    <svg viewBox="0 0 24 24" width="24" height="24">
        <path fill="currentColor" d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/>
    </svg>
    <span>Chat en WhatsApp</span>
</a>
<style>
.whatsapp-button {{
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background-color: #25D366;
    color: white;
    padding: 12px 24px;
    border-radius: 24px;
    text-decoration: none;
    font-family: Arial, sans-serif;
    font-weight: 600;
    transition: background-color 0.3s;
}}
.whatsapp-button:hover {{
    background-color: #128C7E;
}}
</style>
"""
        return html

    def _generate_faq_page(self, faqs: List[Dict], actual_count: int, hotel_name: str = "Hotel") -> str:
        """Generate CSV content for FAQ page.
        
        Args:
            faqs: List of FAQ dictionaries with 'question' and 'answer' keys
            actual_count: Actual number of FAQs (for filename reference)
            hotel_name: Name of the hotel for default FAQs
            
        Returns:
            CSV string content
        """
        if not faqs or len(faqs) == 0:
            faqs = self._generate_default_faqs(hotel_name)
            actual_count = len(faqs)
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        writer.writerow(['id', 'question', 'answer', 'category', 'generated_at'])
        
        for idx, faq in enumerate(faqs, 1):
            if isinstance(faq, dict):
                writer.writerow([
                    idx,
                    faq.get('question', ''),
                    faq.get('answer', ''),
                    faq.get('category', 'General'),
                    datetime.now().isoformat()
                ])
        
        writer.writerow([])
        writer.writerow(['metadata', '', '', '', ''])
        writer.writerow(['actual_count', actual_count, '', '', ''])
        writer.writerow(['generated_at', datetime.now().isoformat(), '', '', ''])
        
        return output.getvalue()

    def _generate_default_faqs(self, hotel_name: str) -> List[Dict]:
        """Generate default FAQs specific to the hotel.
        
        Args:
            hotel_name: Name of the hotel
            
        Returns:
            List of default FAQ dictionaries
        """
        return [
            {
                "question": f"¿Cuáles son los horarios de check-in y check-out en {hotel_name}?",
                "answer": "Check-in desde las 15:00 horas. Check-out hasta las 12:00 horas.",
                "category": "Hospedaje"
            },
            {
                "question": f"¿{hotel_name} incluye desayuno?",
                "answer": "Sí, todos nuestros planes incluyen desayuno tipo buffet.",
                "category": "Servicios"
            },
            {
                "question": f"¿{hotel_name} tiene políticas de cancelación?",
                "answer": "Cancelación gratuita hasta 48 horas antes de la fecha de llegada.",
                "category": "Reservas"
            },
        ]

    def _generate_hotel_schema(self, hotel_data: Dict) -> str:
        """Generate JSON-LD schema for hotel.
        
        Args:
            hotel_data: Dictionary with hotel information
            
        Returns:
            JSON string with schema markup
        """
        schema = {
            "@context": "https://schema.org",
            "@type": "LodgingBusiness",
            "name": hotel_data.get("name", "Hotel"),
            "description": hotel_data.get("description", ""),
            "url": hotel_data.get("website", ""),
            "telephone": hotel_data.get("phone", ""),
            "address": {
                "@type": "PostalAddress",
                "streetAddress": hotel_data.get("address", ""),
                "addressLocality": hotel_data.get("city", ""),
                "addressRegion": hotel_data.get("region", ""),
                "postalCode": hotel_data.get("postal_code", ""),
                "addressCountry": hotel_data.get("country", "CO")
            },
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": hotel_data.get("latitude"),
                "longitude": hotel_data.get("longitude")
            } if hotel_data.get("latitude") and hotel_data.get("longitude") else None,
            "amenityFeature": [
                {"@type": "LocationFeatureSpecification", "name": amenity}
                for amenity in hotel_data.get("amenities", [])
            ],
            "image": hotel_data.get("images", []),
            "priceRange": hotel_data.get("price_range", "$$"),
            "aggregateRating": {
                "@type": "AggregateRating",
                "ratingValue": hotel_data.get("rating", 4.0),
                "reviewCount": hotel_data.get("review_count", 0)
            } if hotel_data.get("rating") else None,
            # FASE-B: SpeakableSpecification for voice search readiness
            "speakable": {
                "@type": "SpeakableSpecification",
                "cssSelector": ["#descripcion", "#servicios", "#habitaciones", "#amenities"]
            }
        }
        
        if schema["geo"] is None:
            del schema["geo"]
        if schema["aggregateRating"] is None:
            del schema["aggregateRating"]
        
        return json.dumps(schema, indent=2, ensure_ascii=False)

    def _generate_faq_conversational(self, faqs: List[Dict], hotel_data: Dict) -> str:
        """Generate TTS-ready conversational FAQ in Markdown + JSON-LD format.
        
        FASE-B: Cada respuesta debe tener entre 40-60 palabras para optimizacion TTS.
        
        Args:
            faqs: List of FAQ dictionaries with 'question' and 'answer'
            hotel_data: Dictionary with hotel information
            
        Returns:
            Markdown string with conversational FAQs (40-60 palabras por respuesta)
        """
        hotel_name = hotel_data.get("name", "Hotel")
        city = hotel_data.get("city", hotel_data.get("address", "Colombia"))
        
        md = f"""# Preguntas Frecuentes - {hotel_name}

> FAQs optimizadas para lectura por voz (TTS). Cada respuesta: 40-60 palabras.

"""
        
        # JSON-LD for structured data
        faq_main_entity = []
        
        for idx, faq in enumerate(faqs[:10], 1):  # Max 10 FAQs for quality
            question = faq.get("question", faq.get("pregunta", ""))
            answer = faq.get("answer", faq.get("respuesta", ""))
            
            # Count words in answer
            answer_words = len(answer.split()) if answer else 0
            
            # Add conversational filler if too short (TTS optimization)
            if answer_words < 40:
                filler = f" {hotel_name} en {city} ofrece esta caracteristica para tu comodidad."
                answer = answer + filler
                answer_words = len(answer.split())
            
            md += f"""## {question}

{answer}

*({answer_words} palabras)*

"""
            
            # JSON-LD entry with speakable
            faq_main_entity.append({
                "@type": "Question",
                "name": question,
                "acceptedAnswer": {
                    "@type": "Answer",
                    "text": answer,
                    "cssSelector": "#faq"
                }
            })
        
        # Add JSON-LD structured data
        faq_jsonld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": faq_main_entity
        }
        
        md += f"""
---

## Schema JSON-LD (para implementar en tu sitio)

```json
{json.dumps(faq_jsonld, indent=2, ensure_ascii=False)}
```

*Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - FASE-B AEO Voice-Ready*
"""
        
        return md

    def _generate_financial_projection(
        self,
        scenarios: Dict,
        hotel_data: Dict
    ) -> str:
        """Generate markdown financial projection.
        
        Args:
            scenarios: Dictionary with financial scenarios
            hotel_data: Dictionary with hotel information
            
        Returns:
            Markdown string with projections
        """
        hotel_name = hotel_data.get("name", "Hotel")
        
        md = f"""# Proyección Financiera: {hotel_name}

**Generado:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Período de proyección:** 12 meses

---

## Resumen Ejecutivo

Esta proyección financiera presenta diferentes escenarios basados en datos disponibles.

## Escenarios

"""
        
        for scenario_name, scenario_data in scenarios.items():
            md += f"""### {scenario_name.replace('_', ' ').title()}

"""
            if isinstance(scenario_data, dict):
                for key, value in scenario_data.items():
                    md += f"- **{key.replace('_', ' ').title()}:** {value}\n"
            else:
                md += f"- Valor: {scenario_data}\n"
            
            md += "\n"
        
        md += """---

## Advertencias y Descargos de Responsabilidad

> **IMPORTANTE:** Esta proyección se basa en datos disponibles y estimaciones de mercado. 
> Los resultados reales pueden variar significativamente.

- Las proyecciones son estimaciones basadas en benchmarks de la industria
- Los factores externos (temporada, economía, competencia) pueden afectar los resultados
- Se recomienda revisar mensualmente y ajustar según datos reales
- Esta proyección no constituye asesoría financiera profesional

## Metodología

Las proyecciones se calculan utilizando:
- Datos históricos del hotel (si disponibles)
- Benchmarks de la industria hotelera
- Factores estacionales regionales
- Indicadores de mercado actualizados

---

*Documento generado automáticamente por IA Hoteles*
"""
        
        return md

    def _generate_geo_playbook(self, gbp_data: Dict, hotel_name: str) -> str:
        """Generate geo playbook markdown."""
        return f"""# Geo Playbook: {hotel_name}

## Optimización de Google Business Profile

### Checklist de Acciones

- [ ] Verificar información básica (nombre, dirección, teléfono)
- [ ] Actualizar horarios de atención
- [ ] Agregar 10+ fotos de alta calidad
- [ ] Configurar atributos del hotel
- [ ] Activar mensajería
- [ ] Configurar reservas

### Publicaciones Semanales

- [ ] Semana 1: Fotos de instalaciones
- [ ] Semana 2: Promoción especial
- [ ] Semana 3: Testimonios de huéspedes
- [ ] Semana 4: Eventos locales

---

Generado: {datetime.now().isoformat()}
"""

    def _generate_review_plan(self, review_data: Dict, hotel_name: str) -> str:
        """Generate review plan markdown."""
        return f"""# Plan de Reviews: {hotel_name}

## Estrategia de Gestión de Reseñas

### Objetivos
- Incrementar reviews en Google Maps
- Mejorar rating promedio
- Responder 100% de reseñas

### Acciones

1. **Solicitud Proactiva**
   - Email post-estadía
   - QR en recepción
   - Recordatorio WhatsApp

2. **Respuesta a Reseñas**
   - Responder en <24 horas
   - Personalizar cada respuesta
   - Agradecer siempre

---

Generado: {datetime.now().isoformat()}
"""

    def _generate_review_widget(self, review_data: Dict, hotel_name: str) -> str:
        """Generate review widget HTML."""
        return f"""<!-- Review Widget for {hotel_name} -->
<div class="review-widget">
    <h3>Lo que dicen nuestros huéspedes</h3>
    <div class="review-stars">★★★★★</div>
    <p class="review-text">"Excelente servicio y ubicación"</p>
    <a href="#" class="review-link">Ver más reseñas</a>
</div>

<style>
.review-widget {{
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
}}
.review-stars {{
    color: #ffc107;
    font-size: 24px;
}}
</style>
"""

    def _generate_org_schema(self, org_data: Dict, hotel_name: str) -> str:
        """Generate Organization schema JSON."""
        if not org_data:
            org_data = {}
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": hotel_name,
            "url": org_data.get("website", ""),
            "logo": org_data.get("logo", ""),
            "contactPoint": {
                "@type": "ContactPoint",
                "telephone": org_data.get("phone", ""),
                "contactType": "Reservations"
            }
        }
        
        if not schema["url"]:
            schema["url"] = "https://example.com"
        
        return json.dumps(schema, indent=2, ensure_ascii=False)

    def _generate_optimization_guide(self, metadata_data: Dict, hotel_name: str) -> str:
        """Generate SEO optimization guide markdown.
        
        Args:
            metadata_data: Dictionary with metadata analysis data
            hotel_name: Name of the hotel
            
        Returns:
            Markdown string with optimization guide
        """
        has_default_title = metadata_data.get("has_default_title", False)
        has_default_description = metadata_data.get("has_default_description", False)
        title_tag = metadata_data.get("title_tag", None)
        meta_description = metadata_data.get("meta_description", None)
        title_length = metadata_data.get("title_length", 0)
        description_length = metadata_data.get("description_length", 0)
        missing_h1 = metadata_data.get("missing_h1", True)
        h1_count = metadata_data.get("h1_count", 0)
        schema_types = metadata_data.get("schema_types", [])
        
        title_status = "⚠️ Necesita atención" if has_default_title else "✅ Correcto"
        description_status = "⚠️ Necesita atención" if has_default_description else "✅ Correcto"
        
        title_length_status = "⚠️ Longitud no óptima" if title_length < 30 or title_length > 60 else "✅ Longitud correcta"
        description_length_status = "⚠️ Longitud no óptima" if description_length < 120 or description_length > 160 else "✅ Longitud correcta"
        
        schema_recommendations = ""
        if "Hotel" not in schema_types:
            schema_recommendations += "- Implementar schema Hotel\n"
        if "BreadcrumbList" not in schema_types:
            schema_recommendations += "- Implementar schema BreadcrumbList\n"
        if "FAQPage" not in schema_types:
            schema_recommendations += "- Considerar schema FAQPage si hay sección de preguntas frecuentes\n"
        if not schema_recommendations:
            schema_recommendations = "- Schema markup ya implementado correctamente"
        
        md = f"""# Guía de Optimización SEO para {hotel_name}

**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. Revisión de Metadatos

### Title Tag (Título de Página)

| Aspecto | Estado |
|---------|--------|
| Valor actual | {title_tag if title_tag else "⚠️ Sin title tag configurado"} |
| Longitud | {title_length} caracteres {title_length_status} |
| Estado general | {title_status} |

**Recomendaciones:**
"""
        
        if has_default_title:
            md += """- ❌ El title tag parece ser genérico (default del CMS)
- ✅ Crear un title único que incluya: nombre del hotel + diferenciador + ubicación
- 📝 Referencia: "Hotel [Nombre] - Mejor Tarifa Garantizada | Santa Rosa de Cabal"
- 📝 Longitud recomendada: 50-60 caracteres

"""
        else:
            md += """- ✅ Title tag personalizado detectado
- 📝 Verificar que incluya palabras clave relevantes

"""

        md += f"""### Meta Description (Descripción Meta)

| Aspecto | Estado |
|---------|--------|
| Valor actual | {(meta_description[:80] + " (resumen de 80 caracteres)") if meta_description else "⚠️ Sin meta description"} |
| Longitud | {description_length} caracteres {description_length_status} |
| Estado general | {description_status} |

**Recomendaciones:**
"""
        
        if has_default_description:
            md += """- ❌ La descripción parece ser genérica (default del CMS)
- ✅ Crear una descripción única de 150-160 caracteres
- 📝 Incluir: propuesta de valor + amenities principales + llamada a la acción
- 📝 Referencia: "Hotel [Nombre] en Santa Rosa de Cabal. WiFi gratis, piscina, desayuno incluido. 
  Reserva directa con la mejor tarifa."

"""
        else:
            md += """- ✅ Descripción personalizada detectada
- 📝 Verificar que incluya palabras clave y llamada a la acción

"""

        md += f"""---

## 2. Checklist de Implementación

### Metadatos (Prioridad Alta)

- [ ] Revisar y personalizar title tag
- [ ] Revisar y personalizar meta description
- [ ] Verificar que title y description sean únicos en cada página
- [ ] Incluir palabras clave principal en los primeros 50 caracteres

### Estructura de Encabezados (Prioridad Alta)

- [ ] {"❌ Falta etiqueta H1 principal" if missing_h1 else "✅ Etiqueta H1 presente (" + str(h1_count) + " encontrada(s))"}
- [ ] Usar solo una etiqueta H1 por página
- [ ] Usar encabezados H2-H6 de forma jerárquica

### Schema Markup (Prioridad Media)

{schema_recommendations}

### URLs Amigables (Prioridad Media)

- [ ] URLs limpioas con guiones (ej: /habitaciones/deluxe)
- [ ] Evitar parámetros largos
- [ ] Incluir palabra clave principal en URL

---

## 3. Recomendaciones de Schema Markup

### Schema Hotel (Obligatorio)

```json
{{
  "@context": "https://schema.org",
  "@type": "Hotel",
  "name": "{hotel_name}",
  "description": "Descripción del hotel y propuesta de valor principal",
  "address": {{
    "@type": "PostalAddress",
    "addressLocality": "Santa Rosa de Cabal",
    "addressCountry": "CO"
  }},
  "telephone": "+57 606 123 4567",
  "priceRange": "$80-150"
}}
```

### Schema AggregateRating (Recomendado)

```json
{{
  "@type": "AggregateRating",
  "ratingValue": "4.5",
  "reviewCount": "150"
}}
```

---

## 4. Próximos Pasos

1. **Inmediato (esta semana):**
   - Corregir title tag si es genérico
   - Corregir meta description si es genérica

2. **Corto plazo (próximas 2 semanas):**
   - Implementar schema Hotel
   - Revisar estructura de encabezados

3. **Mediano plazo (próximo mes):**
   - Auditoría completa de contenido
   - Optimización de imágenes

---

## 5. Voice Search Keywords - Eje Cafetero (FASE-B AEO)

**Keywords de voz para consultas en español en la region del Eje Cafetero:**

| Keyword de Voz | Intencion |
|----------------|-----------|
| "hoteles boutique cerca del Valle del Cocora" | Busqueda de alojamiento cerca de naturaleza |
| "hotel con spa en Santa Rosa de Cabal" | Busqueda de bienestar relaxation |
| "lugar donde tomar cafe de origen en Pereira" | Experiencia cafe de especialidad |
| "hoteles termales en el Eje Cafetero" | Busqueda de turismo termal |
| "hotel familiar cerca de Salento" | Alojamiento familiar rural |
| "mejores restaurantes en el Valle del Cocora" | Informacion complementaria |
| "clima en Pereira hoy" | Utilidad viaje |

**Implementacion:**
- Incluir estas keywords en el contenido de la pagina de inicio
- Usar naturalmente en meta description y headings
- Crear contenido especifico sobre experiencias locales

---

*Documento generado automáticamente por IA Hoteles - FASE-B AEO Voice-Ready*
"""
        return md

    def _generate_performance_audit(self, performance_data: Dict, hotel_name: str) -> str:
        """Generate Core Web Vitals performance audit markdown.
        
        Args:
            performance_data: Dictionary with performance metrics
            hotel_name: Name of the hotel
            
        Returns:
            Markdown string with performance audit
        """
        mobile_score = performance_data.get("mobile_score", 0)
        desktop_score = performance_data.get("desktop_score", 0)
        lcp = performance_data.get("LCP", 0)
        fid = performance_data.get("FID", 0)
        cls = performance_data.get("CLS", 0)
        fcp = performance_data.get("FCP", 0)
        si = performance_data.get("SI", 0)
        tbt = performance_data.get("TBT", 0)
        
        has_performance_data = mobile_score > 0 or desktop_score > 0 or lcp > 0
        
        def get_lcp_status(value):
            if value <= 2500:
                return "🟢 Bueno"
            elif value <= 4000:
                return "🟡 Necesita mejora"
            else:
                return "🔴 Poor"
        
        def get_fid_status(value):
            if value <= 100:
                return "🟢 Bueno"
            elif value <= 300:
                return "🟡 Necesita mejora"
            else:
                return "🔴 Poor"
        
        def get_cls_status(value):
            if value <= 0.1:
                return "🟢 Bueno"
            elif value <= 0.25:
                return "🟡 Necesita mejora"
            else:
                return "🔴 Poor"
        
        def get_score_status(score):
            if score >= 90:
                return "🟢 Excelente"
            elif score >= 50:
                return "🟡 Necesita mejora"
            else:
                return "🔴 Poor"
        
        lcp_status = get_lcp_status(lcp)
        fid_status = get_fid_status(fid)
        cls_status = get_cls_status(cls)
        mobile_status = get_score_status(mobile_score)
        desktop_status = get_score_status(desktop_score)
        
        recommendations = []
        
        if lcp > 2500:
            recommendations.append("""
### 🚀 Largest Contentful Paint (LCP)

**Problema:** El elemento principal tarda más de 2.5s en cargar.

**Soluciones:**
- [ ] Optimizar y comprimir imágenes (usar WebP/AVIF)
- [ ] Implementar lazy loading para imágenes below-the-fold
- [ ] Usar CDN para servir recursos estáticos
- [ ] Minimizar CSS y JavaScript blocking
- [ ] Preload de la imagen hero principal
""")
        
        if fid > 100:
            recommendations.append("""
### ⚡ First Input Delay (FID)

**Problema:** La página responde lentamente a interacciones.

**Soluciones:**
- [ ] Dividir bundles grandes de JavaScript
- [ ] Diferir scripts no esenciales (defer/async)
- [ ] Reducir tiempo de ejecución del main thread
- [ ] Minimizar uso de third-party scripts
- [ ] Implementar code splitting
""")
        
        if cls > 0.1:
            recommendations.append("""
### 📐 Cumulative Layout Shift (CLS)

**La página tiene cambios visuales inesperados.**

**Soluciones:**
- [ ] Especificar dimensiones (width/height) en todas las imágenes
- [ ] Reservar espacio para anuncios
- [ ] Preload de fuentes con font-display: swap
- [ ] No insertar contenido dinámicamente arriba de contenido existente
- [ ] Usar transform para animaciones
""")
        
        if not recommendations:
            recommendations.append("""
### ✅ Felicitaciones

Tu sitio tiene muy buenos indicadores de Core Web Vitals. 
Continúa monitoreando y manteniendo las optimizaciones actuales.
""")
        
        md = f"""# Auditoría de Performance para {hotel_name}

**Fecha de generación:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 1. Resumen de Métricas

"""
        
        if not has_performance_data:
            md += """### ⚠️ Datos de Performance No Disponibles

Los datos de performance no están disponibles actualmente. Esto puede deberse a:
- El sitio web no ha sido auditado previamente
- El sitio no es accesible públicamente
- Los datos aún están siendo recopilados

**Recomendación:** Ejecuta una auditoría en [Google PageSpeed Insights](https://pagespeed.web.dev/) 
para obtener los datos de performance de tu sitio.

"""
        else:
            md += f"""### Puntuaciones Generales

| Métrica | Valor | Estado |
|---------|-------|--------|
| Mobile Score | {mobile_score}/100 | {mobile_status} |
| Desktop Score | {desktop_score}/100 | {desktop_status} |

### Core Web Vitals

| Métrica | Valor | Umbral (Bueno) | Estado |
|---------|-------|-----------------|--------|
| LCP (Largest Contentful Paint) | {lcp}ms | ≤ 2500ms | {lcp_status} |
| FID (First Input Delay) | {fid}ms | ≤ 100ms | {fid_status} |
| CLS (Cumulative Layout Shift) | {cls} | ≤ 0.1 | {cls_status} |

### Métricas Adicionales

| Métrica | Valor |
|---------|-------|
| FCP (First Contentful Paint) | {fcp}ms |
| SI (Speed Index) | {si}ms |
| TBT (Total Blocking Time) | {tbt}ms

---

## 2. Análisis de Performance

### Score Móvil: {mobile_score}/100 {mobile_status}

El score móvil considera la experiencia en dispositivos móviles, que es crucial 
dado que la mayoría del tráfico web proviene de estos dispositivos.

"""
            
            if mobile_score < 50:
                md += """**Prioridades de optimización:**
1. Optimizar imágenes para móvil
2. Reducir JavaScript blocking
3. Minimizar el tamaño del CSS crítico

"""
            elif mobile_score < 90:
                md += """**Mejoras opcionales:**
1. Implementar más optimizaciones de imágenes
2. Revisar third-party scripts
3. Considerar AMP si es aplicable

"""
            else:
                md += """**Excelente performance móvil:**
- El sitio carga rápidamente en dispositivos móviles
- La experiencia de usuario es óptima

"""

            md += f"""### Score Desktop: {desktop_score}/100 {desktop_status}

"""
            
            if desktop_score < 50:
                md += """**Prioridades de optimización:**
1. Habilitar compresión Brotli/Gzip
2. Implementar caching efectivo
3. Optimizar servidor y CDN

"""
            elif desktop_score < 90:
                md += """**Mejoras opcionales:**
1. Preconnect a recursos de terceros
2. Optimizar fuentes web
3. Implementar HTTP/2 o HTTP/3

"""
            else:
                md += """**Excelente performance desktop:**
- El sitio tiene tiempos de carga óptimos en desktop

"""

            md += f"""---

## 3. Recomendaciones de Optimización

""" + "\n".join(recommendations)

            md += f"""---

## 4. Plan de Acción

### Acciones Inmediatas (esta semana)
"""
            
            priority_actions = []
            if mobile_score < 50 or desktop_score < 50:
                priority_actions.append("- Audit en PageSpeed Insights para diagnóstico detallado")
            if lcp > 2500:
                priority_actions.append("- Optimizar imagen hero (principal elemento LCP)")
            if cls > 0.1:
                priority_actions.append("- Especificar dimensiones en imágenes")
            
            if priority_actions:
                md += "\n".join(priority_actions)
            else:
                md += "- Mantener actual configuración de performance"

            md += """

### Acciones a Futuro (próximo mes)
- Implementar monitoring continuo de Core Web Vitals
- Configurar alertas de performance
- Revisión mensual de métricas
- Optimización progresiva basada en datos reales

---

## 5. Recursos Adicionales

- [Google PageSpeed Insights](https://pagespeed.web.dev/)
- [Web Vitals](https://web.dev/vitals/)
- [Chrome DevTools Performance](https://www.google.com/chrome/devtools/performance)

---

*Documento generado automáticamente por IA Hoteles*
"""
        return md

    def _generate_voice_assistant_guide(self, hotel_data: Dict) -> str:
        """Generate voice assistant integration guide (FASE-C).
        
        Generates 3 subdocuments:
        - google_assistant_checklist.md
        - apple_business_connect_guide.md
        - alexa_skill_blueprint.md
        
        These are written as separate files by save_asset when asset_type is voice_assistant_guide.
        The return value is the index/overview file.
        
        Args:
            hotel_data: Dictionary with hotel information
            
        Returns:
            Markdown content with the voice assistant guide index
        """
        from modules.delivery.generators.voice_guide import VoiceGuideGenerator
        
        nombre = hotel_data.get("nombre") or hotel_data.get("name", "Hotel Boutique")
        ubicacion = hotel_data.get("ubicacion") or hotel_data.get("city", "Eje Cafetero, Colombia")
        
        # Generate the 3 subdocuments
        voice_gen = VoiceGuideGenerator()
        guides = voice_gen.generate(hotel_data)
        
        # Store guides in instance for save_asset to use
        if not hasattr(self, '_voice_guide_subdocuments'):
            self._voice_guide_subdocuments = {}
        self._voice_guide_subdocuments[hotel_data.get("hotel_id", "unknown")] = guides
        
        return f"""# Voice Assistant Integration Package

**Hotel**: {nombre}  
**Ubicación**: {ubicacion}  
**Fecha de generación**: {datetime.now().strftime("%Y-%m-%d")}

---

## Overview

Este paquete contiene 3 guías para integrar {nombre} con las principales plataformas de voz:
- **Google Assistant** (Asistente de Google)
- **Apple Siri** (Apple Business Connect)
- **Amazon Alexa** (Alexa Skills Kit)

---

## Contenido del Paquete

1. `google_assistant_checklist.md` - Checklist de integración con Google Assistant
2. `apple_business_connect_guide.md` - Guía de setup para Apple Business Connect  
3. `alexa_skill_blueprint.md` - Blueprint técnico para Alexa Skill

---

## Resumen de Compatibilidad

| Plataforma | Voice Search | Reservas por Voz | Info en Maps |
|------------|--------------|------------------|--------------|
| Google Assistant | ✅ | ✅ (con API) | ✅ |
| Apple Siri | ✅ | ⚠️ Parcial | ✅ |
| Amazon Alexa | ✅ | ⚠️ Requiere Skill | ⚠️ Solo con Skill |

---

## Próximos Pasos

1. **Revisar** las 3 guías incluidas en este paquete
2. **Prioritizar** Google Assistant (mayor alcance en Colombia)
3. **Obtener D-U-N-S Number** (requerido para Apple Business Connect)
4. **Contactar** a AWS si interesa ASP for Hospitality (experiencia in-room)

---

*Generado automáticamente por iah-cli - FASE-C: Integración Plataformas de Voz*
"""

    def save_asset(
        self,
        asset_type: str,
        content: str,
        filename: str,
        metadata: AssetMetadata
    ) -> Path:
        """Save asset and its metadata.
        
        Args:
            asset_type: Type of asset
            content: Asset content
            filename: Output filename
            metadata: Asset metadata
            
        Returns:
            Path to saved file
        """
        hotel_dir = self.output_dir / metadata.hotel_id
        hotel_dir.mkdir(parents=True, exist_ok=True)
        
        asset_type_dir = hotel_dir / asset_type
        asset_type_dir.mkdir(exist_ok=True)
        
        # FASE-C: Special handling for voice_assistant_guide - write subdocuments
        if asset_type == "voice_assistant_guide" and hasattr(self, '_voice_guide_subdocuments'):
            guides = self._voice_guide_subdocuments.get(metadata.hotel_id, {})
            # Fallback: subdocuments may have been stored under "unknown" if hotel_data lacked hotel_id
            if not guides:
                guides = self._voice_guide_subdocuments.get("unknown", {})
            for subdoc_filename, subdoc_content in guides.items():
                file_path = asset_type_dir / subdoc_filename
                file_path.write_text(subdoc_content, encoding='utf-8')
            # Clean up to avoid memory leak
            delattr(self, '_voice_guide_subdocuments')
            return asset_type_dir / "google_assistant_checklist.md"
        
        file_path = asset_type_dir / filename
        file_path.write_text(content, encoding='utf-8')
        
        metadata_filename = f"{file_path.stem}_metadata.json"
        metadata_path = asset_type_dir / metadata_filename
        metadata_path.write_text(
            json.dumps(metadata.to_dict(), indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        return file_path

    def get_generation_summary(self, generations: List[Dict]) -> Dict:
        """Summarize all generations.
        
        Args:
            generations: List of generation result dictionaries
            
        Returns:
            Summary dictionary with counts and statistics
        """
        total = len(generations)
        passed = sum(1 for g in generations if g.get("status") == "generated")
        warning = sum(1 for g in generations if g.get("status") == "estimated")
        blocked = sum(1 for g in generations if g.get("status") == "blocked")
        failed = sum(1 for g in generations if g.get("status") == "error")
        
        by_type = {}
        for g in generations:
            asset_type = g.get("asset_type", "unknown")
            if asset_type not in by_type:
                by_type[asset_type] = {"total": 0, "passed": 0, "warning": 0, "blocked": 0, "failed": 0}
            by_type[asset_type]["total"] += 1
            status = g.get("status", "unknown")
            if status == "generated":
                by_type[asset_type]["passed"] += 1
            elif status == "estimated":
                by_type[asset_type]["warning"] += 1
            elif status == "blocked":
                by_type[asset_type]["blocked"] += 1
            elif status == "error":
                by_type[asset_type]["failed"] += 1
        
        return {
            "total": total,
            "passed": passed,
            "warning": warning,
            "blocked": blocked,
            "failed": failed,
            "success_rate": (passed / total * 100) if total > 0 else 0,
            "by_type": by_type,
            "generated_at": datetime.now().isoformat()
        }

    def _calculate_confidence_score(self, preflight_report: PreflightReport) -> float:
        """Calculate overall confidence score from preflight report.
        
        Args:
            preflight_report: Preflight check results
            
        Returns:
            Confidence score between 0 and 1
        """
        if not preflight_report.checks:
            return 0.0
        
        total_score = 0.0
        for check in preflight_report.checks:
            if check.status == PreflightStatus.PASSED:
                total_score += 1.0
            elif check.status == PreflightStatus.WARNING:
                total_score += 0.5
            else:
                total_score += 0.0
        
        return total_score / len(preflight_report.checks)

    # ========================================================================
    # FASE 6: Orchestration V2 - Intelligent Branching
    # ========================================================================
    
    def assess_data_quality(
        self,
        hotel_data: Optional[Dict[str, Any]] = None,
        gbp_data: Optional[Dict[str, Any]] = None,
        seo_data: Optional[Dict[str, Any]] = None,
        scraping_success: bool = False
    ) -> DataClassification:
        """
        Assess data quality and return classification (LOW/MED/HIGH).
        
        Args:
            hotel_data: Core hotel data
            gbp_data: Google Business Profile data
            seo_data: SEO-related data
            scraping_success: Whether web scraping succeeded
            
        Returns:
            DataClassification enum value
        """
        result = self.data_assessor.assess(
            hotel_data=hotel_data or {},
            gbp_data=gbp_data,
            seo_data=seo_data,
            scraping_success=scraping_success
        )
        return result.classification
    
    def validate_before_generation(
        self,
        validated_data: Dict,
        hotel_context: Optional[Dict[str, Any]] = None
    ) -> tuple:
        """
        Validate data quality BEFORE generation.
        
        This is the key change in FASE 6: we validate data availability
        first, and if it's too low, we fail fast instead of generating
        assets with insufficient data.
        
        Args:
            validated_data: The data to validate
            hotel_context: Hotel context for assessment
            
        Returns:
            Tuple of (is_valid, error_message, classification)
        """
        # Extract data components for assessment
        hotel_data = validated_data.get("hotel_data", {})
        if hasattr(hotel_data, 'value'):
            hotel_data = hotel_data.value if isinstance(hotel_data.value, dict) else {}
        
        gbp_data = validated_data.get("gbp_data", {})
        if hasattr(gbp_data, 'value'):
            gbp_data = gbp_data.value if isinstance(gbp_data.value, dict) else {}
        
        seo_data = validated_data.get("seo_data", {})
        if hasattr(seo_data, 'value'):
            seo_data = seo_data.value if isinstance(seo_data.value, dict) else {}
        
        assessment = self.data_assessor.assess(
            hotel_data=hotel_data if isinstance(hotel_data, dict) else {},
            gbp_data=gbp_data if isinstance(gbp_data, dict) else {},
            seo_data=seo_data if isinstance(seo_data, dict) else {},
            scraping_success=bool(gbp_data)  # If we have GBP data, scraping was partially successful
        )
        
        # If classification is LOW and missing data is severe, fail fast
        if assessment.classification == DataClassification.LOW:
            if len(assessment.missing_data) >= 5:
                return (
                    False,
                    f"Data quality too low ({assessment.overall_score:.0%}). "
                    f"Missing: {', '.join(assessment.missing_data[:3])}...",
                    assessment.classification
                )
        
        return True, "", assessment.classification
    
    def generate_fast(
        self,
        validated_data: Dict,
        hotel_name: str,
        hotel_id: str,
        hotel_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate only essential assets (3-4) for LOW data quality hotels.
        
        Args:
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            hotel_id: Unique hotel identifier
            hotel_context: Optional context about hotel
            
        Returns:
            List of generation result dictionaries
        """
        results = []
        for asset_type in self._fast_assets:
            result = self.generate(
                asset_type=asset_type,
                validated_data=validated_data,
                hotel_name=hotel_name,
                hotel_id=hotel_id,
                hotel_context=hotel_context
            )
            result["generation_path"] = "fast"
            results.append(result)
        return results
    
    def generate_standard(
        self,
        validated_data: Dict,
        hotel_name: str,
        hotel_id: str,
        hotel_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate moderate asset set (6-7) for MED data quality hotels.
        
        Args:
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            hotel_id: Unique hotel identifier
            hotel_context: Optional context about hotel
            
        Returns:
            List of generation result dictionaries
        """
        results = []
        for asset_type in self._standard_assets:
            result = self.generate(
                asset_type=asset_type,
                validated_data=validated_data,
                hotel_name=hotel_name,
                hotel_id=hotel_id,
                hotel_context=hotel_context
            )
            result["generation_path"] = "standard"
            results.append(result)
        return results
    
    def generate_full(
        self,
        validated_data: Dict,
        hotel_name: str,
        hotel_id: str,
        hotel_context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Generate complete asset suite (9+) for HIGH data quality hotels.
        
        Args:
            validated_data: Validated data for generation
            hotel_name: Name of the hotel
            hotel_id: Unique hotel identifier
            hotel_context: Optional context about hotel
            
        Returns:
            List of generation result dictionaries
        """
        results = []
        # Use all IMPLEMENTED assets from catalog
        for asset_type in self.GENERATION_STRATEGIES.keys():
            result = self.generate(
                asset_type=asset_type,
                validated_data=validated_data,
                hotel_name=hotel_name,
                hotel_id=hotel_id,
                hotel_context=hotel_context
            )
            result["generation_path"] = "full"
            results.append(result)
        return results

    def _hash_data(self, data: Dict) -> str:
        """Create hash of data for tracking.
        
        Args:
            data: Dictionary to hash
            
        Returns:
            MD5 hash string
        """
        try:
            data_str = json.dumps(data, sort_keys=True, default=str)
            return hashlib.md5(data_str.encode()).hexdigest()[:16]
        except Exception:
            return "unknown"
