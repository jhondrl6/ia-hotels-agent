"""
Delivery Quality Report - Pre-publication blocking quality gate.

FASE-0E: Implements DeliveryQualityReport and DeliveryQualityReportGenerator.
Evaluates G6/G7/G8/G9 gates from the v4_audit output to determine if a delivery
is ready for ZIP/packaging or must be blocked.

Rules:
- FAIL blocks ZIP/publication.
- WARNING visible but not blocking.
- PASS requires G6/G7/G8/G9 satisfied (coherence >= 0.8, coverage PASS, asset specificity PASS, proposal-asset alignment PASS).
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

from modules.quality_gates.publication_gates import PublicationGateConfig

logger = logging.getLogger(__name__)


@dataclass
class DeliveryQualityReport:
    """
    Pre-ZIP delivery quality assessment.

    Attributes:
        status: PASS | FAIL | WARNING
        blocking: True if ZIP/publication must be aborted
        coverage_gate: Results from coverage gate evaluation
        proposal_asset_gate: Results from proposal-asset alignment gate
        asset_specificity_gate: Results from asset specificity/confidence gate
        evidence_gate: Results from evidence quality gate
        advisory_warnings: List of non-blocking warnings (e.g., IA-Readiness Critical)
        human_review_items: Items requiring manual review before publication
        summary: Aggregate summary of all gate results
    """
    status: str  # PASS | FAIL | WARNING
    blocking: bool
    coverage_gate: dict
    proposal_asset_gate: dict
    asset_specificity_gate: dict
    evidence_gate: dict
    summary: dict
    advisory_warnings: List[dict] = field(default_factory=list)
    human_review_items: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "blocking": self.blocking,
            "coverage_failure_rate": self.coverage_gate,
            "proposal_asset_gate": self.proposal_asset_gate,
            "asset_specificity_gate": self.asset_specificity_gate,
            "evidence_gate": self.evidence_gate,
            "advisory_warnings": self.advisory_warnings,
            "human_review_items": self.human_review_items,
            "summary": self.summary,
        }


class DeliveryQualityReportGenerator:
    """
    Generates a DeliveryQualityReport by evaluating G6/G7/G8/G9 gates
    from the v4_audit directory output.

    The generator reads coherence_validation.json (with post-gen fallback),
    asset_generation_report.json, and proposal_asset_matrix.json
    from the v4_audit directory and evaluates:

    - G6 (Coherence): coherence >= config.coherence_threshold (default 0.8)
    - G7 (Coverage): coverage ratio from coverage gate
    - G8 (Asset Specificity): asset confidence >= 0.7, proposal-asset alignment
    - G9 (Proposal-Asset Alignment): all promised services have aligned assets
    - Evidence gate: overall evidence quality assessment

    Usage:
        generator = DeliveryQualityReportGenerator()
        report = generator.generate("hotel_id", Path("output/v4_complete/hotel_id/v4_audit"))
        generator.save(report, Path("output/v4_complete/hotel_id/v4_audit/delivery_quality_report.json"))

        if report.status == "FAIL":
            raise SystemExit("Delivery blocked by quality gate failures.")
    """

    # Default thresholds
    COHERENCE_THRESHOLD = 0.8
    ASSET_CONFIDENCE_THRESHOLD = 0.7
    ASSET_SPECIFICITY_MIN_ASSETS = 1  # At least one usable asset

    def __init__(self, config: Optional[PublicationGateConfig] = None):
        """
        Initialize the generator with optional custom gate configuration.

        Args:
            config: PublicationGateConfig with custom thresholds.
                    Uses defaults if None.
        """
        self.config = config or PublicationGateConfig()
        self.coherence_threshold = getattr(
            self.config, 'coherence_threshold', self.COHERENCE_THRESHOLD
        )

    def generate(self, hotel_id: str, v4_audit_path: Path) -> DeliveryQualityReport:
        """
        Generate delivery quality report from v4_audit data.

        Args:
            hotel_id: Hotel identifier for logging
            v4_audit_path: Path to the v4_audit directory containing
                          coherence_validation.json and asset_generation_report.json

        Returns:
            DeliveryQualityReport with status, blocking flag, and gate details
        """
        human_review_items: List[str] = []
        gate_results: Dict[str, dict] = {}

        # ── G6: Coherence Gate ─────────────────────────────────────────────
        # P-03: Prefer post-gen coherence score when available, fallback to pre-gen.
        # Report both scores for transparency when both exist.
        post_gen_path = v4_audit_path / "coherence_validation_post_gen.json"
        pre_gen_path = v4_audit_path / "coherence_validation.json"

        coherence_post_data = None
        coherence_post_score = None
        if post_gen_path.exists():
            coherence_post_data = self._load_json(post_gen_path)
            coherence_post_score = self._extract_coherence(coherence_post_data)

        coherence_pre_data = self._load_json(pre_gen_path)
        coherence_pre_score = self._extract_coherence(coherence_pre_data)

        # Use post-gen score as the primary score; fallback to pre-gen
        coherence_score = coherence_post_score if coherence_post_score is not None else coherence_pre_score
        coherence_passed = (
            coherence_score is not None
            and coherence_score >= self.coherence_threshold
        )

        gate_results["coherence"] = {
            "passed": coherence_passed,
            "score": coherence_score,
            "threshold": self.coherence_threshold,
            "gate": "G6",
        }
        # Report both scores for transparency when both exist
        if coherence_pre_score is not None and coherence_post_score is not None:
            gate_results["coherence"]["score_pre"] = coherence_pre_score
            gate_results["coherence"]["score_post"] = coherence_post_score

        if not coherence_passed:
            if coherence_score is None:
                human_review_items.append(
                    "G6: Coherence score not found — coherence_validation.json missing or invalid"
                )
            else:
                human_review_items.append(
                    f"G6: Coherence score {coherence_score:.2f} below threshold "
                    f"{self.coherence_threshold}"
                )

        # ── G7: Coverage Gate ──────────────────────────────────────────────
        coverage_data = self._load_json(v4_audit_path / "asset_generation_report.json")
        coverage_passed, coverage_details = self._evaluate_coverage(coverage_data)
        gate_results["coverage"] = {
            "passed": coverage_passed,
            "details": coverage_details,
            "gate": "G7",
        }
        if not coverage_passed:
            human_review_items.append(
                f"G7: Coverage check failed — {coverage_details.get('reason', 'unknown')}"
            )

        # ── G8: Asset Specificity Gate ─────────────────────────────────────
        asset_data = coverage_data  # Same file, already loaded
        specificity_passed, specificity_details = self._evaluate_asset_specificity(asset_data)
        gate_results["asset_specificity"] = {
            "passed": specificity_passed,
            "details": specificity_details,
            "gate": "G8",
        }
        if not specificity_passed:
            human_review_items.append(
                f"G8: Asset specificity failed — {specificity_details.get('reason', 'unknown')}"
            )

        # ── G9: Proposal-Asset Alignment Gate ───────────────────────────────
        # FASE-DT-3 FASE-2: Consume AssetAlignmentMatrix.is_delivery_ready()
        # como contrato canónico unificado en vez de parsing manual de JSON.
        matrix_path = v4_audit_path / "proposal_asset_matrix.json"
        if matrix_path.exists():
            from modules.asset_generation.proposal_asset_alignment import (
                AssetAlignmentMatrix,
                ProposalAssetMatrixEntry,
            )
            matrix_data = self._load_json(matrix_path)
            raw_entries = matrix_data.get("entries", [])
            # Reconstruir AssetAlignmentMatrix desde los datos del JSON
            entries = [
                ProposalAssetMatrixEntry(
                    service_name=e.get("service_name", ""),
                    pain_ids=e.get("pain_ids", []),
                    asset_type=e.get("asset_type", ""),
                    asset_path=e.get("asset_path"),
                    confidence=e.get("confidence", 0.0),
                    status=e.get("status", "GENERIC_DRAFT"),
                )
                for e in raw_entries
            ]
            matrix = AssetAlignmentMatrix(entries=entries)
            total_services = matrix.total_services
            delivery_ready = matrix.is_delivery_ready()
            aligned_count = matrix.aligned_count
            gate_results["proposal_asset_alignment"] = {
                "passed": delivery_ready,
                "gate": "G9",
                "aligned": aligned_count,
                "total": total_services,
            }
        else:
            # No matrix available — gate skipped (not evaluated)
            gate_results["proposal_asset_alignment"] = {
                "passed": True,
                "gate": "G9",
                "skipped": True,
                "reason": "proposal_asset_matrix.json not found",
            }

        # ── Evidence Gate ──────────────────────────────────────────────────
        evidence_passed, evidence_details = self._evaluate_evidence(
            coherence_pre_data, asset_data
        )
        gate_results["evidence"] = {
            "passed": evidence_passed,
            "details": evidence_details,
            "gate": "EVIDENCE",
        }
        if not evidence_passed:
            human_review_items.append(
                f"Evidence: Quality check failed — {evidence_details.get('reason', 'unknown')}"
            )

        # ── Advisory Warnings ───────────────────────────────────────────────
        # FASE-A: Non-blocking warnings (e.g., IA-Readiness Critical)
        advisory_warnings: List[dict] = []
        ia_readiness_data = self._load_json(v4_audit_path / "ia_readiness_report.json")
        if ia_readiness_data:
            ia_score = self._extract_ia_readiness_score(ia_readiness_data)
            ia_status = ia_readiness_data.get("status", "")
            if ia_status.lower() == "critical" or (ia_score is not None and ia_score < 50):
                advisory_warnings.append({
                    "code": "IA_READINESS_CRITICAL",
                    "severity": "WARNING",
                    "blocking": False,
                    "message": "IA-Readiness Critical: objetivo de citación/recomendación por IA en riesgo sin acción correctiva"
                })

        # ── Determine overall status ───────────────────────────────────────
        BLOCKING_GATE_NAMES = ("coherence", "coverage", "evidence", "proposal_asset_alignment")
        blocking_gates = [
            name for name, result in gate_results.items()
            if not result["passed"] and name in BLOCKING_GATE_NAMES
        ]
        warning_gates = [
            name for name, result in gate_results.items()
            if not result["passed"] and name not in BLOCKING_GATE_NAMES
        ]

        if blocking_gates:
            status = "FAIL"
            blocking = True
        elif warning_gates:
            status = "WARNING"
            blocking = False
        else:
            status = "PASS"
            blocking = False

        # ── Build summary ──────────────────────────────────────────────────
        total_gates = len(gate_results)
        passed_count = sum(1 for r in gate_results.values() if r["passed"])
        summary = {
            "total_gates": total_gates,
            "passed": passed_count,
            "failed": total_gates - passed_count,
            "coherence_score": coherence_score,
            "blocking_gates": blocking_gates,
            "warning_gates": warning_gates,
        }

        return DeliveryQualityReport(
            status=status,
            blocking=blocking,
            coverage_gate=gate_results["coverage"],
            proposal_asset_gate=gate_results.get("proposal_asset_alignment", {"passed": True, "gate": "G9"}),
            asset_specificity_gate=gate_results["asset_specificity"],
            evidence_gate=gate_results["evidence"],
            advisory_warnings=advisory_warnings,
            human_review_items=human_review_items,
            summary=summary,
        )

    def save(self, report: DeliveryQualityReport, path: Path) -> None:
        """
        Save the report as JSON to the specified path.

        Args:
            report: DeliveryQualityReport to save
            path: Destination file path
        """
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(report.to_dict(), indent=2, ensure_ascii=False))

    # ── Private helpers ────────────────────────────────────────────────────

    @staticmethod
    def _load_json(path: Path) -> dict:
        """Load JSON from file, return empty dict if missing or invalid."""
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"Could not load {path}: {e}")
            return {}

    @staticmethod
    def _extract_coherence(data: dict) -> Optional[float]:
        """Extract coherence score from coherence validation data."""
        if not data:
            return None
        # Try direct overall_score
        if "overall_score" in data:
            return float(data["overall_score"])
        # Try nested
        if "coherence" in data and isinstance(data["coherence"], dict):
            return data["coherence"].get("overall_score")
        return None

    @staticmethod
    def _extract_ia_readiness_score(data: dict) -> Optional[float]:
        """Extract IA readiness score from ia_readiness_report.json."""
        if not data:
            return None
        if "overall_score" in data:
            return float(data["overall_score"])
        if "components" in data and isinstance(data["components"], dict):
            # Weighted average already computed as overall_score
            return data["components"].get("overall_score")
        return None

    def _evaluate_coverage(self, data: dict) -> tuple:
        """
        Evaluate coverage gate (G7).
        Checks that generated assets cover the detected pains adequately.
        """
        if not data:
            return False, {"reason": "No asset generation data available"}

        summary = data.get("summary", {})
        total = summary.get("total_assets", 0)
        generated = summary.get("generated", 0)
        failed = summary.get("failed", 0)

        # Coverage PASS if we have generated assets and failure rate is low
        if total == 0:
            return False, {"reason": "No assets generated — coverage is 0%"}

        if generated == 0:
            return False, {"reason": f"All {total} assets failed — coverage is 0%"}

        failure_rate = failed / total if total > 0 else 1.0
        coverage_passed = failure_rate < 0.5  # Less than 50% failure rate

        return coverage_passed, {
            "total_assets": total,
            "generated": generated,
            "failed": failed,
            "failure_rate": round(failure_rate, 2),
            "reason": "" if coverage_passed else f"Failure rate {failure_rate:.0%} >= 50%",
        }

    def _evaluate_asset_specificity(self, data: dict) -> tuple:
        """
        Evaluate asset specificity gate (G8).
        Checks that generated assets have sufficient confidence scores.
        """
        if not data:
            return False, {"reason": "No asset generation data available"}

        generated_assets = data.get("generated_assets", [])
        if not generated_assets:
            return False, {"reason": "No generated assets to evaluate"}

        # Check confidence scores
        low_confidence = [
            a for a in generated_assets
            if a.get("confidence_score", 0) < self.ASSET_CONFIDENCE_THRESHOLD
        ]
        unusable = [
            a for a in generated_assets
            if not a.get("can_use", True)
        ]

        avg_confidence = (
            sum(a.get("confidence_score", 0) for a in generated_assets)
            / len(generated_assets)
        )

        # Block if ALL assets are below threshold (100% estimated)
        if len(low_confidence) == len(generated_assets):
            return False, {
                "reason": "100% of assets are below confidence threshold",
                "avg_confidence": round(avg_confidence, 2),
                "low_confidence_count": len(low_confidence),
                "total_assets": len(generated_assets),
            }

        # Warning if some assets are below threshold
        if low_confidence:
            return False, {
                "reason": f"{len(low_confidence)} assets below confidence threshold",
                "avg_confidence": round(avg_confidence, 2),
                "low_confidence_count": len(low_confidence),
                "total_assets": len(generated_assets),
            }

        # Also check for unusable assets
        if unusable:
            return False, {
                "reason": f"{len(unusable)} assets marked as unusable",
                "avg_confidence": round(avg_confidence, 2),
                "unusable_count": len(unusable),
                "total_assets": len(generated_assets),
            }

        return True, {
            "avg_confidence": round(avg_confidence, 2),
            "total_assets": len(generated_assets),
            "all_above_threshold": True,
        }

    def _evaluate_evidence(self, coherence_data: dict, asset_data: dict) -> tuple:
        """
        Evaluate evidence quality gate.
        Checks that evidence coverage meets minimum standards.
        """
        # Check if we have any data at all
        has_coherence = bool(coherence_data)
        has_assets = bool(asset_data)

        if not has_coherence and not has_assets:
            return False, {"reason": "No evidence data available — both coherence and asset data missing"}

        if not has_coherence:
            return False, {"reason": "Coherence validation data missing — cannot verify evidence quality"}

        # Evidence passes if coherence data exists and is readable
        coherence_score = self._extract_coherence(coherence_data)
        if coherence_score is None:
            return False, {"reason": "Coherence score not extractable from data"}

        return True, {
            "coherence_available": True,
            "asset_data_available": has_assets,
            "coherence_score": coherence_score,
        }
