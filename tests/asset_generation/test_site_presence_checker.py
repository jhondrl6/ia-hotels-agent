"""
Test SitePresenceChecker - FASE-CAUSAL-01

Verifica que el sistema ahora:
1. Verifica sitio real ANTES de generar assets
2. Skip assets que ya existen en producción
3. No regenera sin necesidad

Ejecutar con:
    pytest tests/asset_generation/test_site_presence_checker.py -v
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from datetime import datetime

import sys
import os
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.asset_generation.site_presence_checker import (
    SitePresenceChecker,
    SitePresenceReport,
    PresenceCheckResult,
    PresenceStatus,
    check_before_generate
)


class TestSitePresenceChecker:
    """Tests para SitePresenceChecker."""
    
    def test_presence_status_enum(self):
        """Verificar que PresenceStatus tiene los valores correctos."""
        assert PresenceStatus.EXISTS.value == "exists"
        assert PresenceStatus.NOT_EXISTS.value == "not_exists"
        assert PresenceStatus.REDUNDANT.value == "redundant"
        assert PresenceStatus.VERIFICATION_FAILED.value == "verification_failed"
    
    def test_presence_check_result_should_generate(self):
        """Verificar lógica should_generate."""
        # EXISTS → no generar
        result = PresenceCheckResult(
            asset_type="faq_page",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com"
        )
        assert result.should_generate is False
        
        # NOT_EXISTS → sí generar
        result = PresenceCheckResult(
            asset_type="faq_page",
            status=PresenceStatus.NOT_EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com"
        )
        assert result.should_generate is True
        
        # REDUNDANT → no generar (ya existe y fue entregado)
        result = PresenceCheckResult(
            asset_type="faq_page",
            status=PresenceStatus.REDUNDANT,
            verified_at=datetime.now(),
            site_url="https://example.com"
        )
        assert result.should_generate is False
    
    def test_skip_reason_for_exists(self):
        """Verificar skip_reason cuando asset ya existe."""
        result = PresenceCheckResult(
            asset_type="faq_page",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com",
            details={"schema_type": "FAQPage"}
        )
        assert "ya implementado" in result.skip_reason
    
    def test_site_presence_report_get_assets_to_generate(self):
        """Verificar get_assets_to_generate()."""
        report = SitePresenceReport(
            site_url="https://example.com",
            checked_at=datetime.now(),
            results={
                "faq_page": PresenceCheckResult(
                    asset_type="faq_page",
                    status=PresenceStatus.EXISTS,
                    verified_at=datetime.now(),
                    site_url="https://example.com"
                ),
                "hotel_schema": PresenceCheckResult(
                    asset_type="hotel_schema",
                    status=PresenceStatus.NOT_EXISTS,
                    verified_at=datetime.now(),
                    site_url="https://example.com"
                ),
            }
        )
        
        to_generate = report.get_assets_to_generate()
        assert "hotel_schema" in to_generate
        assert "faq_page" not in to_generate
    
    def test_site_presence_report_delivery_readiness_score(self):
        """Verificar scoring de readiness."""
        report = SitePresenceReport(
            site_url="https://example.com",
            checked_at=datetime.now(),
            results={
                "faq_page": PresenceCheckResult(
                    asset_type="faq_page",
                    status=PresenceStatus.EXISTS,  # Existe → no cuenta como needed
                    verified_at=datetime.now(),
                    site_url="https://example.com"
                ),
                "hotel_schema": PresenceCheckResult(
                    asset_type="hotel_schema",
                    status=PresenceStatus.NOT_EXISTS,  # No existe → needed
                    verified_at=datetime.now(),
                    site_url="https://example.com"
                ),
                "org_schema": PresenceCheckResult(
                    asset_type="org_schema",
                    status=PresenceStatus.NOT_EXISTS,  # No existe → needed
                    verified_at=datetime.now(),
                    site_url="https://example.com"
                ),
            }
        )
        
        # 2 de 3 son needed
        score = report.get_delivery_readiness_score()
        assert score == 2/3


class TestSitePresenceCheckerIntegration:
    """Tests de integración con ConditionalGenerator."""
    
    @patch('modules.asset_generation.site_presence_checker.SchemaFinder')
    def test_check_asset_when_schema_exists(self, mock_schema_finder):
        """Si el sitio YA tiene schema, debe devolver EXISTS."""
        mock_schema_finder.return_value.analyze.return_value = {
            "schemas_encontrados": [
                {"type": "FAQPage", "data": {"name": "Test"}}
            ],
            "campos_faltantes": [],
            "error": None
        }
        
        checker = SitePresenceChecker()
        result = checker._check_asset_presence(
            "faq_page",
            "https://example.com",
            {"schemas_encontrados": [{"type": "FAQPage", "data": {}}]}
        )
        
        assert result.status == PresenceStatus.EXISTS
        assert result.should_generate is False
    
    @patch('modules.asset_generation.site_presence_checker.SchemaFinder')
    def test_check_asset_when_schema_not_exists(self, mock_schema_finder):
        """Si el sitio NO tiene schema, debe devolver NOT_EXISTS."""
        mock_schema_finder.return_value.analyze.return_value = {
            "schemas_encontrados": [],
            "campos_faltantes": ["FAQPage"],
            "error": None
        }
        
        checker = SitePresenceChecker()
        result = checker._check_asset_presence(
            "faq_page",
            "https://example.com",
            {"schemas_encontrados": []}
        )
        
        assert result.status == PresenceStatus.NOT_EXISTS
        assert result.should_generate is True


class TestConditionalGeneratorWithSiteCheck:
    """Tests de integración ConditionalGenerator + SitePresenceChecker."""
    
    @patch('modules.asset_generation.site_presence_checker.SitePresenceChecker')
    def test_generate_skips_when_asset_exists(self, mock_checker_class):
        """Verificar que generate() hace SKIP si site_url indica que ya existe."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        # Crear mock del presence result
        mock_presence_result = Mock()
        mock_presence_result.should_generate = False
        mock_presence_result.skip_reason = "Asset ya implementado en sitio de producción"
        mock_presence_result.status = PresenceStatus.EXISTS
        mock_presence_result.details = {"schema_type": "FAQPage"}
        mock_presence_result.recommendations = []
        
        mock_checker_class.return_value.get_full_presence_decision.return_value = mock_presence_result
        
        gen = ConditionalGenerator()
        gen.site_checker = mock_checker_class.return_value
        
        result = gen.generate(
            asset_type="faq_page",
            validated_data={},
            hotel_name="Hotel Visperas",
            hotel_id="hotelvisperas",
            site_url="https://hotelvisperas.com"
        )
        
        assert result["status"] == "skipped"
        assert result["can_use"] is False
        assert "ya implementado" in result["skip_reason"]
    
    @patch('modules.asset_generation.site_presence_checker.SitePresenceChecker')
    def test_generate_proceeds_when_asset_not_exists(self, mock_checker_class):
        """Verificar que generate() procede si site_url indica que NO existe."""
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        # Crear mock del presence result - NOT_EXISTS
        mock_presence_result = Mock()
        mock_presence_result.should_generate = True
        mock_presence_result.status = PresenceStatus.NOT_EXISTS
        mock_presence_result.skip_reason = None
        mock_presence_result.details = {}
        mock_presence_result.recommendations = []
        
        mock_checker_class.return_value.get_full_presence_decision.return_value = mock_presence_result
        
        gen = ConditionalGenerator()
        gen.site_checker = mock_checker_class.return_value
        
        # Como NOT_EXISTS, debería proceder pero fallar porque no hay datos
        result = gen.generate(
            asset_type="hotel_schema",
            validated_data={},  # Sin datos válidos
            hotel_name="New Hotel",
            hotel_id="newhotel",
            site_url="https://new-hotel.com"
        )
        
        # Debe proceder (no es skipped), aunque puede bloquear por falta de datos
        assert result.get("status") != "skipped"


class TestCheckBeforeGenerateHelper:
    """Tests para la función helper check_before_generate."""
    
    @patch('modules.asset_generation.site_presence_checker.SitePresenceChecker')
    def test_check_before_generate_helper(self, mock_checker_class):
        """Verificar función helper."""
        mock_presence_result = PresenceCheckResult(
            asset_type="faq_page",
            status=PresenceStatus.EXISTS,
            verified_at=datetime.now(),
            site_url="https://example.com"
        )
        
        mock_checker_class.return_value.get_full_presence_decision.return_value = mock_presence_result
        
        should_generate, result = check_before_generate(
            "https://example.com",
            "testhotel",
            "faq_page"
        )
        
        assert should_generate is False
        assert result.status == PresenceStatus.EXISTS


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
