"""Tests for conditional_generator module."""

import pytest
import json
import os
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch
from modules.asset_generation.conditional_generator import ConditionalGenerator
from modules.asset_generation.preflight_checks import PreflightStatus, PreflightReport, PreflightCheck
from modules.asset_generation.asset_metadata import AssetMetadata
from modules.data_validation import DataPoint, DataSource


class TestConditionalGeneratorInitialization:
    """Tests for ConditionalGenerator initialization."""

    def test_conditional_generator_initialization(self):
        """Test that ConditionalGenerator initializes correctly."""
        generator = ConditionalGenerator(output_dir="test_output")
        assert generator is not None
        assert generator.output_dir == Path("test_output")
        assert hasattr(generator, "preflight_checker")
        assert hasattr(generator, "metadata_enforcer")
        assert hasattr(generator, "GENERATION_STRATEGIES")

    def test_conditional_generator_default_output_dir(self):
        """Test default output directory."""
        generator = ConditionalGenerator()
        assert generator.output_dir == Path("output")

    def test_generation_strategies_structure(self):
        """Test that GENERATION_STRATEGIES has correct structure."""
        generator = ConditionalGenerator()
        expected_assets = ["whatsapp_button", "faq_page", "hotel_schema", "financial_projection"]
        for asset in expected_assets:
            assert asset in generator.GENERATION_STRATEGIES
            assert "template" in generator.GENERATION_STRATEGIES[asset]
            assert "output_name" in generator.GENERATION_STRATEGIES[asset]


class TestConditionalGeneratorGenerate:
    """Tests for ConditionalGenerator.generate method."""

    def _create_data_point(self, field_name, value):
        """Helper to create a DataPoint."""
        dp = DataPoint(field_name)
        dp.add_source(DataSource("test", value, datetime.now().isoformat()))
        return dp

    def test_generate_unknown_asset_type(self):
        """Test generate with unknown asset type returns error."""
        generator = ConditionalGenerator()
        result = generator.generate(
            asset_type="unknown_type",
            validated_data={},
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is False
        assert result["status"] == "error"
        assert "Unknown asset type" in result["error"]

    def test_generate_with_passed_status_creates_asset(self, tmp_path):
        """Test generate with PASSED status creates asset."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        dp = self._create_data_point("whatsapp", "+573001234567")
        validated_data = {"whatsapp": dp}
        
        result = generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is True
        # NEVER_BLOCK: status es "success" o "warning" (nunca "blocked")
        assert result["status"] in ("success", "warning")
        assert result["asset_type"] == "whatsapp_button"
        assert result["hotel_id"] == "hotel_123"

    def test_generate_with_warning_creates_estimated_asset(self, tmp_path):
        """Test generate with WARNING creates ESTIMATED_ asset."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        # Create DataPoint with lower confidence
        dp = DataPoint("faqs")
        # Single source typically gives ESTIMATED confidence
        dp.add_source(DataSource("source1", [{"question": "Q1", "answer": "A1"}], datetime.now().isoformat()))
        validated_data = {"faqs": dp}
        
        result = generator.generate(
            asset_type="faq_page",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        # Should succeed but may be estimated or generated depending on confidence
        assert result["success"] is True

    def test_generate_with_blocked_returns_error(self, tmp_path):
        """Test generate with BLOCKED returns error - NEVER_BLOCK: now returns success with warning."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        # Empty DataPoint should give low confidence
        # NEVER_BLOCK: Even with low confidence, generate succeeds with warning
        dp = DataPoint("whatsapp")
        validated_data = {"whatsapp": dp}
        
        result = generator.generate(
            asset_type="whatsapp_button",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        # NEVER_BLOCK: Nunca retorna error por confianza baja - usa fallback
        assert result["success"] is True
        assert result["status"] in ("warning", "success")  # NUNCA "blocked"
        # El asset se genera igual con disclaimer
        assert "can_use" in result
        assert result["can_use"] is True


class TestConditionalGeneratorNamingStrategy:
    """Tests for ConditionalGenerator._apply_naming_strategy method."""

    def test_apply_naming_strategy_for_passed(self):
        """Test naming strategy for PASSED status."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.PASSED,
            checks=[],
            can_proceed=True,
            warnings=[],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        assert "boton_whatsapp" in filename
        assert "ESTIMATED_" not in filename
        assert "FAILED_" not in filename
        assert filename.endswith(".html")

    def test_apply_naming_strategy_for_warning(self):
        """Test naming strategy for WARNING status."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.WARNING,
            checks=[],
            can_proceed=True,
            warnings=["Low confidence"],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        assert "ESTIMATED_" in filename
        assert "boton_whatsapp" in filename

    def test_apply_naming_strategy_includes_timestamp(self):
        """Test that filename includes timestamp."""
        generator = ConditionalGenerator()
        report = PreflightReport(
            asset_type="whatsapp_button",
            overall_status=PreflightStatus.PASSED,
            checks=[],
            can_proceed=True,
            warnings=[],
            blocking_issues=[],
        )
        filename = generator._apply_naming_strategy("whatsapp_button", report, "hotel_123")
        # Should contain timestamp pattern (8 digits for date + underscore + 6 digits for time)
        import re
        assert re.search(r"\d{8}_\d{6}", filename) is not None


class TestConditionalGeneratorContentGeneration:
    """Tests for ConditionalGenerator content generation methods."""

    def test_generate_whatsapp_button_returns_html(self):
        """Test _generate_whatsapp_button returns HTML with cleaned phone number."""
        generator = ConditionalGenerator()
        html = generator._generate_whatsapp_button("+573104019049", "Test Hotel")
        assert "<a" in html
        assert "whatsapp-button" in html
        assert "wa.me" in html
        assert "Test Hotel" in html
        # FIX-C1: Phone number is cleaned to digits only for wa.me URL
        assert "wa.me/573104019049" in html
        assert "</a>" in html
        assert "<style>" in html

    def test_generate_faq_page_returns_json_ld(self):
        """Test _generate_faq_page returns JSON-LD FAQPage (FASE-5 fix)."""
        generator = ConditionalGenerator()
        faqs = [
            {"question": "What time is check-in?", "answer": "3:00 PM", "category": "Check-in"},
            {"question": "Do you have wifi?", "answer": "Yes, free wifi", "category": "Amenities"},
        ]
        json_content = generator._generate_faq_page(faqs, len(faqs))
        # FASE-5: Now returns JSON-LD FAQPage, not CSV
        import json
        parsed = json.loads(json_content)
        assert parsed["@type"] == "FAQPage"
        assert parsed["@context"] == "https://schema.org"
        assert len(parsed["mainEntity"]) == 2
        assert parsed["mainEntity"][0]["name"] == "What time is check-in?"
        assert parsed["mainEntity"][0]["acceptedAnswer"]["text"] == "3:00 PM"

    def test_generate_hotel_schema_returns_json(self):
        """Test _generate_hotel_schema returns JSON."""
        generator = ConditionalGenerator()
        hotel_data = {
            "name": "Test Hotel",
            "description": "A nice hotel",
            "website": "https://example.com",
            "phone": "+573001234567",
            "address": "123 Main St",
            "city": "Bogota",
            "country": "CO",
            "amenities": ["wifi", "pool"],
        }
        json_content = generator._generate_hotel_schema(hotel_data)
        parsed = json.loads(json_content)
        assert parsed["@context"] == "https://schema.org"
        assert parsed["@type"] == "LodgingBusiness"
        assert parsed["name"] == "Test Hotel"
        assert parsed["telephone"] == "+573001234567"

    def test_generate_financial_projection_returns_markdown(self):
        """Test _generate_financial_projection returns Markdown."""
        generator = ConditionalGenerator()
        scenarios = {
            "conservative": {"revenue": 100000, "occupancy": 0.7},
            "optimistic": {"revenue": 150000, "occupancy": 0.85},
        }
        hotel_data = {"name": "Test Hotel"}
        md_content = generator._generate_financial_projection(scenarios, hotel_data)
        assert "# Proyección Financiera: Test Hotel" in md_content
        assert "Conservative" in md_content or "conservative" in md_content
        assert "Optimistic" in md_content or "optimistic" in md_content
        assert "revenue" in md_content.lower() or "Revenue" in md_content
        assert "IMPORTANTE" in md_content or "Advertencias" in md_content


class TestConditionalGeneratorSaveAsset:
    """Tests for ConditionalGenerator.save_asset method."""

    def test_save_asset_creates_file_and_metadata(self, tmp_path):
        """Test save_asset creates file and metadata."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        
        # Create mock metadata
        metadata = Mock(spec=AssetMetadata)
        metadata.hotel_id = "hotel_123"
        metadata.to_dict.return_value = {
            "asset_type": "whatsapp_button",
            "hotel_id": "hotel_123",
            "hotel_name": "Test Hotel",
            "generated_at": datetime.now().isoformat(),
        }
        
        content = "<html>Test</html>"
        filename = "test_file.html"
        
        file_path = generator.save_asset("whatsapp_button", content, filename, metadata)
        
        # Check file was created
        assert file_path.exists()
        assert file_path.read_text() == content
        
        # Check metadata file was created
        metadata_path = file_path.parent / "test_file_metadata.json"
        assert metadata_path.exists()
        
        # Check directory structure
        assert "hotel_123" in str(file_path)
        assert "whatsapp_button" in str(file_path)


class TestConditionalGeneratorGetGenerationSummary:
    """Tests for ConditionalGenerator.get_generation_summary method."""

    def test_get_generation_summary_counts_correctly(self):
        """Test get_generation_summary counts correctly."""
        generator = ConditionalGenerator()
        generations = [
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "generated", "asset_type": "faq_page"},
            {"status": "estimated", "asset_type": "hotel_schema"},
            {"status": "blocked", "asset_type": "financial_projection"},
            {"status": "error", "asset_type": "whatsapp_button"},
        ]
        
        summary = generator.get_generation_summary(generations)
        
        assert summary["total"] == 5
        assert summary["passed"] == 2
        assert summary["warning"] == 1
        assert summary["blocked"] == 1
        assert summary["failed"] == 1
        assert summary["success_rate"] == 40.0  # 2 passed out of 5

    def test_get_generation_summary_by_type(self):
        """Test get_generation_summary groups by type."""
        generator = ConditionalGenerator()
        generations = [
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "generated", "asset_type": "whatsapp_button"},
            {"status": "estimated", "asset_type": "faq_page"},
        ]
        
        summary = generator.get_generation_summary(generations)
        
        assert "whatsapp_button" in summary["by_type"]
        assert "faq_page" in summary["by_type"]
        assert summary["by_type"]["whatsapp_button"]["passed"] == 2
        assert summary["by_type"]["faq_page"]["warning"] == 1

    def test_get_generation_summary_empty_list(self):
        """Test get_generation_summary with empty list."""
        generator = ConditionalGenerator()
        summary = generator.get_generation_summary([])
        
        assert summary["total"] == 0
        assert summary["passed"] == 0
        assert summary["success_rate"] == 0

    def test_get_generation_summary_includes_timestamp(self):
        """Test get_generation_summary includes generated_at timestamp."""
        generator = ConditionalGenerator()
        generations = [{"status": "generated", "asset_type": "test"}]
        
        summary = generator.get_generation_summary(generations)
        
        assert "generated_at" in summary
        # Should be ISO format timestamp
        assert isinstance(summary["generated_at"], str)


class TestConditionalGeneratorHelperMethods:
    """Tests for ConditionalGenerator helper methods."""

    def test_calculate_confidence_score(self):
        """Test _calculate_confidence_score method."""
        generator = ConditionalGenerator()
        
        # Report with passed checks
        check_passed = PreflightCheck(
            check_name="test",
            field_name="test",
            required_confidence=0.8,
            status=PreflightStatus.PASSED,
            message="OK",
            can_generate=True,
        )
        report_passed = PreflightReport(
            asset_type="test",
            overall_status=PreflightStatus.PASSED,
            checks=[check_passed],
            can_proceed=True,
        )
        assert generator._calculate_confidence_score(report_passed) == 1.0
        
        # Report with warning checks
        check_warning = PreflightCheck(
            check_name="test",
            field_name="test",
            required_confidence=0.8,
            status=PreflightStatus.WARNING,
            message="Low",
            can_generate=True,
        )
        report_warning = PreflightReport(
            asset_type="test",
            overall_status=PreflightStatus.WARNING,
            checks=[check_warning],
            can_proceed=True,
        )
        assert generator._calculate_confidence_score(report_warning) == 0.5

    def test_hash_data(self):
        """Test _hash_data method creates consistent hash."""
        generator = ConditionalGenerator()
        data = {"key": "value", "number": 123}
        hash1 = generator._hash_data(data)
        hash2 = generator._hash_data(data)
        
        assert isinstance(hash1, str)
        assert len(hash1) == 16
        assert hash1 == hash2  # Same data should produce same hash
        
        # Different data should produce different hash
        different_data = {"key": "different", "number": 123}
        hash3 = generator._hash_data(different_data)
        assert hash1 != hash3

    def test_generate_content_whatsapp(self):
        """Test _generate_content for whatsapp_button."""
        generator = ConditionalGenerator()
        dp = DataPoint("whatsapp")
        dp.add_source(DataSource("test", "+573001234567", datetime.now().isoformat()))
        validated_data = {"whatsapp": dp}
        
        content = generator._generate_content("whatsapp_button", validated_data, "Test Hotel")
        assert "whatsapp-button" in content
        assert "wa.me" in content

    def test_generate_content_faq(self):
        """Test _generate_content for faq_page returns JSON-LD (FASE-5 fix)."""
        generator = ConditionalGenerator()
        dp = DataPoint("faqs")
        faqs = [{"question": "Q1", "answer": "A1"}]
        dp.add_source(DataSource("test", faqs, datetime.now().isoformat()))
        validated_data = {"faqs": dp}

        content = generator._generate_content("faq_page", validated_data, "Test Hotel")
        # FASE-5: Now returns JSON-LD, not CSV
        import json
        parsed = json.loads(content)
        assert parsed["@type"] == "FAQPage"
        assert len(parsed["mainEntity"]) == 1


class TestMinimumDataGuarantee:
    """Tests for FASE-3: MINIMUM-DATA-GUARANTEE."""

    def test_hotel_schema_with_empty_data(self):
        """Test hotel_data={} genera schema con name='Hotel', country='CO', no crashea."""
        generator = ConditionalGenerator()
        json_content = generator._generate_hotel_schema({})
        parsed = json.loads(json_content)
        assert parsed["@context"] == "https://schema.org"
        assert parsed["@type"] == "LodgingBusiness"
        assert parsed["name"] == "Hotel"
        assert parsed["address"]["addressCountry"] == "CO"
        # Sin coordenadas validas → geo no debe existir
        assert "geo" not in parsed

    def test_completeness_score_full(self):
        """Test todos los campos presentes → score >= 0.9."""
        generator = ConditionalGenerator()
        full_data = {
            "name": "Hotel Test",
            "url": "https://hotel.com",
            "telephone": "+573001234567",
            "address": "Calle 123",
            "latitude": 4.6,
            "longitude": -74.1,
            "rating": 4.5,
            "review_count": 100,
            "description": "Un gran hotel",
            "amenities": ["wifi", "pool"]
        }
        score = generator._validate_hotel_data_completeness(full_data)
        assert score >= 0.9

    def test_completeness_score_empty(self):
        """Test solo name y url → score refleja solo url (name='Hotel' es placeholder)."""
        generator = ConditionalGenerator()
        minimal_data = {"name": "Hotel", "url": "https://example.com"}
        score = generator._validate_hotel_data_completeness(minimal_data)
        # name="Hotel" es excluido (placeholder), url cuenta → 0.2/1.0 = 0.2
        assert 0.15 <= score <= 0.25

    def test_confidence_penalty_low_completeness(self, tmp_path):
        """Test hotel_data con solo name → confidence <= 0.5."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        validated_data = {"hotel_data": {"name": "Solo Name"}}
        result = generator.generate(
            asset_type="hotel_schema",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        # Con solo name (completeness bajo), confidence debe estar penalizado
        assert result["success"] is True
        metadata = result.get("metadata", {})
        confidence = metadata.get("confidence_score", 1.0)
        assert confidence <= 0.5

    def test_data_rescue_flag_blocks_publication(self, tmp_path):
        """Test hotel_data con _data_rescue_needed=True → confidence=0.3."""
        generator = ConditionalGenerator(output_dir=str(tmp_path))
        validated_data = {
            "hotel_data": {
                "_data_rescue_needed": True,
                "name": "Hotel",
                "url": ""
            }
        }
        result = generator.generate(
            asset_type="hotel_schema",
            validated_data=validated_data,
            hotel_name="Test Hotel",
            hotel_id="hotel_123"
        )
        assert result["success"] is True
        metadata = result.get("metadata", {})
        confidence = metadata.get("confidence_score", 1.0)
        assert confidence == 0.3


class TestHotelSchemaRichPreference:
    """Tests for FASE-A: Schema rico preference over basic schema.

    Verifies that:
    1. Schema rico exists + valid JSON-LD -> used directly
    2. Schema rico does not exist -> basic schema generated
    3. Schema rico exists but empty/invalid -> basic schema generated (fallback)
    """

    def test_schema_rico_exists_uses_rich_directly(self, tmp_path):
        """Schema rico existe + JSON-LD valido -> se retorna como asset oficial."""
        hotel_id = "test_hotel_001"
        generator = ConditionalGenerator(output_dir=str(tmp_path))

        # Crear geo_enriched/hotel_schema_rich.json
        geo_dir = tmp_path / hotel_id / "geo_enriched"
        geo_dir.mkdir(parents=True)
        rich_schema = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Amazilia Hotel Test",
            "description": "Hotel boutique en Salento",
            "url": "https://amaziliahotel.com",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Calle 10 #5-50",
                "addressLocality": "Salento",
                "addressRegion": "Quindio",
                "postalCode": "631920",
                "addressCountry": "CO"
            },
            "starRating": {"@type": "Rating", "ratingValue": "4"},
            "amenityFeature": [
                {"@type": "LocationFeatureSpecification", "name": "Piscina"},
                {"@type": "LocationFeatureSpecification", "name": "WiFi"},
            ],
            "priceRange": "$$",
            "telephone": "+576000000000",
            "geo": {
                "@type": "GeoCoordinates",
                "latitude": "4.6372",
                "longitude": "-75.5697"
            }
        }
        (geo_dir / "hotel_schema_rich.json").write_text(
            json.dumps(rich_schema, indent=2), encoding="utf-8"
        )

        # Generar schema
        result = generator._generate_hotel_schema(
            {"name": "Test Hotel", "url": "https://test.com"},
            hotel_id=hotel_id
        )

        # Debe retornar el schema rico, no el basico
        parsed = json.loads(result)
        assert parsed["@type"] == "Hotel"
        assert parsed["name"] == "Amazilia Hotel Test"
        assert "starRating" in parsed  # Campo solo en schema rico
        assert "amenityFeature" in parsed

    def test_schema_rico_not_exists_generates_basic(self, tmp_path):
        """Schema rico no existe -> generacion basica normal (backward compatible)."""
        hotel_id = "test_hotel_002"
        generator = ConditionalGenerator(output_dir=str(tmp_path))

        # No crear geo_enriched/

        result = generator._generate_hotel_schema(
            {"name": "Basic Hotel", "url": "https://basic.com"},
            hotel_id=hotel_id
        )

        parsed = json.loads(result)
        assert parsed["@type"] == "LodgingBusiness"
        assert parsed["name"] == "Basic Hotel"

    def test_schema_rico_exists_but_invalid_falls_back_to_basic(self, tmp_path):
        """Schema rico existe pero invalido (no es JSON-LD) -> genera basico."""
        hotel_id = "test_hotel_003"
        generator = ConditionalGenerator(output_dir=str(tmp_path))

        # Crear geo_enriched/hotel_schema_rich.json invalido
        geo_dir = tmp_path / hotel_id / "geo_enriched"
        geo_dir.mkdir(parents=True)
        (geo_dir / "hotel_schema_rich.json").write_text(
            "No es JSON valido", encoding="utf-8"
        )

        result = generator._generate_hotel_schema(
            {"name": "Fallback Hotel", "url": "https://fallback.com"},
            hotel_id=hotel_id
        )

        parsed = json.loads(result)
        assert parsed["@type"] == "LodgingBusiness"
        assert parsed["name"] == "Fallback Hotel"

    def test_schema_rico_empty_file_falls_back_to_basic(self, tmp_path):
        """Schema rico existe pero vacio -> genera basico."""
        hotel_id = "test_hotel_004"
        generator = ConditionalGenerator(output_dir=str(tmp_path))

        geo_dir = tmp_path / hotel_id / "geo_enriched"
        geo_dir.mkdir(parents=True)
        (geo_dir / "hotel_schema_rich.json").write_text("", encoding="utf-8")

        result = generator._generate_hotel_schema(
            {"name": "Empty Rico Hotel", "url": "https://empty.com"},
            hotel_id=hotel_id
        )

        parsed = json.loads(result)
        assert parsed["@type"] == "LodgingBusiness"

    def test_generate_content_passes_hotel_id_to_hotel_schema(self, tmp_path):
        """Verifica que _generate_content pasa hotel_id para que _generate_hotel_schema use rico."""
        hotel_id = "test_hotel_005"
        generator = ConditionalGenerator(output_dir=str(tmp_path))

        # Crear schema rico
        geo_dir = tmp_path / hotel_id / "geo_enriched"
        geo_dir.mkdir(parents=True)
        rich_schema = {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Viajero Hotel",
        }
        (geo_dir / "hotel_schema_rich.json").write_text(
            json.dumps(rich_schema, indent=2), encoding="utf-8"
        )

        # Usar generate() completo que llama a _generate_content
        validated_data = {"hotel_data": {"name": "Should Not Appear", "url": "https://unused.com"}}
        result = generator.generate(
            asset_type="hotel_schema",
            validated_data=validated_data,
            hotel_name="Viajero Hotel",
            hotel_id=hotel_id
        )

        assert result["success"] is True
        # El contenido se guarda en file_path, leerlo
        with open(result["file_path"], 'r', encoding='utf-8') as f:
            content = f.read()
        parsed = json.loads(content)
        assert parsed["@type"] == "Hotel"
        assert parsed["name"] == "Viajero Hotel"


# ═══════════════════════════════════════════════════════════════════
# FASE-0H-G8: Confidence Scoring Tests
# ═══════════════════════════════════════════════════════════════════

class TestConfidenceScoringFase0HG8:
    """Tests for _calculate_confidence_score with REQUIRED/RECOMMENDED priority."""

    def setup_method(self):
        self.generator = ConditionalGenerator(output_dir="test_output")

    def test_recommended_warning_scores_0_8(self):
        """RECOMMENDED + WARNING + fallback → confidence 0.8."""
        report = PreflightReport(
            asset_type="og_tags_guide",
            overall_status=PreflightStatus.WARNING,
            checks=[
                PreflightCheck(
                    check_name="og_tags_detected_exists",
                    field_name="og_tags_detected",
                    required_confidence=0.4,
                    status=PreflightStatus.WARNING,
                    message="Using fallback: og_tags_detected not found",
                    can_generate=True,
                    fallback_action="generate_og_tags_guide",
                    priority="RECOMMENDED",
                )
            ],
            can_proceed=True,
            warnings=["Missing field og_tags_detected, using fallback"],
            blocking_issues=[],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 0.8, f"Expected 0.8, got {score}"

    def test_recommended_warning_no_fallback_scores_0_5(self):
        """RECOMMENDED + WARNING but NO fallback → still 0.5 (no bump)."""
        report = PreflightReport(
            asset_type="some_asset",
            overall_status=PreflightStatus.WARNING,
            checks=[
                PreflightCheck(
                    check_name="field_exists",
                    field_name="some_field",
                    required_confidence=0.5,
                    status=PreflightStatus.WARNING,
                    message="Missing field",
                    can_generate=True,
                    fallback_action=None,
                    priority="RECOMMENDED",
                )
            ],
            can_proceed=True,
            warnings=["Missing field"],
            blocking_issues=[],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 0.5, f"Expected 0.5, got {score}"

    def test_required_warning_scores_0_5(self):
        """REQUIRED + WARNING → 0.5 (no change from current behavior)."""
        report = PreflightReport(
            asset_type="hotel_schema",
            overall_status=PreflightStatus.WARNING,
            checks=[
                PreflightCheck(
                    check_name="hotel_data_confidence",
                    field_name="hotel_data",
                    required_confidence=0.6,
                    status=PreflightStatus.WARNING,
                    message="Confidence 0.40 below requirement (0.60) but acceptable",
                    can_generate=True,
                    fallback_action="generate_basic_schema",
                    priority="REQUIRED",
                )
            ],
            can_proceed=True,
            warnings=["Suboptimal confidence in hotel_data"],
            blocking_issues=[],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 0.5, f"Expected 0.5, got {score}"

    def test_passed_check_scores_1_0(self):
        """PASSED check → 1.0 (unchanged)."""
        report = PreflightReport(
            asset_type="faq_page",
            overall_status=PreflightStatus.PASSED,
            checks=[
                PreflightCheck(
                    check_name="faqs_confidence",
                    field_name="faqs",
                    required_confidence=0.5,
                    status=PreflightStatus.PASSED,
                    message="Confidence 0.85 meets requirement",
                    can_generate=True,
                    fallback_action=None,
                    priority="REQUIRED",
                )
            ],
            can_proceed=True,
            warnings=[],
            blocking_issues=[],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 1.0, f"Expected 1.0, got {score}"

    def test_blocked_check_scores_0_0(self):
        """BLOCKED check → 0.0 (unchanged)."""
        report = PreflightReport(
            asset_type="unknown",
            overall_status=PreflightStatus.BLOCKED,
            checks=[
                PreflightCheck(
                    check_name="field_confidence",
                    field_name="field",
                    required_confidence=0.5,
                    status=PreflightStatus.BLOCKED,
                    message="Confidence too low",
                    can_generate=False,
                    fallback_action=None,
                    priority="REQUIRED",
                )
            ],
            can_proceed=False,
            warnings=[],
            blocking_issues=["Blocked"],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 0.0, f"Expected 0.0, got {score}"

    def test_mixed_checks_average_correctly(self):
        """Mixed PASSED + RECOMMENDED_WARNING → correct average."""
        report = PreflightReport(
            asset_type="mixed_asset",
            overall_status=PreflightStatus.WARNING,
            checks=[
                PreflightCheck(
                    check_name="check1",
                    field_name="field1",
                    required_confidence=0.5,
                    status=PreflightStatus.PASSED,
                    message="OK",
                    can_generate=True,
                    priority="REQUIRED",
                ),
                PreflightCheck(
                    check_name="check2",
                    field_name="field2",
                    required_confidence=0.4,
                    status=PreflightStatus.WARNING,
                    message="fallback used",
                    can_generate=True,
                    fallback_action="some_fallback",
                    priority="RECOMMENDED",
                ),
            ],
            can_proceed=True,
            warnings=["fallback"],
            blocking_issues=[],
        )
        score = self.generator._calculate_confidence_score(report)
        # (1.0 + 0.8) / 2 = 0.9
        assert score == 0.9, f"Expected 0.9, got {score}"

    def test_no_checks_returns_zero(self):
        """Empty checks → 0.0."""
        report = PreflightReport(
            asset_type="empty",
            overall_status=PreflightStatus.BLOCKED,
            checks=[],
            can_proceed=False,
            warnings=[],
            blocking_issues=["Unknown asset"],
        )
        score = self.generator._calculate_confidence_score(report)
        assert score == 0.0


class TestHotelCastillaRealFixtureG8:
    """Validates that Hotel Castilla Real fixture demonstrates G8 improvement."""

    def test_fixture_assets_confidence_improvement(self):
        """After derivation + priority changes, more assets should have confidence >= 0.65."""
        import json
        from pathlib import Path
        from modules.asset_generation.data_derivation_layer import (
            DataDerivationLayer,
            merge_derived_into_validated,
        )
        from modules.asset_generation.preflight_checks import PreflightChecker

        fixture_path = (
            Path(__file__).parent.parent / "fixtures"
            / "audit_report_hotelcastillareal.json"
        )
        if not fixture_path.exists():
            pytest.skip(f"Fixture not found: {fixture_path}")

        with open(fixture_path, "r", encoding="utf-8") as f:
            audit_report = json.load(f)

        # Simulate validated_data as orchestrator would build it
        # (minimal hotel_data from GBP/schema)
        validated_data = {
            "hotel_data": {
                "name": audit_report.get("hotel_name", "Hotel Castilla Real"),
                "url": audit_report.get("url", ""),
            }
        }

        # Add GBP data if available
        gbp = audit_report.get("gbp", {})
        if gbp:
            if gbp.get("rating"):
                validated_data["hotel_data"]["rating"] = gbp["rating"]
            if gbp.get("reviews"):
                validated_data["hotel_data"]["review_count"] = gbp["reviews"]
            if gbp.get("address"):
                validated_data["hotel_data"]["address"] = gbp["address"]
            if gbp.get("phone"):
                validated_data["hotel_data"]["telephone"] = gbp["phone"]
            validated_data["hotel_data"]["latitude"] = gbp.get("lat", 0)
            validated_data["hotel_data"]["longitude"] = gbp.get("lng", 0)

        # Derive missing fields
        layer = DataDerivationLayer()
        derived = layer.derive(audit_report)
        merge_derived_into_validated(validated_data, derived)

        # Asset types to check (from the plan)
        affected_assets = [
            "optimization_guide",    # metadata → now derivable!
            "local_content_page",    # hotel_data
            "analytics_setup_guide", # ga4_available → RECOMMENDED
            "indirect_traffic_optimization",  # organic_traffic → RECOMMENDED
            "og_tags_guide",         # og_tags_detected → derivable + RECOMMENDED
            "open_graph",            # hotel_data
            "org_schema",            # org_data → derivable + RECOMMENDED
            "monthly_report",        # hotel_data
        ]

        checker = PreflightChecker()
        high_confidence_count = 0

        for asset_type in affected_assets:
            report = checker.check_asset(asset_type, validated_data)

            # Calculate confidence using the generator's method
            generator = ConditionalGenerator(output_dir="test_output")
            score = generator._calculate_confidence_score(report)

            # Log for debugging
            print(f"  {asset_type}: confidence={score:.2f}, "
                  f"status={report.overall_status.value}, "
                  f"priority={getattr(report.checks[0], 'priority', 'N/A') if report.checks else 'no_checks'}")

            if score >= 0.65:
                high_confidence_count += 1

        # VERIFICATION: At least 6 of 8 affected assets should now have confidence >= 0.65
        # (up from 0/8 in the baseline)
        print(f"\n  Assets with confidence >= 0.65: {high_confidence_count}/8")
        assert high_confidence_count >= 6, (
            f"Expected >=6 assets with confidence >=0.65, got {high_confidence_count}/8. "
            f"G8 hardening insufficient."
        )
