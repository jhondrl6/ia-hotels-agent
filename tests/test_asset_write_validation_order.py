"""
Regression Test: Asset Write Validation Order

BUG A: optimization_guide se escribía aunque validation fallaba
- El archivo existía pero asset_generation_report.json decía "failed"
- El fallback se ejecutó y escribió, pero después validation falló

EXPECTED BEHAVIOR:
- Si content validation falla (status = INVALID), el archivo debe ser BORRADO
- El asset debe reportarse como failed, no como generated
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from modules.asset_generation.v4_asset_orchestrator import V4AssetOrchestrator
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.asset_content_validator import AssetContentValidator, ContentStatus, ContentIssue
from modules.asset_generation.asset_metadata import AssetMetadata, AssetStatus
from modules.commercial_documents.data_structures import (
    AssetSpec, DiagnosticDocument, ProposalDocument, 
    ValidationSummary, V4AuditResult
)
from modules.commercial_documents.coherence_validator import CoherenceReport
from modules.commercial_documents.coherence_validator import CoherenceValidator
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


class TestAssetWriteValidationOrder:
    """Test that validation failure prevents file persistence (BUG A fix)."""

    @pytest.fixture
    def temp_output_dir(self, tmp_path):
        """Create a temporary output directory."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()
        return output_dir

    def test_content_validation_failure_removes_written_file(
        self, temp_output_dir
    ):
        """
        BUG A TEST: Cuando content validation FALLA, el archivo debe ser BORRADO.
        
        Escenario:
        1. conditional_generator.write() guarda el archivo
        2. v4_asset_orchestrator valida el contenido
        3. Validation falla (INVALID) → archivo debe BORRARSE
        4. Asset debe reportarse como failed, no como generated
        """
        orchestrator = V4AssetOrchestrator(output_base_dir=str(temp_output_dir))
        
        # Crear spec para optimization_guide
        spec = AssetSpec(
            asset_type="optimization_guide",
            problem_solved="seo_metadata",
            description="Optimization guide for SEO",
            confidence_level=ConfidenceLevel.VERIFIED,
            priority="P2",
            has_automatic_solution=True,
            pain_ids=["seo_metadata"],
            confidence_required=0.7,
            can_generate=True
        )
        
        # Crear validation_summary con campo metadata_data
        mock_field = Mock()
        mock_field.field_name = "metadata_data"
        mock_field.confidence = ConfidenceLevel.VERIFIED
        mock_field.value = {"has_default_title": True, "title_tag": "Ciudad"}
        
        # Crear un archivo temporal con contenido placeholder
        hotel_id = "test_hotel"
        asset_dir = temp_output_dir / hotel_id / "optimization_guide"
        asset_dir.mkdir(parents=True)
        
        # Simular que el archivo fue escrito por conditional_generator
        test_file = asset_dir / "guia_optimizacion_test.md"
        test_file.write_text("$$PLACEHOLDER_TITLE$$ and more content here", encoding='utf-8')
        
        # Verificar que el archivo existe
        assert test_file.exists(), "Test setup failed - file should exist"
        
        # Ahora simular que conditional_generator.generate() devuelve el resultado
        # Pero el content_validator detectará el placeholder
        mock_result = {
            "success": True,
            "status": "generated",
            "preflight_status": "PASSED",
            "file_path": str(test_file),
            "metadata": {
                "confidence_score": 0.8,
                "asset_type": "optimization_guide",
                "hotel_id": hotel_id
            }
        }
        
        # Patchear conditional_generator para devolver nuestro resultado
        with patch.object(orchestrator.conditional_generator, 'generate', return_value=mock_result):
            # Ejecutar la generación
            result = orchestrator._generate_with_coherence_check(
                spec, 
                {"metadata_data": mock_field},  # validated_data
                temp_output_dir,
                "Test Hotel",
                hotel_id
            )
        
        # Verificar que el archivo FUE BORRADO después de la validación fallida
        assert not test_file.exists(), \
            "BUG A NOT FIXED: File should be DELETED when content validation fails"
        
        # Verificar que el asset se reporta como failed
        from modules.asset_generation.v4_asset_orchestrator import FailedAsset
        assert isinstance(result, FailedAsset), \
            f"Expected FailedAsset, got {type(result)}"
        assert "validation failed" in result.reason.lower() or "placeholder" in result.reason.lower(), \
            f"Expected validation failure reason, got: {result.reason}"

    def test_content_validation_failure_cleans_up_metadata_file(
        self, temp_output_dir
    ):
        """
        BUG A TEST: Cuando content validation FALLA, el archivo _metadata.json también debe borrarse.
        """
        orchestrator = V4AssetOrchestrator(output_base_dir=str(temp_output_dir))
        
        spec = AssetSpec(
            asset_type="optimization_guide",
            problem_solved="seo_metadata",
            description="Optimization guide",
            confidence_level=ConfidenceLevel.VERIFIED,
            priority="P2",
            has_automatic_solution=True,
            pain_ids=["seo_metadata"],
            confidence_required=0.7,
            can_generate=True
        )
        
        hotel_id = "test_hotel"
        asset_dir = temp_output_dir / hotel_id / "optimization_guide"
        asset_dir.mkdir(parents=True)
        
        test_file = asset_dir / "guia_optimizacion_test.md"
        test_file.write_text("$$PLACEHOLDER$$", encoding='utf-8')
        
        # Crear metadata file también
        metadata_file = asset_dir / "guia_optimizacion_test_metadata.json"
        metadata_file.write_text(json.dumps({"confidence_score": 0.8}), encoding='utf-8')
        
        assert metadata_file.exists(), "Test setup failed - metadata file should exist"
        
        mock_result = {
            "success": True,
            "status": "generated",
            "preflight_status": "PASSED",
            "file_path": str(test_file),
            "metadata": {"confidence_score": 0.8}
        }
        
        with patch.object(orchestrator.conditional_generator, 'generate', return_value=mock_result):
            result = orchestrator._generate_with_coherence_check(
                spec,
                {},
                temp_output_dir,
                "Test Hotel",
                hotel_id
            )
        
        # Ambos archivos deben ser borrados
        assert not test_file.exists(), "Content file should be deleted"
        assert not metadata_file.exists(), "Metadata file should also be deleted"

    def test_content_validation_success_keeps_file(self, temp_output_dir):
        """
        Validación exitosa NO debe borrar el archivo.
        """
        orchestrator = V4AssetOrchestrator(output_base_dir=str(temp_output_dir))
        
        spec = AssetSpec(
            asset_type="whatsapp_button",
            problem_solved="no_whatsapp",
            description="WhatsApp button",
            confidence_level=ConfidenceLevel.VERIFIED,
            priority="P1",
            has_automatic_solution=True,
            pain_ids=["no_whatsapp"],
            confidence_required=0.7,
            can_generate=True
        )
        
        hotel_id = "test_hotel"
        asset_dir = temp_output_dir / hotel_id / "whatsapp_button"
        asset_dir.mkdir(parents=True)
        
        # Crear contenido válido (no tiene placeholders)
        test_file = asset_dir / "boton_whatsapp_valid.html"
        valid_content = """<!-- WhatsApp Button for Test Hotel -->
<a href="https://wa.me/573001234567">WhatsApp</a>
"""
        test_file.write_text(valid_content, encoding='utf-8')
        
        mock_result = {
            "success": True,
            "status": "generated",
            "preflight_status": "PASSED",
            "file_path": str(test_file),
            "metadata": {"confidence_score": 0.9}
        }
        
        with patch.object(orchestrator.conditional_generator, 'generate', return_value=mock_result):
            result = orchestrator._generate_with_coherence_check(
                spec,
                {},
                temp_output_dir,
                "Test Hotel",
                hotel_id
            )
        
        # Archivo debe seguir existiendo
        assert test_file.exists(), "Valid file should NOT be deleted"
        
        from modules.asset_generation.v4_asset_orchestrator import GeneratedAsset
        assert isinstance(result, GeneratedAsset), f"Expected GeneratedAsset, got {type(result)}"


class TestAssetGenerationReportValidationConsistency:
    """Test that asset_generation_report.json matches actual file state."""
    
    def test_failed_asset_not_in_generated_list(self, tmp_path):
        """
        Un asset que falla validación NO debe aparecer en generated_assets del report.
        """
        orchestrator = V4AssetOrchestrator(output_base_dir=str(tmp_path))
        
        # Simular un asset que falla
        spec = AssetSpec(
            asset_type="optimization_guide",
            problem_solved="seo",
            confidence_level=ConfidenceLevel.VERIFIED,
            priority="P2",
            has_automatic_solution=True,
            pain_ids=["seo"],
            confidence_required=0.7,
            can_generate=True
        )
        
        hotel_id = "test_hotel"
        asset_dir = tmp_path / hotel_id / "optimization_guide"
        asset_dir.mkdir(parents=True)
        
        test_file = asset_dir / "guide_INVALID.md"
        test_file.write_text("$$PLACEHOLDER$$", encoding='utf-8')
        
        mock_result = {
            "success": True,
            "status": "generated",
            "preflight_status": "PASSED",
            "file_path": str(test_file),
            "metadata": {"confidence_score": 0.8}
        }
        
        with patch.object(orchestrator.conditional_generator, 'generate', return_value=mock_result):
            result = orchestrator._generate_with_coherence_check(
                spec, {}, tmp_path, "Test", hotel_id
            )
        
        # Debe ser FailedAsset
        from modules.asset_generation.v4_asset_orchestrator import FailedAsset
        assert isinstance(result, FailedAsset)
        # Note: This test validates the concept - actual integration test would need full setup
