"""Tests FASE-J: NoDefaultsValidator source-aware + template honesto.

Verifica:
- Deteccion de fuentes sospechosas (warnings, no blocks)
- source_reliability = verified/unverified
- Labels condicionales en template
- Backward compatibility (sin sources param = sin warnings)
"""

import pytest
from modules.financial_engine.no_defaults_validator import (
    NoDefaultsValidator,
    NoDefaultsValidationResult,
    ValidationWarning,
    SUSPECT_SOURCES,
)
from modules.commercial_documents.v4_diagnostic_generator import V4DiagnosticGenerator


# --- Fixtures ---

VALID_DATA = {
    "occupancy_rate": 0.75,
    "direct_channel_percentage": 0.20,
    "adr_cop": 180000.0,
}

VERIFIED_SOURCES = {
    "occupancy_rate": "onboarding",
    "direct_channel_percentage": "onboarding",
    "adr_cop": "onboarding",
}

SUSPECT_SOURCES_MIXED = {
    "occupancy_rate": "onboarding",
    "direct_channel_percentage": "benchmark",
    "adr_cop": "legacy_hardcode",  # only this is suspect
}

ALL_SUSPECT_SOURCES = {
    "occupancy_rate": "default",
    "direct_channel_percentage": "hardcoded",
    "adr_cop": "unknown",
}


# ============================================================
# Test 1: suspect source generates warning
# ============================================================

class TestSuspectSourceWarning:
    def test_suspect_source_generates_warning(self):
        """Una fuente sospechosa debe generar warning (no bloquear)."""
        validator = NoDefaultsValidator()
        result = validator.validate(VALID_DATA, sources=SUSPECT_SOURCES_MIXED)

        # No bloquea
        assert result.can_calculate is True
        assert len(result.blocks) == 0

        # Pero genera warnings (solo legacy_hardcode es sospechoso, benchmark NO)
        assert result.has_suspect_sources is True
        assert len(result.source_warnings) == 1
        assert "adr_cop" in result.suspect_fields

        # El warning menciona la fuente
        warning_fields = [w.field for w in result.source_warnings]
        assert "adr_cop" in warning_fields
        for sw in result.source_warnings:
            assert sw.source in SUSPECT_SOURCES


# ============================================================
# Test 2: verified sources produce no warnings
# ============================================================

class TestVerifiedSourcesNoWarnings:
    def test_verified_sources_no_warnings(self):
        """Fuentes verificadas no deben generar warnings."""
        validator = NoDefaultsValidator()
        result = validator.validate(VALID_DATA, sources=VERIFIED_SOURCES)

        assert result.can_calculate is True
        assert result.has_suspect_sources is False
        assert result.source_reliability == "verified"
        assert result.suspect_fields == []
        assert len(result.source_warnings) == 0


# ============================================================
# Test 3: mixed sources partial warning
# ============================================================

class TestMixedSourcesPartialWarning:
    def test_mixed_sources_partial_warning(self):
        """Fuentes mixtas generan warnings solo para las sospechosas."""
        validator = NoDefaultsValidator()
        result = validator.validate(VALID_DATA, sources=SUSPECT_SOURCES_MIXED)

        # Solo 1 de 3 es sospechosa (legacy_hardcode). benchmark es legitimo.
        assert result.has_suspect_sources is True
        assert len(result.source_warnings) == 1
        assert "occupancy_rate" not in result.suspect_fields
        assert "direct_channel_percentage" not in result.suspect_fields
        assert "adr_cop" in result.suspect_fields

        # source_reliability es unverified porque hay al menos 1 sospechosa
        assert result.source_reliability == "unverified"


# ============================================================
# Test 4: backward compat - no sources param = no warnings
# ============================================================

class TestBackwardCompatibility:
    def test_no_sources_param_no_warning(self):
        """Sin param sources no debe haber source_warnings."""
        validator = NoDefaultsValidator()
        result = validator.validate(VALID_DATA)

        assert result.can_calculate is True
        assert result.has_suspect_sources is False
        assert result.source_reliability == "verified"
        assert len(result.source_warnings) == 0
        # general warnings tambien vacio
        assert len(result.warnings) == 0

    def test_none_sources_param_no_warning(self):
        """sources=None explícito tampoco genera warnings."""
        validator = NoDefaultsValidator()
        result = validator.validate(VALID_DATA, sources=None)

        assert result.has_suspect_sources is False
        assert result.source_reliability == "verified"


# ============================================================
# Test 5: financial_title_label - verified
# ============================================================

class TestFinancialTitleLabel:
    def test_financial_title_label_verified(self):
        """source_reliability=verified debe dar label verificable."""
        gen = V4DiagnosticGenerator()
        label = gen._build_financial_title_label("verified")
        assert "verificable" in label.lower()

    def test_financial_title_label_unverified(self):
        """source_reliability=unverified debe dar label estimada."""
        gen = V4DiagnosticGenerator()
        label = gen._build_financial_title_label("unverified")
        assert "estimada" in label.lower()
        assert "verificable" not in label.lower()

    def test_financial_title_label_unknown_defaults_to_estimated(self):
        """Valor desconocido debe defaultear a estimada."""
        gen = V4DiagnosticGenerator()
        label = gen._build_financial_title_label("something_else")
        assert "estimada" in label.lower()
