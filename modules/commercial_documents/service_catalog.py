"""
Service Catalog for Commercial Proposals v4.0.

Maps detected pains to vendible services with metadata.
Used by V4ProposalGenerator for dynamic service table generation.

Created by FASE-CAUSAL-REFACTOR.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional

# FASE-3 ASSET-ALIGNMENT-ZIONE: Import proposal source of truth
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET


@dataclass
class ServiceEntry:
    """A vendible service mapped to a pain."""
    service_name: str          # Name displayed in proposal
    asset_type: str            # Asset type that delivers this service
    pain_id: str               # Pain ID that triggers this service
    description: str           # Short description for the proposal


# =============================================================================
# SERVICE_CATALOG — Complete mapping of pains → vendible services
# =============================================================================
# Each entry represents a service that can be sold in a commercial proposal.
# The pain_id links it to PainSolutionMapper.PAIN_SOLUTION_MAP.

SERVICE_CATALOG: Dict[str, ServiceEntry] = {
    # SEO
    "seo_local": ServiceEntry(
        service_name="SEO Local",
        asset_type="optimization_guide",
        pain_id="poor_performance",
        description="Para aparecer en las primeras posiciones de Google tradicional",
    ),
    # WhatsApp
    "boton_whatsapp": ServiceEntry(
        service_name="Botón de WhatsApp",
        asset_type="whatsapp_button",
        pain_id="no_whatsapp_visible",
        description="Sus huéspedes reservan con 1 clic desde su web",
    ),
    # Schema Hotel
    "schema_hotel": ServiceEntry(
        service_name="Schema Hotel",
        asset_type="hotel_schema",
        pain_id="no_hotel_schema",
        description="Datos estructurados para Google y IA sobre tu hotel",
    ),
    # Schema Organization
    "schema_organization": ServiceEntry(
        service_name="Schema Organization",
        asset_type="org_schema",
        pain_id="no_org_schema",
        description="Datos estructurados sobre la organización del hotel",
    ),
    # FAQ
    "pagina_faq": ServiceEntry(
        service_name="Página de FAQ",
        asset_type="faq_page",
        pain_id="no_faq_schema",
        description="Sus huéspedes encuentran respuestas sin salir de su web",
    ),
    # Open Graph / Social
    "meta_tags_sociales": ServiceEntry(
        service_name="Meta Tags Sociales (Open Graph)",
        asset_type="open_graph",
        pain_id="no_og_tags",
        description="Sus fotos brillan cuando alguien comparte su link en redes",
    ),
    # Informe Mensual
    "informe_mensual": ServiceEntry(
        service_name="Informe Mensual",
        asset_type="monthly_report",
        pain_id="no_monthly_report",
        description="Reporte mensual con metricas de rendimiento y oportunidades",
    ),
}


def get_services_for_pains(detected_pain_ids: List[str]) -> List[ServiceEntry]:
    """Return ServiceEntry list for detected pain IDs.
    
    Args:
        detected_pain_ids: List of pain IDs from PainSolutionMapper.detect_pains()
    
    Returns:
        List of ServiceEntry objects for services whose pain was detected.
        Duplicates are removed (if same service maps to multiple pains).
    """
    seen_service_keys: set = set()
    services: List[ServiceEntry] = []
    
    for pain_id in detected_pain_ids:
        for key, entry in SERVICE_CATALOG.items():
            if entry.pain_id == pain_id and key not in seen_service_keys:
                seen_service_keys.add(key)
                services.append(entry)
    
    return services


def get_service_names_for_pains(detected_pain_ids: List[str]) -> List[str]:
    """Return service names for detected pain IDs.
    
    Args:
        detected_pain_ids: List of pain IDs from PainSolutionMapper.detect_pains()
    
    Returns:
        List of service_name strings for services whose pain was detected.
    """
    services = get_services_for_pains(detected_pain_ids)
    return [s.service_name for s in services]


# FASE-D: AEO conditional service — included when score_aeo < 20
# Triggered by DiagnosticSummary.score_aeo field (0-100, from 4-pillars scoring)
SERVICE_CATALOG["optimizacion_ia_generativa"] = ServiceEntry(
    service_name="Optimización para IA Generativa",
    asset_type="llms_txt",
    pain_id="low_ia_readiness",
    description="Aparece cuando clientes preguntan a ChatGPT/Gemini 'dónde hospedarme en [región]'",
)


# Backwards-compatible lookup: service_name → asset_type
# FASE-3 ASSET-ALIGNMENT-ZIONE: Derived from PROPOSAL_SERVICE_TO_ASSET
# as the single source of truth, instead of SERVICE_CATALOG.
SERVICE_TO_ASSET_LOOKUP: Dict[str, str] = dict(PROPOSAL_SERVICE_TO_ASSET)


# =============================================================================
# TECHNICAL_ASSET_CATALOG — Assets técnicos adicionales (FASE-2)
# =============================================================================
# Estos assets no son servicios comerciales "vendibles" por sí solos,
# pero complementan el kit y se muestran en una sección dedicada de la propuesta.

@dataclass
class TechnicalAssetEntry:
    """A technical asset that supports the commercial package."""
    asset_name: str       # Name displayed in proposal
    asset_type: str       # Asset type identifier
    description: str      # Short description for the proposal


TECHNICAL_ASSET_CATALOG: Dict[str, TechnicalAssetEntry] = {
    "analytics_setup_guide": TechnicalAssetEntry(
        asset_name="Guía de Configuración Analytics",
        asset_type="analytics_setup_guide",
        description="Instrucciones paso a paso para conectar Google Analytics 4 y Google Search Console",
    ),
}


__all__ = [
    "ServiceEntry",
    "TechnicalAssetEntry",
    "SERVICE_CATALOG",
    "TECHNICAL_ASSET_CATALOG",
    "get_services_for_pains",
    "get_service_names_for_pains",
    "SERVICE_TO_ASSET_LOOKUP",
]
