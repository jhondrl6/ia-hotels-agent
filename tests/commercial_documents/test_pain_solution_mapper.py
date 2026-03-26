"""
Tests for PainSolutionMapper - WhatsApp detection fixes (FASE-A).

Tests:
- test_detect_pain_no_whatsapp_unknown: Existing behavior must still pass
- test_detect_pain_whatsapp_conflict: New behavior for CONFLICT confidence
"""

import pytest
from unittest.mock import MagicMock

from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper, Pain
from modules.commercial_documents.data_structures import (
    V4AuditResult, ValidationSummary, ValidatedField, SchemaValidation,
    GBPData, PerformanceData, CrossValidationResult
)
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


def create_mock_audit_result():
    """Create a minimal mock V4AuditResult for testing."""
    schema = MagicMock(spec=SchemaValidation)
    schema.faq_schema_detected = True
    schema.hotel_schema_detected = True
    schema.org_schema_detected = True
    
    gbp = MagicMock(spec=GBPData)
    gbp.geo_score = 80
    gbp.reviews = 50
    gbp.confidence = "verified"
    
    performance = MagicMock(spec=PerformanceData)
    performance.mobile_score = 75
    performance.has_field_data = True
    
    validation = MagicMock(spec=CrossValidationResult)
    
    return MagicMock(spec=V4AuditResult, schema=schema, gbp=gbp, 
                    performance=performance, validation=validation)


def create_validation_summary(fields):
    """Create a ValidationSummary with the given fields."""
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.VERIFIED)


def create_whatsapp_field(confidence_level):
    """Create a ValidatedField for whatsapp_number with specified confidence."""
    return ValidatedField(
        field_name="whatsapp_number",
        value="+1234567890",
        confidence=confidence_level,
        sources=["web_scraping"],
        match_percentage=1.0,
        can_use_in_assets=True
    )


class TestPainSolutionMapperWhatsApp:
    """Test WhatsApp detection in PainSolutionMapper."""

    def test_detect_pain_no_whatsapp_unknown(self):
        """Test that no_whatsapp_visible is detected when confidence is UNKNOWN."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with UNKNOWN confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.UNKNOWN)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect no_whatsapp_visible
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_detect_pain_no_whatsapp_missing(self):
        """Test that no_whatsapp_visible is detected when whatsapp field is missing."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary without whatsapp field
        validation_summary = create_validation_summary([])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect no_whatsapp_visible
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_detect_pain_whatsapp_conflict(self):
        """Test that whatsapp_conflict is detected when confidence is CONFLICT."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with CONFLICT confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.CONFLICT)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect BOTH no_whatsapp_visible AND whatsapp_conflict
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids, \
            "CONFLICT should also trigger no_whatsapp_visible"
        assert "whatsapp_conflict" in pain_ids, \
            "CONFLICT should trigger whatsapp_conflict"
        
        # Find the whatsapp_conflict pain and verify its properties
        conflict_pain = next((p for p in pains if p.id == "whatsapp_conflict"), None)
        assert conflict_pain is not None
        assert conflict_pain.name == "Conflicto de WhatsApp"
        assert conflict_pain.severity == "high"
        assert conflict_pain.detected_by == "validation"
        assert conflict_pain.confidence == 0.5

    def test_no_pain_when_whatsapp_verified(self):
        """Test that no WhatsApp pain is detected when confidence is VERIFIED."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with VERIFIED confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.VERIFIED)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should NOT detect any WhatsApp-related pain
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" not in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_pain_solution_map_contains_whatsapp_conflict(self):
        """Test that PAIN_SOLUTION_MAP includes whatsapp_conflict entry."""
        mapper = PainSolutionMapper()
        
        assert "whatsapp_conflict" in mapper.pain_map
        
        conflict_entry = mapper.pain_map["whatsapp_conflict"]
        assert conflict_entry["assets"] == ["whatsapp_button"]
        assert conflict_entry["confidence_required"] == 0.5
        assert conflict_entry["priority"] == 1
        assert conflict_entry["validation_fields"] == ["whatsapp_number"]
        assert conflict_entry["estimated_impact"] == "high"
        assert conflict_entry["name"] == "Conflicto de WhatsApp"
