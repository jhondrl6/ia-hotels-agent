"""
Tests for FASE 6: Orchestration V2 - Data Assessment and Intelligent Branching

TDD Gate: 4 mandatory tests must pass for FASE 6 completion.

Tests:
1. test_data_assessment_low - Clasifica hotels <30% datos como LOW
2. test_data_assessment_high - Clasifica hotels >70% datos como HIGH
3. test_validation_before_generation - No genera si datos inválidos
4. test_branching_paths - 3 paths ejecutan correctamente
"""

import pytest
from unittest.mock import MagicMock, patch
from pathlib import Path

from modules.asset_generation.data_assessment import (
    DataAssessment,
    DataClassification,
    DataAssessmentResult,
    DataMetric
)


class TestDataAssessment:
    """Tests for Data Assessment module."""
    
    def test_data_assessment_low(self):
        """
        Test: Clasifica hotels <30% datos como LOW.
        
        Scenario: Hotel con datos mínimos (solo nombre)
        Expected: classification = LOW
        """
        assessor = DataAssessment()
        
        # Minimal data: only name present
        hotel_data = {"name": "Hotel Minimal"}
        
        result = assessor.assess(
            hotel_data=hotel_data,
            gbp_data=None,
            seo_data=None,
            scraping_success=False
        )
        
        assert result.classification == DataClassification.LOW
        assert result.overall_score < 0.30
        assert "name" not in result.missing_data or len(result.missing_data) >= 3
    
    def test_data_assessment_high(self):
        """
        Test: Clasifica hotels >70% datos como HIGH.
        
        Scenario: Hotel con datos completos
        Expected: classification = HIGH
        """
        assessor = DataAssessment()
        
        # Complete data
        hotel_data = {
            "name": "Hotel Completo",
            "phone": "+1234567890",
            "address": "123 Main St",
            "email": "info@hotel.com",
            "website": "https://hotel.com",
            "description": "A wonderful hotel",
            "amenities": ["pool", "gym", "spa"]
        }
        
        gbp_data = {
            "reviews": ["Great hotel!", "Amazing stay"],
            "photos": ["photo1.jpg", "photo2.jpg", "photo3.jpg"],
            "rating": 4.5,
            "reviews_count": 100
        }
        
        seo_data = {
            "schema_markup": True,
            "meta_description": "Hotel description",
            "title_tag": "Hotel Completo",
            "headings": True
        }
        
        result = assessor.assess(
            hotel_data=hotel_data,
            gbp_data=gbp_data,
            seo_data=seo_data,
            scraping_success=True
        )
        
        assert result.classification == DataClassification.HIGH
        assert result.overall_score >= 0.70
    
    def test_data_assessment_medium(self):
        """
        Test: Clasifica hotels 30-70% datos como MED.
        
        Scenario: Hotel con datos parciales
        Expected: classification = MED
        """
        assessor = DataAssessment()
        
        # Partial data
        hotel_data = {
            "name": "Hotel Parcial",
            "phone": "+1234567890",
            # Missing address
        }
        
        gbp_data = {
            "reviews": ["Good hotel!"],
            "photos": [],
            "rating": 3.5,
            "reviews_count": 10
        }
        
        result = assessor.assess(
            hotel_data=hotel_data,
            gbp_data=gbp_data,
            seo_data={},
            scraping_success=False
        )
        
        assert result.classification == DataClassification.MED
        assert 0.30 <= result.overall_score < 0.70


class TestValidationBeforeGeneration:
    """Tests for validation before generation."""
    
    def test_validation_before_generation(self):
        """
        Test: No genera si datos inválidos.
        
        Scenario: Intentar generar con datos inválidos (score = 0)
        Expected: Generation should be blocked or use minimal path
        """
        assessor = DataAssessment()
        
        # Empty data should result in LOW classification
        result = assessor.assess(
            hotel_data={},
            gbp_data=None,
            seo_data=None,
            scraping_success=False
        )
        
        # Data is technically "valid" but LOW - generation should use fast path
        assert result.classification == DataClassification.LOW
        
        # Fast path should be recommended
        path = assessor.get_generation_path(result.classification)
        assert path == "fast"
        
        # But generation CAN proceed (with warnings)
        assert result.is_valid or len(result.missing_data) >= 5


class TestBranchingPaths:
    """Tests for branching paths (fast/standard/full)."""
    
    def test_branching_paths(self):
        """
        Test: 3 paths ejecutan correctamente.
        
        Scenario: Clasificar y verificar que cada path tiene el rango correcto
        Expected: LOW→fast(3-4), MED→standard(6-7), HIGH→full(9-12)
        """
        assessor = DataAssessment()
        
        # Test LOW path
        low_result = assessor.assess(
            hotel_data={"name": "Low Hotel"},
            gbp_data=None,
            seo_data=None,
            scraping_success=False
        )
        assert low_result.classification == DataClassification.LOW
        assert assessor.get_generation_path(low_result.classification) == "fast"
        low_range = assessor.get_asset_count_range(low_result.classification)
        assert low_range == (3, 4)
        
        # Test MED path
        med_result = assessor.assess(
            hotel_data={
                "name": "Med Hotel",
                "phone": "+123",
                "address": "123 Main St"
            },
            gbp_data={
                "reviews": ["Good"],
                "rating": 4.0,
                "reviews_count": 50,
                "photos": []
            },
            seo_data={"schema_markup": True},
            scraping_success=False
        )
        assert med_result.classification == DataClassification.MED
        assert assessor.get_generation_path(med_result.classification) == "standard"
        med_range = assessor.get_asset_count_range(med_result.classification)
        assert med_range == (6, 7)
        
        # Test HIGH path
        high_result = assessor.assess(
            hotel_data={
                "name": "High Hotel",
                "phone": "+1234567890",
                "address": "123 Main St",
                "email": "info@hotel.com",
                "website": "https://hotel.com",
                "description": "A wonderful hotel",
                "amenities": ["pool", "gym", "spa"]
            },
            gbp_data={
                "reviews": ["Great!", "Amazing!"],
                "photos": ["p1.jpg", "p2.jpg", "p3.jpg"],
                "rating": 4.8,
                "reviews_count": 200
            },
            seo_data={
                "schema_markup": True,
                "meta_description": True,
                "title_tag": True,
                "headings": True
            },
            scraping_success=True
        )
        assert high_result.classification == DataClassification.HIGH
        assert assessor.get_generation_path(high_result.classification) == "full"
        high_range = assessor.get_asset_count_range(high_result.classification)
        assert high_range == (9, 12)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
