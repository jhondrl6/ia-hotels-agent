"""
TDD Gate: Disclaimer Generator

Estos tests definen el comportamiento esperado del DisclaimerGenerator.
初期: Todos los tests FALLAN (módulo no existe aún).
Después de implementar: Todos los tests PASAN.

COMPORTAMIENTO ESPERADO:
- Asset con confidence < 0.9 debe tener disclaimer explícito
- Disclaimer incluye: sources usadas, gaps existentes, recommendation
- Asset con confidence >= 0.9 NO necesita disclaimer
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest


class TestDisclaimerGeneratorExists:
    """Verifica que el módulo existe y es importable."""
    
    def test_disclaimer_generator_module_exists(self):
        """El módulo debe existir en modules/providers/disclaimer_generator.py"""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        assert DisclaimerGenerator is not None


class TestDisclaimerGeneratorOutput:
    """Verifica formato y contenido del disclaimer."""
    
    def test_generates_disclaimer_for_low_confidence(self):
        """Asset con confidence 0.5 debe generar disclaimer."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["web_scraping", "benchmark_pereira"],
            gaps=["telephone", "address"]
        )
        
        assert disclaimer is not None, "Disclamer nunca debe ser None"
        assert len(disclaimer) > 0, "Disclaimer no puede estar vacío"
        assert "0.5" in disclaimer or "50%" in disclaimer, \
            "Debe mencionar el confidence score"

    def test_disclaimer_includes_sources(self):
        """Disclaimer debe listar las fuentes utilizadas."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.6,
            sources=["web_scraping", "gbp", "benchmark"],
            gaps=[]
        )
        
        assert "web_scraping" in disclaimer.lower() or "scraping" in disclaimer.lower()
        assert "benchmark" in disclaimer.lower()

    def test_disclaimer_includes_gaps(self):
        """Disclaimer debe listar los gaps (datos faltantes)."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["web"],
            gaps=["telephone", "address", "description"]
        )
        
        assert "telephone" in disclaimer.lower() or "phone" in disclaimer.lower()
        assert "gaps" in disclaimer.lower() or "faltantes" in disclaimer.lower() or \
               "missing" in disclaimer.lower()

    def test_disclaimer_includes_recommendation(self):
        """Disclaimer debe incluir recomendación para mejorar."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["benchmark"],
            gaps=["telephone"]
        )
        
        assert any(word in disclaimer.lower() for word in 
                   ["recomend", "recomendación", "recomendación", "suggest", "improve"]), \
            "Debe tener recomendación"

    def test_no_disclaimer_for_high_confidence(self):
        """Asset con confidence >= 0.9 NO necesita disclaimer."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.95,
            sources=["web", "gbp", "user_input"],
            gaps=[]
        )
        
        assert disclaimer == "" or disclaimer is None, \
            "Alta confianza no necesita disclaimer"


class TestDisclaimerGeneratorThresholds:
    """Verifica los thresholds de confianza."""
    
    def test_threshold_090_no_disclaimer(self):
        """Confidence 0.9 exact no necesita disclaimer."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(confidence=0.9, sources=["web"], gaps=[])
        
        # 0.9 es el umbral, puede tener disclaimer o no
        # Lo importante es que sea mínimo
        assert disclaimer is None or len(disclaimer) < 100

    def test_threshold_089_needs_disclaimer(self):
        """Confidence 0.89 SÍ necesita disclaimer."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(confidence=0.89, sources=["web"], gaps=[])
        
        assert disclaimer is not None
        assert len(disclaimer) > 0

    def test_threshold_070_still_needs_disclaimer(self):
        """Confidence 0.7 necesita disclaimer completo."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.7,
            sources=["web_scraping"],
            gaps=["telephone"]
        )
        
        assert disclaimer is not None
        assert "0.7" in disclaimer or "70%" in disclaimer

    def test_threshold_050_needs_detailed_disclaimer(self):
        """Confidence 0.5 necesita disclaimer detallado."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["benchmark"],
            gaps=["telephone", "address", "description", "amenities"]
        )
        
        assert disclaimer is not None
        # Con múltiples gaps, disclaimer debe ser más detallado
        assert len(disclaimer) > 50


class TestDisclaimerGeneratorFormat:
    """Verifica formato del disclaimer."""
    
    def test_disclaimer_is_markdown_compatible(self):
        """Disclaimer debe poder incluirse en markdown sin romper formato."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["web", "benchmark"],
            gaps=["telephone"]
        )
        
        # No debe tener caracteres que rompan markdown
        assert "```" not in disclaimer, "No debe tener bloques de código"
        assert disclaimer.count("#") < 3, "No debe tener muchos headers"

    def test_disclaimer_is_html_compatible(self):
        """Disclaimer debe poder incluirse en HTML sin problemas."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["web"],
            gaps=["address"]
        )
        
        # No debe cerrar tags sin abrir
        assert "<" not in disclaimer or ">" in disclaimer

    def test_disclaimer_has_consistent_style(self):
        """Disclaimer debe tener estilo consistente."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        d1 = generator.generate(confidence=0.5, sources=["a"], gaps=["x"])
        d2 = generator.generate(confidence=0.6, sources=["b"], gaps=["y"])
        
        # Mismo estilo (no necesariamente mismo contenido)
        # Verificar que ambos empiezan con indicador de confidence
        assert "confianza" in d1.lower() or "confidence" in d1.lower() or \
               "estimado" in d1.lower() or "%" in d1


class TestDisclaimerGeneratorEdgeCases:
    """Casos límite del generador."""
    
    def test_empty_sources_uses_defaults(self):
        """Sources vacías debe usar 'unknown' como default."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=[],  # Vacío
            gaps=["telephone"]
        )
        
        assert disclaimer is not None
        assert "unknown" in disclaimer.lower() or "no disponible" in disclaimer.lower()

    def test_empty_gaps_no_problem(self):
        """Gaps vacíos es válido."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.9,
            sources=["web"],
            gaps=[]  # Sin gaps
        )
        
        # Alta confianza sin gaps = sin disclaimer
        assert disclaimer == "" or disclaimer is None

    def test_very_low_confidence_040(self):
        """Confidence 0.4 muy bajo = disclaimer muy prominente."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.4,
            sources=["benchmark"],
            gaps=["all"]
        )
        
        assert disclaimer is not None
        assert len(disclaimer) > 20
        # Debe enfatizar que es muy bajo
        assert "muy" in disclaimer.lower() or "bajo" in disclaimer.lower() or \
               "low" in disclaimer.lower() or "limited" in disclaimer.lower()

    def test_perfect_confidence_100(self):
        """Confidence 1.0 (100%) = sin disclaimer."""
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=1.0,
            sources=["user_verified"],
            gaps=[]
        )
        
        assert disclaimer == "" or disclaimer is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


# =============================================================================
# FASE 9: Intelligent Disclaimer Generator v2 - TESTS OBLIGATORIOS
# =============================================================================

class TestIntelligentDisclaimerGenerator:
    """
    FASE 9: Tests para IntelligentDisclaimerGenerator.
    
    Criterios:
    - Disclaimer menciona datos específicos faltantes
    - Disclaimer incluye improvement steps
    - Improvement score se calcula correctamente
    """
    
    def test_intelligent_disclaimer_content(self):
        """Disclaimer menciona datos específicos (no genérico)."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        disclaimer = generator.generate(
            asset_type="hotel_schema",
            confidence=0.3,
            missing_data=["gbp_reviews", "photos", "ratings"],
            benchmark_used="Pereira boutique avg benchmark",
            improvement_steps=[
                "Completar perfil de Google Business Profile",
                "Agregar 10+ fotos de alta calidad"
            ]
        )
        
        # Debe mencionar datos específicos (Google Business Profile traduce gbp_reviews)
        assert "google business" in disclaimer.lower() or "reviews" in disclaimer.lower() or "reseñas" in disclaimer.lower()
        assert "fotos" in disclaimer.lower() or "photos" in disclaimer.lower()
        # NO debe ser genérico
        assert "datos estimados" not in disclaimer.lower()
    
    def test_disclaimer_includes_benchmark(self):
        """Disclaimer incluye el benchmark usado."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        disclaimer = generator.generate(
            asset_type="description",
            confidence=0.25,
            missing_data=["gbp_reviews"],
            benchmark_used="Medellín hotels average",
            improvement_steps=["Solicitar 5+ reseñas"]
        )
        
        assert "benchmark" in disclaimer.lower() or "medellín" in disclaimer.lower()
    
    def test_disclaimer_includes_steps(self):
        """Disclaimer incluye numbered improvement steps."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        disclaimer = generator.generate(
            asset_type="hotel_schema",
            confidence=0.3,
            missing_data=["gbp_reviews", "photos"],
            benchmark_used="Regional benchmark",
            improvement_steps=[
                "Agregar 10+ fotos a Google Business Profile",
                "Solicitar 5+ reseñas a clientes reales",
                "Verificar información de contacto"
            ]
        )
        
        # Debe tener pasos numerados
        assert "1." in disclaimer
        assert "2." in disclaimer
        assert "3." in disclaimer
        # Debe mencionar qué hacer para mejorar
        assert "mejora" in disclaimer.lower() or "mejorar" in disclaimer.lower()
    
    def test_improvement_score_basic(self):
        """Improvement score se calcula correctamente."""
        from modules.providers.disclaimer_generator import calculate_improvement_score
        
        # Caso del plan: 0.3 -> 0.85 = 0.55
        score = calculate_improvement_score(0.3, 0.85)
        assert abs(score - 0.55) < 0.01, f"Expected 0.55, got {score}"
    
    def test_improvement_score_capped_at_one(self):
        """Improvement score capped at 1.0."""
        from modules.providers.disclaimer_generator import calculate_improvement_score
        
        # Muy alto target (más de 1.0 de gap)
        score = calculate_improvement_score(0.2, 1.5)
        assert score == 1.0, f"Expected 1.0 (capped), got {score}"
    
    def test_improvement_score_zero_when_target_lower(self):
        """Improvement score es 0 cuando target < current."""
        from modules.providers.disclaimer_generator import calculate_improvement_score
        
        score = calculate_improvement_score(0.8, 0.5)
        assert score == 0.0, f"Expected 0.0, got {score}"
    
    def test_improvement_score_same_values(self):
        """Improvement score es 0 cuando target == current."""
        from modules.providers.disclaimer_generator import calculate_improvement_score
        
        score = calculate_improvement_score(0.7, 0.7)
        assert score == 0.0, f"Expected 0.0, got {score}"
    
    def test_intelligent_disclaimer_includes_expected_confidence(self):
        """Disclaimer incluye confidence esperado después de aplicar fixes."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        disclaimer = generator.generate(
            asset_type="hotel_schema",
            confidence=0.3,
            missing_data=["gbp_reviews"],
            benchmark_used="Regional benchmark",
            improvement_steps=["Solicitar reseñas", "Agregar fotos"]
        )
        
        # Debe mencionar confianza esperada
        assert "CONFIDENCIA ESPERADA" in disclaimer or "después" in disclaimer.lower()
    
    def test_intelligent_disclaimer_confidence_levels(self):
        """Disclaimer adapta emoji/label según nivel de confianza."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        
        # Muy bajo < 0.4
        d1 = generator.generate("schema", 0.3, ["reviews"], "bench", ["step"])
        assert "🚨" in d1 or "MUY BAJA" in d1
        
        # Bajo 0.4-0.6
        d2 = generator.generate("schema", 0.5, ["reviews"], "bench", ["step"])
        assert "⚠️" in d2 or "BAJA" in d2
        
        # Moderado 0.6-0.8
        d3 = generator.generate("schema", 0.7, ["reviews"], "bench", ["step"])
        assert "⚡" in d3 or "MODERADA" in d3
    
    def test_generate_metadata_dict_complete(self):
        """generate_metadata_dict retorna todos los campos requeridos."""
        from modules.providers.disclaimer_generator import IntelligentDisclaimerGenerator
        
        generator = IntelligentDisclaimerGenerator()
        result = generator.generate_metadata_dict(
            asset_type="hotel_schema",
            confidence=0.3,
            missing_data=["gbp_reviews", "photos"],
            benchmark_used="Pereira boutique avg",
            improvement_steps=["Add photos", "Request reviews"]
        )
        
        # Verificar estructura completa
        assert "disclaimer" in result
        assert "missing_data" in result
        assert "benchmark_used" in result
        assert "improvement_steps" in result
        assert "confidence_after_fix" in result
        
        # Verificar valores
        assert result["missing_data"] == ["gbp_reviews", "photos"]
        assert result["benchmark_used"] == "Pereira boutique avg"
        assert result["improvement_steps"] == ["Add photos", "Request reviews"]
        assert isinstance(result["confidence_after_fix"], float)
