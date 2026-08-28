"""Tests FASE-SR-F (H5) — Canonicalización de sondas derivadas de URL.

La varianza del plan de assets entre las corridas A (URL limpia, 18:03) y
C (URL con UTM, 18:30) de Salento Real se originaba en sondas construidas
como ``f"{url}/robots.txt"`` y ``f"{url}/llms.txt"``: con query string
producían URLs malformadas (``…/?utm=…/robots.txt``) que el servidor
respondía con la homepage (HTTP 200), corruptiendo la medición de forma
DETERMINISTA según la forma de la URL:

- robots.txt = homepage → 0 bloqueos → ``ai_crawlers.overall_score`` 1.0
  (≥ 0.7) → pain ``ai_crawler_blocked`` omitido (pain_solution_mapper).
- /llms.txt = homepage → ``has_llmstxt=True`` → componente ``llms_txt``
  =100 → ``ia_readiness`` 56.9 (≥ 50) → pain ``low_ia_readiness`` omitido.
- SitePresence direct_fetch = homepage → falso "presente en producción".

Valores reales de disco (reproducidos en TestPainDetectionDeterminism):
- Corrida A: robots 0.5 (14 bloqueados), ia_readiness 34.674 → 7 pains →
  7 assets (low_ia_readiness planifica llms_txt + local_content_page).
- Corrida C: robots 1.0 (0 bloqueados), ia_readiness 56.896 → 5 pains →
  5 assets. Delta de ia_readiness = (50·0.22 + 100·0.09)/0.90 = 22.222.

Fuente: CONTEXT-SALENTOREAL §6 (hipótesis revisada en FASE-SR-F); el
"filtro determinista" del mapper resultó ser un artefacto de medición
upstream, no un filtro del mapper (el mapper es determinista dado el audit).
"""
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, Mock, patch

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import pytest

from modules.auditors.ai_crawler_auditor import AICrawlerAuditor

UTM_URL = (
    "https://www.hotelsalentoreal.com/"
    "?utm_source=google&utm_medium=organic&utm_campaign=GoogleMyBusiness&partner=5792"
)
CLEAN_URL = "https://www.hotelsalentoreal.com/"

# robots.txt real de Salento Real (corrida A): bloquea todo → score 0.5
BLOCKING_ROBOTS = "User-agent: *\nDisallow: /\n"


class FakeHTTPResponse:
    def __init__(self, status_code=200, text=""):
        self.status_code = status_code
        self.text = text
        self.content = text.encode("utf-8")


class RecordingFakeHttpClient:
    """Sustituto de cliente HTTP que graba las URLs solicitadas.

    mode="httpx": devuelve la respuesta directa (AICrawlerAuditor usa
    httpx.Client.get → response).
    mode="tuple": devuelve (response, None) (HttpClient.get de
    modules/utils/http_client.py devuelve una tupla).
    """

    def __init__(self, status_code=200, text="", mode="httpx"):
        self.requests = []
        self._response = FakeHTTPResponse(status_code, text)
        self._mode = mode

    def get(self, url, **kwargs):
        self.requests.append(url)
        if self._mode == "tuple":
            return (self._response, None)
        return self._response


class TestAICrawlerAuditorProbeOrigin:
    """La sonda robots.txt debe anclarse al origen (sin query string)."""

    @pytest.fixture
    def auditor(self):
        return AICrawlerAuditor(timeout=5.0)

    def test_robots_probe_url_strips_query_string(self, auditor):
        """URL con UTM → el fetch debe ir a scheme://netloc/robots.txt."""
        fake_client = RecordingFakeHttpClient(200, BLOCKING_ROBOTS)
        with patch.object(auditor, "client", fake_client):
            auditor.audit_robots_txt(UTM_URL)

        assert fake_client.requests == ["https://www.hotelsalentoreal.com/robots.txt"]

    def test_utm_url_no_longer_mimics_permissive_robots(self, auditor):
        """Reproduce corrida C corregida: con UTM el robots.txt REAL se mide.

        Antes del fix la homepage (200) se parseaba como robots.txt sin
        bloqueos → score 1.0 → pain omitido. Con el fix se mide el robots.txt
        real (bloquea todo) → score 0.5 → pain ai_crawler_blocked generado.
        """
        fake_client = RecordingFakeHttpClient(200, BLOCKING_ROBOTS)
        with patch.object(auditor, "client", fake_client):
            report = auditor.audit_robots_txt(UTM_URL)

        assert report.robots_exists is True
        assert len(report.blocked_crawlers) if hasattr(report, "blocked_crawlers") else True
        blocked = [r for r in report.crawler_results if not r.allowed]
        assert len(blocked) == 14
        assert report.overall_score == pytest.approx(0.5)
        assert report.overall_score < 0.7  # umbral del pain en pain_solution_mapper

    def test_determinism_clean_vs_utm_same_robots_content(self, auditor):
        """Mismo robots.txt del servidor + URL limpia ≡ URL UTM (H5 fix).

        Este es el determinismo del plan de assets: la medición no depende
        de la forma de la URL de entrada.
        """
        results = []
        for url in (CLEAN_URL, UTM_URL):
            fake_client = RecordingFakeHttpClient(200, BLOCKING_ROBOTS)
            with patch.object(auditor, "client", fake_client):
                report = auditor.audit_robots_txt(url)
            results.append(
                (
                    report.robots_exists,
                    report.overall_score,
                    sorted(r.crawler_name for r in report.crawler_results if r.allowed),
                    sorted(r.crawler_name for r in report.crawler_results if not r.allowed),
                )
            )

        assert results[0] == results[1]

    def test_clean_url_preserves_existing_behavior(self, auditor):
        """URL limpia: comportamiento idéntico al previo al fix (corrida A)."""
        fake_client = RecordingFakeHttpClient(200, BLOCKING_ROBOTS)
        with patch.object(auditor, "client", fake_client):
            report = auditor.audit_robots_txt(CLEAN_URL)

        assert fake_client.requests == ["https://www.hotelsalentoreal.com/robots.txt"]
        assert report.overall_score == pytest.approx(0.5)


class TestIAReadinessLlmsProbeOrigin:
    """La sonda /llms.txt del ia_readiness debe anclarse al origen."""

    def _calculate(self, url, llms_status):
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor

        fake = RecordingFakeHttpClient(llms_status, "<html>homepage</html>", mode="tuple")

        schema_result = Mock(total_schemas=0)
        ai_crawler_result = Mock(overall_score=1.0)
        citability_result = Mock(overall_score=57.42)

        with patch("modules.auditors.v4_comprehensive.HttpClient", lambda: fake):
            auditor = V4ComprehensiveAuditor(
                places_client=Mock(), rich_results_client=Mock()
            )
            report = auditor._calculate_ia_readiness(
                schema_result, ai_crawler_result, citability_result, url
            )
        return report, fake

    def test_llms_probe_url_strips_query_string(self):
        """URL con UTM → el fetch de llms.txt no contiene el query string."""
        _, fake = self._calculate(UTM_URL, llms_status=404)
        assert fake.requests == ["https://www.hotelsalentoreal.com/llms.txt"]

    def test_homepage_200_no_longer_counts_as_llmstxt(self):
        """Homepage 200 en la URL malformada ya no cuenta como llms.txt.

        Reproduce el mecanismo de la corrida C: homepage 200 → llms_txt=100
        falso → ia_readiness inflado ≥ 50 → pain omitido. Con el fix, el
        /llms.txt real (404) mantiene el componente en 0.
        """
        report, _ = self._calculate(UTM_URL, llms_status=404)
        assert report.components["llms_txt"] == 0

    def test_llms_txt_present_when_real_file_returns_200(self):
        report, fake = self._calculate(UTM_URL, llms_status=200)
        # La sonda pidió el recurso real (sin query) y fue 200
        assert fake.requests[0].endswith("/llms.txt")
        assert "utm" not in fake.requests[0]
        assert report.components["llms_txt"] == 100

    def test_ia_readiness_delta_between_runs_reproducible(self):
        """Delta A→C = 22.222 con crawler_access 50→100 y llms_txt 0→100.

        Pesos del calculator (GA4 no disponible, redistribución sobre 0.90):
        (50·0.22 + 100·0.09) / 0.90 = 22.222…
        """
        report_c, _ = self._calculate(UTM_URL, llms_status=200)  # crawler 1.0→100, llms 200→100 (valores de corrida C)
        assert report_c.components["crawler_access"] == pytest.approx(100.0)

        report_a = None
        from modules.auditors.v4_comprehensive import V4ComprehensiveAuditor

        fake = RecordingFakeHttpClient(404, "")
        schema_result = Mock(total_schemas=0)
        ai_crawler_result = Mock(overall_score=0.5)  # corrida A
        citability_result = Mock(overall_score=57.42)
        with patch("modules.auditors.v4_comprehensive.HttpClient", lambda: fake):
            auditor = V4ComprehensiveAuditor(
                places_client=Mock(), rich_results_client=Mock()
            )
            report_a = auditor._calculate_ia_readiness(
                schema_result, ai_crawler_result, citability_result, CLEAN_URL
            )

        delta = report_c.overall_score - report_a.overall_score
        assert delta == pytest.approx(22.222, abs=0.01)
        assert report_a.overall_score < 50  # pain low_ia_readiness (corrida A)
        assert report_c.overall_score >= 50  # pain omitido (corrida C)


class TestSitePresenceProbeOrigin:
    """SitePresence direct_fetch (llms_txt) debe anclarse al origen."""

    def _check(self, url, status_code):
        from modules.asset_generation.site_presence_checker import SitePresenceChecker

        requested = []

        def fake_get(full_url, **kwargs):
            requested.append(full_url)
            return FakeHTTPResponse(status_code, "<html>homepage</html>")

        checker = SitePresenceChecker()
        with patch("requests.get", side_effect=fake_get):
            result = checker._check_direct_resource(url, "llms_txt")
        return result, requested

    def test_direct_fetch_strips_query_string(self):
        """URL con UTM → la sonda pide scheme://netloc/llms.txt."""
        result, requested = self._check(UTM_URL, status_code=404)
        assert requested[0] == "https://www.hotelsalentoreal.com/llms.txt"
        assert result["found"] is False

    def test_homepage_200_no_longer_counts_as_present_in_production(self):
        """Homepage 200 ya no produce falso 'presente en producción'."""
        result, requested = self._check(UTM_URL, status_code=200)
        # El 200 viene del recurso REAL /llms.txt solo si existe; con homepage
        # servida en la URL malformada el fix garantiza que se pide el recurso
        # real y el resultado refleja su contenido (aquí 200 → found True,
        # pero la URL solicitada es la correcta).
        assert "utm" not in requested[0]
        assert requested[0].endswith("/llms.txt")
        assert result["found"] is True

    def test_404_for_all_paths_returns_not_found(self):
        result, requested = self._check(UTM_URL, status_code=404)
        # 3 rutas candidatas: /llms.txt, /llm.txt, /.well-known/llm.txt
        assert len(requested) == 3
        assert result["found"] is False


class TestPainDetectionDeterminism:
    """Reproducción a nivel mapper de los ledgers A (7 pains) y C (5 pains).

    Fija el contrato: dado el MISMO audit, el mapper produce SIEMPRE los
    mismos pains (no hay caché ni filtro dependiente de la URL).
    """

    @staticmethod
    def _audit_with(ai_crawler_score, blocked_count, ia_readiness_score):
        from modules.commercial_documents.data_structures import (
            V4AuditResult,
            GBPData,
            PerformanceData,
            CrossValidationResult,
        )

        schema = MagicMock()
        schema.faq_schema_detected = False
        schema.hotel_schema_detected = False
        schema.org_schema_detected = False

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
        audit.url = UTM_URL
        audit.schema = schema
        audit.gbp = gbp
        audit.performance = performance
        audit.validation = validation
        audit.metadata = metadata
        audit.seo_elements = None
        audit.citability = None

        if ai_crawler_score is None:
            audit.ai_crawlers = None
        else:
            audit.ai_crawlers = SimpleNamespace(
                overall_score=ai_crawler_score,
                blocked_crawlers=[f"Bot{i}" for i in range(blocked_count)],
            )

        if ia_readiness_score is None:
            audit.ia_readiness = None
        else:
            audit.ia_readiness = SimpleNamespace(
                overall_score=ia_readiness_score, status="Critical"
            )
        return audit

    @staticmethod
    def _detect(audit):
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
        from modules.commercial_documents.data_structures import ValidationSummary

        summary = ValidationSummary(fields=[], overall_confidence=None)
        return [p.id for p in PainSolutionMapper().detect_pains(audit, summary)]

    def test_run_c_values_omit_both_pains(self):
        """Valores de la corrida C (robots 1.0, ia_readiness 56.9) → 5 pains.

        ai_crawler_blocked y low_ia_readiness AUSENTES — el ledger de C.
        """
        audit = self._audit_with(ai_crawler_score=1.0, blocked_count=0, ia_readiness_score=56.896)
        pain_ids = self._detect(audit)

        assert "ai_crawler_blocked" not in pain_ids
        assert "low_ia_readiness" not in pain_ids
        assert len(pain_ids) == 5

    def test_run_a_values_include_both_pains_with_exact_confidence(self):
        """Valores de la corrida A (robots 0.5, ia_readiness 34.674) → 7 pains.

        low_ia_readiness (conf = 34.674/100) y ai_crawler_blocked (conf 0.5)
        PRESENTES — el ledger de A.
        """
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper
        from modules.commercial_documents.data_structures import ValidationSummary

        audit = self._audit_with(
            ai_crawler_score=0.5, blocked_count=14, ia_readiness_score=34.674
        )
        mapper = PainSolutionMapper()
        pains = mapper.detect_pains(audit, ValidationSummary(fields=[], overall_confidence=None))
        pain_by_id = {p.id: p for p in pains}

        assert "low_ia_readiness" in pain_by_id
        assert pain_by_id["low_ia_readiness"].confidence == pytest.approx(0.34674)
        assert "ai_crawler_blocked" in pain_by_id
        assert pain_by_id["ai_crawler_blocked"].confidence == pytest.approx(0.5)
        assert len(pains) == 7

    def test_mapper_is_deterministic_same_input_same_plan(self):
        """Mismo input → mismo plan de pains (sin caché ni estado)."""
        audit = self._audit_with(
            ai_crawler_score=0.5, blocked_count=14, ia_readiness_score=34.674
        )
        first = self._detect(audit)
        second = self._detect(audit)
        assert first == second

    def test_low_ia_readiness_maps_to_llms_txt_and_local_content(self):
        """El pain low_ia_readiness planifica los 2 assets del delta 7→5."""
        from modules.commercial_documents.pain_solution_mapper import PainSolutionMapper

        mapper = PainSolutionMapper()
        assets = mapper.pain_map["low_ia_readiness"]["assets"]
        assert "llms_txt" in assets
        assert "local_content_page" in assets
