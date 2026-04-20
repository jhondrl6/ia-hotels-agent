"""Tests for MonthlyReportGenerator with real GBP data."""

import pytest
from modules.asset_generation.monthly_report_generator import MonthlyReportGenerator


class TestMonthlyReportHasRealData:
    """Test that monthly report uses real GBP data when available."""

    def setup_method(self):
        self.generator = MonthlyReportGenerator()
        self.hotel_data = {
            "name": "Amazilia Hotel Campestre",
            "city": "Pereira",
            "website": "https://amaziliahotel.com/",
            "telephone": "310 4019049",
            "address": "CERRITOS, Pereira, Risaralda",
            "email": "",
            "whatsapp": "573104019049",
            "total_reviews": 202,
            "average_rating": 4.5,
            "total_photos": 10,
        }

    def test_has_real_data_true_with_gbp(self):
        """Report with GBP data should show has_real_data=True."""
        md = self.generator.generate(self.hotel_data)
        assert "Datos reales" in md
        assert "✅ Sí" in md
        assert "GBP" in md

    def test_has_real_data_false_without_gbp(self):
        """Report without GBP data should show has_real_data=False."""
        hotel_no_gbp = {"name": "Test Hotel", "website": "https://test.com/"}
        md = self.generator.generate(hotel_no_gbp)
        assert "⚠️ Requiere fuentes adicionales" in md

    def test_total_reviews_populated(self):
        """total_reviews should appear in GBP section."""
        md = self.generator.generate(self.hotel_data)
        assert "202" in md

    def test_average_rating_populated(self):
        """average_rating should appear in GBP section."""
        md = self.generator.generate(self.hotel_data)
        assert "4.5" in md

    def test_total_photos_populated(self):
        """total_photos should appear in GBP section."""
        md = self.generator.generate(self.hotel_data)
        assert "10" in md

    def test_phone_populated(self):
        """phone should appear in contact section."""
        md = self.generator.generate(self.hotel_data)
        assert "310 4019049" in md

    def test_address_populated(self):
        """address should appear in contact section."""
        md = self.generator.generate(self.hotel_data)
        assert "CERRITOS" in md

    def test_no_46_blanks_with_gbp_data(self):
        """Report with GBP data should have fewer blanks than generic template."""
        md_with_data = self.generator.generate(self.hotel_data)
        hotel_generic = {"name": "Generic Hotel"}
        md_generic = self.generator.generate(hotel_generic)
        blank_count_data = md_with_data.count("_____")
        blank_count_generic = md_generic.count("_____")
        assert blank_count_data <= blank_count_generic

    def test_returns_string(self):
        """Generator should return a markdown string."""
        result = self.generator.generate(self.hotel_data)
        assert isinstance(result, str)
        assert len(result) > 500

    def test_markdown_header_present(self):
        """Output should contain markdown header."""
        md = self.generator.generate(self.hotel_data)
        assert "# Informe Mensual de Marketing Digital" in md
