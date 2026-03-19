"""Tests for new asset types in conditional generator."""
import pytest
import json
from modules.asset_generation.conditional_generator import ConditionalGenerator


class TestNewAssetTypes:
    """Test generation of new asset types."""

    def setup_method(self):
        self.generator = ConditionalGenerator(output_dir="/tmp/test_output")

    def test_generate_geo_playbook(self):
        """Test geo_playbook generation."""
        result = self.generator._generate_geo_playbook(
            {"geo_score": 50}, "Hotel Test"
        )

        assert "Geo Playbook" in result
        assert "Hotel Test" in result
        assert "Google Business Profile" in result
        assert "Checklist" in result or "Acciones" in result

    def test_generate_review_plan(self):
        """Test review_plan generation."""
        result = self.generator._generate_review_plan(
            {"reviews": 10}, "Hotel Test"
        )

        assert "Plan de Reviews" in result or "Reviews" in result
        assert "Hotel Test" in result
        assert "Estrategia" in result or "Objetivos" in result

    def test_generate_review_widget(self):
        """Test review_widget generation."""
        result = self.generator._generate_review_widget(
            {"rating": 4.5}, "Hotel Test"
        )

        assert "<div" in result  # HTML content
        assert "review-widget" in result or "widget" in result.lower()
        assert "Hotel Test" in result

    def test_generate_org_schema(self):
        """Test org_schema generation."""
        result = self.generator._generate_org_schema(
            {"website": "https://test.com", "phone": "+57 123"},
            "Hotel Test"
        )

        # Should be valid JSON
        schema = json.loads(result)
        assert schema["@type"] == "Organization"
        assert schema["name"] == "Hotel Test"
        assert "https://schema.org" in schema["@context"]
