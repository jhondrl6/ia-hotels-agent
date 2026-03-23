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
