"""
Benchmark Cross Validator - NEVER_BLOCK Architecture

Valida que los datos reales no se desvíen significativamente del benchmark.
Alertar cuando:
- Desviación > 20%: Warning
- Desviación > 50%: Error

Integración con preflight_checks para incluir validación de ADR.
"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, Tuple
import re


@dataclass
class BenchmarkDeviation:
    """Result from benchmark deviation check."""
    actual_value: float
    benchmark_value: float
    deviation_percentage: float
    severity: str  # "ok", "warning", "error"
    message: str


class BenchmarkCrossValidator:
    """
    Valida que los datos reales no se desvíen significativamente del benchmark.
    
    Principios:
    - WARNING: Desviación > 20% del benchmark
    - ERROR: Desviación > 50% del benchmark
    - OK: Desviación <= 20%
    """

    # Thresholds for deviation detection
    WARNING_THRESHOLD = 0.20  # 20%
    ERROR_THRESHOLD = 0.50   # 50%

    def __init__(self):
        """Initialize the benchmark cross validator."""
        pass

    def validate_adr_deviation(
        self,
        actual_adr: float,
        benchmark_adr: float,
        hotel_type: str = "standard"
    ) -> BenchmarkDeviation:
        """
        Validate ADR deviation from benchmark.

        Args:
            actual_adr: Real ADR value (e.g., 400000 COP)
            benchmark_adr: Benchmark ADR value (e.g., 250000 COP)
            hotel_type: Type of hotel for context

        Returns:
            BenchmarkDeviation with validation results
        """
        if actual_adr <= 0 or benchmark_adr <= 0:
            return BenchmarkDeviation(
                actual_value=actual_adr,
                benchmark_value=benchmark_adr,
                deviation_percentage=0.0,
                severity="error",
                message="Invalid ADR values: must be positive numbers"
            )

        # Calculate percentage deviation: |actual - benchmark| / benchmark
        deviation = abs(actual_adr - benchmark_adr) / benchmark_adr

        if deviation > self.ERROR_THRESHOLD:
            severity = "error"
            message = (
                f"ADR deviation {deviation:.1%} exceeds 50% threshold. "
                f"Actual: ${actual_adr:,.0f} COP vs Benchmark: ${benchmark_adr:,.0f} COP. "
                f"Verify data accuracy."
            )
        elif deviation > self.WARNING_THRESHOLD:
            severity = "warning"
            message = (
                f"ADR deviation {deviation:.1%} exceeds 20% threshold. "
                f"Actual: ${actual_adr:,.0f} COP vs Benchmark: ${benchmark_adr:,.0f} COP. "
                f"Consider reviewing data sources."
            )
        else:
            severity = "ok"
            message = (
                f"ADR within acceptable range. "
                f"Deviation: {deviation:.1%} (threshold: 20%)"
            )

        return BenchmarkDeviation(
            actual_value=actual_adr,
            benchmark_value=benchmark_adr,
            deviation_percentage=deviation,
            severity=severity,
            message=message
        )

    def get_benchmark_range_for_type(
        self,
        hotel_type: str,
        region: str = "eje_cafetero"
    ) -> Tuple[float, float]:
        """
        Get benchmark ADR range for hotel type.

        Args:
            hotel_type: Type of hotel (boutique, standard, luxury)
            region: Region identifier

        Returns:
            Tuple of (min_adr, max_adr) in COP
        """
        # Benchmark ADR ranges in COP (from benchmark_resolver.py)
        benchmark_ranges = {
            "boutique": (150000, 350000),
            "standard": (80000, 180000),
            "luxury": (350000, 800000),
        }

        return benchmark_ranges.get(
            hotel_type.lower(),
            benchmark_ranges["standard"]
        )

    def validate_financial_data(
        self,
        financial_data: Dict[str, Any],
        hotel_type: str = "standard"
    ) -> Dict[str, BenchmarkDeviation]:
        """
        Validate financial scenario data against benchmark.

        Args:
            financial_data: Dictionary with financial scenarios
            hotel_type: Type of hotel

        Returns:
            Dictionary mapping scenario names to BenchmarkDeviation results
        """
        results = {}
        min_benchmark, max_benchmark = self.get_benchmark_range_for_type(hotel_type)

        # Get ADR from financial data
        adr_scenarios = financial_data.get("adr_scenarios", {})
        
        # Also check optimistic scenario ADR if present
        optimistic_adr = financial_data.get("optimistic_adr") or financial_data.get("adr")
        if optimistic_adr:
            adr_scenarios["optimistic"] = {"adr": optimistic_adr}

        for scenario_name, scenario in adr_scenarios.items():
            if isinstance(scenario, dict) and "adr" in scenario:
                actual_adr = float(scenario["adr"])
                # Use midpoint of benchmark range for comparison
                benchmark_adr = (min_benchmark + max_benchmark) / 2
                
                deviation = self.validate_adr_deviation(
                    actual_adr,
                    benchmark_adr,
                    hotel_type
                )
                results[f"{scenario_name}_adr"] = deviation

        return results

    def parse_adr_from_string(self, adr_string: str) -> Optional[float]:
        """
        Parse ADR value from string like "$280.000 COP" or "$280000".

        Args:
            adr_string: String containing ADR value

        Returns:
            Float value of ADR or None if parsing fails
        """
        if not adr_string:
            return None

        # Remove currency symbols and spaces
        cleaned = re.sub(r'[$\s COP]', '', str(adr_string))
        
        # Handle Colombian format with dots (e.g., "280.000")
        # Remove thousand separators if they're dots and the number is small
        if '.' in cleaned and len(cleaned) > 6:
            # Large number with dot as thousands separator
            cleaned = cleaned.replace('.', '')
        elif '.' in cleaned:
            # Could be decimal separator in small number
            pass
        
        try:
            return float(cleaned)
        except ValueError:
            return None

    def check_metadata_deviation(
        self,
        metadata: Dict[str, Any],
        benchmark_adr: float
    ) -> Dict[str, Any]:
        """
        Add benchmark deviation info to asset metadata.

        Args:
            metadata: Asset metadata dictionary
            benchmark_adr: Benchmark ADR value

        Returns:
            Updated metadata with benchmark_deviation field
        """
        result = metadata.copy()

        # Check if actual ADR is available in metadata
        actual_adr = metadata.get("adr") or metadata.get("price_range")
        
        if actual_adr and isinstance(actual_adr, (int, float)):
            deviation = self.validate_adr_deviation(
                float(actual_adr),
                benchmark_adr
            )
            result["benchmark_deviation"] = {
                "percentage": deviation.deviation_percentage,
                "severity": deviation.severity,
                "actual_value": deviation.actual_value,
                "benchmark_value": deviation.benchmark_value
            }
            if deviation.severity != "ok":
                result["disclaimers"] = result.get("disclaimers", [])
                result["disclaimers"].append(deviation.message)

        return result


def validate_price_against_benchmark(
    actual_price: str,
    hotel_type: str = "standard"
) -> BenchmarkDeviation:
    """
    Convenience function to validate a price string against benchmark.

    Args:
        actual_price: Price string like "$280.000 COP"
        hotel_type: Type of hotel

    Returns:
        BenchmarkDeviation with validation results
    """
    validator = BenchmarkCrossValidator()
    
    # Parse the price
    actual_adr = validator.parse_adr_from_string(actual_price)
    if actual_adr is None:
        return BenchmarkDeviation(
            actual_value=0,
            benchmark_value=0,
            deviation_percentage=0,
            severity="error",
            message=f"Could not parse ADR from: {actual_price}"
        )
    
    # Get benchmark for hotel type
    min_bench, max_bench = validator.get_benchmark_range_for_type(hotel_type)
    benchmark_adr = (min_bench + max_bench) / 2
    
    return validator.validate_adr_deviation(actual_adr, benchmark_adr, hotel_type)
