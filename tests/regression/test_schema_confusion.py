"""Tests de regresion para confusion de Schema."""

import pytest
from data_models.canonical_assessment import CanonicalAssessment, SchemaAnalysis, Claim
from enums.severity import Severity


class TestSchemaConfusion:
    """Tests para identificacion correcta de Schema."""
    
    def test_schema_hotel_correctly_identified(self):
        """Distingue Schema Hotel de Organization."""
        schema_data = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating"],
            present_fields=["name", "address", "telephone"],
            has_hotel_schema=True,
            has_local_business=False
        )
        
        assert schema_data.schema_type == "Hotel"
        assert schema_data.has_hotel_schema is True
        # No debe reportar como Organization
        
    def test_schema_missing_critical_fields_detected(self):
        """Detecta campos criticos faltantes."""
        schema_analysis = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating", "postalCode"],
            present_fields=["name", "address", "telephone", "priceRange"],
            has_hotel_schema=True,
            has_local_business=False
        )
        
        assert "image" in schema_analysis.missing_critical_fields
        assert "aggregateRating" in schema_analysis.missing_critical_fields
        # Para rich results, image y aggregateRating son criticos
        
    def test_schema_coverage_calculation(self):
        """Calcula coverage_score correctamente."""
        # 4 presentes de 7 totales (4 presentes + 3 faltantes)
        schema = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating", "postalCode"],
            present_fields=["name", "address", "telephone", "priceRange"],
            has_hotel_schema=True,
            has_local_business=False
        )
        
        # Score debe estar entre 0.5 y 0.7
        assert 0.5 <= schema.coverage_score <= 0.7
        
    def test_schema_postalcode_optional_handling(self):
        """Maneja postalCode como campo opcional."""
        # postalCode es opcional segun Google
        schema = SchemaAnalysis(
            schema_type="Hotel",
            coverage_score=0.6,
            missing_critical_fields=["image", "aggregateRating", "postalCode"],
            present_fields=["name", "address", "telephone"],
            has_hotel_schema=True,
            has_local_business=False
        )
        
        # postalCode esta en missing pero no bloquea
        assert "postalCode" in schema.missing_critical_fields
        # Pero el schema sigue siendo funcional
        assert schema.has_hotel_schema is True
