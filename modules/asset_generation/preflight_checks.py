"""Quality gates before generating any asset."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from enum import Enum

from ..data_validation import ConfidenceLevel, DataPoint
from .asset_catalog import ASSET_CATALOG, AssetStatus

# B1: Import BenchmarkCrossValidator for ADR validation
from ..providers.benchmark_cross_validator import BenchmarkCrossValidator


class PreflightStatus(Enum):
    """Status of a preflight check."""
    PASSED = "passed"
    WARNING = "warning"
    BLOCKED = "blocked"


@dataclass
class PreflightCheck:
    """Single preflight check result."""
    check_name: str
    field_name: str
    required_confidence: float  # 0.0 - 1.0
    status: PreflightStatus
    message: str
    can_generate: bool
    fallback_action: Optional[str] = None


@dataclass
class PreflightReport:
    """Complete preflight report for an asset."""
    asset_type: str
    overall_status: PreflightStatus
    checks: List[PreflightCheck]
    can_proceed: bool
    warnings: List[str] = field(default_factory=list)
    blocking_issues: List[str] = field(default_factory=list)


# NEW HOTEL THRESHOLDS (B2)
# Hotels with 0-10 reviews, 0 photos, or place_found=false are considered "new"
NEW_HOTEL_THRESHOLDS = {
    "whatsapp_button": 0.3,  # Reduced from 0.7
    "faq_page": 0.4,         # Reduced from 0.5
}

# Threshold to consider a hotel as "new"
NEW_HOTEL_MAX_REVIEWS = 10
NEW_HOTEL_MAX_PHOTOS = 5


class PreflightChecker:
    """Quality gates for asset generation."""

    @property
    def ASSET_REQUIREMENTS(self) -> dict:
        """
        Derive asset requirements from ASSET_CATALOG.
        Includes IMPLEMENTED and MANUAL_ONLY assets (both can generate with fallback).
        
        Returns:
            Dict mapping asset_type to requirements dict
        """
        return {
            k: {
                "required_confidence": v.required_confidence,
                "required_field": v.required_field,
                "block_on_failure": v.block_on_failure,
                "fallback": v.fallback
            }
            for k, v in ASSET_CATALOG.items()
            if v.status in (AssetStatus.IMPLEMENTED, AssetStatus.MANUAL_ONLY)
        }

    def __init__(self):
        """Initialize the preflight checker."""
        pass

    def is_new_hotel(self, hotel_context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Determine if a hotel is "new" based on context.
        
        A hotel is considered new if:
        - It has 0-10 reviews
        - It has 0-5 photos
        - place_found is false
        
        Args:
            hotel_context: Dictionary with hotel metadata (reviews, photos, place_found)
            
        Returns:
            True if hotel is new, False otherwise
        """
        if not hotel_context:
            return False
            
        reviews = hotel_context.get("reviews", 999)  # Default to established if not specified
        photos = hotel_context.get("photos", 999)
        place_found = hotel_context.get("place_found", True)
        
        return (
            reviews <= NEW_HOTEL_MAX_REVIEWS or
            photos <= NEW_HOTEL_MAX_PHOTOS or
            not place_found
        )

    def get_effective_threshold(
        self, 
        asset_type: str, 
        is_new_hotel: bool
    ) -> float:
        """
        Get the effective confidence threshold for an asset type.
        
        For new hotels, lower thresholds are used to allow generation
        with less data quality.
        
        Args:
            asset_type: Type of asset
            is_new_hotel: Whether the hotel is new
            
        Returns:
            Effective confidence threshold (0.0 - 1.0)
        """
        base_threshold = self.ASSET_REQUIREMENTS.get(asset_type, {}).get(
            "required_confidence", 0.5
        )
        
        if is_new_hotel and asset_type in NEW_HOTEL_THRESHOLDS:
            return NEW_HOTEL_THRESHOLDS[asset_type]
        
        return base_threshold

    def check_asset(self, asset_type: str, validated_data: Dict[str, DataPoint], 
                    hotel_context: Optional[Dict[str, Any]] = None) -> PreflightReport:
        """Check if asset can be generated based on data quality.

        Args:
            asset_type: Type of asset to generate
            validated_data: Dictionary of validated data points

        Returns:
            PreflightReport with status and recommendations
        """
        if asset_type not in self.ASSET_REQUIREMENTS:
            return PreflightReport(
                asset_type=asset_type,
                overall_status=PreflightStatus.BLOCKED,
                checks=[],
                can_proceed=False,
                blocking_issues=[f"Unknown asset type: {asset_type}"],
                warnings=[]
            )

        requirements = self.ASSET_REQUIREMENTS[asset_type]
        required_field = requirements["required_field"]
        
        # B2: Check if hotel is "new" to use differentiated thresholds
        hotel_is_new = self.is_new_hotel(hotel_context)
        required_confidence = self.get_effective_threshold(asset_type, hotel_is_new)
        
        block_on_failure = requirements["block_on_failure"]
        fallback = requirements.get("fallback")

        checks = []
        warnings = []
        blocking_issues = []
        can_proceed = True

        if required_field not in validated_data:
            if block_on_failure:
                check = PreflightCheck(
                    check_name=f"{required_field}_exists",
                    field_name=required_field,
                    required_confidence=required_confidence,
                    status=PreflightStatus.BLOCKED,
                    message=f"Required field '{required_field}' not found in validated data",
                    can_generate=False,
                    fallback_action=None
                )
                checks.append(check)
                blocking_issues.append(f"Missing field: {required_field}")
                can_proceed = False
            else:
                # CONVERTIR A WARNING PARA FALLBACK
                check = PreflightCheck(
                    check_name=f"{required_field}_exists",
                    field_name=required_field,
                    required_confidence=required_confidence,
                    status=PreflightStatus.WARNING,
                    message=f"Using fallback: Required field '{required_field}' not found",
                    can_generate=True,
                    fallback_action=fallback
                )
                check.fallback_action = fallback
                checks.append(check)
                warnings.append(f"Missing field {required_field}, using fallback: {fallback}")
                can_proceed = True
        else:
            data_point = validated_data[required_field]
            check = self._evaluate_check(
                required_field,
                data_point,
                required_confidence
            )
            check.fallback_action = fallback if not block_on_failure and check.status != PreflightStatus.PASSED else None
            checks.append(check)

            if check.status == PreflightStatus.BLOCKED:
                if block_on_failure:
                    can_proceed = False
                    blocking_issues.append(f"Low confidence in {required_field}: {check.message}")
                else:
                    # CONVERTIR A WARNING PARA FALLBACK
                    check.status = PreflightStatus.WARNING
                    check.message = f"Using fallback: {check.message}"
                    check.can_generate = True
                    warnings.append(check.message)
                    can_proceed = True  # IMPORTANTE
            elif check.status == PreflightStatus.WARNING:
                warnings.append(f"Suboptimal confidence in {required_field}: {check.message}")

        overall_status = PreflightStatus.PASSED
        for check in checks:
            if check.status == PreflightStatus.BLOCKED:
                overall_status = PreflightStatus.BLOCKED
                break
            elif check.status == PreflightStatus.WARNING:
                overall_status = PreflightStatus.WARNING

        return PreflightReport(
            asset_type=asset_type,
            overall_status=overall_status,
            checks=checks,
            can_proceed=can_proceed,
            warnings=warnings,
            blocking_issues=blocking_issues
        )

    def _evaluate_check(self, field_name: str, data_point: DataPoint, required_confidence: float) -> PreflightCheck:
        """Evaluate a single data point against confidence requirements.

        Args:
            field_name: Name of the field being checked
            data_point: The data point to evaluate
            required_confidence: Minimum required confidence level (0.0 - 1.0)

        Returns:
            PreflightCheck with evaluation results
        """
        from ..data_validation.confidence_taxonomy import ConfidenceLevel
        
        # Convert ConfidenceLevel enum to numeric score
        confidence_level = getattr(data_point, 'confidence', ConfidenceLevel.UNKNOWN)
        if isinstance(confidence_level, ConfidenceLevel):
            confidence_map = {
                ConfidenceLevel.VERIFIED: 1.0,
                ConfidenceLevel.ESTIMATED: 0.7,
                ConfidenceLevel.CONFLICT: 0.3,
                ConfidenceLevel.UNKNOWN: 0.0,
            }
            actual_confidence = confidence_map.get(confidence_level, 0.0)
        else:
            actual_confidence = float(confidence_level) if confidence_level else 0.0
        
        # Also try to get match_percentage for more precise scoring
        match_percentage = getattr(data_point, '_validation_result', None)
        if match_percentage and hasattr(match_percentage, 'match_percentage'):
            match_pct = match_percentage.match_percentage / 100.0
            if match_pct > actual_confidence:
                actual_confidence = match_pct
        
        value = getattr(data_point, 'value', None)
        is_verified = getattr(data_point, 'is_verified', False)

        if actual_confidence >= required_confidence:
            return PreflightCheck(
                check_name=f"{field_name}_confidence",
                field_name=field_name,
                required_confidence=required_confidence,
                status=PreflightStatus.PASSED,
                message=f"Confidence {actual_confidence:.2f} meets requirement ({required_confidence:.2f})",
                can_generate=True
            )
        elif actual_confidence >= 0.5:
            return PreflightCheck(
                check_name=f"{field_name}_confidence",
                field_name=field_name,
                required_confidence=required_confidence,
                status=PreflightStatus.WARNING,
                message=f"Confidence {actual_confidence:.2f} below requirement ({required_confidence:.2f}) but acceptable",
                can_generate=True
            )
        else:
            return PreflightCheck(
                check_name=f"{field_name}_confidence",
                field_name=field_name,
                required_confidence=required_confidence,
                status=PreflightStatus.BLOCKED,
                message=f"Confidence {actual_confidence:.2f} too low (minimum 0.5 required)",
                can_generate=False
            )

    def get_blocking_issues(self, report: PreflightReport) -> List[str]:
        """Extract blocking issues from a report.

        Args:
            report: PreflightReport to analyze

        Returns:
            List of blocking issue descriptions
        """
        return report.blocking_issues.copy()

    def get_warnings(self, report: PreflightReport) -> List[str]:
        """Extract warnings from a report.

        Args:
            report: PreflightReport to analyze

        Returns:
            List of warning descriptions
        """
        return report.warnings.copy()

    def format_report_for_display(self, report: PreflightReport) -> str:
        """Format preflight report as readable text.

        Args:
            report: PreflightReport to format

        Returns:
            Formatted string with status, messages, and recommendations
        """
        status_icons = {
            PreflightStatus.PASSED: "✅",
            PreflightStatus.WARNING: "⚠️",
            PreflightStatus.BLOCKED: "❌"
        }

        lines = [
            f"Preflight Report: {report.asset_type}",
            "=" * 50,
            f"Overall Status: {status_icons.get(report.overall_status, '?')} {report.overall_status.value.upper()}",
            f"Can Proceed: {'Yes' if report.can_proceed else 'No'}",
            "",
            "Checks:",
            "-" * 30
        ]

        for check in report.checks:
            icon = status_icons.get(check.status, "?")
            lines.append(f"  {icon} {check.check_name}")
            lines.append(f"     Field: {check.field_name}")
            lines.append(f"     Required Confidence: {check.required_confidence:.2f}")
            lines.append(f"     Status: {check.status.value}")
            lines.append(f"     Message: {check.message}")
            lines.append(f"     Can Generate: {'Yes' if check.can_generate else 'No'}")
            if check.fallback_action:
                lines.append(f"     Fallback: {check.fallback_action}")
            lines.append("")

        if report.warnings:
            lines.append("Warnings:")
            lines.append("-" * 30)
            for warning in report.warnings:
                lines.append(f"  ⚠️  {warning}")
            lines.append("")

        if report.blocking_issues:
            lines.append("Blocking Issues:")
            lines.append("-" * 30)
            for issue in report.blocking_issues:
                lines.append(f"  ❌  {issue}")
            lines.append("")

        if report.can_proceed and report.overall_status != PreflightStatus.PASSED:
            lines.append("Recommendations:")
            lines.append("-" * 30)
            lines.append("  Data quality issues detected but asset can be generated.")
            lines.append("  Consider reviewing data sources for better confidence.")

        return "\n".join(lines)

    def get_fallback_action(self, asset_type: str, check: PreflightCheck) -> Optional[str]:
        """Get fallback action for a failed check.

        Args:
            asset_type: Type of asset being generated
            check: The failed preflight check

        Returns:
            Fallback action string or None if not available
        """
        if check.status == PreflightStatus.PASSED:
            return None

        if asset_type not in self.ASSET_REQUIREMENTS:
            return None

        requirements = self.ASSET_REQUIREMENTS[asset_type]
        fallback = requirements.get("fallback")

        if fallback and not requirements.get("block_on_failure", False):
            return fallback

        return check.fallback_action

    def validate_adr_against_benchmark(
        self,
        actual_adr: float,
        hotel_type: str = "standard"
    ) -> Dict[str, Any]:
        """
        Validate ADR against benchmark ranges.

        B1: Integration of BenchmarkCrossValidator into PreflightChecker.

        Args:
            actual_adr: Actual ADR value
            hotel_type: Type of hotel for benchmark comparison

        Returns:
            Dictionary with deviation validation results
        """
        validator = BenchmarkCrossValidator()
        min_adr, max_adr = validator.get_benchmark_range_for_type(hotel_type)
        benchmark_adr = (min_adr + max_adr) / 2

        deviation = validator.validate_adr_deviation(actual_adr, benchmark_adr, hotel_type)

        return {
            "actual_adr": actual_adr,
            "benchmark_adr": benchmark_adr,
            "min_adr": min_adr,
            "max_adr": max_adr,
            "deviation_percentage": deviation.deviation_percentage,
            "severity": deviation.severity,
            "message": deviation.message,
            "can_proceed": deviation.severity != "error"
        }

    def check_asset_with_benchmark(
        self,
        asset_type: str,
        validated_data: Dict[str, DataPoint],
        hotel_context: Optional[Dict[str, Any]] = None
    ) -> PreflightReport:
        """
        Enhanced check_asset that also validates ADR against benchmark.

        B1: Combines preflight check with benchmark cross-validation.

        Args:
            asset_type: Type of asset to generate
            validated_data: Dictionary of validated data points
            hotel_context: Optional context about hotel for benchmark validation

        Returns:
            PreflightReport with benchmark deviation info if applicable
        """
        # Run standard preflight check
        report = self.check_asset(asset_type, validated_data, hotel_context)

        # B1: If hotel_context has adr, validate against benchmark
        if hotel_context and "adr" in hotel_context:
            adr_result = self.validate_adr_against_benchmark(
                hotel_context["adr"],
                hotel_context.get("hotel_type", "standard")
            )

            # Add benchmark deviation info to report warnings
            if adr_result["severity"] != "ok":
                benchmark_warning = (
                    f"Benchmark ADR deviation: {adr_result['deviation_percentage']:.1%} "
                    f"(Actual: ${adr_result['actual_adr']:,.0f} vs "
                    f"Benchmark: ${adr_result['benchmark_adr']:,.0f})"
                )
                if adr_result["severity"] == "error":
                    report.blocking_issues.append(benchmark_warning)
                    report.overall_status = PreflightStatus.BLOCKED
                    report.can_proceed = False
                else:
                    report.warnings.append(benchmark_warning)
                    if report.overall_status == PreflightStatus.PASSED:
                        report.overall_status = PreflightStatus.WARNING

        return report
