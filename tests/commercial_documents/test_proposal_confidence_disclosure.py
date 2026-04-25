"""
Tests for FASE-CONFIDENCE-DISCLOSURE: quality table in commercial proposal.

Verifies that the proposal includes an asset quality table that reflects
real confidence scores and handles missing assets correctly.
"""
import pytest
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


class TestAssetQualityTable:
    """Tests for _generate_asset_quality_table method."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_proposal_includes_quality_table(self):
        """La tabla generada contiene header y filas para los 7 servicios."""
        table = self.gen._generate_asset_quality_table(None)

        # Must have header
        assert "| Entregable |" in table
        assert "| Nivel |" in table
        assert "| Que significa |" in table

        # Must have all 7 services from PROPOSAL_SERVICE_TO_ASSET
        expected_services = [
            "Google Maps Optimizado",
            "SEO Local",
            "Botón de WhatsApp",
            "Datos Estructurados",
            "Informe Mensual",
            "Página de FAQ",
            "Meta Tags Sociales (Open Graph)",
        ]
        for service in expected_services:
            assert service in table, f"Servicio faltante en tabla: {service}"

    def test_quality_table_reflects_real_confidence(self):
        """Si hotel_schema tiene confidence 0.5, muestra 'En preparacion'."""
        assets = [
            {"asset_type": "hotel_schema", "confidence_score": 0.5},
            {"asset_type": "geo_playbook", "confidence_score": 0.9},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.85},
            {"asset_type": "whatsapp_button", "confidence_score": 0.6},
            {"asset_type": "monthly_report", "confidence_score": 0.75},
        ]
        table = self.gen._generate_asset_quality_table(assets)

        # FASE-C: "En preparacion" en lugar de "Requiere datos"
        assert "En preparacion" in table
        # geo_playbook (0.9) → "Completo"
        assert "Completo" in table

        # Verify specific mapping
        lines = table.split("\n")
        schema_line = [l for l in lines if "Datos Estructurados" in l][0]
        # FASE-C: confidence 0.5 >= 0.4 → "En preparacion"
        assert "En preparacion" in schema_line

        geo_line = [l for l in lines if "Google Maps Optimizado" in l][0]
        assert "Completo" in geo_line

    def test_missing_asset_shows_incluido_en_su_kit(self):
        """FASE-C: Si un asset falta en la lista, muestra 'Incluido en su kit' (no 'No generado')."""
        # Only pass 5 of 7 assets
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "voice_assistant_guide", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
        ]
        table = self.gen._generate_asset_quality_table(assets)

        # FASE-C: "Incluido en su kit" en lugar de "No generado"
        lines = table.split("\n")
        schema_line = [l for l in lines if "Datos Estructurados" in l][0]
        assert "Incluido en su kit" in schema_line

        report_line = [l for l in lines if "Informe Mensual" in l][0]
        assert "Incluido en su kit" in report_line

    def test_none_assets_shows_incluido_en_su_kit(self):
        """FASE-C: Si assets_generated es None, todos muestran 'Incluido en su kit'."""
        table = self.gen._generate_asset_quality_table(None)
        # FASE-C: "Incluido en su kit" en lugar de "Pendiente"
        assert "Incluido en su kit" in table
        assert "No generado" not in table

    def test_low_confidence_shows_en_optimizacion(self):
        """FASE-C: Si confidence < 0.4, muestra 'En optimizacion'."""
        assets = [
            {"asset_type": "hotel_schema", "confidence_score": 0.2},
            {"asset_type": "geo_playbook", "confidence_score": 0.2},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.2},
            {"asset_type": "voice_assistant_guide", "confidence_score": 0.2},
            {"asset_type": "optimization_guide", "confidence_score": 0.2},
            {"asset_type": "whatsapp_button", "confidence_score": 0.2},
            {"asset_type": "monthly_report", "confidence_score": 0.2},
        ]
        table = self.gen._generate_asset_quality_table(assets)
        # FASE-C: "En optimizacion" en lugar de "En desarrollo"
        assert "En optimizacion" in table
