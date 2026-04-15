"""
Tests for Price vs Pain Ratio Alignment (Sesión 5 - M-001).

Verifica que:
1. Se usa decimal internamente (0.03-0.06)
2. Se muestra notación x en mensajes (3.0x-6.0x)
3. Coherence pasa cuando pain_ratio está en rango correcto
4. No hay FAIL artificial por desalineación de unidades
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.commercial_documents.coherence_config import (
    PriceValidationRule,
    CoherenceConfig
)
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.commercial_documents.data_structures import (
    DiagnosticDocument,
    ProposalDocument,
    AssetSpec,
    ValidationSummary,
    Scenario,
    ConfidenceLevel
)


class TestPriceValidationRule:
    """Test PriceValidationRule conversion methods."""
    
    def test_from_x_notation_converts_correctly(self):
        """Convierte 3.0x → 0.03 decimal."""
        rule = PriceValidationRule.from_x_notation(
            min_x=3.0,
            max_x=6.0,
            ideal_x=4.5
        )
        
        assert rule.min_ratio == 0.03
        assert rule.max_ratio == 0.06
        assert rule.ideal_ratio == 0.045
    
    def test_to_x_notation_converts_correctly(self):
        """Convierte 0.05 decimal → 5.0x."""
        rule = PriceValidationRule(
            min_ratio=0.03,
            max_ratio=0.06,
            ideal_ratio=0.045
        )
        
        assert rule.to_x_notation(0.03) == 3.0
        assert rule.to_x_notation(0.06) == 6.0
        assert rule.to_x_notation(0.045) == 4.5
        assert rule.to_x_notation(0.05) == 5.0
    
    def test_format_ratio_x_returns_string(self):
        """Formatea ratio como string legible."""
        rule = PriceValidationRule(
            min_ratio=0.03,
            max_ratio=0.06,
            ideal_ratio=0.045
        )
        
        assert rule.format_ratio_x(0.03) == "3.0x"
        assert rule.format_ratio_x(0.05) == "5.0x"
        assert rule.format_ratio_x(0.06) == "6.0x"


class TestCoherenceConfig:
    """Test CoherenceConfig with decimal units."""
    
    def test_default_price_rule_is_decimal(self):
        """Los valores por defecto son decimales, no x."""
        config = CoherenceConfig()
        rule = config.get_price_rule()
        
        # Debe ser decimal (0.03), no x (3.0)
        assert rule.min_ratio == 0.03
        assert rule.max_ratio == 0.06
        assert rule.ideal_ratio == 0.045
    
    def test_validate_price_ratio_uses_x_in_message(self):
        """El mensaje usa notación x para legibilidad."""
        config = CoherenceConfig()
        
        # Price = 150,000, Pain = 3,000,000 → ratio = 0.05 = 5.0x
        is_valid, score, message = config.validate_price_ratio(
            price_monthly=150000,
            pain_monthly=3000000
        )
        
        assert is_valid is True
        assert "5.0x" in message
        assert "optimo" in message


class TestPriceMatchesPainCheck:
    """Test _check_price_matches_pain with decimal units."""
    
    def create_test_documents(self, price: float, pain: float):
        """Helper to create test diagnostic and proposal."""
        financial_impact = Scenario(
            monthly_loss_min=int(pain * 0.8),
            monthly_loss_max=int(pain),
            probability=0.7,
            description="realistic",
            assumptions=[],
            confidence_score=0.8,
            monthly_opportunity_cop=int(pain)
        )
        
        diagnostic = DiagnosticDocument(
            path="/tmp/diagnostic.md",
            problems=[],
            financial_impact=financial_impact,
            generated_at=datetime.now().isoformat()
        )
        
        proposal = ProposalDocument(
            path="/tmp/proposal.md",
            price_monthly=int(price),
            assets_proposed=[],
            roi_projected=3.5,
            generated_at=datetime.now().isoformat()
        )
        
        return diagnostic, proposal
    
    def test_price_in_ideal_range_passes(self):
        """Precio en rango ideal (4.0% = 0.04) pasa con score 1.0."""
        validator = CoherenceValidator()
        
        # Pain = 3M, Price = 120K → ratio = 0.04 = 4.0x (dentro de ideal +/- 0.5%)
        diagnostic, proposal = self.create_test_documents(
            price=135000,  # 4.5% de 3M
            pain=3000000
        )
        
        check = validator._check_price_matches_pain(proposal, diagnostic)
        
        assert check.passed is True
        assert check.score == 1.0
        assert "4.5x" in check.message
        assert "ideal" in check.message
    
    def test_price_in_acceptable_range_passes(self):
        """Precio en rango aceptable (3.5% = 0.035) pasa con score 0.8."""
        validator = CoherenceValidator()
        
        # Pain = 3M, Price = 105K → ratio = 0.035 = 3.5x
        diagnostic, proposal = self.create_test_documents(
            price=105000,
            pain=3000000
        )
        
        check = validator._check_price_matches_pain(proposal, diagnostic)
        
        assert check.passed is True
        assert check.score == 0.8
        assert "3.5x" in check.message
    
    def test_price_too_low_fails(self):
        """Precio muy bajo (< 3% = 0.03) falla."""
        validator = CoherenceValidator()
        
        # Pain = 3M, Price = 60K → ratio = 0.02 = 2.0x
        diagnostic, proposal = self.create_test_documents(
            price=60000,
            pain=3000000
        )
        
        check = validator._check_price_matches_pain(proposal, diagnostic)
        
        assert check.passed is False
        assert "muy bajo" in check.message
        assert "2.0x" in check.message
        assert "3.0x" in check.message  # Mínimo recomendado
    
    def test_price_too_high_fails(self):
        """Precio muy alto (> 6% = 0.06) falla."""
        validator = CoherenceValidator()
        
        # Pain = 3M, Price = 240K → ratio = 0.08 = 8.0x
        diagnostic, proposal = self.create_test_documents(
            price=240000,
            pain=3000000
        )
        
        check = validator._check_price_matches_pain(proposal, diagnostic)
        
        assert check.passed is False
        assert "muy alto" in check.message
        assert "8.0x" in check.message
        assert "6.0x" in check.message  # Máximo recomendado
    
    def test_no_pain_returns_passed(self):
        """Si no hay dolor financiero, pasa automáticamente."""
        validator = CoherenceValidator()
        
        diagnostic, proposal = self.create_test_documents(
            price=150000,
            pain=0
        )
        
        check = validator._check_price_matches_pain(proposal, diagnostic)
        
        assert check.passed is True
        assert check.score == 1.0
        assert "No hay dolor financiero" in check.message


class TestNoArtificialFail:
    """Verifica que no hay FAIL artificial por desalineación de unidades."""
    
    def test_ratio_decimal_matches_config(self):
        """
        Este es el test clave para M-001.
        
        Antes de la Sesión 5:
        - ratio = 0.05 (5%)
        - config.min_ratio = 3.0 (en x)
        - 0.05 < 3.0 → FAIL artificial
        
        Después de la Sesión 5:
        - ratio = 0.05 (5%)
        - config.min_ratio = 0.03 (en decimal)
        - 0.03 <= 0.05 <= 0.06 → PASS
        """
        config = CoherenceConfig()
        rule = config.get_price_rule()
        
        # Simular ratio de 0.05 (5% del dolor)
        ratio = 0.05
        
        # Verificar que está en rango
        assert rule.min_ratio <= ratio <= rule.max_ratio, \
            f"Ratio {ratio} debería estar en rango [{rule.min_ratio}, {rule.max_ratio}]"
        
        # Verificar validación pasa
        is_valid, score, message = config.validate_price_ratio(
            price_monthly=150000,  # 5% de 3M
            pain_monthly=3000000
        )
        
        assert is_valid is True, f"No debería haber FAIL artificial: {message}"
        assert score > 0.5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
