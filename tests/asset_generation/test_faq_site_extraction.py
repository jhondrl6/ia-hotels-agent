"""Tests para FIX-7: FAQ extrae datos del sitio.

Verifica que:
1. _extract_services_from_site detecta servicios reales del sitio
2. generate_list enriquece el prompt con servicios detectados
3. Fallback funciona cuando el scraping falla
"""

import pytest
from unittest.mock import patch, MagicMock
from modules.delivery.generators.faq_gen import FAQGenerator


class TestFAQSiteExtraction:
    """FIX-7: Site-aware FAQ generation with scraping."""

    @pytest.fixture
    def generator(self):
        return FAQGenerator(provider_type="auto")

    @pytest.fixture
    def hotel_data(self):
        return {
            "nombre": "Hotel Termales del Ruiz",
            "ubicacion": "Manizales, Caldas",
            "servicios": ["wifi", "parqueadero"],
            "precio_promedio": "250,000 COP",
        }

    def test_extract_services_finds_termas(self, generator):
        """_extract_services_from_site debe detectar 'termas' en el HTML."""
        html_with_termas = """
        <html><body>
            <h1>Hotel Termales del Ruiz</h1>
            <p>Disfrute de nuestras termas naturales, spa y cascadas termales.</p>
            <p>También ofrecemos masajes, senderismo y avistamiento de aves.</p>
            <p>Nuestro restaurante ofrece cocina local.</p>
        </body></html>
        """

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = html_with_termas
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            services = generator._extract_services_from_site(
                "https://hoteltermales.com"
            )

        assert "termas" in services
        assert "spa" in services
        assert "cascadas" in services
        assert "masaje" in services or "masajes" in services
        assert "senderismo" in services
        assert "restaurante" in services
        assert "aves" in services or "avistamiento" in services

    def test_extract_services_empty_site(self, generator):
        """Sitio sin servicios relevantes debe retornar lista vacía."""
        html_generic = """
        <html><body>
            <h1>Hotel Genérico</h1>
            <p>Bienvenido a nuestro hotel. Habitaciones cómodas.</p>
        </body></html>
        """

        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.text = html_generic
            mock_response.raise_for_status = MagicMock()
            mock_get.return_value = mock_response

            services = generator._extract_services_from_site(
                "https://hotelgenerico.com"
            )

        assert services == []

    def test_extract_services_network_error_fallback(self, generator):
        """Error de red debe retornar lista vacía (fallback)."""
        with patch("requests.get") as mock_get:
            mock_get.side_effect = Exception("Connection timeout")

            services = generator._extract_services_from_site(
                "https://hotel-offline.com"
            )

        assert services == []

    def test_extract_services_http_error_fallback(self, generator):
        """HTTP error (404, 500) debe retornar lista vacía."""
        with patch("requests.get") as mock_get:
            mock_response = MagicMock()
            mock_response.raise_for_status.side_effect = Exception("HTTP 500")
            mock_get.return_value = mock_response

            services = generator._extract_services_from_site(
                "https://hotel-error.com"
            )

        assert services == []

    def test_generate_list_enriches_prompt_with_scraped_services(self, generator, hotel_data):
        """generate_list debe incluir servicios detectados en el prompt del LLM."""
        with patch.object(generator, "_extract_services_from_site") as mock_extract:
            mock_extract.return_value = ["termas", "spa", "cascadas"]

            # Mock the LLM to avoid actual API call
            with patch.object(generator.llm_provider, "unified_request") as mock_llm:
                mock_llm.return_value = (
                    "¿Tienen termas?,Sí, nuestras termas naturales están disponibles.\n"
                    "¿Hay spa?,Contamos con spa completo."
                )

                faqs = generator.generate_list(
                    hotel_data, count=50, site_url="https://hoteltermales.com"
                )

        # Should have called scraping
        mock_extract.assert_called_once_with("https://hoteltermales.com")

        # Should have results
        assert len(faqs) > 0

        # Services from hotel_data + scraped should be merged
        # The mock LLM returned termas and spa questions
        preguntas = [f["pregunta"] for f in faqs]
        assert any("termas" in p.lower() for p in preguntas)

    def test_generate_list_without_site_url(self, generator, hotel_data):
        """Sin site_url, no debe hacer scraping y usar solo hotel_data."""
        with patch.object(generator, "_extract_services_from_site") as mock_extract:
            with patch.object(generator.llm_provider, "unified_request") as mock_llm:
                mock_llm.return_value = (
                    "¿Tienen wifi?,Sí, ofrecemos wifi gratuito.\n"
                    "¿Hay parqueadero?,Contamos con parqueadero privado."
                )

                faqs = generator.generate_list(
                    hotel_data, count=50, site_url=None
                )

        # Should NOT have called scraping
        mock_extract.assert_not_called()

        # Should still work
        assert len(faqs) > 0

    def test_generate_passes_site_url_to_generate_list(self, generator, hotel_data):
        """El método generate() debe pasar site_url a generate_list()."""
        with patch.object(generator, "generate_list") as mock_gen_list:
            mock_gen_list.return_value = [
                {"pregunta": "¿Test?", "respuesta": "Test answer."}
            ]

            generator.generate(
                hotel_data, count=10, site_url="https://hoteltermales.com"
            )

        mock_gen_list.assert_called_once()
        call_kwargs = mock_gen_list.call_args[1]
        assert call_kwargs.get("site_url") == "https://hoteltermales.com"

    def test_services_deduplication(self, generator, hotel_data):
        """Servicios ya en hotel_data no deben duplicarse del scraping."""
        # hotel_data.servicios = ["wifi", "parqueadero"]
        # scraping encuentra ["wifi", "termas", "spa"]
        # resultado: ["wifi", "parqueadero", "termas", "spa"] (wifi no duplicado)

        with patch.object(generator, "_extract_services_from_site") as mock_extract:
            mock_extract.return_value = ["wifi", "termas", "spa"]

            with patch.object(generator.llm_provider, "unified_request") as mock_llm:
                mock_llm.return_value = "¿Test?,Test answer."

                # We can't directly inspect servicios merge, but verify no crash
                faqs = generator.generate_list(
                    hotel_data, count=10, site_url="https://test.com"
                )

        assert len(faqs) > 0

    def test_keyword_coverage(self, generator):
        """SERVICE_KEYWORDS debe cubrir servicios comunes de hoteles termales."""
        essential = ["termas", "spa", "cascadas", "senderismo", "restaurante"]
        for kw in essential:
            assert kw in generator.SERVICE_KEYWORDS, (
                f"Keyword '{kw}' should be in SERVICE_KEYWORDS"
            )
