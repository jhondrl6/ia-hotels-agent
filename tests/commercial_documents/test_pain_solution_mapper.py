"""
Tests for PainSolutionMapper - WhatsApp detection fixes (FASE-A) y
guardias de emision low_ota_divergence / low_organic_visibility (FASE-H, V7 y V8).

Tests:
- test_detect_pain_no_whatsapp_unknown: Existing behavior must still pass
- test_detect_pain_whatsapp_conflict: New behavior for CONFLICT confidence
- TestLowOtaDivergenceUnits / TestLowOtaDivergenceOtaEvidence (V7)
- TestLowOrganicVisibilityDedup (V8)
"""

import pytest
from unittest.mock import MagicMock

from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper, Pain
from modules.commercial_documents.data_structures import (
    V4AuditResult, ValidationSummary, ValidatedField, SchemaValidation,
    GBPData, PerformanceData, CrossValidationResult
)
from modules.data_validation.confidence_taxonomy import ConfidenceLevel


def create_mock_audit_result():
    """Create a minimal mock V4AuditResult for testing."""
    schema = MagicMock(spec=SchemaValidation)
    schema.faq_schema_detected = True
    schema.hotel_schema_detected = True
    schema.org_schema_detected = True
    
    gbp = MagicMock(spec=GBPData)
    gbp.geo_score = 80
    gbp.reviews = 50
    gbp.confidence = "verified"
    gbp.rating = 4.5
    
    performance = MagicMock(spec=PerformanceData)
    performance.mobile_score = 75
    performance.has_field_data = True
    performance.lcp = None
    performance.cls = None
    
    validation = MagicMock(spec=CrossValidationResult)
    validation.whatsapp_html_detected = False

    metadata = MagicMock()
    metadata.has_issues = False
    
    audit = MagicMock(spec=V4AuditResult)
    audit.url = "https://hotel-test.com"
    audit.schema = schema
    audit.gbp = gbp
    audit.performance = performance
    audit.validation = validation
    audit.metadata = metadata
    audit.ai_crawlers = None
    audit.ia_readiness = None
    audit.citability = None
    audit.seo_elements = None
    return audit


def create_validation_summary(fields):
    """Create a ValidationSummary with the given fields."""
    return ValidationSummary(fields=fields, overall_confidence=ConfidenceLevel.VERIFIED)


def create_whatsapp_field(confidence_level):
    """Create a ValidatedField for whatsapp_number with specified confidence."""
    return ValidatedField(
        field_name="whatsapp_number",
        value="+1234567890",
        confidence=confidence_level,
        sources=["web_scraping"],
        match_percentage=1.0,
        can_use_in_assets=True
    )


class TestPainSolutionMapperWhatsApp:
    """Test WhatsApp detection in PainSolutionMapper."""

    def test_detect_pain_no_whatsapp_unknown(self):
        """Test that no_whatsapp_visible is detected when confidence is UNKNOWN."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with UNKNOWN confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.UNKNOWN)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect no_whatsapp_visible
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_detect_pain_no_whatsapp_missing(self):
        """Test that no_whatsapp_visible is detected when whatsapp field is missing."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary without whatsapp field
        validation_summary = create_validation_summary([])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect no_whatsapp_visible
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_detect_pain_whatsapp_conflict(self):
        """Test that whatsapp_conflict is detected when confidence is CONFLICT."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with CONFLICT confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.CONFLICT)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should detect BOTH no_whatsapp_visible AND whatsapp_conflict
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" in pain_ids, \
            "CONFLICT should also trigger no_whatsapp_visible"
        assert "whatsapp_conflict" in pain_ids, \
            "CONFLICT should trigger whatsapp_conflict"
        
        # Find the whatsapp_conflict pain and verify its properties
        conflict_pain = next((p for p in pains if p.id == "whatsapp_conflict"), None)
        assert conflict_pain is not None
        assert conflict_pain.name == "Conflicto de WhatsApp"
        assert conflict_pain.severity == "high"
        assert conflict_pain.detected_by == "validation"
        assert conflict_pain.confidence == 0.5

    def test_no_pain_when_whatsapp_verified(self):
        """Test that no WhatsApp pain is detected when confidence is VERIFIED."""
        mapper = PainSolutionMapper()
        audit_result = create_mock_audit_result()
        
        # Create validation summary with VERIFIED confidence
        whatsapp_field = create_whatsapp_field(ConfidenceLevel.VERIFIED)
        validation_summary = create_validation_summary([whatsapp_field])
        
        pains = mapper.detect_pains(audit_result, validation_summary)
        
        # Should NOT detect any WhatsApp-related pain
        pain_ids = [p.id for p in pains]
        assert "no_whatsapp_visible" not in pain_ids
        assert "whatsapp_conflict" not in pain_ids

    def test_pain_solution_map_contains_whatsapp_conflict(self):
        """Test that PAIN_SOLUTION_MAP includes whatsapp_conflict entry."""
        mapper = PainSolutionMapper()
        
        assert "whatsapp_conflict" in mapper.pain_map
        
        conflict_entry = mapper.pain_map["whatsapp_conflict"]
        assert "whatsapp_button" in conflict_entry["assets"]
        assert conflict_entry["confidence_required"] == 0.5
        assert conflict_entry["priority"] == 1
        assert conflict_entry["validation_fields"] == ["whatsapp_number"]
        assert conflict_entry["estimated_impact"] == "high"
        assert conflict_entry["name"] == "Conflicto de WhatsApp"


# =============================================================================
# FASE-H (V7) — low_ota_divergence: guard numerico + normalizacion de unidades
# =============================================================================
#
# El guard original hacia `hasattr(direct_field.value, '__iter__')` sobre el valor del
# ValidatedField. La unidad canonica del pipeline es float en fraccion 0-1
# (main.py:1865 `canal_directo / 100`, default 0.20 en main.py:1890, campo construido en
# main.py:2306) y un float NUNCA tiene `__iter__`: el pain era codigo muerto y el
# `isinstance(..., (int, float, str))` interno era inalcanzable. Ademas `ota_field` se leia
# y no se usaba. Estos tests fijan las tres mitades del defecto.

def create_direct_field(value, confidence=ConfidenceLevel.ESTIMATED, sources=("Default",)):
    """ValidatedField `direct_channel_percentage` tal como lo construye main.py:2306-2314."""
    return ValidatedField(
        field_name="direct_channel_percentage",
        value=value,
        confidence=confidence,
        sources=list(sources),
        can_use_in_assets=False,
    )


def _ota_pain(pains):
    return next((p for p in pains if p.id == "low_ota_divergence"), None)


class TestLowOtaDivergenceUnits:
    """AC1: `0.2`, `20`, `"0.2"` y `"20"` deben significar todos lo mismo (20%)."""

    @pytest.mark.parametrize("value", [0.2, 20, "0.2", "20", 20.0, "20 %", 0.29])
    def test_dispara_en_ambas_unidades_y_formatos(self, value):
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([create_direct_field(value)])

        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None, f"valor {value!r} (20%-equivalente) no disparo low_ota_divergence"
        assert pain.severity == "high"
        assert pain.detected_by == "validation"
        assert pain.id in mapper.pain_map

    @pytest.mark.parametrize("value", [0.2, 20, "0.2", "20"])
    def test_description_normalizado_a_porcentaje(self, value):
        """AC5: tras normalizar, el description expresa 20% en los cuatro casos."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([create_direct_field(value)])

        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None
        assert "20%" in pain.description, f"{value!r} => {pain.description!r}"

    @pytest.mark.parametrize("value", [0.5, 60, 0.3, "0.3", 1, "100", "0.5"])
    def test_no_dispara_por_encima_del_umbral(self, value):
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([create_direct_field(value)])

        assert _ota_pain(mapper.detect_pains(audit, vs)) is None, \
            f"valor {value!r} esta en o sobre el umbral (30%) y no debe disparar"

    @pytest.mark.parametrize("value", ["n/a", "", None, [], {}, "dos", float("nan"),
                                       float("inf"), -20, True, False])
    def test_valor_basura_no_dispara_y_no_lanza(self, value):
        """AC1: un valor no numerico / no convertible no dispara y no lanza."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([create_direct_field(value)])

        assert _ota_pain(mapper.detect_pains(audit, vs)) is None

    def test_sin_campo_direct_channel_no_dispara(self):
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([])

        assert _ota_pain(mapper.detect_pains(audit, vs)) is None

    def test_dispara_con_default_del_pipeline(self):
        """AC4: `direct_channel_percentage=0.2` de fuente 'Default' (lo que el pipeline ya
        conoce, main.py:1890) debe poder disparar el pain priority 1."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([
            create_direct_field(0.2, ConfidenceLevel.ESTIMATED, ("Default",))
        ])

        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None, "el default real del pipeline (0.2/Default) seguia muerto"
        assert pain.confidence == 0.7  # ESTIMATED -> _confidence_to_float


class TestLowOtaDivergenceOtaEvidence:
    """AC2: `ota_presence` es enriquecimiento NO bloqueante, jamas guard.

    main.py nunca registra `ota_presence` en el ValidationSummary (solo adr_cop,
    occupancy_rate, direct_channel_percentage), de modo que usarlo como guard volveria a
    dejar el pain en codigo muerto.
    """

    def test_evidencia_ota_reflejada_en_description(self):
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        ota_field = ValidatedField(
            field_name="ota_presence",
            value=["booking", "expedia"],
            confidence=ConfidenceLevel.VERIFIED,
            sources=["Onboarding"],
        )
        vs = create_validation_summary([create_direct_field(0.2), ota_field])

        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None
        assert "booking" in pain.description
        assert "expedia" in pain.description
        assert "OTAs confirmadas" in pain.description

    def test_sin_ota_presence_el_pain_sigue_disparando(self):
        """Flujo real: `get_field('ota_presence')` devuelve None y el pain NO desaparece."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([create_direct_field(0.2)])

        assert vs.get_field("ota_presence") is None
        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None
        assert "OTAs confirmadas" not in pain.description

    def test_ota_presence_vacio_no_agrega_ruido(self):
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        ota_vacia = ValidatedField(
            field_name="ota_presence", value=[], confidence=ConfidenceLevel.UNKNOWN,
        )
        vs = create_validation_summary([create_direct_field(0.2), ota_vacia])

        pain = _ota_pain(mapper.detect_pains(audit, vs))
        assert pain is not None
        assert "OTAs confirmadas" not in pain.description


# =============================================================================
# FASE-H (V8) — low_organic_visibility no puede emitirse dos veces
# =============================================================================

class TestLowOrganicVisibilityDedup:
    """AC1/AC2: emision unica que conserva las dos narrativas cuando ambas aplican."""

    @staticmethod
    def _analytics_no_ga4(organic=None):
        data = {"analytics_status": None, "use_ga4": False}
        if organic is not None:
            data["organic_traffic"] = organic
        return data

    def test_ambas_ramas_activas_una_sola_emision(self):
        """use_ga4=False Y organic_traffic < 1000: antes se anexaba el pain dos veces."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([])

        pains = mapper.detect_pains(
            audit, vs, self._analytics_no_ga4(organic=500), whatsapp_html_detected=True,
        )
        ids = [p.id for p in pains]

        assert ids.count("low_organic_visibility") == 1, f"emision duplicada: {ids}"
        assert "no_analytics_configured" in ids, "el otro pain de la rama no debe perderse"
        assert ids.count("no_analytics_configured") == 1

    def test_emision_unica_conserva_dato_medido_y_motivo(self):
        """AC2: la emision unica conserva sesiones/umbral ADEMAS del motivo sin analytics."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([])

        pains = mapper.detect_pains(
            audit, vs, self._analytics_no_ga4(organic=500), whatsapp_html_detected=True,
        )
        pain = next(p for p in pains if p.id == "low_organic_visibility")

        assert "Sin analytics configurado" in pain.description
        assert "500" in pain.description
        assert "1000" in pain.description
        # premisa, severidad, nombre y detected_by intactos (prohibido re-escribirlos)
        assert pain.severity == "medium"
        assert pain.detected_by == "analytics"
        assert pain.name in ("Baja Visibilidad de Trafico Organico", "Baja Visibilidad Organica")

    def test_control_ga4_disponible_narrativa_medida(self):
        """GA4 disponible + organic_traffic=500: una emision con la narrativa medida."""
        mapper = PainSolutionMapper()

        pains = mapper.detect_pains_for_analytics(
            {"analytics_status": None, "use_ga4": True, "organic_traffic": 500}
        )
        ids = [p.id for p in pains]

        assert ids.count("low_organic_visibility") == 1
        assert "no_analytics_configured" not in ids
        pain = next(p for p in pains if p.id == "low_organic_visibility")
        assert pain.name == "Baja Visibilidad Organica"
        assert "500" in pain.description
        assert "Sin analytics configurado" not in pain.description
        assert pain.confidence == 0.7

    def test_solo_sin_ga4_narrativa_de_motivo(self):
        mapper = PainSolutionMapper()

        pains = mapper.detect_pains_for_analytics(self._analytics_no_ga4())
        ids = [p.id for p in pains]

        assert ids.count("low_organic_visibility") == 1
        pain = next(p for p in pains if p.id == "low_organic_visibility")
        assert pain.name == "Baja Visibilidad de Trafico Organico"
        assert pain.confidence == 0.8
        assert "500" not in pain.description

    def test_trafico_sobre_umbral_no_dispara(self):
        mapper = PainSolutionMapper()

        pains = mapper.detect_pains_for_analytics(
            {"analytics_status": None, "use_ga4": True, "organic_traffic": 5000}
        )
        assert "low_organic_visibility" not in [p.id for p in pains]

    def test_organic_no_numeric_no_dispara(self):
        """organic_traffic puede llegar como dict (data_derivation_layer): no debe disparar."""
        mapper = PainSolutionMapper()

        pains = mapper.detect_pains_for_analytics(
            {"analytics_status": None, "use_ga4": True,
             "organic_traffic": {"value": {"mobile_score": 75}}}
        )
        assert "low_organic_visibility" not in [p.id for p in pains]

    def test_detect_pains_y_detect_pains_for_analytics_coincidentes(self):
        """AC1: detect_pains delega en _detect_analytics_pains, ninguna via duplica."""
        mapper = PainSolutionMapper()
        audit = create_mock_audit_result()
        vs = create_validation_summary([])
        analytics = self._analytics_no_ga4(organic=500)

        via_detect = [p.id for p in mapper.detect_pains(audit, vs, analytics,
                                                        whatsapp_html_detected=True)]
        via_analytics = [p.id for p in mapper.detect_pains_for_analytics(analytics)]

        assert via_analytics.count("low_organic_visibility") == 1
        assert via_detect.count("low_organic_visibility") == 1
