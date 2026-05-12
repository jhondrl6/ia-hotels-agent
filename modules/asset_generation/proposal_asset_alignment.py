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
    "SEO Local": "optimization_guide",
    "Botón de WhatsApp": "whatsapp_button",
    "Schema Hotel": "hotel_schema",
    "Schema Organization": "org_schema",
    "Informe Mensual": "monthly_report",
    "Página de FAQ": "faq_page",
    "Meta Tags Sociales (Open Graph)": "open_graph",
    "Optimización para IA Generativa": "llms_txt",
}

# All 8 services that the proposal promises (as of FASE-12C):
# - 7 base services (SEO, WhatsApp, Schema Hotel, Schema Organization, Monthly Report, FAQ, Open Graph)
# - 1 conditional AEO service (Optimización para IA Generativa → llms_txt)
# NOTE: Google Maps Optimizado was removed in FASE-PROP-D because geo_playbook
# was redundant with geo_fix_kit.md and other GEO assets.
# NOTE: "Datos Estructurados" was split into "Schema Hotel" + "Schema Organization" in FASE-12C
# for commercial transparency.
# SOURCE OF TRUTH: This dict is consumed by proposal_asset_alignment_gate (Gate 9)
# and cross-referenced by coherence_validator._check_promised_assets_exist().
# See FASE-SOL2-B for unification rationale.
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
    # FIX-5: Indeterminate — SitePresenceChecker failed, can't verify
    indeterminate: List[ServiceAlignment] = field(default_factory=list)

    @property
    def total_services(self) -> int:
        """Total number of services checked (excludes present_in_production and indeterminate for alignment calc)."""
        return len(self.aligned) + len(self.missing) + len(self.low_quality)

    @property
    def all_covered(self) -> bool:
        """True si todos los servicios estan cubiertos (generado o en produccion)."""
        return len(self.missing) == 0

    @property
    def all_aligned(self) -> bool:
        """DEPRECATED: Use all_covered instead."""
        return self.all_covered

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
            "all_covered": self.all_covered,
            "all_aligned": self.all_covered,  # DEPRECATED: backward compat
            "aligned": [_aligned_dict(s) for s in self.aligned],
            "missing": [_service_dict(s) for s in self.missing],
            "low_quality": [
                {"service": s.service_name, "asset": s.asset_type, "confidence": s.confidence_score, "message": s.message}
                for s in self.low_quality
            ],
            # FIX-5: indeterminate category (only included if non-empty for backward compat)
            "indeterminate": [
                {
                    "service": s.service_name, 
                    "asset": s.asset_type, 
                    "message": s.message
                }
                for s in self.indeterminate
            ] if self.indeterminate else [],
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
    hotel_url: Optional[str] = None,  # FASE-D: Required if site_presence_report provided
    audit_schema: Optional[Dict[str, Any]] = None  # FASE-12B: Audit schema data for coherence check
) -> AlignmentReport:
    """Verify that each promised service has a corresponding generated asset.

    FASE-D: Before marking as "missing", verifies via SitePresenceChecker if the asset
    already exists in the production site. If EXISTS, marks as "present_in_production".

    FASE-12B: Cross-references audit schema data with presence results to detect
    divergences (e.g., SitePresenceChecker reports EXISTS but audit says
    hotel_schema_detected=false). These are marked as "missing" with
    presence_status="divergent".

    Args:
        proposal_services: List of service names marked with checkmark in proposal.
                           If empty, uses ALL_PROMISED_SERVICES.
        generated_assets: List of asset dicts from report (each has 'asset_type').
        asset_catalog: Optional asset catalog for additional metadata.
        confidence_threshold: Minimum confidence for "aligned" vs "low_quality".
        site_presence_report: Optional SitePresenceReport from SitePresenceChecker.check_site()
        hotel_url: URL of the hotel site (required if site_presence_report provided)
        audit_schema: Optional dict with schema audit data (e.g., {"hotel_schema_detected": bool}).
                      Used for FASE-12B coherence/divergence detection.

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
    # FIX-5: Detect when SitePresenceChecker failed and returned unknown status
    presence_unknown = False
    if site_presence_report is not None:
        if isinstance(site_presence_report, dict) and site_presence_report.get('presence_status') == 'unknown':
            presence_unknown = True
        elif hasattr(site_presence_report, 'results'):
            for asset_type, result in site_presence_report.results.items():
                presence_lookup[asset_type] = result

    for service_name in services_to_check:
        expected_asset_type = PROPOSAL_SERVICE_TO_ASSET.get(service_name)

        if not expected_asset_type:
            # Unknown service — skip
            continue

        if expected_asset_type not in asset_lookup:
            # FIX-5: If SitePresenceChecker failed, mark as indeterminate instead of missing
            if presence_unknown:
                report.indeterminate.append(ServiceAlignment(
                    service_name=service_name,
                    asset_type=expected_asset_type,
                    is_aligned=False,
                    status="indeterminate",
                    message=f"Service '{service_name}' asset '{expected_asset_type}' could not be verified — SitePresenceChecker failed",
                    presence_verified=False,
                ))
                continue

            # FASE-D: Asset not generated — check if it exists in production site
            presence_result = presence_lookup.get(expected_asset_type)
            if presence_result and hasattr(presence_result, 'status'):
                presence_status = presence_result.status

                # FASE-12B: Coherence check — detect divergence between audit and presence
                # When audit says hotel_schema_detected=false but presence says EXISTS,
                # this is a false positive (e.g., org schema misidentified as hotel schema).
                # Mark as divergent missing instead of present_in_production.
                if (expected_asset_type == "hotel_schema"
                        and presence_status.value == "exists"
                        and audit_schema is not None
                        and not audit_schema.get("hotel_schema_detected", True)):
                    report.missing.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=False,
                        status="missing",
                        message=(
                            f"DIVERGENCIA: SitePresenceChecker reporta EXISTS para "
                            f"'{expected_asset_type}' pero audit dice hotel_schema_detected=false. "
                            f"Posible falso positivo por detección de Organization schema."
                        ),
                        presence_verified=True,
                        presence_status="divergent"
                    ))
                    continue

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
    ]
    # FIX-5: Show indeterminate count when SitePresenceChecker failed
    if report.indeterminate:
        lines.append(f"Indeterminate (unverified): {len(report.indeterminate)}")
    lines.append("")

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

    # FIX-5: Show indeterminate services
    if report.indeterminate:
        lines.append("")
        lines.append("INDETERMINATE (unverified — SitePresenceChecker failed):")
        for s in report.indeterminate:
            lines.append(f"  ❓ {s.service_name} → {s.asset_type}")

    lines.append("")
    lines.append(f"Status: {'READY' if report.all_covered else 'NOT READY'}")

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
