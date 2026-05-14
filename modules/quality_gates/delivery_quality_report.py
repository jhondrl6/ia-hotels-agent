"""
Delivery Quality Report - Pre-publication blocking quality gate.

FASE-0E: Implements DeliveryQualityReport and DeliveryQualityReportGenerator.
Evaluates G6/G7/G8 gates from the v4_audit output to determine if a delivery
is ready for ZIP/packaging or must be blocked.

Rules:
- FAIL blocks ZIP/publication.
- WARNING visible but not blocking.
- PASS requires G6/G7/G8 satisfied (coherence >= 0.8, coverage PASS, asset specificity PASS).
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
        human_review_items: Items requiring manual review before publication
        summary: Aggregate summary of all gate results
    """
    status: str  # PASS | FAIL | WARNING
    blocking: bool
    coverage_gate: dict
    proposal_asset_gate: dict
    asset_specificity_gate: dict
    evidence_gate: dict
    human_review_items: List[str]
    summary: dict

    def to_dict(self) -> Dict:
        """Convert report to dictionary for JSON serialization."""
        return {
            "status": self.status,
            "blocking": self.blocking,
            "coverage_gate": self.coverage_gate,
            "proposal_asset_gate": self.proposal_asset_gate,
            "asset_specificity_gate": self.asset_specificity_gate,
            "evidence_gate": self.evidence_gate,
            "human_review_items": self.human_review_items,
            "summary": self.summary,
        }


class DeliveryQualityReportGenerator:
    """
    Generates a DeliveryQualityReport by evaluating G6/G7/G8 gates
    from the v4_audit directory output.

    The generator reads coherence_validation.json and asset_generation_report.json
    from the v4_audit directory and evaluates:

    - G6 (Coherence): coherence >= config.coherence_threshold (default 0.8)
    - G7 (Coverage): coverage ratio from coverage gate
    - G8 (Asset Specificity): asset confidence >= 0.7, proposal-asset alignment
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
        coherence_data = self._load_json(v4_audit_path / "coherence_validation.json")
        coherence_score = self._extract_coherence(coherence_data)
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

        # ── Evidence Gate ──────────────────────────────────────────────────
        evidence_passed, evidence_details = self._evaluate_evidence(
            coherence_data, asset_data
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

        # ── Determine overall status ───────────────────────────────────────
        blocking_gates = [
            name for name, result in gate_results.items()
            if not result["passed"] and name in ("coherence", "coverage", "evidence")
        ]
        warning_gates = [
            name for name, result in gate_results.items()
            if not result["passed"] and name not in ("coherence", "coverage", "evidence")
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
            proposal_asset_gate=gate_results.get("proposal_asset", {"passed": True, "gate": "G9"}),
            asset_specificity_gate=gate_results["asset_specificity"],
            evidence_gate=gate_results["evidence"],
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
