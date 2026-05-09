"""Tests for monthly_report asset generation.

Validates that the monthly_report asset:
- Is in the catalog as IMPLEMENTED
- Has promised_by including "always"
- Generates valid content with hotel data
- Generates valid content without hotel data (fallback)
"""

import pytest
from modules.asset_generation.asset_catalog import ASSET_CATALOG, AssetStatus
from modules.asset_generation.monthly_report_generator import MonthlyReportGenerator


class TestMonthlyReportCatalog:
    """Test monthly_report entry in asset catalog."""

    def test_monthly_report_exists_in_catalog(self):
        """monthly_report must exist in the asset catalog."""
        assert "monthly_report" in ASSET_CATALOG

    def test_monthly_report_is_implemented(self):
        """monthly_report status must be IMPLEMENTED."""
        entry = ASSET_CATALOG["monthly_report"]
        assert entry.status == AssetStatus.IMPLEMENTED

    def test_monthly_report_has_promised_by_always(self):
        """monthly_report promised_by must include 'always' so it's always generated."""
        entry = ASSET_CATALOG["monthly_report"]
        assert "always" in entry.promised_by

    def test_monthly_report_block_on_failure_false(self):
        """monthly_report must not block on failure."""
        entry = ASSET_CATALOG["monthly_report"]
        assert entry.block_on_failure is False

    def test_monthly_report_required_field_hotel_data(self):
        """monthly_report requires hotel_data field."""
        entry = ASSET_CATALOG["monthly_report"]
        assert entry.required_field == "hotel_data"


class TestMonthlyReportGenerator:
    """Test MonthlyReportGenerator content generation."""

    def test_generate_with_hotel_data(self):
        """Test generation with complete hotel data."""
        gen = MonthlyReportGenerator()
        hotel_data = {
            "name": "Hotel Test",
            "city": "Pereira",
            "website": "https://test.com",
        }
        content = gen.generate(hotel_data)
        assert len(content) > 200
        assert "Hotel Test" in content
        assert "Pereira" in content
        assert "KPIs a Monitorear" in content
        assert "Checklist" in content

    def test_generate_without_hotel_data(self):
        """Test generation with empty data (fallback)."""
        gen = MonthlyReportGenerator()
        content = gen.generate({})
        assert len(content) > 200
        assert "Hotel" in content  # default name

    def test_generate_with_custom_period(self):
        """Test generation with custom period."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel"}, period="Marzo 2026")
        assert "Marzo 2026" in content

    def test_generate_contains_kpi_tables(self):
        """Generated report must contain KPI tracking tables."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel"})
        assert "Tráfico Web" in content
        assert "Google Business Profile" in content
        assert "Reservas Directas" in content
        assert "WhatsApp" in content
        assert "SEO" in content

    def test_generate_contains_disclaimer(self):
        """Generated report must contain disclaimer about GA4/GSC requirements."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel"})
        assert "Disclaimer" in content or "Disclaimer" in content or "GA4" in content

    def test_generate_contains_assets_summary(self):
        """Generated report must list delivered assets."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel"})
        assert "Assets" in content or "assets" in content

    def test_generate_no_hardcoded_geo_playbook(self):
        """Output must NOT contain hardcoded 'Geo Playbook' or 'Voice Assistant Guide'."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel"})
        assert "Geo Playbook" not in content
        assert "Voice Assistant Guide" not in content

    def test_assets_table_empty_when_no_report(self):
        """When no asset_generation_report.json exists, table shows empty note."""
        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel", "output_dir": "/tmp/nonexistent_dir_xyz"})
        idx = content.find("## 4. Resumen")
        section = content[idx:idx+300]
        assert "No se generaron assets" in section

    def test_assets_table_dynamic_from_json(self):
        """Table reflects actual states from asset_generation_report.json."""
        import json, os
        test_dir = "/tmp/test_report_dir"
        os.makedirs(test_dir, exist_ok=True)
        report_path = os.path.join(test_dir, "asset_generation_report.json")
        with open(report_path, 'w') as f:
            json.dump({
                "generated_assets": {
                    "Schema Hotel (JSON-LD)": {"can_use": True, "confidence_score": 0.95},
                    "FAQ Page": {"can_use": True, "confidence_score": 0.80},
                    "Geo Playbook": {"can_use": False, "confidence_score": 0.25},
                }
            }, f)

        gen = MonthlyReportGenerator()
        content = gen.generate({"name": "Test Hotel", "output_dir": test_dir})
        idx = content.find("## 4. Resumen")
        section = content[idx:idx+500]
        # Must show real asset names from JSON, not hardcoded ones
        assert "Schema Hotel (JSON-LD)" in section
        assert "✅ Entregado" in section
        assert "⚠️ No disponible" in section
        # Must NOT have the hardcoded list
        assert section.count("✅ Entregado") == 2  # only real ones
