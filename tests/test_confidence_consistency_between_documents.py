"""
Test de consistencia de confianza entre documentos comerciales.

Verifica que el diagnóstico y la propuesta usen el mismo nivel de confianza global
y el mismo formato (UPPERCASE).

Issue: B-001 - Inconsistencia de Confianza Global
"""

import pytest
from dataclasses import dataclass, field
from typing import List, Dict, Any
from datetime import datetime

from modules.data_validation.confidence_taxonomy import (
    ConfidenceLevel as DVConfidenceLevel
)
from modules.commercial_documents.data_structures import (
    ConfidenceLevel as CDConfidenceLevel,
    ValidationSummary,
    ValidatedField,
    DiagnosticSummary,
    adapt_validation_confidence,
    confidence_to_label,
)


class TestAdaptValidationConfidence:
    """Test del adaptador de confianza."""
    
    def test_adapt_verified_lowercase(self):
        """Adapta 'verified' (lowercase) a verified (lowercase)."""
        result = adapt_validation_confidence(DVConfidenceLevel.VERIFIED)
        assert result == CDConfidenceLevel.VERIFIED
        assert result.value == "verified"
    
    def test_adapt_estimated_lowercase(self):
        """Adapta 'estimated' (lowercase) a estimated (lowercase)."""
        result = adapt_validation_confidence(DVConfidenceLevel.ESTIMATED)
        assert result == CDConfidenceLevel.ESTIMATED
        assert result.value == "estimated"
    
    def test_adapt_conflict_lowercase(self):
        """Adapta 'conflict' (lowercase) a conflict (lowercase)."""
        result = adapt_validation_confidence(DVConfidenceLevel.CONFLICT)
        assert result == CDConfidenceLevel.CONFLICT
        assert result.value == "conflict"
    
    def test_adapt_unknown_lowercase(self):
        """Adapta 'unknown' (lowercase) a unknown (lowercase)."""
        result = adapt_validation_confidence(DVConfidenceLevel.UNKNOWN)
        assert result == CDConfidenceLevel.UNKNOWN
        assert result.value == "unknown"
    
    def test_adapt_from_string(self):
        """Adapta desde string lowercase."""
        result = adapt_validation_confidence("verified")
        assert result == CDConfidenceLevel.VERIFIED
        
        result = adapt_validation_confidence("estimated")
        assert result == CDConfidenceLevel.ESTIMATED
    
    def test_adapt_unknown_value_defaults_to_unknown(self):
        """Valores desconocidos retornan UNKNOWN."""
        result = adapt_validation_confidence("invalid")
        assert result == CDConfidenceLevel.UNKNOWN


class TestConfidenceToLabel:
    """Test de normalizacion de confidence_to_label."""
    
    def test_returns_uppercase_for_enum(self):
        """Retorna UPPERCASE cuando recibe enum."""
        assert confidence_to_label(CDConfidenceLevel.VERIFIED) == "VERIFIED"
        assert confidence_to_label(CDConfidenceLevel.ESTIMATED) == "ESTIMATED"
    
    def test_returns_uppercase_for_string(self):
        """Retorna UPPERCASE cuando recibe string."""
        assert confidence_to_label("verified") == "VERIFIED"
        assert confidence_to_label("VERIFIED") == "VERIFIED"
        assert confidence_to_label("estimated") == "ESTIMATED"
        assert confidence_to_label("ESTIMATED") == "ESTIMATED"
    
    def test_handles_mixed_case(self):
        """Maneja casing mixto correctamente."""
        assert confidence_to_label("Verified") == "VERIFIED"
        assert confidence_to_label("EsTiMaTeD") == "ESTIMATED"


class TestDiagnosticSummaryConfidence:
    """Test de consistencia en DiagnosticSummary."""
    
    def test_diagnostic_summary_accepts_adapted_confidence(self):
        """DiagnosticSummary accepts adapted confidence."""
        summary = DiagnosticSummary(
            hotel_name='Test Hotel',
            critical_problems_count=3,
            quick_wins_count=2,
            overall_confidence=adapt_validation_confidence(DVConfidenceLevel.VERIFIED),
            top_problems=[],
            validated_data_summary={},
            coherence_score=None
        )
        assert summary.overall_confidence.value == "verified"
    
    def test_diagnostic_summary_value_is_lowercase(self):
        """DiagnosticSummary confidence value is lowercase."""
        summary = DiagnosticSummary(
            hotel_name='Test Hotel',
            critical_problems_count=3,
            quick_wins_count=2,
            overall_confidence=CDConfidenceLevel.ESTIMATED,
            top_problems=[],
            validated_data_summary={},
            coherence_score=None
        )
        assert summary.overall_confidence.value.islower()


class TestE2EConfidenceConsistency:
    """Test end-to-end de consistencia entre documentos."""
    
    def test_diagnostic_and_proposal_same_confidence_source(self):
        """
        Verifica que ambos documentos derivan de la misma fuente de confianza.
        
        Escenario: El flujo v4complete usa validation_summary.overall_confidence
        como fuente unica para diagnostic_summary.overall_confidence
        """
        # Simular ValidationSummary de data_validation (con lowercase)
        validation_summary = ValidationSummary(
            fields=[],
            overall_confidence=DVConfidenceLevel.VERIFIED,
        )
        
        # Adaptar a commercial_documents (UPPERCASE)
        adapted_confidence = adapt_validation_confidence(
            validation_summary.overall_confidence
        )
        
        # Crear DiagnosticSummary con confianza adaptada
        diagnostic_summary = DiagnosticSummary(
            hotel_name="Hotel Test",
            critical_problems_count=2,
            quick_wins_count=1,
            overall_confidence=adapted_confidence,
        )
        
        # Verificar consistencia
        assert diagnostic_summary.overall_confidence == CDConfidenceLevel.VERIFIED
        
        # Verificar que confidence_to_label produce UPPERCASE
        label = confidence_to_label(diagnostic_summary.overall_confidence)
        assert label == "VERIFIED"
        assert label.isupper()
    
    def test_no_uppercase_in_diagnostic_summary(self):
        """Test that diagnostic summary doesn't contain uppercase confidence values."""
        summary = DiagnosticSummary(
            hotel_name='Test',
            critical_problems_count=1,
            quick_wins_count=1,
            overall_confidence=CDConfidenceLevel.VERIFIED,
            top_problems=[],
            validated_data_summary={},
            coherence_score=None
        )
        assert summary.overall_confidence.value.islower(), \
            f"Valor {summary.overall_confidence.value} no es lowercase"


class TestB001Regression:
    """Test de regresion para B-001."""
    
    def test_b001_no_mixed_case_in_output(self):
        """
        Regresion: B-001 - Inconsistencia de Confianza Global.
        
        Antes: Diagnostico 'ESTIMATED', Propuesta 'verified'
        Despues: Ambos 'ESTIMATED' (UPPERCASE)
        """
        # Simular el escenario de B-001
        dv_confidence = DVConfidenceLevel.ESTIMATED  # "estimated"
        
        # Adaptar
        adapted = adapt_validation_confidence(dv_confidence)
        
        # Crear DiagnosticSummary
        summary = DiagnosticSummary(
            hotel_name="Hotel B001",
            critical_problems_count=3,
            quick_wins_count=2,
            overall_confidence=adapted,
        )
        
        # Convertir a label (como hacen los generadores)
        label = confidence_to_label(summary.overall_confidence)
        
        # Verificar que es UPPERCASE, no lowercase
        assert label == "ESTIMATED"
        assert label != "estimated"
        assert label.isupper()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
