"""
Asset Catalog - Single Source of Truth for Asset Types.

This module provides a centralized catalog of all available assets,
their status (IMPLEMENTED, MISSING, DEPRECATED, MANUAL_ONLY),
and helper functions to query the catalog.

Created as part of FASE-ASSET-02: Catálogo Unificado.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Dict, Any


class AssetStatus(Enum):
    """Status of an asset in the catalog."""
    IMPLEMENTED = "implemented"
    MISSING = "missing"
    DEPRECATED = "deprecated"
    MANUAL_ONLY = "manual_only"


@dataclass
class AssetCatalogEntry:
    """
    Entry in the Asset Catalog containing all metadata for an asset type.
    
    Attributes:
        asset_type: Unique identifier for the asset type
        template: Template file used for generation
        output_name: Output filename pattern with {prefix} and {suffix} placeholders
        required_field: Field name required in validated_data for generation
        required_confidence: Minimum confidence score required (0.0 - 1.0)
        fallback: Fallback action when confidence is below threshold
        block_on_failure: Whether to block generation if requirements not met
        status: Current status in the catalog
        promised_by: List of pain IDs that this asset promises to solve
    """
    asset_type: str
    template: str
    output_name: str
    required_field: str
    required_confidence: float
    fallback: str
    block_on_failure: bool
    status: AssetStatus
    promised_by: List[str]


# Asset Catalog - Single Source of Truth
# Based on docs/asset_catalog.md from FASE-ASSET-01
ASSET_CATALOG: Dict[str, AssetCatalogEntry] = {
    "whatsapp_button": AssetCatalogEntry(
        asset_type="whatsapp_button",
        template="whatsapp_template.html",
        output_name="{prefix}boton_whatsapp{suffix}.html",
        required_field="whatsapp",
        required_confidence=0.7,
        fallback="generate_basic_whatsapp",
        block_on_failure=False,  # NEVER_BLOCK: generar botón básico aunque falte WhatsApp
        status=AssetStatus.IMPLEMENTED,
        promised_by=["no_whatsapp_visible"]
    ),
    "faq_page": AssetCatalogEntry(
        asset_type="faq_page",
        template="faq_template.csv",
        output_name="{prefix}faqs{suffix}.csv",
        required_field="faqs",
        required_confidence=0.5,
        fallback="generate_with_actual_count",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["no_faq_schema"]
    ),
    "hotel_schema": AssetCatalogEntry(
        asset_type="hotel_schema",
        template="schema_template.json",
        output_name="{prefix}hotel_schema{suffix}.json",
        required_field="hotel_data",
        required_confidence=0.6,
        fallback="generate_basic_schema",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["no_hotel_schema"]
    ),
    "geo_playbook": AssetCatalogEntry(
        asset_type="geo_playbook",
        template="geo_playbook_template.md",
        output_name="{prefix}geo_playbook{suffix}.md",
        required_field="gbp_data",
        required_confidence=0.5,
        fallback="generate_basic_geo_guide",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["low_gbp_score"]
    ),
    "review_plan": AssetCatalogEntry(
        asset_type="review_plan",
        template="review_plan_template.md",
        output_name="{prefix}plan_reviews{suffix}.md",
        required_field="gbp_reviews",
        required_confidence=0.4,
        fallback="generate_template_plan",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["low_gbp_score", "missing_reviews"]
    ),
    "review_widget": AssetCatalogEntry(
        asset_type="review_widget",
        template="review_widget_template.html",
        output_name="{prefix}widget_reviews{suffix}.html",
        required_field="review_data",
        required_confidence=0.5,
        fallback="generate_placeholder_widget",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["missing_reviews"]
    ),
    "org_schema": AssetCatalogEntry(
        asset_type="org_schema",
        template="org_schema_template.json",
        output_name="{prefix}org_schema{suffix}.json",
        required_field="org_data",
        required_confidence=0.5,
        fallback="generate_basic_org",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["no_org_schema"]
    ),
    "barra_reserva_movil": AssetCatalogEntry(
        asset_type="barra_reserva_movil",
        template="barra_reserva_template.html",
        output_name="{prefix}barra_reserva{suffix}.html",
        required_field="booking_engine",
        required_confidence=0.6,
        fallback="generate_basic_bar",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["no_motor_reservas"]
    ),
    "financial_projection": AssetCatalogEntry(
        asset_type="financial_projection",
        template="projection_template.md",
        output_name="{prefix}proyeccion_financiera{suffix}.md",
        required_field="hotel_financial_data",
        required_confidence=0.5,
        fallback="use_benchmark_only",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=[]
    ),
    # MISSING ASSETS - Identified in FASE-ASSET-01
    "performance_audit": AssetCatalogEntry(
        asset_type="performance_audit",
        template="performance_audit_template.md",
        output_name="{prefix}auditoria_performance{suffix}.md",
        required_field="performance_data",
        required_confidence=0.5,
        fallback="generate_template_audit",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["poor_performance"]
    ),
    "optimization_guide": AssetCatalogEntry(
        asset_type="optimization_guide",
        template="optimization_guide_template.md",
        output_name="{prefix}guia_optimizacion{suffix}.md",
        required_field="metadata",
        required_confidence=0.5,
        fallback="generate_basic_guide",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["metadata_defaults", "pain_solution_mapper"]
    ),
    "direct_booking_campaign": AssetCatalogEntry(
        asset_type="direct_booking_campaign",
        template="campaign_template.md",
        output_name="{prefix}campana_reserva_directa{suffix}.md",
        required_field="ota_data",
        required_confidence=0.5,
        fallback="generate_awareness_campaign",
        block_on_failure=False,
        status=AssetStatus.MANUAL_ONLY,
        promised_by=["low_ota_divergence"]
    ),
    "llms_txt": AssetCatalogEntry(
        asset_type="llms_txt",
        template="llmstxt_template.txt",
        output_name="{prefix}llms{suffix}.txt",
        required_field="hotel_data",
        required_confidence=0.5,
        fallback="generate_basic_llmstxt",
        block_on_failure=False,
        status=AssetStatus.IMPLEMENTED,
        promised_by=["missing_llmstxt"]
    ),
}


def is_asset_implemented(asset_type: str) -> bool:
    """
    Check if an asset type is currently implemented for generation.
    
    Args:
        asset_type: The asset type to check
        
    Returns:
        True if the asset is implemented, False otherwise
    """
    if asset_type not in ASSET_CATALOG:
        return False
    return ASSET_CATALOG[asset_type].status == AssetStatus.IMPLEMENTED


def get_implemented_assets() -> List[str]:
    """
    Get list of all implemented asset types.
    
    Returns:
        List of asset type strings that are implemented
    """
    return [
        asset_type 
        for asset_type, entry in ASSET_CATALOG.items() 
        if entry.status == AssetStatus.IMPLEMENTED
    ]


def get_asset_requirements(asset_type: str) -> Dict[str, Any]:
    """
    Get requirements for an asset type.
    
    Args:
        asset_type: The asset type to get requirements for
        
    Returns:
        Dict with required_field, required_confidence, fallback, block_on_failure
        Returns None if asset_type not in catalog
    """
    if asset_type not in ASSET_CATALOG:
        return None
    
    entry = ASSET_CATALOG[asset_type]
    return {
        "required_field": entry.required_field,
        "required_confidence": entry.required_confidence,
        "fallback": entry.fallback,
        "block_on_failure": entry.block_on_failure
    }


def get_generation_strategy(asset_type: str) -> Dict[str, str]:
    """
    Get generation strategy (template and output_name) for an asset type.
    
    Args:
        asset_type: The asset type to get strategy for
        
    Returns:
        Dict with template and output_name
        Returns None if asset_type not in catalog or not implemented
    """
    if asset_type not in ASSET_CATALOG:
        return None
    
    entry = ASSET_CATALOG[asset_type]
    if entry.status != AssetStatus.IMPLEMENTED:
        return None
    
    return {
        "template": entry.template,
        "output_name": entry.output_name
    }


def get_missing_assets() -> List[str]:
    """
    Get list of all missing asset types.
    
    Returns:
        List of asset type strings that are missing
    """
    return [
        asset_type 
        for asset_type, entry in ASSET_CATALOG.items() 
        if entry.status == AssetStatus.MISSING
    ]


def get_promised_assets() -> List[str]:
    """
    Get list of all asset types promised by pain_solution_mapper.
    
    Returns:
        List of asset type strings that have pain mappings
    """
    return [
        asset_type 
        for asset_type, entry in ASSET_CATALOG.items() 
        if entry.promised_by
    ]


__all__ = [
    'AssetStatus',
    'AssetCatalogEntry',
    'ASSET_CATALOG',
    'is_asset_implemented',
    'get_implemented_assets',
    'get_asset_requirements',
    'get_generation_strategy',
    'get_missing_assets',
    'get_promised_assets',
]
