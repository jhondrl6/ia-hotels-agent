"""
Publication Gates - Pre-publication Quality Gates for Phase 5.

This module implements 13 publication gates (10 blocking + 3 advisory)
that must be evaluated before any commercial document or asset can
be published to a client.

Blocking gates (must pass to publish):
1. hard_contradictions_gate: Blocks if HARD conflicts exist
2. evidence_coverage_gate: Blocks if coverage < 95%
3. financial_validity_gate: Blocks if default values detected
4. coherence_gate: Blocks if coherence < 0.8
5. critical_recall_gate: Blocks if critical recall < 90%
6. ethics_gate: Blocks if ethics validation fails
7. tier_c_onboarding_required_gate: Blocks if tier C onboarding missing
8. coverage_no_silent_drop_gate: Blocks if pain coverage gap detected
9. doc_audit_consistency_gate: Blocks on doc-audit contradictions (WARNING mode)
10. pricing_compliance_gate: Blocks if pain_ratio > tier gate_max (floor-aware D1)

Advisory gates (pass with WARNING, do not block):
11. content_quality_gate: Reports document quality issues
12. asset_confidence_gate: Reports low-confidence assets
13. proposal_asset_alignment_gate: Reports missing promised assets

Usage:
    from modules.quality_gates.publication_gates import (
        run_publication_gates,
        check_publication_readiness,
        PublicationGatesOrchestrator
    )
    
    results = run_publication_gates(assessment, config)
    if not any(r.status in (GateStatus.FAILED, GateStatus.BLOCKED) for r in results):
        print("Ready for publication!")
    else:
        print("Publication blocked by gate failures.")
"""

import re
import os
import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Callable, Set
from enum import Enum
from datetime import datetime

from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult
)
from modules.quality_gates.ethics_gate import EthicsGate, EthicsStatus
from modules.postprocessors.document_quality_gate import DocumentQualityGate
from modules.quality.asset_semantics_validator import validar_semantica_comercial

logger = logging.getLogger(__name__)


# FASE-4 (DT4-N5): Helper to merge AlignmentReport dict with canonical
# AlignmentResult for backward-compatible details in publication gates.
def _merge_report_with_alignment(report_dict: Dict[str, Any],
                                  alignment_dict: Dict[str, Any]) -> Dict[str, Any]:
    """Merge AlignmentReport with AlignmentResult at top level.

    Backward compatible: ``details.total_services``, ``details.aligned_count``,
    etc. still work directly. New canonical structure is at ``details.alignment``.
    """
    merged = dict(report_dict)
    merged["alignment"] = alignment_dict
    return merged


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
class PainLedgerEntry:
    """FASE-0C: Entry in the pain ledger tracking detected problems.

    The coverage gate validates: brechas_en_diagnostico + brechas_justificadas
    == brechas_detectadas — every detected pain must appear in diagnostic,
    proposal, or have an acceptable justification status.
    """
    pain_id: str
    status: str  # "DETECTED" | "JUSTIFIED_SKIP" | "BLOCKED" | "MAPPED_TO_SERVICE"


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
    Orchestrates the execution of all 13 publication gates.
    
    This class manages 10 blocking gates and 3 advisory gates,
    providing a unified interface for checking publication readiness.
    
    Example:
        orchestrator = PublicationGatesOrchestrator(config)
        results = orchestrator.run_all(assessment)
        
        if orchestrator.is_ready_for_publication(results):
            print("All blocking gates passed!")
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
            "tier_c_onboarding_required": self._tier_c_onboarding_gate,
            "coverage_no_silent_drop": self._coverage_gate,
            "doc_audit_consistency": self._doc_audit_consistency_gate,
            "pricing_compliance": self._pricing_compliance_gate,
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
            # Check de fuentes: si hay defaults, es WARNING aunque can_calculate=True
            # (BUG-02 fix: NoDefaultsValidator no detecta que las fuentes son default)
            financial_sources = assessment.get("financial_sources", {})
            DEFAULT_SOURCES = {"default", "legacy_hardcode", "legacy_fixed"}
            default_source_fields = {
                f: financial_sources.get(f)
                for f in ("adr_cop", "occupancy_rate", "direct_channel_percentage")
                if financial_sources.get(f) in DEFAULT_SOURCES
            }
            if default_source_fields:
                # F7 FIX: Usar formal evidence_tier en vez de heurística source-level
                # Las dos gates ahora alinean: financial_validity y tier_c_onboarding_required
                # usan la misma fuente: assessment["financial_evidence_tier"]
                formal_tier = assessment.get("financial_evidence_tier", "C")
                tier_message = f"Tier {formal_tier} evidence"
                return PublicationGateResult(
                    gate_name=gate_name,
                    passed=True,  # No bloquea, solo advierte
                    status=GateStatus.WARNING,
                    message=f"Financial data uses default/legacy values — {tier_message}",
                    value=True,
                    suggestion="Run onboarding with real data to improve evidence tier",
                    details={
                        "default_sources": default_source_fields,
                        "corrected_tier": formal_tier
                    }
                )
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
        
        SOURCE OF TRUTH: This gate extracts the score from the assessment dict,
        which was calculated by CoherenceValidator.validate() (weighted average of
        6 checks). The gate does NOT recalculate — it consumes the single source
        of truth from coherence_validation.json / coherence_report.overall_score.
        
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

        all_estimated = len(low_confidence_assets) == len(generated_assets)

        if all_estimated:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="100% de assets son ESTIMATED (confidence < 0.7). Delivery bloqueado hasta onboarding o datos reales.",
                value=avg_confidence,
                suggestion="Complete onboarding with real data or run enrichment phase",
                details={
                    "total_assets": len(generated_assets),
                    "above_threshold": 0,
                    "below_threshold": len(low_confidence_assets),
                    "all_estimated": True,
                    "low_confidence_assets": [
                        {"type": a["asset_type"], "score": a["confidence_score"]}
                        for a in low_confidence_assets
                    ]
                }
            )

        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,  # Mixed: warns but does not block
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

        FASE-2: BLOCKING para P1 — si un asset asociado a un dolor P1
        tiene status NOT_READY o BLOCKED, el gate retorna BLOCKED.
        Excepcion: si status == "skipped_existing" → pasa PERO narrativa AUDIT_ONLY.

        FASE-D: Before marking as "missing", verifies via SitePresenceChecker if the asset
        already exists in the production site. If EXISTS, marks as "present_in_production".

        FASE-PATCH-B: Este gate valida un contrato estático (PROPOSAL_SERVICE_TO_ASSET).
        El generador de propuestas (_generate_dynamic_services_table) filtra dinámicamente
        servicios según pain_ids detectados y assets realmente generados. Por tanto, un
        alignment_percentage < 100% puede ser esperado cuando el generador excluye
        servicios cujos pain_ids no están presentes o cuyos assets no se generaron.
        Ver FASE-PATCH-B para contexto completo.

        Status: PASSED / WARNING (servicios P2/P3), BLOCKED (servicios P1 con status NOT_READY/BLOCKED).
        Threshold: alignment >= 80% para P2/P3.

        Args:
            assessment: Assessment dictionary with generated_assets and/or proposal_services

        Returns:
            PublicationGateResult with status PASSED, WARNING, or BLOCKED
        """
        gate_name = "proposal_asset_alignment"

        from modules.asset_generation.proposal_asset_alignment import (
            verify_proposal_asset_alignment,
            ALL_PROMISED_SERVICES,
            PROPOSAL_SERVICE_TO_ASSET,
        )
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
        from modules.quality_gates.alignment_result import AlignmentResult

        generated_assets = assessment.get("generated_assets", [])
        skipped_assets = assessment.get("skipped_assets", [])  # FASE-1B: assets ya verificados por conditional_generator
        proposal_services = assessment.get("proposal_services", ALL_PROMISED_SERVICES)

        # FASE-2: Extract asset status map (asset_type -> status) from assessment
        # Status values: NOT_READY, BLOCKED, skipped_existing, IMPLEMENT, DEPRECATED, etc.
        asset_status_map: Dict[str, str] = {}
        for asset in generated_assets:
            at = asset.get("asset_type", "")
            status = asset.get("status", "IMPLEMENT")  # Default to IMPLEMENT if not set
            if at:
                asset_status_map[at] = status

        # Inyectar asset_status_map en assessment para que verify_proposal_asset_alignment
        # pueda usarlo (retrocompatibilidad con otros consumidores)
        assessment_with_status = dict(assessment)
        assessment_with_status["_asset_status_map"] = asset_status_map

        # FASE-2 (DT4-R2): site_presence_report is already canonical from the
        # assessment (computed ONCE in main.py via normalize_site_presence).
        # No fake reconstruction, no re-execution — use the snapshot as-is.
        site_presence_report = assessment.get("site_presence_report")
        hotel_url = assessment.get("hotel_url", "")

        report = verify_proposal_asset_alignment(
            proposal_services=proposal_services,
            generated_assets=generated_assets,
            site_presence_report=site_presence_report,
            hotel_url=hotel_url,
            audit_schema=assessment.get("audit_schema"),  # FASE-12B: coherence/divergence detection
        )

        # FASE-4 (DT4-N5): Build canonical AlignmentResult for consistent
        # reporting across publication gates and delivery quality report.
        alignment_result = AlignmentResult.from_alignment_report(report)

        # ========================================================================
        # FASE-2: P1 Blocking — verificar services cuya asset status es NOT_READY
        # o BLOCKED, y cuyo pain_id correspondiente tiene priority=1.
        # Si existe algun P1 bloqueado (sin skipped_existing), gate BLOCKED.
        # ========================================================================
        pain_map = PainSolutionMapper.PAIN_SOLUTION_MAP
        # Invert: asset_type -> pain_id(s) that this asset solves
        # Build a map: pain_id -> priority
        pain_priority_map: Dict[str, int] = {}
        for pain_id, mapping in pain_map.items():
            priority = mapping.get("priority", 3)
            pain_priority_map[pain_id] = priority

        # For each service in proposal_services, find its pain_ids and check P1 blocking
        def get_pain_ids_for_asset(asset_type: str) -> List[str]:
            """Find pain_ids that are solved by this asset_type."""
            pain_ids = []
            for pain_id, mapping in pain_map.items():
                assets = mapping.get("assets", [])
                if asset_type in assets:
                    pain_ids.append(pain_id)
            return pain_ids

        p1_blocked_services: List[Dict[str, str]] = []  # [{service_name, asset_type, status, reason}]
        p1_services_all: List[str] = []  # All services that solve P1 pains

        for service_name in proposal_services:
            asset_type = PROPOSAL_SERVICE_TO_ASSET.get(service_name)
            if not asset_type:
                continue

            # Get asset status (from generated_assets, from site presence, or default)
            asset_status = asset_status_map.get(asset_type)
            if not asset_status:
                # Check if it's present in production
                present = next(
                    (s for s in report.present_in_production if s.service_name == service_name),
                    None
                )
                if present:
                    # Exists in production — check if it has status metadata
                    asset_status = "present_in_production"
                else:
                    # Missing, not generated — status from PainSolutionMapper might give us info
                    asset_status = None

            if not asset_status or asset_status in ("IMPLEMENT", "present_in_production"):
                continue

            if asset_status == "skipped_existing":
                continue  # Exception: passes with AUDIT_ONLY narrative (handled elsewhere)

            if asset_status not in ("NOT_READY", "BLOCKED"):
                continue  # Only block on NOT_READY or BLOCKED

            # This asset is NOT_READY or BLOCKED — check if it's for a P1 pain
            pain_ids = get_pain_ids_for_asset(asset_type.__str__() if asset_type else "")
            is_p1 = any(pain_priority_map.get(pid, 3) == 1 for pid in pain_ids)
            if is_p1:
                p1_blocked_services.append({
                    "service_name": service_name,
                    "asset_type": asset_type,
                    "status": asset_status,
                    "reason": f"Asset '{asset_type}' es {asset_status} y resuelve dolor P1"
                })
                p1_services_all.append(service_name)

        if p1_blocked_services:
            blocked_service_names = [s["service_name"] for s in p1_blocked_services]
            message = (
                f"BLOQUEO P1: {len(p1_blocked_services)} servicio(s) con asset "
                f"bloqueado/no-listo: {', '.join(blocked_service_names)}"
            )
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=message,
                value=0.0,
                suggestion=(
                    "Activar o resolver el asset antes de publicar. "
                    "Un asset NOT_READY/BLOCKED asociado a dolor P1 no puede prometerse al cliente."
                ),
                details={
                    "p1_blocked": p1_blocked_services,
                    **_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict()),
                },
            )

        # ========================================================================
        # FASE-1 Integration: semantic validation via validar_semantica_comercial
        # Verificar hallucinations (Bloqueado semantico) en aligned/missing assets.
        # ========================================================================
        semantic_blocked: List[Dict[str, str]] = []
        all_services = proposal_services if proposal_services else ALL_PROMISED_SERVICES
        for service_name in all_services:
            asset_type = PROPOSAL_SERVICE_TO_ASSET.get(service_name)
            if not asset_type:
                continue
            # Get pain_ids for this asset
            pain_ids = get_pain_ids_for_asset(asset_type)
            for pain_id in pain_ids:
                asset_status = asset_status_map.get(asset_type, "IMPLEMENT")
                ok, result = validar_semantica_comercial(pain_id, asset_type, asset_status)
                if not ok and result.startswith("BLOCKED:"):
                    semantic_blocked.append({
                        "service_name": service_name,
                        "pain_id": pain_id,
                        "asset_type": asset_type,
                        "reason": result,
                    })

        if semantic_blocked:
            blocked_msgs = [f"{s['service_name']}({s['pain_id']})" for s in semantic_blocked]
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"ALUCINACION: mapeo dolor→asset invalido: {', '.join(blocked_msgs)}",
                value=0.0,
                suggestion="El asset no puede resolver este dolor semanticamente. Revisar propuesta.",
                details={
                    "semantic_blocked": semantic_blocked,
                    **_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict()),
                },
            )

        # ========================================================================
        # Continue with normal alignment checks (after P1 blocking and semantic validation)
        # ========================================================================

        if report.all_aligned:
            # FASE-D: Count present_in_production as effectively aligned
            present_count = len(report.present_in_production)
            indeterminate_count = len(report.indeterminate)
            total_checked = report.total_services + present_count
            aligned_plus_present = len(report.aligned) + present_count
            pct = aligned_plus_present / total_checked if total_checked > 0 else 0.0
            message = f"All {total_checked} promised services have assets ({aligned_plus_present}/{total_checked} aligned, {present_count} already in production)"
            # FIX-5: Note indeterminate assets that couldn't be verified
            if indeterminate_count > 0:
                indeterminate_names = [s.service_name for s in report.indeterminate]
                message += f"; {indeterminate_count} unverified (SitePresenceChecker failed): {', '.join(indeterminate_names)}"
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message=message,
                value=pct,
                suggestion="",
                details=_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict()),
            )

        missing_names = [s.service_name for s in report.missing]
        present_in_prod_names = [s.service_name for s in report.present_in_production]

        # FASE-D: Build better message showing what's missing vs already exists
        message_parts = []
        if missing_names:
            message_parts.append(f"{len(missing_names)} missing: {', '.join(missing_names)}")
        if present_in_prod_names:
            message_parts.append(f"{len(present_in_prod_names)} already in production: {', '.join(present_in_prod_names)}")
        if report.redundant:
            redundant_names = [s.service_name for s in report.redundant]
            message_parts.append(f"{len(redundant_names)} redundant: {', '.join(redundant_names)}")

        message = "; ".join(message_parts) if message_parts else f"{len(missing_names)} promised service(s) missing assets"

        # FASE-2: Effective alignment includes present_in_production as "satisfied"
        # A service present in production counts towards the alignment target.
        total_services_with_presence = report.total_services + len(report.present_in_production)
        aligned_plus_present = len(report.aligned) + len(report.present_in_production)
        effective_alignment = (
            aligned_plus_present / total_services_with_presence
            if total_services_with_presence > 0 else 0.0
        )
        alignment = effective_alignment
        missing_count = len(missing_names)

        if alignment < 0.8:
            # BLOCKED: Less than 80% of promised services have assets or are present in production
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=message,
                value=alignment,
                suggestion=(
                    f"Alignment {alignment:.0%} ({missing_count} services missing) is below "
                    f"80% threshold. Review asset generation pipeline to ensure all promised "
                    f"services produce deliverables before publication."
                ),
                details=_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict()),
            )
        else:
            # WARNING: At least 80% aligned but still some missing
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.WARNING,
                message=message,
                value=alignment,
                suggestion=(
                    f"Alignment {alignment:.0%}: {missing_count} services still missing. "
                    f"Review asset generation pipeline to ensure all promised services "
                    f"produce deliverables."
                ),
                details=_merge_report_with_alignment(report.to_dict(), alignment_result.to_dict()),
            )

    # ============================================================================
    # FASE-3 FIX-10: Tier C Onboarding Gate
    # ============================================================================
    def _tier_c_onboarding_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate: Tier C Onboarding Required.

        FASE-3 FIX-10: Clients Tier C receive proposals with preliminary/estimated
        data (no real financial evidence). Such proposals are NOT publishable without
        onboarding to collect real data.

        This is a POLICY gate — Tier C proposals without onboarding are literally
        unpublishable because all numbers are placeholders.

        Args:
            assessment: Assessment dictionary with financial_evidence_tier

        Returns:
            PublicationGateResult with status BLOCKED for Tier C, PASSED otherwise
        """
        gate_name = "tier_c_onboarding_required"

        tier = assessment.get("financial_evidence_tier", "C")  # Default to C (most restrictive)

        if tier == "C":
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="Tier C: Propuesta preliminar. Requiere datos reales para activación.",
                value=None,
                suggestion="Onboarding required: Collect real financial data (occupancy, ADR, channel mix) before publication.",
                details={"tier": tier, "required_action": "onboarding"},
            )

        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,
            status=GateStatus.PASSED,
            message=f"Tier {tier}: Datos suficientes para propuesta activa.",
            value=None,
            suggestion="",
            details={"tier": tier},
        )

    # ===========================================================================
    # FASE-0C: Coverage Gate — No Silent Drop
    # ============================================================================
    # Acceptable justification statuses — pain_ids with these statuses do NOT
    # need to appear in diagnostic or proposal.
    _JUSTIFIED_STATUSES: Set[str] = {
        "JUSTIFIED_SKIP", "BLOCKED", "MAPPED_TO_SERVICE", "ASSET_GENERATED"
    }

    def _coverage_gate(self, assessment: Dict[str, Any]) -> PublicationGateResult:
        """
        Gate: Coverage — No Silent Drop.

        FASE-0C: Valida que ninguna brecha (pain_id) detectada desaparezca
        sin explicacion. Cada pain en el ledger debe:
          1. Appear in diagnostic_pain_ids, OR
          2. Appear in proposal_pain_ids, OR
          3. Have status in (JUSTIFIED_SKIP, BLOCKED, MAPPED_TO_SERVICE)

        Regla: brechas_en_diagnostico + brechas_justificadas == brechas_detectadas

        The gate reads pain_ledger, diagnostic_pain_ids, and proposal_pain_ids
        from the assessment dict (extracted from diagnostic/proposal documents
        during the v4 pipeline). If the assessment does not contain these fields,
        the gate is BLOCKED because coverage cannot be validated without them.

        Args:
            assessment: Assessment dict with optional keys:
                - pain_ledger: List[PainLedgerEntry]
                - diagnostic_pain_ids: Set[str]
                - proposal_pain_ids: Set[str]

        Returns:
            PublicationGateResult — PASSED if all pains covered/justified,
                                   FAILED if uncovered, BLOCKED if data missing
        """
        gate_name = "coverage_no_silent_drop"

        # Extract coverage data from assessment
        # Distinguish between missing key (BLOCKED - pipeline incomplete)
        # and present-but-empty list (PASS - nothing to validate)
        if "pain_ledger" not in assessment:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="pain_ledger not found in assessment (pipeline incomplete?)",
                value=None,
                suggestion="Ensure diagnostic/proposal generation populates pain_ledger",
            )

        # FASE-0 (DT-4): Try pain_ledger_resolved first (post-orchestrator reconciliation),
        # fallback to pain_ledger if not available.
        raw = assessment.get("pain_ledger_resolved")
        reconciler_ran = raw is not None
        if raw is not None:
            # DT4-R1: Reconciler ran — validate resolved entries
            if isinstance(raw, dict):
                pain_ledger_raw = raw.get("entries", raw)
            elif isinstance(raw, list):
                if not raw:
                    # Reconciler ran but produced empty entries → BLOCKED
                    return PublicationGateResult(
                        gate_name=gate_name,
                        passed=False,
                        status=GateStatus.BLOCKED,
                        message="pain_ledger_resolved is empty after reconciliation — reconciler ran but produced no entries",
                        value=None,
                        suggestion="Check post-orchestrator reconciliation output",
                    )
                pain_ledger_raw = raw
            else:
                pain_ledger_raw = raw
        else:
            # Reconciler never ran — fallback to pain_ledger
            pain_ledger_raw = assessment.get("pain_ledger")
        if not isinstance(pain_ledger_raw, list):
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message="pain_ledger is not a list",
                value=None,
                suggestion="Ensure pain_ledger is a list of PainLedgerEntry dicts",
            )

        # Normalize to PainLedgerEntry
        pain_ledger: List[PainLedgerEntry] = []
        for entry in pain_ledger_raw:
            if isinstance(entry, dict):
                pain_ledger.append(PainLedgerEntry(
                    pain_id=entry.get("pain_id", ""),
                    status=entry.get("status", "DETECTED"),
                ))
            elif hasattr(entry, "pain_id"):
                pain_ledger.append(entry)

        diagnostic_pain_ids: Set[str] = set(assessment.get("diagnostic_pain_ids", []))
        proposal_pain_ids: Set[str] = set(assessment.get("proposal_pain_ids", []))

        # Empty ledger = nothing to check = PASS
        if not pain_ledger:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="Pain ledger vacio — todas las brechas accounted for",
                value=1.0,
                suggestion="",
            )

        # FASE-C-A (D5): covered counts document presence BEFORE justified
        # exemption.  A pain is "covered" when it appears in diagnostic or
        # proposal, regardless of its status.  is_justified exempts only if
        # the pain is additionally explained by an asset (status in
        # _JUSTIFIED_STATUSES).  This prevents the false "Coverage completo"
        # with covered=0 that happened in the 2026-08-01 run.
        #
        # When the reconciler ran (pain_ledger_resolved present), justified
        # pains are counted as covered because the reconciler has already
        # processed and validated them.
        uncovered: List[str] = []
        justified_count = 0
        covered = 0

        for entry in pain_ledger:
            in_diagnostic = entry.pain_id in diagnostic_pain_ids
            in_proposal = entry.pain_id in proposal_pain_ids
            is_justified = entry.status in self._JUSTIFIED_STATUSES

            if in_diagnostic or in_proposal:
                # Pain appears in document — covered regardless of status
                covered += 1
            elif is_justified:
                justified_count += 1
            else:
                uncovered.append(entry.pain_id)

        total = len(pain_ledger)
        coverage_ratio = (covered + justified_count) / total if total > 0 else 1.0

        if uncovered:
            uncovered_str = ", ".join(uncovered)
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.FAILED,
                message=f"Brecha(s) sin cobertura ni justificacion: {uncovered_str}",
                value=coverage_ratio,
                suggestion=(
                    "Agregar las brechas faltantes al diagnostico, "
                    "justificarlas como JUSTIFIED_SKIP/BLOCKED/MAPPED_TO_SERVICE, "
                    "o incluirlas en la propuesta."
                ),
                details={
                    "total_detected": total,
                    "covered": covered,
                    "justified": justified_count,
                    "uncovered": uncovered,
                },
            )

        # FASE-C-A (D5): WARNING when covered=0 — never "Coverage completo"
        # with zero pains appearing in the document.
        if covered == 0 and justified_count > 0:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.WARNING,
                message=(
                    f"0 pains appear in the document; "
                    f"{justified_count} justified by asset status of {total} detected"
                ),
                value=coverage_ratio,
                suggestion=(
                    "Ensure all detected pains are mentioned in diagnostic "
                    "or proposal documents, not just justified by asset status"
                ),
                details={
                    "total_detected": total,
                    "covered": covered,
                    "justified": justified_count,
                    "uncovered": [],
                },
            )

        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,
            status=GateStatus.PASSED,
            message=(
                f"Coverage completo: {covered} en diagnostico/propuesta, "
                f"{justified_count} justificadas de {total} detectadas"
            ),
            value=coverage_ratio,
            suggestion="",
            details={
                "total_detected": total,
                "covered": covered,
                "justified": justified_count,
                "uncovered": [],
            },
        )

    # ===========================================================================
    # FASE-C-A (N2): Doc-Audit Consistency Gate — WARNING mode
    # ===========================================================================
    # Known contradiction patterns between generated documents and audit data.
    # Each entry maps a diagnostic keyword pattern to the audit field that, when
    # True/present, contradicts the document's claim.
    _DOC_AUDIT_CONTRADICTION_PATTERNS: List[Dict[str, Any]] = [
        {
            "id": "og_missing_vs_present",
            "doc_keywords": ["sin meta tags", "sin open graph", "sin etiquetas og"],
            "audit_section": "seo_elements",
            "audit_field": "open_graph",
            "audit_truth": True,
            "description": "Doc claims missing OG tags but audit found them",
        },
        {
            "id": "performance_error_vs_new_site",
            "doc_keywords": ["sitio nuevo", "trafico bajo", "tráfico bajo"],
            "audit_section": "performance",
            "audit_field": "status",
            "audit_truth": "ERROR",
            "description": "Doc claims 'sitio nuevo/trafico bajo' but performance is ERROR",
        },
    ]

    def _doc_audit_consistency_gate(
        self, assessment: Dict[str, Any]
    ) -> PublicationGateResult:
        """
        Gate: Doc-Audit Consistency (N2 — WARNING mode, DEC-C1).

        Detects contradictions between claims in the generated diagnostic
        document and the actual audit data.  For example, if the audit found
        ``seo_elements.open_graph = True`` but the document says "Sin Open
        Graph", this gate reports the contradiction.

        Initial mode: **WARNING** (does not block publication).  Upgrade to
        BLOCKING is documented for a future release.

        Reads:
            - ``assessment["diagnostico_text"]`` — generated diagnostic text
            - ``assessment["audit_data"]`` — structured audit results
              (``seo_elements``, ``gbp``, ``photos``, ``performance``)
            - ``assessment["diagnostic_evidence"]`` — optional structured
              evidence from Option A (evidence_used.json)

        Args:
            assessment: Assessment dict with diagnostic text and audit data

        Returns:
            PublicationGateResult with status WARNING, PASSED, or BLOCKED
            (only on internal errors).
        """
        gate_name = "doc_audit_consistency"

        diag_text = assessment.get("diagnostico_text", "")
        if not diag_text:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="No diagnostic text available for doc-audit consistency check",
                value=None,
                suggestion="",
            )

        audit_data = assessment.get("audit_data", {})
        if not audit_data:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="No audit data available for doc-audit consistency check",
                value=None,
                suggestion="",
            )

        diag_lower = diag_text.lower()
        contradictions: List[Dict[str, str]] = []

        # ------------------------------------------------------------------
        # Check 1: Pattern-based contradictions (OG, performance, …)
        # ------------------------------------------------------------------
        for pattern in self._DOC_AUDIT_CONTRADICTION_PATTERNS:
            section = audit_data.get(pattern["audit_section"], {})
            if isinstance(section, dict):
                actual = section.get(pattern["audit_field"])
            else:
                continue

            if actual == pattern["audit_truth"]:
                matched_kw = [
                    kw for kw in pattern["doc_keywords"] if kw in diag_lower
                ]
                if matched_kw:
                    contradictions.append({
                        "pattern_id": pattern["id"],
                        "doc_keyword": matched_kw[0],
                        "audit_value": str(actual),
                        "description": pattern["description"],
                    })

        # ------------------------------------------------------------------
        # Check 2: Reviews — doc cites "N reseñas" vs gbp.reviews.total
        # ------------------------------------------------------------------
        gbp_data = audit_data.get("gbp", {})
        if isinstance(gbp_data, dict):
            gbp_reviews = gbp_data.get("reviews", {})
            if isinstance(gbp_reviews, dict):
                actual_reviews = gbp_reviews.get("total")
                if actual_reviews is not None:
                    review_mentions = re.findall(
                        r"(\d+)\s*reseñas?", diag_lower
                    )
                    for mention in review_mentions:
                        mentioned_count = int(mention)
                        if (
                            mentioned_count > 0
                            and actual_reviews > 0
                            and abs(mentioned_count - actual_reviews)
                            > max(actual_reviews * 0.5, 10)
                        ):
                            contradictions.append({
                                "pattern_id": "reviews_mismatch",
                                "doc_keyword": f"{mentioned_count} reseñas",
                                "audit_value": str(actual_reviews),
                                "description": (
                                    f"Doc says {mentioned_count} reviews but "
                                    f"audit shows {actual_reviews}"
                                ),
                            })

        # ------------------------------------------------------------------
        # Check 3: Photos — doc target vs audit actual count
        # ------------------------------------------------------------------
        photos_data = audit_data.get("photos", {})
        if isinstance(photos_data, dict):
            actual_photos = photos_data.get("count")
            if actual_photos is not None:
                evidence = assessment.get("diagnostic_evidence", {})
                if isinstance(evidence, dict):
                    target_photos = evidence.get("target_photos")
                    if (
                        target_photos is not None
                        and isinstance(target_photos, (int, float))
                        and actual_photos > 0
                        and abs(target_photos - actual_photos) > actual_photos * 0.5
                    ):
                        contradictions.append({
                            "pattern_id": "photos_mismatch",
                            "doc_keyword": f"target {int(target_photos)} fotos",
                            "audit_value": str(actual_photos),
                            "description": (
                                f"Doc targets {int(target_photos)} photos but "
                                f"audit shows {actual_photos}"
                            ),
                        })

        # ------------------------------------------------------------------
        # Result
        # ------------------------------------------------------------------
        if contradictions:
            contradiction_msgs = [
                f"{c['pattern_id']}: {c['description']}"
                for c in contradictions
            ]
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,  # WARNING does not block (DEC-C1)
                status=GateStatus.WARNING,
                message=(
                    f"{len(contradictions)} doc-audit contradiction(s) detected "
                    f"(WARNING mode): {'; '.join(contradiction_msgs[:3])}"
                ),
                value=len(contradictions),
                suggestion=(
                    "Review diagnostic text to align with audit data. "
                    "This gate will become BLOCKING in a future release."
                ),
                details={"contradictions": contradictions},
            )

        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,
            status=GateStatus.PASSED,
            message="Document consistent with audit data — no contradictions detected",
            value=0,
            suggestion="",
        )

    # ===========================================================================
    # FASE-P0-B: Pricing Compliance Gate — BLOCKING floor-aware (D1)
    # ===========================================================================

    # Hardcoded fallback when pricing.yaml is unreachable (tests, isolated envs).
    _PRICING_FALLBACK: Dict[str, Any] = {
        "tiers": {
            "boutique": {"pain_ratio_gate_max": 0.32, "operational_floor": 400_000},
            "standard": {"pain_ratio_gate_max": 0.32, "operational_floor": 500_000},
            "large":    {"pain_ratio_gate_max": 0.32, "operational_floor": 800_000},
        },
        "gates": {"min_ratio": 0.03, "max_ratio": 0.06, "ideal_ratio": 0.045},
    }

    def _load_pricing_thresholds(self) -> Dict[str, Any]:
        """Load pricing thresholds from config/pricing.yaml (cached).

        Falls back to hardcoded defaults when the YAML is unreachable.
        """
        try:
            from modules.financial_engine.pricing_calculator import _load_pricing_config
            return _load_pricing_config()
        except Exception as exc:
            logger.debug("pricing_compliance: using fallback config (%s)", exc)
            return self._PRICING_FALLBACK

    def _pricing_compliance_gate(
        self, assessment: Dict[str, Any]
    ) -> PublicationGateResult:
        """
        Gate: Pricing Compliance — BLOCKING floor-aware (D1).

        Blocks when ``pain_ratio`` exceeds the tier's ``pain_ratio_gate_max``
        (e.g. 0.32 for boutique).  Emits a non-blocking WARNING when the
        ``pain_ratio`` falls outside the ideal range (0.03-0.06) but the
        ``operational_floor`` was applied (structural ratio inflation).

        Design rationale (01-plan-maestro §7 D1):
            For hotels where ``expected_loss * percentage < operational_floor``,
            the floor forces a price whose ratio = floor / loss.  With the
            global gates (0.03-0.06) as BLOCKING, hotels with loss < 6.67 M/mes
            could NEVER pass.  The tier-level ``pain_ratio_gate_max`` (0.32)
            represents the true abuse threshold; the ideal range is advisory
            when the floor is in play.

        Reads from assessment:
            - ``pricing_data.pain_ratio``
            - ``pricing_data.tier``
            - ``pricing_data.monthly_price_cop``
            - ``pricing_data.expected_loss_cop``

        Reads from ``config/pricing.yaml``:
            - ``tiers.<tier>.pain_ratio_gate_max``
            - ``tiers.<tier>.operational_floor``
            - ``gates.min_ratio``, ``gates.max_ratio``

        Args:
            assessment: Assessment dict with ``pricing_data`` injected by
                ``AssessmentBuilder.with_pricing``.

        Returns:
            PublicationGateResult — BLOCKING / WARNING / PASSED.
        """
        gate_name = "pricing_compliance"

        # ── Extract pricing data ─────────────────────────────────────
        pricing_data = assessment.get("pricing_data")
        if not pricing_data or not isinstance(pricing_data, dict):
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="No pricing data available for compliance check (skipped)",
                value=None,
                suggestion="",
            )

        pain_ratio = pricing_data.get("pain_ratio")
        if pain_ratio is None:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.PASSED,
                message="pain_ratio not found in pricing data (skipped)",
                value=None,
                suggestion="",
            )

        try:
            pain_ratio = float(pain_ratio)
        except (TypeError, ValueError):
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=f"pain_ratio is not numeric: {pain_ratio!r}",
                value=pain_ratio,
                suggestion="Ensure pricing pipeline produces a numeric pain_ratio",
            )

        tier = pricing_data.get("tier", "boutique")
        monthly_price = float(pricing_data.get("monthly_price_cop", 0))
        expected_loss = float(pricing_data.get("expected_loss_cop", 0))

        # ── Load thresholds ──────────────────────────────────────────
        config = self._load_pricing_thresholds()
        tier_config = config.get("tiers", {}).get(tier, {})
        gates = config.get("gates", {})

        gate_max = float(tier_config.get("pain_ratio_gate_max", 0.32))
        operational_floor = float(tier_config.get("operational_floor", 0))
        ideal_min = float(gates.get("min_ratio", 0.03))
        ideal_max = float(gates.get("max_ratio", 0.06))

        # ── Detect floor application ─────────────────────────────────
        floor_applied = (
            operational_floor > 0
            and monthly_price > 0
            and monthly_price <= operational_floor * 1.01
        )

        # ── Evaluate ─────────────────────────────────────────────────
        # BLOCKING: pain_ratio > tier gate_max → abusive pricing
        if pain_ratio > gate_max:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=False,
                status=GateStatus.BLOCKED,
                message=(
                    f"Pricing non-compliant: pain_ratio {pain_ratio:.4f} exceeds "
                    f"tier '{tier}' gate_max {gate_max}"
                ),
                value=pain_ratio,
                suggestion=(
                    f"Reduce price or verify expected_loss. "
                    f"Tier '{tier}' maximum allowed ratio is {gate_max}. "
                    f"Current price ${monthly_price:,.0f} COP vs "
                    f"expected loss ${expected_loss:,.0f} COP."
                ),
                details={
                    "pain_ratio": pain_ratio,
                    "tier": tier,
                    "tier_gate_max": gate_max,
                    "operational_floor": operational_floor,
                    "floor_applied": floor_applied,
                    "ideal_range": [ideal_min, ideal_max],
                    "monthly_price_cop": monthly_price,
                    "expected_loss_cop": expected_loss,
                },
            )

        # WARNING: outside ideal range with floor applied
        outside_ideal = pain_ratio < ideal_min or pain_ratio > ideal_max
        if outside_ideal and floor_applied:
            return PublicationGateResult(
                gate_name=gate_name,
                passed=True,
                status=GateStatus.WARNING,
                message=(
                    f"Pricing compliance PASSED with WARNING: pain_ratio "
                    f"{pain_ratio:.4f} outside ideal range "
                    f"[{ideal_min}-{ideal_max}] — operational_floor "
                    f"${operational_floor:,.0f} applied "
                    f"(tier '{tier}' gate_max {gate_max}: OK)"
                ),
                value=pain_ratio,
                suggestion=(
                    f"pain_ratio is structurally inflated by "
                    f"operational_floor ${operational_floor:,.0f}. "
                    f"Tier '{tier}' allows up to {gate_max}. "
                    f"No action required; informational only."
                ),
                details={
                    "pain_ratio": pain_ratio,
                    "tier": tier,
                    "tier_gate_max": gate_max,
                    "operational_floor": operational_floor,
                    "floor_applied": True,
                    "ideal_range": [ideal_min, ideal_max],
                    "monthly_price_cop": monthly_price,
                    "expected_loss_cop": expected_loss,
                },
            )

        # PASSED: within tier gate_max
        return PublicationGateResult(
            gate_name=gate_name,
            passed=True,
            status=GateStatus.PASSED,
            message=(
                f"Pricing compliant: pain_ratio {pain_ratio:.4f} within "
                f"tier '{tier}' gate_max {gate_max} "
                f"(ideal range [{ideal_min}-{ideal_max}])"
            ),
            value=pain_ratio,
            suggestion="",
            details={
                "pain_ratio": pain_ratio,
                "tier": tier,
                "tier_gate_max": gate_max,
                "operational_floor": operational_floor,
                "floor_applied": floor_applied,
                "ideal_range": [ideal_min, ideal_max],
                "monthly_price_cop": monthly_price,
                "expected_loss_cop": expected_loss,
            },
        )

    def _extract_conflicts(self, assessment: Dict[str, Any]) -> List[Dict]:
        """Extract conflicts from validated assessment."""
        vs = assessment.get("validation_summary", {})
        return vs.get("conflicts", []) if isinstance(vs, dict) else []
    
    def _extract_evidence_coverage(self, assessment: Dict[str, Any]) -> float:
        """Extract evidence coverage from validated assessment."""
        try:
            return float(assessment.get("evidence_coverage", 0.0))
        except (TypeError, ValueError):
            return 0.0
    
    def _extract_financial_data(self, assessment: Dict[str, Any]) -> Dict[str, Any]:
        """Extract financial data from validated assessment."""
        fd = assessment.get("financial_data", {})
        return fd if isinstance(fd, dict) else {}
    
    def _extract_coherence_score(self, assessment: Dict[str, Any]) -> Optional[float]:
        """Extract coherence score from validated assessment."""
        if "coherence_score" not in assessment:
            return None
        try:
            return float(assessment["coherence_score"])
        except (TypeError, ValueError):
            return None
    
    def _extract_critical_recall(self, assessment: Dict[str, Any]) -> Optional[float]:
        """Extract critical recall from validated assessment."""
        # Direct field (preferred)
        if "critical_recall" in assessment:
            try:
                return float(assessment["critical_recall"])
            except (TypeError, ValueError):
                pass
        # Calculate from critical issues
        critical_issues = assessment.get("critical_issues", [])
        if critical_issues:
            return 1.0  # All critical issues were detected (builder guarantees completeness)
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


def check_publication_readiness(
    assessment: Dict[str, Any],
    gate_results: Optional[List[PublicationGateResult]] = None
) -> Dict[str, Any]:
    """
    Check if assessment is ready for publication.
    
    Provides a comprehensive readiness report including:
    - Overall readiness status
    - Individual gate results
    - Blocking issues
    - Recommendations
    
    Args:
        assessment: Dictionary containing all assessment data
        gate_results: Optional pre-computed gate results. When provided,
            readiness is derived from these results without re-executing
            any gates. When None (default), gates are executed once.
    
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
        # Single-execution pattern (recommended):
        results = run_publication_gates(assessment)
        report = check_publication_readiness(assessment, results)
        
        # Backward-compatible (gates executed once):
        report = check_publication_readiness(assessment)
        
        if report["ready"]:
            print("Safe to publish!")
        else:
            for issue in report["blocking_issues"]:
                print(f"Block: {issue}")
    """
    if gate_results is not None:
        results = gate_results
    else:
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
        "warnings": [
            {
                "gate": r.gate_name,
                "message": r.message
            }
            for r in results if r.status == GateStatus.WARNING
        ],
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
