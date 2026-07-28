"""
Canonical Alignment Result DTO — DT4-N5-ALIGNMENT (FASE-4).

Single source of truth for proposal-asset alignment reporting, shared between
publication_gates.py (_proposal_asset_alignment_gate) and
delivery_quality_report.py (DeliveryQualityReportGenerator).

Before FASE-4, the two consumers used different data sources and reported
different totals:
- Gate report said "7/7 aligned" but details.total_services=5
- Delivery report said "aligned: 5, total: 7"

AlignmentResult makes the breakdown explicit: how many were generated, how
many already exist in production, and how many are truly unresolved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class AlignmentResult:
    """Canonical alignment result shared between publication and delivery reporting.

    Attributes:
        promised_services_total: Total services promised in the proposal (e.g., 7)
        generated_aligned: Services with successfully generated assets (e.g., 5)
        present_in_production: Services whose assets already exist on the client site (e.g., 2)
        unresolved: Services with no asset generated and not present in production (e.g., 0)
        coverage_ratio: Proportion covered (generated + present) / promised (e.g., 1.0)
        present_assets: Human-readable names of assets already in production
    """

    promised_services_total: int
    generated_aligned: int
    present_in_production: int
    unresolved: int
    coverage_ratio: float
    present_assets: List[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        """Gate passes when all promised services are covered."""
        return self.unresolved == 0

    @property
    def effective_total(self) -> int:
        """Services effectively covered (generated + pre-existing)."""
        return self.generated_aligned + self.present_in_production

    @property
    def message(self) -> str:
        """Human-readable alignment message consistent across all consumers."""
        parts = [f"{self.effective_total}/{self.promised_services_total} servicios cubiertos"]
        parts.append(f"({self.generated_aligned} generados")
        if self.present_in_production > 0:
            parts.append(f" + {self.present_in_production} ya en producción")
        parts.append(")")
        if self.unresolved > 0:
            parts.append(f" — {self.unresolved} sin cubrir")
        return " ".join(parts)

    def to_dict(self) -> Dict[str, Any]:
        """Serialize to a dict for JSON reports."""
        return {
            "promised_services_total": self.promised_services_total,
            "generated_aligned": self.generated_aligned,
            "present_in_production": self.present_in_production,
            "unresolved": self.unresolved,
            "coverage_ratio": self.coverage_ratio,
            "present_assets": self.present_assets,
            "passed": self.passed,
            "effective_total": self.effective_total,
            "message": self.message,
        }

    @classmethod
    def from_alignment_report(cls, report: Any) -> "AlignmentResult":
        """Build AlignmentResult from an AlignmentReport (used by publication gates).

        Args:
            report: AlignmentReport instance from verify_proposal_asset_alignment()
        """
        generated = len(report.aligned)
        present = len(report.present_in_production)
        unresolved_count = len(report.missing)
        # total services includes present_in_production as they are part of the promise
        total = report.total_services + present

        return cls(
            promised_services_total=total,
            generated_aligned=generated,
            present_in_production=present,
            unresolved=unresolved_count,
            coverage_ratio=(generated + present) / total if total > 0 else 0.0,
            present_assets=[s.service_name for s in report.present_in_production],
        )

    @classmethod
    def from_asset_alignment_matrix(
        cls, matrix: Any, site_presence_report: Optional[Dict[str, Any]] = None
    ) -> "AlignmentResult":
        """Build AlignmentResult from an AssetAlignmentMatrix (used by delivery report).

        Args:
            matrix: AssetAlignmentMatrix instance
            site_presence_report: Optional normalized SitePresence snapshot
                (from site_presence_adapter.normalize_site_presence()).
                When provided, entries with NO_BREACH or MISSING_ASSET status
                are cross-referenced against live site presence — if the asset
                exists on the real site, it is counted as present_in_production
                instead of unresolved.
        """
        entries = matrix.entries
        total = len(entries)

        generated = sum(1 for e in entries if e.status == "LINKED")

        # Cross-reference with SitePresence for entries whose static JSON status
        # predates runtime enrichment (NO_BREACH, MISSING_ASSET → may actually
        # be PRESENT_IN_PRODUCTION on the live site).
        present = 0
        present_assets: List[str] = []
        for e in entries:
            if e.status == "PRESENT_IN_PRODUCTION":
                present += 1
                present_assets.append(e.service_name)
            elif site_presence_report and e.status in ("NO_BREACH", "MISSING_ASSET"):
                presence = site_presence_report.get(e.asset_type, {})
                if isinstance(presence, dict) and presence.get("status") == "exists":
                    present += 1
                    present_assets.append(e.service_name)

        unresolved_count = sum(
            1 for e in entries if e.status in ("MISSING_ASSET", "GENERIC_DRAFT")
        )
        # Subtract entries resolved by SitePresence cross-reference
        if site_presence_report:
            unresolved_count = sum(
                1 for e in entries
                if e.status in ("MISSING_ASSET", "GENERIC_DRAFT")
                and not (
                    isinstance(site_presence_report.get(e.asset_type, {}), dict)
                    and site_presence_report[e.asset_type].get("status") == "exists"
                )
            )

        return cls(
            promised_services_total=total,
            generated_aligned=generated,
            present_in_production=present,
            unresolved=unresolved_count,
            coverage_ratio=(generated + present) / total if total > 0 else 0.0,
            present_assets=present_assets,
        )
