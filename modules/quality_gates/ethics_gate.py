"""Ethics Gate - Validates ethical integrity of commercial proposals.

This gate ensures that proposals have viable returns and are not
financially exploitative.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from enum import Enum


class EthicsStatus(Enum):
    """Status of ethics validation."""
    PASSED = "passed"
    FAILED = "failed"
    WARNING = "warning"


@dataclass
class EthicsIssue:
    """Single ethics issue detected."""
    issue_type: str
    severity: str
    message: str
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EthicsValidationResult:
    """Result of ethics validation."""
    status: EthicsStatus
    issues: List[EthicsIssue] = field(default_factory=list)
    roi_projected: Optional[float] = None
    pricing_total: Optional[float] = None
    projected_return: Optional[float] = None
    
    @property
    def has_issues(self) -> bool:
        return len(self.issues) > 0
    
    @property
    def is_ethical(self) -> bool:
        return self.status == EthicsStatus.PASSED
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "status": self.status.value,
            "issues": [
                {
                    "issue_type": i.issue_type,
                    "severity": i.severity,
                    "message": i.message,
                    "details": i.details
                }
                for i in self.issues
            ],
            "roi_projected": self.roi_projected,
            "pricing_total": self.pricing_total,
            "projected_return": self.projected_return
        }


class EthicsGate:
    """Gate that validates ethical integrity of proposals.
    
    This gate ensures:
    1. ROI is not negative (no exploitative proposals)
    2. If there's pricing, there's a viable return path
    3. Not all scenarios show $0 returns
    """
    
    MIN_ACCEPTABLE_ROI = -0.10
    
    def __init__(self):
        pass
    
    def validate(self, financial_data: Dict[str, Any]) -> EthicsValidationResult:
        """Validate ethical integrity of the proposal.
        
        Args:
            financial_data: Financial data including scenarios, pricing, and returns
            
        Returns:
            EthicsValidationResult with status and issues
        """
        issues = []
        
        scenarios = financial_data.get("scenarios", [])
        
        pricing_activation = financial_data.get("pricing_activation", 0)
        pricing_monthly = financial_data.get("pricing_monthly", 0)
        pricing_total = pricing_activation + (pricing_monthly * 12)
        
        occupancy_rate = financial_data.get("occupancy_rate")
        direct_channel_percentage = financial_data.get("direct_channel_percentage")
        adr_cop = financial_data.get("adr_cop")
        
        has_defaults = False
        if occupancy_rate == 0 or direct_channel_percentage == 0 or adr_cop == 0:
            has_defaults = True
            issues.append(EthicsIssue(
                issue_type="default_financial_data",
                severity="error",  # Changed from warning to error to block
                message="Financial data contains default values (0), cannot validate ethical ROI",
                details={
                    "occupancy_rate": occupancy_rate,
                    "direct_channel_percentage": direct_channel_percentage,
                    "adr_cop": adr_cop
                }
            ))
        
        roi_projected = None
        projected_return = None
        
        if scenarios:
            conservative = next((s for s in scenarios if s.get("scenario_type", "").lower() == "conservador"), None)
            if conservative:
                projected_return = conservative.get("projected_return", 0) or conservative.get("net_benefit", 0)
                
                if pricing_total > 0 and projected_return is not None:
                    roi_projected = (projected_return - pricing_total) / pricing_total if pricing_total > 0 else None
        
        has_zero_returns = False
        has_negative_returns = False
        has_positive_returns = False
        
        for scenario in scenarios:
            ret = scenario.get("projected_return", 0) or scenario.get("net_benefit", 0)
            if ret == 0:
                has_zero_returns = True
            elif ret < 0:
                has_negative_returns = True
            elif ret > 0:
                has_positive_returns = True
        
        if pricing_total > 0:
            if projected_return is not None and projected_return <= 0:
                issues.append(EthicsIssue(
                    issue_type="no_viable_return",
                    severity="error",
                    message=f"Pricing (${pricing_total:,.0f}) but no positive projected return",
                    details={
                        "pricing_total": pricing_total,
                        "projected_return": projected_return,
                        "roi_projected": roi_projected
                    }
                ))
                
            if not has_positive_returns and has_zero_returns:
                issues.append(EthicsIssue(
                    issue_type="all_scenarios_zero_or_negative",
                    severity="warning",
                    message="All scenarios show zero or negative returns",
                    details={
                        "has_zero_returns": has_zero_returns,
                        "has_negative_returns": has_negative_returns,
                        "has_positive_returns": has_positive_returns
                    }
                ))
        
        if roi_projected is not None and roi_projected < self.MIN_ACCEPTABLE_ROI:
            issues.append(EthicsIssue(
                issue_type="exploitative_roi",
                severity="error",
                message=f"ROI ({roi_projected*100:.1f}%) is too negative - proposal is exploitative",
                details={
                    "roi_projected": roi_projected,
                    "threshold": self.MIN_ACCEPTABLE_ROI
                }
            ))
        
        if issues:
            has_errors = any(i.severity == "error" for i in issues)
            status = EthicsStatus.FAILED if has_errors else EthicsStatus.WARNING
        else:
            status = EthicsStatus.PASSED
        
        return EthicsValidationResult(
            status=status,
            issues=issues,
            roi_projected=roi_projected,
            pricing_total=pricing_total,
            projected_return=projected_return
        )
    
    def validate_from_assessment(self, assessment: Dict[str, Any]) -> EthicsValidationResult:
        """Validate ethics from assessment structure.
        
        Args:
            assessment: Full assessment dictionary
            
        Returns:
            EthicsValidationResult
        """
        financial_data = assessment.get("financial_data", {})
        
        if not financial_data:
            financial_data = assessment
        
        scenarios = []
        
        if "scenarios" in financial_data:
            scenarios = financial_data["scenarios"]
        elif "financial_scenarios" in assessment:
            scenarios = assessment.get("financial_scenarios", [])
        
        pricing = financial_data.get("pricing", {})
        if isinstance(pricing, dict):
            pricing_activation = pricing.get("activation", 0) or pricing.get("setup_fee", 0)
            pricing_monthly = pricing.get("monthly", 0) or pricing.get("recurring", 0)
        else:
            pricing_activation = 0
            pricing_monthly = 0
        
        occupancy_rate = financial_data.get("occupancy_rate", financial_data.get("occupancy"))
        direct_channel_percentage = financial_data.get("direct_channel_percentage", financial_data.get("direct_channel"))
        adr_cop = financial_data.get("adr_cop", financial_data.get("adr"))
        
        return self.validate({
            "scenarios": scenarios,
            "pricing_activation": pricing_activation,
            "pricing_monthly": pricing_monthly,
            "occupancy_rate": occupancy_rate,
            "direct_channel_percentage": direct_channel_percentage,
            "adr_cop": adr_cop
        })


def run_ethics_gate(assessment: Dict[str, Any]) -> EthicsValidationResult:
    """Convenience function to run ethics gate.
    
    Args:
        assessment: Assessment dictionary
        
    Returns:
        EthicsValidationResult
    """
    gate = EthicsGate()
    return gate.validate_from_assessment(assessment)
