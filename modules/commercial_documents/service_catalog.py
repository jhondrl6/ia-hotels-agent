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
# FASE-A: identidad canónica servicio↔asset↔pain (Capa 2)
from modules.common.service_identity import SERVICE_IDENTITIES


@dataclass
class ServiceEntry:
    """A vendible service mapped to a pain."""
    service_name: str          # Name displayed in proposal
    asset_type: str            # Asset type that delivers this service
    pain_id: str               # Pain ID that triggers this service
    description: str           # Short description for the proposal


# =============================================================================
# SERVICE_CATALOG — PROYECCIÓN del registro canónico de identidad
# =============================================================================
# FASE-A: este catálogo era el único de los censados que cargaba la tripleta completa
# (servicio, asset, pain), y por eso fue la base de Capa 2. Ahora DERIVA de ella en vez
# de ser copia independiente: una copia es drift garantizado (V3/V14).
# El orden de SERVICE_IDENTITIES sostiene el orden de las filas en la propuesta.

SERVICE_CATALOG: Dict[str, ServiceEntry] = {
    identidad.key: ServiceEntry(
        service_name=identidad.service_name,
        asset_type=identidad.asset_type,
        pain_id=identidad.pain_id,
        description=identidad.description,
    )
    for identidad in SERVICE_IDENTITIES
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
