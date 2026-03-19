"""Tests for V4ComprehensiveAuditor competitors integration."""
import pytest
from unittest.mock import Mock, patch
from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor, V4AuditResult


class TestV4ComprehensiveCompetitors:
    """Test competitors integration in v4 comprehensive audit."""
    
    @patch.object(V4ComprehensiveAuditor, '_audit_gbp')
    @patch.object(V4ComprehensiveAuditor, '_audit_competitors')
    def test_audit_includes_competitors(self, mock_audit_competitors, mock_audit_gbp):
        """Audit result should include competitors list."""
        # Create complete GBP mock with all required attributes
        gbp_mock = Mock()
        gbp_mock.place_found = True
        gbp_mock.name = "Test Hotel"
        gbp_mock.geo_score = 75
        gbp_mock.place_id = "test_123"
        gbp_mock.photos = 15  # Required by _generate_recommendations
        gbp_mock.reviews = 30  # Required by _generate_recommendations
        gbp_mock.rating = 4.5
        mock_audit_gbp.return_value = gbp_mock
        
        mock_audit_competitors.return_value = [
            {"nombre": "Competidor 1", "geo_score": 80}
        ]
        
        auditor = V4ComprehensiveAuditor()
        # Mock other methods to avoid API calls
        schema_mock = Mock()
        schema_mock.hotel_schema_detected = True
        schema_mock.hotel_confidence = "VERIFIED"
        schema_mock.faq_schema_detected = False
        schema_mock.total_schemas = 1
        schema_mock.properties = {}
        schema_mock.errors = []
        schema_mock.warnings = []
        auditor._audit_schemas = Mock(return_value=schema_mock)

        perf_mock = Mock()
        perf_mock.has_field_data = False
        perf_mock.mobile_score = 45
        perf_mock.status = "LAB_DATA_ONLY"
        perf_mock.lcp = None
        perf_mock.fid = None
        perf_mock.cls = None
        perf_mock.message = "Lab data only"
        auditor._audit_performance = Mock(return_value=perf_mock)

        validation_mock = Mock()
        validation_mock.whatsapp_status = "VERIFIED"
        validation_mock.phone_web = "+57 123"
        validation_mock.phone_gbp = "+57 123"
        validation_mock.adr_status = "ESTIMATED"
        validation_mock.conflicts = []
        auditor._run_cross_validation = Mock(return_value=validation_mock)
        
        result = auditor.audit("https://example.com", "Test Hotel")
        
        # Competitors should be called
        mock_audit_competitors.assert_called_once()
        
        # Result should include competitors
        assert hasattr(result, 'competitors')
        assert len(result.competitors) == 1
        assert result.competitors[0]["nombre"] == "Competidor 1"
    
    def test_audit_result_to_dict_includes_competitors(self):
        """to_dict should serialize competitors field."""
        from dataclasses import field
        
        # Create a mock result with competitors
        result = V4AuditResult(
            url="https://test.com",
            hotel_name="Test",
            timestamp="2026-03-02",
            schema=Mock(),
            gbp=Mock(),
            performance=Mock(),
            validation=Mock(),
            overall_confidence="VERIFIED",
            competitors=[{"nombre": "Hotel A", "geo_score": 80}]
        )
        
        data = result.to_dict()
        
        assert "competitors" in data
        assert len(data["competitors"]) == 1
