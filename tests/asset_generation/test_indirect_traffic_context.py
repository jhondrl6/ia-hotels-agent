"""Tests para FIX-6: indirect_traffic lee audit_context.

Verifica que:
1. Con GBP >1000 reseñas → NO sugiere "reclama tu GBP"
2. Con GBP <10 reseñas → SÍ sugiere optimizar GBP
3. Sin audit_report → funciona normalmente (backward compat)
"""

import json
import os
import tempfile
import pytest
from modules.delivery.generators.indirect_traffic_optimization_gen import (
    IndirectTrafficOptimizationGenerator,
)


class TestIndirectTrafficContext:
    """FIX-6: Audit-aware traffic optimization generator."""

    @pytest.fixture
    def generator(self):
        return IndirectTrafficOptimizationGenerator()

    @pytest.fixture
    def hotel_data(self):
        return {
            "nombre": "Hotel Termales Test",
            "ubicacion": "Santa Rosa de Cabal",
            "website": "https://hoteltermales.com",
        }

    @pytest.fixture
    def audit_high_reviews(self):
        """Audit con GBP establecido y >1000 reseñas."""
        return {
            "google_business_profile": {
                "place_found": True,
                "review_count": 1500,
                "rating": 4.7,
                "place_id": "ChIJ123",
                "name": "Hotel Termales Test",
            },
            "schema": {
                "hotel_schema_detected": True,
                "faq_schema_detected": True,
                "total_schemas": 3,
            },
            "performance": {
                "mobile_score": 85,
                "desktop_score": 92,
            },
        }

    @pytest.fixture
    def audit_low_reviews(self):
        """Audit con GBP sin reseñas."""
        return {
            "google_business_profile": {
                "place_found": True,
                "review_count": 3,
                "rating": 3.5,
            },
            "schema": {
                "hotel_schema_detected": False,
                "faq_schema_detected": False,
                "total_schemas": 0,
            },
            "performance": {
                "mobile_score": 35,
                "desktop_score": 55,
            },
        }

    @pytest.fixture
    def audit_no_gbp(self):
        """Audit sin GBP encontrado."""
        return {
            "google_business_profile": {
                "place_found": False,
                "review_count": 0,
                "rating": 0,
            },
            "schema": {},
            "performance": {},
        }

    def test_high_reviews_no_suggest_reclaim(self, generator, hotel_data, audit_high_reviews):
        """Con GBP >1000 reseñas, NO debe sugerir 'reclama tu GBP'."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(audit_high_reviews, f)
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)

            # Should contain data-driven section
            assert "Diagnostico Data-Driven" in content

            # Should mention established profile
            assert "establecido" in content.lower() or "enfocarse" in content.lower()

            # Should NOT suggest "reclama tu GBP" as critical
            assert "Reclama y verifica tu Google Business Profile" not in content

        finally:
            os.unlink(audit_path)

    def test_low_reviews_suggests_promotion(self, generator, hotel_data, audit_low_reviews):
        """Con GBP <10 reseñas, debe sugerir acciones de promoción."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(audit_low_reviews, f)
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)

            assert "Diagnostico Data-Driven" in content

            # Should mention low reviews / need for promotion
            assert any(
                phrase in content.lower()
                for phrase in ["incentiva", "reseñas", "promoción", "promocion"]
            )

            # Should mention missing schemas
            assert "Hotel schema" in content or "Esquema" in content

        finally:
            os.unlink(audit_path)

    def test_no_gbp_suggests_reclaim(self, generator, hotel_data, audit_no_gbp):
        """Sin GBP encontrado, debe sugerir reclamar."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(audit_no_gbp, f)
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)

            assert "Diagnostico Data-Driven" in content
            assert "Reclama y verifica tu Google Business Profile" in content

        finally:
            os.unlink(audit_path)

    def test_no_audit_path_backward_compat(self, generator, hotel_data):
        """Sin audit_report_path, debe funcionar como antes (backward compat)."""
        content = generator.generate(hotel_data, audit_report_path=None)

        # Should still produce content
        assert len(content) > 0
        assert "Hotel Termales Test" in content or "tu hotel" in content

        # Should NOT have data-driven section
        assert "Diagnostico Data-Driven" not in content

    def test_invalid_audit_path_handled(self, generator, hotel_data):
        """Path inválido no debe causar error."""
        content = generator.generate(
            hotel_data, audit_report_path="/nonexistent/path.json"
        )

        assert len(content) > 0
        # No crash, no data-driven section
        assert "Diagnostico Data-Driven" not in content

    def test_invalid_json_handled(self, generator, hotel_data):
        """JSON inválido no debe causar error."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write("not valid json {{{")
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)
            assert len(content) > 0
            assert "Diagnostico Data-Driven" not in content
        finally:
            os.unlink(audit_path)

    def test_prioritized_actions_critical_first(self, generator, hotel_data, audit_low_reviews):
        """Acciones prioritarias deben empezar con las críticas."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(audit_low_reviews, f)
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)

            assert "Acciones Prioritarias" in content

            # Should have critical items with [Crítico] tag
            assert "[Crítico]" in content or "[Critico]" in content

        finally:
            os.unlink(audit_path)

    def test_mobile_performance_warning(self, generator, hotel_data, audit_low_reviews):
        """Mobile score <50 debe generar advertencia de rendimiento."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(audit_low_reviews, f)
            audit_path = f.name

        try:
            content = generator.generate(hotel_data, audit_report_path=audit_path)

            # Should mention mobile performance issue
            assert "mobile" in content.lower()
            assert "35" in content  # mobile_score from fixture

        finally:
            os.unlink(audit_path)
