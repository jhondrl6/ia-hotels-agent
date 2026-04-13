"""
Publication Gates - Pre-publication Quality Gates for Phase 5.

This module implements the 5 critical gates that must pass before
any commercial document or asset can be published to a client.

Gates:
1. hard_contradictions_gate: Blocks if HARD conflicts exist
2. evidence_coverage_gate: Blocks if coverage < 95%
3. financial_validity_gate: Blocks if default values detected
4. coherence_gate: Blocks if coherence < 0.8
5. critical_recall_gate: Blocks if critical recall < 90%

Usage:
    from modules.quality_gates.publication_gates import (
        run_publication_gates,
        check_publication_readiness,
        PublicationGatesOrchestrator
    )
    
    results = run_publication_gates(assessment, config)
    if all(r.passed for r in results):
        print("Ready for publication!")
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
from datetime import datetime

from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult
)
from modules.quality_gates.ethics_gate import EthicsGate, EthicsStatus
from modules.postprocessors.document_quality_gate import DocumentQualityGate


# =============================================================================
# NOTA: Citability e IA-Readiness son métricas ADVISORY.
# NO se incluyen como gates bloqueantes.
# Se reportan en diagnóstico para orientar mejoras pero NO bloquean publicación.
# =============================================================================

class GateStatus(str, Enum):
    """Status of a publication gate."""
    PASSED = "PASSED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"


@dataclass
class PublicationGateResult:
    """
    Result of a single publication gate check.
    
    Attributes:
        gate_name: Name of the gate that was checked
        passed: Whether the gate passed
        status: PASSED/FAILED/BLOCKED status
        message: Human-readable description of the result
        value: The actual value that was checked (e.g., 0.85 for coherence)
        suggestion: Suggested action if gate failed
        details: Optional additional details about the check
    """
    gate_name: str
    passed: bool
    status: GateStatus
    message: str
    value: Any = None
    suggestion: str = ""
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary for serialization."""
        return {
            "gate_name": self.gate_name,
            "passed": self.passed,
            "status": self.status.value,
            "message": self.message,
            "value": self.value,
            "suggestion": self.suggestion,
            "details": self.details
        }


@dataclass
class PublicationGateConfig:
    """
    Configuration for publication gates thresholds.
    
    All thresholds are configurable but have sensible defaults
    based on the KPI definitions in .opencode/plans/07-kpis-metricas.md
    """
    evidence_coverage_threshold: float = 0.95  # >= 95%
    coherence_threshold: float = 0.8  # >= 0.8
    critical_recall_threshold: float = 0.90  # >= 90%
    hard_contradictions_max: int = 0  # Must be 0
    financial_validity_required: bool = True  # Must be True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "evidence_coverage_threshold": self.evidence_coverage_threshold,
            "coherence_threshold": self.coherence_threshold,
            "critical_recall_threshold": self.critical_recall_threshold,
            "hard_contradictions_max": self.hard_contradictions_max,
            "financial_validity_required": self.financial_validity_required
        }


class PublicationGatesOrchestrator:
    """
    Orchestrates the execution of all publication gates.
    
    This class manages the execution of the 5 critical gates
    and provides a unified interface for checking publication readiness.
    
    Example:
        orchestrator = PublicationGatesOrchestrator(config)
        results = orchestrator.run_all(assessment)
        
        if orchestrator.is_ready_for_publication(results):
            print("All gates passed!")
    """
    
    def __init__(self, config: Optional[PublicationGateConfig] = None):
        """
        Initialize the orchestrator with configuration.
        
        Args:
            config: Gate thresholds configuration. Uses defaults if None.
        """
        self.config = config or PublicationGateConfig()
        self.gates: Dict[str, Callable] = {
            "hard_contradictions": self._hard_contradictions_gate,
            "evidence_coverage": self._evidence_coverage_gate,
            "financial_validity": self._financial_validity_gate,
            "coherence": self._coherence_gate,
            "critical_recall": self._critical_recall_gate,
            "ethics": self._ethics_gate,
            "content_quality": self._content_quality_gate,
            "asset_confidence": self._asset_confidence_gate,
            "proposal_asset_alignment": self._proposal_asset_alignment_gate,
        }
        self.ethics_gate = EthicsGate()
        self.content_quality_gate = DocumentQualityGate()
    
    def run_all(self, assessment: Dict[str, Any]) -> List[PublicationGateResult]:
        """
        Execute all publication gates on the assessment.
        
        Args:
            assessment: Dictionary containing all assessment data including
                       validation results, coherence scores, financial data, etc.
        
        Returns:
            List of PublicationGateResult, one for each gate
        """
        results = []
        for gate_name, gate_func in self.gates.items():
            try:
                result = gate_func(assessment)
                results.append(result)
            except Exception as e:
                # If a gate fails to execute, mark it as BLOCKED
                results.append(PublicationGateResult(
                    gate_name=gate_name,
                    passed=False,
                    status=GateStatus.BLOCKED,
                    message=f"Gate execution failed: {str(e)}",
                    value=None,
                    suggestion="Review assessment data structure and retry"
                ))
        return results
    
    def is_ready_for_publication(self, results: List[PublicationGateResult]) -> bool:
        """
        Check if all gates passed and publication is allowed.
        
        Args:
            results: List of gate results from run_all()
        
        Returns:
            True if all gates passed, False otherwise
        """
        return all(r.passed for r in results)
    
    def get_blocking_gates(self, results: List[PublicationGateResult]) -> List[PublicationGateResult]:
        """
        Get list of gates that failed or blocked publication.
        
        Args:
            results: List of gate results from run_all()
        
        Returns:
            List of failed/blocked gate results
        """
        return [r for r in results if not r.passed]
    
    def _hard_contradictions_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 1: Hard Contradictions Check
        
        Blocks if there are any HARD conflicts that haven't been resolved.
        Hard conflicts indicate fundamental disagreements between data sources
        that would make publication unsafe.
        
        Threshold: hard_contradictions count must be 0
        
        Args:
            assessment: Assessment dictionary with validation/conflict data
        
        Returns:
            PublicationGateResult with status
        """
        gate_name = "hard_contradictions"
        
        # Extract hard contradictions from assessment
        conflicts = self._extract_conflicts(assessment)
        hard_count = sum(1 for c in conflicts if c.get("severity") == "HARD" or 
                        c.get("type") == "HARD")
        
        # Alternative: check in validation_summary
        if hard_count == 0:
            validation_summary = assessment.get("validation_summary", {})
            if isinstance(validation_summary, dict):
                hard_count = validation_summary.get("hard_contradictions_count", 0)
        
        passed = hard_count <= self.config.hard_contradictions_max
        
        if passed:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"No hard contradictions detected (count: {hard_count})",
                value=hard_count,
                suggestion=""
            )
        else:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Found {hard_count} hard contradiction(s) that must be resolved",
                value=hard_count,
                suggestion=(
                    "Resolve all HARD conflicts before publication. "
                    "Review conflicting data sources and determine which value is correct. "
                    "Update assessment with resolved values."
                ),
                details={"conflicts": conflicts}
            )
    
    def _evidence_coverage_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 2: Evidence Coverage Check
        
        Blocks if evidence coverage is below threshold.
        Evidence coverage measures the percentage of claims that have
        supporting evidence excerpts.
        
        Threshold: >= 95%
        Formula: (Claims with evidence_excerpt) / (Total claims)
        
        Args:
            assessment: Assessment dictionary with claims/evidence data
        
        Returns:
            PublicationGateResult with status
        """
        gate_name = "evidence_coverage"
        
        # Extract evidence coverage from assessment
        coverage = self._extract_evidence_coverage(assessment)
        
        passed = coverage >= self.config.evidence_coverage_threshold
        
        if passed:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"Evidence coverage at {coverage:.1%} (threshold: {self.config.evidence_coverage_threshold:.0%})",
                value=coverage,
                suggestion=""
            )
        else:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Evidence coverage {coverage:.1%} below threshold {self.config.evidence_coverage_threshold:.0%}",
                value=coverage,
                suggestion=(
                    f"Add evidence excerpts to at least "
                    f"{((self.config.evidence_coverage_threshold - coverage) * 100):.0f}% more claims. "
                    "Review claims without evidence and extract supporting text from source data."
                ),
                details={
                    "current_coverage": coverage,
                    "required_coverage": self.config.evidence_coverage_threshold,
                    "gap": self.config.evidence_coverage_threshold - coverage
                }
            )
    
    def _financial_validity_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 3: Financial Validity Check
        
        Blocks if financial data contains default values (0, None, empty).
        Implements the "No Defaults in Money" rule.
        
        Threshold: All critical financial fields must have valid non-default values
        Critical fields: occupancy_rate, direct_channel_percentage, adr_cop
        
        Args:
            assessment: Assessment dictionary with financial data
        
        Returns:
            PublicationGateResult with status
        """
        gate_name = "financial_validity"
        
        # Extract financial data
        financial_data = self._extract_financial_data(assessment)
        
        if not financial_data:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="No financial data found in assessment",
                value=None,
                suggestion="Run financial validation or onboarding to collect hotel financial data"
            )
        
        # Validate using NoDefaultsValidator
        validator = NoDefaultsValidator()
        validation_result = validator.validate(financial_data)
        
        passed = validation_result.can_calculate
        
        if passed:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="All financial data validated - no default values detected",
                value=True,
                suggestion=""
            )
        else:
            blocked_fields = [b.field for b in validation_result.blocks]
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Financial data contains default values in: {', '.join(blocked_fields)}",
                value=False,
                suggestion=(
                    "Complete the onboarding process with real financial data: "
                    f"{', '.join(blocked_fields)}. "
                    "Default values (0, None, empty) are not allowed in financial calculations."
                ),
                details={
                    "blocked_fields": blocked_fields,
                    "blocks": [
                        {
                            "field": b.field,
                            "value": b.value,
                            "reason": b.reason.value,
                            "hint": b.correction_hint
                        }
                        for b in validation_result.blocks
                    ]
                }
            )
    
    def _coherence_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 4: Coherence Score Check
        
        Blocks if coherence score is below threshold.
        Coherence measures alignment between diagnostic, proposal, and assets.
        
        Threshold: >= 0.8
        Interpretation:
        - >= 0.8: "Certified" - ready for publication
        - 0.5-0.8: "Preliminary" - needs disclaimer
        - < 0.5: "Draft" - do not send
        
        Args:
            assessment: Assessment dictionary with coherence data
        
        Returns:
            PublicationGateResult with status
        """
        gate_name = "coherence"
        
        # Extract coherence score from assessment
        coherence_score = self._extract_coherence_score(assessment)
        
        if coherence_score is None:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="Coherence score not found in assessment",
                value=None,
                suggestion="Run coherence validation to generate coherence score"
            )
        
        passed = coherence_score >= self.config.coherence_threshold
        
        if passed:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"Coherence score {coherence_score:.2f} meets threshold {self.config.coherence_threshold}",
                value=coherence_score,
                suggestion=""
            )
        else:
            status = GateStatus.BLOCKED if coherence_score < 0.5 else GateStatus.FAILED
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=status,
                message=f"Coherence score {coherence_score:.2f} below threshold {self.config.coherence_threshold}",
                value=coherence_score,
                suggestion=(
                    "Review alignment between diagnostic problems and proposed assets. "
                    "Ensure every problem has a corresponding solution and all assets are justified. "
                    f"Current gap: {(self.config.coherence_threshold - coherence_score):.2f} points."
                ),
                details={
                    "coherence_score": coherence_score,
                    "threshold": self.config.coherence_threshold,
                    "gap": self.config.coherence_threshold - coherence_score
                }
            )
    
    def _critical_recall_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 5: Critical Issue Recall Check
        
        Blocks if critical issue recall is below threshold.
        Critical recall measures percentage of critical issues detected
        vs. total critical issues present.
        
        Threshold: >= 90%
        Critical issues include:
        - Default CMS titles/taglines
        - Performance score < 50
        - LCP > 4s
        - Critical schema missing (image, aggregateRating)
        
        Args:
            assessment: Assessment dictionary with audit results
        
        Returns:
            PublicationGateResult with status
        """
        gate_name = "critical_recall"
        
        # Extract critical recall from assessment
        critical_recall = self._extract_critical_recall(assessment)
        
        if critical_recall is None:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="Critical recall metric not found in assessment",
                value=None,
                suggestion="Ensure audit results include critical issue detection data"
            )
        
        passed = critical_recall >= self.config.critical_recall_threshold
        
        if passed:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"Critical recall at {critical_recall:.1%} (threshold: {self.config.critical_recall_threshold:.0%})",
                value=critical_recall,
                suggestion=""
            )
        else:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Critical recall {critical_recall:.1%} below threshold {self.config.critical_recall_threshold:.0%}",
                value=critical_recall,
                suggestion=(
                    "Review critical issue detection algorithms. "
                    "Ensure all critical issues are being detected: CMS defaults, "
                    "performance problems, and missing critical schema. "
                    f"Gap: {((self.config.critical_recall_threshold - critical_recall) * 100):.0f}% of critical issues missed."
                ),
                details={
                    "critical_recall": critical_recall,
                    "threshold": self.config.critical_recall_threshold,
                    "gap": self.config.critical_recall_threshold - critical_recall
                }
            )
    
    def _ethics_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 6: Ethics Check
        
        Validates that proposals are ethically sound:
        - ROI is not excessively negative
        - If there's pricing, there's a viable return path
        - Not all scenarios show zero returns
        
        Threshold: Must pass ethics validation
        
        Args:
            assessment: Assessment dictionary with financial data
            
        Returns:
            PublicationGateResult with status
        """
        gate_name = "ethics"
        
        result = self.ethics_gate.validate_from_assessment(assessment)
        
        if result.status == EthicsStatus.PASSED:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="Ethics validation passed",
                value=result.roi_projected,
                suggestion=""
            )
        elif result.status == EthicsStatus.WARNING:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"Ethics validation passed with warnings: {len(result.issues)}",
                value=result.roi_projected,
                suggestion=". ".join([i.message for i in result.issues[:2]])
            )
        else:
            error_issues = [i.message for i in result.issues if i.severity == "error"]
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Ethics validation failed: {'; '.join(error_issues[:2])}",
                value=result.roi_projected,
                suggestion="Review pricing and projected returns. Proposal must show viable ROI.",
                details=result.to_dict()
            )

    def _content_quality_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 7: Content Quality Check

        Validates commercial documents for visible errors that damage
        client credibility: placeholder regions, duplicate currency,
        zero-confidence statements, mixed languages.

        Blocker issues cause the gate to fail. Warnings pass with advisory.

        Reads documents from assessment["diagnostico_text"] and/or
        assessment["propuesta_text"] when available.

        Args:
            assessment: Assessment dictionary with document text.

        Returns:
            PublicationGateResult with status.
        """
        gate_name = "content_quality"

        diag_text = assessment.get("diagnostico_text", "")
        prop_text = assessment.get("propuesta_text", "")
        hotel_data = assessment.get("hotel_data", {})

        diag_result = self.content_quality_gate.validate_document(
            diag_text, "diagnostico", hotel_data
        ) if diag_text else None

        prop_result = self.content_quality_gate.validate_document(
            prop_text, "propuesta", hotel_data
        ) if prop_text else None

        # Collect all issues
        all_issues = []
        if diag_result:
            all_issues.extend(diag_result.issues)
        if prop_result:
            all_issues.extend(prop_result.issues)

        blockers = [i for i in all_issues if i.severity == "blocker"]
        warnings = [i for i in all_issues if i.severity == "warning"]

        if not all_issues:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="Document quality checks passed: no issues detected",
                value=1.0,
                suggestion="",
            )

        if blockers:
            blocker_msgs = [i.message for i in blockers[:3]]
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"Content quality blockers: {len(blockers)} - {'; '.join(blocker_msgs)}",
                value=diag_result.score if diag_result else 0.0,
                suggestion=(
                    "Run ContentScrubber to auto-fix issues, then re-validate. "
                    "If scrubber cannot fix, review LLM prompt quality."
                ),
                details={
                    "blockers": [i.to_dict() if hasattr(i, "to_dict") else str(i.__dict__) for i in blockers],
                    "warnings": len(warnings),
                },
            )

        # Only warnings — gate passes but signals advisory
        warning_msgs = [i.message for i in warnings[:3]]
        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,
            status=GateStatus.PASSED,
            message=f"Content quality: {len(warnings)} warning(s) - {'; '.join(warning_msgs)}",
            value=0.0 if diag_result is None else max(diag_result.score, prop_result.score if prop_result else diag_result.score),
            suggestion="Consider running ContentScrubber for cleaner documents",
            details={"warnings": warning_msgs},
        )

    def _asset_confidence_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 8: Asset Confidence Check

        Validates that generated assets have acceptable confidence scores.
        Assets with confidence_score < threshold are flagged as warnings
        (not blocking) to alert the client about quality concerns.

        Uses Option A (Conservative): WARNING status, not BLOCKED.
        Threshold: configurable, default 0.7.

        Args:
            assessment: Assessment dictionary with generated_assets data

        Returns:
            PublicationGateResult with status PASSED or WARNING
        """
        gate_name = "asset_confidence"
        threshold = 0.7

        generated_assets = assessment.get("generated_assets", [])

        if not generated_assets:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="No generated assets to evaluate",
                value=1.0,
                suggestion="",
                details={"total_assets": 0, "above_threshold": 0, "below_threshold": 0}
            )

        low_confidence_assets = [
            a for a in generated_assets
            if a.get("confidence_score", 0) < threshold
        ]

        if not low_confidence_assets:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"All {len(generated_assets)} assets meet confidence threshold ({threshold})",
                value=1.0,
                suggestion="",
                details={
                    "total_assets": len(generated_assets),
                    "above_threshold": len(generated_assets),
                    "below_threshold": 0
                }
            )

        avg_confidence = sum(
            a.get("confidence_score", 0) for a in generated_assets
        ) / len(generated_assets)

        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,  # Conservative: warns but does not block
            status=GateStatus.WARNING,
            message=f"{len(low_confidence_assets)} asset(s) below confidence threshold ({threshold})",
            value=avg_confidence,
            suggestion="Run enrichment phase to improve asset quality",
            details={
                "total_assets": len(generated_assets),
                "above_threshold": len(generated_assets) - len(low_confidence_assets),
                "below_threshold": len(low_confidence_assets),
                "low_confidence_assets": [
                    {"type": a["asset_type"], "score": a["confidence_score"]}
                    for a in low_confidence_assets
                ]
            }
        )
    
    # Helper methods for extracting data from assessment

    def _proposal_asset_alignment_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate 9: Proposal-Asset Alignment Check

        Verifies that every service promised in the commercial proposal
        has a corresponding generated asset. Missing assets mean the client
        is paying for something they don't receive.

        Status: WARNING (not blocking) if assets are missing.
        Threshold: All 7 promised services should have assets.

        Args:
            assessment: Assessment dictionary with generated_assets and/or proposal_services

        Returns:
            PublicationGateResult with status WARNING if missing assets
        """
        gate_name = "proposal_asset_alignment"

        from modules.asset_generation.proposal_asset_alignment import (
            verify_proposal_asset_alignment,
            ALL_PROMISED_SERVICES,
        )

        generated_assets = assessment.get("generated_assets", [])
        proposal_services = assessment.get("proposal_services", ALL_PROMISED_SERVICES)

        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
        )

        if report.all_aligned:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=f"All {report.total_services} promised services have corresponding assets (7/7)",
                value=report.alignment_percentage,
                suggestion="",
                details=report.to_dict(),
            )

        missing_names = [s.service_name for s in report.missing]
        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,  # WARNING, not blocking — warns but doesn't block publication
            status=GateStatus.WARNING,
            message=(
                f"{len(report.missing)} promised service(s) missing assets: "
                f"{', '.join(missing_names)}"
            ),
            value=report.alignment_percentage,
            suggestion=(
                "Review asset generation pipeline to ensure all promised services "
                "produce deliverables. The following services lack assets: "
                f"{', '.join(missing_names)}"
            ),
            details=report.to_dict(),
        )

    def _extract_conflicts(self, assessment: Dict[str, Any]) -> List[Dict]:
        """Extract conflicts list from assessment."""
        # Try different paths where conflicts might be stored
        if "conflicts" in assessment:
            return assessment["conflicts"]
        if "validation" in assessment and isinstance(assessment["validation"], dict):
            return assessment["validation"].get("conflicts", [])
        if "cross_validation" in assessment:
            return assessment["cross_validation"].get("conflicts", [])
        if "validation_summary" in assessment and isinstance(assessment["validation_summary"], dict):
            return assessment["validation_summary"].get("conflicts", [])
        return []
    
    def _extract_evidence_coverage(self, assessment: Dict[str, Any]) -> float:
        """Extract evidence coverage from assessment."""
        # Try direct evidence_coverage in assessment root
        if "evidence_coverage" in assessment:
            return float(assessment["evidence_coverage"])

        # Try direct metrics
        if "metrics" in assessment and isinstance(assessment["metrics"], dict):
            coverage = assessment["metrics"].get("evidence_coverage")
            if coverage is not None:
                return float(coverage)
        
        # Try quality_metrics
        if "quality_metrics" in assessment:
            coverage = assessment["quality_metrics"].get("evidence_coverage")
            if coverage is not None:
                return float(coverage)
        
        # Calculate from claims if available
        if "claims" in assessment:
            claims = assessment["claims"]
            if claims:
                with_evidence = sum(1 for c in claims if c.get("evidence_excerpt"))
                return with_evidence / len(claims)
        
        # Try diagnostic document
        if "diagnostic" in assessment and isinstance(assessment["diagnostic"], dict):
            claims = assessment["diagnostic"].get("claims", [])
            if claims:
                with_evidence = sum(1 for c in claims if c.get("evidence_excerpt"))
                return with_evidence / len(claims)
        
        return 0.0
    
    def _extract_financial_data(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data from assessment."""
        # Try direct financial_data
        if "financial_data" in assessment:
            return assessment["financial_data"]
        
        # Try hotel_data
        if "hotel_data" in assessment:
            return assessment["hotel_data"]
        
        # Try validation_summary fields
        if "validation_summary" in assessment and isinstance(assessment["validation_summary"], dict):
            fields = assessment["validation_summary"].get("fields", [])
            data = {}
            for field in fields:
                if isinstance(field, dict):
                    data[field.get("field_name")] = field.get("value")
            if data:
                return data
        
        # Try onboarding_data
        if "onboarding_data" in assessment:
            return assessment["onboarding_data"]
        
        return {}
    
    def _extract_coherence_score(self, assessment: Dict[str, Any]) -> Optional[float]:
        """Extract coherence score from assessment."""
        # Try direct coherence_score in assessment root
        if "coherence_score" in assessment:
            return float(assessment["coherence_score"])
        
        # Try metrics
        if "metrics" in assessment and isinstance(assessment["metrics"], dict):
            score = assessment["metrics"].get("coherence_score")
            if score is not None:
                return float(score)
        
        # Try coherence_report
        if "coherence_report" in assessment and isinstance(assessment["coherence_report"], dict):
            return assessment["coherence_report"].get("overall_score")
        
        # Try quality_metrics
        if "quality_metrics" in assessment:
            return assessment["quality_metrics"].get("coherence_score")
        
        return None
    
    def _extract_critical_recall(self, assessment: Dict[str, Any]) -> Optional[float]:
        """Extract critical recall from assessment."""
        # Try direct critical_recall in assessment root
        if "critical_recall" in assessment:
            return float(assessment["critical_recall"])
        
        # Try metrics
        if "metrics" in assessment and isinstance(assessment["metrics"], dict):
            recall = assessment["metrics"].get("critical_recall")
            if recall is not None:
                return float(recall)
        
        # Try quality_metrics
        if "quality_metrics" in assessment:
            return assessment["quality_metrics"].get("critical_recall")
        
        # Try audit_results
        if "audit_results" in assessment and isinstance(assessment["audit_results"], dict):
            return assessment["audit_results"].get("critical_recall")
        
        # Calculate from critical issues
        critical_issues = assessment.get("critical_issues", [])
        detected = assessment.get("critical_issues_detected", [])
        if critical_issues and detected is not None:
            return len(detected) / len(critical_issues) if critical_issues else 1.0
        
        return None


# Convenience functions for direct use

def run_publication_gates(
    assessment: Dict[str, Any],
    config: Optional[PublicationGateConfig] = None
) -> List[PublicationGateResult]:
    """
    Execute all publication gates on an assessment.
    
    This is the main entry point for checking publication readiness.
    
    Args:
        assessment: Dictionary containing all assessment data
        config: Optional gate configuration. Uses defaults if None.
    
    Returns:
        List of PublicationGateResult for each gate
    
    Example:
        results = run_publication_gates(assessment)
        
        for result in results:
            icon = "✅" if result.passed else "❌"
            print(f"{icon} {result.gate_name}: {result.message}")
    """
    orchestrator = PublicationGatesOrchestrator(config)
    return orchestrator.run_all(assessment)


def check_publication_readiness(assessment: Dict[str, Any]) -> Dict[str, Any]:
    """
    Check if assessment is ready for publication.
    
    Provides a comprehensive readiness report including:
    - Overall readiness status
    - Individual gate results
    - Blocking issues
    - Recommendations
    
    Args:
        assessment: Dictionary containing all assessment data
    
    Returns:
        Dictionary with readiness report:
        {
            "ready": bool,
            "status": "READY" | "NOT_READY",
            "gate_results": [...],
            "blocking_issues": [...],
            "summary": {...}
        }
    
    Example:
        report = check_publication_readiness(assessment)
        if report["ready"]:
            print("Safe to publish!")
        else:
            for issue in report["blocking_issues"]:
                print(f"Block: {issue}")
    """
    results = run_publication_gates(assessment)
    
    blocking_gates = [r for r in results if not r.passed]
    ready = len(blocking_gates) == 0
    
    # Build summary
    passed_count = sum(1 for r in results if r.passed)
    
    summary = {
        "total_gates": len(results),
        "passed": passed_count,
        "failed": len(results) - passed_count,
        "blocked": sum(1 for r in results if r.status == GateStatus.BLOCKED),
        "timestamp": datetime.now().isoformat()
    }
    
    return {
        "ready": ready,
        "status": "READY_FOR_PUBLICATION" if ready else "NOT_READY",
        "gate_results": [r.to_dict() for r in results],
        "blocking_issues": [
            {
                "gate": r.gate_name,
                "message": r.message,
                "suggestion": r.suggestion,
                "value": r.value
            }
            for r in blocking_gates
        ],
        "summary": summary
    }


def generate_gate_failure_report(results: List[PublicationGateResult]) -> str:
    """
    Generate a human-readable report of gate failures.
    
    Args:
        results: List of gate results from run_publication_gates()
    
    Returns:
        Formatted string report suitable for display or logging
    
    Example:
        results = run_publication_gates(assessment)
        if not all(r.passed for r in results):
            print(generate_gate_failure_report(results))
    """
    lines = []
    lines.append("=" * 60)
    lines.append("PUBLICATION GATE FAILURE REPORT")
    lines.append("=" * 60)
    lines.append("")
    
    failed_gates = [r for r in results if not r.passed]
    
    if not failed_gates:
        lines.append("✅ All gates passed - ready for publication!")
        return "\n".join(lines)
    
    lines.append(f"❌ {len(failed_gates)} gate(s) failed:")
    lines.append("")
    
    for i, result in enumerate(failed_gates, 1):
        status_icon = "🚫" if result.status == GateStatus.BLOCKED else "⚠️"
        lines.append(f"{i}. {status_icon} {result.gate_name.upper()}")
        lines.append(f"   Status: {result.status.value}")
        lines.append(f"   Message: {result.message}")
        if result.value is not None:
            lines.append(f"   Value: {result.value}")
        if result.suggestion:
            lines.append(f"   Suggestion: {result.suggestion}")
        if result.details:
            lines.append(f"   Details: {result.details}")
        lines.append("")
    
    lines.append("=" * 60)
    lines.append("ACTION REQUIRED: Resolve all blocking issues before publication")
    lines.append("=" * 60)
    
    return "\n".join(lines)


# Export all public classes and functions
__all__ = [
    "GateStatus",
    "PublicationGateResult",
    "PublicationGateConfig",
    "PublicationGatesOrchestrator",
    "run_publication_gates",
    "check_publication_readiness",
    "generate_gate_failure_report"
]
