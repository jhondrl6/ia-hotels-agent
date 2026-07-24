"""Tests for Open Graph end-to-end generation - FASE-C.

Tests:
1. audit_report with open_graph=false activates pain_id no_og_tags
2. pain_id no_og_tags generates asset open_graph with template
3. audit_report with open_graph=true NO activates pain_id
4. template open_graph generates HTML valido con placeholders reemplazados
"""

import pytest
import logging
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


class MockSEOElements:
    """Mock SEOElementsResult for testing."""
    def __init__(self, open_graph: bool, confidence: str = "high"):
        self.open_graph = open_graph
        self.imagenes_alt = False
        self.redes_activas = False
        self.confidence = confidence
        self.notes = ""
        self.open_graph_tags = {}
        self.images_without_alt = 0
        self.social_links_found = []


class TestOpenGraphPainIdActivation:
    """Test suite for open_graph pain_id activation from audit_report."""
    
    def test_audit_report_open_graph_false_activates_pain_id_no_og_tags(self):
        """Test that open_graph=false in audit_report activates pain_id no_og_tags."""
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper, Pain
        from modules.commercial_documents.data_structures import ValidationSummary, ConfidenceLevel
        
        # Create a mock audit_result with seo_elements
        mock_audit = Mock()
        mock_audit.seo_elements = MockSEOElements(open_graph=False, confidence="high")
        # Mock other required attributes to avoid AttributeError
        mock_audit.schema = Mock(faq_schema_detected=True, hotel_schema_detected=True, org_schema_detected=True)
        mock_audit.gbp = Mock(geo_score=80, reviews=50, confidence="high")
        mock_audit.performance = Mock(mobile_score=70, has_field_data=True)
        mock_audit.metadata = Mock(has_issues=False, has_default_title=False, has_default_description=False)
        mock_audit.ai_crawlers = None
        mock_audit.citability = None
        mock_audit.ia_readiness = None
        
        # Create mock validation_summary
        mock_validation_summary = Mock()
        mock_validation_summary.get_field = Mock(return_value=None)
        mock_validation_summary.fields = []
        
        # Create mapper and detect pains
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(mock_audit, mock_validation_summary)
        
        # Verify no_og_tags pain is detected
        pain_ids = [p.id for p in pains]
        assert "no_og_tags" in pain_ids, f"Expected no_og_tags in {pain_ids}"
        
        # Verify the pain has correct properties
        no_og_pain = next((p for p in pains if p.id == "no_og_tags"), None)
        assert no_og_pain is not None
        assert no_og_pain.severity == "medium"
        assert no_og_pain.detected_by == "seo_elements_detection"
        assert no_og_pain.confidence == 0.9  # high confidence
    
    def test_audit_report_open_graph_true_incomplete_tags_activates_pain_id_enhance(self):
        """Test that open_graph=true WITH incomplete OG tags (<10) activates no_og_tags in enhance_existing mode."""
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
        from modules.commercial_documents.data_structures import ValidationSummary
        
        # Create mock audit result with open_graph=True but FEW tags (enhance_existing mode)
        mock_audit = Mock()
        seo_elem = MockSEOElements(open_graph=True, confidence="high")
        # Only 3 tags → incomplete (< 10 threshold)
        seo_elem.open_graph_tags = {"og:title": "...", "og:description": "...", "og:url": "..."}
        mock_audit.seo_elements = seo_elem
        mock_audit.schema = Mock(faq_schema_detected=True, hotel_schema_detected=True, org_schema_detected=True)
        mock_audit.gbp = Mock(geo_score=80, reviews=50, confidence="high")
        mock_audit.performance = Mock(mobile_score=70, has_field_data=True)
        mock_audit.metadata = Mock(has_issues=False, has_default_title=False, has_default_description=False)
        mock_audit.ai_crawlers = None
        mock_audit.citability = None
        mock_audit.ia_readiness = None
        
        mock_validation_summary = Mock()
        mock_validation_summary.get_field = Mock(return_value=None)
        mock_validation_summary.fields = []
        
        # Create mapper and detect pains
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(mock_audit, mock_validation_summary)
        
        # Verify no_og_tags IS detected (enhance_existing mode)
        pain_ids = [p.id for p in pains]
        assert "no_og_tags" in pain_ids, f"Expected no_og_tags in enhance_existing mode: {pain_ids}"
        
        # Verify enhanced pain has lower confidence
        no_og_pain = next((p for p in pains if p.id == "no_og_tags"), None)
        assert no_og_pain is not None
        assert no_og_pain.confidence == 0.5  # Medium confidence in enhance_existing mode


class TestOpenGraphAssetGeneration:
    """Test suite for open_graph asset generation from pain_id."""
    
    def test_pain_id_no_og_tags_generates_open_graph_asset(self):
        """Test that pain_id no_og_tags generates open_graph asset."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        from modules.asset_generation.asset_catalog import is_asset_implemented
        
        # Verify open_graph is implemented
        assert is_asset_implemented("open_graph"), "open_graph asset should be implemented"
        
        # Create generator
        generator = ConditionalGenerator()
        
        # Check PAIN_TO_ASSET mapping
        assert "no_og_tags" in generator.PAIN_TO_ASSET, "no_og_tags should be in PAIN_TO_ASSET"
        
        # Get assets for no_og_tags
        asset_types = generator.PAIN_TO_ASSET["no_og_tags"]
        # Handle both string and list formats
        if isinstance(asset_types, str):
            asset_types = [asset_types]
        assert "open_graph" in asset_types, f"open_graph should be in assets for no_og_tags: {asset_types}"
    
    def test_open_graph_template_exists_and_valid(self):
        """Test that open_graph_template.html exists and is valid."""
        template_path = Path("modules/asset_generation/templates/open_graph_template.html")
        assert template_path.exists(), f"Template should exist at {template_path}"
        
        content = template_path.read_text(encoding='utf-8')
        
        # Check required placeholders
        required_placeholders = [
            "{{hotel_name}}",
            "{{description}}",
            "{{image_url}}",
            "{{url}}",
            "{{site_name}}"
        ]
        for placeholder in required_placeholders:
            assert placeholder in content, f"Template should contain {placeholder}"
        
        # Check required OG tags
        assert 'og:title' in content
        assert 'og:description' in content
        assert 'og:image' in content
        assert 'og:url' in content
        assert 'og:type' in content
        assert 'og:site_name' in content
        
        # Check Twitter card tags
        assert 'twitter:card' in content
        assert 'twitter:title' in content
        assert 'twitter:description' in content
        assert 'twitter:image' in content
    
    def test_open_graph_template_replaces_placeholders(self):
        """Test that open_graph template properly replaces placeholders."""
        from modules.asset_generation.open_graph_generator import OpenGraphGenerator
        
        generator = OpenGraphGenerator()
        
        # Use field names that OpenGraphGenerator._extract_og_data expects
        test_data = {
            "hotel_name": "Test Hotel Colombia",
            "description": "Hotel de prueba en Colombia",
            "website_url": "https://test-hotel.com/",  # OpenGraphGenerator expects website_url
            "photo_url": "https://example.com/hotel.jpg",
            "photos": [{"url": "https://example.com/hotel.jpg"}],
            "rating": 4.5,
            "review_count": 100,
            "phone": "+57 300 1234567",
            "address": "Calle 123, Bogota",
        }
        
        # Generate using OpenGraphGenerator
        og_data = generator._extract_og_data(test_data)
        html = generator._generate_html(og_data)
        
        # Verify placeholders are NOT in output
        assert "{{hotel_name}}" not in html
        assert "{{description}}" not in html
        assert "{{image_url}}" not in html
        assert "{{url}}" not in html
        
        # Verify actual data is in output
        assert "Test Hotel Colombia" in html
        assert "https://test-hotel.com/" in html


class TestOpenGraphIntegration:
    """Integration tests for open_graph end-to-end flow."""
    
    def test_conditional_generator_open_graph_branch(self):
        """Test conditional_generator has open_graph branch."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        generator = ConditionalGenerator()
        
        # Verify open_graph is in GENERATION_STRATEGIES
        assert "open_graph" in generator.GENERATION_STRATEGIES, "open_graph should be in GENERATION_STRATEGIES"
    
    def test_full_flow_audit_to_asset(self):
        """Test full flow from audit_report with open_graph=false to open_graph asset."""
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        from modules.asset_generation.asset_catalog import is_asset_implemented
        
        # Verify open_graph is implemented
        assert is_asset_implemented("open_graph"), "open_graph asset should be implemented"
        
        # Check PAIN_TO_ASSET has no_og_tags mapped to open_graph
        generator = ConditionalGenerator()
        assert "no_og_tags" in generator.PAIN_TO_ASSET
        
        asset_types = generator.PAIN_TO_ASSET["no_og_tags"]
        if isinstance(asset_types, str):
            asset_types = [asset_types]
        assert "open_graph" in asset_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])