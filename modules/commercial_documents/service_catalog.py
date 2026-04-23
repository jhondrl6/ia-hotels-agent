"""
Service Catalog for Commercial Proposals v4.0.

Maps detected pains to vendible services with metadata.
Used by V4ProposalGenerator for dynamic service table generation.

Created by FASE-CAUSAL-REFACTOR.
"""

from dataclasses import dataclass
from typing import Dict, List, Optional


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
    # GEO / Maps
    "google_maps_optimizado": ServiceEntry(
        service_name="Google Maps Optimizado",
        asset_type="geo_playbook",
        pain_id="low_gbp_score",
        description="Aparece primero cuando alguien busca 'hotel cerca de...'",
    ),
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
        description="Sus guests reservan con 1 clic desde su web",
    ),
    # Schema / IA
    "datos_estructurados": ServiceEntry(
        service_name="Datos Estructurados",
        asset_type="hotel_schema",
        pain_id="no_hotel_schema",
        description="Información que Google y la IA leen automáticamente",
    ),
    # FAQ
    "pagina_faq": ServiceEntry(
        service_name="Página de FAQ",
        asset_type="faq_page",
        pain_id="no_faq_schema",
        description="Sus guests encuentran respuestas sin salir de su web",
    ),
    # Open Graph / Social
    "meta_tags_sociales": ServiceEntry(
        service_name="Meta Tags Sociales (Open Graph)",
        asset_type="open_graph",
        pain_id="no_og_tags",
        description="Sus fotos brillan cuando alguien comparte su link en redes",
    ),
    # Barra de reservas móvil
    "barra_reserva_movil": ServiceEntry(
        service_name="Barra de Reserva Móvil",
        asset_type="barra_reserva_movil",
        pain_id="no_motor_reservas",
        description="Motor de reservas optimizado para dispositivos móviles",
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


# Backwards-compatible lookup: service_name → asset_type
# Mirrors PROPOSAL_SERVICE_TO_ASSET for compatibility with gates.
SERVICE_TO_ASSET_LOOKUP: Dict[str, str] = {
    entry.service_name: entry.asset_type
    for entry in SERVICE_CATALOG.values()
}


__all__ = [
    "ServiceEntry",
    "SERVICE_CATALOG",
    "get_services_for_pains",
    "get_service_names_for_pains",
    "SERVICE_TO_ASSET_LOOKUP",
]
