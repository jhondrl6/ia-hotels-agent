"""Proposal-Asset Alignment Verification.

Verifies that every service promised in the commercial proposal has a
corresponding generated asset. This prevents the client from paying for
services they don't receive.

Created as part of FASE-ASSETS-VALIDACION.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional


# ==========================================================================
# MAPPING: Proposal Service → Asset Type (Source of Truth)
# ==========================================================================
# Each key is a service name as it appears in the commercial proposal.
# Each value is the asset_type that should be generated for that service.

PROPOSAL_SERVICE_TO_ASSET: Dict[str, str] = {
    "Google Maps Optimizado": "geo_playbook",
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Datos Estructurados": "hotel_schema",
    "Informe Mensual": "monthly_report",
    "Página de FAQ": "faq_page",
    "Meta Tags Sociales (Open Graph)": "open_graph",
}

# All 7 services that the proposal always promises (as of v4.34.0: +FAQ, +Open Graph)
ALL_PROMISED_SERVICES: List[str] = list(PROPOSAL_SERVICE_TO_ASSET.keys())


@dataclass
class ServiceAlignment:
    """Alignment status of a single service."""
    service_name: str
    asset_type: str
    is_aligned: bool
    status: str  # "aligned", "missing", "low_quality", "present_in_production", "redundant"
    confidence_score: Optional[float] = None
    message: str = ""
    presence_verified: bool = False  # FASE-D: whether presence was checked via SitePresenceChecker
    presence_status: Optional[str] = None  # FASE-D: PresenceStatus value if verified


@dataclass
class AlignmentReport:
    """Complete alignment report for proposal → assets."""

    aligned: List[ServiceAlignment] = field(default_factory=list)
    missing: List[ServiceAlignment] = field(default_factory=list)
    low_quality: List[ServiceAlignment] = field(default_factory=list)
    # FASE-D: New categories for site presence verification
    present_in_production: List[ServiceAlignment] = field(default_factory=list)
    redundant: List[ServiceAlignment] = field(default_factory=list)

    @property
    def total_services(self) -> int:
        """Total number of services checked (excludes present_in_production for alignment calc)."""
        return len(self.aligned) + len(self.missing) + len(self.low_quality)

    @property
    def all_aligned(self) -> bool:
        """True if all services have aligned assets (no missing after presence check)."""
        return len(self.missing) == 0

    @property
    def alignment_percentage(self) -> float:
        """Percentage of services with aligned assets (excludes present_in_production)."""
        if self.total_services == 0:
            return 0.0
        return len(self.aligned) / self.total_services

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        # FASE-D: Build presence verified dict for each aligned/missing entry
        def _service_dict(s: ServiceAlignment) -> Dict[str, Any]:
            d = {"service": s.service_name, "asset": s.asset_type, "message": s.message}
            # Backward compatible: only add presence fields if verified
            if s.presence_verified:
                d["presence_verified"] = True
                d["presence_status"] = s.presence_status
            return d
        
        def _aligned_dict(s: ServiceAlignment) -> Dict[str, Any]:
            d = {"service": s.service_name, "asset": s.asset_type, "confidence": s.confidence_score}
            if s.presence_verified:
                d["presence_verified"] = True
                d["presence_status"] = s.presence_status
            return d
        
        return {
            "total_services": self.total_services,
            "aligned_count": len(self.aligned),
            "missing_count": len(self.missing),
            "low_quality_count": len(self.low_quality),
            # FASE-D: backward compatible - new fields only added if present
            "alignment_percentage": self.alignment_percentage,
            "all_aligned": self.all_aligned,
            "aligned": [_aligned_dict(s) for s in self.aligned],
            "missing": [_service_dict(s) for s in self.missing],
            "low_quality": [
                {"service": s.service_name, "asset": s.asset_type, "confidence": s.confidence_score, "message": s.message}
                for s in self.low_quality
            ],
            # FASE-D: new categories (only included if non-empty for backward compat)
            "present_in_production": [
                {
                    "service": s.service_name, 
                    "asset": s.asset_type, 
                    "presence_verified": s.presence_verified,
                    "presence_status": s.presence_status
                }
                for s in self.present_in_production
            ] if self.present_in_production else [],
            "redundant": [
                {
                    "service": s.service_name, 
                    "asset": s.asset_type, 
                    "presence_verified": s.presence_verified,
                    "presence_status": s.presence_status
                }
                for s in self.redundant
            ] if self.redundant else [],
        }


def verify_proposal_asset_alignment(
    proposal_services: List[str],
    generated_assets: List[Dict[str, Any]],
    asset_catalog: Optional[Dict[str, Any]] = None,
    confidence_threshold: float = 0.7,
    site_presence_report: Optional[Any] = None,  # FASE-D: SitePresenceReport from SitePresenceChecker
    hotel_url: Optional[str] = None  # FASE-D: Required if site_presence_report provided
) -> AlignmentReport:
    """Verify that each promised service has a corresponding generated asset.

    FASE-D: Before marking as "missing", verifies via SitePresenceChecker if the asset
    already exists in the production site. If EXISTS, marks as "present_in_production".

    Args:
        proposal_services: List of service names marked with checkmark in proposal.
                           If empty, uses ALL_PROMISED_SERVICES.
        generated_assets: List of asset dicts from report (each has 'asset_type').
        asset_catalog: Optional asset catalog for additional metadata.
        confidence_threshold: Minimum confidence for "aligned" vs "low_quality".
        site_presence_report: Optional SitePresenceReport from SitePresenceChecker.check_site()
        hotel_url: URL of the hotel site (required if site_presence_report provided)

    Returns:
        AlignmentReport with aligned, missing, present_in_production, redundant, and low_quality lists.
    """
    report = AlignmentReport()

    # Default to all promised services if none specified
    services_to_check = proposal_services if proposal_services else ALL_PROMISED_SERVICES

    # Build lookup of generated assets by type
    asset_lookup: Dict[str, Dict[str, Any]] = {}
    for asset in generated_assets:
        asset_type = asset.get("asset_type", "")
        if asset_type:
            asset_lookup[asset_type] = asset
    
    # FASE-D: Build presence lookup from site_presence_report
    presence_lookup: Dict[str, Any] = {}
    if site_presence_report and hasattr(site_presence_report, 'results'):
        for asset_type, result in site_presence_report.results.items():
            presence_lookup[asset_type] = result

    for service_name in services_to_check:
        expected_asset_type = PROPOSAL_SERVICE_TO_ASSET.get(service_name)

        if not expected_asset_type:
            # Unknown service — skip
            continue

        if expected_asset_type not in asset_lookup:
            # FASE-D: Asset not generated — check if it exists in production site
            presence_result = presence_lookup.get(expected_asset_type)
            if presence_result and hasattr(presence_result, 'status'):
                presence_status = presence_result.status
                if presence_status.value == "exists":  # PresenceStatus.EXISTS
                    # Asset already exists in production — mark as present_in_production, not missing
                    report.present_in_production.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=True,
                        status="present_in_production",
                        message=f"Service '{service_name}' asset '{expected_asset_type}' already exists in production site",
                        presence_verified=True,
                        presence_status=presence_status.value
                    ))
                    continue
                elif presence_status.value == "redundant":
                    report.redundant.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=False,
                        status="redundant",
                        message=f"Service '{service_name}' asset '{expected_asset_type}' is redundant (already delivered)",
                        presence_verified=True,
                        presence_status=presence_status.value
                    ))
                    continue
                elif presence_status.value in ("not_exists", "verification_failed"):
                    # Asset not in production site either — truly missing
                    report.missing.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=False,
                        status="missing",
                        message=f"Service '{service_name}' promises asset '{expected_asset_type}' but it was not generated and does not exist in production",
                        presence_verified=True,
                        presence_status=presence_status.value
                    ))
                    continue
            
            # No presence info or asset truly missing
            report.missing.append(ServiceAlignment(
                service_name=service_name,
                asset_type=expected_asset_type,
                is_aligned=False,
                status="missing",
                message=f"Service '{service_name}' promises asset '{expected_asset_type}' but it was not generated"
            ))
            continue

        # Asset exists — check quality
        asset = asset_lookup[expected_asset_type]
        confidence = asset.get("confidence_score", 0.0)

        if confidence < confidence_threshold:
            report.low_quality.append(ServiceAlignment(
                service_name=service_name,
                asset_type=expected_asset_type,
                is_aligned=False,
                status="low_quality",
                confidence_score=confidence,
                message=f"Asset '{expected_asset_type}' has low confidence ({confidence:.2f} < {confidence_threshold})"
            ))
        else:
            report.aligned.append(ServiceAlignment(
                service_name=service_name,
                asset_type=expected_asset_type,
                is_aligned=True,
                status="aligned",
                confidence_score=confidence,
                message=f"Service '{service_name}' properly aligned with asset '{expected_asset_type}'"
            ))

    return report


def get_missing_services(report: AlignmentReport) -> List[str]:
    """Get list of service names that are missing assets.

    Args:
        report: AlignmentReport from verify_proposal_asset_alignment

    Returns:
        List of service names without corresponding assets.
    """
    return [s.service_name for s in report.missing]


def get_alignment_summary(report: AlignmentReport) -> str:
    """Generate human-readable alignment summary.

    Args:
        report: AlignmentReport from verify_proposal_asset_alignment

    Returns:
        Formatted string with alignment status.
    """
    lines = [
        "=== Proposal-Asset Alignment Report ===",
        f"Total services: {report.total_services}",
        f"Aligned: {len(report.aligned)} ({report.alignment_percentage:.0%})",
        f"Missing: {len(report.missing)}",
        f"Low quality: {len(report.low_quality)}",
        "",
    ]

    if report.aligned:
        lines.append("ALIGNED:")
        for s in report.aligned:
            conf = f" (confidence: {s.confidence_score:.2f})" if s.confidence_score else ""
            lines.append(f"  ✅ {s.service_name} → {s.asset_type}{conf}")

    if report.low_quality:
        lines.append("")
        lines.append("LOW QUALITY:")
        for s in report.low_quality:
            lines.append(f"  ⚠️ {s.service_name} → {s.asset_type} (confidence: {s.confidence_score:.2f})")

    if report.missing:
        lines.append("")
        lines.append("MISSING:")
        for s in report.missing:
            lines.append(f"  ❌ {s.service_name} → {s.asset_type}")

    lines.append("")
    lines.append(f"Status: {'READY' if report.all_aligned else 'NOT READY'}")

    return "\n".join(lines)


__all__ = [
    'PROPOSAL_SERVICE_TO_ASSET',
    'ALL_PROMISED_SERVICES',
    'ServiceAlignment',
    'AlignmentReport',
    'verify_proposal_asset_alignment',
    'get_missing_services',
    'get_alignment_summary',
]
