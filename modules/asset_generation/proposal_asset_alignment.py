"""Proposal-Asset Alignment Verification.

Verifies that every service promised in the commercial proposal has a
corresponding generated asset. This prevents the client from paying for
services they don't receive.

Created as part of FASE-ASSETS-VALIDACION.
"""

import json
from pathlib import Path
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
        elif isinstance(site_presence_report, dict) and 'results' in site_presence_report:
            # FIX: asdict() convierte SitePresenceReport a dict plano
            presence_lookup = site_presence_report['results']

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
            # FIX: Handle both object (.status attr) and dict ('status' key from asdict)
            if presence_result and hasattr(presence_result, 'status'):
                presence_status = presence_result.status
            elif presence_result and isinstance(presence_result, dict) and 'status' in presence_result:
                presence_status = presence_result['status']
            else:
                presence_status = None

            # Normalize: extract string value from enum or use directly
            if presence_status is not None:
                presence_status_value = presence_status.value if hasattr(presence_status, 'value') else str(presence_status)
            else:
                presence_status_value = None

            if presence_status is not None:

                # FASE-12B: Coherence check — detect divergence between audit and presence
                # When audit says hotel_schema_detected=false but presence says EXISTS,
                # this is a false positive (e.g., org schema misidentified as hotel schema).
                # Mark as divergent missing instead of present_in_production.
                if (expected_asset_type == "hotel_schema"
                        and presence_status_value == "exists"
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

                if presence_status_value == "exists":  # PresenceStatus.EXISTS
                    # Asset already exists in production — mark as present_in_production, not missing
                    report.present_in_production.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=True,
                        status="present_in_production",
                        message=f"Service '{service_name}' asset '{expected_asset_type}' already exists in production site",
                        presence_verified=True,
                        presence_status=presence_status_value
                    ))
                    continue
                elif presence_status_value == "redundant":
                    report.redundant.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=False,
                        status="redundant",
                        message=f"Service '{service_name}' asset '{expected_asset_type}' is redundant (already delivered)",
                        presence_verified=True,
                        presence_status=presence_status_value
                    ))
                    continue
                elif presence_status_value in ("not_exists", "verification_failed"):
                    # Asset not in production site either — truly missing
                    report.missing.append(ServiceAlignment(
                        service_name=service_name,
                        asset_type=expected_asset_type,
                        is_aligned=False,
                        status="missing",
                        message=f"Service '{service_name}' promises asset '{expected_asset_type}' but it was not generated and does not exist in production",
                        presence_verified=True,
                        presence_status=presence_status_value
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


# ==========================================================================
# FASE-0D: ProposalAssetMatrix — Matriz Propuesta → Brecha → Asset
# ==========================================================================


@dataclass
class ProposalAssetMatrixEntry:
    """Entry in the proposal-asset matrix linking service → breach → asset.

    Every service sold in a commercial proposal is cross-referenced against
    the pain ledger (breach) and generated assets to produce a traceable link.

    Statuses:
        LINKED — service has a real breach AND a generated asset
        MISSING_ASSET — service has a breach but no asset was generated
        NO_BREACH — service sold without a corresponding pain in the ledger
        GENERIC_DRAFT — fallback for services with partial match
    """
    service_name: str
    pain_ids: List[str] = field(default_factory=list)
    asset_type: str = ""
    asset_path: Optional[str] = None
    confidence: float = 0.0
    status: str = "GENERIC_DRAFT"  # LINKED | MISSING_ASSET | NO_BREACH | GENERIC_DRAFT


class ProposalAssetMatrix:
    """Builds the matrix that links every proposal service to its breach and asset.

    Rules:
        - Every sold service must map to a real breach (pain_id in ledger).
        - Every sold service must have a specific asset or be marked MISSING_ASSET.
        - An existing asset must resolve the associated pain_id.

    Divergencia semántica con AlignmentReport (P-04, DT-2):
        - ProposalAssetMatrix: traceability pain-driven — ¿el servicio de la
          propuesta responde a un pain real de analytics Y tenemos asset?
          Usa PAIN_SOLUTION_MAP + pain_ledger. Taxonomía: LINKED, MISSING_ASSET,
          NO_BREACH, GENERIC_DRAFT.
        - AlignmentReport: delivery verification — ¿el asset existe (generado
          O en producción)? Usa PROPOSAL_SERVICE_TO_ASSET + site presence.
          Taxonomía: aligned, missing, low_quality, present_in_production,
          redundant, indeterminate.
        - DEUDA TÉCNICA (v4.64.0): unificar ambos modelos en un solo contrato
          canónico que consuma DeliveryContext como fuente de verdad. La
          unificación NO es trivial (> 10 líneas) porque mezcla dimensiones
          ortogonales: analytics (pain) × delivery (asset existence).

    Usage:
        matrix = ProposalAssetMatrix()
        entries = matrix.build(proposal_services, pain_ledger, generated_assets)
        matrix.save(entries, Path("v4_audit/proposal_asset_matrix.json"))
    """

    def __init__(self):
        """Initialize with PainSolutionMapper for pain-to-asset mapping."""
        from ..commercial_documents.pain_solution_mapper import PainSolutionMapper
        self._pain_map = PainSolutionMapper.PAIN_SOLUTION_MAP

    def _get_pain_ids_for_asset_type(self, asset_type: str) -> List[str]:
        """Find all pain_ids that map to the given asset_type.

        Reverse-looks up the PAIN_SOLUTION_MAP: for each pain_id,
        checks if asset_type is in its assets list.

        Args:
            asset_type: e.g., 'whatsapp_button', 'hotel_schema'

        Returns:
            List of pain_id strings that map to this asset_type
        """
        matching: List[str] = []
        for pain_id, mapping in self._pain_map.items():
            if asset_type in mapping.get("assets", []):
                matching.append(pain_id)
        return matching

    def build(
        self,
        proposal_services: List[str],
        pain_ledger: List[Any],  # List[PainLedgerEntry]
        generated_assets: List[Any],  # List[GeneratedAsset] or List[dict]
    ) -> List[ProposalAssetMatrixEntry]:
        """Build the proposal-asset-brecha matrix.

        Args:
            proposal_services: Service names as they appear in the proposal
            pain_ledger: List of PainLedgerEntry from the pain ledger
            generated_assets: List of GeneratedAsset or dicts with
                'asset_type', 'confidence_score', 'path' keys

        Returns:
            List of ProposalAssetMatrixEntry, one per service
        """
        entries: List[ProposalAssetMatrixEntry] = []

        # Build fast lookups
        ledger_pain_ids: set = {
            e.get("pain_id") if isinstance(e, dict) else e.pain_id
            for e in pain_ledger
        }

        # Build asset_by_type lookup: handles both GeneratedAsset objects and dicts
        asset_by_type: Dict[str, Any] = {}
        for a in generated_assets:
            if isinstance(a, dict):
                asset_by_type[a.get("asset_type", "")] = a
            else:
                asset_by_type[getattr(a, "asset_type", "")] = a

        for service_name in proposal_services:
            expected_asset = PROPOSAL_SERVICE_TO_ASSET.get(service_name)
            if not expected_asset:
                # Unknown service — skip silently
                continue

            # Find all pain_ids that could map to this asset_type
            candidate_pain_ids = self._get_pain_ids_for_asset_type(expected_asset)
            # Filter to only those actually present in the ledger
            matched_pain_ids = [pid for pid in candidate_pain_ids if pid in ledger_pain_ids]

            # Find generated asset for this type
            gen_asset = asset_by_type.get(expected_asset)

            # Determine status based on breach + asset presence
            if matched_pain_ids and gen_asset is not None:
                status = "LINKED"
                confidence = (
                    gen_asset.get("confidence_score", 0.0) if isinstance(gen_asset, dict)
                    else getattr(gen_asset, "confidence_score", 0.0)
                )
                asset_path = (
                    gen_asset.get("path", None) if isinstance(gen_asset, dict)
                    else getattr(gen_asset, "path", None)
                )
            elif matched_pain_ids and gen_asset is None:
                status = "MISSING_ASSET"
                confidence = max(
                    (e.get("confidence", 0.0) if isinstance(e, dict) else getattr(e, "confidence", 0.0)
                     for e in pain_ledger if (e.get("pain_id") if isinstance(e, dict) else e.pain_id) in matched_pain_ids),
                    default=0.0,
                )
                asset_path = None
            elif not matched_pain_ids:
                status = "NO_BREACH"
                confidence = 0.0
                asset_path = None
            else:
                status = "GENERIC_DRAFT"
                confidence = 0.0
                asset_path = None

            entries.append(ProposalAssetMatrixEntry(
                service_name=service_name,
                pain_ids=matched_pain_ids,
                asset_type=expected_asset,
                asset_path=asset_path,
                confidence=confidence,
                status=status,
            ))

        return entries

    def save(self, entries: List[ProposalAssetMatrixEntry], path: Path) -> None:
        """Save the matrix to a JSON file.

        Args:
            entries: List of ProposalAssetMatrixEntry from build()
            path: Output path for proposal_asset_matrix.json
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "proposal_asset_matrix_version": "1.0",
            "entries": [
                {
                    "service_name": e.service_name,
                    "pain_ids": e.pain_ids,
                    "asset_type": e.asset_type,
                    "asset_path": e.asset_path,
                    "confidence": e.confidence,
                    "status": e.status,
                }
                for e in entries
            ],
        }
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)


# ==========================================================================
# FASE-DT-3 FASE-2: AssetAlignmentMatrix — Contrato Canónico Unificado
# ==========================================================================
# Unifica ProposalAssetMatrix (traceability pain-driven) y AlignmentReport
# (delivery verification) en un solo contrato que consume DeliveryContext
# como fuente de verdad post-DT-1.
#
# Taxonomía unificada (AlignmentStatus):
#   LINKED               — Pain real + asset existe → ✅
#   MISSING_ASSET         — Pain real + asset NO existe → ❌ (fallo real)
#   NO_BREACH             — Pain NO existe → ⏭️ (no aplica)
#   GENERIC_DRAFT         — Placeholder genérico → ❌
#   PRESENT_IN_PRODUCTION — Asset existe en sitio → ✅
#   LOW_QUALITY           — Asset generado pero baja calidad → ⚠️
#   INDETERMINATE         — No se pudo determinar → ⚠️

from enum import Enum as _Enum


class AlignmentStatus(_Enum):
    """Estado de alineación propuesta→asset unificado.

    Combina las dimensiones ortogonales:
    - analytics (pain-driven): ¿el servicio está justificado?
    - delivery (asset-existence): ¿el asset está listo?
    """
    LINKED = "linked"
    MISSING_ASSET = "missing_asset"
    NO_BREACH = "no_breach"
    GENERIC_DRAFT = "generic_draft"
    PRESENT_IN_PRODUCTION = "present_in_production"
    LOW_QUALITY = "low_quality"
    INDETERMINATE = "indeterminate"


@dataclass
class AssetAlignmentMatrix:
    """Contrato canónico unificado Proposal→Asset.

    Reemplaza a ProposalAssetMatrix y AlignmentReport con una sola fuente
    de verdad que responde ambas preguntas sin duplicar lógica:
    - \"¿el servicio responde a un pain real?\" (analytics)
    - \"¿el asset está listo para delivery?\" (delivery)

    Consume DeliveryContext como fuente de verdad post-DT-1.
    """

    entries: List[ProposalAssetMatrixEntry] = field(default_factory=list)
    _entry_map: Dict[str, ProposalAssetMatrixEntry] = field(default_factory=dict, repr=False)

    def __post_init__(self) -> None:
        """Rebuild entry map after initialization."""
        self._rebuild_map()

    def _rebuild_map(self) -> None:
        """Rebuild fast lookup from entries list."""
        self._entry_map = {e.service_name: e for e in self.entries if e.service_name}

    # ── Factory Methods ─────────────────────────────────────────────────

    @classmethod
    def build(
        cls,
        delivery_context: Any,
        pain_ledger: List[Any],
        generated_assets: Optional[List[Any]] = None,
    ) -> "AssetAlignmentMatrix":
        """Build the matrix from DeliveryContext and pain_ledger.

        Preferred constructor — consumes DeliveryContext as source of truth.

        Args:
            delivery_context: DeliveryContext instance (post-DT-1)
            pain_ledger: List of PainLedgerEntry from the pain ledger
            generated_assets: Optional override; if None, derived from
                             delivery_context.assets

        Returns:
            AssetAlignmentMatrix with one entry per promised service
        """
        from ..commercial_documents.pain_solution_mapper import PainSolutionMapper

        pain_map = PainSolutionMapper.PAIN_SOLUTION_MAP
        entries: List[ProposalAssetMatrixEntry] = []

        # Build fast lookups
        ledger_pain_ids: set = {
            e.get("pain_id") if isinstance(e, dict) else getattr(e, "pain_id", "")
            for e in pain_ledger
        }

        # Derive assets from delivery_context or use override
        if generated_assets is not None:
            asset_by_type: Dict[str, Any] = {}
            for a in generated_assets:
                if isinstance(a, dict):
                    asset_by_type[a.get("asset_type", "")] = a
                else:
                    asset_by_type[getattr(a, "asset_type", "")] = a
        else:
            asset_by_type = {
                a.asset_type: a for a in getattr(delivery_context, "assets", [])
            }

        for service_name in ALL_PROMISED_SERVICES:
            expected_asset = PROPOSAL_SERVICE_TO_ASSET.get(service_name)
            if not expected_asset:
                continue

            # Find all pain_ids that map to this asset_type
            candidate_pain_ids = [
                pid for pid, mapping in pain_map.items()
                if expected_asset in mapping.get("assets", [])
            ]
            matched_pain_ids = [pid for pid in candidate_pain_ids if pid in ledger_pain_ids]

            gen_asset = asset_by_type.get(expected_asset)

            if matched_pain_ids and gen_asset is not None:
                status = "LINKED"
                confidence = (
                    gen_asset.get("confidence_score", 0.0) if isinstance(gen_asset, dict)
                    else getattr(gen_asset, "confidence_score", 0.0)
                )
                asset_path = (
                    gen_asset.get("path", None) if isinstance(gen_asset, dict)
                    else getattr(gen_asset, "path", None)
                )
            elif matched_pain_ids and gen_asset is None:
                status = "MISSING_ASSET"
                confidence = max(
                    (e.get("confidence", 0.0) if isinstance(e, dict) else getattr(e, "confidence", 0.0)
                     for e in pain_ledger
                     if (e.get("pain_id") if isinstance(e, dict) else getattr(e, "pain_id", "")) in matched_pain_ids),
                    default=0.0,
                )
                asset_path = None
            elif not matched_pain_ids:
                status = "NO_BREACH"
                confidence = 0.0
                asset_path = None
            else:
                status = "GENERIC_DRAFT"
                confidence = 0.0
                asset_path = None

            entries.append(ProposalAssetMatrixEntry(
                service_name=service_name,
                pain_ids=matched_pain_ids,
                asset_type=expected_asset,
                asset_path=asset_path,
                confidence=confidence,
                status=status,
            ))

        return cls(entries=entries)

    # ── Lookup ──────────────────────────────────────────────────────────

    def get_alignment(self, service_name: str) -> AlignmentStatus:
        """Lookup alignment status for a single service.

        Args:
            service_name: Service name as it appears in the proposal

        Returns:
            AlignmentStatus enum value; INDETERMINATE if not found
        """
        entry = self._entry_map.get(service_name)
        if entry is None:
            return AlignmentStatus.INDETERMINATE
        try:
            return AlignmentStatus(entry.status.lower())
        except ValueError:
            return AlignmentStatus.INDETERMINATE

    def is_delivery_ready(self) -> bool:
        """Check if all actionable services have their assets ready.

        Actionable services = those with a real pain (excludes NO_BREACH).
        Delivery is ready when none of them are MISSING_ASSET or GENERIC_DRAFT.

        Returns:
            True if all actionable services are LINKED or PRESENT_IN_PRODUCTION
        """
        actionable = [e for e in self.entries if e.status != "NO_BREACH"]
        if not actionable:
            return True
        return all(
            e.status in ("LINKED", "PRESENT_IN_PRODUCTION")
            for e in actionable
        )

    # ── Serialization ──────────────────────────────────────────────────

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dict for proposal_asset_matrix.json.

        Format is backward-compatible with ProposalAssetMatrix.save() output.
        """
        return {
            "proposal_asset_matrix_version": "2.0",  # Unified contract
            "alignment_status_version": "1.0",
            "delivery_ready": self.is_delivery_ready(),
            "entries": [
                {
                    "service_name": e.service_name,
                    "pain_ids": e.pain_ids,
                    "asset_type": e.asset_type,
                    "asset_path": e.asset_path,
                    "confidence": e.confidence,
                    "status": e.status,
                    "alignment": self.get_alignment(e.service_name).value,
                }
                for e in self.entries
            ],
        }

    def save(self, path: Path) -> None:
        """Save the matrix to a JSON file.

        Args:
            path: Output path for proposal_asset_matrix.json
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        data = self.to_dict()
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False, sort_keys=True)

    # ── Backward compat helpers ────────────────────────────────────────

    @property
    def aligned_count(self) -> int:
        """Number of LINKED services (backward compat)."""
        return sum(1 for e in self.entries if e.status == "LINKED")

    @property
    def missing_count(self) -> int:
        """Number of MISSING_ASSET services (backward compat)."""
        return sum(1 for e in self.entries if e.status == "MISSING_ASSET")

    @property
    def total_services(self) -> int:
        """Total entries in the matrix."""
        return len(self.entries)


__all__ = [
    'PROPOSAL_SERVICE_TO_ASSET',
    'ALL_PROMISED_SERVICES',
    'ServiceAlignment',
    'AlignmentReport',
    'AlignmentStatus',
    'AssetAlignmentMatrix',
    'ProposalAssetMatrixEntry',
    'ProposalAssetMatrix',
    'verify_proposal_asset_alignment',
    'get_missing_services',
    'get_alignment_summary',
]
