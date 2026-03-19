from __future__ import annotations

from pathlib import Path

import pytest

from modules.scrapers.seo_accelerator_pro import SEOAcceleratorProEnhanced as SEOAccelerator
from modules.generators.seo_report_builder import SEOAcceleratorReportBuilder
import modules.scrapers.seo_accelerator_pro as seo_module


@pytest.fixture
def mocked_http(monkeypatch):
    html = """
    <html>
      <head>
        <title>Hotel Demo | Experiencias únicas</title>
        <meta name="description" content="Reserva tu estadía en Hotel Demo con termales y spa." />
        <meta name="viewport" content="width=device-width, initial-scale=1" />
      </head>
      <body>
        <h1>Hotel Demo en Bogotá</h1>
        <h2>Habitaciones</h2>
        <img src="room.jpg" alt="Habitación principal" />
        <a href="https://wa.me/3001234567">Reserva por WhatsApp</a>
        <a href="https://facebook.com/hotel-demo">Facebook</a>
      </body>
    </html>
    """.strip()

    class DummyResponse:
        def __init__(self, text: str) -> None:
            self.text = text
            self.status_code = 200
            self.url = "https://example.com/"

        def raise_for_status(self) -> None:  # pragma: no cover - no error path here
            return None

    def fake_get(url, headers=None, timeout=15, allow_redirects=True):  # noqa: D401 - stub
        return DummyResponse(html)

    monkeypatch.setattr(seo_module.requests, "get", fake_get)


@pytest.fixture
def mocked_dependencies(monkeypatch):
    def fake_schema_analyze(self, url):  # noqa: D401 - stub
        return {
            "tiene_hotel_schema": True,
            "schemas_faltantes": [],
            "schemas_encontrados": [
                {"type": "Hotel", "data": {"name": "Hotel Demo"}},
            ],
            "score_schema": 80,
        }

    def fake_unified_request(self, prompt, **kwargs):  # noqa: D401 - stub
        prompt_lower = prompt.lower()
        if "keywords" in prompt_lower:
            return "\n".join(
                [
                    "hotel boutique en bogotá",
                    "hotel con termales en bogotá",
                    "hotel spa para parejas en bogotá",
                    "alojamiento familiar en bogotá",
                    "hotel pet friendly en bogotá",
                ]
            )
        return "\n".join(
            [
                "Blog: Guía para disfrutar Bogotá en 3 días",
                "FAQ: ¿Qué amenities incluye Hotel Demo?",
                "Guía: Actividades cerca de Hotel Demo",
            ]
        )

    monkeypatch.setattr(seo_module.SchemaFinder, "analyze", fake_schema_analyze)
    monkeypatch.setattr(seo_module.ProviderAdapter, "unified_request", fake_unified_request)


def test_seo_accelerator_generates_markdown(tmp_path: Path, mocked_http, mocked_dependencies):
    accelerator = SEOAccelerator(
        url="https://example.com",
        business_name="Hotel Demo",
        location="Bogotá",
        provider_type="deepseek",
    )

    analysis = accelerator.analyze_complete(include_competitor_analysis=False)

    assert analysis["score"]["total"] <= 100
    assert analysis["metadata"]["title"] == "Hotel Demo | Experiencias únicas"
    assert analysis["keywords"], "Debe generar keywords locales"

    markdown = accelerator.generate_markdown_report(analysis)
    assert "DIAGNÓSTICO SEO" in markdown
    assert "KEYWORDS LOCALES" in markdown

    builder = SEOAcceleratorReportBuilder(analysis, "Hotel Demo", "https://example.com")
    output_path = builder.write(tmp_path)
    assert output_path.exists()
    assert output_path.name == "03_SEO_ACCELERATOR.md"
    content = output_path.read_text(encoding="utf-8")
    assert "Hotel Demo" in content
    assert "🔑 KEYWORDS LOCALES RECOMENDADAS" in content
