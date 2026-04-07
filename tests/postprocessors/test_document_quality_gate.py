"""Tests for DocumentQualityGate — blocker and warning checks for commercial documents."""
import pytest
from modules.postprocessors.document_quality_gate import (
    DocumentQualityGate,
    DocumentQualityIssue,
    DocumentQualityResult,
)


@pytest.fixture
def gate():
    return DocumentQualityGate()


# ==============================================================================
# BLOCKER CHECK 1: Placeholder region ("default" where city should be)
# ==============================================================================
class TestPlaceholderRegion:
    def test_detects_en_default(self, gate):
        doc = "Lo que esta pasando en default es preocupante."
        result = gate.validate_document(doc, "diagnostico", {})
        assert not result.passed
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("placeholder_region" == i.check_name for i in blockers)

    def test_detects_region_de_default(self, gate):
        doc = "El mercado en la region de default muestra caida."
        result = gate.validate_document(doc, "diagnostico", {})
        assert not result.passed
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("placeholder_region" == i.check_name for i in blockers)

    def test_detects_de_default(self, gate):
        doc = "Los precios de default son altos."
        result = gate.validate_document(doc, "propuesta", {})
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("placeholder_region" == i.check_name for i in blockers)

    def test_does_not_flag_valid_city(self, gate):
        doc = "Lo que esta pasando en Santa Rosa de Cabal es preocupante."
        result = gate.validate_document(doc, "diagnostico", {})
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert all("placeholder_region" != i.check_name for i in blockers)


# ==============================================================================
# BLOCKER CHECK 2: Duplicate currency ("COP COP")
# ==============================================================================
class TestDuplicateCurrency:
    def test_detects_cop_cop(self, gate):
        doc = "Perdida estimada: $3.132.000 COP COP por mes."
        result = gate.validate_document(doc, "diagnostico", {})
        assert not result.passed
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("duplicate_currency" == i.check_name for i in blockers)

    def test_single_cop_is_ok(self, gate):
        doc = "Perdida estimada: $3.132.000 COP por mes."
        result = gate.validate_document(doc, "diagnostico", {})
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert all("duplicate_currency" != i.check_name for i in blockers)


# ==============================================================================
# BLOCKER CHECK 3: Zero confidence in commercial doc
# ==============================================================================
class TestZeroConfidence:
    def test_detects_zero_confidence(self, gate):
        doc = "Con 0% de confianza en el analisis, esto es problematico."
        result = gate.validate_document(doc, "diagnostico", {})
        assert not result.passed
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("zero_confidence" == i.check_name for i in blockers)

    def test_detects_zero_percent_variations(self, gate):
        doc = "Confianza del 0 % de confianza detectada."
        result = gate.validate_document(doc, "propuesta", {})
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert any("zero_confidence" == i.check_name for i in blockers)

    def test_does_not_flag_in_asset_doc(self, gate):
        doc = "Con 0% de confianza en el analisis tecnico."
        result = gate.validate_document(doc, "asset", {})
        # asset type should not flag zero confidence
        blockers = [i for i in result.issues if i.severity == "blocker"]
        assert all("zero_confidence" != i.check_name for i in blockers)


# ==============================================================================
# WARNING CHECK 1: Mixed language (Portuguese)
# ==============================================================================
class TestMixedLanguagePortuguese:
    def test_detects_passo(self, gate):
        doc = "El proximo passo es importante."
        result = gate.validate_document(doc, "diagnostico", {})
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any(
            i.check_name == "mixed_language" and "passo" in i.detected_value.lower()
            for i in warnings
        )

    def test_detects_protecao(self, gate):
        doc = "La protecao de datos es fundamental."
        result = gate.validate_document(doc, "diagnostico", {})
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any("protecao" in i.detected_value.lower() for i in warnings)


# ==============================================================================
# WARNING CHECK 2: Mixed language (English)
# ==============================================================================
class TestMixedLanguageEnglish:
    def test_detects_guests(self, gate):
        doc = "Los guests del hotel son internacionales."
        result = gate.validate_document(doc, "diagnostico", {})
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any(
            i.check_name == "mixed_language" and i.detected_value.lower() == "guests"
            for i in warnings
        )

    def test_does_not_flag_spanish_word(self, gate):
        doc = "Los huespedes del hotel son internacionales."
        result = gate.validate_document(doc, "diagnostico", {})
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert all(i.detected_value.lower() != "huespedes" for i in warnings)


# ==============================================================================
# WARNING CHECK 3: Generic AI phrases
# ==============================================================================
class TestGenericAIPhrases:
    def test_detects_boilerplate(self, gate):
        doc = "oportunidades de crecimiento en presencia digital son clave en la era digital actual"
        result = gate.validate_document(doc, "diagnostico", {})
        warnings = [i for i in result.issues if i.severity == "warning"]
        assert any("generic_ai_phrases" == i.check_name for i in warnings)


# ==============================================================================
# DocumentQualityResult
# ==============================================================================
class TestDocumentQualityResult:
    def test_passed_when_no_blockers(self, gate):
        doc = "Un documento limpio sin problemas mayores."
        result = gate.validate_document(doc, "diagnostico", {})
        assert result.passed
        assert result.score == 1.0

    def test_failed_when_blockers(self, gate):
        doc = "en default COP COP 0% de confianza"
        result = gate.validate_document(doc, "diagnostico", {})
        assert not result.passed

    def test_score_decreases_with_issues(self, gate):
        clean = gate.validate_document("Todo ok.", "diagnostico", {})
        dirty = gate.validate_document("en default.", "diagnostico", {})
        assert clean.score > dirty.score

    def test_counts_blockers_and_warnings(self, gate):
        doc = "en default y los passo estan ok."
        result = gate.validate_document(doc, "diagnostico", {})
        assert result.blockers_count >= 1
        assert result.warnings_count >= 1

    def test_document_type_stored(self, gate):
        result = gate.validate_document("ok", "propuesta", {})
        assert result.document_type == "propuesta"
