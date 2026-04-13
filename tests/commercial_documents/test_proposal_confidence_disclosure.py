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
            "Visibilidad en ChatGPT",
            "Busqueda por Voz",
            "SEO Local",
            "Boton de WhatsApp",
            "Datos Estructurados",
            "Informe Mensual",
        ]
        for service in expected_services:
            assert service in table, f"Servicio faltante en tabla: {service}"

    def test_quality_table_reflects_real_confidence(self):
        """Si hotel_schema tiene confidence 0.5, muestra 'Requiere datos'."""
        assets = [
            {"asset_type": "hotel_schema", "confidence_score": 0.5},
            {"asset_type": "geo_playbook", "confidence_score": 0.9},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "voice_assistant_guide", "confidence_score": 0.7},
            {"asset_type": "optimization_guide", "confidence_score": 0.85},
            {"asset_type": "whatsapp_button", "confidence_score": 0.6},
            {"asset_type": "monthly_report", "confidence_score": 0.75},
        ]
        table = self.gen._generate_asset_quality_table(assets)

        # hotel_schema (0.5) → "Requiere datos"
        assert "Requiere datos" in table
        # geo_playbook (0.9) → "Completo"
        assert "Completo" in table

        # Verify specific mapping
        lines = table.split("\n")
        schema_line = [l for l in lines if "Datos Estructurados" in l][0]
        assert "Requiere datos" in schema_line

        geo_line = [l for l in lines if "Google Maps Optimizado" in l][0]
        assert "Completo" in geo_line

    def test_missing_asset_shows_not_generated(self):
        """Si un asset falta en la lista, muestra 'No generado'."""
        # Only pass 5 of 7 assets
        assets = [
            {"asset_type": "geo_playbook", "confidence_score": 0.8},
            {"asset_type": "indirect_traffic_optimization", "confidence_score": 0.8},
            {"asset_type": "voice_assistant_guide", "confidence_score": 0.8},
            {"asset_type": "optimization_guide", "confidence_score": 0.8},
            {"asset_type": "whatsapp_button", "confidence_score": 0.8},
        ]
        table = self.gen._generate_asset_quality_table(assets)

        # hotel_schema and monthly_report are missing → "No generado"
        lines = table.split("\n")
        schema_line = [l for l in lines if "Datos Estructurados" in l][0]
        assert "No generado" in schema_line

        report_line = [l for l in lines if "Informe Mensual" in l][0]
        assert "No generado" in report_line

    def test_none_assets_shows_pending(self):
        """Si assets_generated es None, todos muestran 'Pendiente'."""
        table = self.gen._generate_asset_quality_table(None)
        assert "Pendiente" in table
        assert "No generado" not in table

    def test_low_confidence_shows_en_desarrollo(self):
        """Si confidence < 0.4, muestra 'En desarrollo'."""
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
        assert "En desarrollo" in table
