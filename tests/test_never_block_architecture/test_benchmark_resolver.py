"""
TDD Gate: Benchmark Resolver

Estos tests definen el comportamiento esperado del BenchmarkResolver.
初期: Todos los tests FALLAN (módulo no existe aún).
Después de implementar: Todos los tests PASAN.

COMPORTAMIENTO ESPERADO:
- Cuando faltan datos del hotel, usar benchmark regional (Pereira/Santa Rosa de Cabal)
- Cuando hay datos reales, NO usar benchmark
- Benchmark tiene confidence menor que datos reales
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest


class TestBenchmarkResolverExists:
    """Verifica que el módulo existe y es importable."""
    
    def test_benchmark_resolver_module_exists(self):
        """El módulo debe existir en modules/providers/benchmark_resolver.py"""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        assert BenchmarkResolver is not None


class TestBenchmarkResolverFillGaps:
    """Verifica que el resolver llena gaps con benchmark regional."""
    
    def test_resolve_missing_city_uses_pereira_benchmark(self):
        """Cuando falta 'city', debe usar Pereira como fallback para eje cafetero."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="addressLocality",
            value=None,  # Falta dato
            context={"region": "eje_cafetero", "country": "CO"}
        )
        
        assert result.value is not None, "Debe devolver un valor, nunca None"
        assert result.value in ["Pereira", "Santa Rosa de Cabal"], \
            f"Debe ser Pereira o Santa Rosa de Cabal, got: {result.value}"
        assert "benchmark" in result.sources, "Fuente debe ser 'benchmark'"
        assert result.confidence < 1.0, "Benchmark debe tener confidence < 1.0"
        assert result.confidence >= 0.5, "Benchmark debe tener confidence >= 0.5"

    def test_resolve_missing_telephone_uses_benchmark_format(self):
        """Cuando falta telephone, debe usar formato +57 XXX para Colombia."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="telephone",
            value=None,
            context={"region": "eje_cafetero", "country": "CO"}
        )
        
        assert result.value is not None
        assert result.value.startswith("+57"), "Teléfono Colombia debe empezar con +57"
        assert "XXX" not in result.value, "No debe contener placeholder XXX"
        assert "benchmark" in result.sources

    def test_resolve_missing_description_uses_benchmark_category(self):
        """Cuando falta description, debe generar descripción basada en benchmark."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="description",
            value=None,
            context={"hotel_type": "boutique", "region": "eje_cafetero"}
        )
        
        assert result.value is not None
        assert len(result.value) > 50, "Descripción debe tener contenido real"
        assert "placeholder" not in result.value.lower()
        assert "benchmark" in result.sources

    def test_resolve_with_real_data_ignores_benchmark(self):
        """Cuando hay datos reales, NO usa benchmark."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="addressLocality",
            value="Santa Rosa de Cabal",  # Dato real
            context={"region": "eje_cafetero"}
        )
        
        assert result.value == "Santa Rosa de Cabal"
        assert "scraping" in result.sources or "user_input" in result.sources
        assert result.confidence >= 0.8, "Datos reales deben tener confidence >= 0.8"

    def test_resolve_empty_string_uses_benchmark(self):
        """Campo vacío (no None) también debe usar benchmark."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="description",
            value="",  # Vacío
            context={"region": "eje_cafetero"}
        )
        
        assert result.value is not None
        assert len(result.value) > 0
        assert "benchmark" in result.sources


class TestBenchmarkResolverConfidence:
    """Verifica que el confidence scoring es correcto."""
    
    def test_benchmark_has_lower_confidence_than_real(self):
        """Benchmark debe tener confidence menor que datos reales."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        
        real_result = resolver.resolve(
            field="city",
            value="Pereira",
            context={"region": "eje_cafetero"}
        )
        
        benchmark_result = resolver.resolve(
            field="city",
            value=None,
            context={"region": "eje_cafetero"}
        )
        
        assert real_result.confidence > benchmark_result.confidence, \
            "Datos reales deben tener más confidence que benchmark"
        assert benchmark_result.confidence < 0.8, "Benchmark debe ser < 0.8"

    def test_cross_referenced_benchmark_has_higher_confidence(self):
        """Benchmark con cross-reference (múltiples fuentes) tiene más confidence."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        
        # Single source benchmark
        single = resolver.resolve(
            field="telephone",
            value=None,
            context={"region": "eje_cafetero"}
        )
        
        # Multi-source benchmark (from different benchmark sources)
        multi = resolver.resolve(
            field="telephone",
            value=None,
            context={"region": "eje_cafetero", "cross_reference": True}
        )
        
        assert multi.confidence >= single.confidence, \
            "Cross-reference debe mejorar confidence"


class TestBenchmarkResolverEdgeCases:
    """Casos límite del resolver."""
    
    def test_resolve_unknown_region_uses_generic_benchmark(self):
        """Región desconocida debe usar benchmark genérico Colombia."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="country",
            value=None,
            context={"region": "unknown"}
        )
        
        assert result.value is not None
        assert result.confidence < 0.7, "Región desconocida = confidence menor"

    def test_resolve_non_hotel_field_returns_none(self):
        """Campos no-hoteléricos no deben tener benchmark."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="random_field",
            value=None,
            context={}
        )
        
        assert result.value is None

    def test_resolve_with_high_quality_context(self):
        """Context con alta calidad debe mejorar benchmark confidence."""
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        resolver = BenchmarkResolver()
        result = resolver.resolve(
            field="priceRange",
            value=None,
            context={
                "region": "eje_cafetero",
                "hotel_category": "boutique",
                "adr_benchmark": 180000  # COP
            }
        )
        
        assert result.value is not None
        assert result.confidence >= 0.6, "Con context bueno, confidence debe ser >= 0.6"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
