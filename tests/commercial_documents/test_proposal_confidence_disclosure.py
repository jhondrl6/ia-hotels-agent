"""
Tests for the asset quality table of the commercial proposal — current contract.

The table `| Entregable | Momento de entrega | Qué incluye |` (FASE-B) maps each
canonical service (PROPOSAL_SERVICE_TO_ASSET) to its delivery moment according to
confidence_score, with thresholds from regional_benchmarks.yaml
(high 0.85 / medium 0.70 / low 0.40 by default).
"""
import pytest
from modules.asset_generation.proposal_asset_alignment import PROPOSAL_SERVICE_TO_ASSET
from modules.commercial_documents.v4_proposal_generator import V4ProposalGenerator


class TestAssetQualityTable:
    """Tests for _generate_asset_quality_table method."""

    def setup_method(self):
        self.gen = V4ProposalGenerator()

    def test_proposal_includes_quality_table(self):
        """La tabla contiene el header actual y una fila por servicio canónico."""
        table = self.gen._generate_asset_quality_table(None)

        assert "| Entregable | Momento de entrega | Qué incluye |" in table

        for service_name in PROPOSAL_SERVICE_TO_ASSET:
            assert service_name in table, f"Servicio faltante en tabla: {service_name}"

        service_rows = [l for l in table.split("\n") if l.startswith("| ") and "Entregable" not in l]
        assert len(service_rows) == len(PROPOSAL_SERVICE_TO_ASSET)

    def test_quality_table_reflects_real_confidence(self):
        """El momento de entrega sigue los thresholds: >=0.85 Día 1, 0.70-0.85 Semana 1, 0.40-0.70 Semana 2."""
        assets = [
            {"asset_type": "llms_txt", "confidence_score": 0.9},
            {"asset_type": "open_graph", "confidence_score": 0.75},
            {"asset_type": "hotel_schema", "confidence_score": 0.5},
            {"asset_type": "whatsapp_button", "confidence_score": 0.2},
        ]
        table = self.gen._generate_asset_quality_table(assets)
        lines = table.split("\n")

        llms_line = [l for l in lines if "Optimización para IA Generativa" in l][0]
        assert "Día 1 (Activación inicial)" in llms_line
        assert "Listo para implementar" in llms_line

        og_line = [l for l in lines if "Meta Tags Sociales (Open Graph)" in l][0]
        assert "Semana 1 (Con sus datos)" in og_line

        schema_line = [l for l in lines if "Schema Hotel" in l][0]
        assert "Semana 2 (Configuración)" in schema_line

        wa_line = [l for l in lines if "Botón de WhatsApp" in l][0]
        assert "En mejora continua" in wa_line

    def test_missing_asset_shows_preparacion_posterior(self):
        """Si un asset falta en la lista, su fila muestra 'Día 1 (Activación inicial) / Preparacion posterior a la firma'."""
        assets = [
            {"asset_type": "llms_txt", "confidence_score": 0.9},
            {"asset_type": "open_graph", "confidence_score": 0.9},
        ]
        table = self.gen._generate_asset_quality_table(assets)
        lines = table.split("\n")

        schema_line = [l for l in lines if "Schema Hotel" in l][0]
        assert "Día 1 (Activación inicial)" in schema_line
        assert "Preparacion posterior a la firma" in schema_line

        faq_line = [l for l in lines if "Página de FAQ" in l][0]
        assert "Preparacion posterior a la firma" in faq_line

    def test_none_assets_shows_dia_1(self):
        """Si assets_generated es None, todas las filas muestran 'Día 1 (Activación inicial)'."""
        table = self.gen._generate_asset_quality_table(None)
        assert "Día 1 (Activación inicial)" in table
        assert "No generado" not in table
        assert "Preparacion posterior a la firma" in table

    def test_low_confidence_shows_en_mejora_continua(self):
        """Si confidence < low threshold (0.4), muestra 'En mejora continua'."""
        assets = [
            {"asset_type": asset_type, "confidence_score": 0.2}
            for asset_type in PROPOSAL_SERVICE_TO_ASSET.values()
        ]
        table = self.gen._generate_asset_quality_table(assets)
        assert "En mejora continua" in table

        lines = table.split("\n")
        llms_line = [l for l in lines if "Optimización para IA Generativa" in l][0]
        assert "En mejora continua" in llms_line
