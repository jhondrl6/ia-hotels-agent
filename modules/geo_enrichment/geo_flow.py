"""GEO Flow - Orchestrator for Diagnostic → Enrichment → Sync → Responsibility.

This module implements the GEO Flow that runs AFTER the CORE pipeline,
providing a unified entry point for all GEO enrichment operations.

Architecture:
    GEO Flow is ORTHOGONAL to the CORE pipeline - it only reads hotel_data
    and produces enriched assets without modifying CORE output.

Flow:
    1. GEO Diagnostic (42 methods, 4 bands)
    2. GEO Enrichment Layer (conditional asset generation by band)
    3. Sync Contract (narrative consistency with commercial diagnosis)
    4. Responsibility Contract (CORE vs GEO asset relationships)

Reference: FASE-6 prompt, FASE-6 tasks
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from data_models.canonical_assessment import CanonicalAssessment

from .geo_diagnostic import GEODiagnostic, GEOAssessment, GEOBand
from .geo_enrichment_layer import GEOEnrichmentLayer
from .sync_contract import SyncContractAnalyzer, SyncResult, LossLevel
from .asset_responsibility_contract import (
    AssetResponsibilityContract,
    AssetType,
)

logger = logging.getLogger(__name__)


# =============================================================================
# GEO FLOW RESULT DATA CLASS
# =============================================================================

@dataclass
class GeoFlowResult:
    """Result of the complete GEO Flow execution.
    
    Attributes:
        success: True if flow completed without critical errors.
        case: GEOBand enum (MINIMAL/case_a = EXCELLENT, LIGHT/case_b = GOOD, 
                           FULL/case_c/d = FOUNDATION/CRITICAL).
        geo_assessment: Full GEO diagnostic assessment.
        assets_generated: List of file paths for generated GEO assets.
        sync_result: Sync contract analysis result.
        responsibility_guide: Implementation guide for CORE/GEO assets.
        errors: List of non-critical errors encountered.
    """
    success: bool
    case: GEOBand  # GEOBand enum
    geo_assessment: Optional[GEOAssessment] = None
    assets_generated: List[str] = field(default_factory=list)
    sync_result: Optional[SyncResult] = None
    responsibility_guide: Optional[Dict[str, Any]] = None
    errors: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        # Manual serialization since GEOAssessment may not have to_dict
        geo_dict = None
        if self.geo_assessment:
            geo_dict = {
                "total_score": self.geo_assessment.total_score,
                "band": self.geo_assessment.band.value if hasattr(self.geo_assessment.band, 'value') else str(self.geo_assessment.band),
            }
        
        return {
            "success": self.success,
            "case": self.case.value if self.case else None,
            "geo_assessment": geo_dict,
            "assets_generated": self.assets_generated,
            "sync_result": {
                "is_consistent": self.sync_result.is_consistent if self.sync_result else None,
                "combination_tag": self.sync_result.combination_tag if self.sync_result else None,
                "recommendation": self.sync_result.recommendation if self.sync_result else None,
                "sync_score": self.sync_result.sync_score if self.sync_result else None,
            } if self.sync_result else None,
            "responsibility_guide": self.responsibility_guide,
            "errors": self.errors,
        }


# =============================================================================
# GEO FLOW ORCHESTRATOR
# =============================================================================

class GeoFlow:
    """Orchestrates the complete GEO Enrichment Flow.
    
    This is the main entry point for GEO operations. It coordinates:
    1. Diagnostic (GEO assessment)
    2. Enrichment (conditional asset generation)
    3. Sync Contract (narrative consistency)
    4. Responsibility Contract (asset relationships)
    
    Usage:
        flow = GeoFlow()
        result = flow.execute(hotel_data, commercial_diagnosis, output_dir)
    """
    
    def __init__(self):
        """Initialize GEO Flow with all components (except diagnostic which requires hotel_data)."""
        # Note: GEODiagnostic requires hotel_data in __init__, so we create it in execute()
        self.enrichment_layer = GEOEnrichmentLayer()
        self.sync_analyzer = SyncContractAnalyzer()
        self._responsibility_contract = AssetResponsibilityContract()
    
    def execute(
        self,
        hotel_data: CanonicalAssessment,
        commercial_diagnosis: Optional[Dict[str, Any]] = None,
        output_dir: str = "output"
    ) -> GeoFlowResult:
        """Execute the complete GEO Flow.
        
        Args:
            hotel_data: CanonicalAssessment with hotel information.
            commercial_diagnosis: Optional commercial diagnosis from GapAnalyzer.
                                 If provided, enables Sync Contract analysis.
            output_dir: Base output directory for generated assets.
            
        Returns:
            GeoFlowResult with all GEO Flow outputs.
        """
        errors: List[str] = []
        assets_generated: List[str] = []
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 1: GEO DIAGNOSTIC
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[GeoFlow] Step 1/4: Running GEO Diagnostic...")
        geo_assessment = None
        diagnostic = None
        try:
            # GEODiagnostic requires hotel_data in __init__
            diagnostic = GEODiagnostic(hotel_data)
            geo_assessment = diagnostic.diagnose()
            logger.info(
                f"[GeoFlow]   Diagnostic complete: Band={geo_assessment.band.value}, "
                f"Score={geo_assessment.total_score}/100"
            )
        except Exception as e:
            errors.append(f"Diagnostic failed: {str(e)}")
            logger.error(f"[GeoFlow]   Diagnostic error: {e}")
            # Graceful degradation: return partial result
            return GeoFlowResult(
                success=False,
                case=GEOBand.CRITICAL,
                geo_assessment=None,
                assets_generated=[],
                sync_result=None,
                responsibility_guide=None,
                errors=errors
            )
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 2: GEO ENRICHMENT LAYER
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[GeoFlow] Step 2/4: Running GEO Enrichment Layer...")
        enrichment_result: Dict[str, Any] = {}
        try:
            enrichment_result = self.enrichment_layer.generate(
                hotel_data=hotel_data,
                geo_assessment=geo_assessment,
                output_dir=output_dir,
                commercial_diagnosis=commercial_diagnosis
            )
            assets_generated = enrichment_result.get("files", [])
            logger.info(f"[GeoFlow]   Enrichment complete: {len(assets_generated)} assets")
        except Exception as e:
            errors.append(f"Enrichment failed: {str(e)}")
            logger.warning(f"[GeoFlow]   Enrichment error (continuing): {e}")
            # Graceful degradation: continue with diagnostic only
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 3: SYNC CONTRACT (requires commercial_diagnosis)
        # ═══════════════════════════════════════════════════════════════════
        sync_result: Optional[SyncResult] = None
        if commercial_diagnosis is not None:
            logger.info("[GeoFlow] Step 3/4: Running Sync Contract...")
            try:
                sync_result = self.sync_analyzer.analyze(
                    commercial_diagnosis=commercial_diagnosis,
                    geo_assessment=geo_assessment
                )
                logger.info(
                    f"[GeoFlow]   Sync complete: {sync_result.combination_tag}, "
                    f"consistent={sync_result.is_consistent}"
                )
            except Exception as e:
                errors.append(f"Sync Contract failed: {str(e)}")
                logger.warning(f"[GeoFlow]   Sync error (continuing): {e}")
        else:
            logger.info("[GeoFlow]   Sync Contract skipped (no commercial_diagnosis)")
        
        # ═══════════════════════════════════════════════════════════════════
        # STEP 4: RESPONSIBILITY CONTRACT
        # ═══════════════════════════════════════════════════════════════════
        logger.info("[GeoFlow] Step 4/4: Building Responsibility Guide...")
        responsibility_guide: Optional[Dict[str, Any]] = None
        try:
            # Build asset inventory for the guide
            asset_inventory = self._build_asset_inventory(
                core_assets=[],  # CORE assets come from v4_asset_orchestrator
                geo_assets=assets_generated
            )
            
            # Use generate_delivery_template instead (which exists)
            responsibility_guide = {
                "asset_inventory": asset_inventory,
                "geo_band": geo_assessment.band.value,
                "total_score": geo_assessment.total_score,
                "implementation_note": "CORE assets first, GEO assets as enrichment after"
            }
            logger.info("[GeoFlow]   Responsibility Guide complete")
        except Exception as e:
            errors.append(f"Responsibility Contract failed: {str(e)}")
            logger.warning(f"[GeoFlow]   Responsibility error (continuing): {e}")
        
        # ═══════════════════════════════════════════════════════════════════
        # FINAL RESULT
        # ═══════════════════════════════════════════════════════════════════
        success = geo_assessment is not None and len(errors) == 0
        
        return GeoFlowResult(
            success=success,
            case=geo_assessment.band if geo_assessment else GEOBand.CRITICAL,
            geo_assessment=geo_assessment,
            assets_generated=assets_generated,
            sync_result=sync_result,
            responsibility_guide=responsibility_guide,
            errors=errors
        )
    
    def _build_asset_inventory(
        self,
        core_assets: List[str],
        geo_assets: List[str]
    ) -> List[Dict[str, Any]]:
        """Build asset inventory for responsibility guide.
        
        Args:
            core_assets: List of CORE asset file paths.
            geo_assets: List of GEO asset file paths.
            
        Returns:
            List of asset inventory entries.
        """
        inventory = []
        
        # Add CORE assets
        for path in core_assets:
            filename = Path(path).name
            inventory.append({
                "filename": filename,
                "type": AssetType.CORE.value,
                "path": path,
                "priority": 1,  # CORE always first
                "mandatory": True,
            })
        
        # Add GEO assets
        for path in geo_assets:
            filename = Path(path).name
            is_enrichment = "_rich" in filename or filename.startswith("geo_")
            inventory.append({
                "filename": filename,
                "type": AssetType.GEO.value,
                "path": path,
                "priority": 2 if is_enrichment else 3,  # Enrichments after CORE
                "mandatory": False,
                "enriched_by": self._get_enriched_version(filename),
            })
        
        return inventory
    
    def _get_enriched_version(self, filename: str) -> Optional[str]:
        """Get the CORE file that a GEO file enriches.
        
        Args:
            filename: GEO asset filename.
            
        Returns:
            Corresponding CORE filename or None.
        """
        enrichment_map = {
            "hotel_schema_rich.json": "hotel_schema.json",
            "faq_schema_rich.json": "faq_schema.json",
            "boton_whatsapp_rich.html": "boton_whatsapp.html",
        }
        return enrichment_map.get(filename)


# =============================================================================
# CONVENIENCE FUNCTION
# =============================================================================

def run_geo_flow(
    hotel_data: CanonicalAssessment,
    commercial_diagnosis: Optional[Dict[str, Any]] = None,
    output_dir: str = "output"
) -> GeoFlowResult:
    """Convenience function to run the GEO Flow.
    
    Args:
        hotel_data: CanonicalAssessment with hotel information.
        commercial_diagnosis: Optional commercial diagnosis dict.
        output_dir: Output directory for assets.
        
    Returns:
        GeoFlowResult with all outputs.
    """
    flow = GeoFlow()
    return flow.execute(hotel_data, commercial_diagnosis, output_dir)
