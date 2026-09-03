"""Tests de las ramas de emisión añadidas en FASE-B (V1: pains muertos en Capa 1).

POR QUÉ EXISTE
`evidence/FASE-B/decision-pains-muertos.md` decidió IMPLEMENTAR 3 pains con señal de dato
verificable (`missing_llmstxt`, `missing_alt_text`, `no_social_links`) y DIFERIR 6. Este
archivo prueba las 3 ramas nuevas.

QUÉ PRUEBA ADEMÁS DEL CASO FELIZ
La mitad de los tests son NEGATIVOS y son la parte importante. Un guard que confunda
«no medido» con «medido en False» produce pains que disparan en falso — es el defecto de
`ai_crawler_blocked` (dossier §3) y la lección «vacío vs ausente». Cada rama nueva tiene por
eso sus casos de no-medición:

  · `ia_readiness is None`                 → la sonda HTTP no corrió
  · `components` sin la clave `llms_txt`   → corrió otro cálculo, no esa sonda
  · `seo_elements.confidence == "low"`     → el detector lanzó excepción y devolvió todos
                                             los flags en False (seo_elements_detector.py:70-74)
  · `images_without_alt == 0`              → página sin imágenes: el detector devuelve
                                             imagenes_alt=True, no hay nada que corregir

Y el retiro de `no_ga4_enhanced` (decisión B1 §3.10) se fija con un test de regresión que
le pone al mapper un objeto que SÍ tiene `is_enhanced`: si alguien reintroduce la rama
muerta, el test falla.
"""

import pytest

from modules.auditors.ia_readiness_calculator import IAReadinessReport
from modules.auditors.seo_elements_detector import SEOElementsResult
from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
from tests.commercial_documents.test_pain_solution_mapper import (
    create_mock_audit_result,
    create_validation_summary,
)


@pytest.fixture
def mapper():
    return PainSolutionMapper()


@pytest.fixture
def audit():
    """Audit base con las dos señales nuevas apagadas (no medidas)."""
    return create_mock_audit_result()


@pytest.fixture
def sin_whatsapp():
    """ValidationSummary vacío: evita que el ruido de WhatsApp tape la rama bajo prueba."""
    return create_validation_summary([])


def _ids(pains):
    return [p.id for p in pains]


def _seo(**kwargs) -> SEOElementsResult:
    """SEOElementsResult real, no un MagicMock: el guard lee atributos concretos."""
    base = dict(confidence="high", open_graph=True, imagenes_alt=True, redes_activas=True)
    base.update(kwargs)
    return SEOElementsResult(**base)


def _ia_ready(**componentes) -> IAReadinessReport:
    return IAReadinessReport(
        overall_score=50.0,
        components=dict(componentes),
        status="partial",
        actionable_items=[],
    )


# =============================================================================
# missing_llmstxt — sonda HTTP real (v4_comprehensive.py:1295, ia_readiness_calculator:53)
# =============================================================================

class TestMissingLlmsTxt:

    def test_se_emite_cuando_la_sonda_devuelve_cero(self, mapper, audit, sin_whatsapp):
        audit.ia_readiness = _ia_ready(llms_txt=0)

        assert "missing_llmstxt" in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_cuando_llms_txt_existe(self, mapper, audit, sin_whatsapp):
        audit.ia_readiness = _ia_ready(llms_txt=100)

        assert "missing_llmstxt" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_si_ia_readiness_no_se_midio(self, mapper, audit, sin_whatsapp):
        """AUSENTE ≠ 0. `ia_readiness is None` es el estado por defecto del audit cuando el
        cálculo no corrió; emitir ahí sería un falso positivo masivo."""
        audit.ia_readiness = None

        assert "missing_llmstxt" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_si_components_no_trae_la_clave(self, mapper, audit, sin_whatsapp):
        """El report puede existir con otros componentes poblados y sin la sonda de llms.txt.
        `.get("llms_txt") == 0` sobre clave ausente devuelve None, no 0."""
        audit.ia_readiness = _ia_ready(schema_quality=80, crawler_access=60)

        assert "missing_llmstxt" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_datos_del_pain_emitido(self, mapper, audit, sin_whatsapp):
        audit.ia_readiness = _ia_ready(llms_txt=0)

        pain = next(p for p in mapper.detect_pains(audit, sin_whatsapp)
                    if p.id == "missing_llmstxt")
        assert pain.detected_by == "ia_readiness_calculator"
        assert pain.confidence == 0.9
        assert pain.id in PainSolutionMapper.PAIN_SOLUTION_MAP


# =============================================================================
# missing_alt_text / no_social_links — seo_elements (medición real de HTML)
# =============================================================================

class TestMissingAltText:

    def test_se_emite_con_recuento_positivo(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(imagenes_alt=False, images_without_alt=7)

        pains = mapper.detect_pains(audit, sin_whatsapp)
        assert "missing_alt_text" in _ids(pains)

    def test_el_detalle_lleva_el_recuento(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(imagenes_alt=False, images_without_alt=7)

        pain = next(p for p in mapper.detect_pains(audit, sin_whatsapp)
                    if p.id == "missing_alt_text")
        assert "7" in pain.description
        assert pain.confidence == 0.9

    def test_no_se_emite_con_bandera_en_falso_pero_recuento_cero(self, mapper, audit, sin_whatsapp):
        """VACÍO ≠ AUSENTE. `imagenes_alt=False` con `images_without_alt=0` es la firma de
        un resultado inconsistente, no de un sitio con imágenes sin alt. Emitir ahí cobraría
        por arreglar cero imágenes."""
        audit.seo_elements = _seo(imagenes_alt=False, images_without_alt=0)

        assert "missing_alt_text" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_cuando_el_detector_fallo(self, mapper, audit, sin_whatsapp):
        """seo_elements_detector.py:70-74 devuelve confidence="low" con TODOS los flags en
        False cuando BeautifulSoup lanza. Ese resultado no dice nada del sitio."""
        audit.seo_elements = _seo(
            confidence="low", imagenes_alt=False, images_without_alt=0, redes_activas=False,
        )

        ids = _ids(mapper.detect_pains(audit, sin_whatsapp))
        assert "missing_alt_text" not in ids
        assert "no_social_links" not in ids

    def test_no_se_emite_si_no_hay_medicion(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = None

        assert "missing_alt_text" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_con_alt_correctos(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(imagenes_alt=True, images_without_alt=0)

        assert "missing_alt_text" not in _ids(mapper.detect_pains(audit, sin_whatsapp))


class TestNoSocialLinks:

    def test_se_emite_cuando_no_hay_enlaces(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(redes_activas=False, social_links_found=[])

        assert "no_social_links" in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_cuando_si_hay_enlaces(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(
            redes_activas=True, social_links_found=["https://instagram.com/hotel"],
        )

        assert "no_social_links" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_no_se_emite_si_no_hay_medicion(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = None

        assert "no_social_links" not in _ids(mapper.detect_pains(audit, sin_whatsapp))

    def test_datos_del_pain_emitido(self, mapper, audit, sin_whatsapp):
        audit.seo_elements = _seo(redes_activas=False)

        pain = next(p for p in mapper.detect_pains(audit, sin_whatsapp)
                    if p.id == "no_social_links")
        assert pain.detected_by == "seo_elements_detection"
        assert pain.confidence == 0.9
        assert pain.id in PainSolutionMapper.PAIN_SOLUTION_MAP


# =============================================================================
# no_ga4_enhanced — RETIRADO (decisión B1 §3.10, premisa N-A1 corregida)
# =============================================================================

class TestNoGa4EnhancedRetirado:
    """N-A1 lo clasificó como «pain VIVO que se emite y se descarta». Medido: su guardia
    `hasattr(status, "is_enhanced")` era insatisfacible porque el campo no existe en
    `AnalyticsStatus` ni se puebla en ningún punto del repo (S-B7). Se retiró de Capa 1."""

    def test_ya_no_esta_en_capa1(self):
        assert "no_ga4_enhanced" not in PainSolutionMapper.PAIN_SOLUTION_MAP

    def test_no_se_emite_ni_con_un_status_que_si_tiene_el_campo(self, mapper, audit, sin_whatsapp):
        """Regresión del retiro: se le entrega al mapper exactamente el objeto que la rama
        muerta necesitaba para disparar. Si alguien la reintroduce, esto falla."""
        class StatusConCampo:
            ga4_available = True
            is_enhanced = False

        pains = mapper.detect_pains(
            audit, sin_whatsapp,
            analytics_data={"analytics_status": StatusConCampo(), "use_ga4": True},
        )
        assert "no_ga4_enhanced" not in _ids(pains)

    def test_analytics_setup_guide_sigue_prometido_por_el_pain_vivo(self):
        """El retiro no huérfaniza el asset: `analytics_setup_guide` sigue prometido por
        `no_analytics_configured`, que sí existe en Capa 1 y sí se emite."""
        from modules.asset_generation.asset_catalog import ASSET_CATALOG

        entry = ASSET_CATALOG["analytics_setup_guide"]
        assert entry.promised_by == ["no_analytics_configured"]
        assert all(p in PainSolutionMapper.PAIN_SOLUTION_MAP for p in entry.promised_by)
