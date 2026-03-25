"""
Regression Test: Confidence Score Consistency

BUG B: confidence_score siempre 0.5 en asset_generation_report
- geo_playbook metadata dice 0.7 pero report dice 0.5
- Los scores no se estaban leyendo correctamente

EXPECTED BEHAVIOR:
- confidence_score en report = confidence en metadata para todos los assets
- El score original del conditional_generator debe preservarse hasta el report
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime

from modules.asset_generation.v4_asset_orchestrator import (
    V4AssetOrchestrator, GeneratedAsset, AssetGenerationResult
)
from modules.asset_generation.asset_diagnostic_linker import (
    AssetDiagnosticLinker, AssetMetadata
)
from modules.commercial_documents.data_structures import AssetSpec, DiagnosticDocument
from modules.commercial_documents.coherence_validator import CoherenceReport
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


class TestConfidenceScoreConsistency:
    """Test that confidence_score is correctly propagated from metadata to report."""

    @pytest.fixture
    def mock_coherence_report(self):
        """Create a mock CoherenceReport."""
        report = Mock(spec=CoherenceReport)
        report.overall_score = 0.85
        report.is_coherent = True
        report.to_dict = Mock(return_value={
            "overall_score": 0.85,
            "is_coherent": True,
            "details": {}
        })
        return report

    @pytest.fixture
    def mock_diagnostic_doc(self):
        """Create a mock DiagnosticDocument."""
        doc = Mock(spec=DiagnosticDocument)
        doc.path = "/tmp/diagnostic.json"
        
        # Crear problemas mock
        problem = Mock()
        problem.id = "low_gbp_score"
        problem.name = "Bajo Score GBP"
        problem.description = "Google Business Profile con score bajo"
        doc.problems = [problem]
        return doc

    def test_confidence_score_preserved_in_generated_asset(self):
        """
        BUG B TEST: El confidence_score del metadata original debe preservarse.
        
        Escenario:
        1. conditional_generator genera asset con confidence_score = 0.7
        2. v4_asset_orchestrator procesa el asset
        3. AssetMetadata se crea/sobrescribe en diagnostic_linker
        4. Report final debe tener confidence_score = 0.7 (no 0.5)
        """
        # Crear un GeneratedAsset con confidence_score conocido
        asset = GeneratedAsset(
            asset_type="geo_playbook",
            filename="geo_playbook_20231015.html",
            path="/tmp/hotel/geo_playbook/geo_playbook_20231015.html",
            metadata_path="/tmp/hotel/geo_playbook/geo_playbook_20231015_metadata.json",
            preflight_status="PASSED",
            confidence_score=0.7,  # Valor original del conditional_generator
            pain_ids_resolved=["low_gbp_score"],
            can_use=True,
            delivery_filename="geo_playbook.html"
        )
        
        # Verificar que el asset tiene el score correcto
        assert asset.confidence_score == 0.7

    def test_confidence_score_from_metadata_to_report(self):
        """
        BUG B TEST: El confidence_score debe transmitirse correctamente al report.
        
        El flujo es:
        conditional_generator → metadata → GeneratedAsset → AssetGenerationResult → report.json
        """
        # Crear orchestrator
        orchestrator = V4AssetOrchestrator(output_base_dir="/tmp/test_output")
        
        # Mockear los componentes
        with patch.object(orchestrator.conditional_generator, 'generate') as mock_gen:
            # Simular que conditional_generator devuelve 0.7
            mock_gen.return_value = {
                "success": True,
                "status": "generated",
                "preflight_status": "PASSED",
                "file_path": "/tmp/test_hotel/geo_playbook/test.md",
                "metadata": {
                    "confidence_score": 0.7,  # <-- Este valor debe llegar al report
                    "asset_type": "geo_playbook",
                    "hotel_id": "test_hotel"
                }
            }
            
            # Ejecutar
            result = orchestrator._generate_with_coherence_check(
                asset_spec=AssetSpec(
                    asset_type="geo_playbook",
                    problem_solved="low_gbp_score",
                    confidence_level=ConfidenceLevel.VERIFIED,
                    priority="P1",
                    has_automatic_solution=True,
                    pain_ids=["low_gbp_score"],
                    confidence_required=0.7,
                    can_generate=True
                ),
                validated_data={},
                output_dir=Path("/tmp/test_output"),
                hotel_name="Test Hotel",
                hotel_id="test_hotel"
            )
        
        # Verificar que el confidence_score se preservó
        assert isinstance(result, GeneratedAsset)
        assert result.confidence_score == 0.7, \
            f"BUG B NOT FIXED: Expected 0.7, got {result.confidence_score}"

    def test_confidence_score_different_values_for_different_assets(self):
        """
        BUG B TEST: Verificar que diferentes scores se preservan correctamente.
        """
        orchestrator = V4AssetOrchestrator(output_base_dir="/tmp/test_output")
        
        test_cases = [
            ("whatsapp_button", 0.9),
            ("faq_page", 0.85),
            ("geo_playbook", 0.7),
            ("hotel_schema", 0.75),
            ("financial_projection", 0.6),
        ]
        
        for asset_type, expected_score in test_cases:
            with patch.object(orchestrator.conditional_generator, 'generate') as mock_gen:
                mock_gen.return_value = {
                    "success": True,
                    "status": "generated",
                    "preflight_status": "PASSED",
                    "file_path": f"/tmp/test/{asset_type}/test.md",
                    "metadata": {
                        "confidence_score": expected_score,
                        "asset_type": asset_type
                    }
                }
                
                result = orchestrator._generate_with_coherence_check(
                    asset_spec=AssetSpec(
                        asset_type=asset_type,
                        problem_solved="test",
                        confidence_level=ConfidenceLevel.VERIFIED,
                        priority="P1",
                        has_automatic_solution=True,
                        pain_ids=["test"],
                        confidence_required=0.7,
                        can_generate=True
                    ),
                    validated_data={},
                    output_dir=Path("/tmp/test_output"),
                    hotel_name="Test",
                    hotel_id="test"
                )
                
                assert isinstance(result, GeneratedAsset)
                assert result.confidence_score == expected_score, \
                    f"Bug B: {asset_type} expected {expected_score}, got {result.confidence_score}"

    def test_metadata_enrichment_preserves_confidence_score(self):
        """
        BUG B TEST: enrich_asset_metadata debe preservar el confidence_score original.
        """
        linker = AssetDiagnosticLinker()
        
        # Score original del conditional_generator
        original_score = 0.7
        
        # Enrich la metadata pasando el score original
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="low_gbp_score",
                confidence_level=ConfidenceLevel.VERIFIED,
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["low_gbp_score"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8),
            original_confidence_score=original_score  # <-- Passing original score
        )
        
        # Verificar que el score se preservó
        assert enriched.confidence_score == original_score, \
            f"Expected {original_score}, got {enriched.confidence_score}"

    def test_metadata_to_dict_includes_confidence_score(self):
        """
        BUG B TEST: to_dict() debe incluir confidence_score.
        """
        linker = AssetDiagnosticLinker()
        
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="test",
                confidence_level=ConfidenceLevel.VERIFIED,
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["test"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8),
            original_confidence_score=0.75
        )
        
        # Convertir a dict
        as_dict = enriched.to_dict()
        
        # Verificar que confidence_score está en el dict
        assert "confidence_score" in as_dict, \
            "confidence_score missing from to_dict() output"
        assert as_dict["confidence_score"] == 0.75, \
            f"Expected 0.75 in dict, got {as_dict['confidence_score']}"

    def test_asset_generation_result_to_dict_includes_confidence_score(self):
        """
        BUG B TEST: AssetGenerationResult.to_dict() debe incluir confidence_score.
        """
        # Crear GeneratedAsset con score conocido
        asset = GeneratedAsset(
            asset_type="geo_playbook",
            filename="test.md",
            path="/tmp/test.md",
            metadata_path="/tmp/test_metadata.json",
            preflight_status="PASSED",
            confidence_score=0.7,  # <-- Valor específico
            pain_ids_resolved=["test"],
            can_use=True
        )
        
        # Crear AssetGenerationResult
        result = AssetGenerationResult(
            hotel_id="test_hotel",
            hotel_name="Test Hotel",
            generated_assets=[asset],
            failed_assets=[],
            coherence_report=Mock(overall_score=0.85, is_coherent=True, to_dict=lambda: {}),
            output_dir="/tmp/output",
            timestamp=datetime.now().isoformat()
        )
        
        # Convertir a dict
        as_dict = result.to_dict()
        
        # Verificar que los generated_assets tienen confidence_score
        assert "generated_assets" in as_dict
        assert len(as_dict["generated_assets"]) == 1
        
        asset_dict = as_dict["generated_assets"][0]
        assert "confidence_score" in asset_dict, \
            "confidence_score missing from generated_assets in report"
        assert asset_dict["confidence_score"] == 0.7, \
            f"Expected 0.7, got {asset_dict['confidence_score']}"


class TestConfidenceScoreDefaultBehavior:
    """Test default confidence_score behavior when not explicitly provided."""

    def test_enrich_without_score_uses_default_derivation(self):
        """
        Cuando no se pasa original_confidence_score, debe derivarse del confidence_level.
        """
        linker = AssetDiagnosticLinker()
        
        # Sin pasar original_confidence_score (default 0.0)
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="test",
                confidence_level="VERIFIED",  # Pass as string → 0.9
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["test"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8)
            # No se pasa original_confidence_score
        )
        
        # Debe derivar 0.9 de VERIFIED
        assert enriched.confidence_score == 0.9

    def test_enrich_with_estimated_derives_06(self):
        """ESTIMATED → 0.6"""
        linker = AssetDiagnosticLinker()
        
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="test",
                confidence_level="ESTIMATED",  # Pass as string, not enum
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["test"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8)
        )
        
        assert enriched.confidence_score == 0.6

    def test_enrich_with_conflict_derives_03(self):
        """CONFLICT → 0.3"""
        linker = AssetDiagnosticLinker()
        
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="test",
                confidence_level="CONFLICT",  # Pass as string, not enum
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["test"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8)
        )
        
        assert enriched.confidence_score == 0.3

    def test_enrich_with_unknown_derives_05(self):
        """UNKNOWN → 0.5"""
        linker = AssetDiagnosticLinker()
        
        enriched = linker.enrich_asset_metadata(
            base_metadata={},
            asset_spec=AssetSpec(
                asset_type="geo_playbook",
                problem_solved="test",
                confidence_level=ConfidenceLevel.UNKNOWN,  # → 0.5
                priority="P1",
                has_automatic_solution=True,
                pain_ids=["test"],
                confidence_required=0.7,
                can_generate=True
            ),
            diagnostic_doc=Mock(path="/tmp/diag.json", problems=[]),
            coherence_report=Mock(overall_score=0.8)
        )
        
        assert enriched.confidence_score == 0.5
