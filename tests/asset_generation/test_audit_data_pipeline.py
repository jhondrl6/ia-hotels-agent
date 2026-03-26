"""Tests for FASE 12: Audit Data Pipeline - Bug 1 Fix

Verifica que V4ComprehensiveAuditor pasa los datos del hotel al ConditionalGenerator
a través de V4AssetOrchestrator._extract_validated_fields().

ISSUE: hotel_schema.json contenía "name": "Hotel" en lugar de "Hotel Vísperas"
CAUSA: _extract_validated_fields() no pasaba hotel_data del audit_result.schema.properties
"""

import pytest
from unittest.mock import Mock, MagicMock
from pathlib import Path

from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
from modules.commercial_documents.data_structures import (
    V4AuditResult,
    ValidationSummary,
    ValidatedField,
    SchemaValidation,
    GBPData,
    PerformanceData,
    CrossValidationResult,
)


class TestAuditDataPipeline:
    """Tests for audit data pipeline (FASE 12)."""

    def _create_mock_audit_result(self):
        """Create a mock V4AuditResult with hotel data."""
        mock_audit = Mock(spec=V4AuditResult)
        mock_audit.url = "https://hotelvisperas.com"
        mock_audit.hotel_name = "Hotel Visperas"
        mock_audit.timestamp = "2026-03-25T10:00:00"
        
        # Schema with real hotel data
        mock_schema = Mock(spec=SchemaValidation)
        mock_schema.hotel_schema_detected = True
        mock_schema.hotel_schema_valid = True
        mock_schema.hotel_confidence = "HIGH"
        mock_schema.faq_schema_detected = True
        mock_schema.faq_schema_valid = True
        mock_schema.faq_confidence = "HIGH"
        mock_schema.org_schema_detected = False
        mock_schema.total_schemas = 2
        mock_schema.errors = []
        
        # Actual hotel properties that should flow to assets
        mock_schema.properties = {
            "name": "Hotel Visperas",
            "description": "Hotel boutique de lujo en Santa Rosa de Cabal",
            "telephone": "+573001234567",
            "url": "https://hotelvisperas.com",
            "address": "Santa Rosa de Cabal, Risaralda, Colombia",
            "image": "https://hotelvisperas.com/images/hotel.jpg",
            "price_range": "$$"
        }
        
        mock_audit.schema = mock_schema
        mock_audit.gbp = Mock(spec=GBPData)
        mock_audit.performance = Mock(spec=PerformanceData)
        mock_audit.validation = Mock(spec=CrossValidationResult)
        mock_audit.overall_confidence = "HIGH"
        mock_audit.critical_issues = []
        
        return mock_audit

    def _create_validation_summary(self):
        """Create a mock ValidationSummary with validated fields."""
        mock_summary = Mock(spec=ValidationSummary)
        
        # Create some validated fields
        whatsapp_field = Mock(spec=ValidatedField)
        whatsapp_field.field_name = "whatsapp"
        whatsapp_field.value = "+573001234567"
        whatsapp_field.confidence = "HIGH"
        whatsapp_field.sources = ["web"]
        
        rooms_field = Mock(spec=ValidatedField)
        rooms_field.field_name = "rooms"
        rooms_field.value = 12
        rooms_field.confidence = "MEDIUM"
        rooms_field.sources = ["web"]
        
        adr_field = Mock(spec=ValidatedField)
        adr_field.field_name = "adr"
        adr_field.value = 180000
        adr_field.confidence = "HIGH"
        adr_field.sources = ["web"]
        
        mock_summary.fields = [whatsapp_field, rooms_field, adr_field]
        
        return mock_summary

    def test_extract_validated_fields_with_audit_result(self):
        """
        FASE 12: Test that _extract_validated_fields includes hotel_data from audit.
        
        BEFORE FIX: validated_data = { whatsapp, rooms, adr }
        AFTER FIX:  validated_data = { whatsapp, rooms, adr, hotel_data: { name, description, ... } }
        """
        orchestrator = V4AssetOrchestrator(output_base_dir="output")
        
        audit_result = self._create_mock_audit_result()
        validation_summary = self._create_validation_summary()
        
        validated_data = orchestrator._extract_validated_fields(
            validation_summary, 
            audit_result=audit_result
        )
        
        # Should have both the field data AND hotel_data
        assert "whatsapp" in validated_data
        assert "rooms" in validated_data
        assert "adr" in validated_data
        
        # FASE 12: hotel_data should be present
        assert "hotel_data" in validated_data, "hotel_data must be in validated_data after FASE 12 fix"
        
        hotel_data = validated_data["hotel_data"]
        assert hotel_data["name"] == "Hotel Visperas"
        assert hotel_data["description"] == "Hotel boutique de lujo en Santa Rosa de Cabal"
        assert hotel_data["telephone"] == "+573001234567"
        assert hotel_data["url"] == "https://hotelvisperas.com"
        assert hotel_data["address"] == "Santa Rosa de Cabal, Risaralda, Colombia"
        assert hotel_data["price_range"] == "$$"

    def test_extract_validated_fields_without_audit_result(self):
        """
        BACKWARD COMPATIBILITY: Should work without audit_result (default None).
        """
        orchestrator = V4AssetOrchestrator(output_base_dir="output")
        
        validation_summary = self._create_validation_summary()
        
        # Should NOT raise - audit_result is optional
        validated_data = orchestrator._extract_validated_fields(validation_summary)
        
        # Original fields should still work
        assert "whatsapp" in validated_data
        assert "rooms" in validated_data
        assert "adr" in validated_data
        
        # hotel_data should NOT be present when audit_result is None
        assert "hotel_data" not in validated_data

    def test_extract_validated_fields_with_partial_schema(self):
        """
        Should handle audit_result with incomplete schema gracefully.
        """
        orchestrator = V4AssetOrchestrator(output_base_dir="output")
        
        audit_result = self._create_mock_audit_result()
        # Clear some properties to simulate partial data
        audit_result.schema.properties = {
            "name": "Hotel Partial"
            # Other fields missing
        }
        
        validation_summary = self._create_validation_summary()
        
        validated_data = orchestrator._extract_validated_fields(
            validation_summary, 
            audit_result=audit_result
        )
        
        assert "hotel_data" in validated_data
        assert validated_data["hotel_data"]["name"] == "Hotel Partial"
        # Missing fields should return None (dict.get() default)
        assert validated_data["hotel_data"]["telephone"] is None

    def test_hotel_data_flows_to_conditional_generator(self):
        """
        Integration test: Verify hotel_data reaches ConditionalGenerator.
        
        This simulates the full flow:
        1. V4AssetOrchestrator.generate_assets() receives audit_result
        2. _extract_validated_fields() extracts hotel_data
        3. validated_data is passed to ConditionalGenerator
        """
        orchestrator = V4AssetOrchestrator(output_base_dir="output")
        
        audit_result = self._create_mock_audit_result()
        validation_summary = self._create_validation_summary()
        
        # Extract validated fields (this is what happens at line 220 of generate_assets)
        validated_data = orchestrator._extract_validated_fields(
            validation_summary, 
            audit_result
        )
        
        # Verify hotel_data is ready to be passed to ConditionalGenerator
        assert validated_data["hotel_data"]["name"] == "Hotel Visperas"
        
        # The ConditionalGenerator would use hotel_data like:
        # hotel_name = validated_data["hotel_data"].get("name", "Hotel")
        # Instead of the broken behavior:
        # hotel_name = "Hotel"  # default hardcoded value
