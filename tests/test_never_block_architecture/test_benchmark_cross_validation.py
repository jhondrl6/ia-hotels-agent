"""
TDD Gate: Benchmark Cross Validator

Tests for B1: Benchmark Cross Validation
- Warning when deviation > 20%
- Error when deviation > 50%

COMPORTAMIENTO ESPERADO:
- ADR real se valida contra benchmark regional
- Warning cuando desviación > 20%
- Error cuando desviación > 50%
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest


class TestBenchmarkCrossValidatorExists:
    """Verifica que el módulo existe y es importable."""
    
    def test_benchmark_cross_validator_module_exists(self):
        """El módulo debe existir en modules/providers/benchmark_cross_validator.py"""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        assert BenchmarkCrossValidator is not None


class TestADRDeviationValidation:
    """Verifica que la validación de desviación de ADR funciona correctamente."""
    
    def test_adr_within_20_percent_is_ok(self):
        """ADR con desviación <= 20% debe ser 'ok'."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        # Benchmark boutique: $250k avg, ADR real: $260k (4% desviación)
        result = validator.validate_adr_deviation(
            actual_adr=260000,
            benchmark_adr=250000,
            hotel_type="boutique"
        )
        
        assert result.severity == "ok", f"Expected 'ok' but got '{result.severity}'"
        assert result.deviation_percentage <= 0.20, \
            f"Deviation {result.deviation_percentage:.1%} should be <= 20%"

    def test_adr_above_20_percent_is_warning(self):
        """ADR con desviación > 20% y <= 50% debe ser 'warning'."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        # Benchmark boutique: $250k avg, ADR real: $320k (28% desviación)
        result = validator.validate_adr_deviation(
            actual_adr=320000,
            benchmark_adr=250000,
            hotel_type="boutique"
        )
        
        assert result.severity == "warning", f"Expected 'warning' but got '{result.severity}'"
        assert result.deviation_percentage > 0.20, \
            f"Deviation {result.deviation_percentage:.1%} should be > 20%"
        assert result.deviation_percentage <= 0.50, \
            f"Deviation {result.deviation_percentage:.1%} should be <= 50%"

    def test_adr_above_50_percent_is_error(self):
        """ADR con desviación > 50% debe ser 'error'."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        # Benchmark boutique: $250k avg, ADR real: $500k (100% desviación)
        result = validator.validate_adr_deviation(
            actual_adr=500000,
            benchmark_adr=250000,
            hotel_type="boutique"
        )
        
        assert result.severity == "error", f"Expected 'error' but got '{result.severity}'"
        assert result.deviation_percentage > 0.50, \
            f"Deviation {result.deviation_percentage:.1%} should be > 50%"

    def test_negative_adr_returns_error(self):
        """Valores ADR negativos deben retornar error."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        result = validator.validate_adr_deviation(
            actual_adr=-100,
            benchmark_adr=250000
        )
        
        assert result.severity == "error"

    def test_zero_adr_returns_error(self):
        """ADR cero debe retornar error."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        result = validator.validate_adr_deviation(
            actual_adr=0,
            benchmark_adr=250000
        )
        
        assert result.severity == "error"


class TestBenchmarkRangeForHotelType:
    """Verifica que los rangos de benchmark son correctos para cada tipo de hotel."""
    
    def test_boutique_benchmark_range(self):
        """Rango benchmark para boutique: $150k - $350k COP."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        min_adr, max_adr = validator.get_benchmark_range_for_type("boutique")
        
        assert min_adr == 150000, f"Expected min 150000 but got {min_adr}"
        assert max_adr == 350000, f"Expected max 350000 but got {max_adr}"

    def test_standard_benchmark_range(self):
        """Rango benchmark para standard: $80k - $180k COP."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        min_adr, max_adr = validator.get_benchmark_range_for_type("standard")
        
        assert min_adr == 80000, f"Expected min 80000 but got {min_adr}"
        assert max_adr == 180000, f"Expected max 180000 but got {max_adr}"

    def test_luxury_benchmark_range(self):
        """Rango benchmark para luxury: $350k - $800k COP."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        min_adr, max_adr = validator.get_benchmark_range_for_type("luxury")
        
        assert min_adr == 350000, f"Expected min 350000 but got {min_adr}"
        assert max_adr == 800000, f"Expected max 800000 but got {max_adr}"

    def test_unknown_type_defaults_to_standard(self):
        """Tipo desconocido debe usar rango standard."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        min_adr, max_adr = validator.get_benchmark_range_for_type("unknown_type")
        
        assert min_adr == 80000, f"Expected min 80000 but got {min_adr}"
        assert max_adr == 180000, f"Expected max 180000 but got {max_adr}"


class TestParseADRFromString:
    """Verifica que el parsing de strings ADR funciona."""
    
    def test_parse_colombian_format_with_dots(self):
        """Parser debe entender formato colombiano: $280.000 COP."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        result = validator.parse_adr_from_string("$280.000 COP")
        
        assert result == 280000, f"Expected 280000 but got {result}"

    def test_parse_number_without_currency(self):
        """Parser debe funcionar sin símbolo de moneda."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        result = validator.parse_adr_from_string("520000")
        
        assert result == 520000, f"Expected 520000 but got {result}"

    def test_parse_returns_none_for_invalid(self):
        """Parser debe retornar None para strings inválidos."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        result = validator.parse_adr_from_string("invalid")
        
        assert result is None, f"Expected None but got {result}"


class TestFinancialDataValidation:
    """Verifica validación de datos financieros completos."""
    
    def test_validate_financial_scenarios(self):
        """Validar escenarios financieros contra benchmark."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        # Standard benchmark range: $80k - $180k, midpoint ~$130k
        financial_data = {
            "adr_scenarios": {
                "optimistic": {"adr": 140000},  # ~8% from midpoint = ok
                "pessimistic": {"adr": 95000},  # ~27% from midpoint = warning
            }
        }
        
        results = validator.validate_financial_data(financial_data, hotel_type="standard")
        
        assert "optimistic_adr" in results
        assert results["optimistic_adr"].severity == "ok"
        assert results["pessimistic_adr"].severity == "warning"


class TestMetadataDeviation:
    """Verifica que la desviación se añade a metadata."""
    
    def test_metadata_with_benchmark_deviation(self):
        """Metadata debe incluir benchmark_deviation cuando hay ADR."""
        from modules.providers.benchmark_cross_validator import BenchmarkCrossValidator
        
        validator = BenchmarkCrossValidator()
        metadata = {
            "hotel_id": "visperas_001",
            "adr": 400000  # 60% más alto que benchmark boutique
        }
        
        result = validator.check_metadata_deviation(metadata, benchmark_adr=250000)
        
        assert "benchmark_deviation" in result
        assert result["benchmark_deviation"]["severity"] == "error"
        assert result["benchmark_deviation"]["percentage"] > 0.50


class TestConvenienceFunction:
    """Verifica la función de conveniencia validate_price_against_benchmark."""
    
    def test_validate_price_string_warning(self):
        """validate_price_against_benchmark debe retornar warning para desviación > 20%."""
        from modules.providers.benchmark_cross_validator import validate_price_against_benchmark
        
        result = validate_price_against_benchmark("$320.000 COP", hotel_type="boutique")
        
        # $320k vs benchmark promedio $250k = 28% desviación = warning
        assert result.severity == "warning"

    def test_validate_price_string_error(self):
        """validate_price_against_benchmark debe retornar error para desviación > 50%."""
        from modules.providers.benchmark_cross_validator import validate_price_against_benchmark
        
        result = validate_price_against_benchmark("$500.000 COP", hotel_type="boutique")
        
        # $500k vs benchmark promedio $250k = 100% desviación = error
        assert result.severity == "error"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
