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

FASE-SR-A (N1): "truly unresolved" is computed in exactly one place —
AlignmentResult.compute_unresolved() — consumed by both reports. The
NO_BREACH bucket ("sin brecha — no comprometido, fuera del coverage") is
neither covered nor unresolved and is disclosed separately via ``no_breach``
so the message stays coherent with ``coverage_ratio`` (fixes gate_report
unresolved=4 vs delivery=1 in the same run).

FASE-SR-B (D-PF1): ``coverage_ratio`` se calcula sobre el conjunto
``actionable`` — NO_BREACH queda fuera del denominador (L-NC10/L-SR3/AC1).
Ambos constructores delegan en UN solo cálculo canónico
(``_from_entries``) alimentado por las mismas entradas de matriz, así el
gate_report y delivery_quality_report producen resultados idénticos. Con
``no_breach == 0`` (ruta legacy sin pain_ledger) el denominador es el total
de servicios prometidos — comportamiento idéntico al pre-SR-B.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

# FASE-SR-A (N1): statuses that count as "sin cubrir" (unresolved). Single rule
# shared by gate_report (from_alignment_report) and delivery_quality_report
# (from_asset_alignment_matrix) via AlignmentResult.compute_unresolved().
# NO_BREACH ("no comprometido, fuera del coverage") and presence-resolved
# entries are NOT unresolved — same semantics as
# AssetAlignmentMatrix.is_delivery_ready().
UNRESOLVED_STATUSES = ("MISSING_ASSET", "GENERIC_DRAFT")


@dataclass
class _DerivedEntry:
    """Legacy-path entry derived from AlignmentReport categories.

    Light stand-in for ProposalAssetMatrixEntry: exposes the attributes
    that _from_entries() and compute_unresolved() read via getattr()
    (``status``, ``asset_type``, ``service_name``) so the no-pain_ledger
    legacy path of ``from_alignment_report`` reuses the SAME canonical
    computation.
    """

    status: str
    asset_type: str
    service_name: str = ""


def _presence_resolved(
    site_presence_report: Optional[Dict[str, Any]], asset_type: str
) -> bool:
    """True when the normalized SitePresence snapshot reports the asset exists."""
    if not site_presence_report:
        return False
    presence = site_presence_report.get(asset_type, {})
    return isinstance(presence, dict) and presence.get("status") == "exists"


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
        no_breach: Services declared "no comprometido, fuera del coverage"
            (NO_BREACH) — neither covered nor unresolved; disclosed so the
            message stays coherent with coverage_ratio (FASE-SR-A)
    """

    promised_services_total: int
    generated_aligned: int
    present_in_production: int
    unresolved: int
    coverage_ratio: float
    present_assets: List[str] = field(default_factory=list)
    # FASE-SR-A (N1): NO_BREACH services are neither covered nor unresolved;
    # effective_total + unresolved + no_breach == promised_services_total.
    no_breach: int = 0

    @property
    def passed(self) -> bool:
        """Gate passes when all promised services are covered."""
        return self.unresolved == 0

    @property
    def effective_total(self) -> int:
        """Services effectively covered (generated + pre-existing)."""
        return self.generated_aligned + self.present_in_production

    @property
    def actionable_total(self) -> int:
        """FASE-SR-B (D-PF1): servicios comprometidos (denominador del coverage).

        Accionables = prometidos - NO_BREACH (mismo concepto que
        ``AssetAlignmentMatrix.is_delivery_ready()``): los servicios "sin costo
        (fallback)" no comprometidos no cuentan como deuda de entrega.
        """
        return max(self.promised_services_total - self.no_breach, 0)

    @property
    def message(self) -> str:
        """Human-readable alignment message consistent across all consumers.

        FASE-SR-B (D-PF1): el denominador del mensaje es ``actionable_total``
        (coherente con ``coverage_ratio``); los NO_BREACH se revelan como
        "no comprometidos, fuera del coverage".
        """
        if self.actionable_total == 0:
            base = (
                f"0 servicios comprometidos — nada prometido sin pain ni "
                f"presencia ({self.no_breach} sin brecha, fuera del coverage)"
                if self.no_breach > 0
                else "0 servicios comprometidos — nada prometido"
            )
            return base
        parts = [
            f"{self.effective_total}/{self.actionable_total} "
            f"servicios comprometidos cubiertos"
        ]
        parts.append(f"({self.generated_aligned} generados")
        if self.present_in_production > 0:
            parts.append(f" + {self.present_in_production} ya en producción")
        parts.append(")")
        if self.unresolved > 0:
            parts.append(f" — {self.unresolved} sin cubrir")
        if self.no_breach > 0:
            parts.append(
                f" — {self.no_breach} sin brecha (no comprometidos, "
                f"fuera del coverage)"
            )
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
            "no_breach": self.no_breach,
            "passed": self.passed,
            "effective_total": self.effective_total,
            "actionable_total": self.actionable_total,
            "message": self.message,
        }

    @classmethod
    def compute_unresolved(
        cls,
        entries: Iterable[Any],
        site_presence_report: Optional[Dict[str, Any]] = None,
    ) -> int:
        """FASE-SR-A (N1): the single computation of "sin cubrir" (unresolved).

        Both reports — gate_report (from_alignment_report) and
        delivery_quality_report (from_asset_alignment_matrix) — MUST count
        unresolved through this helper. No parallel sums allowed (L-NC10).

        Rule (matrix + SitePresence semantics, matches
        AssetAlignmentMatrix.is_delivery_ready()):
        - Only actionable failures count: MISSING_ASSET / GENERIC_DRAFT.
        - NO_BREACH ("no comprometido, fuera del coverage") is a non-committed
          service, not an uncovered one.
        - An entry whose asset already exists on the live site (SitePresence
          cross-reference) is covered, not unresolved.

        Args:
            entries: iterable of matrix-like entries exposing ``.status`` and
                ``.asset_type`` (ProposalAssetMatrixEntry) — or plain
                ``(status, asset_type)`` tuples.
            site_presence_report: normalized SitePresence snapshot
                (from site_presence_adapter.normalize_site_presence()).

        Returns:
            Number of truly unresolved (sin cubrir) services.
        """
        unresolved = 0
        for entry in entries:
            status, asset_type = cls._entry_status_and_asset(entry)
            if status not in UNRESOLVED_STATUSES:
                continue
            if _presence_resolved(site_presence_report, asset_type):
                continue
            unresolved += 1
        return unresolved

    @staticmethod
    def _entry_status_and_asset(entry: Any) -> Tuple[str, str]:
        """Accept matrix-like entries or (status, asset_type) tuples."""
        if isinstance(entry, tuple) and len(entry) == 2:
            return entry[0], entry[1]
        return getattr(entry, "status", ""), getattr(entry, "asset_type", "")

    @classmethod
    def _from_entries(
        cls,
        entries: Iterable[Any],
        site_presence_report: Optional[Dict[str, Any]] = None,
    ) -> "AlignmentResult":
        """FASE-SR-B (D-PF1): cálculo canónico desde entradas de matriz.

        ÚNICO punto donde se computan generated/present/no_breach/unresolved/
        coverage. Tanto ``from_alignment_report`` (con semantic_entries) como
        ``from_asset_alignment_matrix`` delegan aquí, alimentados por las
        mismas entradas → los dos reportes del MISMO run son idénticos (AC3)
        y el coverage usa el denominador actionable (AC1).
        """
        entry_list = list(entries)
        total = len(entry_list)

        generated = sum(1 for e in entry_list if getattr(e, "status", "") == "LINKED")

        # Cross-reference with SitePresence for entries whose static JSON status
        # predates runtime enrichment (NO_BREACH, MISSING_ASSET → may actually
        # be PRESENT_IN_PRODUCTION on the live site).
        present = 0
        present_assets: List[str] = []
        for e in entry_list:
            status = getattr(e, "status", "")
            asset_type = getattr(e, "asset_type", "")
            if status == "PRESENT_IN_PRODUCTION":
                present += 1
                present_assets.append(getattr(e, "service_name", ""))
            elif status in ("NO_BREACH", "MISSING_ASSET") and _presence_resolved(
                site_presence_report, asset_type
            ):
                present += 1
                present_assets.append(getattr(e, "service_name", ""))

        # FASE-SR-A (N1): unified counting — single helper shared by both reports
        unresolved_count = cls.compute_unresolved(entry_list, site_presence_report)
        no_breach_count = sum(
            1 for e in entry_list
            if getattr(e, "status", "") == "NO_BREACH"
            and not _presence_resolved(site_presence_report, getattr(e, "asset_type", ""))
        )

        # FASE-SR-B (D-PF1): coverage sobre el conjunto actionable — NO_BREACH
        # fuera del denominador (AC1). Accionables cubiertos = 0 → ratio 1.0
        # (nada comprometido sin pain ni presencia → nada puede estar faltante).
        actionable = max(total - no_breach_count, 0)
        coverage = (generated + present) / actionable if actionable > 0 else 1.0

        return cls(
            promised_services_total=total,
            generated_aligned=generated,
            present_in_production=present,
            unresolved=unresolved_count,
            coverage_ratio=coverage,
            present_assets=present_assets,
            no_breach=no_breach_count,
        )

    @classmethod
    def from_alignment_report(
        cls,
        report: Any,
        semantic_entries: Optional[List[Any]] = None,
        site_presence_report: Optional[Dict[str, Any]] = None,
    ) -> "AlignmentResult":
        """Build AlignmentResult from an AlignmentReport (used by publication gates).

        Args:
            report: AlignmentReport instance from verify_proposal_asset_alignment()
            semantic_entries: FASE-SR-A (N1) — optional pain-driven matrix entries
                (AssetAlignmentMatrix.build() output) carrying the NO_BREACH
                taxonomy the delivery-verification report cannot know. When
                provided, the WHOLE result is computed from these entries via
                _from_entries() — the exact same computation as
                delivery_quality_report (same basis, same taxonomy, same
                coverage denominator); otherwise it is derived from the report
                categories alone (legacy delivery-verification semantics).
            site_presence_report: normalized SitePresence snapshot, used with
                semantic_entries for the presence cross-reference.
        """
        if semantic_entries is not None:
            # FASE-SR-B (D-PF1): fuente única — mismas entradas que la matriz
            # canónica que consume delivery_quality_report.
            return cls._from_entries(semantic_entries, site_presence_report)

        # Legacy fallback: derive semantic states from the report categories
        # and count through the SAME helper (no parallel sums). low_quality
        # assets are generated (delivered) — they map to LINKED here, exactly
        # as they were never counted as missing before FASE-SR-A.
        derived: List[Any] = [
            _DerivedEntry("LINKED", s.asset_type, s.service_name) for s in report.aligned
        ]
        derived += [
            _DerivedEntry("LINKED", s.asset_type, s.service_name)
            for s in report.low_quality
        ]
        derived += [
            _DerivedEntry("MISSING_ASSET", s.asset_type, s.service_name)
            for s in report.missing
        ]
        derived += [
            _DerivedEntry("PRESENT_IN_PRODUCTION", s.asset_type, s.service_name)
            for s in report.present_in_production
        ]
        # no_breach = 0 (NO_BREACH is pain-driven — not knowable here) →
        # actionable == total → legacy coverage semantics preserved.
        return cls._from_entries(derived, None)

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
        return cls._from_entries(matrix.entries, site_presence_report)
