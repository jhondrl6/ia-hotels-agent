"""FASE-SR-E (H7): detección de JSON-LD en formato ARRAY + propagación de error.

Reproduce la cadena de fallo de la corrida C de Hotel Salento Real:
1. El sitio tiene 3 bloques ``application/ld+json``: (a) @graph Yoast/WebPage,
   (b) ARRAY JSON ``[{@type: Hotel}]`` y (c) dict single ``{@type: Hotel}``.
2. ``_validate_schema`` no soporta listas → ``AttributeError: 'list' object
   has no attribute 'get'`` → ``test_url`` lo traga como status ERROR →
   ``get_hotel_schema_report`` retorna ``has_hotel_schema=False`` → el audit
   reporta "0 schemas" en silencio → pain falso ``no_hotel_schema``.

Contrato post-fix (L-SR5: nunca silenciar errores de parsing):
- Cada elemento de un bloque ARRAY se valida como schema individual.
- Un bloque corrupto NO invalida los demás (parse_errors visibles).
- "Ausencia verificada" (status COMPLETE, 0 schemas) se distingue de
  "detección fallida" (status ERROR con error_message propagado al audit).
"""

import json
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from modules.data_validation.external_apis.rich_results_client import (
    RichResultsTestClient,
    RichResultsTestResult,
)
from modules.auditors.v4_comprehensive import (
    SchemaAuditResult,
    V4ComprehensiveAuditor,
)


# ── Fixture: los 3 bloques reales de hotelsalentoreal.com ────────────────
# Verificación en vivo 2026-08-28 (plan maestro §1, H7).

SALENTO_BLOCK_GRAPH = json.dumps(
    {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "WebPage",
                "name": "Hotel Salento Real",
                "url": "https://www.hotelsalentoreal.com/",
            }
        ],
    }
)

SALENTO_BLOCK_ARRAY = json.dumps(
    [
        {
            "@context": "https://schema.org",
            "@type": "Hotel",
            "name": "Hotel Salento Real",
            "address": {
                "@type": "PostalAddress",
                "streetAddress": "Calle 10 # 3-25",
            },
            "telephone": "+57 316 6296142",
            "image": "https://www.hotelsalentoreal.com/img/hotel.jpg",
            "url": "https://www.hotelsalentoreal.com/",
            "priceRange": "$$",
        }
    ]
)

SALENTO_BLOCK_DICT = json.dumps(
    {
        "@context": "https://schema.org",
        "@type": "Hotel",
        "name": "Hotel Salento Real",
        "address": "Calle 10 # 3-25, Salento",
        "telephone": "+57 316 6296142",
    }
)

SALENTO_HTML = (
    "<html><head>"
    f'<script type="application/ld+json">{SALENTO_BLOCK_GRAPH}</script>'
    f'<script type="application/ld+json">{SALENTO_BLOCK_ARRAY}</script>'
    f'<script type="application/ld+json">{SALENTO_BLOCK_DICT}</script>'
    "</head><body></body></html>"
)


def _mock_response(html: str) -> MagicMock:
    response = MagicMock()
    response.text = html
    response.raise_for_status.return_value = None
    return response


class TestArrayJsonLdSupport:
    """T1/T2: el parser soporta JSON-LD en formato ARRAY."""

    def test_validate_schema_accepts_array_block(self):
        """Un bloque JSON-LD ARRAY con @type Hotel se valida por elemento."""
        client = RichResultsTestClient(api_key="test")

        data = json.loads(SALENTO_BLOCK_ARRAY)
        results = client._validate_schema(data)

        assert len(results) >= 1
        hotel_results = [r for r in results if r.schema_type == "Hotel"]
        assert len(hotel_results) == 1
        assert hotel_results[0].detected is True
        assert hotel_results[0].properties.get("name") == "Hotel Salento Real"

    def test_validate_schema_array_with_mixed_elements(self):
        """Un ARRAY con elementos de distinto tipo valida cada uno."""
        client = RichResultsTestClient(api_key="test")

        data = [
            {"@type": "Hotel", "name": "Hotel X", "address": "Calle 1"},
            {"@type": "Organization", "name": "Org X"},
        ]
        results = client._validate_schema(data)

        types = {r.schema_type for r in results}
        assert types == {"Hotel", "Organization"}

    def test_salento_fixture_detects_two_hotel_schemas(self):
        """El HTML real de Salento produce ≥ 2 schemas Hotel y status COMPLETE."""
        client = RichResultsTestClient(api_key="test")

        with patch(
            "modules.data_validation.external_apis.rich_results_client.requests.get"
        ) as mock_get:
            mock_get.return_value = _mock_response(SALENTO_HTML)
            result = client.test_url("https://www.hotelsalentoreal.com/")

        assert result.status == "COMPLETE"
        hotel_types = [s.schema_type for s in result.schemas if s.schema_type == "Hotel"]
        assert len(hotel_types) >= 2
        assert result.detected_items >= 3  # WebPage + 2 Hotels

    def test_salento_report_has_hotel_schema_verified(self):
        """get_hotel_schema_report detecta el Hotel del fixture real."""
        client = RichResultsTestClient(api_key="test")

        with patch(
            "modules.data_validation.external_apis.rich_results_client.requests.get"
        ) as mock_get:
            mock_get.return_value = _mock_response(SALENTO_HTML)
            report = client.get_hotel_schema_report("https://www.hotelsalentoreal.com/")

        assert report["has_hotel_schema"] is True
        hotels_in_report = [
            t for t in report["all_schemas"] if t == "Hotel"
        ]
        assert len(hotels_in_report) >= 2
        assert report["confidence"] in ("verified", "VERIFIED")


class TestErrorPropagation:
    """T1/T2: la detección fallida se distingue de la ausencia verificada."""

    def test_report_exposes_error_when_detection_fails(self):
        """status ERROR → el reporte expone error_message (nunca 0 silencioso)."""
        client = RichResultsTestClient(api_key="test")

        with patch.object(
            RichResultsTestClient, "_analyze_page_directly"
        ) as mock_analyze:
            mock_analyze.return_value = RichResultsTestResult(
                url="https://example.com",
                status="ERROR",
                error_message="list' object has no attribute 'get'",
            )
            report = client.get_hotel_schema_report("https://example.com")

        assert report["status"] == "ERROR"
        assert report["error_message"] == "list' object has no attribute 'get'"
        assert report["has_hotel_schema"] is False

    def test_report_verified_absence_has_no_error(self):
        """Ausencia genuina: status COMPLETE con 0 schemas y sin error."""
        client = RichResultsTestClient(api_key="test")

        with patch.object(
            RichResultsTestClient, "_analyze_page_directly"
        ) as mock_analyze:
            mock_analyze.return_value = RichResultsTestResult(
                url="https://example.com", status="COMPLETE", schemas=[]
            )
            report = client.get_hotel_schema_report("https://example.com")

        assert report["status"] == "COMPLETE"
        assert report["error_message"] is None
        assert report["has_hotel_schema"] is False

    def test_corrupt_block_does_not_invalidate_valid_blocks(self):
        """Un bloque JSON corrupto NO invalida los demás; parse_errors visibles."""
        corrupt_html = (
            "<html><head>"
            '<script type="application/ld+json">{@type: "Hotel", roto}</script>'
            f'<script type="application/ld+json">{SALENTO_BLOCK_DICT}</script>'
            "</head><body></body></html>"
        )
        client = RichResultsTestClient(api_key="test")

        with patch(
            "modules.data_validation.external_apis.rich_results_client.requests.get"
        ) as mock_get:
            mock_get.return_value = _mock_response(corrupt_html)
            result = client._analyze_page_directly("https://example.com")

        assert result.status == "COMPLETE"
        assert any(s.schema_type == "Hotel" for s in result.schemas)
        parse_errors = (result.raw_response or {}).get("parse_errors", [])
        assert len(parse_errors) == 1

    def test_all_blocks_corrupt_propagates_error(self):
        """Si TODOS los bloques fallan el resultado es ERROR (no 0 silencioso)."""
        corrupt_html = (
            "<html><head>"
            '<script type="application/ld+json">{bloque-roto-1}</script>'
            '<script type="application/ld+json">{bloque-roto-2}</script>'
            "</head><body></body></html>"
        )
        client = RichResultsTestClient(api_key="test")

        with patch(
            "modules.data_validation.external_apis.rich_results_client.requests.get"
        ) as mock_get:
            mock_get.return_value = _mock_response(corrupt_html)
            result = client.test_url("https://example.com")

        assert result.status == "ERROR"
        assert result.error_message
        assert "2" in result.error_message  # menciona los 2 bloques fallidos


class TestAuditPropagation:
    """T1/T2: el audit expone el error del detector (falso negativo visible)."""

    @staticmethod
    def _auditor_with_error_report() -> V4ComprehensiveAuditor:
        mock_client = MagicMock()
        mock_client.get_hotel_schema_report.return_value = {
            "url": "https://example.com",
            "has_hotel_schema": False,
            "has_lodgingbusiness_schema": False,
            "has_localbusiness_schema": False,
            "schema_valid": False,
            "errors": [],
            "warnings": [],
            "properties": {},
            "confidence": "unknown",
            "all_schemas": [],
            "status": "ERROR",
            "error_message": "list' object has no attribute 'get'",
            "parse_errors": [],
            "timestamp": "2026-08-28T00:00:00",
        }
        mock_client.get_faq_schema_report.return_value = {
            "url": "https://example.com",
            "has_faq_schema": False,
            "schema_valid": False,
            "errors": [],
            "warnings": [],
            "confidence": "unknown",
            "status": "COMPLETE",
            "error_message": None,
            "timestamp": "2026-08-28T00:00:00",
        }
        return V4ComprehensiveAuditor(rich_results_client=mock_client)

    def test_schema_audit_result_has_error_message_field(self):
        """SchemaAuditResult expone error_message (None por defecto)."""
        result = SchemaAuditResult(
            hotel_schema_detected=False,
            hotel_schema_valid=False,
            hotel_confidence="unknown",
            faq_schema_detected=False,
            faq_schema_valid=False,
            faq_confidence="unknown",
            org_schema_detected=False,
            total_schemas=0,
        )
        assert result.error_message is None

    def test_audit_propagates_detection_error(self):
        """ERROR del detector → error_message visible + warning en el audit."""
        auditor = self._auditor_with_error_report()

        result = auditor._audit_schemas("https://example.com")

        assert result.total_schemas == 0
        assert result.error_message == "list' object has no attribute 'get'"
        assert any(
            "list' object has no attribute 'get'" in str(w)
            for w in result.warnings
        ), "el error de parsing debe ser visible en warnings (L-SR5)"

    def test_audit_clean_report_has_no_error(self):
        """Reporte sin error → error_message None y sin warning de parsing."""
        auditor = self._auditor_with_error_report()
        auditor.rich_results.get_hotel_schema_report.return_value["status"] = "COMPLETE"
        auditor.rich_results.get_hotel_schema_report.return_value["error_message"] = None
        auditor.rich_results.get_hotel_schema_report.return_value["has_hotel_schema"] = True
        auditor.rich_results.get_hotel_schema_report.return_value["all_schemas"] = ["Hotel"]

        result = auditor._audit_schemas("https://example.com")

        assert result.error_message is None
        assert result.hotel_schema_detected is True
        assert result.total_schemas == 1
