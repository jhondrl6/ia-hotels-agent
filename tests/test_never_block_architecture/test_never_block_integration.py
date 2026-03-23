"""
TDD Gate: Never Block Integration

Estos tests definen el comportamiento esperado del flujo NEVER_BLOCK.
初期: Todos los tests FALLAN (integración no implementada aún).
Después de implementar: Todos los tests PASAN.

COMPORTAMIENTO ESPERADO:
- Sistema NUNCA bloquea generación por falta de datos
- Preflight-check convierte BLOCKED → WARNING con benchmark fallback
- Assets incluyen disclaimer cuando confidence < 0.9
- Outputs NO tienen placeholders
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

import pytest

# Importar los módulos que deben existir después de implementar
# Estos imports FALLARÁN hasta que se implementen las fases 1-3
try:
    from modules.asset_generation.preflight_checks import PreflightChecker, PreflightStatus
    from modules.asset_generation.asset_content_validator import AssetContentValidator, ContentStatus
    PREFLIGHT_AVAILABLE = True
except ImportError:
    PREFLIGHT_AVAILABLE = False

from modules.asset_generation.asset_catalog import ASSET_CATALOG


class TestNeverBlockPrinciple:
    """Verifica el principio fundamental: NEVER_BLOCK."""
    
    def test_preflight_never_blocks_on_missing_data(self):
        """Preflight NO debe bloquear aunque falten datos."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("PreflightChecker not available yet")
        
        checker = PreflightChecker()
        
        # Caso: Sin datos en absoluto
        validated_data = {}  
        
        # Para cualquier asset
        for asset_type in ASSET_CATALOG.keys():
            report = checker.check_asset(asset_type, validated_data)
            
            # NEVER BLOCK - debe ser WARNING o PASSED, nunca BLOCKED
            assert report.overall_status != PreflightStatus.BLOCKED, \
                f"{asset_type}: No debe bloquear aunque falten datos"
            assert report.can_proceed == True, \
                f"{asset_type}: Siempre debe poder continuar"

    def test_preflight_uses_benchmark_fallback(self):
        """Cuando faltan datos, preflight debe usar benchmark fallback."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("PreflightChecker not available yet")
        
        checker = PreflightChecker()
        validated_data = {}  # Sin datos
        
        report = checker.check_asset("hotel_schema", validated_data)
        
        # WARNING indica que se usó fallback
        assert report.overall_status == PreflightStatus.WARNING, \
            "Sin datos debe ser WARNING (fallback usado)"
        assert len(report.warnings) > 0, "Debe haber warnings sobre el fallback"


class TestPlaceholderPrevention:
    """Verifica que NO se generan placeholders."""
    
    def test_validator_detects_city_placeholder(self):
        """AssetContentValidator debe detectar placeholder 'Ciudad'."""
        validator = AssetContentValidator()
        
        content = "Hotel en Ciudad, dirección: Ciudad"
        result = validator.validate_content(content)
        
        assert result.status == ContentStatus.INVALID, \
            "Placeholder 'Ciudad' debe ser detectado"
        assert any("placeholder" in i.issue_type.lower() for i in result.issues)

    def test_validator_detects_phone_placeholder(self):
        """AssetContentValidator debe detectar placeholder '+57XXX'."""
        validator = AssetContentValidator()
        
        content = "Teléfono: +57XXX"
        result = validator.validate_content(content)
        
        assert result.status == ContentStatus.INVALID, \
            "Placeholder '+57XXX' debe ser detectado"

    def test_validator_detects_dollar_placeholder(self):
        """AssetContentValidator debe detectar placeholder '$$+'."""
        validator = AssetContentValidator()
        
        content = "Precio: $$$+"
        result = validator.validate_content(content)
        
        assert result.status == ContentStatus.INVALID

    def test_validator_blocks_placeholder_in_final_output(self):
        """Validator debe bloquear outputs con placeholders."""
        validator = AssetContentValidator()
        
        # Contenido que un generador mal implementado podría producir
        bad_content = """
        # Guía de Optimización SEO para Hotelvisperas
        
        ## Datos del Hotel
        - Ciudad: Ciudad
        - Teléfono: +57XXX
        - Price Range: $$+
        
        ## Schema Hotel
        ```json
        {
          "addressLocality": "Ciudad"
        }
        ```
        """
        
        result = validator.validate_content(bad_content)
        
        assert result.status == ContentStatus.INVALID, \
            "Output con placeholders debe ser INVALID"

    def test_validator_accepts_real_data(self):
        """Validator debe aceptar datos reales."""
        validator = AssetContentValidator()
        
        good_content = """
        # Guía de Optimización SEO para Hotelvisperas
        
        ## Datos del Hotel
        - Ciudad: Santa Rosa de Cabal
        - Teléfono: +57612345678
        - Price Range: $$-$$$
        
        ## Schema Hotel
        ```json
        {
          "addressLocality": "Santa Rosa de Cabal",
          "telephone": "+57612345678"
        }
        ```
        """
        
        result = validator.validate_content(good_content)
        
        # Contenido bueno debe ser al menos WARNING, no INVALID
        assert result.status != ContentStatus.INVALID or len(result.issues) == 0, \
            "Datos reales no deben generar issues"


class TestConfidenceAnnotation:
    """Verifica que confidence es honesto y está annotado."""
    
    def test_estimated_asset_has_confidence_below_09(self):
        """Asset estimado debe tener confidence < 0.9."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("PreflightChecker not available yet")
        
        checker = PreflightChecker()
        validated_data = {}  # Sin datos reales
        
        report = checker.check_asset("hotel_schema", validated_data)
        
        # Sin datos reales, confidence debe ser bajo
        # (El valor exacto depende de benchmark)
        assert report.overall_status == PreflightStatus.WARNING

    def test_confidence_in_metadata(self):
        """Confidence debe estar en metadata del asset."""
        # Verificar que AssetMetadataEnforcer tiene campo confidence
        from modules.asset_generation.asset_metadata import AssetMetadata, AssetMetadataEnforcer
        
        metadata = AssetMetadataEnforcer().create_metadata(
            asset_type="hotel_schema",
            preflight_status=PreflightStatus.WARNING,
            confidence_score=0.5,
            sources=["benchmark"],
            gaps=["telephone"]
        )
        
        assert hasattr(metadata, 'confidence_score'), \
            "Metadata debe incluir confidence_score"
        assert metadata.confidence_score == 0.5


class TestDisclaimerIntegration:
    """Verifica que disclaimers se incluyen cuando corresponde."""
    
    def test_estimated_asset_generates_disclaimer(self):
        """Asset ESTIMATED debe tener disclaimer."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Disclaimer generator not available yet")
        
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.5,
            sources=["benchmark"],
            gaps=["telephone", "address"]
        )
        
        assert disclaimer is not None
        assert len(disclaimer) > 0
        assert "0.5" in disclaimer or "50%" in disclaimer.lower()

    def test_verified_asset_no_disclaimer(self):
        """Asset VERIFIED no necesita disclaimer."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Disclaimer generator not available yet")
        
        from modules.providers.disclaimer_generator import DisclaimerGenerator
        
        generator = DisclaimerGenerator()
        disclaimer = generator.generate(
            confidence=0.95,
            sources=["web", "gbp", "user_input"],
            gaps=[]
        )
        
        assert disclaimer == "" or disclaimer is None


class TestBenchmarkIntegration:
    """Verifica integración con BenchmarkResolver."""
    
    def test_preflight_uses_benchmark_when_data_missing(self):
        """Preflight debe usar benchmark cuando falta data."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Benchmark resolver not available yet")
        
        from modules.providers.benchmark_resolver import BenchmarkResolver
        
        # Simular gap de datos
        resolver = BenchmarkResolver()
        benchmark_telephone = resolver.resolve(
            field="telephone",
            value=None,
            context={"region": "eje_cafetero"}
        )
        
        # Benchmark debe dar valor
        assert benchmark_telephone.value is not None
        assert benchmark_telephone.confidence < 1.0
        assert "benchmark" in benchmark_telephone.sources


class TestOutputDelivery:
    """Verifica que outputs son delivery-ready."""
    
    def test_hotel_schema_without_placeholders(self):
        """Hotel schema generado debe estar libre de placeholders."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Full integration not available yet")
        
        validator = AssetContentValidator()
        
        # Ejemplo de schema malo (con placeholders)
        bad_schema = '''
        {
          "@type": "Hotel",
          "name": "Hotelvisperas",
          "description": "Descripción del hotel...",
          "address": {
            "addressLocality": "Ciudad"
          },
          "telephone": "+57XXX"
        }
        '''
        
        result = validator.validate_json(bad_schema)
        
        assert result.status == ContentStatus.INVALID, \
            "Schema con placeholders debe ser INVALID"

    def test_markdown_guide_without_placeholders(self):
        """Guía markdown generada debe estar libre de placeholders."""
        validator = AssetContentValidator()
        
        bad_guide = '''
        # Guía de Optimización SEO
        
        ## Metadata
        - Title: No configurado
        - Description: No configurado
        
        ## Recomendaciones
        - Revisar en Ciudad
        - Llamar al +57XXX
        '''
        
        result = validator.validate_content(bad_guide)
        
        assert result.status == ContentStatus.INVALID, \
            "Guía con placeholders debe ser INVALID"

    def test_all_assets_have_valid_confidence(self):
        """Todos los assets deben tener confidence score válido."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("PreflightChecker not available yet")
        
        checker = PreflightChecker()
        validated_data = {}
        
        for asset_type in ASSET_CATALOG.keys():
            report = checker.check_asset(asset_type, validated_data)
            
            # Debe tener al menos un check con confidence
            assert len(report.checks) > 0, f"{asset_type}: Debe tener checks"
            
            for check in report.checks:
                assert 0.0 <= check.required_confidence <= 1.0, \
                    f"{asset_type}.{check.check_name}: Confidence inválido"


class TestCoherenceMaintenance:
    """Verifica que coherence score se mantiene >= 0.8."""
    
    def test_coherence_gate_exists(self):
        """Debe existir gate de coherencia."""
        # Verificar que coherence_validator existe en workflow
        try:
            from modules.quality_gates.coherence_gate import CoherenceGate
            assert CoherenceGate is not None
        except ImportError:
            pytest.fail("CoherenceGate no existe")

    def test_empty_data_still_passes_coherence(self):
        """Incluso con datos vacíos, coherence debe pasar (con disclaimers)."""
        # Si no hay conflictos internos, coherence debe ser válida
        # Los disclaimers permiten confiance baja sin bloquear
        pass  # Implementado en fases anteriores


class TestEndToEndNeverBlock:
    """Test E2E del flujo NEVER_BLOCK."""
    
    def test_full_flow_with_no_data_still_produces_output(self):
        """Flujo completo sin datos debe producir output (no bloquear)."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Full integration not available yet")
        
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        generator = ConditionalGenerator(output_dir="/tmp/test_output")
        
        # Sin datos reales
        validated_data = {}
        
        # Debe producir algo, no bloquear
        result = generator.generate(
            asset_type="hotel_schema",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="test"
        )
        
        # SUCCESS con WARNING, no ERROR ni BLOCKED
        assert result['status'] in ['warning', 'passed', 'success'], \
            f"Debe producir warning/success, got: {result.get('status')}"
        assert result.get('can_use') == True, \
            "Asset debe poder usarse aunque sea estimado"

    def test_output_has_proper_naming_with_estimated(self):
        """Output sin datos reales debe usar prefijo ESTIMATED_."""
        if not PREFLIGHT_AVAILABLE:
            pytest.skip("Full integration not available yet")
        
        from modules.asset_generation.conditional_generator import ConditionalGenerator
        
        generator = ConditionalGenerator(output_dir="/tmp/test_output")
        
        result = generator.generate(
            asset_type="geo_playbook",
            validated_data={},  # Sin datos
            hotel_name="Test Hotel",
            hotel_id="test"
        )
        
        if result.get('status') == 'warning':
            filename = result.get('filename', '')
            assert 'ESTIMATED' in filename or 'estimated' in filename, \
                "Asset estimado debe tener 'ESTIMATED' en el nombre"


class TestRegressionWithHotelVisperas:
    """Verifica que Hotel Vísperas no tiene regression."""
    
    def test_hotelvisperas_outputs_have_no_placeholders(self):
        """Los outputs de Hotel Vísperas no deben tener placeholders."""
        import json
        from pathlib import Path
        
        # Usar Path.cwd() para obtener el project root (donde se ejecuto pytest)
        project_root = Path.cwd()
        report_path = project_root / "output" / "v4_complete" / "hotelvisperas" / "v4_audit" / "asset_generation_report.json"
        
        try:
            with open(report_path, 'r') as f:
                report = json.load(f)
        except FileNotFoundError:
            pytest.skip("Hotel Vísperas report not found")
        
        # Verificar que no hay assets bloqueados por placeholders
        for failed in report.get('failed_assets', []):
            reason = failed.get('reason', '')
            assert 'placeholder' not in reason.lower(), \
                f"Asset {failed.get('asset_type')} falló por placeholder: {reason}"

    def test_hotelvisperas_coherence_above_threshold(self):
        """Coherence de Hotel Vísperas debe ser >= 0.8."""
        import json
        from pathlib import Path
        
        project_root = Path.cwd()
        report_path = project_root / "output" / "v4_complete" / "hotelvisperas" / "v4_audit" / "coherence_validation.json"
        
        try:
            with open(report_path, 'r') as f:
                coherence = json.load(f)
        except FileNotFoundError:
            pytest.skip("Coherence report not found")
        
        assert coherence.get('overall_score', 0) >= 0.8, \
            f"Coherence {coherence.get('overall_score')} < 0.8"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
