"""GEO Enrichment Module - Diagnostic and enrichment for AI discovery.

This module provides GEO (Generative Engine Optimization) diagnostic capabilities
for hotel websites, evaluating 42 methods across 8 areas to produce actionable
enrichment recommendations.

The module is ORTHOGONAL to the existing pipeline - it only reads hotel_data
and produces diagnostic output without modifying the input.
"""

from .geo_diagnostic import (
    GEOBand,
    ScoreBreakdown,
    GEOAssessment,
    GEODiagnostic,
)

from .sync_contract import (
    SyncContractAnalyzer,
    SyncResult,
    analyze_sync,
    GEOBand as SyncGEOBand,
    LossLevel,
)

from .asset_responsibility_contract import (
    AssetType,
    AssetResponsibility,
    AssetResponsibilityContract,
    get_implementation_order,
    get_replacement_rule,
    generate_delivery_template,
)

# FASE-6: GEO Flow Orchestrator
from .geo_flow import (
    GeoFlow,
    GeoFlowResult,
    run_geo_flow,
)

__all__ = [
    # FASE-2: GEO Diagnostic
    "GEOBand",
    "ScoreBreakdown",
    "GEOAssessment",
    "GEODiagnostic",
    # FASE-4: Sync Contract
    "SyncContractAnalyzer",
    "SyncResult",
    "analyze_sync",
    "LossLevel",
    # FASE-5: Asset Responsibility Contract
    "AssetType",
    "AssetResponsibility",
    "AssetResponsibilityContract",
    "get_implementation_order",
    "get_replacement_rule",
    "generate_delivery_template",
    # FASE-6: GEO Flow Orchestrator
    "GeoFlow",
    "GeoFlowResult",
    "run_geo_flow",
]

__version__ = "1.0.0"
